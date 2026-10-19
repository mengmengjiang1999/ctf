![](https://image.3001.net/images/20190914/1568448942_5d7ca1aeba635.png!small)

**Applepie这款工具是一个专门用于模糊测试、内部安全审查和寻找漏洞的工具，从本质上来说，它是一款使用了Windows（版本：Windows 10
v17763）虚拟机管理程序平台API（WHVP）的管理程序。其中，Applepie还整合了Bochs来提供深度内部检测和设备模拟等功能。**

Windows虚拟机管理程序平台（WHVP）是一套API套件，可以给我们提供访问Hyper-V的虚拟机管理程序功能的服务。这个API可以帮助我们在用户空间中轻松创建一个虚拟机，而不需要任何的驱动程序或其他权限。

##  功能介绍

该工具的主要功能是帮助研究人员在安全分析的过程中进行模糊测试和内部安全检查。通过使用常见的模糊测试技术，我们可以在任何测试目标、内核和用户环境中使用该工具。整个环境允许研究人员在不需要任何目标资源的情况下对目标进行模糊测试。而且该工具代码覆盖率非常高，而且可以在扫描的过程中构建模糊测试用例以备后续使用。

针对系统快照的模糊测试也是该工具的一个特点，当我们拿到目标系统在某个状态下的系统快照之后，我们就可以加载快照并进行模糊测试了。由于虚拟机重置的成本是非常低的，所以我们可以轻松降低安全分析所需的时间。

##  项目构建

###  工具要求

> 1、最新版本的MSVC编译器（Visual Studio 2017）
>
> 2、Rust（<https://rustup.rs/>）
>
> 3、Python 3（<https://www.python.org/>）
>
> 4、[Cygwin](https://www.cygwin.com/setup-x86_64.exe)+autoconf+GNU
>
> 5、Hyper-V

##  构建步骤

请大家遵循下列步骤完成项目代码构建：

    
    
    Clean install of Windows 10, Build 17763
    
        rustc 1.33.0-nightly (8e2063d02 2019-01-07)
    
        Microsoft (R) C/C++ Optimizing Compiler Version 19.16.27025.1 for x64
    
        Visual Studio Community 2017 version 15.9.4
    
        applepie commit `f84c084feb487e2e7f31f9052a4ab0addd2c4cf9`
    
        Python 3.7.2 x64
    
        git version 2.20.1.windows.1

首先，确保Windows 10已经更新至最新版本，因为我们只在最新版本的Windows 10系统中测试了WHVP等功能。

在“启动或关闭Windows功能中”，点击“Hyper-V”，然后选择“Windows虚拟机监控程序平台”，最后点击确定并重启设备。

![](https://image.3001.net/images/20190914/1568448967_5d7ca1c773bb7.png!small)

安装VS Community 2017并更新版本，选择“Desktop development with C++”：

![](https://image.3001.net/images/20190914/1568448972_5d7ca1cc1ea6f.png!small)

安装“Rust nightly for x86_64-pc-windows-msvc”：

![](https://image.3001.net/images/20190914/1568448976_5d7ca1d066c73.png!small)

##
![](https://image.3001.net/images/20190914/1568448979_5d7ca1d3c1140.png!small)

接下来，分别安装Git、Cygwin x64、Python和"x64 Native Tools Command Prompt for VS 2017"，

最后，运行下列命令将项目代码克隆至本地：

    
    
    git clone https://github.com/zolabs/applepie

然后切换至本地项目目录，运行下列命令：

    
    
    python build.py

##  工具演示视频

###  添加的新功能

> 视频地址：【点我观看】

###  代码覆盖演示

> 视频地址：【点我观看】

##  项目地址

> Applepie：【[GitHub传送门](https://github.com/****zolabs/applepie)】

***参考来源：[zolabs](https://github.com/****zolabs/applepie)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

  

