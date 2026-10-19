***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 **微软** **Exchange** **似乎易受权限提升攻击影响，任何用户，只要有邮箱，就能变身为** **Domain Admin** **。**

荷兰Fox-IT公司研究员Dirk-jan
Mollema在博客上发布了PoC，并详细解释了攻击细节。Mollema认为，主要的问题在于，Exchange默认在活动目录域名具有高权限。

他在博客文章中指出，“`ExchangeWindowsPermissions`组在活动目录的 Domain
对象上具有`WriteDacl`访问权限，使得该组成员均可修改域名权限，其中的一个权限是执行`DCSync`操作。”

这就导致攻击者能够通过Domain
Controller操作同步活动目录用户的哈希密码。攻击者可通过访问这些哈希密码假冒用户并在使用NTLM（微软的认证协议）或该域名内的Kerberos认证的服务进行认证。

 **目前，Mollema尚未回应相关问题。他发布的博客文章题目是《滥用Exchange：你距离成为Domain
Admin仅差一个API调用》。全文如下：**

在多数使用活动目录和Exchange的组织机构中，Exchange服务器都具有一种高权限：成为Exchange服务器上的Administer就足以提升至Domain
Admin。最近我在ZDI上偶然发现了一篇博客文章（见文末链接），他们详细说明了如何使用NTLM经由HTTP让Exchange进行认证。结合使用NTLM中继攻击，任何人只要拥有一个邮箱就能提升至Domain
Admin权限，在我所知道的大概90%的使用Exchange组织机构中都是可行的。这种攻击可能是默认的，目前尚未有任何补丁，不过可以使用一些缓解措施来阻止此类权限提升问题。本文详细说明了这种攻击，而且PoC已发布，名为“PrivExchange”。

##  **结合利用已知漏洞的新方法**

这篇文章讲的是如何结合利用一些新漏洞以及已知的协议弱点，发动新攻击。结合使用3个组件，拥有邮箱的任何用户就能提升至Domain Admin访问权限：

> Exchange Servers默认的权限太高
>
> NTLM认证易受中继攻击
>
> Exchange的某个功能使其能够认证到具有Exchange服务器计算机账户的攻击者

##  **Exchange和高权限**

这里说的主要漏洞是，Exchange在活动目录域名中具有高权限。Exchange Windows
Permissions组在活动目录的Domain对象中具有WriteDacl访问权限，导致该组的任何成员都能修改域名权限，其中一种权限是执行DCSync操作。任何具有这种权限的用户或计算机都能执行同步操作，而这种操作正常情况下是供Domain
Controllers进行复制，这就导致攻击者能够同步活动目录中的所有用户的哈希密码。多名研究人员曾对此进行过阐述（见文末参考部分），而且我和同事Rindert也在去年写过。在那篇文章中我也发布了ntlmrelayx的更新，增加了在NTLM中继过程中执行这些访问控制清单(ACL)攻击的可能性。

 ****

##  **NTLM 中继机器账户**

NTLM中继已经存在有段时间了。之前，它的主要关注点是经由SMB中继NTLM，以便在其它主机上执行代码。虽然到目前为止，仍然很可能在很多未启用SMB签名进行安全加固的公司中实施这种攻击，但其它协议也易受中继攻击。我认为其中最有意思的协议就是LDAP，它可用于读取并修改活动目录中的对象。简单说一下NTLM中继，就是除非已经应用了缓解措施，否则在连接至攻击者机器上之后和网络中的其它机器进行连接时，很可能会绕过Windows自动执行的认证，如下图所示：

