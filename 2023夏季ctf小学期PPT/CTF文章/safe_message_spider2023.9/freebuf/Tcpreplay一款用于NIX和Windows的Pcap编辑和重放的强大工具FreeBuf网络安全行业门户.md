**今天给大家介绍的是一款名叫Tcpreplay的工具，广大研究人员可以利用该工具来在*NIX和Windows平台下实现Pcap的编辑和重放。**

![a.png](https://image.3001.net/images/20181228/1545986626_5c25e2429e163.png!small)

## Tcpreplay

Tcpreplay是一款遵循[GPLv3](http://www.gnu.org/licenses/gpl-3.0.html)许可证协议的实用工具套件，该工具支持UNIX以及Windows操作系统，可对tcpdump和Ethereal/Wireshark等工具捕捉到的网络流量进行编辑和重放。它可以对客户端和服务器端流量进行分类，重写Layer
2、3、4层数据包，并将流量重新发送至目标网络，适用设备包括交换机、路由器、防火墙、NIDS和入侵防御系统。除此之外，Tcpreplay还支持多种开源项目。

### 工具下载

GitHub：【[下载地址](https://github.com/appneta/tcpreplay/releases)】

SourceForge：【[下载地址](https://sourceforge.net/projects/tcpreplay)】

## 依赖组件

### 网络重放

    
    
    -tcpreplay：以任意速度向目标网络重放pcap文件，支持随机IP地址。
    
    -tcpreplay-edit：以任意速度向目标网络重放pcap文件，支持数据包实时修改。
    
    -tcpliveplay：重放存储在pcap文件中的TCP网络流量，远程服务器可响应。

### Pcap文件编辑和使用

    
    
    -tcpprep：pcap文件预处理工具，可判断和处理数据包来源为客户端或是服务器。
    
    -tcprewrite：pcap文件编辑器，可重写TCP/IP和Layer 2数据包头。
    
    -tcpbridge：桥接两个网段。
    
    -tcpcapinfo：元pcap文件解码/调试器

## 工具安装

访问项目页面，获取更详细的下载和安装指南。【[传送门](http://tcpreplay.appneta.com/)】

Unix用户快速安装：

    
    
    ./configure
    
    make
    
    sudo make install

## 构建netmap功能

该功能可以检测Linux和BSD系统上的netmap网络驱动，如果检测到之后，工具会在tcpreplay和tcpreplay-edit的运行过程中绕过网络驱动器，并直接在网络缓冲区中写入数据。

下载并安装最新版的netmap：【[下载地址](http://info.iet.unipi.it/~luigi/netmap/)】。如果你把netmap提取到/usr/src/或/usr/local/src目录下，你可以正常编译，否则你需要指定netmap源目录：

    
    
    ./configure--with-netmap=/home/fklassen/git/netmap
    
    make
    
    sudo make install

netmap源码获取：【[传送门](http://code.google.com/p/netmap/)】

### 安装Tcpreplay源码

下载[tar
ball](https://github.com/appneta/tcpreplay/tarball/master)或[zip](https://github.com/appneta/tcpreplay/zipball/master)文件，或使用下列命令克隆git库：

    
    
    git clone git@github.com:appneta/tcpreplay.git

## 参考资料

项目Wiki：【[传送门](http://tcpreplay.appneta.com/)】

开发者Wiki：【[传送门](https://github.com/appneta/tcpreplay/wiki)】

***参考来源：[tcpreplay](https://github.com/appneta/tcpreplay)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

