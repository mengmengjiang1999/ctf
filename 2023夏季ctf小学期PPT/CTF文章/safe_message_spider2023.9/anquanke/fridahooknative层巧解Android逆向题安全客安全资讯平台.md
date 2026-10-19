# frida hook native层巧解Android逆向题

阅读量 **215283**

发布时间 : 2022-12-01 10:30:06

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

## 前言

最近还是老朋友发来一道Android逆向题，挺有意思，用frida hook native层解出了题目，记录下学习的过程。

## Java层静态分析

直接拖进jadx，MainActivity内容如下：

![](https://p2.ssl.qhimg.com/t01a02472dda779c8c4.png)

代码不多，基本流程就是，获取输入字符，通过一个反射调用（调用的函数是加密了，要用native层的decode解密）处理了一下输入字符串，然后通过check函数进行判断，前面的是处理过的输入字符串，后面的一串应该是密钥之类的。

![](https://p2.ssl.qhimg.com/t017904f5f634b7a0fe.png)

## firda hook java层

首先比较关心decode解密的数据是啥，直接hook一下，可以看到反射调用的是base64，那么后续传入比较的字符串就是base64处理过了，我们解出来的flag应该也是要base64解密一次。  
看到还有一串“Hikari#a0344y3y#1930121”，应该是传入check的密钥。

![](https://p5.ssl.qhimg.com/t016d45c29e65a60893.png)

接下来比较关心的就是check函数是怎么处理输入的字符串。

## Native层静态分析

直接解压把libcheck.so拖入ida。  
发现是静态注册的，直接能在导出函数里找到，关键步骤还是再最后几行，可以看到是通过RC4进行了加密，与一个数组进行了比较判断，跟进do_crypt函数后，处理伪码后如下：

![](https://p4.ssl.qhimg.com/t017dd0132760341f74.png)

那么这个数组的内容应该就是要找的加密后的flag。

![](https://p3.ssl.qhimg.com/t0122051d6cedaaffa0.png)

## Frida hook native

记录下函数地址，关掉ida。

![](https://p4.ssl.qhimg.com/t015ccaf47e0488b0ce.png)

直接上frida，先来hook一下这个函数，看看输入输出，这里从上面可以看到是arm指令后面计算函数地址不需要加1，打印下输入输出的内容。

![](https://p3.ssl.qhimg.com/t011dc631f480f6dc43.png)

动态调试起来输入结果如下：

![](https://p2.ssl.qhimg.com/t01ecfd87cc79339d5b.png)

能成功hook了，刚好这里是通过RC4算法进行的加密，那么我们只需要把输入的内容替换成上面找到的flag的密文，就应该能得到真实的flag（base64编码后的）。  
通过frida操作内存，把输入的参数arg[1]hook并覆写内存成我们密文的内容，这里需要注意一点，你输入的文本尽可能长一点，不然获取到的结果不全。  
打印内存得到了一串字符串，base64解码一下，得到flag。

## 总结

题目设置刚刚好，后面看了别人的wp，发现rc4是魔改过的，但是这里是rc4，那么就可以这么取巧去做一下，运气也不错，直接做了出来，主要还是学习一下frida对native层的hook。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **雷石安全实验室** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/283461](/post/id/283461)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [逆向工程](/tag/逆向工程)

 **+1** __0赞

 __收藏

![](https://p2.ssl.qhimg.com/t01ebe472d127128939.png) 雷石安全实验室

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

