##  **前言：**

**如今工业控制系统设计的领域包括交通运输、能源行业、装备制造、机械制造等多个国家关键基础领域。工业控制系统的信息安全问题关系到国家安全和社会稳定。Modbus
协议是一种典型的工业控制系统通信协议，是目前应用最为广泛的工业控制协议之一。由于其设计简单、容易开发的特性，使得Modbus TCP
协议极易被恶意攻击者利用，从而对工业控制系统造成破坏和损失。**

通过前两篇[模拟器](https://www.freebuf.com/ics-articles/234845.html)和[Smod框架的讲解](https://www.freebuf.com/ics-articles/235047.html) **，**
相信大家对Modbus有了大概的认识，本文主要是通过Python代码和Mbtget工具多种姿势读写Modbus PLC，让大家对Mdobus有更深入的理解。

##  **一、Modbus_tk库介绍：**

Modbus_tk是使用python语言实现的Modbus协议栈，该函数库即支持主机也支持从机，既支持RTU也支持TCP。

下载安装pip install modbus_tk，下图是modbus_tk库包含的内容：

![](https://image.3001.net/images/20200429/1588148712_5ea939e8d2759.png!small)

###  **RTU通信读写寄存器**

因为代码这块主要讲RTU通信和TCP通信读写寄存器，那什么是RTU呢？Modbus是一种应用层协议，它定义了与基础网络无关的数据单元（ADU），可以在以太网（TCP/IP）或串行链路上进行通信。在串行链路上，Modbus协议有两种传输模式——ASCII模式和RTU模式。其中，ASCII（AmericanStandard
Code for Information Interchange）为美国国家信息交换标准编码，RTU（ Remote Terminal
Unit）为远程终端设备。所以RTU通信就是通过模拟远程终端设备读写寄存器。

RTU通信我们需要的辅助工具是VSPD（Virtual Serial Port Driver 9.0 by Eltima
Software）虚拟串口工具，如下图所示，帮助我们添加模拟的端口是COM1/COM2：

![](https://image.3001.net/images/20200429/1588150423_5ea94097c6595.png!small)

添加端口之后，打开我们计算机的设备管理就增加了如下端口示意图：

![](https://image.3001.net/images/20200429/1588150478_5ea940ce76e30.png!small)

配置好串口之后，接着来配置我们的模拟器Modbus Slave（PLC），为什么要用模拟器呢？因为大部分真实的Mdobus PLC都是通过Modbus
TCP协议通讯的，所以RTU的通信读写我们通过模拟器来实现。

> 1、选择连接方式为Serial Port（串口）
>
> 2、串口设置为上图的COM1->COM2
>
> 3、通信方式选择RTU
>
> 4、波特率9600、数据位8位、无校验位、1位停止位默认不变
>
> 5、模拟器的寄存器上设置好供modbus_tk读取的值

![](https://image.3001.net/images/20200429/1588151051_5ea9430b59000.png!small)

接下来就是通过Python的modbus_tk库来读取寄存器的值：

> 1、导入modbus_rtu和cst来选择读取线圈和寄存器
>
> 2、设置好串口读取的参数（端口、波特率、校验位和停止位）
>
> 3、设置读取寄存器值（1为设备ID，0为开始读取的地址，9为读取的位数）
>
> 4、显示之前在保持寄存器里设置的值，读取成功

![](https://image.3001.net/images/20200429/1588149184_5ea93bc0d3470.png!small)

###  **TCP通信读写PLC**

讲完了RTU通信，那现在讲一下ModbusTCP通信。在实际的工业系统应用中，Modbus
TCP的使用也更加普遍。虽然TCP中没有了CRC校验，但是数据包中已经进行了校验，再加上工业PLC网络大部分不对外开放，所以Modbus
TCP通信也是相对比较安全的，但是如果攻击者进入了工业系统内网中，那后果不堪设想。ModbusTCP通信使用TCP502端口和正常的从机IP地址来进行联系。

下图是modbus_tk库进行TCP通信读取Schneider M340的代码和结果：

> 1、导入modbus_tcp和cst来选择读取线圈和寄存器
>
> 2、TCP通信只需设置PLC的IP就可以
>
> 3、设置读取保持寄存器的值（1为设备ID，100为开始读取的地址，25为读取值的位数）
>
> 4、成功读取到PLC寄存器的值

![](https://image.3001.net/images/20200429/1588149479_5ea93ce76308b.png!small)

##  **二、Mbtget工具介绍：**

介绍完了用代码来读取Modbus
PLC的值，大家是不是觉得还是比较麻烦，我用个工具不香吗？哈哈，接下来介绍的就是轻量级的工具——Mbtget。它是简单的perl脚本编写的，通过一行命令寥寥几个参数就可以读写线圈和寄存器的值，十分方便。

首先是在linux上的安装：

![](https://image.3001.net/images/20200502/1588402233_5ead18391c880.png!small)

安装十分的简单，完成后我们使用help命令查看Mbtget的使用方法和功能，如下图所示：

![](https://image.3001.net/images/20200429/1588150601_5ea94149636b3.png!small)

我们先来个简单的，-r1代表读取线圈状态，-u1代表UID为1，-n8代表读取八位值，再接上PLC的IP，就得到了如下的图，成功读取了线圈：

![](https://image.3001.net/images/20200429/1588150642_5ea941725ec0b.png!small)

接下来填写的是-r3读保持寄存器，-u1代表UID为1，-a100代表读取的地址从一百位起，-n16代表读取16位值，再接上PLC的IP，就得到了如下的图，成功读取了保持寄存器：

![](https://image.3001.net/images/20200429/1588149325_5ea93c4d32d07.png!small)

最后我们选择演示写值入寄存器，-w6代表写入单个的保持寄存器，12代表写入的值，-a1代表从地址第一位开始，-d代表将Tx（发送transport）和Rx
（接受receive）用十六进制表示出来，如下图所示，写入成功：

![](https://image.3001.net/images/20200429/1588151823_5ea9460fcdd6e.png!small)

Mbtget工具的使用已经讲完啦，大家觉得是不是特别简单实用。毕竟篇幅有限，关于Python的modbus_tk库和Mbtget工具的使用，大家如有不解之处，可以随时私信或者评论俺。

##  **总结：**

Modbus TCP协议是一种通用的工业以太网协议，如今Modbus TCP协议已被广泛应用于无数工业控制系统中，因此对Modbus
TCP协议进行信息安全研究对整个工业控制系统的安全性研究具有重要意义。而经过文中对Modbus
PLC的任意读写操作，证明了进行工业控制系统信息安全研究的必要性。同时也暴露出Modbus
TCP协议目前存在缺乏认证机制、无授权访问控制机制、无防重放攻击机制以及缺乏机密性保护等问题。

例如可以设计Modbus
TCP信息安全防护模型，可以分为密码模块、站间认证模块、防重放模块和授权访问控制模块。这样的安全防护思路和想法很多，需要大家沉下心努力去研究探索，才能在工控安全的道路上越走越远。

 ***本文作者：黄一113530，转载请注明来自FreeBuf.COM**

