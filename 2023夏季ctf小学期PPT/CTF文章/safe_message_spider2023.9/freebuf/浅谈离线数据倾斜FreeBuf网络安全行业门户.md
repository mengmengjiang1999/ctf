**作者：京东零售 荆明岚**

##  **一、数据倾斜的基本概念**

 **1、什么是数据倾斜？**

用最通俗易懂的话来说,数据倾斜无非就是大量的相同key被partition分配到一个分区里,造成了'一个人累死,其他人闲死'的情况,这种情况是我们不能接受的,这也违背了并行计算的初衷,首先一个节点要承受着巨大的压力,而其他节点计算完毕后要一直等待这个忙碌的节点,也拖累了整体的计算时间,可以说效率是十分低下的

 **2、数据倾斜发生时的现象**

（1）绝大多数task执行得都非常快，但个别task执行的极慢。

（2）原本能正常执行的Spark作业，某天突然爆出OOM（内存溢出）异常。观察异常栈，是我们写的业务代码造成的

 **3、通用的常规解决方案：**

（1）增加jvm内存,这适用于第一种情况(唯一值非常少，极少数值有非常多的记录值(唯一值少于几千)),这种情况下,往往只能通过硬件的手段来进行调优,增加jvm内存可以显著的提高运行效率。

（2）增加reduce的个数,这适用于第二种情况(唯一值比较多，这个字段的某些值有远远多于其他值的记录数，但是它的占比也小于百分之一或千分之一),我们知道,这种情况下,最容易造成的结果就是大量相同key被partition到一个分区,从而一个reduce执行了大量的工作,而如果我们增加了reduce的个数,这种情况相对来说会减轻很多,毕竟计算的节点多了,就算工作量还是不均匀的,那也要小很多。

（3）自定义分区,这需要用户自己继承partition类,指定分区策略,这种方式效果比较显著。

（4）重新设计key,有一种方案是在map阶段时给key加上一个随机数,有了随机数的key就不会被大量的分配到同一节点(小几率),待到reduce后再把随机数去掉即可。

（5）使用combinner合并,combinner是在map阶段,reduce之前的一个中间阶段,在这个阶段可以选择性的把大量的相同key数据先进行一个合并,可以看做是local
reduce,然后再交给reduce来处理,这样做的好

 **4、通用定位发生数据倾斜的代码？**

（1）数据倾斜只会发生在shuffle中，下面是常用的可能会触发shuffle操作的算子：distinct、groupByKey、reduceByKey、aggregateByKey、join、cogroup、repartition等。出现数据倾斜时，可能就是代码中使用了这些算子的原因

（2）通过观察spark UI，定位数据倾斜发生在第几个stage中，如果是用yarn-client模式提交，那么本地是可以直接看到log的，可以在log中找到当前运行到了第几个stage;如果用yarn-cluster模式提交，可以通过Spark Web UI 来查看当前运行到了第几个stage。此外，无论是使用了yarn-client模式还是yarn-cluster模式，我们都可以在Spark Web UI
上深入看一下当前这个stage各个task分配的数据量，从而进一步确定是不是task分配的数据不均匀导致了数据倾斜

##  **二、 Hive数据倾斜**

 **1、Hive的执行是分阶段的**
，map处理数据量的差异取决于上一个stage的reduce输出，所以如何将数据均匀的分配到各个reduce中，就是解决数据倾斜的根本所在

 **2 、造成数据倾斜的原因**

1)、key分布不均匀

2)、业务数据本身的特性

3)、建表时考虑不周

4)、某些SQL语句本身就有数据倾斜

 **3 、数据倾斜的表现：**

数据倾斜出现在SQL算子中包含join/group
by/等聚合操作时，大量的相同KEY被分配到少量的reduce去处理。导致绝大多数TASK执行得都非常快，但个别TASK执行的极慢，原本能正常执行的作业，某天突然爆出OOM（内存溢出）异常。任务进度长时间维持在99%（或100%）。任务监控页面，发现只有少量（1个或几个）reduce子任务未完成。因为其处理的数据量和其他reduce差异过大。单一reduce的记录数与平均记录数差异过大，通常可能达到3倍甚至更多。
最长时长远大于平均时长。可以查看具体job的reducer counter计数器协助定位。

 **4、数据倾斜的解决方案：**

 **（1）参数调节：**

