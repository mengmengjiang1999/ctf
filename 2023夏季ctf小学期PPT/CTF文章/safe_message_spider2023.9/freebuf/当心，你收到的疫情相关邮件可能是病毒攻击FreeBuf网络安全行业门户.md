**警惕！黑客已将疫情信息融入到互联网黑产攻击链和产业链，对疫情信息关注者发动攻击。**

自新型冠状病毒感染的肺炎疫情发生以来，绿盟科技高度关注不法分子使用疫情话题发起的黑客攻击。通过对近期网络威胁行为的跟踪与分析，绿盟科技伏影实验室发现在经过一段时间的试探过程后，黑客已将新型冠状病毒肺炎疫情信息融入到互联网黑产攻击链和产业链当中，对疫情信息关注者发动攻击。

**行骗套路一：鱼叉邮件**

鱼叉邮件是黑客攻击过程中社会工程学的主要表现，因此攻击者通常会根据时事新闻更新鱼叉邮件的诱饵信息内容。此次新冠肺炎疫情显然给攻击者提供了借题发挥的平台。绿盟科技发现，近期已有主流恶意邮件传播的木马家族在诱饵内容中加入了疫情相关信息，借此增加邮件诱饵的可信度。

案例一

 **假借疫情放假信息，FormBook木马发动鱼叉邮件攻击**

绿盟科技近期捕获了FormBook木马利用肺炎疫情发起的攻击事件。该起攻击事件中，攻击者将疫情信息融入鱼叉邮件诱饵中，设计了欺骗度极高的社工内容，借此攻击罗马尼亚的机动车制造商。

该诱饵邮件内容如下：

