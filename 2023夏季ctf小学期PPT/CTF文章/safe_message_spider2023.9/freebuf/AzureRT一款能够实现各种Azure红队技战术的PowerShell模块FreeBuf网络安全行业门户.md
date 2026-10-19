![](https://image.3001.net/images/20220623/1655975193_62b42d197451986ea5d9f.png!small)

## 关于AzureRT

AzureRT是一款能够实现各种Azure红队技战术的PowerShell模块，在AzureRT的帮助下，广大研究人员可以从攻击者的角度来与Azure和Azure
AD进行交互，以此来测试目标环境的安全性。

AzureRT可以帮助广大研究人员测试和处理基于访问令牌的身份验证，从Az切换到AzureAD和Az命令行接口界面，并提供了各种渗透测试技术，例如基于Runbook的命令执行等。

## 使用场景

> 1、测试Az、AzureAD访问令牌安全；
>
> 2、测试Az、AzureAD、Microsoft.Gragh和Az命令行接口身份认证上下文；
>
> 3、查看目标Azure VM上授权用户的可用权限；
>
> 4、查看可访问的Azure资源以及我们对其拥有的权限；
>
> 5、轻松读取所有可访问的Azure Key Vault敏感信息；
>
> 6、作为服务主体进行身份验证，以利用分配给该服务主体的特权角色；
>
> 7、通过恶意Runbook对Azure Automation执行攻击，以测试其安全性；

## 工具安装与配置

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/mgeeky/AzureRT.git

该工具基于PowerShell Az和AzureAD模块实现其功能、Microsoft.Gragh和Az
cli是可选项。在使用该工具之前，请使用下列命令确保环境安装正确：

    
    
    Install-Module Az -Force -Confirm -AllowClobber -Scope CurrentUser
    
    Install-Module AzureAD -Force -Confirm -AllowClobber -Scope CurrentUser
    
    Install-Module Microsoft.Graph -Force -Confirm -AllowClobber -Scope CurrentUser # OPTIONAL
    
    Install-Module MSOnline -Force -Confirm -AllowClobber -Scope CurrentUser        # OPTIONAL
    
    Install-Module AzureADPreview -Force -Confirm -AllowClobber -Scope CurrentUser  # OPTIONAL
    
    Install-Module AADInternals -Force -Confirm -AllowClobber -Scope CurrentUser    # OPTIONAL
    
     
    
    Import-Module Az
    
    Import-Module AzureAD

接下来，我们可以使用下列命令加载工具模块：

    
    
    PS> . .\AzureRT.ps1

或者，我们也可以让AzureRT来安装和导入所有的依赖组件：

    
    
    PS> . .\AzureRT.ps1
    
    PS> Import-ARTModules

## 功能模块

### 权限提升

> Add-ARTADGuestUser - 发送Azure AD来宾用户邀请邮件，可以提权获取到AAD租户的访问权限，并返回兑换邀请链接的URL地址；
>
> Set-ARTADUserPassword - 利用身份验证管理员角色分配来重置其他非管理员用户的密码；
>
> Add-ARTUserToGroup - 将指定的Azure AD用户添加到指定的Azure AD组；
>
> Add-ARTUserToRole - 将指定的Azure AD用户添加到指定的Azure AD角色；
>
> Add-ARTADAppSecret - 将客户端敏感信息添加到Azure AD应用程序；

### 横向渗透

> Invoke-ARTAutomationRunbook -> 在指定的Automation账户下并针对选定的Worker组创建自动化；Runbook。该Runbook将包含要在目标Azure
> VM上执行的Powershell命令；
>
> Invoke-ARTRunCommand - 对指定的Azure
> VM利用VirtualMachine/runCommand权限以运行自定义Powershell命令；
>
> Update-ARTAzVMUserData - 通过直接API调用修改Azure VM用户数据脚本；
>
> Invoke-ARTCustomScriptExtension - 创建新的或修改Azure VM自定义脚本扩展，从而实现远程代码执行；

### 侦察模块

> Get-ARTAccess - 执行Azure识别与态势感知；
>
> Get-ARTADAccess - 执行Azure AD识别与态势感知；
>
> Get-ARTDangerousPermissions - 分析可访问的Azure资源和用户对其拥有的相关权限，以查找可能被攻击者滥用的所有危险资源；
>
> Get-ARTRoleAssignment - 显示分配给当前使用主体的Azure RBAC角色；

## 许可证协议

本项目的开发与发布遵循[
_MIT_](https://github.com/mgeeky/AzureRT/blob/master/LICENSE)开源许可证协议。

## 项目地址

 **AzureRT：** 【[ _GitHub传送门_](https://github.com/mgeeky/AzureRT)】

## 参考资料

> [ _https://graph.microsoft.com/_](https://graph.microsoft.com/)
>
> [ _https://management.azure.com/_](https://management.azure.com/)
>
> [ _https://vault.azure.net/_](https://vault.azure.net/)

