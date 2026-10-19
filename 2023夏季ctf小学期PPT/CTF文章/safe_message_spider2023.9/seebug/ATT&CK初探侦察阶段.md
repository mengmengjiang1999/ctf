作者：FA1C0N@RPO-Official  
相关阅读：[《ATT&CK 初探 2 -- 资源开发利用阶段》](https://paper.seebug.org/1628/ "《ATT&CK 初探 2
-- 资源开发利用阶段》")

## 介绍

RPO是一个信息安全爱好者成立的小组，我们致力于找到有趣的东西。

## 前言

ATT&CK（Adversarial Tactics, Techniques, and Common Knowledge
）是一个攻击行为知识库和模型，主要应用于评估攻防能力覆盖、APT情报分析、威胁狩猎及攻击模拟等领域。从2013年MITRE首次提出这个概念，2015年ATT&CK框架正式发布。在2016年到2020年的一份Excel电子表格发展到如今的社区知识集合。简单的说ATT&CK就是一张表，红蓝双方按照表中的区块对企业设施展开对抗，从而发现安全的薄弱点。我们未来会不断更新整个框架的技术细节和利用/防御方式。

![image-20210506211206510](https://images.seebug.org/content/images/2021/05/08/1620457566000-image-20210506211206510.png-w331s)

## 正篇

### 侦察阶段（Reconnaissance）

#### 一 主动扫描 （Active scanning）

##### IP块扫描

攻击者可能会扫描IP的方式收集受害者网络信息。扫描的方式可以是简单的ping扫描到更细微的扫描，后者可能会通过服务器响应或其他网络组件显示主机软件/版本。为后续进一步利用打好了基础。

主动扫描可以用于在网络中收集资产信息，便于快速掌握开放到公网上的网络服务。

我们可以对受害者执行主动扫描以收集信息。

主动扫描是指通过网络流量探查受害者基础设施的扫描，与不涉及直接交互的其他形式的侦察相反。敌手可能会根据他们寻求收集的信息而执行不同形式的主动扫描。

###### 使用方式

Nmap，Masscan

由于自己扫描的话在不开启代理的情况下会暴漏个人IP，容易导致被ban
IP，或者溯源甚至被反控等风险。隐藏自己的方法除了代理以外还可以借助各大安全厂商的网络空间扫描引擎，比如ZoomEye，Shodan，Censys，FOFA等。

##### 漏洞扫描

攻击者可能会进一步扫描受害者以查找可以使用的漏洞。漏洞扫描通常检查目标主机/应用程序（例如：软件和版本）的配置是否存在攻击者可以利用的攻击点。一般的攻击者会通过老旧版本软件存在的漏洞趁虚而入。

这些扫描还可能包括更广泛的尝试来收集受害者主机信息，这些信息可用于识别更常见的可利用漏洞。漏洞扫描通常通过服务器上正在运行的软件版本，侦听端口或其他网络组件来收集正在运行的软件和版本号。

系统地枚举和检查可识别，可猜测和未知的内容位置，路径，文件名，参数，以发现可能存在安全漏洞的弱点和要点。漏洞扫描包括恶意扫描和授权漏洞扫描引擎的扫描

![image-20210424185550292](https://images.seebug.org/content/images/2021/05/08/1620457567000-image-20210424185550292.png-w331s)

###### 使用方式

主动漏洞扫描器：awvs，nessus，Appscan

被动漏洞扫描器：w13scan，xray

目前市面上大部分主流扫描器都被一些入侵检测软件记录了特征。直接暴露渗透时使用的软件也是有隐患的。在某次hvv过程中，笔者从流量中发现了大规模的icmp包，疑似探测行为，查看数据为十六进制，转字符串得“Pinging
from Delphi code written by F.
Piette”，将此字符串进行搜索比较发现此段字符串出现自XX扫描器或其简单变种，若将此特征写入入侵检测软件，那么每次触发特征值都能捕捉到类似XX扫描器或其变种的攻击从而进行预警甚至阻断。

从攻击方的角度可以通过更换扫描器特征的方式绕过入侵检测系统，或者使用更加小众的扫描器亦或者自己去编写一个扫描器。

Tips：根据目标主机对应的端口响应来做出相应判断，最好扫描速度可控，大规模接收到来自同一ip的icmp这种事并不常见，一旦出现十有八九是探测扫描甚至更恶劣的行为。

###### 防守方缓解措施

可通过减少暴露面来缓解

关注可能表示扫描的可疑网络流量，例如来自单个源的大量流量。分析Web数据也可能会发现可归因于潜在恶意活动的对象。

#### 二 收集受害者主机信息 （Gather Victim Host Information）

这一个模块中，attack矩阵给出了四个子技术，分别是硬件，软件，固件和客户端信息，并给出提示通过扫描探测，网络钓鱼或者社工（比如寻找一些该公司泄露出的购物发票等信息）的方式去获取这四种信息。

攻击者可以通过各种方式收集此信息，例如通过主动扫描（例如：主机名，服务器标语，用户代理字符串）或
网络钓鱼诱骗直接收集信息。攻击者还可能直接破坏站点，然后收集访问者主机信息。有关硬件基础结构的信息也可能通过在线或其他可访问的数据集（例如：招聘网站，网络地图，评估报告，简历或发票）暴露给攻击者。

##### 硬件

这些信息包含各种详细信息，例如特定主机上的类型和版本，以及其他可能存在的防御保护组件（例如：卡/生物识别器，专用加密硬件等）。

##### 软件

这些信息包含各种详细信息，例如特定主机上的类型和版本，以及其他可能存在的防御保护组件（例如，杀毒软件，SIEM等）。

##### 固件

这些信息包含各种详细信息，例如特定主机上的类型和版本，这些信息可用于推断有关环境中主机的更多信息（例如：配置，用途，使用期限/补丁程序级别等）。

##### 客户端信息

这些信息包含各种详细信息，包括操作系统/版本，虚拟化，体系结构（例如32位或64位），语言和/或时区。

###### 使用方式

通过受害者的招聘信息可能会获取到技术栈和使用软件等信息。

<https://met.red/> 是一个支持高精度的ip定位网站

###### 防守方缓解措施

在最大程度地减少可提供给外部各方的数据数量和敏感性。公布一些数据时一定要脱敏。

这里提到了水坑攻击，水坑攻击指的是预先掌握受害者活动的规律，在其经常访问的容易被攻破的网站上先行写入攻击代码，攻击代码利用浏览器的缺陷，当受害者访问网站时终端会被植入恶意程序或者直接被盗取相关信息。这里提到的一种框架是scanbox，其可通过加载不同的功能来获取不同受害者主机的信息。

#### 三 收集受害者身份信息（Gather Victim Identity Information）

有关身份的信息包括各种详细信息，包括个人数据（例如：员工姓名，电子邮件地址等）以及诸如凭据之类的敏感信息。

防守方缓解措施：减少可提供给外部各方的数据的数量和敏感性。

##### 凭据

收集受害者的凭据可以通过多种方式，社工，转储泄露以及网络钓鱼等。这里提到了水坑攻击，github泄露，以及其他的泄露问题。大多数人的凭据是很少更换或者相互接近的，对比凭据特征做出的字典想必可以在一定的范围内发挥巨大的作用。

github泄露是非常致命的，开发人员可能在一些时候将凭据或者关键的信息写入自己的文件中，再将这些文件传储到github。

###### 使用方式

<https://www.jisec.com/sec/528.html>

<https://github.com/VKSRC/Github-Monitor>

##### 电子邮箱

收集受害者使用的相关电子邮件地址。收集到的话建议使用之前我们做出来的具有针对性的字典进行一波碰撞，说不定有意外的惊喜，一旦拿到了电子邮箱的控制权，那么我们就可以根据找回密码轻松得到我们想要的信息。

###### 使用方式

<https://www.maltego.com>

maltego是一款信息收集工具，它可以通过IP，域名等方式搜集查询到网站注册人邮箱等其他相关信息。

##### 员工名称

收集员工名称也是信息收集的一环，有很多员工名称会被呈现在其业务相关的网站上。这些员工名称可以作为字典合成的一部分或者查找域名等信息的关键所在，也可用其来制造更加逼真的“诱饵”做网络钓鱼用。

使用方法

<https://github.com/m8r0wn/CrossLinked>

#### 四 收集受害者网络信息（Gather Victim Network Information）

收集有关受害者网络的信息。有关网络的信息可能包括各种详细信息，包括IP，域名以及有关其拓扑和操作的详细信息。

防守方缓解措施：在最大程度地减少可提供给外部各方的数据数量和敏感性。

##### 域属性

收集有关受害者网络域的信息。有关域及其属性的信息可能包括各种详细信息，包括受害者拥有的域以及姓名，注册商或者更直接可操作的信息，例如联系人，公司地址和名称服务器的相关信息。

whois查询可以查询到相关域名各类详细信息，比如域名，相关注册表域ID，registrar
whois服务器，更新日期，创建日期，注册服务商，域名归属者联系方式等信息。

###### 使用方式

[域名Whois查询 - 站长之家 (chinaz.com)](https://whois.chinaz.com/)

##### 域名解析

收集有关受害者DNS的信息。DNS信息可能包括各种详细信息，包括注册服务器以及目标子域，邮件服务器和其他主机的地址的记录。

与DNS查询的方式相反，被动DNS属于反向获取或查询DNS数据信息。这些数据信息不仅包含了当前的DNS数据，也包括了历史记录中的一些DNS数据映射。

###### 使用方式

<https://github.com/dnsdb/dnsdbq>

    
    
        $ ./dnsdbq -r farsightsecurity.com/A -l 1 
        ;; record times: 2013-09-25 15:37:03 .. 2015-04-01 06:17:25 (~1y ~187d)
        ;; count: 6350; bailiwick: farsightsecurity.com.
        farsightsecurity.com.  A  66.160.140.81

https://dnsdumpster.com/是个在线查询DNS的网站，它能显示出域名服务商所在地，MX记录，TXT记录及A记录，也能绘制出映射域的图像

![image-20210426195659413](https://images.seebug.org/content/images/2021/05/08/1620457568000-image-20210426195659413.png-w331s)

<https://dns.bufferover.run/dns?q=> 是一个在线查询子域名的网站。

<https://github.com/knownsec/ksubdomain> 是一款基于无状态子域名爆破工具。

##### 网络可信依赖

有关网络信任的信息可能包括各种详细信息，包括已连接（并可能提升了）网络访问权限的第二或第三方组织/域

这里提到的是AD林，可以拓展到AD林根域，子域，域树等关系。域(Domain)是Windows网络中独立运行的单位，域之间相互访问则需要建立信任关系。信任关系是连接在域与域之间的桥梁。这里提到一款工具，mimikatz，这款工具可以获得AD相关的信息（域管理员登录留下的记录，黄金、白银票据）。

##### 网络拓扑

关于网络拓扑的信息可以包括各种细节，包括面向外部和内部网络环境的物理、逻辑布局。此信息可能还包括有关网络设备（网关，路由器等）和其他基础结构的详细信息。

网络拓扑的获取是存在一些难度的，但是通过有效的社工，还是有可能获得目标的网络拓扑。

提到网络拓扑，如果您已经进入到某一个内部网络，想要获取取得权限或者相关网络拓扑时，那么您一定会回忆起一款工具——BloodHound，它不仅能让您看到相关网络关系，还可以选择最佳攻击路线和最简获得域控的步骤。

##### IP地址

收集受害者的IP地址。公用IP地址可以按一定顺序分配给组织。有关分配的IP地址信息可能包括各种详细信息，例如正在使用的IP地址。IP地址还可以使攻击者获得有关受害者的其他详细信息，例如组织规模，地理位置，Internet服务提供商，以及在何处。

可以通过域名直接寻找IP地址（ping
域名）也可以使用whois查询和DNS查询，通过whois查询和DNS查询可以获取相关IP，获取IP后就可以进行一系列的扫描探测行为。

##### 网络安全设备

收集有关目标受害者网络安全设备的信息。有关网络安全设备的信息可能包括各种详细信息，例如已部署的防火墙，IPS，IDS，EDR，堡垒机等的存在和详细信息。攻击者还可能针对有关基于受害者的网络入侵检测系统（NIDS）或其他与防御性网络安全操作有关的设备的信息。

###### 使用方式

waf00f等一系列扫描器识别受害者相关网络所使用的安全设备（软/硬）。

#### 五 收集受害者组织信息（Gather Victim Org Information）

收集有关受害者组织的信息。有关组织的信息可能包括各种详细信息，包括部门/部门的名称，业务运营的详细信息以及关键员工的角色和职责。

防守方缓解措施：在最大程度地减少可提供给外部各方的数据数量和敏感性。

##### 确定物理位置

受害者相关的物理位置的信息可能包括各种详细信息，包括关键资源和基础架构的存放位置。实际位置还可以显示受害者在哪个具体的位置工作（辖区/机构）。

可使用的方式有很多，比如IP定位，钓鱼，社工等一系列方式。

我们可以通过其社交媒体来确定位置，比如图片没有进行处理就上传，存在地理位置信息，又或者可以根据图片推导出拍照位置。

当然，确定物理位置时，可以先通过微步查看其IP性质（基站？住宅？等等），在某次活动中，笔者经常会受到来自恶意IP的攻击，但是每次想要溯源时候常常会发现很多都是一些基站或者不固定IP，这种溯源从某种角度来说是比较困难的。

站长工具和一些网站（<https://www.xj.hk/hack/>）均可提供IP查询。

在得知公司信息时，可以在招聘软件上寻找相关公司在各地的办事处地址，层层深挖会得到更多的信息。

##### 业务关系

收集有关受害者的业务关系信息。有关组织业务关系的信息可能包括各种详细信息，包括网络访问权限的组织（比如委托第三方对业务进行完善的服务提供商或相关业务的承包商，在一家公司里，这些组织、域往往通过VPN，堡垒机进行运维，当然也存在实地运维的可能性），同时可能包括一些收购的子公司，通过域的信任去连接受害者所处的域，从而进行运维或获取公司内部的信息和服务。当然，此信息还可能揭示受害者的硬件和软件资源的供应相关信息。相关业务关系可以去查找其企业历年来的投标招标信息，相信你会有意外的收获，也可以通过天眼查（<https://www.tianyancha.com/>）等网站去查找公司相关业务关系。

##### 确定业务周期

收集有关受害者的业务节奏的信息，这些信息可在目标确定期间使用。有关组织业务节奏的信息可能包括各种细节，包括每周的工作时间/天。此信息还可能显示受害者的硬件和软件资源的购买和运输时间/日期。

在得知受害者相关单位和岗位时，可以通过社工，钓鱼的方式去深入了解业务和工作周期（可以通过招聘软件去联系HR获得相关业务职位的具体信息，包括胜任该岗位需要的技能与工作时间安排等）。笔者当时应聘在面试中一般都会和HR聊到业务周期等相关信息。

##### 确定角色

收集有关受害者组织内的身份和角色的信息。这些信息可能会揭示各种细节，包括关键人员的可识别信息以及他们在机构内的访问权限。

受害者身份鉴别可以是通过社交媒体获得的，如果受害者在其单位表现优秀并且该单位经常性表彰优秀员工并编写文章，发表在相关单位的官网上，那么该受害者的身份就暴露在了internet中。

#### 六 信息网络钓鱼 （Phishing for Information）

##### 鱼叉式钓鱼服务 Spearphishing Service

鱼叉式钓鱼钓鱼服务是针对特定个人，公司或行业的社会工程学。攻击者通过虚假的网络社交账号与受害者建立联系，从而更容易的刺探内部信息和服务。甚至是诱使受害者点开恶意链接或附件。

##### 鱼叉式钓鱼攻击 Spearphishing Attachment

攻击者通过将文件附加到鱼叉式钓鱼邮件中，通常需要诱导用户打开才能执行其内的恶意程序。

附件有很多选项，如Microsoft
Office文档，可执行文件，PDF，压缩文件等。攻击者会在电子邮件中给出一个合适的理由，文件为什么应该打开，并可能解释如何绕过系统保护，从而让附件中的攻击载荷在用户的系统中执行。

###### 使用方式

通过cs的Attacks -> Package -> MS Office
Macro可以快速生成一份宏病毒代码，然后粘贴到word的->视图->查看宏->创建宏里就好了（不过会被杀软直接干掉，后面我们会细说如何过杀软）。

##### 鱼叉式钓鱼链接 Spearphishing Link

攻击者通过发送带有恶意链接的鱼叉式电子邮件，试图访问受害者系统。这种攻击使用电子邮件中的链接下载恶意软件，而不是将恶意文件附加到电子邮件，从而避免电子邮件检查的防御。

该攻击会暗示或者要求受害者去点击邮件中的链接，受害者访问这个链接可能会通过浏览器漏洞获得权限（如前段时间的chrome
0Day），或者转到鱼叉式钓鱼攻击让受害者下载应用程序，文档，压缩包等，亦或者模仿受害者常用的网站做一个虚假的界面欺骗用户提供账号，密码，PIN或者其他隐秘信息。

#### 七 搜索闭源 （Search Closed Sources ）

在开始攻击之前攻击者可能会从闭源收集受害者的信息。这些信息可能可以从信誉良好的私有资源或数据库购买到，比如付费的技术/威胁情报。攻击者也可以从信誉较差的比如暗网或者网络黑市（比如telegram或者黑产群等）购买信息。

攻击者可能会根据寻求的信息从不同的闭源对其搜索。从这些闭源查询到的信息很可能会让攻击者发现 **侦察阶段**
的其他攻击面（比如钓鱼攻击或者开放的网站或者域名）建立的业务资源（比如开发能力或者获得能力），初始权限（比如远程服务访问，可用账户）。

###### 使用方式

<https://x.threatbook.cn/>微步威胁情报社区

#### 八 搜索开放式技术数据库 （Search Open Technical Databases ）

攻击者可以通过搜索免费的技术数据库，以搜集可以用在攻击阶段的信息，比如域/证书的注册信息，从流量/扫描中收集的网络数据/产品的集合。

这些信息可能让攻击者发现侦查阶段的其他攻击面，比如钓鱼或开放的网站/域，资产信息，初始权限。

###### 使用方式

DNS/WHOIS/数字证书/CDN/网络空间扫描器/查询

[DNSdumpster.com - dns recon and research, find and lookup dns
records](https://dnsdumpster.com/)

<https://www.circl.lu/services/passive-dns/>

[Whois Lookup & IP | Whois.net](https://www.whois.net/)

[域名Whois查询 - 站长之家 (chinaz.com)](https://whois.chinaz.com/)

<https://www.sslshopper.com/ssl-checker.html>

<https://www.zoomeye.org/>

<https://fofa.so/>

#### 九 搜索开放网站/域名（Search Open Websites/Domains）

攻击者可以通过搜索查找有关受害者的可用的网站/域名。这些信息可以通过各种线上网站获得，例如社交媒体，新网站，或者托管有关企业的运行信息（例如，雇佣，请求，奖励的合同）网站。

##### 社交媒体

攻击者可以通过社交媒体中企业员工/实习生/新员工在社交媒体的视频/图片/文字中获得企业的相关信息，比如企业办公室布局，电脑桌面程序，徽章图片，公开在白板上的信息/密码等，从而使攻击者更好的进行钓鱼攻击或者直接获得初始账号，收集业务资源等。

##### 搜索引擎

攻击者可以通过google/百度语法搜索特定的关键词或特定文件类型，其实也就是我们常说的google黑客。

###### 使用方式

[Google Hacking Database (GHDB) - Google Dorks, OSINT, Recon (exploit-db.com)](https://www.exploit-db.com/google-hacking-database)

[Exploring Google Hacking Techniques - Top Google Dorks
(securitytrails.com)](https://securitytrails.com/blog/google-hacking-techniques)

[高级搜索 (baidu.com)](https://www.baidu.com/gaoji/advanced.html)

#### 十 搜索受害者拥有的网站 （Search Victim-Owned Websites）

攻击者可以搜索数据受害者的网站，这些网站可能会包含多种信息，比如部门名称，物理位置，关键员工的相关数据（姓名，职务，联系方式等）。这些网站可能还会包含关键业务运作和商业关系的细节。

## Refer

[Updates - Updates - July 2016 | MITRE
ATT&CK?](https://attack.mitre.org/resources/updates/updates-july-2016/index.html)

[Matrix - Enterprise | MITRE
ATT&CK?](https://attack.mitre.org/matrices/enterprise/)

<https://wiki.owasp.org/index.php/OAT-014_Vulnerability_Scanning>

<https://www.freebuf.com/articles/others-articles/250028.html>

<https://www.aqniu.com/vendor/72973.html>

<https://plcscan.org/blog/2020/04/research-report-of-renowned-internet-census-organization-1/>

[https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MjM5NDQ5NjM5NQ==&action=getalbum&album_id=1481755277342326786&scene=173&from_msgid=2651626102&from_itemidx=1&count=3&nolastread=1#wechat_redirect](https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MjM5NDQ5NjM5NQ==&action=getalbum&album_id=1481755277342326786&scene=173&from_msgid=2651626102&from_itemidx=1&count=3&nolastread=1#wechat_redirect)

<https://attack.mitre.org/techniques/T1595/002/>

<https://bbs.csdn.net/topics/100128165>

<https://cybersecurity.att.com/blogs/labs-research/scanbox-a-reconnaissance-framework-used-on-watering-hole-attacks>

<https://www.freebuf.com/articles/network/261703.html>

[首页 - 微步在线威胁情报社区 (threatbook.cn)](https://x.threatbook.cn/)

[What is Spear-phishing? Defining and Differentiating Spear-phishing from
Phishing | Digital Guardian](https://digitalguardian.com/blog/what-is-spear-phishing-defining-and-differentiating-spear-phishing-and-phishing)

[一个“特别”的Word宏病毒深度分析 -FreeBuf网络安全行业门户](https://www.freebuf.com/articles/system/103309.html)

[office宏攻击 - Leticia's Blog
(uuzdaisuki.com)](https://uuzdaisuki.com/2020/08/20/office宏攻击/)

[https://blog.csdn.net/shuteer_xu/article/details/107031951?utm_medium=distribute.pc_relevant.none-task-blog-2%7Edefault%7EBlogCommendFromMachineLearnPai2%7Edefault-3.control&dist_request_id=&depth_1-utm_source=distribute.pc_relevant.none-task-blog-2%7Edefault%7EBlogCommendFromMachineLearnPai2%7Edefault-3.control](https://blog.csdn.net/shuteer_xu/article/details/107031951?utm_medium=distribute.pc_relevant.none-task-blog-2%7Edefault%7EBlogCommendFromMachineLearnPai2%7Edefault-3.control&dist_request_id=&depth_1-utm_source=distribute.pc_relevant.none-task-blog-2%7Edefault%7EBlogCommendFromMachineLearnPai2%7Edefault-3.control)

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1583/>

