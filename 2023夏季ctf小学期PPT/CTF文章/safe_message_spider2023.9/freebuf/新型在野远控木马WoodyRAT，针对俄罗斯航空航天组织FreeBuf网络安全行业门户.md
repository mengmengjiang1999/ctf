Malwarebytes 威胁情报团队发现了一种新的远控木马，命名为 Woody RAT，研究人员发现其在野已经存在至少一年。

攻击者最近利用 Follina 漏洞来针对俄罗斯的实体发起攻击，根据注册的虚假域名推测，攻击目标应该为名为 OAK 的俄罗斯航空航天与国防组织。

## 分发方式

Woody RAT 使用两种方式进行分发：压缩文件与利用 Follina 漏洞的 Office 文档文件。

早期的样本在 ZIP 文件中，伪装成俄罗斯特组织的文件。当 Follina 漏洞出现时，攻击者也利用其进行分发恶意软件。整体攻击流程如下所示：

![image.png-81.9kB](https://image.3001.net/images/20220809/1660020389_62f1e6a5c809717533f5b.png!small)

攻击流程

### 压缩文件

Woody RAT 被打包在压缩文件中发给受害者，这些压缩文件是通过鱼叉邮件进行传播的。一些压缩文件如下所示：

> anketa_brozhik.doc.zip：其中包含同名的 Woody RAT 文件：Anketa_Brozhik.doc.exe
>
> zayavka.zip：其中包含 Woody RAT 伪装的程序：selection.doc.exe

### Follina 漏洞

恶意文档（Памятка.docx）使用 Follina 漏洞（CVE-2022-30190）来传播 Woddy
RAT，诱饵文档名意为“信息安全备忘录”，其中列举了关于密码和机密信息有关的安全措施。

![image.png-289.8kB](https://image.3001.net/images/20220809/1660020390_62f1e6a69a4a7bc3db996.png!small)诱饵文档

## Woody RAT

攻击者在样本中留下了 PDB 路径的调试信息：

![image.png-128.6kB](https://image.3001.net/images/20220809/1660020391_62f1e6a7b352d02bbe909.png!small)调试信息

许多 CRT 函数都是静态链接的，这使 IDA 产生了大量的分析噪音。在初始化前，恶意软件通过以 0x8007 作为参数调用 SetErrorMode
来有效地屏蔽所有错误报告。

![image.png-61.5kB](https://image.3001.net/images/20220809/1660020392_62f1e6a88404e56336adc.png!small)主函数

### Cookie

Woody RAT 使用 HTTP 与 C&C 服务器进行通信。为了标识每台失陷主机，恶意软件会根据主机信息生成 Cookie
值。主机信息包括网卡信息、计算机名称、卷信息，并且追加八字节的随机字符，尽量使 Cookie 能够成为唯一值。

使用 GetAdaptersInfo、GetComputerNameA 和 GetVolumeInformationW 获取信息后，生成的 Cookie
会随着每个 HTTP 请求一起发送。

![image.png-213.6kB](https://image.3001.net/images/20220809/1660020393_62f1e6a9377080a8bfbd1.png!small)get_cookie_data
函数

### 数据加密

恶意软件使用 RSA-4096 和 AES-CBC 来加密发送到 C&C 服务器的数据，其中 RSA-4096
的公钥硬编码在二进制文件中，恶意软件在运行时利用 BCryptImportKeyPair 函数导入。

恶意软件在运行时通过生成 32 字节随机值获取 AES-CBC 的密钥，使用 RSA-4096 算法对这 32 字节加密回传 C&C 服务器。恶意软件和
C&C 服务器同时使用这些字节利用 BCryptGenerateSymmetricKey 生成 AES-CBC 的密钥，该密钥在随后的 HTTP
请求中用于加密和解密数据。

![image.png-358.7kB](https://image.3001.net/images/20220809/1660020394_62f1e6aa2c6298f0e9211.png!small)RSA
加密

![image.png-229.4kB](https://image.3001.net/images/20220809/1660020395_62f1e6abaccb89f78e7d5.png!small)AES
加密

## C&C 请求

恶意软件向 C&C 服务器发出的第一个 HTTP 请求是 `knock`，为带有 Cookie 的 POST 请求。请求中包含 32 字节随机值，用于生成
AES-CBC 密钥，而这 32 个字节是经过 RSA-4096 加密的。

![image.png-312.7kB](https://image.3001.net/images/20220809/1660020396_62f1e6ac801c86eb0fe7a.png!small)请求头

返回的响应在解密后，包含此后该主机与 C&C 服务器通信的 URL 路径。

随后，恶意软件发起 `submit`请求，将失陷主机相关环境信息回传，数据经过 AES-CBC 加密。环境信息如下所示：

> 操作系统
>
> 架构
>
> 已安装的反病毒软件
>
> 计算机名称
>
> 操作系统构建版本
>
> .NET 信息
>
> PowerShell 信息
>
> Python 信息（安装路径、版本等）
>
> 存储驱动器信息
>
> 环境变量
>
> 网络接口
>
> 管理员权限
>
> 正在运行的进程列表
>
> 代理信息
>
> 用户名
>
> 所有用户帐户的列表

目前恶意软件通过注册表项检测六个反病毒软件，分别为：Avast Software、Doctor Web、Kaspersky、AVG、ESET 和
Sophos。

最后，恶意软件会定期向 C&C 服务器发出 `ping`请求。如果响应 `_CRY`就继续保持轮询，如果响应 `_ACK`就会包含继续执行的命令。

## C&C 命令

恶意软件使用一个特定线程与 C&C 服务器通信，并使用另一个线程来执行从 C&C
服务器接收到的命令。为了保持线程同步，恶意软件利用事件和互斥锁。必须强调的是，所有通信都是经过 AES 加密的。

![image.png-101.4kB](https://image.3001.net/images/20220809/1660020397_62f1e6ade8d898f10652a.png!small)命令执行

### _SET 命令

> PING：此命令用于设置对 C&C 服务器的 ping 请求之间的睡眠周期
>
> PURG：未知命令
>
> EXIT：退出命令执行线程

### _REQ 命令

> EXEC：创建两个命名管道并将输入和输出重定向到这些管道，使用 ReadFile 从命名管道读取命令的输出，然后将`_DAT`附加到此数据，再进行
> AES 加密并发送到 C&C 服务器

![image.png-256.8kB](https://image.3001.net/images/20220809/1660020398_62f1e6aec1728eb7b2454.png!small)EXEC
命令

> UPLD：下载文件到失陷主机
>
> INFO：重新将 submit 的信息发回 C&C 服务器

![image.png-76.4kB](https://image.3001.net/images/20220809/1660020399_62f1e6af8e16f16d2a579.png!small)INFO
命令

> UPEX：在失陷主机下载文件并执行（UPLD + EXEC）
>
> DNLD：将失陷主机的文件上传回 C&C 服务器
>
> PROC：直接执行命令，不调用 cmd.exe
>
> UPPR：在失陷主机下载文件并执行（UPLD + PROC）
>
> SDEL：删除失陷主机的文件
>
> _DIR：列出指定目录的所有文件与属性（文件名、类型、所有者、创建时间、上次访问时间、上次写入时间、大小、权限）
>
> STCK：一次执行多个命令，按照接收顺序执行
>
> SCRN：屏幕截图后使用 AES-CBC 对图像进行加密并发送到 C&C 服务器
>
> INJC：下发要注入的代码并注入指定目标进程，使用 WriteProcessMemory 将代码写入远程内存，然后使用
> CreateRemoteThread 创建远程线程

![image.png-73kB](https://image.3001.net/images/20220809/1660020400_62f1e6b04eb41a1d97915.png!small)INJC
命令

> PSLS：使用 SystemProcessInformation 调用NtQuerySystemInformation
> 以检索所有正在运行的进程，将相关信息（PID、父进程 PID、进程名称、所有者）发回 C&C 服务器
>
> DMON：使用 CreateProcess 创建进程不回传输出
>
> UPDM：上传文件并执行（DMON 方式）

### SharpExecutor 和 PowerSession 命令

恶意软件还内嵌了两个 .NET 实现的 DLL 文件，分别为 WoodySharpExecutor 和
WoodyPowerSession。WoodySharpExecutor 支持恶意软件运行从 C&C 服务器接收的 .NET 代码，
WoodyPowerSession 支持恶意软件执行从 C&C 服务器接收的 PowerShell 命令和脚本。WoodyPowerSession
使用管道来执行这些 PS 命令：

![image.png-351.2kB](https://image.3001.net/images/20220809/1660020401_62f1e6b1133274214c44d.png!small)SharpExecutor
和 PowerSession 命令

DLL 支持的命令有：

> DN_B：使用 RunBinaryStdout 方法执行汇编代码
>
> DN_D：接收由代码、类名、方法名和参数组成的 base64 字符串数组，为攻击者提供对执行更精细的控制，如不将输出回传
>
> PSSC：接收 base64 编码的 PowerShell 命令并执行
>
> PSSS：接收 base64 编码的 PowerShell 脚本并执行
>
> PSSM：接收 base64 编码的字符串数组，解码后导入命令管道并调用

## 恶意软件清理

创建命令线程后，恶意软件就会使用 ProcessHollowing 技术从磁盘中删除自身。首先创建一个挂起的记事本进程，然后使用
NtWriteVirtualMemory 将 Shellcode 写入挂起的进程。再使用 NtSetContextThread 重置线程入口点并恢复线程。

![image.png-189.9kB](https://image.3001.net/images/20220809/1660020401_62f1e6b1e8ceca55878ce.png!small)自行删除

## 未知攻击者

研究人员未能对该恶意软件进行归因，暂时没有任何可靠的证据能指向特定的攻击者开发了 Woody RAT。

## IOC

> 982ec24b5599373b65d7fec3b7b66e6afff4872847791cf3c5688f47bfcb8bf0  
> 66378c18e9da070629a2dbbf39e5277e539e043b2b912cc3fed0209c48215d0b  
> b65bc098b475996eaabbb02bb5fee19a18c6ff2eee0062353aff696356e73b7a  
> 43b15071268f757027cf27dd94675fdd8e771cdcd77df6d2530cb8e218acc2ce  
> 408f314b0a76a0d41c99db0cb957d10ea8367700c757b0160ea925d6d7b5dd8e  
> 0588c52582aad248cf0c43aa44a33980e3485f0621dba30445d8da45bba4f834  
> 5c5020ee0f7a5b78a6da74a3f58710cba62f727959f8ece795b0f47828e33e80  
> 3ba32825177d7c2aac957ff1fc5e78b64279aeb748790bc90634e792541de8d3  
> 9bc071fb6a1d9e72c50aec88b4317c3eb7c0f5ff5906b00aa00d9e720cbc828d  
> ffa22c40ac69750b229654c54919a480b33bc41f68c128f5e3b5967d442728fb  
> kurmakata.duckdns[.]org  
> microsoft-ru-data[.]ru  
> 194.36.189.179  
> microsoft-telemetry[.]ru  
> oakrussia[.]ru  
> garmandesar.duckdns[.]org:444/uoqiuwef.html  
> fcloud.nciinform[.]ru/main.css

## 参考来源

> [MalwareBytes](https://www.malwarebytes.com/blog/news/2022/08/woody-rat-a-> new-feature-rich-malware-spotted-in-the-wild)

