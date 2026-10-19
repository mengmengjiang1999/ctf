随着近年来国内机器人领域的不断升温，机器人智能化逐渐进入人们的视野，其中，不少厂家都在使用 **Robot Operation System**
**（机器人操作系统，以下简称ROS）**
。但是，因ROS诞生于实验室相对封闭的环境，因此一开始对于安全性的研究并未受到开发者的重视，导致ROS存在着诸多安全上的问题，随着开源和ROS的大热，很多安全问题也随之暴露出来，成为安全从业者研究的热门方向。

 **《探秘ROS安全系列》** 是 **京东安全** 自主研究和编写的系列文章，此系列将从 **ROS**
**简介＆背景、ROS安全方案＆研究趋势、ROS安全方案注解、京东ROS安全研究实践**
4个部分，详细介绍京东安全对于ROS安全的研究和实践，希望能够与大家一同探讨。

本期是整个系列的 **第二期** ，将从 **ROS** **安全方案、安全研究趋势**
两个模块的内容出发，供大家了解现有的ROS安全研究情况，以下，enjoy~

（全文2133字，阅读时间约7分钟）

## 一、ROS安全方案

 **1** **、ROS 1.0 安全方案**

在第一期中，我们介绍了关于ROS安全的研究阶段，其中，在第二阶段，ROS
1.0的安全风险充分暴露，业界涌现了众多安全方案，主要解决身份认证、加密通信、访问控制等风险。在各方案中，SROS安全特性相对全面，同时具备较好的易用性（部署工具/脚本），是ROS社区推荐方案。

 **方案1：ROSAuth**

特点：

【目的】解决远程客户端访问ROS身份认证问题。

【实现】ROS系统运行在隔离网络域内；远程客户端在通过SSL在外部Authenticator进行身份鉴权并获取token；远程客户端使用token，通过SSL访问ROS；ROS校验token，允许或拒绝访问。

【不足】未解决身份认证后的Authorization问题。

 **ROSAuth**

https://web.cs.wpi.edu/~cshue/research/tepra14.pdf

