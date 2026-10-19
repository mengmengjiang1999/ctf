***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

## 前言

 **Microsoft SQL Server
是微软公司推出的关系型数据库管理系统,因其具有使用方便与可伸缩性好，且与相关软件集成程度高等优点,从而被广泛使用。Microsoft SQL Server
数据库引擎为关系型数据和结构化数据提供了更安全可靠的存储功能，可以构建和管理对高可用和高性能有需求的业务业务场景。**

## 0x01 Microsoft SQL Server数据库简介

目前Microsoft SQL Server数据库在全球的应用量也比较靠前，据统计，在全球范围内对互联网开放Microsoft SQL
Server数据库服务的资产数量多达237,065台，发现中国地区对外开放的Microsoft SQL
Server数据库服务数量排名第一，数量为75793台，接近全球总量的30%。排名第二与第三的分别是美国与荷兰地区，其对外开放的Microsoft SQL
Server数据库服务数量分别为35,965台和33,664台。由此看来，国内使用Microsoft SQL
Server数据库的用户很广泛，对Microsoft SQL Server数据库的漏洞防范就显得尤为重要了。

![Microsoft SQL
Server数据库](https://image.3001.net/images/20181109/1541744348_5be526dcdd4d1.png!small)

(统计数据仅为对互联网开放的资产，本数据来源于FOFA )

## 0x02 Microsoft SQL Server漏洞概述

近几年Microsoft SQL
Server数据库爆发的漏洞数量与其它类型数据库相比，所暴露出来的漏洞相对较少。在此，挑选两个可利用性高，且具有代表性的漏洞进行分析，分析列表如下：

**漏洞名称** | **漏洞类型** | **风险级别** | **CVE编号**  
---|---|---|---  
Microsoft SQL Server sp_replwritetovarbin远程堆溢出漏洞 | 缓冲区溢出 | 高 | CVE-2008-5416  
Lyris ListManager MSDE SA弱密码漏洞 | 弱密码 | 中 | CVE-2005-4145  
  
## 0x03 Microsoft SQL Server漏洞分析

### 一、CVE-2008-5416漏洞分析

 **1、漏洞信息：**

> 漏洞名称：Microsoft SQL Server sp_replwritetovarbin Stored Procedure Buffer
> Overflow Vulnerability
>
> 漏洞编号： CVE-2008-5416
>
> 漏洞类型： Buffer Overflow Vulnerability

 **2、漏洞概述：**

Microsoft SQL Server是一款流行的SQL数据库系统。Microsoft SQL
Server的sp_replwritetovarbin扩展存储过程中存在堆溢出漏洞，如果远程攻击者在参数中提供了未初始化变量的话，就可以触发这个溢出，向可控的位置写入内存，导致已有漏洞SQL
Server进程的权限执行任意代码。在默认的配置中，任何用户都可以访问sp_replwritetovarbin过程。通过认证的用户可以通过直接的数据库连接或SQL注入来利用这个漏洞。

 **3、漏洞影响：**

Microsoft SQL Server 受CVE-2008-5416漏洞影响的版本如下：

![Microsoft SQL
Server漏洞分析](https://image.3001.net/images/20181109/1541744407_5be527175adcb.png!small)

 **4、漏洞分析：**

1）CVE-2008-5416漏洞PoC利用代码分析：

我们从互联网中找到了CVE-2008-5416漏洞PoC，如下是漏洞PoC利用代码片段：

![Microsoft SQL
Server漏洞分析](https://image.3001.net/images/20181109/1541744427_5be5272b43a24.png!small)

通过PoC代码可以看出，先定义未初始化的自定义变量，然后传入超长数据段(数据段中可构造恶意攻击代码)，通过sp_replwritetovarbin扩展在存储过程中进行堆溢出，将构造的攻击代码写入内存并执行。

2）CVE-2008-5416漏洞攻击流量分析：

攻击者TDS协议对靶机发起远程登陆认证请求，因为该漏洞只有远程认证成功后才可以进一步被利用。如下所示：

![Microsoft SQL
Server漏洞分析](https://image.3001.net/images/20181109/1541744447_5be5273f53db2.png!small)

当登陆请求认证成功后，进一步查询数据库服务器的版本信息。如下所示：

![](https://image.3001.net/images/20181109/1541744457_5be527498397d.png!small)

在确定数据库系统的版本信息后，再进一步选择对应的攻击PayLoad载荷，进行存储过程溢出攻击。如下所示：

![](https://image.3001.net/images/20181109/1541744467_5be527535503d.png!small)

 **5、漏洞验证：**

通过Metasploit渗透测试框架对存在CVE-2008-5416漏洞的靶机进行测试，发现可以利用成功。如下图所示：

![Microsoft SQL
Server漏洞分析](https://image.3001.net/images/20181109/1541744509_5be5277db838f.png!small)

 **6、漏洞修复建议：**

Microsoft已经为此发布了一个安全公告（MS09-004）以及相应补丁。链接如下:

> <https://docs.microsoft.com/zh-cn/security-> updates/Securitybulletins/2009/ms09-004>

### 二、CVE-2005-4145漏洞分析：

 **1、漏洞信息：**

> 漏洞名称：Lyris ListManager MSDE Weak SA Password Vulnerability
>
> 漏洞编号：CVE-2005-4145
>
> 漏洞类型：Weak Password Vulnerability

 **2、漏洞概述：**

Lyris_technologies_inc Listmanager是Microsoft SQL
ServerMSDE中的一款重要组件，由于Lyris_technologies_inc
Listmanager5.0-8.9b版本中存在将数据库的SA帐户配置为使用具有小型搜索空间的密码的设计缺陷，导致攻击者可远程通过暴力破解攻击获取Microsoft
SQL Server数据库的访问权。

 **3、漏洞影响：**

Lyris_technologies_inc Listmanager受CVE-2005-4145漏洞影响的版本如下：

![漏洞影响](https://image.3001.net/images/20181109/1541744542_5be5279eee714.png!small)

 **4、漏洞分析：**

1）漏洞PoC代码分析：

我们从互联网中找到了CVE-2005-4145漏洞PoC，如下是漏洞PoC利用代码片段：

![漏洞分析](https://image.3001.net/images/20181109/1541744561_5be527b1ad7d2.png!small)

从上面的漏洞PoC代码可以看出，先尝试使用账号SA，密码lminstall进行尝试登陆，如成功，就执行下面的SQL利用代码，否则，进一步对SA账户进行进程PID暴力枚举来获取登陆权限，如登陆成功，同理，执行下面的SQL利用代码。

2）CVE-2005-4145漏洞PoC数据包分析：

攻击者通过TDS协议对靶机不停的发起远程登陆认证请求，用户名为SA，不停的枚举密码。

![CVE-2005-4145漏洞PoC数据包分析](https://image.3001.net/images/20181109/1541744591_5be527cfc11a6.png!small)

 **5、漏洞验证：**

通过Metasploit渗透测试框架对存在CVE-2005-4145漏洞的靶机进行测试，发现可以利用成功。如下图所示：

![漏洞验证](https://image.3001.net/images/20181109/1541744600_5be527d8cd00f.png!small)

技巧提示：CVE-2005-4145漏洞PoC通过默认账号或指定账号的方式来进行枚举测试，由于代码实现比较简单，也比较鸡肋。我们可自行通过Hydra等工具枚举成功后，再将枚举成功的值填写Password字段中，然后进一步快速深度利用。

 **6、漏洞修复建议：**

目前，官方已经在Lyris_technologies_inc Listmanager 8.9b版本修复了此漏洞，可自行升级到8.9b及以上版本。

## 0x04 结语

通过对Microsoft SQL Server进行一些列的梳理和分析，可以从以下几个维度进行归纳和总结：

> 1、高危漏洞主要分布在：Microsoft SQL Server7、Microsoft SQL Server2000、Microsoft SQL
> Server2005这三个版本。
>
> 2、影响范围比较广的漏洞类型有：缓冲区溢出漏洞、弱密码、权限提升、拒绝服务等四种。
>
> 3、Microsoft SQL Server高危漏洞的触发条件比较苛刻，基本上都需要先通过账号进行登陆才能进一步利用。
>
> 4、Microsoft SQL
> Server类漏洞比较集中爆发的时期是1997年至2005年这8年。随着微软对安全性越来越重视，在随后发布的Microsoft SQL
> Server2008及之后版本中存在的高危安全性问题越来越少。

 ***本文作者：千里目安全实验室，转载请注明来自FreeBuf.COM**

