渗透测试阶段信息收集完成后，需根据所收集的信息，扫描目标站点可能存在的漏洞，包括SQL注入漏洞、跨站脚本漏洞、文件上传漏洞、文件包含漏洞及命令执行漏洞等，然后通过这些已知的漏洞，寻找目标站点存在攻击的入口。那么今天我们就介绍几款常用的WEB应用漏洞扫描工具。  
  
 **一、AWVS**

Acunetix Web Vulnerability
Scanner（简称AWVS）是一款知名的网络漏洞扫描工具，它通过网络爬虫测试你的网站安全，检测流行安全漏洞。在漏洞扫描实战过程中，一般会首选AWVS，因为这个能扫描出来的漏洞很多，而且使用比较简单。  
  
 **点评：** 强大的漏洞扫描器，漏洞库大而全，可以说市面上最出色的漏洞扫描器  
  
官方网站：https://www.acunetix.com/  
AWVS扫描器使用说明文档：https://www.wangan.com/docs/acunetixweb  
  
 **二、APPScan**  
  
IBM AppScan是一款非常好用且功能强大的Web 应用安全测试工具，曾以 Watchfire AppScan 的名称享誉业界，Rational
AppScan 可自动化 Web 应用的安全漏洞评估工作，能扫描和检测所有常见的 Web 应用安全漏洞，例如 SQL 注入（SQL-injection）、跨站点脚本攻击（cross-site scripting）、缓冲区溢出（buffer overflow）及最新的 Flash/Flex
应用及 Web 2.0 应用曝露等方面安全漏洞的扫描。  
  
 **点评：** AppScan 好处在于误报是最少的，相比WVS扫描更慢，建议配合使用  
  
官方网站：https://www.hcltechsw.com/products/appscan  
详细使用说明文档：https://www.wangan.com/docs/hcl1001  
  
 **三、Nikto**  
  
Nikto是一款开源的Web服务器扫描程序，它可以对Web服务器的多种项目(包括3500个潜在的危险文件/CGI，以及超过900个服务器版本，还有250多个服务器上的版本特定问题)进行全面的测试。Nikto可以在短时间内扫描服务器的多个端口，Nikto因其效率和服务器强化功能而受到青睐。

![Nikto扫描器](https://image.3001.net/images/20210413/1618304327_60755d476ec4b58f602ae.png!small)

 **点评：**
Nikto作为开源的漏洞扫描器，基于Whisker/libwhisker完成其底层功能。这是一款非常棒的工具，但其软件本身并不经常更新，最新和最危险的可能检测不到。  
  
Github地址：https://github.com/sullo/nikto  
详细使用说明文档：https://www.wangan.com/docs/nikto2  
  
 **四、OpenVAS**  
  
OpenVAS（开放式漏洞评估系统）是一个客户端/服务器架构，它常用来评估目标主机上的漏洞。OpenVAS是Nessus开始收费后，独立出来的一个开源的扫描器，OpenVAS默认安装在标准的Kali
Linux上。  
  
 **点评：** OpenVAS具有强大的系统和设备扫描器，缺点是扫描速度慢，占用磁盘空间较大。  
  
官方网站：https://www.openvas.org/  
详细使用说明文档：https://www.wangan.com/docs/openvas  
  
 **五、Xray**  
  
Xray是一款功能强大的安全评估工具，检测速度快（发包速度快，漏洞检测算法高效）；支持范围广（大至 OWASP Top 10 通用漏洞检测，小至各种 CMS
框架 POC，均可以支持）；编写代码的人员素质高, 通过 Code Review、单元测试、集成测试等多层验证来提高代码可靠性。  
  
Xray支持的漏洞检测类型包括XSS漏洞检测 (key: xss)、SQL 注入检测 (key: sqldet)、命令/代码注入检测 (key: cmd-injection)、目录枚举 (key: dirscan)、路径穿越检测 (key: path-traversal)、XML 实体注入检测 (key:
xxe)、文件上传检测 (key: upload)、弱口令检测 (key: brute-force)、jsonp 检测 (key: jsonp)、ssrf
检测 (key: ssrf)、基线检查 (key: baseline)、任意跳转检测 (key: redirect)、CRLF 注入 (key: crlf-injection)、Struts2 系列漏洞检测 (高级版key: struts)、Thinkphp系列漏洞检测 (高级版key:
thinkphp)、POC 框架 (key: phantasm)。  
  
 **点评：** Xray是一款基于Go语言开发的漏洞扫描器，支持导入poc扫描，不过团队对poc的质量要求很高，导致现在poc数量比较少  
  
官方网站：https://xray.cool/  
详细使用说明文档：https://docs.xray.cool/#/tutorial/introduce  
  
  
以上五款WEB应用漏洞扫描工具是日常工作较为实用的扫描器，大家有更好的工具欢迎评论区留言。

-END-
