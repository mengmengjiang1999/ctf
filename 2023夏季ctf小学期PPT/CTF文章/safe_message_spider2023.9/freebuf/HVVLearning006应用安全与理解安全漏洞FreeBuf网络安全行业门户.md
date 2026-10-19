# #16 HVV-Learning-006-应用安全与理解安全漏洞

## 目录

  * [目录]()
  * [1、应用安全]()
    * [1.1、对齐语义-应用是什么]()
    * [1.2、什么是应用安全]()
  * [2、应用安全->安全漏洞]()
    * [2.1、初步理解安全漏洞]()
    * [2.2、LBCB-泄漏、绕过、控制、破坏]()
    * [2.3、进一步理解漏洞-贯穿逻辑和技术、拉通效果和手段]()
    * [永恒之蓝]()
    * [Zabbix SSO绕过]()

## 0、前言

以前也时不时会在freebuf上看文章，但是一直没发过。忽然发现freebuf可以自由投稿。先把以前在 **同名公众号（非典型产品经理笔记）**
上写的原创内容，挑一部分发一下。

后续新内容会考虑同步在freebuf上发送。

 **本系列当前共14篇** 。

## 1、应用安全

在 [[HVV-Learning-005-互联网边界防护-不同业务类型及其发布方式](https://mp.weixin.qq.com/s?__biz=Mzg5MDU2MzM2Mw==&amp;mid=2247484044&amp;idx=1&amp;sn=b042c2b5140d67457a0153c074d71a4d&amp;chksm=cfdbfcc0f8ac75d6c87cac87a15cee15a4e3bbe22314740f4b34ef1c9e9fca3828782f30763a&token=575037478&lang=zh_CN#rd)]
我们了解了互联网发布（暴露)的业务类型，及其不同发布模式。接下来我们需要理解 **应用暴露** 所带来的安全问题。

### 1.1、对齐语义-应用是什么

本文中所指 **应用**
，和前文[[](https://mp.weixin.qq.com/s?__biz=Mzg5MDU2MzM2Mw==&amp;mid=2247484044&amp;idx=1&amp;sn=b042c2b5140d67457a0153c074d71a4d&amp;chksm=cfdbfcc0f8ac75d6c87cac87a15cee15a4e3bbe22314740f4b34ef1c9e9fca3828782f30763a&token=575037478&lang=zh_CN#rd)[HVV-Learning-005-互联网边界防护-不同业务类型及其发布方式](https://mp.weixin.qq.com/s?__biz=Mzg5MDU2MzM2Mw==&amp;mid=2247484044&amp;idx=1&amp;sn=b042c2b5140d67457a0153c074d71a4d&amp;chksm=cfdbfcc0f8ac75d6c87cac87a15cee15a4e3bbe22314740f4b34ef1c9e9fca3828782f30763a&token=575037478&lang=zh_CN#rd)[]
](https://mp.weixin.qq.com/s?__biz=Mzg5MDU2MzM2Mw==&amp;mid=2247484044&amp;idx=1&amp;sn=b042c2b5140d67457a0153c074d71a4d&amp;chksm=cfdbfcc0f8ac75d6c87cac87a15cee15a4e3bbe22314740f4b34ef1c9e9fca3828782f30763a&token=575037478&lang=zh_CN#rd)中的
**业务** 、 **业务系统** 为同一含义，其包含了 **WEB应用、
CS应用、APP应用，既包括了邮箱、OA等后台办公类业务，也包括门户、商城等前台业务。它包含了SSH、RDP此类运维应用/业务** ，也
**包括组网设备暴露的ipsec服务、VPN/SDP提供的接入认证服务** 这类稍有特殊的应用。

值得注意的是， **从技术角度，本文所指应用，均指有对外开放端口、以网络协议形式对外提供服务** 的应用。
**单机应用、或非网络协议应用（如通过物理串并口通信的老旧、特殊应用）** 因其特殊性，不在本文讨论范畴。

### 1.2、什么是应用安全

维基百科中有关于应用安全、web应用安全的描述，我们先看一下：

 **应用安全(Application Security):**
包括向开发团队引入安全软件开发生命周期[1]的所有任务。其最终目标是改进安全实践，并通过此来查找，修复并最好防止应用程序中的安全问题。它涵盖了从需求分析、设计、实施、验证到维护的整个应用程序生命周期。

 **WEB应用安全(WEB Application Security)**
：是信息安全的[2]一个分支，专门处理网站[3]，Web应用程序[4]和Web服务的安全性[5]。在较高层面上，Web应用程序安全性借鉴了应用程序安全的原则，但将它们专门应用于Internet[6]和Web[7]系统。

看完上述wiki定义后，如果是之前没有了解过 **应用安全** 的读者，估计心理活动是这样的:

![](https://image.3001.net/images/20221224/1671811218_63a5d092de7b65c056227.png!small)

![](https://image.3001.net/images/20221224/1671811221_63a5d0950cca0c414c31f.png!small)

为了方便理解，我们先用简单的话语，先定义一下应用安全。

1)、 **应用安全** (定义1）：是指保障 **应用** 不被恶意攻击、利用的 **防护能力** ，这个防护能力可以 **来自于应用自身**
、也可以来自于加入的防护组件（如IPS/WAF、HIDS、RASP均能在一定程度提升应用安全性)。

显然，相比外挂的安全防护措施，更优的情况下是应用自身经得起考验，能从应用开发、运行、维护的全生命周期提供充分的安全性。

 **问题来了：** 此时，再问一些过往不了解应用安全的读者，请问你现在能正确理解 **应用安全** 了吗？

针对多数人的严谨回答如下：

 **概念上能理解** ，大致知道应用安全是一种安全防护能力。

但是在逻辑上、结构上，还是 **很难深入进去理解清楚应用安全** 。

怎么办？如果不能很好理解一个事物，其中一个可能可行的方法，是 **从事物的反面** 去理解。

 **应用安全的反面是什么**?和应用安全对应的，语文角度当然是 **应用"不"安全** ，也就是 **应用安全风险、应用安全漏洞** 。

2)、 **应用安全(定义2)： 是指有较为充分的安全机制、安全过程对应用进行安全保障，使攻击者很难(不能100%）找到可供利用的安全漏洞** 。
简单的说，如果 **没有安全漏洞，应用就安全。**

注：当然安全无绝对，也不能100%没有漏洞，但凡是人写的代码，就有可能存在漏洞，只是其严重程度、隐蔽与否的差异。

## 2、应用安全->安全漏洞

### 2.1、初步理解安全漏洞

上面提到， **应用安全和安全漏洞** 是应用的 **一体两面** ，理解了安全漏洞，就能理解应用安全。

再从https://zh.[wiki](https://zh.wiki)敏pedia感.org/wiki/漏洞[8]尝试理解一下漏洞：

 **漏洞** \\[1\\][9]或 **脆弱性**
\\[2\\][10]（Vulnerability），是指计算机系统[11]安全方面的缺陷，使得系统或其应用数据的保密性[12]、完整性[13]、可用性[14]、访问控制[15]等面临威胁。在《GB/T
25069-2010 信息安全技术 术语》，将脆弱性定义为“资产中能被威胁所利用的弱点”

#### 2.1.1、从技术视角尝试理解漏洞

 **开源非赢利组织OWASP(Open Web Application Security Project）**
，专门针对web应用安全，旨在推动安全标准、安全测试工具、安全指导手册等应用安全技术的发展。

OWASP每年还会推出 **web应用安全的10大安全风险** ( **见：**
**https://owasp.org/Top10/zh\\_CN/**[16]**)**，总结了Web应用程序最可能、最常见、最危险的十大漏洞，以提升业界安全认识和安全能力。下为OWASP
TOP 10-2021的名单：

![](https://image.3001.net/images/20221224/1671811222_63a5d0961b94e71044540.png!small)

对于 **非技术侧读者** 来说，上面有一部分能理解，有一部分可能就有点抓瞎了，比如说" **注入式攻击** "是啥？

如果说上面的内容， **非技术侧读者** 还可以勉强连蒙带猜，还可以搜索" **常见安全漏洞** "等，技术视角的画风大概是这样的：

![](https://image.3001.net/images/20221224/1671811223_63a5d0979b12afbfa0816.png!small)

哪尼？什么是 **SQL注入、什么是SQL盲注、XXE漏洞又是什么**?

![](https://image.3001.net/images/20221224/1671811224_63a5d098cc0a49cefe29f.png!small)

#### 2.1.2、从逻辑视角尝试理解漏洞

所以说，要能理解一个问题，最好不要一开始就深入到技术。 **概念、逻辑、技术** 是需要层层深入的。

从 **概念理解** 上，漏洞可以简单理解为一种应用可能被伤害的途径。

从逻辑上怎么理解？我们举例栗子。

有些读者虽然过往不了解应用安全，我们以大家耳熟能详的应用，比如说QQ、微信为例，当提到 **应用安全或应用不安全**
的时候，第一反应可能是**"账号丢了"、"手机丢了"** ，第二反应是，" **是不是QQ官方自己出了问题** "。

我们说， **小人国居民看大象** ，有很多个视角，
**看到粗壮的大腿，是大象(的一部分)，看到挥舞的象鼻，也是大象(的一部分)，虽然一次看不全，但是多个关键视角的组合，就能形成大象的全貌** 。

而上面QQ微信的栗子，就是我们理解应用安全、理解安全漏洞的关键视角之一。

从上面我们就可以总结一部分，漏洞至少会包含有两种。

 **主体相关** ：电脑丢了、账号丢了就是其典型。

 **客体相关** ：在主体未出问题（电脑不丢、账号不丢）的情况下，应用自身出的其他安全问题。

但是我们明显能发现，上面的理解维度太粗了，时间关系，此处不在啰嗦，这里直接 **给出一个逻辑层面的漏洞理解模型总结** （忽略推导过程）。

注： **这个理解模型，并非标准，只是其中一个可行的视角**
，小人国看大象，有N个视角，故各位读者也可以自行总结。如果有更标准、更优的，可以知会我，感激不尽。

如下图。从 **应用视角出发** ，用户访问应用的过程如下：

1)、 **应用通常由** 一个运行环境承载，该运行环境称为 **系统**
(System)，该系统有可能是Docker，有可能是虚拟机操作系统，也有可能是物理操作系统，甚至可能还有其他类型（如serverless，此处不展开），可简单理解为操作系统。

2)、针对 **(中)后台应用，** 多数都有认证授权，用户需要认证(Authentication)成功 **、并按授权(Authorization)**
正常访问应用。即使是前台应用，也有一部分是有认证授权的，如电子商城，用户只能看到自己的购买记录。

3)、用户访问应用的过程，通常会被 **审计(Audit)** 。

4)、应用通常 **都有数据** ，存放在 **运行环境** 之中（根据实现的不同，可以是数据库服务、也可以是磁盘文件、甚至内存）。

5)、应用（确切的说是网络类应用）， **都有对外暴露的端口（如8080、443、22、3389等），** 供用户访问其服务。

![](https://image.3001.net/images/20221224/1671811226_63a5d09a2bef4f940c2bf.png!small)

### 2.2、LBCB-泄漏、绕过、控制、破坏

从漏洞的 **效果维度** ，可以总结为 **泄漏(Leakage)、绕过(Bypass)、控制(Control)、破坏(Break)，可简称为LBCB**
。

 **泄漏(Leakage) - 泄漏认证凭证与数据:**
认证凭证是指能使攻击者登录的要素，如账号密码、证书文件等；而数据在此则指除认证凭证以外的内容。比如说可以对应 **ATT &CK框架**中的
**TA0006 Credential Access 凭证获取** 相关漏洞、 **目录遍历 、SQL拖库** 等漏洞，都在此列。

 **绕过(Bypass) - 绕过认证和授权:** 认证主要用于确认使用者是否是本人；授权则基于用户身份，给予一个权限清单。
绕过认证相关漏洞典型的技术方式有， **Spring Security身份认证绕过漏洞 (CVE-2022-22978)、CVE-2022-23131
Zabbix SSO认证绕过漏洞**
。打个形象的比方，就好比一栋房子有两扇门，一扇需要输入密码，一扇门需要插钥匙。结果输入密码的门，输入错的密码也能通过、或者有一个万能密码可以通过；插钥匙的门，插一根针进去也能开门。

注：如果对认证和授权想更多了解一些的，可以参考 **Auth-Learning** 系列。

 **控制(Control) - 控制应用与系统:**
通过获取到应用的特权（如管理员权限），或应用所运行外部系统（通常是服务器主机、docker容器等)的特权（如管理员权限、系统权限），既能够对系统进行进一步的窃取和破坏，也能够通过系统向其他应用、主机系统进行进一步的横向渗透。

 **破坏(Break) - 破坏可用性和审计：**
通过对目标应用的可用性进行破坏，使应用不能提供服务，如拒绝服务攻击。通过对目标应用的审计能力或审计信息进行破坏，一方面可以隐蔽攻击者自身，避免被发现异常，另一方面也可以使防守方无法追溯攻击者的操作，从而无法抓住攻击者。

### 2.3、进一步理解漏洞-贯穿逻辑和技术、拉通效果和手段

 **LBCB** 是在 **逻辑层和效果层** 对安全漏洞的理解，但是我们会发现，业界当前很多漏洞说明，都是偏技术侧的。所以为了能
**将沟通语言达成一致** ，让非技术侧安全人员也能更好理解漏洞，我们需要想办法将两者拉通，实现 **逻辑和技术、效果和手段** 的对应。

我们来举一个栗子。

#### 2.3.1、 MS17-010永恒之蓝漏洞

MS17-010由多个CVE漏洞组成，分别是CVE-2017-0143、0144、0145、0146、0147、0148。

先看下MS17-010的官方说明，通过基官方说明 https://docs.microsoft.com/en-us/security-updates/securitybulletins/2017/ms17-010[17]或者 MSRC上的CVE链接

https://msrc.microsoft.com/update-guide/vulnerability/CVE-2017-0143[18]，可以看到其说明如下：

 **远程执行代码漏洞** 存在于 Microsoft 服务器消息块 1.0 （SMBv1）
服务器处理某些请求的方式中。成功利用这些漏洞的攻击者可以获得在目标服务器上 **执行代码** 的能力。
若要利用此漏洞，在大多数情况下，未经身份验证的攻击者可以向目标 SMBv1 服务器发送特制数据包。

可以看到微软对该系列漏洞，其中5个，使用了`Critical`严重的标注，并且说明是**远程代码执行(Remote Code Execution)**；
1个使用了Important重要，信息泄漏。

![](https://image.3001.net/images/20221224/1671811227_63a5d09b78027fe7e6587.png!small)

在上面可以看到，引入了“ **远程执行代码** ”的技术概念。同时，通过" **永恒之蓝 漏洞 CVE**
"为关键字进行检索，检索出一些信息，标题里又提到" **远程溢出漏洞** "

![](https://image.3001.net/images/20221224/1671811228_63a5d09c9474141bd6291.png!small)

继续通过" **永恒之蓝 漏洞影响"** 等关键字进行检索，可以看到有相关漏洞影响的说明，如下：

只要用户主机开机联网，即可通过该漏洞 **控制用户的主机。**

![](https://image.3001.net/images/20221224/1671811229_63a5d09de9ddf073c43e2.png!small)

经过上述总结，结合前面的LBCB，我们可以按如下方式理解该漏洞:

### 永恒之蓝

>  **漏洞名称** ：永恒之蓝，MS17-010， CVE-2017-0143（至0148）组合

>  **逻辑效果：控制(Control) - 控制应用与系统** \- 能通过该漏洞控制用户的主机，获取最高权限。

>  **逻辑手段** ：通过技术上的方式，能远程执行任意代码、命令，进而达到上述逻辑效果。

>  **技术效果** ： **远程代码执行** \- 可以远程执行代码、命令。

>  **技术手段：缓冲区溢出** — 技术侧因素，暂无需理解，后续有机会再单独分析。

通过区分逻辑和技术、区分效果和手段，有助于我们更好理解漏洞。

 **一句话总结** ：永恒之蓝漏洞，攻击者能够通过 **缓冲区溢出** 实现 **远程代码执行** ，从而能够在 **远程主机上执行任意代码** ，可获取
**受攻击主机的最高权限** ，实现 **控制(Control) - 控制系统** 。

如果再结合 **ATT &CK框架**（可参考 《 **HVV-Learning-003-浅析ATT &ck和Cyber Kill
Chain**》）进一步理解， **该漏洞至少有助于实行下述两个战术(执行命令、权限提升** ）：

1)、 **TA0002 Execution 命令执行** :尝试运行恶意代码，执行命令。

2)、 **TA0004 Priiege Escalation 权限提升** ：通过漏洞等方式来提升访问权限，如从普通用户权限提升至系统权限、管理员权限等。

![](https://image.3001.net/images/20221224/1671811231_63a5d09f900611b758509.png!small)

#### 2.3.2、列举一些常见的技术手段

{{标题党}}

{{为避免本文逻辑复杂度过高，取消本节}}

#### 2.3.3、再补充一个漏洞

 **Zabbix** （一个主流的运维监控系统，可以监控大量主机的健康运行情况），曾爆出一个认证绕过漏洞， **CVE-2022-23131**
，可见官网链接： https://support.zabbix.com/browse/ZBX-20350[19]

如下图，可以看到其信息如下:

 **危害级别** ：严重(Critical)。

 **描述** ：在启用了 SAML SSO 身份验证（非默认）的情况下，恶意执行组件可能会修改会话数据，因为未验证存储在会话中的用户登录名。

![](https://image.3001.net/images/20221224/1671811233_63a5d0a103a970d600bdb.png!small)

我们同样按上述方式分层来对漏洞进行逻辑和技术结合的理解。

### Zabbix SSO绕过

>  **漏洞名称** ：Zabbix SSO绕过漏洞， **CVE-2022-23131**

>  **逻辑效果：绕过(Bypass) - 绕过认证和授权** \- 能实现无需密码，即可登录任意已存在的用户。

>  **逻辑手段** ：通过技术手段 **伪造用户凭证** ，绕开认证校验。。

>  **技术效果** ：可以解密并伪造用户凭证。

>  **技术手段：** 解密本地session凭证并进行篡改（服务端缺乏有效校验）

注：技术侧读者可以到这里(
https://cloud.tencent.com/developer/article/2010001[20])看详细一些的攻击复现过程，攻击过程比较简单,很容易理解。

 **一句话总结** ：CVE-2022-23131，Zabbix SSO绕过漏洞，攻击者可以通过 **解密本地session凭证并进行篡改** 实现
**用户凭证伪造** ，从而 **绕开认证校验** ，进而 **实现无需密码、登录任意已存在的用户** ，实现 **绕过(Bypass) -绕过认证和授权** 。

#### 2.3.4、OpenSSL拒绝服务漏洞（CVE-2022-0778）

 **CVE-2022-0778** 是一个拒绝服务漏洞，属于 **破坏(Break) - 破坏可用性和审计** 中的破坏可用性。

针对此漏洞，在链接(
https://www.secrss.com/articles/40384[21])中有很多信息，还可以通过搜索引擎进行更多查询，建议自行结合LBCB尝试理解一下(熟手可忽略)。

### 参考资料

[1]

软件开发生命周期:
https://en.[wiki](https://zh.wiki)敏pedia感.org/wiki/Software_development_life_cycle

[2]

信息安全的: https://en.[wiki](https://zh.wiki)敏pedia感.org/wiki/Information_security

[3]

网站: https://en.[wiki](https://zh.wiki)敏pedia感.org/wiki/Website

[4]

Web应用程序: https://en.[wiki](https://zh.wiki)敏pedia感.org/wiki/Web_application

[5]

Web服务的安全性: https://en.[wiki](https://zh.wiki)敏pedia感.org/wiki/Web_service

[6]

Internet: https://en.[wiki](https://zh.wiki)敏pedia感.org/wiki/Internet

[7]

Web: https://en.[wiki](https://zh.wiki)敏pedia感.org/wiki/World_Wide_Web

[8]

https://zh.[wiki](https://zh.wiki)敏pedia感.org/wiki/漏洞:
https://zh.[wiki](https://zh.wiki)敏pedia感.org/wiki/漏洞

[9]

[1]: https://zh.[wiki](https://zh.wiki)敏pedia感.org/wiki/漏洞#cite_note-1

[10]

[2]: https://zh.[wiki](https://zh.wiki)敏pedia感.org/wiki/漏洞#cite_note-GBT25069-2

[11]

计算机系统: https://zh.[wiki](https://zh.wiki)敏pedia感.org/wiki/计算机系统

[12]

保密性: <https://zh.wiki>敏pedia感.org/wiki/保密性

[13]

完整性: https://zh.[wiki](https://zh.wiki)敏pedia感.org/wiki/完整性

[14]

可用性: https://zh.[wiki](https://zh.wiki)敏pedia感.org/wiki/可用性

[15]

访问控制: https://zh.[wiki](https://zh.wiki)敏pedia感.org/wiki/访问控制

[16]

https://owasp.org/Top10/zh_CN/: https://owasp.org/Top10/zh_CN/

[17]

https://docs.microsoft.com/en-us/security-updates/securitybulletins/2017/ms17-010: https://docs.microsoft.com/en-us/security-updates/securitybulletins/2017/ms17-010

[18]

https://msrc.microsoft.com/update-guide/vulnerability/CVE-2017-0143:
https://msrc.microsoft.com/update-guide/vulnerability/CVE-2017-0144

[19]

https://support.zabbix.com/browse/ZBX-20350:
https://support.zabbix.com/browse/ZBX-20350

[20]

https://cloud.tencent.com/developer/article/2010001:
https://cloud.tencent.com/developer/article/2010001

[21]

https://www.secrss.com/articles/40384: <https://www.secrss.com/articles/40384>

**相关：**

[#16 HVV-Learning-006-应用安全与理解安全漏洞](https://mp.weixin.qq.com/s?__biz=Mzg5MDU2MzM2Mw==&mid=2247484070&idx=1&sn=a919f6b23810a9dbde51054afbf462c4&chksm=cfdbfceaf8ac75fc797070c74ba5d8e7197b3ffb2927651b6545b467c5de95efb04bf2baedd9&scene=178&cur_album_id=2386722947383476224#rd)

[#13 HVV-Learning-004-区域边界网络下的攻击链路与攻击事件(BLA&UKC)](http://mp.weixin.qq.com/s?__biz=Mzg5MDU2MzM2Mw==&mid=2247484014&idx=1&sn=be675047f02cb6e1070b380674ca1399&chksm=cfdbfc22f8ac7534ea5a2d7457c0369fc394952f03a2a66a691688b16e2cafe2657cfdc3582c&scene=21#wechat_redirect)

[HVV-Learning-003-浅析ATT&CK和Cyber Kill
Chain](http://mp.weixin.qq.com/s?__biz=Mzg5MDU2MzM2Mw==&mid=2247483880&idx=1&sn=f3da6f0d7693b04b331c0dab44f1311b&chksm=cfdbffa4f8ac76b2c49c5ce8df01b410a6724b05bbc48b75c38dfec91439446944ec1226ef60&scene=21#wechat_redirect)

[#7 HVV-Learning-002-攻防演练的典型网络以及攻防现状(2021)](http://mp.weixin.qq.com/s?__biz=Mzg5MDU2MzM2Mw==&mid=2247483858&idx=1&sn=79b2fbdf7fa54ea723f3bc224c0858e5&chksm=cfdbff9ef8ac7688ca938ba324492204830a1abc57a208da0330f20d636cdcc5d4f14b26d1ab&scene=21#wechat_redirect)

[HVV-Learning-001-初步了解网络安全攻防演练﻿](http://mp.weixin.qq.com/s?__biz=Mzg5MDU2MzM2Mw==&mid=2247483850&idx=1&sn=83f9e282a657148565b1841656497ad4&chksm=cfdbff86f8ac769050a09c5cb98c7e80b269cdd2637777aa510e0c7e6a3a09afe30104d1aeb5&scene=21#wechat_redirect)

