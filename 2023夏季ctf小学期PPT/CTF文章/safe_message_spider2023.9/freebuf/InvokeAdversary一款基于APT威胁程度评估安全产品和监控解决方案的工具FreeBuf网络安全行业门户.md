**Invoke-Adversary是一个基于APT威胁程度，来评估安全产品和监控解决方案的PowerShell脚本。在看到来自Florian
Roth的APTSimulator优秀工具后，我的灵感来自写这个脚本。我编写这个脚本的灵感主要来自[Florian
Roth](https://twitter.com/cyb3rops)的[APTSimulator](https://github.com/NextronSystems/APTSimulator)工具集。**

 **警告：**
该脚本仅用于授权测试和/或研究教育目的。使用脚本可能会对Windows系统的安全性和稳定性（包括但不限于：密码转储，禁用安全功能等）造成影响，因此请勿将其运行在生产系统上。该脚本的是属于我个人的，且与Microsoft不以任何形式相关。

##  **“Kill Chain”模型** ，或在有针对性的网络安全攻击期间会发生些什么？

Cyber Kill Chain模型是由[Lock Martin](https://www.lockheedmartin.com/us/what-we-do/aerospace-defense/cyber/cyber-kill-chain.html)公司Eric M.
Hutchins等三位安全研究员，在2011年3月举行的ICIW大会上公布的。由于攻击可能会分阶段发生，因此作为防御者，若能阻断/瓦解攻击方的进攻组织环节，即是成功地挫败对手的攻击企图。

Kill Chain模型将攻击者的攻击过程分解为如下七个步骤：

>  **侦察（Reconnaissance）** \- 攻击者开始探测目标可能存在的弱点或不良配置
>
>  **组装（Weaponization）** \- 攻击者开始构建一个可以传递给受害者的有效载荷（它可以是PDF文件或Office文档）
>
>  **投送（Delivery）** \- 攻击者通过电子邮件，网页链接或可移动媒体将有效载荷发送给目标
>
>  **利用（Exploit）** \- 有效载荷将在受害者的网络上执行
>
>  **植入（Installation）** \- 有效载荷将下载其他远程访问工具，并安装它们以建立持久后门
>
>  **命令和控制（Command and Control）** \- 在受害者和攻击者之间创建一个通道
>
>  **收割（Actions）** \- 执行预期目标（如加密文件，窃取数据等）

![image410.png](https://image.3001.net/images/20180423/15244699577024.png!small)

除此之外，[Mitre](https://www.mitre.org/)是一家非营利性组织，为网络对抗行为开发了一种增强模型称为“敌对策略，技术和常识”（ATT＆CK）矩阵。

目前，[MITRE
ATT＆CK](https://attack.mitre.org/wiki/ATT&CK_Matrix)矩阵为企业日常遇到的对抗技术和策略提供了最全面的框架。

 **技术**|  **描述**  
---|---  
[Persistence（持久化）](https://attack.mitre.org/wiki/Persistence)| 在目标系统上持续存在的一种技术  
[Privilege
Escalation（提权）](https://attack.mitre.org/wiki/Privilege_Escalation)|
一种攻击者用于获取更高权限的技术  
[Defense Evasion（防御规避）](https://attack.mitre.org/wiki/Defense_Evasion)|
可以用来逃避检测或避免其他防御措施的技术  
[Credential Access（凭据访问）](https://attack.mitre.org/wiki/Credential_Access)|
访问或控制系统，域或服务凭据  
[Discovery（发现）](https://attack.mitre.org/wiki/Discovery)| 允许攻击者获得关于系统和内网信息的技术  
[Lateral Movement（内网漫游）](https://attack.mitre.org/wiki/Lateral_Movement)|
使攻击者能够访问和控制网络上的远程系统的技术  
[Execution（执行）](https://attack.mitre.org/wiki/Execution)| 在远程或本地系统上执行攻击者代码的技术  
[Collection（收集）](https://attack.mitre.org/wiki/Collection)| 用于识别和收集信息的技术  
[Exfiltration（窃取）](https://attack.mitre.org/wiki/Exfiltration)|
帮助攻击者从目标网络中窃取文件和信息的技术  
[Command and
Control（命令和控制）](https://attack.mitre.org/wiki/Command_and_Control)|
攻击者与目标网络内的系统进行通信的技术  
  
当前有许多公司都在使用安全信息和事件管理（SIEM），端点保护平台（EPP）和端点检测与响应（EDR）产品来监视和保护其环境。但似乎还缺少了一个能够生成真实环境中的针对性攻击真实数据的工具。Invoke-Adversary是一个PowerShell脚本，它使用一组函数来模拟Windows企业网络中的后利用行为。

通过使用Invoke-Adversary脚本你可以：

> 评估您的安全监控工具和实践
>
> 评估端点检测代理

## 设置

部署要求：

> PowerShell 3.0版本及以上
>
> Windows 7（某些测试用例只能在Windows 10上运行）及更高版本
>
> Invoke-Adversary.ps1文件下载：<https://github.com/MotiBa/Invoke-> Adversary/tree/master>

## 使用

运行脚本最简单的方法是打开一个以管理员身份运行的PowerShell ISE窗口并按F5。

![IA0.png](https://image.3001.net/images/20180423/15244699847281.png!small)

脚本即将开始运行，您需要做的第一件事就是阅读免责声明，并通过键入yes来接受条款

![IA11.png](https://image.3001.net/images/20180423/15244700156333.png!small)

现在，您可以通过菜单上的编号来选择任何的测试用例

![IA2.png](https://image.3001.net/images/20180423/15244700376654.png!small)

通过菜单上的编号选择你想要运行的测试

![IA3.png](https://image.3001.net/images/20180423/15244700636001.png!small)

## 截图

![image210.png](https://image.3001.net/images/20180423/15244701279048.png!small)

![image310.png](https://image.3001.net/images/20180423/15244700909010.png!small)

## 运用了哪些战术/策略

 **防御规避**

> 禁用网络接口 - 禁用网络适配器并致使网络连接丢失
>
> 禁用Windows Defender AV - 关闭实时保护，扫描所有下载的文件和附件，行为监控，网络保护和隐私模式
>
> 添加本地防火墙规则例外 - 将虚构规则“Invoke-APT测试规则”添加到Windows高级防火墙
>
> 关闭Windows防火墙 - 关闭Windows高级防火墙
>
> 清除安全日志 - 使用wevtutil命令清除安全日志

 **持久战术**

> 辅助功能 - 使用图像文件执行选项“劫持cmd.exe替换为sethc.exe
>
> AppInit DLL - 在AppInit_DLLs下为pserver32.dll添加条目
>
> 应用程序Shimming -> 在HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\\{842562ef-8d28-411d-a67d-ab75ef611fe8}.sdb下创建注册表值
>
> 创建本地用户 - 新用户（用户名为：support_388945a0）
>
> 创建本地管理员 - 创建一个新用户（用户名为：Lost_337fde69_81a9）并添加到本地管理员组
>
> 创建新服务 - 创建新服务（WindowsHealth）
>
> 创建新的服务（不加引号的路径） - 与以前相同，只用未加引号的路径
>
> 注册表启动键值[HKLM] -> HKLM\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer\Run下的新启动键值
>
> 注册表启动键值[HKCU] - HKCU\Software\Microsoft\Windows\CurrentVersion\Run下的新启动键值
>
> 计划任务 - 新的计划任务（OfficeUpdaterA）被创建

 **凭据访问**

> Mimikatz - Logonpasswords - 将mimikatz下载到一个随机文件名，并使用执行参数： "privilege::debug"
> "sekurlsa::logonpasswords" "exit" (credit: <https://twitter.com/gentilkiwi>)
>
> PowerShell Mimikatz – Run Invoke-Mimikatz.ps1 (credit:
> <https://twitter.com/josephbialek?lang=en>)
>
> PowerShell Encoded Mimikatz - 使用编码的PowerShell命令行运行Invoke-Mimikatz.ps1
>
> 捕获Lsass内存转储 - 使用Windows错误报告捕获lsass内存 (credit:
> <https://twitter.com/mattifestation>)
>
> 捕获Lsass内存转储（Prodump）- 将Prodump下载到随机文件并捕获lsass内存
>
> 复制本地SAM文件（通过Invoke-NinjaCopy）- 运行Invoke-> NinjaCopy复制C:\Windows\System32\config\sam文件 (credit:
> <https://twitter.com/josephbialek?lang=en>)

 **发现战术**

> 帐户发现- 运行net命令来发现本地和域用户和组
>
> 网络服务扫描 - 在用户选择的主机上扫描端口（1-1024）
>
> 系统所有者发现 - whoami命令
>
> 系统时间发现 - 运行"net time"和"w32tm.exe /tz"命令
>
> 服务发现 - 所有服务的列表
>
> 网络连接发现 - netstat

 **命令和控制**

> 常用端口 - 尝试连接到用户选择的主机
>
> 罕见端口 - 尝试使用不常见的端口连接到用户选择的主机 (credit: [Florian
> Roth](https://twitter.com/cyb3rops))
>
> Web服务 - 在pastebin上创建一个新帖子并上传BITS服务信息
>
> DNS - 已公布的IP地址黑名单列表 - 解析前10个恶意IP地址 (credit: [Florian
> Roth](https://twitter.com/cyb3rops))
>
> 连接 - 已公布的IP地址黑名单列表 - 连接到前10个恶意IP地址(credit: [Florian
> Roth](https://twitter.com/cyb3rops))

 **执行**

> PSExec（随机文件名） - 将PSEec重命名为随机文件名并执行(credit:
> <https://twitter.com/markrussinovich>)
>
> PSExec（远程） - 在用户选择的主机上运行psexec
>
> PowerShell API调用 - 来自PowerShell的本机API调用
>
> 自我删除（批处理文件） - 自我删除批处理文件
>
> WMI进程执行 - 使用WMI命令行（WMIC）实用程序

 **收集**

捕屏 - 屏幕抓取

 **AppLocker绕过**

Regsvr32 - Regsvr32技术 (credit: <https://twitter.com/subTee>)

***参考来源：[technet](https://blogs.technet.microsoft.com/motiba/2018/04/09/invoke-adversary-simulating-adversary-operations/)，FB小编 secist
编译，转载请注明来自FreeBuf.COM**  

