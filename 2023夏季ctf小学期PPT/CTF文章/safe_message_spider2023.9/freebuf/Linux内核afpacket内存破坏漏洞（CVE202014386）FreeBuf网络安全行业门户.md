2020年9月3日，Palo Auto Networks公司的研究员Or
Cohen发布了一个Linux内核漏洞（CVE-2020-14386），文件af_packet.c存在整数溢出漏洞，可导致越界写入从而造成本地代码执行和权限提升。

##  ** **1**** ** **Linux Kernel**** ** **介绍****

Linux Kernel是由 Linus
Torvalds最初开发的开源的操作系统内核。实现了包括CPU、进程、内存、文件系统等核心模块，被广泛移植到Alpha、arc、arm、ia64、mips、powerpc、sparc、x86-64等许多体系结构上。目前多用于各种服务器和物联网终端等，也可在桌面终端使用Linux。

##  ** **2**** ** **漏洞**** ** **分析****

该漏洞触发时需要本地低权限用户执行其具有执行权限的可执行文件，同时系统启用CAP_NET_RAW功能。CAP_NET_RAW是一种允许使用原始套接字的设置。

漏洞位于net/packet/af_packet.c文件，该文件参与Linux的TCP/IP协议套件实现中的原始数据包套接字。

![](https://image.3001.net/images/20200925/1601025568_5f6db620a8615053a6589.png!small)

unsigned
short类型变量macoff（对应数据链路层的偏移）和netoff（对应网络层的偏移）在收到回环网卡的原始套接字数据包时，按照以上方式赋值。其中类型为数据报套接字（用于UDP）时两者的值都为数据包头部长度+16，否则将netoff赋值为数据包头部长度+16和maclen中较大的一个，在po->has_vnet_hdr存在（即存在虚拟网络，如NAT等）时加上其大小，再将macoff赋值为netoff减去mac头部的值（即减去数据链路层头部）。这里计算netlen时，可能出现传入的长度异常而导致上溢，此后计算macoff时，将会计算出不正常的结果。

![](https://image.3001.net/images/20200925/1601025587_5f6db6336947f92404c91.png!small)

当执行virtio_net_hdr_from_skb函数时，该函数根据参数中的数值申请缓冲区，这里用到了macoff这一数值。从而分配异常长度的缓冲区，可能造成越界写从而出现容器逃逸，权限提升等。

![](https://image.3001.net/images/20200925/1601025607_5f6db6479f41d543b2db3.png!small)

分析补丁可以发现，补丁将netoff变量的类型改为了unsigned
int，并且判断了该值是否大于unsigned_short的最大值，如过大则丢弃内存中的数据包，从而不会导致内存破坏。

##  **3 影响范围**

Linux kernel 4.6-5.9rc4

#  ** **4 解决方案****

###  ** **4.1检测方案****

输入以下命令查看本机的内核版本

cat /proc/version

如显示的Linux version大于4.6且小于5.9，则漏洞可能存在。

 ** **4.2 修复方案****

升级内核版本，安全版本的链接如下：

[
_https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=acf69c946233259ab4d64f8869d4037a198c7f06_](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=acf69c946233259ab4d64f8869d4037a198c7f06)

或使用命令升级：

sudo apt-get install linux-generic-lts-xenial linux-image-generic-lts-xenial
（ubuntu,debian等系统使用）

yum -y update kernel （CentOS,RedHat等系统使用）

 ** **4.3 临时修复方案****

通过禁用CAP_NET_RAW可以临时缓解该漏洞，方法如下：

setcap cap_net_raw-ep /bin/ping

#  **5** ** **时间轴****

2020/9/3 Oh Cohen发布关于该漏洞的说明

2020/9/23 深信服千里目安全实验室发布漏洞分析文章

#  **6** ** **参考链接****

  1. [ _https://github.com/torvalds/linux/commit/8913336a7e8d56e984109a3137d6c0e3362596a4_](https://github.com/torvalds/linux/commit/8913336a7e8d56e984109a3137d6c0e3362596a4)
  2. [ _https://www.openwall.com/lists/oss-security/2020/09/03/3_](https://www.openwall.com/lists/oss-security/2020/09/03/3)
  3. [ _https://seclists.org/oss-sec/2020/q3/att-146/0001-net-packet-fix-overflow-in-tpacket_rcv.patch_](https://seclists.org/oss-sec/2020/q3/att-146/0001-net-packet-fix-overflow-in-tpacket_rcv.patch)

