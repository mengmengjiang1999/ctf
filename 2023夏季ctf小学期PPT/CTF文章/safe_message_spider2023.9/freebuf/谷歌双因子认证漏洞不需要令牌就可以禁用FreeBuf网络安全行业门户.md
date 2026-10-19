以下文章转自InfoQ，作者：Alex Blewitt，译者：无名

若干天前，Amos（@fasterthanlime）遭遇了黑客的[密码攻击](https://link.zhihu.com/?target=https%3A//fasterthanli.me/articles/beware-the-google-password-manager)，被偷了几百欧元。攻击者之所以可以得逞，是因为他可以关闭 password.google.com
的双因子身份验证，无需通过双因子身份验证机制来确认身份，导致双因子身份验证失去了意义。此外，随后的调查显示，存储在 password.google.com
中的密码很容易被提取，说明该服务在安全性方面存在很大的问题。InfoQ 已经联系了谷歌的安全工程师，他们做出了回应，在得到进一步信息后将更新本文。

这个漏洞的入口点是一个类似 VNC 的远程会话，这让攻击者能够访问当时正在被使用的 macOS 窗口系统。该服务使用的是
NoMachine，在没有认证的情况下直接将 4000 端口暴露了出来。正如 Amos 指出的，这是个错误。

然而，更大的问题出现了，因为 Amos 使用 macOS 的 Safari 登录账号，Safari“帮忙”记住了密码，并进行自动填充，这也让黑客随后得以获取
Amos 的详细信息。

由于 Amos 最近在那台机器上登录过，谷歌在机器上缓存了一个最近的会话令牌 (大概是用来配合 2FA)。攻击者在一段时间后通过 Safari
自动填充功能重用缓存的密码，刷新会话令牌，并使用它来禁用
2FA。这显然是有意这么设计的，也就是说，设计者默认如果你登录了一台电脑，并且知道密码，那么此刻你肯定就是电脑的主人。如果你最近登录过，并进行过会话，你只需要一个因子——密码——来刷新会话令牌，然后就可以开始后续的操作。

 **你不需要 2FA 令牌就可以禁用谷歌 2FA。**

这似乎是一个很基本的安全问题，但很显然，为了方便用户，避免他们要经常输入 2FA
令牌，最好是先登录机器（只要你知道密码），然后就可以修改安全级别。换句话说，它就是 2FA。如果登录了，那就是 1FA
了。这种观点的理由是：你登录自己的机器，那它一定是安全的，不是吗？

> @mrisher 对 @fasterthanlime
> 说：或许是术语上的不同？除了密码之外，不是还有指纹解锁和面部解锁吗？我承认屏幕锁存在一定的差别——比如耸肩膀、闭眼睛等——但这仍然是第二个验证因子，不是吗？  
>  
> @mrisher 对 @fasterthanlime 说：在我们的模型中，设备锁是密码之外的第二个验证因子。你不这么认为吗？

是的，我不这么认为。2FA 的意义在于它应该是第二个因子身份验证。如果你可以只用一个密码来修改安全级别，那它就是
1FA。这是谷歌安全工程师提供的[建议](https://link.zhihu.com/?target=https%3A//twitter.com/alblue/status/1279091457178177536)，而这让人更加感到担忧。

此外，一旦攻击者禁用了2FA，他们就能够远程攻击会话，并使用[http://passwords.google.com](https://link.zhihu.com/?target=http%3A//passwords.google.com)提取Chrome
之前自动保存的密码。Amos 告诉InfoQ，他是一名1Password 用户，被Chrome
截获的密码有些过时了，但有一些仍然有效，攻击者用他的账号订购了一些硬件，还有其他一些账单需要Amos 支付。

事实上，直到有个使用了2FA 的服务在午夜给Amos 发送了通知，他才注意到事情有些不对劲。

Amos
调查得出的另一个结果是，[http://passwords.google.com](https://link.zhihu.com/?target=http%3A//passwords.google.com)似乎使用谷歌登录密码来加密其他密码。任何知道你的密码的人——比如，Safari
自动为你填充密码——都可以解开被加密的密码。这与苹果的钥匙串管理器有点类似，只要你知道钥匙串的密码，就可以解开钥匙串里的内容。Chrome
通过云端服务来同步密码，任何 Chrome
实例都可以访问并解开密码。谷歌的[密码检查服务](https://link.zhihu.com/?target=https%3A//passwords.google.com/checkup/)也使用了这些密码，它可以使用你的账号密码来解密账号中的其他密码，以确定它们是否已被黑客攻击或者是否太过简单。攻击者可以通过控制计算机会话并使用在线密码管理器轻松获取密码。用户可以使用“choose
as passphrase”加密密码来禁用密码检查功能，阻止谷歌在线解开你的密码。

这里有一些结论：

> 如果你用 Chrome 的记住密码功能，并且它用你的默认账号密码加密其他密码，那么
> [http://passwords.google.com](https://link.zhihu.com/?target=http%3A//passwords.google.com)就有可能是一个安全漏洞。最好使用真正的密码管理器。如果你没有使用真正的密码管理器，并继续在
> Chrome 中使用
> [http://passwords.google.com](https://link.zhihu.com/?target=http%3A//passwords.google.com)，至少要从当前账号中选择一个不一样的密码。
>
> 如果你不确定是否有人在使用你的谷歌帐号，可以看一下这个页面[https://g.co/securityCheckup
> ](https://link.zhihu.com/?target=https%3A//g.co/securityCheckup)，看看最近有哪些设备在哪些地方使用了你的帐号，你可以撤销它们。
>
> 2FA 的安全性并没有问题，但为了方便而临时禁用它则可能是个问题。
>
> 谷歌还提供了一个高级保护程序，虽然无法阻止这类攻击，但读者可能会感兴趣：  
> [https://landing.google.com/advancedprotection/
> ](https://link.zhihu.com/?target=https%3A//landing.google.com/advancedprotection/)。

Amos
在“[小心谷歌密码管理器](https://link.zhihu.com/?target=https%3A//fasterthanli.me/articles/beware-the-google-password-manager)”这篇文章中详细记录了此次事件。

你对这种情况怎么看？这是为了方便消费者和为用户着想，还是一个需要修复的安全漏洞？

本文转自InfoQ，未经许可不得二次转载。

原文链接：[https://www.infoq.cn/article/gUfTfcxhMpoL9cuTA7ND?utm_source=related_read&utm_medium=article](https://link.zhihu.com/?target=https%3A//www.infoq.cn/article/gUfTfcxhMpoL9cuTA7ND%3Futm_source%3Drelated_read%26utm_medium%3Darticle)

