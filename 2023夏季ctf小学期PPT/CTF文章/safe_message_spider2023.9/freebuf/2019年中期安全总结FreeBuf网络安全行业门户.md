**2019的前六个月处理了众多网络安全威胁，年中安全综述突出了上半年处理的网络安全威胁，并提供安全解决方案建议，帮助用户和组织确定正确解决方案和防御策略。**

##  勒索工具

###  事件回顾

2019年上半年，网络犯罪分子对他们的勒索目标更具选择性，主要集中在跨国公司、企业甚至政府组织。他们的做法包括向员工发送量身定制的网络钓鱼电子邮件，利用安全漏洞进入网络，然后在网络中横向拓展。

例如，Lockeroga勒索软件在三月份袭击了一家挪威制造公司，并停止了几家工厂的生产，最终导致超过5500万美元的财务损失；马里兰州巴尔的摩市在其系统5月份被Robbinhod勒索软件感染后，已经花费了530万美元的恢复成本。

一些市政组织受到压力，希望支付赎金能迅速恢复受影响系统。佛罗里达州的三个市在数周内受到了不同的勒索软件攻击：Riviera
Beach，受到一个身份不明的勒索软件变种攻击，以及Lake City和Key Biscayne，这两个城市都受到了Ryuk勒索软件的攻击。

