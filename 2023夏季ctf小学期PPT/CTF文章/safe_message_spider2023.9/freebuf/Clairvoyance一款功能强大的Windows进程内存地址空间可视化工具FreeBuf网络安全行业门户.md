![](https://image.3001.net/images/20210106/1609911882_5ff54e4a8ee5af581769a.png!small)

## 工具概述

Clairvoyance是一款功能强大的Windows进程内存地址空间可视化工具，它可以针对一个Windows
64位内核中运行的整个64位进程地址空间（用户和内核）创建一个丰富多彩的页面保护可视化界面。

![](https://image.3001.net/images/20210106/1609911891_5ff54e538125c1637e4bc.png!small)

该工具利用hilbert空间填充曲线将一维空间即地址空间转化为二维可视化界面。上图中的每个彩色像素表示虚拟内存中4KB页的页保护（UserRead、UserReadWrite等）。

地址空间是通过从使用WindDbg生成的内核崩溃转储中手动解析与进程相关联的四级页表层次结构来直接计算的。

最后，该工具将输出一个文件，其中包含在二维画布上显示该文件所需的元数据，并且能够计算与特定高亮显示像素相对应的虚拟地址。

## 工具下载

广大研究人员可以直接访问该项目的【[
_Releases页面_](https://github.com/0vercl0k/clairvoyance/releases)】来下载对应操作系统平台的预编译版本。

![](https://image.3001.net/images/20210106/1609911902_5ff54e5e0a3998cf9aee1.png!small)

## 工具使用

为了生成内核崩溃导出信息，我们建议大家使用[ _WinDbg_](https://docs.microsoft.com/en-us/windows-hardware/drivers/debugger/debugger-download-tools)和[
_KDNet_](https://docs.microsoft.com/en-us/windows-hardware/drivers/debugger/setting-up-a-network-debugging-connection-automatically)，并使用下列命令：

    
    
    .dump /f

获取到导出信息之后，我们可以将其路径传递给Clairvoyance，接下来Clairvoyance便会在浏览器中以可视化的形式将数据显示出来：

![](https://image.3001.net/images/20210106/1609911914_5ff54e6ad0c356bff1812.gif)

## 枸橘构建

我们可以使用[ _clang++-11_](https://clang.llvm.org/)在Linux上构建Clairvoyance，或使用微软的[
_Visual Studio
2019_](https://visualstudio.microsoft.com/vs/community/)在Windows上构建Clairvoyance。

如需自行动手构建Clairvoyance，可以使用项目目录[
_build/_](https://github.com/0vercl0k/clairvoyance/blob/main/build)下的脚本来实现：

    
    
    (base) clairvoyance\build>build-msvc.bat
    
    (base) clairvoyance\build>cmake ..
    
    -- Selecting Windows SDK version 10.0.19041.0 to target Windows 10.0.19042.
    
    -- Configuring done
    
    -- Generating done
    
    -- Build files have been written to: clairvoyance/build
    
     
    
    (base) clairvoyance\build>cmake --build . --config RelWithDebInfo
    
    Microsoft (R) Build Engine version 16.8.2+25e4d540b for .NET Framework
    
    Copyright (C) Microsoft Corporation. All rights reserved.
    
     
    
      clairvoyance.vcxproj -> clairvoyance\build\RelWithDebInfo\clairvoyance.exe
    
      Building Custom Rule clairvoyance/CMakeLists.txt

## 工具使用截图

### 页面堆内存：

![](https://image.3001.net/images/20210106/1609911965_5ff54e9d84ef27dba9914.png!small)

### 内核栈：

![](https://image.3001.net/images/20210106/1609911978_5ff54eaa683a468a30acc.png!small)

### 系统缓存：

![](https://image.3001.net/images/20210106/1609911985_5ff54eb1ad9e4639f5f78.png!small)

## 项目地址

Clairvoyance：【[ _GitHub传送门_](https://github.com/0vercl0k/clairvoyance)】

