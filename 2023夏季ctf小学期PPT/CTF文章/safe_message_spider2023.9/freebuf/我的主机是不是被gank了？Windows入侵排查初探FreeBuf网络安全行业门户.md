**所以，凭什么说我的主机被入侵了呢？**

![](https://image.3001.net/images/20200603/1591190734_5ed7a4ced5d40.png!small)

##  0x01 红队渗透流程

知攻击才能懂防守，以作为攻击方的红队视角：作为攻击者，当你拿到主机的一般用户权限后你会做什么？那当然是收集信息，然后尽可能的获得更高的权限了

攻击手段有千万种，往往脱离不了以下规则：

> 1.尽可能的获取有用的信息。 -->敏感文件被访问
>
> 2.修改Windows相关配置以达到自身的目的。 -->系统配置被修改

先梳理一下渗透测试中常见的一些姿势：

![](https://image.3001.net/images/20200603/1591192036_5ed7a9e4cef82.png!small)

那么以上流程，在蓝队的视角里就是如下情况：

 **收集信息** ：

> 执行cmd指令
>
> 执行powershell脚本，指令

 **提权** ：

> 进行程序调试（如：privilege::debug)
>
> 某系统进程内存占有率异常增加.

 **权限维持** ：

> SAM文件被访问
>
> lsass.exe 进程被调试
>
> 某些端口被进程打开/转发
>
> 注册表被修改
>
> 账户信息有变动

 **横向渗透：**

> 进行远程登录/命令执行
>
> 与域内主机的通信流量增加
>
> smb流量增加

 **后渗透**

> 日志丢失

## 0x02 蓝队排查流程

作为蓝队，应该以怎样的思路判断自己的主机已经沦陷了呢？

以下为总结的一些常规操作：

![](https://image.3001.net/images/20200603/1591191405_5ed7a76d71c1f.png!small)

着重分析一下这些操作的具体方法：

###  注册表排查

    
    
    # 开机自启
    HKCU:\Software\Microsoft\Windows\CurrentVersion\Run
    HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\RunOnce
    HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\RunServices
    HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\RunServicesOnce
    HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\Run
    HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\RunOnce
    HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\RunServices
    HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\RunServicesOnce
    # winrm后门
    HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System
    # Logon Scripts后门
    HKCU\Environment\
    # 服务项
    HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services

###  安全配置排查

    
    
    # 检查防火墙策略
    netsh firewall show config
    # 检查端口，进程连招
    netstat -ano | findstr "[port]"
    tasklist | findstr "[pid]"
    # 检查系统安装的补丁
    systeminfo

![](https://image.3001.net/images/20200603/1591191418_5ed7a77ae85bd.png!small)

    
    
    # Applocker应用控制策略检查，查看是否对敏感目录使用了适当的规则
      Applocker用于限制某些目录下应用程序，脚本等的执行。
    # 打开方式
    运行->secpol.msc

![](https://image.3001.net/images/20200603/1591191431_5ed7a7878484e.png!small)

![](https://image.3001.net/images/20200603/1591191455_5ed7a79f4d98d.png!small)

> 此处可参考微软官方文档：<https://docs.microsoft.com/zh-cn/windows/security/threat-> protection/windows-defender-application-control/applocker/working-with-> applocker-rules>

**防御Applocker绕过**

常见的绕过方式有Regsv***.exe绕过 和 msxsl.exe执行脚本绕过

禁止这两个文件的使用即可

![](https://image.3001.net/images/20200603/1591191568_5ed7a81063a98.png!small)

![](https://image.3001.net/images/20200603/1591191573_5ed7a8153d610.png!small)

###  UAC (User Account Control)

在命令行中输入gpedit.msc查看本地组策略，找到路径 计算机配置->Windows设置->安全设置->本地策略->安全选项

![](https://image.3001.net/images/20200603/1591191594_5ed7a82a1acbc.png!small)

排查安全策略是否配置妥当

![](https://image.3001.net/images/20200603/1591191612_5ed7a83c1d01f.png!small)

例如，通过如下选项可配置当某程序要以管理员身份运行时弹出UI界面

![](https://image.3001.net/images/20200603/1591191688_5ed7a888411bd.png!small)

###  PowerShell执行策略

    
    
    #在powershell中运行如下指令
    #查看策略
    Get-ExecutionPolicy
    #更改策略
    Set-ExecutionPolicy -Scope CurrentUser Restricted #设置执行策略为允许单独的命令，但不会运行脚本。
    Get-ExecutionPolicy -List #查看当前的执行策略

绕过Powershell执行策略的方式有很多种，甚至直接在后面加上 -ep Bypass
就可以执行powershell脚本。可见微软并没有将该策略当做一种严格安全防护。因此这里不再赘述。

###  ASR (Attack surface reduction，攻击面减少规则)

适用Windows版本（windows较低版本中找不到对应的函数）

> Windows 10 专业版、版本 1709或更高版本
>
> Windows 10 企业版、版本 1709或更高版本
>
> Windows Server、版本1803（半年度频道）或更高版本
>
> Windows Server 2019你可以使用组策略、PowerShell 和 MDM Csp 配置这些设置
    
    
    # 运行powershell
    # 设置ASR规则
    Set-MpPreference -AttackSurfaceReductionRules_Ids <GUID> -AttackSurfaceReductionRules_Actions Enabled
    # 禁用ASR规则
    Add-MpPreference -AttackSurfaceReductionRules_Ids <GUID> -AttackSurfaceReductionRules_Actions Disabled

示例GUID：

> 阻止所有 Office 应用程序创建子进程 D4F940AB-401B-4EFC-AADC-AD5F3C50688A
>
> 阻止执行可能混淆的脚本 5BEB7EFE-FD9A-4556-801D-275E5FFC04CC
>
> 阻止从 Office 宏调用 Win32 API 92E97FA1-2EDF-4476-BDD6-9DD0B4DDDC7B
>
> 阻止 Office 应用程序创建可执行内容 3B576869-A4EC-4529-8536-B80A7769E899
>
> 阻止 Office 应用程序将代码注入其他进程 75668C1F-73B5-4CF0-BB93-3ECF5CB7CC84
>
> 阻止 JavaScript 或 VBScript 启动下载的可执行内容 D3E037E1-3EB8-44C8-A917-57927947596D
>
> 阻止来自电子邮件客户端和 Web 邮件的可执行内容 BE9BA2D9-53EA-4CDC-84E5-9B1EEEE46550
>
> 阻止可执行文件，除非它们满足流行、年龄或受信任列表条件 01443614-cd74-433a-b99e-2ecdc07bfc25对勒索软件使用高级防护
> c1db55ab-c21a-4637-bb3f-a12568109d35
>
> 阻止从 Windows 本地安全机构子系统（lsass.exe）偷窃的凭据 9e6c4e1f-7d60-472f-ba1a-a39ef669e4b2
>
> 阻止从 PSExec 和 WMI 命令发起的进程创建 d1e49aac-8f56-4280-b9ba-993a6d77406c
>
> 阻止从 USB 运行的不受信任和未签名的进程 b2b3f03d-6a65-4f7b-a9c7-1c7ef74a9ba4
>
> 阻止 Office 通信应用程序创建子进程 26190899-1602-49e8-8b27-eb1d0a1ce869
>
> 阻止 Adobe Reader 创建子流程 7674ba52-37eb-4a4f-a9a1-f0f9a1619a2c通过 WMI 事件订阅阻止持久性
> e6db77e5-3df2-4cf1-b95a-636979351e5b

以上代码及资料均参考自微软的官方文档：<https://docs.microsoft.com/zh-cn/windows/security/threat-protection/microsoft-defender-atp/customize-attack-surface-reduction>

###  用户权限分配

查看其中是否有用户获得异常的授权

![](https://image.3001.net/images/20200603/1591191650_5ed7a8626585d.png!small)

该配置中的程序调试如果没有需要尽量置为空，Mimikatz的privilege::debug便是借助该配置的不妥当才得以提权

![](https://image.3001.net/images/20200603/1591191659_5ed7a86ba8962.png!small)

###  检查进程

Process Explorer

排查当前进程

![](https://image.3001.net/images/20200603/1591191705_5ed7a8994f8dc.png!small)

可以右键选择Check VirusTotal，

![](https://image.3001.net/images/20200603/1591191714_5ed7a8a275e07.png!small)

软件会把当前文件上传至VirusTotal进行在线查毒

![](https://image.3001.net/images/20200603/1591191738_5ed7a8ba44a8d.png!small)

并将结果返回至软件

![](https://image.3001.net/images/20200603/1591191745_5ed7a8c188440.png!small)

###  D盾

> 账号：检查当前用户/用户组
>
> 端口：是否有不该打开的端口被开放
>
> 进程：是否有可疑进程

均可在D盾中轻松查看，在此不再赘述

###  文件访问记录

    
    
    访问本地目录 C:\Users\[用户名称]\AppData\Roaming\Microsoft\Windows\Recent

![](https://image.3001.net/images/20200603/1591191779_5ed7a8e309c2a.png!small)

###  程序运行记录

    
    
    访问本地目录 C:\Windows\prefetch

![](https://image.3001.net/images/20200603/1591191787_5ed7a8ebdfaf8.png!small)

可以看到有许多.pf，pf文件是一些预读文件，用于提高程序的加载速度。有没有感觉新安装的游戏，第二次打开要比第一次打开玩加载速度快。可以使用工具WinPrefetchView进行查看，该软件会自动定位系统中的上述文件夹并读取内容

可以很清晰的查看到运行过的程序(隐私考虑。某些地方就打码了 :)

![](https://image.3001.net/images/20200603/1591191803_5ed7a8fb4c707.png!small)

双击便可查看详细信息，如创建时间，上一次的运行时间，程序所在路径等，

![](https://image.3001.net/images/20200603/1591191837_5ed7a91da7101.png!small)

选中上方程序在下方可以查看该程序访问的文件（此处以chrome为例）

![](https://image.3001.net/images/20200603/1591191874_5ed7a9427fbb8.png!small)

###  事件查看器

> #打开事件查看器
>
> eventvwr.msc
>
> # 部分重点排查ID
>
> 1102审核日志已清除
>
> 4608Windows启动
>
> 4609Windows关闭
>
> 4624帐户已成功登录
>
> 4625帐户登录失败
>
> 4657注册表被更改
>
> 4696向进程分配令牌
>
> 4697系统中添加服务
>
> 4698创建计划任务
>
> 4699删除计划任务
>
> 4700启用计划任务
>
> 4704分配用户权限
>
> 4706为域创建新信任
>
> 4713Kerberos策略被更改
>
> 4716可信域信息被修改
>
> 4719系统审核策略已更改
>
> 4720创建用户帐户
>
> 4723尝试更改帐户密码
>
> 4724尝试重置帐户密码
>
> 4726用户帐户已被删除
>
> 4739域策略已更改
>
> 4741创建计算机帐户

###  异常的计划任务

查看定时任务

> 开始->运行taskschd.msc 查看定时任务。

查看自启动程序

> 开始->运行msconfig.exe，查看自启动程序。

###  Powershell / cmd执行记录

Windows将cmd指令历史和powershell指令历史存到了一个文件中， 默认的储存位置如下：

    
    
    C:\Users\[用户名]\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt

![](https://image.3001.net/images/20200603/1591191914_5ed7a96a41ce1.png!small)

**使用杀软**

安装杀软进行全面的查杀

## 0x03 一些总结

以前一直在做逆向，近期才开始学内网安全方面的知识。不初学者包括我在内都有一些疑问，日志被攻击者删除了怎么办？上面这些操作是不是就没有意义了？查过一些资料，目前有不少已经开发的出的如堡垒机可以在内网保存日志信息的产品，一些有价值的攻击目标也往往会部署这些安全产品来应对网络安全问题。写这篇文章是做一个短期的总结，个人水平有限，若分享的文中有错误还望各位大佬斧正。如果分享的这些知识能帮到各位看官就再好不过啦~

##  **0x04 参考资料**

> <https://www.cnblogs.com/backlion/p/9484950.html>
>
> <https://www.cnblogs.com/pshell/p/7741823.html>
>
> <https://lengjibo.github.io/Persistence/>
>
>
> [https://blog.csdn.net/weixin_34216036/article/details/92367818?utm_medium=distribute.pc_relevant.none-> task-blog-> BlogCommendFromMachineLearnPai2-1.nonecase&depth_1-utm_source=distribute.pc_relevant.none-> task-blog-> BlogCommendFromMachineLearnPai2-1.nonecase](https://blog.csdn.net/weixin_34216036/article/details/92367818?utm_medium=distribute.pc_relevant.none-> task-blog-> BlogCommendFromMachineLearnPai2-1.nonecase&depth_1-utm_source=distribute.pc_relevant.none-> task-blog-BlogCommendFromMachineLearnPai2-1.nonecase)
>
> <https://docs.microsoft.com/zh-cn/windows/security/threat-> protection/microsoft-defender-atp/customize-attack-surface-reduction>

***本文作者： IceyHac，转载请注明来自FreeBuf.COM**  
  
  

