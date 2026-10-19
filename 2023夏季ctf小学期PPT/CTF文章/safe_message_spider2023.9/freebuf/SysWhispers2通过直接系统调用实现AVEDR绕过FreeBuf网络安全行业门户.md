![](https://image.3001.net/images/20210126/1611652066_600fdbe248273aa0fb798.png!small)

## SysWhispers2

SysWhispers2可以生成能够进行直接系统调用的Heder/ASM文件植入来帮助广大研究人员实现AV/EDR绕过。

当前的SysWhispers2支持所有的核心系统调用，并且在该项目的example-output/目录下提供了预生成的样本文件。

## SysWhispers1和SysWhispers2之间的区别

它的用法与[
_SysWhispers1_](https://github.com/jthuraisamy/SysWhispers)几乎相同，但现在我们无需指定要支持哪些版本的Windows。这两个版本之间的大多数改变都是用户不可见的，并且不再依赖于[
_@j00ru_](https://twitter.com/j00ru)的[
_系统调用表_](https://github.com/j00ru/windows-syscalls)，而使用的是[
_@modexpblog_](https://twitter.com/modexpblog)推广的“[
_按系统调用地址排序_](https://www.mdsec.co.uk/2020/12/bypassing-user-mode-hooks-and-direct-invocation-of-system-calls-for-red-teams/)”技术，这将大大减少系统调用存根的大小。

SysWhispers2中的具体实现是基于@modexpblog代码的变种版本，其中的一个区别在于函数名哈希在每一代上都是随机的。[
_@ElephantSe4l_](https://twitter.com/ElephantSe4l)之前也[
_发布_](https://www.crummie5.club/freshycalls/)过这种技术，并基于C++17[
_实现_](https://github.com/crummie5/FreshyCalls)了类似的功能，值得一看。

原来的SysWhispers存储库仍然可以访问，但将来可能会被弃用。

## 技术介绍

各种安全产品会在用户模式API函数中放置钩子，这就允许它们将执行数据流重定向到它们的引擎并检测可疑行为。ntdll.dll中能够执行系统调用的函数仅由几个汇编指令组成，因此我们可以在自己的移植程序中重新实现它们以绕过这些安全产品设置的钩子。

在SysWhispers的帮助下，红队研究人员可以在核心内核映像（ntoskrnl.exe）中针对任何系统调用生成Header/ASM文件，Header中还会包含必要的类型定义。

## 工具安装

广大研究人员可以使用下列命令将该项目源码克隆至本地，并完成工具的安装和配置：

    
    
    > git clone https://github.com/jthuraisamy/SysWhispers2.git
    
    > cd SysWhispers2
    
    > py .\syswhispers.py --help

### 工具使用

 **命令行：**

    
    
    # 针对所有支持的Windows操作系统版本导出所有兼容的函数功能（具体请查看example-output/目录）
    
    py .\syswhispers.py --preset all -o syscalls_all
    
     
    
    # 导出常见函数
    
    py .\syswhispers.py --preset common -o syscalls_common
    
     
    
    # 导出兼容所有版本的NtProtectVirtualMemory和NtWriteVirtualMemory
    
    py .\syswhispers.py --functions NtProtectVirtualMemory,NtWriteVirtualMemory -o syscalls_mem

 **脚本输出**

    
    
    PS C:\Projects\SysWhispers2> py .\syswhispers.py --preset common --out-file syscalls_common
    
     
    
                      .                         ,--.
    
    ,-. . . ,-. . , , |-. o ,-. ,-. ,-. ,-. ,-.    /
    
    `-. | | `-. |/|/  | | | `-. | | |-' |   `-. ,-'  
    
    `-' `-| `-' ' '   ' ' ' `-' |-' `-' '   `-' `---    
         /|                     |  @Jackson_T                 
    
        `-'                     '  @modexpblog, 2021
    
     
    
    SysWhispers2: Why call the kernel when you can whisper?
    
     
    
    Common functions selected.
    
     
    
    Complete! Files written to:
    
            syscalls_common.h
    
            syscalls_common.c
    
            syscalls_common_stubs.asm

## CreateRemoteThread DLL注入样例

    
    
    py .\syswhispers.py -f NtAllocateVirtualMemory,NtWriteVirtualMemory,NtCreateThreadEx -o syscalls
    
    
    #include <Windows.h>
    
     
    
    void InjectDll(const HANDLE hProcess, const char* dllPath)
    
    {
    
        LPVOID lpBaseAddress = VirtualAllocEx(hProcess, NULL, strlen(dllPath), MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
    
        LPVOID lpStartAddress = GetProcAddress(GetModuleHandle(L"kernel32.dll"), "LoadLibraryA");
    
     
    
        WriteProcessMemory(hProcess, lpBaseAddress, dllPath, strlen(dllPath), nullptr);
    
        CreateRemoteThread(hProcess, nullptr, 0, (LPTHREAD_START_ROUTINE)lpStartAddress, lpBaseAddress, 0, nullptr);
    
    }
    
    
    #include <Windows.h>
    
    #include "syscalls.h" // Import the generated header.
    
     
    
    void InjectDll(const HANDLE hProcess, const char* dllPath)
    
    {
    
        HANDLE hThread = NULL;
    
        LPVOID lpAllocationStart = nullptr;
    
        SIZE_T szAllocationSize = strlen(dllPath);
    
        LPVOID lpStartAddress = GetProcAddress(GetModuleHandle(L"kernel32.dll"), "LoadLibraryA");
    
     
    
        NtAllocateVirtualMemory(hProcess, &lpAllocationStart, 0, (PULONG)&szAllocationSize, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
    
        NtWriteVirtualMemory(hProcess, lpAllocationStart, (PVOID)dllPath, strlen(dllPath), nullptr);
    
        NtCreateThreadEx(&hThread, GENERIC_EXECUTE, NULL, hProcess, lpStartAddress, lpAllocationStart, FALSE, 0, 0, 0, nullptr);
    
    }

## 常见函数

使用--preset common选项将会使用下列函数创建一个Header/ASM对：

    
    
    NtCreateProcess (CreateProcess)
    
    NtCreateThreadEx (CreateRemoteThread)
    
    NtOpenProcess (OpenProcess)
    
    NtOpenThread (OpenThread)
    
    NtSuspendProcess
    
    NtSuspendThread (SuspendThread)
    
    NtResumeProcess
    
    NtResumeThread (ResumeThread)
    
    NtGetContextThread (GetThreadContext)
    
    NtSetContextThread (SetThreadContext)
    
    NtClose (CloseHandle)
    
    NtReadVirtualMemory (ReadProcessMemory)
    
    NtWriteVirtualMemory (WriteProcessMemory)
    
    NtAllocateVirtualMemory (VirtualAllocEx)
    
    NtProtectVirtualMemory (VirtualProtectEx)
    
    NtFreeVirtualMemory (VirtualFreeEx)
    
    NtQuerySystemInformation (GetSystemInfo)
    
    NtQueryDirectoryFile
    
    NtQueryInformationFile
    
    NtQueryInformationProcess
    
    NtQueryInformationThread
    
    NtCreateSection (CreateFileMapping)
    
    NtOpenSection
    
    NtMapViewOfSection
    
    NtUnmapViewOfSection
    
    NtAdjustPrivilegesToken (AdjustTokenPrivileges)
    
    NtDeviceIoControlFile (DeviceIoControl)
    
    NtQueueApcThread (QueueUserAPC)
    
    NtWaitForMultipleObjects (WaitForMultipleObjectsEx)

## 导入Visual Studio

> 将生成的H/C/ASM文件拷贝到项目目录中。
>
> 在Visual Studio中，点击“Project → Build Customizations...”，并启用MASM。
>
> 在Solution Explorer中，将.h和.c/.asm文件以Header和源文件的形式添加至项目中。
>
> 点击ASM文件的属性，将Item Type设置为Microsoft Macro Assembler。
>
> 确保项目平台设置为了x64，因为目前还不支持32位项目。

## 工具限制

> 目前仅支持64位Windows系统；
>
> 目前还不支持来自图像子系统（sys）的系统调用；
>
> 已在Visual Studio 2019（v14）Window 10 SDK中进行了测试；

## 许可证协议

本项目的开发与发布遵循Apache License 2.0开源许可证协议。

## 项目地址

SysWhispers2：【[ _GitHub传送门_](https://github.com/jthuraisamy/SysWhispers2)】

