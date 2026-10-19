***本文作者：Shad0wpf_，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**

## 起因  

 **昨天，在某安全交流群，看到关于Nmap扫描的讨论，对一个段做主机存活扫描，发现主机全部存活。**

![](https://image.3001.net/images/20190401/1554098956_5ca1ab0c2bf55.png!small)

扫描源主机是安装在虚拟机上的Kali，网络连接为NAT模式，使用-sP参数对192.168.0.0/24网段扫描，探测存活主机，返回结果为256个IP全部在线，而实际情况是该网段只有几个IP存活，使用Ping命令，其它不在线的IP是Ping不通的。

![image.png](https://image.3001.net/images/20190401/1554098970_5ca1ab1a4e21e.png!small)

## 分析

难道是Nmap出错了？带着这个疑问，我查阅了Nmap的官方文档，Nmap使用`-sn`参数指定只做主机存活发现（以前的一些版本中使用`-sP`，新版本中`-sn`和`-sP`都可以使用，为同一参数），不做端口扫描。Nmap默认的主机存活发现使用了以下四种方式：

    
    
    ICMP echo request
    
    TCP SYN to port 443
    
    TCP ACK to port 80
    
    ICMP timestamp request

只要其中一个主机存活的特征存在，Nmap判断为主机存活。

Linux下默认Ping命令使用的ICMP echo请求，现在Ping不通，那第一种请求是没有主机存活特征的，问题可能在后面的三种请求。

抓个包分析吧。

![](https://image.3001.net/images/20190401/1554099090_5ca1ab929835a.png!small)

扫描源IP为10.10.10.128，筛选了其中一个不存在的IP 192.168.0.10。ICMP echo请求ICMP
timestamp请求没有响应，但奇怪的是，到80端口的ACK请求，有一个RST标志的响应，窗口大小是32767。

正常情况下，数据包发送到一个不存在的IP，不会收到任何响应。

TCP连接端口未监听、请求超时、异常关闭等几种情况会发送RST标志的响应。IP存在，但端口关闭，收到ACK标志的包时，会返回一个RST标志的包，内容为Seq=1，Win=0，Len=0。

这里返回了一个RST标志的包，而且窗口大小不为0，Nmap认为该端口开放（参考Nmap的TCP Windows
Scan），也就是这个包导致了Nmap对主机存活的误判断。这个包是哪来的呢？网络结构很简单，除了VMware的NAT外，没有其它网络设备，说明这个包是NAT返回的。

## 解决

现在已经知道了引起Nmap误判断的原因是VMware的NAT，那用什么方法来避免呢？ **方法一：** 只使用ICMP
echo请求探测（-PE）探测主机时，添加-PE参数，nmap只发送一个ICMP echo请求。

    
    
    nmap -sn -PE -n 192.168.0.0/24
    

现在可以扫描出准确的主机存活信息了。

![image.png](https://image.3001.net/images/20190401/1554099178_5ca1abea2549f.png!small)

> `-n`参数禁用域名解析，避免浪费大量实在在域名解析等待上。

过滤其中一个存活的IP192.168.0.102，Nmap发送一次IMCP echo请求，收到102的ICMP响应后，判断主机存活，不在发送其它数据包。

![image.png](https://image.3001.net/images/20190401/1554099194_5ca1abfa13f7a.png!small)

不存活的IP192.168.0.106，发现两次ICMP echo请求，仍未收到106的ICMP响应，则判断为主机不存活。

![image.png](https://image.3001.net/images/20190401/1554099202_5ca1ac0210507.png!small)

不过这种方式存在一个问题，Nmap最多发送两次ICMP echo请求，主机禁Ping或者丢包时造成漏报。

 **方法二：** VMware虚拟机网络连接方式改为桥接

既然问题是VMware的NAT引起的，那就索性不用NAT了，改成桥接，这也是VMware官方的建议。

![image.png](https://image.3001.net/images/20190401/1554099219_5ca1ac13af958.png!small)  

其实，VMware网络连接使用桥接模式，好处不只是解决了Nmap对主机存活的误判断，也避免了无法traceroute和操作系统判断不准确的问题，可以直接创建反弹shell监听端口，网络性能上也优于NAT。

影响操作系统判断的原因，这里提一下，经过VMware NAT返回的数据包，TTL永远是128，即使对方操作系统是Linux。

![image.png](https://image.3001.net/images/20190401/1554099226_5ca1ac1a8e4f0.png!small)

下图是两种网络连接模式，使用`-O`参数探测操作系统是的结果对比。

![image.png](https://image.3001.net/images/20190401/1554099233_5ca1ac21f248d.png!small)

所以，作为渗透测试的虚拟机，还是直接用桥接网卡吧。

## 参考

> Nmap 主机发现扫描：<https://nmap.org/book/man-host-discovery.html>
>
> Nmap TCP Window Scan (-sW)：<https://nmap.org/book/scan-methods-window-> scan.html>
>
> 不同操作系统的默认TTL：<https://subinsb.com/default-device-ttl-values/>

## 后记

至于VMware NAT为什么会存在这些问题，由于个人的时间精力有限、对TCP/IP/NAT等各种协议的理解有限，未做深入研究。

感谢@伍默提供的测试截图及数据抓包。

 ***本文作者：Shad0wpf_，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**

