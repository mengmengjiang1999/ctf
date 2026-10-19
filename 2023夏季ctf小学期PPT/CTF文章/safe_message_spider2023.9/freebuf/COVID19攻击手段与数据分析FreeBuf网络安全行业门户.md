**随着新冠病毒在世界范围内传播，研究人员发现自2月初以来，与冠状病毒相关的搜索和浏览量大幅增加，同时网络罪犯正利用新冠话题获利。**

研究人员监控新冠主题相关的新域名注册，2月到3月日均冠状病毒相关域名注册量增长了656%，恶意注册（包括恶意软件和网络钓鱼）增长569%，“高风险”注册（包括欺诈、挖矿和其他恶意URL域）增长788%。截至3月底，确定了116357个冠状病毒相关的新注册域名。其中，2022个是恶意的，40261个是“高风险的”。通过Whois、DNS记录和爬虫收集分析这些域。发现许多域名注册后被转售，其中一部分域名既被用于恶意活动，也被用于欺诈。还发现了部分以冠状病毒为主题的域有高风险JavaScript页面，可能随时将用户重定向到恶意网页。

## 数据分析

### 用户搜索

![](https://image.3001.net/images/20200423/1587629914_5ea14f5ab3164.png!small)

近期观察到用户对冠状病毒相关主题的兴趣急剧增加。在图1中可以看到在2020年1月底、2月底和3月中旬三个显著的高峰。第一个峰值与中国的病毒爆发一致，第二个峰值表示美国第一例不明原因病例，第三个峰值与美国的病毒爆发同时出现。图1中的一个例外是酒精，因为用户全年都对它感兴趣。

![](https://image.3001.net/images/20200423/1587629950_5ea14f7e14ce3.png!small)

在图2中看到，与2月初到3月底相比，访问与冠状病毒相关的url数量增加了近10倍。

用户对冠状病毒关注度给了网络犯罪分子有利可图的机会。攻击者获益的一个常见方法是注册相关关键字的域名，如“冠状病毒”或“COVID”。这些域名通常看起来合法，但会被用于各种各样的恶意活动，包括诱骗用户下载恶意文件、网络钓鱼、诈骗、恶意篡改和加密货币挖掘。

### 域名信息

从2020年1月1日到2020年3月31日检索了包含冠状病毒相关关键字的nrd，系统检测到116357个相关的NRD，每天大约有1300个域名。图3显示了研究期间检测到的新域名注册趋势。随着时间的推移，冠状病毒域的数量在增加，3月12日之后，每天检测到3000多个新的域。

![](https://image.3001.net/images/20200423/1587630213_5ea15085b5556.png!small)

可以把NRD分为两类。恶意nrd包括C2、恶意软件传播和网络钓鱼域；高风险nrd包含欺诈、挖矿和其他恶意URL域。发现了2022个恶意和40261个高风险NRD。恶意率为1.74%，高危率为34.60%。在恶意域名中，15.84%试图窃取用户凭据，84.09%托管了不同种类的恶意软件，包括木马和信息窃取软件等。2月到3月日均冠状病毒相关域数量增加了656%，恶意和高风险域分别增长了569%和788%。

![](https://image.3001.net/images/20200423/1587630481_5ea15191a7808.png!small)

共观察到这些域的2835197个DNS查询（不包括缓存），平均恶意NRD比平均非恶意NRD多88%。3月16日NRD数量急剧增加，这与美国病毒爆发有关。

![](https://image.3001.net/images/20200423/1587630585_5ea151f9e832e.png!small)

在图5中列出了匹配最多NRD的前15个关键字。这些关键词的风险水平高于平均水平（高风险率>40%），它们更容易被滥用。另一方面，恶意率与一般关键词相似。一个特殊的例子是“virusnews”匹配344个nrd，其中33%是恶意的。

## 技术分析

### 钓鱼攻击

钓鱼攻击的目的是诱骗用户共享其凭据和个人信息。在冠状病毒域中，观察到攻击者向用户发送电子邮件，其中包含假冒网站链接，欺骗用户输入登录信息。

![](https://image.3001.net/images/20200423/1587630845_5ea152fdafb22.png!small)

在形如‘corona
masr*.com‘域名中，同一天检测到一个20个域名注册，其中*是1到101之间的数字。在图6是以美国银行为目标的钓鱼网站hxxp[:]//corona-masr21[.]com/boa/bankofamerica/login.php。此外还包括http[:]//corona-masr21[.]com/apple-online和hxxps[:]//corona-masr3[.]com/CAZANOVA%20TRUE%20LOGIN%20SMART%202019/。

此外发现钓鱼服务域还托管恶意压缩文件及其恶意程序组件。

![](https://image.3001.net/images/20200423/1587631122_5ea15412cba35.png!small)

### 恶意软件传播

许多新注册的COVID-19域被识别与恶意软件活动相关。其中covid-19-gov[.]com与[Proofpoint报告](https://www.proofpoint.com/us/threat-insight/post/new-redline-stealer-distributed-using-coronavirus-themed-email-campaign)的RedLine Stealer活动相同。研究人员确定了一个RedLine Stealer样本，该样本执行时，首先打开Internet
Explorer并尝试连接到hxxp://localhost:14109。然后向hxxp://45.142.212[.]126:6677/IRemotePanel发起一个HTTP
POST请求，远程C2服务器发出HTTP 200 OK响应后，样本开始从主机进行数据过滤：

![](https://image.3001.net/images/20200423/1587631446_5ea155567f56a.png!small)

RedLine Stealer可在隐藏窗口中执行命令：

    
    
    cmd.exe” /C taskkill /F /PID <RedLine Stealer PID> && choice /C Y /N /D Y /T 3 & Del

该命令通过进程标识符（PID）杀死正在运行的RedLine Stealer恶意软件，并删除存在RedLine
Stealer恶意软件的目录，并用Y响应删除提示。此外，RedLine
Stealer变体不会在磁盘上生成其他恶意文件、创建/更改任何互斥对象或尝试建立持久控制。

除了RedLine Stealer，还在‘corona-map-data[.]com/bin/regsrtjser346.exe’检测到Danabot
banking木马，在Corona virusapps[.]com域上发现了三个恶意Android应用程序，url分别为：Corona-virusapps[.]com/s<1-3>/CoronaVirus-apps.apk、coronaviruscovid19
information[.]com/it/corona.apk和coronaviruscovid19
information[.]com/en/corona.apk。

### C2 Communication

网络罪犯主要使用冠状病毒相关域进行恶意软件传播、网络钓鱼和诈骗，同时也观察到C2通信情况。

![](https://image.3001.net/images/20200423/1587645807_5ea18d6f59b83.png!small)

在NATSupportManager远程访问工具网络流量中，可以看到域covidpreventandcure[.]com解析为5.181.156[.]14。然后它向hxxp://5.181.156[.]14/fakeurl.htm发送多个POST请求，并向端口443发送TCP数据包。如图10所示，POST通信格式为HTML表单，C2服务器将编码命令和有效负载附加到HTTP响应中，木马则会发送编码后的数据。

![](https://image.3001.net/images/20200423/1587646033_5ea18e51a03d8.png!small)

covidpreventandcure[.]com于3月26日注册。两天后发现相关DNS流量，一直持续到4月11日。4月份解析此域的DNS流量增加。

### 诈骗广告

研究中发现了高风险域名中的诈骗网站，试图骗取用户购买短缺物品。如口罩或洗手液。

![](https://image.3001.net/images/20200423/1587646195_5ea18ef3c21d6.png!small)

![](https://image.3001.net/images/20200423/1587646243_5ea18f231feb1.png!small)

### 心理利用

![](https://image.3001.net/images/20200423/1587646334_5ea18f7e35868.png!small)

发现网站利用人们对冠状病毒的恐惧迫使他们购买电子书，如图16所示。发现了8个注册域，包括coronavirussecrets[.]com和pandemic-survival-coronavirus[.]com。

### 传统诈骗

![](https://image.3001.net/images/20200423/1587646511_5ea1902f90eec.png!small)

在coronavirusaware[.]xyz和covid19center[.]检测到诈骗活动，如图17所示。攻击者目的是恐吓用户，迫使他们打电话，攻击者利用电话进行诈骗。

### 病毒网站

![](https://image.3001.net/images/20200423/1587646661_5ea190c502983.png!small)

发现许多新冠病毒网站，比如coronamasksupply[.]com和coronavirusinrelatime[.]com在浏览器中对用户操作进行劫持。

## 总结

当人们的恐惧感增强时，总会有网络罪犯试图从中获利。就冠状病毒而言，每天注册的冠状病毒相关域名数量急剧增加，恶意冠状病毒NRD平均每日数量增加569%，高风险域名平均每日数量增加788%。自1月1日以来，发现2022个恶意和40261个高风险NRD。

人们应该对任何带有COVID-19主题的电子邮件或新注册的网站持高度怀疑态度，任何以COVID-19为主题的电子邮件都应该小心处理。

## IOCs

### Credential Harvesting

> corona-masr21[.]com/boa/bankofamerica/login.php
>
> corona-masr21[.]com/apple-online
>
> corona-masr3[.]com/CAZANOVA%20TRUE%20LOGIN%20SMART%202019/
>
> corona-virusus[.]com

### Scams

> allsurgicalfacemask[.]com
>
> surgicalfacemaskpharmacyonline[.]com
>
> selectsanitizer[.]com
>
> survivecoronavirus[.]org
>
> facemasksus[.]com
>
> coronavirussecrets[.]com
>
> pandemic-survival-coronavirus[.]com
>
> internet-covid19.xyz
>
> coronavirusaware[.]xyz
>
> covid19center[.]online
>
> Whatsapp[.]version[.]gratis
>
> whatsapp[.]cc0[.]co

### Coinminers

> coronamasksupply[.]com
>
> coronavirusinrealtime[.]com
>
> coronashirts[.]store

### Black Hat SEO

> coronavirus-latest-update[.]info
>
> coronavirus-com[.]info
>
> sharkroulette[.]com
>
> Illicit pharmacy:
>
> covid19-remedy[.]com
>
> rxcovid[.]com
>
> anticovid19-pharmacy[.]com

### OtherDomains

> coronavirus2day[.]com
>
> hashtag.sslproviders[.]net
>
> coronavirus-game[.]ru
>
> buygoods[.]com

 ***参考来源：[unit42](https://unit42.paloaltonetworks.com/how-cybercriminals-prey-on-the-covid-19-pandemic/)，由Kriston编译，转载请注明来自FreeBuf.COM**

