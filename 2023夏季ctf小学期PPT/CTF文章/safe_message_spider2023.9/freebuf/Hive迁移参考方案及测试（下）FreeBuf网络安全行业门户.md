聊完Hive的架构、工作原理，以及迁移方案，让我们一起来看下Hive的迁移测试。

## 准备测试环境

 **(1）创建两个京东云JMR集群**

其中hive和hadoop的版本如下：

hive版本：2.3.7

hadoop版本：2.8.5

 **（2）为Master节点设置环境变量，方便执行hive/hadoop命令**

在/etc/profile中文件末尾增加：

export PATH=$PATH:/data0/apache-hive-2.3.7-bin/bin:/data0/hadoop-2.8.5/bin

完成后 source /etc/profile

 **（3）切换到Hadoop用户**

su hadoop

## 构造常用hive表及数据

 **（1）准备数据**

本地创建文件 user.txt 文本文件

#构造的数据

10,wang,20,jiangsu,xuzhou

11,liu,32,jiangsu,xuzhou

12,ren,34,jiangsu,nanjing

100,cao,34,guangdong,shenzhen

101,li,33,guangdong,shenzhen

102,ma,23,guangdong,guangzhou

1000,cui,12,shan'xi,xi'an

1001,jia,23,shan'xi,xi'an

1002,mi,23,shan'xi,xi'an

1003,ai,23,shan'xi,xi'an

 **（2）创建Hive库**

进入Master节点

#在JMR环境中启动hive

hive

#创建数据库

hive> create database user_info_db;

#使用新创建的数据库

use user_info_db;

 **（3）创建Hive表并灌入数据**

常见的Hive表主要有内部表、普通外部表、外部表、分区表、分桶表、分桶排序表、倾斜表等。以下针对每类表都创建一个表进行迁移测试。

 **a >内部表**

#创建表

create table user_tbl_internal(

uid int,

name string,

age int,

province string,

city string)

row format delimited fields terminated by ','

lines terminated by '\n';

#加载数据

load data local inpath '/root/user.txt' into table user_tbl_internal;

#查看HDFS的文件

hadoop fs -ls /apps/hive/warehouse/user_info_db.db/user_tbl_internal

 **b >外部表**

#创建一个外表，存储用户信息

create external table user_tbl_ext(

uid int,

name string,

age int,

province string,

city string)

row format delimited fields terminated by ','

lines terminated by '\n';

#加载数据

load data local inpath '/root/user.txt' into table user_tbl_ext;

#查看HDFS的文件

hadoop fs -ls /apps/hive/warehouse/user_info_db.db/user_tbl_ext

 **3 >分区表**

#分区表的定义：在数据量非常大的时候，为了提升查询效率，节省查询时间，把表数据分散到子目录下的方式就是分区表

#分区表适合的场景和目的：适合对数据量大、有明确合适的分区字段，使用分区字段作为查询条件以提升查询效率。

举例：

#当有海量的数据保存在HDFS某一个hive表名对应的目录下时，使用hive进行操作时，通常会搜索这个目录下所有的文件，会非常耗时；

#如果我们知道这些数据的某些特征，在使用hive进行操作的时候，就可以在where子句中对这些特征进行过滤，那么操作就会在符合条件的子目录下进行，其他不符合条件的目录下的内容就不会被处理。从而提高处理的效率。

#内部表和外部表都可以使用分区的功能，使用分区的内部或外部表称为分区表

#创建一个分区外表，存储用户信息：注意分区字段不能再作为表的一个列名

create external table user_tbl_ext_parti(

uid int,

name string,

age int)

partitioned by(province string, city string)

row format delimited fields terminated by ','

lines terminated by '\n';

#动态导入：

#一般情况在我们都是使用动态分区导入数据

#分区字段有多少个不同的值，就有几个文件。相同分区的数据存放在同一个文件中。

#在导入数据之前必须执行下面的两条语句让hive支持动态分区功能，默认是不支持动态分区的:

set hive.exec.dynamic.partition=true;

set hive.exec.dynamic.partition.mode=nonstrict;

#动态分区导入数据的sql语句：

insert overwrite table user_tbl_ext_parti

partition(province, city)

select uid, name, age, province, city from user_tbl_ext;

#查看数据文件内容

hadoop fs -cat
/apps/hive/warehouse/user_info_db.db/user_tbl_ext_parti/province=jiangsu/city=xuzhou/000000_0

10,wang,20

11,liu,32

#查看分区表在HDFS中的存放

#多个分区字段，则会有多级目录

[root@P4anyrQH-Master1 bin]# hadoop fs -ls
/apps/hive/warehouse/user_info_db.db/user_tbl_ext_parti/*

Found 2 items

drwxrwxrwx - hadoop supergroup 0 2021-03-23 20:25
/apps/hive/warehouse/user_info_db.db/user_tbl_ext_parti/province=guangdong/city=guangzhou

drwxrwxrwx - hadoop supergroup 0 2021-03-23 20:25
/apps/hive/warehouse/user_info_db.db/user_tbl_ext_parti/province=guangdong/city=shenzhen

Found 2 items

drwxrwxrwx - hadoop supergroup 0 2021-03-23 20:25
/apps/hive/warehouse/user_info_db.db/user_tbl_ext_parti/province=jiangsu/city=nanjing

drwxrwxrwx - hadoop supergroup 0 2021-03-23 20:25
/apps/hive/warehouse/user_info_db.db/user_tbl_ext_parti/province=jiangsu/city=xuzhou

Found 1 items

drwxrwxrwx - hadoop supergroup 0 2021-03-23 20:25
/apps/hive/warehouse/user_info_db.db/user_tbl_ext_parti/province=shan%27xi/city=xi%27an

#注意：在使用insert overwrite table
#select方式导入数据到分区表时，有多个分区字段时，分区partition中的字段顺序必须和select字段的顺序一致。

补充：也可以使用如下方式进行数据加载，不过需要指定具体的分区字段的值

#加载数据

load data local inpath '/root/user.txt' into table user_tbl_ext_parti
partition (provice = "hebei",city = "handan");

 **4 >分桶表**

#对于每一个表（table）或者分区，
Hive可以进一步组织成桶，也就是说桶是更为细粒度的数据范围划分。Hive采用对列值哈希，然后除以桶的个数求余的方式决定该条记录存放在哪个桶当中。

#适用场景：当数据量比较大，我们需要更快的完成任务，多个map和reduce进程是唯一的选择。但是如果输入文件是一个的话，map任务只能启动一个。此时分桶表是个很好的选择，通过指定CLUSTERED的字段，将文件通过hash打散成多个小文件。

#把表（或者分区）组织成桶（Bucket）有两个好处：

#1)获得更高的查询处理效率。桶为表加上了额外的结构，Hive
在处理有些查询时能利用这个结构。具体而言，连接两个在（包含连接列的）相同列上划分了桶的表，可以使用 Map 端连接 （Map-side
join）高效的实现。比如JOIN操作。对于JOIN操作两个表有一个相同的列，如果对这两个表都进行了桶操作。那么将保存相同列值的桶进行JOIN操作就可以，可以大大较少JOIN的数据量。

#2)使取样（sampling）更高效。在处理大规模数据集时，在开发和修改查询的阶段，如果能在数据集的一小部分数据上试运行查询，会带来很多方便。

#分桶是将某个字段取哈希值，值相同的数据分发到一个桶中;

#在创建分桶表的时候必须指定分桶的字段，并且指定要分桶的数量;

#创建分桶表

create external table user_tbl_ext_parti_bucket(

uid int,

name string,

age int)

partitioned by(province string, city string)

clustered by(age) into 2 buckets

row format delimited fields terminated by ','

lines terminated by '\n';

#设置使用分桶

#插入数据之前需要设置参数hive.enforce.bucketing=true，以强制hive的reducer数目为分桶数。如果不设置这个hive参数，最后的桶个数可能不是建表语句中的个数。

set hive.enforce.bucketing = true;

#导入数据：分区表会以MapReduce任务的方式加载数据

insert overwrite table user_tbl_ext_parti_bucket

partition(province, city)

select uid, name, age, province, city from user_tbl_ext;

#查看分桶表在HDFS中的存放

#多个分区字段，则会有多级目录

hadoop fs -ls /apps/hive/warehouse/user_info_db.db/user_tbl_ext_parti_bucket/*

Found 2 items

drwxrwxrwx - hadoop supergroup 0 2021-03-23 20:39
/apps/hive/warehouse/user_info_db.db/user_tbl_ext_parti_bucket/province=guangdong/city=guangzhou

drwxrwxrwx - hadoop supergroup 0 2021-03-23 20:39
/apps/hive/warehouse/user_info_db.db/user_tbl_ext_parti_bucket/province=guangdong/city=shenzhen

Found 2 items

drwxrwxrwx - hadoop supergroup 0 2021-03-23 20:39
/apps/hive/warehouse/user_info_db.db/user_tbl_ext_parti_bucket/province=jiangsu/city=nanjing

drwxrwxrwx - hadoop supergroup 0 2021-03-23 20:39
/apps/hive/warehouse/user_info_db.db/user_tbl_ext_parti_bucket/province=jiangsu/city=xuzhou

Found 1 items

drwxrwxrwx - hadoop supergroup 0 2021-03-23 20:39
/apps/hive/warehouse/user_info_db.db/user_tbl_ext_parti_bucket/province=shan%27xi/city=xi%27an

#查看分桶情况：

[hadoop@P4anyrQH-Master1 root]$ hadoop fs -ls
/apps/hive/warehouse/user_info_db.db/user_tbl_ext_parti_bucket/province=shan%27xi/city=xi%27an

Found 2 items

-rwxrwxrwx 3 hadoop supergroup 12 2021-03-23 21:00 /apps/hive/warehouse/user_info_db.db/user_tbl_ext_parti_bucket/province=shan%27xi/city=xi%27an/000000_0

-rwxrwxrwx 3 hadoop supergroup 34 2021-03-23 21:00 /apps/hive/warehouse/user_info_db.db/user_tbl_ext_parti_bucket/province=shan%27xi/city=xi%27an/000001_0

#查看分桶后的文件内容：确实根据分桶值分配到2个桶里了

[hadoop@P4anyrQH-Master1 root]$ hadoop fs -cat
/apps/hive/warehouse/user_info_db.db/user_tbl_ext_parti_bucket/province=shan%27xi/city=xi%27an/000000_0

1000,cui,12

[hadoop@P4anyrQH-Master1 root]$ hadoop fs -cat
/apps/hive/warehouse/user_info_db.db/user_tbl_ext_parti_bucket/province=shan%27xi/city=xi%27an/000001_0

1003,ai,23

1002,mi,23

1001,jia,23

 **5 >分桶排序表：Bucketed Sorted Tables**

分桶排序表形如：CLUSTERED BY(userid) SORTED BY(viewTime) INTO 32 BUCKETS

#创建分桶排序表

create external table user_tbl_ext_parti_bucket_sort(

uid int,

name string,

age int)

partitioned by(province string, city string)

clustered by(age) sorted by(age) into 2 buckets

row format delimited fields terminated by ','

lines terminated by '\n';

#设置使用分桶

#插入数据之前需要设置参数hive.enforce.bucketing=true，以强制hive的reducer数目为分桶数。如果不设置这个hive参数，最后的桶个数可能不是建表语句中的个数。

set hive.enforce.bucketing = true;

#导入数据：分区表会以MapReduce任务的方式加载数据

insert overwrite table user_tbl_ext_parti_bucket_sort

partition(province, city)

select uid, name, age, province, city from user_tbl_ext;

#查看分桶表在HDFS中的存放

[root@P4anyrQH-Master1 ~]# hadoop fs -ls
/apps/hive/warehouse/user_info_db.db/user_tbl_ext_parti_bucket_sort/*

Found 2 items

drwxrwxrwx - hadoop supergroup 0 2021-03-25 12:03
/apps/hive/warehouse/user_info_db.db/user_tbl_ext_parti_bucket_sort/province=guangdong/city=guangzhou

drwxrwxrwx - hadoop supergroup 0 2021-03-25 12:03
/apps/hive/warehouse/user_info_db.db/user_tbl_ext_parti_bucket_sort/province=guangdong/city=shenzhen

Found 2 items

drwxrwxrwx - hadoop supergroup 0 2021-03-25 12:03
/apps/hive/warehouse/user_info_db.db/user_tbl_ext_parti_bucket_sort/province=jiangsu/city=nanjing

drwxrwxrwx - hadoop supergroup 0 2021-03-25 12:03
/apps/hive/warehouse/user_info_db.db/user_tbl_ext_parti_bucket_sort/province=jiangsu/city=xuzhou

Found 1 items

drwxrwxrwx - hadoop supergroup 0 2021-03-25 12:03
/apps/hive/warehouse/user_info_db.db/user_tbl_ext_parti_bucket_sort/province=shan%27xi/city=xi%27an

#查看分桶排序表在HDFS中的存放及内容

[root@P4anyrQH-Master1 ~]# hadoop fs -ls
/apps/hive/warehouse/user_info_db.db/user_tbl_ext_parti_bucket_sort/province=shan%27xi/city=xi%27an/*

-rwxrwxrwx 3 hadoop supergroup 12 2021-03-25 12:03 /apps/hive/warehouse/user_info_db.db/user_tbl_ext_parti_bucket_sort/province=shan%27xi/city=xi%27an/000000_0

-rwxrwxrwx 3 hadoop supergroup 34 2021-03-25 12:03 /apps/hive/warehouse/user_info_db.db/user_tbl_ext_parti_bucket_sort/province=shan%27xi/city=xi%27an/000001_0

[root@P4anyrQH-Master1 ~]# hadoop fs -cat
/apps/hive/warehouse/user_info_db.db/user_tbl_ext_parti_bucket_sort/province=shan%27xi/city=xi%27an/000000_0

1000,cui,12

You have mail in /var/spool/mail/root

[root@P4anyrQH-Master1 ~]# hadoop fs -cat
/apps/hive/warehouse/user_info_db.db/user_tbl_ext_parti_bucket_sort/province=shan%27xi/city=xi%27an/000001_0

1003,ai,23

1002,mi,23

1001,jia,23

#登录源数据库MySQL查看排序相关信息

mysql -hlocalhost -uhive -p

mysql> use hive;

mysql> select * from SORT_COLS;

+-------+-------------+-------+-------------+

| SD_ID | COLUMN_NAME | ORDER | INTEGER_IDX |

+-------+-------------+-------+-------------+

| 31 | age | 1 | 0 |

| 32 | age | 1 | 0 |

| 33 | age | 1 | 0 |

| 34 | age | 1 | 0 |

| 35 | age | 1 | 0 |

| 36 | age | 1 | 0 |

+-------+-------------+-------+-------------+

6 rows in set (0.00 sec)

## HDFS迁移

 **（1）迁移HDFS数据**

 **a >全量数据迁移**

数据全量迁移：

su hadoop

hadoop distcp -i -log /home/hadoop/logs
HDFS://192.168.0.5:8020/apps/hive/warehouse/
HDFS://192.168.0.8:8020/apps/hive/warehouse

 **b >增量数据迁移**

#新增一张表

su hadoop

\--创建表

create table user_tbl_add_1(

uid int,

name string,

age int,

province string,

city string)

row format delimited fields terminated by ','

lines terminated by '\n';

\--加载数据

load data local inpath '/home/hadoop/user.txt' into table user_tbl_add_1;

\--查看HDFS的文件

hadoop fs -ls /apps/hive/warehouse/user_info_db.db/user_tbl_add_1

#原表新增数据

insert into table user_tbl_internal

select uid, name, age, province, city from user_tbl_add_1;

#开始增量迁移

su hadoop

hadoop distcp -i -delete -log /home/hadoop/logs -update
HDFS://192.168.0.5:8020/apps/hive/warehouse/
HDFS://192.168.0.8:8020/apps/hive/warehouse

 **（2）HDFS数据一致性校验**

 **a >校验 HDFS 数据目录文件数量是否一致**

#查看源和目标HDFS的目录、文件数、文件内容大小是否相同：

[hadoop@P4anyrQH-Master1 logs]$ hadoop fs -count -v -x /apps/hive/warehouse

DIR_COUNT FILE_COUNT CONTENT_SIZE PATHNAME

36 32 1632 /apps/hive/warehouse

[root@iQotdoaa-Master1 ~]# hadoop fs -count -v -x /apps/hive/warehouse

DIR_COUNT FILE_COUNT CONTENT_SIZE PATHNAME

36 32 1632 /apps/hive/warehouse

经查目录数、文件数、字节数均相同，迁移完成。

 **b >校验 HDFS 数据目录文件数量是否一致**

[hadoop@P4anyrQH-Master1 root]$ hadoop fs -ls -R -C /apps/hive/warehouse

/apps/hive/warehouse/user_info_db.db

/apps/hive/warehouse/user_info_db.db/user_tbl_ext

/apps/hive/warehouse/user_info_db.db/user_tbl_ext/user.txt

/apps/hive/warehouse/user_info_db.db/user_tbl_ext_parti

/apps/hive/warehouse/user_info_db.db/user_tbl_ext_parti/province=guangdong

...

在源集群切换到root用户，执行：hadoop fs -ls -R -C /apps/hive/warehouse > srcfilelist

在目标集群切换到root用户，执行：hadoop fs -ls -R -C /apps/hive/warehouse > dstfilelist

使用diff命令进行比较：

[root@P4anyrQH-Master1 ~]# diff srcfilelist dstfilelist -s --normal

Files srcfilelist and dstfilelist are identical

经查目录和文件列表相同。

 **c >校验 HDFS 数据目录文件内容是否一致**

#查看源端文件MD5值

[hadoop@P4anyrQH-Master1 logs]$ hadoop fs -checksum
/apps/hive/warehouse/user_info_db.db/user_tbl_ext/000000_0

/apps/hive/warehouse/user_info_db.db/user_tbl_ext/000000_0
MD5-of-0MD5-of-512CRC32C
0000020000000000000000000a59f8a9ab89996e42566969734e21ee

#查看目标端文件MD5值

[root@iQotdoaa-Master1 ~]# hadoop fs -checksum
/apps/hive/warehouse/user_info_db.db/user_tbl_ext/000000_0

/apps/hive/warehouse/user_info_db.db/user_tbl_ext/000000_0
MD5-of-0MD5-of-512CRC32C
0000020000000000000000000a59f8a9ab89996e42566969734e21ee

#MD5值相同表示

经查文件MD5相同，此文件迁移成功。

## Hive元数据迁移

 **（1）迁移Hive元数据**

从源集群导出元数据：

mysqldump -hlocalhost -uhive -p --databases hive > hive_bk.sql

导入目标集群：

[root@iQotdoaa-Master1 ~]# mysql -hlocalhost -uhive -p

mysql> source hive_bk.sql

checksum校验数据：

./checksum_table --src-host mysql-xxx.rds.jdcloud.com --src-user 'user-xxx'
--src-pass 'password-xxx' --dest-host mysql-xxx.rds.jdcloud.com --dest-user
'user-xxx' --dest-pass 'password-xxx' --ws 30 --database 'dbname-xxx'

 **（2）修正Hive 元数据中与HDFS路径相关的信息**

元数据从源集群迁移到目标集群后，修正元数据中HDFS路径相关信息：

update SDS set location = (select replace(location, 'P4anyrQH-Master1.jcloud.local', 'iQotdoaa-Master1.jcloud.local') ) where location like
'%P4anyrQH-Master1.jcloud.local%';

update DBS set DB_LOCATION_URI = (select replace(DB_LOCATION_URI, 'P4anyrQH-Master1.jcloud.local', 'iQotdoaa-Master1.jcloud.local') ) where
DB_LOCATION_URI like '%P4anyrQH-Master1.jcloud.local%';

update SKEWED_COL_VALUE_LOC_MAP set LOCATION = (select replace(LOCATION,
'P4anyrQH-Master1.jcloud.local', 'iQotdoaa-Master1.jcloud.local') ) where
LOCATION like '%P4anyrQH-Master1.jcloud.local%';

update SERDE_PARAMS set PARAM_VALUE = (select replace(PARAM_VALUE, 'P4anyrQH-Master1.jcloud.local', 'iQotdoaa-Master1.jcloud.local') ) where PARAM_VALUE
like '%P4anyrQH-Master1.jcloud.local%';

update TABLE_PARAMS set PARAM_VALUE = (select replace(PARAM_VALUE, 'P4anyrQH-Master1.jcloud.local', 'iQotdoaa-Master1.jcloud.local') ) where PARAM_VALUE
like '%P4anyrQH-Master1.jcloud.local%';

## 迁移验证

 **（1）基础迁移**

修正元数据后可以在目标新集群正常访问hive表数据

hive> select * from user_tbl_ext_parti_bucket;

OK

102 ma 23 guangdong guangzhou

100 cao 34 guangdong shenzhen

101 li 33 guangdong shenzhen

12 ren 34 jiangsu nanjing

11 liu 32 jiangsu xuzhou

10 wang 20 jiangsu xuzhou

1000 cui 12 shan'xi xi'an

1003 ai 23 shan'xi xi'an

1002 mi 23 shan'xi xi'an

1001 jia 23 shan'xi xi'an

Time taken: 0.122 seconds, Fetched: 10 row(s)

hive>

 **（2）业务迁移**

构造业务 test.sql并执行。

## 构造大量表和海量数据进行迁移测试

有条件的情况下，建议进行大量Hive元数据库表及海量HDFS文件数据迁移的测试验证。

  

