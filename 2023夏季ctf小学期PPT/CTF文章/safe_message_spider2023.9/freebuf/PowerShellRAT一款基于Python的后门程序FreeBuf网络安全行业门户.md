**今天给大家介绍的是一款名叫Powershell-RAT的Python后门，它可以利用Gmail邮件附件来从目标用户的设备中提取数据。这款RAT可以帮助红队测试人员给任何一台Windows设备安装后门，它不仅可以使用屏幕捕捉功能来跟踪用户的活动，而且还可以通过电子邮件附件来将提取出的数据发送给攻击者。**

![PowerShell-RAT：一款基于Python的后门程序](https://image.3001.net/images/20180319/152145632823.png!small)  

## Powershell-RAT

下载地址：【[GitHub传送门](https://github.com/Viralmaniar/Powershell-RAT)】

注：本工具目前还不会被任何反病毒软件检测到，PowerShell-RAT的开发意图是为了进行安全教育并给研究人员提供实验工具，请不要将其用于恶意目的，否则后果自负。

### 依赖组件

如果我的Windows设备没装Python的话，我该怎么办？

> 1\. 使用 PyInstaller将项目库中的PowershellRAT.py编译成可执行文件；
>
> 2\. PyInstaller在PyPI上就有，你可以直接使用pip来完成安装：
    
    
    pip install pyinstaller

### 工具配置

> 1\. 输入一个Gmail邮箱地址；
>
> 2\. 访问<https://myaccount.google.com/lesssecureapps>，并启用“Allow less secure
> apps”；
>
> 3\. 在Mail.ps1这个PowerShell文件中修改账号的$username和$password变量值；
>
> 4\. 根据邮箱地址修改$msg.From和$msg.To.Add；

## 如何使用

> 选项1：通过设置执行策略来不受限制地使用Set-ExecutionPolicyUnrestricted，这个选项在管理员设备上比较有用。
>
> 选项2：该选项将使用Shoot.ps1脚本在目标设备上进行屏幕截图。
>
> 选项3：该选项将使用schtasks在目标设备上安装后门，并将任务名设置为MicrosoftAntiVirusCriticalUpdatesCore。
>
> 选项4：该选项将使用Powershell从目标设备上发送电子邮件，并使用Mail.ps1脚本将提取到的数据+屏幕截图以邮件附件的形式进行发送。
>
> 选项5：该选项将使用schtasks在目标设备上安装后门，并将任务名设置为MicrosoftAntiVirusCriticalUpdatesUA。
>
> 选项6：该选项将从目标设备上删除截图文件（增强隐蔽性）。
>
> 选项7：该选项将使用schtasks在目标设备上安装后门，并将任务名设置为MicrosoftAntiVirusCriticalUpdatesDF。
>
> 选项8：该选项将自动执行上述所有操作，攻击者每5分钟便会收到一封带有屏幕截图的邮件，截图文件将在12分钟后自动删除。
>
> 选项9：退出程序（或按 Control+C）。

## 工具界面

首次运行Powershell-RAT时你将会看到如下图所示的选项界面：

![PowerShell-RAT：一款基于Python的后门程序](https://image.3001.net/images/20180319/15214563676949.png!small)  

使用Hail Mary选项可以帮助你在目标Windows设备中安装后门：

![PowerShell-RAT：一款基于Python的后门程序](https://image.3001.net/images/20180319/15214563752191.png!small)  

配置完成之后，你就可以查看到用户的活动截图了：

![PowerShell-RAT：一款基于Python的后门程序](https://image.3001.net/images/20180319/15214563845764.png!small)  

接下来，工具还将使用Gmail并以邮件附件的形式将提取出的数据发送给攻击者：

![PowerShell-RAT：一款基于Python的后门程序](https://image.3001.net/images/20180319/15214563922365.png!small)  

 *** 参考来源：[Powershell-RAT](https://github.com/Viralmaniar/Powershell-RAT)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

