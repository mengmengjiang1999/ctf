## 关于Gorsair

Gorsair是一款功能强大的针对Docker容器的安全分析和渗透测试工具，可以帮助广大研究人员检查目标Docker容器中潜在的安全问题，并发现和访问目标Docker容器的API。一旦成功访问了目标Docker守护进程，就可以使用Gorsair直接在远程容器上执行命令了。

众所周知，在外网上暴露或公开Docker
API是一种非常危险的行为，因为这样可以允许恶意代理获取所有其他容器、映像和系统的信息。如果映像使用的是root用户，还可能允许攻击者获得针对整个系统的高级访问权限。

而Gorsair的诞生，将极大程度地提升Docker容器在API方面的安全性，以更好地保证Docker容器的安全。

## 工具安装

### 发布版本安装

首先，我们需要设置好需要安装的Gorsair发行版的“GORSAIR_VERSION”版本号信息。

接下来，设置对应操作系统的“OS”操作系统信息（linux、windows或darwin）。

组后，设置对应的系统架构“ARCH”（amd64、arm或ppc64le）。

配置好上述内容之后，我们就可以运行下列命令来安装Gorsair：

    
    
    curl -sS https://github.com/Ullaakut/Gorsair/releases/download/$GORSAIR_VERSION/gorsair_$OS_$ARCH --output /usr/local/bin/gorsair && chmod +x /usr/local/bin/gorsair

### 从代码源安装

首先，确保已经安装好了支持所有工具模块的Go版本（v1.11及以上版本）。

其次，确保系统环境变量中已经将“GO111MODULE”变量设置为了“on”。

接下来，使用下列命令将该项目源码克隆至本地，并在项目根目录下运行构建语句：

    
    
    git clone https://github.com/Ullaakut/Gorsair.git
    
    go build -o /usr/local/bin/gorsair cmd/*.go

## 命令行参数

> -t, --targets: 根据nmap目标格式设置目标，样例：--targets="192.168.1.72,192.168.1.74"；
>
> -p, --ports: (默认: 2375,2376) 设置自定义端口；
>
> -s, --speed: (默认: 4)
> 设置自定义nmap查找预设以提高速度或准确性。如果你试图扫描一个不稳定且速度缓慢的网络，建议降低该值；如果在一个性能非常好且可靠的网络上，建议增加该值；
>
> -D, --decoys: 要使用的诱饵IP地址列表
>
> -e, --interface: 需要使用的网络接口
>
> \--proxies:需要使用的HTTP/SOCKS4代理列表
>
> -S, --spoof-ip: IP地址欺骗所使用的IP地址；
>
> \--spoof-mac: MAC地址欺骗所使用的MAC地址；
>
> -v, --verbose: 启用Verbose日志模式；
>
> -h, --help: 显示工具实使用信息；

## 工具使用演示

![](https://image.3001.net/images/20220226/1645816425_62192a69d6b7813d65a1f.gif)

## 如何保护自己的容器免受此类攻击

> 避免将可访问Docker套接字的容器暴露在外网中
>
> 避免在Docker容器中使用root账号

## 工具演示视频

 **视频地址：** 【[ _点我观看_](https://asciinema.org/a/226476)】

## 项目地址

 **Gorsair：** 【[ _GitHub传送门_](https://github.com/Ullaakut/Gorsair)】

## 参考资料

> [ _https://nmap.org/book/man-target-> specification.html_](https://nmap.org/book/man-target-specification.html)
>
> [ _https://nmap.org/book/man-performance.html_](https://nmap.org/book/man-> performance.html)
>
> [ _https://nmap.org/book/man-bypass-firewalls-> ids.html_](https://nmap.org/book/man-bypass-firewalls-ids.html)
>
> [ _https://nmap.org/book/man-bypass-firewalls-> ids.html﻿_](https://nmap.org/book/man-bypass-firewalls-ids.html)

