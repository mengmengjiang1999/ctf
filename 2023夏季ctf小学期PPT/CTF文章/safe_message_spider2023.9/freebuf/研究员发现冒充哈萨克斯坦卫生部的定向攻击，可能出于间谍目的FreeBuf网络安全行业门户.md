11月10日，MalwareBytes实验室发现了一次冒充哈萨克斯坦卫生部的定向攻击，攻击者利用多阶段 PowerShell
恶意文件进行攻击。目前无法确认其具体意图，猜测可能是用于监视和间谍活动。

![1637038709_61933a75da878c7d08e47.png!small?1637038708900](https://image.3001.net/images/20211116/1637038709_61933a75da878c7d08e47.png!small?1637038708900)

向前回溯，攻击者 DangerSklif（命名可能参考了莫斯科的急救医院）在11月8日创建了 GitHub 账户并且上传了相关恶意文件。

## 概述

攻击链首先从名为 Уведомление.rar 的 RAR 文件开始，文件名是俄文“通知”的意思。文件中包含一个同名的 LNK
文件，打开该文件后会显示一个 PDF 文件来诱骗受害者，PDF 文件中是假冒哈萨克斯坦卫生部发布的有关 COVID-19
的相关内容。用户打开后，后台同时开始执行恶意脚本。

![1637038761_61933aa91da043832933d.png!small?1637038761859](https://image.3001.net/images/20211116/1637038761_61933aa91da043832933d.png!small?1637038761859)

假冒文档

## 攻击过程

攻击链如下所示。首先执行的 LNK 文件会调用 PowerShell 脚本进行提权和持久化操作：

![1637038810_61933adae14cd0d9f0ddf.png!small?1637038809879](https://image.3001.net/images/20211116/1637038810_61933adae14cd0d9f0ddf.png!small?1637038809879)

攻击过程

所有攻击的恶意文件都部署在名为 GoogleUpdate 的仓库中。该代码库由用户 DangerSklif 在 11 月 8 日创建。

![1637038835_61933af3851e2252a13bb.png!small?1637038834732](https://image.3001.net/images/20211116/1637038835_61933af3851e2252a13bb.png!small?1637038834732)

GitHub存储库

## 分析

LNK 文件经过混淆，去混淆后可以发现其使用 cmd.exe 调用 PowerShell 从 GitHub 上下载后续样本。

![image.png-351kB](https://image.3001.net/images/20211116/1637039173_61933c45a5c7d0cda475e.png!small)

LNK文件

lib7.ps1 会下载来自相同的 GitHub 账户的诱饵 PDF 文件，并将其存储在 Downloads 目录下。接着，它会打开诱饵 PDF
文件来迷惑用户，同时在后台获取操作系统版本信息，根据操作系统版本下载后续样本。

![image.png-188.1kB](https://image.3001.net/images/20211116/1637039175_61933c47148e45689bb4c.png!small)

lib7.ps1

如果操作系统是 Windows 7/8 会下载执行 lib30.ps1，如果操作系统是 Windows 10，则会下载
lib207.ps1。检查操作系统版本是因为要针对不同的操作系统使用不同的提权方法，这与 TA505 此前使用的类似。

攻击者在 lib207.ps1 中使用计划任务中的 SilentCleanup 绕过 Windows 10 的用户账户控制（UAC），相应的
PowerShell 命令用 0x58 的密钥进行了异或加密。

![image.png-497.7kB](https://image.3001.net/images/20211116/1637039175_61933c47f36d4f0ee2516.png!small)

lib207.ps1

解密后，就可以发现具体的命令：在计划任务中创建任务，调用 PowerShell 以更高权限执行创建的 VBS 文件。

![image.png-148.9kB](https://image.3001.net/images/20211116/1637039178_61933c4a25191af72e454.png!small)

解密后的 lib207.ps1

攻击者在 lib30.ps1 中使用 sysprep.exe 和 DLL 侧加载来绕过用户账户控制（UAC），相应的 PowerShell 命令用 0x02
的密钥进行了异或加密。

![image.png-778.1kB](https://image.3001.net/images/20211116/1637039179_61933c4b04c540b7e5ac7.png!small)

lib30.ps1

解密后的命令如下所示。首先在 Windows/Temp 目录下创建 cmd.bat，接着将创建一个包含 DLL 文件（Windows 7 下为
CRYPTBASE.dll 或 Windows 8 下为 shcore.dll）的 CAB 文件，随后使用 wusa.exe 将其解压到
C:\Windows\System32\Sysprep 目录。

最后，sysprep.exe 侧加载恶意 DLL 文件。该 DLL 文件执行创建的 cmd.bat 文件，以高权限执行。

![image.png-272.8kB](https://image.3001.net/images/20211116/1637039181_61933c4d420d61f22a9a9.png!small)

解密后的 lib30

绕过 UAC 后，所有操作系统环境下都会下载并执行下一阶段的恶意样本（lib106.ps1）执行以下操作：

  * 在 `ProgramFiles`目录中创建 VBS 文件（cu.vbs），并将此 VBS 文件通过 `HKLM\Software\Microsoft\Windows\CurrentVersion\Run`进行持久化
  * 使用 `Attrib.exe +h`隐藏 VBS 文件
  * 使用 PowerShell 下载并执行下一阶段的样本（updater.ps1）

![image.png-119.5kB](https://image.3001.net/images/20211116/1637039182_61933c4e6697ab0f4cf58.png!small)

lib106.ps1

最后是下载 Cobalt Strike：

![image.png-627.2kB](https://image.3001.net/images/20211116/1637039183_61933c4f266b0a00d7e5a.png!small)

updater.ps1

Cobalt Strike 的 ShellCode 采用 base64 编码与异或加密，解码后使用 VirtualAlloc 再调用 Invoke
函数执行。

![image.png-1866.2kB](https://image.3001.net/images/20211116/1637039186_61933c520b6b00a948b5a.png!small)

模糊处理后的updater.ps1

## 攻击者意图

最近哈萨克斯坦在承接中国转移的加密货币产业，报道称因此过度消耗了有限的电力资源。哈萨克斯坦也是俄罗斯的重要盟友，有着利润丰厚的油气公司。

攻击者除了 GitHub 账户外，没有留下任何其他信息。无法确认攻击的具体意图，猜测可能是用于监视和间谍活动。

## IOC

> 574a33ee07e434042bdd1f59fc89120cb7147a1e20b1b3d39465cd6949ba7d99  
> d0f3c838bb6805c8a360e7b1f28724e73e7504f52147bbbb06551f91f0df3edb  
> 08f096134ac92655220d9ad7137e35d3b3c559359c238e034ec7b4f33a246d61  
> 81631df5d27761384a99c1f85760ea7fe47acc49ef81003707bb8c4cbf6af4be  
> 912434caec48694b4c53a7f83db5f0b44b84ea79be57d460d83f21181ef1acbb  
> 893f6cac7bc1a1c3ee72d5f3e6994e902b5af044f401082146a486a0057697e5  
> 11d6b0b76d057ac9db775d9a1bb14da2ed9acef325060d0452627d9391be4ea2  
> 8f974d8d0741fd1ec9496857d7aabbe0d3ba4d2e52cc311c76c28396edae9eb9  
> 301194613cbc11430d67acf7702fd15ec40ee0f9be348cf8a33915809b65bc5e  
> 026fcb13e9a4ea6c1eab73c892118a96731b868a1269f348a14a5087713dd9e5  
> 36aba78e63825ab47c1421f71ca02422c86c774ba525959f42b8e565a808a7d4  
> 188.165.148.241

## 参考来源

> [MalwareBytes](https://blog.malwarebytes.com/threat-> intelligence/2021/11/a-multi-stage-powershell-based-attack-targets-> kazakhstan/)

