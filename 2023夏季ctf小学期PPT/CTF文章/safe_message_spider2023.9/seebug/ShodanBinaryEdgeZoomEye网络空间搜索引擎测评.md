**来源：<https://www.freebuf.com/fevents/206656.html>**  
**英文原文：<https://www.secjuice.com/new-kids-on-the-block/>**

## 一、前言

许多IT行业的安全研究人员都会遇到这样的情况，他们需要来自技术层面的OSINT（网络空间搜索引擎）数据[1]。也许他们是想调查目标所遭受的攻击面，进行被动侦察，或者想要测量攻击的整体威胁等级。例如去年出现的
[memcached DDoS 攻击](https://www.cloudflare.com/learning/ddos/memcached-ddos-attack/ "memcached DDoS
攻击")，其放大率为10,000倍甚至更高。Shodan当天发布的第一份报告显示，大约有17,000个易受攻击的服务器在线，这很容易被防火墙列入黑名单。

很长一段时间， [shodan.io](https://shodan.io/ "shodan.io")
一枝独秀。虽然它很棒并且被广泛使用，但我意识到其后台发生了很多过滤。我记得大约两三年前，曝出了一个针对Cisco产品的RCE漏洞——虽然Shodan的日点击量很高，但一周后，搜索结果几乎为空。

随着OSINT变得越来越重要，分析师可利用的搜索引擎工具也更加丰富。这就是本文所探讨的内容：我将把Shodan与过去几年出现的两种新服务[Binaryedge](https://www.binaryedge.io/
"Binaryedge")和[Zoomeye](https://www.zoomeye.org/
"Zoomeye")进行比较，这两项服务似乎已经准备好争夺OSINT工具的王冠。此外，我还将比较它们的功能和搜索结果量（虽然会省去价格部分）。

我从以下几点进行比较：

  * 定期的网上扫描功能

  * 搜索、过滤和下载结果的Web界面

  * 过滤选项

  * 将结果集成到第三方工具的API

关于我的比较结果，每个人的体会可能不同，但一切都是我最真实的反馈。

### 1.1 Shodan

[Shodan](https://shodan.io/
"Shodan")在OSINT中几乎人尽皆知。它以[标记和搜索](https://www.shodan.io/explore
"标记和搜索")各种不同设备（包括[网络摄像头](https://www.shodan.io/explore/tag/webcam
"网络摄像头")，[工业控制系统](https://www.shodan.io/explore/category/industrial-control-systems "工业控制系统")和[物联网](https://www.shodan.io/explore/tag/iot
"物联网")设备）的能力而闻名。在那个“天呐！！物联网攻击！我们都死定了”的时代，它是“[物联网搜索引擎](https://www.zdnet.com/article/shodan-the-iot-search-engine-which-shows-us-sleeping-kids-and-how-we-throw-away-our-privacy/
"物联网搜索引擎")”的首选。Shodan制定了全互联网OSINT数据的行业标准，并且你一定能在上面找到[乐趣](https://www.shodan.io/search?query=%22default+password%22+cisco
"乐趣")。

**Shodan的优点：**

  * 因 API和许多模块以及语言集成而便于开发；

  * 许多东西可集成到其他软件系统中（例如：标签、保存的搜索结果等）。

Shodan的缺点：

  * 缺乏对付费客户的人力支持；

  * 偶尔的特定搜索结果被刻意屏蔽很烦人；

  * 在界面中没有过滤proto:tcp/udp的选项（虽然有一个，但没有记录，至少我没有发现关于它的任何信息）。 

## 1.2 BinaryEdge 和 ZoomEye 闪亮登场

[BinaryEdge](https://www.binaryedge.io/
"BinaryEdge")是一家瑞士公司，它进行全网范围内的扫描，并在[博客](https://blog.binaryedge.io/
"博客")上发布大量的结果、发现和报告（主要针对技术用户）。BinaryEdge对开放的[mongodb/redis/memcache-databases](https://blog.binaryedge.io/2015/08/10/data-technologies-and-security-part-1/ "mongodb/redis/memcache-databases")的分析引起了我的注意，我大量引用过这些数据库。他们在开放平台方面迈出了巨大的一步，将其发展为一个具有广泛搜索、过滤和下载功能的OSINT工具，现在似乎能够与Shodan匹敌。

**BinaryEdge 的优点：**

  * 更新新功能的速度快；

  * 发表技术博客。

BinaryEdge的缺点：

  * 当他们将服务运用到其他解决方案中时，例如对开放端口的IP进行批量检查时，API调用的价格十分昂贵。每天用 BinaryEdge 检查50,000个IP肯定不便宜。

[ZoomEye](https://www.zoomeye.org/
"ZoomEye")由中国的[知道创宇404实验室](https://medium.com/@knownsec404team
"知道创宇404实验室")开发，他们还运营着出色的[Seebug漏洞平台](https://www.seebug.org/
"Seebug漏洞平台")，并进行了大量的安全研究。ZoomEye于两年前引起了我的注意，当时我用它来代替Shodan，那时他们的结果并不像Shodan那么详细。然而在今年，出现了许多[有趣的RCE漏洞](https://paper.seebug.org/886/
"有趣的RCE漏洞")时，我再次使用ZoomEye，发现他们已经可以提供相当可靠的搜索结果。

**ZoomEye的优点：**

  * 进步迅速，飞跃巨大；

  * 项目背后极好的人力支持。 

ZoomEye的缺点：

  * 需要用手机号完成注册。

## 二、产品功能

纯OSINT任务的基本功能：

![](https://images.seebug.org/content/images/2019/07/a301ff6d-a784-4220-8d0d-9a00689c1ebc.png-w331s)

搜索结果的截图如下。

Shodan：

![](https://images.seebug.org/content/images/2019/07/70d5e196-3bd4-42c5-b883-18defa7918da.png-w331s)

BinaryEdge：

![](https://images.seebug.org/content/images/2019/07/f3bdd368-54f8-43af-b947-ed99debabbec.png-w331s)

ZoomEye：

![](https://images.seebug.org/content/images/2019/07/26aff1e2-fe31-4bb1-a550-4f93d86e7467.png-w331s)

**每种产品的优点：**

共同点：

  * 能够搜索和过滤不仅仅是IP和端口的信息；

  * 可以呈现并搜索扫描时收集到的全部标题和信息（如cookie、serverheaders、versions）；

  * 下载全部搜索结果。

Shodan：

  * 界面简洁，良好的深入挖掘和聚合功能，显示部分标题信息；

  * 搜索结果与漏洞的关联良好。

BinaryEdge:

  * 在进行大规模研究时，可进行ASN搜索无疑是一个巨大的优势；

  * 实用的图像搜索功能。 

ZoomEye:

  * 历史记录触手可得，且可以限制特定时间的搜索；

  * 搜索结果与漏洞的关联十分出色。

一旦你习惯了每个操作界面，就会发现它们的运行非常符合逻辑，并且便于开发。

## 三、搜索结果

现在来看看有趣的部分：我检查了各种目标的搜索结果，比如漏洞相关服务和一般的服务/产品。

需要注意的是：

  * 以下数据的有效日期截止到2019-06-09；

  * ZoomEye的搜索结果已被过滤，只包含2019-01-01以后的搜索结果。

### 3.1 漏洞相关服务

我挑选了今年曝出的一些不错的RCE漏洞，将它们按日期进行升序排序，链接到了包含漏洞详情的文章，并给出了CVE。

**DATE**

|

**VULN/CVE**

|

**SHODAN**

|

**BINARYEDGE**

|

**ZOOMEYE**  
  
---|---|---|---|---  
  
**2019-03-20** ****

|  |

[Confluence RCE](https://paper.seebug.org/886/)  
[CVE-2019-3396](https://www.cvedetails.com/cve/CVE-2019-2725/)  
  
---  
  
_[19.000](https://www.shodan.io/search?query=x-confluence)_

|  |

_[53.000](https://app.binaryedge.io/services/query?query=x-confluence&page=1)_  
  
---  
  
|

[34.000](https://www.zoomeye.org/searchResult?q=x-confluence%20%2Bafter%3A%222019-01-01%22%20%2Bbefore%3A%222020-01-01%22&t=all)  
  
---  
  
**2019-03-21** ****

|

_[Nexus Repository Manager RCE](https://support.sonatype.com/hc/en-us/articles/360017310793-CVE-2019-7238-Nexus-Repository-Manager-3-Missing-Access-Controls-and-Remote-Code-Execution-2019-02-05)_  
_[CVE-2019-7238](https://www.cvedetails.com/cve/CVE-2019-7238/)_

|

_[5.500](https://www.shodan.io/search?query=%22Nexus+Repository+Manager%22+port%3A%228081%22)_

|

_[200](https://app.binaryedge.io/services/query?query=%22Nexus%20Repository%20Manager%22%20port:%228081%22&page=1)_

|

_[9.100](https://www.zoomeye.org/searchResult?q=%22Nexus%20Repository%20Manager%22%20%2Bport:%228081%22%20%2Bafter:%222019-01-01%22%20%2Bbefore:%222020-01-01%22&t=all)_  
  
**2019-04-04** ****

|

_[WebLogic RCE](https://medium.com/@knownsec404team/knownsec-404-team-oracle-weblogic-deserialization-rce-vulnerability-0day-alert-90dd9a79ae93)_  
_[CVE-2019-2725](https://www.cvedetails.com/cve/CVE-2019-2725/)_

|

_[2.000](https://www.shodan.io/search?query=weblogic)_

|

_[84.000](https://app.binaryedge.io/services/query?query=weblogic&page=1)_

|

_[40.000](https://www.zoomeye.org/searchResult?q=weblogic%20%2Bafter:%222019-01-01%22%20%2Bbefore:%222020-01-01%22&t=all&t=host)_  
  
**2019-05-09** ****

|

_[Typo3 RCE](https://typo3.org/security/advisory/typo3-core-sa-2019-012/)_  
_[CVE-2019-11832](https://www.cvedetails.com/cve/CVE-2019-11832/)_

|

_[8.100](https://www.shodan.io/search?query=fe_typo_user)_

|

_[11.000](https://app.binaryedge.io/services/query?query=fe_typo_user&page=1)_

|  |

[15.000](https://www.zoomeye.org/searchResult?q=fe_typo_user%20%2Bafter:%222019-01-01%22%20%2Bbefore:%222020-01-01%22&t=all&t=web)  
  
---  
  
**2019-05-14** ****

|  |

[Windows RDP RCE](https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2019-0708)  
[CVE-2019-0708](https://www.cvedetails.com/cve/CVE-2019-0708/)  
  
---  
  
|

_[2.600.000
[3]](https://www.shodan.io/search?query=port%3A3389+%22Remote+Desktop+Protocol%22)_  
  
---  
  
_[10.000.000](https://app.binaryedge.io/services/query?query=ms-wbt-server%20port:%223389%22%20protocol:%22tcp%22&page=1)_

|

_[7.000.000](https://www.zoomeye.org/searchResult?q=%2Bservice%3A%22ms-wbt-server%22%20%2Bafter:%222019-01-01%22%20%2Bbefore:%222020-01-01%22%20%2Bservice:%22ms-wbt-server%22%20%2Bport:%223389%22&t=all)_  
  
对比图表显示如下：

![](https://images.seebug.org/content/images/2019/07/d90adb35-0567-4c96-b60d-fba9873635bb.png-w331s)

结果不言而喻。

### 3.2 常规服务搜索结果

在第二步中，我搜索了一些服务并比较了这些数字。

**SERVICE**

|

**SHODAN**

|

**BINARYEDGE**

|

**ZOOMEYE**  
  
---|---|---|---  
  
**Memcached** ****

|

[34.000](https://www.shodan.io/search?query=product%3A%22Memcached%22)

|

_[19.000](https://app.binaryedge.io/services/query?query=product:%22Memcached%22&page=1)_

|

_[45.000](https://www.zoomeye.org/searchResult?q=port%3A11211%20%2Bafter:%222019-01-01%22%20%2Bbefore:%222020-01-01%22%20%2Bapp:%22Memcached%22&t=all)_  
  
**MongoDB** ****

|

_[64.000](https://www.shodan.io/search?query=product%3A%22mongodb%22)_

|

_[72.000](https://app.binaryedge.io/services/query?query=product:%22mongodb%22&page=1)_

|

_[46.000](https://www.zoomeye.org/searchResult?q=mongodb%20%2Bafter%3A%222019-01-01%22%20%2Bbefore%3A%222020-01-01%22)_  
  
**SNMP** ****

|

[2.100.000](https://www.shodan.io/search?query=port%3A161)

|

_[0](https://app.binaryedge.io/services/query?query=port:161%20%20protocol:%22udp%22&page=1)_

|

[2.200.000](https://www.zoomeye.org/searchResult?q=%2Bafter%3A%222019-01-01%22%20%2Bbefore%3A%222020-01-01%22%20%2Bservice%3A%22snmp%22)  
  
**BGP** ****

|

_[700.000](https://www.shodan.io/search?query=port%3A179+product%3A%22BGP%22)_

|

_[0](https://app.binaryedge.io/services/query?query=port:%22179%22%20protocol:%22udp%22&page=1)_

|

_[700.000](https://www.zoomeye.org/searchResult?q=%2Bafter%3A%222019-01-01%22%20%2Bbefore%3A%222020-01-01%22%20%2Bservice%3A%22bgp%22)_  
  
**Citrix Netscaler** ****

|

_[26](https://www.shodan.io/search?query=%22citrix+netscaler%22)_

|

[72.000](https://app.binaryedge.io/services/query?query=%22Citrix%20NetScaler%20httpd%22&page=1)

|

_[48.000](https://www.zoomeye.org/searchResult?q=%2Bafter%3A%222019-01-01%22%20%2Bbefore%3A%222020-01-01%22%20%2Bapp%3A%22Citrix%20NetScaler%20httpd%22)_  
  
**Cisco Port 22** ****

|

_[370.000](https://www.shodan.io/search?query=cisco+port%3A22)_

|

_[430.000](https://app.binaryedge.io/services/query?query=port:22%20cisco&page=1)_

|

[580.000](https://www.zoomeye.org/searchResult?q=port%3A22%20%2Bcisco%20%2Bafter%3A%222019-01-01%22%20%2Bbefore%3A%222020-01-01%222)  
  
对比图表显示如下：

![](https://images.seebug.org/content/images/2019/07/b8b3ca1f-daec-4135-a8d0-0de6b7943c3d.png-w331s)

如你所见：

  * BinaryEdge在UDP 服务上有盲点；

  * 与每个端口的“原始”结果相比，Shodan仍然提供了良好的结果。 

## 四、结论

BinaryEdge和ZoomEye完全可以和Shodan相媲美。这三种服务虽有细微差别，但都为OSINT提供了有价值的扩展。它们之间没有明显的输赢之分，每项服务都有其优缺点，我喜欢市场上存在竞争。

## 五、其他

还有一些服务我没有对它们作比较，原因如下：

  * Censys.io：一个不错的服务，但价格太高，限制太多。如果你想以一个合理的价格搜索和下载一个30万的搜索结果时，你不会选择使用它。

  * 在对OSINT进行全排名时，Hackertarget.com和Securitytrails.com也是非常有价值的工具，虽然它们提供了某些IP的结果，但是它们不能用于全网范围内的研究。

* * *

[1] – I speak mostly about data gathered by internet-wide scan

[2] – How old observed results might be (based on observation, not
measurements)

[3] The resultset for shodan-RDP is somewhat hidden, the tag for
Terminalserver/RDP-Server is missing in the products-section.

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/970/>

