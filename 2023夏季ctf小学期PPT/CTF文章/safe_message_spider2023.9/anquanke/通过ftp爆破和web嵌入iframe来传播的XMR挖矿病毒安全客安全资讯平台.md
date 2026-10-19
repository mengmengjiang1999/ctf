# 通过ftp爆破和web嵌入iframe来传播的XMR挖矿病毒

阅读量 **327621**

|评论 **6**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-01-24 11:35:54

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t017d51dce3ed68f5ac.jpg)

先分析一下Photo.scr这个文件，这个文件是一个PE文件，母体没有加任何的壳，可以直接分析。这个程序的资源段附带了一个被vmp加壳的程序，该附加程序为挖矿程序。先分析母体，嗯，已经基本被各大引擎识别了。

![](https://p4.ssl.qhimg.com/t01844b3ef88da62557.png)

构建一个访问网址

![](https://p3.ssl.qhimg.com/t011b3a851050a64359.png)

打开恶意网址，读取数据，并且检验文件大小是否位0x800字节

![](https://p4.ssl.qhimg.com/t01bf9bbb7dd497bb88.png)

访问失败次数小于900次则继续访问

![](https://p1.ssl.qhimg.com/t01cbe21844cb3bccb2.png)

该网址下载了的是矿机的配置文件

![](https://p4.ssl.qhimg.com/t01c0b49a2f38e8792c.png)

该网址下载的是矿机的配置文件，以下检查配置矿机配置文件内容是否正确

![](https://p3.ssl.qhimg.com/t011798edc45ce38c09.png)

如果检查通过，则继续通过一系列的字符串拼接，最终构成可用的挖矿程序参数

![](https://p5.ssl.qhimg.com/t01ea1f70c042d740d4.png)

![](https://p1.ssl.qhimg.com/t01c7253b75715d4f03.png)

接下来，该母体会通过自身资源释放挖矿程序放在用户的%temp%目录下

![](https://p5.ssl.qhimg.com/t01d32cc3d2c74e1320.png)

![](https://p4.ssl.qhimg.com/t0102ca7e8587bfe9e2.png)

![](https://p5.ssl.qhimg.com/t01907946d0bd016720.png)

创建挖矿程序

![](https://p2.ssl.qhimg.com/t01bfa52480f23943a0.png)

我们可以看到生成的挖矿程序

![](https://p1.ssl.qhimg.com/t01433d66361f9a90e5.png)

执行挖矿程序

![](https://p0.ssl.qhimg.com/t0185e9123ff4cb02f8.png)

挖矿程序使用了vmp加壳的，所以有检测虚拟机和调试器

![](https://p1.ssl.qhimg.com/t01c31f9777e116fa48.png)

接下来会将该母体内置的矿池地址写到%temp%\pools.txt

![](https://p0.ssl.qhimg.com/t01cb0c04dc90f74f7a.png)

![](https://p0.ssl.qhimg.com/t014777404e0bf649f1.png)

![](https://p3.ssl.qhimg.com/t01d31c24b0ffa4c3ff.png)

通过添加HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run实现开机自启动

![](https://p0.ssl.qhimg.com/t01c8c211610f4ac7e1.png)

![](https://p5.ssl.qhimg.com/t0163decb511f2b1a44.png)

将母体文件拷贝到各个磁盘根目录

![](https://p4.ssl.qhimg.com/t01a07d936639706694.png)

![](https://p1.ssl.qhimg.com/t01da4daf6d1df6d16d.png)

接下来该程序会创建很多的线程，通过内置的用户名和密码来爆破ftp，使用ftp来实现自己的传播，将ftp上每个文件夹都上传母体文件

![](https://p1.ssl.qhimg.com/t01b42d470bac767d14.png)

![](https://p3.ssl.qhimg.com/t01e190a60f8bba051b.png)

内置的用户名和密码

![](https://p0.ssl.qhimg.com/t0186a29d548b3bdb2e.png)

![](https://p4.ssl.qhimg.com/t01426a138eb94da104.png)

并且该程序还会搜索该ftp上的所有文件，检索.php. .html.
.asp等常见的web文件，嵌入自己的一个iframe标签，实现通过被攻击用户的web服务下载，增加传染率。

![](https://p0.ssl.qhimg.com/t012499027c985edd01.png)

![](https://p4.ssl.qhimg.com/t013c9933e979a6ff77.png)

![](https://p3.ssl.qhimg.com/t01c085f1e52662775a.png)

最后，将成功的ftp的用户名，密码，系统等信息上传

![](https://p2.ssl.qhimg.com/t01407d59d0f7a058d7.png)

![](https://p2.ssl.qhimg.com/t012dbdea07c12888ac.png)

**总结**

这个程序在传播模块这里主要关注通过在用户的web页面中嵌入传播标签，实现更大效率的传播。其他的也没什么了。

**矿池地址**

42n7TTpcpLe8yPPLxgh27xXSBWJnVu9bW8t7GuZXGWt74vryjew2D5EjSSvHBmxNhx8RezfYjv3J7W63bWS8fEgg6tct3yZ

**IOC**

Photo.src md5: aba2d86ed17f587eb6d57e6c75f64f05

NsCpuCNMiner32.exe3afeb8e9af02a33ff71bf2f6751cae3a

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **binlmmhc** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/170102](/post/id/170102)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [恶意软件](/tag/恶意软件)
  * [挖矿](/tag/挖矿)

 **+1** __2赞

 __收藏

![](https://p3.ssl.qhmsg.com/dm/200_200_100/t00df551a583a87f4e9.jpg) binlmmhc

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

