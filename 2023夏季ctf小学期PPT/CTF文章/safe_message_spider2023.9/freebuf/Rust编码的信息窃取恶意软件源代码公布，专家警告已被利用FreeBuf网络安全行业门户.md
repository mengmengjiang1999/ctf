黑客论坛上发布了一个 **用Rust编码的信息窃取恶意软件源代码** ，安全分析师警告，该恶意软件已被积极用于攻击。

该恶意软件的开发者称，仅用6个小时就开发完成，相当隐蔽， **VirusTotal的检测率约为22%** 。

![](https://image.3001.net/images/20220726/1658805742_62df5dee264bae647bc5f.png!small)恶意软件开发者在一个暗网论坛上公布源代码

信息窃取恶意软件采用Rust（一种跨平台语言）编写的，可在多个操作系统使用。从其当前的使用范围看，它 **目前只针对Windows操作系统**
。但它采用Rust编写意味着将其移植到Linux或macOS并不复杂，所以原开发者或其他人可能在未来进行改写。

网络安全公司Cyble的分析师对该信息窃取软件进行了采样，并将其命名为 "Luca Stealer"。

采样报告显示，Luca
Stealer具有明显的恶意功能，当执行时，它试图从30个基于Chromium的网络浏览器中窃取数据，它将窃取存储的信用卡、登录凭证和cookies等信息；它还针对"加密货币、浏览器钱包插件、Steam账户、Discord代币、Ubisoft
Play等。

![](https://image.3001.net/images/20220726/1658805697_62df5dc1f156601399c58.png!small)针对浏览器扩展程序

与其他信息窃取软件相比，Luca Stealer是密码管理器浏览器插件，可以窃取此类插件储存在本地的数据。它还会捕捉屏幕截图，将其保存为.png文件，执行
"whoami"对主机系统进行剖析，并将细节发送给其运营商。

![](https://image.3001.net/images/20220726/1658805649_62df5d910a95fc31754cf.png!small)收集主机系统信息

但Luca Stealer并不具备其他信息窃取软件都拥有的修改剪贴板内容功能，该功能可以劫持加密货币交易的剪切器。

Cyble分析师介绍，被盗数据通过Discord webhooks或Telegram
bots渗出，具体取决于渗出的文件是否超过50MB。它使用Discord webhook将数据发回给攻击者，以获取更大的被盗数据日志。

被盗的数据压缩在ZIP文档中，并附有所包含内容的摘要，方便窃密者快速评估数据价值。

![](https://image.3001.net/images/20220726/1658805577_62df5d495bb089b78dbae.png!small)

ZIP文件发送的被盗文件摘要

Cyble报告称，目前发现了至少25例Luca
Stealer的在野利用，虽然源代码已被公布，但它是否会大规模部署还不得而知。但由于其源代码是免费公布，可能成为其滥用原因之一。

 **原文链接：**

> https://www.bleepingcomputer.com/news/security/source-code-for-rust-based-> info-stealer-released-on-hacker-forums/

