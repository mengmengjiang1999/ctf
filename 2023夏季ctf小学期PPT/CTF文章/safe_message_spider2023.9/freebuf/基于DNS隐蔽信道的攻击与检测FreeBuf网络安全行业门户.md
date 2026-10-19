>
> **免责声明：本文作者竭力保证文章内容可靠，但对于任何错误、疏漏或不准确的内容，作者不负任何责任。文章部分内容来源于网络是出于传递更多信息的目的，对此不负任何法律责任。本文仅用于技术分享与讨论，严禁用于其他用途。**

## 一、基于DNS的隐蔽通信

 **企业网络经常面临网络攻击者窃取有价值和敏感数据的威胁。复杂的攻击者越来越多地利用DNS通道来泄露数据，以及维护恶意软件的隧道C
&C（命令和控制）通信。这是因为DNS对于几乎所有应用程序来说都是如此重要的服务，从本地计算机到Internet的任何通信（不包括基于静态IP的通信）都依赖于DNS服务，限制DNS通信可能会导致合法远程服务的断开，因此，企业防火墙通常配置为允许UDP端口53（由DNS使用）上的所有数据包，即DNS流量通常允许通过企业防火墙而无需深度检查或状态维护。从攻击者的角度来看，这使得DNS协议成为数据泄露地隐蔽通信通道。**

攻击者利用DNS的一种方法是注册域名（例如，fengrou2019.club），以便攻击者在主机受害者中的恶意软件可以将有价值的私人信息（例如信用卡号，登录密码或知识产权）编码为形式为arbitrary-string.fengrou2019.club的DNS请求。此DNS请求由全局域名系统中的解析器转发到fengrou2019.club域的权威服务器（在攻击者的控制下），后者又向主机受害者发送响应。这为攻击者在主受害者及其命令和控制中心之间提供了低速但隐蔽的双向通信信道。如图所示为Bot在获取控制命令后回传窃密信息的流程图。

