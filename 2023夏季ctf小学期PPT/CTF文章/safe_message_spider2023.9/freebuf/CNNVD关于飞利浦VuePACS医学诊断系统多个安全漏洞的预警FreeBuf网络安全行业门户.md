7月14日，国家信息安全漏洞库（CNNVD）发布了《关于飞利浦 Vue
PACS医学诊断系统多个安全漏洞的预警》，华云安作为CNNVD技术支撑单位为此漏洞通报提供支持。

近日，飞利浦官方发布了多个安全漏洞的公告，包括Philips Vue PACS
安全漏洞（CNNVD-202107-242、CVE-2021-33020）、Philips Vue
PACS加密问题漏洞（CNNVD-202107-238、CVE-2021-33018）等。成功利用漏洞的攻击者可以对飞利浦Vue
PACS医学诊断系统发送恶意请求、获取用户敏感信息，导致系统无法正常工作，最终控制目标系统。VUE Picture Archiving and
Communication Systems 12.2.x.x及以下版本、Vue MyVue 12.2.x.x及以下版本、Vue Speech
12.2.x.x及以下版本、Vue Motion
12.2.1.5及以下版本均受漏洞影响。目前，飞利浦官方已经发布了解决方案修复了漏洞，建议用户及时确认是否受到漏洞影响，尽快采取修补措施。

##  **一、漏洞介绍**

飞利浦 Vue
PACS是飞利浦公司的一款医学诊断平台，多用于公共医疗健康领域的基础设施。2021年7月12日，飞利浦官方发布了多个安全漏洞的公告，详细信息如下：

序号| 漏洞名称| 漏洞编号| 漏洞简介  
---|---|---|---  
1| Philips Vue PACS 安全漏洞| （CNNVD-202107-242、CVE-2021-33020）|
漏洞源于该平台使用过期的安全密钥，导致攻击者可以通过使用曾经泄露的密钥对系统发起攻击。  
2| Philips Vue PACS 安全漏洞| （CNNVD-202107-238、CVE-2021-33018）|
该漏洞源于使用了存在安全隐患的加密算法，导致攻击者可以利用针对加密算法的漏洞对平台发起攻击。  
3| Philips Vue PACS 安全漏洞| （CNNVD-202107-235、CVE-2021-27497）|
该漏洞源于产品未使用或错误地使用保护机制，对其提供针对产品的定向攻击的充分防御。  
4| Philips Vue PACS 安全漏洞| （CNNVD-202107-245、CVE-2021-27493）|
由于对用户提供的数据没有进行严格过滤，攻击者可通过构造特制的请求包触发该漏洞，进而在目标平台上执行恶意代码。  
5| Philips Vue PACS 安全漏洞| （CNNVD-202107-250、CVE-2021-33024）|
该漏洞源于产品传输或存储身份验证凭据时使用了不安全的方法，容易受到未经授权的拦截或检索。  
6| Philips Vue PACS 安全漏洞| （CNNVD-202107-248、 CVE-2021-33022）|
该漏洞源于软件以明文方式传输敏感或对安全至关重要的数据，这种通信通道可以被未经授权的攻击者嗅探到。  
  
##  **二、危害影响**

成功利用漏洞的攻击者可以对飞利浦Vue PACS诊疗平台发送恶意请求、获取用户敏感信息，导致平台无法正常工作，最终控制目标系统。VUE Picture
Archiving and Communication Systems 12.2.x.x及以下版本、Vue MyVue 12.2.x.x及以下版本、Vue
Speech 12.2.x.x及以下版本、Vue Motion 12.2.1.5及以下版本均受漏洞影响。飞利浦 Vue
PACS医学诊断系统在全球范围内拥有大量用户，主要部署在内网中使用。

##  **三、修复建议**

目前，飞利浦官方已经发布了解决方案修复了漏洞，建议用户及时确认是否受到漏洞影响，尽快采取修补措施。官方链接如下：

[https://www.philips.com/a-w/security/security-advisories.html#security_advisories](https://link.zhihu.com/?target=https%3A//www.philips.com/a-w/security/security-advisories.html%23security_advisories)

CNNVD将继续跟踪上述漏洞的相关情况，及时发布相关信息。如有需要，可与CNNVD联系。联系方式:
[cnnvd@itsec.gov.cn](mailto:cnnvd@itsec.gov.cn)

​原文链接：https://mp.weixin.qq.com/s/1En1JKEG_sWFWbMEMMnoYw

