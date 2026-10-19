![](https://image.3001.net/images/20210716/1626443703_60f18fb7d0bc1f35e92b4.jpg!small)

## 关于Swift-Attack

Swift-Attack是一个专为蓝队安全研究人员设计的单元测试套件，旨在帮助广大研究人员检测某些常见的macOS后渗透方法，并构建检测方案。

本项目已经包括了一些使用命令行历史记录和磁盘二进制文件的后渗透测试用例，这些内容比较容易被检测到。除此之外，还提供了使用API调用的后渗透测试用例，而这种方式的检测难度会更大。当然了，本项目提供的后渗透测试用理并不完整，我们只提供了一些常见的测试用例。在将来，我们还会添加更多额外的单元测试以扩展Swift-Attack项目。

需要注意的是，所有这些测试都在本地运行，并将结果返回给stdout。

## 工具安装与配置

首先，广大研究人员需要使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/cedowens/Swift-Attack

确保已经安装好了Swift环境以及开发者工具（可以通过macOS的应用商店安装），然后在Xcode中打开xcodeproj文件，并在Xcode中进行项目构建。

编译后的应用程序存储路径类似如下：

    
    
    Users//Library/Developer/Xcode/DerivedData/Swift-Attack-[random]/Build/Products/Debug/Swift-Attack.app

接下来，在命令行窗口中使用cd命令切换到上述路径：

    
    
    cd Swift-Attack.app/Contents/MacOS......

给Swift-Attack项目文件提供完整的磁盘访问权限以确保在运行所有测试的过程中不会出现报错。

运行下列命令即可移除Quarantine属性：

    
    
    xattr -c Swift-Attack

最后，使用下列命令即可运行Swift-Attack：

    
    
    ./Swift-Attack -h

## 工具使用

我们可以使用下列单个或多个参数选项来运行Swift-Attack：

    
    
    ./Swift-Attack [option1] [option2]...

我们还提供了一个简单的macro.txt文件，以辅助测试macOS中Office宏执行的相关情况。

## 单元测试项目

> 使用osascript脚本调用终端；
>
> 通过API调用终端；
>
> 使用osascript脚本导出剪贴板内容；
>
> 使用API导出剪贴板内容；
>
> 使用screencapture获取屏幕截图；
>
> 使用API调用获取屏幕截图；
>
> Shell命令支持；
>
> 导出zsh历史记录；
>
> 安全工具枚举；
>
> 使用osascript脚本获取系统信息；
>
> 通过API调用获取系统信息；
>
> 导出磁盘中的ssh、aws、gcp和azure密钥；
>
> 导出浏览器历史记录（Chrome、Safari、Firefox）；
>
> 导出Quarantine历史记录；
>
> Office宏支持；
>
> 独立的安装工具包；
>
> CVE-2021-30657绕过Payload；

## 工具运行截图

![](https://image.3001.net/images/20210716/1626443746_60f18fe25587a8330e95d.png!small)

## 项目地址

 **Swift-Attack：** 【[ _GitHub传送门_](https://github.com/cedowens/Swift-Attack)】

## 参考资料

> [
> _https://github.com/D00MFist/PersistentJXA_](https://github.com/D00MFist/PersistentJXA)
>
> [ _https://github.com/cedowens/Persistent-> Swift_](https://github.com/cedowens/Persistent-Swift)
>
> [ _https://github.com/cedowens/MacC2_](https://github.com/cedowens/MacC2)
>
> [ _https://cedowens.medium.com/macos-gatekeeper-> bypass-2021-edition-5256a2955508﻿_](https://cedowens.medium.com/macos-> gatekeeper-bypass-2021-edition-5256a2955508)

