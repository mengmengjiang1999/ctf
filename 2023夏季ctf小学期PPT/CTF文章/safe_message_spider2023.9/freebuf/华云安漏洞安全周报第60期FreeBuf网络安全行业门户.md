根据[国家信息安全漏洞库（CNNVD）统计](https://link.zhihu.com/?target=https%3A//mp.weixin.qq.com/s%3F__biz%3DMzAxODY1OTM5OQ%3D%3D%26mid%3D2651442082%26idx%3D1%26sn%3D5386e2d92b2674abf3e22e1776d50b3a%26scene%3D21%23wechat_redirect)，本周（2021.11.15~2021.11.21）CNNVD接报漏洞379，信息技术产品漏洞（通用型漏洞）103个，网络信息系统漏洞（事件型漏洞）276个；CNNVD接报漏洞预警170份，其中华云安报送预警15个，漏洞报送数量持续位居前列！

本周重点关注漏洞包括：Hadoop Yarn RPC 未授权访问漏洞、Intel BIOS 多个权限提升漏洞、CVE-2021-37580-Apache
ShenYu 身份验证绕过漏洞、NPM 多个安全漏洞、CVE-2021-36749-Apache Druid LoadData
文件读取漏洞。漏洞影响范围较广，华云安建议相关用户做好资产自查与预防工作。

##  **Hadoop Yarn RPC 未授权访问漏洞**

高危

2021年11月15日，华云安思境安全团队发现 Apache 官方发布安全更新，披露了 Hadoop Yarn RPC
组件中存在一处未授权访问漏洞。Hadoop Yarn 是 Hadoop
核心组件之一，主要功能是将资源分配至各个集群中运行各种应用程序，并调度不同集群节点上的任务执行。该漏洞是由于 Hadoop Yarn 默认对外开放 RPC
服务，且缺乏身份验证引起；成功利用此漏洞的攻击者在未授权的情况下，可通过构造恶意数据执行远程代码攻击，目前该漏洞暂无 CVE 编号并存在在野利用。

[https://hadoop.apache.org/docs/current/hadoop-yarn/hadoop-yarn-site/YARN.html](https://link.zhihu.com/?target=https%3A//hadoop.apache.org/docs/current/hadoop-yarn/hadoop-yarn-site/YARN.html)

##  **Intel BIOS 多个权限提升漏洞**  
高危

2021年11月16日，华云安思境安全团队发现 Intel 官方发布安全更新，披露了 Intel BIOS 固件中存在
CVE-2021-0157、CVE-2021-0158、CVE-2021-0146 等多个权限提升漏洞。Intel Bios
是英特尔（Intel）的基本输入输出系统，用于在通电启动阶段执行硬件初始化，以及为操作系统提供运行时服务的固件。该漏洞是由于 Intel(R) 处理器的
BIOS 固件控制流管理不当导致，成功利用这些漏洞的攻击者在具有本地访问权限的前提下可进行权限提升。

[https://www.intel.com/content/www/us/en/security-center/advisory/intel-sa-00562.html](https://link.zhihu.com/?target=https%3A//www.intel.com/content/www/us/en/security-center/advisory/intel-sa-00562.html)

##  **CVE-2021-37580-Apache ShenYu 身份验证绕过漏洞**

超危

2021年11月16日，华云安思境安全团队发现 Apache 官方发布安全更新，披露了 Apache ShenYu
组件中存在一处身份验证绕过漏洞。Apache ShenYu 是一个异步的，高性能的，跨语言的，响应式的 API 网关。该漏洞是由于 ShenyuAdmin
Bootstrap 中 JWT 的错误使用引起，导致攻击者可以绕过身份验证，直接进入目标系统后台。

[https://lists.apache.org/thread/o15j25qwtpcw62k48xw1tnv48skh3zgb](https://link.zhihu.com/?target=https%3A//lists.apache.org/thread/o15j25qwtpcw62k48xw1tnv48skh3zgb)

##  **NPM 多个安全漏洞**  
高危

2021年11月17日，华云安思境安全团队发现 GitHub 官方发布安全更新，披露了 npm 组件中存在一处信息泄露漏洞和一处未授权漏洞。npm（全称
Node Package Manager，即“node包管理器”）是 Node.js 默认的、用 JavaScript
编写的软件包管理系统。成功利用此漏洞的攻击者在未授权的情况下，可通过构造恶意数据造成服务器敏感性信息泄露攻击，或在未授权的情况下使用账户发布任何 npm
包的新版本。

[https://github.blog/2021-11-15-githubs-commitment-to-npm-ecosystem-security/](https://link.zhihu.com/?target=https%3A//github.blog/2021-11-15-githubs-commitment-to-npm-ecosystem-security/)

##  **CVE-2021-36749-Apache Druid LoadData 文件读取漏洞**  
中危

2021年11月19日，华云安思境安全团队发现 Apache 官方发布安全更新，披露了 Apache Druid LoadData
组件中存在一处文件读取漏洞。Apache Druid 是一款使用 Java 语言编写的、面向列的开源分布式数据库。该漏洞是由于用户指定 HTTP
InputSource 没有做出限制，可以通过将文件 URL 传递给 HTTP InputSource
来绕过应用程序级别的限制。成功利用此漏洞的攻击者在未授权的情况下，通过构造恶意请求执行文件读取，最终造成服务器敏感性信息泄露。

[https://lists.apache.org/thread.html/rc9400a70d0ec5cdb8a3486fc5ddb0b5282961c0b63e764abfbcb9f5d%40%3Cdev.druid.apache.org%3E](https://link.zhihu.com/?target=https%3A//lists.apache.org/thread.html/rc9400a70d0ec5cdb8a3486fc5ddb0b5282961c0b63e764abfbcb9f5d%2540%253Cdev.druid.apache.org%253E)

进入华云安漏洞情报平台参阅详情

华云安是一家面向网络空间安全领域的高新技术企业，公司专注于攻击面检测与管理。拥有灵洞自适应威胁与漏洞管理系统、灵刃智能化渗透攻防系统、灵鉴弱点识别与检测系统等网络安全产品及服务，为政府、金融、能源、教育、医疗等行业，提供集网络安全情报采集分析能力、
关键信息基础设施防御能力、网络安全反制能力于一体的新一代云原生安全产品解决方案。实现威胁管理、攻击模拟、溯源分析、端点防御等一体化安全运营管理能力。华云安致力于为新形势下的网络安全和关键信息基础设施保护作出自身的贡献！

