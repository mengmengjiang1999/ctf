**作者：T1tan**  
**本文首发于ZoomEye，原文链接：<https://mp.weixin.qq.com/s/uEcSVpCT4xWEEwPoJuvABg>**

### 1\. 什么是ZoomEye dork

ZoomEye
dork是ZoomEye资产测绘平台的查询语法加上特定关键词组成的语句，用来搜索挖掘ZoomEye平台数据进行消费，ZoomEye官网：<https://www.zoomeye.org/>
。

![](https://images.seebug.org/content/images/2021/07/701e4541-5555-44ea-a89d-1f1e98f78d67.png-w331s)

### 2\. ZoomEye dork使用场景

通过ZoomEye dork挖掘的数据可以使用在攻击与防守场景里面。

#### 2.1 攻击视角

开源情报OSINT  
攻防演练HVV（红队Red Team）  
漏洞预警到ZoomEye dork（统计和排查数据)攻击者获取情报  
提交漏洞到SRC  
等...

#### 2.2 防御视角

暗资产排查（未统计和排查到的资产）  
攻防演练HVV（蓝队Blue Team）  
漏洞预警到ZoomEye dork（统计和排查数据)防御者获取情报  
C&C（命令与控制服务器）排查如cobalt strike后渗透工具  
等...

### 3\. 一些场景下的ZoomEye dork语句

特定场景下的一些专题：<https://www.zoomeye.org/topics>,下面提供一些ZoomEye dork语句。

#### 3.1 摄像头

摄像头（CAMERA或WEBCAM）又称为电脑相机、电脑眼、电子眼等，是一种视频输入设备，被广泛的运用于视频会议、远程医疗及实时监控等方面。

