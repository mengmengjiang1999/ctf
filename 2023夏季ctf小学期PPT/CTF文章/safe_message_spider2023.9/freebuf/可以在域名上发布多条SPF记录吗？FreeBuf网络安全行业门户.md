![](https://image.3001.net/images/20210228/1614489637_603b2825439f78ac595a9.png!small)

你可以在域名上发布多条 SPF 记录吗？答案是否定的：一个域名 **一定不能** 有多条 SPF 记录，否则 SPF
会失败并返回永久错误（PermError）。

SPF 记录是位于 DNS 中的 TXT 记录，准确地以 "v=spf1" 开始，后面跟一系列的 mechanisms 和 modifiers。

SPF 检查先获取域名上面的所有以 "v=spf1" 开始的 TXT 记录：

> 如果没有找到记录，返回
>
> `None`
>
> ；
>
> 如果找到多条记录，返回
>
> `PermError`
>
> 。

比如，如果您有 2 个 TXT 记录在 yourdomain.com 上面：

Record Type| Name| Value| TTL  
---|---|---|---  
TXT| yourdomain.com| v=spf1 include:_spf.google.com -all| Default  
TXT| yourdomain.com| v=spf1 include:servers.mcsv.net -all| Default  
  
所有代表 yourdomain.com 发出的邮件将不会通过 SPF 验证，并且返回 PermError。

要改正这个问题，您需要把所有要添加的 mechanisms 和 modifiers 放在 1 个 SPF 记录中，如下所示：

Record Type| Name| Value| TTL  
---|---|---|---  
TXT| yourdomain.com| v=spf1 include:_spf.google.com include:servers.mcsv.net
-all| Default  
  
要使 SPF 验证通过，必须满足以下所有的条件：

> 域名上有且仅有 1 个 SPF 记录；
>
> 该记录的语法是正确的；
>
> [DNS 查询不能超过 10](https://dmarcly.com/blog/zh-CN/spf-permerror-too-many-dns-> lookups-when-spf-record-exceeds-10-dns-lookup-limit)。否则，用 [Safe
> SPF](https://dmarcly.com/safe-spf)来修复它。

使用 [Safe SPF](https://dmarcly.com/safe-spf)来修复 [SPF PermError: Too Many DNS
Lookups](https://dmarcly.com/blog/zh-CN/spf-permerror-too-many-dns-lookups-when-spf-record-exceeds-10-dns-lookup-limit)问题。

监测 SPF 记录

既然 SPF 设置的有效性对 SPF 验证成功如此重要，当 SPF 被错误设置的时候，您也许想要获得警报，这样可以尽快修正错误。

DMARCLY's 域名监测功能允许您做到这些。要监测您的域名的话：

> [登录](https://dmarcly.com/login)到控制面板；
>
> 去 DNS Records => Domains，添加域名；
>
> 去 Reporting and Alerts => DNS Alerts，用您的邮件地址创建一个接收人。

从此以后，如果在域名上面找到多条 SPF 记录的话，您将会收到类似下面的警报：

![](https://image.3001.net/images/20210228/1614489656_603b2838dfd0e7ea31084.png!small)

相关问题：[可以在域名上发布多条 DMARC 记录吗？](https://dmarcly.com/blog/zh-CN/can-i-have-multiple-dmarc-records-on-my-domain)

本文翻译自 <https://dmarcly.com/blog/can-i-have-multiple-spf-records-on-my-domain>，已经经过作者授权。

