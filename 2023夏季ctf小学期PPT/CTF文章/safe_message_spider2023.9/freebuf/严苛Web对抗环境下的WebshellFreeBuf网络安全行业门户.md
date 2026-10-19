## **引言**

随着攻防对抗的强度越来越高，各大厂商流量分析、EDR等专业安全设备已广泛使用，对于Webshell的检测能力愈发成熟，对于攻击方来说，传统落地文件型的Webshell生存空间越来越小。如何在实战演练过程中完成高隐匿和持续性的Web权限维持，成为了Web对抗技术的研究重点，Webshell逐渐涌现出来一些新的利用方式。

## Webshell 变迁

传统 Webshell
都是基于文件类型，攻击者可以通过文件上传、任意文件写入等漏洞将Webshell植入到目标机器的Web目录下，从而达到权限维持的目的，由于需要在目标机器上执行写入操作，防守方可以通过静态检测的方式对文件中所使用的关键词、敏感函数、文件创建/修改时间、文件权限、文件所有者等多个维度的特征进行检测，传统Webshell生存空间被逐渐压缩，内存型Webshell应运而生。内存型
Webshell（MemWebshell）利用代码执行等方式，直接将恶意的代码注入到Web应用进程当中，具备无文件落地的特性更加符合OPSEC的原则，给检测带来巨大难度，适用于严苛的Web对抗场景。

## MemWebshell 分类

MemWebshell 从注入方式和运行原理的角度上划分为两个大类：

1\. 基于Servlet规范利用：利用反序列化等具备任意代码执行能力的漏洞，动态注册符合Servlet规范的自定义恶意组件到Web容器的 Context
中，包括 Servlet、Filter、Listener 等，攻击者通过请求特定的路由实现与MemWebshell的通信；

2\. 基于 Java Instrumentation 利用：利用 Java Instrumentation 技术（JDK 5.0引入），动态修改 JVM
中Class 的字节码，包括类的属性、方法等内容，攻击者利用该技术 Hook 已有容器或 Servlet
代码逻辑，使用动态字节码操作类库实现自定义恶意代码逻辑的插入或修改；

## 动态注册 MemWebshell

在日常项目开发当中有两种标准的注册方式，使用「XML配置文件」或「注解配置」，其本质是描述目标实例对象所需的配置信息，例如：路由信息、类信息等，最终底层都由
Web 容器来获取 XML 或者注解中的配置，完成 Servlet 实例对象的初始化，并注册到容器相应的 Context 中。其中，主要利用了
Servlet API 提供的动态注册机制，该机制是在 Servlet 3.0 中发布，为 Servlet、Filter、Listener 在
javax.servlet.ServletContext 接口中都提供了相应的注册方法，攻击者可利用该特性完成 MemWebshell 的动态注册。

 **注册 Filter MemWebshell**

Filter 为过滤器，通过实现 javax.servlet.Filter 接口实现对目标请求的拦截，请求进入服务器后，先由 Filter
对请求进行预处理，通过配置 URL Pattern 实现对指定请求的拦截和过滤。

如何动态注册 Filter 到容器中？以 Tomcat 为例，断点调试自定义的 Servlet，可以看到 Filter 的调用核心是
ApplicationFilterChain 类，其中 filters 属性中存放着所有已经注册完成的 filter 实例，在
ApplicationFilterChain#internalDoFilter 方法中会循环获取 filters 属性中的过滤器实例，并调用过滤器的
doFilter 方法，实现对请求过滤逻辑的调用。如下图所示，filters 中已经存在一个容器自带的过滤器 WsFilter，跟踪该 Filter
来了解动态注册的方式。

