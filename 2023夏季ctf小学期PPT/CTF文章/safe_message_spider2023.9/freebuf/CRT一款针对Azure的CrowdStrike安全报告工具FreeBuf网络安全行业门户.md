![](https://image.3001.net/images/20220211/1644512840_620546488425214d575e9.png!small)  

## 关于CRT

CRT全称为“CrowdStrike Reporting Tool for
Azure”，是一款针对Azure的CrowdStrike安全报告工具。该工具会在Azure AD/O365
租户中查询以下配置，并帮助广大研究人员寻找一些跟权限和配置有关的安全信息，以帮助组织更好地保护Azure环境的安全性。

## 功能介绍

### Exchange Online（O365）

> Federation配置
>
> Federation Trust
>
> 邮箱上配置的客户端访问设置
>
> 远程域的邮件转发规则
>
> 邮箱SMTP转发规则
>
> 邮件发送规则
>
> 授予“完全访问”权限的代理
>
> 授予任意权限的代理
>
> 具有“发送方式”或“发送代表”权限的代理
>
> 启用Exchange Online PowerShell的用户
>
> 启用“Audit Bypass”的用户
>
> 从全局地址列表（GAL）中隐藏的邮箱
>
> 收集管理员审核日志记录配置设置

### Azure AD

> 拥有KeyCredentials的服务主体对象
>
> O365管理员组报告
>
> 代理权限和应用程序权限

查询租户合作伙伴信息：要查看租户合作伙伴信息，包括分配给合作伙伴的角色，则必须以全局管理员身份登录Microsoft 365管理中心：【 _传送门_】。

## 工具要求

该工具的正常运行需要下列PowerShell模块，CRT会自动完成依赖组件的安装：

> ExchangeOnlineManagement
>
> AzureAD

注意：要返回所查询配置的完整范围，还需要以下角色：

> 全局管理员（Global Admin）

当全局管理员权限不可用时，该工具将通知你哪些信息将因此而不可用。

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/CrowdStrike/CRT.git

## 工具使用

如果没有指定运行参数的话，工具将在运行脚本的目录中自动创建名为日期和时间（YYYYDDMMTHHMM）的文件夹。默认身份验证方法将提示每个连接是否与MFA兼容。

    
    
    .\Get-CRTReport.ps1

-BasicAuth参数：[可选]如果用户主体未强制使用MFA，则可以使用此参数，该参数将仅提示一次身份验证，并使用Get-Credential存储凭据。（不推荐）
    
    
    .\Get-CRTReport.ps1 -BasicAuth

-JobName参数：[可选]使用JobName参数区分不同租户。如果未指定JobName，则将在工作目录中生成一个日期/时间格式的文件夹。
    
    
    .\Get-CRTReport.ps1 -JobName MyJobName

-WorkingDirectory参数：[可选]如果要为Job指定不同的工作目录，可以使用此参数。默认工作目录是运行脚本的目录。
    
    
    .\Get-CRTReport.ps1 -JobName MyJobName -WorkingDirectory 'C:\Path\to\Job\Folder'

-Commands参数：[可选]使用此参数，可以指定需要以引号、逗号或空格分隔的形式运行的特定命令。
    
    
    .\Get-CRTReport.ps1 -JobName MyJobName -WorkingDirectory 'C:\Path\to\Job\Folder' -Commands "Command1,Command2"

-AzureEnvironmentName&-ExchangeEnvironmentName参数：[可选]使用此参数，指定Azure或Exchange环境名称。使用Tab键补全可以查看支持的可选值。
    
    
    .\Get-CRTReport.ps1 -ExchangeEnvironmentName O365USGovGCCHigh -AzureEnvironmentName AzureUSGovernment

-Interactive参数：[可选]根据租户中的数据量，某些命令可能需要很长时间才能处理完成。使用Interactive参数，我们可以选择在模块运行之前跳过任何特定命令。
    
    
    .\Get-CRTReport.ps1 -JobName MyJobName -WorkingDirectory 'C:\Path\to\Job\Folder' -Interactive

### 可用的命令

    
    
    FedConfig
    
    FedTrust
    
    ClientAccess
    
    RemoteDomains
    
    SMTPForward
    
    TransportRules
    
    FullAccessGranted
    
    AnyAccessGranted
    
    SendAsGranted
    
    EXOPowerShell
    
    AuditBypassEnabled
    
    HiddenMailboxes
    
    KeyCredentials
    
    O365AdminGroups
    
    DelegateAppPerms
    
    AdminAuditLogConfig

## 项目地址

 **CRT：** 【[ _GitHub传送门_](https://github.com/CrowdStrike/CRT)】

## 参考资料

[
_https://admin.microsoft.com/AdminPortal/Home#/partners_](https://admin.microsoft.com/AdminPortal/Home#/partners)

