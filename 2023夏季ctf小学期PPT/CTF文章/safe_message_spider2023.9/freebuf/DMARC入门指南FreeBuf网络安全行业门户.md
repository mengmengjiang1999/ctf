![](https://image.3001.net/images/20220419/1650338288_625e29f0b22e2917e3bee.jpg!small)

#### 什么是 DMARC?

DMARC 是 “Domain-based Message Authentication, Reporting & Conformance”
的缩写，用来检查邮件是否来自声称的来源。它构建在广泛部署的 SPF 和 DKIM
协议之上，并添加了域名对齐检查和报告发送功能，来改善和监测域名的反冒名攻击保护。

这里是一个 DMARC 的示意图 [dmarc.org](https://dmarc.org/):

![](https://image.3001.net/images/20220419/1650338293_625e29f55ff37a0288ba3.jpg!small)

#### 为什么 DMARC 如此重要？

下面的说明来自 dmarc.org:

>
> 随着社交网络和电子商务的兴起，垃圾邮件发送者和钓鱼攻击者出于经济的动机会入侵用户帐户，并盗窃密码，银行帐户，信用卡，等等。冒名发送电子邮件很容易，攻击者发现冒名发送邮件能够利用用户对知名品牌的信任。简单地在邮件里面显示一个知名品牌的标志就可以获取用户信任。
>
> 邮件用户无法分辨真实的邮件和假冒的邮件，邮箱服务提供商也很难作出决定。邮件发送者对邮件验证的状态并不知晓，因为没有让他们指定接收反馈报告的机制。SPF
> 和 DKIM 的部署进展缓慢，因为缺少反馈，从而意味者没有好办法来监测进程和排查问题。
>
> DMARC 能够解决这些问题，帮助邮件发送者和接收者协作来保证邮件安全，从而保护用户和品牌不受代价高昂的滥用。

#### 什么是 DMARC 记录？

DMARC 记录是发布在 DNS 中的 TXT 资源记录，它指定邮箱服务应该如何处理 DMARC 验证失败的邮件。

下面考察一个发布在 “sender.exampledomain.com” 上面的 DMARC 记录：

    
    
    v=DMARC1;p=reject;pct=100;rua=mailto:postmaster@exampledomain.com

在这个例子里，发送者要求邮箱服务拒绝所有验证失败的邮件，并且发送聚合格式的报告到指定的地址。如果发送者正在测试电子邮件配置的话，他们可以把 “reject”
换成 “quarantine”，这样就要求邮箱服务隔离验证失败的邮件，而不是完全拒绝。DMARC 记录采用了灵活的 “标签-值” 的语法，和 DKIM
记录类似。

#### 什么是 DMARC 记录标签？

一个典型的 DMARC 记录如下所示：

    
    
    v=DMARC1; p=none; ri=3600; rua=mailto:5b06a240321f1@ag.dmarcly.com; ruf=mailto:5b06a240321f1@fo.dmarcly.com; sp=none; adkim=s; aspf=s; fo=0:1:d:s;

它包含多个标签，来指定邮箱服务应该如何发送 DMARC 报告。下面我们逐个讨论。

 **v** 是 DMARC 协议版本。缺省是 DMARC1。

 **p** 是策略。DMARC 将该策略应用到验证失败的邮件。可选值为 'none', 'quarantine', 或者 'reject'。'none'
用来接收 DMARC 报告并由此获得邮件验证状态。'quarantine' 用来隔离验证失败的邮件。'reject' 用来拒收验证失败的邮件。

 **ri** 报告发送间隔，以秒计算。它定义接收 aggregate 报告的频率。

 **rua** 指定接收 aggregate 报告的 URI 列表。注意：这个不是电邮地址列表。DMARC 要求一系列的
URI，形式是：'mailto:test@example.com'。

 **ruf** 指定接收 forensic 报告的 URI 列表。注意：这个不是电邮地址列表。DMARC 要求一系列的
URI，形式是：'mailto:test@example.com'。

 **sp** 是子域名策略。DMARC 将该策略应用到来自子域名的验证失败的邮件。域名管理者可以使用该标签来为所有子域名发布一个通配的策略。

 **adkim** 指定 DKIM 中的 '对齐模式'，可以是 'r' (放松) 或者 's' (严格)。在放松模式下，验证过的 DKIM 签名域名
(d=) 的组织域名如果和邮件的 From 域名一致，那么 DMARC 检查将会通过。在严格模式下，DKIM 签名域名必须和邮件的 From 域名严格匹配。

 **aspf** 指定 SPF 中的 '对齐模式'，可以是 'r' (放松) 或者 's' (严格)。在放松模式下，验证过的 SPF 域名 (d=)
的组织域名如果和邮件的 From 域名一致，那么 DMARC 检查将会通过。在严格模式下，SPF 域名必须和邮件的 From 域名严格匹配。

 **fo** 是 forensic 选项。可选值：'0' 如果 DKIM 和 SPF 都失败，那么发送报告；'1' 如果 DKIM 或者 SPF
失败，那么发送报告；'d' 如果 DKIM 失败，那么发送报告；'s' 如果 SPF 失败，那么发送报告。

 **rf** 指定 forensic 报告格式。

 **pct** 是百分比标签，它指定将 DMARC 策略应用到验证失败邮件的百分比。'pct = 50' 意味着 50% 的失败的邮件会执行 DMARC
策略。注意：这对 'none' 策略不起作用，仅对 'quarantine' 或者 'reject' 策略起作用。

#### 什么是 DMARC 策略？

DMARC 策略是 DMARC 记录中的 **p 标签** 。它指定邮箱服务应该如何处理验证失败的邮件。

DMARC 策略可以取值以下之一： **none** (监控模式), **quarantine** 和 **reject** 。

– **none** : DMARC 不对验证失败的邮件做任何处理。这也被称为监控模式。通过分析 DMARC
报告，可以知道邮件的发送源主机。一旦对邮件验证状态有充分的了解，就可以迁移到 quarantine。

– **quarantine** : 失败的邮件将会被隔离。

– **reject** : 失败的邮件将会被拒收。这些邮件不会出现在接收者的收件箱中。这个策略会阻止所有冒名发送的邮件。

<http://dmarcly.com/blog/getting-started-with-dmarc>

#### 发布 DMARC 记录

在发布之前，需要先创建一个 DMARC 记录。要创建一个 DMARC 记录，[登录](https://dmarcly.com/login)到 DMARCLY
控制台。

登录了以后，点击左边的 DNS 记录/发布 DMARC 记录，像这样：

![](https://image.3001.net/images/20220419/1650338296_625e29f838a34a4d31c2e.png!small)

已经创建的 DMARC 记录出现在高亮的区域。

接下来，需要把它作为 TXT 记录发布在 DNS 中，在目标域名上 (比如 yourdomain.com)。遵循以下步骤：

  * 登录到 DNS 管理后台；

  * 选择目标域名；

  * 用下面的设置创建一个 TXT 记录：
    
        Type: TXT
    Host: _dmarc
    TXT Value: (上面创建的 DMARC 记录)
    TTL: 1 hour

比如，下面是发布后的在 GoDaddy DNS 管理后台的例子：

![](https://image.3001.net/images/20220419/1650338298_625e29fa7c6d87345cd36.png!small)

其他的 DNS 服务的界面也类似。

保存更改。 现在 DMARC 记录已经发布在 yourdomain.com 上。

#### DMARC Wiki

要了解更多关于 DMARC 信息，下面是一些 DMARC 链接：

  * [DMARC - Wikipedia](https://en.wikipedia.org/wiki/DMARC)
  * [FAQ - DMARC Wiki - DMARC.org](https://dmarc.org/wiki/FAQ)
  * [Glossary - DMARC Wiki - DMARC.org](https://dmarc.org/wiki/Glossary)

也可以参阅 [DMARC RFC7489](https://tools.ietf.org/html/rfc7489)。

还有 [DMARC, DKIM, 和 SPF 实施终极指南](http://dmarcly.com/blog/zh-CN/how-to-implement-dmarc-dkim-spf-to-stop-email-spoofing-phishing-the-definitive-guide)。

本文翻译自 <http://dmarcly.com/blog/getting-started-with-dmarc>，转载请保留完整。

