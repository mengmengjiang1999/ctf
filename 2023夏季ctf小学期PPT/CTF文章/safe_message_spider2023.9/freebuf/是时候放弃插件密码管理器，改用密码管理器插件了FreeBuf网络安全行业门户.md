## **神锁离线版密码管理器插件**

现已支持Google Chrome 和 Microsoft Edge浏览器，在插件商店中搜索安装就行了。

插件延续神锁离线版App的优良传统，无需注册、无需登录，即装即用。

安装后，把插件固定在插件栏，可以一键弹出扫码框。

![v2-fb72d76298bc976cfb2934f1e232cdc0_720w.jpg](https://image.3001.net/images/20210226/1614307217_60385f91a2acc67ab7250.jpg!small)

插件使用非常简单直观。在浏览器中打开需要登录的网页时，会自动弹出扫码登录框，只需在手机上点击2次就可以完成密码填充。

![v2-aaee6d0073b7788757bc8c92dbe044d4_720w.jpg](https://image.3001.net/images/20210226/1614307218_60385f9216a738f1f6c68.jpg!small)

1\. 打开手机上的神锁离线版App（需要升级到2020.08版以上），点击扫码。

![v2-c45be9389ad4351a1a91dd981ba3618c_720w.jpg](https://image.3001.net/images/20210226/1614307218_60385f92b7649cb47a5aa.jpg!small)

> 温馨提示，手机不需要离二维码很近，可以适当远一点。有些手机摄像头微距可能模糊，反而不容易扫出来。

2\. 接着会看到和自动填充一样的界面，点击选择要填充的账号。

![v2-2b46ea6959f21716260670666c543061_720w.jpg](https://image.3001.net/images/20210226/1614307219_60385f9339294371fb9b8.jpg!small)

选择后，App会加密账号密码数据，并打开手机浏览器，将加密信息发送到桌面浏览器，完成自动填充。

![v2-cb33f6e817e31cb58a579f718b5c873c_720w.jpg](https://image.3001.net/images/20210226/1614307220_60385f94031387bd3b439.jpg!small)

##  **为什么放弃插件密码管理器**

绝大多数密码管理器提供插件版时，都基于浏览器的插件开发接口，实现完整的密码管理器，称之为插件密码管理器。

那些云同步的插件密码管理器不是很好用吗？为什么要放弃？因为 **不安全！**

![v2-70fcb334569fdcd08b2752157e69ae9d_720w.jpg](https://image.3001.net/images/20210226/1614307220_60385f94776357d3d4d9d.jpg!small)

即使不考虑云安全以及网络安全，插件密码管理器采用的技术也存在严重的安全威胁。

浏览器的插件开发接口基于Web技术，非常开放灵活。恶意程序通过 DOM / JS，几乎可以访问页面中的任何数据。著名安全研究员 Sean Cassidy
在他的博客 [Browser Extension Password Managers Should Not Be
Used](https://link.zhihu.com/?target=https%3A//www.seancassidy.me/browser-extension-password-managers-should-not-be-used.html)中认为插件密码管理器风险无法避免。

![v2-1b2df1d33d9f250d97c6b1fa21e270d9_720w.jpg](https://image.3001.net/images/20210226/1614307220_60385f94d7f6f8fd02f44.jpg!small)

而且，浏览器漏洞众多，是除操作系统外，被黑客攻击最多的平台。

![v2-2cf72ed2e083eb58cd6c6b5cccf2022b_720w.jpg](https://image.3001.net/images/20210226/1614307221_60385f95402b971d38118.jpg!small)

> 数据来源：[CVE
> Details](https://link.zhihu.com/?target=https%3A//www.cvedetails.com/top-50-products.php%3Fyear%3D0)

正是因为这两大风险，安全研究人员都建议不要使用插件密码管理器。

神锁离线版密码管理器对待安全问题，从来都是精心设计，不落俗套。神锁离线版没有在插件中实现密码管理器的功能，而是做了一个真正的插件。使用手机端的App扫码，将密码加密发送到插件，再填充到网页。密码全部保存在手机App中，受手机安全芯片保护（[手机模拟银行*卡支付使用相同的安全芯片](https://link.zhihu.com/?target=https%3A//developer.android.google.cn/guide/topics/connectivity/nfc/hce%23SecureElement)）。

![v2-c8bdbc16a3bc98b11c106376230e0525_720w.jpg](https://image.3001.net/images/20210226/1614307221_60385f9597b7c8fb21f26.jpg!small)

神锁离线版手机App，通过扫描由插件生成的二维码，与插件创建安全共享密钥，将需要填充的账号密码加密发送到插件。插件解密密码后，将它填充到网页的输入框中。

通过二维码创建的安全共享密钥，只有手机App和插件知道，实现端到端加密。无论是第三方，还是神锁离线版官方，都无法解密。

神锁离线版插件不保存任何密码，黑客无法通过读取浏览器数据来破解用户密码。

我们假设一个极端情况，浏览器存在严重的安全漏洞，破得像筛子一样，

  * 使用神锁离线版插件，在填充的时候，恶意程序可以偷取一个密码。
  * 使用其他插件密码管理器，在输入主密码后，恶意程序可以偷取所有保存的密码。

![v2-54a0b718ffc8a7be40f6e6cea82cc2db_720w.jpg](https://image.3001.net/images/20210226/1614307221_60385f95eb6f7f9f6fb8c.jpg!small)

##  **神锁离线版插件的其他优势**

神锁离线版在安全设计上，一直以来都是遥遥领先。此外，神锁离线版还有这些优势：

  * 极简主义，让生活回归简单

使用神锁离线版插件，和使用手机App一样，无需注册，无需登录，甚至无需设置，即装即用。

> 我们相信，使用密码管理器，就不应该再为密码发愁，包括主密码，[0 Password,
> 忘记密码管理器的主密码怎么办？](https://link.zhihu.com/?target=https%3A//www.bluespace-> labs.com/blog/0password/)

  * 信任和分享

插件无需登录或绑定账号，需要分享账号给可以信任的好友时，只需隔空扫码。

  

## 未完待续...

  * [神锁离线版插件的安全设计](https://zhuanlan.zhihu.com/p/258740812)

> 大家都已经知道，加密 ≠ 安全，所谓的军事级别加密，只是营销口号，忽悠外行。  
> 密码管理器的安全关键在于：安全设计。

  *  **神锁离线版插件端到端加密比HTTPS更安全**

> 神锁离线版插件的加密传输有多安全？比银行都在使用的HTTPS还安全。

  *  **验证神锁离线版的安全机制**

![v2-aa58fe5f12355da7e93b9ab087c6b090_720w.jpg](https://image.3001.net/images/20210226/1614307222_60385f964a1ed95c16034.jpg!small)

