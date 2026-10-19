# 受害者入侵黑客服务器，获取Muhstik解密密钥

阅读量 **647797**

|评论 **1**

发布时间 : 2019-10-12 11:30:23

 **x**

##### 译文声明

本文是翻译文章，文章原作者 安全分析与研究，文章来源：安全分析与研究

原文地址：[https://mp.weixin.qq.com/s?__biz=MzA4ODEyODA3MQ==&mid=2247484990&idx=1&sn=59b80f6e19ac2d69e5831797b759cddd&chksm=902fa916a75820007749657a89423ece1cc666674c23705d4a5a7071661f0c5e998a0242d089&mpshare=1&scene=1&srcid=1009liMe4wFq9wvFFXTlJ6vq&sharer_sharetime=1570626102640&sharer_shareid=3aed1a9e8ca30db91f074b119a150387#rd](https://mp.weixin.qq.com/s?__biz=MzA4ODEyODA3MQ==&mid=2247484990&idx=1&sn=59b80f6e19ac2d69e5831797b759cddd&chksm=902fa916a75820007749657a89423ece1cc666674c23705d4a5a7071661f0c5e998a0242d089&mpshare=1&scene=1&srcid=1009liMe4wFq9wvFFXTlJ6vq&sharer_sharetime=1570626102640&sharer_shareid=3aed1a9e8ca30db91f074b119a150387#rd)

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/dm/1024_724_/t01738a3453ddad0a7f.jpg)

今年九月份以来Muhstik勒索病毒黑产团队通过入侵一些公开的QNAP
NAS设备，使用Muhstik勒索病毒对设备上的文件进行加密，加密后的文件名后缀变为muhstik，如果要解密文件，需要受害者支付0.09BTC(约合700美)的赎金……

此勒索病毒的勒索提示信息，如下所示：

