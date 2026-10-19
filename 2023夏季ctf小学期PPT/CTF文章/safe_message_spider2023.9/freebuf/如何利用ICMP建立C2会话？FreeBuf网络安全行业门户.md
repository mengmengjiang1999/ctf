**在之前的文章中我为大家展示了如何获取各种C2会话。本文我将为大家介绍另一种获取C2会话的方法，即利用ICMP来建立C2会话。在正式开始之前，让我们先来简单了解下什么是ICMP？
ICMP是（Internet Control Message
Protocol）Internet控制报文协议。它允许互联网连接的设备在遇到传送数据包的问题时，将错误消息发送回源IP地址。这个协议非常的实用，但对于攻击者而言它的用途却不止于此。**

为了设置我们的会话，我们需要先来下载几个文件。第一个文件将在攻击机上运行。你可以在这里下载到：<https://github.com/inquisb/icmpsh>。我在我的Kali机器上克隆了该文件。第二个文件是一个PowerShell脚本，我们将在受害者机器上运行。你可以在此处下载到：<https://github.com/samratashok/nishang/blob/master/Shells/Invoke-PowerShellIcmp.ps1>。

在我的攻击机实例上，我克隆了icmpsh。

![如何利用ICMP建立C2会话](https://image.3001.net/images/20190120/1547946809_5c43cb399b870.jpg!small)

我运行了python脚本来启动我的侦听程序。

![如何利用ICMP建立C2会话](https://image.3001.net/images/20190120/1547946825_5c43cb4940218.jpg!small)

如下所示，运行该脚本需要为其提供源IP以及目标IP地址。

![如何利用ICMP建立C2会话](https://image.3001.net/images/20190120/1547946839_5c43cb57b7408.jpg!small)

可以看到什么都没发生，这是由于我们未进行客户端的相关设置。转到GitHub站点并保存该源码。

![如何利用ICMP建立C2会话](https://image.3001.net/images/20190120/1547946860_5c43cb6c4b0de.jpg!small)

获取PowerShell代码后，我们需要将其传输到受害机器上。传输的方法有很多，这里我就不再详细说明了。这只是一个测试所以我直接拷贝了该文件。

现在脚本已准备就绪，下面让我们来运行该脚本。这是一个PowerShell脚本，所以我们需要打开一个PowerShell命令提示符。

![如何利用ICMP建立C2会话](https://image.3001.net/images/20190120/1547946886_5c43cb860222e.jpg!small)

打开PowerShell命令提示符后，我们来运行该脚本。导航到放置文件的位置并运行以下命令。

![如何利用ICMP建立C2会话](https://image.3001.net/images/20190120/1547946907_5c43cb9b41b3f.jpg!small)

成功运行脚本后，在我的kali上我获取到了一个会话连接。如下：

![如何利用ICMP建立C2会话](https://image.3001.net/images/20190120/1547946925_5c43cbaddc223.jpg!small)

现在我可以运行任何命令，就像我在受害者机器上一样。

那么，使用ICMP建立C2会话的好处又是什么呢？所有通信都被注入到ICMP数据包，包括请求和响应。由于所有流量都在ICMP数据包中，因此基于代理的防火墙无法检测到这些流量。但这并不是说无法检测到这些连接，而是可以绕过某些防火墙规则。

*参考来源：[blackhillsinfosec](https://www.blackhillsinfosec.com/how-to-c2-over-icmp/)，FB小编secist编译，转载请注明来自FreeBuf.COM  

