Spring框架是一个开放源代码的J2EE应用程序框架，由Rod Johnson发起，是针对bean的生命周期进行管理的轻量级容器（lightweight
container）。Spring解决了开发者在J2EE开发中遇到的许多常见的问题，提供了功能强大IOC、AOP及Web
MVC等功能。Spring可以单独应用于构筑应用程序，也可以和Struts、Webwork、Tapestry等众多Web框架组合使用，并且可以与Swing等桌面应用程序AP组合。

因此， Spring不仅仅能应用于J2EE应用程序之中，也可以应用于桌面应用程序以及小应用程序之中。Spring框架主要由七部分组成，分别是Spring
Core、 Spring AOP、 Spring ORM、 Spring DAO、Spring Context、 Spring Web和 Spring
Web MVC。

##  **Part1 漏洞状态**

![v2-933208c6c6c4bd820c4693d16554e098_720w.jpg](https://image.3001.net/images/20220414/1649910216_6257a1c83954f43cdde8e.jpg!small)

##  **Part2 漏洞描述**

在 JDK 9+ 上运行的Spring MVC或Spring WebFlux应用程序可能容易受到通过数据绑定的远程代码执行 (RCE)
的攻击。具体的利用需要应用程序作为 WAR 部署在Tomcat 上运行。如果应用程序被部署为Spring
Boot可执行jar，即默认值，则它不易受到漏洞利用。但是，该漏洞的性质更为普遍，可能还有其他方法可以利用它。

![v2-709ae974f1c624d835a180f92eb73fcb_720w.jpg](https://image.3001.net/images/20220414/1649910216_6257a1c876150e49bd33f.jpg!small)

影响范围：  
– spring框架版本5.3.0 -5.3.17、5.2.0 – 5.2.19  
– JDK 9+  
– Apache Tomcat

##  **Part3 复现环境**

Windows 10  
Tomcat 8.5.7.7  
Spring MVC 5.2.3

##  **Part4 漏洞复现**

– 搭建Spring MVC基础环境

![v2-ceb97fb2d75fcc8231fd3b4ea24e120e_720w.jpg](https://image.3001.net/images/20220414/1649910216_6257a1c8c8ebab9ff90ed.jpg!small)![v2-6938af4df9f20df36345450de5971971_720w.jpg](https://image.3001.net/images/20220414/1649910217_6257a1c91faa3f1db9cb5.jpg!small)

– 修改配置  
File->Project Structure

![v2-52f2bc4e4a24dc6cb216aa29dfdbcf80_720w.jpg](https://image.3001.net/images/20220414/1649910217_6257a1c95a19befaa51be.jpg!small)

![v2-c767116fa0685e31c70025fa77a9703a_720w.jpg](https://image.3001.net/images/20220414/1649910217_6257a1c9b08721768724a.jpg!small)

![v2-795074b116ccf58026c5965a334b0808_720w.jpg](https://image.3001.net/images/20220414/1649910221_6257a1cdeddc9f2a9415c.jpg!small)

– 代码结构

![v2-95085eaefc1c6b4a47d4b22f833cf8a8_720w.jpg](https://image.3001.net/images/20220414/1649910222_6257a1ce3de788b31028e.jpg!small)

 **– RunController源码**

    
    
    package com.springrce.controller;
    import com.springrce.module.Feature;
    import org.springframework.web.bind.annotation.RequestMapping;
    import org.springframework.web.bind.annotation.RestController;
    @RestController
    public class RunController {
    @RequestMapping(“/VulEye”)
    public String Go(Feature feature){
    return “VulEye ” + feature.getFuture();
    }
    }

 **– Feature源码**

    
    
    package com.springrce.module;
    public class Feature {
    private String Future;
    private int lvl;
    public int getlvl(){
    return lvl;
    }
    public String getFuture(){
    return Future;
    }
    public void setlvl(int lvl){
    this.lvl = lvl;
    }
    public void setFuture(String Future){
    this.Future = Future;
    }
    }

 **– Web.xml修改**

    
    
    contextConfigLocation /WEB-INF/applicationContext.xml org.springframework.web.context.ContextLoaderListener
    dispatcher
    org.springframework.web.servlet.DispatcherServlet
    1
    dispatcher
    /

 **– dispatcher-servlet.xml修改**  
– Web文件结构调整

![v2-d7891c5bb106a0c00deb16a37b028fd0_720w.jpg](https://image.3001.net/images/20220414/1649910222_6257a1ce834f232a9cb18.jpg!small)

Index.jsp 放到page下面  
– Tomcat设置

![v2-fc097498db14fb15f61c9c5d33c0bcea_720w.jpg](https://image.3001.net/images/20220414/1649910222_6257a1cec3c62c5177e25.jpg!small)![v2-90220b50d1c6cd7cd333f36fe1d067fd_720w.jpg](https://image.3001.net/images/20220414/1649910223_6257a1cf05f56d78ee507.jpg!small)![v2-363a4c901fa28fb5a7981eefe97225b2_720w.jpg](https://image.3001.net/images/20220414/1649910223_6257a1cf446a4c4c7abaf.jpg!small)

这里使用 Tomcat 8.5.77  
– Tomcat Deployment里面添加Artifacts

![v2-968e5227c14bc59036e164e5c0eae742_720w.jpg](https://image.3001.net/images/20220414/1649910223_6257a1cf7a3e05d59aacd.jpg!small)

– 启动Tomcat然后进入测试网页  
http://localhost:8080/springrce_war_exploded/VulEye?Future=Better

![v2-1c2732622d8e974adbbff25458e2598b_720w.jpg](https://image.3001.net/images/20220414/1649910223_6257a1cfbc5f71a0a9a90.jpg!small)

显示Vuleye Better，则环境搭建成功  
-运行测试代码

![v2-b22f57e6ef0b47a27d8f994a12fa7741_720w.jpg](https://image.3001.net/images/20220414/1649910223_6257a1cff0051697de035.jpg!small)

查看Web根目录下是否出现shell.jsp

![v2-688f5bb7a827a699836c6a8cf0699118_720w.jpg](https://image.3001.net/images/20220414/1649910224_6257a1d03cff4cfdb179b.jpg!small)

– 浏览器打开链接http://localhost:8080/springrce_war_exploded/shell.jsp?cmd=calc  
弹出计算器

![v2-80a9b756749003aa842561d39dc871d5_720w.jpg](https://image.3001.net/images/20220414/1649910224_6257a1d0772a1de2c0b87.jpg!small)

 **– 复现成功！**

##  **Part5 漏洞细节**

 **1、基本原理参数绑定**  
目的是方便Web用户远程操作对象。  
源代码片段：

![v2-07b56430f429427b9961b361d391e31a_720w.jpg](https://image.3001.net/images/20220414/1649910224_6257a1d0c4b3d10ce973f.jpg!small)

返回一个VulEye字符串和feature.getFuture() 组合。而Future在链接中被参数绑定为Better.所以网页显示
VulEyeBetter。

2、当web用户访问对象属性时，Spring框架实现中的绑定过程（bindRequestParameters）会调用getCachedIntrospectionResults方法来获取和设置缓存中的对象属性。但是，getCachedIntrospectionResults方法的返回对象包含一个类对象。这意味着Web用户可以通过简单地提交URL来远程获取类对象比如VulEye?class。

3、将类对象暴露给Web用户是非常危险的，并且会在很多方面导致RCE。类加载器通常通过利用有效负载来动态加载一些敏感类以进行对象修改和代码执行。

4、获取RCE的一种简单方法是使用公开的类加载器来修改Tomcat日志配置，并在更改Tomcat日志配置后远程上传JSP Web
shell。下面展示了一个通过简单提交URL来更改Tomcat日志配置的示例。这是在公共PoC中针对SpringShell漏洞使用的利用方法。  
/VulEye?class.module.classLoader.resources.context.parent.pipeline.first.suffix=.jsp  
– 因此可以通过这种方式在Web根目录下写入*.jsp 文件后，通过URL访问进行RCE。

##  **Part6 修复建议**

升级Spring框架到最新版本；  
– 该漏洞仅在JDK9及以上版本才可以被触发，可以降低JDK版本至JDK8；  
– 升级Tomcat到最新版本；  
–
利用WAF、IPS等应用层的入侵检测设备，针对目前公开的EXP是通过POST上传jsp文件，参数中都带有class、classloader等字段，进行关键字过滤。

