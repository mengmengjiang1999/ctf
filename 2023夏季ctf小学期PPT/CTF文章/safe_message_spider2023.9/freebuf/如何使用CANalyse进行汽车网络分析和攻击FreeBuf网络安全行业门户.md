测试![](https://image.3001.net/images/20210508/1620445181_609607fdc5cb39d57696a.png!small)

## 关于CANalyse

CANalyse是一款针对汽车车辆安全的网络分析和攻击工具。CANalyse可以用来分析日志文件，它可以自动寻找唯一的数据集，并能够连接到简单的用户接口，比如说Telegram等等。基本上来说，在使用此工具时，攻击者可以提供一个bot-ID，并通过telegram-bot在互联网上使用该工具。CANalyse支持在树莓派种使用，能够通过telegram-bot记录并分析汽车的网络流量以及数据日志，并通过这些数据来攻击和利用汽车漏洞，就好比向一台汽车植入了硬件后门一样。

使用此工具的先决条件是，硬件植入物已安装在车内，并且能够与车辆内部的网络/通信信道进行通信。

## 工具运行机制

![](https://image.3001.net/images/20210508/1620445211_6096081b6541bda3e721c.png!small)

## 依赖组件

Python 3

pip3

txt文件中列出的所有代码库

## 工具安装

    
    
    git clone https://github.com/KartheekLade/CANalyse.git
    
    cd CANalyse
    
    pip3 install -r requirements.txt

## 工具使用

    
    
    cd CANalyse/
    
    python3 canalyse_tool.py

## 问题解决

如果工具输入“No such device”错误信息的话，或者你无法查看到捕捉到的流量，请检查设置中的“interface & communication
channel”选项。

如果所需库的自动安装不起作用，请尝试使用sudo运行一次或手动安装它们。

如果不能正确执行命令，请检查“menu”。

## 工具介绍视频

视频地址：【[ _点我观看_](https://youtu.be/s5WGn3rwzKk)】

## 项目地址

CANalyse：【[ _GitHub传送门_](https://github.com/KartheekLade/CANalyse)】

## 参考资料

> [ _https://www.python.org/_](https://www.python.org/)
>
> [ _https://kartheeklade.medium.com/what-is-canalyse-and-how-do-i-control-> hack-cars-through-telegram-> part-1-de358640becf_](https://kartheeklade.medium.com/what-is-canalyse-and-> how-do-i-control-hack-cars-through-telegram-part-1-de358640becf)
>
> [ _https://youtu.be/s5WGn3rwzKk﻿_](https://youtu.be/s5WGn3rwzKk)

