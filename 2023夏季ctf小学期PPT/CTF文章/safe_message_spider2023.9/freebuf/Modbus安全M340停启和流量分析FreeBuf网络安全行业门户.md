## 前言

 **随着施耐德（Schneider）新款的Modicon
M340可编程控制器集各种强劲功能和创新设计于一身，为复杂设备制造商和中小型项目提供各种自动化功能的最佳技术和高效、灵活、经济性的解决方案。且Modicon
M340充分支持工业和基础设施自动化控制系统的“透明就绪”架构，成为Modicon
Premium和Quantum系列产品线的最佳拓展。在灵活强大的Unity软件配合下，备受众多企业的喜爱。**

随着前几篇对[Modbus PLC的读写介绍](https://www.freebuf.com/ics-articles/235586.html)，相信大家对Modbus协议已经比较熟悉了，这次我为大家演示Schneider的PLC
M340停启操作以及中间涉及的流量分析。

## M340介绍

施耐德在整合了Modicon和TE品牌的自动化产品后，将Unity
Pro软件作为未来中高端PLC的统一平台。支持Quantum、Premium和M340三个系列。施耐德大型PLC以昆腾系列为代表，中型的有Premium、Momentum、M340等，小型的有Twido等。

如今的控制系统和工厂自动化系统，以太网的应用几乎已经和PLC一样普及。且施耐德M340采用了以太网的网口连接方式，通过以太网不仅可以下载程序，也可以用于与第三方设备进行以太网通讯，以及运用在PLC与PLC之间的数据交换。当然，大容量的内存、高可靠性、高性能金属机架、内置WEB服务器和支持热插拔功能等多数优点，已让M340使用越来越广泛。

![](https://image.3001.net/images/20200509/1589030870_5eb6afd60a14a.png!small)

## 停启准备

其实想偷个懒，找了一大堆资料，也没找到关于新的PLC
M340停启的Exploit，都是关于老版本Quantum系列140的，如下图那种，并不想用这个，因为140可能快停产了，M340、M580才是现在厂家大力推广的用来替代140的新产品。最后一脸坦然……好吧，是越想越气，没办法，只能自己动手了，最直接的办法，用上位机的编程软件进行停启再抓包进行流量分析，提取停启的数据包再自己来验证。

![](https://image.3001.net/images/20200509/1589030994_5eb6b052db83f.png!small)

## 抓取流量

这一步比较简单，我开启wirkshark实时抓取流量后，找到Schneider编程软件连接上的M340，然后点击下图中的STOP按钮，停止PLC M340。

![](https://image.3001.net/images/20200511/1589188423_5eb9174749a14.png!small)

因为PLC的编程软件部署在上位机上，所以我抓取到了上位机和M340的通信流量，如下图所示：

![](https://image.3001.net/images/20200511/1589189204_5eb91a54f077e.png!small)

## 分析流量

首先需要讲清楚，关于Modbus读写线圈和寄存器，是不需要通过任何通信验证的，而关于Modbus PLC的停启，是需要引入Session
Key这个概念的。Session Key 是会话使用的 Session 值，如果 Session 值不正确，则PLC会直接主动终止通信。FCcode 是
Modbus 协议的功能码，施耐德默认使用 0x5a 即 90 作为通信的功能码。下图是 Modbus 协议数据格式：

![](https://image.3001.net/images/20200511/1589189921_5eb91d21e0397.png!small)

那大家会问了，Session值是怎么来的呢，当我们想停启PLC的时候，PLC会主动返回（Response）一个Session值给我们，我们需要找到那个数据包。正如我这边找到的返回数据包，查看在Data里面，最后两位十六进制0x33，这个就是Session
值：

![](https://image.3001.net/images/20200511/1589182483_5eb900136c941.png!small)

那我怎么判定这个数据包携带的就是Session值呢，请看下图，红色代表上位机请求包，蓝色代表返回包，当1中返回携带了0x33这个Session值之后，之后2中所有红色的请求包都会带上0x33这个Session值，在抓取到的数据包中很好找，下图是我使用wireshark追踪TCP流看到的：

![](https://image.3001.net/images/20200511/1589182299_5eb8ff5b95f94.png!small)

![](https://image.3001.net/images/20200512/1589249658_5eba067a2ffb8.png!small)

## 停启M340

当我们获取到Session
ID之后就很简单了，可以通过任意一台能连接PLC设备的电脑发送控制CPU停启的命令，下面是我用python通过socket模块简单构造的一个数据包，其中0x33是之前抓包得到的Session
ID，41功能码代表关闭停止PLC，40功能码代表的是开启PLC，发送后成功关闭PLC：

![](https://image.3001.net/images/20200511/1589187429_5eb913651d6f7.png!small)

下方是Modbus部分常用的功能码，大家可以了解下：

![](https://image.3001.net/images/20200511/1589180895_5eb8f9df3fd06.png!small)

## 读写线圈和寄存器

停启的讲完了，我想还是再补充一些读写线圈和寄存器的流量是啥样的吧，也是很有意思的。

众所周知，Modbus 协议使用串口传输时可以选择RTU或ASCII模式，并规定了消息、数据结构、命令和应答方式并需要对数据进行校验。ASCII
模式采用LRC校验，RTU模式采用16 位CRC校验。但是通过以太网传输时使用TCP，这种模式不使用校验，也就是上述说的只要能连接上就能读取线圈和寄存器。

下图是我读取线圈抓取的流量包：

> 1、选择读取的UID为1
>
> 2、Function Code：Read Coils读取线圈
>
> 3、右边是PLC返回的包，显示线圈里的值

![](https://image.3001.net/images/20200512/1589254454_5eba19364875c.png!small)

下图是我写入寄存器的流量包：

> 1、选择写入的UID为1
>
> 2、Function Code：write Single Register写入单个寄存器
>
> 3、Data为0x08代表写入的值是0x08

![](https://image.3001.net/images/20200512/1589254947_5eba1b23abba4.png!small)

## 总结

由我上述的演示可以看出，Modbus
协议通信过程中，地址和命令全部采用明文传输，因此数据可以很容易的被攻击者捕获和解析，为攻击者提供便利。同时在Modbus
协议通信过程中，没有任何认证方面的相关定义，攻击者只需要找到一个合法的地址就可以建立一个Modbus
通信会话，轻易发送任意功能码进行攻击，而其中的Session 值也很容易获取。

这些都是根本上Modbus协议的安全问题，我们只能通过一些外部措施来进行保护和防御，例如使用Modbus
系统专用的异常行为检测设备和即时更新使用最新的PLC固件和软件等，来提高Modbus系统的安全性。

 ***本文作者：kirazhou，转载请注明来自FreeBuf.COM**

