![](https://image.3001.net/images/20201031/1604158931_5f9d85d3b604a4d03eac1.png!small)

## PSMDATP

PSMDATP是一款针对Microsoft Defender
ATP的PowerShell管理模块，这个工具本质上来说是一个易于使用的命令行工具，广大研究人员可以使用PSMDATP来访问和使用 Microsoft
Defender Advanced Threat Protection（MDATP） API。

这个工具是一个针对MDATP的PowerShell模块，它的主要特性如下：

  * 可以帮助大家提升PowerShell技术；
  * 提供了一种更加简单的方法并通过PowerShell来与MDATP进行交互，并自动化实现某些任务；

## 工具要求

  * Windows PowerShell 5.1；
  * 通过在AzureAD中注册应用程序配置访问授权；

## 应用程序权限

下面给出的是我们必须授权的应用程序权限列表样例：

![](https://image.3001.net/images/20201031/1604158956_5f9d85ec916273c915889.png!small)

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/alexverboon/PSMDATP.git

## 工具使用

如需使用该功能模块，我们可以打开PowerShell命令行终端，然后通过PSGallery来安装该模块，安装命令如下：

    
    
    Install-Module PSMDATP -Scope CurrentUser

## 应用程序注册

### 初始配置

当你安装好该工具并在AzureAD中注册好应用程序之后，你将会在该项目的Module文件夹中看到一个名为TEMPLATE_PoshMTPconfig.json的文件。现在，我们需要将该文件改名为PoshMTPConfig.json，然后在其中输入API设置。接下来，将该文件拷贝到Module文件夹下的主路径。

配置样例：

    
    
    "C:\Users\User1\Documents\WindowsPowerShell\Modules\PSMDATP"
    
    ───PSMDATP
    
    │   │   PoshMTPconfig.json
    
    │   │
    
    │   └───0.0.2
    
    │           PSMDATP.psd1
    
    │           PSMDATP.psm1
    
    │           TEMPLATE_PoshMTPconfig.json

当前版本的PSMDATP PowerShell模块进要求提供API_MDATP信息：

    
    
    {
    
        "API_MDATP":  {
    
                          "AppName":  "WindowsDefenderATPPSMDATP",
    
                          "OAuthUri":  "https://login.windows.net/<YOUR TENANT ID>/oauth2/token",
    
                          "ClientID":  "CLIENT ID",
    
                          "ClientSecret":  "<CLIENT SECRET>"
    
                      },
    
        "API_MSGRAPH":  {
    
                            "AppName":  "xMSGraph",
    
                            "OAuthUri":  "https://login.windows.net/<YOUR TENANT ID>/oauth2/token",
    
                            "ClientID":  "<CLIENT ID>",
    
                            "ClientSecret":  "<CLIENT SECRET>"
    
                        }
    
    }

## 工具使用样例

### 枚举已包含的命令行工具

首先，我们可以使用下列命令查看PSMDATP模块所包含的命令行工具：

    
    
    get-command -Module PSMDATP | Select Name

命令执行结果如下：

    
    
    Add-MDATPDeviceTag
    
    Add-MDATPIndicator{
    
    Get-MDATPAlert
    
    Get-MDATPCollectionPackageUri
    
    Get-MDATPDevice
    
    Get-MDATPDeviceAction
    
    Get-MDATPDeviceTag
    
    Get-MDATPIndicator
    
    Get-MDATPInvestigation
    
    Get-MDATPQuery
    
    Get-MDATPTvmRecommendation
    
    Get-MDATPTvmVulnerability
    
    Remove-MDATPDevice
    
    Remove-MDATPDeviceTag
    
    Remove-MDATPIndicator
    
    Start-MDATPAppRestriction
    
    Start-MDATPAVScan
    
    Start-MDATPInvestigation
    
    Start-MDATPInvestigationPackageCollection
    
    Start-MDATPIsolation
    
    Stop-MDATPAppRestriction
    
    Stop-MDATPIsolation

### 获取MDATP警报

运行下列命令即可获取过去30天内所有接收到的MDATP警报：

    
    
    Get-MDATPAlert -PastHours 720

### 枚举MDATP设备

运行下列命令即可列举所有MDATP注册的设备：

    
    
    Get-MDATPDevice -All

## 项目地址

PSMDATP：【[ _GitHub传送门_](https://github.com/alexverboon/PSMDATP)】

