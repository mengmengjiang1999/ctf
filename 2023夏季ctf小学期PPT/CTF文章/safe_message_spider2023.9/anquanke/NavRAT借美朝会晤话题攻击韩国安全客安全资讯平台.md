# NavRAT借美朝会晤话题攻击韩国

阅读量 **161434**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-06-05 15:09:06

 **x**

##### 译文声明

本文是翻译文章，文章来源：https://blog.talosintelligence.com/

原文地址：<https://blog.talosintelligence.com/2018/05/navrat.html>

译文仅供参考，具体内容表达以及含义原文为准。

##

##

## 一、前言

Talos最近发现了一份新型的恶意HWP（Hangul Word
Processor）文档，该文档以韩国用户为攻击目标。如果用户打开了恶意文档，就会下载一个远程访问木马（我们称之为NavRAT），该木马能够在受害者主机上执行各种操作，包括命令执行、键盘记录等功能。

诱饵文件名为“미북 정상회담 전망 및 대비.hwp”（美朝会晤展望.hwp），文档中嵌入了一个EPS（Encapsulated
PostScript）对象，以便在受害者系统上执行恶意shellcode，其目的是从被攻陷的另一个网站上下载恶意载荷并加以执行，新下载的恶意载荷也就是本文的主角：NavRAT。

这是一款经典RAT，可以在受害主机上下载文件、执行命令，也具备键盘记录功能。然而，这款木马的命令及控制（C2）架构非常特别。木马使用合法的Naver邮箱平台，通过电子邮件与受害者交互。恶意软件发送电子邮件来上传文件，通过邮件附件来下载文件。之前我们也曾看到恶意软件滥用过免费的邮箱平台，但这是我们第一次看到使用Naver平台的恶意软件，而该平台是韩国内较为知名的平台。

