# DNSMon：用DNS数据进行威胁发现（2）

阅读量 **205939**

发布时间 : 2021-01-04 14:30:06

 **x**

##### 译文声明

本文是翻译文章，文章原作者 Netlab，文章来源：Netlab

原文地址：<https://blog.netlab.360.com/use-dns-data-produce-threat-intelligence-2/>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t01d713ae2a888aab79.jpg)

## 背景

本文是介绍DNSMon在生产威胁情报(域名IoC)系列文章的第二篇。

为了对抗安全人员的分析，钓鱼域名是恶意样本经常采用的一种技术手段。从字符组成和结构上看，钓鱼域名确实具有混淆视听的功效，但对于DNSMon这种具备多维度关联分析的系统来说，模仿知名公司域名的效果则适得其反，因为这样的域名一旦告警，反而更容易引起分析人员的注意。

本案例从一组疑似钓鱼域名出发，逐步介绍DNSMon是如何利用whois，ICP备案，域名解析内容和图关联等信息，让一组干瘪的域名逐渐一点点丰富起来直至最后恶意定性的。

意料之外的是，随着线索的展开，我们发现这是一起失陷设备数量巨大的安全事件，从我们的数据测算，感染规模远超100w设备。为此，我们进行了较为细致的逆向分析和回溯，但限于篇幅，样本分析细节及其家族演变，将在后续再另起一篇介绍。

通常威胁分析普遍的惯例是先知道样本恶意再逆向,
有时根据DNS数据估算感染规模。这次DNSMon系列文章里揭示的，更多是先根据DNS数据发现异常并定性，再进一步探寻还原事件真相。即从先逆向再统计，变成了先统计再逆向。  
这个顺序的变动，是DNSMon的一小步，却是整个威胁分析分支的一大步。

## DNSMon对未知威胁的预警

2020-11-17，DNSMon系统提示一组域名baidugif[.]com, qqjpeg[.]com, 163pics[.]com,
163image[.]com存在安全威胁，打开一看，域名的特殊构造立刻勾起了我们进一步细致查看的兴趣。

baidu + gif, qq + jpeg, 163 + pics, 163 + image,
看起来像是大厂提供图片服务的域名，难道近期有什么新政策或者新业务，导致几个大公司纷纷加开新的图片服务？不过既然系统提示有安全威胁，是李鬼的可能性更大。

就先从系统汇总的域名基础信息开始，看看有哪些异常的内容。

