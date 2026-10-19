## **0x 01 背景**

企业在建设SIEM威胁事件管理系统时，要考虑对应各种安全设备，对设备数据时行聚合、分析、可视化、告警。对接防火墙日志设备时遇到一个问题：防火墙设备，告警信息，一般者支持Syslog日志外发，有的防火墙也支持Kafka直接外发，但太多数设备是不支持Kafka外发的，即使支持Kafka外发，也不支持Kafka集群外发、授权访问外发。

所以，我们的需求如下：

1.让安全设备外发告警支持Kafka外发。

2.让安全设备外发告警支持Kafka授权外发。

3.让安全设备外发告警支持Kakfa集群授权外发。

接下来就是要接一个转换过程，将Syslog日志转发到Kakfa带授权的集群上，对Kafka队列的数据进行生产。为了解决这个问题，解决这种问题有很多技术方案。我们这次介绍使用Syslog-NG来实现以上几个功能需求。

##  **0x02 Syslog日志直接转存Kafka**

Syslog-NG启动一个UDP、TCP的Syslog监听，当Syslog-NG接收Syslog日志后，通过Syslog-NG插件，直接将Syslog日志转存到Kafka上。

首先是安装Syslog-NG，如下：``

`sudo yum install syslog-ng`

再安装Syslog-NG的Kafka插件，如下：

`sudo yum install syslog-ng-kafka`

安装后，我们可以通过下面的命令看Kafka组件是否安装成功：

    
    
    syslog-ng -V
    
    
    syslog-ng --module-registry

配置Syslog-NG.conf，在配置文件中，加入如下写Kafka队列的内容， 如下：

![1651828818_6274e852114ebd297c706.png!small](https://image.3001.net/images/20220506/1651828818_6274e852114ebd297c706.png!small)

上面这段配置设置完成了，Syslog监听的数据，就会写到Kafka队列上。

##  **0x03 Syslog日志通过Syslog-NG转给Program**

我们可以通过的Syslog-NG将接收的Syslog日志，通过配置Sylog-NG，将日志数据通过Paragram关键字设定，转给一个外部的可执行程序，而这个外部可执行程序，我们配置的是一个Python程序，我们在Python程序中，
完成Syslog日志的接收到Kafka队列Topic写入这个过程。

![1651828861_6274e87d87bedd8d133a7.png!small](https://image.3001.net/images/20220506/1651828861_6274e87d87bedd8d133a7.png!small)

Python程序，如下：

![1651828899_6274e8a33a2cd07008f82.png!small](https://image.3001.net/images/20220506/1651828899_6274e8a33a2cd07008f82.png!small)

使用Program关键字是不依赖安装插件，只要在设置Program的地方调用外部执行程序就可了。

##  **0x04 防火墙外发日志写带授权Kafka集群**

生产环境下Kafka资源采用集群，及带账号授权的访问，正式的环境一般都设置密码，而且我们可以在Syslog-NG中不使用Pragram关键字，使用SyslogNG的Kafka组件直接在配置文件中写入Python代码。

![1651828937_6274e8c9e141e5dd55b8f.png!small](https://image.3001.net/images/20220506/1651828937_6274e8c9e141e5dd55b8f.png!small)

这种方式，是直接在syslog-ng.conf里配置Python程序进行处理，大家可以参考0x03节的Python操作Kafka的代码，移植到Python代码当中，
完成对Kafka队列写操作。

0x05 写Kafka的意义

为什么我们要将防火墙的Syslog日志写入到Kafka队列中，是因为后续应用Kafka队列完成SIEM系统的实时计算、全流量告警日志长周期保存准备。通过将Syslog日志转给Kafka，进行在后续数据平台上的计算、查询、审计报警。

![1651816930_6274b9e2328b9263481f6.png!small](https://image.3001.net/images/20220506/1651816930_6274b9e2328b9263481f6.png!small)

当数据进入大数据存储平台，就了对应的查询审计方法，我们统计了一下常用数据处理平台的查询方法。

安全设备->

|

  

Syslog->

|

  

Syslog->Kafka->

|

  

HDFS->

|

  

Hive SQL

|

  

SQL  
  
---|---|---|---|---|---  
  
  

|

  

Kafka->

|

  

Graylog->

|

  

Spark->

|

  

Spark SQL

|

  

SQL  
  
  

|

  

|

  

|

  

Flink->

|

  

Flink SQL

|

  

SQL  
  
  

|

  

|

  

|

  

ElasticSearch->

|

  

MYSQL

|

  

MySQL  
  
  

|

  

|

  

|

  

|

  

DSL

|

  

DSL  
  
  

|

  

|

  

|

  

Clickhouse

|

  

SQL

|

  

SQL  
  
比如，我们将防火墙日志，同过Kafka接入ES，我们除了可以使用ES自身的DSL，还可以使用Kibanna的DSL，如果安装的插件，还可以执行SQL进行审计查询。

![1651828960_6274e8e0291916077a789.png!small](https://image.3001.net/images/20220506/1651828960_6274e8e0291916077a789.png!small)

这是将不支持Kafka日志外发的防火的日志、数据代理日志，通过Syslog到Kafka的转存，写到ES后，用Kibana的DevTools通过ES的SQL插件进行日志SQL查询，而防火墙设备很多时候显然是不支持这种查询的，通过以上的方案配合实现了这种数据审计。

![1651828974_6274e8ee45776f1287965.png!small](https://image.3001.net/images/20220506/1651828974_6274e8ee45776f1287965.png!small)

## 0x05 总结

本篇主要解决的问题是， 传统的防火墙设备在对接企业SIEM威胁事件管理平台时，
单纯的Syslog协议的日志告警外发，不能满足各种大数据平台需求，因此，在设备没有对设备添加新的Kafka日志外发功能之前，通过对已有的Syslog日志的数据转发，达到接入SIEM数据实时分析平台的目的，实现的方法有很多种，我们选择了一个成本相对较低的实现方案，对那没有过多硬件资源的单位和机构，此种方法实现更灵活，成本相对更低廉。

