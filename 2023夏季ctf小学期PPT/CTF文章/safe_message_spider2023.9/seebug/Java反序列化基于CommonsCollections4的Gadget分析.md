**作者：welkin@京东安全  
公众号：[京东安全](https://mp.weixin.qq.com/s/vq4_L8UCEEW9NDSSrnRcSA "京东安全")**

本文主要分为两方面，其一是基于PriorityQueue类的序列化对象的构造，另一方面是PriorityQueue对象在反序列化过程中恶意代码的触发原理。

### 背景及概要

随着Java应用的推广和普及，Java安全问题越来越被人们重视，纵观近些年来的Java安全漏洞，反序列化漏洞占了很大的比例。就影响程度来说，反序列化漏洞的总体影响也明显高于其他类别的漏洞。

在反序列化漏洞的利用过程中，攻击者会构造一系列的调用链以完成其攻击行为。如何高效的生成符合条件且可以稳定利用的攻击Payload成为了攻击链条中的重要一环，当前已经有很多现成的工具帮助我们完成Payload的生成工作。本文主要以Ysoserial工具为例分析了基于org.apache.commons.collections4类库的Gadget，其通过构造一个特殊的PriorityQueue对象，将其序列化成字节流后，在字节流反序列化的过程中触发代码执行。

更多关于Ysoserial的信息，请参考：

<https://github.com/frohoff/ysoserial>

本文主要分为两方面，其一是基于PriorityQueue类的序列化对象的构造，另一方面是PriorityQueue对象在反序列化过程中恶意代码的触发原理。下文将从这两方面展开描述一些细节以及实际测试时的一些问题，整体的流程如图1-1所示。

![img](https://images.seebug.org/content/images/2019/01/08/1546931212000-0073pZerly4fyubnq3udpj30oa05s0sz.jpg-w331s)

图1-1

### 序列化对象的构造

首先，被序列化为字节流的对象实际是一个特殊的PriorityQueue对象，本小节主要分析构造该对象的过程，即图1-1的第一步。

图2-1为`ysoserial.payloads.CommonsCollections4`中getObject方法的代码，是用于构造该PriorityQueue对象的代码：

![img](https://images.seebug.org/content/images/2019/01/08/1546931212000-0073pZerly4fyubnq0j4jj30oz0hrmym.jpg-w331s)

图2-1

上图中需要注意的有如下两点：

  1. 通过createTemplatesImpl方法生成templates对象

  2. 通过PriorityQueue类的比较器将构造的一系列transformer串联起来

#### 0x0A createTemplatesImpl方法生成攻击载荷

通过createTemplatesImpl方法生成templates对象是非常重要的一部分，因为这是实际承载我们恶意代码的对象，详细说一下，跟进分析createTemplatesImpl方法，其代码具体实现和关键点流程分别如下图2-2和图2-3所示：

![img](https://images.seebug.org/content/images/2019/01/08/1546931212000-0073pZerly4fyubnq3r0pj30oa0hlq50.jpg-w331s)

图2-2

![img](https://images.seebug.org/content/images/2019/01/08/1546931212000-0073pZerly4fyubnq3so4j30oa0pmgnb.jpg-w331s)

图2-3

首先生成TemplatesImpl实例，然后通过javassist类库修改StubTransletPayload类字节码，在其中插入执行命令的代码（这里是通过`java.lang.Runtime.getRuntime().exec()`方法执行命令，也可以插入其他利用代码，如反弹shell等），然后将其父类设置为abstTranslet类，最后将修改后的字节码通过反射写入到TemplatesImpl实例的_bytecodes变量中，这里还同时写入了Foo.class的字节码。除此之外，为了后续恶意代码的触发（如作者注释中所写：required
to make TemplatesImpl
happy），还要修改TemplatesImpl实例的`_name`和`_tfactory`变量，否则后面会在命令代码执行前抛出异常。
StubTransletPayload类代码实现如图2-4所示：

![img](https://images.seebug.org/content/images/2019/01/08/1546931212000-0073pZerly4fyubnq0k57j30oa06lwey.jpg-w331s)

图2-4

StubTransletPayload类继承自AbstractTranslet类并实现了Serializable接口，通常我们构造一个恶意类可能会直接在static代码块或构造方法中写入我们想要执行的代码，这一步在上面通过javassist类库实现，关于StubTransletPayload类需要继承AbstractTranslet类的原因会在反序列化恶意代码触发时解释。
以上即为createTemplatesImpl方法的实现，其本质上是构造了一个特定结构的TemplatesImpl类实例，具体变量的值如图2-5所示：

![img](https://images.seebug.org/content/images/2019/01/08/1546931212000-0073pZerly4fyubnq476wj30oa0b4t9h.jpg-w331s)

图2-5

#### 构造并串联transformer

回到图2-1本段开始处getObject方法的代码中，在35行和40行分别初始化了ConstantTransformer对象和InstantiateTransformer对象，47行将两个对象构造成Transformer数组作为参数初始化了ChainedTransformer对象chain。

而在50行，这个ChainedTransformer对象chain又是我们要序列化的对象PriorityQueue中comparator构造方法的参数，comparator可以理解为在PriorityQueue中决定优先次序的比较器，此处用的是TransformingComparator对象。

在44-45行、55-57行利用java的反射机制和引用传递的特性修改chain对象中的变量，ConstantTransformer对象中iConstant变量的值设为`com.sun.org.apache.xalan.internal.xsltc.trax.TrAXFilter.class`，InstantiateTransformer对象中iParamTypes设为javax.xml.transform.Templates.class，iArgs设为此前构造的templates对象。

51、52行向队列中插入两个1，这里是为了后面堆化时触发一次堆排序。
最终构造了一个用TransformingComparator对象作比较器的PriorityQueue对象，其内存中变量示意图和抽象结构图分别如图2-6和图2-7所示：

![img](https://images.seebug.org/content/images/2019/01/08/1546931212000-0073pZerly4fyubnq0jfpj30oa09d3zj.jpg-w331s)

图2-6

![img](https://images.seebug.org/content/images/2019/01/08/1546931212000-0073pZerly4fyubnq0nxkj30j30elgmb.jpg-w331s)

图2-7

接下来将分析下这个对象序列化后的字节序列如何在反序列化的过程中触发代码执行。

#### 0x3 反序列化过程中恶意代码的触发原理

反序列化开始至触发代码执行的整体流程如图3-1所示：

![img](https://images.seebug.org/content/images/2019/01/08/1546931213000-0073pZerly4fyubnq2klfj30hz0uwdhn.jpg-w331s)

图3-1

反序列化过程中首先进入ObjectInputStream类的readObject方法中，然后进入readObject0方法中读取字节流，其中会读取tc标记，然后根据tc标记的类型进入不同的逻辑处理函数中，标记类型可见图3-2：

![img](https://images.seebug.org/content/images/2019/01/08/1546931213000-0073pZerly4fyubnq0iwpj30oa0o6myo.jpg-w331s)

图3-2

反序列化的是PriorityQueue对象，这里会进入TC_OBJECT的处理逻辑中，跟进到readOrdinaryObject方法里，其具体代码如图3-3，在1769行读取类描述信息，1780行通过类描述信息，初始化对象obj（即PriorityQueue对象）：

![img](https://images.seebug.org/content/images/2019/01/08/1546931213000-0073pZerly4fyubnq32xsj30oa0haabf.jpg-w331s)

图3-3

在图3-4中1793行判断是否实现Externalizable接口，通过Externalizable接口可以通过调用对象的readExternal方法实现自定义地完全控制某一对象及其超类的流格式和内容，这里代码进入默认的readSerialData方法中。

![img](https://images.seebug.org/content/images/2019/01/08/1546931213000-0073pZerly4fyubnq3qu7j30oa02waan.jpg-w331s)

图3-4

在图3-5中1882行判断序列化对象是否有readObject方法，如果有则通过反射调用对象的readObject方法为成员变量赋值，接下来就进入了PriorityQueue对象的readObject方法中。

![img](https://images.seebug.org/content/images/2019/01/08/1546931213000-0073pZerly4fyubnq3lj9j30oa0az0tq.jpg-w331s)

图3-5

图3-6为PriorityQueue对象的readObject方法：

![img](https://images.seebug.org/content/images/2019/01/08/1546931213000-0073pZerly4fyubnq3j8nj30oa0dhjs8.jpg-w331s)

图3-6

图3-7中在defaultReadObject方法中会调用defaultReadFields方法为成员变量赋值：

![img](https://images.seebug.org/content/images/2019/01/08/1546931213000-0073pZerly4fyubnq0471j30oa083aar.jpg-w331s)

图3-7

defaultReadFields方法中1989行会递归调用readObject0方法为对象的成员变量赋值直至完成，逻辑与前面描述相似，此处不再赘述。

![img](https://images.seebug.org/content/images/2019/01/08/1546931213000-0073pZerly4fyubnq075xj30oa0goq4p.jpg-w331s)

图3-8

defaultReadObject方法执行完成后，代码流程回到PriorityQueue对象的readObject方法（图3-6）中，读取被transient修饰的Object数组queue（此前被赋值为两个int型的数值1），这部分可以和PriorityQueue类的writeObject方法对照着看（图3-9）。

![img](https://images.seebug.org/content/images/2019/01/08/1546931213000-0073pZerly4fyubnq324hj30oa0a00tb.jpg-w331s)

图3-9

然后代码流程进入图3-6中173行的heapify方法，PriorityQueue本质上是一个最小堆，通过siftDown方法进行次序的调整实现堆化，之前往PriorityQueue对象中插入两个1，可以使队列的SIZE满足for循环的条件从而进入siftDown方法中。

![img](https://images.seebug.org/content/images/2019/01/08/1546931214000-0073pZerly4fyubnq4dyaj30oa03gwf1.jpg-w331s)

继续跟进siftDown方法，次序的调整必然涉及比较，在这儿此前精心构造的比较器就派上用场了，跟进siftDownUsingComparator方法，在图3-11中699行调用了比较器的compare方法。

![img](https://images.seebug.org/content/images/2019/01/08/1546931214000-0073pZerly4fyubnq1ab0j30oa06bdg5.jpg-w331s)

![img](https://images.seebug.org/content/images/2019/01/08/1546931214000-0073pZerly4fyubnq0ynrj30oa0dh3zc.jpg-w331s)

图3-11

跟进compare方法，在比较前会先通过transformer的transform方法转换一下对象。而此处的transformer正是我们此前构造的ChainedTransformer对象chain序列化成字节流后又反序列化所得（在递归调用readObject0方法时实现），如图3-12所示。

![img](https://images.seebug.org/content/images/2019/01/08/1546931214000-0073pZerly4fyubnq3klvj30oa048mxk.jpg-w331s)

![img](https://images.seebug.org/content/images/2019/01/08/1546931214000-0073pZerly4fyubnq3f7kj30oa0gywg0.jpg-w331s)

图3-12

继续跟进到ChainedTransformer的transform方法中，此时iTransformers中有ConstantTransformer对象和InstantiateTransformer对象，此处代码逻辑是将ConstantTransformer对象中transform方法的返回值作为参数传入InstantiateTransformer对象的transform方法中。

![img](https://images.seebug.org/content/images/2019/01/08/1546931214000-0073pZerly4fyubnpzpzdj30oa046dg0.jpg-w331s)

图3-13

ConstantTransformer对象中transform方法的返回iConstant变量，即com.sun.org.apache.xalan.internal.xsltc.trax.TrAXFilter.class:

![img](https://images.seebug.org/content/images/2019/01/08/1546931214000-0073pZerly4fyubnq18x1j30oa03emxm.jpg-w331s)

图3-14

InstantiateTransformer对象中transform方法反射获取构造方法后生成了TrAXFilter类的实例，通过newInstance方法进入了TrAXFilter类含参构造方法TrAXFilter(Templates
templates)中，并将TemplatesImpl实例作为参数传入，如图3-15所示。

![img](https://images.seebug.org/content/images/2019/01/08/1546931214000-0073pZerly4fyubnq6ayuj30oa03xjrq.jpg-w331s)

图3-15

TrAXFilter(Templates
templates)方法代码如图3-16所示，在64行调用了TemplatesImpl对象的newTransformer方法，newTransformer方法中又调用getTransletInstance方法（图3-17中410行），恶意代码的触发便是在该方法中。

![img](https://images.seebug.org/content/images/2019/01/08/1546931214000-0073pZerly4fyubnq4lhuj30oa051jrv.jpg-w331s)

图3-16

![img](https://images.seebug.org/content/images/2019/01/08/1546931214000-0073pZerly4fyubnq0txtj30oa0cuq3u.jpg-w331s)

图3-17

如图3-18所示，getTransletInstance方法中第376行调用了defineTransletClasses方法后，380行会将_class数组中的某个类实例化：

![img](https://images.seebug.org/content/images/2019/01/08/1546931214000-0073pZerly4fyubnq4ixdj30oa0hp75v.jpg-w331s)

图3-18

跟进defineTransletClasses方法发现有如图3-19所示这样一段代码：

![img](https://images.seebug.org/content/images/2019/01/08/1546931214000-0073pZerly4fyubnq4xw6j30oa0o8myz.jpg-w331s)

图3-19

其在for循环里遍历_bytecodes数组并通过TransletClassLoader加载字节码，其中会判断_class[i]的父类是否为`ABSTRACT_TRANSLET（”com.sun.org.apache.xalan.internal.xsltc.runtime.AbstractTranslet”）`，这解释了为什么_bytecodes中的StubTransletPayload类要继承自AbstractTranslet类，_transletIndex变量初始化时为-1，若此处判断条件为false，`_transletIndex`的值仍为-1，则程序执行流程会进入后面`if
(_transletIndex <
0)`的代码块中抛出异常。构造StubTransletPayload类为AbstractTranslet类的子类即可把恶意类的索引值i赋值给`_transletIndex`。defineTransletClasses方法执行完成后，跳回到getTransletInstance方法中，将`_class[_transletIndex]`（即StubTransletPayload类）实例化触发我们之前通过javassist类库插入的代码块，实现代码执行（图3-20）。

![img](https://images.seebug.org/content/images/2019/01/08/1546931215000-0073pZerly4fyubnq5s9pj30oa0cbt9s.jpg-w331s)

图3-20

到这儿基本上整个Gadget的触发流程就走完了。此处通过调用TemplatesImpl对象的newTransformer方法去间接的调用getTransletInstance方法实现代码执行。除此之外，TemplatesImpl类中的getOutputProperties方法又调用了newTransformer，例如fastjson的反序列化中基于TemplatesImpl类的Gadget便是通过getOutputProperties方法去触发代码执行。
理论上只要构造特定的TemplatesImpl类对象，然后调用其getTransletInstance方法就可以实现代码执行。为方便理解，我写了一个简单的Demo，通过反射正向构造了一个TemplatesImpl对象并调用其getTransletInstance方法来触发代码执行，代码如下：

![img](https://images.seebug.org/content/images/2019/01/08/1546931215000-0073pZerly4fyubnq5cwuj30fe0cxmyh.jpg-w331s)

evil.java代码如下:

![img](https://images.seebug.org/content/images/2019/01/08/1546931215000-0073pZerly4fyubnq5ej0j30fa0bkdgd.jpg-w331s)

### 关于类的加载中静态代码的执行

在demo中是通过插入静态代码块的方式注入恶意代码，我看到后面defineClass对类的加载时一度以为这样的实现类似于fastjson中基于`com.sun.org.apache.bcel.internal.util.ClassLoader`类实现的POC（具体可参考文章DefineClass在Java反序列化当中的利用），在类加载的过程中实现的static代码块执行，但后来调试时发现`static{}`中插入的恶意代码仍然是在类实例化（即调用`newInstance()`）时触发。
关于类加载的过程，在《深入理解Java虚拟机》中虚拟机类加载机制一节中有详细的说明，类加载可分为加载、验证、准备、解析和初始化这五个阶段。其中我们关心的static代码块的执行是在初始化阶段，初始化阶段实际是执行类构造器`<clinit>()`的过程，`<clinit>()`是在Javac编译过程中生成字节码时被添加到语法树中。

`<clinit>()`方法是编译器自动收集类中的所有类变量的赋值动作和静态语句块中的语句合并产生。——《深入理解Java虚拟机》

书中还提到虚拟机规范严格规定了有且只有四种情况必须立即对类进行初始化：

  * 遇到new、getstatic、putstatic、invokestatic这四条字节码指令时，如果类还没有进行过初始化，则需要先触发其初始化。生成这四条指令最常见的Java代码场景是：使用new关键字实例化对象时、读取或设置一个类的静态字段（static）时（被static修饰又被final修饰的，已在编译期把结果放入常量池的静态字段除外）、以及调用一个类的静态方法时。

  * 使用Java.lang.refect包的方法对类进行反射调用时，如果类还没有进行过初始化，则需要先触发其初始化。

  * 当初始化一个类的时候，如果发现其父类还没有进行初始化，则需要先触发其父类的初始化。

  * 当虚拟机启动时，用户需要指定一个要执行的主类，虚拟机会先执行该主类。

前面在通过TransletClassLoader中的defineClass方法加载类时仅将字节码装载到了JVM中，没有执行类的初始化，而fastjson的Poc中通过Class.forName()加载类时，Class.forName()方法除了将对应的类装载到JVM中，还会执行类构造器`<clinit>()`对类进行初始化，从而执行static代码块。Class.forName()代码实现（JDK1.7）见图4-1：

![img](https://images.seebug.org/content/images/2019/01/08/1546931215000-0073pZerly4fyubnq3x6wj30oa0870tg.jpg-w331s)

![img](https://images.seebug.org/content/images/2019/01/08/1546931215000-0073pZerly4fyubnq2kbzj30oa0d0aay.jpg-w331s)

图4-1

forName0()方法用native关键字修饰，说明这个方法是原生函数，非Java语言实现。可从forName()方法的注释中看到第二个参数决定类是否会被初始化，在forName(String
className)中默认为true。以上基本解释了我在关于注入的静态代码触发位置的疑惑。

### 总结

整个Gadget的调用栈见图5-1：

![img](https://images.seebug.org/content/images/2019/01/08/1546931215000-0073pZerly4fyubnq67jzj30oa0qdjup.jpg-w331s)

图5-1

反序列化时首先从ObjectInputStream类的readObject方法中进入到PriorityQueue类的readObject方法里，其readObject方法中会进行堆化，堆化时队列中元素大于等于2时会进行堆排序，这时会调用自定义的比较器（`TransformingComparator`），`TransformingComparator`在比较次序时会将对象进行转换。转换时使用的transformer是基于ConstantTransformer对象和`InstantiateTransformer`对象构造的ChainedTransformer对象，ChainedTransformer对象在其转换方法（`transform()`）中会依次调用`ConstantTransformer`对象和`InstantiateTransformer`对象的transform方法，并将前一个对象transform方法的返回值作为参数传入后一个对象的transform方法中，`InstantiateTransformer`对象中的transform方法会基于参数（这里即`ConstantTransformer.transform()`的返回值`com.sun.org.apache.xalan.internal.xsltc.trax.TrAXFilter`）新建实例，则进入了TrAXFilter类的构造方法中，这里调用了TransformerImpl实例的newTransformer方法，又调用了getTransletInstance方法，加载`_bytecodes`中修改后的StubTransletPayload类字节码并生成实例，从而触发代码执行。

### 参考

<https://github.com/frohoff/ysoserial>

<https://stackoverflow.com/questions/39504847/why-does-class-not-invoke-the-static-block-in-a-class>

<https://www.freebuf.com/articles/others-articles/167932.html>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/786/>

