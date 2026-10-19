## 背景概述

**近日，深信服安全团队捕获到Bluehero挖矿蠕虫最新变种，该挖矿蠕虫集多种功能为一体，释放后门程序窃取主机信息，释放Mimikatz模块、嗅探模块、“永恒之蓝”攻击模块、LNK漏洞利用模块（CVE-2017-8464）进行传播和反复感染，最终释放挖矿模块进行挖矿。**

通过威胁情报查询，Bluehero挖矿蠕虫最新变种两个关键文件的创建时间均为6月3号，可以确认近期刚开始进行活动，并且有扩大感染面的趋势。深信服安全团队在第一时间捕获到该变种进行分析：

![](https://image.3001.net/images/20190617/1560740067_5d0700e362fb8.png!small)

![](https://image.3001.net/images/20190617/1560740070_5d0700e68e65e.png!small)

Bluehero挖矿蠕虫变种运行流程如下：

![](https://image.3001.net/images/20190617/1560740073_5d0700e9f1c3b.png!small)

## 详细分析

### Download.exe

创建C:\WebKitsSDK\2.7.92目录：

![](https://image.3001.net/images/20190617/1560740077_5d0700ed7ae13.png!small)

释放并运行后门程序，该后门程序的文件名为随机字符：

![](https://image.3001.net/images/20190617/1560740080_5d0700f0c5cf4.png!small)

通过链接<http://fid.hognoob.se/SunloglicySrv.exe>下载SunloglicySrv.exe到C:\WebKitsSDK\2.7.92并运行：

![](https://image.3001.net/images/20190617/1560740083_5d0700f3853fb.png!small)

从C2服务器下载相应的配置文件cfg.ini，如下所示：

![](https://image.3001.net/images/20190617/1560740090_5d0700fa6f83b.png!small)

相应的C2服务器URL地址：

> <http://uio.hognoob.se:63145/cfg.ini>
>
> <http://uio.heroherohero.info:63145/cfg.ini>

下载回来的配置文件中包含挖矿流量的矿池地址：

    
    
    pxi.hognoob.se:35791
    
    pxx.hognoob.se:35789

下载模块的URL地址：

> <http://fid.hognoob.se/download.exe>

![](https://image.3001.net/images/20190617/1560740097_5d0701011d9ac.png!small)

### 后门程序

自复制到C:\Windows\system32\目录下，名字为随机字符：

![](https://image.3001.net/images/20190617/1560740100_5d070104c6b16.png!small)

将复制体注册为服务，服务名为Abfdef：

![](https://image.3001.net/images/20190617/1560740104_5d0701082bbcd.png!small)

通过服务启动，连接C&C端q1a.hognoob.se的1889端口，发送主机信息：

![](https://image.3001.net/images/20190617/1560740109_5d07010d2e06b.png!small)

### SunloglicySrv.exe

自复制到windows目录，以随机字符命名：

![](https://image.3001.net/images/20190617/1560740112_5d0701107e213.png!small)

通过命令行重新启动：

![](https://image.3001.net/images/20190617/1560740115_5d070113b8a35.png!small)

释放Mimikatz模块，用于抓取域用户密码：

![](https://image.3001.net/images/20190617/1560740120_5d07011899033.png!small)

释放嗅探模块，扫描指定IP段：

![](https://image.3001.net/images/20190617/1560740123_5d07011be3026.png!small)

![](https://image.3001.net/images/20190617/1560740130_5d070122091b5.png!small)

设置ipsec规则，过滤掉相关的协议流量：

![](https://image.3001.net/images/20190617/1560740134_5d070126577ad.png!small)

关闭主机防火墙、网络共享、杀毒软件等，如下所示：

![](https://image.3001.net/images/20190617/1560740139_5d07012b3afd6.png!small)

创建相应的计划任务，如下所示：

![](https://image.3001.net/images/20190617/1560740145_5d07013173be1.png!small)

释放“永恒之蓝”攻击模块，进行内网横向传播：

![](https://image.3001.net/images/20190617/1560740152_5d0701387c488.png!small)

释放LNK漏洞利用模块：

![](https://image.3001.net/images/20190617/1560740159_5d07013f88c9c.png!small)

利用LNK漏洞（CVE-2017-8464）下载最开始的download.exe模块，加速传播：

![](https://image.3001.net/images/20190617/1560740163_5d070143b2f95.png!small)

C:\Windows\Temp目录下释放挖矿模块，并运行挖矿程序：

![](https://image.3001.net/images/20190617/1560740167_5d0701475df9e.png!small)

![](https://image.3001.net/images/20190617/1560740174_5d07014e2913b.png!small)

挖矿流量如下：

![](https://image.3001.net/images/20190617/1560740181_5d070155b7bc0.png!small)

## IOC

### DNS:

    
    
    q1a.hognoob.se

### URL：

> <http://fid.hognoob.se/download.exe>
>
> <http://uio.hognoob.se:63145/cfg.ini>
>
> <http://uio.heroherohero.info:63145/cfg.ini>
>
> <http://fid.hognoob.se/SunloglicySrv.exe>

### MD5：

    
    
    0FE77BC5E76660AD45379204AA4D013C（download.exe）
    
    7B6308828105E080D7F238BB14D28874（SunloglicySrv.exe）

## 解决方案

1、深信服为广大用户免费提供查杀工具，可下载如下工具，进行检测查杀。

> 64位系统下载链接：<http://edr.sangfor.com.cn/tool/SfabAntiBot_X64.7z>
>
> 32位系统下载链接：<http://edr.sangfor.com.cn/tool/SfabAntiBot_X86.7z>

3、更新MS17-010 补丁以及 CVE-2017-8464漏洞补丁。

 ***本文作者：深信服千里目安全实验室，转载请注明来自FreeBuf.COM**

