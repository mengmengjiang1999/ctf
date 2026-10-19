# 【缺陷周话】第4期：XML 外部实体注入

阅读量 **222185**

发布时间 : 2018-10-08 18:00:25

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。XML 外部实体注入漏洞也就是我们常说的 XXE 漏洞。XML
作为一种使用较为广泛的数据传输格式，很多应用程序都包含有处理 xml 数据的代码，默认情况下，许多过时的或配置不当的 XML
处理器都会对外部实体进行引用。如果攻击者可以上传 XML 文档或者在 XML
文档中添加恶意内容，通过易受攻击的代码、依赖项或集成，就能够攻击包含缺陷的XML处理器。XXE 漏洞的出现和开发语言无关，只要是应用程序中对 xml
数据做了解析，而这些数据又受用户控制，那么应用程序都可能受到 XXE 攻击。本篇文章以 java 程序为例给大家介绍 XXE 漏洞的成因及修复。XXE
漏洞详细请见 CWE-611: Improper Restriction of XML External Entity Reference
(‘XXE’)(<http://cwe.mitre.org/data/definitions/611.html)>。

## 2、XML外部实体注入

XXE 漏洞可能会用于提取数据、执行远程服务器请求、扫描内部系统、执行拒绝服务攻击和其他攻击。业务影响主要取决于受影响的引用程序和数据保护需求。

2018年至今，CVE 中共有发布了 92 条漏洞信息与其相关。部分CVE如下：

CVE-2018-8027 | Apache Camel 2.20.0 到 2.20.3 和2.21.0 Core 在 XSD 验证处理器中存在 XXE
漏洞。  
---|---  
CVE-2018-13439 | 微信支付 Java SDK 中的 WXPayUtil 类中存在XXE漏洞。  
CVE-2018-1000548 | 在版本号小于 14.3 的 Umlet
中，在文件解析中存在XML外部实体注入漏洞，可能导致机密数据泄露、拒绝服务、服务器端请求伪造。此攻击可以通过特制的 UXF 文件进行攻击。  
CVE-2018-1364

| IBM Content Bavigator 2.0 和 3.0
版本中在处理XML数据时，易受XML外部实体（XXE）攻击。远程攻击者可以利用此漏洞暴露敏感信息或占用内存资源。  
  
## 3、示例代码

###  3.1 缺陷代码

本节使用示例代码来源为某开源支付 Java SDK
(<https://pay.weixin.qq.com/wiki/doc/api/jsapi.php?chapter=11_1)>，源文件名：WXPayUtil.java，文件路径为：java-sdk-v3\src\main\java\com\github\wxpay\sdk。

![](https://p3.ssl.qhimg.com/t0145e818f545f5f8f0.jpg)

在上述代码可以看到在25行处数据通过 xmlToMap 形参传入，数据未做任何过滤，且 XML
处理器也未做安全设置就在32行处对数据做了解析，而实际场景中，参数 strXML 也是受攻击者控制的，这样攻击者可能通过构造恶意的 strXML 来进行
XXE 攻击。

使用360代码卫士对上述示例代码进行检测，可以在文件第32行检出“有风险的XML外部实体注入”缺陷。如图1所示：

![](https://p5.ssl.qhimg.com/dm/1024_825_/t01f843cf9cd9a9cd20.jpg)

图1 检测出有风险的XML外部实体注入

### 3.2 修复代码

![](https://p3.ssl.qhimg.com/t012506e5ec1e38ff0e.jpg)

![](https://p3.ssl.qhimg.com/t01bc011b6d6388083d.png)

在上述修复代码中的第28行使用的是一个 xml 工具类 WXPayXmlUtil，用于生成一个安全的xml处理器。而 WXPayXmlUtil
类中最为关键的是第16行，通过 setFeature 让生成的 xml 处理器完全禁用
DTDS。通过图2可以看出，360代码卫士对修复后的代码并未检出缺陷。

![](https://p0.ssl.qhimg.com/t01500142ee2b9cc43d.jpg)

图2 XXE漏洞修复示例

## 4、如何避免 XXE 漏洞

常见的避免方法：

1、尽可能使用简单的数据格式（如：JSON），避免对敏感数据进行序列化。

2、及时修复或更新应用程序或底层操作系统使用的所有XML处理器和库。同时，通过依赖项检测，将 SOAP 更新到 1.2 版本或更高版本。

3、在应用程序的所有 XML 解析器中禁用XML外部实体和DTD进程，具体实现可以参考《OWASP Cheat Sheet ‘XXE
Prevention’》(<https://www.owasp.org/index.php/XML_External_Entity_(XXE)_Prevention_Cheat_Sheet)>，如下代码是
java 应用程序中使用DocumentBuilderFactory 解析 xml 时防范 XXE 漏洞的示例：

![](https://p5.ssl.qhimg.com/t0108a2de69a920880e.jpg)

4、输入校验：在服务器端使用白名单进行输入验证和过滤，以防在 XML 文档、标题或节点中出现恶意数据。

5、验证 XML 和 XSL 文件上传功能是否使用 XSD 验证或其他类似验证的方法来验证上传的 XML 文件。

6、DAST 工具需要额外的手动步骤来检查和利用 XXE 漏洞，而使用 ASAT 工具可以通过检测依赖项和安全配置来发现 XXE 漏洞。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **奇安信代码卫士** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/161177](/post/id/161177)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [代码审计](/tag/代码审计)
  * [360代码卫士](/tag/360代码卫士)
  * [安全缺陷](/tag/安全缺陷)

 **+1** __2赞

 __收藏

![](https://p4.ssl.qhimg.com/t015a32ce3696fa7636.png) 奇安信代码卫士

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

