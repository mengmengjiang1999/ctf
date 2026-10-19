****

**本文是我的关于[如何](https://www.peerlyst.com/tags/how-to)开始Android[逆向](https://www.peerlyst.com/tags/reverse-engineering)系列文章的第一部分。在文末提供了一个文档，你可以根据该文档说明部署同我一样的实验环境。**

在了解[android应用](https://www.peerlyst.com/tags/android-application)的[逆向](https://www.peerlyst.com/tags/engineering)之前，你必须对android平台及其架构和android应用程序的构建块（组件）已有了一个较好的理解。如果你并不了解这些，那么我建议你先参阅以下链接，然后再继续浏览本文。

> [Android平台架构](https://secureyourdigitallife.in/introduction-to-android-and-> itss-architecture/)
>
> Android应用程序及其组件
>
> [Android应用程序及其架构（PPT）](https://secureyourdigitallife.in/android-> architecture-components-ppt/)

我当前的实验室环境如下：

> 主机系统为windows，其中安装了[virtual](https://www.peerlyst.com/tags/virtual) box 和
> [genymotion](https://www.genymotion.com/fun-zone/)
>
> virtual box 和 genymotion的设备都处于桥接模式
>
> Android 4.4 (kitkat [API](https://www.peerlyst.com/tags/api) version 19)
>
> 在virtual box中，[kali linux](https://www.peerlyst.com/tags/kali-> linux)也同时运行（与genymotion一起）

 **注：** 该设置并非固定，你可以根据自身需求环境进行调整。例如，你也可以使用kali linux作为你的主机系统，并在上面安装genymotion。

在正式开始我们的逆向之旅前，我想先向大家介绍一下名为adb（android debugger
bridge）的工具/服务器。它可以帮助我们连接，获取数据并将指令传递给远程Android设备（调试模式可以通过设备设置中的开发者模式打开）。当前情况下，我们将使用genymotion设备（虚拟设备）。

对于安卓应用的逆向，这里有一个非常好的可供我们学习和练习的apk - [DIVA](https://payatu.com/damn-insecure-and-vulnerable-app/) ( Damn insecure and vulnerable [mobile
Application](https://www.peerlyst.com/tags/mobile-application)
)。这是一个由Payatu的安全分析师开发的脆弱安卓应用。下面我们也将以该应用为例：

首先，让我们来启动genymotion设备：

> 在Windows/Linux中搜索Genymotion应用
>
> Start genymotion

![如何开始对Android应用的逆向分析？](https://image.3001.net/images/20180810/1533863020_5b6ce46c589f5.jpg!small)

选中你想要启动的设备，然后点击Start按钮。

![如何开始对Android应用的逆向分析？](https://image.3001.net/images/20180810/1533863035_5b6ce47bb2dae.jpg!small)

如果你以上步骤正确执行，则应该能看到类似以下的界面：

![如何开始对Android应用的逆向分析？](https://image.3001.net/images/20180810/1533863052_5b6ce48c38185.jpg!small)

可以看到Android设备已经启动，现在我们来启动虚拟机中的kali linux。步骤如下：

> 启动virtual box
>
> 从中启动kali虚拟机

 **注：** 这两个虚拟机处于桥接模式。如果有DHCP服务器，则需要连接到路由器或网络。

现在两台机器都已启动，下面让我们来检查下kali和Android设备之间的连接情况。为此，我们需要获取Android设备的IP地址。

> 导航到设置菜单
>
> 单击WiFi选项
>
> 你会在网络中看到WiredSSID
>
> 长按“WiredSSID”选项
>
> 你会看到如下所示界面

![如何开始对Android应用的逆向分析？](https://image.3001.net/images/20180810/1533863075_5b6ce4a345b1a.jpg!small)

获取IP后我们回到kali终端，并键入以下命令检查连接情况：

    
    
    adb connect 192.168.20.74

如果命令正确执行，你将会看到以下输出。

![如何开始对Android应用的逆向分析？](https://image.3001.net/images/20180810/1533863100_5b6ce4bc75144.png!small)

现在让我们通过执行以下命令，来验证设备是否真正连接：

    
    
    adb devices

![如何开始对Android应用的逆向分析？](https://image.3001.net/images/20180810/1533863116_5b6ce4cc1a062.png!small)

通过确认我们得知设备已连接到IP地址192.168.20.74和5555端口（adb默认的连接端口为5555）。

现在，我们就可以在Android设备上执行不同的adb命令了。通过-h选项查看可用参数：

    
    
    adb -h

![如何开始对Android应用的逆向分析？](https://image.3001.net/images/20180810/1533863140_5b6ce4e418ccd.png!small)

在帮助信息中会为你列出所有可用的参数选项。下面是一些在逆向中时常会用到的命令：

ADB 调试

> adb devices – Lists all the connected devices
>
> adb forward – used for forwarding socket connections
>
> adb kill-serve

无线

> adb connect – connects to the remote device
>
> adb usb – connects to the USB attached device

包管理器

adb install – install a package adb uninstall - uninstall a package adb shell
pm list packages – used for displaying lists of packages installed adb shell
pm path – used for displaying package path on device adb shell pm clear

文件管理器

adb pull – used for pulling / downloading a file adb push – used for pushing /
uploading a file adb shell ls – used for displaying list of files and
directories in the current directory adb shell cd – used for changing the
directory adb shell rm- used for removing a file adb shell mkdir – used for
creating a directory adb shell touch – used for creating a file adb shell pwd
– used for displaying the current path adb shell cp – used for copying a file
adb shell mv – used for moving a file

网络

adb shell netstat – used for displaying the statistics for network connection
adb shell ping – used for pinging a host / IP adb shell netcfg adb shell ip

Logcat

adb logcat adb shell dumpsys adb shell dumpstate

截图

adb shell screencap adb shell screenrecord

系统

adb root adb sideload adb shell ps adb shell top adb shell getprop adb shell
setprop

在了解adb命令后，下面我们来安装DIVA（Android应用程序）。

 **注：** 请将该应用下载安装至你的kali机器上，因为所有的adb命令都将从kali中触发。

执行以下命令安装该应用：

    
    
    adb install diva-beta.apk

![如何开始对Android应用的逆向分析？](https://image.3001.net/images/20180810/1533863164_5b6ce4fc13652.png!small)

现在，我们已经完成了diva-beta.apk的安装。让我们来验证下该应用是否已在我们的设备中成功安装。

![如何开始对Android应用的逆向分析？](https://image.3001.net/images/20180810/1533863188_5b6ce5144f9b8.jpg!small)

可以看到应用程序已被正确安装，并可在设备的菜单中使用。

让我们通过单击该应用程的图标来启动它。你将看到如下启动界面：

![如何开始对Android应用的逆向分析？](https://image.3001.net/images/20180810/1533863212_5b6ce52cb4e94.jpg!small)

当前，DIVA为我们准备了以下挑战：

不安全的日志记录 硬编码问题 - 第1部分 不安全的数据存储 - 第1部分 不安全的数据存储 - 第2部分 不安全的数据存储 - 第3部分 不安全的数据存储
- 第4部分 输入验证问题 - 第1部分 输入验证问题 - 第2部分 访问控制问题 - 第1部分 访问控制问题 - 第2部分 访问控制问题 - 第3部分
硬编码问题 - 第2部分 输入验证问题 - 第3部分

我们将逐一解决上述挑战，让你了解Android应用中的不同漏洞。对于第一项挑战，即不安全日志记录，我们可以通过adb命令来检查diva应用的日志记录。命令如下：

    
    
    adb logcat

如果命令正确执行，你将会看到如下所示内容：

![如何开始对Android应用的逆向分析？](https://image.3001.net/images/20180810/1533863242_5b6ce54a1cf87.png!small)

可以看到这里的日志记录非常的杂乱，因为它显示了许多不同的日志记录数据（整个设备）。为了让我们看起来更加清晰，我将使用grep命令。但在此之前，我们需要首先获取该应用程序包的进程ID。命令如下：

    
    
    adb shell ps | grep diva

如果命令正确执行，你将会看到如下所示内容：  

![如何开始对Android应用的逆向分析？](https://image.3001.net/images/20180810/1533863713_5b6ce721345cd.png!small)

adb
shell是用于通过adb发送任何shell指令的命令；ps作为shell指令发送，ps的输出提供给grep命令。Grep是一个非常棒的用于搜索相关字符串的工具，在本例中我们搜索的字符串为“diva”。

从输出结果中我们得知，diva的pid为1654，包名称为“jakhar.aseem.diva”

现在，让我们以组合的形式使用logcat和grep命令：

    
    
    adb logcat | grep 1654

![如何开始对Android应用的逆向分析？](https://image.3001.net/images/20180810/1533863741_5b6ce73dd5418.png!small)

你将看到与该特定进程（即diva）相关的所有日志。

[实验环境设置文档](https://res.cloudinary.com/peerlyst/image/upload/v1532806760/post-attachments/mobile_lab_setup_ww2rl1.pdf)

 ** *参考来源：[peerlyst](https://www.peerlyst.com/posts/how-to-start-reverse-engineering-on-android-application-ankit-mishra)，FB小编 secist
编译，转载请注明来自FreeBuf.COM**

