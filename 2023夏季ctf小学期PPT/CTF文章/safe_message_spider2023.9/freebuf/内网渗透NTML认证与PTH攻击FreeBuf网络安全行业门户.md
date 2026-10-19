## 前言

这是内网系列的第五篇文章了，我们今天来看看内网中的另一种认证方式以及PTH攻击。在做内网渗透的时候，我们会接触到很多hash，如NTML hash，NTML
v1，NTML v2等等。那么这些hash到底都是什么？它们有什么样的作用？同时，那些hash可以用于hash传递攻击。这篇文章我们就来认识一下。

![1689396252_64b2241c8e52a16fd44bf.png!small?1689396251077](https://image.3001.net/images/20230715/1689396252_64b2241c8e52a16fd44bf.png!small?1689396251077)

关于内网前面的几篇文章如下，大家感兴趣的可以去看看：  

[内网渗透：Kerberos认证协议安全性分析](https://www.freebuf.com/articles/network/371028.html)

[内网横移：抓取域管理员密码](https://www.freebuf.com/articles/web/370338.html)

[内网渗透：详解kerberoast攻击](https://www.freebuf.com/articles/network/371446.html)

[内网渗透：详解Responder利用方式](https://www.freebuf.com/articles/network/371863.html)

另外，我在freebug的知识大陆建立了一个帮会，现在免费加入，会不断更新相关的文章，欢迎大家加入帮会，共同探讨。

帮会名称：安全防线

## win本地存储的hash

我们知道在win中是不会存储用户的明文密码的，用户的密码都以hash的形式存在，它会将用户的明文密码经过加密后存储在SAM数据库中。SAM文件的路径是%SystemRoot%\system32\config\sam。

在域环境下，域控制器中也存在这样的数据库AD (Account Database)，位于ntds.dit

![1689396275_64b224339942b63d2b8f9.png!small?1689396274216](https://image.3001.net/images/20230715/1689396275_64b224339942b63d2b8f9.png!small?1689396274216)

本地存储的哈希通常由两种， **分别为LM-Hash和NT-Hash，这是对同一个密码的两种不同的加密方式** 。

SAM文件中存储的hash结构通常为：username:RID:LM-HASH:NT-HASH

### LM hash

LM Hash是Windows使用的最古老的密码存储，其历史可追溯到1980年代的OS /
2，是微软为了提高Windows操作系统的安全性而采用的散列加密算法，其本质是DES加密。

由于允许的字符集有限，因此它们很容易破解。尽管LM Hash较容易被破解，但是为了保证系统的兼容性， **Windows只是将LM Hash禁用了**
(从Windows Vista和Windows Server 2008版本开始，Windows操作系统默认禁用LM
Hash)。如果仍然可用，则可以从Windows系统上的SAM数据库或域控制器上的NTDS数据库中获取它们。

 **LM hash是在LAN Manager 挑战/响应验证机制(LM)中使用。**

目前某些工具的参数需要填写固定格式LM hash:NT hash，可以将LM Hash填0(LM
hash可以为任意值)，即00000000000000000000000000000000:NT hash

 **生成原理**

1.将明文口令转换为其大写形式

2.将字符串大写后转换为16进制字符串

3.密码不足14字节要求用0补全

4.将上述编码分成2组7字节（56bits=7*8）的数据

5.将每一组7字节的十六进制转换为二进制，每7bit一组末尾加0，再转换成十六进制组成得到2组8字节的编码

6.将以上步骤得到的两组8字节编码，分别作为DES加密key为魔术字符串“KGS!@#$% ”进行加密

7.将 **两组DES加密后的编码拼接得到结果**

### NTLM hash

NTLMHash是微软为了在提高安全性的同时保证兼容性而设计的散列加者算法， **NTLMHash是基于MD4加密算法进行加密的**
。个人版从Windows Vista以后，服务器版从Wndows Sever2003以后，Windows 操作系统的认证方式均为NTLM Hash.

它的前身是LM Hash，两者相差不大，只是使用的加密算法不同。通常意义上的NT
Hash指存储在SAM数据库及NTDS数据库中对密码进行摘要计算后的结果，NT
Hash可以通过转储SAM数据库或使用Mimikatz来获得，可直接用于PtH，并且通常存在于lsass进程中，便于SSP使用

 **NTLM
hash广泛使用于WindowsNT挑战/响应验证机制(NTLM)，在kerberos协议中也可以看到它的身影。其长度为32位，由数字与字母组成**

 **生成过程**

1.明文转换为16进制ASCII码

2.将十六进制结果转为 Unicode格式

3.对所获取的 Unicode串进行标准MD4单向哈希，无论数据源有多少字节，MD4固定产生128-bit的哈希值

上面就是NTML hash的生成过程，可以通过下面的网站生成NTLM hash进行验证

<https://www.tobtu.com/lmntlm.php>

![1689396531_64b2253309ded138ce3dc.png!small?1689396529611](https://image.3001.net/images/20230715/1689396531_64b2253309ded138ce3dc.png!small?1689396529611)

  

## win本地认证（登录）

 **由于目前使用的hash大部分都是NTLM hash，因此下面以NTLM hash进行说明。**

在进行本地认证的过程中，用户登录时，系统将用户输入的明文密码加密成NTLM Hash，与SAM数据库中的NTLM Hash进行比较，从而实现认证。

winlogon.exe -> 接收用户输入 -> lsass.exe -> (认证)

 **用户注销、重启、锁屏后，操作系统会让winlogon显示登录界面，也就是输入框，接收输入后，输入框将密码交给lsass进程，
这个进程中会存一份明文密码，将明文密码加密成NTLM Hash，对比SAM数据库中的hash进行验证。**

 **问题：win本地不会保存密码，那么我们通过 mimikatz等工具抓取到的明文密码是从那里抓取的？**

其实上面的介绍已经说了，我们将明文密码输入以后会交给lsass进程，这个进程会在内存中保留明文密码，因此我们是从lsass进程抓取到的明文密码。

PS：微软为了防止明文密码泄露发布了补丁KB2871997，关闭了Wdigest功能。
**当系统为win10或2012R2以上时，默认在内存缓存中禁止保存明文密码。因此我们现在通过工具都不能抓取到明文密码了** 。

![1689396625_64b2259158c1e003f1e8b.png!small?1689396623820](https://image.3001.net/images/20230715/1689396625_64b2259158c1e003f1e8b.png!small?1689396623820)

  

## NTML网络认证协议

NTLM是除Kerberos之外的一种网络认证协议，只支持Windows。它是一种基于质询/应答
(Challenge/Response)消息交换模式的认证机制， 常用于工作组和域环境下登录场景的身份认证。

### NTML的认证方式

 **交互式认证** ：使用域账号登录到客户端；涉及两部分（客户端、域控）

 **非交互式认证** ：在已经登陆 的客户端上使用 SSO的方式访问一台服务器；涉及三部分（客户端、域控、服务器）

    
    
    # 非交互式场景 
    net use Z: \\10.0.1.102\vefs "password" /user:domain\xiaoming # or net use Z: \\10.0.1.102\vefs "password" /user:xiaoming

### 域和工作组

先来看看工作组和域有什么不同

工作组和域宏观上都是一群计算机的集合，域中计算机的数量规模通常大于工作组内的计算机。

工作组内的机器名义上虽然是属于一个集合，但是内部各计算机还是各自管理各自的，没有一个相对成熟的信任机制，工作组内各个计算机的关系依旧是点对点。因此，在工作组环境下进行访问认证，仅涉及Client和Server。我们使用的个人计算机，默