![](https://image.3001.net/images/20190904/1567558252_5d6f0a6c7228c.png!small)

这些引人注目的攻击和高额支付与我们从2018年下半年到2019年上半年的勒索软件数量急剧增加相一致，但勒索软件家族种类有所下降。

##
![](https://image.3001.net/images/20190904/1567558423_5d6f0b1747392.png!small)

###  复杂的程序

我们还观察到文件加密之外的破坏程序。一些勒索软件变种，设计了更多的功能以减少受害者恢复文件和系统的机会。

![](https://image.3001.net/images/20190904/1567558510_5d6f0b6e2f346.png!small)

我们的数据显示，上半年各种勒索软件家族都很活跃。但Wannacry仍然是最容易被发现的勒索软件家族，其数量远远超过其他勒索软件家族的总和。

##
![](https://image.3001.net/images/20190904/1567558567_5d6f0ba7218ae.png!small)

##  威胁趋势

###  无文件攻击

![](https://image.3001.net/images/20190904/1567558733_5d6f0c4dd5f88.png!small)

正如我们所预测的，攻击者越来越趋向于无文件攻击手段，或者滥用合法的系统管理和渗透测试工具来隐藏他们的恶意活动。

所谓的无文件攻击不像传统恶意软件那么明显，因为通常不会写入磁盘，而在系统内存中执行，或位于注册表中，或者使用通常列为白名单的工具，如powershell、psexec或windows管理工具。

以下是检测到的使用无文件技术的攻击行为：

![](https://image.3001.net/images/20190904/1567558921_5d6f0d09a0d56.png!small)
[Cryptocurrency-mining malware ](https://blog.trendmicro.com/trendlabs-security-intelligence/miner-malware-spreads-beyond-china-uses-multiple-propagation-methods-including-eternalblue-powershell-abuse/?_ga=2.83862358.1542375649.1567482348-976224299.1564124697)
[Ransomware](https://blog.trendmicro.com/trendlabs-security-intelligence/emotet-distributed-ransomware-loader-for-nozelesn-found-via-managed-detection-and-response/?_ga=2.88893531.1542375649.1567482348-976224299.1564124697) [Banking
trojan](https://blog.trendmicro.com/trendlabs-security-intelligence/fileless-banking-trojan-targeting-brazilian-banks-downloads-possible-botnet-capability-info-stealers/?_ga=2.88893531.1542375649.1567482348-976224299.1564124697)

这些攻击有一个共同点：使用工具PowerShell。对于系统管理员来说，PowerShell是一个方便的工具，但攻击者可以使用它来启动有效payload，无需在受影响的系统本地内存中写入或运行文件。

###  恶意宏软件

恶意宏软件较2018年下半年略有下降。我们对基于宏的威胁的检测大多是在垃圾邮件中的Powload。

Powload经过多年的发展，其有效负载更加多样化，使用隐写术，甚至使用特定地区的标签或词汇。我们还看到其他的恶意宏软件被用于垃圾邮件中。

##
![](https://image.3001.net/images/20190904/1567559349_5d6f0eb5db48b.png!small)

##  邮件威胁

###  网络钓鱼欺诈

网络钓鱼活动在2019年上半年有所下降。数据显示，阻止钓鱼网站访问的次数减少了18%。造成这种下降的原因可能有几个，包括用户对网络钓鱼欺诈的意识提高。在同一时间段内，我们注意到被屏蔽的网络钓鱼URL数量增加了76%。

网络犯罪分子进一步利用人们对知名品牌和工具的信任和多平台的社会工程学进行网络钓鱼。  
![](https://image.3001.net/images/20190904/1567566486_5d6f2a9637afa.png!small)
安卓[照片app](https://blog.trendmicro.com/trendlabs-security-intelligence/various-google-play-beauty-camera-apps-sends-users-pornographic-content-redirects-them-to-phishing-websites-and-collects-their-pictures/?_ga=2.117277126.1542375649.1567482348-976224299.1564124697)钓鱼
[水坑攻击](https://blog.trendmicro.com/trendlabs-security-intelligence/desktop-mobile-phishing-campaign-targets-south-korean-websites-steals-credentials-via-watering-hole/?_ga=2.84871257.1542375649.1567482348-976224299.1564124697)
[浏览器](https://blog.trendmicro.com/trendlabs-security-intelligence/phishing-attack-uses-browser-extension-tool-singlefile-to-obfuscate-malicious-log-in-pages/?_ga=2.84871257.1542375649.1567482348-976224299.1564124697)

###  商业网络诈骗

商业电子邮件诈骗（BEC）是一个简单但成本越来越高的骗局，企业必须警惕。BEC诈骗者使用各种社会工程技术，通常是模仿CEO和其他高管，欺骗不知情的员工将资金转移到他们的账户上。

![](https://image.3001.net/images/20190904/1567566806_5d6f2bd6b8525.png!small)

BEC多年来一直是网络诈骗威胁的一部分，骗子们一直在开发利用受害者的新方法。也有一些实例支持我们的预测，BEC诈骗者将针对公司层次结构较低的员工。

我们的数据显示，从2018年下半年到2019年上半年，通过垃圾邮件进行的性骚扰增加了两倍多，这与我们去年预测的轨迹相符。在联邦调查局2018年收到的与敲诈勒索有关的投诉中，性侵犯占了大多数。

由于性侵犯骗局的敏感性质，受害者很可能会被迫默许性侵犯者的要求。具体例子是，共接着试图通过发布威胁视频来向用户勒索钱财。

##
![](https://image.3001.net/images/20190904/1567566982_5d6f2c86ab3d7.png!small)

##  漏洞

###  硬件缺陷

2018年初，熔毁和幽灵的披露为修补漏洞带来了新的挑战。在2019年上半年，发现了更多的硬件级漏洞。

今年2月，研究人员展示了一个概念证明，显示黑客如何利用enclaves，enclaves旨在保护和访问英特尔Software Guard
Extensions（SGX）中的数据 ，这是一套英特尔核心和Xeon处理器中的指令。

###  高影响漏洞

在2019年上半年的威胁形势中，漏洞占主导地位。通过我们的零日计划（ZDI）报告的大多数漏洞的严重性都很高。

![](https://image.3001.net/images/20190904/1567567327_5d6f2ddf78dfe.png!small)

以下是2019年上半年出现的一些明显的漏洞及其对企业造成的危险：

![](https://image.3001.net/images/20190904/1567567377_5d6f2e11360e3.png!small)

##  IOT和IIOT攻击

###  僵尸网络和蠕虫

正如我们预测的那样，僵尸网络和蠕虫一直在争夺对连接到物联网（IoT）设备的控制权。包括Bashlite以及Omni，Hakai和Yowai等Mirai变种。在受感染的物联网设备上扫描竞争对手，删除其他恶意软件，并嵌入自己的有效载荷。

###  重要基础设施

工业物联网（IIoT）改变了工业设施和关键基础设施的运行方式，提升了效率和为企业提供了运营可视性。
然而，运营技术（OT）和信息技术（IT）的融合也带来了新的安全风险，并导致更广泛的攻击面。

根据3月份发布的一项调查显示，在过去两年中，50％的被调查组织已经发现其关键基础设施遭到了攻击。 在2019年，攻击者正在评估IIoT目标。
Xenotime黑客组织正在探索美国和亚太地区电网的工业控制系统（ICS）。 其组织的恶意软件扫描并列出了目标的远程登录门户和网络中的漏洞。

至2019年中期，已经出现了许多持续和隐蔽的威胁。对于全面防御来说，没有一个简单的答案——企业和用户必须找到一种多层的方法来解决他们的具体安全漏洞。网关、网络、服务器和端点需要保护。对于面对使用复杂技术恶意软件的企业，需要结合专业知识和安全技术的解决方案来更好地检测、关联、响应和补救威胁。

 ***参考来源：[trendmicro](https://www.trendmicro.com/vinfo/us/security/research-and-analysis/threat-reports/roundup/evasive-threats-pervasive-effects)，由Kriston编译，转载请注明来自FreeBuf.COM**

  

