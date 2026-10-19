## Ethr

Ethr是一个用golang编写的跨平台网络性能测量工具。该项目的目标是提供本机工具，用于跨多种协议（如TCP，UDP，HTTP，HTTPS和跨多个平台）对带宽，连接，数据包，延迟，丢失进行全面的网络性能测量。  
![49815752-506f0000-fd21-11e8-954e-d587e79c5d85.png](https://image.3001.net/images/20190118/1547800769_5c4190c195d17.png!small)  
Ethr从现有的开源网络性能工具中获取灵感，并以这些想法为基础。对于带宽测量，它类似于iPerf3，用于TCP和UDP流量。
iPerf3有更多选项可用于执行限制测试，更丰富的功能集，而Ethr支持多线程，允许它扩展到1024甚至更高数量的连接，多个客户端与单个服务器通信等。用于延迟测量，它类似于Windows上的latte或Linux上的sockperf。与其他工具相比，Ethr提供了更多的测试测量，例如它在单个工具中提供带宽，连接，数据包，延迟和TCP连接设置延迟的测量。在未来，计划增加更多功能（希望其他人贡献）以及更多协议支持，使其成为网络性能测量的综合工具。与通过像cygwin这样可能限制功能的抽象层进行编译相比，由于golang，Ethr本身就是跨平台的。它希望通过结合iPerf3，ntttcp，psping，sockperf和latte等工具的功能统一性能测量，并提供跨多个平台和多种协议的单一工具。

## 下载

    
    
    For Windows 10: https://github.com/Microsoft/Ethr/files/2640289/ethr.zip
    For Ubuntu: https://github.com/Microsoft/Ethr/files/2640288/ethr.gz
    For ArchLinux: https://aur.archlinux.org/packages/ethr
    

## 安装

注意：需要从源代码构建版本1.10或更高版本。

### 从源码安装

    
    
    git clone https://github.com/Microsoft/ethr.git
    cd ethr
    dep ensure -v
    go build
    

### Docker

    
    
    docker build -t microsoft/ethr .
    

### Linux

`docker run -e GOOS=linux -v $(pwd):/out microsoft/ethr make build-docker`

### Windows

`docker run -e BINARY_NAME=ethr.exe -e GOOS=windows -v $(pwd):/out
microsoft/ethr make build-docker`

### OSX

`docker run -e BINARY_NAME=ethr -e GOOS=darwin -v $(pwd):/out microsoft/ethr
make build-docker`

### go get用法

`go get github.com/Microsoft/ethr`

## ArchLinux安装

如果你使用 [`yay`](a%20href=) (<https://github.com/Jguer/yay>):`yay -S ethr`

## 用法

### 简单用法

帮助:`ethr -h`服务器:

    
    
    ethr -s
    

带文本UI的服务器：

    
    
    ethr -s -ui
    

客户端:

    
    
    ethr -c <server ip>
    

例：

    
    
    // 开始服务
    ethr -s
    // 使用1个线程启动客户端以进行默认（带宽）测试测量
    ethr -c localhost
    // 使用64个线程启动连接/测试
    ethr -c localhost -t c -n 64
    

### 完整的命令行

常用参数:

    
    
    -h                        帮助
    -no                       禁用日志记录到文件
    -o <filename>             记录到filename指定的文件
                              缺省值：服务器的ethrs.log，客户端的ethrc.log，外部客户端模式的ethrxc.log
    -debug                    记录调试输出
    -ports <string>           使用自定义端口号而不是默认端口号
                              格式：“Key1 = Value，Key2 = value，......”
                              默认值：“control = 8888，tcp = 9999，udp = 9999，http = 9899，https = 9799”
                              控制用于ethr的控制信道通信。
                              对于协议，基本端口由值指定，并计算其他端口。
                              示例：tcp = 9999表示带宽端口：9999，CPS：9998，PPS：9997，延迟：9996
                              注意：必须在客户端和服务器上使用相同的端口
                              注意：此选项对外部客户端模式无效
    -4                        仅使用IP v4版本
    -6                        仅使用IP v6版本
    

服务器参数

    
    
    -s                      服务器模式
    -ui                     显示文本UI
    

客户端参数

    
    
    -c <server>客户端模式，连接到服务器指定的名称或IP
    -t <b | c | p | l>测试完成，b：带宽，c: connections/s, p: packets/s，l：延迟
                                   默认是带宽测试
    -p <tcp | udp | http | https | icmp>要使用的协议，默认为TCP
    -n <number>要使用的会话/线程数
    -l <number>用于每个请求的缓冲区大小
    -i <number>延迟测试的迭代次数
    -d <duration>测试运行的持续时间，例如，10s，4m，5h等.0  - 永远，默认值：10s
    

外部服务器参数

    
    
    -m x                       外部服务器模式 - 在此模式下，Ethr仅支持TCP，侦听9999
                               任何客户端都可以在此模式下连接到Ethr。 Ethr还可以在此模式下接收数据
                               此模式对于在负载均衡器后面的多个实例上运行Ethr服务器非常有用，
                               来自客户端的流量由负载均衡器分配给这些实例
    -s                         服务器模式
    -ui                        显示文本UI
    

外部客户端模式

    
    
    -m x将模式设置为外部客户端模式
    -c <目标>外部客户端模式中，连接到由主机指定的目的：端口
                                   示例：-x www.microsoft.com:443或-x 10.1.0.4:22等
    -t <b | cl>测试完成，b：带宽，cl：连接延迟
    -d <duration>测试运行的持续时间，例如，10s，4m，5h等.0  - 永远，默认值：10s
    -g <duration>连续建立连接之间的间隙（或间隔）（用于连接延迟测试）
    

## 状态

Protocol  | Bandwidth | Connections/s | Packets/s | Latency  
---|---|---|---|---  
TCP  | Yes | Yes | No | Yes  
UDP  | Yes | NA | Yes | No  
HTTP | Yes | No | No | No  
HTTPS | Yes | No | No | No  
ICMP | No | NA | No | No  
  
## 平台支持

 **Windows** 经测试：Windows 10，Windows 7 SP1

未经测试：其他Windows版本

 **Linux** 测试：

Ubuntu Linux 18.04.1 LTS，OpenSuse Leap 15

未经测试：其他Linux版本 **  
**

 **OSX** 测试：

OSX由贡献者测试 **  
**

 **其他** 目前尚未测试其他平台

**参考来源：[github](https://github.com/Microsoft/ethr/blob/master/README.md)，本文由周大涛编译，转载请注明来自FreeBuf.COM**

