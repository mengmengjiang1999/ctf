![](https://image.3001.net/images/20191014/1571023912_5da3ec28b8c65.jpg!small)

**由于博主近期在学习spring的安全知识，那么不得不接触到spring
security相关漏洞。在cve上的spring相关漏洞列表里，一眼就看到了这个漏洞——Spring Security OAuth 2.3 Open
Redirection(CVE-2019–3778)，既然如此凑巧，那博主就决定研究一下，网上搜了一下，具体的分析没找到（可能是姿势不对），就想着自己写一篇留作记录。**

根据官方（<https://pivotal.io/security/cve-2019-3778>）的注解，先解释一下漏洞详情吧。

## 漏洞篇

### 漏洞描述

恶意攻击者可以构造一个请求，发送给使用“授权码“类型授权的终点上，并且通过“redirect_uri”参数控制跳转的URI。这可以导致授权服务器将资源所有者用户代理重定向到被攻击者控制的URI，从而泄漏授权码。鉴于oauth2协议的特殊认证机制，该漏洞定位到Medium。

### 影响产品

> Spring Security OAuth 2.3 to 2.3.4
>
> Spring Security OAuth 2.2 to 2.2.3
>
> Spring Security OAuth 2.1 to 2.1.3
>
> Spring Security OAuth 2.0 to 2.0.16
>
> Older unsupported versions are also affected

## Spring Security OAuth 简介篇：

### 什么是 oAuth？

oAuth 协议为用户资源的授权提供了一个安全的、开放而又简易的标准。与以往的授权方式不同之处是 oAuth
的授权不会使第三方触及到用户的帐号信息（如用户名与密码），即第三方无需使用用户的用户名与密码就可以申请获得该用户资源的授权，因此 oAuth 是安全的。

### 什么是 Spring Security？

Spring Security 是一个安全框架，前身是 Acegi Security，能够为 Spring
企业应用系统提供声明式的安全访问控制。Spring Security 基于 Servlet 过滤器、IoC 和 AOP，为 Web
请求和方法调用提供身份确认和授权处理，避免了代码耦合，减少了大量重复代码工作。

### oAuth的使用场景

![](https://image.3001.net/images/20191014/1571023271_5da3e9a79ec1a.jpg!small)

### oAuth协议的授权模式

oAuth2.0标准中客户端必须得到用户的授权（authorization grant），才能获得令牌（access token）。oAuth 2.0
定义了四种授权方式：

 **简化模式**

简化模式适用于纯静态页面应用。所谓纯静态页面应用，也就是应用没有在服务器上执行代码的权限（通常是把代码托管在别人的服务器上），只有前端 JS 代码的控制权。

 **授权码模式**

授权码模式适用于有自己的服务器的应用，它是一个一次性的临时凭证，用来换取 access_token 和
refresh_token。认证服务器提供了一个类似这样的接口：

[](https://www.funtl.com/exchange?code=&client_id=&client_secret=)

    
    
    [https://www.funtl.com/exchange?code=&client_id=&client_secret=](https://www.funtl.com/exchange?code=&client_id=&client_secret=)

 **密码模式**

密码模式中，用户向客户端提供自己的用户名和密码。客户端使用这些信息，向 "服务商提供商"
索要授权。在这种模式中，用户必须把自己的密码给客户端，但是客户端不得储存密码。这通常用在用户对客户端高度信任的情况下，比如客户端是操作系统的一部分。

 **客户端模式**

如果信任关系再进一步，或者调用者是一个后端的模块，没有用户界面的时候，可以使用客户端模式。鉴权服务器直接对客户端进行身份验证，验证通过后，返回 token。

Oauth的授权流程如下：

![](https://image.3001.net/images/20191012/1570878900_5da1b5b4df59f.jpg!small)

## 复现篇

### 1.限制条件

> 有问题的Spring Security OAuth2版本
>
> oAuth认证使用授权码模式
>
> 用户需要在登录的情况下

### 2.搭建靶机

（靶机自建 ），设置两个应用程序（客户端和认证服务器），启用oauth2做登录认证。相关资料

> <https://github.com/spring-projects/spring-security-oauth/releases>
>
> <https://github.com/oktadeveloper/okta-spring-boot-authz-server-example>

靶机如下：

![](https://image.3001.net/images/20191012/1570878945_5da1b5e1efb05.jpg!small)

### 3.靶机使用oauth的版本（存在漏洞的版本）

![](https://image.3001.net/images/20191012/1570878960_5da1b5f020ede.jpg!small)

### 4.检查漏洞代码

代码中obtainMatchingRedirect方法在检查参数的时候存在问题

> 包：org.springframework.security.oauth2.provider.endpoint
>
> 类：DefaultRedirectResolver
>
> 方法：obtainMatchingRedirect

![](https://image.3001.net/images/20191012/1570878971_5da1b5fb22ae7.jpg!small)

### 5.测试内容

用户登录后，CLIENT APP执行的以下请求包含REDIRECT_URI参数。只需添加一个百分号即可触发重定向bypass认证机制

5.1 源请求包含了有效的URI如下：

![](https://image.3001.net/images/20191012/1570879060_5da1b6549c3db.jpg!small)

5.2 攻击者通过修改redirect_uri参数为[http://www.baidu.com](http://www.baidu.com/)
并发送请求，oAuth捕捉到了认证参数有问题，返回结果如下

![](https://image.3001.net/images/20191012/1570879087_5da1b66f9cec9.jpg!small)

5.3 此时在修改的 redirect_uri 中加上“%”，再次发送，如下：

![](https://image.3001.net/images/20191012/1570879097_5da1b6799850e.jpg!small)

5.4 此刻认证被绕过，用户被重定向了，返回结果如下：

![](https://image.3001.net/images/20191012/1570879121_5da1b69109fd1.jpg!small)

修复：

> 2.3.xusers should upgrade to2.3.5
>
> 2.2.xusers should upgrade to2.2.4
>
> 2.1.xusers should upgrade to2.1.4
>
> 2.0.xusers should upgrade to2.0.17
>
> Older versions should upgrade to a supported branch

## 个人总结

问题的关键点在于obtainMatchingRedirect方法在获取到用户输入redirect_url参数时对参数对校验机制不够严谨，未对“%”这类的特殊字符进行处理，最终导致此类bypass认证的出现。所以，建议各位大牛在自己实现oauth协议的时候，对于接收到的来自用户的参数多加检查，最后送大家一句话：Never
believe users ！！！

### 参考文档：

> <https://pivotal.io/security/cve-2019-3778>
>
> <https://www.exploit-db.com/exploits/47000>
>
> <https://cve.mitre.org/cgi-bin/cvekey.cgi?keyword=spring>
>
> <https://blog.csdn.net/vbirdbest/article/details/92071480>
>
> <https://github.com/spring-projects/spring-security-oauth/releases>
>
> <https://github.com/oktadeveloper/okta-spring-boot-authz-server-example>

 ***本文作者：Bman，转载请注明来自FreeBuf.COM**

