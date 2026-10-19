近期，研究人员发现与Interactish开源服务相关的漏洞攻击行为，此工具可以生成特定域名来帮用户测试攻击是否成功。研究人员可以在漏洞利用程序中插入Interacticsh来检查PoC是否工作。

##  **Interactsh** **工具**

研究人员在2021年4月中旬发现，恶意负载中存在一些使用相同域名但不同子域的攻击行为。经过调查发现其源代码是一个可以生成特定URL的工具，用于测试DNS查询和HTTP连接。该工具于2021年4月16日公开源码，4月18日第一次发现该工具。

![1634745888_61703e202bb67be24fd06.png!small?1634745881425](https://image.3001.net/images/20211021/1634745888_61703e202bb67be24fd06.png!small?1634745881425)

研究人员通过web界面随机生成了一个Interactsh连接：

> ‘C4mqgxkyedf0000ar3d0gnkmaqayyyyyb[.]interact[.]sh’

![1634745931_61703e4be633bc7f19c8a.png!small?1634745925139](https://image.3001.net/images/20211021/1634745931_61703e4be633bc7f19c8a.png!small?1634745925139)

若外部访问此URL，在web界面中可显示访问记录，安装客户端后可直接在命令中使用URL。

##  **Interaction** **测试**

攻击者和研究人员可以使用此工具测试攻击是否成功。

![1634745952_61703e60741263b36560f.png!small?1634745945930](https://image.3001.net/images/20211021/1634745952_61703e60741263b36560f.png!small?1634745945930)

测试样例

样例为物联网设备远程命令执行漏洞。攻击者发送HTTP
post请求，使用wget命令访问通过Interacticsh创建的C2服务器。可通过观察C2服务器是否收到请求，确定此攻击是否成功。

##  **Interactish** **漏洞利用**

4月18日，发现该工具被使用。其中有许多简单的命令注入，都与特定的CVE（如下表）有关。另外还发现了大规模的扫描从一组IP地址发送，相同的C2服务器。

CVE Number

|

Severity

|

Category

|

Hit Counts  
  
---|---|---|---  
  
CVE-2017-9506

|

Medium

|

Server-Side Request Forgery (SSRF)

|

1,132  
  
CVE-2017-12629

|

Critical

|

Remote Code Execution

|

663  
  
CVE-2019-2767

|

High

|

Authentication Bypass (Insert Data)

|

192  
  
CVE-2021-33544

|

High

|

Remote Code Execution

|

163  
  
CVE-2021-32819

|

High

|

Remote Code Execution

|

51  
  
CVE-2012-1301

|

Critical

|

Server-Side Request Forgery (SSRF)

|

13  
  
CVE-2018-1000600

|

High

|

Server-Side Request Forgery (SSRF)

|

11  
  
CVE-2021-27905

|

Critical

|

Server-Side Request Forgery (SSRF)

|

9  
  
CVE-2020-28188

|

Critical

|

Remote Code Execution

|

7  
  
CVE-2018-15517

|

High

|

Server-Side Request Forgery (SSRF)

|

6  
  
CVE-2009-4223

|

N/A

|

PHP Remote File Inclusion

|

5  
  
CVE-2019-18394

|

Critical

|

Server-Side Request Forgery (SSRF)

|

5  
  
CVE-2021-27886

|

Critical

|

Remote Code Execution

|

3  
  
CVE-2020-13379

|

High

|

Server-Side Request Forgery (SSRF)

|

2  
  
目前记录了大约32200次Interactish访问，其中测试漏洞排名如下：

CVE Number

|

Severity

|

Category  
  
---|---|---  
  
CVE-2021-31755

|

Critical

|

Remote Code Execution  
  
CVE-2020-28871

|

Critical

|

Remote Code Execution  
  
CVE-2020-25223

|

Critical

|

Remote Code Execution  
  
CVE-2020-8813

|

High

|

Remote Code Execution  
  
CVE-2020-7247

|

Critical

|

Remote Code Execution  
  
CVE-2020-28188, CVE-2020-15568, CVE-2018-13354, CVE-2018-13338

|

Critical

|

Remote Code Execution  
  
CVE-2019-2616

|

High

|

Authentication Bypass (Insert Data)  
  
CVE-2018-16167

|

High

|

Remote Code Execution  
  
CVE-2018-14839

|

Critical

|

Remote Code Execution  
  
CVE-2016-1555

|

Critical

|

Remote Code Execution  
  
##  **Interactsh** **数据分析**

在使用Interactsh的DNS查询中发现了三个可疑IP地址：82.112.184.197、138.68.184.23、82.112.184.206，这三个IP地址都有大量的Interactish活动。

自四月以来Interactsh使用频率如下：![1634745985_61703e81c251ca2da28e3.png!small?1634745978900](https://image.3001.net/images/20211021/1634745985_61703e81c251ca2da28e3.png!small?1634745978900)

带有Interactsh链接的DNS查询分布如下图：![1634745998_61703e8ee98cf50a9b9e8.png!small?1634745992108](https://image.3001.net/images/20211021/1634745998_61703e8ee98cf50a9b9e8.png!small?1634745992108)

尽管Interactish可用于合法目的，但攻击者仍广泛的使用它来测试恶意流量。在过去几年中利用第三方开源工具测试漏洞成为新趋势。攻击者可以方便地使用开源工具，防御者很难通过服务/IP/服务器等简单规则阻止流量。

## 原文链接

[unit42](https://unit42.paloaltonetworks.com/exploits-interactsh/)

