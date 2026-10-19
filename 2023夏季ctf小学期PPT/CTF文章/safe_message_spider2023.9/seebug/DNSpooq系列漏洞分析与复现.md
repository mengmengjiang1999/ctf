**作者：启明星辰ADLab  
原文链接：<https://mp.weixin.qq.com/s/JtPEWD66yhhRWe_MpnPMaQ>**

## １ 前言

近期，以色列安全咨询企业JSOF在最新报告中披露了七个 DNSmasq 漏洞（统称 DNSpooq），并指出攻击者借此感染了数以百万计的设备。DNSmasq
是一套流行的开源 DNS 转发软件，能够为运行该软件的网络设备添加 DNS 缓存和 DHCP 服务器功能，广泛用于各种小型局域网络。受 DNSpooq
影响的设备不仅可能遭遇 DNS 缓存中毒，还可被用于远程代码执行、拒绝服务（DoS）攻击。目前受影响的厂商包括但不限于 Android /
Google、康卡斯特、思科、红帽、Netgear、高通、Linksys、IBM、D-Link以及 Ubiquiti
。根据shodan显示，有超100万台应用DNSmasq的设备暴露在公网，可能受影响的设备不计其数。

其中， CVE-2020-25684、CVE-2020-25685 和 CVE-2020-25686 这三个漏洞，可能导致 DNS
服务遭遇缓存中毒攻击。另外四个漏洞为 CVE-2020-25687、CVE-2020-25683、CVE-2020-25682 和
CVE-2020-25681 ，均为缓冲区溢出漏洞。黑客或可在配置了 DNSmasq 的网络设备上，利用这些漏洞远程执行任意代码。

## ２ DNS协议简介

DNS的请求和响应的基本单位是DNS报文（Message）。请求和响应的DNS报文结构是完全相同的，每个报文都由以下五段（Section）构成：

