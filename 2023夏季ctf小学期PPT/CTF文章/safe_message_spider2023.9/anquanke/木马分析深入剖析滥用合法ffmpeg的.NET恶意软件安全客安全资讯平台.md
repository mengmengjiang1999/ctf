# 【木马分析】深入剖析滥用合法ffmpeg的.NET恶意软件

阅读量 **97708**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2017-07-24 12:08:48

 **x**

##### 译文声明

本文是翻译文章，文章来源：malwarebytes.com

原文地址：<https://blog.malwarebytes.com/threat-analysis/2017/07/malware-abusing-ffmpeg/>

译文仅供参考，具体内容表达以及含义原文为准。

译者：[ **shan66**](http://bobao.360.cn/member/contribute?uid=2522399780)

预估稿费：190RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

  

当下，恶意软件的一大发展趋势是，将恶意软件包“纳入”合法应用程序中。因此，在本文中，我们将同读者一道来分析一个下载合法ffmpeg的恶意软件。借助这个应用程序，这款使用.NET语言编写间谍软件貌似简单，但是却有着非常强大的威力。现在，虽然大多数恶意软件都能够在被感染的机器上定期发送截图了，但是这个恶意软件却可以进一步记录完整的视频，从而窥探用户的各种活动。

上述恶意软件家族是由MalwarHunterTeam于2015年首次发现的，最近这种势头正在呈现蔓延之势。

  

**分析的样本**

2a07346045558f49cad9da0d249963f1 – 注入器（JS）

049af19db6ddd998ac94be3147050217 – 可执行文件（C＃）

9c9f9b127becf7667df4ff9726420ccb – 加载器

85d35dd33f898a1f03ffb3b2ec111132 – 最终有效载荷

**下载的插件：**

e907ebeda7d6fd7f0017a6fb048c4d23 – remotedesktop.dll

d628d2a9726b777961f2d1346f988767 – processmanager.dll

  

**行为分析**

JS文件首先将包含的可执行文件放入％TEMP％文件夹中，然后运行它。而可执行文件则利用一个随机的文件名完成自动安装，并在％APPDATA％中创建自己的文件夹。代码的持久性是通过注册表run键来实现的。该恶意软件的另一个副本将被放入启动文件夹中：

在运行期间，可执行文件会在其安装文件夹内创建.tmp文件。这些文件的内容没有进行加密，如果我们仔细观察的话，就会发现它实际上用于记录按键和正在运行的应用程序的相关信息：

我们注意到的另一个有趣的事情是，该恶意软件会下载一些合法的应用程序：Rar.exe、ffmpeg.exe以及相关DLL：DShowNet.dll，DirectX.Capture.dll

此外，我们发现该恶意软件在运行时将关闭并删除某些应用程序。在测试过程中，它从被攻击的机器中删除了ProcessExplorer和baretail。

  

**网络通信**

该恶意软件通过TCP的98端口与CnC服务器进行通信。

如果服务器向客户端发送一个命令“idjamel”，那么客户机就会返回收集到的受害机器的基本信息，例如machinename /
username、安装的操作系统以及正在运行的进程的列表。之后，服务器会向客户端发送相应的配置信息，即目标银行列表。

该Bot将配置信息保存在注册表中：

之后，CnC发送一组Base64编码的PE文件。每个文件的内容都可以通过文件名的前缀来进行识别：非恶意的二进制文件由关键字“djamelreference”标识，恶意插件则由“djamelplugin”标识。

下载DShowNET.dll：

下载插件 – remotedesktop.dll (e907ebeda7d6fd7f0017a6fb048c4d23):

ffmpeg应用程序从下面的URL地址下载：

打开地址我们可以看到一些页面，这可能是攻击者所控制的。 Facebook的按钮指向“AnonymousBr4zil”帐户：

这个bot会向服务器报告正在运行的应用程序，即通过标题栏发送Base64编码的文本：

例如：

    
    
    awt||UHJvY2VzcyBFeHBsb3JlciAtIFN5c2ludGVybmFsczogd3d3LnN5c2ludGVybmFscy5jb20gW3Rlc3RtYWNoaW5lXHRlc3Rlcl0=djamel

解码后的内容：

    
    
    Process Explorer - Sysinternals: www.sysinternals.com [testmachinetester]

  

**解开该恶意软件的神秘面纱**

**脱壳**

该样本是利用CloudProtector加壳的，这一点要特别感谢@MalwareHunterTeam的提示。它使用的加壳软件，与我们之前分析的样本所使用的加壳软件完全相同（之前的分析文字请访问这里）。就像在之前所了解的一样，它使用自定义算法和存放在配置中的密钥来解密有效负载。然后，借助RunPE技术（也称为ProcessHollowing），将解密的可执行文件加载到内存中。

**核心代码**

解压后的有效载荷，含有所有恶意功能。它不会做进一步的混淆处理，所以我们可以轻松地对其进行反编译（可以使用dnSpy），并读取其代码。

我们可以看到一些类，单看其名称就猜到它们的作用，如ProtectMe、ScreemCapture和SocketClient。

首先，我们可以发现这个恶意软件的用途：监视用户，以及为受感染的机器添加后门。

Form1类是主要模块，负责与CnC沟通和协调行动。它包含了用于恶意软件安装的硬编码数据和CnC服务器的地址：

37.187.92.171:98

受害者机器的名称将从二进制文件复制并保存在注册表项中：

如果bot检测到e-Carte Bleue（一款法国支付卡）的软件，它会将相应的字符串添加到标识符中，并向服务器发送相应的附加信息：

这个软件的每个模块都是独立运行的，所以都会开启一个新线程：

  

**视频录制**

我们可以看到负责下载ffmpeg应用程序的代码段：

恶意软件作者的主要目标是窥探用户的银行业务。这就是为什么当受害者打开特定网站，与网上银行相关的时候，录像事件被触发。目标列表由CnC提供，并通过“ve”保存到注册表中，例如：

该软件会定期检查列表中的目标是否已在浏览器中打开。如果检测到，该恶意软件就会开始录像：

函数“VeifyingTime”的作用是将标题栏与提供的字符串进行比较。

然后，在ffmpeg应用程序的帮助下录制视频：

之后，它们被发送到CnC，通过Base64进行编码：

该恶意软件还具有简单截图的功能，并将其保存为JPG格式。图片和捕获的日志由Rar应用程序定期进行压缩处理，然后也将其发送到CnC：

  

**键盘记录器**

类名kyl表示键盘记录器：

它还具有枚举已经打开的窗口的功能：

这是负责创建之前提到的.tmp文件的类。

  

**自我保护**

这个类负责禁用可能用于监控恶意软件活动的应用程序：

  

**插件**

该bot的功能可以通过从CnC下载的附加插件来进一步加以扩展：

根据我们的观察，该bot下载了两个插件，为其提供了典型的RAT功能：

processmanager.dl，写于2015年：

以及remotedesktop.dll，写于2016年：

与主模块和之前提到的插件不同，remotedesk.dll被进行了混淆处理，因此，其类和变量的名称基本就是乱码，猜不出其具体含义：

  

**结束语**

很明显，这个恶意软件是由一个“天真”的家伙编写的。 二进制和通信协议都没有进行有强度的混淆处理。此外，使用的加壳软件也是众所周知的，很容易被破解。
然而，该恶意软件得功能却非常丰富，同时也进行了更积极的保护。不过，该恶意软件具有窥探受害者和植入后门的功能，所以不容轻视，因为即使是一个“天真的”的攻击者，也可以在被忽视时造成很大的危害。

该恶意软件被Malwarebytes识别为Backdoor.DuBled。

本文翻译自malwarebytes.com [原文链接](https://blog.malwarebytes.com/threat-analysis/2017/07/malware-abusing-ffmpeg/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **shan66** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/86475](/post/id/86475)

安全客 - 有思想的安全新媒体

本文转载自: [malwarebytes.com](https://blog.malwarebytes.com/threat-analysis/2017/07/malware-abusing-ffmpeg/)

如若转载,请注明出处： <https://blog.malwarebytes.com/threat-analysis/2017/07/malware-abusing-ffmpeg/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p0.ssl.qhmsg.com/dm/200_200_100/t0137bdcb0fbd458b88.jpg) shan66

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

