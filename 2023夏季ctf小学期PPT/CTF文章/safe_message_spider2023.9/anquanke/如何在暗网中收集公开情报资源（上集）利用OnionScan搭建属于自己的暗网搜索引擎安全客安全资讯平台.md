# 如何在暗网中收集公开情报资源（上集）：利用OnionScan搭建属于自己的暗网搜索引擎

阅读量 **564298**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2016-08-11 14:36:12

 **x**

##### 译文声明

本文是翻译文章，文章来源：安全客

原文地址：<http://www.automatingosint.com/blog/2016/07/dark-web-osint-with-python-and-onionscan-part-one/>

译文仅供参考，具体内容表达以及含义原文为准。

文章结构

一、暗网科普

二、自己动手，丰衣足食

三、服务器搭建－DigitalOcean Droplet虚拟服务器

四、配置运行环境－Golan和OnionScan

五、编写OnionScan封装脚本（Python）

六、运行结果

七、参考链接

**（一）、暗网科普**

Dark
Web，即暗网（又名深网）。其实它并没有我们想象中那样的神秘。暗网资源指的是哪些存储在网络数据库中，但是又不能通过普通的超链接来访问到的那一部分资源集合。据不完全统计，暗网中的网站比我们通过普通手段可以访问到的网站要多出好几个数量级。互联网比人们想象的要庞大得多，类似Google和微软Bing等搜索网引擎只收录了目前互联网中大约5%的内容。虽然这些网站是真实存在的，但是它们并没有被任何常用的搜索引擎编列索引，以至于很少有人能够找到这些网站。

在这种情况下，能够搜索到暗网资源的“特殊”搜索引擎就显得非常的“高大上”了。在此之前，美国国防部高级研究项目局（DARPA）曾开展过一个秘密项目，即Memex项目。Memex搜索引擎的核心理念就是“如何挖掘出不易被发现的东西”。DARPA于2015年4月17日正式宣布将Memex项目进行开源，这也就使得用户可以利用这些开源组件来进行高度定制化的搜索。

