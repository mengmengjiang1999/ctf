# 你不在意的HTTPS证书吊销机制

阅读量 **351873**

|评论 **1**

发布时间 : 2019-08-05 11:30:11

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t01560270be3c1df5b7.jpg)

作者：陈驰 （CFC4N）现任美团安全部技术专家，十年以上互联网产品研发经验，专注于分布式系统架构设计，目前主要从事安全防御产品研发工作。

## 缘起

偶刷《长安十二时辰》，午睡时，梦到我穿越到了唐朝，在长安城中的靖安司，做了一天的靖安司司丞。当徐宾遇害消失的时候我不在司内，当时的情形我不得而知。后来徐宾醒了，据他描述说“通传陆三”是暗桩，险些致徐宾于死地。而擅长大案牍术的高智商人才居然被一个普通通传的几句话骗至险境，实在丢了我的脸。陆三是通传，熟知靖安司的号令传递系统望楼信号，他是暗桩的消息，传遍整个机构。这让张小敬和姚汝能认为望楼系统已无法完成消息保密传送的功能，其实他们根本不了解这望楼。整个望楼系统由“传递系统+加密系统”组成，靖安司作为一个军事级别的机构，信息传递绝对是多重加密的。只看懂望楼图案，或者只有密码本都是破译不了密码的，对于通传陆三是暗桩的影响，也只需要更换密码本即可。这些可是我学了RSA非对称加密后设计的望楼系统，早就评估过这些风险了。即使HTTPS通讯中，丢了密钥也…嗯？如果HTTPS证书私钥丢了，会怎样？是不是也没法防范这个私钥被利用了？想到这个问题，我突然从梦中惊醒，去温故一下证书吊销机制。

#

## 疑问

  * HTTPS的证书过期是谁来判断？

  * HTTPS的证书过期是谁来判断？
  * 证书的合法性又是谁检查的呢？
  * 什么时候触发?
  * 影响性能吗?
  * 如何吊销证书?
  * HTTPS的请求是客户端（浏览器）发起的，他是如何知道证书被吊销的？
  * 验证HTTPS证书的过程是什么样的？

## HTTPS通讯过程

大家都清楚，HTTPS的握手是在TCP握手完成后，流程都熟的很，但还是要温故一下：

