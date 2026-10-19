**今天给大家介绍的是一款名叫DCOMrade的工具（PowerShell脚本），各位研究人员可利用该工具来枚举存在漏洞的DCOM应用程序。**

![一款枚举DCOM应用漏洞的PowerSHell脚本](https://image.3001.net/images/20190309/1552068967_5c82b16782721.jpg!small)

## DCOMrade

DCOMrade是一款PowerShell脚本，该脚本可枚举可能存在漏洞的DCOM应用程序，广大研究人员可利用该脚本实现横向渗透、代码执行和数据提取等操作。该脚本基于PowerShell
2.0开发，但理论上可支持任何版本的PowerShell。该脚本当前支持下列Windows操作系统（32位和64位）：

> 1、 Windows 7；
>
> 2、 Windows 10；
>
> 3、 Windows Server 2012/2012 R2；
>
> 4、 Windows Server 2016；

### 工具依赖

1、 脚本的正常工作，需要在Windows防火墙（5985）中允许Windows Remote Management服务；

2、 如果目标系统的网络配置设置为了“Public”（公共网络），则需要执行下列命令来启用Windows Remote Management服务：

    
    
    Enable-PSRemoting-SkipNetworkProfilecheck –Force

3、 该脚本只能在拥有本地管理员凭证的目标主机上运行，如果没有本地管理员凭证，你将无法在目标设备上开启远程会话，而且也无法激活DCOM应用程序。

## 工具运行机制

首先，工具会与目标系统建立远程连接，所有的远程操作都会通过这个连接来完成。接下来，脚本会在目标系统上运行PowerShell命令来检索所有的DCOM应用程序以及对应的AppID。这些AppID会用来搜索Windows注册表并判断对应的AppID是否在各自注册表条目中包含LaunchPermission子键。最后，工具会存储这些AppID，并检索各自对应的CLSID。

获取到CLSID之后，就可以激活对应的DCOM应用程序了。此时，工具会检测DCOM应用程序中的MemberTypes，并通过对比其中的字符串值来判断应用程序是否存在漏洞。

参考：【[VulnerableSubet文件](https://github.com/sud0woodo/DCOMrade/blob/master/VulnerableSubset.txt)】

## 使用样例

### 在Windows域中：

    
    
    .\DCOMrade.ps1-ComputerName [Computername / IP] -User [Local Administrator] -OS [OperatingSystem] -Domain [Domain name]

### 不在Windows域中：

    
    
    .\DCOMrade.ps1-ComputerName [Computername / IP] -User [Local Administrator] -OS [OperatingSystem]

## 项目地址

DCOMrade：【[GitHub传送门](https://github.com/sud0woodo/DCOMrade)】

 ***
参考来源：[DCOMrade](https://github.com/sud0woodo/DCOMrade)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

