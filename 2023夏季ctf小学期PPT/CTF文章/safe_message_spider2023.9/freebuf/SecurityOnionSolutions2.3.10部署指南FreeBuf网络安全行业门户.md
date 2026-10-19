（完成本文所述实验内容，需要读者具备日志采集分析、ELK和Docker环境的操作经验）

## 1.部署准备

###  **1.1 什么是Security Onion Solution**

Security
Onion是免费的开源Linux发行版，它主要用于网络威胁发现，企业安全监视和日志管理。它包括TheHive、Playbook和Sigma、Fleet和osquery、Cyber​​Chef、Elasticsearch、Logstash、Kibana、Suricata、Zeek(以前的bro-ids)等安全工具。

Security Onion始于2008年（开发年代和OSSIM相近），最初基于Ubuntu Linux发行版，直到Security
Onion的最后一个主要版本是基于Ubuntu 16.04的，所有称它为Security Onion 16.04，开源许可协议License GPLv2。

目前讲述的SOS 2.3安全洋葱解决方案是在CentOS Linux下基于容器开发，该平台命名为Security Onion 2，截至目前的最新发行版为v
2.3.10。

以下是Security Onion 2与旧版系统（v 16.04）的差异：

  * 从Ubuntu软件包移至Docker容器；

  * 支持CentOS Linux 7；

  * 将pcap收集工具从netsniff-ng(v16.04之前的版本都采用该组件)更改为Google Stenographer(一种新型抓包方案，可快速将网络包保存到硬盘)

  * 升级到Elastic Stack 7.x并支持Elastic Common Schema（ECS）；

  * 将内核模块PF_RING替换为AF_PACKET；

  * Suricata完全取代Snort；

  * 删除了Sguil，Squit和capME；

  * 增加了存储节点现在称为搜索节点；

  * 整合的新技术包括：TheHive、Strelka、支持Sigma规则、Grafana （主机的健康监控和报警）、Fleet（用于osquery管理）、Playbook（检测Playbook的工具）、Onion Hunt、Security Onion Console ；

###  **1.2 重要组件功能分析**

