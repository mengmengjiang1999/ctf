# 前言

当拿下域控权限时，为了维持权限，常常需要驻留一些后门，从而达到长期控制的目的。Windows
AD域后门五花八门，除了常规的的添加隐藏用户、启动项、计划任务、抓取登录时的密码，还有一些基于`ACL`的后门。

# ACL介绍

ACL是一个访问控制列表，是整个访问控制模型（ACM）的实现的总称。常说的ACL主要分为两类，分别为特定对象安全描述符的自由访问控制列表 (DACL)
和系统访问控制列表 (SACL)。对象的 DACL 和 SACL 都是访问控制条目 (ACE)
的集合，ACE控制着对象指定允许、拒绝或审计的访问权限，其中Deny拒绝优先于Allow允许。

[安全描述符](https://learn.microsoft.com/zh-cn/windows/desktop/SecGloss/s-gly)包含与[安全对象](https://learn.microsoft.com/zh-cn/windows/win32/secauthz/securable-objects)关联的安全信息。 安全描述符由
[SECURITY_DESCRIPTOR](https://learn.microsoft.com/zh-cn/windows/desktop/api/Winnt/ns-winnt-security_descriptor)结构和关联的安全信息组成。
安全描述符可以包含以下安全信息：：

1、对象所有者和主组[的安全标识符](https://learn.microsoft.com/zh-cn/windows/win32/secauthz/security-identifiers)(SID) 。

2、指定允许或拒绝特定用户或组的访问权限的 [DACL](https://learn.microsoft.com/zh-cn/windows/win32/secauthz/access-control-lists)。

3、一个 [SACL](https://learn.microsoft.com/zh-cn/windows/win32/secauthz/access-control-lists)，指定为对象生成审核记录的访问尝试的类型。

4、一组控制位，用于限定安全描述符或其单个成员的含义。

# 隐藏安全描述符

当可控一个用户时，不想该用户被轻易发现，可以对其进行隐藏。首先查看该用户所用者，默认是域管组：

![3a2d9490-6b84-48d6-a1f9-e02ad933161b](https://image.3001.net/images/20221207/1670376318_638feb7e2bef395bb66a3.jpeg!small)

可以在GUI上对所有者进行修改，也可以使用`powerview`进行修改：

    
    
    Set-DomainObjectOwner -identity jumbo -OwnerIdentity jumbo

修改完成后：

![a7f0c51c-abca-4b0b-b288-2218e633e8da](https://image.3001.net/images/20221207/1670376319_638feb7f530012d6e37ff.jpeg!small)

因为是权限维持，所以当前权限是域管，先尝试给域管添加一个对`jumbo`用户`Deny`所有权限的ACL，但是发现`powerview`的`Add-DomainObjectAcl`方法并没有设置`Deny`权限的操作，只有`Allow`：

![image-20221203165731119](https://image.3001.net/images/20221207/1670376320_638feb8069e20d95f1f3a.png!small)

当然，你可以使用`New-ADObjectAccessControlEntry`来完成手动ACL的添加，他的原理如下图：

![image-20221203165922392](https://image.3001.net/images/20221207/1670376321_638feb81afedecf6c7d7d.png!small)

上图看出还要手动做最后的ACL保存。既然`Add-DomainObjectAcl`已经完成了自动化的`CommitChanges`，直接把`Allow`默认可变的参数不就行了？首先手动在`Add-DomainObjectAcl`添加一个`AccessControlType`参数：

    
    
    .PARAMETER AccessControlType  
    ​  
    Specifies the type of ACE (allow or deny)

![image-20221203170302148](https://image.3001.net/images/20221207/1670376323_638feb830f874e93335bf.png!small)

设置参数定义：

    
    
    [Parameter(Mandatory = $True, ParameterSetName='AccessRuleType')]  
    [ValidateSet('Allow', 'Deny')]  
    [String[]]  
    $AccessControlType,

![image-20221203170313999](https://image.3001.net/images/20221207/1670376324_638feb845805d359c69af.png!small)

删除之前的默认的`Allow`：

![image-20221203170641601](https://image.3001.net/images/20221207/1670376325_638feb859c8a079316709.png!small)

最后把`AccessControlType`参数替换之前的`ControlType`：

![image-20221203170738348](https://image.3001.net/images/20221207/1670376326_638feb86cce60569a6a68.png!small)

现在就可以在使用`AccessControlType`参数来给对象添加`Allow`或者`Deny`的权限了。

【----帮助网安学习，以下所有学习资料免费领！加vx：yj009991，备注“freebuf”获取！】

① 网安学习成长路径思维导图  
② 60+网安经典常用工具包  
③ 100+SRC漏洞分析报告  
④ 150+网安攻防实战技术电子书  
⑤ 最权威CISSP 认证考试指南+题库  
⑥ 超1800页CTF实战技巧手册  
⑦ 最新网安大厂面试题合集（含答案）  
⑧ APP客户端安全检测指南（安卓+IOS）

当尝试域管添加一个对`jumbo`用户`Deny`所有权限的ACL后：

    
    
    Add-DomainObjectAcl -TargetIdentity jumbo -PrincipalIdentity S-1-5-21-12312321-1231312-123123-500 -AccessControlType Deny

![871e59ae-a6bb-4e4a-83c9-bd01800bba33](https://image.3001.net/images/20221207/1670376328_638feb8820bc9c818e00c.jpeg!small)

当然，把`SID`改成`SamAccountName`也是可以的：

    
    
    Add-DomainObjectAcl -TargetIdentity jumbo -PrincipalIdentity administrator -AccessControlType Deny

可以发现域管也没权限查看`jumbo`用户的属性了：

![WKtY1zjGss](https://image.3001.net/images/20221207/1670376329_638feb895bd7c3e5394d6.jpg!small)

![J3Qsrfsyl0](https://image.3001.net/images/20221207/1670376330_638feb8a9543d988bd6c1.jpg!small)

当使用`system`用户查看`jumbo`用户ACL时，可以看到对应的`Deny`的ACL：

![cccac477-019c-4600-8678-124461d8fb96](https://image.3001.net/images/20221207/1670376331_638feb8be34f8efb862ce.jpeg!small)

现在域管对`jumbo`用户已经无法操作任何东西了，先用`system`用户删除该`Deny`权限，准备使用`powerview`的`Remove-DomainObjectAcl`方法时，发现也只有的`Allow`，也就是默认只能移除对象的`Allow`权限，老方法，把删除的ACL属性设置为可变参数：

![image-20221203171520243](https://image.3001.net/images/20221207/1670376333_638feb8d2b085b3f68573.png!small)

![image-20221203171530075](https://image.3001.net/images/20221207/1670376334_638feb8e7b2ec8698db98.png!small)

![image-20221203171559987](https://image.3001.net/images/20221207/1670376335_638feb8fd6281c1a36d73.png!small)

![image-20221203171546945](https://image.3001.net/images/20221207/1670376337_638feb9128b10aafa2712.png!small)

进行删除：

    
    
    Remove-DomainObjectAcl -TargetIdentity jumbo -PrincipalIdentity S-1-5-21-12312321-1231312-123123-500 -Rights ALL -AccessControlType Deny

当然，把`SID`改成`SamAccountName`也是可以的：

    
    
    Remove-DomainObjectAcl -TargetIdentity jumbo -PrincipalIdentity administrator -Rights ALL -AccessControlType Deny

![67ee14b5-46a7-44a7-81ea-57eaed22c0b5](https://image.3001.net/images/20221207/1670376338_638feb9269cb468660473.jpeg!small)

那么同学们可能会想，如果真的有人进行了上面操作，真的没办法查看了吗，实际上并不是，对象的拥有者是有权限修改的，比如把`jumbo`用户的拥有者改成默认的域管组，然后对域管进行设置`Deny`的ACL，但是实际上拥有者依然有权限修改其ACL，这也是为什么在文章开始的时候，要把`jumbo`拥有者设置为`jumbo`的目的：

![image-20221203172330615](https://image.3001.net/images/20221207/1670376339_638feb9395861dd9f991f.png!small)

上面尝试了拒绝域管对`jumbo`所有的权限，那为了隐藏，并且为了防止后续还要对`jumbo`用户的一些其他修改，实际上可以对`jumbo`用户设置`everyone`拒绝读取的权限即可：

![8f23c0b4-e7e9-4f55-9c30-8abbc2a86f09](https://image.3001.net/images/20221207/1670376340_638feb94e5db554e86a21.jpeg!small)

现在所有用户对其都没有查看权限了：

![WKtY1zjGss](https://image.3001.net/images/20221207/1670376341_638feb95db371b3241cfd.jpg!small)

当然，只是设置了拒绝读取权限，实际上当域管去修改其ACL权限时，还是可以的：

![image-20221203173141621](https://image.3001.net/images/20221207/1670376343_638feb97424fe64aeb1b7.png!small)

现在通过`net user`命令已经看不到`jumbo`这个用户了：

![image-20221203173434064](https://image.3001.net/images/20221207/1670376344_638feb987954e4b638572.png!small)

在“用户和计算机”里看用户长这样：

![image-20221203173508632](https://image.3001.net/images/20221207/1670376345_638feb99b8c8e7a5a417d.png!small)

从上面的操作可以发现，给`everyone`用户添加拒绝读取权限时是通过GUI实现的，因为`everyone`用户是个特殊的用户，属于[特殊身份群体](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/understand-special-identities-groups#everyone)，是一个属于[Well-known SIDs](https://learn.microsoft.com/en-us/windows/win32/secauthz/well-known-sids)的用户，其对应的SID为`S-1-1-0`：

![image-20221203194510264](https://image.3001.net/images/20221207/1670376346_638feb9ad2bede8eaa2b5.png!small)

当尝试使用`powerview`的`Add-DomainObjectAcl`方法是无法完成给`everyone`用户添加ACL的：

![07fc0328-3a8b-46b7-b245-b0449ef29533](https://image.3001.net/images/20221207/1670376348_638feb9c7e5f3f76a7b59.jpeg!small)

通过查看`powerview`的代码，会通过`Get-ObjectAcl`方法获取对应用户的SID，但是刚刚提到，`everyone`用户是个特殊的用户，导致查不到：

![image-20221203194829686](https://image.3001.net/images/20221207/1670376350_638feb9e40d2963bb6c9e.png!small)

但是看了下还有个`New-ADObjectAccessControlEntry`方法，会判断输入的`PrincipalIdentity`参数是不是`SID`，如果是`SID`就不走查询，因此可以照葫芦画瓢，把这个判断加到`Add-DomainObjectAcl`方法中：

    
    
          if ($PrincipalIdentity -notmatch '^S-1-.*') {  
              $PrincipalSearcherArguments = @{  
                  'Identity' = $PrincipalIdentity  
                  'Properties' = 'distinguishedname,objectsid'  
              }  
              if ($PSBoundParameters['PrincipalDomain']) { $PrincipalSearcherArguments['Domain'] = $PrincipalDomain }  
              if ($PSBoundParameters['Server']) { $PrincipalSearcherArguments['Server'] = $Server }  
              if ($PSBoundParameters['SearchScope']) { $PrincipalSearcherArguments['SearchScope'] = $SearchScope }  
              if ($PSBoundParameters['ResultPageSize']) { $PrincipalSearcherArguments['ResultPageSize'] = $ResultPageSize }  
              if ($PSBoundParameters['ServerTimeLimit']) { $PrincipalSearcherArguments['ServerTimeLimit'] = $ServerTimeLimit }  
              if ($PSBoundParameters['Tombstone']) { $PrincipalSearcherArguments['Tombstone'] = $Tombstone }  
              if ($PSBoundParameters['Credential']) { $PrincipalSearcherArguments['Credential'] = $Credential }  
              $Principal = Get-DomainObject @PrincipalSearcherArguments  
              if (-not $Principal) {  
                  throw "Unable to resolve principal: $PrincipalIdentity"  
              }  
              elseif($Principal.Count -gt 1) {  
                  throw "PrincipalIdentity matches multiple AD objects, but only one is allowed"  
              }  
              $ObjectSid = $Principal.objectsid  
              Write-Host ($ObjectSid)  
          }  
          else {  
              Write-Host "..sid.."  
              $ObjectSid = $PrincipalIdentity  
          }
    
    
                  $Identity = [System.Security.Principal.IdentityReference] ([System.Security.Principal.SecurityIdentifier]$ObjectSid)  
    ​

现在尝试下，给`jumbo2`用户添加`everyone`所有拒绝的ACL：

    
    
    Add-DomainObjectAcl -TargetIdentity jumbo2 -PrincipalIdentity S-1-1-0 -Rights All -AccessControlType Deny

![image-20221203223418355](https://image.3001.net/images/20221207/1670376352_638feba012832cffb45e9.png!small)

![image-20221203223515329](https://image.3001.net/images/20221207/1670376353_638feba1a98aed2f0ffac.png!small)

`Remove-DomainObjectAcl`方法同理。

# 隐藏主体

通过上面的步骤，除了`jumbo`用户本身可以查看`jumbo`用户以为，其他用户都没有`ReadControl`权限，但是在“Active
Directory用户和计算机管理”里还是可以看到，虽然`ico`图标都没了，接下来要让在“Active
Directory用户和计算机管理”里也看不到。为了方便演示，笔者把`jumbo`用户移到一个单独的`OU`组里：

![image-20221203174836127](https://image.3001.net/images/20221207/1670376355_638feba31457d7b803442.png!small)

然后给这个`OU`设置`everyone`拒绝读取权限即可：

![image-20221203174920757](https://image.3001.net/images/20221207/1670376356_638feba424335b53fabdb.png!small)

![image-20221203174956407](https://image.3001.net/images/20221207/1670376357_638feba5bc313b58ba662.png!small)

遇到一些粗心大意的管理员，可能会觉得这只是无意残留的无害物质，无伤大雅。

# Dcsync

`Dcsync`实际上就是给用户设置两条扩展权限，分别为：

    
    
    DS-Replication-Get-Changes (GUID: 1131f6aa-9c07-11d1-f79f-00c04fc2dcd2)  
    DS-Replication-Get-Changes-All (GUID: 1131f6ad-9c07-11d1-f79f-00c04fc2dcd2)

当用户拥有这两条ACL后，即可使用`DRS`协议获取域`hash`凭据。给用户在域对象上添加`Dcsync`权限即可：

![image-20221203180529979](https://image.3001.net/images/20221207/1670376359_638feba70b6772f791ac8.png!small)

# 代理账号

上面提到，把`jumbo`用户拥有者改成自身，然后设置`everyone`对其没有读取权限，这样就可以达到隐藏`jumbo`，然后手上的`jumbo`用户就可以肆无忌惮的做一些操作。但是有个问题，万一做操作的时候，该用户被发现了，管理员把该用户进行了禁用，那好不容易获取到的账号就废了。为了防止账号被发现后被禁用/被改密码不可用，应该设置个代理账号，把准备拿来攻击的账号（某个管理员用户或者有`dcsync`类似权限的账号）的拥有者设置代理账号，代理账号是其拥有所有者，然后设置所有用户对攻击账号都不可操作，最后每次都可以使用代理账号控制攻击账号，就算攻击账号被禁用/被改密码，也可以使用代理账号来重新启用他。

首先攻击账号为`attack`，代理账号为`good`，首先设置`attack`账号所有者为`good`：

    
    
    Set-DomainObjectOwner -identity attack -OwnerIdentity good

![image-20221203225649767](https://image.3001.net/images/20221207/1670376360_638feba833fffb71e735f.png!small)

给`attack`账号添加`dcsync`权限：

    
    
    Add-DomainObjectAcl -TargetIdentity "DC=domain,DC=com" -PrincipalIdentity attack -Rights DCSync -AccessControlType Allow

![image-20221203230454614](https://image.3001.net/images/20221207/1670376361_638feba987351f010cdea.png!small)

设置`attack`都不可操作：

    
    
    Add-DomainObjectAcl -TargetIdentity attack -PrincipalIdentity S-1-1-0 -Rights All -AccessControlType Deny

这个时候，如果`attack`在发起攻击的时候被管理员发现了，把`attack`账号密码重置了，但是`good`账号是`attack`账号的拥有者，可以修改`attack`账号的`ACL`，比如给自己添加修改密码的权限，然后去重置`attack`账号的密码，然后就又可以拿来攻击了。

# 总结

本文主要讲了在`Windows`域中如何利用`ACL`进行后门隐藏，并对`powerview`进行修改使其支持在添加`ACL`或者删除`ACL`时可以指定`Allow`或者`Deny`，也可以选择`everyone`此类特殊用户。

 **更多网安技能的在线实操练习，[请点击这里>>](https://www.hetianlab.com/)**

