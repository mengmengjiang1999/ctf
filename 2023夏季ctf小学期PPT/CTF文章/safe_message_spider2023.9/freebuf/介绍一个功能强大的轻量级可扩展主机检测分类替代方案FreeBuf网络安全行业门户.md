![](https://image.3001.net/images/20201104/1604491688_5fa299a8a7e989488f3f6.jpg!small)  

## SitRep

SitRep旨在提供一个轻量级的、可扩展的主机分类替代方案。这个方案可以在运行时通过独立文件来动态加载检查机制，这将允许研究人员快速修改现有检查，或根据需要添加新检查。

这里的检查按类别分组，可以标记为OpSec safe/unsafe，并且只有在提供了/AllowUnsafe参数时才会进行不安全的检查。

方案所检测到的有意思的结果将使用“[*]”符号进行标记。

## 检查分类方案

SitRep的检查机制可以划分为各种不同的类别，这样可以更加有效地为研究人员提供可用信息。当前的SitRep提供了以下检查分类方案。

### 环境

    
    
    CurrentUser.cs - 当前用户
    
    DomainName.cs - 域名
    
    HostName.cs - 主机名
    
    LoggedOnUsers.cs - 显示所有已登录用户
    
    OSVersion.cs - 操作系统版本信息
    
    VirtualEnvironment.cs - 检查我们是否在虚拟化环境中运行
    
    userEnvironmentVariables.cs - 获取应用于当前进程的环境变量
    
    SystemEnvironmentVariables.cs - 从注册表（HKLM）获取系统环境变量
    
    NameServers.cs - 获取每个网络接口的DNS服务器

### 防御

    
    
    AVProcesses.cs - 检查是否有任何已知的AV进程正在运行

### 权限

    
    
    Integrity.cs - 获取当前进程的完整性级别
    
    LocalAdmin.cs - 检查我们是否是本地管理员
    
    Privileges.cs - 列出我们目前的特权
    
    UACLevel.cs - 获取UAC级别
    
    UserDomainGroups.cs - 获取用户域组成员身份
    
    ComputerDomainGroups.cs - 获取计算机所属的域组

### 软件

    
    
    InstalledBrowsers.cs - 列出终端节点上安装的浏览器

### 凭证

    
    
    CredentialManager.cs - 检索存储在Windows凭据管理器中的当前用户的凭证

下列检测当前不会被标记为OpSec safe：

    
    
    CredentialManager.cs
    
    ComputerDomainGroups.cs
    
    UserDomainGroups.cs

如果有需要的话，你可以修改相关的配置并更新OpSec标签。

## 禁用某项检测

默认配置下，SitRep的所有检测都是自动启用的。到那时，由于所有的检测都是动态加载的，因此我们是可以根据需要来禁用某些检测的。

CheckBase中包含了一个名为“Enabled”的布尔值选项，该选项默认为True。我们可以通过添加构造函数来在派生类中进行自定义设置。下面的例子中我们将禁用当前用户的检测（CurrentUser.cs）：

    
    
    public CurrentUser()
    
    {
    
        base.Enabled = false;
    
    }

## 排除某项检测

由于检测是动态加载的，因此我们同样可以排除某项检测。最简单的方法就是在Visual Studio中，右键点击目标检测类，然后选择“exclude from
project”。

## 使用样例

运行所有检测：

    
    
    SitRep.exe /AllowUnsafe

仅进行OpSec safe检测（默认）：

    
    
    SitRep.exe

### SitRep执行样例：

![](https://image.3001.net/images/20201104/1604491757_5fa299ed1857b44e58cac.png!small)

## 添加检测

SitRep的所有检测类都继承自CheckBase基类，并且实现了ICheck接口，这样可以强制实现动态监测加载的需求。当然了，我们也可以根据需要去调用其他的方法或增加其他的类。

### ICheck接口暴露了下列属性和方法：

    
    
    IsOpsecSafe (bool) - 表明检测是否为OpSec safe
    
    DisplayOrder (int) - 在其显示组中显示此检查结果的顺序
    
    Check() - 调用执行实际检测的方法

派生类必须重写CheckBase中定义的“ToString()”方法，并在显示每个检查的输出时调用此方法。

本地访问方法是通过“NativeMethods”目录中的类来提供的，每一个类都以它们需要交互的DLL来进行名命。

每一个检查都要自己负责处理自己的错误，整个检测方法都会封装在一个try-catch语句块中。

空的检测方法如下所示：

    
    
    using SitRep.Interfaces;
    
    using System;
    
     
    
    namespace SitRep.Checks.Software
    
    {
    
        class ExampleCheck : CheckBase, ICheck
    
        {
    
            public bool IsOpsecSafe => true;
    
     
    
            public int DisplayOrder => 1;
    
     
    
            public Enums.Enums.CheckType CheckType => Enums.Enums.CheckType.Credential;
    
     
    
            public void Check()
    
            {
    
                try
    
                {
    
                    throw new NotImplementedException();
    
                }
    
                catch
    
                {
    
                    Message = "Check failed [*]";
    
                }
    
            }
    
     
    
            public override string ToString()
    
            {
    
                throw new NotImplementedException();
    
            }
    
        }
    
    }

## SitRep获取

点我获取：【G[ _itHub传送门_](https://github.com/mdsecactivebreach/sitrep)】

