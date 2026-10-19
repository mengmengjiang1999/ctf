***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

![0.png](https://image.3001.net/images/20190218/1550505229_5c6ad50d6c172.png!small)

##  写在前面的话

 **今天，我们一起看一看攻击者（未经身份验证的用户）如何利用这个Exchange漏洞来在Exchange服务器上冒充合法用户并进行恶意操作。**

那么接下来我们直奔主题，我们将给大家详细分析这个服务器端请求伪造（SSRF）漏洞，并演示攻击者如何伪装成合法用户。

##  漏洞分析

在实施攻击的过程中，攻击者需要利用一个SSRF漏洞并结合其他安全缺陷来实现身份伪装。Exchange允许任意用户指定URL地址来实现订阅推送，而服务器会直接尝试向这个URL地址发送通知。漏洞之所以存在，是因为Exchange服务器使用了[CredentialCache.DefaultCredentials](https://docs.microsoft.com/en-us/dotnet/api/system.net.credentialcache.defaultcredentials)来进行网络连接：

![1.png](https://image.3001.net/images/20190218/1550505244_5c6ad51c5cc9f.png!small)

在Exchange Web服务中，CredentialCache.DefaultCredentials是以NT
AUTHORITY\SYSTEM权限运行的。这将导致Exchange服务器向攻击者的服务器发送NTLM哈希。Exchange服务器还会默认设置下列注册表键:

    
    
    HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Lsa\DisableLoopbackCheck= 1

此时，攻击者将能够使用这些NTLM哈希来进行HTTP身份验证。比如说，他们可以使用这些哈希来访问Exchange Web服务（EWS）。因为它是以NT
AUTHORITY\SYSTEM权限运行的，攻击者就可以利用TokenSerializationRight获取到特权“会话”，并使用一个SOAP头来冒充特定用户。

下面给出的SOAP头样本中，攻击者使用了SID（S-1-5-21-4187549019-2363330540-1546371449-500）来伪装成管理员用户：

![2.png](https://image.3001.net/images/20190218/1550505254_5c6ad526613c3.png!small)

##  漏洞利用

为了方便演示，我们使用了下面这两个Python脚本：

1、 serverHTTP_relayNTLM.py：它可以从入站连接中获取NTLM哈希，并将其用于EWS身份验证。

2、 Exch_EWS_pushSubscribe.py：让PushSubscription调用我们的serverHTTP_relayNTLM.py。

脚本下载地址：【[传送门](https://github.com/thezdi/PoC/tree/master/CVE-2018-8581)】（还需Python-ntlm模块）

首先，我们需要获取到目标用户的SID，大致方法如下：

1、 以认证用户的身份登录OWA：

![3.png](https://image.3001.net/images/20190218/1550505276_5c6ad53cecf79.png!small)

2、 接下来，创建新的文件夹，我们这里使用“tempFold”。点击下拉菜单中的“Permissions”：

![4.png](https://image.3001.net/images/20190218/1550505286_5c6ad54604e0a.png!small)

3、 添加需要冒充的用户电子邮件地址，这里我们使用victim@contoso.local：

![5.png](https://image.3001.net/images/20190218/1550505298_5c6ad552c3202.png!small)

4、 按下F12键，选择“Network”标签，然后再次点击新创建文件夹下拉菜单中的“Permissions”：

![6.png](https://image.3001.net/images/20190218/1550505310_5c6ad55e80e6d.png!small)

5、 我们需要检查第一个service.svc?action=GetFolder请求返回的响应，查看方法：

    
    
    Body->ResponseMessages->Items->0->Folders->0->PermissionSet->Permissions->N->UserId->SID

样本中的N为2，但是你可以根据你自己的情况来选择正确的。PrimarySmtpAddress为目标用户的邮件地址，如果响应中不包含PermissionSet参数，我们就需要查看另一个service.svc?action=GetFolder请求了：

![7.png](https://image.3001.net/images/20190218/1550505326_5c6ad56ee70f4.png!small)

6、
我们选择使用serverHTTP_relayNTLM.py中的SID来进行操作，我们还需要选择一个没有被屏蔽的TCP端口来转发Exchange服务器上的出站连接。比如说，TCP端口8080可用的话。

接下来，使用真实信息修改serverHTTP_relayNTLM.py：

![8.png](https://image.3001.net/images/20190218/1550505341_5c6ad57d2f688.png!small)

设置好正确的脚本变量后，我们就可以开始了：

![9.png](https://image.3001.net/images/20190218/1550505354_5c6ad58ab32ee.png!small)

7、 下一步就是设置Exch_EWS_pssushSubscribe.py脚本中的变量了：

![10.png](https://image.3001.net/images/20190218/1550505371_5c6ad59b2c3ef.png!small)

完成后，我们就可以执行脚本了：

![11.png](https://image.3001.net/images/20190218/1550505393_5c6ad5b185ec2.png!small)

8、 最后一步，我们需要利用事件触发机制来推送通知。我们可以进行类似创建和发送新邮件，或者删除新创建的文件夹来实现：

  
![12.png](https://image.3001.net/images/20190218/1550505485_5c6ad60d23b2f.png!small)

成功后，我们的serverHTTP_relayNTLM.py就可以从Exchange服务器那里收到入站连接了：

![13.png](https://image.3001.net/images/20190218/1550505497_5c6ad6197d1ec.png!small)

攻击成功后，我们将在响应中看到UpdateInboxRulesResponse
ResponseClass="Success"。这也就意味着，入站规则已经成功添加进目标用户的邮箱了，所有的入站邮件都会被转发给攻击者。

接下来，我们需要测试这个新规则。我们需要利用任意邮箱账号来给目标用户发送一封邮件，但不要用我们新添加的规则（attacker@contoso.local），因为如果转发地址和目的地址相同的话规则就无效了。现在，登录管理员账号，发送某些信息给目标用户：

![14.png](https://image.3001.net/images/20190218/1550505516_5c6ad62c2d667.png!small)

检查攻击者的收件箱，我们就可以看到这封邮件了：

![15.png](https://image.3001.net/images/20190218/1550505529_5c6ad639aeedb.png!small)

没错，就是这么简单。希望可以给大家平常的挖洞带来一些灵感！

***参考来源：[zerodayinitiative](https://www.zerodayinitiative.com/blog/2018/12/19/an-insincere-form-of-flattery-impersonating-users-on-microsoft-exchange)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

