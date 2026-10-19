## 1 定义

Apache Flink
是一个分布式大数据处理引擎，可对有限数据流和无限数据流进行有状态或无状态的计算，能够部署在各种集群环境，对各种规模大小的数据进行快速计算。

![](https://image.3001.net/images/20230516/1684219134_646324fe2544e694efe0a.png!small)

## 2 核心概念与机制

#### 2.1 State

一般指一个具体的 Task/Operator 的状态，用于缓存 用户数据、窗口数据、程序运行时状态、数据源偏移量 等信息，State 数据默认保存在
Java 的堆内存

Flink 中有两种基本的状态：Keyed State 和 Operator State。

  1. Keyed State：基于KeyedStream 上的状态，这个状态是跟特定的 Key 绑定的。KeyedStream 流上的每一个 Key，都对应一个 State。
  2. Operator State：Operator State 与 Key 无关，而是与 Operator 绑定，整个 Operator 只对应一个 State。

比如: Flink 中的 Kafka Connector 就使用了 Operator State，它会在每个 Connector 实例中，保存该实例消费
Topic 的所有(partition, offset)映射。

Flink中状态的实现有三种：MemoryState、FsState、RocksDBState。三种状态存储方式与使用场景各不相同，详细介绍如下：

##### MemoryStateBackend

  * 构造函数：MemoryStateBackend(int maxStateSize, boolean asyncSnapshot)
  * 存储方式：State存储于各个 TaskManager内存中，Checkpoint存储于 JobManager内存
  * 容量限制：单个State最大5M、maxStateSize<=akka.framesize（10M）、总大小不超过JobManager内存
  * 使用场景：无状态或者JobManager挂掉不影响的测试环境等，不建议在生产环境使用

##### FsStateBackend

  * 构造函数：FsStateBackend(URI checkpointUri, boolean asyncSnapshot)
  * 存储方式：State存储于 TaskManager内存，Checkpoint存储于 外部文件系统（本次磁盘 or HDFS）
  * 容量限制：State总量不超过TaskManager内存、Checkpoint总大小不超过外部存储空间
  * 使用场景：常规使用状态的作业，分钟级的窗口聚合等，可在生产环境使用

##### RocksDBStateBackend

  * 构造函数：RocksDBStateBackend(URI checkpointUri, boolean enableincrementCheckpoint)
  * 存储方式：State存储于 TaskManager上的kv数据库（内存+磁盘），Checkpoint存储于 外部文件系统（本次磁盘 or HDFS）
  * 容量限制：State总量不超过TaskManager内存+磁盘、单key最大2g、Checkpoint总大小不超过外部存储空间
  * 使用场景：超大状态的作业，天级的窗口聚合等，对读写性能要求不高的场景，可在生产环境使用

#### 2.2 CheckPoint

CheckPoint（定期对状态备份并提供恢复能力的机制）则表示了一个Flink Job 在一个特定时刻的一份全局状态快照，即包含了所有
Task/Operator 的状态。  
当程序出现问题需要恢复 Sate 数据的时候，只有程序提供支持才可以实现 State 的容错。State 的容错需要依靠 CheckPoint
机制，这样才可以保证 Exactly-once 这种语义，但是注意，它只能保证 Flink 系统内的 Exactly-once，比如 Flink
内置支持的算子。针对 Source和 Sink 组件，如果想要保证 Exactly-once 的话，则这些组件本身应支持这种语义

#### 2.3 Time

分为 Event time、Ingestion time、Processing time，Flink
的无限数据流是一个持续的过程，时间是我们判断业务状态是否滞后，数据处理是否及时的重要依据。

![](https://image.3001.net/images/20230516/1684219134_646324fec20276120e63f.png!small)

#### 2.4 Window

聚合事件（如
count、sum）在流处理和批处理中的工作方式不同。例如，无法计算流中的所有元素（认为流是无界的，数据是无限的）。流上的聚合由窗口来确定计算范围，例如，在过去
5 分钟内计数或最后 100 个元素的总和。

在 Flink 中，当 属于这个窗口的第一个元素到达时就会创建一个窗口。  
当时间（事件或处理时间）超过窗口的结束时间戳加上用户指定的最大允许延迟时间时，窗口就会被完全删除。

这就是 Flink 窗口的生命周期。  
Flink 中的每个窗口都有一个 触发器和执行函数：

  * 触发器定义窗口何时触发
  * 执行函数定义触发时的计算逻辑

除此之外，窗口还可以定义一个 回收器，用来在 窗口触发后、计算执行前(后) 排除或者回收指定的元素。

窗口可以是时间驱动或数据驱动，一种窗口的分类方式：滚动窗口（tumbling，窗口无重叠）、滑动窗口（sliding，窗口有重叠）、会话窗口（session，以无活动时间间隔划分）。

![](https://image.3001.net/images/20230516/1684219135_646324ff6088125661fc9.png!small)

#### 2.5 Watermark

Watermark 是描述 「事件时间」的输入完整性 的概念，是系统根据当前处理数据的 「事件时间」 判断 「处理进度和完整性」 的工具。

在事件时间维度上划分的各个窗口原本都是 未封闭的，表示 数据还没全部达到。  
Watermark 的作用就是给各个窗口 「盖上盖子」，使其成为一个封闭的窗口，表示数据已经全部达到。

![](https://image.3001.net/images/20230516/1684219136_6463250046df3657791fd.png!small)

### 2.6 Trigger

有了 Watermark 之后，虽然用户可以以此来判定 窗口是否完整，但窗口完整并不意味着要触发计算，只能说满足了触发计算的条件。

真正决定在处理时间的什么时候触发计算的是 Trigger，其是描述 何时「计算窗口」的机制 。

Trigger 的触发计算信号可以从以下几个维度来定义：

  * 事件时间维度：按照事件时间窗口完整触发计算，即 Watermark 出现。
  * 处理时间维度：按照固定的处理时间触发计算，是固定的、不延迟的，定期输出结果。
  * 元素计数维度：窗口累计固定数量后触发计算
  * 带标记信号或其他依赖其他触发器：接受到EOF等事件时触发计算

## 3 多级API

![](https://image.3001.net/images/20230516/1684219136_64632500c5c5c45ec179d.png!small)

Flink API 最底层的抽象为有状态实时流处理。其抽象实现是 Process Function，并且 Process Function 被 Flink
框架集成到了 DataStream API
中来为我们使用。它允许用户在应用程序中自由地处理来自单流或多流的事件（数据），并提供具有全局一致性和容错保障的状态。此外，用户可以在此层抽象中注册事件时间（event
time）和处理时间（processing time）回调方法，从而允许程序可以实现复杂计算。

Flink API 第二层抽象是 Core APIs。实际上，许多应用程序不需要使用到上述最底层抽象的 API，而是可以使用 Core APIs
进行编程：其中包含 DataStream API（应用于有界/无界数据流场景）和 DataSet API（应用于有界数据集场景）两部分。Core APIs
提供的流式 API（Fluent
API）为数据处理提供了通用的模块组件，例如各种形式的用户自定义转换（transformations）、联接（joins）、聚合（aggregations）、窗口（windows）和状态（state）操作等。此层
API 中处理的数据类型在每种编程语言中都有其对应的类。

Process Function 这类底层抽象和 DataStream API 的相互集成使得用户可以选择使用更底层的抽象 API
来实现自己的需求。DataSet API 还额外提供了一些原语，比如循环/迭代（loop/iteration）操作。

Flink API 第三层抽象是 Table API。Table API
是以表（Table）为中心的声明式编程（DSL）API，例如在流式数据场景下，它可以表示一张正在动态改变的表。Table API
遵循（扩展）关系模型：即表拥有 schema（类似于关系型数据库中的 schema），并且 Table API 也提供了类似于关系模型中的操作，比如
select、project、join、group-by 和 aggregate 等。Table API
程序是以声明的方式定义应执行的逻辑操作，而不是确切地指定程序应该执行的代码。尽管 Table API
使用起来很简洁并且可以由各种类型的用户自定义函数扩展功能，但还是比 Core API 的表达能力差。此外，Table API
程序在执行之前还会使用优化器中的优化规则对用户编写的表达式进行优化。

表和 DataStream/DataSet 可以进行无缝切换，Flink 允许用户在编写应用程序时将 Table API 与
DataStream/DataSet API 混合使用。

Flink API 最顶层抽象是 SQL。这层抽象在语义和程序表达式上都类似于 Table API，但是其程序实现都是 SQL 查询表达式。SQL 抽象与
Table API 抽象之间的关联是非常紧密的，并且 SQL 查询语句可以在 Table API 中定义的表上执行。

## 4 扩展库

#### 4.1 复杂事件处理(CEP)

模式检测是事件流处理中的一个非常常见的用例。Flink 的 CEP库提供了 API，使用户能够以例如正则表达式或状态机的方式指定事件模式。CEP
库与Flink 的 DataStream API 集成，以便在 DataStream 上评估模式。CEP 库的应用包括网络入侵检测，业务流程监控和欺诈检测。

### 4.2 StateProcessorAPI

可以用来读、写、修改、分析checkpoint和state。

### 4.3 Gelly

Gelly 是一个可扩展的图形处理和分析库。Gelly 是在 DataSet API 之上实现的，并与 DataSet API
集成。因此，它能够受益于其可扩展且健壮的操作符。Gelly 提供了内置算法，如 label propagation、triangle enumeration
和 page rank 算法，也提供了一个简化自定义图算法实现的 Graph API。

## 5 编程模型

![](https://image.3001.net/images/20230516/1684219137_646325015b26a0718812e.png!small)

## 6 应用场景

#### 6.1 CDC变更数据捕获

CDC 是变更数据捕获 (Change Data Capture) 技术的缩写，它可以将源数据库 (Source) 的增量变动记录，同步到一个或多个数据目的
(Sink)。在同步过程中，还可以对数据进行一定的处理，例如分组 (GROUP BY)、多表的关联 (JOIN) 等。

例如对于电商平台，用户的订单会实时写入到某个源数据库；A 部门需要将每分钟的实时数据简单聚合处理后保存到 Redis 中以供查询，B
部门需要将当天的数据暂存到 Elasticsearch 一份来做报表展示，C 部门也需要一份数据到 ClickHouse 做实时数仓。随着时间的推移，后续
D 部门、E 部门也会有数据分析的需求，这种场景下，传统的拷贝分发多个副本方法很不灵活，而 CDC 可以实现一份变动记录，实时处理并投递到多个目的地。

#### 6.2 CDC 的应用场景

  * 数据同步：用于备份，容灾；
  * 数据分发：一个数据源分发给多个下游系统；
  * 数据采集：面向数据仓库 / 数据湖的 ETL 数据集成，是非常重要的数据源。

CDC 的技术方案非常多，目前业界主流的实现机制可以分为两种：

##### 1.基于查询的 CDC：

  * 离线调度查询作业，批处理。把一张表同步到其他系统，每次通过查询去获取表中最新的数据；
  * 无法保障数据一致性，查的过程中有可能数据已经发生了多次变更；
  * 不保障实时性，基于离线调度存在天然的延迟。

##### 2.基于日志的 CDC：

  * 实时消费日志，流处理，例如 MySQL 的 binlog 日志完整记录了数据库中的变更，可以把 binlog 文件当作流的数据源；
  * 保障数据一致性，因为 binlog 文件包含了所有历史变更明细；
  * 保障实时性，因为类似 binlog 的日志文件是可以流式消费的，提供的是实时数据。

![](https://image.3001.net/images/20230516/1684219137_64632501e2f3b00e32b7d.png!small)

#### 6.3 Data Pipeline

![](https://image.3001.net/images/20230516/1684219138_64632502a03a79e494ba2.png!small)

Data Pipeline 的核心场景类似于数据搬运并在搬运的过程中进行部分数据清洗或者处理，而整个业务架构图的左边是 Periodic
ETL，它提供了流式 ETL 或者实时 ETL，能够订阅消息队列的消息并进行处理，清洗完成后实时写入到下游的 Database 或 File system
中。

 **场景举例：**

实时数仓：当下游要构建实时数仓时，上游则可能需要实时的 Stream
ETL。这个过程会进行实时清洗或扩展数据，清洗完成后写入到下游的实时数仓的整个链路中，可保证数据查询的时效性，形成实时数据采集、实时数据处理以及下游的实时
Query。

#### 6.4 Data Analytics

![](https://image.3001.net/images/20230516/1684219139_646325037b2228fc434cd.png!small)

Data Analytics，如图，左边是 Batch Analytics，右边是 Streaming Analytics。Batch Analysis
就是传统意义上使用类似于 Map Reduce、Hive、Spark Batch 等，对作业进行分析、处理、生成离线报表，Streaming
Analytics 使用流式分析引擎如 Storm，Flink 实时处理分析数据，应用较多的场景如实时大屏、实时报表。

#### 6.5 Data Driven

![](https://image.3001.net/images/20230516/1684219140_64632504526fcd16aca86.png!small)

## 7 相关资料

  * 官方文档：<https://nightlies.apache.org/flink/flink-docs-release-1.14/zh/docs>
  * maven依赖：<https://flink.apache.org/downloads.html#maven-dependencies>
  * flink编程示例代码：<https://github.com/apache/flink-training.git>
  * state编程示例代码：<https://github.com/apache/flink-statefun-playground.git>

作者：冯鸿儒

