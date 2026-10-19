![](https://image.3001.net/images/20210823/1629728777_6123b0092f3489fc0228b.png!small)

## 关于Kali-Whoami

Whoami工具的目的是让您在Kali-linux上尽可能地保持匿名活动，该工具提供了一个用户友好且易于使用的简单界面，并遵循两种不同的路径以确保最高级别的匿名性。

但是别忘了，互联网上从来没有百分之百的安全！

## 功能介绍

反中间人攻击；

日志清理；

IP修改；

DNS修改；

MAC地址修改；

反冷启动；

时区修改；

主机名称修改；

浏览器匿名化；

## 准备工作

如果你没有定期更新你的系统，或者还没有安装相关的依赖组件的话，你就无法正常使用该工具了。因此，我们需要先安装并配置好Whoami所需的依赖组件，我们可以直接运行下列命令完成准备工作：

    
    
    sudo apt update && sudo apt install tar tor curl python3 python3-scapy network-manager

## 工具安装

首先，我们需要使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/omer-dogan/kali-whoami

接下来，安装makefile

    
    
    sudo make install

完成上述操作之后，我们就可以开始使用Whoami了。

## 工具使用

完成工具的安装之后，我们需要在系统的搜索栏中搜索“Kali Whoami”，或直接在命令行终端中运行下列命令：

    
    
    sudo kali-whoami --help

此时，你将会看到如下所示的提示界面：

    
    
    [+] Usage : sudo kali-whoami [option]
    
     
    
    --start  :   It will make backups and start the program.
    
    --stop   :   Closes the program using a backup.
    
    --status :   Provides information about working status.
    
    --fix    :   Used to repair the system in case of a possible bug.
    
    --help   :   This shows the menu.

## 工具演示

![](https://image.3001.net/images/20210823/1629728820_6123b034d14c9e760bc9e.gif!small)

## 许可证协议

本项目的开发与发布遵循GPL V3开源许可证协议。

## 项目地址

 **Kali-Whoami：** 【[ _GitHub传送门_](https://github.com/omer-dogan/kali-whoami)】

