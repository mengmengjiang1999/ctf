# APT组织污水（MuddyWater）新武器MuddyC3代码泄露与分析

阅读量 **334501**

发布时间 : 2019-06-25 16:58:10

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t0103f8c62d59518f29.jpg)

## 背景

今年5月初，有黑客成员在Telegram渠道（Channel：GreenLeakers）披露其拥有据称APT组织MuddyWater网络攻击的证据和资料，并进行售卖。

MuddyWater被普遍认为是一个来自中东地区的，长期活跃的APT组织。从2019年2月到4月，该组织发起了一系列针对土耳其、伊朗、阿富汗、伊拉克、塔吉克斯坦和阿塞拜疆的政府、教育机构、金融、电信和国防公司的网络钓鱼电子邮件攻击。

![](https://p5.ssl.qhimg.com/t01c649a3c381792664.png)

其Web控制后台的界面：

![](https://p3.ssl.qhimg.com/t019784b8b42a063c03.png)

以及一个其研制的渗透工具，从Banner上可以看出为muddyc3，版本号为1.0.0。

![](https://p4.ssl.qhimg.com/t014d52f1886a84f277.png)

昨日（6月24日）另外一个telegram channel泄露了一份muddyc3的源码并进行了相关拍卖。

![](https://p5.ssl.qhimg.com/t01411570e2621458ea.png)

后续也有安全研究人员在Github上发布了相关恶意样本和反编译的源码https://github.com/0xffff0800/muddyc3，其版本同样为1.0.0。

## 分析

我们在了解到该muddyc3信息后，在搜索引擎进行搜索，发现了两个名为muddyc3.exe的样本。

![](https://p4.ssl.qhimg.com/t0125ed8ace24f9fe7f.png)

###  反编译

我们发现其中一个样本是在x64环境下的PyInstaller打包的版本，从Banner信息可以看到其版本为v1.0.1。

尝试对其进行反编译，可以利用PyInstaller的archive_viewer脚本提取对应的pyc脚本，但由于脚本运行是需要用户交互指定反编译文件名，所以可以定制代码将所需要反编译的pyc全部提取，提取后需要修复pyc的头部magic信息。或者为了方便直接使用pyinstxtractor脚本。

还原成pyc文件后，用相关反编译工具，如Easy Python Decompiler或者uncompyle6。在实际过程中，发现部分文件使用Easy
Python Decompiler会出现反编译错误。另外从pyc幻数得知其编译环境是Python 2.7版本。

最后剔除内部库，得到源码：

###  功能和代码分析

版本1.0.1和1.0.0版本从代码结构上只有少量不同，下图为入口界面截图

![](https://p0.ssl.qhimg.com/t017eea70ae337e7c57.png)

运行开始需要指定C&C服务器IP和端口，以及是否使用代理的IP。

主要实现了list，show，use和payload四个命令，而show命令在实际代码中不存在对应处理逻辑。

并且列举了一些示例初始载荷的实现方式，初始脚本载荷代码可以嵌在如文档宏等方式，而当攻击目标触发了初始脚本执行后，其会以指定路径访问控制IP。

![](https://p4.ssl.qhimg.com/t01715c7dc18720fb82.png)

该工具主体是基于web.py实现的一个服务端（lib目前下其实为web.py库实现），用于和被控主机实现请求响应和命令交互，其中v1.0.0版本和v1.0.1版本的交互url路径列表不太相同。

V1.0.0

V1.0.1

其主要实现像sct、hta、powershell形态的下阶段载荷和上传、下载、信息回传等，以及支持模块。

由于其打包的exe控制程序并没有包含默认的powershell载荷代码，所以无法进一步得知。

例如这里我们尝试访问根路径。

尝试访问/hta路径。

其进行了简单的字符替换和base64编码，实际为：

## 总结

从反编译的控制程序实现的完备性来看，应该为MuddyWater组织的早期使用版本，可以作为一个基本的后渗透框架的雏形。

奇安信威胁情报中心红雨滴团队也将继续关注相关组织的更多进展。

## IOC

daa7d4c40ffaa6cf4e4708747d3a9b37

146cc97df36cb4cea39074652d069519

## 参考链接

https://github.com/kennethreitz-archive/pyinstaller/blob/master/ArchiveViewer.py

https://github.com/countercept/python-exe-unpacker

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **奇安信威胁情报中心** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/181000](/post/id/181000)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [恶意软件](/tag/恶意软件)
  * [恶意活动](/tag/恶意活动)

 **+1** __1赞

 __收藏

![](https://p3.ssl.qhimg.com/t01dce0f9e833e11f13.png) 奇安信威胁情报中心

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

