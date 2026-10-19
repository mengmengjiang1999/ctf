## 一、概述

**腾讯御见威胁情报中心近期发现KoiMiner挖矿木马变种，该变种的挖矿木马已升级到6.0版本，木马作者对部分代码加密的方法来对抗研究人员调试分析，木马专门针对企业SQL
Server 服务器的1433端口爆破攻击进行蠕虫式传播。腾讯御见威胁情报中心监测数据发现，KoiMiner挖矿木马已入侵控制超过5000台SQL
Server服务器，对企业数据安全构成重大威胁。该病毒在全国各地均有分布，广东、山东、广西位居前三。**

![1.png](https://image.3001.net/images/20181115/1542271134_5bed309eac37b.png!small)

KoiMiner挖矿木马的活跃趋势

腾讯安全专家建议企业网管对SQL
Server服务器做重点加固，停止使用简单密码，防止服务器被黑客暴力破解入侵。网管亦可在服务器部署腾讯御点终端安全管理系统防范此类病毒入侵。

![2.png](https://image.3001.net/images/20181115/1542271150_5bed30ae6f3d2.png!small)

腾讯御点拦截KoiMiner挖矿木马

与2018年7月发现的KoiMiner对比，该变种具有以下变化：

1.全部代码加密改为部分代码加密；

2.Apache Struts2漏洞攻击改为SQL Server 1433端口爆破；

3.下载的挖矿木马由直接下载PE可执行文件改为从图片中获取二进制代码再生成本地执行的挖矿木马。

![3.png](https://image.3001.net/images/20181115/1542271169_5bed30c188505.png!small)

KoiMiner挖矿木马攻击流程

攻击时Sqlbrowser.exe从C2地址获取动态配置的IP列表（从病毒下载的扫描目标IP段看，攻击范围十分广泛）、端口列表并进行端口扫描，然后对开放1433端口的IP使用C2地址获取的user列表、password列表进行爆破登录，登录成功后执行sql.txt中的shellcode代码。

Shellcode首先修复SQL的存储过程xp_cmdshell、sp_addextendedproc，然后注册多个com组件以便于恶意代码执行，然后尝试结束杀毒软件和taskmgr进程，最后通过写入二进制数据流的形式创建并保存文件o6.exe、x64.exe、sqlbrowser.exe。o6.exe利用微软MS16-032漏洞进行提升权限，然后执行x64.exe挖矿木马，并启动sqlbrowser.exe对网络中的其他SQL
Server服务器进行蠕虫式攻击。

## 二、详细分析

### 端口爆破

爆破模块sqlbrowser.exe使用C#编写，部分代码使用加密函数进行加密，运行过程中调用JvcPLNnlO0s99rHu6y进行解密。

![4.png](https://image.3001.net/images/20181115/1542271268_5bed3124092d8.png!small)

 **主要类功能如下：**

Crack 密码猜解

Exec 执行SqlCommand（shellcode）

GetConfigInfo 获取配置文件

Program 主类

Scan 端口扫描

![5.png](https://image.3001.net/images/20181115/1542271284_5bed31343b78c.png!small)

扫描的IP段列表：1.0.0.0 - 223.255.255.255

![6.png](https://image.3001.net/images/20181115/1542271323_5bed315bb8d97.png!small)

端口、用户名、密码字典

![7.png](https://image.3001.net/images/20181115/1542271348_5bed3174678fe.png!small)

获取配置文件ipsList、userList、passwordList、sqlList

![8.png](https://image.3001.net/images/20181115/1542271386_5bed319ab222c.png!small)

对IP进行端口扫描

![9.png](https://image.3001.net/images/20181115/1542271406_5bed31aee5364.png!small)

密码爆破

### Shellcode分析

端口爆破后执行shellocde，shellcode通过多个C2地址动态配置。

以hxxp://18.205.168.2/tinnoota/upload/33/1072/config/ini/sql.txt为例进行分析。

 **准备阶段**

恢复SQL的储存过程xp_cmdshell和sp_addextendedproc，通过重载xpstar.dll、xplog70.dll、odsole70.dll恢复储存扩展，然后利用扩展函数来执行服务操作、注册表操作、文件操作、进程操作等命令行。

![10.png](https://image.3001.net/images/20181115/1542271449_5bed31d9652ba.png!small)

通过xp_servicecontrol启动SQLSERVERAGENT服务，通过 sp_configure启用Ad Hoc Distributed
Queries和Ole Automation
Procedures，从而更方便进行远程操作。![11.jpg](https://image.3001.net/images/20181115/1542271485_5bed31fd17cf6.jpg!small)

通过写注册表Software\Policies\Microsoft\Windows\System，取消CMD命令提示符禁用，写注册表SOFTWARE\Microsoft\Jet\4.0\Engines，打开沙盒模式，删除注册表SOFTWARE\Microsoft\Windows
NT\CurrentVersion\Image File Execution
Options中的多个键：regini.exe、secedit.exe、ftp.exe、cacls.exe、net1.exe、icacls.exe、cmd.exe、sethc.exe、wscript.exe。

![12.jpg](https://image.3001.net/images/20181115/1542271576_5bed32586c1b1.jpg!small)

通过注册表写HKEY_CLASSES_ROOT\CLSID来注册以下COM对象：

    
    
    Microsoft.Jet.OLEDB.4.0
    
    JavaScript1.1
    
    Scripting.FileSystemObject
    
    Microsoft.XMLHTTP.1.0

![13.jpg](https://image.3001.net/images/20181115/1542271613_5bed327d827e4.jpg!small)

通过{72C24DD5-D70A-438B-8A42-98424B88AFB8}（WScript.Shell）执行secedit.exe
/configure /db secedit.sdb设置以下文件的安全属性：

    
    
    c:\windows\system32\cmd.exe
    
    c:\windows\system32\ftp.exe
    
    c:\windows\system32\cacls.exe
    
    c:\windows\system32\net1.exe
    
    c:\windows\system32\regini.exe
    
    c:\windows\system32\net1895.exe

![14.jpg](https://image.3001.net/images/20181115/1542271725_5bed32ed2a7c0.jpg!small)

通过Scripting.FileSystemObject删除以下目录：

    
    
    c:\Documents and Settings\Default User\Local Settings\Temporary Internet Files\Content.IE5\*;
    
    c:\Documents and Settings\NetworkService\Local Settings\Temporary Internet Files\Content.IE5\*;
    
    c:\Documents and Settings\LocalService\Local Settings\Temporary Internet Files\Content.IE5\*;
    
    C:\Windows\System32\config\systemprofile\AppData\Local\Microsoft\Windows\Temporary Internet Files\Content.IE5\*;

然后通过{72C24DD5-D70A-438B-8A42-98424B88AFB8}（WScript.Shell）创建Sethc.ini、Sethd.ini并分别写入以下内容，然后通过regini将其添加至注册表：

    
    
    HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\WindowsNT\CurrentVersion\Image File Execution Options [2 8 18]
    
    HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\WindowsNT\CurrentVersion\Image File Execution Options [1 7 17]

![15.png](https://image.3001.net/images/20181115/1542271776_5bed3320492ac.png!small)

劫持注册表粘滞键功能，替换成任务管理器。

通过microsoft.jet.oledb.4.0设置以下文件完全访问权限：

    
    
     c:\windows\system32\cmd.exe
    
    c:\windows\system32\ftp.exe 
    
    c:\windows\system32\icacls.exe 
    
    c:\windows\system32\cacls.exe 
    
    c:\windows\system32\wscript.exe

然后尝试结束杀毒软件进程：

    
    
    360sd.exe
    
    360tray.exe
    
    360safe.exe
    
    ZhuDongFangYu.exe
    
    360leakfixer.exe
    
    AhnSD.exe
    
    alg.exe
    
    ACASP.exe
    
    AYAgent.exe
    
    msseces.exe
    
    KSafetray.exe
    
    KSafe.exe

![16.jpg](https://image.3001.net/images/20181115/1542271823_5bed334f7d7e1.jpg!small)

尝试通过三种不同的方法注册以下组件：

    
    
    scrrun.dll 
    
    wshom.ocx 
    
    urlmon.dll 
    
    shdocvw.dll 
    
    jscript.dll 
    
    vbscript.dll
    
    
    select * from openrowset('microsoft.jet.oledb.4.0',';database=ias\ias.mdb','select shell("regsvr32 scrrun.dll wshom.ocx urlmon.dll shdocvw.dll jscript.dll vbscript.dll /s")'); 
    
    
    declare @shell00 int exec sp_oacreate'wscript.shell',@shell00 output exec sp_oamethod@shell00,'run',null,'command.com /c regsvr32 scrrun.dll wshom.ocx urlmon.dllshdocvw.dll jscript.dll vbscript.dll /s'; 
    
    
    declare @shell00 int exec sp_oacreate'wscript.shell',@shell00 output exec sp_oamethod @shell00,'run',null,'regsvr32scrrun.dll wshom.ocx urlmon.dll shdocvw.dll jscript.dll vbscript.dll /s';

 **Payload植入**

通过xp_cmdshell、wscript.shell、microsoft.jet.oledb.4.0三种方法尝试以下操作：

1.结束进程taskmgr.exe  

2.创建以下目录：

    
    
    C:\ProgramData
    
    C:\ProgramData\DataFiles
    
    C:\ProgramData\DataFiles\Microsoft
    
    C:\ProgramData\DataFiles\Microsoft\Fonts
    
    C:\ProgramData\DataFiles\Microsoft\Temp
    
    C:\ProgramData\DataFiles\Microsoft\Browser
    
    C:\ProgramData\DataFiles\Microsoft\Images

![17.jpg](https://image.3001.net/images/20181115/1542271919_5bed33af2ed64.jpg!small)

通过创建并写入二进制数据流ADODB.Stream的方法，创建以下文件并将三段二进制文本数据分别写入：

    
    
    C:\ProgramData\DataFiles\Microsoft\Fonts\o6.exe
    
    C:\ProgramData\DataFiles\Microsoft\Fonts\x64.exe
    
    C:\ProgramData\DataFiles\Microsoft\Images\sqlbrowser.exe

![18.jpg](https://image.3001.net/images/20181115/1542271965_5bed33dd619aa.jpg!small)

二进制数据开始

![19.jpg](https://image.3001.net/images/20181115/1542272051_5bed3433bc353.jpg!small)

二进制数据结束

最后通过三种方法执行生成的文件，命令行参数如下：

    
    
    C:\ProgramData\DataFiles\Microsoft\Fonts\x64.exe
    
    C:\ProgramData\DataFiles\Microsoft\Fonts\o6.exe x64.exe
    
    C:\ProgramData\DataFiles\Microsoft\Images\sqlbrowser.exe 20181101

x64.exe是挖矿木马，o6.exe利用漏洞提权并执行x64.exe，sqlbrowser.exe
进行新一轮SQL爆破攻击，从参数中的“20181101”代表的日期来看，恶意代码仍在不断维护更新中。

![20.jpg](https://image.3001.net/images/20181115/1542272097_5bed34614c235.jpg!small)

### 提权木马o6.exe

利用Windows辅助登录服务漏洞MS16-032提升权限：  

![21.png](https://image.3001.net/images/20181115/1542272145_5bed34911c127.png!small)然后以高权限创建指定进程：

![22.png](https://image.3001.net/images/20181115/1542272176_5bed34b098a9b.png!small)

### 挖矿木马x64.exe

使用C#编写，部分代码使用加密函数进行加密，运行过程中调用JvcPLNnlO0s99rHu6y进行解密。![23.png](https://image.3001.net/images/20181115/1542272210_5bed34d2bd23a.png!small)

主要类功能如下：  

> CreateFileByHex 将下载的二进制创建PE文件
>
> ExecCommand 启动指定文件
>
> MainEntrance 控制挖矿进程、保护进程启动及停止
>
> ProExecution 创建挖矿文件路径、命令行，结束杀软
>
> Program 主类
>
> ProtectEntrance 监控重启挖矿进程、结束其他高占用CPU进程
>
> SetFileAttritubes 设置文件隐藏、系统权限可读属性以及安全属性
>
> TheFirstRun 首次运行复制自身到指定目录、判断是否具有admin权限、创建互斥体

首次运行后将自身命名为csrss.exe并拷贝到以下两个目录：

    
    
    C:\ProgramData\MicrosoftLabs\NetFramewor\BreadcrumbStore\Main\
    
    
    C:\ProgramData\MicrosoftLabs\NetFramewor\BreadcrumbStore\Protect\

![24.png](https://image.3001.net/images/20181115/1542272250_5bed34fa1e47e.png!small)

csrss.exe从211.54.150.94下载logo_6.gif，然后将其中的二进制数据写入App目录下创建的lsass.exe：

![25.png](https://image.3001.net/images/20181115/1542272328_5bed3548763d4.png!small)

lsass.exe为开源门罗币挖矿木马XMRig：

![26.jpg](https://image.3001.net/images/20181115/1542272365_5bed356d16cd7.jpg!small)

csrss.exe启动挖矿木马lsass.exe，启动参数：

    
    
    -a cryptonight -o stratum+tcp://pool.supportxmr.com:3333-u48ojQAPbQCY5j75Hshe1mXKSAe3db6NVRAxsiMxS7rMNcEGE1mKGW1eETRamd1cKgRHCtqdTnEUu6NEKKSGXVugN9q2WVM8-p x --donate-level=1 --retries=10 --max-cpu-usage=50 -k -o stratum+tcp://fr.minexmr.com:80-u48ojQAPbQCY5j75Hshe1mXKSAe3db6NVRAxsiMxS7rMNcEGE1mKGW1eETRamd1cKgRHCtqdTnEUu6NEKKSGXVugN9q2WVM8-p    x --donate-level=1 --retries=1 --max-cpu-usage=50

![27.png](https://image.3001.net/images/20181115/1542272394_5bed358a43864.png!small)

矿池：

    
    
    pool.supportxmr.com
    
    fr.minexmr.com

钱包信息：

![28.png](https://image.3001.net/images/20181115/1542272626_5bed3672a55ef.png!small)

钱包信息显示，KoiMiner变种控制的钱包已收获20余个门罗币，按最新市价，约相当于1.5万元人民币。

##  **三、安全建议**

1.加固SQL Server服务器，修补服务器安全漏洞。使用安全的密码策略 ，使用高强度密码，切勿使用弱口令，特别是sa账号密码，防止黑客暴力破解。

2.修改SQL Sever服务默认端口，在原始配置基础上更改默认1433端口设置，并且设置访问规则，拒绝1433端口探测。

3.使用腾讯御知网络空间风险雷达（网址：<https://s.tencent.com/product/yuzhi/index.html>）进行风险扫描和站点监控。

4.网站管理员可使用腾讯云网站管家智能防护平台（网址：<https://s.tencent.com/product/wzgj/index.html>），该系统具备Web入侵防护，0Day漏洞补丁修复等多纬度防御策略，可全面保护网站系统安全。

## IOCs（部分）

###  **IP**

174.142.80.200

14.47.196.12

125.130.59.163

202.123.183.164

14.33.33.206

221.208.189.96

118.24.16.150

175.6.23.2

211.54.150.94

112.217.125.67

211.112.25.235

111.230.101.122

61.77.166.215

18.205.168.2

211.197.75.71

###  **URL**

hxxp://211.112.25.235/ezon/sw/SWFT/Image/user/web/port.txt

hxxp://211.112.25.235/ezon/sw/SWFT/Image/user/web/password.txt

hxxp://211.112.25.235/ezon/sw/swft/image/user/web/sql.txt

hxxp://211.112.25.235/ezon/sw/swft/image/user/web/ip.txt

hxxp://211.112.25.235/ezon/sw/SWFT/Image/user/web/user.txt

hxxp://211.112.25.235/ezon/sw/swft/image/user/web/port.txt

hxxp://174.142.80.200:8080/cameo/fonts/config/ini/files//x32.txt

hxxp://174.142.80.200:8080/cameo/fonts/config/ini/files//n64.txt

hxxp://174.142.80.200:8080/cameo/fonts/config/INI/Files//n32.txt

hxxp://14.47.196.12/ezon/images/xmr64.png

hxxp://125.130.59.163/ezon/images/xmr64.png

hxxp://202.123.183.164/application/partol/images/xmr64.png

hxxp://14.33.33.206/ezon/images/xmr64.png

hxxp://14.33.33.206/ezon/images/xmr32.png

hxxp://221.208.189.96:81/skin/red/images/xmr32.png

hxxp://221.208.189.96:81/skin/red/images/xmr64.png

hxxp://211.54.150.94/ezon/images/img/logo_6.gif

###  **矿池：**

pool.supportxmr.com

fr.minexmr.com

###  **钱包：**

48ojQAPbQCY5j75Hshe1mXKSAe3db6NVRAxsiMxS7rMNcEGE1mKGW1eETRamd1cKgRHCtqdTnEUu6NEKKSGXVugN9q2WVM8

463tGbooc85VubSo9TjhjLegtVvBQD6qPVJ3LxDoNrtKexAqcyDkoqm9p32MrDoMWcSmWz41EKbxL3AKPJyCjCmcTPZ96

47Uvt85TgZzHkveaTed69jhY4CSN8334BUufUtmaoLSNJadf2BoxxroHm5evYqQy4NJeyVBYYtGK8SHSAtFSiW6aDztDs

48gzbYzJ5mGE6QWQM8F7fKLk46UCoDbQEfeudysEjmifTroCKRmwvoyUGrSMjwy95ZeMrHoURhnFY5LJ9qaYW8FiFoimegp

### **md5**

229dadc6f3a80867d1fa9dae2c26f972

f1d92506cafd52be6b712f866fa274d4

1c68d7254d8907e2f2ee080440d3fe88

8e304c6af1853c1411698172aca4076f

e0d6ea4d42cb00c5427d391c97ba36c8

8ecf43d3b5d2357f89365198528951c0

e8d3fd8f108ed61acddbd20e0740d105

8a068ebbc1428f074884f66c616f6737

5a5462f1847306cb759d6c7abed60af5

64614e399a0aaed26db2a28d145abc68

c5b0b4c325a74cdc13ebf7135f6dcb3a

fb6aafeed4007c183e981b77c73c66ac

72541d0fd0bbda790794d4f2a152aa4e

1b6afd9198fed9b66eafa1d38a365cb3

4a2126ec9c7227144cb857da81e02d27

02e547abb48390e4558bcff8cbbf6be4

02638f1cb23ec5c2ceeca354ee36b11a

 ***本文作者：腾讯电脑管家，转载请注明来自FreeBuf.COM**

