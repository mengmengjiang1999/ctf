##  概述

 **加密通信现已无处不在，但从某种程度上说，加密不仅保证了信息的机密性，也没有阻碍对流量进行分析。某些协议（如 SSH 与
TLS）可以确保流量分析工具不能直接读取内容，但对传输数据的大小和顺序的分析是可以提供帮助的。本文将概述 Zeek 用于提供 SSH
连接可见性的一些工作。**

任何在对外暴露的 IP 上观察过网络流量的人都可以看到互联网中的各种连接。未许可的、来自互联网扫描仪、爬虫、蠕虫与反射的连接都是很常见的。类似
[Shodan](https://www.shodan.io/)、[Greynoise](https://greynoise.io/) 与
[Censys](https://censys.io/)
的服务提供商创造了互联网范围内的扫描数据，提供用于取证和情报调查的历史数据集。虽然这些服务都是良性的，也可以向提供商提交排除扫描的要求。但并不是所有的扫描都是良性的，比如
[Mirai
的变体](https://www.usenix.org/system/files/conference/usenixsecurity17/sec17-antonakakis.pdf)。僵尸网络会扫描
SSH 和 Telnet 服务，并尝试使用默认的密码列表进行登录尝试。

##  Zeek 的 SSH 暴力破解检测

检测针对主机的 SSH 暴力破解是 Zeek 提供的“开箱即用”的能力之一。启用针对 SSH
暴力破解的[策略脚本](https://github.com/zeek/zeek/blob/4c6b35970d3742abc3a23f2f4a83cceee5c7a94c/scripts/policy/protocols/ssh/detect-bruteforcing.zeek)后，Zeek 就可以跟踪每个主机成功、失败的 SSH 连接尝试，以此来检测 SSH 暴力破解。该脚本检测的是 SSH
暴力破解尝试，如果是凭据窃取，则称为 [Credential
Stuffing](https://github.com/OWASP/CheatSheetSeries/blob/master/cheatsheets/Credential_Stuffing_Prevention_Cheat_Sheet.md)。

此脚本的逻辑是使用 [SumStats
框架](https://docs.zeek.org/en/stable/frameworks/sumstats.html)统计
ssh_auth_successful 和 ssh_auth_failed 事件的数量。每次发生 ssh_auth_failed
事件时，计数器都会递增。如果计数器超过配置的阈值（password_guesses_limit），就会发出告警。如果通过密码猜测最终登录成功服务器，脚本也会发出告警。如果在
ssh_auth_failed 事件后看到 ssh_auth_successful 事件，且发起和响应的主机也相同，Zeek
推断已经通过暴力破解登录成功。进一步理解 SSH 协议对理解到底是什么原因导致了 ssh_auth_successful 事件与
ssh_auth_failed 事件是十分必要的。

##  SSH 协议

[RFC 4251](https://www.ietf.org/rfc/rfc4251.txt) 对 SSH 的描述：SSH
协议是一种用于通过不安全网络进行安全远程登录和其他网络服务的协议。该协议由三个子协议组成，具有不同的消息类型，以便在控制端和客户端之间交换信息。这三个子协议负责不同的任务，包括：

> [传输层协议](https://tools.ietf.org/html/rfc4253.html)，用于建立加密并完善其他两个子协议
>
> [认证协议](https://tools.ietf.org/html/rfc4252)，用于验证 SSH 连接的端点
>
> [连接协议](https://tools.ietf.org/html/rfc4254)，用于提供交互式会话、命令执行、X11 Forwarding
> 或是端口连接

下图描述的就是典型 SSH 连接交换信息的过程。最初建立 TCP 连接，两个端点都发送它们的版本标示字符串，这与 HTTP 协议中的 User-Agent
类似，但 SSH
中需要双方都各提供一个。在交换后进行初始密钥交换，这有助于创建对称密钥加密隧道。在加密开始之前要明确协商使用的密码套件、压缩方法和其他配置选项。图中顶部的框就显示了这种交换，标记为
In the clear。值得注意的是，在明文中交换的信息也被
[HASSH](https://engineering.salesforce.com/open-sourcing-hassh-abed3ae5044c)
等指纹技术所使用。

尽管 SSH 协议没有强制要求加密开始后必须要做什么。但大多数客户端都向服务器发送类型为 ssh-userauth
的服务请求消息，（在下图的绿色框内标记为“Encrypted”的第一条发送的消息），指示客户端希望向服务器发起身份验证。服务器通过接受消息
SSH_MSG_SERVICE_ACCEPT 或断开消息 SSH_MSG_DISCONNECT 响应客户端的服务请求，断开消息将终止 TCP 连接。如果
TCP 连接没有终止，则可以认为服务器向客户端发送了接受消息。测量服务器接受消息的大小也是信息泄漏的一个例子。这就是 Zeek 如何推断成功的 SSH
身份验证，从而生成 ssh_auth_successful 事件的关键。

![blog-image-1.png](https://image.3001.net/images/20200311/15839048751464.png!small)

身份验证完成后，客户端会向服务器发起另一个服务请求。与类型为 ssh-authuser 的第一次服务请求不同，第二次服务请求的类型为 ssh-connection。同样的，如果服务器接受客户端的服务请求，将会发送服务接受消息而不是断开消息。如上图的紫色框中所示，交换连接协议。这些消息用于发出特定的请求，如用于交互式登录的
PTY 会话、用于 X11 Forwarding 的 X11 会话或用于 SFTP 的会话。在 SSH
协议中测量此时数据包的大小也可用于推断客户端和服务器之间建立的会话类型，例如[检测文件上传](https://github.com/reservoirlabs/bro-scripts/tree/master/exfil-detection-framework)时就具备易于识别的包大小。

##  Zeek 中与 SSH 相关的事件

通过了解 SSH 协议和数据包大小的不同状态，就可以了解 Zeek 何时会生成 ssh_auth_successful 和 ssh_auth_failed
事件。[代码](https://github.com/zeek/zeek/blob/4c6b35970d3742abc3a23f2f4a83cceee5c7a94c/src/analyzer/protocol/ssh/SSH.cc#L110-L148)中也显示了
SSH 分析器以 generate_ssh_auth_ 为开头的事件产生的逻辑。

查看[之前的代码提交记录](https://github.com/zeek/zeek/commit/05ecac24971cba58f58c28704cdb2b77bee2dbf1#diff-659b84fd121bd8a965997d9166e2d509L62)可以发现灵感的来源，[SSH.cc
文件的历史](https://github.com/zeek/zeek/blob/05ecac24971cba58f58c28704cdb2b77bee2dbf1/src/analyzer/protocol/ssh/SSH.cc)显示当前的代码逻辑是在四年前添加的。ProcessEncrypted
函数中的逻辑可以总结如下：

> 1、确定服务器的 SSH_MSG_SERVICE_REQUEST 数据包的大小，标记为Auth service accept
>
> 2、确定客户端的未经身份验证的状态（在图中被标记为 Optional auth request (none)）是否会导致服务器发出
> SSH_MSG_USERAUTH_SUCCESS 或 SSH_MSG_USERAUTH_FAILURE 的响应 a. 身份验证成功将比步骤 1
> 中的数据包小 16 个字节 b. 失败的包大小会存在差异
>
> 3、在步骤 2a 中成功消息发送到客户端前，确定服务器是否发送了图中标记为 Optional banner 的可选 Banner
>
> 4、检查服务器对在图中标记为 Auth request (publickey) 的客户端第二次身份认证尝试的响应包大小 a. 认证成功将比步骤 1
> 中的数据包小 16 个字节 b. 失败的包大小与步骤 2b 的大小相同

这就了解了 Zeek 如何推断身份认证成功的，但还没有了解如何推断身份认证失败的。ssh_auth_failed 事件永远不会是 SSH
协议分析器触发的，而是 Zeek scriptland
触发的。[这些代码](https://github.com/zeek/zeek/blob/4c6b35970d3742abc3a23f2f4a83cceee5c7a94c/scripts/base/protocols/ssh/main.zeek#L262)显示一旦
SSH 连接将要在 Zeek Core 中过期就会触发 ssh_auth_failed 事件。任何未触发 ssh_auth_successful
事件又完成的 SSH 连接都有可能触发 ssh_auth_failed 事件。回想一下上一节中，ssh_auth_failed
事件被用于在请求主机与响应主机之间进行计数，与设置好的阈值进行比较。

##  回到暴力破解

最近 Corelight 实验室分析了有关 SSH
数据包的一组细节，这些数据包是从一个规模适中的网络收集来的。数据集包括匿名的远程主机与本地主机的主机号、端口号、时间戳与数据包大小。在我们分析的过程中，很快就发现只需要检查数据包的大小与排序，就可以对连接行为进行恶意推断，即便是加密流量也没问题。

为了描述这一发现，我们首先将数据集划分成不同的会话，然后将会话表示为图形。这些图形表示在概念上与 Joy 使用的 [SPLT
分析](https://github.com/cisco/joy/issues/200#issuecomment-419482182)有些类似。

下图是认证尝试的示例，X 轴为时间，红色表示本地主机发送的分组大小，蓝色表示远程主机发送的分组大小。这个示例是远程主机 1 试图对本地主机 66
进行暴力破解。本地主机 66
可能配置为响应客户端身份验证尝试失败前要延迟一段时间，小数据包交换之间的间隙就可以证明这一点。会话开始时的大数据包可能反映了初始密钥交换，即上图中的
kex_algorithms…。

![blog-image-2.png](https://image.3001.net/images/20200311/15839049263279.png!small)

下图是成功连接的 SSH 会话示例，本地主机已经成功通过远程主机验证，并开始将数据传送给远程主机。本地主机生成 PDU 的大小可能超过以太网的
MTU，在图中包的大小总是接近 1500。假设这些都成功后，远程主机 78 属于 GitHub 的基础设施，这个 SSH 会话可能用于传输一些小文件。

![blog-image-3.png](https://image.3001.net/images/20200311/15839049549647.png!small)

下面两幅图是成功认证后长时间传输大量数据的图形表示。第一幅图显示了客户端传输大量数据的 SSH 会话示例，第二幅图显示了服务器传输大量数据的 SSH
会话示例。

![blog-image-4.png](https://image.3001.net/images/20200311/15839049763006.png!small)

![blog-image-5.png](https://image.3001.net/images/20200311/15839049981791.png!small)

##  总结

这篇文章讲述了 Zeek 提供加密通信可见性的众多方法之一。仅仅是传输的内容被加密并不能阻止所有的分析方法，本文中讨论的许多概念也可以用于
TLS，[一些研究](https://arxiv.org/pdf/1805.11544.pdf)也针对 HTTP
进行了研究。此外，其他[一些研究](https://www.trisul.org/blog/analysing-ssh/post.html)表明包分析可以用于识别那些包含对 [Shell 或 pty
访问请求](https://github.com/trisulnsm/apps/blob/master/analyzers/ssh-alert/ssh_dissect.lua#L13)的 SSH_MSG_CHANNEL_REQUEST 数据包的大小。

SSH 无处不在，如果你想要了解 Zeek 关于 SSH 的可见性的更多信息，请参阅 [HASSH Zeek
软件包](https://github.com/salesforce/hassh)与默认提供的 [SSH
策略脚本](https://github.com/zeek/zeek/tree/4c6b35970d3742abc3a23f2f4a83cceee5c7a94c/scripts/policy/protocols/ssh)。如果还想进一步深入了解
Corelight 实验室是如何对网络数据进行深入分析的，请联系我们！

特别感谢 Vlad Grigorescu 对本文的贡献。

 ***参考来源：[corelight](https://corelight.blog/2019/05/07/how-zeek-can-provide-insights-despite-encrypted-communications/)，FB 小编 Avenger 编译，转载请注明来自
FreeBuf.COM**

  

