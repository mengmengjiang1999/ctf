### 遍历进程

首先要遍历本机进程，这里使用的api是 **WTSEnumerateProcessesEx** ，所属头文件 **wtsapi32.h**

    
    
    BOOL WTSEnumerateProcessesEx(
        HANDLE hServer,			// 主机服务器句柄 本机填 WTS_CURRENT_SERVER_HANDLE
        DWORD  *pLevel,			// 值为1 返回WTS_PROCESS_INFO_EX结构体数组 值为0 返回WTS_PROCESS_INFO结构体数组
        DWORD  SessionId,		        // 进程会话 枚举所有进程会话 填WTS_ANY_SESSION
        LPSTR  *ppProcessInfo,	        // 接收指向WTS_PROCESS_INFO_EX或WTS_PROCESS_INFO结构体数组的指针
        DWORD  *pCount			// 得到进程数
    );					// 成功返回非0 失败返回0
    

以下是 **WTS_PROCESS_INFO_EX** 结构体定义，这里用不到 **WTS_PROCESS_INFO** 不讲解

    
    
    typedef struct _WTS_PROCESS_INFO_EX {
      DWORD         SessionId;			// 进程会话
      DWORD         ProcessId;			// 进程PID
      LPSTR         pProcessName;		        // 进程名
      PSID          pUserSid;			// SID
      DWORD         NumberOfThreads;	                // 线程数
      DWORD         HandleCount;		        // 句柄数
      DWORD         PagefileUsage;		        // 页交换文件使用大小
      DWORD         PeakPagefileUsage;	        // 历史页交换文件使用
      DWORD         WorkingSetSize;		        // 工作集大小
      DWORD         PeakWorkingSetSize;	        // 峰值工作集大小
      LARGE_INTEGER UserTime;			// 进程在用户模式下运行时间
      LARGE_INTEGER KernelTime;			// 进程在内核模式下运行时间
    } WTS_PROCESS_INFO_EX, *PWTS_PROCESS_INFO_EX;
    

释放内存函数 **WTSFreeMemoryEx** ，最后还要将指针设置成NULL

    
    
    BOOL WTSFreeMemoryEx(
    	WTS_TYPE_CLASS WTSTypeClass,	// 枚举类型 值为WTSTypeProcessInfoLevel1 代表释放WTS_PROCESS_INFO_EX指针
    	PVOID          pMemory,		// 释放的指针
    	ULONG          NumberOfEntries	// 释放的数量
    );					// 成功返回非0 失败返回0
    

示例

    
    
    #include <stdio.h>
    #include <windows.h>
    #include <WtsApi32.h>
    #include <sddl.h>
    #pragma comment(lib,"Wtsapi32.lib")
    
    int main()
    {
        DWORD level = 1;
        // 保存进程信息
        PWTS_PROCESS_INFO_EX processList = NULL;
        // 进程数
        DWORD processCnt = 0;
        BOOL bRet = FALSE;
    	
        // 查询进程
        bRet = WTSEnumerateProcessesEx(WTS_CURRENT_SERVER_HANDLE, &level, WTS_ANY_SESSION, (LPTSTR*)&processList, &processCnt);
        if (!bRet)
        {
            printf("error get process\n");
            return 0;
        }
    
        printf("Processes Found: %d\n\n", processCnt);
        printf("#\tPID\tHandles\tThreads\tProcess Name\t\n\n");
    
    	// 保存结构体指针
        PWTS_PROCESS_INFO_EX tempList = processList;
        // 输出进程信息
        for (DWORD i = 0; i < processCnt; i++)
        {
            printf("%d\t", i + 1);
            printf("%d\t", tempList->ProcessId);
            printf("%d\t", tempList->HandleCount);
            printf("%d\t", tempList->NumberOfThreads);
            printf("%ws\t", tempList->pProcessName);
            printf("\n");
            // 移到下一个进程
            tempList++;
        }
    
        // 释放内存
        bRet = WTSFreeMemoryEx(WTSTypeProcessInfoLevel1, processList, processCnt);
        if (!bRet)
        {
            printf("error free memory\n");
            return 0;
        }
        processList = NULL;
        return 0;
    }
    

