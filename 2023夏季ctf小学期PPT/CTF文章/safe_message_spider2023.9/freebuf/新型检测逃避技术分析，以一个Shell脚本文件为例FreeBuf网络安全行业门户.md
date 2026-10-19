## 背景

Linux 平台上的攻击者通常使用恶意 Shell 脚本作为初始的攻击向量，拉取恶意 Payload 到失陷主机执行。

最初，攻击者只使用 base64 等编码方案来进行检测逃避。目前，攻击者正在采用更新的技术，包括禁用防火墙、监控代理等方式进行检测逃避。

本文将以一个 Shell
脚本文件（[5050506ad2ccea35fe3b7aba63c4f413](https://www.virustotal.com/gui/file/39ac019520a278e350065d12ebc0c24201584390724f3d8e0dc828664fee6cae/detection)）为例，进行分析。

## 卸载监控 Agent

监控 Agent 是监控系统中进程和网络相关活动的安全软件。监控 Agent 会记录各种日志，这可以在进行事件调查分析时提供帮助。恶意 Shell
脚本试图：

卸载阿里云的 Aegis

卸载腾讯云的 YunJing

![](https://image.3001.net/images/20210801/1627830194_6106b7b2dc7e15ade880a.png!small)

## 禁用防火墙

大多数服务器都会部署防火墙作为防御机制，所以攻击者会在恶意 Shell 脚本试图禁用防火墙（ufw）。与此同时，攻击者还会清除 iptables 的规则。

![](https://image.3001.net/images/20210801/1627830204_6106b7bc6251be8d31197.png!small)

攻击者还会禁用基于不可屏蔽中断（nmi）实现的 watchdog。watchdog
是一种可配置的定时器机制，会在给定的条件和时间产生中断。为了规避这种防御机制，攻击者会使用 sysctl 禁用 watchdog 功能。

![](https://image.3001.net/images/20210801/1627830217_6106b7c9d7a2c83524289.png!small)

## 禁用安全模块

恶意 Shell 脚本通常会禁用 SElinux、Apparmor 等 Linux
安全模块。这些安全模块都实施强制访问控制（MAC）策略，管理员可以通过模块控制应用程序的安装/访问权限。

### AppArmour

AppArmour 是 Linux 中的一项安全功能，用于锁定 Firefox
等应用程序提高系统安全性。用户可以通过向某个应用程序授予有限的权限来限制应用程序的访问。

![1627829234_6106b3f23984c32f7ca82.png!small?1627829233338](https://image.3001.net/images/20210801/1627829234_6106b3f23984c32f7ca82.png!small?1627829233338)

### SElinux

SElinux 也是 Linux 的一项安全功能，安全管理员可以通过配置应用程序限定安全上下文。在某些 Web 服务器上，Shell
功能会被禁用或被限制，攻击者通常会绕过/禁用此功能。

![1627829221_6106b3e5d4cf087a53e73.png!small?1627829220978](https://image.3001.net/images/20210801/1627829221_6106b3e5d4cf087a53e73.png!small?1627829220978)

## 修改 ACL

访问控制列表（ACL）包含文件和程序的权限规则。文件系统 ACL 控制那些用户可以访问那些文件，用户拥有哪些权限。Linux 中的 setfacl
可用于修改、删除 ACL。

![1627829206_6106b3d6863467ecf3267.png!small?1627829205719](https://image.3001.net/images/20210801/1627829206_6106b3d6863467ecf3267.png!small?1627829205719)

## 更改属性

Linux 中的 chattr 可用于设置/取消设置文件属性，攻击者会将恶意软件设置为不可变，使用户不能删除恶意软件。

![](https://image.3001.net/images/20210801/1627830225_6106b7d13f52c4da3c81a.png!small)

![](https://image.3001.net/images/20210801/1627830234_6106b7daac85aa0e320dd.png!small)

## 重命名常用程序

实用程序 wget、curl 通常用于下载恶意文件，如果能够修改程序名称，监控特定程序名称的安全程序有可能就不会产生告警。

![1627829381_6106b485b5bcfe7b34843.png!small?1627829380810](https://image.3001.net/images/20210801/1627829381_6106b485b5bcfe7b34843.png!small?1627829380810)

![1627829368_6106b4785fcbaf84ef11c.png!small?1627829367602](https://image.3001.net/images/20210801/1627829368_6106b4785fcbaf84ef11c.png!small?1627829367602)

## 结论

攻击者不断使用更复杂、更新颖的方法进行检测规避，更完整、全面地监控和记录系统的活动正变得越来越重要。建议所有人都应该定期监控不受信任的二进制执行产生的可疑进程、可疑事件和可疑流量。一定要定期更新系统和固件，进行安全升级。

## IOC

> 39ac019520a278e350065d12ebc0c24201584390724f3d8e0dc828664fee6cae
>
> 1ad0104478301e73e3f49cdeb10f8c1a1d54bccf9248e34ff81352598f112e6b
>
> b60ffcc7153650d6a232b1cb249924b0c6384c27681860eb13b12f4705bc0a05
>
> 3b280a4017ef2c2aef4b3ed8bb47516b816166998462899935afb39b533890ad
>
> 7b6f7c48256a8df2041e8726c3490ccb6987e1a76fee947e148ea68eee036889
>
> d7c4693f4c36d8c06a52d8981827245b9ab4f63283907ef8c3947499a37eedc8

## 参考来源

> [Uptycs](https://www.uptycs.com/blog/evasive-techniques-used-by-malicious-> linux-shell-scripts)

