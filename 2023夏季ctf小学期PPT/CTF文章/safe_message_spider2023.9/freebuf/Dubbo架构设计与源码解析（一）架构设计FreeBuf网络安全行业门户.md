![](https://image.3001.net/images/20221219/1671417350_639fce0648f7c3868dc11.png!small)

## **一、架构演变**

单应用架构 ----> 垂直架构 ----> 分布式架构 ----> 微服务架构 ----> 云原生架构

![](https://image.3001.net/images/20221219/1671417350_639fce06f3f38bcc2dca9.jpg!small)

##  **二、Dubbo总体架构**

![](https://image.3001.net/images/20221219/1671417351_639fce07c25c0d27fb2ac.png!small)

###  **1、角色职能**

•Container：服务容器 （tomcat、jetty、weblogic）

•Provider：服务提供者

•Consumer：服务消费者

•Registry：注册中心（zookeeper、Nacos 、Apollo）

•Minitor：监控中心

###  **2、调用流程**

（1）服务容器负责启动，加载，运行服务提供者。

（2）服务提供者在启动时，向注册中心注册自己提供的服务。

（3）服务消费者在启动时，向注册中心订阅自己所需的服务。

（4）注册中心返回服务提供者地址列表给消费者，如果有变更，注册中心将基于长连接推送变更数据给消费者。

（5）服务消费者，从提供者地址列表中，基于软负载均衡算法，选一台提供者进行调用，如果调用失败，再选另一台调用。

（6）服务消费者和提供者，在内存中累计调用次数和调用时间，定时每分钟发送一次统计数据到监控中心。

##  **三、Dubbo分层架构**

![](https://image.3001.net/images/20221219/1671417352_639fce088acc30a3f549d.png!small)

• **Config 配置层** ：对外配置接口，以 `ServiceConfig`,
`ReferenceConfig`为中心，可以直接初始化配置类，也可以通过 spring 解析配置生成配置类

• **Proxy 服务代理层** ：服务接口透明代理，生成服务的客户端 Stub 和服务器端 Skeleton, 以
`ServiceProxy`为中心，扩展接口为 `ProxyFactory`

• **Registry 注册中心层** ：封装服务地址的注册与发现，以服务 URL 为中心，扩展接口为 `RegistryFactory`,
`Registry`, `RegistryService`

• **Cluster 路由层** ：封装多个提供者的路由及负载均衡，并桥接注册中心，以 `Invoker`为中心，扩展接口为 `Cluster`,
`Directory`, `Router`, `LoadBalance`

• **Monitor 监控层** ：RPC 调用次数和调用时间监控，以 `Statistics`为中心，扩展接口为 `MonitorFactory`,
`Monitor`, `MonitorService`

• **Protocol 远程调用层** ：封装 RPC 调用，以 `Invocation`, `Result`为中心，扩展接口为 `Protocol`,
`Invoker`, `Exporter`

• **Exchange 信息交换层** ：封装请求响应模式，同步转异步，以 `Request`, `Response`为中心，扩展接口为
`Exchanger`, `ExchangeChannel`, `ExchangeClient`, `ExchangeServer`

• **Transport 网络传输层** ：抽象 mina 和 netty 为统一接口，以 `Message`为中心，扩展接口为 `Channel`,
`Transporter`, `Client`, `Server`, `Codec`

• **Serialize 数据序列化层** ：可复用的一些工具，扩展接口为 `Serialization`, `ObjectInput`,
`ObjectOutput`, `ThreadPool`

##  **四、Dubbo六大核心能力**

###  **1、面向接口代理的高性能RPC调用**

提供高性能的基于代理的远程调用能力，服务以接口为粒度，为开发者屏蔽远程调用底层细节。

###  **2、服务自动注册和发现**

支持多种注册中心服务，服务实例上下线实时感知。

###  **3、负载均衡和智能容错**

内置多种负载均衡策略，智能感知下游节点健康状况，显著减少调用延迟，提高系统吞吐量。

###  **4、高度可扩展能力**

遵循微内核+插件的设计原则，所有核心能力如Protocol、Transport、Serialization被设计为扩展点，平等对待内置实现和第三方实现

###  **5、运行期流量调度**

内置条件、脚本等路由策略，通过配置不同的路由规则，轻松实现灰度发布，同机房优先等功能。

###  **6、可视化的服务治理与运维**

提供丰富服务治理、运维工具：随时查询服务元数据、服务健康状态及调用统计，实时下发路由策略、调整配置参数。

##  **五、RPC通信协议**

分布式框架的核心是RPC框架，RPC框架的核心是RPC协议。RPC是指服务之间远程调用协议，也就是指明了服务之间接口调用，进行序列化和网络传输的约定。

![](https://image.3001.net/images/20221219/1671417354_639fce0acd2876987041a.png!small)

![](https://image.3001.net/images/20221219/1671417355_639fce0b7f2085b05d203.png!small)

Dubbo提供了 Triple(Dubbo3)、Dubbo2 协议， 第三方协议进行了集成，包括
gRPC、Thrift、JsonRPC、Hessian2、REST
等。其中RPC协议包含：服务提供者的IP地址、协议指定开放端口、运行服务、协议报文编码、序列化方式

##  **六、负载均衡和集群容错**

###  **1、负载均衡**

Dubbo 提供的是客户端负载均衡，即由 Consumer 通过负载均衡算法得出需要将请求提交到哪个 Provider 实例。在集群负载均衡时，Dubbo
提供了多种均衡策略，缺省为 random随机调用。

算法| 特性| 备注  
---|---|---  
RandomLoadBalance | 加权随机 | 默认算法，默认权重相同  
RoundRobinLoadBalance| 加权轮询 | 借鉴于 Nginx 的平滑加权轮询算法，默认权重相同  
LeastActiveLoadBalance| 最少活跃优先 + 加权随机 | 背后是能者多劳的思想  
ShortestResponseLoadBalance| 最短响应优先 + 加权随机 | 更加关注响应速度  
ConsistentHashLoadBalance| 一致性 Hash | 确定的入参，确定的提供者，适用于有状态请求  
  
### **2、集群容错**

在集群调用失败时，Dubbo 提供了多种容错方案，缺省为 failover 重试

![](https://image.3001.net/images/20221219/1671417356_639fce0c072d4e09b80d3.png!small)

  

容错机制| 特性  
---|---  
Failover| 失败自动切换  
Failfast| 快速失败  
Failsafe| 失败安全  
Failback| 失败自动恢复  
Forking| 并行调用多个服务器  
Broadcast| 广播调用所有提供者  
  
##  **七、设计思想**

###  **1、领域模型**

• **Protocol 服务域** ：Invoker 暴露和引用的主功能入口，它负责 Invoker 的生命周期管理

• **Invoker 实体域** ：Dubbo 的核心模型，其它模型都向它靠拢，或转换成它，它代表一个可执行体，可向它发起 invoke
调用，它有可能是一个本地的实现，也可能是一个远程的实现，也可能一个集群实现

• **Invocation 会话域** ：持有调用过程中的变量，比如方法名，参数等

###  **2、基本设计原则**

• **Microkernel + Plugin 模式** ：Microkernel 只负责组装 Plugin，Dubbo
自身的功能也是通过扩展点实现的，也就是 Dubbo 的所有功能点都可被用户自定义扩展所替换

• **URL** ：采用 URL 作为配置信息的统一格式，所有扩展点都通过传递 URL 携带配置信息

##  **八、总结**

####
至此，Dubbo总体架构与核心模块介绍完成，文中如有不当或者错误观点，欢迎大家评论区指出。感兴趣的同学，可以关注后续“Dubbo架构设计与源码解析”系列的文章。

 **作者：黄金**

