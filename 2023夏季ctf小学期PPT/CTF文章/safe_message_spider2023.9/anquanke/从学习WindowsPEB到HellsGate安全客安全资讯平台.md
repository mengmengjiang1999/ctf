# 从学习Windows PEB到Hell's Gate

阅读量 **247295**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2022-02-10 14:30:31

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

## 0x01 前言

地狱之门技术相对来说已经算比较老的技术了，各种Dinvoke的框架中实际上也是借鉴了这种思路，最近这段时间想要研究下一些其他绕过AV/EDR的常见手段，其中就包括系统调用(syscall)和sRDI技术，但是发现对于PEB的了解比较少，借此学习下PEB的相关属性和围绕PEB能够展开的相关技术。

## 0x02 PEB的一些数据结构了解

进程环境块是一个从内核中分配给每个进程的用户模式结构,每一个进程都会有从ring0分配给该进程的进程环境块，后续我们主要需要了解`_PEB_LDR_DATA`以及其他子结构  
找到一张非常好的图:

> 这张图是x86系统的结构体，可以看到PEB是在fs寄存器的0x30的偏移处，因此是x86的结构体

![](https://p0.ssl.qhimg.com/t0111dadcc06c18db45.png)

继续借助上图，可以看到在PEB结构偏移`0xc`处有一个LDR结构体,该结构体包含有关为进程加载的模块的信息（存储着该进程所有模块数据的链表），可以参考[MSDN](https://docs.microsoft.com/en-us/windows/win32/api/winternl/ns-winternl-peb_ldr_data)

![](https://p2.ssl.qhimg.com/t0160dcab0f7014ee70.png)

很多时候通常的思路是通过TEB找到PEB中的LDR结构体，在该结构体中存在着 **3处双向链表** :

    
    
    struct _PEB_LDR_DATA
    {
        ULONG Length;                                                           //0x0
        UCHAR Initialized;                                                      //0x4
        VOID* SsHandle;                                                         //0x8
        struct _LIST_ENTRY InLoadOrderModuleList;                               //0xc
        struct _LIST_ENTRY InMemoryOrderModuleList;                             //0x14
        struct _LIST_ENTRY InInitializationOrderModuleList;                     //0x1c
        VOID* EntryInProgress;                                                  //0x24
        UCHAR ShutdownInProgress;                                               //0x28
        VOID* ShutdownThreadId;                                                 //0x2c
    };
    

分别代表 **模块加载顺序，模块在内存中的加载顺序以及模块初始化装载的顺序**  
`_LIST_ENTRY`的结构定义如下:

    
    
    typedef struct _LIST_ENTRY {
       struct _LIST_ENTRY *Flink;
       struct _LIST_ENTRY *Blink;
    } LIST_ENTRY, *PLIST_ENTRY, *RESTRICTED_POINTER PRLIST_ENTRY;
    

该图为对于这三个双向链表给出的解释:

![](https://p5.ssl.qhimg.com/t014b89c65c028c2e55.png)

每个双向链表都是指向进程装载的模块，结构中的每个指针，指向了一个`LDR_DATA_TABLE_ENTRY`的结构：

    
    
    struct _LDR_DATA_TABLE_ENTRY
    {
        struct _LIST_ENTRY InLoadOrderLinks;                                    //0x0
        struct _LIST_ENTRY InMemoryOrderLinks;                                  //0x8
        struct _LIST_ENTRY InInitializationOrderLinks;                          //0x10
        VOID* DllBase;                                                          //0x18 模块基址
        VOID* EntryPoint;                                                       //0x1c
        ULONG SizeOfImage;                                                      //0x20
        struct _UNICODE_STRING FullDllName;                                     //0x24 模块路径+名称
        struct _UNICODE_STRING BaseDllName;                                     //0x2c 模块名称
    ...
    };
    

因此在这里可以看到模块的名称以及DLL基址等信息

![](https://p5.ssl.qhimg.com/t019e9ac2dddd6437b0.png)

## 0x03 代码层面熟悉PEB的相关调用

关于如何得到偏移，微软内部函数已经提供了相关API来检索32位或者64位的PEB:

  * [__readgsqword](https://docs.microsoft.com/en-us/cpp/intrinsics/readgsbyte-readgsdword-readgsqword-readgsword?view=msvc-170&viewFallbackFrom=vs-2019)
  * [__readfsqword](https://docs.microsoft.com/en-us/cpp/intrinsics/readfsbyte-readfsdword-readfsqword-readfsword?view=msvc-170&viewFallbackFrom=vs-2019)

下面通过一段简单的代码可以得到关于Ntdll的相关信息:

    
    
    #include <iostream>
    #include "peb.h"
    int main()
    {
        PPEB Peb = (PPEB)__readgsqword(0x60); //PEB 可以通过x86_64:gs寄存器偏移96(0x60) x86:fs寄存器偏移0x48(0x30) 定位
        PLDR_MODULE pLoadModule;
        pLoadModule = (PLDR_MODULE)((PBYTE)Peb->LoaderData->InMemoryOrderModuleList.Flink->Flink - 0x10);
        printf("%ws\r\n", pLoadModule->FullDllName.Buffer);
    }
    

![](https://p5.ssl.qhimg.com/t01b719eaad3d7a522d.png)

在上述代码中我们首先通过位于0x60的指向GS寄存器的指针检索到当前进程的PEB，我们访问LDR结构体，并且并向前链接到第二个内存顺序模块

> 需要注意的是，在我们的正向链接中，我们从Flink中减去16字节，以确保我们正确对齐（这16字节对齐必须在32位和64位进程中都出现）

![](https://p3.ssl.qhimg.com/t01aaf0a9f3fb547edf.png)

这里减去0x10移动指针到结构体顶端，防止模块信息显示错误,否则将会:

![](https://p1.ssl.qhimg.com/t016a375b19e487c3e5.png)

大多数情况下NTDLL模块会是第二个内存模块，kernel32dll将会是第三个内存模块，在这里我们可以通过如下程序来遍历进程所有在内存中加载过的模块以及基址:

    
    
    #include <iostream>
    #include "peb.h"
    int main()
    {
        PPEB Peb = (PPEB)__readgsqword(0x60); //PEB 可以通过x86_64:gs寄存器偏移96(0x60) x86:fs寄存器偏移0x48(0x30) 定位
        PLDR_MODULE pLoadModule;
        pLoadModule = (PLDR_MODULE)((PBYTE)Peb->LoaderData->InMemoryOrderModuleList.Flink - 0x10);
        PLDR_MODULE pFirstLoadModule = (PLDR_MODULE)((PBYTE)Peb->LoaderData->InMemoryOrderModuleList.Flink - 0x10);
        do
        {
            printf("Module Name:%ws\r\nModule Base Address:%p\r\n\r\n", pLoadModule->FullDllName.Buffer,pLoadModule->BaseAddress);
            pLoadModule = (PLDR_MODULE)((PBYTE)pLoadModule->InMemoryOrderModuleList.Flink - 0x10);
        } while ((PLDR_MODULE)((PBYTE)pLoadModule->InMemoryOrderModuleList.Flink -0x10) != pFirstLoadModule);
    }
    

![](https://p5.ssl.qhimg.com/t019946f57a143a54e1.png)

掌握这一点后现在我们知道如何获取内存模块的基址，因此我们有能力遍历模块的导出地址表,这就涉及到通过该基址去遍历PE头文件从而获取导出地址表，可以将其分为四个步骤:

  * 1.获取每个模块的基地址
  * 2.获取`_IMAGE_DOS_HEADER`，并通过检查`IMAGE_DOS_SIGNATURE`来验证正确性
  * 3.遍历`_IMAGE_NT_HEADER`、`_IMAGE_FILE_HEADER`、`_IMAGE_OPTIONAL_HEADER`
  * 4.在`_IMAGE_OPTIONAL_HEADER`中找到导出地址表，并将类型转为`_IMAGE_EXPORT_DIRECTORY`

在获得导出表之前我们还需要知道PE文件头的详细数据结构:

    
    
    typedef struct _IMAGE_NT_HEADERS {
        DWORD Signature;                         //PE文件头标志 => 4字节
        IMAGE_FILE_HEADER FileHeader;             //标准PE头 => 20字节
        IMAGE_OPTIONAL_HEADER32 OptionalHeader; //扩展PE头 => 32位下224字节(0xE0) 64位下240字节(0xF0)
    } IMAGE_NT_HEADERS32, *PIMAGE_NT_HEADERS32;
    

因此当我们得到PE头时，便可以通过如下代码最终将`OptionalHeader`转为`IMAGE_EXPORT_DIRECTORY`得到最终的导出表:

    
    
    PBYTE ImageBase;
        PIMAGE_DOS_HEADER Dos = NULL;
        PIMAGE_NT_HEADERS Nt = NULL;
        PIMAGE_FILE_HEADER File = NULL;
        PIMAGE_OPTIONAL_HEADER Optional = NULL;
        PIMAGE_EXPORT_DIRECTORY ExportTable = NULL;
    
        PPEB Peb = (PPEB)__readgsqword(0x60);
        PLDR_MODULE pLoadModule;
        pLoadModule = (PLDR_MODULE)((PBYTE)Peb->LoaderData->InMemoryOrderModuleList.Flink - 0x10);
        ImageBase = (PBYTE)pLoadModule->BaseAddress;
        Dos = (PIMAGE_DOS_HEADER)ImageBase;
        if (Dos->e_magic != IMAGE_DOS_SIGNATURE)
            return 1;
        Nt = (PIMAGE_NT_HEADERS)((PBYTE)Dos + Dos->e_lfanew);
        File = (PIMAGE_FILE_HEADER)(ImageBase + (Dos->e_lfanew + sizeof(DWORD)));
        Optional = (PIMAGE_OPTIONAL_HEADER)((PBYTE)File + sizeof(IMAGE_FILE_HEADER));
        ExportTable = (PIMAGE_EXPORT_DIRECTORY)(ImageBase + Optional->DataDirectory[0].VirtualAddress);
    

当我们得到`NT_Header`时,由于PE头文件的数据结构已经给出，其前四个字节为一个DWORD类型的`Signature`，因此加上这四个字节就会得到`FileHeader`，然后在此基础上加上FileHeader数据结构所占大小最终得到`Optional`，只需要将其类型转为`_IMAGE_EXPORT_DIRECTORY`就得到了我们的导出地址表,再通过:

  * 1.FunctionNameAddressArray 一个包含函数名称的数组
  * 2.FunctionOrdinalAddressArray 充当函数寻址数组的索引
  * 3.FunctionAddressArray 一个包含函数地址的数组

可以实现遍历模块中的导出表的所有有名称导出函数:

    
    
    int GetPeHeader()
    {
        PBYTE ImageBase;
        PIMAGE_DOS_HEADER Dos = NULL;
        PIMAGE_NT_HEADERS Nt = NULL;
        PIMAGE_FILE_HEADER File = NULL;
        PIMAGE_OPTIONAL_HEADER Optional = NULL;
        PIMAGE_EXPORT_DIRECTORY ExportTable = NULL;
    
        PPEB Peb = (PPEB)__readgsqword(0x60);
        PLDR_MODULE pLoadModule;
        // NTDLL
        pLoadModule = (PLDR_MODULE)((PBYTE)Peb->LoaderData->InMemoryOrderModuleList.Flink->Flink - 0x10);
        ImageBase = (PBYTE)pLoadModule->BaseAddress;
    
        Dos = (PIMAGE_DOS_HEADER)ImageBase;
        if (Dos->e_magic != IMAGE_DOS_SIGNATURE)
            return 1;
        Nt = (PIMAGE_NT_HEADERS)((PBYTE)Dos + Dos->e_lfanew);
        File = (PIMAGE_FILE_HEADER)(ImageBase + (Dos->e_lfanew + sizeof(DWORD)));
        Optional = (PIMAGE_OPTIONAL_HEADER)((PBYTE)File + sizeof(IMAGE_FILE_HEADER));
        ExportTable = (PIMAGE_EXPORT_DIRECTORY)(ImageBase + Optional->DataDirectory[0].VirtualAddress);
    
        PDWORD pdwAddressOfFunctions = (PDWORD)((PBYTE)(ImageBase + ExportTable->AddressOfFunctions));
        PDWORD pdwAddressOfNames = (PDWORD)((PBYTE)ImageBase + ExportTable->AddressOfNames);
        PWORD pwAddressOfNameOrdinales = (PWORD)((PBYTE)ImageBase + ExportTable-> AddressOfNameOrdinals);
        for (WORD cx = 0; cx < ExportTable->NumberOfNames; cx++) 
        {
            PCHAR pczFunctionName = (PCHAR)((PBYTE)ImageBase + pdwAddressOfNames[cx]);
            PVOID pFunctionAddress = (PBYTE)ImageBase + pdwAddressOfFunctions[pwAddressOfNameOrdinales[cx]];
            printf("Function Name:%s\tFunction Address:%p\n", pczFunctionName, pFunctionAddress);
        }
    }
    

得到NTDLL的导出函数以及地址

![](https://p0.ssl.qhimg.com/t01d069327a91418912.png)

## 0x04 何为地狱之门

到这里就需要引入地狱之门的概念了，首先让我们观察正常的NTDLL的函数对应的汇编代码:

![](https://p3.ssl.qhimg.com/t012572101855778f20.png)

NTDLL再进入Ring0执行函数内核部分前将验证当前的线程执行环境是x64还是x86,通过对`ShareUserData+0x308`的后续测试说明了这一点。随后如果确定执行环境是基于x64则会通过`syscall`执行系统调用,否则会执行函数返回，而在此之前都会给eax寄存器一个系统调用号并且该调用号不同版本的Windows是不一样的:  
[https://j00ru.vexillium.org/syscalls/nt/64/](https://)可以对该号进行查询  
我们再来看一个被上钩的NTDLL的汇编:

![](https://p0.ssl.qhimg.com/t019d9d33963f5f7c7f.png)

`ZwMapViewOfSection`上的Hook是很明显的（jmp \<offset\>指令，而不是mov r10,
rcx）。而`ZwMapViewOfSection`的邻居`ZwSetInformationFile和NtAccessCheckAndAuditAlarm`是干净的，它们的系统调用号分别是0x27和0x29。

系统调用被定义为WORD类型（16位无符号整数），并存储在EAX寄存器中，并且实际上我们是能够动态获得系统调用号的,以`NtOpenProcess`为例:

![](https://p0.ssl.qhimg.com/t014741ec3e1cb4e0dc.png)

这也就是地狱之门的原理所在，通过直接读取进程第二个导入模块即NtDLL，解析结构然后遍历导出表，根据函数名Hash找到函数地址，将这个函数读取出来通过`0xb8`这个操作码来动态获取对应的系统调用号，从而绕过内存监控，在自己程序中执行了NTDLL的导出函数而不是直接通过`LoadLibrary`然后`GetProcAddress`

## 0x05 代码层面解析

现在我们通过作者给出的示例代码来逐步解析`hell's Gate`的实现过程  
在实现过程中需要定义一个与syscall相关联的数据结构:`_VX_TABLE_ENTRY`事实上每一个系统调用都需要分配这样一个结构,结构体定义如下:

    
    
    typedef struct _VX_TABLE_ENTRY {
     PVOID pAddress;
     DWORD64 dwHash;
     WORD wSystemCall;
    } VX_TABLE_ENTRY, * PVX_TABLE_ENTRY;
    

其中包括了 **指向内存模块的函数地址指针** ， **一个函数哈希** (后续通过Hash查找内存模块的函数)以及
**一个无符号16位的系统调用号**`wSysemCall`  
同时还定义了一个更大的数据结构`_VX_TABLE`用来包含每一个系统调用的函数:

    
    
    typedef struct _VX_TABLE {
     VX_TABLE_ENTRY NtAllocateVirtualMemory;
     VX_TABLE_ENTRY NtProtectVirtualMemory;
     VX_TABLE_ENTRY NtCreateThreadEx;
     VX_TABLE_ENTRY NtWaitForSingleObject;
    } VX_TABLE, * PVX_TABLE;
    

下面就需要通过PEB的相关结构来动态获取系统调用号和函数地址来填充刚刚定义的数据结构以便于自己实现系统调用，作者的思路是通过TIB(线程信息块)获取TEB然后在获取TEB的数据结构，这也是最常见的方式:

    
    
    #在Windows x64中，TEB的寄存器换做了GS寄存器，使用[GS:0x30]访问
    NtCurrentTeb();
    // x86
    __readfsqword(0x18);
    // x64
    __readgsqword(0x30);
    

因此我们获取PEB的方式就变为调用`__readgsqword`或者`__readfsdword`:

    
    
    PTEB pCurrentTeb = RtlGetThreadEnvironmentBlock();
    PPEB pCurrentPeb = pCurrentTeb->ProcessEnvironmentBlock;
    if (!pCurrentPeb || !pCurrentTeb || pCurrentPeb->OSMajorVersion != 0xA) {
     return 0x1;
    }
    PTEB RtlGetThreadEnvironmentBlock() {
    #if _WIN64
     return (PTEB)__readgsqword(0x30);
    #else
     return (PTEB)__readfsdword(0x16);
    #endif
    }
    # 最后还通过PEB的成员OSMajorVersion判断操作系统是否是Windows 10
    

之后的操作和前文我们实现遍历模块的导出函数是一致的，需要我们解析PE头然后找到EAT:

![](https://p4.ssl.qhimg.com/t01dc108c5a17b73c49.png)

成功获取EAT指针之后现在就需要将之前定义的数据结构填充，通过`GetVxTableEntry`函数填充`_VX_TABLE`:

    
    
    VX_TABLE Table = { 0 };
    Table.NtAllocateVirtualMemory.dwHash = 0xf5bd373480a6b89b;
    GetVxTableEntry(ImageBase, ExportTable, &Table.NtAllocateVirtualMemory);
    
    Table.NtCreateThreadEx.dwHash = 0x64dc7db288c5015f;
    GetVxTableEntry(ImageBase, ExportTable, &Table.NtCreateThreadEx);
    Table.NtProtectVirtualMemory.dwHash = 0x858bcb1046fb6a37;
    GetVxTableEntry(ImageBase, ExportTable, &Table.NtProtectVirtualMemory);
    
    Table.NtWaitForSingleObject.dwHash = 0xc6a2fa174e551bcb;
    GetVxTableEntry(ImageBase, ExportTable, &Table.NtWaitForSingleObject);
    

在实例代码中主要是实现了Ntdll中的四个函数，分别如上所示，因此需要知道这四个函数的Hash以及四个`_VX_TABLE_ENTRY`结构体，`Hell's
gate`最为关键的处理函数也就包含在`GetVxTableEntry`之中:

    
    
    BOOL GetVxTableEntry(PVOID pModuleBase, PIMAGE_EXPORT_DIRECTORY ExporTable, PVX_TABLE_ENTRY pVxTableEntry)
    {
        PDWORD pdwAddressOfFunctions = (PDWORD)((PBYTE)pModuleBase + ExporTable-> AddressOfFunctions);
        PDWORD pdwAddressOfNames = (PDWORD)((PBYTE)pModuleBase + ExporTable->AddressOfNames);
        PWORD pwAddressOfNameOrdinales = (PWORD)((PBYTE)pModuleBase + ExporTable -> AddressOfNameOrdinals);
        for (WORD cx = 0; cx < ExporTable->NumberOfNames; cx++)
        {
            PCHAR  pczFunctionName = (PCHAR)((PBYTE)pModuleBase + pdwAddressOfNames[cx]);
            PVOID pFunctionAddress = (PBYTE)pModuleBase + pdwAddressOfFunctions[pwAddressOfNameOrdinales[cx]];
            if (djb2((PBYTE)pczFunctionName) == pVxTableEntry->dwHash) 
            {
                printf("[+]Function:%s Matched\n", pczFunctionName);
                pVxTableEntry->pAddress = pFunctionAddress;
                // 定位mov eax的操作码
                if (*((PBYTE)pFunctionAddress + 3) == 0xb8) 
                {
                    BYTE high = *((PBYTE)pFunctionAddress + 5);
                    BYTE low = *((PBYTE)pFunctionAddress + 4);
                    pVxTableEntry->wSystemCall = (high << 8) | low;
                    break;
                }
            }
        }
    }
    

首先遍历导出表的函数，通过djb2算法计算每一个函数哈希与我们想要实现的函数哈希比较，如果相同则填充函数地址，并且验证函数第三步以寻找汇编代码`0xb8`即`mov
eax`是否存在，因为系统调用号是一个WORD类型，也就是两个字节并且是小端存储，因此通过高低位转换的方式最终动态获得系统调用号填充到函数结构体`pVxTableEntry`中

    
    
    BYTE high = *((PBYTE)pFunctionAddress + 5);
     BYTE low = *((PBYTE)pFunctionAddress + 4);
     pVxTableEntry->wSystemCall = (high << 8) | low;
    

最后我们便可以通过这样一段宏汇编代码(MASM)来定义执行通过系统调用号调用NT函数的函数:

    
    
     wSystemCall DWORD 0h
    .code
     HellsGate PROC
     mov wSystemCall, 0h
     mov wSystemCall, ecx
     ret
     HellsGate ENDP
     HellDescent PROC
     mov r10, rcx
     mov eax, wSystemCall
     syscall
     ret
     HellDescent ENDP
    end
    

第一个函数HellsGate用来设置对应Nt函数的系统调用号，第二个函数直接模拟系统调用来调用对应系统调用号的函数,过程和下图`ZwSetInformationFile`的汇编指令是一样的，省略了判断线程执行环境是x64还是x86:

![](https://p0.ssl.qhimg.com/t011c86c4e518410475.png)

因此当我们想要调用Nt函数时，并且在已经得到PE头文件基址和EAT后我们可以先对之前定义的数据结构进行填充:

    
    
    VX_TABLE Table = { 0 };
        Table.NtAllocateVirtualMemory.dwHash = 0xf5bd373480a6b89b;
        if (!GetVxTableEntry(ImageBase, ExportTable, &Table.NtAllocateVirtualMemory))
        {
            printf("[-]GetVxTableEntry Failed!\n");
            return -1;
        }
        Table.NtCreateThreadEx.dwHash = 0x64dc7db288c5015f;
        if (!GetVxTableEntry(ImageBase, ExportTable, &Table.NtCreateThreadEx))
        {
            printf("[-]GetVxTableEntry Failed!\n");
            return -1;
        }
        Table.NtProtectVirtualMemory.dwHash = 0x858bcb1046fb6a37;
        if (!GetVxTableEntry(ImageBase, ExportTable, &Table.NtProtectVirtualMemory))
        {
            printf("[-]GetVxTableEntry Failed!\n");
            return -1;
        }
        Table.NtWaitForSingleObject.dwHash = 0xc6a2fa174e551bcb;
        if (!GetVxTableEntry(ImageBase, ExportTable, &Table.NtWaitForSingleObject))
        {
            printf("[-]GetVxTableEntry Failed!\n");
            return -1;
        }
    

这样每一个我们想调用的Nt函数都有唯一的`VT_TABLE_ENTRY`结构体，其中包含该函数对应的系统调用号、函数地址指针和函数哈希，随后我们通过定义的汇编函数进行调用:

![](https://p2.ssl.qhimg.com/t011e08687794c2dc50.png)

汇编如下:

![](https://p3.ssl.qhimg.com/t01ad64f8c823107c8f.png)

这样我们便能够模拟引入Ntdll调用Nt函数的方式，也就是调用`Native API`而不是`Win API`来绕过Hooks

## 0x06 局限以及解决方案

###  1.光环之门 Halo’s Gate

地狱之门这项技术通过访问PEB中已经加载到内存的模块NTDLL，
**从模块中提取所述的系统调用号和函数地址指针并将它们保存在专用内存表中，然后用于直接调用系统 API。实现动态检索系统调用号**
，非常之巧妙，但仍存在一定局限性:

Hell’s
Gate的一个最大的局限是它所访问内存中的NTDLL也必须是默认的或者说是未经修改的，因为如果本身NTDLL已经被修改过，或者被Hook过则函数汇编操作码就不会是`0xb8`，对应着`mov
eax`，而可能是`0xE9`,对应着`jmp`  
前文这张图已经体现的很明显

![](https://p0.ssl.qhimg.com/t01b436c33c9392a2ec.png)

因此当我们需要调用的NT函数已经被AV/EDR所Hook，那我们就无法通过地狱之门来动态获取它的系统调用号

因此出现了光环之门(Halo’s Gate)这项技术，准确的来说这种技术只是地狱之门的一个补丁，它源于一个勒索软件使用的脱钩技术:  
<https://blog.vincss.net/2020/03/re011-unpack-crypter-cua-malware-netwire-bang-x64dbg.html>  
从上图我们可以看到，`ZwMapViewOfSection`已经被Hook，而它的邻函数`ZwSetInformationFile和NtAccessCheckAndAuditAlarm`都没有被Hook，并且邻函数的系统调用号也是临接的，这给了我们一个这样的思路:

  * 为了重构`ZwMapViewOfSection`的系统调用号只需查看邻函数的系统调用号并进行相应调整即可，如果邻函数同样被Hook，则检查邻函数的邻函数，以此类推

在`Doge-Gabh`中已经集成了`Halo's Gate`，我们通过源码来看一下实现过程:

![](https://p5.ssl.qhimg.com/t011d0c3654fe84c0b1.png)

从windbg中也可以看到:

![](https://p2.ssl.qhimg.com/t013f07cc924b671e3e.png)

前四个字节分别为`4c8bd1b8`且后两个字节为00，中间两个字节对应的系统调用号

当出现被Hook的Nt函数时便采取向周围查询的方式:

![](https://p2.ssl.qhimg.com/t011965cb4103bfbdbb.png)

因此通过`Halo's Gate`使得`Hell's Gate`能最大程度的发挥和实现，从而实现敏感函数的脱钩处理

###  2.按系统调用地址排序

这里还介绍一种更加方便简单和迅速的方法来发现SSN(syscall
number),这种方法不需要unhook，不需要手动从代码存根中读取，也不需要加载NTDLL新副本，可以将它理解成为光环之门的延伸，试想当上下的邻函数都被Hook时，光环之门的做法是继续递归，在不断的寻找没有被Hook的邻函数，而在这里假设一种最坏的情况是所有的邻函数(指Nt系函数)都被Hook时，那最后将会向上递归到`SSN=0`的Nt函数，
**在此之前我们需要知道了解几个知识:**

  * 1.实际上所有的Zw函数和Nt同名函数实际上是等价的  

  * 2.系统调用号实际上是和Zw函数按照地址顺序的排列是一样的

因此我们可以就获得了这样一种获取系统调用索引的简单方法,即枚举所有Zw*函数，记录函数名称和地址，然后按地址对它们进行排序（使用升序排列），这样每一个Zw函数对应的SSN就是在升序排列中对应的索引值:

于是当我将所有的Zw系函数记录，并且将其以地址为键名进行升序排列，输出前三个函数时我们可以发现:

![](https://p5.ssl.qhimg.com/t0185e009abd09f9c93.png)

上图为所有Zw函数按照地址顺序排列后的前三个，我们在从windbg中查看本地对应的三个Nt函数的SSN:

![](https://p2.ssl.qhimg.com/t01449e75cd7ddbbf03.png)

和升序排列后对应的索引顺序是完全一致的，
**因此我们就只需要遍历所有Zw函数，记录其函数名和函数地址，最后将其按照函数地址升序排列后，每个函数的SSN就是其对应的排列顺序**

贴一个利用Map实现的获取SSN的代码实现:

    
    
    void GetSSN()
    {
        std::map<int, string> Nt_Table;
        PBYTE ImageBase;
        PIMAGE_DOS_HEADER Dos = NULL;
        PIMAGE_NT_HEADERS Nt = NULL;
        PIMAGE_FILE_HEADER File = NULL;
        PIMAGE_OPTIONAL_HEADER Optional = NULL;
        PIMAGE_EXPORT_DIRECTORY ExportTable = NULL;
    
        PPEB Peb = (PPEB)__readgsqword(0x60);
        PLDR_MODULE pLoadModule;
        // NTDLL
        pLoadModule = (PLDR_MODULE)((PBYTE)Peb->LoaderData->InMemoryOrderModuleList.Flink->Flink - 0x10);
        ImageBase = (PBYTE)pLoadModule->BaseAddress;
    
        Dos = (PIMAGE_DOS_HEADER)ImageBase;
        if (Dos->e_magic != IMAGE_DOS_SIGNATURE)
            return 1;
        Nt = (PIMAGE_NT_HEADERS)((PBYTE)Dos + Dos->e_lfanew);
        File = (PIMAGE_FILE_HEADER)(ImageBase + (Dos->e_lfanew + sizeof(DWORD)));
        Optional = (PIMAGE_OPTIONAL_HEADER)((PBYTE)File + sizeof(IMAGE_FILE_HEADER));
        ExportTable = (PIMAGE_EXPORT_DIRECTORY)(ImageBase + Optional->DataDirectory[0].VirtualAddress);
    
        PDWORD pdwAddressOfFunctions = (PDWORD)((PBYTE)(ImageBase + ExportTable->AddressOfFunctions));
        PDWORD pdwAddressOfNames = (PDWORD)((PBYTE)ImageBase + ExportTable->AddressOfNames);
        PWORD pwAddressOfNameOrdinales = (PWORD)((PBYTE)ImageBase + ExportTable->AddressOfNameOrdinals);
        for (WORD cx = 0; cx < ExportTable->NumberOfNames; cx++)
        {
            PCHAR pczFunctionName = (PCHAR)((PBYTE)ImageBase + pdwAddressOfNames[cx]);
            PVOID pFunctionAddress = (PBYTE)ImageBase + pdwAddressOfFunctions[pwAddressOfNameOrdinales[cx]];
            if (strncmp((char*)pczFunctionName, "Zw",2) == 0) {
               // printf("Function Name:%s\tFunction Address:%p\n", pczFunctionName, pFunctionAddress);
                Nt_Table[(int)pFunctionAddress] = (string)pczFunctionName;
            }
        }
        int index = 0;
        for (std::map<int, string>::iterator iter = Nt_Table.begin(); iter != Nt_Table.end(); ++iter) {
            cout << "index:" << index  << ' ' << iter->second << endl;
            index += 1;
        }
    }
    

同样可以实现获取Nt系函数的SSN,排列顺序索引和SSN的值是完全对应的:

![](https://p0.ssl.qhimg.com/t014bdbd62bbfe9dfc8.png)

以上两种方式都是代替Hell’s Gate获取SSN的不错实现方式，在这里抛砖引玉做一个简答介绍，所述之处有错还请谅解

* * *

**参考文章:**  
<https://github.com/am0nsec/HellsGate/blob/master/hells-gate.pdf>  
<https://www.kn0sky.com/?p=69>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Crispr** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/267345](/post/id/267345)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [windows安全](/tag/windows安全)

 **+1** __9赞

 __收藏

![](https://p4.ssl.qhimg.com/t01f727a088f341ab8f.png) Crispr

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