![1638859089_61af015118a87c91a616a.png!small?1638859090214](https://image.3001.net/images/20211207/1638859089_61af015118a87c91a616a.png!small?1638859090214)

通过调试分析可以发现在上层的 WsServerContainer 方法中，Tomcat 对 WsFilter 过滤器的注册，即 filters
属性中的默认过滤器。

    
    
    WsServerContainer(ServletContext servletContext) {  
    ...  
      
    // 动态注册 WsFilter 类  
    FilterRegistration.Dynamic fr = servletContext.addFilter(  
    "Tomcat WebSocket (JSR356) Filter", new WsFilter());  
    fr.setAsyncSupported(true);  
      
    EnumSet<DispatcherType> types = EnumSet.of(DispatcherType.REQUEST,  
    DispatcherType.FORWARD);  
      
    // 绑定过滤器与URL映射关系  
    fr.addMappingForUrlPatterns(types, true, "/*");  
    }

参照上述默认过滤器 WsFilter 类的注册，可以实现自定义过滤器的动态注册代码。通过请求任意路由的 cmd 参数即可执行任意命令。

![1638859956_61af04b438c7df8ccf34b.png!small?1638859957309](https://image.3001.net/images/20211207/1638859956_61af04b438c7df8ccf34b.png!small?1638859957309)

调试 Tomcat 源码可以获知，每次请求的 ApplicationFilterChain#filters属性都是动态生成的，请求结束后，会调用
ApplicationFilterChain#release 方法释放其中的 Filter，自定义的 Filter 无法直接通过反射将注册进去，需要在
StandardContext#filterMaps 中进行 FilterMap 的添加。注册过程中，会受到 Tomcat
生命周期状态的影响，需要利用反射动态的对运行状态进行 修改 和 恢复。整个注册过程中的关键技术就是基于 Servlet 3.0 ServletContext
接口方法的调用，而 Tomcat 中 ApplicationContext 类实现了该接口。

Filter在注册过程中有三个关键实例：

  * filterDefs：该实例中包含所有Filter以及Filter的定义信息；

  * filterMaps：该实例中包含所有Filter的URL映射关系；

  * filterConfigs：该实例中包含所有的Filter以及Filter对应的FilterDef。

Filter MemWebshell 注册思路：

1\. 获取 ApplicationContext 实例，并调用 addFilter 等方法进行 Filter 的注册以及URL匹配模式的绑定；

2\. 利用反射动态的对容器运行状态进行 修改 和 恢复，辅助 Filter 的注册添加。

 **注册 Servlet MemWebshell**

Servlet 为 Server Applet 的简称，即：服务端程序，Servlet 用于读取处理客户端发送的数据，并响应结果。通过将自定义的
Servlet 与 URL 匹配模式注册到容器中，实现 Servlet MemWebshell。

Servlet 的动态注册相比于上述 Filter 比较类似，同样是使用 Tomcat ApplicationContext 中的 addServlet
方法进行实现，直接使用该方法进行 Servlet 的注册会出现异常，主要会受到容器运行状态的影响，可以仿照 Filter
注册的方式，动态的对运行状态进行修改，这里会使用更加“优雅”的方式进行注册，下面是核心的注册逻辑：

    
    
    Wrapper wrapper = standardContext.createWrapper();  
    wrapper.setName("MemWebshellServlet");  
    wrapper.setServlet(servletTest);  
    standardContext.addChild(wrapper);  
    standardContext.addServletMappingDecoded("/memwebshell-servlet", "MemWebshellServlet");

Servlet MemWebshell注册思路：

1\. 获取 standardContext 实例，创建 Servlet 容器；

2\. 设置待注册 Servlet Name 以及 Servlet 类；

3\. 注册 Servlet 容器到 standardContext 中；

4\. 增加 URL 匹配模式与 Servlet 的对应关系。

通过分析 ApplicationContext#addServlet 方法的实现，利用上述思路，使用更加精简的代码完成 Servlet
MemWebshell 的注册，省去了对容器运行状态的修改。

 **注册 Listener MemWebshell**

Listener 为 Servlet 的监听器，可以监听客户端的请求、服务端的操作。可以在 application、session、request
对象创建、销毁或者增改删属性事件发生时，自动执行代码的功能组件，同样也可以在其中进行 MemWebshell 的注入。

通过实现 ServletRequestListener 接口的 requestInitialized 和 requestDestroyed
方法，在请求创建或者销毁时调用。通过分析 Tomcat ApplicationContext#addListener 方法的 Listener
注册，底层实际调用 StandardContext#addApplicationEventListener 方法将自定义的 Listener 添加到了
applicationEventListenersList 属性中。

    
    
    // 注册自定义的Listener  
    standardContext.addApplicationEventListener(listenerTest);

Listener MemWebshell注册思路：

1\. 获取 standardContext 实例；

2\. 调用 addApplicationEventListener 方法添加自定义 Listener。

## Instrumentation注入MemWebshell

 **Instrumentation 技术介绍**

Instrumentation 是 Java 1.5 发布的新特性，其底层实现依赖于 JVMTI（JVM Tool Interface），是 Java
虚拟机对外提供的 Native 编程接口，通过 JVMTI 外部进程可以获取到运行时的 JVM
信息，使得开发者可以通过构建独立于应用程序的代理程序（Agent），实现监控 JVM 内部的状态，甚至可以实现对 JVM 中 Class
字节码的查看和修改，这种特性实际上提供了一种虚拟机级别的 AOP 方式，开发者无需对目标应用进行任何改动，就能完成一些 AOP
的功能，实现对类字节码的动态修改和增加。Instrumentation 类型的 MemWebshell 正是利用了这一特点，通过动态的修改 JVM
中的关键类，实现了对客户端请求数据的接收，在此基础上进行MemWebshell 的注入。

![1638860020_61af04f48fd3768c28c81.png!small?1638860021740](https://image.3001.net/images/20211207/1638860020_61af04f48fd3768c28c81.png!small?1638860021740)

Instrument Agent 有两种不同的加载方式：

1\. On Load 加载：JDK 1.5 开始的特性，实现独立的代理 Jar 包，在 JVM 启动时，指定启动参数 -javaagent
通过代理的形式引入，其中的 premain 方法在程序本身 main 方法运行之前，对加载的 Class 进行修改；

2\. On Attach 加载：JDK 1.6 开始的特性，相比于启动时加载 Jar 包，这种方式可以在 JVM 启动后通过 Attach API
实现动态加载代理 Jar 包，通过实现 agentmain 方法对加载的 Class 进行修改。

![1638860053_61af051599a273817cc8c.png!small?1638860054716](https://image.3001.net/images/20211207/1638860053_61af051599a273817cc8c.png!small?1638860054716)

如上图 On Load 加载方式为例，通过使用 JVM 启动参数指定 Java Agent，在 Agent 中调用 Instrumentation API
的 addTransformer 方法注册类加载时的回调方法，从而实现通用的类加载拦截，而 Instrumentation MemWebshell
正是在这里介入到了 Class 加载的环节当中。

正常情况下，JVM 启动后会加载所需的类并进入程序的 main 方法中，当 Agent 介入后，类首次加载并且进入 main 方法之前，premain
方法会先被调用，利用 addTransformer 方法注册自定义的 ClassFileTransformer 类到 JVM 中，在加载其他类前回调该类的
transform 方法对指定的类进行转换，借助 ASM、Javassist 等字节码增加框架，可以在类中插入自定义的字节码，从而完成
MemWebshell 的注入。

而在 On Attach 加载方式中，由于是在 JVM 已经启动之后才进行注入，其中的类已经完成了加载，因此需要借助 Instrumentation API
中的 retransformClasses 方法对类进行重新转换，让其回调到自定义的 transform 方法中进行处理。

下列是 Instrumentation API 中的关键方法：

    
    
    // Instrumentation API  
      
    public interface Instrumentation {  
    // 注册一个自定义的 ClassFileTransformer，通过实现其中的transform方法实现对类的修改  
    void addTransformer(ClassFileTransformer transformer);  
      
    // 对已经加载的类进行重新转换，会被回调到 ClassFileTransformer 中进行处理  
    void retransformClasses(Class<?>... classes) throws UnmodifiableClassException;  
      
    // 获取所有已经加载到 JVM 中的类  
    Class[] getAllLoadedClasses();  
      
    // 获取所有已经被初始化过的类  
    Class[] getInitiatedClasses(ClassLoader loader);  
      
    // 判断指定类是否可被修改  
    boolean isModifiableClass(Class<?> theClass);  
    }  
      
    // ClassFileTransformer 接口  
    public interface ClassFileTransformer {  
    byte[] transform(    
    ClassLoader loader,  
    String className,  
    Class<?> classBeingRedefined,  
    ProtectionDomain protectionDomain,  
    byte[] classfileBuffer  
    )  
    }

 **MemWebshell 注入思路**

在 Java Agent 的介绍当中，已经分析到了注入 MemWebshell 的核心思路，攻击者获取到服务器权限以后，目标机器上通常已经启动了 Java
程序，因此会选择使用 Attach 的方式注入恶意的代码到内存中。MemWebshell 要与外部进行通信，需要在每次请求中都能进行访问，不受请求目标
URL 的影响，以 Tomcat 为例，从动态注册 Filter 中流程中可以获知
ApplicationFilterChain#internalDoFilter 方法在每次请求过程中都会调用，其入参 ServletRequest 和
ServletResponse 分别可以用于获取 外部传参 和 返回结果，满足了注入 MemWebshell 的关键条件，攻击者会使用 javaassist
字节码增强框架实现自定义逻辑添加。

    
    
    // ApplicationFilterChain#internalDoFilter  
      
    private void internalDoFilter(ServletRequest request, ServletResponse response) throws IOException, ServletException {  
    /**  
    * 插入自定义 MemWebshell 字节码  
    */  
    if (this.pos < this.n) { ... }  
    ...  
    }

已经具备了 Request 和 Response 实例，注入的 MemWebshell 实际就是类似于 Servlet
的代码逻辑，通过“密码”从请求中获取入参，经过Webshell处理后，使用 Response
输出流进行结果的返回。整个处理逻辑可以实现高度定制化的需求，例如：目前主流的冰蝎会在服务端实现自定义的 ClassLoader 类，利用
defineClass 方法还原客户端发送的字节码为 Class 类，在自定义的类中实现 Webshell 的功能代码，结合 MemWebshell
具备灵活度高、隐蔽性强的特点。

## MemWebshell 总结

基于 Servlet MemWebshell 可以添加自定义的代码逻辑到内存中，充分的利用了 Servelet 3.0 ServletContext
的动态注册特性，类似的方式可以在 Weblogic、JBoss 等符合特性的其他容器中进行注册，除了基于Web容器，SpringBoot
Controller 和 Intercepor
也能动态注册。动态注册MemWebshell整个过程中，具备无文件落地的特性，符合OPSEC的原则，给检测带来了巨大的难度。

Instrumentation MemWebshell
在运行过程中，不会在服务器上留下文件痕迹，有效的避开了主机安全设备的静态查杀过程，并且不启动额外端口、进程等特点，作为权限维持的手段受到攻击者的青睐。不过该种技术也存在一定的局限性，首先需要有目标服务器足够的控制权限，能够上传
Agent Jar 包并且运行 Java 命令实现功能代码的注入，而且由于需要修改 JVM 中加载的 Class
字节码，在原有的程序逻辑上具有一定的侵入性，一旦出现修改错误可能会导致目标服务 Crash 风险。

