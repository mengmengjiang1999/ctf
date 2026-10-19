**概述  
**

去年年末，奇安信病毒响应中心发布了《不给钱就撕票！论现代勒索软件的野蛮进化史》[https://mp.weixin.qq.com/s/xnt6iVLNKRyVvqfCO_-Lmg](https://mp.weixin.qq.com/s?__biz=MzI5Mzg5MDM3NQ==&mid=2247484629&idx=1&sn=50e1706f247206deb1450e4aace236d9&scene=21#wechat_redirect)一文，文中提到了勒索软件开始不单纯进行勒索文件从而获取赎金，而且还开始对敏感文件进行窃取，从而加大勒索的范围：即不交赎金，我让你电脑文件无法打开使用不成，还让你的文件宣布泄露出去。

而Ryuk勒索软件，相信不少前线应急选手都有所耳闻，近日，奇安信病毒响应中心在日常样本监控过程中捕获了Ryuk勒索软件释放的窃密模块，发现其进行了大幅度更新。

除此之外，我们偶然发现，该窃密模块居然是第三方开发，从而分发给Ryuk勒索软件团伙进行”分红”，这让我们对勒索黑产产业链有了新的认识。

 **  
**

 **样本分析** **  
**

 **样本主要功能：**
样本经过内存加载后，遍历磁盘文件，排除指定目录和后缀，搜索特定的文件，并与内置的字符串列表进行比对，窃取文档、源代码、比特别钱包、图片等文件，将匹配成功的文件上传至FTP服务器上，还会获取ARP表中的IP地址列表，搜索共享文件。

下列为具体分析过程。

样本外层经过复杂的混淆，给内置的ShellCode分配内存并调用：  

![640?wx_fmt=png](https://mmbiz.qpic.cn/sz_mmbiz_png/icIVJN2qXD6tiaQQXHo5Bw0s1gcz5AqBjP4J8T8lUt9fsCRqicR44Gd0YZZQfQpSPnwg6xJz3l8ZYRMFF4Tzf9ZXA/640?wx_fmt=png)

内存加载：

![640?wx_fmt=png](https://mmbiz.qpic.cn/sz_mmbiz_png/icIVJN2qXD6tiaQQXHo5Bw0s1gcz5AqBjPfOXVl8r8x0mancvm8xenSKmgJPlzKgoGNaNSlyjhyc6NIR2kZtupzw/640?wx_fmt=png)

获取磁盘信息之后开始遍历磁盘文件，排除的目录和指定文件如下：

![640?wx_fmt=png](https://mmbiz.qpic.cn/sz_mmbiz_png/icIVJN2qXD6tiaQQXHo5Bw0s1gcz5AqBjP3G6CNpG3fcdD3m5S22fcsoAnPlickA3eqUN539wxnrb6sYfpiaic1jjkw/640?wx_fmt=png)

  

其中出现了Ryuk的勒索信“RyukReadMe.txt”，排除的后缀名如下：

![640?wx_fmt=png](https://mmbiz.qpic.cn/sz_mmbiz_png/icIVJN2qXD6tiaQQXHo5Bw0s1gcz5AqBjPglkVP2C8cSeKRrzFIEd5oicnXLdfgqprSnZWj2mZV5ZclBHxq8THIibg/640?wx_fmt=png)

  

除此之外还会跳过经过Ryuk加密后的文件，.RYK为经过Ryuk勒索加密后的后缀名。

![640?wx_fmt=png](https://mmbiz.qpic.cn/sz_mmbiz_png/icIVJN2qXD6tiaQQXHo5Bw0s1gcz5AqBjPU49XQSt686p1icibWUicqGTgbnPpKedXPzTykvBzZiahAbPCkCtbYgnBtg/640?wx_fmt=png)

寻找以下指定后缀，主要目的是窃取源代码、文档、比特币钱包和图片等文件：

![640?wx_fmt=png](https://mmbiz.qpic.cn/sz_mmbiz_png/icIVJN2qXD6tiaQQXHo5Bw0s1gcz5AqBjPDeqYlgMBm7FhpmBQSb8lpltyibMGb7uqWZI8kP87Cn23ae54KHvyiayg/640?wx_fmt=png)

判断文件名是否存在如下字符串：

![640?wx_fmt=png](https://mmbiz.qpic.cn/sz_mmbiz_png/icIVJN2qXD6tiaQQXHo5Bw0s1gcz5AqBjPbWOEKKujrzk13ZI9u0b8pAtgoEgucXSt2mkObDJwoypyWhb3PaGxjw/640?wx_fmt=png)

判断文件内容是否存在如下字符串：

![640?wx_fmt=png](https://mmbiz.qpic.cn/sz_mmbiz_png/icIVJN2qXD6tiaQQXHo5Bw0s1gcz5AqBjPlTKfebTS1uicTyjdQ4DvE14koLvEChPmY06iakVjJBwTCkKZWuPvt8Ag/640?wx_fmt=png)

  

将符合上述条件的文件上传到FTP服务器上，密码和账号均为anonymous：

![640?wx_fmt=png](https://mmbiz.qpic.cn/sz_mmbiz_png/icIVJN2qXD6tiaQQXHo5Bw0s1gcz5AqBjPEbGnpiaCNhficLl7YmVibichthcdoEvXzgbvWGHa6hLWYs2PicWFTPC5Jzg/640?wx_fmt=png)

在老版的代码中还会读取ARP表中的IP地址，搜索共享文件：

![640?wx_fmt=png](https://mmbiz.qpic.cn/sz_mmbiz_png/icIVJN2qXD6tiaQQXHo5Bw0s1gcz5AqBjP0xNepAofTQFPeCwOyZCuRjk43kcPjKuKrMSzicIrACviahoHsSZmQuZA/640?wx_fmt=png)

将内置的字符串列表进行分类，发现不少敏感词汇：

行业| 关键词(括号内为中文翻译)  
---|---  
军事| 'spy'（间谍）, 'radar'（雷达）, 'agent'（代理）, 'newswire'（新闻通讯）,'fraud'（欺诈）,
'hack'（黑客）, 'defence'（防御）, 'treason'（叛国）, 'censored'（审查）, 'bribery'（贿赂）,
'contraband'（违禁品）, 'attack'（攻击）, 'military'（军事）, 'tank'（坦克）, 'convict'（定罪）,
'scheme'（方案）, 'tactical'（战术）, 'explosive'（***）, 'drug'（毒品）,
'traitor'（叛徒）,'embeddedspy'（嵌入式间谍）, 'radio'（无线电）, 'submarine'（潜艇），‘NATO’（北约）等。  
银行| 'SWIFT', 'IBAN', 'balance', 'statement', 'checking', 'saving', 'routing'  
政府| 'clandestine'（秘密）, 'investigation'（调查）, 'federal'（联邦）, 'bureau'（局）,
'government'（政府）, 'security'（安全）, 'victim'（受害者）,
'court'（法院），“NSA”（国家安全局），“FBI”（联邦调查局）等  
个人| 'personal'（个人）, 'passport'（**）  
姓氏| 'Emma', 'Liam, 'Olivia, 'Noah', 'William', 'Isabella', 'James', 'Sophia',
'Logan'  
  
**关联分析** ****  

在对老版的窃密模块进行分析时，我们发现老版并没有shellcode内存加载的行为，通过对新捕获窃密模块的shellcode进行分析关联，发现这套Shellcode不止应用于Ryuk的窃密模块，其背后应该存在一个分发商。

Shellcode对比图如下，左为关联的样本：

![640?wx_fmt=png](https://mmbiz.qpic.cn/sz_mmbiz_png/icIVJN2qXD6tiaQQXHo5Bw0s1gcz5AqBjPryUj7NPSxPVGibWp2FKtaZFiabD1OmH1LxQaqicdp39uTcwgRLE5zdopg/640?wx_fmt=png)

发现只有立即数不同其余完全相同，内存加载后发现是Phobos勒索软件：

![640?wx_fmt=png](https://mmbiz.qpic.cn/sz_mmbiz_png/icIVJN2qXD6tiaQQXHo5Bw0s1gcz5AqBjPLZU4N9ReCE7uJ2FgsQ5MBIkbUyDIFlyDjD3maELzFR2jIGl90IhKDQ/640?wx_fmt=png)

在另一个关联样本中，shellcode对比图，左为关联样本：

![640?wx_fmt=png](https://mmbiz.qpic.cn/sz_mmbiz_png/icIVJN2qXD6tiaQQXHo5Bw0s1gcz5AqBjPamYGROXlkkFEzoicI2rgQhDV94Vnp1ia3picvVVia4NkvV4uAInrn0YzUQ/640?wx_fmt=png)

内存加载后为Hermes勒索软件：

![640?wx_fmt=png](https://mmbiz.qpic.cn/sz_mmbiz_png/icIVJN2qXD6tiaQQXHo5Bw0s1gcz5AqBjPAoPwqiaIbVJvZmPSmPIMSLBh3D0y4SU6xrQNQ5JR0qxkyHr7CyibLdkA/640?wx_fmt=png)

除了投放勒索软件，该分发商还会投放Spy类的软件，限于篇幅就不一一分析了。

目前，越来越多的勒索软件开始加入信息窃取的行列中，DoppelPaymer最近在其勒索信中宣布如果不支付赎金将会发布或出售窃取的信息。

![640?wx_fmt=png](https://mmbiz.qpic.cn/sz_mmbiz_png/icIVJN2qXD6tiaQQXHo5Bw0s1gcz5AqBjPsfLZkCMQWHEj3wK2lKy3LXGOx7uicBFhtHRNXRVW55tvLWjY4D4Dbhg/640?wx_fmt=png)

在地下论坛中，勒索交易已然成为常态，出售勒索的代理商或者开发者比比皆是：

![640?wx_fmt=png](https://mmbiz.qpic.cn/sz_mmbiz_png/icIVJN2qXD6tiaQQXHo5Bw0s1gcz5AqBjPVQlTiazAhsAZMvIDMicUuWficLSajBc757FXQAYibiauHVoUkecic8OESFzQ/640?wx_fmt=png)

而有些开发者正在寻求分发商：

![640?wx_fmt=png](https://mmbiz.qpic.cn/sz_mmbiz_png/icIVJN2qXD6tiaQQXHo5Bw0s1gcz5AqBjPicvAuzbOP2x3X8LGibJsCiaSGRd6BicgstNxMc4W5whGP7UGgfrKZCTjIQ/640?wx_fmt=png)

可见，窃密模块开发者，与勒索软件分发商的完美融合，或将给业界造成更大的打击。  

  

 **总结** ****

基于奇安信的多维度大数据关联分析，我们发现早在2019年九月份时Ryuk就已经使用“窃密”模块搜集被害者信息。
已经监控到老版“窃密”模块已有国内用户中招，由于C2服务器早已失效，故损失面积较小：最新捕获的“窃密”模块暂无用户中招。

因此，鉴于国内有用户中招，奇安信病毒响应中心提醒用户，疫情在家远程办公，不要点击来源不明的邮件和可执行文件，同时提高个人的安全意识，从而可以防止用户隐私信息被盗取的风险，奇安信病毒响应中心会持续对勒索软件窃密趋势进行跟踪

同时基于奇安信威胁情报中心的威胁情报数据的全线产品，包括奇安信威胁情报平台（TIP）、天擎、天眼高级威胁检测系统、奇安信NGSOC等，都已经支持对该家族的精确检测。  

  

 **IOC** ****

MD5：

fab16b4acf2515cd6b86f70531a05664

d1271a784906a817308eced597873667

73bbbc8ae0c442025a926402c114bd1e

FTP：

66.42.108.141

66.42.76.46

