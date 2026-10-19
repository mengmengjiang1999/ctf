**作者：LarryS@青藤实验室**  
**原文链接：<https://mp.weixin.qq.com/s/dy4ytn6cgKxp7avu-WNSHg>**

## 0\. 前言

这篇文章介绍了 CVE-2023-24949 漏洞，该漏洞英文全称是 “Windows Kernel Elevation of Privilege
Vulnerability”，由此判断漏洞位于 ntoskrnl.exe 中。根据官方说明，攻击者利用该漏洞可以实现本地提权。

本文按照个人的分析流程对漏洞进行了介绍，通过补丁对比、功能分析以及函数调试确定了漏洞原理以及漏洞的触发方法，并成功对漏洞进行触发，最后进行了简单的总结。

## 1\. 补丁对比

检查补丁修复前后的 ntoskrnl.exe，发现一共修改了三个函数。

![
](https://images.seebug.org/content/images/2023/06/56cdeb9f-e8a7-4f73-bda7-af52d85e4ab8.png-w331s)

其中

`IoInitSystemPreDrivers` 调整了部分代码结构，减少了条件语句的嵌套，同时将部分代码整合成了新的函数，没有功能性变化；

`PopTransitionSystemPowerStateEx` 同样未发现功能性变化；

问题出现在 `MiCaptureRetpolineRelocationTables` 函数：

_注：为了方便理解，我在这里直接贴出进行完函数功能分析后，已经整理了变量名和数据结构的函数版本。_

![](https://images.seebug.org/content/images/2023/06/14/1686725522000-2023-06-08-14-44-26.png-w331s)

注意黄框圈起的位置就是补丁修复位置，在补丁修复之前，首先进行三个数的相加，然后通过检查加法结果是否大于其中一个加数来判断是否溢出。补丁修复后，三个数相加的操作被分成两步进行，每次的加法操作都通过调用
`RtlULongAdd` 实现，该函数有一个检查加法结果是否大于被加数的操作：

    
    
    NTSTATUS __stdcall RtlULongAdd(ULONG ulAugend, ULONG ulAddend, ULONG *pulResult)
    {
      ULONG v3; // eax
      ULONG result; // edx
      NTSTATUS status; // eax
    
      v3 = ulAugend + ulAddend;
      result = -1;
      if ( v3 >= ulAugend )
        result = v3;
      status = v3 < ulAugend ? 0xC0000095 : 0;
      *pulResult = result;
      return status;
    }

由此可以看出这其实是一个整数溢出问题，在补丁修复之前，只检查了加数 `imageDynamicRelocationRva`
和其他两个数相加之后是否溢出，但是没有检查加数 `baseRelocSize` 和 加数 `12` 相加后是否溢出。

注意截图中的绿框，在后续代码中使用了 `baseRelocSize + 12`
作为空间分配和数据复制的大小参数。在截图中无法看出，进行加法操作的三个加数原本都是四字节数据，加法的结果也是四字节数据，但是在 64
位系统上，实际上存储这些数据的寄存器是 64 位的，而进行空间分配的 `MiAllocatePool` 函数和进行数据复制的 `memmove`
函数，表示数据大小的参数是 `size_t` 类型，在 64 位系统上同样表示 64 位数据。因此，如果表示数据大小的参数 `baseRelocSize +
12` 发生溢出，就可以绕过上方的 `curRetRelocRva > endOfTable` 检查，从而在 `memmove`
函数中访问到远超出合法数据范围数据。

## 2\. 函数功能分析

上面的截图已经对变量进行了重命名，并且导入了相关数据结构，但在分析之初，所有变量名都还是 `v*`
的格式，完全看不出函数功能，因此在进行了补丁分析之后，我首先对函数功能进行了分析。

### 2.1 初步的尝试

从函数名来看，这个函数和 Retpoline 有关，Retpline 是用于解决 Spectre
漏洞变体的一种机制。同时根据函数引用，`MiParseImageLoadConfig` 函数对其进行了调用，看起来好像和可执行文件的加载有关，但是不确定。

我对这两类漏洞有一些浅薄的认识，但是不知道 Retpoline 和可执行文件加载有什么关系，于是开始了一些漫无目的的搜索。

在对 Retpoline、relocation table 等关键词进行搜索时，我发现了 Dynamic Value Relocation
Table(DVRT) 的介绍【1】，及其链接的 Load Configuration Directory 的相关文档【2】，事情一下子变得清晰了起来。

### 2.2 相关知识点介绍

Spectre 是和计算机硬件相关的一种漏洞，利用了 CPU 的分支预测机制实现敏感数据的泄露。Retpoline 就是谷歌为了解决该问题开发的一种 CPU
补丁机制。

在原有的 CPU 分支预测机制中，CPU 会根据之前执行的指令预测分支跳转的目的地址并提前进行预处理，但是攻击者可以通过构造特定的代码序列促使 CPU
猜错分支，从而获取受保护的数据。

Retpoline 机制采用一种类似于 jump table 的模式，将分支跳转操作转换为一个间接的非分支跳转，从而避免了 CPU 分支预测机制的使用。

Retpoline 的转换是在将内核模块加载到内存时临时执行的，但是操作系统是怎么知道在哪里进行转换呢？答案是所有的信息都保存在 Dynamic Value
Relocation Table(DVRT) 中，可以通过二进制文件的 load config 目录获得。

DVRT 会在编译阶段放入二进制文件中，编译器会把所有和间接跳转/调用有关的元数据保存到文件的 .reloc 段。当文件运行时，内核会对 DVRT
数据进行解析，并对保存的所有分支跳转进行转换。

### 2.3 DVRT 相关数据结构

首先是 DVRT 本身的格式，我只列出了两个数据结构，因为这两个数据结构可以导入 IDA，有助于对漏洞函数的分析：

    
    
    // DVRT 头部
    struct ImageDynamicRelocationTable
    {
        uint32_t version;   // 目前只有一个版本 1
        uint32_t size;      // 头部后面的 retpoline 信息数据大小
    };
    
    // 根据不同类型的 retpoline 类型，每块的起始部位有一个头部
    struct ImageDynamicRelocation
    {
        uint64_t symbol;          // 表示 retpoline 类型，可选数值为 3，4，5
        uint32_t baseRelocSize;   // 头部后面的该类型 retpoline 信息数据大小
    };

然后是 `_IMAGE_LOAD_CONFIG_DIRECTORY64` 结构，该结构可以用来对 DVRT 进行定位，同样可以导入
IDA，后面在使用到该数据结构的时候，会对相关字段进行说明：

    
    
    struct _IMAGE_LOAD_CONFIG_CODE_INTEGRITY {
       WORD Flags;           
       WORD Catalog;         
       DWORD CatalogOffset;  
       DWORD Reserved;       
    };
    
    struct _IMAGE_LOAD_CONFIG_DIRECTORY64 {
       DWORD Size;           
       DWORD TimeDateStamp; 
       WORD MajorVersion;    
       WORD MinorVersion;    
       DWORD GlobalFlagsClear;
       DWORD GlobalFlagsSet;   
       DWORD CriticalSectionDefaultTimeout; 
       ULONGLONG DeCommitFreeBlockThreshold; 
       ULONGLONG DeCommitTotalFreeThreshold;
       ULONGLONG LockPrefixTable;
       ULONGLONG MaximumAllocationSize;
       ULONGLONG VirtualMemoryThreshold; 
       ULONGLONG ProcessAffinityMask;
       DWORD ProcessHeapFlags; 
       WORD CSDVersion;     
       WORD DependentLoadFlags;
       ULONGLONG EditList;        
       ULONGLONG SecurityCookie;  
       ULONGLONG SEHandlerTable;   
       ULONGLONG SEHandlerCount;   
       ULONGLONG GuardCFCheckFunctionPointer; 
       ULONGLONG GuardCFDispatchFunctionPointer;
       ULONGLONG GuardCFFunctionTable;
       ULONGLONG GuardCFFunctionCount;
       DWORD GuardFlags;     
       _IMAGE_LOAD_CONFIG_CODE_INTEGRITY CodeIntegrity;
       ULONGLONG GuardAddressTakenIatEntryTable;
       ULONGLONG GuardAddressTakenIatEntryCount;
       ULONGLONG GuardLongJumpTargetTable;
       ULONGLONG GuardLongJumpTargetCount;
       ULONGLONG DynamicValueRelocTable;
       ULONGLONG CHPEMetadataPointer;
       ULONGLONG GuardRFFailureRoutine;
       ULONGLONG GuardRFFailureRoutineFunctionPointer;
       DWORD DynamicValueRelocTableOffset;
       WORD DynamicValueRelocTableSection;
       WORD Reserved2;
       ULONGLONG GuardRFVerifyStackPointerFunctionPointer;
       DWORD HotPatchTableOffset;
       DWORD Reserved3;
       ULONGLONG EnclaveConfigurationPointer;
       ULONGLONG VolatileMetadataPointer;
       ULONGLONG GuardEHContinuationTable;
       ULONGLONG GuardEHContinuationCount;
    };

### 2.4 小结

根据以上信息，可以确定漏洞函数用于在 load config 阶段获取
DVRT，同时根据其调用者，以及调用之前执行的其他函数参数，就可以确定漏洞函数中大部分变量的类型及功能，最终得到文章开头截图中的函数状态。

## 3\. 漏洞触发

### 3.1 确定方向

想要触发漏洞，首先需要知道怎样到达漏洞函数。在查看 `MiCaptureRetpolineRelocationTables`
函数的引用情况时，有两个函数对该函数进行了调用：

![](https://images.seebug.org/content/images/2023/06/14/1686725524000-2023-05-19-17-52-56.png-w331s)

ChatGPT 对这两个函数的解释如下：

> MiParseImageLoadConfig 是 Windows 操作系统 NT 内核中的一个函数，用于解析可执行文件的加载配置信息。在 Windows
> 中，可执行文件通常包含有加载配置信息，这些信息用于指示操作系统如何将该文件加载到内存中，并且如何初始化其中的数据和代码。
> MiParseImageLoadConfig
> 函数主要是在内核模块加载过程中使用的，它会从可执行文件中读取加载配置信息，并且根据这些信息对内存进行合适的分配和初始化。具体来说，MiParseImageLoadConfig
> 函数可以完成以下几个任务： 1\. 解析可执行文件中的加载配置信息，包括基址、大小、校验和等。 2\.
> 根据加载配置信息计算出需要分配的内存大小和位置，并且分配相应的虚拟内存区域。 3\.
> 将可执行文件中的代码、数据等部分复制到分配的内存区域中，并且完成必要的重定位和初始化工作。
>
> 需要注意的是，MiParseImageLoadConfig 函数是 Windows
> 内核中的一个底层函数，通常不会直接被应用程序调用。它主要是由其他内核模块相关的函数来调用，以完成可执行文件的加载和初始化工作。
>
> MiCaptureBootDriverRetpolineInfo 是 Windows 操作系统 NT 内核中的一个函数，用于捕获引导驱动程序的
> Retpoline 信息。在 Windows 中，Retpoline 是一种特殊的代码转换技术，用于缓解 Spectre 及类似的 CPU
> 漏洞所导致的安全风险。 具体来说，当一个驱动程序被加载到内存中时，MiCaptureBootDriverRetpolineInfo
> 函数会扫描它的代码段，并且为其中包含的 Retpoline 调用生成相应的跳转目标地址表。这个跳转目标地址表可以用于替代原本的 Retpoline
> 跳转，从而提高代码的执行效率和安全性。 需要注意的是，MiCaptureBootDriverRetpolineInfo
> 函数只会在引导过程中被调用，它主要是用于捕获引导驱动程序的 Retpoline 信息，以便在后续的操作中使用。其他驱动程序的 Retpoline
> 信息则会在加载时进行捕获和处理。

看起来一个函数是在可执行文件加载的时候被调用，一个是在系统引导的过程中被调用，显然前者比较好分析。

虽然是这么想的，但是我并不确定上面信息的准确度，同时也不知道自己理解的是不是正确，因此我对这两个函数分别下了断点，尝试操作系统看看会不会发生中断。

之后我发现，在 Explorer 中对文件进行浏览时，可以轻易的多次中断在 `MiParseImageLoadConfig` 函数上，但是并没有出现
`MiCaptureBootDriverRetpolineInfo` 中断的情况，因此选择 `MiParseImageLoadConfig`
这条调用线作为分析对象。

### 3.2 定位 DVRT

目前并没有公开文档说明包含 DVRT 信息的 PE
文件结构，而且在上面测试系统是否中断时，我也尝试在漏洞函数上下了断点，但是并没有发生中断在漏洞函数的情况，因此我没有办法通过分析已有文件确定 DVRT
信息的位置。

_注：后来我发现其实在系统文件夹还是比较容易能够中断在漏洞函数的，但是因为文件太多，不确定到底是哪个文件包含 DVRT 信息。_

一开始我尝试直接使用 VS 的功能，让编译后的程序具有 DVRT，但是没有成功，不确定 VS
是否具有相关功能，因此我决定任意创建一个程序，然后使用十六进制编辑器直接修改文件内容，使系统在处理该文件时能够到达漏洞所在位置。

使用 visual studio 创建一个 Empty Project(C++)，程序内容任意，我只写了一个空的 main 函数，编译生成 exe 文件。

先使用该文件进行测试，看系统代码能够执行到哪里。在 `MiCaptureRetpolineRelocationTables`
函数设置断点，系统不会发生中断，但是如果在 `MiParseImageLoadConfig`
设置断点，系统会发生多次中断，无法判断哪次中断是测试文件导致的。

通过查看 IDA，发现系统在调用 `MiCaptureRetpolineRelocationTables` 之前，首先调用了
`MiCaptureDynamicRelocationTableRva`
函数，如果该函数执行成功，才会继续往下执行，因此我在该函数的调用位置设置断点，并且将测试文件单独放在一个文件夹中，在使用资源管理器打开该文件夹时，系统中断在了
`MiCaptureDynamicRelocationTableRva` 函数的调用处，说明这个正常生成的测试文件至少是可以执行到
`MiCaptureDynamicRelocationTableRva` 函数的。

`MiCaptureDynamicRelocationTableRva` 函数定义如下：

![](https://images.seebug.org/content/images/2023/06/14/1686725524000-2023-06-09-11-52-13.png-w331s)

_注：configDirec 这个变量的类型是我根据函数功能以及和 DVRT
有关的数据结构进行的猜测，设置后发现`_IMAGE_LOAD_CONFIG_DIRECTORY64` 类型确实能够满足函数功能。_

注意图片中的注释信息，为了让这个函数执行成功，我们需要让 `DynamicValueRelocTableSection` 这个字段的数值不为 0。

但是如何确定 `DynamicValueRelocTableSection` 在文件中的位置呢？可以使用 VS 提供的 dumpbin.exe
工具，输出结果如下：

    
    
    PS C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.35.32215\bin\Hostx64\x86> ./dumpbin.exe /loadconfig 【手动马赛克文件路径】
    Microsoft (R) COFF/PE Dumper Version 14.35.32216.1
    Copyright (C) Microsoft Corporation.  All rights reserved.
    
    
    Dump of file 【手动马赛克文件路径】
    
    File Type: EXECUTABLE IMAGE
    
      Section contains the following load config:
    
                00000140 size
                       0 time date stamp
                    0.00 Version
                       0 GlobalFlags Clear
                       0 GlobalFlags Set
                       0 Critical Section Default Timeout
                       0 Decommit Free Block Threshold
                       0 Decommit Total Free Threshold
        0000000000000000 Lock Prefix Table
                       0 Maximum Allocation Size
                       0 Virtual Memory Threshold
                       0 Process Affinity Mask
                       0 Process Heap Flags
                       0 CSD Version
                    0000 Dependent Load Flag
        0000000000000000 Edit List
        0000000140003008 Security Cookie
        0000000140002190 Guard CF address of check-function pointer
        00000001400021A0 Guard CF address of dispatch-function pointer
        0000000000000000 Guard CF function table
                       0 Guard CF function count
                00000100 Guard Flags
                           CF instrumented
                    0000 Code Integrity Flags
                    0000 Code Integrity Catalog
                00000000 Code Integrity Catalog Offset
                00000000 Code Integrity Reserved
        0000000000000000 Guard CF address taken IAT entry table
                       0 Guard CF address taken IAT entry count
        0000000000000000 Guard CF long jump target table
                       0 Guard CF long jump target count
        0000000000000000 Dynamic value relocation table
        0000000000000000 Hybrid metadata pointer
        0000000000000000 Guard RF address of failure-function
        0000000000000000 Guard RF address of failure-function pointer
                00000000 Dynamic value relocation table offset
                    0000 Dynamic value relocation table section
    .....

注意到文件中的 Dynamic value relocation table offset 和 Dynamic value relocation table
section 都是 0，这里就是我们打算修改的内容。

为了能够定位该内容在文件中的位置，可以搜索 `0000000140003008 Security Cookie`
这个字段，因为它的值比较特殊，不容易发生重复。最终定位到如下位置：

![](https://images.seebug.org/content/images/2023/06/14/1686725524000-2023-06-09-12-08-22.png-w331s)

根据 `_IMAGE_LOAD_CONFIG_DIRECTORY64` 的结构确定红框中配置信息的起始位置，同时定位要修改的 DVRT
信息所在位置，其中前四个字节是 offset，后四个字节是 section。我们需要修改的是后四个字节，让其不等于0，同时因为这个二进制文件有 6 个
section，因此数值也不能大于 6。这里可以直接将这个数值修改成 1。

修改后的文件还不能到达漏洞点，但是此时可以先调试确定一下相关变量的数值。结合上面的 `MiCaptureDynamicRelocationTableRva`
函数截图，当系统计算完 sectionHeader 之后，检查该数值发现定位到的是第一个 section header `.text`

    
    
    // sectionHeader
    nt!MiCaptureDynamicRelocationTableRva+0xeb:
    fffff805`7e9249f7 493bf8          cmp     rdi,r8
    0: kd> db r8
    fffff805`d4090208  2e 74 65 78 74 00 00 00-0c 0d 00 00 00 10 00 00  .text...........
    fffff805`d4090218  00 0e 00 00 00 04 00 00-00 00 00 00 00 00 00 00  ................
    fffff805`d4090228  00 00 00 00 20 00 00 60-2e 72 64 61 74 61 00 00  .... ..`.rdata..
    fffff805`d4090238  b4 0e 00 00 00 20 00 00-00 10 00 00 00 12 00 00  ..... ..........
    fffff805`d4090248  00 00 00 00 00 00 00 00-00 00 00 00 40 00 00 40  ............@..@
    fffff805`d4090258  2e 64 61 74 61 00 00 00-38 06 00 00 00 30 00 00  .data...8....0..
    fffff805`d4090268  00 02 00 00 00 22 00 00-00 00 00 00 00 00 00 00  ....."..........
    fffff805`d4090278  00 00 00 00 40 00 00 c0-2e 70 64 61 74 61 00 00  ....@....pdata..
    // 计算得到的 DVRT RVA
    0: kd> p
    nt!MiCaptureDynamicRelocationTableRva+0x100:
    fffff805`7e924a0c 41890e          mov     dword ptr [r14],ecx
    0: kd> r rcx
    rcx=0000000000001000

继续向下执行可以进入 `MiCaptureRetpolineRelocationTables` 函数，根据上面计算得到的 RVA 数值得到的 DVRT
如下：

    
    
    0: kd> p
    nt!MiCaptureRetpolineRelocationTables+0x76:
    fffff805`7e9254de 4a8b043b        mov     rax,qword ptr [rbx+r15]
    0: kd> p
    nt!MiCaptureRetpolineRelocationTables+0x7a:
    fffff805`7e9254e2 4889442420      mov     qword ptr [rsp+20h],rax
    2: kd> db rbx+r15
    fffff805`d4091000  b8 01 00 00 00 c3 cc cc-cc cc cc cc cc cc cc cc  ................
    fffff805`d4091010  cc cc cc cc cc cc 66 66-0f 1f 84 00 00 00 00 00  ......ff........
    fffff805`d4091020  48 3b 0d e1 1f 00 00 75-10 48 c1 c1 10 66 f7 c1  H;.....u.H...f..
    fffff805`d4091030  ff ff 75 01 c3 48 c1 c9-10 e9 aa 02 00 00 cc cc  ..u..H..........
    fffff805`d4091040  40 53 48 83 ec 20 b9 01-00 00 00 e8 be 0b 00 00  @SH.. ..........
    fffff805`d4091050  e8 db 06 00 00 8b c8 e8-e8 0b 00 00 e8 cb 06 00  ................
    fffff805`d4091060  00 8b d8 e8 0c 0c 00 00-b9 01 00 00 00 89 18 e8  ................
    fffff805`d4091070  44 04 00 00 84 c0 74 73-e8 37 09 00 00 48 8d 0d  D.....ts.7...H..

在测试文件中搜索这段数据，定位发现这段数据就是 `.text` 段的起始内容：

![](https://images.seebug.org/content/images/2023/06/14/1686725524000-2023-06-09-15-19-34.png-w331s)

根据上面对 DVRT 数据结构的介绍，我们知道，如果按照 DVRT 解析这段数据，这里保存的首先是 8 字节的
`ImageDynamicRelocationTable` 结构，然后是 12 字节的 `ImageDynamicRelocation` 结构。

分析到这里，虽然我们不知道具有 DVRT 的 PE 文件究竟是什么结构，但是我们已经可以欺骗系统让它认为测试文件具有 DVRT，而且也知道了系统认为的
DVRT 在文件中的位置。

### 3.3 分析触发条件 & 尝试触发漏洞

我们看一下 `MiCaptureRetpolineRelocationTables` 函数的细节，确定 DVRT 需要满足的要求：

![](https://images.seebug.org/content/images/2023/06/14/1686725524000-2023-06-09-15-32-07.png-w331s)

注意黄框圈起的部分，按照要求修改测试文件中的数据：

![](https://images.seebug.org/content/images/2023/06/14/1686725524000-2023-06-09-15-32-49.png-w331s)

到这里测试文件应该是修改好了，重新测试的时候发现系统并没有崩溃，调试器提示信息：

    
    
    SXS: BasepCreateActCtx() NtCreateSection() failed. Status = 0xc000009a

重新在 `MiCaptureRetpolineRelocationTables` 单步调试，发现当系统执行到三个数值的加法处时，确实发生了整数溢出：

    
    
    3: kd> p
    nt!MiCaptureRetpolineRelocationTables+0xfe:
    fffff805`7e925566 4503f4          add     r14d,r12d
    3: kd> r r14d
    r14d=1014
    3: kd> r r12d
    r12d=ffffffff
    3: kd> p
    nt!MiCaptureRetpolineRelocationTables+0x101:
    fffff805`7e925569 443bf2          cmp     r14d,edx
    3: kd> r r14d
    r14d=1013

但是当系统执行到 `MiAllocatePool` 函数时，空间分配失败了。仔细看一下这个函数的调用参数：

    
    
    3: kd> p
    nt!MiCaptureRetpolineRelocationTables+0x181:
    fffff805`7e9255e9 e832ddb1ff      call    nt!MiAllocatePool (fffff805`7e443320)
    3: kd> r rcx
    rcx=0000000000000100
    3: kd> r rdx
    rdx=000000010000000b

rdx 应该就是分配空间大小，正如我们所猜测的那样，由于整数溢出，这里会分配一个超大的空间。问题就在这里，因为我的虚拟机内存不足，所以这个函数调用失败了。

调高虚拟机内存后，空间分配成功，继续执行数据复制操作：

    
    
    0: kd> p
    nt!MiCaptureRetpolineRelocationTables+0x19d:
    fffff805`7e925605 e83619d0ff      call    nt!memcpy (fffff805`7e626f40)
    0: kd> r rcx
    rcx=ffffd6001c000000
    0: kd> r rdx
    rdx=fffff805e5631008
    0: kd> r r8
    r8=000000010000000b

同样会尝试复制大量数据，数据源地址 `fffff805e5631008`，数据大小 `10000000b`，由于访问到非法内存空间，系统崩溃。

![](https://images.seebug.org/content/images/2023/06/14/1686725524000-2023-06-09-17-12-15.png-w331s)

## 4\. 总结

通过以上分析可知，CVE-2023-24949 是一个整数溢出漏洞，到我分析的位置为止，该漏洞可以实现内存越界读，如果想要实现本地提权，还需要进一步分析。

值得注意的是，这个漏洞的触发条件十分简单，在保证内存足够的前提下，只要在资源管理器看到测试文件就能触发漏洞，如果将测试文件放在桌面，系统将无法正常启动。如果配合钓鱼攻击，该漏洞可以实现更多功能。鉴于此，这次的
poc 文件不会直接发布在 github 上，感兴趣的朋友可以根据文章自己进行复现。

## 5\. 参考资料

  1. [Dynamic Value Relocation Table (DVRT) details](https://denuvosoftwaresolutions.github.io/DVRT/dvrt.html)
  2. [Windows PE32 load config directory](https://learn.microsoft.com/en-us/windows/win32/debug/pe-format#the-load-configuration-structure-image-only)
  3. [How Meltdown and Spectre haunt Anti-Cheat](https://denuvosoftwaresolutions.github.io/DVRT/haunted)
  4. <https://msrc.microsoft.com/update-guide/vulnerability/CVE-2023-24949>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/2080/>

