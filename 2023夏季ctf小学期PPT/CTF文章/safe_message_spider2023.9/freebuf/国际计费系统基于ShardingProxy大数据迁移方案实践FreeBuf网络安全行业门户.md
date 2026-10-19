## 1 背景

计费数据量剧增，需要将老库进行数据拆分到多个分库，数据分片；

拆分规则为收付款对象（或ID）字段，进行HASH，取模(32)，分32个库

## 2 目标

实现数据从老库，按照分片规则，迁移到分库中

保证数据平滑迁移，尽量停产时间最小

支持回滚，同步失败，支持回滚单库

## 3 方案

### 3.1 基于蜂巢中间件实现

![](https://image.3001.net/images/20220809/1660016312_62f1d6b871f7819de26c3.png!small)

### 3.2 半自研同步数据处理程序

  1. 开发数据处理程序，消费历史数据MQ；消费增量数据MQ
  2. 基于dts同步历史数据（指定时间位点，同步历史）
  3. 基于JDQ同步实时数据（指定时间位点，恢复实时同步）

![](https://image.3001.net/images/20220809/1660016313_62f1d6b9ad6c79a8634f5.png!small)

### 3.3 基于开源中间件策略

![](https://image.3001.net/images/20220809/1660016314_62f1d6baed273093c0f18.png!small)

### 3.4 完全自研数据处理工具

  1. 开发数据查询程序，历史数据查询发送MQ写入
  2. 实时数据双写
  3. 统一发送MQ，由MQ异步处理写入

![](https://image.3001.net/images/20220809/1660016316_62f1d6bc2e17be5367dd1.png!small)

### 3.5 方案对比

![](https://image.3001.net/images/20220809/1660016316_62f1d6bcc1f6e160f8c89.png!small)

 **综上整体评估，我们最终选取，基于sharding-proxy做数据迁移整体方案**

## 4 Proxy介绍与搭建

### 4.1 简介

#####  **4.1.1 设计意义**

定位为透明化的数据库代理端，提供封装了数据库二进制协议的服务端版本，用于完成对异构语言的支持。 目前提供 MySQL 和 PostgreSQL（兼容
openGauss 等基于 PostgreSQL 的数据库）版本，它可以使用任何兼容 MySQL/PostgreSQL 协议的访问客户端（如：MySQL
Command Client, MySQL Workbench, Navicat 等）操作数据，对 DBA 更加友好。

> 向应用程序完全透明，可直接当做 MySQL/PostgreSQL 使用；
>
> 适用于任何兼容 MySQL/PostgreSQL 协议的的客户端。

![](https://image.3001.net/images/20220809/1660016317_62f1d6bd6c4e77f89bd4c.png!small)

#####  **4.1.2 整体架构**

![](https://image.3001.net/images/20220809/1660016318_62f1d6be435690d358970.png!small)

整个架构可以分为前端、后端和核心组件三部分。

前端负责与客户端进行网络通信，采用的是基于NIO的客户端/服务器框架，在Windows和Mac操作系统下采用NIO模型，Linux系统自动适配为Epoll模型。通信的过程中完成对MySQL协议的编解码。核心组件得到解码的MySQL命令后，开始调用Sharding-Core对SQL进行解析、路由、改写、结果归并等核心功能。后端与真实数据库的交互目前借助于Hikari连接池。

### 4.2 搭建

#####  **4.2.1 关键字解读**

下载，解压，安装mysql驱动，启动，完事

##### 4.2.2 安装shareding-proxy

安装包下载，选择合适版本（本文选用4.1.1），在官网进行下载，官网地址<https://shardingsphere.apache.org/document/current/cn/downloads>

![](https://image.3001.net/images/20220809/1660016318_62f1d6beee34521fd0dc9.png!small)

安装包解压（自动解压，或是命令解压），解压目录自己随意指定（有权限目录均可）

![](https://image.3001.net/images/20220809/1660016320_62f1d6c06d2f607c79228.png!small)

解压后shareding-proxy目录

![](https://image.3001.net/images/20220809/1660016321_62f1d6c16025814076d1c.png!small)

shareding-proxy配置目录conf，包含所有配置数据

![](https://image.3001.net/images/20220809/1660016322_62f1d6c213dacca860a29.png!small)

##### 4.2.3 安装mysql驱动

将mysql的驱动jar包(mysql-connector-java-5.1.44.jar )放在shareding-proxy的lib目录下ShardingSphere-Proxy不带mysql驱动jar包，需要手动下载  
下载地址<https://dev.mysql.com/downloads/connector/j/>

![](https://image.3001.net/images/20220809/1660016322_62f1d6c2b98ede0d79c01.png!small)

#### 4.2.4 proxy启动

shareding-proxy的bin目录start.sh，通过./start.sh启动

![](https://image.3001.net/images/20220809/1660016323_62f1d6c3d7f4e1065a0d5.png!small)

##### 4.2.5 Remark

Sharding-Proxy默认的启动端口是3307

### 4.3 配置

##### 4.3.1 关键字解读

六大配置——日志配置(logback.xml)，基础服务配置(server.yaml)，逻辑配置(四个conf配置文件，分片（核心）/影子/读写分离/加密配置)  
本例基于server.yaml、config-sharding.yaml配置分片策略

##### 4.3.2 server.yaml

基础服务配置，三部分组成

###### 1）shareding-jdbc的编排治理配置，提供数据治理功能，包含如下：

> 配置集中化与动态化。（支持数据源，表与分片读写分离策略的动态切换）
>
> 数据治理。提供熔断数据库访问程序对数据库的访问和禁用从库的访问的能力
>
> 支持Zookeeper和etcd的注册中心；

![](https://image.3001.net/images/20220809/1660016324_62f1d6c491087ada62498.png!small)

###### 2）权限配置，配置用户名和密码以及授权数据库

下例配置两个用户，分别为：root/root和sharding/sharding，其中root默认授权所有的数据库，而sharding用户则授权sharding_db数据库。在这里的数据库（schema）是逻辑数据库，在config-*.yaml中配置对应分库映射

![](https://image.3001.net/images/20220809/1660016325_62f1d6c55b33853a9eeaa.png!small)

代理数据源参数配置

配置数据链接，线程，核数等

![](https://image.3001.net/images/20220809/1660016326_62f1d6c61ccf91eee1201.png!small)

##### 4.3.3 config-sharding.yaml

shareding-proxy核心配置，分片规则相关配置，包含schemaName、dataSources、shardingRule三部分

###### 1）下图逻辑库对应分库数据源的映射配置

schemaName逻辑库名，在server.yaml声明的授权的schema就是这里的schemaName

dataSources为数据源配置，本例映射俩个分库（ds0，ds_1），ds${0..1}对应逻辑分库名，url填写实际库

![](https://image.3001.net/images/20220809/1660016327_62f1d6c783748d2fbbd4d.png!small)

##### 4.3.4 logback.xml

基于logback的日志配置

##### 4.3.5 剩余三项配置

config-shadow.yaml/config-master_slave.yaml/config-encrypt.yaml  
分别为影子库配置，主从配置，数据字段加密配置，有意可以自行看下文链接

## 5 调试

基于搭建ShardingSphere-Proxy代理选择直连工具客户端

  1. 用Navicat或者mysql命令直连
  2. 手动mysql命令链接如下

![](https://image.3001.net/images/20220809/1660016328_62f1d6c88f71e1f6a85fe.png!small)

查询不带拆分键默认搜全库，新增默认根据拆分键路由对应真实库

## 6 数据迁移

 **迁移三步**

1）线上安装sharding-proxy  
2）数据同步：创建迁移任务，启动同步，原理即是创建DTS任务

![](https://image.3001.net/images/20220809/1660016329_62f1d6c9a9096beb84b15.png!small)

![](https://image.3001.net/images/20220809/1660016330_62f1d6caa3948fae44adf.png!small)

3）数据完整性校验

全量比对，整体同步进度查询

![](https://image.3001.net/images/20220809/1660016331_62f1d6cb692c3b14620dd.png!small)

时间分段比对，按照各个时间段抽样进行新库老库总量比对，手动校验

![](https://image.3001.net/images/20220809/1660016331_62f1d6cbdb0f648b3fb44.png!small)

随机抽样比对：随机新库某个时间段的数据逐条进行比对，手动工具校验  
手动根据开发工具分别抽样查询，并查询出的数据与老库进行比对

全量数据校验：对比同步数据进行全量数据校验，根据DTS工具进行校验，耗时较长

![](https://image.3001.net/images/20220809/1660016332_62f1d6cc80e1fdcbb0d65.png!small)

## 7 配置查询机

基于easyops或者myops配置物流指定查询机，通过查询机查询proxy代理实现

## 8 问题与总结

整体数据迁移过程中遇到的最大的问题即是数据不可测，针对各种历史数据问题导致数据迁移中断，造成返工，清理垃圾数据，重新迁移

### 8.1 拆分键为空

拆分键为空默认不支持

![](https://image.3001.net/images/20220809/1660016333_62f1d6cd35b6c764535ea.png!small)

### 8.2 更新拆分键

更新语句默认不支持更新拆分键(实际4.x不支持更新带拆分键，5.x已经支持更新带拆分键不改的情况下)  
Unknown exception: [INSERT INTO …. ON DUPLICATE KEY UPDATE can not support
update for sharding column.]

### 8.3 针对以上俩种异常的解决方法

拆分键不能为空，设置默认拆分键  
更新带拆分键，升级sharding-proxy到5.x或配置同步DTS去掉拆分键更新

######  **作者：任洪波**

