![76.jpg](https://image.3001.net/images/20200628/1593332814_5ef8544e536e1.jpg!small)  

**Ripple20** **漏洞曝光：19个0 day漏洞影响数十亿IoT设备**

 **  
**

近日，美国国土安全局、CISA ICS-CERT发布了关于新发现的数十个安全漏洞的通告，称漏洞影响全球500余个厂商生产的数十亿联网设备。

这些漏洞是以色列网络安全公司JSOF 研究人员发现的，研究人员在Treck 开发的底层TCP/IP
软件库中发现了19个安全漏洞，研究人员将这些漏洞称之为——Ripple20。攻击者利用这些漏洞可以无需用户交互就实现对目标设备的完全控制。

 **受影响的产品和厂商**

受影响的设备包括家用和企业级商用设备，遍及不同行业，包括医疗健康、数据中心、电信、石油天然气、原子能、交通和其他关键基础设施领域。其中涉及部分财富500企业，比如HP、施耐德电气、Intel、罗克韦尔自动化、卡特彼勒、巴克斯特等。

详文阅读：

<https://blog.csdn.net/systemino/article/details/106838301>

**Netgear** **数十款路由器曝出严重漏洞，影响79种不同型号设备**

 **  
**

来自GRIMM的安全研究人员Adam Nichols和来自越南互联网服务提供商VNPT
的研究人员d4rkn3ss分析报告了一个影响Netgear路由器的严重的栈缓存溢出远程代码执行漏洞，漏洞CVSS
评分为8.8分，漏洞影响79种不同型号的Netgear路由器的758种固件版本，受影响的固件中最早的版本是2007年发布的。远程攻击者利用该漏洞可以以root权限执行代码，并接管设备。

详文阅读：

<https://www.4hou.com/posts/yMJR>

  

 **思科报告称：智能汽车易受黑客攻击 通过漏洞可实现“远程控制”**

 **  
**

近日据外媒报道，据思科客户体验评估和渗透团队(CX APT)表示， GNU Glibc设备中存在一个内存损坏漏洞使得智能车辆容易受到黑客攻击。

据悉，GNU libc内存损坏漏洞使得Linux
ARMv7系统容易被利用，这个漏洞被识别为TALOS-2020-1019/CVE-2020-6096。对暴露的联网车辆的安全威胁和网络攻击可能包括软件漏洞、基于硬件的攻击，甚至可能远程控制车辆。

同时，报告还指出，这些系统在通过移动网络、WiFI、蓝牙、DAB、USB连接的车辆上引入了大量“不同的攻击载体”。但Pen Test
Partners的安全专家安德鲁•蒂尔尼(Andrew
Tierney)表示，该漏洞的范围不仅限于车辆，还将涉及更广泛的物联网。Tierney还表示，这是一个新的漏洞，我们之前从未发现它。

详文阅读：

<https://www.easyaq.com/news/2147307840.shtml>

 ****

**Windows 10 Version 2004 新 BUG：重复报告安全警报**

  

近日 Version 2004 用户反馈，即使在 PUP 应用程序被清理之后，Windows Security 应用程序依然会触发警报。在 PUP
应用程序被移除或者允许在 Windows 10 上运行之后，Windows Security 在随后的扫描中依然会检测到旧项目，造成错误的检测循环。

一位用户指出：“我在进行常规扫描时，发现这些威胁被高亮显示为低级，而且 Defender 无法删除它们，导致一直显示。我同样使用了 Malwarebytes
进行扫描，但这边并没有显示出来。”

看来，Windows Defender 已经被默认为在Windows 10 Version 2004 中识别 PUP 为威胁。在 PUP
被删除后，Windows Defender 在随后的历史记录扫描中又将同一文件识别为威胁。

详文阅读：

<http://hackernews.cc/archives/31290>

**GuardMiner 挖矿木马近期活跃，具备蠕虫化主动攻击能力，已有较多企业中招**

  

腾讯安全威胁情报中心检测到跨平台挖矿木马GuardMiner近期十分活跃，该木马会扫描攻击Redis、Drupal、Hadoop、Spring、thinkphp、WebLogic、SQLServer、Elasticsearch多个服务器组件漏洞，并在攻陷的Windows和Linux系统中分别执行恶意脚本init.ps1，init.sh，恶意脚本会进一步下载门罗币挖矿木马、清除竞品挖矿木马并进行本地持久化运行。在Linux系统上利用SSH连接和Redis弱口令爆破进行内网扩散攻击。因挖矿守护进程使用文件名为sysguard、sysguerd、phpguard，腾讯安全威胁情报中心将该挖矿木马命名为GuardMiner。因该病毒已具备蠕虫化主动攻击扩散的能力，近期已有较多企业中招。

详文阅读：

<http://hackernews.cc/archives/31248>

