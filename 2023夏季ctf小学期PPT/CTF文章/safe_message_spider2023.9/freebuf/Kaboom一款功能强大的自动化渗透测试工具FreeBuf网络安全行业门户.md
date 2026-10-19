**今天，我们给大家介绍的是一款名叫Kaboom的自动化渗透测试工具，广大研究人员可以使用这款功能强大的工具来完成日常的渗透测试任务。**

![Kaboom](https://image.3001.net/images/20190305/1551776646_5c7e3b86cfa62.png!small)

## 项目地址

Kaboom：<https://github.com/Leviathan36/kaboom>

## 工具介绍

Kaboom实际上是一个渗透测试脚本，它可以帮助我们自动化完成渗透测试任务。它可以胜任渗透测试过程中每一个阶段的多个任务：

###  **1、 信息收集[nmap-unicornscan]**

> a) TCP扫描
>
> b) UDP扫描

###  **2、 漏洞评估[nmap-nikto-dirb-searchsploit-msfconsole]（可测试多种服务）**

> a) smb
>
> b) ssh
>
> c) snmp
>
> d) smtp
>
> e) ftp
>
> f) tftp
>
> g) ms-sql
>
> h) mysql
>
> i) rdp
>
> j) http
>
> k) https
>
> l) 等等...

它还可以搜索CVE并直接在开放漏洞利用库或Metasploit数据库中搜索相应的漏洞利用代码。

###  **3、 漏洞利用[hydra]**

> 爆破SSH

## 工具使用

Kaboom支持以下两种模式：

###  **1、 交互模式**

输入“kaboom”，按下回车键，剩下的脚本会帮你完成。

###
![Kaboom](https://image.3001.net/images/20190305/1551776673_5c7e3ba1125f1.png!small)
**2、 非交互模式**

    
    
    kaboom <results_path> <nic> <target_ip> [-s or --shutdown]

如果你使用shutdown选项，Kaboom将会在完成扫描任务后关闭目标设备。

如果你想查看帮助信息，可使用下列命令：

    
    
    kaboom -h (or --help)

![Kaboom](https://image.3001.net/images/20190305/1551776706_5c7e3bc2bf688.png!small)

## 目录层级

Kaboom的命令运行结果存储方式如下：

![Kaboom](https://image.3001.net/images/20190305/1551776717_5c7e3bcd2e044.png!small)

### 许可证协议

Kaboom遵循[GPLv3](https://github.com/Leviathan36/kaboom/blob/master/LICENSE)许可证协议。

***参考来源：[kaboom](https://github.com/Leviathan36/kaboom)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

