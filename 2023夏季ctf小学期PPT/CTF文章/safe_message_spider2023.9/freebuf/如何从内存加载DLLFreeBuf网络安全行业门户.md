**本教程介绍了一种技术，该技术可如何从内存中加载动态链接库(DLL)。**

 **文章结尾将给出github地址**

##  Windows可执行文件– PE格式

首先我们先看看pe的结构

DOS headerDOS stub  
---  
PE header  
Section header  
Section 1  
Section 2  
. . .  
Section n  
  
下面给出的所有结构都可以在头文件winnt.h中找到。

##  DOS header

DOS header 仅用于向后兼容。它位于DOS stub 之前。

Microsoft定义DOS标头如下：

    
    
    typedef struct _IMAGE_DOS_HEADER {// DOS .EXE标头
        WORD e_magic; //Magic number
        字e_cblp; //文件最后一页上的字节
        字e_cp; //文件中的页面
        WORD e_crlc; //Relocations
        字e_cparhdr; //段落中header的大小
        字e_minalloc; //所需的最少额外段落
        字e_maxalloc; //所需的最大额外段落数
        WORD e_ss; //初始（相对）SS值
        WORD e_sp; //初始SP值
        WORD e_csum; //校验和
        WORD e_ip; //初始IP值
        WORD e_cs; //初始（相对）CS值
        字e_lfarlc; //重定位表的文件地址
        WORD e_ovno; //覆盖数
        WORD e_res [4]; //保留字
        WORD e_oemid; // OEM标识符（用于e_oeminfo）
        WORD e_oeminfo; // OEM信息；特定于e_oemid
        字e_res2 [10]; //保留字
        LONG e_lfanew; //新的exe标头的文件地址
      } IMAGE_DOS_HEADER，* PIMAGE_DOS_HEADER;

##  PE header

PE 头包含有关可执行文件内不同部分的信息，这些信息用于存储代码和数据或定义从其他库导入或此库提供的导出。

它的定义如下：

    
    
    typedef struct _IMAGE_NT_HEADERS {
        DWORD签名；
        IMAGE_FILE_HEADER FileHeader;
        IMAGE_OPTIONAL_HEADER32可选标题；
    } IMAGE_NT_HEADERS32，* PIMAGE_NT_HEADERS32;

该FileHeader里描述的physical 文件的格式，如目录符号等信息：

    
    
    typedef struct _IMAGE_FILE_HEADER {
        WORD    Machine;
        WORD NumberOfSections;
        DWORD TimeDateStamp;
        DWORD PointerToSymbolTable;
        DWORD NumberOfSymbols;
        WORD SizeOfOptionalHeader;
        WORD    Characteristics;
    } IMAGE_FILE_HEADER，* PIMAGE_FILE_HEADER;

该OptionalHeader里包含的信息逻辑库的格式，包括需要的操作系统版本，内存需求和切入点：

    
    
    typedef struct _IMAGE_OPTIONAL_HEADER {
        //
        //标准字段。
        //
    WORD    Magic;
        BYTE    MajorLinkerVersion;
        BYTE    MinorLinkerVersion;
        DWORD   SizeOfCode;
        DWORD   SizeOfInitializedData;
        DWORD   SizeOfUninitializedData;
        DWORD   AddressOfEntryPoint;
        DWORD   BaseOfCode;
        DWORD   BaseOfData;
        //
        // NT其他字段。
        //
        DWORD   ImageBase;
        DWORD   SectionAlignment;
        DWORD   FileAlignment;
        WORD    MajorOperatingSystemVersion;
        WORD    MinorOperatingSystemVersion;
        WORD    MajorImageVersion;
        WORD    MinorImageVersion;
        WORD    MajorSubsystemVersion;
        WORD    MinorSubsystemVersion;
        DWORD   Win32VersionValue;
        DWORD   SizeOfImage;
        DWORD   SizeOfHeaders;
        DWORD   CheckSum;
        WORD    Subsystem;
        WORD    DllCharacteristics;
        DWORD   SizeOfStackReserve;
        DWORD   SizeOfStackCommit;
        DWORD   SizeOfHeapReserve;
        DWORD   SizeOfHeapCommit;
        DWORD   LoaderFlags;
        DWORD   NumberOfRvaAndSizes;
        IMAGE_DATA_DIRECTORY DataDirectory[IMAGE_NUMBEROF_DIRECTORY_ENTRIES];
    } IMAGE_OPTIONAL_HEADER32，* PIMAGE_OPTIONAL_HEADER32;