![
](https://images.seebug.org/content/images/2021/07/204fa7fa-5740-4819-a038-a44c55d1592c.png-w331s)

[**app:"Cisco WVC54GCA webcam
rtspd"**](https://www.zoomeye.org/searchResult?q=app%3A "Cisco WVC54GCA webcam
rtspd")

Cisco WVC54GCA是一款无线网络摄像头，支持增强的 MPEG-4 和 MPEG 压缩，包括Cisco-Linksys等系列产品。

[**app:"Bosch DINION IP Bullet 5000 webcam http
admin"**](https://www.zoomeye.org/searchResult?q=app: "Bosch DINION IP Bullet
5000 webcam http admin")

博世是德国的工业企业之一，主要从事汽车、智能交通技术、工业技术、消费品和能源及建筑技术产业。

[**app:"Polycom ViewStation"**](https://www.zoomeye.org/searchResult?q=app:
"Polycom ViewStation")

宝利通主要致力于提供端到端语音、视频、数据和 Web 富媒体协作应用。应用范围从台式机和个人移动系统到会议室系统，再到网络中心。

[**app:"Linksys WVC54GC webcam
UPnP"**](https://www.zoomeye.org/searchResult?q=app%3A "Linksys WVC54GC webcam
UPnP")

Linksys WVC54GC webcam可在物体发生动态变化时会把截图发送到客户的邮箱里，拥有内置的网络服务器，不需要电脑即可工作。

[**app:"Samsung SNB-2000
webcamrtspd"**](https://www.zoomeye.org/searchResult?q=app%3A "Samsung
SNB-2000 webcam rtspd")

Samsung SNB-2000 webcam是一款枪式网络摄像机，支持日夜转换功能，网络兼容性十分丰富，拥有600线的水平清晰度。

#### 3.2 区块链

区块链是一个信息技术领域的术语。从本质上讲，它是一个共享数据库，存储于其中的数据或信息，具有“不可伪造”“全程留痕”“可以追溯”“公开透明”“集体维护”等特征。基于这些特征，区块链技术奠定了坚实的“信任”基础，创造了可靠的“合作”机制，具有广阔的运用前景。

![
](https://images.seebug.org/content/images/2021/07/90b601a2-46b1-4a73-a73e-306802c5a5bb.png-w331s)

[**app:"Bitcoin protocol"**](https://www.zoomeye.org/searchResult?q=app%3A
"Bitcoin protocol")

Bitcoin（比特币）网络节点，启动比特币客户端默认开启，每笔交易由发起方向周围的节点进行广播，节点收到之后再广播给自己周围的节点，分布式的节点会负责实时更新数据，广播和验证交易。

[**app:"XMR-Stak miner"**](https://www.zoomeye.org/searchResult?q=app%3A "XMR-Stak miner")

XMR-Stak 是一款开源的通用矿池系统，支持CPU和GPU来挖加密货币，且占用空间小，由最初的xmr-stak-cpu、xmr-stak-amd和xmr-stak-nvidia三款集成而来，支持64位的Windows、Linux和MacOS系统。

[**app:"Baikal Miner"**](https://www.zoomeye.org/searchResult?q=app%3A "Baikal
Miner")

Baikal Miner 是由Baikal团队开发的mini X11算法挖矿矿机，只需要4个芯片即可达到150MH/s，具有高算力低功耗的特点。

[**app:"Claymore Miner
ManagementPage"**](https://www.zoomeye.org/searchResult?q=app%3A "Claymore
Miner Management Page")

Claymore
Miner是一款专门用于以太坊的矿机,支持CPU和GPU进行挖矿，由于其特别的双挖模式而被矿工们大范围的使用，在支持N卡和A卡的同时,也能在Windows和Linux上流畅使用。

[**app:"antMiner"**](https://www.zoomeye.org/searchResult?q=app%3A "antMiner")

AntMiner
（蚂蚁矿机）系列矿机是由比特大陆发布的专门用于挖矿的设备，是全球市占率第一的加密货币挖矿机品牌，后来业务拓展至其他加密货币，如以太坊、达世币、莱特币、门罗币等等。

#### 3.3 WAF

Web应用防护系统（也称为：网站应用级入侵防御系统。英文：Web Application
Firewall，简称：WAF）。利用国际上公认的一种说法：Web应用防火墙是通过执行一系列针对HTTP/HTTPS的安全策略来专门为Web应用提供保护的一款产品。

![ ](https://images.seebug.org/content/images/2021/07/3a405bfb-ba75-4ad4-adc4-57154899affe.png-w331s)

[**app:"Fortinet FortiGuard Web FilteringService waf
httpd"**](https://www.zoomeye.org/searchResult?q=app%3A "Fortinet FortiGuard
Web Filtering Service waf httpd")

包含FortiGuard企业级系列防火墙，吞吐量最大可以达到1Gbps，具有高可用性，多个安全区等功能，是功能强大，多合一的网络安全解决方案。

[**app:"DCN WAF httpd"**](https://www.zoomeye.org/searchResult?q=app%3A "DCN
WAF httpd")

DNF WAF包括DCFW系列产品，使用业界领先的细粒度多核防护引擎，能够实时识别和防护多种针对WEB的应用层攻击。

[**app:"Safe3 WAF httpd"**](https://www.zoomeye.org/searchResult?q=app%3A
"Safe3 WAF httpd")

Safe3WAF是国内安全组织保护伞网络基于新一代Web安全技术开发的全方位企业Web信息安全产品，目前使用Safe3WAF网站用户有搜狐、国防科技大学招生网等

[**app:"YUNDUN WAF httpd"**](https://www.zoomeye.org/searchResult?q=app%3A
"YUNDUN WAF httpd")

YUNDUN WAF是基于大数据和AI技术打造的业务级Web应用防火墙，实时拦截各种漏洞，保护Web应用免遭网络、应用、业务等各种已知和未知威胁。

[**app:"YXLink WAF httpd"**](https://www.zoomeye.org/searchResult?q=app%3A
"YXLink WAF httpd")

YXLink
WAF能实现Web应用加速与防止敏感信息泄露的功能，检测引擎支持百万级别的并发连接、十万级别的每秒HTTP/HTTPS请求数，为Web应用提供较为全面的防护解决方案。

#### 3.4 打印机

打印机（Printer)
是计算机的输出设备之一，用于将计算机处理结果打印在相关介质上。衡量打印机好坏的指标有三项：打印分辨率，打印速度和噪声。打印机的种类很多，按打印元件对纸是否有击打动作，分击打式打印机与非击打式打印机。按打印字符结构，分全形字打印机和点阵字符打印机。按一行字在纸上形成的方式，分串式打印机与行式打印机。按所采用的技术，分柱形、球形、喷墨式、热敏式、激光式、静电式、磁式、发光二极管式等打印机。

![
](https://images.seebug.org/content/images/2021/07/adb18742-330e-4641-9e65-a108c360f3cf.png-w331s)

[**app:"Brother MFC-7360N
pop3d"**](https://www.zoomeye.org/searchResult?q=app%3A "Brother MFC-7360N
pop3d")

包含Brother MFC-7360N、Brother MFC-820CW等多种型号。具有印刷字迹清晰，反应快，使用性好，操作方便等特点。

[**app:"Star Micronics TSP828L
printerftpd"**](https://www.zoomeye.org/searchResult?q=app%3A "Star Micronics
TSP828L printer ftpd")

包含Star Micronics TSP828L、Star Micronics TSP143、Star Micronics TSP700等型号。

[**app:"Intermec 540+/542+ print
servertelnetd"**](https://www.zoomeye.org/searchResult?q=app%3A "Intermec
540%2B%2F542%2Bprint server telnetd")

包含Intermec 540+、Intermec 542+等型号。

[**app:"Avery-Dennison Monarch 7411 printserver
ftpd"**](https://www.zoomeye.org/searchResult?q=app%3A "Avery-Dennison Monarch
7411 print server ftpd")

包含Avery-Dennison Monarch 7411等型号

[**app:"Toshiba e-STUDIO 233copier/printer/fax http
config"**](https://www.zoomeye.org/searchResult?q=app%3A "Toshiba e-STUDIO 233
copier%2Fprinter%2Ffax http config")

包含Toshiba e-STUDIO 233、Toshiba e-STUDIO5500c等多种型号。具有墨点小,速度快,精度高等特点。

#### 3.5 网络存储

网络存储（Network Storage）是数据存储的一种方式，网络存储结构大致分为三种：直连式存储（DAS：Direct Attached
Storage）、网络附加存储（NAS：Network Attached Storage）和存储区域网（SAN：Storage Area
Network）。由于NAS对于普通消费者而言较为熟悉，所以一般网络存储都指NAS。

![
](https://images.seebug.org/content/images/2021/07/31e0a620-d4d0-44ff-94a2-c5428fc64337.png-w331s)

[**app:"WISEGIGA Smart
CloudStorage"**](https://www.zoomeye.org/searchResult?q=app%3A "WISEGIGA Smart
Cloud Storage")

包括WISEGIGA Smart Cloud Storage、UB-100系列、UB-400系列等。

[**app:"ZexaBox storage-misc
httpd"**](https://www.zoomeye.org/searchResult?q=app%3A "ZexaBox storage-misc
httpd")

ZexaBox个人云存储小工具可实现即插即用，加密存储等功能。

[**app:"TerraMaster NAS storage-mischttpd"**](https://www.zoomeye.org/searchResult?q=app%3A "TerraMaster NAS
storage-misc httpd")

针对客户不同需求，Terra
Master推出了不同系列存储产品，如双硬盘、四硬盘、八硬盘的DAS直连式存储系统，以及双盘位，四盘位和八盘位等NAS网络存储系统。

[**app:"EMC Celerra NAS device
smbd"**](https://www.zoomeye.org/searchResult?q=app%3A "EMC Celerra NAS device
smbd")

包括EMC Celerra
NAS，Celerra可以作为集成单元或NAS标头使用，可以添加到独立的EMC存储阵列中。它支持SMB，NFS，FTP，NDMP，TFTP和MPFS协议。

[**app:"Meridian Quantum Snap!
httpconfig"**](https://www.zoomeye.org/searchResult?q=app%3A "Meridian Quantum
Snap! http config")

Meridian Quantum Snap是一种网络连接存储计算机设备。

### 4\. 参考链接

<https://www.zoomeye.org/project?id=camera>

<https://www.zoomeye.org/project?id=blockchain>

<https://www.zoomeye.org/project?id=printer>

<https://www.zoomeye.org/project?id=waf>

<https://www.zoomeye.org/project?id=networkStorage>

<https://baike.baidu.com/item/%E6%91%84%E5%83%8F%E5%A4%B4/321263?fr=aladdin>

<https://baike.baidu.com/item/%E5%8C%BA%E5%9D%97%E9%93%BE/13465666?fr=aladdin>

<https://baike.baidu.com/item/WAF/3239498?fr=aladdin>

<https://baike.baidu.com/item/%E6%89%93%E5%8D%B0%E6%9C%BA/215563?fr=aladdin>

<https://baike.baidu.com/item/%E7%BD%91%E7%BB%9C%E5%AD%98%E5%82%A8/10510271?fr=aladdin>

# 5\. 扫码加入ZoomEye交流群：

![
](https://images.seebug.org/content/images/2021/07/c2bdcd9a-04a1-4a4f-9a93-3730651a67ba.jpg-w331s)

（群满后请添加管理员vx：team016，添加时请备注“ZoomEye”）

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1629/>

