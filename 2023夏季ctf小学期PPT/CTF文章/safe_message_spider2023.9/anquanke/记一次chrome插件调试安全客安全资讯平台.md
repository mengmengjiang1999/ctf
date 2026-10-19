# 记一次chrome插件调试

阅读量 **242420**

发布时间 : 2022-10-28 14:30:03

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t01c8a58a54f2a13b69.jpg)

## 前言

因为谷歌翻译退出中国，导致翻译不太好用了，所以去谷歌商店找了个用着还不错的翻译插件，没想到发现其全文翻译的功能每天只能使用3次，不限使用需要开会员。之前还没做过插件调试，这次就简单试试水，最后成功达到了目的，遂记录下。

## 调试过程

###  思路

因为这个插件每天只能全文翻译三次，当超过次数后会弹窗提示，导致功能不可用。猜测肯定是哪里做了一个计数，同时还有会员、功能翻译次数的判断，那么思路无非就是修改这个判断的结果，从而达到无限制使用的目的

###  前置知识

Chrome插件基本由mainfest.json, content-script, background.js, popup组成

mainfest.json: 插件的配置文件

content-script: 用来向页面注入css和js

background.js: 常驻于浏览器的一个脚本, 始终在运行

popup: 即点击插件的logo以后弹出的窗口

###  debug

打开chrome，在源码栏选择content scripts栏，全局搜索提示“非会员每天”定位到判断函数，随便在上面下个断点

![](https://p1.ssl.qhimg.com/t01a0aea518382c481e.png)

点击插件翻译按钮，简单跟了几步就发现一个关键判断，这里的参数值不用关心是如何生成的，只需要知道这里判断return的结果会对上面的判断产生影响

![](https://p2.ssl.qhimg.com/t01e128acb00f663f4b.png)

其中一个判断值就是i这个对象

![](https://p0.ssl.qhimg.com/t0110020c5bc579459c.png)

i这个对象里面有个字典，其中pageTranslateLimit这个值中的times很关键

只需要将它每次修改为0，那么上面的次数判断就能绕过，充不充会员也就没啥意义了

###  修改覆盖

在chrome的地址栏输入chrome://version/后, 可以看到你的chrome根目录

![](https://p4.ssl.qhimg.com/t01bdfebc9e87e09d2c.png)

在该目录下的Extensions是插件目录，右键插件图标管理扩展程序就能看到插件的id值

![](https://p4.ssl.qhimg.com/t01715ad8d68c8ad626.png)

将原目录的文件拷出来，然后修改99.js文件，在关键函数下重新赋值即可

![](https://p5.ssl.qhimg.com/t011d17bc44d8915376.png)

然后删除原版插件，打开开发者模式，加载修改后的文件

![](https://p3.ssl.qhimg.com/t01468736fd17613c3b.png)

然后就能愉快的无限制使用翻译功能了

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **雷石安全实验室** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/282224](/post/id/282224)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Chrome](/tag/Chrome)

 **+1** __0赞

 __收藏

![](https://p2.ssl.qhimg.com/t01ebe472d127128939.png) 雷石安全实验室

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

