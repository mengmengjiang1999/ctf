**今天给大家介绍的是一款功能强大的UDP隧道工具，该工具可以利用原始套接字并通过伪造的TCP/UDP/ICMP流量来帮助研究人员绕过UDP防火墙（或不稳定的UDP环境）。**

![a.png](https://image.3001.net/images/20181019/1539916348_5bc9423cd766d.png!small)

## 支持的平台

Linux主机，需拥有root访问权，其中包括桌面端Linux、Android手机/平板、OpenWRT路由器或树莓派。

对于Windows/macOS平台，我们发布了一个预安装了udp2raw的虚拟镜像，大家可以直接使用VMware/VirtualBox来加载安装。虚拟镜像会自动获取IP，其中的dup2raw可以在启动完成之后立即运行（请确定虚拟机网络模式设置为桥接）。

## 功能介绍

### 发送/接收UDP数据包（伪造的TCP/ICMP头）

伪造的TCP/ICMP头可以帮助我们绕过UDP屏蔽、UDP QOS或其他不正确的UDP NAT行为。除此之外，该工具还支持包含了UDP头的元数据包、在UDP
Header模式下，它跟普通的UDP隧道一样，你可以直接使用其他功能。

### 模拟TCP握手

模拟三次握手过程，包括seq和ack_seq。MSS、sackOk、TS、TS_ack、wscale等TCP选项都可以模拟。工具可以保证数据包实时传递，在使用OpenVPN时不存在TCP连接问题。

### 加密、反重放和MITM

-使用AES-128-CBC加密通信流量。

-通过MD5或CRC32保护数据完整性。

-利用反重放窗口机制防御重放攻击，与IPSec和OpenVPN类似。

-手动认证，无中间人攻击

## 工具使用

### 安装

大家可以从【[这里](https://github.com/wangyu-/udp2raw-tunnel/releases)】下载源码。

### 工具运行

假设你的UDP已被屏蔽，假设你的服务器IP为44.55.66.77，你有一个服务在监听udp端口7777。

    
    
    # Runat server side:
    ./udp2raw_amd64-s -l0.0.0.0:4096 -r 127.0.0.1:7777  -a-k "passwd" --raw-mode faketcp 
    # Runat client side
    ./udp2raw_amd64-c -l0.0.0.0:3333  -r44.55.66.77:4096 -a-k "passwd" --raw-mode faketcp  
    

### 服务器端输出

![b.png](https://image.3001.net/images/20181019/1539916387_5bc94263b1ea9.png!small)

### 客户端输出

![c.png](https://image.3001.net/images/20181019/1539916396_5bc9426c65665.png!small)

此时，已成功通过TCP端口4096在客户端和服务器端之间建立了一条经过加密的通信隧道。在客户端通过UDP端口3333连接，等同于在服务器端连接端口7777。

如果你需要在Android端运行的话，请参考【[这篇教程](https://github.com/wangyu-/udp2raw-tunnel/blob/master/doc/android_guide.md)】

## 帮助菜单

    
    
    udp2raw-tunnel
    version:Aug 18 2017 00:29:11
    repository:https://github.com/wangyu-/udp2raw-tunnel
     
    usage:
        run as client : ./this_program -c -llocal_listen_ip:local_port -r server_ip:server_port  [options]
        run as server : ./this_program -s -lserver_listen_ip:server_port -r remote_ip:remote_port  [options]
     
    commonoptions, these options must be same on both side:
        --raw-mode            <string>        avaliable values:faketcp(default), udp,icmp
        -k, --key              <string>        password to gen symetric key,default:"secret key"
        --cipher-mode         <string>        avaliable values:aes128cbc(default),xor, none
        --auth-mode           <string>        avaliable values:md5(default), crc32,simple, none
        -a, --auto-rule                        auto add (and delete)iptables rule
        -g, --gen-rule                         generate iptables rulethen exit
        --disable-anti-replay                 disable anti-replay, notsuggested
    clientoptions:
        --source-ip           <ip>            force source-ip for raw socket
        --source-port         <port>          force source-port for raw socket,tcp/udp only
                                              thisoption disables port changing while re-connecting
    otheroptions:
        --log-level           <number>        0:never    1:fatal  2:error   3:warn
                                             4:info (default)     5:debug   6:trace
        --log-position                        enable file name,function name, line number in log
        --disable-color                       disable log color
        --disable-bpf                         disable the kernelspace filter, most time its not necessary
                                             unless you suspect there is a bug
        --sock-buf            <number>        buf size for socket, >=10 and <=10240,unit:kbyte, default:1024
        --seqmode             <number>        seq increase mode for faketcp:
                                             0:dont increase
                                             1:increase every packet
                                              2:increase randomly,  about every 3 packets (default)
        --lower-level         <string>        send packet at OSI level 2,  format:'if_name#dest_mac_adress'
                                             ie:'eth0#00:23:45:67:89:b9'.Beta.
    -h, --help                             print this helpmessage  
    

### IPTABLES规则

该程序可通过元套接字发送数据包。在FakeTCP模式下，iptables规则会在通信双方两端屏蔽掉Linux内核的TCP数据包处理进程，你可以使用-a选项在工具启动和退出的时候自动自动添加/删除iptables规则。除此之外，你还可以使用-g选项手动生成并添加一条iptables规则。

### 加密模式和认证模式

我们建议大家使用aes128cbc + md5来最大程度地实现安全性。如果你想要在路由器上使用该工具，你可以尝试xor +
simple，在普通情况下这样足以绕过大部分防火墙的数据报审计功能，不过这种方法无法抵御其他严重攻击。

### Seq模式

FakeTCP模式的工作机制并不是跟真实的TCP连接完全一样，因为互联网服务提供商能够区分模拟TCP流量和真实TCP流量。Seq模式可以帮助我们进一步提升模拟TCP流量的真实程度。

 ***参考来源：[kitploit](https://www.kitploit.com/2018/09/udp2raw-tunnel-udp-tunnel-which-tunnels.html)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

