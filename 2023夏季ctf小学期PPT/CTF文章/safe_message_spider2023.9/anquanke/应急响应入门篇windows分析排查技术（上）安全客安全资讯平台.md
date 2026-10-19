# 应急响应入门篇-windows分析排查技术（上）

阅读量 **247198**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-11-10 10:00:18

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t01efac09409181d75c.jpg)

## 一、应急响应：

**概念：**

一般情况下，各种木马，病毒等恶意程序，都会在计算机开机启动过程中启动。

当企业发生 **黑客入侵、系统崩溃**
或其它影响业务正常运行的安全事件时，急需第一时间进行处理，使企业的网络信息系统在最短时间内恢复正常工作，进一步查找入侵来源，还原入侵事故过程，同时给出解决方案与防范措施，为企业挽回或减少经济损失。

###  常见的应急响应事件分类：

web入侵：网页挂马、主页篡改、Webshell  
系统入侵：病毒木马、勒索软件、远控后门  
网络攻击：DDOS攻击、DNS劫持、ARP欺骗

**分析排查** 是指对windows系统中的文件、进程、系统信息、日志记录等进行检测，挖掘windows系统中是否具有异常情况。目的在于：
**保护windows系统安全** 。

## 二、windows应急响应实际分析

在windows系统中可以通过以下三种方式查看开机启动项

###  1.分析开机启动项

**方法1.利用操作系统中的启动菜单**

1.先进入组织，然后打开文件夹选项，把隐藏文件显示。

![](https://p1.ssl.qhimg.com/t01d4e2bc9a493381d5.png)

2.然后输入路径：C:\Users\x\AppData\Roaming\Microsoft\Windows\Start
Menu\Programs\Startup，访问就看到了开机启动项里的文件

![](https://p2.ssl.qhimg.com/t01ee2bed9249a0a5f5.png)

![](https://p2.ssl.qhimg.com/t013b0e3e1db91f264b.png)

**法2,利用系统配置msconfig**

1.使用win+r ,输入msfconfig

![](https://p4.ssl.qhimg.com/t01f190f87fc61af0d4.png)

2.然后对正在运行的文件进行分析。如vmvaretools

**法3.利用注册表regedit**

使用win+r，输入regedit，一步一步找到开机启动项的位置

![](https://p0.ssl.qhimg.com/t016d57673b70a74279.png)

![](https://p5.ssl.qhimg.com/t0180e07f5f6826bd5e.png)

然后进行下一步分析

![](https://p2.ssl.qhimg.com/t01f5441fd66fa43318.png)

###  02文件分析-temp临时异常文件

temp（临时文件夹），位于C:\Documents and settings\Administrator

**法1：直接访问根目录**

![](https://p2.ssl.qhimg.com/t01f21b8cd9cc46e120.png)

**法2：输入%temp%，然后运行，即可调用出来。**

![](https://p4.ssl.qhimg.com/t01624f4f37e504a274.png)

3.对temp目录下的pe文件进行查看，查看那些比较大一点的文件（exe、dll、sys）

![](https://p1.ssl.qhimg.com/t01044370ef4e190442.png)

4.将文件上传到virustotal进行查看，是否为恶意代码

<https://www.virustotal.com/>

![](https://p1.ssl.qhimg.com/t012b374b3cbcebb1ce.png)

###  03文件分析—浏览器信息分析

在被黑客拿下的服务器，很有可能会使用浏览器进行网站的访问，因此我们可以查看浏览器记录，探索浏览器是否被使用和下载恶意代码。

1.先打开ie浏览器，然后在浏览器打开历史记录

![](https://p4.ssl.qhimg.com/t015e046fa15c06e594.png)

2.然后按照日期进行筛选，查看可疑程序时间。

![](https://p2.ssl.qhimg.com/t01fa23ae8ebf9986ce.png)

3.由于在不同浏览器，查看浏览记录的方式不一样。所以推荐一个工具 **browserhistory** 。

下载之后打开软件，进行配置

![](https://p1.ssl.qhimg.com/t01f0df93a3ae53d69f.png)

然后进行浏览器历史记录查看。

![](https://p3.ssl.qhimg.com/t01a42410981eadf8f9.png)

查看浏览器cookie信息，推荐 **iecookies view**

![](https://p0.ssl.qhimg.com/t01727a620a795708f0.png)

进行筛选，查找。

![](https://p4.ssl.qhimg.com/t017deca418c575850f.png)

保存文件

![](https://p5.ssl.qhimg.com/t01609d76b2e1f12ba1.png)

![](https://p4.ssl.qhimg.com/t01d6da9047eac47031.png)

然后对其进行分析

![](https://p1.ssl.qhimg.com/t01d8eb4f0b5ac5d165.png)

推荐一个下载工具的地方：

<http://launcher.nirsoft.net/downloads/index.html>

![](https://p4.ssl.qhimg.com/t013cc4d094c5e6dc6f.png)

###  04 文件时间属性分析

在windows系统下，文件属性的时间属性有：创建时间、修改时间、访问时间（默认情况下禁用）

![](https://p3.ssl.qhimg.com/t0157388b00e122ad1e.png)

如果遇到了一个修改时间早于创建时间，比较异常的那种修改时间。这种文件就特别可疑/。

没找到可疑文件，记得认真看一下修改时间。

![](https://p1.ssl.qhimg.com/t01f0373ef5e3519f5e.png)

可以使用中国菜刀连接，然后修改文件的修改时间

![](https://p4.ssl.qhimg.com/t01c4e68bebf8fb57dc.png)

![](https://p2.ssl.qhimg.com/t014da31467952368df.png)

###  5最近打开文件分析

windows系统默认记录系统中最近打开使用的文件信息

可以在目录 C:\Users\x\Recent下查看，也可以使用win+r 输入 %UserProfile%\Recent 查看

![](https://p0.ssl.qhimg.com/t01c2c600b4848d7c5e.png)

1.然后打开最近的文件

![](https://p2.ssl.qhimg.com/t01aee53126ee2ef91d.png)

可以直接打开文件进行分析。

![](https://p2.ssl.qhimg.com/t01cc5ece121c83af05.png)

如果文件太多，还可以使用日期进行筛选

![](https://p5.ssl.qhimg.com/t018295e5583fe3261b.png)

最后还可以使用cmd命令 find / ？ 加各种参数然后对最近打开的文件进行筛选。

![](https://p0.ssl.qhimg.com/t018ead8034185cf6b8.png)

**总结：**

本文针对常见的攻击事件，总结了一些如何对Window服务器入侵，一步步操作对入侵进行分析。主要针对开机启动项、temp临时异常文件、浏览器信息、文件属性、最近打开文件进行分析。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Arthur** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/258490](/post/id/258490)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [应急响应](/tag/应急响应)

 **+1** __6赞

 __收藏

![](https://p4.ssl.qhimg.com/t010857340ce46bb672.jpg) Arthur

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

