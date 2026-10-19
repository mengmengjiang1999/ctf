![](https://image.3001.net/images/20210927/1632702362_61510f9a4e9e998befc15.jpg!small)

## 关于Process-Dump

Process
Dump是一款Windows逆向工程分析工具，该工具基于命令行接口实现，可以帮助广大研究人员从内存中将恶意软件PE文件导出至磁盘并进行分析。一般来说，在执行恶意软件文件之前，攻击者都会对其进行打包和模糊处理，以避免AV扫描。但是，在执行这些文件时，它们通常会在内存中解包或注入反混淆版本的恶意软件代码。恶意软件研究人员在分析恶意软件时的一项常见任务是将这些未打包的代码从内存转储回磁盘，以便使用AV产品进行扫描或使用IDA等静态分析工具进行分析。

进程转储适用于Windows 32和64位操作系统，可以从特定进程或当前运行的所有进程转储内存组件。Process
Dump支持创建和使用良性文件哈希数据库，因此可以跳过所有的良性文件。

## 功能介绍

> 1.从特定进程或所有进程转储代码；
>
> 2.查找并转储进程中未正确加载的隐藏模块；
>
> 3.查找和转储松散代码块，即使它们不与PE文件关联；
>
> 4.重构转储信息；
>
> 5.可以在关闭转储监视器模式（'-closemon'）下运行，在该模式下，进程将在终止前暂停并转储；
>
> 6.支持多线程，因此当你在转储所有正在运行的进程时，它的运行速度将非常快；
>
> 7.可以生成一个良性文件哈希数据库，在计算机感染恶意软件之前生成此文件，以便在进程转储时仅转储新的恶意软件组件。

## 工具安装

我们可以直接点击【[ _这里_](http://www.split-code.com/files/pd_v2_1.zip)】下载最新版本的Process-Dump预编译发布版本，下载地址如下：

    
    
    http://www.split-code.com/files/pd_v2_1.zip
    

在使用该工具之前，我们还需要安装“Microsoft Visual C++ Redistributable for Visual Studio
2015”，下载地址如下：

    
    
    https://www.microsoft.com/en-ca/download/details.aspx?id=48145
    

### 编译源代码

该工具适用于Visual Studio 2019的免费社区版本，我们可以使用下列命令将该项目源码克隆至本地，并在VS2019中打开项目，然后进行项目编译：

    
    
    git clone https://github.com/glmcdona/Process-Dump.git
    

## 工具使用样例

从系统上的所有进程转储所有模块和隐藏代码块（忽略已知的良性模块）：

    
    
    pd64.exe -system
    

在终端监视器模式下运行，直到按下Ctrl + C键之前，进程转储将在终止之前转储任何进程：

    
    
    pd64.exe -closemon
    

从特定进程标识符转储所有模块和隐藏代码块：

    
    
    pd64.exe -pid 0x18A
    

按进程名称转储所有模块和隐藏代码块：

    
    
    pd64.exe -p .*chrome.*
    

构建良性文件哈希数据库，用于排除使用上述命令转储模块中的良性代码：

    
    
    pd64.exe -db gen
    

## 沙箱使用样例

如果你正在运行一个自动化沙箱，或手动反恶意软件研究环境，我建议广大研究人员以下列方式运行Process-Dump，所有的命令都需要以管理员权限运行：

首先，打开你的干净环境，并构建良性文件哈希数据库。然后运行下列命令：

    
    
    pd64.exe -db gen
    
    pd64 -db genquick
    

启动Process-Dump终端监控器，此时该工具将在后台转储恶意软件所使用的全部中间进程信息：

    
    
    pd64.exe -closemon
    

现在，运行恶意软件文件，并观察恶意软件安装行为。当你准备从内存转储正在运行的恶意软件信息时，可直接运行下列命令：

    
    
    pd64.exe -system
    

所有转储的组件都将存储至pd64.exe所在的工作目录中，我们可以使用“-o”参数修改输出文件路径。

## 项目地址

 **Process-Dump：** 【[ _GitHub传送门_](https://github.com/glmcdona/Process-Dump)】

## 参考资料

> [ _http://split-code.com/processdump.html_](http://split-> code.com/processdump.html)
>
> [ _https://www.microsoft.com/en-> ca/download/details.aspx?id=48145_](https://www.microsoft.com/en-> ca/download/details.aspx?id=48145)
>
> [ _http://www.split-code.com/﻿_](http://www.split-code.com/)

