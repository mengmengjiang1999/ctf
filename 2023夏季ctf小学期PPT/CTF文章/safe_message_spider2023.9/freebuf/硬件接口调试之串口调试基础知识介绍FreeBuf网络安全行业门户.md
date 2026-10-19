## 前言

对于IOT的漏洞挖掘，硬件调试是一项相对简单的技能，通过串口调试作为辅助，也许可以获得路由器的固件、开启ssh、获取shell等等，下面对路由器串口调试必备的基础知识作简要介绍。

## 认识串口小板

如图，是一款USB TO
TTL转换板，这款小板支持3种供电模式：对外输出5V、对外输出3.3V和由外部供电。正面有一个跳帽，跳帽跳到3V3，小板由USB供电，对外输出3.3V；跳帽跳到5V，小板由USB供电，对外输出5V；摘下跳帽，由外部供电，要求3.3V或5V的直流电源。

![v2-d4cdb58bf5629adf7b46082d7efcc4d5_720w.png](https://image.3001.net/images/20221021/1666332238_6352364eacd87d5ea8d23.png!small)

  

![v2-aa7dab451e8a7eba529ff9b2fae4f21c_720w.png](https://image.3001.net/images/20221021/1666332239_6352364f655fc149ca880.png!small)

​另外需要关注的是3个LED灯，分别是TXD LED、RXD LED、POWER LED。通常观察灯来知晓小板的运行情况。电源供电后，POWER
LED常亮，有数据发送和接收时，TXD LED和RXD LED会闪烁。

## 寻找目标路由器串口

大多数家用路由器开发板上都会有串口针脚，有的串口印有TXD、RXD 、GND这样的标识，有的没有标识，可以用万用表测试一下。

![v2-a8d47def46b251c93157a74e6b06fd87_720w.png](https://image.3001.net/images/20221021/1666332240_63523650487ab3f5745bb.png!small)

​将万用表档位调整到20V，万用表黑色针接触天线，万用表红色针分别接触四个开发板串口针脚。电源脚为3.3V或5V，GND脚为0，RX和TX脚的电压值不能确定，有的路由器RX和TX脚都是高电压，有的路由器TX脚在开机过程中会有电压变化。

## 连接方式

一般是用USB口供电，TXD连接RXD，RXD连接TXD，GND连接RXD

![v2-b92eacad14003722b4ed63cefc61dced_720w.png](https://image.3001.net/images/20221021/1666332241_6352365123c8d2fef9a70.png!small)

​如果获取到目标路由器开发板的硬件手册，也可以对照硬件手册，找到主控芯片的TXD和RXD引脚进行连接。

## 调试软件选择和串口驱动安装

windows10下 CH340/CH341 USB转串口驱动安装

SecureCRT 、串口调试助手 、xshell等

## com端口和波特率设置

以windows10为例，COM端口查看如下

![v2-5fa362ece94d32e2e8940c8cecca3e18_720w.png](https://image.3001.net/images/20221021/1666332241_63523651a8921ab17b0ef.png!small)

​波特率常用的有9600、115200等。如果串口输出乱码，则有可能是波特率设置错误。

