![](https://image.3001.net/images/20220421/1650499385_62609f39cea59d144fdff.jpg!small)

发送者策略框架 (Sender Policy Framework, SPF) 和 DMARC 还有 DKIM
一起，在邮件验证中扮演重要的角色。它能够防止来自未经授权的发送者的邮件抵达收件箱。

本文是一个全面的 SPF 指南。我们将讨论各个 SPF 概念，工作原理，在典型场景中的具体的设置方法，等等。在阅读本文后，您将能够为您的组织实现 SPF。

#### 什么是发送者策略框架 (Sender Policy Framework, SPF)

发送者策略框架 (Sender Policy Framework, SPF)
是一个电子邮件验证机制，它使得仅有被授权的发送者可以代表域名发送邮件，并且阻止其他所有未经授权的发送者这样做。SPF
使接收服务器能够检查一封声称来自一个特定域名的邮件是否来自一个域名管理者指定的 IP 地址。

SPF 由 RFC 7208 定义，更多的信息可以参考 www.openspf.org。

#### SPF 历史

SPF 的概念在 2000 年首次被提出。接着提出的方案还有 Hadmut Danisch 的 "Reverse MX" (RMX)，以及 Gordon
Fecyk 的 "Designated Mailer Protocol" (DMP)。这些方案被提交到 IETF Anti-Spam Research
Group (ASRG)。

在 2003 年，Meng Weng Wong 融合了 RMX 和 DMP 规范，进一步形成了 SPF。

在 2004 年早期，IETF 尝试使用 SPF 和微软的 CallerID 提议作为 Sender ID
技术的基础；由于技术上和授权方面的冲突，Sender ID 现在已经销声匿迹。因此技术社区回到原来的 SPF。在 2006 年，实验性的 RFC 4408
作为 SPF 规范发布。

在 2014 年，IETF 将 SPF 规范作为 "proposed standard" 发布在 RFC 7208。

#### 为什么要 SPF

电子邮件本来并没有被设计成一个安全的通讯平台 -任何人都可以以任何域名的名义发送邮件。这让网络攻击者盗取邮件接收者的敏感信息，比如信用卡信息和密码成为可能。

SPF 被设计来解决这个特定的问题：当 SPF 在域名上面正确地设置了以后，与 SPF
兼容的邮箱服务提供商会检查进来的邮件是否来自允许代表该域名的主机。如果是这样的话，邮件被称为被 SPF
验证，并且会被投递到收件箱。否则，会对邮件执行其他检查，并且根据检查结果和 DMARC 设置，可能会被隔离或者拒收。

#### SPF 的好处

SPF 提供了验证邮件发送者的机制 - 这确保指定的白名单以外的主机无法代表域名发送邮件。这从根本上杜绝了一大类的冒名攻击。

简单地说：

  * 没有 SPF：任何主机都可以使用域名发送邮件；
  * 使用 SPF：只有白名单中指定的主机可以使用域名发送邮件。

#### SPF 不能做什么

电子邮件中有两类 From 地址：envelope From 地址和头域 From 地址。SPF 仅验证 envelope From 地址，但是并不验证头域
From 地址。DMARC 引入 "SPF identifier alignment" 的概念来解决这个问题。

要了解更多信息，请参阅：[电子邮件中的 From 地址](https://dmarcly.com/blog/zh-CN/how-to-implement-dmarc-dkim-spf-to-stop-email-spoofing-phishing-the-definitive-guide#a-tale-of-two-from-addresses)。

当邮件通过间接邮件流的时候，比如说被转发，SPF 检查会失败。因为中间主机的 IP 地址和源主机的不同，并且可能不在白名单上面，邮件可能在接收服务器上面
SPF 验证失败。幸运的是，一个新的叫 authenticated received chain (ARC) 的协议能够解决这个问题：[什么是验证接收链
(authenticated received chain, ARC)](https://dmarcly.com/blog/zh-CN/what-is-authenticated-received-chain-arc)。ARC 保留 SPF
验证结果并且将其输送到下游主机节点，这样的话，终端服务器能够访问到它。

最后，SPF 没有报告/反馈功能。这使得它难以实施和维护。

#### SPF 和 DKIM 以及 DMARC 的比较

现代邮件验证方案通常包含 DKIM，DMARC，以及 SPF。这三者一起可以为商务邮件提供完全的反冒名邮件欺诈保护，并最小化相关的风险。

DKIM 是 DomainKeys Identified Mail 的缩写。它是一种电子邮件验证机制，用来检测伪造的邮件头域和内容。DKIM
使得接收者能够检查邮件头域和内容是否在传输过程中已经被篡改。要了解更多内容，请参阅：[什么是
DKIM](https://dmarcly.com/blog/zh-CN/how-to-implement-dmarc-dkim-spf-to-stop-email-spoofing-phishing-the-definitive-guide#what-is-dkim)。

DMARC 是 Domain-based Message Authentication, Reporting & Conformance
的缩写。它是一种用来确定电子邮件是否来自声称的发送者的机制。它建立于 SPF 和 DKIM
之上，并且增加了域名对齐检查和报告功能。要了解更多内容，请参阅：[什么是 DMARC](https://dmarcly.com/blog/zh-CN/how-to-implement-dmarc-dkim-spf-to-stop-email-spoofing-phishing-the-definitive-guide#what-is-dmarc)。

如上所述，SPF, DKIM, 和 DMARC 在邮件验证中扮演不同的角色。与此同时，当协同工作的时候，它们能够提供完全的反邮件冒名保护。简单地说：SPF
验证邮件发送来源；DKIM 确保邮件头域和内容没有被篡改；DMARC 在 SPF 和 DKIM 的基础上添加额外的功能，比如 identifier
alignment。

DMARCLY 使用 SPF, DKIM 和 DMARC，用户可以先从 SPF 和 DMARC 开始，然后再扩展到完整的 SPF, DKIM, 和
DMARC 实现。

#### SPF 如何工作：SPF 解释

要让 SPF 发挥作用，域名管理者需要和邮箱服务提供商协同工作。在域名管理者这边，在 DNS 中发布一条 SPF
记录来指定发送者白名单，即哪些主机可以代表域名发送邮件；接收邮件的服务器负责执行检查：对每一封邮件，从 DNS 中获取 SPF
记录，并检查发送者是否在名单上。

考虑下面的情形：

  * 组织域名是 business.com；您需要从 support@business.com 发送邮件到雇员和顾客；
  * 邮件发送主机的 IP 地址是 192.168.0.1；
  * 某个攻击者使用位于 IP 地址为 1.2.3.4 的主机来尝试发送冒名邮件。

当邮件发送服务连接到托管目标邮箱的服务器时：

  * 目标邮箱服务器从 envelope from 地址中提取域名；在这里，域名是 business.com；
  * 该服务器检查发起连接的主机的 IP 地址是否包含在发布在 DNS 中的 business.com 的 SPF 记录中。如果是的话，SPF 检查通过，否则不通过。

举个例子，假设 SPF 记录如下：

    
    
    v=spf1 ip4:192.168.0.1 -all

这个记录指定只有来自 IP 地址 192.168.0.1 的邮件才会通过 SPF 检查，所有来自其他任何 IP 地址的邮件无法通过 SPF 检查。因此，来自
IP 地址为 1.2.3.4 的欺诈服务器的邮件将无法通过 SPF 检查。

可以认为 SPF 记录是一个合法 IP 地址的白名单，当且仅当一封邮件来自其中的一个 IP 地址时，SPF
才会让其通过。其他所有的主机都无法使用您的域名发送邮件。SPF 检查的结果会被 DMARC 用来做进一步的处理。

![](https://image.3001.net/images/20220421/1650499388_62609f3cf3b631fb736bc.png!small)

如果使用 Gmail 的话，很容易查看邮件是否通过 SPF 检查。登录到网页版的 Gmail，点击要检查的电子邮件，然后使用 "Show original"
功能来检查邮件的详情。下面是一个例子：

![](https://image.3001.net/images/20220421/1650499390_62609f3ec29792745a8bb.png!small)

在上面的例子中，邮件通过了 SPF 检查，就像在高亮的区域显示的那样。

#### 什么是 SPF 记录

SPF 记录是一个发送者策略框架记录，类型为 TXT 资源记录，它被发布在 DNS
中，在指定的域名上面。它的目的是指定一个允许代表域名发送邮件的发送者的列表。

值得注意的是，以前有一个 SPF 资源记录类型，但是已经在 2014 年被弃用。SPF 记录必须以 TXT 记录的类型发布在 DNS 中。

SPF 记录由域名管理者发布，由邮箱服务提供商执行检查。

<https://dmarcly.com/blog/how-to-set-up-sender-policy-framework-spf-the-complete-guide>

#### SPF 记录语法

每一个 SPF 记录以版本号开始，即 `v=spf1`，后面跟着一组 mechanisms，有可能还有 qualifiers 以及
modifiers。SPF 中的 mechanisms, qualifiers, 和 modifiers 能够被用来灵活地定义一个 IP 地址的列表。

#### SPF mechanisms

mechanism 是一种用来指定 IP 地址范围的办法。有 8 种 mechanisms 可用：

  * `IP4`: 如果发送者位于指定的 IPv4 地址范围，匹配；
  * `IP6`: 如果发送者位于指定的 IPv6 地址范围，匹配；
  * `A`: 如果域名有地址记录 (A 或者 AAAA) 能够解析成发送者的地址，匹配；
  * `MX`: 如果域名有 MX 记录能够解释成发送者的地址，匹配 (即邮件来自域名的接收邮件服务器之一)；
  * `PTR`: 如果发起连接的 IP 地址的域名 (PTR 记录) 和指定的域名一致，并且该域名能够解析成发起连接的 IP 地址 (forward-confirmed reverse DNS)，匹配。该 mechanism 已经被废除，不应该再使用；
  * `EXISTS`: 如果指定的域名能够解析到任意一个 IP 地址，匹配。这个 mechanism 并不常用。和 SPF 宏命令一起，这个 mechanism 提供了更加复杂的匹配，比如 DNSBL-queries；
  * `INCLUDE`: 包含另外一个域名上面的 SPF 记录。如果该域名的 SPF 记录通过，这个 mechanism 也通过。但是，如果该域名的 SPF 记录失败，处理继续。要完全使用另外一个域名的 SPF 记录，必须使用 redirect；
  * `ALL`: 总是匹配；用来作为一个缺省的结果，如 -all，如果前面的 mechanisms 没有匹配的话。

#### SPF qualifiers

qualifier 指定 mechanism 估值的结果。每一个 qualifier 都能够和上面描述的任意一个 mechanism 组合。

  * `+`代表 PASS, 即 SPF 检查通过。这个符号可以被省略；比如，+mx 和 mx 是一样的；
  * `?`代表一个中性的结果，类似于 NONE (没有 SPF 记录)；
  * `~`(波浪线) 代表 SOFTFAIL, 介于 NEUTRAL 和 FAIL 之间。通常，返回 SOFTFAIL 的邮件会被接收但是被打上标签；
  * `-`代表 FAIL, 即 SPF 检查失败。

#### SPF modifiers

有两个广泛部署的 modifiers：

  * `exp=some.example.com`指定一个在 DNS 中有 TXT 记录的域名 (由 SPF 的宏语言使用) 来获取检查失败的解释。很少使用；
  * `redirect=some.example.com`可以代替 `all`mechanism 来使用另外一个域名的 SPF 记录；
  * SPF modifiers 使得未来对 SPF 的扩展变得可能。

注意 `redirect`和 `include`工作方式不同：

  * `include`是一个 mechanism, 如果它不通过检查的话，下一个 SPF 记录中的 mechanism 将会被检查；
  * `redirect`是一个 modifier, 检查的结果完全由指定域名的 SPF 记录的估值结果决定。

#### SPF 记录例子

下面是一个典型的 SPF 记录：

    
    
    v=spf1 a mx include:_spf.example.com -all

这个 SPF 记录允许下面的 IP 地址来代表域名 business.com 发送电子邮件：

  * 如果 business.com 有一个可解析的地址记录 (A 或者 AAAA)，解析后的 IP 地址被允许 (a mechanism)；
  * 如果 business.com 有一个可解析的 MX 记录，解析后的 IP 地址被允许 (mx mechanism)；
  * 任何包含在 _spf.example.com 上面的 IP 地址都被允许 (include:_spf.example.com mechanism)； 注意如果使用第三方邮件发送服务的话，它们通常要求使用 include mechanism 将它们的 SPF 记录加入到您的 SPF 记录。比如，SendGrid 会让您添加 include:sendgrid.net 到您的 SPF 记录中，这样的话发送自 SendGrid 的邮件会通过 SPF 检查。

一个阻止域名发送任何邮件的特殊的 SPF 记录如下：

    
    
    v=spf1 -all

这个记录阻止任何 IP 地址代表域名发送邮件。

应该把上面的 SPF 记录发布到不发送邮件的域名上，包括停放域名 (parked
domains)。否则这些域名可能会收到冒名邮件攻击，最终域名声誉和邮件抵达率会降低，如果过后这些域名被用来发送邮件的话。

请记住：必须要包含所有要为组织发送邮件的 IP 地址；否则，会有部分邮件不能通过 SPF 检查。

#### 如何生成/创建 SPF 记录

可以通过两种方式生成 SPF 记录：手工生成或者使用工具，比如 DMARCLY 的 SPF 记录生成器。

如果要手工创建一个 SPF 记录，可以从 `v=spf1`开始，然后添加所有合法的发送者到记录中，最后在末尾添加 `-all`来完成整个记录。

此外，可以使用 DMARCLY 的 SPF 记录生成器来创建一条 SPF 记录。见下面的小节。

#### SPF 记录生成器/创建器

使用 [SPF 记录生成器](https://dmarcly.com/tools/spf-record-generator)，简单地输入合适的设定，像合法发送者等，然后点击 Generate SPF Record 按钮，一条 SPF
记录就产生了。这种办法不容易产生错误，因此推荐使用。

#### 多功能 DMARC/DKIM/SPF 向导

如果在实施 SPF 的同时也在实施 DKIM 和 DMARC，可以使用 DMARCLY 的多功能 DMARC/DKIM/SPF
向导。该向导提供端到端的指引，帮助实施完整的反邮件冒名保护。

了解更多：[DMARC/DKIM/SPF 向导](https://dmarcly.com/tools/spf-dkim-dmarc-wizard/)。

#### 如何在 DNS 中添加/发布 SPF 记录

一旦创建了 SPF 记录，您需要将其发布到 DNS 中，这样接收邮件的服务器才能访问到。要发布一条 SPF 记录，只需要在域名上创建一条 TXT 记录。

假定使用 GoDaddy 作为域名服务提供商。如果使用其他服务的话，界面类似。

执行下面的步骤：

  * 登录到 GoDaddy。选择要设置的域名，然后点击 DNS 按钮。

![](https://image.3001.net/images/20220421/1650499394_62609f4274ec8d4c2b39f.png!small)

  * 如果域名上面从来没有发布过 SPF 记录，点击 Records 区域下面的 Add 按钮。

![](https://image.3001.net/images/20220421/1650499396_62609f447d0fc2e02425e.png!small)

  * 否则，已经在域名上面发布过 SPF 记录，所以只需要编辑它即可。要检查是否有 SPF 记录，尝试找一个 TXT 记录，它的值以 `v=spf1`开始。
  * 在 Type 下拉框中选择 TXT。在 Host 域中输入 @。在 TXT Value 中输入 SPF 记录。然后点击 Save 按钮。

![](https://image.3001.net/images/20220421/1650499398_62609f46125e96ac0c9ae.png!small)

这样就发布了 SPF 记录。注意如果要检查这个刚发布的 SPF 记录的话，由于 DNS 传播需要时间，可能需要 1 个小时后才能查到。

#### SPF DNS 查找限制

每次当邮件抵达托管邮箱的主机，该主机都会查询 DNS 来执行 SPF 检查。有对应的防范措施来防止这种查询变成拒绝服务 (Denial of
Service, DoS) 攻击。

SPF 规范规定每次 SPF 检查执行的 DNS 查询次数不能超过 10，其中包括任何 "include" mechanism 或者 "redirect"
modifier 引起的查询。如果超过 10 次的话，SPF 返回 PermError。

`include`, `a`, `mx`, `ptr`, `exists`mechanisms 还有 `redirect`modifier
不包含在这个限制之内。`all`, `ip4`, 和 `ip6`mechanisms 并不需要 DNS 查询，因此也不受这个限制。`exp`modifier
也不受这个限制，因为在查询 DNS 来获得解释文本时，SPF 记录已经被估值完毕。

例如，看一下 `google.com`的 SPF 记录：

    
    
    v=spf1 include:_spf.google.com ~all

记录中的 `include`mechanism 消耗 1 次 DNS 查询。接下来是 `_spf.google.com`的 SPF 记录：

    
    
    v=spf1 include:_netblocks.google.com include:_netblocks2.google.com include:_netblocks3.google.com ~all

记录中的 3 个 `include`mechanisms 消耗 3 次 DNS 查询。所有下面的记录
`_netblocks.google.com``_netblocks2.google.com``_netblocks3.google.com`解析成 1
个纯 IP 地址列表。因此并不消耗 DNS 查询。

因此，`google.com`的 SPF 记录消耗的 DNS 查询次数为 4 次 (1+3)。

可以用 [SPF 记录检查器](https://dmarcly.com/tools/spf-record-checker)来验证
`google.com`上面的 SPF 记录中的 DNS 查询次数符合上面的结果。

#### 如何检查/验证/测试 SPF 记录

有些时候，需要检查 SPF 记录是否正确发布。就像创建一个 SPF 记录一样，可以手工检查或者使用 DMARCLY 的 SPF 记录检查器。

下个小节描述如何使用 DMARCLY 的 SPF 记录检查器来检查 SPF 记录。

#### SPF 记录检查器/验证器/测试器

要检查域名上面的 SPF 记录，使用 [SPF 记录检查器](https://dmarcly.com/tools/spf-record-checker)。输入域名，它就会从 DNS 中返回 SPF 记录：

  * 检查 SPF 记录的语法是否正确；
  * 确保 DNS 查询次数不超过 10 次；
  * "压平"返回的 SPF 记录，将其变成一个纯 IP 地址列表，可供逐一检查。有时候这对排查 SPF 记录故障很有帮助。

这是一个 SPF 记录检查例子：

![](https://image.3001.net/images/20220421/1650499399_62609f47f0a1b3b30735e.png!small)

如上所示，SPF 记录测试结果显示 `dmarcly.com`上面的 SPF 设置是正确的。

#### 常见问题

> 一些 DNS 服务提供商使用的 SPF 记录类型是什么？

对 SPF 资源记录类型的支持已经在 2014 年正式终止。SPF 记录必须以 **DNS TXT** 的类型发布。

> 能够在域名上面发布多条 SPF 记录吗？

不可以。如果域名上面有多条 SPF 记录，SPF 将返回 PermError。

了解更多：[可以在域名上发布多条 SPF 记录吗？](https://dmarcly.com/blog/zh-CN/can-i-have-multiple-spf-records-on-my-domain)

本文翻译自 <https://dmarcly.com/blog/how-to-set-up-sender-policy-framework-spf-the-complete-guide>，转载请保留完整内容。

