# 武装你的BurpSuite

阅读量 **224885**

发布时间 : 2022-03-28 14:30:42

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t01da0a25ed6311c794.png)

## 0x01 前言

BurpSuite是广大安全人员使用率最高的一款工具了，通过对数据包的修改，重放往往能发现很多安全问题，而burp的插件能帮助我们进一步优化使用体验，更好的去发现漏洞。下面是经常用到的插件，这里给大家做一个分享。

## 0x02 信息收集插件

###  2.1 HAE

项目地址：<https://github.com/gh0stkey/HaE>  
介绍：一款通过自定义正则的方式匹配响应报文或请求报文，提取获取敏感信息的插件  
使用方式：导入插件，初始规则有很多，可以根据自身需求定制

###  2.2 Domain Hunter

项目地址：<https://github.com/bit4woo/domain_hunter_pro>  
介绍：快捷的目标管理、自动化的信息收集工具，可以从流量中提取子域名，相关域名，邮箱，java包名。批量获取子域名相关信息，还有一些小工具。  
使用方式：导入插件，添加新项目

![](https://p1.ssl.qhimg.com/t01096c03abf0ee8b1e.png)

添加根域，就可以开始使用了

![](https://p2.ssl.qhimg.com/t0147c1f17153df36d5.png)

里面还有很多小功能，可以自行尝试。

###  2.3 CaA

项目地址：<https://github.com/gh0stkey/CaA>  
介绍：主要作用就是收集流经BurpSuite
Proxy模块中的HTTP流量，并从流量中提取一些有价值的信息，它可以帮助你记录这些信息并统计每个信息字段出现的频次，这些信息可以用于接口、参数、目录等相关的枚举工作  
使用方式：导入插件，配置数据库。

![](https://p0.ssl.qhimg.com/t01129858808ff9471a.png)

自动启用，查询时注意需要输入完整域名，Param：参数表，file：文件表，Endpoint：末尾的接口表，FullPath：完整目录表，Path：一级目录表。

![](https://p2.ssl.qhimg.com/t01e10f23b86517e700.png)

## 0x03 漏洞挖掘插件

###  3.1 fastjsonscan

项目地址：<https://github.com/zilong3033/fastjsonScan>  
介绍：自动扫描fastjson漏洞的插件

###  3.2 shiroscan

项目地址：<https://github.com/pmiaowu/BurpShiroPassiveScan>  
介绍：自动扫描shiro漏洞的插件

###  3.3 log4jscan

项目地址：<https://github.com/f0ng/log4j2burpscanner>  
介绍：自动扫描log4j2漏洞的插件

###  3.4 jwt

项目地址：<https://github.com/ozzi-/JWT4B>  
介绍：测试jwt相关漏洞，可以在官方插件库直接安装

###  3.5 APIKit

项目地址：<https://github.com/API-Security/APIKit>  
介绍：可以主动/被动扫描发现应用泄露的API文档，并将API文档解析成BurpSuite中的数据包用于API安全测试  
现阶段支持  
GraphQL  
OpenAPI-Swagger  
SpringbootActuator  
SOAP-WSDL

###  3.6 J2EEScan

项目地址： <https://github.com/ilmila/J2EEScan>  
介绍： J2EE 应用程序漏洞扫描插件，可以在官方插件库直接安装

## 0x04 辅助插件

###  4.1 403bypass

项目地址：<https://github.com/sting8k/BurpSuite_403Bypasser>  
介绍：用python编写的用来测试绕过403的插件，自动扫描

###  4.2 chunked-coding-converter

项目地址：<https://github.com/c0ny1/chunked-coding-converter>  
介绍：主要用于分块传输绕WAF

###  4.3 hackbar

项目地址：<https://github.com/d3vilbug/HackBar>  
介绍：和火狐插件hackbar类似，提供了一些payload，可以在官方插件库直接安装

![](https://p2.ssl.qhimg.com/t017ae8376f188df52c.png)

## 0x05 后记

除了上面的插件，burp还有许多优秀的插件，都是师傅们在日常挖掘漏洞的经验总结，帮助我们更好的对目标进行测试，但漏洞挖掘终究还是以人为本，多多测试自然能看出哪些参数和路由会存在什么问题，继而去发现验证。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **雷石安全实验室** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/270770](/post/id/270770)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [BurpSuite](/tag/BurpSuite)

 **+1** __14赞

 __收藏

![](https://p2.ssl.qhimg.com/t01ebe472d127128939.png) 雷石安全实验室

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

