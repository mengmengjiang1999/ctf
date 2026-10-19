# 背景

近期的 Firefox漏洞CVE-2019-11707最早是 Google Project Zero的Samuel
Groß在4月15号提交的，不过他发现的0day只能导致代码执行，却无法进行Firefox的沙盒逃逸，因此如果在实际攻击中利用应该还需要配合一个沙盒逃逸的漏洞。

![image.png](https://image.3001.net/images/20190624/1561348920_5d104b3889814.png!small)

  

随后在近日，数字货币交易机构Coinbase的安全人员向Firefox提交了其内部遭到攻击时捕获到的一个漏洞，该漏洞经过证明为一处沙盒逃逸的漏洞，并被命名为CVE-2019-11708。

![image.png](https://image.3001.net/images/20190624/1561348931_5d104b43954a7.png!small)

后续Coinbase的相关安全人员也公布了其中的 IOC，并且声称其并不是遭受攻击的唯一数字货币交易机构。

Hash：

af10aad603fe227ca27077b83b26543b

de3a8b1e149312dac5b8584a33c3f3c6

C2 IP：

89.34.111.113:443

185.49.69.210:80

并且著名的Mac恶意样本研究小站Objective-See发布了涉及该漏洞事件投递的macOS 后门的分析报告（ _<https://objective-see.com/blog/blog_0x43.html>_ ）。

结合报告披露的内容，有数字加密货币的相关人员收到了如下图的邮件之后，点击了对应的html从而导致后台恶意代码执行，有意思的是其提供的后续恶意代码和之前Coinbase安全人员提供的一致，即de3a8b1e149312dac5b8584a33c3f3c6，因此将这个两次事件联系到一起，猜测这次0day的攻击源头来自于people.ds.cam.ac.uk/nm603/awards/Adams_Prize。

![image.png](https://image.3001.net/images/20190624/1561348938_5d104b4acab4c.png!small)

随后我们对相关线索进行进一步的分析。

# 分析

我们通过vt可以看到Coinbase提供的两个样本，其中主要关注第二个，该样本和之前objective-see中提到的一致。

![image.png](https://image.3001.net/images/20190624/1561349007_5d104b8f4c3f5.png!small)

第一次的提交时间为6月6日，来自于南非，第二次则是6月20日，来自于加拿大。

![image.png](https://image.3001.net/images/20190624/1561349027_5d104ba3a8941.png!small)

再看看由Coinbase提供的两个ip，89.34.111.113:443和185.49.69.210:80

其中89.34.111.113下就有之前提到的de3a8b1e149312dac5b8584a33c3f3c6（IconServicesAgent），除此之外一个还有一个windows相关的样本，上传时间为2018年4月16日。

![Firefox相关攻击事件](https://image.3001.net/images/20190624/1561349067_5d104bcb04006.png!small)

结合奇安信TIP 平台也可以查看到该 IP 历史对应的样本，其为 Emotet，知名的银行木马。

![Firefox相关攻击事件](https://image.3001.net/images/20190624/1561349075_5d104bd312370.png!small)

185.49.69.210:80下则没有太多有效关联信息。

![Firefox相关攻击事件](https://image.3001.net/images/20190624/1561349086_5d104bdea7b63.png!small)

分析下de3a8b1e149312dac5b8584a33c3f3c6这个样本，该样本应该是 Mac 下的 Netwire RAT，Netwire RAT
是一个公开的木马。样本中有一处比较特殊的字符串"hyd7u5jdi8"。

![Firefox相关攻击事件](https://image.3001.net/images/20190624/1561349097_5d104be960602.png!small)

hyd7u5jdi8这个字符比较特殊，其曾在2012年的Netwire样本中出现，该样本号称第一个mac osx及linux的样本。

![Firefox相关攻击事件](https://image.3001.net/images/20190624/1561349106_5d104bf29911b.png!small)

而该Netwire 木马之前也被APT组织和网络犯罪团伙所使用：

例如被认为隶属于伊朗的APT 33所使用， 著名的网络犯罪团伙Carbanak和尼日利亚黑客组织SilverTerrier。

![image.png](https://image.3001.net/images/20190624/1561349123_5d104c03b4773.png!small)

![image.png](https://image.3001.net/images/20190624/1561349127_5d104c075d1ec.png!small)

![image.png](https://image.3001.net/images/20190624/1561349131_5d104c0b234c0.png!small)

有意思的是之后名为Vitali Kremez的研究人员介绍该字符串也出现在 FireEye在2017年5月报的CVE-2017-0261 eps
0day攻击事件中。

![image.png](https://image.3001.net/images/20190624/1561349135_5d104c0fb3f0d.png!small)

而在当时的攻击中最后投递的样本正是Netwire。

![image.png](https://image.3001.net/images/20190624/1561349139_5d104c131b564.png!small)

而从fireeye的报告中可以看到，这起攻击中出现了三个团伙turla，apt28，及一个未知的经济动机组织，该组织使用的正是NETWIERE，且其攻击的目标为全球银行组织在中东的相关机构。

![image.png](https://image.3001.net/images/20190624/1561349143_5d104c174cfdf.png!small)

而我们注意到fireeye在2019年3月底的利用 WinRAR 漏洞CVE-2018-20250的攻击活动报告中的一起攻击活动中，提到了利用 WinRAR
漏洞投递 Netwire 木马，并且使用了89.34.111.113的 C2，其 C2 IP 地址和此次0day 漏洞的攻击 C2相同。

![image.png](https://image.3001.net/images/20190624/1561349146_5d104c1ac5138.png!small)

![image.png](https://image.3001.net/images/20190624/1561349151_5d104c1fce4e4.png!small)

# 总结

当前的证据似乎还不能完全归属到已知的攻击组织，但结合上述关联分析，我们可以做出如下推测：

1\. 该组织应该以经济牟利为重要攻击动机，历史攻击目标可能为银行，并延伸至数字货币交易所

2\. 从目标地域来看，中东似乎是其主要目标，但结合文件上传地分布，也不排除是全球性的

3\. 使用 Netwire 作为其主要的 RAT 工具，值得注意的是 Netwire 是公开的商业版
RAT，并适配与多个平台，攻击者可能使用的带有特定指纹的版本

4\. 攻击者似乎具备较强的0day 漏洞利用能力，但也不排除其是购买的0day 漏洞，但值得注意的是攻击者一直处于活跃之中。

# 参考链接

 _<https://www.bleepingcomputer.com/news/security/firefox-0-day-used-in-targeted-attacks-against-cryptocurrency-firms/>_

 _<https://www.fireeye.com/blog/threat-research/2019/03/winrar-zero-day-abused-in-multiple-campaigns.html>_

 _<https://www.fireeye.com/blog/threat-research/2017/05/eps-processing-zero-days.html>_

 _<https://www.lac.co.jp/lacwatch/pdf/20190619_cecreport_sp.pdf>_

 _<https://objective-see.com/blog/blog_0x43.html>_

 _<https://ti.360.net/blog/articles/winrar-exploit-update/>_

 _<https://www.symantec.com/blogs/threat-intelligence/elfin-apt33-espionage>_

 _<https://www.fireeye.com/blog/threat-research/2017/09/apt33-insights-into-iranian-cyber-espionage.html>_

