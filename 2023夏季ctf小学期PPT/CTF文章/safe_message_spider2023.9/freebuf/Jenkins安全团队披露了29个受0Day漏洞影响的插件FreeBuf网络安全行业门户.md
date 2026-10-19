Jenkins安全团队披露了影响Jenkins自动化服务器中29个插件的数十项缺陷，其中大部分尚未得到修复

Jenkins是最受欢迎的开源自动化服务器，它由CloudBees和Jenkins社区维护。该自动化服务器支持开发人员构建、测试和部署他们的应用程序，它在全球有数十万个活跃的安装，用户数量超过100万。

 **Jenkins的安全团队近日披露了影响Jenkins自动化服务器中29个插件中的34个安全缺陷，其中29个安全缺陷还没有被修复。**

以下是Jenkins发布的公告中指出的漏洞：

  * Build Notifications Plugin
  * build-metrics Plugin
  * Cisco Spark Plugin
  * Deployment Dashboard Plugin
  * Elasticsearch Query Plugin
  * eXtreme Feedback Panel Plugin
  * Failed Job Deactivator Plugin
  * GitLab Plugin
  * HPE Network Virtualization Plugin
  * Jigomerge Plugin
  * Matrix Reloaded Plugin
  * OpsGenie Plugin
  * Plot Plugin
  * Project Inheritance Plugin
  * Recipe Plugin
  * Request Rename Or Delete Plugin
  * requests-plugin Plugin
  * Rich Text Publisher Plugin
  * RocketChat Notifier Plugin
  * RQM Plugin
  * Skype notifier Plugin
  * TestNG Results Plugin
  * Validating Email Parameter Plugin
  * XebiaLabs XL Release Plugin
  * XPath Configuration Viewer Plugin

这些漏洞的严重程度从低到高不等，截至公告发布时，以下漏洞还没有被修复：

  * Build Notifications Plugin
  * build-metrics Plugin
  * Cisco Spark Plugin
  * Deployment Dashboard Plugin
  * Elasticsearch Query Plugin
  * eXtreme Feedback Panel Plugin
  * Failed Job Deactivator Plugin
  * HPE Network Virtualization Plugin
  * Jigomerge Plugin
  * Matrix Reloaded Plugin
  * OpsGenie Plugin
  * Plot Plugin
  * Project Inheritance Plugin
  * Recipe Plugin
  * Request Rename Or Delete Plugin
  * Rich Text Publisher Plugin
  * RocketChat Notifier Plugin
  * RQM Plugin
  * Skype notifier Plugin
  * Validating Email Parameter Plugin
  * XPath Configuration Viewer Plugin

未修补的漏洞列表包括XSS、跨站请求伪造（CSRF）、缺失或不正确的权限检查，以及以纯文本存储的密码、API密钥和令牌。

以下则是公告发布时，已经通过补丁解决的漏洞：

GitLab Plugin应更新至1.5.35版本

requests-plugin Plugin应更新至2.2.17版

TestNG Results Plugin应更新至555.va0d5f66521e3版本

XebiaLabs XL Release Plugin应更新至22.0.1版本

>  **参考来源：** https://securityaffairs.co/wordpress/132836/security/jenkins-> plugins-zero-day-flaws.html

