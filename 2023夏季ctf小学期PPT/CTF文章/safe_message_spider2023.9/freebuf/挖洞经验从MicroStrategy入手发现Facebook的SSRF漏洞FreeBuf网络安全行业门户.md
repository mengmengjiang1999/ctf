![1592991329_5ef31e61902d4.jpg!small](https://image.3001.net/images/20200624/1592991329_5ef31e61902d4.jpg!small)

**本文中，作者从Facebook子域名中部署的微策略（MicroStrategy）应用服务入手，通过Burp
Collaborator构造，利用深入深入再深入的挖掘，发扬持之以恒的精神，发现了敏感信息泄露和SSRF漏洞，收获了$31500（$1000+$30000+$500）的漏洞奖金。一起来看看。**

## 漏洞端倪

Facebook是流行的社交媒体平台，我个人喜欢测试Facebook漏洞，这不，最近我发现了Facebook的子域名<https://m-nexus.thefacebook.com/>，访问它后会自动跳转到<https://m-nexus.thefacebook.com/servlet/mstrWebAdmin>，如下图所示：

![1592990063_5ef3196f46b99.png!small](https://image.3001.net/images/20200624/1592990063_5ef3196f46b99.png!small)

从网页中的响应内容，我马上对其中的关键字mstrWebAdmin进行了谷歌查找，发现它是基于商务智能公司微策略（MicroStrategy）工作集成的一个网站服务：

![1592990076_5ef3197cb4fe1.png!small](https://image.3001.net/images/20200624/1592990076_5ef3197cb4fe1.png!small)

我还从一篇博文中找到了确定线索：

![1592990088_5ef31988c3180.png!small](https://image.3001.net/images/20200624/1592990088_5ef31988c3180.png!small)

接着，我从MicroStrategy的官方配置文档中发现，有两个可以公开访问的端点：

![1592990108_5ef3199c0b851.png!small](https://image.3001.net/images/20200624/1592990108_5ef3199c0b851.png!small)

结合MicroStrategy官方配置文档深入研究，我发现了一个默认为HTTP基本认证配置的端点：<https://m-nexus.thefacebook.com/servlet/mstrWeb>，以及另一个无需身份验证的端点：<https://m-nexus.thefacebook.com/servlet/taskProc>

在后一个无需验证的端点中，它会用“taskId”等参数来执行数据收集和内容生成。我用Burp的Intruder模块对其中的任务参数进行了枚举，发现其每一个任务请求都会执行一个有效的会话参数验证，唯独在处理“taskId=shortURL”时无需会话参数验证，因此，攻击者可以利用这条线索无需任何身份验证访问到facebook的该类服务。

![1592990157_5ef319cdee3e0.png!small](https://image.3001.net/images/20200624/1592990157_5ef319cdee3e0.png!small)

![1592990174_5ef319de09c49.png!small](https://image.3001.net/images/20200624/1592990174_5ef319de09c49.png!small)

但是，在该操作请求下，我尝试着把MicroStrategy官方配置文档中涉及的参数都fuzz了一遍，也没有从请求响应中返回有用的信息，大多数时候它返回的都是状态码为500的错误消息“The
source URL is not
valid”，为此，我就尝试了把MicroStrategy的一些SDK源码下载下来打算进行一个源码分析。以下是一个将近400M的源码，其中包含了一些脚本和jar文件。

![1592990201_5ef319f9c587f.png!small](https://image.3001.net/images/20200624/1592990201_5ef319f9c587f.png!small)

在 jd-gui 帮助下，我对它进行了反编译。我查找的目标是无需会话参数验证，处理short
URL的shortURL请求任务，最终，我在其中一个jar文件中发现了相关调用说明：

![1592990215_5ef31a0752603.png!small](https://image.3001.net/images/20200624/1592990215_5ef31a0752603.png!small)

现在我要分析的是，为什么每次该任务请求返回的都是错误消息。另外，从代码中可以看出，“shortURL”请求中涉及的srcURL参数值必须是经“<https://tinyurl.com/>"
转化后的短地址，只有通过该短地址，任务才能执行数据导致或读取。如下：

![1592990232_5ef31a182cc7a.png!small](https://image.3001.net/images/20200624/1592990232_5ef31a182cc7a.png!small)

## 测试利用

以下是我发给Facebook的复现步骤：

1、打开Burp抓包工具，选择其中的“Burp Collaborator client”，生成一个Collaborator 域名，并复制：

![1592990265_5ef31a396f6ea.png!small](https://image.3001.net/images/20200624/1592990265_5ef31a396f6ea.png!small)

2、打开“<https://tinyurl.com/>"网站，输入复制的Collaborator域名，生成tinyurl方式的短域名：

![1592990279_5ef31a47c5377.png!small](https://image.3001.net/images/20200624/1592990279_5ef31a47c5377.png!small)

3、在以下链接，在“srcURL”参数处插入我们生成的tinyurl短域名，然后发起访问：

[https://m-nexus.thefacebook.com/servlet/taskProc?taskId=shortURL&taskEnv=xml&taskContentType=json&srcURL=](https://m-nexus.thefacebook.com/servlet/taskProc?taskId=shortURL&taskEnv=xml&taskContentType=json&srcURL=){YOUR_TINY_URL_HERE}

![1592990303_5ef31a5f8a86f.png!small](https://image.3001.net/images/20200624/1592990303_5ef31a5f8a86f.png!small)

4、观察Burp Collaborator服务端的返回信息，可以看到，IP地址“199.201.64.1”对Burp
Collaborator服务端发起了请求：

![1592990325_5ef31a7591d7a.png!small](https://image.3001.net/images/20200624/1592990325_5ef31a7591d7a.png!small)

5、理论上看，这无疑是SSRF的前奏了，经whois记录查询，IP地址199.201.64.1确实属于Facebook所有：

![1592990341_5ef31a858e10f.png!small](https://image.3001.net/images/20200624/1592990341_5ef31a858e10f.png!small)

6、为深入测试SSRF，我又构造了一个由内部IP地址（如123.10.123.10）生成的tinyurl短域名，形成srcURL参数值，发起请求后，无任何反应：

![1592990356_5ef31a946abb5.png!small](https://image.3001.net/images/20200624/1592990356_5ef31a946abb5.png!small)

7、我又用127.0.0.1:8080构造了一个tinyurl短域名，形成srcURL参数值，发起请求后，Facebook服务端提示需要进行HTTP基本认证：

![1592990374_5ef31aa6756ee.png!small](https://image.3001.net/images/20200624/1592990374_5ef31aa6756ee.png!small)

反复利用该方法，可以枚举出Facebook防火墙后的一系列内部IP地址和相关架构信息，于是我立马把该漏洞上报给了Facebook安全团队。但是之后，Facebook认为这不属于安全漏洞，......：

![1592990393_5ef31ab90f475.png!small](https://image.3001.net/images/20200624/1592990393_5ef31ab90f475.png!small)

## 深入挖掘（$1000）

利用上述发现，我尝试利用不同的SSRF测试姿势试图读取Facebook服务端的敏感信息，或是云端的实例数据，但经file://、dict://、ftp://、gopher://等一通操作之后，竟然都不成功，一无所获。

最终，我总算发现了几个像样的漏洞实例。如以下的这个XSS：

![1592990419_5ef31ad35a1d5.png!small](https://image.3001.net/images/20200624/1592990419_5ef31ad35a1d5.png!small)

以及这个基于SSRF的钓鱼攻击，这里首先需要自架一个服务端，部署上伪造的Facebook登录页面：

![1592990447_5ef31aef14e73.png!small](https://image.3001.net/images/20200624/1592990447_5ef31aef14e73.png!small)

在<https://tinyurl.com/>中，将<http://ahmedabadexpress.co.in/fb/login/fb.html>生成tinyurl短域名：

![1592990460_5ef31afc8f625.png!small](https://image.3001.net/images/20200624/1592990460_5ef31afc8f625.png!small)

在以下链接的srcURL参数中插入生成的tinyurl短域名，然后发送给受害者：

[https://m-nexus.thefacebook.com/servlet/taskProc?taskId=shortURL&taskEnv=xml&taskContentType=json&srcURL=](https://m-nexus.thefacebook.com/servlet/taskProc?taskId=shortURL&taskEnv=xml&taskContentType=json&srcURL=){YOUR_TINY_URL_HERE}

![1592990486_5ef31b164e3f2.png!small](https://image.3001.net/images/20200624/1592990486_5ef31b164e3f2.png!small)

如果攻击者不小心上钩后，他输入的用户名密码将会存储到我服务器的<http://ahmedabadexpress.co.in/fb/login/usernames.txt>文件中，之后，再跳转到带m-nexus.thefacebook.com字串的真正的Facebook登录页面。

我在服务端访问以下文件<http://ahmedabadexpress.co.in/fb/login/usernames.txt>，即可看到钓鱼窃取来的受害者用户名密码信息：

![1592990511_5ef31b2f66958.png!small](https://image.3001.net/images/20200624/1592990511_5ef31b2f66958.png!small)

当然，作为攻击者来说，也可以利用该漏洞让受害者跳转到其它部署有恶意软件的恶意网站，实现感染类攻击。

探测Facebook内部架构或服务：

利用Burp Intruder发送枚举请求，可以探测出防火墙后运行于Facebook服务端的应用服务情况，如端口或应用名称等信息：

![1592990545_5ef31b51c659b.png!small](https://image.3001.net/images/20200624/1592990545_5ef31b51c659b.png!small)

比如，我在端口10303上发现了Facebook服务端的一个名为“LightRay”的应用服务：

![1592990563_5ef31b63b8bf0.png!small](https://image.3001.net/images/20200624/1592990563_5ef31b63b8bf0.png!small)

该漏洞上报后，Facebook安全团队迅速做了修复处理，赏金为$1000：

![1592990586_5ef31b7a82450.png!small](https://image.3001.net/images/20200624/1592990586_5ef31b7a82450.png!small)

## 好戏才刚刚开始

现在，在知道Facebook生产系统部署了MicroStrategy Web SDK后，我甚是欢喜，因为MicroStrategy Web
SDK是基于java的，而我喜欢发现java类漏洞。于是，我用JD Decompiler
工具对每个jar文件进行了反编译准备进行代码审计，另外，我还在我自架的网站上部署了MicroStrategy Web
SDK，如果有相应漏洞，也好进行验证。经过26天的钻研和折腾之后，我终于发现了一个有意思的线索。

在源码的“com.microstrategy.web.app.task.WikiScrapperTask”类中，当我们发送了作为用户输入的参数后，“str1”即被初始化，它会检查用户输入的URL字串中是否包含http://或https://，
如果有，然后会调用“webScrapper”方法。

![1592990632_5ef31ba82c18e.png!small](https://image.3001.net/images/20200624/1592990632_5ef31ba82c18e.png!small)

“webScrapper”方法会在后台用Java的HTML解析器JSOUP向用户输入的URL发送一个GET请求，以获取和解析其中的HTML页面：

![1592990649_5ef31bb94d6f5.png!small](https://image.3001.net/images/20200624/1592990649_5ef31bb94d6f5.png!small)

因此，最终它又可形成一个SSRF漏洞：

![1592990664_5ef31bc8db193.png!small](https://image.3001.net/images/20200624/1592990664_5ef31bc8db193.png!small)

![1592990671_5ef31bcfa1914.png!small](https://image.3001.net/images/20200624/1592990671_5ef31bcfa1914.png!small)

但不幸的是，这次是一个Blind SSRF，所以无法判断一些GET请求的有效性，但是，经对m-nexus.thefacebook.com网站部署的MicroStrategy Web
SDK研究后，我发现这是一个内部SSRF漏洞，因此无法像前述方法那样对Facebook内网架构执行枚举或探测，无实质危害性。如果就这样上报给Facebook安全团队后，肯定会被拒绝掉，那接下来怎么办呢？我也没辙了。

![1592990704_5ef31bf0ba795.png!small](https://image.3001.net/images/20200624/1592990704_5ef31bf0ba795.png!small)

到此，我把这个漏洞先放一放，然后转向研究Facebook主站域名 (facebook.com)漏洞。

## 转机再现

几个月之后，我在Facebook系统中发现了另外一个漏洞，它是Facebook
URL短址生成服务导致的敏感信息泄露漏洞。URL短址生成是通过大幅缩短统一资源定位字串的方式，来生成更短的URL链接，但最终的请求指向仍然不变。

Facebook有自己的短址生成方式，如<https://fb.me/>，该短址生成服务可供Facebook内部员工和公众用户使用，访问经其变化后的短址会直接跳转到相应的长址。另外，我还注意到Facebook短址“fb.me”缺乏速率限制措施（rate-limit），因此，我决定对其发起敏感目录或文件的暴力枚举，观察其响应中是否有值得注意的内容。在Burp
Intruder模块的帮助下，我捕捉到了几个Facebook短址链接，访问它们会跳转到Facebook的内部系统，然后，经由这些内部系统会再跳转到Facebook主站（facebook.com）。大致的跳转逻辑如下：

    
    
    https://fb.me/xyz==> 301 Moved Permanently —https://our.intern.facebook.com/intern/{some-internal-data} ==> 302 Found —https://www.facebook.com/intern/{some-internal-data} ==> 404 Not Found

注意，这里跳转到的Facebook内部系统链接，其中包含了很多敏感信息或数据，如“[https://our.intern.facebook.com/intern/webmanager?domain=xyz.com&user=admin&token=YXV0aGVudGljYXRpb24gdG9rZW4g](https://our.intern.facebook.com/intern/webmanager?domain=xyz.com&user=admin&token=YXV0aGVudGljYXRpb24gdG9rZW4g)"

具体示例如以下请求<https://fb.me/err>后，在响应内容中出现了很多internal敏感信息和日志记录：

![1592990771_5ef31c3309db3.png!small](https://image.3001.net/images/20200624/1592990771_5ef31c3309db3.png!small)

为此，我特意针对<https://fb.me/xyz>构造了一个字典列表和一个Python脚本，配合Intruder模块，发起了自动化请求。Python脚本如下：

![1592990783_5ef31c3f422a5.png!small](https://image.3001.net/images/20200624/1592990783_5ef31c3f422a5.png!small)

以下是请求发起后，从响应内容中获取的大量Facebook内部系统敏感信息：

![1592990798_5ef31c4e3c387.png!small](https://image.3001.net/images/20200624/1592990798_5ef31c4e3c387.png!small)

![1592990806_5ef31c56e6c31.png!small](https://image.3001.net/images/20200624/1592990806_5ef31c56e6c31.png!small)

出于Facebook保密策略，我这里只放了两张截图。该漏洞的危害在于可以泄露内部的HTTP
GET请求响应，导致日志文件件路径信息泄露，还可无需任何权限验证地对Facebook内部数据、内部IP、内部ID、配置信息、内部文件等发起请求。利用该漏洞，攻击者可以枚举Facebook当前系统中的有效内部URL链接。

## 漏洞综合利用

所以，现在来看，我手头上有两个漏洞了：

> 1、Blind SSRF，利用它可以提交针对Facebook内部和外部系统的请求；
>
> 2、服务端敏感信息泄露，可以看到的是Facebook内部的日志文件夹路径、文件路径、内部数据请求响应等数据信息。

我特意构建了一个场景，基于敏感信息泄露实现目录遍历和服务端请求伪造攻击（SSRF）。攻击者只要知晓内部IP地址，那么对内部网络系统的攻击也就相对简单了。

我连同PoC一起发送给了Facebook，收到的回复却是说涉及到的这些内部主机系统都是用来发送外部请求的，而且不能复现SSRF漏洞。我KAO。竟然漏洞无效。

![1592990868_5ef31c94aaf70.png!small](https://image.3001.net/images/20200624/1592990868_5ef31c94aaf70.png!small)

后来，过了几天，我发现Facebook已经悄悄修复了其中的blind
SSRF漏洞，而且之前的wikiScrapper任务方法调用已经无法利用了。我觉得这似乎不太公平，于是乎向Facebook安全团队发函质询：

![1592990901_5ef31cb570491.png!small](https://image.3001.net/images/20200624/1592990901_5ef31cb570491.png!small)

Facebook在给我的回复中声称，这不是它们的刻意修复，估计是其它不相关漏洞的连带修复，或组件更新导致的。

![1592990921_5ef31cc9f3cca.png!small](https://image.3001.net/images/20200624/1592990921_5ef31cc9f3cca.png!small)

太不幸了，是吧。

![1592990935_5ef31cd72df01.png!small](https://image.3001.net/images/20200624/1592990935_5ef31cd72df01.png!small)

## SSRF重现（$30000）

继续经过几天的研究后，我终于发现了另外一个Blind SSRF漏洞。从MicroStrategy web
SDK中，我确认这是一个SSRF漏洞，在“com.microstrategy.web.app.utils.usher”类的源代码中，我发现处理“serverURL”参数的方法“validateServerURL”
会向用户输入的URL链接发送一个GET请求。

![1592991048_5ef31d487b8e7.png!small](https://image.3001.net/images/20200624/1592991048_5ef31d487b8e7.png!small)

我用Burp Collaborator URL替换了请求链接中 “serverURL”后，得到的服务端响应如下：

![1592991065_5ef31d593fe16.png!small](https://image.3001.net/images/20200624/1592991065_5ef31d593fe16.png!small)

很快，Burp
Collaborator服务端就收到了来自Facebook请求的响应，响应中包含请求发起端的Facebook内部IP地址信息。SSRF无疑了。

![1592991099_5ef31d7b8b2b9.png!small](https://image.3001.net/images/20200624/1592991099_5ef31d7b8b2b9.png!small)

终于让Facebook安全团队如愿了，综合利用该漏洞同样可导致内部敏感信息泄露，他们也回复称漏洞可以复现，此处收获的赏金为$30000，WOW：

![1592991117_5ef31d8d22cc0.png!small](https://image.3001.net/images/20200624/1592991117_5ef31d8d22cc0.png!small)

## 另一个SSRF（$500）

接着，我想测试MicroStrategy演示门户网站中是否存在SSRF漏洞，又发现基于SSRF方式，请求MicroStrategy的AWS元数据API，可以从MicroStrategy服务端读取一些敏感信息，如以下SSRF请求链接<http://169.254.169.254/latest/user-data>后得到的响应信息：

![1592991166_5ef31dbe095ff.png!small](https://image.3001.net/images/20200624/1592991166_5ef31dbe095ff.png!small)

之后，我立马上报给了MicroStrategy安全团队，再次收获了$500的赏金。

![1592991220_5ef31df47950b.png!small](https://image.3001.net/images/20200624/1592991220_5ef31df47950b.png!small)

## 总结

原谅我写这么一篇writeup长文，目的在于让大家真正理解我的发现过程和思路。我综合利用代码审计、特定值枚举和脚本技巧最终发现了高危漏洞。当时我想构造发现Facebook的RCE漏洞，但他们的安全措施很到位。不管怎样，这三个漏洞让我收获了$31500
($1,000 + $30,000 + $500) 的奖励，相当值得。

**参考来源**

> [medium](https://medium.com/@win3zz/how-i-made-31500-by-submitting-a-bug-to-> facebook-d31bb046e204)

