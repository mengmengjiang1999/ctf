![](https://image.3001.net/images/20210315/1615791417_604f05399dce2758ad1b4.png!small)

当排查邮件送达问题时，您可能会在接收邮件服务器上看到类似下面的 SPF 错误：

SPF PermError: too many DNS lookups

SPF Permanent Error: too many DNS lookups

SPF Fail: too many DNS lookups

这些信息表明您域名上的 SPF 记录包含多于 10 次 DNS 查询，这使得该 SPF 记录违反了 [SPF
规范](http://emailstuff.org/rfc/4408#section-10.1)的 [SPF 10
次查询极限](https://dmarcly.com/blog/zh-CN/spf-permerror-too-many-dns-lookups-when-spf-record-exceeds-10-dns-lookup-limit)。

当该错误发生时，SPF 返回一个 PermError（永久性错误），该错误会使 SPF
验证无法通过。如果最终的邮件验证结果失败，该邮件将很可能不会抵达收件箱。

#### 修复 SPF PermError: too many DNS lookups 问题的步骤

遵循以下 3 个步骤来修复该问题。

##### 1\. 跳转到 DMARCLY 的 Safe SPF 功能页面

[登录](https://dmarcly.com/login)到 DMARCLY 的控制面板，然后去到 DNS Records -> Safe SPF。

##### 2\. 在域名上面设置 Safe SPF

选择 DNS 查询次数超过 10 次的 SPF 记录所在的域名。您需要在这个域名上面设置 Safe SPF 来突破 SPF 的 10 次 DNS 查询极限。

点击 "Set Up Safe SPF"。输入域名上的原来的 SPF 记录。点击 "Generate Safe SPF Record"。

您原来的 SPF 记录会被转化成 Safe SPF 记录。该 Safe SPF 记录是一个完全有效的 SPF 记录，并且包含和原来的 SPF 记录同样的
IP 地址，但是执行更少的 DNS 查询。

现在在 DNS 中往域名上面发布生成的 Safe SPF 记录。然后点击 "Save Safe SPF"。

##### 3\. 确认该 SPF PermError 已经被修复

使用[在线 SPF 记录检查器](https://dmarcly.com/tools/spf-record-checker)来检查域名，您现在会看到 DNS
查询次数位于 10 次 DNS 查询极限之内。请注意 DNS 传播需要一段时间，所以如果您没有看到新的 SPF 记录，请过 5 分钟再重试。

现在您原来的包含 10 次 DNS 查询的 SPF 记录已经变成了一个 Safe SPF 记录。这条 Safe SPF 记录包含和原来同样的 IP
地址，并且执行不多于 10 次的 DNS 查询。而且，当任何第三方服务改变的时候，该 Safe SPF 记录会被自动更新，所以它永远和原来的 SPF
记录同步。

现在您再也不用担心恼人的 SPF PermError: too many DNS lookups 问题了！

本文翻译自 <https://dmarcly.com/blog/how-to-fix-spf-permerror-too-many-dns-lookups>，已经经过作者授权。

