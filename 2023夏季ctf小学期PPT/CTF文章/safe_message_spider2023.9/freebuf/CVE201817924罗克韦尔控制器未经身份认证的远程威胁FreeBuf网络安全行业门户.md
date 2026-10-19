Rockwell
Automation是全球最大的自动化和信息化公司之一，拥有众多的产品，涵盖高级过程控制、变频器、运动控制、HMI、马达控制中心、分布式控制系统、可编程控制器等。

## Part1 漏洞状态

漏洞细节| 漏洞POC| 漏洞EXP| 在野利用  
---|---|---|---  
有| 有| 无| 无  
  
### Part2 漏洞描述

‍漏洞名称|

罗克韦尔控制器未经身份认证的远程威胁  
  
---|---  
CVE编号| CVE-2018-17924  
漏洞等级| 高危  
公开状态| 公开  
漏洞描述|

多款Rockwell
Automation产品中存在安全漏洞，该漏洞源于程序缺少身份验证。攻击者可通过发送CIP连接请求，完成连接后发送新的IP配置利用该漏洞修改系统配置并造成设备与系统之间的通信丢失。  
  
时间线|

2018-12-07  
  
影响产品  
  
|

MicroLogix 1400 Controllers Series A（全部版本）

Series B 21.003及之前版本，

Series C 21.003及之前版本，

1756-ENBT（全部版本），

1756-EWEB Series A（全部版本），

1756-EWEB Series B（全部版本），

1756-EN2F Series A（全部版本），

1756-EN2F Series B（全部版本），

1756-EN2F Series C 10.10及之前版本，

1756-EN2T Series A（全部版本），

1756-EN2T Series B（全部版本），

1756-EN2T Series C（全部版本），

1756-EN2T 10.10及之前版本，

1756-EN2TR Series A（全部版本），

1756-EN2TR Series B（全部版本），

Series C 10.10及之前版本，

1756-EN3TR Series A（全部版本），

1756-EN3TR Series B 10.10及之前版本（1756 ControlLogix EtherNet/IP通信模块）。  
  
 **测试设备:** AB1756

## Part3 漏洞分析

AB PLC使用ENIP协议通信，未判断数据来源，分析RS
linx与PLC通信的数据包，确认只需要获取session后建立连接，便可向PLC发送修改IP的指令，使得PLC与现有设备的连接断开。

![图片](https://image.3001.net/images/20230518/1684394883_6465d38379adadaffc72e.jpg!small)

  *  **构建POC**

先使用命令码0x65，注册session，并将返回的session拼接到修改IP的命令内，即可完成远程修改IP的行为。

![图片](https://image.3001.net/images/20230518/1684394900_6465d3940eedf4d014e8a.jpg!small)

![图片](https://image.3001.net/images/20230518/1684394908_6465d39ccb14865cdc9ab.jpg!small)

![图片](https://image.3001.net/images/20230518/1684394926_6465d3ae6d5aa40b5b679.jpg!small)

  *  **验证**

修改之前PLC
IP为192.168.1.44![图片](https://image.3001.net/images/20230518/1684394953_6465d3c920ceb4fbf0995.jpg!small)

![图片](https://image.3001.net/images/20230518/1684394961_6465d3d19fa06419e14c3.jpg!small)

运行POC，可以到看PLC 的IP 已经修改为192.168.1.144

![图片](https://image.3001.net/images/20230518/1684394973_6465d3dd387ece687a73e.jpg!small)

![图片](https://image.3001.net/images/20230518/1684394980_6465d3e4ba1c0b188061f.jpg!small)

![图片](https://image.3001.net/images/20230518/1684394989_6465d3edccc2af5a4ab84.jpg!small)

## Part4 修复建议

厂家已发布修复漏洞的补丁和固件，尽快升级到最新版本。

