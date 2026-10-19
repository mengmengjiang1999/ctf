## **前言**

当前，不少企业在安装AD域的同时安装ADCS证书服务器来管理证书，攻击者会针对ADCS进行攻击从而获取域控权限，导致AD集权安全收到威胁。

本系列前两篇文章，主要介绍了ADCS的基础架构，对证书模板错误配置攻击ESC1-8以及THEFT1-5进行了配置与分析。

[第一篇：ADCS知识点全收录！如何利用证书服务器对域控进行多角度攻击（上）](https://mp.weixin.qq.com/s?__biz=MzkxNTEzMTA0Mw==&mid=2247492128&idx=1&sn=844fef7bae678be996c07ac1ac48331a&chksm=c1617decf616f4fa8aa0588af751790108d539f8fe30ade30dfdb377c50bcbaad799c4bba354&scene=21#wechat_redirect)

[第二篇：ADCS知识点全收录！如何利用证书服务器对域控进行多角度攻击（中）](https://mp.weixin.qq.com/s?__biz=MzkxNTEzMTA0Mw==&mid=2247492198&idx=1&sn=a76945168a0f875685e3e0d8aad4596c&chksm=c1617daaf616f4bc0e7812ee5eb533ba786dd63c30c3f91cfbd0bd9e509263b4f36dd5987494&scene=21#wechat_redirect)

本文为第三篇，也是本系列最后一篇。我们将为大家分享账户持久化及域持久化相关内容。

## PERSIST1-通过证书窃取活跃用户凭据

如果存在企业CA，则用户可以请求任何可供其注册的模板的证书。在用户凭证被盗用的情况下，可以通过该身份凭据向已存在的证书模板申请一个可以进行AD身份验证的模板，具体模板需符合以下情况：

  * 证书模版允许公开注册
  * 允许域用户或者所属的组进行注册
  * 还得具有以下EKU：

    
    
    客户端认证          1.3.6.1.5.5.7.3.2
    PKINIT客户端认证    1.3.6.1.5.2.3.4
    智能卡登录       1.3.6.1.4.1.311.20.2.2
    任何目的            2.5.29.37.0
    子CA               (no EKUs)
    

  * 不需要证书管理员批准

默认情况下在所有的证书模版中，用户模板符合此项要求，某些情况下，用户模板可能会被禁止使用。

![image](https://image.3001.net/images/20230425/1682391879_6447434753e4775b82466.png!small)

Certify.exe find /clientauth 命令将通过LDAP查询符合上述条件的可用模板：

![image](https://image.3001.net/images/20230425/1682391911_644743675d4f9d683bf99.png!small)

如上所示，用户模板存在并符合标准。默认的用户模板发放的证书有效期为一年，证书管理员可能会修改到期时间来延长使用期限，并且如果攻击者使用此类的恶意模板注册证书，
**则只要证书还未失效则攻击者还可以利用此证书来进行身份验证，即使用户更改了此密码！**

在发现任何存在漏洞的模板时，需要特别关注“注册主体”。如“注册权限和协议”部分所述，对于已发布的模板，存在一种特殊的“证书注册”扩展权限，用于定义允许在证书中进行注册的主体。Certify的find命令将枚举这些主体，以及模板的ACL信息。攻击者只需要控制具有在模板中进行注册的权限的主体即可。

我们可以通过GUI界面或者certify来申请证书：

    
    
    Certify.exe request /ca:ADCS.lohack.com\lohack-ADCS-CA  /template:User
    

![image](https://image.3001.net/images/20230425/1682391956_64474394db450822b272c.png!small)

## PERSIST2-通过机器账户进行持久化

机器账户只是一种特殊类型用户账户。如果证书模板符合用户模板的要求，但是允许域计算机作为注册主体，则攻击者可以注册已被入侵系统的机器账户。默认的机器模板符合所有这些特征：

![image](https://image.3001.net/images/20230425/1682392003_644743c3242b1bf21153c.png!small)

如果攻击者在被入侵的系统上进行了权限提升，并且获取到了SYSTEM权限，则攻击者可以使用SYSTEM账户注册授予机器账户注册权限的证书模板。Certify在请求证书时使用其/machine参数实现此操作，使其自动提升为SYSTEM，然后注册证书模板：

申请证书：

    
    
    Certify.exe request /ca:ADCS.lohack.com\lohack-ADCS-CA  /template:Machine /machine
    

![image](https://image.3001.net/images/20230425/1682392036_644743e4f06271ec122a9.png!small)

通过访问机器账户证书，攻击者可以作为机器账户身份进行kerberos认证或者使用S4U2Self，攻击者也可以获取到主机上任何服务（例如，CIFS、HTTP、RPCSS等）的Kerberos服务票据，并冒充任何用户。Elad
Shamir的关于Kerberos委派攻击的精彩文章详细介绍了这种攻击场景。

最终，攻击者通过机器账户证书获得了一个持久化方法，其有效期与证书的有效期一样长（对于默认的机器模板，有效期为一年）。这种持久化机制在系统更改密码（默认为每30天）之后仍然有效，可以在系统被擦除之后继续存活（假设在擦除后使用相同的机器账户名称），并且不需要更改主机操作系统本身的任何内容！

## PERSIST3-通过证书更新的账户持久化

证书模板具有“有效期”和“续订期”（通常为6周）两个参数。有效期决定了颁发的证书可以被使用的时间，续订期则是在证书过期之前的一段时间窗口，在此期间，账户可以向颁发证书机构申请证书的更新。虽然对于自动申请证书的证书来说，这个过程是自动完成的，但普通账户也可以手动进行更新。

如果攻击者通过窃取或恶意申请方式获得了具有域身份验证功能的证书，那么在证书的有效期内，攻击者便可以利用该证书进行对AD的身份验证。攻击者还可以在证书过期之前对证书进行更新，从而延长其有效期，实现持久化攻击，并避免在证书颁发机构服务器上留下痕迹。这种攻击可以防止其他的票证申请被请求，从而使得攻击者能够持续访问AD，而且不留下其他痕迹。

## DPERSIST1-使用被盗的证书伪造证书

当一个组织安装ADCS时，默认情况下，AD启用基于证书的身份验证。要使用证书进行身份验证，CA必须颁发一个包含允许域身份验证的EKU
OID（例如客户端身份验证）的证书给账户。

当账户使用证书进行身份验证时，AD验证该证书是否链接到根CA和NTAuthCertificates(LDAP属性中CN=NTAuthCertificates,CN=Public
Key Services,CN=Services,CN=Configuration,DC=DOMAIN,DC=COM)对象指定的 CA 证书。

企业CA具有证书和相关私钥，这些证书和私钥存在于CA服务器本身上，下面几种特征可以确认CA证书：

  * 如前所述，证书存在于CA服务器本身上，并且其私钥由机器DPAPI保护。
  * 证书的颁发者（Issuer）和主题（Subject）都设置为CA的可分辨名称。
  * 只有CA证书具有“CA版本”扩展，而其他证书没有。
  * CA证书没有扩展用于密钥用途（EKU）。

通过确认CA证书，我们可以枚举当前主机所存储的证书文件。

CA使用私钥来签发证书。如果我们窃取了这个私钥，那么我们将可以实现伪造任何人在AD中进行认证。提取该证书私钥可通过在运行中输入certsrv.msc，然后右击证书办法机构，选择备份，并且备份的时候选择私钥也进行备份。

![image](https://image.3001.net/images/20230425/1682392125_6447443d6c9a466bbd1fc.png!small)

![image](https://image.3001.net/images/20230425/1682392136_6447444859ddd9068ab72.jpg!small)

除了通过CA备份之外，还有其他方法可以提取私钥。可以使用本文的“通过 DPAPI窃取用户证书-THEFT2”部分中提到的Mimikatz语法，或使用
SharpDPAPI 的命令 SharpDPAPI.exe certificates /machine（如之前所示）来完成此操作。

首先使用mimikatz获取CA证书私钥：首先使用crypto::capi 对本地的CryptoAPI 进行patch，然后进行证书与私钥的导出。

![image](https://image.3001.net/images/20230425/1682392163_64474463cbb8d5925bb0c.png!small)

然后伪造证书：  
/caname:证书颁发机构的主题名称（需要签署证书）  
/upn:指定的用户主体名称（UPN）（例如：user@lab.local）  
/pfx:保存最终证书的文件名（默认：无文件，存储在CERT_SYSTEM_STORE_CURRENT_USER中）

![image](https://image.3001.net/images/20230425/1682392188_6447447ca67f6810cd84b.png!small)

sharpDPAPI执行命令：

    
    
    SharpDPAPI.exe certificates /machine
    

可以获取到CA的私钥和证书文件，将证书和私钥文件用openssl生成CA.pfx文件。

![image](https://image.3001.net/images/20230425/1682392221_6447449d423337eb3b080.png!small)

拿到CA的PFX文件后，然后我们就可以通过私钥文件伪造一个证书，在伪造证书的时候，目标用户必须是激活或者是启用的，因此使用krbtgt账户是不可以的，通过工具certipy生成申请：

  * 首先申请一个正常用户的证书作为模版：

    
    
    certipy req -username test1@lohack.com -password xxxx -ca lohack-ADCS-CA -target ADSC.lohack.com -template User
    

![image](https://image.3001.net/images/20230425/1682392256_644744c01973c0a54a4d0.jpg!small)

  * 接着通过上面获取到的CA私钥为administrator 生成证书文件，并且以刚才创建的用户证书作为模版申请：

    
    
    certipy forge -ca-pfx CA.pfx  -upn administrator@lohack.com CN=Administrator,CN=Users,DC=LOHACK,DC=COM
    

![image](https://image.3001.net/images/20230425/1682392368_64474530c04efb58b7970.jpg!small)

  * 最后利用生成票据

    
    
    certipy auth -pfx administrator_forged.pfx -dc-ip 10.10.21.2
    

![image](https://image.3001.net/images/20230425/1682392316_644744fc9a3599149a701.jpg!small)  
我们从域控抓取一下administrator的hash，发现是一样的

![image](https://image.3001.net/images/20230425/1682392399_6447454fdc70acb7a3b05.jpg!small)

## DPERSIST2-信任恶意CA证书

在“Kerberos身份验证和NTAuthCertificates容器”部分中介绍了NTAuthCertificates对象。该对象在其cacertificate属性中定义一个或多个CA证书，而AD在身份验证过程中使用该对象。正如Microsoft所详细说明的那样，在身份验证期间，域控制器会检查NTAuthCertificates对象是否包含了发证机构字段中指定的CA的条目。如果存在，身份验证将继续进行。如果NTAuthCertificates对象中不存在该证书，则身份验证将失败。

攻击者可以采用另一种伪造路径，即生成自签名的CA证书并将其添加到NTAuthCertificates对象中。如果攻击者掌控NTAuthCertificates
AD对象（在默认配置中，只有企业管理员组成员以及域管理员或林根域管理员具有这些权限），则可以使用高级访问权限从任何系统中编辑NTAuthCertificates对象。使用certutil.exe
-dspublish -f C:\Temp\CERT.crt NTAuthCA或使用PKI Health
Tool来实现。指定的证书应该能够与先前详细介绍的ForgeCert伪造证书方法配合使用，以根据需要生成证书。

在测试过程中，还需要使用certutil.exe将证书添加到RootCA目录服务存储中，然后才能使伪造的证书在SChannel上工作。但是，无法使这些伪造的证书在PKINIT上工作。对于攻击者来说，通常更倾向于窃取现有的CA证书而不是安装额外的恶意CA证书。

## DPERSIST3-恶意错误配置

通过对ADCS组件的安全描述符进行修改，有许多权限维持的攻击手法。攻击者可以利用提升的权限实现“域内提取”部分中描述的任何场景，以及将“控制权限”（例如，WriteOwner/WriteDACL等）添加到敏感对象中。这包括：

1.CA服务器的 AD计算机对象。  
2.CA服务器的RPC/DCOM服务。  
3.AD 容器

    
    
    CN=Public Key Services,CN=Services,CN=Configuration,DC=<COMPANY>,DC=<COM>
    

中的任何子代 AD 对象或容器。例如Certificate Templates、Certificate
Authorities、NTAuthCertificates等。

4.AD组默认或当前组织授予了控制ADCS的权限。例如内置的Cert Publishers 组及其任何成员。

一个拥有域中提升权限的攻击者可以将WriteOwner权限添加到默认的User证书模板中，并将攻击者自己设置为权限的负责人。

为了在以后滥用此权限，攻击者首先会将User模板的所有权修改为自己，然后在模板上设置mspki-certificate-name-flag为1，以启用ENROLLEE_SUPPLIES_SUBJECT（即允许用户在请求中提供Subject Alternative
Name）。接下来，攻击者可以使用该模板进行注册，并指定一个域管理员名称作为备用名称，然后使用生成的证书作为DA进行身份验证。

