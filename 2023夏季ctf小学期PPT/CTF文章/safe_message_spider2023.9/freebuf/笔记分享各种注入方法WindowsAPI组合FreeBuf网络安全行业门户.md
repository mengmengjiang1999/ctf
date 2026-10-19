整理笔记时发现之前留下的资料，抛砖引玉，分享给大家。

常见注入方法| OpenProcess  
VirtualAllocEx  
WriteProcessMemory  
CreateRemoteThread|  
---|---|---  
DLL注入| LoadLibrary/LoadLibraryEx  
GetProcAddress  
SetWindowsHookEx| 钩子注入  
APC注入| CreateToolhelp32Snapshot  
Process32First  
Thread32First  
Thread32Next  
Process32Next  
OpenProcess  
VirtualAllocEx  
WriteProcessMemory  
QueueUserAPC/NtQueueApcThread  
VirtualFreeEx  
CloseHandle| 异步过程调用中断  
Atom Bombing注入| CreateToolhelp32Snapshot  
Thread32First  
Thread32Next,  
OpenThread  
CreateEvent  
DuplicateHandle  
NtQueueApcThread  
QueueUserAPC  
GetModuleHandle  
GetProcAddress  
SetEvent  
GetCurrentProcess  
SleepEx  
WaitForMultipleObjectsEx  
MsgWaitForMultipleObjectsEx  
CloseHandle| 据说可以绕过所有Windows AV查杀机制  
ALPC注入| NtQuerySystemlnformation  
NtDuplicateObject/ZwDuplicateObject  
GetCurrentProcess  
NtQueryObject  
NtClose  
RtllnitUnicodeString  
NtConnectPort  
VirtualAllocEx  
WriteProcessMemory  
CopyMemory  
ReadProcessMemory  
VirtualFreeEx  
VirtualQueryEx  
GetMappedFileName,  
OpenProcess  
CloseHandle  
GetSystemlnfo| Advanced/Asynchronous Local Procedure Call  
LOCKPOS| CreateFileMappingW  
MapViewOfFile  
RtlAllocateHeap  
NtCreateSection  
NtMapViewOfSection  
NtCreateThreadEx| 与僵尸网络Flokibot使用类似的注入技术  
Hollowing注入| CreateProcess  
NtQueryProcesslnformation  
ReadProcessMemory  
GetModuleHandle  
GetProcAddress  
ZwUnmapViewOfSection/NtUnmapViewOfSection  
VirtualAllocEx  
WriteProcessMemory  
VirtualProtectEx  
SetThreadContext  
ResumeThread| 进程替换和RunPE，见封装工具:RISCyPacker  
DOPPELGANGING| CreateFileTransacted  
WriteFlle  
NtCreateSection  
RollbackTransaction  
NtCreateProcessEx  
RtICreateProcessParametersEx  
VirtualAllocEx  
WriteProcessMemory  
NtCreateThreadEx  
NtResumeThread|
类似Hollowing,参考:https://www.blackhat.com/docs/eu-17/materials/eu-17-Liberman-Lost-In-Transaction-Process-Doppelganging.pdf  
REFLECTIVE反射注入| CreateFileA  
HeapAlloc  
OpenProcessToken  
OpenProcess  
VirtualAlloc  
GetProcAddress  
LoadRemoteLibraryR/LoadLibrary  
HeapFree  
CloseHandle| 也可通过封装ReflectiverLoader实现  
线程执行劫持| RtlAdjustPrivilege  
OpenProcess  
CreateToolhelp32Snapshot  
Thread32First  
Thread32Next  
CloseHandle  
VirtualAllocEx  
OpenThread  
VirtualFree/VirtualFreeEx  
SuspendThread  
GetThreadContext  
VirtualAlloc  
WriteProcessMemory  
SetThreadContext  
ResumeThread|  
  
其实现方法可在github上搜索源码，还有一些常见的方法(如注册表Appinit_DLL, AppCertDlls,
IFEO）和不常见的hook方法(如EWMI)，后期再整理...

