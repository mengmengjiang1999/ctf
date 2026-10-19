##  **前言：**

 **Modbus
是由Modicon公司1979年发行的，已经被广泛应用于工业控制现场的应用层协议，如Modbus协议已被广泛应用于在监控和控制现场设备。Modbus协议最初是通过串行数据进行通信的，也就是Modbus
Serial协议。随着工业现代化的发展，产生了Modbus TCP协议，即通过与TCP协议相结合来发送和接收Modbus
Serial数据。Modbus的出现是为了使工业现场设备实时地接收和发送相关命令和数据，然后最重要的安全措施在Modbus的设计之初并没有被考虑进去。**

通过前一篇对[Moubus模拟器的使用和基础知识的理解](https://www.freebuf.com/ics-articles/234845.html)，本文主要深入研究Modbus专属的渗透框架Smod，以及一些对Modbus PLC设备的扫描和漏洞利用脚本。

##  **安全环境介绍：**

自1979年以来，作为业界系列上的标准，Modbus已经使数百万自动化设备能够进行通信。这些设备在全世界分布着，下图是SHODAN搜集协议使用分布区域的动态立体图。大家可以看一下，链接：<https://ics-radar.shodan.io/>

![](https://image.3001.net/images/20200427/1587951394_5ea637224a3b5.png!small)

然而广泛的使用也必然引起黑客们的注意，随之而来的是爆出各种各样的安全问题，包括拒绝服务、远程代码执行和堆栈缓冲区溢出等漏洞，下方是部分关于Modbus协议和Schneider设备的漏洞：

![](https://image.3001.net/images/20200427/1587952220_5ea63a5cecdea.png!small)

##  **Smod介绍：**

Smod是一个模块化的Modbus渗透测试框架，可以用来测试Modbus协议所需的各种诊断和攻击功能。这是一个使用Python和Scapy的完整的Modbus协议实现。这个软件可以在python
2.7.x下的Linux / OSX上运行。

近年来，SummerySCADA（过程控制网络）系统已经从专有封闭网络转向开源解决方案和支持TCP /
IP的网络。这使他们容易受到我们传统计算机网络面临的相同安全漏洞的影响。由于Modbus/TCP协议简单且容易实现，而且广泛应用于电力、水力等工业系统。所以Smod框架均使用Modbus/TCP协议。而且Smod框架可以用来评估一个Modbus协议系统的漏洞。下图是启动Smod：

> 下载链接：<https://download.csdn.net/download/weixin_43977912/12366214>

![](https://image.3001.net/images/20200426/1587883193_5ea52cb9c7575.png!small)

##  **扫描PLC：**

在对PLC设备进行一系列渗透测试操作之前，我们先对网段PLC设备进行一次扫描，了解有哪些设备。虽然Smod框架里面也有扫描脚本，但并没有Nmap里面的Scripts脚本效率高，当然也可以用PLCScan（通过先检测端口TCP/502，若开放会调用其他函数来进行更深层次的扫描检测的工具）。这里我选择Nmap里的三个模块：

> modbus-discover.nse（nmap自带）识别并发现Modbus PLCS设备及版本
>
> modicon-info.nse（需添加）识别并列举Schneider Electric Modicon PLC
>
> modbus-enum.nse （需添加）识别并枚举使用Modbus的设备

检测脚本下载地址：<https://download.csdn.net/download/weixin_43977912/12369553>

![](https://image.3001.net/images/20200426/1587907847_5ea58d07af342.png!small)

使用modbus-discover.nse脚本，发现了一系列Schneider Electric的设备及版本号，还有开启的502端口和sid（设备ID）。

![](https://image.3001.net/images/20200427/1587971694_5ea6866ee4216.png!small)

使用modicon-info.nse脚本获取更详细的信息：

> BMX P34 2020：BMX P34 高性能CPU，内置USB口，Modbus，Ethernet TCP/IP
>
> Fireware：固件版本v3.2
>
> Memory Card：BMXRMS008MP 内存卡8MB

![](https://image.3001.net/images/20200426/1587907792_5ea58cd09457a.png!small)

##  **Smod渗透：**

接下来我们来使用Smod，看看它有哪些厉害的功能：

> 1、 暴力破解PLC的UID
>
> 2、 网络嗅探进行ARP地址欺骗
>
> 3、 枚举Modbus PLC的功能
>
> 4、 模糊读写单一或多个线圈功能
>
> 5、 模糊读写单一或多个输入寄存器功能
>
> 6、 测试读写单一或多个保持寄存器功能
>
> 7、 测试单个PLC 所有功能
>
> 8、 对单个或多个线圈写值进行Dos攻击
>
> 9、 对单个或多个寄存器写值进行Dos攻击
>
> 10、对ARP地址欺骗进行Dos攻击

![](https://image.3001.net/images/20200426/1587912705_5ea5a001ecf19.png!small)

首先我们暴力破解PLC的UID，因为接下来的操作，例如读写线圈和寄存器或者Dos攻击，都需要带上UID，所以我们先使用/modbus/scanner/uid这个模块。如下图所示，我们填写好RHOSTS
IP后直接exploit，获取到的UID为1。

![](https://image.3001.net/images/20200427/1587976010_5ea6974ab8fee.png!small)

接着我们对Modbus
PLC的功能进行枚举（/modbus/scanner/getfunc），携带上UID，查看我们可以针对其PLC做哪些渗透工作，如下图所示，发现基本常用的功能码（Function
Code）都支持，那接下来就好办了。

![](https://image.3001.net/images/20200427/1587976847_5ea69a8f181f7.png!small)

知道了该PLC支持的功能，我们先选择读取线圈看一下是否成功（/modbus/function/readCoils），发现读取成功了Coils给了回应，如下图所示：

![](https://image.3001.net/images/20200427/1587979551_5ea6a51f1db87.png!small)

接下来我们主要对保持寄存器进行读取（/modbus/function/readHoldingRegister），需要设置的参数如下：

RHOSTS：xx.xx.xx.xx（IP）

Quantity：0x0010（为读取寄存器连续个数，默认为10个，对应组态软件的通道数量，这里我们读取16个，所以换成16进制是0010）

StartAddr：0x0064（为寄存器起始地址，默认从0开始，这里我们从100开始，所以换成16进制是0064）

UID：1

如下图所示，读取到了registerval（寄存器的值）：

![](https://image.3001.net/images/20200427/1587979033_5ea6a319a10ae.png!small)

Dos这块的攻击我就不演示了，把我一群PLC设备弄挂了我上哪哭去……篇幅原因，我再演示对单个寄存器的写值功能，其他模块的功能大同小异，大家有空可以一一尝试哈，如果有不理解的地方，可以直接评论或者私信俺。如下图所示，设置好了寄存器的数据存放地址和值，成功写入。

![](https://image.3001.net/images/20200428/1588042400_5ea79aa095ca9.png!small)

##  **总结：**

使用了Smod渗透框架才知道，我们在一个PLC的网络里，居然可以做这么多坏事！读写线圈和寄存器，还有Dos攻击，这些对PLC都是致命的，所以一个Modbus协议系统里需要多层次的安全防御手段，例如流量异常行为检测，只有可信任的设备，才能接入工控系统网络，且需要进行身份认证，确保登陆者也是可信任者。对Modbus
系统进行日志记录和安全审计功能，记录操作的时间、地点、操作者和操作行为等关键信息从而提供安全事件爆发后的追查能力。

当然，之前讲述了很多Modbus协议和PLC设备被爆出的漏洞，所以企业也要定期对工控系统进行漏洞扫描，即时修补漏洞更新软硬件。后续将与大家一起更深入研究Modbus协议，通过Python的modbus_tk模块进行读写PLC并进行详细的流量分析。

 ***本文作者： 黄一113530，转载请注明来自FreeBuf.COM**  
  

