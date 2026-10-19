**代码审计是使用静态分析发现源代码中安全缺陷的方法，能够辅助开发或测试人员在软件上线前较为全面地了解其安全问题，防患于未然，因此一直以来都是学术界和产业界研究的热点，并且已经成为安全开发生命周期
SDL 和 DevSecOps 等保障体系的重要技术手段。**  

360代码卫士团队基于自主研发的国内首款源代码安全检测商用工具，以及十余年漏洞技术研究的积累，推出“缺陷周话”系列栏目。每周针对 CWE、OWASP
等标准中的一类缺陷，结合实例和工具使用进行详细介绍，旨在为广大开发和安全人员提供代码审计的基础性标准化教程。

上一期给大家了解了空解指针【[传送门](http://www.freebuf.com/articles/rookie/183889.html)】的应用，本期继续带来SQL注入的介绍。

## 一、SQL 注入

所谓 SQL 注入，就是通过将 SQL 命令插入应用程序的 http 请求中，并在服务器端被接收后用于参与数据库操作，最终达到欺骗服务器执行恶意的 SQL
命令的效果。理论上来讲，应用程序中只要是与数据库有数据交互的地方，无论是增删改查，如果数据完全受用户控制，而应用程序又处理不当，那么这些地方都是可能存在
SQL 注入的。目前几乎所有的开发语言如：JAVA、PHP、Python、ASP
等都可以使用SQL数据库来存放数据，处理不当就可能导致SQL注入问题的发生。本篇文章以 JAVA 语言源代码为例，分析 SQL
注入产生的原因以及修复方法。SQL 注入详细请见 CWE-89: Improper Neutralization of Special Elements
used in an SQL Command ('SQL
Injection')（<http://cwe.mitre.org/data/definitions/89.html>）。

## 二、SQL 注入的危害

恶意攻击者除了可以利用 SQL
注入漏洞获取数据库中的信息（例如，管理员后台密码、站点的用户个人信息）之外，甚至在数据库权限足够的情况下可以向服务器中写入一句话木马，从而获取
webshell 或进一步获取服务器系统权限。

2017年1月至2018年9月，CVE 中共有793条漏洞信息与其相关。部分 CVE如下：

CVE-2018-13050 | Zoho ManageEngineApplications Manager 13.x 中存在 SQL 注入漏洞，通过 /
j_security_check POST 请求中的 j_username 参数可以注入sql语句。  
---|---  
CVE-2017-16542  
| Zoho ManageEngineApplications Manager 13
程序可以通过manageApplications.do?method=insert 请求中的 name 参数进行 SQL 注入。  
CVE-2017-16849 | Zoho ManageEngine Applications Manager 13允许通过
/MyPage.do?method=viewDashBoard 中的forpage 参数进行SQL注入。  
CVE-2017-5570  
| 在 eClinicalWorks Patient Portal 7.0 build 13 中发现MessageJson.jsp
中存在的盲注，但是只能由经过身份验证的用户通过发送HTTP POST请求来利用。并且恶意攻击者可以通过该漏洞使用诸如select_loadfile()
之类的方法将数据库数据转储到恶意服务器。  
  
## 三、示例代码

### 3.1 缺陷代码

本章节中使用示例代码来源于Samate Juliet Test Suite for Java v1.3
(<https://samate.nist.gov/SARD/testsuite.php>)，源文件名：CWE89_SQL_Injection__connect_tcp_execute_01.java。

![image.png](https://image.3001.net/images/20180917/1537176535_5b9f73d71b581.png!small)

![image.png](https://image.3001.net/images/20180917/1537176550_5b9f73e6d5038.png!small)

在上述代码可以看到数据在 54 行被污染，在第 58 行中将污染数据传递给`data`，并未经任何安全处理就在第 115 行中直接用于 SQL
拼接，且参与数据库操作，从而导致 SQL 注入的产生。

使用 360 代码卫士对上述示例代码进行检测，可以在文件第 115
行检出“SQL注入”缺陷，显示等级为高，同时，提供跟踪路径可以清晰分析缺陷产生的过程。如图1、图2所示：

![image.png](https://image.3001.net/images/20180917/1537176573_5b9f73fd784da.png!small)

图1 SQL 注入检出缺陷的 source 点

![image.png](https://image.3001.net/images/20180917/1537176593_5b9f74110b847.png!small)

图2 SQL 注入检出缺陷的 sink 点

### 3.2 修复代码

![image.png](https://image.3001.net/images/20180917/1537176786_5b9f74d2456e3.png!small)

在上述修复代码中的第 305 行，执行 SQL
时采用的预编译，使用参数化的语句，用户的输入就被限制于一个参数当中。通过图3可以看出，360代码卫士对修复后的代码并未检出。

![image.png](https://image.3001.net/images/20180917/1537176628_5b9f7434150dd.png!small)

图3 SQL注入修复示例

## 4、如何避免SQL注入

 **常见的修复方法：**

1\. 使用预编译处理输入参数：要防御 SQL 注入，用户的输入就不能直接嵌套在 SQL
语句当中。使用参数化的语句，用户的输入就被限制于一个参数当中。如下所示：

![image.png](https://image.3001.net/images/20180917/1537176802_5b9f74e2e5260.png!small)

2\.
输入验证：检查用户输入的合法性，以确保输入的内容为正常的数据。数据检查应当在客户端和服务器端都执行，之所以要执行服务器端验证，是因为客户端的校验往往只是减轻服务器的压力和提高对用户的友好度，攻击者完全有可能通过抓包修改参数或者是获得网页的源代码后，修改验证合法性的脚本（或者直接删除脚本），然后将非法内容通过修改后的表单提交给服务器等等手段绕过客户端的校验。因此，要保证验证操作确实已经执行，唯一的办法就是在服务器端也执行验证。但是这些方法很容易出现由于过滤不严导致恶意攻击者可能绕过这些过滤的现象，需要慎重使用。

3\. 错误消息处理：防范 SQL 注入，还要避免出现一些详细的错误消息，恶意攻击者往往会利用这些报错信息来判断后台 SQL
的拼接形式，甚至是直接利用这些报错注入将数据库中的数据通过报错信息显示出来。

4.加密处理：将用户登录名称、密码等数据加密保存。加密用户输入的数据，然后再将它与数据库中保存的数据比较，这相当于对用户输入的数据进行了“消毒”处理，用户输入的数据不再对数据库有任何特殊的意义，从而也就防止了攻击者注入
SQL 命令。

 ***本文作者：360代码卫士，转载请注明来自FreeBuf.COM**

