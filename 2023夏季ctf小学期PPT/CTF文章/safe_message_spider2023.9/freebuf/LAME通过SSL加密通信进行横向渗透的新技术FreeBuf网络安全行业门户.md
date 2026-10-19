**本文主要讨论一项用于红队的被称之为“LAME”的新横向渗透技术及其缓解措施。简单来说，“LAME”技术就是利用受信任的SSL证书，在内部网络中建立加密通信信道的一项技术。在今年的8月份，Deloitte
Greece道德黑客团队成员vangelos Mourikis和Nikos
Karouzos，在都柏林举办的实践社区（CoP）峰会上，确定并展示了该项技术。**

## 简介

在渗透测试或红蓝对抗期间，我们都会尽一切努力获得对目标内网的远程访问，并在环境范围内提升权限，建立持久通信信道持续监控，并不断扩大战果直至实现方案目标。

为了建立一个隐蔽持久的通信信道，红队往往会采用许多横向渗透技术。而通常他们的做法是建立基于TCP/IP通信协议的信道（如DNS，SMB和HTTP），模拟预期的网络流量和用户行为，从而保持不被发现。但这些协议都使用未加密的通信，因此我们可以通过一些网络监控工具，NIDS/HIDS等来轻松识别这些流量。另外，就算你使用了带有自签名证书的加密通道（例如HTTPS），也同样会触发入侵检测/监控系统的警报，因为它是中间人（MiTM）攻击的一种非常常见的攻击媒介。

更新后的杀毒软件可以轻松识别这些技术，并使用了最新的启发式引擎，它们能够关联和阻止这些类型的通信信道。

 **图1** \- 未加密的通信信道（HTTP）：

![1.png](https://image.3001.net/images/20180909/1536458105_5b947d79e2cb3.png!small)

 **图2** \- 尝试使用自签名SSL证书，执行payload会产生许多错误消息，并为入侵检测/监视系统留下大量痕迹：

![2.png](https://image.3001.net/images/20180909/1536458114_5b947d82e99e0.png!small)

## “LAME”技术

那么，如果我们可以使用受信任的SSL证书在内网中进行横向渗透结果又会如何呢？

## 事实

###  **1.域名系统（DNS）**

域实现和规范 [RFC
1035](https://tools.ietf.org/html/rfc1035)（1987年11月）指出“主文件中A行的RDATA部分是一个Internet地址，表示为四个十进制数字用点分隔，且没有任何嵌入空格（例如，“10.2.0.52"
或 "192.0.5.6"）。”

私有IP地址分配稍后介绍（[RFC 1918](https://tools.ietf.org/html/rfc1918) \-私有Internet地址分配，1996年2月），未指定与公共DNS记录分配给私有IP地址有关的任何安全考虑事项。

虽然许多出版物提出了不同建议，但仍然可以将公共域名的A记录分配给私有（内部）IP地址。

### 2\. SSL 证书

证书颁发机构（[RFC
6125](https://tools.ietf.org/html/rfc6125)）执行的SSL证书的验证和签名，在很大程度上依赖于对相应DNS名称的检查。为了提高效率，签名证书不会被绑定到相应的IP地址上，因此底层架构中的更改并不会影响证书的有效性。所以，我们可以为解析到私有（内部）IP地址的公共DNS名称颁发受信任的SSL证书。

## 准备

出于概念验证（PoC）的目的，我们使用了像Cloudflare和LetsEncrypt这类的免费服务。

为了执行LAME技术，我们还需要进行以下操作：

>
> [使用LetsEncrypt的DNS验证方法](https://certbot.eff.org/docs/using.html#manual)，为internal.dotelite.gr颁发SSL证书。  
>
>
> 使用CloudFlare将DNS A记录internal.dotelite.gr分配给内部IP地址：192.168.72.141。

 **图3** \- 公共DNS名称的受信任SSL证书解析到内部IP地址上：

![3.png](https://image.3001.net/images/20180909/1536458129_5b947d91ab0ae.png!small)

## 执行

 **图4** \- 以下是“LAME”技术的执行流程图：

![4.png](https://image.3001.net/images/20180909/1536458141_5b947d9d1cdef.png!small)

红队已在IP地址192.168.72.141上，部署了一个命令和控制（CNC）服务器，并使用签名的SSL证书为internal.dotelite.gr配置了一个HTTPS服务器。

在受害者机器（192.168.72.140）上获取远程代码执行后，红队建立了一个加密的通信信道。使用PowerShell
oneliner，受害者将经历以下过程并最终连接到internal.dotelite.gr：

1.受害者在内部DNS服务器上，请求internal.dotelite.gr的DNS记录。

2.内部DNS服务器将DNS记录请求转发到Internet上的根DNS服务器。

3.公共DNS服务器（例如CloudFlare）使用指向内部IP 192.168.72.141的DNS记录进行响应。

4.内部DNS服务器接收上述DNS记录。

5.DNS记录存储在内部DNS服务器的缓存中，并且可以在内网中提供多个类似的请求。

6.DNS记录被转发给受害者。

7.受害者将使用受信任的SSL证书与攻击者的内部IP 192.168.72.141建立加密通信信道。

 **图5** \- PowerShell oneliner“LAME”技术（Step 0）：

![5.png](https://image.3001.net/images/20180909/1536458160_5b947db03db2a.png!small)

 **图6** \- 将internal.dotelite.gr子域解析到IP 192.168.72.141的DNS解析流量（Steps 1-6）：

![6.png](https://image.3001.net/images/20180909/1536458171_5b947dbb96fff.png!small)

 **图7** \- TLS通信（Step 7）：

![7.png](https://image.3001.net/images/20180909/1536458184_5b947dc8b9543.png!small)

 **图8** \- 内网中功能齐全的加密通信信道（Step 7）：

![8.png](https://image.3001.net/images/20180909/1536458200_5b947dd849a8c.png!small)

 **图9** \- 上述命令执行的网络流量（Step 7）：

![9.png](https://image.3001.net/images/20180909/1536458214_5b947de602336.png!small)

## 总结

获得解析为内部IP地址的公共DNS名称的受信任SSL证书并非不可能。一旦获取，我们则可以将其用于在内部网络中建立加密通信信道。这不仅可以让我们的通信信道更加隐蔽，还可以帮助我们躲过入侵检测/监控系统。

此外，LAME技术还可用于APT中。结合端口转发和代理，红队可以在内部网络获得初始立足点后在目标环境中创建多个隐蔽枢纽点，并通过Internet上的外部CNC服务器进行控制。

## 缓解措施

由于通信的加密性和交换SSL证书的有效性，导致这种横向渗透技术难以被检测发现。而阻止内部网络中主机之间的HTTPS流量，则可能会导致合法服务的可用性问题，因此似乎并不是一个可行的解决方案。我们的建议是在内部网络中强制使用集中式DNS服务器，并为所有请求的DNS条目创建特定的监控用例。分析已解析的DNS记录，并进一步调查分配给内部IP地址的潜在可疑条目。此外，我们建议增强主机级别的监控功能，以便及时的识别可能具有相同结果的替代攻击路径(例如，监控本地“etc/hosts”文件的变化)。

 **更新（04/09/2018）：** 除了上述建议之外，你还可以在内部集中式DNS服务器中启用反重绑定保护（例如--stop-dns-rebind
，[dnsmasq](http://www.thekelleys.org.uk/dnsmasq/docs/dnsmasq-man.html)中的--rebind-domain-ok选项）。

 ***参考来源：[dotelite](https://dotelite.gr/the-lame-technique/)，FB小编 secist
编译，转载请注明来自FreeBuf.COM**

