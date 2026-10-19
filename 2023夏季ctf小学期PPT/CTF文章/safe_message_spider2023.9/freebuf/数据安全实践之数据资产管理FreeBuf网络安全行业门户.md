## 前言

**在企业安全建设中，资产管理是很多安全工作的基础。而数据资产管理可以帮助我们更准确的发现安全风险，执行更有效的控制措施，在数据安全体系化建设中也有着举足轻重的作用。**

欢迎关注以往文章个人隐私保护系列：[《个人隐私保护之一：隐私政策解析》](https://www.freebuf.com/articles/database/219564.html)、[《APP隐私保护之二：用户端隐私保护实践（上）》](https://www.freebuf.com/articles/database/220083.html)、[《APP隐私保护之二：用户端隐私保护实践（下）》](https://www.freebuf.com/articles/database/220833.html)、
[《个人隐私保护之三：数据安全防护实践》](https://www.freebuf.com/articles/database/223045.html)

## 数据安全视角的数据资产

![](https://image.3001.net/images/20200115/1579057250_5e1e806202591.png!small)

## 整体架构与价值

数据资产管理主要分为三部分：数据采集，数据整合与识别，数据使用

![](https://image.3001.net/images/20200115/1579057357_5e1e80cd7d1ed.png!small)

> 数据调取，访问的权限管控，根据数据目录，数据负责人，建立管控流程
>
> 识别重要数据系统，接口，推进安全防护项目，包括数据加密，脱敏，认证，日志等改造
>
> 数据泄露事件的告警，溯源，审计，提供基础数据和综合分析平台

## 数据资产收集

数据一般在数据库，文件中静态存储，也通过应用，工具等方式进行流转。

### 1.数据类型和数据分布的收集

（1）全内网网络扫描识别数据库服务器IP、端口、服务类型

nmap -sP 获取存货主机

    
    
    nmap -sV -iL [nmaptest.txt]  数据库端口服务发现

（2）DBA或者运维申请数据库查询权限，如DBA有管理平台或相关数据，也可以直接对接收集数据

（3）获取数据结构和数据类型

获取库名：

    
    
    $SQL = 'show databases';

获取表明：  

    
    
    SELECT 
       table_name    获取表明
    FROM
     INFORMATION_SCHEMA.COLUMNS

获取表结构（字段，数据类型，注释）：  

    
    
    SELECT
      COLUMN_NAME 列名,
      COLUMN_TYPE 数据类型,
      DATA_TYPE 字段类型,
     CHARACTER_MAXIMUM_LENGTH 长度,
      IS_NULLABLE 是否为空,
      COLUMN_DEFAULT 默认值,
      COLUMN_COMMENT 备注
    FROM
     INFORMATION_SCHEMA.COLUMNS
    where
    -- db为数据库名称，到时候只需要修改成你要导出表结构的数据库即可
    -- table_schema ='db'

（4）数据样本信息获取

每个库表获取10-20条样本数据

`select * from [table] limit 0,20 `

获取20条样本，也可以根据需要调整阈值

### 2.数据所属应用，应用数据接口

应用一般从CMDB或公司的资产管理平台中获取，注意的是需要有一个唯一标识将应用和数据库进行关联。

应用数据接口可以通过网络流量分析获取流量中所有被访问接口URL。

提取URL和HOST加入资产列表

![](https://image.3001.net/images/20200115/1579069951_5e1eb1ff731b8.png!small)

Request判断是否是敏感请求

![](https://image.3001.net/images/20200115/1579069968_5e1eb210b7321.png!small)

Resbonse判断是否是敏感请求

![](https://image.3001.net/images/20200115/1579069987_5e1eb223dc944.png!small)

## 数据分级分类

等级划分一般企业为四级分发，L1-L4级。L1为***息，L2位秘密信息（或内部公开），L3为保密信息，L4为绝密信息。

针对不同的数据类型设定密级，根据公司情况信息密级可能不同：

> L4：如生物识别信息，密码，公司重大计划或战略数据等
>
> L3：如电话，住址，画像，个人喜好等
>
> L2：如姓名，国籍，日常统计数据等
>
> L1：昵称，公开评论，已发布公告等

数据资产管理中阈值数据分级分类字典，如：

数据标签 | 数据分类 | 数据分级  
---|---|---  
手机号 | 用户数据 | L3  
用户画像 | 用户数据 | L3  
员工工资 | 公司数据 | L3  
昵称 | 用户数据 | L0  
  
## 敏感数据识别

### 1.结构化数据敏感数据识别

基于关键字的敏感数据打标：通过字段名称，注释信息

基于正则的敏感数据打标：通过样本数据

基于机器学习的敏感数据打标：整个表中所有字段名，样本数据，与其他表的相似度进行训练

如对账号字段打标：

    
    
      var i= fieldName.toLowerCase().indexOf("user");
    
      var j = fieldName.toLowerCase().indexOf("id");
    
      var a = fieldDesc.indexOf("登录名");
    
      var b = fieldDesc.indexOf("用户名");
    
      var rexEmail =/[0-9a-zA-Z\_\.]{1,19}@[0-9a-zA-Z\_\.]{1,23}\.[com,cn,net,org,edu,gov,hk,tw]{1,3}/;
    
      var rexMobile = /((^1(3|8)\d{9})|(^(14(5|7|9)|17[0135678]|15[012356789]|19[89]|16[6])\d{8}))$/;
    
      return ((rexEmail.test(fieldValue) || rexMobile.test(fieldValue)) && (i != -1 ||j != -1))||(a!= -1 ||b != -1);

### 2.敏感数据接口识别

从流量中获取数据包对[response](https://fanyi.sogou.com/?keyword=response&fr=websearch_submit&from=en&to=zh-CHS)的body内容进行数据解析：

通过正则提取是否含有批量敏感数据，如匹配***，手机号等。

通过格式化body内容，并匹配关键字可以进一步提升识别率和检出率。

如果匹配到敏感数据，提升准确率可适当调证匹配个数阈值，提取request中的url加入敏感数据接口，并获取域名，数据类型，统计访问量等信息。

### 3.文件等数据

采用DLP产品对文件进行识别和审计

文件系统，邮件系统，办公终端，移动终端等。

## 数据资产应用场景

### 场景一：敏感数据接口监控和日志审计

> 监控非授权访问，过度权限，高频获取数据
>
> 建立人员行为画像，对行为进行风险评分

### 场景二：数据访问权限申请

> 线上系统/应用间数据调取的权限控制
>
> 人员从应用内，DB，大数据平台访问/导出数据的权限控制

### 场景三：数据泄露事件溯源

> 人员行为画像，系统数据画像分析数据源
>
> 数据接口的访问日志/流量溯源
>
> 通过数据资产分布溯源

 ***本文原创作者：Alkaid13 ，本文属于FreeBuf原创奖励计划，未经许可禁止转载**

