![1617171054_6064126ec9f0e3e08aeaa.png!small?1617171055404](https://image.3001.net/images/20210331/1617171054_6064126ec9f0e3e08aeaa.png!small?1617171055404)

## Java安全检查引擎

Xcheck的java安全检查引擎支持 **Spring RequestMapping** 、 **JAX-RS** 、 **WebService** 和
**Java Servlet** 几种常用web接口的代码安全检查，目前内部误报率数据统计低于10%，扫描速度1w+行每秒。

覆盖漏洞类别包括但不限于以下：

  * 系统命令注入
  * 模板注入
  * 反序列化
  * 路径穿越漏洞
  * SQL注入
  * XML实体注入
  * XPATH注入![1617171092_60641294050da77127f2b.png!small?1617171093292](https://image.3001.net/images/20210331/1617171092_60641294050da77127f2b.png!small?1617171093292)

## OWASP Benchemark评测结果

OWASP benchmark是OWASP组织下的一个开源项目，又叫作OWASP基准测试项目，它是免费且开放的测试套件。可用来评估那些自动化安全扫描工具的
**速度、覆盖范围和准确性** 。

![1617171128_606412b84cc2f48777c29.png!small?1617171128678](https://image.3001.net/images/20210331/1617171128_606412b84cc2f48777c29.png!small?1617171128678)

从上图结果可以看出，对注入类漏洞（LDAPI、PATH Traversal、SQLI、XPATHI、CMDI） **Xcheck的召回率均达到了100%**
。

![1617171159_606412d76dbb1324ef080.png!small?1617171160269](https://image.3001.net/images/20210331/1617171159_606412d76dbb1324ef080.png!small?1617171160269)

从上图可以看出，对于基于benchmark评测，Xcheck的测试结果是与现有的某些商业化的代码检查工具的测试结果是不相上下的。

![1617171192_606412f830621da323732.png!small?1617171193528](https://image.3001.net/images/20210331/1617171192_606412f830621da323732.png!small?1617171193528)

## Apache Ambari任意代码执行漏洞：CVE-2014-3582 检测

在对内部项目的代码检查中，发现一个项目存在命令注入漏洞，经过查找，确认是已经披露出来的Apache
Ambari任意代码执行漏洞——CVE-2014-3582。

![1617171221_60641315b97a9007d1ea4.png!small?1617171222318](https://image.3001.net/images/20210331/1617171221_60641315b97a9007d1ea4.png!small?1617171222318)

漏洞分析如下：

    1. 污点引入，`java/org/apache/ambari/server/security/unsecured/rest/CertificateSign.java`，63行  
![1617171307_6064136b70a922a75ca63.png!small?1617171308032](https://image.3001.net/images/20210331/1617171307_6064136b70a922a75ca63.png!small?1617171308032)

    2. 跟进signAgentCrt函数，`java/org/apache/ambari/server/security/CertificateManager.java`，187行。在192行将污点传递给`agentHostname`，在239行`agentHostname`传递给`agentCrtName`，然后又到`scriptArgs`当中。![1617171363_606413a34f1999ffa3233.png!small?1617171363834](https://image.3001.net/images/20210331/1617171363_606413a34f1999ffa3233.png!small?1617171363834)![1617171386_606413ba748f2a2800e99.png!small?1617171386764](https://image.3001.net/images/20210331/1617171386_606413ba748f2a2800e99.png!small?1617171386764)  

    3. `java/org/apache/ambari/server/security/CertificateManager.java`，271行。调用`runCommand`函数，然后触发漏洞。![1617171428_606413e43f5cd2df5c688.png!small?1617171429190](https://image.3001.net/images/20210331/1617171428_606413e43f5cd2df5c688.png!small?1617171429190)整理数据流分析图如下：  
![1617171470_6064140e7a9431a2af275.png!small?1617171471009](https://image.3001.net/images/20210331/1617171470_6064140e7a9431a2af275.png!small?1617171471009)

## 4 最后

Xcheck作为国内新生的代码安全审计工具，面对这些早已名声在外的前辈，会时刻保持谦逊，不断进取向前。后续我们Xcheck团队也会持续披露Xcheck发现的一些有价值的漏洞或者分享代码安全审计相关技术。

专注于代码安全 | 公众号：腾讯代码安全检查Xcheck

  

