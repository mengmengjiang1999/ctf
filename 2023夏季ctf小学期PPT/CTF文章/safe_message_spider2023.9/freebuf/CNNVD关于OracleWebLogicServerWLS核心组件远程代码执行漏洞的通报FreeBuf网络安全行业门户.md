***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 **近日，国家信息安全漏洞库（CNNVD）收到Oracle WebLogic Server
WLS核心组件远程代码执行漏洞（CNNVD-201807-1276、CVE-2018-2893）情况的报送。**

远程攻击者可利用该漏洞在未授权的情况下发送攻击数据，通过T3协议在WebLogic
Server中执行反序列化操作,实现任意代码执行。该漏洞是由于Oracle一个历史漏洞WeblogicServer反序列化漏洞（CNNVD-201804-803、CVE-2018-2628）修补不完善导致，CNNVD已于4月发布了该漏洞预警。WebLogic
Server
10.3.6.0、12.1.3.0、12.2.1.2、12.2.1.3等版本均受漏洞影响。目前，Oracle官方已发布补丁修复了该漏洞，建议用户及时确认是否受到漏洞影响，尽快采取修补措施。

## 一、漏洞介绍

Oracle WebLogic
Server是美国甲骨文（Oracle）公司开发的一款适用于云环境和传统环境的应用服务中间件，它提供了一个现代轻型开发平台，支持应用从开发到生产的整个生命周期管理，并简化了应用的部署和管理。在WebLogic
的 RMI（远程方法调用）通信中，T3协议用来在 WebLogic Server 和其他 Java
程序间传输数据，该协议在开放WebLogic控制台端口的应用上默认开启。

北京时间7月18日凌晨，Oracle官方发布了7月份关键补丁更新CPU（Critical Patch
Update），其中修复了一个在4月份CPU补丁中未能完全修复的WeblogicServer反序列化漏洞（CNNVD-201804-803、CVE-2018-2628）。攻击者可以在未经授权的情况下，远程发送攻击数据，通过T3协议在WebLogic
Server中执行反序列化操作，反序列过程中会远程加载RMI registry，加载回来的registry又会被反序列化执行，最终实现了远程代码的执行。

## 二、危害影响

攻击者可利用漏洞在未授权的情况下远程发送攻击数据，通过T3协议在WebLogic
Server中执行反序列化操作,最终实现远程代码执行。该漏洞涉及了多个版本，具体受影响版本如下：

##  ** 三、修复建议**

目前，Oracle官方已经发布补丁修复该漏洞，请用户及时检查产品版本，如确认受到漏洞影响，可安装补丁进行防护。

1、Oracle官方更新链接如下：

<http://www.oracle.com/technetwork/security-advisory/cpujul2018-4258247.html>

2、临时解决方案

通过设置weblogic.security.net.ConnectionFilterImpl默认连接筛选器，对T3/T3s协议的访问权限进行配置，阻断漏洞利用途径。具体如下：

> （a）进入WebLogic控制台，在base_domain的配置页面中，进入“安全”选项卡页面，点击“筛选器”，进入连接筛选器配置。
>
> （b）在连接筛选器中输入：WebLogic.security.net.ConnectionFilterImpl，在连接筛选器规则中输入：* * 7001
> deny t3 t3s
>
> （c）保存后规则即可生效，无需重新启动。

本通报由CNNVD技术支撑单位——启明星辰信息技术有限公司(积极防御实验室)、上海斗象信息科技有限公司、[北京天融信网络安全技术有限公司](https://baike.baidu.com/item/%E5%8C%97%E4%BA%AC%E5%A4%A9%E8%9E%8D%E4%BF%A1%E7%BD%91%E7%BB%9C%E5%AE%89%E5%85%A8%E6%8A%80%E6%9C%AF%E6%9C%89%E9%99%90%E5%85%AC%E5%8F%B8)、北京神州绿盟信息安全科技股份有限公司、北京数字观星科技有限公司提供支持。

CNNVD将继续跟踪上述漏洞的相关情况，及时发布相关信息。如有需要，可与CNNVD联系。

联系方式: cnnvd@itsec.gov.cn

