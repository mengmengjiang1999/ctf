5月28日下午，微软威胁情报中心（MSTIC）发现，SolarWinds事件背后的攻击者正在进行一场针对全球政府机构的网络钓鱼运动。

[MSTIC透露](https://blogs.microsoft.com/on-the-issues/2021/05/27/nobelium-cyberattack-nativezone-solarwinds/):“本周，我们观察到了黑客组织Nobelium针对政府机构、智库、顾问和非政府组织的网络攻击。”

这波攻击针对150多个不同组织的大约3000个电子邮件账户。“虽然美国的组织受到的攻击最多，但目标受害者遍及至少24个国家。”

 **微软追踪此次的攻击者为黑客组织Nobelium，也是此前微软认定的SolarWinds事件的攻击者，背后可能是俄罗斯政府支持。**

该组织使用美国国际开发署（USAID）的Constant Contact账户（一种合法的电子邮件营销服务）发送了这些钓鱼邮件。

![](https://image.3001.net/images/20210531/1622445678_60b48e6eacedbb7709f6b.png!small)冒充美国国际开发署的钓鱼邮件

该活动始于2021年1月，慢慢演变成一系列攻击，上周以美国国际开发署为主题的网络钓鱼浪潮达到高潮。

网络安全公司[Volexity也发布了一份报告](https://www.volexity.com/blog/2021/05/27/suspected-apt29-operation-launches-election-fraud-themed-phishing-campaigns/)，
**将这次网络钓鱼活动与俄罗斯外国情报机构（SVR）的运营商** （追踪为APT29、Cozy Bear和The
Dukes）联系在一起，这些网络钓鱼活动使用的战术可以追溯到2018年。

Nobelium的感染链和恶意软件传递技术在整个攻击过程中不断发展，通过包含HTML附件的鱼叉式钓鱼信息将一个ISO文件放入受害者的硬盘。

在受害者挂载ISO后，他们被鼓励打开包含在其中的文件（LNK快捷方式或RTF文档），这将执行一个DLL捆绑在文件或存储在ISO映像中，在系统上加载钴打击信标。

微软表示:“如果目标设备是苹果iOS设备，用户会被重定向到Nobelium控制下的另一台服务器，利用当时的CVE-2021-1879分发代码漏洞利用。”

微软补充说:“这些有效载荷的成功部署使Nobelium能够持续访问受威胁系统。”
“Nobelium利用恶意载荷对目标采取横向移动、数据泄露和传递额外等行动。”

微软的报告中阐述了攻击期间观察到的恶意行为、细节，攻击者动机，以及抵御攻击的最佳实践。

![](https://image.3001.net/images/20210531/1622445824_60b48f00c38b03fe912ea.png!small)HTML-ISO感染链

微软在报告中推测，Nobelium此次的攻击是情报收集工作的一部分。这次攻击之所以声势浩大原因有三。

> 一是Nobelium的活动以及类似参与者的活动是获得供应商的访问权并感染客户。
>
>
> 二是Nobelium活动者通常回追踪其所在国家/地区关注的问题。例如此次Nobelium的目标是人权组织等。在疫情高峰期则是疫苗机构和医疗机构，2019年则是体育和反兴奋剂组织。
>
> 三是来自民族国家的网络攻击并没有放缓。

在一篇新的博客文章中，微软还提供了Nobelium在攻击中使用的四个新恶意软件家族的细节。

这四个新系列包括一个名为 "EnvyScout "的HTML附件，一个名为 "BoomBox "的下载器，一个名为 "NativeZone
"的加载器，以及一个名为 "VaporRage "的壳码下载器和启动器。

去年12月，SolarWinds在一次网络攻击中被攻破，攻击者针对该公司的客户发起供应链攻击。

SolarWinds供应链攻击背后的黑客组织被追踪为Nobelium（微软）、NC2452（火眼）、StellarParticle
（CrowdStrike）、SolarStorm（Palo Alto Unit 42）和Dark Halo （Volexity）。

美国政府正式指控俄罗斯外国情报局（Russian Foreign Intelligence Service），（被追踪为APT29、The
Dukes或Cozy Bear）的威胁行当，认为是攻击SolarWinds的组织在进行“大范围的网络间谍活动”。

微软还在2月份表示，SolarWinds的黑客已经下载了Azure、Intune和Exchange组件的有限数量的源代码。

### 参考链接：

> <https://www.bleepingcomputer.com/news/security/microsoft-russian-svr-> hackers-target-govt-agencies-from-24-countries/>
>
> <https://blogs.microsoft.com/on-the-issues/2021/05/27/nobelium-cyberattack-> nativezone-solarwinds/>
>
> <https://www.volexity.com/blog/2021/05/27/suspected-apt29-operation-> launches-election-fraud-themed-phishing-campaigns/>

