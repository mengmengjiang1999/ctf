![](https://image.3001.net/images/20191017/1571319755_5da86fcb22f1d.png!small)

## 工具介绍

RITA是一款专门针对网络流量分析与测试人员的开源框架，广大研究人员可以利用RITA来对收集到的安全威胁情报进行深度分析。

RITA能够以TSV格式来读取Bro/Zeek日志，该工具当前支持以下几个主要功能：

> 1、Beacon检测：搜索目标网络中的所有Beacon行为标记；
>
> 2、DNS隧道检测：搜索基于DNS的隐蔽通信信道标记；
>
> 3、黑名单检测：查询黑名单以搜索可疑域名和主机；

## 工具安装-【[
_安装手册_](https://github.com/activecm/rita/blob/master/docs/Manual%20Installation.md)】

### 自动化安装

RITA的自动安装工具目前支持Ubuntu 16.04 LTS，Security Onion*和CentOS 7。

1、从RITA项目的【[
_Release页面_](https://github.com/activecm/rita/releases/latest)】下载最新版本的install.sh文件。

2、给install.sh脚本提供可执行权限：

    
    
    chmod +x ./install.sh

3、使用下列命令运行安装器：

    
    
    sudo ./install.sh

如需在Security Onion平台上使用RITA来进行信息收集，请查看这篇【[
_技术文档_](https://securityonion.net/docs/RITA)】。

### 手动安装

构建RITA源码：

    
    
    go get github.com/activecm/rita
    
    (git clone git@github.com:activecm/rita.git)
    
    $GOPATH/src/github.com/activecm/rita
    
    cd $GOPATH/src/github.com/activecm/rita
    
    make

配置系统：

    
    
    sudo mkdir /etc/rita && sudo chmod 755 /etc/rita
    
    sudo mkdir -p /var/lib/rita/logs && sudo chmod -R 755 /var/lib/rita
    
    sudo cp $GOPATH/src/github.com/activecm/rita/etc/rita.yaml /etc/rita/config.yaml && sudo chmod 666 /etc/rita/config.yaml

## 工具使用

### 系统要求

> 1、操作系统：64位Ubuntu 16.04 LTS，并使用“apt-get”完成系统更新。
>
> 2、处理器：至少三核心，如果与其他虚拟机产生资源竞争，则有可能导致数据包丢失。
>
> 3、内存：至少16GB内存，如需监控100MB以上网络流量，则需64GB内存；如需监控1GB以上网络流量，则需128GB内存。
>
> 4、存储：至少300GB存储空间，建议使用1TB或更多。
>
> 5、网络：为了结合Bro/Zeek来不作流量，我们需要至少两块网卡，其中一个负责系统的管理，另一块负责捕捉端口流量。

### 配置文件

Filtering:
InternalSubnets是必须配置的，否则无法查看到分析结果。如果你的网络使用了标准RFC1918，内部IP范围为10.0.0.0/8,
172.16.0.0/12,
192.168.0.0/16，我们需要去掉配置文件中InternalSubnets数据域的注释，并根据我们的环境情况进行参数修改。RITA的主要目标是为了寻找已被入侵的内部系统在于外部系统通信的标识，并且能够自动过滤内部终端的通信。

除了Filtering: InternalSubnets之外，你可能还需要配置Filtering:
AlwaysInclude，它是一个范围列表，可以指定需要过滤的内容。

### 获取数据（生成Bro/Zeek日志）

选项1：生成PCAP

使用一个数据包嗅探工具生成PCAP文件，例如[ _tcpdump_](http://www.tcpdump.org/)和[
_wireshark_](https://www.wireshark.org/)等等。

（可选项）将多个PCAP文件整合为一个PCAP文件：

    
    
    mergecap -w outFile.pcap inFile1.pcap inFile2.pcap

或，利用Bro/Zeek日志生成PCAP文件：

    
    
    bro -r pcap_to_log.pcap local "Log::default_rotation_interval = 1 day"

选项2：安装Bro/Zeek，并直接监控目标接口【[ _控制指令_](https://www.zeek.org/sphinx/quickstart/)】

出于性能考虑，你可能需要编译Bro/Zeek源码，【[这个脚本](https://github.com/activecm/bro-install)】可以完成自动化编译。

RITA自动化安全器默认会对Bro/Zeek源码进行预编译，只需要在运行安装器的时候提供“--disable-bro”参数即可。

## 使用样例

如果你想获取当周有价值的威胁情报数据，可以直接使用下列RITA命令：

    
    
    rita import --rolling --numchunks 7 /opt/bro/logs/current week-dataset

如果你想获取48小时内有价值的威胁情报数据，可以直接使用下列RITA命令：

    
    
    rita import --rolling --numchunks 48 /opt/bro/logs/current 48-hour-dataset

## 使用RITA测试数据

### 使用show-X命令：

> 1、show-databases: 输出当前存储的数据集
>
> 2、show-beacons: 打印检测到了C2痕迹的主机列表
>
> 3、show-bl-hostnames: 打印黑名单中接收链接的主机名列表
>
> 4、show-bl-source-ips: 打印黑名单中初始化链接的IP列表
>
> 5、show-bl-dest-ips: 打印黑名单中接收链接的IP列表
>
> 6、show-exploded-dns: 打印DNS分析结果，显示隐蔽的DNS信道
>
> 7、show-long-connections: 打印长链接以及相关信息
>
> 8、show-strobes: 打印高频链接
>
> 9、show-useragents: 打印用户代理信息

### 以CSV/HTML格式显示数据：

> 1、-H：以人类可读的格式显示数据。
>
> 2、html-report：生成HTML报告。

## 项目地址

> RITA：【[ _GitHub传送门_](https://github.com/activecm/rita)】

### 许可证协议

> RITA项目遵循GNU GPL v3开源许可证协议。

 *** 参考来源：[
_activecm_](https://github.com/activecm/rita)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