所述DataDirectory目录包含16（IMAGE_NUMBEROF_DIRECTORY_ENTRIES定义库的逻辑组件）条目：

Index  |  描述  
---|---  
0  |  导出功能  
1  |  导入功能  
2  |  资源资源  
3  |  异常信息  
4  |  安全信息  
5  |  基地搬迁表  
6  |  调试信息  
7  |  特定于架构的数据  
8  |  全局指针  
9  |  线程本地存储  
10  |  加载配置  
11  |  绑定进口  
12  |  导入地址表  
13  |  延迟加载导入  
14  |  COM运行时描述符  
  
对于导入DLL，我们仅需要描述导入和基本重定位表的条目。为了提供对导出功能的访问，需要导出条目。

##  Section header

段头存储在PE头中的OptionalHeader结构之后。Microsoft提供了宏IMAGE_FIRST_SECTION以基于PE标头获得起始地址。

实际上，节头是文件中每个节的信息列表：

    
    
    typedef struct _IMAGE_SECTION_HEADER {
        BYTE    Name[IMAGE_SIZEOF_SHORT_NAME];
        union {
                DWORD   PhysicalAddress;
                DWORD   VirtualSize;
        } Misc;
        DWORD   VirtualAddress;
        DWORD   SizeOfRawData;
        DWORD   PointerToRawData;
        DWORD   PointerToRelocations;
        DWORD   PointerToLinenumbers;
        WORD    NumberOfRelocations;
        WORD    NumberOfLinenumbers;
        DWORD   Characteristics;
    } IMAGE_SECTION_HEADER, *PIMAGE_SECTION_HEADER;

一个部分可以包含代码，数据，重定位信息，资源，导出或导入定义等。

##  加载库

要模拟PE加载程序，我们必须首先了解，将文件加载到内存并准备结构以便从其他程序中调用它们是必需的。

在发出API调用LoadLibrary时，Windows基本上执行以下任务：

> 1.打开给定的文件并检查DOS和PE标头。  
>
>
>
> 2.尝试在位置PEHeader.OptionalHeader.ImageBase处分配PEHeader.OptionalHeader.SizeOfImage字节的内存块。
>
>
> 3.解析节标题并将节复制到其地址。相对于已分配内存块的基址的每个节的目标地址存储在IMAGE_SECTION_HEADER结构的VirtualAddress属性中。
>
> 4.如果分配的内存块与ImageBase不同，则必须调整代码和/或数据部分中的各种引用。这称为Base relocation.。
>
> 5.必须通过加载相应的库来解决所需的库导入。
>
>
> 6.必须根据部分的特性来保护不同部分的存储区域。有些部分标记为可丢弃，因此此时可以安全释放。这些部分通常包含仅在导入期间需要的临时数据，例如基本重定位的信息。
>
> 7.现在，库已完全加载。必须通过使用标志DLL_PROCESS_ATTACH调用入口点来对此进行通知。

在以下段落中，将描述每个步骤。

##  分配内存

该库所需的所有内存必须使用VirtualAlloc保留/分配，因为Windows提供了保护这些内存块的功能。这是限制访问存储器所必需的，例如阻止对代码或常量数据的写访问。

OptionalHeader结构定义该库所需的内存块的大小。如果可能，必须在ImageBase指定的地址处保留它：

    
    
    memory = VirtualAlloc((LPVOID)(PEHeader->OptionalHeader.ImageBase),
        PEHeader->OptionalHeader.SizeOfImage,
        MEM_RESERVE,
        PAGE_READWRITE);

