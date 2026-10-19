***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担**

## 一、概述

**AdvantechWebAccess（前称BroadWinWebAccess）是研华（Advantech）公司的一套基于浏览器架构的HMI/SCADA软件。该软件支持动态图形显示和实时数据控制，并提供远程控制和管理自动化设备的功能，在工业领域有者广泛的应用。**

AdvantechWebAccess软件一直是漏洞挖掘者的最爱，ZDI的一篇报告中指出曾经一天内收到100个关于AdvantechWebAccess软件漏洞的上报，ICS-CERT中亦有大量相关漏洞纰漏。最近关注了该软件的CVE-2017-16720/
CNVD-2018-00670漏洞，有的地方描述该漏洞为路径遍历漏洞，有的描述为RCE漏洞，且给出了不同的评分。那么其到底是以什么漏洞？深入分析一下便可知晓。

![](https://image.3001.net/images/20190615/1560593542_5d04c4869dad2.png!small)

![](https://image.3001.net/images/20190615/1560593549_5d04c48de47c6.png!small)

## 二、初步分析

很显然ZDI对该漏洞做了更加详细的纰漏，一眼看过去0x2711IOCTL？IOCTL是设备驱动程序中对设备的I/O通道进行管理的函数，难道这个漏洞与驱动有关？经过大量资料查阅，最终找到了相关解释：

![](https://image.3001.net/images/20190615/1560593562_5d04c49a48afa.png!small)

原来是AdvantechWebAccess软件中该服务的函数调用形式与Windows设备IO控制函数调用非常相似，故沿用了该叫法。从这段解释中，同时也可以发现该服务默认运行于TCP4592端口，可基于RPC协议进行远程访问控制。纳尼？和RPC扯上关系了？到底是一个什么洞？先搭环境跑PoC再说。

## 三、漏洞调试分析

下载AdvantechWebAccess V.8.0（该漏洞在<=8.3.2中均存在）在Win7x64虚拟机中安装，相应端口开放情况如下图所示：

![](https://image.3001.net/images/20190615/1560593589_5d04c4b518843.png!small)

既然漏洞与RPC协议相关，使用RpcView对该进程进行查看：

![](https://image.3001.net/images/20190615/1560593601_5d04c4c185a49.png!small)

选取webvrpcs.exe进程，可以很方便的获取到RPC服务端口（TCP592）、接口的uuid和version信息。

在<https://www.exploit-db.com/exploits/44278>获取PoC代码并执行，靶机中的Calc.exe成功运行，可发现存在RPC协议交互数据：

![](https://image.3001.net/images/20190615/1560593615_5d04c4cf3a61b.png!small)

![](https://image.3001.net/images/20190615/1560593646_5d04c4ee69b13.png!small)

![](https://image.3001.net/images/20190615/1560593673_5d04c50923673.png!small)

对目标文件（webvrpcs.exe）进行IDA逆向查看，由于该服务（webvrpcs.exe）使用了RPC协议，启用IDA插件mIDA提取代码中的RPC接口并重建相关的IDL（Interface
Definition Language）文件，在IDA中得到以下结果：

![](https://image.3001.net/images/20190615/1560593684_5d04c514a177e.png!small)

对PoC代码进行走读，第一步为连接建立，三次RPC call中第三次需要用到第二次的返回的context
handle,作为第三次call的参数，RPC协议正是利用这种模式在Server与Client之间建立稳定连接的：

![](https://image.3001.net/images/20190615/1560593749_5d04c55569185.png!small)

![](https://image.3001.net/images/20190615/1560593756_5d04c55cc651f.png!small)

由此可以看到第一个Call似乎没有太多用处（最后可以作验证）。由于漏洞函数指向0x2711
IOCTL，且在Call的过程中使用的opcode为1，因此在mIDA的输出中，首先选择opcode 0x01，右击Decompile，得到函数原型如下：

![](https://image.3001.net/images/20190615/1560593767_5d04c567a10f8.png!small)

![](https://image.3001.net/images/20190615/1560593775_5d04c56fac2e5.png!small)

可见该函数有5个参数，与最终传入Call的stubdata相对应:4个数字型和一个string型参数。

开启IDA调试器，从sub_401260入手进行单步调试，发现从开始到最终calc.exe得到执行，整个过程中函数调用顺序为：

1、webvrpcs.exe:sub_401260

2、webvrpcs.exe:sub_402c60

3、webvrpcs.exe:sub_4046D0

4、drawsrv.dll:DsDaqWebService

5、drawsrv.dll:sub_100017B0

对于第4个函数DsDaqWebService需要对drawsrv.dll进行检查，可见EDX中保存了IOCTL的值，在IDA把代码进行缩小，可发现有非常多的分支/跳转，而EAX的值最终决定了函数的下一步跳转到哪个分支：

![](https://image.3001.net/images/20190615/1560593793_5d04c58184cbc.png!small)

![](https://image.3001.net/images/20190615/1560593799_5d04c587ce7ae.png!small)

进过几步跳转，最终来到问题函数，查看伪代码如下：

![](https://image.3001.net/images/20190615/1560593810_5d04c5922b7b2.png!small)

![](https://image.3001.net/images/20190615/1560593817_5d04c5996f0e3.png!small)

函数sub_100017B0起了一个新进程，且带有参数lpCommandLine，函数中调用了Windows API
CreateProcessA,且将参数lpCommandLine直接传入，对于函数CreateProcessA的详细使用方式可查阅Windows
API，同时结合Windows在系统中搜索文件的规则，该参数可以使用类似PoC中使用的形式

    
    
    command ="..\\..\\windows\\system32\\calc.exe"

同时亦可直接使用：

    
    
    command = "calc.exe"

对上述想法进行验证：首先注销第一个RPC Call, 其次将Payload中的command换成如上所示，再次执行仍然可以成功弹出计算器。

![](https://image.3001.net/images/20190615/1560593847_5d04c5b7dfd14.png!small)

## 四、总结

从对漏洞整个分析以及PoC分析来看，此漏洞应定性为远程代码执行漏洞而非路径遍历漏洞，且漏洞具有非常大的危害，此前研华公司先后声称在V8.3、V8.3.1等版本中已经修补此漏洞，但实际漏洞均存在，当前最新版本的V8.4.0中漏洞已经得到修复。另外，从IDA分析中可以发现问题函数附近存在大量跳转，这意味者漏洞的触发可能存在多种方式（于是就是多个不同的CVE了），而从以往已公开的漏洞情况来看，有大量漏洞与本文分析的CVE-2017-16720相似的，小伙伴们，撸起袖子加油干，大量CVE等待收割。

 ***本文作者：ww5466064，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**

