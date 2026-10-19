在之前的文章中，已经讨论了活动目录的基本知识。在这篇文章中，我们将讨论如何设置和配置环境，以便我们可以使用它来执行各种攻击方案和检测。我们将讨论如何通过GUI和CLI方式完成。

##### 1、Active Directory 设置

让我们从活动目录实验室设置开始。我们将首先创建一个森林根域。然后我们将在森林中添加一个域。我们还可以向森林中添加一个或多个子域和外部域。

在森林根域创建后，我们将重点介绍如何将`AD`对象添加到AD环境，如用户对象、计算机对象、组对象、网络共享等，然后了解计算机如何加入域。

###### 1.1 、创建虚拟机

首先，我们将在虚拟机中安装`Windows Server 2019`操作系统。虚拟机可以在`Vmware Workstation`或`Oracle
VirtualBox`或任何其他管理程序中创建。可以从微软官方下载`Windows Server ISO`评估版进行安装。注意-请始终从Microsoft评估中心下载服务器操作系统ISO文件的评估副本。<https://www.microsoft.com/en-us/evalcenter/>

安装完成后，我们将配置创建`Active Directory`林的基本要求。

 **修改主机名**

要改变机器的主机名，通过运行`sysdm.cpl`打开系统属性。然后对主机名进行修改，修改完成要重启才能生效。

