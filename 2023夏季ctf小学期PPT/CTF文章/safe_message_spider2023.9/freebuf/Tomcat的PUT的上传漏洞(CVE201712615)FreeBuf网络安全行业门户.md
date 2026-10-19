原创： free雅轩  合天智汇

近期在项目中碰到的ApacheTomcat中间件愈来愈多，于是乎。想着做一个整理。将ApacheTomcat中间件的几大较为重要的高危漏洞做一个总结整理复现。用作来巩固更新自己的知识库。

在这里感谢公司Bearcat师傅和残忆师傅以及李师傅等指导和共享精神。

首先我们先来了解以下Tomcat的概念：

Tomcat是我们在工作中所使用的一款开源轻量级的Web应用程序服务器。通常情况下在中小型系统或者并发量较小的场合下使用，常用来与JSP和PHP脚本结合使来解析脚本语言部署搭建网站等系统。

在这里我们将Tomcat的几大高危漏洞整理至以下：

1、Tomcat后台弱口令上传war包

2、Tomcat的PUT的上传漏洞(CVE-2017-12615)

3、Tomcat反序列化漏洞(CVE-2016-8735)

4、Tomcat之JMX服务弱口令漏洞

5、Tomcat 样例目录session操控漏洞

6、Tomcat本地提权漏洞(CVE-2016-1240)

7、Tomcat win版默认空口令漏洞(CVE-2009-3548)

接着上一篇的弱口令上传war包getsehll后（[Tomcat后台弱口令上传war包漏洞复现](http://mp.weixin.qq.com/s?__biz=MjM5MTYxNjQxOA==&mid=2652848895&idx=1&sn=8367abae0a4407084664d2c9af981e47&chksm=bd593e328a2eb724ac00369835737de2c89ad7021cea8916c61b670a4a0a2909a07960aa176a&scene=21#wechat_redirect)），我们再来看第二篇put方法的上传漏洞之getshell。

漏洞详情：

  

  
![图片.png](https://image.3001.net/images/20181018/1539842461_5bc8219d04970.png!small)  

可以看到17年时官方爆出Tomcat的CVE-2017-12615漏洞。说的就是ApacheTomcat服务组件中开启了http的Put方法所造成的攻击者可以利用该方法任意上传jsp木马所造成的远程代码执行漏洞。该漏洞所影响的版本从ApacheTomcat7.0.0-7.0.79

漏洞所需环境：

Tomcat7.0.79（开启Put方法）

JDK1.8.0

看到有朋友留言说是找不到tomcat的复现环境包。在这里写下我的方法。

直接在搜索引擎搜索“tomcat
indexof”去检索tomcat的官方文件镜像站点，在里面下载。其他的一些类似的struts等资源也是同理搜索。总而言之，就是善用googlehack语法。

![图片.png](https://image.3001.net/images/20181018/1539842475_5bc821ab8e540.png!small)  

下载好环境包并且搭建好之后我们就可以着手复现了。

  
![图片.png](https://image.3001.net/images/20181018/1539842486_5bc821b672f4a.png!small)  

这里强调一点，windows环境下载源码在bin目录，而Linux环境则在src源代码目录文件中下载。如果需要同时搭建运行多个tomcat版本的化，则需要更改tomcat/conf/server.xml中的三处默认端口。

1、第22行：

[code]

<Serverport="8005" shutdown="SHUTDOWN">

[/code]

8005为tomcat的远程停止服务的端口。

2、第71-73行：

[code]

<Connectorport="8080" protocol="HTTP/1.1"

connectionTimeout="20000" redirectPort="8443" />

[/code]

8080为Tomcat服务的HTTP协议端口，8443为HTTPS端口

3、第93行：

[code]

<Connectorport="8009" protocol="AJP/1.3"redirectPort="8443" />

[/code]

8009为Tomcat服务的AJP端口。

如果运行多个版本的tomcat服务则需要针对每个版本的这三个端口进行修改。修改8005以及8080/8443和8099为其他没被占用的端口。以及不同版本的Tomcat需要不同的JDK来进行运行。

搭建好之后我们需要先进行设置一下在HTTP请求中开启Put方法。在conf/web.xml文件中将readonly初始化参数由默认值设置为false。即可成功开启Put方法。

  
![图片.png](https://image.3001.net/images/20181018/1539842497_5bc821c193c24.png!small)  

根据上图注释信息我们可以得知默认情况下是禁止http请求中的上传（PUT）和删除（DELETE）方法的。在这里我们在配置文件给他加入这样一行。开启他的PUT方法。

[CODE]

<init-param>

<param-name>readonly</param-name>

<param-value>false</param-value>

</init-param>

[/CODE]

![图片.png](https://image.3001.net/images/20181018/1539842507_5bc821cb95dee.png!small)  

设置完成后，即可重启tomcat服务，来转包利用PUT方法上传木马。我们先来测试一下：

  
![图片.png](https://image.3001.net/images/20181018/1539842515_5bc821d3db554.png!small)  

上传成功。接下来就不言而喻了。

![图片.png](https://image.3001.net/images/20181018/1539842524_5bc821dc532f5.png!small)  

当然，为了方便。一般情况下我们直接使用EXP快速利用。在这里贴上Bearcat师傅的CVE-2017-12615的EXP下载地址。https://github.com/iBearcat/CVE-2017-12615

  
![图片.png](https://image.3001.net/images/20181018/1539842532_5bc821e46f861.png!small)  

修复方案：

1、配置readonly和VirtualDirContext值为True或注释参数，禁止使用PUT方法并重启tomcat

注意：如果禁用PUT方法，对于依赖PUT方法的应用，可能导致业务失效。

2、根据官方补丁升级最新版本

  

  

