# 谨防Magic SpEL - Part 1(CVE-2018-1273)

阅读量 **179103**

|评论 **2**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-06-20 16:29:09

 **x**

##### 译文声明

本文是翻译文章，文章来源：http://blog.h3xstream.com/

原文地址：<http://blog.h3xstream.com/2018/05/beware-of-magic-spell-part-1-cve-2018.html>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t0193330ca4b398af37.jpg)

## 前言

今年2月，我们使用一款安全漏洞扫描软件，在Spring Framework组件上至少扫描了100多个模块，包括核心部件(spring-core,
spring-mvc）和可选组件（spring-data, spring-social, spring-oauth等）。  
从这次扫描中，我们报告了一些漏洞。在这篇博客文章中，我们将详细介绍SpEL注入漏洞。尽管Twitter上已经出现了一些代码层的分析和漏洞利用分析，但我们这里将重点关注如何找到这些漏洞，然后对已提出的修补程序进行彻底审查。

## 初步分析

我们从MapDataBinder.java类中发现可疑表达式开始，这是由Find Security Bugs报告的SPEL_INJECTION模式标识。  
我们在表单提交时发现参数来自POST参数：propertyName

    
    
    public void setPropertyValue(String propertyName, @Nullable Object value) throws BeansException {
        if (!isWritableProperty(propertyName)) { // <---Validation here
            throw new NotWritablePropertyException(type, propertyName);
        }
        StandardEvaluationContext context = new StandardEvaluationContext();
        context.addPropertyAccessor(new PropertyTraversingMapAccessor(type, conversionService));
        context.setTypeConverter(new StandardTypeConverter(conversionService));
        context.setRootObject(map);
        Expression expression = PARSER.parseExpression(propertyName); // Expression evaluation
    

而对propertyName进行保护的方式是isWritableProperty方法的验证。跟一下代码，可以看到isWritableProperty方法会引起getPropertyPath的执行

    
    
    @Override
    public boolean isWritableProperty(String propertyName) {
    
        try {
            return getPropertyPath(propertyName) != null;
        } catch (PropertyReferenceException e) {
            return false;
        }
    }
    
    
    
    private PropertyPath getPropertyPath(String propertyName) {
    
        String plainPropertyPath = propertyName.replaceAll("\[.*?\]", "");
        return PropertyPath.from(plainPropertyPath, type);
    }
    

我们详细分析一下PropertyPath.from()，  
随后我们意识到其可以非常容易地绕过：由括号闭合的值将被忽略。凭借这些知识，攻击目标变得更加清晰。我们可能能够提交一个具有”parameterName[T(malicious.class).exec(‘test’)]”模式的变量名。

## 验证猜想

如果不将想法实现，那么它将毫无意义。在进行代码审计的时候，验证自己的猜想往往很困难。  
而第一步显然是要构建一个环境。我们使用了位于spring-data-examples库中的示例项目。  
在验证了表单之后，我们建立了以下请求并将其发送给HTTP代理。随后我们立即跟进分析，确认模块的可利用性：

    
    
    POST /users?size=5 HTTP/1.1
    Host: localhost:8080
    Referer: http://localhost:8080/
    Content-Type: application/x-www-form-urlencoded
    Content-Length: 110
    Connection: close
    Upgrade-Insecure-Requests: 1
    
    username=test&password=test&repeatedPassword=test&password[T(java.lang.Runtime).getRuntime().exec("calc")]=abc
    

![](https://p3.ssl.qhimg.com/t0147cbe9dd13cdb01f.png)

## 分析修复代码

我们可以在与bug ID DATACMNS-1264相关的比对中找到完整的修复代码。

    
    
    https://github.com/spring-projects/spring-data-commons/commit/613cf08f7255056a2a2d185b6e6c0f2c50534ed3#diff-524dd48a5ac084fe41ef505c143d8b8b
    

这就是为什么它可以被认为是真正有效的。  
虽然之前提出的攻击依赖于正则表达式的副作用，但实验中也发现了另一种风险：  
处理后的值被解析两次：一次用于验证，再一次用于执行。  
这是一个细微的细节，在执行代码审计时经常被忽略。攻击者可能会利用每个实现之间每一个字符差异。  
但是这仍然是理论上的，因为在这样的基础上，我们还没有发现可利用的方式  
同时Pivotal所做的更正也解决了这种可能在未来引入漏洞的双重解析风险。  
首先，使用更有限的表达式分析器（SimpleEvaluationContext）。  
然后在表达式被加载和执行时，对类型进行新的验证，  
同时isWritableProperty方法将被保留，但对象持久化映射层的安全性不再依赖它：

    
    
    public void setPropertyValue(String propertyName, @Nullable Object value) throws BeansException {
        [...]
        EvaluationContext context = SimpleEvaluationContext //
            .forPropertyAccessors(new PropertyTraversingMapAccessor(type, conversionService)) // NEW Type validation
            .withConversionService(conversionService) //
            .withRootObject(map) //
            .build();
    
        Expression expression = PARSER.parseExpression(propertyName);
    

## 我们的应用程序将会受影响吗？

大多数Spring开发人员采用Spring Boot来帮助依赖管理。如果是这种情况应尽快进行更新，以避免丢失重要的安全补丁或增加业务风险。  
如果由于任何原因您必须延迟更新，以下是利用此漏洞的具体条件：  
1.拥有版本1.13~1.13.10 / 2.0~2.0.5的spring-data-commons  
2.至少有一个接口用作表单（例如spring-data-examples项目中的UserForm）  
3.攻击者也可以访问受到影响的表单。

## 下期预告

正如标题所暗示的那样，本文将会有第二部分，因为在Spring OAuth2中发现了一个非常类似的漏洞。  
我们希望不管是否有相似之处，都将这两个漏洞分开，以避免与开发条件和不同payload混淆。  
您可能想知道除了Spring Framework本身之外，这些SpEL注入可能出现在哪里。您不太可能直接在Web应用程序逻辑中找到SpEL
API。我们的渗透安全团队只找到过一次这种情况。最可能出现的情况是审查类似于data-commons的其他Spring组件。  
这些检查可以很简单的添加到您的自动扫描工具中。如果您是Java开发人员或负责审计Java代码以确保安全的人员，则可以使用Find Security
Bugs（我们用来查找此漏洞的工具）扫描您的应用程序。  
正如本文中隐晦地演示的那样，虽然此工具可能有效，但是可利用性的确认仍需要对漏洞的复现来确认。  
我们希望这个博客对你有所帮助。也许，你很快就会发现类似的漏洞。

## 参考文献

<https://pivotal.io/security/cve-2018-1273>  
<https://github.com/find-sec-bugs/find-sec-bugs>

审核人：yiwang 编辑：边边

本文翻译自http://blog.h3xstream.com/
[原文链接](http://blog.h3xstream.com/2018/05/beware-of-magic-spell-part-1-cve-2018.html)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **一叶飘零** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/148374](/post/id/148374)

安全客 - 有思想的安全新媒体

本文转载自: [http://blog.h3xstream.com/](http://blog.h3xstream.com/2018/05/beware-of-magic-spell-part-1-cve-2018.html)

如若转载,请注明出处： <http://blog.h3xstream.com/2018/05/beware-of-magic-spell-part-1-cve-2018.html>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)
  * [CVE-2018-1273](/tag/CVE-2018-1273)
  * [java安全](/tag/java安全)
  * [Spring Framework](/tag/Spring Framework)

 **+1** __1赞

 __收藏

![](https://p0.ssl.qhimg.com/t0115eb10739cb26739.png) 一叶飘零

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

