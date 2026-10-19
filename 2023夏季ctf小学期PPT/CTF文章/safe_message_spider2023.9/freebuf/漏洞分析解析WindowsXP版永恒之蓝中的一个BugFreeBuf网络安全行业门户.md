***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

## 背景

 **黑掉Windows 7已经没什么挑战了，我这一次打算重新回顾一下那个针对Windows
XP永恒之蓝漏洞的漏洞利用代码，之前这份Exploit就没成功过，而且我尝试了各种版本的补丁和服务包，但这份漏洞利用代码要么无法工作，要么就让设备蓝屏。因此我打算继续研究一下，因为FuzzBunch有太多没有被挖掘出来的“潜力”了。**

但是在一次针对其他Windows XP设备的渗透测试过程中，我本来对FuzzBunch没抱希望的，但可怕的是，它竟然能用…

所以我问自己，为什么它能用到外界的Windows XP设备上，却没办法在我的实验环境中使用呢？（长话短说：因为单核/多核/PAE
CPU中的NT/HAL存在差别，导致FuzzBunch的XP Payload在单核设备上会终止运行。）

### 多个漏洞利用链

请记住，永恒之蓝有很多个版本。但是FuzzBunch针对Windows
XP的漏洞利用链却和针对其他版本的Exploit有着很大区别，具体请参考DerbyCon
8.0的相关资料：【[幻灯片](https://drive.google.com/file/d/1evqBqqNCTha7LxKNC9P85ql49qLbWZ_i/view)】【[视频](https://www.youtube.com/watch?v=ZHWidYrEgNM)】。

## Payload方法论

原来，漏洞利用代码根本没问题，有问题的是FuzzBunch的Payload。

主要阶段的Shellcode执行的是下列活动：

1.利用[KdVersionBlock](https://web.archive.org/web/20061110120809/http:/www.rootkit.com/newsread.php?newsid=153)技术获取&nt和&hal；

2.解析某些必要的函数指针，比如说hal!HalInitializeProcessor；

3.恢复Boot处理器KPCR/KPRCB，因为它会在漏洞利用过程中崩溃；

4.运行[DoublePulsar](https://zerosum0x0.blogspot.com/2017/04/doublepulsar-initial-smb-backdoor-ring.html)，在SMB服务中植入后门；

5.将nt!PopProcessorIdle的运行状态恢复到正常状态。

## 单核分支异常

在IdleFunction上设置多个硬件断点，并向Shellcode中设置偏移量+0x170，我们会发现多核设备安装分支的情况跟单核设备的不同。

    
    
    kd>ba w 1 ffdffc50 "ba e 1 poi(ffdffc50)+0x170;g;"

多核设备会要求获取一个指向hal!HalInitializeProcessor的函数指针。

![2.png](https://image.3001.net/images/20181217/1545054205_5c17a7fd624ab.png!small)

这个函数估计是用来清理KPRCB的半崩溃状态的。

单核设备无法找到hal!HalInitializeProcessor，sub_547会返回NULL值。Payload将无法继续运行，然后通过数据清零来进行自毁，并且会设置ROP链来释放某些内存，恢复执行流程。

![3.png](https://image.3001.net/images/20181217/1545054213_5c17a805f38fe.png!small)

## 根本原因分析

sub_547这个Shellcode函数无法在单核CPU主机上找到hal!HalInitializeProcessor的地址，从而导致Payload的执行过程被强制终止。因此我们需要对这个Shellcode函数进行逆向分析，找到导致攻击Payload运行失败的根本原因。

这里的内核Shellcode存在一个问题，即没有考虑到Windows
XP上所有可用的不同类型的NT内核可执行文件。比如说，多核设备的NT程序（例如ntkrnlamp.exe）可以正常工作，但单核设备（例如ntoskrnl.exe）就会出现问题。除此之外，halmacpi.dll和halacpi.dll也存在类似的问题。

### NT疑惑

sub_547要做的第一件事就是获取NT程序所使用的HAL导入函数。Payload首先会读取NT程序中的0x1040偏移量来查找HAL函数。

在多核Windows XP设备中，读取这个偏移地址可以让Shellcode找到正确的hal!HalQueryRealTimeClock函数：

![4.png](https://image.3001.net/images/20181217/1545054230_5c17a816bf7a4.png!small)

但是在单核设备上是没有HAL导入表的，只有一个字符串表：

![5.png](https://image.3001.net/images/20181217/1545054247_5c17a8277f2fb.png!small)

一开始我以为自己找到了问题的根源，但其实不然，因为这里有一个修正码问题。Shellcode会检查偏移量0x1040的值是否位于HAL范围内。如果条件不满足，则会减去0xc40，然后以0x40作为增量值在HAL地址范围内进行搜索，直到搜索地址再次到达0x1040为止。

![6.png](https://image.3001.net/images/20181217/1545054258_5c17a832d80eb.png!small)

最终，单核设备上的Payload会找到一个HAL函数，即hal!HalCalibratePerformanceCounter：

![7.png](https://image.3001.net/images/20181217/1545054267_5c17a83b2d006.png!small)

题外话：方程式组织（国际著名黑客组织）在判断不同XP NT类型上做得非常优秀！

### HAL可变字节表

Shellcode在找到了HAL函数之后，会尝试定位hal!HalInitializeProcessor。Shellcode中内置的表（位于0x5e7偏移量）包含了一个长度为1字节的域，后面可以跟一段字节序列。接下来，Shellcode会以在增量0x20字节遍历搜索新的HAL函数地址。

下面是多核版本HAL中找到的5个字节目标数据：

![8.png](https://image.3001.net/images/20181217/1545054276_5c17a84472e72.png!small)

但是，单核版本的HAL函数差异就很大：

![9.png](https://image.3001.net/images/20181217/1545054286_5c17a84e0d0af.png!small)

这里有一个类似的mov指令，但它并不是movzx指令。因为这个函数中并不包含这个字节序列，因此代码无法找到这个目标函数。

## 总结

大家都知道，在不同版本的Windows系统中，想通过搜索字节序列来识别函数并不是一件容易的事情。从这个漏洞中，我们至少应该学到一点，即各位Exploit开发者在设计漏洞利用代码时必须要考虑周全，注意NTOSKRNL和HAL在单核/多核/PAE架构上存在的差异。

这也是Eternal系列漏洞的一个分析样例，全球的网络组织可能会重复使用相同的漏洞利用代码或Payload，但他们也会使用不同的方法来开发Exploit。如果一种方法无法成功，也可以通过漏洞利用代码的多样化特点最终完成他们的攻击任务。

 ***参考来源：[zerosum0x0](https://zerosum0x0.blogspot.com/2018/11/dissecting-bug-in-eternalblue-client.html)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

