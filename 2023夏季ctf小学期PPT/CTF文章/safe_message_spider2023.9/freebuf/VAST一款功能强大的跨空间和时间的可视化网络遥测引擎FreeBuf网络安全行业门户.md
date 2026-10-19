![](https://image.3001.net/images/20210512/1620827937_609bdf210281154bd3786.png!small)

## 关于VAST

VAST是一款功能强大的跨空间和时间的可视化网络遥测引擎，可用于数据驱动的安全审查活动中。

## 核心功能

高流量数据处理：支持每秒导入超过10万个事件的多种日志格式，包括Zeek、Suricata、JSON和CSV。

低延迟查询：由于多级位图索引和参与者模型并发性，整个数据池的响应时间为亚秒级，有助于对整个数据集进行即时指标检查。

灵活的导出格式：访问通用文本格式（ASCII、JSON、CSV）、二进制格式（MRT、PCAP）的数据。

强大的数据模型和查询语言：通用半结构化数据模型允许以类型化方式表达复杂数据，可以通过特定于域的操作实现强大的数据子集设置，例如top-k前缀搜索IP地址和子集关系。

## 工具获取

Linux用户可以直接点击【[ _这里_](https://storage.googleapis.com/tenzir-public-data/vast-static-builds/vast-static-latest.tar.gz)】或通过cURL下载最新版本的静态源码：

    
    
    curl -L -O https://storage.googleapis.com/tenzir-public-data/vast-static-builds/vast-static-latest.tar.gz

接下来，我们需要手动解压压缩文档。其中将包含三个目录，即bin、etc和share。然后，我们需要直接在bin目录中调用源码：

    
    
    tar xfz vast-static-latest.tar.gz
    
    bin/vast --help

如果想要直接在计算机中为本地主机安装VAST，可以直接将代码包解压至/usr/local/文件夹中。

FreeBSD和macOS用户则需要构建源码，此时需要使用下列命令将该项目源码克隆至本地：

    
    
    git clone --recursive https://github.com/tenzir/vast

安装好所有的依赖组件之后，我们就可以使用下列命令构建VAST了：

    
    
    ./configure
    
    cmake --build build
    
    cmake --build build --target test
    
    cmake --build build --target install
    
    cmake --build build --target integration

## 工具使用

开启一个VAST节点：

    
    
    vast start

导入Zeek日志：

    
    
    zcat *.log.gz | vast import zeek

针对过去一小时的数据执行一次查询，以JSON格式呈现结果：

    
    
    vast export json ':timestamp > 1 hour ago && (6.6.6.6 || 5353/udp)'

导入一个PCAP包：

    
    
    vast import pcap -c 1024 < trace.pcap

对PCAP数据执行一次查询，以数据包时间排序，并导入至tcpdump：

    
    
    vast export pcap "sport > 60000/tcp && src !in 10.0.0.0/8" \
    
      | ipsumdump --collate -w - \
    
      | tcpdump -r - -nl

## 项目地址

VAST：【[ _GitHub传送门_](https://github.com/tenzir/vast)】

## 参考资料

[ _https://arrow.apache.org/_](https://arrow.apache.org/)

[ _https://www.zeek.org/_](https://www.zeek.org/)

[ _https://suricata-ids.org/_](https://suricata-ids.org/)

[ _https://storage.googleapis.com/tenzir-public-data/vast-static-builds/vast-static-latest.tar.gz_](https://storage.googleapis.com/tenzir-public-data/vast-static-builds/vast-static-latest.tar.gz)

[
_https://github.com/tenzir/vast/blob/master/INSTALLATION.md﻿_](https://github.com/tenzir/vast/blob/master/INSTALLATION.md)

