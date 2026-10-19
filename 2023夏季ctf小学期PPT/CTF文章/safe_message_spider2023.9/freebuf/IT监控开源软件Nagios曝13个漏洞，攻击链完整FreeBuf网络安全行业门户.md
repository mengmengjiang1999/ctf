> Nagios是应用广泛的一种免费开源的IT
> 监控软件，一般来说，Nagios能够监控几乎所有类型的组件，例如网络协议、操作系统、系统指标、应用程序、服务、Web服务器、网站，中间件等。

根据最新消息，Nagios软件中包含13个漏洞，极有可能被恶意利用，使得攻击者可以劫持基础设施。漏洞涵盖了远程代码执行和特权升级。

## 完整的漏洞列表

CVE-2020-28903 – Nagios XI中的XSS漏洞，攻击者可以控制融合服务器。

CVE-2020-28905 – Nagios Fusion可实现远程代码执行进行身份验证

CVE-2020-28902 –通过对cmd_subsys.php中的时区参数进行命令注入，将Nagios Fusion特权从apache升级到nagios

CVE-2020-28901 –通过对cmd_subsys.php中component_dir参数的命令注入，将Nagios
Fusion特权从apache升级到nagios

CVE-2020-28904 –通过安装恶意组件将Nagios Fusion特权从apache升级到nagios

CVE-2020-28900 – 通过upgrade_to_latest.sh将Nagios Fusion和XI特权从Nagios升级到root

CVE-2020-28907 – 通过upgrade_to_latest.sh将Nagios Fusion特权从apache升级到root并修改了代理配置。

CVE-2020-28906 –通过修改fusion-sys.cfg / xi-sys.cfg，将Nagios
Fusion和XI特权从nagios升级到root

CVE-2020-28909 –通过修改可以作为sudo执行的脚本，将Nagios Fusion特权从nagios升级到root

CVE-2020-28908 –通过cmd_subsys.php中的命令注入，将Nagios Fusion特权从apache升级到nagios

CVE-2020-28911 – Nagios Fusion信息泄露：低权限用户可以发现用于对融合服务器进行身份验证的密码

CVE-2020-28648 – Nagios XI认证远程代码执行

CVE-2020-28910 – Nagios XI getprofile.sh特权升级

其中，最严重的漏洞（[CVE-2020-28648](https://nvd.nist.gov/vuln/detail/CVE-2020-28648)）作为一个不正确的输入验证漏洞，主要存在于Nagios
XI的自动发现组件中，可以被经过身份验证的攻击者用来执行远程代码，该漏洞CVSS评分为8.8，影响到5.7.5之前的版本。一旦攻击者损害了在一个客户站点上的Nagios软件安装，就可以将受污染的数据发送到上游Nagios
Fusion服务器，攻击所有其他客户。

## 攻击链

为了更好地理解危害性，研究人员设计了一个包含漏洞利用的攻击链：

1、使用RCE和特权升级，在受感染客户站点的Nagios XI服务器上获得根级代码执行

2、污染返回到Nagios Fusion的数据从而触发XSS

3、利用触发XSS的会话，使RCE和Priv危害Nagios Fusion服务器

4、获得凭据并利用其余客户站点上的
XI服务器进行攻击![1621910698_60ac64aa4891e11929468.png!small?1621910699071](https://image.3001.net/images/20210525/1621910698_60ac64aa4891e11929468.png!small?1621910699071)

综上所述，Nagios中发现的漏洞具备利用可能及危害性，此类针对开源软件的攻击将对目标组织产生巨大影响。

注：研究人员在2020年10月向Nagios报告了这些漏洞，且该公司在11月[对](https://www.nagios.com/products/security/)这些漏洞进行了[处理](https://www.nagios.com/products/security/)。

## 参考来源

> [
> _securityaffairs_](https://securityaffairs.co/wordpress/118207/hacking/nagios-> it-monitoring-flaws.html)