![](https://p3.ssl.qhimg.com/t0122c38649df9b6fc7.png)

近日一名德国的Muhstik勒索病毒受害者在支付了670欧元的赎金之后，对Muhstik勒索病毒解密服务器进行分析，发现黑客所使用的服务器里面包含多个WebShell脚本，很可能这个服务器已经被其他黑客入侵了，通过这些WebShell可以访问PHP脚本，于是他创建了一个PHP脚本，并使用它获取到了黑客服务器数据库上存储的2858个Muhstik解密的密钥

在获取到相应的解密密钥之后，他在论坛发表了这则消息，如下所示：

![](https://p5.ssl.qhimg.com/t017cff4f0b4a02e7dd.png)

并在pastebin.com网站下公布了Muhstik的解密密钥，地址：

<https://pastebin.com/raw/N8ahWBni>

获取到的解密密钥，如下所示：

![](https://p5.ssl.qhimg.com/t01fc8e5ffa3b352622.png)

他在文档中声称：我知道这是非法的，但是我使用的是已经被黑客入侵的服务器，而且我不是坏人……

这位德国的受害者，他被勒索了670欧元，他感觉很伤心，是我，我也伤心，好几千块呢，所以他公布了自己的BTC钱包地址，希望有人能为他的这个行为而支付相应的BTC，得到一定的回报，BTC地址：

1JrwK1hpNXHVebByLD2te4E2KzxyMnvhb

解密工具下载地址：

<https://mega.nz/#!O9Jg3QYZ!5Gj8VrBXl4ebp_MaPDPE7JpzqdUaeUa5m9kL5fEmkVs>

解密工具，使用方法：

1.上传到NAS设备

2.chmod +x decrypt 设置可执行权限

3.sudo ./decrypt YOURDECRYPTIONKEY 使用管理者权限执行，并传入解密密钥

下载解密工具，发现它是使用python脚本编写的，对解密工具进行逆向分析，还原出里面的python脚本，此解密工具会先遍历磁盘，寻找加密的文件或勒索信息文件，如下所示：

![](https://p4.ssl.qhimg.com/t01806fca8b30b2f03f.png)

然后通过解密密钥进行解密，如下所示：

![](https://p0.ssl.qhimg.com/t0152a5d22883735070.png)

10月7号，Emsisoft也发布了可以运行在Windows平台上Muhstik的解密工具，如下所示：

![](https://p5.ssl.qhimg.com/t01cfc89e28c9fc18e8.png)

解密工具下载地址：

<https://www.emsisoft.com/ransomware-decryption-tools/free-download>

打开解密工具，如下所示：

![](https://p4.ssl.qhimg.com/t01e710f3315aaf81aa.png)

Emsisoft确实是一家良心的安全公司，一直在致力于开发和提供各种勒索病毒免费解密工具，此前Emsisoft安全公司的一位勒索病毒解密工具开发者，被全球一百多个勒索病毒黑产团伙跟踪，导致他不断更换住所，这些勒索病毒黑产团伙最后甚至还开发了一款以他的名字为命名的勒索病毒，该安全研究人员的人身安全可能都受到了威胁……

补充：

Muhstik解密python源码

<https://download.bleepingcomputer.com/demonslay335/decrypt_muhstik.py>

使用方法：

usage: decrypt_muhstik.py [-h] -p PASSWORD -d DIRECTORY [-r]

Decrypt Muhstik Ransomware

(c) 2019 Emsisoft Ltd.

optional arguments:  
-h, —help show this help message and exit  
-p PASSWORD, —password PASSWORD  
Password to decrypt with (32 hex characters)  
-d DIRECTORY, —directory DIRECTORY  
Directory to decrypt (recursive)  
-r, —remove Delete the encrypted file if successful (careful!)

例子：

> python decrypt_muhstik.py -p fbb6193d8bbb1ecf7207f12d7c9cd2c8 -d
> D:muhstiktest

最近一两年针对企业攻击的勒索病毒越来越多,不断有新的变种以及勒索病毒新家族出现,真的是越来越多了，各企业一定要高度重视,黑产团伙一直在寻找新的攻击目标……

本文翻译自安全分析与研究
[原文链接](https://mp.weixin.qq.com/s?__biz=MzA4ODEyODA3MQ==&mid=2247484990&idx=1&sn=59b80f6e19ac2d69e5831797b759cddd&chksm=902fa916a75820007749657a89423ece1cc666674c23705d4a5a7071661f0c5e998a0242d089&mpshare=1&scene=1&srcid=1009liMe4wFq9wvFFXTlJ6vq&sharer_sharetime=1570626102640&sharer_shareid=3aed1a9e8ca30db91f074b119a150387#rd)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **安全分析与研究** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/188460](/post/id/188460)

安全客 - 有思想的安全新媒体

本文转载自:
[安全分析与研究](https://mp.weixin.qq.com/s?__biz=MzA4ODEyODA3MQ==&mid=2247484990&idx=1&sn=59b80f6e19ac2d69e5831797b759cddd&chksm=902fa916a75820007749657a89423ece1cc666674c23705d4a5a7071661f0c5e998a0242d089&mpshare=1&scene=1&srcid=1009liMe4wFq9wvFFXTlJ6vq&sharer_sharetime=1570626102640&sharer_shareid=3aed1a9e8ca30db91f074b119a150387#rd)

如若转载,请注明出处：
[https://mp.weixin.qq.com/s?__biz=MzA4ODEyODA3MQ==&mid=2247484990&idx=1&sn=59b80f6e19ac2d69e5831797b759cddd&chksm=902fa916a75820007749657a89423ece1cc666674c23705d4a5a7071661f0c5e998a0242d089&mpshare=1&scene=1&srcid=1009liMe4wFq9wvFFXTlJ6vq&sharer_sharetime=1570626102640&sharer_shareid=3aed1a9e8ca30db91f074b119a150387#rd](https://mp.weixin.qq.com/s?__biz=MzA4ODEyODA3MQ==&mid=2247484990&idx=1&sn=59b80f6e19ac2d69e5831797b759cddd&chksm=902fa916a75820007749657a89423ece1cc666674c23705d4a5a7071661f0c5e998a0242d089&mpshare=1&scene=1&srcid=1009liMe4wFq9wvFFXTlJ6vq&sharer_sharetime=1570626102640&sharer_shareid=3aed1a9e8ca30db91f074b119a150387#rd)

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [恶意软件](/tag/恶意软件)
  * [勒索软件](/tag/勒索软件)

 **+1** __5赞

 __收藏

![](https://p0.ssl.qhimg.com/t016695dd24f0873866.png) 安全分析与研究

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

