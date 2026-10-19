![26.jpg](https://image.3001.net/images/20181102/1541144443_5bdbff7ba91c6.jpg!small)  

**Mini_httpd组件存在(CVE-2018-18778)任意文件读取漏洞，并可能影响全球百万在线设备**

 **  
**

近日，天融信阿尔法实验室研究员发现了大量应用于IOT设备的Mini_httpd组件存在(CVE-2018-18778)任意文件读取漏洞，并可能影响全球百万在线设备。
Mini_httpd是一个小型Http服务器,占用系统资源较小，因此被广泛采用于IOT设备（比如路由器、摄像头等）,通过该漏洞，恶意攻击者可以读取设备上的任意文件，严重威胁设备的安全性。

Mini_httpd组件被大量设备厂商采用，通过网络探测搜索到采用Mini_httpd的组件设备数量达到惊人的1239248台，采用Mini_httpd的设备覆盖全球主要国家和地区，其中中国大陆达到10387台，数量最多的是台湾地区达到334590台。

漏洞原因是由于没有过滤Http包头的特定字段，导致可以构造访问系统文件的路径，从而导致可访问任意文件，攻击者可以利用该漏洞读取设备的任意文件，这将严重威胁采用Mini_httpd的设备的安全性。

详文阅读：

[http://blog.topsec.com.cn/ad_lab/cve-2018-18778原创漏洞安全通告/?from=timeline&isappinstalled=0](http://blog.topsec.com.cn/ad_lab/cve-2018-18778%E5%8E%9F%E5%88%9B%E6%BC%8F%E6%B4%9E%E5%AE%89%E5%85%A8%E9%80%9A%E5%91%8A/?from=timeline&isappinstalled=0)

  

 **漏洞预警 | BleedingBit蓝牙芯片远程代码执行漏洞**

 **  
**

安全研究人员最近公布了两个蓝牙芯片漏洞的漏洞细节，并将之命名为BleedingBit。这两个漏洞可以让攻击者实现远程代码执行，因为涉及到非常多的物联网设备，包括一些医学设备如胰岛素泵、心脏起搏器等，所以这两个漏洞的危害极其严重。

发现这两个蓝牙漏洞的是Armis的安全研究人员（去年曝出BlueBorne漏洞的安全公司），TI（德州仪器）生产的蓝牙芯片（BLE）存在漏洞，Cisco、Meraki、Aruba等公司的企业产品也在用这些芯片。

详文阅读：

[https://www.anquanke.com/post/id/163307?from=timeline&isappinstalled=0](https://www.anquanke.com/post/id/163307?from=timeline&isappinstalled=0)

  

 **CVE-2018-15454 Cisco ASA及FTD软件拒绝服务漏洞**

  

Cisco官方发布安全预警 多款运行Cisco Adaptive Security Appliance (ASA)和 Cisco Firepower
Threat Defense (FTD) 的设备受到影响。这两款软件均支持Session Initiation Protocol (SIP)。

而在(SIP)检查引擎中的漏洞受到未经身份验证的远程攻击导致受影响的设备重新启动或持续高CPU占用率，从而导致拒绝服务(DoS)

该漏洞是由于SIP流量处理不当造成的。攻击者可以通过高速率发送特定的SIP请求到受影响的设备来利用此漏洞。导致设备崩溃重启。

详文阅读：

<https://www.anquanke.com/post/id/163300>

  

 **震网病毒新变体疑似又袭击伊朗**  

 **  
**

周三，以色列晚报 Hadashot
报道称，伊朗“前几天证实称再次遭遇类似震网病毒的攻击，但该病毒更暴力、更先进也更复杂，它攻击了伊朗的基础设施和战略网络。”

上周日，伊朗最高领袖阿亚图拉·卡梅尼 (Ayatollah Ali Khamenei)
发表电视演讲表示，伊朗的民事防御措施应该能抗击利用新威胁开展的敌方渗透。

这款新变体的目的是实施蓄意破坏，它行踪隐秘而且使得它对离心机造成的损害就像是设备偶然失灵造成的。

详文阅读：

[http://codesafe.cn/index.php?r=news/detail&id=4539](http://codesafe.cn/index.php?r=news/detail&id=4539)

  

 **严重漏洞可劫持Telecrane起重机**

 **  
**

Telecrane的一款联网施工起重机存在一个漏洞，可以让网络攻击者拦截其通信并接管设备。

随着各行业学习利用联网的便利性助力提高生产力、准确率、运营优化，越来越多的设备对象被囊括在物联网之中，在Telecrane的案例中，F25系列使用互联网连接来帮助操作人员引导起重机活动。。从技术角度来看，Telecrane的缺陷(CVE-2018-17935)是指在两种硬件之间的传输机制中，通过捕获-重放来绕过认证，使起重机能够与驾驶员座舱中的控制器进行对话。

这些设备使用了可通过嗅探和重新传输复制的固定代码，利用这个漏洞可以让未经授权的用户查看命令、重放命令、控制设备或阻止设备运行。

详文阅读：

<https://www.hackeye.net/threatintelligence/17046.aspx>

  