![0.png](https://image.3001.net/images/20190802/1564738814_5d4404fecb342.png!small)

DNS这种穿透防火墙的能力为攻击者提供了一个隐蔽的通道，尽管是低速通道，通过将其他协议（例如，SSH，FTP）隧道传输到命令和控制中心，可以通过该通道泄露私有数据并保持与恶意软件的通信。现代恶意软件和网络攻击在很大程度上依赖于DNS服务，使其活动可靠且难以跟踪。例如­­­，2017年发现的远程访问木马DNSMessenger使用DNS查询和响应在受感染的主机上执行恶意PowerShell命令。

##  **二、DNS检测**

监控网络DNS活动和阻止可疑域已被证明是抵御此类攻击的有效技术。对于分析DNS流量以识别恶意网络活动，人们提出了很多检测方法，比如使用字符频率分析的DNS隧道检测方法等。

对于任何组织用以对抗各种安全威胁来说，在企业级水平上的单点Bot检测至关重要。本文要介绍的DNS检测工具BotDAD，它就是部署在企业的网络边界上进行单点Bot检测的，它通过观察主机在一段时间内的DNS指纹，尝试寻找域正常的主机行为相当不同的异常行为，从而识别受感染的主机。

本文以BotDAD工具为例，将对BotDAD进行DNS检测的技术分析。

### 1\. DNS检测特征

BotDAD中统计分析了15种DNS的行为特征，如下:  

序号 | DNS特征 | 描述  
---|---|---  
p1 | 每小时DNS请求的数量  
| 受感染的僵尸主机每小时的请求数量往往高于正常主机。  
  
p2 | 每小时不同的DNS请求数  
| 感染DGA恶意软件的主机往往比普通主机具有更多不同的请求。  
  
p3 | 单个域的最大请求数  
| 帮助检测DNS隧道，敏感信息通过DNS协议传输。  
  
p4 | 每分钟平均请求数  
| 用于检测受恶意软件感染的计算机，该计算机不使用短暂的DNS请求，而是使用休眠间隔定期对DNS请求做出贡献。  
它的计算方法是将主机发送的请求数除以主机处于活动状态并使用DNS服务的持续时间。  
  
p5 | 每分钟最多请求数  
| 帮助检测感染恶意软件的僵尸程序，这些恶意软件使用短暂的DNS请求通过域生成算法生成的多个URL与C＆C服务器进行通信。  
  
p6 | MX记录查询数  
| 是网络中基于垃圾邮件的僵尸网络的强有力指标。  
  
p7 | PTR记录（从ip地址到域名的一条记录）查询数  
| 有助于检测网络中存在异常行为的主机以及可能的感染。  
  
p8 | 查询的不同DNS服务器的数量  
| 有助于检测网络中具有异常行为的机器，因为标准系统查询多个DNS服务器的情况并不常见。  
TLD: top level domain，顶级域名  
SLD: second level domain，二级域名  
  
p9 | 不同TLD请求的数量  
| 在检测基于DGA的机器人方面非常有效，这些机器人不仅生成具有不同二级域的随机域，还生成具有不同顶级域名的随机域。  
  
p10 | 不同SLD请求的数量  
| 是网络中存在基于DGA的机器人的强烈指示。  
  
p11 | 唯一性比率  
| 是在主机每小时发送至少1000个请求的假设下，发送的请求数与发送的不同请求数之比。  
  
p12 | Failed/NXDOMAIN请求的数量  
| 是网络中主机感染的一个非常强的指标。  
它通过主机维护响应代码等于DNS_RCODE_NXDOMAIN的响应数。  
  
p13 | 已解析IP地址的不同城市数量  
| 是一个强烈的异常指标，尤其是当IP地址分布在各个城市时。  
使用Maxmind数据库（“Geo2 Databases | MaxMi，2017”）获得城市映射的IP地址。  
  
p14 | 已经解析的ip地址的不同国家数量  
|  
  
p15 | Flux ratio  
| 在主机发送至少100个查询并且已收到至少100个响应的条件下，发送的不同请求与解析的不同ip地址的比率。  
  
  
通过对BotDAD工作做源码解析，找到其核心类与核心函数，其中便对以上15种DNS特征进行了使用。

核心类：BotDAD/DnsAnalyser.py/classs Network

核心函数：BotDAD/DnsAnalyser.py/classs Network/find_anomaly()

### 2.BotDAD安装与使用

2.1 安装：

依赖python版本：python2.7

系统环境：windows

预安装：

![1.png](https://image.3001.net/images/20190802/1564738859_5d44052b9cab8.png!small)

2.2 数据集准备：

BotDAD提供了3种预备数据集的方式：

2.2.1 抓包、过滤、切片

（1）使用wireshark抓包

（2） 包过滤命令

    
    
    tshark.exe -r "input.pcap" -F pcap -Y dns -t ad -w"big.pcap"     #windows

或

    
    
    tshark -r "input.pcap" -F pcap -Y dns -t ad -w"big.pcap"         #linux

（3）切片命令

    
    
    editcap.exe -F pcap -i 3600"big.pcap" "slice.pcap"              #windows

或

    
    
    editcap -F pcap -i 3600"big.pcap" "slice.pcap"                  #linux

2.2.2 直接可用：20160421_150521.pcap

Manmeet Singh（BotDAD论文作者）提供，可直接使用。

链接：<https://drive.google.com/file/d/14cRY6aEQz_xVsfySBb4Ik6mPYDLoIc88/view?usp=sharing>

2.2.3 直接可用：校园DNS网络流量

数据集由BotDAD论文作者提供。

2016年4月至5月期间，由超过4000个活跃用户组成的校园DNS网络流量（在高峰负载时间内）为10个随机日，可在数据集中的每小时PCAP文件中获得。

（由于10GB数据限制，目前只能上传Day0（Full）和Day1（部分）的流量）

数据集链接为：[
_https://data.mendeley.com/datasets/zh3wnddzxy/1_](https://data.mendeley.com/datasets/zh3wnddzxy/1)

2.3 使用前的问题与解决：

2.3.1 包导入问题

下载后，尝试直接运行main.py，遇到一个问题：

![2.png](https://image.3001.net/images/20190802/1564739153_5d44065169314.png!small)

由于问题出现在pcapparser.py，而在BotDAD开源的项目中，公布的是PcapParser.pyc文件，因此需要pyc反编译，本文使用uncompyle实现反编译。

通过反编译得到PcapParser.py，利用python2命令行环境验证，发现问题就出在这里：

![3.png](https://image.3001.net/images/20190802/1564739172_5d440664ce0c7.png!small)

2.3.2 问题解决

查看[win-inet-pton的API](https://pypi.org/project/win-inet-pton/)，发现其中提供的对于inet_ntop的使用方法与代码中的使用方法不太一样。

![4.png](https://image.3001.net/images/20190802/1564739271_5d4406c7848cb.png!small)

检索反编译的PcapParser.py代码中，inet_ntop出现的地方，发现只有两处：

一处是文件导入的地方：![5.png](https://image.3001.net/images/20190802/1564739291_5d4406dbc6c61.png!small)

另一处的用法其实与[win-inet-pton的API](https://pypi.org/project/win-inet-pton/)中提供的用法是一致的：![6.png](https://image.3001.net/images/20190802/1564739308_5d4406ec9a071.png!small)

所以我这边尝试修改PcapParser.py代码，然后用PcapParser.py替代PcapParser.py用于BotDAD的运行：

修改前，原inet_ntop的导入方式：![7.png](https://image.3001.net/images/20190802/1564739366_5d4407269a6d6.png!small)

修改后，直接导入win_inet_pton即可：![8.png](https://image.3001.net/images/20190802/1564739406_5d44074e8b66f.png!small)

完成替换之后，再运行main.py，如图，运行成功，问题解决：![9.png](https://image.3001.net/images/20190802/1564739426_5d4407621b8a8.png!small)

一开始运行，首先在main.py的上一级目录中生成3个文件：![10.png](https://image.3001.net/images/20190802/1564739442_5d440772cd3db.png!small)

执行到console>的耗时还是挺长的，大概7分钟。![11.png](https://image.3001.net/images/20190802/1564739461_5d44078578ed2.png!small)

2.4 BotDAD的使用

BotDAD的使用命令总结如下：![12.png](https://image.3001.net/images/20190802/1564739662_5d44084eaa883.png!small)

 ****

2.4.1l命令

我这里使用l命令，主机列表包含571个主机。

![13.png](https://image.3001.net/images/20190802/1564739835_5d4408fb4f0c6.png!small)

2.4.2 m命令  

![14.png](https://image.3001.net/images/20190802/1564739865_5d440919873d6.png!small)![15.png](https://image.3001.net/images/20190802/1564739865_5d4409199a3a6.png!small)

输入主机列表中的一个IP地址，无返回，在main.py的同级目录下生成文件：

![16.png](https://image.3001.net/images/20190802/1564739900_5d44093c5adae.png!small)![17.png](https://image.3001.net/images/20190802/1564739900_5d44093c5b89b.png!small)

2.4.3 p命令

生成图像，plot DNS query timeline：

![18.png](https://image.3001.net/images/20190802/1564739919_5d44094f7d631.png!small)

![19.png](https://image.3001.net/images/20190802/1564739962_5d44097a0335f.png!small)

2.4.4 d/D命令

主机IP后面出现的数字与主机列表中最后一列的数字对应一致。

D命令是将d展示部分做保存。

![20.png](https://image.3001.net/images/20190802/1564740012_5d4409acacfd1.png!small)![21.png](https://image.3001.net/images/20190802/1564740012_5d4409acba488.png!small)

用D命令：  
![22.png](https://image.3001.net/images/20190802/1564740038_5d4409c6cf405.png!small)![23.png](https://image.3001.net/images/20190802/1564740038_5d4409c6d7e2a.png!small)

2.4.5 h命令

saving的过程可能会比较慢。

![24.png](https://image.3001.net/images/20190802/1564740071_5d4409e794b97.png!small)

好长时间之后：![25.png](https://image.3001.net/images/20190802/1564740081_5d4409f13b19a.png!small)

在main.py的上一级目录下生成html文件:![26.png](https://image.3001.net/images/20190802/1564740104_5d440a086fcc5.png!small)

2.4.6x命令

.csv：逗号分隔值文件格式。

![](https://image.3001.net/images/20190802/1564740146_5d440a3233d35.png!small)

在main.py的上一级目录下生成.pcap.csv文件：

![](https://image.3001.net/images/20190802/1564740159_5d440a3f72abf.png!small)

2.4.7 F命令

很多主机被列出来，说明请求[www.google.com](http://www.google.com/)的主机非常多。

![29.png](https://image.3001.net/images/20190802/1564740208_5d440a70d0feb.png!small)

找一个特殊的URL，与前面执行d命令中的截图中的数据刚好对应：![30.png](https://image.3001.net/images/20190802/1564740237_5d440a8de3c9f.png!small)

2.4.8 f命令

![](https://image.3001.net/images/20190802/1564740248_5d440a987d82f.png!small)

2.4.9 q命令

![](https://image.3001.net/images/20190802/1564740256_5d440aa0da748.png!small)

## 三、总结

攻防相济，攻击者试图用更与时俱进的技术建立稳健的C&C通信信道，研究学者在检测或防御技术上的重大突破也存在着被攻击者利用的可能性。以基于DNS隐蔽信道的攻击与检测为例，目前基于网络流量的DNS检测技术，尤其是利用Passive
DNS来实现对网络的DNS监控，不需要任何关于僵尸网络协议、通信或签名的先验知识，在当前的DNS检测领域具有一定的先进性和代表性。但基于DNS特征的检测技术也存在一些问题，一些数据特征可能具有时间和空间的特性，所以实验结果很可能具有偏向性，而这些不符合当前时空特性的数据特征就有被攻击者利用的可能性。研究者需要评估自己的结果是否对较好的泛化性能。比如随着时间的推动，技术不断发展，一些用于DNS检测的特征可能已经过时，新的特征也需要我们去挖掘，并防止被利用的可能。

### 参考链接

> [1]<https://github.com/mannirulz/BotDAD>
>
> [2][Singh M, Singh M, Kaur S. Detecting bot-infected machines using DNS
> fingerprinting[J]. Digital Investigation, 2019, 28:
> 14-33.](https://www.sciencedirect.com/science/article/pii/S174228761830272X)

 ***本文作者：BUPT/TTZM，转载请注明来自FreeBuf.COM**