![image-20220512103354287](https://image.3001.net/images/20220815/1660533584_62f9bb504d31c1dd62c72.png!small)

![image-20220512103415569](https://image.3001.net/images/20220815/1660533585_62f9bb5148bda0656a4bc.png!small)

![image-20210315154602465](https://image.3001.net/images/20220815/1660533586_62f9bb5249749b22952cc.jpeg!small)

更改主机名时必须使用正确的命名约定，以便轻松记住哪个服务器是 DC、文件服务器、DHCP 服务器等。

主机名也可以使用以下`powershell`命令更改：

    
    
    Rename-Computer -NewName "RDSDC01" -Restart
    

**配置固定IP地址**

进入网络配置中心，给主机配置一个静态IP地址。

![image-20220512103713678](https://image.3001.net/images/20220815/1660533587_62f9bb53dda1708caff6a.png!small)

###### 1.2、添加角色

在服务器管理器面板选择添加角色和功能

![image-20220512104019736](https://image.3001.net/images/20220815/1660533589_62f9bb5532297ad5db5f9.png!small)

打开添加角色和功能向导，点击下一步

![image-20210315155315962](https://image.3001.net/images/20220815/1660533590_62f9bb566db9ed95e9e55.jpeg!small)

安装类型选择`基于角色和基于功能的安装`

![image-20210315155405415](https://image.3001.net/images/20220815/1660533591_62f9bb57be914d9661e4d.jpeg!small)

服务器角色选择`Active Directory 域服务`

![image-20210315155548012](https://image.3001.net/images/20220815/1660533592_62f9bb58ea2e70b9fabf8.jpeg!small)

确认无误之后，点`安装`

![image-20210315155713991](https://image.3001.net/images/20220815/1660533594_62f9bb5a41495f5a03de5.jpeg!small)

等待安装完成

![image-20210315155906173](https://image.3001.net/images/20220815/1660533595_62f9bb5b765711dfc1003.jpeg!small)

安装完成后，在服务器管理器中心可以看到

![image-20220512104405155](https://image.3001.net/images/20220815/1660533596_62f9bb5caaaab4f20d7a1.png!small)

###### 1.3、将服务器提升为域控制器

点击提示的感叹号，点击`将此服务器提升为域控制器`

![image-20210315161044666](https://image.3001.net/images/20220815/1660533597_62f9bb5dbb9b04be1a665.jpeg!small)

###### 1.4、添加新林

打开`Active Directory`域服务配置向导，选择`添加新林`，并设置一个`根域名`（生成环境中按实际情况设置）

![image-20210315161358810](https://image.3001.net/images/20220815/1660533598_62f9bb5ee68cca4e52324.jpeg!small)

设置一个`目录服务还原模式密码`，此密码为管理员提供了一种进入AD数据库的后门，以防域出现问题或需要还原/恢复AD数据库。

![image-20210315161501126](https://image.3001.net/images/20220815/1660533600_62f9bb60381b59070d09a.jpeg!small)

跳过DNS委派，直接点下一步

![image-20210315161627252](https://image.3001.net/images/20220815/1660533601_62f9bb619a450928805da.jpeg!small)

确认`NetBIOS`域名

![](https://image.3001.net/images/20220815/1660533602_62f9bb62e7bfb691a73cd.jpeg!small)

指定AD DS数据库，日志文件和SYSVOL存储的路径，可以使用默认的，也可以自定义，这里选默认，点击下一步

![image-20210315161851317](https://image.3001.net/images/20220815/1660533604_62f9bb6424736baf4854e.jpeg!small)

确认无误之后，点击下一步

![image-20210315161921330](https://image.3001.net/images/20220815/1660533605_62f9bb65845bb86d03c6c.jpeg!small)

系统会进行先决条件检查

![image-20210315162022217](https://image.3001.net/images/20220815/1660533606_62f9bb66b293e51af42d3.jpeg!small)

如果不符合要求，会无法继续安装，按照提示解决即可。然后点击`安装`

![image-20210315163051762](https://image.3001.net/images/20220815/1660533608_62f9bb685947eccfe110a.jpeg!small)

等待安装完成

![image-20210315163156205](https://image.3001.net/images/20220815/1660533610_62f9bb6a206b2c79f93fa.jpeg!small)

安装完成后服务器将重新启动。重启后，域控制器就准备好了！将出现一个登录屏幕。可以使用相同的管理员帐户登录。请注意，现在该帐户被提升为域管理员，因为计算机现在是域控制器。

##### 2、Active Directory 设置（命令行方式）

###### 2.1、使用Powershell脚本

可以使用`PowerShell`脚本自动化安装角色服务和创建AD林。几分钟即可自动完成安装。

![image](https://image.3001.net/images/20220815/1660534008_62f9bcf8997789961cce1.jpg!small)

两个关键参数：

1、Domian

2、DSRM password

安装角色的函数：

    
    
    function InstallADRole {
        Write-Host "[+] Installing required AD Roles and features." -ForegroundColor 'Green'
        Install-windowsFeature AD-Domain-Services
        Add-windowsfeature RSAT-ADDS
        Import-Module ADDSDeployment
        Write-Host "`n`nAD Roles and features are installed.`n`n" -ForegroundColor "Gray"
        }
    

安装 AD 林功能函数：

    
    
    function ADforestInstall {
        Write-Host "[+] Installing AD forest $DomainName" -ForegroundColor 'Green'
        $DomainNetBiosName = $DomainName.split('.')[0]
        Install-ADDSForest -CreateDnsDelegation:$false -DatabasePath "C:\\Windows\\NTDS" -DomainMode "7" -DomainName $DomainName -DomainNetbiosName $DomainNetBiosName -ForestMode "7" -InstallDns:$true -LogPath "C:\\Windows\\NTDS" -NoRebootOnCompletion:$false -SysvolPath "C:\\Windows\\SYSVOL" -Force:$true -SkipPreChecks -SafeModeAdministratorPassword $pass 
        Write-Host "`n`n$DomainName has been installed successfully. Domain controller will restart`n`n" -ForegroundColor 'Gray'
    }
    

调用上述两个函数，并将域名传递给`ADforestInstall`函数。和提示输入`DSRM`密码。

    
    
    function Invoke-ADForest
        {
            Param
            ([Parameter(Mandatory=$true, Position=0)] [string] $DomainName)
            $pass = Read-Host -Prompt "Set Safe Mode Administrator Password" -AsSecureString
            InstallADRole
            ADforestInstall
        }
    

该脚本可以从Github中下载 https://github.com/ScarredMonk/ActiveDirectoryInstallation。

##### 3、说明

本文由笔者在原文上编译，转载请注明原文出处。

原文出处：[Active Directory Lab Setup (Part 1) - Forest
Installation](https://rootdse.org/posts/active-directory-lab-setup-forest/)

