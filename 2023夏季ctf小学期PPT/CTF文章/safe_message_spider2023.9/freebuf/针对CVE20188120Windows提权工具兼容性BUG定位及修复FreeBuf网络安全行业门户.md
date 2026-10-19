## 一、背景介绍：

2018年5月微软发布了针对Windows操作系统内核组件漏洞（CVE-2018-8210）的补丁，该漏洞影响多个版本的操作系统，成功利用漏洞可使得普通应用程序以内核权限执行任意代码。

笔者在6月对该漏洞进行分析并发布了漏洞分析和漏洞利用文章（[地址](http://www.freebuf.com/vuls/174183.html)），文中同时附带了一份提权工具，支持WinXP、Win2003、Win7、Win2008等系统。后有网友回帖表示在Win7
x86系统下该利用工具无效，经调试确认提权工具确实存在部分兼容性问题。本文将针对该问题进行补充说明，解决存在的兼容性问题。

CVE-2018-8120为缓冲区溢出漏洞，可造成内核任意地址写入。
前文中漏洞利用工具通过触发漏洞，对内核服务函数指针表进行修改，替换为一段修改当前进程Token的ShellCode地址。

  

## 二、 问题定位：

经测试在Win7 x86确实无法实现提权，现进行问题定位。设置双机调试内核环境，在关键的位置设置断点，进行调试确认问题的原因。

### 漏洞利用工具调试

首先设置双机调试环境，虚拟机安装Win7 x86，真机安装WinDbg进行内核调试，在win32k! SetImeInfoEx
()设置断点，查看提权工具是否可以成功调用漏洞函数。

![image.png](https://image.3001.net/images/20180808/1533713113_5b6a9ad9208e1.png!small)![image.png](https://image.3001.net/images/20180808/1533713116_5b6a9adcbdf51.png!small)

确认是可以成功调用SetImeInfoEx()的，通过IDA反汇编查看该版本的SetImeInfoEx()函数确认漏洞存在。

![image.png](https://image.3001.net/images/20180808/1533713122_5b6a9ae20c907.png!small)

在SetImeInfoEx()函数进行单步跟踪，确认是否可以触发漏洞

![image.png](https://image.3001.net/images/20180808/1533713129_5b6a9ae9423bc.png!small)

经过单步跟踪，发现可以触发SetImeInfoEx()函数存在的缓冲区溢出漏洞，成功修改了指定的内存数据。

漏洞利用工具通过覆盖GDI内核对象关键字段，实现任意内核地址读写。继续执行漏洞利用工具，检查是否成功修改内核服务函数指针表HalDispatchTable。

![image.png](https://image.3001.net/images/20180808/1533713136_5b6a9af02f061.png!small)

进一步进行查看发现，漏洞利用程序计算的HalDispatchTable内存地址并不正确，导致漏洞利用程序没有成功修改函数指针，提权ShellCode也就没有得以执行。

NtQueryIntervalProfile()和HalDispatchTable

我们说明一下为什么修改HalDispatchTable后，可以执行ShellCode。NtQueryIntervalProfile()是Ntdll.dll中导出的未公开的系统调用.它调用内核可执行程序ntosknl.exe导出的KeQueryIntervalProfile()函数.如果我们反汇编这个函数，可看到如下：

![image.png](https://image.3001.net/images/20180808/1533713203_5b6a9b331b816.png!small)

位于nt!HalDispatchTable+0x4地址上的函数会被KeQueryIntervalProfile()调用（看红色方框）.所以如果我们覆盖那个地址上的指针-也就是说HalDispatchTable中的第二个指针-带有我们ShellCode地址；然后我们调用函数NtQueryIntervalProfile(),将执行我们的ShellCode。

三、解决问题：

前面已经定位到问题，由于没有正确的修改系统服务表的函数指针，导致提权的ShellCode没有执行。现在的问题是找出原先计算过程中为什么会出错，导致没有计算出正确的地址。

### 如何计算HalDispatchTable表地址

HalDispatchTable由NT内核文件导出，获取该表地址只需要通过GetProcAddress()搜索NT内核文件导出表即可，不过该函数在用户态下，无法对内核模块进行搜索。

在我们的漏洞利用工具中，计算HalDispatchTable表主要是函数leakHal()函数完成的，下面看看该函数的流程：

![image.png](https://image.3001.net/images/20180808/1533713219_5b6a9b434db7e.png!small)

该函数首先通过EnumDeviceDrivers()获取到ntoskrnl.exe模块的运行时基址，之后在用户态加载ntoskrnl.exe并搜索HalDispatchTable表的导出地址，程序使用真实导出地址减去模块基地址，获得了该表相对于模块基地址的偏移值。最后使用第一步获取的ntoskrnl.exe的运行时基地址加上上面计算的偏移值，得出内核中HalDispatchTable表的内存地址。

### NT内核文件之ntoskrnl.exe

NT内核文件是Windows的内核关键组件，通常是指可执行文件ntoskrnl.exe。但是微软根据当前CPU的核心数量以及PAE开启状态，加载不同的内核可执行文件。

![image.png](https://image.3001.net/images/20180808/1533713236_5b6a9b547e309.png!small)

如上图所示，系统根据当前处理器的工作模式，加载不同的内核文件。

### 解决方案

由于原先的代码在计算HalDispatchTable表的时候，没有考虑到微软针对CPU设置加载不同版本内核组件的问题，导致在部分系统上无法成功修改函数指针。

在代码中加入检测CPU设置的代码，根据具体的设置，判断内核所加载的NT内核组件，并计算HalDispatchTable的真实内存地址即可。下面是补充的代码：

![image.png](https://image.3001.net/images/20180808/1533713242_5b6a9b5aad286.png!small)![image.png](https://image.3001.net/images/20180808/1533713247_5b6a9b5fe6215.png!small)

在原先的leakHal()代码加入了DeteckKernel()函数，
该函数检测CPU数量和PAE开启状况，返回系统可能加载的内核组件名称。后续程序按原定的流程，加载该内核组件，获取HalDispatchTable表的内存地址并修改。

最后调用NtQueryIntervalProfile()函数，我们的ShellCode将以内核权限执行，以替换Token的方式进行提权。

![image.png](https://image.3001.net/images/20180808/1533713278_5b6a9b7eea287.png!small)

## 四、总结

笔者已重新测试WinXP x86、Win 2003 x86、Win 2003 x64、Win7 x86、Win7 x64，Win2008
x86以及Win2008
x64等系统修改后的代码均可以正常提权。如各位看官遇到其他问题，欢迎跟帖进行反馈，笔者将酌情进行更新解决。更新后的代码在Github有提交，感兴趣的可以去下载并测试。[GitHub](https://github.com/alpha1ab/CVE-2018-8120)地址，谢谢支持！

另外，北京天融信阿尔法实验室常年招人，实验室专注漏洞相关技术研究，二进制和WEB方向岗位均可，诚挚欢迎各位有志从事逆向分析、样本检测、漏洞挖掘、渗透测试以及移动端安全研究相关工作的小伙伴。有兴趣的请投递简历到：[http://blog.topsec.com.cn/人才招聘/](http://blog.topsec.com.cn/%E4%BA%BA%E6%89%8D%E6%8B%9B%E8%81%98/)

