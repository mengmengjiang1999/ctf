**作者：京东物流 李光新**

## 1 治理背景

测试环境这个话题对于开发和测试同学一定不陌生，大家几乎每天都会接触。但是说到对测试环境的印象，却鲜有好评:

•环境不稳定，测试五分钟，排查两小时

•基础建设不全，导致验证不充分，遗漏缺陷

•多人共用，节点堵塞

这些问题在行业内其实屡见不鲜，针对测试环境的治理，不得不引起我们的重视。

首先我们要清晰的认知到，测试环境管理做的不好，不光有严重的质量风险，还会非常影响迭代效率，所以这件事情很重要。那在解决它之前，我们首先要去想想，对于测试环境我们到底有哪些诉求？

很明显，测试环境的定位就是满足产研测的测试需求，保障产品迭代质量。所以从使用类型上，一般要支撑集成测试，系统测试，甚至故障测试等。

而这些环境背后，其实都伴随着 **非功能性要求** ，重点体现在:

1.从使用者角度

•想用就有，不要等待

•要低维护，高稳定

2.从企业角度

•低成本，高效率

简单总结一下，理想的测试环境应该是：自由连接、随时可用、互访可控。

那么现实中的测试环境又是怎样的呢？所谓“理想很丰满，现实很骨感”，对于一线测试工程师可能会发现，真实的测试环境并非这么理想。

测试同学算是测试环境的主要使用者，对测试环境的管理理应负有直接责任。不过现实中，经常看到的是，测试同学因本身测试任务较多，且测试环境管理也要求具备一定的系统运维能力，导致相对而言，测试同学要想做好测试环境管理，也不容易~

下面就主要给大家分享一次实际工作中的Mysql性能优化实践，与大家共勉~

 **问题点** ：物流中台运单waybill.etms应用，由于包裹表未使用索引，导致的cpu飚高问题

## 2 分析过程

1.不管是在日常自动化测试还是功能测试过程中，经常会遇到数据库数据落库比较慢的场景，不仅影响功能测试进度，还会影响自动化的执行时长和成功率，在此背景下，展开如下排查工作~

2.查询两个异常运单，发现数据落库在十分钟以上，展开分析，

