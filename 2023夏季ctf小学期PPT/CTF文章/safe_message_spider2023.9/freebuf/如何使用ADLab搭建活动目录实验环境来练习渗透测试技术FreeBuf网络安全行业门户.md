![](https://image.3001.net/images/20211130/1638278439_61a62527912f6a8adfd80.jpg!small)  

## 关于ADLab PowerShell模块

ADLab是一个功能强大的PowerShell模块，该工具可以自动化实现一个活动目录实验环境，以帮助广大研究人员更好地学习和研究内部网络环境内的渗透测试技术。

## 工具准备

首先，我们需要使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/xbufu/ADLab.git

接下来，我们需要将该模块移动至PSModulePath。

显示PSModulePath：

    
    
    $env:PSModulePath.split(";")

移动模块至该路径：

    
    
    Move-Item .\ADLab\ "C:\Windows\system32\WindowsPowerShell\v1.0\Modules\"

### 导入模块

导入全局模块：

    
    
    Import-Module ADLab

导入本地模块：

    
    
    Import-Module .\ADLab.psm1

## 初始化实验环境

### Invoke-DCPrep

这个功能函数用于准备当前的虚拟机或计算机设备，并将其当作一个域控制器来使用。它回设置一个静态IP地址，并设置本地localhost主机为DNS服务器，然后对本地计算机进行重命名。

使用默认配置运行当前虚拟机，并显示Verbose输出：

    
    
    Invoke-DCPrep -Verbose

设置自定义主机名并使用Google DNS作为外网访问：

    
    
    Invoke-DCPrep -Hostname "DC" -NewIPv4DNSServer "8.8.8.8"

使用自定义IP和默认网关，并显示Verbose输出：

    
    
    Invoke-DCPrep -Verbose -NewIPv4Address "192.168.1.99" -NewIPv4Gateway "192.168.1.1"

### Invoke-ForestDeploy

该功能函数将安装AD DS功能，并设置新的活动目录森林，整个过程自动完成，无需用户输入信息，完成后将会重启计算机。

安装新的森林，使用默认DSRM密码-“Password！”：

    
    
    Invoke-ForestDeploy -Domain bufu-sec.local

安装新的森林，使用DSRM密码-“P@ssword!”，并显示调试信息：

    
    
    Invoke-ForestDeploy -Domain "bufu-sec.local" -DSRMPassword "P@ssword!" -Verbose

### Invoke-DNSDeploy

该功能从安装DNS功能开始，然后添加主区域并配置服务器转发器。

在当前主机上安装并配置DNS，然后显示Verbose输出：

    
    
    Invoke-DNSDeploy -Verbose -NetworkID 192.168.47.0/24 -ZoneFile "192.168.47.2.in-addr.arpa.dns" -ServerForwarder 1.1.1.1

### Invoke-DHCPDeploy

在本地DC上安装并配置DHCP：

    
    
    Invoke-DHCPDeploy -Verbose -ScopeName "Default" -ScopeID 192.168.47.0 -StartIP 192.168.47.100 -EndIP 192.168.47.200 -SubnetMask 255.255.255.0 -DNSServer 192.168.47.10 -Router 192.168.47.10

在指定DC上安装并配置DHCP：

    
    
    Invoke-DHCPDeploy -Verbose -ScopeName "Default" -ScopeID 192.168.47.0 -StartIP 192.168.47.100 -EndIP 192.168.47.200 -SubnetMask 255.255.255.0 -DNSServer 192.168.47.10 -Router 192.168.47.10 -DCFQDN DC01.bufu-sec.local

## 内容

### Invoke-ADLabFill

该函数首先会创建一个组，并在全局Groups变量中定义OU。默认情况下，它会为每个OU生成10个用户对象。

使用对象填充域森林，并显示Verbose输出：

    
    
    Invoke-ADLabConfig -Verbose

针对每个OU创建50个用户，并显示Verbose输出：

    
    
    Invoke-ADLabConfig -Verbose -UserCount 50

## 攻击向量

### Set-ASREPRoasting

该函数从域中获取一定数量的随机用户，并为每个用户设置DoesNotRequirePreAuth标志，其中不包括管理员和krbtgt等默认帐户。默认情况下，会获取5%的ASREP-Roastable用户。

获取5%的ASREP-Roastable用户，并显示Verbose输出：

    
    
    Set-ASREPRoasting -Verbose

获取ASREP-Roastable域中的10个随机用户：

    
    
    Set-ASREPRoasting -VulnerableUsersCount 10

获取ASREP-Roastable bufu用户，并显示Verbose输出：

    
    
    Set-ASREPRoasting -Users bufu -Verbose

将提供的用户列表设置为ASREP-Roastable用户，并显示Verbose输出：

    
    
    Set-ASREPRoasting -Users ("bufu", "pepe") -Verbose

### Set-Kerberoasting

该函数从域中获取一定数量的随机用户，并为每个用户添加一个SPN，其中不包括管理员和krbtgt等默认帐户。默认情况下，会获取5%的kerberoastable用户。

获取5%的kerberoastable用户，并显示Verbose输出：

    
    
    Set-Kerberoasting -Verbose

获取kerberoastable域中的10个随机用户：

    
    
    Set-Kerberoasting -VulnerableUsersCount 10

获取kerberoastable bufu用户，并显示Verbose输出：

    
    
    Set-Kerberoasting -Users bufu -Verbose

将提供的用户列表设置为kerberoastable 用户，并显示Verbose输出：

    
    
    Set-Kerberoasting -Users ("bufu", "pepe") -Verbose

### Set-BadACLs

该函数首先授予Chads组对域管理员的常见权限，然后授予Degens组对Chads组的常见权限。最后，它将Degens组的一些用户的常见权限授予Normaies组的一些用户。

创建存在安全问题的ACL并显示Verbose输出：

    
    
    Set-BadACLs -Verbose

### Set-PSRemoting

该函数首先将GPO配置为允许WinRM通过TCP端口5985连接到加入域的系统，然后通过GPO启用PS远程处理。

启用PS远程功能并显示Verbose输出：

    
    
    Set-PSRemoting -Verbose

## 项目地址

 **ADLab：** 【[ _GitHub传送门_](https://github.com/xbufu/ADLab)】

## 参考资料

  * [ _https://twitter.com/joehelle_](https://twitter.com/joehelle)
  * [ _https://github.com/dievus/PowerShellForPentesters/_](https://github.com/dievus/PowerShellForPentesters/)

