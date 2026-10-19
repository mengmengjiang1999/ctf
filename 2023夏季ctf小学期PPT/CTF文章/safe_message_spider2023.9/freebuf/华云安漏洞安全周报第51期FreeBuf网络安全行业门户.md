​根据国家信息安全漏洞库（CNNVD）统计，本周（2021.
9.6~2021.9.12）CNNVD接报漏洞1374，信息技术产品漏洞（通用型漏洞）121个，网络信息系统漏洞（事件型漏洞）1253个，其中华云安
**报送漏洞100个** ；CNNVD接报漏洞预警66份，其中华云安 **报送预警2份** ； **本周漏洞报送数量持续位居前列！**
_（数据来源于CNNVD）_

本周重点关注漏洞包括：CVE-2021-40346-HAProxy 整数溢出漏洞、CVE-2021-40444-MSHTML
代码注入漏洞、CVE-2021-39115-Jira Service Management Server 远程代码执行漏洞、Node.js
多个安全漏洞、CVE-2021-38360-WordPress wp-publications
路径遍历漏洞。漏洞影响范围较广，华云安建议相关用户做好资产自查与预防工作。

##  **CVE-2021-40346-HAProxy 整数溢出漏洞**

中危

2021年9月7日，华云安思境安全团队发现 HAProxy 组件中存在一处整数溢出漏洞。HAProxy
是一个广泛使用的开源负载均衡器和代理服务器，非常适用于负载较大的web站点，并被许多大型企业使用。该漏洞是由于 HAProxy 中的
htx_add_header() 和 htx_add_trailer()
函数中缺少头名称的长度检查引起，成功利用此漏洞的攻击者可以实现绕过安全控制，未授权访问并修改敏感数据。

情报来源：

> [https://www.haproxy.com/blog/september-2021-duplicate-content-length-> header-> fixed/](https://link.zhihu.com/?target=https%3A//www.haproxy.com/blog/september-2021-duplicate-> content-length-header-fixed/)

##  **CVE-2021-40444-MSHTML 代码注入漏洞**

高危

2021年9月8日，华云安思境安全团队发现 Microsoft 官方发布安全更新，披露了 MSHTML 组件中存在一处代码注入漏洞。Microsoft
MSHTML.DLL 是一个用于解析 HTML 语言的动态链接库，IE、Outlook、Outlook Express
等应用程序都使用了该动态链接库。成功利用此漏洞的远程攻击者可以创建带有恶意 ActiveX 控件的特制 Office
文档，诱使受害者打开文档并在系统上执行任意代码。

情报来源：

> [https://msrc.microsoft.com/update-> guide/vulnerability/CVE-2021-40444](https://link.zhihu.com/?target=https%3A//msrc.microsoft.com/update-> guide/vulnerability/CVE-2021-40444)

##  **CVE-2021-39115-Jira Service Management Server 远程代码执行漏洞**

高危

2021年9月10日，华云安思境安全团队发现 Atlassian 官方发布安全更新，披露了 Jira Service Management
组件中存在一处远程代码执行漏洞。Jira Service Management 是 Atlassian 旗下的一款面向
ITSM（IT服务管理）的企业级解决方案，基于 Jira 平台构建，通过该平台，IT 团队可以轻松接收、跟踪、管理和解决来自团队客户的需求。该漏洞是由于
Jira Service Management 允许用户上传自定义的邮件模板引起，成功利用此漏洞的远程攻击者在未授权的情况下，可以与“Jira
管理员”访问任意 Java 代码或运行任意系统命令。

情报来源：

>
> [https://jira.atlassian.com/browse/JSDSERVER-8665](https://link.zhihu.com/?target=https%3A//jira.atlassian.com/browse/JSDSERVER-8665)

##  **Node.js 多个安全漏洞**

高危

2021年9月10日，华云安思境安全团队发现 GitHub 公开披露了 Node.js 包 tar 和 @npmcli/arborist
组件中的7个高危漏洞，分别是：CVE-2021-32803-Node-tar 路径遍历漏洞、CVE-2021-32804-Node-tar
路径遍历漏洞、CVE-2021-37701-Npm Node-tar 后置链接漏洞、CVE-2021-37712-Npm Node-tar
后置链接漏洞、CVE-2021-37713-Node-tar 路径遍历漏洞、CVE-2021-39134-Arborist
后置链接漏洞、CVE-2021-39135-NPM @npmcli/arborist 后置链接漏洞。Tar 是 npm 的一个核心依赖，用于提取和安装
npm 包。@npmcli/arborist 是 npm CLI 的一个核心依赖项，用于管理 node_modules 树。当 tar 被用来提取不受信任的
tar 文件或当 npmCLI 在某些文件系统条件下被用来安装不受信任的 npm 包时，这些漏洞可能会由于文件覆盖或创建而导致任意代码执行。

情报来源：

> [https://github.blog/2021-09-08-github-security-update-vulnerabilities-tar-> npmcli-> arborist/](https://link.zhihu.com/?target=https%3A//github.blog/2021-09-08-github-> security-update-vulnerabilities-tar-npmcli-arborist/)

##  **CVE-2021-38360-WordPress wp-publications 路径遍历漏洞**

高危

2021年9月11日，华云安思境安全团队发现 Wordfence 发布安全更新，披露了 WordPress wp-publications
组件中存在一处路径遍历漏洞。wp-publications 是 WordPress 开源的一个应用插件。该漏洞是由于 ~/bibtexbrowser.php
中的 Q_FILE 参数缺少有效的验证，易造成本地文件包含漏洞。成功利用此漏洞的攻击者可实现包含本地 zip 文件，从而造成远程代码执行。

情报来源：

> [https://www.wordfence.com/vulnerability-> advisories/#CVE-2021-38360](https://link.zhihu.com/?target=https%3A//www.wordfence.com/vulnerability-> advisories/%23CVE-2021-38360)

 **华云安**

华云安是一家面向网络空间安全领域，专注于漏洞研究、攻防对抗、产品研发、安全服务的高新技术企业。公司在漏洞管理和威胁治理方面具备深厚的技术积累。拥有灵洞自适应威胁与漏洞管理系统、灵刃智能化渗透攻防系统等网络安全产品及服务，为政府、金融、能源、教育、医疗等行业，提供集网络安全情报采集分析能力、
关键信息基础设施防御能力、网络安全反制能力于一体的新一代云原生安全产品解决方案。实现威胁管理、攻击模拟、溯源分析、端点防御等一体化安全运营管理能力。华云安致力于为新形势下的网络安全和关键信息基础设施保护作出自身的贡献！

进入 **华云安漏洞情报平台** 参阅详情

>
> [漏洞情报平台​vti.huaun.com/index/​vti.huaun.com/index/​vti.huaun.com/index/](https://link.zhihu.com/?target=https%3A//vti.huaun.com/index/)

