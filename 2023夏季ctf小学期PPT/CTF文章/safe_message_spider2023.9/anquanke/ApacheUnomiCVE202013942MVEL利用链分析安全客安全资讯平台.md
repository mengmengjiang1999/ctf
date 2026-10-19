# Apache Unomi CVE-2020-13942 MVEL利用链分析

阅读量 **245646**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-12-23 16:30:11

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t015a73d6ddc7c471ab.jpg)

## Apache Unomi介绍

Apache Unomi具有隐私管理、用户/事件/目标跟踪、报告、访客资料管理、细分、角色、A/B测试等功能，可以作为Web
CMS、个性化服务、原生移动应用的分析服务、具有分段功能的集中配置文件管理系统、授权管理中心。

## 漏洞介绍

CVE-2020-13942是CVE-2020-11975的绕过  
该漏洞描述的是Unomi针对MVEL表达式（和OGNL表达式）的未进行敏感函数的过滤，直接解析，导致任意代码执行

本文主要对MVEL这条利用链做代码层面的分析

## poc请求包

漏洞利用时相关的Poc请求包如下，后续代码分析会涉及到

![](https://p2.ssl.qhimg.com/t0131c00420d6ae85a5.png)

## 分析思路

MVEL表达式解析的模式有两种，分别是

  * 解释模式`MVEL.eval(expression, vars)`
  * 编译模式`MVEL.compileExpression(expression) + MVEL.executeExpression(compiled, vars)`

具体可以参考：[MVEL解析表达式](https://wsygoogol.github.io/2016/11/15/MVEL%E8%A7%A3%E6%9E%90%E8%A1%A8%E8%BE%BE%E5%BC%8F/)

###  倒推分析

通过在源码中搜索关键字`script::`与`MVEL.executeExpression(`可以初步定位出现问题的代码位于源码的如下位置

    
    
    unomi-unomi-root-1.5.1\persistence-elasticsearch\core\src\main\java\org\apache\unomi\persistence\elasticsearch\conditions\ConditionContextHelper.java
    

我们构造的恶意表达式就是通过这条代码进行解析从而导致RCE的

![](https://p4.ssl.qhimg.com/t01dfec8bba88f1d103.png)

基于此方法向上回溯，找调用它的地方

![](https://p2.ssl.qhimg.com/t014212e901aadd51f6.png)

继续向上回溯

![](https://p4.ssl.qhimg.com/t01919977be4eb3c77e.png)

看到`condition.getParameterValues()`基本可以确定我们的思路是正确的

接下来主要找入口点，即往`/context.json`这个路径下发送数据是如何一步一步到`ConditionContextHelper#getContextualCondition()`的

向上回溯`getContextualCondition()`有三处调用到

![](https://p2.ssl.qhimg.com/t018e3f6772112a16ff.png)

几个方法分别是`buildFilter()`、`count()`、`eval()`，因为看到poc里有关键字`filter`，所以先跟入`buildFilter()`，看看是不是从这里进来的

![](https://p4.ssl.qhimg.com/t01211df5db4af883b0.png)

接着向上回溯，看`buildFilter()`的调用位置

![](https://p2.ssl.qhimg.com/t0108364253f92371d6.png)

最终回溯到的位置（即入口位置）位于`ElasticSearchPersistenceServiceImpl`重写的`excute()`方法中

![](https://p1.ssl.qhimg.com/t011b6c050c166d7b61.png)

看完`buildFilter()`，然后接着看`eval()`（`count()`方法作用不大，忽略）  
`eval()`最终回溯到的位置（即入口位置）位于`ElasticSearchPersistenceServiceImpl`重写的`testMatch()`方法中

然后只需要找出调用如下两个方法的位置就可以找到完整的调用链

    
    
    ElasticSearchPersistenceServiceImpl#excute()
    ElasticSearchPersistenceServiceImpl#testMatch()
    

###  正推分析

接下来我开始从请求的入口处开始进行分析  
在docker环境中找到了如下jar包

    
    
    unomi-wab-1.5.1.jar
    

这个jar包包含了处理web的逻辑，其对应着的源码包是

    
    
    unomi-unomi-root-1.5.1/wab
    

里面的`contextServlet.class`对应着我们请求的`/context.json`  
该类继承了`HttpServlet`类，且无`doGet()`和`doPost()`方法，但是有用于处理请求的`service()`方法

> 注：`service()`此方法是接收http-request请求的原始方法，请求会发送到这个方法然后才会向`doGet()`或`doPost()`分发

![](https://p4.ssl.qhimg.com/t01ca7684b28ffe0a0b.png)

这里的`contextRequest`就是我们poc传入的body（可以根据`getSessionId`等方法以及响应数据判断出来）

接着这里会将`contextRequest`作为参数传入`handleRequest()`

![](https://p2.ssl.qhimg.com/t01be30f03f180cf12a.png)

接着看到355行

![](https://p1.ssl.qhimg.com/t0143c16ec98cbfd745.png)

在执行`getFilters()`后，拿到的应该是如下部分

![](https://p5.ssl.qhimg.com/t0155357fc5de8385ab.png)

之后进入for循环，比较重要的是有一个`personalizedContent`对象，这个类的数据结构如下：

![](https://p4.ssl.qhimg.com/t01d56f3b30ed954265.png)

正好对应着我们上图传入的内容

然后跟进359行的`personalizationService.filter()`方法

> 注：personalizationService是interface，我们知道，接口不可以实例化。但是接口对象可以指向它的实现类对象。

所以这里的`filter()`应该是其Impl类的`filter()`方法，所以我们跟进位于源码包

    
    
    unomi-unomi-root-1.5.1\services\src\main\java\org\apache\unomi\services\impl\profiles\ProfileServiceImpl.java
    

的`filter()`方法

![](https://p1.ssl.qhimg.com/t01dbd0f3da8661efc8.png)

然后跟进67行的`profileService.matchCondition()`也在同一个源码包下

![](https://p1.ssl.qhimg.com/t01b9882402cfcf1e72.png)

在781行出现了最关键的`persistenceService.testMatch()`，而上半段分析的`ElasticSearchPersistenceServiceImpl`正好是`persistenceService`唯一的实现类

至此，整个调用链已经打通，我们整理一下调用链

###  调用链整理

    
    
    org.apache.unomi.web.ContextServlet#service() -> org.apache.unomi.web.ContextServlet#handleRequest() -> org.apache.unomi.services.impl.personalization.PersonalizationServiceImpl#filter() -> org.apache.unomi.services.impl.profiles.ProfileServiceImpl#matchCondition() -> org.apache.unomi.persistence.elasticsearch.ElasticSearchPersistenceServiceImpl#testMatch() -> org.apache.unomi.persistence.elasticsearch.conditions.ConditionEvaluatorDispatcher#eval() -> org.apache.unomi.persistence.elasticsearch.conditions.ConditionContextHelper#getContextualCondition() -> org.apache.unomi.persistence.elasticsearch.conditions.ConditionContextHelper#parseParameter() -> org.apache.unomi.persistence.elasticsearch.conditions.ConditionContextHelper#executeScript()
    

最终被`executeScript()`的

    
    
    MVEL.executeExpression(mvelExpressions.get(script), context);
    

解析执行

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Aview** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/261766](/post/id/261766)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [表达式注入](/tag/表达式注入)
  * [Apache Unomi](/tag/Apache Unomi)
  * [CVE-2020-13942](/tag/CVE-2020-13942)

 **+1** __5赞

 __收藏

![](https://p3.ssl.qhimg.com/t01b160c52790a76b7b.png) Aview

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

