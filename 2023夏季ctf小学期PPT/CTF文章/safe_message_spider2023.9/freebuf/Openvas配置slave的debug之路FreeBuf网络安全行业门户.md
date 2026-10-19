**作为安全行业从业者，一定会有一款适合自己的扫描器，在众多开源扫描器中，相信有很多人会选择openvas，绿骨头组织的这款产品因其性能卓越，扩展性强，接入点、接入方式灵活等众多优点，至今已经成为了企业的安全解决方案之一。**

这款扫描器有一个非常优秀的功能点，即以GMP协议为支撑，平台支持灵活任务下发。因此这个功能是一定要尝试的，试想当你想对一批目标进行定时扫描或者常规扫描时，你只需要简单的配置，通过web界面或者cli脚本，将任务下发给你的scanner-slave集群，然后坐等收集扫描结果，是不是很爽！

笔者最近在配置openvas的主从服务器时，遇到了一些BUG甚是头疼，磕了很久终于解决，于是记录下来，以防有同道中人掉坑里。

## 名词扫盲

在配置扫描器的时候，海量的教程，海量的词汇经常让我头晕晕的，比如Openvasmd、gvmd、openvassd、gasd、OMP、GMP等等，首先我们来过一遍这些名词。第三列的重要指数是笔者综合在学习OpenVas的过程中碰到的频率，重要性，困扰性给的一个参考值。

名称 | 功能 | 重要指数  
---|---|---  
gvmd | GVM10自带的守护进程 | 10  
openvasmd | GVM9及之前的守护进程的叫法 | 10  
openvassd | GVM的扫描器进程，作用就是进行漏洞扫描，并将结果反馈给管理模块。 | 10  
OSPd | 多个扫描器之间使用OSP协议进行通信，而OSPd就是通信进程。 | 3  
GOS | 全称Greenbone Operating System。GSM设备的操作系统。提供商业版本，具有企业支持功能的GVM框架。 | 4  
GSM | 全称Greenbone Security Manager，绿骨公司系列产品之一，常以应用程序或虚拟机形式出现。 | 8  
GMP | 全称Greenbone Management
Protocol，听名字就知道是管理协议，gvmd和openvasmd使用该协议、基于XML与其他模块进行通信，以前叫OMP。 | 8  
OSP | 全称Open Scanner Protocol，多种绿骨公司产品之间用于通信的协议 | 5  
GVM | 全称Greenbone Vulnerability
Manager，这是许多服务的一个框架，作为一个商业产品也是组成GSM的一部分，以前直接叫openvas。 | 10  
GVM9 | GVM9代版本，也叫OpenVas9，用在GOS 4代系列。 | 10  
GVM10 | GVM10代版本，用在GOS 5代系列。 | 10  
GSE | 全称Greenbone Source
Edition，绿骨应用栈，支撑漏洞扫描，漏洞管理，GVM等，用以支持第三方调用，比如Linux的某个分支提供GVM，但它是以GSE为基础构建的。 | 3  
  
## 配置slave-scanner的方法

不论是跟GMP还是OSP server通信，首先需要选择一种主从服务器间的通信方法：

### TLS

TLS连接类型是GOS
3.1及更高版本中用于通信的默认连接类型,也是笔者要重点介绍的配置方法.笔者的测试环境为centos7,具体版本见2.3,一台slave和一台master,且防火墙关闭(方便测试)

 **Master配置**

第一步:登录到GSA上,进入 Configuration-> Credentials

