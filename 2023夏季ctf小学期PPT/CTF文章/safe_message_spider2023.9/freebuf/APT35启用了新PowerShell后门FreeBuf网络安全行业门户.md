近日，研究人员发现 Phosphorus（又名 Charming
Kitten、APT35）组织的攻击行动有所增长。业界多次发现该组织对各行各业机构或人士发起攻击，甚至干预美国总统选举。

Cybereason 的研究人员最近发现 APT35 使用了名为 `PowerLess`的新型 PowerShell 后门。该后门通过在 .NET
上下文中直接运行而非生成 PowerShell 进程来规避 PowerShell 安全检测。

在攻击行动中使用的新工具集并不止新的 PowerShell
后门，还有恶意软件加载程序、浏览器信息窃取程序和键盘记录工具。近期该组织频繁在攻击中使用开源工具，例如
[DiskCryptor](https://github.com/DavidXanatos/DiskCryptor)、BitLocker、[Fast
Reverse Proxy](https://github.com/fatedier/frp)等。

## 从已知出发

IP 地址 `162.55.136.20`已经被包括美国国家应急响应中心（USCERT）在内的多方认定为 APT35 组织使用的攻击基础设施。

通过该 IP 地址下载的文件中，发现了名为 `WindowsProcesses.exe`的文件：

![image.png-78kB](https://image.3001.net/images/20220207/1644210551_6200a977d83171ed5692b.png!small)关联文件

根据 VirusTotal 的检测结果，该文件被 35/68 个引擎检出：

![image.png-44.1kB](https://image.3001.net/images/20220207/1644210552_6200a978b7e52fb396efb.png!small)检测结果

## WINDOWSPROCESSES.EXE

名为 `WINDOWSPROCESSES.EXE`的文件是一个 64 位的 Loader，用于解析 `%windir%\Temp\dll.dll`路径的
DLL 文件。

![image.png-112.8kB](https://image.3001.net/images/20220207/1644210553_6200a979a477966ba1038.png!small)执行流程

解析了相关的 DLL 文件和 API 调用后，开始执行 `dll.dll`：

![image.png-119kB](https://image.3001.net/images/20220207/1644210554_6200a97a4423b0a042fb7.png!small)主要代码

攻击者应该是借鉴了 GitHub
上的公开[代码片段](https://gist.github.com/farzinenddo/bb1f1ecb56aa9326abc7b47fc99e588e)，在运行时使用
CLR 运行 PowerShell。攻击者保留了这段代码的命名为 `Powerless`，其 PDB 路径为
`C:\\Users\\pugna\\Desktop\\126\\V1\\PowerLessCLR\\x64\\Release\\PowerLessCLR.pdb`。

## dll.dll

`dll.dll`是一个 .NET 编写的 AES 解密程序，使用硬编码密钥 `()*&3dCfabE2/123`解密另一个名为 `upc`的文件，最终执行
PowerShell 代码。

![image.png-58.1kB](https://image.3001.net/images/20220207/1644210554_6200a97ad22af84ce500f.png!small)文件代码

![image.png-83.5kB](https://image.3001.net/images/20220207/1644210555_6200a97b830bbec93b972.png!small)文件代码

## upc

upc 文件中的数据块经过多层加密，需要通过 base64 和 AES ECB 算法分阶段解密。

解密密钥如下所示：

> ()*&3dCfabE2/123
>
> 0123654789mkiujn
>
> 25sL(*14@#SDFCgd

在解密 PowerShell 后门前，会为失陷主机生成一个唯一标识符并将该标识符发送到 C&C 服务器下载配置文件。

![image.png-63.3kB](https://image.3001.net/images/20220207/1644210556_6200a97c1d793c29e9b1c.png!small)C&C
通信

## PowerLess

所有解密都完成后，PowerLess 后门将会被执行：

![image.png-175.1kB](https://image.3001.net/images/20220207/1644210556_6200a97c8743d2bd30f8f.png!small)后门命令解析

PowerLess 具备以下主要功能：

> 下载并执行其他恶意软件
>
> 使用加密 C&C 信道
>
> 任意命令执行
>
> 终止进程
>
> 窃取浏览器数据
>
> 键盘记录

该后门在 .NET 的上下文中运行，并不会产生 `powershell.exe`进程。

![image.png-43.3kB](https://image.3001.net/images/20220207/1644210557_6200a97d28eda2a95a73b.png!small)进程检测

但当后门接收到终止进程的命令时，后门反而会生成 powershell.exe` 进程。

![image.png-29.2kB](https://image.3001.net/images/20220207/1644210565_6200a9852736ebfec25f4.png!small)部分代码

代码中存在大量拼写错误和语法错误，可以认为后门开发者的母语并非英语。

![image.png-130.6kB](https://image.3001.net/images/20220207/1644210566_6200a9863552b45ae9112.png!small)日志拼写错误

## 键盘记录

PowerLess 后门能够下载的其中一个模块就是使用 .NET 编写的键盘记录工具：

![image.png-144.4kB](https://image.3001.net/images/20220207/1644210566_6200a986b392bd018d64f.png!small)部分代码

键盘记录的日志存储在 `“C:\\Windows\\Temp\\Report.06E17A5A-7325-4325-8E5D-E172EBA7FC5BK`：

![image.png-21.3kB](https://image.3001.net/images/20220207/1644210567_6200a98774f449d08ec94.png!small)日志路径

## 信息窃密

另一个模块是信息窃密工具，也是使用 .NET 编写的。读取 Chrome 和 Edge 浏览器的数据库文件，加密后以 JSON 格式写入文件中。

![image.png-88.2kB](https://image.3001.net/images/20220207/1644210567_6200a987ec3243227644c.png!small)部分代码

日志存储在 `C:\\Windows\\Temp\\cup.tmp`。

![image.png-28.9kB](https://image.3001.net/images/20220207/1644210568_6200a9885d9e2de129e2a.png!small)日志路径

## 其他工具

除 PowerLess 外，研究人员还发现了其他工具。尽管目前没有确切的证据证明都来自 APT35，但研究人员认为是来自同一开发者的。

根据 `WindowsProcesses.exe`的 PDB 路径
`C:\Users\pugna\Desktop\126\V1\PowerLessCLR\x64\Release\PowerLessCLR.pdb`：

![image.png-34.4kB](https://image.3001.net/images/20220207/1644210568_6200a988aab5ac1845bf5.png!small)PDB
路径

检索前缀发现其他工具：

![image.png-128.4kB](https://image.3001.net/images/20220207/1644210569_6200a989089fa71a4ea4c.png!small)其他样本

## Chromium F

`Chromium F.exe`是一个浏览器信息窃取程序，功能与前述模块类似。

![image.png-300.9kB](https://image.3001.net/images/20220207/1644210569_6200a989ccf8ad920ab93.png!small)部分代码

## Sou.exe

`Sou.exe`基于开源 `NAudio`录音程序修改而来。

![image.png-124.9kB](https://image.3001.net/images/20220207/1644210570_6200a98a69f1ab7630825.png!small)部分代码

## 新样本

可能来自同一开发者的新样本似乎是尚未完成的勒索软件样本，也是基于 .NET
开发，目前的功能只有锁定屏幕。尚未完成勒索赎金、邮箱等字段的填充设置。该样本是在伊朗上传的，有可能攻击者正在筹划利用勒索软件。

![image.png-22.5kB](https://image.3001.net/images/20220207/1644210570_6200a98ad3eb23937932a.png!small)样本上传信息

![image.png-462.7kB](https://image.3001.net/images/20220207/1644210571_6200a98b4dccd18d0e69a.png!small)勒索软件截图

## FRP Loader

在过往利用的 ProxyShell 攻击中，较为活跃的 IP 是 `148.251.71.182`。最近发现，该 IP 开始利用 Log4j 漏洞发起攻击。

![image.png-73.8kB](https://image.3001.net/images/20220207/1644210577_6200a991108bdf23aa07a.png!small)相关文件

其中，`RCE`为一个 Java Loader 用于根据操作系统使用对应版本的 FRP 程序。

![image.png-24.5kB](https://image.3001.net/images/20220207/1644210577_6200a9918667b8ed41878.png!small)RCE
文件

Loader 有两种变种，检查操作系统的文件分割符来判断操作系统，再下载 Payload 并执行持久化。

![image.png-253.4kB](https://image.3001.net/images/20220207/1644210578_6200a992221d1bcfdd16c.png!small)部分代码

## PowerShell

另一种方式是通过 PowerShell
代码进行投递，由[开源工具](https://m.majorgeeks.com/files/details/ps1_to_exe.html)`Ps1 To
Exe`转换为可执行文件。

![image.png-314.2kB](https://image.3001.net/images/20220207/1644210579_6200a993196290d8986f6.png!small)文件信息

Loader 会为 FRP 创建计划任务，完整的进程树如下所示：

![image.png-352.7kB](https://image.3001.net/images/20220207/1644210579_6200a993edec243316217.png!small)进程树

## 勒索软件

美国国家应急响应中心（USCERT）披露的另一个 IP 地址为 `91.214.124.143`，该 IP 地址与 Memento 勒索软件存在关联。

![image.png-58.4kB](https://image.3001.net/images/20220207/1644210580_6200a994d0a7e2778503a.png!small)关联信息

![image.png-108.9kB](https://image.3001.net/images/20220207/1644210581_6200a9954e24121ae618e.png!small)关联信息

## 结论

攻击者启用了新的 PowerShell 后门
PowerLess，但该攻击者可能缺乏专业的编码经验。为分析人员提供了追踪线索，如复用已知的攻击基础设施、保留了 PDB 路径等。

## 参考来源

> [Cybereason](https://www.cybereason.com/blog/powerless-trojan-iranian-apt-> phosphorus-adds-new-powershell-backdoor-for-espionage)

