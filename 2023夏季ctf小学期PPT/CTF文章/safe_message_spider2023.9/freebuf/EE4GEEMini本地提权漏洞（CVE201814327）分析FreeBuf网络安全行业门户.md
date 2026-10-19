***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

## 前言

 **我在前段时间从买了一个4G调制解调器。这是一个便携式4G
WiFi移动宽带调制解调器。有一天，我查看了安装在电脑上的用于故障排除的服务，我看到了一个奇怪的服务，名为“Alcatel OSPREY3_MINI
Modem Device Helper”。我想知道这是个什么玩意，然后我想到这可能是我的EE 4G
WiFi调制解调器。然后在谷歌上搜索了一会儿，这个调制解调器是阿尔卡特公司生产的。**

然后出于好奇的角度查看了安装的服务，发现存在一个漏洞。

    
    
    C:\>sc qc "Alcatel OSPREY3_MINI Modem Device Helper"
    [SC] QueryServiceConfig SUCCESS
    SERVICE_NAME: Alcatel OSPREY3_MINI Modem Device Helper
            TYPE               : 110  WIN32_OWN_PROCESS (interactive)
            START_TYPE         : 2   AUTO_START
            ERROR_CONTROL      : 1   NORMAL
            BINARY_PATH_NAME   : C:\Program Files (x86)\Web Connecton\EE40\BackgroundService\ServiceManager.exe -start
            LOAD_ORDER_GROUP   :
            TAG                : 0
            DISPLAY_NAME       : Alcatel OSPREY3_MINI Modem Device Helper
            DEPENDENCIES       :
            SERVICE_START_NAME : LocalSystem
    

但由于文件夹存在权限问题，您不能直接编写文件。我一开始以为这并不是问题。但是当我查看了“EE40”文件夹和W00t的文件夹权限!它被设置为“Everyone:(OI)(CI)(F)”，这意味着任何用户都可以在该文件夹中读写、执行、创建、删除任何内容，它是子文件夹。ACL规则具有OI对象继承和CI容器继承，这意味着该文件夹和子文件夹中的所有文件都具有相同的权限。

    
    
    C:\Program Files (x86)\Web Connecton>icacls EE40
    EE40 Everyone:(OI)(CI)(F)
         NT SERVICE\TrustedInstaller:(I)(F)
         NT SERVICE\TrustedInstaller:(I)(CI)(IO)(F)
         NT AUTHORITY\SYSTEM:(I)(F)
         NT AUTHORITY\SYSTEM:(I)(OI)(CI)(IO)(F)
         BUILTIN\Administrators:(I)(F)
         BUILTIN\Administrators:(I)(OI)(CI)(IO)(F)
         BUILTIN\Users:(I)(RX)
         BUILTIN\Users:(I)(OI)(CI)(IO)(GR,GE)
         CREATOR OWNER:(I)(OI)(CI)(IO)(F)
         APPLICATION PACKAGE AUTHORITY\ALL APPLICATION PACKAGES:(I)(RX)
         APPLICATION PACKAGE AUTHORITY\ALL APPLICATION PACKAGES:(I)(OI)(CI)(IO)(GR,GE)
         APPLICATION PACKAGE AUTHORITY\ALL RESTRICTED APPLICATION PACKAGES:(I)(RX)
         APPLICATION PACKAGE AUTHORITY\ALL RESTRICTED APPLICATION PACKAGES:(I)(OI)(CI)(IO)(GR,GE)
    Successfully processed 1 files; Failed processing 0 files
    C:\Program Files (x86)\Web Connecton>
    C:\Program Files (x86)\Web Connecton>
    C:\Program Files (x86)\Web Connecton>icacls EE40\BackgroundService
    EE40\BackgroundService Everyone:(OI)(CI)(F)
                           Everyone:(I)(OI)(CI)(F)
                           NT SERVICE\TrustedInstaller:(I)(F)
                           NT SERVICE\TrustedInstaller:(I)(CI)(IO)(F)
                           NT AUTHORITY\SYSTEM:(I)(F)
                           NT AUTHORITY\SYSTEM:(I)(OI)(CI)(IO)(F)
                           BUILTIN\Administrators:(I)(F)
                           BUILTIN\Administrators:(I)(OI)(CI)(IO)(F)
                           BUILTIN\Users:(I)(RX)
                           BUILTIN\Users:(I)(OI)(CI)(IO)(GR,GE)
                           CREATOR OWNER:(I)(OI)(CI)(IO)(F)
                           APPLICATION PACKAGE AUTHORITY\ALL APPLICATION PACKAGES:(I)(RX)
                           APPLICATION PACKAGE AUTHORITY\ALL APPLICATION PACKAGES:(I)(OI)(CI)(IO)(GR,GE)
                           APPLICATION PACKAGE AUTHORITY\ALL RESTRICTED APPLICATION PACKAGES:(I)(RX)
                           APPLICATION PACKAGE AUTHORITY\ALL RESTRICTED APPLICATION PACKAGES:(I)(OI)(CI)(IO)(GR,GE)
    Successfully processed 1 files; Failed processing 0 files
    

