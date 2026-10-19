## 介绍：

JARM 是一个活动的[传输层安全
(TLS)](https://en.wikipedia.org/wiki/Transport_Layer_Security)服务器指纹识别工具。

 **使用 JARM 进行扫描提供了识别和分组 Internet 上的恶意服务器的能力。**

[JARM tools]([https
://github.com/salesforce/jarm](https://github.com/salesforce/jarm))

## JARM 指纹可用于：

快速验证组中的所有服务器是否具有相同的 TLS 配置。

通过配置对 Internet 上的不同服务器进行分组，例如，识别服务器可能属于 Google、Salesforce 和 Apple。

识别默认应用程序或基础架构。

识别 Internet 上的恶意软件命令和控制基础设施以及其他恶意服务器。

## 本文中，您将了解到：

JARM 是如何工作的。

如何使用 JARM 来识别恶意服务器。

从被动网络安全黑名单转变为主动网络安全黑名单。

如何将 JARM 部署到您的检测和响应管道中。

JARM 如何用于配置验证和应用程序识别。

# JARM 的工作原理

    
    
    [zhy@zhy jarm]$ python jarm.py -V
    JARM version 1.0
    [zhy@zhy jarm]$ python jarm.py -h
    usage: jarm.py [-h] [-i INPUT] [-p PORT] [-v] [-V] [-o OUTPUT] [-j] [-P PROXY] [scan]
    
    Enter an IP address and port to scan.
    
    positional arguments:
      scan                  Enter an IP or domain to scan.
    
    options:
      -h, --help            show this help message and exit
      -i INPUT, --input INPUT
                            Provide a list of IP addresses or domains to scan, one domain or IP address per line. Optional:
                            Specify port to scan with comma separation (e.g. 8.8.4.4,853).
      -p PORT, --port PORT  Enter a port to scan (default 443).
      -v, --verbose         Verbose mode: displays the JARM results before being hashed.
      -V, --version         Print out version and exit.
      -o OUTPUT, --output OUTPUT
                            Provide a filename to output/append results to a CSV file.
      -j, --json            Output ndjson (either to file or stdout; overrides --output defaults to CSV)
      -P PROXY, --proxy PROXY
                            To use a SOCKS5 proxy, provide address:port.
    

在学习 JARM 的工作原理之前，了解 TLS
的工作原理很重要。TLS及其前身SSL用于加密常见应用程序（如Internet浏览器）的通信，以确保数据安全，也用于加密恶意软件，因此它可以进行隐藏在噪声中。中要启动
TLS 会话，客户端将在 TCP 三次握手之后发送 TLS Client Hello
消息。此数据包及其生成方式取决于构建客户端应用程序时使用的包和方法。服务器如果接受 TLS 连接，将使用 TLS Server Hello 数据包进行响应。

![image](https://image.3001.net/images/20220525/1653482074_628e225a76d41370b9f7d.gif!small)

TLS 服务器根据在 TLS 客户端 Hello 数据包中接收到的详细信息制定其服务器 Hello 数据包。根据应用程序或服务器的构建方式，服务器回复
Hello 的方式可能会有所不同，包括：

> 操作系统
>
> 操作系统版本
>
> 使用的库
>
> 使用的这些库的版本
>
> 调用库的顺序
>
> 自定义配置

所有这些因素导致每个 TLS 服务器以独特的方式响应。各种因素的组合使得不同组织部署的服务器不太可能有相同的响应。

下面是在[Wireshark](https://wireshark.com/)中查看的 TLS 客户端 Hello 和服务器 Hello 的示例。

![image](https://image.3001.net/images/20220525/1653481840_628e2170c35b715852943.png!small)

![image](https://image.3001.net/images/20220525/1653481847_628e2177e27d38ad629ca.png!small)

JARM 通过主动向目标 TLS 服务器发送 10 个 TLS 客户端 Hello 数据包并捕获 TLS 服务器 Hello
响应的特定属性来工作。然后以特定方式对聚合的 TLS 服务器响应进行哈希处理以生成 JARM 指纹。

JARM 中的 10 个 TLS 客户端 Hello 数据包经过特殊设计，可在 TLS 服务器中提取唯一响应。JARM 以不同的顺序发送不同的 TLS
版本、密码和扩展，以收集唯一的响应。服务器是否支持 TLS 1.3？它会与 1.2 密码协商 TLS 1.3
吗？如果我们将密码从最弱到最强排序，它会选择哪个密码？这些是 JARM 本质上要求服务器提取最独特的响应的不寻常问题的类型。然后对 10
个响应进行哈希处理以生成 JARM 指纹。

    
    
    [zhy@zhy-f0 jarm]$ python jarm.py -v baidu.com
    Domain: baidu.com
    Resolved IP: 220.181.38.251
    JARM: 29d29d00029d29d1fc29d29d29d29d881e59db99b9f67f908be168829ecef9
    Scan 1: c02f|0303|http/1.1|ff01-000b-0023-0010,
    Scan 2: c02f|0303|http/1.1|ff01-000b-0023-0010,
    Scan 3: |||,
    Scan 4: c02f|0303||ff01-000b-0023,
    Scan 5: c02f|0303||ff01-000b-0023,
    Scan 6: c011|0302|http/1.1|ff01-000b-0023-0010,
    Scan 7: c02f|0303|http/1.1|ff01-000b-0023-0010,
    Scan 8: c02f|0303|http/1.1|ff01-000b-0023-0010,
    Scan 9: c02f|0303|http/1.1|ff01-000b-0023-0010,
    Scan 10: c02f|0303|http/1.1|ff01-000b-0023-0010
    

![image](https://image.3001.net/images/20220525/1653481819_628e215bd6ed388c654e2.png!small)

![image](https://image.3001.net/images/20220525/1653481826_628e2162959126319791b.png!small)

在收到每个 TLS 服务器问候消息后，JARM 会使用 FIN 优雅地关闭连接，以免套接字打开。

## JARM 示例：

Domain| JARM  
---|---  
salesforce.com|
`2ad2ad0002ad2ad00042d42d00000069d641f34fe76acdc05c40262f8815e5`  
force.com| `2ad2ad0002ad2ad00042d42d00000069d641f34fe76acdc05c40262f8815e5`  
google.com| `27d40d40d29d40d1dc42d43d00041d4689ee210389f4f6b4b5b1b93f92252d`  
gmail.com| `27d40d40d29d40d1dc42d43d00041d4689ee210389f4f6b4b5b1b93f92252d`  
facebook.com| `27d27d27d29d27d1dc41d43d00041d741011a7be03d7498e0df05581db08a9`  
instagram.com|
`27d27d27d29d27d1dc41d43d00041d741011a7be03d7498e0df05581db08a9`  
oculus.com| `29d29d20d29d29d21c41d43d00041d741011a7be03d7498e0df05581db08a9`  
  
需要注意的是，JARM 是一种高性能指纹功能，不应将其视为或与安全加密功能混淆。

## 如何使用 JARM 识别恶意服务器

https://wangzhan.360.cn/296.html

