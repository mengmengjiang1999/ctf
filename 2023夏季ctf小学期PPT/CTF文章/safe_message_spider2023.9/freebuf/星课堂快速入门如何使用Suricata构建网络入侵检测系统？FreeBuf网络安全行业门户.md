一. Suricata简介

Suricata是一个免费、开源、成熟、快速、健壮的网络威胁检测引擎。Suricata引擎能够进行实时入侵检测(IDS)、内联入侵预防(IPS)、网络安全监控(NSM)和离线pcap处理。Suricata使用强大而广泛的规则和签名语言来检查网络流量，并提供强大的Lua脚本支持来检测复杂的威胁。使用标准的输入和输出格式(如YAML和JSON)，使用现有的SIEMs、Splunk、Logstash/Elasticsearch、Kibana和其他数据库等工具进行集成将变得非常简单。Suricata项目和代码由开放信息安全基金会(OISF)拥有和支持，OISF是一个非盈利基金会，致力于确保Suricata作为一个开源项目的开发和持续成功。

二.Suricata主要特点

l支持从nfqueue中读取流量

l 支持分析离线pcap文件和pcap文件方式存储流量数据

l支持ipv6

l支持pcap，af_packet，pfring，硬件卡抓包

l 多线程

l支持内嵌lua脚本，以实现自定义检测和输出脚本

l支持ip信用等级

l 支持文件还原

l兼容snort规则

l 支持常见数据包解码：IPv4, IPv6, TCP, UDP, SCTP, ICMPv4, ICMPv6, GRE, Ethernet, PPP,
PPPoE, Raw, SLL, VLAN, QINQ, MPLS, ERSPAN, VXLAN

l 支持常见应用层协议解码：HTTP, SSL, TLS, SMB, DCERPC, SMTP, FTP, SSH, DNS, Modbus,
ENIP/CIP, DNP3, NFS, NTP, DHCP, TFTP, KRB5, IKEv2, SIP, SNMP, RDP

三.Suricata主要特点

3.1 规则配置

配置文件位置：/etc/suricata/suricata.yaml

规则目录位置：/etc/suricata/rules

先设置HOME_NET与EXTERNAL_NET，推荐HOME_NET填写内网网段，EXTERNAL_NET设置为any

注意：如果HOME_NET设置了any，EXTERNAL_NET设置！HOME_NET的话会报错，如果HOME_NET设置了内网地址，EXTERNAL_NET设置为！$HOME_NET的话，有些内网之间的告警就无法匹配到。

一般为了测试方便，都设置为any。

![v2-f13fccc79d3e0d1af38be26ad8d16533_720w.png](https://image.3001.net/images/20220422/1650608392_626249084f0726e52b86e.png!small)

​

编辑切换为居中

添加图片注释，不超过 140 字（可选）

通过配置文件的default-rule-path设置规则目录，rule-files来选择启用那些规则

其他配置文件有：

classification-file：

/etc/suricata/classification.config

reference-config-file：

/etc/suricata/reference.config

threshold-file：

/etc/suricata/threshold.config

3.2 规则配置

更多参考官网文档：

低版本手册：

http://suricata.readthedocs.io/en/suricata-4.0.4

高版本手册：

https://suricata.readthedocs.io/en/latest/index.html#

suricata和snort区别：

https://suricata.readthedocs.io/en/latest/rules/differences-from-snort.html

下面是suricata规则的常见格式：

![v2-9a56a2144a94841eb103708e455e7cf9_720w.png](https://image.3001.net/images/20220422/1650608393_626249091b36b23f4ace3.png!small)

​

编辑切换为居中

添加图片注释，不超过 140 字（可选）

3.2.1 规则头部

规则头部对应属性：

alert tcp $EXTERNAL_NET $FILE_DATA_PORTS -> $HOME_NET any

规则行为；协议；源ip；源端口；流量方向；目标ip；目标端口；红色代表规则头

规则行为，根据优先级排列：

pass 如果匹配到规则后，suricata会停止扫描数据包，并跳到所有规则的末尾

drop ips模式使用，如果匹配到之后则立即阻断数据包不会发送任何信息

reject 对数据包主动拒绝，接受者与发送中都会收到一个拒绝包

alert 记录所有匹配的规则并记录与匹配规则相关的数据包

协议：

在规则中指定匹配那些协议，suricata支持的协议要比snort多一些

TCP、UDP、ICMP、IP（同时用与TCP与UDP）、http、ftp、smb、dns

源ip，目标ip：

支持单个ip，cidr，ip组，[96.30.87.36,96.32.45.57]，所有主机any，以及规则文件中配置的ip变量$HOME_NET（受保护的ip段）与$EXTERNAL_NET（其他所有ip）

源端口/目标端口：

支持设置单个端口80，端口组[80,8080],端口范围[1024:65535]以及any任意端口,还可以在配置文件中添加端口组，通过！号来进行排除

流量方向：

-> 单向流量，从源ip到目标ip的单项流量

<> 双向流量，2个ip往返之间的流量

3.2.2 规则选项

规则选项使用分号分隔，有两种格式：

（keyword）:（settings）;

(keyword);

即由关键字和设置值（部分没有）组成

关键字有很多类，大致有以下几种：

元关键字、paylaod关键字、及各类协议关键字等

![v2-148d67f6ed098d9f89577639850d809e_720w.png](https://image.3001.net/images/20220422/1650608393_62624909861deb1c358a2.png!small)

​

编辑切换为居中

添加图片注释，不超过 140 字（可选）

3.3 规则提取测试

下面是经常使用的测试命令：

suricata -c /etc/suricata/suricata.yaml -T #-T参数测试规则是否存在问题

suricata -r test.pcap -k none -S test.rules #测试流量和规则匹配情况

运行生成四个结果文件：

![v2-9de18507788b6c778d623b012e3b764a_720w.png](https://image.3001.net/images/20220422/1650608394_6262490a1ae742f6f706b.png!small)

​

编辑

添加图片注释，不超过 140 字（可选）

![v2-d84df53984e595bf6f3aa8d8c1749195_720w.png](https://image.3001.net/images/20220422/1650608394_6262490a8140bbe4e05e2.png!small)

​

编辑切换为居中

添加图片注释，不超过 140 字（可选）

![v2-13e339f19d9186ad08f16920d0ff71a2_720w.png](https://image.3001.net/images/20220422/1650608395_6262490b49abcf4655caf.png!small)

​

编辑切换为居中

添加图片注释，不超过 140 字（可选）

如果有签名命中则出现在eve.json与fast.log中。其中，fast.log记录了包含的具体alert情况，包括时间、五元组信息、告警id和告警信息等，是我们本次重点分析的对象。eve.json则记录了告警信息、flow流信息、协议解析的信息（例如http，dns等），以及攻击的payload等。

