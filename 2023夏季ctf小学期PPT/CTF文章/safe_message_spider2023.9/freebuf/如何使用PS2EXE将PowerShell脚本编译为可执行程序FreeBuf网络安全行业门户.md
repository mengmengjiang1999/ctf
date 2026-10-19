![](https://image.3001.net/images/20211008/1633705846_61605f76dedd72d8aee52.jpg!small)

## 关于PS2EXE

PS2EXE是一个可以将PowerShell脚本编译为可执行程序的模块，在GUI和Ingo
Karstein脚本的支持下，该模块能够生成真正的Windows可执行程序。除此之外，PS2EXE还支持PowerShell 5.x和图形化前端。

## 注意事项

有一些人可能会滥用PS2EXE来编译他的计算机病毒脚本，因此越来越多的病毒扫描程序会将使用PS2EXE创建的程序识别为恶意程序并将其删除。因此，希望大家不要将其用于恶意目的。

## 工具安装

首先，我们需要使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/MScholtes/PS2EXE.git

接下来，运行下列命令安装PS2EXE：

    
    
    PS C:\> Install-Module ps2exe

## 工具使用

    
    
    Invoke-ps2exe .\source.ps1 .\target.exe

或

    
    
    ps2exe .\source.ps1 .\target.exe

上述命令会将“source.ps1”编译成可执行程序target.exe，如果命令参数中忽略了“.\target.exe”的话，生成的文件将为“.\source.exe”。

或者，我们也可以启动Win-PS2EXE来开启图形化前端：

    
    
    Win-PS2EXE

## 支持的参数

    
    
    ps2exe [-inputFile] '<file_name>' [[-outputFile] '<file_name>'] [-prepareDebug]
    
           [-x86|-x64] [-lcid <id>] [-STA|-MTA] [-noConsole] [-UNICODEEncoding]
    
           [-credentialGUI] [-iconFile '<filename>'] [-title '<title>'] [-description '<description>']
    
           [-company '<company>'] [-product '<product>'] [-copyright '<copyright>'] [-trademark '<trademark>']
    
           [-version '<version>'] [-configFile] [-noOutput] [-noError] [-noVisualStyles] [-requireAdmin]
    
           [-supportOS] [-virtualize] [-longPaths]

## 参数解释

    
    
    inputFile = 你需要转换为可执行程序的PowerShell脚本（文件需要是UTF8或UTF16编码）
    
    outputFile = 目标可执行文件名称或目录
    
    prepareDebug = 创建调试帮助信息    
    
    x86或x64 = 编译运行时32位或64位代码
    
    lcid = 编译可执行程序的位置ID
    
    STA或MTA = 单线程模式或多线程模式
    
    noConsole = 生成的可执行文件为Windows应用程序，不带终端窗口
    
    UNICODEEncoding = 将输入编码为UNICODE（终端模式）
    
    credentialGUI = 使用GUI弹出凭证窗口（终端模式）
    
    iconFile = 编译可执行文件的图标文件名
    
    title = 标题信息
    
    description = 描述信息
    
    company = 公司信息
    
    product = 产品信息
    
    copyright = 版权信息
    
    trademark = 商标信息
    
    version = 版本信息
    
    configFile = 编写配置文件（<outputfile>.exe.config）
    
    noOutput = 生成可执行文件，不带标准输出
    
    noError = 生成可执行文件，不带错误输出
    
    noVisualStyles = 禁用Windows GUI应用程序的可视化风格
    
    requireAdmin = 如果启用的UAC，编译的可执行文件只会在提权上下文中执行
    
    supportOS = 使用最新Windows版本的功能
    
    virtualize = 激活应用程序虚拟化
    
    longPaths = 启用长路径支持

## 项目地址

 **PS2EXE：** 【[ _GitHub传送门_](https://github.com/MScholtes/PS2EXE)】

## 参考资料

> [ _https://github.com/MScholtes/TechNet-> Gallery_](https://github.com/MScholtes/TechNet-Gallery)
>
> [ _https://gallery.technet.microsoft.com/PS2EXE-GUI-> Convert-e7cb69d5_](https://gallery.technet.microsoft.com/PS2EXE-GUI-> Convert-e7cb69d5)
>
> [
> _https://www.powershellgallery.com/packages/ps2exe/﻿_](https://www.powershellgallery.com/packages/ps2exe/)

