# Jenkins Nested View插件XXE漏洞（CVE-2021-21680）分析

阅读量 **131951**

|评论 **2**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-09-08 15:30:56

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t0148d3f9f405b3b108.jpg)

## 0x01 前言

逆推这个漏洞本身不难，主要记录下思路。

先看下漏洞描述：  
该插件 1.20 及更早版本未配置其 XML 转换器以防止 XML 外部实体 (XXE) 攻击。这使攻击者能够配置视图，让 Jenkins
解析精心设计的视图 XML 定义，该定义使用外部实体从 Jenkins 控制器或服务器端请求伪造中提取秘密。  
该插件 1.21 禁用了其 XML 转换器的外部实体解析。

根据漏洞描述可以提取关键信息：

  1. XXE漏洞
  2. 漏洞出现在配置视图处

## 0x02 分析

Jenkins在github提交了修复代码，[修复后的版本和1.19.1对比](https://github.com/jenkinsci/nested-view-plugin/commit/79787294f034b3009c3de557c6441c9ceba936b8)如下图。定位代码修改处，主要是updateByXml方法添加限制对指外部DTD的访问来进行修复。

![](https://p2.ssl.qhimg.com/t01c1a2735e2a4fef30.png)

updateByXml方法在doConfigDotXml中被调用。当请求方法时GET时会将NestedView作为XML数据返回，当请求方法是POST时，执行`updateByXml((Source)new
StreamSource(req.getReader()))`将请求数据作为Source进行XML解析。那么我们只需要请求的时候设置HTTP
method为POST，就可以对NestedView进行更新，然后用GET方法来读取。

![](https://p4.ssl.qhimg.com/t01bf8a812a3af1b353.png)

入口具体的api在哪里？在[这个链接](https://issues.jenkins.io/browse/JENKINS-8927?page=com.atlassian.jira.plugin.system.issuetabpanels%3Acomment-tabpanel&showAll=true)找到了-`/user/view/viewname/config.xml`。现在我们只要更新config.xml文件就能调用doConfigDotXml方法，那么xml文件的内容就能够传入到请求流从而进行解析。

![](https://p2.ssl.qhimg.com/t01885a703633068f31.png)

现在的问题是怎么构造xml文件？既然能通过GET获取XML数据，我们可以在页面创建一个nested view，通过查看历史创建的nested
view的config.xml文件就能够来构造我们想要的XML。

![](https://p4.ssl.qhimg.com/t019f006c8124be39d4.png)

现在只要在nested view的config.xml文件中插入dtd，就可以达到我们的目的：

    
    
    <!DOCTYPE description [
    <!ENTITY description SYSTEM "file:///E:/111.txt">]>
    

另外需要注意，Jenkins配置了crumb来防御CSRF攻击，所以请求的时候在url后面加上`Jenkins-Crumb`，`Jenkins-Crumb`的值可以通过api`/crumbIssuer/api/json`获取。

![](https://p5.ssl.qhimg.com/t0160cd6754cac153ff.png)

## 0x03 总结

此次漏洞主要通过补丁对比反推漏洞，漏洞本身不复杂。首先根据描述提取关键信息比如什么漏洞类型、大致的漏洞位置，根据补丁修复代码，反推出漏洞。该漏洞是一个典型XXE漏洞，通过TransformerFactory使用了默认的解析方法，没有对dtd禁止。

    
    
    StreamSource source = new StreamSource(req.getReader());
    Transformer t = TransformerFactory.newInstance().newTransformer();
    t.transform(source, new StreamResult(out));
    

下面是TransformerFactory解析xml防御XXE漏洞的典型方法，禁止外部DTD。

    
    
    factory.setFeature(XMLConstants.FEATURE_SECURE_PROCESSING, true);
    factory.setAttribute(XMLConstants.ACCESS_EXTERNAL_DTD, "");
    factory.setAttribute(XMLConstants.ACCESS_EXTERNAL_STYLESHEET, "");
    

除了TransformerFactory，在Java中还有许多XML解析工具，如果需要防御XXE漏洞，基本都是通过禁用DTD及外部实体来解决的。

    
    
    DocumentBuilder
    XMLStreamReader
    SAXBuilder
    SAXParser
    SAXReader
    XMLReader
    SAXSource
    SAXTransformerFactory
    ......
    

## 0x04 参考链接

[https://issues.jenkins.io/browse/JENKINS-8927?page=com.atlassian.jira.plugin.system.issuetabpanels%3Acomment-tabpanel&showAll=true](https://issues.jenkins.io/browse/JENKINS-8927?page=com.atlassian.jira.plugin.system.issuetabpanels%3Acomment-tabpanel&showAll=true)  
<https://www.jenkins.io/security/advisory/2021-08-31/>  
<https://github.com/jenkinsci/nested-view-plugin/commit/79787294f034b3009c3de557c6441c9ceba936b8>  
<https://www.apiref.com/java11-zh/java.xml/javax/xml/XMLConstants.html>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **R17a** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/252564](/post/id/252564)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [XXE](/tag/XXE)
  * [Jenkins](/tag/Jenkins)
  * [CVE-2021-21680](/tag/CVE-2021-21680)

 **+1** __0赞

 __收藏

![](https://p3.ssl.qhimg.com/t01247f7d4151cd618c.png) R17a

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

