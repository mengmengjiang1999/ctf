近期研究人员发布了2021年5月至7月中等及以上严重程度的漏洞分析报告（5至7月总共发布了5308个新的漏洞），分析掌握了攻击者最常使用的漏洞，以及每次攻击的严重程度、类别和来源，为抵御网络攻击提供新的解决方案。

## 漏洞总览

在5至7月总共监控了4120个新发布的漏洞，从中度到严重程度不等。

![](https://image.3001.net/images/20210928/1632838797_6153248dd922f9b110bc6.png!small)

![Severity distribution for CVEs registered in May-July 2021: 44.8% medium,
43.1% high, 12.0%
critical.](https://image.3001.net/images/20210928/1632841136_61532db04223dfb7fbfdb.png!small)

与上一季度相比，严重漏洞占比下降了3.5%，中等漏洞略高于之前。总体PoC可用性降低，特别是对于高和中等类别，严重漏洞PoC可用性较高。

4120个最新发布的CVE中，28.2%属于本地漏洞，其余71.8%属于远程漏洞。从2021年5月至7月，最常见的漏洞类型如下：

![1632839552_61532780d384a6d672f05.png!small?1632839552900](https://image.3001.net/images/20210928/1632839552_61532780d384a6d672f05.png!small?1632839552900)

![1632839666_615327f2a39439c9633d2.png!small?1632839667165](https://image.3001.net/images/20210928/1632839666_615327f2a39439c9633d2.png!small?1632839667165)

## 在野漏洞

本季度共分析了1000多万次会话。根据IP地址、端口号和时间戳进一步处理恶意流量，确保了每个攻击会话的唯一性，最终确定了229万个有效的恶意会话。研究人员关联分析过滤后数据推断攻击趋势，从而了解威胁情况。恶意攻击分类如下：

![Attack severity distribution in May-July 2021: 26.2% medium, 37.8% high,
36.0%
critical.](https://image.3001.net/images/20210928/1632841138_61532db27554ccabb2e6e.png!small)

![1632840863_61532c9fd2b782ef21664.png!small?1632840864042](https://image.3001.net/images/20210928/1632840863_61532c9fd2b782ef21664.png!small?1632840864042)

5-7月数据每两周统计：

![1633005611_6155b02b1e1075b9ea4ce.png!small?1633005611050](https://image.3001.net/images/20210930/1633005611_6155b02b1e1075b9ea4ce.png!small?1633005611050)

在本季度经常会发现攻击者使用较新漏洞进行攻击。

![1633005977_6155b199f2507244c7e67.png!small?1633005977968](https://image.3001.net/images/20210930/1633005977_6155b199f2507244c7e67.png!small?1633005977968)

接下来分析5-7月攻击数据中发现攻击者所使用的漏洞。

### [CVE-2020-13927](https://nvd.nist.gov/vuln/detail/CVE-2020-13927)

Apache API存在未经验证的请求缺陷（CVE-2020-13927）。如示例数据，Airflow中可能存在未经验证的远程代码执行（RCE）漏洞。

![Figure 6. Apache Airflow command injection
vulnerability.](https://image.3001.net/images/20210930/1633010017_6155c161b479c91991218.png!small)

### [CVE-2021-27850](https://nvd.nist.gov/vuln/detail/CVE-2021-27850)

攻击者可以通过请求特定URL下载AppModule.class，http://localhost:8080/assets/something/services/AppModule.class
，其中包含Apache Tapestry HMAC密钥。

![Figure 7. Apache Tapestry ClasspathAssetRequestHandler information
disclosure
vulnerability.](https://image.3001.net/images/20210930/1633010021_6155c1652584e9fab23ec.png!small)

### [CVE-2021-21985](https://nvd.nist.gov/vuln/detail/CVE-2021-21985)

VMware vCenter Server远程代码执行漏洞于5月被披露，该漏洞的扫描检查器流量和攻击流量：

![Figure 8. VMware vCenter Server remote code execution vulnerability
checker.](https://image.3001.net/images/20210930/1633010024_6155c168d32adee81022e.png!small)

![Figure 9. VMware vCenter Server remote code execution
vulnerability.](https://image.3001.net/images/20210930/1633010028_6155c16ccd2fbd2f15720.png!small)

### [CVE-2021-29441](https://nvd.nist.gov/vuln/detail/CVE-2021-29441)

Nacos后门，能够绕过和跳过身份验证，该漏洞于4月底发布。

![Figure 10. Nacos authentication bypass
vulnerability.](https://image.3001.net/images/20210930/1633010031_6155c16f781eeacdd1442.png!small)

### [CVE-2021-1498](https://nvd.nist.gov/vuln/detail/CVE-2021-1498)

Cisco在5月份发布了多个漏洞。Cisco HyperFlex HX允许未经验证的远程访问使用特定URL执行命令注入攻击。

![Figure 11. Cisco HyperFlex HX Handling remote command execution
vulnerability.](https://image.3001.net/images/20210930/1633010034_6155c172878cd113ee5e2.png!small)

### [CVE-2021-33564](https://nvd.nist.gov/vuln/detail/CVE-2021-33564)

Dragonfly gem公开了一个参数注入漏洞，攻击者可远程读取和写入任意文件。

![Figure 13. Dragonfly Ruby gem argument injection
vulnerability.](https://image.3001.net/images/20210930/1633010038_6155c1761efd6b3fc37b6.png!small)

### [CVE-2021-35464](https://nvd.nist.gov/vuln/detail/CVE-2021-35464)

ForgeRock AM服务器中jato.pageSession的Java反序列化漏洞。攻击者通过访问/ccversion/*来触发漏洞绕过身份验证。

![Figure 15. ForgeRock OpenAM insecure deserialization
vulnerability.](https://image.3001.net/images/20210930/1633010042_6155c17a50aebd0b230c1.png!small)

## 攻击数据分析

按类别对每种网络攻击进行了分类，并在下表中对它们进行了排序。

![1633009682_6155c012823848f71e367.png!small?1633009682353](https://image.3001.net/images/20210930/1633009682_6155c012823848f71e367.png!small?1633009682353)

![1633009706_6155c02a68d0ce5fbceb2.png!small?1633009706318](https://image.3001.net/images/20210930/1633009706_6155c02a68d0ce5fbceb2.png!small?1633009706318)

攻击来源：

![In our monitoring of network security trends, we identified the regions from
which each network attack appeared to originate. In order, these were: United
States, China, Russian Federation, India, the Netherlands, Germany, Albania,
Korea, Hong Kong, United Kingdom, Brazil, Panama, Bulgaria, Vietnam, Lebanon,
Syrian Arab Republic, France, Turkey, Indonesia, Georgia and
others.](https://image.3001.net/images/20210930/1633010044_6155c17ce9cda0327a893.png!small)

## 原文链接

[unit42](https://unit42.paloaltonetworks.com/network-security-trends/)

