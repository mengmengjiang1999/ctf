根据[国家信息安全漏洞库（CNNVD）统计](https://mp.weixin.qq.com/s?__biz=MzAxODY1OTM5OQ==&mid=2651442914&idx=1&sn=2c3719eaeb2876901a5cf9b4ba20081e&scene=21#wechat_redirect)，本周（2023.05.08~2023.05.14）CNNVD接报漏洞311个，其中信息技术产品漏洞（通用型漏洞）175个，网络信息系统漏洞（事件型漏洞）136个，CNNVD收录漏洞通报102份。

本周重点关注漏洞包括：CVE-2023-31039 Apache bRPC 代码执行漏洞、CVE-2023-20877 VMware Aria
Operations 权限提升漏洞、2023-05 补丁日：微软多个漏洞安全更新、CVE-2023-29032 Apache OpenMeetings
身份认证绕过漏洞。漏洞影响范围较广，华云安建议相关用户做好资产自查与预防工作。

 **01 CVE-2023-31039 Apache bRPC 代码执行漏洞**

威胁等级：高危

漏洞描述：

2023年05月08日，华云安思境安全团队监测发现 Apache 官方发布了安全更新，披露了Apache bRPC
1.5.0之前版本存在安全漏洞。Apache bRPC 是一款开源的工业级C++
RPC框架，常用于搜索、存储、机器学习、广告、推荐等高性能系统。未经身份验证的攻击者利用该漏洞可能对 bRPC 服务器启动时修改 ServerOptions
pid_file 参数，导致bRPC进程的权限执行任意代码。

情报来源：

<https://lists.apache.org/thread/jqpttrqbc38yhckgp67xk399hqxnz7jn>

 **02** **CVE-2023-20877 VMware Aria Operations 权限提升漏洞**

威胁等级：超危

漏洞描述：

2023年05月11日，华云安思境安全团队监测发现 VMware 官方发布安全更新，披露了 Linux Kernel v5.11-rc1 ~
v6.2-rc5 存在安全漏洞。VMware Aria
Operations是一套适用于私有云、混合云、多云环境的IT运营管理平台。未经身份验证的攻击者可能利用具有ReadOnly
权限的用户执行特殊命令导致权限提升。

情报来源：

<https://www.vmware.com/security/advisories/VMSA-2023-0009.html>

 **03 2023-05 补丁日：微软多个漏洞安全更新**

威胁等级：高危

漏洞描述：

2023年05月10日，华云安思境安全团队监测发现 Microsoft 官网发布安全更新，此次安全更新发布了 38
个漏洞补丁，其中包含7个严重漏洞,31个高危漏洞。主要覆盖了以下组件：Microsoft Windows and Windows Components;
Office and Office Components; Microsoft Edge (Chromium-based); SharePoint
Server; Visual Studio; SysInternals; Microsoft
Teams等。漏洞影响范围较广，华云安建议相关用户做好资产自查与预防工作。

情报来源：

<https://msrc.microsoft.com/update-guide/en-us/releaseNote/2023-May>

 **04** **CVE-2023-29032 Apache OpenMeetings 身份认证绕过漏洞**

威胁等级：超危

漏洞描述：

2023年05月12日，华云安思境安全团队监测发现 Apache 官方发布安全更新，披露了 Apache OpenMeetings 3.1.3 到
7.1.0版本存在授权问题漏洞。Apache OpenMeetings
是一个多语言可定制的视频会议和协作系统。它支持音频、视频,能让你查看每个与会者的桌面。未经身份验证的攻击者利用该漏洞来充当其他用户导致身份绕过。

情报来源：

<https://lists.apache.org/thread/j2d6mg3rzcphfd8vvvk09d8p4o9lvnqp>

华云安

华云安是一家深耕于网络空间安全领域的高新技术企业，专注于漏洞研究、攻防对抗、产品研发、安全服务；致力于对主动防御、情报协同、溯源反制能力进行融合创新，以攻击者视角构建攻击面管理安全能力平台，提供新一代网络安全对抗防御解决方案。公司服务于国家网络安全监管部门及金融、能源、教育、医疗等关键信息基础设施行业。

公司持续构建的原子化安全能力平台，秉承数据驱动、AI引领的理念，通过基于知识图谱的安全风险库和场景化人工智能引擎两大核心技术，结合不同的业务需求灵活组合安全能力，实现一个平台覆盖所有安全能力。

