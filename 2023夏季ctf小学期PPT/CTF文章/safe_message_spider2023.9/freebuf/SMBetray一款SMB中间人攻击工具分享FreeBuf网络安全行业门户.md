**PS：本文仅作技术分析，禁止用于其他非法用途**

**今天给大家介绍的是一款名叫SMBetray的工具，这是一款SMB中间人攻击工具，该工具可以通过文件内容交换、lnk交换和明文数据入侵来对目标客户端实施攻击。**

![aaaaa.png](https://image.3001.net/images/20180915/1537008236_5b9ce26c33130.png!small)

## SMBetray

该工具可允许攻击者拦截和修改不安全的SMB连接，在已知证书的情况下，该工具还可以入侵某些安全的SMB连接。

### 背景内容

该工具发布于Defcon 26上，相关演讲主题为“SMBetray – 后门与签名攻击”。

在SMB连接中，需要使用安全机制来保护服务器和客户端之间传输数据的完整性，而这种安全机制就是SMB签名和加密。首先，在签名过程中需要从服务器端获取密钥和证书，并对SMB数据包进行签名，最后再通过网络发送数据包。如果用户密码已知，那么攻击者就可以重新创建SessionBaseKey和所有其他的SMB密钥，并利用它们来修改SMB数据包，然后对修改后的数据包进行重新签名。除此之外，很多网站管理员默认会禁用签名功能，因此这种攻击方式的效率也会比较高。

## 功能介绍

> 1.被动下载通过有线网络发送的任意文件明文数据；
>
> 2.将目标客户端降级为NTLMv2（而非Kerberos）；
>
> 3.当目标目录被用户访问后，向目标目录中注入文件；
>
> 4.用同名的lnk文件替换掉所有的原始文件，并在用户点击后执行攻击者指定的命令或代码；
>
> 5.仅用同名的lnk文件替换目标系统中的可执行文件，并在用户点击后执行攻击者指定的命令或代码；
>
> 6.用攻击者注入的本地目录中的文件内容（扩展名为“X“）替换目标系统中扩展名为“X“的文件内容，扩展名可区分大小写；

## 工具安装

该工具要求系统可使用iptables，安装命令如下：

    
    
    sudo bash install.sh

## 工具使用

首先，对目标系统、网关或目的网络执行bi-directional arp-cache感染攻击，比如说：

    
    
    sudo arpspoof -i <iface> -c both -t <target_ip> -r <gateway_ip>

接下来，运行smbetray以及相关的攻击模块：

    
    
    sudo ./smbetray.py --passive ./StolenFilesFolder --lnkSwapAll "powershell -noP-sta -w 1 -enc AABCAD....(etc)" -I eth0

### Demo

点击【[这里](https://blog.quickbreach.io/smbetray-backdooring-and-breaking-signatures/)】查看该工具的使用样例。

***参考来源：[smbetray](https://github.com/quickbreach/smbetray)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

