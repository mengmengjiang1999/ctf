# 0x00写在前面

工欲善其事必先利其器！熟悉掌握一种神器对以后的工作必然是有帮助的，下面我将从简单的描述Wireshark的使用和自己思考去写，若有错误或不足还请批评指正。

# 0x01Wireshark介绍

Wireshark（前称Ethereal）是一个网络封包分析软件。网络封包分析软件的功能是撷取网络封包，并尽可能显示出最为详细的网络封包资料。Wireshark使用WinPCAP作为接口，直接与网卡进行数据报文交换。在过去，网络封包分析软件是非常昂贵的，或是专门属于盈利用的软件。Ethereal的出现改变了这一切。在GNUGPL通用许可证的保障范围底下，使用者可以以免费的代价取得软件与其源代码，并拥有针对其源代码修改及客制化的权利。Ethereal是全世界最广泛的网络封包分析软件之一。（百度百科）

官网：https://www.wireshark.org

# 0x02Wireshark使用

首先从官网根据自己的环境下载对应的软件版本，下一步安装即可，建议不要安装在C盘。

接下来打开Wireshark，可以看到设别的网卡信息，选择需要抓包的网卡双击即可。或者按Ctrl+K，勾选需要抓包的网卡，一般情况都会选择WLAN点击Start开始抓包。从流量波形图可以看到弯曲起伏则表示有流量，直线则没有流量。

