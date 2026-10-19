近期公开的WebSVN命令注入漏洞（CVE-2021-32305）发现在野利用样本。在2021年5月发现并修补了关键命令注入漏洞，在一周内攻击者就利用该漏洞部署了Mirai
DDoS恶意软件的变体。

## 漏洞原因与补丁分析

与许多源代码浏览工具一样，WebSVN允许用户搜索修订历史记录来查找代码的变化。这些搜索是向后端PHP发送请求完成的。

![1630974714_6136b2fa3ff2cafa68453.png!small?1630974711985](https://image.3001.net/images/20210907/1630974714_6136b2fa3ff2cafa68453.png!small?1630974711985)

在2.6.1之前的版本中，用户的搜索查询在shell命令中不会转义。在include/svnlook.php中，函数getListSearch负责将搜索查询的命令参数连接起来并创建shell命令。

![1630974788_6136b344561705f88aeb1.png!small?1630974786030](https://image.3001.net/images/20210907/1630974788_6136b344561705f88aeb1.png!small?1630974786030)

include/command.php中runCommand函数最终将命令传递给proc_open函数执行。此函数文档中警告如下：

![1630974871_6136b3977360fe24d9f72.png!small?1630974869145](https://image.3001.net/images/20210907/1630974871_6136b3977360fe24d9f72.png!small?1630974869145)

用户输入转义不正确时，搜索查询中包含特殊字符可实现代码执行。为了修复此漏洞，需要先执行escapeshellarg判别用户输入。

![1630975007_6136b41f8897b564601e9.png!small?1630975005222](https://image.3001.net/images/20210907/1630975007_6136b41f8897b564601e9.png!small?1630975005222)

另一种解决方案是允许proc_open通过传递字符串数组作为第一个参数来自动转义和引用命令。这种方法更简洁，更易于维护。但是，它需要修改大量代码，并且与旧版本的PHP不兼容。

> proc_open(['svn', 'list', '-R', '--search', $searchstring, '--xml'], ...);

## 在野利用

CVE-2021-32305公布后不久，发现攻击者在野利用。攻击示例：

![1630975243_6136b50b3811296797ee5.png!small?1630975240908](https://image.3001.net/images/20210907/1630975243_6136b50b3811296797ee5.png!small?1630975240908)

攻击者利用命令注入漏洞下载shell脚本并感染系统。攻击者在攻击时不知道目标环境细节信息，包括web服务器操作系统和处理器体系结构等。攻击的下一步中会使用的shell脚本解决此问题：

![1630975380_6136b594f3067952a5f2d.png!small?1630975378753](https://image.3001.net/images/20210907/1630975380_6136b594f3067952a5f2d.png!small?1630975378753)

针对12种不同的体系结构提供了不同的恶意Linux二进制文件。

## 恶意软件分析

对该恶意软件的分析表明，该软件用于DDoS攻击，并与Mirai家族共享部分代码。为了减小可执行文件的大小，每个文件都使用UPX进行压缩。恶意软件运行后，它会不断尝试通过666端口连接C2服务器。一旦建立连接，它就会使用自定义的TCP协议进行通信，发送架构信息，然后等待攻击者的命令。

![1630975597_6136b66ddc8b85f5620d4.png!small?1630975595577](https://image.3001.net/images/20210907/1630975597_6136b66ddc8b85f5620d4.png!small?1630975595577)

恶意软件主要目的是发起DDoS攻击，分析的样本中有八种类型的攻击，每种攻击都是针对不同类型的目标而设计。下表显示了攻击者可发送的命令：

![1630975723_6136b6ebd6de96b6bb4e0.png!small?1630975721670](https://image.3001.net/images/20210907/1630975723_6136b6ebd6de96b6bb4e0.png!small?1630975721670)

## IOC

75.119.143[.]229

e6f20e73af6cc393dd139b32117a8681e15edfe61c157f3509d1e740184b3d5c

c782f9cdec637503472bc62d25348cefccc3de58244441547f3e2ed9b22c6c93

63c2cae1f3d04d81a4a1dcd773c62d7e9a71cf7e3ae0c5a9f931353e86f11651

3cc3d7d32e8c85e0c594ca5cb2ecfbfba66ebbc1853bcb02c2a39fce9f238dbc

dc7cf2212f09482ac034eb7e9f89ef0cec8bc9532d4fe2db8a880c2e1e4ee8a2

8cc43db17480170fac3213518fe18d52a5648ce04060561d6359d6c589a4321c

b09c85e75f65a9acc4693957caf4b4c56dd808c7d0d657c1bc9f74a1bd772abe

a55a2318e95dcfbe2d2082ee569642034ab05168fa0142ff1009798131b61f52

b43fd19dfeeb89507f9de162e7a727fa6024ca4b1d19cb5c44e53755200f2b66

7dc972346b9f82709bbcaabc30f126984468e60f2b085091471a9796ac4539b9

f4d851908e900d9201597f898cbb4420772a935901f25a77b31fc80e7cbc88b3

889cc2a3e06c5770ff23017aa067cd8a01b8b410e143e9da63542ead7ce484da

## 原文链接

[unit42](https://unit42.paloaltonetworks.com/cve-2021-32305-websvn/)

