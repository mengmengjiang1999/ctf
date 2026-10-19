![](https://image.3001.net/images/20211002/1633147063_6157d8b73587315893eb6.png!small)

## 关于DNSTake

DNSTake是一款功能强大的域名安全工具，该工具可以通过检测导致子域名托管的缺少托管的DNS区域。

当子域名（subdomain.example.com）或域名将其权威域名服务器设置为提供商（例如AWS Route 53、Akamai、Microsoft
Azure等），但托管区域已被删除时，就会出现DNS接管漏洞。因此，当请求DNS记录时，服务器会响应SERVFAIL错误。这将允许攻击者在正在使用的服务上创建丢失的托管区域，从而控制该（子）域名的所有DNS记录。

## 工具安装

### 预编译工具

广大研究人员可以访问该项目的【[
_Releases页面_](https://github.com/pwnesia/dnstake/releases)】直接下载该工具的预编译版本，解压后即可在本地运行。

### 源码安装

首先，我们需要安装并配置好Go 1.16+编译器环境。

接下来，运行下列命令来快速安装DNSTake：

    
    
    ▶ go install github.com/pwnesia/dnstake/cmd/dnstake@latest

或者，我们也可以直接使用下列命令手动通过源码构建DNSTake可执行程序：

    
    
    ▶ git clone https://github.com/pwnesia/dnstake
    
    ▶ cd dnstake/cmd/dnstake
    
    ▶ go build .
    
    ▶ (sudo) mv dnstake /usr/local/bin

## 工具使用

    
    
    $ dnstake -h
    
    ▄▄▄▄   ▐ ▄ .▄▄ ·▄▄▄▄▄ ▄▄▄· ▄ •▄ ▄▄▄ .
    
      ██▪ ██ •█▌▐█▐█ ▀.•██  ▐█ ▀█ █▌▄▌▪▀▄.▀·
    
      ▐█· ▐█▌▐█▐▐▌▄▀▀▀█▄▐█.▪▄█▀▀█ ▐▀▀▄·▐▀▀▪▄
    
      ██. ██ ██▐█▌▐█▄▪▐█▐█▌·▐█ ▪▐▌▐█.█▌▐█▄▄▌
    
      ▀▀▀▀▀• ▀▀ █▪ ▀▀▀▀ ▀▀▀  ▀  ▀ ·▀  ▀ ▀▀▀
    
     
    
            (c) pwnesia.org — v0.0.1
    Usage:
    
      [stdin] | dnstake [options]
    
      dnstake -t HOSTNAME [options]  
    Options:
    
      -t, --target <HOST/FILE>   定义单个目标主机或目标主机列表
    
      -c, --concurrent <i>       设置并发等级（默认：25）
    
      -s, --silent               减少错误输出或清理输出数据
    
      -h, --help                显示帮助信息
    
    Examples:
    
      dnstake -t (sub.)domain.tld
    
      dnstake -t hosts.txt
    
      cat hosts.txt | dnstake
    
      subfinder -silent -d domain.tld | dnstake

## 许可证地址

本项目的开发与发布遵循MIT开源许可证协议。

## 项目地址

 **DNSTake：** 【[ _GitHub传送门_](https://github.com/pwnesia/dnstake)】

## 参考资料

> [ _https://golang.org/doc/install_](https://golang.org/doc/install)
>
> [
> _https://github.com/projectdiscovery/retryabledns_](https://github.com/projectdiscovery/retryabledns)
>
> [
> _https://0xpatrik.com/content/images/2018/08/ns_automation-2.png_](https://0xpatrik.com/content/images/2018/08/ns_automation-2.png)
>
> [ _https://github.com/indianajson/can-i-take-over-dns#what-is-a-dns-> takeover_](https://github.com/indianajson/can-i-take-over-dns#what-is-a-dns-> takeover)
>
> [ _https://0xpatrik.com/subdomain-takeover-> ns/_](https://0xpatrik.com/subdomain-takeover-ns/)

