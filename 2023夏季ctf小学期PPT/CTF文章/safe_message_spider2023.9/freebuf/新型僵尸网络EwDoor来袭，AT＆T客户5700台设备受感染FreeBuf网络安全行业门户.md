近期，奇虎360 Netlab研究人员发现一个新的僵尸网络——
EwDoor，该僵尸网络利用四年前的一个严重漏洞（编号CVE-2017-6079），针对未打补丁的AT＆T客户发起猛烈攻击，仅三个小时，就导致将近6000台设备受损。

“2021年10月27日，我们的 Botmon 系统发现攻击者通过 CVE-2017-6079 攻击 Edgewater Networks
的设备，在其有效载荷中使用相对独特的挂载文件系统命令，这引起了我们的注意，经过分析，我们确认这是一个全新的僵尸网络，基于它针对 Edgewater
生产商及其后门功能，我们将其命名为 EwDoor。” 奇虎360发布报告分析。

EdgeMarc 设备支持高容量 VoIP 和数据环境，弥补了运营服务提供商在企业网络服务上的缺陷。但同时，这也要求设备需公开暴露在 Internet
上，无可避免地增加了其受远程攻击的风险。

##  **三小时内发现近6000台受损设备**

研究人员通过注册其备份命令和控制 (C2) 域，监控从受感染设备发出的请求，以确定僵尸网络的规模。不幸的是，在遇到主 C2 网络故障后，EwDoor
重新配置了其通信模型。

在短短三小时内，研究人员发现受感染的系统是 AT&T 使用的EdgeMarc Enterprise Session Border
Controller。并且专家已经确定了位于美国的5700台受感染设备（IP）。

“通过回查这些设备使用的 SSl 证书，我们发现大约有 10 万个 IP 使用相同的 SSl 证书。我们不确定与这些 IP
对应的设备有多少可能被感染，但我们可以推测，由于它们属于同一类设备，因此可能的影响是真实的。”

## EwDoor主要目的是 DDoS 攻击

研究发现，EwDoor已经经历了3个版本的更新，其主要功能可以概括为DDoS攻击和Backdoor两大类。基于被攻击设备与电话通信相关，研究人员推测EwDoor主要目的是
DDoS 攻击，以及收集通话记录等敏感信息。

EwDoor支持六大功能（基本逻辑如下所示）：

>   * 自我更新
>   * 端口扫描
>   * 文件管理
>   * DDoS 攻击
>   * 反壳
>   * 执行任意命令
>

![](https://image.3001.net/images/20211201/1638339854_61a7150ebe41e46c07b6b.png!small)

EwDoor 僵尸网络 (360 Netlab)

  

为了躲避安全专家的分析，EwDoor竟采取了一系列保护措施，例如使用TLS协议防止通信被拦截，敏感资源加密等。“修改ELF中的'ABIFLAGS'PHT以对抗qemu-user和一些高内核版本的linux沙箱。这是一个比较少见的对策，说明EwDoor的作者对Linux内核、QEMU、Edgewater设备非常熟悉。”研究报告提到。

专家还在[报告](https://blog.netlab.360.com/warning-ewdoor-botnet-is-attacking-att-customers/)中提供了有关 EwDoor 僵尸网络的其他技术细节，并分享了针对此威胁的入侵指标 (IOC)。

  

> 参考来源：
>
> https://securityaffairs.co/wordpress/125143/cyber-crime/ewdoor-botnet.html
>
> https://www.bleepingcomputer.com/news/security/ewdoor-botnet-targets-atandt-> network-edge-devices-at-us-firms/

