![](https://image.3001.net/images/20221025/1666695539_6357c1731e7cebe8462f0.png!small)  

## 关于MHDDoS

MHDDoS是一款功能强大的DDoS服务器/站点安全测试工具，该工具包含56种技术，可以帮助广大研究人员对自己的服务器或网站执行DDoS安全测试。

## 工具技术

### Layer7

> GET | GET 泛洪
>
> POST | POST 泛洪
>
> OVH | 绕过OVH
>
> RHEX | 随机HEX
>
> STOMP | 绕过chk_captcha
>
> STRESS | 使用高位字节发送HTTP包
>
> DYN | 一种随机子域名的新方法
>
> DOWNLOADER | 缓慢读取数据的新方法
>
> SLOW | 一种DDoS的技术
>
> HEAD | https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/HEAD
>
> NULL | 空UserAgent
>
> COOKIE | 随机Cookie PHP 'if (isset($_COOKIE))'
>
> PPS | 仅'GET / HTTP/1.1\r\n\r\n'
>
> EVEN | 包含更多Header的GET方法
>
> GSB | Google Project Shield 绕过
>
> DGB | DDoS Guard 绕过
>
> AVB | Arvan Cloud 绕过
>
> BOT | Like Google bot
>
> APACHE | Apache漏洞利用
>
> XMLRPC | WP XMLRPC 漏洞利用(add /xmlrpc.php)
>
> CFB | CloudFlare 绕过
>
> CFBUAM | CloudFlare Under Attack Mode 绕过
>
> 绕过 | 绕过 Normal AntiDDoS
>
> BOMB | 绕过 with codesenberg/bombardier
>
> KILLER | 执行多线程DDoS攻击
>
> TOR | 绕过 onion website

### Layer4

> TCP | TCP 泛洪绕过
>
> UDP | UDP 泛洪绕过
>
> SYN | SYN 泛洪
>
> CPS | 开启或关闭连接代理
>
> ICMP | Icmp请求泛洪 (Layer3)
>
> CONNECTION | 使用代理打开活动连接
>
> VSE | 发送VSE协议
>
> TS3 | 发送Teamspeak 3 Status Ping 协议
>
> FIVEM | 发送Fivem Status Ping 协议
>
> MEM | Memcached 放大攻击
>
> NTP | NTP 放大攻击
>
> MCBOT | Minecraft Bot 攻击
>
> MINECRAFT | Minecraft Status Ping 协议
>
> MCPE | Minecraft PE Status Ping 协议
>
> DNS | DNS 放大攻击
>
> CHAR | Chargen 放大攻击
>
> CLDAP | Cldap 放大攻击
>
> ARD | Apple Remote Desktop 放大攻击
>
> RDP | Remote Desktop Protocol 放大攻击

### 工具

> CFIP | 寻找基于Cloudflare的网站真实IP地址
>
> DNS | 显示站点的DNS记录
>
> TSSRV | TeamSpeak SRV解析器
>
> PING | PING服务器
>
> CHECK | 检测目标站点状态
>
> DSTAT | 显示收到的字节数据

### 其他

> STOP | 终止所有攻击测试
>
> TOOLS | 终端工具
>
> HELP | 显示工具帮助信息

## 工具要求

> [dnspython](https://github.com/rthalley/dnspython)
>
> [cfscrape](https://github.com/Anorov/cloudflare-scrape)
>
> [impacket](https://github.com/SecureAuthCorp/impacket)
>
> [requests](https://github.com/psf/requests)
>
> [Python3](https://python.org/)
>
> [PyRoxy](https://github.com/MatrixTM/PyRoxy)
>
> [icmplib](https://github.com/ValentinBELYN/icmplib)
>
> [certifi](https://github.com/certifi/python-certifi)
>
> [psutil](https://github.com/giampaolo/psutil)
>
> [yarl](https://github.com/aio-libs/yarl)

## 工具安装

### 源码安装

该工具基于Python开发，因此我们首先需要在本地设备上安装并配置好Python环境。接下来，使用下列命令将该项目源码克隆至本地，并使用pip和项目提供的requirements.txt来配置工具组件：

    
    
    git clone https://github.com/MatrixTM/MHDDoS.git
    
    cd MHDDoS
    
    pip install -r requirements.txt

### One-Line安装

    
    
    apt -y update && apt -y install curl wget libcurl4 libssl-dev python3 python3-pip make cmake automake autoconf m4 build-essential ruby perl golang git && git clone https://github.com/MatrixTM/MHDDoS.git && cd MH* && pip3 install -r requirements.txt

## 工具使用样例

### Layer7（网站）

    
    
    python start.py bypass https://example.com 5 101 socks5.txt 100 3600
    
    python start.py bomb https://example.com 0 50 proxy.txt 100 3600

### Layer4（服务器）

    
    
    python start.py udp 1.1.1.1:53 1 3600
    
    python start.py dns 1.1.1.1:53 100 3600 dns.txt
    
    python start.py minecraft 1.1.1.1:53 1000 3600 5 socks5.txt

### 调试模式（记录攻击状态）

    
    
    python start.py bypass https://example.com 5 1000 socks5.txt 100 100 true
    
    python start.py udp 1.1.1.1:53 1 100 true
    
    python start.py dns 1.1.1.1:53 1 100 dns.txt true
    
    python start.py minecraft 1.1.1.1:53 1 100 5 socks5.txt true

### 工具/帮助

    
    
    python start.py tools
    
    python start.py help

## 工具运行截图

![](https://image.3001.net/images/20221025/1666695683_6357c2032a00b7f571bce.png!small)

![](https://image.3001.net/images/20221025/1666695691_6357c20ba03e5663cbd4d.png!small)

## 工具视频

 **使用演示** ：【[ _点我观看_](https://www.aparat.com/v/bHcP9)】

 **工具教程** ：【[ _点我观看_](https://aparat.com/v/XPn5Z)】

## 许可证协议

本项目的开发与发布遵循[
_MIT_](https://github.com/MatrixTM/MHDDoS/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **MHDDoS** ：【[ _GitHub传送门_](https://github.com/MatrixTM/MHDDoS)】

