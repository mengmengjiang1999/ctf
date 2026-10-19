****

## **​0x01 漏洞描述**

Ghostcat (幽灵猫 CNVD-2020-10487/CVE-2020-1938)
是由长亭科技安全研究员发现的存在于Tomcat中的安全漏洞，由于Tomcat AJP协议设计上存在缺陷，攻击者通过Tomcat AJP
Connector可以读取或包含Tomcat上所有webapp目录下的任意文件，例如可以读取webapp配置文件或源代码。此外在目标应用有文件上传功能的情况下，配合文件包含的利用还可以达到远程代码执行的危害。对于处在漏洞影响版本范围内的Tomcat而言，若其开启AJP
Connector且攻击者能够访问AJP Connector服务端口的情况下，即存在被Ghostcat漏洞利用的风险。注意AJP
Connector默认配置下即为开启状态，且监听在0.0.0.0:8009。

##  **0x02 影响范围**

  * Apache Tomcat 6

  * Apache Tomcat 7 < 7.0.100

  * Apache Tomcat 8 < 8.5.51

  * Apache Tomcat 9 < 9.0.31

##  **0x03 漏洞检测**

自行编写Java Web靶场并打包成war文件前注意在配置文件pom.xml中添加需要测试的tomcat版本。

![640?wx_fmt=jpeg](https://mmbiz.qpic.cn/mmbiz_jpg/xLk5PwibzMpQKp4Q7HUf4miatibCISSIyrJ7xvUdApslCXGia4geyqbHFlhRUX9G0IP7icEiasAvnhB50qwzibfC5ia6FA/640?wx_fmt=jpeg)

DockerFile如下所示。

![640?wx_fmt=jpeg](https://mmbiz.qpic.cn/mmbiz_jpg/xLk5PwibzMpQKp4Q7HUf4miatibCISSIyrJMTghDX7oJDHemmC8ugjC84h8Onl5lY8SYrz3nPtvybHePXWRsFs2ow/640?wx_fmt=jpeg)运行docker，这里除了8080端口还必须映射8009端口扫描成功建立在能与该端口通信的基础上，确认端口打开后使用xray服务扫描。![640?wx_fmt=jpeg](https://mmbiz.qpic.cn/mmbiz_jpg/xLk5PwibzMpQKp4Q7HUf4miatibCISSIyrJFaxD61jUXribFkIjibqutpPVzuepCLUGAejY0h09rQpeeMq8LTZBIrkA/640?wx_fmt=jpeg)

若xray成功扫描到漏洞，结果如下所示。

![640](https://mmbiz.qpic.cn/mmbiz_png/HUX0fjexBicfjGXHYvvawQUFfvOX3ibUWd7u8AdpskgEXZkH0AEoHw6KnTQictNWR66FjPKVjtbH6jJW82iba0DIYw/640)

##  **0x04 原理分析**

###  **AJP Connector**

Apache
Tomcat服文件务器通过Connector连接器组件与客户程序建立连接，Connector表示接收请求并返回响应的端点。即Connector组件负责接收客户的请求，以及把Tomcat服务器的响应结果发送给客户。AJP
(AJPv13)协议是定向包协议。出于性能考虑选择了二进制格式传输纯文本信息。它能减少Web服务器通过TCP连接与Servlet容器进行通信时，高开销套接字的创建，降低HTTP请求的处理成本。因此主要在需要集群、反向代理的场景被使用。因此AJP
Connector是Apache Tomcat为了优化性能而开发的采用AJPv13协议的Connector。客户端通过HTTP Connector和AJP
Connector能以两种方式访问服务器资源。![640](https://mmbiz.qpic.cn/mmbiz_png/0PPj0PlCdBMpB7Yn7MT3cjbYlaAvBwwM4nbL4f9nOXwz35LjqxRzsJMxibhthRfy3PAboZURnjNPXQWBR3t9OUA/640)

###  **漏洞代码**

修复前的apache-tomcat-9.0.30-src代码中的问题函数关键部分如下所示，省略部分代码仅以注释形式保留。红框标注部分的代码未经过任何数据清洗就将数据传入。

![640?wx_fmt=jpeg](https://mmbiz.qpic.cn/mmbiz_jpg/xLk5PwibzMpQKp4Q7HUf4miatibCISSIyrJSgrjrMqolLcCbzs91M6lwwPZCHHKnAXtJDyrwQricq6O2nib10smUnmA/640?wx_fmt=jpeg)

执行到包含漏洞代码的 else 的条件是：  

  * n不等于Constants.SC_A_REQ_LOCAL_ADDR即AJP_LOCAL_ADDR

  * n不等于Constants.SC_A_REQ_REMOTE_PORT即AJP_REMOTE_PORT

  * n不等于Constants.SC_A_SSL_PROTOCOL即AJP_SSL_PROTOCOL

红框标记处的request.setAttribute和request.getAttribute二者配对使用，因为AJP实现代码未对输入数据进行清理，所以通信时DefaultServlet中的getRelativePath函数多次调用request.getAttribute的函数，将会取出不可信的数据。![640?wx_fmt=jpeg](https://mmbiz.qpic.cn/mmbiz_jpg/xLk5PwibzMpQKp4Q7HUf4miatibCISSIyrJHjlN5eM3JDEI1KJu9icmkAwMrdW1LMCnBTsYQxFKzdcNXEw9dg8SIEA/640?wx_fmt=jpeg)

黑客可以通过控制javax.servlet.include.request_uri、javax.servlet.include.path_info、javax.servlet.include.servlet_path
这三个属性的值构造 payload 进行攻击。

###  **任意文件读取**

通信时通过一系列调用最终在serveResource函数中调用了包含request.getAttribute的getResource，因为变量path是黑客可以控制的变量，所以在执行resources.getResource(path)时可以造成任意文件读取。![640?wx_fmt=jpeg](https://mmbiz.qpic.cn/mmbiz_jpg/xLk5PwibzMpQKp4Q7HUf4miatibCISSIyrJq0CaLDutrukfIh0bDKibiahvQKTyMiaibaztSfA58pDb6ZNkXZyWKd9Klw/640?wx_fmt=jpeg)

###  **任意代码执行**

通信时在调用了包含request.getAttribute的service，因为变量jspUri是黑客可以控制的变量，所以在执行serviceJspFile(request,
response, jspUri, precompile)时，若服务器碰巧能上传文件，黑客则可以通过上传包含shell的jsp文件达到任意代码执行的目的。

![640?wx_fmt=jpeg](https://mmbiz.qpic.cn/mmbiz_jpg/xLk5PwibzMpQKp4Q7HUf4miatibCISSIyrJo3QpK1JEDkSRaNmB4ISH08DwrEoUICBJLqWx2SedUiarGx9Nb4yhUfw/640?wx_fmt=jpeg)

##  **0x05 参考资料**

1\. <https://www.chaitin.cn/zh/ghostcat>

2\. <https://www.anquanke.com/post/id/199351>3\.
<https://www.anquanke.com/post/id/199448>4\.
<http://archive.apache.org/dist/tomcat/>

