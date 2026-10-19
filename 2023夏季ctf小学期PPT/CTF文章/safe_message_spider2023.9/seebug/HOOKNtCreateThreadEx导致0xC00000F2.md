作者：Leeqwind  
作者博客：<https://xiaodaozhi.com/kernel/31.html>

近期在研究和开发基于虚拟化的虚拟 HOOK 技术。在 Windows 7 x64 环境开发实测期间，发现针对 `NtCreateThreadEx` 函数的
HOOK 存在问题：该函数大部分情况下变得只返回 `0xC00000F2` (`STATUS_INVALID_PARAMETER_4`) 第 4
个参数无效的状态码。这导致系统出现很多问题，大部分的新线程都无法成功创建。为了解决这个问题，在这篇文章中对问题进行追溯，查找到底是哪里导致的。

经过追踪：发现位于在 `NtAllocateVirtualMemory` 中如下位置赋值了提到的错误状态码：

    
    
    kd> p
    nt! ?? ::NNGAKEGL::`string'+0x47703:
    fffff800`041e171e b8f20000c0      mov     eax,0C00000F2h

调用栈如下：

    
    
    kd> k
     # Child-SP          RetAddr           Call Site
    00 fffff880`028e7470 fffff800`03e918d3 nt! ?? ::NNGAKEGL::`string'+0x47703
    01 fffff880`028e7610 fffff800`03e8de70 nt!KiSystemServiceCopyEnd+0x13
    02 fffff880`028e7818 fffff800`04180a63 nt!KiServiceLinkage
    03 fffff880`028e7820 fffff800`03e918d3 nt!NtSetInformationProcess+0x4c6
    04 fffff880`028e7b70 fffff800`03e8de70 nt!KiSystemServiceCopyEnd+0x13
    05 fffff880`028e7d08 fffff800`04180226 nt!KiServiceLinkage
    06 fffff880`028e7d10 fffff800`0417e84d nt!RtlCreateUserStack+0x122
    07 fffff880`028e7e00 fffff800`0417e47e nt!PspAllocateThread+0x299
    08 fffff880`028e8020 fffff800`04182385 nt!PspCreateThread+0x1d2
    09 fffff880`028e82a0 fffff880`03ea22ee nt!NtCreateThreadEx+0x25d
    0a fffff880`028e89f0 fffff800`03e918d3 DetectModule!Handle_SSDT_NtCreateThreadEx+0x9e 
    0b fffff880`028e8a70 00000000`76e51d9a nt!KiSystemServiceCopyEnd+0x13
    0c 00000000`0366af18 000007fe`fd01b4a3 ntdll!NtCreateThreadEx+0xa
    0d 00000000`0366af20 00000000`76bf65b6 KernelBase!CreateRemoteThreadEx+0x163
    0e 00000000`0366b3e0 000007fe`f57f7186 kernel32!CreateThreadStub+0x36
    0f 00000000`0366b430 00000000`00000000 0x000007fe`f57f7186

具体的调用链：

    
    
    NtCreateThreadEx > PspCreateThread > PspAllocateThread > RtlCreateUserStack > ZwSetInformationProcess > NtSetInformationProcess > ZwAllocateVirtualMemory > NtAllocateVirtualMemory

