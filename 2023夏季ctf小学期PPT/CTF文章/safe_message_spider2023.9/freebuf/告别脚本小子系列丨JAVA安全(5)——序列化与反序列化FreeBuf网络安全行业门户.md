![](https://image.3001.net/images/20220425/1650878456_626667f870d416b5c4389.jpg!small)

## **前言**

告别脚本小子系列是本公众号的一个集代码审计、安全研究和漏洞复现的专题，意在帮助大家更深入的理解漏洞原理和掌握漏洞挖掘的思路和技巧。系列课程包含多篇文章，往期内容如下：

 **往期内容回顾**

1

[告别脚本小子系列丨JAVA安全(1)——JAVA本地调试和远程调试技巧](https://mp.weixin.qq.com/s?__biz=MzkzNjMxNDM0Mg==&mid=2247483768&idx=1&sn=36ff6d279fa7dbd7d5ae00b06a3c3ddc&chksm=c2a1d5f1f5d65ce701e1f73ce0f584412bfc38a507622758f2acabce370cdcc4bb4af2270045&token=134012946&lang=zh_CN&scene=21#wechat_redirect)

2

[告别脚本小子系列丨JAVA安全(2)——JAVA反编译技巧](https://mp.weixin.qq.com/s?__biz=MzkzNjMxNDM0Mg==&mid=2247483803&idx=1&sn=1af141cd5623b2682cfbdc2c12a53309&chksm=c2a1d512f5d65c04bc046ee83de4ba98881d086837f05cef581b39323026195b504bb5635c4c&token=134012946&lang=zh_CN&scene=21#wechat_redirect)

3

[告别脚本小子系列丨JAVA安全(3)——JAVA反射机制](https://mp.weixin.qq.com/s?__biz=MzkzNjMxNDM0Mg==&mid=2247483830&idx=1&sn=39c08c61cbab36ace4ac691e0756948b&chksm=c2a1d53ff5d65c29f9b8310c324c67568fe27e61720baffff8af19ef9cb94f5096d73df0c69f&token=134012946&lang=zh_CN&scene=21#wechat_redirect)

4

[告别脚本小子系列丨JAVA安全(4)——ClassLoader机制与冰蝎Webshell分析](https://mp.weixin.qq.com/s?__biz=MzkzNjMxNDM0Mg==&mid=2247483971&idx=1&sn=13bc478b9bad8c40279f4a2b22c7e29e&chksm=c2a1d6caf5d65fdc4c76043ba0650ca947722c69bfd4bca69a4ef35d3fb318b5cf26fa557c6d&token=134012946&lang=zh_CN&scene=21#wechat_redirect)

  

##  **0x01 概述**

反序列化漏洞是java安全中最常见的漏洞之一，学习反序列化漏洞的相关知识有助于帮我们掌握更多关于java安全系统性内容。序列化是指把内存中的对象转化为字节序列，主要用于在不同程序之间传递和存储对象。而反序列化是指把字节序列重新转化为对象。例如，weblogic通过t3协议来和其他java程序之间传输数据，数据传输的方式就是通过序列化和反序列化来实现的，这也是导致weblogic经常爆出反序列化漏洞的根本原因。

##  **0x02 序列化详解**

首先来看java中最典型的序列化和反序列化的一段代码如下。我把相关代码的解释都放在注释里面，方便大家查看。

>
>     import java.io.*;class User implements Serializable{private String
> name;public User(String name) {this.name = name;}//
> 方便打印查看类的信息@Overridepublic String toString() {return "User{name=" + name +
> '}';}}public class Demo1 {public static void main(String[] args) throws
> Exception {User user = new User("zhangsan");String filename =
> "user.ser";serialize(filename, user); // 把对象序列化保存到文件User user1 = (User)
> unserialize(filename); // 从文件反序列化对象System.out.println(user1);}//
> 序列化对象并保存到文件public static void serialize(String filename, Object obj) throws
> Exception{// 创建一个FIleOutputStreamFileOutputStream fos = new
> FileOutputStream(filename);//
> 将这个FIleOutputStream封装到ObjectOutputStream中ObjectOutputStream os = new
> ObjectOutputStream(fos);//
> 调用writeObject方法，序列化对象到文件user.ser中os.writeObject(obj);}// 从文件反序列化对象public
> static Object unserialize(String filename) throws Exception{//
>  创建一个FIleInutputStreamFileInputStream fis = new FileInputStream(filename);//
> 将FileInputStream封装到ObjectInputStream中ObjectInputStream oi = new
> ObjectInputStream(fis);//
> 调用readObject从user.ser中反序列化出对象，还需要进行一下类型转换，默认是Object类型return
> oi.readObject();}}

上述代码定义了一个User类用于测试序列化和反序列化的过程。首先并不是所有的类都是可以进行序列化和反序列化的，要进行序列化和反序列化则该类必须继承自java.io.Serializable接口（该类的全部属性也必须继承自Serializable接口）。否则会抛出NotSerializableException报错，如图2.1所示。

![](https://image.3001.net/images/20220425/1650876204_62665f2c06460c6378de4.png!small)

图2.1 如果不继承Serializable接口则会抛出异常

序列化和反序列化的过程都是基于字节流来完成的。序列化是通过writeObject方法来把类对象转换为字符输出流，上述demo则是把User对象转化为文件字符输出流并保存成文件；反序列化是通过readObject方法来把字符输入转化为类对象，上述demo则是通过读取文件内容转化为User对象。在序列化和反序列化的过程中有两点需要注意：

1） 类对象序列化之后不一定要保存成文件，也可以通过ByteArrayOutputStream保存为字节数组。

2） 反序列化之后返回的数据类型为Object类型，如果要转化为序列化之前的类，需要进行强制类型转化。

运行上面的Demo代码，会在当前项目根目录生成序列化之后保存的文件user.ser文件，通过xxd可以查看文件的16进制编码，如图2.2所示。目前大部分的序列化之后的数据格式都是aced
0005，其中aced代表序列化协议，0005代表序列化协议版本。这个可以作为判断字符流是序列化数据的依据。![](https://image.3001.net/images/20220425/1650876235_62665f4be4d56b2452c96.png!small)

图2.2 查看序列化数据的16进制格式

一般来说，序列化之后的数据是不允许修改的，但是可以允许在不改变字符长度的情况下对属性值进行替换。如图2.3所示，可以把“zhangsan”替换为“lisi
”，用空格来补齐字符个数。![](https://image.3001.net/images/20220425/1650876274_62665f72850c1d0006ab6.png!small)

图2.3 对序列化之后的字符进行字符替换

##  **0x03 反序列化漏洞**

反序列化漏洞是指在反序列化过程中自动执行类中readObject方法导致的漏洞，类似于PHP反序列化时会自动执行__wakeup方法一样。为了更清晰的认识反序列化漏洞的原因，我们把上面的代码稍微改一下，如图3.1所示。![](https://image.3001.net/images/20220425/1650878201_626666f946637c7f43f10.png!small)

图3.1 在反序列化的类中增加readObject方法

通过上面的代码可以看出，如果readObject中执行了某种危险的操作，就可能到做反序列化漏洞，如图3.2所示。![](https://image.3001.net/images/20220425/1650878229_6266671573a8cf6bdeb67.png!small)

图3.2 通过反序列化执行恶意操作

当然在实际环境中不可能有这么简单的情况，这里只是阐述一些原理性的东西。真实的环境下一定是一种利用链的调用关系，我们现在只是简单描述一下关于反序列化利用链，真实的利用链将在后续的课程中进行详述。反序列化利用链是一种链式调用逻辑，如图3.3所示。![](https://image.3001.net/images/20220425/1650878255_6266672f3336b00ff0b96.png!small)

图3.3 反序列化调用链原理

反序列化调用链从本质来说就是构造一条从反序列化入口Source到危险方法Sink的调用链。反序列化的Source点一定是从readObject方法开始，但是Sink点却可以有很多种不同的类型。最常见的反序列化Sink是命令执行，但是也有可能是文件上传、SSRF、XXE等其他类型的Sink。

##  **0x04 JAVA与PHP反序列化对比**

相信大多数小伙伴都是从PHP开始接触代码，作为曾经世界上最好的语言，有必要来和我们当前世界上最好的语言来进行对比，看看两者反序列化过程中的差异。  
 **1） 反序列化的数据存储格式**  
JAVA序列化之后的数据是满足特定序列化协议的字符流，PHP序列化之后是一种类似json的格式。JAVA序列化之后的数据是不可读的，PHP序列化之后的数据是可读的。如图4.1所示。![](https://image.3001.net/images/20220425/1650878293_62666755e1f845cd47615.png!small)

图4.1 PHP和JAVA序列化数据格式对比

不同语言对于序列化有不同的实现方式，同一种语言也有多种不同的序列化方式。相对于JAVA而言，PHP的序列化可读性更强，序列化之后的数据可以按照字段含义进行直接修改。  
 **2） 反序列化触发点不同**  
从上面的关于JAVA反序列化的分析中可以看出，JAVA反序列化的入口点Source是readObject方法。而PHP与JAVA不同，PHP反序列化的入口点Source是__wakeup和__destruct方法。  
说到PHP反序列化的触发点，就不得不提PHP的魔术方法。PHP的魔术方法是指以（__）开头的函数方法，通常是在某种条件下自动触发执行的方法。在反序列化的过程中常用的魔术方法如表4.1所示。表4.1
PHP反序列化过程中常用魔术方法

 **方法名**|  **方法介绍**  
---|---  
__wakeup| 在调用unsearialize()时，自动执行该方法。属于反序列化Source之一。  
__destruct| 析构函数，在到某个对象的所有引用都被删除或者当对象被显式销毁时执行。属于反序列化Source之一。  
__toString| 一个类被当成字符串时自动调用该方法。属于反序列化利用链中常见魔术方法之一。  
__call| 在对象中调用不可访问的方法时触发，即当调用对象中不存在的方法会自动调用该方法。属于反序列化利用链中常见魔术方法之一。  
__set| 给不可访问的属性赋值时自动调用该方法。属于特定场景下反序列化利用链会用到的方法。  
__get| 读取不可访问属性的值时自动调用该方法。属于特定场景下反序列化利用链会用到的方法。  
__invoket| 当尝试以调用函数的方式调用一个对象时自动调用该方法。属于特定场景下反序列化利用链会用到的方法。  
  
因为PHP魔术方法的存在，为反序列化利用链的构造增加很多思路，可以通过特定魔术方法拓宽反序列化利用链。与PHP不同的是，JAVA并没有严格意义上的魔术方法，但是其实JAVA里面有一些类似的方法，如表4.2所示。  
表4.2 JAVA中经常会被自动调用的方法

 **方法名**|  **方法介绍**  
---|---  
readObject| 在反序列化的过程中会自动调用改方法，属于反序列化的入口Source。  
toString| 把对象当成字符串来操作是会自动调用该方法。  
hashCode| 返回该对象的hash值，集合类操作时会调用此方法。  
equals| 对象进行比较、排序、查找时可能可能调用此方法。  
finalize| 当垃圾回收器确定不存在对该对象的更多引用时，由对象的垃圾回收器调用此方法。  
  
JAVA没有魔术方法，只有一些经常会使用到的方法。JAVA在构造反序列化利用链时比PHP更加灵活，因为JDK代码大多数情况下还是JAVA编写的，可以方便的通过调试技巧来确定不同类方法之间的相互调用。  
 **3） 类加载机制不同**  
在PHP中要调用某个类必须要引入，PHP引入类文件常见的是这四种方式require、require_once、inclue、include_once。在反序列化的过程中，反序列化利用链中的每一个类也都必须是显式引入的，即必须通过上面四个函数中的某一个引入对应的类文件。如果不引入，就会报错，如图4.2所示。![](https://image.3001.net/images/20220425/1650878381_626667ad2fed4932dcb2a.png!small)

图4.2 PHP反序列化之前必须显式引入

  
与PHP的类加载机制不同，JAVA中类加载只与classpath有关，只要是在classpath中的类就能被直接调用。JAVA中并不要求在调用类之前进行显式引入，一般来说项目jar包中的类都可以任意调用。  
我想这应该是JAVA出现的反序列化漏洞要远远多于PHP反序列化漏洞的原因之一。  
 **4） 应用场景不同**  
PHP一般用于中小型项目，项目一般比较简单，代码较少。传统PHP项目是直接编写代码，现在的PHP项目会采用一些主流的PHP框架。但是PHP项目中很少使用其他第三方的组件（其实现在已经慢慢开始流行使用composer来加载第三方组件了）。JAVA一般用于大型项目，项目结构和功能复杂，代码较多。JAVA项目中一般会引入大量第三方jar包，而第三方jar包通常是反序列化利用链的重要组成部分。

##  **0x05 结论**

JAVA反序列化是经典的JAVA漏洞，上面的文章分析的都是JDK中最常见的序列化和反序列化方式。但是JAVA中还有其他的序列化和反序列化方式，包括：基于Externalizable接口的序列化和反序列化、基于fastjson的序列化与反序列化、基于XStream的序列化与反序列化、基于jackson的序列化与反序列化等。每一种序列化与反序列化都可能出现对应的反序列化漏洞，而这也是研究反序列化漏洞的重要组成部分。后续我们的课程也会持续更新这部分的内容，感兴趣的小伙伴可以点一个关注。  
  
[原文链接﻿](https://mp.weixin.qq.com/s?__biz=MzkzNjMxNDM0Mg==&mid=2247484384&idx=1&sn=675a280b04097ab115a98b623ffc9957&chksm=c2a1d769f5d65e7ff06adba1117ee14d1d772baedcd822302c5827b77fd6177a55f1c6add46b&token=134012946&lang=zh_CN#rd)

