# SpringCloud Function SpEL漏洞环境搭建+漏洞复现

阅读量 **228698**

|评论 **1**

发布时间 : 2022-03-30 10:30:09

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t0112d942ebf88ada57.jpg)

## 漏洞概述

Spring Cloud Function 是基于Spring Boot
的函数计算框架（FaaS），该项目提供了一个通用的模型，用于在各种平台上部署基于函数的软件，包括像 Amazon AWS Lambda 这样的
FaaS（函数即服务，function as a
service）平台。它抽象出所有传输细节和基础架构，允许开发人员保留所有熟悉的工具和流程，并专注于业务逻辑。

在版本3.0.0到当前最新版本3.2.2(commit dc5128b)，默认配置下，都存在Spring Cloud Function
SpEL表达式注入漏洞。

## 漏洞复现

在IDEA中选择新建项目，然后选择`Spring Initializr`，输入随机项目名称，然后选择java版本和jdk版本后点击下一步。

![](https://p3.ssl.qhimg.com/t014ad7ca04e105f14a.png)

选择`Spring Web`和`Function`作为依赖项，点击完成。

![](https://p2.ssl.qhimg.com/t01f223d0a7e8e5d674.png)

漏洞环境就搭建完成。因当前官方还未发布新版本，所以最新版本3.2.2也是存在漏洞的，若在官方出新版本后想要复现此漏洞，那么需要修改pom中`spring-cloud-function-web`的版本为3.2.2，如下图所示：

![](https://p3.ssl.qhimg.com/t016d5625ecbd70f3c4.png)

确认项目中的`spring-cloud-function-web`是存在漏洞版本后，就可以直接启动项目了，无需进行任何修改。

![](https://p5.ssl.qhimg.com/t015fd9f6aeda218827.png)

然后对本地8080端口发送payload即可。

![](https://p5.ssl.qhimg.com/t01634b1cc53120d3b3.png)

## 漏洞分析

先看git提交记录，<https://github.com/spring-cloud/spring-cloud-function/commit/0e89ee27b2e76138c16bcba6f4bca906c4f3744f>
，在提交描述中，明确指出修复了`RoutingFunction` SpEL代码注入漏洞，并且可以看到目前只更新了两个文件，其中一个文件仅为单元测试。

![](https://p4.ssl.qhimg.com/t01522cefda7b0e078b.png)

在测试用例中也清楚写明了漏洞位置以及相关测试Payload。

![](https://p5.ssl.qhimg.com/t011e3578785e4c8587.png)

通过测试用例可知，在给`Spring Cloud
Function`的web服务发送包的时候，加一个相关的Header信息，然后跟入SpEL表达式即可执行命令。

![](https://p1.ssl.qhimg.com/t01f1a7b331349072a2.png)

在文件`org.springframework.cloud.function.context.config.RoutingFunction`中，请求进入到`apply`方法，接着调用了`route`方法，然后通过判断特定的消息头信息是否为空，如果不为空则调用`functionFromExpression`方法。

![](https://p0.ssl.qhimg.com/t01f3fe721d30091a7e.png)

![](https://p3.ssl.qhimg.com/t01d46052bc57dbf113.png)

因调用到了SpEL对`routingExpression`进行解析，从而导致了SpEL表达式注入。

![](https://p3.ssl.qhimg.com/t017dedcad7a520d92e.png)

整个逻辑中由于完全信任从最开始传入的header信息，并且在解析SpEL表达式时候的`evalContext`使用的是功能更强同时安全隐患较大的`StandardEcalutionContext`

![](https://p2.ssl.qhimg.com/t01714fc156cfb94015.png)

在官方最新的修补文件中，可以看到新增了`headerEvalContext`对象，该对象所对应的是使用了仅支持最基本功能的`SimpleEvaluationContext`。

![](https://p3.ssl.qhimg.com/t01004d5f90c6c85c39.png)

且在调用`functionFromExpression`方法的时候新增了一个`isViaHead`布尔类型的参数，用来判断该值是否是取自消息的`header`中，如果是则使用`headerEvalContext`对象来解析SpEL表达式。

![](https://p5.ssl.qhimg.com/t01b807211758180f0a.png)

## 修复建议

目前SpringCloud Function官方已针对此漏洞进行修复，但还没有发布正式版本，可拉取最新修复代码重新编译打包进行临时修补。  
墨云科技建议您在升级前做好数据备份工作，避免出现数据丢失等问题。  
官方已发布修复补丁参考地址：<https://github.com/spring-cloud/spring-cloud-function/commit/0e89ee27b2e76138c16bcba6f4bca906c4f3744f>

**了解更多相关信息，请关注公众号“墨云安全”，关注更智能的网络攻防。**

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **VLab** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/271167](/post/id/271167)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)
  * [Java](/tag/Java)

 **+1** __6赞

 __收藏

![](https://p1.ssl.qhimg.com/t0155c2022df9e4d96d.png) VLab

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

