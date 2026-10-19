# 新型勒索病毒NEMTY来袭，GandCrab真的消亡了吗？

阅读量 **390078**

发布时间 : 2019-08-26 14:30:29

 **x**

##### 译文声明

本文是翻译文章，文章原作者 安全分析与研究，文章来源：安全分析与研究

原文地址：<https://mp.weixin.qq.com/s/mFRgTzJihYcj411aCQa-pQ>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t01978c60de1cf65aeb.jpg)

赚了20亿美元的GandCrab勒索病毒运营团队于2019年6月1号宣布停止更新，之后不断有新型的勒索病毒出现，此前Sodinokibi勒索病毒接管了GandCrab的传播渠道，然而赚了那么多的GandCrab勒索病毒运营团伙真的会退出吗？后面会不会换一个勒索病毒家族，继续运营呢？

最近一两年勒索病毒主要是针对企业进行攻击，被加密勒索之后，很多企业、政府、组织为了快速恢复业务都会选择交付赎金或找中介进行解密，不少勒索病毒运营团队这一两年都在背后“闷声发大财”，做黑产的目的是为了快速获利，运营团队会追求利益的最大化，勒索病毒的巨大利益已经让不少其它黑产团伙转行加入进来，这么巨大的利益，GandCrab的运营团伙真的会放弃这么好赚钱的机会？

近日一款新型的勒索病毒被安全研究人员曝光，如下所示：

![](https://p0.ssl.qhimg.com/t0187d97cd607108fb2.png)

评论中提到这款勒索病毒与此前的GandCrab非常相似，同时通过分析发现它与后面出现的Sodinokibi勒索病毒有很多相似之处，如下所示：

![](https://p1.ssl.qhimg.com/t0152645c0b6ff91ac8.png)

国外曾有两篇介绍GandCrab和Sodinokibi两款勒索病毒背后运营团伙和故事的文章，有兴趣的可以参考学习一下，链接：

<https://krebsonsecurity.com/2019/07/whos-behind-the-gandcrab-ransomware/>

<https://krebsonsecurity.com/2019/07/is-revil-the-new-gandcrab-ransomware/>

此新型勒索病毒加密后的文件后缀名为NEMTY，如下所示：

![](https://p5.ssl.qhimg.com/t017c3b4681b9920cf5.png)

生成的勒索提示信息文本文件名为[加密后缀]-DECRYPT.txt，内容如下所示：

![](https://p2.ssl.qhimg.com/t013f96613560aac653.png)

查询此勒索病毒的HASH值，发现它在2019年8月21号，22号，23号都有被人上传到app.any.run网站，如下所示：

![](https://p2.ssl.qhimg.com/t010022453b6212a6fc.png)

下载到相应的样本，发现它的时间戳为2019年8月19号，如下所示：

![](https://p5.ssl.qhimg.com/t010ff82de0be95e6e2.png)

此勒索病毒也采用混淆外壳封装，通过动态调试，可达到OEP，即可获取勒索病毒核心Payload代码，如下所示：

![](https://p3.ssl.qhimg.com/t01facd41686a11ecfe.png)

勒索病毒核心代码，如下所示：

![](https://p0.ssl.qhimg.com/t01a2f9bd2fc1891fbb.png)

此勒索病毒同样会避开一些地区进行文件加密，选择避开的主要地区，如下所示：

Russia 俄罗斯  
Belarus 白俄罗斯  
Kazakhstan 哈萨克斯坦  
Tajikistan 塔吉克斯坦共和国  
Ukraine 乌克兰

遍历磁盘目录，如果为以下目录或目录包含以下字符串，则不加密此目录下的文件，相应的字符串，如下所示：

$RECYCLE.BIN、rsa、NTDETECT.COM、ntldr、MSDOS.SYS、IO.SYS、boot.ini  
AUTOEXEC.BAT、ntuser.dat、desktop.ini、CONFIG.SYS、RECYCLER  
BOOTSECT.BAK、bootmgr、programdata、appdata、windows、Microsoft Common Files

遍历磁盘目录文件后缀名为以下后缀名，则不加密文件，相应的后缀名列表，如下所示：

nemty、log、LOG、CAB、cab、CMD、cmd、COM、com、cpl、CPL、exe  
EXE、ini、INI、dll、DLL、lnk、LNK、url、URL、ttf、TTF、DECRYPT.txt

生成勒索病毒相关信息的JSON文件内容，如下所示：

{“General”: {“IP”:”[IP]”,”Country”:”[Country]”,”ComputerName”:”  
[ComputerName]”,”Username”:”[Username]”,”OS”:”Windows 7”,  
“isRU”:false,”version”:”1.0”,”CompID”:”{[CompID]}”,  
“FileID”:” _NEMTY_ [FileID]_”,”UserID”:”[UserID]”,  
“key”:”PSiOB2jtlqA3RCGLwo2UAQsgt5v98yxj”,”pr_key”:”[pr_key]}

勒索病毒会在C:UsersPanda目录生成勒索病毒配置文件 _NEMTY_7tVsB73_.nemty，查看此配置为文件，内容如下所示

![](https://p1.ssl.qhimg.com/t01a9ea5d65d2a99892.png)

通过TOR访问此勒索病毒解密网站，如下所示：

![](https://p2.ssl.qhimg.com/t015dbd399321d28128.png)

上传生成的配置文件之后，如下所示：

![](https://p1.ssl.qhimg.com/t01f186c3419e5beafe.png)

上传一个加密后的PNG文件，即可得到黑客的BTC钱包地址，如下所示：

![](https://p2.ssl.qhimg.com/t01f054cb7b640c5e24.png)

黑客BTC钱包地址：

3Jn174dUWRTVBwRCnsAjfpbRLo55QXRXwn

经过分析发现，此新型勒索病毒似乎融合了之前GandCrab和Sodinokibi两款勒索病毒的一些特点，但此勒索病毒代码结构与此前两款勒索病毒都不相同，该勒索病毒后期会不会接管GandCrab和Sodinokibi的传播渠道，它与GandCrab和Sodinokibi两款勒索病毒又有什么关系，以及后期会不会流行爆发，需要持续跟踪观察，请各企业做好相应的防范措施，勒索病毒太暴利了，后面一定会有越来越多的新型勒索病毒家族和黑产运营团队加入进来，勒索病毒的重点在于防御

本文转自：[安全分析与研究](https://mp.weixin.qq.com/s/mFRgTzJihYcj411aCQa-pQ)

本文翻译自安全分析与研究 [原文链接](https://mp.weixin.qq.com/s/mFRgTzJihYcj411aCQa-pQ)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **安全分析与研究** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/184994](/post/id/184994)

安全客 - 有思想的安全新媒体

本文转载自: [安全分析与研究](https://mp.weixin.qq.com/s/mFRgTzJihYcj411aCQa-pQ)

如若转载,请注明出处： <https://mp.weixin.qq.com/s/mFRgTzJihYcj411aCQa-pQ>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [恶意软件](/tag/恶意软件)
  * [勒索软件](/tag/勒索软件)

 **+1** __0赞

 __收藏

![](https://p0.ssl.qhimg.com/t016695dd24f0873866.png) 安全分析与研究

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

