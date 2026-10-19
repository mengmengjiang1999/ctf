## 简介

ProxyChains是Linux和其他Unix下的代理工具。它可以使任何程序通过代理上网，
允许TCP和DNS通过代理隧道。ProxyChains通过一个用户定义的代理列表强制连接指定的应用程序， 直接断开接收方和发送方的连接。

## 安装

ProxyChains在kali中已经默认安装，如果是其他Linux发行版。你可以通过apt命令直接进行安装。

在kali中安装ProxyChains比较简单，我们可以源码编译安装，也可以利用apt命令直接安装。

    
    
    #编译安装
    git clone https://github.com/rofl0r/proxychains-ng
    cd proxychains-ng
    ./configure
    sudo make && make install
    #apt命令安全
    apt-get install proxychains

## 配置文件

配置文件位于 /etc/proxychains.conf ，打开后你需要在末尾添加你使用的代理。例如：

![1682649739_644b328b226e66cf1d5fd.png!small?1682649741442](https://image.3001.net/images/20230428/1682649739_644b328b226e66cf1d5fd.png!small?1682649741442)

 **至于代理IP，网上有很多，我们可以自行选择。**

## 使用方法

只需在执行命令前面添加参数proxychains即可。如，在利用apt命令

![1682649760_644b32a0cdae5420eeac4.png!small?1682649763012](https://image.3001.net/images/20230428/1682649760_644b32a0cdae5420eeac4.png!small?1682649763012)

## 测试IP

    
    
    proxychains curl ipinfo.io

![1682649790_644b32bede4859b7123d8.png!small?1682649793199](https://image.3001.net/images/20230428/1682649790_644b32bede4859b7123d8.png!small?1682649793199)

![1682649813_644b32d5206575b3eac22.png!small?1682649815653](https://image.3001.net/images/20230428/1682649813_644b32d5206575b3eac22.png!small?1682649815653)