第一步，从系统提取whois注册信息。一般来讲，合规运营的公司注册信息会规范且完整。

    
    
    [163pics.com](http://163pics.com/)     createddate                 2020-11-12 12:26:17
    [163pics.com](http://163pics.com/)     updateddate                 2020-11-12 12:26:17
    [163pics.com](http://163pics.com/)     expiresdate                 2022-11-12 12:26:17
    [163pics.com](http://163pics.com/)     status                      clientDeleteProhibited | clientRenewProhibited | clientTransferProhibited | clientUpdateProhibited
    [163image.com](http://163image.com/)    createddate                 2020-11-12 12:26:17
    [163image.com](http://163image.com/)    updateddate                 2020-11-12 12:26:17
    [163image.com](http://163image.com/)    expiresdate                 2022-11-12 12:26:17
    [163image.com](http://163image.com/)    status                      clientDeleteProhibited | clientRenewProhibited | clientTransferProhibited | clientUpdateProhibited
    [qqjpeg.com](http://qqjpeg.com/)      createddate                 2020-11-12 12:26:17
    [qqjpeg.com](http://qqjpeg.com/)      updateddate                 2020-11-12 12:26:17
    [qqjpeg.com](http://qqjpeg.com/)      expiresdate                 2022-11-12 12:26:17
    [qqjpeg.com](http://qqjpeg.com/)      status                      clientDeleteProhibited | clientRenewProhibited | clientTransferProhibited | clientUpdateProhibited
    [baidugif.com](http://baidugif.com/)    createddate                 2020-11-12 12:26:17
    [baidugif.com](http://baidugif.com/)    updateddate                 2020-11-12 12:26:17
    [baidugif.com](http://baidugif.com/)    expiresdate                 2022-11-12 12:26:17
    [baidugif.com](http://baidugif.com/)    status                      clientDeleteProhibited | clientRenewProhibited | clientTransferProhibited | clientUpdateProhibited
    

查询的结果显示，4个域名的注册信息很一致，注册时间甚至精确到同一秒完成，而且都打开了隐私保护。鉴于百度，腾讯和网易不会走上“分久必合，合久必分”的历史路线，因此不可能存在统一进行域名注册的操作。

李鬼的可能性+1。

第二步，从系统提取ICP备案信息。下面这段话是从域名备案管理系统的政策文件[《工业和信息化部关于规范互联网信息服务使用域名的通知》](https://beian.miit.gov.cn/#/Integrated/lawStatute)摘抄的：

> …进一步规范互联网信息服务域名使用，现就有关事项通知如下：  
>  一、互联网信息服务提供者从事互联网信息服务使用的域名应为其依法依规注册所有。  
>  …

也就是说，在国内合规运营的公司一般都要进行域名备案以正常开展业务，而这4个域名的查询结果是“未备案或备案取消”。

李鬼的可能性+2。

第三步，从系统提取域名的DNS解析信息。

    
    
    2020-11-13 18:18:56     [baidugif.com](http://baidugif.com/)    A       47.100.164.28  37963|Hangzhou_Alibaba_Advertising_Co.,Ltd.
    2020-11-13 18:19:04     [qqjpeg.com](http://qqjpeg.com/)      A       47.116.142.94  37963|Hangzhou_Alibaba_Advertising_Co.,Ltd.
    2020-11-13 18:18:50     [163pics.com](http://163pics.com/)     A       39.98.228.46  37963|Hangzhou_Alibaba_Advertising_Co.,Ltd.
    2020-11-13 17:00:22     [163image.com](http://163image.com/)    A       39.98.228.46  37963|Hangzhou_Alibaba_Advertising_Co.,Ltd.
    

4个域名的活跃时间一致，解析结果看起来还算正常，没有指向同一个IP，但ASN都同属37963阿里云，显然是同一组织或个人所为。

此外，当我们观察这个四个域名的流量曲线，注意到这4个域名活动行为几乎一致。

李鬼的可能性+3。

到这里，这一组域名已经可以标记为99%级别可靠的恶意域名了，但是要将其标注为99.99%可靠的域名的话，我们还需要更多的交叉数据比对。

## 关联

从DNSMon提取的基础信息显示，这组域名就是李鬼无疑了。但系统的安全威胁告警，并不是仅仅依赖这些基础信息做决策得出的，而是借助了更多的数据展开关联分析得出的结论。

关联分析根源于最朴素的想法：“近朱者赤近墨者黑”，和坏蛋打交道大概率不是好人，马老板的朋友圈多数是能人异士。

以4个域名做为种子，从我们的数据得到了下面的关联图：

![](https://blog.netlab.360.com/content/images/2020/12/1-2-1.png)

对于关联图，一方面，是利用其中的样本信息对4个域名进行定性，就是回答域名具体用途是什么，钓鱼？Downloader或是C&C？

分析之后，可以看出系统预警的原因是因为：关联出来的样本，能在VT查询到结果的，比如e64ac44596e1c66036ca3e58c28c24a6，已经被众多杀毒引擎标注有问题；未能在VT查到结果的，比如b4070c64ae268e9edf383b6096a68fc3，图系统也有偏黑的属性标签。而和4个种子域名关联最紧密的b4070c64ae268e9edf383b6096a68fc3
是一个DLL文件，都以TCP：2653和4个域名进行了通信，看起来域名的用途大概率是C&C。

另一方面，关联图可以弥补遗漏的信息。

其中，最有意思的是关联出的一个域名“xia.doubeidong[.]com”，在其上承载着一个URL
“http[:]//xia.doubiedong.com:45678/”，后台服务是国内黑客的最爱HFS。根据页面信息显示，在服务器提供服务的16个小时里，已经有超过700万次的下载。

![](https://blog.netlab.360.com/content/images/2020/11/3.png)

弥补信息的另一个有趣点在URL。

    
    
    http[:]//wx1.sinaimg.cn/large/0082blolly1gkh5uqz322g300g00g7jv.gif  MD5: c3a7d82f39437c624169c59bcdaf0430
    http[:]//tiebapic.baidu.com/tieba/pic/item/e1fe9925bc315c6070d21eae9ab1cb134954772f.jpg  MD5: c3a7d82f39437c624169c59bcdaf0430
    

打开这两个URL，页面显示的是一个很小很模糊的顺时针转动箭头，但是另存为文件后，文件大小却接近571KB，明显是在玩假图片的路数。

至此，利用DNSMon系统，我们从数据层面对这4个域名有了“恶意”的定性。但要解释样本和域名之间的关系，还是要进行简要地逆向分析。

## 逆向定性

经分析，baidugif[.]com, qqjpeg[.]com, 163pics[.]com,
163image[.]com的用途确实是C&C，而xia.doubiedong[.]com则和挖矿有关。

## 样本1分析：b4070c64ae268e9edf383b6096a68fc3

样本b4070c64ae268e9edf383b6096a68fc3，是一个加载器，主要功能是加载运行内嵌在PE资源里的5个恶意的文件。

![](https://blog.netlab.360.com/content/images/2020/12/samp_res.jpg)

其中名为LOL的资源与本案例相关的，因此本文只聚焦LOL文件。

![](https://blog.netlab.360.com/content/images/2020/12/lol_res.jpg)

Dump出LOL的MD5为a20a9e26865291aa651242abcf8a958c，它包含了5个域名 ，比我们从数据观测的角度多一个。

    
    
    [qqjpeg.com](http://qqjpeg.com/)
    [163pics.com](http://163pics.com/)
    [163image.com](http://163image.com/)
    [baidugif.com](http://baidugif.com/)
    [baidupics.com](http://baidupics.com/)
    

LOL运行时会向C&C发送加密的长度10字节的上线信息，以下明文为例

    
    
    6c 36 04 00 00 ff 02 ff 02 ff
    

加密算法RC4, KEY 10字节,

    
    
    0C 22 38 4E 5A 0C 22 38 4E 5A
    

加密后得到BOT向C&C发送的密文

    
    
    6f 50 4f 3a 7b 94 b2 8e ec e6
    

当C&C收到BOT的请求后，向BOT回发的加密的信息

    
    
    ba 0a 43 19 eb 61 9b 1a d3 0c 74 5e d5 c1 ae 59 a0 cf 52 d7 15 35 9b c1 61 07 20 16 93 5f 01 d3 9d ed 05 9c 20 41 83 a9 8b 44 d7 8e de df 21 4a 6b 95 08 6f f6 cc cd 0a 54 7d d5 ea 6b fc 18 46 ec 9d f9 2e fe e7 59 81 63 64 4a 0f c7 05 83 5e fd 58 a6 59 ce f4 f8 ed f8 ba 3a 02 13 89 11 f4 64 a4 b6 60 23 55 7a 50 2e ef 09 de 5a 72 42 a8 3b b5 2d 2f dd 45 d3 ef 5e 94 8d d3 5c 5c f7 e0 ae e1 4e f5 32 13 88 07 5f 45 24 22 11 14 b8 d2 88 f7 73 87 6a b4 f4 a4 76 23 97 4f 08 b5 4a fe f5 2a 57 6e b4 ce 2f 51 05 81 1c 14 93 84 14 bb 3e 85 a0 7c fe 1c 28 18 c1 d8 d5 5c c8 f7 c7 a1 b1 d7 c7 f3 83 34 3b c8 f5 12 0d d4 06 84 5d f2 fd 11 4c 87 05 3e bb 6b 4a 66 0b da b2 d1 68 d7 6f b9 a1 08 dc 8d 40 18 ff af c3 c7 b8 9d de 8f e6 d5 4e 40 8d be 68 d0 60 80 63 84 93 3b 88 6f 33 52 f8 ad 8d 89 8f de 81 ef 24 8a 0d 52 6f 67 3a ae fc 2b fc 4b c8 8b 55 b8 01 c3 91 67 46 fc a4 3d a2 5c 99 a4 48 17 41 6f 48 08 76 3b 8b 50 19 de 8c fc 86 82 ab 42 af fd 7d f6 95 c6 6c e1 98 fb 7f df 2d 98 16 72 dd 1a c0 03 db 06 10 36 f4 e8 8a 49 3a 2e 80 58 87 cb 48 b2 e7 f7 af 73 3e 44 dd 5c db 8b 45 9c 30 74 84 bf 9c 5c 16 69 77 b7 af 5d 26 fa 18 bf f9 52 1f 17 0e 49 b5 ca 94 85 b1 ac d9 eb 26 48 9e fe e4 b5 27 b2 f7 d8 55 02 f9 90 9c 98 37 8f bb 66 f9 3a 99 a0 21 2f 4a e8 bf 63 9a 54 69 08 bf bd 8b e2 80 3d 2d 9b 65 22 5e 9e f1 0f 29 16 dd 97 e7 b1 6e 0c dc 00 3b 1f 0b 77 49 2b a9 ee 78 81 40 db bc 15 26 c4 7c 8a 2a 66 8d fa 3b a8 80 a8 ce f6 5e 04 c0 3b f8 a6 34 fa 8d d7 55 46 67 e7 d8 4d d1 24 79 f7 af 26 fc 90 fd ca 57 35 e5 e4 ce b5 d3 43 8f b4 63 9e 12 67 e3 a5 4e 3d e7 af 14 be fc 29 1f a9 4b 64 5d e9
    

解密算法RC4, KEY 10字节

    
    
    0C 22 38 4E 5A 0C 22 38 4E 5B
    

解密后得到以下URL，可以看出，它们和前文所述”玩假图片的路数的URL”的模式是一样的。

    
    
    https[:]//imglf3.nosdn.127.net/img/T0Jid3A3NGx6NGYwR1RURm53bXUvVnBSMnp4Kyt6NW1rUi9lN29ITDhYSlhOTWxnSHFpMVhRPT0.gif
    https[:]//imglf6.nosdn.127.net/img/T0Jid3A3NGx6NGYwR1RURm53bXUvWXYvd1U3QUt6SXUrNCtvK2JiOXhNY3gvaldBdmlHRWF3PT0.gif
    http[:]//tiebapic.baidu.com/tieba/pic/item/cffc1e178a82b901bc520176648da9773812effd.jpg
    http[:]//tiebapic.baidu.com/tieba/pic/item/cffc1e178a82b901bc520176648da9773812effd.jpg
    http[:]//wx3.sinaimg.cn/large/008elXdrly1glzkcp1nndg300g00gqht.gif
    http[:]//wx2.sinaimg.cn/large/008elXdrly1glzkclznjtg300g00gqht.gif
    

那图片到底是什么呢？以上面URL对应的图片（MD5:6f978ff7382f89d613647283850d4a38）为例，经发析，发现它是一个使用RC4加密，zlib压缩的文件，解密解压后得到下面的最终的业务PE文件（MD5:dd8a3e4e5c84ffb9ec8b845ac687d647），验证了我们最初的判断，”假图片”。

![](https://blog.netlab.360.com/content/images/2020/12/lol_final.jpg)

至此b4070c64ae268e9edf383b6096a68fc3与4个李鬼域名，以及”玩假图片的路数”URL都关联起来了。

## 样本2分析：d8380bf0739384d82aaadc4d36f3abee

样本d8380bf0739384d82aaadc4d36f3abee访问URL下载到的45678.txt文件是一串被加密过的数据：

    
    
    A5CA21A8E6A3DCC0E2B1AE786464602A3F3F7E7F64753E697F6574717F3E737F7D3F6967633F7160793F607562637F7E717C3F76797C753F47555273722623212821232829712673232726232175257228732726292926297426732F7D7564787F742D747F677E7C7F717436797E7C797E752D646265753663787162755B75692D7173717273267176762874737276762476747472232121257322232471272574B1AFA5CA21A8E6A3DCC0E21D1AA3DCC0E221A1B3A4F6A5C8C6A7B1AE532A4C47797E747F67634C797E764C637D63632122683E756875B1AFA3DCC0E221A1B3A4F6A5C8C6A7E4399CFF2
    

这串数据解密后得到有道云笔记的一个URL：

    
    
    http[:]//note.youdao.com/yws/api/personal/file/WEBcb63181389a6c37631e5b8c769969d6c?method=download&inline=true&shareKey=acabc6aff8dcbff4fddb3115c234a75d
    

上述URL下载得到的是一个EXE文件，名为n1.exe或n2.exe:

    
    
    731c9d6e7c77e4f507de16ba8146779b n1_exe_youdao
    b1fd035f4aaba2cd1e56e25e94dd99f3 n2_exe_youdao
    

该文件本质是一个RAR自解压文件：

![](https://blog.netlab.360.com/content/images/2020/12/Snipaste_2020-12-28_15-31-20-2.png)

其中的 audiodg.exe 或 lsmm.exe 文件，是易语言编写的一个 EXE
文件。它在运行过程中会对自身内嵌的PE进行部分数据的替换与组合，并释放出以下两个文件：

  1. servicesXX.exe(XX为2个随机字符)
  2. delziji123.txt(存放自身的文件路径，后续会根据这个路径将自身删除)  
servicesXX.exe 文件中包含另一条有道云笔记的URL：

    
    
    http[:]//note.youdao.com/yws/api/personal/file/WEB7d6e44695d1d0f3e1c0cd07fb4d60643?method=download&inline=true&shareKey=329a77febe53d227a830bd860e10bca9
    

访问该URL下载到hx1.exe文件，该文件即为矿机程序。

## 感染分布

从实际的感染分布来看，中国大陆地区的31个省市均有感染。

![](https://blog.netlab.360.com/content/images/2020/11/4.png)

## 溯源分析

在查看数据的过程中，我们也一直在想，究竟样本是经过什么途径到达了感染的目标？经过溯源，我们还原了感染的路径，如下图。

![](https://blog.netlab.360.com/content/images/2020/12/5.png)

是一个叫NBMSClient的工具一系列的父子进程创建，最终加载了一个名为uwspvps.dll的动态链接库，访问了引起我们注意的4个域名。

通过搜索引擎搜索“NBMSClient”，结果显示是一个网吧相关的运维工具。可以猜测，随着样本被维护通道的不断下发推广，域名和其他诸多线索逐渐汇集到了DNSMon，从而触发了此次预警。

## 结论：

1\. 得益于DNS的基础性，DNSMon具备及时发现不同行业安全威胁的能力
，尤其在现有安全软件无检出，或者是用户没有使用安全安全软件的场景下，这种新维度可以和现有安全产品组成有效的交叉火力。

2\. 网吧运维工具由于安装范围广，应该具备较为专业的安全能力为维护通道保驾护航，防止下发通道被恶意利用。

3\.
为躲避各类安全产品的检测，恶意样本的传播借助了大公司的基础服务，比如本次事件用到了wx1.sinaimg[.]cn，tiebapic.baidu[.]com和note.youdao[.]com提供的图片下载服务。

## IoC

    
    
    域名：
    [baidugif.com](http://baidugif.com/) 
    [qqjpeg.com](http://qqjpeg.com/) 
    [163pics.com](http://163pics.com/) 
    [163image.com](http://163image.com/) 
    [xia.doubiedong.com](http://xia.doubiedong.com/)
    [baidupics.com](http://baidupics.com/)

本文翻译自Netlab [原文链接](https://blog.netlab.360.com/use-dns-data-produce-threat-intelligence-2/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **360网络安全研究院** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/227326](/post/id/227326)

安全客 - 有思想的安全新媒体

本文转载自: [Netlab](https://blog.netlab.360.com/use-dns-data-produce-threat-intelligence-2/)

如若转载,请注明出处： <https://blog.netlab.360.com/use-dns-data-produce-threat-intelligence-2/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [DNS](/tag/DNS)

 **+1** __2赞

 __收藏

![](https://p2.ssl.qhmsg.com/dm/200_200_100/t00df551a583a87f4e9.jpg)
360网络安全研究院

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

