Cisco于1月20日发布安全更新，修复影响多款SD-WAN产品和Cisco Smart Software Manager软件的远程代码执行（RCE）漏洞。

SD-WAN是帮助管理WAN的软件产品，而Smart Software Manager是Cisco授权许可基于云的管理解决方案。

根据Cisco的安全公告，Cisco SD-WAN产品受到两个缓冲区溢出漏洞（CVE-2021-1300和CVE-2021-1301）的影响。

CVE-2021-1300源于对IP流量的处理错误，攻击者可借助恶意IP流量利用该漏洞，成功利用漏洞，攻击者可以root权限在底层操作系统上执行任意代码。Cisco将该漏洞的安全影响等级评估为高，CVSS
3.0基准评分为9.8。

CVE-2021-1301存在于Cisco SD-WAN软件的NETCONF子系统中。经身份验证的远程攻击者可利用该漏洞导致受影响的设备或系统拒绝服务。

这两个漏洞影响以下Cisco SD-WAN Software：

  * IOS XE SD-WAN Software
  * SD-WAN vBond Orchestrator Software
  * SD-WAN vEdge Cloud Routers
  * SD-WAN vEdge Routers
  * SD-WAN vManage Software
  * SD-WAN vSmart Controller Software

影响Cisco的云授权许可管理程序的RCE漏洞分别为CVE-2021-1138，CVE-2021-1139，CVE-2021-1140，CVE-2021-1141和CVE-2021-1142。Cisco
Smart Software Manager Satellite 5.1.0及之前版本受到影响

这五个漏洞均存在于Cisco Smart Software Manager Satellite的web
UI中，均源于不充分的输入验证。远程攻击者可通过向受影响的设备发送恶意HTTP请求利用漏洞在底层操作系统上运行任意命令。对CVE-2021-1138，CVE-2021-1140和CVE-2021-1142的利用，无需身份验证；而利用CVE-2021-1139和CVE-2021-1141，要求攻击者经过身份验证。

Cisco已在6.3.0及之后版本中修复了上述漏洞，并将Cisco Smart Software Manager Satellite改名为Cisco
Smart Software Manager On-Prem。

Cisco表示目前尚未获悉前述漏洞遭到公开披露或恶意利用。这些漏洞是Cisco的安全研究人员在对受影响产品进行内部安全测试的过程中发现的。

