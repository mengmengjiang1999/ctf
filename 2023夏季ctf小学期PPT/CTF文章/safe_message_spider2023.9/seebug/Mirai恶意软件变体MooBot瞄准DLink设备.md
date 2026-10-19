**作者：Chao Lei, Zhibin Zhang, Cecilia Hu, Aveek Das  
译者：知道创宇404实验室翻译组  
原文链接：<https://unit42.paloaltonetworks.com/moobot-d-link-devices/>**

## 执行摘要

8月初，Unit 42研究人员发现攻击利用了D-Link（一家专门从事网络和连接产品的公司）制造的设备中的多个漏洞。被利用的漏洞包括：

  1. [CVE-2015-2051](https://nvd.nist.gov/vuln/detail/CVE-2015-2051): D-Link HNAP SOAPAction 标头命令执行漏洞
  2. [CVE-2018-6530](https://nvd.nist.gov/vuln/detail/CVE-2018-6530): D-Link SOAP 接口远程代码执行漏洞
  3. [CVE-2022-26258](https://nvd.nist.gov/vuln/detail/CVE-2022-26258): D-Link 远程命令执行漏洞
  4. [CVE-2022-28958](https://nvd.nist.gov/vuln/detail/CVE-2022-28958): D-Link 远程命令执行漏洞

![Conceptual image representing IoT security, including the MooBot attacks
targeting D-Link devices that are discussed
here.](https://images.seebug.org/content/images/2022/09/13/1663048355000-1bbeju.png-w331s)

如果设备遭到入侵，它们将完全由攻击者控制，攻击者可以利用这些设备进行进一步的攻击，例如分布式拒绝服务 (DDoS) 攻击。Unit
42研究人员捕获的攻击企图利用上述漏洞传播MooBot，这是一种Mirai变体，目标是运行Linux的暴露网络设备。

虽然D-Link已发布有关此处提及的所有漏洞的安全公告，但某些用户可能正在运行未修补或旧版本的设备。Unit 42强烈建议尽可能应用升级和补丁。

## 活动概述

整个攻击过程如图1所示：

![1. Attacker exploits vulnerable devices by leveraging CVE-2015-2051,
CVE-2018-6530, CVE-2022-26528 and CVE-2022-28958. 2. The downloader requests
MooBot binary from remote host. 3. Communication with C2 server. 4. The
compromised devices launches an attack on other devices based on C2 command.
](https://images.seebug.org/content/images/2022/09/13/1663048355000-2uxegv.png-w331s)
图 1. 活动概览

## 被利用的漏洞

此次攻击利用了四个已知的漏洞。成功利用后，`wget`实用程序将从恶意软件基础设施下载MooBot样本，然后执行下载的二进制文件。漏洞相关信息如表1所示。

**ID** | **漏洞** | **描述** | **严重性**  
---|---|---|---  
1 | CVE-2015-2051 | D-Link HNAP SOAPAction Header 命令执行漏洞 | CVSS 2.0 版：10.0 高危  
2 | CVE-2018-6530 | D-Link SOAP 接口远程代码执行漏洞 | CVSS 3.0 版：9.8 严重  
3 | CVE-2022-26258 | D-Link 远程命令执行漏洞 | CVSS 3.0 版：9.8 严重  
4 | CVE-2022-28958 | D-Link 远程命令执行漏洞 | CVSS 3.0 版：9.8 严重  
  
表1. 利用的漏洞列表

## D-Link 利用有效负载

攻击者利用四个可能导致远程代码执行的D-Link漏洞，从主机`159.203.15[.]179`（[ZoomEye
搜索结果](https://www.zoomeye.org/searchResult?q=159.203.15%5B.%5D179 "ZoomEye
搜索结果")）下载MooBot下载程序。

#### 1\. CVE-2015-2051：D-Link HNAP SOAPAction Header 命令执行漏洞

![CVE-2015-2051 exploit payload, showing the connection to host
159.203.15\[.\]179, from which a MooBot downloader can be accessed.
](https://images.seebug.org/content/images/2022/09/13/1663048355000-3xgdaw.png-w331s)
图2. CVE-2015-2051利用有效负载

针对较旧的D-Link路由器的攻击利用了HNAP SOAP接口中的漏洞。攻击者可以通过盲目的操作系统命令注入来执行代码。

#### 2\. CVE-2018-6530：D-Link SOAP 接口远程代码执行漏洞

![CVE-2018-6530 exploit payload, showing the connection to host
159.203.15\[.\]179, from which a MooBot downloader can be
accessed.](https://images.seebug.org/content/images/2022/09/13/1663048356000-4nhomy.png-w331s)
图3. CVE-2018-6530利用有效负载

该漏洞是由于较旧的D-Link路由器在向SOAP接口发出的请求中未经确认地使用了“服务”参数。可以利用该漏洞允许未经身份验证的远程代码执行。

#### 3\. CVE-2022-26258：D-Link 远程代码执行漏洞

![CVE-2022-26258 exploit payload, showing the connection to host
159.203.15\[.\]179, from which a MooBot downloader can be
accessed.](https://images.seebug.org/content/images/2022/09/13/1663048356000-5gjomc.png-w331s)
图4. CVE-2022-26258利用有效负载

该利用针对`/lan.asp`组件中的命令注入漏洞。该组件未成功清理HTTP参数`DeviceName`的值，这可能导致任意命令执行。

#### 4\. CVE-2022-28958：D-Link 远程代码执行漏洞

![CVE-2022-28958 exploit payload, showing the connection to host
159.203.15\[.\]179, from which a MooBot downloader can be
accessed.](https://images.seebug.org/content/images/2022/09/13/1663048356000-6yegos.png-w331s)
图5. CVE-2022-28958利用有效负载

该漏洞针对`/shareport.php`组件中的远程命令执行漏洞。该组件未成功清理HTTP参数`value`的值，这可能导致任意命令执行。

## 恶意软件分析

与此攻击相关的所有工件如下表所示：

**文件名** | **SHA256** | **描述**  
---|---|---  
rt | B7EE57A42C6A4545AC6D6C29E1075FA1628E1D09B8C1572C848A70112D4C90A1 |
脚本下载器。它将MooBot下载到受感染的系统上，并将二进制文件重命名为Realtek。  
wget[.]sh | 46BB6E2F80B6CB96FF7D0F78B3BDBC496B69EB7F22CE15EFCAA275F07CFAE075 |
脚本下载器。它将MooBot下载到受感染的系统上，并将二进制文件重命名为Android。  
arc | 36DCAF547C212B6228CA5A45A3F3A778271FBAF8E198EDE305D801BC98893D5A |
MooBot可执行文件。  
arm | 88B858B1411992509B0F2997877402D8BD9E378E4E21EFE024D61E25B29DAA08 |
MooBot可执行文件。  
arm5 | D7564C7E6F606EC3A04BE3AC63FDEF2FDE49D3014776C1FB527C3B2E3086EBAB |
MooBot可执行文件。  
arm6 | 72153E51EA461452263DBB8F658BDDC8FB82902E538C2F7146C8666192893258 |
MooBot可执行文件。  
arm7 | 7123B2DE979D85615C35FCA99FA40E0B5FBCA25F2C7654B083808653C9E4D616 |
MooBot可执行文件。  
i586 | CC3E92C52BBCF56CCFFB6F6E2942A676B3103F74397C46A21697B7D9C0448BE6 |
MooBot可执行文件。  
i686 | 188BCE5483A9BDC618E0EE9F3C961FF5356009572738AB703057857E8477A36B |
MooBot可执行文件。  
mips | 4567979788B37FBED6EEDA02B3C15FAFE3E0A226EE541D7A0027C31FF05578E2 |
MooBot可执行文件。  
mipsel | 06FC99956BD2AFCEEBBCD157C71908F8CE9DDC81A830CBE86A2A3F4FF79DA5F4 |
MooBot可执行文件。  
sh4 | 4BFF052C7FBF3F7AD025D7DBAB8BD985B6CAC79381EB3F8616BEF98FCB01D871 |
MooBot可执行文件。  
x86_64 | 4BFF052C7FBF3F7AD025D7DBAB8BD985B6CAC79381EB3F8616BEF98FCB01D871 |
MooBot可执行文件。  
  
表2. 攻击相关工件

Unit
42研究人员对下载的恶意软件样本进行了分析。基于其行为和模式，我们认为托管在`159.203.15[.]179`上的恶意软件样本与名为MooBot的Mirai僵尸网络的变体有关。

![The most obvious feature of MooBot is the executable file containing the
string w5q6he3dbrsgmclkiu4to18npavj702f, which will be used to generate random
alphanumeric strings as
shown.](https://images.seebug.org/content/images/2022/09/13/1663048356000-7cmlco.png-w331s)
图6. MooBot随机字符串生成器

MooBot最明显的特性是包含字符串`w5q6he3dbrsgmclkiu4to18npavj702f`的可执行文件，它将用于生成随机字母数字字符串。

执行时，二进制文件打印`get haxored!`到控制台，生成具有随机名称的进程并清除可执行文件。

![The screenshot shows examples of MooBot spawning processes with random
names.](https://images.seebug.org/content/images/2022/09/13/1663048356000-8yomni.png-w331s)
图7. MooBot创建流程

作为一个变体，MooBot继承了Mirai最重要的功能——具有嵌入式默认登录凭据和僵尸网络配置的数据部分——但MooBot没有使用Mirai的加密密钥`0xDEADBEEF`，而是使用`0x22`对其数据进行加密。

![Red arrows highlight the decode username and the decode
password](https://images.seebug.org/content/images/2022/09/13/1663048356000-9ivtrz.png-w331s)
图8. MooBot配置解码功能

在从配置中解码其C2服务器`vpn.komaru[.]today`后，MooBot将发送一条消息通知C2服务器有一个新的MooBot在线。消息以硬编码的魔法值`0x336699`开头。

在我们分析时，C2服务器处于离线状态。根据代码分析，MooBot还会向C2服务器发送心跳消息，并解析来自C2的命令，对特定IP地址和端口号发起DDoS攻击。

## 结论

上面提到的漏洞攻击复杂性低，但对安全造成严重影响，可能导致远程代码执行。一旦攻击者以这种方式获得控制权，他们就可以通过将新受感染的设备纳入到其僵尸网络中来进行进一步的攻击，例如DDoS。

因此，我们强烈建议尽可能应用补丁和升级。

Palo Alto Networks 客户通过以下产品和服务获得针对漏洞和恶意软件的保护：

  1. 具有威胁预防安全订阅的下一代防火墙可以通过威胁预防签名[38600](https://threatvault.paloaltonetworks.com/?query=38600), [92960](https://threatvault.paloaltonetworks.com/?query=92960), [92959](https://threatvault.paloaltonetworks.com/?query=92959)和[92533](https://threatvault.paloaltonetworks.com/?query=92533)来阻止具有最佳实践的攻击。

  2. [WildFire](https://www.paloaltonetworks.com/products/secure-the-network/wildfire)可以通过静态签名检测来阻止恶意软件。

  3. Palo Alto Networks IoT安全平台可以利用网络流量信息来识别设备的供应商、型号和固件版本，并识别易受上述CVE攻击的特定设备。

  4. [高级URL过滤](https://www.paloaltonetworks.com/network-security/advanced-url-filtering)和[DNS安全](https://www.paloaltonetworks.com/network-security/dns-security)能够阻止C2域和恶意软件托管URL。

  5. 此外，[IoT Security](https://www.paloaltonetworks.com/network-security/iot-security)具有内置的基于机器学习的异常检测功能，如果设备表现出非典型行为，例如突然出现来自新来源的流量、连接数量异常高或IoT应用有效载荷中通常出现的某些属性的无法解释的激增，则可以向客户发出警报。

## IOC

### 基础设施

#### MooBot C2

`vpn.komaru[.]today`

#### 恶意软件主机

http://159.203.15[.]179/wget.sh  
http://159.203.15[.]179/wget.sh3  
http://159.203.15[.]179/mips  
http://159.203.15[.]179/mipsel  
http://159.203.15[.]179/arm  
http://159.203.15[.]179/arm5  
http://159.203.15[.]179/arm6  
http://159.203.15[.]179/arm7  
http://159.203.15[.]179/sh4  
http://159.203.15[.]179/arc  
http://159.203.15[.]179/sparc  
http://159.203.15[.]179/x86_64  
http://159.203.15[.]179/i686  
http://159.203.15[.]179/i586

### 工件

#### Shell 脚本下载器

**文件名** | **SHA256**  
---|---  
rt | B7EE57A42C6A4545AC6D6C29E1075FA1628E1D09B8C1572C848A70112D4C90A1  
wget[.]sh | 46BB6E2F80B6CB96FF7D0F78B3BDBC496B69EB7F22CE15EFCAA275F07CFAE075  
  
表3. Shell脚本下载器

#### MooBot样本

**文件名** | **SHA256**  
---|---  
arc | 36DCAF547C212B6228CA5A45A3F3A778271FBAF8E198EDE305D801BC98893D5A  
arm | 88B858B1411992509B0F2997877402D8BD9E378E4E21EFE024D61E25B29DAA08  
arm5 | D7564C7E6F606EC3A04BE3AC63FDEF2FDE49D3014776C1FB527C3B2E3086EBAB  
arm6 | 72153E51EA461452263DBB8F658BDDC8FB82902E538C2F7146C8666192893258  
arm7 | 7123B2DE979D85615C35FCA99FA40E0B5FBCA25F2C7654B083808653C9E4D616  
i586 | CC3E92C52BBCF56CCFFB6F6E2942A676B3103F74397C46A21697B7D9C0448BE6  
i686 | 188BCE5483A9BDC618E0EE9F3C961FF5356009572738AB703057857E8477A36B  
mips | 4567979788B37FBED6EEDA02B3C15FAFE3E0A226EE541D7A0027C31FF05578E2  
mipsel | 06FC99956BD2AFCEEBBCD157C71908F8CE9DDC81A830CBE86A2A3F4FF79DA5F4  
sh4 | 4BFF052C7FBF3F7AD025D7DBAB8BD985B6CAC79381EB3F8616BEF98FCB01D871  
x86_64 | 3B12ABA8C92A15EF2A917F7C03A5216342E7D2626B025523C62308FC799B0737  
  
表4. MooBot样本

## 其他资源

[针对网络安全设备的新Mirai变体](https://unit42.paloaltonetworks.com/mirai-variant-iot-vulnerabilities/) \- Unit 42, Palo Alto Networks  
[网络攻击趋势：互联网威胁（2020年11月至2021年1月）](https://unit42.paloaltonetworks.com/network-attack-trends-winter-2020/) \- Unit 42, Palo Alto Networks

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1966/>

