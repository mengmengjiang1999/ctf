# 京东云TiDB SQL层的背景介绍

从总体上概括 TiDB 和 MySQL 兼容策略，如下表：

![](https://image.3001.net/images/20221017/1665987301_634cf2e55ab895d585ae9.png!small)

# SQL层的架构

用户的 SQL 请求会直接或者通过 Load Balancer 发送到 京东云TiDB Server，TiDB Server 会解析 MySQL
Protocol Packet，获取请求内容，对 SQL 进行语法解析和语义分析，制定和优化查询计划，执行查询计划并获取和处理数据。数据全部存储在 TiKV
集群中，所以在这个过程中 TiDB Server 需要和 TiKV 交互，获取数据。最后 TiDB Server 需要将查询结果返回给用户。

![image.png](https://image.3001.net/images/20221018/1666064251_634e1f7b8c13de7d4263d.png!small)

## ●SQL优化流程的概览

在 TiDB 中，从输入的查询文本到最终的执行计划执行结果的过程可以见下图：

![image.png](https://image.3001.net/images/20221018/1666064273_634e1f91b77a0867eb6de.png!small)

在经过了 parser 对原始查询文本的解析以及一些简单的合法性验证后，TiDB
首先会对查询做一些逻辑上的等价变化，通过这些等价变化，使得这个查询在逻辑执行计划上可以变得更易于处理。在等价变化结束之后，TiDB
会得到一个与原始查询等价的查询计划结构，之后根据数据分布、以及一个算子具体的执行开销，来获得一个最终的执行计划，同时，TiDB 在执行 PREPARE
语句时，可以选择开启缓存来降低 TiDB 生成执行计划的开销。

![image.png](https://image.3001.net/images/20221018/1666072162_634e3e624a6c98bccd481.png!small)

![image.png](https://image.3001.net/images/20221018/1666064294_634e1fa63963d9e223b8e.png!small)  
![image.png](https://image.3001.net/images/20221018/1666072191_634e3e7f8b2be811fbcff.png!small)

![image.png](https://image.3001.net/images/20221018/1666064308_634e1fb4c330a152bf02e.png!small)

举个例子如下：  
![image](https://image.3001.net/images/20221018/1666064353_634e1fe1ad0ddcd4c2099.png!small)

从上述例子中可以看出，优化器估算的 estRows 和实际执行中统计得到的 actRows 几乎是相等的，说明优化器估算的行数与实际行数的误差很小。同时
IndexLookUp_10 算子在实际执行过程中使用了约 9 KB 的内存，该 SQL 在执行过程中，没有触发过任何算子的落盘操作。

# SQL优化案例最佳实践

### 案例一：索引的错误选择导致SQL变慢的优化实践

场景：数据库迁移到TiDB，SQL在MySQL运行不到1S，在TiDB运行超过30S

SQL执行计划如下：

![image.png](https://image.3001.net/images/20221018/1666064427_634e202bb04cd3b1dc433.png!small)

execution info列，有该执行计划的时间，这个SQL的表的连接顺序，要从最里面的循环开始看，如下图，m,d是最先开始进行连接的：

![image.png](https://image.3001.net/images/20221018/1666064447_634e203f45e0697ba6743.png!small)

关注下图的time变化，执行计划由毫秒级变成了秒级的地方，由71ms变成了33s，所以瓶颈卡在（（m join d） join taskm）join
taskd 这个地方，对应的SQL片段如下：

    
    
    INNER JOIN taskd
    ON taskd.no = d.no
     AND taskd.o_no = d.o_no
     AND taskd.d_no = d.d_no
     AND taskd.w_no = d.w_no
     AND taskd.g_no = d.g_no
     AND IF(NULL = d.MD5_VALUE, 1, d.MD5_VALUE) = IF(NULL = d.MD5_VALUE, 1, taskd.MD5_VALUE)
     AND taskd.yn = 0
    

### ●优化思路

1、首先观察结果，看到慢在最内 3 层的 join 上 ，(m join d) join taskd；

2、对比 MySQL 的执行计划，发现 MySQL 最内的 3 层的 join 是 (m join d) join taskm,
所以把相关的3张表提取出来，修改其join顺序；

3、修改顺序后，join 的时间能减少但是和 MySQL差距还是很大，再次观察，发现 taskd 上TiDB和MySQL使用的索引不一样，所以使用了 use
index 来强制TIDB走和MySQL相同的索引。

### 案例二：表关联的错误选择导致SQL变慢的优化实践

 **场景：在MySQL运行时间毫秒级别，在TiDB运行时间18S**

在TiDB的运行时间及执行计划  
![image.png](https://image.3001.net/images/20221018/1666064544_634e20a05f0a043353768.png!small)

优化前后的执行计划

![image.png](https://image.3001.net/images/20221018/1666064483_634e20633e88910963f39.png!small)

优化后加了hint的SQL

![image.png](https://image.3001.net/images/20221018/1666064522_634e208a2795bfc0f666f.png!small)

### ● 优化思路：

1\. TiDB执行耗时 10+s 的原因是对 wps 表的估算不准确，导致优化器认为 w表 和 p表 走 hash join
效率更高，然后我们看到的执行计划的主要耗时在 pri 表回表获取数据的耗时较长 ；

2\. w 表估算不准确的原因为TiDB 会把 w 的条件 有range scan 转换点查，然后利用这个索引的统计信息去估算；

3\. 点查估算是会利用对应的 CMSketch 去进行估算，结合 p 表数据量很大，根据经验推测可能是 CMSketch 内部 hash 冲突导致。

## ●案例一、二的延伸扩展：

在SQL优化的工作中，经常会通过加hint的方式改变SQL的执行计划，从而达到了优化的目的，但是缺点是对SQL进行了硬编码，如果业务程序使用了ORM框架，SQL的改造难度会增加。SQL
Binding（SPM）则很好的解决了硬编码的问题，通过SQL
Binding，DBA可以在不改变SQL文本的情况下，优化sql的执行计划，从而达到优化的目标，从而使SQL优化变得更加优雅。

京东云联合 PingCAP 基于国内开源 NewSQL 数据库 TiDB 打造的一款同时支持 OLTP 和 OLAP
两种场景的分布式云数据库产品，实现了自动的水平伸缩，强一致性的分布式事务，部署简单，在线异步表结构变更不影响业务，同时兼容 MySQL
协议，使迁移使用成本降到极低。

作者：赵玉龙

