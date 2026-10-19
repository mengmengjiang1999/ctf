## **0x01漏洞描述**

由于对多个系统文件（包括安全帐户管理器 (SAM) 数据库）的访问控制列表 (ACL)
过于宽松，当系统启用了内置管理员账户(administrator)时，普通用户可以利用此漏洞结合哈希传递攻击实现权限提升，从而在目标主机上以SYSTEM权限执行任意代码。

##  **0x02影响版本**

> Windows Server, version 20H2 (Server Core Installation)
>
> Windows Server, version 2004 (Server Core installation)
>
> Windows Server 2019 (Server Core installation)
>
> Windows Server 2019
>
> Windows 10 Version 21H1 for x64-based Systems
>
> Windows 10 Version 21H1 for ARM64-based Systems
>
> Windows 10 Version 21H1 for【过滤】32-bit Systems
>
> Windows 10 Version 20H2 for x64-based Systems
>
> Windows 10 Version 20H2 for ARM64-based Systems
>
> Windows 10 Version 20H2 for【过滤】32-bit Systems
>
> Windows 10 Version 2004 for x64-based Systems
>
> Windows 10 Version 2004 for ARM64-based Systems
>
> Windows 10 Version 2004 for【过滤】32-bit Systems
>
> Windows 10 Version 1909 for x64-based Systems
>
> Windows 10 Version 1909 for ARM64-based Systems
>
> Windows 10 Version 1909 for【过滤】32-bit Systems
>
> Windows 10 Version 1809 for x64-based Systems
>
> Windows 10 Version 1809 for ARM64-based Systems
>
> Windows 10 Version 1809 for【过滤】32-bit Systems

##  **0x03环境搭建**

1、本次漏洞环境使用windows10 1809版本复现，ED2K下载地址：

>
> ed2k://|file|cn_windows_10_business_editions_version_1809_updated_sept_2019_x64_dvd_f873d037.iso|5444462592|BF3C1964141BCF6ACD40EC6AAF2A0940|/

2、下载完成后使用VMware虚拟机安装windows10,具体过程请自行百度。

![1628576571_61121b3b1d66785dd6602.png!small?1628576572527](https://image.3001.net/images/20210810/1628576571_61121b3b1d66785dd6602.png!small?1628576572527)

##  **0x04漏洞复现**

1、使用以下命令检查是否存在漏洞，如果输出 BUILTIN\Users:(I)(RX) 表示该系统易受攻击；如果输出 Access is denied
或拒绝访问表示该系统不易受攻击。

![1628576576_61121b40d133463748a9c.png!small?1628576578476](https://image.3001.net/images/20210810/1628576576_61121b40d133463748a9c.png!small?1628576578476)

2、在github上下载利用exp，也可以下载作者编译好的 exe 文件，查看当前用户权限

> 下载地址：https://github.com/GossiTheDog/HiveNightmare

Exe文件下载地址：

>
> https://github.com/GossiTheDog/HiveNightmare/releases/download/0.5/HiveNightmare.exe

![1628576582_61121b46e06400707eda9.png!small?1628576584286](https://image.3001.net/images/20210810/1628576582_61121b46e06400707eda9.png!small?1628576584286)

3、执行下载的exe文件，普通账号下执行HiveNightmare.exe,在当前目录下导出SAM-haxx以及SYSTEM-haxx和SECURITY-haxx三个文件，此工具允许普通用户权限检索 Windows 10 中的所有注册表配置单元，包括 SAM 中的哈希值，可用于以 SYSTEM 权限执行命令。

![1628576587_61121b4bb6c92b931be8c.png!small?1628576589197](https://image.3001.net/images/20210810/1628576587_61121b4bb6c92b931be8c.png!small?1628576589197)

注：在虚拟机复现导出SAM可能会报以下错误。

![1628576596_61121b5436f20c1de5b14.png!small?1628576597522](https://image.3001.net/images/20210810/1628576596_61121b5436f20c1de5b14.png!small?1628576597522)

这是因为虚拟机中系统保护可能没有打开，也不会自动创建系统还原点，这里就需要自己手动去开启系统保护并创建一个系统还原点，右键点击此电脑-》属性-》系统保护-》配置-》启用系统保护

![1628576601_61121b597484c2bea0af7.png!small?1628576603054](https://image.3001.net/images/20210810/1628576601_61121b597484c2bea0af7.png!small?1628576603054)

然后再点击“创建”设置一个还原点，然后使用vssadmin list shadows命令查看会有一个卷影

![1628576607_61121b5f5a897c45a7a82.png!small?1628576608707](https://image.3001.net/images/20210810/1628576607_61121b5f5a897c45a7a82.png!small?1628576608707)

![1628576671_61121b9f397460cafaeda.png!small?1628576672685](https://image.3001.net/images/20210810/1628576671_61121b9f397460cafaeda.png!small?1628576672685)

此时再来使用exe导出SAM，可以看到导出成功。

![1628576676_61121ba423ca7547d1812.png!small?1628576677525](https://image.3001.net/images/20210810/1628576676_61121ba423ca7547d1812.png!small?1628576677525)

4、将三个文件拷贝到kali系统中，并执行impacket项目下的secretsdump.py,可生成主机上所有账号的hash值

    
    
    python2 secretsdump.py -sam SAM-2021-07-26 -system SYSTEM-2021-07-26 -security SECURITY-2021-07-26 LOCAL

![1628576681_61121ba94905058f6bb8c.png!small?1628576682619](https://image.3001.net/images/20210810/1628576681_61121ba94905058f6bb8c.png!small?1628576682619)

5、通过psexec.py横向工具直接利用 administrator 的 hash 登录管理员账户，获得 SYSTEM 权限会话

    
    
    python2 psexec.py -hashes
    aad3b435b51404eeaad3b435b51404ee:69943c5e63b4d2c104dbbcc15138b72b administrator@172.16.1 .143 cmd.exe

![1628576687_61121bafddcaa617e4df3.png!small?1628576689247](https://image.3001.net/images/20210810/1628576687_61121bafddcaa617e4df3.png!small?1628576689247)

##  **0x05修复方案**

1、临时修复方案：

1.1、限制对 %windir%\system32\config 内容的访问

以管理员身份打开命令提示符或 Windows PowerShell，运行以下命令：icacls %windir%\system32\config*.*
/inheritance:e

1.2、删除卷影复制服务 (VSS) 卷影副本

删除限制访问 %windir%\system32\config 之前存在的任何系统还原点和卷影卷，创建一个新的系统还原点（如果需要）。

不过在操作时需要注意的是，从系统中删除卷影副本会影响系统和文件的“恢复“操作。

参考链接：https://msrc.microsoft.com/update-guide/vulnerability/CVE-2021-36934