运行结果  
![image](https://image.3001.net/images/20220216/1645010425_620cddf9648ec229872fe.jpg!small)

### 获取sid

这里我们要打印SID，如果直接`printf("%d\t", tempList->pUserSid);`是不行的。要用到将SID转换成字符串的函数
**ConvertSidToStringSid** ，所在头文件 **sddl.h**

    
    
    BOOL ConvertSidToStringSid(
        PSID  Sid,		// Sid
        LPWSTR *StringSid    // 接收SID字符串指针
    );		        // 成功返回非0 失败返回0
    

示例

    
    
    // sid字符串
    LPWSTR stringSID = NULL;
    bRet = ConvertSidToStringSid(tempList->pUserSid, &stringSID);
    
    if (!bRet)
    {
        printf("error sid\t");
    }
    else
    {
        printf("%ws\t", stringSID);
        // 释放返回的缓冲区
        LocalFree((HLOCAL)stringSID);
    }
    

### 获取域名\用户名

用到查询函数为 **LookupAccountSid**

    
    
    BOOL LookupAccountSid(
        LPCSTR        lpSystemName,		    // 本地填NULL
        PSID          Sid,			    // SID
        LPSTR         Name,			    // 接收用户名
        LPDWORD       cchName,		    // 用户名缓冲区大小
        LPSTR         ReferencedDomainName,	    // 接收域名
        LPDWORD       cchReferencedDomainName,    // 域名缓冲区大小
        PSID_NAME_USE peUse			    // 指向SID_NAME_USE结构体指针
    );					    // 成功返回非0 失败返回0
    

结合前面的获取sid的代码

    
    
    #include <stdio.h>
    #include <windows.h>
    #include <WtsApi32.h>
    #include <sddl.h>
    #pragma comment(lib,"Wtsapi32.lib")
    
    // 获取SID
    void GetSID(PSID userSid)
    {
    	LPWSTR stringSID = NULL;
    
    	// 成功获取
    	if (ConvertSidToStringSid(userSid, &stringSID))
    	{
    		printf("%ws\t", stringSID);
    		// 释放返回的缓冲区
    		LocalFree((HLOCAL)stringSID);
    		return;
    	}
    
    	printf("-\t");
    }
    
    // 获取域名\用户名
    void GetAccount(PSID userSid)
    {
    	// 用户名
    	TCHAR userName[255];
    	DWORD bufferLen = 255;
    	// 域名
    	TCHAR domainName[255];
    	DWORD domainNameBufferLen = 255;
    	SID_NAME_USE peUse;
    
    	// 成功获取
    	if (LookupAccountSid(NULL, userSid, userName, &bufferLen, domainName, &domainNameBufferLen, &peUse))
    	{
    		printf("%ws\\%ws\t", domainName, userName);
    		return;
    	}
    	printf("-\t");
    }
    
    int main()
    {
    	DWORD level = 1;
    	// 保存进程信息
    	PWTS_PROCESS_INFO_EX processList = NULL;
    	// 进程数
    	DWORD processCnt = 0;
    	BOOL bRet = FALSE;
    
    	bRet = WTSEnumerateProcessesEx(WTS_CURRENT_SERVER_HANDLE, &level, WTS_ANY_SESSION, (LPTSTR*)&processList, &processCnt);
    
    	// 查询进程失败
    	if (!bRet)
    	{
    		printf("error get process\n");
    		return 0;
    	}
    
    	printf("Processes Found: %d\n\n", processCnt);
    	printf("#\tPID\tHandles\tThreads\tProcess Name\tSID\tAccount\t\n\n");
    
    
    	PWTS_PROCESS_INFO_EX tempList = processList;
    	// 输出进程信息
    	for (DWORD i = 0; i < processCnt; i++)
    	{
    		printf("%d\t", i + 1);
    		printf("%d\t", tempList->ProcessId);
    		printf("%d\t", tempList->HandleCount);
    		printf("%d\t", tempList->NumberOfThreads);
    		printf("%ws\t", tempList->pProcessName);
    
    		// 获取SID
    		GetSID(tempList->pUserSid);
    		// 获取域名\用户名
    		GetAccount(tempList->pUserSid);
    
    		printf("\n");
    		// 移到下一个进程
    		tempList++;
    	}
    
    	// 释放内存
    	bRet = WTSFreeMemoryEx(WTSTypeProcessInfoLevel1, processList, processCnt);
    	if (!bRet)
    	{
    		printf("error free memory\n");
    		return 0;
    	}
    
    	processList = NULL;
    	return 0;
    }
    

使用管理员运行后的结果  
![image](https://image.3001.net/images/20220216/1645010455_620cde178a29b149dc4c9.jpg!small)

### 进程提权

可看到csrss.exe fontdrvhost.exe 等等程序都没有获取到对应的信息，很明显是没有对应的权限。这时就需要提升自己进程到系统权限。

windows的每个用户登录系统后，系统会产生一个访问令牌（access
token），其中关联了当前用户的权限信息，用户登录后创建的每一个进程都含有用户access
token的拷贝，当进程试图执行某些需要特殊权限的操作或是访问受保护的内核对象时，系统会检查其acess
token中的权限信息以决定是否授权操作。Administrator组成员的access
token中会含有一些可以执行系统级操作的特权（privileges）
，如终止任意进程、关闭/重启系统、加载设备驱动和更改系统时间等，不过这些特权默认是被禁用的，当Administrator组成员创建的进程中包含一些需要特权的操作时，进程必须首先打开这些禁用的特权以提升自己的权限，否则系统将拒绝进程的操作。注意，非Administrator组成员创建的进程无法提升自身的权限，因此下面提到的进程均指Administrator组成员创建的进程。（命令行输入net
user可查看或net user 具体用户名称）

我们的程序只需要启用调试权限(SeDebugPrivilege)，就可以调试其他程序

使用[process explorer](https://docs.microsoft.com/zh-cn/sysinternals/downloads/process-explorer)查看我们写的程序拥有的权限，可看到SeDebugPrivilege未启用  
![image](https://image.3001.net/images/20220216/1645010476_620cde2ca96cbb4f64cbf.jpg!small)  
首先要获取到一个进程的访问令牌，函数为 **OpenProcessToken**

    
    
    BOOL OpenProcessToken(
        HANDLE  ProcessHandle,	// 进程句柄
        DWORD   DesiredAccess,	// 令牌的请求类型
        PHANDLE TokenHandle		// 返回令牌句柄
    );				// 成功返回非0 失败返回0
    

然后取得特权的LUID值。查询或更改特权的API需要LUID来引用相应的特权，LUID表示local unique
identifier，它是一个64位值，在当前系统中是唯一的。为了提升进程权限到指定的特权，我们必须先找到该特权对应的LUID。使用
**LookupPrivilegeValue** 函数

    
    
    BOOL LookupPrivilegeValue(
        LPCSTR lpSystemName,	    // 系统名称 本地填NULL
        LPCSTR lpName,	    // 权限名称
        PLUID  lpLuid	    // 返回LUID标识
    );			    // 成功返回非0 失败返回0
    

最后使用 **AdjustTokenPrivileges** ，来修改令牌权限

    
    
    BOOL AdjustTokenPrivileges(
    	HANDLE            TokenHandle,			// 令牌句柄
    	BOOL              DisableAllPrivileges,	        // 是否禁用令牌所有权限
    	PTOKEN_PRIVILEGES NewState,			// 指向TOKEN_PRIVILEGES结构的指针
    	DWORD             BufferLength,			// 指向PreviousState缓冲区大小 设为0即可
    	PTOKEN_PRIVILEGES PreviousState,		        // 存放修改前的TOKEN_PRIVILEGES结构信息 设为NULL即可
    	PDWORD            ReturnLength			// 实际PRIVILEGES NewState结构返回的大小 设为NULL即可
    );							// 成功返回非0 失败返回0
    

这里先看 **TOKEN_PRIVILEGES** 结构体定义

    
    
    typedef struct _TOKEN_PRIVILEGES {
      DWORD               PrivilegeCount;		    // 数组元素个数
      LUID_AND_ATTRIBUTES Privileges[ANYSIZE_ARRAY];	    // 指向LUID_AND_ATTRIBUTES结构体
    } TOKEN_PRIVILEGES, *PTOKEN_PRIVILEGES;
    

再来查看 **LUID_AND_ATTRIBUTES** 结构体定义

    
    
    typedef struct _LUID_AND_ATTRIBUTES {
      LUID  Luid;			// 指定一个LUID值
      DWORD Attributes;		// 特权属性
    } LUID_AND_ATTRIBUTES, *PLUID_AND_ATTRIBUTES;
    

特权属性Attributes有以下值

    
    
    SE_PRIVILEGE_ENABLED 			// 使特权有效
    SE_PRIVILEGE_ENABLED_BY_DEFAULT           // 使特权默认有效
    SE_PRIVILEGE_REMOVED 			// 移除该特权
    SE_PRIVILEGE_USED_FOR_ACCESS 	        // 取得对象或服务的访问权
    

示例

    
    
    #include <stdio.h>
    #include <windows.h>
    #include <WtsApi32.h>
    #include <sddl.h>
    #pragma comment(lib,"Wtsapi32.lib")
    
    // 获取SID
    void GetSID(PSID userSid)
    {
    	LPWSTR stringSID = NULL;
    
    	// 成功获取
    	if (ConvertSidToStringSid(userSid, &stringSID))
    	{
    		printf("%ws\t", stringSID);
    		// 释放返回的缓冲区
    		LocalFree((HLOCAL)stringSID);
    		return;
    	}
    
    	printf("-\t");
    }
    
    // 获取域名\用户名
    void GetAccount(PSID userSid)
    {
    	// 用户名
    	TCHAR userName[255];
    	DWORD bufferLen = 255;
    	// 域名
    	TCHAR domainName[255];
    	DWORD domainNameBufferLen = 255;
    	SID_NAME_USE peUse;
    
    	// 成功获取
    	if (LookupAccountSid(NULL, userSid, userName, &bufferLen, domainName, &domainNameBufferLen, &peUse))
    	{
    		printf("%ws\\%ws\t", domainName, userName);
    		return;
    	}
    	printf("-\t");
    }
    
    // 启用调试权限
    BOOL EnableDebugAbility()
    {
    	// 令牌句柄
    	HANDLE hProcessToken = NULL;
    	// 1.打开进程访问令牌
    	if (!OpenProcessToken(GetCurrentProcess(), TOKEN_ADJUST_PRIVILEGES, &hProcessToken))
    	{
    		printf("error open process token\n");
    		return FALSE;
    	}
    
    	// 2.取得SeDebugPrivilege特权的LUID值
    	LUID luid;
    	if (!LookupPrivilegeValue(NULL, SE_DEBUG_NAME, &luid))
    	{
    		printf("error lookup value\n");
    		return FALSE;
    	}
    	
    	// 3.调整访问令牌特权
    	TOKEN_PRIVILEGES token;
    	token.PrivilegeCount = 1;
    	token.Privileges[0].Luid = luid;
    	// 使特权有效
    	token.Privileges[0].Attributes = SE_PRIVILEGE_ENABLED;
    	
    	if (!AdjustTokenPrivileges(hProcessToken, FALSE, &token, 0, NULL, NULL))
    	{
    		printf("error adjust token\n");
    		return FALSE;
    	}
    	
    	CloseHandle(hProcessToken);
    	return TRUE;
    	
    }
    
    int main()
    {
    	// 提权失败
    	if (!EnableDebugAbility()) return 0;
    
    	DWORD level = 1;
    	// 保存进程信息
    	PWTS_PROCESS_INFO_EX processList = NULL;
    	// 进程数
    	DWORD processCnt = 0;
    	BOOL bRet = FALSE;
    
    	bRet = WTSEnumerateProcessesEx(WTS_CURRENT_SERVER_HANDLE, &level, WTS_ANY_SESSION, (LPTSTR*)&processList, &processCnt);
    
    	// 查询进程失败
    	if (!bRet)
    	{
    		printf("error get process\n");
    		return 0;
    	}
    
    	printf("Processes Found: %d\n\n", processCnt);
    	printf("#\tPID\tHandles\tThreads\tProcess Name\tSID\tAccount\t\n\n");
    
    	// 保存结构体指针
    	PWTS_PROCESS_INFO_EX tempList = processList;
    
    	// 输出进程信息
    	for (DWORD i = 0; i < processCnt; i++)
    	{
    		printf("%d\t", i + 1);
    		printf("%d\t", tempList->ProcessId);
    		printf("%d\t", tempList->HandleCount);
    		printf("%d\t", tempList->NumberOfThreads);
    		printf("%ws\t", tempList->pProcessName);
    
    		// 获取SID
    		GetSID(tempList->pUserSid);
    		// 获取域名\用户名
    		GetAccount(tempList->pUserSid);
    
    		printf("\n");
    		// 移到下一个进程
    		tempList++;
    	}
    
    	// 释放内存
    	bRet = WTSFreeMemoryEx(WTSTypeProcessInfoLevel1, processList, processCnt);
    	if (!bRet)
    	{
    		printf("error free memory\n");
    		return 0;
    	}
    
    	processList = NULL;
    	return 0;
    }
    

成功获取所有进程信息  
![image](https://image.3001.net/images/20220216/1645010501_620cde452619a472aaef9.jpg!small)  
查看SeDebugPrivilege也成功启用  
![image](https://image.3001.net/images/20220216/1645010512_620cde506675da4d6d432.jpg!small)

### 参考链接

[Windows
用户、认证和对象安全](https://blog.csdn.net/chenyonken/article/details/78290810?locationNum=7&fps=1)  
[windows进程提权(C语言实现)](https://www.jianshu.com/p/c0d48a675e55)  
[Windows API
Exploitation](https://www.youtube.com/watch?v=uPDIlJehABc&list=PLn9dWu8nAtkQgXB92sRrTgZt2B6qSolx4&index=4)

