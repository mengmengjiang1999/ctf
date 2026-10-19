随着近年来国内机器人领域的不断升温，机器人智能化逐渐进入人们的视野，其中，不少厂家都在使用 **Robot Operation
System（机器人操作系统，以下简称ROS）**
。但是，因ROS诞生于实验室相对封闭的环境，因此一开始对于安全性的研究并未受到开发者的重视，导致ROS存在着诸多安全上的问题，随着开源和ROS的大热，很多安全问题也随之暴露出来，成为安全从业者研究的热门方向。

 **《探秘ROS安全系列》** 是京东安全自主研究和编写的系列文章，此系列将从
**ROS简介＆背景、ROS安全方案、ROS安全方案注解、京东ROS安全研究实践4个部分**
，详细介绍京东安全对于ROS安全的研究和实践，希望能够与大家一同探讨。

 **本文将从ROS背景、机器人安全研究两个部分，供大家先行了解ROS及其安全方面的研究情况** ，以下，enjoy~

（全文3137字，阅读时间约10分钟）

一、ROS背景

 **1** **、ROS研究缘起**

国际机器人联盟（IFR）将机器人划分成 **工业机器人** 和 **服务机器人**
两类。工业机器人出现较早，主要用于自动化制造领域，如焊接、装配等；服务机器人指用于非制造领域、以服务为核心的自主或半自主机器人，包括个人/家用服务机器人（扫地）、商用服务机器人（接待/巡检）、物流/仓储机器人（搬运/分拣）、医疗服务机器人（运送/辅助）等，IFR
Word Robotics 2020预测服务机器人继续保持高速发展。

