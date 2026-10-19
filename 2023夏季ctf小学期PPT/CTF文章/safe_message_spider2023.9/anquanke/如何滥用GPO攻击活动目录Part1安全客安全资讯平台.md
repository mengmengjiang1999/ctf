# 如何滥用 GPO 攻击活动目录 Part 1

阅读量 **251819**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-01-09 14:34:13

 **x**

##### 译文声明

本文是翻译文章，文章原作者 rastamouse，文章来源：rastamouse.me

原文地址：<https://rastamouse.me/2019/01/gpo-abuse-part-1/>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/dm/1024_549_/t015358c947934a711e.png)

## 前言

很久以来我一直想写关于组策略对象(GPO, Group Policy Objects)的内容，很高兴终于可以开始了。

如果你对GPO不太熟悉，我强烈建议你阅读[Andy
Robbins](https://twitter.com/_wald0)的“[红队GPO和OU指南](https://posts.specterops.io/a-red-teamers-guide-to-gpos-and-ous-f0d03976a31e)”。他介绍了GPO如何执行，如何使用BloodHound找到基于GPO控制的攻击路径，并解释了执行这些攻击的几种方法。

在武器化方面，[Will
Schroeder](https://twitter.com/harmj0y)发表了文章：[滥用GPO权限](http://www.harmj0y.net/blog/redteaming/abusing-gpo-permissions/)，并在Powerview中实现了New-GPOImmediateTask。但是这个功能后来[被删除](https://www.harmj0y.net/blog/powershell/make-powerview-great-again/)了，并带有以下解释：

> 不一致，手工操作更好

本系列文章的目的是演示如何枚举这些滥用机会，并将其用于权限提升和实现持久化。

## 枚举

有一些我们可能感兴趣的权限，例如：

  * 在域（domain）中创建新的GPO。
  * 将GPO链接到某个OU（组织单元, organizational unit）。
  * 修改现有的GPO(这可能是/不是当前链接的)。

我之所以这样认为，是因为它们是单独授权的权限。例如：

  * 授权创建GPO并不一定授权其链接到OU。
  * 用户可能修改现有的GPO，但它可能是未链接的，不能链接自己本身。
  * 或者用户可能无法修改GPO，但可以将其链接到另一个OU。

因此，拥有的权限组合将取决于如何实现这种滥用。

## 创建GPO

在组策略管理控制台(GPMC)中授权在域中创建GPO，如下：

![](https://p3.ssl.qhimg.com/t0163f6ba15caa81302.png)

可以用下面的方法在PowerView中进行枚举：

    
    
    PS > Get-DomainObjectAcl -SearchBase "CN=Policies,CN=System,DC=testlab,DC=local" -ResolveGUIDs | Where-Object { $_.ObjectAceType -eq "Group-Policy-Container" }
    
    AceQualifier           : AccessAllowed
    ObjectDN               : CN=Policies,CN=System,DC=testlab,DC=local
    ActiveDirectoryRights  : CreateChild                                       <--- CreateChild just means "Create GPO" in this context
    ObjectAceType          : Group-Policy-Container
    ObjectSID              :
    InheritanceFlags       : None
    BinaryLength           : 56
    AceType                : AccessAllowedObject
    ObjectAceFlags         : ObjectAceTypePresent
    IsCallback             : False
    PropagationFlags       : None
    SecurityIdentifier     : S-1-5-21-407754292-3742881058-3910138598-1106     <--- SID of the user/group
    AccessMask             : 1
    AuditFlags             : None
    IsInherited            : False
    AceFlags               : None
    InheritedObjectAceType : All
    OpaqueLength           : 0
    
    
    
    PS > Convert-SidToName S-1-5-21-407754292-3742881058-3910138598-1106
    LABDesktop Admins
    

## GP-Link

Get-DomainOU向我们展示了活动目录（Active Directory）中所有的组织单元。在这个例子中，我们只有默认的Domain
Controllers和自定义的Workstations组织单元。

    
    
    PS > Get-DomainOU
    
    usncreated             : 6031
    systemflags            : -1946157056
    iscriticalsystemobject : True
    gplink                 : [LDAP://CN={6AC1786C-016F-11D2-945F-00C04fB984F9},CN=Policies,CN=System,DC=testlab,DC=local;0]     <--- GUID(s) of GPO(s) already linked to the OU
    whenchanged            : 06/01/2019 13:14:24
    objectclass            : {top, organizationalUnit}
    showinadvancedviewonly : False
    usnchanged             : 6031
    dscorepropagationdata  : {06/01/2019 13:15:24, 01/01/1601 00:00:01}
    name                   : Domain Controllers
    description            : Default container for domain controllers
    distinguishedname      : OU=Domain Controllers,DC=testlab,DC=local
    ou                     : Domain Controllers
    whencreated            : 06/01/2019 13:14:24
    instancetype           : 4
    objectguid             : d312c411-7c7c-4fb7-b4f9-cbf0637b551f
    objectcategory         : CN=Organizational-Unit,CN=Schema,CN=Configuration,DC=testlab,DC=local
    
    usncreated            : 12790
    name                  : Workstations
    gplink                : [LDAP://cn={7DD7A136-334C-47C1-8890-D9766D449EFA},cn=policies,cn=system,DC=testlab,DC=local;0]     <--- GUID(s) of GPO(s) already linked to the OU
    whenchanged           : 07/01/2019 07:18:51
    objectclass           : {top, organizationalUnit}
    usnchanged            : 13118
    dscorepropagationdata : {07/01/2019 07:18:51, 07/01/2019 07:17:22, 07/01/2019 07:14:37, 06/01/2019 13:52:27...}
    distinguishedname     : OU=Workstations,DC=testlab,DC=local
    ou                    : Workstations
    whencreated           : 06/01/2019 13:28:56
    instancetype          : 4
    objectguid            : 4f733ab3-1809-4a31-b299-e07a3b7b4669
    objectcategory        : CN=Organizational-Unit,CN=Schema,CN=Configuration,DC=testlab,DC=local
    

ADUC（Active Directory Users and Computers）中的控制委派向导（Delegation of Control
Wizard）具有“管理组策略链接”的预定义模板。它能帮助我们将不同类型的权限授予特定对象的主体。

在本例中，我们将它授予LABDesktop Admins组。

![](https://p2.ssl.qhimg.com/t01328d45fcfb1ea4b2.png)

同样地，我们可以在PowerView中通过将Get-DomainOu输出到Get-DomainObjectAcl进行枚举，并查找GP-Link ACE。

    
    
    PS > Get-DomainOU | Get-DomainObjectAcl -ResolveGUIDs | Where-Object { $_.ObjectAceType -eq "GP-Link" }
    
    AceQualifier           : AccessAllowed
    ObjectDN               : OU=Workstations,DC=testlab,DC=local               <--- The OU Distinguished Name
    ActiveDirectoryRights  : ReadProperty, WriteProperty                       <--- WriteProperty (GP-Link is a property on the OU object that you can see in the Attribute Editor of ADUC)
    ObjectAceType          : GP-Link
    ObjectSID              :
    InheritanceFlags       : ContainerInherit                                  <--- This will be interesting later
    BinaryLength           : 56
    AceType                : AccessAllowedObject
    ObjectAceFlags         : ObjectAceTypePresent
    IsCallback             : False
    PropagationFlags       : None
    SecurityIdentifier     : S-1-5-21-407754292-3742881058-3910138598-1106     <--- SID of the user/group
    AccessMask             : 48
    AuditFlags             : None
    IsInherited            : False
    AceFlags               : ContainerInherit
    InheritedObjectAceType : All
    OpaqueLength           : 0
    

## 修改GPO

我们还可以将Get-DomainGPO输送到Get-DomainObjectAcl中，查找有哪些主体可以修改它们。在这里，我们查找与WriteProperty、WriteDacl或WriteOwner匹配的ActiveDirectoryRights。(在大多数情况下，我们只希望找到WriteProperty，但是拥有WriteDacl或WriteOwner使我们能够将WriteProperty授予自己并修改GPO)。

我们给SecurityIdentifier添加了一个match项，所以我们只列出RIDs > 1000的，避免列出每个GPO的Domain
Admins和Enterprise Admins等等。

    
    
    PS > Get-DomainGPO | Get-DomainObjectAcl -ResolveGUIDs | Where-Object { $_.ActiveDirectoryRights -match "WriteProperty|WriteDacl|WriteOwner" -and $_.SecurityIdentifier -match "S-1-5-21-407754292-3742881058-3910138598-[d]{4,10}" }
    
    AceType               : AccessAllowed
    ObjectDN              : CN={7DD7A136-334C-47C1-8890-D9766D449EFA},CN=Policies,CN=System,DC=testlab,DC=local
    ActiveDirectoryRights : CreateChild, DeleteChild, Self, WriteProperty, DeleteTree, Delete, GenericRead, WriteDacl, WriteOwner
    OpaqueLength          : 0
    ObjectSID             :
    InheritanceFlags      : None
    BinaryLength          : 36
    IsInherited           : False
    IsCallback            : False
    PropagationFlags      : None
    SecurityIdentifier    : S-1-5-21-407754292-3742881058-3910138598-1105     <--- SID of the user/group
    AccessMask            : 983295
    AuditFlags            : None
    AceFlags              : None
    AceQualifier          : AccessAllowed
    
    AceType               : AccessAllowed
    ObjectDN              : CN={7DD7A136-334C-47C1-8890-D9766D449EFA},CN=Policies,CN=System,DC=testlab,DC=local
    ActiveDirectoryRights : CreateChild, DeleteChild, ReadProperty, WriteProperty, GenericExecute
    OpaqueLength          : 0
    ObjectSID             :
    InheritanceFlags      : ContainerInherit
    BinaryLength          : 36
    IsInherited           : False
    IsCallback            : False
    PropagationFlags      : None
    SecurityIdentifier    : S-1-5-21-407754292-3742881058-3910138598-1109     <--- SID of the user/group
    AccessMask            : 131127
    AuditFlags            : None
    AceFlags              : ContainerInherit
    AceQualifier          : AccessAllowed
    
    
    
    PS > Get-DomainGPO | Where-Object { $_.DistinguishedName -eq "CN={7DD7A136-334C-47C1-8890-D9766D449EFA},CN=Policies,CN=System,DC=testlab,DC=local" } | Select-Object DisplayName
    
    displayname
    -----------    Workstation Policy
    

如GPMC的Details中所示，LABbwallace是这个名为WorkStation Policy的GPO的所有者。

![](https://p5.ssl.qhimg.com/t0108bb3026580e9f4d.png)

GPO的创建者被自动显式授权Edit settings（编辑设置）、delete（删除）、modify
security（修改安全性），这些安全性表现为Createchild、Deletechild、Self、WriteProperty、DeleteTree、Delete、GenericRead、WriteDacl、WriteOwner。

![](https://p2.ssl.qhimg.com/t01b8708a2971030280.png)

在本例中，LABtlockhart还被授予了编辑设置权限，即Createchild、Deletechild、ReadProperty、WriteProperty、GenericExecute。

## 映射GPO和OUs

这可以从几个不同的角度来完成。你可能有一个有趣的GPO，并且希望知道单个GPO对应的是哪个组织单元和/或计算机；你可能希望列出适用于特定组织单元的每个GPO；或者你可能希望列出适用于特定计算机的每个GPO。

###  通过计算机

我们列出对应于ws-1.testlab.local的每个GPO，只显示名称和GUID。

    
    
    PS > Get-DomainGPO -ComputerIdentity ws-1 -Properties Name, DisplayName
    
    displayname           name
    -----------           ----    Demo GPO              {ECB75201-82D7-49F3-A0E0-86788EE7DC36}
    Workstation Policy    {7DD7A136-334C-47C1-8890-D9766D449EFA}
    Default Domain Policy {31B2F340-016D-11D2-945F-00C04FB984F9}
    

在这里，GPO有一个Display Name、GUID和一个对象GUID，后两者很容易混淆。

###  通过GPO

这里，我们列出了Demo GPO映射的每个组织单元。我们使用GUID在GPLink中搜索过滤器。

    
    
    PS > Get-DomainOU -GPLink "{ECB75201-82D7-49F3-A0E0-86788EE7DC36}" -Properties DistinguishedName
    
    distinguishedname
    -----------------    OU=Domain Controllers,DC=testlab,DC=local
    OU=Workstations,DC=testlab,DC=local
    

如果你需要知道这些组织单元中有哪些计算机，可以这样做：

    
    
    PS > Get-DomainComputer -SearchBase "LDAP://OU=Workstations,DC=testlab,DC=local" -Properties DistinguishedName
    
    distinguishedname
    -----------------    CN=WS-1,OU=Workstations,DC=testlab,DC=local
    CN=WS-2,OU=Workstations,DC=testlab,DC=local
    CN=WS-3,OU=Workstations,DC=testlab,DC=local
    

###  通过组织单元（OU）

如果我们获得Workstations组织单元的GPLink属性(它告诉我们链接到它的每个GPO)，结果将作为单个文本字符串返回，这意味着我们不能直接将其导入get-DomainGPO并找到它们相应的Display Names。

    
    
    PS > Get-DomainOU -Identity "Workstations" -Properties GPLink
    
    gplink
    ------    [LDAP://cn={ECB75201-82D7-49F3-A0E0-86788EE7DC36},cn=policies,cn=system,DC=testlab,DC=local;0][LDAP://cn={7DD7A136-334C-47C1-8890-D9766D449EFA},cn=policies,cn=system,DC=test...
    

但是我们可以这样做：

    
    
    PS > $GPLink = (Get-DomainOU -Identity "Workstations" -Properties GPLink).gplink
    PS > [Regex]::Matches($GPLink, '(?<={)(.*?)(?=})') | Select-Object -ExpandProperty Value | ForEach-Object { Get-DomainGPO -Identity "{$_}" -Properties DisplayName }
    
    displayname
    -----------    Demo GPO
    Workstation Policy
    

![](https://p2.ssl.qhimg.com/t019f24e66f5b213cd6.png)

在这些示例中，一些聪明的读者可能会注意到有些情况下通过继承(例如默认域策略)返回了包含的GPO，而有些情况则不返回。

## 继承

我发现继承非常有趣，特别是当涉及到控制委派向导时。默认情况下，它将启用该对象和所有子对象的继承。

![](https://p4.ssl.qhimg.com/t012dcb75b1fcbd3028.png)

    
    
    PS > Get-DomainOU | Get-DomainObjectAcl -ResolveGUIDs | Where-Object { $_.ObjectAceType -eq "GP-Link" }
    
    AceQualifier           : AccessAllowed
    ObjectDN               : OU=Workstations,DC=testlab,DC=local
    ActiveDirectoryRights  : ReadProperty, WriteProperty
    ObjectAceType          : GP-Link
    ObjectSID              :
    InheritanceFlags       : ContainerInherit     <---    BinaryLength           : 56
    AceType                : AccessAllowedObject
    ObjectAceFlags         : ObjectAceTypePresent
    IsCallback             : False
    PropagationFlags       : None
    SecurityIdentifier     : S-1-5-21-407754292-3742881058-3910138598-1106
    AccessMask             : 48
    AuditFlags             : None
    IsInherited            : False                <--- This OU *is not* inheriting from elsewhere
    AceFlags               : ContainerInherit     <---    InheritedObjectAceType : All
    OpaqueLength           : 0
    

如果我们在内部创建一个新的组织单元，LABDesktop Admins将继承相同的GP-Link权限。

    
    
    AceQualifier           : AccessAllowed
    ObjectDN               : OU=DAs,OU=Workstations,DC=testlab,DC=local     <--- DA OU is a child of Workstation OU
    ActiveDirectoryRights  : ReadProperty, WriteProperty
    ObjectAceType          : GP-Link
    ObjectSID              :
    InheritanceFlags       : ContainerInherit                <---    BinaryLength           : 56
    AceType                : AccessAllowedObject
    ObjectAceFlags         : ObjectAceTypePresent
    IsCallback             : False
    PropagationFlags       : None
    SecurityIdentifier     : S-1-5-21-407754292-3742881058-3910138598-1106
    AccessMask             : 48
    AuditFlags             : None
    IsInherited            : True                            <--- This OU *is* inheriting
    AceFlags               : ContainerInherit, Inherited     <---    InheritedObjectAceType : All
    OpaqueLength           : 0
    

如果我们只是手动将Workstations组织单元上的继承修改为这个对象，则新的ACL（访问控制列表, Access Control List）如下所示：

    
    
    AceQualifier           : AccessAllowed
    ObjectDN               : OU=Workstations,DC=testlab,DC=local
    ActiveDirectoryRights  : ReadProperty, WriteProperty
    ObjectAceType          : GP-Link
    ObjectSID              :
    InheritanceFlags       : None    <---    BinaryLength           : 56
    AceType                : AccessAllowedObject
    ObjectAceFlags         : ObjectAceTypePresent
    IsCallback             : False
    PropagationFlags       : None
    SecurityIdentifier     : S-1-5-21-407754292-3742881058-3910138598-1106
    AccessMask             : 48
    AuditFlags             : None
    IsInherited            : False    <---    AceFlags               : None     <---    InheritedObjectAceType : All
    OpaqueLength           : 0
    

![](https://p1.ssl.qhimg.com/t01e32f718502866855.png)

最后，如果有这样的嵌套子级：

![](https://p4.ssl.qhimg.com/t01ee553abff5b43b8c.png)

则DA组织单元将继Workstations和Admins。因此，我们有一个用于 LABDesktop
Admins的Workstations授权，以及一个用于LABTeam 2的Admins授权，DA组织单元将继承这两者。

    
    
    AceQualifier           : AccessAllowed
    ObjectDN               : OU=Workstations,DC=testlab,DC=local
    ActiveDirectoryRights  : ReadProperty, WriteProperty
    ObjectAceType          : GP-Link
    ObjectSID              :
    InheritanceFlags       : ContainerInherit
    BinaryLength           : 56
    AceType                : AccessAllowedObject
    ObjectAceFlags         : ObjectAceTypePresent
    IsCallback             : False
    PropagationFlags       : None
    SecurityIdentifier     : S-1-5-21-407754292-3742881058-3910138598-1106
    AccessMask             : 48
    AuditFlags             : None
    IsInherited            : False
    AceFlags               : ContainerInherit
    InheritedObjectAceType : All
    OpaqueLength           : 0
    
    AceQualifier           : AccessAllowed
    ObjectDN               : OU=Admins,OU=Workstations,DC=testlab,DC=local
    ActiveDirectoryRights  : ReadProperty, WriteProperty
    ObjectAceType          : GP-Link
    ObjectSID              :
    InheritanceFlags       : ContainerInherit
    BinaryLength           : 56
    AceType                : AccessAllowedObject
    ObjectAceFlags         : ObjectAceTypePresent
    IsCallback             : False
    PropagationFlags       : None
    SecurityIdentifier     : S-1-5-21-407754292-3742881058-3910138598-1110
    AccessMask             : 48
    AuditFlags             : None
    IsInherited            : False
    AceFlags               : ContainerInherit
    InheritedObjectAceType : All
    OpaqueLength           : 0
    
    AceQualifier           : AccessAllowed
    ObjectDN               : OU=Admins,OU=Workstations,DC=testlab,DC=local
    ActiveDirectoryRights  : ReadProperty, WriteProperty
    ObjectAceType          : GP-Link
    ObjectSID              :
    InheritanceFlags       : ContainerInherit
    BinaryLength           : 56
    AceType                : AccessAllowedObject
    ObjectAceFlags         : ObjectAceTypePresent
    IsCallback             : False
    PropagationFlags       : None
    SecurityIdentifier     : S-1-5-21-407754292-3742881058-3910138598-1106
    AccessMask             : 48
    AuditFlags             : None
    IsInherited            : True
    AceFlags               : ContainerInherit, Inherited
    InheritedObjectAceType : All
    OpaqueLength           : 0
    
    AceQualifier           : AccessAllowed
    ObjectDN               : OU=DAs,OU=Admins,OU=Workstations,DC=testlab,DC=local
    ActiveDirectoryRights  : ReadProperty, WriteProperty
    ObjectAceType          : GP-Link
    ObjectSID              :
    InheritanceFlags       : ContainerInherit
    BinaryLength           : 56
    AceType                : AccessAllowedObject
    ObjectAceFlags         : ObjectAceTypePresent
    IsCallback             : False
    PropagationFlags       : None
    SecurityIdentifier     : S-1-5-21-407754292-3742881058-3910138598-1110
    AccessMask             : 48
    AuditFlags             : None
    IsInherited            : True
    AceFlags               : ContainerInherit, Inherited
    InheritedObjectAceType : All
    OpaqueLength           : 0
    
    AceQualifier           : AccessAllowed
    ObjectDN               : OU=DAs,OU=Admins,OU=Workstations,DC=testlab,DC=local
    ActiveDirectoryRights  : ReadProperty, WriteProperty
    ObjectAceType          : GP-Link
    ObjectSID              :
    InheritanceFlags       : ContainerInherit
    BinaryLength           : 56
    AceType                : AccessAllowedObject
    ObjectAceFlags         : ObjectAceTypePresent
    IsCallback             : False
    PropagationFlags       : None
    SecurityIdentifier     : S-1-5-21-407754292-3742881058-3910138598-1106
    AccessMask             : 48
    AuditFlags             : None
    IsInherited            : True
    AceFlags               : ContainerInherit, Inherited
    InheritedObjectAceType : All
    OpaqueLength           : 0
    

![](https://p3.ssl.qhimg.com/t016be59a81b23252ae.png)

我觉得关于枚举的介绍已经够多了！接下来的文章，我们将从一些滥用开始。

本文翻译自rastamouse.me [原文链接](https://rastamouse.me/2019/01/gpo-abuse-part-1/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **yimeng** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/169289](/post/id/169289)

安全客 - 有思想的安全新媒体

本文转载自: [rastamouse.me](https://rastamouse.me/2019/01/gpo-abuse-part-1/)

如若转载,请注明出处： <https://rastamouse.me/2019/01/gpo-abuse-part-1/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Windows](/tag/Windows)
  * [活动目录](/tag/活动目录)
  * [GPO](/tag/GPO)

 **+1** __2赞

 __收藏

![](https://p3.ssl.qhimg.com/t016fefd8e565877ad5.png) yimeng

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