![](https://image.3001.net/images/20210414/1618392161_6076b461c19fac06b4370.jpg!small)

（图片选自上述链接论文）

 **方案2：ROSRV**

特点：

【目的】实现ROS通信实时监控管理。

【实现】ROS Runtime Verification使用Man-in-the-Middle技术，通过增加RVMaster节点，实时监控ROS
1.0内部消息，同时可配置访问控制策略进行访问控制。

【不足】访问控制基于IP，RVMaster中心化设计在节点数过多时的scalability问题。

 **ROSRV**

https://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.1063.8693&rep=rep1&type=pdf

![](https://image.3001.net/images/20210414/1618392196_6076b48403dedf1b21cd6.jpg!small)

（图片选自论文《2014 ROSRV: Runtime verification for robotics》）

  

 **方案3：Secure ROS transport**

特点：

【目的】解决ROS通信安全与访问控制

【方案1】应用层方案，使用外部Authentication Server实现publisher-subscriber之间的身份认证与加密通信。优点是无需改动ROS，缺点是应用层实现，无法阻止类似DoS攻击。

（参考链接：https://mediatum.ub.tum.de/doc/1343172/1343172.pdf）

![](https://image.3001.net/images/20210414/1618392232_6076b4a8a69fe667cd15e.jpg!small)（图片选自上述链接论文）

【方案2】通信层方案，使用证书+TLS解决节点间身份认证、加密通信、访问控制问题。缺点是没有解决master节点安全问题。

（参考链接：https://www.researchgate.net/publication/314082519_Secure_Communication_for_the_Robot_Operating_System）  
![](https://image.3001.net/images/20210414/1618392256_6076b4c02ec7e58d84093.jpg!small)（图片选自上述链接论文）

  

 **方案4：Secure ROS**

特点：

【目的】解决ROS通信安全与访问控制。

【方案】基于IPSec实现身份认证与加密通信，使用系统配置文件实现集中式访问控制。优点是安装方便，不足是访问控制等基于IP粒度。

 **Secure ROS**

https://roscon.ros.org/2017/presentations/ROSCon%202017%20SecureROS.pdf![](https://image.3001.net/images/20210414/1618392284_6076b4dc2f037b4a454ac.jpg!small)

（图片选自2019年 IROS SROS2 Tutorial workshop 的讨论PPT）

  

 **方案5：SROS**

特点：

【目的】解决ROS通信安全与访问控制。

【方案】基于TLS+证书机制解决身份认证、加密通信、访问控制问题。使用经过证书签名的配置文件进行集中式访问控制，细粒度。不足是需要源码安装及相关配置。

 **SROS**

https://roscon.ros.org/2016/presentations/sros.pdf![](https://image.3001.net/images/20210414/1618392312_6076b4f8825931fc83451.jpg!small)

（图片选自2019年 IROS SROS2 Tutorial workshop 的讨论PPT）

  

 **2** **、ROS 2.0 安全方案**

ROS 2.0阶段，因组件DDS自带安全特性原因，安全方案有了统一框架，并形成SROS 2。命名SROS
2是为继承和区分SROS方案，但不同于SROS，SROS2是ROS 2官方标准并集成在主线中。

 **SROS 2**

https://ruffsl.github.io/IROS2018_SROS2_Tutorial/

  

ROS 2.0中，DDS-Security默认未使能。SROS 2方案则是在ROS 2.0基础上，使能DDS-Security，并提供对应部署应用的工具集。可以认为：

 **SROS 2=ROS 2.0+DDS-Security+Tools**

具体可以参考

https://ubuntu.com/blog/what-is-sros-2

  

ROS 2适配修改主要有两个，一个是RCL（ROS Client Library）层修改，一个是SROS 2 utilities工具集。

RCL修改主要是安全特性开关和策略配置，具体如ROS_SECURITY_ENABLE (true/false)、ROS_SECURITY_STRATEGY
(Enforce/Permissive)、 ROS_SECURITY_KEYSTORE (key files directory) 等参数实现和支持。

SROS 2 utilities工具主要解决PKI秘钥证书和控制策略文件的管理，具体如
CA和KEYSTORE根目录管理、节点公私钥和证书创建部署、访问控制策略文件（Governance/Permission）创建部署等。![](https://image.3001.net/images/20210414/1618392395_6076b54bbb46b984e24e2.jpg!small)

（图片选自2019年 IROS SROS2 Tutorial workshop 的讨论PPT）

![](https://image.3001.net/images/20210414/1618392434_6076b57249d987f49a326.jpg!small)（图片选自《ROS
2 Foxy Fitzroy: Setting a new standard for production robot development》）

  

如上图所示，SROS
2通过PKI机制，解决节点间通信安全，包括身份认证、加密通信；通过策略配置文件（Governance、Permission，证书签名），实现集中式访问控制。

关于访问控制，首先，Governance文件限制domain域的整体访问控制策略，如节点访问控制（是否允许未授权节点访问，是否允许被发现），以及domain内部topic访问控制（是否允许被发现、是否允许未授权读写）等。其次，每个节点的Permission限制自己的访问权限，如是否允许对某topic读写。

因DDS是标准规范且有开源、商业不同实现，ROS 2增加了DDS 抽象适配层RMW，如上图所示。

  
  
 **二、机器人安全趋势**  
  

ROS是目前最主流的机器人操作系统框架，ROS安全经过多年研究和发展，在风险分析和安全方案维度已有不小进步，ROS
2中已有了基于DDS的统一安全框架。但是对于ROS甚至整个机器人系统来说，在安全标准与规范、DDS标准与实现差异、DDS安全与性能、全系统方案等维度，还有很多工作可以改进。

  

 **1** **、安全标准**

自动驾驶领域已经有相对完整、成熟的安全标准，包括功能安全（Functional Safety）标准ISO 26262、网络安全（Cyber
Security）标准ISO 21434。但在机器人领域，现有工业机器人标准ISO 10218、ISO 20218、ISO/TS
15066、服务机器人标准ISO 13482、ISO
23482等主要面向功能安全，尚无权威的网络安全标准。但是，随着服务机器人应用推广、机器人网络安全研究、及产业联盟的推动，机器人网络安全标准是必然趋势。

  

 **2** **、安全方案**

在安全方案维度，针对现有方案的问题或盲点，后续可见的研究趋势有：

 **一是DDS本身的成熟度演进。** 一方面，当前开源或商业DDS实现与DDS标准规范还存在差异，例如DDS-Security标准规定了5大安全特性（Authentication、Access Control、Cryptographic、Logging、Data
Tagging），而多数方案仅实现前3种强制特性；另一方面，开源DDS实现目前还存在性能、稳定性问题，质量成熟度不高。

 **二是基于DDS-Security安全方案的性能调优。** 一方面，在安全研究第三阶段，已有很多论文对DDS-Security方案的性能进行过深入分析，如加密算法对通信性能影响、DDS-Security使能及Governance配置对整体性能影响等，但仍缺乏相对全面、精细的性能调优实践、指导。而ROS系统中不同节点、不同消息的安全需求并不完全一致，面向性能优化的安全策略对方案实施有积极意义。另一方面，社区中DDS-Security使能对应的demo样例相对简单、对应安全文档匮乏，用户学习和配置困难，不利于方案推广。

 **三是安全研究从ROS框架扩展到机器人全系统。** 在SROS/SROS2聚焦解决ROS本身安全问题后，作为ROS执行环境、存储载体的Host
OS的安全和风险受到更多关注。例如SROS 2中秘钥证书默认明文存储在Host
OS指定目录下，无额外安全措施。业界libddssec方案通过TEE技术（ARM
Trustzone）解决秘钥证书安全存储问题，为机器人系统提供了可信计算和可信根能力，提升系统整体安全性。除软硬件安全能力应用外，一些研究倾向借用传统安全方案如IDS（Intrusion
Detection System）部署缓解Host风险，一些研究倾向于在机器人全系统中实施零信任方案，如Zero Trust in Robotics。

 **Zero Trust in Robotics**

https://news.aliasrobotics.com/zero-trust-architecture-robotics/

本期对于ROS的安全方案和趋势介绍就到这里，如有兴趣大家可留言探讨， **在下期当中，** 京东安全将对 **基于DDS协议的SROS
2方案详情以及实践经验** 同大家进行分享，感谢关注！

 **（本文原创自京东安全，转载请注明出处）  
**

