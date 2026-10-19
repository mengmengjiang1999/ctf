近几个月来，卡巴斯基发表了多篇安全研究报告，如关于针对巴西的恶意软件、关于CEO欺诈企图、关于Andariel、关于LockBit勒索家族等等。在这篇文章中，重点论述了LockBit勒索病毒新变种LockBit
Green的相关报告。

![1687969236_649c5dd4c5fc21e61ae2b.jpg!small?1687969239676](https://image.3001.net/images/20230629/1687969236_649c5dd4c5fc21e61ae2b.jpg!small?1687969239676)

##  **最新研究：LockBit Green & Multi-platform LockBit **

### LockBit Green

LockBit是目前活跃且多产的勒索软件家族，他们攻击的目标是世界各地的企业。随着时间的推移，他们采用了 BlackMatter 和 DarkSide
等其他勒索软件团伙的代码，使潜在的附属机构更容易操作勒索软件。

从今年2月开始，我们检测到一个新的变种，名为 "LockBit
Green"，它借用了现已解散的Conti团伙的代码。根据卡巴斯基威胁归因引擎（KTAE），LockBit包含了25%的Conti代码。

![1687969300_649c5e1489770757a7bc2.png!small?1687969303489](https://image.3001.net/images/20230629/1687969300_649c5e1489770757a7bc2.png!small?1687969303489)

KTAE 显示了 LockBit Green 和 Conti 之间的相似之处

被采用的代码中，有三块非常突出：勒索软件说明、命令行选项和加密方案。采用赎金说明是最没有意义的，LockBit这种行为让我们也摸不着头脑。在命令行选项方面，该小组添加了
Conti 的选项，以便在 Lockbit 中使用。Lockbit Green 中可用的所有命令行选项有：

 **命令行**|  **功能性**  
---|---  
-p folder| 使用单线程加密选定的文件夹  
-m local| 加密多个线程中的所有可用驱动器，每个驱动器  
-m net| 加密多个线程中的所有网络共享，每个线程  
-m all| 加密多个线程中的所有可用驱动器和网络共享，每个线程  
-m backups| 标记无法在检测到的版本上使用，但在勒索软件内部进行编码  
\- size chunk| 仅加密部分文件的功能  
-log file.log| 可以记录勒索软件执行的每个操作  
-nomutex| 跳过突变器的创建  
  
最后，LockBit采用了Conti的加密方案。该小组现在使用自定义ChaCha8实现，使用随机生成的密钥和随机数来加密文件，并使用硬编码的公共 RSA
密钥保存/加密。

![1687969567_649c5f1fc5e827165214d.png!small?1687969571067](https://image.3001.net/images/20230629/1687969567_649c5f1fc5e827165214d.png!small?1687969571067)

两个系列之间的二进制差异

### 多架构的LockBit

我们最近偶然发现了一个上传到多重扫描仪的 ZIP 文件，其中包含多种架构的 LockBit 示例，如 Apple M1、ARM v6、ARM
v7、FreeBSD 等。那么，值得思考的问题就是“代码库相似性怎么样？”。

为此，我们使用了 KTAE：只需放入下载的 ZIP 文件就可以看到所有样本均源自 LockBit Linux/ESXi 版本。

![1687969616_649c5f50a98191564345e.png!small?1687969619606](https://image.3001.net/images/20230629/1687969616_649c5f50a98191564345e.png!small?1687969619606)

与 LockBit Linux 共享源代码

对样本的进一步分析使我们相信，LockBit正在各种架构上测试他们的勒索软件，而不是将其部署在野外。例如，macOS的样本是无符号的，所以它不能按原样执行。此外，字符串的加密方法很简单：一个字节的XOR。尽管如此，我们的发现表明，LockBit将在不久的将来瞄准更多的野外平台。

##  **回溯新型变种勒索软件LockBit Green的发展**

 **恶意软件家族**

|

LockBit  
  
---|---  
  
 **发布日期**

|

2023年2月20日  
  
 **威胁类型**

|

勒索软件  
  
 **描述**

|

最近，LockBit 勒索软件组织发布了一种新的勒索软件，称为 LockBit Green。最新的变种是基于泄露的 Conti 勒索软件源代码。这也遵循
LockBit 从其他现有勒索软件创建新变种的趋势。例如，他们之前发布了 LockBit Black，它与 BlackMatter 勒索软件非常相似。  
  
2022 年 2月，一位匿名人士使用 Twitter 账户“@ContiLeaks”发布了有关 Conti 组织的信息，包括 Jabber
聊天日志、有关其基础设施的详细信息、内部文档以及 Conti 勒索软件的源代码。2022 年 5 月，Conti
勒索软件组织决定重组并重新发起这一勒索软件。下图是Conti勒索软件和LockBit
Green的主要功能代码，逻辑非常相似。此外，它们都使用相同的名为“hsfjuukjzloqu28oajh727190”的突变器。LockBit Green
使用新的基于 Conti
的加密器。LockBit家族自己的加密器工作也是正常的，使用基于Conti的新加密器表明这两个勒索软件集团之间有合作。重用和改编竞争对手的源代码可以帮助减少开发成本和时间。

以下是LockBit 勒索软件家族的发展历史：

2019年9月

|

LockBit 攻击始于 2019 年。起初，它被称为“ABCD 勒索软件”，后来更名为 LockBit。  
  
---|---  
  
2021 年 6 月

|

LockBit 2.0 于 2021 年 6 月出现，引入了双重勒索技术和跨 Windows 域的设备自动加密。  
  
2021 年 10 月

|

LockBit 开始渗透 Linux 服务器，目标是 ESXi 服务器。LockBit 勒索软件组织还推出了 StealBit，一种用于加密的恶意软件工具。  
  
2022 年 6 月

|

LockBit 3.0，也称为 LockBit Black，于 2022 年 6 月被发现，引入了第一个勒索软件漏洞赏金计划，并泄露了新的勒索策略和
Zcash 加密货币支付选项。LockBit 3.0 的代码与著名的 BlackMatter 和 DarkSide 勒索软件非常相似。  
  
2022 年 9 月

|

2022 年 9 月，一名据称心怀不满的开发人员在 Twitter 上泄露了 LockBit 3.0
加密器的构建器。这对勒索软件组织来说是一个打击，因为构建工具的数据允许任何人使用加密器、解密器和专用工具启动自己的勒索软件套件，并以某些方式启动解密器。Bl00dy
勒索软件团伙使用泄露的构建工具开发了一种加密器，并将其用于对乌克兰企业的攻击。  
  
2023 年 1 月

|

LockBit勒索软件团伙发布了LockBit Green，该软件基于泄露的Conti勒索软件源代码。  
  
在这次勒索软件攻击中发现了两个样本。第一个样本LBB.malz是一个 32 位勒索软件，在 LockBit 系列中称为
LockBitBlack。样本分析可参见
<https://mp.weixin.qq.com/s/zT1GbqXFkj0FHiUhNlisZg>。第二个样本LBG64.malz是一个名为
LockBit Green 的 64 位勒索软件，它是 LockBit 3.0 的新成员。下面主要针对LBG64.malz进行分析。

 **文件名**

|

 **哈希值**

|

 **编码时间**  
  
---|---|---  
  
LBG64.malz

|

6147afcb98efab7f0621a910a843878c

|

2022/12/26  
  
马尔兹LBG

|

426eea06802387c3a24e2eceb892600e

|

2022/7/14  
  
LBG64.malz执行后，默认会为加密文件添加后缀“.fb7c204e”。勒索信息文件的名称为“!!!-Restore-My-Files-!!!.txt”，如下图所示。每个受害者都有一个唯一的 ID。受害者可以使用 Tor
浏览器或普通浏览器通过链接与攻击者取得联系。赎金票据没有说明赎金金额，但建议受害者不要联系网络保险公司和数据恢复组织，并解释了原因。

 **勒索信：!!!-Restore-My-Files-!!!.txt**

![1687969796_649c600497e5bbd2d69a1.png!small?1687969799689](https://image.3001.net/images/20230629/1687969796_649c600497e5bbd2d69a1.png!small?1687969799689)

 **加密文件**

![1687969834_649c602a6cea0d0f16956.png!small?1687969837202](https://image.3001.net/images/20230629/1687969834_649c602a6cea0d0f16956.png!small?1687969837202)

 **MITRE ATT** **& CK**

 **操作**

|

 **战术**

|

 **技术**

|

 **子技术**  
  
---|---|---|---  
  
使用 GetLogicalDriveStringsW() 获取磁盘驱动器的类型并枚举从C: **\** 到Z:\的所有磁盘驱动器

|

发现 (TA0007)

|

文件和发现 (T1083)

|

不适用  
  
使用 AES-256 和 XChaCha20 加密

|

影响（TA0040）

|

数据加密以提高影响力 (T1486)

|

不适用  
  
动态解析 API 和字符串

|

防御规避 (TA0005)

|

反混淆/解码文件或信息 (T1140)

|

不适用  
  
端口 445 和 IPC$ 共享的横向移动

|

横向运动 (TA0008)

|

远程服务 (T1021)

|

SMB/Windows 管理员共享 (T1021.002)  
  
调用SetFileAttributesW设置读写权限

|

防御规避 (TA0005)

|

文件和目录权限修改 (T1222)

|

Windows 文件和目录权限修改 (T1222.001)  
  
使用 CreateToolhelp32Snapshot、Process32First 和 Process32Next 枚举系统中所有正在运行的进程

|

发现 (TA0007)

|

流程发现 (T1057)

|

不适用  
  
枚举网络共享的名称，例如IPC$共享

|

发现 (TA0007)

|

网络共享发现 (T1135)

|

不适用  
  
使用wmic.exe删除 volume shadows

|

影响（TA0040）

|

禁止系统恢复 (T1490)

|

不适用  
  
使用wmic.exe删除 volume shadows副本

|

执行（TA0002）

|

Windows 管理规范 (T1047)

|

不适用  
  
> 更多详细内容可参考：<https://www.sangfor.com/farsight-labs-threat-> intelligence/cybersecurity/lockbit-green-ransomware-conti-based-encryptor>

## 总结

企业勒索软件防御策略：

  * 不要在外部网络上提供服务。如果非要打开，请使用强密码。
  * 不要打开可疑的电子邮件，尤其是其中的链接和附件。在打开未知文件之前使用防病毒软件对其进行扫描（如果必须这样做）。
  * 安装防病毒软件，定期进行系统扫描，删除检测到的威胁，并定期安装更新和补丁。
  * 通过官方认证渠道下载产品，并使用官方开发者提供的工具/功能激活和更新产品。不建议使用非法激活工具和第三方下载程序，因为它们通常用于分发恶意内容。
  * 对重要数据实施双备份策略或备份到云端。

## 参考来源：

> <https://securelist.com/crimeware-report-lockbit-switchsymb/110068/>
>
> <https://www.sangfor.com/farsight-labs-threat-> intelligence/cybersecurity/lockbit-green-ransomware-conti-based-encryptor>

