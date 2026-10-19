***本工具仅供技术分享、交流讨论，严禁用于非法用途。**

## 介绍：

DeAuth是使用Linux Shell编写的一个DeAuth快速攻击工具，可以借助无线网卡快速的进行MDK3攻击。

我们可以在以下系统中进行攻击（已测）：

Kali Linux（Armhf、Arm64、Amd64）、Turmux、Debian等

使用之前，我们需要先安装“airmon-ng”、“iwconfig”、”airodump-ng”、“mdk3”、“ifconfig”。

并且，你需要使用一个支持Monitor模式的无线网卡，我们才可以快速的攻击。

## 使用方式：

Linux Shell
直接执行deauth.sh，根据工具的中文提示，进行使用即可。注意，攻击的方式是通过信道进行MDK3解除认证攻击，部分无线网卡可能会发热严重。

如果MDK3不适用于部分WLAN，所以你可以使用MDK4进行攻击，只需要把MDK3更改为MDK4即可。

## 预览：

![](https://image.3001.net/images/20210712/1626055023_60eba16f2ac51ae6eb09d.png!small)

GIT地址：https://gitee.com/moxinwangluo/DeAuth/

