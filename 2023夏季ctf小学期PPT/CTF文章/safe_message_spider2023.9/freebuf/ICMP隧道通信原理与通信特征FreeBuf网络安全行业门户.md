原创：Neiko合天智汇

#  **一、ICMP 隧道技术解析**

 **ICMP协议**

ICMP（Internet Control Message
Protocol）Internet控制报文协议。它是TCP/IP协议簇的一个子协议，用于在IP主机、路由器之间传递控制消息。控制消息是指网络通不通、主机是否可达、路由是否可用等网络本身的消息。这些控制消息虽然并不传输用户数据，但是对于用户数据的传递起着重要的作用。

主要概念有：

1.确认ip数据包是否成功到达目的地

2.通知源主机发送ip数据包丢失的原因

3.ICMP是基于IP协议工作的

4.ICMP只能作用于IPV4，IPV6下，使用ICMPv6

 **ICMP帧格式如下所示**

![ba1e22fcec98417587b991e7e4b81562](https://p1-tt.byteimg.com/large/pgc-image/ba1e22fcec98417587b991e7e4b81562)

其中，类型和代码字段决定了ICMP报文的类型，如下图所示

![be75e9371e6b423f90b1672542ae00f0](https://p6-tt.byteimg.com/large/pgc-image/be75e9371e6b423f90b1672542ae00f0)

 **ICMP隧道技术原理**

由于ICMP报文自身可以携带数据，而且ICMP报文是由系统内核处理的，不占用任何端口，因此具有很高的隐蔽性。

通常ICMP隧道技术采用ICMP的ICMP_ECHO和ICMP_ECHOREPLY两种报文，把数据隐藏在ICMP数据包包头的选项域中，利用ping命令建立隐蔽通道。

![b37d1b5cac5d4e3082319d38e0951395](https://p9-tt.byteimg.com/large/pgc-image/b37d1b5cac5d4e3082319d38e0951395)

进行隐蔽传输的时候，肉鸡(防火墙内部)运行并接受外部攻击端的ICMP_ECHO数据包，攻击端把需要执行的命令隐藏在ICMP_ECHO数据包中，肉鸡接收到该数据包，解出其中隐藏的命令，并在防火墙内部主机上执行，再把执行结果隐藏在ICMP_ECHOREPLY数据包中，发送给外部攻击端。

![668895d8740b47be8fec69e2c713fc8f](https://p6-tt.byteimg.com/large/pgc-image/668895d8740b47be8fec69e2c713fc8f)

简单的说就是，利用ICMP的请求和应答数据包，伪造Ping命令的数据包形式，实现绕过防火墙和入侵检测系统的阻拦。

 **ICMP隧道优缺点**

优点：

1.防火墙对ICMP_ECHO数据包是放行的，并且内部主机不会检查ICMP数据包所携带的数据内容，隐蔽性高。

缺点：

1.ICMP隐蔽传输是无连接的，传输不是很稳定，而且隐蔽通道的带宽很低

2.利用隧道传输时，需要接触更低层次的协议 ，这就需要高级用户权限

#  **二、ICMP隧道攻击实现以及流行工具展示**

 **icmpsh**

这一工具简单并且便携。受控端（客户端）使用C语言实现。只能运行在目标Windows机器上，而主控端（服务端）由于已经有C和Perl实现的版本，而且之后又移植到了Python上，因此可以运行在任何平台的攻击者机器中。

 **icmpsh建立隧道及数据包分析**

![3b8e0dd05ff048f79e07be0624505ebd](https://p9-tt.byteimg.com/large/pgc-image/3b8e0dd05ff048f79e07be0624505ebd)

可以看到已经实现成功。

抓包，可以看到我们输入的命令

![4730b16b060d40e9b938b74a61afdfff](https://p9-tt.byteimg.com/large/pgc-image/4730b16b060d40e9b938b74a61afdfff)

 **icmptunnel**

icmptunnel是通过创建虚拟网卡，将所有流量都经过这个虚拟网卡。即ICMP隧道

  1. icmptunnel建立隧道及数据包分析

客户端主机上的所有用户流量都路由到虚拟网卡tun0。icmptunnel在此接口上侦听IP数据包。这些数据包封装在ICMP回显数据包中。

![7d907db60f5144af905a380efa578d91](https://p6-tt.byteimg.com/large/pgc-image/7d907db60f5144af905a380efa578d91)

建立ICMP隧道

![7462e402ad0843a6be65776a70e68f9f](https://p9-tt.byteimg.com/large/pgc-image/7462e402ad0843a6be65776a70e68f9f)

此时所有流量都通过虚拟网卡，即icmp隧道

![ee80286686a24b5bad31340e00bc66f9](https://p6-tt.byteimg.com/large/pgc-image/ee80286686a24b5bad31340e00bc66f9)

![b71899ffba8748a3b54f5c70080ae8f4](https://p1-tt.byteimg.com/large/pgc-image/b71899ffba8748a3b54f5c70080ae8f4)

 **ptunnel**

ptunnel支持大多数具有libpcap的操作系统，从版本0.7开始，ptunnel也可以在Windows上编译。

前提是需要装WinPcap

  1. petunnel 建立隧道及数据包分析

![9cf7d9718e85408496a068abb265b436](https://p6-tt.byteimg.com/large/pgc-image/9cf7d9718e85408496a068abb265b436)

![7357538514e44c55af06d6bed676c850](https://p6-tt.byteimg.com/large/pgc-image/7357538514e44c55af06d6bed676c850)

使用命令建立ICMP隧道

![7f61566a59f3476885b7ff26f08f463c](https://p1-tt.byteimg.com/large/pgc-image/7f61566a59f3476885b7ff26f08f463c)

# 三、检测icmp隧道通信特征

 **icmp会话中数据包的总数**

一个正常的 ping 每秒最多只会发送两个数据包，而使用 ICMP隧道的浏览器在同一时间会产生大量 ICMP 数据包。

![1f075339dae84ddd823392bbfe5903fa](https://p1-tt.byteimg.com/large/pgc-image/1f075339dae84ddd823392bbfe5903fa)

 **隧道数据通常比较大**

ICMP隧道 数据包中DATA 往往大于 64 比特

![398aa9c9e6334343aa1ae3233b717530](https://p9-tt.byteimg.com/large/pgc-image/398aa9c9e6334343aa1ae3233b717530)

 **请求包和响应包内容不一致**

![68f609a63c5a4d6ebbdeb492c1f62ad6](https://p1-tt.byteimg.com/large/pgc-image/68f609a63c5a4d6ebbdeb492c1f62ad6)

![7a9adf44c73e47e9a7301cd6dd28308a](https://p1-tt.byteimg.com/large/pgc-image/7a9adf44c73e47e9a7301cd6dd28308a)

而正常的icmp数据包里，请求和回应部分数据是一致的

![df708fe16e164d0285dde5a87ef21752](https://p1-tt.byteimg.com/large/pgc-image/df708fe16e164d0285dde5a87ef21752)

![694139f181764da99ce36ae7e95de462](https://p6-tt.byteimg.com/large/pgc-image/694139f181764da99ce36ae7e95de462)

部分隧道工具会显示tun的标志

![c1acfeeda0454825a7ebadda04460d84](https://p1-tt.byteimg.com/large/pgc-image/c1acfeeda0454825a7ebadda04460d84)

 **看完文章，可以上合天网安实验室学习哦！**

Wireshark数据抓包分析之互联网控制报文协议：

http://www.hetianlab.com/expc.do?ec=ECID172.19.104.182015072017274900001

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关！

  

