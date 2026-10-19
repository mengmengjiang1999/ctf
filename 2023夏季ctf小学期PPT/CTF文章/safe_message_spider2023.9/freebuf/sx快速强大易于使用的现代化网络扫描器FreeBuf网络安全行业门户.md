![](https://image.3001.net/images/20210825/1629875868_6125ee9c0adaaa2c74a67.jpg!small)

## 关于sx

sx是一款基于命令行接口的网络扫描器，该工具严格遵循UNIX的设计理念，而该项目的主要目标是为广大研究人员提供一个简洁、快速、易于使用的强大网络扫描器。

## 功能介绍

> 运行速度比Nmap要快30倍；
>
> ARP扫描：支持扫描本地网络以检测活动设备；
>
> ICMP扫描：使用高级ICMP扫描技术来检测活动主机和防火墙规则；
>
> TCP SYN扫描：传统半开放扫描以查找开放TCP端口；
>
> TCP FIN/NULL/XMAS扫描：扫描某些防火墙绕过技术；
>
> 自定义TCP扫描：发送任意形式数据包，并获得回复数据包中设置的所有TCP标志的结果；
>
> UDP扫描：扫描UDP端口并获取全部ICMP响应，以检测开放端口和防火墙规则；
>
> 应用程序扫描：包括SOCKS5扫描、Docker扫描和Elasticsearch扫描；
>
> 随机枚举IP地址；
>
> JSON格式输出支持；

## 工具安装

广大研究人员可以直接点击【[ _这里_](https://github.com/v-byte-cpu/sx/releases)】从该项目GitHub主页的Releases页面下载sx，并将可执行文件路径添加至PATH环境变量中。

### 源码构建

 **要求：**

> [ _Go v1.15或更新版本_](https://golang.org/dl/)；
>
> [ _libpcap_](https://www.tcpdump.org/)；

接下来，切换至项目根目录，然后运行下列命令：

    
    
    go build

## 工具使用

### ARP扫描

扫描你的本地网络，并显示已连接设备的IP地址、MAC地址和相关硬件厂商信息：

    
    
    sx arp 192.168.0.1/24

样本输出：

    
    
    192.168.0.1          b0:be:76:40:05:8d    TP-LINK TECHNOLOGIES CO.,LTD.
    
    192.168.0.111        80:c5:f2:0b:02:e3    AzureWave Technology Inc.
    
    192.168.0.171        88:53:95:2d:3c:af    Apple, Inc.

JSON格式输出：

    
    
    sx arp --json 192.168.0.1/24

样本输出：

    
    
    {"ip":"192.168.0.1","mac":"b0:be:76:40:05:8d","vendor":"TP-LINK TECHNOLOGIES CO.,LTD."}
    
    {"ip":"192.168.0.111","mac":"80:c5:f2:0b:02:e3","vendor":"AzureWave Technology Inc."}
    
    {"ip":"192.168.0.171","mac":"88:53:95:2d:3c:af","vendor":"Apple, Inc."}

### TCP扫描

跟Nmap或其他扫描器不同，sx指挥使用ARP缓存的概念。我们假设实际的ARP缓存位于arp.cache文件中，我们就可以执行下列arp扫描了：

    
    
    sx arp 192.168.0.1/24 --json | tee arp.cache

拿到ARP缓存文件后，我们就可以执行类似TCP SYN之类的高等级协议扫描了：

    
    
    cat arp.cache | sx tcp -p 1-65535 192.168.0.171

样本输出：

    
    
    192.168.0.171        22
    
    192.168.0.171        443

此时，我们已经发现了端口22和443为开放状态。

JSON格式输出：

    
    
    cat arp.cache | sx tcp  --json -p 1-65535 192.168.0.171

样本输出：

    
    
    {"scan":"tcpsyn","ip":"192.168.0.171","port":22}
    
    {"scan":"tcpsyn","ip":"192.168.0.171","port":443}

### VPN接口扫描

    
    
    sx tcp 10.1.27.1 -p 80 --json

### Elasticsearch扫描

Elasticsearch扫描能够获取集群信息和所有索引节点信息：

    
    
    sx elastic -p 9200 10.0.0.1/16

## 工具使用帮助

    
    
    sx help

## 许可证协议

本项目的开发与发布遵循MIT开源许可证协议。

## 项目地址

 **sx：** 【[ _GitHub传送门_](https://github.com/v-byte-cpu/sx)】

## 参考资料

> [
> _https://tools.ietf.org/rfc/rfc793.txt_](https://tools.ietf.org/rfc/rfc793.txt)
>
> [
> _https://tools.ietf.org/rfc/rfc768.txt_](https://tools.ietf.org/rfc/rfc768.txt)
>
> [
> _https://tools.ietf.org/rfc/rfc1122.txt_](https://tools.ietf.org/rfc/rfc1122.txt)
>
> [
> _https://tools.ietf.org/rfc/rfc1928.txt_](https://tools.ietf.org/rfc/rfc1928.txt)
>
> [
> _https://tools.ietf.org/rfc/rfc792.txt_](https://tools.ietf.org/rfc/rfc792.txt)

