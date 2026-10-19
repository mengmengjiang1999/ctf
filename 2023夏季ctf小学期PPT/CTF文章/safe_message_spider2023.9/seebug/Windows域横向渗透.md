来源链接：Mottoin http://www.mottoin.com/89413.html

### 环境拓扑

我们的目的是获取redhook.DA域的一个可用的账户，当前攻击者已在公司网络内，但并未在同一个子网。

![1](http://img.mottoin.com/wp-content/uploads/2016/09/1-34.png)

### Compromising Client 1

假设我们已经获取到了Client1的登陆凭据，如果网络足够大，你可以发现存储在某处网络共享上面的其他凭据（通过批量的脚本：vbs,ps1,.net等等）。关于怎么访问网络，你可以使用Cobalt
Strike框架。

我们可以这样做：

![2](http://img.mottoin.com/wp-content/uploads/2016/09/2-33.png)

我们可以通过批量的脚本快速的获得NETBIOS的信息。

![3](http://img.mottoin.com/wp-content/uploads/2016/09/3-29.png)

在win上，可以用命令nbtstat -A IP获得相同的信息，可以看到机器名是WIN7-ENT-CLI1，属于REDHOOK域。

#### PsExec:

使用msf的psexec可以很容易的获取到一个shell。BOB是一个本地用户，不用指定SMBDomain参数。

![4](http://img.mottoin.com/wp-content/uploads/2016/09/4-23.png)

我们也可以使用Impacket’s PsExec，但psexec的好处是可以传递hash。

![5](http://img.mottoin.com/wp-content/uploads/2016/09/5-23.png)

不要忘了微软自己的PSEXEC有额外的好处，添加一个-s参数会给你一个system的shell。

![6](http://img.mottoin.com/wp-content/uploads/2016/09/6-21.png)

#### WMI

一些WMI的选项也可以让你远程系统上执行命令。最值得注意的是WMIC，不仅可以在远程系统上执行命令，还可以通过内置的命令获取系统的敏感信息和配置操作系统。

![7](http://img.mottoin.com/wp-content/uploads/2016/09/7-18.png)

最好使用cmd.exe /c或powershell -exec bypass -command。

我们使用Impacket WmiExec可以获取到一个半交互式的shell，执行命令并获取输出。

![8](http://img.mottoin.com/wp-content/uploads/2016/09/8-17.png)

最后使用PowerSploit的Invoke-WmiCommand命令。

![9](http://img.mottoin.com/wp-content/uploads/2016/09/9-17.png)

#### Pass-The-Hash, WCE & Mimikatz:

有时候你只能获取到NTLM的hash值，可以使用msf的psexec或WCE或Mimikatz。

![10](http://img.mottoin.com/wp-content/uploads/2016/09/10-17.png)

缺点是WCE可能会被发现，而mimikatz是直接加载内存。

![11](http://img.mottoin.com/wp-content/uploads/2016/09/11-16.png)

### Smash-And-Grab

#### Metasploit (Mimikatz & hashdump):

![dom-10](http://img.mottoin.com/wp-content/uploads/2016/09/Dom-10.png)

#### Secretsdump & Invoke-Mimikatz:

也可以使用Impacket’s SecretsDump和Powersploit’s Invoke-Mimikatz来获取。mimikatz的脚本托管在攻击者的服务器上。

![dom-11](http://img.mottoin.com/wp-content/uploads/2016/09/Dom-11.png)

可能还有其他技术，但是以上是最经典的。

#### Impersonation:

现在我们有了redhook域里的一台机器并且能连接到不同的子网中，现在开始做一个信息收集。

要查询域的信息，需要有一个域用户，当前的bob用户并不是域用户或system权限，但是我们可以通过

NtQuerySystemInformation来发现其他用户的token，进而模拟他们登陆。

meterpreter有这个插件，使这个过程非常简单。

![dom-14](http://img.mottoin.com/wp-content/uploads/2016/09/Dom-14.png)

也可以使用incognito（下载地址：https://labs.mwrinfosecurity.com/blog/2012/07/18/incognito-v2-0-released/）

![dom-15](http://img.mottoin.com/wp-content/uploads/2016/09/Dom-15.png)

### Reconnaissance

#### 域侦察：

现在我们有了一个域用户，我们需要尽快扩大战果。

![16](http://img.mottoin.com/wp-content/uploads/2016/09/16-11.png)

以上命令分别是：

  1. 获取当前用户
  2. 获取当前机器名
  3. 获取IP信息
  4. 获取域内共享资源列表
  5. 返回验证当前登录会话的域控制器的名称
  6. 获取域控地址
  7. 查看本机所有用户
  8. 查看域用户
  9. 查看所有本地管理员组的用户
  10. 列出域内活跃的机器和会话
  11. 获取从域控上的连接源
  12. 获取本地管理员的信息
  13. 获取域管理员的信息

通过简单的信息收集，我们能了解到让我们自己成为域管理员的途径。

  1. TemplateAdmin 是client1和client2的管理员
  2. 虽然我们没有明文，但是我们有TemplateAdmi的hash来访问client2
  3. REDHOOK\ Administrator认证在client2，如果搞定client2，即可获得域控

#### Socks Proxy:

最后一个事就是添加路由，让我们通过代理能访问系统，如果使用msf或cobalt strike那么就非常简单。

![dom-16](http://img.mottoin.com/wp-content/uploads/2016/09/Dom-16.png)

使用session1 通过socks4a来进行进一步的扫描。

![dom-17](http://img.mottoin.com/wp-content/uploads/2016/09/Dom-17.png)

使用proxychains。

![dom-18](http://img.mottoin.com/wp-content/uploads/2016/09/Dom-18.png)

### Compromising Client 2

#### Metasploit (PortProxy & PsExec):

共享的本地管理员账户，客户端1和客户端2的TemplateAdmin是通用的账号，密码也一样。 我们可以使用portproxy从client1进行端口转发。

![dom-19](http://img.mottoin.com/wp-content/uploads/2016/09/Dom-19.png)

client1监听10.1.1.2:9988向10.0.0.128:9988发送流量。再配置psexec。

![dom-20](http://img.mottoin.com/wp-content/uploads/2016/09/Dom-20.png)

### Impacket (PsExec) & netsh:

在client1上使用netsh手动设置转发规则。

![dom-21](http://img.mottoin.com/wp-content/uploads/2016/09/Dom-21.png)

现在有个规则是把流量从10.0.0.129:5678转发到10.1.1.3:445，Impacket’s PsExec需要一个自定义端口，编辑源码来实现。

![dom-22](http://img.mottoin.com/wp-content/uploads/2016/09/Dom-22.png)

![dom-23](http://img.mottoin.com/wp-content/uploads/2016/09/Dom-23.png)

当完成转发之后，记得清理规则。

    
    
    C:\Windows\system32> netsh interface portproxy reset

如果我们获取不到明文密码，我们仍然可以冒充域管理员的令牌。

### Smash-And-Grab ²

#### Metasploit Easy-Mode (Mimikatz & hashdump & incognito):

![dom-24](http://img.mottoin.com/wp-content/uploads/2016/09/Dom-24.png)

![dom-25](http://img.mottoin.com/wp-content/uploads/2016/09/Dom-25.png)

#### Impacket (PsExec) & incognito:

我们使用incognito来执行远程命令。

![dom-26](http://img.mottoin.com/wp-content/uploads/2016/09/Dom-26.png)

![dom-27](http://img.mottoin.com/wp-content/uploads/2016/09/Dom-27.png)

#### 文件传输

接下来我们就很容易来拖拽文件了。

![28](http://img.mottoin.com/wp-content/uploads/2016/09/28-1.png)

### Compromising Redrum-DC

#### Socks Proxy & Impacket (WmiExec):

我们要么获取域管理员的密码，要么我们自己新建一个域管理员。

还记得之前用户socks代理么，我们可以使用它来访问域内几乎所有东西。

![dom-28](http://img.mottoin.com/wp-content/uploads/2016/09/Dom-28.png)

#### Sysinternals (PsExec) & Invoke-Mimikatz:

![dom-29](http://img.mottoin.com/wp-content/uploads/2016/09/Dom-29.png)

win2k12增强了hash的保护性，所以我们这样来获取hash值。

![dom-30](http://img.mottoin.com/wp-content/uploads/2016/09/Dom-30.png)

### 提取NTDS

很多时候提取了NTDS 说明渗透要结束了，下面我介绍一下访问本地shell或通过wmi来执行命令的方法。

#### Volume Shadow Copy (Classic-Mode):

![31](http://img.mottoin.com/wp-content/uploads/2016/09/31-1.png)

把文件拖到攻击者的机器里面有很多方法，我介绍一种，可以简单的使用Impacket’s SecretsDump本地解压传输内容。

![dom-31](http://img.mottoin.com/wp-content/uploads/2016/09/Dom-31.png)

注意下NTDS可能会包含很多用户，甚至上千，是非常大的，导出的时候要小心。

#### Socks Proxy & Impacket (SecretsDump) (Easy-Mode):

如果我们有socks代理，则很容易的使用明文密码来执行SecretsDump 。

![dom-32](http://img.mottoin.com/wp-content/uploads/2016/09/Dom-32.png)

### 资源

  * Active Directory Security ([@PyroTek3](https://twitter.com/PyroTek3)) – [here](https://adsecurity.org/)
  * harmj0y ([@harmj0y](https://twitter.com/harmj0y)) – [here](http://www.harmj0y.net/blog/)
  * Exploit-Monday ([@mattifestation](https://twitter.com/mattifestation)) – [here](http://www.exploit-monday.com/)
  * PowerView – [here](https://github.com/PowerShellMafia/PowerSploit/tree/master/Recon)
  * PowerSploit – [here](https://github.com/PowerShellMafia/PowerSploit)
  * Impacket – [here](https://github.com/CoreSecurity/impacket)
  * Impacket compiled by maaaaz – [here](https://github.com/maaaaz/impacket-examples-windows)
  * Mimikatz – [here](http://blog.gentilkiwi.com/mimikatz)
  * Incognito – [here](https://labs.mwrinfosecurity.com/blog/2012/07/18/incognito-v2-0-released/)
  * Windows Credentials Editor – [here](http://www.ampliasecurity.com/research/wcefaq.html)
  * Sysinternals Suite – [here](https://technet.microsoft.com/en-us/sysinternals/bb842062.aspx)

*原文：[fuzzysecurity](http://www.fuzzysecurity.com/tutorials/25.html) Mottoin翻译发布

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/49/>

