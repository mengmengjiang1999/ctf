**Justniffer是一款功能强大的网络协议分析工具，它可以捕捉网络流量并以定制化的方式生成日志文件。除此之外，它还可以模拟Apache
Web服务器日志文件，跟踪响应事件并从HTTP流量中提取出所有截获到的文件。**

![aaa.jpg](https://image.3001.net/images/20190215/1550218216_5c6673e8dc163.jpg!small)

Justniffer允许我们从当前活动网络或之前捕捉到的pcap文件中交互式地追踪TCP流量。Justniffer捕捉到的原始文件格式为libpcap，这个格式也是tcpdump和其他工具所支持的格式。

## 可靠的TCP流量重构

Justniffer的主要功能就是能够处理所有复杂的底层协议问题，并提取出正确的TCP/IP流量：IP碎片、TCP重传数据、数据包排序等。它使用了部分Linux内核源代码来处理所有的TCP/IP内容。准确的说，它使用了修改版本的libnids代码库，其中包含了部分Linux内核源码。

## 重构并将HTTP内容存为文件

提供了多功能多用途的嗅探器来辅助重构TCP网络流，其中包括：

    
    
    HTTP嗅探器
    
    LDAP嗅探器
    
    SMTP嗅探器
    
    SIP嗅探器
    
    密码嗅探器

除此之外，Justniffer还可以恢复目标网络发送的各种文件。

## 可扩展性

该工具可支持用户使用外部脚本进行功能扩展。项目已经提供了一个Python脚本，可以用来恢复所有通过HTTP发送的文件，包括图片、文本、html和JavaScript等等。

## 功能概述

1、 可靠的TCP流量重构：使用了部分Linux内核代码，可以对数据包重新排序、重编译TCP分段以及IP碎片；

2、 切换文字模式：支持自定义；

3、 可扩展性：可使用bash、python、perl脚本以及ELF可执行文件等实现功能扩展；

4、 性能测试：它可以收集很多关于性能的数据，例如连接时间、关闭时间、请求时间和响应时间等等。

### 项目地址

Justniffer项目官网：【[传送门](https://sourceforge.net/projects/justniffer/files/)】

最新版本下载：【[justniffer_0.5.15.tar.gz](https://sourceforge.net/projects/justniffer/files/latest/download)】

 ***参考来源：[justniffer](https://www.kitploit.com/2019/02/justniffer-network-tcp-packet-sniffer.html)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

