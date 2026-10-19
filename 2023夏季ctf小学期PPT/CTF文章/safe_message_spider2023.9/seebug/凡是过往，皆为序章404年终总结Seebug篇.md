2020年，Seebug漏洞平台的重心逐渐从漏洞平台转变为漏洞信息平台，将收录漏洞情报作为Seebug漏洞平台的主要重点，并推出了1day漏洞情报收录的功能，将Seebug从漏洞平台转变为漏洞集中收录、聚合信息的平台。

2020年，Seebug一共收录了935个漏洞，79个相关Poc；自上线以来，累计收录58231个漏洞，45269个Poc。

2020年，Seebug Paper一共发表了347篇文章，其中94篇为404实验室翻译组翻译的威胁情报，56篇为404实验室原创的安全技术文章。

在2021年的年初，我们一起来回顾一下2020年的那些漏洞和那些事。

## 一、2020年最受瞩目的漏洞top20

id | name | Seebug链接  
---|---|---  
1 | Weblogic 远程代码执行漏洞（CVE-2020-2883） |
<https://www.seebug.org/vuldb/ssvid-98212>  
2 | 深信服EDR 未授权 0Day RCE漏洞 | <https://www.seebug.org/vuldb/ssvid-98347>  
3 | 通达OA前台任意用户伪造登录漏洞 | <https://www.seebug.org/vuldb/ssvid-98218>  
4 | Citrix ADC&NetScaler远程命令执行漏洞(CVE-2019-19781) |
<https://www.seebug.org/vuldb/ssvid-98121>  
5 | Apache Tomcat session持久化远程代码执行漏洞(CVE-2020-9484) |
<https://www.seebug.org/vuldb/ssvid-98234>  
6 | Apache Dubbo反序列化漏洞(CVE-2020-1948) |
<https://www.seebug.org/vuldb/ssvid-98258>  
7 | WebLogic 未授权远程代码执行漏洞(CVE-2019-2725) |
<https://www.seebug.org/vuldb/ssvid-98117>  
8 | 通达OA 文件上传+文件包含导致RCE漏洞 | <https://www.seebug.org/vuldb/ssvid-98186>  
9 | Apache Tomcat Ajp协议文件包含漏洞 | <https://www.seebug.org/vuldb/ssvid-98134>  
10 | Gitlab CE/EE任意文件读取导致远程命令执行漏洞(CVE-2020-10977) |
<https://www.seebug.org/vuldb/ssvid-98287>  
11 | Fastjson<1.2.69反序列化远程代码执行漏洞 | <https://www.seebug.org/vuldb/ssvid-98236>  
12 | Spring Framework RFD漏洞(CVE-2020-5398) |
<https://www.seebug.org/vuldb/ssvid-98127>  
13 | Wordpress IMPress for IDX Broker 低权限xss漏洞 |
<https://www.seebug.org/vuldb/ssvid-98247>  
14 | Joomla 授权 RCE漏洞 （CVE-2020-11890 CVE-2020-10238 CVE-2020-10239） |
<https://www.seebug.org/vuldb/ssvid-98353>  
15 | 宝塔面板PhpmyAdmin未授权访问漏洞 | <https://www.seebug.org/vuldb/ssvid-98358>  
16 | ThinkCMF缓存Getshell漏洞 | <https://www.seebug.org/vuldb/ssvid-98223>  
17 | 万户网络技术有限公司ezEIP前台存在文件上传漏洞 | <https://www.seebug.org/vuldb/ssvid-98240>  
18 | ThinkPHP5 SQL注入漏洞 && 敏感信息泄露 | <https://www.seebug.org/vuldb/ssvid-98289>  
19 | Jira信息泄露（CVE-2019-8449）漏洞 | <https://www.seebug.org/vuldb/ssvid-98130>  
20 | 禅道前台Getshell | <https://www.seebug.org/vuldb/ssvid-98352>  
  
## 二、2020年最受关注的组件top10

name | 点击量  
---|---  
WeiPHP | 98919  
WebLogic | 76881  
Windows | 50521  
Tongda OA | 31745  
Microsoft SharePoint | 29740  
phpcms | 25280  
Apache Tomcat | 20385  
Microsoft Exchange | 20203  
Nexus | 18820  
Spring | 17682  
Zentao | 16258  
TP-LINK | 15667  
Shiro | 15474  
WebAccess/SCADA | 15446  
Pi-hole | 15135  
深信服 EDR | 14263  
Symmetricom SyncServer | 14035  
Advantech WebAccess HMI Designer | 14008  
Comtech Stampede FX | 13746  
Apache Dubbo | 13456  
  
