***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 **近日，Spring官方团队在最新的安全更新中披露了一则Spring Cloud Config目录遍历漏洞（CVE-2019-3799）。漏洞官方定级为
High，属于高危漏洞。该漏洞本质是允许应用程序通过spring-cloud-config-server模块获取任意配置文件,攻击者可以构造恶意URL实现目录遍历漏洞的利用。** **  
**

##  **Spring产品介绍**

Spring是一个Java/Java
EE/.NET的分层应用程序框架。它是一个基于IOC和AOP构架多层J2EE系统的开源框架，模块化好且实现了很优雅的MVC，对不同的数据访问技术提供了统一的接口。此外它采用的IOC可以很容易的实现Bean的装配，提供的AOP简洁易用并据此实现了Transaction
Management等功能。Spring
提供简易的开发方式，这种开发方式，将避免那些可能致使底层代码变得繁杂混乱的大量属性文件和帮助类。目前此框架的使用非常活跃。Spring
Data是Spring框架中提供底层数据访问的项目模块，Spring Data Commons是一个共用的基础模块。 **  
**

##  **漏洞分析**

CVE-2019-3799漏洞原理：由于spring-cloud-config-server模块未对传入路径进行安全限制，攻击者可以利用多个..%252f进行目录遍历，查看服务器其他路径的敏感文件，造成敏感信息泄露。

官方修复补丁如下：

![Spring Cloud
Config目录遍历漏洞（CVE-2019-3799）预警](https://image.3001.net/images/20190418/1555589108_5cb867f4e55b3.png!small)

通过补丁对比发现，官方最新版本加入了isInvalidEncodedPath方法，对传入的url进行判断，若存在%，则对传入的url进行url解码。阻止了攻击者通过url编码绕过对../的检测。

![Spring Cloud
Config目录遍历漏洞（CVE-2019-3799）预警](https://image.3001.net/images/20190418/1555589119_5cb867ff34e7a.png!small)新添加的isInvalidPath方法则是对url中关键词进行检测，如果存在WEB-INF，META-INF，..，../，则会触发warning。

##  **漏洞复现**

下载一个存在漏洞的 Spring Cloud Config，下载地址如下：

> <https://github.com/spring-cloud/spring-cloud-config>

启动环境后，使用get方法传入/test/pathtraversal/master/..%252f..%252f..%252f..%252f../etc/passwd，即可读取到linux下passwd文件信息。

## ![Spring Cloud
Config目录遍历漏洞（CVE-2019-3799）预警](https://image.3001.net/images/20190418/1555589133_5cb8680d61299.png!small)
**影响范围**

目前据统计，在全球范围内对互联网开放Spring服务器的资产数量多达5万多台，其中归属中国地区的受影响资产数量为28000台以上。

目前受影响的Spring Cloud Config 版本：

> Spring Cloud Config 2.1.0 to 2.1.1
>
> Spring Cloud Config 2.0.0 to 2.0.3
>
> Spring Cloud Config 1.4.0 to 1.4.5

##  **修复建议**

Spring官方最新版本已经对Spring Cloud Config目录遍历漏洞进行了修复，下载地址：<https://github.com/spring-cloud/spring-cloud-config/releases>

##  **参考链接**

<https://pivotal.io/security/cve-2019-3799>

 ***本文作者：深信服千里目安全实验室，转载请注明来自FreeBuf.COM**

