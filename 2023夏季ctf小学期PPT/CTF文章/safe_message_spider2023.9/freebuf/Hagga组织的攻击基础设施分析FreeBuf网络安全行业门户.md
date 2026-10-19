在 Z-Lab 公布了 Hagga 组织的威胁后，研究人员正在持续对其进行追踪，最近， Hagga 又在通过多阶段感染分发 Agent Tesla
窃密程序，研究人员披露了使用的 IOC 指标与 C&C 面板的通用 URL 模式。

![image.png-235.6kB](https://image.3001.net/images/20220718/1658121996_62d4ef0c8ad8930398632.png!small)C&C
面板 IOC

## 69.174.99.181

根据 Passive DNS 数据，69.174.99.181 从 2021 年 11 月 1 日起就绑定在
update.newbotv4.monster。在此之前，该 IP 没有绑定其他域名，这表明该 IP 地址可能是专用基础设施。

与该 IP 地址相关有一个过期的自签发证书，CN 值为 localhost，且证书的 SHA1 为
`B0:23:8C:54:7A:90:5B:FA:11:9C:4E:8B:AC:CA:EA:CF:36:49:1F:F6`。

在分析遥测数据时，97% 的数据都与 3306 端口的单个 Hostinger IP 地址通信有关。在攻击行动发生的 10 月 14 日至 12 月 17
日之间，与分发 Agent Tesla 的时间窗口重合。

## Hostinger IP 地址

Hostinger cPanel 服务关联的 16 个 TCP
端口为：端口21、25、80、110、143、443、465、587、993、995、2080、2083、2086、2087 和 3306。

Hostinger IP 地址的遥测数据最早可以追溯到 2021 年 9 月 17 日，有非常多 IP 地址存在 3306 端口的入站连接。推测该 IP
地址在其他 Hostinger 客户端之间共享。

![image.png-82kB](https://image.3001.net/images/20220718/1658121997_62d4ef0d79b3c6fd961bd.png!small)Hostinger
MySQL 客户端

## Hostinger MySQL 客户端

考虑到 Hostinger IP 被用于共享的可能性，将分析范围限制为与初始 C&C 地址相关的数据。能够确定几个对原始 C&C IP 地址的 HTTP
请求，其中有几个使用通用命名约定的 webpanel 路径。

![image.png-66.6kB](https://image.3001.net/images/20220718/1658121998_62d4ef0e3d58ea81afdfa.png!small)HTTP
URL 请求

此外，根据 webpanel 模式发现了其他 Hostinger MySQL 客户端的类似请求：

![image.png-50.5kB](https://image.3001.net/images/20220718/1658121998_62d4ef0eda1b4f065ae7c.png!small)HTTP
URL 请求

有趣的是，155.94.209.50 中部署了 login.php 页面，访问时能够看到 Mana Tools 标志的登录页面：

![image.png-165.9kB](https://image.3001.net/images/20220718/1658121999_62d4ef0f78899ecc82724.png!small)MANA
TOOLS C&C 面板

请求 `http://69.174.99.181/webpanel-reza/login.php`时，可以看到相同的页面。

Mana Tools 是一个恶意软件分发和 C&C 面板，由 Hagga 组织创建。与几个著名的恶意软件变种有关，包括
RevengeRAT、AzoRult、Lokibot、Formbook 和 Agent Tesla。

除了 155.94.209.50 之外，研究人员还确定了另外三个 MySQL 客户端，它们都使用了与 69.174.99.181 相同的过期自签名 SSL
证书。

根据 DNS 与 WHOIS 数据，所有 IP 都部署在 QuadraNet 的基础设施中。

![image.png-113.4kB](https://image.3001.net/images/20220718/1658122000_62d4ef103a55078cfd4eb.png!small)

攻击基础设施

这些服务器似乎都是 Windows 服务器，在 RDP 响应中能够返回 WIN-NetBIOS 计算机名称。

根据遥测数据，攻击者在 2021 年 10 月 13 日，将 C&C 域名从 bot.statusupdate.one 切换为
newbotv4.monster。

## X.509 证书

序列号为 B5C752C98781B503 的证书是作为 XAMPP 安装组件的默认证书，XAMPP 是一个免费的开源发行版软件，它将
OpenSSL、MariaDB、PHP 和 Perl 与 Apache Web 服务器打包在一起。

该证书在部署 Mana Tools 的主机上频繁发现，攻击者似乎使用 XAMPP 作为基础环境。

## Hostinger IP

通过遥测数据与 MalBeacon 的数据综合判断，确定了巴基斯坦拉合尔附近的几个攻击者 IP，都与 C&C 服务器 69.174.99.181 和
64.188.20.198 存在关联。

![image.png-99.9kB](https://image.3001.net/images/20220718/1658122001_62d4ef110f25404acca71.png!small)MALBECON
数据

遥测数据中，也能印证在 2021 年 11 月 26 日从 42.201.155.21 与在 2021 年 12 月 2 日至 2021 年 12 月 3
日期间从 42.201.155.40 都存在过 cPanel 的连接流量，可以高度确认这些是攻击者 IP 。

根据遥测数据，HOSTINGER 默认提供的绑定关系如下所示：

![image.png-119.8kB](https://image.3001.net/images/20220718/1658122001_62d4ef11c1bfcf3abc73c.png!small)HOSTINGER
Passive DNS 数据

## Hostinger IP 的持续跟踪

根据遥测数据持续跟踪 Hostinger IP 如下所示：

> 103.151.122.110 (VNPT-AS-VN, VN)
>
> 72.11.157.208 (QuadraNet, US)
>
> 192.154.226.47 (Reprise Hosting, US)
>
> 64.188.21.227 (QuadraNet, US)
>
> 72.11.143.125 (QuadraNet, US)
>
> 72.11.143.47 (QuadraNet, US)
>
> 207.32.217.137 (1G Servers, US)
>
> 194.31.98.108 (PREFIXBROKER, NL)
>
> 103.133.105.61 (VNPT-AS-VN, VN)
>
> 78.138.105.142 VELIANET-FR-PINETLLC, FR)
>
> 103.153.77.98 (VNPT-AS-VN, VN)

跟踪过程中还发现了 Mana Tools C&C 面板进行了升级：

![image.png-459.8kB](https://image.3001.net/images/20220718/1658122002_62d4ef12a0d83e3209b62.png!small)新版
Mana Tools C&C 面板

根据 MalBeacon 的数据发现了一批新的攻击者 IP 地址，仍然在巴基斯坦拉合尔附近。在与 C&C 面板通信的相同时间窗口，这些 IP 与
Hostinger IP 也存在通信行为。

![image.png-145.7kB](https://image.3001.net/images/20220718/1658122003_62d4ef1394307b75ab6b1.png!small)HAGGA
架构

## 结论

研究人员通过与 Agent Tesla 有关的 C&C 服务器为起点，不断通过数据分析扩展 Hagga 攻击基础设施的整体架构。确定了部署 Mana
Tools C&C 面板的服务器与攻击者的 IP 地址。

## IOC

> 103.151.122.110  
> 72.11.157.208  
> 192.154.226.47  
> 64.188.21.227  
> 72.11.143.125  
> 72.11.143.47  
> 207.32.217.137  
> 194.31.98.108  
> 103.133.105.61  
> 78.138.105.142  
> 103.153.77.98  
> 69.174.99.181  
> 161.129.64.49  
> 155.94.209.50  
> 64.188.27.104  
> 64.188.20.198  
> mobibagugu.duckdns.org  
> mobibanewdan.duckdns.org  
> mohbeebnew.duckdns.org  
> mubbibun.duckdns.org  
> cdec22.duckdns.org  
> vncgoga.duckdns.org  
> bakuzamokala.duckdns.org  
> warnonmobina.duckdns.org  
> abotherrdpajq.duckdns.org  
> mobinomomuam.duckdns.org  
> workflowstatus.live  
> heavy-dutyindustry.shop  
> microsoftiswear.duckdns.org  
> update.newbotv4.monster  
> newbotv4.monster  
> bot.statusupdate.one

## 参考来源

> [Cymru](https://team-cymru.com/blog/2022/07/12/an-analysis-of-> infrastructure-linked-to-the-hagga-threat-actor/)

