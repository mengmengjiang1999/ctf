# 【技术分享】基于检测防御企业无线安全威胁的WIPS设计

阅读量 **181176**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2016-11-01 14:18:23

 **x**

##### 译文声明

本文是翻译文章，文章来源：安全客

译文仅供参考，具体内容表达以及含义原文为准。

****

**作者：**[ **icecolor**](http://bobao.360.cn/member/contribute?uid=775238387)

**稿费：500RMB（不服你也来投稿啊！）**

**投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿**

**传送门**

[**【技术分享】
企业无线安全解决方案——分析无线攻击行为与制定防御规则安全策略**](http://bobao.360.cn/learning/detail/3613.html)

  

**前言**

随着企业对安全的重视，应用于各种网络环境的IPS应运而生。企业无线网络其实是一个脆弱点。

参看360天巡团队的一篇文章[[2015企业无线网络安全报告]](http://www.freebuf.com/articles/wireless/72084.html)，就是一个无线网络缺陷引发的血案。

无线网络出现威胁的时候，不单单是无线网络的威胁，更是 **内网** 威胁！

  

**关于企业无线网络威胁**

简单的画了个图，顺便推荐一下，<https://www.processon.com/>这个在线画图网站，真的很赞。我是刚知道的，大家有做PPT的可以用下。

从图上可知，防火墙并不能保护无线边界的安全，任何一个无线入口，都会成为公司网络沦陷的关键.内网安全、vpn等等。可以具体了解下现流行的无线攻击手段：

**Fake AP**

黑客会生成一个与合法AP SSID一样的恶意热点，然后进行对合法热点进行DOS攻击使其合法客户端连接到hack
AP上从而进行一系列的密码获取和流量窃取用户劫持等。

**Denial of Service**

拒绝服务会导致路由器与客户端断开，崩溃、无限重连。/Deauth解除认证攻击来获取握手包进行暴力破解。

**Rogue AP**

攻击者可以建立一个带有诱惑字样的热点名称，如：SSID=freewif等引诱被害人连接，进行hacking。

**Ad-hoc/私建热点**

上面那文章也提到了天河一号私建热点的情况,员工的私建热点，员工私建热点一但被攻破公司网络将面临严重威胁。

**Router backdoor vulnerability**

最近网络中也爆出了很多关于CISCO、D-link的一系列的后门漏洞和代码执行，还有一些诸如CSRF类的漏洞。都是一些无线安全威胁。

所以，黑客在获得无线网络权限后，假设被攻击者的网段在公司有很高的权限，那后果可想而知。并且，你的VPN网络也会收到威胁。

  

**关于WIPS的设计阐述**

中国的WIPS市场不太多，目前我就知道有几家做了：360-天巡、启明星辰有。然后山东有一个小公司也有叫什么我忘了。绿盟我听别人说有，但我没找到。

国外品牌挺多的，也挺厉害的，我找其中一家公司还要过演示视频，发了十几封邮件，光职业我就换了很多，什么programmer/security
engineer/Student/CTO/连厨师我都写过，可人家没鸟我。

由于是无线网络的原因，IPS还有一部分是一个接收和扫描信号的传感器硬件。我这里也没有那东西，也没办法详细剖析硬件，只说技术层面的东西。

我内心认为的一个WIPS功能：（只是自己的想法，不代表大众）

  

**WIPS的部署与结构**

在公司办公楼内，根据传感器的传输能力来均衡部署。中控服务负责处理数据，服务器负责一些配置运行，控制台负责时时监控无线信息。简单来说它们的工作就是：

入侵检测—传感器—策略执行

  

**入侵检测识别**

**（一）Identify DOS Attack**

DOS攻击有很多种，什么Authentiction Flood 、De-Authentcation Flood、Association
Flood、Beacon Flood 等等。

Deauth
Flood：这个在常见无线攻击中，是最常用的，应该也是最常见的，当Client对AP进行认证的时候，过程可以使用一些Radius、EAP等安全协议来认证Client，然后它们就连在一起了，这时候如果接收到Deauth的框架信息，就会与客户端分离.迫使再次重新连接进行拒绝服务。可以延伸的问题就是1.handshake
被抓2.再次连接的到AP可能是hack AP。

Client和AP之间的连接是通过各种数据帧交换建立起来的，Client与AP连接后，交换了

ManagementFrame，一些身份验证和ASSOC。

我以前在《企业级无线渗透与无线数据浅析》里好像提过Deauth，我曾经把Deauth的数

据和正常数据进行比对，结果是一样的，但比对数据可以识别攻击，就是不能0误报。

这里还面临着一个问题，如果攻击者是单纯的进行拒绝服务，你可以去做出识别并阻断，而如果攻击者的意图在于捕获HandShake进行破解，那你的识别就显得无力，因为一个AP在Client数量很多，数据流畅的时候，基本上第一个Deauth就已经能捕获了。

Identify Rules

其实针对这种攻击呢，称为链路层攻击，在MAC层做这种检测。其实MAC层做检测要比在IP层要好的多，因为IP可以分配给不同的计算机，而MAC都是与计算机网卡相关的地址。计算机的第二链路层负责MAC地址。所以很多针对链路层的攻击的检测都从MAC地址下手。

1\. IPS检测这种攻击只要看到大量的帧之后，就可以启动报警，帧的数量参数由自己来定。

我们可以根据Management Frames的类型和Authentication报文进行检测Deauth：

我自己搞的这个Handshake包为合法数据，Deauth包为我用aireplay发送的包。

2\.
还有就是我之前想过两个方法，可以指定一个阈值为Deauth，收到Deauth报警时，做出判断机制，如果是用于WPA/WPA2的机制，就去警告用户去修改密码。就算hack收到了握手包也没有用.不过这个办法就是麻烦。另一个是根据接受包的一些时间限制，Deauth一般都比合法断连要快。

3\. 其实思路不能全局限于Deauth数据上，我们可以在Client上做一些手脚，例如网卡或者接入点AP什么的有一些限制机制，去阻止Deauth。

4\. 还有一些其他的DOS，举两个例子，一个是针对802.1X的EAPOL Logoff。

还有一个就是Authentication Flood
Attack，这是一种验证请求攻击模式：在这个模式里，软件自动模拟随机产生的mac向目标AP发起大量验证请求，可以导致AP忙于处理过多的请求而停止对正常连接客户端的响应；这个模式常见的使用是在reaver穷据路由PIN码，当遇到AP被“pin死”时，可以用这个模式来直接让AP停止正常响应，迫使AP主人重启路由！

大家都可以根据报文去分析，防御。当然，在WIPS里面，不是单单写入Deauth的防御规则就可以了，一定要每种攻击都防御。

5\. 在802.11W协议中，用了共享密钥技术，密钥在AP和client之间共享，解决了Management
Frames安全但是目前这个标准还没获得更多的系统支持，也许稳定性什么的都有不算太好。

6\. 针对这种链路层的攻击呢，要普及一些MAC Frames的知识，对识别攻击和分析数据很重要。

这是一个完整的MAC
Frames格式，包括三部分：帧头、帧体、帧效验序列。而帧头又包括：帧控制、持续时间、地址、和序列控制信息。帧效验就是CRC效验。帧控制字段是个很重要的东西：

TO/Frome
DS里面的意思可对照http://www.willhackforsushi.com/papers/80211_Pocket_Reference_Guide.
pdf

我上面用红字标识的，都是对检测有用的，这篇PDF有一些解释，没必要把里面的全都贴进来，大家自己看吧，写的很详细。

把这篇PDF后半段读明白，基本明白的也差不多了。

你要对捕获的MAC帧地址进行分析，要分析Frames type ，目的MAC，源MAC，SSID，Channel等信息进行检测。所以MAC
Frames必须要明白一些的。

**  
**

**（二）Identify Fake AP**

在802.1X企业中，最容易遭受到的就是Fake AP了。

不管你的无线是Radius架构，还是AC+AP。这种攻击都是很令人头疼的。

黑客先建立一个与你同SSID的热点，运用DOS Attack将合法Client强制断掉AP，当Client再次执行关联请求时，已经被劫持到Fake
AP上，进行劫持，密码窃取等行为。

Identify Rules

（1）提个简单思路，先将合法的AP MAC加入白名单，之前提过一次：

在WIPS的保护，开始时时监听扫描范围无线热点：

1.发现其SSID与企业热点相同或类似的/无密码保护的，信道异常，应立刻进行阻断，名单规则应为‘非白即黑’。

2.WIPS应设置每个热点的建立时间，并进行记录其运行时间，发现其热点时间不匹配的，应尽快阻断。

（2）还有一种就是基于Timestamp的检测。当一个Fake AP建立的时候，它要创建一个Management Frames
Beacon，每一个客户端都将包含一个Timestamp，这个时间戳应该是逐渐增长的，有一定规律的，是同步的，在802.11里面叫做TSF。而Fake AP
是没这个概念的，会出现一些偏差，老外根据这个写了一个检测脚本，就是预先设定一个值，看看是否会越过这个值。

    
    
    import sys, scapy, datetime
    from scapy.all import *
    from sets import Set
    THRESH = 5
    global ssidDict
    global ssidCnt
    def monitorPackets(p):
            global ssidDict
            global ssidCnt
            if p.haslayer(Dot11):
                    if (p.getlayer(Dot11).subtype==8):
                            ssid = p.getlayer(Dot11).info
                            bssid = p.getlayer(Dot11).addr2
                            stamp = str(p.getlayer(Dot11).timestamp)
                            if bssid not in ssidDict:
                                            ssidDict[bssid] = []
                                            ssidCnt[bssid]=0
                            elif (long(stamp) < long(ssidDict[bssid][len(ssidDict[bssid])-1])):
                                    ssidCnt[bssid]=ssidCnt[bssid]+1
                                    if (ssidCnt[bssid] > THRESH):
                                            print "[*] - Detected fakeAP for: "+ssid
                            ssidDict[bssid].append(stamp)
    interface=sys.argv[1]
    ssidDict = {}
    ssidCnt = {}
    start = datetime.datetime.now()
    sniff(iface=interface,prn=monitorPackets)

它没给使用文档，基本上这种情况加个监听参数就可以了，切记装了Scapy。

**  
**

**（三）Identify Rogue AP**

流氓热点呢，跟上面的Fake AP类似，比如，我在一个商场内，起一个热点，名为：Freewifi，基本上就GG了，在公司，学校，更要多一点。什么CMCC-EDU，ChinaNet……

Identify Rules

（1）对任何信息不匹配的AP都将进行阻断。

针对Rogue AP的检测也是要时时监控MAC地址及SSID，对一些未连接密码或者SSID较为敏感的AP进行隔离阻断。

（2）对白名单的规则设置也要注意：是要只允许指定MAC连接，并且MAC地址唯一。

Rogue AP我觉得不能单纯的是认为是hack AP，我觉得应该严谨点：一切未授权的访问设备！不论其意图！一旦Rogue AP
未被阻止，可能导致ARP中毒，DHCP攻击、STP攻击、DoS攻击等。所以，要预先配置授权列表达到防御效果：

（3）处理 Ad-hoc/私建热点

Ad-hoc是一种自配置网络的移动节点，ad-hoc攻击里面有两个常见的数据流量攻击分类：

1\. DATA traffic attack

2\. CONTROL traffic attack

还有就是私建热点问题，其实这个是很存在安全隐患的，可能一些公司规定不让使用无线网，或者是限制无线网络的热点数量，所以才导致员工私建热点。私建热点会导致热点被入侵攻击威胁到企业网络安全。可能有的员工会觉得把SSID隐藏了就没人找到了。

拜托大哥，一个Kismet+DOS attack就教做人了好不，

Hidden SSID，根本就算不上一个安全机制，你骗你邻居还行，对抗IPS是不可能的。

Identify Rules

（1）所以，第一要杜绝Ad-hoc网络的组建，二是要对传感器覆盖区域进行扫描，不管是隐藏的还是非隐藏的一些未授权SSID，全部阻断。

（2）加强员工教育吧，毕竟这是人为的事。

**  
**

**（四）Defense Router backdoor vulnerability**

D-link，Cisco TP-link等路由器厂商，都供有专门的企业版路由器，或者一些小公司都是直接用的路由器，那么WIPS里面应有检测硬件设备漏洞这一功能，例如有个RouteSploi漏洞框架：

还有一个叫<https://github.com/jh00nbr/Routerhunter-2.0>的路由器扫描器，也不知道这个作者是不是对D-link有意见，放的D-link漏洞最多，虽说D-link漏洞就是很多。

平常用户以及企业安全意识薄弱，对路由器安全更是薄弱，对路由器固件什么的一些升级也不太懂，一个标准的WIPS，这些功能我觉得是该有的。

当扫描出来存在漏洞时，应及时推送补丁供其下载，保证系统安全。

**  
**

**WIPS的其他辅助功能**

**（1）热点阻断**

当我们发现一个有威胁的热点时，我们要将其阻断，阻断方式就为向该AP进行DOS攻击。DOS攻击很多种，上面也说了，什么Auth，Deauth，Assoc。

Auth DOS：

当attacker向AP发送大量伪造的身份验证请求，当AP超出自身承受请求能力时，AP将与Client断开连接

Deauth
DOS：应该是最好用的一种了，不管是攻击还是防御，当攻击者发送取消认证后，客户端会重新进行连接认证，反复取消就可以让Client拒绝服务，根据Airdrop自己写一些规则.

    
    
    #[comments]
    #All lines in this page are commented out
    # The # symbol at the front of a line denotes a commented line
    #airdrop-ng.py rule configuration file
    #a is allow
    #d is deny
    #format is (a or d)/bssid|(any or client mac or list of client macs in format of mac1,mac2,mac3)
    #it is not wise to mix rule types for example
    #d/any|00:17:AB:5C:DE:3A,00:1B:63:00:60:C4,apple
    #While it may work i have no idea result it will have and at this time is not recommended
    #EX d/bssid|mac1,mac2  #note this is not a valid rule just shows format the / and | placement do matter
    #MORE EXAMPLE RULES
    #d/00:1F:90:CA:0B:74|00:18:41:75:8E:4B
    #deny rule with a single client
    #d/any|00:21:E9:3D:EB:45,00:17:AB:5C:DE:3A,00:1B:63:00:60:C4
    #a deny rule for several clients on any AP
    #d/any|any
    #a global deny any any rule
    #A/00:17:3F:3A:F0:7E|00:21:E9:3D:EB:45,00:17:AB:5C:DE:3A,00:1B:63:00:60:C4
    #an allow rule with multiple clients
    #D/00-1E-58-00-FF-5E|00:19:7E:9A:66:96
    #another deny rule with a different mac format
    #d/12:02:DC:02:10:00|any
    #a bssid deny any client rule
    #a/any|any
    #a global allow, no idea why you would wanna use this ;)
    #oui examples
    #d/any|Apple, Inc;APPLE COMPUTER;APPLE COMPUTER, INC.;Apple Computer Inc.;APPLE COMPUTER INC.;APPLE, INC
    #d/any|apple
    #d/action|broadcom #kicks only broadcom devices off actiontech routers
    #d/00:1F:3C|any #kicks all clients that match that oui
    #d/action|00:1F:3C kick any clinets off an actiontec router that match the oui
    #d/action|00:21:E9:3D:EB:45,00:17:AB:5C:DE:3A,00:1B:63:00:60:C4 #kick the following clients off an any actiontech router
    #d/00:17:3F:3A:F0:7E|apple kick any apple device off that ap

所有规则在外的都被打断，就形成了阻断AP。

随意用什么攻击都行，只要将威胁AP阻断就可以了。

**（2）无线追踪，定位，与取证**

我认为，一个合格的WIPS，一定要有的功能：

1\. 获取分析入侵的无线数据，确立证据。联合绘制的区域热点地图，进行定位，保证出现威胁时，除阻断外，立刻定位到热点位置，追踪其溯源。

2\. 每周或者每天生成一份报告，用统计图及其文字形式报告在这一段时间的威胁，那种攻击最多，那里的私建热点、fake AP 最多等…..

3\. 也有关于无线蜜罐的东西，感觉也可以用一用，SheepWall+WIPS我觉得就挺好的思路，可以帮助取证。

4\. WIPS也要记录其终端型号，像什么IOS，Android…….

****

**（3）关于Snort**

Snort是一个基于签名检测的开源IDS。比较灵活，它能根据你的配置来进行匹配操作，放点无线方面的规则。规则怎么写大家Google一下就行了，它规则挺活的，也挺有意思的。

Snort的Wips配置：

其实Snort只是个轻量级的IPS，还是有很多不足之处。其实Snort+Wellenreiter+Kismet就能组一个简单的IPS，但是我觉得也就是够研究着玩，真正做到严谨点的，还得是专业的WIPS。

**最完美的WIPS功能一览**

**  
**

**WIPS适用范围、意见与未来走向**

1.其实WIPS的适用范围更多的应该是：企业、军工、以及现在好多普及热点的无线城市。可大大降低无线网络边界安全隐患。

2.结合内网防御功能，抵挡一些mac Spoofing
和ARP毒化，彻底杜绝安全隐患，在传感器中使用几个无线模块，可同时监控多频段，覆盖多个信道，也不要忘记保护Client的安全。

3.看完就想做的，这东西需要一个传感器，非安全公司自己做，不太可能，得买。

4.很多人觉得WIPS没用，威胁没有那么多，抱个电脑跑来跑去不现实。（有一种渗透叫移动渗透，有一种攻击叫做War Driving）

PS：这是早先我用一个Nexus7刷的NetHunter。或者你想体积更小一点，用Nexus5也可以的，连个OTG，就可以搞了。

5.希望大家重视一下无线网络边界问题，我忘记是从谁的微博上看了，说公司HR对安全部门平常看不到有什么事做，工程师好像当时说要是真到了看的出事的时候，就已经麻烦了。不管是不是段子，安全防御，不要等亡羊补牢。

6.希望以后的WIPS，不仅仅是针对于AP热点。对一切无线网设备都有保护，如ZIgbee/bluetooth等。再给个思路，有条件的自己搭建一个CrackOS，然后把每个员工的Hash去跑一下，设置一些弱密码，然后根据结果让员工去修改。嗯,不错。

7.要想买WIPS的，给老东家打个广告：<http://tianxun.360.cn/>，希望再回去能给个工位，不要钻小屋，看妹子不太方便。

8\. 这是我的微博：<http://weibo.com/u/2232769023>

**传送门**

* * *

[**【技术分享】
企业无线安全解决方案——分析无线攻击行为与制定防御规则安全策略**](http://bobao.360.cn/learning/detail/3613.html)

本文翻译自安全客 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **icecolor** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/84825](/post/id/84825)

安全客 - 有思想的安全新媒体

本文转载自: [安全客]()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p4.ssl.qhmsg.com/dm/200_200_100/t01dab5be797e60cce8.jpg) icecolor

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

