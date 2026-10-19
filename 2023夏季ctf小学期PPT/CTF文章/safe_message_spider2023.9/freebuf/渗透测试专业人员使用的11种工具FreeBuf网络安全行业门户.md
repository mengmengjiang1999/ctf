**渗透测试是模拟一种网络攻击，在真正的黑客入侵之前，模拟黑客入侵企业网络来发现薄弱之处。就像电影《Sneakers》一样，黑客顾问闯入公司网络以发现网络的弱点。其中，渗透测试人员或白帽都使用了黑客可用的工具和技术。**  

回到过去的旧时代，黑客入侵是一件非常困难的事，并且需要大量的手动操作。然而如今，一整套的自动化测试工具似乎改造了黑客，他们甚至可以增强计算机的性能，进行比以往更多的测试。

工欲善其事，必先利其器。既然如今已经有了更为便捷、快速的渗透测试工具，这对现代渗透测试工作者无疑是有很大的帮助的。以下列出了他们使用的一些工具。

![1433918403802.png](https://image.3001.net/images/20200227/15827874732437.png!small)

##  一、Kali Linux

Kali是基本的渗透测试操作系统，为大多数人采用，除非是掌握尖端知识或有特殊情况。Kali以前称为BackTrack Linux，由Offensive
Security（OffSec，进行OSCP认证）的优秀人员维护，如今在各种方面都进行了优化，可以用作渗透测试员的攻击工具。

虽然可以在自己的硬件上运行Kali，但渗透测试人员在OS
X或Windows上使用Kali虚拟机的情况也十分普遍。Kali附带了此处提到的大多数工具，并且是大多数人默认的渗透测试操作系统。不过值得注意的是，Kali优化了进攻而非防御，因此很容易被反过来利用。不要将过多的机密文件保留在Kali
VM中。

![kali_linux_tools_abstract_gears_binary_data_by_nevarpp_gettyimages-688718788_2400x1600-100832674-large.jpg](https://image.3001.net/images/20200227/15827896804348.jpg!small)

##  二、Nmap

nmap是网络扫描仪的缩写，它的延伸是端口扫描仪。作为一种经过实践检验的渗透测试工具，几乎所有人都可以使用。哪些端口是开放的？这些端口上正在运行什么？对于侦察阶段的渗透测试人员来说，这是必不可少的信息，而nmap通常是完成该任务的最佳工具。

尽管非技术性高管人员偶尔会抱怨在端口扫描企业，但nmap本身是完全合法的，就像是敲附近每个人的家门来查看是否有人在家。许多合法的组织，例如保险公司，Shodan和Censys
这样的互联网搜索引擎以及BitSight这样的风险评级企业，都使用专门的端口扫描软件（通常是nmap竞争对手masscan或zmap）定期扫描整个IPv4范围，以绘制整个企业大大小小的公共安全态势。话虽如此，那些恶意攻击者也会进行端口扫描，因此需要进行日志记录以备将来参考。

##  三、Metasploit

当您可以利用Metasploit时，为什么还受到漏洞的困扰？这个软件就像是一把弓箭：瞄准目标，选择漏洞，选择有效载荷，然后发射。对于大多数渗透测试者来说不可或缺，metasploit可以自动进行大量以前繁琐的工作，它是“世界上使用最广泛的渗透测试框架”。一个由Rapid7提供商业支持的开源项目，Metasploit是防御者确保其系统免受攻击的必要工具。

##  四、Wireshark

Wireshark是一种无处不在的工具，可用于了解跨网络传输的流量。虽然通常用于深入研究日常的TCP /
IP连接问题，但Wireshark支持对数百种协议进行分析，包括对其中许多协议的实时分析和解密支持。如果您是渗透测试的新手，Wireshark是一个必须学习的工具。

##  五、John the Ripper

这里的John不是维多利亚时代的伦敦连环杀人凶手，但是却会以您的GPU运作速度破解密码。该密码破解程序是开源的，用于离线密码破解。John利用可能的密码单词列表，然后“@”代替“a”，以“5”代替“s”，以此类推地进行转换，或者它可以用强大的硬件无限运行直到找到密码为止。考虑到绝大多数人使用的是简单的短密码，John经常可以成功破解密码。

![titel-cas-cybersecurity.png](https://image.3001.net/images/20200227/15827897544999.png!small)

##  六、Hashcat

“世界上最快、最先进的密码恢复实用程序”，以此来描述Hashcat或许并不为过，Hashcat使用者对其价值自然也是心知肚明。Hashcat可与John
the Ripper一较高下。它是破解哈希的首选渗透测试工具，并且hashcat支持多种猜测密码的蛮力攻击，包括字典和掩码攻击。

渗透测试通常会涉及哈希密码的泄露，利用这些凭证可以将像hashcat这样的程序脱机，至少希望猜出或强行使用其中一些密码。

Hashcat在现代GPU上运行最好。传统的hashcat仍支持CPU上的哈希破解，但是要提醒用户的是，这比显卡的处理能力要慢得多。

##  七、Hydra

Hydra 是John the
Ripper的同类工具，可用于在线破解密码（例如SSH或FTP登录、IMAP、IRC、RDP等）。将Hydra用于指定的破解服务，有必要的话可以输入单词列表，然后开始破解。诸如Hydra之类的工具提醒人们，在一系列登录尝试之后，限制密码和断开用户连接是可以成功抵御攻击的。

![512727-637142599573511576-16x9.jpg](https://image.3001.net/images/20200227/15827897224894.jpg!small)

##  八、Burp Suite

如果不提及Web漏洞扫描程序Burp Suite，对渗透测试工具的讨论就是不完整的，而Burp
Suite不同于到目前为止提到的其他工具，它是付费的，是一款专业人员常用的昂贵的工具。虽然有一个Burp Suite社区版，但它缺少许多功能，并且Burp
Suite企业版的价格为每年3999美元。

不过，对得起这个价格的理由在于，Burp
Suite是一个非常有效的Web漏洞扫描程序。将其用于要测试的网络资产，准备就绪后即可运行。Burp的竞争对手Nessus也提供了类似功能的产品，当然价格也差不多。

##  九、Zed Attack Proxy

那些没有买Burp Suite的人会发现OWASP的Zed Attack
Proxy（ZAP）几乎一样有效，它是完全免费的工具。顾名思义，ZAP置于浏览器和测试网站之间（又名中间人），允许拦截流量进行检查和修改。它缺少Burp的许多细节，但是它的开放源代码许可证更容易进行大规模的部署，同时也更便宜。对于初学者来说，它是一款很好地了解网络流量脆弱性的工具。ZAP竞争对手Nikto也提供了类似的开源工具。

##  十、sqlmap

大家应该都听过SQL注入？接下来要介绍的是sqlmap。这个非常有效的SQL注入工具是开源的，可以“自动执行检测、利用SQL注入漏洞并接管数据库服务器的过程”。Sqlmap的支对象包括MySQL、Oracle、PostgreSQL、Microsoft
SQL Server、Microsoft Access、IBM DB2、SQLite、Firebird、Sybase、SAP
MaxDB、Informix、HSQLDB和H2。过去的人们曾经不得不用Hot
Needle将SQL注入到硬盘上。而如今sqlmap则无需如此，便捷程度在您的日常工作中脱颖而出。

##  十一、Aircrack-ng

想检测客户的wifi或家庭wifi的安全性如何？用aircrack-ng即可。这个wifi安全审核工具是免费的，但是用户可以购买自己的Pringles“天线”。如今，由于配置不佳、密码错误或加密协议过时等问题，可能会破坏wifi。不管有没有Pringles的“天线”，Aircrack-ng仍是许多人的首选。

 ***参考来源：[csoonline](https://www.csoonline.com/article/2943524/11-penetration-testing-tools-the-pros-use.html)，Sandra1432编译，转载请注明来自FreeBuf.COM**

