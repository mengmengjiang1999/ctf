![](https://image.3001.net/images/20220420/1650447301_625fd3c5402cef704683b.jpg!small)

DMARC 是 **Domain-based Message Authentication, Reporting &
Conformance**的缩写，是一种电子邮件验证协议，用来检查邮件是否发送自声称的来源。DMARC 基于另外两种电子邮件验证协议 SPF 和
DKIM。除了电子邮件验证之外，它还增加了报告功能，使得域名管理者可以检查域名上面的邮件验证数据。

#### DMARC 的目的是什么？

DMARC 的主要目的是阻止电子邮件冒名发送和钓鱼攻击。电子邮件钓鱼近年来成了一个主要的安全问题。有研究表明，超过 90%
的网络攻击从钓鱼邮件开始，并且接近 50%
的网络攻击瞄准小型企业。一旦企业被攻击得手，就会导致种种的风险：品牌声誉受损，知识产权被盗窃，直接的财务损失，等等。

DMARC 是一道防御电子邮件冒名发送和钓鱼攻击的强大防线。如果正确地实施了 `p=reject`模式，DMARC
可以防止验证失败的邮件投递到目标域名，同时允许所有验证成功的邮件通过。

#### DMARC 如何工作？

在一个典型的 DMARC 实现中，需要两方面的协作：域名管理者发布 DMARC 记录，同时接收邮件的服务器执行 DMARC 策略并且发送报告。

在域名管理者这边，需要在 DNS 中发布一条正确配置的 DMARC 记录到域名上，配置主要指定 DMARC 策略和接收报告的电邮地址。DMARC 策略有 3
个可选值，来指定接收邮件的服务器应该如何处理验证失败的邮件：none (监控), quarantine, 和 reject。

在接收邮件的服务器这边，当邮件到来的时候，服务器调用 DMARC 模块来检查该邮件，包括连接主机的 IP 地址，envelope from
地址，header from 地址，以及在 DKIM 签名中的 `d=`标签(如果有的话)。检查返回 DMARC
验证结果，可能值是通过或者失败。如果结果失败的话，服务器会根据 DMARC 策略来相应地处理邮件。下面是 DMARC 如何处理验证失败的邮件：

  *  **none** (监控): 监控模式，不对验证失败的邮件做任何处理。这主要用来请求 DMARC 报告，这样域名管理者清楚了解系统中的邮件流；
  *  **quarantine** : 隔离模式，把验证失败的邮件归类为垃圾邮件。这个模式比监控模式更加严格，因为验证失败的邮件被从收件箱移除了；
  *  **reject** : 拒绝模式，完全拒收验证失败的邮件。在拒绝模式下，验证失败的邮件会被拒收，因此邮件不会被投递到用户的邮箱，包括垃圾邮件箱。结果是用户不会看到收验证失败的邮件。

<https://dmarcly.com/blog/what-is-dmarc-domain-based-message-authentication-reporting-and-conformance>

#### DMARC 在 SPF 和 DKIM 的基础上提供了别的什么？

DMARC 通过对 SPF 和 DKIM 验证结果进行估值来返回结果。DMARC 验证结果为通过，如果以下之一为真：

  * SPF 验证结果为通过，并且有 SPF identifier alignment；
  * DKIM 验证结果为通过，并且有 DKIM identifier alignment。

值得一提的是上面的 "identifier alignment" 的概念：DMARC 引入 identifier alignment
的概念来确保终端用户所看到的邮件发送者的确是被验证过的。SPF 本身并不验证 header from 地址，DKIM 也不会。

此外，SPF 和 DKIM 也没有报告发送功能，因此，实施者很难了解验证通过和验证失败的邮件的百分比。报告功能的缺失在过去阻碍了 SPF 和 DKIM
的实施。

DMARC 实现了 aggregate 报告和 forensic 报告的发送功能。Aggregate 报告包含邮件验证结果的聚合数据，并且会被定期发送到
DMARC 记录中的 `rua`标签所指定的邮箱当中。Forensic (failure) 报告在邮件验证失败之后几乎被马上发送到 DMARC 记录中的
`ruf`标签所指定的邮箱当中。请注意，只有少数邮箱服务提供商支持 forensic 报告，而所有主流的邮箱服务提供商都支持 aggregate 报告。

#### DMARC 效果如何？

简单地说，非常有效。当正确地实施了 reject 模式之后，DMARC 能够阻止冒名发送的电子邮件，前提是 SPF 和 DKIM 能够正常工作的话。

#### 每一个公司都应该实施 DMARC 吗？

大部分公司现在还没有及时地实施 DMARC。这些公司可能实施了 SPF 或者 DKIM，但是还没有实施
DMARC。这就给电子邮件冒名发送和邮件钓鱼留下可乘之机，因为 SPF 和 DKIM 都没有 identifier alignment。

如果您的公司还没有实施 DMARC，建议尽快实施。实施 DMARC 并非难事。可以简单地从监控模式开始，创建一条 DMARC 记录，并将其发布在 DNS
中。然后可以查看 aggregate 报告来了解域名上的邮件验证数据是否正常。

一旦进展顺利，可以进展到 quarantine 隔离模式，一直到最终的 reject 拒绝模式来完全保护邮件系统。

保护您的域名。不要让攻击者用来冒名发送邮件！

要开始实施 DMARC，可以阅读我们的 DMARC 指南：[如何实施 DMARC/DKIM/SPF
来阻止邮件冒名发送和钓鱼攻击：终极指南](https://dmarcly.com/blog/zh-CN/how-to-implement-dmarc-dkim-spf-to-stop-email-spoofing-phishing-the-definitive-guide)。

这里有一些 DMARC 部署工具，它们会对顺利实施 DMARC 非常有帮助：[DMARC/DKIM/SPF
部署工具](https://dmarcly.com/tools)。

要最快看到实施的效果，尝试用这个端到端的 [SPF/DKIM/DMARC 向导](https://dmarcly.com/tools/spf-dkim-dmarc-wizard/)。

本文翻译自 <https://dmarcly.com/blog/what-is-dmarc-domain-based-message-authentication-reporting-and-conformance>，转载请保留完整内容。

