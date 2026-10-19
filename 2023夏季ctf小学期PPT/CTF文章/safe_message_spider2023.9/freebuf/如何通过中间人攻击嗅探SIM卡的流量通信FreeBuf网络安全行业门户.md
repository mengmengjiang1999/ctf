## 写在前面的话

**这篇文章我将介绍如何制作中间人（MitM）设置来嗅探SIM卡和后端服务器之间的流量。虽然这不是一项新的研究，但我希望这将帮助一些没有电信基础的人学习移动数据嗅探和虚假基站的知识。但是我只会介绍使用2G和GPRS的SIM卡的方案。希望将来可以带来更多关于3G，4G的文章吧！**

## 为什么

随着越来越多的物联网设备诞生，这些设备一般通过SIM卡连接到其服务器。他们可以是很常见的东西，如咖啡机，智能手表，智能眼镜，汽车或重要医疗设备等更大的东西。如果您想要嗅探物联网设备和后端服务器之间的流量，这篇文章可以帮你。

## 目标

为了对移动数据流量进行中间人攻击。我们需要使用USRP硬件制作了一个简单的伪基站。

## 要求

我在文中提到的用于进行此设置的设备。当然还有许多其他代替品。所以我没有任何声称这是最好的方法！

## 硬件

1.[USRP
B210](<https://www.ettus.com/product/details/UB210-KIT>)（带天线和电缆usb3连接到PC）

2.智能手机/或旧的GSM手机。在IoT pentest场景的情况下，我们在此处使用IoT设备。

3.一张SIM卡

4.一台笔记本电脑

## 软件

1.OpenBTS

2.SipauthServ

3.Smqueue（可选）

4.Asterisk（可选）

5.操作系统 - Ubuntu 16.04

## 什么是OpenBTS

![1.png](https://image.3001.net/images/20181103/1541223909_5bdd35e598ead.png!small)

OpenBTS.org是一个开源软件项目，致力于制作电信协议和传统的复杂的专有硬件系统，具有互联网协议和灵活的软件架构。OpenBTS软件是一个Linux应用程序，它使用软件定义的无线电向用户设备提供标准的3GPP空中接口，同时将这些设备作为SIP端点呈现给Internet。这构成了一种新型无线网络的基础，该网络有望扩大对未服务和服务不足市场的覆盖范围，同时释放创新平台，包括为新兴网络技术提供支持，例如针对物联网的网络技术。[参考](<http://openbts.org/about/>)

## 建立伪基站

![2.png](https://image.3001.net/images/20181103/1541223920_5bdd35f032290.png!small)

首先要做的是运行OpenBTS。我按照此[链接](<http://openbts.org/w/index.php?title=BuildInstallRun#Running_It_All>)从源代码构建OpenBTS。通常会有一些缺少的依赖项需要修复。除此之外，构建OpenBTS不需要特定的设置。首先，我们主要需要两个服务，即OpenBTS本身和SipauthServe。从源代码构建OpenBTS和SipauthServe后，启动终端中的两个服务。在上面的[链接](
<http://openbts.org/w/index.php?title=BuildInstallRun#Running_It_All>)中，还有其他组件，如Smqueue和Asterisk，它们使呼叫和SMS功能正常工作。但由于我们的重点主要是移动数据（这里是GPRS），我们在这里不关心设置这些组件。

## 运行OpenBTS

1.使用USB将USRP设备连接到计算机。

2.就我而言，我新建了一个虚拟机，我在其中构建了所有必需的软件，移植起来很方便。但在使用虚拟机时，要确保具有USB转发功能。在virtualbox中，您应该要启用USB>设备>
Ettus Research USRP B210（或类似的名称。如果您不知道正确的名称，请执行dmesg以确定。）

3.uhd_usrp_probe：使用此命令，用于Linux的USRP硬件驱动程序外设报告实用程序，一旦检测到设备，将下载B210的固件。

4.运行SipauthServe：

    
    
    home/dev/subscriberRegistry/apps$ sudo ./sipauthserve

5.运行OpenBTS：

    
    
    home/dev/openbts/apps$ sudo ./OpenBTS

6.运行OpenBTSCLI

    
    
    home/dev/openbts/apps$ sudo ./OpenBTSCLI

## 配置基站

在上面的步骤中，您会注意到我们运行了OpenBTSCLI。这主要是为了配置我们的OpenBTS。

下面是OpenBTSCLI中主要配置：

1.允许任何电话无需任何身份验证即可连接到基站。无论其提供商。

    
    
    OpenBTS> config Control.LUR.OpenRegistration

2.启用GPRS

    
    
    OpenBTS> config GPRS.Enable 

3.启用IP转发

    
    
    echo 1 > /proc/sys/net/ipv4/ip_forward

4.设置iptables：[这里](<http://openbts.org/w/index.php?title=GPRS>)详细介绍了整个GPRS和IPtables设置。

## 让手机连接到基站

智能手机需要更改某些设置才能使其连接到基站。如果是物联网设备，需要设置更多东西，因为在物联网设备中几乎没有选项来配置“移动网络”。我们稍后会谈到这一点。

## 设置Android手机

（在iPhone上基本相似。）

1.启用2G。这将从4G下调至2G：设置>蜂窝网络>首选网络类型> 2G

2.添加APN：设置>蜂窝网络>接入点名称。添加时，请确保将MCC和MNC设置为与SIM卡相同的值。在德国，MCC为262.跨国公司将根据提供商进行更改。详细信息查看此[链接](<http://www.mcc-mnc.com/>)。APN和Name值可以是任何值。此外，将身份验证保持为none。

![3.jpeg](https://image.3001.net/images/20181103/1541223927_5bdd35f7d53ea.jpeg!small)

3.搜索我们的基站并手动连接到它：设置>蜂窝网络>搜索网络。通常它显示为包括MCC和MNC值的数字。

![4.jpeg](https://image.3001.net/images/20181103/1541223933_5bdd35fd82f2e.jpeg!small)

如果您看到该消息，即您的手机已在网络上注册，则可以通过检入OpenBTSCLI来确认：

    
    
    OpenBTS> tmsis

这将显示注册到基站的SIM卡的IMSI。IMSI是SIM卡的私有标识符。具有IMSI的攻击者可以识别和跟踪订户的网络。

## 移动数据嗅探

GPRS正常工作后，您应该可以在手机中实际看到“LTE”或移动数据符号的位置看到符号“G”。尝试在智能手机的浏览器中搜索某些内容。这会超级慢。

 ***参考来源：[insinuator](https://insinuator.net/2018/02/hacking-101-to-mobile-data/)，周大涛编译，转载请注明来自FreeBuf.COM**

