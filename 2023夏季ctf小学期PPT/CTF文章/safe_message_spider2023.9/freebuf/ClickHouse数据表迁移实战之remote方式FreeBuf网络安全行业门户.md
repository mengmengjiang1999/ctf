# 1 引言

大家好，ClickHouse是一个用于联机分析(OLAP)的列式数据库管理系统(DBMS)。我们内部很多的报表、数据看板都基于它进行开发。今天为大家带来remote方式的ClickHouse数据表迁移的完整过程介绍，如有错误，还请各位大佬指正。

以下sql语句为测试使用，如需使用请根据实际情况修改。

# 2 背景

我们使用的是京东云提供的分布式数据库
JCHDB，原ClickHouse是两个部门共用的，因涉及相关业务、管理及费用划分等问题，需进行ClickHouse集群的分离。原ClickHouse面包含表有：业务A订单表与业务B大屏数据表；拆分后需要将业务B的大屏数据表迁移到新ClickHouse集群中去。

# 3 迁移方式

经查阅，迁移方式有如下几种：

1.通过remote函数进行数据迁移

2.通过文件导出导入方式进行数据迁移

3.通过CSV文件导出导入

4.通过Linux pipe管道进行流式导出导入

京东云JCHDB详细方案可参考文档：  
https://docs.jdcloud.com/cn/jchdb/local-clickhouse-clickhouse

经过与云JCHDB负责运维同事沟通及调研，因数据量目前不大，比较适合采用remote方式进行迁移，注意remote使用的前提要求即可。如果数量过大请参考其他迁移方式。

remote方式使用前，请增加  
max_partitions_per_insert_block参数值，避免语句执行失败，示例报如下错误：

    
    
    报错：
    Too many partitions for single INSERT block (more than 100). The limit is controlled by 'max_partitions_per_insert_block' setting
    
    原因：
    clickhouse 要求每次写入的数据不能跨越特别多的 partitions，具体受参数 max_partitions_per_insert_block 控制，调整该参数即可。
    
    

# 4 步骤

1\. 创建新clickhouse集群：请到云管平台申请，请先预估好业务未来数据量，再去填写申请的容量配置；

2\. 创建数据库：

    
    
    CREATE DATABASE IF NOT EXISTS new_database on cluster default;
    
    

注意后面的on cluster default;必须带上。

3\. 创建表：

根据实际表字段、表引擎编写sql。参考：  
https://clickhouse.com/docs/zh/sql-reference/statements/create/table

4\. 建立测试表

    
    
    CREATE TABLE 
    IF NOT EXISTS new_database.test_ck_01_local ON CLUSTER default
    ( 
        id String COMMENT '随机主键',
        dt Date COMMENT '分区字段'
    ) 
    ENGINE = ReplicatedReplacingMergeTree
    ('/clickhouse/new_database/tables/{shard}/test_ck_01_local', '{replica}')
    PARTITION BY toYYYYMMDD
    (dt) 
    ORDER BY id;
    
    CREATE TABLE
    IF NOT EXISTS new_database.test_ck_01 ON CLUSTER default AS new_database.test_ck_01_local
    ENGINE=Distributed(default, new_database, test_ck_01_local, rand());
    
    

5\. 写入测试数据：

    
    
    在原clickhouse里执行写入数据语句：
    INSERT INTO old_database.test_ck_01 values('1',NOW());
    INSERT INTO old_database.test_ck_01 values('2',NOW());
    根据实际情况多些一些数据即可。
    
    从新ClickHouse集群客户端里执行查询语句：（如不成功说明网络不通）
    SELECT * from 
    remote('老集群地址',old_database.test_ck_01,'user','password')
    
    

6\. 测试迁移命令：

    
    
    INSERT INTO new_database.test_ck_01
    SELECT * from 
    remote('老集群地址',old_database.test_ck_01,'user','password')
    
    

7\. 正式迁移步骤如下：

  * 提前修改代码里的clickhouse地址，替换新地址；
  * 通知大数据实时负责人停止flink等写入任务；
  * 进行数据迁移到新ClickHouse集群（参考以上迁移语句）；
  * 通知大数据实时负责人开启flink等写入任务；
  * 验证数据是否同步到新ClickHouse集群；
  * 在灰度或预发环境部署或重启，通过代码调用查询新ClickHouse集群看是否正常。

8\. 迁移语句：（在目标clickhouse集群客户端内执行）

    
    
    INSERT INTO new_database.待迁移的数据表
    SELECT * from 
    remote('老集群地址',old_database.老数据表,'user','password')
    
    

9\. 验证表数据量是否一致：

    
    
    SELECT COUNT(1) from 待迁移的数据表 final
    
    

**注意：** 迁移完成后数据量可能不一致，请使用 final合并查询，会把重复的数据条目进行合并。

# 5 参考

官方文档：  
https://clickhouse.com/docs/zh

京东云clickhouse学习：  
https://docs.jdcloud.com/cn/jchdb/product-overview

remote使用：  
https://blog.csdn.net/u010180815/article/details/115070235

> 作者：京东物流 刘邓忠
>
> 内容来源：京东云开发者社区