## 三、2020年漏洞类型

![](https://images.seebug.org/content/images/2021/01/579fe2a7-1c76-426f-b034-691efdd0295f.png-w331s)

## 四、2020年兑换最多的Poc

ID | 漏洞名称 | Poc链接  
---|---|---  
1 | WebLogic 未授权远程代码执行漏洞(CVE-2019-2725) |
<https://www.seebug.org/vuldb/ssvid-98117>  
2 | Apache Dubbo反序列化漏洞(CVE-2020-1948) |
<https://www.seebug.org/vuldb/ssvid-98258>  
3 | D-link DIR-610 未授权RCE（CVE-2020-9376、CVE-2020-9377） |
<https://www.seebug.org/vuldb/ssvid-98346>  
4 | Citrix ADC&NetScaler远程命令执行漏洞(CVE-2019-19781) |
<https://www.seebug.org/vuldb/ssvid-98121>  
5 | Apache Tomcat Ajp协议文件包含漏洞 | <https://www.seebug.org/vuldb/ssvid-98134>  
6 | ThinkCMF缓存Getshell漏洞 | <https://www.seebug.org/vuldb/ssvid-98223>  
7 | Weblogic XMLDecoder反序列化代码执行（CVE-2019-2729） |
<https://www.seebug.org/vuldb/ssvid-98369>  
8 | Citrix ADC&NetScaler目录遍历漏洞 | <https://www.seebug.org/vuldb/ssvid-98120>  
9 | Adobe ColdFusion 任意文件读取（CVE-2020-3761)和任意文件包含(CVE-2020-3794)漏洞 |
<https://www.seebug.org/vuldb/ssvid-98190>  
10 | Nexus Repository Manager Groovy注入漏洞（CVE-2020-11753） |
<https://www.seebug.org/vuldb/ssvid-98224>  
  
## 五、2020年最受欢迎的paper

ID | 文章名称 | 作者 | 文章链接  
---|---|---|---  
1 | CSS-T Mysql Client 任意文件读取攻击链拓展 | 知道创宇404实验室 |
<https://paper.seebug.org/1112/>  
2 | Fastjson 反序列化漏洞史 | 知道创宇404实验室 | <https://paper.seebug.org/1192/>  
3 | ThinkPHP6 任意文件操作漏洞分析 | 启明星辰ADLab | <https://paper.seebug.org/1114/>  
4 | 这是一篇“不一样”的真实渗透测试案例分析文章 | 奇安信A-TEAM | <https://paper.seebug.org/1144/>  
5 | 聊聊区块链中的几个技术点 | 知道创宇404实验室 | <https://paper.seebug.org/1110/>  
6 | Shadowsocks 重定向攻击分析 | 数智安全研究院 | <https://paper.seebug.org/1134/>  
7 | Cobalt Strike 4.0 手册——献给渗透测试人员的先进威胁战术 | 奇安信A-TEAM |
<https://paper.seebug.org/1143/>  
8 | XSS 扫描器成长记 | 知道创宇404实验室 | <https://paper.seebug.org/1119/>  
9 | CVE-2020-0796 Windows SMBv3 LPE Exploit POC Analysis | 知道创宇404实验室 |
<https://paper.seebug.org/1165/>  
10 | pwn的艺术浅谈（二）：linux堆相关 | 天融信阿尔法实验室 | <https://paper.seebug.org/1109/>  
11 | CSS-T Mysql Client Arbitrary File Reading Attack Chain Extension |
知道创宇404实验室 | <https://paper.seebug.org/1113/>  
12 | 从 0 开始入门 Chrome Ext 安全（番外篇） -- ZoomEye Tools | 知道创宇404实验室 |
<https://paper.seebug.org/1115/>  
13 | Hessian 反序列化及相关利用链 | 知道创宇404实验室 | <https://paper.seebug.org/1131/>  
14 | APT 分析及 TTPs 提取 | PIanet | <https://paper.seebug.org/1132/>  
15 | CVE-2020-0796 Windows SMBv3 LPE Exploit POC 分析 | 知道创宇404实验室 |
<https://paper.seebug.org/1164/>  
16 | 渗透利器 Cobalt Strike 在野利用情况专题分析 | 启明星辰ADLab |
<https://paper.seebug.org/1190/>  
17 | pwn 的艺术浅谈（一）：linux 栈溢出 | 天融信阿尔法实验室 | <https://paper.seebug.org/1108/>  
18 | CVE-2019-19781 远程代码执行漏洞深入分析 | 天融信阿尔法实验室 |
<https://paper.seebug.org/1117/>  
19 | 从0开始聊聊自动化静态代码审计工具 | 知道创宇404实验室 | <https://paper.seebug.org/1339/>  
20 | Cobalt Strike 绕过流量审计 | Keyi | <https://paper.seebug.org/1349/>  
  
