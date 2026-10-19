对 WHOIS 数据的最新[研究](http://interisle.net/ContactStudy2021.html)表明，ICANN
管理范围内的顶级域名有超过一半的控制方身份不明。ICANN
的政策允许域名注册服务提供商和域名管理服务提供商隐藏的联系人数据比GDPR要求的多得多，几乎是GDPR的五倍。

原来，利用 WHOIS 数据可以查到域名的持有人，可以利用此方法来扩展查找姓名、地址、电话号码等，发现归属于同一注册人的其他域名。现在，以 GDPR
为首的法律法规为这种狩猎方法画上了句号。

WHOIS 数据在威胁狩猎上作用越来越小，互联网相关数据的关联整合对威胁调查而言变得越来越重要，尤其是 GDPR 问世后凸显了这种价值。

互联网的实体之间数十亿关系，包括 PassiveDNS、SSL 证书、子域名、OSINT 等。这些实体之间的关系，也许就是揭开真相的关键。

互联网实体的关联可以帮助分析人员查找威胁基础设施的关联，通过尽力消除数据中的噪音为分析人员提供高度相关的上下文和可运营的威胁情报。![](https://image.3001.net/images/20210928/1632805728_6152a36091e14e52ca4ad.png!small)

例如上图，假如我们发现了一个恶意软件使用的 IP 地址和加密 C&C 通信的 SSL 证书、证书中有颁发证书的域名和托管的 IP 地址。利用
PassiveDNS 可以发现该 IP 地址和另一个域名有关联。分析人员可以快速发现，攻击者在攻击行动中的不同主机都嵌入了相同的唯一 Cookie。

下面讲一个使用 SSL 证书的实例。SSL 证书包含的通用名称、组织名称、序列号和 SHA1 都可以用来帮助确定实体间的关联关系，包括域名和 IP 地址。

查看域名 `cms.letzplayagame.com`的 WHOIS
信息：![](https://image.3001.net/images/20210928/1632805737_6152a369378d085b776cb.png!small)

尽管没有任何信息可以用来扩展发现其他基础设施，但仍可以看到该域名在黑名单中，而且 CrowdStrike 已确定其与 RAT 和 CobaltStrike
有关。

紧接着，查看与该域名相关的两个 IP 地址，尝试是否能够找到与之关联的 SSL 证书，确认其是否与其他域名/IP
地址相关。![](https://image.3001.net/images/20210928/1632805744_6152a370a680cc7e680ad.png!small)

查看 IP 地址 102.129.224.148 就能够发现两个与之相关的 SSL
证书。![](https://image.3001.net/images/20210928/1632805751_6152a377f3584ddc04058.png!small)

再点击组织名称 `Asphyxiation Server`，查看相同组织名称的其他 SSL 证书（根据 Digicert 的最佳实践，通用名称是用于 DNS
查找的
FQDN，浏览器使用此信息标识网站。组织名称是在国家、省/州、市一级注册过，尽量使用注册的法定名称）。![](https://image.3001.net/images/20210928/1632805759_6152a37f2e21266d54524.png!small)

发现了两个与证书相关的、新的 IP 地址（5.101.0.202 和
5.101.1.202），新的域名（taintakoo.com）。其中，5.101.0.202 与另外四个域名存在关联，根据 CrowdStrike
的情报，该 IP 地址与 RAT 和 Cobalt Strike
有关。![](https://image.3001.net/images/20210928/1632805764_6152a38481f25494cfef6.png!small)

域名 `cms.tanitakoo.com`与 `letzplayagame.com`都有着类似的子域名命名习惯。可以查看相关的 5 个 SSL
证书：![](https://image.3001.net/images/20210928/1632805771_6152a38b910d6c9d4d1a8.png!small)  
通过证书又可以发现与 IP 地址相关的域名（streamer.local 与
s10.wisp.cat）：![](https://image.3001.net/images/20210928/1632805775_6152a38f988d3c2948b2c.png!small)

上面这个案例就足以证明，一方面随着 GDPR 的使用导致 WHOIS 数据关联的失效，另一方面 SSL 证书是可以代替 WHOIS 进行关联发现的。

## 参考来源

> [RISKIQ](https://www.riskiq.com/blog/external-threat-management/threat-> hunting-post-whois/)

