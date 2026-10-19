## **项目介绍**

Apache Flume
是一个分布式的，可靠的，并且可用于高效地收集，汇总和移动大量日志数据的软件。它具有基于流数据流的简单而灵活的体系结构。它具有可调的可靠性机制以及许多故障转移和恢复机制，并且具有健壮性和容错性。它使用一个简单的可扩展数据模型，该模型允许进行在线分析应用程序。

##  **漏洞描述**

在7月22日，Apache发布安全公告，修复了一个存在于Apache
Flume中的远程代码执行漏洞，CVE编号为CVE-2022-34916。当攻击者控制目标 LDAP 服务器时，如果配置使用带有 JNDI LDAP 数据源
URI 的 JMS 源，Apache Flume 版本 1.4.0 到 1.10.0 很容易受到远程代码执行 (RCE) 攻击。

##  **利用范围**

1.4.0 <= Apache Flume <= 1.10.0

##  **漏洞分析**

###  **环境搭建**

从GitHub上下载1.10.0版本，导入IDEA。

项目jdk使用1.8，然后修改TestIntegrationActiveMQ
测试类中的DESTINATION_NAME，因为destinationName是由DESTINATION_NAME
定义；修改JNDI_PREFIX为ldap://

![](https://image.3001.net/images/20220922/1663827601_632bfe9199b2a0225d8c1.png!small)在JMSMessageConsumerTestBase.java中将destinationLocator
= JMSDestinationLocator.CDI;修改为destinationLocator =
JMSDestinationLocator.JNDI;

![](https://image.3001.net/images/20220922/1663827626_632bfeaa3ef65265f5858.png!small)

最后运行TestIntegrationActiveMQ 测试类即可。

###  **漏洞原理**

根据Apache Flume漏洞描述，可以确定问题是出现在了JMSMessageConsumer中。

![](https://image.3001.net/images/20220922/1663827694_632bfeeeebc7e9658f8f8.png!small)查看DIff（https://github.com/apache/flume/commit/7fe9af49）记录发现，修复方式是在JMSMessageConsumer中的else分支下，在initialContext.lookup(destinationName)前新增了对destinationName的校验。

![](https://image.3001.net/images/20220922/1663827717_632bff0528dd711797cde.png!small)

那么漏洞触发点已经很明确了，在没有增加校验前，只要进入JMSMessageConsumer中else分支，控制destinationName参数，即可实现JNDI注入。

###  **代码分析**

知道了漏洞原理后，分析一下代码。

首先在TestJMSMessageConsumer#testCreateDurableSubscription 初始化了
JMSMessageConsumer 并传入 destinationLocator

![](https://image.3001.net/images/20220922/1663827797_632bff558ec3400f7b49a.png!small)destinationLocator的定义是在JMSMessageConsumerTestBase.java中。

![](https://image.3001.net/images/20220922/1663827812_632bff64d24e4d39eb2c5.png!small)在搭建环境时，我们是将destinationLocator
= JMSDestinationLocator.CDI；修改为了destinationLocator =
JMSDestinationLocator.JNDI；

![](https://image.3001.net/images/20220922/1663827984_632c001049b188e5e6b95.png!small)

这样配置，是为了在JMSMessageConsumer中不满足if条件后，能够进入到else，到达漏洞触发点。

而在官方提供的测试类中，TestIntegrationActiveMQ 类存在
testQueueLocatedWithJndi，将作为source点传入参数。

![](https://image.3001.net/images/20220922/1663828007_632c00279e92e9cc9e723.png!small)修改DESTINATION_NAME为恶意JNDI地址，将JNDI_PREFIX修改为ldap://

![](https://image.3001.net/images/20220922/1663828022_632c00369baace2e5af36.png!small)通过参数的传入，经过如上分析的流程，到达else后，由于没有校验，直接触发initialContext.lookup，造成JNDI注入，从而执行恶意远程代码。

##  **漏洞复现**

![](https://image.3001.net/images/20220922/1663828060_632c005cc9cd65685e919.png!small)

##  **修复建议**

官方已发布安全版本，请尽快更新至安全版本，下载链接：https://flume.apache.org/download.html

##  **参考材料**

1.https://github.com/apache/flume/commit/7fe9af49

2.https://issues.apache.org/jira/browse/FLUME-3428

