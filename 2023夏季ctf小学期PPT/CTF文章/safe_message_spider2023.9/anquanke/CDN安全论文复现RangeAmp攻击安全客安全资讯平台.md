# CDN安全-论文复现-RangeAmp攻击

阅读量 **409190**

|评论 **8**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-03-26 15:30:00

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

论文名称：《CDN Backfired: Amplification Attacks Based on HTTP Range Requests》

论文链接：<https://netsec.ccert.edu.cn/files/papers/cdn-backfire-dsn2020.pdf>

论文简介：2020年清华大学巨佬发布在IEEE/IFIP International Conference on Dependable Systems
and Networks (DSN)上，同时被获得2020年DSN最佳论文。本文主要介绍了基于HTTP Range
Request机制下的HTTP放大攻击，同时本文的实验结果表明，能将原始流量放大至数万倍。可以利用此种方式发送高效率的DDos攻击。

文章简介：本文主要对论文内容进行阐述，最后我对作者所提及的漏洞进行了复现，并详细的撰写复现过程。

## 0x01:摘要

首先简单介绍CDN的当前在网络中的现状，其次介绍HTTP-RANG的由来，并且着重介绍：在RFC文件中建议CDN厂商都支持，当前CDN厂商确实都支持，但是在部署上存在严重的问题。接着引出他们发现的攻击类型（OBR）(SBR)，介绍他们提出的攻击在实验中的结果。最后他们提出简单的防护措施，并将漏洞和防御方法都发给供应商和用户。最后总结介绍论文的三个贡献：

> 1.作者发现了两种基于RangeAmp的两种攻击方式。  
>  2.作者测试了13个CDN厂商并且确定了攻击的可行性。  
>  3.作者提出了短时间的解决方案。

## 0x02:背景

###  0x01:CDN的背景

