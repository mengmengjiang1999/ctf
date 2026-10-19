## **浅谈** **RASP安全防御技术**

###  **RASP介绍**

RASP全称为Runtime application self-protection（运行时应用程序自我保护）。Gartner
在2014年应用安全报告里将RASP列为应用安全领域的关键趋势 ，并将其定义为:

“Applications should not be delegating most of their runtime protection to the
external devices. Applications should be capable of self- protection (i.e.,
have protection features built into the application runtime environment).”

（应用程序不应该依赖外部组件进行运行时保护，而应该具备自我保护的能力，也即建立应用运行时环境保护机制）

RASP在业界具体的应用是将RASP工具部署到中间件（Tomcat、weblogic等）中，在应用程序接收请求之前对请求进行过滤和分析，规避安全风险。应用程序无需进行任何的开发方面的修改，只需进行简单的配置即可。

###  **RASP解决的痛点：**

  *  ** **攻击技术层出不穷**** ：攻击者不断研究出攻击手段，生成恶意用户输入，绕过WAF。为了保障安全，WAF采取了发现可疑立刻阻止的策略，从而导致了比较多的误杀。
  *  ** **老系统维护问题**** ：有些企业的历史比较悠久，其使用的信息系统的上线时间也比较差。有很多时候并非没有发现问题，而是发现问题了无从下手，无法从代码层面整改。

###  **RASP能防护哪些漏洞？**

来自：https://www.imperva.com/resources/datasheets/RASP-Datasheet.pdf

以下为OpenRASP （OpenRASP 是百度安全推出的一款免费、开源的RASP产品）覆盖OWASP TOP 10 覆盖说明，且持续更新中。

![](https://image.3001.net/images/20210420/1618889851_607e4c7bead803c5a7042.png!small)

 ** **编号****

|

 ** **分类说明****

|

 ** **攻击类型****  
  
---|---|---  
  
A1

|

注入

|

SQL注入  
  
命令注入  
  
LDAP 注入  
  
NOSQL 注入  
  
XPATH 注入  
  
A2

|

失效的身份认证和会话管理

|

Cookie 篡改  
  
后台爆破  
  
A3

|

敏感数据泄露

|

敏感文件下载  
  
任意文件读取  
  
数据库慢查询  
  
文件目录列出  
  
A4

|

XML 外部实体（XXE）

|

XXE  
  
A5

|

失效的访问控制

|

任意文件上传  
  
CSRF  
  
SSRF  
  
文件包含  
  
A6

|

安全配置错误

|

打印敏感日志信息  
  
Struts OGNL 代码执行  
  
远程命令执行  
  
A7

|

跨站脚本（XSS）

|

反射型 XSS  
  
存储型 XSS  
  
A8

|

不安全的反序列化

|

反序列化用户输入  
  
A9

|

使用含有已知漏洞的组件

|

资产弱点识别  
  
A10

|

不足的日志记录和监控

|

WebShell 行为  
  
##  **RASP vs WAF 技术对比**

这里可以参考http://blog.nsfocus.net/rasp-tech/中的内容，网上的资料比较多了，这里不过多赘述。

##  **RASP的技术逻辑**

![](https://image.3001.net/images/20210420/1618889865_607e4c8967dc0af64094d.png!small)

来自：http://www.owasp.org.cn/OWASP_Events/1RASP.pdf

##  **RASP的技术优势**

 **RASP的核心技术优势可以概括为以下几点：**

  *  ** **部署和使用简单**** ：RASP只需进行简单的配置，即可与应用程序集成，应用程序无需进行任何的开发方面的修改；
  *  ** **检测误报率、漏报率低**** ：不同于 WAF的盲目的规则匹配，OpenRASP知道应用内部的关键函数，在这些关键函数执行之前添加安全检查，得到的参数都是经过变形还原后的、真实的请求数据。
  *  ** **极高的覆盖度和兼容性**** ： RASP 安全系统可以应用到任何可注入的应用程序，能处理绝大多数的网络协议：HTTP、 HTTPS、AJAX、SQL 与 SOAP。而 WAF 通过监控网络流量提供保护，因此只支持 Web 应用程序（HTTP）。此外，WAF 需要特定的解析器、协议分析工具或其他组件来分析应用程序使用的其他网络协议，这会导致一些兼容性与性能问题。

##  **RASP的核心不足**

 ** **性能影响****
：大多数RASP直接部署在系统中间件内，且实时检测和拦截风险，所以对CPU的性能有一定损耗，有可能会影响用户体验。据说OpenRASP最初版本CPU
性能损耗可达20%，目前已有所改善。对性能的影响可能是导致RASP现在还没有大范围使用的最大原因。

 **RASP的发展情况**  
简单整理了一些国内研究RASP技术的团队如下：

OpenRasp

（开源项目，隶属于百度OAESE智能终端安全生态联盟，起始于2017.8）

![](https://image.3001.net/images/20210420/1618889898_607e4caa0c1e24ab57905.png!small)

灵蜥:

（灵蜥应用系统攻击自免疫平台是一款新型WEB应用防护系统，基于RASP技术原理，与应用程序的运行环境和开发语言无缝结合并高度融合。通过修复应用自身内部缺陷，使应用自身具备攻击免疫能力，并以可视化的方式呈现攻击与防御情况。依托安百全网态势感知与漏洞情报下发防御策略，同时提供虚拟补丁进行“热修复”，使应用自身防御能力不断提升，可从容应对已知和未知风险，真正实现应用系统的动态与长期安全。）

![](https://image.3001.net/images/20210420/1618889910_607e4cb65378b142aeb8f.png!small)

云锁：

（云锁通过RASP技术对应用系统的流量、上下文、行为进行持续监控，识别及防御已知及未知威胁，能有效防御SQL注入、命令执行、文件上传、任意文件读写、反序列化、Struts2等基于传统签名方式无法有效防护的应用漏洞；）

![](https://image.3001.net/images/20210420/1618889921_607e4cc1df72c3da5d314.png!small)

  

