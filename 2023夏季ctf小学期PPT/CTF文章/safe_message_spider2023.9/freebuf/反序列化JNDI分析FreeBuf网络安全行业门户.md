## ****JNDI****

Java Naming and Directory
Interface，Java命名和目录接口，通过调用JNDI的API应用程序可以定位资源和其他程序对象，现在JNDI能访问的服务有：JDBC、LDAP、RMI、DNS、NIS、CORBA。

JNDI三种服务

##  ** **JNDI注入****

JNDI注入的关键是在用户进行远程方法调用时返回的stub是一个reference类型的对象，且用户本地CLASSPATH不存在该类字节码，导致用户需要加载reference类的字节码，直接返回恶意类字节码命令执行

  

##  ** **Naming Service命名服务：****

命名服务将名称和对象进行关联，提供通过名称找到对象的操作

##  ** **Directory Service 目录服务：****

目录服务是命名服务的扩展，除了提供名称和对象的关联，还允许对象具有属性。目录服务中的对象称之为目录对象。目录服务提供创建、添加、删除目录对象以及修改目录对象属性等操作。

 ** **Reference 引用：****

在一些命名服务系统中，系统并不是直接将对象存储在系统中，而是保持对象的引用。引用包含了如何访问实际对象的信息。

![1648434418_62411cf27ebcc8b1c53ac.png!small?1648434418886](https://image.3001.net/images/20220328/1648434418_62411cf27ebcc8b1c53ac.png!small?1648434418886)

##  ** **RMI绑定远程对象****

通过在注册中心上绑定一个恶意reference类对象，将恶意对象的字节码放在HTTP/FTP/SMB服务器上，需要客户端在加载reference类时在本地无法找到，通过codebase远程加载恶意类，在类实例化时触发payload

需要满足如下利用条件

安装并配置了SecurityManager

java.rmi.server.useCodebaseOnly=false，当useCodebasOnly为true时只允许加载信任codebase，不对未知codebase动态加载类，Java从7u21、6u45开始默认该属性为true

泛用性很低

Debug调试原理

##  ** **JNDI Reference****

当有客户端通过 ** **lookup("refObj")****
获取远程对象时，获取的是一个Reference存根（Stub),由于是Reference的存根，所以客户端会现在本地的classpath中去检查是否存在类refClassName，如果不存在则去指定的url(恶意类得http服务)，该引用对象(Reference)的加载与RMI
Class Loading的机制不同，因此可以绕过java.rmi.server.useCodebaseOnly的限制

利用条件

 ** **JDK 6u45**** ** **、**** ** **7u21**** ** **之后****
：java.rmi.server.useCodebaseOnly的默认值被设置为true。当该值为true时，将禁用自动加载远程类文件，仅从CLASSPATH和当前JVM的java.rmi.server.codebase指定路径加载类文件。使用这个属性来防止客户端JVM从其他Codebase地址上动态加载类，增加了RMI
ClassLoader的安全性。

 ** **JDK 6u141**** ** **、**** ** **7u131**** ** **、**** ** **8u121**** **
**之后：****
增加了com.sun.jndi.rmi.object.trustURLCodebase选项，默认为false，禁止RMI和CORBA协议使用远程codebase的选项，因此RMI和CORBA在以上的JDK版本上已经无法触发该漏洞，但依然可以
** **通过指定**** ** **URI**** ** **为**** ** **LDAP**** ** **协议来进行**** **
**JNDI**** ** **注入攻击**** 。

 ** **JDK 6u211**** ** **、**** ** **7u201**** ** **、**** ** **8u191**** **
**之后：****
增加了com.sun.jndi.ldap.object.trustURLCodebase选项，默认为false，禁止LDAP协议使用远程codebase的选项，把LDAP协议的攻击途径也给禁了。

其设置为false时限制了从远程Codebase加载Reference工厂类

创建Reference实例时几个比较关键的属性： new Reference("refClassName", "insClassName",
"http://example.com:8888/"); className：远程加载时所使用的类名；
classFactory：加载的class中需要实例化类的名称；
classFactoryLocation：远程加载类的地址，提供classes数据的地址可以是file/ftp/http等协议；

Reference对象没有实现Remote接口也不继承UnicastRemoteObject类，就不能绑定到注册中心上，需要用ReferenceWrapper这个包装类对其进行包装

首先调用initialContext.lookup方法

