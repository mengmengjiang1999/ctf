**近期，Palo Alto
Network的研究人员发现了一款名叫XBash的新型恶意软件，而这款恶意软件不仅是一个勒索软件，而且它还融合了挖矿、僵尸网络和蠕虫等功能。**

![a.png](https://image.3001.net/images/20180926/1537895356_5baa6bbc43648.png!small)

研究人员表示，XBash主要针对的是Linux和Windows服务器。该恶意软件采用Python开发，并且使用[PyInstaller](http://www.pyinstaller.org/)这样的合法工具来将恶意软件主体隐藏在了自包含的Linux
ELF可执行文件中以便实现传播。

XBash的恶意代码借鉴了很多不同种类的恶意软件，例如勒索软件、加密货币挖矿软件、僵尸网络以及蠕虫病毒等等。

Palo
AltoNetworks的研究人员在[分析报告](https://researchcenter.paloaltonetworks.com/2018/09/unit42-xbash-combines-botnet-ransomware-coinmining-worm-targets-linux-windows/)中写到：“XBash融合了勒索软件和其他的恶意攻击能力，而且还具备自我传播的功能，这也就意味着它拥有跟WannaCry或[Petya/NotPetya](https://securityaffairs.co/wordpress/63081/malware/zlab-malware-analysis-report-notpetya.html)类似的蠕虫功能。启用了‘蠕虫功能’（该功能目前还没有启用）之后，它将能够迅速在受感染的目标组织网络中传播。”

在对恶意代码进行了深入分析之后，研究人员将XBash背后的网络犯罪组织锁定在了[IronGroup](https://securityaffairs.co/wordpress/73211/cyber-crime/iron-cybercrime-group-hackingteam.html)的身上。

Iron
Group这个网络犯罪组织从2016年开始就一直活跃至今，当初该组织因为Iron勒索软件而出名，近几年该组织也开发了多种恶意软件，其中包括后门、恶意挖矿软件、以及多种针对移动端和桌面端系统的勒索软件。

根据Intezer发布的分析报告，在2018年4月份，研究人员在监控公共数据Feed的时候，发现了一个使用了HackingTeam泄漏的RCS源代码的未知后门。研究人员表示：“我们发现这个后门是由Iron
Group开发的，而这个网络犯罪组织也是Iron勒索软件的开发组织。目前为止，已经有数千名用户遭到了Iron Group的攻击。”

除此之外，XBash还可以自动搜索互联网中存在安全漏洞的服务器，恶意代码会搜索没有及时打补丁的Web应用程序，并使用一系列漏洞利用代码或基于字典的爆破攻击来搜索用户凭证。当XBash搜索到了正在运行的Hadoop、Redis或ActiveMQ之后，它将尝试对目标服务器实施攻击，并进行自我传播。

## XBash目前主要利用的三种漏洞如下：

1.[HadoopYARN 资源管理器中未经认证的代码执行漏洞](https://github.com/rapid7/metasploit-framework/blob/master/modules/exploits/linux/http/hadoop_unauth_exec.rb)，该漏洞最早在2016年10月份就被曝光了，并且一直没有分配CVE编号。

2.[Redis任意文件写入和远程代码执行漏洞](https://packetstormsecurity.com/files/134200/Redis-Remote-Command-Execution.html)，该漏洞最早在2015年10月份就被曝光了，并且同样没有分配CVE编号。

3.[ActiveMQ任意文件写入漏洞](http://activemq.apache.org/security-advisories.data/CVE-2016-3088-announcement.txt)，CVE-2016-3088。

这款恶意软件在成功入侵了存在漏洞的Redis服务器后，将能够感染同一网络内的其他Windows系统。

XBash的扫描组件可扫描的目标有Web服务器（HTTP）, VNC, MariaDB, MySQL, PostgreSQL,Redis, MongoDB,
Oracle DB, CouchDB, ElasticSearch, Memcached, FTP, Telnet, RDP,UPnP/SSDP, NTP,
DNS, SNMP, LDAP, Rexec, Rlogin, Rsh和Rsync。

从非法盈利方面来看，攻击者主要通过在目标Windows系统中实现恶意挖矿以及针对运行了数据库服务的Linux服务器进行勒索攻击来实现牟利。

XBash组件可以扫描和删除MySQL、MongoDB和PostgreSQL数据库，并向目标主机发送勒索消息，然后要求用户支付0.02个比特币来“赎回”他们的数据。

![b.png](https://image.3001.net/images/20180926/1537895364_5baa6bc41cde9.png!small)

不幸的是，就算用户支付了赎金，他们也不可能再拿回自己的数据了，因为恶意软件在删除数据的时候根本就没备份…

研究人员表示，他们对XBash样本中的比特币钱包地址进行了分析，分析结果表明，从2018年5月份开始，相关的钱包总共有48笔转账交易，收入总共为0.964个比特币，当时的价值大约为6000美金。

研究人员还发现，XBash中还有一部分针对企业网络的代码，即一个名叫“LanScan”的Python类，这个类可以帮助恶意软件扫描本地局域网信息，并收集网络内其他主机的IP地址。不过这个类目前还没有激活使用，说明攻击者还在开发这个功能。

专家认为，XBash之后还会出现更多新的变种，因此广大用户还需保持警惕。关于XBash的更多信息，可以从研究人员发布的报告中获取【[传送门](https://researchcenter.paloaltonetworks.com/2018/09/unit42-xbash-combines-botnet-ransomware-coinmining-worm-targets-linux-windows/)】。

***参考来源：[securityaffairs](https://securityaffairs.co/wordpress/76305/malware/xbash-malware.html)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

