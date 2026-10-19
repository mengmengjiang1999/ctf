***严正声明：本文仅限于技术讨论与分享，严禁用于非法途径。**

## 一、概述

西门子PLC广泛应用于工业控制系统。本文主要利用手上S7-1200 V3.0.2 固件版本的PLC和TIA13等环境进行S7comm-plus加密协议初步分析及防重放攻击分析，本文章只做交流学习使用，禁止应用于非法用途，欢迎各路大神进行交流，共同学习进步。

## 二、西门子PLC介绍

西门子PLC广泛应用于工业控制系统。西门子控制器包括S7-200、S7-300、S7-400、S7-1200以及S7-1500版本的西门子PLC，

S7-200、S7-300、S7-400系列的PLC采用早期的西门子私有协议S7comm进行通信。S7-1200/1500系列固件版本为V3.0以下的PLC采用西门子新一代的S7comm-Plus协议进行通信，该协议采用了一些特殊编码规范。S7-1200/1500系列固件版本为V3.0以上，采用了最新的S7comm-Plus协议，S7comm-plus协议引入了会话ID来防止重放攻击。

查看S7 plc系列有哪些型号及对应的固件版本，可以参考下图。

![](https://image.3001.net/images/20191115/1573818214_5dce8f6684740.png!small)

## 三、协议分析

### 3.1协议结构

S7Comm-plus以太网协议基于OSI模型如下：

![](https://image.3001.net/images/20191115/1573817562_5dce8cdacdf1f.png!small)

通过抓包分析和wireshark源码解析，可以知道S7Comm-plus协议的帧结构大致由头部、数据域、和尾部组成，头部和尾部是固定的，而数据域对不同的帧结构和内容均有很大的差异。帧结构示意图如下图所示：

![](https://image.3001.net/images/20191115/1573817579_5dce8cebe181c.png!small)

### 3.2 头部和尾部分析

Header和Trailer的组成是一样的，包含协议号、PDU类型和数据长度信息，其结构如下图所示：

![](https://image.3001.net/images/20191115/1573816632_5dce893841885.png!small)

其中头部和尾部的结构一致。Protocol id为一个字节、 PDU type 为一个字节Length为双字节。PDU type定义了该帧的类型。

![](https://image.3001.net/images/20191115/1573817602_5dce8d02994f8.png!small)

### 3.3 数据域分析

Data域是帧结构中最复杂也是变化最多的区域，通过分析可以将Data域分为Integrity part
、D_header和Data三个部分。具体结构如下图所示：

![](https://image.3001.net/images/20191115/1573816690_5dce8972bb325.png!small)

（1）D_Head

当PDU type为0x01和0x02，数据包中没有32位 Integrity part，当pdu type为0x03，数据包中有32位Integrity
part；在数据头中有两处reseved和一处unknown部分，对于不同的帧其值是不一样的，从wireshark抓包数据分析，其值分布如下所示：

![](https://image.3001.net/images/20191115/1573816727_5dce899738ca3.png!small)

（2）Data

data部分的结构、内容及格式与PDU type和opcode有关，Data部分情况种类多、较为复杂，详细分析可以阅读wireshark s7comm-plus协议解析代码。

## 四、防重放攻击分析

### 4.1 环境安装

(1) PC1（192.168.10.101）:安装博图软件TIA13，用于连接S71200 plc设备，并进行启停PLC
CPU控制，主要用于抓包分析，博图软件添加正确的PLC设备、并配置好PLC网络地址，确保能连接成功，如下所示：

![](https://image.3001.net/images/20191115/1573816974_5dce8a8e2de98.png!small)

(2)PLC (192.168.10.53)：6ES7 214-1AG31-0xB0 V3.0.2,如下所示：

![](https://image.3001.net/images/20191115/1573817641_5dce8d29ce11b.png!small)

(3) pc2 (192.168.10.100): 该主机主要进行重放攻击实验。

### 4.2 抓包分析

（1）离线模式下，点击博图软件stop 和 start 按钮，进行抓包分析。

![](https://image.3001.net/images/20191115/1573818569_5dce90c92c1e3.png!small)

返回session id，以后每次请求均要带上该session id，达到防止重放攻击目的。

Stop 和 start cpu 启停包长的均为121字节，操作成功响应数据包为84字节

![](https://image.3001.net/images/20191115/1573818578_5dce90d23d81c.png!small)

信息泄露，不知道为什么这么设计，需要返回设备信息。

（2）session id 计算方式，s7comm_plus[24]+0x80, s7comm_plus数据包第24位+0x80,如下图所示：

![](https://image.3001.net/images/20191115/1573817082_5dce8afa5fa1c.png!small)

（3）stop cpu 指令分析，主要是AddressList和ValueList, 值为00000034019077000801, 将
值修改为00000034019077000803 则为 start cpu 指令

![](https://image.3001.net/images/20191115/1573817106_5dce8b125efe4.png!small)

## 五、实施重放攻击

经过上面分析，只要获取到session id，并在每次请求plc的时候，添加上session id即可绕过S7comm-plus防重放攻击,编写如下验证代码,并抓包分析,观察现象：

![](https://image.3001.net/images/20191115/1573817167_5dce8b4fbf581.png!small)

![](https://image.3001.net/images/20191115/1573817692_5dce8d5c97e34.png!small)

运行以上代码，重放攻击成功，当进行stop时，plc RUN/STOP 灯显示黄色，当进行start cpu时候，RUN/STOP
指示灯显示绿色，如下所示：

![](https://image.3001.net/images/20191115/1573817715_5dce8d731b44d.png!small)

重放攻击抓包分析如下所示:

![](https://image.3001.net/images/20191115/1573818117_5dce8f0594c8d.png!small)

## 六、总结分析

在实验过程中还发现两处问题，当完成COTP 连接后发送的第一个S7comm-plus CreateObject
数据包可以获取到plc的相关信息，造成信息泄露，可以推出cpu型号及固件版本，攻击者可以利用这些信息开展进一步攻击。另外，当TIA13软件在线连接上PLC，启停脚本失效，应该是PLC只允许一个工程师站客户端进行连接的原因。

相关资料文档如下：

> 1、工控资产嗅探与分析(S7 PLC)
>
> <https://www.freebuf.com/articles/ics-articles/209786.html>
>
> 2、西门子S7Comm协议分析
>
> <https://laucyun.com/3aa43ada8cfbd7eca51304b0c305b523.html#6-2-1>
>
> 3、西门子S7-1200 CPU控制分析：
>
> <https://github.com/dark-lbp/isf>
>
> 4、西门子S7通信过程及重放攻击分析：
>
> <https://www.freebuf.com/articles/ics-articles/212283.html#>
>
> 5、刺穿S7CommPlus协议安全保护机制的长矛
>
> <https://www.freebuf.com/column/197267.html>
>
> 6、S7comm_plus wireshark解析代码
>
> <https://github.com/QingChenHT/S7COMMM-Plus>

***本文原创作者：yy0308，本文属于FreeBuf原创奖励计划，未经许可禁止转载**

