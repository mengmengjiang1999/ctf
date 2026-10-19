# 《ICS3Fuzzer: A Framework for Discovering Protocol Implementation Bugs in ICS
Supervisory Software by Fuzzing》论文笔记

阅读量 **121629**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2022-02-22 14:30:00

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t01ff66c585eb29aee3.jpg)

## abstract+introduction

###  背景

工控网打破了工业物联网中假定的每个系统相互分离的限制，引入的威胁。工控网中的目标主要分为两类：一类是控制控制生产过程的设备，另一类是控制这些设备的监控软件supervisory
software。

###  问题

专注于分析针对PLC设备的supervisory software，特别是寻找其中有关协议实现的漏洞。（攻击面）

###  目前工作及其缺点

目前针对ICS内部的supervisory
software的fuzzing工作较少，并且受限，主要是三个方面：通常是运行在windows上的闭源程序，并且体量较大，严重依赖GUI；通常作为客户端，这对于fuzzer来说不易测试；通常使用专有协议进行通信，并且协议状态是和GUI紧耦合的。

现有fuzzing工作与ICS3fuzzer特性对比图

![](https://p5.ssl.qhimg.com/t010c7b2e892bae0b45.png)

###  挑战

  1. 闭源、体量大
  2. 与GUI操作紧耦合
  3. 私有协议

###  论文工作

提出了ICS3Fuzzer，ICS Supervisory Software Fuzzer，一个可移植的、模块化的，能够自动化测试supervisory
software的fuzzing框架。

**没有直接分析提取协议实现（因为十分困难），而是直接在同步控制GUI操作以及网络通信的情况下，直接运行和fuzz对应的supervisory
software。**

ICS3Fuzzer是黑盒的，通过自动化地输入专门生成地有效地输入并到达不同的协议状态，来持续地驱动整个过程。并且提出了新的fuzzy策略，倾向于更有可能发生漏洞的状态。测试目标时是结合模拟测试与实际测试的优缺点。

贡献：

  1. 设计实现了ICS3Fuzzer
  2. 提出了新的fuzzing策略
  3. 结果好，并开源

## BACKGROUND AND MOTIVATION

###  ICS Architecture

典型的ICS系统由三层,分别是（1） **Field Instrument Control Layer**
，由传感器（senior）和执行器（actuator）构成，用来进行系统的输入和输出（2） **Process Control Layer**
，由专用嵌入式设备组成，比如PLC/RTU，用来控制实时进程（3） **Supervisory Control Layer**
，由几个工作站组成，用来提供实时监控以及控制系统的设备。

![](https://p1.ssl.qhimg.com/t0116a117dc26d0d807.png)

ICS系统的几个显著的特点：

  1. ICS直接与物理世界进行交互，因此其中的安全问题往往会造成更大的危害。
  2. ICS必须可靠并且满足实时约束，必须使用实时操作系统，并且特定领域协议（domain-specific protocols）被用来在上述三层之间进行通信，并且协议往往未被加密。
  3. ICS的网络是air-gaped，即与外部网络隔离，因此其中往往缺少很多安全性措施。但是随着IIOT的发展，这种隔离逐渐被削弱，因此会带来很多问题。

ICS系统中supervisory
software的共同特点为，都提供了用于读可操作变量、开启/停止PLC、下载固件等接口，这些功能在一个指定的信道进行通信，通信数据包含如下内容：

  1. 实时设备状态：sensor reading、feedback of control command exectuion、heartbeat messages
  2. 设备信息：device name、version、model、manufacturer
  3. structured data block: program blocks、memory blocks、 diagnostic files

###  Security Risks Exposed by Supervisory Software

生产系统种涉及OT和IT网络，supervisory
software运行在OT网络种，并且OT网络与IT网络之间存在强大的隔离，但是APT攻击往往能够穿透这层隔离。

####  Assumption

假设攻击者已经控制了ICS北部一台主机，并且能够监控、拦截、修改ICS内部主机之间的通信，即MITM attack。

####  Attack Approaches and Consequences

主要通过两种方式，一种是修改报文，使得Supervisory software 崩溃，另一种是利用Supervisory
software已有逻辑执行恶意命令。

![](https://p1.ssl.qhimg.com/t01ff91ab0b86eaa7aa.png)

## DESIGN OVERVIEW

###  Movitating Example

下图表示的是supervisory software GX Words2和PLC之间的TCP session，在这个过程中，为了获取网络数据公开了许多
**input states** ，并且在每一个特殊的input state下，supervisory software都在等待一种特定的来自PLC
设备的报文。

我们定义一种session type作为一种 **functionality** ，双向交换报文。functionality是一种supervisory
semantic，例如向PLC中下载程序、开启PLC等等。

![](https://p3.ssl.qhimg.com/t018517e413c02bda66.png)

####  Key observartion

  1. TCP session的开始往往是一种按钮操作（可理解为人工操作），有人类通过GUI界面完成。
  2. 在session期间，在许多情况还需要额外的按钮操作来完成交互。
  3. session通过周期性的交换heartbeat报文或者停止报文交换来结束此session。

####  New Insight

Supervisory software在不同的interaction states时往往有着不同的行为（code
execution），Supervisory
software的交互状态本质上是与PLC设备进行交互的特定的程序上下文；交互状态取决于几个因素，包括之前的按钮操作、之前的input
states等。Supervisory software的实现与GUI接口是高度耦合的。

###  Challenges

  1. **C1：Guiding the supervisory software to enter a specific input state.**

每个session都涉及了许多input states，为了能够达到针对input states较好的覆盖需要克服三个困难：

**首先** TCP session初始化是由作为client的supervisory software发起的，因此fuzzing
tool需要等待接收supervisory software发起的请求； **其次**
为了fuzz一个特定的输入状态，我们需要使得supervisory多次到达正确的交互状态，这需要同步三种事件，GUI操作、supervisory
software中的代码执行情况、设备的响应。没有设计专门的机制来自动且同步地操控GUI操作以及网络流量，很难做到这一点； **还有**
由于状态之间复杂的依赖关系，很多情况下都需要supervisory
software先到达某个特定状态，然后才能到达目标状态，然而仅仅是识别出相对完整的状态集合已经十分困难。

  1. **C2：Fuzzing proprietary protocols with unknown message frame format and state-space.**

不知道状态空间就无法探索深度的程序路径以及深度的协议状态；不知道报文格式，就无法推断出报文字段值的约束关系，无法高效地生成有意义输入。

  1. **C3：Simulating the session of proprietary protocol.**

对于每个supervisory
software发出的请求，都必须对其提供一个相应的回应，因此需要模拟这个session，但是这需要针对proprietary
protocols有一个全面的理解。

###  Solutions to Challenges

**为了解决挑战C1** ，我们设计了一个新的控制机制，通过自动准确地同步GUI操作以及网络通信，到达任何被识别的input states。

**为了解决挑战C2** ，采用 **已有工作来逆向** 报文的格式，并且进行 **差异性分析识别字段与约束**
；为了识别协议状态以及过滤无效状态，不参用逆向的办法，而 **是建立基于执行路径与对应输入的state-book**
；为了能够对state能够达到较好地覆盖，提出新的切换state的策略。

**为了解决挑战C3** ，通过建立一组基于真实抓包流量建立的communication templates/patterns，进行PLC
device仿真，如果匹配不到合适的回复报文，那么就采用真正的PLC device.

## DETAILED DESIGN

ICS3Fuzzer的结构如下图所示，主要分为两部分Pre-processing phase和Fuzzing phase：

  1. Pre-processing phase 
    1. Functionality analysis. 分析如何在fuzzing loop期间自动化地开启会话。
    2. Proprietary protocol analysis. 分析报文格式以及状态空间，以帮助能够选择有价值的input states和生成高效的变异数据；根据捕获的流量模拟交互报文，从而不被限制在特定的硬件中。
  2. Fuzzing phase：全自动的，并且由四步工作组成 
    1. 根据从state-book，选择一个有价值的input state。
    2. 根据得到的协议格式信息，生成变异的输入。
    3. 自动化地同步控制GUI操作以及网络通信，将变异数据喂给已选择的input state。
    4. 监控supervisory software的status并且记录malformed input。

![](https://p4.ssl.qhimg.com/t01e2c100958ab000ac.png)

###  Functionality Analysis

此部分的目的是准备进行task/functionality的UI组件，通过网络接口进行会话。利用`guiAutolit`来实现“activator”，可用来触发GUI事件，比如鼠标移动等。

具体来说，此步分为两部分：

  1. 获取GUI handle：可以通过控制GUI handle来写脚本控制GUI事件
  2. 定义操作顺序：functionality是按照特定的GUI操作顺序出发的。

最终ICS3Fuzzer可利用guiAutolit来自动化实现fuzzing。

###  Proprietary Protocol Analysis

####  Inferring Protocol Format

利用现有工具`Towards automated protocol reverse engineering using semantic
information`

####  Obtaining State-Space

此步骤目的为了定义和区分session中的input state，往往一个session中包含许多input
state，并且其中有许多相似且重复的input state。

区分input states的办法：

  1. 直接的办法：比较messages的相似性，但不准确
  2. 论文方法：记录在对应input state下的execution trace（我理解为程序对每个message的execution trace），即是messages的区别很小也有可能导致十分不同的execution traces。在fuzzing过程中，应该着重关注那些能够导致更多中execution trace的input state。

由于本论文具有通用性，所以不专门分析特定ICS protocol的输入状态，而是建立维护一个state-book，其中包括code execution
trace以及corresponding inputs，并不需要回复输入状态的特殊语义。

具体通过DynamoRIO插桩实现trace收集，并且只record/dump在消息传输阶段的message
transmission（通过hook以及track send()以及recv()）。因此在state-book中的每一个input
state都对应着一个tuple，包括original message，execution trace，以及index。

####  Device Emulation

为了不被具体的硬件限制，论文选择基于获取到的报文模拟communication。

具有两个挑战：

  1. 当supervisory software初始化一个request时，需要根据抓取到的报文识别出对应的response.
  2. 需要调整对应报文中的动态字段。

对应上述挑战的解决办法：

  1. 设备中的request-response一般是非常相似的，可以根据抓取的报文建立对应关系。
  2. 根据人工总结的经验，加上人工分析，识别定义出报文中的动态变化字段。

如果上述办法仍然不能获取对应的response，那么就需要借助于真是的PLC device。最终ICS3Fuzzer可以对每个supervisory
software的request产生对用的response。

###  State Selection

对state-book中记录的input state中的三个属性，index、execution trace、original
message，赋予权重，所以每一个input state都具有一个权重，那么权重就可以代表每一个input state的价值。

权重的考量基于三个hypotheses:

  1. 网络通信越深，越有可能触发bug
  2. 当message呗转发给software，那么越多的BB被触发，越有可能存在bug
  3. input越复杂，越有可能造成crash

对应上述三个hypotheses的具体做法：

  1. 使用index代表depth。但是同时需要注意消除具有相似的state，比如导致复的行为，具体来说即相似的报文以及程序执行路径。
  2. 与AFL等基于反馈的fuzzer一致
  3. 输入越复杂，编译越多样，就有可能触发新的执行路径，具体使用message内被定义的字段数来代表复杂度。

最终选取state depth、basic blocks count、field count来代表上述三个hypotheses，最终计算出state
weight。

###  Input Generation

此步骤利用获取的protocol format来生成变异的输入，主要完成两个任务：

  1. 根据你想得到的protocol format生成输入
  2. 根据得到的约束关系纠正报文字段。

###  Data Feeding

fuzzing supervisory software需要同步网络输入以及GUI操作，此论文通过proxy机制来实现了这一目标。

![](https://p1.ssl.qhimg.com/t0175ce8ae608afdb56.png)

包含了Dispatcher、GUI Proxy、Traffic Proxy，Dispatcher通过给traffic
proxy发送command来关系network traffic，通过给GUI
proxy发送command来关系GUI操作，自动化的实现了fuzzing的输入.

###  Crash Monitor

基于Windows EventLog Service来做。

没考虑由于程序挂起（program hang）导致的bug。

###  Manual Work

需要人工工作来完成预处理过程，以解决GUI操作以及protocol先验知识，主要包括四个方面：

  1. exploring GUI interface
  2. writing activators
  3. obtaining protocol knowledge，包括状态空间收集、报文template获取、协议格式逆向
  4. verifying the accuracy of the analysis.

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **random** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/267341](/post/id/267341)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [协议安全](/tag/协议安全)

 **+1** __0赞

 __收藏

![](https://p0.ssl.qhimg.com/t013b7df8df77b60cc5.png) random

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

