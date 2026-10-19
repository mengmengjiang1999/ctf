**HW期间，为防范钓鱼，即日起FreeBuf将取消投稿文章的一切外部链接。给您带来的不便，敬请谅解~**

![](https://image.3001.net/images/20210405/1617604231_606aae873f5f131fd9c4a.png!small)

## 关于InveighZero

InveighZero是一款集LLMNR/NBNS/mDNS/DNS/DHCPv6欺骗和中间人攻击于一身的工具，该工具旨在帮助渗透测试专家和红队研究人员找出目标Windows系统中的安全缺陷。InveighZero基于C#开发，当前版本中的很多功能都跟PowerShell版本的Inveigh（https://github.com/Kevin-Robertson/Inveigh）类似。

## 提权模式功能（要求管理员权限）

> SMB捕捉：基于数据包欺骗；
>
> LLMNR欺骗：基于数据包欺骗；
>
> NBNS欺骗：基于数据包欺骗；
>
> mDNSs欺骗：基于数据包欺骗；
>
> DNS欺骗：基于数据包欺骗；
>
> DHCPv6欺骗：基于数据包欺骗；
>
> Pcap输出：TCP和UDP数据包；
>
> 数据包欺骗终端输出：SYN数据包，SMB Kerberos协商等；

## 非提权模式功能

> LLMNR欺骗：基于UDP监听器；
>
> NBNS欺骗：基于UDP监听器；
>
> mDNSs欺骗：基于UDP监听器；
>
> DNS欺骗：基于UDP监听器；
>
> DHCPv6欺骗：基于UDP监听器；
>
> 注意：NBNS欺骗可以在NBNS启用的情况下在所有系统上正常运行。LLMNR和mDNS欺骗貌似只能在Windows 10和Windows Server
> 2016上正常工作。

## 其他功能

> HTTP捕捉：基于TCP监听器；
>
> 代理认证捕捉：基于TCP监听器；

## 暂不支持的功能

> ADIDNS攻击；
>
> HTTP-SMB中继；
>
> HTTPS监听器；
>
> Kerberos Kirbi输出；

## 环境要求

> .NET Framework >= 3.5

## 工具获取

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/Kevin-Robertson/InveighZero.git

## 工具使用

使用默认配置执行：

    
    
    Inveigh.exe

设置主IP地址：

    
    
    Inveigh.exe -IP 192.168.1.1

向其他系统发送伪造（欺骗攻击）流量：

    
    
    Inveigh.exe -IP 192.168.1.1 -SpooferIP 192.168.1.2

针对HTTP和SMB的pcap输出：

    
    
    Inveigh.exe -Pcap Y -PcapTCP 80,445

## 工具运行截图

![](https://image.3001.net/images/20210405/1617604271_606aaeaf942431c38b093.png!small)

![](https://image.3001.net/images/20210405/1617604278_606aaeb60551a06aabec1.png!small)

## 项目地址

InveighZero：https://github.com/Kevin-Robertson/InveighZero

