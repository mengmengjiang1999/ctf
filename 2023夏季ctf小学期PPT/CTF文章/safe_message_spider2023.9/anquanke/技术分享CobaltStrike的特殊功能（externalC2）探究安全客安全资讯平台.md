# 【技术分享】Cobalt Strike的特殊功能（external_C2）探究

阅读量 **203365**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2017-10-10 13:49:24

 **x**

##### 译文声明

本文是翻译文章，文章来源：安全客

原文地址：<https://outflank.nl/blog/2017/09/17/blogpost-cobalt-strike-over-external-c2-beacon-home-in-the-most-obscure-ways/>

译文仅供参考，具体内容表达以及含义原文为准。

译者：[WisFree](http://bobao.360.cn/member/contribute?uid=2606963099)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**写在前面的话**

本文所介绍的内容并非Cobalt
Strike官方支持的功能，而且我们还没有对这些功能进行完整的测试。如果你想要自己动手进行实验的话，你可以参考[@armitagehacker](https://twitter.com/@armitagehacker)给出的这份参考文档【[点我获取](https://www.cobaltstrike.com/help-externalc2)】。

无论怎样，研究的过程都是充满乐趣的。本文将要介绍的功能可以给我们提供很大的灵活性，并允许我们在一个高度安全的环境中充分利用Cobalt
Strike的强大功能。除此之外，我们也希望这个功能在将来能够正式成为Cobalt Strike官方支持的功能。

  

**External_C2**

我们首先遇到的问题就是需要给C2流量选择一种标准信道，我们的选择对象有DNS、HTTP或HTTPS，但我们认为Mallable格式也许对C2流量的支持会更好，尤其是当我们向一个真实的网站发送非C2流量时（配合Haproxy），效果会比较好。当然了，我们还需要构建我们自己的通信信道并让Cobalt
Strike接管它。除此之外，我们甚至还打算自己搭建一台代理并对特殊的Mallable内容进行解码，将数据通过我们自己的信道发送，然后在我们的重定向器中对Mallable数据重新进行解析，最终将其转发给Cobalt
Strike的Team Server。

当时我还专门向 [@armitagehacker](https://twitter.com/@armitagehacker)
咨询了有没有其他方法可以让我们跟Mallable数据引擎进行交互，他当时提到了一部分实验代码，也许我们可以用这些实验代码来试试看。这个接口名叫“External_C2”，它允许我们使用beacon数据包并通过可选端口与Team
Server进行交互。下面给出的是整个交互过程中的External_C2数据流图：

我们的第三方控制器名叫C2_server，而客户端为C2_client。C2_client将会要求进行第一阶段的通信操作，加载shellcode并与beacon的指定管道进行连接。接下来，C2_client将会从这个指定管道中读取数据包并将其转发给C2_server，然后C2_client便会收到响应数据包以及beacon。C2_clinet与C2_server之间的通信完全取决于开发人员的实现方式，我们可以将beacon数据当作是一种“黑盒”，而你需要确保将其当作一种二进制数据来处理(不能使0x00终结字符串)。

在Cobalt Strike中，这种“未公开的代码”可以被用来运行下面这个脚本：

大家可以看到，现在我们已经设置了一个external_C2监听器，并且正在监听teamserver的2222端口。

**PoC ：beacon与文件共享功能**

@armitagehacker给我们提供了一些样本代码（C语言），其中包含有客户端和服务器端进程代码。将代码按照客户端跟服务器端划分完成之后，我们尝试通过我们自己的通信连接来获取一个可用的beacon通信。实际上，为了方便进行下一步的调试，我决定要将C2_client的数据存储在一份文件之中，然后让C2_server的代码每隔X秒就对该文件的大小进行一次检测。如果大小超过了两个字节，则准备捕获一个新的数据包，然后将其发送给Team
Server。响应数据将会被存储在另一份文件中，而这个文件则交由C2_client来进行处理。这也就意味着，为了让整个通信过程能够正常运行，客户端和服务器端必须要能够对同一目录进行读取和写入。我已经在Samba共享目录以及Owncloud同步目录中进行了测试，测试过程均没有出现任何问题，只不过有时候速度会比较慢罢了。

为了加快开发进度，我用Python对代码进行了重写。这样不仅简化了代码，而且还可以帮助我们更轻松地访问各种通信信道，因为相比于C语言，Python能够让我们的开发变得更加简单。目前为止，我还没有用Python完整实现C2_client，而且Python版的C2_client也无法正常访问指定管道。不过我可以将这些功能放在一个DLL文件之中，然后再在Python代码中调用这些功能就暂时解决这一问题了。

PoC代码：【[点我获取](https://github.com/outflanknl/external_c2)】

我们的Python代码目前仍然需要从DLL文件中调用@armitagehacker给我们提供的功能以执行shellcode，这样就可以正确地与指定管道进行交互了。

当然了，完整的Python版本还是非常好的，但是我自己没有那么多时间去解决指定管道的问题，而且这也是我第一次使用Python来实现C语言下的DLL，再加上我并不是专业的开发人员，所以大家先将就着用吧！

不过就我个人而言，我还是比较希望使用纯Python代码来实现的。

**PoC 演示**

就在我们发布了这个PoC的几个月之后，我们突然发现在客户端部分似乎还可以优化一下。现在你需要知道的是，客户端的网络安装架构其实并不是默认状态的，其中还涉及到高度安全的数据处理流程以及安全风险管控。简单来说，在整个目标网络架构中存在多个“超级安全空间”（Super
Secure Zone），这些空间与普通的组织IT网络以及IT管理空间进行了严格的划分。下面的图片显示的就是这种安装架构：

对于这种特殊的场景，客户端在访问IT管理空间时，我们就可以通过一些网络嗅探以及SMB-relay攻击来尝试接管IT管理空间内的某些账号，并最终登录Bastion主机。

接下来，我们需要从Bastion主机开启一个beacon，并尝试重新连接到我们的Team
Server（处于IT管理空间之中）。但有意思的是，整个系统就跟Bastion主机一样，我们很容易就实现了入侵和重连，而且这里并没有部署任何的管理协议（SMB、WinRM或WMI等等）。除此之外，例如ARP欺骗、ICMP重定向、LLMNR和其他类型的流量攻击方式在网络层也被屏蔽了。唯一可行的出站流量就是从Bastion主机发往超级安全空间（Super
Secure Zone）的网络数据，而入站流量则是针对中央共享文件的web-RDP流量以及SMB流量。

我们将特定文件存放到了共享目录中，然后执行了以下命令：

1\. 攻击者的设备：开启Team Server，加载external.cna文件。

2\. 攻击者的设备：运行C2_server.py。

3\. Baston主机：c2file.exe **\sharesystemsharesubdirTEMPFILENAME**

运行完之后，我们就得到了一个新的beacon！

在下面这张截图中，你可以看到Cobalt
Strike的接口，其中有一个beacon连接到了Bastion主机。下图中已打开的标签截图表明我们使用的是Cobalt
Strike的内置命令。主机桌面上的cmd.exe运行了c2file.exe，而资源管理器窗口中显示的就是共享文件的内容。请注意其中的bea,be*文件，这些文件就是数据交换发生的地方。

  

**绕过空气间隙设备**

虽然本文所介绍的场景是非常特殊的，但我们也在想办法如何将同样的PoC应用到其他场景中。比如说，在面对空气间隙设备时，你可以使用一个便携式的USB设备来当作数据传输载体。但是此时，我们可以让c2file指向这个U盘驱动器的路径，然后通过Team
Server来完成数据的传输。我们在实验室中的测试是成功的，但是数据的传输速率很可能因为环境的不同而发生变化。但从技术角度出发，这也是一种利用Cobalt
Strike的external_C2绕过了空气间隙保护的实例。

本文翻译自安全客 [原文链接](https://outflank.nl/blog/2017/09/17/blogpost-cobalt-strike-over-external-c2-beacon-home-in-the-most-obscure-ways/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **WisFree** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/86980](/post/id/86980)

安全客 - 有思想的安全新媒体

本文转载自: [安全客](https://outflank.nl/blog/2017/09/17/blogpost-cobalt-strike-over-external-c2-beacon-home-in-the-most-obscure-ways/)

如若转载,请注明出处： <https://outflank.nl/blog/2017/09/17/blogpost-cobalt-strike-over-external-c2-beacon-home-in-the-most-obscure-ways/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p5.ssl.qhimg.com/t014c3fa13dce6c85dd.png) WisFree

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

