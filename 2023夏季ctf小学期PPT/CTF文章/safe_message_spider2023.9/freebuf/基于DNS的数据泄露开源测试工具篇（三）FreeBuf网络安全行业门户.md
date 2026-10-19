**免责声明：本文作者竭力保证文章内容可靠，但对于任何错误、疏漏或不准确的内容，作者不负任何责任。文章部分内容来源于网络是出于传递更多信息的目的，对此不负任何法律责任。本文仅用于技术分享与讨论，严禁用于其他用途。**
****  
 ****

## 一、前言

在[基于DNS的数据窃取开源工具篇(一)](https://www.freebuf.com/sectool/222561.html)和[基于DNS的数据窃取开源工具篇(二)](https://www.freebuf.com/sectool/223123.html)中，已经讨论DET和PyExfil两个开源项目关于利用DNS完成数据窃取的部分。本文将继续讨论如图1中所示的第三个开源工具DNSExfiltrator。

![1-DET、PyExfil、DNSExfiltrator、Egress-Assess的首页展示.png](https://image.3001.net/images/20191226/1577340753_5e044f5148e2e.png!small)图1
DET、PyExfil、DNSExfiltrator、Egress-Assess的首页展示

## 二、DNSExfiltrator简介

DNSExfitrator开源项目[1]是一个数据泄露测试工具，它利用DNS协议进行隐蔽的数据泄露。DNSExfiltrator采用C/S模式，其服务端使用python实现(dnsexfiltrator.py)，客户端提供C#源码，可通过csc.exe编译为Windows可执行文件；同时，也可以通过作者用JavaScript、Powershell包装后的脚本文件来启用客户端。DNSExfiltrator项目源码结构梳理如图2。

![2-DNSExfiltrator项目组成概况.png](https://image.3001.net/images/20191226/1577340762_5e044f5a52298.png!small)图2
DNSExfiltrator项目组成概况

总结DNSExfiltrator的特色主要有：

> 1) 默认使用系统定义的DNS服务器，可以通过-s 指定特定DNS服务端。
>
> 2) 支持DoH，通过-h参数启用。
>
> 3) 默认使用base64URL编码，但也可以通过-b32指定使用Base32编码。
>
> 4) 支持基础R**加密对数据进行加解密。
>
> 5) 提供一些可选功能用来逃避检测，主要有：
>
> a) 请求限制——每个DNS请求间隔时间大小，实现更隐蔽的数据窃取。
>
> b) 减小DNS请求大小，默认使用每个DNS请求最大剩余可用字节。
>
> c) 减小DNS标签大小，默认使用最大支持的标签长度63字符。

## 三、基于DNS的数据窃取的源码简要分析

DNSExfiltrator工具采用C/S模式，服务端为DNSExfiltrator.py文件，客户端使用C#实现，可通过csc.exe编译为Windows可执行程序。同时，为了便于使用，作者还提供了包装了DNSExfiltrator客户端二进制文件的Powershell脚本和JavaScript脚本。

 **DNSExfiltrator准备条件：**

1）拥有一个域名，并将其DNS记录指向运行DNSExfiltrator.py的服务端；

2）服务端依赖python的dnslib库。

### （一）服务端源码分析

对服务端源码文件dnsexfiltrator.py进行梳理、分析，将其源码概况和服务端工作的主要流程整理如图3。

![3-服务端源码概况及服务端的主要流程.png](https://image.3001.net/images/20191226/1577340773_5e044f65f05d1.png!small)图3
服务端源码概况及服务端的主要流程

通过对服务端源码dnsexfiltrator.py的梳理、分析，整理服务端接收、恢复窃密数据的主要流程为：

1) 监听53端口并接收请求数据。当DNS请求包的请求类型为TXT记录，则进入第（2）步。

2) 提取请求的子域名，即使用dnslib库提取数据包的qname，DNSExfiltrator中qname的拼接组成主要有如图4所示的两种。

