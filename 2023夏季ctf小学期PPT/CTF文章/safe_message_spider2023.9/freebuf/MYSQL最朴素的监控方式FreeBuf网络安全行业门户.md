对于当前数据库的监控方式有很多，分为数据库自带、商用、开源三大类，每一种都有各自的特色；而对于mysql数据库由于其有很高的社区活跃度，监控方式更是多种多样，不管哪种监控方式最核心的就是监控数据，获取得到全面的监控数据后就是灵活的展示部分。那我们今天就介绍一下完全采用mysql自有方式采集获取监控数据，在单体下达到最快速、方便、损耗最小。

本次文章完全使用mysql自带的show命令实现获取，从connects、buffercache、lock、SQL、statement、Database
throughputs、serverconfig7大方面全面获取监控数据。

### 1 连接数（Connects）

  * 最大使用连接数：show status like ‘Max_used_connections’
  * 当前打开的连接数：show status like ‘Threads_connected’

### 2 缓存（bufferCache）

  * 未从缓冲池读取的次数：show status like ‘Innodb_buffer_pool_reads’
  * 从缓冲池读取的次数：show status like ‘Innodb_buffer_pool_read_requests’
  * 缓冲池的总页数：show status like ‘Innodb_buffer_pool_pages_total’
  * 缓冲池空闲的页数：show status like ‘Innodb_buffer_pool_pages_free’
  * 缓存命中率计算：（1-Innodb_buffer_pool_reads/Innodb_buffer_pool_read_requests）*100%
  * 缓存池使用率为：((Innodb_buffer_pool_pages_total-Innodb_buffer_pool_pages_free）/Innodb_buffer_pool_pages_total）*100%

### 3 锁（lock）

  * 锁等待个数：show status like ‘Innodb_row_lock_waits’
  * 平均每次锁等待时间：show status like ‘Innodb_row_lock_time_avg’
  * 查看是否存在表锁：show open TABLES where in_use>0；有数据代表存在锁表，空为无表锁

备注：锁等待统计得数量为累加数据，每次获取得时候可以跟之前得数据进行相减，得到当前统计得数据

### 4 SQL

  * 查看mysql开关是否打开：show variables like ‘slow_query_log’，ON为开启状态，如果为OFF，set global slow_query_log=1 进行开启
  * 查看mysql阈值：show variables like ‘long_query_time’，根据页面传递阈值参数，修改阈值 set global long_query_time=0.1
  * 查看mysql慢sql目录：show variables like ‘slow_query_log_file’
  * 格式化慢sql日志：mysqldumpslow -s at -t 10 /export/data/mysql/log/slow.log  
注：此语句通过jdbc执行不了，属于命令行执行。  
意思为：显示出耗时最长的10个SQL语句执行信息，10可以修改为TOP个数。显示的信息为：执行次数、平均执行时间、SQL语句

备注：当mysqldumpslow命令执行失败时，将慢日志同步到本地进行格式化处理。

### 5 statement

  * insert数量：show status like ‘Com_insert’
  * delete数量：show status like ‘Com_delete’
  * update数量：show status like ‘Com_update’
  * select数量：show status like ‘Com_select’

### 6 吞吐（Database throughputs）

  * 发送吞吐量：show status like ‘Bytes_sent’
  * 接收吞吐量：show status like ‘Bytes_received’
  * 总吞吐量：Bytes_sent+Bytes_received

### 7 数据库参数（serverconfig）

show variables

![](https://image.3001.net/images/20220812/1660267983_62f5adcfe9b0e4dc4be67.png!small)

### 8 慢SQL

慢SQL指的是MySQL慢查询，具体指运行时间超过long_query_time值的SQL。  
我们常听MySQL中有二进制日志binlog、中继日志relaylog、重做回滚日志redolog、undolog等。针对慢查询，还有一种慢查询日志slowlog，用来记录在MySQL中响应时间超过阀值的语句。慢SQL对实际生产业务影响是致命的，所以测试人员在性能测试过程中，对数据库SQL语句执行情况实施监控，给开发提供准确的性能优化意见显得尤为重要。那怎么使用Mysql数据库提供的慢查询日志来监控SQL语句执行情况，找到消耗较高的SQL语句，以下详细说明一下慢查询日志的使用步骤：

  * 确保打开慢SQL开关slow_query_log

![](https://image.3001.net/images/20220812/1660267986_62f5add245fbea59502c0.png!small)

  * 设置慢SQL域值long_query_time  
这个long_query_time是用来定义慢于多少秒的才算“慢查询”，注意单位是秒，我通过执行sql指令set
long_query_time=1来设置了long_query_time的值为1, 也就是执行时间超过1秒的都算慢查询，如下：

![](https://image.3001.net/images/20220812/1660267986_62f5add2e39769e329e81.png!small)

  * 查看慢SQL日志路径

![](https://image.3001.net/images/20220812/1660267987_62f5add3880c022b731cd.png!small)

  * 通过慢sql分析工具mysqldumpslow格式化分析慢SQL日志  
mysqldumpslow慢查询分析工具，是mysql安装后自带的，可以通过./mysqldumpslow —help查看使用参数说明

![](https://image.3001.net/images/20220812/1660267988_62f5add432202d69ff4f4.png!small)

常见用法：

  1. 取出使用最多的10条慢查询  
./mysqldumpslow -s c -t 10 /export/data/mysql/log/slow.log

  2. 取出查询时间最慢的3条慢查询  
./mysqldumpslow -s t -t 3 /export/data/mysql/log/slow.log

注意: 使用mysqldumpslow的分析结果不会显示具体完整的sql语句,只会显示sql的组成结构;  
假如: SELECT FROM sms_send WHERE service_id=10 GROUP BY content LIMIT 0, 1000;  
mysqldumpslow命令执行后显示：  
Count: 2 Time=1.5s (3s) Lock=0.00s (0s) Rows=1000.0 (2000),
vgos_dba[vgos_dba]@[10.130.229.196]SELECT FROM sms_send WHERE service_id=N
GROUP BY content LIMIT N, N

 **mysqldumpslow的分析结果详解：**

  * Count：表示该类型的语句执行次数，上图中表示select语句执行了2次。
  * Time：表示该类型的语句执行的平均时间（总计时间）
  * Lock：锁时间0s。
  * Rows：单次返回的结果数是1000条记录，2次总共返回2000条记录。

通过这个工具就可以查询出来哪些sql语句是慢SQL，从而反馈研发进行优化，比如加索引，该应用的实现方式等。

 **常见慢SQL排查**

  1. 不使用子查询  
SELECT FROM t1 WHERE id (SELECT id FROM t2 WHERE name=’hechunyang’);  
子查询在MySQL5.5版本里，内部执行计划器是这样执行的：先查外表再匹配内表，而不是先查内表t2，当外表的数据很大时，查询速度会非常慢。  
在MariaDB10/MySQL5.6版本里，采用join关联方式对其进行了优化，这条SQL会自动转换为 SELECT t1. FROM t1 JOIN
t2 ON t1.id = t2.id;  
但请注意的是：优化只针对SELECT有效，对UPDATE/DELETE子 查询无效， 生产环境尽量应避免使用子查询。

  2. 避免函数索引  
SELECT FROM t WHERE YEAR(d) >= 2016;  
由于MySQL不像Oracle那样⽀持函数索引，即使d字段有索引，也会直接全表扫描。  
应改为 > SELECT FROM t WHERE d >= ‘2016-01-01’;

  3. 用IN来替换OR低效查询  
慢SELECT FROM t WHERE LOC_ID = 10 OR LOC_ID = 20 OR LOC_ID = 30;  
高效查询 > SELECT FROM t WHERE LOC_IN IN (10,20,30);

  4. LIKE双百分号无法使用到索引  
SELECT FROM t WHERE name LIKE ‘%de%’;  
使用SELECT FROM t WHERE name LIKE ‘de%’;

  5. 分组统计可以禁止排序  
SELECT goods_id,count() FROM t GROUP BY goods_id;  
默认情况下，MySQL对所有GROUP BY col1，col2…的字段进⾏排序。如果查询包括GROUP BY，想要避免排序结果的消耗，则可以指定ORDER
BY NULL禁止排序。  
使用SELECT goods_id,count() FROM t GROUP BY goods_id ORDER BY NULL;

  6. 禁止不必要的ORDER BY排序  
SELECT count(1) FROM user u LEFT JOIN user_info i ON u.id = i.user_id WHERE 1
= 1 ORDER BY u.create_time DESC;  
使用SELECT count(1) FROM user u LEFT JOIN user_info i ON u.id = i.user_id;

### 9 总结

  * 任何东西不应过重关注其外表，要注重内在的东西，往往绚丽的外表下会有对应的负担和损耗。
  * mysql数据库的监控支持通过SQL方式从performance_schema库中访问对应的表数据，前提是初始化此库并开启监控数据写入。
  * 对于监控而言，不在于手段的多样性，而需要明白监控的本质，以及需要的监控项内容，找到符合自身项目特色的监控方式。
  * 在选择监控工具对mysql监控时，需要关注监控工具本身对于数据库服务器的消耗，不要影响到其自身的使用。

######

###### 作者：安甲舒

