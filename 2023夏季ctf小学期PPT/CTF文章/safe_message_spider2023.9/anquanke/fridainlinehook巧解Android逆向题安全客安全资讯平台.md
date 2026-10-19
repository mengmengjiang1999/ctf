# frida inlinehook 巧解Android逆向题

阅读量 **113980**

|评论 **1**

发布时间 : 2023-01-03 15:30:42

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

## 前言

最近又又又是老朋友发来一道Android逆向题，比赛时没做出来，后来参考了别人的思路，还是用frida解出了题目，学到一些思路记录下。

## Java层静态分析

直接拖进jadx，MainActivity内容如下，代码不多，基本流程就是，获取输入字符，通过一个native层的checkflag判断输入是否正确：

![](https://p0.ssl.qhimg.com/t0141c0b0e029418480.png)

## Native层静态分析

直接解压把libnative-lib.so拖入ida。  
发现是静态注册的，直接能在导出函数里找到，处理伪码后如下，直接是ollvm当时就放弃了：

![](https://p1.ssl.qhimg.com/t01a66303d8a4537c5c.png)

尝试用脚本模拟执行so，反混淆一下，emmmmm区别不大，但是好像勉强能看了？

![](https://p0.ssl.qhimg.com/t019cdda90f5019c19a.png)

翻了下看到进来有几处检测，一个很明显判断长度是否16：

![](https://p1.ssl.qhimg.com/t01ff34fe539dc31eb4.png)

另外两处sub_78B0 sub_74E0，是检测调试：

![](https://p4.ssl.qhimg.com/t01e1aeee4ae042f730.png)

直接patch掉这个检测：

![](https://p5.ssl.qhimg.com/t01d805fdbfe274ab0a.png)

后面一长串看不懂了，绕晕了，后面看到一个地方很有意思：

![](https://p4.ssl.qhimg.com/t01149d245a7b727d7e.png)

上面这个判断很可疑（其实就是瞎猫撞死耗子），如果这里不行，就没有后文了，显然发了这篇文章这里肯定是可以的。

## Frida inlinehook

记录下指令地址，掏出frida开始hook这条指令看看寄存器的值。

![](https://p2.ssl.qhimg.com/t0142201cb272b024e1.png)

跑起来，输入测试flag观察结果，我输入个f000000000000000，可以看到出现一次判断成功，后面第二次不相等了就没有后面的判断了：

![](https://p0.ssl.qhimg.com/t01e6a44763d1491502.png)

再次试试，fl00000000000000，可以看到判断成功两次，同样第三次判断不相等又没有后文了：

![](https://p4.ssl.qhimg.com/t0168d9a21e9d4a593d.png)

根据上面的判断，那思路其实已经有了，逐位爆破应该就是能获取到flag，剩下就是脚本问题，这个好解决，构造一个主动调用，在java层调用checkflag函数，同时inlinehook观察指令判断情况一位一位爆破就行，代码如下：

![](https://p1.ssl.qhimg.com/t01fa36877c4b2eae16.png)

![](https://p2.ssl.qhimg.com/t0178e9f2fdca20749e.png)

然后一开始出了个bug，想不通，后来发现是我的flag填充位有问题，不能是0（因为flag中是包含0的，我的代码逻辑没考虑这么多，所以到下一位是0的时候，前一位爆破完，就标志位会出错了）：

![](https://p4.ssl.qhimg.com/t01caccd42e47a65eb3.png)

最后在代码中把填充位换成其他字符，换成z，就愉快的跑出结果了：

![](https://p5.ssl.qhimg.com/t0195f0e89b2b3b6fd8.png)

## 总结

题目设置刚刚好（我看就是不想让人做出来），后面看了别人的wp是用unidbg做的，这个我不怎么会就换成用frida，直接做了出来，主要还是学习一下frida的inlinehook。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **雷石安全实验室** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/284343](/post/id/284343)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [移动安全](/tag/移动安全)

 **+1** __1赞

 __收藏

![](https://p2.ssl.qhimg.com/t01ebe472d127128939.png) 雷石安全实验室

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