![1648434426_62411cfaa63b248a874e6.png!small?1648434427339](https://image.3001.net/images/20220328/1648434426_62411cfaa63b248a874e6.png!small?1648434427339)

调用getURLOrDefaultInitCtx()方法，使用getURLScheme方法获取协议名，getURLContext根据schema来获取对应协议的环境对象。这里返回rmiURLContext对象

![1648434436_62411d04dc68884ffe21b.png!small?1648434437590](https://image.3001.net/images/20220328/1648434436_62411d04dc68884ffe21b.png!small?1648434437590)

调用GenericURLContext的lookup方法，这里的this是指rmiURLContext。

调用对应协议类的getRootURLContext解析Rmi地址，不同的协议调用对应协议Con类的getRootURLContext，进入不同的协议路线

![1648434439_62411d0779ca9a6d49f61.png!small?1648434439821](https://image.3001.net/images/20220328/1648434439_62411d0779ca9a6d49f61.png!small?1648434439821)

  

public Object lookup(String var1) throws NamingException { // 获取rmi注册中心的相关数据
ResolveResult var2 = this.getRootURLContext(var1, this.myEnv); // 获取注册中心对象
Context var3 = (Context)var2.getResolvedObj(); Object var4; try { //
去注册中心lookup，进入此处 lookup var4 = var3.lookup(var2.getRemainingName()); } finally
{ var3.close(); } return var4;

var2中存储着rmi注册中心的属性

![1648434447_62411d0fc310a126b9a43.png!small?1648434448164](https://image.3001.net/images/20220328/1648434447_62411d0fc310a126b9a43.png!small?1648434448164)

var3是Registry_stub对象

![1648434458_62411d1a4dd04ad2090ea.png!small?1648434459320](https://image.3001.net/images/20220328/1648434458_62411d1a4dd04ad2090ea.png!small?1648434459320)

跟进lookup函数、此处调用的是RegistryContext.lookup()。registry时Registrytmpl_stub对象，this是RegistryContext对象。

其中从RMI注册表中lookup查询到服务端中目标类的Reference后返回一个ReferenceWrapper_Stub类实例，该类实例就是客户端的存根、用于实现和服务端进行交互，最后调用decodeObject()函数来解析

![1648434461_62411d1d15500bee44746.png!small?1648434461875](https://image.3001.net/images/20220328/1648434461_62411d1d15500bee44746.png!small?1648434461875)

跟进decodeObject函数。，先判断入参ReferenceWrapper_Stub类实例是否是RemoteReference接口实现类实例，而ReferenceWrapper_Stub类正是实现RemoteReference接口类的，因此通过判断调用getReference()来获取到ReferenceWrapper_Stub类实例中的Reference获取Reference(即我们在RMI注册绑定的Reference)

![1648434472_62411d284285694b60464.png!small?1648434472562](https://image.3001.net/images/20220328/1648434472_62411d284285694b60464.png!small?1648434472562)

然后调用 NamingManager.getObjectInstance函数、跟进

![1648434477_62411d2da7662adf52189.png!small?1648434478793](https://image.3001.net/images/20220328/1648434477_62411d2da7662adf52189.png!small?1648434478793)

继续跟进getObjectFactoryFromReference函数，使用loadclass加载类，就会向工厂请求恶意的class

![1648434482_62411d329b3cd2ba665be.png!small?1648434483062](https://image.3001.net/images/20220328/1648434482_62411d329b3cd2ba665be.png!small?1648434483062)

收到请求

![1648434486_62411d364f56742055fd0.png!small?1648434486719](https://image.3001.net/images/20220328/1648434486_62411d364f56742055fd0.png!small?1648434486719)

调用Newinstance触发构造函数，从而触发命令执行。调用栈如下

![1648434492_62411d3c0ce02bccdf370.png!small?1648434492559](https://image.3001.net/images/20220328/1648434492_62411d3c0ce02bccdf370.png!small?1648434492559)

## 参考文章

[https://blog.z3ratu1.cn/Java%20RMI%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E4%B8%8EJNDI%E6%B3%A8%E5%85%A5%E5%85%A5%E9%97%A8.html
](https://blog.z3ratu1.cn/Java%20RMI%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E4%B8%8EJNDI%E6%B3%A8%E5%85%A5%E5%85%A5%E9%97%A8.html)

[https://xz.aliyun.com/t/8214 ](https://xz.aliyun.com/t/8214)

[http://wjlshare.com/archives/1522﻿](http://wjlshare.com/archives/1522)

  

