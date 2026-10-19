## 1、服务主体名称（SPN）

服务主体名称(`SPN`)是服务实例的唯一标识符。`Kerberos`身份验证使用`SPN`将服务实例与服务登录帐户相关联。这允许客户端应用程序请求服务对帐户进行身份验证，即使客户端没有该帐户名。

在`Kerberos`身份验证服务可以使用`SPN`对服务进行身份验证之前，`SPN`必须在服务实例用来登录的账户对象上注册。一个特定的`SPN`只能在一个账户上注册。当客户端想要连接到服务时，它会找到该服务的一个实例，为该实例组成一个`SPN`，连接到服务，并提供`SPN`以供该服务进行身份验证。

`SPN（ServicePrincipalName）`唯一标识了一个服务账户，它看起来像下面这样：

![image-20220419102304296](https://image.3001.net/images/20220427/1651038664_6268d9c8ef04614acf5ab.png!small)

## 2、为什么设置`SPN`很重要！

设置`SPN`的最重要原因是，它可以识别你的目标服务器在网络上托管的特定服务。当我们配置我们的服务器（托管服务）以使用`Kerberos`认证让客户访问该服务时，有几个先决条件必须满足。

首先，客户和服务器必须加入到一个域中。如果服务器来自其他域，那么必须在两个域之间建立信任。其次，必须为托管服务的服务器成功注册一个`SPN`，以便在网络上识别它。

我们有几种方法可以检查`SPN`是否已经注册成功。如果托管服务的服务器是在域账户下运行的（推荐使用），我们可以运行以下命令来查看已注册的服务。

![image-20220419102347387](https://image.3001.net/images/20220427/1651038666_6268d9ca578c3136eeb01.png!small)

## 3、如何设置SPN

服务主体名称 (`SPN`) 是`Active
Directory`中客户端用来唯一标识服务实例的名称。`SPN`将服务名称与计算机和用户账户相结合，形成一种服务`ID`。为了使`Kerberos`认证（一种在网络上验证客户和服务器实体的协议）发挥作用，必须为`Active
Directory`中为每个服务账户注册一个`SPN`。

 **演示**

在这个演示中，为`SQLServiceAccount`设置一个`SPN`。

我们有一个域帐户`SQLServiceAccount`，我们将使用它作为服务帐户。我们将在一台假装是`SQL`服务器的计算机上注册它，用下面的命令来注册一个`SPN`：

    
    
    setspn -s MSSQLSvc/sqlserver.rootdse.lab ROOTDSE\SQLServiceAccount
    

![image-20220419103445730](https://image.3001.net/images/20220427/1651038668_6268d9cc122d9c7ea3ad5.png!small)

让我们从`Active Directory`用户和计算机中验证其属性，以查看其设置是否正确。

![image-20220419103635829](https://image.3001.net/images/20220427/1651038669_6268d9cd75311c79eca5c.png!small)

现在，如果我们在整个域中搜索`SPN`，我们应该能够看到它。

![image-20220419103715322](https://image.3001.net/images/20220427/1651038670_6268d9cec7d8f472073ab.png!small)

或者我们可以通过`LDAP`查询，在`adsisearcher`的帮助下，轻松枚举出服务账户的服务主体名称（`SPN`）：

    
    
    PS C:\> ([adsisearcher]'(servicePrincipalName=*)').FindAll()
    Path                                                       Properties
    ----                                                       ----------    LDAP://CN=RDSEDC01,OU=Domain Controllers,DC=rootdse,DC=lab {ridsetreferences, logoncount, codepage, objectcategory...}
    LDAP://CN=krbtgt,CN=Users,DC=rootdse,DC=lab                {logoncount, codepage, objectcategory, description...}
    LDAP://CN=SQLServiceAccount,CN=Users,DC=rootdse,DC=lab     {givenname, codepage, objectcategory, dscorepropagationdata...}
    

现在我们可以看到`SPN`已正确配置，接下来让我们看看如何进行`kerberoasting`。

## 4、Kerberoasting

在开始`Kerberoasting`之前，让我们先讨论一下这种攻击的实际工作原理。`Kerberoasting`是流行的`AD
Kerberos`攻击之一，`Tim Medin（Kerberoast Guy）`在`Derbycon
2014`的演讲中指出了这一点。在此攻击中，服务帐户的凭据哈希被从`Active
Directory`中提取并离线破解。我们需要确定哪些帐户是`kerberoastable`的，然后作为任何经过身份验证的用户，我们可以请求目标服务帐户的服务票证(`TGS`)，而不需要向运行服务的目标服务器发送任何流量。

如下图所示，`Kerberoasting`的重点是向`KDC`请求`TGS`。此攻击仅涉及重点标记的步骤 3 和 4。

![image-20220419104731446](https://image.3001.net/images/20220427/1651038672_6268d9d082425df8de297.png!small)

以下是执行`Kerberoasting`的步骤：

1、枚举设置了`SPN`值的`AD`账户

2、使用目标服务账户的`SPN`值从`AD`请求服务票（`TGS`）

3、提取服务票据并导入到离线破解

4、对其进行暴力攻击以破解目标服务账户的密码

这种攻击如此有效的原因是：

> 进行kerberoasting不需要特殊权限。任何经过身份验证的用户都可以做到。
>
> 管理员为服务账户创建了弱密码，就像普通用户账户一样。
>
> 在一个组织环境中，服务账户密码的更改频率非常低。
>
> 在大多数情况下，服务账户具有域管理权限（或者至少在目标服务器上具有本地管理权限）。
>
> 由于上述原因，它被认为是一种唾手可得的果实，因为它很容易执行，并且如果服务帐户被成功入侵，则很有可能在域中提升权限。

对于服务票据的提取，我们可以使用类似如下的工具：

> Mimikatz
>
> PowerView
>
> SharpView
>
> Rubeus

下面是使用`Rubeus`进行`kerberoasting`的演示：

![image-20220419105424302](https://image.3001.net/images/20220427/1651038674_6268d9d22764f86b7ef21.png!small)

一旦我们得到票据，我们就可以开始破解密码。破解服务账户是一个特别成功的方法，因为它们的密码很少更改。而且，离线破解票据不会产生任何域流量或账户被锁定，所以它是无法被检测到的。

![image-20220419105656797](https://image.3001.net/images/20220427/1651038679_6268d9d73fb6b1a93ebe7.png!small)

## 5、总结

对于在域内拥有有限权限的攻击者来说，`Kerberoasting`是一种有效的技术。这完全取决于密码的强度，一旦被破解，就会获得对多个账户的访问权限，并可以用来发动进一步的攻击。设置强密码可能会使攻击变得更加困难，因此应该像对待其他特权帐户一样对待服务帐户。

最佳做法是建立一个服务账户的清单，定期检查最后一次修改密码的时间，并实施定期轮换密码的流程。几乎没有什么方法可以通过在环境中实施欺骗来检测这种攻击。在另一篇博文中，写了关于使用`AD`诱饵检测环境中可能存在的`kerberoasting`尝试。链接在这里：[使用AD诱饵检测LDAP枚举和Bloodhound的Sharphound收集器](https://medium.com/securonix-tech-blog/detecting-ldap-enumeration-and-bloodhound-s-sharphound-collector-using-active-directory-decoys-dfc840f2f644)。

## 6、说明

本文由笔者在原文上编译，转载请注明原文出处。

原文出处：[Active Directory Security Fundamentals (Part 2)- SPN,
Kerberoasting](https://rootdse.org/posts/active-directory-security-2/)

