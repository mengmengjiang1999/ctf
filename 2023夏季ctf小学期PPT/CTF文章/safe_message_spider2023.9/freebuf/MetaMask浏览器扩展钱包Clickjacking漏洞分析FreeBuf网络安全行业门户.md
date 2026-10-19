By：Thinking@慢雾安全团队

##  **背景概述**

2022 年 6 月 3 日，MetaMask（MM）公开了白帽子发现的一个严重的 Clickjacking 漏洞，这个漏洞可以造成的影响是：在用户的 MM
插件钱包处于解锁状态，用户访问恶意的站点时，站点可以利用 iframe 标签将解锁的 MM
插件钱包页面嵌入到网页中并进行隐藏，然后引导用户在网站上进行点击操作，实际上是在 MM 解锁的页面中进行操作，从而盗取用户的数字货币或藏品等相关资产。鉴于
MM 的用户体量较大，且 Fork MetaMask 插件钱包的项目也比较多，因此在 MM
公开这个漏洞后，我们立即开始对这个漏洞进行复现，然后开始搜寻这个漏洞对于其他 Fork MetaMask 项目的影响。

随后，慢雾安全团队尽可能地通知受到影响的项目方，并引导项目方进行修复。现在将这个 Clickjacking 漏洞的分析公开出来避免后续的项目踩坑。

##  **漏洞分析**

由于 MM 在发布这个 Clickjacking
漏洞的时候并没有详细的说明，仅是解释了这个漏洞的利用场景以及能够产生的危害，所以我在进行复现的时候也遇到了挺多坑（各种盲猜漏洞点），所以为了让大家能够更好地顺畅地理解整个漏洞，我在进行漏洞分析之前先补充下一个知识点。

我们来了解下 Manifest - Web Accessible
Resources。在浏览器扩展钱包中有这么一个配置：web_accessible_resources，其用来约束 Web
页面能够访问到浏览器扩展的哪些资源，并且在默认的情况下是 Web
页面访问不到浏览器扩展中的资源文件，仅浏览器扩展的本身才能访问到浏览器扩展的资源。简而言之就是 http/https 等协议下的页面默认是没法访问到
chrome-extension，当然如果扩展钱包配置了 web_accessible_resources 将扩展钱包内部的资源暴露出来，那么就能被
http/https 等协议下的页面访问到了。

而 MM 扩展钱包在 10.14.6 之前的版本（本文以 10.14.5 为例）一直保留着 "web_accessible_resources":
["inpage.js", "phishing.html"] 的配置，而这个配置是漏洞得以被利用的一个关键点。

![MetaMask浏览器扩展钱包Clickjacking漏洞分析](https://image.3001.net/images/20220614/1655203983_62a8688f0b6983f4ac6ab.jpg!small)

然而在进行漏洞分析的时候，发现在 app/scripts/phishing-detect.js(v10.14.5)
中已经对钓鱼页面的跳转做了协议的限制。（这里的限制在我的理解应该是还有其他的坑，毕竟 "web_accessible_resources":
["inpage.js", "phishing.html"]`这个配置还保留着）。

![MetaMask浏览器扩展钱包Clickjacking漏洞分析](https://image.3001.net/images/20220614/1655203986_62a868923bbae86790fe8.jpg!small)

我们继续跟进这个协议限制的改动时间点，发现是在如下这个 commit 中添加了这个限制，也就是说在 v10.14.1 之前由于没有对跳转的协议进行限制，导致
Clickjacking 漏洞可以轻易被利用。

相关的 commit:

<https://github.com/MetaMask/metamask-extension/commit/c1ca70d7325577835a23c1fae2b0b9b10df54490>

<https://github.com/MetaMask/metamask-extension/compare/v10.14.0...v10.14.1>

![MetaMask浏览器扩展钱包Clickjacking漏洞分析](https://image.3001.net/images/20220614/1655203990_62a8689629cbd0e80e37b.jpg!small)

为了验证代码的分析过程，我们切换到 protocol 限制之前的版本 v10.14.0 进行测试，发现可以轻松复现整个攻击过程。

![MetaMask浏览器扩展钱包Clickjacking漏洞分析](https://image.3001.net/images/20220614/1655203994_62a8689acf50be1fced05.jpg!small)

但是在 MM 公开的报告中也提到，Clickjacking 漏洞是在 v10.14.6 进行了修复，所以 v10.14.5
是存在漏洞的，再继续回头看这里的猜想。（这里的限制在我的理解应该是还有其他的坑，毕竟 "web_accessible_resources":
["inpage.js", "phishing.html"] 这个配置还保留着）。

经过反复翻阅代码，在 v10.14.5 以及之前版本的代码，会在钓鱼页面提示的时候，如果用户点击了 continuing at your own risk.
之后就会将这个 hostname 加入到本地的白名单列表中。从而在下一次访问到该网站的时候就不会再出现 MetaMask Phishing
Detection 的提醒。

比如这个钓鱼网站：ethstake.exchange，通过 iframe 标签将钓鱼网站嵌入到网页中，然后利用 Clickjacking
漏洞就能将恶意的钓鱼网站加入到白名单中，同时在用户下一次访问钓鱼网站的时候 MM 不会再继续弹出警告。

![MetaMask浏览器扩展钱包Clickjacking漏洞分析](https://image.3001.net/images/20220614/1655203999_62a8689f06a27649a3f43.jpg!small)

##  **分析结论**

如上述的分析过程，其实 MM 近期修复的是两个 Clickjacking 漏洞，在复现过程中发现最新的 v10.14.6 已经将
web_accessible_resources 的相关配置移除了，彻底修复了 MetaMask Phishing Detection
页面的点击劫持的问题。

（1）利用 Clickjacking 漏洞诱导用户进行转账的修复（影响版本：< = v10.14.0）：

<https://github.com/MetaMask/metamask-extension/commit/c1ca70d7325577835a23c1fae2b0b9b10df54490>

（2）利用 Clickjacking 漏洞将钓鱼网站加入到白名单的修复（影响版本：<= v10.14.5）：

<https://github.com/MetaMask/metamask-extension/commit/7199d9c56775111f85225fe15297e47de8e2bc96>

慢雾安全团队对 chrome 扩展商店中的各个知名的扩展钱包进行了 Clickjacking 的漏洞检测，发现如下的钱包受到 Clickjacking
漏洞影响：

  * Coinbase Wallet (v2.17.2)

  * Coin98 Wallet (v6.0.6)

  * Maiar DeFi Wallet (v1.2.17)

慢雾安全团队第一时间联系项目方团队，但是到目前为止部分项目方还未反馈，并且 MM 公开这个漏洞至今已经过去了 11
天。为了避免用户因为该漏洞遭受损失，慢雾安全团队选择公开漏洞的分析。如果受影响的相关项目方看到这篇文章需要协助请联系慢雾安全团队。

慢雾安全团队再次提醒浏览器扩展钱包项目方如果有基于 MetaMask <v10.14.6
的版本进行开发的要注意排查是否有受到该漏洞的影响，如需要协助请联系慢雾安全团队。

慢雾安全团队建议普通用户在项目方还未修复漏洞之前可以先暂时停止使用这些扩展钱包（在浏览器扩展程序管理中关闭这些扩展钱包），等待钱包官方发布修复版本后，用户可以及时更新到已修复的版本进行使用。

 **参考链接** ：

<https://medium.com/metamask/metamask-awards-bug-bounty-for-clickjacking-vulnerability-9f53618e3c3a>