![微软 Exchange 爆出 0day 漏洞，来看 POC
和技术细节](https://image.3001.net/images/20190126/1548481186_5c4bf2a2071b7.jpg!small)

当认证被中继到LDAP时，目录中的对象可被修改，给予攻击者权限，包括DCSync操作所需要的权限。因此，如果我们能够使Exchange通过NTLM认证和我们进行认证，那么我们就能执行ACL攻击。值得注意的是，只有在受害者通过HTTP而非SMB和我们进行认证时，中继到LDAP才奏效。

 ****

##  **使 Exchange 进行认证**

目前为止，唯一一个缺失的组件是使Exchange认证到我们的一种简单方法。ZDI的一名未透露姓名的研究员发现，使 Exchange 经由 Exchange
`PushSubscription`功能通过 HTTP 向任意 URL
认证是很可能实现的。他们使用这个漏洞将NTLM认证中继回Exchange（即反射型攻击）并假冒其他用户。如果我们再结合Exchange默认具有的高权限并执行中继攻击而非反射型攻击，那么我们就能使用这些权限获得DCSync权限。这个推送通知服务允许用户在即使未发生任何事件的情况下每隔X分钟（X值由攻击者设定）发送一次信息。这就能确保Exchange即使在收件箱中没有任何活动的情况下和我们连接。

##  **执行权限提升攻击**

实施攻击，实现权限提升的流程如下图所示：  

![微软 Exchange 爆出 0day 漏洞，来看 POC
和技术细节](https://image.3001.net/images/20190126/1548481214_5c4bf2be426a4.jpg!small)

我们需要使用两款工具执行该攻击：`privexchange.py`和`ntlmrelayx`。这两款工具可从GitHub的PrivExchange和impacket库中获取。以中继模式启动ntlmrelayx，以Domain
Controller上的LDAP作为目标，并通过如下代码使受攻击者控制的用户提升权限（这个案例中是`ntu`用户）：

![微软 Exchange 爆出 0day 漏洞，来看 POC
和技术细节](https://image.3001.net/images/20190126/1548481233_5c4bf2d1d00b3.jpg!small)

我们开始运行`privexchange.py`脚本：

![1000.jpg](https://image.3001.net/images/20190126/1548481251_5c4bf2e39135b.jpg!small)

如果是以没有邮箱的用户运行的话，就会得到如上出错消息。再尝试一下通过具有关联邮箱的用户运行一下：  

![1001.jpg](https://image.3001.net/images/20190126/1548481268_5c4bf2f4e2fff.jpg!small)

一分钟之后（推送通知提供的值），我们可以看到连接进入ntlmrelayx，用户获得DCSync权限：  

![微软 Exchange 爆出 0day 漏洞，来看 POC
和技术细节](https://image.3001.net/images/20190126/1548481292_5c4bf30cf0fe5.png!small)

我们确认DCSynx权限位于secretsdump位置：

![微软 Exchange 爆出 0day 漏洞，来看 POC
和技术细节](https://image.3001.net/images/20190126/1548481308_5c4bf31c51788.png!small)

凭借所有活动目录用户的哈希密码，攻击者就相当于持有一张金卡，能够假冒任何用户或使用任何用户密码哈希认证到任何接受NTLM或Kerberos域名认证的服务。

 ****

##  **技术细节：中继到 LDAP 并签名**

上文提到从SMB中继到LDAP不起作用，这也是为何说这种攻击无法通过使用最近发布的SpoolService
RPC滥用等实施（它通过SMB认证）的原因。由于关于这部分的问题很多，现在统一说一下。如果你不打算详细了解NTLM认证部分，可以跳过这部分。

在SMB和HTTP中的NTLM认证的不同之处在于默认协商的标记(flag)。有问题的部分是`NTLMSSP_NEGOTIATE_SIGN`标记(`0x00000010`)，如MS-NLMP第2.2.2.5节所示。通过HTTP的NTLM认证并不会默认设置该标记，但如果是通过SMB认证，则会默认设置：

![微软 Exchange 爆出 0day 漏洞，来看 POC
和技术细节](https://image.3001.net/images/20190126/1548481326_5c4bf32e78654.png!small)

当我们将它中继到LDAP时，认证成功，但LDAP的预期是所有通过衍生自密码的会话密钥签名的信息（中继攻击中不具备）。因此它会忽视任何不具备签名的信息，从而导致攻击失败。有人可能会想，是否可以在传输过程中修改这些标记，这样就不用协商签名了。由于Windows现代版本都默认包含一个MIC（信息完整性代码）即基于所有3
NTLM信息的签名，因此对其中任何信息的修改都会导致其不合法。

![微软 Exchange 爆出 0day 漏洞，来看 POC
和技术细节](https://image.3001.net/images/20190126/1548481345_5c4bf34118ecf.png!small)

那我们能删除MIC吗？可以是可以，毕竟它并非受NTLM信息保护的部分，但问题是NTLM认证(NTLMv2)中的最后一道防护措施阻止这样做：在 NTLMv2
响应的底部（该响应本身以受害者密码签名）存在一个`AV_PAIR` 结构`MsAvFlags`。当该字段的值为`0x0002`
时，表明客户端发送了一个具有type 3信息的MIC。

![微软 Exchange 爆出 0day 漏洞，来看 POC
和技术细节](https://image.3001.net/images/20190126/1548481368_5c4bf35839ae4.png!small)

修改NTLMv2响应将导致认证失效，因此我们不能删除这个flags字段。该字段说明MIC被计算且包含，将使目标服务器验证MIC，从而验证所有的3信息都不会在传输过程中遭修改，因此我们无法删除签名标记。

我认为，这种情况仅对微软对NTLM的实现有效。实现NTLM的自定义工具很可能并不受影响，只有添加MIC和AV_PAIR标记时，导致它们易受标记修改攻击，从而导致SMB
-> LDAP中继成为可能。其中一个例子就是NTLM的Java实现，它可在传输过程中遭修改绕过安全措施。

##  **攻击无需任何凭证**

上一节中，我们使用受攻陷凭证执行了攻击的第一步。如果攻击者只是位于执行网络攻击的位置，但并不具备任何凭证，那么仍然很可能触发Exchange进行认证。如果我们执行SMB到HTTP（或HTTP到HTTP）中继攻击（使用LLMNR/NBNS/mitm6欺骗），那么我们就能将位于同样网络片段中的用户认证中继到Exchange
EWS并使用他们的凭证触发回调。我给出了一小段修改后的httpattack.py，你可以结合ntlmrelayx从网络角度实施攻击，而无需任何凭证（你只需要修改攻击者主机即可，因为它在文件中是硬编码的）：  

![微软 Exchange 爆出 0day 漏洞，来看 POC
和技术细节](https://image.3001.net/images/20190126/1548481389_5c4bf36d18ec3.png!small)

##  **缓解措施**

攻击依靠多种组件才能实施。在此前的博客文章中我已经强调过多种针对NTLM中继攻击和中继到LDAP的防御措施。  

适用于该攻击的最重要的缓解措施包括：

> 删除Exchange在Domain对象上的不必要的高权限。
>
> 启用LDAP签名以及LDAP信道绑定，分别阻止中继到LDAP和LDAPS。
>
> 阻止Exchange服务器和任意端口上的工作站进行连接。
>
> 启用IIS中Exchange端点上（并非Exchange Back End，否则会导致Exchange崩溃）的Extended Protection
> for Authnticaiton。它将验证NTLM认证中的信道绑定参数，它将NTLM认证关联到TLS连接中并阻止向Exchange
> web服务进行中继。
>
> 删除注册表项(registry key)，从而能够中继回Exchange服务器，如微软对CVE-2018-8518缓解措施的讨论。
>
> 在Exchange服务器上执行SMB签名（偏好域名中的所有其它服务器和工作站）以阻止针对SMB的跨协议中继攻击。
>
>
> 如果不使用EWS的push/pull订阅服务，则可以通过使用限制策略将EWSMaxSubscriptions设置为0的方式禁用。这是@gentikiwi提供的方法，我还没有测试过合法应用程序使用它们的频率，因此推荐在小范围内进行测试。

###  **工具以及受影响版本**

PoC请参见
<https://github.com/dirkjanm/PrivExchange>，且已在如下Exchange/Windows版本上进行了测试：

> 将Server2012R2 上的Exchange 2013 (CU21)中继到Server 2016 DC（都是完全修复版本）
>
> 将Server 2016上的Exchange 2016 (CU11)中继到Server 2019 DC（都是完全修复版本）
>
> 将Server 2019上的Exchange 2019中继到Server 2019 DC（感谢@gentilkiwi进行测试）

如上的Exchange服务器都是使用共享权限模式安装的（默认），但有writeup指出，RBAC拆分权限部署也很容易受到攻击（我并未亲自测试过）。

Exchange 2010
SP3似乎并未受影响。在我的实验室中，这个版本按类似于以上提及的SMB协商签名，从而打破了这种中继攻击。版本14.3.435.0以及14.3.123.4均展现出这种行为。

 ****

##  **资源/参考**

可参见如下博客文章、白皮书和研究论文了解关于此类攻击的更多信息：

###  **1.** **缓解资源**

> <https://github.com/gdedrouas/Exchange-AD-> Privesc/blob/master/DomainObject/Fix-DomainObjectDACL.ps1>
>
> <https://www.blackhat.com/docs/webcast/04262018-Webcast-Toxic-Waste-Removal-> by-Andy-Robbins.pdf>

ACL权限提升研究

<https://www.blackhat.com/docs/us-17/wednesday/us-17-Robbins-An-ACE-Up-The-Sleeve-Designing-Active-Directory-DACL-Backdoors-wp.pdf>

###  **2\. NTLM** **中继** **/** **签名讨论**

> NTLM反射型攻击回顾<https://github.com/SecureAuthCorp/impacket/issues/451>
>
> NTLM SMB-> LDAP中继<https://github.com/SecureAuthCorp/impacket/pull/500>

 **中继凭证林总**

> <https://www.secureauth.com/blog/playing-relayed-credentials>

###  **3.** **其它参考**

 **MS-NLMP**

<https://msdn.microsoft.com/en-us/library/cc236621.aspx>

 **讨论Exchange API的ZDI文章**

<https://www.zerodayinitiative.com/blog/2018/12/19/an-insincere-form-of-flattery-impersonating-users-on-microsoft-exchange>

 **通过meterpreter进行NTLM远程中继，讨论如何远程通过枢纽主机进行中继**

<https://diablohorn.com/2018/08/25/remote-ntlm-relaying-through-meterpreter-on-windows-port-445/>

 **ACL攻击相关**

<https://www.slideshare.net/DirkjanMollema/aclpwn-active-directory-acl-exploitation-with-bloodhound>

##  **原文链接**

<https://dirkjanm.io/abusing-exchange-one-api-call-away-from-domain-admin/>

 ***本文作者：360代码卫士；转载请注明来自FreeBuf.COM**

 ** ******

