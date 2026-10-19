# API声明文件Swagger Injection攻击

阅读量 **324344**

发布时间 : 2021-12-30 17:29:39

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t017cf26554dbe12ead.jpg)

## Swagger

在API化的世界里，相信无论是前端还是后端开发，都或多或少地被接口维护折磨过。随着API迭代，老旧API文档和SDK需要更新，这是一个耗散研发精力的事情。为解决此类问题，以API为软件能力最终交付物的生态不断演进，最终形成了工具+流程的一套解决方案。通过这套方案，研发人员只需要按照既定的规范去定义接口，再通过Swagger衍生出来的一系列项目和工具，就可以做到生成各种格式的接口文档，生成多种语言的客户端和服务端的代码，以及在线接口调试页面等等。

![](https://p2.ssl.qhimg.com/t01af310638fa27c27a.png)

在传统service交付模式中，上游供应商提供SDK，开发者下载SDK并植入自己的项目代码中，以调用上游service的能力，在以API为最终交付物的软件生态中，上游仅维护API的正常功能并通过API声明文件的方式对外暴露API的接入方式，下游企业通过这份API格式声明自动化生成多语言的SDK进行集成，这一过程通过自动化的手段大大提高了应用间集成的效率。

![](https://p3.ssl.qhimg.com/t015258af0f311e546c.png)

## Swagger Injection

swagger API声明文件包含了API的接入方式、参数定义及格式。样例：

![](https://p0.ssl.qhimg.com/t017032cd1e6a60dbb3.png)

前文中提到，上游供应商交付这份API声明文件之后，下游企业自动化解析该声明生成SDK的过程会出现代码注入问题，经过笔者的一些测试，通过向swagger
json中注入payload，可以成功污染SDK的代码，并在API client运行时触发RCE，具体流程如下：

![](https://p5.ssl.qhimg.com/t0150b07f1244a1be93.png)

## Swagger-codegen代码注入

在上述API交付流程中，下游企业通过swagger自动化生成代码的工具项目很多，其中以官方swagger-codegen为代表被广泛集成于各种api-automation流程中。

![](https://p1.ssl.qhimg.com/t01d4257812dcaf8f91.png)

构造恶意swagger definition

![](https://p4.ssl.qhimg.com/t017db8b75beaf55009.png)

生成SDK中携带恶意代码

![](https://p3.ssl.qhimg.com/t017210a4c3774c92d0.png)

## Restler-fuzzer代码注入

![](https://p4.ssl.qhimg.com/t013bab19f350d2b586.png)

restler-fuzzer是MS开源的一款在CI过程中API自动化测试工具，该工具在compile阶段解析swagger声明生成python
request SDK，然后在test/fuzz阶段通过python内置类控制request的参数和结构变化，从而达到黑盒测试bug和安全漏洞的目标。

在swagger解析过程中通过构造特定参数向中间态python文件中植入代码。

![](https://p5.ssl.qhimg.com/t01d6fd27a599840192.png)

针对fuzzer的online service，可以通过提交特定swagger直接RCE。

![](https://p4.ssl.qhimg.com/t0154f8574a9a34c72d.png)

## 总结

提供一种以swagger为输入点的攻击思路，API开发者生态中的swagger to
code阶段主流工具存在代码注入风险，开发者应将API声明文件视作不可信输入源对待，并在自动化代码生成环节添加相应的安全管控手段。

![](https://p2.ssl.qhimg.com/t01c9a44bdd469711c2.png)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **星阑科技** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/264276](/post/id/264276)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全](/tag/安全)
  * [API](/tag/API)
  * [Swagger Injection](/tag/Swagger Injection)

 **+1** __0赞

 __收藏

![](https://p0.ssl.qhimg.com/t01ae1a72a720da3a7b.png) 星阑科技

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

