# metinfo 6.2.0最新版本前台注入分析

阅读量 **323944**

|评论 **1**

发布时间 : 2019-04-02 12:00:11

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t01fa22c5953944abdf.png)

## 概述

看到某个表哥发的metinfo
6.1.3最新注入（<https://xz.aliyun.com/t/4508>)，以前我发过metinfo利用注入getshell的文章，这里正好可以结合。（[https://nosec.org/home/detail/2324.html](https://nosec.org/home/detail/2324.html%5D))，在检查官方发布的最新版6.2.0版本的时候，发现该漏洞并未修复。

## 利用条件

前台，（<https://xz.aliyun.com/t/4508> ）作者在这里说需要注册会员，其实有一处不需要。

## 漏洞详情

这里关键点在auth类的encode()和decode()方法。看下代码：

![](https://p3.ssl.qhimg.com/t011bd8e8ef70123d1a.png)

这里两个方法全都调用了authcode()方法，跟进authcode看一下：

![](https://p1.ssl.qhimg.com/t0195faab7c8ef73f0c.png)

这里decode和encode算法可逆，但我们需要知道$key的值，查看构造函数：

![](https://p0.ssl.qhimg.com/t016a902b8fb4f073bd.png)

这里$key的值是来源于met_webkeys这个配置，查看met_webkeys来源发现在安装的时候把这个key写入到<span
style=”color: rgb(212, 212, 212);”></span><span style=”color: rgb(206, 145,
120);”>.<span style=”color: rgb(51, 51,
51);”>/config/config_safe.php文件中。</span></span><span style=”color: rgb(212,
212, 212);”></span><span style=”color: rgb(206, 145, 120);”></span><span
style=”color: rgb(212, 212, 212);”></span>

![](https://p0.ssl.qhimg.com/t01d4ef3636ade24621.png)

查看<span style=”color: rgb(206, 145, 120);”><span style=”color: rgb(51, 51,
51);”>/config/config_safe.php</span></span>文件，这里写入方式类似以下，但p牛在某篇文章中说过，这种是无法解析的，php后面必须要有一个空白字符，右键查看源代码即可得到met_webkeys，但有的会报错，根据这个表哥所说和php线程安全有关，本地试了下好像是这样。

![](https://p0.ssl.qhimg.com/t018aa525c682c4a303.png)

![](https://p0.ssl.qhimg.com/t01d107f0418819f803.png)

![](https://p4.ssl.qhimg.com/t01a8a42e55be10dc4e.png)

这里有两个利用点，简单说下其中一个。在register类的doemailvild()方法中，这里把用户提交的p参数进行了解密，并且传入到了get_user_valid()方法中。

![](https://p2.ssl.qhimg.com/t01e8c831e0499e9280.png)

查看get_user_valid()方法，这里又把解密后的值传入到了get_user_by_username()方法。

![](https://p3.ssl.qhimg.com/t0109479ea7316585f7.png)

查看get_user_by_username()方法，又传入了get_user_by_nameid()方法。

![](https://p1.ssl.qhimg.com/t01fb5dbd1bb6d9d2df.png)

查看get_user_by_nameid()方法，直接拼接。

![](https://p3.ssl.qhimg.com/t01db733f966740ffc2.png)

这里基本就清楚了，将auth类的authcode()方法copy本地。

![](https://p5.ssl.qhimg.com/t01cc07b2fa1697dd1a.png)

访问本地文件得到加密后的字符串。

![](https://p2.ssl.qhimg.com/t01d32e30926f1997bd.png)

将加密后的字符串放到cookie，get或者post中，构造请求提交，延时注入成功。

![](https://p2.ssl.qhimg.com/t01ebc089894c8b2675.png)

## payload

这里有两个，一个是不需要登陆就可注入，另一个是coolcat表哥所说的需要以会员登陆。以下请自行替换p参数。

1、不需要登陆

    
    
    GET /admin/index.php?n=user&m=web&c=register&a=doemailvild HTTP/1.1
    
    Cookie: p=00c7%2FDBwD23b41olxVCthTvDDTRBhldmrrdyA8S3t%2F3yAl4QZ0P%2FSfOS5zlB
    

2、 需要登陆

    
    
    GET /admin/index.php?n=user&m=web&c=profile&a=dosafety_emailadd HTTP/1.1
    
    Cookie: p=497cD9UpkDtsvFzU9IKNlPvSyg1z%2bf09cmp8hqUeyJW9ekvPfJqx8cLKFSHr;<自行添加登陆后的cookie>
    

本文由白帽汇原创，转载请注明来源：<https://nosec.org/home/detail/2436.html>

白帽汇从事信息安全，专注于安全大数据、企业威胁情报。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **白帽汇** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/175818](/post/id/175818)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)
  * [代码审计](/tag/代码审计)
  * [Metinfo](/tag/Metinfo)

 **+1** __6赞

 __收藏

![](https://p4.ssl.qhimg.com/t01cbcea083daf5b1a3.png) 白帽汇

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