CDN(内容分发网络)：是指一种透过[互联网](https://zh.wikipedia.org/wiki/%E4%BA%92%E8%81%AF%E7%B6%B2)互相连接的电脑网络系统，利用最靠近每位用户的服务器，更快、更可靠地将音乐、图片、视频、应用程序及其他文件发送给用户，来提供高性能、可扩展性及低成本的网络内容传递给用户（维基百科）。简单的来说，假如你有一台服务器在北京，而你本人在广东，你访问服务器时，你的请求需要从广东发送到北京，这之间经过多个网络设备以及长距离的传输，存在较高的网络延迟。如果你使用CDN，CDN将会为你在全国各地区分配多台服务器，每台服务器上缓存你服务器上的资源。此时你从广东访问你的服务器，如果请求的目标资源被缓存至CDN节点，那就可以直接访问广东的CDN节点的缓存，来获得响应，降低了网络延迟。

作者拿一次客户端请求服务端的完整过程做了详细的介绍。其请求过程如下：用户对服务器请求目标资源。DNS解析将最终跳转到CDN服务商。CDN服务商根据IP的地址为其分配最近的CDN节点。CDN检查目标资源是否被缓存，如果被缓存，直接返回缓存信息。如果目标资源没有被缓存，则将去请求源服务器，同时缓存目标资源。

![](https://p4.ssl.qhimg.com/t01d1845b44cf47912a.png)

同时作者指出下图中的CDN，可能不止是一个CDN厂商，可能是多个CDN厂商相互套用加速。如果多个厂商相互套用的情景下，图中的Ingress
Node称之为FCDN，Egress Node称为BCDN。在本章节的最后，作者提出在请求CDN资源末尾加上随机的get参数，能够绕过CND的缓存。例如
1M.zip?adasda=1，能够使CDN去请求源站资源。

###  0x02：HTTP Range Requset机制

由于请求被取消或者TCP连接丢失，HTTP在传输过程中往往发生中断，HTTP协议却又是无状态的应用程序。而HTTP Range
Request就是为了解决这一问题，它能够快速恢复，重新传输丢失的部分。HTTP Range
Requset机制，允许用户请求目标资源的部分内容。只要在请求中加入`Range:`请求头。作者介绍了两种Rang请求的用法：

    
    
    请求一个文件的部分通常在HTTP请求头中加上Range: bytes=[first_byte-last_byte]或者Range: bytes=[-suffix_length]。
    多段式Range请求，在Range中分多段请求部分数据，在第一部分的基础之上加上逗号进行分割。
    

![](https://p1.ssl.qhimg.com/t019dc3628e0411b539.png)

图中a请求对应着图c响应，同样的b对应d。在图a中`Range:bytes=0-0`为请求目标资源中第一个字节数据。在图C中服务端响应客户端请求，返回206状态码，以及目标资源一个字节的数据。图b中`Range:bytes
=
1-1,-2`请求目标资源第二个字节,和文件的最后两个字节。图d服务端对图b做出了响应，返回206状态码，和两段资源，其中可以发现每段响应都带着`Content-Range`和`Content-Type`这个请求头，`Content-Range`包含目标文件的大小，`Content-Type`包含目标文件的格式。作者提出可以通过发送一个`Range:
bytes=0-0`来判断是否支持Range请求，如果支持则response中状态码为216，如果不支持则返回200。

## 0x03:CDN中的 HTTP -Range-Request

在作者测试的13个CDN中发现目前存在的CDN中对HTTP Range请求存在三种响应方式。

    
    
    Laziness:对于用户发来的Range请求，直接转发给源主机。
    Deletion：直接将请求头的Range删除，然后请求整个资源。
    Expansion：将Range的范围扩大至一定的范围。
    

经过试验作者发现大部分的CDN都是采取删除方案或者扩大方案，因为CDN厂商坚信既然请求部分数据，那必定会请求其他数据，所以不如直接把用户请求的资源完整的缓存在CDN服务器上。本章节的最后作者介绍了下Range请求在RFC文档中定义的变化：在RFC2616中并没有对Range请求做限制，但是由于攻击者发现CVE-2011-3192漏洞：“Apache
Killer”，攻击者发现通过创建大量的多范围的Range请求的线程，可以消耗尽Apache服务器上的内存。因此在RFC7233中对Range请求做了一些限制：”对于大量小范围的Range请求，以及两个以上请求范围有重复的Range请求，服务器应该忽略、合并或者拒绝”。但是显然作者测试的13个CDN并没有这样做。

## 0x04：攻击模型介绍

这一部分作者主要详细介绍了两种攻击模型。一种是SBR攻击，另一种是OBR攻击。首先简单的阐述了两种攻击的攻击方式以及目标。

![](https://p2.ssl.qhimg.com/t010035b9c783bc7d75.png)

    
    
    SBR攻击：图中的a线路，用户利用攻击者构造Range请求发送给CDN，CDN请求源主机完整的资源。用户只发送了很少的请求，而CDN却向服务器请求完整的资源。攻击对象为用户源主机，主要消耗源主机和CDN之间的带宽。
    OBR攻击：图中的b线路，应用场景是一个网站被多个CDN嵌套加速(这里的FCDN，BCDN为CDN服务器)。用户发送攻击者构造的Range请求，服务器收到的是很小的流量，但是CDN直接传输却有着很大的流量。攻击对象为CDN主机，主要消耗BCDN或FCNB的带宽
    

###  0x01: SBR攻击

如果主机CDN利用Dletetion策略和Expansion策略去处理Range请求，那么他就可能遭受SBR攻击。在SBR攻击中源主机收到的流量将远远大于用户的Range请求。由于以上两种处理Range请求的策略，用户请求部分目标资源，而CDN去请求服务器完整资源，导致攻击者构造的Range请求被CDN放大，攻击者能够通过请求CDN主机而对源主机发动Dos攻击。具体参考作者的图解。

![](https://p2.ssl.qhimg.com/t015171e5b69231bcd3.png)

从图中看，攻击者在请求头中加入`Range:
bytes=0-0`(表示请求目标资源第一个字节的数据)，CDN假如采取Deletetion策略或Expansion策略，CDN将会向源主机请求完整的目标资源。源主机返回完整目标资源给CDN，CDN对资源进行缓存，同时CDN返回状态码为206的部分主机资源。可以看到如果目标资源越大，则源主机消耗的流量越多。如果利用前面提到的绕过CDN的缓存，多线程的RANGE请求，理论上可以占满服务器的带宽。

###  0x02:OBR攻击

如果在多CDN加速场景下，如果FCDN采用Laziness策略同时BCDN在处理多段范围重叠Range请求时，没有对范围重叠字段进行检查，同时会对多段范围重叠Range请求，做出相应。那么该场景下CDN将会被OBR攻击方式攻击。具体的攻击方式如下。

![](https://p2.ssl.qhimg.com/t01cd57ff7a17e58c42.png)

在我们假设的两种策略都被实现下，攻击者发送多段范围重叠Range请求，例如`Range:
bytes=0-,0-,0-...`(0-的含义是N)。FCND由于是Laziness策略直接将源请求转发给BCDN。BCDN对目标资源进行完整的请求。源服务器将完整的目标资源发送给BCDN，同时BCDN将响应FCDN的多段范围重叠请求，会返回n段完整的数据资源。那么在BCDN和FCDN之间将会有大量的流量产生。而且多段范围重叠Range请求，能够一次返回多个资源，能够更快的占满带宽。

## 0x04：现实世界的CDN安全测试

###  0x01:第一次试验

作者在13个CDN厂商的CDN进行实验，分别为Alibaba Cloud、Tencent Cloud、Huawei
Cloud、Cloudflare、CDN77、Flastly、Azure、CDNsum、G-Core
Labs、CloudFront、Akamai、StackPath。作者首先测试各个厂商应对Range响应的策略。根据两种攻击类型来分别测试对Range请求的响应策略，分别为单一CDN应用场景下的Range请求测试，和多CDN应用场景下多段范围重叠Range请求测试。作者通过对比本地测试构造的Range请求，和源服务器接收到的请求，来判断CDN厂商对于Range请求的应对策略。

####  0x01：单一CDN应用场景下的测试（SBR）

作者通过构造两种Range请求来测试CDN的响应策略，一种是请求前几字节数据，另一种是请求末尾几字节请求数据。作者通过分析源服务器接受到的请求，来确定CDN的响应策略。最终得到的实验结果如下。

![](https://p1.ssl.qhimg.com/t01340aacbf1227b266.png)

从表中可以看到Akamai, Alibaba Cloud, CDN77, CDNsun, Cloudflare, Fastly, G-Core Labs,
Huawei Cloud, and TencentCloud
都采取了删除策略。国内的三家厂商分别提供了是否开启Range请求的按钮，但是开启之后都容易被SBR攻击。其中微软的Azure当Range请求的范围低于8M时采用Deletetion策略。但是当目标资源高于8M，Azure将会采用Expansion策略，将Range头替换为`Range:
bytes=8388608-16777215`.KeyCDN和StackPath都采用Laziness策略，但是对于第一次Range请求，CDN不缓存目标资源。当再一次接受到目标资源时，CDN才会缓存。作者测试出以上13个CDN均能满足SBR攻击的条件。

####  0x02：多CDN应用场景下的多段范围重叠Range请求测试（OBR）

作者也对多CDN应用场景下可能存的多段范围重叠Range请求对各CDN进行测试，此次测试实际上是在测试满足OBR攻击两个条件的FCND和BCDN。作者得到的测试结果如表二、表三。

![](https://p5.ssl.qhimg.com/t01b197317b7f378015.png)

表格二中显示，CDN77、CDNsum、Cloudflare、StackPath等CDN对于多端范围重叠Range请求，没有任何改变直接转发，采用Laziness策略。满足发动OBR攻击FCND的Liness策略，如果这四个CDN厂商的CDN，在多CDN应用场景中被用作FCND那么就有可能遭受OBR攻击。

![](https://p5.ssl.qhimg.com/t01f28da86c34eeb707.png)

表格三中显示，Akamai、Azure、StackPath三个厂商，在处理多段范围重叠Range请求时，没有对范围重叠字段进行检查，同时会对多段范围范围重叠Range请求，做出相应。也就是说当用户构造的请求为`Range:
bytes=-n,-n,-n,-n,-n,....`,m次`-n`请求，那么在FCND和BCND服务器之间传输的数据将是m*目标资源大小的流量。

###  0x02：第二次试验

第二次试验中作者测试SBR攻击可以将流量放大的系数。作者对以上提及的13个CDN进行SBR攻击测试，测试SBR攻击能够将原始攻击流量放大的系数。实验的方法为：作者分别在源服务器上放上1MB、10MB、25MB的资源。通过抓取作者发送的攻击流量包和捕获源服务器向CDN发送的数据包，计算出两个数据包之间流量数据相差倍数，即为放大的系数。作者得到的结果如下所示。

![](https://p5.ssl.qhimg.com/t01f4cd1cbf534d21ee.png)

从图中我们可以看流量被放大的倍数还是非常可观的，1MB最小被放大的系数为724，25MB时被放大的系数最大为43330。从流量中可以发现其实返回的目标资源是一样大的，不同的是不同的CDN在对目标资源的请求时，会加上不同的请求头所以导致请求放大的系数有所差异。根据上表，作者绘制了放大系数与文件大小之间的图。

![](https://p3.ssl.qhimg.com/t011e2ad026b9357e33.png)

作者发现当使用Azure的CDN是当文件大小超过16MB时，随着目标资源的增大，放大系数达到稳定。同样的情况发生在CloudFront上，当文件大小超过10M时，放大系数不增大反而降低。同时作者通过绘制用户接受到的CDN返回的流量和文件大小的关系的图例。

![](https://p0.ssl.qhimg.com/t0170421eab6f2ffa67.png)

发现KeyCDN返回用户的资源信息离谱的大，原因是因为KeyCDN每次需要至少发送两次Range请求，因此KeyCDN发给用户的响应数据比较大。

###  0x03:第三次实验

第三次实验作者主要是对OBR攻击进行了测试。进行OBR攻击首先需要FCND和BCDN满足条件，FCND需要满足的条件为：采用Lainess策略。在上文中的表二，作者测试出满足条件的四个CDN为：CDN77、CDNsum、Cloudflare、StackPath。BCDN需要满足的条件为：会对多段重叠的Range请求做出响应，通过不会检查Range请求范围是否重叠。在上文中的表三，作者测试出满足条件的三个CDN为：Akamai、Azure、StackPath。接着作者对这12中组合进行实验。作者通过将FCDN将源主机代理到一台服务器中，同时这台服务器将代理的请求转发至BCDN。抓取这台代理服务器的流量，最终获取到FCND和BCDN之间传输的流量数据。同时根据OBR攻击的理论指导。CDN之间传输的流量为分段Range传输中n的个数*目标资源的文件大小。但是CDN对于HTTP请求头大小存在限制：Akamai最大请求头为32KB、StackPath最大请求头为81KB、CDN77
和 CDNsun
请求头为16KB、Cloudflare限制请求头大小为：31KB（其中包含Host请求头），只有Azure限制Range请求头为64。作者为了不影响CDN厂商的工作，只在服务器上存放1KB的目标资源。而是将请求头能利用的空间沾满。从而获得最大的放大系数。作者得到的实验结果如下：

![](https://p2.ssl.qhimg.com/t0126d97ead63df1c8e.png)

可以看到在BCDN和FCDN之间传输的流量非常的大。而原服务器和客户端接收到的流量却非常小。

###  0x04：第四次实验

第四次实验作者利用SBR攻击来实际测试下能够占用多少带宽。作者在服务器上放置10MB大小的目标资源文件，同时控制每秒发送的range请求的数量，得到用户带宽占用如下图所示。

![](https://p2.ssl.qhimg.com/t015e025539e291a78a.png)

此图的x轴为时间，Y轴为用户收到的响应数据所占用的带宽。不同颜色的折线表示每秒发送的rang请求的数量。可以看到无论每秒发送多少Range请求，用户的带宽都不会超过500Kb/s。作者接近着又对服务器端的出站流量进行分析。通过绘图结果如下所示。

![](https://p3.ssl.qhimg.com/t012d435455f226e34e.png)

作者服务器的带宽是1000MB，但是通过SBR攻击，在攻击客户端最高带宽不到500KB/S，能让服务器的1000Mb的带宽全部占满。

###  0x05:原因分析

同时作者发现HTTP2.0中依然是继承了，HTTP1.0中的Range请求策略。作者认为根本的原因在于RFC文档中定义不明确和服务商的安全疏忽造成了这个漏洞的产生。

## 0x05：漏洞复现

作者最后将漏洞提交给各大厂商，收到了各大厂商的好评，论文上说各大厂商修补了这个漏洞。就在看完实验部分想立马动身开始搞一下的时候，作者给我泼了一把冷水，最后我全当测试着玩，发现了小惊喜。华XX，并没有完全修补这个漏洞。在服务器上放10M的文件，burp35线程发包。100Mb的带宽一分钟之内打满。效果如下。

![](https://p4.ssl.qhimg.com/t01e7ed366fbfcf40e3.png)

复现过程如下，只要把自己的域名在华某云上加速，然后dig查询下自己的域名是否被加速。

![](https://p0.ssl.qhimg.com/t016b3dafb8fa976427.png)

只要出现.cdnhwc2.com结尾的CNAME就证明加速成功。接着在后台开启Range回源选项。

![](https://p3.ssl.qhimg.com/t01a127c1556824862a.png)

接下来放在服务器上一个资源，这里我放的是1M.zip。利用HTTP range request 请求CDN。具体请求如下：

    
    
    GET /1M.zip?9989z=z HTTP/1.1
    Host: www.xxx.xxx
    Range: bytes=0-0
    Content-Length: 4
    Connection: close
    

其中文件后面的参数是来绕过CDN的缓存的。请求过程中抓取源服务器的数据包得到如下结果。

![](https://p4.ssl.qhimg.com/t01e4ccb5050e4ed904.png)

`0-524287`是0.5M的资源。他的响应策略就是每次缓存0.5Mb的资源缓存到服务器上。但是对于`Range:
bytes=9999-`,或者是重叠的Range请求，依然采取的是缓存整个目标资源。而且是每次请求0.5M的资源。10M的资源他需要去发送20个Range请求。可以构造请求如下。

    
    
    GET /10M.zip?9989z=z HTTP/1.1
    Host: www.xxx.xxx
    Range: bytes=0-1,1-1
    Content-Length: 4
    Connection: close
    

源服务器接收到的请求流量数据为下图所示。

![](https://p1.ssl.qhimg.com/t01f9ed618215332f4c.png)

请求了多次，每次请求0.5MB的资源。

![](https://p1.ssl.qhimg.com/t01946c20ab334414fd.png)

![](https://p4.ssl.qhimg.com/t0191eb0aa08bc4df3b.png)

最后burp一把梭，线程开高点，一会就会把源服务器打躺下。

![](https://p4.ssl.qhimg.com/t012d8ecccff5cd0f7c.png)

最后想测试一把OBR攻击，作者测试的那个存在OBR攻击的CDN厂商，有几个需要信用卡来注册。比较麻烦，时间又不怎么够就没有测试。

## 0x06：总结

仔细读了这篇文章，复现加上写笔记补知识花了一个星期整吧，也是满满的收获。其实仔细一想作者的攻击手段并不复杂，但是其创新的思路和攻击方法是很难想到的。作者能够发现这样的漏洞一定是有很深厚的基础知识，看了很多类似的论文。从这篇文章我学到一点去翻看官方的RFC文档真的很重要，很具有权威性。最后本菜鸡第一次发文，大佬轻喷。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Zer0r3** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/235832](/post/id/235832)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CDN](/tag/CDN)
  * [Range请求](/tag/Range请求)

 **+1** __18赞

 __收藏

![](https://p2.ssl.qhimg.com/t01dfaea2bce8fc9d3b.png) Zer0r3

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

