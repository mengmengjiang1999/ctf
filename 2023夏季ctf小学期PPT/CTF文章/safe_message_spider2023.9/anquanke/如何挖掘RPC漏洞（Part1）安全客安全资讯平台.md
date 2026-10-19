# 如何挖掘RPC漏洞（Part 1）

阅读量 **470958**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-12-09 10:00:16

 **x**

##### 译文声明

本文是翻译文章，文章原作者 fortinet，文章来源：fortinet.com

原文地址：<https://www.fortinet.com/blog/threat-research/the-case-studies-of-microsoft-windows-remote-procedure-call-serv.html>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t015771d9367abf00eb.gif)

## 一、前言

2018年8月下旬，一名研究人员（SandboxEscaper）公开了一个Windows本地权限提升0day漏洞。在互联网上公开后不到两周时间内，该漏洞就已经被恶意软件攻击者所使用（参考ESET发表的[文章](https://www.welivesecurity.com/2018/09/05/powerpool-malware-exploits-zero-day-vulnerability/)）。这件事情在InfoSec社区造成了一定程度的混乱，也引起了FortiGuard实验室的警觉。

FortiGuard实验室认为，理解这类攻击原理非常重要，可以帮助其他研究人员挖掘出类似SandboxEscaper在Windows任务计划程序（Windows
Task Scheduler）中找到的漏洞。在本文中，我们将与大家分享如何滥用RPC服务器上的符号链接来提升权限。

事实证明，Windows Task Scheduler通过RPC服务器对外公开的某个RPC（Remote Procedure Call，远程过程调用）
API中存在漏洞。在Windows中，大多数RPC服务器都托管于以本地系统权限运行的系统进程中，低权限的RPC客户端可以与RPC服务器进行交互。与其他软件一样，这些RPC服务器也可能存在漏洞，如拒绝服务、内存损坏、逻辑错误等等。换句话说，攻击者可以利用RPC服务器中存在的任何漏洞来发起攻击。

这个0day漏洞之所以如此流行，其中一个原因在于底层漏洞利用起来非常简单。这是一个程序逻辑错误漏洞，只要使用正确的工具及技术就比较容易发现。攻击者通常使用伪造的符号链接（symbolic
link）来利用这类权限提升漏洞，越权至某些文件或者目录，从而能让普通用户提升权限。如果大家对这方面内容比较感兴趣，来自Google Project
Zero的James Forshaw分享了关于符号链接攻击的各种资源，大家可以作为参考。

## 二、RPC服务器运行时及静态分析

进入新的研究领域后，在自己开发工具之前，最好先看一下网上是否已经有开源工具。幸运的是，微软RPC协议非常出名，在过去十几年里已经有研究人员在这方面做了许多优秀的逆向分析工作。研究人员可以使用[RpcView](http://www.rpcview.org/)这款开源工具，这个工具非常方便，可以识别Windows系统上运行的RPC服务。这是我最喜欢的RPC工具之一，具有各种强大的功能，如搜索RPC接口的UUID（Universal
Unique Identifier）、RPC接口名等等。

然而，我们的目的是将所有RPC信息反编译并导出到文本文件中，该工具并不满足我们的要求。幸运的是，在阅读源码后，我们发现工具开发者已经集成了我们所需的功能，但默认情况下该功能没有启用，只能在调试模式下使用某个命令行参数触发。在这个限制条件下，我们选择将已有的`DecompileAllInterfaces`函数集成到RpcView
GUI中。如果大家也想使用这个功能，可以访问我们的[Github页面](https://github.com/fortiguard-lion/RpcView)，下载我们定制的RpcView工具。在下文中大家就可以看到“反编译所有接口”这个功能的好处。

![](https://p3.ssl.qhimg.com/t018489193ba6e3a6ef.gif)

图1. RpcView反编译所有接口

当分析RPC服务器的行为时，我们总是会通过RPC接口调用服务器对外提供的API。我们可以通过RPC客户端向服务器发送RPC请求，与RPC交互，然后使用SysInternals中的Process
Monitor工具来观察服务器的行为。在我看来，最方便的做法是编写脚本，而不是开发C/C++ RPC客户端，因为前者不需要代码编译过程，比较节省时间。

我们选择使用[PythonForWindows](https://github.com/hakril/PythonForWindows)这个库。这个库能够帮助我们以Python的方式来抽象处理Windows功能，但需要依赖Python的`ctypes`库。这个库中还包含一些RPC库，这些库提供了一些方便的封装函数，可以节省我们开发RPC客户端的时间。比如，典型的RPC客户端程序需要定义接口定义语言，并且我们需要手动实现绑定操作，这个过程通常需要涉及到一些C++代码。从下面两段代码中，我们可以清晰地看到在实现RPC客户端方面脚本语言和编程语言之间的区别：

    
    
    import sys
    import ctypes
    import windows.rpc
    import windows.generated_def as gdef
    from windows.rpc import ndr
    
    StorSvc_UUID = r"BE7F785E-0E3A-4AB7-91DE-7E46E443BE29"
    
    class SvcSetStorageSettingsParameters(ndr.NdrParameters):
    MEMBERS = [ndr.NdrShort, ndr.NdrLong, ndr.NdrShort, ndr.NdrLong]
    
    def SvcSetStorageSettings():
    print "[+] Connecting...."
    client = windows.rpc.find_alpc_endpoint_and_connect(StorSvc_UUID, (0,0))
    print "[+] Binding...."
    iid = client.bind(StorSvc_UUID, (0,0))
    params = SvcSetStorageSettingsParameters.pack([0, 1, 2, 0x77])
    print "[+] Calling SvcSetStorageSettings"
    result = client.call(iid, 0xb, params)
    if len(str(result)) > 0:
    print " [*] Call executed successfully!"
    stream = ndr.NdrStream(result)
    res = ndr.NdrLong.unpack(stream)
    if res == 0:
    print " [*] Success"
    else:
    print " [*] Failed"
    
    if __name__ == "__main__":
    SvcSetStorageSettings()
    

代码1. 使用PythonForWindows RPC Client开发的SvcSetStorageSettings

    
    
    RPC_STATUS CreateBindingHandle(RPC_BINDING_HANDLE *binding_handle)
    {
    RPC_STATUS status;
    RPC_BINDING_HANDLE v5;
    RPC_SECURITY_QOS SecurityQOS = {};
    RPC_WSTR StringBinding = nullptr;
    RPC_BINDING_HANDLE Binding;
    
    StringBinding = 0;
    Binding = 0;
    status = RpcStringBindingComposeW(L"BE7F785E-0E3A-4AB7-91DE-7E46E443BE29", L"ncalrpc", nullptr, nullptr, nullptr,&StringBinding);
    if (status == RPC_S_OK)
    {
    status = RpcBindingFromStringBindingW(StringBinding, &Binding);
    RpcStringFreeW(&StringBinding);
    if (!status)
    {
    SecurityQOS.Version = 1;
    SecurityQOS.ImpersonationType = RPC_C_IMP_LEVEL_IMPERSONATE;
    SecurityQOS.Capabilities = RPC_C_QOS_CAPABILITIES_DEFAULT;
    SecurityQOS.IdentityTracking = RPC_C_QOS_IDENTITY_STATIC;
    
    status = RpcBindingSetAuthInfoExW(Binding, 0, 6u, 0xAu, 0, 0, (RPC_SECURITY_QOS*)&SecurityQOS);
    if (!status)
    {
    v5 = Binding;
    Binding = 0;
    *binding_handle = v5;
    }
    }
    }
    
    if (Binding)
    RpcBindingFree(&Binding);
    return status;
    }
    
    VOID RpcSetStorageSettings()
    {
    RPC_BINDING_HANDLE handle;
    RPC_STATUS status = CreateBindingHandle(&handle);
    
    if (status != RPC_S_OK)
    {
    _tprintf(TEXT("[-] Error creating handle %dn"), status);
    return;
    }
    
    RpcTryExcept
    {
    if (!SUCCEEDED(SvcSetStorageSettings(0, 1, 2, 0x77))
    {
    _tprintf(TEXT("[-] Error calling RPC APIn"));
    return;
    }
    
    }
    RpcExcept(1)
    {
    
    RpcStringFree(&instanceid);
    
    }
    RpcEndExcept
    }
    

代码2. 使用C++ RPC Client开发的SvcSetStorageSettings

当RPC客户端成功调用相应的RPC API后，我们可以使用Process Monitor来监控程序活动轨迹。Process
Monitor对动态分析来说非常有用，可以提供基于事件的API运行时信息。值得注意的是，Process
Monitor中有个较少使用的功能，可以提供调用栈（call-stack）信息，如图2所示。利用这个信息，我们可以跟踪某个事件的API调用过程。

![](https://p0.ssl.qhimg.com/t01c82814a04c2636ab.png)

图2. Process Monitor API调用栈功能

在使用IDA
Pro之类的工具静态分析时，我们可以根据上图中`Address`和`Path`信息精确定位相应的模块及函数例程。这一点非常有用，因为有些时候我们可能无法单独使用Process
Monitor输出信息来发现潜在的符号链接攻击特征。这时候反汇编工具的静态分析功能就能派上用场，可以帮助我们发现竞争条件问题，我们会在Part
2文章中讨论这方面内容。

## 三、UTC案例分析

大家是否知道微软会在Windows
10及更高版本系统上收集客户信息、数据以及文件相关信息？有没有想过背后的工作原理？如果大家感兴趣，可以阅读[这篇文章](https://www.zdnet.com/article/windows-10-telemetry-secrets/)，其中介绍了UTC（Universal Telemetry Client，通用遥测客户端）背后的工作机制。

为了开启下一阶段分析过程，我们首先使用RpcView GUI将所有RPC接口导出到文本文件中，结果文件中包含RPC服务器中可以调用的所有RPC
API。从输出文件中，我们需要查找可以接受宽字符串作为输入的RPC
API，最终从`diagtrack.dll`中找到了比较有趣的一个RPC接口。随后，我们可以确认这个DLL组件负责UTC功能的的具体实现，比如，我们可以在RpcView
GUI中发现这个DLL的描述为`Microsoft Windows Diagnostic Tracking`。

![](https://p3.ssl.qhimg.com/t0107bce57da6a55672.png)

图3. 使用RpcView分析UTC相关DLL组件，其中某个RPC接口接受宽字符串作为输入数据

请记住，这里我们的目标是找到某个API，这个API可以接收文件路径作为输入参数，最终可能导致权限提升问题（如Windows Task
Scheduler中存在的问题）。但在图3中，我们发现有16个API可能满足我们的要求。显然，我们需要过滤掉不符合我们条件的API。因此我们使用IDA
Pro，开始静态分析，找到待深入分析的目标API。

我首先找到的是`RpcServerRegisterIf`这个RPC函数，这个函数通常用来注册RPC服务器上的接口规范（interface
specification）。接口规范中包含托管于特定RPC服务器上的RPC接口定义。根据MSDN官方文档的描述，接口规范位于函数的第一个参数中，该参数遵循`RPC_SERVER_INTERFACE`数据结构，结构定义如下：

    
    
    struct _RPC_SERVER_INTERFACE
    {
    unsigned int Length;
    RPC_SYNTAX_IDENTIFIER InterfaceId;
    RPC_SYNTAX_IDENTIFIER TransferSyntax;
    PRPC_DISPATCH_TABLE DispatchTable;
    unsigned int RpcProtseqEndpointCount;
    PRPC_PROTSEQ_ENDPOINT RpcProtseqEndpoint;
    void *DefaultManagerEpv;
    const void *InterpreterInfo;
    unsigned int Flags;
    };
    

接口规范中的`InterpreterInfo`是指向`MIDL_SERVER_INFO`数据结构的一个指针，该结构由`DispatchTable`指针所组成，指针中保存特定RPC接口所支持的接口API信息。这的确是我们在寻找的字段。

    
    
    typedef struct _MIDL_SERVER_INFO_
    {
    
    PMIDL_STUB_DESC pStubDesc;
    const SERVER_ROUTINE* DispatchTable;
    PFORMAT_STRING ProcString;
    const unsigned short* FmtStringOffset;
    const STUB_THUNK* ThunkTable;
    PRPC_SYNTAX_IDENTIFIER pTransferSyntax;
    ULONG_PTR nCount;
    PMIDL_SYNTAX_INFO pSyntaxInfo;
    } MIDL_SERVER_INFO, *PMIDL_SERVER_INFO;
    

通常情况下，我们可以使用IDA Pro遍历导入地址表（IAT）来定位`DispatchTable`，如下图所示：

![](https://p4.ssl.qhimg.com/t010c28db465b476b1d.gif)

图4. 使用IDA Pro遍历IAT寻找RPC公开的API

定位到UTC的接口API（前缀为`UtcApi`，如图4所示）后，我们尝试判断这些接口API中是否涉及到ACL（Access Control
List，访问控制列表）相关API，比如`SetNamedSecurityInfo`以及`SetSecurityInfo`等。之所以对这些ACL
API感兴趣，是因为更改对象（包括文件、目录以及注册表等）的DACL（discretionary access
control，自主访问控制）安全描述符时会用到这些API。IDA Pro中还有另一个有用的功能，就是Proximity
view，可以在一张图中显示出某个函数例程的调用图。我们可以使用Proximity view来寻找ACL API中引用或者调用的函数例程。

![](https://p4.ssl.qhimg.com/t01562c5310db8a6f4a.png)

图5. IDA的Proximity view可以显示`SetSecurityInfo`与`diagtrack.dll`中函数例程的关系

然而，当我们想去寻找`SetSecurityInfo`与`UtcApi`之间的关系时，IDA
Pro并没有给出任何结果。进一步研究后，我们发现`UtcApi`会将客户端的RPC请求放入异步线程工作队列中进行处理。如图5所示，当触发`Microsoft::Diagnostic::EscalationWorkItem::Execute`时，就会执行`SetSecurityInfo`。这是一个回调函数，用来处理堆积在工作队列中、来自RPC客户端的请求。

此时，我们需要澄清如何提交请求。分析各种应用后，我们找到了Microsoft Feedback Hub，这是一个UWP（Universal Windows
Platform，通用Windows平台）应用程序，已在Windows
10默认安装。有些情况下，调试UWP应用能够给我提供很多信息。不幸的是，我们无法使用WinDbg直接打开或者attach
UWP应用。然而，我们可以使用Windows 10 SDK中Windows
Debugger包含的PLMDebug工具来启用UWP应用调试功能。首先我们可以通过Powershell内置cmdlet来确定Feedback
Hub的完整包名：

    
    
    PS C:Usersresearcher> Get-AppxPackage | Select-String -pattern "Feedback"
    Microsoft.WindowsFeedbackHub_1.1809.2971.0_x86__8wekyb3d8bbwe
    PS C:Usersresearcher> cd "c:Program FilesWindows Kits10Debuggersx86"
    PS C:Program FilesWindows Kits10Debuggersx86>
    PS C:Program FilesWindows Kits10Debuggersx86> .plmdebug.exe /query 
    Microsoft.WindowsFeedbackHub_1.1809.2971.0_x86__8wekyb3d8bbwe
    Package full name is Microsoft.WindowsFeedbackHub_1.1809.2971.0_x86__8wekyb3d8bbwe.
    Package state: Unknown
    SUCCEEDED
    PS C:Program FilesWindows Kits10Debuggersx86>
    

获取完整包名后，我们可以再次使用PLMDebug，启用Feedback Hub的UWP调试功能：

    
    
    c:Program FilesWindows Kits10Debuggersx86>plmdebug.exe /enabledebug Microsoft.WindowsFeedbackHub_1.1809.2971.0_x86__8wekyb3d8bbwe "c:program fileswindows kits10Debuggersx86windbg.exe"
    Package full name is Microsoft.WindowsFeedbackHub_1.1809.2971.0_x86__8wekyb3d8bbwe.
    Enable debug mode
    SUCCEEDED
    

下次启动Feedback Hub时，应用就会自动attach到WinDbg。

![](https://p3.ssl.qhimg.com/t01e341605215b2b1d8.png)

图6. 根据Process Monitor Event Properties窗口确定API调用的偏移地址

启动Feedback Hub后，我们可以遵循应用在屏幕上给出的提示进行操作，然后就能在Process
Monitor中观察各种活动记录。这是个好兆头，表明我们的方向没有问题。当我们分析`SetSecurityFile`事件的调用栈时，我们发现`SetSecurityInfo`这个ACL
API 的偏移地址为`0x15A091`（我们可以在Event
Properties窗口的Process选项卡中找到`diagtrack.dll`的基址）。这个偏移地址位于`Microsoft::Diagnostics::Utils::FileSystem::SetTokenAclOnFile`例程中，如图6所示，我们也可以在图5的Proximity
view中找到这个值。这些信息表明我们可以利用Feedback Hub，最终得到我们想要的代码路径。

除此之外，从Process
Monitor输出信息中，我们还知道这个事件会尝试设置文件对象的DACL，但如果想通过静态代码分析来找出文件对象的获取方式可能是一件非常耗时的事情。幸运的是，我们可以将本地调试器attach到`svchost.exe`程序上，这是因为该进程不受PPL（Protected
Process Light）机制的保护，并且托管了具备管理员权限的UTC服务。这样我们就可以灵活地动态调试UTC服务，理解文件路径的获取过程。

将反馈信息通过Feedback
Hub提交后，所有的反馈信息和相关附件都会保存在临时目录中，格式为`%DOCUMENTS%\FeedbackHub\<guid>\diagtracktempdir<random_decimals>`。其中在`diagtracktempdir`后的十进制随机数使用`BCryptGenRandom`
API生成，这意味着所生成的随机数基本上无法预测。然而符号链攻击中非常重要的一环就是要预测文件或者目录的名称，因此随机生成的`diagtracktempdir`的确增加了符号链漏洞利用的难度。因此，我们需要深入其他例程，寻找其他潜在的漏洞。

当我们尝试理解如何设置`diagtracktempdir`安全描述符时，我们发现目标会使用显式安全描述符字符串（即`O:BAD:P(A;OICI;GA;;;BA)(A;OICI;GA;;;SY)`）来创建目录，这意味着对象的DACL只会绑定到Administrator以及本地系统用户。然而，如果设置了如下注册表键值，系统就会忽略显式安全描述符：

    
    
    HKEY_LOCAL_MACHINE\Software\Microsoft\Diagnostics\DiagTaskTestHooks\Volatile
    
    “NoForceCopyOutputDirAcl” = 1
    

简而言之，如果不存在如上表项，那么`diagtracktempdir`就会强制使用显式安全描述符，否则就会在目录上应用默认的DACL。这可能会引发一些安全问题，因为文件创建过程中不会使用任何模拟（impersonation）令牌。无论如何，如果我们具备注册表任意写入漏洞，就可以绕过该目录中显式安全描述符的限制。但这并不是我们想要的结果，因此我们最好还是回到Process
Monitor：

![](https://p2.ssl.qhimg.com/t01a1b636a46b93d9e4.png)

图7. 设置DACL，重命名`diagtracktempdir`目录

我们可以将图7的操作过程总结如下：

1、以本地系统权限授予当前登录用户对`diagtracktempdir`的访问权限；

2、通过模拟方式重命名`diagtracktempdir`目录；

3、通过模拟方式撤销当前登录用户对`diagtracktempdir`的访问权限。

图7的操作过程可以通过如下代码段来表示：

    
    
    bQueryTokenSuccessful = UMgrQueryUserToken(hContext, v81, &hToken);
    if ( hToken && hToken != -1 )
    {
    // This will GRANT access of the current logged in user to the directory in the specified handle
    bResultCopyDir = Microsoft::Diagnostics::Utils::FileSystem::SetTokenAclOnFile(&hToken, hDir, Sid, GRANT_ACCESS)
    if ( !ImpersonateLoggedOnUser(hToken) ) 
    {
    bResultCopyDir = 0x80070542;
    }
    }
    // Rename diagtracktempdir to GUID-styled folder name
    bResultCopyDir = Microsoft::Diagnostics::Utils::FileSystem::MoveFileByHandle(SecurityDescriptor, v65, Length);
    if ( bResultCopyDir >= 0 )
    {
    boolRenamedSuccessful = 1;
    // This will REVOKE access of the current logged in user to the directory in the specified handle
    bSetAclSucessful = Microsoft::Diagnostics::Utils::FileSystem::SetTokenAclOnFile(&hToken, hDir, Sid, REVOKE_ACCESS)if (bSetAclSucessful)
    {
    // Cleanup and RevertToSelf
    return;
    }
    }
    else
    {
    lambda_efc665df8d0c0615e3786b44aaeabc48_::operator_RevertToSelf(&hTokenUser);
    // Delete diagtracktempdir folder and its contents
    lambda_8963aeee26028500c2a1af61363095b9_::operator_RecursiveDelete(&v83);
    }
    

代码3：授予并取消当前用户对`diagtracktempdir`的访问权限

从代码3中，我们可知文件重命名操作会在什么情况下失败。如果`bResultCopyDir`的值小于0，那么执行流程就会调用`RecursiveDelete`函数。此外还需要注意的是，在调用`RecursiveDelete`函数之前，程序会先调用`RevertToSelf`函数来停止模拟，这意味着系统会使用本地系统权限来删除目标目录及目录内容。因此，如果我们能使用符号链接来将`diagtracktempdir`重定向到一个任意目录，就可以实现任意文件删除目标。幸运的是，微软已经消除了这个潜在的问题。如果目录设置了`FILE_ATTRIBUTE_REPARSE_POINT`标志（`junction`目录通常会设置该标志），那么`RecursiveDelete`函数就会显式跳过这些目录。因此我们可以确定，这个删除操作并不会带来任何安全风险。

由于我们无法实现任意文件删除，我们决定分享一下如何将任意文件写入`diagtracktempdir`目录中。查看代码，我们发现在递归删除操作完成后，UTC服务并不会撤销当前用户对`diagtracktempdir`目录的安全描述符。这是系统有意为之的行为，因为我们并不需要在一个即将被删除的目录上附加新的DACL，这是多余的操作。然而这也为攻击者提供了一个潜在的竞争条件机会，攻击者可以在同一个目录中创建带有独占文件句柄的文件来避免系统删除`diagtracktempdir`目录。当`RecursiveDelete`函数尝试打开和删除带有独占文件句柄的文件时，就会碰到共享冲突，然后正常退出执行。最终，攻击者可以将文件释放到受限目录（如`C:\WINDOWS\System32`）的`diagtracktetempdir`目录中并加以执行。

那么下一个问题就是，我们如何让文件重命名操作失败？查看`Microsoft::Diagnostics::Utils::FileSystem::MoveFileByHandle`的底层实现后，我们可以看到这本质上是一个封装函数，用来调用`SetFileInformationByHandle`
API。我们发现派生自该API的底层内核函数似乎总会获取到父目录的一个可写权限文件句柄。比如，如果文件句柄当前指向的是`c:\blah\abc`，那么系统就会尝试获取`c:\blah`目录具备可写权限的文件句柄。然而，如果我们我们指定当前登录用户不具备写入权限的某个目录，那么`Microsoft::Diagnostics::Utils::FileSystem::MoveFileByHandle`就可能无法正常执行。我们可以使用如下目录，因为这些目录不允许普通用户账户执行目录创建操作。

    
    
    C:\WINDOWS\System32
    C:\WINDOWS\tasks
    

由于请求过程中需要将大量log文件写入我们可控的`diagtracktempdir`目录中，这需要一定时间来处理，因此我们应该有较大的把握能够在竞争条件中获胜。因此，如果我们在目标目录中创建了独占文件句柄，那么大部分时间内，在搭载多核处理器的操作系统上我们应该都能完成任务。

接下来，我们需要找到办法，以编程方式使用`UtcApi`所需的正确参数来触发这条代码路径。由于我们能够在RPC函数上调试并设置断点，Feedback
Hub中的`NdrClientCall`函数可以让我们的工作更加轻松。从调试器中我们可以知道Scenario
ID，也可以知道需要发送给`UtcApi`的文件路径。在本例中，我们准备使用的Scenario
ID为`{1881A45E-01FD-4452-ACE4-4A23666E66E3}`，貌似`UtcApi_EscalateScenarioAsync`例程被触发时都能看到这个值，并且也能触及RPC服务器上我们所需的代码路径。需要注意的是，我们还可以使用这个文件路径来控制`diagtracktempdir`的具体创建位置。

    
    
    Breakpoint 0 hit
    eax=0c2fe7b8 ebx=032ae620 ecx=0e8be030 edx=00000277 esi=0c2fe780 edi=0c2fe744
    eip=66887154 esp=0c2fe728 ebp=0c2fe768 iopl=0 nv up ei pl nz na po nc
    cs=001b ss=0023 ds=0023 es=0023 fs=003b gs=0000 efl=00000202
    Helper+0x37154:
    66887154 ff15a8f08866 call dword ptr [Helper!DllGetActivationFactory+0x6d31 (6688f0a8)] ds:0023:6688f0a8={RPCRT4!NdrClientCall4 (76a74940)}
    0:027> dds esp l9
    0c2fe728 66892398 Helper!DllGetActivationFactory+0xa021
    0c2fe72c 66891dca Helper!DllGetActivationFactory+0x9a53
    0c2fe730 0e8be030
    0c2fe734 1881a45e // Scenario ID
    0c2fe738 445201fd
    0c2fe73c 234ae4ac
    0c2fe740 e3666e66
    0c2fe744 00000000
    0c2fe748 032ae620 // Escalation path
    0:027> du 032ae620
    032ae620 "E:\researcher\Documents\Feedback"
    032ae660 "Hub\{e04b7a09-02bd-42e8-a5a8-666"
    032ae6a0 "b5102f5de}\{e04b7a09-02bd-42e8-a"
    032ae6e0 "5a8-666b5102f5de}"
    

`UtcApi_EscalateScenarioAsync`的函数原型如下所示：

    
    
    long UtcApi_EscalateScenarioAsync (
    [in] GUID SecnarioID, 
    [in] int16 unknown, 
    [in] wchar_t* wszEscalationPath
    [in] long unknown2, 
    [in] long unknown3, 
    [in] long num_of_keyval_pairs, 
    [in] wchar_t **keys, 
    [in] wchar_t **values)
    

结合以上信息，我们的PoC代码操作过程可以分为如下几个步骤：

1、创建一个循环线程，监视我们的目标目录（如`C:\WINDOWS\SYSTEM32`），以便及时捕捉到`diagtracktempdir`的目录名；

2、创建另一个循环线程，该线程会创建`C:\WINDOWS\SYSTEM32\diagtracktempdir{random_decimal}\z`的一个独占句柄；

3、调用`UtcApi_EscalateScenarioAsync(1881A45E-01FD-4452-ACE4-4A23666E66E3)`，触发`Microsoft::Diagnostic::EscalationWorkItem::Execute`；

4、随后，攻击者可以向`C:\WINDOWS\SYSTEM32\diagtracktempdir{random_decimal}`目录中写入并执行任意文件，与此同时合法程序会认为`%SYSTEM32%`目录中只包含合法的OS文件。

我们的PoC演示了一种潜在利用方法，可以利用UTC服务在受限目录的静态目录中创建任意文件及目录。

![](https://p5.ssl.qhimg.com/t011f2a011c0a6ba00d.png)

图8. 可以在`diagtracktempdi`目录中创建任意文件的PoC代码

重申一下，如MSRC所述，如果不能控制或者重命名`diagtracktempdir`目录，这个PoC并不会对Windows系统带来安全风险。然而，恶意软件开发者通常会使用各种不同的技术（如UAC绕过技术），将文件写入Windows系统目录中，以便绕过启发式检测器。实际上，在探索PoC中可以使用的潜在文件路径时，我们发现`C:\WINDOWS\SYSTEM32\Tasks`目录包含普通用户账户的写入和执行权限，但没有读取权限，这也是为什么该目录经常会被恶意软件开发者用来存储恶意文件。

## 四、总结

在本文中，我们与大家分享了如何使用不同的工具和在线资源来寻找Windows
RPC服务器中的潜在安全风险。我们同样演示了逆向分析RPC服务器所需的一些基础知识。我们相信RPC服务器中还有其他潜在的安全风险尚未发掘，因此，我们将进一步加强Windows
RPC服务器的安全性。在下一篇文章中，我们会继续调查。改进我们的方法，继续发现其他RPC服务器漏洞。

本文翻译自fortinet.com [原文链接](https://www.fortinet.com/blog/threat-research/the-case-studies-of-microsoft-windows-remote-procedure-call-serv.html)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **興趣使然的小胃** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/167427](/post/id/167427)

安全客 - 有思想的安全新媒体

本文转载自: [fortinet.com](https://www.fortinet.com/blog/threat-research/the-case-studies-of-microsoft-windows-remote-procedure-call-serv.html)

如若转载,请注明出处： <https://www.fortinet.com/blog/threat-research/the-case-studies-of-microsoft-windows-remote-procedure-call-serv.html>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Windows](/tag/Windows)
  * [漏洞分析](/tag/漏洞分析)
  * [RPC](/tag/RPC)
  * [系统安全](/tag/系统安全)

 **+1** __6赞

 __收藏

![](https://p2.ssl.qhmsg.com/dm/200_200_100/t0104d1b8b4ca36e961.jpg) 興趣使然的小胃

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

