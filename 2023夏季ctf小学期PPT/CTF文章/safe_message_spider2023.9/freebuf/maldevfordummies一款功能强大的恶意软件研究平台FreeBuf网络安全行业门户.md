![](https://image.3001.net/images/20220925/1664118242_63306de2867cb42240b77.jpg!small)

## 关于maldev-for-dummies

毫无疑问，在目前的网络环境中，恶意软件开发正在成为网络犯罪组织的一项重要技能。maldev-for-dummies是一款简单易用的恶意软件研究工具，这个代码库中包含了很多跟恶意软件开发相关的组件工具，可以帮助广大研究人员通过自定义恶意软件，来测试目标系统或产品解决方案的安全性。

随着防病毒（AV）和企业检测与响应（EDR）工具变得越来越成熟，红队被迫保持领先。执行汇编和将未修改的Payload放到磁盘上的时代已经一去不复返了。如果你想让你的任务持续一周以上，你就必须加快Payload的创建和恶意软件的开发。然而，在这一领域起步可能令人望而却步，而且找到合适的资源并不容易的。

本工具主要面向的是恶意软件研究领域的初学者，但安全专家也欢迎使用以增强自己的技术水平。

## 工具准备

在开始之前，我们需要一台专用的开发设备，并且不要安装或运行任何安全防护工具。我们建议使用Windows系统进行开发，但Linux或macOS也可以。接下来，安装好熟悉的IDE即可。（推荐使用Visual
Studio）最后，安装maldev-for-dummies所需的工具链：

> 1、C#开发所需的.NET包；
>
> 2、Nim-lang：可以使用Choosenim完成安装；
>
> 3、Golang；
>
> 4、Rust：可以使用Rustup来安装Rust和相关的工具链；
>
> 5、禁用Windows Defender或添加适当的排除项；

## 工具依赖

### Nim

大多数Nim程序都需要使用一个名为“Winim”的库来跟Windows API进行交互，我们可以使用Nimble包管理器来安装Winim库：

    
    
    nimble install winim

### Golang

该工具的源代码还使用了一些其他的依赖组件，我们可以使用下列命令进行安装：

    
    
    go mod tidy

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/chvancooten/maldev-for-dummies.git

## 工具编译

C#和Nim都属于编译型语言，这也就意味着我们需要一个编译器来将源代码编译为可执行程序。

### C#

C#代码（.cs文件）可以直接使用csc工具编译，或通过Visual Studio编译：

    
    
    csc filename.exe /unsafe

### Nim

Nim代码（.nim文件）需要使用“nim c”命令进行编译，我们可以使用下列命令构建项目源码：

    
    
    nim c filename.nim

如果你想优化构建程序的大小，并过滤调试信息，则可以添加下列命令参数：

    
    
    nim c -d:release -d:strip --opt:size filename.nim

### Golang

Golang代码（.go文件）需要使用“go build”命令进行编译，我们可以使用下列命令构建项目源码：

    
    
    GOOS=windows go build

如果你想优化构建程序的大小，并过滤调试信息，则可以添加下列命令参数：

    
    
    GOOS=windows go build -ldflags "-s -w"

## 项目地址

 **maldev-for-dummies** ：【[
_GitHub传送门_](https://github.com/chvancooten/maldev-for-dummies)】

## 参考资料

> [ _https://code.visualstudio.com/_](https://code.visualstudio.com/)
>
> [
> _https://visualstudio.microsoft.com/vs/community/_](https://visualstudio.microsoft.com/vs/community/)
>
> [ _https://dotnet.microsoft.com/en-us/download/dotnet-> framework_](https://dotnet.microsoft.com/en-us/download/dotnet-framework)
>
> [ _https://nim-lang.org/install.html_](https://nim-lang.org/install.html)
>
> [ _https://github.com/dom*96/choosenim_](https://github.com/dom96/choosenim)
>
> [ _https://go.dev/doc/install_](https://go.dev/doc/install)
>
> [ _https://www.rust-lang.org/tools/install_](https://www.rust-> lang.org/tools/install)
>
> [ _https://github.com/chvancooten/maldev-for-> dummies/blob/main/Exercises/BONUS%20Exercise%203%20-%20Basic%20EDR%20Evasion/solutions/csharp_](https://github.com/chvancooten/maldev-> for-> dummies/blob/main/Exercises/BONUS%20Exercise%203%20-%20Basic%20EDR%20Evasion/solutions/csharp)

