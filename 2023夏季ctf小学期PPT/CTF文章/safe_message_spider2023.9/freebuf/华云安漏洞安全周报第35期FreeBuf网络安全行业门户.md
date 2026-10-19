根据国家信息安全漏洞库（CNNVD）统计，本周（2021.
5.17~2021.5.23）CNNVD接报漏洞1431个，信息技术产品漏洞（通用型漏洞）37个，网络信息系统漏洞（事件型漏洞）1394个；CNNVD接报漏洞预警63份，其中华云安报送预警6份，
**预警报送数量持续位居前列**
！[（数据来源于CNNVD）](https://link.zhihu.com/?target=https%3A//mp.weixin.qq.com/s%3F__biz%3DMzAxODY1OTM5OQ%3D%3D%26mid%3D2651441843%26idx%3D1%26sn%3D74c20ee83e12f2471e5cb5132be0faa1%26scene%3D21%23wechat_redirect)

本周重点关注漏洞包括：CVE-2021-29505-XStream 远程代码执行漏洞、CVE-2021-27651-Pega Infinity
密码重置漏洞、CVE-2021-1499-Cisco HyperFlex HX Data Platform
文件上传漏洞、CVE-2021-1497-Cisco HyperFlex HX Data Platform
远程命令执行漏洞、CVE-2021-20374-IBM Maximo Asset Management
跨站脚本漏洞。漏洞影响范围较广，华云安建议相关用户做好资产自查与预防工作。

##  **CVE-2021-29505-XStream 远程代码执行漏洞**

 **超危**

2021年5月17日，华云安思境安全团队发现 XStream 官方发布安全更新，披露了 XStream 组件中存在一处远程代码执行漏洞。XStream 是
Java 类库，用来将对象序列化成 XML（JSON）或反序列化为对象。XStream 是自由软件，可以在 BSD
许可证的许可下分发。该漏洞是由于在解组时处理的流包含类型信息以重新创建以前写入的对象。因此，XStream
基于这些类型信息创建新的实例。成功利用此漏洞攻击者可以操纵处理后的输入流并替换或注入对象，从而导致服务器执行任意代码。

情报来源：

[https://x-stream.github.io/download.html](https://link.zhihu.com/?target=https%3A//x-stream.github.io/download.html)

##  **CVE-2021-27651-Pega Infinity 密码重置漏洞**

 **超危**

2021年5月17日，华云安思境安全团队发现 Pega 官方发布安全更新，披露了 Pega Infinity 组件中存在一处远程命令执行漏洞。Pega
Infinity 是 PegaSystems
开发的一套完整企业软件套件，提供了基于云的解决方案，使用户可以越来越快地构建应用程序。该漏洞是由于重置密码的脆弱验证机制引起，攻击者可在未授权的情况下利用该漏洞构造恶意数据，使用本地账户的密码重置功能来绕过本地身份验证检查，导致使用重置密码后的账户进行登录。

情报来源：

[https://collaborate.pega.com/discussion/pega-security-advisory-a21-hotfix-matrix](https://link.zhihu.com/?target=https%3A//collaborate.pega.com/discussion/pega-security-advisory-a21-hotfix-matrix)

##  **CVE-2021-1499-Cisco HyperFlex HX Data Platform 文件上传漏洞**

 **中危**

2021年5月19日，华云安思境安全团队发现 Cisco 官方发布安全更新，披露了 Cisco HyperFlex 中存在一处文件上传漏洞。Cisco
HyperFlex HX Data Platform 是 Cisco
的一个网络设备，提供企业级的敏捷性，可扩展性，安全性和生命周期管理功能。该漏洞是由于缺少上传功能的身份验证，攻击者可在未授权的情况下利用该漏洞构造恶意数据进行文件上传执行攻击，最终造成代码执行。

情报来源：

[https://tools.cisco.com/security/center/content/CiscoSecurityAdvisory/cisco-sa-hyperflex-upload-KtCK8Ugz](https://link.zhihu.com/?target=https%3A//tools.cisco.com/security/center/content/CiscoSecurityAdvisory/cisco-sa-hyperflex-upload-KtCK8Ugz)

##  **CVE-2021-1497-Cisco HyperFlex HX Data Platform 远程命令执行漏洞**

 **超危**

2021年5月19日，华云安思境安全团队发现 Cisco 官方发布安全更新，披露了 Cisco HyperFlex HX Data Platform
组件中存在一处远程代码执行漏洞。该漏洞是由于 Web
的管理界面中存在命令注入漏洞，攻击者可在未授权的情况下利用该漏洞构造恶意数据执行远程代码攻击，从而获取服务器最高权限。

情报来源：

[https://tools.cisco.com/security/center/content/CiscoSecurityAdvisory/cisco-sa-hyperflex-rce-TjjNrkpR](https://link.zhihu.com/?target=https%3A//tools.cisco.com/security/center/content/CiscoSecurityAdvisory/cisco-sa-hyperflex-rce-TjjNrkpR)

##  **CVE-2021-20374-IBM Maximo Asset Management 跨站脚本漏洞**

 **中危**

2021年5月20日，华云安思境安全团队发现 IBM 官方发布安全更新，披露了 IBM Maximo Asset Management
的组件中存在一处跨站脚本漏洞。IBM Maximo Asset Management 是 IBM
的一套综合性资产生命周期和维护管理解决方案，该方案能够在一个平台上管理所有类型的资产，并对这些资产实现单点控制。成功利用此漏洞可允许攻击者在 Web UI
中嵌入任意的 JavaScript 代码，从而导致在可信会话中暴露凭据。

情报来源：

[https://www.ibm.com/blogs/psirt/security-bulletin-ibm-maximo-asset-management-is-vulnerable-to-cross-site-scripting-cve-2021-20374/](https://link.zhihu.com/?target=https%3A//www.ibm.com/blogs/psirt/security-bulletin-ibm-maximo-asset-management-is-vulnerable-to-cross-site-scripting-cve-2021-20374/)

## 华云安

华云安是一家面向网络空间安全领域，专注于漏洞研究、攻防对抗、产品研发、安全服务的高新技术企业。

