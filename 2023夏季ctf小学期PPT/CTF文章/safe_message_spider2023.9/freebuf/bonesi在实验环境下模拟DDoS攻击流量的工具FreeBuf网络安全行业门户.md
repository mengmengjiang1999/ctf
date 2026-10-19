**BoNeSi，DDoS僵尸网络模拟器是一种测试平台环境中模拟僵尸网络流量的工具。它旨在研究DDoS攻击的影响。**

 **![ddos-protection-from-your-host-2.png](https://image.3001.net/images/20190219/15505686725942.png!small)**

### 可以生成什么流量？

**BoNeSi** 从定义的僵尸网络大小（不同的IP地址）生成ICMP，UDP和TCP（HTTP）泛洪攻击。 **BoNeSi**
具有高度可配置性，可以配置速率，数据量，源IP地址，URL和其他参数。

###  是什么让它与其他工具不同？

还有很多其他工具可以使用UDP和ICMP来欺骗IP地址，但是对于TCP欺骗，没有解决方案。 **BoNeSi** 是第一个模拟来自大型僵尸网络的HTTP-GET洪水的工具。 **BoNeSi** 还试图避免生成具有易于识别的模式的数据包（可以轻松过滤掉）。

###  我在哪里可以运行BoNeSi？

我们强烈建议在封闭的测试平台环境中运行 **BoNeSi**
。但是，UDP和ICMP攻击也可以在互联网上运行，但你应该小心。无法在Internet上模拟HTTP-Flooding攻击，因为来自Web服务器的答案必须路由回运行 **BoNeSi** 的主机。

###  TCP Spoofing如何工作？

**BoNeSi嗅探** 网络接口上的TCP数据包，并响应所有数据包以建立TCP连接。对于此功能，必须将来自目标Web服务器的所有流量路由回运行
**BoNeSi** 的主机

###  **BoNeSi** 的性能有多好？

我们非常关注性能以模拟大型僵尸网络。在具有2Ghz的AMD Opteron上，我们每秒能够生成多达150,000个数据包。在最近的具有3.3Ghz的AMD
Phenom II X6 1100T上，您可以生成300,000 pps（在2个内核上运行）。

###  BoNeSi **攻击是否成功？**

**是的，他们非常成功。UDP / ICMP攻击可以轻松填补带宽，HTTP-Flooding攻击可以快速淘汰网络服务器。我们还针对最先进的商业DDoS缓解系统测试了** BoNeSi**，并且能够使其崩溃或隐藏攻击。

可在[此处](http://madm.dfki.de/projects/netcentricsecurity)找到BoNeSi的演示视频。

##  详细资料

BoNeSi是用于不同协议类型的网络流量生成器。创建的数据包和连接的属性可以通过几个参数来控制，例如发送速率或payload大小，或者它们是偶然确定的。即使在生成tcp流量时，它也会欺骗源IP地址。因此，它包含一个简单的tcp-stack来处理混杂模式下的tcp连接。为了正确工作，必须确保响应数据包被路由到运行BoNeSi的主机。因此BoNeSi不能用于任意网络基础设施。可生成的最高级流量是http请求。
**TCP / HTTP** 为了使http请求更加真实，有几件事情是偶然决定的：

> 源端口
>
> ttl：3..255
>
> tcp选项：具有不同长度和概率的七种不同的现实生活选项
>
> http头的用户代理：在给定列表的文件中（包含示例文件，见下文）Copyright 2006-2007 Deutsches
> Forschungszentrum fuer Kuenstliche
> Intelligenz这是免费软件。根据Apache许可证2.0版获得许可。在法律允许的范围内，不提供任何担保。

##  安装

    
    
    :~$ ./configure
    :~$ make
    :~$ make install

##  用法

    
    
    :~$ bonesi [OPTION...] <dst_ip:port>
     Options:
      -i, --ips=FILENAME               filename with ip list
      -p, --protocol=PROTO             udp (default), icmp or tcp
      -r, --send_rate=NUM              packets per second, 0 = infinite (default)
      -s, --payload_size=SIZE          size of the paylod, (default: 32)
      -o, --stats_file=FILENAME        filename for the statistics, (default: 'stats')
      -c, --max_packets=NUM            maximum number of packets (requests at tcp/http), 0 = infinite (default)
          --integer                    IPs are integers in host byte order instead of in dotted notation
      -t, --max_bots=NUM               determine max_bots in the 24bit prefix randomly (1-256)
      -u, --url=URL                    the url (default: '/') (only for tcp/http)
      -l, --url_list=FILENAME          filename with url list (only for tcp/http)
      -b, --useragent_list=FILENAME    filename with useragent list (only for tcp/http)
      -d, --device=DEVICE              network listening device (only for tcp/http, e.g. eth1)
      -m, --mtu=NUM                    set MTU, (default 1500). Currently only when using TCP.
      -f, --frag=NUM                   set fragmentation mode (0=IP, 1=TCP, default: 0). Currently only when using TCP.
      -v, --verbose                    print additional debug messages
      -h, --help                       print help message and exit

##  另外包含的示例文件

 **50K-机器人**

随机生成50,000个ip地址以与--ips选项一起使用

 **browserlist.txt**

几个浏览器标识与--useragentlist选项一起使用

 **urllist.txt**

几个网址与--urllist选项一起使用

 ***参考来源：[github](https://github.com/Markus-Go/bonesi)，由周大涛编译，转载请注明来自FreeBuf.COM**

