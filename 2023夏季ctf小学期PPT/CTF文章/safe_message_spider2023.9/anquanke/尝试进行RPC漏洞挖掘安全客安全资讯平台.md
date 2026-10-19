# 尝试进行RPC漏洞挖掘

阅读量 **336209**

|评论 **1**

发布时间 : 2019-01-10 10:23:04

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p403.ssl.qhimgs4.com/t014908ca95336cf9b9.png)

作者：houjingyi

## 0x00 摘要

2018年8月27日名为sandboxescaper的网友上传了一份win10本地提权的0day利用代码(后被微软修复并分配CVE编号CVE-2018-8440)，我通过对历史漏洞进行研究，对Windows系统中RPC(Remote
Procedure
Call,远程过程调用)漏洞挖掘进行了简单的探索，和大家分享一下探索的过程。理解这种攻击的工作方式将极大地帮助其他研究人员发现类似于sandboxescaper在Windows任务计划程序中发现的漏洞，这篇文章中首先回顾sandboxescaper和google
project zero发现的历史漏洞原理，接着介绍对类似漏洞挖掘的尝试和一些成果，最后提出一些继续挖掘类似漏洞的方法。

## 0x01 历史漏洞回顾

简单回顾一下CVE-2018-8440的原理：SchRpcSetSecurity函数在win10中会检测C:\Windows\Tasks目录下是否存在后缀为.job的文件，如果存在则会写入DACL(Discretionary
Access Control
List,自主访问控制列表)数据。如果将job文件硬链接到特定的dll那么特定的dll就会被写入DACL数据，本来普通用户对特定的dll只具有读权限，这样就具有了写权限，接下来向dll写入漏洞利用代码并启动相应的程序就可以提权了。详细的分析请阅读参考资料中此前发布的预警通告。

那么首先可以想到的是RPC中是否还有类似的函数存在同样的问题呢？无独有偶，在2018年4月google project
zero披露过SvcMoveFileInheritSecurity函数中的漏洞。

    
    
    void SvcMoveFileInheritSecurity(LPCWSTR lpExistingFileName, 
                                   LPCWSTR lpNewFileName, 
                                   DWORD dwFlags) {
     PACL pAcl;
     if (!RpcImpersonateClient()) {
       // Move file while impersonating.
       if (MoveFileEx(lpExistingFileName, lpNewFileName, dwFlags)) {
         RpcRevertToSelf();
         // Copy inherited DACL while not.
         InitializeAcl(&pAcl, 8, ACL_REVISION);
         DWORD status = SetNamedSecurityInfo(lpNewFileName, SE_FILE_OBJECT, 
             UNPROTECTED_DACL_SECURITY_INFORMATION | DACL_SECURITY_INFORMATION,
             nullptr, nullptr, &pAcl, nullptr);
           if (status != ERROR_SUCCESS)
             MoveFileEx(lpNewFileName, lpExistingFileName, dwFlags);
       }
       else {
         // Copy file instead...
         RpcRevertToSelf();
       }
     }
    }

在继续深入之前先简单介绍一下Windows中的(Access Control
Model,访问控制模型)。如果一个Windows对象没有DACL，则系统允许每个人完全访问。如果对象具有DACL，则系统仅允许DACL中的ACE(Access
Control
Entry,访问控制条目)明确允许的访问。如果DACL中没有ACE，则系统不允许任何人访问。下图是一个拒绝用户Andrew访问，允许A组成员写入，允许所有人读取和执行的DACL的例子。

