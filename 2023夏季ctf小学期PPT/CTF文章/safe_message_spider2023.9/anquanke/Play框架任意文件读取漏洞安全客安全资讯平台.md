# Play框架任意文件读取漏洞

阅读量 **286185**

|评论 **1**

发布时间 : 2018-07-20 15:25:21

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t0119c893408a5c56ee.jpg)

## 简介

360 Redteam在研究区块链项目过程中，发现某区块链项目API使用了Play
Framework框架进行构建网站，我们对该框架进行审计后发现一处通用型漏洞，该框架处理静态文件资源路径不当，在Windows环境下可导致任意文件读取漏洞。

Play
Framework是一个开源Star10k+的Web应用框架，使用Scala和Java语言混合编写。该框架具有可扩展、资源消耗低等特点。我们发现该框架涵盖客户人群包括游戏公司EA、领英、沃尔玛、三星等多家知名公司。同时我们发现部分区块链钱包项目中也使用到了该框架，该漏洞可能会导致窃取钱包秘钥等问题。

## 漏洞编号

CVE-2018-13864

## 发现团队

360 RedTeam & 0keeTeam

## 影响范围

Play Framework 2.6.12-2.6.15

## 漏洞详情

首先我们在Play Framework的 routes 文件中可以看到静态资源解析路由的配置信息

    
    
    # Map static resources from the /public folder to the /assets URL path GET /assets/*file controllers.Assets.at(path="/public", file)

该路由调用 controllers.Assets.at 函数将 /assets/* 指向文件目录 /public
，即可解析该目录中的CSS、JS文件等。跟踪controllers.Assets.at 函数

漏洞文件：/framework/src/play/src/main/scala/play/api/controllers/Assets.scala

跟踪 assetAt 函数

这里使用 resourceNameAt 函数获取标准化的文件名，跟踪该函数

resourceNameAt 函数首先会将文件路径进行URL解码，然后将 path 与 decodedFile进行拼接然后通过
removeExtraSlashes 函数将双斜杠//替换成单斜杠/，拿到最终的绝对路径。

但是后面有路径标准化判断，会判断文件路径标准化后的前缀是否为 /public/ ，跟踪一下 fileLikeCanonicalPath 函数看看都干了什么

该函数中以“/”为分隔符将路径进行分隔，然后对数组进行遍历，如果碰到“..”就删除前一个数组元素，达到标准化路径

既然代码中是以“/”分隔，在Windows环境中，我们可以使用反斜杠“\”进行绕过，这样不会删掉前面目录，达到跨目录的效果，而且前缀依然是
/public/，满足标准化路径的判断。

我们发现在Scala版与Java版均受该漏洞影响。

## 漏洞利用

我们在官网下载了Scala版的聊天室Demo（<https://github.com/playframework/play-scala-chatroom-example/tree/2.6.x>），在Windows下使用sbt运行该源码。

![](https://i.imgur.com/hc4o8pC.png)

抓取一个静态文件，然后找到项目编译后对应的文件路径

构造payload，读取项目目录中的 build.sbt 文件试试，这个文件正常是访问不到的。

400报错，查了一下发现是akka http不允许特殊符号，那我们进行URL编码

成功跨目录读取到了其他文件。

## 修复方案

升级到Playframework >=2.6.16版本

## 时间线

2018-07-10 360 Redteam报告Playframework官方人员  
2018-07-11 Playframework官方确认漏洞  
2018-07-17 Playframework发布2.6.16版本，修复此漏洞

## 参考链接

<https://www.playframework.com/security/vulnerability/CVE-2018-13864-PathTraversal>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **0keeTeam** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/152476](/post/id/152476)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)
  * [Play框架](/tag/Play框架)
  * [CVE-2018-13864](/tag/CVE-2018-13864)
  * [360 RedTeam &amp; 0keeTeam](/tag/360 RedTeam &amp; 0keeTeam)

 **+1** __5赞

 __收藏

![](https://p5.ssl.qhmsg.com/dm/200_200_100/t00df551a583a87f4e9.jpg) 0keeTeam

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