![https://mmbiz.qpic.cn/mmbiz_png/IpYUt4DIvZeedwPiagiaQxGbld6iaiaiaskicQOzbZXTrib3vqf7zczlO9XjV9lTq610iampPkT5RRRlNMMIuF5tH6pGmw/640?wx_fmt=png](https://image.3001.net/images/20200221/1582276478_5e4f9f7e499e3.jpg!small)

在精心构造的社工邮件内容中，攻击者伪装为企业员工，催促邮件接收者尽快检查附件内容并回复。为提高可信度，邮件中声称该因为受新冠肺炎疫情影响，该公司将放假延长到2月9日，并延期至2月10日复工（Because
of the infflience ofcoronavirus, our holiday has been extended to 9th Feb, we
will return to workfully on the 10th Feb）。从邮件内容来看，攻击者对疫情时事较为了解，可能是有组织的黑客团体。

**附件文件REQUEST1.iso**

该邮件的恶意载荷包含两层伪装。光盘镜像文件REQUEST1.iso中包含一个屏幕保护文件co2.scr，实际为恶意的PE可执行文件：

![https://mmbiz.qpic.cn/mmbiz_png/IpYUt4DIvZeedwPiagiaQxGbld6iaiaiaskicQonvbzfvIfibFyBOAfePf9hRFX3Mic3oyrhCgQAGzqHpPa4JXu4EEDeyg/640?wx_fmt=png](https://image.3001.net/images/20200221/1582276486_5e4f9f86eddf6.png!small)

**混淆外壳co2.scr**

co2.scr是.net外壳程序，混淆了函数名、函数内容以及代码逻辑，用来干扰杀毒引擎和分析软件的分析：

![https://mmbiz.qpic.cn/mmbiz_png/IpYUt4DIvZeedwPiagiaQxGbld6iaiaiaskicQonvbzfvIfibFyBOAfePf9hRFX3Mic3oyrhCgQAGzqHpPa4JXu4EEDeyg/640?wx_fmt=png](https://image.3001.net/images/20200221/1582276493_5e4f9f8da230e.png!small)

对该程序脱壳后，可以获取第二层载荷PLxHldNnIKOb.exe

**加载器PLxHldNnIKOb.exe**

PLxHldNnIKOb.exe是Dropper程序，将自身资源段中携带的二进制文件解密并使用指定方式加载运行。根据配置的不同，该程序支持以下恶意行为：

![https://mmbiz.qpic.cn/mmbiz_png/IpYUt4DIvZeedwPiagiaQxGbld6iaiaiaskicQx1YF13lFEluQB50Rzkr0XpuhMLenwPQz65FagLRloDyqUu9m106F1Q/640?wx_fmt=png](https://image.3001.net/images/20200221/1582276500_5e4f9f9474207.jpg!small)

该程序使用隔位异或的方式解密资源段内容，解密键为OOmmuoPtHAHiIjANYoKqZhYfb：

![https://mmbiz.qpic.cn/mmbiz_png/IpYUt4DIvZeedwPiagiaQxGbld6iaiaiaskicQHSn8q8brIWiaSo5SgkjZpA71MBpEGic7aia2aCa84hpDWvqbjnPOKqLYQ/640?wx_fmt=png](https://image.3001.net/images/20200221/1582276508_5e4f9f9c3140c.png!small)

根据设置，PLxHldNnIKOb.exe程序运行后会将最终载荷hRNfZekS加载至内存执行。

**最终载荷hRNfZekS**

Dropper文件释放运行的最终载荷是新版本的FormBook木马程序，连接C&C为[www.4my.fans](http://www.4my.fans)。FormBook是一款多功能木马，主要用于窃取用户主机信息或作为跳板下载执行其他恶意程序。

FormBook木马有高度对抗行为，会通过创建傀儡进程，反向注入等行为将注入行为复杂化。受C&C指令控制，FormBook木马可以执行以下行为：

![https://mmbiz.qpic.cn/mmbiz_png/IpYUt4DIvZeedwPiagiaQxGbld6iaiaiaskicQ8L4v5NdDETXqptBGE3OGI1lB1dpibjoCIYcXoOSVCV4K4TMicFCwnLnQ/640?wx_fmt=png](https://image.3001.net/images/20200221/1582276514_5e4f9fa2e69a5.png!small)

**案例小结**
：FormBook是有较长历史的木马程序，被国际上多个黑客组织大量使用。目前，搭载FormBook的鱼叉邮件已成为对邮件使用者的主要威胁种类之一。该起借助冠状病毒信息的鱼叉邮件攻击事件表明，黑客组织对攻击流程中载荷投递阶段的设计十分重视，更新速度快，诱饵质量高。邮件用户切不可因邮件内容的高可信度而麻痹大意，应谨慎对待邮件附件，不运行未知程序，将可疑文件交由安全人员处理。  
  

案例二

 **Emotet** **木马来袭，黑客伪装成日本各县市的保健所发布邮件**

随着疫情的发展，同属于知名邮件木马的Emotet木马家族，近期也使用包含新冠肺炎疫情信息的邮件在日本进行传播。这些针对日本的鱼叉邮件，发件者普遍伪装为日本各县市的保健所，邮件内容在强调新冠肺炎疫情的同时，要求收件者打开附件中的“对策”或“通知”文件。

![https://mmbiz.qpic.cn/mmbiz_png/IpYUt4DIvZeedwPiagiaQxGbld6iaiaiaskicQFcgQhHZOo8AQr8bwv021vavVAHxp0TXF8OEe5EBmRTUocuwcLdicOfQ/640?wx_fmt=png](https://image.3001.net/images/20200221/1582276522_5e4f9faa9d8c7.jpg!small)![https://mmbiz.qpic.cn/mmbiz_png/IpYUt4DIvZeedwPiagiaQxGbld6iaiaiaskicQhNu8rOm18eXOKWTNFYIP1pmVbcApic1DOTcqd1mQxoy1JDjEmdojYpg/640?wx_fmt=png](https://image.3001.net/images/20200221/1582276529_5e4f9fb1f148d.jpg!small)![https://mmbiz.qpic.cn/mmbiz_png/IpYUt4DIvZeedwPiagiaQxGbld6iaiaiaskicQ6dYshCuicqicmy9shIPUJMtdyI2JTZT92yt2RFNhn1TT9CecITqOhVSw/640?wx_fmt=png](https://image.3001.net/images/20200221/1582276537_5e4f9fb95b6c2.jpg!small)

**doc** **文档载荷**

这些邮件附带的doc文档，显示社工内容欺骗用户运行内置的vba脚本，该vba脚本会运行powershell命令，安装Emotet木马程序。

![https://mmbiz.qpic.cn/mmbiz_png/IpYUt4DIvZeedwPiagiaQxGbld6iaiaiaskicQbOZxjIVNiaOxuiaXoqh0nicNJzxkM7vXDBZ7icMRjMLsfdOkNLd5UmwA9g/640?wx_fmt=png](https://image.3001.net/images/20200221/1582276546_5e4f9fc20398c.png!small)

**Emotet** **木马**

Emotet家族属于银行木马，出现于2014年，主要以垃圾邮件形式传播，感染Windows主机后并盗取用户邮箱来获得重要个人财务信息。近年来，Emotet在多起事件中被发现开始用于传播其他恶意家族，涉及银行木马、DDoS和勒索等。

Emotet传播的其它部分恶意家族分类如下表所示：

![https://mmbiz.qpic.cn/mmbiz_png/IpYUt4DIvZeedwPiagiaQxGbld6iaiaiaskicQSursDcmLUeIpmOmTOoZC9Ywpb2ibsiclDqvemyaq159Yyn7HddtJWXJw/640?wx_fmt=png](https://image.3001.net/images/20200221/1582276557_5e4f9fcd9d234.png!small)

有信息显示，Emotet木马主要受黑客组织Mealybug操纵，从2014年开始维护Emotet代码并展开多次攻击。该利用疫情信息传播的邮件中搭载的Emotet木马是该家族的最新版本，标记为Emotet_Doc_Downloader_C，在doc类型恶意文件中非常多见：

![https://mmbiz.qpic.cn/mmbiz_png/IpYUt4DIvZeedwPiagiaQxGbld6iaiaiaskicQHLOL1Oic8CPG8nO9FGr2iapwsbYA0U1YaibpRwic8B0qTHwGtnRdyI2PPQ/640?wx_fmt=png](https://image.3001.net/images/20200221/1582276564_5e4f9fd4b993b.png!small)

**案例小结：**
这起攻击事件表明，Emotet成为恶意邮件传播的主要木马家族绝非偶然。无论是攻击时间（最早出现在1月底）还是诱饵质量（保健所名称和联系方式属实），Emotet都走在了恶意邮件家族的前列。普通邮件用户在接触到外文类型的邮件时，应默认按照恶意邮件来进行处理，千万不要一时好奇，被攻击者所利用。

**行骗套路二、热点名称的恶意程序**

除鱼叉邮件外，部分攻击者也会使用热点关键词作为文件名称，投递恶意程序进行攻击。部分恶意程序名称与主要功能见下表：

![https://mmbiz.qpic.cn/mmbiz_png/IpYUt4DIvZeedwPiagiaQxGbld6iaiaiaskicQcdhPZnJ071RCjEMic7Qn7icMHKEllfEO3KrFwtQoBmn3kcYXDkliaOCCw/640?wx_fmt=png](https://image.3001.net/images/20200221/1582276574_5e4f9fde39713.jpg!small)

这些程序大多是数据清除程序或远控木马，使用热点事件进行简单的社会工程学加工，属于愿者上钩型。

**安全总结：通过正规渠道获取疫情相关信息，避免因猎奇心理导致设备中招。**

新型冠状病毒肺炎疫情的爆发，给黑客们提供了绝佳的社会工程学材料，小到个人大到组织，纷纷利用本次事件扩大武器的攻击面。

近期，许多平常接触网络较少的用户开始在互联网渠道获取信息，这些群体缺乏对信息的基本鉴别能力，难以正确识别和阻截这些恶意软件。因此我们建议，一定要通过正规渠道获取疫情相关信息，避免因猎奇心理导致设备中招。

![https://mmbiz.qpic.cn/mmbiz_png/IpYUt4DIvZeedwPiagiaQxGbld6iaiaiaskicQccNwcme47tj5O1G00V3e8qOJLeQo4NMWfn5m0sypu3bSoLR4TIesicA/640?wx_fmt=png](https://image.3001.net/images/20200221/1582276582_5e4f9fe6b15ed.jpg!small)

  
![https://mmbiz.qpic.cn/mmbiz_png/IpYUt4DIvZeedwPiagiaQxGbld6iaiaiaskicQNCp35DsrBkULP0ib1V1W4fUgAZLeibHadYIuxnbb8aHknbQ210qALO4Q/640?wx_fmt=png](https://image.3001.net/images/20200221/1582276591_5e4f9fef33bd7.jpg!small)  
  

**绿盟科技伏影实验室**
专注于安全威胁研究与监测技术，包括但不限于威胁识别技术，威胁跟踪技术，威胁捕获技术，威胁主体识别技术。研究目标包括：僵尸网络威胁，DDOS对抗，WEB对抗，流行服务系统脆弱利用威胁、身份认证威胁，数字资产威胁，黑色产业威胁及
新兴威胁。通过掌控现网威胁来识别风险，缓解威胁伤害，为威胁对抗提供决策支撑。