现在我们还有几个问题，其中最有趣的问题之一就是追踪溯源：谁才是这款恶意软件的幕后黑手。前面我们发表过关于Group123的几篇文章（参考[[1]](https://blog.talosintelligence.com/2018/01/korea-in-crosshairs.html&sa=D&ust=1527796940962000)、[[2]](https://blog.talosintelligence.com/2017/11/ROKRAT-Reloaded.html&sa=D&ust=1527796940963000)、[[3]](https://blog.talosintelligence.com/2017/04/introducing-rokrat.html&sa=D&ust=1527796940963000)以及[[4]](https://blog.talosintelligence.com/2018/02/group-123-goes-wild.html&sa=D&ust=1527796940963000)），现在我们有一定的把握认为此次攻击活动以及NavRAT与Group123有关。

##

## 二、恶意文档

###  诱饵文档

此次攻击活动以钓鱼邮件为先锋，钓鱼邮件包含一个HWP文档，文档名为“미북 정상회담 전망 및
대비.hwp”（美朝会晤展望.hwp），该主题借鉴了可能在6月12日举行的[美朝峰会](https://www.cnbc.com/2018/05/31/us-north-korea-meetings-in-new-york-aimed-at-salvaging-summit.html&sa=D&ust=1527796940964000)。文档截图如下所示：

![](https://p3.ssl.qhimg.com/t01490a00605b7e0252.png)

该文档提到了关于美朝会晤的一些疑虑，预计此次峰会将重点关注无核化问题。2018年4月27日，韩国与朝鲜首脑签署了[《为了朝鲜半岛和平、繁荣和统一的板门店宣言》](https://uk.reuters.com/article/uk-northkorea-southkorea-summit-statemen/panmunjom-declaration-for-peace-prosperity-and-unification-of-the-korean-peninsula-idUKKBN1HY193&sa=D&ust=1527796940965000)，此次会晤则是该事件所延伸的一次安排。

该文档中包含前文提到过的EPS对象，用来在目标系统上执行恶意shellcode。这是攻击者在使用HWP文档时常用的攻击方法，我们前面也遇到过并写过分析文档。

###  恶意代码

前面我们也分析过一些恶意文档，从攻击者的角度来看EPS是非常有效的攻击方式，这是一种功能强大的基于栈的脚本语言，如果被恶意使用，可以用来获取其他攻击载荷。文件内容如下所示：

    
    
    /shellcode <90909090909090909090E800<...redacted…>4D2D6DC95CBD5DC1811111111111111> def
    <7B0D0A2756...redacted…>312067657420636C6F736566696C650D0A717569740D0A7D>
    token pop exch pop
    Exec
    

shellcode执行后，首先会执行解密过程，从互联网上下载其他载荷。对于本文分析的这个样本，载荷文件所对应的URI为：

    
    
    hxxp://artndesign2[.]cafe24[.]com:80/skin_board/s_build_cafeblog/exp_include/img.png
    

该网站为一个合法的韩国网站，我们认为该网站已被攻击者攻陷，用来将最终载荷投递到目标系统上。前面我们在分析针对朝鲜半岛的攻击活动中也看到过这种攻击方式。

样本直接下载这个图像文件，然后在内存中加载并执行shellcode。这是典型的无文件执行方式，只会在受害主机的内存中运行恶意进程。样本会使用如下路径来下载并运行解码后的可执行文件：

    
    
    %APPDATA%LocalTemp~emp.exe
    

一旦执行成功，NavRAT会立刻利用`cmd.exe`在目标系统上获取`systeminfo`以及`tasklist`信息，将输出结果写入TMP文件中，并将该文件隐藏在AhnLab目录中。有趣的是，攻击者使用了`>>`操作方法将结果追加到文件中，以便将多个输出结果输入到同一个TMP文件中：

    
    
    "C:Windowssystem32cmd.exe" /C systeminfo >> "C:Ahnlab$$$A24F.TMP"
    "C:WINDOWSsystem32cmd.exe" /C tasklist /v >> "C:Ahnlab$$$A24F.TMP"
    

##

## 三、NAVRAT

###  木马功能

NavRAT是一款远程访问木马（RAT），可以上传、下载并执行文件。被分析的样本中包含许多日志信息。恶意软件作者将每个动作都记录到文件中（经过编码）。在分析样本中，我们往往很难使用攻击者自己提供的日志记录功能来辅助样本分析，但该样本比较特殊，我们可以利用这个功能让分析过程更加顺畅。

![](https://p4.ssl.qhimg.com/t012a8f03e44fdf7e10.png)

如上图所示，恶意软件在使用API注入进程时提供的日志消息。

NavRAT一开始会将自身（`~emp.exe`）拷贝到`%ProgramData%AhnlabGoogleUpdate.exe`路径中，这里恶意软件借鉴的是韩国较为著名的一家安全公司的程序路径：[AhnLab](http://www.ahnlab.com/&sa=D&ust=1527796940968000)。NavRAT随后创建了一个注册表项，以便下次重启系统后能执行文件拷贝操作，这是较为原始的一种本地持久化方法。前文提到过的日志文件与NavRAT处于同一个目录中，这样一来我们也很容易就能找到并分析其日志文件。

NavRAT支持进程注入功能。通过这种方法，它可以将自身注入正在运行的IE进程中，避免以独立进程方式来运行，减少被检测到的几率。恶意软件可以获取目标用户系统上的按键状态：

![](https://p2.ssl.qhimg.com/t01a24e117dedf96d6a.png)

这款RAT最有趣的地方在于C2服务器架构。恶意软件使用了Naver邮箱平台来与实际操作者进行交互。

###  命令与控制方式

恶意软件通过Naver邮箱平台与实际操作者交互，所使用的凭据硬编码在样本文件中：

![](https://p1.ssl.qhimg.com/t01d027ad40df8dc541.png)

然而在我们的调查过程中，NavRAT无法与这个邮箱地址通信：

    
    
    [05/30/2018, 17:39:45]  NaverUpload Start!!
    [05/30/2018, 17:39:46]  NaverUpload :PreUploading success
    [05/30/2018, 17:39:46]   uploading step-1 : HttpSendRequest failed. Err[12150]
    [05/30/2018, 17:39:46]  ////////////// Response Headers getting failure //////////
    [05/30/2018, 17:39:46]  NaverUpload :Uploading failed. Try[0]
    [05/30/2018, 17:39:47]   uploading step-1 : HttpSendRequest failed. Err[12150]
    [05/30/2018, 17:39:47]  ////////////// Response Headers getting failure //////////
    [05/30/2018, 17:39:47]  NaverUpload :Uploading failed. Try[1]
    [05/30/2018, 17:39:48]   uploading step-1 : HttpSendRequest failed. Err[12150]
    [05/30/2018, 17:39:48]  ////////////// Response Headers getting failure //////////
    [05/30/2018, 17:39:48]  NaverUpload :Uploading failed. Try[2]
    [05/30/2018, 17:39:49]   uploading step-1 : HttpSendRequest failed. Err[12150]
    [05/30/2018, 17:39:49]  ////////////// Response Headers getting failure //////////
    [05/30/2018, 17:39:49]  NaverUpload :Uploading failed. Try[3]
    [05/30/2018, 17:39:51]   uploading step-1 : HttpSendRequest failed. Err[12150]
    [05/30/2018, 17:39:51]  ////////////// Response Headers getting failure //////////
    [05/30/2018, 17:39:51]  NaverUpload :Uploading failed. Try[4]
    [05/30/2018, 17:39:52]  UploadProc : UploadFile Err
    [05/30/2018, 17:39:52]  PreCommProc : UploadProc failed
    

之所以通信中断，原因在于Naver采取了防护措施。恶意软件很有可能在太多国家中都执行过，因此该账户目前处于锁定状态：

![](https://p5.ssl.qhimg.com/t01f99af1a6ed8d4b75.png)

![](https://p4.ssl.qhimg.com/t017e8e1bb8cf9300f8.png)

为了重置密码，用户必须提供账户相关信息，或者使用账户所有者的手机进行重置（手机号码归属地为英国）。在目前这种状态下，NavRAT无法正常工作。我们认为恶意软件所有者并不知道Naver已经采取了这种保护机制。

NavRAT可以通过邮件附件来下载并执行文件，也支持删除邮件，同时也能通过Naver账户来发送邮件。我们分析的这个样本会尝试将数据发送给`chioekang59[@daum](https://github.com/daum
"@daum")[.]net`这个地址。

![](https://p3.ssl.qhimg.com/t01bb455a3e9f92e88c.png)

###  历史渊源

在调查过程中，我们尝试过寻找NavRAT的其他样本。我们只识别出2016年5月编译的一个老样本。与本文案例相似，这个老样本使用了一个伪造的AhnLab目录来存放日志文件（`C:\AhnLab\`）。在这个版本中，开发者并没有移除编译路径信息：

    
    
    N:CodeProjectVC_Code ProjectAttack_Spymailacounts.comsrc_total_20160430 - v10.0(DIV)binPrecomExe(Win32).pdb
    

我们可以得出一个结论，那就是NavRAT很有可能从2016年开始就已经存在：我们认为当时所对应的版本号为10.攻击者（们）很可能在人们的眼皮底下隐蔽了许多年，我们认为这款恶意软件很少被使用，只用于非常特定的目标。

##

## 四、与Group123的关联

我们在分析与韩国有关的恶意软件时，总是会看到Group123的身影。我们确定了一些证据点，根据Group123之前所具备的TTPs（战术、技术与步骤），我们有一定的把握认为Group123也参与此次攻击事件中。

此次攻击事件所使用的操作方式与Group123组织相同：将EPS对象嵌入HWP文档中，包含恶意shellcode。嵌入对象的shellcode用来下载某个图像文件，而该文件实际上是一个新的shellcode，用来解码出一个嵌入式可执行文件。我们在之前的攻击活动中曾发现Group123使用过完全相同的方法。其中一个例子就是[ROKRAT](https://blog.talosintelligence.com/2017/04/introducing-rokrat.html&sa=D&ust=1527796940972000)，这是我们在2017年4月份发现的另一款远程访问木马，同样针对朝鲜半岛。

EPS对象所使用的shellcode与这个样本并不完全相同，但包含许多相似之处，比如所使用的指令数量、NOP数量以及几乎完全相同的命令布局。如下图所示，左侧为NavRAT，右侧为ROKRAT的shellcode。

![](https://p2.ssl.qhimg.com/t01d9c8050944a414cd.png)

我们对下载的图像文件中的shellcode做了相同的分析，发现shellcode并不完全相同，但整体设计非常相似。

此外，我们可以拓宽受害者范围，将公共云平台加入C2服务器架构中。攻击者之前使用的是Yandex、Pcloud、Mediafire、Twitter等平台，现在他们使用的是Naver。这个平台主要在韩国境内使用，连接到这个平台的动作很难被定为恶意活动，恶意流量可以隐藏在全局流量中。

基于这些因素，我们有一定的把握认为NavRAT以及此次攻击活动与Group123有关。恶意软件开发者很有可能不是Group123团队中的人，但采用了相同的感染平台以及操作模式。Talos之前发表过关于Olympic
Destroyer的研究结果，我们可以看到其中包含许多虚假标志。当我们分析NavRAT时，我们并没有看到攻击者刻意去这么处理，没有刻意使用IOC或者虚假标志来干扰研究人员的追踪溯源过程。NavRAT没有使用这种虚假标志，因此我们认为其与Group123组织有较为直接的关系。

##

## 五、总结

韩国现在对高级攻击者来说吸引力依然十足，并且仍将保持这个趋势。这个地区具备地缘政治利益，这是神秘的朝鲜与更为开放的韩国必然带来的一个结果。在此次攻击活动中，攻击者使用了经典的HWP文档来下载并执行之前不为人知的恶意软件：NavRAT。恶意软件开发者借助真实事件来伪造钓鱼文件，以美朝会晤为话题吸引目标用户打开恶意文档。

在过去的18个月中，我们观察过与Group123有关的攻击事件，也发表过一些研究成果，这种方法与这些攻击活动有相似之处：shellcode包含一些共同点，最终载荷位于某个图像文件中，托管于被攻陷的某个网站上。攻击者使用了一个开放平台作为C2服务器。在本文案例中，NavRAT使用了Naver这个邮件服务商作为平台，而之前的ROKRAT使用的是云服务提供商。最后，这两者的受害者拓扑信息与目标区域保持一致。这些元素并不能作为严格的证据，断定NavRAT与ROKRAT之前有所关联，但我们有一定的把握认为NavRAT与Group123有关。

从攻击者的角度来看，使用知名的本地云/邮箱服务提供商是非常明智的选择，因为此时想从合法的流量中识别恶意流量是非常困难的一件事。在本文案例中，如果有太多国家/地区尝试访问邮箱的收件箱，那么邮箱服务商就会锁定这个账户。我们在多个开放沙箱系统上识别出了这个样本，我们认为是这些沙箱多次发起了连接请求。

##

## 六、IOC

恶意HWP文档：`e5f191531bc1c674ea74f8885449f4d934d5f1aa7fd3aaa283fe70f9402b9574`

NavRAT：`4f06eaed3dd67ce31e7c8258741cf727964bd271c3590ded828ad7ba8d04ee57`

在线载荷：`hxxp://artndesign2[.]cafe24[.]com:80/skin_board/s_build_cafeblog/exp_include/img.png`

2016年的NavRAT样本：`e0257d187be69b9bee0a731437bf050d56d213b50a6fd29dd6664e7969f286ef`

本文翻译自https://blog.talosintelligence.com/
[原文链接](https://blog.talosintelligence.com/2018/05/navrat.html)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **興趣使然的小胃** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/146816](/post/id/146816)

安全客 - 有思想的安全新媒体

本文转载自:
[https://blog.talosintelligence.com/](https://blog.talosintelligence.com/2018/05/navrat.html)

如若转载,请注明出处： <https://blog.talosintelligence.com/2018/05/navrat.html>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [恶意软件](/tag/恶意软件)
  * [网络攻击](/tag/网络攻击)
  * [NavRAT](/tag/NavRAT)

 **+1** __0赞

 __收藏

![](https://p0.ssl.qhmsg.com/dm/200_200_100/t0104d1b8b4ca36e961.jpg) 興趣使然的小胃

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

