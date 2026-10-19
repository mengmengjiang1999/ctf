***本文作者：cgf99，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**  

## 一、背景

**近期，在蜜罐平台发现了几个可疑的URL链接。分别是<http://54.38.213.72/bins.sh>、<http://51.15.207.183/sbins.sh>、<http://89.34.26.152/bins.sh>。上述URL链接在写稿期间（9月28日）还可以正常访问。**

其中，下载的bins.sh和sbins.sh的内容分别如下

<http://54.38.213.72/bins.sh>内容：

![类linux环境下支持多协议的DDOS病毒分析](https://image.3001.net/images/20180928/1538127353_5badf5f95945a.png!small)

<http://51.15.207.183/sbins.sh>内容：  

![类linux环境下支持多协议的DDOS病毒分析](https://image.3001.net/images/20180928/1538128337_5badf9d11ced8.png!small)  

<http://89.34.26.152/bins.sh> 内容：

![类linux环境下支持多协议的DDOS病毒分析](https://image.3001.net/images/20180928/1538127411_5badf63386735.png!small)

粗略一看，文件内容和形式基本一致。

下载的文件列表如下：

![类linux环境下支持多协议的DDOS病毒分析](https://image.3001.net/images/20180928/1538127428_5badf64485416.png!small)

##  **二、** **分析环境**

由于本地条件有限，测试的环境是Kali-linux虚拟机系统，物理机是window系统64位。

##  **三、** **初步分析**

将所下载的文件，手动对其添加可执行属性，发现在kali-linux下大多数文件无法执行，只有ftp、bash、qvmxvl、razdzn、wget、vvglma等六个文件可以顺利执行。

其中，无法运行的都是提示“cannot execute binary file: Exec format error”。具体如下图所示：

![类linux环境下支持多协议的DDOS病毒分析](https://image.3001.net/images/20180928/1538128465_5badfa5134426.png!small)

根据提示，我们大概判断，可能哪些不能执行的文件都是适用与其他系统的，比如不同的CPU架构，不同的LINUX版本等。所以，攻击者在url下载链接中分别下载并运行不同的版本，用于针对不同的系统环境。

但是，我们依旧可以利用IDA进行反汇编，可以看到大概的功能和作用，比如对其中的ajoomk文件进行反汇编，发现其包含了sendSTD、sendUDP、sendTCP、BCMSCAN、PhoneScan、MiraiIPRanges、HackerScan1、BCMscanner、TelnetScanner、MiraiScanner、PhonerScanner、SendHTTP等函数，从字面理解，该文件应该包含了STD、UDP、TCP、HTTP等发包的功能、已经Telnet扫描、BCM扫描、Mirai扫描、手机扫描、黑客扫描等攻击和渗透模块。如下所示：

![类linux环境下支持多协议的DDOS病毒分析](https://image.3001.net/images/20180928/1538128363_5badf9ebdd4ac.png!small)

此外，能在kali-linux测试环境下正常运行的文件情况分别如下：

1、ftp文件运行如下

![类linux环境下支持多协议的DDOS病毒分析](https://image.3001.net/images/20180928/1538128379_5badf9fb9e8ee.png!small)2、bash文件运行如下

![类linux环境下支持多协议的DDOS病毒分析](https://image.3001.net/images/20180928/1538128394_5badfa0ab22fe.png!small)

3、wget文件运行如下

![类linux环境下支持多协议的DDOS病毒分析](https://image.3001.net/images/20180928/1538127572_5badf6d4b932d.png!small)4、
qvmxvl

该文件运行后，即退出。

![类linux环境下支持多协议的DDOS病毒分析](https://image.3001.net/images/20180928/1538127602_5badf6f28ed1d.png!small)

利用PS枚举进程，发现多了两个名为ud1gpd1gm51ghbdhidgh58f的进程在运行。

![类linux环境下支持多协议的DDOS病毒分析](https://image.3001.net/images/20180928/1538127619_5badf7035be67.png!small)

通过/proc/pid查找，发现pid=1383和pid=1384两个进程对应的就是qvmxvl进程。

![类linux环境下支持多协议的DDOS病毒分析](https://image.3001.net/images/20180928/1538128429_5badfa2d5629f.png!small)5、vvglma

该文件运行后退出。

![类linux环境下支持多协议的DDOS病毒分析](https://image.3001.net/images/20180928/1538127669_5badf7358374b.png!small)

利用PS枚举进程，发现多了两个名为h16g516gpr6g的进程在运行。

![类linux环境下支持多协议的DDOS病毒分析](https://image.3001.net/images/20180928/1538128512_5badfa80b9724.png!small)

同样的，经过分析，其实h16g516gpr6g进程指向的就是vvgmla进程。

![类linux环境下支持多协议的DDOS病毒分析](https://image.3001.net/images/20180928/1538127707_5badf75b0d90f.png!small)6、razdzn

该文件运行后，即退出。

![类linux环境下支持多协议的DDOS病毒分析](https://image.3001.net/images/20180928/1538127738_5badf77a3d979.png!small)

利用PS枚举进程，发现多了两个名为0wqgnwqgikqg6stan5wg4eva的进程在运行。

![类linux环境下支持多协议的DDOS病毒分析](https://image.3001.net/images/20180928/1538128537_5badfa99bb270.png!small)

同样，经过分析，0wqgnwqgikqg6stan5wg4eva其实指向的就是razdzn进程。

由此，我们可以初步判断，ftp、bash、wget三个文件是一样的程序不同的版本，qvmxvl、razdzn、vvglma三个文件是一样的程序不同的版本。

##  **四、** **具体分析**

###  **1、ftp**

该文件是C语言编写的。

利用IDA反编译后我们可以看到，在main函数里面，就是一个循环操作的过程，连接服务器，获取指令，处理指令…

![类linux环境下支持多协议的DDOS病毒分析](https://image.3001.net/images/20180928/1538128582_5badfac6c31f6.png!small)

其中initConnection函数主要负责初始化网络操作。

![类linux环境下支持多协议的DDOS病毒分析](https://image.3001.net/images/20180928/1538127833_5badf7d99d6bb.png!small)

具体的服务器地址和端口为51.15.207.183:543。

![类linux环境下支持多协议的DDOS病毒分析](https://image.3001.net/images/20180928/1538127855_5badf7ef06e8e.png!small)

这个IP和端口就是前文中ftp运行后实际连接的服务器的IP地址和端口。

读取命令字符串后进行如下的处理，主要是进行指令字符串处理操作和指令处理操作。

![类linux环境下支持多协议的DDOS病毒分析](https://image.3001.net/images/20180928/1538127876_5badf804a7f68.png!small)

进入processCmd函数，发现其实现了对UDP、TCP、RAWU、HTTP、STD、GAME等指令的操作，分别利用UDP、TCP、HTTP、RAWU、STD、GAME等协议实现了发包的功能，从而实现对目标的DDOS攻击。

由于测试条件时间有限，特研发了一个小程序，功能就是连接51.15.207.183的543端口，循环读取服务器命令。经过两个小时的运行，获得了如下的命令结果，遗憾的是只有获取了UDP、GAME、STD、TCP等协议的格式，没有获取到HTTP和RAWU协议的命令，另外，列表中的命令都是间隔出现的，并且中间会连续收到PING和PONG命令（无效的命令，用于时间间隔）。

PING PING !* UDP 68.3.81.175 80 300 32 1240 10 !* GAME 147.135.9.136 65120 30
!* STD 147.135.9.136 65120 5000 1240 !* STD 73.229.243.179 80 1400 1240 !* UDP
68.3.81.175 80 300 32 1240 10 !* GAME 147.135.9.136 65120 30 !* STD
147.135.9.136 65120 5000 1240 !* STD 73.229.243.179 80 1400 1240 !* UDP
68.3.81.175 80 300 32 1240 10 PING !* UDP 73.99.114.229 6697 300 32 1240 10
PONG !* UDP 47.32.99.106 6697 300 32 1240 10 !* UDP 108.238.177.193 6697 300
32 1240 10 !* UDP 67.160.181.96 6697 300 32 1240 10 PONG !* TCP 67.160.181.96
6697 7200 32 syn,rst 1240 10 !* UDP 24.216.217.134 3074 200 32 1240 10 !* UDP
47.32.99.106 6697 300 32 1240 10  
---  
  
其中，我们可以发现，命令以!*开头（与前文中IDA分析结果一致，命令以0x21也就是!字符开头）

具体的指令格式如下：

!*字符串开头 |  协议 |  目标IP |  端口 |  间隔时间 |  发包次数 （有些协议无此项） |  包大小 |  结尾符0x10  
---|---|---|---|---|---|---|---  
  
其中每个项之间都以空格隔开。

比如指令指的是向108.238.177.193的主机的6697端口发送UDP数据报文，每个报文的大小为1240,连续发送32次，每隔300秒循环。

我们可以在IDA的void*__cdecl sendUDP(int a1, int a2, int a3, int a4, int a5, int
a6)函数里面看到具体的操作，如下：

![类linux环境下支持多协议的DDOS病毒分析](https://image.3001.net/images/20180928/1538128657_5badfb11915bd.png!small)

TCP协议sendTCP的操作函数如下所示，我们发现，在利用TCP发包的时候，还可以用指定控制标志的TCP包进行发送，比如syn、fin、rst、ack、psh等。用IDA分析TCP发包函数int
__cdecl sendTCP(int a1, int a2,int a3, int a4, int a5, int a6, int a7)，可以看到如下：

![类linux环境下支持多协议的DDOS病毒分析](https://image.3001.net/images/20180928/1538128670_5badfb1e0599b.png!small)

RAWU命令的处理函数void*__cdecl RawUDP(int a1, int a2, int a3, int
a4)与UDP的处理函数sendUDP流程基本一样。

HTTP协议的处理函数int__cdecl GucciHTTP(char a1, int a2, unsigned __int16 a3, int a4,
int a5, int a6)如下图所示。

![类linux环境下支持多协议的DDOS病毒分析](https://image.3001.net/images/20180928/1538128682_5badfb2a3b5d3.png!small)

其中GGGSSSSSSS执行的是自定义的浏览器的信息字符串。几乎所有的浏览器信息都静态包含在代码中，比如截取了部分信息如下。

![类linux环境下支持多协议的DDOS病毒分析](https://image.3001.net/images/20180928/1538128026_5badf89a4639a.png!small)

STD命令的处理函数sendSDT IDA反汇编后的结果如下图所示：

![类linux环境下支持多协议的DDOS病毒分析](https://image.3001.net/images/20180928/1538128694_5badfb360408e.png!small)

GAME命令的处理函数Game经IDA反汇编后如下图所示：

![类linux环境下支持多协议的DDOS病毒分析](https://image.3001.net/images/20180928/1538128703_5badfb3fada47.png!small)

此外，系统还支持STOP命令，用于程序退出。

##  **五、** **初步判断**

> 1、该活动应该是分布式拒绝服务攻击活动。
>
> 2、针对的对象很复杂，可能是物联网僵尸活动，面向运行类linux系统的设备（针对不同的物联网设备和主机系统）
>
> 3、此外，攻击的IP比较目前只是看到了有限的几个。具体每个IP的归属尚未分析。

 ***本文作者：cgf99，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**