如果保留的内存与ImageBase中指定的地址不同，则必须执行下面的基本重定位。

##  复制sections

保留内存后，即可将文件内容复制到系统中。必须对section header 进行评估，以确定文件中的位置和内存中的目标区域。

在复制数据之前，必须先提交内存块：

    
    
    dest = VirtualAlloc(baseAddress + section->VirtualAddress,
        section->SizeOfRawData,
        MEM_COMMIT,
        PAGE_READWRITE);

##  Base relocation

库的代码/数据部分中的所有内存地址都相对于ImageBase在OptionalHeader中定义的地址进行存储。如果无法将库导入到该内存地址，则必须对引用进行调整=>
relocated。文件格式通过在基本重定位表中存储有关所有这些引用的信息来帮助实现此目的，这些信息可在OptionalHeader中的DataDirectory的目录条目5中找到。

该表由一系列这种结构组成

    
    
    typedef struct _IMAGE_BASE_RELOCATION {
        DWORD   VirtualAddress;
        DWORD   SizeOfBlock;
    } IMAGE_BASE_RELOCATION;

它包含（SizeOfBlock – IMAGE_SIZEOF_BASE_RELOCATION）/
2个条目，每个条目16位。高4位定义重定位的类型，低12位定义相对于VirtualAddress的偏移量。

似乎在DLL中使用的唯一类型是

> IMAGE_REL_BASED_ABSOLUTE
>
> 用于填充。
>
> IMAGE_REL_BASED_HIGHLOW
>
> 将ImageBase和分配的内存块之间的增量添加到在偏移处找到的32位。

##  解决导入部分

OptionalHeader中DataDirectory的目录条目1指定要从中导入符号的库列表。此列表中的每个条目定义如下：

    
    
    typedef struct _IMAGE_IMPORT_DESCRIPTOR {
        union {
            DWORD   Characteristics;            // 0 for terminating null import descriptor
            DWORD   OriginalFirstThunk;         // RVA to original unbound IAT (PIMAGE_THUNK_DATA)
        };
        DWORD   TimeDateStamp;                  // 0 if not bound,
                                                // -1 if bound, and real date\time stamp
                                                //     in IMAGE_DIRECTORY_ENTRY_BOUND_IMPORT (new BIND)
                                                // O.W. date/time stamp of DLL bound to (Old BIND)
        DWORD   ForwarderChain;                 // -1 if no forwarders
        DWORD   Name;
        DWORD   FirstThunk;                     // RVA to IAT (if bound this IAT has actual addresses)
    } IMAGE_IMPORT_DESCRIPTOR;

该名条目描述偏移到库的名称（例如的空值终止字符串KERNEL32.DLL）。该OriginalFirstThunk条目指向的函数名的引用列表从外部库中导入。FirstThunk指向地址列表，该地址列表中包含指向导入符号的指针。

解决导入问题时，我们浏览两个列表，将名称定义的函数导入第一个列表，并将指向符号的指针存储在第二个列表中：

    
    
    nameRef = (DWORD *)(baseAddress + importDesc->OriginalFirstThunk);
    symbolRef = (DWORD *)(baseAddress + importDesc->FirstThunk);
    for (; *nameRef; nameRef++, symbolRef++)
    {
        PIMAGE_IMPORT_BY_NAME thunkData = (PIMAGE_IMPORT_BY_NAME)(codeBase + *nameRef);
        *symbolRef = (DWORD)GetProcAddress(handle, (LPCSTR)&thunkData->Name);
        if (*funcRef == 0)
        {
            handleImportError();
            return;
        }
    }

##  内存保护

每个部分的“ 特征”条目中都指定了权限标志。这些标志可以是以下之一或组合

