**近期，思科Talos安全团队的安全研究专家Jared Rittle和Carl Hurd在[ _Moxa
AWK-3131A_](https://www.moxa.com/en/products/industrial-network-infrastructure/wireless-ap-bridge-client/wlan-ap-bridge-client/awk-3131a-series)网络设备中发现了三个严重的安全漏洞，这些漏洞将允许攻击者在安装了该款设备的工业环境中执行恶意活动。**

AWK-3131A是一款无线网络设备，主要适用于大型工业环境，并能够提供跨部署环境的网络通信服务。根据安全研究专家的发现，这款设备中存在的几个严重安全漏洞将有可能允许攻击者执行各种恶意行为，其中包括远程代码执行和权限提升。

![](https://image.3001.net/images/20200226/1582703416_5e562338bbc68.jpg!small)

## 漏洞细节

### Moxa AWK-3131A iw_console提权漏洞 (TALOS-2019-0925/CVE-2019-5136)

Moxa
AWK-3131A的iw_console功能中存在一个可被攻击者利用的权限提升漏洞，受影响固件版本为v1.13。其中，一个特殊的菜单选择字符串将可能导致从受限控制台实现权限转换，并导致系统以root用户权限访问。攻击者可以在作为低权限用户进行身份验证时发送命令来触发此漏洞。

> 如需了解该漏洞的详细信息，可以参考完整的【[
> _漏洞公告_](https://www.talosintelligence.com/vulnerability_reports/TALOS-2019-0925)】。

### Moxa AWK-3131A ServiceAgent 使用硬编码加密密钥 (TALOS-2019-0926/CVE-2019-5137)

ServiceAgent二进制文件中硬编码加密密钥的使用，将允许攻击者解密从Moxa AWK-3131A（固件版本1.13）中捕捉到的网络流量。

> 如需了解该漏洞的详细信息，可以参考完整的【[
> _漏洞公告_](https://www.talosintelligence.com/vulnerability_reports/TALOS-2019-0926)】。

### Moxa AWK-3131A加密诊断脚本命令注入漏洞 (TALOS-2019-0927/CVE-2019-5138)

Moxa
AWK-3131A（固件版本1.13）的加密诊断脚本功能中存在可利用的命令注入漏洞。巧尽心思构建的诊断脚本文件可能导致执行任意busybox命令，从而实现对设备进行远程控制。攻击者可以在验证为低权限用户时发送诊断信息以触发此漏洞。

> 如需了解该漏洞的详细信息，可以参考完整的【[
> _漏洞公告_](https://www.talosintelligence.com/vulnerability_reports/TALOS-2019-0927)】。

### Moxa AWK-3131A多个iw_* 实用工具使用硬编码凭证漏洞 (TALOS-2019-0928/CVE-2019-5139)

Moxa
AWK-3131A（固件版本1.13）的多个iw_*实用程序中存在可利用的硬编码凭据使用漏洞。设备操作系统包含未记录的加密密码，允许攻击者创建自定义诊断脚本。

> 如需了解该漏洞的详细信息，可以参考完整的【[
> _漏洞公告_](https://www.talosintelligence.com/vulnerability_reports/TALOS-2019-0928)】。

### Moxa AWK-3131A iw_webs DecryptScriptFile 文件名命令注入漏洞
(TALOS-2019-0929/CVE-2019-5140)

Moxa
AWK-3131A（固件版本1.13）的iw_webs功能中存在可利用的命令注入漏洞。精心编制的诊断脚本文件名可能会导致用户输入的数据映射在随后的iw_系统调用中，从而实现对设备的远程控制。攻击者可以在作为低权限用户进行身份验证时发送命令来触发此漏洞。

> 如需了解该漏洞的详细信息，可以参考完整的【[
> _漏洞公告_](https://www.talosintelligence.com/vulnerability_reports/TALOS-2019-0929)】。

### Moxa AWK-3131A iw_webs iw_serverip 参数命令注入漏洞
(TALOS-2019-0930/CVE-2019-5141)

Moxa
AWK-3131A（固件版本1.13）的iw_webs功能中存在可利用的命令注入漏洞。精心编制的iw_serverip参数可能会导致用户输入数据映射在随后的iw_系统调用中，从而实现对设备的远程控制。攻击者可以在作为低权限用户进行身份验证时发送命令来触发此漏洞。

> 如需了解该漏洞的详细信息，可以参考完整的【[
> _漏洞公告_](https://www.talosintelligence.com/vulnerability_reports/TALOS-2019-0930)】。

### Moxa AWK-3131A WAP主机名命令注入漏洞 (TALOS-2019-0931/CVE-2019-5142)

Moxa
AWK-3131A（固件版本1.13）的主机名功能中存在可利用的命令注入漏洞。精心编制的网络配置信息条目可能导致攻击者在目标设备上执行任意系统命令，从而完全控制设备。攻击者可以发送各种经过身份验证的请求来触发此漏洞。

> 如需了解该漏洞的详细信息，可以参考完整的【[
> _漏洞公告_](https://www.talosintelligence.com/vulnerability_reports/TALOS-2019-0931)】。

### Moxa AWK-3131A iw_console conio_writestr远程代码执行漏洞
(TALOS-2019-0932/CVE-2019-5143)

Moxa AWK-3131A（固件版本1.13）的iw_console
conio_writestr功能中存在可利用的格式字符串漏洞。精心编制的时间服务器条目可能导致时间服务器缓冲区溢出，从而导致远程代码执行。攻击者可以在作为低权限用户进行身份验证时发送命令来触发此漏洞。

> 如需了解该漏洞的详细信息，可以参考完整的【[
> _漏洞公告_](https://www.talosintelligence.com/vulnerability_reports/TALOS-2019-0932)】。

### Moxa AWK-3131A ServiceAgent 拒绝服务漏洞 (TALOS-2019-0938/CVE-2019-5148)

Moxa
AWK-3131A（固件版本1.13）的ServiceAgent功能中存在可利用的拒绝服务漏洞。精心编制的数据包可能导致整型下溢的情况，将有可能导致系统访问未映射或越界的内存数据。攻击者可以在未经验证的情况下发送此数据包以触发此漏洞。

> 如需了解该漏洞的详细信息，可以参考完整的【[
> _漏洞公告_](https://www.talosintelligence.com/vulnerability_reports/TALOS-2019-0938)】。

### Moxa AWK-3131A iw_webs 用户配置远程代码执行漏洞 (TALOS-2019-0944/CVE-2019-5153)

Moxa
AWK-3131A（固件版本1.13）的iw_webs配置解析功能中存在可利用的远程代码执行漏洞。精心编制的用户名项可能导致错误消息缓冲区溢出，从而实现远程代码执行。攻击者可以在作为低权限用户进行身份验证时发送命令来触发此漏洞。

> 如需了解该漏洞的详细信息，可以参考完整的【[
> _漏洞公告_](https://www.talosintelligence.com/vulnerability_reports/TALOS-2019-0944)】。

### Moxa AWK-3131A iw_webs 账号设置错误访问控制漏洞 (TALOS-2019-0955/CVE-2019-5162)

Moxa
AWK-3131A（固件版本1.13）的iw_webs帐户设置功能中存在可利用的不当访问控制漏洞。精心编制的用户名项可能会导致覆盖现有的用户帐户密码，从而导致攻击者能够以该用户身份远程shell访问设备。攻击者可以在作为低权限用户进行身份验证时发送命令来触发此漏洞。

> 如需了解该漏洞的详细信息，可以参考完整的【[
> _漏洞公告_](https://www.talosintelligence.com/vulnerability_reports/TALOS-2019-0955)】。

### Moxa AWK-3131A iw_webs 主机名认证绕过漏洞 (TALOS-2019-0960/CVE-2019-5165)

Moxa
AWK-3131A（固件版本1.13）的主机名处理进程中存在可利用的身份验证绕过漏洞。特别配置的设备主机名可能会导致设备将选定的远程通信量解释为本地通信量，从而绕过web身份验证。攻击者可以发送经过身份验证的SNMP请求来触发此漏洞。

> 如需了解该漏洞的详细信息，可以参考完整的【[
> _漏洞公告_](https://www.talosintelligence.com/vulnerability_reports/TALOS-2019-0960)】。

## 版本测试

Talos安全团队已在运行了v1.13版本固件的Moxa AWK-3131A设备上测试并验证了相关漏洞。

## 漏洞修复

![](https://image.3001.net/images/20200226/1582703460_5e562364b1ca2.jpg!small)

根据我们的协调披露政策，思科Talos安全团队已与Moxa展开深度合作，以确保这个问题能够在短期之内得到有效解决，并及时为受这些漏洞影响的用户提供[
_更新补丁_](https://www.moxa.com/en/support/support/security-advisory/awk-3131a-series-industrial-ap-bridge-client-vulnerabilities)。【[
_点我获取_](https://1.bp.blogspot.com/-JXkSIehaKi4/XUgwEX6wLjI/AAAAAAAAAC8/8mea4rZfy7AGT_PIchejkERmCFmfdbxTACPcBGAYYCw/s1600/patch_availability_available.jpg)】

 *** 参考来源：[
_talosintelligence_](https://blog.talosintelligence.com/2020/02/vuln-spotlight-moxa-awk-feb-2020.html)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