![4 -DNSExfiltrator服务端提取的qname组成结构.png](https://image.3001.net/images/20191226/1577340817_5e044f91ab77d.png!small)图4
DNSExfiltrator服务端提取的qname组成结构

3) 判断包类型，若qname以"init."开始，则为初始化请求包执行步骤（4），否则进入步骤（5）。

4)
"init."标识该包为初始化包，则首先进行Base32解码，然后提取窃取文件的“filename：文件名”、“nbchunks：数据块总数”、“BASE32：是否使用BASE32编码”，并初始化接收准备。

5) 此类包传输实际窃密文件数据，窃取的数据加密、编码后拼接组成的查询子域名如图5。

![5 -用于传输文件数据的子域名拼接组成示例.png](https://image.3001.net/images/20191226/1577340825_5e044f9946349.png!small)图5
用于传输文件数据的子域名拼接组成示例

6) 当某一个查询请求中的包序号等于块总数时，标志着窃取的文件数据已传输完毕，开始执行写入、恢复为本地文件的操作。

 **注：服务端处理初始化包后会回复客户端请求的TXT记录为“OK”，处理真实窃密数据包后，则会回复TXT记录为对应“包序号”。**

### （二）客户端源码简要分析

DNSExfiltrator客户端采用C#语言编写，可以编译为独立的可执行文件或一个DLL。编译方法：

1) 编译为Windows可执行程序编译：

    
    
    C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe /unsafe/reference:System.IO.Compression.dll /out:dnsExfiltrator.exe dnsExfiltrator.cs

2) 编译为DLL：

    
    
    C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe/unsafe /target:library /reference:System.IO.Compression.dll/out:dnsExfiltrator.dll dnsExfiltrator.cs

![6 -DNSExfiltrator客户端源码结构及主要流程.png](https://image.3001.net/images/20191226/1577340860_5e044fbcbb684.png!small)图6
DNSExfiltrator客户端源码结构及主要流程

通过对DNSExfiltrator.cs的梳理和分析，其源码结构和客户端工作主要流程如图6。参照图6，整理DNSExfiltrator发送窃密文件数据的主要流程如下：

1) 预处理工作，主要是通过指定的标签最大值、域名最大长度，计算拼接子域名时的相关参数值。

2) 读取文件数据到内存中，完成压缩、加密、编码。

3) 发送初始化DNS包，包括将要传输的文件信息包括：文件名、数据块总数、编码方式等，各信息拼接的结构如图7。

![7 -DNSExfiltrator初始化包的组成结构.png](https://image.3001.net/images/20191226/1577340871_5e044fc78d774.png!small)图7
DNSExfiltrator初始化包的组成结构

4) 通过服务端响应的TXT记录“ok”，确认初始包发送成功。

5) 按步骤（1）计算所得参数值，将文件数据切分为数据块，然后按图8所示的组成结构拼接成子域名。

![8 -DNSExfiltrator窃密数据包的组成结构.png](https://image.3001.net/images/20191226/1577340893_5e044fddc4096.png!small)图8
DNSExfiltrator窃密数据包的组成结构

6) 逐个发送构建好的DNS TXT请求包。其中，客户端会根据服务端对每个DNS
TXT记录响应的包序号来确认数据发送成功后，才发送下一个携带窃密文件数据的DNS TXT请求包。

## 四、小结

### （一）DNSExfiltrator的优势分析：

1）支持使用DoH形式的DNS解析，且可以自行指定DoH服务提供商。

2）客户端使用C3语言编写，便于编译为Windows可执行文件或DLL，且作者还提供了使用DNSExfiltrator的JS、Powershell脚本。

3）客户端、服务端依赖较少，环境搭建简单。

### （二）DNSExfiltrator的不足之处：

1）包序号在工具的窃密和文件恢复过程中尤为重要，在实际使用时不稳定。

2）未提供文件校验，窃取的数据完整、真实不能保证。

3）每个包按包序号逐个发送、确认，在实际DNS请求情况下效率低、易出错。

 **参考链接：**  

[1] [DNSExfiltrator项目地址](https://github.com/Arno0x/DNSExfiltrator)  

 ***本文作者：GZHU/asUwIll，转载请注明来自FreeBuf.COM**

