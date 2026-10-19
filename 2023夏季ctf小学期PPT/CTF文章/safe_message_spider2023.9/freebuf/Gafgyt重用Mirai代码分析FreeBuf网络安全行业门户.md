Gafgyt（又名Bashlite）是著名的恶意软件家族，主要针对物联网设备发起攻击，例如华为路由器、Realtek 路由器和华硕网络设备等。Gafgyt
还使用很多漏洞（CVE-2017-17215、CVE-2018-10561）用于载荷投递。

## 重用Mirai代码

近期，几个Gafgyt的变种重用了Mirai的一些代码模块：

> HTTP 洪水
>
> UDP 洪水
>
> TCP 洪水
>
> STD 模块
>
> Telnet 爆破

分析的样本是
[4b94d1855b55fb26fc88c150217dc16a](https://www.virustotal.com/gui/file/da20bf020c083eb080bf75879c84f8885b11b6d3d67aa35e345ce1a3ee762444)与
[cd3b462b35d86fcc26e4c1f50e421add](https://www.virustotal.com/gui/file/1b3bb39a3d1eea8923ceb86528c8c38ecf9398da1bdf8b154e6b4d0d8798be49)。

## HTTP 洪水

攻击者通过向攻击目标发送大量 HTTP 请求进行 DDoS 攻击。Gafgyt 使用了 Mirai 泄露的代码，下图显示了这种区别：

![](https://image.3001.net/images/20210716/1626369991_60f06fc713cd63251752e.png!small)

左侧是 Gafgyt 反编译的代码，右侧是 Mirai 的源码。

## UDP 洪水

攻击者通过向攻击目标发送大量 UDP 数据包进行 DDoS 攻击。Gafgyt 重用 Mirai 泄露的代码实现了 UDP 洪水的功能：

![](https://image.3001.net/images/20210716/1626370309_60f07105c8b2fb73113fc.png!small)

## TCP 洪水

Gafgyt 执行所有类型的 TCP 洪水攻击，如 SYN、PSH、FIN 等。在 TCP 洪水中，攻击者利用正常的 TCP
三次握手向受害者发送大量请求，导致服务器无响应。

![](https://image.3001.net/images/20210716/1626370317_60f0710dbfde4b102591a.png!small)

左侧为 Gafgyt 的 TCP 洪水模块，右侧是 Mirai 的类似代码。

## STD 模块

Gafgyt 包含将随机字符串（硬编码的字符串数组）发送到特定的 IP 地址，Mirai 也有类似的功能。

![](https://image.3001.net/images/20210716/1626370326_60f0711617ebd898f7f06.png!small)

## Telnet 爆破

Gafgyt 除了洪水模块，还包含一些其他修改过的模块，例如 Telnet 爆棚模块。

![](https://image.3001.net/images/20210716/1626370014_60f06fde1bf518270185b.png!small)

## 使用 CVE

Gafgyt 利用 IoT 设备的漏洞组建大规模僵尸网络，然后对特定的 IP 地址发起 DDoS 攻击。最近出现了很多 Gafgyt 的变种，例如
[986633b0f67994a14e4ead3ee4ccbd73](https://www.virustotal.com/gui/file/7fe8e2efba37466b5c8cd28ae6af2504484e1925187edffbcc63a60d2e4e1bd8)和
[725097e3213efb6612176adefda3d64f](https://www.virustotal.com/gui/file/25461130a268f3728a0465722135e78fd00369f4bccdede4dd61e0c374d88eb8)。都包含了多个漏洞利用模块，像针对华为路由器（CVE-2017-17215）、Realtek
设备（CVE-2014-8361）和 GPON 路由器（CVE-2018-10561）的攻击。

![](https://image.3001.net/images/20210716/1626370020_60f06fe4a394b53702e0c.png!small)![](https://image.3001.net/images/20210716/1626370330_60f0711ab155c840015f6.png!small)![](https://image.3001.net/images/20210716/1626370333_60f0711da1a262bc7fc35.png!small)Gafgyt
通常会使用 wget 获取载荷，再使用 chmod 赋予执行权限，最后执行该载荷。

![](https://image.3001.net/images/20210716/1626370027_60f06feb24fc7196bfb1a.png!small)

恶意脚本执行逻辑：

> 使用 wget 获取载荷
>
> 使用 chmod 赋予执行权限
>
> 执行载荷
>
> 删除载荷

![](https://image.3001.net/images/20210716/1626370043_60f06ffb27fabddc7cc81.png!small)

## 总结

恶意软件开发者不能总是开发全新的代码，研究人员发现恶意软件开发者会经常重用恶意软件泄露的源代码。

## IOC

    
    
    37.228.188.12  
    178.253.17.49  
    156.226.57.56  
    156.244.91.129  
    212.139.167.234  
    193.190.104.125  
    37.251.254.238  
    212.139.167.234  
    da20bf020c083eb080bf75879c84f8885b11b6d3d67aa35e345ce1a3ee762444  
    1b3bb39a3d1eea8923ceb86528c8c38ecf9398da1bdf8b154e6b4d0d8798be49  
    7fe8e2efba37466b5c8cd28ae6af2504484e1925187edffbcc63a60d2e4e1bd8   
    25461130a268f3728a0465722135e78fd00369f4bccdede4dd61e0c374d88eb8  
    4883de90f71dcdac6936d10b1d2c0b38108863d9bf0f686a41d906fdfc3d81aa  
    25461130a268f3728a0465722135e78fd00369f4bccdede4dd61e0c374d88eb8

## 参考来源

> [uptycs](https://www.uptycs.com/blog/mirai-code-re-use-in-gafgyt)

