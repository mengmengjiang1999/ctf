## 写在前面

继前面三种常见的Tomcat的内存马构造方式，后面将会讲解更加独特的Tomcat内存马构造，这是内存马系列文章第四篇，主要讲解Tomcat的架构，为后面Tomcat组件内存马做铺垫（不是在容器中实现的内存马，可以一定程度避免查杀）。

## 前置

### 顶层架构

我们可以通过一张图来表示。

![image-20220912111100201.png](https://image.3001.net/images/20220917/1663399365_632575c5e237b4dfce3bd.png!small)

架构足够模块化，从图中我们可以知道最上层为Server服务器，为Service服务提供一个生存环境，掌握每个Service服务的生命周期，至于Service则是嘴歪提供服务。

而在每隔Service中有着多个Connector和一个Container，他们的作用分别是Connector:负责接收浏览器的TCP连接请求，提供Socket与Request、Response的相关转化，与请求端交换数据，Container:用于封装和管理Servlet，以及具体处理Request请求，是所有子容器的父接口（包括Engine、Host、Context、Wrapper）。

  * `Engine`\-- 引擎

  * `Host`\-- 主机

  * `Context`\-- 上下文

  * `Wrapper`\-- 包装器

Service服务之下还有各种`支撑组件`，下面简单罗列一下这些组件。

  * `Manager`\-- 管理器，用于管理会话Session

  * `Logger`\-- 日志器，用于管理日志

  * `Loader`\-- 加载器，和类加载有关，只会开放给Context所使用

  * `Pipeline`\-- 管道组件，配合Valve实现过滤器功能

  * `Valve`\-- 阀门组件，配合Pipeline实现过滤器功能

  * `Realm`\-- 认证授权组件

同样可以在tomcat的server.xml中看到一些配置。

    
    
    <?xml version="1.0" encoding="UTF-8"?>
    <Server port="8005" shutdown="SHUTDOWN">
      <Listener className="org.apache.catalina.startup.VersionLoggerListener" />
      <!-- Security listener. Documentation at /docs/config/listeners.html
      <Listener className="org.apache.catalina.security.SecurityListener" />
      -->
      <!-- APR library loader. Documentation at /docs/apr.html -->
      <Listener className="org.apache.catalina.core.AprLifecycleListener" SSLEngine="on" />
      <!-- Prevent memory leaks due to use of particular java/javax APIs-->
      <Listener className="org.apache.catalina.core.JreMemoryLeakPreventionListener" />
      <Listener className="org.apache.catalina.mbeans.GlobalResourcesLifecycleListener" />
      <Listener className="org.apache.catalina.core.ThreadLocalLeakPreventionListener" />
    
      <GlobalNamingResources>
        <Resource name="UserDatabase" auth="Container"
                  type="org.apache.catalina.UserDatabase"
                  description="User database that can be updated and saved"
                  factory="org.apache.catalina.users.MemoryUserDatabaseFactory"
                  pathname="conf/tomcat-users.xml" />
      </GlobalNamingResources>
    
      <Service name="Catalina">
    
        <Connector port="8080" protocol="HTTP/1.1"
                   connectionTimeout="20000"
                   redirectPort="8443" />
    
        <Engine name="Catalina" defaultHost="localhost">
          <Realm className="org.apache.catalina.realm.LockOutRealm">
            <Realm className="org.apache.catalina.realm.UserDatabaseRealm"
                   resourceName="UserDatabase"/>
          </Realm>
    
          <Host name="localhost"  appBase="webapps"
                unpackWARs="true" autoDeploy="true">
            <Valve className="org.apache.catalina.valves.AccessLogValve" directory="logs"
                   prefix="localhost_access_log" suffix=".txt"
                   pattern="%h %l %u %t "%r" %s %b" />
    
          </Host>
        </Engine>
      </Service>
    </Server>
    
    

我们可以知道开放的端口，第一部分就是tomcat默认的监听器，第二部分就是资源，第三部分就是一些Service服务，上面的这个xml文件只配置了一个Connector，提供了HTTP/1.1的连接支持，但是Tomcat是支持多个Connector配置的，比如：

![image-20220912112444755.png](https://image.3001.net/images/20220917/1663399380_632575d410de8bb030e0e.png!small)

存在多个配置

之后还存在一些Engine等等结构，当然除了这些还有着负责jsp页面解析、jsp属性验证，同时也负责将jsp页面动态转换为java代码并编译为class文件的Jasper组件，提供命名服务的Naming组件，提供Session服务的Session组件，负责日志记录的Logging组件，提供JVM监控服务的JMX组件。

### 生命周期

整个Tomcat的生命周期以观察者模式为基础

Subject 抽象主题：负责管理所有观察者的引用，同时定义主要的事件操作，而Tomcat核心类LifeCycle就是这个抽象主题。

ConcretSubject 具体主题：实现抽象主题定义的所有接口，发生变化通知观察者，如StandardServer

Observer 观察者：监听主题变化的操作接口，LifeCycleListener为这个抽象观察者

我们可以来看看`Lifecycle`的方法。

![image-20220912130435959.png](https://image.3001.net/images/20220917/1663399388_632575dc1da8845a3efa5.png!small)

定义了许多的方法，分别为添加监听器，获取监听器，删除监听器或者是初始化，启动方法和停止消毁相关的方法。

![image-20220912130651024.png](https://image.3001.net/images/20220917/1663399395_632575e342c35b460608e.png!small)

存在有一个对`LifecycleBase`类对`Lifecycle`进行了实现，对各个方法进行了重写，我们来看看其中的几个方法。

`init()`

![image-20220912130936284.png](https://image.3001.net/images/20220917/1663399401_632575e9b0ba65dedd334.png!small)

这里判断了state只有为NEW的时候才会进行初始化，首先将其状态设置为`INITIALIZING`，之后调用`initInternal`进行初始化操作，在初始化完成之后设置状态，如果在过程中出现错误，将会抛出异常

值得注意的是`initInternal`方法是一个抽象方法，需要各个组件进行重写，其他的方法也就不详细写了，师傅们可以跟一下。

从上述源码看得出来，`LifecycleBase`是使用了状态机+模板模式来实现的。模板方法有下面这几个：

    
    
    // 初始化方法
    protected abstract void initInternal() throws LifecycleException;
    // 启动方法
    protected abstract void startInternal() throws LifecycleException;
    // 停止方法
    protected abstract void stopInternal() throws LifecycleException;
    // 销毁方法
    protected abstract void destroyInternal() throws LifecycleException;
    

### Tomcat类加载机制

Java默认的类加载机制是通过`双亲委派模型`来实现的。而Tomcat实现的方式又和`双亲委派模型`有所区别。原因在于一个Tomcat容器允许同时运行多个Web程序，每个Web程序依赖的类又必须是相互隔离的。因此，如果Tomcat使用`双亲委派模式`来加载类的话，将导致Web程序依赖的类变为共享的。对于双亲委派模型的机制我们是非常熟悉的了，也不过多的讲解了。

贴个图

![image-20220912132620354.png](https://image.3001.net/images/20220917/1663399411_632575f3adce9ce43f350.png!small)

大概就是这样个一类加载顺序，同样存在有另一中缺陷，如果在程序中使用了第三方实现类，如果使用双亲委派模型，那么第三方实现类也需要放在Java核心类里面才可以，不然的话第三方实现类将不能被加载使用，但是在`java.lang.Thread`类中存在有两个方法能够获取到上下文类加载器。

![image-20220912132854431.png](https://image.3001.net/images/20220917/1663399418_632575fa69cc156e5343c.png!small)

我们可以通过在SPI类里面调用`getContextClassLoader`来获取第三方实现类的类加载器。由第三方实现类通过调用`setContextClassLoader`来传入自己实现的类加载器。

接下来来看看Tomcat独有的类加载机制模型。

我们可以从[官方文档](https://tomcat.apache.org/tomcat-8.5-doc/class-loader-howto.html)找到说明

![image-20220912133108953.png](https://image.3001.net/images/20220917/1663399425_63257601a0fa7ef674b5f.png!small)

这个类加载器结构图和之前的双亲委派机制的架构图有着很大的区别。

每个类加载器的作用如下Common类加载器，负责加载Tomcat和Web应用都复用的类

Catalina类加载器，负责加载Tomcat专用的类，而这些被加载的类在Web应用中将不可见

Shared类加载器，负责加载Tomcat下所有的Web应用程序都复用的类，而这些被加载的类在Tomcat中将不可见。

WebApp类加载器，负责加载具体的某个Web应用程序所使用到的类，而这些被加载的类在Tomcat和其他的Web应用程序都将不可见。

Jsp类加载器，每个jsp页面一个类加载器，不同的jsp页面有不同的类加载器，方便实现jsp页面的热插拔

直接来分析一下Tomcat启动所调用的流程。

如果在`org.apache.catalina.startup.Bootstrap`类中，来看一下类中存在的方法

![image-20220912133705986.png](https://image.3001.net/images/20220917/1663399433_632576093d4fcd0587235.png!small)

其中存在main方法，在启动tomcat的同时将会调用这个方法，但是在这个类最后面存在一个静态代码块将会首先执行。

    
    
    从环境变量中获取catalina.home，在没有获取到的时候将执行后面的获取操作
    在第一步没获取的时候，从bootstrap.jar所在目录的上一级目录获取
    第二步中的bootstrap.jar可能不存在，这时我们直接把user.dir作为我们的home目录
    重新设置catalinaHome属性
    接下来获取CATALINA_BASE（从系统变量中获取），若不存在，则将CATALINA_BASE保持和CATALINA_HOME相同
    重新设置catalinaBase属性
    

而在main方法中，main方法大体分成两块，一块为init，另一块为load+start，我们可以来看看init中的的代码。

    
    
    public void init() throws Exception {
        // 非常关键的地方，初始化类加载器s，后面我们会详细具体地分析这个方法
        initClassLoaders();
    
        // 设置上下文类加载器为catalinaLoader，这个类加载器负责加载Tomcat专用的类
        Thread.currentThread().setContextClassLoader(catalinaLoader);
        SecurityClassLoad.securityClassLoad(catalinaLoader);
    
        // 使用catalinaLoader加载我们的Catalina类
        // Load our startup class and call its process() method
        if (log.isDebugEnabled())
            log.debug("Loading startup class");
        Class<?> startupClass = catalinaLoader.loadClass("org.apache.catalina.startup.Catalina");
        Object startupInstance = startupClass.getConstructor().newInstance();
    
        // 设置Catalina类的parentClassLoader属性为sharedLoader
        // Set the shared extensions class loader
        if (log.isDebugEnabled())
            log.debug("Setting startup class properties");
        String methodName = "setParentClassLoader";
        Class<?> paramTypes[] = new Class[1];
        paramTypes[0] = Class.forName("java.lang.ClassLoader");
        Object paramValues[] = new Object[1];
        paramValues[0] = sharedLoader;
        Method method =
            startupInstance.getClass().getMethod(methodName, paramTypes);
        method.invoke(startupInstance, paramValues);
    
        // catalina守护对象为刚才使用catalinaLoader加载类、并初始化出来的Catalina对象
        catalinaDaemon = startupInstance;
    }
    

跟进一下`initClassLoaders`。

    
    
    private void initClassLoaders() {
        try {
            // 创建commonLoader，如果未创建成果的话，则使用应用程序类加载器作为commonLoader
            commonLoader = createClassLoader("common", null);
            if( commonLoader == null ) {
                // no config file, default to this loader - we might be in a 'single' env.
                commonLoader=this.getClass().getClassLoader();
            }
            // 创建catalinaLoader，父类加载器为commonLoader
            catalinaLoader = createClassLoader("server", commonLoader);
            // 创建sharedLoader，父类加载器为commonLoader
            sharedLoader = createClassLoader("shared", commonLoader);
        } catch (Throwable t) {
            // 如果创建的过程中出现异常了，日志记录完成之后直接系统退出
            handleThrowable(t);
            log.error("Class loader creation threw exception", t);
            System.exit(1);
        }
    }
    

接下来来看看`SecurityClassLoad.securityClassLoad`的使用其实就是使用catalinaLoader加载tomcat源代码里面的各个专用类。我们大致罗列一下待加载的类所在的package。

org.apache.catalina.core.*

org.apache.coyote.*

org.apache.catalina.loader.*

org.apache.catalina.realm.*

org.apache.catalina.servlets.*

org.apache.catalina.session.*

org.apache.catalina.util.*

org.apache.catalina.valves.*

javax.servlet.http.Cookie

org.apache.catalina.connector.*

org.apache.tomcat.*

## 组件

好不容易跟进了前面的tomcat源码，终于来到了我们的目的地组件的分析。

### Server

在跟进前面的Tomcat启动类中调用了，server.init方法和server.start方法，我们来看看Server的源码实现

在`org.apache.catalina.Server`接口中有着对方法的定义。

![image-20220912135001385.png](https://image.3001.net/images/20220917/1663399446_63257616b02f8a6b812df.png!small)

我们可以观察到其继承了我们前面分析了的生命周期的接口`Lifecycle`，这就意味着，在在调用了server.init或者start方法的同时同样会调用所有的service的方法。

来看看Server的实现类，类为`org.apache.catalina.core.StandardServer`下，在初始化的时候将会调用`initInternal`方法。

![image-20220912135358074.png](https://image.3001.net/images/20220917/1663399453_6325761d38e657705d043.png!small)

从这里的循环语句中也可以证实确实将会调用所有存在service的init方法，同样在调用servser.start方法的时候将会调用`startInternal`方法。

![image-20220912135520728.png](https://image.3001.net/images/20220917/1663399460_632576241cb69823cb40c.png!small)

同样通过了循环的方式进行调用，我们可以通过idea查看该类的继承实现结构关系图。

![image-20220912135924209.png](https://image.3001.net/images/20220917/1663399466_6325762a381b204885111.png!small)

### Service

其接口在`org.apache.catalina.Service`中，存在方法的定义，同样继承了Lifecycle接口。我们来到Service的实现类`org.apache.catalina.core.StandardService`。

首先上图看一下类的关系

![image-20220912140245150.png](https://image.3001.net/images/20220917/1663399472_63257630dc699e37dd14f.png!small)

既然在调用Server.init中会调用service.init方法，那我们就跟进一下service.init讲了个什么。

![image-20220912140505921.png](https://image.3001.net/images/20220917/1663399481_632576396f31af4080f13.png!small)

其中存在对Engine的初始化 / Executor的初始化(后面会提到) /
connector的初始化。同样的，跟进一下start方法的逻辑和上面调用init方法进行初始化差不多，分别调用了对应的start方法。

### Container

对于Container的接口在`org.apache.catalina.Container`中，同样继承了`Lifecycle`接口

首先看一下他的继承关系。

![image-20220912141434575.png](https://image.3001.net/images/20220917/1663399488_63257640c9037f3b5d791.png!small)

由上图我们可以知道Engine包含多个Host，Host包含多个Context，Context包含多个Wrapper，每个Wrapper对应一个Servlet。

分别的说明

Engine，我们可以看成是容器对外提供功能的入口，每个Engine是Host的集合，用于管理各个Host。

Host，我们可以看成`虚拟主机`，一个tomcat可以支持多个虚拟主机。

Context，又叫做上下文容器，我们可以看成`应用服务`，每个Host里面可以运行多个应用服务。同一个Host里面不同的Context，其contextPath必须不同，默认Context的contextPath为空格("")或斜杠(/)。

Wrapper，是Servlet的抽象和包装，每个Context可以有多个Wrapper，用于支持不同的Servlet。另外，每个JSP其实也是一个个的Servlet。

### Connector

最后来到了最关键的Connector部分了，也是构造内存马的关键位置。

首先来看看整体的架构流程图。

![image-20220912142342083.png](https://image.3001.net/images/20220917/1663399495_63257647948051cc9d298.png!small)

描述了请求到达Container进行处理的全过程。

不同协议`ProtocolHandler`会有不同的实现。

![image-20220912142537293.png](https://image.3001.net/images/20220917/1663399501_6325764dac6d235a94c1d.png!small)

  1. ajp和http11是两种不同的协议

  2. nio、nio2和apr是不同的通信方式

  3. 协议和通信方式可以相互组合

`ProtocolHandler`包含三个部件：`Endpoint`、`Processor`、`Adapter`。

  1. `Endpoint`用来处理底层Socket的网络连接，`Processor`用于将`Endpoint`接收到的Socket封装成Request，`Adapter`用于将Request交给Container进行具体的处理。

  2. `Endpoint`由于是处理底层的Socket网络连接，因此`Endpoint`是用来实现`TCP/IP协议`的，而`Processor`用来实现`HTTP协议`的，`Adapter`将请求适配到Servlet容器进行具体的处理。

  3. `Endpoint`的抽象实现类AbstractEndpoint里面定义了`Acceptor`和`AsyncTimeout`两个内部类和一个`Handler接口`。`Acceptor`用于监听请求，`AsyncTimeout`用于检查异步Request的超时，`Handler`用于处理接收到的Socket，在内部调用`Processor`进行处理。

接下来深入源码进行一下分析

跟进`org.apache.catalina.connector.Connector`类的代码逻辑

发现以下几点

  1. 无参构造方法，传入参数为空协议，会默认使用`HTTP/1.1`

  2. `HTTP/1.1`或`null`，protocolHandler使用`org.apache.coyote.http11.Http11NioProtocol`，不考虑apr

  3. `AJP/1.3`，protocolHandler使用`org.apache.coyote.ajp.AjpNioProtocol`，不考虑apr

  4. 其他情况，使用传入的protocol作为protocolHandler的类名

  5. 使用protocolHandler的类名构造ProtocolHandler的实例

接下来来到了`Connector#initInternal`方法的调用。

![image-20220912143734193.png](https://image.3001.net/images/20220917/1663399510_632576563a31e0a23174d.png!small)

总结一下就是初始化了一个CoyoteAdapter，并将其设置进入了protocolHandler中，之后接受了body的method列表，默认为POST。

最后初始化了初始化protocolHandler

之后将会调用`protocolHandler#init`方法

而对于start方法的调用，在`Connector`中

![image-20220912144206485.png](https://image.3001.net/images/20220917/1663399516_6325765c56f24541e5088.png!small)

在设置了状态为`STARTING`之后就调用了`protocolHandler#start`方法。

![image-20220912144319402.png](https://image.3001.net/images/20220917/1663399522_63257662452647232cb47.png!small)

将会调用endpoint#start方法。

跟进一下

![image-20220912144500383.png](https://image.3001.net/images/20220917/1663399531_6325766bb438d564d0ddf.png!small)

调用bind方法

创建工作者线程池。

初始化连接latch，用于限制请求的并发量。

开启poller线程。poller用于对接受者线程生产的消息（或事件）进行处理，poller最终调用的是Handler的代码。

开启acceptor线程

#### Acceptor

请求的入口是在`Acceptor`。`Endpoint.start()`方法会开启`Acceptor线程`来处理请求

那么我们接下来就要分析一下`Acceptor线程`中的执行逻辑

在其run方法中存在

  1. 运行过程中，如果`Endpoint`暂停了，则`Acceptor`进行自旋（间隔50毫秒）

  2. 如果`Endpoint`终止运行了，则`Acceptor`也会终止

  3. 如果请求达到了最大连接数，则wait直到连接数降下来

  4. 接受下一次连接的socket

存在这样的逻辑

`setSocketOptions()`这儿是关键，会将socket以事件的方式传递给poller。

![image-20220912145543039.png](https://image.3001.net/images/20220917/1663399540_63257674984b3c7d30b46.png!small)

跟进一下`setSocketOptions`

![image-20220912145648775.png](https://image.3001.net/images/20220917/1663399548_6325767c1509210da94b5.png!small)

其中存在`this.getPoller0.register`的调用将channel注册到poller，注意关键的两个方法，`getPoller0()`和`Poller.register()`。先来分析一下`getPoller0()`，该方法比较关键的一个地方就是`以取模的方式`对poller数量进行轮询获取。

    
    
    /**
     * The socket poller.
     */
    private Poller[] pollers = null;
    private AtomicInteger pollerRotater = new AtomicInteger(0);
    /**
     * Return an available poller in true round robin fashion.
     *
     * @return The next poller in sequence
     */
    public Poller getPoller0() {
        int idx = Math.abs(pollerRotater.incrementAndGet()) % pollers.length;
        return pollers[idx];
    }
    

接下来我们分析一下`Poller.register()`方法。因为`Poller`维持了一个`events同步队列`，所以`Acceptor`接受到的channel会放在这个队列里面。

#### Poller

`Acceptor`生成了事件`PollerEvent`，那么`Poller`必然会对这些事件进行消费。我们来分析一下`Poller.run()`方法。

在其中存在有

![image-20220912150030584.png](https://image.3001.net/images/20220917/1663399556_6325768465b6e858a194e.png!small)

调用了processKey(sk, socketWrapper)进行处理。

![image-20220912150119743.png](https://image.3001.net/images/20220917/1663399562_6325768a6a04f2dc57a29.png!small)

该方法又会根据key的类型，来分别处理读和写。

  1. 处理读事件，比如生成Request对象

  2. 处理写事件，比如将生成的Response对象通过socket写回客户端

跟进`processSocket`方法

![image-20220912150220147.png](https://image.3001.net/images/20220917/1663399568_63257690ad4bf16bbfe19.png!small)

  1. 从`processorCache`里面拿一个`Processor`来处理socket，`Processor`的实现为`SocketProcessor`

  2. 将`Processor`放到工作线程池中执行

#### Processor

调用`service()`方法

  1. 生成Request和Response对象

  2. 调用`Adapter.service()`方法，将生成的Request和Response对象传进去

#### Adapter

`Adapter`用于连接`Connector`和`Container`，起到承上启下的作用。`Processor`会调用`Adapter.service()`方法主要做了下面几件事情

根据coyote框架的request和response对象，生成connector的request和response对象（是HttpServletRequest和HttpServletResponse的封装）

补充header

解析请求，该方法会出现代理服务器、设置必要的header等操作

真正进入容器的地方，调用Engine容器下pipeline的阀门

## 总结

就这样，深入代码的了解了整个Tomcat的架构(当然，还是有很多的代码没有贴出来，太长了，需要师傅们自己跟一下)，跟完之后大吸一口凉气。真难》

## Ref

https://www.jianshu.com/u/794bce41b31b

http://chujunjie.top/2019/04/30/Tomcat源码学习笔记-Connector组件-二/

