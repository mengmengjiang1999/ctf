## 项目背景

 **公司项目需要将分布在多台机器中的日志统一收集管理。笔者先后使用logstash，flume等开源项目。并最终自研一套基于Java语言的日志收集系统
Bloodhound。以下从项目关注的角度对开源系统与自研进行分析。**

### 1 开源日志收集系统特征

Logstash 和 Flume 都是很成熟的日志收集平台，结构清晰，插件丰富，文档简明易懂，示例代码非常多。其中Logstash
侧重对字段的预处理，Flume 侧重不同的网络拓扑中日志的传递，通过Agent打通各个网络结点。

### 2 关于日志收集系统的考量

 **开发语言的选择**

公司的开发团队主要集中在 Java，Python。而 Logstash 的插件使用 Ruby，从团队角度，不太具备扩展性。在使用 logstash
增加一个插件比较痛苦，同时几个月使用下来，感觉性能偏低，启动时较慢。

**性能的考虑**

Flume性能相对比较低，主要有以下几点：

① 单线程。

Flume 每个 Agent 分为 source,channel,sink 等插件。每个插件都只启用单线程处理。如果任务是写数据库等 IO
操作，性能必然会被拖累。

②source的Timer机制

Source 线程在检测有新的更新，会一直读取推向 Channel，当所有的更新处理完毕，线程会退出。启动一个 Timer
线程。定期3秒重新启动，如此反复。在这个过程中，没有充分利用 Java 的多线程通知机制，每次启动都有一些调度，排队，检测及任务初始化过程。影响性能。

③Flume事务机制

Flume 本身已对事各进行了优化，允许批量提交事件。但本质上还是需要检测Sink的处理结果，再进行 Commit 或 Roolback。

 **管理的考虑**

如果将一个 agent 的任务处理串，source->channel->sink 理解为一个任务(这个任务是个抽象的概念，Flume
里并没有这个概念)，那么 Flume 从业务脚度上看，就是单任务收集系统。如果需要同时处理两个任务，必须开启两个 Flume Agent
进程。随着收集任务的增加，必然会大大增加管理成本。

![图片1.png](https://image.3001.net/images/20180412/15235206165790.png!small)  

(flume处理：多进程处理多任务)  

![图片2.png](https://image.3001.net/images/20180412/15235206406343.png!small)

(Bloodhound处理：单进程处理多任务)  

此外，我们还有监控需求，统计需求，任务管理等。这些任务需要和我们的 grafana 平台打通。综合考虑下，我们选择自研日志收集系统。

## BloodHound系统

### 项目名称来源

From wikipedia:

The Bloodhound is a large scent hound, originally bred for hunting deer, wild
boar, and since the Middle Ages for tracking people. Believed to be descended
from hounds once kept at the Abbey of Saint-Hubert, Belgium, it is known to
French speakers as the Chien de Saint-Hubert.

This breed is famed for its ability to discern human scent over great
distances, even days later. Its extraordinarily keen sense of smell is
combined with a strong and tenacious tracking instinct, producing the ideal
scent hound, and it is used by police and law enforcement all over the world
to track escaped prisoners, missing people, lost children and lost pets.

“嗅觉最灵敏的猎犬，寓意是能从包括流量在内的各种粗糙的原始数据中提炼中初步有价值的信息。”

### 项目需求

> 多任务管理系统
>
> 强扩展性
>
> 任务监控
>
> 高性能

### 项目架构

![图片3.png](https://image.3001.net/images/20180412/15235209886891.png!small)  

### 系统分层

核心框架层

为了充分利用Flume的功能特性，我们也将Bloodhound拆分层source->channel->sink三个层次。这个设计是为了充分利用Flume中的丰富插件资源，请参照以下配置文件。

![图片4.png](https://image.3001.net/images/20180412/15235211069639.png!small)  

时序图

![图片5.png](https://image.3001.net/images/20180412/15235211357712.png!small)  

**source 层**  

source为数据输入，通常为文件，消息系统等。示例中的Source为Redis，Source为单独运行的线程，从Redis中指定的队列中获取输入，读取完成后则推向
Channel。当 Channel 中队列已满时，则 source 线程则进入等待。

 **Channel 层**

Channel 作为枢钮,连接 Source 和 Channel，主要功能如下：

> 维护一个队列，接受 source 的 put，向 Sink 发送处理。
>
> 管理一个线程池，调度 Sink 任务。由于 Sink 通常较慢，因此整个核心模块中，只有 Sink 为多线程处理，其余均为单线程执行。
>
> 控制QPS，可以使用令牌或漏斗，主要目的是保护高并发写入的环境下，Sink 对应的数据库或 Redis。不至于压力过大，影响正常业务请求。
>
> 发送 Metrics，提供实时监控数据来源。

Channel 层主要的方法有：popEvents, addEvents, notifyEvents, sendMetrics等。

 **Sink 层**

Sink 层为一个 Runnable，接受 Events，被 Channel 调度，执行最终的落地逻辑。

以上三层中，Channel 层有 MemoryChannel 和 FileChannel，如果任务比较重要，应该选择
FileChannel，可以保证进程中断后，Event 不会被丢失。MemoryChannel 管理一个 Queue，性能相对比较高。Source 和
Sink 可以大量复用Flume中的插件代码。

 **任务管理器**

任务管理器，故名思义是管理整个日志收集系统的管理模块。

1 任务管理

> 任务注册接口：可通过任务注册接口向整个进程提交一个任务，如配置所示，任务注册接口是通过一个 http post 方法提供注册并启动一个新的任务。
>
> 数据提交接口：默认情况下，Source 是 pull 模式，从文件中，队列中拉取日志。同时也支持 http
> 方式提交。数据提交接口需要传递两个参数，jobName 和 events 。

2 任务监控

> 查看任务执行情况：在grafana中查看各个任务执行情况，这个数据由核心框架层提供。
>
> 查看任务运行情况：提供列表，查看任务状态，启动，停止任务。
>
> 系统运维层
>
> 进程管理：使用supervisor管理进程。
>
> 调度器：根据各个业务情况，使用调度任务对任务进行管理。调用任务管理中的任务启动，停止等。这一块和日志收集核心不太相关，就不再赘述。

## 结语

笔者从事过多个项目需要使用日志收集，同时也使用了 logstash, flume
等开源系统，总体感觉开源系统比较成熟，有大量插件，事务管理。但和自已业务系统结合不够紧密。自研框架工作量较大，也会有很多坑，优势是较好的和业务接轨。

 ***本文作者：踏浪无痕@岂安科技，转载请注明来自FreeBuf.COM**

