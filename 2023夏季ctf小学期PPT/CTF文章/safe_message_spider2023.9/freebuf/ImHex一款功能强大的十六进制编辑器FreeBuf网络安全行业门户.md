![](https://image.3001.net/images/20210126/1611654445_600fe52d8bc5818112994.png!small)

## ImHex

ImHex是一款功能强大的十六进制编辑器，该工具专为逆向工程分析师、编程开发人员以及那些想好好保护自己眼睛的安全人员所设计。哪怕你每天工作到凌晨三点（虽然不建议），也不会伤害你的眼睛！

## 功能介绍

>
> 功能丰富的十六进制数据界面：字节修复、修复管理、字节拷贝（字节、十六进制字符串、C、C++、C#、Rust、Python、Java和JavaScript数组、HTML自包含div等）。
>
> 字符串、十六进制搜索。
>
> 自定义C++类模式语言，支持对文件内容进行解析和高亮显示。
>
> 数据导入：支持Base64文件、IPS和IPS32。
>
> 数据导出：IPS和IPS32。
>
> 数据检查器允许解释多种不同类型的数据（小端和大端）。
>
> 大文件支持和快速有效的加载。
>
> 文件哈希支持：CRC16、CRC32、MD4、MD5、SHA-1、SHA-224、SHA-256、SHA-384和SHA-512。
>
> 反汇编程序支持多种不同的体系结构：ARM32 (ARM, Thumb, Cortex-M, AArch32)、ARM64、MIPS (MIPS32,
> MIPS64, MIPS32R6, Micro)、x86 (16-bit, 32-bit, 64-bit)、PowerPC (32-bit,
> 64-bit)、SPARC、IBM SystemZ、xCORE、M68K、TMS320C64X、M680X和Ethereum。
>
> 支持书签、区域突出显示和注释。
>
> 数据分析：提供文件解析器和MIME类型数据库、字节分布图、熵图、最高平均熵、加密/压缩文件检测。
>
> 其他实用工具：ASCII表、正则表达式替换、数学表达式计算器、十六进制颜色选择器。
>
> 在深夜使用时不会“烧坏”你的视网膜。

## 模式语言

ImHex所使用的开发基于自定义类C模式语言，易于阅读、理解和学习。感兴趣的同学可以在ImHex中点击“Help -> Pattern Language
Cheat Sheet”来了解更多。

## Nightly构建

该工具的Nightly构建版本可以在该项目的【[ _GitHub
Actions_](https://github.com/WerWolv/ImHex/actions?query=workflow%3ABuild)】中获取到。

> Windows • x86_64
>
> [ _MSI
> Installer_](https://nightly.link/WerWolv/ImHex/workflows/build/master/Windows%20Installer.zip)
>
> [ _Portable
> ZIP_](https://nightly.link/WerWolv/ImHex/workflows/build/master/Windows%20Portable%20ZIP.zip)
>
> MacOS • x86_64
>
> [
> _DMG_](https://nightly.link/WerWolv/ImHex/workflows/build/master/macOS%20DMG.zip)
>
> Linux • x86_64
>
> [
> _ELF_](https://nightly.link/WerWolv/ImHex/workflows/build/master/Linux%20ELF.zip)

## 编译

在编译项目源码时，我们需要一个C++20兼容的编译器，比如说GCC 10.2.0。除此之外，在编译ImHex时还需要安装下列依赖组件：

> GLFW3
>
> libmagic, libgnurx, libtre, libintl, libiconv
>
> libcrypto
>
> capstone
>
> nlohmann json
>
> Python3
>
> freetype2
>
> Brew (macOS only)

## Windows和Linux

该项目还为Arch Linux、Fedora、Debian/Ubuntu提供了打包的依赖安装[
_脚本_](https://github.com/WerWolv/ImHex/blob/master/dist)。

依赖安装完成之后，可以运行下列命令来构建ImHex：

    
    
    mkdir build
    
    cd build
    
    cmake -DCMAKE_BUILD_TYPE=Release ..
    
    make -j

## macOS

如需在macOS上构建ImHex，运行下列命令即可：

    
    
    brew bundle --no-lock --file dist/Brewfile
    
    mkdir build
    
    cd build
    
    CC=$(brew --prefix llvm)/bin/clang CXX=$(brew --prefix llvm)/bin/clang++ PKG_CONFIG_PATH="$(brew --prefix openssl)/lib/pkgconfig":"$(brew --prefix)/lib/pkgconfig" cmake -DCMAKE_BUILD_TYPE=Release ..
    
    make -j

## 工具运行截图

![](https://image.3001.net/images/20210126/1611654480_600fe55097f0e1e1797ae.png!small)

![](https://image.3001.net/images/20210126/1611654488_600fe558167b2994089e2.png!small)

## 项目地址

ImHex：【[ _GitHub传送门_](https://github.com/WerWolv/ImHex)】

