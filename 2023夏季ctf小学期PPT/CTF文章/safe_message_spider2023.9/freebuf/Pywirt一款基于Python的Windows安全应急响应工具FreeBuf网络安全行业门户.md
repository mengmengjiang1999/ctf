![](https://image.3001.net/images/20221204/1670168778_638cc0ca24f57bd05411e.jpg!small)

## 关于Pywirt

Pywirt是一款基于Python开发的网络安全工具，该工具专门针对Windows操作系统设计，可以帮助广大研究人员使用winrm并通过在Windows操作系统上收集各种信息来加快安全事件应急响应的速度。

该工具已在Windows 10操作系统上进行过完整测试。

## 功能介绍

该工具支持在Windows操作系统上收集下列信息：

> IP配置
>
> 用户信息
>
> 组信息
>
> 任务
>
> 服务
>
> 计划任务
>
> 注册表控制
>
> TCP&UDP活动端口
>
> 文件共享
>
> 文件信息
>
> 防火墙配置
>
> 会话信息
>
> 开放会话
>
> 日志条目

## 工具安装

由于该工具基于Python 3开发，因此广大研究人员首先需要在本地设备上安装并配置好Python 3环境。接下来，使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/t3l3machus/eviltree.git

接下来，运行下列命令完成工具依赖组件的安装：

    
    
    cd pywirt
    
    pip3 install pywinrm

## 工具使用

首先，我们需要在cred_list.txt文件中指定下列信息：

    
    
    IP地址｜用户名｜密码

例如：

    
    
    192.168.5.85|test|12345

 **pywint信息** ：

![](https://image.3001.net/images/20221204/1670168817_638cc0f1305d06ef4363c.jpg!small)

## 许可证协议

本项目的开发与发布遵循[ _GPL_ _-3.0_](https://github.com/anil-yelken/pywirt/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **Pywirt** ：【[ _GitHub传送门_](https://github.com/anil-yelken/pywirt)】

## 参考资料

> [ _https://twitter.com/anilyelken06_](https://twitter.com/anilyelken06)
>
> [ _https://medium.com/@anilyelken_](https://medium.com/@anilyelken)

