随着Python越来越流行，在安全领域的用途也越来越多。比如可以用requests
模块撰写进行Web请求工具；用sockets编写TCP网络通讯程序；解析和生成字节流可以使用struct模块。而要解析和处理网络包在网络安全领域更加普遍，时常我们会使用tcpdump和wireshark（tshark）。但是如果要自己写程序进行处理，则需要更灵活的语言包（库），这就是本文要介绍的Scapy。

![](https://image.3001.net/images/20220510/1652112578_62793cc2057eba47d9043.png!small)

# 概述

Scapy
是一个用来解析底层网络数据包的Python模块和交互式程序，该程序对底层包处理进行了抽象打包，使得对网络数据包的处理非常简便。该类库可以在在网络安全领域有非常广泛用例，可用于漏洞利用开发、数据泄露、网络监听、入侵检测和流量的分析捕获的。Scapy与数据可视化和报告生成集成，可以方便展示起结果和数据。

Scapy的基本理念是提出一个基于领域特定语言，从而轻松快速地进行有线格式（Wire Format）管理。

# 安装运行

Scapy可以通过pip安装:

pip install scapy

也可以通过发行版的包管理器安装，比如yum，但是其版本可能太老已经过时。

也可以通过直接从官方仓库clone源码安装：

git clone github /secdev/scapy

然后，可以可以简单地运行：

cd scapy

./run_scapy

![1652112593_62793cd17b503af9cbc0c.png!small](https://image.3001.net/images/20220510/1652112593_62793cd17b503af9cbc0c.png!small)

# 用法示例

# 解析PCAP抓包

用Scapy做的最简单的事情就是读取PCAP文件。让我们下载Wireshark的sip-rtp-opus-hybrid.pcap 示例PCAP数据包为例子：

用rdpcap()函数引入PCAP文件，读取其内容的函数：

>>> pkts = rdpcap("sip-rtp-opus-hybrid.pcap")

>>> pkts

<sip-rtp-opus-hybrid.pcap: TCP:0 UDP:7 ICMP:0
Other:0>![1652112620_62793cecd47b63dc327d2.png!small](https://image.3001.net/images/20220510/1652112620_62793cecd47b63dc327d2.png!small)

为了更详细读取PCAP文件中的数据，可以使用PcapReader从打开的文件句柄中迭代地读取数据包，一次一个包，bing实例化的对象：

>>> fd = open("sip-rtp-opus-hybrid.pcap", "rb")

>>> reader = PcapReader(fd)

>>> reader

<scapy.utils.PcapReader at 0x7f913c7c24e0>

>>> for CC in reader:

...: print(CC)

...:

![1652112633_62793cf98ee9107049b52.png!small](https://image.3001.net/images/20220510/1652112633_62793cf98ee9107049b52.png!small)

>>> fd.close()

如上面所示，每个数据包都以有线格式提供。Scapy 将每个数据包以网络层的堆栈。Scapy层对象对应于网络协议及其有线格式。

获取第一个数据包并检查IP层是否可用：

>>> first= CC[0]

>>> first.haslayer(IP)

True

>>> IP in first

True

要解析来自特定层的数据包，可按想要的层对其进行索引，并让Scapy打印所有字段：

![1652112656_62793d10baea01706c3dd.png!small](https://image.3001.net/images/20220510/1652112656_62793d10baea01706c3dd.png!small)

要以十六进制打印数据包，可以使用hexdump()功能：

>>> hexdump(first)

![1652112665_62793d19a83ba75e94726.png!small](https://image.3001.net/images/20220510/1652112665_62793d19a83ba75e94726.png!small)

为了完全解析和完美地输出一个数据包，需要调用show()方法：

>>> first.show()

![1652112675_62793d238a5b4d44d0612.png!small](https://image.3001.net/images/20220510/1652112675_62793d238a5b4d44d0612.png!small)

可以看到，上面未能有效地解析SI负载。这是因为Scapy主要处理二进制协议
网络堆栈的较低部分，而SIP不是。但是可以引入第三方模块来解析一些应用层协议，比如HTTP协议。

# 实时抓包解析

比如可以读取带有预先捕获的数据包的PCAP文件，如果要做一些数据包嗅探，如果系统准备好在混杂模式下使用网络接口，可以调用sniff()从网卡获取一些数据包的函数：

>>> for CC in sniff(count=5):

...: CC.show()

...:

![1652112685_62793d2d702bbd387beb3.png!small](https://image.3001.net/images/20220510/1652112685_62793d2d702bbd387beb3.png!small)

Scapy中也可以使用和Wireshark（tshark）、tcpdump 相同BPF语法来过滤嗅探到的数据包和许多其他工具支持：

>>> for CC in sniff(filter="udp", count=5):

...: CC.show()

...:

要将捕获的数据包保存到 PCAP 文件中以供进一步分析，可以使用wrpcap()函数来导出到文件：

>>> capture = sniff(filter="udp", count=5)

>>> capture

<Sniffed: TCP:0 UDP:5 ICMP:0 Other:0>

>>> wrpcap("udp.pcap", capture)

# 发送ping包

除了可以嗅探（捕获和解析）网络数据包，但Scapy也支持生成数据包进行各种主动欺骗：网络扫描、服务器探测、通过发送攻击系统格式错误的请求等等。

下面尝试ping一个服务器，涉及到要给服务发送一个ICMP数据包：

>>> CC = IP(dst="XXX") / ICMP()

>>> CC.show()

![1652112697_62793d395388d625dfff6.png!small](https://image.3001.net/images/20220510/1652112697_62793d395388d625dfff6.png!small)

然后调用sr1()函数，可以发送一个ICMP数据包（即ping），等待返回数据包返回：

>>> rr=sr1(CC)

Begin emission:

Finished sending 1 packets.

...*

Received 4 packets, got 1 answers, remaining 0 packets

>>> rr

![1652112708_62793d442b02f02984049.png!small](https://image.3001.net/images/20220510/1652112708_62793d442b02f02984049.png!small)

上面得到了正确的ICMP回复。

为了发送多个数据包和接收响应（例如实现ping扫描），可以用sr()功能。发送多个数据包，但等待单个响应。还可以用sr1_flood()功能。

# 网络协议层乱序

Scapy通过重载了Python“/”运算符来实现层堆叠，不再不强制按照网络层顺序执行，以达到以预期人为顺序执行（这在某些测试和应用中很有用）。

![1652112716_62793d4c44156380199b3.png!small](https://image.3001.net/images/20220510/1652112716_62793d4c44156380199b3.png!small)

>>> CC=ICMP() / UDP() / IP() / IP()

>>> CC

<ICMP |<UDP |<IP frag=0 proto=ipencap |<IP |>>>>

>>> CC.show()

###[ ICMP ]###

type= echo-request

code= 0

chksum= None

id= 0x0

seq= 0x0

###[ UDP ]###

sport= domain

dport= domain

len= None

chksum= None

###[ IP ]###

version= 4

ihl= None

tos= 0x0

len= None

id= 1

flags=

frag= 0

ttl= 64

proto= ipv4

chksum= None

src= 127.0.0.1

dst= 127.0.0.1

\options\

###[ IP ]###

version= 4

ihl= None

tos= 0x0

len= None

id= 1

flags=

frag= 0

ttl= 64

proto= hopopt

chksum= None

src= 127.0.0.1

dst= 127.0.0.1

\options\

>>> hexdump(CC)

WARNING: No IP underlayer to compute checksum. Leaving null.

0000 08 00 F7 65 00 00 00 00 00 35 00 35 00 30 00 00 ...e.....5.5.0..

0010 45 00 00 28 00 01 00 00 40 04 7C CF 7F 00 00 01 E..(....@.|.....

0020 7F 00 00 01 45 00 00 14 00 01 00 00 40 00 7C E7 ....E.......@.|.

0030 7F 00 00 01 7F 00 00 01

![1652112726_62793d5649bcf4f79b410.png!small](https://image.3001.net/images/20220510/1652112726_62793d5649bcf4f79b410.png!small)

设计成这样，主要是为了可以生成任意的网络数据包（故意损坏的），用来进行漏洞测试研究或利用。当然对于对这一块不熟悉的用户， **强烈建议不要轻易尝试**
，以免造成问题。

# 数据可视化

Scapy也支持通过PyX（需要预先安装模块）对数据进行可视化。可以输出为一个数据包或数据包列表的图形(PostScript/PDF格式)：

>>> xxCC[404].pdfdump(layer_shift=1)

>>> xxCC[404].psdump("/tmp/xxCC.eps",layer_shift=1)

![1652112735_62793d5fd4f7d4409d09a.png!small](https://image.3001.net/images/20220510/1652112735_62793d5fd4f7d4409d09a.png!small)

# 模糊测试

利用函数fuzz()可以利用快速构建生成随机测试值利用模糊模板并循环发送进行测试。以下示例中，IP层正常，UDP和NTP层被fuzz。UDP
校验和将正确，UDP 目标端口将被 NTP重载为123，并且NTP版本将被强制为4，所有其他端口将被随机化：

send(IP(dst="target")/fuzz(UDP()/NTP(version=4)),loop=1)

................^C

Sent 16 packets.

# 总结

抛砖引玉，我们在此介绍了一些基本的Scapy用途，当然这只是scapy庞大功能中的冰山一角，更多的用法请参考官方文档。

据虫虫所知目前有些工具已经使用了scapy包：

Trackerjacker: WiFi网络映射器

![1652112745_62793d69c3c39580a748e.png!small](https://image.3001.net/images/20220510/1652112745_62793d69c3c39580a748e.png!small)

Wifiphisher: Wifi接入点创建工具

![1652112755_62793d7324845849568a3.png!small](https://image.3001.net/images/20220510/1652112755_62793d7324845849568a3.png!small)

Sshame：SSH 公钥暴力破解器

![1652112763_62793d7bdd22e51bfc548.png!small](https://image.3001.net/images/20220510/1652112763_62793d7bdd22e51bfc548.png!small)

ISF：工业系统的利用框架。

![1652112772_62793d84a2d9b391016e3.png!small](https://image.3001.net/images/20220510/1652112772_62793d84a2d9b391016e3.png!small)

还有一些更特殊的用途则需要各位hacker来进一步发掘。

