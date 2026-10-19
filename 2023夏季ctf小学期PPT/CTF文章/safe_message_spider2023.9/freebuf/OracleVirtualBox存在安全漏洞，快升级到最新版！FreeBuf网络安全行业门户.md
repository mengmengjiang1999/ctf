![](https://image.3001.net/images/20211125/1637819734_619f2556f11f4953446e4.jpg!small)近期，专家披露了甲骨文VirtualBox
中的漏洞（编号为 CVE-2021-2442），该漏洞可能会被用于破坏虚拟机管理程序并触发拒绝服务 (DoS) 条件。

CVE-2021-2442由 SentinelLabs 的 Max Van Amerongen 发现，其 CVSS 评分为
6.0。该漏洞可能影响到VirtualBox 6.1.24 之前的版本。

美国国家标准与技术研究院（NIST）对漏洞进行了详细描述：“该漏洞很容易被高权限攻击者利用，一旦夺取VirtualBox的漏洞权限，可能导致VirtualBox
挂起或频繁崩溃。”

今年7月， Oracle 已发布补丁将CVE-2021-2442修复。此前， Amerongen还发现了甲骨文VirtualBox NAT
中的2个提权漏洞，分别编号为CVE-2021-2145和CVE-2021-2310。

CVE-2021-2145 是 Oracle VirtualBox NAT 中的整数下溢出提权漏洞，而 CVE-2021-2310
则是基于堆的缓冲区溢出提权漏洞。这2个漏洞影响VirtualBox 6.1.20 之前的版本，甲骨文已在今年4月进行修复。

以上的漏洞有源于VirtualBox缺乏必要的数据验证手段，攻击者可以利用这些漏洞提升权限，并在VirtualBox执行任意代码。

为避免这一漏洞被不发分子利用，专家建议企业尽快将其 VirtualBox 安装升级到最新版本。

> 参考来源：https://securityaffairs.co/wordpress/124944/security/oracle-virtualbox-> flaws.html

