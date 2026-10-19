## 导读

本文是线上问题处理案例系列之一，旨在通过真实案例向读者介绍发现问题、定位问题、解决问题的方法。本文讲述了从垃圾回收耗时过长的表象，逐步定位到数据库连接池保活问题的全过程，并对其中用到的一些知识点进行了总结。

## 一、问题描述

大促期间，某接口超时次数增多，经排查直接原因是 GC 耗时过长，查看监控 FullGC 达 500ms 以上，接口超时时间与 FullGC 发生时间吻合。

![1684736426_646b09aa9a9b277a5ba90.png!small?1684736427130](https://image.3001.net/images/20230522/1684736426_646b09aa9a9b277a5ba90.png!small?1684736427130)

图 1 FullGC 耗时监控

## 二、应用基本情况

  * 容器：8C12G；
  * JVM 配置：-XX:+UseConcMarkSweepGC -Xms6144m -Xmx6144m -Xmn2048m -XX:ParallelGCThreads=8 -XX:+UseCMSInitiatingOccupancyOnly -XX:CMSInitiatingOccupancyFraction=70 -XX:+ParallelRefProcEnabled；
  * 数据库类型：MySQL；
  * 数据库连接池：DBCP；

## 三、排查过程

1、 GC 耗时过长，说明内存中垃圾对象很多。

2、 首先怀疑是否有内存泄漏，观察 FullGC 后堆内存回收情况，尚属正常，暂时排除内存泄漏原因。

![1684736437_646b09b507bc6f987f6f6.png!small?1684736437795](https://image.3001.net/images/20230522/1684736437_646b09b507bc6f987f6f6.png!small?1684736437795)

图 2 发生 FullGC 后堆内存回收监控

3、 推断 FullGC 耗时过长是否因为老年代有大量死亡对象，遂导出 FullGC 前后堆内存 dump，通过比对 “保留大小”，发现 FullGC
后大量数据库相关对象被回收。

![1684736445_646b09bdef1cd597ebeec.png!small?1684736446558](https://image.3001.net/images/20230522/1684736445_646b09bdef1cd597ebeec.png!small?1684736446558)

图 3 堆内存对象分析

4、 数据库连接正常应该不会频繁创建和断开，进入老年代后，正常不应该被回收，通过堆 dump 内容 OQL 分析每个数据库连接数量，发现很多库连接数都大于
“maxActive” 数量，可以肯定有很多失效连接。

5、 初步判断直接原因是很多失效数据库连接进入老年代，导致 FullGC 耗时过长。

6、 怀疑连接池验证周期过长，导致数据库因空闲过长关闭连接，将连接池参数 “  
timeBetweenEvictionRunsMillis” 由 1 分钟调整到 10 秒，问题依旧。

7、 阅读 DBCP 源码，发现是通过  
org.apache.commons.pool.impl.GenericObjectPool.Evictor 定时任务，按照
timeBetweenEvictionRunsMillis 配置的周期定时驱逐失效连接，驱逐条件：若连接空闲时间大于
“minEvictableIdleTimeMillis”，则会驱逐连接，等待垃圾回收。若开启 “testWhileIdle” 则会执行
“validationQuery”。进一步阅读代码，发现执行 “validationQuery”
后，连接空闲时间并不会重新计算，导致连接在业务低谷时很容易被淘汰，而数据库连接会关联大量对象，创建、回收成本昂贵，并且影响 GC。

8、 反向思考，为何只有在大促期间才发生问题？

![1684736464_646b09d0735cbe27b0f25.png!small?1684736464883](https://image.3001.net/images/20230522/1684736464_646b09d0735cbe27b0f25.png!small?1684736464883)

图 4 平时和大促时回收频率对比

可以看到平时由于业务量小，GC 不频繁，过期连接没有达到进入老年代阈值，在年轻代被回收。而大促时业务量大，GC 频繁，连接在进入老年代以后才过期，导致老年代
FullGC 时间过长。

9、 至此，基本可以肯定问题原因是数据库连接池不具备 “保活” 能力，导致连接不断淘汰和新建，在业务高峰时段，连接进入老年代然后失效，造成 FullGC
耗时过长，最终导致接口超时次数增多。

## 四、解决方案

 **方案 1** ：改为 G1 回收器，对老年代回收是分块进行，可以防止长时间停顿。另外默认 MaxTenuringThreshold 值是
15，可以防止失效连接过早进入老年代；

 **方案 2** ：  
minEvictableIdleTimeMillis 设置为 0，使数据库连接不会自动失效，进入老年代以后一直存活，避免在老年代失效回收；

## 五、问题总结

数据库连接池并不具备通常理解的 “保活” 能力，数据库连接在业务不活跃的应用中，会不断淘汰和重连，而连接会通过虚引用方式（  
com.mysql.jdbc.NonRegisteringDriver$ConnectionPhantomReference）携带大量对象，如果连接存活时间内
YGC 次数达到寿命阈值，则会进入老年代，老年代是使用 “标记 - 清除” 算法，回收成本更高，进而造成 FullGC 耗时过长。

## 六、拓展知识点

1、 Druid 连接池同样存在不能 “保活” 问题，较新版本提供 “KeepAlive” 选项（未验证）；

2、 Druid 连接池配置的 “validationQuery” 语句通常并不会被执行，MySqlValidConnectionChecker
在检查连接有效性时，会判断驱动是否实现 pingInternal 方法，如果实现则会通过此方法验证有效性。MySQL 的 JDBC 驱动实现了该方法，因此
“validationQuery” 配置的语句通常不会执行；

![1684736475_646b09db20e9142da157a.png!small?1684736475787](https://image.3001.net/images/20230522/1684736475_646b09db20e9142da157a.png!small?1684736475787)

图 5 连接有效性校验代码

3、 DBCP 和 Druid 连接池默认都是 FILO，如果业务不繁忙，会导致只有最前边的连接被使用 - 归还 -使用，后边连接基本都在无谓的驱逐、重建连接；

4、 虚引用对 GC 的影响：这些引用只有经过两次 GC 才能被回收掉，如果进入老年代，则必须经过两次 FullGC
才能释放内存。本例中由于不断有新的虚引用对象在老年代失效，导致 FullGC 后，内存水位仍然偏高，会加剧 GC 压力。新版本 JVM 已对此做了优化，一次
GC 可以回收掉；

5、 类似的影响还有 finalize 方法；

6、 CMS 回收器默认 MaxTenuringThreshold 为 6，而 ParallelGC 和 G1 均默认 15；

## 结语

本文对数据库连接失效引起的 GC 问题进行了详细分析，希望读者通过本文对数据库连接 “保活” 机制、GC
问题基本分析方法有所收益，后续该系列文章会继续推出其他案例分享。

> 作者：京东零售 王利辉
>
> 内容来源：京东云开发者社区

