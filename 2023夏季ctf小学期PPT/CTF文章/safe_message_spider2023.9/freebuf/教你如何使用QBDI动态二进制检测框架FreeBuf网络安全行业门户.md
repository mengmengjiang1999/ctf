## 工具介绍

QBDI 全名为 QuarkslaB Dynamicbinary Instrumentation，它是一个模块化的跨平台以及跨架构的 DBI
框架。该工具目前支持 Linux、macOS、Android、iOS 和 Windows 操作系统，支持的架构有 x86、x86-64、ARM 和
AArch64 架构。QBDI 的模块化特征意味着它不需要包含任何首选的注入方法，并且可以结合外部注入工具一起使用。QBDI 包含了一个基于
LD_PRELOAD 的小型 Linux 以及一个动态可执行的 macOS 注入器（QBDIPreload），它们是 QBDI 的 Python
绑定基础，即 pyQBDI。QBDI 还整合了 Frida，一个动态指令工具集。

QBDI 针对 x86-64 架构的支持已经非常成熟了，虽然该工具目前仍针对 ARM 架构在进行开发，但已经足够执行类似 ls 或 cat 这样简单的
CLI 程序了。工具计划增加对 x86 和 AArch64 的支持。

但是，QBDI 目前无法处理信号、多线程和 C++异常机制。

##  编译

在构建该项目时，系统需要满足下列依赖：cmake、make（针对 Linux 和 macOS）、ninja（针对 Android）、Visual
Studio（针对 Windows）和 C++ 11 工具集。

###  编译过程分为两个步骤：

> 1、 构建本地代码以及依赖；
>
> 2、 使用代码库构建 QBDI；

当前的依赖组件需要 用户构建 LLVM 和 Google Test，我们需要本地构建 LLVM，因为 QBDI 需要使用常规 LLVM 没有对外提供的私有
API，而且 QBDI 也只能匹配指定版本的 API。第一步的操作会进行缓存，并且只用执行一次，后续的构建操作只需要重复第二步骤即可。

QBDI 需要使用 cmake 构建，并要求传递构建配置标识。为了简化操作，我们提供了一个 Shell
脚本来完场常规配置的构建，大家也可以根据自己的需要来修改脚本，完成 QBDI 的自定义编译。

##  Linux

###  x86-64

在项目结构的根路径创建一个新的目录，并执行 Linux 配置脚本：

    
    
    mkdir build
    cd build
    ../cmake/config-linux-X86_64.sh

如果构建脚本时提醒你缺失平台依赖的话，你需要重新构建依赖并执行下列命令：

    
    
    make llvm
    
    make gtest

该命令会重构平台上的依赖组件，接下来你可以重新运行配置脚本并完成项目编译:

    
    
    ../cmake/config-linux-X86_64.sh
    
    make -j4

###  ARM 编译

针对 ARM 架构，用户可以使用 config-linux-ARM.sh
配置脚本来完成环境配置，不过这个脚本需要大家针对自己的跨架构编译工具链来进行定制修改：

> 1、 正确的代码必须导出至 AS、CC、CXX 和 STRIP 环境变量。
>
> 2、「-DCMAKE_C_FLAGS」和「-DCMAKE_CXX_FLAGS」需要包含正确的默认标识（取决于使用的工具链），至少要修改
> ARM_ARCH、ARM_C_INCLUDE 和 ARM_CXX_INCLUDE。

##  macOS

在 macOS 上编译 QBDI 需要满足下列条件：

> 1、 Sierra 以上版本的 macOS；
>
> 2、 XCode；
>
> 3、 命令行工具（xcode-select--install）；
>
> 4、 包管理器，例如 MacPorts 或 HomeBrew；
>
> 5、 某些工具包（port install cmakewget）；

满足上述条件后，在项目目录的根节点新建一个目录，然后执行 macOS 配置脚本：

    
    
    mkdir build
    
    cd build
    
    ../cmake/config-macOS-X86_64.sh

如果构建脚本时提醒你缺失平台依赖的话，你需要重新构建依赖并执行下列命令：

    
    
    make llvm
    
    make gtest

该命令会重构平台上的依赖组件，接下来你可以重新运行配置脚本并完成项目编译:

    
    
    ../cmake/config-linux-X86_64.sh
    
    make -j4

##  Windows

在 Windows 上构建项目需要安装 Python 3，以及最新版本的 CMake。

首先，需要修改 config-win-X86_64.py 来匹配安装好的 Visual Studio，然后运行下列代码：

    
    
    mkdir build
    
    cd build
    
    python../cmake/config-win-X86_64.py

如果构建脚本时提醒你缺失平台依赖的话，你需要重新构建依赖并执行下列命令：

    
    
    MSBuild.exedeps\llvm.vcxproj
    
    MSBuild.exedeps\gtest.vcxproj

该命令会重构平台上的依赖组件，接下来你可以重新运行配置脚本并完成项目编译:

    
    
    python../cmake/config-win-X86_64.py
    
    MSBuild.exe/p:Configuration=Release ALL_BUILD.vcxproj

##  Android

针对 Android 平台，需要 Android NDK，该功能只在 Linux 平台上测试过。配置脚本 config-android-ARM.sh
需要修改以匹配 NDK 版本以及目标平台：

> 1、 NDK_PATH 需指向 Android NDK；
>
> 2、 SDKBIN_PATH 需要补充完整，指向 NDK 所使用的工具集；
>
> 3、 API_LEVEL 需匹配目标 Android API 版本；
>
> 4、 正确的代码必须导出至 AS、CC、CXX 和 STRIP 环境变量；

###  项目地址

QBDI：【[GitHub 传送门](https://github.com/QBDI/QBDI)】

 ***参考来源：[QBDI](https://github.com/QBDI/QBDI)，FB 小编 Alpha_h4ck 编译，转载请注明来自
FreeBuf.COM**

