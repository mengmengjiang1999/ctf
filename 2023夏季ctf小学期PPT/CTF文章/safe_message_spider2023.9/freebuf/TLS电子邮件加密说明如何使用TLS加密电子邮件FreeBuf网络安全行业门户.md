电子邮件[[1]](https://zhuanlan.zhihu.com/p/573253275#ref_1)是企业首选的沟通方式，这已经不是什么秘密了——这种趋势会随着远程办公的大流行而增加。也就是说，电子邮件实际上是从邮件客户端发送到接收电子邮件的服务器或从一个服务器发送到另一个服务器的明文通信，如果没有通过安全传输层协议（TLS）等加密技术进行额外保护，则传输中的信息内容很容易受到泄露。

了解TLS如何帮助电子邮件安全通信，以及如何在Postfix开源邮件传输代理（MTA）Microsoft 365 Exchange Online 和
Google Workspace 中安全地实施 TLS，以帮助强化电子邮件免受欺骗和数据盗窃。

## TLS基础知识：什么是安全传输层(TLS)?

安全传输层（TLS）是一种加密协议，TLS为一个安全电子邮件服务器“传输”到另一个安全电子邮件服务器的信息提供端到端的加密技术，有助于保护用户隐私并防止窃听或更改内容。TLS是SSL的后续协议。它的工作方式与SSL基本相同，都使用加密技术来保护数据和信息的传输。TLS是一个互联网工程任务组(IETF)的标准协议，在两个通信的计算机应用程序之间提供身份验证、隐私和数据完整性。为了实现邮件内容的最佳安全性和隐私性，在所有处理电子邮件通信的服务器（包括内部服务器和外部服务器之间的跳点服务）之间都需要使用TLS。建议所有客户端和服务器坚持在其电子邮件通信中强制使用TLS——最好是最新版本TLS1.3。

TLS被领先的电子邮件提供商和ISPs使用，包括谷歌、微软、雅虎和康卡斯特，还用于通过HTTPS保护网络通信。

## TLS如何帮保护电子邮件通信的安全？

TLS通过加密从邮件服务器到邮件服务器的信息来保护电子邮件通信，这使黑客更难截获和读取信息。TLS协议结合使用对称加密(使用发送方和接收方都知道的密钥对数据进行加密和解密)和非对称加密(使用公钥和私钥对加密和解密数据)来保持性能和安全性之间的平衡。TLS支持使用数字证书对接收服务器进行身份验证（发送者服务器的身份验证是可选的），通过验证接收者（或发送者）的真实.身份来帮助防止电子邮件欺诈和数据泄露。

广泛使用的开源Postfix邮件传输代理(MTA)赢得了高度安全的声誉，可以被配置为支持TLS，使Postfix用户能够加密邮件并验证远程SMTP客户端或服务器。

## 如何在Microsoft 365 Exchange Online中强制设置TLS？

Microsoft 365 Exchange Online提供TLS支持，但是，它必须设置为强制执行TLS，幸运的是，在Microsoft 365
Exchange
Online中设置强制TLS既快速又简便，只需要您希望与之建立强制TLS的组织域名和该域的有效电子邮件地址，该供应商还需要配置他们的电子邮件服务器来强制执行TLS。这种相互配置可确保所有电子邮件都经过加密并通过互联网安全发送。

在Microsoft365 Exchange Online中设置强制TLS的过程分为两个步骤：创建出站TLS连接器和创建入站TLS连接器。

## 如何在Google Workspace中设置TLS合规性？

Google
Workspace支持TLS，但是，对于安全的TLS连接，发送方和接收方都必须设置TLS合规性。如果接收服务器不使用TLS，Gmail仍会传送邮件——但连接不安全。通过添加TLS合规性设置，Gmail始终使用安全连接来收发指定域和电子邮件地址。

## 总结

在电子邮件通信中使用和强制使用TLS必须被视为保护企业电子邮件和保护敏感信息的深入防御方法的重要组成部分。TLS被几乎所有领先的电子邮件提供商和ISPs使用；但是，该协议必须被正确地设置和配置，以提供最佳的安全性。

来源网站：[https://guardiandigital.com/](https://link.zhihu.com/?target=https%3A//guardiandigital.com/solutions)沃通WoTrus原创翻译整理，转载请注明来源

原文网址：[https://linuxsecurity.com/features/tls-email-encryption-explained-how-to-encrypt-email-with-tls](https://link.zhihu.com/?target=https%3A//linuxsecurity.com/features/tls-email-encryption-explained-how-to-encrypt-email-with-tls)

## 参考

  1. [^](https://zhuanlan.zhihu.com/p/573253275#ref_1_0)<https://www.wosign.com/Products/email-certificate.htm>

