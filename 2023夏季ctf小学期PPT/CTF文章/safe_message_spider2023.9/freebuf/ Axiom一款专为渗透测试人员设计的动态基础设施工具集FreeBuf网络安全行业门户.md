![](https://image.3001.net/images/20200807/1596782307.png!small)

Project Axiom是一组强大又实用的动态基础设施工具集，该工具专为渗透测试人员设计，可用于管理漏洞奖励计划和渗透测试的小型动态基础设施设置。

Axiom现在非常适合个人以及小型团队使用，而且运行成本也不高，不需要花费很多时间来管理。如果正常使用该工具，每月的运行费用不到5美元，而且还有两个月免费的使用时间。

### ****DigitalOcean API密钥****

想要使用Axiom，首先需要申请一个Digitalocean API密钥，可以点击我们的推荐链接[
_https://m.do.co/c/bd80643300bd_](https://m.do.co/c/bd80643300bd)进行注册，并有机会获得免费赠送的100美元的试用积分！

### ****Bash One Liner****

（默认情况下，Ubuntu 20.04上是没有安装curl的，如果你需要使用curl，就会看到“找不到命令”的错误提示，这时请运行sudo apt
update && sudo apt install curl）命令。

    
    
    bash <(curl -s https://raw.githubusercontent.com/pry0cc/axiom/master/interact/axiom-configure)

当第一次尝试启动并运行工具配置时，我发现可用的工具和整个生态系统都非常庞大，并且在完成每一个安全任务时，甚至都有50种不同的方法来完成所有的操作。社区现在也有很多专为红队人员设计的基础设施工具和辅助设备，但它们都需要大量的准备工作才能开始使用。而且感觉在很多情况下，人们只是在发布他们所使用的东西，而没有提供任何入门的帮助或者文档。

在查看其他渗透测试发行版系统时，会面临的另一种情况是，该版本对日常的漏洞奖励计划和红队团队合作中使用的许多常用工具的支持很少。像Kali这样的发行版对于传统的网络安全来说是非常好的，但是对于漏洞泛滥和大型基础设施项目而言，它们还缺少很多出色的东西。

特别是Go工具，还有很多很棒的小型Go实用程序，例如[ _Tom Hudson_](https://github.com/tomnomnom/)，[
_Luke Stephens_](https://github.com/hakluke)和[ _Jason
Haddix_](https://github.com/jhaddix)之类的。很多Go语言程序都适用于各种漏洞奖励计划中的任务，这些实用程序通常在Bash
One Liner代码中被整合在了一起。

建立自己的“
攻击vps”，以获取shell，运行枚举工具并扫描，让程序在tmux窗口中的后台运行。您将需要手动运行并安装所有需要的工具，配置ZSH、vim和tmux。但是在Axiom的帮助下，我们只需要运行一个命令即可进行安装，然后可以使用Axiom工具箱脚本来配置新的“攻击VPS”。![](https://image.3001.net/images/20200807/1596782330.png!small)

运行“axiom-init”，2分钟即可创建一个新实例，其中包含您可能想要或需要进行的所有操作内容，以便为您的渗透测试执行网络侦察，在netcat中获取一个shell，或者您可能希望通过VPN（axiom提供了对openvpn、axiom-deploy openvpn等东西的一键式部署配置文件的支持，您很快就会拥有一个完全配置的openvpn服务器）。

完成后，只需使用“axiom-rm your-instance-12”快速确认对话框并关闭实例，对话框就消失了！它将不再花费您任何运行成本。![](https://image.3001.net/images/20200807/1596782340.png!small)

项目的初始化脚本封装了notify-send钩子，在启动所选择的计算机时就可以完成工具的配置和运行了。![](https://image.3001.net/images/20200807/1596782348.png!small)

在这个工具包中，我们尽最大可能去简化了渗透测试工具集的配置，我们创建了一系列bash封装器以辅助使用。Axiom基础镜像是由大量Bug
Hunters和Lean团队开发的，用于快速初始化和配置基础设施（并预先安装了日常使用的工具）。![](https://image.3001.net/images/20200807/1596782356.png!small)

“axiom-ssh host”可以用于连接到您的设备，可以使用“axiom-ls”查看可用的设备。![](https://image.3001.net/images/20200807/1596782365.png!small)

****使用**** ** **“**** ** **Axiom-configure**** ** **”**** **
**进行程序设置****![](https://image.3001.net/images/20200807/1596782375.png!small)

![](https://image.3001.net/images/20200807/1596782392.png!small)

## ****Axiom工具安装****

### ****支持操作系统****

我们目前正在尝试尽可能多地添加支持的操作系统，主要适用于* nix，例如MacOS，Ubuntu，Debian，Arch Linux，将来还有Kali。

> MacOS-支持
>
> Ubuntu-支持
>
> Debian-半支持-计划
>
> Arch Linux-半支持-计划
>
> Kali-未知

### ****工具依赖****

    
    
    Packer-使用v1.5.6测试
    
    fzf-使用v0.21.1测试
    
    doctl-使用v1.43测试
    
    jq-使用v1.6测试（最新版本更好）

Packer在任何地方都很容易上手，尽管是手动的，获得正确的版本非常重要，如果版本太旧，则var-file语法就会失败。

fzf同样是很常见的，不过doctl可能有点棘手，在ubuntu和ew上可以使用snap实现。除此之外，jq需要使用最新版本！

## ****有趣的截图****

这是一个有趣的开箱即用的程序，可通过subfinder获取子域，查找并解析它们，传递已解析和HTTP可能的响应，以便获取截图以供进一步检查！![](https://image.3001.net/images/20200807/1596782422.png!small)

## ****部署配置文件****

这些工作还在进行中，我们对部署配置文件的愿景是，在机器已经启动并运行后可以快速部署可能要部署的“可选附加件”。例如openvpn和covenant（都有准备好的安装脚本）。

## ****实例配置文件选择器****

对于高级用户来说，有一点值得注意的是，同时添加了axiom-select和axiom-connect脚本。Axiom-select允许选择实例名称，并将其存储在名为“profile.json”的状态文件〜/ .axiom
/目录中。初始化新服务器时也需要进行此选择。现在，选择一个实例后，就可以从任何地方运行axiom-connect并将其放入SSH
Shell中，这对于创建到VPS hackbox的“透明”连接非常有用，并且可以连接到keybindings来打开新的终端窗口。

由于notify-send的大量集成，基本上可以毫无顾忌地使用整个生态系统（也将变得更好）。

提示：如果您正在运行MacOS，请将一下内容放到bin路径中：

    
    
    notify-send
    
    #!/bin/bash
    
     osascript -e "display notification \"$2\" with title \"$1\""

## 所有的命令-解释

### ****axiom-backup****

axiom-backup 是一个用于备份您选择的实例的命令，该命令的工作原理如下：

    
    
    axiom-backup <instance>

这将在后端执行的操作是针对op用户的~/目录运行rsync传输。这个rsync传输将排除当前的主目录和预安装的文件。因此，您将只传输放置在主目录中的文件。建议创建一个工作目录并存储您可能在其中积累的所有文本文件/侦探战利品。您可以根据需要定期运行axiom-backup <instance>，并可以近乎实时地进行同步。

这样，如果需要快速关闭该实例，则可以这样做，并且可以使用下一个命令快速恢复。

### ****axiom-restore****

axiom-restore将恢复以前备份的机器（如以上命令所示）。备份的文件夹存储在~/.axiom/boxes/<box-name>中，如果要在恢复时将自定义文件添加到箱子中，则可以在~/.axiom/boxes/<box>目录中创建自定义文件/文件夹结构。一种情况可能是同步自定义单词列表。我们也考虑在将来备份$
GOPATH / bin路径，以便您可以同步自定义二进制文件和go工具。

axiom-restore是另一个使用配置文件选择器的命令。使用axiom-init命令初始化新计算机时，实例的名称将被放入~/.axiom/profile.json文件中。该文件描述了配置文件选择器的状态。可以使用axiom-select命令修改“选择”哪台计算机。

axiom-restore命令的一个典型示例如下所示：

    
    
    axiom-init
    
    axiom-restore originalbox-13
    
    # Selecting a different box
    
    axiom-select anotherbox-5
    
    axiom-restore originalbox-13

### ****axiom-select****

axiom-select是负责执行手动配置文件选择的命令。当运行axiom-select
<instance>时，它将把配置文件设置为该实例，当运行axiom-connect，axiom-restore和axiom-deploy命令时。它会记住你指的是哪一个实例。

初始化新实例时，配置文件选择器会自动设置为该新实例。但是，如果要在其他设备上部署某些设备，该怎么办？或者，如果您要将一个配置从一台计算机还原到另一台计算机，又该怎么办？

    
    
    axiom-select instance-32

### ****axiom-deploy****

axiom-deploy命令可用于在计算机初始化后部署配置文件。您可能不希望开箱即用的openvpn服务器或契约团队服务器，但您可能希望在开箱即用之后部署它！

使用axiom-deploy，一旦选择了一个实例，就可以按照以下方式部署配置文件：

    
    
    axiom-select instance-32
    
    axiom-deploy openvpn

如果需要一些示例，只需查看~/.axiom/profiles/openvpn/manifest.json文件即可。

### ****axiom-update****

Axiom的更新非常简单，它只针对运行Axiom的整个系统范围的更新。使用cd命令进入〜/ .axiom /目录中，运行git pull即可。

### ****axiom-build****

一旦使用axiom-update更新了Axiom设置，就可以使用axiom-build重新构建镜像。定期建立新的镜像是非常重要的，因为可能会改进安全性或增加新功能！

### ****axiom-connect****

axiom-connect是另一个可用于通过SSH进入Axiom实例的命令。然而，这个命令的有趣之处在于，它完全不需要参数，它仅读取当前选择配置文件中存在的任何实例，并且建立连接！

就个人而言，使用termite -e axiom-connect将其映射到keybinding，因此在初始化新实例后，可以打开与计算机的新SSH连接（例如它的本地连接！）。

### ****axiom-ls****

axiom-ls 用于列出当前的实例（以及正在运行的任何其他Droplet）。

它不要求任何参数。

### ****axiom-rm****

axiom-rm 用于删除设备，可以使用 axiom-rm <instance>来初始化设备。

### ****axiom-vpn****

axiom-vpn 用于连接到部署openvpn服务器（使用部署脚本）。

运行axiom-deploy openvpn后，可以运行axiom-vpn
<instance>，它将下载openvpn连接文件，并针对该文件运行openvpn。

### ****axiom-configure****

axiom-configure是一个可以用于配置的命令，理想情况下，它应该只运行一次，如果您犯了一个错误并弄乱了配置，建议先运行sudo rm -rf
~/.axiom/然后再运行bash的一行程序来进行上面的安装​​。

该命令将安装deps，下载并克隆Axiom代码库，将interact文件夹添加到$
PATH中，然后运行构建的第一个版本。此时将需要一个Digitalocean API密钥。

### ****axiom-ssh****

axiom-ssh 用于通过SSH连接到目标设备，可以按以下方式使用它：

    
    
    axiom-ssh <instance>
    
    axiom-ssh <instance> --tmux

如果使用--tmux标志，它将进入Axiom工具上名为main的tmux会话中。但是，如果tmux会话已经存在，它将简单地重新连接。这对于正在进行的工作、连接性较差的地方（飞机上！）或者运行多个任务时很有用。

## 项目地址

Axiom：【[ _GitHub传送门_](https://github.com/pry0cc/axiom)】

