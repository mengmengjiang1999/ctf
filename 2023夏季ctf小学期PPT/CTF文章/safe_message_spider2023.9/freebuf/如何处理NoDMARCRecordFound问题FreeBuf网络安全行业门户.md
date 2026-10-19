当您使用各种在线工具检查域的 DMARC 记录时，您可能会遇到以下错误之一：

> "No DMARC record found"
>
> "DMARC record not found"
>
> "Missing DMARC record"
>
> "Unable to find DMARC record"
>
> "No DMARC record published"
>
> "Hostname returned a missing or invalid DMARC record"
>
> "DMARC policy not enabled"

任何这些消息或类似信息都意味着一件事：DMARC 检查显示您的域名不受保护并且受到欺骗攻击。
任何欺骗攻击者都可以使用您的域发送恶意电子邮件，这可能会在您登陆客户邮箱后对您的品牌造成损害。

要解决此问题，您需要开始为您的域实施 DMARC，这是电子邮件身份验证行业标准。

## 如何处理 No DMARC Record Found 问题

解决此问题很容易：您需要使用适当的设置生成 DMARC 记录，将其发布到 DNS 中，然后进行验证。

以下是修复 “未找到 DMARC 记录” 的 3 个步骤。

###  **1\. 生成 DMARC 记录**

在我们发布它之前，使用我们的[免费 DMARC 记录生成器](https://dmarcly.com/tools/dmarc-generator)来生成
DMARC 记录。

这里要注意 2 件事。 首先，如果您是第一次实施 DMARC，则很可能需要将策略设置为 none（p = none），这会将 DMARC 置于监控模式。
这不会以任何方式影响您的电子邮件流，同时允许您接收 DMARC 报告，以便深入了解您的电子邮件身份验证状态。 其次，请求 DMARC 通过将 rua
标记指向该邮箱，将聚合报告发送到您有权访问的邮箱。 我建议您使用 DMARCLY 的仪表板生成这样的 DMARC 记录，并让它为您设置邮箱。

###  **2\. 发布 DMARC 记录**

DMARC 的工作原理是在 DNS 中发布记录，以便接收电子邮件服务器。 生成记录后，您需要登录域的 DNS 提供商的仪表板以添加记录。 例如，如果您的域
mydomain.com 托管在 GoDaddy 上，则需要登录 GoDaddy。

以下是有关使用各种 DNS 服务添加 DMARC 记录的教程的一些链接：

  * [How to add DMARC record in GoDaddy](https://dmarcly.com/blog/how-to-add-dmarc-record-in-godaddy-godaddy-dmarc-setup-guide)
  * [How to add DMARC record in Cloudflare](https://dmarcly.com/blog/how-to-add-dmarc-record-in-cloudflare-cloudflare-dmarc-setup-guide)
  * [How to add DMARC record in Namecheap](https://dmarcly.com/blog/how-to-add-dmarc-record-in-namecheap-namecheap-dmarc-setup-guide)
  * [How to add DMARC record in cPanel](https://dmarcly.com/blog/how-to-add-dmarc-record-in-cpanel-cpanel-dmarc-setup-guide)

###  **3\. 检查 DMARC 记录**

发布记录后，您可以使用我们的[免费在线 DMARC 检查器](https://dmarcly.com/tools/dmarc-checker)来验证它确实在
DNS 中并且可供所有人访问。

本文翻译自 <https://dmarcly.com/blog/how-to-fix-no-dmarc-record-found>。已经得到原文作者授权。

