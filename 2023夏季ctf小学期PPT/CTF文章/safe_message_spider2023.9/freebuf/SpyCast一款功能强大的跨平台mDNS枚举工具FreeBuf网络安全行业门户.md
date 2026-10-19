![](https://image.3001.net/images/20220930/1664538498_6336d7829e3dafa445043.png!small)

## 关于SpyCast

SpyCast是一款功能强大的跨平台mDNS枚举工具，该工具支持在主动模式下下递归查询服务，也可以在被动模式下仅侦听多播数据包。因此，广大研究人员可以使用该工具测试mDNS协议和本地网络的安全性。

## mDNS介绍

mDNS，即多播DNS，该协议将主机名解析为不包含本地名称服务器的小型网络中的IP地址。 它是一种零配置服务，使用与单播域名系统
（DNS）基本相同的编程接口，数据包格式和操作语义。 虽然Stuart Cheshire将mDNS设计为独立协议，但它可以与标准DNS服务器协同工作。

mDNS协议发布为 RFC 6762使用IP多播用户数据报协议 （UDP）数据包，由Apple Bonjour和开源Avahi软件包实现。
Android包含mDNS实现。 mDNS也已在Windows 10中实现，最初仅限于发现网络打印机[3] ，后来也能够解析主机名。

mDNS可以与DNS服务发现 （DNS-SD）结合使用， DNS服务发现是RFC 6763中单独指定的配套零配置技术。

mDNS主要实现了在没有传统DNS服务器的情况下使局域网内的主机实现相互发现和通信，使用的端口为5353，遵从dns协议，使用现有的DNS信息结构、名语法和资源记录类型。并且没有指定新的操作代码或响应代码。

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/evilsocket/spycast.git

### 代码构建

切换到项目目录下，然后使用cargo构建项目代码：

    
    
    cargo build --release

我们还可以针对不同的操作系统来构建代码包，比如说macOS平台下，可以使用下列命令构建：

    
    
    cargo tauri build

SpyCast还可以构建出不带默认用户交互界面的版本，此时所有的数据输出结果都会打印在控制台终端中：

    
    
    cargo build --no-default-features --release

## 工具运行

下列命令能够以主动模式运行SpyCast，该模式下工具将会递归查询所有可用的mDNS服务：

    
    
    ./target/release/spycast

下列命令能够以被动模式运行SpyCast，该模式下工具不会产生任何mDNS流量，并只会监听多播数据包：

    
    
    ./target/release/spycast --passive

查看工具帮助信息：

    
    
    spycast --help

## 工具运行截图

![](https://image.3001.net/images/20220930/1664538596_6336d7e45c2990fced18c.png!small)

## 许可证协议

本项目的开发与发布遵循[
_GPL3_](https://github.com/evilsocket/spycast/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **SpyCast** ：【[ _GitHub传送门_](https://github.com/evilsocket/spycast)】

