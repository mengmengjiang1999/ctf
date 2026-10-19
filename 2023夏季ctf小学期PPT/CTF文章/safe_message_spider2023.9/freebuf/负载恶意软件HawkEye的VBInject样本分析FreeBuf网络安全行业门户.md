*****本文原创作者：Macc，本文属于FreeBuf原创奖励计划，未经允许禁止转载**  
**

##  **0x01 概述**

 **恶意软件HawkEye的利用大多都是通过钓鱼邮件分发，利用office直接启动HawkEye主体或者一些经过加密的程序，本文中的VB
Inject属于后者，也把重心放在了调试这个VB程序上。**

文件基本信息如下：

项 | 值  
---|---  
PEID  
| VB  
  
MD5  
| 3e3cec381975a0c4a3a2333370ca0799  
  
大小  
| 684KB  
  
修改日期  
| 2018/6/13  
  
  
VirusTotal上的该样本信息：

![图片1.png](https://image.3001.net/images/20181008/1538981323_5bbafdcb49943.png!small)

病毒名大多为VBKrypt或者VBInject。

##  **0x02 行为监控** ****

![图片2.png](https://image.3001.net/images/20181008/1538981427_5bbafe33505b8.png!small)

将自身复制到C:\User\user\AppData\Romaing\WindowsUpdate.exe，创建C:\User\user\AppData\Romaing\pid.txt,C:\User\user\AppData\Romaing\pidloc.txt，并将WindowsUpdate.exe加入自启动项。

用wireshark抓网络行为，发现该样本会访问<http://whatismyipaddress.com/>，并与yandex邮件服务器建立连接。

![图片3.png](https://image.3001.net/images/20181008/1538981469_5bbafe5d56400.png!small)

##  **0x03 反调试** ****

因为是个VB程序，首先就想到用VB decompile反编译。效果如下：

![图片4.png](https://image.3001.net/images/20181008/1538981513_5bbafe8989bff.png!small)

似乎是没不能看出什么，于是来调试一下。

![图片5.png](https://image.3001.net/images/20181008/1538981541_5bbafea534164.png!small)

步过这个call之后，会跳转到一个错误指令：

![图片6.png](https://image.3001.net/images/20181008/1538981567_5bbafebf1e7dc.png!small)

想到可能是因为反调试导致的，所以步入0x4012A1的call，然而里面的代码都是模块msvbvm60的，一个比较快能定位到主程序的办法就是通过VB
decompile中显示的地址。于是我在0x4A07D6、0x4A0BC8下断。Form_Load中没有什么有用的信息，直接断到Form_Paint。

![图片7.png](https://image.3001.net/images/20181008/1538981602_5bbafee2186a7.png!small)

这里做了一些字符串的操作，直接自动步过，然后来到下面这个call：

![图片8.png](https://image.3001.net/images/20181008/1538981641_5bbaff09e3f11.png!small)

回车进去看到有调用DllFunctionCall，这里会调用RtlMoveMemory很多次，复制一段内存：

![图片9.png](https://image.3001.net/images/20181008/1538981676_5bbaff2cf23c3.png!small)

在循环结束的地方F4：

![图片10.png](https://image.3001.net/images/20181008/1538981729_5bbaff613dc42.png!small)

单步之后发现程序会在下图位置运行起来，进入错误指令：

![图片11.png](https://image.3001.net/images/20181008/1538981776_5bbaff90cfa27.png!small)

跟进后，又来到下面的call(因为其他的call都有函数名__vbaxxx)，回车进入后发现这个call也调用了DllFuncitonCall：

![图片12.png](https://image.3001.net/images/20181008/1538981811_5bbaffb339c8c.png!small)![图片13.png](https://image.3001.net/images/20181008/1538981815_5bbaffb751999.png!small)

调用了EnumWindows，这个函数一个参数是回调函数，所以需要留意。

 **函数原型：**

BOOL EnumWindows( WNDENUMPROC lpEnumFunc, LPARAM lParam )；

lpEnumFunc是指向回调函数的指针，lParam是传递给回调函数的参数。

![图片14.png](https://image.3001.net/images/20181008/1538981936_5bbb0030c74f0.png!small)

看此时栈的状态，第一个参数位于0x12F4D8，在该处下断。

然后F8->执行到用户代码，断到该处：：

![图片15.png](https://image.3001.net/images/20181008/1538981971_5bbb00530e6af.png!small)

单步到后面的jmp之后跳到下面的地址：

![图片16.png](https://image.3001.net/images/20181008/1538982007_5bbb007728693.png!small)

这里call edx之后，跳到错误地址，该地址正确编码后的指令是：

![图片17.png](https://image.3001.net/images/20181008/1538982039_5bbb00976e2e2.png!small)

地址为0x48EA92，但程序却跳到了0x48EA93：

![图片18.png](https://image.3001.net/images/20181008/1538982068_5bbb00b4e4f76.png!small)

注意到在call之前的一条adc指令，程序在这里加了1，导致跳转到0x48EA93，反反调试的话做到这里把这条指令nop掉就可以了，不过可以看看[ebx+2]的值是怎么决定的。

![图片19.png](https://image.3001.net/images/20181008/1538982109_5bbb00dd06e81.png!small)

返回去看到这里，就知道为什么了。

fs:[esi](此时esi的值为0x18)指向自身(TEB结构)，偏移为3的地址处是BeingDebugged, 0x01是被调试中：

![图片21.png](https://image.3001.net/images/20181008/1538982316_5bbb01ac0a520.png!small)

![图片22.png](https://image.3001.net/images/20181008/1538982329_5bbb01b9b73bf.png!small)

nop掉保存再调试。

##  **0x04 运行时解密** ****

从过了反调试的地址0x48EA92开始：

![图片23.png](https://image.3001.net/images/20181008/1538982363_5bbb01db0499d.png!small)

干扰指令很多，还有一部分硬编码。一直单步，遇到call都最好跟进，这段代码中的call不多：

![图片24.png](https://image.3001.net/images/20181008/1538982389_5bbb01f53f0fb.png!small)

调用DllFunctionCall得到EnumWindows的地址：

![图片25.png](https://image.3001.net/images/20181008/1538982429_5bbb021d70f99.png!small)

![图片26.png](https://image.3001.net/images/20181008/1538982442_5bbb022aac8fe.png!small)

这里可以直接步过：

![图片27.png](https://image.3001.net/images/20181008/1538982474_5bbb024a3cf68.png!small)

然后出现VirtualAlloc，然后同样DllFunctionCall得到VirtualAlloc地址，然后调用。

![图片28.png](https://image.3001.net/images/20181008/1538982501_5bbb02658f58e.png!small)

分配了内存1，推断是要解密自身代码写入到地址：

![图片29.png](https://image.3001.net/images/20181008/1538982526_5bbb027ef2777.png!small)

开始往这片内存写入内容，然后跳转到这个地址：

![图片30.png](https://image.3001.net/images/20181008/1538982560_5bbb02a0ce0e2.png!small)

单步到下图，又有一个反调试，同样是通过TEB读取PEB BeingDebugged的值：

![图片31.png](https://image.3001.net/images/20181008/1538982593_5bbb02c1da3d1.png!small)

又调用一次VirtualAlloc分配内存2：

![图片32.png](https://image.3001.net/images/20181008/1538982627_5bbb02e385622.png!small)

![图片33.png](https://image.3001.net/images/20181008/1538982638_5bbb02eed5b2c.png!small)

跟到下面又发现对PEB结构的访问，偏移为0x68。

其实不太清楚偏移0x68是什么，就查了一下：

>
> PEB有一个名为NtGlobalFlag（偏移量为0x68）的字段，程序可以挑战识别它们是否正在被调试。通常，当未调试进程时，NtGlobalFlag字段包含值0x0。在调试进程时，该字段通常包含值0x70。

此时这个值正好为0x70，所以这个je不能跳。

继续单步跟，会调用很多次DllFuncitonCall，可以看到获取了许多API的地址，如ShellExecuteW,WriteFile,CreateFile,VirtualProtect,CreateProcess等。

接下来又分配了内存3，地址为：

![图片35.png](https://image.3001.net/images/20181008/1538982768_5bbb0370d9949.png!small)

来看看分配的这三块内存的状态：

![图片36.png](https://image.3001.net/images/20181008/1538982808_5bbb039818d3b.png!small)

目前除了刚分配那个不能执行，其他的都可读可写可执行：

![图片37.png](https://image.3001.net/images/20181008/1538982890_5bbb03eaad0d4.png!small)

往内存0x3430000赋值：

![图片38.png](https://image.3001.net/images/20181008/1538982847_5bbb03bf8bf6c.png!small)

开始解码：

![图片39.png](https://image.3001.net/images/20181008/1538982925_5bbb040d5acb8.png!small)

解码完成后，有点PE头的样子了，只是少了标志性的”MZ”：

![图片40.png](https://image.3001.net/images/20181008/1538982960_5bbb04305b759.png!small)

调用GetCommandLineW，以获取的路径为参数创建子进程：

![图片41.png](https://image.3001.net/images/20181008/1538983266_5bbb056248d85.png!small)

调用ZwAllocateVirtualMemory在指定进程分配内存：

![图片43.png](https://image.3001.net/images/20181008/1538983316_5bbb05944568e.png!small)

将0x5A赋值给0x343600不完整的PE文件，后面还会写入’M’。

![图片44.png](https://image.3001.net/images/20181008/1538983409_5bbb05f187f55.png!small)

然后调用ZwWriteVirtualMemory写入内存空间，写入的内容地址正是0x343600。

![图片45.png](https://image.3001.net/images/20181008/1538983458_5bbb0622e5db4.png!small)

父进程将解密出来要执行的PE写入子进程的内存，然后中止当前进程。

##  **0x05 样本主体** ****

在之前的行为监控中，注意到，样本在C:\User\user\AppData\Romaing\目录下生成了三个文件
pid.txt，pidloc.txt，WindowsUpdate.exe。这些功能都是通过解密出来的PE实现的。样本的VB代码只相当于一个外壳，运行时解密、创建子进程、注入进程等。提取出来的这个PE载入ExeinfoPE，发现这个程序是.NET
Reactor类型的代码混淆。

![图片46.png](https://image.3001.net/images/20181008/1538983575_5bbb0697d9b06.png!small)

这里我用了de4dot-mod反混淆工具，不用工具直接动态调试也可以。

![图片47.png](https://image.3001.net/images/20181008/1538983609_5bbb06b983a9c.png!small)

去除反混淆后生成的文件变成了528KB，原文件大小为65512KB，用PEID打开，可以看到导入表只有一个动态链接库mscoree.dll，函数是_CoreExeMain。

![图片48.png](https://image.3001.net/images/20181008/1538983648_5bbb06e0560a6.png!small)

接下来尝试用.NET的反编译工具dnSpy试试。

![图片49.png](https://image.3001.net/images/20181008/1538983686_5bbb0706ee3cb.png!small)

反编译成功后，发现该程序是恶意软件HawkEye，用于凭据窃取，包括电子邮件Web浏览器，Bitcoin钱包，反病毒检查，键盘记录等。

 ***本文原创作者：Macc，本文属于FreeBuf原创奖励计划，未经允许禁止转载**

