# 一道Android逆向题的取巧解题思路

阅读量 **176518**

发布时间 : 2022-10-31 14:30:32

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

## 前言

最近朋友发来一道Android逆向题，挺有意思，花时间研究了一下，在算法逆不出来的情况下（我太菜），用frida取巧解出了题目，记录下学习的过程。

## 抛出问题

安装打开题目发现是要求输入字符串。

![](https://p2.ssl.qhimg.com/t010cfdd346ad3b77cb.png)

随便输入提示错误。

![](https://p4.ssl.qhimg.com/t01914682a2995ea9c5.png)

## Java层静态分析

拖进jadx，先分析下java层。里面类有点多，估计是垃圾代码，直接看Androidmanifest文件找到启动的Activity去分析。

![](https://p5.ssl.qhimg.com/t018ada62cffde3d8ab.png)

找到对应的类，一看上面就是一个byte数组，一个loadLibrary，一个native函数，so逆向跑不了。  
下面看到对应的按钮点击事件。

![](https://p1.ssl.qhimg.com/t0162fae33f3626e936.png)

继续跟进去看，找到了核心的逻辑，是通过encry函数处理输入字符串，返回一个byte数组，然后和前面的byte数组比较是否相等，那前面的byte数组应该就是加密后的flag，我们要做的就是逆出来。

![](https://p2.ssl.qhimg.com/t0142378df68f0ed0f5.png)

## Native层静态分析

encry是写在native层，对apk解包，取出对应的so（libencry.so）拖进ida。  
可以看到是静态注册的，直接能在导出函数里找到。

![](https://p5.ssl.qhimg.com/t010b79e193c89fefa2.png)

转成C伪码，看一下，我还是太菜，不会。

![](https://p3.ssl.qhimg.com/t0196361a11c4bc5eb8.png)

动态调了下，也没调明白，我太菜了。

## Frida动态hook

关掉ida，直接上frida，先来hook一下这个函数，看看输入输出。  
可以hook到，输入的参数以及输出的byte数组

![](https://p0.ssl.qhimg.com/t013a0335d1cc8b9deb.png)

这里开始测试（猜），flag格式一般就是flag{xxxxxx},我输入“flag{”进行测试，hook结果如下：

![](https://p4.ssl.qhimg.com/t0164bdc5db453c2165.png)

对比Java层中的byte数组，发现前几位已经能对上了，但是最后一位对不上，应该是因为so层中的加密算法后一位会影响前一位。  
到这里就已经可以get到一个比较取巧的思路了，写个rpc脚本调用一位一位爆破flag。

## Frida rpc调用

直接hook encry函数，主动调用。  
js部分如下：

![](https://p2.ssl.qhimg.com/t0155b2521ad351343c.png)

python调用，爆破部分如下：

![](https://p5.ssl.qhimg.com/t01efb262d95d31722f.png)

一位一位遍历所有可打印字符跑起来。  
成功获取（爆出）到flag。

![](https://p4.ssl.qhimg.com/t016257bdff638c9e6a.png)

## 总结

常规做法做不出来，只能取巧，题目设置也刚好，最终还是以结果为导向，能解题的方法总是好方法。这里只是举例了用frida，实际上也可以使用unidbg去主动调用so进行爆破，原理是差不多的。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **雷石安全实验室** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/282006](/post/id/282006)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [移动安全](/tag/移动安全)

 **+1** __0赞

 __收藏

![](https://p2.ssl.qhimg.com/t01ebe472d127128939.png) 雷石安全实验室

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

