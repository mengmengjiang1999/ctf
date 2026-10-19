![](https://image.3001.net/images/20230718/1689649633_64b601e1ce3f87f02b93f.jpg!small)  

## 关于Azure-AccessPermissions

Azure-AccessPermissions是一款功能强大且易于使用的PowerShell脚本，在该工具的帮助下，广大研究人员可以快速枚举目标Azure活动目录环境中的访问权限。

## 工具要求

在使用该脚本之前，我们还需要安装并配置好下列PowerShell模块：

> [ _Microsoft.Graph_](https://github.com/microsoftgraph/msgraph-sdk-> powershell)
>
> [ _AADInternals_](https://github.com/Gerenios/AADInternals)
>
> [ _AzureADPreview_](https://learn.microsoft.com/en-> us/powershell/azure/active-directory/install-adv2?view=azureadps-2.0)

上述的PowerShell组件都可以使用下列命令轻松完成直接安装：

    
    
    PS:> Install-Module Microsoft.Graph
    
    PS:> Install-Module AADInternals
    
    PS:> Install-Module AzureADPreview

## 工具下载

该工具基于纯PowerShell开发，因此我们只能在支持PowerShell脚本运行的设备环境中使用Azure-AccessPermissions。

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/csandker/Azure-AccessPermissions.git

## 工具使用

### 首次使用

该工具使用了基于浏览器的UI界面来帮助广大研究人员与Azure建立连接。如果你是首次使用Azure-AccessPermissions，则可能会遇到如下所示的错误信息：

    
    
    [*] Connecting to Microsoft Graph...
    
    WARNING: WebBrowser control emulation not set for PowerShell or PowerShell ISE!
    
    Would you like set the emulation to IE 11? Otherwise the login form may not work! (Y/N): Y
    
    Emulation set. Restart PowerShell/ISE!

这个问题的解决也非常简单，只需要允许PowerShell枚举浏览器并返回你的命令即可。

## 工具使用样例

导入并运行脚本即可，无需使用其他的命令参数。

注意：当你第一次运行该工具时，可能需要完成两次身份验证，一次是Microsoft Graph，另一次是Azure AD Graph：

    
    
    PS:> Import-Module .\Azure-AccessPermissions.ps1

## 工具输出样例

![](https://image.3001.net/images/20230718/1689649727_64b6023f8932f88f33958.png!small)![](https://image.3001.net/images/20230718/1689649735_64b6024755fbb57d202f9.png!small)

## 项目地址

 **Azure-AccessPermissions** ：【[
_GitHub传送门_](https://github.com/csandker/Azure-AccessPermissions)】

## 参考资料

> [ _https://csandker.io/2022/10/19/Untangling-Azure-> Permissions.html_](https://csandker.io/2022/10/19/Untangling-Azure-> Permissions.html)
>
> [ _https://csandker.io/2022/11/10/Untangling-Azure-II-Privileged-> Access.html_](https://csandker.io/2022/11/10/Untangling-Azure-II-Privileged-> Access.html)
>
> [ _https://github.com/microsoftgraph/msgraph-sdk-> powershell_](https://github.com/microsoftgraph/msgraph-sdk-powershell)
>
> [
> _https://github.com/Gerenios/AADInternals_](https://github.com/Gerenios/AADInternals)
>
> [ _https://learn.microsoft.com/en-us/powershell/azure/active-> directory/install-adv2?view=azureadps-2.0_](https://learn.microsoft.com/en-> us/powershell/azure/active-directory/install-adv2?view=azureadps-2.0)

