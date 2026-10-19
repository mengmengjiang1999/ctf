## 1\. 简介

什么是SIEM？英文全称为Security Information Event
Management，安全信息与事件管理，Gartner定义为：安全信息和事件管理（SIEM）技术通过对来自各种事件和上下文数据源的安全事件的实时收集和历史分析来支持威胁检测和安全事件响应。

而在安全的解决方案中，Elasticsearch被广泛的应用，比如著名的开源网络回溯分析系统Arkime，
著名开源EDR产品Wazuh、著名开源IDS系统SELKS都使用Elasticsearch作为其数据存储。很多人不知道的是Elasticsearch自身也提供了一套开箱即用的SIEM系统。本文就对Elasticsearch
SIEM做一些简单的介绍，方便大家使用Elasticsearch SIEM快速搭建企业自身SIEM系统。

![1648883163_6247f5dbc36691f746816.png!small?1648883163113](https://image.3001.net/images/20220402/1648883163_6247f5dbc36691f746816.png!small?1648883163113)

## 2\. Elasticsearch SIEM收集器

安装Elasticsearch、Logstash、Kibana的文章网上有很多，我在这里不赘述，大家请自行搜索。

本文中使用的ELK 7.2.0 版本。

打开Kibana,在添加数据源的页面可以看到有专门的安全分析页面。从这个页面可以看出Elasticsearch SIEM
已经适配的网络安全方面的数据类型。我们先看一下现在Elasticsearch SIEM 内置的一些类型。

![1649929606_6257ed8678543b05033ea.png!small?1649929606144](https://image.3001.net/images/20220414/1649929606_6257ed8678543b05033ea.png!small?1649929606144)

Auditbeat是一种轻量级的数据收集器，您可以将其安装在服务器上，以审核系统上用户和进程的活动。

Winlogbeat用于密切监控基于 Windows 的基础设施上发生的事件。使用 Winlogbeat，将 Windows 事件日志流式传输至
Elasticsearch 和 Logstash。本质上是对windows系统上的事件查看器的监控。

![1649929622_6257ed96bb0d51944a889.png!small?1649929622262](https://image.3001.net/images/20220414/1649929622_6257ed96bb0d51944a889.png!small?1649929622262)

Cisco ：接收思科网络设备日志，包含思科防火墙的日志。使用filebeat收集；

CoreDNS logs：coredns是一个用go语言编写的开源的DNS服务，被广泛应用。 使用filebeat收集；

Envoyproxy ：是一款 CNCF 旗下的开源项目，由C++编写的高性能代理服务器。使用filebeat收集；

Iptables / Ubiquiti ：iptables 是 Linux 防火墙系统的重要组成部分，iptables
的主要功能是实现对网络数据包进出设备及转发的控制。当数据包需要进入设备、从设备中流出或者由该设备转发、路由时，都可以使用 iptables
进行控制。使用filebeat收集；

NetFlow:是一种网络监测功能，可以收集进入及离开网络界面的IP封包的数量及资讯，最早由思科公司研发，应用在路由器及交换器等产品上。经由分析Netflow收集到的资讯，网络管理人员可以知道封包的来源及目的地，网络服务的种类，以及造成网络拥塞的原因。使用logstash收集；

osquery是一款由facebook开源的，面向OSX和Linux的操作系统检测框架。 允许通过使用SQL的方式来获取操作系统的数据。
使用filebeat收集；

Suricata是一个免费、开源、成熟、快速、健壮的网络威胁检测引擎。Suricata引擎能够进行实时入侵检测(IDS)、内联入侵预防(IPS)、网络安全监控(NSM)和离线pcap处理。使用filebeat收集；

Zeek是一个开源的、被动网络流量分析软件。它主要被用作安全监测设备来检查链路上的所有流量中是否有恶意活动的痕迹。使用filebeat收集。

根据Elasticsearch SIEM已经适配的数据类型，我们可以构建一个小型的网络安全环境：

![1649929648_6257edb0c495454679165.png!small?1649929648593](https://image.3001.net/images/20220414/1649929648_6257edb0c495454679165.png!small?1649929648593)

## 3\. 接收其他安全数据

当然，Elasticsearch毕竟是外国公司，他的SIEM适配的很多数据格式可能在国内并不常用，有时候就需要把国内自己的设备数据接入Elasticsearch
SIEM；

国内主流厂商的设备几乎都支持Syslog,而日志接收和处理是ELK中Logstash和filebeat的强项。

如果是数据比较简单，发送日志的数据源也较少，建议使用filebeat,较为轻量级，节省系统资源，也支持简单的数据处理，只是6.0版本以后不能进行多输出。

如果数据需要复杂的处理，日志类型比较多，建议使用Logstash, 毕竟提供了强大的数据处理过滤能力，也支持多输出。

如果日志源比较多，也需要处理，就需要使用多个filebeat + Logstash的架构了。

在接入日志的时候，要注意可以使用logstash的Pipeline对日志进行处理，转为ECM。

ECM（Elastic Common
Schema），是Elastic定义的一套数据格式，协助分析来自不同来源的数据。相同的数据格式更方便使用Elastic预制的模版和一些内置规则。比如在市面上，不同厂商的对设备IP的字段可能有各种叫法，比如ip、deviceIp、host_ip等等，在ECM规则中，不管原来的设备ip是什么，需要统一转换成source.ip。

ECM规则地址:<https://github.com/elastic/ecs>

## 4\. Elasticsearch SIEM页面展示

在Kibana中点击下面小锁的图标，就可以进入SIEM的展示页面。

这里主要有概览、主机、网络、时间线四个Tab页。

概览比较简单，除了一些介绍，主要统计了接收到的主机和网络信息。

![1649929677_6257edcd28978c302113b.png!small?1649929677082](https://image.3001.net/images/20220414/1649929677_6257edcd28978c302113b.png!small?1649929677082)

主机模块，主要由Auditbeat、Winlogbeat提供数据。主要对主机数量、用户身份验证、IP信息、异常进程、主机事件进行数据统计和图表展示。

![](https://image.3001.net/images/20220414/1649930053_6257ef45c68132900b6bf.png!small)

网络信息里，主要是从filebeat、auditbeat、packetbeat获取。主要对网络中的网络综合信息、流量TOP10、DNS TOP10进行展示。

![1649930096_6257ef707a8283db13114.png!small?1649930096080](https://image.3001.net/images/20220414/1649930096_6257ef707a8283db13114.png!small?1649930096080)

时间线，是一个按照某种字段搜索进行时间排序的展示页面。这里可以根据自己环境中的数据创建过滤条件，结果以时间展示。下图中是对环境中所有的登录信息进行展示，可以查看是否有异常登录情况。当我们知道已知的一些病毒规则或者暴露端口，可以使用对应的过滤条件进行过滤。

![1649930112_6257ef8031f6782c13d70.png!small?1649930111666](https://image.3001.net/images/20220414/1649930112_6257ef8031f6782c13d70.png!small?1649930111666)

![1649930142_6257ef9e3ea83cceede87.png!small?1649930142003](https://image.3001.net/images/20220414/1649930142_6257ef9e3ea83cceede87.png!small?1649930142003)

除了这几个模块以外，在kibana的展示模块中还有内置了很多类型的展示页面。下图是winlogbeat的内置展示统计页面，Elasticsearch
SIEM内置的数据类型都有自己的展示页面。

![1649930159_6257efaf8c66648e572ed.png!small?1649930159097](https://image.3001.net/images/20220414/1649930159_6257efaf8c66648e572ed.png!small?1649930159097)

## 5\. 总结

Elasticsearch
SIEM提供了中小型企业一种自建SIEM的解决方案。优点是开源、组件齐全、文档详细、易扩展等等。缺点是Elasticsearch和kibana国产话做的一般，而且无论是Elasticsearch的DSL、kibana的KQL还是Logstash的Pipeline都有一定的学习成本。本文只是对Elasticsearch
SIEM做了简单的介绍，Elasticsearch和很多安全工具的组合都会有化学反应，而且Elasticsearch已经出到了8.1版本，和Endpoint
security组成了Limitless XDR的解决方案，在官方的文档中原来的SIEM模块也被最新的Elastic
Security所取代。现在和关于Elasticsearch安全相关的文章有很多，有兴趣的朋友可以自己去探索。笔者也计划在以后深入介绍Elasticsearch
SIEM相关知识。