![1681796653_643e2e2dde98773d889cf.png!small](https://image.3001.net/images/20230418/1681796653_643e2e2dde98773d889cf.png!small)

3.发现都是查询delivery_package_d抛出异常，怀疑是不是共性问题；

    
    
    ybill_log.log:2022-03-17 14:42:03 ERROR com.jd.etms.waybill.worker.business.WaybillCreateFromBusiLogic handling:65 - Bus运单JDVE00001018005接货平台下发处理异常
    waybill_log.log-org.springframework.jdbc.UncategorizedSQLException: 
    waybill_log.log-### Error querying database. Cause: com.mysql.jdbc.exceptions.MySQLTimeoutException: Statement cancelled due to timeout or client request
    waybill_log.log-### The error may exist in mybatis/mysql/DeliveryPackageDDao.xml
    waybill_log.log-### The error may involve defaultParameterMap
    waybill_log.log-### The error occurred while setting parameters
    waybill_log.log-### SQL: select   package_id,package_barcode,waybill_code,vendor_barcode,good_weigth,good_volume,remark,  create_time,update_time,yn,again_weight,weigh_User_Name,weigh_Time,pack_time,again_weight_volume,package_state,data_version,flag,expected_delivered_time,packwk_no,store_id,cky2   from delivery_package_d  where waybill_code=? and yn=1
    waybill_log.log-### Cause: com.mysql.jdbc.exceptions.MySQLTimeoutException: Statement cancelled due to timeout or client request
    waybill_log.log-; uncategorized SQLException for SQL []; SQL state [null]; error code [0]; Statement cancelled due to timeout or client request; nested exception is com.mysql.jdbc.exceptions.MySQLTimeoutException: Statement cancelled due to timeout or client request
    waybill_log.log-    at org.springframework.jdbc.support.AbstractFallbackSQLExceptionTranslator.translate(AbstractFallbackSQLExceptionTranslator.java:83) ~[spring-jdbc-3.2.18.RELEASE.jar:3.2.18.RELEASE]

1.直接搜异常日志关键字，“接货平台下发处理异常”，确认推测正确；

  

![1681796665_643e2e3946f7f5e098019.png!small](https://image.3001.net/images/20230418/1681796665_643e2e3946f7f5e098019.png!small)

2.排查异常sql:

    
    
    waybill_log.log-### SQL: select   package_id,package_barcode,waybill_code,vendor_barcode,good_weigth,good_volume,remark,  create_time,update_time,yn,again_weight,weigh_User_Name,weigh_Time,pack_time,again_weight_volume,package_state,data_version,flag,expected_delivered_time,packwk_no,store_id,cky2   from delivery_package_d  where waybill_code=? and yn=1
    waybill_log.log-### Cause: com.mysql.jdbc.exceptions.MySQLTimeoutException: Statement cancelled due to timeout or client request

从上面sql中可以定位到，是查询表delivery_package_d时出现了问题，而且是 **执行超时**
，不是连接超时，所以可以排除是连接的问题，与研发沟通，怀疑是索引的问题；

1.然后排查数据库索引：

![1681796677_643e2e455d3b3d9089df0.png!small](https://image.3001.net/images/20230418/1681796677_643e2e455d3b3d9089df0.png!small)

  

运单数据库是分库分表的，上述包裹表delivery_package_d有两个表比另外两个表，少了两个索引，定位异常问题，然后添加索引；

    
    
    ALTER TABLE waybill_0.`delivery_package_d_0` ADD INDEX `idx_package` USING BTREE(`PACKAGE_BARCODE`);
    ALTER TABLE waybill_0.`delivery_package_d_0` ADD INDEX `idx_waybill_code` USING BTREE(`WAYBILL_CODE`);
    ALTER TABLE waybill_0.`delivery_package_d_0` ADD INDEX `idx_waybill_code_package` USING BTREE(`WAYBILL_CODE`, `PACKAGE_BARCODE`);
    ALTER TABLE waybill_0.`delivery_package_d_0` ADD PRIMARY KEY USING BTREE(`PACKAGE_ID`, `CREATE_TIME`);
    ALTER TABLE waybill_0.`delivery_package_d_1` ADD INDEX `idx_waybill_code` USING BTREE(`WAYBILL_CODE`);
    ALTER TABLE waybill_0.`delivery_package_d_1` ADD INDEX `idx_waybill_code_package` USING BTREE(`WAYBILL_CODE`, `PACKAGE_BARCODE`);
    ALTER TABLE waybill_0.`delivery_package_d_1` ADD PRIMARY KEY USING BTREE(`PACKAGE_ID`, `CREATE_TIME`);

2.查看数据库服务器性能，执行前后性能对比

![1681796693_643e2e55255447952b993.png!small](https://image.3001.net/images/20230418/1681796693_643e2e55255447952b993.png!small)

![1681796702_643e2e5e7b659fe115b03.png!small](https://image.3001.net/images/20230418/1681796702_643e2e5e7b659fe115b03.png!small)

添加索引后，自动化执行速度和成功率也有显著提升。

## 3 扩展分析

正常情况下，慢sql日志是存储在服务器上的，但是也可以通过mysql设置来通过数据库查看慢sql。

慢日志全称为慢查询日志（Slow Query Log），主要用来记录在 MySQL 中执行时间超过指定时间的 SQL
语句。通过慢查询日志，可以查找出哪些语句的执行效率低，以便进行优化。

默认情况下，MySQL 并没有开启慢日志，可以通过修改 slow_query_log 参数来打开慢日志。与慢日志相关的参数介绍如下：

• **slow_query_log** ：是否启用慢查询日志，默认为0，可设置为0、1，1表示开启。

• **slow_query_log_file** ：指定慢查询日志位置及名称，默认值为host_name-slow.log，可指定绝对路径。

• **long_query_time** ：慢查询执行时间阈值，超过此时间会记录，默认为10，单位为s。

• **log_output** ：慢查询日志输出目标，默认为file，即输出到文件。

• **log_timestamps** ：主要是控制 error log、slow log、genera log
日志文件中的显示时区，默认使用UTC时区，建议改为 SYSTEM 系统时区。

• **  
log_queries_not_using_indexes** ：是否记录所有未使用索引的查询语句，默认为off。

• **min_examined_row_limit** ：对于查询扫描行数小于此参数的SQL，将不会记录到慢查询日志中，默认为0。

• **log_slow_admin_statements** ：慢速管理语句是否写入慢日志中，管理语句包含 alter table、create
index 等，默认为 off 即不写入。

可以先来自定义慢sql时长，也就是语句执行超过多长时间会被定义为慢sql；

    
    
    show variables like 'long_query_time' //慢sql查询阈值设置

然后，开启是否记录所有未使用索引的查询语句开关  
log_queries_not_using_indexes，默认为off；

    
    
    SHOW variables LIKE 'log_queries_not_using_indexes' //查询未开启索引的开关；
    set global log_queries_not_using_indexes = on //开启索引监控开关；

上述开关开启之后，开始分析异常日志；

    
    
    show variables like 'log_output' - log_output 默认值是FILE，是输出在服务器上的；
    set global log_output = 'TABLE' - 设置为TABLE，可以直接从数据库查到；

通过数据库查询慢sql:

    
    
    select *from mysql.slow_log - 慢日志查询结果；

从上图中可以很明显的看出具体的慢sql涉及的表，及查询时长，后面就可以针对具体的表进行针对性的优化了~

当然，在实际环境下，不建议开启  
log_queries_not_using_indexes 参数，此参数打开后可能导致慢日志迅速增长。

所以，针对上述分析过程，各位操作完成后，可以再关闭慢日志输出到数据库，之后有分析需求再开启，这样就会有效减少对数据库的压力。

## 4 总结

综上，我们每个人不仅仅是测试环境的使用者，更是测试环境的建设者，每个人都需要有意识的把负责的服务测试环境稳定性提升上来，这样整体业务的测试环境稳定性才能有保障。

而且，对于测试环境管理和维护这条路，其实是随着解决的问题深入，需要有很深入的思考和解决问题能力，随之，对技术的要求也越来越高，当然，这也正是我们的价值所在。

以上，与君共勉~

