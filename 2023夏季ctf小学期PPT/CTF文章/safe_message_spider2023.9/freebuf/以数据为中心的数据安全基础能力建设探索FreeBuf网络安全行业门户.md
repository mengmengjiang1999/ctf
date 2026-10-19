企业数据安全治理，除了熟悉法律法规条文，信息采集最小化，服务入口明确隐私协议外，更多的是需要建设内部基础能力，如数据识别、分类分级、数据加密、权限管控等数据安全的基础能力。

本文数据为中心的理念，围绕数据识别、分类分级、基础防护几个方面，结合开源软件做一次梳理和功能演示，希望能帮助有需要的人员对数据安全有个直观的了解。

在数据识别基础上，建立数据资产大盘，实现数据资产风险识别、监测、运营的资产全生命周期管理；

在数据分类分级的基础上，对不同数据资产进行分类、分级，将优势资源投入到关键资产的安全防护上；

在数据安全基础防护方面，除了应具有基础设施和架构的安全稳固外，基于数据识别和分类分级，对存储、传输的敏感数据进行加密防护、账号权限管控、数据脱敏和分发管控，结合内外部风险变化，最终走向数据安全风控之路。

## 1、数据识别、分类

在大数据时代的今天，如何做好数据识别、分类，在这个基础上建立数据资产全生命周期管理是很多企业面临的挑战。比如企业内部有多少数据库表明文存储手机号字段、有多少接口对外暴露且有手机号字段，这些数据库表、接口等资产又面临哪些风险，如何做到全生命周期的风险管控。针对结构化数据，如数据库表中字段识别、半结构化数据，如日志中的数据识别、非结构化如图片、音视频文件的数据识别，在识别能力的覆盖范围、识别准确率、对性能的影响等方面，这对很多企业还是有不小的挑战。

### 1.1. 内容识别示例

数据识别可以通过关键字、正则、算法等实现，网上文章很多，以及一些大厂也有成熟的识别技术和方案，从落地实现上主要还是基于业务场景，从数据类型上看主要分为结构化、半结构化、非结构化的数据识别。

结构化：关系型数据库

半结构化：日志数据、JSON数据、XML文档等

非结构化：HTML网页、办公文档、图片、音视频文件等

