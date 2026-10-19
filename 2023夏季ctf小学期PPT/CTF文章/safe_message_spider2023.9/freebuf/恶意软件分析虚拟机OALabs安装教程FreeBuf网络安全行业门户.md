**Windows虚拟机（VM）是最重要的恶意软件分析工具之一。使用VM我们可以灵活地调试恶意软件，且不必担心主机感染等问题。就算VM不小心被感染了，我们也可以通过快照快速的将其恢复为原始状态。**

传统上，恶意软件分析师往往需要在Windows VM上维护一系列的分析工具。但随着[FLARE-VM项目](https://github.com/fireeye/flare-vm)的发布，这一切都发生了改变。 FLARE-VM建立在[Chocolatey](https://chocolatey.org/)项目的基础上，并为Windows软件提供了集中化的管理。而OALabs-VM installer（安装程序）则是我们对项目的进一步扩展，该安装程序将使用你需要的工具，自动化的为你配置一个完整的VM。

 **本教程是有关如何使用OAlabs-VM installer安装和配置一个FREE Windows 7 VM的详细说明。**

## 安装 Virtual Box

这里我将使用VirtualBox，这是一个免费开源的虚拟机软件。为了更便于大家的学习，我建议大家也使用VirtualBox。当然，如果你习惯于使用VM那么也没有问题。

首先，我们来下载并安装VirtualBox：<https://www.virtualbox.org/wiki/Downloads>。

## 安装 FREE Windows 7 VM

OALabs-VM installer主要目的是在微软提供的FREE VM上运行，用于测试Edge Web浏览器。虽然我们只在free
VM上进行了测试，但该安装程序可以支持在任何的32位Windows 7 VM上运行。这里我们选择使用32bit Windows
7，这样更易于我们的调试工作（大多数windows恶意软件都为32位）。

免费的Microsoft VM许可证有效期为90天。我们可以在安装过程中创建快照，并在过期后恢复快照，这样我们就可以无限期的使用了。

导航至Microsoft VM下载页面：<https://developer.microsoft.com/en-us/microsoft-edge/tools/vms/>，并在下拉菜单中选择以下VM配置：

> IE11 on Win7 (x86)
>
> VirtualBox

下载.zip文件并将其解压缩到你的主机上。zip文件夹中应包含.ova文件。

![恶意软件分析虚拟机OALabs安装教程](https://image.3001.net/images/20180722/15322267953843.png!small)

接下来，我们打开VirtualBox并选择File-> Import
Appliance。选择我们刚刚解压缩的.ova文件路径，并单击Continue。然后，系统会要求你选择appliance
settings，这里建议你将CPU数量设置为2，其余设置默认即可。

![恶意软件分析虚拟机OALabs安装教程](https://image.3001.net/images/20180722/15322268142582.png!small)

最后单击“Import”导入VM。这里我们可能需要等待一段时间。

VM成功导入后在启动之前，我们先来创建一个快照备份。我们可以将该备份命名为Clean Install。

![3Screen-Shot-2018-07-21-at-2.27.18-PM.png](https://image.3001.net/images/20180722/15322268341459.png!small)

![恶意软件分析虚拟机OALabs安装教程](https://image.3001.net/images/20180722/15322268615026.png!small)

创建完成后，我们启动VM并注册使用许可，步骤如下：

> 启动VM
>
> 忽略任何重启VM的提示，选择“Restart Later”
>
> 记下用户名和密码
>
> 通常为IEUser:Passw0rd!
>
> 打开cmd.exe并输入slmgr /ato激活90天许可证
>
> 等待激活确认弹出窗口，并将其关闭

**![恶意软件分析虚拟机OALabs安装教程](https://image.3001.net/images/20180722/15322268838336.png!small)**

 **PRO-TIP：** 如果你想要使用剪贴板在主机和VM之间复制文本，你可以在Settings-> Advanced-> Shared
Clipboard中启用该功能。但需要提醒大家的是，如果你VM中分析的恶意软件可以从剪贴板窃取数据，那么请务必禁用该功能。

![恶意软件分析虚拟机OALabs安装教程](https://image.3001.net/images/20180722/15322269029034.png!small)

## 安装 OALabs-VM 工具

安装OALabs-VM工具只需简单的三步。首先，在VM中打开Internet Explorer并浏览到OALabs Boxstarter
gist：<https://gist.github.com/OALabs/cad8d9489245f3f96d9669f56d2877f>。该gist包含一个Powershell脚本，该脚本将启动installer进程。单击github界面中的Raw按钮，然后在Internet
Explorer中选择File-> Save As...，将脚本下载为文本文件。

![恶意软件分析虚拟机OALabs安装教程](https://image.3001.net/images/20180722/15322269228605.png!small)

确保已将脚本文件以.txt格式保存至桌面，并关闭Internet Explorer。

![恶意软件分析虚拟机OALabs安装教程](https://image.3001.net/images/20180722/15322269387515.png!small)

找到保存的文件并将文件扩展名更改为.ps1。然后右键单击该文件并选择Run with PowerShell。这将启动installer。

安装过程可能需要一些时间，因为它需要下载多个软件包。在安装过程中，VM可能会自动重启多次。某些软件包还可能会弹出询问框，我们只需以默认设置单击确认即可。安装完成后，脚本将提示你单击Enter，以完成安装并关闭PowerShell窗口。

![恶意软件分析虚拟机OALabs安装教程](https://image.3001.net/images/20180722/15322269608234.png!small)

 **PRO-TIP：** OALabs-VM安装完成后，你应该再创建一个快照备份，并命名为Clean With Tools。

## OALabs工具概览

OALabs-VM
installer仅会为我们安装，在[教程](https://www.youtube.com/oalabs/videos)中使用到的少数几个工具。但安装程序还为我们安装了Chocolatey软件包管理器，因此你可以很容易的从Chocolatey软件库中[安装其他软件](https://chocolatey.org/packages)。以下是OALabs-VM工具的一些基本介绍。

###  **Checksum**

Checksum是一个命令行工具，可用于显示文件的校验和哈希值。例如 checksum -t sha256 <file> 将为我们显示文件的SHA256
hash。

### 7zip

7-Zip是一款完全免费而且开源的压缩软件，相比其他软件有更高的压缩比但同时耗费的资源也相对更多。该实用程序被安装在VM的%programfiles%\7zip中，你可以在开始菜单中进行访问。有关更多详细信息，请参阅[7zip](https://www.7-zip.org/)网站。

### Process Explorer

Process
explorer是一个Windows系统和应用程序监视工具。恶意软件常常利用系统进程名来蒙混过关，所以判断进程是否危险不能只看进程名，还要追查用户名、所在路径、命令行及参数等。系统自带的“任务管理器”无法查看详细的信息，借助Process
Explorer可以完成这一切。有关更多详细信息，请参阅[Process Explorer](https://docs.microsoft.com/en-us/sysinternals/downloads/process-explorer)网站。

### Resource Hacker

Resource
Hacker是一款免费查看，修改，添加，删除和重命名，提取Windows可执行文件和资源文件的资源替换工具。有关更多详细信息，请参阅[Resource
Hacker](http://www.angusj.com/resourcehacker/)网站。

###  **HxD**

HxD是一个认真设计的快捷16进制编辑器。还提供直接磁盘编辑、内存修改和处理任何大小的文件。易用的用户界面，提供查找、替换、导出、校验和、字节数据插入、文件粉碎、分割和合并文件、统计数据分布等功能。有关更多详细信息，请参阅[HxD](https://mh-nexus.de/en/hxd/)网站。

### Sublime Text 3

Sublime Text是一个代码编辑器，也是HTML和散文先进的文本编辑器。有关更多详细信息，请参阅[Sublime
Text](https://www.sublimetext.com/)网站。

### Google Chrome

这个不用多介绍了，天天在用的。

### PEBear

PEBear是Hasherezade开发的PE查看器和编辑器。你可以在开始菜单中进行访问，也可以将其固定到任务栏。有关更多详细信息，请参阅hasherezade关于[PEBear的帖子](https://hshrzd.wordpress.com/pe-bear/)。

### LordPE

是一款功能强大的PE文件分析、修改、[脱壳](https://baike.baidu.com/item/%E8%84%B1%E5%A3%B3)软件。LordPE是查看PE格式文件信息的首选工具，并且可以修改相关信息。有关使用说明，请查看LordPE的[aldeid
wiki帖子](https://www.aldeid.com/wiki/LordPE)。

### x64dbg (x32dbg)

x64dbg汉化版是一款功能强大的64位系统调试工具，其主要的目的就是帮助用户管理自己的系统组件参数，支持函数操作方案，可以从电脑行的函数区域中加载需要执行调试的命令，方便你使用预设的函数快速调试对应的字符串，同时还可以将你不知道保存在哪里的字符串快速的搜索出来。你可以在开始菜单中进行访问，也可以将其固定到任务栏。有关更多详细信息，请参阅[x64dbg](https://x64dbg.com/#start)网站。

### Python2

我们安装的python为标准2.7版本，并且已经设置了环境变量，因此可以从命令行直接使用。此外，我们还安装了pip python包管理器。

### strings.py

Strings.py是一个由Willi
Ballenthin编写的基于python的自定义字符串工具。该文件的源码可[在此处获取](https://gist.github.com/herrcore/0b66bef7e844187169a966ef606de563)。

## 文档工具

此外，还安装了以下文档分析工具。

> oletools
>
> offvis
>
> officemalscanner
>
> pdfid
>
> pdfparser
>
> pdfstreamdumper

## 安装 FREE IDA Disassembler(x64)

如上所述，我们已将OALabs-VM installer配置为与Windows 7 32bit
VM一起使用。但这里有个不太好的消息就是，免费版的IDA反汇编程序只支持在64位Windows上运行。这意味着我们必须要配置一个单独的VM。我们再次从Microsoft下载第二个FREE
VM：<https://developer.microsoft.com/en-us/microsoft-edge/tools/vms/>。这次我们选择Windows 10 64bit VM。

![恶意软件分析虚拟机OALabs安装教程](https://image.3001.net/images/20180722/15322269905151.png!small)

按照与FREE Windows 7 VM相同的步骤，导入并配置Windows 10 64bit
VM。下载并安装IDA反汇编程序：[https://www.hex-rays.com/products/ida/support/download_freeware.shtml。](https://www.hex-rays.com/products/ida/support/download_freeware.shtml)

## 使用 FLARE-VM 安装所有工具！

如果你觉得 OAlabs-VM installer安装仍缺少了一些你喜欢的工具，则可以使用[FLARE-VM
install](https://www.fireeye.com/blog/threat-research/2017/07/flare-vm-the-windows-malware.html)来安装更大的分析工具集。这里还有一个来自RingZeroLabs的[优秀视频教程](https://www.youtube.com/watch?v=qW-LzlVQyCg)，它将引导你完成FREE Windows VM和FLARE-VM的安装。

## 演示视频

 **
*参考来源：[oalabs](https://oalabs.openanalysis.net/2018/07/16/oalabs_malware_analysis_virtual_machine/)，FB小编
secist 编译，转载请注明来自FreeBuf.COM**

