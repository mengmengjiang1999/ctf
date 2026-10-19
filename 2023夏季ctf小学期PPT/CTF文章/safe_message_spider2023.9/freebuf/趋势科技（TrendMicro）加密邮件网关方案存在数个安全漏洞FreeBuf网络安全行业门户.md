***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

##  Core Security安全研究员发现Trend Micro中存在数个邮件网关加密漏洞，其中包括风险级别为 critical 和
high的漏洞。这些漏洞到的 CVE 编号分别为 CVE-2018-6219 至 CVE-2018-6230。  

其中最危险的漏洞可以被本地或远程攻击者利用，获取目标系统的权限执行任意代码执行命令。

> Trend Micro 邮件网关的加密方案是基于 Linux
> 的软件解决方案，它在网关层面为邮件提供了加密和解密的处理，用户不用关心所使用的邮件客户端以及初始平台。TMEEG客户端上电子邮件的加密和解密都是通过策略管理器（Policy
> Manager）进行控制的，管理员则可以根据各种参数配置策略进行首发件控制。

目前发现的漏洞就是在 Trend Micro 邮件加密网关的网络控制台上，远程攻击者如果利用了这个漏洞可以获得root权限的代码执行能力。

![Email-Encryption-Gateway.png](https://image.3001.net/images/20180226/15196135093993.png!small)  

其中影响最大的漏洞为 CVE-2018-6223 ，它与应用注册中缺少身份验证有关。
由于管理员可以在部署过程中使用注册终端中进行配置设定，攻击者也无需身份验证也可访问终端，他们可以设置管理员凭据并对配置进行其他更改。

其他两项漏洞分别是high级别的XSS漏洞，存在可导致命令执行的任意文件写入问题和未经严重的软件更新。其他缺陷包括SQL和XML外部实体（XXE）注入。

## 安全更新

目前受到影响的软件是趋势科技电子邮件加密网关 5.5（Build 1111.00）及更早版本，相关用户可以及时进行软件更新。

2017-06-05 : Core Security 研究人员通知 Trend Micro 漏洞事宜

2017-11-13：Core Security 再次询问 ETA 官方修复。

2018-02-21: CORE-2017-0006 发布

Trend Micro 目前确认还有一个中危级别的 CSRF 问题以及低危级别的 SQL 注入漏洞尚未完全修复。

![trendmicro-monitor.jpg](https://image.3001.net/images/20180226/15196152886862.jpg!small)  

***参考来源：[securityaffairs](http://securityaffairs.co/wordpress/69499/hacking/trendmicro-email-encryption-gateway-flaws.html)，Elaine编译，转载请注明FreeBuf.COM**  

