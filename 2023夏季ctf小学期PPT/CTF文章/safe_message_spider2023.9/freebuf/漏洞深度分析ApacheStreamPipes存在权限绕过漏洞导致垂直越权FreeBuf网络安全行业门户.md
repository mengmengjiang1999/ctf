# 项目地址

https://github.com/apache/streampipes

# 项目介绍

Apache StreamPipes 使工业数据分析变得简单！

StreamPipes 是工业物联网的端到端工具箱。它带有针对非技术用户的丰富的图形用户界面，并提供以下功能：

  * 快速连接超过 20 种工业协议，例如 OPC-UA、PLC、MQTT、REST、Pulsar、Kafka 等。
  * 使用超过 100 种算法和数据接收器创建数据协调和分析管道，以将数据转发到第三方系统。
  * 使用数据浏览器通过许多为时间序列数据量身定制的小部件直观地探索历史数据。
  * 实时仪表板，用于显示来自数据源和管道的实时数据，例如，用于车间监控。
  * StreamPipes 具有高度可扩展性，包括一个 Java SDK 来创建新的管道元素和适配器。Python 支持在早期开发阶段可用 - 敬请期待！管道元素是独立的微服务，可以在任何地方运行——集中在您的服务器上或靠近边缘。您想在实时数据上使用自己的机器学习模型吗？只需编写您自己的数据处理器并使其可作为管道元素重复使用。

除此之外，StreamPipes 还包括用于生产部署的功能：

  * 将管道、数据流和仪表板等资源分配给资产以实现更好的组织。
  * 管道和适配器的监控和指标。
  * 内置用户和访问权限管理。
  * 导出和导入资源。

# 项目版本

0.90.0

# 漏洞细节

开启REST API，虽然配置了全局 jwt 权限校验，但是并未对用户 token 进行鉴别。因此普通用户亦可使用自己 jwt
发送数据包进行创建用户，且并未对创建用户归属的用户组和权限进行检查，导致低权限用户可以越权创建管理员账户。

具体分析如下：  
项目提供了  
org.apache.streampipes.rest.impl#UserResource 类对用户进行相关操作，且实现了私有函数进行检查。

![1687937985_649be3c1004d2a2da88d8.png!small](https://image.3001.net/images/20230628/1687937985_649be3c1004d2a2da88d8.png!small)

例如 updateUserAccountDetails 函数就调用了 isAdmin 进行操作前检查。

![1687937994_649be3ca55569b977bd16.png!small](https://image.3001.net/images/20230628/1687937994_649be3ca55569b977bd16.png!small)

但创建用户函数 user 并未对当前用户及用户传入的权限、用户信息、用户组进行检查。导致可以实现权限绕过实现垂直越权。

![1687938004_649be3d4627ced4e273e2.png!small](https://image.3001.net/images/20230628/1687938004_649be3d4627ced4e273e2.png!small)

# 漏洞利用

创建低权限用户 admin@admin.com ，role 为 Pipline User，无任务界面及功能查看、点击、设置权限。

![1687938014_649be3dea78fbfcd428b5.png!small](https://image.3001.net/images/20230628/1687938014_649be3dea78fbfcd428b5.png!small)

刷新上述空白页面，抓包获取 jwt。

![1687938023_649be3e72bb1fa4091c29.png!small](https://image.3001.net/images/20230628/1687938023_649be3e72bb1fa4091c29.png!small)

以该用户权限访问创建用户链接，无法查看、操作任何内容。

![1687938038_649be3f605b7fc59faf5c.png!small](https://image.3001.net/images/20230628/1687938038_649be3f605b7fc59faf5c.png!small)

以管理员身份抓包获取创建用户创建数据包，删除cookie、替换jwt为受限用户 admin@admin.com。

![1687938047_649be3ffb75c5eb33887c.png!small](https://image.3001.net/images/20230628/1687938047_649be3ffb75c5eb33887c.png!small)

不仅可以创建用户 admin1 ，还可以创建带管理员权限的用户。

![1687938056_649be408ccf977a7f4c17.png!small](https://image.3001.net/images/20230628/1687938056_649be408ccf977a7f4c17.png!small)

以越权创建的用户 admin1 登录，可以实现全部管理员操作。

![1687938064_649be410d97e155b2bd13.png!small](https://image.3001.net/images/20230628/1687938064_649be410d97e155b2bd13.png!small)

# 修补方式

厂商已发布了漏洞修复程序，请使用此产品的用户尽快更新至安全版本，版本升级链接如下：  
https://streampipes.apache.org/download