hive.map.aggr=true
（是否在Map端进行聚合，默认为true），这个设置可以将顶层的聚合操作放在Map阶段执行，从而减轻清洗阶段数据传输和Reduce阶段的执行时间，提升总体性能

Set hive.groupby.skewindata=true（hive自动进行负载均衡）

 **（2）SQL语句调节**

 **a、如何Join：**

关于驱动表的选取，选用join key分布最均匀的表作为驱动表

做好列裁剪和filter操作，以达到两表做join的时候，数据量相对变小的效果，避免笛卡尔积

Hive中进行表的关联查询时，尽可能将较大的表放在Join之后

 **b、大小表Join，开启mapjoin**

mapjoin的原理： MapJoin
会把小表全部读入内存中，在map阶段直接拿另外一个表的数据和内存中表数据做匹配，由于在map是进行了join操作，省去了reduce
阶段，运行的效率就会高很多。参与连接的小表的行数，以不超过2万条为宜，大小不超过25M

 **设置参数**

set hive.auto.convert.join=true;

hive.mapjoin.smalltable.filesize=25000000 即25M

 **手动指定**

\-- a 表是大表，数据量是百万级别

\-- b 表是小表，数据量在百级别，mapjion括号中的b就是指定哪张表为小表

select

/+mapjoin(b)/

a.field1 as field1,

b.field2 as field2,

b.field3 as field3

from a left join b

on a.field1 = b.field1;

 **c、大表Join大表：**

 **null值不参与连接** ，简单举例

select field1,field2,field3…

from log a left join user b on a.userid is not null and a.userid=b.userid

union select field1,field2,field3 from log where userid is null;

 **将热点key打散**
，但是需要注意，尽量不要在join时，对关联key使用rand()函数。因为在hive中当遇到map失败重算时，就会出现数据重复（数据丢失）的问题，spark引擎使用rand容易导致task失败重新计算的时候偶发不一致的问题。可以使用md5加密唯一维度值的方式替代rand()，
比如： md5(concat(coalesce(sku_id, 0), '_', coalesce(dim_store_num, 0), '_',
coalesce(store_id, 0), '_',coalesce(delv_center_id,
0)))，其中concat的字段是表的唯一粒度；也可以使用hash。

 **d、count distinct大量相同特殊值，使用sum...group by代替count(distinct )**

例如 select a,count(distinct b) from t group by a

可以写成 select a,sum(1) from (select a,b from t group by a,b) group by a;

select count (distinct key) from a

可以写成 Select sum(1) from (Select key from a group by key) t
特殊情况特殊处理：在业务逻辑优化效果的不大情况下，有些时候是可以将倾斜的数据单独拿出来处理。最后union回去

 **e、 不管是join还是groupby 请先在内层先进行数据过滤，建议只保留需要的key值**

 **f、 取最大最小值尽量使用min/max；不要采用row_number**

 **g、 不要直接select * ;在内层做好数据过滤**

 **h、 尽量使用sort by替换order by**

 **i、 明确数据源，有上层汇总的就不要使用基础fdm或明细表**

 **J、join避免多对多关联**

在join链接查询时，确认是否存在多对多的关联，起码保证有一个表的结果集的关联字段不重复

 **5、典型的业务场景举例**

 **（1）空值产生的数据倾斜**

场景：如日志中，常会有信息丢失的问题，比如日志中的 user_id，如果取其中的 user_id 和 用户表中的user_id 关联，会碰到数据倾斜的问题。

解决方法1： user_id为空的不参与关联

select * from log a

join users b

on a.user_id is not null

and a.user_id = b.user_idunion allselect * from log a

where a.user_id is null;

 **（2）不同数据类型关联产生数据倾斜**

