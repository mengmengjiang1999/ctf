" **SPF PermError: too many DNS lookups** " 是一个在很多 SPF (Sender Policy
Framework，发送者策略框架) 实现中常见的错误。当超过这个 10 次 DNS 查询的极限以后，SPF PermError，即 SPF
永久性错误，将被返回。SPF PermError 会降低邮件送达率。

本文介绍什么是 SPF 的 DNS 查找极限，当 SPF 记录越过这个极限的后果，以及如何使用 DMARCLY 的 [Safe
SPF](https://dmarcly.com/safe-spf)功能来解决这个问题。

#### SPF PermError: too many DNS lookups

当您在域名上设置 SPF 的时候，您可能会得到某些类似于 "SPF PermError: too many DNS lookups"
的错误。这个错误可能发生在邮件服务器上，也有可能在线上 [SPF 记录检查器](https://dmarcly.com/tools/spf-record-checker)中。

#### DMARC 如何解释 "SPF PermError: too many DNS lookups"？

当 SPF 检查返回 "SPF PermError: too many DNS lookups" 的时候，DMARC 认为这个结果为 fail，因为
DMARC 把所有的永久错误 (permanent error) 解释为 fail。

#### SPF DNS 查找极限是什么？

根据官方的 RFC 规范文档 [RFC7208](https://tools.ietf.org/html/rfc7208)：

> SPF 实现必须把每次 SPF 检查的执行 DNS 查询的 mechanisms 和 modifiers 限制在 10 次以内，其中包括所有
> "include" mechanism 或者 "redirect" modifier 所带来的 DNS 查询。如果检查中该数目超过 10 次，SPF
> 必须返回 PermError 结果。执行 DNS 查询的 mechanisms 有 "include"，"a"，"mx"，"ptr"，和
> "exists"，modifier 有 "redirect"。"all"，"ip4"，以及 "ip6" mechanisms 并不执行 DNS
> 查询，所以对该数目没有影响。

换句话说，SPF 规范规定执行 DNS 查找的 mechanisms 和 modifiers 一定不能超过 10，否则返回 "SPF PermError:
too many DNS lookups"。

该限定是在接收邮件的服务器上作出的。以下是一些流行的实现该极限的 SPF 软件包：

  * [libspf2](http://www.libspf2.org/)
  * [Mail::SPF](http://search.cpan.org/dist/Mail-SPF/)
  * [Mail::SPF::Query](http://search.cpan.org/dist/Mail-SPF-Query/)
  * [pyspf](https://pypi.python.org/pypi/pyspf)

#### 为什么要做 SPF DNS 查询限制？

为什么要做这样的限制？实际上，这个限制是用来缓解拒绝服务攻击（DoS）的。考虑以下情形：

  * 一个恶意的用户在域名 `malicious.com`上创建了 SPF 记录；该 SPF 记录指向另外一个域名 `victim.com`；
  * 然后该用户从 `malicious.com`发送大量的邮件到不同的邮件服务器；
  * 当接收到这样的邮件后，邮件服务器向 DNS 查询 `victim.com`；
  * 由于涉及大量的邮件服务器，这类的 DNS 查询流量被放大了；这就形成了针对 `victim.com`的 DoS 攻击；
  * 此外，攻击的真正的来源是未知的。

正如您所见，如果不是小心防范的话，攻击者能够利用一个看起来完全无害的邮件验证机制发起攻击！虽然后果很严重，但是解决的办法却很简单：把每次 SPF 检查的执行
DNS 查询的 mechanisms 和 modifiers 限制在 10 次以内，就能够大幅地缓解攻击力度；因为放大系数顶多是 10，而不是无上限。

#### 我的 SPF 记录超过这个 SPF DNS 查找极限了吗？

您可以使用我们的 [SPF 记录检查工具](https://dmarcly.com/tools/spf-record-checker)来检查您的 SPF
记录的 DNS 查找数目。除了基本的 SPF 设置信息之外，它还显示该 SPF 记录的 DNS 查询次数。下面是对
`microsoft.com`的查找结果，显示该域名的 SPF 记录的 DNS 查询次数为 10：

![](https://image.3001.net/images/20210218/1613643326_602e3e3e8e69a15e97d30.png!small)

建议您对您的域名做一个类似的检查，看看该数目是否在合适的范围内。

#### 当 SPF 记录超出 DNS 查询次数极限时，会发生什么？

当邮件接收服务器发现发送者域名上的 SPF 记录包含多于 10 次 DNS 查询时，返回 "SPF PermError: too many DNS
lookups" 错误。如上所述，SPF PermError 被 DMARC 视为 fail，因此该邮件有可能不会抵达收件箱。

因此，您务必要把您 SPF 记录中的 DNS 查询次数保持在 10 以内。

但是我的 SPF 记录中包含很多第三方服务！

现在几乎所有的公司都把基础服务外包给第三方服务提供商，像邮件投递，市场营销，还有其他。每当加入一个 `include`来把服务添加到您的 SPF
记录中，DNS 查询次数便加 1。如果这些服务进一步包含其他服务的话，您的 SPF 记录很快就会达到/超过该极限。

很多邮件服务提供商像 Gmail 会把未验证的邮件归类为垃圾邮件，然而微软 Office 365 采取更为激进的措施：如果邮件域名未能通过 SPF
验证，域名将被封锁。

> 反垃圾邮件策略允许管理员"白名单"域名。我们正在改变我们的策略以使得域名在未通过验证时不被加入到白名单中。  
>  
> — Microsoft Office 365, April 2020

了解更多关于该变动的[信息](https://www.microsoft.com/en-us/microsoft-365/roadmap?filters=&searchterms=62398)。

#### SPF 记录压平

这个问题有一个简单的解决方案。通过"压平"一个 SPF 记录，您可以减少 DNS 查询的数目至 10 以内。

SPF 记录压平工作原理是：对每一个调用 DNS 查询的 mechanism/modifier，查询 DNS 以获得它的 IP 地址，然后用这些 IP
地址来代替原来的 mechanism/modifier。每当一个 mechanism 或者 modifier 被取代时，总的 DNS 查询数目就会减 1。

借助 SPF 记录压平技术，您可以把一个非常复杂的，调用超过 10 次 DNS 查询的 SPF 记录变成一个扁平的 IP 地址列表，使您的 SPF
记录处于"安全区域"。

我们看一下一个压平的 SPF 记录是什么样的。下面是把 `microsoft.com`上面的 SPF 记录压平后得到的 IP 地址：

![](https://image.3001.net/images/20210218/1613643336_602e3e488a4425816b5ef.png!small)

正如上面显示的，这个压平后的 SPF 记录包含和原来 SPF 记录中同样的 IP 地址，但是它并没有包含调用 DNS 查询的
mechanism/modifier！

问题解决了吗？然而并没有。

如果这些 `include`mechanisms 下面的 IP 地址发生变化会怎么样？这意味着压平后的 SPF 记录包含的 IP
地址和原来不再完全相同，这样的话就会导致不正确的 SPF 验证结果。

当然，您可以手动再次压平这个 SPF 记录，然后在 DNS 中更新它。毋庸赘言，这个过程非常乏味，而且容易出错，更不用说您需要一直检测该 SPF 记录。

幸运的是，DMARCLY 有一个功能叫 [Safe SPF](https://dmarcly.com/safe-spf)，该功能可以完美地解决这个问题。

#### Safe SPF 作用大

Safe SPF 有一石两鸟的效果：能够永远把您的 SPF 记录的 DNS 查询次数保持在 10 以下，而且无需持续手动压平 SPF 记录并在 DNS
中更新！

遵循以下步骤来在您的域名上设置 Safe SPF：

  1.  **生成 Safe SPF 记录**

在 DMARCLY 控制面板->DNS 记录->Safe SPF 中，选择您需要在其上设置 Safe SPF 的域名，然后点击 Generate Safe
SPF Record 按钮，如下所示：

![](https://image.3001.net/images/20210218/1613643345_602e3e515395d61be9183.png!small)

  2.  **发布该 Safe SPF 记录**

现在 Safe SPF 记录已经生成，您需要把它发布到 DNS 中，就像发布普通的 SPF 记录一样。请记住：Safe SPF 记录就是 SPF 记录。

了解[如何发布 SPF 记录](https://dmarcly.com/blog/how-to-implement-dmarc-dkim-spf-to-stop-email-spoofing-phishing-the-definitive-guide#publishing-an-spf-record)。

  3.  **确认 Safe SPF 记录**

接下来您需要确认该 Safe SPF 记录已正确发布并且对所有人可见。现在点击 Verify Safe SPF 按钮：

![](https://image.3001.net/images/20210218/1613643351_602e3e5746c1de3656a6d.png!small)

  4.  **保存 Safe SPF**

最后，您需要保存 Safe SPF 以使得您的 SPF 记录保持一直更新：

![](https://image.3001.net/images/20210218/1613643356_602e3e5c95e63976a913b.png!small)

就像这样：

![](https://image.3001.net/images/20210218/1613643366_602e3e6625c40a43222a3.png!small)

如上所示，Safe SPF 已经在指定的域名上面激活。

一旦 Safe SPF 在域名上激活：

  * 该 Safe SPF 记录包含和原来的 SPF 记录同样的 IP 地址；
  * 该 Safe SPF 记录包含的 DNS 查询不多于 10；
  * 当下层的 IP 地址发生变动时，该 Safe SPF 记录永远保持同步；
  * 您不需要做任何维护工作。

#### 如何更新一个现有的 Safe SPF 记录（方法 1）

在您生成并发布一个 Safe SPF 记录后，您可能想要更新原来的 SPF 记录。

比如，您想要：

  1. 添加一个新的 mechanism (include, ip4, mx, a, etc.) 到原来的 SPF 记录；
  2. 更新原来的 SPF 记录中的一个 mechanism；
  3. 移除原来的 SPF 记录中的一个 mechanism。

您可以使用上个小节中的 Safe SPF 过程来完成这个任务。值得注意的是，您需要先更新您的原来的 SPF 记录，然后再用 Safe SPF 把它压平。

下面来看一个实际的例子。

假定您的域名是：`yourdomain.com`，并且域名原来的 SPF 记录是：

    
    
    v=spf1 mx include:someservice.com -all

您已经在过去创建了一个 Safe SPF 记录：

    
    
    v=spf1 include:_u.yourdomain.com._spf.dmarcly.com -all

您打算集成一个新的邮件服务叫 anotherservice。现在您需要把它包括到您的 SPF 记录中，这样发送自这个新服务的主机的邮件可以通过 SPF
验证。

假定 anotherservice 的 SPF 记录是：

    
    
    include:anotherservice.com

您需要更新您的原有的 SPF 记录来包含这个服务，就像这样：

    
    
    v=spf1 mx include:someservice.com include:anotherservice.com -all

接下来，您需要用 Safe SPF 来压平更新后的原来的 SPF 记录：

    
    
    v=spf1 mx include:someservice.com include:anotherservice.com -all

准确地说，在 Safe SPF 的 Original SPF Record 框中输入上面的值，然后完成余下的步骤。

一旦完成后，您的 `yourdomain.com`上面的新的 Safe SPF 记录包含所有来自 include:anotherservice.com 的
IP 地址，还有所有现有的 IP 地址。并且如果 include:anotherservice.com 的 IP 地址有任何变动的话，将会自动同步到您的
Safe SPF 记录中。

这个方法适用于所有的情形，包括添加，代替，和移除。

例如，如果您想要把 SPF 记录中的 someservice.com 代替成 anotherservice.com，只需要把它更新为：

    
    
    v=spf1 mx include:anotherservice.com -all

然后用 Safe SPF 压平它。

另外一个例子是您想要把 mx mechanism 从 SPF 记录中移除，只需要把它更新为：

    
    
    v=spf1 include:someservice.com -all

然后用 Safe SPF 压平它。

#### 如何更新一个现有的 Safe SPF 记录（方法 2）

另一个更新现有的 Safe SPF 记录的方法是把新的 mechanism 直接添加到已经发布的 Safe SPF 记录中。

值得注意的是，这个方法仅适用于添加额外的 mechanism；它并不适用于更换或者移除现有的 mechanism。如果您想要更换或者移除现有的
mechanism，请用上述的方法 1。

假定您已经发布了一个 Safe SPF 记录：

    
    
    v=spf1 include:_u.yourdomain.com._spf.dmarcly.com -all

这个记录包含原来 SPF 记录中的所有 IP 地址。

然后您需要添加一个新的服务 include:newservice.com，您可以直接把域名上的 SPF 记录更新为：

    
    
    v=spf1 include:_u.yourdomain.com._spf.dmarcly.com include:newservice.com -all

现在您域名上的 SPF 记录包含所有原来的 SPF 记录中的 IP 地址，还有 newservice.com 中的 IP 地址。换句话说，发送自
newservice 的主机的邮件将会通过 SPF 验证。

#### 部分 Safe SPF

如果处于某个原因，您想要压平 SPF 记录的一部分，其他保持不变，您可以使用部分 Safe SPF。

一个具体的原因是，某些邮件服务像 HelpScout 要求它的 SPF 记录必须显式地指定。

比如，要用 HelpScout 帮您发送邮件，您需要在您的 SPF 记录中显式地指定：

    
    
    include:helpscoutemail.com

使用部分 Safe SPF 可以完美解决这个问题。在这个特定的例子中，您只需要压平原来 SPF 记录中 include:helpscoutemail.com
以外的部分，然后在 Safe SPF 记录生成以后再把它加回来。

这里有一个例子。您的原来的 SPF 记录是这样的：

    
    
    v=spf1 include:service1.com include:service2.com include:explicitservice.com -all

您只需要压平 service1.com 和 service2.com，但不需要压平 explicitservice.com。部分 Safe SPF
可以完成这个任务。

您需要用 Safe SPF 压平下面的 SPF 记录：

    
    
    v=spf1 include:service1.com include:service2.com -all

也就是说，从记录中除去 explicitservice.com，只需保留 service1.com 和 service2.com。

现在您已经生成并且发布了 Safe SPF 记录：

    
    
    v=spf1 include:_u.yourdomain.com._spf.dmarcly.com -all

这个记录包含了所有来自 service1.com 和 service2.com 的 IP 地址。我们现在需要把 explicitservice.com
加回去，使得记录变成：

    
    
    v=spf1 include:_u.yourdomain.com._spf.dmarcly.com include:explicitservice.com -all

一旦上面的 SPF 记录发布在域名上面，它包含了来自 3 个服务的所有的 IP 地址。而且，explicitservice.com 现在在 SPF
记录中是显式指定的。

本文翻译自 <https://dmarcly.com/blog/spf-permerror-too-many-dns-lookups-when-spf-record-exceeds-10-dns-lookup-limit>，已经过作者同意。

