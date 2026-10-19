「中睿大学」是中睿天下建设的网络攻防学习、交流与分享平台。聚焦「实战对抗」，基于中睿天下多年一线攻防实战经验，分享行业知识及优秀实践，帮助合作伙伴及用户等提升网络安全监测预警、分析研判、态势感知、攻击溯源以及应急处置等攻防能力。

这次，我们走进「中睿大学」系列课程之“内存取证第一步——进程内存Dump与内存镜像Dump”。

###  **#内存转储#**

内存转储是将内存所运行的程序中所有数据通过调试器保存到磁盘中的过程。系统崩溃时，将内存中的数据转储保存在转储文件中，供给有关人员进行排错分析。其生成所保存的文件被称作内存转储文件，主要用于程序的调试和内存取证。

###  **#转储系统内存镜像#**

用于对整个系统内存进行分析，寻找是否存在恶意程序。转储速度依照系统物理内存大小而定，相比单个进程的转储文件更加全面，但与此同时速度也较慢。明确定位到恶意程序时，将其进程内存转储进行分析，更加灵活、快速。

本文主要介绍在Windows与Linux系统下如何提取内存文件，分为单个进程内存的转储与整个系统内存的转储。

##  **1\. Windows系统下如何转储内存**

###  **进程内存转储**

 **#任务管理器#**

◆ 简介

任务管理器为Windows系统自带工具，用于提供有关计算机性能的信息，并且显示计算机上所运行的程序和进程详细信息。

◆ 使用方式

打开运行对话框（Win+R）—>输入 taskmgr

◆ 环境限制

该工具为Windows系统自带工具  
仅支持在Windows环境下使用

◆ 转储进程内存方式

选定目标进程右键，点击创建转储文件即可。

