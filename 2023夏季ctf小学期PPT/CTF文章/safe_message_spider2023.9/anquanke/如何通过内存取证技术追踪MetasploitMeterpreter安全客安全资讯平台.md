# 如何通过内存取证技术追踪Metasploit Meterpreter

阅读量 **184186**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-04-11 11:02:12

 **x**

##### 译文声明

本文是翻译文章，文章原作者 SCAR，文章来源：articles.forensicfocus.com

原文地址：<https://articles.forensicfocus.com/2018/04/03/finding-metasploits-meterpreter-traces-with-memory-forensics/>

译文仅供参考，具体内容表达以及含义原文为准。

## 一、前言

Metasploit框架不仅深受渗透测试人员喜爱，也经常被实际攻击者使用。为什么这里我们要强调内存取证分析的重要性呢？作为动态可扩展的Metasploit载荷，Meterpreter可以完全驻留在内存中，不需要向受害者磁盘驱动器中写入任何数据。在本文中，我会向大家介绍如何使用Volatility
Framework，利用内存取证技术追踪Metasploit攻击的蛛丝马迹。

## 二、具体过程

在分析内存映像时，首先我们应当收集操作系统的信息，以选择正确的Volatility配置。比如，这里我们最好在生成内存映像过程中收集操作系统版本信息，因为Volatility并不能确保每次都能正确检测到这个值。此外，如果我们从第三方那获取到内存映像，无法得知操作系统版本信息，那么我推荐大家使用
**imageinfo** 这个插件：

![](https://p5.ssl.qhimg.com/t0183e4cb408bde57f5.png)

如上图所示，这次实验中Volatility正确猜测出了操作系统的版本：Windows 7 x86 with SP1。现在我们可以使用 **pslist**
插件查看进程列表：

![](https://p4.ssl.qhimg.com/t01042176abd24f8c99.png)

这里大家能不能看出可疑的恶意进程？比如说PID
3000这个进程如何？好吧，有可能是用户正在更新杀毒软件？但奇怪的是这个进程在启动42秒后就退出了。我们可以使用 **netscan**
插件进一步观察网络连接情况。

![](https://p2.ssl.qhimg.com/t0189eace4d76278268.png)

我们可以看到某个未知的进程已经与`192.168.1.39:4444`建立连接。这里告诉大家一个信息，`4444`端口是Metasploit默认的回连端口。由于Meterpreter会将自身注入目标进程中，我们可以使用
**malfind** 插件定位这个目标：

![](https://p2.ssl.qhimg.com/t01b979e9dae9008d43.png)

貌似Meterpreter已经与`svchost.exe`融合在一起，PID为`3312`。我们可以将其导出到一个文件中，看一下恶意软件对这个文件的检测情况：

![](https://p2.ssl.qhimg.com/t015f13ebf5f1aa17c3.png)

竟然没有杀毒软件能够检测这个文件？好吧，开个玩笑而已，情况并没有那么糟糕：

![](https://p0.ssl.qhimg.com/t01ae92bde486fa93be.png)

不论如何，许多主流软件并没有成功检测这个威胁，比如McAfee、Malwarebytes、DrWeb等……

如果你使用YARA规则来检测恶意软件，你可以编写自己的规则，也可以从网上直接借鉴一些规则，然后使用 **yarascan** 这个插件来检测：

![](https://p5.ssl.qhimg.com/t01f1c1508280639e2d.png)

这里我们使用了自己编写的一个简单规则，如下所示：

![](https://p5.ssl.qhimg.com/t0168186b9599f9b47a.png)

因此，看来一切的源头都是因为运行了PID 3000这个进程。如果我们回头看看pslist的输出结果，我们可以看到系统运行的浏览器为Internet
Explorer浏览器（`iexplore.exe`，PID为2568以及2640）。我们可以使用 **iehistory** 插件来查看浏览器历史记录：

![](https://p4.ssl.qhimg.com/t015d8c3c05be0e1e7a.png)

正中靶心！受害者从服务器上下载了 **antivirus_update.exe**
这个程序，服务器的IP地址前面我们已经见到过！但他们为什么会这么做呢？我们可以使用 **memdump** 插件导出Internet
Explorer的进程内存，搜索“ **antivirus** ”字符串：

![](https://p3.ssl.qhimg.com/t01c461641e2b59cb38.png)

如上图所示，攻击者使用社会工程学方法以及短网址来诱导受害者。因此当受害者下载并执行这个文件时，攻击者就会得到一个meterpreter会话，并将其融入`svchost.exe`进程中（PID为`3312`）。

但受害者真的运行这个程序了吗？我们可以查找程序运行的证据！首先，我们可以使用 **shimcache**
插件，该插件可以用来跟踪被执行程序的兼容性问题，可能会包含我们正在寻找的一些证据：

![](https://p3.ssl.qhimg.com/t0125d7979c25c0e502.png)

果不其然，我们找到了这个证据。让我们继续前行，使用 **userassist** 插件对注册表进行取证：

![](https://p4.ssl.qhimg.com/t01cdd11423946b1364.png)

这个程序被执行了两次！看来受害者并不是特别明智。我们也可以通过其他方式来搜索程序执行的证据，比如prefetch（预读取）文件。我们可以在内存中找到这些蛛丝马迹，Volatility也有一个插件能够处理这些文件：
**prefetchparser** 。

不幸的是，受害者系统上禁用了预读取功能，因此我们无法找到任何痕迹。

目前我们已经收集了许多信息，但还有一件事情可以去做：检测本地持久化机制！ **autoruns** 这个插件可以用来检测攻击者经常使用的一些本地持久化技术：

![](https://p3.ssl.qhimg.com/t01c169d90b903d76e7.png)

如上图所示，即使受害者不去主动运行“Antivirus Update”进程，该进程也会在系统重启时自动启动，就这么简单。

## 三、总结

整个过程就是如此，希望大家享受安全取证过程。

本文翻译自articles.forensicfocus.com
[原文链接](https://articles.forensicfocus.com/2018/04/03/finding-metasploits-meterpreter-traces-with-memory-forensics/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **興趣使然的小胃** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/104322](/post/id/104322)

安全客 - 有思想的安全新媒体

本文转载自:
[articles.forensicfocus.com](https://articles.forensicfocus.com/2018/04/03/finding-metasploits-meterpreter-traces-with-memory-forensics/)

如若转载,请注明出处： <https://articles.forensicfocus.com/2018/04/03/finding-metasploits-meterpreter-traces-with-memory-forensics/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Volatility](/tag/Volatility)
  * [metasploit](/tag/metasploit)
  * [Meterpreter](/tag/Meterpreter)
  * [内存取证](/tag/内存取证)

 **+1** __0赞

 __收藏

![](https://p0.ssl.qhmsg.com/dm/200_200_100/t0104d1b8b4ca36e961.jpg) 興趣使然的小胃

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

