# 警惕RSA SecurID标题的诱饵文档传播Maze勒索病毒

阅读量 **1054479**

发布时间 : 2019-11-18 12:00:29

 **x**

##### 译文声明

本文是翻译文章，文章原作者 安全分析与研究，文章来源：安全分析与研究

原文地址：<https://mp.weixin.qq.com/s/E1bqAS8bb6apctul0CvZ0Q>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t01f56721e5713cb472.png)

Maze勒索病毒，又称Chacha勒索病毒，是今年5月份由Malwarebytes安全研究员首次发现，此勒索病毒主要使用各种漏洞利用工具包Fallout、Spelevo，伪装成合法加密货币交换应用程序的假冒站点或挂马网站等方式进行分发传播，近日笔者监控到一例通过标题为RSA
SecurID的诱饵文档传播此勒索病毒的最新样本

捕获到的诱饵文档是一个以RSA SecurID为标题的文档，内容如下所示：

![](https://p4.ssl.qhimg.com/t018636a9dac5c75015.png)

文档里面包含恶意宏代码，诱导受害者双击启动宏代码，恶意宏代码，如下所示：

![](https://p5.ssl.qhimg.com/t01180d48ddba2b6f7a.png)

动态调试恶意宏代码，如下所示：

![](https://p4.ssl.qhimg.com/t01d7f3c794fc244353.png)

读取窗体中的数据，然后进行解析，窗体的数据，如下所示：

![](https://p2.ssl.qhimg.com/t019589aaa78dabeff9.png)

宏代码解密窗体中的数据，然后从远程服务器hxxp://149.56.245.196/wordupd.tmp
下载恶意程序到C:WindowsTempered.tmp,然后执行恶意程序，如下所示：

![](https://p1.ssl.qhimg.com/t0166db037b4bbcad20.png)

下载的ered.tmp就是Maze勒索病毒，外壳程序如下所示：

![](https://p0.ssl.qhimg.com/t017c79fb34c7d9c245.png)

分配相应的内存空间，然后解密出勒索病毒的核心代码，如下所示：

![](https://p2.ssl.qhimg.com/t01f1c09182b22b8ba7.png)

再跳转执行勒索病毒核心代码，如下所示：

![](https://p2.ssl.qhimg.com/t0103fae9eb47942ecc.png)

此勒索病毒加密后的文件后缀名为随机文件名，如下所示：

![](https://p1.ssl.qhimg.com/t0189ae8dfd562e3f0b.png)

勒索提示信息文件DECRYPT-FILES.txt，内容如下所示：

![](https://p5.ssl.qhimg.com/t01262b4f0e96485ff7.png)

加密文件之后会修改桌面背景图片，如下所示：

![](https://p4.ssl.qhimg.com/t0169e9eeff338113ab.png)

该勒索病毒解密网站，如下所示：

![](https://p2.ssl.qhimg.com/t01cec14833e25a643a.png)

上传勒索提示信息文件之后，如下所示：

![](https://p5.ssl.qhimg.com/t0157f0330cee0adaef.png)

勒索赎金为:0.13967635
BTC，相当于1200美元，过期翻倍，我去！现在搞勒索都这么黑的，上次还是400美元，这次直接1200美元了，黑客的BTC钱包地址：  
334yPgzDkqD7vvh2GKMrFSQneWVp2onvUq

文档内容上显示的时间为2019年11月12日，估计是12号制作的诱饵文档,最近一段时间一些流行的勒索病毒家族主要使用漏洞和垃圾邮件两种方式进行传播感染，各企业一定要做好相应的防范措施，大部分流行的勒索病毒暂无公开的解密工具，此勒索病毒之前主要使用漏洞利用工具包，通过假虚网站或垃圾网站挂马的方式进行传播，此次又增加了垃圾邮件文档的方式进行传播，可见勒索病毒黑客团伙不断在更新增加自己的攻击传播方式，以获取最大的利益，未来会不会也会利用无文件的方式传播此勒索病毒呢？

IOC  
MD5  
a2d631fcb08a6c840c23a8f46f6892dd  
a0c5b4adbcd9eb6de9d32537b16c423b

C&C  
149.56.245.196  
91.218.114.4  
91.218.114.25  
91.218.114.11  
91.218.114.26  
91.218.114.31

URL  
hxxp://149.56.245.196/wordupd.tmp  
hxxp://91.218.114.4/messages/content/appvsgp.html?kakp=2mj&rkjn=koimf  
hxxp://91.218.114.11/forum/hhiwoqn.action  
hxxp://91.218.114.4/messages/jwt.asp?rgct=dp&gf=m1h&igtu=617lg1ps42&q=0q7r0l6v  
hxxp://91.218.114.25/view/check/fvksl.html?dab=a6tud3  
hxxp://91.218.114.26/archive/pj.jspx?wi=h1265&hi=e  
hxxp://91.218.114.31/support/mkhbm.action?vshw=m627m  
hxxp://91.218.114.11/ticket/nsa.jsp?efd=g0xay3bx&mtu=1  
hxxp://91.218.114.25/pipkl.cgi?ampf=8613eu&cnp=wc6502gj16&q=5m&ycme=35s4b  
hxxp://91.218.114.31/check/s.phtml?uxkv=wjebu46&wmbk=12vc05ja7m  
hxxp://91.218.114.26/support/uuxyhvhu.do?ic=wjpr4uy&lpap=2&edem=62i22cgi41&p=dj6

本文转自：[安全分析与研究](https://mp.weixin.qq.com/s/E1bqAS8bb6apctul0CvZ0Q)

本文翻译自安全分析与研究
[原文链接](https://mp.weixin.qq.com/s/E1bqAS8bb6apctul0CvZ0Q)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **安全分析与研究** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/193032](/post/id/193032)

安全客 - 有思想的安全新媒体

本文转载自: [安全分析与研究](https://mp.weixin.qq.com/s/E1bqAS8bb6apctul0CvZ0Q)

如若转载,请注明出处： <https://mp.weixin.qq.com/s/E1bqAS8bb6apctul0CvZ0Q>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [恶意软件](/tag/恶意软件)
  * [勒索软件](/tag/勒索软件)

 **+1** __0赞

 __收藏

![](https://p0.ssl.qhimg.com/t016695dd24f0873866.png) 安全分析与研究

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

