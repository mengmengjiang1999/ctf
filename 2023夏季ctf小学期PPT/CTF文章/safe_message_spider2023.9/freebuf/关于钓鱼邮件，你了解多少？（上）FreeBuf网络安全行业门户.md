![](https://image.3001.net/images/20210204/1612423126_601b9fd62eab288be3b5c.png!small)

这一两年来，由于祖国对信息安全的重视，各事业单位、关键基础设施在经过一轮轮hvv的锤炼后，简单的漏洞变得越来越少，蓝队攻击的成本越来越高，要不是有反序列化、fastjson、thinkphp、shiro等饭碗，日子就越来越不好过了。同时也包括一些wa的取证项目，已经很少有thinkphp一把梭的小可爱了。这时候在不想被领导骂菜的情况下，只能研究一下钓鱼了。

>
> 之前也经常也接到一些钓鱼邮件的实施工作，不过都是gophish加一个企业邮发过去了事。比较浅显，也只是以点击链接给出警示，点到为止。并不会有后续操作。钓鱼按照目的来分，有两种：
>
> 一种是在钓鱼邮件中防止一个链接或者二维码，用于搜集一些关键系统口令或者个人敏感信息。这种适用于钓鱼邮件演练的实施。
>
> 一种是直接在附件中、或者链接中引导下载RAT，直接控制对端计算机，然后在内网中横向移动，这种的场景是wa取证项目或者一些红蓝对抗。
>
> 其中几个难点如下：
>
> 1.如何投递邮件？
>
> 2.如何诱导对方点击你的恶意链接、恶意文件？
>
> 3.如何免杀自己的RAT？

在本文中，我们讨论前两个问题，免杀的话题大概加起来比前两个都多，下一篇会讨论。

##  ** **如何投递邮件？****

###  ** **1**** ** **.**** ** **有钱买域名****

在真实的钓鱼场景中，一般是用一些近似的邮箱或邮件服务商注册的邮箱，在给甲方做钓鱼邮件演练的时候，如果预算高，会注册一个和甲方域名相似的域名，可以使用[
_urlcrazy_](https://github.com/urbanadventurer/urlcrazy)工具自动寻找：urlcrazy -i
weibo.com

![1612418781_601b8edd8efc39fd87d28.png!small?1612418782091](https://image.3001.net/images/20210204/1612418781_601b8edd8efc39fd87d28.png!small?1612418782091)

> valid为false的就是没有人使用的，挑一个便宜的、顺眼的注册一个。
>
> 有了域名之后，我们还需要一个smtp服务器，这里推荐ewomail，安装很方便，可以一键部署：wget -c
> http://download.ewomail.com/ewomail-1.0.sh && sh ewomail-1.0.sh [你的域名]
>
>
> 找一台VPS跑一下这个命令你就可以拥有一整套邮件服务器组件，具体文档点击[这里](http://doc.ewomail.com/docs/ewomail/jianjie)

这里有个坑，在腾讯云上是无法连接其他机器的25端口，即使你的出站规则配置全开，也是要提交一个工单给客服，他们才会帮你开。

![1612420351_601b94ff5bb2fd69b4e7d.png!small?1612420352423](https://image.3001.net/images/20210204/1612420351_601b94ff5bb2fd69b4e7d.png!small?1612420352423)

然后我们再做一些DNS的配置工作，这一台smtp服务器就可以使用了。

这里我注册了一个[365-offices.com.cn](http://106.75.253.201:8000/)的域名，验证一下发给我司的腾讯企业邮：

![1612420387_601b9523a696492ba2f04.png!small?1612420389197](https://image.3001.net/images/20210204/1612420387_601b9523a696492ba2f04.png!small?1612420389197)

这样就能成功收到：![1612420407_601b95373cbf820c59760.png!small?1612420407946](https://image.3001.net/images/20210204/1612420407_601b95373cbf820c59760.png!small?1612420407946)

后面就到了第二个问题的范畴。

###  ** **2.没钱买域名****

也有一些赠送的钓鱼邮件测试或者时间紧迫的红蓝对抗，我们会因为各种原因没有自己的域名用，这时候称之为‘硬钓’，硬钓只能尽量的伪装，不做伪装：![1612420477_601b957d38bc312ae2cda.png!small?1612420477671](https://image.3001.net/images/20210204/1612420477_601b957d38bc312ae2cda.png!small?1612420477671)

显然，这也太不像了，最大的破绽是并不是同一个域名发出的，内容也比较简单。而且，曾经受到过客户灵魂发问，为什么你们发的钓鱼邮件地址不是也不像我们的域名？然后说要买一个域名，客户表示不需要。没办法，不吃草的马儿也要会跑！

钱不够技术来凑。让我们来伪装一下这封邮件，让它更具欺骗性。

首先，我们都知道支撑互联网邮件服务的是smtp协议，全称是（Simple Mail Transfer
Protocol），既然是简单协议，必然是牺牲一些安全性的，假定我们使用向alice@365-offices.com.cn发送邮件，来看一下最简单的发送邮件过程：

首先要找到邮件服务器地址，可以查询一下MX记录：

> root@h33l0:/home/p1pp0# nslookup -type=mx 365-offices.com.cn
>
> Server: 223.5.5.5
>
> Address: 223.5.5.5#53
>
> Non-authoritative answer:
>
> 365-offices.com.cn mail exchanger = 10 mail.365-offices.com.cn.

可以得到邮件服务器为mail.365-offices.com.cn。

![1612422098_601b9bd23d2d0b89294e3.png!small?1612422099231](https://image.3001.net/images/20210204/1612422098_601b9bd23d2d0b89294e3.png!small?1612422099231)

先快速介绍一下邮件传递的过程，我们使用的邮箱客户端程序，网页版的qq邮箱、Foxmail、outlook统称为MUA（Mail User
Agent）,他们只跟自己代理邮箱的smtp服务器（MTA）交互，而你使用qq邮箱向sina邮箱发送一封邮件，实际上最少经过4台机器，即：

> 发件MUA -> QQ MTA-> SINA MTA ->收件MUA。

网络上关于smtp底层的讲解都是以MUA的视角，即MUA通过认证登录到自己所属的MTA，再发送邮件，实际上我们可以直接与接受方的MTA交互，可以简化掉一些登录的流程，便于理解smtp的原理。

这里我们效仿swaks直接伪装成一台邮件服务器（MTA），而不是客户端（MUA），直接连接mail.365-offices.com.cn的25端口：

> === Trying mail.365-offices.com.cn:25...
>
> === Connected to mail.365-offices.com.cn.
>
> <\- 220 mail.365-offices.com.cn ESMTP Postfix

使用EHLO/HELO命令，向对端的MTA标识自己的身份，格式是EHLO + <domain>,MTA将返回一些元信息:

> -> EHLO abctest.com.cn
>
> <\- 250-mail.365-offices.com.cn
>
> <\- 250-PIPELINING
>
> <\- 250-SIZE
>
> <\- 250-ETRN
>
> <\- 250-STARTTLS
>
> <\- 250-AUTH PLAIN LOGIN
>
> <\- 250-AUTH=PLAIN LOGIN
>
> <\- 250-ENHANCEDSTATUSCODES
>
> <\- 250-8BITMIME
>
> <\- 250 DSN

接下来进入邮件发送部分，使用mail from命令指定邮件由谁发出：

> -> MAIL FROM:<admin@abctest.com>
>
> <\- 250 2.1.0 Ok

RCPT TO指定发送给谁：

> -> RCPT TO:<alice@365-offices.com.cn>
>
> <\- 250 2.1.5 Ok

使用DATA命令指定邮件正文，以[.]结束，

> -> DATA
>
> <\- 354 End data with <CR><LF>.<CR><LF>
>
> -> Date: Fri, 22 Jan 2021 02:19:04 -0500
>
> -> To: alice@365-offices.com.cn
>
> -> From: admin@abctest.com
>
> -> Subject: test Fri, 22 Jan 2021 02:19:04 -0500
>
> -> Message-Id: <20210122021904.1687008@h33l0>
>
> -> X-Mailer: swaks v20190914.0 jetmore.org/john/code/swaks/
>
> ->
>
> -> This is a test mailing
>
> ->
>
> ->
>
> -> .
>
> <\- 250 2.0.0 Ok: queued as 6488F6000103

QUIT结束连接。

> -> QUIT
>
> <\- 221 2.0.0 Bye
>
> === Connection closed with remote host.

###  ** **3.**** ** **邮件发送人伪造****

首先，我想先讨论发件人的伪造，如果邮箱后缀都不够相似的话，很难说是一封合格的邮钓鱼件。

我们观察以上最简单的发送邮件流程中，涉及到域名后缀的有三个地方：

> 与接收者MTA打招呼时的EHLO命令
>
> 指定发送人的MAIL FROM命令
>
> 正文里的From头部

原理上，我们可以按照上面讲述原理的过程，直接与对端MTA交互，自定义以上三个部分，就可以模拟任何地址发送邮件了，因为MTA之间没有任何认证的过程,我们来测试一下。

这里我们介绍一下[
_swaks_](https://github.com/jetmore/swaks)，是perl开发的邮件伪造工具，kali自带，简而言之，他封装了MTA之间的交互逻辑，你可以用它伪装成MTA或者使用真实邮箱与其他MTA交互。贴一下说明：

> \--from <要显示的发件人邮箱>
>
> \--ehlo <伪造的邮件ehlo头>
>
> \--body <邮件正文>
>
> \--header <邮件头信息，subject为邮件标题>
>
> \--data <源邮件>

后面有用到其他选项再说，swaks会默认使用：

> -> X-Mailer: swaks v20190914.0 jetmore.org/john/code/swaks/

X-mailer类似于web中的User-Agent，定义了客户端的类型，swaks作为著名工具会被检测出来，建议大家自己定义这个头部，方法是加上
--header-X-Mailer头部。

![1612422335_601b9cbf02a2502a5310e.png!small?1612422335361](https://image.3001.net/images/20210204/1612422335_601b9cbf02a2502a5310e.png!small?1612422335361)

我们换一个邮箱试试：

（这时候ip因为发邮件太多，被腾讯企业邮ban了，换一个gmail演示，先用一下swaks）

> root@h33l0:/tmp# proxychains swaks --to xxx@gmail.com --from
> _[admin@1634.com](mailto:admin@1634.com)_

![1612422403_601b9d035a8f50ec90ef6.png!small?1612422403769](https://image.3001.net/images/20210204/1612422403_601b9d035a8f50ec90ef6.png!small?1612422403769)

似乎简简单单有手就行？

当然不是的，因为我没有给我自己的smtp服务器配置任何安全策略，它并不检查MTA的合法性，向gmail发送的邮箱域名也是精心挑选的1634.com。

从smtp通讯过程来看，最简单有效杜绝发件人伪造的方法就是验证MTA的合法性，所谓合法的MTA就是拥有MTA对应域名的所属的邮件服务器，当然，实际应用上也是这样做的。

##  ** **1.4**** ** **SPF规则****

SPF规则，网上的文章很多了，这里快速的说明一下：

Sender Policy Framework，即发件人策略框架，用来查验MTA的合法性，使用DNS中的TXT记录来配置，查询域名对应SPF的记录方法为：

> nslookup -type=txt <domain>

![1612422514_601b9d728de175ddac707.png!small?1612422514976](https://image.3001.net/images/20210204/1612422514_601b9d728de175ddac707.png!small?1612422514976)这一条以v=spf1开头的即为spf记录，其中v=spf1是固定前缀，表示了使用spf的第一个版本，后面每一条规则以空格隔开，与iptables、ACL一致，从前向后匹配规则，命中即结束匹配，这些规则定义了那些ip是合法的MTA。

可以用以下方式来配置（仅列举常见的）：

> all : 所有ip
>
> ip4 : 一个ip地址
>
> a : 该域名对应的a记录
>
> mx : 该域名对应的mx记录
>
> include：继承一个域名的spf记录

每个规则可以有四种前缀：

> "+" Pass（通过）
>
> "-" Fail（拒绝）
>
> "~" Soft Fail（软拒绝）
>
> "?" Neutral（中立）
>
> 详细可以查看[ _openspf_ _.org_](openspf.org)。

spf配置，可以简单分为两种情况，企业自建的邮件服务：exchange、zimbra，他们的spf记录是这样的：

![1612422602_601b9dcab371a8c5286d3.png!small?1612422603073](https://image.3001.net/images/20210204/1612422602_601b9dcab371a8c5286d3.png!small?1612422603073)

比较简单，自己的a记录、mx记录、和一个ip地址。

如果是托管在云提供商上，就类似于上图中的：

> cagetest.com text = "v=spf1 include:spf.mail.qq.com ~all"

这时候，确切的想要知道是哪些主机就需要继续查询，一直查询到根节点：

> nslookup -type=txt spf.mail.qq.com
>
>
> ![1612422631_601b9de77f0e48c76101b.png!small?1612422631786](https://image.3001.net/images/20210204/1612422631_601b9de77f0e48c76101b.png!small?1612422631786)
>
> nslookup -type=txt
> spf-a.mail.qq.com![1612422653_601b9dfd8d12b685b1200.png!small?1612422653886](https://image.3001.net/images/20210204/1612422653_601b9dfd8d12b685b1200.png!small?1612422653886)

  

所以，无论如何,最终你得到的就是一些合法的ip地址，和-all，拒绝其他所有地址。

这里有一个工具[
_checkdmarc_](https://github.com/domainaware/checkdmarc)可以帮你做快速检查，dmarc是另一种spf的升级版，实测国内运营商支持的比较少，这里不探讨，

> root@h33l0:/home/p1pp0/ # checkdmarc cagetest.com
>
> {
>
> "domain": "cagetest.com",
>
> "base_domain": "cagetest.com",
>
> "dnssec": false,
>
> "ns": {
>
> "hostnames": [
>
> "f1g1ns2.dnspod.net",
>
> "f1g1ns1.dnspod.net"
>
> ],
>
> "warnings": []
>
> },
>
> "mx": {
>
> "hosts": [
>
> {
>
> "preference": 10,
>
> "hostname": "mxbiz1.qq.com",
>
> "addresses": [],
>
> "tls": false,
>
> "starttls": false
>
> },
>
> {
>
> "preference": 20,
>
> "hostname": "mxbiz2.qq.com",
>
> "addresses": [
>
> "163.177.89.176",
>
> "61.241.49.98"
>
> ],
>
> "tls": false,
>
> "starttls": false
>
> }
>
> ],
>
> "warnings": [
>
> "The DNS operation timed out after 2.0 seconds",
>
> "mxbiz1.qq.com: SSL error: [SSL: DH_KEY_TOO_SMALL] dh key too small
> (_ssl.c:1123)",
>
> "163.177.89.176 does not have any reverse DNS (PTR) records",
>
> "61.241.49.98 does not have any reverse DNS (PTR) records",
>
> "mxbiz2.qq.com: SSL error: [SSL: DH_KEY_TOO_SMALL] dh key too small
> (_ssl.c:1123)"
>
> ]
>
> },
>
> "spf": {
>
> "record": "v=spf1 include:spf.mail.qq.com ~all",
>
> "valid": true,
>
> "dns_lookups": 8,
>
> "warnings": [],
>
> "parsed": {
>
> "pass": [],
>
> "neutral": [],
>
> "softfail": [],
>
> "fail": [],
>
> "include": [
>
> {
>
> "domain": "spf.mail.qq.com",
>
> "record": "v=spf1 include:spf-a.mail.qq.com include:spf-b.mail.qq.com
> include:spf-c.mail.qq.com include:spf-d.mail.qq.com
> include:spf-e.mail.qq.com include:spf-f.mail.qq.com
> include:spf-g.mail.qq.com -all",
>
> "dns_lookups": 7,
>
> "parsed": {
>
> "pass": [],
>
> "neutral": [],
>
> "softfail": [],
>
> "fail": [],
>
> "include": [
>
> {
>
> "domain": "spf-a.mail.qq.com",
>
> "record": "v=spf1 ip4:203.205.251.0/24 ip4:103.7.29.0/24 ip4:59.36.129.0/24
> ip4:113.108.23.0/24 ip4:113.108.11.0/24 ip4:119.147.193.0/24
> ip4:119.147.194.0/24 ip4:59.78.209.0/24 ip4:113.96.223.0/24
> ip4:183.3.226.0/24 ip4:183.3.255.0/24 ip4:59.36.132.0/24 -all",
>
> "dns_lookups": 0,
>
> "parsed": {
>
> "pass": [
>
> {
>
> "value": "203.205.251.0/24",
>
> "mechanism": "ip4"
>
> },
>
> {
>
> "value": "103.7.29.0/24",
>
> "mechanism": "ip4"
>
> },
>
> {
>
> "value": "59.36.129.0/24",
>
> "mechanism": "ip4"
>
> },
>
>  
>
>
> ],
>
> "neutral": [],
>
> "softfail": [],
>
> "fail": [],
>
> "include": [],
>
> "redirect": null,
>
> "exp": null,
>
> "all": "fail"
>
> },
>
> "warnings": []
>
> },
>
>  
>
>
> },
>
> "dmarc": {
>
> "record": null,
>
> "valid": false,
>
> "location": null,
>
> "error": "The DNS operation timed out after 2.0 seconds"
>
> }
>
> }

（太长了删除了一部分）

### 由于篇幅有限， **接下来内容将会在下篇文章中展开，敬请期待。**

![](https://image.3001.net/images/20210220/1613791610_6030817acda840cf49676.jpg!small)

