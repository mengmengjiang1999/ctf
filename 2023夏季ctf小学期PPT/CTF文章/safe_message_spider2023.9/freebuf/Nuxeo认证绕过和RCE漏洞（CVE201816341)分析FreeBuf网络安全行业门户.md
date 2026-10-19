***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

>
> 本文介绍的两个漏洞由笔者发现并提交给官方，CVE编号为：CVE-2018-16341。有趣的是在官方10.3版本的发布日志中并没有提及该漏洞(CVE-2018-16341)，但实际已被修复。  
>

## 简介

Nuxeo Platform是一款跨平台开源的企业级内容管理系统(CMS)。

nuxeo-jsf-ui组件处理facelet模板不当，当访问的facelet模板不存在时，相关的文件名会输出到错误页面上，而错误页面会当成模板被解析，文件名包含表达式也会被输出同时被解析执行，从而导致远程代码执行漏洞。

在漏洞挖掘过程中发现nuxeo-jsf组件默认在10.2没有安装，历史版本是默认就安装的。可以通过nuxeoctl mp-install nuxeo-jsf-ui 命令安装。

## 影响范围

> Nuxeo Server版本 < 10.3

## 漏洞复现

通过在官网下载Nuxeo 10.2的安装包在本地安装，使用默认密码登陆Administrator/Administrator。

在登陆状态下访问test${11*11}.xhtml，可以看到表达式被执行

![01.png](https://image.3001.net/images/20181226/15458131885249.png!small)

## 执行系统命令

Nuxeo 是构建在Seam Framework之上的,
Seam是由Jboss开发的Web应用程序框架，在前几年比较流行，但依然有很多应用程序使用了Seam。

当用EL来执行任意系统命令时，Seam内部对EL的解析有一定的防护，用下面的Payload可绕过。

>
> ${"".getClass().forName("java.lang.Runtime").getMethod("getRuntime",null).invoke(null,null).exec("calc",null).toString()}  
>

![02.png](https://image.3001.net/images/20181226/15458132634811.png!small)

## 认证绕过

在不登陆的情况下，是无法访问facelet模板的，如果需要登陆才能命令执行，漏洞略显得有点鸡肋。发现可以通过

login.jsp/%24%7b%31%31%2a%31%31%7d.xhtml 绕过访问。

![03.png](https://image.3001.net/images/20181226/15458132932838.png!small)

## 认证绕过分析

通过查看web.xml配置文件，开发者为*.xhtml资源注册了名为NuxeoAuthenticationFilter的过滤器和Faces
Servlet。凭借经验认证工作应该在filter处理。

通过调试发现，在NuxeoAuthenticationFilter类中的bypassAuth方法中有相关逻辑

![04.png](https://image.3001.net/images/20181226/15458133176408.png!small)

进入到该方法中，unAuthenticatedURLPrefix是一个列表，值为["login.jsp","webservices/"]
，requestPag 只要以 unAuthenticatedURLPrefix 数组中的字符串开头就不会验证用户身份。

![05.png](https://image.3001.net/images/20181226/15458133423622.png!small)

根据注册的Faces Servlet规则”*.html”， login.jsp/test.xhtml
肯定是匹配的，如果要对资源进行访问控制肯定要先进入到访问控制逻辑中的，但是访问控制逻辑中只是通过startsWith方法来比较的，肯定也是符合的，所以login.jsp/test.xhtml这个路径可以绕过NuxeoAuthenticationFilter认证控制进入到Faces
Servlet（模版相关）中。

可能会问，那我使用/webservices/xx.xhtml是不是也可以绕过呢？答案是不可以。对/webservices/*资源注册了另一个Servlet，一个请求只能被一个Servlet处理，这个注册方式优先级更高。

## RCE 分析

先来一张案发现场的图，is变量含有用户可控的内容进入到了parse方法中。

![06.png](https://image.3001.net/images/20181226/15458133687553.png!small)

src的handler为NuxeoNotFoundResourceHandler，看下实现，

![07.png](https://image.3001.net/images/20181226/15458133841774.png!small)

getInputStream中的错误信息中包含表达式，也会进入parse方法中执行，
即请求的路径不存在时将会把路径当成源内容返回给调用者，这里就会进入到模版的parse方法中，然后就被解析执行了。

![08.png](https://image.3001.net/images/20181226/15458134035145.png!small)

## 补丁分析

>
> <https://github.com/nuxeo/nuxeo/commit/eb54a9145c6d8297eba9d7dafc74556e735fa388#diff-> cf2094833ef0eea473d03bf6559f1798R97>

这是通过过滤的方式修复的，在getInputStream中，只有当路径中不包含”#”和”$”时才会把路径输出到输入流中，这样就无法执行EL了。

![09.png](https://image.3001.net/images/20181226/15458134357244.png!small)

## 参考链接

> <https://doc.nuxeo.com/nxdoc/nuxeo-jsf-ui/>
>
> <http://blog.orange.tw/2018/08/how-i-chained-4-bugs-features-into-rce-on-> amazon.html>
>
> <https://github.com/nuxeo/nuxeo>

作者：斗象能力中心 TCC - 星光

