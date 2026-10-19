# 任意RAT改加载器Bypass

阅读量 **218171**

|评论 **3**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-06-29 10:30:52

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

## 前言

​ 沉寂许久，时隔良久，赴当年之约，感触良多。百川赴海返潮易，一叶报秋归树难。今天分享一篇任意RAT Bypass杀软的思路，
**提供思路仅供参考，不提供任何源码** 。文章中提到的地方若有错误的地方请指正。

直入主题，目前RedTeam的主流RAT无非就Cobalt
Strike。其他的RAT大多基于C/C#开发（这里不做讨论），小众点的RAT，BUG，兼容性等一系列体验感不是很好。而Cobalt
Strike的特征已经被各大厂商记录到特征库中，所以用Cobalt Strike做Bypass的效果并不是很友好。

此次测试使用的杀毒软件是国内企业杀软，以及Tinder（自行翻译，懂得都懂，毕竟ByPass见光死），RAT使用的是gh0st的变种。
**（使用gh0st原因简单阐明：特征多，容易被杀）**

## 正文

###  0X00

​ 这里笔者拿国内的老版本RAT进行测试。仅提供研究思路，不提供任何源码。

ShellBase、ShellCode、RomteLoad工程源码使用VS2010编译，念旧。在打开的时候默认VS2019，见谅！Gh0st源码使用VC++6.0编译。

之前研究目前主流的RAT以及国内一些老版本的RAT，这里笔者就拿国内的老版本RAT进行测试。因为较CS，国内老版RAT特征多能够更好的体现笔者的思路。

###  0X01

​
国内的RAT是基于gh0st以及gh0st的变种。知名的如大灰狼、灰鸽子等。其中，主流的写法是功能插件化（功能插件化，这一点跟CS差不多，插件化的优越性大家都知道的，（简单概括就是：方便、快捷），然后用外壳内存加载功能插件，主机上线后通过IOCP协议传输来调用功能，形成Payload
— Server ==> Client为一体的工作环境。

服务控制端过程大概是：

功能集成Server.dll => 16进制加密Server.dll => 外壳Install解密内存加载Server.dll => 生成二进制可执行文件

###  0X02

​ 经分析发现现在的杀毒对于这种写法基本看的很死 比如某企业杀软会把一个exe文件区块化去查杀
导致实际操作去Bypass时，做好的Server端一次Bypass基本2-5天就被再次查杀。

原因：Bypass基本思路都是 杀小红伞基本去处理输入表 杀QVM一般处理代码段。所以，从根本上来看是没改变这种写法的

笔者的思路是通过下载把Server.dll直接下载到内存里，然后再执行。

过程大概是：Server.dll => 16进制加密Server.dll => 把Server.dll放到下载地址然后base64加密 =>
加载器解密地址下载到内存执行

**这种思路对Cobalt Strike也适用，笔者可以准确标明，经本人亲自测试可行。**

###  0X03

![](https://p0.ssl.qhimg.com/t01216784fbcc79513b.png)

ShellBase是写的对地址进行base64加密的工具

![](https://p5.ssl.qhimg.com/t01b53897990b45dbe4.png)

Shellcode是更改对Server.dll的16进制加密器

![](https://p2.ssl.qhimg.com/t0156df703c4475d55f.png)

首先生成一个Server.dll 然后生成加密器和Url加密器。

![](https://p5.ssl.qhimg.com/t0130fac9e4d7411f42.png)

通过查杀发现被杀

运行ShellCode加密Server.dll后查杀可发现已经不杀了

![](https://p1.ssl.qhimg.com/t0113bffb6352469ad1.png)

笔者来对比一下ShellCode加密前后的Server.dll

![](https://p2.ssl.qhimg.com/t010e0d2cf12f90e4b4.png)

![](https://p4.ssl.qhimg.com/t01ab3f303077aa2cd1.png)

![](https://p1.ssl.qhimg.com/t0197c1fc8b60ce92c8.png)

可以看到是经过加密且Bypass。

接下来笔者把加密好的Shellcode.dll放到Http下载地址里。（Http下载服务器搭建，笔者在这里就不详细说明）  
将URL:<http://URL/ShellCode.dll>
加密，得到加密过后的下载地址：TVFRVR8KClxLT0ATExMLQxYWFxcLS0BRCmxLUUBXS0BRBXZNSldRRlBRC3VASlVJQAt3QElAU0RLRkALdFBAV1xmSUxAS1ELcHdpJQ==

在这里有一个注意点，笔者用的这个地址加密不只有Base64，还有Rc4，所以大家解不开是正常的。

![](https://p4.ssl.qhimg.com/t01dbb1e88c23f5e529.png)

这就是上面提到的思路，他是一个加载器（或者通俗点下载者），其作用是：

解密 ==> 加密后的地址 ==> 下载文件到内存 ==> 执行

测试上线，这里选择虚拟机测试，懂得都懂，毕竟后门或者啥的我也没仔细去看。

![](https://p5.ssl.qhimg.com/t012c1e4f4d2e9f7362.png)

经测试，国内企业杀软，以及Tinder无感执行。至于微步云沙箱或者别的沙箱，笔者就不上传了，免得被记录特征导致代码失效。

这个思路基本印证了笔者的想法 ，某企业杀软对于二进制文件是区块化的查杀。这个笔者是研究yara规则时发现的。好了，笔者思路分享就到此结束，大家再会！！！

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **ShadowJe** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/245231](/post/id/245231)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [恶意软件](/tag/恶意软件)
  * [红蓝对抗](/tag/红蓝对抗)

 **+1** __1赞

 __收藏

![](https://p3.ssl.qhimg.com/t010373d19354927ed5.png) ShadowJe

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

