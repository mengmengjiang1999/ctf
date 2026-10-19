# 浅谈PSEXEC做的那些事

阅读量 **248675**

发布时间 : 2020-11-17 16:30:03

 **x**

##### 译文声明

本文是翻译文章，文章原作者 酒仙桥6号部队，文章来源：酒仙桥6号部队

原文地址：[https://mp.weixin.qq.com/s/HOck5KYFGrVvCxrRCtrnHw?scene=1&clicktime=1605689373&enterid=1605689373](https://mp.weixin.qq.com/s/HOck5KYFGrVvCxrRCtrnHw?scene=1&clicktime=1605689373&enterid=1605689373)

译文仅供参考，具体内容表达以及含义原文为准。

#

在某个游戏的夜晚，兄弟找我问个工具，顺手聊到PsExec的工具，之前没用过，看到兄弟用的时候出现了点问题，那就试用用，顺便分析一下它做了什么。

![](https://p5.ssl.qhimg.com/t0118299cc4d6c7e687.png)

#

## PsExec简介

#

PsExec 是由 Mark Russinovich 创建的 Sysinternals
Suite中包含的工具，是一种。最初，它旨在作为系统管理员的便利工具，以便他们可以通过在远程主机上运行命令来执行维护任务。PsExec是一个轻量级的telnet替代工具，它使您无需手动安装客户端软件即可执行其他系统上的进程，并且可以获得与命令控制台几乎相同的实时交互性。PsExec最强大的功能就是在远程系统和远程支持工具（如ipconfig、whoami）中启动交互式命令提示窗口，以便显示无法通过其他方式显示的有关远程系统的信息。

  * PsExec特点

  1. psexec远程运行需要远程计算机启用文件和打印共享且默认的Admin$共享映射到C:windows目录。
  2. psexec建立连接之后目标机器上会被安装一个“PSEXESVC”服务。但是psexec安全退出之后这个服务会自动删除（在命令行下使用exit命令退出）。

#

## 工作原理

#

  * PsExec详细运行过程简介正式开展测试，启用net sharAdmin $共享。拒绝访问？这是要出师未捷身先死？ 
    1. TCP三次握手，通过SMB会话进行身份验证。
    2. 连接admin$共享，通过 SMB 访问默认共享文件夹 ADMIN$，写入PSEXESVC.exe文件；
    3. 利用ipc命名管道调用svcctl服务
    4. 利用svcctl服务开启psexesvc服务
    5. 生成4个命名管道以供使用。一个psexesvc管道用于服务本身，另外的管道stdin（输入）、stdout（输出）、stderr（输出）用于重定向进程。

正式开展测试，启用net sharAdmin $共享。拒绝访问？这是要出师未捷身先死？

![](https://p1.ssl.qhimg.com/t0162ba0cef5e9909cc.png)

稳住，先别慌，抓包看看，目测是admin$无法访问导致的。

![](https://p2.ssl.qhimg.com/t01a15041fb098ead51.png)

检查admin $、IPC$，已经开启共享。

![](https://p0.ssl.qhimg.com/t01f3b7e9ca84b39272.png)

尝试访问一下，果然是admin$访问不了，咋办呢（陷入沉思~~）

![](https://p0.ssl.qhimg.com/t0171e36d5f8cde0fbe.png)

本地策略原因限制了访问？打来看看“网络访问、拒绝本地登陆、拒绝从网络远程访问这台计算机”的策略，没异常啊。不是策略，机制么？remote
UAC？很大可能呀，不管，关了！

![](https://p3.ssl.qhimg.com/t017cdc376d2a27b2fd.png)

再运行psexec：

![](https://p3.ssl.qhimg.com/t01a2a21847d1c8f5b5.png)

哦豁，可以了，目标服务器被添加“PSEXESVC”服务。为什么关了remote UAC就可以了？（陷入了反思~）

![](https://p5.ssl.qhimg.com/t01ead43610ac9954ff.png)

UAC是什么？UAC是微软在Windows Vista
以后版本引入的一种安全机制，可以阻止未经授权的应用程序自动进行安装，并防止无意中更改系统设置。那么对于防御是不是不改UAC，保持默认或更高就可以了？并不是，可以改注册表的嘛。

方法二：

HKEY_LOCAL_MACHINESOFTWAREMicrosoftWindowsCurrentVersionPoliciesSystem添加新DWORD值，键值：LocalAccountTokenFilterPolicy
为1。

#

## 进一步分析

#

条件具备，软件正常，开始抓包分析。psexec刚开始运行就做了三件事，第一：通过TCP3次握手连接目标445端口；第二：SMB协商使用SMBv2协议通信；第三：进行NTML认证。

![](https://p0.ssl.qhimg.com/t01df44491439fc46e8.png)

三次握手略过，直接分析SMB协议。SMB(全称是Server
MessageBlock)是一个协议名，可用于在计算机间共享文件、打印机、串口等，电脑上的网上邻居就是靠它实现的，SMB工作原理如下：攻击机向目标机器发送一个SMB
negotiate protocol
request请求数据包，并列出它所支持的所有SMB协议版本（其中Dialect带有一串16进制的code对应着SMB的不同版本以此分辨准确版本），若无可使用的版本返回0XFFFFH结束通信。

![](https://p0.ssl.qhimg.com/t01f6b63d7cc4d481f2.png)

目标机器返回NEGTIATE ResponseDialect数据包协商确定使用SMB2.1，至此SMB协商使用SMBv2协议通信过程结束。

![](https://p0.ssl.qhimg.com/t01e672de26822e1377.png)

NTML认证开始，攻击机向目标机器发送SESSION_SETUP_ANDX协商请求，以完成攻击机与目标机器之间的身份验证，该请求包含用户名密码。

![](https://p5.ssl.qhimg.com/t016c97aca5ef4bd027.png)

认证结束，psexec就能正常使用了么？肯定不是，接着进入PsExec运行的重点分析过程。首先，攻击机向目标机器发送Tree connect
rerquest SMB数据包，并列出想访问网络资源的名称ipc$、admin$，目标机器返回tree connect
response响应数据包表示此次连接是否被接受或拒绝。

![](https://p2.ssl.qhimg.com/t011434cb159d3170ce.png)

连接到相应资源后，通过 SMB 访问默认共享文件夹ADMIN$，写入PSEXESVC.exe文件。（4d5a是PE文件即可移植的可执行的文件的MZ文件头）

![](https://p3.ssl.qhimg.com/t01059b1d0f967846af.png)

close request and response 数据包表示PSEXESVC.exe文件完成写入。

![](https://p4.ssl.qhimg.com/t01a7853263d91c262c.png)

从代码层面看，psexec从资源文件中提取出了一个服务，并开始创建且运行了该服务程序。

![](https://p0.ssl.qhimg.com/t017366b6f8b0f49c18.png)

接着查看openservicew
request的数据包，发现攻击机开始远程调用svcctl协议并打开psexesvc服务（psexec必须调用svcctl协议，否则psexesvc服务无法启动）

![](https://p2.ssl.qhimg.com/t013ff247334641b877.png)

从代码层面看到，还需要创建与服务端通信的管道名。PsExec使用命名管道可在同一台计算机的不同进程之间或在跨越一个网络的不同计算机的不同进程之间，支持可靠的、单向或双向的数据通信。

![](https://p3.ssl.qhimg.com/t0190fe8736ad441f87.png)

![](https://p3.ssl.qhimg.com/t01431c79810bac4284.png)

从数据包层发现开始创建psexesvc、stdin、stdout、stderr 4个命名管道。

![](https://p1.ssl.qhimg.com/t01f4e765a8e37149f1.png)

![](https://p2.ssl.qhimg.com/t0129e0fd0985113bd0.png)

管道创建成功，psexec可以正常使用，已成功连上目标机器cmd。

![](https://p5.ssl.qhimg.com/t0134f4e08eb083d505.png)

在连接过程中，攻击机会每隔30s向目标机器发送一次TCP-keep-alive数据包，保持TCP心跳连接。

![](https://p4.ssl.qhimg.com/t016cd650f7291c3997.png)

攻击机退出远程连接时，tcp四次挥手关闭连接，psexesvc、stdin、stdout、stderr4个管道也会关闭，会话结束。

![](https://p1.ssl.qhimg.com/t017b1b2653b2f27af9.png)

psexec成功登录退出后，会在目标机器的安全日志中产生Event 4624、4628、4634，在系统日志中产生Event
7045（记录PSEXESVC安装）、Event 7036（记录PSEXESVC服务状态）。

![](https://p3.ssl.qhimg.com/t014e141cfd7e099d28.png)

![](https://p0.ssl.qhimg.com/t01da8105d5f7c981bb.png)

另外，当psexec远控目标机器时，可执行程序PSEXESVC.EXE被提取至目标机器的C:Windows目录下，然后再执行远程操作命令，psexec断开后，目标机器C:Windows目录下的PSEXESVC.EXE被删除。

pexec连接成功，打开目标机器cmd，可执行cmd相关命令，还有其它相关命令：

    
    
    psexec \\ip -u administrator -p 123456 -d -s calc

运行calc后返回，目标机器上会有一个calc进程，-s意思是以系统身份运行。窗口是看不到的，如果需要目标机器看到这个窗口，需要加参数-i。

    
    
    psexec \\ip -u administrator -p 123456 -d calc

以当前身份运行calc，然后返回。

    
    
    psexec \\ip -u administrator -p 123456 -i -d cmd /c start http://www.baidu.com

以目标机器当前用户身份打开百度网页，并让他看到这个网页。

![](https://p2.ssl.qhimg.com/t015c464e56b0584833.png)

#

## 结尾

#

![](https://p1.ssl.qhimg.com/t0187bd7ff8eadbe826.png)

如果运营过程发现安全设备有psexec相关告警，检查的时候围绕着psexec的特性针对性地对数据包的检查，发现误报及时添加相关白名单过滤持续性的安全运营，能显著地提高安全运营能力。

本文翻译自酒仙桥6号部队
[原文链接](https://mp.weixin.qq.com/s/HOck5KYFGrVvCxrRCtrnHw?scene=1&clicktime=1605689373&enterid=1605689373)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **酒仙桥六号部队** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/222746](/post/id/222746)

安全客 - 有思想的安全新媒体

本文转载自:
[酒仙桥6号部队](https://mp.weixin.qq.com/s/HOck5KYFGrVvCxrRCtrnHw?scene=1&clicktime=1605689373&enterid=1605689373)

如若转载,请注明出处：
[https://mp.weixin.qq.com/s/HOck5KYFGrVvCxrRCtrnHw?scene=1&clicktime=1605689373&enterid=1605689373](https://mp.weixin.qq.com/s/HOck5KYFGrVvCxrRCtrnHw?scene=1&clicktime=1605689373&enterid=1605689373)

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [渗透测试](/tag/渗透测试)

 **+1** __4赞

 __收藏

![](https://p3.ssl.qhimg.com/t0110bc5d794d277012.png) 酒仙桥六号部队

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

