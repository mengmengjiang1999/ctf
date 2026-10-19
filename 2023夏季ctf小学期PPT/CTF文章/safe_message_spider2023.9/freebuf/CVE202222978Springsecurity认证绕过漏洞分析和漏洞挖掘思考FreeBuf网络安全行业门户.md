## **前言**

在此之前，已经对CVE-2022-32532 Apache Shiro RegExPatternMatcher
认证绕过漏洞进行了分析，它和CVE-2022-22978漏洞产生原理上，本质是一样的。在分析这两个漏洞后，结合今年kcon议题[《自动化API漏洞Fuzz实战》](http://mp.weixin.qq.com/s?__biz=Mzg3NDcwMDk3OA==&mid=2247484068&idx=1&sn=89ea1b1be48a0cb7f93a4750765719d1&chksm=cecd8b79f9ba026f7fbf52771e41272d684fc3af5175587f768082f8dbaee12d6d33bb892ceb&scene=21#wechat_redirect)，产生了对漏洞挖掘关注点的一些思考。

#  **CVE-2022-22978 Spring-security RegexRequestMatcher 认证绕过漏洞分析**

###  **漏洞描述**

当Spring-security使用 RegexRequestMatcher
进行权限配置，由于RegexRequestMatcher正则表达式配置权限的特性，正则表达式中包含“.”时，未经身份验证攻击者可以通过构造恶意数据包绕过身份认证。

###  **影响版本**

Spring Security 5.5.x < 5.5.7

Spring Security 5.6.x < 5.6.4

###  **环境搭建**

使用github上的漏洞环境（https://github.com/XuCcc/VulEnv/tree/master/springboot/cve_2022_22978）

![](https://image.3001.net/images/20220907/1662522358_631813f6dd5914a049e34.png!small)

###  **漏洞分析**

具体漏洞产生的原理分析可参考[CVE-2022-32532 Apache Shiro RegExPatternMatcher
认证绕过漏洞](http://mp.weixin.qq.com/s?__biz=Mzg3NDcwMDk3OA==&mid=2247483864&idx=1&sn=6c02552494d488652ed20f20425854f1&chksm=cecd8805f9ba01130cbf0f11d0277eac9aee8a448132587f75041727915160ea27410a104fc8&scene=21#wechat_redirect)。

构造的漏洞应用场景。

创建一个Controller，自定义接口。

![](https://image.3001.net/images/20220907/1662522424_63181438bcb426754bae2.png!small)通过正则表达式添加认证配置。

![](https://image.3001.net/images/20220907/1662522812_631815bca876d5a6d7082.png!small)

在访问/admin/{name}接口时，需要认证才能访问。

因为之前对CVE-2022-32532 Apache Shiro RegExPatternMatcher
认证绕过的分析，此次很快就将漏洞点定位在spring-security-web-5.6.3.jar中。

org.springframework.security.web.uti.matcher.RegexRequestMatcher#matchers

![](https://image.3001.net/images/20220907/1662528359_63182b6710157270bf80f.png!small)

request.getServletPath()会对字符解码
并且会将;之后的字符到/字符删除，随后通过getServletPath获取URL，尝试提取？后的参数进行拼接，然后使用正则表达式匹配。

联想到在HttpServletRequest中URL解析函数中利用；进行权限绕过的场景：

其中HTTPServletRequest中对URL路径的几种解析方法。

    
    
    request.getRequestURL()：返回全路径；
    request.getRequestURI()：返回除去Host（域名或IP）部分的路径；
    request.getContextPath()：返回工程名部分，如果工程映射为/，则返回为空；
    request.getServletPath()：返回除去Host和工程名部分的路径；
    request.getPathInfo()：仅返回传递到Servlet的路径，如果没有传递额外的路径信息，则此返回Null；

当认证接口使用getRequestURI()或getRequestURL()函数来解析用户请求的URL时，若URL中包含了一些特殊符号，如分号；就可能产生限制绕过。

而在spring-security中，存在StrictHttpfirewall机制默认对特殊字符进行过滤，所以使用/admin/..;/1这种方式也就无法绕过。

![](https://image.3001.net/images/20220907/1662528438_63182bb69c280d0225a9a.png!small)不过在之前分析shiro认证绕过也提到，在正则表达式中元字符“.”是匹配除换行符（\n、\r）之外的任何单个字符，在java中的正则默认情况下“.”也同样不会包含\n、\r字符，所以RegexRequestMatcher在进行正则匹配时不会处理\n、\r

![](https://image.3001.net/images/20220907/1662528624_63182c703959f398c837e.png!small)在spring-security中利用换行符可实现权限认证进行绕过，\r的URl编码为%0d，\n的URL编码为%0a

![](https://image.3001.net/images/20220907/1662528641_63182c81b712af731d843.png!small)这样的绕过方式也和CVE-2022-32532
Apache Shiro RegExPatternMatcher 认证绕过如出一辙。

###  **漏洞复现**

访问/admin/1会302跳转至登陆页面进行权限验证。

![](https://image.3001.net/images/20220907/1662528685_63182cadc33651d390a13.png!small)使用/admin/1%0d%0a，成功绕过登陆认证。

![](https://image.3001.net/images/20220907/1662528707_63182cc3d0ed95197fd57.png!small)

#  **漏洞挖掘的思考**

因为我自己是在分析了CVE-2022-32532后再分析CVE-2022-22978，也在用正则匹配流量的过程中发现过正则“.”号不匹配换行符的问题，在拜读了CVE-2022-32532发现者分析文章，了解了其发现漏洞的过程。

![](https://image.3001.net/images/20220907/1662529261_63182eed03ae8d9c4e3e5.png!small)

##  **高效的漏洞挖掘方法**

从漏洞分析的角度来讲，CVE-2022-32532
和CVE-2022-22978的原理其实很简单，那从漏洞发现和挖掘上看，在了解了类似于CVE-2022-22978这样的安全漏洞后或者是其他的过程发现一些特性，拓展到其他框架或组件中去寻找类似的安全问题，构造利用场景，这是无疑一种高效挖洞的方法。一些未知由语言特性、机制特性等引发的安全漏洞，也等着我们去发现和研究。

在这样的背景下，结合今年KCon《自动化API漏洞Fuzz实战》议题介绍的自动化API漏洞
Fuzz方案，让我觉得API由于本身的特性和发展，以及产生的安全问题，也会逐渐成为漏洞挖掘中一个重要的关注点。

##  **API特性与发展**

简单介绍下，API本质上是一种跨语言、跨架构的数据传输约定，API连接了不同层次、不同编程语言、不同厂商 所研发的软件，让数据可以跨应用软件进行自由流动。

![](https://image.3001.net/images/20220907/1662529299_63182f139b2f9ad67c806.png!small)API本身的概念，这里不用做过多介绍。大多数人关注API安全可能在于数据隐私保护方面，这也是API安全近几年崛起的主要原因之一，对于攻击者而言，攻击API从而获取系统权限或者数据的成本也是极低的。

![](https://image.3001.net/images/20220907/1662529364_63182f54c2f7ebdea5f38.png!small)看得出API也在这个万物互联互通的时代正高速发展。

##  **浅谈自动化API Fuzz到高危漏洞挖掘**

API本身的会存在涉及到各种安全风险，而其大部分安全问题可进阶利用，产生危害更大的安全问题。

![](https://image.3001.net/images/20220907/1662529577_631830299bbe7c183ea60.png!small)

通过自动化API
fuzz，发现API的安全漏洞，再对这些漏洞可以进一步挖掘和利用，例如通过API未授权漏洞、权限绕过、安全性错误配置等，进一步挖掘文件上传、命令执行等等漏洞。

API Fuzz流程。

![](https://image.3001.net/images/20220907/1662529596_6318303c39d9935d53bc1.png!small)

当然，通过API
Fuzz挖掘漏洞在SRC挖掘的过程中，同样适用。具体可参考https://mp.weixin.qq.com/s/MCtwiT93Fo9Js9ekuD-8wA中的实际案例。

在如今安全研究漏洞挖掘卷到飞起的天下，挖掘高危漏洞，安全研究员除了自身扎实的基础、丰富的漏洞经验外，可能有时还需要一点运气或灵感。通过自动化API
Fuzz去挖掘新的高危漏洞的方式，也可以成为一个新的卷点。

![](https://image.3001.net/images/20220907/1662529654_63183076b5b6196d7bc5f.png!small)

##  **参考材料**

>
> 1.https://mp.weixin.qq.com/s?__biz=Mzg3NDcwMDk3OA==∣=2247484068&idx=1&sn=89ea1b1be48a0cb7f93a4750765719d1&chksm=cecd8b79f9ba026f7fbf52771e41272d684fc3af5175587f768082f8dbaee12d6d33bb892ceb&scene=126&&sessionid=1662041689#rd
>
> 2.https://xz.aliyun.com/t/11501#toc-2
>
> 3.https://mp.weixin.qq.com/s/GiQJj2iD3ta8ltsHX9fYJw
>
> 4.https://github.com/XuCcc/VulEnv/tree/master/springboot/cve_2022_22978