![](https://image.3001.net/images/20210402/1617349148_6066ca1c1c7f7e4658f49.png!small)

（图片来源为IFR Word Robotics 2020报告）

与传统工业机器人相比，服务机器人的工作环境更开放、网络连接更丰富、功能应用更智能，和用户、环境、数据的交互更深入，随着服务机器人在多领域推广应用，机器人的安全、数据和隐私保护等问题越来越受到关注。
**当前，服务机器人主流基于开源机器人操作系统ROS构建** ，故ROS系统安全性也成为研究热点。

 **2、ROS的发展**

 **ROS（Robot Operation
System）虽然名字叫操作系统，但并非传统意义的操作系统（如Linux、Windows、Android等），而是一种开源的机器人软件中间件（Robotics
Middleware）**
。ROS通过集成软件库、协议、工具等组件，构建适合多种机器人的通用软件框架，提高代码复用，降低开发难度，在机器人、无人机、自动驾驶等产品得到广泛应用。

![](https://image.3001.net/images/20210402/1617349205_6066ca55210b208fc2f96.jpg!small)

ROS项目最早可追溯到斯坦福大学的STAIR（Stanford Artificial Intelligence Robot）和PR（Personal
Robotics）的研究项目。

2007年Willow Garage公司参与合作并基于ROS早期原型开发了PR2产品（Personal Robotics 2）。

2010年1月ROS 1.0 (PR2 Milestone 3)第一个版本发布，2010年7月PR2产品开始上线和销售。

2012年开源机器人基金会Open Source Robotics Foundation（OSRF）成立。

2013年ROS项目移交给OSRF（2017年更名为Open Robotics）并维护至今。

![](https://image.3001.net/images/20210402/1617349253_6066ca855cdb10f2a7c61.jpg!small)ROS
1.0和PR2

 **ROS历史上有两个大版本，即ROS 1.0和ROS 2.0** 。为使ROS版本有相对稳定的开发环境，版本发布有节奏跟随Ubuntu发行版，详情可参考
ROS1 Release Schedule 或ROS2 Release Schedule。

 **ROS1 Release Schedule参考链接**
http://wiki.ros.org/Distributions#Release_Schedule

 **ROS** **2 Release Schedule参考链接**

https://www.ros.org/reps/rep-2000.html

ROS 1.0活跃版本信息如下左图所示，2020年Noetic是ROS 1.0最后一个官方LTS版本。

![](https://image.3001.net/images/20210402/1617349294_6066caae6be8a1624b5f9.jpg!small)

未来ROS社区主要发布和维护ROS 2.0 版本。ROS 2.0版本信息如下右图所示，最新LTS版本为Foxy。

![](https://image.3001.net/images/20210402/1617349307_6066cabbe38c1b412cf6a.jpg!small)

 **3、ROS的架构**

 **1）ROS1.0架构**

 **ROS 1.0设计目标是解决：因缺乏通用软件组件，导致机器人应用或硬件有差异时，软件复用率低、开发量巨大的问题。**
应用场景主要聚焦在：专业用户（科研团队）、封闭环境（实验室等）、单机器人、无实时性要求等。安全不在设计目标内。

ROS 1.0架构核心是基于message 的松耦合、分布式架构。核心概念包括：

 **【Node】** 执行特定任务的进程。一个可执行程序可以创建一个或多个node

 **【Master】** 特殊node，提供全局管理功能和服务，如参数服务、node查找、消息注册等

 **【Message】** node之间的通信消息体，类似OS消息概念

 **【Topic】** 消息发布和接收的载体，publish-subscribe机制，异步通信

 **【Services】** 另一种基于消息的通信机制，request-reply机制，同步通信

![](https://image.3001.net/images/20210402/1617349329_6066cad10513232e58f62.jpg!small)

![](https://image.3001.net/images/20210402/1617349341_6066cadd8ddefe969c3af.jpg!small)

 **2）ROS2.0架构**

随着ROS 1.0和各种机器人产品应用推广，涌现了 **新的ROS需求，如多机器人支持、嵌入式平台支持、实时性需求、商用产品质量、开放环境等**
。同时开源社区也出现众多可借鉴的技术，如DDS（Data Distribution
Service）数据分发服务。在上述背景下，ROS重新设计开发了2.0版本。

 **ROS 2.0相比ROS 1.0的主要差异点** 可参考下图，主要在于 ：

1）新特性：多机器人系统支持、良好的通信实时性、商用级代码质量、嵌入式平台支持

2）取消master节点，实现“去中心化”

3）引入DDS中间件，替换ROS 1.0自研消息通信机制

4）支持多种Host OS平台，如Linux、Windows、Mac、RTOS

5）安全，DDS协议有5大安全标准（下图Plugin），ROS 2利用DDS 安全特性解决了身份认证、加密通信、访问控制等已知风险

![](https://image.3001.net/images/20210402/1617349360_6066caf0efffba0e3b7c7.jpg!small)

![](https://image.3001.net/images/20210402/1617349373_6066cafda277f5bf56cc4.jpg!small)

 **3）ROS系统搭建**

ROS作为中间件，需运行在Host OS之上。当前官方支持Host有Ubuntu
Linux、Windows、macOS。以Ubuntu为例，ROS支持apt安装和源码安装两种方式，大家可参考安装并运行demo体验ROS机制。业界也有更丰富的机器人仿真环境，如TurtleBot3
Simulation，如感兴趣可自行参考。

 **apt安装参考链接**

https://docs.ros.org/en/foxy/Installation/Linux-Install-Debians.html）

 **源码安装参考链接**

<https://docs.ros.org/en/foxy/Installation/Linux-Development-Setup.html>

 **二、ROS机器人安全研究**

 **1** **、ROS机器人安全研究阶段**

机器人系统是一种Cyber-Physical
System（信息物理系统），特点是网络领域的威胁攻击最终可能影响到物理世界安全。我们回顾业界机器人安全研究文章（见下图），将其分为三个阶段：

 **1）第一阶段，2008-2012年ROS发展初期** ，研究对象相对零散具体，表现在对特定机器人应用场景的威胁分析，比如救援机器人（Rescue
Robot）、家用机器人（Household Robots）、远距医疗机器人（Telesurgical Robot）、无人机（Unmanned Aerial
Vehicle）等。风险分析主要聚焦在远程通信和控制安全，如高效远程认证、远距医疗ITP（Interoperable Telesurgery
Protocol）协议等；另外也有相对综合性的分析，如对家用机器人和无人机产品的系统级安全和隐私分析。这些研究侧面反映了当时机器人缺乏统一底层框架、缺乏通用远程架构的情况。

![](https://image.3001.net/images/20210402/1617349430_6066cb36aca4ac271db4d.jpg!small)

（机器人ROS安全研究回顾）

 **2）第二阶段，2013-2017年ROS 1.0发展成熟期**
，涌现了大量面向ROS机器人的安全分析和方案，相比第一阶段，研究对象更聚焦ROS框架，同时呈现许多新特征。具体如下：

2012年Defcon@20会议现场，研究者举办了一个针对ROS小车的攻击测试，结果发表在2013年《A preliminary cyber-physical security assessment of the Robot Operating System
(ROS)》论文中。测试显示，攻击者可成功发送指令控制小车，同时也出现了摄像头功能失效、本地控制主机硬盘错误等无法分辨是攻击还是软件异常的情况。一方面验证了ROS系统已知安全风险(如无身份认证、明文通信等)，一方面也反映了Cyber-Physical系统的复杂性。下图是该测试小车、软件架构、现场部署环境。

![](https://image.3001.net/images/20210402/1617349537_6066cba12bc1933e302c9.png!small)

（图片引自上述论文）

该测试和论文成果开启了对ROS的安全研究热潮，并呈现出新趋势：从对单一机器人场景到共性安全问题分析、从对特定机器人架构到对通用ROS框架分析、从ROS
Application-level应用层方案到ROS框架通信层（Communication
Channel）、从通信安全到系统访问控制、从安全特性到安全性能评估、从ROS框架安全到机器人全系统安全。

在这些分析过程中，ROS 1.0框架主要安全风险充分暴露：匿名通信无身份认证、消息明文传输、缺少访问控制等。ROS 1.0安全风险是有根源的，因为ROS
1.0设计之初就没有将安全作为目标和需求。关于这点，Open Robotics的CEO Brian Gerkey在2016年 ROS-Industrial
Conference有过如下表述“ **If you claim that you've found a security hole in ROS 1,
you're lying; there is no security** ”。

![](https://image.3001.net/images/20210402/1617349590_6066cbd60d38f01e3dcf4.png!small)

（图片引自ROS Answers论坛和ROS-Industrial Conference2016材料）

在此阶段，也涌现了多个针对ROS 1.0主要风险的安全方案，如roauth、ROSRV、SROS等。 **方案详情我们将在下篇文章中发布。**

2017年《The Role of Security in Human-Robot Shared Environments A Case Study in
ROS-based Surveillance Robots》文章是一次综合考虑风险和消除方案、定制化安全（如多机器人通信协同）需求、全系统设计的尝试。

![](https://image.3001.net/images/20210402/1617349612_6066cbec33b874d6f4230.jpg!small)

（图中为上述论文STOP R&D项目综合安全分析和消除方案）

 **3）第三阶段，2018年后ROS 2.0发展期** ，随着2.0架构升级和DDS集成，安全研究呈现两个特点，一是研究对象从ROS 1.0过度到ROS
2.0，二是对安全方案性能的分析。

 **首先，ROS 2.0采用DDS替换了ROS 1.0自研的publish-subscribe通信机制。**
而DDS本身有Security安全协议规范，因此ROS 2.0安全主要基于DDS-Security。ROS 2.0中DDS-Security默认不使能，使能DDS-Security需打开配置并重新编译。

《Robot Operating System 2: The need for a holistic security approach to
robotic architectures》综合分析了ROS2系统的安全风险，并针对DDS-Security使能和安全配置项（如governance
policy） **对性能影响进行了定性分析** 。

 **也有对具体性能的定量** **分析** ——如《Message encryption in robot operating system:
Collateral effects of hardening mobile
robots》继承2016年性能分析文章，评估了3种算法（3DES、AES、Blowfish）对不同类型消息加密后的性能（时延、吞吐量）、系统（网络负载增量、CPU占用率、电池损耗）的影响，提出了针对不同消息类型，有策略的选择加密算法的观点。《Security
and Performance Considerations in ROS 2: A Balancing Act》针对ROS2使能DDS-Security进行了深度分析，对比了ROS 2、ROS 2 + DDS Security Enable、ROS 2 +
VPN三种场景下通信性能指标，结果显示使能DDS-Security时性能均有不同程度劣化。

上述针对ROS 2+DDS的定性和定量分析，都显示使能DDS-Security安全后性能下降比较严重。但同时也应该注意到， **ROS 2+DDS-Security实际是可以根据安全需求进行精细化配置的，性能调优有较大空间。**

 **2** **、ROS威胁建模**

在业界关于机器人系统安全研究基础上，ROS社区创建了ROS2 Threat Model威胁分析模型，对基于ROS 2的机器人系统，进行了全方位的威胁建模，
**采用了业界标准的STRIDE和DREAD分析方法**
，定义系统元素并绘制数据流图，再对各元素进行威胁分析、制定风险消除方案。分析维度全面，可归纳概括有：内外部通信、远程控制/应用接口、主机系统和内核、端侧数据存储、云服务和云存储、云-端通信服务等。

下图是ROS 2系统通用STRIDE数据流图。

 **ROS2通用威胁建模**

https://design.ros2.org/articles/ros2_threat_model.html

![](https://image.3001.net/images/20210402/1617349637_6066cc0510f73426d2b98.jpg!small)

（图片来源为ROS2通用STRIDE威胁建模分析）

实际上针对具体产品，由于通信方式、业务功能、云-端服务部署等差异，数据流图可能要复杂的多，需要具体分析，大家可参考Turtlebot3的威胁分析。

 **Turtlebot3产品威胁建模**

https://design.ros2.org/articles/ros2_threat_model/ROS2_Application.png

 **3** **、ROS安全设计**

在上述安全研究和威胁建模分析过程中， **业界对ROS安全方案设计主要有两种思路：**

 **一种是网络隔离** ，即利用专网、VPN、防火墙等手段，构建ROS网络隔离区，缩小风险面。

 **另一种是基于ROS框架进行安全加固** ，代表有前文提到的ROS 1.0阶段的rosauth、ROSRV、SROS等、以及ROS
2.0阶段的SROS2。

本期对于ROS背景及安全研究的介绍就到这里，如有兴趣大家可留言探讨， **在下期当中，** 京东安全将对于 **ROS的安全方案详情以及未来的安全趋势**
同大家进行分享，感谢关注！

 ****

 **（本文原创自京东星辰安全实验室，转载请注明出处）  
**

 ****

 **京东星辰安全实验室(Dawn Security Lab, JD.com)**
是京东安全旗下研究团队，专注于基础系统、应用和泛IoT领域前沿安全技术探索和产品建设，目前研究方向有操作系统和应用安全、隐私保护、泛IoT安全（如机器人ROS安全、物联网设备安全）等。

