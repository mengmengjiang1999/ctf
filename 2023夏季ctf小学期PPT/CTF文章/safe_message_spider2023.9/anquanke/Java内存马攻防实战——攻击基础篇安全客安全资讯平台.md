# Java内存马攻防实战——攻击基础篇

阅读量 **204945**

发布时间 : 2022-05-17 10:30:56

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t0182ae4c7c8faafa5c.jpg)

在红蓝对抗中，攻击方广泛应用webshell等技术在防守方提供的服务中植入后门，防守方也发展出各种技术来应对攻击，传统的落地型webshell很容易被攻击方检测和绞杀。而内存马技术则是通过在运行的服务中直接插入运行攻击者的webshell逻辑，利用中间件的进程执行某些恶意代码，而不依赖实体文件的存在实现的服务后门，因此具有更好的隐蔽性，也更容易躲避传统安全监测设备的检测。

本文以Java语言为基础讨论内存马技术的攻防，分为两个篇章，分别是攻击基础篇和防护应用篇。本篇攻击基础篇介绍了Java
Servlet技术前置知识，并重点讨论了Java内存马的注入点和注入方式。下一篇文章将会针对这些注入方式的拦截防御手段展开讨论，进一步探索Java内存马的攻防实战。

## JAVA Servlet技术前置知识

###  Servlet/Filter/Listener JAVA WEB三大件

**1\. Servlet**

Servlet 是服务端的 Java 应用程序，用于处理HTTP请求，做出相应的响应。

