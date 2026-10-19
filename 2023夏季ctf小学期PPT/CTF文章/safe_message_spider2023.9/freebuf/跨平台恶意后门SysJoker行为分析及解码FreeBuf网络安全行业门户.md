在恶意软件领域中，能够针对多个操作系统发起攻击的跨平台恶意软件是很多的。2020 年 9 月发现的 Vermilion Strike 就是最新的示例。

2021 年 12 月，网络安全公司 Intezer 发现了一个能够对 Windows、Mac 和 Linux 发起攻击的跨平台后门 SysJoker，其
Linux 版本和 Mac 版本的恶意软件在 VirusTotal 上完全没有检出。

SysJoker 是在一家教育机构的 Web 服务器上发现的，该服务器为 Linux 系统。经过进一步调查，发现 SysJoker 也有 Mach-O 和
Windows 版本。

根据在 VirusTotal 上发现的 C&C 域名与相关样本，估算 SysJoker 攻击是在 2021 年下半年发起的。

SysJoker 会伪装成系统更新，下载托管在 Google Drive 上的文本文件，通过解密得到 C&C 地址。

在分析过程中，其 C&C 地址更改了 3 次，这表明攻击者仍然处于活动状态并且在监视受感染的机器。根据受害者和恶意软件的特定行为，SysJoker
应该是针对特定目标的恶意软件。

SysJoker 以 TypeScript 文件的后缀名 `.ts`上传到 VirusTotal，此恶意软件可能是通过受感染的 npm 包进行传播的。

## SysJoker

SysJoker 使用 C++ 编写，每个样本都是针对特定操作系统量身定制的。在 VirusTotal 中 macOS 和 Linux 样本都是零检出。

