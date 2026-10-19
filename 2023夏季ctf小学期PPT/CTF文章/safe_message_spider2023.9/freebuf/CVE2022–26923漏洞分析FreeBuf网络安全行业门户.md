## **漏洞简介**

2022年5月10日，微软发布补丁修复了一个
AD域权限提升漏洞（CVE-2022–26923）。该漏洞是由于在申请证书时对AD域中的计算机账户身份审核不够严格，经过身份验证的攻击者可以操纵他们拥有或管理的计算机帐户的属性，假冒DC从AD
CS 服务器获取DC证书，最终导致普通权限用户提升至域管理员权限。这一漏洞最早由安全研究员Oliver
Lyak在2021年12月14日报告给微软，微软在2022年5月的安全更新中对其进行了修补。

##  **01** AD CS身份识别

默认情况下，CA允许域用户注册User模板证书，允许域计算机注册Machine模板证书。两个证书模板都允许客户端身份验证。这意味着颁发的证书可用于通过PKINIT
Kerberos 扩展对KDC进行身份验证。

通过对比User和DomainController两个模板的msPKI-Certificate-Name-Flag属性可以看到User模版包含SUBJECT_ALT_REQUIRE_UPN，DomainController包含
SUBJECT_ALT_REQUIRE_DNS。这两个字段分别标识证书中的用户和计算机的身份，用于CA识别证书的所有者。

如当我们使用User模板请求证书时，用户帐户的UPN将嵌入到证书中。在进行进行身份验证时，KDC会尝试将 UPN 从证书映射到用户。

