**作者：斗象能力中心 TCC – Cody  
来源：[https://blog.riskivy.com/exchange-server-in-pentest/?from=timeline&isappinstalled=0](https://blog.riskivy.com/exchange-server-in-pentest/?from=timeline&isappinstalled=0)**

**前言：**

在渗透测试中，往往会遇到企业内网环境中使用的一些常用组件，这些组件对内或对外提供了服务与接口，也给渗透测试人员与黑客提供了新的可尝试的攻击面，合理的利用组件服务提供的功能和接口，可以帮助渗透测试人员完成信息收集、环境侦测，甚至通过其漏洞弱点、配置缺陷、功能滥用直接拿下权限，在渗透测试与后渗透阶段达到事半功倍的效果。

Windows Exchange
Server，应该是国内外应用都非常广泛的邮件服务器了，本文将围绕Exchange展开，介绍在渗透测试中对Exchange服务器的攻击利用。

正式开始之前，我们先对Exchange相关的一些概念与基础知识进行梳理简介，便于对Exchange有简单初步的了解。

**本文实验环境:**

  * 域环境：fb.com
  * 域控：10.0.83.93，masterdc，Windows 2012 R2
  * Exchange服务器：10.0.83.94，test2k12，Windows 2012 R2，安装Exchange Server 2013 SP1
  * 域内工作机：10.0.83.80，testwin7，Windows 7，安装Outlook 2013 SP1

## **一、初识Exchange**

> Microsoft Exchange Server is a mail server and calendaring server developed
> by Microsoft. It runs exclusively on Windows Server operating systems. ——
> wikipedia

如维基百科对Exchange
Server的描述，Exchange是由微软推出的用于企业环境中部署的邮件服务器。微软对外发布的第一个Exchange版本是Exchange
4.0，最开始Exchange使用X.400目录服务，随后转向使用微软的活动目录，最开始的时候微软还提供了Microsoft Exchange
Client，即Exchange邮件客户端，随后被Outlook取代，时至今日，微软已经发布了10个大版本号的Exchange，今年10月份，微软推出了最新版本的Exchange
Server 2019。在不同的企业环境中部署使用的Exchange版本不一，各版本提供的架构、功能、服务、接口都各有不同，本文将以Exchange
Server 2013为例展开叙述。

Exchange Server是一种本地化部署的形式，除此之外还有以SaaS的在线服务模式，这两种部署模式即各种文档或资料中常说的Exchange On-premise和Exchange Online，另外，Exchange还支持本地化部署与云端部署共存的部署方式，即混合部署（Exchange
Hybrid）。

### **1.邮件服务器角色（Server Role）**

Exchange是一个功能完整而庞大的邮件服务器，实际上Exchange背负的不仅仅是传统的邮件收发处理、邮件路由等基本的邮件功能，在微软背景下Exchange与活动目录域服务、全局编排目录及其他微软相关服务和组件也有着众多联系。Exchange邮件服务器在企业环境中使用占比非常高，其通过划分不同的服务器角色、执行各自的组件和服务以及相互之间的依存调用使得邮件处理形成一个强大、丰富、稳定、同时又复杂的过程。Exchange在逻辑上分为三个层次：网络层（network
layer）、目录层（directory layer）、消息层（messaging layer），服务器角色正是在消息层上的一个细分。

Exchange Server 2013包含三个服务器角色，我们往前推进一个版本到Exchange Server
2010，来介绍Exchange服务器角色的演变和功能简述。

Exchange Server 2010包含五个服务器角色，分别是邮箱服务器（mailbox server）、集线传输服务器（hub transport
server）、客户端访问服务器（client access server）、边缘传输服务器（edge transport
server）、统一消息服务器（unified messaging
server），除了边缘传输服务器以外其他角色都可以在同一台主机上进行部署添加，其中邮箱服务器、集线传输服务器、客户端访问服务器是核心服务器角色，部署这三个角色就能提供基本的邮件处理功能。

  * **邮箱服务器（mailbox server）** ：该角色是提供托管邮箱、公共文件夹以及相关的消息数据（如地址列表）的后端组件，是必选的服务器角色。
  * **客户端访问服务器（client access server）** ：接收和处理来自于不同客户端的请求的中间层服务器角色，该角色服务器提供了对使用不同协议进行访问的支持，每个Exchange环境中至少需要部署一个客户端访问服务器，客户端访问服务器提供了对以下不同接口访问Exchange服务器的处理。

    
    
    MAPI访问
    POP3和IMAP4访问
    Outlook Web App访问（OWA）
    Outlook Anywhere访问
    Autodiscover自动发现服务
    可用性服务

  * **集线传输服务器（hub transport server）** ：或称中心传输服务器，该服务器角色的核心服务就是Microsoft Exchange Transport，负责处理Mail Flow（这又是Exchange中的一大知识点，Exchange管理员需要通过MailFlow实现邮件出站与进站配置）、对邮件进行路由、以及在Exchange组织中进行分发，该服务器角色处理所有发往属于本地邮箱的邮件和发往外部邮箱的邮件，并确保邮件发送者和接收者的地址被正确解析并执行特定策略（如邮件地址过滤、内容过滤、格式转换等），同时，还可以进行记录、审计、添加免责声明等，正如Hub transport的含义，该服务器角色相当于一个邮件传输的中继站点，每个Exchange环境中至少需要部署一个集线传输服务器。
  * **统一消息服务器（unified messaging server）** ：将专用交换机（private branch exchange/PBX） 和Exchange Server集成在一起，以允许邮箱用户可以在邮件中发送存储语音消息和传真消息，可选角色。
  * **边缘传输服务器（edge transport server）** ：该服务器角色作为专用服务器可以用于路由发往内部或外部的邮件，通常部署于网络边界并用于设置安全边界。其接受来自内部组织的邮件和来自外部可信服务器的邮件，然后应用特定的反垃圾邮件、反病毒策略，最后将通过策略筛选的邮件路由到内部的集线传输服务器，可选角色。

在Exchange Server
2013中，服务器角色精简为三个，分别是邮箱服务器、客户端访问服务器和边缘传输服务器，其中邮箱服务器角色和客户端访问服务器角色通常被安装在同一台服务器中。

  * **邮箱服务器** ：负责认证、重定向、代理来自外部不同客户端的访问请求，主要包含客户端访问服务（Client Access service）和前端传输服务（Front End Transport service）两大组件。
  * **客户端访问服务器** ：托管邮箱、公共文件夹等数据，主要包含集线传输服务（Hub Transport service）和邮箱传输服务（Mailbox Transport service）两大组件服务。
  * **边缘传输服务器** ：负责路由出站与入站邮件、策略应用等。

在Exchange Server 2016和2019中，只有两种服务器角色，分别是邮箱服务器和边缘传输服务器，所有关键角色和组件都融入到邮箱服务器中。

### **2.客户端/远程访问接口和协议**

邮件通信分为邮件发送和邮件接收，其中邮件发送使用统一的通信协议，即SMTP，而邮件的收取则有多种协议标准，如由早期的POP发展至今的POP3，如今使用广泛的IMAP，Exchange开发了私有的MAPI协议用于收取邮件，较新版本的Outlook通常使用MAPI与Exchange进行交互，除此之外早期的Outlook还使用称为Outlook
Anywhere的RPC交互。下面介绍Exchange提供支持的访问接口和协议。

**Outlook Web App（OWA）**

Exchange提供的Web邮箱，地址通常为 <http://DOAMIN/owa/>

![img](https://images.seebug.org/content/images/2018/12/28/1545976334000-1-2.png-w331s)

**Exchange Administrative Center（ECP）**

Exchange管理中心，管理员用于管理组织中的Exchange的Web控制台，地址通常为 <http://DOMAIN/ecp/>

![img](https://images.seebug.org/content/images/2018/12/28/1545976334000-7-3.png-w331s)

**Outlook Anywhere（RPC-over-HTTP，RPC/HTTP）**

前身为RPC-over-HTTP，随后在Exchange 2007和Exchange 2010中被重命名为Outlook Anywhere。RPC-over-HTTP是在Exchange
2003被提出的，在此之前，外网用户使用Exchange邮箱需要先通过VPN连接到企业内部网络中，随后微软在Outlook中推出新特性Outlook
Anywhere，外网用户可以直接通过Outlook
Anywhere连接使用Exchange邮箱而无需使用VPN，内网用户则通过RPC协议连接使用Exchange。从Exchange
2013开始，Outlook不再区分内外网环境，统一使用Outlook Anywhere，同时，不需要开放单独的RPC端口。Outlook
Anywhere在Exchange Server 2013中默认开启。

在Outlook中使用RPC-over-HTTP的连接方式连接Exchange（在协议中显示为RPC/HTTP）：

![img](https://images.seebug.org/content/images/2018/12/28/1545976334000-2-2.png-w331s)

**MAPI（MAPI-over-HTTP，MAPI/HTTP）**

一种Outlook与Exchange交互的新的传输协议，于Exchange 2013 SP1和Outlook 2013 SP1中被提出。

在Outlook中使用MAPI-over-HTTP的连接方式连接Exchange（在协议中显示为HTTP）：

![img](https://images.seebug.org/content/images/2018/12/28/1545976335000-3-2.png-w331s)

**Exchange ActiveSync（EAS，XML/HTTP）**

ActiveSync是一种允许用户通过移动设备或其他便携式设备访问和管理邮件、联系人、日历等Exchange功能的同步协议，在Windows上使用时其进程名称为wcesomm.exe。

**Exchange Web Service（EWS，SOAP-over-HTTP）**

Exchange提供了一套API编程接口可供开发者调用，用于访问Exchange服务器，与邮件、联系人、日历等功能进行交互和管理操作，在Exchange
Server 2007中被提出。微软基于标准的Web Service开发EWS，EWS实现的客户端与服务端之间通过基于HTTP的SOAP交互。

### **3.Exchange功能和服务**

**自动发现（Autodiscover）**

Autodiscover自动发现是自Exchange Server
2007开始推出的一项自动服务，用于自动配置用户在Outlook中邮箱的相关设置，简化用户登陆使用邮箱的流程。如果用户账户是域账户且当前位于域环境中，通过自动发现功能用户无需输入任何凭证信息即可登陆邮箱。自动发现服务运行于客户端访问服务器（Client
Access Server）上，其实质是Outlook客户端通过LDAP查询、DNS查询等，连接到指定域的Exchange的客户端访问服务器（Client
Access Server）上。

自动发现的过程首先需要获取自动配置文件，然后根据配置文件进行连接和配置，获取自动配置文件的过程不展开细说了，简单来说它将找到提供自动发现服务的客户端访问服务器、访问/autodiscover/autodiscover.xml获得配置文件。

这里有个关键地方，即正确配置DNS解析，使得Outlook客户端不管是在域环境主机上还是外部网络环境，都可以正确找到自动发现服务所在的服务器。

配置名称autodiscover指向客户端访问服务器：

![img](https://images.seebug.org/content/images/2018/12/28/1545976335000-4-2.png-w331s)

配置autodiscover的SRV记录：

![img](https://images.seebug.org/content/images/2018/12/28/1545976335000-5-2.png-w331s)

域用户在加入域的主机上使用Outlook自动发现功能：

![img](https://images.seebug.org/content/images/2018/12/28/1545976335000-6-2.png-w331s)

域用户在工作组主机上使用Outlook自动发现功能：

![img](https://images.seebug.org/content/images/2018/12/28/1545976335000-7-2.png-w331s)

**全局地址列表（GAL）**

地址列表（Address
List）记录了用户在域活动目录中的基本信息和在Exchange中的邮箱地址，用于将用户在活动目录中的属性对象与邮件地址形成关联。在Exchange中管理员可以创建不同的地址列表，用于方便管理维护组织，也方便邮箱用户通过地址列表查找特定的联系人邮箱，Exchange默认会创建一些内置的地址列表，其中包含了一个Default
Global Address List（默认全局地址列表），所有邮箱用户都会被加入到这个地址列表中。

![img](https://images.seebug.org/content/images/2018/12/28/1545976335000-8-1.png-w331s)

下面，我们进入正题

这里我们将会用到两个知名度最高的Exchange利用工具，一个是Sensepost用Go实现的与Exchange进行命令行交互的工具Ruler，Ruler可以通过RPC/HTTP或者MAPI/HTTP的方式与Exchange进行交互，只要拥有合法的用户凭证，就可以利用Ruler执行一系列的信息侦察、定向攻击等操作。另一个是Powershell实现的MailSniper，主要用于后渗透阶段的一些信息收集和获取。关于工具的详细介绍与用法可以去Github跟Freebuf上自行查找。

## **二、发现Exchange**

在渗透测试中，当进行信息收集与环境侦察时，发现与识别Exchange及其相关服务，可以有多种方法与途径，或者说，当你在执行一些端口扫描、名称查询等过程时，当发现如下举例的一些迹象和扫描结果时，你应该意识到，该环境中可能存在Exchange组件。

### **1.端口与服务**

Exchange的正常运行，如上一章节所列举的，需要多个服务与功能组件之间相互依赖与协调，因此，安装了Exchange的服务器上会开放某些端口对外提供服务，不同的服务与端口可能取决于服务器所安装的角色、服务器进行的配置、以及网络环境与访问控制的安全配置等。通过端口发现服务，来识别确认服务器上安装了Exchange，是最常规也是最简易的方法。如下是执行了一次端口扫描的结果报告。

    
    
    root@kali:~# nmap -A -O -sV -Pn 10.0.83.94
    Starting Nmap 7.70 ( https://nmap.org ) at 2018-12-24 14:14 CST
    Nmap scan report for 10.0.83.94
    Host is up (0.00043s latency).
    Not shown: 974 filtered ports
    PORT     STATE SERVICE            VERSION
    25/tcp   open  smtp               Microsoft Exchange smtpd
    | smtp-commands: test2k12.fb.com Hello [10.0.83.11], SIZE 37748736, PIPELINING, DSN, ENHANCEDSTATUSCODES, STARTTLS, X-ANONYMOUSTLS, AUTH NTLM, X-EXPS GSSAPI NTLM, 8BITMIME, BINARYMIME, CHUNKING, XRDST,
    |_ This server supports the following commands: HELO EHLO STARTTLS RCPT DATA RSET MAIL QUIT HELP AUTH BDAT
    | smtp-ntlm-info:
    |   Target_Name: FB
    |   NetBIOS_Domain_Name: FB
    |   NetBIOS_Computer_Name: TEST2K12
    |   DNS_Domain_Name: fb.com
    |   DNS_Computer_Name: test2k12.fb.com
    |   DNS_Tree_Name: fb.com
    |_  Product_Version: 6.3.9600
    |_ssl-date: 2018-12-24T06:17:42+00:00; +49s from scanner time.
    80/tcp   open  http               Microsoft IIS httpd 8.5
    |_http-server-header: Microsoft-IIS/8.5
    |_http-title: 403 - \xBD\xFB\xD6\xB9\xB7\xC3\xCE\xCA: \xB7\xC3\xCE\xCA\xB1\xBB\xBE\xDC\xBE\xF8\xA1\xA3
    81/tcp   open  http               Microsoft IIS httpd 8.5
    |_http-server-header: Microsoft-IIS/8.5
    |_http-title: 403 - \xBD\xFB\xD6\xB9\xB7\xC3\xCE\xCA: \xB7\xC3\xCE\xCA\xB1\xBB\xBE\xDC\xBE\xF8\xA1\xA3
    ……
    465/tcp  open  smtp               Microsoft Exchange smtpd
    | smtp-commands: test2k12.fb.com Hello [10.0.83.11], SIZE 36700160, PIPELINING, DSN, ENHANCEDSTATUSCODES, STARTTLS, X-ANONYMOUSTLS, AUTH GSSAPI NTLM, X-EXPS GSSAPI NTLM, 8BITMIME, BINARYMIME, CHUNKING, XEXCH50, XRDST, XSHADOWREQUEST,
    |_ This server supports the following commands: HELO EHLO STARTTLS RCPT DATA RSET MAIL QUIT HELP AUTH BDAT
    | smtp-ntlm-info:
    |   Target_Name: FB
    |   NetBIOS_Domain_Name: FB
    |   NetBIOS_Computer_Name: TEST2K12
    |   DNS_Domain_Name: fb.com
    |   DNS_Computer_Name: test2k12.fb.com
    |   DNS_Tree_Name: fb.com
    |_  Product_Version: 6.3.9600
    |_ssl-date: 2018-12-24T06:17:37+00:00; +49s from scanner time.
    587/tcp  open  smtp               Microsoft Exchange smtpd
    | smtp-commands: test2k12.fb.com Hello [10.0.83.11], SIZE 36700160, PIPELINING, DSN, ENHANCEDSTATUSCODES, STARTTLS, AUTH GSSAPI NTLM, 8BITMIME, BINARYMIME, CHUNKING,
    |_ This server supports the following commands: HELO EHLO STARTTLS RCPT DATA RSET MAIL QUIT HELP AUTH BDAT
    | smtp-ntlm-info:
    |   Target_Name: FB
    |   NetBIOS_Domain_Name: FB
    |   NetBIOS_Computer_Name: TEST2K12
    |   DNS_Domain_Name: fb.com
    |   DNS_Computer_Name: test2k12.fb.com
    |   DNS_Tree_Name: fb.com
    |_  Product_Version: 6.3.9600
    |_ssl-date: 2018-12-24T06:17:39+00:00; +49s from scanner time.
    ……
    2525/tcp open  smtp               Microsoft Exchange smtpd
    | smtp-commands: test2k12.fb.com Hello [10.0.83.11], SIZE, PIPELINING, DSN, ENHANCEDSTATUSCODES, STARTTLS, X-ANONYMOUSTLS, AUTH NTLM, X-EXPS GSSAPI NTLM, 8BITMIME, BINARYMIME, CHUNKING, XEXCH50, XRDST, XSHADOWREQUEST,
    |_ This server supports the following commands: HELO EHLO STARTTLS RCPT DATA RSET MAIL QUIT HELP AUTH BDAT
    |_smtp-ntlm-info: ERROR: Script execution failed (use -d to debug)
    |_ssl-date: 2018-12-24T06:17:48+00:00; +50s from scanner time.
    ……

80端口上的IIS、25/587/2525端口上的SMTP，及其其上详细的指纹信息，可以帮助我们确定该主机上正运行着Exchange服务。

### **2.SPNs名称查询**

端口扫描是信息收集阶段最常用的手段，端口扫描通过与目标主机之间的TCP/UDP协议交互，根据返回的各种信息判断端口开放情况和服务软件，这需要直接的与目标主机进行通信，且往往会产生规模较大的流量通信。除了端口扫描之外，对于熟悉内网渗透的同学来说，通过SPN来发现服务应该也是必备伎俩了，这种方法在Windows环境中尤其有效，因为其不需要与各个主机进行通信，而是通过已有的普通用户权限，查询活动目录数据库，枚举得到SPN，从而获知各个主机上运行着哪些服务应用。

SPN（Service Principal
Name），是Kerberos认证中不可缺少的，每一个启用Kerberos认证的服务都拥有一个SPN，如文件共享服务的SPN为cifs/domain_name，LDAP服务的SPN为ldap/domain_name，在Kerberos认证过程，客户端通过指定SPN让KDC知晓客户端请求访问的是哪个具体服务，并使用该服务对应的服务账号的密钥来对最终票据进行加密。关于Kerberos和SPN的更多信息不在此展开讲，有兴趣的同学可以自行查阅资料。

在活动目录数据库中，每一个计算机对象有一个属性名为servicePrincipalName，该属性的值是一个列表，存储着该计算机启用Kerberos认证的每一个服务名称。安装在Windows域环境中的Exchange服务同样会接入Kerberos认证，因此，Exchange相关的多个服务，应该都可以从该属性中找到对应的SPN。

![img](https://images.seebug.org/content/images/2018/12/28/1545976335000-9-1.png-w331s)

执行SPN名称查找的工具和方法有很多，这里直接以域内的一台工作机，通过setspn.exe查询获得。

![img](https://images.seebug.org/content/images/2018/12/28/1545976335000-10.png-w331s)

可以看到，exchangeRFR/exchangeAB/exchangeMDB/SMTP/SMTPSvc等，涉及SMTP服务、邮件地址簿服务、客户端访问服务器角色服务等，都是Exchange注册的服务。

再次强调，SPN是启用Kerberos的服务所注册的便于KDC查找的服务名称，这些SPN名称信息被记录在活动目录数据库中，只要服务安装完成，这些SPN名称就已经存在，除非卸载或删除，SPN名称查询与当前服务是否启动没有关系（如Exchange服务器的IMAP/POP等部分服务默认是不启动的，但其SPN名称同样存在）。

除此之外，有时候通过其他一些方法同样可以帮助探测确认Exchange服务，如发现OWA、EWS接口、自动发现服务、DNS域名记录等等，Exchange是一个庞大复杂的组件服务，各种配置信息和公开服务都可以帮助我们进行信息收集。

![img](https://images.seebug.org/content/images/2018/12/28/1545976335000-11.png-w331s)

## **三、Exchange接口与服务利用**

上文提到，Exchange提供了多种客户端邮箱接口和服务接口，对于渗透测试人员而言，这些接口就是踏入Exchange内部的第一道关卡，提供服务的接口需要有效的用户凭证信息，显然，用户名与密码破解是摆在面前的第一个尝试。在企业域环境中，Exchange与域服务集合，域用户账户密码就是Exchange邮箱的账户密码，因此，如果我们通过暴力破解等手段成功获取了邮箱用户密码，在通常情况下也就间接获得了域用户密码。

### **1.利用自动发现服务进行暴力破解**

Autodiscover自动发现服务使用Autodiscover.xml配置文件来对用户进行自动设置，获取该自动配置文件需要用户认证，如访问http://test2k12.fb.com/Autodiscover/Autodiscover.xml文件将提示需要认证，如下为认证通过，将获取到如下的XML文件内容：

![img](https://images.seebug.org/content/images/2018/12/28/1545976335000-12.png-w331s)

利用这个接口，可以对邮箱账号做暴力破解。Ruler提供了对Exchange的自动配置文件接口进行认证的暴力破解，通过配置线程数、间隔时间可以限制破解速度防止多次登陆失败触发告警或账户被封禁。

![img](https://images.seebug.org/content/images/2018/12/28/1545976335000-13.png-w331s)

### **2.Password Spray**

password spray同样是一种破解账户密码的方法，与常规的暴力破解方法不同的是，password
spary针对一批账户进行破解，每次对单个用户账户进行一次或少数次登陆尝试后换用下一个用户进行尝试，如此反复进行并间隔一定时间，以此方法躲避多次暴力破解的检测和账户锁定的风险。

mailsniper提供分别针对OWA接口、EWS接口和ActiveSync接口的password spray。

![img](https://images.seebug.org/content/images/2018/12/28/1545976335000-14.png-w331s)

## **四、取得合法凭证的后渗透阶段**

当渗透测试人员已成功取得某些用户的合法邮箱凭证，或者拿到与邮箱认证相同的域账户凭证，该用户凭证可能是通过暴力破解用户名密码得到的，可能是dump到了用户明文密码或哈希值，或者通过其他途径取得的合法有效凭证，可以帮助渗透测试人员进一步进行后渗透攻击，收集更多的敏感信息、利用合法功能与服务进行扩展。

### **1.滥用Outlook功能getshell**

Outlook是Office办公软件中用于管理电子邮件的专用软件，Exchange邮箱用户使用Outlook进行邮件管理可以体验Exchange专用的各种功能，也是应用非常广泛的办公软件之一。Outlook功能非常强大，其中的一些合法功能由于其特殊性，当攻击者利用一些灵活（而猥琐）的伎俩时往往可达成意想不到的效果。

**规则和通知功能的滥用**

Outlook提供了一项 ”规则和通知“ （Rules and
Alerts）的功能，可以设置邮件接收和发送的策略，分为规则条件和动作，即用户定义当邮件满足某些条件时（如邮件主题包含特定词语），触发一个特定的动作，这个动作可以是对邮件的管理、处置，甚至是启动应用程序。

![img](https://images.seebug.org/content/images/2018/12/28/1545976335000-15.png-w331s)

当攻击者拥有合法邮箱用户凭证的情况下，可以利用该功能在正常用户收到符合某种条件的邮件时执行特定的命令，例如反弹一个shell。该利用方法需要注意：

  * 攻击者已拥有有效的邮箱用户凭证；
  * 当触发动作为启动应用程序时，只能直接调用可执行程序，如启动一个exe程序，但无法为应用程序传递参数，即无法利用powershell执行一句话代码进行反弹shell（因为只能执行powershell.exe而无法传递后面的命令行参数）；
  * 用户需要在开启Outlook的情况下触发规则条件才有效，在未使用Outlook的情况下无法触发动作；但是，用户通过其他客户端（如OWA）接收浏览了该邮件，而后打开了Outlook，仍然可以触发该动作发生（只要这封邮件没有在打开Outlook之前删除）；
  * 规则和通知可以通过Outlook进行创建、管理和删除，OWA对规则和通知的操作可用项较少（无法创建 ”启动应用程序“ 的动作）；

手动新建一个规则及其触发动作，当收件主题中包含 ”pwn“ 时，启动计算器程序（calc.exe）。

![img](https://images.seebug.org/content/images/2018/12/28/1545976335000-16.png-w331s)

发送一封邮件主题包含单词 ”pwn“ 的邮件，当用户使用Outlook时，收到该邮件之后，触发规则，弹出计算器。

![img](https://images.seebug.org/content/images/2018/12/28/1545976335000-17.png-w331s)

从上面的尝试可以证明，该功能可以实现根据邮件主题或内容匹配启动指定应用程序，因此，可以作为一个合适的攻击面，在满足一定条件的情况下进行利用。总结一下该攻击需要满足的条件：

  * 攻击者需要拥有合法的邮箱用户凭证，且该用户使用Outlook进行邮件管理；
  * 攻击者需要通过Outlook登陆用户邮箱，然后为其创建一条合适的规则，将要执行的应用程序要么位于用户使用Outlook的主机上，要么位于主机可访问到的位置（如内网共享文件夹、WebDAV目录下等）；

Ruler也提供了利用上述规则和通知功能，可以通过命令行创建规则、发送邮件触发规则。通过结合Empire、共享文件夹、ruler，对该功能进行利用。

使用Empire启用一个监听器，创建一句话的powershell木马。

![img](https://images.seebug.org/content/images/2018/12/28/1545976335000-18.png-w331s)

将生成的一句话木马通过工具生成一个exe，并把该可执行文件放到内网一台机器的共享目录中。

![img](https://images.seebug.org/content/images/2018/12/28/1545976336000-19.png-w331s)

利用ruler和已拥有的合法邮箱凭证，在目标邮箱账户中创建一条规则，规则触发字符是 ”tcc“，规则触发动作指向共享目录中的可执行文件。

![img](https://images.seebug.org/content/images/2018/12/28/1545976336000-1-3.png-w331s)

利用ruler发送一封包含 ”tcc“
字符串的主题的邮件，ruler将使用用户自己的邮箱给自己发送一封邮件，从而触发规则（这一步可以在上一步骤中同时完成）。

![img](https://images.seebug.org/content/images/2018/12/28/1545976336000-2-3.png-w331s)

当用户使用Outlook收发邮件时，将触发规则，并从共享目录中拉取可执行木马文件并执行，该过程没有任何异样。木马执行后shell已经成功回弹。

![img](https://images.seebug.org/content/images/2018/12/28/1545976336000-22.png-w331s)

完事之后删掉规则。

![img](https://images.seebug.org/content/images/2018/12/28/1545976336000-3-3.png-w331s)

**主页设置功能的滥用**

在Outlook中，提供了一个功能允许用户在使用Outlook的时候设置收件箱界面的主页，可以通过收件箱的属性来设置加载外部URL，渲染收件箱界面。

![img](https://images.seebug.org/content/images/2018/12/28/1545976336000-24.png-w331s)

收件箱主页URL作为收件箱的设置属性，会在客户端Outlook和Exchange服务端之间进行同步，而通过MAPI/HTTP协议与Exchange服务端的交互，可以直接设置该属性。因此，当已拥有合法邮箱凭证的前提下，可以利用该功能，为邮箱用户设置收件箱主页URL属性，将其指向包含恶意代码的页面，当用户在Outlook中浏览刷新收件箱时，将触发加载恶意页面，执行恶意脚本代码，形成远程命令执行。

Outlook收件箱主页指向的URL在Outlook中通过iframe标签加载，其执行wscript或vbscript受沙箱环境限制，无法使用脚本代码创建敏感的恶意对象，即无法直接通过CreateObject(“Wscript.Shell”)的方式执行命令。但是，此处可以通过载入与Outlook视图相关的ActiveX组件，然后获取ViewCtl1对象，通过该对象获取应用程序对象OutlookApplication，该对象即表示整个Outlook应用程序，从而逃出Outlook沙箱的限制，接着，就可以直接通过Outlook应用程序对象调用CreateObject方法，来创建新的应用程序对象Wscript.Shell，执行任意命令。该利用方法详情可参考[链接1](https://sensepost.com/blog/2017/outlook-home-page-another-ruler-vector/)、[链接2](https://docs.microsoft.com/zh-cn/office/vba/api/Outlook.viewc)、[链接3](https://docs.microsoft.com/zh-cn/office/vba/api/Outlook.Application)。

    
    
    Set Application = ViewCtl1.OutlookApplication           # 取得顶层的Outlook应用程序对象，实现逃逸
    Set cmd = Application.CreateObject("Wscript.Shell")     # 利用Outlook应用程序对象创建新的对象，执行系统命令
    cmd.Run("cmd.exe")

实现该攻击需要的前提条件：

  * 攻击者需要拥有合法的邮箱用户凭证，且该用户使用Outlook进行邮件管理；
  * 攻击者通过Outlook登陆用户邮箱，为其收件箱属性设置主页URL，指向包含恶意脚本代码的页面；

ruler提供了通过MAPI/HTTP的协议交互，利用合法的邮箱凭证向服务端写入收件箱主页URL属性，当用户使用Outlook并从Exchange服务端同步该设置时，其随后对收件箱的刷新浏览将触发加载恶意网页，并执行恶意代码。

使用empire生成powershell一句话木马，通过Web服务器托管包含该一句话木马的恶意网页。

![img](https://images.seebug.org/content/images/2018/12/28/1545976336000-25.png-w331s)

利用ruler和已有的合法邮箱凭证，在目标邮箱中设置收件箱主页URL，指向Web服务器上的恶意网页。

![img](https://images.seebug.org/content/images/2018/12/28/1545976337000-4-3.png-w331s)

随后，用户通过Outlook浏览收件箱，empire将接收到反弹shell，该过程Outlook收件箱可能会提示已阻止不安全的ActiveX控件，实际上命令已经执行完成。

![img](https://images.seebug.org/content/images/2018/12/28/1545976338000-27.png-w331s)

![img](https://images.seebug.org/content/images/2018/12/28/1545976338000-28.png-w331s)

完事之后，删除该属性设置，如果不清除该设置，用户随后的多次浏览收件箱都将触发命令执行，造成empire接收多个反弹shell。

![img](https://images.seebug.org/content/images/2018/12/28/1545976338000-5-3.png-w331s)

### **2.检索邮件内容**

MailSniper可以被用户或管理员用于检索查找自己邮箱和文件夹信息，而攻击者利用该工具，也可以在获得合法邮箱凭证之后，通过检索邮箱文件夹来尝试发现和窃取包含敏感信息的邮件数据。Mailsniper包含两个主要的cmdlet，分别是Invoke-SelfSearch和Invoke-GlobalMailSearch，用于检索邮件中的关键字。

**检索当前用户的Exchange邮箱数据**

    
    
    # 查找邮件内容中包含pwn字符串的邮件，-Folder参数可以指定要搜索的文件夹，默认是inbox，使用时最好指定要搜索的文件夹名称（或者指定all查找所有文件），因为该工具是外国人写的，Exchange英文版收件箱为Inbox，当Exchange使用中文版时收件箱不为英文名，默认查找inbox文件夹会因找不到该文件而出错
    
    Invoke-SelfSearch -Mailbox zhangsan@fb.com -Terms *机密* -Folder 收件箱 -ExchangeVersion Exchange2013_SP1

检索用户zhangsan@fb.com的收件箱中包含关键字 “机密” 的邮件。

![img](https://images.seebug.org/content/images/2018/12/28/1545976338000-30.png-w331s)

**检索所有用户的Exchange邮箱数据**

利用已掌握的Exchange最高权限组成员用户，为普通用户分配ApplicationImpersonation角色，使得该普通用户可以以当前用户身份合法伪装其他邮箱用户，进而获得查询所有邮箱用户邮件的权限。更多关于ApplicationImpersonation
role，可以查看 [链接](https://docs.microsoft.com/en-us/exchange/applicationimpersonation-role-exchange-2013-help)。

    
    
    # 利用administrator管理员用户为普通用户zhangsan分配ApplicationImpersonation角色，检索所有邮箱用户的邮件中，包括“内部邮件”关键字的内容
    
    Invoke-GlobalMailSearch -ImpersonationAccount zhangsan -ExchHostname test2k12 -AdminUserName fb.com\administrator -ExchangeVersion Exchange2013_SP1 -Term "*内部邮件*" -Folder 收件箱

执行该检索的过程中，利用管理员权限为用户zhangsan@fb.com分配ApplicationImpersonation角色，然后获取组织中所有邮件地址列表，并通过角色委派通过EWS服务接口逐一检索各个邮箱账户，任务结束后，ApplicationImpersonation角色分配也被删除。

![img](https://images.seebug.org/content/images/2018/12/28/1545976338000-31.png-w331s)

![img](https://images.seebug.org/content/images/2018/12/28/1545976338000-32.png-w331s)

### **3.获取组织内的所有邮箱用户列表**

利用已掌握的合法邮箱凭证，可以利用OWA或者EWS接口查询获取到Exchange组织中所有的邮箱用户的邮件地址，即全局地址列表。

    
    
    Get-GlobalAddressList -ExchHostname test2k12 -UserName zhangsan -ExchangeVersion Exchange2013_SP1

![img](https://images.seebug.org/content/images/2018/12/28/1545976338000-6-3.png-w331s)

### **4.查找存在缺陷的用户邮箱权限委派**

邮箱用户可以通过Outlook设置自己邮箱各个文件夹的权限，通过权限设置可以委派给其他用户访问邮箱文件夹的权限，默认情况下存在两条访问规则，分别是默认规则和匿名规则，但其权限等级都为“无”。如果用户通过该属性设置了邮箱文件夹（如收件箱、发件箱等）的委派权限给其他用户，但权限委派过于宽泛时，可能导致攻击者利用有权限的用户，间接获得目标邮箱用户的邮件访问权。如下，用户zhangsan@fb.com设置了默认所有人对收件箱具有读取的权限。

![img](https://images.seebug.org/content/images/2018/12/28/1545976338000-34.png-w331s)

Invoke-OpenInboxFinder用于查找和发现指定邮箱用户的文件夹是否存在危险的权限委派。

    
    
    Invoke-OpenInboxFinder -ExchangeVersion Exchange2013_SP1 -ExchHostname test2k12.fb.com -EmailList .\users.txt

![img](https://images.seebug.org/content/images/2018/12/28/1545976338000-35.png-w331s)

当通过Invoke-OpenInboxFinder发现某些邮箱用户存在可读取邮件权限后，可以利用上面提到的Invoke-SelfSearch，检索该邮箱用户是否存在包含敏感词的邮件，使用Invoke-SelfSearch时需要添加-OtherUserMailbox选项参数，该选项表示通过权限委派缺陷检索非当前用户邮箱数据。

![img](https://images.seebug.org/content/images/2018/12/28/1545976338000-36.png-w331s)

## **五、NTLM中继与Exchange**

NTLM Relay，又一个有趣的话题。NTLM是一种基于挑战-响应的认证交互协议，被Windows上的多种应用层协议用于身份认证，如SMB、HTTP、MSSQL等。NTLM中继攻击，是指攻击者在NTLM交互过程中充当中间人的角色，在请求认证的客户端与服务端之间传递交互信息，将客户端提交的Net-NTLM哈希截获并在随后将其重放到认证目标方，以中继重放的中间人攻击实现无需破解用户名密码而获取权限。关于NTLM中继攻击的安全研究及相关工具已有很多，也有各种新玩法层出不穷，有兴趣的可以自行查阅研究，有时间再另作文章讨论。

NTLM中继攻击在SMB、HTTP协议中的应用讨论得比较多，其实质是应用协议通过NTLM认证的方式进行身份验证，因此，利用NTLM进行认证的应用都可能遭受NTLM中继攻击。Exchange服务器提供RPC/HTTP、MAPI/HTTP、EWS等接口，都是基于HTTP构建的上层协议，其登陆方式通过NTLM进行，因此，NTLM中继同样适用与Exchange。

Exchange的NTLM中继攻击由William Martin于Defcon26的演讲中提出并实现了利用工具ExchangeRelayx，可以看
[这里](https://blog.quickbreach.io/one-click-to-owa/)。

ExchangeRelayx由python实现，依赖安装完成并启动后，会启动SMB服务和2个HTTP服务，SMB服务和监听在80端口的HTTP服务用于接收受害者主机发送的认证，监听在8000端口的HTTP服务是一个管理后台，用于管理重放攻击成功的Exchange会话。该工具实现了将获取到的Net-NTLM哈希重放到真实Exchange服务器的EWS接口进行认证，通过EWS获取用户邮箱的邮件信息、附件下载、创建转发规则、查询GAL等。

启动ExchangeRelayx，将管理后台监听在本地8000端口。

![img](https://images.seebug.org/content/images/2018/12/28/1545976338000-37.png-w331s)

随后，攻击者给目标用户发送钓鱼邮件，邮件内容包含一个恶意外链，该链接可以是指向攻击服务器80端口上的Web
Server，或者是指向攻击服务器上的SMB共享，当用户点击该链接时，当前用户的NTLM认证将被发往攻击服务器，攻击服务器取得该Net-NTLM哈希时，将其重放到真实Exchange服务器以访问EWS接口，重放认证通过，管理后台可看到Exchange会话已经上线。

![img](https://images.seebug.org/content/images/2018/12/28/1545976338000-38.png-w331s)

攻击服务器上ExchangeRelayx的SMB服务接收到受害者的NTLM认证，并将其重放进行攻击。

![img](https://images.seebug.org/content/images/2018/12/28/1545976339000-39.png-w331s)

![img](https://images.seebug.org/content/images/2018/12/28/1545976339000-40.png-w331s)

点击Go to Portal，ExchangeRelayx提供了一个类OWA的邮件管理界面，可以查看用户所有邮件和文件夹。

![img](https://images.seebug.org/content/images/2018/12/28/1545976339000-41.png-w331s)

可以查询联系人信息，获取到更多邮箱用户的邮件地址。

![img](https://images.seebug.org/content/images/2018/12/28/1545976339000-42.png-w331s)

可以下载附件，导出地址簿联系人，还可以创建邮件转发规则，将该用户的邮件自动转发到指定邮箱。

![img](https://images.seebug.org/content/images/2018/12/28/1545976339000-43.png-w331s)

可以看到，利用NTLM中继攻击Exchange用户邮箱并不复杂，其原理与NTLM中继应用于其他协议并无不同，ExchangeRelayx这套框架实现了将截获的Net-NTLM哈希重放到真实Exchange服务器的EWS服务接口上，利用该认证凭证成功取得了一个Exchange用户邮箱会话，从而实现了读取用户邮件、查看联系人列表等操作。该攻击方式需要钓鱼邮件的配合，或者配合Responde、Inveigh等工具实施名称查询欺骗来完成。

### **写在最后**

本文篇幅较长，从开篇介绍Exchange相关概念与基础知识，到探测发现Exchange，通过Exchange公开接口与服务展开攻击，在渗透测试取得一定成果时，后渗透阶段我们利用Exchange同样可以做很多事情，最后，简单介绍了NTLM中继应用于Exchange的尝试。

邮件通信是企业正常运转过程中进行沟通交流与信息传递的重要载体，因此，邮件服务涉及的相关基础设施的安全也变得至关重要，攻击者突破网络边界取得权限，其目的之一是窃取关键数据，也正因如此，邮件组件服务成了黑客攻击过程中极受重视的一环。本文讨论了当前应用最为广泛的邮件服务之一Exchange在渗透测试过程中的一些利用姿势，作为近一段时间的研究总结，同时旨在抛砖引玉，希望更多有兴趣的同学一起交流探讨。

### **参考链接**

  * <https://docs.microsoft.com/en-us/Exchange/new-features/build-numbers-and-release-dates?view=exchserver-2019>
  * <https://docs.microsoft.com/en-us/previous-versions/technet-magazine/ff381422(v=msdn.10)>
  * <https://docs.microsoft.com/en-us/exchange/architecture/architecture?view=exchserver-2019>
  * <https://docs.microsoft.com/en-us/exchange/client-developer/exchange-web-services/autodiscover-for-exchange>
  * <https://github.com/sensepost/ruler>
  * <https://silentbreaksecurity.com/malicious-outlook-rules/>
  * <https://sensepost.com/blog/2016/mapi-over-http-and-mailrule-pwnage/>
  * <https://sensepost.com/blog/2017/outlook-home-page-another-ruler-vector/>
  * <https://github.com/dafthack/MailSniper>
  * <https://www.blackhillsinfosec.com/abusing-exchange-mailbox-permissions-mailsniper/>
  * <https://www.blackhillsinfosec.com/introducing-mailsniper-a-tool-for-searching-every-users-email-for-sensitive-data/>
  * <https://blog.quickbreach.io/one-click-to-owa/>
  * <https://github.com/quickbreach/ExchangeRelayX>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/775/>

