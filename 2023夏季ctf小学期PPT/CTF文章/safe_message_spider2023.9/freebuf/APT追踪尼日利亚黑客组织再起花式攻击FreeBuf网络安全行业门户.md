![尼日利亚黑客组织](https://image.3001.net/images/20180503/15253270465073.png!small)

## 一、概述

 **今年 3 月，东巽科技 2046Lab
再一次跟踪到一起源自非洲的黑客组织攻击事件，和之前的攻击事件《[折翼的雏鹰：尼日利亚某黑客组织溯源](http://www.freebuf.com/articles/paper/157711.html)》类似，攻击者利用自己的PC进行木马测试后，未删除遗留的数据和屏幕截图，不同的是这次的遗留数据多达6G，同时包含有明确的受害者信息。**

通过对遗留数据、屏幕截图分析，研究人员又挖掘出了攻击者的skype账号、网盘账号、邮件账号等信息，并缴获攻击者之间的关于黑客攻击的聊天记录、网盘内容。综合以上这些材料分析，研究人员得到如下结论：

> 1．该黑客组织以盗取受害者金融资产为目的，包括但不限于：paypal、perfectmoney、数字货币、银行账户等。
>
>
> 2．该黑客组织的攻击的目标广泛，遍及全球，不仅对普通网民进行攻击，还针对“工具小子”类型的黑客进行黑吃黑攻击和对网赚兼职人员进行定向攻击。截止4月16日，已攻击700+受害者，数字在持续增加。
>
>
> 3．该黑客组织的攻击手法多样，除了采用常见的邮件附件攻击、银行和数字货币以及yahoo邮箱钓鱼站点攻击、伪装帅哥美女欺诈单身和离异人士，还采用了一些奇特手法，如利用Youtube明面讲解黑客教程实则绑马黑客工具攻击其他黑客、在fiverr等兼职网站明面发布兼职任务实则捆绑木马的word定向攻击网赚兼职人员。

总的来看，该黑客组织是整合各种手段来达到盗取受害者财务的目的并以此为生，而本次的溯源分析将揭露了这些手段的详细的全过程。截止发稿时，研究人员发现该黑客组织的攻击仍在继续。

## 二、受害者分析

### 2.1 攻击目标分析

目标是攻击者拟计划实施攻击的人群，并非每一个目标都会中招成为受害者，通过目标分析可以判定攻击者对目标是否有倾向性。从截图综合分析看，该黑客组织攻击目标主要有以下几类：

 **1.** **普通网民：** 这类目标分为两类，一是大型网站泄露数据中的邮箱，如alibaba
leads，该黑客组织通过购买获得；二是通过邮箱采集器如Email
Scraper爬取的邮箱，该黑客组织常用的关键字为石油天然气、航空航天制造业等，如下某成员的屏幕截图。这类目标主要是遭受钓鱼邮件攻击。

![通过工具搜集普通网民邮箱](https://image.3001.net/images/20180502/15252430087893.png!small)

图 通过工具搜集普通网民邮箱

![该黑客组织网盘中包含目标邮箱的文件](https://image.3001.net/images/20180502/15252432546863.png!small)

图 该黑客组织网盘中包含目标邮箱的文件

 **2．** **“工具小子”黑客：** 该组织通过Youtube传播黑客视频教程，引诱“工具小子”类黑客通过视频下方的链接下载捆绑了木马的工具。

![通过youtube上传视频并附上捆绑木马工具的链接攻击“工具小子”](https://image.3001.net/images/20180502/15252432709009.png!small)

图 通过youtube上传视频并附上捆绑木马工具的链接攻击“工具小子”

 **3．** **网赚兼职人员：**
该黑客组织上传捆绑木马的doc文档到fiverr、freelancer等平台（兼职网站）并发布悬赏任务，诱使兼职人员打开文件查看任务需求时植入木马。

![通过fiverr兼职平台发布任务攻击网赚兼职人员](https://image.3001.net/images/20180502/15252432849511.png!small)

图 通过fiverr兼职平台发布任务攻击网赚兼职人员

### 2.2 受害者分析

部分攻击目标最终会成为受害者，截止4月16日，研究人员从该黑客组织的多个C2中统计到受害者共有727名，黑客窃取了上万份键盘记录、密码和大量的屏幕截图。

![该黑客组织某一C2的截图](https://image.3001.net/images/20180502/152524331318.png!small)

图 该黑客组织某一C2的截图

通过对受害的IP进行区域统计，美国占比22%（163名）第一，其次是英国、法国各占15%（109名）和10%（71名），而其他零星的国家占比达到了20%（144），因此推测该黑客组织并未针对特定区域进行攻击，而采取的广撒网的模式。

![尼日利亚黑客组织再起花式攻击](https://image.3001.net/images/20180502/15252434685747.png!small)

研究人员专门针对我国的受害者进行了分析，统计中国大陆和中国台湾受害者合计数量47，在该组织的skype聊天记录中也发现其登陆国内受害者的126邮箱。但在深入分析被窃内容后发现，部分IP对应的受害者为安全公司的沙盒，因此真实的受害者数量低于统计数据，推测该黑客组织暂未针对我国的网民进行大面积攻击。

![组织成员因不认识126邮箱的中文验证码向同伙求助](https://image.3001.net/images/20180502/15252434819005.png!small)

图 该组织成员因不认识126邮箱的中文验证码向同伙求助

## 三、攻击者分析

### 3.1 地域分析

通过对该黑客组织的截屏内容分析发现，与其他攻击事件类似，该组织也使用了OpenVPN、PurVPN等多款VPN工具来隐藏自己的身份，如下图。

![攻击者设备上的4种VPN](https://image.3001.net/images/20180502/15252434962724.png!small)

图 攻击者设备上的4种VPN

为了准确掌握该组织的确定位置，研究人员对C2的访问日志进行分析、IP提取和归属地查询，统计结果如下表。

![C2的日志记录](https://image.3001.net/images/20180502/1525243507835.png!small)

图 C2的日志记录

**IP** |  **地区** |  **IP** **详情** |  **备注**  
---|---|---|---  
191.101.156.86 |  美国 |  VPS |  host1plus.com  
141.101.159.57 |  美国 |  - |  leadertelecom.ru  
206.123.154.170 |  美国 |  pureVPN |  pureVPN  
172.94.18.64 |  德国 |  VPS |  host1plus.com  
94.46.12.209 |  葡萄牙 |  VPS |  ptisp.pt  
172.111.232.30 |  加拿大 |  pureVPN |  pureVPN  
159.65.32.133 |  美国 |  VPS |  digitalocean.com  
172.94.49.235 |  土耳其 |  pureVPN |  pureVPN  
111.90.138.79 |  马来西亚 |  VPS |  [www.shinjiru.com](http://www.shinjiru.com)  
45.35.32.58 |  美国 |  VPS |  psychz.net  
105.112.37.104 |  尼日利亚 |  - |  Celtel Nigeria Limited t.a ZAIN  
169.159.87.146 |  尼日利亚 |  - |  Smile-Nigeria-AS  
154.66.51.227 |  尼日利亚 |  - |  Smile-Nigeria-AS  
197.210.8.171 197.210.227.* 197.210.226.* 197.210.24.* 197.210.44.*
197.210.25.* 197.210.28.* 197.210.29.* 197.210.47.* 197.210.172.* 197.210.45.*
|  尼日利亚 |  动态IP |  mtnnigeria.net  
  
表 黑客组织访问C2的IP地址统计

从统计结果来看，可以排除美国、德国、葡萄牙、加拿大等一系列的VPN地址和VPS的地址，剩下的动态IP主要位于尼日利亚，结合后面的组织分析内容，研究人员基本确定该黑客组织的成员主要位于尼日利亚，而该区域正是著名的“尼日利亚骗局”的发源地。

## 3.2 组织分析

### 3.2.1 组织规模

研究人员在该组织屏幕截图中发现了一名成员kelechi使用skype与同伙交流，然后根据图片中的gmail邮箱结合攻击者常用的密码组合，成功进入了该成员的skype。通过分析该成员的聊天记录，研究人员推测该组织大约有10成员左右，并溯源出了组织中的部分成员。

### 3.2.2 Nnaemeka Kelechi（C2所有者1）

该成员是本次跟踪溯源中发现截图和数据最多的组织成员，通过分析该成员的截图，研究人员发现其使用skype和teamviewer工具和同伙交流，并通过skype的信息溯源到了其facebook主页，对比C2记录的webcam照片和facebook照片后，研究人员确认为同一人，而其真实名字就是Nnaemeka
Kelechi，如下图。从facebook主页还可看见该成员在公开出售盗取的paypal、比特币信息。该成员的主要角色是发送木马邮件，并操控C2回收数据。

![成员Kelechi的溯源过程](https://image.3001.net/images/20180502/15252439546320.png!small)

图 成员Kelechi的溯源过程

通过深挖，研究人员发现该成员注册了多个邮箱用于社工、钓鱼邮件测试以及购买VPS、域名服务、cloudflare等，如下表。

**邮箱、电话** |  **用途**  
---|---  
nnaemekas4real@gmail.com |  真实账号，用于gmail、facebook、skype等  
sonahelton2@yahoo.com |  用于社工诈骗、钓鱼邮件测试，注册有fiverr、VPN账号、cloudflare等  
refinebaby4few@yahoo.com |  用于社工诈骗、密保邮箱，注册有facebook、fiverr、aliexpress等  
mrjacobs201@gmail.com |  用于收信封、youtube传播视频、购买域名和服务器等。  
sonahelton2@gmail.com |  用于facebook、收信封  
sonahelton2@mail.com |  用于Fiverr、域名和服务器购买  
+234 8061362274 |  用于whatsapp等  
  
表 成员Kelechi的其他账号信息

### 3.2.3 Samura（C2所有者2）

确定该成员是因为其与Kelechi联系频繁，几乎每天通过skype沟通，其skype昵称为onu.samson。研究人员在C2截图中同时找到了Kelechi和该成员的屏幕截图，截图除了印证两人的skype聊天外，还发现相互之间通过Teamviewer协助，而该成员的PC用户名为Samura，考虑到skype昵称通常为虚假名字，推测PC用户名此为其姓名的一部分，如下图。

![Samura和Kelechi之间的交流](https://image.3001.net/images/20180502/15252441975395.png!small)

图 Samura和Kelechi之间的交流

通过对Samura设备截图和数据的深挖，研究人员发现了该成员的更多信息（见下表），并发现该成员配置木马Agent
Telsa和操作C2服务器的截图，而该C2服务器也是Kelechi使用的服务器，两人的配置在不同目录。由此可见，该成员的角色也是发送木马邮件，并操作C2回收数据。

**邮箱、电话** |  **用途**  
---|---  
brooksglenn248@gmail.com  |  注册NOIP、购买域名和VPS、钓鱼邮件测试等  
danielskanin247@gmail.com  |  黑客论坛注册、数字货币交易所和钱包、钓鱼邮件测试  
brooksfundinggroup@gmail.com  |  数字货币交易所、shopify等  
onu.samson@gmail.com  |  域名和主机购买等  
marinojason370@yahooo.com  |  钓鱼邮件测试等  
tonyapettiner@gmail.com  |  CloudFlare注册  
  
表 Samura的更多信息

![Samura正在配置Agent
Telsa木马](https://image.3001.net/images/20180502/15252442095204.png!small)

图 Samura正在配置Agent Telsa木马

![Sumura和Kelechi共用的C2服务器，两人路径不同](https://image.3001.net/images/20180502/1525244220150.png!small)

图 Sumura和Kelechi共用的C2服务器，两人路径不同

### 3.2.4 simon tope（钓鱼网站制作者）

在C2数据中，研究人员发现一个邮箱simontope13@gmail.com账号在hosteringer.com上注册了18个域名，而其中4个域名确定为钓鱼网站，如下图。研究人员深入分析后发现Kelechi等人也使用该账号管理钓鱼网站，因此推测其为组织成员之一。

![ simon
tope（钓鱼网站制作者）](https://image.3001.net/images/20180502/15252443869405.png!small)

通过对simontope13@gmail.com的社交信息搜索，研究人员发现了其twitter主页，主页名字为simon
[tope](mailto:Tope%E4%BD%BF%E7%94%A8simontope13@gmail.com)，如下图。通过深挖发现了该成员的更多信息（见下表），并确认该成员的主要角色为负责设计钓鱼网站和发送钓鱼邮件。

![simon
tope的Twtiter主页](https://image.3001.net/images/20180502/152524440047.png!small)

图 simon tope的Twtiter主页

**邮箱、电话** |  **用途**  
---|---  
simontope13@gmail.com |  Facebook、Twitter、Aliexpress、购买域名和服务器、CloudFlare  
simontope123@gmail.com |  Facebook、购买域名和服务器  
paperchasers64@gmail.com |  giftcards.ng、购买域名和服务器  
solutionnet77@gmail.com |  测试钓鱼邮件、购买和注册域名  
debosco25@gmail.com |  购买域名和服务器  
lateefclicker@gmail.com |  Amazon AWS  
+234 7030414096 |  Facebook  
  
表 成员simon tope更多相关信息

### 3.2.5 其他相关成员（木马测试，洗钱）

通过对成员Kelechi的skype聊天记录的深度分析，研究人员发现还有一些人与其联系密切，有的讨论木马测试问题，有的交流网页设计问题，通过这些对话内容，推测这些人也是该黑客组织成员，如下图。  
![elechi建议grebs dietmar erwin不要用Virustotal测试木马
](https://image.3001.net/images/20180502/15252446167979.png!small)

图 Kelechi建议grebs dietmar erwin不要用Virustotal测试木马

  
![Kelechi和AKWUDOLUEZE正在交流邮件HTML格式问题](https://image.3001.net/images/20180502/15252446281044.png!small)

图 Kelechi和AKWUDOLUEZE正在交流邮件HTML格式问题

**Skype ID** **（昵称）** |  **邮箱或电话信息** |  **角色**  
---|---|---  
dietmar_erwin（grebs dietmar erwin）  |  dietmar_erwin@yahoo.com  |
参与钓鱼邮件和钓鱼网站测试、木马测试  
young.etihad（AKWUDOLUEZE）  |  +234 8141206076 +233 8058707714  |
发送垃圾邮件、处理C2的logs、木马测试  
ferdinandcruzzy（Phed Cheed）  |  \-  |  洗钱，主要处理银行账户余额、paypal余额等较难转移资金的问题。  
live:bconley80s（Conley P）  |  +14104246524  |  洗钱，主要处理银行账户。  
  
表 相关成员信息

## 四、攻击手段

本次的跟踪溯源过程，研究人员发现了超过6G的大量截图和数据，这些数据包含了攻击者从目标搜集、武器准备到投放利用以及最后进行资源收割的全部过程。

### 4.1 目标搜集

该黑客组织采用了多种方式来搜索目标：

1．通过工具扫描搜集目标。该黑客组织最常用的搜集目标的方式是通过Email Scraper一类的自动爬虫工具来从互联网上自动爬取邮箱，如下图。

![攻击者正在按行业收集邮箱](https://image.3001.net/images/20180502/15252448518767.png!small)

图 攻击者正在按行业收集邮箱

2．通过购买方式获取搜集目标。从成员kelechi的截图和交易记录发现，该黑客组织还会从地下的黑客论坛购买网站泄露数据，从中提取目标的邮箱，如下图。

![图片.png](https://image.3001.net/images/20180502/15252448632126.png!small)

图 Kelechi 购买网站泄漏数据的记录

3．通过交友方式搜集目标。在截图中，研究人员发现该团队伪装成帅哥或者美女，主动搭讪或者通过交友站点，引诱目标上钩，如下图。

![该组织成员在Facebook上伪装帅哥勾搭“猎物”](https://image.3001.net/images/20180502/15252448768711.png!small)

图 该组织成员在Facebook上伪装帅哥勾搭“猎物”

### 4.2 武器准备

 **4.2.1 工具准备**

从该黑客组织的屏幕截图可以看到，攻击者使用了下面这几款攻击武器：

1．Agent
Tesla，是一款国外黑客常用的付费KeyLogger，主要有窃取常用浏览器、软件存储的密码，键盘、粘贴板记录、定期截屏、定时照相等功能，如下图。

![该组织使用Agent
Tesla生成端](https://image.3001.net/images/20180502/15252448879582.png!small)

图 该组织使用Agent Tesla生成端

2．888 RAT，是一款收费远控，除了常用远控功能以外，还有输入框抓取等功能。该组织利用该远控配合Agent Tesla，实现对受害者的全面控制，如下图。

![该组织使用的888 RAT
远控](https://image.3001.net/images/20180502/15252449061786.png!small)

图 该组织使用的888 RAT 远控

3．njRAT，也是一款早期的远控，其稳定性好和易于免杀特性成为了较为流行黑客工具，如下图。

![该组织正在使用njRAT](https://image.3001.net/images/20180502/15252449241647.png!small)

图 该组织正在使用njRAT

### 4.2.2 武器组装

选择并测试好黑客工具后，该黑客组织便利用Agent
Tesla生成端的捆绑功能，将木马与其他应用程序（如其他黑客工具）、word等文件进行捆绑，组装成具有迷惑性和隐蔽性的新工具和doc文件，如下图。

![黑客组织将木马与大通银行爆破工具进行捆绑](https://image.3001.net/images/20180502/15252449866366.png!small)

图 黑客组织将木马与大通银行爆破工具进行捆绑

![黑客组织正在制作doc格式的木马](https://image.3001.net/images/20180502/152524501927.png!small)

图 黑客组织正在制作doc格式的木马

### 4.3 投放利用

准备好武器后，黑客组织便会利用多种方式将武器投递出去。与以往跟踪到的组织不同，该黑客组织使用的投递分发方式更加多样，除了常见的邮件、钓鱼网站、社工外，还采用了youtube和兼职网站的方式。

 **4.3.1 Youtube传播捆马黑客工具**

该黑客组织通过在youtube上传黑客工具视频教程，并附上工具下载链接的方式传播捆绑木马的黑客工具，同时禁用了评论，避免受害者留言报告其恶意内容。该组织的这个思路巧妙的地方是，抓住了即使杀软报毒，受害者也会因为黑客工具报毒属于正常现象而忽略告警的心理。其攻击步骤如下：

1．下载youtube上已有的黑客教程视频，并下载相关黑客工具；

2．将对应的黑客工具捆绑上木马，上传到mega网盘并生成分享链接；

![攻击者的mega网盘](https://image.3001.net/images/20180502/15252450839514.png!small)

图 攻击者的mega网盘

3．上传视频到youtube，并附上捆马工具的mega链接地址。

![攻击者正在上传视频](https://image.3001.net/images/20180502/15252450962100.png!small)

攻击者正在上传视频

4．等待受害者上钩。

下表是该黑客组织在youtube传播捆绑木马的视频列表，下载的文件均为捆绑木马的黑客工具，攻击者针对的目标主要为“工具小子”类黑客，推测其目的是想“黑吃黑”。

**标题** |  **视频链接** |  **下载链接** |  **文件名** |  **发布日期**  
---|---|---|---|---  
USA Bank brute Checker Version 5 0 2 |
<https://www.youtube.com/watch?v=HNIXJP2Bsyk> |
<https://mega.nz/#!z5hnQKIB!3SVM1wmsR3sRlHfQ5L3xIZDkXxwXhRlcr2uhqRymoQY> |
USA Bank brute Checker .zip |  2018年3月27日  
Payoneer Hack Money Adder 2018 Undetected No survey WORKING |
<https://www.youtube.com/watch?v=MQeN-65k-YY> |
<https://mega.nz/#!iswESbRa!bQq8we7lvP2Vgcn_n92c0rJ0F-nlowNIysIV9OLkojY> |
payoneer money adder latest .zip |  2018年2月17日  
[Chase Bank Brute Checker](https://www.youtube.com/watch?v=L9AvPMdKc84) |
<https://www.youtube.com/watch?v=L9AvPMdKc84> |
<https://mega.nz/#!zsJQXJpZ!G9zt6UBQuKfDcMMqVvDXbytS5lOGerypz9vLmFNKLH0> |
Chase Brute By77PixelS .zip |  2018年2月17日  
How to crack accounts with Account Reaper 2018 |
<https://www.youtube.com/watch?v=FBnFgmTg_pU> |
<https://mega.nz/#!box2BQJZ!KzawB5stvoTsUxKKJaCeqfuJPNO_psoZsPr3zZq0jVI> |
AR_1_4_1 .zip |  2018年1月18日  
Account Reaper 1 4 0 2 Cracked +Combo 50k New 2018 |
<https://www.youtube.com/watch?v=eDF03hOlvkc> |
<https://mega.nz/#!box2BQJZ!KzawB5stvoTsUxKKJaCeqfuJPNO_psoZsPr3zZq0jVI> |
AR_1_4_1 .zip |  2018年1月18日  
How to use UltraMailer to send Bulk Mail | UltraMailer v3.5 -Bulk email
software for Email Marketing |  <https://www.youtube.com/watch?v=1_Dk47Zzbmg>
|  <https://mega.nz/#!HxolxTKa!zccyu1al1GnWDH6Hz4VnYd-sF4KJEUzBJqP3SZaH9Io> |
UltraMailer_Setup_v3.5_en_fixed16 .zip |  2017年11月7日  
Bitcoin Miner 100 Working NO Scam |
<https://www.youtube.com/watch?v=116hWwcjxM4> |
<https://mega.nz/#!XlRQwYxZ!ys_Zq9MGTo2tn5KGbZqhonh49rxq01VQhpdQ5zqX4jo> |
Bitcoin Money Adder .zip |  2017年11月6日  
Sanmao SMTP mail cracker private |  <https://www.youtube.com/watch?v=p0yv-BKiQiw> |
<https://mega.nz/#!uwZDxZTT!djpUla5lMoELaEyO_wJ78sMcSK6DZhrIKWTgWAAyras> |
MailCracker .zip |  2017年10月1日  
Harris Bitcoin Miner Software Earn up to 1 BTC daily for FREE 1 |
<https://www.youtube.com/watch?v=aK37Q5k0okw> |
<https://mega.nz/#!6lAj0KbY!WcabTByq3C7nPxH04Mc4wFLTWcWXj0MRSzrZsCZlabA> |
Harris Bitcoin Miner Software .zip |  2017年9月28日  
Bitcoin Adder New 2017 |  <https://www.youtube.com/watch?v=D1cPgG45RV0> |
<https://mega.nz/#!XlRQwYxZ!ys_Zq9MGTo2tn5KGbZqhonh49rxq01VQhpdQ5zqX4jo> |
Bitcoin Money Adder .zip |  2017年8月31日  
  
表 黑客在Youtube传播的捆绑木马的黑客工具的地址

 **4.3.2 兼职网站传播捆马文档**

研究人员观察到该黑客组织会通过网赚兼职网站fiverr.com和freelancer（类似于国内的猪八戒网）发布兼职任务，然后上传捆马的doc附件作为需求文档，如下图。

![该黑客组织发布假的兼职任务](https://image.3001.net/images/20180502/15252451195723.png!small)

图 该黑客组织发布假的兼职任务

当受害者试图了解需求而打开doc文件时会被植入木马，植入木马后，该黑客组织会盗取受害者的fiverr等账号中的资金以及其它资产，如下图。

![该组织在doc中插入图片诱导用户启用宏](https://image.3001.net/images/20180502/15252451315012.png!small)

图 该组织在doc中插入图片诱导用户启用宏

 **4.3.3 钓鱼邮件诱骗目标点击木马**

针对搜集到的目标，该黑客组织会通过邮件群发工具发送大量的钓鱼邮件，其中以 **错误的转账确认、伪造盗用身份信息诈骗、银行账号安全升级**
等多种方式，诱骗目标打开邮件中捆绑了木马的附件，一旦目标点击附件，木马将运行并窃取受害者的账号密码、截图或开启摄像头拍照，如下图。

![该组织正在采集石油天然气等关键字相关邮箱地址并批量发送钓鱼邮件](https://image.3001.net/images/20180502/15252475822875.png!small)

图 该组织正在采集石油天然气等关键字相关邮箱地址并批量发送钓鱼邮件

![冒充国际贸易公司，诱骗目标确认公司银行信息
](https://image.3001.net/images/20180502/15252476277345.png!small)

图 冒充国际贸易公司，诱骗目标确认公司银行信息  
![警告目标的个人信息涉嫌欺诈，诱骗用户下载点击附件](https://image.3001.net/images/20180502/1525247989763.png!small)

图 警告目标的个人信息涉嫌欺诈，诱骗用户下载点击附件

  
![冒充美国银行发送邮件提醒用户升级账户](https://image.3001.net/images/20180502/1525248037334.png!small)

图 冒充美国银行发送邮件提醒用户升级账户

 **4.3.4 钓鱼网站窃取用户信息**

该黑客组织有专人搭建了常见的银行、yahoo邮箱等风格钓鱼网站套取用户信息，经研究人员统计，该组织购买了多个域名，其中某个账号在hostinger网站上绑定的18域名已有4个被确认为钓鱼站点，并已经获取到一些受害者的银行账号信息，如下图。

![该组织某账号下18个网站，其中4个能作为钓鱼网站](https://image.3001.net/images/20180502/15252480533765.png!small)

图 该组织某账号下18个网站，其中4个能作为钓鱼网站

 **图 4 个钓鱼网站**

![某钓鱼网站后台数据](https://image.3001.net/images/20180502/15252480826391.png!small)

图 某钓鱼网站后台数据

除上述常见的钓鱼站点外，该黑客组织还注册了仿冒的黑客工具站点域名hunterexploit.pro（原网站为hunterexploit.com），并克隆了原网站页面，修改付款链接和价格，兜售比官方站点更便宜的工具，欺骗目标付费购买假的黑客工具。

![仿冒的黑客工具销售站点](https://image.3001.net/images/20180502/15252480966674.png!small)

图 仿冒的黑客工具销售站点

下表为研究人员已经确认的钓鱼网站地址：

**钓鱼网站** |  **用途**  
---|---  
zup.96.lt |  LLOYDS BANK钓鱼  
pinnacle.96.lt |  Gmail、Yahoo、ALO、Outlook钓鱼  
catchy.96.lt |  LLOYDS BANK钓鱼  
bnk.96.lt |  STATE BANK钓鱼  
hunterexploit.pro |  hunterexploit.com克隆网站，钓鱼  
[www.dboxdocu.com](http://www.dboxdocu.com) |  Dropbox钓鱼  
btc-rush.club |  数字货币投资诈骗  
  
表 确认过的钓鱼站点

 **4.3.5 社交网络欺诈**

该黑客组织注册了很多facebook、tinder、google账号，并伪装成帅哥美女，对离异或单生人士实施欺诈，一旦获取受害者信任，便诱骗受害者为自己购买电子礼物（如Itunes
Gift Card），然后再通过倒买获利，如下图。

![该黑客组织进行社交欺诈伪装的身份](https://image.3001.net/images/20180502/15252481157912.png!small)

图 该黑客组织进行社交欺诈伪装的身份

![ 该黑客组织向受害者索取gift
card](https://image.3001.net/images/20180502/15252481265765.png!small)

图 该黑客组织向受害者索取gift card

 **4.3.6 撞库攻击**

撞库攻击是指利用已有的账号信息，尝试在不同的站点进行碰撞验证，筛选出可用的账号信息。在本次跟踪的攻击事件中，该黑客组织将搜集到的邮箱+密码对，利用工具对paypal和一些银行进行撞库攻击，如下图。

![该黑客组织正在对paypal进行撞库攻击](https://image.3001.net/images/20180502/15252481378576.png!small)

图 该黑客组织正在对paypal进行撞库攻击

### 4.4 武器安装

当受害者点击钓鱼邮件附件、youtube捆绑木马和捆马文档，便会触发木马的安装。研究人员从该组织发送邮件中的附件、C2服务器、youtube视频链接中提取了多个木马样本，如下图。

 **图 该组织涉及到的部分样本**

本报告中，分析攻击者最常使用的，从邮件附件提取的doc格式样本，如下图。

![攻击者发送的伪装快递的钓鱼邮件](https://image.3001.net/images/20180502/15252483702382.png!small)

图 攻击者发送的伪装快递的钓鱼邮件

武器的安装过程如下：

1．点击运行“Shippment Details.doc”后，会触发word文档中的vba代码，该代码1300行左右经过较为复杂的混淆来隐藏其指令。

![
word中的VBA代码](https://image.3001.net/images/20180502/15252483822738.png!small)

图 word中的VBA代码

2．VBA代码被执行后，会调用如下cmd命令，从<http://plumberspro.us/bind.exe>下载木马文件bind.exe到系统的临时目录并执行，可见doc文件的作用是充当下载者，如下图。

![
VBA调用的cmd命令下载木马文件](https://image.3001.net/images/20180502/15252483947333.png!small)

图 VBA调用的cmd命令下载木马文件  
![通过网络流量包监测到http://plumberspro.us/bind.exe的下载过程](https://image.3001.net/images/20180502/15252484034628.png!small)

图 通过网络流量包监测到<http://plumberspro.us/bind.exe>的下载过程

3．bind.exe执行后，释放并执行4个PE文件和1个VBS脚本，分别为：

> a、C:\Users\ADMINI~1\AppData\Local\Temp\itUTjNZV.exe
>
> b、C:\Users\Administrator\AppData\Roaming\Microsoft\Windows\Templates\now.exe
>
> c、C:\Users\Administrator\AppData\Local\Temp\ZMWNIT.exe
>
> d、C:\Users\Administrator\AppData\Roaming\firfox\firfox.exe
>
> e、C:\Users\ADMINI~1\AppData\Local\Temp\HTNYEL.vbs

4．这些文件执行后，c和e实现辅助功能，分别负责查询IP位置信息和保证d已经运行。a、b、d是武器准备阶段的木马Agent
Tesla、888RAT和一个未见截图的Hunter’s
Eyes木马，木马运行后与C2进行通信确保被长期控制，这些木马实现如添加计划任务实现用户登录自启动、添加键盘钩子、获取屏幕截图等操作，如下表。

**文件** **** |  **恶意代码类型** **** |  **通信的** **C2** **地址** ****  
---|---|---  
C:\Users\ADMINI~1\AppData\Local\Temp\itUTjNZV.exe  |  Agent Tesla  |
<http://plumberspro.us/Exterminators%20Lander%20Updated/images/WebPanel/api.php>  
C:\Users\Administrator\AppData\Roaming\Microsoft\Windows\Templates\now.exe  |
888 RAT  |  tcp:// godstar.hopto.org:1300  
C:\Users\Administrator\AppData\Roaming\firfox\firfox.exe  |  Hunter’s Eyes  |
tcp:// godstar.hopto.org:5555  
  
表 释放的木马文件和通信地址

### 4.5 命令控制

上述木马执行成功后，该黑客组织对受害者进行长期控制，包括窃取账号、密码、截图、键盘记录、下载文件、操作屏幕等，如下图。

![该黑客组织正在控制888
RAT](https://image.3001.net/images/20180502/15252486586026.png!small)

图 该黑客组织正在控制888 RAT

![ 该黑客组织正在查看Agent
Tesla收到的密码](https://image.3001.net/images/20180502/15252486696755.png!small)

图 该黑客组织正在查看Agent Tesla收到的密码

在本次的跟踪中，研究人员发现了该组织的多个C2控制中心地址，如下表。

**域名** **** |  **C2** **类型** **** |  **备注** ****  
---|---|---  
plumberspro.us  |  Agent Tesla（new）  |  攻击团队主要C2  
trentfast.com  |  Agent Tesla（new）  |  攻击团队次要C2  
godstar.hopto.org  |  888 RAT  |  NOIP动态DNS+VPN端口转发  
grigori.ddns.net  |  888 RAT  |  NOIP 动态DNS  
grigoris.ddns.net  |  888 RAT  |  grigoris.ddns.net  
hotelvenisi.com  |  Agent Tesla（new）  |  已下线  
exterminatorsnearby.us  |  Agent Tesla（new）  |  已下线  
sibursin-int.com  |  Agent Tesla（new）  |  已下线  
zup.96.lt |  Zeus  |  \-  
samora007.hopto.org  |  888 RAT  |  NOIP 动态DNS  
volcano111.hopto.org  |  888 RAT  |  NOIP动态DNS  
  
表 该黑客组织使用的C2地址

本报告重点分析该黑客团队重点使用的新版Agent Telsa木马与C2服务器的plumberspro.us的通信流量。与早前版本不同，新版本的Agent
Telsa木马采用了3DES加密通信数据，加密模式ECB，3DES加密后使用base64对数据编码，最后以参数p将数据post到C2的api.php，如下为网络中截取的加密后的内容：

解密P的内容为：

新版本Agent Telsa与C2的通信数据结构如下：

其中type包括：uninstall、update、info、screenshots、keylog、passwords。其具体意义可参考2046Lab的早期报告<http://www.freebuf.com/articles/network/145985.html>。

### 4.6 资源收割

当黑客组织通过各种攻击手法获取到受害者的信息或者权限后，便开始实现自己的最终目的：资源收割。透过分析投递利用阶段的社交网络欺诈、撞库攻击以及攻击者的其他截图，研究人员确定该黑客组织的最终意图是
**盗取或骗取受害者财物** ，手段或是通过欺诈收取礼物，或通过黑客手段获取账户信息然后转移银行资产或者虚拟货币，如下图。

![黑客组织登陆到某受害者的wells
fargo银行账户转移资产](https://image.3001.net/images/20180502/15252486964191.png!small)

图 黑客组织登陆到某受害者的wells fargo银行账户转移资产

![黑客组织准备转走受害者在Western
Union的美元](https://image.3001.net/images/20180502/15252487044142.png!small)

图 黑客组织准备转走受害者在Western Union的美元

## 五、总结

通过对该黑客组织近两个月的跟踪和分析，研究人员捕获到了大量有价值的情报，如C2地址、木马样本、托管木马下载地址、攻击者IP、钓鱼网站地址等IOCs（威胁指标），同时通过关联分析溯源出了该攻击者组织位于尼日利亚以及其成员信息和具体的攻击手段，并最终揭开了该组织的攻击意图为盗取或骗取受害者财物。
**该黑客组织比较明显的特点是融合了多种攻击手段来达到目的** ， **并把攻击目标群体扩大了兼职人员、与之类似的黑客，** 汇总的TTPs总结如下。

**关键项** |  **本次攻击事件情况说明**  
---|---  
主要攻击目标 |  普通网民、兼职人员和“工具小子”类黑客  
目标国家 |  世界各国  
关键作用点 |  Youtube站点、社交网站、网赚兼职网站、Email  
攻击手法 |  Youtube传播、社交网站社工、网赚网站社工、钓鱼邮件  
攻击目的 |  获取用户paypal、perfectmoney、银行现金、数字货币或者直接骗取gift card一类财物  
漏洞使用情况 |  暂未发现  
免杀技术 |  Tesla不定期免杀更新，并使用crypter 进行FUD。其中技术主要有混淆、反调试、powershell、白程序等。  
活跃程度 |  频繁，至今活跃  
反追踪能力 |  一般，使用了VPN、VPS等隐藏手段，但经常不用vpn登陆自己的C2  
攻击源 |  尼日利亚，10人左右黑客组织  
  
表 TTPs总结

 ***本文作者：dongxun（东巽科技），转载请注明来自 FreeBuf.COM**