![](https://p403.ssl.qhimgs4.com/t0183ae4dbb0b86a6ab.png)

回到SvcMoveFileInheritSecurity函数。这个函数的功能应该是移动文件到一个新的位置，然后调用SetNamedSecurityInfo函数将所有继承的ACE应用于新目录中的DACL。为了确保这个函数不会以服务的用户身份运行时(这里是Local
System)允许任意用户移动任意文件，需要模拟一个RPC调用者(caller)。模拟是线程使用与拥有线程的进程不同的安全信息执行的能力。通常服务器应用程序中的线程模拟客户端，这允许服务器线程代表该客户端操作以访问服务器上的对象或验证对客户端自己对象的访问。Windows的RPC服务应用程序可以调用RpcImpersonateClient函数来模拟一个客户端。对于大多数的模拟，这个模拟线程可以调用RevertToSelf函数恢复到原来的安全描述符。

问题就在于此，当第一次调用MoveFileEx函数后会调用RpcRevertToSelf函数，然后调用SetNamedSecurityInfo函数。如果SetNamedSecurityInfo函数调用失败会再次调用MoveFileEx函数，尝试恢复原来的文件移动操作。第一个漏洞是有可能原来文件名所处的位置通过符号链接指向了别的地方，因此可以创建任意文件(CVE-2018-0826)。第二个漏洞是如果先硬链接像SYSTEM32目录中那些用户只有读取权限的文件，在移动后的硬链接文件上调用SetNamedSecurityInfo函数，SetNamedSecurityInfo函数会从新目录位置中提取继承的ACE，然后将ACE应用到被硬链接的文件上。由于这是作为SYSTEM执行的，这意味着任何文件都可以被赋予任意安全描述符，这将允许用户修改它(CVE-2018-0983)。

![](https://p403.ssl.qhimgs4.com/t01180ef7ade937b995.png)

修复也经历了一些波折，微软在2018年2月和3月分别发布了两个补丁之后才彻底解决该问题。修补后和修补前的SvcMoveFileInheritSecurity函数如图所示，解决方法是第一次调用MoveFileEx函数后不再调用RpcRevertToSelf函数恢复到原来的安全描述符。

![](https://p403.ssl.qhimgs4.com/t01a7f349fe58285557.png)

## 0x02 尝试挖掘类似漏洞

要试图寻找类似的漏洞，首先需要导出所有的RPC函数。在A view into ALPC-RPC这个talk中提到了RPCview这个工具，这个工具可以用来反编译并查看RPC
interface，界面是用QT写的。然而当下载下来运行时会出现下面这样的错误。

![](https://p403.ssl.qhimgs4.com/t013901110aee96a47e.png)

仔细阅读README之后发现需要自己添加rpcrt4.dll的版本。对于win10来说，修改RpcCore\RpcCore4_32bits\RpcInternals.h和RpcCore\RpcCore4_64bits\
RpcInternals.h，如下所示。

![](https://p403.ssl.qhimgs4.com/t01c37ee27ce17741d4.png)

写一个bat编译。

    
    
    set CMAKE_PREFIX_PATH=C:\Qt\Qt5.9.1\5.9.1\msvc2017_64
    cmake ..\.. -G"Visual Studio 15 2017 Win64"
    cmake --build . --config release
    cd D:\ALPC-fuzz\RpcView\Build\x64\bin\Release
    mkdir RpcView64
    copy *.dll RpcView64\
    copy *.exe RpcView64\
    C:\Qt\Qt5.9.1\5.9.1\msvc2017_64\bin\windeployqt.exe --release RpcView64

以管理员身份运行编译好的RpcView.exe(普通用户权限反编译出来的结果较少)。

![](https://p403.ssl.qhimgs4.com/t01b02b5b684f79a505.png)

Decompilation窗口是对指定interface反编译的结果，其中函数名都是ProcX的形式，为了得到函数名需要正确设置符号路径。该工具似乎并不支持微软的符号服务器，所以把c:\windows\system32目录下所有的dll的符号下载到本地。

    
    
    symchk /s srv*c:\symbol*https://msdl.microsoft.com/download/symbols c:\windows\system32\*.dll

设置_NT_SYMBOL_PATH环境变量。

![](https://p403.ssl.qhimgs4.com/t01c0e471a45ad7909c.png)

现在能够反编译出来函数名了，需要对源代码做适当的修改让它一次性导出所有反编译结果，而不用一个一个去点。主要修改了源代码中下面几处地方。

在EndpointsWidget.cpp的EndpointsWidget_C::AddEndpoint函数开始时添加了一些代码导出反编译的Endpoints。

![](https://p403.ssl.qhimgs4.com/t01ab225bec982a4548.png)

在InterfacesWidget.cpp的InterfacesWidget_C::AddInterfaces函数返回前增加了调用InterfaceSelected函数的循环。

![](https://p403.ssl.qhimgs4.com/t019d5df02fe2ad92c6.png)

在InterfacesWidget_C::InterfaceSelected函数中首先检查uuid是否重复避免陷入死循环。

![](https://p403.ssl.qhimgs4.com/t0196013ee1eaed0a17.png)

原来反编译需要右键点击Decompile，所以注释掉了这部分代码使得InterfacesWidget_C::InterfaceSelected函数能够直接调用SigDecompileInterface函数。

![](https://p403.ssl.qhimgs4.com/t019eb506e3cf3f4719.png)

修改了IdlInterface.cpp的IdlInterface::dump函数，把反编译结果写到文件中。

![](https://p403.ssl.qhimgs4.com/t018aa91c52670aae20.png)

此外还有其它一些因为编译语言环境不同的修改。运行修改版的RPCview效果如下。

![](https://p403.ssl.qhimgs4.com/t0194ef2144fae76b1a.png)

之前出过问题的SvcMoveFileInheritSecurity函数和SchRpcSetSecurity函数的函数名都带有Security，来看看还有没有函数名中含有Security的函数。

![](https://p403.ssl.qhimgs4.com/t017555c1bc55615469.png)

除了SvcMoveFileInheritSecurity函数和SchRpcSetSecurity函数，果然还有一些函数名中含有Security的函数。比如这里的NetrpSetFileSecurity函数，看起来真的很有可能存在类似的问题。在IDA中看看反编译出的代码。

![](https://p403.ssl.qhimgs4.com/t01f57308002ab93484.png)

如果RtlValidRelativeSecurityDescriptor函数和SetFileSecurityW函数之间调用了RpcRevertToSelf函数，就像之前存在漏洞的SvcMoveFileInheritSecurity函数一样那么很有可能也能用这个函数提权，不过这个函数中是不存在这种漏洞的。

虽然在初次尝试挖掘过程中没有能够找到类似的问题，但是猜测sandboxescaper所披露的CVE-2018-8440应该是用和文中类似的方法发现的。之后fortinet也对RPCview进行了类似的改造。

![](https://p403.ssl.qhimgs4.com/t0137e257376f9d03cf.png)

## 0x03 RPC Fuzzing

回到之前的talk：A view into ALPC-RPC，研究人员开源了一个RPC
fuzz工具RPCForge，但是这个工具并不能直接使用，因为对方没有开源如何生成待fuzz的interface的这部分代码，而只给出了5个示例的interface。

![](https://p403.ssl.qhimgs4.com/t0192c453348d2132ba.png)

RPCForge的作者之一也是PythonForWindows这个库的作者，这个库中提供了一些方便的封装函数，可以节省开发RPC客户端的时间。RPCForge也用到了这个库。其实RPCForge的原理特别简单，就是不断去调用这些RPC函数，观察是否有崩溃或者异常。函数的参数是通过用sulley中提供的原始数据生成的。

![](https://p403.ssl.qhimgs4.com/t013501046f899d8817.png)

虽然现在已经导出了所有interface反编译的结果，但是在此前修改的RPCview反编译的格式和RPCForge用的格式并不相同，于是尝试编写了简易的python脚本，通过正则对两个工具的格式进行转换。

![](https://p403.ssl.qhimgs4.com/t012bc0e3cd691810b5.png)

由于有一些interface并没有能够下载到对应的符号，加之一些结构体中数据过于复杂未进行处理，在RPCview反编译出来的两百多个interface中能够fuzz的只有一百多个。

在运行RPCForge一段时间后，就在win10最新版上跑出了两个BSOD，第一个直到现在仍然能在最新的win10正式版和预览版上复现，第二个可以在win10
1803上复现，不能在win10 1809上复现(更多的版本没有测试)。

首先是第一个漏洞：

![](https://p403.ssl.qhimgs4.com/t0194de6a14754e543b.png)

![](https://p403.ssl.qhimgs4.com/t01b0a6dbd7460ef01a.png)

![](https://p403.ssl.qhimgs4.com/t01786c7c6ba084eb56.png)

原理非常简单，BfeRpcEngineClose函数没有检查传进来的参数，直接访问了非法的地址。

![](https://p403.ssl.qhimgs4.com/t01c3a053c42d7075e0.png)

接着是第二个漏洞：

![](https://p403.ssl.qhimgs4.com/t01ed82fe309bd50a32.png)

![](https://p403.ssl.qhimgs4.com/t01bb46951add20c7ec.png)

![](https://p403.ssl.qhimgs4.com/t0110e920977f6dcfa1.png)

当一些%s被作为Srv_CreateResourcePolicy函数的参数传入时Srv_CreateResourcePolicy函数最终调用到vsnwprintf函数，使用栈上的值作为字符串的地址，由于没有检查%s个数导致非法地址访问，多一个%s产生了BSOD。

将这两个问题报告给MSRC之后，MSRC以”Beyond causing a crash this doesn’t appear to leak any
data or escalate privileges in any way”为由拒绝修复。

![](https://p403.ssl.qhimgs4.com/t01e4b028ca1628e0c7.png)

## 0x04 一些调试技巧

在确定漏洞的具体成因时需要调试，但此处的调试与常规稍有区别，因为含有漏洞函数的dll是被加载到system的svchost.exe中运行的，不能直接用内核态调试sys的方法，用户态调试也因为权限问题不太好操作。在此采用了下面的方法进行调试。

搭建好双机调试环境之后首先确定含有漏洞函数的dll的svchost.exe的进程号，例如30c，首先查看进程信息。

    
    
    1: kd> !process 30c 0
    Searching for Process with Cid == 30c
    PROCESS ffffb9010a30b540
        SessionId: 0  Cid: 030c    Peb: a1e044f000  ParentCid: 024c
        DirBase: 21b00002  ObjectTable: ffffd98b2160cb00  HandleCount: 1145.
        Image: svchost.exe

使用得到的地址切换到该进程上下文，重新加载用户态符号之后再次侵入式切换。

    
    
    1: kd> .process /p ffffb9010a30b540
    Implicit process is now ffffb901`0a30b540
    .cache forcedecodeuser done
    1: kd> .reload /f /user
    Loading User Symbols
    1: kd> .process /i /p ffffb9010a30b540
    You need to continue execution (press 'g' <enter>) for the context
    to be switched. When the debugger breaks in again, you will be in
    the new process context.

在存在漏洞函数上下断点，g之后运行poc即可断下。

    
    
    1: kd> bp resourcepolicyserver!Srv_CreateResourcePolicy
    1: kd> g
    Break instruction exception - code 80000003 (first chance)
    nt!DbgBreakPointWithStatus:
    fffff802`085d4980 cc              int     3
    1: kd> g
    Breakpoint 0 hit
    resourcepolicyserver!Srv_CreateResourcePolicy:
    0033:00007ffa`0d91afb0 4883ec38        sub     rsp,38h

如果存在漏洞函数所在的dll默认并没有被加载可以在poc代码中先调用该dll中的其它函数并且设置断点，待该dll被加载之后再在想要下断点的函数处断下，继续运行poc代码即可。为了方便调试复现，还可以用pyinstaller将python代码打包成可以运行的exe。

    
    
    pyinstaller.exe -F D:\20181009\poc\poc.py --hidden-import interfaces.test

## 0x05 继续挖掘的方向

时至今日，除了CVE-2018-8440这个能够直接提权的漏洞外，sandboxescaper还公布了两个越权删除任意文件的EXP(CVE-2018-8584)和一个越权读取任意文件的EXP。12月份公布的后两个漏洞虽然也是Windows中的逻辑问题，但是与RPC无关。已经被修复的CVE-2018-8584是RpcDSSMoveFromSharedFile函数中的漏洞，同样也是一个逻辑问题，当任意权限的用户调用该函数时，该函数会将第三个参数所代表的文件删除。在此之前，通过CreateMountPoint函数建立两个文件夹之间的软链接，达到删除目录下的特定文件从而将所链接目录下的文件一并删除的效果。

为了能够继续发现RPC中的漏洞，通过研究发现还有以下尝试方向：

  1. 静态审计函数名中含有Move，Copy，Security等词的高危RPC函数。
  2. 通过Process Monitor之类的工具动态监控其它的RPC函数在运行时有无调用到1中所说的高危函数。
  3. RPC Forge这个工具原理还比较简单，作者也坦言道：  

> This is more a PoC than a real fuzzer. Its aim was to be able to forge a
> valid serialized stream reaching RPC methods code without being rejected by
> the Windows RPC Runtime (because of bad arguments type leading to error:
> RPC_X_BAD_STUB_DATA).Thus, it doesn’t contain any instrumentation in the
> server side to improve code coverage.

通过改进原始数据或者增强代码覆盖率进行发现更多的漏洞的尝试时发现，基于代码覆盖率统计做驱动反馈的效果不佳。Pin或DynamoRIO类似的工具多用于用户态，Qemu或Bochs等虚拟化技术多用于内核态，对于system权限的svchost.exe进程似乎都不太方便。另外就是要fuzz的dll太多了，被加载到几十个进程，每个dll又只有那么几个函数，输入数据覆盖的代码有限而且分散，效果不会太好。

另外无论是静态审计还是动态监控也与预期有一定差异。在理解CVE-2018-8440后可能认为发现它的过程比较简单，但是在调试后会发现设置文件安全描述符的函数代码是一处虚函数调用，静态审计无法看到，动态调试才能确定最终调用了taskcomp!SetSDNotification函数，按照传递的任务名称参数和SDDL安全描述字串设置%systemdir%\Tasks\任务名称.job的安全属性。

## 0x06 总结

通过改进完善开源fuzz工具和研究已经公布的漏洞来寻找类似的漏洞仍然是找到漏洞的一种高效的方式。RPC中仍然存在非常有趣的逻辑漏洞等待人们发现，快速找到这些逻辑漏洞可能需要对系统深入的理解以及一些不同于查找内存破坏漏洞的手段。

本文用到的所有代码开源在<https://github.com/houjingyi233/ALPC-fuzz-study>，文中提到的两个BSOD的代码和打包好的可执行文件在<https://github.com/houjingyi233/windows-BSOD>。

## 0x07 参考链接

  1. <https://blog.0patch.com/>
  2. [http://sandboxescaper.blogspot.com](http://sandboxescaper.blogspot.com/)
  3. <https://github.com/silverf0x/RpcView>
  4. [Windows全版本提权之Win10系列解析](https://www.freebuf.com/vuls/184090.html)
  5. [Windows: StorSvc SvcMoveFileInheritSecurity Arbitrary File Creation EoP](https://bugs.chromium.org/p/project-zero/issues/detail?id=1427)
  6. [Windows: StorSvc SvcMoveFileInheritSecurity Arbitrary File Security Descriptor Overwrite EoP](https://bugs.chromium.org/p/project-zero/issues/detail?id=1428)
  7. [A view into ALPC-RPC](https://pacsec.jp/psj17/PSJ2017_Rouault_Imbert_alpc_rpc_pacsec.pdf)
  8. [win10本地提权0Day预警](https://cert.360.cn/warning/detail?id=208606780533f78f0731544f1935f8b2)
  9. [Windows Exploitation Tricks: Exploiting Arbitrary File Writes for Local Elevation of Privilege](https://googleprojectzero.blogspot.com/2018/04/windows-exploitation-tricks-exploiting.html)
  10. [RPC Bug Hunting Case Studies – Part 1](https://www.fortinet.com/blog/threat-research/the-case-studies-of-microsoft-windows-remote-procedure-call-serv.html)
  11. [Introduction to Logical Privilege Escalation on Windows](https://conference.hitb.org/hitbsecconf2017ams/materials/D2T3%20-%20James%20Forshaw%20-%20Introduction%20to%20Logical%20Privilege%20Escalation%20on%20Windows.pdf)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **360CERT安全通告** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/169382](/post/id/169382)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)
  * [RPC](/tag/RPC)

 **+1** __29赞

 __收藏

![](https://p0.ssl.qhmsg.com/dm/200_200_100/t013be54b59d8ac5fe6.jpg)
360CERT安全通告

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

