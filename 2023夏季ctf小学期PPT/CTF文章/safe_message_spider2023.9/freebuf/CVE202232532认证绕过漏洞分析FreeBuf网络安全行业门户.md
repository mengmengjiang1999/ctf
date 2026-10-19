## **前言**

结合自身经历，在使用正则表达式去匹配流量特征时，由于正则表达式中元字符“.”不匹配换行符（\n、\r）导致一直提取不上所需的流量。而如今，之前踩过的坑却出现在了Apache
Shiro框架之中......

##  **漏洞描述**

6月29日，Apache 官方披露 Apache Shiro 权限绕过漏洞(CVE-2022-32532)，当 Apache Shiro 中使用
RegexRequestMatcher 进行权限配置，且正则表达式中携带“.”时，未经授权的远程攻击者可通过构造恶意数据包绕过身份认证。

##  **相关介绍**

Apache Shiro 是一个功能强大且易于使用的 Java
安全框架，它可以执行身份验证、授权、加密和会话管理，可以用于保护任何应用程序——从命令行应用程序、移动应用程序到最大的 web 和企业应用程序。

##  **利用范围**

Apache Shiro < 1.9.1

##  **漏洞分析**

###  **环境搭建**

这里使用此漏洞提交者4ra1n 师傅的漏洞demo（https://github.com/4ra1n/CVE-2022-32532）进行复现分析。

###  **漏洞原理**

在漏洞分析之前，先了解一下相关漏洞产生原理。

在正则表达式中元字符`.`是匹配除换行符（`\n`、`\r`）之外的任何单个字符。

![](https://image.3001.net/images/20220707/1657172958_62c673de0f2b70fc660fc.png!small)要匹配包括
\n 在内的任何字符，需使用像(.|\n)的模式。

![](https://image.3001.net/images/20220707/1657172987_62c673fbc4b44cccc6c04.png!small)结合4ra1n师傅的分析，在java中的正则默认情况下.也同样不会包含\n、\r字符，因此在一些场景中，使用正则.的规则就有可能被绕过。

![](https://image.3001.net/images/20220707/1657173014_62c67416d10e535891da5.png!small)新增Pattern.DOTALL模式后，正则表达式.就可以匹配任何字符包括换行符。

![](https://image.3001.net/images/20220707/1657173052_62c6743c1428bfc7f3ccf.png!small)

###  **源码分析**

结合shiro源码和漏洞场景分析，在shiro-core-1.9.0.jar中存在一个RegExPatternMatcher类

org.apache.shiro.util.RegExPatternMatcher.class。

![](https://image.3001.net/images/20220707/1657173076_62c674541ea09dc547a0d.png!small)

RegexRequestMatcher和AntPathMatcher类似，提供请求路径匹配功能及拦截器参数解析的功能。而一般情况下RegexRequestMatcher类是不会在项目中出现，需要用户自己配置。

分析RegexRequestMatcher用于匹配的代码。

![](https://image.3001.net/images/20220707/1657173097_62c6746918f8fef880079.png!small)

可以看到，这里正如上面漏洞原理分析的一样，pattern存在带.的正则表达式匹配，若source中存在\r或\n字符时，将判断错误。

而在4ra1n师傅构造的漏洞场景中。

![](https://image.3001.net/images/20220707/1657173121_62c6748181794dafe3872.png!small)

自定义了Filter，增加权限认证场景：

1、判断请求头中的Token是否匹配。

2、如果不存在Token或者Token头错误则认为认证失败。

并且配置了自定义的AccessControlFilter实现类，并将 PatternMatcher配置为RegExPatternMatcher。

同时自定义MyShiroFilterFactoryBean。

![](https://image.3001.net/images/20220707/1657173145_62c67499b14f86353434c.png!small)继承自ShiroFilterFactoryBean类；设置匹配规则为/permit/.*字符串，表示需要拦截/permit/下所有的路径。

![](https://image.3001.net/images/20220707/1657173165_62c674ade023afd9eb06b.png!small)

在自定义controller中，配置了/permit/{value}这样从路径取参数的路由和/permit/*这样的通配路由。

###  **漏洞复现**

当访问/permit/any，返回拒绝访问。

![](https://image.3001.net/images/20220707/1657173192_62c674c883f5841a74d1c.png!small)![](https://image.3001.net/images/20220707/1657173201_62c674d156b52eaef643d.png!small)![](https://image.3001.net/images/20220707/1657173214_62c674de2f27cf6d37217.png!small)![](https://image.3001.net/images/20220707/1657173227_62c674ebc7d429dcfa3fb.png!small)

所以在如上满足使用了RegExPatternMatcher类，设置带有.的正则表达式等条件的场景下，利用该漏洞可实现权限认证绕过。

##  **修复建议**

参考漏洞影响范围进行排查，目前官方已发布修复补丁：https://github.com/apache/shiro/commit/6bcb92e06fa588b9c7790dd01bc02135d58d3f5b

##  **参考材料**

![](https://image.3001.net/images/20220707/1657173308_62c6753c12f75d61ac242.png!small)

