**最近发现了恶意软件glupteba的网络攻击行为。它是一个旧的恶意软件，曾在名为“windigo”的行动中出现过，并通过漏洞传播给windows用户。**

2018年，一家安全公司报告说，glupteba已经独立于windigo行动，并转向按安装付费的广告软件服务。Glupteba活动目的各不相同：提供代理服务，利用漏洞进行挖矿活动等。

在研究了近期发现的glupteba变体之后，我们发现glupteba恶意软件之外的两个未经记录的组件：  

> 1、浏览器窃取程序，它可以从浏览器中窃取敏感数据，例如浏览历史记录、网站cookies、帐户名和密码，并将信息发送到远程服务器。
>
> 2、利用CVE-2018-14847漏洞攻击本地网络中Mikrotik路由器。它将被盗的管理员凭据上传到服务器。路由器将被作为代理中继使用。  
>

此外，我们在Glupteba中发现他可以从比特币交易中检索最新的C&C域名。我们将在下一节中进一步解释此功能。攻击者仍在改进他们的恶意软件，并试图将他们的代理网络扩展到物联网设备。  

![1.PNG](https://image.3001.net/images/20190913/1568381488_5d7b9a3034b88.png!small)![2.PNG](https://image.3001.net/images/20190913/1568381492_5d7b9a34c8011.png!small)

**Glupteba下载分析**  

下载的二进制文件由一个自定义打包程序打包，用go编程语言编写，并编译为可执行文件。首先通过获取当前应用程序信息、操作信息、硬件信息以及一些二进制硬编码的信息来初始化配置信息。它创建注册表项hkey_users\<sid>\software\microsoft\testapp以存储所有获取的信息。运行初始化函数的结果如下图所示。  

![1.PNG](https://image.3001.net/images/20190914/1568430376_5d7c592845638.png!small)sendparentprocesss函数从注册表中获取machine_guid，并从文件名、pid和父进程的名称中获取分发服务器id和活动id。它将信息嵌入post请求中，使用aes密码对其进行加密，并上传到c&c服务器。  

之后检查进程是否被提升并作为系统用户运行。如果进程没有提升，它将尝试利用fodhelper方法来提升权限。如果它不是作为系统用户运行，那么它将使用“作为受信任的安装程序运行”方式启动。

有以下主要命令：  
![1.PNG](https://image.3001.net/images/20190914/1568430705_5d7c5a71bb559.png!small)

函数mainstall检查已安装的防病毒程序，添加防火墙规则，并添加Defender排除项。

函数mainpoll定期轮询c&c服务器获取新命令。post参数如下所示（aes加密前）：  

    
    
    challenge=e94e354daf5f48ca&cloudnet_file=1&cloudnet_process=1&lcommand=0&mrt=1&pgdse=0&sb=1≻=0&uuid=&version=145&wup_process=1&wupv=0.  
    

最后，函数handlecommand实现后门功能。  

![1.PNG](https://image.3001.net/images/20190914/1568431038_5d7c5bbed3593.png!small)![2.PNG](https://image.3001.net/images/20190914/1568431042_5d7c5bc20a889.png!small)

## C&C更新能力

后门有大部分标准功能，该恶意软件可以通过discoverdomain功能通过区块链更新其c&c服务器地址。  

discoverdomain函数可以通过发送后门命令运行，也可以由自动运行。discoverdomain首先使用公开列表枚举electrum比特币钱包服务器，然后尝试使用硬编码哈希查询历史记录。  

##
![1.PNG](https://image.3001.net/images/20190914/1568431345_5d7c5cf116e2b.png!small)

## 浏览器窃取信息组件

glupteba变体中发现组件称为“updateprofile”，它是一个浏览器配置文件、cookies和密码提取程序。cookies、history和其他配置文件被压缩并上传到信息收集服务器。此组件也用go编写，编译为可执行的，并用upx打包。

浏览器窃取程序的另一个版本称为“vc.exe”。它的目标是提取浏览器密码和cookies，并将提取的数据发送到信息收集服务器。  

## 路由器攻击组件

我们发现的另一个组件是路由器攻击组件，它也是用go语言开发的。它可以查看受害者网络的默认网关并通过调用wmi命令“select
defaultipgateway from win32_networkadapterconfiguration where
ipenabled=true”获得默认ip网关的列表。

除了这些地址，还添加了以下三个默认地址：192.168.88.11、192.168.0.1、192.168.1.1。  

一旦组件成功连接到监听端口8291的设备，它就会试图利用CVE-2018-14847漏洞攻击该设备，该漏洞会影响Mikrotik路由器上使用的Routeros系统。它允许攻击者从未修补的路由器获取管理员凭据。获取的帐户名和密码存储在json对象中，经过加密，并发送到c&c服务器。  

成功获取凭据后，将向路由器的计划程序添加任务。添加调度器任务有三种实现方法：使用winbox协议、使用ssh或使用api。  

![1.PNG](https://image.3001.net/images/20190914/1568433952_5d7c67203a64c.png!small)

## 路由器流量中继

在上述设置之后，路由器成为攻击者中继流量的SOCKS代理。通过socks代理路由的第一个远程连接来自服务器，该服务器可能属于攻击者。此服务器查询返回当前SOCKS代理服务器的IP地址。此查询被重复发送，可能是为了监视SOCKS代理服务。  

在第一次检查路由器状态之后，有两种类型的流量连接到代理的不同服务器。第一个是垃圾邮件流量。远程服务器通过路由器的socks代理连接到不同邮件服务器的smtp。如果邮件服务器接受了连接，则该远程服务器将开始发送垃圾邮件。  

![1.PNG](https://image.3001.net/images/20190914/1568434231_5d7c68378dd5c.png!small)除了垃圾邮件流量，还有一组远程服务器的其他流量，这些服务器反复连接到instagram。但是发送的流量受https加密保护，不清楚这些连接到底是用来做什么的。有可能是针对instagram的密码重用攻击。  

##
![1.PNG](https://image.3001.net/images/20190914/1568434390_5d7c68d6da125.png!small)

## 安全建议

恶意软件是一种广泛存在的威胁，会影响用户和企业。从网关、端点、网络和服务器，多层的安全方法非常重要。

在设置路由器时，安全性应该是首要考虑的问题，因为大多数家庭和办公室的设备都连接到这些设备上。用户和企业可以采用良好的安全措施来抵御威胁。此外，部署相关工具为家庭网络和与其连接的设备提供额外的安全性，进一步加强防御。

 ***参考来源：[trendmicro](https://blog.trendmicro.com/trendlabs-security-intelligence/glupteba-campaign-hits-network-routers-and-updates-cc-servers-with-data-from-bitcoin-transactions/)，由Kriston编译，转载请注明来自FreeBuf.COM**  

