**随着互联网的不断发展，安全问题也越来越受到企业的重视。但安全问题往往需要大量资金的投入，例如聘请安全工程师，产品研发，测试等流程。这对于那些原本就资金紧缺的企业而言，是绝对无法接受的。因此，为了减少在这方面的资金投入，许多安全人员都会选择使用一些开源软件来替代。**

事实上，无论是学习，试验，还是在生产基础上进行部署，安全专业人员长期以来都将开源软件视为其工具包的重要组成部分。
下面我们为大家整理推荐10款，你应该了解/值得使用的开源安全工具。

##  **Nessus**

![nessuslogo_02.png](https://image.3001.net/images/20180612/15287660493737.png!small)

Nessus可以说是是目前全世界最多人使用的系统漏洞扫描与分析软件。根据sectools.org的数据显示，Nessus是[最受欢迎的漏洞扫描器](http://sectools.org/)，也是目前使用的第三大流行安全程序。

Nessus有免费版和商业版。目前的版本，Nessus
7.1.0，是一个商业版本，虽然它是免费的个人家庭使用。目前2005年的版本仍然是[开源免费](http://repository.slacky.eu/slackware-12.1/network/nessus/2.2.11/)的。

虽然Tenable保留了第2版，但它已经在几个不同的方向上分叉开发。Nessus知识仍然是一项宝贵的职业技能。

## Snort

![Snort.png](https://image.3001.net/images/20180612/15287660646105.png!small)

正如成千上万的IT安全专业人员首先从Nessus学习漏洞扫描一样，Snort一直是入侵检测系统（IDS）知识的起点。snort有三种工作方式：嗅探器，数据包记录器和网络入侵检测系统。因此，它可以是自动化安全系统的核心，也可以是一系列商业产品的组件。

目前Snort为思科所有，Snort将继续发展并由一个活跃的社区负责开发。Snort作为一款重要的开源软件，可以说是安全从业者必须要了解和学习的软件之一。

## Nagios

![Nagios_Screen.jpg](https://image.3001.net/images/20180612/15287662714751.jpg!small)

Nagios是一款开源的免费网络监视工具，能有效监控Windows、Linux和Unix的主机状态，交换机路由器等网络设备，打印机等。与许多其他开源软件包一样，Nagios也提供免费版和商业版。

[Nagios Core](https://www.nagios.org/projects/nagios-core/)是开源项目的核心，基于免费的开源版本。可以通过[插件](https://www.nagios.org/projects/nagios-plugins/)监控单个产品或执行单个任务；大约有50个由Nagios开发的“官方”插件和超过3000个社区贡献的插件。

Nagios的用户界面可以通过桌面，Web或移动平台的[前端](https://www.nagios.org/downloads/nagios-core-frontends/)进行修改，并且可以通过其中一种可用的[配置工具](https://www.nagios.org/projects/nagios-config-tools/)来管理配置。

## Ettercap

![Ettercap.png](https://image.3001.net/images/20180612/15287662879705.png!small)

如果你需要测试你的企业网络以抵御中间人攻击（MITM），那么[Ettercap](https://www.ettercap-project.org/)将会是你的首选工具。该项目自2001年首次发布以来，一直在做一件事 - 即发起MITM攻击。

Ettercap当前支持四种基本的攻击模式：基于IP，基于MAC以及两种基于ARP策略的攻击。在扫描测试攻击的过程中，Ettercap可以提供有关网络及其设备的大量信息。作为整体安全工具包的一部分，Ettercap在MITM攻击方面做的堪称优秀。

## Infection Monkey

![Infection_Monkey.png](https://image.3001.net/images/20180612/15287662994315.png!small)

[Infection
Monkey](http://www.guardicore.com/infectionmonkey/)是一款由以色列安全公司GuardiCore在2016黑帽大会上发布的数据中心安全检测工具，其主要用于数据中心边界及内部服务器安全性的自动化检测。

用户界面是Infection Monkey的显著特点之一。 尽管一些开源安全项目提供了极简主义的UI或依赖于GUI的插件或皮肤，但Infection
Monkey具有与许多商业软件工具相同的GUI。Infection
Monkey的源代码你可在[GitHub](https://github.com/guardicore/monkey)上获取到。

## Delta

![delta_arch
\(1\).png](https://image.3001.net/images/20180612/15287663565775.png!small)

相对于传统网络的安全测试，软件定义网络（SDN）的安全问题则是一个处在发展阶段的领域 -这也是[Delta](https://www.opennetworking.org/incubator-projects/delta/)被开发出来的重要原因之一。

作为开放网络基金会（ONF）的一个项目，Delta在SDN中寻找潜在的问题，并探讨这些问题以帮助确定它们的可利用性。Delta具有内置的fuzzing功能，旨在探测已知或未知的网络漏洞。

Delta的代码和可执行程序可在[GitHub](https://github.com/OpenNetworkingFoundation/DELTA)上查看/下载。

## Cuckoo Sandbox

![Cuckoo_Sandbox.jpg](https://image.3001.net/images/20180612/15287663709883.jpg!small)

有很多方法可以判断一个文件是否是安全的，但这些方法都存在一定的风险，[Cuckoo
sandbox](https://cuckoosandbox.org/)是一款著名的开源沙箱系统，用于安全的测试文件，基于虚拟化环境所建立的恶意程序分析系统能自动执行并且分析程序行为。

## The Sleuth Kit

![Sleuthkit.jpg](https://image.3001.net/images/20180612/15287663911751.jpg!small)

弄清楚攻击中发生的事情可能是防止未来入侵的关键一步。[Sleuth
Kit](https://www.sleuthkit.org/)是一个开源的电子取证调查工具，它可以用于从磁盘映像中恢复丢失的文件，以及为了特殊事件进行磁盘映像分析。

[Autopsy](https://www.sleuthkit.org/autopsy/)工具是sleuth kit的一个网页接口，支持sleuth
kit的所有功能。这个工具在Windows和Linux平台下都可获取到。两者目前都拥有大量活跃的用户群体，并被积极的开发和贡献。

## Lynis

![d31faef0660348188a22512756457b84.jpeg](https://image.3001.net/images/20180612/15287665214126.jpeg!small)

[
Lynis](https://cisofy.com/lynis/)是一款Unix系统的安全审计以及加固工具，能够进行深层次的安全扫描，其目的是检测潜在的时间并对未来的系统加固提供建议。这款软件会扫描一般系统信息，脆弱软件包以及潜在的错误配置.

Lynis代码目前被托管在[GitHub](https://github.com/CISOfy/lynis)，其主要支持来自其创建者Cisofy。Lynis的特殊功能之一是，由于其Unix基础，它能够对流行的IoT开发板（包括Raspberry
Pi）进行扫描和评估。

## Certbot

![652a431ae91148ac91e5a13b198b2a6a.jpeg](https://image.3001.net/images/20180612/15287665924055.jpeg!small)

加密对许多安全标准都很重要，实施加密可能会很复杂并且代价高昂，但EFF已经试图通过像[Certbot](https://certbot.eff.org/)这样的工具来减少这些困扰，Certbot是一个开源的自动客户端，可以为你的Web服务器提取和部署SSL/TLS证书。

 ***参考来源：[darkreading](https://www.darkreading.com/threat-intelligence/10-open-source-security-tools-you-should-know/d/)，FB小编 secist
编译，转载请注明来自FreeBuf.COM**

