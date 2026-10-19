2023 年 5 月中旬，TA453（又名 Charming Kitten、APT42、Mint Sandstorm、Yellow
Garuda）伪装成皇家联合军种研究所（RUSI）的高级研究员，向媒体人发送钓鱼邮件进行攻击。美国一家专注于外交事务智库的专家收到了有关“全球安全背景下的伊朗”的项目反馈，并提供草稿进行审查。攻击者不仅表示会提供酬金，还提供了其他核安全专家的背书。TA453
最终使用云服务投递攻击链，让受害者会下载新开发的 PowerShell 后门 GorjoEcho。

## 角色扮演

随着 JCPOA 谈判的进行，伊朗方面发现自己日益孤立。TA453 继续扮演与中东事务和核安全有关的专家，针对与这些外交政策有关的专家发起攻击。

![image.png-171.8kB](https://image.3001.net/images/20230710/1688997577_64ac0ec9178ddf26941ea.png!small)前期钓鱼邮件

![image.png-420.9kB](https://image.3001.net/images/20230710/1688997577_64ac0ec9eae2f8e6f306b.png!small)后续钓鱼邮件

Proofpoint 的研究人员判断这些账户都是攻击者创建的模拟账户，而不是账户本身被窃。

## 复杂感染

在进行了电子邮件交互后，TA453 就会通过 Google Macro 发送一个恶意链接。该链接将攻击目标重定向到 Dropbox 的 URL，该 URL
可下载加密的 RAR 文件（Abraham Accords & MENA.rar）。压缩文件中包含一个名为 `Abraham Accords &
MENA.pdf.lnk`的 Dropper，后续会使用 PowerShell 代码从云服务商从下载后续 Payload。

![image.png-119.5kB](https://image.3001.net/images/20230710/1688997578_64ac0ecacd1a87e75314d.png!small)完整感染链

## 后续感染阶段

恶意软件使用的 Gorjol 函数通过 .txt 文件下载 base64 编码的数据，解码后如下所示：

![image.png-237.1kB](https://image.3001.net/images/20230710/1688997579_64ac0ecb8d3a2ae0d3b19.png!small)Borjol
函数

Borjol 通过合法的 Clever Cloud 服务使用 AES 加密的 HTTPS 链接与 fuschia-rhinestone.cleverapps[.]io 进行通信。返回的数据解密为另一个 Borjol 函数，该函数使用之前的变量并解密 PowerShell
后门 GorjolEcho。

GorjolEcho 首先显示一个诱饵 PDF 文档，该文档与钓鱼文档一致。后门将信息编码后回传给 C&C 服务器，如果 C&C 服务器响应除 400 或
200 以外的任何 HTTP 响应，都会显示韩语错误消息（大意为：哇，我们在做什么？）。收到有效响应后，GorjolEcho
就可以启动或者停止来自攻击者的命令。研究人员在分析时并未发现，但有可能受害者已经下载了被 Volexity 称为 POWERSTART 的恶意代码。

![image.png-440.5kB](https://image.3001.net/images/20230710/1688997580_64ac0eccb17db0ddc22d8.png!small)GorjolEcho
后门

## 苹果设备也不放过

TA453 发送了 GorjolEcho 后门后，忽然就意识到恶意代码无法在苹果设备上运行。一周后 TA453 再次发送钓鱼邮件，这次提供了在 Mac
操作系统上可以运行的感染链。

![image.png-486.6kB](https://image.3001.net/images/20230710/1688997581_64ac0ecdbc2bdfdfc1609.png!small)针对
Mac 操作系统的钓鱼邮件

邮件携带一个加密的 ZIP 文件，其中包含一个定制的 Mac 应用程序，该程序伪装成 RUSI 的 VPN 或者共享驱动器的样子。执行后，脚本会通过指定的
URL 下载后续 Payload。二阶段是名为 NokNok 的 bash
脚本，主要是后门程序。通过操作系统名称、主机名称与随机数来创建唯一标识，经过编码与加密后发送到 C&C 服务器。脚本期望的响应为 KillKill 或者
ModuleName，前者会终止运行，后者会执行响应的命令。

![image.png-80.3kB](https://image.3001.net/images/20230710/1688997582_64ac0ecec75e0db5804d4.png!small)NokNok

分析人员确定了四个相似的模块：

  * processes
  * informations
  * applications
  * persistence

![image.png-140.4kB](https://image.3001.net/images/20230710/1688997583_64ac0ecf9de85ed5c6ae3.png!small)多个模块

这些模块都是 base 脚本，旨在收集信息后回传至 C&C 服务器。processes 模块会使用 ps -aux 命令获取当前正在运行的进程列表：

![image.png-132.2kB](https://image.3001.net/images/20230710/1688997584_64ac0ed06a3f7237be5ec.png!small)processes
模块

information 模块使用 system_profiler 获取软件相关信息，特别是
SPSoftwareDataType（包含操作系统版本、运行时间、已安装软件等）。还会使用 ifconfig 收集网络相关信息，通过 base64
编码保存到 result.txt 进行回传。

![image.png-147.2kB](https://image.3001.net/images/20230710/1688997585_64ac0ed130ac79bb55655.png!small)information
模块

applications 模块也是类似的，使用 echo 列出已安装应用程序。persistence 模块首先释放 LaunchAgents
然后将硬编码密钥写入 Id.txt，继而通过 Finder 建立持久化。

![image.png-148kB](https://image.3001.net/images/20230710/1688997586_64ac0ed205d96a01f56fd.png!small)persistence
模块

TA453 很可能为 GorjolEcho 与 NokNok 分别量身定做了攻击模块，但功能是大体类似的。从代码来看，与 Goolge 此前披露的
Charming Kitten 十分相似。而且，NokNok 的部分功能也与 2017 年披露的 Charming Kitten Mac 恶意软件相似。

## 虚假文件共享网站

电子邮件中的恶意附件介绍了虚假文件共享服务的链接与凭据，该服务伪装成 RUSI Wing FTP 服务器。

![image.png-78.3kB](https://image.3001.net/images/20230710/1688997586_64ac0ed2d9d0f81d71031.png!small)虚假网站

该网站拒绝给出的用户名与密码，可能只是为了确定恶意软件投递成功。该网站可能对访问者进行了跟踪与指纹识别，分析人员并未发现异常。通过邮件确认，TA453
表示用户名密码是正确的，只要运行应用程序即可访问文件。

![image.png-54.6kB](https://image.3001.net/images/20230710/1688997587_64ac0ed376514d20ea8ad.png!small)错误消息

## 归因

发现的感染链与过去的 TA453 不同，但分析人员仍然高度可信地确认该攻击行动为 TA453 所为。Proofpoint 认为 TA453
主要是为了支持伊斯兰革命卫队（IRGC）的工作，特别是 IRGC 情报组织。

## IOC

> 464c5cd7dd4f32a0893b9fff412b52165855a94d193c08b114858430c26a9f1d  
> ddead6e794b72af26d23065c463838c385a8fdff9fb1b8940cd2c23c3569e43b  
> 1fb7f1bf97b72379494ea140c42d6ddd53f0a78ce22e9192cfba3bae58251da4  
> e98afa8550f81196e456c0cd4397120469212e190027e33a1131f602892b5f79  
> 5dc7e84813f0dae2e72508d178aed241f8508796e59e33da63bd6b481f507026  
> b6916b5980e79a2d20b4c433ad8e5e34fe9683ee61a42b0730effc6f056191eb  
> acfa8a5306b702d610620a07040262538dd59820d5a42cf01fd9094ce5c3487c  
> library-store[.]camdvr[.]org  
> filemanager.theworkpc[.]com  
> fuschia-rhinestone.cleverapps[.]io  
> 144.217.129[.]176

## 参考来源

> [Proofpoint](https://www.proofpoint.com/us/blog/threat-insight/welcome-new-> york-exploring-ta453s-foray-lnks-and-mac-malware)

