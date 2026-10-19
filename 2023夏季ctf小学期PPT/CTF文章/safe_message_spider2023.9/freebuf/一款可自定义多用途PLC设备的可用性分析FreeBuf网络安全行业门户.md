## 一、概述

 **OpenPLC是一个基于易于使用软件的开源可编程逻辑控制器。OpenPLC项目是根据IEC
61131-3标准创建的，该标准定义了PLC的基本软件架构和编程语言。**

## 二、系统构成

OpenPLC项目由三部分组成：运行时(程序运行环境)，编辑器（下位机程序编写工具）和HMI Builder(上位机程序编写工具)。

> 1）运行时应安装在您的设备上，并负责执行您的PLC程序，且只能运行在Debian和ubuntu操作系统下。
>
> 2) 编辑器是在您的计算机上运行的软件，用于创建和编写PLC程序。
>
> 3) HMI Builder(ScadaBR组态软件工具），您可以创建漂亮的基于Web的动画，以反映您的过程状态。ScadaBR通过Modbus /
> TCP与OpenPLC Runtime(运行时)通信。

Openplc 与 I/O对应关系(Modbus地址映射)，如下所示：

![](https://image.3001.net/images/20190830/1567157410_5d68eca259984.png!small)

从图中可以看出，openplc 支持输入/输出数字量和输入/输出模拟量 I/O接口传输数据

Openplc 支持以下嵌入式平台I/O驱动，如下所示：

![](https://image.3001.net/images/20190830/1567157418_5d68ecaadc4a4.png!small)

### 2.1 程序运行环境

必须在您的设备上安装OpenPLC运行环境才能执行PLC程序。OpenPLC运行环境支持多个嵌入式系统平台，也可以作为软PLC安装在Windows和Linux机器上。您甚至可以使用从设备来扩展I
/ O点或将它们用作主软PLC I / O。

（1）支持部署openplc到嵌入式平台包括如下：

![](https://image.3001.net/images/20190830/1567157804_5d68ee2ce2107.png!small)

 **a)Openplc 运行于Raspberry PI（树莓派）**

1.下载bootloader和Raspbian操作系统到树莓派平台

2.在树莓派平台在线安装openplc开源项目，通过如下命令：

    
    
    sudo apt-get install git
    
    gitclone<https://github.com/thiagoralves/OpenPLC_v3.git>
    
    cd OpenPLC_v3&& ./install.sh rpi

3.安装成功后，通过web管理终端进行plc运行环境管理，输入如下命令：

[ _http://192.168.10.122:8080_](http://192.168.10.122:8080/)

![](https://image.3001.net/images/20190830/1567157840_5d68ee5090a96.png!small)

4.可以按照如下方式，进行plc梯形图程序下载到树莓派plc中

![](https://image.3001.net/images/20190830/1567157847_5d68ee571cea9.png!small)

![](https://image.3001.net/images/20190830/1567157852_5d68ee5c093d1.png!small)

5\. 树莓派平台I/O 与 openplc modbus 地址映射关系，如下所示：

![](https://image.3001.net/images/20190830/1567157869_5d68ee6d40d6a.png!small)

 **b) Openplc 运行于Unipi Industrial Platform**

安装步骤与部署到树莓派过程一致，唯一区别是支持的I/O控制点数不一样

支持openplc 部署到X86（linux或window）平台

1\. 在线安装部署openplc，输入如下命令：

    
    
    sudo apt-get install git
    
    gitclone<https://github.com/thiagoralves/OpenPLC_v3.git>
    
    cd OpenPLC_v3&& ./install.sh linux

2\. 通过docker方式快速安装部署openplc，输入如下命令：

docker run --name=open_plc -d --restart always fdamador/openplc -p 8080:8080
-p 502:502

3\. 部署成功，通过输入[http://ip:8080](http://ip:8080/)进入Openplc
运行环境web管理界面，在该界面可以进行如下操作：

启动/停止 PLC

上传/下载PLC梯形图程序

![](https://image.3001.net/images/20190830/1567158071_5d68ef37ace33.png!small)

### 2.2 下位机程序编辑器

OpenPLC Editor是一个允许您为OpenPLC运行时编写PLC程序的软件。程序根据IEC
61131-3标准编写。编辑器使用非常简单，并支持标准中定义的所有五种语言：梯形图（LD），功能块图（FBD），指令列表（IL），结构化文本（ST）和顺序功能图（SFC）。

1\. 编写梯形图程序，编写完后，进行程序编译，将编译生成的*.st文件上传到PLC运行环境，如下所示:

![](https://image.3001.net/images/20190830/1567158233_5d68efd9ed70f.png!small)

2.Plc程序支持标准功能块如线圈、寄存器、计数器、演示器等以及附件功能块如时钟、pid调节等，详解下图所示：

### 2.3 上位机编辑器

ScadaBR是一个开源的监控和数据采集（SCADA）系统，允许您为自动化项目创建交互式屏幕，也称为人机界面（HMI）。ScadaBR可以与OpenPLC通信，进行数据采集与实时监控。

安装下面步骤进行编辑器安装：

1.参考官网详细安装步骤，如下链接所示：

[ _https://www.openplcproject.com/reference-installing-scadabr_](https://www.openplcproject.com/reference-installing-scadabr)

2.安装成功后输入如下地址和admin/admin 进入编辑器界面，如下所示：

![](https://image.3001.net/images/20190830/1567158417_5d68f0912ceab.png!small)

编写上位机组态程序：

1.利用如下界面进行图形组态，组态完成后与openplc进行实时通信

![](https://image.3001.net/images/20190830/1567158479_5d68f0cf1b862.png!small)

![](https://image.3001.net/images/20190830/1567158593_5d68f141a62d0.png!small)

## 三、总结

### 1\. Openplc运行环境

可以运行嵌入式操作平台如Raspberry PI（树莓派）、Unipi Industrial Platform
等平台也可以运行X86平台，模拟一个真实plc基本控制功能，可以进行数字量和模拟量的控制。并且openplc
已经内置嵌入式平台I/O硬件的驱动。Openplc 内部已经和嵌入式I/O进行了地址映射，可以对I/O进行操作与控制。Openplc
支持modbus协议，支持读线圈(1)、读输入(2)、读保存寄存器（3）、读输入寄存器(4)、写线圈(5)、写寄存器（6）、写多线圈（15）、写多寄存器（16）等基本功能码。目前支持modbus和dnp3协议。

### 2.Openplc 下位机编程

openplc提供配套plc下位机编程工具，支持梯形图（LD），功能块图（FBD），指令列表（IL），结构化文本（ST）和顺序功能图（SFC)5种编程语言，程序编写好后，能够将编译后的程序上传到嵌入式平台(实plc)或X86平台(软plc)，并在平台上执行plc程序运算。

### 3.Openplc 上位机编程

openplc提供配套plc上位机编程工具(ScadaBR)，支持组态软件开发，进行plc设备数据采集与监控。

ScadaBR 采用modbus协议与plc实时通信。

### 4.基于嵌入式平台的openplc或者软openplc

只能应用于简单教学、研究、工业控制、网络竞赛、CTF、自定义工艺高交互蜜罐等场景，不能应用于生产环境(稳定性、可靠性、实时性未进行充分测试)

### 5\. 支持情况

目前openplc 已经支持许多价格低廉嵌入式平台的驱动，如下所示：

![](https://image.3001.net/images/20190830/1567159310_5d68f40e0a1d7.png!small)

目前openplc 只支持dnp3和modbus协议，如果想支持其它工控协议，需要自行添加工控协议进行扩展，如下所示：

![](https://image.3001.net/images/20190830/1567159812_5d68f60489e00.png!small)

## 四、结束

> openplc 运行环境、上位机编辑器、下位机编辑器源码参考地址：<https://github.com/thiagoralves>

 ***本文原创作者：yy0308，本文属于FreeBuf原创奖励计划，未经许可禁止转载**