因为“ServiceManager。exe“是一个Windows服务可执行文件，通过植入一个同名的恶意程序"ServiceManager.exe"将导致执行二进制文件为“NT
AUTHORITY\SYSTEM”，在Windows操作系统中授予最高权限。此漏洞可用于在本地Windows操作系统中升级特权。例如，攻击者可以从一个低权限的用户帐户中植入一个反向shell，通过重新启动计算机，恶意服务将作为“NT
AUTHORITY\SYSTEM”启动，使攻击者可以完全系统地访问远程PC。

## 修复固件

易受攻击的软件版本为“EE40_00_02.00_44”：  
![修复固件](https://image.3001.net/images/20181028/1540695248_5bd524d05a44b.png!small)在向EE报告了漏洞后，他们发布了一个补丁来更新调制解调器。按照以下步骤将调制解调器更新到最新的补丁。1.进入路由器的默认网关:<http://192.168.1.1>2.单击“检查更新”文本以更新固件。更新后的补丁软件版本为“EE40_00_02.00_45”，从您的计算机中删除先前安装的软件。  
![修复固件](https://image.3001.net/images/20181028/1540695255_5bd524d797be0.png!small)

## 手动修复洞

1\.
在开始菜单或运行提示符中输入“regedit”，打开Windows注册表编辑器。2.前往以下路径:`Computer\HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\Alcatel
OSPREY3_MINI Modem Device Helper`3\. 向“ImagePath”值添加双引号:`"C:\Program Files
(x86)\Web Connecton\EE40\BackgroundService\ServiceManager.exe -start"`  
![手动修复洞](https://image.3001.net/images/20181028/1540695262_5bd524deb373d.png!small)  
这也可以用这种方式来做。您必须打开具有管理权限的CMD提示符并运行此命令。对于64-bit Windows：`reg add
"HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\Alcatel OSPREY3_MINI
Modem Device Helper" /v ImagePath /t REG_EXPAND_SZ /d "\"C:\Program Files
(x86)\Web Connecton\EE40\BackgroundService\ServiceManager.exe -start\""
/f`对于32-bit Windows：`reg add
"HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\Alcatel OSPREY3_MINI
Modem Device Helper" /v ImagePath /t REG_EXPAND_SZ /d "\"C:\Program Files\Web
Connecton\EE40\BackgroundService\ServiceManager.exe -start\"" /f`

## 手动修复文件夹权限

打开CMD提示符，转到Alcatel调制解调器服务的位置，然后输入以下命令。

    
    
    cd “C:\Program Files\Web Connecton\”
    icacls "EE40" /t /grant:r Everyone:(OI)(CI)R
    

## 披露时间表

05-07-2018: ZeroDayLab顾问(Osanda Malith
Jayathissa)通过twitter向EE报告了这个问题05-07-2018:通过邮件向阿尔卡特汇报。12-07-2018: Osanda Malith
Jayathissa联系MITRE。16-07-2018: CVE指定CVE-2018-14327。25-07-2018:
EE通过电子邮件联系了Osanda Malith Jayathissa更多的技术细节。26-07-2018:致电Osanda Malith
Jayathissa和EE进一步讨论漏洞。26-07-2018: EE确认补丁将在一周内上线。03-08-2018: Osanda Malith
Jayathissa联系EE更新补丁，EE表示他们将在8月10日周五之前提供更多信息。10-08-2018:
EE表示patch已经被推迟了，并且会通知Osanda Malith Jayathissa更新。23-08-2018:
EE回复了一个补丁更新，供Osanda Malith Jayathissa核实。ZeroDayLab顾问证实了补丁的成功运行。03-09-2018:
EE通知Osanda Malith Jayathissa说补丁已经发布。

 ***参考来源[osandamalith](https://osandamalith.com/2018/09/17/ee-4gee-mini-local-privilege-escalation-vulnerability-cve-2018-14327/)，由周大涛编译，转载请注明来自FreeBuf.COM**