![1654762869_62a1ad75c14ed039fee78.png!small?1654762870090](https://image.3001.net/images/20220609/1654762869_62a1ad75c14ed039fee78.png!small?1654762870090)

尝试修改用户的UPN属性，如果能够将该属性修改为AD管理员账号的UPN，则可以实现欺骗AD
CS获取AD管理员权限证书，但是实际上DC会对UPN检查保持全林唯一。

![1654762987_62a1adeb1124bdd2994d9.png!small?1654762987426](https://image.3001.net/images/20220609/1654762987_62a1adeb1124bdd2994d9.png!small?1654762987426)

虽然UPN无法假冒，但是不代表dnsHostName不可以假冒。在MS-ADTS（3.1.1.5.1.3
唯一性约束）文档中并没有标识dnsHostName属性具有唯一性。实际上，通过下面的漏洞分析也可以发现实际这个属性可以重复，这也是这个漏洞产生的主要原因。

##  **02** 漏洞分析复现

成功利用该漏洞需要满足以下几个必要条件：

1、攻击者获取到一个通过认证的普通域用户凭据或计算机账户凭据

2、AD 域内已配置了 AD CS 服务

3、Machine模板证书可以自动申请

首先第一步需要获得一个已知凭据的计算机账户，如果没有可以使用普通账户通过Impacket创建一个新的计算机账户。

![1654763011_62a1ae03e89d9269f0f3e.png!small?1654763012649](https://image.3001.net/images/20220609/1654763011_62a1ae03e89d9269f0f3e.png!small?1654763012649)

默认情况下每个普通用户都拥有添加10个机器账户的权限，添加机器权限可以通过编辑组策略控制，在Windows Server
2012以下版本的DC可以通过用户的属性 MS-DS-Machine-Account-Quota设置可添加计算机账户的数量。

![1654763019_62a1ae0bc9c26c12aaca0.png!small?1654763024668](https://image.3001.net/images/20220609/1654763019_62a1ae0bc9c26c12aaca0.png!small?1654763024668)

尝试直接修改机器的dnsHostName，提示出现操作错误（无法更新属性值），但是没有提示唯一性错误，因此可以猜测该值可以修改为DC的dnsHostName，但是出于某种限制，如值的类型不对或者是有某种对象的值依赖于该值导致无法成功更新修改到AD。

![1654763033_62a1ae199a235daf62efc.png!small?1654763033960](https://image.3001.net/images/20220609/1654763033_62a1ae199a235daf62efc.png!small?1654763033960)

观察使用账户test3创建的主机，发现其ACL信息非常有意思。虽然是test3创建的计算机账户，但是机器账户的所有者却是Domain
Admins账户。机器账户的中几条ACL信息非常有价值，分别是：

1.已验证的到DNS主机名的写入

2.已验证的到服务主体名的写入

3.已验证的到计算机属性的写入

这证明创建计算机账户的用户账户是有计算机账户的dnsHostName、servicePrincipalName和其他属性的写权限，因此修改dnsHostName属性值在ACL权限上是可行的。

![1654763057_62a1ae3146d4c30eb27e5.png!small?1654763058789](https://image.3001.net/images/20220609/1654763057_62a1ae3146d4c30eb27e5.png!small?1654763058789)

通过普通域用户对其创建主机的dnsHostName进行修改，将值修改为一个不存在的主机名发现成功，因此实现本漏洞的关键是如何绕过限制进行修改。

![1654763070_62a1ae3e18a11b9162757.png!small?1654763070515](https://image.3001.net/images/20220609/1654763070_62a1ae3e18a11b9162757.png!small?1654763070515)

在将dnsHostName从mc7.moin.com修改为xxx.moin.com时，发现该计算机账户的servicePricipalName属性也发生了变化，其中的两个字段包含了新的dnsHostName。可以推测这个属性对dnsHost
Name有依赖。

![1654763088_62a1ae508ff6e9f259ec8.png!small?1654763088767](https://image.3001.net/images/20220609/1654763088_62a1ae508ff6e9f259ec8.png!small?1654763088767)

查看微软的官方文档https://docs.microsoft.com/en-us/windows/win32/adschema/r-validated-spn，发现官方对servicePrincipalName属性的描述为“验证写入权限以启用符合计算机 DNS 主机名的 SPN
属性设置”，因此猜测是该属性中对应的值中包含现有的dnsHostName，尝试删除servicePrincipalName中包含hostHostName的值，也可直接删除servicePrincipalName属性。

在删除后，通过修改dnsHostName属性值为DC的dnHostName，发现修改成功。

![1654763147_62a1ae8bad43eafd10a82.png!small?1654763147938](https://image.3001.net/images/20220609/1654763147_62a1ae8bad43eafd10a82.png!small?1654763147938)

现在成功获得一个dnsHostName与域控相同的机器账户，由于创建账户时指定了账户密码，因此可以利用该账户欺骗AD CS获取域控权限证书。

该漏洞的主要实现过程可以总结为以下几步：

1.获取一个已知密码的计算机账户

2.删除计算机账户的servicePrincipalName属性或删除其中与dnsHostName有关的值

3.修改dnsHostName为DC的dnsHostName

最后使用该机器账户向AD CS服务器申请模版为“Machine”的证书并保存的本地，此时获取的实际是DC权限的证书。

![1654763216_62a1aed04be4ed092e2d2.png!small?1654763220657](https://image.3001.net/images/20220609/1654763216_62a1aed04be4ed092e2d2.png!small?1654763220657)

使用该证书申请TGT,能够成功获取域控账户的NT Hash,说明证书有效。这说明成功的从普通域用户权限提升到了域控权限。

![1654763302_62a1af268e58fce3eafb5.png!small?1654763302655](https://image.3001.net/images/20220609/1654763302_62a1af268e58fce3eafb5.png!small?1654763302655)

查看AD CS服务器中的证书申请记录，也可以看出AD CS认为认为颁发的证书为DC。

![1654763322_62a1af3abb9d5c08277bc.png!small?1654763323096](https://image.3001.net/images/20220609/1654763322_62a1af3abb9d5c08277bc.png!small?1654763323096)

 **03** 痕迹信息

在进行修改dnsHostName值时，会在域控产生事件ID为5136的目录服务更改日志。其中的特征为将计算机对象的dNSHostName值修改为DC的名称。

![1654763337_62a1af49ec203582f166d.png!small?1654763340485](https://image.3001.net/images/20220609/1654763337_62a1af49ec203582f166d.png!small?1654763340485)

同时会产生事件ID为4742的计算机管理审核成功日志，日志信息中包含了被修改的计算机账户信息和修改后的dnsHostName信息。如若使用此漏洞后需要进行痕迹清理，这两条日志最为关键。

![1654763384_62a1af781e92a58e801b4.png!small?1654763384314](https://image.3001.net/images/20220609/1654763384_62a1af781e92a58e801b4.png!small?1654763384314)

##  **04** 总结

本次漏洞产生的主要原因是计算机账户关键属性的ACL设置问题和AD
CS检查客户端身份不严格导致，结合之前的samAccountName欺骗漏洞，AD域中涉及身份认证标识的问题不止一次，微软在AD域中不用具有唯一性的自动编号字段SID而是其他字段作为身份认证标识在安全方面着实欠妥。

本次漏洞利用简单，流量特征不明显难以检测，同时获取的AD域证书有效时间长，因此对于AD域的提权和权限维持都有很高的利用价值。

