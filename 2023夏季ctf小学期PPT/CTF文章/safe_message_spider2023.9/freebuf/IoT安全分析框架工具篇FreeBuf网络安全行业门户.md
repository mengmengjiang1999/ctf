## 1\. 概述

物联网是一个比较复杂的领域，涉及到较多的电气工程、通信工程、电子工程等领域相关知识，物联网领域的安全技术和框架跟互联网也有较大的区别，为了帮助工程师尽可能系统性的了解物联网设备安全性分析框架和技术，本篇从硬件工具角度出发，系统的介绍物联网安全分析中常用的分析工具。

## 2\. 内部架构视图

单独的看一个物联网设备，可以将该设备分成三个部分：

> Microprocessor：负责设备最核心的运算
>
> Peripherals： 和Microprocessor组成MCU，负责和外部世界进行连接
>
> External Modules： 不同种类的物联网设备要处理不同的数据，通过不同的Module来感知物理世界

![image.png](https://image.3001.net/images/20210517/1621254267_60a2607bb20b47ce52967.png!small)

## 3\. 接口调试工具

### 3.1 JTAG

 **3.1.1 简介**

JTAG是联合测试工作组（Joint Test Action
Group）的简称，是在名为标准测试访问端口和边界扫描结构的IEEE的标准1149.1的常用名称。此标准用于验证设计与测试生产出的印刷电路板功能。说简单点，通过JTAG接口可以读写设备内存和寄存器中的值，是一个强大的“后门”。

![image.png](https://image.3001.net/images/20210517/1621254268_60a2607cd7d4df3d12e9e.png!small)

 **3.1.2 示意图**

除了有明显JTAG接口底座，还有一些需要根据芯片引脚和辅助工具来自己搜索。如JTAGulator、JTAGenum。

![image.png](https://image.3001.net/images/20210517/1621254270_60a2607e36cf211de88ba.png!small)

###

 **3.1.3 调试工具--硬件﻿**

 **BusPirate**

BusPirate是一个开放源代码的黑客工具，提供访问UART、JTAG、I2C等功能。

![image.png](https://image.3001.net/images/20210517/1621254272_60a26080bdc4d96d90bee.png!small)

 **Jlink**

SEGGER J-Links是市场上使用最广泛的调试探针系列。无与伦比的性能，丰富的功能集，支持较多的CPU以及与较好的兼容性。

![image.png](https://image.3001.net/images/20210517/1621254273_60a26081e6a7bd69f2fe9.png!small)

 **3.1.4 调试工具—软件**

 **OpenOCD**

Open On-Chip Debugger（OpenOCD）是一个免费的开源JTAG调试软件，旨在使用调试适配器提供调试，系统内编程和边界扫描。

### 3.2 UART

 **3.2.1 简介**

通用非同步收发传输器（Universal Asynchronous
Receiver/Transmitter，通常称为UART）是一种异步收发传输器，是电脑硬件的一部分，将数据透过串列通讯和平行通讯间作传输转换。

简单来说，通过UART口可以跟设备进行数据交互，访问Shell、烧录固件等。

 **3.2.2 示意图**

图片框出来的四个触点对应着UART使用到的GND、TX、RX、VCC引脚。

![image.png](https://image.3001.net/images/20210517/1621254275_60a26083149c0fdfc3757.png!small)

 **3.2.3 调试工具—硬件**

常用的访问设备UART接口的工具有BusPirate、USBtoTTL等工具。

如图为某品牌USBtoTTL工具。

![image.png](https://image.3001.net/images/20210517/1621254277_60a2608550f61d45ed5e6.png!small)

 **3.2.4 调试工具—软件**

可使用Picocom、Putty等工具。

## 4\. Microcontroller Unit分析工具

### 4.1 侧信道

 **4.1.1 简介**

边信道攻击是一种攻击方式，它基于从密码系统的物理实现中获取的信息而非暴力破解法或是算法中的理论性弱点。例如：时间信息、功率消耗、电磁泄露或甚是声音可以提供额外的信息来源，这可被利用于对系统的进一步破解。而侧信道就是指设备在运算时，敏感信息通过功率变化、时间变化等泄露出来。

 **4.1.2 常用工具**

> 示波器
>
> Chipwhisperer
>
> 逻辑分析仪
>
> 万用表
>
> 隔离变压器
>
> 热风机、电烙铁

这里着重介绍下Chipwhisperer和逻辑分析仪。

逻辑分析仪

逻辑分析仪是一种采集和显示数字电路信号的仪器。逻辑分析仪的最主要作用在于时序判定。逻辑分析仪不像示波器那样有许多电压等级，只显示两个电压，逻辑1和逻辑0，以及不确定x。使用逻辑分析仪可以读取芯片的数字信号，并对数字信号进行解码。

![image.png](https://image.3001.net/images/20210517/1621254278_60a26086578f1ade99678.png!small)

逻辑分析仪信号解码界面如下图所示：将逻辑分析仪的探针接入芯片的引脚，在对通信数据进行解码。逻辑分析仪可以解码常见的UART/SPI/I2C等协议。

![image.png](https://image.3001.net/images/20210517/1621254279_60a260875419051003332.png!small)

Chipwhisperer

ChipWhisperer是一个开放源代码的侧信道攻击平台，ChipWhisperer主要致力于功耗分析攻击以及电压和时钟故障，这些中断会破坏设备的电源或时钟信号，从而导致意外行为（例如，跳过密码检查）。在进行功率测量时，通常还需要示波器进行辅助。

![image.png](https://image.3001.net/images/20210517/1621254280_60a26088e11fbca59c232.png!small)

### 4.2 Flash Dump

 **4.2.1 简介**

物理设备上的 flash 芯片常用于存储固件，如果这个芯片没有设置读-写保护权限的话，攻击者可以直接读取(通过 dump
或者调试接口)固件分析并修改固件以绕过接口访问的认证。同时，攻击者可通过dump出的固件进一步分析业务逻辑，从而对整个业务有更清晰的了解。

 **4.2.2 示意图**

![image.png](https://image.3001.net/images/20210517/1621254284_60a2608ca7bb05e78fffc.png!small)

 **4.2.3 读取工具—硬件**

BusPirate

热风机和电烙铁

 **4.2.4 读取工具—软件**

#### Flashrom

flashrom是一种用于识别，读取，写入，验证和擦除闪存芯片的实用程序。

## 5\. 通信协议分析工具

### 5.1 近场通信

 **5.1.1 蓝牙**

蓝牙，一种无线通讯技术标准，用来让固定与移动设备，在短距离间交换资料，以形成个人局域网。其使用短波特高频无线电波，经由2.4至2.485
GHz的ISM频段来进行通信。蓝牙有两种通信信道：广播信道和数据信道（advertising channels and data
channels）,对应的通道如下图，其中广播信道只使用37，38，39这三个通道。数据信道共包含37个信道。在数据传输时，设备间会使用跳频算法在数据通道间跳频。常见的CC2540不具备捕获数据通道中的数据的能力，需使用昂贵的专业蓝牙设备（数万元）或Ubertooth进行捕获（几百元，但是不稳定且只能捕获BLE）。

常见的两种蓝牙类型：

> CLASSIC
>
> BLE

 **BLE分析工具**

Ubertooth One是适用于蓝牙实验的开源2.4
GHz无线开发平台。Ubertooth允许你在监视模式下使用蓝牙，这种“混杂”模式使无线电将接收到的所有内容传递到主机上。

![image.png](https://image.3001.net/images/20210517/1621254288_60a260902f29c36886fa2.png!small)

 **5.1.2 ZigBee**

ZigBee，也称紫蜂，是一种低速短距离传输的无线网络协议，底层是采用IEEE
802.15.4标准规范的媒体访问层与物理层。主要特色有低速、低耗电、低成本、支持大量网络节点、支持多种网络拓扑、低复杂度、可靠、安全。

 **捕获工具—硬件**

 **CC2531 USB dongle**

CC2531 USB dongle可为PC提供访问IEEE802.15.4 / ZigBee应用程序的接口，随附CC2531ZNP-Prod固件，可将dongle直接插入PC / Raspberry等中用作Zigbee数据包嗅探器。

![image.png](https://image.3001.net/images/20210517/1621254289_60a260913f579e749875f.png!small)

 **RZUSBSTICK**

RZUSBSTICK是用于开发，调试和演示各种低功耗无线应用（包括IEEE 802.15.4、6LoWPAN和ZigBee网络）的工具。

![image.png](https://image.3001.net/images/20210517/1621254290_60a2609270db7aa0056f7.png!small)

 **分析工具—软件**

SmartRF Packet Sniffer

SmartRF Packet Sniffer是一种PC软件应用程序，可以显示和存储由侦听RF设备捕获的无线电数据包。

![image.png](https://image.3001.net/images/20210517/1621254291_60a2609381fe3bc63ce9c.png!small)

 **KillerBee**

KillerBee是基于Python的框架和工具集，用于探索和利用ZigBee和IEEE 802.15.4网络的安全性。
使用KillerBee工具和兼容的IEEE 802.15.4无线电接口，您可以窃听ZigBee网络，重放流量，攻击密码系统等等。
使用KillerBee框架，您可以构建自己的工具，实现ZigBee模糊测试、仿真和攻击终端设备，路由器和协调器等等。

###

 **5.1.3 RAW RF(433Mhz)**

433MHz技术使用433MHz无线频段，因此相比于WiFi和Zigbee，433MHz的显著优势是无线信号的穿透性强、能够传播得更远。但其缺点也是很明显的，就是其数据传输速率只有9600bps，远远小于WiFi和Zigbee的数据速率，因此433Mhz技术一般只适用于数据传输量较少的应用场合。

 **捕获工具—硬件**

 **HackRF One**

HackRF One是一款软件定义的无线电设备，能够发送或接收1 MHz至6 GHz的无线电信号。HackRF
One是为支持现代和下一代无线电技术的测试和开发而设计的，它是一种开源硬件平台，可用作USB外设或编程用于独立操作。

![image.png](https://image.3001.net/images/20210517/1621254293_60a2609501f40d0336c8a.png!small)

 **信号分析工具和平台**

 **URH**

Universal Radio
Hacker（URH）是用于无线协议调查的完整套件，并具有对许多常见的软件定义无线电的本地支持。URH可以轻松解调信号，并自动检测调制参数，从而轻松识别空中飞过的比特和字节。

如下图所示，使用HackRF + URH捕获通信数据模拟信号，并将模拟信号解调为数字信号。

![image.png](https://image.3001.net/images/20210517/1621254294_60a260967504267488bb3.png!small)

 **5.1.4 RFID（IC卡、ID卡）**

射频识别是一种无线通信技术，可以通过无线电信号识别特定目标并读写相关数据，而无需识别系统与特定目标之间建立机械或者光学接触。
无线电的信号是通过调成无线电频率的电磁场，把数据从附着在物品上的标签上传送出去，以自动辨识与追踪该物品。

我们常用的IC卡、ID卡使用的就是该技术。

 **分析工具—硬件**

Proxmark

Proxmark是一种RFID多功能工具，可与全球绝大多数RFID标签和系统进行高层和底层交互。

![image.png](https://image.3001.net/images/20210517/1621254295_60a26097a61ecb377d640.png!small)

分析工具—软件

Proxmark 3

Proxmark
3是专用的、功能强大的多功能工具，用于RFID分析，可为任何以125KHz、134KHz和13.56MHz频率工作的RFID系统提供读取、写入、分析、监听、重放、仿真、调制、解调、解码、编码、解密和加密。

### 5.2 Wlan&以太网

Wlan和以太网的抓包和分析方法相关教程较多，不在此赘述。

### 5.3 4G/5G通信

4G/5G通信相关的分析设备成本相较于其他通信方式要贵出许多，常用的设备如下所示。

 **硬件工具**

Ettus B210和BladeRF属于高性能SDR设备，可以较好的实现4G/5G通信模拟和监听。

ettus b210

![image.png](https://image.3001.net/images/20210517/1621254298_60a2609ab8b18ed017bb2.png!small)

BladeRF

![image.png](https://image.3001.net/images/20210517/1621254299_60a2609bd0c6cdd55909e.png!small)

 **4G/5G平台工具**

#### srsRAN

srsRAN是一个免费的开源4G和5G软件无线电套件。srsRAN套件当前包括：

> srsUE - a full-stack 4G and 5G NSA UE (User Equipment) application (5G SA
> coming soon)
>
> srsENB - a full-stack 4G eNodeB (Basestation) application (5G NSA and SA
> coming soon)
>
> srsEPC - a light-weight 4G EPC (Core Network) implementation with MME, HSS
> and S/P-GW

AirScope

AirScope是一款软件无线电LTE空中接口分析仪。它使用标准PC和通用SDR前端为网络分析提供实时无线解码功能。SDR前端设备指ettus
b210、BladeRF。

### 5.4 接触式智能卡

智能卡分为接触式和非接触式，接触式卡片其芯片直接封装在卡基表面，而非接触式卡片是由芯片和线圈组成。智能卡通常使用基于iso7816标准的通信协议。

 **分析工具—硬件 &软件**

Osmocom SIMtrace 2

Osmocom SIMtrace 2是一个软件、固件和硬件系统，用于被动跟踪SIM卡和移动电话之间的SIM-ME通信以及远程SIM操作。

![image.png](https://image.3001.net/images/20210517/1621254301_60a2609d3ed35552c4766.png!small)

### 5.5 USB

通用串行总线是连接计算机系统与外部设备的一种串口总线标准，也是一种输入输出接口的技术规范，被广泛地应用于个人电脑和移动设备等信息通讯产品。

 **USB工具—硬件 &软件**

FaceDancer

FaceDancer板是充当“远程控制” USB控制器的简单硬件设备。
借助适当的软件，你可以使用这些开发板快速轻松地仿真USB设备，并对USB主机控制器进行Fuzz测试。

![image.png](https://image.3001.net/images/20210517/1621254302_60a2609e87bda52c8dc11.png!small)

## 6\. 辅助设备

### 隔离变压器

隔离变压器是一种变压器，通常出于安全原因，用于将电力从交流电源传输到某些设备或设备，同时将受电设备与电源隔离。统的单相电源线由火线、零线和地线组成。当多个物理上分开的设备共用一条电源线时，由于设备的接地电位不同，有可能产生接地回路。接地的测试设备（如示波器）可能会在无意中导致这些设备的电源短路。而且，交流电源线上会产生高频噪声，从而导致敏感的传感器和仪器出现问题。通过在电源输入端与设备之间正确使用隔离变压器，可以避免所有这些问题。

![image.png](https://image.3001.net/images/20210517/1621254303_60a2609fd4bf6d3fe9278.png!small)

### 万用表

万用表，是一种多用途电子测量仪器，主要用于物理、电气、电子等测量领域，一般包含电流表、电压表、电阻表等功能。

![image.png](https://image.3001.net/images/20210517/1621254305_60a260a104196f9e54993.png!small)

## 7\. 小结

本文按照物联网嵌入式设备的抽象模型简要的介绍了常用的硬件分析工具，内容并不难懂，但也可以看出物联网技术的复杂性。文章里每一小节都只是一个引子，工程师和爱好者们可以从使用工具出发，结合实践，从而可以更好的理解每一个单独的领域。

