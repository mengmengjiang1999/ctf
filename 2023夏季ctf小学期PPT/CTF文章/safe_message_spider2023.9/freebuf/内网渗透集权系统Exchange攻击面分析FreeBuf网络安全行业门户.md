## 前言

当我们通过漏洞或者其它的攻击方式进入内网以后，除了做权限维持以外，最可能做的就是拿下内网内的集权系统，如域控，邮箱服务器等。今天就来看看针对邮箱服务器如何去利用。

Exchange在域内有着重要的地位,一般来说,拿到Exchange服务器的权限,基本等同于拿到域管的权限。因此它又是内网选手重点关注对象。

这是内网方面的第七篇文章，关于内网前面的几篇文章如下，大家感兴趣的可以去看看：

[内网渗透：Kerberos认证协议安全性分析](../articles/network/371028.html)

[内网横移：抓取域管理员密码](../articles/web/370338.html)

[内网渗透：详解kerberoast攻击](../articles/network/371446.html)

[内网渗透：详解Responder利用方式](../articles/network/371863.html)

[内网渗透：NTML认证与PTH攻击](../articles/network/372482.html)

[内网渗透：MS14-068原理以及利用](../articles/network/373088.html)

 **由于本人水平有限，文章中可能会出现一些错误，欢迎各位大佬指正，感激不尽。如果有什么好的想法也欢迎交流~~**

## Exchange简介

Exchage就是我们常说的邮箱服务器。Exchange是由微软推出的用于企业环境中部署的邮件服务器。微软对外发布的第一个Exchange版本是Exchange
4.0，最开始Exchange使用X.400目录服务，随后转向使用微软的活动目录，最开始的时候微软还提供了Microsoft Exchange
Client，即Exchange邮件客户端，随后被Outlook取代

## 如何确认邮箱服务器的位置

1）根据DNS解析的MX去判断

MX（Mail
Exchanger）记录是邮件交换记录，它指向一个邮件服务器，用于电子邮件系统发邮件时根据收信人的地址后缀来定位邮件服务器。一句话来说就是MX记录的作用是给寄信者指明某个域名的邮件服务器有哪些。

因此在内网内也可以通过这种方式去判断邮箱服务器的IP。

可以使用dig，nslookup等命令查询域名的mx记录，下面以baidu为例，在内网中查询时，一般获取到的是内网IP。

![1692857919_64e6f63f0ce84690edb15.png!small?1692857919940](https://image.3001.net/images/20230824/1692857919_64e6f63f0ce84690edb15.png!small?1692857919940)

  

2）通过SPN定位

关于SPN前面的文章已经说过了，域内可以通过查询SPN来查找相关的服务。命令如下

    
    
    setspn -Q IMAP/*

3）通过扫描端口来判断，这种方式一般不推荐，因为涉及的网段比较多

4）通过Exchange的漏洞也有可能泄露服务器的IP，下面会有介绍。

  

## Exchange与outlook的关系

我们日常工作中接触比较多的应该就是Outlook的，用来收发邮件，那么outlook与exchange又有什么关系？

 **Exchage是我们常说的邮件服务器，负责的邮件的接受和发送**

 **Outlook是邮件客户端，直接面向用户，负责从邮件服务器拉取邮件或者发送邮件到邮件服务器。**

Exchange是由微软推出的用于企业环境中部署的邮件服务器。微软对外发布的第一个Exchange版本是Exchange
4.0，最开始Exchange使用X.400目录服务，随后转向使用微软的活动目录，最开始的时候微软还提供了Microsoft Exchange
Client，即Exchange邮件客户端，随后被Outlook取代

### 客户端与服务器接收邮件的方式

邮件通信分为邮件发送和邮件接收，其中邮件发送使用统一的通信协议，即SMTP，而邮件的收取则有多种协议标准，如由早期的POP发展至今的POP3，如今使用广泛的IMAP，Exchange开发了私有的MAPI协议用于收取邮件，较新版本的Outlook通常使用MAPI与Exchange进行交互，除此之外早期的Outlook还使用称为Outlook
Anywhere的RPC交互。下面介绍Exchange提供支持的访问接口和协议。

## Exchange提供支持的访问接口和协议

### Outlook Web App（OWA）

Exchange提供的Web邮箱，地址通常为 [http://DOAMIN/owa/](http://doamin/owa/)

### Exchange Administrative Center（ECP）

Exchange管理中心，管理员用于管理组织中的Exchange的Web控制台，地址通常为
[http://DOMAIN/ecp/](http://domain/ecp/)

### Exchange Web Service（EWS，SOAP-over-HTTP）

Exchange提供了一套API编程接口可供开发者调用，用于访问Exchange服务器，与邮件、联系人、日历等功能进行交互和管理操作，在Exchange
Server 2007中被提出。微软基于标准的Web Service开发EWS，EWS实现的客户端与服务端之间通过基于HTTP的SOAP交互。

  

## Exchange功能和服务

下面介绍一下Exchange邮件的一些常用功能。

### 自动发现（Autodiscover）

Autodiscover自动发现是自Exchange Server
2007开始推出的一项自动服务，用于自动配置用户在Outlook中邮箱的相关设置，简化用户登陆使用邮箱的流程。如果用户账户是域账户且当前位于域环境中，通过自动发现功能用户无需输入任何凭证信息即可登陆邮箱。自动发现服务运行于客户端访问服务器（Client
Access Server）上，其实质是Outlook客户端通过LDAP查询、DNS查询等，连接到指定域的Exchange的客户端访问服务器（Client
Access Server）上。

自动发现的过程首先需要获取自动配置文件，然后根据配置文件进行连接和配置，获取自动配置文件的过程不展开细说了，简单来说它将找到提供自动发现服务的客户端访问服务器、访问/autodiscover/autodiscover.xml获得配置文件。

这里有个关键地方，即正确配置DNS解析，使得Outlook客户端不管是在域环境主机上还是外部网络环境，都可以正确找到自动发现服务所在的服务器。

### 全局地址列表（GAL）

地址列表（Address
List）记录了用户在域活动目录中的基本信息和在Exchange中的邮箱地址，用于将用户在活动目录中的属性对象与邮件地址形成关联。在Exchange中管理员可以创建不同的地址列表，用于方便管理维护组织，也方便邮箱用户通过地址列表查找特定的联系人邮箱，Exchange默认会创建一些内置的地址列表，其中包含了一个Default
Global Address List（默认全局地址列表），所有邮箱用户都会被加入到这个地址列表中。

## Exchage攻击方式

上面了解了Exchange的一些基本知识，下面就来看看Exchage有哪些攻击面。

拿到内网机器以后，一般需要获取用户密码才能进行下一步的利

