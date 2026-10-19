![](https://image.3001.net/images/20200215/1581753083_5e47a2fb6cd7b.bmp!small)

## 写在前面的话

 **就在不久之前，安全研究人员[ _Orange Tsai_](https://twitter.com/orange_8361)在一些常见的SSL-VPN产品中[ _发现了几个安全漏洞_](https://blog.orange.tw/2019/07/attacking-ssl-vpn-part-1-preauth-rce-on-palo-alto.html)，这些漏洞将允许攻击者通过安全防护设备来入侵目标网络系统，其中存在安全漏洞的构造函数如下：**

> Palo Alto
>
> Fortinet
>
> Pulse Secure

实际上，这些年来一直都有安全研究人员不断地从安全相关的设备中发现严重的安全漏洞，这对于我们这些安全从业人员来说，难免有些讽刺意味。

在这篇文章中，我们将对SonicWall的安全产品进行分析，该厂商曾表示相关产品[ _不会受到Palo
Alto漏洞的影响_](https://www.sonicwall.com/support/product-notification/security-advisory-sonicwall-not-affected-by-critical-remote-code-execution-vulnerability-cve-2019-1579/190805112136807/)，那么我们一起来看一看厂商所说的是否属实。¯\\_(ツ)_/¯

## 产品漏洞分析

我对SonicWall的产品了解并不多，在搜索了相关的SSL-VPN设备后，我找到了Secure Remote
Access（SRA）。幸运的是，我们能够下载到该型号设备对应的试用版虚拟机，所有的分析都是在版本型号为8.1.0.7-22sv的设备上进行的，而且这貌似是非常旧的版本，因为我在网上没找到相关的更新版本。

首先，我们先来看看SSL-VPN的web接口，该接口包含很多CGI文件，而这些文件都存储在cgi-bin目录中。它们可以被远程调用，并且是只能运行在Linux平台中的32位ELF源文件。我们可以通过分析这些文件来了解目标设备处理身份认证的过程，并找到身份认证系统中可能存在的漏洞，或者弄清楚是否可以在不经过认证的情况下调用某些文件。

在这些文件中，我找到了一个名为supportLogin的程序，这个程序负责处理某些类型的身份认证。我从中找到了一些漏洞，而这些漏洞将允许攻击者在通过身份认证之前就可以利用这些漏洞来实施攻击，但需要设备启用“Virtual
Assist”模块。实话实说，我并不清楚这是否为常用的一个模块。

### 第一个漏洞-SQL注入漏洞

我找到的第一个漏洞是一个SQL注入漏洞，该漏洞存在于一个名叫customerTID的参数中。目标Web应用使用了一个SQLite数据库，并且使用了sqlite3中的printf函数，它会根据用户提供的输入数据来构造查询语句。在大多数情况下，应用后台会使用%q格式化符号来转义引号字符。但是在某些情况下服务端使用的却是%s。此时，将无法正常执行转义操作，因此导致了SQL注入漏洞的存在：

![](https://image.3001.net/images/20200215/1581753105_5e47a3118c438.png!small)

该问题将导致SQL盲注漏洞的存在，并且可以被攻击者远程利用。更重要的是，这个SQLite数据库中似乎在一个名叫Sessions的表中存储了身份认证用户的会话标识符，这也就意味着，攻击者可以通过其他方式入侵数据库并获取到各种级别的SSL-VPN访问权限。

> 这个SQL注入漏洞分配的CVE编号为：【[ _CVE-2019-7481_](https://cve.mitre.org/cgi-> bin/cvename.cgi?name=CVE-2019-7481)】

### 第二个漏洞-缓冲区溢出漏洞

在同一个CGI文件中，我找到了第二个漏洞，这个漏洞将允许攻击者在目标设备上实现任意代码执行。这是一个缓冲区溢出漏洞，存在于浏览器User-Agent信息的解析过程中。比如说，当攻击者将User-Agent设置为Safari时就会发生溢出，此时后台服务器将会调用libSys.so库中的getSafariVersion函数：

![](https://image.3001.net/images/20200215/1581753113_5e47a3191f8a3.png!small)

getSafariVersion函数部分代码如下：

![](https://image.3001.net/images/20200215/1581753117_5e47a31d971c7.png!small)

此时，攻击者可以利用memcpy函数来实现本地缓冲区溢出，SRA中并没有使用Stack
Canary技术，因此攻击者可以通过覆盖EIP或利用ROP链来执行任意命令。

攻击者可以构造如下请求来让CGI发生崩溃：

    
    
    GET /cgi-bin/supportLogin HTTP/1.1 
    Host: 10.1.0.100 
    User-Agent: plop Mac OS X Safari Version/12345678901234567890123456789012345678901234AAAABBBBCCCC lol Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8 Accept-Language: en-US,en;q=0.5 
    Accept-Encoding: gzip, deflate 

这个Handler将会自动重启，因此攻击者就可以多次重复利用该漏洞，并且执行类似爆破libc基地址之类的操作。在实际场景中，一般不超过100次尝试，攻击者就能在目标设备上利用nobody权限来执行任意命令了。

> 这个缓冲区溢出漏洞分配的CVE编号为：【[ _CVE-2019-7482_](https://cve.mitre.org/cgi-> bin/cvename.cgi?name=CVE-2019-7482)】

### 第三个漏洞-目录遍历漏洞

第三个漏洞是一个预身份认证目录遍历漏洞，可以用来判断某个文件是否存在。理论上说，如果目标文件遵循某种特定结构，那么攻击者就可以利用该漏洞来读取其中的部分内容。

> 这个漏洞分配的CVE编号为：【[ _CVE-2019-7483_](https://cve.mitre.org/cgi-> bin/cvename.cgi?name=CVE-2019-7483)】

重要的是，在实际场景中，攻击者可以利用该漏洞来判断目标设备是否存在前两个漏洞。

如果目标设备需要一定时间才能处理下列请求，则说明该设备存在漏洞：

    
    
    /cgi-bin/handleWAFRedirect?repeated=1&hdl=../etc/doesntexist

如果请求实际存在的文件，则处理时间会更短：

    
    
     /cgi-bin/handleWAFRedirect?repeated=1&hdl=../etc/passwd

### 其它漏洞

在分析过程中，我们还发现了另外三个漏洞，但是它们都需要拿到用户账号之后才可以被利用，它们分别是：

> CVE-2019-7484：SQL注入漏洞
>
> CVE-2019-7485：缓冲区溢出漏洞
>
> CVE-2019-7486：代码注入漏洞

前两个漏洞与本文之前所描述的漏洞非常相似，最后一个漏洞则是一个相对简单的命令注入漏洞，但需要管理员账户才能被利用，利用方式如下：

    
    
    POST /cgi-bin/viewcacert HTTP/1.1
    Host: 192.168.200.1
    [...]
    Content-Length: 67
    
    buttontype=delete&CERT=newcert-3'--'
    ping -c 4 192.168.200.123
    ls

## 漏洞上报

我于2019年6月5日将漏洞信息上报给了SonicWall团队，而SonicWall团队于2019年12月17日公布了相关的[
_安全公告_](https://psirt.global.sonicwall.com/vuln-list)。

 *** 参考来源：[ _scrt_](https://blog.scrt.ch/2020/02/11/sonicwall-sra-and-sma-vulnerabilties/)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

