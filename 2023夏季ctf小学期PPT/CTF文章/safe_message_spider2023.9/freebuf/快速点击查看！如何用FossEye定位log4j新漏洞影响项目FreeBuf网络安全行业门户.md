## 快速定位log4j新漏洞影响的项目

 **第一步** ：将FossEye知识库更新至最新版本

 **第二步** ：【项目管理】全量扫描代码仓库

![图片](https://image.3001.net/images/20211210/1639121344_61b301c029e550b5e6a8a.png!small)

 **第三步** 【资产管理-漏洞】根据漏洞id搜索“CVE-2021-44228”，点击查看影响项目数

![](https://image.3001.net/images/20211210/1639121363_61b301d3d0a13d1fa584e.png!small)

 **第四步** 溯源页面显示出该漏洞影响的所有项目，点击放大镜图标可查看代码具体位置

![](https://image.3001.net/images/20211210/1639121380_61b301e4c3cd1278e4274.png!small)![](https://image.3001.net/images/20211210/1639121408_61b302007cd5855acd09a.png!small)

  

  

## 漏洞详情

###  **漏洞概述**

此次Apache Log4j2 漏洞是用于 Log4j2 提供的 lookup
功能造成的，该功能允许开发者通过一些协议去读取相应环境中的配置。但在实现的过程中，并未对输入进行严格的判断，从而造成漏洞的发生。恶意攻击者可以利用该漏洞注入恶意class文件从而执行任意命令。

###  **漏洞编号**

CVE-2021-44228

###  **漏洞危险等级：** 严重

###  **影响版本**

Apache Log4j <=2.15.0-rc1

可能的受影响应用包括但不限于如下：

  * Spring-Boot-strater-log4j2

  * Apache Struts2

  * Apache Solr

  * Apache Flink

  * Apache Druid

  * ElasticSearch

  * flume

  * dubbo

  * Redis

  * logstash

  * kafka

###  **
**漏洞复现****![](https://image.3001.net/images/20211210/1639121992_61b304484abd5ffb31482.png!small)

![](https://image.3001.net/images/20211210/1639122009_61b30459858763c7a604b.png!small)

###  ** **漏洞分析****

![](https://image.3001.net/images/20211210/1639122035_61b30473f099eba8ea049.png!small)

  

略去一些非关键流程，日志信息最终会进入MessagePatternConverter.java 文件的format方法，如下图， ** **当日志信息中出现
"${"关键字 则通过StrSubstitutor.java的replace方法对其进行替换和解析****

![](https://image.3001.net/images/20211210/1639122071_61b304978d756f098de89.png!small)

  

最终通过StrSubstitutor.java文件中的substitute方法对传入的日志信息进行替换。这个函数主要作用就是提取出日志信息中的${}信息，并根据内容调用。varName就是提取出来的关键信息，最关键的位置如下：

![](https://image.3001.net/images/20211210/1639122091_61b304ab35af30afffe7d.png!small)

![](https://image.3001.net/images/20211210/1639122102_61b304b6b8c27e6dfdd82.png!small)

  

在lookup中，prefix是对应配置类，name是其参数并通过调用对应方法进行解析。

  
![](https://image.3001.net/images/20211210/1639122118_61b304c64936e3ea15a3f.png!small)

lookup保存有如下解析类：

![](https://image.3001.net/images/20211210/1639122177_61b30501c6bc9000b6b38.png!small)

  

最终在JndiLookup.java中触发漏洞

![](https://image.3001.net/images/20211210/1639122187_61b3050b03357b6de769e.png!small)

  

堆栈：

lookup:172, JndiManager (org.apache.logging.log4j.core.net)  
lookup:56, JndiLookup (org.apache.logging.log4j.core.lookup)  
lookup:184, Interpolator (org.apache.logging.log4j.core.lookup)  
resolveVariable:1054, StrSubstitutor (org.apache.logging.log4j.core.lookup)  
substitute:976, StrSubstitutor (org.apache.logging.log4j.core.lookup)  
substitute:872, StrSubstitutor (org.apache.logging.log4j.core.lookup)  
replace:427, StrSubstitutor (org.apache.logging.log4j.core.lookup)  
format:132, MessagePatternConverter (org.apache.logging.log4j.core.pattern)  
format:38, PatternFormatter (org.apache.logging.log4j.core.pattern)  
toSerializable:334, PatternLayout$PatternSerializer
(org.apache.logging.log4j.core.layout)  
toText:233, PatternLayout (org.apache.logging.log4j.core.layout)  
encode:218, PatternLayout (org.apache.logging.log4j.core.layout)  
encode:58, PatternLayout (org.apache.logging.log4j.core.layout)  
directEncodeEvent:177, AbstractOutputStreamAppender
(org.apache.logging.log4j.core.appender)  
tryAppend:170, AbstractOutputStreamAppender
(org.apache.logging.log4j.core.appender)  
append:161, AbstractOutputStreamAppender
(org.apache.logging.log4j.core.appender)  
tryCallAppender:156, AppenderControl (org.apache.logging.log4j.core.config)  
callAppender0:129, AppenderControl (org.apache.logging.log4j.core.config)  
callAppenderPreventRecursion:120, AppenderControl
(org.apache.logging.log4j.core.config)  
callAppender:84, AppenderControl (org.apache.logging.log4j.core.config)  
callAppenders:448, LoggerConfig (org.apache.logging.log4j.core.config)  
processLogEvent:433, LoggerConfig (org.apache.logging.log4j.core.config)  
log:417, LoggerConfig (org.apache.logging.log4j.core.config)  
log:403, LoggerConfig (org.apache.logging.log4j.core.config)  
log:49, DefaultReliabilityStrategy (org.apache.logging.log4j.core.config)  
logMessage:146, Logger (org.apache.logging.log4j.core)  
log:2117, AbstractLogger (org.apache.logging.log4j.spi)  
tryLogMessage:2205, AbstractLogger (org.apache.logging.log4j.spi)  
logMessageTrackRecursion:2159, AbstractLogger (org.apache.logging.log4j.spi)  
logMessageSafely:2142, AbstractLogger (org.apache.logging.log4j.spi)  
logMessage:2017, AbstractLogger (org.apache.logging.log4j.spi)  
logIfEnabled:1983, AbstractLogger (org.apache.logging.log4j.spi)  
error:740, AbstractLogger (org.apache.logging.log4j.spi)  
main:14, log4j (com.z)

###  **修复建议**

官方修复链接如下：

https://github.com/apache/logging-log4j2/releases/tag/log4j-2.15.0-rc2

临时解决方案（三选一）：

（1） 修改jvm参数 -Dlog4j2.formatMsgNoLookups=true

（2） 修改配置log4j2.formatMsgNoLookups=True

（3） 将系统环境变量 FORMAT_MESSAGES_PATTERN_DISABLE_LOOKUPS 设置为 true

###  **参考链接**

https://nvd.nist.gov/vuln/detail/CVE-2021-44228  
https://github.com/apache/logging-log4j2/pull/608  
https://github.com/tangxiaofeng7/apache-log4j-poc  
https://logging.apache.org/log4j/2.x/changes-report.html#a2.15.0  
https://logging.apache.org/log4j/2.x/manual/lookups.html#JndiLookup  
https://github.com/advisories/GHSA-jfh8-c2jp-5v3q

