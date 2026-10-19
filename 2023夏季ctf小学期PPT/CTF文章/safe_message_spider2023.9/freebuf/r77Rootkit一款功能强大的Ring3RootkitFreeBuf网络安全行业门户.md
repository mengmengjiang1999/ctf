![](https://image.3001.net/images/20210522/1621667346_60a8ae12212d69f0af113.jpg!small)

## 关于r77-Rootkit

r77-Rootkit是一款功能强大的无文件Ring 3
Rootkit，并且带有完整的安全工具和持久化机制，可以实现进程、文件和网络连接等操作及任务的隐藏。

r77能够在所有进程中隐藏下列实体：

> 文件、目录、连接、命名管道、计划任务；
>
> 进程；
>
> CPU用量；
>
> 注册表键&值；
>
> 服务；
>
> TCP&UDP连接；

该工具兼容32位和64位版本的Windows 7以及Windows 10。

## 通过前缀隐藏

所有以“$77”为前缀命名的实体都将被隐藏：

![](https://image.3001.net/images/20210522/1621667357_60a8ae1dbed5458e2db3d.png!small)

## 配置系统

动态配置系统允许广大研究人员通过PID或抿成来隐藏进程，通过完整路径来隐藏文件系统，或通过指定端口隐藏TCP&UDP连接：

![](https://image.3001.net/images/20210522/1621667365_60a8ae252fe26b7a805a1.png!small)

配置信息存储在“HKEY_LOCAL_MACHINE\SOFTWARE\$77config”中，并且可以在未提权状态下由任何进程写入。这个键的DACL被设置为可以给任意用户授予完整访问权。

“$77config”键在注册表编辑器被注入了Rootkit之后会自动隐藏。

## 安装工具

r77可以直接使用单独的“Install.exe”进行安装，安装工具会将r77服务在用户登录之前开启，后台进程会向所有当前正在运行以及后续生成的进程中注入命令。这里需要使用两个进程来分别注入32位和64位进程，这两个进程都可以使用配置系统和PID来进行隐藏。

“Uninstall.exe”程序负责将r77从系统中卸载掉，并解除Rootkit跟所有进程的绑定关系。

## 无文件持久化

Rootkit将驻留在系统内存中，不会将任何文件写入磁，这种机制是分多个阶段实现的。

### 阶段一

安装程序为32位和64位r77服务创建两个计划任务。计划任务确实需要存储名为$77svc32.job和$77svc64.job的文件，这是无文件概念的唯一例外。但是，一旦Rootkit运行，计划任务也会通过前缀隐藏。

计划任务将使用下列命令开启“powershell.exe”：

    
    
    [Reflection.Assembly]::Load([Microsoft.Win32.Registry]::LocalMachine.OpenSubkey('SOFTWARE').GetValue('$77stager')).EntryPoint.Invoke($Null,$Null)

该命令是内联的，不需要.ps1脚本。这里，使用PowerShell的.NET
Framework功能从注册表加载C#可执行文件并在内存中执行。由于命令行的最大长度为260（MAX_PATH），因此只有足够的空间执行简单的Assembly.Load().EntryPoint.Invoke()。

![](https://image.3001.net/images/20210522/1621667380_60a8ae3409e9449a582ef.png!small)

![](https://image.3001.net/images/20210522/1621667385_60a8ae399b29a49d22aa5.png!small)

### 阶段二

执行的C#代码为stager，它将会使用Process
Hollowing技术创建r77服务进程。r77服务是一个本地可执行文件，分别以32位和64位架构继续宁编译。父进程被设置为了winlogon.exe以增加欺骗性（模糊性）。另外，这两个进程被ID隐藏，在任务管理器中不可见。

![](https://image.3001.net/images/20210522/1621667403_60a8ae4b3ebcf454cb423.png!small)

磁盘上从未存储可执行文件或DLL。stager存储在注册表中，并从其资源加载r77服务可执行文件。

## 测试环境

测试控制台可以用来向单独进程注入r77，或接触进程跟Rootkit的绑定关系：

![](https://image.3001.net/images/20210522/1621667410_60a8ae5289bf1d6868e12.png!small)

## 工具下载

 **r77 Rootkit 1.2.0.zip：** 【[
_点我下载_](https://bytecode77.com/downloads/r77Rootkit%201.2.0.zip)】（解压密码：bytecode77）

## 项目地址

 **r77-Rootkit：** 【[ _GitHub传送门_](https://github.com/bytecode77/r77-rootkit)】

## 参考资料

[
_https://bytecode77.com/downloads/r77%20Rootkit%20Technical%20Documentation.pdf_](https://bytecode77.com/downloads/r77%20Rootkit%20Technical%20Documentation.pdf)

[ _https://bytecode77.com/r77-rootkit﻿_](https://bytecode77.com/r77-rootkit)

