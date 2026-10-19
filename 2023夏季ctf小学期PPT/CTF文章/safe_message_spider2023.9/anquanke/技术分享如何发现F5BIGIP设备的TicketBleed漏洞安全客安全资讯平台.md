# 【技术分享】如何发现F5 BIG-IP设备的TicketBleed漏洞

阅读量 **155618**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2017-02-10 13:53:47

 **x**

##### 译文声明

本文是翻译文章，文章来源：blog.filippo.io

原文地址：<https://blog.filippo.io/finding-ticketbleed/ >

译文仅供参考，具体内容表达以及含义原文为准。

翻译：[胖胖秦](http://bobao.360.cn/member/contribute?uid=353915284)

预估稿费：200RMB

投稿方式：发送邮件至[linwei#360.cn](mailto:linwei@360.cn)，或登陆[网页版](http://bobao.360.cn/contribute/index)在线投稿

**前言**

Ticketbleed（CVE-2016-9244）是存在F5产品的TLS堆栈中的软件漏洞，它允许远程攻击者一次性提取多达31个字节的未初始化内存数据，像Heartbleed一样,它可以包含任意的敏感信息。

如果您不确定是否会受到此漏洞的影响，您可以在[ticketbleed.com](https://ticketbleed.com/)（包含在线测试）或[F5
K05121675文章](https://support.f5.com/csp/article/K05121675)中找到详细信息和缓解说明。

在这篇文章中，我们将讨论如何找到，验证和披露Ticketbleed。

**  
**

**JIRA RG-XXX**

这要从CloudFlare [Railgun](https://www.cloudflare.com/website-optimization/railgun/)产生的一个错误报告说起。

rg-listener <> 原始请求失败,错误命令是"local error: unexpected message"

rg-listener <> 原始流量包被记录并显示在握手之间触发了一个TLS警告.

值得注意的是客户在Railgun 和原始服务器之前使用了一个F5的负载均横: visitor > edge > cache > rg-sender > F5
> rg-listener > F5 > origin web server

Matthew不可能在Go中使用一个基本的TLS.Dial 来复现它，所以问题似乎很棘手

Railgun的位置：Railgun通过建立永久优化的连接并对HTTP响应执行增量压缩来加速Cloudflare edge和原始网站之间的请求。

Railgun连接使用基于TLS的自定义二进制协议，两个终端都是Go程序：一个终端位于Cloudflare
edge，另一个安装在客户服务器上。这意味着整个连接都要通过Go TLS栈,crypto/tls。  

连接失败的错误代码是:local error: unexpected message,这意味着客户端发送了一些Railgun的Go
TLS堆栈无法处理的数据。由于客户端在Railgun和我们之间运行着F5负载均衡，这也表明Go TLS栈和F5之间存在不兼容性。

但是，当我的同事Matthew试图使用crypto/tls.Dial连接到负载均衡上来重现错误时，它成功了。

深入分析PCAP

由于Matthew正坐在我对面，他知道我一直在使用Go TLS协议来实现TLS 1.3。于是我们很快完成了联合调试。

下面是我们分析的PCAP。

上图中有ClientHello和ServerHello数据包,然后马上发送ChangeCipherSpec消息。在TLS
1.2中,ChangeCipherSpec代表的意思就是”让我们开始加密吧”。只有一种情况,ChangeCipherSpec会在握手之前先发送,那就是会话复用。

事实上，通过观察ClientHello，我们可以发现Railgun客户端发送了一个Session Ticket。

Session Ticket携带着先前会话的一些加密密钥信息,来告诉服务器复用先前会话，而不是协商新的会话。

要了解有关TLS 1.2会话复用的更多信息，请阅读[Cloudflare Crypto Team TLS
1.3Take](https://blog.cloudflare.com/tls-1-3-explained-by-the-cloudflare-crypto-team-at-33c3/)的第一部分,阅读副本或Cloudflare博客上的[“TLS会话复用”的帖子](https://blog.cloudflare.com/tls-session-resumption-full-speed-and-secure/)。

在发送ChangeCipherSpec消息之后，Railgun和Wireshark变的不知所错（HelloVerifyRequest？Umh？）。所以我们有理由确定这个问题与Session
Ticket有关。

在Go中，您需要在客户端上设置ClientSessionCache来显式开启Session
Ticket。我们验证Railgun开启了这个功能，并写了这个小测试：

    
    
    package main
     
    import (  
        "crypto/tls"
    )
     
    func main() {  
        conf := &tls.Config{
            InsecureSkipVerify: true,
            ClientSessionCache: tls.NewLRUClientSessionCache(32),
        }
     
        conn, err := tls.Dial("tcp", "redacted:443", conf)
        if err != nil {
            panic("failed to connect: " + err.Error())
        }
        conn.Close()
     
        conn, err = tls.Dial("tcp", "redacted:443", conf)
        if err != nil {
            panic("failed to resume: " + err.Error())
        }
        conn.Close()
    }

这足以证明错误的发生(local error: unexpected message)与Session Ticket有关。

**  
**

**深入分析crypto/tls**

只要我们能在本地重现它,就能弄懂它。crypto/tls的错误消息缺少详细的信息，但是快速的调整允许我们精确定位错误在哪里发生。

每次发生错误时，都会调用setErrorLocked记录错误，并确保所有后续操作失败。该函数通常从错误的站点调用。

我们应该在panic(err)处进行堆栈跟踪，它会告诉我们消息在哪出现异常。

    
    
    diff --git a/src/crypto/tls/conn.go b/src/crypto/tls/conn.go  
    index 77fd6d3254..017350976a 100644  
    --- a/src/crypto/tls/conn.go
    +++ b/src/crypto/tls/conn.go
    @@ -150,8 +150,7 @@ type halfConn struct {
     }
     
     func (hc *halfConn) setErrorLocked(err error) error {
    -       hc.err = err
    -       return err
    +       panic(err)
     }
     
     // prepareCipherSpec sets the encryption and MAC states
    panic: local error: tls: unexpected message
     
    goroutine 1 [running]:  
    panic(0x185340, 0xc42006fae0)  
        /Users/filippo/code/go/src/runtime/panic.go:500 +0x1a1
    crypto/tls.(*halfConn).setErrorLocked(0xc42007da38, 0x25e6e0, 0xc42006fae0, 0x25eee0, 0xc4200c0af0)  
        /Users/filippo/code/go/src/crypto/tls/conn.go:153 +0x4d
    crypto/tls.(*Conn).sendAlertLocked(0xc42007d880, 0x1c390a, 0xc42007da38, 0x2d)  
        /Users/filippo/code/go/src/crypto/tls/conn.go:719 +0x147
    crypto/tls.(*Conn).sendAlert(0xc42007d880, 0xc42007990a, 0x0, 0x0)  
        /Users/filippo/code/go/src/crypto/tls/conn.go:727 +0x8c
    crypto/tls.(*Conn).readRecord(0xc42007d880, 0xc400000016, 0x0, 0x0)  
        /Users/filippo/code/go/src/crypto/tls/conn.go:672 +0x719
    crypto/tls.(*Conn).readHandshake(0xc42007d880, 0xe7a37, 0xc42006c3f0, 0x1030e, 0x0)  
        /Users/filippo/code/go/src/crypto/tls/conn.go:928 +0x8f
    crypto/tls.(*clientHandshakeState).doFullHandshake(0xc4200b7c10, 0xc420070480, 0x55)  
        /Users/filippo/code/go/src/crypto/tls/handshake_client.go:262 +0x8c
    crypto/tls.(*Conn).clientHandshake(0xc42007d880, 0x1c3928, 0xc42007d988)  
        /Users/filippo/code/go/src/crypto/tls/handshake_client.go:228 +0xfd1
    crypto/tls.(*Conn).Handshake(0xc42007d880, 0x0, 0x0)  
        /Users/filippo/code/go/src/crypto/tls/conn.go:1259 +0x1b8
    crypto/tls.DialWithDialer(0xc4200b7e40, 0x1ad310, 0x3, 0x1af02b, 0xf, 0xc420092580, 0x4ff80, 0xc420072000, 0xc42007d118)  
        /Users/filippo/code/go/src/crypto/tls/tls.go:146 +0x1f8
    crypto/tls.Dial(0x1ad310, 0x3, 0x1af02b, 0xf, 0xc420092580, 0xc42007ce00, 0x0, 0x0)  
        /Users/filippo/code/go/src/crypto/tls/tls.go:170 +0x9d

让我们看看异常的消息警报会发送到哪里conn.go:672。

    
    
     670     case recordTypeChangeCipherSpec:
     671         if typ != want || len(data) != 1 || data[0] != 1 {
     672             c.in.setErrorLocked(c.sendAlert(alertUnexpectedMessage))
     673             break
     674         }
     675         err := c.in.changeCipherSpec()
     676         if err != nil {
     677             c.in.setErrorLocked(c.sendAlert(err.(alert)))
     678         }

所以异常的消息是ChangeCipherSpec。让我们检查上一级的堆栈,看看是否有线索。让我们看看handshake_client.go:262。

    
    
     259 func (hs *clientHandshakeState) doFullHandshake() error {
     260     c := hs.c
     261
     262     msg, err := c.readHandshake()
     263     if err != nil {
     264         return err
     265     }

这是doFullHandshake函数。等等，这里的服务器显然正在进行会话复用（在Server Hello之后立即发送一个Change Cipher
Spec），而客户端正在尝试进行完整握手？

看起来情况是,客户端提供Session Ticket，服务器接受它，但是客户端并不知道并继续执行下去。

  

**深入RFC**

在这一点上，我查阅了TLS 1.2的相关信息,以了解服务器是如何表示接受Session Ticket？

[RFC 5077](https://tools.ietf.org/html/rfc5077),过时的RFC 4507：

当携带一个ticket时,客户端会在TLS ClientHello中生成并包含一个Session ID. 如果服务器接收了ticket并且Session
ID不为空,它必须马上返回与ClientHello相同的Session ID.

因此，客户端不应该猜测是否Session Ticket会被接受, 客户端应该发送一个Session ID并在服务器的回显中查找这个Session ID。

crypto/tls中的代码很明显的说明了这一点。

    
    
    func (hs *clientHandshakeState) serverResumedSession() bool {  
        // If the server responded with the same sessionId then it means the
        // sessionTicket is being used to resume a TLS session.
        return hs.session != nil && hs.hello.sessionId != nil &&
            bytes.Equal(hs.serverHello.sessionId, hs.hello.sessionId)
    }

**深入分析Session IDs**

一定是这里出错了。让我们加入一些基于打印输出的调试。

    
    
    diff --git a/src/crypto/tls/handshake_client.go b/src/crypto/tls/handshake_client.go  
    index f789e6f888..2868802d82 100644  
    --- a/src/crypto/tls/handshake_client.go
    +++ b/src/crypto/tls/handshake_client.go
    @@ -552,6 +552,8 @@ func (hs *clientHandshakeState) establishKeys() error {
     func (hs *clientHandshakeState) serverResumedSession() bool {
            // If the server responded with the same sessionId then it means the
            // sessionTicket is being used to resume a TLS session.
    +       println(hex.Dump(hs.hello.sessionId))
    +       println(hex.Dump(hs.serverHello.sessionId))
            return hs.session != nil && hs.hello.sessionId != nil &&
                    bytes.Equal(hs.serverHello.sessionId, hs.hello.sessionId)
     }
    00000000  a8 73 2f c4 c9 80 e2 ef  b8 e0 b7 da cf 0d 71 e5  |.s/...........q.|
     
    00000000  a8 73 2f c4 c9 80 e2 ef  b8 e0 b7 da cf 0d 71 e5  |.s/...........q.|  
    00000010  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|

F5服务器将Session ID填充到它的最大长度32字节，而不是当客户端发送它时再返回它。crypto / tls在Go中使用16字节会话ID。

从这里看错误就很明显了：服务器认为它告诉客户端使用Ticket而客户端认为服务器启动了新会话，于是意外就发生了。

在TLS空间中，我们发现了一些不兼容性。为了[不与某些服务器实现发生冲突](https://bugs.chromium.org/p/chromium/issues/detail?id=315828),ClientHellos必须小于256字节或大于512字节。

    
    
    00000000  79 bd e5 a8 77 55 8b 92  41 e9 89 45 e1 50 31 25  |y...wU..A..E.P1%|
    00000000  79 bd e5 a8 77 55 8b 92  41 e9 89 45 e1 50 31 25  |y...wU..A..E.P1%|  
    00000010  04 27 a8 4f 63 22 de 8b  ef f9 a3 13 dd 66 5c ee  |.'.Oc".......f.|

噢哦。等等。这些不是零也不是填充。那是…内存？

在这一点上，和Heartbleed的处理类似。服务器申请和客户端的会话ID一样大的缓冲区，然后总是返回32个字节的数据，在额外的字节里携带着未分配的内存数据。

  

**深入浏览器**

我最后一个疑问是：为什么之前没有发现这个漏洞？

答案是:所有浏览器使用32字节的SESSION ID来协商SESSION TICKET。我和Nick
Sullivan一起检查了NSS，OpenSSL和BoringSSL来确认这个问题。[以BoringSSL](https://github.com/google/boringssl/blob/33fe4a0d1406f423e7424ea7367e1d1a51c2edc1/ssl/handshake_client.c#L1901-L1908)为例。

    
    
      /* Generate a session ID for this session based on the session ticket. We use
       * the session ID mechanism for detecting ticket resumption. This also fits in
       * with assumptions elsewhere in OpenSSL.*/
      if (!EVP_Digest(CBS_data(&ticket), CBS_len(&ticket),
                      session->session_id, &session->session_id_length,
                      EVP_sha256(), NULL)) {
        goto err;
      }

BoringSSL使用SHA256作为SESSION TICKET，正好是32个字节。

(有趣的是，在TLS中，有人提到使用1字节的SESSION ID，但是没有人对它进行测试。)

至于Go，可能是客户端没有启用SESSION TICKET。

  

**深入披露**

在意识到这个问题的影响之后，我们在公司内部进行了分享,我们的支持团队会建议客户禁用SESSION TICKET，并试图联系F5。

我们与F5 SIRT联系，交换PGP密钥，并提供报告和PoC。

报告已提交给开发团队，确定问题是未初始化的内存，但是仅限于Session Ticket功能。

目前还不清楚哪些数据可以通过此漏洞泄露，但是HeartBleed和[Cloudflare Heartbleed
Challenge](https://blog.cloudflare.com/the-results-of-the-cloudflare-challenge/)告诉我们未初始化的内存是不安全的

在规划时间表时，F5团队面临着严格的发布计划。综合考虑多种因素，包括有效的缓解（禁用Session Ticket），我决定采用由[Google's
Project
Zero发布的业界标准的披露政策](https://googleprojectzero.blogspot.co.uk/2015/02/feedback-and-data-driven-updates-to.html)：在115天之后,如果漏洞没有被修复,就会被披露。

巧合的是今天正好是计划发布修复补丁的截至日期。

我要感谢F5 SIRT的专业性，透明度和协作性，这和我们在业内经常听到的对抗性形成鲜明对比。

该漏洞已分配CVE-2016-9244。

**  
**

**深入互联网**

当我们向F5报告问题时，我已经针对单个主机测试了该漏洞，该主机在禁用Session
Ticket后很快变得不可用。这意味着漏洞具有低信度，并且没有办法再现它。

这是进行互联网扫描的绝佳场合。我选择了由密歇根大学授权Censys.io的工具包：zmap和zgrab。

zmap是一种用于检测开放端口的IPv4空间扫描工具，而zgrab是一种Go工具，通过连接到这些端口并收集大量协议详细信息来进行跟踪。

我在zgrab添加对Session
Ticket复用的支持，然后让zgrab发送一个31字节的会话ID，并将其与服务器返回的ID进行比较。我写了一个简单的Ticketbleed检测器。

    
    
    diff --git a/ztools/ztls/handshake_client.go b/ztools/ztls/handshake_client.go  
    index e6c506b..af098d3 100644  
    --- a/ztools/ztls/handshake_client.go
    +++ b/ztools/ztls/handshake_client.go
    @@ -161,7 +161,7 @@ func (c *Conn) clientHandshake() error {
                    session, sessionCache = nil, nil
                    hello.ticketSupported = true
                    hello.sessionTicket = []byte(c.config.FixedSessionTicket)
    -               hello.sessionId = make([]byte, 32)
    +               hello.sessionId = make([]byte, 32-1)
                    if _, err := io.ReadFull(c.config.rand(), hello.sessionId); err != nil {
                            c.sendAlert(alertInternalError)
                            return errors.New("tls: short read from Rand: " + err.Error())
    @@ -658,8 +658,11 @@ func (hs *clientHandshakeState) processServerHello() (bool, error) {
     
            if c.config.FixedSessionTicket != nil {
                    c.resumption = &Resumption{
    -                       Accepted:  hs.hello.sessionId != nil && bytes.Equal(hs.serverHello.sessionId, hs.hello.sessionId),
    -                       SessionID: hs.serverHello.sessionId,
    +                       Accepted: hs.hello.sessionId != nil && bytes.Equal(hs.serverHello.sessionId, hs.hello.sessionId),
    +                       TicketBleed: len(hs.serverHello.sessionId) > len(hs.hello.sessionId) &&
    +                               bytes.Equal(hs.serverHello.sessionId[:len(hs.hello.sessionId)], hs.hello.sessionId),
    +                       ServerSessionID: hs.serverHello.sessionId,
    +                       ClientSessionID: hs.hello.sessionId,
                    }
                    return false, FixedSessionTicketError
            }

选择31字节的原因是我可以确保不泄露敏感信息。

然后，我从Censys网站下载最近的扫描结果，其中包括什么主机支持Session Ticket信息，并使用pv和jq完成了管道。

在11月份的Alexa top 1m列表中的前1,000个主机中有2个存在漏洞，我中断了扫描，避免泄露漏洞，并推迟到了披露日期。

在完成这篇指导时，我完成了扫描，0.1％和0.2％的主机容易受到攻击，0.4％的网站支持Session Ticket。

  

**阅读更多**

欲了解更多详情，请访问[F5
K05121675文章](https://support.f5.com/csp/article/K05121675)或[ticketbleed.com](https://ticketbleed.com/)，在那里你会发现一个技术总结，受影响的版本，缓解指令，一个完整的时间表，扫描结果，扫描机器的IP地址，并可以进行在线测试。

否则，你应该[关注我的Twitter](https://twitter.com/FiloSottile)。

  

本文翻译自blog.filippo.io [原文链接](https://blog.filippo.io/finding-ticketbleed/
)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **胖胖秦** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/85456](/post/id/85456)

安全客 - 有思想的安全新媒体

本文转载自: [blog.filippo.io](https://blog.filippo.io/finding-ticketbleed/ )

如若转载,请注明出处： <https://blog.filippo.io/finding-ticketbleed/ >

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __1赞

 __收藏

![](https://p5.ssl.qhmsg.com/dm/200_200_100/t0130c8844942b1f889.jpg) 胖胖秦

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

