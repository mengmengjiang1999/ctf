**严正声明：本文仅限于技术探讨，严禁用于其他用途。**

 **今天给大家介绍一种在隔离环境中实现隐蔽后门数据传输的方法，这里需要使用到的是一款名叫GhostTunnel的工具。**

![GhostTunnel：一种在隔离环境中实现隐蔽后门传输的技术](https://image.3001.net/images/20180915/1537009424_5b9ce710d9a84.png!small)

## GhostTunnel

GhostTunnel这款工具实现了一种在隔离环境中实现隐蔽后门数据传输的技术，该工具能够通过HID设备（仅投放代理Payload）来对目标实施攻击。

GhostTunnel使用了802.11 Probe
Request帧和Beacon帧实现通信，并且不会建立WiFi链接。实际上，它主要通过在beacon帧和probe
request帧中嵌入数据来实现通信。该项目所发布的GhostTunnel服务器以及Windows代理均采用
C/C++开发，客户端代理不需要特殊权限，它可以使用系统的WiFi API来发送Probe
Request并接收Beacon。比如说在Windows平台下，它可以使用原生的WiFi
API。因此你可以在其他的平台上实现类似的代理客户端。服务器端运行在Linux上，你可能需要一个或两个支持monitor监控模式的USB无线网卡来注入和发送数据包。

## 工具优势

> 1\. 隐蔽性；
>
> 2\. 现有的连接状态和通信情况不会干扰目标用户；
>
> 3\. 能够绕过防火墙；
>
> 4\. 可以对严格隔离的网络系统实施攻击；
>
> 5\. 通信信道不受目标现有网络链接的影响；
>
> 6\. 支持最多256个客户端；
>
> 7\. 有效距离最远为50米；
>
> 8\. 跨平台支持；
>
> 9\. 可用来对任何支持无线通信的设备进行攻击，我们已在Windows 7-Windows 10和MacOS平台上进行了测试。

## 工具使用

1\. 服务器端只需要一个或两个支持数据包注入和网络监控模式的无线网卡即可，例如TP-LINK TL-WN722N和Alfa
AWUS036ACH等等。使用命令如下：

    
    
    ./ghosttunnel[interface]
     ./ghosttunnel [interface1] [interface2]
     
     COMMANDS:
          sessions= list all clients
          use= select a client to operate, use [clientID]
          exit= exit current operation
          wget= download a file from a client, wget [filepath]
          quit= quit ghost tunnel
          help= show this usage help

2\. 客户端需要向目标系统发送并执行Payload（目前项目只提供了Windows客户端）。

## 功能实现

> 1\. Shell命令负责创建一个远程Shell；
>
> 2\. 下载文件的最大大小限制为10M，并且一次只能下载一个文件；
>
> 3\. 你可以根据自己的需要修改项目代码，并添加额外功能；

## 项目构建

服务器端要求：

    
    
    apt-get install pkg-config libnl-3-dev libnl-genl-3-dev

代码编译：

    
    
    server:
           cd src
           make
    windowsclient:
           Microsoft Visual Studio 2015

## 参考项目

1\. Aircrack-ng：【[传送门](https://github.com/aircrack-ng/aircrack-ng)】

2\. MDK4：【[传送门](https://github.com/aircrack-ng/mdk4)】

3\. hostapd：【[传送门](http://w1.fi/hostapd)】

4\. Kismet：【[传送门](https://github.com/kismetwireless/kismet)】

***参考来源：[GhostTunnel](https://github.com/360PegasusTeam/GhostTunnel)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

