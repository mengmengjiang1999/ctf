# Ryuk勒索病毒更新，俄罗斯黑客团伙幕后开发运营

阅读量 **192866**

发布时间 : 2019-06-24 10:30:03

 **x**

##### 译文声明

本文是翻译文章，文章原作者 CyberThreatAnalyst，文章来源：CyberThreatAnalyst

原文地址：<https://mp.weixin.qq.com/s/HSb06PQQfhLL4uEDyz5DCA>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t014f9e34c43a8e36f7.jpg)

Ryuk勒索病毒最早在2018年8月由国外某安全公司发现并报道，此勒索病毒主要通过垃圾邮件或漏洞利用工具包进行传播感染，相关报道指出Ryuk的代码与Hermes勒索病毒代码非常相似，而Hermes恶意软件则与臭名昭着的朝鲜Lazarus
APT网络犯罪组织有关，那Ryuk勒索病毒是不是也是由朝鲜Lazarus
APT组织运营和传播的呢？其实不是，根据CrowdStrike安全公司的报道说明Ryuk勒索病毒是由黑客组织GRIM SPIDER开发，GRIM
SPIDER自2018年8月以来一直在幕后运营Ryuk勒索软件，攻击的目标主要是一些国外大型企业与机构，从这些大型企业获得高额的赎金，这款勒索病毒曾经还利用TrickBot银行木马的渠道来传播自己，因为TrickBot银行木马传播渠道的运营者是俄罗斯黑客团伙WIZARD
SPIDER，GRIM SPIDER是俄罗斯黑客团伙WIZARD SPIDER的部门之一

Ryuk这款勒索病毒在国外非常流行，国外相关媒体曾报道美国多家大型报社被该勒索病毒攻击，导致发货中断，造成巨大损失，事实上任何一款流行的勒索病毒样本背后都有一个强大的黑产运营团队持续运营，就像GandCrab勒索病毒一样，勒索病毒运营团队负责这款勒索病毒的渠道更新扩展与传播、样本的变种与改进、以及解密赎金的运作等等，Ryuk勒索病毒背后也一定有一支强大的黑客运营团队……

昨天国外恶意样本威胁研究团队MalwareHunterTeam捕获到了一例新的Ryuk勒索病毒变种，该变种添加了一些IP地址黑名单，相匹配的计算机不会被加密，同时这款勒索病毒样本采用了数字签名，使用的数字签名信息，如下所示：

![](https://p1.ssl.qhimg.com/t01ff526826c98e4add.png)

查看证书，如下所示：

![](https://p2.ssl.qhimg.com/t017f79b9722067025e.png)

数字证书的有效期为2019/6/13-2020/6/13，数字证书颁发者机构网站：

<https://www.thawte.com/repository/>

![](https://p0.ssl.qhimg.com/t01ea5b24b3f9ca5188.png)

此勒索病毒运行行为截图，如下所示：

![](https://p0.ssl.qhimg.com/t018c3caad77fee0742.png)

主机文件被加密后的文件后缀名为RYK,如下所示：

![](https://p5.ssl.qhimg.com/t0192b916192561d492.png)

同时生成勒索信息超文本文件RyukReadMe.html，如下所示：

![](https://p0.ssl.qhimg.com/t019a8cbb639d90ae7a.png)

黑客只留下了联系方式，受害者需要联系黑客进行解密，两个邮箱地址，如下：

[sorcinacin@protonmail.com](mailto:sorcinacin@protonmail.com)

[neyhyretim@protonmail.com](mailto:neyhyretim@protonmail.com)

## 勒索病毒核心技术剖析

此变种样本同样采用了代码混淆加壳等技术，通过动态调试，解密出相关的数据，如下所示：

![](https://p0.ssl.qhimg.com/t01f8f502b758ca8088.png)

二次解密数据，如下所示：

![](https://p1.ssl.qhimg.com/t01a5ff4e21c3f3f153.png)

最后再解密出相应的勒索病毒核心代码，经过了三次解密操作，在内存中还原最终的勒索病毒核心Payload程序，如下所示：

![](https://p0.ssl.qhimg.com/t011c20819107a79811.png)

分析勒索病毒核心Payload，可以发现它增加了一IP黑名单字符串，在这些名单之内的主机不会被加密，直接退出，如下所示：

![](https://p1.ssl.qhimg.com/t01ceeb0f2339052115.png)

相应的IP地址字符串列表，如下：

10.30.4、10.30.5、10.30.6、10.31.32

同时它还增加了计算机名与相应的字符串进行比较，如果计算机名中包含这些字符串，则不加密主机，如下所示：

![](https://p0.ssl.qhimg.com/t0158bcf0bf3ad52631.png)

获取的计算机名称与下面的一些字符串：

“SPB”，“Spb”，“spb”，“MSK”，“Msk”和“msk”进行比较， 如果计算机名称包含这些字符串中的任何一个，Ryuk将不会加密此计算机

这款勒索病毒也检测了操作系统语言，如果为相关地区语言的主机，则不加密主机，如下所示：

![](https://p5.ssl.qhimg.com/t01b6cb541dba225800.png)

相关的地区列表，如下：

419(LANG_RUSSIAN 俄 语 )、

422(LANG_UKRAINIAN 乌克兰) 、

423(LANG_BELARUSIAN 白俄罗斯)

可以看到它主要是躲避了俄罗斯的相关地区，以防这些地区的主机被加密

本文转自：[CyberThreatAnalyst](https://mp.weixin.qq.com/s/HSb06PQQfhLL4uEDyz5DCA)

本文翻译自CyberThreatAnalyst
[原文链接](https://mp.weixin.qq.com/s/HSb06PQQfhLL4uEDyz5DCA)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **安全分析与研究** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/180837](/post/id/180837)

安全客 - 有思想的安全新媒体

本文转载自: [CyberThreatAnalyst](https://mp.weixin.qq.com/s/HSb06PQQfhLL4uEDyz5DCA)

如若转载,请注明出处： <https://mp.weixin.qq.com/s/HSb06PQQfhLL4uEDyz5DCA>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [恶意软件](/tag/恶意软件)
  * [勒索软件](/tag/勒索软件)

 **+1** __2赞

 __收藏

![](https://p0.ssl.qhimg.com/t016695dd24f0873866.png) 安全分析与研究

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

