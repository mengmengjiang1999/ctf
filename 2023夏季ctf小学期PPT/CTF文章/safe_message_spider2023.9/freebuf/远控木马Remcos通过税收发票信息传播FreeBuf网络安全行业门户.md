近日，分析人员发现 Remcos RAT 正在以税务发-票为话题进行分发。钓鱼邮件中带有很短的消息内容，从事税务相关工作的用户可能会在没有防范的情况下执行文件。

![image.png-45.8kB](https://image.3001.net/images/20220323/1648013298_623aaff22d1dbefe5b48e.png!small)钓鱼邮件

![image.png-110.1kB](https://image.3001.net/images/20220323/1648013298_623aaff28ec1c92326fb8.png!small)恶意附件

解压附件 `Tax.gz`后，释放名为 `Tax.com`的可执行文件。如果执行环境是 64 位环境下，通过
`http://zhost.polycomusa.com/Chrimaz.exe`下载并执行恶意软件（1df2bf9313decafd0249d6a4556010bc）。如果不是
64 位环境，会下载名为 `3xp1r3Exp.ps1`的 PowerShell 脚本并执行。

![image.png-18.3kB](https://image.3001.net/images/20220323/1648013299_623aaff317f338ce03c2a.png!small)调试代码

PowerShell 脚本中包含绕过 UAC 并下载文件的功能。

![image.png-39.8kB](https://image.3001.net/images/20220323/1648013299_623aaff365262de2cc99d.png!small)PowerShell
脚本

各种绕过 UAC 技术中，PowerShell 脚本创建了文件夹并使用了 DLL 劫持。

    
    
    New-Item “\?\C:\Windows \System32” -ItemType Directory﻿

看起来像是要在 C 盘的 Windows 文件夹下创建 System32 子文件夹，但是实际上是在 `Windows`文件夹（带空格）的。通过
Windows 界面无法创建文件名末尾带有空格的文件夹，攻击者利用了这一点进行创建。

![image.png-102kB](https://image.3001.net/images/20220323/1648013299_623aaff3c9d78720a2c6b.png!small)创建文件夹

确定是否需要提权要检查文件是否在受信任的文件夹中执行，攻击者滥用判断自动提权条件的目录验证逻辑，系统扫描发现文件名末尾有空格会自动删除（通过
AppInfo.dll 的 GetLongPathNameW）。攻击者可以绕过这个条件的话，可以在不询问用户的情况下提权并执行恶意文件。

WastedLocker 勒索病毒此前使用过该技术，可以查看[相关文章](https://asec.ahnlab.com/en/17493/)。

从 PowerShell 脚本的第 17 行开始，将普通 System32 文件夹中的 winsat.exe 复制到虚假的 System32
文件夹中。随后利用 `winsat.exe`在隐藏窗口属性的情况下执行，由于 `winsat.exe`是白名单文件，执行时并不会弹出 UAC
警告，这也是攻击者经常用过的绕过方式。

这样，目录后面的空格会被删除，被视为受信任的目录下执行，攻击者就可以使用普通程序加载恶意 DLL 文件了。

分析时无法确认其他恶意行为，但恶意 DLL 文件执行时与 `‘C:\ProgramData\Chrimaz\Chrimaz.exe`有关，通过分析可确认为
Remcos RAT。

    
    
    powershell.exe -windowstyle hidden -NoProfile -ExecutionPolicy bypass -Command $mydir = [System.Environment]::GetFolderPath('CommonApplicationData');$bitdir = '\Chrimaz';$fulldir = $mydir+$bitdir; Add-MpPreference -ExclusionPath $fulldir;﻿

从 2 月 24 日开始，通过各个 URL 分发类似 PowerShell 脚本和恶意 DLL 文件的越来越多。

## IOC

> 98cf9ab79e33c04a4934628f6aa3161d  
> 1df2bf9313decafd0249d6a4556010bc  
> 9cdcaa1c51bfa4ce6d6abb9376ba26a8  
> a0f177bfd53ee82d20233bd362fdf024  
> 150744df32e4a57bb169f91cba45697c  
> 824a79fc5bebeb7b-508247619eca82cd  
> http://zhost.polycomusa.com  
> http://giraffebear.polycomusa.com

## 参考来源

> [ASEC](https://asec.ahnlab.com/en/32376)