最终在 NtAllocateVirtualMemory 函数中因其第4个参数的问题导致了 0xC00000F2 的状态码。报错误码的指令前面的 10
条执行指令如下：

    
    
    eb05            jmp     nt!NtAllocateVirtualMemory+0x119 (fffff800`04189da9)
    488b056092f3ff  mov     rax,qword ptr [nt!MmHighestUserAddress (fffff800`040c3010)]
    48050000ffff    add     rax,0FFFFFFFFFFFF0000h
    483bd8          cmp     rbx,rax
    0f8755790500    ja      nt! ?? ::NNGAKEGL::`string'+0x476f9 (fffff800`041e1714)
    488b054a92f3ff  mov     rax,qword ptr [nt!MmHighestUserAddress (fffff800`040c3010)]
    482bc3          sub     rax,rbx
    482dffff0000    sub     rax,0FFFFh
    493bc7          cmp     rax,r15
    0f8246790500    jb      nt! ?? ::NNGAKEGL::`string'+0x47703 (fffff800`041e171e)
    b8f20000c0      mov     eax,0C00000F2h

通过 IDA Hex 插件查看：

    
    
    if ( v147 > MmHighestUserAddress - 0x10000 )
        return 0xC00000F0i64;
    if ( MmHighestUserAddress - v147 - 0xFFFF < v19 )
        return 0xC00000F2i64;

在上面的第二个 if 判断命中条件，返回了 0xC00000F2 状态码。

在 Windbg 中捕获的该函数的指令执行路径如下，在分析时由于篇幅关系，在下面的指令片段中均把机器码左侧 64 位地址的高 32 位隐去：

    
    
    nt!NtAllocateVirtualMemory:
    `04189c90 4c894c2420      mov     qword ptr [rsp+20h],r9
    `04189c95 4c89442418      mov     qword ptr [rsp+18h],r8
    `04189c9a 4889542410      mov     qword ptr [rsp+10h],rdx
    `04189c9f 48894c2408      mov     qword ptr [rsp+8],rcx
    `04189ca4 53              push    rbx
    `04189ca5 56              push    rsi
    `04189ca6 57              push    rdi
    `04189ca7 4154            push    r12
    `04189ca9 4155            push    r13
    `04189cab 4156            push    r14
    `04189cad 4157            push    r15
    `04189caf 4881ec60010000  sub     rsp,160h
    `04189cb6 4d8bd1          mov     r10,r9
    `04189cb9 498bc0          mov     rax,r8
    `04189cbc 4c8bca          mov     r9,rdx
    `04189cbf 4c8be9          mov     r13,rcx
    `04189cc2 4d85c0          test    r8,r8
    `04189cc5 0f8523080000    jne     nt!NtAllocateVirtualMemory+0x85e (`0418a4ee)
    `0418a4ee 4883f820        cmp     rax,20h
    `0418a4f2 0f8223710500    jb      nt! ?? ::NNGAKEGL::`string'+0x475f0 (`041e161b)
    `0418a4f8 488bc8          mov     rcx,rax
    `0418a4fb e82002ceff      call    nt!RtlFindMostSignificantBit (`03e6a720)
    `0418a500 440fbec0        movsx   r8d,al
    `0418a504 b83f000000      mov     eax,3Fh
    `0418a509 412bc0          sub     eax,r8d
    `0418a50c 4898            cdqe
    `0418a50e 48898424b0010000 mov     qword ptr [rsp+1B0h],rax
    `0418a516 4883f835        cmp     rax,35h
    `0418a51a 0f86abf7ffff    jbe     nt!NtAllocateVirtualMemory+0x3b (`04189ccb)
    `04189ccb 4533c0          xor     r8d,r8d
    `04189cce 418bf8          mov     edi,r8d
    `04189cd1 654c8b242588010000 mov   r12,qword ptr gs:[188h]
    `04189cda 4d8b5c2470      mov     r11,qword ptr [r12+70h]
    `04189cdf 4c895c2478      mov     qword ptr [rsp+78h],r11
    `04189ce4 8bb424c0010000  mov     esi,dword ptr [rsp+1C0h]
    `04189ceb 448bf6          mov     r14d,esi
    `04189cee 4183e67f        and     r14d,7Fh
    `04189cf2 0fb7050f93f3ff  movzx   eax,word ptr [nt!KeNumberNodes (`040c3008)]
    `04189cf9 443bf0          cmp     r14d,eax
    `04189cfc 0f8734790500    ja      nt! ?? ::NNGAKEGL::`string'+0x4760b (`041e1636)
    `04189d02 83e680          and     esi,0FFFFFF80h
    `04189d05 f7c6ffcf07df    test    esi,0DF07CFFFh
    `04189d0b 0f852f790500    jne     nt! ?? ::NNGAKEGL::`string'+0x47615 (`041e1640)
    `04189d11 f7c600300800    test    esi,83000h
    `04189d17 0f842d790500    je      nt! ?? ::NNGAKEGL::`string'+0x4761f (`041e164a)
    `04189d1d f7c60000e820    test    esi,20E80000h
    `04189d23 0f85e2090000    jne     nt!NtAllocateVirtualMemory+0xa7b (`0418a70b)
    `04189d29 8b8424c8010000  mov     eax,dword ptr [rsp+1C8h]
    `04189d30 89442460        mov     dword ptr [rsp+60h],eax
    `04189d34 8bc8            mov     ecx,eax
    `04189d36 e8c5bcd1ff      call    nt!MiMakeProtectionMask (`03ea5a00)
    `04189d3b 89442474        mov     dword ptr [rsp+74h],eax
    `04189d3f 83f8ff          cmp     eax,0FFFFFFFFh
    `04189d42 0f84c2790500    je      nt! ?? ::NNGAKEGL::`string'+0x476ef (`041e170a)
    `04189d48 410fb69424f6010000 movzx edx,byte ptr [r12+1F6h]
    `04189d51 88542470        mov     byte ptr [rsp+70h],dl
    `04189d55 84d2            test    dl,dl
    `04189d57 7436            je      nt!NtAllocateVirtualMemory+0xff (`04189d8f)
    `04189d8f 498b19          mov     rbx,qword ptr [r9]
    `04189d92 48899c24a0000000 mov     qword ptr [rsp+0A0h],rbx
    `04189d9a 4d8b3a          mov     r15,qword ptr [r10]
    `04189d9d 4c897c2468      mov     qword ptr [rsp+68h],r15
    `04189da2 eb05            jmp     nt!NtAllocateVirtualMemory+0x119 (`04189da9)
    `04189da9 488b056092f3ff  mov     rax,qword ptr [nt!MmHighestUserAddress (`040c3010)]
    `04189db0 48050000ffff    add     rax,0FFFFFFFFFFFF0000h
    `04189db6 483bd8          cmp     rbx,rax
    `04189db9 0f8755790500    ja      nt! ?? ::NNGAKEGL::`string'+0x476f9 (`041e1714)
    `04189dbf 488b054a92f3ff  mov     rax,qword ptr [nt!MmHighestUserAddress (`040c3010)]
    `04189dc6 482bc3          sub     rax,rbx
    `04189dc9 482dffff0000    sub     rax,0FFFFh
    `04189dcf 493bc7          cmp     rax,r15
    `04189dd2 0f8246790500    jb      nt! ?? ::NNGAKEGL::`string'+0x47703 (`041e171e)
    `041e171e b8f20000c0      mov     eax,0C00000F2h

根据上面的指令执行路径可知，关键的寄存器是 r9 寄存器。但在函数稍开始位置将第二个参数寄存器 rdx 的值赋值给 r9 寄存器。

参数4：在赋值 r9 之前，函数将 r9 寄存器赋值给 r10 寄存器；在函数稍后位置将 r10 寄存器存储的值作为地址取指针长度的值赋值给 r15
寄存器，并且在最后作为 cmp 比较的依据之一，即代码中的 v19 变量。

参数2：在将 rdx 的值赋值 r9 寄存器之后，在稍后位置将 r9 寄存器的值作为地址取指针长度的值赋值 rbx 寄存器，并通过将
MmHighestUserAddress-rbx-0xFFFF 获得的值与前面的 r15 寄存器进行大小比较。

函数原型：

    
    
    NTSTATUS
    NTAPI
    NtAllocateVirtualMemory(
        IN     HANDLE      ProcessHandle,
        IN OUT PVOID      *BaseAddress,
        IN     ULONG_PTR   ZeroBits,
        IN OUT PSIZE_T     RegionSize,
        IN     ULONG       AllocationType,
        IN     ULONG       Protect
        );

MmHighestUserAddress 初值：

    
    
    mov     rax, 7FFFFFEFFFFh
    lea     rdx, aSafeboot_0 ; "SAFEBOOT:"
    mov     cs:MmHighestUserAddress, rax
    mov     rax, 7FFFFFF0000h
    mov     cs:MmUserProbeAddress, rax

如果前面相减得到的 rax 值小于 r15 值，那么报错。

    
    
    if ( MmHighestUserAddress - *BaseAddress - 0xFFFF < *RegionSize )
        return 0xC00000F2i64;

在报错指令位置下断点，截获到一次报错的上下文，判断的两个寄存器值如下：

    
    
    kd> r rax, r15
    rax=000007fffffe0000 r15=fffffa8000000000

显而易见地，问题出在 r15 寄存器的值，而 r15 寄存器的值是由 r10 寄存器存储的指针指向地址的值赋值的。

    
    
    kd> r r10
    r10=fffff880030f8918
    kd> dq fffff880030f8918 l1
    fffff880`030f8918  fffffa80`00000000

显而易见地这是一个非常离谱的值，通常此处通过 RegionSize 参数指向域的值确定分配虚拟内存的区域大小，而 0xfffffa8000000000
显然超过了正常用户地址空间的范围。

至于为什么会传入这样无效的值，继续向上探究：

    
    
    nt!NtSetInformationProcess:
    `041d659c fff3            push    rbx
    kd> r rdx
    rdx=0000000000000029
    kd> p
    nt!NtSetInformationProcess+0x2:
    `041d659e 56              push    rsi
    `041d659f 57              push    rdi
    `041d65a0 4154            push    r12
    `041d65a2 4155            push    r13
    `041d65a4 4156            push    r14
    `041d65a6 4157            push    r15
    `041d65a8 4881ec10030000  sub     rsp,310h
    `041d65af 488b052a44e8ff  mov     rax,qword ptr [nt!_security_cookie (`0405a9e0)]
    `041d65b6 4833c4          xor     rax,rsp
    `041d65b9 4889842400030000 mov     qword ptr [rsp+300h],rax
    `041d65c1 458bf9          mov     r15d,r9d
    `041d65c4 4d8be0          mov     r12,r8
    `041d65c7 4c8bd1          mov     r10,rcx
    `041d65ca 48894c2458      mov     qword ptr [rsp+58h],rcx
    `041d65cf 4c898424b0000000 mov     qword ptr [rsp+0B0h],r8
    `041d65d7 44897c2474      mov     dword ptr [rsp+74h],r15d
    `041d65dc 654c8b342588010000 mov   r14,qword ptr gs:[188h] ;; Get _KTHREAD pointer
    `041d65e5 4c89b42480000000 mov     qword ptr [rsp+80h],r14
    `041d65ed 418abef6010000  mov     dil,byte ptr [r14+1F6h] ;; PreviousMode
    `041d65f4 33f6            xor     esi,esi
    `041d65f6 403afe          cmp     dil,sil ;; PreviousMode == KernelMode
    `041d65f9 0f8461030000    je      nt!NtSetInformationProcess+0x3c3 (`041d6960)
    `041d6960 bb08000000      mov     ebx,8
    `041d6965 448d6bf9        lea     r13d,[rbx-7]
    `041d6969 e949fdffff      jmp     nt!NtSetInformationProcess+0x11a (`041d66b7)
    `041d66b7 83fa17          cmp     edx,17h
    `041d66ba 0f8f76010000    jg      nt!NtSetInformationProcess+0x299 (`041d6836)
    `041d6836 83fa27          cmp     edx,27h
    `041d6839 0f8e2f010000    jle     nt!NtSetInformationProcess+0x3d1 (`041d696e)
    `041d683f 83ea28          sub     edx,28h
    `041d6842 0f84c95f0600    je      nt! ?? ::NNGAKEGL::`string'+0x4ce75 (`0423c811)
    `041d6848 412bd5          sub     edx,r13d ; r13d=029h
    `041d684b 0f8573030000    jne     nt!NtSetInformationProcess+0x627 (`041d6bc4)
    `041d6851 4883cbff        or      rbx,0FFFFFFFFFFFFFFFFh
    `041d6855 4c3bd3          cmp     r10,rbx
    `041d6858 0f850b5f0600    jne     nt! ?? ::NNGAKEGL::`string'+0x4cdbf (`0423c769)
    `041d685e 4183ff28        cmp     r15d,28h
    `041d6862 0f85155f0600    jne     nt! ?? ::NNGAKEGL::`string'+0x4cdd3 (`0423c77d)
    `041d6868 403afe          cmp     dil,sil
    `041d686b 0f85d8030000    jne     nt!NtSetInformationProcess+0x6ac (`041d6c49)
    `041d6871 4c8bfe          mov     r15,rsi
    `041d6874 458b3424        mov     r14d,dword ptr [r12]
    `041d6878 4183fe40        cmp     r14d,40h
    `041d687c 0f87f15e0600    ja      nt! ?? ::NNGAKEGL::`string'+0x4cdc9 (`0423c773)
    `041d6882 418b44240c      mov     eax,dword ptr [r12+0Ch]
    `041d6887 410b442408      or      eax,dword ptr [r12+8]
    `041d688c 410b442404      or      eax,dword ptr [r12+4]
    `041d6891 0f85dc5e0600    jne     nt! ?? ::NNGAKEGL::`string'+0x4cdc9 (`0423c773)
    `041d6897 4983c410        add     r12,10h
    `041d689b 49393424        cmp     qword ptr [r12],rsi
    kd> r r12
    r12=fffff88003aefd98
    kd> p
    `041d689f 0f84215f0600    je      nt! ?? ::NNGAKEGL::`string'+0x4ce23 (`0423c7c6)
    `041d68a5 49ba1400000080f7ffff mov r10,0FFFFF78000000014h
    `041d68af 4d8b12          mov     r10,qword ptr [r10]
    `041d68b2 0f31            rdtsc
    `041d68b4 48c1e220        shl     rdx,20h
    `041d68b8 480bc2          or      rax,rdx
    `041d68bb 4c03d0          add     r10,rax
    `041d68be 4183e21f        and     r10d,1Fh
    `041d68c2 4503d5          add     r10d,r13d
    `041d68c5 4d8b1c24        mov     r11,qword ptr [r12] ;; 从r12指向地址取值赋给r11
    `041d68c9 4c899c24f8000000 mov     qword ptr [rsp+0F8h],r11 ;; 为[rsp+0F8h]变量赋值
    `041d68d1 65488b042588010000 mov   rax,qword ptr gs:[188h]
    `041d68da 488b4870        mov     rcx,qword ptr [rax+70h]
    `041d68de 0fbaa13c04000011 bt      dword ptr [rcx+43Ch],11h
    `041d68e6 0f823e010000    jb      nt!NtSetInformationProcess+0x48d (`041d6a2a)
    `041d68ec 4d8b4c2408      mov     r9,qword ptr [r12+8]
    `041d68f1 4c3bce          cmp     r9,rsi
    `041d68f4 0f85d65e0600    jne     nt! ?? ::NNGAKEGL::`string'+0x4ce2d (`0423c7d0)
    `0423c7d0 4983f920        cmp     r9,20h
    `0423c7d4 7217            jb      nt! ?? ::NNGAKEGL::`string'+0x4ce51 (`0423c7ed)
    `0423c7d6 498bc9          mov     rcx,r9
    `0423c7d9 e8423fc8ff      call    nt!RtlFindMostSignificantBit (`03ec0720)
    `0423c7de 0fbec8          movsx   ecx,al
    `0423c7e1 b83f000000      mov     eax,3Fh
    `0423c7e6 2bc1            sub     eax,ecx
    `0423c7e8 4c63c8          movsxd  r9,eax
    `0423c7eb eb04            jmp     nt! ?? ::NNGAKEGL::`string'+0x4ce55 (`0423c7f1)
    `0423c7f1 4983f935        cmp     r9,35h
    `0423c7f5 0f8739a2f9ff    ja      nt!NtSetInformationProcess+0x497 (`041d6a34)
    `0423c7fb e9faa0f9ff      jmp     nt!NtSetInformationProcess+0x35d (`041d68fa)
    `041d68fa 4d8d6c2410      lea     r13,[r12+10h]
    `041d68ff 4c896c2420      mov     qword ptr [rsp+20h],r13
    `041d6904 4533c0          xor     r8d,r8d
    `041d6907 498bd3          mov     rdx,r11
    `041d690a 418bca          mov     ecx,r10d
    `041d690d e8863e0000      call    nt!MiScanUserAddressSpace (`041da798)
    `041d6912 8bc8            mov     ecx,eax
    `041d6914 3bc6            cmp     eax,esi
    `041d6916 7c28            jl      nt!NtSetInformationProcess+0x3a3 (`041d6940)
    `041d6940 3bce            cmp     ecx,esi
    `041d6942 0f8cec000000    jl      nt!NtSetInformationProcess+0x497 (`041d6a34)
    `041d6a34 498d542410      lea     rdx,[r12+10h]
    `041d6a39 488932          mov     qword ptr [rdx],rsi
    `041d6a3c 410fbaee0d      bts     r14d,0Dh
    `041d6a41 c744242804000000 mov     dword ptr [rsp+28h],4
    `041d6a49 4489742420      mov     dword ptr [rsp+20h],r14d
    `041d6a4e 4c8d8c24f8000000 lea     r9,[rsp+0F8h] ;; 取[rsp+0F8h]变量的地址给r9寄存器
    `041d6a56 4d8b442408      mov     r8,qword ptr [r12+8]
    `041d6a5b 488bcb          mov     rcx,rbx
    `041d6a5e e87da4d0ff      call    nt!ZwAllocateVirtualMemory (`03ee0ee0)
    kd> p
    nt!NtSetInformationProcess+0x4c6:
    `041d6a63 8bc8            mov     ecx,eax
    kd> r rax
    rax=00000000c00000f2
    kd> r rsp
    rsp=fffff88003aef820
    kd> dq rsp+0x0f8 l1
    fffff880`03aef918  fffff800`00000000
    kd> dq fffff88003aefd98 l1
    fffff880`03aefd98  fffff800`00000000

函数定义：

    
    
    NTSTATUS
    NTAPI
    NtSetInformationProcess (
        IN HANDLE           ProcessHandle,
        IN PROCESSINFOCLASS ProcessInformationClass,
        IN PVOID            ProcessInformation,
        IN ULONG            ProcessInformationLength
        );

其中第二个参数是定义设置进程信息的类型。根据上面的指令执行路径得知，这次调用传递给该函数的第二个参数值为0x29，根据 PROCESSINFOCLASS
定义：

    
    
    typedef enum _PROCESSINFOCLASS {
        ...
        ProcessThreadStackAllocation = 0x29, // 0x29, 41
        ...
    } PROCESSINFOCLASS;

进程信息类型为 0x29 时表示设置进程的线程栈分配信息。

在这次 NtSetInformationProcess 函数调用中，可以看到传入 ZwAllocateVirtualMemory
函数的第四个参数来自它自身第三个参数 r8 寄存器指向的结构体对象基址 +10 偏移的域值。

第三个参数是 ProcessInformation，指向一个由调用者分配的缓冲区，作为用于提供指定的进程信息类型所需的各种数据的结构。

在该函数调用初期查看这个缓冲区中的数据：

    
    
    kd> dq 0xfffff880`03aefd88
    fffff880`03aefd88  00000000`00000000 00000000`00000000
    fffff880`03aefd98  fffff880`00000000 00000000`00000000
    fffff880`03aefda8  00000000`00000000 00000000`00000000

可以确定的是上级函数传入 NtSetInformationProcess 的第三个参数时缓冲区中的数据就是这样的，就是说偏移为 +10h 位置的域其值为
0xFFFFF88000000000 这种异常的值。

所以此时继续向上探究。在 nt!RtlCreateUserStack 函数首地址下断点捕获其调用路径：

    
    
    nt!RtlCreateUserStack:
    `041cf104 4c89442418      mov     qword ptr [rsp+18h],r8
    `041cf109 4889542410      mov     qword ptr [rsp+10h],rdx
    `041cf10e 48894c2408      mov     qword ptr [rsp+8],rcx
    `041cf113 53              push    rbx
    `041cf114 56              push    rsi
    `041cf115 4154            push    r12
    `041cf117 4155            push    r13
    `041cf119 4156            push    r14
    `041cf11b 4157            push    r15
    `041cf11d 4881ecb8000000  sub     rsp,0B8h
    `041cf124 4d8be9          mov     r13,r9
    `041cf127 488bf2          mov     rsi,rdx
    `041cf12a 488bd9          mov     rbx,rcx
    `041cf12d 4d8bf9          mov     r15,r9
    `041cf130 49c1ef38        shr     r15,38h
    `041cf134 44887c2430      mov     byte ptr [rsp+30h],r15b
    `041cf139 48b8ffffffffffffff00 mov rax,0FFFFFFFFFFFFFFh
    `041cf143 4c23e8          and     r13,rax
    `041cf146 4c89ac2408010000 mov     qword ptr [rsp+108h],r13
    `041cf14e 4180ff40        cmp     r15b,40h
    `041cf152 0f8764060400    ja      nt! ?? ::NNGAKEGL::`string'+0x7020 (`0420f7bc)
    `041cf158 4b8d446d00      lea     rax,[r13+r13*2]
    `041cf15d 4889442460      mov     qword ptr [rsp+60h],rax
    `041cf162 65488b042588010000 mov   rax,qword ptr gs:[188h]
    `041cf16b 488b4870        mov     rcx,qword ptr [rax+70h]
    `041cf16f 4c8bb138030000  mov     r14,qword ptr [rcx+338h]
    `041cf176 4c89742458      mov     qword ptr [rsp+58h],r14
    `041cf17b 4885db          test    rbx,rbx
    `041cf17e 0f848b010000    je      nt!RtlCreateUserStack+0x20b (`041cf30f)
    `041cf184 4885d2          test    rdx,rdx
    `041cf187 0f8482010000    je      nt!RtlCreateUserStack+0x20b (`041cf30f)
    `041cf18d b800400000      mov     eax,4000h
    `041cf192 4885db          test    rbx,rbx
    `041cf195 480f44d8        cmove   rbx,rax
    `041cf199 483bde          cmp     rbx,rsi
    `041cf19c 0f832c060400    jae     nt! ?? ::NNGAKEGL::`string'+0x7032 (`0420f7ce)
    `0420f7ce 488db3ffff0f00  lea     rsi,[rbx+0FFFFFh]
    `0420f7d5 4881e60000f0ff  and     rsi,0FFFFFFFFFFF00000h
    `0420f7dc e9c1f9fbff      jmp     nt!RtlCreateUserStack+0x9e (`041cf1a2)
    `041cf1a2 498d4dff        lea     rcx,[r13-1]
    `041cf1a6 48f7d1          not     rcx
    `041cf1a9 4e8d642bff      lea     r12,[rbx+r13-1]
    `041cf1ae 4c23e1          and     r12,rcx
    `041cf1b1 4881c6ffff0000  add     rsi,0FFFFh
    `041cf1b8 4881e60000ffff  and     rsi,0FFFFFFFFFFFF0000h
    `041cf1bf 498b8618030000  mov     rax,qword ptr [r14+318h]
    `041cf1c6 48898424a0000000 mov     qword ptr [rsp+0A0h],rax
    `041cf1ce eb05            jmp     nt!RtlCreateUserStack+0xd1 (`041cf1d5)
    `041cf1d5 4885c0          test    rax,rax
    `041cf1d8 0f8503060400    jne     nt! ?? ::NNGAKEGL::`string'+0x7045 (`0420f7e1)
    `041cf1de 410fb6c7        movzx   eax,r15b
    `041cf1e2 89442478        mov     dword ptr [rsp+78h],eax
    `041cf1e6 8364247c00      and     dword ptr [rsp+7Ch],0
    `041cf1eb 83a4248400000000 and     dword ptr [rsp+84h],0
    `041cf1f3 83a4248000000000 and     dword ptr [rsp+80h],0
    `041cf1fb 4889b42488000000 mov     qword ptr [rsp+88h],rsi ; assign-> RegionSize
    `041cf203 4c89842490000000 mov     qword ptr [rsp+90h],r8
    `041cf20b 41b928000000    mov     r9d,28h
    `041cf211 4c8d442478      lea     r8,[rsp+78h]
    `041cf216 418d5101        lea     edx,[r9+1]
    `041cf21a 4983cfff        or      r15,0FFFFFFFFFFFFFFFFh
    `041cf21e 498bcf          mov     rcx,r15
    `041cf221 e83aadd0ff      call    nt!ZwSetInformationProcess (`03ed9f60)
    kd> r r8
    r8=fffff8800422bd88
    kd> dq [r8]
    fffff880`0422bd88  00000000`00000000 00000000`00000000
    fffff880`0422bd98  fffff880`00100000 00000000`00000000
    fffff880`0422bda8  00000000`00000384 00000000`00000000
    fffff880`0422bdb8  00000000`00000018 fffff880`0422bdd0
    kd> r
    rax=0000000000000000 rbx=fffff88000002000 rcx=ffffffffffffffff
    rdx=0000000000000029 rsi=fffff88000100000 rdi=0000000000000000
    rip=fffff800041cf221 rsp=fffff8800422bd10 rbp=fffffa8004170b30
     r8=fffff8800422bd88  r9=0000000000000028 r10=0000000000000001
    r11=fffff8800422bde0 r12=fffff88000002000 r13=0000000000001000
    r14=000007fffffd7000 r15=ffffffffffffffff
    iopl=0         nv up ei ng nz na po nc
    cs=0010  ss=0018  ds=002b  es=002b  fs=0053  gs=002b  efl=00000286

根据执行路径可知，传入给 ZwSetInformationProcess 的第三个参数指针指向的是位于 RtlCreateUserStack
栈区域的局部结构体变量。在将结构体地址赋值给 r8 寄存器之前，函数执行对结构体 6 个域赋值操作，其中需要关注的是第 5 个域，即在前面一直追寻的指示
RegionSize 的来源的域，这个域是通过 rsi 寄存器赋值的。

向上追溯，发现在 rsi 寄存器取 rbx+0xFFFFF 地址之后，再经过几次逻辑与运算：

    
    
    lea     rsi,[rbx+0FFFFFh]
    and     rsi,0FFFFFFFFFFF00000h
    add     rsi,0FFFFh
    and     rsi,0FFFFFFFFFFFF0000h

此时 rbx 的值是 0xFFFFF88000002000，而 rbx 是在函数执行开始时由 rcx 寄存器直接赋值的，而 rcx 寄存器是作为函数的第 1
个参数传入的。该函数原型如下：

    
    
    NTSTATUS
    NTAPI
    RtlCreateUserStack (
        _In_opt_ SIZE_T       CommittedStackSize,
        _In_opt_ SIZE_T       MaximumStackSize,
        _In_opt_ ULONG_PTR    ZeroBits,
        _In_     SIZE_T       PageSize,
        _In_     ULONG_PTR    ReserveAlignment,
        _Out_    PINITIAL_TEB InitialTeb
    );

其中第一个参数是 CommittedStackSize，作为栈的初始提交大小。显然地在这里传入该函数的这个参数就是不寻常的值。那么继续向上探究：

    
    
    nt!PspAllocateThread:
    `041cd5b4 488bc4          mov     rax,rsp
    `041cd5b7 4c894820        mov     qword ptr [rax+20h],r9
    `041cd5bb 44884018        mov     byte ptr [rax+18h],r8b
    `041cd5bf 48895010        mov     qword ptr [rax+10h],rdx
    `041cd5c3 48894808        mov     qword ptr [rax+8],rcx
    `041cd5c7 53              push    rbx
    `041cd5c8 56              push    rsi
    `041cd5c9 57              push    rdi
    `041cd5ca 4154            push    r12
    `041cd5cc 4155            push    r13
    `041cd5ce 4156            push    r14
    `041cd5d0 4157            push    r15
    `041cd5d2 4881ece0010000  sub     rsp,1E0h
    `041cd5d9 458ad0          mov     r10b,r8b
    `041cd5dc 4c8be9          mov     r13,rcx
    `041cd5df 33ff            xor     edi,edi
    `041cd5e1 48897c2470      mov     qword ptr [rsp+70h],rdi
    `041cd5e6 4c3bcf          cmp     r9,rdi
    `041cd5e9 740b            je      nt!PspAllocateThread+0x42 (`041cd5f6)
    `041cd5eb 410fba210f      bt      dword ptr [r9],0Fh
    `041cd5f0 0f823c0ff6ff    jb      nt! ?? ::NNGAKEGL::`string'+0x241f0 (`0412e532)
    `041cd5f6 4c8ba42460020000 mov     r12,qword ptr [rsp+260h]
    `041cd5fe 65488b042588010000 mov   rax,qword ptr gs:[188h]
    `041cd607 4889842498000000 mov     qword ptr [rsp+98h],rax
    `041cd60f 4c8b842478020000 mov     r8,qword ptr [rsp+278h]
    `041cd617 4189b878010000  mov     dword ptr [r8+178h],edi
    `041cd61e 4588907c010000  mov     byte ptr [r8+17Ch],r10b
    `041cd625 4c8bb42440020000 mov     r14,qword ptr [rsp+240h]
    `041cd62d 4c3bf7          cmp     r14,rdi
    `041cd630 0f848a060000    je      nt!PspAllocateThread+0x70b (`041cdcc0)
    `041cd636 483b0df349f4ff  cmp     rcx,qword ptr [nt!PsInitialSystemProcess (`04112030)]
    `041cd63d 0f841a0ff6ff    je      nt! ?? ::NNGAKEGL::`string'+0x2421f (`0412e55d)
    `041cd643 483bd7          cmp     rdx,rdi
    `041cd646 0f851a040000    jne     nt!PspAllocateThread+0x4b2 (`041cda66)
    `041cd64c 498b85c8010000  mov     rax,qword ptr [r13+1C8h]
    `041cd653 48f7d8          neg     rax
    `041cd656 1bf6            sbb     esi,esi
    `041cd658 83e658          and     esi,58h
    `041cd65b 41bf98040000    mov     r15d,498h
    `041cd661 4103f7          add     esi,r15d
    `041cd664 488d442458      lea     rax,[rsp+58h]
    `041cd669 4889442440      mov     qword ptr [rsp+40h],rax
    `041cd66e 89742438        mov     dword ptr [rsp+38h],esi
    `041cd672 897c2430        mov     dword ptr [rsp+30h],edi
    `041cd676 89742428        mov     dword ptr [rsp+28h],esi
    `041cd67a 48897c2420      mov     qword ptr [rsp+20h],rdi
    `041cd67f 458aca          mov     r9b,r10b
    `041cd682 4c8bc2          mov     r8,rdx
    `041cd685 488b15c449f4ff  mov     rdx,qword ptr [nt!PsThreadType (`04112050)]
    `041cd68c 418aca          mov     cl,r10b
    `041cd68f e84cd60000      call    nt!ObCreateObject (`041dace0)
    `041cd694 8bd8            mov     ebx,eax
    `041cd696 89442450        mov     dword ptr [rsp+50h],eax
    `041cd69a 3bc7            cmp     eax,edi
    `041cd69c 0f8cc00ef6ff    jl      nt! ?? ::NNGAKEGL::`string'+0x24224 (`0412e562)
    `041cd6a2 448bc6          mov     r8d,esi
    `041cd6a5 33d2            xor     edx,edx
    `041cd6a7 488b5c2458      mov     rbx,qword ptr [rsp+58h]
    `041cd6ac 488bcb          mov     rcx,rbx
    `041cd6af e8dc61d1ff      call    nt!memset (`03ee3890)
    `041cd6b4 413bf7          cmp     esi,r15d
    `041cd6b7 0f87b40ef6ff    ja      nt! ?? ::NNGAKEGL::`string'+0x24233 (`0412e571)
    `041cd6bd 4889bb30040000  mov     qword ptr [rbx+430h],rdi
    `041cd6c4 488d8bb0030000  lea     rcx,[rbx+3B0h]
    `041cd6cb 48898c2480000000 mov     qword ptr [rsp+80h],rcx
    `041cd6d3 498b8580010000  mov     rax,qword ptr [r13+180h]
    `041cd6da 488901          mov     qword ptr [rcx],rax
    `041cd6dd 41f6042404      test    byte ptr [r12],4
    `041cd6e2 0f85c00ef6ff    jne     nt! ?? ::NNGAKEGL::`string'+0x2426a (`0412e5a8)
    `041cd6e8 488db338040000  lea     rsi,[rbx+438h]
    `041cd6ef 48893e          mov     qword ptr [rsi],rdi
    `041cd6f2 c7834004000007000000 mov dword ptr [rbx+440h],7
    `041cd6fc 488d8bc0030000  lea     rcx,[rbx+3C0h]
    `041cd703 33d2            xor     edx,edx
    `041cd705 448d4201        lea     r8d,[rdx+1]
    `041cd709 e88e56d0ff      call    nt!KeInitializeSemaphore (`03ed2d9c)
    `041cd70e 488d8b68030000  lea     rcx,[rbx+368h]
    `041cd715 48894908        mov     qword ptr [rcx+8],rcx
    `041cd719 488909          mov     qword ptr [rcx],rcx
    `041cd71c 488d83e8030000  lea     rax,[rbx+3E8h]
    `041cd723 48894008        mov     qword ptr [rax+8],rax
    `041cd727 488900          mov     qword ptr [rax],rax
    `041cd72a 4889bb80040000  mov     qword ptr [rbx+480h],rdi
    `041cd731 4889bb98030000  mov     qword ptr [rbx+398h],rdi
    `041cd738 488d83a0030000  lea     rax,[rbx+3A0h]
    `041cd73f 48894008        mov     qword ptr [rax+8],rax
    `041cd743 488900          mov     qword ptr [rax],rax
    `041cd746 48a11400000080f7ffff mov rax,qword ptr [FFFFF78000000014h]
    `041cd750 488b4c2458      mov     rcx,qword ptr [rsp+58h]
    `041cd755 48898160030000  mov     qword ptr [rcx+360h],rax
    `041cd75c 48898c24b8000000 mov     qword ptr [rsp+0B8h],rcx
    `041cd764 89bc24c0000000  mov     dword ptr [rsp+0C0h],edi
    `041cd76b f0480fba2e00    lock bts qword ptr [rsi],0
    `041cd771 0f823d0ef6ff    jb      nt! ?? ::NNGAKEGL::`string'+0x24276 (`0412e5b4)
    `041cd777 4c8b7c2458      mov     r15,qword ptr [rsp+58h]
    `041cd77c 498d9fb8030000  lea     rbx,[r15+3B8h]
    `041cd783 48899c24b0000000 mov     qword ptr [rsp+0B0h],rbx
    `041cd78b 488d9424b8000000 lea     rdx,[rsp+0B8h]
    `041cd793 488b0d2eb4ebff  mov     rcx,qword ptr [nt!PspCidTable (`04088bc8)]
    `041cd79a e8a5050000      call    nt!ExCreateHandle (`041cdd44)
    `041cd79f 488903          mov     qword ptr [rbx],rax
    `041cd7a2 483bc7          cmp     rax,rdi
    `041cd7a5 0f84170ef6ff    je      nt! ?? ::NNGAKEGL::`string'+0x24284 (`0412e5c2)
    `041cd7ab 4c3bf7          cmp     r14,rdi
    `041cd7ae 0f8429050000    je      nt!PspAllocateThread+0x728 (`041cdcdd)
    `041cd7b4 668bf7          mov     si,di
    `041cd7b7 89742460        mov     dword ptr [rsp+60h],esi
    `041cd7bb 41f6042480      test    byte ptr [r12],80h
    `041cd7c0 0f8592020000    jne     nt!PspAllocateThread+0x4a4 (`041cda58)
    `041cd7c6 41f6042402      test    byte ptr [r12],2
    `041cd7cb 0f85dc040000    jne     nt!PspAllocateThread+0x6f8 (`041cdcad)
    `041cd7d1 41b808000000    mov     r8d,8
    `041cd7d7 4c8ba42470020000 mov     r12,qword ptr [rsp+270h]
    `041cd7df 4c3be7          cmp     r12,rdi
    `041cd7e2 0f84c90ef6ff    je      nt! ?? ::NNGAKEGL::`string'+0x2437b (`0412e6b1)
    `041cd7e8 4939bd20030000  cmp     qword ptr [r13+320h],rdi
    `041cd7ef 0f8512030000    jne     nt!PspAllocateThread+0x552 (`041cdb07)
    `041cd7f5 41f6042401      test    byte ptr [r12],1
    `041cd7fa 0f858e0ef6ff    jne     nt! ?? ::NNGAKEGL::`string'+0x24358 (`0412e68e)
    `041cd800 bb00100000      mov     ebx,1000h
    `041cd805 41397c2420      cmp     dword ptr [r12+20h],edi
    `041cd80a 0f853e0ef6ff    jne     nt! ?? ::NNGAKEGL::`string'+0x24318 (`0412e64e)
    `041cd810 488d942450010000 lea     rdx,[rsp+150h]
    `041cd818 498bcd          mov     rcx,r13
    `041cd81b e8f04bd4ff      call    nt!KeStackAttachProcess (`03f12410)
    `041cd820 4c8bb42448020000 mov     r14,qword ptr [rsp+248h]
    `041cd828 4c89742428      mov     qword ptr [rsp+28h],r14
    `041cd82d 48c744242000000100 mov   qword ptr [rsp+20h],10000h
    `041cd836 4c8bcb          mov     r9,rbx
    `041cd839 4d8b442408      mov     r8,qword ptr [r12+8]
    `041cd83e 498b542418      mov     rdx,qword ptr [r12+18h]
    `041cd843 498b4c2410      mov     rcx,qword ptr [r12+10h]
    `041cd848 e8b7180000      call    nt!RtlCreateUserStack (`041cf104)
    kd> r
    rax=0000000000000000 rbx=0000000000001000 rcx=fffff88000002000
    rdx=000007fe00000000 rsi=fffffa8003020000 rdi=0000000000000000
    rip=041cd848 rsp=fffff8800422be00 rbp=fffffa8004170b30
     r8=0000000000000000  r9=0000000000001000 r10=0000000000000001
    r11=fffff8800422bde0 r12=fffff8800422c310 r13=fffffa8004170b30
    r14=fffff8800422c340 r15=fffffa8003028b60
    kd> dq [rsp+270h] l1
    fffff880`0422c070  fffff880`0422c310
    kd> dq fffff880`0422c310 l4
    fffff880`0422c310  00000000`00000000 00000000`00000000
    fffff880`0422c320  fffff880`00002000 000007fe`00000000

根据上面的执行路径，传入 RtlCreateUserStack 函数的第一个参数 rcx 寄存器是由 qword ptr [r12+10h] 赋值的。而
r12 寄存器在稍早时候取 [rsp+270h] 指向地址的指针长度的值。

[rsp+270h] 是调用者传递给该函数的第 11 个参数。继续向上追溯：

    
    
    nt!PspCreateThread:
    `041cd2ac 48895c2410      mov     qword ptr [rsp+10h],rbx
    `041cd2b1 55              push    rbp
    `041cd2b2 56              push    rsi
    `041cd2b3 57              push    rdi
    `041cd2b4 4154            push    r12
    `041cd2b6 4155            push    r13
    `041cd2b8 4156            push    r14
    `041cd2ba 4157            push    r15
    `041cd2bc 4881ec40020000  sub     rsp,240h
    `041cd2c3 488b051667e8ff  mov     rax,qword ptr [nt!_security_cookie (`040539e0)]
    `041cd2ca 4833c4          xor     rax,rsp
    `041cd2cd 4889842430020000 mov     qword ptr [rsp+230h],rax
    `041cd2d5 4c8bac24c0020000 mov     r13,qword ptr [rsp+2C0h]
    `041cd2dd 488bbc24a0020000 mov     rdi,qword ptr [rsp+2A0h]
    `041cd2e5 4c8bb424a8020000 mov     r14,qword ptr [rsp+2A8h]
    `041cd2ed 4c8bbc24c8020000 mov     r15,qword ptr [rsp+2C8h]
    `041cd2f5 65488b1c2588010000 mov   rbx,qword ptr gs:[188h]
    `041cd2fe 48898c2480000000 mov     qword ptr [rsp+80h],rcx
    `041cd306 488b8c24b0020000 mov     rcx,qword ptr [rsp+2B0h]
    `041cd30e 4c89842488000000 mov     qword ptr [rsp+88h],r8
    `041cd316 4533c0          xor     r8d,r8d
    `041cd319 48898c2490000000 mov     qword ptr [rsp+90h],rcx
    `041cd321 488b8c24b8020000 mov     rcx,qword ptr [rsp+2B8h]
    `041cd329 498bc1          mov     rax,r9
    `041cd32c 48898c2498000000 mov     qword ptr [rsp+98h],rcx
    `041cd334 488b8c24e8020000 mov     rcx,qword ptr [rsp+2E8h]
    `041cd33c 89542464        mov     dword ptr [rsp+64h],edx
    `041cd340 458ae0          mov     r12b,r8b
    `041cd343 48894c2470      mov     qword ptr [rsp+70h],rcx
    `041cd348 4d3be8          cmp     r13,r8
    `041cd34b 7407            je      a8 (`041cd354)
    `041cd34d 448aa3f6010000  mov     r12b,byte ptr [rbx+1F6h]
    `041cd354 4c89442468      mov     qword ptr [rsp+68h],r8
    `041cd359 be080000c0      mov     esi,0C0000008h
    `041cd35e 493bc0          cmp     rax,r8
    `041cd361 0f842a020000    je      2e5 (`041cd591)
    `041cd367 4c89442430      mov     qword ptr [rsp+30h],r8
    `041cd36c 4c8b05ad4cf4ff  mov     r8,qword ptr [nt!PsProcessType (`04112020)]
    `041cd373 488d4c2478      lea     rcx,[rsp+78h]
    `041cd378 48894c2428      mov     qword ptr [rsp+28h],rcx
    `041cd37d 458acc          mov     r9b,r12b
    `041cd380 ba02000000      mov     edx,2
    `041cd385 488bc8          mov     rcx,rax
    `041cd388 c744242044666c74 mov     dword ptr [rsp+20h],746C6644h
    `041cd390 e84ba10000      call    nt!ObReferenceObjectByHandleWithTag (`041d74e0)
    `041cd395 488b6c2478      mov     rbp,qword ptr [rsp+78h]
    `041cd39a 4533c0          xor     r8d,r8d
    `041cd39d 413bc0          cmp     eax,r8d
    `041cd3a0 0f8c9a010000    jl      294 (`041cd540)
    `041cd3a6 453ae0          cmp     r12b,r8b
    `041cd3a9 0f85bc010000    jne     2bf (`041cd56b)
    `041cd56b 483b2dbe4af4ff  cmp     rbp,qword ptr [nt!PsInitialSystemProcess (`04112030)]
    `041cd572 0f8537feffff    jne     103 (`041cd3af)
    `041cd3af 8b8c24d0020000  mov     ecx,dword ptr [rsp+2D0h]
    `041cd3b6 41b901000000    mov     r9d,1
    `041cd3bc 418bc0          mov     eax,r8d
    `041cd3bf 4184c9          test    r9b,cl
    `041cd3c2 410f45c1        cmovne  eax,r9d
    `041cd3c6 f6c102          test    cl,2
    `041cd3c9 0f85ba010000    jne     2dd (`041cd589)
    `041cd3cf 89442460        mov     dword ptr [rsp+60h],eax
    `041cd3d3 f6c104          test    cl,4
    `041cd3d6 0f855e200500    jne     nt! ?? ::NNGAKEGL::`string'+0x2a7ca (`0421f43a)
    `041cd3dc f6c108          test    cl,8
    `041cd3df 0f8598010000    jne     2d1 (`041cd57d)
    `041cd3e5 66ff8bc4010000  dec     word ptr [rbx+1C4h]
    `041cd3ec 0f0d8d78010000  prefetchw [rbp+178h]
    `041cd3f3 488b8578010000  mov     rax,qword ptr [rbp+178h]
    `041cd3fa 4883e0fe        and     rax,0FFFFFFFFFFFFFFFEh
    `041cd3fe 488d4802        lea     rcx,[rax+2]
    `041cd402 f0480fb18d78010000 lock cmpxchg qword ptr [rbp+178h],rcx
    `041cd40b 0f8535200500    jne     nt! ?? ::NNGAKEGL::`string'+0x2a7d6 (`0421f446)
    `041cd411 488bcd          mov     rcx,rbp
    `041cd414 e8d70ad2ff      call    nt!ObfReferenceObject (`03eedef0)
    `041cd419 488b442470      mov     rax,qword ptr [rsp+70h]
    `041cd41e 488b942488000000 mov     rdx,qword ptr [rsp+88h]
    `041cd426 4c8d9c24a0000000 lea     r11,[rsp+0A0h]
    `041cd42e 4d8bce          mov     r9,r14
    `041cd431 458ac4          mov     r8b,r12b
    `041cd434 4c895c2458      mov     qword ptr [rsp+58h],r11
    `041cd439 4889442450      mov     qword ptr [rsp+50h],rax
    `041cd43e 488d442468      lea     rax,[rsp+68h]
    `041cd443 4889442448      mov     qword ptr [rsp+48h],rax
    `041cd448 488d442460      lea     rax,[rsp+60h]
    `041cd44d 488bcd          mov     rcx,rbp
    `041cd450 4889442440      mov     qword ptr [rsp+40h],rax
    `041cd455 488b8424e0020000 mov     rax,qword ptr [rsp+2E0h]
    `041cd45d 4889442438      mov     qword ptr [rsp+38h],rax
    `041cd462 488b8424d8020000 mov     rax,qword ptr [rsp+2D8h]
    `041cd46a 4889442430      mov     qword ptr [rsp+30h],rax
    `041cd46f 4c897c2428      mov     qword ptr [rsp+28h],r15
    `041cd474 4c896c2420      mov     qword ptr [rsp+20h],r13
    `041cd479 e836010000      call    nt!PspAllocateThread (`041cd5b4)
    kd> dq [rsp+50h] l1
    fffff880`04286070  fffff880`04286310
    kd> dq fffff880`04286310 l4
    fffff880`04286310  00000000`00000000 00000000`00000000
    fffff880`04286320  fffff880`00000000 00000144`00000000

观察上面的执行路径不难发现传递给 PspAllocateThread 函数的第 11 个参数来自 PspCreateThread 函数的
[rsp+2E8h] 第 14 个参数，而在当前函数中没有进行任何修改和取值访问。

而在 NtCreateThreadEx 函数中由于虚拟化设置问题暂时无法进行单步追踪。所以通过 IDA 对其汇编代码进行分析，再加上通过
PspAllocateThread 函数返回后的上下文，对运行现场的环境进一步的追踪：

    
    
    `403701DF loc_1403701DF:
    `403701DF    mov     [rsp+748h+var_6D8], bl
    `403701E3    mov     rax, [rsp+748h+arg_40]
    `403701EB    mov     [rsp+748h+var_6C8], rax
    `403701F3    mov     rax, [rsp+748h+arg_48]
    `403701FB    mov     [rsp+748h+var_6C0], rax
    `40370203    mov     rax, [rsp+748h+arg_38]
    `4037020B    mov     [rsp+748h+var_6D0], rax
    `40370210    mov     [rsp+748h+var_6B8], ebx
    `40370217    xor     edx, edx        ; Val
    `40370219    mov     r8d, 150h       ; Size
    `4037021F    lea     rcx, [rsp+748h+var_198] ; Dst
    `40370227    call    memset
    `4037022C    test    rdi, rdi
    `4037022F    jz      short loc_140370285
    `40370231    mov     rax, gs:188h
    `4037023A    lea     r9, [rsp+748h+var_198]
    `40370242    mov     r8d, 1
    `40370248    mov     dl, [rax+1F6h]
    `4037024E    mov     rcx, rdi
    `40370251    call    PspBuildCreateProcessContext
    `40370256    test    eax, eax
    `40370258    js      loc_140370396
    `4037025E    lea     rax, [rsp+748h+var_70]
    `40370266    bt      dword ptr [rsp+748h+var_198], 0Ch
    `4037026F    cmovnb  rax, rbx
    `40370273    mov     rbx, rax
    `40370276    bt      dword ptr [rsp+748h+var_198], 0Eh
    `4037027F    jb      loc_1403C8D38
    `40370285
    `40370285 loc_140370285:
    `40370285    mov     [rsp+748h+var_638], 10000Bh
    `40370290    mov     rax, cs:PspUserThreadStart
    `40370297    mov     [rsp+748h+var_570], rax
    `4037029F    mov     rax, [rsp+748h+arg_20]
    `403702A7    mov     [rsp+748h+var_5E8], rax
    `403702AF    mov     rax, [rsp+748h+arg_28]
    `403702B7    mov     [rsp+748h+var_5E0], rax
    `403702BF    mov     ecx, 2Bh
    `403702C4    mov     [rsp+748h+var_62E], cx
    `403702CC    mov     [rsp+748h+var_62C], cx
    `403702D4    lea     eax, [rcx+28h]
    `403702D7    mov     [rsp+748h+var_62A], ax
    `403702DF    mov     [rsp+748h+var_628], cx
    `403702E7    mov     [rsp+748h+var_626], cx
    `403702EF    lea     eax, [rcx+8]
    `403702F2    mov     [rsp+748h+var_630], ax
    `403702FA    mov     ecx, 1F80h
    `403702FF    mov     [rsp+748h+var_634], ecx
    `40370306    mov     eax, 27Fh
    `4037030B    mov     [rsp+748h+var_568], ax
    `40370313    mov     [rsp+748h+var_550], ecx
    `4037031A    lea     rax, [rsp+748h+var_6D8]
    `4037031F    mov     [rsp+748h+var_6E0], rax
    `40370324    and     [rsp+748h+var_6E8], 0
    `4037032A    and     [rsp+748h+var_6F0], 0
    `40370330    mov     dword ptr [rsp+748h+var_6F8], r12d ; __int64
    `40370335    lea     rax, [rsp+748h+var_6A8]
    `4037033D    mov     [rsp+748h+var_700], rax ; __int64
    `40370342    lea     rax, [rsp+748h+var_668]
    `4037034A    mov     [rsp+748h+var_708], rax ; __int64
    `4037034F    mov     rax, qword ptr [rsp+748h+var_190]
    `40370357    mov     qword ptr [rsp+748h+var_710], rax ; int
    `4037035C    mov     qword ptr [rsp+748h+var_718], rbx ; int
    `40370361    lea     rax, [rsp+748h+var_198]
    `40370369    mov     [rsp+748h+var_720], rax ; __int64
    `4037036E    and     [rsp+748h+var_728], 0
    `40370374    mov     r9, r15         ; __int64
    `40370377    mov     r8, r14         ; __int64
    `4037037A    mov     edx, r13d       ; __int64
    `4037037D    mov     rcx, rsi        ; PVOID
    `40370380    call    PspCreateThread

上面的反汇编指令片段是在 IDA 中截取的。根据汇编代码显示，[rsp+748h+var_6E0] 是传入 PspCreateThread 函数的第 14
个参数。其取值为 [rsp+748h+var_6D8] 局部变量的地址。var_6D8 是位于栈上的一个结构体对象，需要关注的是其中 +10
偏移的域，在稍早时候对结构体赋初值，这个域由第 9 个参数 [rsp+748h+arg_40] 赋值。

    
    
    `403701DF    mov     [rsp+748h+var_6D8], bl
    `403701E3    mov     rax, [rsp+748h+arg_40]
    `403701EB    mov     [rsp+748h+var_6C8], rax

由第 9 个参数赋初值，那就说明这个值是由 NtCreateThreadEx 的调用者传入的。该函数原型如下：

    
    
    NTSTATUS
    NTAPI
    Handle_SSDT_NtCreateThreadEx(
        OUT PHANDLE                  ThreadHandle,
        IN  ACCESS_MASK              DesiredAccess,
        IN  POBJECT_ATTRIBUTES       ObjectAttributes,
        IN  HANDLE                   ProcessHandle,
        IN  LPTHREAD_START_ROUTINE   StartAddress,
        IN  LPVOID                   Parameter,
        IN  BOOL                     CreateSuspended,
        IN  ULONG                    StackZeroBits,
        IN  ULONG                    SizeOfStackCommit,
        IN  ULONG                    SizeOfStackReserve,
        OUT LPVOID                   BytesBuffer
    );

第 9 个参数是 SizeOfStackCommit，但我在 Hook 处理函数中监控这个参数，它的值始终是处于正常范围的数值，从未出现前面分析中的
0xFFFFF88000000000 这样的数据。突然注意到在 Hook 处理函数中调用原函数时对栈上的参数进行赋值的代码：

    
    
    `050721af 488b8424d0000000 mov     rax,qword ptr [rsp+0D0h]
    `050721b7 4889442450       mov     qword ptr [rsp+50h],rax
    `050721bc 8b8424c8000000   mov     eax,dword ptr [rsp+0C8h]
    `050721c3 89442448         mov     dword ptr [rsp+48h],eax
    `050721c7 8b8424c0000000   mov     eax,dword ptr [rsp+0C0h]
    `050721ce 89442440         mov     dword ptr [rsp+40h],eax
    `050721d2 8b8424b8000000   mov     eax,dword ptr [rsp+0B8h]
    `050721d9 89442438         mov     dword ptr [rsp+38h],eax
    `050721dd 8b8424b0000000   mov     eax,dword ptr [rsp+0B0h]
    `050721e4 89442430         mov     dword ptr [rsp+30h],eax
    `050721e8 488b8424a8000000 mov     rax,qword ptr [rsp+0A8h]
    `050721f0 4889442428       mov     qword ptr [rsp+28h],rax
    `050721f5 488b8424a0000000 mov     rax,qword ptr [rsp+0A0h]
    `050721fd 4889442420       mov     qword ptr [rsp+20h],rax
    `05072202 4c8b8c2498000000 mov     r9,qword ptr [rsp+98h]
    `0507220a 4c8b842490000000 mov     r8,qword ptr [rsp+90h]
    `05072212 8b942488000000   mov     edx,dword ptr [rsp+88h]
    `05072219 488b8c2480000000 mov     rcx,qword ptr [rsp+80h]
    `05072221 ff542468         call    qword ptr [rsp+68h]

上面代码中 mov dword ptr [rsp+40h], eax 这条指令对 SizeOfStackCommit
参数进行传值。在传值之前我无意中看了一下 rsp+40h 地址的原值：

    
    
    kd> dq [rsp+40h] l1
    fffff880`0310ea30  fffff880`0310ea98

原来如此，由于 Hook 处理函数和原函数指针类型定义失误，将这个参数定义成了 ULONG32 类型，所以在传参时只通过 eax 进行赋值，栈上的参数位置高
32 位被忽略并保持原值；但在实际的 NtCreateThreadEx 函数中，应是将这个参数作为 ULONG_PTR 进行解析，在 64 位下应是
ULONG64 宽度，所以将参数中没有清零的高 32 位也作为参数值的一部分了，这就最终导致了前面的错误状态码。而这次的错误和虚拟化无关。

真是一次坑爹的分析。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/577/>

