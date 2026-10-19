![](https://image.3001.net/images/20211223/1640238387_61c40d33aaf35357ce9cf.jpg!small)12月22日bleepingcomputer消息，自今年3月以来，就有报道称
Microsoft Teams 链接预览功能存在一些安全漏洞，但微软却表示不会修复或者推迟这些漏洞的修补计划。

这些安全漏洞由德国 IT 安全咨询公司 Positive Security 联合创始人 Fabian Bräunlein 发现，分别是服务器端请求伪造
(SSRF)漏洞、URL 预览欺骗漏洞、IP 地址泄漏 (Android) 漏洞和被称为死亡消息 (Android) 的拒绝服务 (DoS) 漏洞。

Bräunlein 向 Microsoft 安全响应中心 (MSRC) 报告了四个漏洞，该中心负责调查有关 Microsoft 产品及服务的漏洞报告。

“这些漏洞允许访问微软内部服务，欺骗链接预览，并且，对于Android用户来说，泄露他们的IP地址和破坏他们的Teams应用程序/渠道，”研究人员说。

在这四个漏洞中，微软只解决了IP 地址泄漏 (Android) 漏洞，对于其他漏洞，微软表示他们并未在当前版本中修复 SSRF，而 DoS
也是计划在未来版本中考虑修复。

使用户暴露于网络钓鱼的漏洞未被修补

至于URL预览欺骗漏洞，虽然被标记为不会对 Teams 用户构成任何危险，但威胁者可以利用该漏洞伪装成恶意链接，进行钓鱼攻击。

微软表示：“MSRC 调查了这个问题并得出结论，认为这不会构成直接威胁，不需要紧急关注。因为一旦用户点击 URL，他们将不得不转到那个恶意
URL，这将是一个免费的样品，用户能看到不是其想打开的链接应该不会上当。”

研究人员补充说：“虽然所发现的漏洞影响有限，但令人惊讶的是，如此简单的攻击载体以前似乎没有被测试过，而且微软没有意愿或资源来保护他们的用户免受其害。”

自 7 月以来，Teams 还使用 Defender for Office 365 安全链接保护，来保护用户免受基于 URL
的网络钓鱼攻击，这在一定程度上解释了该公司决定不解决可能在网络钓鱼活动中滥用的欺骗漏洞。

虽然安全链接保护对所有Teams用户都可用，并且适用于跨对话、群组聊天和Teams渠道共享的链接，但它仍然需要通过在Microsoft 365
Defender门户中设置安全链接策略来启用。

> 参考来源：https://www.bleepingcomputer.com/news/security/microsoft-teams-bug-> allowing-phishing-unpatched-since-march/

