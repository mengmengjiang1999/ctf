![](https://image.3001.net/images/20220208/1644314942_6202413ed86b62dab684f.jpeg!small)

## 关于Bluffy

Bluffy是一款功能强大的反病毒产品静态安全测试工具，该工具可以将Shellcode转换为各种看似真实的数据格式，以实现反病毒产品的绕过，从而测试反病毒产品的安全性能。

Bluffy同时也是一个PoC概念验证工具，类似于[ _0xBoku_](https://twitter.com/0xBoku)的[
_Ninja_UUID_Runner_](https://github.com/boku7/Ninja_UUID_Runner)和[
_ChoiSG_](https://github.com/ChoiSG)的[
_UuidShellcodeExec_](https://github.com/ChoiSG/UuidShellcodeExec)。

目前，Bluffy已经实现了下列格式转换：

> UUID
>
> CLSID
>
> SVG
>
> CSS
>
> CSV

## 依赖组件

在使用Bluffy之前，我们需要确保本地安装并配置好下列依赖组件。

该工具基于Python语言开发，因此需要先在本地设备上安装并配置好Python 3.9或更高版本环境：

    
    
    sudo apt install python3.9

### rich安装

    
    
    sudo pip3 install rich

### pcre2.8

针对Ubuntu：

    
    
    $ lsb_release -a
    
    No LSB modules are available.
    
    Distributor ID: Ubuntu
    
    Description:  Ubuntu 21.04
    
    Release:  21.04
    
    Codename: hirsute

为了连接“libpcre2-8.a”，还需要将其引入至下列文件：

    
    
    /usr/lib/gcc/x86_64-w64-mingw32/10-win32

对于获取Header和lib文件，则需要使用MSYS2，或者是Mingw64:

    
    
    sudo apt install mingw-64
    
    sudo wget https://packages.msys2.org/package/mingw-w64-x86_64-pcre2?repo=mingw64 -P /usr/lib/gcc/x86_64-w64-mingw32/10-win32

## 工具下载&安装

接下来，使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/ad-995/bluffy.git

## 工具使用

我们可以使用Bluffy来构建一个Payload，并获取我们的源码文件。比如说，我们这里使用calc.bin来作为演示，这个文件将加载calc.exe来作为概念验证。由于Bluffy会使用隐写术来防止静态分析，并将相关代码隐藏到其他合法文件之中，因此我们需要进行额外的分析来确保Payload能够绕过动态检测机制。

运行Bluffy，选择一个掩码并提供我们的.bin文件：

    
    
    python ./bluffy.py -b calc.bin -m css -x

检查你的Payload，然后构建代码。在构建Payload时，需要拷贝Bluffy创建的.h文件，并将其重命名为css.c，然后运行make命令将其构建为可执行程序，并使用提供的样例进行测试：

    
    
    mv css.h examples/css/css.h
    
    cd examples/css
    
    make

上述命令将会使用一个“main.c”文件来构建一个Windows可执行程序。如果你还是用了calc.bin，此时你将会看到一个新的计算器窗口弹出来，如果计算器运行成功，恭喜你你的操作完全正确！

## 工具使用演示

![](https://image.3001.net/images/20220208/1644315031_62024197c6101d2b685de.gif!small)

## 项目地址

 **Bluffy：** 【[ _GitHub传送门_](https://github.com/ad-995/bluffy)】

## 参考资料

> [
> _https://github.com/boku7/Ninja_UUID_Runner_](https://github.com/boku7/Ninja_UUID_Runner)
>
> [
> _https://github.com/ChoiSG/UuidShellcodeExec_](https://github.com/ChoiSG/UuidShellcodeExec)
>
> [
> _https://twitter.com/michaeljranaldo_](https://twitter.com/michaeljranaldo)
>
> [ _https://twitter.com/__mez0___](https://twitter.com/__mez0__)
>
> [
> _https://packages.msys2.org/base/mingw-w64-pcre2_](https://packages.msys2.org/base/mingw-w64-pcre2)
>
> [ _https://pcre.org/_](https://pcre.org/)
>
> [
> _https://ad-995.group/posts/bluffy/bluffy.html_](https://ad-995.group/posts/bluffy/bluffy.html)

