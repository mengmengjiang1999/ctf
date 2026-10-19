***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

**![](https://gss3.bdstatic.com/7Po3dSag_xI4khGkpoWK1HF6hhy/baike/crop%3D0%2C126%2C745%2C491%3Bc0%3Dbaike92%2C5%2C5%2C92%2C30/sign=b72bea483badcbef157b2446919f02ec/359b033b5bb5c9ea7247d06fdf39b6003bf3b382.jpg)**

 **Oracle
FusionMiddleware（Oracle融合中间件）是美国甲骨文（Oracle）公司的一套面向企业和云环境的业务创新平台。该平台提供了中间件、软件集合等功能。Oracle
WebLogic Server是其中的一个适用于云环境和传统环境的应用服务器组件。**

Oracle官方发布了4月份的关键补丁更新CPU（Critical
PatchUpdate），其中包含一个高危的Weblogic反序列化漏洞(CVE-2018-2628)，该漏洞修补不善导致被绕过。Oracle
官方发布的7月份补丁中修复了该漏洞，分配了漏洞编号CVE-2018-2893。

通过该漏洞，攻击者可以在未授权的情况下远程执行代码。攻击者只需要发送精心构造的T3协议数据，就可以获取目标服务器的权限。攻击者可利用该漏洞控制组件，影响数据的可用性、保密性和完整性。

## 影响范围

Oracle WebLogic Server 10.3.6.0

Oracle WebLogic Server 12.1.3.0

Oracle WebLogic Server 12.2.1.2

Oracle WebLogic Server 12.2.1.3

以上均为官方支持的版本。

## 修复方案

1.Oracle 官方已经在 7 月份中的补丁中修复了该漏洞，建议受影响的用户尽快升级更新。

下载地址：<http://www.oracle.com/technetwork/security-advisory/cpujul2018-4258247.html>  

2.根据业务需求选择禁用T3协议。

此漏洞产生于WebLogic的T3服务，因此可通过控制T3协议的访问来临时阻断针对该漏洞的攻击。当开放WebLogic控制台端口（默认为7001端口）时，T3服务会默认开启。

具体操作：

（1）进入WebLogic控制台，在base_domain的配置页面中，进入“安全”选项卡页面，点击“筛选器”，进入连接筛选器配置。

（2）在连接筛选器中输入：weblogic.security.net.ConnectionFilterImpl，在连接筛选器规则中输入：127.0.0.1
* * allow t3 t3s，0.0.0.0/0 * *deny t3 t3s（t3和t3s协议的所有端口只允许本地访问）。

（3）保存后需重新启动。

## 参考

> <http://www.oracle.com/technetwork/security-> advisory/cpujul2018-4258247.html>
>
> <http://www.cnvd.org.cn/flaw/show/CNVD-2018-13334>  
>

