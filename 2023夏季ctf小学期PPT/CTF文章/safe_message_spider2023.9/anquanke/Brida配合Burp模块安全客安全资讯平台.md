# Brida配合Burp模块

阅读量 **154194**

发布时间 : 2022-06-24 10:30:34

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

## 前言

前一篇文章介绍了brida的安装及其基本的用法，这篇文章来讲一下brida如何更流畅地和burp联动起来。

## js编写

拿了一个app做测试，先简单定位到对应的加密函数。不放心可以先用frida测试一下，能否hook到数据，这里不演示了。

![](https://p3.ssl.qhimg.com/t01a76380a30aa7fc55.png)

根据上篇文章的格式，写一个hook的脚本。

![](https://p5.ssl.qhimg.com/t01801c8e371e278597.png)

## 配置brida自定义plugin

到brida中的Custom plugin面板，简单配置下。  
主要是在起作用的范围，以及hook的函数，处理的时机。

![](https://p0.ssl.qhimg.com/t01bfe2778fd938a50e.png)

配置完后添加然后启用。

![](https://p2.ssl.qhimg.com/t019c2c33f5181c01c0.png)

## repeater以及intruder测试

简单抓了一个涉及加密参数的包。

![](https://p2.ssl.qhimg.com/t01305edd0b43665f1f.png)

把他放到repeater中，修改对应的加密参数为明文。然后发送。打开brida插件的调试界面。

![](https://p5.ssl.qhimg.com/t01f59c47df95d8879c.png)

可以看到原始数据包中的明文，被加密函数处理后替换成密文发送了。

![](https://p0.ssl.qhimg.com/t01b24094cde9e9e3a6.png)

然后再在intruder中添加一些测试数据。

![](https://p1.ssl.qhimg.com/t0168a14eecccd521c4.png)

开始爆破就行了，日志中都是有的，这里不继续演示了。

## 总结

对brida的自定义插件功能进行了简单的研究与尝试，极大的简化了我们测试app工作，也更好的把hook和网络数据包联动了起来。  
赶紧上手去挖自己的高危严重吧！

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **雷石安全实验室** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/275231](/post/id/275231)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [brida](/tag/brida)

 **+1** __1赞

 __收藏

![](https://p2.ssl.qhimg.com/t01ebe472d127128939.png) 雷石安全实验室

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

