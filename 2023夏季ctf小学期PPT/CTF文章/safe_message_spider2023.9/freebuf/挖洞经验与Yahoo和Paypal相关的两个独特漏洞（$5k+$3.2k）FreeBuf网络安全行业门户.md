***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 ****![bug-bounty-3-.jpg](https://image.3001.net/images/20190408/1554724326_5cab35e700050.jpg!small)
**本文分享的是与Yahoo和Paypal相关的两个独特漏洞，一个为Yahoo的IDOR漏洞（不安全的直接对象引用），另一个为Paypal的DoS漏洞，两个漏洞的发现者都为印度安全工程师，其发现原理和思路也相对简单和典型，分享于此，希望能对读者起到借鉴参考作用。**

## YAHOO的IDOR漏洞（$5,000）

繁忙的一天，当我外出工作回到办公室的时候，已经是下午5点了，还有一小时就下班回家。好吧，这点时间我只有打开Burp测试一些目标网站了。

那个时候，我经常用Yahoo
Notepad（雅虎网络笔记）来记录一些个人心得体会，此时，我就突然想来测测这个应用到底如何。于是，我打开了这个雅虎网络笔记的对应网站 -<https://notepad.yahoo.com>，然后，在开启了Burp抓包的同时，我也在向我的个人笔记空间中书写笔记。

笔记记录完之后，我在Proxy HTTP History标签中进行了检查，一个GET请求中的加密字符串映入了我的眼帘：

    
    
    GET /ws/v3/users/fziy4wzxr41k4qwsgumu2v2qymynzat6kclqpwmc/items?format=json&count=200&type=Journal&wssid=55mJmcMk3tg&rand=1478541308397&prog=aeon HTTP/1.1

Host: calendar.yahoo.com

![01.jpeg](https://image.3001.net/images/20190408/1554723647_5cab333fdbd84.jpeg!small)可以看到，在users/旁边的加密字符串
- **fziy4wzxr41k4qwsgumu2v2qymynzat6kclqpwmc** ，它代表什么呢？

我立马意识到，它是我的用户名，它被加密然后发送到服务器端！那我就想着，能不能把它换成我明文方式的Yahoo用户名呢? 这样一来，其构造的GET请求如下：

    
    
    GET /ws/v3/users/yahoo-username/items?format=json&kw=test&count=200&type=Journal&wssid=55mJmcMk3tg&rand=1478541308397&prog=aeon HTTP/1.1

Host: calendar.yahoo.com

让人意外的是，我把这个加密字符串换成了我明文方式的Yahoo用户名后，Yahoo服务端的响应和加密字符串的响应是相同的，也就是两者的响应内容都是相同的包含同一笔记内容的JSON格式！

接着，我又在上述GET请求中，尝试把这个用户名换成了我另外一个Yahoo测试账户(test_account_2222)
，之后，它响应的是我这个Yahoo测试账户的笔记内容。

![02.png](https://image.3001.net/images/20190408/1554723833_5cab33f98431d.png!small)问题之处在于，Yahoo
Notepad（雅虎网络笔记）虽然把用户名进行了加密传输，但是在对服务端的请求过程中，毫无对用户名和账户的匹配检查机制，这也就导致了可以通过输入任意用户名来获取任意账户的云端笔记内容。

> /ws/v3/users/fziy4wzxr41k4qwsgumu2v2qymynzat6kclqpwmc/items?
>
> /ws/v3/users/user-name/items?

经过几个测试账号的反复实验确认，我确定该漏洞漏洞确实存在，理论上来说，这应该算是一个大漏洞了，因为我可以在GET请求中输入任意用户名的方式，去查看任意用户账户对应的雅虎网络笔记内容。

实际上，从检查应用请求到发现漏洞的整个过程中，总共也就花了差不多15分钟，欣喜若狂之余我也非常清醒理智，要淡定要淡定。这肯定是一个很独特的漏洞，需要的是不同的思维方式和敏锐的嗅觉，这一次恭喜我做到了！

漏洞最终被Yahoo分类为IDOR（不安全的直接对象引用）漏洞，获得了$5,000美金的奖励。我个人的感觉是，开发人员认为只要加密就安全了，但其实不然，除了加密，还需要验证手段才行。

## PayPal的DoS漏洞（$3,200）

某天，我在测试网站 - braintreepayments.com
的漏洞，它属于Paypal漏洞众测范围内项目，是PayPal于2013年收购的在线支付平台。

在检查该网站的源代码过程中，我发现了以下这段奇怪的JavaScript代码：

    
    
    var targetLocale = window.location.href.match(/locale=(.{5})/) ? window.location.href.match(/locale=(.{5})/)[1] : null;
    

![03.png](https://image.3001.net/images/20190408/1554723893_5cab34356d490.png!small)在仔细阅读完代码之后，分析可知，locale为地区语言参数，currentLocale为当前语言参数，如en-us。我注意到该代码段具备的一个功能是，去检查用户带有locale参数的请求，如果该参数的值不等于en-us，也就是浏览器获取到的currentLocale值时，那么，这个用户的locale参数值就会被代码方法
window.localStorage.setItem('locale', targetLocale) 存储到storedLocale中去。

在这种机制下，每当一位用户访问[braintreepayments.com](http://braintreepayments.com)网站时，如果其当前的currentLocale值与storedLocale不匹配，那么他就会被强制重定向到网页
-[https://braintreepayments.com/`locale`](https://braintreepayments.com/%60locale%60)，这种情况下，即使他点击<https://braintreepayments.com/>网站上的任意链接，最终也是一样被重定向到网页
-[https://braintreepayments.com/`locale`](https://braintreepayments.com/%60locale%60)。

这个功能可构造出一个什么漏洞呢？当然是Dos了。尽管locale地区参数只有5位字母（如en-us、zh-cn等），才能被保存在浏览器的localstorage中，但这也足够用来创建一个适合的PoC了，如下：

> [https://www.braintreepayments.com/legal/policy-> updates?utm_campaign=BT_EMEA_LUX_SafeHarborUpdate_20160413&utm_medium=email&utm_source=Eloqua&elq_cid=5230793&locale=fword](https://www.braintreepayments.com/legal/policy-> updates?utm_campaign=BT_EMEA_LUX_SafeHarborUpdate_20160413&utm_medium=email&utm_source=Eloqua&elq_cid=5230793&locale=fword)

该PoC链接造成的影响是，受害者一旦点击访问了上述链接，他们就会被自动重定向到<https://braintreepayments.com/fword>网页中去，即使他们再点击其中的Log
in或Sign up也一样没用，还是会继续跳转到<https://braintreepayments.com/fword>网页中。

![04.png](https://image.3001.net/images/20190408/1554724071_5cab34e79adcf.png!small)漏洞影响就是，如果恶意攻击者通过一些公开渠道大肆散布上述PoC链接，大量受害者会重定向到<https://braintreepayments.com/fword>网页，将会造成普通用户无法正常访问使用braintreepayment平台网站，形成间接方式的Dos攻击，且受害者需要清除浏览器中的JS缓存才能解除这种恶意重定向。漏洞上报后，获得了Paypal官方$3,200美金的奖励。

 ***参考来源：[medium](https://medium.com/h4x00r/my-very-first-bug-a-dreaded-dupe-and-then-an-idor-jackpot-d01b69f6fbae)\[userjournal](https://blog.usejournal.com/an-unusal-bug-on-braintree-paypal-b8d3ec662414)，clouds编译，转载请注明来自FreeBuf.COM**  

