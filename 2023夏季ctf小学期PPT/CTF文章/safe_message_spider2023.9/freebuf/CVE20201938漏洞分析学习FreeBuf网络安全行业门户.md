## 一、环境搭建

环境搭建这部分直接使用brew包管理器进行Tomcat安装，版本为8.5.47如下图所示：

![image-20200309132012150.png](https://image.3001.net/images/20200408/1586316995_5e8d46c350612.png!small)

与IDEA进行远程调试的设置部分略过，搭建完成后查看端口开启状况如下图所示：

![image-20200309140540104](https://image.3001.net/images/20200408/1586317018_5e8d46da4ce1b.png!small)

## 二、AJP协议学习

既然CVE-2020-1938漏洞是通过Tomcat的AJP协议进行攻击，那么首先应先对AJP协议进行学习，了解它是啥、用来干啥的。

这里附上Apache官网上对于AJP协议部分的[AJP官方文档](http://tomcat.apache.org/connectors-doc/ajp/ajpv13a.html)。

![图1](https://image.3001.net/images/20200408/1586317041_5e8d46f1d3324.png!small)

![image-20200309153110663](https://image.3001.net/images/20200408/1586317049_5e8d46f9be412.png!small)

![image-20200309153226998](https://image.3001.net/images/20200408/1586317055_5e8d46ffe8ab3.png!small)

通过阅读官方文档与server.xml文档后可知，Tomcat服务器对外监听两个端口用于与客户端进行正常的访问通信，如上图所示，分别监听8080端口与8009端口，其中8080端口为我们所熟知的正常进行HTTP协议通信的端口，8009端口则是使用AJP协议进行通信，使用二进制格式来传输可读性文本，能降低
HTTP 请求的处理成本，因此主要在需要集群、反向代理的场景被使用。

![image-20200309154433958](https://image.3001.net/images/20200408/1586317067_5e8d470b12d09.png!small)

通过阅读文档可知AJP协议的请求报文结构、Headers的定义方式、属性的代码值等等，这部分在接下来的漏洞代码分析中还会再回来查找。

## 三、漏洞分析

漏洞分析这一块是跟着最早放出的[安恒 Tomcat-Ajp协议漏洞分析](https://mp.weixin.qq.com/s/GzqLkwlIQi_i3AVIXn59FQ)文章做的，个人对该分析文章进行学习与漏洞细节补充，下载[Tomcat源码](https://repo1.maven.org/maven2/org/apache/tomcat/tomcat-coyote/8.5.47/tomcat-coyote-8.5.47-sources.jar)进行分析。

定位到漏洞核心代码部分在`org.apache.coyote.ajp.AjpProcessor.java`文件的778~812行，如下所示：

![image-20200309160031514](https://image.3001.net/images/20200408/1586317077_5e8d471589c2e.png!small)

首先，对第一个红框位置代码进行分析，先为`attributeCode`进行赋值后将比较结果作为循环条件；在`Constants.java`文件中查询到`Constants.SC_A_ARE_DONE的值为0XFF`，在官方手册中查询到属性代码为请求终止，则这是个恒True的判断，循环执行下面的`switch`判断代码。

![image-20200309165711327](https://image.3001.net/images/20200408/1586317114_5e8d473aa8b33.png!small)

对第二个红框位置代码进行分析，当case到`Constants.SC_A_REQ_ATTRIBUTE`时会进入下面的判断，那么这个`Constants.SC_A_REQ_ATTRIBUTE`又是什么呢？在`Constants.java`中查找到`SC_A_REQ_ATTRIBUTE
= 10;`同时还有一行注释声明此用于不在上面列表中的属性。

![image-20200309170909074](https://image.3001.net/images/20200408/1586317126_5e8d4746a1f10.png!small)

继续返回官网手册进行查找，果然在官网的属性说明中存在着如下图所示的声明。也就是说，如果要发超出上述基础属性以外的值，都可以通过`req_attribute(0X0A)`来设置其属性名和值来发送。

![image-20200309171219577](https://image.3001.net/images/20200408/1586317134_5e8d474e1455c.png!small)

那么第三个红框部分的代码的含义就已经显而易见了，我们可以将AJP里面的内容取出来设置成`request`对象的`Attribute`属性。

在上面部分设置完成`request`对象之后一直没搞清楚是怎么传进容器的，直到看到了[浅析Tomcat之CoyoteAdapter](https://blog.csdn.net/iteye_14395/article/details/82541196)这篇文章：

>
> Adapter连接了Tomcat连接器Connector和容器Container.它的实现类是CoyoteAdapter主要负责的是对请求进行封装,构造Request和Response对象.并将请求转发给Container也就是Servlet容器.

![image-20200309184100650](https://image.3001.net/images/20200408/1586317147_5e8d475b8189a.png!small)

终于将安恒漏洞分析文章中的`getAdapter().service(request,response)`串联起来，到这里之后还需要注意Servlet的处理，可以在`web.xml`中看到在其中配置了两个`servlet`处理，`DefaultServlet`和`JSP
Servlet`，越精确的路径越优先匹配，而`/`匹配所有，匹配程度模糊所以优先级最低，当其它的`Servlet`匹配不成功时便由DefaultServlet来进行兜底。

![image-20200309174035651](https://image.3001.net/images/20200408/1586317170_5e8d47720603d.png!small)

跟进Tomcat_lib中`DefaultServlet.class`文件，通过`serveResource`方法来获取资源文件。

![image-20200309191305368](https://image.3001.net/images/20200408/1586317178_5e8d477a60e8d.png!small)

通过`getRelativePath`来获取资源文件路径。

![image-20200309191606961](https://image.3001.net/images/20200408/1586317187_5e8d4783edf32.png!small)

然后再通过控制ajp控制的上述三个属性来读取文件,通过操控上述三个属性从而可以读取到/WEB-INF下面的所有敏感文件，不限于class、xml、jar等文件。

参考文章均在笔记中以超链接形式添加，第一次进行Java漏洞分析多有不足还望包涵= =

  