![](https://p5.ssl.qhimg.com/t0180db68b9c44f849e.jpg)

1.第一个阶段，完成 Client Hello、Server
Hello等握手。包含使用SSL版本、服务器和客户端的随机数、密码套件、数据压缩等参数响应。2.第二阶段，服务端把域名证书的公钥下发给浏览器（客户端），浏览器（客户端）校验证书合法性。3.第三阶段，客户端把自己的证书发送给服务端（证书登陆的情况下），服务端检测客户端证书等。4.第四阶段，完成密钥协商、对称加密密钥交换。

（简称解释：RN: Random Number；PMS: Pre Master Secret；MS: Master Secret）

对于第二阶段中的证书检验这块，相信很多人都不太了解，甚至都不知道会检验什么内容，那么下面我们就来了解一下。

### 证书完整性验证

使用RSA公钥解密来验证证书上的私钥签名是否合法，如果签名无效，则可认定证书被修改，直接报错。

### 证书有效性验证

CA在颁发证书时，都为每个证书设定了有效期，包括开始时间与结束时间。系统当前时间不在证书起止时间的话，都认为证书是无效的。

### 证书吊销状态检测

如果，证书在有效期之内需要丢了怎么办？需要吊销证书了，那么这里就多了一个证书吊销状态的检测。用户将需要吊销的证书通知到CA服务商，CA服务商通知浏览器该证书的撤销状态。来看一个证书吊销后的浏览器提醒：

![](https://p3.ssl.qhimg.com/t017fb34208c7b8781e.jpg)

Chrome返回了NET::ERR_CERT_REVOKED，并且拒绝继续访问，更不提供强制访问的接口，没了继续访问的手动点击链接。

### 验证发行者

HTTPS数字证书的使用分两个角色：

  * 证书发行方issuer，有签名密钥的私钥。
  * 证书申请方subject，使用证书公钥进行身份验证的用户 浏览器检查证书的发行者字段与证书路径中上级证书的subject字段相同。

为了增加安全性，PKI在实现时，多数都验证了发型方的密钥、签名等信息是否跟当前证书的密钥相同。但对于信任链来说，根证书自己签发的，也就是说它们的issuer和subject是一样的。

同时，这些CA根证书都是被操作系统、浏览器等直接打入系统的。比如：

![](https://p5.ssl.qhimg.com/t0145acc6582c95054d.jpg)

### 检查域名(IP)规范

中间CA提供了对域名证书的管理以及颁发的颗粒度度控制。证书的生效范围会限于固定域名、域名范围（包括子域）或者固定IP。比如下图是https://www.baidu.com的HTTPS证书DNS信息。

![](https://p1.ssl.qhimg.com/t015b0bf64be1d651b2.jpg)

上图所示，DNS范围包含了多个域名，同时二级以及二级以上域名都支持范围形式。以*通配义字符表示。但*.example.com的二级域名范围就不能包含a.b.example.com这个三级域名。同时，DNS范围也支持IP的，只是IP不支持范围形式，必须把所有IP列表都放入列表中。

### 检查策略约束

法律策略相关检测（略）。

### 证书的吊销状态检测方式

上面提到了浏览器（客户端）在验证证书合法性时的验证范围，我们暂时只关注证书吊销信息的检测，下面我们仔细来了解一下两种检测机制的实现原理。

## 1\. Certificate Revocation Lists (CRL)

CA会定期更新发布撤销证书列表，Certificate Revocation Lists (以下简称CRL)，RFC 5280：Internet X.509
Public Key Infrastructure Certificate and Certificate Revocation List (CRL)
Profile。CRL分布在公共可用的存储库中，浏览器可以在验证证书时获取并查阅CA的最新CRL。该方法的一个缺陷是撤销的时间粒度限于CRL发布期。只有在计划更新所有当前发布的CRL之后，才会通知浏览器撤销。各家签名CA厂商的策略不一样，有的是几小时，有的是几天，甚至几周。2015年，美国几所大学的学生论文中，统计了当时的CA证书吊销情况，如下图：

![](https://p3.ssl.qhimg.com/t01a8a8313ee7a0e9f9.jpg)

这个统计可以看出，CA证书厂商的CRL数量不一，大部分是30-50个，而GoDaddy有300多个CRL的地址，同时有近30W个证书是吊销状态的，文件大小平均达到了1M。

  * ### 证书的CRL信息

CRL信息是CA在颁发证书时，写入在X.509 v的扩展区域的，比如alipay.com的证书信息：

![](https://p3.ssl.qhimg.com/t01db9defab586be524.jpg)

可以看到，其CRL信息为http://crl3.digicert.com/SecureSiteCAG2.crl
以及http://crl4.digicert.com/SecureSiteCAG2.crl

  * ### CRL 检测流程

![](https://p3.ssl.qhimg.com/t014323995fe59bea82.png)

可以想象一下，在浏览器去校验证书合法性时，还要去下载一个1M的文件后，再去校验。校验通过后才去连想要访问的网站服务器，这相当浪费时间、效率。同时，很多浏览器所处网络是有网络访问限制的，可能在一个局域网，比如我们村，或者物理距离非常远，存在严重的网络延迟问题。

## 2\. Online Certificate Status Protocol (OCSP)

在RFC2560X.509 Internet Public Key Infrastructure Online Certificate Status
Protocol – OCSP的描述中，浏览器从在线OCSP服务器（也称为OCSP Response Server）请求证书的撤销状态，OCSP
Server予以响应。这种方法避免CRL更新延迟问题。同样的，X.509
v3证书的OCSP信息也是存储在拓展信息中，如alipay.com证书那张图的绿色框内部分。

  * ### OCSP 检测流程

![](https://p5.ssl.qhimg.com/t01de896a630522ab22.png)

浏览器在获得Web服务器的公钥证书后，开始验证公钥的合法性，这里会向该公钥的扩展信息中提供的OCSP Server地址发送OCSP
Response，获得响应后，确认证书有效，再继续跟Web服务器通信。

  * ### OCSP的优点

相对于CRL方式，证书吊销后，CA Server可以立刻将吊销信息发送给浏览器，生效时间快。响应包内容短，不像CRL的响应包，都将近1M以上。

  * ### OCSP的缺点

第一个缺点：浏览器的每次HTTPS请求创建，都需要连接CA OCSP Server进行验证，有的浏览器所在IP与CA OCSP
Server的网络并不是通畅的，比如我们村。而且，OCSP的验证有网络IO，花费了很长的时间，严重影响了浏览器访问服务器的用户体验。

第二个缺点：在浏览器发送服务器HTTPS证书序号到CA OCSP Server时，也将暴露了用户的隐私，将用户访问的网址透漏给了CA OCSP
Server。

  * ### OCSP机制衍生出来的问题

设想一个场景，你是浏览器企业，研发的浏览器在检查证书吊销状态时，得不到OCSP server的响应，你会如何选择？

  * 如果你选择拒绝该证书信息，并且拒绝后续的HTTPS通讯，那么这个方式称之为Hard-fail
  * 如果你选择信任该证书，认为没有被吊销，那么这个方式称之为Soft-fail

如果是hard-fail模式，那浏览器对任何HTTPS服务器访问的先决条件都取决于OCSP
Server，这将是一个致命的单点故障，对于具有资深架构设计经验的你来说，你会这么选择吗？

如果是soft-fail模式，取不到OCSP Server的响应就忽略了，那么，要这个机制还有啥意义呢？要你有何用？

  * ### OCSP Stapling

OCSP Stapling的方案是解决了CRL、OCSP的缺点，将通过OCSP Server获取证书吊销状况的过程交给Web 服务器来做，Web
服务器不光可以直接查询OCSP信息，规避网络访问限制、OCSP服务器离用户的物理距离较远等问题，还可以将查询响应缓存起来，给其他浏览器使用。由于OCSP的响应也是具备CA
RSA私钥签名的，所以不用担心伪造问题。

  * 解决了访问慢的问题
  * 解决了用户隐私泄露的问题

通讯过程如上，但对于Web服务器在去OCSP Server查询证书状态时，也同样面临无法获取到OCSP
Response的问题，在响应给浏览器时，浏览器也还是要面临hard-fail、soft-fail的选择问题，这很让浏览器头大。

  * ### OCSP Must-Staple

面对hard-fail、soft-fail的问题，各家浏览器厂商的态度都不一样。同时，不管浏览器如何选择，都不能满足广大域名用户的需求，那么不如把这个选择交给域名用户自己。为此，OCSP
Must-Staple应运而生了，浏览器必须检测OCSP响应。域名证书创建时，自定义设定启用这个选项，将这个信息打入X.509
v3的扩展中，浏览器读取后，强制进行OCSP检测，走hard-fail模式。这个规范被起草在 X.509v3 Extension: OCSP
Stapling Required draft-hallambaker-muststaple-00 ，不过，暂未被采纳为RFC标准。

  * ### CA厂商支持

目前支持该扩展的证书的CA厂商有Let’s Encrypt。如果使用的是openssl 1.1.0
以前的版本，可以使用11.3.6.1.5.5.7.1.24 = DER:30:03:02:01:05 来指定。RFC
比如生成csr的时候，在openssl.cnf中增加： [v3_req ]  
basicConstraints = CA:FALSE  
keyUsage = nonRepudiation, digitalSignature, keyEncipherment  
subjectAltName = @alt_names  
1.3.6.1.5.5.7.1.24 = DER:30:03:02:01:05如果是使用openssl 1.1.0或更高的版本，可以这样设置：[
v3_req ]  
basicConstraints = CA:FALSE  
keyUsage = nonRepudiation, digitalSignature, keyEncipherment  
subjectAltName = @alt_names

## 各平台上浏览器对证书吊销的支持情况

### 1\. Mac Safari

在Mac OS X 10.7 (Lion)以后，Safari/macOS默认情况下，不检测CRLs、OCSP，走自己的key
chain体系。（资料比较少，apple官方也搜不到几条）

### 2\. Windows Internet Explorer

Windows Vista系统开始，Internet Explorer
7浏览器内置了CryptoAPI，来支持OCSP方式检测证书吊销情况。检测范围包括issuer发行商的证书、subject服务器的证书。为什么IE访问HTTPS的网站时，会比别的浏览器慢？你应该已经知道答案了。

### 3\. Mozilla Firefox

在2010年时，Mozilla Firefox的所有版本都支持OCSP方式检测。在Firefox
3里把OCSP检测机制设定为默认机制。在以后的版本更新中，Firefox针对中级证书跟域名证书做了不同的策略。 **中级证书的吊销状态验证**
在2015年，Firefox
37开始，针对中级证书的检测，Mozilla也启用了自研的证书吊销状况检查机制OneCRL来代替OCSP机制，目的还是想解决CRL、OCSP机制的缺点。而中级证书是不能采用OCSP
stapling方式，不允许被缓存的。所以…还有， RFC 6961 defines a mechanism for stapling OCSP
responses for CA certificates. Since FIrefox does not rely on OCSP to validate
intermediate certificates, we have no plans to implement support for this.

Firefox 官方短期内并无支持Multi-staple的打算。

**域名证书的吊销状态验证** 在Firefox的官方WIKI上，提到针对域名证书的吊销验证分为如下5个方案：方案一：Short-Lived
Certificates，默认情况下，针对有效期少于10天的证书，直接跳过验证，认为不安全。可以在security.pki.cert_short_lifetime_in_days参数里配置。方案二：OCSP
Stapling，跟RFC规范一样。如果security.OCSP.enabled的值为0，则忽略OCSP response。方案三：OCSP Must-staple，跟RFC规范一样。可以通过设置security.ssl.enable_ocsp_must_staple或security.ssl.enable_ocsp_stapling
参数来禁用。

方案四：OCSP，跟RFC规范一样。如果OCSP的响应在2秒（EV证书是10秒）内没返回，则直接忽略。

方案五：CRLite，类似Chrome CRLSets的一种检测机制，用于OCSP、OCSP
stapling失败后的机制。Firefox的官方计划把这种机制作来代替CRL方式作为主要的检测机制（OCSPOCSP stapling失败后）。

### 4\. Chrome

2012年，Chrome禁用了CRLs、OCSP检测: Google Chrome Will No Longer Check for Revoked SSL
Certificates Online ，使用了自行设计的证书校验机制 CRLSets

那么，Chrome这么选择的理由是什么呢？显然，通过上面CRL跟OCSP两种验证方式的比较来看，前者时效性不行，后者影响性能。那么，google
Chrome就决定自建证书吊销状态验证系统。Chrome的安全工程师Adam Langley在他的BLOG上写了一篇文章：《Revocation
checking and Chrome’s CRL》，对于Chrome的HTTPS证书验证这块，Adam
Langley可是非常有看法的，非常反对使用CRL、OCSP的方式来校验证书吊销状态，连续写了好几篇关于证书吊销状态检测的文章，同时，也在chromium的开发者主页上的安全板块有提到【What’s
the story with certificate revocation?】： Chrome’s primary mechanism for
checking the revocation status of HTTPS certificates is CRLsets.Chrome also
supports Online Certificate Status Protocol (OCSP). However, the effectiveness
of OCSP is is essentially 0 unless the client fails hard (refuses to connect)
if it cannot get a live, valid OCSP response. No browser has OCSP set to hard-fail by default, for good reasons explained by Adam Langley (see [Revocation
still doesn’t work](No, don’t enable revocation checking) and
https://www.imperialviolet.org/2014/04/19/revchecking.html).

Stapled OCSP with the Must Staple option (hard-fail if a valid OCSP response
is not stapled to the certificate) is a much better solution to the revocation
problem than non-stapled OCSP. CAs and browsers are working toward that
solution (see the Internet-Draft: http://tools.ietf.org/html/draft-hallambaker-tlssecuritypolicy-03).

Additionally, non-stapled OCSP poses a privacy problem: in order to check the
status of a certificate, the client must query an OCSP responder for the
status of the certificate, thus exposing a user’s HTTPS browsing history to
the responder (a third party).

That said, you can use enterprise policies to enable soft-fail OCSP
(http://www.chromium.org/administrators/policy-list-3#EnableOnlineRevocationChecks) and hard-fail OCSP for local trust
anchors (http://www.chromium.org/administrators/policy-list-3#RequireOnlineRevocationChecksForLocalAnchors).

Chrome performs online checking for Extended Validation certificates if it
does not already have a non-expired CRLSet entry covering the domain. If
Chrome does not get a response, it simply downgrades the security indicator to
Domain Validated.

See also this bug for more discussion of the user-facing UX:
https://crbug.com/361820.

但这也不是完美解决了这个问题，来自【An Evaluation of the Effectiveness of Chrome’s CRLSets】：

This means that Chrome’s CRLSet, which currently lists the serial numbers of
24,206 revoked certificates, reflects only 1.08% of the revoked certificates
collected by Websense in one hour.

这篇文章中提到CRLSet的最大问题是包含的证书吊销数据太少，个别情况下占了主流CRL证书吊销信息的2%不到。而且，CRLSets的更新也不是那么及时，chrome为了用户体验，为了性能，为了用户隐私，牺牲了一点点安全性，也是可以理解的。但好像对不起最安全浏览器的称号了。[手动狗头]

## 汇总

![](https://p5.ssl.qhimg.com/t0117e11ab834334ea3.jpg)

如上图，在2015年，Northeastern University、University of Maryland、Duke
University等几所大学的研究人员分析了市场上流行的五个浏览器（多个平台、多个版本），把各个浏览器在不同级别证书下的支持情况绘制了表格。（论文在参考文献中给出）从图中可以看出，我们印象中最安全的浏览器Chrome表现却让你大跌眼镜，在HTTPS的安全性这块，表现最差。上面我们也谈到，chrome为了访问速度隐私等用户体验考虑，忽略了CRL、OCSP等证书吊销状态检测机制，牺牲了TLS这块的安全性支持。而IE浏览器却出乎我们意料，在HTTPS的安全性这块，支持的非常好，可以说是这几个浏览器中最安全的了，可是…可是他网页打开速度慢啊…截至至今天（2019年7月16日），已经4年过去了，很多浏览器、WebServer的支持情况也有很大的变化，并不能反映出当下互联网的现状，这些数据也作为参考吧。

### 附：WebServer的支持情况

  * The Apache web server has supported OCSP stapling since v2.3.3 (ref).
  * The nginx web server has supported OCSP stapling since v1.3.7 (ref).

## 总结

### 证书泄露的危害

那么，证书丢了，会对网站安全产生很大影响吗？回头看下使用该证书的条件：

  * 具备证书
  * 具备域名
  * 浏览器访问该服务器

如果几个都具备，那么你就是该网站的官方了。

在安全界，有个攻击手段，叫Man-in-the-middle
attack中间人攻击，如果证书被黑客拿到，搭建一个具备相同域名的网站，通过DNS污染的方式使得用户浏览器访问该域名，那么可以成为一个反向代理，把用户的请求解析后，伪造程客户端来跟真实的Web服务器通讯，从而获取双方通信的明文信息，达到攻击的目的。

![](https://p0.ssl.qhimg.com/t01f6ff407015eb18e0.png)

那这种情况怎么防范？中间人攻击的防御方式是开启客户端对证书的认证，但你的证书私钥又丢了，那能咋办？通过本文前面章节的了解到，这种情况，也只能主动到CA厂商那申请证书吊销了，不管有几个浏览器支持，也得申请，毕竟，这损失能减少一点是一点。

### 证书泄露了怎么办？

证书泄露了怎么办？从浏览器的支持情况来看，好像及时申请吊销了证书，也不能对丢失的证书起到太大的防范作用，很多浏览器并不是很支持的嘛。

不过，多少也能避免一些损失，毕竟IE浏览器对这块的支持力度还是很大的嘛。

### 注

本文的参考文献，大部分都是5-6年前的资料，这么多年过去了，互联网技术产品日新月异，里面很多结论早已不符合现状，尤其是浏览器当今对证书吊销状态检测的支持情况。部分内容，仅作为参考，便于读者去了解技术变迁的背景知识。

## 参考文献

  * RFC3280 Internet X.509 Public Key Infrastructure Certificate
  * High-reliability OCSP stapling and why it matters
  * Security Certificate Revocation AwarenessThe case for “OCSP Must-Staple”
  * Security Certificate Revocation AwarenessSpecific Implementations
  * Security Sidebar: My Browser Has No Idea Your Certificate Was Just Revoked
  * SSL certificate revocation and how it is broken in practice
  * Revoking Intermediate Certificates: Introducing OneCRL
  * Revocation doesn’t work (18 Mar 2011)
  * Revocation checking and Chrome’s CRL (05 Feb 2012)
  * No, don’t enable revocation checking (19 Apr 2014)
  * Revocation still doesn’t work (29 Apr 2014)
  * An End-to-End Measurement of Certificate Revocation in the Web’s PKI

## 结束

嗯？话说《长安十二时辰》中望楼消息传送机制的加固呢？嗨，梦都醒了，谁还记得这事啊。

### 团队介绍

美团安全部的大多数核心人员，拥有多年互联网以及安全领域实践经验，很多同学参与过大型互联网公司的安全体系建设，其中也不乏全球化安全运营人才，具备百万级IDC规模攻防对抗的经验。安全部也不乏CVE“挖掘圣手”，有受邀在Black
Hat等国际顶级会议发言的讲者，当然还有很多漂亮的运营妹子。目前，美团安全部涉及的技术包括渗透测试、Web防护、二进制安全、内核安全、分布式开发、大数据分析、安全算法等等，同时还有全球合规与隐私保护等策略制定。我们正在建设一套百万级IDC规模、数十万终端接入的移动办公网络自适应安全体系，这套体系构建于零信任架构之上，横跨多种云基础设施，包括网络层、虚拟化/容器层、Server
软件层（内核态/用户态）、语言虚拟机层（JVM/JS
V8）、Web应用层、数据访问层等，并能够基于“大数据+机器学习”技术构建全自动的安全事件感知系统，努力打造成业界最前沿的内置式安全架构和纵深防御体系。随着美团的高速发展，业务复杂度不断提升，安全部门面临更多的机遇和挑战。我们希望将更多代表业界最佳实践的安全项目落地，同时为更多的安全从业者提供一个广阔的发展平台，并提供更多在安全新兴领域不断探索的机会。

### 一个广告

美团安全2019年招聘火热进行中~如果你想加入我们，欢迎简历请发至邮箱zhaoyan17@meituan.com。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **美团安全应急响应中心** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/183339](/post/id/183339)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Https](/tag/Https)

 **+1** __7赞

 __收藏

![](https://p2.ssl.qhimg.com/t011de8b7028cee15f8.png) 美团安全应急响应中心

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