![1601443959_5f7418770ae510464e50a.png!small](https://image.3001.net/images/20200930/1601443959_5f7418770ae510464e50a.png!small)

# 0x03Wireshark语法

1、过滤MAC地址

eth.addr == 00:71:cc:9a:28:93 //过滤目标或源地址是00:71:cc:9a:28:93的数据包

eth.src == 00:71:cc:9a:28:93 //过滤源地址是00:71:cc:9a:28:93的数据包

eth.dst == 00:71:cc:9a:28:93 //过滤目标地址是00:71:cc:9a:28:93的数据包

2、过滤VLAN

vlan.id == 1024 //过滤VLANID为1024的数据包

vlan.id_name == yunzui //过滤VLAN名为1024的数据包

3、IP过滤

//源IP地址过滤

ip.src == 8.8.8.8

ip.src eq 8.8.8.8

//目标IP地址过滤

ip.dst == 8.8.8.8

ip.dst eq 8.8.8.8

//ip地址过滤。不论源还是目标

ip.addr == 8.8.8.8

ip.addr eq 8.8.8.8

4、端口过滤

tcp.port == 8888

udp.port eq 8888

tcp.dstport == 8888 // 只显tcp协议的目标端口8888

tcp.srcport == 8888 // 只显tcp协议的来源端口8888

//过滤端口范围

tcp.port >= 1 and tcp.port <= 8888

5、常用协议过滤

tcp //只显示TCP协议的数据流

udp //只显示UDP协议的数据流

arp //只显示ARP协议的数据流

icmp //只显示ICMP协议的数据流

http //只显示HTTP协议的数据流

smtp //只显示SMTP协议的数据流

ftp //只显示FTP协议的数据流

dns //只显示DNS协议的数据流

……

排除HTTP包，如!http 或 not http

 **6、http** **模式过滤**

http.request.method == “GET”

http.request.method == “POST”

http.request.uri == “/img/logo-edu.gif”

http contains “GET”

http contains “HTTP/1.”

// GET数据包

http.request.method == “GET” && http contains “Host: ”

http.request.method == “GET” && http contains “User-Agent: ”

// POST数据包

http.request.method == “POST” && http contains “Host: ”

http.request.method == “POST” && http contains “User-Agent: ”

// HTTP请求数据包

http.request.method == "POST" && http contains "Java/1.8.0_121"

// HTTP响应数据包

http contains “HTTP/1.1 200 OK” && http contains “Content-Type: ”

7、运算符

less than：lt

less and equal： le

equal：eq

great then：gt

great and equal：ge

not equal：ne

8、连接符

and，or

如tcp.port == 8888 and ip.addr = 88.88.88.88

# 0x04 Wireshark功能

1、Wireshark数据包的结构

第1行：数据包整体概述，内容比较多

第2行：数据链路层详细信息，主要为mac地址

第3行：网络层详细信息，主要的是双方的IP地址

第4行：传输层的详细信息，主要的是双方的端口号

第5行：TCP或UDP是传输的DATA，DNS这是域名的相关信息

![1601444010_5f7418aa446cf6f7a487a.png!small](https://image.3001.net/images/20200930/1601444010_5f7418aa446cf6f7a487a.png!small)

2、wireshark着色规则

在菜单栏中点开视图中的着色规则就可以看到

![1601444040_5f7418c80230ad9f2a00c.png!small](https://image.3001.net/images/20200930/1601444040_5f7418c80230ad9f2a00c.png!small)

3、数据包的统计分析

协议分级统计功能可以查看所选包协议的分布情况，可以分析者帮助识别可疑协议，和不正常的网络应用程序，提高分析效率。

在菜单栏中点开统计中的协议分级（P）就可以看到

![1601444061_5f7418dd1aa1a2ac7a4ff.png!small](https://image.3001.net/images/20200930/1601444061_5f7418dd1aa1a2ac7a4ff.png!small)

在Endpoints窗口中，可以通过排序Bytes和Tx Bytes来判断占用带宽最大的主机

在菜单栏中点开统计中的Endpoints就可以看到

![1601444073_5f7418e9c1e33c6fadb02.png!small](https://image.3001.net/images/20200930/1601444073_5f7418e9c1e33c6fadb02.png!small)

Conversions窗口可以看到两个主机之间发送/接收数据包的数量、字节大小以及数据的流向情况，也可以通过排序来判断占用最大带宽的主机。

在菜单栏中点开统计中的Conversions就可以看到

![1601444088_5f7418f866bbe36918755.png!small](https://image.3001.net/images/20200930/1601444088_5f7418f866bbe36918755.png!small)

4、追踪数据流

当分析到某条数据包对于的数据流查看。可以选中数据，右键选择追踪流。里面就会有tcp流、udp流、ssl流、http流。数据包属于哪种流就选择对应的流。

![1601444098_5f7419021088dc81bcd95.png!small](https://image.3001.net/images/20200930/1601444098_5f7419021088dc81bcd95.png!small)

# 0x05实战分析

攻防世界中级数据分析题

题目：黑客通过wireshark抓到管理员登陆网站的一段流量包（管理员的密码即是答案)。 flag提交形式为flag{XXXX}

![1601444112_5f741910e16bd8ea25eca.png!small](https://image.3001.net/images/20200930/1601444112_5f741910e16bd8ea25eca.png!small)

下载题目数据包，根据题目要求对数据包进行分析

提取题目keyword ：网站（HTTP） 登陆（POST）

打开数据包过滤对应数据流

http.request.method == "POST"

![1601444122_5f74191aa2414238570f7.png!small](https://image.3001.net/images/20200930/1601444122_5f74191aa2414238570f7.png!small)

追踪HTTP数据流，获取管理员密码

ffb7567a1d4f4abdffdb54e022f8facd

![1601444136_5f74192898e1322e63ece.png!small](https://image.3001.net/images/20200930/1601444136_5f74192898e1322e63ece.png!small)

# 0x06总结思考

伴随着网络安全攻防对抗愈演愈烈，全流量分析显得尤为重要，在海量的大数据中提取关键信息，不仅是攻击者的思路更是分析人员的必修课。

雁过留痕！Wireshark从TCP/IP协议全过程捕获数据流，是一款非常不错的分析工具，这里只介绍了很少的功能，有兴趣的朋友可以继续深究！

# 0x07参考链接

> https://www.jianshu.com/p/63f6f7d5deed
>
> https://mp.weixin.qq.com/s/tKsOm-xxe7ZBqgkKccjjZg
>
> https://adworld.xctf.org.cn/

