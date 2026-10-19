****

[](https://youtu.be/ug5ZuezbD3c)

****

**早在2013年9月，蜘蛛实验室（ Spider
Labs）就发表过一篇题为“SpiderLabs在你内网中获取域管的五大方式”的文章。这篇文章是我继该文的，应该说是非官方的“Part 2”部分。**

##  **1.Netbios和LLMNR Name Poisoning（中毒攻击）**

虽说如今Netbios/LLMNR并不像2013年那么盛行，但在测试中绝大多数人都能通过此类攻击，获取NTLMv1和NTLMv2哈希值并对对其进行破解利用。你可以借助像[hate_crack](https://github.com/trustedsec/hate_crack)这样的高级框架，来帮助你完成对哈希值的破解任务。

我个人通常使用的都是一些通用的字典列表，例如"
[uniqpass](https://webcache.googleusercontent.com/search?q=cache:BV8AEB0cWtcJ:https://dazzlepod.com/uniqpass/+&cd=1&hl=en&ct=clnk&gl=us)"以及常用hashcat规则集“base64”。但并不是所有密码都能被破解的，对于一些强制性的复杂密码类型，我们往往别无选择。

Responder可以说是与mitm中毒和欺骗攻击相关首选工具。目前该项目仍然由Laurent Gaffie维护。

[Inveigh](https://github.com/Kevin-Robertson/Inveigh)是一款Windows
PowerShell的LLMNR/NBNS协议欺骗/中间人工具。

它的核心是一个.NET数据包嗅探器，它侦听并响应LLMNR/mDNS/NBNS请求，同时还会通过Windows
SMB服务捕获传入的NTLMv1/NTLMv2身份验证尝试。

##  **2.中继攻击**

较新的MultiRelay工具目前是由Laurent Gaffie维护的。

但我个人更喜欢impacket的工具，用于中继和其他渗透测试需求。我发现Impacket的工具，在大多数unix上以及在Mac
OS本地运行都非常的可靠和稳定。与其他免费的开源工具相比，这些工具在主机上执行时会留下的痕迹也相对小很多（如果你考虑这方面的问题，那么无疑这是一个最佳的选择）。你可以安装[impacket，](https://github.com/CoreSecurity/impacket)为你的测试做准备。

 **SMB中继解释：**

### [
**smbrelayx.py**](https://github.com/CoreSecurity/impacket/blob/impacket_0_9_15/examples/smbrelayx.py)

在SMBRelay攻击中，攻击者要以中间人攻击方式来实施。攻击者等待某人来验证在他网络上的目标服务器。这样一来可以利用漏洞扫描器+管理员自动验证主机脚本。当自动化进程连接到攻击者，他通过他的目标(网络上的其他系统，也许是服务器)进行身份验证。目标会产生challenge，并将其发送给攻击者。攻击者发送challenge回到原始扫描系统。扫描系统拥有哈希值的加密功能正确密码的哈希值会将其发送给攻击者。攻击者传递正确的加密的响应返回给他的目标，并成功验证。

阻止这种攻击的唯一方法是强制执行服务器SPN检查禁用SMB端口。当然了，你也可以选择禁用SMB的数据输出端口：137，138，129和445，使用一些主机签名和数据包签名，或启用一些额外的保护措施。

 **NTLM中继解释：**

### [
**ntlmrelayx.py**](https://github.com/CoreSecurity/impacket/blob/master/examples/ntlmrelayx.py)

用户请求访问。用户尝试通过提供用户凭据登录到客户端。登录前，客户端计算机缓存密码的哈希值并放弃密码。客户端向服务器发送一个请求，该请求包括用户名以及纯文本格式的请求。服务器发送质询消息。服务器生成一个称为质询的
16 字节随机数（即
NONCE），并将它发送到客户端。客户端发送应答消息。客户端使用由用户的密码生成的一个密码哈希值来加密服务器发送的质询。它以应答的形式将这个加密的质询发回到服务器。服务器将质询和应答发送到域控制器。服务器将用户名、原始质询以及应答从客户端计算机发送到域控制器。域控制器比较质询和应答以对用户进行身份验证。域控制器获取该用户的密码哈希值，然后使用该哈希值对原始质询进行加密。接下来，域控制器将加密的质询与客户端计算机的应答进行比较。如果匹配，域控制器则发送该用户已经过身份验证的服务器确认。服务器向客户端发送应答。假定凭据有效，服务器授予对所请求的服务或资源的客户端访问权。

NTLM身份验证是一个复杂的协议，这里<http://davenport.sourceforge.net/ntlm.html>提供了非常详细的说明。

![1_MeIC7wR1YNcKcDwBIyPCkg.png](https://image.3001.net/images/20180315/15210839909170.png!small)  

SMBRelay和较新的攻击都利用了SMB签名，并允许特权用户通过SMB/NTLM身份验证机制进行身份验证。

> 需要注意的是，在不同网络上的Windows主机列表包含的目标很重要。我有一个很好的技巧就是以随机方式创建非签名主机的目标列表
>
> 下面的主机，使我能更快的获取域管允许域用户本地管理员访问SQL服务器，该服务器与域控制器共享相同的本地管理员密码

 **默认情况下，如果不指定要执行的二进制文件，ntlmrealyx将运行secretsdumps。**

 **![2_pOO-cX5cNUfEn1o32-SFPA.png](https://image.3001.net/images/20180315/15210840119508.png!small)  
**

成功执行NTLM中继后，你会在执行ntmrelayx的目录中找到名为“IP_samhashes”的哈希文件。

拿到哈希后，我使用impacket的wmiexec.py脚本，利用[pass-the-hash](https://www.sans.org/reading-room/whitepapers/testing/pass-the-hash-attacks-tools-mitigation-33283)技术最终获得了DA

![3_dukE-2XCk_6I9FGb98sfmQ.png](https://image.3001.net/images/20180315/15210840376555.png!small)  

![4_vnEng8O4sGJ1DENY2SmiqA.png](https://image.3001.net/images/20180315/15210840543703.png!small)  

在上面的场景中，我能够将凭据从一个网络中继到另一个网络，并检索可以通过wmiexec.py传递的管理员散列。并且可以让我在不破解哈希的情况下，直接获取域管理员权限。

##  **3.**[ **MS17-010**](https://github.com/SecWiki/windows-kernel-exploits/blob/master/MS17-010/ms17_010_eternalblue.rb)

[ **nmap -Pn -p445 - open - max-hostgroup 3 - smb-vuln-ms17-010 script
<ip_netblock>**](https://isc.sans.edu/forums/diary/Using+nmap+to+scan+for+MS17010+CVE20170143+EternalBlue/22574/)

ETERNALBLUE，ETERNALCHAMPION，ETERNALROMANCE和ETERNALSYNERGY是2017年4月14日Shadow
Brokers泄露出的四个NSA威胁漏洞。WannaCry/WannaCrypt是一个利用ETERNALBLUE漏洞进行传播的“蠕虫式”[勒索病毒](https://baike.baidu.com/item/%E5%8B%92%E7%B4%A2%E7%97%85%E6%AF%92)软件，EternalRocks比比勒索病毒WannaCry更隐蔽危害也更大，WannaCry只利用了2个漏洞，而EternalRocks则利用了7个漏洞。Petya也是一个勒索病毒程序，首先它会利用Microsoft
Office中的CVE-2017-0199漏洞，然后通过ETERNALBLUE进行传播。

![5_Nh7ufmdlWuyz1A6uOQvgSg.png](https://image.3001.net/images/20180315/15210840765099.png!small)  

## 4.[ **Kerberoasting**](https://www.blackhillsinfosec.com/a-toast-to-kerberoast/)

我曾多次成功在Active Directory域环境中，使用被称之为Kerberoasting的攻击来提升权限。[Tim
Medin](https://twitter.com/TimMedin)在[SANS Hackfest
2014](https://files.sans.org/summit/hackfest2014/PDFs/Kicking%20the%20Guard%20Dog%20of%20Hades%20-%20Attacking%20Microsoft%20Kerberos%20-%20Tim%20Medin%281%29.pdf)上展示了这种技术，从那以后也出现了许多与该技术细节相关的精彩文章和会议讲座。

Microsoft的Kerberos实现可能有点复杂，其主要利用了旧版Windows客户端的传统Active
Directory支持，以及使用的加密类型和用于加密和签署Kerberos票据的key
material。实质上，当域帐户被配置为在环境中运行服务时（例如MSSQL），服务主体名称（SPN）在域中被使用将服务与登录帐户相关联。当用户想要使用特定资源时，他们会收到一个当前运行该服务帐户的NTLM哈希和签名的Kerberos票据。

下面的例子来自[mubix的网站：](https://room362.com/post/2016/kerberoast-pt1/)

    
    
    root@wpad:~/impacket/examples# ./GetUserSPNs.py -dc-ip 192.168.168.10 sittingduck.info/notanadmin
    Impacket v0.9.15-dev - Copyright 2002-2016 Core Security Technologies
    
    Password:
    ServicePrincipalName                Name        MemberOf                                          PasswordLastSet
    ----------------------------------  ----------  ------------------------------------------------  -------------------    http/win10.sittingduck.info         uberuser    CN=Domain Admins,CN=Users,DC=sittingduck,DC=info  2015-11-10 23:47:21
    MSSQLSvc/WIN2K8R2.sittingduck.info  sqladmin01                                                    2016-05-13 19:13:20

##  **5.** **mitm6**

Mitm6是一个非常强大的工具，用于在典型的Windows广播网络上获取和提升权限。当其他攻击都失败时，你可以尝试smbrelay +
mitm6或ntlmreayx攻击。总之请发挥你的想象力，你将收获意想不到的惊喜！

![6_puHYIgmUcLKQerVLjPTJeg.png](https://image.3001.net/images/20180315/15210841051886.png!small)  

**与ntlmrelayx的用法：**

mitm6与ntlmrelayx应该说是最好的拍档。在这种情况下，目标DNS会被欺骗，导致受害者以HTTP和SMB的连接方式连接到ntlmrelayx。为了确保ntlmrelayx在IPv4和IPv6上侦听，我们可以使用-6参数。要获取WPAD的凭据，我们需要在命令提示符中-wh参数后添加主机，并指定WPAD文件所在的主机（因为DNS服务器是mitm6，所以本地域中的任何不存在的主机名都可以使用）。

mitm6是一个可以利用默认Windows配置，接管默认DNS服务器的渗透测试工具。首先让mitm6开始在攻击者机器的主接口上侦听，并通过DHCPv6向Windows客户端请求IPv6配置。mitm6将会应答这些DHCPv6请求，并为受害者分配本地链路范围内的IPv6地址。而在实际的IPv6网络中，这些地址由主机本身自动分配，不需要由DHCP服务器来配置，这使得我们有机会将攻击者IP设置为受害者的默认IPv6
DNS服务器，并将受害者流量重定向到攻击者机器而不是合法服务器。有关攻击的完整说明，请参阅我们关于 [mitm6](https://blog.fox-it.com/2018/01/11/mitm6-compromising-ipv4-networks-via-ipv6/)的博文。

 **相关参考：**

> <https://github.com/lgandx/Responder>
>
> <https://github.com/Kevin-Robertson/Inveigh>
>
> <https://github.com/purpleteam/snarf>
>
> <https://github.com/fox-it/mitm6>
>
> <https://www.fox-it.com/en/insights/blogs/blog/inside-windows-network/>
>
> <https://github.com/SecWiki/windows-kernel-> exploits/blob/master/MS17-010/ms17_010_eternalblue.rb>
>
> <https://room362.com/post/2016/kerberoast-pt1/>
>
>
> <https://isc.sans.edu/forums/diary/Using+nmap+to+scan+for+MS17010+CVE20170143+EternalBlue/22574>
>
> <https://www.blackhillsinfosec.com/a-toast-to-kerberoast/>
>
> <https://1337red.wordpress.com/using-a-scf-file-to-gather-hashes/>

***参考来源：[medium](https://medium.com/@adam.toscher/top-five-ways-i-got-domain-admin-on-your-internal-network-before-lunch-2018-edition-82259ab73aaa)，FB小编
secist 编译，转载请注明来自FreeBuf.COM**