![](https://image.3001.net/images/20220225/1645791870_6218ca7e14e958b41582e.png!small)

### 1.2. 分类分级管理展示

![](https://image.3001.net/images/20220225/1645790512_6218c530637dc65ac3d79.png!small)

## 2、利用ShardingSphere-Proxy实现敏感数据加密

ShardingSphere是apache顶级开源项目，旨在构建异构数据库上层的标准和生态。它关
注如何充分合理地利用数据库的计算和存储能力，而并非实现一个全新的数据库。ShardingSphere 站在
数据库的上层视角，关注他们之间的协作多于数据库自身。

连接、增量和可插拔是 Apache ShardingSphere 的核心概念。

  * 连接:通过对数据库协议、SQL方言以及数据库存储的灵活适配，快速的连接应用与多模式的异构数据库;
  * 增量:获取数据库的访问流量，并提供流量重定向(数据分片、读写分离、影子库)、流量变形(数据加密、数据脱敏)、流量鉴权(安全、审计、权限)、流量治理(熔断、限流)以及流量分析(服 务质量分析、可观察性)等透明化增量功能;
  * 可插拔:项目采用微内核+三层可插拔模型，使内核、功能组件以及生态对接完全能够灵活的方式 进行插拔式扩展，开发者能够像使用积木一样定制属于自己的独特系统。

ShardingSphere-Proxy定位为透明化的数据库代理端，提供封装了数据库二进制协议的服务端版本，用于完成对异构语言的支 持。目前提供 MySQL
和 PostgreSQL

![](https://image.3001.net/images/20220225/1645790916_6218c6c444ef8ace80114.png!small)

安装

下载ShardingSphere‐Proxy 的最新发行版。解压缩后修改conf/server.yaml和以config-前缀开头的文件，如:conf/config-encrypt.yaml 文件，进行字段加密配置，其他配置如分片规则、读写分离规则配置暂不讨论。Linux
操作系统运行 bin/start.sh，可以指定proxy端口，bin/start.sh 3308.

敏感字段配置

![](https://image.3001.net/images/20220225/1645791543_6218c9373e9efc909b9e9.png!small)

    
    
    (base) gengdeMacBook-Pro:conf js2thon$ mysql -h127.0.0.1 -uroot -P3308
    Welcome to the MySQL monitor.  Commands end with ; or \g.
    Your MySQL connection id is 13
    Server version: 8.0.20-Sharding-Proxy 4.1.0
    Copyright (c) 2000, 2020, Oracle and/or its affiliates. All rights reserved.
    Oracle is a registered trademark of Oracle Corporation and/or its
    affiliates. Other names may be trademarks of their respective
    owners.
    Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.
    mysql> show tables;
    +----------------------+------------+
    | Tables_in_encrypt_db | Table_type |
    +----------------------+------------+
    | t_encrypt            | BASE TABLE |
    +----------------------+------------+
    1 row in set (0.03 sec)
    mysql> select * from t_encrypt;
    +----------+---------+-------------+
    | order_id | user_id | phone       |
    +----------+---------+-------------+
    |       10 |       0 | 18516014911 |
    |       11 |       1 | 18516014922 |
    |       12 |       2 | 18516014933 |
    |       13 |       3 | 18516014944 |
    |       14 |       4 | 18516014955 |
    +----------+---------+-------------+
    5 rows in set (0.09 sec)
    mysql> select * from t_encrypt;
    +----------+---------+--------------------------+-------------+
    | order_id | user_id | phone_cipher             | phone       |
    +----------+---------+--------------------------+-------------+
    |       10 |       0 | uFZ1RGQfxsUM+GUJqI5rlQ== | 18516014911 |
    |       11 |       1 | SGxnMaUHY/HR50hJcYp6Vg== | 18516014922 |
    |       12 |       2 | Z5NBefdS9WN3Bl6p45R1Dw== | 18516014933 |
    |       13 |       3 | SKqYOUF4dxloUH5M9t/wEg== | NULL        |
    |       14 |       4 | 4q+dOa+bxUTFSzX6AOjvUg== | NULL        |
    +----------+---------+--------------------------+-------------+

## 3、利用Vault实现数据库动态凭证和数据加解密的接口调用

Hashicorp
Vault解决了管理敏感信息的问题，如数据库凭证和API密钥就是需要以安全的方式存储和提供给应用程序的敏感数据，Vault支持许多secret引擎，部分如下：

> Key-Value： 简单的静态键值对
>
> 动态生成的凭据：由Vault根据客户端请求生成
>
> 加密密钥：用于使用客户端数据执行加密功能

###
3.1.数据库动态凭证![](https://image.3001.net/images/20220226/1645842106_62198ebaa63294a839d12.png!small)

Vault安装配置较为简单，这里主要列下相关配置信息：

 **数据库链接配置**

![](https://image.3001.net/images/20220225/1645791632_6218c9902ff66208e93a5.png!small)

 **角色配置**

![](https://image.3001.net/images/20220225/1645791672_6218c9b8da8a830e280e0.png!small)

 **获取数据库凭证**

![](https://image.3001.net/images/20220226/1645843718_62199506a3c8e5d542b2c.png!small)

 **使用动态凭证登录验证**

    
    
    (base) js2thondeMacBook-Pro:Downloads js2thon$ mysql -u v-my-r-owFmZ3LFu -pM8DdaYZXYRU-rNIm2CbQ
    mysql: [Warning] Using a password on the command line interface can be insecure.
    Welcome to the MySQL monitor.  Commands end with ; or \g.
    Your MySQL connection id is 1379
    Server version: 5.6.41-log MySQL Community Server (GPL)
    Copyright (c) 2000, 2020, Oracle and/or its affiliates. All rights reserved.
    Oracle is a registered trademark of Oracle Corporation and/or its
    affiliates. Other names may be trademarks of their respective
    owners.
    Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.
    mysql>

上面在Vault配置了用户只有SELECT权限，验证可以正常查询

    
    
    mysql> use mysql_test;
    Reading table information for completion of table and column names
    You can turn off this feature to get a quicker startup with -A
    Database changed
    mysql> show tables;
    +----------------------+
    | Tables_in_mysql_test |
    +----------------------+
    | account              |
    +----------------------+
    mysql> select * from account;
    +------+------+
    | id   | name |
    +------+------+
    |  100 | abc  |
    +------+------+
    1 row in set (0.00 sec)

执行数据插入操作，因为没有权限Vault报错。

    
    
    mysql> insert into account values(101,'def');
    ERROR 1142 (42000): INSERT command denied to user 'v-my-r-owFmZ3LFu'@'localhost' for table 'account'

### 3.2.数据加解密接口调用

Vault作为kms提供加解密接口，通过调用接口实现数据加解密，Vault数据密钥的创建可参考官网文档，此处忽略。

![](https://image.3001.net/images/20220226/1645864706_6219e702d4cfcc409871e.png!small)

 **Vault管理后台密钥创建**

![](https://image.3001.net/images/20220226/1645865077_6219e8756b3d4847a5411.png!small)

 **加解密接口调用Python实现**

![](https://image.3001.net/images/20220226/1645865121_6219e8a142ead0e720b09.png!small)

## 4、问题和思考

本文从数据识别、分类分级、配置管理、存储字段加密这个流程梳理下来，其实需要横向和纵向扩展的还非常多，统一密钥管理、账号权限、资产大盘、风险监测和运营管理，这些组成了数据安全的基础能力。上面也只是罗列了一些开源工具的能力，只是做了单点的简单功能演示，没有详细进一步去了解实现机制和优劣势，后续有精力再做深一步的研究，也希望有落地实现的同行交流实际经验，如在架构方案设计、异构适配、性能稳定性等方面的多维度实践探索。

