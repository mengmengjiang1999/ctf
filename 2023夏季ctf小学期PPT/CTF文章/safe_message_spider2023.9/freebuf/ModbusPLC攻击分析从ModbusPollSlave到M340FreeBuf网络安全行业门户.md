## 前言

 **工业控制已从单机控制走向集中监控、集散控制，如今已进入网络时代，工业控制器连网也为网络管理提供了方便。Modbus
就是工业控制器的网络协议中的一种。在2004年，中国国家标准委员会正式把Modbus作为了国家标准，开启了Modbus为中国工业通信做贡献的时代。**

本文主要研究Modbus Poll/Salve模拟器的使用以及对Schneider（施耐德）PLC
M340的连接测试，文中涉及一些测试思路可能存在不严谨之处，欢迎大家指正哈

## 协议介绍

Modbus一种应用层消息传递协议，位于OSI模型的第7级，提供在不同类型的总线或网络上连接的设备之间的客户端/服务器通信。Modbus传输方式包括ASCII、RTU、TCP三种报文类型，协议本身并没有定义物理层，只是定义了控制器能够认识和使用的消息结构，通过对数据的校验来区分。文中均采用Modbus
TCP协议来进行通信。

![](https://image.3001.net/images/20200423/1587650046_5ea19dfeb0732.png!small)

这里我主要介绍一下文中涉及的概念以及小伙伴们必须知道的Modbus的基础知识，详细的概念我就不展开介绍了，大家可以阅读：

> <https://www.freebuf.com/articles/ics-articles/148637.html>

下表是由Modbus从设备提供给Modbus主设备的对象类型的表：

 **Object type**|  **Access**|  **Size**|  **Address Space**  
---|---|---|---  
线圈Coil| Read-write| 1 bit| 00001 - 09999  
离散输入Discrete input| Read-only| 1 bit| 10001 - 19999  
输入寄存器Input register| Read-only| 16 bits| 30001 - 39999  
保持寄存器Holding register| Read-write| 16 bits| 40001 - 49999  
  
## 模拟器介绍

要介绍Modbus的模拟器，就得从它的通信方式开始介绍了。Modbus使用一种简单的Master and
Slave主从协议进行通信。客户机作为主站，向服务器发送请求；服务器（从站）接到请求后，对请求进行分析并作出应答。一般使用上，监控系统(HMI)都为Master，而PLC、电表、仪表等都为Slave。

所以，模拟器Modbus Poll就是Master，Modbus Slave就是Slave，和S7系列模拟器的Client和Server是一个道理。

![](https://image.3001.net/images/20200426/1587865857_5ea4e9011cd6f.png!small)

> 下载链接：<https://www.modbustools.com/download.html>

### 模拟器连接

接下来就是实际连接啦，首先我们设置好我们虚拟的PLC（Modbus Slave），如下图所示：

> 1、 点开上方connection，选择了连接协议为Modbus TCP/IP
>
> 2、 默认地址为127.0.0.1无需设置，到时候Modbus Poll就连这个地址，其他的端口为502和Ipv4默认。
>
> 3、 ID默认为1，是Slave的设备地址，F=03代表03的功能码
>
> 4、 设置好一些供Poll读取的数据

![](https://image.3001.net/images/20200423/1587650005_5ea19dd5833ee.png!small)

如下图所示，这是Modbus
Poll连接好Slave的示意图，也读取到了Slave中设置好的寄存器的值，其中Tx=112代表向PLC发送数据帧的次数，Err
=0代表通讯错误次数，互相连接上之后就不会再出现No connection的红字。

![](https://image.3001.net/images/20200423/1587653513_5ea1ab89d1d01.png!small)

因为Modbus能访问一条数据链路上的254个设备，Poll也支持读写同时来自不同设备的不同数据内容。下图显示了两个打开的窗口，从从站ID
1读取10个保持寄存器，从从站ID 2读取10个保持寄存器。

![](https://image.3001.net/images/20200424/1587693007_5ea245cfcbf25.png!small)

模拟器之间的连接就暂时只讲这么多，其实还有很多功能，例如读取输入寄存器和线圈、监控数据流量等，这些在接下来主要讲连接Schneider的PLC设备的时候具体说。

### Modbus Poll 连接SchneiderM340

和西门子PLC需要编程软件博途一样，这次Schneider（施耐德）PLC在上位机部署的编程软件用的是EcoStruxure Control Expert
来连接M340设备，如下图所示：

![](https://image.3001.net/images/20200425/1587824585_5ea447c978521.png!small)

Modicon
M340是全球能效管理专家施耐德电气于2007年推出的高性能中型PLC平台，拥有“精巧、可靠、创新、易用、高性价比”等诸多新亮点，适用于中小型项目、复杂机械及过程装备，实验对象如下图所示：

![](https://image.3001.net/images/20200425/1587824619_5ea447eb2e312.png!small)

首先我们先在编程软件上查看PLC的IP地址，用于Modbus Poll的连接：

![](https://image.3001.net/images/20200425/1587822158_5ea43e4eec2bf.png!small)

接着我们通过之前的叙述了解到模拟器连接Slave（PLC）需要知道设备ID ，这个是连接的关键点，虽然大部分都会设置为1，但是还是需要特地查看一下：

![](https://image.3001.net/images/20200425/1587822552_5ea43fd8ac3f2.png!small)

然后我们选择读取AI：AnalogInput（模拟输入，输入寄存器）中的值，如下图所示：

![](https://image.3001.net/images/20200425/1587822619_5ea4401b158aa.png!small)

最后通过对Modbus Poll设置好连接PLC的IP、ID以及Function进行设置，最终连接到M340的寄存器区域读取到数据。

![](https://image.3001.net/images/20200426/1587866299_5ea4eabb13c37.png!small)

## 总结

由上述可见，虽然Modbus 协议获得了广泛的应用，但是在实现具体的工业控制系统时，安全问题在却很少被注意到。首先，TCP /IP
协议自身存在的安全问题不可避免地会影响到工控网络安全，例如中间人攻击，拒绝服务等攻击手段都会影响到Modbus系统安全，还有Modbus本身缺少身份认证，功能码滥用等问题都需要注意。这些安全问题都需要通过安全设计、安全审计和入侵防御等安全措施进一步深入的解决。

本篇文章是对Modbus PLC基础性的研究，主要关于模拟器的使用以及连接使用PLC的一些基本概念。后续会对Schneider
PLC进行更深入的探讨，主要关于Modbus专属的Smod渗透框架研究以及Modbus流量分析等。

 ***本文作者：黄一113530，转载请注明来自FreeBuf.COM**

