![](https://image.3001.net/images/20221216/1671166789_639bfb45d7357fb8b1d6f.jpg!small)

## 关于Pylirt

Pylirt是一款针对Linux系统的网络安全事件应急响应工具套件，在该工具的帮助下，广大研究人员可以轻松收集目标Linux系统相关的各种信息，并以此来加速事件应急响应人物的进程。

## 功能介绍

当前版本的Pylirt支持收集下列信息：

    
    
    /etc/passwd
    
    cat /etc/group
    
    cat /etc/sudoers
    
    lastlog
    
    cat /var/log/auth.log
    
    uptime/proc/meminfo
    
    ps aux
    
    /etc/resolv.conf
    
    /etc/hosts
    
    iptables -L -v -n
    
    find / -type f -size +512k -exec ls -lh {}/;
    
    find / -mtime -1 -ls
    
    ip a
    
    netstat -nap
    
    arp -a
    
    echo $PATH

## 工具安装

由于该工具基于Python 3开发，因此广大研究人员首先需要在本地设备上安装并配置好Python 3环境。接下来，使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/anil-yelken/pylirt

获取到项目源码之后，使用下列命令切换到项目目录中，然后通过pip3命令安装项目所需的其他依赖组件：

    
    
    cd pylirt
    
    sudo pip3 install paramiko

## 工具使用&配置

在使用该工具之前，我们需要在cred_list.txt文件中按照下列格式指定目标Linux操作系统的IP地址、用户名和密码。

格式如下：

    
    
    IP|Username|Password

![](https://image.3001.net/images/20221216/1671166822_639bfb6600abad9718bb2.jpg!small)

配置完成之后，我们就可以运行下列命令来使用Pylirt了：

    
    
    sudo python3 plirt.py

注意，该工具的运行需要使用管理员权限（sudo）来最大化工具功能。

## 工具使用演示

![](https://image.3001.net/images/20221216/1671166834_639bfb720b96f70a048ba.jpg!small)

## 许可证协议

本项目的开发与发布遵循[ _GPL_ _-3.0_](https://github.com/anil-yelken/pylirt/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **Pylirt** ：【[ _GitHub传送门_](https://github.com/anil-yelken/pylirt)】

## 参考资料

> [ _https://twitter.com/anilyelken06_](https://twitter.com/anilyelken06)
>
> [ _https://medium.com/@anilyelken_](https://medium.com/@anilyelken)

