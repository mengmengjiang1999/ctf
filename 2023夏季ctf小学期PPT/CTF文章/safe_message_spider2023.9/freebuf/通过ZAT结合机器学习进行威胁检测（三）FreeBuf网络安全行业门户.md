## 系列文章

[通过ZAT结合机器学习进行威胁检测](https://www.freebuf.com/geek/244263.html)

[通过ZAT结合机器学习进行威胁检测（二）](https://www.freebuf.com/geek/244688.html)

## 从zeek日志到Parquet

首先我这里简单介绍一下parquet。Parquet出现的目的是使Hadoop生态系统中的任何项目都可以利用压缩，高效的列式数据，是Hadoop生态系统中任何项目均可使用的列式存储格式。

### 软件

> Zeek分析工具（ZAT）
>
> parquet
>
> spark

### 数据

zeek中大约 2300万行的数据集

导入所需要的库

![](https://image.3001.net/images/20200804/1596506306.jpg!small)

## 使用4个并行执行器启动Spark

在这里，我们使用4个并行执行器来构建本地Spark服务器。我这边是在MAC上运行，对于spark服务器我建议采用至少8核的服务器。以下代码启动4个执行程序并加载conn.log数据到spark

![](https://image.3001.net/images/20200804/1596507855.jpg!small)

# Spark Worker和数据分区

Spark将读入并将数据分区给我们的工作人员。我们的dataframe(rdd)方法将具有一些在工作池中划分的分区。每个工作人员将仅对一部分数据进行操作如下所示

![](https://image.3001.net/images/20200804/1596509019.png!small)
spark_df.rdd.getNumPartitions()

# 将我的Zeek日志转换为Parquet文件

Apache Parquet是一种专注于性能的列式存储格式。这是我们将Zeek /
Zeek日志转换为Parquet文件的代码，只需一行代码。由于我们使用Spark分布式执行程序进行转换，因此该转换具有超级可伸缩性。

![](https://image.3001.net/images/20200804/1596509651.jpg!small)

# Parquet files are compressed

在这里我们可以看到parquet以压缩列格式存储数据，有几种压缩选型可以选择

原始conn.log数据达到了2个G

经过parquet后约420MB左右

现在我们将parquet的数据加载到了spark，我们演示了一些简单的spark的操作

首先获取有关spark dataframe的数据

![](https://image.3001.net/images/20200804/1596510418.jpg!small)

    
    
    Number of Rows: 22694356
    Columns: ts,uid,id_orig_h,id_orig_p,id_resp_h,id_resp_p,proto,service,duration,orig_bytes,resp_bytes,conn_state,local_orig,missed_bytes,history,orig_pkts,orig_ip_bytes,resp_pkts,resp_ip_bytes,tunnel_parents

下面的查询是对4个执行程序的。数据包含超过2200万个zeek conn日志条目，完成时间仅仅是mac电脑上运行的一秒钟时间

![](https://image.3001.net/images/20200804/1596511873.jpg!small)![](https://image.3001.net/images/20200804/1596512819.jpg!small)

让我们看一下各个主机，按端口和服务分组

![](https://image.3001.net/images/20200804/1596520850.jpg!small)![](https://image.3001.net/images/20200804/1596520918.jpg!small)

## 总结

Spark具有强大的SQL引擎以及机器学习库。现在，我们已经将数据加载到Spark Dataframe中，下一章我们将利用Spark
SQL命令使用Spark MLLib进行一些分析和聚类