![](https://p2.ssl.qhimg.com/t0188157f82a2af94a2.png)

**2\. Filter**

Filter 是介于 Web 容器和 Servlet 之间的过滤器，用于过滤未到达 Servlet 的请求或者由 Servlet
生成但还未返回响应。客户端请求从 Web 容器到达 Servlet 之前，会先经过 Filter，由 Filter 对 request
的某些信息进行处理之后交给 Servlet。同样，响应从 Servlet 传回 Web 容器之前，也会被 Filter 拦截，由 Filter 对
response 进行处理之后再交给 Web 容器。

![](https://p5.ssl.qhimg.com/t0162482299af1c6d60.png)

**3\. Listener**

Listener
是用于监听某些特定动作的监听器。当特定动作发生时，监听该动作的监听器就会自动调用对应的方法。下面是一个HttpSession的Listener示意图。

![](https://p2.ssl.qhimg.com/t010b6feefccfbad336.png)

该 Listener 监听 session 的两种状态，即创建和销毁。当 session 被创建时，会自动调用 HttpSessionListener 的
sessionCreated() 方法，我们可以在该方法中添加一些处理逻辑。当 session 被销毁时，则会调用 sessionDestroyed()
方法。

当我们在请求一个实现servlet-api规范的java web应用时，程序先自动执行 listener 监听器的内容，再去执行 filter
过滤器，如果存在多个过滤器则会组成过滤链，最后一个过滤器将会去执行 Servlet 的 service 方法，即 Listener -> Filter ->
Servlet。

## 内存马的攻击面

webshell实际上也是一种web服务，那么从创建web服务的角度考虑，自顶向下，有下面几种手段和思路：

  1. 动态注册/字节码替换 interceptor/controller（使用框架如 spring/struts2/jfinal）
  2. 动态注册/字节码替换 使用责任链设计模式的中间件、框架的实现（例如 Tomcat 的 Pipeline & Valve，Grizzly 的 FilterChain & Filter 等等）
  3. 动态注册/字节码替换 servlet-api 的具体实现 servlet/filter/listener
  4. 动态注册/字节码替换一些定时任务的具体实现 比如 TimeTask等

另外，换一个角度来说，webshell作为一个后门，实际上我们需要他完成的工作是能接收到恶意输入，执行恶意输入并回显。那么我们可以考虑启动一个进程或线程，无限循环等待恶意输入并执行代码来作为一个后门。

## 环境准备

我们首先从Tomcat这一使用广泛的中间件开始说起，在其他中间件如weblogic中对servlet-api规范的实现略有不同，但其思想是一致的。

实验环境如下  
`jdk 8u102  
springboot 2.5.5 (Tomcat embedded)  
fastjson 1.2.47`

下面我们构造一个简单的JAVA 任意代码注入点

![](https://p0.ssl.qhimg.com/t01d8921b14ac9c626d.png)

通过fastjson 1.2.47 rmi反序列化的方式进行注入，因为重点是注入内存马所以选择了jdk 1.8u102<121的版本进行实验。

fastjson使用的exp为：

![](https://p1.ssl.qhimg.com/t01efcf77f92993d26a.png)

这里通过marshalsec启动rmi服务器，并通过python SimpleHTTPSever来提供恶意类字节码下载服务：

![](https://p3.ssl.qhimg.com/t010396a4416ceeea7d.png)

通过该漏洞我们能实现任意java代码执行：

![](https://p3.ssl.qhimg.com/t01c0ddb9ac66e34a22.png)

比如利用jndi注入这个类会弹出计算器。

至此我们获得了tomcat环境下的java代码任意执行。

## 动态注入Servlet

###  注入过程

通常情况下，Servlet/Filter/Listener配置在配置文件（web.xml）和注解中，在其他代码中如果想要完成注册，主要有以下几种思路：

  1. 调用Servlet Api 的相关接口（一般只能在应用初始化时调用）
  2. 使用中间件提供的相关接口

下面复现的是第二种方式，对于tomcat获取StandardContext来在web应用运行时注入servlet：

![](https://p5.ssl.qhimg.com/t01941dbbfa5ff315a5.png)

可以看到我们的基本流程如下：  
1.获取 ServletContext  
2.获取 Tomcat 对应的 StandardContext  
3.构建新 servlet warpper  
4.将构建好的 warpper 添加到 standardContext 中，并加入 servletMappings

在后续的fliter型内存马和listener型内存马中我们会发现其注入过程也是类似的。

###  几个疑问

**1\. Wrapper是什么？**

在这次复现的环境中，我们使用的中间件是Tomcat。

Tomcat 是 Web 应用服务器，是一个 Servlet/JSP 容器，Tomcat 作为 Servlet 的容器，能够将用户的请求发送给
Servlet，并且将 Servlet 的响应返回给用户，Tomcat中有四种类型的Servlet容器，从上到下分别是
Engine、Host、Context、Wrapper

• Engine，实现类为 org.apache.catalina.core.StandardEngine  
• Host，实现类为 org.apache.catalina.core.StandardHost  
• Context，实现类为 org.apache.catalina.core.StandardContext  
• Wrapper，实现类为 org.apache.catalina.core.StandardWrapper

每个Wrapper实例表示一个具体的Servlet定义，StandardWrapper是Wrapper接口的标准实现类（StandardWrapper
的主要任务就是载入Servlet类并且进行实例化）。  
其结构如下图：

![](https://p3.ssl.qhimg.com/t0157a93c2c581273b4.png)

可以看到，如果我们想要添加一个Servlet，需要创建一个Warpper包裹他来挂载到Context(StandardContext中)。

**2\. 在复现过程中，我们看到了很多Context，这些Context分别对应什么呢？**

是 WebApplicationContext，ServletContext与StandardContext。

WebApplicationContext: 其实这个接口其实是SpringFramework
ApplicationContext接口的一个子接口，对应着我们的web应用。它在ApplicationContext的基础上，添加了对ServletContext的引用，即getServletContext方法。因此在注入内存马的过程中，我们可以利用他来拿到ServletContext。

ServeltContext: 这个就是我们之前说的servlet-api给的规范servlet用来与容器间进行交互的接口的组合，这个接口定义了一系列的方法来描述上下文（Cotext），servlet通过这些方法可以很方便地与自己所在的容器进行一些交互，比如通过getMajorVersion与getMinorVersion来获取容器的版本信息等。

StandardContext:
这个是tomcat中间件对servlet规范中servletContext的实现，在之前的tomcat架构图中可以看到他的作用位置，用来管理Wrapper。

如果我们将  
`standardContext.addServletMappingDecoded("/bad",servletName);`  
改为  
`servletContext.addServlet("/bad",servletName);`  
会得到如下报错  
`java.lang.IllegalStateException: Servlets cannot be added to context [] as
the context has been initialised`

可以看到ServletContext虽然提供了addServlet等接口，但是只允许在应用初始化时调用。对于Tomcat来说如果我们要在应用初始化后动态添加Servlet，我们需要在standardContext中addChild也即包装好Servlet的Wrapper。

**3\. 如何获取ServletContext/StandardContext?**

在Tomcat中，只要我们获取了ServletContext，就能找到应用的StandardContext，而且对于不同的中间件来说，ServletContext更具有普适性，所以这个问题可以归结于如何获取ServletContext。

在这个例子中，我们获取ServletContext的方法是：

`// 获取当前应用上下文  
WebApplicationContext context =
RequestContextUtils.findWebApplicationContext(((ServletRequestAttributes)
RequestContextHolder.currentRequestAttributes()).getRequest());  
ServletContext servletContext = context.getServletContext();`

通过先获取WebApplicationContext再拿到ServletContext。

当然这只是其中一种方法，一般来说获取ServletContext有两种思路，一种是通过获取上下文的http请求信息来获得servletContext，在这个例子中就是通过ServletRequestAttributes)
RequestContextHolder.currentRequestAttributes()找到了WebApplicationContext，进而找到了ServletContext。

另外一种思路就是通过在tocmcat启动的http线程中遍历找到有用的信息。在前文中对tomcat的架构进行了介绍，根据tomcat的架构我们可以自顶向下找到线程对应的servletContext。
bitterz师傅给出了一条tomcat全版本的利用链，其中tomcat9的具体链条如下：

![](https://p4.ssl.qhimg.com/t01d4c42fe2b4007c19.png)

从Connector找到StandardSerive，再到StandardEngine，最后获取到TomcatEmbeddedContext[@5990](https://github.com/5990
"@5990")也就是我们想要的StandardContext。

## 动态注入Filter

具体思路如下:

调用 ApplicationContext 的 addFilter 方法创建 filterDefs 对象，需要反射修改应用程序的运行状态，加完之后再改回来；

调用 StandardContext 的 filterStart 方法生成 filterConfigs；

调用 ApplicationFilterRegistration 的 addMappingForUrlPatterns 生成 filterMaps；

为了兼容某些特殊情况比如Shiro，将我们加入的 filter 放在 filterMaps 的第一位，可以自己修改 HashMap
中的顺序，也可以在自己调用 StandardContext 的 addFilterMapBefore 直接加在 filterMaps 的第一位。

鉴于之前已经讨论过standardContext的获取和webshell的内容，在此处略去，我们只关心如何在拿到standardContext的情况下注入Filter型内存马。

![](https://p0.ssl.qhimg.com/t011f7a94162272186a.png)

## 动态注入Listener

在前面的铺垫中我们介绍了多种listener，对于内存马来说，最好用的一个Listener莫过于ServletRequestListener，他监听request的建立和销毁，因此我们可以拿到  
Tomcat 中 EventListeners 存放在 StandardContext 的 applicationEventListenersObjects
属性中，同样可以使用 StandardContext 的相关 add 方法添加。

具体动态添加过程相对Filter和Servlet来说反而要相对简单些。直接通过StandardContext的addApplicationEventListener方法即可。

代码如下：

![](https://p5.ssl.qhimg.com/t01ed031f64d36955ce.png)

值得注意的是requestEvent 只能直接拿到Servletrequest对象，response需要通过request拿到。

## 动态注入Tomcat Value Pipe

###  Tomcat Value 机制

在之前的Tomcat框架图中，我们还漏了一个重要的机制Pipeline.在Tomcat中，四大容器类StandardEngine、StandardHost、StandardContext、StandardWrapper中，都有一个管道(PipeLine)及若干阀门(Valve)。如下图所示。

![](https://p2.ssl.qhimg.com/t01644ebc56958338e2.png)

顾名思义，类似供水管道（PipeLine）中的各个阀门(Value)，用来实现不同的功能，比方说控制流速、控制流通等等。

我们可以自行编写具备相应业务逻辑的Valve，并添加进相应的管道当中。这样，当客户端请求传递进来时，可以在提前相应容器中完成逻辑操作。这为我们编写内存马提供了一个很好的落脚点。

动态添加的方法也很简单，在获取到standardContext后直接拿Pipeline，调用Pipline.addValue方法即可。代码其他部分不再赘叙。

![](https://p4.ssl.qhimg.com/t011ac88c506de438e0.png)

效果如下：

![](https://p2.ssl.qhimg.com/t01f5130be0bca39dad.png)

访问任意url并输入密码和命令既可以getshell：

![](https://p5.ssl.qhimg.com/t01cc9a4757e465dc92.png)

特征是恶意类会实现org.apache.catalina.Valve接口：

![](https://p0.ssl.qhimg.com/t01bdd3510dd4b57722.png)

## 动态注入Glassfish Grizzly

为了说明利用框架责任链组件注入java内存马，这里再举一个su18师傅提到的GlassFish Gizzly的链子。

GlassFish中的grizzly组件负责解析和序列化HTTP 请求/响应，类似Tomcat的Pipeline和Valve，grizzly
有FilterChain 和Filter，而filter就为我们提供了一个内存马的注入点。

注入代码如下，这里采取的方法是通过HttpServletRequest获取grizzlyRequest，调用其addAfterServiceListener

![](https://p4.ssl.qhimg.com/t01161d1fd2c39b2c13.png)

在AfterServiceListener的onAfterService中拿到filterChain并添加恶意Filter：

![](https://p2.ssl.qhimg.com/t010a02e22e0c771ed2.png)

一个示例恶意Filter如下，可以通过connection的channel来操作socket读写管道：

![](https://p0.ssl.qhimg.com/t01d4a84a36f09c88dd.png)

特征是恶意类会实现org.glassfish.grizzly.filterchain.Filter接口。

## 动态注入Spring Controller

在SpringMVC框架中，请求是通过Controller来处理的，如果我们用jspscanner去看spring的servlet，会发现只有一个servlet

![](https://p5.ssl.qhimg.com/t017c27c0ab8ef5ea91.png)

那么我们的Controller在哪呢?  
通过调试分析我们可以发现Spring
Contorller实际上挂载在RequestMappingHandlerMapping的registry中，可以通过registerMapping和addMappingName等方法动态添加Controller

![](https://p0.ssl.qhimg.com/t0125392e7d2b797b25.png)

这里的思路简单来说就是

  1. 获取应用的上下文环境，也就是ApplicationContext
  2. 从 ApplicationContext 中获取 AbstractHandlerMapping 实例（用于反射）
  3. 反射获取 AbstractHandlerMapping类的 getMappingRegistry字段
  4. 通过 getMappingRegistry注册Controller

![](https://p5.ssl.qhimg.com/t01317d881dc7cf17b4.png)

完成上述操作后，我们实际上相当于将Evil类的test方法添加到了Controller中，我们只要在test方法里写入内存马逻辑就可以了。

![](https://p1.ssl.qhimg.com/t01969f4077c5cef495.png)

效果如图：

![](https://p4.ssl.qhimg.com/t01c55966047abb8b2b.png)

![](https://p3.ssl.qhimg.com/t01deec699df1a1bbfc.png)

![](https://p0.ssl.qhimg.com/t01d2dc6f01850c63b7.png)

## 动态注入Spring Interceptor

Interceptor类似servlet规范中的filter，不过spring的interceptor主要针对的是spring controller的过滤。

注入方式也和Controller类似，也是在AbstractHandlerMapping中，存放在adaptedInterceptors属性里。

![](https://p0.ssl.qhimg.com/t0129403e036911eaec.png)

## 注入线程

利用Java中Timer的特性，启动一个Timer线程，在其中执行webshell逻辑，如果不是所有未完成的任务都已完成执行，或不调用 Timer
对象的cancel
方法，这个线程不会停止，也不会被回收。也就是说，如果是一个jsp文件，即使这个jsp后门在上传访问后被删除，Timer启动的线程也不会停止，这就为我们的内存马利用提供了一个很好的平台。当然因为不在web上下文中，获取http请求和回显的逻辑要稍微复杂些，不过用之前遍历进程找servletContext的方式可以实现指定中间件的通杀。

比如：

![](https://p4.ssl.qhimg.com/t01e7f46cfd0891279b.png)

能拿到ServerSocketChannel。  
也可再找到Request：

![](https://p1.ssl.qhimg.com/t01271e0a20bf1c3e9c.png)

实现：

![](https://p1.ssl.qhimg.com/t01a998bcde12196ceb.png)

## 内存马持久化

因为内存马本身不落地的特性，应用重启后内存马就不复存在，为了实现内存马的持久化，势必还是要有文件落地的，这里我们可以利用一些钩子，比如Runtime.getRuntime().addShutdownHook()，rebeyond师傅的memShell项目就是通过这种手段实现复活的。

![](https://p1.ssl.qhimg.com/t01aa7c7566118a7585.png)

JVM关闭前，会先调用addShutdownHook()，其中的writeFiles把inject.jar和agent.jar写到磁盘上，然后调用startInject，startInject通过Runtime.exec启动java
-jar inject.jar等待注入新的jvm进程。

类似效果的还有weblogic的 startUpClass
在weblogic在启动后，加载webapp之前，会根据startUpClass参数，去执行指定类。

以及Servlet Api 提供的ServletContainerInitializer接口。在META-INF/services/javax.servlet.ServletContainerInitializer文件中通过SPI的方式进行注册。容器在启动时，就会扫描所有带有这些注册信息的类，启动时会ServletContainerInitializer声明的onStartup方法。

此外，通过java.util提供的jar相关接口还可以对本地jar包进行修改,比如4ra1n师傅提到的tomcat-websocket.jar以及Landgery师傅提到的charsets.jar，都可以起到一定的内存马“隐秘落地”效果。

## 结语

在本篇中主要讨论了java内存马的一些注入点和注入方式，可以看到注入点主要集中在java
servlet规范的listener/filter/servlet中，根据不同中间件的实现方式通过不同的手段进行注入，当然也可以根据中间件或上web框架提供的一些其他特性进行注入。在下一篇文章中，我们将会针对这些注入方式的拦截防御手段进行讨论，进一步探索java内存马的攻防实战。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **长亭科技** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/273250](/post/id/273250)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)
  * [Java](/tag/Java)

 **+1** __5赞

 __收藏

![](https://p4.ssl.qhimg.com/t012a2b2cc9165a693a.jpg) 长亭科技

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

