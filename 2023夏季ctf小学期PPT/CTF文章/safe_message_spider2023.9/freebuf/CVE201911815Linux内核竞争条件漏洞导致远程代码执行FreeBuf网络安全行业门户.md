***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

![](https://image.3001.net/images/20190714/1563103299_5d2b1043b405a.jpg!small)

 **运行了Linux发行版的计算机设备，如果内核版本小于5.0.8的话，将有可能受到一个内核竞争条件漏洞的影响，并导致系统无法抵御远程网络攻击。**

潜在的攻击者可以利用Linux内核中net/rds/tcp.c的rds_tcp_kill_sock
TCP/IP实现缺陷，从而触发设备的拒绝服务（DoS）状态，并在受影响的设备上实现远程代码执行。

攻击者可以通过特制的TCP数据包对存在漏洞的Linux设备进行攻击，而这些特制的TCP数据包将能够在目标系统上触发“用后释放”错误，并允许攻击者在目标设备上执行任意代码。

NIST针对这个远程代码执行漏洞的漏洞评分为8.1分，因此该漏洞为高危漏洞（NVD），该漏洞分配的CVE编号为CVE-2019-11815（Red
Hat、Ubuntu、SUSE和Debian不同版本均受此漏洞的影响），未经身份验证的攻击者将能够利用该漏洞实现远程代码执行，而且整个过程完全不需要任何用户交互。

![](https://image.3001.net/images/20190714/1563103304_5d2b10486c2f2.jpg!small)

幸运的是，由于利用该漏洞来实施攻击的复杂度非常高，因此该漏洞的可利用评级仅为2.2，而该漏洞的影响评级也仅为5.9。

根据[CVSS](https://www.first.org/cvss)
3.0的漏洞影响衡量标准，漏洞CVE-2019-11815对目标设备以及数据的机密性、完整性以及可用性会产生非常严重的影响，潜在的攻击者在成功利用该漏洞之后，可以获取到目标设备所有资源的访问权和修改权，甚至还可以执行拒绝服务等攻击。

正如CWE软件安全缺陷数据库中提供的[描述](https://cwe.mitre.org/data/definitions/416.html)一样：“用后释放漏洞是由于在内存释放后，资源再次被引用所引起的软件崩溃状态，这些被引用的内容可以是某个值，或是某段代码。”

Linux内核开发人员在今年的五月底针对漏洞CVE-2019-11815的问题发布了一个[安全补丁](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=cb66ddd156203daefb8d71158036b27b0e2caf63)，并在6月17日发布的[Linux内核
v5.0.8版本](https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.0.8)中修复了该问题。

建议广大用户尽快检查自己的Linux设备是否受到该漏洞的影响，并尽快安装更新补丁，具体的漏洞环节方案可以参考RedHat提供的[CVE-2010-3904安全公告](https://access.redhat.com/security/cve/cve-2010-3904#field_cve_mitigation_text)。

 ***
参考来源：[bleepingcomputer](https://www.bleepingcomputer.com/news/security/linux-kernel-prior-to-508-vulnerable-to-remote-code-execution/)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

