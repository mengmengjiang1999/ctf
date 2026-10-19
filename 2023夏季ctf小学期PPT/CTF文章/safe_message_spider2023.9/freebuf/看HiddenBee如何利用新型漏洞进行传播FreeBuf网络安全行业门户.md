***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

![16.jpg](https://image.3001.net/images/20180803/1533268006_5b63d0260997f.jpg!small)

## 写在前面的话

 **最近我们发现了一个试图利用CVE-2018-4878（Flash
Player中的漏洞）漏洞的攻击，其序列与我们当前发现的任何漏洞利用工具都不一样。经过调查，我们发现这是中国安全公司奇虎360在2017年年底所引用的现有开发框架的一部分。但当时payload似乎是一个推广广告软件的木马。而这次使用的payload它不是一个标准的PE文件。相反，它更像是一种多阶段可执行格式，并且它还充当一个下载加载程序，用于检索隐藏的Bee
miner僵尸网络使用的LUA脚本。这可能是第一个用来挖掘加密货币的bootkit案例。**

## 广告概述

攻击者利用成人网站的诱惑性广告将受害者吸引到钓鱼页面。我们认为此系列广告主要针对亚洲国家地区用户，根据所投放的广告和我们已知的数据。这个声称是可以在线约会服务的服务器包含一个恶意的iframe，其主要负责开发和感染用户。

![1.png](https://image.3001.net/images/20180803/1533267594_5b63ce8a5fa20.png!small)![2.png](https://image.3001.net/images/20180803/1533267607_5b63ce970789c.png!small)

## IE exploit

在这里，恶意代码从具有嵌入式加密块的网页开始执行。并采用Base64编码，然后使用[RC4](http://my.freebuf.com/post/edit/a%20href=)或[Rabbit](http://my.freebuf.com/post/edit/a%20href=)两种算法之一进行加密：

![3.png](https://image.3001.net/images/20180803/1533267672_5b63ced8b6d17.png!small)

在解密之后，该块将被执行。您可以在这里找到正在运行的Java
Script的解码版本。我们可以在脚本中看到，它会生成随机会话密钥，然后使用攻击者的公共RSA密钥对其进行加密：

![4.png](https://image.3001.net/images/20180803/1533267682_5b63cee2894af.png!small)

加密的密钥将传递到下一个函数并转换为JSON格式，对硬编码的URL执行POST请求：

![5.png](https://image.3001.net/images/20180803/1533267694_5b63ceee575df.png!small)

如果我们查看客户端和服务器之间的流量（客户端发送加密的`“key”`，服务器响应`“value”`），我们更明显发现这一点：

![6.png](https://image.3001.net/images/20180803/1533267704_5b63cef8b0954.png!small)

## 服务器端

1.攻击者的使用私有RSA密钥加密，服务器传递解密会话的密钥。

2.选择对称算法来(Rabbit或RC4)加密漏洞payload。

3.将加密的内容返回给客户端。由于客户端在内存中仍然有密钥的未加密版本，所以它能够解密并执行该漏洞。然而，只从通信流量不能检索原始会话密钥，也不可能重现漏洞。但幸运的是，我们在动态分析中成功捕获了漏洞。并且我们发现攻击者利用的漏洞是CVE-2018-8174。

## Flash漏洞利用

这是一个较新的Flash漏洞（CVE-2018-4878）利用程序,在奇虎360发布文档时并不是其exploit
kits的一部分，可能是为了增强其性能后来添加的。该漏洞中嵌入的shell代码仅仅是下一阶段的下载程序。成功利用后，它将在以下URL检索其payload：

![7.png](https://image.3001.net/images/20180803/1533267714_5b63cf02ee000.png!small)

这个扩展名为`.wasm`文件，伪造成一个Web Assembler模块。但事实上，它是完全不同的东西。

正如你所看到的，它加载了用于解压缩cabinet文件的`Cabinet.dll`模块。在后面的部分中，我们看到了用于通过HTTP协议进行通信的API和字符串。我们还发现了对`“dllhost.exe”`和`“bin/i386/core.sdb”`的引用。

![9.png](https://image.3001.net/images/20180803/1533267729_5b63cf114211d.png!small)

我们很容易猜到这个模块将下载并利用`dllhost.exe`来运行。而另一个字符串Base64编码的内容为：

![10.png](https://image.3001.net/images/20180803/1533267737_5b63cf1948415.png!small)

将其解码后的内容展现了更多的网址：

    
    
    http://103.35.72.223/git/wiki.asp?id=530475f52527a9ae1813d529653e9501
    http://103.35.72.223/git/glfw.wasm
    http://103.35.72.223/rt/lsv3i06rrmcu491c3tv82uf228.wasm
    

看看Fiddler捕获的流量，我们发现其模块确实在查询这些URL：

![11.png](https://image.3001.net/images/20180803/1533267744_5b63cf2040524.png!small)

请求来自`dllhost.exe`，这可能意味着上面的可执行文件已经被注入恶意代码。文件`glfw.wasm`与`Web
Assembly`之间没有任何共同之处。事实上，它是一个Cabinet文件，包含内部路径下的打包内容：`bin/i386/core.sdb`。从内部看，我们发现了相同的自定义可执行格式，比如DLL名称：

![12.png](https://image.3001.net/images/20180803/1533267751_5b63cf2703db2.png!small)

然后另一个问题是参与者可能试图通过假装使用SLTP协议来检索实际payload来隐藏流量，这可以在从核心内部的Cabinet文件中提取的字符串`core.sdb`中发现这一点：

    
    
    INSTALL_SOURCE
    &sid=%u
    INSTALL_SID
    INSTALL_CID
    sltp://setup.gohub[.]online:1108/setup.bin?id=128
    ntdll.dll
    ZwQueryInformationProcess
    VolumeNumber
    SCSIDISK
    os=%d&ar=%d
    kernel32.dll
    IsWow64Process
    RtlGetNtVersionNumbers
    %02x
    &sz=
    sltp
    

该主机名解析为`67.198.208[.]110`：

    
    
    Pinging setup.gohub.online [67.198.208.110] with 32 bytes of data:
    Reply from 67.198.208.110: bytes=32 time=76ms TTL=51
    

来自沙盒计算机的加密TCP网络流量显示了如何检索二进制的payload：

![13.png](https://image.3001.net/images/20180803/1533267760_5b63cf3000cee.png!small)

可见整个payload开发和检索过程相当复杂，如果考虑到活动背后的目的是用来开采加密货币时，那么也不难想到：

![14.png](https://image.3001.net/images/20180803/1533267766_5b63cf367279e.png!small)

这个矿机的独特之处在于，它通过使用bootkit实现持久性，如本文所述。受感染的主机将修改其主引导记录，以便在每次操作系统启动时启动矿机。

## 简单payload的复杂攻击

这种攻击在许多方面上都很有意思，因为它在漏洞利用交付部分中使用了不同的技术以及不同的打包payload技术。因此我们认为它集中在少数几个亚洲国家，不仅如此，它还表明威胁行动者并没有完全放弃exploit
kits，尽管在过去几年有明显的下降趋势。

![15.gif](https://image.3001.net/images/20180803/1533267775_5b63cf3fb95fc.gif!small)

### IOC

受污染的交友网站

`144.202.87[.]106`

exploit kits

`103.35.72[.]223`

52he3kf2g2rr6l5s1as2u0198k.wasm

`087FD1F1932CDC1949B6BBBD56C7689636DD47043C2F0B6002C9AFB979D0C1DD`

glfw.wasm

`CCD77AC6FE0C49B4F71552274764CCDDCBA9994DF33CC1240174BCAB11B52313`

Payload URL 和 IP

    
    
    setup.gohub[.]online:1108/setup.bin?id=128
    67.198.208[.]110
    

Miner Proxy

`133.130.101[.]254`

 ***参考来源[malwarebytes](https://blog.malwarebytes.com/threat-analysis/2018/07/hidden-bee-miner-delivered-via-improved-drive-by-download-toolkit/)，由周大涛编译，转载请注明来自FreeBuf.COM**

