# 黑客购买新型WSH RAT最新变种样本攻击银行客户

阅读量 **496785**

发布时间 : 2019-09-15 11:30:51

 **x**

##### 译文声明

本文是翻译文章，文章原作者 安全分析与研究，文章来源：安全分析与研究

原文地址：<https://mp.weixin.qq.com/s/vNw65kP6a1uGT9rn5pi6Ng>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/dm/1024_360_/t01c4f3ea5711f81817.jpg)

WSH
RAT是今年6月2日发布的一款新型的RAT恶意软件，是基于VBS的Houdini蠕虫(H-Worm)的最新变种，Houdini蠕虫最初是在2013年开发和传播的，此新型的WSH
RAT主要通过恶意URL、MHT和ZIP等多种形式进行网络钓鱼攻击主动分发，主要针对银行客户进行钓鱼攻击，同时开发者以订阅方式进行销售，每月支付50美元的客户可以解锁该工具的所有功能，如下所示：

![](https://p0.ssl.qhimg.com/t019b3243b4cef38e6b.png)

该RAT会盗取受害者的网络浏览器和电子邮件客户端的密码、远程控制目标计算机、上传、下载执行文件以及执行远程脚本和命令等，同时它还具有键盘记录，对抗安全软件等多种功能，参考链接：

(<https://www.bleepingcomputer.com/news/security/new-wsh-rat-malware-targets-bank-customers-with-keyloggers/>)

近日安全研究人员近日发现了一个Jar的恶意程序，如下所示：

![](https://p2.ssl.qhimg.com/t01a4ce620255e2546c.png)

笔者对此样本进行了详细分析，发现它应该是WSH RAT的最新变种样本，说明已经有黑产团伙通过购买WSH RAT恶意软件发起网络攻击行为了

WSH RAT样本为一个Jar包的恶意程序，执行流程，如下所示：

![](https://p1.ssl.qhimg.com/t01431e9e24b2062a1a.png)

运行Jar RAT程序，如下所示：

![](https://p2.ssl.qhimg.com/t01e43b1cbf5b4957a6.png)

进程相关的信息，如下所示：

![](https://p5.ssl.qhimg.com/t015e57fc9e82b41a49.png)

执行完之后，执行hliqmPFawG.js恶意脚本，进程信息，如下所示：

![](https://p0.ssl.qhimg.com/t01d0feb9487dc94a2a.png)

通过java程序调用class文件[随机文件名].txt，进程信息，如下所示：

![](https://p5.ssl.qhimg.com/t01fff3f3855dc06bdd.png)

执行之后，从服务器端返回指令，执行键盘记录操作，然后上传用户主机相关信息和键盘记录信息到远程服务器，如下所示：

![](https://p2.ssl.qhimg.com/t019150c7f98ae7c96c.png)

对Jar RAT样本进行详细分析，如下所示：

1.主程序jar包，读取资源文件ycfysuwhlz，然后生成lrefocyhfz.js恶意脚本文件，如下所示：

![](https://p4.ssl.qhimg.com/t016bd19bac1d0323f7.png)

2.生成的lrefocyhfz.js脚本，内容如下所示：

![](https://p0.ssl.qhimg.com/t018971be9d02118472.png)

3.lrefocyhfz.js脚本通过下面的代码解密前面的字符串，如下所示：

![](https://p1.ssl.qhimg.com/t0194a7314b90022f5c.png)

4.解密之后的脚本，内容如下所示：

![](https://p4.ssl.qhimg.com/t01330228e45dbbef41.png)

5.解密之后的lrefocyhfz.js脚本前半部分生成另外一个恶意js脚本hliqmPFawG.js，如下所示：

![](https://p5.ssl.qhimg.com/t0184a6e0237fa4e8f1.png)

6.后半部分，先解密生成一个class文件，并命名为[随机名].txt，如下所示：

![](https://p5.ssl.qhimg.com/t0187046e9da42da338.png)

7.然后检测系统中的java环境 ，如果存在java环境，则直接通过java调用生成的class文件[随机名].txt，如下所示：

![](https://p1.ssl.qhimg.com/t01f1750c4a7c9ce624.png)

8.如果不存在java环境，则从网址<https://posta.co.tz/goz/jre7.zip>
下载jre包，解压之后，设置java环境，再通过java调用class文件，如下所示：

![](https://p4.ssl.qhimg.com/t01a718d54446c1dc51.png)

9.恶意hliqmPFawG.js脚本，内容如下所示：

![](https://p1.ssl.qhimg.com/t01d12971d437457309.png)

10.对脚本进行解密之后，内容如下所示：

![](https://p3.ssl.qhimg.com/t01a950cc364537924f.png)

恶意服务器C&C地址：pluginsrv1.duckdns.org，端口:7756

恶意脚本hliqmPFawG.js

1.设置注册表自启动项，并拷贝自身到相应的目录，如下所示：

![](https://p2.ssl.qhimg.com/t01f4cc22568d1168e6.png)

2.给远程服务器pluginsrv1.duckdns.org，发送相应的指令，等待服务器返回不同的指令，执行不同的操作，如下所示：

![](https://p3.ssl.qhimg.com/t01d5d08f4faf0127af.png)

POST请求过程，如下所示：

![](https://p2.ssl.qhimg.com/t0130e1acd0e4c6cc8b.png)

发送主机相关信息到远程服务器，如下所示：

![](https://p1.ssl.qhimg.com/t01b29c0b7bffd31a01.png)

返回的指令操作，如下所示：

1.断开连接、重启、关机、远程CMD执行、安装SDK，如下所示：

![](https://p3.ssl.qhimg.com/t01c769b721f1581fd5.png)

安装WSH SDK，如下所示：

![](https://p5.ssl.qhimg.com/t017bc31deb838cc1da.png)

2.获取浏览器密码信息，上传到远程服务器，如下所示：

![](https://p5.ssl.qhimg.com/t01d36b955b334122e0.png)

3.更新、卸载，如下所示：

![](https://p3.ssl.qhimg.com/t01117b9202ce21215f.png)

4.下载、上传，如下所示：

![](https://p4.ssl.qhimg.com/t01f381007220d63fdb.png)

5.文件管理、键盘记录、反向代理设置，如下所示：

![](https://p3.ssl.qhimg.com/t018a5256410c1e3b77.png)

6.日志信息、CMD通道、进程信息、关闭安全软件，UAC等，如下所示：

![](https://p0.ssl.qhimg.com/t015eb0b005b06fd210.png)

7.检测、更新状态，如下所示：

![](https://p2.ssl.qhimg.com/t01f723959d71908f09.png)

8.远程执行恶意脚本，结束进程，休眠，如下所示：

![](https://p2.ssl.qhimg.com/t011be7bc5a7741859b.png)

通过java程序调用生成的class文件[随机名].txt

1.分析[随机名].txt的文件结构，如下所示：

![](https://p5.ssl.qhimg.com/t018ed2d5f24444f1dc.png)

2.Jrat程序执行之后，释放/operational下的iiiiiiiiii.class文件到%temp%目录下的随机数字.class文件，然后再通过java加载随机数字.class文件，如下所示：

![](https://p4.ssl.qhimg.com/t010d08495993667751.png)

此样本在VT上查询样本的关联信息，可以看到它是能过钓鱼邮件进行传播感染的，如下所示：

![](https://p1.ssl.qhimg.com/t01f5c887de3d25c109.png)

VT网站上的各种引擎对这个恶意样本的检出率并不高，只有15款引擎能检测出此RAT样本

此样本的IOC信息，各情报厂商可以自查一下

MD5：95014878404D850502BA546A0FEB3CFC

C&C地址：pluginsrv1.duckdns.org

端口：7756

WSH
RAT是一款新型的RAT恶意软件，它会释放各种模块，并通过远程控制对受害者机器下发各种指令，执行相应的操作，目前发现它主要针对银行客户进行攻击，未来会不会在全球爆发，需要持续的关注

本文转自：[安全分析与研究](https://mp.weixin.qq.com/s/vNw65kP6a1uGT9rn5pi6Ng)

本文翻译自安全分析与研究
[原文链接](https://mp.weixin.qq.com/s/vNw65kP6a1uGT9rn5pi6Ng)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **安全分析与研究** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/186552](/post/id/186552)

安全客 - 有思想的安全新媒体

本文转载自: [安全分析与研究](https://mp.weixin.qq.com/s/vNw65kP6a1uGT9rn5pi6Ng)

如若转载,请注明出处： <https://mp.weixin.qq.com/s/vNw65kP6a1uGT9rn5pi6Ng>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [恶意软件](/tag/恶意软件)

 **+1** __1赞

 __收藏

![](https://p0.ssl.qhimg.com/t016695dd24f0873866.png) 安全分析与研究

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

