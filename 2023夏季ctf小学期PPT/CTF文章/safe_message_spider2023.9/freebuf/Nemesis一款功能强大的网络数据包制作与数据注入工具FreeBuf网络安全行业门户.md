![](https://image.3001.net/images/20230705/1688555707_64a550bb2f874ed553060.png!small)

## 关于Nemesis

Nemesis是一款功能强大的网络数据包制作与数据注入工具，该工具旨在为类UNIX和Windows系统提供一个基于命令行的可移植人工IP堆栈。该套件按协议划分，并允许广大研究人员根据自己的需求制作目标网络数据包，或通过简单的Shell脚本向目标数据包中注入其他数据。

## 关键功能

> 1、支持ARP/RARP、DNS、ETHERNET、ICMP、IGMP、IP、OSPF、RIP、TCP和UDP协议；
>
> 2、支持在类UNIX系统上实现Layer 2或Layer 3注入；
>
> 3、支持在Windows系统上实现Layer 2注入；
>
> 4、支持从文件读取和注入数据包Payload；
>
> 5、支持从文件中读取IP和TCP选项；
>
> 6、已在OpenBSD、Linux、Solaris、macOS和Windows 2000平台上进行过测试；

每个支持的协议都使用自己的协议“注入器”，并且每个注入器附带了一个解释其功能的手册页。

## 工具下载

广大研究人员可以直接使用下列命令将该项目源码克隆至本地并自行进行编译：

    
    
    git clone https://github.com/libnet/nemesis.git

除此之外，我们也可以直接访问该项目的【[
_Releases页面_](https://github.com/libnet/nemesis/releases)】下载最新的发布版本。

## 工具构建&安装

Nemesis基于[ _libnet_](https://sourceforge.net/projects/libnet-dev/)构建，Windows平台下的代码构建还需要使用[ _libpcap_](http://www.tcpdump.org/)。

### Debian/Ubuntu

    
    
    curl -sS https://deb.troglobit.com/pubkey.gpg | sudo apt-key add -    
    echo "deb [arch=amd64] https://deb.troglobit.com/debian stable main" | sudo tee /etc/apt/sources.list.d/troglobit.list
    
    sudo apt-get update && sudo apt-get install nemesis

### 源码构建

在Debian或Ubuntu等衍生GNU/Linux系统上执行下列代码：

    
    
    sudo apt install libnet1-dev

然后找到工具配置脚本，并设置下列路径：

    
    
    configure LDFLAGS=-L/path/to/lib CPPFLAGS=-I/path/to/header

然后切换到/usr/local路径中，并运行下列代码：

    
    
    tar xf nemesis-1.7.tar.xz
    
    cd nemesis-1.7/
    
    ./configure --prefix=/usr
    
    make -j5
    
    sudo make install-strip

## 工具使用

注入恶意ICMP重定向：

    
    
    sudo nemesis icmp -S 10.10.10.3 -D 10.10.10.1 -G 10.10.10.3 -i 5

DHCP发现（必须使用sudo和-d来从源IP0.0.0.0发送）：

    
    
    sudo nemesis dhcp -d eth0

IGMP v2加入组239.186.39.5：

    
    
    sudo nemesis igmp -v -p 22 -S 192.168.1.20 -g 239.186.39.5 -D 239.186.39.5

IGMP v2查询，附带路由警报IP选项：

    
    
    echo -ne '\x94\x04\x00\x00' >RA
    
      sudo nemesis igmp -v -p 0x11 -c 100 -D 224.0.0.1 -O RA

或

    
    
    echo -ne '\x94\x04\x00\x00' | sudo nemesis igmp -v -p 0x11 -c 100 -D 224.0.0.1 -O -
IGMP v3查询，附带路由警报IP选项：

    
    
    echo -ne '\x03\x64\x00\x00' > v3
    
      sudo nemesis igmp -p 0x11 -c 100 -i 0.0.0.0 -P v3 -D 224.0.0.1 -O RA

随机TCP数据包：

    
    
    sudo nemesis tcp

DoS和DDoS测试：

    
    
    sudo nemesis tcp -v -S 192.168.1.1 -D 192.168.2.2 -fSA -y 22 -P foo
    
      sudo nemesis udp -v -S 10.11.12.13 -D 10.1.1.2 -x 11111 -y 53 -P bindpkt
    
      sudo nemesis icmp redirect -S 10.10.10.3 -D 10.10.10.1 -G 10.10.10.3 -qR
    
      sudo nemesis arp -v -d eth0 -H 0:1:2:3:4:5 -S 10.11.30.5 -D 10.10.15.1

## 许可证协议

本项目的开发与发布遵循[ _BSD_ _-3-_
_Clause_](https://github.com/libnet/nemesis/blob/master/LICENSE)开源许可证协议。

## 项目地址

 **Nemesis** ：【[ _GitHub传送门_](https://github.com/libnet/nemesis)】

## 参考资料

> [ _https://sourceforge.net/projects/libnet-> dev/_](https://sourceforge.net/projects/libnet-dev/)
>
> [ _http://www.tcpdump.org/_](http://www.tcpdump.org/)
>
> [ _https://airs.com/ian/configure/_](https://airs.com/ian/configure/)