![](https://image.3001.net/images/20210311/1615432291_60498a634d7b38e534529.png!small)![](https://image.3001.net/images/20210311/1615432302_60498a6e93d9bd7192b62.png!small)

保存路径：

C:\Users\用户\AppData\Local\Temp\进程名.DMP![](https://image.3001.net/images/20210311/1615432323_60498a8366f0caf4fccbf.png!small)

 **#ProcessExplorer#**

◆ 简介

一款Windows系统与应用程序监控工具，结合了文件监视和注册表监视两个工具的功能，还增加了多项重要的增强功能，此工具支持64位Windows系统，可以理解为一个增强版的任务管理器，转储进程内存与任务管理器相似。

◆ 下载地址

https://docs.microsoft.com/en-us/sysinternals/downloads/process-explorer

◆ 环境限制

ProcessExplore仅可在Windows系统下使用

Windows 7/Windows 2008 以下环境下需要安装补丁KB2758857后才可正常使用

### ◆ 转储进程内存方式

1\. 以管理员身份打开procexp.exe

![](https://image.3001.net/images/20210311/1615432352_60498aa031579291e661b.png!small)2\.
选中目标进程右键->Create Dump->Create Full
Dump![](https://image.3001.net/images/20210311/1615432374_60498ab6da0d9c2490d81.png!small)3\.
选择保存位置即可![](https://image.3001.net/images/20210311/1615432398_60498acec8e8231c3bbac.png!small)

 **#** **Procdump** **#**

◆ 简介

‎ ProcDump 是一种命令行实用程序，其主要目的是监控 CPU
峰值的应用程序，并在峰值期间生成崩溃转储，管理员或开发人员可以用它来确定峰值的原因。ProcDump 还包括挂窗监控（使用 Windows
和任务管理器使用的窗口挂起的相同定义）、未处理的异常监控，并可以根据系统性能计数器的值生成转储。它也可以作为一个一般过程转储实用程序，你可以嵌入到其他脚本。‎使用需提前知道目标进程的PID号（该工具存在Linux版本，Linux系统下使用方式见后文。）

◆ 下载地址

https://docs.microsoft.com/zh-cn/sysinternals/downloads/procdump

◆ 环境限制

系统环境限制：Windows/Linux

◆ 转储进程方式

Windows系统下查询进程PID

PID可在命令行中输入tasklist查询所有进程，也可在任务管理器中查看

[https://docs.microsoft.com/zh-cn/windows-hardware/drivers/debugger/finding-the-process-id（查询PID方式）](https://docs.microsoft.com/zh-cn/windows-hardware/drivers/debugger/finding-the-process-id%EF%BC%88%E6%9F%A5%E8%AF%A2PID%E6%96%B9%E5%BC%8F%EF%BC%89)

![](https://image.3001.net/images/20210311/1615432421_60498ae5d9920b69dae6c.png!small)

 **形式1：图形化**

**命令行执行procdump.exe应用程序，第一次运行需要同意用户协议**![](https://image.3001.net/images/20210311/1615432439_60498af7ec2d30e5cce4d.png!small)

 **使用该工具需要同意用户协议后才可以正常使用**

 **目标转储进程名为：shell.exe,PID号为：2380的进程内存,内存转储文件默认存储位置与procdump.exe处于同一目录**

 **所用到的参数：-ma dump指定进程的所有内存信息**

 **.\procdump.exe -ma
2380**![](https://image.3001.net/images/20210311/1615432461_60498b0d5f6b4eb2b1969.png!small)

 **形式2：命令行**

 **本次实验环境为msf回弹shell，命令行下同意用户协议需要加参数-accepteula（同样第一次使用同意）**

**下图为同意用户终端协议**![](https://image.3001.net/images/20210311/1615432482_60498b2242caa17098686.png!small)

 **同意用户协议后可正常使用，使用方式同图形化使用方式：procdump.exe -ma 2380**

###  **内存镜像**

 **#** **DumpIt** **#**

◆ 简介

利用Dumplt可以将一个系统的完整内存镜像dump下来，dumplt制作的内存镜像(raw文件)与系统内存接近。

◆ 下载地址

https://www.downloadcrew.com/article/23854-dumpit

◆ 环境限制

仅可在Windows系统下运行

◆ 使用Dumplt制作系统内存镜像

双击Dumplt.exe运行，输入y并回车。开始制作系统内存镜像。![](https://image.3001.net/images/20210311/1615432506_60498b3ae5e77d365e91d.png!small)

回显Success为制作成功，默认存储路径与Dumplt.exe文件处于同一路径。获取到整个系统内存文件后，可导入Volatility进行内存取证分析。

##  **2.** **Linux系统下如何转储内存**

###  **进程内存转储**

 **#** **ProcDump-for-Linux** **#**

◆ 简介

ProcDump linux版功能与windows版基本相同，使用方式有所变化

◆ 下载地址

https://github.com/Sysinternals/ProcDump-for-Linux

◆ 环境限制

仅Linux系统下使用，开发者给出了rpm包和deb包

开发者给出的可运行环境：

· Red Hat Enterprise Linux / CentOS 7

· Fedora 29

· Ubuntu 16.04 LTS

所支持的Linux发行版下安装方式

https://github.com/Sysinternals/ProcDump-for-Linux/blob/master/INSTALL.md

◆ ProcDump-for-Linux使用方式

1\. rpm -Uvh

rpm -Uvh

https://packages.microsoft.com/config/centos/7/packages-microsoft-prod.rpm

2\. yum install
procdump![](https://image.3001.net/images/20210311/1615432574_60498b7ef187b9a0bb722.png!small)输入procdump检查是否安装成功![](https://image.3001.net/images/20210311/1615432595_60498b9365a2f6fc1f90f.png!small)查看上面procdump给出的参数详情来看，指定PID号需要加参数-p![](https://image.3001.net/images/20210311/1615432614_60498ba65fcb3de787670.png!small)或者使用-w直接指定进程名来进行dump![](https://image.3001.net/images/20210311/1615432634_60498bbacc4e8f034710b.png!small)

###  **内存镜像**

 **#** **Linux Memory Grabbe** **#**

◆ 简介

Linux Memory Grabber一个用于转储Linux内存并创建Volatility（TM）配置文件的脚本。

◆ 下载地址

https://github.com/halpomeranz/lmg/

◆ 环境限制

仅在Linux系统下使用

◆ 安装步骤

该工具可以安装到U盘中，安装方式：

https://github.com/halpomeranz/lmg/blob/master/INSTALL

◆ 前期准备

Lmg: https://github.com/halpomeranz/lmg/ 脚本主程序

avml：https://github.com/microsoft/avml（可直接下载二进制文件） Linux的便携式内存采集工具

LiME: https://github.com/504ensicsLabs/LiME

 **下载来的所有文件必须处于同一文件夹**

◆ 安装过程

新建目录Linux_Memory_Grabber![](https://image.3001.net/images/20210311/1615432659_60498bd30c7231b223841.png!small)

将需要用到的文件复制到新键的目录中

Cp lmg/lmg
Linux_Memory_Grabber/![](https://image.3001.net/images/20210311/1615432677_60498be5b438e9a1af079.png!small)

修改avml二进制文件名

mv avml avml-$(uname -m)

mv avml-convert avml-convert-$(uname
-m)![](https://image.3001.net/images/20210311/1615432708_60498c044bb9f99cf94e9.png!small)

添加执行权限

chmod +x avml-convert-x86_64
avml-x86_64![](https://image.3001.net/images/20210311/1615432729_60498c19a78bd4dbaf658.png!small)

进入到LiME/src目录

Cd LiME/src

Patch < ../../../lmg/lime-Makefile.patch

# Centos7下patch 命令使用yum -y install
patch安装即可![](https://image.3001.net/images/20210311/1615432747_60498c2bc96b341700597.png!small)

到这里即安装完成，可以使用二进制文件lmg来转储Linux系统内存，该项目地址中还可以配置Volatility进行联动。

 **#** **使用lmg转储linux内存镜像** **#**

./lmg
-y![](https://image.3001.net/images/20210311/1615432764_60498c3cd94c9436b5c6e.png!small)转储成功，保存路径在当前目录下capture文件下![](https://image.3001.net/images/20210311/1615432803_60498c63dae8fec414109.png!small)

.lime为后缀的文件为系统内存转储文件，可用与导入Volatility进行内存分析。

部分内容源自互联网公开资料整理

