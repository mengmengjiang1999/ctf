##  简单介绍 Mimikatz 攻击

**Mimikatz 在内网渗透测试中发挥着至关重要的作用，主要是因为它能够以明文形式从内存中提取明文密码。众所周知，攻击者在他们的渗透中大量使用
Mimikatz，尽管微软推出了安全补丁，但是在较旧的操作系统（如 Windows 2008 Server）中 Mimikatz
仍然有效，所以在很多情况下它可能导致横向移动和域权限提升。值得注意的是，如果 Mimikatz
是从本地管理员等权限执行的，则它只能导出用户凭据和密码哈希值。**

下面通过几种方法来防御 Mimikatz 攻击：

##  Debug 权限设置

根据 Microsoft
的调试权限确定哪些用户可以将调试器附加到任何进程或内核。默认情况下，此权限授予本地管理员。然而，除非他是系统进程，否则本地管理员极不可能需要此权限。

![](https://image.3001.net/images/20180813/1534164328_5b717d682ddd5.png!small)本地管理员-调试权限

在默认安装的 Windows Server 2016 系统中，未定义调试权限的组策略，这意味着只有本地管理员具有此权限。

![](https://image.3001.net/images/20180813/1534164606_5b717e7ea7913.png!small)调试权限
- 组策略

从攻击者的角度来看，可以通过使用 Mimikatz 以下命令执行此检查：

    
    
    privilege::debug

![](https://image.3001.net/images/20180813/1534164794_5b717f3a498ec.png!small)检查调试权限

Mimikatz 需要此权限，因为它要与 LSASS
进程交互。因此，将此权限仅设置为需要这权限的特定用户或组，并将其从本地管理员中删除是非常重要。可以通过将策略定义为不包含任何用户或组来禁用
SeDebugPrivilege。

    
    
    Group Policy Management Editor -> Windows Settings -> Security Settings -> Local Policies -> User Rights Assignment -> Debug programs -> Define these policy settings:

![](https://image.3001.net/images/20180813/1534165321_5b718149c9954.png!small)

禁用 SeDebugPrivilege

![](https://image.3001.net/images/20180813/1534165370_5b71817ad9624.png!small)Mimikatz-禁用调试权限

##  WDigest

WDigest 协议是在 WindowsXP 中被引入的，旨在与 HTTP 协议一起用于身份认证。默认情况下，Microsoft 在多个版本的
Windows（Windows XP-Windows 8.0 和 Windows Server 2003-Windows Server
2012）中启用了此协议，这意味着纯文本密码存储在 LSASS（本地安全授权子系统服务）进程中。Mimikatz 可以与 LSASS
交互，允许攻击者通过以下命令检索这些凭据：

    
    
    sekurlsa::wdigest

![](https://image.3001.net/images/20180813/1534165815_5b718337b307f.png!small)Mimikatz
— WDigest

Microsoft 在 Windows8.1，Windows 10，Windows Server 2012 R2 和 Windows Server 2016
系统中默认禁用此协议。但是，如果您的组织使用较旧的操作系统（如 Windows 7 和 Windows Server 2008 等），Microsoft
已发布了一个补丁（KB2871997），允许管理员启用或禁用 WDigest 协议。打完补丁后，建议验证是否已经从注册表中禁用 WDigest。

    
    
    HKEY_LOCAL_MACHINE\System\CurrentControlSet\Control\SecurityProviders\WDigest

![](https://image.3001.net/images/20180813/1534166027_5b71840ba5804.png!small)WDigest-禁用

Negotiate 和 UseLogonCredential 注册表项值应设置为 0 可以完全禁用此协议。应该注意的是，在较新的操作系统（Windows
Server 2016，Windows 10 等）中，UseLogonCredential
注册表项不存在。当然，具有本地管理员权限的攻击者可以修改注册表以启用 WDigest 并获取凭据，因为 Dave Kennedy
在他的博客中对此进行了大量解释。因此，如果在禁用此协议后将这些值设置为 1，则表明存在攻击。应该不断监视注册表修改，以便在早期阶段获得警报并捕获威胁。

如果我们禁用此协议，攻击者尝试从 WDigest 检索纯文本凭据将失败：

![](https://image.3001.net/images/20180813/1534166691_5b7186a3596c2.png!small)Mimikatz-WDigest 已禁用

##  LSA 保护

本地安全权限服务（LSASS）验证用户是否进行本地和远程登录，并实施本地安全策略。Windows 8.1 及更高版本的系统中，Microsoft 为 LSA
提供了额外的保护，以防止不受信任的进程读取内存或代码注入。Windows 8.1 之前的系统，攻击者可以执行 Mimikatz 命令来与 LSA
交互并检索存储在 LSA 内存中的明文密码。

    
    
    sekurlsa::logonPasswords

![](https://image.3001.net/images/20180813/1534167122_5b71885204a50.png!small)Mimikatz-与
LSA 交互

建议 Windows Server 2012R2 和 Windows 8.1 之前的系统应启用 LSA 保护，以防止 Mimikatz 访问 LSASS
进程的特定内存位置获取明文密码。可以通过创建注册表项 RunAsPPL 并设置其值为 1 来启用此保护。

    
    
    HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\LSA

![](https://image.3001.net/images/20180813/1534167416_5b718978825e9.png!small)LSA
保护已启用

在启用了 LSA 保护的系统中，攻击者将收到以下错误：

![](https://image.3001.net/images/20180813/1534167481_5b7189b9e3248.png!small)Mimikatz-LSA 保护

##  受限制的管理模式

Microsoft 在 WindowsServer 2012 R2 中引入了一项额外的安全功能，可以有效的防止本地管理员的纯文本凭据在 RDP
会话期间存储在 LSASS 中。即使 LSA 保护可以阻止 Mimikatz 检索凭证，但建议在攻击者禁用 LSA
保护的情况下使用此安全功能作为额外的安全保护。

应在以下位置创建「DisableRestrictedAdmin」注册表项并且设置为 0，这样可以通过网络 RDP
会话请求管理员登陆系统。此外，创建「DisableRestrictedAdminOutboundCreds」注册表项值为 1，可以禁止管理员执行 RDP
的系统内部的网络身份验证。缺少此注册表项，管理员可以导出凭据。

    
    
    HKEY_LOCAL_MACHINE\System\CurrentControlSet\Control\Lsa

已启用受限制的管理模式

需要在域中强制执行「对远程服务器的凭据限制委派」策略，以确保所有出站 RDP 会话都使用「RestrictedAdmin」模式，因此才不会泄露凭据。

![](https://image.3001.net/images/20180813/1534168298_5b718ceabfa00.png!small)组策略限制凭证授权

需要使用「Require Restricted Admin」设置启用该策略。

![](https://image.3001.net/images/20180813/1534168378_5b718d3a6ecc5.png!small)启用受限制的管理员-限制凭证授权

强制执行此策略后，管理员可以远程 RDP 到所需注册表权限的工作站和服务器，以便控制 Windows 运行一些程序。

![](https://image.3001.net/images/20180813/1534168621_5b718e2dad2ce.png!small)运行-受限制的管理模式切换

或者直接从命令提示符执行它。

![](https://image.3001.net/images/20180813/1534168708_5b718e841d779.png!small)命令提示符-受限制的管理模式切换

对于 Windows 2012 R2 和 Windows 8.1 之前的旧操作系统，此选项是 Microsoft 补丁的一部分 KB2871997。

##  凭证缓存

如果域控制器不可用，Windows 将检查已缓存的最后一个密码哈希值，以便使用系统对用户进行身份验证。这些密码哈希值缓存在以下注册表设置中：

    
    
    HKEY_LOCAL_MACHINE\SECURITY\Cache

如果执行 Mimikatz 以下命令，可以检索这些哈希值：

    
    
    lsadump::cache

默认情况下，Windows 会缓存最后 10 个密码哈希值。建议通过将以下安全设置来防止密码的本地缓存，将其值设置为 0。

    
    
    Computer Configuration -> Windows Settings -> Local Policy -> Security Options -> Interactive Logon: Number of previous logons to cache -> 0

![](https://image.3001.net/images/20180813/1534169224_5b719088c61fd.png!small)交互式登录-不缓存登录

攻击者尝试使用 Mimikatz 检索这些密码哈希将失败：

![](https://image.3001.net/images/20180813/1534169280_5b7190c0e2b71.png!small)Credential
Caching 禁用后 Mimikatz 出错

##  受保护的用户组

WindowsServer 2012 及更高版本中的 Microsoft 引入了一个名为「Protected
Users」的新安全组。此组使域管理员能够保护本地管理员等有权限的用户，因为属于该组的任何帐户只能通过 Kerberos 对域进行身份验证。这将有助于防止
NTLS 密码哈希值或 LSAS 中的纯文本凭据泄露给敏感帐户，这些帐户通常是攻击者的目标。

可以在「Active Directory 用户和计算机」中找到「Protected Users」安全组。

![](https://image.3001.net/images/20180813/1534170343_5b7194e7863bf.png!small)

ActiveDirectory-受保护的用户安全组

成为此安全组一部分的帐户将在身份验证方面自动归入 Kerberos 策略，默认情况下配置如下：

![](https://image.3001.net/images/20180813/1534170575_5b7195cfa829a.png!small)Kerberos
默认策略

或者，可以通过执行以下 PowerShell 命令将帐户添加到「受保护的用户」组中：

    
    
    Add-ADGroupMember –Identity 'Protected Users' –Members Jane

![](https://image.3001.net/images/20180813/1534170683_5b71963b1e199.png!small)通过
PowerShell 添加受保护的用户组帐户

通过安装 Microsoft 的补丁 KB2871997，WindowsServer 2008 等较旧的操作系统可以拥有此安全组。

##  结论

通过使用有效的端点解决方案与 AppLocker 等应用程序白名单相结合来防止恶意的可执行文件，执行一些 PowerShell 命令和 cmd
命令，还可以加固安全性。即使网络攻击者已经实现绕过这些控制，执行注册表修改，以便充分利用 Mimikatz
进行凭证获取，在此过程中将会生成许多事件，管理员应该监视某些注册表项，这有助于检测攻击行为。

***本文原创作者：sysver，转载请注明来自FreeBuf.COM**

