![](https://image.3001.net/images/20221220/1671530503_63a188073ac19ef724cd0.png!small)

## 关于AzureGraph

AzureGraph是一款针对Azure活动目录的信息收集工具，该工具基于Microsoft Graph实现其功能。多亏了Microsoft
Graph技术，AzureGraph才能从Azure活动目录获取各种信息，如用户、设备、应用程序、域等。

此应用程序允许我们通过PowerShell终端以简单易行的方式通过API查询此数据。除此之外，我们还可以从云端下载所有信息，并完全离线使用。

## 工具要求

> PowerShell 4.0 +

## 工具下载

广大研究人员可以直接使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/JoelGMSec/AzureGraph

## 工具使用

    
    
    .\AzureGraph.ps1 -h
    
     
    
         _                         ____                 _
    
        / \    _____   _ _ __ ___ / ___|_ __ __ _ _ __ | |__
    
       / _ \  |_  / | | | '__/ _ \ |  _| '__/ _' | '_ \| '_ \
    
      / ___ \  / /| |_| | | |  __/ |_| | | | (_| | |_) | | | |
    
     /_/   \_\/___|\__,_|_|  \___|\____|_|  \__,_| .__/|_| |_|
    
                                                 |_|
    
      -------------------- by @JoelGMSec --------------------    
     
    
     
    
     Info:  This tool helps you to obtain information from Azure AD
    
            like Users or Devices, using de Microsft Graph REST API
    
     
    
     Usage: .\AzureGraph.ps1 -h
    
             显示工具帮助信息
    
     
    
            .\AzureGraph.ps1
    
             以完整交互模式运行AzureGraph
    
     
    
     Warning: 在使用该工具之前，请先生成Microsoft Graph令牌

## 如何获取Microsoft Graph令牌？

为了能够使用MS Graph API，我们需要一个身份验证令牌。为了实现这一目标，我们可以以三种不同的方式生成：

> 1、使用浏览器或CURL并通过[ _MS_ __ _Graph官方网站_](https://developer.microsoft.com/en-> us/graph/graph-explorer)获取；
>
> 2、使用AzureGraph输入Azure凭证；
>
> 3、通过其他方式获得刷新令牌；

![](https://image.3001.net/images/20221220/1671530537_63a188297a3c3fa41397e.png!small)

对于第一种情况，令牌将出现在“访问令牌”选项卡上，我们随后将其输入工具以与该服务交互。该系统的唯一问题是令牌的寿命不是很长，因此建议利用该时间窗口下载所有信息，并以完全离线的方式处理这些信息。

对于第二种情况，我们将需要使用租户ID、通过Azure访问它的权限以及相关用户的凭据。

对于第三种情况，这是一件更复杂的事情，因为我们需要用有效的令牌拦截客户端和服务器之间的请求，以获得所需的“刷新令牌”。这个方法的好处是它永远不会过期，因为它的功能是定期创建新的令牌。

## 工具使用演示

![](https://image.3001.net/images/20221220/1671530546_63a188327504d966c3e04.png!small)

正如你所看到的，该工具的使用非常简单，该工具支持通过菜单进行交互式访问，并使用小键盘上下键移动或回车选择功能：

![](https://image.3001.net/images/20221220/1671530553_63a188393f11988eae55a.png!small)

选择第一项后，我们将看到下列三种认证方式：

![](https://image.3001.net/images/20221220/1671530560_63a1884075a7108d6c15d.png!small)

接下来，我们就可以开始查询相关信息了，比如说，我们可以使用特定的过滤器或参数来查询所有信息：

![](https://image.3001.net/images/20221220/1671530567_63a1884778b4da8cf009e.png!small)

下图显示的是所有可用的信息：

![](https://image.3001.net/images/20221220/1671530573_63a1884da7d9d4e5ce76f.png!small)

在执行任何操作时，我们都可以按下“退格”键返回主菜单，下面给出的是该工具所有支持查询的数据：

> 1、用户
>
> 2、用户组
>
> 3、设备
>
> 4、服务
>
> 5、应用
>
> 6、组织
>
> 7、域

我们还可以使用菜单上的最后一个选项完全自动下载上述所有信息。这样做的好处就是能够以离线的形式处理所有信息：

![](https://image.3001.net/images/20221220/1671530584_63a188580700305beaaa2.png!small)

## 许可证协议

本项目的开发与发布遵循[ _GPL_
_-3.0_](https://github.com/JoelGMSec/AzureGraph/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **AzureGraph** ：【[ _GitHub传送门_](https://github.com/JoelGMSec/AzureGraph)】

## 参考资料

> [ _https://developer.microsoft.com/en-us/graph/graph-> explorer_](https://developer.microsoft.com/en-us/graph/graph-explorer)
>
> [ _https://azure.microsoft.com/_](https://azure.microsoft.com/)
>
> [ _https://azure.microsoft.com/en-us/products/active-> directory_](https://azure.microsoft.com/en-us/products/active-directory)
>
> [
> _https://github.com/BloodHoundAD/AzureHound_](https://github.com/BloodHoundAD/AzureHound)
>
> [
> _https://github.com/hausec/PowerZure_](https://github.com/hausec/PowerZure)
>
> [
> _https://github.com/Gerenios/AADInternals_](https://github.com/Gerenios/AADInternals)
>
> [ _https://learn.microsoft.com/en-> us/graph/overview_](https://learn.microsoft.com/en-us/graph/overview)
>
> [ _https://learn.microsoft.com/en-us/sharepoint/find-your-office-365-tenant-> id_](https://learn.microsoft.com/en-us/sharepoint/find-your-> office-365-tenant-id)

