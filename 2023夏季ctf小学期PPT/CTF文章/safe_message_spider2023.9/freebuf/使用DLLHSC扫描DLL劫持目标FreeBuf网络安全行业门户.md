![](https://image.3001.net/images/20210321/1616321460_60571bb4627337f757ee2.png!small)

## DLLHSC

DLLHSC全称为DLL Hijack
SCanner，即DLL劫持扫描工具，DLLHSC可以生成线索并自动帮助广大研究人员发现合适的DLL劫持攻击目标，以方便实现DLL搜索顺序劫持。

此存储库包含工具的Visual
Studio项目文件（DLLHSC）、API钩子功能的项目文件（detour）、Payload项目文件以及针对x86和x64体系结构的已编译可执行文件。其中，项目代码全部采用Visual
Studio Community 2019进行开发和编译。

如果选择使用源代码处编译工具，则需要编译项目DLLHSC、detour和Payload。DLLHSC实现了这个工具的核心功能，detour项目生成一个用于钩住API的DLL文件，Payload项目负责生成用作概念验证的DLL，广大研究人员可以测试可执行文件并查看是否可以通过搜索顺序劫持技术来加载它。生成的Payload必须与DLLHSC存放在同一目录中，detour生成的文件名分别为payload32.dll（针对x86体系架构）和payload64.dll（针对x64体系架构）。

## 工具操作模式

DLLHSC实现了三种操作模式，具体如下：

### 1、轻量级模式

将可执行镜像加载到内存中，解析导入表，然后用Payload DLL替换导入表中引用的任何DLL。

该工具只在应用程序目录中放置一个模块（DLL），该模块不属于WinSxS，也不属于KnownDLLs。

Payload
DLL在执行时，将在以下路径中创建一个文件：C:\Users\%USERNAME%\AppData\Local\Temp\DLLHSC.tmp作为执行验证。接下来，工具将启动应用程序，并通过检查临时文件是否存在来报告是否执行了Payload
DLL。当某些可执行文件从加载的DLL导入函数时，如果提供的DLL无法导出这些函数并满足所提供镜像的依赖关系时，可能会显示错误消息框。但是，消息框返回的信息表明，如果满足依赖关系，则目标DLL可能是Payload执行的良好候选目标。在这种情况下，则需要进行额外的分析。这些消息框的标题可能包含以下字符串：找不到序号或找不到入口点。DLLHSC会查找包含这些字符串的窗口，一旦它们出现就立即关闭并报告结果。

### 2、列表模块模式

使用提供的可执行镜像创建进程，枚举加载到此进程的地址空间中的模块，并在应用筛选器后报告结果。

该工具只报告从系统目录加载的不属于knowndll的模块，输出的结果为需要额外分析的线索。然后，分析员可以将报告的模块放在应用程序目录中，并检查应用程序是否加载了提供的模块。

### 3、运行时模式

通过[ _Microsoft
Detours_](https://github.com/microsoft/Detours)钩住LoadLibrary和LoadLibraryEx
API，并报告在运行时加载的模块。

每次扫描的应用程序在调用LoadLibrary和LoadLibraryEx
API时，该工具都会截获调用并将请求的模块写入文件C:\Users\%USERNAME%\AppData\Local\Temp\DLLHSCRTLOG.tmp之中。如果LoadLibraryEx专门使用了LOAD_LIBRARY_SEARCH_SYSTEM32标记进行调用的话，则不会向文件写入任何输出结果。所有调用拦截完成之后，工具将读取日志文件内容并输出结果。需要进一步分析的是KnownDLLs注册表项中不存在的模块、系统目录中不存在的模块以及没有完整路径的模块。

## 编译和运行指南

如果你打算使用源代码来编译工具，我们建议你在Visual Code Studio
2019上进行操作。为了使该工具正常工作，必须为相同的体系结构编译项目DLLHSC、detour和payload，然后将它们放在相同的目录中。请注意，从项目Payload生成的DLL必须重命名为payload32.DLL（针对32位体系结构）或payload64.DLL（针对64位体系结构）。

## 工具帮助菜单

    
    
    NAME
    
            dllhsc - DLL Hijack SCanner
    
     
    
    SYNOPSIS
    
            dllhsc.exe -h
    
     
    
            dllhsc.exe -e <executable image path> (-l|-lm|-rt) [-t seconds]
    
     
    
    DESCRIPTION
    
            DLLHSC scans a given executable image for DLL Hijacking and reports the results
    
     
    
            It requires elevated privileges
    
     
    
    OPTIONS
    
            -h, --help
    
                    display this help menu and exit
    
     
    
            -e, --executable-image
    
                    executable image to scan
    
     
    
            -l, --lightweight
    
                    parse the import table, attempt to launch a payload and report the results
    
     
    
            -lm, --list-modules
    
                    list loaded modules that do not exist in the application's directory
    
     
    
            -rt, --runtime-load
    
                    display modules loaded in run-time by hooking LoadLibrary and LoadLibraryEx APIs
    
     
    
            -t, --timeout
    
                    number of seconds to wait for checking any popup error windows - defaults to 10 seconds

## 工具使用演示

本节提供了有关如何运行DLLHSC及其报告的结果的示例。为此，我们选择使用合法的Microsoft实用程序OleView.exe（MD5:D1E6767900C85535F300E08D76AAC9AB）作为演示样例。为了获得更好的结果，建议在安装目录中扫描提供的可执行镜像。

下图中显示了OleView.dll在加载Payload DLL时返回的错误消息提示框：

![](https://image.3001.net/images/20210321/1616321495_60571bd75bc7ec7e3566d.png!small)

该工具将等待10秒或-t秒的最长时间，以确保进程初始化已完成，并且已生成任意消息框。然后它将检测消息框，然后关闭它并报告结果：

![](https://image.3001.net/images/20210321/1616321501_60571bdd7527cc9f5cfc9.png!small)

-lm参数将启动提供的可执行文件并打印它加载的模块，这些模块不属于KnownDLLs列表，也不属于WinSxS依赖项。此模式旨在提供可用作Payload载的DLL的验证，仅用于为分析人员提供潜在目标：

![](https://image.3001.net/images/20210321/1616321507_60571be3a2348f68563dc.png!small)

当以进程的形式启动时，-rt参数会将提供的可执行镜像加载到其地址空间中的模块打印出来：

![](https://image.3001.net/images/20210321/1616321514_60571bea949918db07b57.png!small)

## 项目地址

DLLHSC：【[ _GitHub传送门_](https://github.com/ctxis/DLLHSC)】

## 参考资料

> [
> _https://github.com/microsoft/Detours_](https://github.com/microsoft/Detours)

