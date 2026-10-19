# Discuz ML! V3.X 代码注入漏洞深度分析

阅读量 **402723**

|评论 **15**

发布时间 : 2019-07-12 16:30:20

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t01e9f6f7b8cb5e4990.jpg)

作者：Alpha 天融信阿尔法实验室

## 0x00 前言

Discuz！ML是一个由CodersClub.org创建的多语言，集成，功能齐全的开源网络平台，用于构建像“社交网络”这样的互联网社区。

该引擎基于Comsenz Inc.创建的着名的Discuz！X引擎开发。

![](https://p5.ssl.qhimg.com/t013695ce3221495954.png)

## 0x01 漏洞描述

2019年7月11日，
Discuz！ML被发现存在一处远程代码执行漏洞，攻击者通过在请求流量的cookie字段中的language参数处插入构造的payload，进行远程代码执行利用，该漏洞利用方式简单，危害性较大。

本次漏洞是由于Discuz! ML对于cookie字段的不恰当处理造成的

cookie字段中的language参数未经过滤，直接被拼接写入缓存文件之中，而缓存文件随后又被加载，从而造成代码执行

简而言之，如下图流程可以简单的理解该漏洞

首先，通过cookie传入payload，构造好的payload被写入template文件中

![](https://p0.ssl.qhimg.com/t012085cd2d69a77f2e.png)

接着，这个被插入payload的template.php文件被include，造成代码执行

![](https://p5.ssl.qhimg.com/t01a11b63fdba5f8f78.png)

## 0x02 受影响的系统版本

Discuz! ML v.3.4

Discuz! ML v.3.3

Discuz! ML v.3.2

## 0x03 漏洞分析

本次漏洞是由于Discuz! ML于对于cookie字段的不恰当处理造成的

程序对cookie中的language字段的操作过程，位于sourceclassdiscuzdiscuz_application.php中

![](https://p2.ssl.qhimg.com/t01d0e3ce2b7e776916.png)

在这里，从cookie中取出language值，未经过滤，直接赋值给$lng变量

接着将$lng值赋值给名为DISCUZ_LANG的常量

![](https://p3.ssl.qhimg.com/t01a69a12bf53501974.png)

在Discuz! ML中，在生成cachefile名时，需要使用到DISCUZ_LANG这个常量进行拼接

![](https://p1.ssl.qhimg.com/t01a64115031461ef95.png)

由于DISCUZ_LANG常量由cookie中传递而来，并未经过任何过滤，因此DISCUZ_LANG常量可控

在程序运行时，Discuz! ML会将template/default/common目录下的默认模板写入缓存

在这个过程中，程序首先会打开并读取位于template/default/common目录下默认模板中的内容：

![](https://p0.ssl.qhimg.com/t017a07199c4e7769f0.png)

这里将读取的header.htm模板中的内容赋值给$template变量

再读取默认模板内容之后，程序接下来通过preg_replace_callback方法对模板内容进行替换与修改

![](https://p5.ssl.qhimg.com/t0132758544ea291a99.png)

在对默认模板内容进行修改时，注意如下图片中操作

![](https://p3.ssl.qhimg.com/t01a61cdeaee14e52f2.png)

上图操作中，会将’$tplfile’, ‘$fname’, “.time().”, ‘$templateid’, ‘$cachefile’,
‘$tpldir’, ‘$file’这些变量值拼接到名为headeradd的变量中

![](https://p0.ssl.qhimg.com/t01e224c7274db88bb3.png)

Headeradd变量随后被拼接到$template中

注意这里的headeradd变量

![](https://p5.ssl.qhimg.com/t01077d3d676e8e6d9c.png)

如上图红圈处，这里将cachefile变量拼接到headeradd变量中，间接的将cachfile变量拼接到template中。

还记得cachefile变量吗？

![](https://p3.ssl.qhimg.com/t015be51c070c94feeb.png)

Cachefile变量的值，其中一部分是可控的

![](https://p4.ssl.qhimg.com/t01c6561d0e3d466e73.png)

例如上图，我们可以在其中插入形如 sc.’phpinfo().’的payload

这个payload随着headeradd变量，被带入template中

接下来，被污染的template值被写入缓存文件中

![](https://p4.ssl.qhimg.com/t01a0ba681f72b1bf97.png)

如上图可见，最终写入的缓存文件名即为cachefile的值，内容即为template值，Payload已经随着headeradd拼接到template而被写入这个缓存文件中

![](https://p0.ssl.qhimg.com/t01549e9c40f9166602.png)

上图这里看起来比较杂乱，简化起来如下图

![](https://p2.ssl.qhimg.com/t0183e7431bce8e2d88.png)

当缓存文件被注入如上文payload后，再次加载程序，

当程序执行到位于sourcemoduleforumforum_index.php处时：

![](https://p3.ssl.qhimg.com/t019b343a8e7fc1c919.png)

可见上图432行，会使用include方法包含 template方法的返回值

跟进Template方法，找到其返回值，即是此处被include中的内容

Template方法位于sourcefunctionfunction_core.php

![](https://p4.ssl.qhimg.com/t01695bb2204ef6eda8.png)

在其654行处，可见返回cachefile路径

![](https://p3.ssl.qhimg.com/t01f3e5fa6205bf01e8.png)

cachefile即为上文被植入payload的文件

由此，被插入payload的缓存文件被include，其中构造好的payload被执行，造成代码执行漏洞

## 0x04 修复建议

目前官方没有进行修复，请时刻关注：[https://bitbucket.org/vot/discuz.ml/commits/all，等待官方补丁。](https://bitbucket.org/vot/discuz.ml/commits/all%EF%BC%8C%E7%AD%89%E5%BE%85%E5%AE%98%E6%96%B9%E8%A1%A5%E4%B8%81%E3%80%82)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **天融信阿尔法实验室** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/181887](/post/id/181887)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)
  * [Web安全](/tag/Web安全)

 **+1** __15赞

 __收藏

![](https://p0.ssl.qhimg.com/t016dfbf6ffbd895d3b.png) 天融信阿尔法实验室

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

