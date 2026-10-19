## **0x01 概述**

 **Apache Tomcat** 是一个开源的Java Servlet容器和JavaServer
Pages（JSP）容器。它是由Apache软件基金会开发和维护的，是一个轻量级、快速、可扩展的Web服务器，用于执行Java
Servlet和JavaServer Pages技术。

Tomcat是一个独立的服务器，它可以用作Java应用程序的Web服务器，也可以作为Servlet容器集成到其他Web服务器（例如Apache
HTTP服务器）中。它可以处理HTTP请求，并将它们传递给相应的Servlet或JSP进行处理，然后将结果返回给客户端。

Tomcat提供了许多功能，包括 **连接池、会话管理、安全性、Web应用程序部署、负载均衡等**
。它是Java企业级Web应用程序的常用部署环境，广泛用于开发和部署Java Web应用程序和服务。

笔者通过对数百个真实项目引入组件的分析选出了Tomcat组件的常见漏洞进行分析。本次分析的是 **CVE-2017-5648** 。该漏洞是Tomcat-catalina组件处理访问错误资源请求时，如404，500，此时若服务器存在自定义的错误页面则会将请求交给DefaultServlet处理，从而可能导致错误页面被重写。

##  **0x02 组件使用场景**

Tomcat-catalina组件负责处理HTTP请求、响应、会话管理、Servlet容器、连接池、线程池等核心功能，是Tomcat服务器的
**核心引擎** 。

##  **0x03 漏洞信息**

###  **3.1 漏洞简介**

 **漏洞名称：** 安全限制绕过漏洞

 **漏洞编号：** CVE-2017-5664

 **漏洞类型：** CWE-755 异常情况处理不当

###  **CVSS评分：** CVSS v3.1：7.5

 **漏洞危害等级：** 高危

###  **3.2 漏洞概述**

该漏洞是Tomcat-catalina组件处理访问错误资源请求时，如404，500，此时若服务器存在自定义的错误页面则会将请求交给DefaultServlet处理，从而可能
**导致错误页面被重写** 。

###  **3.3 漏洞利用条件**

DefaultServlet的readOnly属性为false（默认为true）。并且当存在自定义的静态文件形式的错误页面时，可以覆盖错误页面。

###  **3.4 漏洞利用条件**

Apache Tomcat 9.0.0.M1 ~ 9.0.0.M20

Apache Tomcat 8.5.0 ~ 8.5.14

Apache Tomcat 8.0.0.RC1 ~ 8.0.43

Apache Tomcat 7.0.0 ~ 7.0.77

###  **3.5 漏洞分析**

Tomcat的核心功能有两个，其中连接器负责监听网络端口，接收和响应网络请求，并将收到的网络字节流转换成 Tomcat Request 再转成标准的
ServletRequest 给容器，同时将容器传来的 ServletResponse 转成 Tomcat Response
再转成网络字节流。而容器有一个引擎可以管理多个虚拟主机。每个虚拟主机可以管理多个 Web 应用。每个 Web 应用会有多个 Servlet
包装器。Engine、Host、Context 和 Wrapper，四个容器之间属于父子关系。

![图片](https://image.3001.net/images/20230810/1691650577_64d48a11f375005574d13.png!small)

最后实际处理请求的是Servlet的Service方法，其会根据请求方法进行处理函数的派遣。

![图片](https://image.3001.net/images/20230810/1691650586_64d48a1aee6eafc0e2db9.png!small)

根据Tomcat官方文档，DefaultServlet是服务静态资源的。

其配置在$CATALINA_BASE/conf/web.xml文件中，其readonly属性默认为true，意味着HTTP请求方法的PUT或DELETE是被拒绝的。

![图片](https://image.3001.net/images/20230810/1691650596_64d48a24e978878716334.png!small)

从其代码中也可以看出，如果ReadOnly为true，会返回错误代码403。

![图片](https://image.3001.net/images/20230810/1691650605_64d48a2d92d344bdeeb0b.png!small)

当请求一个错误页面，比如不存在的页面的时候，该请求会被重定向到错误页面，如下图被重定向到了我们的错误页面404.html。

![图片](https://image.3001.net/images/20230810/1691650613_64d48a3535466b55d041e.png!small)

此时应该按照GET请求进行处理，但是却保留了原先的请求方法，分配到了doPUT函数，因而配置的404.html页面会在DefaultServlet.java:546
resources.wirte()执行后被覆盖。

![图片](https://image.3001.net/images/20230810/1691650621_64d48a3d5477efa37e464.png!small)

###  **3.6 漏洞复现**

修改Tomcat目录下conf/web.xml的DefaultServlet配置如下：

![图片](https://image.3001.net/images/20230810/1691650628_64d48a44ae6c4164162c4.png!small)

随后配置自定义的静态错误页面：

![图片](https://image.3001.net/images/20230810/1691650636_64d48a4c331a43ed8ff32.png!small)

此时访问错误页面，返回this is an error page!

![图片](https://image.3001.net/images/20230810/1691650644_64d48a542bd87455f20a7.png!small)

使用PUT方法请求错误页面。

![](https://image.3001.net/images/20230810/1691650804_64d48af4244b344c9568c.png!small)

DefaultServlet调用doPUT方法对404.html文件进行了写入。

![图片](https://image.3001.net/images/20230810/1691650651_64d48a5b077c7f466d113.png!small)

再次请求发现默认的错误页面已被更改。

![图片](https://image.3001.net/images/20230810/1691650658_64d48a62005bee3af5d74.png!small)

###  **3.7 修复方法**

漏洞修复的办法有如下几种：

  *  **升级Tomcat至该漏洞不存在的版本**

更新 Apache Tomcat >= 9.0.0.M21

更新 Apache Tomcat >= 8.5.15

更新 Apache Tomcat >= 8.0.44

更新 Apache Tomcat >= 7.0.78

Tomcat官方的修复方案是在Service方法中多了一次验证，如果是因为错误转发过来的则当作GET处理请求。

![图片](https://image.3001.net/images/20230810/1691650664_64d48a68dff5aa36d8063.png!small)

  

修复版本可从Tomcat官网下载：

https://tomcat.apache.org/

  *  **修改web.xml配置**

将DefaultServlet的ReadOnly属性设置为true，让该Servlet拒绝PUT，DELETE请求。

  *  **更改自定义错误页面文件类型**

静态的请求才会由DefaultServlet，也就.html文件。如果自定义的错误页面为404.jsp，就会由jspServlet对转发的请求进行处理。

