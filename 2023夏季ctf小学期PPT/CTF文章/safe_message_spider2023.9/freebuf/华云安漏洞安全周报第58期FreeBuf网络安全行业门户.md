根据[国家信息安全漏洞库（CNNVD）](https://link.zhihu.com/?target=https%3A//mp.weixin.qq.com/s%3F__biz%3DMzAxODY1OTM5OQ%3D%3D%26mid%3D2651442063%26idx%3D2%26sn%3D6efb4c965c324d28293915089a158689%26scene%3D21%23wechat_redirect)统计，本周（2021.
11.1~2021.11.7）CNNVD接报漏洞307，信息技术产品漏洞（通用型漏洞）90个，网络信息系统漏洞（事件型漏洞）217个；CNNVD接报漏洞预警48份。

本周重点关注漏洞包括：CVE-2021-41973-Apache MINA 拒绝服务漏洞、CVE-2021-43267-Linux Kernel TIPC
远程代码执行漏洞、CVE-2021-42359-WordPress 访问控制错误漏洞、CVE-2021-22260-GitLab
跨站脚本漏洞、CVE-2021-40120-Cisco Small Business RV Series Routers
输入验证错误漏洞。漏洞影响范围较广， **华云安建议相关用户做好资产自查与预防工作。**

##  **CVE-2021-41973-Apache MINA拒绝服务漏洞**  
中危

2021年11月1日，华云安思境安全团队发现 Apache 官方发布安全更新，披露了 Apache MINA 组件中存在一处拒绝服务漏洞。Apache
MINA 是一款网络应用程序框架，该产品主要用于开发高性能和高可伸缩性的网络应用程序。该漏洞是由于在 Apache MINA 中，一个特定的恶意的 HTTP
请求可能会导致 HTTP Header 解码器无限循环。解码器假设 HTTP 报头从缓冲区的开头开始，如果有比预期更多的数据，则进行循环。

[https://lists.apache.org/thread.html/r0b907da9340d5ff4e6c1a4798ef4e79700a668657f27cca8a39e9250%40%3Cdev.mina.apache.org%3E](https://link.zhihu.com/?target=https%3A//lists.apache.org/thread.html/r0b907da9340d5ff4e6c1a4798ef4e79700a668657f27cca8a39e9250%2540%253Cdev.mina.apache.org%253E)

##  **CVE-2021-40120-Cisco Small Business RV Series Routers 输入验证错误漏洞**

高危

2021年11月3日，华云安思境安全团队发现 Cisco 官方发布安全更新，披露了 Cisco Small Business RV Series
Routers 组件中存在一处输入验证错误。该漏洞是由于 Web
的管理界面中存在一个漏洞，该漏洞可能允许具有管理权限的经过身份验证的远程攻击者将任意命令注入底层操作系统并使用 root权限执行。

[https://tools.cisco.com/security/center/content/CiscoSecurityAdvisory/cisco-sa-sbrv-cmdinjection-Z5cWFdK](https://link.zhihu.com/?target=https%3A//tools.cisco.com/security/center/content/CiscoSecurityAdvisory/cisco-sa-sbrv-cmdinjection-Z5cWFdK)

##  **CVE-2021-43267-Linux Kernel TIPC 远程代码执行漏洞**  
严重

2021年11月4日，华云安思境安全团队发现 Linux Kernel 的 TIPC 模块中存在一处远程代码执行漏洞。Linux kernel 是
Linux 基金会的开源操作系统 Linux 所使用的内核。该漏洞是由于应用对 MSG_CRYPTO
消息类型大小验证不足。成功利用此漏洞的远程攻击者可以执行任意代码，获取内核权限，从而攻击整个系统。

[https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.14.16](https://link.zhihu.com/?target=https%3A//cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.14.16)

##  **CVE-2021-22260-GitLab 跨站脚本漏洞**  
中危

2021年11月4日，华云安思境安全团队发现 GitLab 官方发布安全更新，披露了 Gitlab 的组件中存在一处跨站脚本漏洞。GitLab
是一个开源的端到端软件开发平台，具有内置的版本控制、问题跟踪、代码审查、CI/CD（持续集成和持续交付）等功能。该漏洞是由于 Web
应用缺少对客户端数据的正确验证，成功利用此漏洞的攻击者可执行客户端代码。

[https://gitlab.com/gitlab-org/gitlab/-/issues/336614](https://link.zhihu.com/?target=https%3A//gitlab.com/gitlab-org/gitlab/-/issues/336614)

##  **CVE-2021-42359-WordPress 访问控制错误漏洞**  
高危

2021年11月7日，华云安思境安全团队发现 WordPress DSGVO Tools 组件中存在一处访问控制错误漏洞。WordPress 是
WordPress 基金会的一套使用 PHP 语言开发的博客平台，该平台支持在 PHP 和 MySQL
的服务器上架设个人博客网站。该漏洞是由于应用缺少能力检查和随机数检查，可供未经身份验证的用户使用，并且在删除取消订阅时不检查帖子类型要求。

[https://www.wordfence.com/blog/2021/11/vulnerability-in-wp-dsgvo-tools-gdpr-plugin-allows-unauthenticated-page-deletion/](https://link.zhihu.com/?target=https%3A//www.wordfence.com/blog/2021/11/vulnerability-in-wp-dsgvo-tools-gdpr-plugin-allows-unauthenticated-page-deletion/)

进入华云安漏洞情报平台参阅详情

[https://vti.huaun.com​vti.huaun.com](https://link.zhihu.com/?target=https%3A//vti.huaun.com)

华云安

华云安是一家面向网络空间安全领域的高新技术企业，公司专注于攻击面检测与管理。拥有灵洞自适应威胁与漏洞管理系统、灵刃智能化渗透攻防系统、灵鉴弱点识别与检测系统等网络安全产品及服务，为政府、金融、能源、教育、医疗等行业，提供集网络安全情报采集分析能力、
关键信息基础设施防御能力、网络安全反制能力于一体的新一代云原生安全产品解决方案。实现威胁管理、攻击模拟、溯源分析、端点防御等一体化安全运营管理能力。华云安致力于为新形势下的网络安全和关键信息基础设施保护作出自身的贡献！

