**Android
5.26.0系统中，开源的私人浏览器DuckDuckGo被发现存在漏洞可导致攻击，攻击者可通过该漏洞利用URL欺骗的方式发动攻击，目前该浏览器的安装量已超过500万。**

![DuckDuckGo__Privacy_Browser_for_Android.jpg](https://image.3001.net/images/20190529/15591132446160.jpg!small)

安全研究员Dhiraj
Mishra将这个漏洞编号为CVE-2019-12329，并通过HackOne平台的漏洞赏金计划向该应用的安全团队通知漏洞的存在。研究人员表示，他通过特定的JavaScript页面欺骗了DuckDuckGo浏览器的omnibar完成了漏洞验证，该页面使用setInterval函数，使其每10到50毫秒便可重新加载一个URL。

虽然真正的DuckDuckGo.com网站会在每50毫秒自动加载一次，但其内部的HTML会被修改为完全不同的内容用于甄别。

![Proof of
concept.png](https://image.3001.net/images/20190529/15591133004867.png!small)

代码证明

研究人员表示，这个漏洞是在2018年10月31日通过HackOne平台提交给该浏览器的安全团队的，最初其威胁级别是高危，直至2019年5月27日，才得出最后的结论：这个漏洞的威胁级别并不算高危。

潜在的攻击者可以通过更改浏览器地址栏中显示的URL来欺骗用户，使他们认为自己正在浏览安全的网页，从而执行URL欺骗攻击。

![DuckDuckGo Privacy Browser for Android spoofed
omnibar.png](https://image.3001.net/images/20190529/15591133573479.png!small)

DuckDuckGo omnibar的PoC

因此，不知情的用户可能会被重定向至各种由攻击者伪造的网站页面，而这些网站可能会是网络钓鱼、恶意广告，又或者是恶意软件植入，其最终的目标都会是目标用户的数据信息。

在5月初，安全研究员Arif Khan还发现UC浏览器和UC浏览器mini版也存在类似的URL欺骗攻击漏洞，而这两款App共计已安装了6亿多次。

Arif Khan表示，URL欺骗攻击是最恼人的钓鱼攻击，因为这原本应当是用户识别网站的唯一方法。

***参考来源：[bleepingcomputer](https://www.bleepingcomputer.com/news/security/duckduckgo-android-browser-vulnerable-to-url-spoofing-attacks/)，Karunesh91编译，转载请注明来自FreeBuf.COM**