除了Memex之外，还有一个更加接地气的暗网搜索引擎，它就是[Onion.City](http://onion.city/)。Onion.City暗网搜索引擎使用了Tor2web代理技术，通过这种技术可以深度访问匿名Tor网络。但是Onion.City的搜索结果会涉及到地下黑市中的所有商品，包括枪支，毒品，以及盗窃所得的信用卡等非法商品。

**（二）、自己动手，丰衣足食**

看了之前的介绍，有没有想自己动手尝试来实现一个暗网资源搜索工具呢？在此之前，你可能已经听说过一款名叫[OnionScan](https://github.com/s-rah/onionscan)的工具了，这是一个非常棒的工具，你可以用它来扫描暗网中的隐藏服务，并收集一些潜在的泄漏数据。最近，该项目的研究人员对2016年6月份的暗网数据进行了分析和研究，随后便发布了一份[分析报告](https://mascherari.press/onionscan-report-june-2016/)。他们用非常炫酷的视觉效果呈现出了这些分析数据，并且还提供了一些非常详细的描述信息。但是你可能会有两个疑问：首先，该工具可以从暗网中扫描各种资源，那么他们是如何做到的呢？其次，这些炫酷的可视化效果是如何生成的呢？

首先我们需要做以下几件事：

1\. 配置一台能够7*24小时运行的服务器，并在服务器中加载我们的扫描器，因为扫描工作往往需要花费大量的时间。

2\. 在服务器上运行TOR软件。

3\. 安装OnionScan。

4\. 编写Python脚本来实现扫描过程的自动化处理，并管理扫描结果和其他的一些分析数据。

5\. 完善Python代码，提供更多的可视化操作接口。（这一部分内容将会在《如何在暗网中收集公开情报资源（下集）》中进行介绍）

那么，让我们开始吧！

**（三）、服务器搭建－DigitalOcean Droplet虚拟服务器**

如果你在Amazon的云平台上已经拥有了自己的服务器，或者你有自己的Linux服务器，那么你就可以跳过这一步骤了。如果你没有自己的服务器，那么你可以使用我的推荐链接来获取DigitalOcean服务的免费使用权（价值十美金，够用好几个月了）。如果服务到期之后你打算续费的话，那么我就会得到相应的报酬。当然了，你也可以不使用我的邀请链接，直接付费使用服务器。在整个配置过程中，我假设你安装的是Ubuntu
16.04。

1\. 首先你需要做的是，通过点击“创建Droplet（Create Droplet）”按钮来创建一个新的Droplet。

2\. 接下来，选择Ubuntu 16.04，然后选择每月五美金的套餐选项（如果你追求的是更高的性能，你也可以选择其他的套餐）。

3\. 你可以根据自己的需要来选择一个数据中心，然后在页面底部点击“创建（Create）”按钮。

点击了“创建”按钮之后，系统便会开始创建你的Droplet。随后系统便会向你发送一封电子邮件，并告知你如何去访问这台刚刚设置好的Linux服务器。如果你使用的是Mac
OS
X或者Linux系统的话，你可以打开你的“终端”，如果你使用的是Windows，那么请你在操作之前先安装Putty。（点击[这里](https://the.earth.li/~sgtatham/putty/latest/x86/putty.exe)下载Putty）

现在，你就可以使用SSH来访问你的服务器了。使用Windows
Putty的用户可以将电子邮件中提供的服务器IP地址拷贝进来，然后按下“回车键”即可。你将会以“root”用户的身份进行登录，你只需要将电子邮件中附带的登录密码输入进去，就可以成功访问服务器了。

对于Mac OS X用户和Linux用户而言，可以在终端中输入下列命令：

    
    
    ssh root@IPADDRESS

系统可能会要求你输入两次密码，然后你在登录前还需要修改之前的登录密码。当你完成这些操作之后，你就可以正常访问服务器了。

**（四）、配置运行环境－Golan和OnionScan**

在部署Python代码和OnionScan之前，我们还需要对服务器的环境进行配置。请你严格按照我们下方所给出的操作步骤进行操作，无论你使用的是Mac OS
X，还是Linux，或者是Windows，这些操作步骤都是相同的，因为这些命令全部会在服务器端运行。

当然了，你不必手动输入这些命令，复制粘贴也是可以的。每输入完一行命令之后，别忘了按下“回车键”，小心别打错命令了（注意空格和符号）。

    
    
    screen
    apt-get update
    apt-get install tor git bison libexif-dev
    apt-get install python-pip
    pip install stem

现在，我们需要安装Go语言的运行环境，因为OnionScan是采用Go语言进行编写的。Ryan
Frankel此前曾发表过一篇教程（《[只需七步即可在Ubuntu上安装Go语言](http://www.hostingadvice.com/how-to/install-golang-on-ubuntu/)》），所以我在这里直接引用了这篇文章中的命令。

    
    
    bash < <(curl -s -S -L https://raw.githubusercontent.com/moovweb/gvm/master/binscripts/gvm-installer)
    [[ -s "$HOME/.gvm/scripts/gvm" ]] && source "$HOME/.gvm/scripts/gvm"
    source /root/.gvm/scripts/gvm
    gvm install go1.4 —binary
    gvm use go1.4

很好，我们已经安装好Golang了。现在，我们可以利用下列命令来安装OnionScan：

    
    
    go get github.com/s-rah/onionscan
    go install github.com/s-rah/onionscan

现在，如果你只在终端中输入

    
    
    onionscan

按下“回车键”之后，你就会得到“onionscan”的命令行使用信息。如果上述命令能够成功执行的话，那么OnionScan就算安装成功了。如果你在关闭了终端之后，发现无法运行onionscan了，你可以直接输入下列命令来解决这一问题：

    
    
    gvm use go1.4

这行命令应该可以解决你的问题。

现在，我们需要对TOR的配置进行一些改动，以便让我们的Python脚本能够申请到新的IP地址。我们可以利用下面这条命令来实现：

    
    
    tor —hash-password PythonRocks

运行上面这条命令之后，系统将会输出一些数据。在数据的最后一行你会看到类似下面的信息：

    
    
    16:3E73307B3E434914604C25C498FBE5F9B3A3AE2FB97DAF70616591AAF8

复制上面这条数据，然后输入并执行下面这行命令：

    
    
    nano -w /etc/tor/torrc

这行命令会开启一个简单的文本编辑器。现在，跳转到文本的底部（按下CTRL+W,CTRL+V），然后将之前复制的那一串数据粘贴进去，并将数据补充完整：

    
    
    ControlPort 9051
    ControlListenAddress 127.0.0.1
    HashedControlPassword 16:3E73307B3E434914604C25C498FBE5F9B3A3AE2FB97DAF70616591AAF8

现在，按下CTRL+O来写入文件，然后按下CTRL+X退出文件编辑器。现在输入下面的命令：

    
    
    service tor restart

这条命令会重启TOR服务，重启之后我们的配置才会生效。请注意，如果你想要使用除“PythonRocks”以外的其他密码，你就得按照上面的步骤重新进行操作，并将“PythonRocks”替换成你的新密码。除此之外，你还需要修改部分Python代码。

现在，我们的系统环境基本上已经配置完成了。接下来，我们就可以开始着手编写一些代码了。但是现在还剩最后一步操作，就是获取我的.onion地址列表（大约有7182个地址）。这样一来，你的脚本才可以正常扫描暗网中的隐藏服务。

    
    
    wget https://raw.githubusercontent.com/automatingosint/osint_public/master/onionrunner/onion_master_list.txt

我们的配置已经全部完成了，现在就可以将我们写好的Python代码部署进去了。你可以在本地环境中编写代码，如果你愿意的话你也可以选择直接在Linux服务器端进行编写，最终的效果其实是一样的。我个人比较喜欢在自己的本地计算机中使用[WingIDE](https://www.wingide.com/)来编写Python脚本。

关于“screen”命令

你可能已经发现了，在运行上面这些命令之前，都需要先执行“screen”命令。如果你与服务器的连接意外断开了，这条命令可以帮助你保持通信会话的连接状态。

**（五）、编写OnionScan封装脚本（Python）**

虽然OnionScan是一款非常优秀的工具，但是我们还需要对其进行系统化的控制，并根据我们的具体需求来处理扫描结果。除此之外，由于TOR连接有时会非常不稳定，所以我们还需要终止一些无法继续运行的处理过程，并从TOR网络中获取新的IP地址。现在，我们可以新建一个Python文件，然后将其命名为“onionrunner.py”。由于篇幅有限，原文对该脚本的代码进行了较为详细的描述，感兴趣的读者可以阅读原文。在此，我们仅提供了该脚本的[下载地址](https://raw.githubusercontent.com/automatingosint/osint_public/master/onionrunner/onionrunner.py)。

这个脚本的代码量非常大，但是你可以从中学到很多新的Python编码技巧。当然了，你也可以采用这种封装技巧来对其他的扫描软件进行封装。

**（六）、运行结果**

现在，我们可以通过下面这条命令来运行“onionrunner.py”脚本：

    
    
    python onionrunner.py

运行之后，你将会得到如下图所示的输出数据：

打开“onionscan_result”目录之后，你将会看到一个json文件，该文件会以OnionScan所扫描到的隐藏服务名称来命名。只要你有足够的耐心，你可以让这个程序一直运行下去。在下集，我们将会给大家介绍如何去处理这些json文件，并通过可视化效果来呈现出这些数据。

如果你已经迫不及待地想要获取到所有数据的话，你可以点击[这里](https://github.com/automatingosint/osint_public/tree/master/onionrunner)下载所有的扫描结果（总共有8167条扫描结果）。

**（七）、参考链接**

1.OnionScan项目的Github主页：

<https://github.com/s-rah/onionscan>

2.OnionScan的暗网分析报告（2016年6月）：

<https://mascherari.press/onionscan-report-june-2016/>

3.WingIDE官方网站：

<https://www.wingide.com/>

4.Putty下载地址：

<https://the.earth.li/~sgtatham/putty/latest/x86/putty.exe>

5.《只需七步即可在Ubuntu上安装Go语言》：

<http://www.hostingadvice.com/how-to/install-golang-on-ubuntu/>

6.onionrunner.py文件源码下载地址：

<https://raw.githubusercontent.com/automatingosint/osint_public/master/onionrunner/onionrunner.py>

7.完整的扫描结果（总共有8167条结果数据）：

<https://github.com/automatingosint/osint_public/tree/master/onionrunner>

8.Memex项目简介：

<http://www.darpa.mil/program/memex>

9.Onion.City：

<http://onion.city/>

本文翻译自安全客 [原文链接](http://www.automatingosint.com/blog/2016/07/dark-web-osint-with-python-and-onionscan-part-one/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **WisFree** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/84377](/post/id/84377)

安全客 - 有思想的安全新媒体

本文转载自: [安全客](http://www.automatingosint.com/blog/2016/07/dark-web-osint-with-python-and-onionscan-part-one/)

如若转载,请注明出处： <http://www.automatingosint.com/blog/2016/07/dark-web-osint-with-python-and-onionscan-part-one/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __6赞

 __收藏

![](https://p5.ssl.qhimg.com/t014c3fa13dce6c85dd.png) WisFree

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

