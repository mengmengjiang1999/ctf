![](https://image.3001.net/images/20220818/1660792241_62fdadb149e93620868e8.jpg!small)

## 关于PR-DNSd

PR-DNSd是一个功能强大的被动递归DNS守护程序，该工具的主要功能和使用场景如下：

> 1、以本地主机DNS服务运行；
>
> 2、以企业内部DNS服务器运行，还能够进行有意义的EDR/IR和日志分析；
>
> 3、以云服务运行，从非企业环境/设备（家庭网络或BYOD等）收集被动DNS数据；
>
> 4、在云环境中以DNS-over-TLS服务器运行，为支持的设备提供额外的私有DNS服务，例如Android
> 9的私有DNS或移动设备基于域模式的防火墙/代理配置；

## 工具下载和快速使用

### 源码获取

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/korc/PR-DNSd.git

### Go安装

该工具基于Go语言开发，因此广大研究人员首先需要在本地设备上安装并配置好Golang环境。

接下来，使用下列命令将该项目安装到本地，并进行工具配置，配置完成后即可开始使用（以google.com为例）：

    
    
    go get github.com/korc/PR-DNSd
    
    sudo setcap cap_net_bind_service,cap_sys_chroot=ep go/bin/PR-DNSd
    
    go/bin/PR-DNSd -upstream *9.9.9.9:53 -listen 127.0.0.1:53
    
    echo nameserver 127.0.0.1 | sudo tee /etc/resolv.conf
    
    dig google.com
    
    dig -x $(dig +short google.com)

如果你无法使用setcap，则需要使用-chroot ""和-listen :<high_port>选项，或以root权限运行。

## 工具使用

### 工具帮助信息

    
    
    -cert string
    
        TCP-TLS监听器证书
    
    -chroot string
    
        chroot 目录设置 (默认为"/var/tmp")
    
    -count int
    
        应用去抖动延迟之前允许的响应计数 (默认为100)
    
    -ctmout string
    
        上游查询的客户端超时
    
    -debounce string
    
        UDP响应到单个IP之间所需的持续时间，以防御DoS (默认为"200ms")
    
    -key string
    
        TCP-TLS证书密钥 (默认为-cert的值)
    
    -listen string
    
        监听地址 (默认为":53")
    
    -silent
    
        静默模式，不报告普通数据
    
    -store string
    
        将PTR数据存储到指定文件
    
    -tlslisten string
    
        TCP-TLS监听器地址 (默认为":853")
    
    -upstream string
    
        上游DNS服务器 (tcp-tls:// prefix for DoT) (默认为"1.1.1.1:53")

### 以私有服务器运行（Android 9私有DNS设置）

    
    
    PR-DNSd -tlslisten :853 -cert YOUR_SERVER_CRT_KEY_PEM -upstream 1.1.1.1:53 -store pr-dnsd

## 工具使用演示

![](https://image.3001.net/images/20220818/1660792229_62fdada5819f983d09c06.jpg!small)

## 许可证协议

本项目的开发与发布遵循[ _MIT_](https://github.com/korc/PR-DNSd/blob/master/LICENSE.txt)开源许可证协议。

## 项目地址

 **PR-DNSd** ：【[ _GitHub传送门_](https://github.com/korc/PR-DNSd)】