![](https://image.3001.net/images/20200127/1580091563_5e2e48ab36f84.png!small)

![](https://image.3001.net/images/20200127/1580091569_5e2e48b143e76.png!small)

第二步:进入Configuration-> Scanner，Type一定要选GMP Scanner.Credential选刚刚创建的test.

![](https://image.3001.net/images/20200127/1580091583_5e2e48bf71791.png!small)

第三步:创建任务

![](https://image.3001.net/images/20200127/1580091607_5e2e48d7627f3.png!small)

第四步:配置证书，重中之重

任务创建之后需要在master上给相应的scanner配置slave的cacert.pemslave上cert默认路径在/var/lib/gvm/CA/cacert.pem此处需要把slave上的cacert.pem复制到master上.

此处配置证书需要在master机器上，并以命令行方式进行

    
    
    gvmd --get-scanners                   //查找test的uuid
    gvmd --modify-scanner="test-uuid" --scanner-ca-pub=/path/to/slave/cacert.pem

此处配置完成master后,最好重启一下gvmd以及gsad.原因后面会说.接下来配置Slave.

 **Slave配置**

第一步,创建一个非admin的账号

    
    
    gvmd --create-user=test --new-password=test --role=Admin  
    

第二步:保证gvmd监听在TCP-port上,而不是Unix socket,这一步笔者在实验的时候错了许多次,总结出几个要注意的点.首先执行:  

    
    
    service gvmd stop
    service gsad stop  
    

其次执行:  

    
    
    gvmd --listen=0.0.0.0 --port=9391
    gsad --mlisten=0.0.0.0 --mport=9391  
    

确保gsad正常运行的前提下,gvmd监听9391端口:  

    
    
    netstat -anop | grep  gvmd
    tcp        0      0 0.0.0.0:9391            0.0.0.0:*               LISTEN      13034/gvmd: Waiting  off (0.00/0/0)  
    

期间打开log,跟进报错:  

    
    
    tail -f /var/log/gvm/gvmd.log  
    

启动task

点击启动task,此处可能会遇到如下几个问题:

问题一:

    
    
    failed to connect xxxx port 9391.  
    

解决方案:确保slave上的9391端口开放,确保防火墙能通过.

问题二:

    
    
    (master)slave_connect failed  | (slave)read_from_client_tls

该问题广泛出现在Greenbone 开源社区，github issue，同样的配置不见得能解决同样的问题，因此笔者进行了深入的分析和研究。

    
    
    tail -f /var/log/gvm/gvmd-master:
    md manage:WARNING:slave_connect: failed to open connection to XXXX on 9391
    lib  serv:WARNING:gvm_server_verify: the certificate is not trusted
    lib  serv:WARNING:gvm_server_verify: the certificate hasn't got a known issuer  
    
    
    
    tail -f /var/log/gvm/gvm-slave:
    md   main:read_from_client_tls: failed to read from client: The TLS connection was non-properly terminated.  
    

1.笔者首先抓了master上的包,发现有向slave的9391端口发的包, slave的9391端口也有返回包,排除了网络不可达的问题.

2.端口可以通信，那会不会是证书选错了？笔者通过查阅各种资料,确保cacert没有搞错,路径没有搞错

3.端口正常，证书正确，配置正确？经历一天的排除+尝试,一遍遍确认自己配置是正确的前提下,笔者终于找到了找到了一个可能的原因,即当执行下列命令之后  

    
    
    gvmd  --modify-scanner="uuid" --scanner-ca-pub=/path/to/cacert.pem  
    

gvmd并不能立即加载该证书,并且即使按照上面步骤执行也会重复出现上述报错.如果没有加载证书，配置再正确，报错都一样，分析都是白搭。

因此需要在配置完证书之后,重启一下gvmd使其加载证书,才能加载正确配置。

重启task即可在两边的log中发现如下log,且GSA上也终于从requested变成了running.欣喜地发现进度为1%.  

    
    
    Status of task test6  has changed to Running  
    

### ssh

从GOS 4开始，SSH是默认的连接类型，可通过GVM建立管理守护进程之间的连接。 GMP协议通过SSH隧道传输并转发到gvmd /
openvasmd,目前笔者还没有测试过.  

### Unix Domain Socket

Unix Domain Socket是Greenbone Source Edition中gvmd的默认类型。
但只可以使用在与进程相同的主机上运行client-tools时。

gvmd/openvasmd提供的Unix Domain Socket的从GVM 9中的openvasmd.sock更改为GVM
10中的gvmd.sock。

在GOS 4代里sock路径一般为/run/openvas/openvasmd.sock.

在GOS 5代里sock路径一般为/run/gvm/gvmd.sock.

基于OSPd的扫描器也可以通过Unix Domain Socket访问。

举个例子,笔者的实验环境为:  

    
    
    rpm -qa | grep gvm  
    rpm -qa | grep openvas 
    gvmd-8.0.0-6928.el7.art.x86_64
    gvm-libs-10.0.0-6924.el7.art.x86_64
    openvas-scanner-6.0.0-6930.el7.art.x86_64
    openvas-smb-1.0.5-6923.el7.art.x86_64  
    

默认启动的gvmd使用的是Unix Domain Socket,验证如下:  

    
    
    netstat -ano |grep gvmd
    unix  2      [ ACC ]     STREAM     LISTENING     25846    /var/run/gvmd.sock  
    

## 总结

1.官方文档永远是最好的教程,其次是开源社区.

2.Debug时要有自己的主线+思考，不是盲目地遇到 一个问题就去查，别人的前置环境和自己的不一样会让自己掉进去，越陷越深，这样问题就会发散。

3.心平气和，万不得已之时，重启大法好！

> 附一份官方参考文档:<https://readthedocs.org/projects/gvm-tools/downloads/pdf/latest/>

 ***本文作者：LittleT1ger，转载请注明来自FreeBuf.COM**