![](https://images.seebug.org/content/images/2021/02/2879dc98-f618-4a83-ae5d-5acaab7d6183.png-w331s)

DNS
Header是每个DNS报文都必须拥有的一部分，它的长度固定为12个字节。Question部分存放的是向服务器查询的域名数据，一般情况下它只有一条Entry。每个Entry的格式是相同的，如下所示：

![](https://images.seebug.org/content/images/2021/02/2bbe0fdf-991d-4da3-a89c-192a3c50b6fa.png-w331s)

QNAME：由labels序列构成的域名。QNAME的格式使用DNS标准名称表示法。这个字段是变长的，因此有可能出现奇数个字节，但不进行补齐。DNS使用一种标准格式对域名进行编码。它由一系列的label（和域名中用.分割的label不同）构成。每个label首字节的高两位用于表示label的类型。RFC1035中分配了四个里面的两个，分别是：00表示的普通label，11（0xC0）表示的压缩label。

Answer，Authority和Additional三个段的格式是完全相同的，都是由零至多条Resource
Record（资源记录）构成。这些资源记录因为不同的用途而被分开存放。Answer对应查询请求中的Question，Question中的请求查询结果会在Answer中给出，如果一个响应报文的Answer为空，说明这次查询没有直接获得结果。

RR(Resource Record)资源记录是DNS系统中非常重要的一部分，它拥有一个变长的结构，具体格式如下：

![](https://images.seebug.org/content/images/2021/02/0dcf6a33-cb11-4194-bb3c-cf50f1e6797a.png-w331s)

  * NAME：它指定该条记录对应的是哪个域名，格式使用DNS标准名称表示法。 

  * TYPE：资源记录的类型。 

  * CLASS：对应Question的QCLASS，指定请求的类型，常用值为IN，值为0x001。 

  * TTL(Time To Live)资源的有效期：表示你可以将该条RR缓存TLL秒，TTL为0表示该RR不能被缓存。 TTL是一个4字节有符号数，但是只使用它大于等于0的部分。

  * RDLENGTH：一个两字节非负整数，用于指定RDATA部分的长度（字节数）。 

  * RDATA：表示一个长度和结构都可变的字段，它的具体结构取决于TYPE字段指定的资源类型。 

DNS常见资源记录类型有NS记录、A记录、CNAME记录。

  * NS记录 

NS记录用于指定某个域的权威DNS。比如在com的DNS里，记录着[http://baidu.com](https://link.zhihu.com/?target=http://baidu.com)这个域的DNS，大概如下：

![](https://images.seebug.org/content/images/2021/02/6170d3a9-f9e5-4d78-ad72-005d9801b61d.png-w331s)

这三条记录，就是说[http://ns1.baidu.com](https://link.zhihu.com/?target=http://ns1.baidu.com)、[http://ns2.baidu.com](https://link.zhihu.com/?target=http://ns2.baidu.com)、[http://ns3.baidu.com](https://link.zhihu.com/?target=http://ns3.baidu.com)（以下简称ns1、ns2、ns3）都是[http://baidu.com](https://link.zhihu.com/?target=http://baidu.com)域的权威DNS，询问任意其中一个都可以。

当然，在com的权威DNS里，还会记录ns1~ns3这几个[http://baidu.com](https://link.zhihu.com/?target=http://baidu.com)权威DNS的IP，会一并返回给问询者，以便问询者直接用IP联系ns1~ns3。

  * A记录

A记录就是最经典的域名和IP的对应，在[http://ns1.baidu.com](https://link.zhihu.com/?target=http://ns1.baidu.com)里面，记录着百度公司各产品的域名和IP的对应关系，每一个这样的记录，就是一个A记录，比如下面的3个A记录：

![](https://images.seebug.org/content/images/2021/02/d407103a-74a6-4789-8020-d2a3d9a64743.png-w331s)

如果用户询问[http://ns1.baidu.com](https://link.zhihu.com/?target=http://ns1.baidu.com)：“[http://wenku.baidu.com](https://link.zhihu.com/?target=http://wenku.baidu.com)的IP是多少？”，ns1就会找到对应的A记录或者CNAME记录并返回。

  * CNAME记录

[CNAME](http://en.wikipedia.org/wiki/CNAME_record)记录也称别名记录，允许将多个记录映射到同一台计算机上。比如，在ns1中，并没有[http://www.baidu.com](https://link.zhihu.com/?target=http://www.baidu.com)的A记录，而是一个CNAME记录：

![](https://images.seebug.org/content/images/2021/02/97cdada9-62ac-4245-b333-5df9ca91f4c0.png-w331s)
也就是告诉用户，[http://www.baidu.com](https://link.zhihu.com/?target=http://www.baidu.com)的别名是[http://www.a.shifen.com](https://link.zhihu.com/?target=http://www.a.shifen.com)，可以直接请求解析[http://www.a.shifen.com](https://link.zhihu.com/?target=http://www.a.shifen.com)。

## ３ DNS缓存攻击

当访问[www.baidu.com](http://www.baidu.com)时，域名解析的大致流程如下图所示。

![](https://images.seebug.org/content/images/2021/02/f9f11714-b5fd-4d5a-b335-e7d5efa2522f.png-w331s)

DNS缓存中毒是一种比较经典的攻击方式，如果攻击者可以成功执行，就会在DNS缓存服务器上留下一个有害的条目，使得用户访问正常网站的请求重定向到被攻击者控制的恶意网站。

DNSpooq系列缓存中毒漏洞的简单攻击流程图如下图所示：

![](https://images.seebug.org/content/images/2021/02/02f4f308-ffd9-4ad2-91ee-4ac9777a17e3.png-w331s)

1.用户发送浏览淘宝的请求给DNS转发器，希望得到对应的IP。

2.DNS转发器没有此域名的缓存，所以将请求转发给上游DNS服务器。

3.在得到上游DNS服务器回复前，攻击者发送一个伪造的回复，将淘宝域名与一个恶意IP相对应。

4.DNS转发器接受了这个伪造的回复，并发送给用户，于是用户请求访问的淘宝被重定向到了攻击者操纵的恶意网站。

这个DNS转发器应用场景很广泛，比如个人开的热点，机场、宾馆里的公共网络等，一旦攻击成功，则影响使用这些网络的所有人。

在DNS Header中有一个16-bit的区域叫TXID（transaction
ID），用于将查询包和回复包匹配。在过去，TXID是防御DNS缓存中毒的重要手段。但是在2008年，安全研究员Dan
Kaminsky证明16-bit的TXID是远远不够的，后来又增加了端口随机化，所以这个时候想伪造回复包，不仅需要猜对TXID，还需要猜对端口，一共32位的随机值，此外还需要知道源IP和目的IP。

## 4 安全扩展

到了21世纪，DNS安全扩展正在被慢慢应用。DNS安全扩展是目前为了解决DNS欺骗和缓存污染问题而设计的一种安全机制。DNSSEC依靠数字签名来保证DNS应答报文的真实性和完整性。简单来说，权威服务器使用私钥对资源记录进行签名，递归服务器利用权威服务器的公钥对应答报文进行验证。如果验证失败，则说明这一报文可能是有问题的。

为了实现资源记录的签名和验证，DNSSEC增加了四种类型的资源记录：RRSIG（Resource Record Signature）、DNSKEY（DNS
Public Key）、DS（Delegation Signer）、NSEC（Next Secure）。

例如我们执行命令行：dig @8.8.8.8 paypal.com，得到的DNS查询结果如下所示：

![](https://images.seebug.org/content/images/2021/02/62d3989b-2c4c-4339-ab68-bf8839f712f3.png-w331s)

红框中为应答部分，这是未开启DNSSEC的情况下的。我们执行命令行：dig +dnssec @8.8.8.8
paypal.com，得到的DNS查询结果如下所示：

![](https://images.seebug.org/content/images/2021/02/1558e095-829a-4042-aac7-c4bad9e6ad95.png-w331s)

蓝框中便是RRSIG资源记录存储，该资源记录存储的是对资源记录集合（RRSets）的数字签名。

## 5 Dnsmasq缓存中毒漏洞

以下三个漏洞，组合起来用可以降低伪造回复包的熵值。

### CVE-2020-25684

DNSmasq本身限制了转发给上游服务器查询包的数量，通常最大是150条。用户可以自己设定这个值。转发查询使用的是frec(forward
record)结构。每个frec都和TXID相关联。当回复被接受或经过一定时间，这个frecs就会被删除。

通常情况下，用于转发查询的socket数量被限制在64个。每个用于转发的socket和一个随机的端口绑定。

理论上，查询包中TXID和源端口加起来会有32-bit的熵。但是实际上，这个熵要更少一些。因为dnsmasq在同一个端口会多路复用多个TXID，而没有将每个TXID和每个端口设置为一一对应的关系，如下图所示。结果就是，攻击者只需要猜中64个端口中的一个端口还有正确的TXID就可以了，而不用猜中某个特定的端口和特定的TXID。所以这导致实际上只有26位熵值。

![](https://images.seebug.org/content/images/2021/02/26257268-9f80-4b1e-83c0-d8e8deb42105.png-w331s)

### CVE-2020-25685

如果要对DNS转发器进行投毒，除了需要猜对正确的TXID和源端口，攻击者发送伪造的回复还需要匹配已开放的frecs。如果想让frec匹配，那么TXID和问题区都要匹配，换句话说，回复的内容是之前询问过的。

dnsmasq只存放问题区的哈希值，而不是把整个语句存下来。当整个查询提交的时候，这个哈希值会被保存。

如果dnsmasq没有编译DNSSEC支持，那么他默认使用CRC32作为哈希算法。问题就在于CRC32从密码学角度并不是一个安全的算法。可以很轻松的使用类似SMT
solver等工具进行CRC32碰撞，这里原理不做过多介绍。

所以基于这一特性，攻击者可以生成多个查询，每一个查询的CRC32的值都相同，不过查询的是不同的域名，而这些域名最好是不存在的，即没有被缓存的。然后攻击者可以发送一个具有相同CRC32值的伪造的回复。

如下图所示，攻击者控制一台客户端对多个域名发起问询，每一个CRC32的值都是相同的，然后在递归DNS服务器回复之前，回复一个具有相同CRC32值的域名或IP，攻击即有可能成功。

![](https://images.seebug.org/content/images/2021/02/ae587eb8-d388-4a50-bbd2-54d2d36fe9d1.png-w331s)

### CVE-2020-25686

dnsmasq的另一个问题就是在同一个域名被查询请求时会粗暴的创建多个frecs。随后会转发所有的请求，如果成功的匹配其中的任意一个，就计入缓存。这个问题导致就算dnsmasq使用安全的哈希算法，也可能成功的实施攻击。

通过以上三个漏洞，导致攻击者伪造恶意回复包的成功率大大提高，后面还需要利用dnsmasq没有对回复包做验证的特性进行攻击。

一般情况下，在递归服务器上会对回复包做一些验证机制，例如bailiwicks。但是在配置dnsmasq的设备上并没有做任何验证，所以可以在用户请求的时候，攻击者可以发送如下回复:

![](https://images.seebug.org/content/images/2021/02/eaac2343-bfde-4de1-a30e-3cbadedfad7d.png-w331s)

然后这条记录的缓存就会被插入到dnsmasq的设备中。前文介绍过CNAME，所以当用户想访问的时候，会被重定向到被攻击者控制的IP为6.6.6.6的服务器。而配置了类似bailiwicks的设备，会去找权威服务器询问的IP。

## 6 Dnsmasq缓冲区溢出漏洞

### CVE-2020-25681

以下名称以规范的DNS名称顺序排序。最重要的标签是“example”。在此级别上，“example”将首先排序，然后是以“a.example”结尾的名称，然后是以“z.example”结尾的名称。每个级别中的名称以相同的方式排序。如下图所示。

![](https://images.seebug.org/content/images/2021/02/7d2484d8-4867-4c8e-a544-4830d0271758.png-w331s)

CVE-2020-25681漏洞位于dnssec.c文件的sort_rrset()函数中，该函数负责按照DNSSEC验证过程的要求采用冒泡排序算法将给定的资源记录集合（RRSets）排序为规范顺序。该函数定义如下：

![](https://images.seebug.org/content/images/2021/02/9a0d7d7d-7322-4e42-96c2-75555fcc393a.png-w331s)

它接受了响应数据包（header）以及数据包长度（plen）。rrset是指向资源记录集合中RR数组的指针，而rrsetidx是集合中的RR数，rr_desc是指向与RRset关联的RR类型的描述符的指针。最后，有两个缓冲区buff1和buff2，它们用作排序例程的工作区缓冲区。这两个缓冲区在程序开始时都是相对分配的，它们是daemon>
workspacename和daemon-> keyname。当dnsmasq开启DNSSEC时，将会分配这两个缓冲区。

![](https://images.seebug.org/content/images/2021/02/d31b7d29-71c9-4610-9b51-6c684f48bd2f.png-w331s)

MAXDNAME大小为1025，所以workspacename和keyname的大小2050，也是该漏洞发生溢出的缓冲区。

首先启动dnsmasq，并设置参数为：

-p 53535 --no-daemon --log-queries -S 127.0.0.2 --no-hosts --no-resolv -d -q --dnssec --trust-anchor=.,20326,8,2,E06D44B80B8F1D39A95C0B0D7C65D08458E880409BBC683457104237C7F8EC8D，构造完恶意DNS查询响应包，使用命令行：dig NS +dnssec @localhost -p 53535 .，命中sort_rrset()函数断点后如下图所示：

![](https://images.seebug.org/content/images/2021/02/a11bf030-5144-4717-a7b7-d38d2f39db27.png-w331s)

在构造资源记录集合（RRSets）时，必须保证记录个数大于1，这样才能保证进入排序循环。

这里构造的rrsetidx为0x3。

![](https://images.seebug.org/content/images/2021/02/7505eda7-110e-4110-8fe8-36f7f2693cd1.png-w331s)

正常数据包如下图所示：

![](https://images.seebug.org/content/images/2021/02/c25d3202-502b-4d48-8c51-7c379fe83a1d.png-w331s)

Answers块中，p1指向第一个资源记录，p2指向第二个，然后进行排序。

![](https://images.seebug.org/content/images/2021/02/d80722f8-c3b7-4a60-8b39-e9f9609889c8.png-w331s)

分别跳过Class，Type和TTL，到达RDATA区域。

![](https://images.seebug.org/content/images/2021/02/2554c5e6-7016-44b4-a198-945b3159df99.png-w331s)

Data lengh为20，为Name Server的长度。然后进入排序循环。

![](https://images.seebug.org/content/images/2021/02/d4bc0bec-d56e-40bf-9e54-7bbcb370af43.png-w331s)

行315，首先调用get_rdata()函数解析第一个资源记录p1的RDATA域中的NameServer，看下该函数实现。

![](https://images.seebug.org/content/images/2021/02/12764c66-90d7-4671-9ef2-9336c5f67b07.png-w331s)

判断d是否等于-1，这里不等于，不进入if语句，来到如下代码。

![](https://images.seebug.org/content/images/2021/02/0329f5c4-d956-4326-bcb6-74b4b440d89e.png-w331s)

然后调用extract_name()函数解析，这里需要保证extract_name()函数解析错误返回0，保证进入get_rdata()函数返回为0，通过设置超长NameServer字符串即可。

![](https://images.seebug.org/content/images/2021/02/5e758aaf-46ef-4e08-a548-07fce2eb891d.png-w331s)

进入if语句，行318，计算len1，为end1-p1，即是NameServer的长度。行319，调用memcpy()将p1拷贝到buff1+left1中。

![](https://images.seebug.org/content/images/2021/02/7eed32f4-364d-4242-9ecf-2c324aa57546.png-w331s)

这里len1设置为3550，p1为NameServer，长度RDLENGTH为用户可控。前文已经介绍buff1为daemon>
workspacename，大小为2020，因此发生堆溢出。

![](https://images.seebug.org/content/images/2021/02/4df4fa5a-e793-4bf5-b6aa-a6a25ca00c3a.png-w331s)

## 7 缓解措施

1.升级dnsmasq到最新版本(2.83及以上)，这是目前最有效的方法。

2.如果不必要，配置dnsmasq设备不要在WAN口监听。

3.暂时关闭DNSSEC验证选项。

4.使用为DNS提供传输安全的协议，如DoT或DoH。

## 8 参考链接

[1] <https://www.jsof-tech.com/disclosures/dnspooq/>

[2] <https://www.jsof-tech.com/wp-content/uploads/2021/01/DNSpooq-Technical-WP.pdf>

[3] <https://www.rfc-editor.org/rfc/rfc1664.txt>

[4] <https://security.googleblog.com/2017/10/behind-masq-yet-more-dns-and-dhcp.html>

[5] <https://spoofer.caida.org/summary.php>

[6] <https://www.rfc-editor.org/rfc/rfc7858.txt>

[7] <https://www.rfc-editor.org/rfc/rfc5452.txt>

[8] <http://www.thekelleys.org.uk/dnsmasq/doc.html>

[9] <https://dl.acm.org/doi/10.1145/3372297.3417280>

[10] <https://github.com/Z3Prover/z3>

[11] <https://www.chromium.org/developers/design-documents/dns-prefetching>

[12] <https://www.rfc-editor.org/rfc/rfc4033.txt>

[13] <https://zhuanlan.zhihu.com/p/92899876>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1484/>