## 六、2020年最受欢迎的404原创文章

ID | 文章名称 | 文章链接  
---|---|---  
1 | CSS-T Mysql Client 任意文件读取攻击链拓展 | <https://paper.seebug.org/1112/>  
2 | Fastjson 反序列化漏洞史 | <https://paper.seebug.org/1192/>  
3 | 聊聊区块链中的几个技术点 | <https://paper.seebug.org/1110/>  
4 | XSS 扫描器成长记 | <https://paper.seebug.org/1119/>  
5 | CVE-2020-0796 Windows SMBv3 LPE Exploit POC Analysis |
<https://paper.seebug.org/1165/>  
6 | CSS-T Mysql Client Arbitrary File Reading Attack Chain Extension |
<https://paper.seebug.org/1113/>  
7 | 从 0 开始入门 Chrome Ext 安全（番外篇） -- ZoomEye Tools |
<https://paper.seebug.org/1115/>  
8 | Hessian 反序列化及相关利用链 | https://paper.seebug.org/1131/  
9 | CVE-2020-0796 Windows SMBv3 LPE Exploit POC 分析 |
https://paper.seebug.org/1164/  
10 | 从0开始聊聊自动化静态代码审计工具 | <https://paper.seebug.org/1339/>  
11 | Liferay Portal Json Web Service 反序列化漏洞(CVE-2020-7961) |
<https://paper.seebug.org/1162/>  
12 | Getting Started with Chrome Ext Security (Extra)-Zoomeye Tools |
<https://paper.seebug.org/1116/>  
13 | CVE-2020-3119 Cisco CDP Stack Overflow Analysis |
<https://paper.seebug.org/1156/>  
14 | Hessian deserialization and related gadget chains |
<https://paper.seebug.org/1137/>  
15 | Liferay Portal Json Web Service Deserialization Vulnerability
(CVE-2020-7961) Analysis | <https://paper.seebug.org/1163/>  
16 | 从代码角度看各类子域名收集工具 | <https://paper.seebug.org/1292/>  
17 | CVE-2020-3119 Cisco CDP 协议栈溢出漏洞分析 | <https://paper.seebug.org/1154/>  
18 | 使用 ZoomEye 寻找 APT 攻击的蛛丝马迹 | <https://paper.seebug.org/1219/>  
19 | ksubdomain 无状态域名爆破工具 | <https://paper.seebug.org/1325/>  
20 | 从反序列化到类型混淆漏洞——记一次 ecshop 实例利用 | <https://paper.seebug.org/1267/>  
  
## 七、2020年最受欢迎的翻译文章Top10

ID | 文章名称 | 文章链接  
---|---|---  
1 | CVE-2020-0796 Windows SMBv3 LPE Exploit POC Analysis |
<https://paper.seebug.org/1165/>  
2 | CSS-T Mysql Client Arbitrary File Reading Attack Chain Extension |
<https://paper.seebug.org/1113/>  
3 | Getting Started with Chrome Ext Security (Extra)-Zoomeye Tools |
<https://paper.seebug.org/1116/>  
4 | CVE-2020-3119 Cisco CDP Stack Overflow Analysis |
<https://paper.seebug.org/1156/>  
5 | Hessian deserialization and related gadget chains |
<https://paper.seebug.org/1137/>  
6 | Liferay Portal Json Web Service Deserialization Vulnerability
(CVE-2020-7961) Analysis | <https://paper.seebug.org/1163/>  
7 | Fastjson Deserialization Vulnerability History |
<https://paper.seebug.org/1193/>  
8 | Nexus Repository Manager 3 Several Expression Parsing Vulnerabilities |
<https://paper.seebug.org/1167/>  
9 | Look for traces of APT attacks through the ZoomEye history api |
<https://paper.seebug.org/1220/>  
10 | F5 BIG-IP hsqldb (CVE-2020-5902) Vulnerability Analysis |
<https://paper.seebug.org/1272/>  
  
## 八、2020年最受欢迎的威胁情报

