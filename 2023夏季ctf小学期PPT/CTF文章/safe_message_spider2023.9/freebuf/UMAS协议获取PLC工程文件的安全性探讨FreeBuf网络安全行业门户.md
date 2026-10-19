## ****一. UMAS协议简介****

UMAS基于旧的Telemechanique PLC使用的Xway Unite协议。UMAS协议用于配置和监视Schneider-Electric
PLC。它基于众所周知的Modbus协议，并使用Modbus协议规范中指定的保留功能代码之一 （十六进制功能代码0x5A）。

施耐德电气PLC收到Modbus数据包时，将检查功能代码是否为0x5A（即功能码90）。如果是，则使用某些特定的库，否则，将正常处理modbus请求，返回或修改指定的寄存器或PLC的线圈。（Nmap等工具探测PLC信息使用的功能码是43，即0x2b）

##  ** **二. 研究目的****

本次针对UMAS协议的研究主要目的是深入分析PLC在上传下载项目工程文件时的安全性。

##  ** **三. 研究过程****

###  ** **01**** ** **研究环境****

本次研究对象是型号为M340的施耐德PLC：

PLC范围：Modicon M340

处理器名称：BMX P34 2020

处理器版本：03.10-1

硬件ID：1030106

网络地址：TCP:10.45.115.24

![1620876943_609c9e8ff220474113a72.png!small](https://image.3001.net/images/20210513/1620876943_609c9e8ff220474113a72.png!small)

组态软件：Unity Pro XL

![1620876977_609c9eb12bc09fc1efb2d.png!small](https://image.3001.net/images/20210513/1620876977_609c9eb12bc09fc1efb2d.png!small)

上位机IP：10.45.115.27（Windows 7 旗舰版）

PLCIP：10.45.115.24（M340）

###  ** **02**** ** **研究步骤****

目前网络上已有许多关于Modbus和UMAS协议的资料，但仅局限于基本的协议介绍，本次研究将结合实际操作对M340PLC的上传项目工程文件进行详细分析。

 ** **具体步骤：****

首先抓取组态软件读取PLC工程文件的数据包：

![1620877002_609c9eca42b991668ed8f.png!small](https://image.3001.net/images/20210513/1620877002_609c9eca42b991668ed8f.png!small)

上图可以看到M340与组态软件的通信过程都是使用的90功能码，这个只是UMAS的一个头部标识，具体的协议结构如下：

![1620877012_609c9ed44cd94fcac8511.png!small](https://image.3001.net/images/20210513/1620877012_609c9ed44cd94fcac8511.png!small)

0x5A后面才是UMAS协议的功能码，本次研究的对象就是UMAS Code为0x33, 0x34,
0x35时的工程文件上传过程（从PLC将工程文件上传到组态软件）

> UMAS FunctionCode 0x33 - INITIALIZE_UPLOAD：初始化下载（从PLC复制工程到PC）
>
> UMAS FunctionCode 0x34 - DOWNLOAD_BLOCK：下载块（从PLC复制工程到PC）
>
> UMAS FunctionCode 0x35 - END_STRATEGY_DOWNLOAD：完成下载（从PLC复制工程到PC）

![1620877025_609c9ee13157d0f2fb47d.png!small](https://image.3001.net/images/20210513/1620877025_609c9ee13157d0f2fb47d.png!small)

从刚才抓取的数据包追踪TCP流，然后查找：5a为功能码，9a为本次会话的标识，33为开始上传，34为上传中，35为结束上传。

![1620877040_609c9ef05be82757c2bd7.png!small](https://image.3001.net/images/20210513/1620877040_609c9ef05be82757c2bd7.png!small)

![1620877058_609c9f02190269ad795af.png!small](https://image.3001.net/images/20210513/1620877058_609c9f02190269ad795af.png!small)

分析发现，组态软件在从PLC复制工程文件到PC时，并没有做会话识别，只需建立正常的Modbus/TCP连接便可获取PLC的工程文件。

编写相应的代码进行文件的获取，获取的文件存储为0414.apx，如下所示。

![1620877066_609c9f0a6999c7f611988.png!small](https://image.3001.net/images/20210513/1620877066_609c9f0a6999c7f611988.png!small)

这个工程文件在组态软件原文件名为heatpowerplant_m340_20210414.stu，将后缀改为.zip，然后解压能得到一个名为Station.apx的文件。操作过程如下：

利用diff和md5工具比较以上两个文件：

![1620877091_609c9f2328437fe1fcf22.png!small](https://image.3001.net/images/20210513/1620877091_609c9f2328437fe1fcf22.png!small)

 ** **完全一致！**** 没有任何校验，只需发送特定的数据包，将返回的数据进行拼接便能得到M340 PLC正在运行的工程文件。

##  ** **防御建议****

由于协议本身没有任何防护措施，建议从安全管理和整体的安全防护方案角度来降低安全风险，保障企业的安全生产和运营。

 ** **参考链接****

https://community.checkpoint.com/t5/IoT-Protect/UMAS-Protocol-visibility-of-Engineering-and-configuration/td-p/40145

