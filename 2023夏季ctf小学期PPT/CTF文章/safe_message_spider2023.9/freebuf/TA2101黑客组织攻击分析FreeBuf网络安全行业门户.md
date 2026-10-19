**研究人员最近发现了新的黑客组织攻击活动，被命名为TA2101，其目标是在德国公司和组织安装后门恶意软件。**

##  概述

攻击者冒充德国联邦财政部的联邦议员（Bundeszentralamt fur Steuern），并在电子邮件中使用了相似的域名。

对德国的攻击中，攻击者选择了Cobalt Strike，这是一种商业许可的软件工具，通常用于渗透测试。尽管该产品广泛用作模拟工具，但许多攻击者如Cobalt
Group，APT32和APT19仍将其用作为恶意软件来部署和执行活动。

研究人员还发现攻击者在传播Maze勒索软件时采用了与Cobalt Strike相似的社会工程技术，在对意大利组织攻击时冒充了意大利税务局Agenzia
Delle Entrate。最近还发现该组织在假冒美国邮政服务（USPS），针对美国相关目标传播IcedID银行木马。

##  攻击活动分析

在2019年10月16日至11月12日之间，研究人员观察到攻击者向德国，意大利和美国的组织发送恶意电子邮件消息，这些攻击对象没有特定的垂直领域，但收件人多为商业、IT业，制造业和卫生保健相关行业。

###  2019年10月16日至23日

10月16日至23日，研究人员发现数百封冒充德国联邦财政部的电子邮件，邮件带有德国相关的恶意Microsoft Word附件。

恶意邮件正文为退税相关内容，并诱骗收件人在三天内应提交退款申请（使用附件Microsoft Word文档表单），这些电子邮件主要针对IT服务公司。

![](https://image.3001.net/images/20191119/1574128211_5dd34a539efd0.png!small)打开Microsoft
Word附件后，将执行Microsoft Office宏，进而执行PowerShell脚本，该脚本会将Maze勒索软件下载并安装到受害者的系统上。

![](https://image.3001.net/images/20191119/1574128274_5dd34a929efab.png!small)

###  2019年10月29日

10月29日，研究人员发现数十封冒充意大利税务部电子邮件，邮件带有意大利相关的恶意Microsoft Word附件。

该邮件正文为执法活动通知，通知收货人打开并阅读随附文件，以避免进一步的税费和罚款。

这些电子邮件主要针对制造公司，攻击者将Microsoft Office宏的感染链用于PowerShell脚本中，该脚本最终下载并安装了Maze勒索软件。

![](https://image.3001.net/images/20191119/1574128475_5dd34b5bbb8b3.png!small)下图恶意文档自称是意大利税收部使用的RSA
SecurID密钥。

![](https://image.3001.net/images/20191119/1574128542_5dd34b9e3c1eb.png!small)

###  2019年11月6日

在2019年11月6日，研究人员观察到数百封冒充德国联邦财政部电子邮件，邮件传递带有德国相关的恶意Microsoft Word附件。
该恶意文档声称是德国财政部使用的RSA SecurID密钥。这些电子邮件主要针对商业和IT服务公司，并使用与以前的攻击活动相同的感染链。

![](https://image.3001.net/images/20191119/1574128644_5dd34c04d7acf.png!small)打开Microsoft
Word文档并启用宏会在用户的系统上安装Maze勒索软件，对受害者所有文件进行加密，并在每个目录中以TXT格式保存以下勒索内容。

![](https://image.3001.net/images/20191119/1574128702_5dd34c3e23542.png!small)

###  2019年11月7日

在2019年11月7日，研究人员观察到数百封冒充了德国互联网服务提供商电子邮件，邮件带有德国相关的恶意Microsoft Word附件。

与11月6日的攻击活动一样，攻击者采用了相似的.icu域作为发件人的电子邮件地址。 恶意的Microsoft Word附件带有所谓的RSA
SecurID密钥，其格式类似于11月6日的发现的附件内容。电子邮件主要针对商业和IT服务公司。

![](https://image.3001.net/images/20191119/1574128835_5dd34cc369e22.png!small)

###  2019年11月12日

在2019年11月12日，研究人员观察到数千封冒充美国邮政服务（USPS）的电子邮件，邮件带有英语相关的恶意Microsoft
Word附件，并试图传播IcedID银行木马。

之前的欧洲攻击活动不同，攻击者选择了一个类似.com的uspsdelivery-service.com域，而不是.icu域。 恶意Microsoft
Word附件带有RSA SecurID密钥，其格式与以前活动中使用的相似。

![](https://image.3001.net/images/20191119/1574128997_5dd34d6579f64.png!small)这些电子邮件使用相同的感染链主要针对医疗保健行业。

##  域和URL分析

研究人员观察到了一系列相同的TTP（战术，技术和程序）， 这些措施包括使用.icu域，这些活动中域DNS的SOA记录了相同的电子邮件地址。

攻击者使用的规范URL的格式可重复，且字符串中的word _ /.tmp随时间略有变化，该word_ /
.tmp的使用情况可能与infosec社区在2019年发现的攻击活动有关。

与记录的gladkoff1991@yandex.ru之间的联系不只是最近的Cobalt Strike活动，还涉及2019年9月以“
eFax”为主题的Buran恶意软件攻击活动。

###  German Cobalt Strike/German Tax Office spoof (10.23)

email address: antwortensienicht@bzst-informieren.icu

SOA: gladkoff1991@yandex.ru

Italian Maze Campaign/Italian Ministry of Taxation spoof (10.29)

email address: info@agenziaentrate.icu

SOA: gladkoff1991@yandex.ru

IP: 91.218.114[.]37

German Maze Campaign/German Tax Office spoof (11.6)

此攻击活动使用与10月23日相同的诱饵，包括相同的“ RSA Key”恶意Microsoft Word附件。

German Maze Campaign/German ISP spoof (11.7)

email address: antwortensienicht@bzstinform.icu

SOA: gladkoff1991@yandex.ru

US IcedID Campaign / USPS Spoof (11.12)

Domain:uspsdelivery-service[.]com

SOA: gladkoff1991@yandex.ru

##  总结

以税务为主题的电子邮件攻击目标为2019税务申报人，与财务相关的诱饵已按季节性使用，与税收相关的恶意软件和网络钓鱼活动呈上升趋势。

在2017年，这些活动集中于网络钓鱼和复杂的社会工程学以及银行木马和勒索软件，2018年，这些活动以税收为主题。

随着德国和意大利出现利用类似的税收和退款相关的攻击活动，研究人员已经观察到类似的诈骗，并且攻击者在欧洲分尝试传播木马。最近，攻击者又假冒美国邮政局攻击了美国相关组织。这些诱饵文件越来越复杂，反映出社会工程在在全球电子邮件攻击领域中不断改进，攻击者注重有效性性而不是数量。

##  IOCs

![](https://image.3001.net/images/20191119/1574130321_5dd35291a81c8.png!small)

***参考来源：[proofpoint](https://www.proofpoint.com/us/threat-insight/post/ta2101-plays-government-imposter-distribute-malware-german-italian-and-us)，由Kriston编译，转载请注明来自FreeBuf.COM**