ID | 文章名称 | 文章链接  
---|---|---  
1 | 新兴的URSA木马使用复杂的加载程序影响了许多国家 | <https://paper.seebug.org/1338/>  
2 | 浅谈基于开源工具的威胁情报自动化生产 | <https://paper.seebug.org/1210/>  
3 | Eleethub：使用 Rootkit 进行自我隐藏的加密货币挖矿僵尸网络 | <https://paper.seebug.org/1214/>  
4 | 针对知名航天和军事公司的攻击活动分析 | <https://paper.seebug.org/1248/>  
5 | 新型 Golang 蠕虫在服务器上投放 XMRig Miner 病毒 | <https://paper.seebug.org/1440/>  
6 | Mikroceen 后门程序：对中亚地区政府机构和组织进行秘密间谍活动 | <https://paper.seebug.org/1206/>  
7 | 针对南亚政府和军事组织的 BackConfig 恶意软件 | <https://paper.seebug.org/1202/>  
8 | 针对欧洲组织的新的僵尸网络 Outlaw 再度来袭 | <https://paper.seebug.org/1204/>  
9 | Rovnix Bootkit 恶意软件相关活动分析 | <https://paper.seebug.org/1253/>  
10 | COMpfun 操作者利用基于 HTTP 状态的木马欺骗签证申请 | <https://paper.seebug.org/1212/>  
11 | 垃圾钓鱼邮件活动：通过 paste.ee 和 Excel 文件向德国用户发送 Netwire RAT 恶意软件 |
<https://paper.seebug.org/1216/>  
12 | 多阶段 APT 攻击使用 C2 功能降低 Cobalt Strike | <https://paper.seebug.org/1250/>  
13 | UltraRank 黑客组织的新攻击 | <https://paper.seebug.org/1438/>  
14 | 攻击者滥用合法的云监控工具进行网络攻击 | <https://paper.seebug.org/1333/>  
15 | Mirai 和 Hoaxcalls 僵尸网络瞄准旧版赛门铁克 Web 网关 | <https://paper.seebug.org/1211/>  
16 | Joker 恶意软件通过上传到 Google Play 商店促使用户下载 | <https://paper.seebug.org/1352/>  
17 | LOLSnif–另一个基于Ursnif的目标追踪活动 | <https://paper.seebug.org/1213/>  
18 | Wolf 恶意软件再次发起攻击 | <https://paper.seebug.org/1215/>  
19 | Gamaredon 威胁组织活动相关分析 | <https://paper.seebug.org/1245/>  
20 | NetWalker 勒索软件相关分析 | <https://paper.seebug.org/1243/>  
  
# 2021 Seebug

2021年，Seebug会经历一次大的改版，将漏洞信息聚合作为Seebug漏洞平台的主要目标。同时长期收取1day漏洞情报，向各位白帽子提供最快最全的漏洞情报推送~

为了迎接2021年，我们精心挑选了10个受到关注的漏洞的PoC，全部提供公开兑换啦！

ID | 文章名称 | 文章链接  
---|---|---  
1 | FusionAuth FreeMarker模板注入漏洞(CVE-2020-7799) |
<https://www.seebug.org/vuldb/ssvid-98128>  
2 | Apache Tomcat Ajp协议文件包含漏洞(CVE-2020-1938) |
<https://www.seebug.org/vuldb/ssvid-98134>  
3 | Apache ShardingSphere远程代码执行漏洞(CVE-2020-1947) |
<https://www.seebug.org/vuldb/ssvid-98180>  
4 | 通达OA任意文件上传配合文件包含导致的RCE | <https://www.seebug.org/vuldb/ssvid-98186>  
5 | Liferay Portal JSON Web Service RCE漏洞(CVE-2020-7961) |
<https://www.seebug.org/vuldb/ssvid-98193>  
6 | 用友GRP-u8 SQL注入 | <https://www.seebug.org/vuldb/ssvid-98376>  
7 | VMware vCenter未授权任意文件读取漏洞 | <https://www.seebug.org/vuldb/ssvid-98394>  
8 | Jira未授权用户枚举(CVE-2020-14181) | <https://www.seebug.org/vuldb/ssvid-98400>  
9 | ecshop商城系统4.0.8-4.1.0 delete_cart_goods.php文件SQL注入漏洞 |
<https://www.seebug.org/vuldb/ssvid-99060>  
10 | SolarWinds任意文件读取漏洞（CVE-2020-10148） |
<https://www.seebug.org/vuldb/ssvid-99087>  
  
扫码文末二维码，关注Seebug官方微信公众号并参与活动，有机会抽取“星链计划定制抱枕+Seebug定制机械键盘”大礼包哦！！！

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1457/>

