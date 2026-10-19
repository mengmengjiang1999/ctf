Advantech
WebAccess是中国台湾研华（Advantech）公司的一套基于浏览器架构的HMI/SCADA软件，该软件支持动态图形显示和实时数据控制，并提供远程控制和管理自动化设备的功能。

## Part1 漏洞状态

漏洞细节| 漏洞POC| 漏洞EXP| 在野利用  
---|---|---|---  
有| 有| 有| 无  
  
## Part2 漏洞描述

Advantech WebAccess
8.1_20160519及之前版本存在认证收集泄露，要利用此漏洞，首先需要通过身份验证。该漏洞存在于upAdminPg.asp中，一个通过身份验证的管理员可以查看其他管理员包括系统管理员（admin）的密码，攻击者可以利用此漏洞升级权限。

![v2-d53f7ec160e98cd1782af93f99ba9171_720w.jpg](https://image.3001.net/images/20220428/1651122888_626a22c8c3737d73f790e.jpg!small)漏洞名称|
Advantech WebAccess8.1-认证收集漏洞  
---|---  
CVE编号| CVE-2016-5810  
漏洞类型| 信息泄露  
漏洞等级| 低危（4.0）  
公开状态| 公开  
时间线| 2016.05.11 – 漏洞报告给供应商2016.07.18 – 漏洞公开发布  
  
## Part3 漏洞复现

1\.
实验环境渗透主机：kali(192.168.33.129)目标主机：winserver2008R2(192.168.33.139)软件版本：AdvantechWebAccess
8.02. 涉及工具meterasploit 3. 复现步骤1）启动环境,目标主机启动,如下图：

![v2-71581d5e5f497d59c61e9bfe0292ee84_720w.jpg](https://image.3001.net/images/20220428/1651122889_626a22c91d9410673432b.jpg!small)

2）攻击者通过渗透主机（Kali）启动终端，之后启动msfconsole，终端输入如下：

search Advantech

use 1

![v2-0b7f736a784ef8dedccea1f10a308446_720w.jpg](https://image.3001.net/images/20220428/1651122889_626a22c96a80492bee1cd.jpg!small)![v2-24bec8c83752edc3b77f4d86ade0ad89_720w.jpg](https://image.3001.net/images/20220428/1651122889_626a22c9aa8089b402c22.jpg!small)

设置参数，并攻击，如下：

![v2-7a873f33aeea333affba3405e1762319_720w.jpg](https://image.3001.net/images/20220428/1651122889_626a22c9ee937778931a1.jpg!small)

发现已获取所有管理员包括系统管理员（admin）的账户、密码。

## Part4 漏洞分析

通过分析代码发现在broadweb/upAdmin.asp中代码第144行、150行可以发现返回结果中可返回其password。

![v2-41fca9c604a012c365148435ab3857c9_720w.jpg](https://image.3001.net/images/20220428/1651122890_626a22ca646047a86765b.jpg!small)

## Part5 修复建议

升级到研华WebAccess8.2或更高版本。

 **获取更多情报**

联系我们，获取更多漏洞情报详情及处置建议，让企业远离漏洞威胁。  
电话：18511745601

邮箱 ：shiliangang@andisec.com

