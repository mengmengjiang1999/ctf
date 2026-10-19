***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

**![epa_britain_uber_transport_93988016.jpg](https://image.3001.net/images/20181126/1543216557_5bfb9dadf34ed.jpg!small)**

**大家好，今天我要分享的是一个影响20多个Uber子域名的XSS漏洞，该漏洞存在于uberinternal.com身份验证时向uber.onelogin.com的跳转过程中，漏洞最终获得了Uber官方$2500美金奖励。**

## 先导概念

文章开始前，我们需要先来了解一下安全断言标记语言SAML（Security Assertion Markup Language）。

SAML是一种基于XML的开源标准数据格式，它在当事方之间交换身份验证和授权数据，尤其是在身份提供者和服务提供者之间交换。SAML规范定义了三个角色：委托人（通常为一名用户）、身份提供者（IdP），服务提供者（SP）。在用SAML解决的使用案例中，委托人从服务提供者那里请求一项服务。服务提供者请求身份提供者并从那里并获得一个身份断言。服务提供者可以基于这一断言进行访问控制的判断——即决定委托人是否有权执行某些服务。

![15389191925301.png](https://image.3001.net/images/20181126/1543216024_5bfb9b9886310.png!small)在将身份断言发送给服务提供者之前，身份提供者也可能向委托人要求一些信息——例如用户名和密码，以验证委托人的身份。SAML规范了三方之间的断言，尤其是断言身份消息是由身份提供者传递给服务提供者。在SAML中，一个身份提供者可能提供SAML断言给许多服务提供者。同样的，一个服务提供者可以依赖并信任许多独立的身份提供者的断言。更多信息参考[SAML说明](https://developers.onelogin.com/saml)。

## 信息收集

在信息收集阶段，我发现Uber的内部系统网站uberinternal.com也在测试范围之内，于是，我就开始对它执行子域名枚举，该过程，我用到了子域名枚举神器aquatone，它发现了一堆子域名网站并作了截图。

值得注意的是，uberinternal.com的大多数子域名网站在身份验证阶段，都会跳转到uber.onelogin.com，而onelogin就是使用SAML验证的一个Uber服务。有意思的是，在SAML的应用中，存在很多验证被绕过的实例，这其中就包括了影响Uber自身服务的一些漏洞，如[实例1](https://hackerone.com/reports/223014)和[实例2](https://hackerone.com/reports/136169)。

首先，我计划来找找是否存在SAML身份验证绕过的情况，一开始我选的目标是Uchat系统，但是有人已经早我一步发现了这个漏洞，接下来，我只有改变目标了。

在登录uberinternal.com相关服务的过程中，会涉及到SAML验证，首先，SAML机制会向uber.onelogin.com后端验证服务发送一个请求，成功登录uberinternal.com服务后，uber.onelogin.com会返回一个有效响应。在此互动中，我感兴趣的是用来接收uber.onelogin.com响应的页面。

由此，可以来看看uberinternal.com在身份验证时发生页面跳转的情况，在下图中，可以看到，它向uber.onelogin.com传递了一个base64编码的SAMLRequest参数：

![01.png](https://image.3001.net/images/20181126/1543216095_5bfb9bdf2c753.png!small)为了解码这个base64请求参数，我们可以用[samltool](https://www.samltool.com/decode.php)这个在线工具中的SAML
Decoder功能，解码后，可以看到，其中包含了一个用来接收uber.onelogin.com响应的链接，也可称之为 SAML consume URL：

> <https://carbon-prototype.uberinternal.com:443/oidauth/saml_consume>

![02.png](https://image.3001.net/images/20181126/1543216201_5bfb9c4997f36.png!small)如果你还想深入测试一下这种跳转过程中发生的SAML交互，BurpSuite中就有一个专门用来测试SAML的插件，非常适合用来测试SAML。不过，最终我还是自己写了一个小工具
[SAMLExtractor](https://github.com/fadyosman/SAMLExtractor)，可以用它来解码提取出跳转发生时，用来接收响应的那个SAML
consume URL。  

接下来，我们要来尝试的就是绕过上述SAML consume
URL链接的SAML身份验证了，因为我不是太了解这种机制，所以我决定用以下[dirsearch](https://github.com/maurosoria/dirsearch)命令，来看看其oidauth目录下是否还有其它存在的子目录或文件：

> ./dirsearch.py -u <https://carbon-prototype.uberinternal.com:443/oidauth/>
> -ejson

## 漏洞发现

在经过一番暴力枚举之后，我发现oidauth目录下存在的以下这个页面：

> <https://carbon-prototype.uberinternal.com:443/oidauth/logout>

这是一个登录退出页面，为什么我觉得它有意思呢，因为很多web开发者会把这种退出页面用来实现重定向跳转，而且，有时候这种页面中可能会存在XSS漏洞。为此，当我在浏览器中打开上述页面链接之后，其又跳转到了以下这个页面：

> [https://carbon-> prototype.uberinternal.com/oidauth/prompt?base=https%3A%2F%2Fcarbon-> prototype.uberinternal.com%3A443%2Foidauth&return_to=%2F%3Fopenid_c%3D1542156766.5%2FSnNQg%3D%3D&splash_disabled=1](https://carbon-> prototype.uberinternal.com/oidauth/prompt?base=https%3A%2F%2Fcarbon-> prototype.uberinternal.com%3A443%2Foidauth&return_to=%2F%3Fopenid_c%3D1542156766.5%2FSnNQg%3D%3D&splash_disabled=1)

URL解码之后的链接如下：

> [https://carbon-> prototype.uberinternal.com/oidauth/prompt?base=https://carbon-> prototype.uberinternal.com:443/oidauth&return_to=/?openid_c=1542156766.5/SnNQg==&splash_disabled=1](https://carbon-> prototype.uberinternal.com/oidauth/prompt?base=https://carbon-> prototype.uberinternal.com:443/oidauth&return_to=/?openid_c=1542156766.5/SnNQg==&splash_disabled=1)

注意其中的base参数，它是用于获取另一个URL“carbon-prototype.uberinternal.com:443”的，但是，当我把它置换为经典的
javascript:alert(123)
之后，XSS出现了！不仅如此，这个页面还存在点击劫持漏洞（Clickjacking），在利用场景中，可以把XSS和Clickjacking一起配合，可更为方便地实现攻击。

##
![UberXSS.png](https://image.3001.net/images/20181126/1543216294_5bfb9ca6d157e.png!small)延伸发现

利用之前我编写的小工具SAMLExtractor中批量发现SAML consume
URL的功能，我把所有uberinternal.com的子域名网站都测试了一遍，看看是否还有其它子域名网站具备这种相同的调用机制。在我的改装脚本中，我会在验证方式中去调用存在XSS漏洞的页面
oidauth/prompt ，然后尝试javascript:alert(123)
的XSS漏洞，如果存在XSS，那么就会完美地跳出javascript:alert(123)内容了！

    
    
    import requests
    
    import urllib3
    
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    from colorama import init ,Fore, Back, Style
    
    init()
    
    with open("/home/fady/uberSAMLOIDAUTH") as urlList:
    
                for url in urlList:
    
                    url2 = url.strip().split("oidauth")[0] + "oidauth/prompt?base=javascript%3Aalert(123)%3B%2F%2FFady&return_to=%2F%3Fopenid_c%3D1520758585.42StPDwQ%3D%3D&splash_disabled=1"
    
                    request = requests.get(url2, allow_redirects=True,verify=False)
    
                    doesit = Fore.RED + "no"
    
                    if ("Fady" in request.content):
    
                        doesit = Fore.GREEN + "yes"
    
                    print(Fore.WHITE + url2)
    
                    print(Fore.WHITE + "Len : " + str(len(request.content)) + "   Vulnerable : " + doesit)

最终，我先发现了<https://eng.uberinternal.com>这个网站存在上述XSS漏洞[作了上报](https://hackerone.com/reports/354686)，之后，我又用这种方式发现了uberinternal.com下[20多个子域名网站存在上述XSS漏洞](https://hackerone.com/reports/326449)，两次漏洞报告先后分别获得了Uber官方奖励的$500和$2000美金。

更多信息，请参考原漏洞报告-[ report 1](https://hackerone.com/reports/354686) / [report
2](https://hackerone.com/reports/326449)

 ** ***参考来源：[fady](https://blog.fadyothman.com/how-i-discovered-xss-that-affects-over-20-uber-subdomains/)，clouds编译，转载请注明来自FreeBuf.COM** ****  
  
**

