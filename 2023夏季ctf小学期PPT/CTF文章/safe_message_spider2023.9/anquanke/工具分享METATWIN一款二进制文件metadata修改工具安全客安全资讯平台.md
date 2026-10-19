# 【工具分享】META TWIN：一款二进制文件metadata修改工具

阅读量 **159902**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2017-10-16 14:04:10

 **x**

##### 译文声明

本文是翻译文章，文章来源：threatexpress.com

原文地址：<http://threatexpress.com/2017/10/metatwin-borrowing-microsoft-metadata-and-digital-signatures-to-hide-binaries/>

译文仅供参考，具体内容表达以及含义原文为准。

译者：[興趣使然的小胃](http://bobao.360.cn/member/contribute?uid=2819002922)

预估稿费：120RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**一、前言**

****

受Casey
Smith（[@subtee](https://twitter.com/subTee)）发表的[一则推文](https://twitter.com/subTee/status/912769644473098240)的启发，我更新了几年前我与Andrew
Chiles（[@andrewchiles](https://twitter.com/AndrewChiles)）共同开发的一款工具。

以红队身份参与渗透测试活动时，如果无法避免磁盘操作，那么你可以使用这款工具尽可能融入周围环境。在内存中操作是非常好的方法，然而许多情况下，我们不得不使用磁盘上的二进制文件。我使用的技术非常有效，那就是修改二进制文件的资源信息（元数据，metadata）。元数据包含许多字段，如文件图标、版本、描述、产品名称、版权等信息。许多威胁源经常会通过突破安全防御或者修改IOC特征来尝试欺骗或蒙蔽安全分析人员（可以参考我发布的关于修改IOC特征的[系列视频](https://www.youtube.com/watch?v=_JiGsFPYDMQ&t=969s)）。

将文件融入周围环境可以使安全分析人员将恶意行为当成可信行为。特别是如果某个二进制文件看起来像是微软出品的，那么应该更加可信。

这正是[MetaTwin](https://github.com/minisllc/metatwin)发挥作用的场景。经过修改后，这款工具不仅能够修改二进制文件的元数据，也能添加最近由@subtee以及@mattifestation描述的数字签名信息。

  

**二、MetaTwin工作原理**

****

1、MetaTwin以经过合法签名的二进制文件作为源文件，如explorer.exe。

2、提取资源（利用[ResourceHacker](http://angusj.com/resourcehacker/)）以及数字签名信息（利用[SigThief](https://github.com/secretsquirrel/SigThief)）。

3、将提取到的数据写入目标二进制文件中。

  

**三、工具演示**

****

在这个例子中，我选择使用默认的meterpreter
reverse_tcp二进制文件。选择这个程序并没有什么特别含义，这里我们可以使用任意二进制文件（.exe或.dll文件）。就我个人而言，在实际环境中我是Cobalt
Strike的忠实粉丝。

如你所见，经过处理的文件看起来非常有迷惑性。红方操作人员无需消耗太多精力，只需将其保存在类似c:ProgramData之类的目录中，修改文件时间戳，就可以实现更长时间的驻留。

  

**四、有趣的实验结果**

****

**4.1 反病毒软件**

通常情况下，经过简单的修改，防御方工具的反应也会有所不同。当然反病毒软件通常不是个花架子，但我们还是很好奇它们会如何处理经过MetaTwin修改的Metasploit
meterpreter程序。除了添加元数据及数字签名外，我们没有做其他的混淆处理。实验结果非常有趣。

未经处理的源文件检测结果如下图所示。

不出意外，VirusTotal上的检出率非常高。

具体检测结果为：<https://www.virustotal.com/#/file/02d873881fef5b497503a48c221c4977e3a1a0d2cf9bfa78a8d6c567e63dca70/detection>

添加元数据后的检测结果如下图所示。

有趣的是，仅添加元数据就能降低反病毒软件的检出率。

具体检测结果为：<https://www.virustotal.com/#/file/cc96177e110d4413f918d9b7ef3650eab59bd7fa7a12afe37fde7ce3e6d63d1b/detection>

添加元数据及数字签名后的检测结果如下图所示。

添加数字签名及元数据后，检出率从76%降到了58%。这一点非常重要，因为我们还没有真正尝试规避反病毒软件！

具体检测结果为：<https://www.virustotal.com/#/file/e653b4d75cc02da5ea258be5b1c1eb6feed9586fa6b977eb570a188a38783e66/detection>

**4.2 SysInternals AutoRuns**

除了反病毒软件外，我们还调查了SysInternals AutoRuns工具对这些修改的具体反应。

我们使用计划任务创建了与修改版二进制文件有关的任务，以此简单实现了本地持久化机制。AutoRuns可以用来检测这类Windows持久化方法，然而，默认情况下，它并不会显示与修改版程序有关的任务。

默认设置下，AutoRuns会隐藏“微软”的计划任务，如下所示。

AutoRuns的默认设置如下：

修改默认配置后，我们就可以发现伪装的“微软”计划任务。

**五、总结**

****

根据以上观察结果，我们可以得出一个非常明显的结论，那就是某些防病毒软件以及端点检测和响应（EDR）工具容易受到元数据以及数字签名的欺骗，因此难以有效胜任蓝方角色。在无法避免磁盘操作的情况下，红方操作人员在未来对抗中可以充分利用这一点。

本文翻译自threatexpress.com [原文链接](http://threatexpress.com/2017/10/metatwin-borrowing-microsoft-metadata-and-digital-signatures-to-hide-binaries/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **興趣使然的小胃** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/87015](/post/id/87015)

安全客 - 有思想的安全新媒体

本文转载自: [threatexpress.com](http://threatexpress.com/2017/10/metatwin-borrowing-microsoft-metadata-and-digital-signatures-to-hide-binaries/)

如若转载,请注明出处： <http://threatexpress.com/2017/10/metatwin-borrowing-microsoft-metadata-and-digital-signatures-to-hide-binaries/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p3.ssl.qhmsg.com/dm/200_200_100/t0104d1b8b4ca36e961.jpg) 興趣使然的小胃

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

