***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 **近日，国家信息安全漏洞库（CNNVD）收到关于Apache Struts2
S2-057安全漏洞（[CNNVD-201808-740](http://www.cnnvd.org.cn/web/xxk/ldxqById.tag?CNNVD=CNNVD-201808-740)、CVE-2018-11776）情况的报送。成功利用漏洞的攻击者可能对目标系统执行恶意代码。Apache
Struts 2.3–Apache Struts 2.3.34、ApacheStruts 2.5–Apache Struts
2.5.16等版本均受此漏洞影响。**

目前，Apache官方已经发布了版本更新修复了该漏洞。建议用户及时确认Apache Struts产品版本，如受影响，请及时采取修补措施。

##  **一、漏洞介绍**

Apache Struts2是美国阿帕奇（Apache）软件基金会下属的Jakarta项目中的一个子项目，是一个基于MVC设计的Web应用框架。

2018年8月22日，Apache官方发布了Apache Struts2
S2-057安全漏洞（[CNNVD-201808-740](http://www.cnnvd.org.cn/web/xxk/ldxqById.tag?CNNVD=CNNVD-201808-740)、CVE-2018-11776）。当在struts2开发框架中启用泛namespace功能，并且使用特定的result时，会触发远程代码执行漏洞。

##  **二、危害影响**

成功利用该漏洞的攻击者，可以在目标系统中执行恶意代码。Apache Struts 2.3–Apache Struts2.3.34、Apache
Struts2.5–Apache Struts 2.5.16等版本等均受此漏洞影响。

##  **三、修复建议**

目前，Apache官方已经发布了版本更新修复了该漏洞。建议用户及时确认Apache Struts产品版本，如受影响，请及时采取修补措施。漏洞修补措施如下：

升级到struts2 2.3.35 或者 struts2 2.5.17

[https://cwiki.apache.org/confluence/display/WW/S2-057?from=timeline&isappinstalled=0](https://cwiki.apache.org/confluence/display/WW/S2-057?from=timeline&isappinstalled=0)

本通报由CNNVD技术支撑单位——安恒信息技术有限公司、远江盛邦（北京）网络安全科技股份有限公司等提供支持。

CNNVD将继续跟踪上述漏洞的相关情况，及时发布相关信息。如有需要，可与CNNVD联系。

联系方式: [cnnvd@itsec.gov.cn](mailto:cnnvd@itsec.gov.cn)

 ***本文作者：CNNVD，转载请注明来自FreeBuf.COM**  

