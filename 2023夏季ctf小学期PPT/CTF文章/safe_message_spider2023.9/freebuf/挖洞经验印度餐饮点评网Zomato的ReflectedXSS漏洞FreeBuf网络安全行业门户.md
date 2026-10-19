***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

**大家好，今天要分享的是印度美食搜索点评网站Zomato的一个反射型XSS漏洞（$250），文中作者详细描述了具体的漏洞发现过程。漏洞虽然简单，国内厂商也可能几乎没啥赏金，但也可学习学习，参考借鉴。**

## 漏洞发现

最近我在读《Mastering Modern Web Penetration
Testing》（精通流行Web渗透测试技术）这本书，书中提到了<https://www.wolframalpha.com/>这个网站，可以用它来进行子域名枚举，效果还不错。

于是，我就想找个目标上手试试，所以我就在其搜索栏中输入了zomato.com，之后，枚举结果中返回了10多个子域名信息。而且，结果中还会返回各个子域名的日均访问量，这个选项对发现一些偏门网站还是有用的。基于此，返回结果中最后一个子域名secretx.zomato.com引起了我的注意，因为它的日均访问量才400，是所有子域名中最少的。

我在浏览器中打开了secretx.zomato.com, 跳出来一个按钮 -“sign in with Zomato”，我看了看源码，也没什么特别的。

我点击按钮，它就跳转到了zomato.com，随后，又跳出来一个显示框，它上面提示“SecretX Client wants to access you
Zomato Account. Accept or Recject”。哦，有点意思。

所以，我又立即回到网站secretx.zomato.com中仔细查看源码，从中我发现了以下URL链接：

>
> [https://auth2.zomato.com/oauth2/auth?response_type=code&client_id=80b39918-90be-49d2-ac52-4a8b1a25bcf1&redirect_uri=https%3A%2F%2Fsecretx.zomato.com%2Fuser%2Foauth2%2Fredirect_uri&state=2BHoBnVFFKP29L6SerHgEb7OCnBDPO](https://auth2.zomato.com/oauth2/auth?response_type=code&client_id=80b39918-90be-49d2-ac52-4a8b1a25bcf1&redirect_uri=https%3A%2F%2Fsecretx.zomato.com%2Fuser%2Foauth2%2Fredirect_uri&state=2BHoBnVFFKP29L6SerHgEb7OCnBDPO)

当点击Sign in with
Zomato的按钮之后，以上URL链接就会被加载。接下来，我在上述URL参数中添加了一些授权验证的填充值，看看是否能引起一些错误响应，果然：

填充进去的参数值竟然都能在响应页面中有所显示，如error=xss，error_description=xsssy，error_hint=xss等，这下我接着来检查
< 和 > 是否被过滤掉，结果是：NO！  

## 构造Payload  

有了这些发现，我就想构造XSS攻击，但可能由于服务端部署了WAF，所以总是不起效。在这个阶段，我花了好多时间，最终也没啥效果。之后，我就在一些漏洞报告中寻找绕过WAF的技巧，并一个个Payload地进行尝试。

最终，终于有一个Payload可用了：

    
    
    <marquee loop=1 width=0 onfinish=alert`1`>XSS</marquee>

但因为alert()、confirm()、prompt()这些形式都被服务端的WAF过滤阻拦了，所以连DOM信息也获取不到。后来我还试了Payload的URL编码，但也没成功。时间马上就是凌晨3点半了，为了第二天上课不迟到，我想洗洗睡了。

好在我还有点精神，提提神后，我继续找很多文章博客进行参考，之后我突然想到Somdev之前发布的一个XSS Cheatsheet -<https://github.com/s0md3v/AwesomeXSS>，其中提到用co\u006efirm()来代替confirm()，构造Payload实现绕过：

    
    
    co\u006efirm()

经过unicode字符编码，这一试竟然可以！可以获取到服务端的DOM元素信息了：  

上报了漏洞之后，我就一头睡过去了，第二天醒来手机信息提示：“Zomato has rewarded you 250$”。

## PoC

存在XSS漏洞的URL链接：

>
> [https://auth2.zomato.com/oauth2/fallbacks/error?error=xss&error_description=xss&error_hint=xss](https://auth2.zomato.com/oauth2/fallbacks/error?error=xss&error_description=xss&error_hint=xss)

存在漏洞的参数：所有参数

XSS Payload:

    
    
    <marquee loop%3d1 width%3d0 onfinish%3dco\u006efirm(document.cookie)>XSS<%2fmarquee>

PoC URL:

>
> [https://auth2.zomato.com/oauth2/fallbacks/error?error=xss&error_description=xsssy&error_hint=%3Cmarquee%20loop%3d1%20width%3d0%20onfinish%3dco](https://auth2.zomato.com/oauth2/fallbacks/error?error=xss&error_description=xsssy&error_hint=%3Cmarquee%20loop%3d1%20width%3d0%20onfinish%3dco)\u006efirm(document.cookie)%3EXSS%3C%2fmarquee%3E  
>

## 视频

看不到？点[这里](https://v.qq.com/x/page/z08319nojgq.html)

## 漏洞原因

在漏洞报送进程中，Zomato漏洞分类负责人Prateek Tiwari
告诉我，漏洞出在了Zomato采用的开放授权验证提供商Hydra身上，为了表示感谢，Hydra还把我加入了新版本的发行致谢名单中。  

***参考来源：[medium](https://medium.com/@sudhanshur705/reflected-xss-in-zomato-f892d6887147)，clouds编译，转载请注明来自FreeBuf.COM**  

