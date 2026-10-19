# 禁用SMB1协议

阅读量 **415758**

|评论 **1**

发布时间 : 2018-01-31 17:30:41

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t0132d5feaeaf8ffbaa.png)

整理者：cyg07@360CERT

> 一直以来，业界都在致力于解决SMB1协议的安全问题。
>
> 黑客们乐此不疲的进行SMB1漏洞挖掘，协议专家一直布道SMB1的种种是非，犯罪份子直接使用SMB1的“永恒之蓝”漏洞利用框架进行全球范围的网络勒索。
>
> 这一切都像是要让SMB1协议走向尽头似的。
>
> 是时候告别SMB1了吗？

![](https://p4.ssl.qhimg.com/t0183711f65ff2d217f.png)

## SMB的古代史

上世纪1983年初，就职于IBM公司的Barry
Feigenbaum开发了一个网络共享协议，试图让现在听上去已古老的DOS操作系统支持网络文件访问。作者在雏形版本中称呼它
“BAF”，后在正式发版的时候更名为“SMB”(Server Message Block)，最早见于1984年11月8日的IBM Personal
Computer Seminar Proceedings, 卷2。

随后，微软在IBM版本的基础上作了大幅修改，形成通用版本。分别在1987年和1992年将其引入Microsoft LAN Manager和Windows
Workgroups项目， 从此SMB也开启在Windows平台漫长的生涯。

1996年微软的SMB迎来一次不小的挑战，SUN公司强势推出了WebNFS。微软针锋相对，一方面将SMB更名为更通用的CIFS（Common
Internet File System），并递交公开的IETF CIFS
1.0草案。此外继续给SMB/CIFS增加一系列特性，包括符号连接，硬链接等来迎合市场，为减少性能损耗，微软也着手优化掉不必要的NetBIOS协议。

![](https://p2.ssl.qhimg.com/t014a9ff0b8fc230e2b.jpg)

20世纪末，随着微软Windows NT 技术的应用，SMB/CIFS协议更加活跃。因此微软启动“Direct hosting of SMB over
TCP/IP”计划，正式将NetBIOS协议象征性保留，SMB将直接运行于TCP协议之上，端口也
从139/TCP转向445/TCP。同时，IT架构方面也在发生着变化，增加了Kerberos，影子拷贝，服务器互拷等一系列场景需求，为此，专家们在SMB/CIFS上进一步引入了对应的协议扩展。

SMB/CIFS的易扩展性让它在Windows，Linux，NAS等平台或场景中扮演着重要的角色，SMB/CIFS协议支持了超过100条的复杂主指令(Command)。但是SMB相关的文档都是不精确，不完整，不可理解的。SMB/CIFS开始变得臃肿了，自身啰里啰唆的交互让它成了当时的网络资源杀手，很少用户会把它应用在WAN下，甚至一些厂家不得不搭建中间协议缓存系统来提高整体的网络性能。

SMB这样的情况让很多人都很不开心，（当然有些人是很开心的，比如Hackers）。

![](https://p2.ssl.qhimg.com/t01d874c76add7378d0.png)

直到2007年，SMB2项目的出现给SMB协议带来了光明的希望。

至此，第一代SMB协议缝缝补补24年，即SMB1（全名：Server Message Block，曾用名：CIFS，1983年－2007年）。

## SMB1是不安全的

2017年，SMB1已经近34岁了，和很多“出生”于80年代的软件一样，它的设计和出现更多是为了迎合那个已经不再存在的世界。那个还没有恶意攻击行为，还没有海量重要数据，还没有普及计算机的世界。在现在看来，SMB1协议拥有一个“既天真又开放”的一生。

近年负责微软SMB协议项目的专家[NedPyle](https://social.technet.microsoft.com/profile/NedPyle+%5BMSFT%5D)，在Twitter中说了这么一个比喻，“当今社会还在运行SMB1协议就像带着你的祖母去一个热闹的舞会，她是出于好意前往的，但她是真得跳不动了。而且，这可能会是个令人害怕和难堪的事情。”。

SMB1确实给互联网带来过人人恐慌的经历。

2017年3月，早在MS17-010漏洞被WannaCRY勒索蠕虫利用前，微软发布了MS17-10补丁程序并提醒用户这是一个重要更新，用户没有多少感知。安全人员根据补丁文件数字签名发现微软在2月份的时候就知道漏洞细节。4月，著名的黑客组织影子经纪人（The
Shadow
Brockers）发布“永恒之蓝”的完整漏洞利用框架，信息安全行业沸腾了，但用户依然没有太强烈的感知。5月，WannaCRY勒索蠕虫直接利用“永恒之蓝”漏洞和框架配套的“双星脉冲”后门成功扫荡互联网，一时间人人自危，短时间波及150多个国家，超过30万台主机受到影响，有信息表示该攻击事件造成了全球80亿美元的直接经济损失。

“永恒之蓝”是微软SMB1协议漏洞的一个近乎完美攻击利用，能够稳定攻击Windows 2K，Windows
XP，Windows7，Windows8，甚至Windows
10在内的操作系统。SMB1长远的历史地位，大规模用户量和远程网络服务功能，让它的漏洞与生俱来就具备成为最有价值漏洞的资本。实际上，微软的MS17-010系列漏洞拿到了2017安全奥斯卡（Pwnie
Awards 2017）的最佳服务器端漏洞奖，也因其罕见的影响力而被作为一个划时代的漏洞写入到了互联网安全历史。

![](https://p4.ssl.qhimg.com/t01c7effce283d0951a.jpg)

WannaCRY事件之后，安全行业普遍认为互联网安全进入了后“永恒之蓝”时代，但有关微软SMB1协议的安全漏洞还没有结束：

  * 2017年5月，包括CVE-2017-0272, CVE-2017-0277, CVE-2017-0278, CVE-2017-0279的多个可被远程利用的SMB1漏洞曝光；
  * 2017年10月，包括CVE-2017-11781，CVE-2017-11782，CVE-2017-11815，CVE-2017-11780的多个可被远程利用的SMB1漏洞曝光；

衡量微软SMB1在现阶段是否足够安全，举证其发生过的严重漏洞和其近期的漏洞还是比较肤浅的，更需要从当代的安全需求和角度去考虑。2007年至今，微软和业界对SMB作了大幅度改进，修订出了更符合现代安全需求的SMB2,3协议和实现。

对比SMB2, 3协议，使用SMB1将失去SMB2, 3协议上一系列现代化的保护：

  * 攻击面变窄（SMB2+）：SMB1协议命令100条+，SMB2缩减到19条，大幅度降低SMB协议攻击面；
  * 预认证完整性（SMB 3.1.1+），对抗降级攻击。
  * 会话协商安全（SMB 3.0, 3.02），对抗降级攻击。
  * 新加密体系（SMB 3.0+），防止嗅探，中间人攻击。1.1的加密体系性能要优于原体系的签名体系。
  * 恶意SMB访客拒绝机制（Win10+），对抗中间人攻击。
  * 更好的消息签名机制（SMB 2.02+），在SMB2和SMB3中分别使用SHA-256和AES-CMAC替换原有的MD5哈希算法，签名性能有很大提升。

糟糕的是，不管如何提高SMB协议的安全性，只要服务端和客户端支持使用SMB1，中间人攻击就无法避免。黑客只要踢掉SMB2+协议并告诉此路不通，客户端就会主动屁颠的降级到SMB1，和黑客共享通信过程中的一系列消息，除非通信内容本身加密。这并不是小说中的情节，实际攻击是存在的。

## SMB1不是必需的

很长一段时间里工业界都是需要SMB1协议的。NedPyle在微软博客《SMB1 Product
Clearinghouse》一文中，整理了使用SMB1的提供商依然有数十个，而且*nix平台下也有不少SMB协议实现和兼容，比如知名开源软件Samba等。

如果只谈论微软SMB1是不完整的。

![](https://p0.ssl.qhimg.com/t01e4fe2849d53bfec2.png)

很多人都以为Samba是微软Windows NT平台下SMB协议的一个克隆，但回顾历史会发现这并不准确。1992年1月Samba发布了第一个版本，
1993年Windows NT才发布它的第一个版本。除非让Samba研发人员时光穿梭，不然克隆Windows NT的说法不成立。

Samba最初目标是为了兼容DEC公司研发的Pathworks产品，这在当时很流行，主要运行于Ultrix 和VMS操作系统上。Samba作者Andrew
Tridgell试图在一台Sun工作站上完成DEC
Pathworks功能，这可以让他的桌面系统直接访问部门的Unix服务器，作者觉得这很酷。考虑微软桌面系统的垄断地位，Samba在实现时很注意兼容Windows客户端，这也是后来总是被拿出来和Windows
SMB作比较的原因。但这不代表Samba不注重其它客户端的兼容，只能说花在分析微软SMB协议上的时间要比其它客户端要多的多。

![](https://p0.ssl.qhimg.com/t01bcec5cd29b4c482c.png)

Samba的研发团队在过去很长时间里，都在对外声明Samba项目并不是基于黑客式的软件逆向工程得出来的代码。他们并不推崇软件逆向工程，觉得这样的方式得出来的代码不具有可维护性。Samba项目的成功，一方面是得益于SMB/CIFS那些可能不准确，不完整的公开文档（如“draft-leach-cifs-v1-spec-02.txt”），还有被称之为“法国咖啡技术”的方法。

法国咖啡技术，简而言之：一个人想学习法语，没有相关书籍，课程，老师等条件，于是他选择直接前往巴黎现场学习。他走进一个本地咖啡厅，开始观察顾客和服务员间对话，顾客说什么服务员带来什么，一段时间后他学会了“水”，“咖啡”，“面包”等单词，这和学习SMB里的“文件大小”，“时间戳”字段类似。有天他想学习法语骂人，这在咖啡厅很难遇见，于是他故意往服务员身上泼咖啡，服务员随即骂了他一嘴，这和如何确定SMB里的错误码是一个道理。一段时间后他学会了部分单词和基本用法，为掌握更多法语，他开始揣摩组合单词并做成剧本，晚上练习剧本，白天找耐心的服务员对话，通过比较服务员和剧本获得正确法语，同理可以应用在Samba的协议分析上。

Samba研发过程越是艰辛，暗示着SMB1协议的碎片化越严重，那是否也暗示着SMB1的信徒众多，业界离不开它？

![](https://p1.ssl.qhimg.com/t01fbd7d7cb7251ffe6.png)

2007年SMB2项目启动至今，留给SMB1协议的专用场景已经很少了。除非，还有这些看起来“合理”的理由：

  * 因种种原因需要运行Windows XP或Windows 2003系统。
  * 依然使用古老的管理软件，需要 “网上邻居”功能。
  * 古老的打印机，它需要通过扫描共享的方式来工作。

不过看上去，这些使用SMB1的场景只会影响到很小范围的业务和用户。目前相关服务提供商如果不支持SMB2+，那可能他们的业务也到尽头。微软在意识到SMB1问题的严重性后，一直在和存储，打印机，软件应用等领域的合作伙伴推广SMB2+协议的支持与应用。目前Samba，EMC，NetApp，苹果公司的OSX和MacOS都已经支持SMB2，3。

实际上，微软和Samba都已经在新版本中默认禁用了SMB1协议。

![](https://p1.ssl.qhimg.com/t01142eae7f52ca181f.png)

2017年5月WannaCRY勒索病毒事件爆发之时，很多企业选择直接在客户端和交换机上默认禁用139,445/TCP端口通信，并没有听说造成了业务影响（当然这个做法，长期看不见得合理）。专家NedPyle作过一次测试，“禁用SMB1
700天：什么都没发生，就像过去699天一样。任何在我的网络中请求使用SMB1都是违法的。”。

![](https://p0.ssl.qhimg.com/t0176e558eb43ac630d.png)

## 尾声

回过头，SMB1漏洞引爆的WannaCRY勒索蠕虫事件并不是意外，而是一直以来互联网对于最佳安全实践贯彻不坚决的总体反映，是网络安全中的一次“灰犀牛”事件。

![](https://p3.ssl.qhimg.com/t018ba8a9a35d501bed.jpg)

一方面，安全专家需要反思。更多时候，专业安全人员的工作是否应该专注于提高系统的安全性，而非让个人，企业了解得像专业安全人员一样多。做防御的，不应该总想着能阻止攻击，而应该考虑怎么减少攻击面，提高攻击门槛。

另一方面，现代网络中禁用SMB1协议并没有那么难，需要的是关闭它的信心和勇气。

万物互联的大安全时代，是时候行动起来挥手告别SMB1了。

## 引用

  1. <https://www.us-cert.gov/ncas/current-activity/2017/01/16/SMB-Security-Best-Practices>
  2. <https://www.us-cert.gov/ncas/current-activity/2017/03/16/Microsoft-SMBv1-Vulnerability>
  3. <https://support.microsoft.com/en-us/help/2696547/how-to-detect-enable-and-disable-smbv1-smbv2-and-smbv3-in-windows-and>
  4. <https://www.samba.org/samba/docs/myths_about_samba.html>
  5. <https://www.samba.org/ftp/tridge/misc/french_cafe.txt>
  6. <https://blogs.technet.microsoft.com/josebda/2008/12/09/smb2-a-complete-redesign-of-the-main-remote-file-protocol-for-windows/>
  7. <https://blogs.technet.microsoft.com/josebda/2008/12/09/smb2-a-complete-redesign-of-the-main-remote-file-protocol-for-windows/>
  8. <http://ftp.icm.edu.pl/packages/samba/slides/crh-Connectathon-2010.pdf>
  9. <https://support.microsoft.com/en-us/help/204279/direct-hosting-of-smb-over-tcp-ip>
  10. <https://support.microsoft.com/en-us/help/4034314/smbv1-is-not-installed-windows-10-and-windows-server-version-1709>
  11. <https://partnersupport.microsoft.com/zh-hans/par_servplat/forum/par_winserv/smb-v1%E5%92%8Csmb-v3%E7%9A%84%E5%8C%BA%E5%88%AB/9c58a810-8251-4e7c-b651-fad7f662cac7?auth=1>
  12. <http://www.searchsecurity.com.cn/showcontent_94749.htm>
  13. <https://www.theregister.co.uk/2017/01/18/uscert_warns_admins_to_kill_smb_after_shadow_brokers_dump/>
  14. <https://blogs.technet.microsoft.com/filecab/2016/09/16/stop-using-smb1/>
  15. <https://blogs.technet.microsoft.com/filecab/2017/06/01/smb1-product-clearinghouse/>
  16. <https://blogs.technet.microsoft.com/ralphkyttle/2017/05/13/smb1-audit-active-usage-using-message-analyzer/>
  17. <https://blogs.technet.microsoft.com/staysafe/2017/05/17/disable-smb-v1-in-managed-environments-with-ad-group-policy/>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **360CERT安全通告** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/97002](/post/id/97002)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [SMB1协议](/tag/SMB1协议)

 **+1** __1赞

 __收藏

![](https://p4.ssl.qhmsg.com/dm/200_200_100/t013be54b59d8ac5fe6.jpg)
360CERT安全通告

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