场景：用户表中user_id字段为int，log表中user_id字段既有string类型也有int类型。当按照user_id进行两个表的Join操作时，默认的Hash操作会按int型的id来进行分配，这样会导致所有string类型id的记录都分配到一个Reducer中。

解决方法：把数字类型转换成字符串类型

select * from users a

left outer join logs b

on a.usr_id = cast(b.user_id as string)

 **（3）小表不小不大，怎么用 map join 解决倾斜问题**

使用 map join 解决小表(记录数少)关联大表的数据倾斜问题，这个方法使用的频率非常高，但如果小表很大，大到map
join会出现bug或异常，这时就需要特别的处理

select * from log a

left outer join users b

on a.user_id = b.user_id;

users 表有 600w+ 的记录，把 users 分发到所有的 map 上也是个不小的开销，而且 map join 不支持这么大的小表。如果用普通的
join，又会碰到数据倾斜的问题

解决方法：

select /+mapjoin(x)/* from log a

left outer join (

select /+mapjoin(c)/d.*

from ( select distinct user_id from log ) c

join users d

on c.user_id = d.user_id

) x

on a.user_id = b.user_id;

log里user_id有上百万个，这就又回到原来map
join问题。所幸，每日的会员uv不会太多，有交易的会员不会太多，有点击的会员不会太多，有佣金的会员不会太多等等。所以这个方法能解决很多场景下的数据倾斜问题

 **（4）业务逻辑突发热key的处理（真实线上问题）**

**业务场景举例：**流量数据多个设备号对应了一个安装id，突发某几个安装id数量级特别大。在归一环节中，按照安装id进行分发reduce，再进行处理，异常热key会造成单一节点处理数据量大，由于数据倾斜从而导致任务卡死的情况。

**解决方案：**基于小时任务，提前设置一个异常范围，把异常安装id和对应的aid捞出来，写到维表里面。按照归一逻辑，优先使用aid值作为归一结果，所以在归一任务中，读取异常值，随机分发到reduce中，并将aid赋值给归一字段，这样就避免了热点处理

 **总结：**

 **1、对于join，在判断小表不大于1G的情况下，使用map join**

 **2、对于group by或distinct，设定 hive.groupby.skewindata=true**

 **3、尽量使用上述的SQL语句调节进行优化**

 **6、数据倾斜的监控预防**

 **（1）测试的时候需要关注数据分布，针对不同日期、关键指标、重点key、枚举值等**

 **（2）增加数据质量监控，数据计算的每层任务增加数据质量监控。**

 **（3）L0任务，大数据平台需要有健康度巡检，对资源、参数配置，数据倾斜、稳定性等做任务健康度打分，从而发现数据倾斜的趋势，及早检查任务**

##  **三、spark数据倾斜**

 **Spark优化数据倾斜的思路，join方式从SMJ方式改成BMJ的方式，但是只适合大小表的情况。优化思路一般是：
改join方式，开启spark自适应框架，优化sql。**

 **1、开启sparksql的数据倾斜时的自适应关联优化**

spark.shuffle.statistics.verbose=true --打开后MapStatus会采集每个partition条数的信息，用于倾斜处理

 **2 、Sortmergejoin 改成 BroadcastHashJoin。调大BroadcastHashJoin的阈值** ，

在某些场景下可以把SortMergeJoin转化成BroadcastHashJoin而避免shuffle产生的数据倾斜

增加参数：spark.sql.autoBroadcastJoinThreshold=524288000 --将BHJ的阈值提高到500M
**3、优化sql同hive**

 **4、倾斜KEY查找**

需要结合实际业务代码，查找到引起Shuffle的算子，并按照以下两种方式查找大KEY.

 **方式一：通过SQL抽样倾斜KEY**

适用场景：如果数据量比较小的情况下，通过SQL的方式验证比较便捷

操作步骤：

1、针对KEY进行数量统计。

2、按照数量从大到小进行排序。

3、直接取 limit N 即可。

 **方式二：通过sample抽样倾斜KEY**

适用场景：如果数据量很大，可以通过抽样进行抽取大KEY。能否抽取到大KEY一般和抽取数据比例有关系。

操作步骤：

（1）对KEY赋值为1，便于下一步进行计数

（2） 对KEY进行累计

（3）对KEY和VALUE交换

（4）针对KEY按照字典进行倒排

（5）将KEY和VAlUE位置交换，还原到真实的<KEY,VALUE>

（6）从已排序的RDD中，直接取前 N条

数据倾斜一般由Shuffle时数据不均匀导致，一般有三类算子会产生Shuffle：Aggregation （groupBy）、Join、Window。

####  **Aggregation**

建议打散key进行二次聚合：采用对 非constant值、与key无关 的列进行hash取模， **不要使用rand类函数**

以DataFrame API示例：

dataframe

.groupBy(col("key"), pmod(hash(col("some_col")),
100)).agg(max("value").as("partial_max"))

.groupBy(col("key")).agg(max("partial_max").as("max"))

####  **Window**

目前支持该模式下的倾斜window，（仅支持3.0）

select (... row_number() over(partition by ... order by ...) as rn) where rn
[==|<=|<] k and other conditionsspark.sql.rankLimit.enabled=true
（目前支持基于row_number的topK计算逻辑）

####  **Shuffled Join**

 **Spark 2.4开启参数**

spark.sql.adaptive.enabled=true

spark.shuffle.statistics.verbose=true

spark.sql.adaptive.skewedJoin.enabled=true

spark.sql.adaptive.allowAdditionalShuffle=true

如果不能处理，建议用户自行定位热点数据进行处理

Spark 3.0

spark.sql.adaptive.enabled=true

spark.sql.adaptive.skewJoin.enabled=true

spark.sql.adaptive.skewJoin.enhance.enabled=true (通用倾斜算法，可处理更多场景)

spark.sql.adaptive.forceOptimizeSkewedJoin=true （允许插入额外shuffle，可处理更多场景）

其他参数：

spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes
（默认为256MB，分区大小超过该阈值才可被识别为倾斜分区，如果希望调整的倾斜分区小于该阈值，可以酌情调小）

spark.sql.adaptive.skewJoin.skewedPartitionFactor
（默认为5，分区大小超过中位数Xfactor才可被识别为倾斜分区，一般不需要调整）

spark.sql.adaptive.skewJoin.enhance.maxJoins （默认5，通用倾斜算法中，如果shuffled
join超过此阈值则不处理，一般不需要调整）

spark.sql.adaptive.skewJoin.enhance.maxSplitsPerPartition
（默认1000，通用倾斜算法中，尽量使得每个倾斜分区的划分不超过该阈值，一般不需要调整）

####  **数据膨胀（Join）**

spark.sql.adaptive.skewJoin.inflation.enabled=true
（默认false，由于采样计算会导致性能回归，正常任务不要开启）

spark.sql.adaptive.skewJoin.inflation.factor=50
（默认为100，预估的分区输出大小超过中位数Xfactor才可被识别为膨胀分区，由于预估算法存在误差，一般不要低于50）

spark.sql.adaptive.shuffle.sampleSizePerPartition=500
（默认100，每个Task中的采样数，基于该采样数据预估Join之后的分区大小，如果Task数量不大，可以酌情调大）

####  **倾斜key检测（Join）**

由于Join语义限制，对于A left join skewed
B之类的场景，无法对B进行划分处理，否则会导致数据正确性问题，这也是Spark项目所面临的难题。如果开启以上功能依然不能处理数据倾斜，可以通过开启倾斜key检测功能来定位是哪些key导致了倾斜或膨胀，继而进行过滤等处理。

spark.sql.adaptive.shuffle.detectSkewness=true
（默认false，由于采样计算会导致性能回归，正常任务不要开启）

其他参数：

spark.sql.adaptive.shuffle.sampleSizePerPartition=100
（默认100，每个Task中的采样数，如果Task数量不大，可以酌情调大）

