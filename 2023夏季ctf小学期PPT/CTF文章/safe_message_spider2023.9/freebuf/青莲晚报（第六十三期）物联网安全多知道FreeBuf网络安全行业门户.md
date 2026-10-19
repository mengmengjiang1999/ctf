![微信公众号-青莲晚报封面图-58.jpg](https://image.3001.net/images/20191127/1574846394_5dde3fba9a003.jpg!small)**  
**

**恶意软件将路由器捆绑至僵尸网络 黑客可以借此发动DDoS攻击**

 **  
**

[Gafgyt恶意软件](https://www.zdnet.com/article/mirai-gafgyt-iot-botnets-stab-systems-with-apache-struts-sonicwall-exploits/)可以通过小型办公室和家庭路由器的漏洞访问到这些设备。

最近Gafgyt（[也称为Bashlite）](https://www.zdnet.com/article/bashlite-iot-malware-upgrade-lets-it-target-wemo-home-automation-devices/)进行了更新，华为HG532和RealtekRTL81XX一直是Gafgyt的目标，现在还将ZyxelP660HN-T1A列入了攻击目标。

一般情况下，恶意软件都通过扫描程序来查找公网节点，然后利用漏洞实现入侵。专家称，为了在攻击时获得充分资源，新版本的Gafgyt会杀死JenX之类的其他恶意软件，从而使其可以充分利用设备发起攻击。Gafgyt僵尸网络似乎正在直接与另一个僵尸网络JenX竞争，后者的攻击目标正是华为和Realtek路由器。

黑客除了利用 Gafgyt 发起DDoS攻击，还主要将其用于攻击游戏服务器，[尤其是那些使用Valve
](https://www.zdnet.com/article/cyber-crooks-take-aim-at-their-next-big-target-esports-tournaments-and-players/)[Source
Engine](https://www.zdnet.com/article/cyber-crooks-take-aim-at-their-next-big-target-esports-tournaments-and-players/)的游戏，包括热门游戏《反恐精英》和《军团要塞2》。目标服务器不是由Valve部署的，而是由玩家部署的私有服务器。

很多年轻玩家出于报复对手的心态而选择攻击对方。玩家甚至不需要访问地下论坛就可以使用这些恶意服务。专家指出，[僵尸网络租用服务](https://www.zdnet.com/article/ubisoft-to-send-out-cease-desist-legal-letters-to-ddos-for-hire-services/)在Instagram上使用伪造的个人资料做广告，租用费用仅为8美元。

专家介绍说：“显然，他们可以通过该平台接触到大量年轻人，所有人都可以使用这些服务，而且比地下站点更容易访问。”

随着越来越多的物联网产品连接到互联网，如果设备没有保持最新状态[，将设备捆绑到僵尸网络](https://www.zdnet.com/article/iot-security-why-everyone-needs-to-step-to-ensure-the-security-of-the-internet-of-things/)[和其他恶意活动中](https://www.zdnet.com/article/iot-security-why-everyone-needs-to-step-to-ensure-the-security-of-the-internet-of-things/)将会变得更加容易。

新版Gafgyt主要针对的是旧路由器，其中一些已经投放市场长达五年以上。专家建议用户将路由器升级到较新的型号，并应定期应用软件更新以确保设备受到保护，尽可能地抵抗攻击。

Davila说道：“总的来说，用户可以养成习惯，例如更新路由器，安装最新补丁程序，并设置复杂的密码，从而抵御僵尸网络的攻击。”

详文阅读：

<http://hackernews.cc/archives/28015>

**印度官方确认在核电站网络中发现恶意软件**

 **  
**

外媒Ars Technica周三发布的一份报告称，印度核能有限公司(NPCIL)证实，库丹库拉姆核电站的管理网络存在恶意软件。Ars
Technica称，这款恶意软件被认为是Lazarus网络犯罪集团所为。

NPCIL副主任A. K. Nema在一份新闻稿中说道：“当（我们）在2019年9月4日注意到此事时CERT-In已经传达过这一情况。”据悉，CERT-In是印度国家计算机应急响应小组。Nema补充称，印度原子能部门立即对此事展开了调查。

另外据Nema披露，调查显示，受感染的PC属于一名用户，其PC出于管理目的而需连接到互联网。“这些网络正在被持续监控。”

详文阅读：

<http://hackernews.cc/archives/27992>

**无法删除的恶意软件 xHelper 持续感染大量安卓设备**

 **  
**

xHelper 最早发现于 3月。到 8 月，它逐渐感染了 32,000 多台设备。而截至本月，根据赛门铁克的数据，感染总量已达到
45,000。该恶意软件的感染轨迹不断上升。赛门铁克表示，xHelper 每天平均造成 131 名新受害者，每月约有 2400 名新的受害者。

根据 Malwarebytes 的说法，这些感染的来源是“网络重定向”，它会将用户发送到托管Android 应用程序的网页。这些网站指导用户如何从 Play
商店外部间接加载非官方的 Android 应用。这些应用程序中隐藏的代码将下载 xHelper 木马。

好消息是该木马目前没有执行破坏性操作，多数时间它会显示侵入式弹出广告和垃圾邮件通知。广告和通知会将用户重定向到 Play
商店，并要求用户安装其他应用程序——通过这种方式，xHelper 从按安装付费的方式中赚钱。

恼人的是 xHelper 服务无法删除，因为该木马每次都会重新安装自身，即使用户对整个设备进行了出厂重置后也是如此。xHelper
如何在恢复出厂设置后得以生存仍然是个谜。不过，Malwarebytes 和赛门铁克均表示 xHelper 不会篡改系统服务和系统应用程序。

在某些情况下，用户说，即使他们删除了 xHelper
服务，然后禁用了“从未知来源安装应用程序”选项，它还是会在几分钟内重新感染设备。也有少数用户报告说使用某些付费的移动防病毒解决方案取得了成功。

赛门铁克在最新发布的博客文章中表示，该木马正仍在不断发展，定期发布的代码更新解释了为什么某些防病毒解决方案在某些情况下会删除
xHelper，而在更高版本中却不会。

同时，赛门铁克也作出警告，尽管该木马目前从事垃圾邮件和广告收入活动，但它还具有其他更危险的功能。xHelper 可以下载并安装其他应用程序，xHelper
团队可以在任何时候使用该功能来部署第二阶段恶意软件有效负载，例如勒索软件、银行木马、DDoS僵尸程序或密码窃取程序等。

详文阅读：

<http://hackernews.cc/archives/27963>

**SRLabs 发现智能扬声器新漏洞 或变身监听用户的间谍设备**

  

SRLabs 的安全分析师，找到了一种利用 Google 和 Amazon 智能扬声器进行网络钓鱼和窃听用户的新漏洞。 **之后其上传了看似无害的Alexa
Skills 和 Google Actions 自定义操作技能，以测试该漏洞是否会轻易得逞。** 由视频演示可知，一位 SRLabs 研究人员向
Google Home 索要了一个随机数，由其产生并发出声音。

可即便 Actions 已执行完成，程序仍保持后台监听的状态。之后，第三方计算机收到了用户所述内容的抄录。

 **至于 Alexa，安全分析师也创建了一个简单的“星座技巧”，要求 Alexa 对其进行“幸运解读”。**

Alexa 会询问用户的十二星座，之后开始监听相关的星座运势读数、同时麦克风一直在后台保持监听。

即便被告知停止操作，Alexa 仍会继续监听房间内发出的声音，并将其发送至接收端的软件。

此外，研究人员还能够让讲述人发出虚假的错误信息。比如在一分钟后发出另一个伪造的错误，诱骗用户自曝账号密码。

事实上，SRLabs 至始至终都在利用同一个漏洞。 **该缺陷使得他们能够持续地向智能扬声器提供无法言语的一系列字符（U+D801、点、空格）。**

如此一来，即便设备保持着‘静音’的状态，‘算法’也能够维持对用户展开监听的信道的畅通。

鉴于谷歌和亚马逊不会对安装在其智能扬声器上的软件技能展开仔细的检查，恶意团体或轻易将间谍软件添加到应用程序的补丁中，而无需另行通知。

周一的时候，SRLabs 安全分析师决定将漏洞公之于众。但在此之前，其已经向两家公司提出过警告。此外，SRLabs 向 YouTube
上传了一段视频，以展示该漏洞对智能扬声器用户造成的安全隐患。

目前尚没有任何证据表明除 SRLabs 研究团队意外的任何人在使用相关漏洞，不过亚马逊已经实施了相应的对策来检测和防止对 Alexa 技能的滥用。

至于谷歌，该公司也表示更新了审查程序，以揪出这类行为，并移除任何有违操作准则的Actions 。

详文阅读：

<http://hackernews.cc/archives/27842>

**俄安全研究员发现小米漏洞，可以访问全球所有的小米宠物喂食器**

  

一位俄罗斯安全研究人员说，她意外地找到了一种方法，可以入侵并接管世界各地的所有小米宠物喂食器。

来自俄罗斯圣彼得堡的安全研究员安娜 · 普罗维茨托娃（ Anna Prosvetova ）上周在其私人 Telegram 上发布的一系列消息中说，她发现了
[小米 FurryTail ](https://www.aliexpress.com/item/4000236477987.html)智能宠物喂食器的后端
API 和固件中的漏洞。

这些是智能宠物食品容器，可以通过移动应用程序对其进行配置，以在一天中的特定时间释放少量食物。

小米 FurryTail 设备专门用于处理猫和狗的食物，当主人在长途旅行中将宠物独自留在房屋或公寓中时，通常会使用它们。

 **研究人员找到了 10,950 个 FURRYTAIL 喂料器**

Prosvetova 说，当她看着自己从速卖通购买的设备（ 80 美元）时，发现 API 使她能够看到世界各地所有其他激活的 FurryTail 设备。

她总共发现了 10,950 台设备，研究人员声称她可以在不需要密码的情况下更改喂食时间表。

此外，她发现设备还使用 ESP8266 芯片组进行 WiFi
连接。她说，该芯片组中的漏洞使攻击者可以下载和安装新固件，然后重新启动送纸器，以便更改得以保留。

Prosvetova 表示，该漏洞对于希望将宠物喂食器劫持到 IoT DDoS 僵尸网络中的黑客来说非常理想，因为整个过程可以轻松实现自动化并大规模进行。

详文阅读：

<http://toutiao.secjia.com/article/page?topid=112087>

  

