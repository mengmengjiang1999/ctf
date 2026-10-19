根据国家信息安全漏洞库（CNNVD）统计，本周（2021.
5.31~2021.6.6）CNNVD接报漏洞2142个，信息技术产品漏洞（通用型漏洞）76个，网络信息系统漏洞（事件型漏洞）2066个。CNNVD接报漏洞预警76份，
**其中华云安报送预警5份，预警报送数量持续位居前列**
！[（数据来源于CNNVD）](https://link.zhihu.com/?target=https%3A//mp.weixin.qq.com/s%3F__biz%3DMzAxODY1OTM5OQ%3D%3D%26mid%3D2651441863%26idx%3D1%26sn%3D627fc544dafc1e26974906496155f1e1%26scene%3D21%23wechat_redirect)

本周重点关注漏洞包括：CVE-2021-25641-Apache Dubbo 反序列化漏洞、CVE-2021-30181-Apache Dubbo
远程代码执行漏洞、CVE-2021-30179-Apache Dubbo 远程代码执行漏洞、CVE-2021-30465-runc 安全特征问题漏洞、用友
NC BeanShell 远程代码执行漏洞、CVE-2021-24370-Fancy Product
Designer远程代码执行漏洞。漏洞影响范围较广，华云安建议相关用户做好资产自查与预防工作。

##  **CVE-2021-25641-Apache Dubbo 反序列化漏洞**

中危

2021年5月31日，华云安思境安全团队发现 Apache 官方发布安全更新，披露了 Apache Dubbo 组件中存在一处反序列化漏洞。Apache
Dubbo 是一款基于 Java 的轻量级 RPC
（远程过程调用）框架。该产品提供了基于接口的远程呼叫、容错和负载平衡以及自动服务注册和发现等功能。成功利用此漏洞攻击者可以通过篡改字节前序标志来选择提供者将使用哪个序列化
id。

情报来源：

[https://lists.apache.org/thread.html/r237ff7f286bda31682c254550c1ebf92b0ec61329b32fbeb2d1c8751%40%3Cusers.tapestry.apache.org%3E](https://link.zhihu.com/?target=https%3A//lists.apache.org/thread.html/r237ff7f286bda31682c254550c1ebf92b0ec61329b32fbeb2d1c8751%2540%253Cusers.tapestry.apache.org%253E)

##  **CVE-2021-30181-Apache Dubbo 远程代码执行漏洞**

低危

2021年5月31日，华云安思境安全团队发现 Apache 官方发布安全更新，披露了 Apache Dubbo 组件中存在一处远程代码执行漏洞。该漏洞是由于
Apache Dubbo 支持脚本路由功能，成功利用此漏洞攻击者可在获得权限的情况下，构造恶意配置，插入恶意代码，最终获取服务器最高权限。

情报来源：

[https://lists.apache.org/thread.html/re22410dc704a09bc7032ddf15140cf5e7df3e8ece390fc9032ff5587%40%3Cdev.dubbo.apache.org%3E](https://link.zhihu.com/?target=https%3A//lists.apache.org/thread.html/re22410dc704a09bc7032ddf15140cf5e7df3e8ece390fc9032ff5587%2540%253Cdev.dubbo.apache.org%253E)

##  **CVE-2021-30179-Apache Dubbo 远程代码执行漏洞**

中危

2021年5月31日，华云安思境安全团队发现 Apache 官方发布安全更新，披露了 Apache Dubbo 组件中存在一处远程代码执行漏洞。该漏洞是由于
Dubbo 在通用过滤器中未对传入的反序列化数据进行严格的过滤，成功利用此漏洞攻击者可在未授权的情况下，构造恶意数据，从而执行远程代码攻击，最终接管服务器。

情报来源：

[https://lists.apache.org/thread.html/rccbcbdd6593e42ea3a1e8fedd12807cb111375c9c40edb005ef36f67@%3Cdev.dubbo.apache.org%3E](https://link.zhihu.com/?target=https%3A//lists.apache.org/thread.html/rccbcbdd6593e42ea3a1e8fedd12807cb111375c9c40edb005ef36f67%40%253Cdev.dubbo.apache.org%253E)

##  **CVE-2021-30465-runc 安全特征问题漏洞**

中危

2021年6月1日，华云安思境安全团队发现 runc 组件中存在一处安全特征问题漏洞。Runc 是一款用于根据 OCI 规范生成和运行容器的 CLI
（命令行界面）工具。成功利用此漏洞攻击者可在未授权的情况下，通过创建恶意的 POD 及 container
将宿主文件系统绑定挂载到容器中，造成容器逃逸，最终造成服务器敏感性信息泄露。

情报来源：

[http://www.openwall.com/lists/oss-security/2021/05/19/2](https://link.zhihu.com/?target=http%3A//www.openwall.com/lists/oss-security/2021/05/19/2)

##  **用友 NC BeanShell 远程代码执行漏洞**

超危

2021年6月1日，华云安思境安全团队发现用友 NC BeanShell 组件中存在一处远程代码执行漏洞。用友 NC 6 是用友 NC
产品的全新系列、是面向集团企业的世界级高端管理软件。该漏洞是由于用友 NC 对外开放了 BeanShell
测试接口，并没有设置权限，成功利用此漏洞攻击者可在未授权的情况下，构造恶意数据，执行任意代码，最终获取服务器最高权限。

情报来源：

[http://umc.yonyou.com/ump/querypatchdetailedmng?PK=18981c7af483007db179a236016f594d37c01f22aa5f5d19](https://link.zhihu.com/?target=http%3A//umc.yonyou.com/ump/querypatchdetailedmng%3FPK%3D18981c7af483007db179a236016f594d37c01f22aa5f5d19)

##  **CVE-2021-24370-Fancy Product Designer远程代码执行漏洞**

超危

2021年6月4日，华云安思境安全团队发现 WordPress 插件 Fancy Product Designer 中存在一处远程代码执行漏洞。Fancy
Product Designer 是 WordPress、WooCommerce 和 Shopify
的一个可视化产品配置插件，它允许客户使用自己的图形和内容定制产品。该漏洞源于 “wp-admin” 或 “wp-content/plugins/fancy-product-designer/inc” 中文件上传时对文件的验证不足。成功利用此漏洞攻击者可以绕过恶意文件上传的检查，并上传部署可执行的 PHP
文件执行远程代码攻击，最终可以完全接管受攻击的站点。

情报来源：

[https://www.wordfence.com/blog/2021/06/critical-0-day-in-fancy-product-designer-under-active-attack/﻿](https://link.zhihu.com/?target=https%3A//www.wordfence.com/blog/2021/06/critical-0-day-in-fancy-product-designer-under-active-attack/)

