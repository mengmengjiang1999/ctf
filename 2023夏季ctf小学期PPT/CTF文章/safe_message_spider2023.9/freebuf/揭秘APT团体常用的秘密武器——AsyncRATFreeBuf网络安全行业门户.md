AsyncRAT 是 2019 年 1 月在 [GitHub](https://github.com/NYAN-x-CAT/AsyncRAT-C-Sharp)上开源的远控木马，旨在通过远程加密链接控制失陷主机，提供如下典型功能：

> 截取屏幕
>
> 键盘记录
>
> 上传/下载/执行文件
>
> 持久化
>
> 禁用 Windows Defender
>
> 关机/重启
>
> DOS 攻击

GitHub 上提供了免责声明，但 AsyncRAT 仍然被许多攻击者，甚至是 APT 组织所广泛使用。Netskope
的研究人员最近发现了一个零检出的恶意脚本，该脚本通过 Amazon S3 存储桶下载 AsyncRAT 恶意软件。在分析时，VirusTotal
上的所有检测引擎都没有检出。

![image.png-93.4kB](https://image.3001.net/images/20220911/1662825808_631cb550bf8b23ddb453d.png!small)攻击链

## 阶段 01 - 零检出 Downloader

起始的批处理脚本，就是 VirusTotal 零检出的文件。

![image.png-65.5kB](https://image.3001.net/images/20220911/1662825809_631cb5517d3cd62aa316a.png!small)零检出
Downloader

尽管没有检测引擎检出，但该样本仍然能够被沙盒动态分析中的 Sigma 和 IDS 规则进行检出。

![image.png-276.1kB](https://image.3001.net/images/20220911/1662825810_631cb552322f508a2fcb6.png!small)Sigma
规则检测恶意行为

检测引擎未能静态检出可能是由于攻击者在文件中增加了超过一百个长字符串进行干扰。

![image.png-427.2kB](https://image.3001.net/images/20220911/1662825811_631cb5530e015f9fbbfac.png!small)注释字符串

字符串都是相同的日文文本，翻译过来都是无用的废话。

![image.png-125.7kB](https://image.3001.net/images/20220911/1662825811_631cb553cd42467188674.png!small)文本翻译

恶意的命令反而非常简单，夹杂在无意义的长字符串间。经过了混淆也可能是导致没有检出的原因之一。

![image.png-220.1kB](https://image.3001.net/images/20220911/1662825812_631cb5549d0a9af1a8fc4.png!small)恶意命令

恶意命令通过 PowerShell 从 Amazon S3 存储桶下载并执行后续阶段攻击。

## 阶段 02 - PowerShell

从 Amazon S3 存储桶下载的文件是一个 PowerShell 脚本。它首先在 `C:\ProgramData`中创建一个名为 `Not`的文件夹。

![image.png-18.2kB](https://image.3001.net/images/20220911/1662825813_631cb55562c52090ab578.png!small)创建目录

随后在目录中创建五个文件，链式执行另一个 PowerShell 脚本。

![image.png-114.9kB](https://image.3001.net/images/20220911/1662825813_631cb555e2a6a07ef421a.png!small)链式执行

最后一个 PowerShell 脚本中包含两个 PE 文件：

![image.png-115.3kB](https://image.3001.net/images/20220911/1662825814_631cb5569eaeafe59a5f0.png!small)PowerShell
脚本

第一个文件名为 `RunPE`，第二个文件用于将 AsyncRAT 注入到的合法进程中。

![image.png-78.6kB](https://image.3001.net/images/20220911/1662825815_631cb55783ec37ba819f6.png!small)运行命令

PowerShell 脚本将 RunPE 直接加载到内存中，因此所有 PE 文件都不会落地。

## 阶段 03 - RunPE

该文件负责使用 Process Hollowing 技术将 AsyncRAT 注入另一个进程，攻击者使用 .NET 开发该恶意软件并使用 Confuser
进行加壳。

![image.png-74.9kB](https://image.3001.net/images/20220911/1662825816_631cb5584185610af63ed.png!small)RunPE
文件信息

后续由 PowerShell 脚本将 RunPE 加载到内存中，调用 `Execute`方法。该方法接收可执行文件路径
`C:\Windows\Microsoft.NET\Framework\v4.0.30319\aspnet_compiler.exe`与参数中的
AsyncRAT 数据。

![image.png-134.8kB](https://image.3001.net/images/20220911/1662825816_631cb558f1117f0134de0.png!small)执行函数

去除混淆后，可以明确看出 AsyncRAT 是通过 Process Hollowing 注入的。

![image.png-85.3kB](https://image.3001.net/images/20220911/1662825817_631cb559ceb865058ee0c.png!small)函数调用

## 阶段 04 - AsyncRAT

AsyncRAT 样本在 2022 年 7 月 22 日编译。

![image.png-81.5kB](https://image.3001.net/images/20220911/1662825818_631cb55a7285960e49415.png!small)AsyncRAT
样本

样本没有经过混淆，可以直接进行反编译。

![image.png-39.2kB](https://image.3001.net/images/20220911/1662825819_631cb55b30891917bdcd0.png!small)反编译
AsyncRAT 样本

AsyncRAT 样本的主要执行流程如下所示：

![image.png-145.6kB](https://image.3001.net/images/20220911/1662825819_631cb55bc207361da612b.png!small)多个方法

AsyncRAT 的配置在 `InitializeSettings`函数中被解密。

![image.png-175.5kB](https://image.3001.net/images/20220911/1662825820_631cb55cb113821d3ebc0.png!small)解密的配置参数

AsyncRAT 在 CBC 模式下使用 AES-256 算法来解密字符串：

![image.png-181.6kB](https://image.3001.net/images/20220911/1662825821_631cb55d6fcdbab71c698.png!small)使用
AES 解密

该函数读取 base64 编码的字符串，前 32 个字节代表 HMAC，后面 16 个字节是解密向量 IV，其余字节是加密数据。

![image.png-94kB](https://image.3001.net/images/20220911/1662825822_631cb55e70456318f13f4.png!small)加密数据

研究人员提供了解密 AsyncRAT 的 [Python
脚本](https://github.com/netskopeoss/NetskopeThreatLabsIOCs/tree/main/AsyncRAT/script)。

![image.png-396.3kB](https://image.3001.net/images/20220911/1662825823_631cb55f1b644401691c2.png!small)配置解密

该样本并未启用反分析功能，但也使用了反虚拟化的技术，检查了硬盘大小、操作系统制造商和型号等。

![image.png-50.6kB](https://image.3001.net/images/20220911/1662825823_631cb55fe65500fb9ce98.png!small)AsyncRAT
反分析

样本还通过注册表与计划任务来实现持久化。

![image.png-96.3kB](https://image.3001.net/images/20220911/1662825824_631cb56080aea719523a3.png!small)持久化机制

AsyncRAT 将 C&C 地址和端口存储在其配置中，还提供了从 Pastebin 下载获取配置的选项。

![image.png-88.3kB](https://image.3001.net/images/20220911/1662825825_631cb5615e991531496ac.png!small)从
Pastebin 下载获取配置

AsyncRAT 与 C&C 服务器进行加密通信，通过界面控制设备。

![image.png-165.1kB](https://image.3001.net/images/20220911/1662825826_631cb5621146e528a4b24.png!small)AsyncRAT
控制面板

## 结论

本文介绍了 AsyncRAT 完整攻击流程的一个示例，攻击者甚至动用了完全未检测的脚本。由于 AsyncRAT
开源，攻击者都可以根据自己的需要进行功能修改。

## IOC

> 6d49c55e6231ae7af3b09287df08f440  
> 96e6e83b2a8e85153bcf6756403ae3e0  
> 228c44b9cc0e8c86c51fddaf3294bcf8  
> 370a1f36b649d6a041afca88c6ac0e55  
> 9c7994acb861283eab4675bb06ba4159  
> bed7fd2f5fc7183c0a509fc8f9d48ec9  
> 192a7c188e6ede340bdb4d518a4ed036  
> 2cb-586884e131b1c0ba96396ea4e70f6  
> fbf876a3676d0b6959639bc5c603d8e4  
> hxxps://buckotx.s3.amazonaws[.]com/x.png  
> bashamed[.]org:6666

## 参考来源

> [Netskope](https://www.netskope.com/blog/asyncrat-using-fully-undetected-> downloader)