为了便于理解，下面将简单介绍SOS一些重要的系统组件运行原理。以前的文章（[李晨光：快速安装可视化IDS系统Security Onion（v
12）](https://zhuanlan.zhihu.com/p/302768468)）介绍过NSM（网络安全监控）的概念，NSM的理念贯穿于Secrity
Onion各系软件中，它是一种收集日志信息，分析网络威胁以及分析网络流量通过多种手段来进行故障排除和检查的实践。

  * Elastic Stack是SOS构建SIEM系统的重要组件。

  * ElasticSearch提供收集、分析、存储数据三大功能。

  * Logstash主要是用来日志的收集、分析、过滤日志的工具。Logstash使用各种输入插件来收集日志。它也可以接收OSSEC或Suricata的输入数据。

  * Kibana 可以为Logstash 和ElasticSearch 提供的日志分析友好的Web 界面，SOS系统中没有专门设计UI只能通过Kibana来可以汇总、分析和搜索重要数据日志。

  * Filebeat 收集文件数据

  * Suricata：开源IDS，可对网络异常行为进行报警。

  * Zeek (原bro-ids)：检测非标准端口上的协议标语，收集HTTP客户端和服务器标头，收集DNS请求和响应、SSH、SSL证书、LDAP / Active Directory等。在进行数据包分析过程中，Zeek和Suricata都非常消耗硬件资源。

![1609914749_5ff5597da4a962a77dba6.png!small?1609914753088](https://image.3001.net/images/20210106/1609914749_5ff5597da4a962a77dba6.png!small?1609914753088)

###  **1.3 下载**

SOS 是一个值得尝试的系统，大家可以一边下载这个大型ISO文件，一边阅读下列相关知识点。

下载2.3.10 ISO image **（约6.84GB）** 的网址

[https://download.securityonion.net/file/securityonion/securityonion-2.3.10.iso](https://link.zhihu.com/?target=https%3A//download.securityonion.net/file/securityonion/securityonion-2.3.10.iso)

MD5: 55E10BAE3D90DF47CA4D5DCCDCB67A96

SHA1: 01361123F35CEACE077803BC8074594D57EE653A

SHA256: 772EA4EFFFF12F026593F5D1CC93DB538CC17B9BA5F60308F1976B6ED7032A8D

###  **1.4 核心功能**

Security
Onion的最大特点就是虽然集成度很高，但用户安装界面却比较简单，另一个特点就是新，我相信很多开源软件大家都并不熟悉，由于它是基于Centos
Linux开发所有安全组件都经过特殊设置，而且跟操作系统完美结合，所以即使是“门外汉”部署这套系统照样能够上手。

Security Onion提供的3个大核心功能：

1）全包捕获：全包捕获通过Stenographer来实现，它会捕获Security Onion传感器的所有网络流量。就像一部网络摄像机一样，捕获网络数据包。

2）网络和端点检测：分析网络流量或主机系统，并为检测到的事件和活动提供日志和警报数据。

3）强大的分析工具：SOS紧密集成了下列工具：

  * 安全洋葱控制台（SOC）可以查看所有的NIDS和HIDS警报，从功能上看这和安全运营中心SOC差的还很远，不过很吸引眼球不是嘛。

  * The Hive，可以发现很多事件报警和日志。

  * Kibana:使我们能够通过“单一窗格”快速分析和分析由Security Onion生成的所有不同数据类型。

  * Cyber​​Chef:允许您解码，解压缩和分析数据包。

  * Playbook：用来创建检测剧本，这些剧本是完全独立的，描述了特定检测策略的不同方面。

###  **1.5 架构**

SOS不但包含了Elastic Stack（
一套完整的大数据处理系统，从日志输入、转换到存储分析、可视化），而且还添加了下列内容（这3个组件在Security Onion中作为Docker容器运行）：

  * Curator：主要用来帮助管理Elasticsearch索引和快照。

  * ElastAlert：用于查询ElasticSearch，并提供具有多种输出类型的警报机制。

  * FreqServer ：用于分析那些被频繁访问的字段，并给出访问次数排名。

![1609914802_5ff559b2a0c551ea60fa8.png!small?1609914806522](https://image.3001.net/images/20210106/1609914802_5ff559b2a0c551ea60fa8.png!small?1609914806522)

大家注意：这里我们仅在一个小型实验室中进行安装采用的是EVAL（测试评估版）模式。如果在生产环境中宜采用分布式安装模式。

###  **1.6 评估版中的日志提取**

核心管道：Filebeat [EVAL节点] –> ES提取[EVAL节点]

日志：Zeek、Suricata、Wazuh、Osquery / Fleet

Osquery发送方管道：Osquery [端点] –>舰队[EVAL节点] –>通过核心管道的ES提取

日志：WEL、Osquery、syslog

下面的实验中采用独立安装方式，此方式由运行服务器和传感器组件以及相关进程的单个虚拟机组成，最适合初学者入门。

###  **1.7 关于Docker**

由于 SO 2.3.1 采用的是 Docker CE v19.0.3容器，Docker CE (Docker Community Edition
社区版，与之对应的是EE，企业版)是免费的Docker产品的新名称，Docker
CE包含了完整的Docker平台，非常适合开发人员和运维团队构建容器APP。大家在使用SO 2.3.1时会涉及到很多ELK和Docker的知识点。

## 2、系统安装

SOS 2.3是一个比之前的Security
Onion更强大的新平台。新增的软件都很超前，所以这些附加功能导致更高的硬件配置也非常高。经过测试SOS适合VirtualBOX、和Vmware
workstation下都可顺利安装（如果你的配置满足要求的话）。

 **假设监控链路的带宽为1Gbps。**

###  **2.1 安装最低要求：**

 **CPU** ： 4 +Core

SOS系统中的Suricata和Zeek服务运行时会占用大量CPU资源。网段内监控的流量越多，所需的CPU内核数就越多。在全线速1Gbps链路中运行Suricata和Zeek服务，对于Suricata和Zeek而言至少需要CPU
10 Core以上才能满足需要。

 **Disk** ：100+GB ，推荐200GB。

由于系统中多个Docker应用的瓶颈会暴露在I/O上，强烈推荐使用SSD，至少也是磁盘整列RAID1+0。

 **RAM** ：12+GB

12G是满足安装的最基本条件，要运行顺畅至少16GB内存，推荐64或128GB，大内存用于Logstash，Elasticsearch，Lucene，Suricata，Zeek等的磁盘缓存。内存的大小，将直接影响搜索速度以及系统可靠性（内存如果太小会导致核心服务崩溃）以及处理和捕获流量的能力。

 **网络适配器** ：2 NIC

一块专用于管理的有线网络接口，使用静态IP地址。另一块网卡无IP地址，专门用来嗅探。如在生产环节下推荐Intel万兆网卡。

 **关于存储：**

SOS 2.3是计算密集型和磁盘密集型的大数据分析平台，当系统启用了完整数据包捕获之后，由传感器捕获的数据就需要大量磁盘空间来存储。

估算：假设正在监视平均50Mbps的链路，消耗磁盘空间50Mb / s = 6.25 MB / s = 375 MB /分钟= 22,500 MB /小时=
540,000 MB /天。

因此，每天存储Pcap文件需要大约540 GB的空间，而且这些数据最好存储在本地，而不推荐SAN / iSCSI / FibreChannel /
NFS之类的远程存储，它们会增加复杂性和故障点，并严重影响性能。当然如果只是做实验尝尝鲜，暂时可以不必考虑这一点。

###  **2.2 通过ISO在虚拟机中安装**

下面虚拟机采用最新版VirtualBOX，新建虚拟机的参数配置满足上面的必要条件，虚拟机（Oracle VM VirtualBOX）设置：

![1609914865_5ff559f10c7191a38642b.png!small?1609914868808](https://image.3001.net/images/20210106/1609914865_5ff559f10c7191a38642b.png!small?1609914868808)

在本文中采用ISO镜像文件进行安装，如果你希望通过USB启动机器安装，推荐使用Balena
Etcher将下载的ISO镜像文件写入到U盘（16+GB），制作成可引导的启动U盘，同时调整BIOS的启动顺序。

下面通过ISO文件在虚拟机中安装，首先选择基于图形模式安装系统。

![1609914897_5ff55a11c9060faf2f016.png!small?1609914902204](https://image.3001.net/images/20210106/1609914897_5ff55a11c9060faf2f016.png!small?1609914902204)

![1609914944_5ff55a40c2a63b913b3f2.png!small?1609914948164](https://image.3001.net/images/20210106/1609914944_5ff55a40c2a63b913b3f2.png!small?1609914948164)

安装警告：这里输入管理员名称admin（有别于root用户），并输入密码。回车后开始安装基本系统， 十分钟后，一个基本系统安装完成。漫长的过程还在后面。

通过输入“Alt+Tab”组合键，可以在4种模式下转换：

  *  **主安装界面**

  *  **Shell**

  *  **LOG**

  *  **Storage-lo**

系统安装完成后，自动重启。

![1609915269_5ff55b85e149e5c600485.png!small?1609915273521](https://image.3001.net/images/20210106/1609915269_5ff55b85e149e5c600485.png!small?1609915273521)

大约经过一刻钟，初始化安装阶段完成，此时按下回车重启系统。我们再次登录系统，此时输入admin,以及密码。

![1609915501_5ff55c6dc36b608d810c2.png!small?1609915505082](https://image.3001.net/images/20210106/1609915501_5ff55c6dc36b608d810c2.png!small?1609915505082)

根据系统提示输入Yes。下面我们开始配置系统。

![1609915419_5ff55c1becdf7c8438112.png!small?1609915423223](https://image.3001.net/images/20210106/1609915419_5ff55c1becdf7c8438112.png!small?1609915423223)在下图中我们选择第一项"EVAL"
(测试评估版)。

![1609915464_5ff55c488d378377b34f7.png!small?1609915467885](https://image.3001.net/images/20210106/1609915464_5ff55c488d378377b34f7.png!small?1609915467885)

选择标准模式安装。

![1609915492_5ff55c64474e6054b5ec8.png!small?1609915495536](https://image.3001.net/images/20210106/1609915492_5ff55c64474e6054b5ec8.png!small?1609915495536)

下面选择自动更新

![1609915539_5ff55c93e506b98e00cbb.png!small?1609915543286](https://image.3001.net/images/20210106/1609915539_5ff55c93e506b98e00cbb.png!small?1609915543286)

输入主机名称

![1609915556_5ff55ca48e9e98fb1929a.png!small?1609915559889](https://image.3001.net/images/20210106/1609915556_5ff55ca48e9e98fb1929a.png!small?1609915559889)

经过分析发现，在系统Updating packages环节，并不是从网络安装系统（网络收、发包几乎为0）。

下面选择一个网口，一般是第一个网口，我们为它分配静态IP地址、网关以及DNS。

![1609915601_5ff55cd125617cbbf23c5.png!small?1609915604369](https://image.3001.net/images/20210106/1609915601_5ff55cd125617cbbf23c5.png!small?1609915604369)

![1609915670_5ff55d16ac3c6e9c0fb5c.png!small?1609915673963](https://image.3001.net/images/20210106/1609915670_5ff55d16ac3c6e9c0fb5c.png!small?1609915673963)

关于网络设置的几个截图就不上了。

设置完一块网卡之后，开始设置另一块网卡，第二块网卡就是嗅探网卡，为其设置为嗅探功能，输入监控网段的CIDR号。

![1609915902_5ff55dfe0a76af81b88f0.png!small?1609915905262](https://image.3001.net/images/20210106/1609915902_5ff55dfe0a76af81b88f0.png!small?1609915905262)

看到这里，如果你要问为什么不给服务器设置DHCP，为什么不为第二块嗅探功能的网卡设置IP地址，那么先请复习一下基础知识（OSSIM最佳实践一书的服务器部署的内容）。

下面接着安装，选择组件（可以为空选项）

![1609915930_5ff55e1aed9c4f8e4cb54.png!small?1609915934171](https://image.3001.net/images/20210106/1609915930_5ff55e1aed9c4f8e4cb54.png!small?1609915934171)

嗯~
o(*￣▽￣*)o？？怎么又是选择组件？不重复了吗？我们接着往下走。该部安装配置时间大约1小时。硬盘分区设置和操作系统组件设置都是自动完成，而且如果你要是终端了该过程，整个安装就会前功尽弃。

输入电子邮箱地址作为登录用户名。

![1609916041_5ff55e8988eeb94c14da4.png!small?1609916044735](https://image.3001.net/images/20210106/1609916041_5ff55e8988eeb94c14da4.png!small?1609916044735)

为访问白名单设置：可以是单个IP，也可也是一个网段，但不建议设置主机名或FQDN名称。

![1609916081_5ff55eb12996cb9b3532d.png!small?1609916084419](https://image.3001.net/images/20210106/1609916081_5ff55eb12996cb9b3532d.png!small?1609916084419)

![1609916161_5ff55f01899ad4290e48e.png!small?1609916165370](https://image.3001.net/images/20210106/1609916161_5ff55f01899ad4290e48e.png!small?1609916165370)

![1609916170_5ff55f0a2e771bbfad309.png!small?1609916173411](https://image.3001.net/images/20210106/1609916170_5ff55f0a2e771bbfad309.png!small?1609916173411)

以上步骤完成之后，系统安装后期会安装以下组件，到这里还没装完，是不是都等得不耐烦了呢？下面环节如果终止，也会导致系统安装失败。

  * 生成CA中心

  * 从iso中拷贝 containers

  * 应用idstools salt state

  * 应用elasticsearch salt stae

  * 应用pcap salt state

  * 应用zeek Salt state

  * 应用curator salt state

  * 应用soc salt state

  * 应用kibana salt state

  * 应用 utility salt state

  * 验证安装

![1609916295_5ff55f876983deca88c8f.png!small?1609916298638](https://image.3001.net/images/20210106/1609916295_5ff55f876983deca88c8f.png!small?1609916298638)

当大家看到系统提示输入回车重启系统后，表示整个系统到此就安装并配置完成了，可以重启系统。

![1609916346_5ff55fbac51bd37028785.png!small?1609916350039](https://image.3001.net/images/20210106/1609916346_5ff55fbac51bd37028785.png!small?1609916350039)

注： **系统安装配置完成后，虚拟机文件夹容量约为22GB。如果你的磁盘空间小于30GB，会导致配置过程意外终止，整个安装前功尽弃！**

现在我们就可以在客户机浏览器地址栏输入IP了，接着显示登录界面，输入刚才输入的电子邮件地址和口令来登录系统。

![1609916775_5ff56167a62daa6718357.png!small?1609916778910](https://image.3001.net/images/20210106/1609916775_5ff56167a62daa6718357.png!small?1609916778910)

![1609916791_5ff561778bab742a83ef0.png!small?1609916794950](https://image.3001.net/images/20210106/1609916791_5ff561778bab742a83ef0.png!small?1609916794950)

###  **2.3 关键元素 SOC 报警控制台**

安全洋葱控制台（SOC）使您可以访问我们的新警报界面。该界面为您概述了Security
Onion生成的警报。图中，启用Acknowledged切换功能仅会显示先前已被分析师确认的警报。

启用该Escalated切换将仅显示以前由分析人员升级为TheHive的警报状态栏。

![1609916812_5ff5618cc8b62fcc9859d.png!small?1609916816255](https://image.3001.net/images/20210106/1609916812_5ff5618cc8b62fcc9859d.png!small?1609916816255)

看到下面界面，是不是感觉似曾相识以下是Security Onion数据总览，这里也是仪表盘的主页，内容比较长，下图仅截取一部分。

![1609916838_5ff561a68e761fc12f973.png!small?1609916842944](https://image.3001.net/images/20210106/1609916838_5ff561a68e761fc12f973.png!small?1609916842944)

![1609916855_5ff561b746a53eba5421c.png!small?1609916861164](https://image.3001.net/images/20210106/1609916855_5ff561b746a53eba5421c.png!small?1609916861164)

查看日志消息

![1609916877_5ff561cde6624dbbd9fd5.png!small?1609916882859](https://image.3001.net/images/20210106/1609916877_5ff561cde6624dbbd9fd5.png!small?1609916882859)

Hunt event（查看威胁狩猎事件）

![1609916929_5ff56201ee15837b0409b.png!small?1609916933625](https://image.3001.net/images/20210106/1609916929_5ff56201ee15837b0409b.png!small?1609916933625)

系统内置剧本（PlayBooks）

![1609916943_5ff5620fd951262085bd8.png!small?1609916947845](https://image.3001.net/images/20210106/1609916943_5ff5620fd951262085bd8.png!small?1609916947845)

无需安装系统内置的性能监控工具-Grafana，它是一款用Go语言开发的源数据可视化工具，可以做数据监控和数据统计，带有告警功能。

![1609916963_5ff56223e70d705a59481.png!small?1609916968873](https://image.3001.net/images/20210106/1609916963_5ff56223e70d705a59481.png!small?1609916968873)

![1609916993_5ff562416d229c3577300.png!small?1609916998190](https://image.3001.net/images/20210106/1609916993_5ff562416d229c3577300.png!small?1609916998190)

还有很多GUI界面，此处就不逐一展示，到此整个系统安装完成。

### 3.必备命令

 **3.1 系统状态检测**

![1609983935_5ff667bf14ccf6a65115d.png!small?1609983938593](https://image.3001.net/images/20210107/1609983935_5ff667bf14ccf6a65115d.png!small?1609983938593)

如果所有服务都正常启动那么后面对应的提示都为“OK”。

如果服务启动时出现错误如何处理？

下面是异常情况下的例子

![1609983960_5ff667d85839f3852e44e.png!small?1609983961613](https://image.3001.net/images/20210107/1609983960_5ff667d85839f3852e44e.png!small?1609983961613)

我们发现so-elastalert服务出现ERROR。其他服务正常。输入下列命令来重启该服务。

[admin@securityonion ~]$ **sudo so-elastalert-restart**

## 3.2 查看Docker镜像

我们知道Docker
hub（[https://hub.docker.com/u/securityonion/](https://link.zhihu.com/?target=https%3A//hub.docker.com/u/securityonion/)）可以用来管理公共镜像，上面有着非常丰富的资源，我们也可以自己的镜像推送上去。在SOS的使用场景里，它有一个私有的镜像仓库，用来管理SOS内置的镜像。

系统通过 SecurityOnionISO镜像安装，然后， Docker引擎和这些 Docker镜像就可以直接通过 ISO文件(ISO文件中的
docker目录压缩包)获取了。

为了查看Dockers的镜像文件信息我们输入下列命令：

  * [admin@securityonion ~]$ sudo docker image  

## 4.测试报警

新上一套系统，一切都是陌生的，如果你没有SIEM运维经验，这套系统将举步维艰。假设你之前用过OSSIM或其他SIEM系统。一定想知道如何检验SOS的功能。最主要就是要看他的网络报警的功能是否强大，如何触发报警，方法有两个：

  * 通过重放网络攻击数据包的方式，也就是重放PCAP文件(系统中有专门用于测试的pcap文件，通过脚本就可以重放）数据包重放方式执行之后会触发下列操作
  * 1）Suricata生成IDS警报
  * 2）Zeek生成网络元数据
  * 这些触发之后的IDS警报和网络元数据将存储在Elasticsearch中我们在WebUI界面可通过Security Onion Console（SOC）进行查询。网络数据包重放有哪些技巧和门道？大家可以参考《开源安全运维平台OSSIM疑难解析》。
  * 通过TAP或者SPAN的方式

## 5.导入外部PCAP文件

有时候我们在外部系统抓取的可以PCAP文件，需要导入到SOS系统中进行分析。可以采用下面的方法进行。

将PCAP放入指定目录/opt/samples/

[admin@securityonion docker]$ sudo ls /opt/samples/1.pcap

输入命令： **sudo so-import-pcap /opt/samples/1.pcap**

##  **6.应知内容**

  *  **下面回顾一下All in One模式下系统安装条件也是最低要求**

  * CPU： 4 +Core

  * Disk：100+GB

  * RAM：12+GB

  * 网络适配器：2 NIC

  * 镜像文件安装，容量6.84GB

  * 系统安装时长：90分钟

  * SOS系统采用优化的CentOS 7 Linux系统，内置Docker CE v19.0.3容器，各组件基于Docker运行。这套强大的网络威胁发现和企业日志管理的解决方案，可以为大家在日常安全管理中发挥重要作用，作为入门者而言其安装部署难度比OSSIM略高。

下期预告：将会为大家分析SOS中的Docker容器的用途，敬请期待！

注意：如果是虚拟机安装不推荐在系统中安装VMware Tools，那样会影响Docker 桥接口的运行。

