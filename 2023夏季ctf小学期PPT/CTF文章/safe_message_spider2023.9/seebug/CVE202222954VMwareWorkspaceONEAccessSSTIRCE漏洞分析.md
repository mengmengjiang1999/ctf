**作者：xxhzz@星阑科技PortalLab  
原文链接：<https://mp.weixin.qq.com/s/PDxbQKm7CLRjjlA4d-55kA>**

# **前言**

4月6日和5月18日，VMware官方发布的两则安全公告中显示，关乎旗下产品的CVE漏洞多达10个，其中不乏有CVSSv3评分9.8的高危漏洞！如此高频的出洞速率，吸引了笔者注意。继上篇[CVE-2022-22972
VMware Workspace ONE Access
身份认证绕过漏洞分析](http://mp.weixin.qq.com/s?__biz=Mzg3NDcwMDk3OA==&mid=2247483810&idx=1&sn=48063cb1d5271a9b9668a6848be09c2e&chksm=cecd887ff9ba016909849b0e941f69f409d547ca94389a37f50dec9d7dccfa537368c673fb33&scene=21#wechat_redirect)之后，笔者将对CVE-2022-22954
VMware Workspace ONE Access SSTI RCE 漏洞进行细致分析。

![图片](https://images.seebug.org/content/images/2022/11/25/1669358055000-1bxfqr.png-w331s)

# **漏洞描述**

根据4月6日VMware官方发布的安全公告，官方已更新解决了多个产品的安全问题。其中CVE-2022-22954，CVSS评分为9.8，危害等级为严重。该漏洞是由于VMware
Workspace ONE Access and Identity Manager
包含一个服务器端模板注入漏洞，导致具有网络访问权限的恶意攻击者可进行远程代码执行。

![图片](https://images.seebug.org/content/images/2022/11/25/1669358056000-2yepoj.png-w331s)

# **利用范围**

  * VMware Workspace ONE Access 21.08.0.1, 21.08.0.0，20.10.0.1, 20.10.0.0

  * VMware Identity Manager（vIDM） 3.3.6, 3.3.5, 3.3.4, 3.3.3

  * VMware vRealize Automation(vIDM) 7.6

  * VMware Cloud Foundation (vIDM) 4.x

# **漏洞分析**

根据freemarker官网文档（<https://freemarker.apache.org/docs/ref_builtins_expert.html#ref_builtin_eval>）中给出了安全问题的提示。

使用内置函数将字符串计算为 FTL 表达式，FTL 表达式可以访问变量，并调用 Java 方法，例如 "1+2"?eval将返回数字
3，所以`?eval`前的字符串因来自不受信任的来源，可能就会成为攻击媒介。

![图片](https://images.seebug.org/content/images/2022/11/25/1669358056000-3zjiza.png-w331s)

在Vmware中的endusercatalog-ui-1.0-SNAPSHOT-classes.jar自带的模板customError.ftl就调用了freemarker引擎的eval函数来渲染errObj，这就导致了本次SSTI注入漏洞。

![图片](https://images.seebug.org/content/images/2022/11/25/1669358057000-4jpeio.png-w331s)

## **环境搭建**

可参考[CVE-2022-22972 VMware Workspace ONE Access
身份认证绕过漏洞分析](http://mp.weixin.qq.com/s?__biz=Mzg3NDcwMDk3OA==&mid=2247483810&idx=1&sn=48063cb1d5271a9b9668a6848be09c2e&chksm=cecd887ff9ba016909849b0e941f69f409d547ca94389a37f50dec9d7dccfa537368c673fb33&scene=21#wechat_redirect)。

本次漏洞分析源码所在位置：/opt/vmware/horizon/workspace/webapps/catalog-portal/WEB-INF/lib。

![图片](https://images.seebug.org/content/images/2022/11/25/1669358057000-5qjuif.png-w331s)

## **动态调式**

已经定位到安全问题所在，接下来寻找渲染customError.ftl模板的相关代码。

在com.vmware.endusercatalog.ui.web.UiErrorController#handleGenericError函数中。

![图片](https://images.seebug.org/content/images/2022/11/25/1669358058000-6qkkil.png-w331s)

errorObj由参数传入。

查找handleGenericError函数的被调用关系发现。

![图片](https://images.seebug.org/content/images/2022/11/25/1669358058000-7ofgmw.png-w331s)

handleGenericError函数受如上图所示的两个requestMapping所在的控制器UiErrorController调用。

跟进其中出现的getErrorPage函数，位于com.vmware.endusercatalog.ui.web.UiErrorController#getErrorPage。

![图片](https://images.seebug.org/content/images/2022/11/25/1669358059000-8yoefz.png-w331s)

除了直接用handleGenericError函数拿到需要渲染的模板，还存在handleUnauthorizedError函数通过条件判断，只有一个分支进入handleGenericError

如何构造参数？

在两个requestMapping中，其中的/ui/view/error为API接口，直接访问无法从请求中提取javax.servlet.error.message，从而无法控制errorObj。

寻找/ui/view/error的其他调用，位于com.vmware.endusercatalog.ui.web.UiApplicationExceptionResolver#resolveException函数。

![图片](https://images.seebug.org/content/images/2022/11/25/1669358059000-9gxoxw.png-w331s)

存在对javax.servlet.error.message赋值的过程。

查看resolveException函数的被调用关系，受上方handleAnyGenericException函数调用。

![图片](https://images.seebug.org/content/images/2022/11/25/1669358060000-10hgedu.png-w331s)

其中@ExceptionHandler表明，该处为异常处理器，当程序直接抛出Exception类型的异常时会进入handleAnyGenericException，再通过调用resolveException函数，进行赋值，最终都会返回/ui/view/error。

而在 handleAnyGenericException 中，进入 resolveException 时会根据异常的类型传入不同的参数，如果异常类不是
LocalizationParamValueException 子类的话则传入
uiRequest.getRequestId()，所以我们需要构造参数可控的地方还需要抛出 LocalizationParamValueException
异常类或其子类异常，这样errorObj所需Attribute
errorJson来自LocalizationParamValueException异常的getArgs。

![图片](https://images.seebug.org/content/images/2022/11/25/1669358060000-11enjvx.png-w331s)

在LocalizationParamValueException函数，如果可以控制抛出异常的参数，就可以把payload传入errorObj。

![图片](https://images.seebug.org/content/images/2022/11/25/1669358060000-12ekrsu.png-w331s)

在endusercatalog-auth-1.0-SNAPSHOT.jar中com.vmware.endusercatalog.auth.InvalidAuthContextException，存在一个InvalidAuthContextException异常，继承于LocalizationParamValueException。

![图片](https://images.seebug.org/content/images/2022/11/25/1669358061000-13tktgz.png-w331s)

在com.vmware.endusercatalog.auth.AuthContext构造函数中抛出异常。

![图片](https://images.seebug.org/content/images/2022/11/25/1669358061000-14sjosw.png-w331s)

生成 AuthContext对象的地方在AuthContextPopulationInterceptor
拦截器中，而且各项参数均是从请求中获取，这里可构造注入点。

但正常情况下，在 endusercatalog-auth-1.0-SNAPSHOT.jar 中的拦截器类无法访问到类。

但在com.vmware.endusercatalog.ui.UiApplication，使用 @ComponentScan
注解声明自动将com.vmware.endusercatalog.auth包的类装配进bean容器。

![图片](https://images.seebug.org/content/images/2022/11/25/1669358061000-15yxvxl.png-w331s)

在包中com.endusercatalog.ui.config.WebConfig可查找到。

![图片](https://images.seebug.org/content/images/2022/11/25/1669358062000-16thyhv.png-w331s)

可进行构造的url。

![图片](https://images.seebug.org/content/images/2022/11/25/1669358062000-17elgcu.png-w331s)

通过如上分析，可构造payload，进行命令执行。

![图片](https://images.seebug.org/content/images/2022/11/25/1669358062000-18abfdf.png-w331s)

## **漏洞复现**

![图片](https://images.seebug.org/content/images/2022/11/25/1669358063000-19tbqvs.png-w331s)

# **修复建议**

参考漏洞影响范围进行排查，目前官方已发布修复补丁：

<https://kb.vmware.com/s/article/88099>

# **参考材料**

1.<https://www.vmware.com/security/advisories/VMSA-2022-0011.html>

2.<https://cve.mitre.org/cgi-bin/cvekey.cgi?keyword=vmware>

3.<https://mp.weixin.qq.com/s/X_E0zWONLVUQcgP6nZ78Mw?scene=21#wechat_redirect>

4.<https://mp.weixin.qq.com/s/zVYQQgDjcwJKAnX8SZJ5Cw>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/2026/>

