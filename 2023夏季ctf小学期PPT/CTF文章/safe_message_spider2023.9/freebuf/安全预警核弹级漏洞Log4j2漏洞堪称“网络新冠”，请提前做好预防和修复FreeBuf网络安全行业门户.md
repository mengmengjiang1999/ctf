## **一.漏洞描述**

 **Apache Log4j2** 是一款开源的 Java 日志记录工具，该日志框架被大量用于业务系统开发，用来记录日志信息。此次漏洞是由于 Log4j2
在记录错误日志的过程中，并未对输入进行严格的判断，在打印错误日志的过程中会触发该漏洞。

##  **二. 受影响版本**

Apache Log4j 2.x <= 2.15.0-rc1

##  **三.** **部分使用该框架的组件**

Spring-Boot-strater-log4j2

Apache Struts2

Apache Solr

Apache Flink

Apache Druid

ElasticSearch

flume

dubbo

Redis

logstash

Kafka

###  **漏洞流量包**

![](https://image.3001.net/images/20211210/1639116560_61b2ef108f51a65c6c59d.png!small)

![](https://image.3001.net/images/20211210/1639116600_61b2ef380bf14a29a7f63.png!small)

##  **四. 检测规则**

![](https://image.3001.net/images/20211210/1639116647_61b2ef6714818cbdbe786.png!small)

##  **五. 修复方案**

1、官方发布rc1版本后发现可被绕过，紧急发布rc2修复此漏洞

[https://github.com/apache/logging-log4j2/releases/tag/log4j-2.15.0-rc2](https://link.zhihu.com/?target=https%3A//github.com/apache/logging-log4j2/releases/tag/log4j-2.15.0-rc2)

 **中新赛克星河企业安全管理中心云端已自动升级更新，同时支持对该漏洞进行全面检测，并已发布相关告警信息，后续也将对该漏洞信息持续更新报道。**