> IMAGE_SCN_MEM_EXECUTE
>
> 本节包含可以执行的数据。
>
> IMAGE_SCN_MEM_READ
>
> 本节包含可读数据。
>
> IMAGE_SCN_MEM_WRITE
>
> 本节包含可写的数据。

这些标志必须映射到保护标志

> PAGE_NOACCESS
>
> PAGE_WRITECOPY
>
> PAGE_READONLY
>
> PAGE_READWRITE
>
> PAGE_EXECUTE
>
> PAGE_EXECUTE_WRITECOPY
>
> PAGE_EXECUTE_READ
>
> PAGE_EXECUTE_READWRITE

现在，可以使用函数VirtualProtect限制对内存的访问。如果程序尝试以未经授权的方式访问它，则Windows会引发异常。

除了上面的部分标志之外，还可以添加以下内容：

> IMAGE_SCN_MEM_DISCARDABLE
>
> 导入后可以释放此部分中的数据。通常，这是为重定位数据指定的。
>
> IMAGE_SCN_MEM_NOT_CACHED
>
> Windows不得缓存此部分中的数据。将位标志PAGE_NOCACHE添加到上面的保护标志中。

##  Notify library

最后要做的是调用DLL入口点（由AddressOfEntryPoint定义），并因此通知库有关附加到进程的信息。

入口点的功能定义为

    
    
    typedef BOOL (WINAPI *DllEntryProc)(HINSTANCE hinstDLL, DWORD fdwReason, LPVOID lpReserved);

所以我们最后需要执行的代码是

    
    
    DllEntryProc entry = (DllEntryProc)(baseAddress + PEHeader->OptionalHeader.AddressOfEntryPoint);
    (*entry)((HINSTANCE)baseAddress, DLL_PROCESS_ATTACH, 0);

之后，我们可以像使用任何普通库一样使用导出的函数。

##  导出功能

如果要访问库导出的函数，则需要找到符号的入口点，即要调用的函数的名称。

OptionalHeader中DataDirectory的目录条目0包含有关导出函数的信息。它的定义如下：

    
    
    typedef struct _IMAGE_EXPORT_DIRECTORY {
        DWORD   Characteristics;
        DWORD   TimeDateStamp;
        WORD    MajorVersion;
        WORD    MinorVersion;
        DWORD   Name;
        DWORD   Base;
        DWORD   NumberOfFunctions;
        DWORD   NumberOfNames;
        DWORD   AddressOfFunctions;     // RVA from base of image
        DWORD   AddressOfNames;         // RVA from base of image
        DWORD   AddressOfNameOrdinals;  // RVA from base of image
    } IMAGE_EXPORT_DIRECTORY, *PIMAGE_EXPORT_DIRECTORY;

首先要做的是将函数名称映射到导出符号的序号。因此，只需并行遍历AddressOfNames和AddressOfNameOrdinals定义的数组，直到找到所需的名称。

现在，您可以使用序号通过评估AddressOfFunctions数组的第n个元素来读取地址。

##  释放

要释放自定义加载的库，请执行以下步骤

调用入口点以通知库有关分离的信息：

    
    
    DllEntryProc entry = (DllEntryProc)(baseAddress + PEHeader->OptionalHeader.AddressOfEntryPoint);
    (*entry)((HINSTANCE)baseAddress, DLL_PROCESS_ATTACH, 0);

用于解析导入的免费外部库。

释放已分配的内存。

##  内存模块

MemoryModule是一个C库，可用于从内存加载DLL。

该接口与加载库的标准方法非常相似：

    
    
    typedef void *HMEMORYMODULE;
    HMEMORYMODULE MemoryLoadLibrary(const void *);
    FARPROC MemoryGetProcAddress(HMEMORYMODULE, const char *);
    void MemoryFreeLibrary(HMEMORYMODULE);

##  github

> <http://github.com/fancycode/MemoryModule>

***参考来源：[joachim](https://www.joachim-bauch.de/tutorials/loading-a-dll-from-memory/)，FB小编周大涛编译，转载请注明来自FreeBuf.COM**

