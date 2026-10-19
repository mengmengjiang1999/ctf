![](https://image.3001.net/images/20210320/1616249118_6056011e6f274de233852.png!small)

## OpenHaystack

OpenHaystack是一个针对蓝牙设备的跟踪框架，OpenHaystack可以利用苹果提供的Find My
Network服务来追踪个人用户的蓝牙设备，我们可以用它来创建自己的跟踪标签，并将其附加到物理对象（比如说钥匙串或背包等）上，或者将其集成到其他支持蓝夜功能的设备中（比如说笔记本等等）。

![](https://image.3001.net/images/20210320/1616249131_6056012b72c939e01c8b6.png!small)

OpenHaystack是一个应用程序，它允许我们创建自己的个人配件，而这些个人配件是可以通过苹果的 _Find My
Network_服务进行跟踪的。你只需要一台Mac和一台[ _BBC micro:bit_](https://microbit.org/)或
_任意支持蓝牙的设备_，即可使用OpenHaystack了。通过使用该应用程序，你可以在地球上任何地方跟踪你的个人配件，哪怕那里没有蜂窝网络覆盖。因为附近的iPhone设备会发现你的配件，并在有网络连接时将它们的位置上传到苹果的服务器上。

## 运行机制

OpenHaystack是苹果Find My network（或离线搜索）逆向工程和安全分析工作的成果。达姆施塔特大学的[
_安全移动网络实验室_](https://seemoo.de/)在2019年6月首次发布离线搜索结果后，我们就开始对其进行分析。通过这项工作，我们发现了iPhone设备是如何找到苹果设备的，即使它们处于离线状态。整个系统巧妙地结合了蓝牙广告、公钥加密和加密位置报告的中央数据库。我们公开了离线查找的封闭部分的规范，并进行了全面的安全和隐私分析，并且发现了两个明显的漏洞。最严重的一个漏洞是[
_CVE-2020-9986_](https://support.apple.com/en-us/HT211849)，该漏洞允许恶意应用程序访问位置数据，而苹果公司已经修复了这个问题。

![](https://image.3001.net/images/20210320/1616249201_6056017130fe829ebb4ea.png!small)

## 如何使用OpenHaystack

OpenHaystack由两个组件组成。首先，我们提供了一个macOS应用程序，它可以显示您个人蓝牙设备上一次报告的位置。其次，固件映像使蓝牙设备能够广播信标，使它们可以被iPhone发现。

## 系统要求

OpenHaystack要求macOS 11或更高系统版本。

## 工具安装

OpenHaystack应用程序需要一个用于Apple
Mail的自定义插件。它用于通过私有API从Apple服务器下载位置报告（技术说明：该插件继承了Apple
Mail使用此API所需的权限），因此需要临时禁用[
_Gatekeeper_](https://support.apple.com/guide/security/gatekeeper-and-runtime-protection-sec5599b66df/1/web/1)。我们的插件不访问任何其他私人数据，如电子邮件等（[
_源代码_](https://github.com/seemoo-lab/openhaystack/blob/main/OpenHaystack/OpenHaystackMail)）。

首先，我们需要从本项目的【Releases】页面下载预编译源码，或者大家也可以使用Xcode对源码进行手动构建。

下载好后，打开OpenHaystack应用程序，此时程序将会要求用户在~/Library/Mail/Bundle中安装Mail插件。打开终端窗口，然后运行下列命令，此时将会禁用Gatekeeper并允许苹果Mail插件运行：

    
    
    sudo spctl --master-disable

打开苹果电子邮件程序，点击“首选项→常规→管理插件”，激活OpenHaystackMail.mailbundle选项，然后重启电子邮件程序。

打开终端，然后运行下列命令，就可以重新启用Gatekeeper了：

    
    
    sudo spctl --master-enable

## 工具使用

### 添加新的配件

在创建新的配件时，我们需要输入一个配件名称，并选择合适的图标和颜色。然后应用程序会生成一个新的密钥对，用于加密和解密位置报告，私钥将存储在macOS的钥匙串keychain中。

### 部署设备

通过USB将
_支持的设备_连接到Mac上，然后点击配件名称旁的“Deploy”部署按钮，并选择相应的设备。除了使用OpenHaystack的集成部署，你还可以复制用于广告的公钥（右键单击配件）并进行手动部署。

### 显示设备位置

最长可能需要30分钟，直到你在右侧的地图上看到第一个位置报告，地图上将始终显示所有项目的最新位置。你还可以单击每个项目以检查上次更新的接收时间。通过单击“重新加载”按钮，可以更新位置报告。

![](https://image.3001.net/images/20210320/1616249172_60560154d6c89ef37595e.jpg!small)

## 苹果Find My Network工作机制

![](https://image.3001.net/images/20210320/1616249182_6056015e93b0c02afbb8c.png!small)

## 许可证协议

本项目的开发与发布遵循GNU Affero General Public License v3.0开源许可证协议。

## 项目地址

OpenHaystack：【[ _GitHub传送门_](https://github.com/seemoo-lab/openhaystack)】

## 参考资料

> [ _https://arxiv.org/abs/2103.02282_](https://arxiv.org/abs/2103.02282)
>
> [ _https://developer.apple.com/find-my/﻿_](https://developer.apple.com/find-> my/)