![image.png-64.4kB](https://image.3001.net/images/20220113/1642054794_61dfc48a6048b84655d72.png!small)

VirusTotal 检测结果

## 行为分析

在不同的操作系统上，SysJoker 的行为都是相似的。本文以针对 Windows 系统的恶意样本为例，进行相关分析。

第一阶段的 Dropper（d71e1a6ee83221f1ac7ed870bc272f01）是一个 DLL 文件，上传到 VirusTotal 的名字是
`style-loader.ts`，在撰写本文时只有 6 个引擎检出。（截至发稿前已有 22 个引擎检出）

![image.png-172.6kB](https://image.3001.net/images/20220113/1642054795_61dfc48bc07f5de501b71.png!small)

VirusTotal 检测结果

Dropper 使用 PowerShell 命令从 `https://github.url-mini.com/msg.zip`中下载一个压缩的
SysJoker（53f1bb23f670d331c9041748e7e8e396），并将其复制到
`C:\ProgramData\RecoverySystem\recoveryWindows.zip`，再进行解压缩并执行。

![image.png-356.2kB](https://image.3001.net/images/20220113/1642054796_61dfc48cb7698c3b8ef89.png!small)

进程执行链

一旦 SysJoker（d90d0f4d6dad402b5d025987030cc87c）成功执行，样本会随机休眠 90 到 120 秒。然后创建
`C:\ProgramData\SystemData\`目录并将自身复制到该目录下，伪装成
`igfxCUIService.exe`程序文件（igfxCUIService 与 Intel Graphics Common User Interface
Service 有关）。

接着收集有关失陷主机的信息。SysJoker 使用不同的临时文本文件来记录命令的结果。这些文本文件会被立即删除，数据存储在 JSON
对象中，然后编码并写入名为 `microsoft_Windows.dll`的文件。下图展示了 SysJoker 在内存中构建的JSON对象：

![image.png-169kB](https://image.3001.net/images/20220113/1642054797_61dfc48d758d5b4a3cb01.png!small)

内存数据结构

SysJoker 会收集 MAC 地址、用户名、物理设备序列号和 IP 地址等信息。

另外，SysJoker 通过注册表
`HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run`实现持久化。在上述每个步骤之间，恶意软件都会随机休眠一段时间。

下图显示了进程树和命令：

![image.png-536.1kB](https://image.3001.net/images/20220113/1642054797_61dfc48df0dd16eded55f.png!small)

进程执行链

## 编码/解码

SysJoker 在二进制文件中保存一个硬编码的 XOR 密钥，用于解码和编码二进制文件中的字符串以及与 C&C 服务器间发送和接收的数据。

所有版本的 SysJoker 中都使用相同的 XOR 密钥：

>
> MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDkfNl+Se7jm7sGSrSSUpV3HUl3vEwuh+xn4qBY6aRFL91x0HIgcH2AM2rOlLdoV8v1vtG1oPt9QpC1jSxShnFw8evGrYnqaou7gLsY5J2B06eq5UW7+OXgb77WNbU90vyUbZAucfzy0eF1HqtBNbkXiQ6SSbquuvFPUepqUEjUSQIDAQAB

## C&C

为了获取可用的 C&C 服务器地址并开始通信，SysJoker 首先对硬编码的 Google Drive 链接进行解码。

![image.png-797.4kB](https://image.3001.net/images/20220113/1642054799_61dfc48fe0a474f4808bb.png!small)

数据解码对应关系

Google Drive 链接上部署了一个名为 `domain.txt`的文本文件，该文件包含一个经过编码的 C&C
服务器地址。文本文件的内容会随着时间的推移而变化，不断更新当前可用的 C&C 服务器。

![image.png-78.8kB](https://image.3001.net/images/20220113/1642054803_61dfc4934cacfeab85361.png!small)

CyberChef 解码示例

SysJoker 将收集到的用户信息发送到 C&C 服务器的 `/api/attach`作为初始握手。C&C 服务器会回复一个唯一
Token，从此以后的恶意软件与 C&C 服务器通信，Token 将被用作标识符。

SysJoker 运行一个 while(1) 循环，该循环会使用唯一 Token 向 C&C 服务器的 `/api/req`发送请求，接收响应处理为
JSON。这就是 SysJoker 与 C&C 服务器保活获取指令的方式：

![image.png-237.3kB](https://image.3001.net/images/20220113/1642054803_61dfc493e0d67826deb04.png!small)

请求代码结构

如果服务器响应数据，SysJoker 解析接收到的 Payload 执行对应指令：exe、cmd、remove_reg 和 exit。

![image.png-85.5kB](https://image.3001.net/images/20220113/1642054804_61dfc4947f8d2274b6a4e.png!small)

C&C 通信基本流程

当前版本的恶意软件并未实现 `remove_reg`和 `exit`。根据指令名称，可以推断是恶意软件的自我删除功能。

### exe

`exe`指令负责下载并运行可执行文件。SysJoker 会接收到一个 zip 文件的下载
URL、一个文件应该被放置到的路径，以及可执行文件的文件名。SysJoker 将下载该压缩文件，解压缩并执行。

![image.png-209.5kB](https://image.3001.net/images/20220113/1642054805_61dfc4956e843417c02c2.png!small)exe指令

执行后，恶意软件将向 C&C 服务器的 `/api/req/res`发送消息。如果成功则返回 `success`，否则返回 `exception`。

![image.png-261.8kB](https://image.3001.net/images/20220113/1642054806_61dfc4966a4a8b7338a38.png!small)exe
指令响应

### cmd

`cmd`指令负责运行命令并将其结果发送给 C&C 服务器。SysJoker 将对命令进行解码、执行并将结果发送给 `/api/req/res`。

![image.png-346.6kB](https://image.3001.net/images/20220113/1642054807_61dfc49767615ccc9ce84.png!small)cmd
指令

在撰写本文时，C&C 服务器没有响应下一个阶段的指令。

## 结论

有迹象表明 SysJoker 是由高级攻击者使用的：

> 代码是重新编写的，在其他攻击中从未见过。最重要的是，很少发现前所未见的 Linux 恶意软件。
>
> 攻击者注册了至少 4 个不同的域名，并为三种不同的操作系统重新编写恶意软件。
>
> 没有发现攻击者发送第二阶段的指令。这表明攻击是特定目标的，通常是高级攻击者的表现。

根据恶意软件的功能，猜测攻击的目的是间谍活动以及横向移动。

## IOC

> bd0141e88a0d56b-508bc52db4dab68a49b6027a486e4d9514ec0db006fe71eed  
> d028e64bf4ec97dfd655ccd1157a5b96515d461a710231ac8a529d7bdb936ff3  
> 1a9a5c797777f37463b44de2b49a7f95abca786db3977dcdac0f79da739c08ac  
> 61df74731fbe1eafb2eb987f20e5226962eeceef010164e41ea6c4494a4010fc  
> 1ffd6559d21470c40dcf9236da51e5823d7ad58c93502279871c3fe7718c901c  
> https://bookitlab.net  
> https://winaudio-tools.com  
> https://graphic-updater.com  
> https://github.url-mini.com  
> https://office360-update.com  
>
> https://drive.google.com/uc?export=download&id=1-NVty4YX0dPHdxkgMrbdCldQCpCaE-> Hn  
> https://drive.google.com/uc?export=download&id=1W64PQQxrwY3XjBnv_QAeBQu-> ePr537eu

## 参考来源

> [Intezer](https://www.intezer.com/blog/malware-analysis/new-backdoor-> sysjoker/)

