## 前言

 **如果你有一台无线路由器，那你就得小心了。因为这台路由器可能到处都是安全漏洞，而这些漏洞很可能会让你的一切陷入安全风险之中。**

![页首配图](https://image.3001.net/images/20181023/1540230315_5bce0cab44f76.png!small)

美国消费者协会(ACI)的最新研究结果显示，由于无线路由器的固件更新问题（未能及时和正确地更新），美国的家庭和办公室中平均每六台无线路由器就有五台(83%的概率)存在安全漏洞，并会导致用户陷入网络攻击的风险之中。

ACI的研究人员在对来自14家不同设备制造商的186台SOHO(小型家用/办公)无线路由器(均为美国地区有售)进行了测试之后，得出了下面这些非常令人不安的测试结果。

报告中提到：“调查过程中的分析工具采用的是Insignary的Clarity扫描工具，我们的分析结果显示，在186台测试样本路由器中，有155台(83%)存在不同严重程度的固件安全漏洞，并有可能成为网络攻击的目标。”这份报告标题为《[物联网设备安全：你家的无线路由器到底有多安全？](http://www.theamericanconsumer.org/wp-content/uploads/2018/09/FINAL-Wi-Fi-Router-Vulnerabilities.pdf)》，而报告中也对总共发现的超过32000个已知安全漏洞进行了介绍，感兴趣的同学可以自行阅读了解。

这些安全漏洞不仅会影响路由器的安全，而且还会给犯罪分子进行进一步的恶意活动提供便利，因为攻击者一旦入侵了一台路由器，那目标网络内的其他设备也将受到牵连。其中，用户面临的安全风险包括个人信息泄露、身份信息识别和网络欺诈攻击等等。

当然了，这些漏洞的严重等级也都不同。根据[国家漏洞数据库](https://nvd.nist.gov/vuln-metrics/cvss)的评估等级（低危、中危、高危和严重），在所有检测到的路由器漏洞中有7%为严重漏洞，还有21%被评估为高危漏洞，中危漏洞大约占所有漏洞的60%。平均算下来，每一台路由器大约存在12个严重漏洞和36个高危漏洞。

![路由器](https://image.3001.net/images/20181023/1540230321_5bce0cb1596ff.png!small)

很多路由器现在也越来越依赖[开源代码库](https://www.welivesecurity.com/2018/05/18/open-source-code-vulnerabilities/)了，这也是导致路由器固件存在这么多安全漏洞的主要原因之一。除此之外，漏洞无法及时修复也和制造商跟用户有着一系列的关系。比如说，供应商推送安全更新不够及时，有的厂商甚至都不会推送更新。而且就算他们推送了，绝大部分的用户也不会去安装这些补丁。

很多用户可能会觉得，就算路由器有漏洞，也没那么要紧吧？您可别这样想，就在四个月前，有一款名叫[VPNFilter](https://www.welivesecurity.com/2018/06/07/vpnfilter-update-bad-news-routers/)的恶意软件就成功入侵了50多个国家的数百万台路由器。

而且在2016年10月21日，美国地区就出现了一系列的[分布式拒绝服务(DDoS)](https://www.welivesecurity.com/2016/10/24/10-things-know-october-21-iot-ddos-attacks/)攻击，并影响了美国大部分的互联网活动，而发动这一系列攻击的就是一个由家庭路由器组成的僵尸网络。

如果你想知道如何提升路由器的安全性，可以参考下面这两篇教程：【[教程一](https://www.welivesecurity.com/2017/10/26/secure-your-router-prevent-iot-threats/)】【[教程二](https://www.welivesecurity.com/2018/01/23/five-ways-router-configured-securely/)】

 ***参考来源：[welivesecurity](https://www.welivesecurity.com/2018/10/08/routers-firmware-flaws-leave-users-risk/?utm_source=feedburner&utm_medium=feed&utm_campaign=Feed%3A+eset%2Fblog+%28ESET+Blog%3A+We+Live+Security%29)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

