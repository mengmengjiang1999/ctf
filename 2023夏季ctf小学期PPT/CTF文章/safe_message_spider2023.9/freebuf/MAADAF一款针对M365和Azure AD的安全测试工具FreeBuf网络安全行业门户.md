![](https://image.3001.net/images/20230803/1691077660_64cbcc1cc13f8602c9159.png!small)

## 关于MAAD-AF

MAAD-AF是一款针对开源云安全的测试工具，该工具旨在通过执行各种攻击方法来帮助广大研究人员测试M365和Azure AD的安全性。MAAD-AF为安全从业者提供了易于使用的攻击模块，以利用M365和Azure AD环境中的各种错误配置以及安全问题。

MAAD-AF旨在使云安全测试变得简单、快速和有效。通过其几乎无需设置和易于使用的交互式攻击模块，安全团队可以轻松快速地测试其安全控制、检测和响应能力。

## 功能介绍

> 1、实现了安全测试/后渗透测试技术；
>
> 2、简单易用的交互式操作；
>
> 3、不需要任何设置；
>
> 4、实现了针对Azure AD的攻击测试模块；
>
> 5、实现了针对Exchange的攻击测试模块；
>
> 6、实现了针对Teams的攻击测试模块；
>
> 7、实现了针对SharePoint的攻击测试模块；
>
> 8、实现了针对eDiscovery的攻击测试模块；

## MAAD-AF攻击模块

> 1、Azure AD外部网络侦查（包括子模块）
>
> 2、Azure AD内部网络侦查（包括子模块）
>
> 3、后门帐户设置
>
> 4、受信任的网络修改
>
> 5、禁用邮箱审核
>
> 6、禁用反网络钓鱼
>
> 7、邮箱删除规则设置
>
> 8、通过邮箱转发实现数据提取
>
> 9、获得用户邮箱访问权限
>
> 10、外部团队访问设置（包括子模块）
>
> 11、跨租户同步利用漏洞（包括子模块）
>
> 12、eDiscovery漏洞利用（包括子模块）
>
> 13、暴力破解
>
> 14、MFA篡改
>
> 15、用户账户删除
>
> 16、SharePoint漏洞利用（包括子模块）

## 工具机制&架构

![](https://image.3001.net/images/20230803/1691077685_64cbcc35255cab8961f8a.png!small)

## 工具要求

> 1、一台联网的Windows主机；
>
> 2、PowerShell v5+（以管理员权限运行）；
>
> 3、安装好下列PowerShell模块：
>
>   * [Az](https://www.powershellgallery.com/packages/Az/)
>   * [AzureAd](https://www.powershellgallery.com/packages/AzureAD/)
>   * [MSOnline](https://www.powershellgallery.com/packages/MSOnline/)
>   *
> [ExchangeOnlineManagement](https://www.powershellgallery.com/packages/ExchangeOnlineManagement/)
>   *
> [MicrosoftTeams](https://www.powershellgallery.com/packages/MicrosoftTeams/)
>   *
> [AzureADPreview](https://www.powershellgallery.com/packages/AzureADPreview/)
>   * [ADInternals](https://aadinternals.com/aadinternals/)
>   *
> [ExchangePowershell](https://www.powershellgallery.com/packages/ExchangeOnlineManagement/3.0.0)
>   *
> [Microsoft.Online.SharePoint.PowerShell](https://www.powershellgallery.com/packages/Microsoft.Online.SharePoint.PowerShell/16.0.23311.12000)
>   * [PnP.PowerShell](https://github.com/pnp/powershell)
>   *
> [Microsoft.Graph.Identity.SignIns](https://www.powershellgallery.com/packages/Microsoft.Graph.Identity.SignIns/2.0.0-rc3)
>

## 工具限制

当前版本的MAAD-AF仅支持Windows操作系统。

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/vectra-ai-research/MAAD-AF.git

## 工具使用

该工具的使用非常简单，“即插即用”。

首先，我们需要以管理员权限运行PowerShell，然后切换到本地的MAAD-AF目录中：

    
    
    cd /MAAD-AF

然后使用下列命令运行MAAD_Attack.ps1脚本即可：

    
    
    ./MAAD_Attack.ps1

## 许可证协议

本项目的开发与发布遵循[ _GPL_ _-3.0_](https://github.com/vectra-ai-research/MAAD-AF/blob/main/LICENSE.md)开源许可证协议。

## 项目地址

 **MAAD-AF** ：【[ _GitHub传送门_](https://github.com/vectra-ai-research/MAAD-AF)】

