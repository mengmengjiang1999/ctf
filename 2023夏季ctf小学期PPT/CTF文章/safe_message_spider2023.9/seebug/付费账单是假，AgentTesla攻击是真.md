**译者：知道创宇404实验室翻译组  
原文链接：<https://www.fortinet.com/blog/threat-research/fake-purchase-order-used-to-deliver-agent-tesla>**

自网络钓鱼出现以来，欺诈性的付费账单一直是最常见的诱惑之一。通常的操作方法包括迎合接受者避免债务的愿望，尤其是在可能牵涉到商业利益的情况。

FortiGuard 实验室最近发现了一个有趣的仿冒电子邮件，它伪装成一份账单，发送给一家乌克兰制造企业，该企业从事原材料和化学品生产。电子邮件中包含一个
PowerPoint 附件，实际上一个复杂的、多阶段的手段，用于部署特斯拉 RAT (远程访问木马)。

这个攻击的独特之处在于使用了 PPAM，这是一种并不常见的文件格式。PPAM 是一个 Microsoft PowerPoint
外接程序，它为开发人员提供额外的功能，比如额外的命令、自定义宏和新工具。这个博客将详细说明感染过程和随后的恶意软件部署。

## 检查网络钓鱼邮件

像许多基于计算机的攻击一样，这次攻击开始于发送给乌克兰一个组织的钓鱼电子邮件。

![Figure 1.  E-mail to the target
recipient.](https://images.seebug.org/content/images/2022/03/09/1646792951000-1zefpz.png-w331s)
图1. 给目标收件人发电子邮件

撇开拼写和语法问题不谈，像大多数好的网络钓鱼攻击一样，这一条提供了明确时间，敦促收件人紧急审查所附的订单。

深入研究电子邮件及其来源，我们可以在邮件标题中看到一些附加信息。

![Figure 2.  E-mail headers showing the origin of the
message.](https://images.seebug.org/content/images/2022/03/09/1646792952000-2zeoil.png-w331s)
图2. 显示消息来源的电子邮件标题

![Figure 2b. Parked
page](https://images.seebug.org/content/images/2022/03/09/1646792955000-3fscfi.png-w331s)
图2b 停留页

电子邮件发自地址 194[.]99[.]46[.]38 ，即 slot0.warongsoto.com.。这是托管在普通的 VPS
服务器上。访问服务器时，我们注意到站点声明服务器控制面板由 VESTA 控制。最近的 CVE 数据显示 Vesta
控制面板受到远程命令执行和特权升级漏洞的影响，这些漏洞最终会导致系统的完全破坏([CVE-2020-10786](https://www.cvedetails.com/cve/CVE-2020-10786)
和 [CVE-2020-10787](https://www.cvedetails.com/cve/CVE-2020-10787))。

该域本身似乎处于无人管理状态，没有活动内容托管。它于2021年10月在美国注册。
原始电子邮件地址似乎没有提到实际的个人，搜索其他地方使用这个地址的其他案例也没有结果。

## 检查 dropper - 第一时期

### 第一阶段

植入最终的有效载荷发生在多个阶段，这实际上是一个非常复杂的操作。如图1所示，电子邮件的附件是文件“order001.ppam”。这是一个Microsoft
PowerPoint使用的插件文件格式，它包含一个恶意的宏，作为部署 Agent Tesla。

第一时期的第一个阶段始于打开 PPAM 附件来激活包含在内的宏。

![Figure 3. Visual Basic macro contained within
“order001.ppam”](https://images.seebug.org/content/images/2022/03/09/1646792960000-4etuvo.png-w331s)
图3 “order001.ppam”中包含的 visualbasic 宏

一旦宏执行完毕，它就会找到网址缩短服务 Bit.ly 下载下一阶段的植入程序。使用的地址是:
hXXp://www[.]bitly[.]com/awnycnxbcxncbrpopor/

### 第二阶段

对 Bitly 的访问将被重定向到 MediaFire
上的一个位置——一个文件托管站点(hXXp://download2261[.]mediafire[.]com/6lcqxbws032g/wctsdmx4dsh95xs/19.htm)。正如推断的那样，这是一场黑客攻击，且不仅仅是针对一个接收者。多个文件在几天内可用，如图4所示。

![Figure 4. MediaFire repository showing multiple other files from this
campaign.](https://images.seebug.org/content/images/2022/03/09/1646792961000-5uoepj.png-w331s)
图4. MediaFire 存储库显示了此攻击中的多个其他文件

每个文件都与下一步的下载位置非常相似(只有一些小的调整)。如果直接下载，会显示19.htm（图5）。

![Figure 5.  HTM file as it appears when
downloaded.](https://images.seebug.org/content/images/2022/03/09/1646792973000-6kejfy.png-w331s)
图5 下载时显示的 HTM 文件

如果我们将文件排列成更易读的格式，我们就能更好地了解它试图做什么。

![Figure 6. Key part of the HTM
file.](https://images.seebug.org/content/images/2022/03/09/1646792975000-7wqxpj.png-w331s)
图6. HTM 文件的关键部分

如图6所示，该文件尝试 `taskkill` 几个应用程序和服务，然后将一个计划任务添加到 Windows Task 调度器中。然后该脚本尝试从
MediaFire-hXXp://www[.]mediafire[.]com/file/otza6n31talvvle/19.dll下载并执行另一个文件。

### 第三阶段

虽然文件扩展名给人的感觉是 Microsoft 动态链接库(.Dll)，19.dll 实际上是一个 PowerShell
脚本，其中包含大量十六进制数据中的指令。

![Figure 7. HTM file as it appears when
downloaded.](https://images.seebug.org/content/images/2022/03/09/1646792977000-8eqxyc.png-w331s)
图7 下载时显示的 HTM 文件

一旦执行，十六进制数据将转换为在内存中运行的其他 PowerShell 命令。例如，添加新的注册表项以帮助实现持久性。

![Figure 8. Added entries to the Windows
Registry.](https://images.seebug.org/content/images/2022/03/09/1646792978000-9dmbdx.png-w331s)
图8. 向 Windows 注册表添加条目

如果捕获并审查，最引人注目的条目是两个大型压缩字节数组: STRDYFUGIHUYTYRTESRDYUGIRI。

![Figure 9. Large byte
arrays.](https://images.seebug.org/content/images/2022/03/09/1646792981000-10weeyr.png-w331s)
图9. 字节数组

如图9所示，之后字节数组进行解压缩以便使用。一旦解压缩，这些字节数组可以保存为可执行的 Windows
文件。STRDYFUGIHUYTYRTESRDYUGIRI 将把Agent Tesla 注入运行中的 Windows 程序。

19.dll 被重命名为19.ps1 后便作为普通 PowerShell 脚本执行。之后，它将尝试启动 Agent Tesla，然后将其注入
aspnet_compiler.exe 应用程序。

![Figure 10. On the left, the PowerShell script can be seen to be launching
aspnet_compiler.exe](https://images.seebug.org/content/images/2022/03/09/1646792984000-11ydbcn.png-w331s)
图10. 在左边，可以看到 PowerShell 脚本正在启动 aspnet_compiler.exe

## 检查恶意软件 - 第二时期

在其核心，Agent Tesla 是一个键盘记录器和远程访问木马。它将从键盘和剪贴板捕获任何信息，并将它们发送回
C2(命令和控制)服务器。在这个案例中，一旦注入 aspnet_compiler.exe进程, Agent
Tesla将启动和运行。有了注册表中的条目，即使主机重新启动，它也会持续运行。。

![Figure 11. Agent Tesla running inside a
debugger.](https://images.seebug.org/content/images/2022/03/09/1646792986000-12xpztd.png-w331s)
图11. Agent Tesla在调试器中运行

如图11所示，这个变体类似于 FortiGuard 实验室之前分析的一个[变体](https://www.fortinet.com/blog/threat-research/phishing-campaign-targeting-korean-to-deliver-agent-tesla-new-variant)。

它将在后台运行并观察用户，记录他们的操作并将其发送回攻击者。

![Figure 12.  Typical connection cycle to Agent Tesla’s
C2.](https://images.seebug.org/content/images/2022/03/09/1646792987000-13peghk.png-w331s)
图12. Agent Tesla的 C2的连接周期

## 总结

大多数黑客喜欢使用屡试不爽的诱饵，就像这里的仿冒诈骗电子邮件一样，因为他们未尝败绩。附在钓鱼电子邮件上的dropper显示，为了逃避现代安全防控，攻击技术持续演变和复杂化，需要穿过重重关卡才能到达最终有效载荷的释放点。

一旦最终部署到系统中，混淆和隐藏日常文件和进程的能力证明了Agent
Tesla是一个非常有强力和可怕的威胁。不幸的是，这种日益复杂化的趋势不太可能在短期内得到解决。

## **IOCs**

Sample SHA-256:

| DLL/PS1 SHA256 | |
------------------------------------------------------------ | |
27C7F5F2A21298C66A8EEF11DF73BFB1E9EEF7B84974CEF9AF695A7E216EFA21 | |
F86FDC385BA4467FD27093DFB6A642C705199AC3307D24096D7150FB6A80E8FD | |
9971EE4C59F1838C111CFAA0BC26A6C08B80FD7364C193F6D8DCA1A840D37B7F | |
D147E24E603FB17CE3C6EC839CC8AD07BCE06455037CC0E139CC68042153B7A7 | |
7659EC63CF7010158517AD0DFD3828F8B46592BDBC374D906BACD80A8500DA4B | |
D98D56AEB0A3DBD020C1F6ED9CFE0848A4D8C57DABBB064FBCD0305BDF8B329C | |
4FD01BF61C49579A40EFDD86D736930585AB3E79D9085177303DDCFF61480E26 | |
7384900E7BB02B1028D92A145CBE2BDB5E3283336C0E5E6014AFCD546B17B985 | |
EFDFD9CCDFB052FD7693403D1E8E085594C1B3B7ED221FD6021F794B5BA752C5 | |
90313F269F0583FBC179BEABAE2A48B1B53594F1FB4A27556861D5D82AD722EC | |
3C1636CF2A4296840D55A8BAF9ABB56E1C847C5D6E3A7DF0D7040050D017E54C | |
EC9E8CB17C92C4D6175FB3E715F73C4BEF833742168451398A99DE22F06FB52E | |
87B7F2C05F3E63821DE8AD22EE7ED9CA034CD61332EBAE3E1F76AF085696D5F8 | |
B5CF3D2594E148C458467C833B0D95976480FB054A7763E1F6DCF4187A61E1BE | |
0C3F881258EF9F1DB9A9923945AB07351DA8BA1A337AACCBCB6B5BD56AE080B3 | |
3B9D6FC6449B7B42E816A19C2B649A5E5CF4E724B2FCD93E56445DECA89FB850 | |
34CFFA6664C92F77EE60749E251A4ED18A15A3F0F61C78BCADA9EA86478681E0 | |
380C8FC86237A6B847F40870E9A15ADA1914F25174FF40838604354389EF9540 | |
B8403149F7A6E0FCCCB9C6E793BDCE7431385F86174D80B0C65F89A9C948A47F | |
D7E76887903EBD361112531017E140D2BFAAA816598C648F3B1238DCC6906BF1 | |
CB758A93876ACD5F7A314FDA6CCB97D0FC115ABFFF7F22637B629B1E91CF1970 | |
F3D9873EE798BF649A22C50E3DAEEBADFC127A405C0D8F54266B66C4377901E0 | |
1BD2383346BF8B1924C179B1616AF56A2BC4248717329B90E01FF13DB45ABE4F | |
5DC6B8CC1E9D1EE535752E6C5320280F864EA660B5BF8657F96B8E2B1053C57A | |
FA37BD017B82C1F7C545475F7A0CD786F81BC2CC024DA46CBDB4071B22ED4FFB |

| Fileless Tesla SHA256 | |
------------------------------------------------------------ | |
F69B85F5763CEC5A5DA5CE1152038FFEEF7A2A75600003ADBFEB3DC87502C8A8 | |
B409FF4CD1B8F18E80AFA98B3306440391FB5CBE294E6DA14E8146F63ECA2C6C | |
34EEEDAB0ABBEB1BAFFCCFDAEF74E54A7786F24BC5024B2F23A6F9385FEC9917 | |
6449D03A519CAB4B7C4E19D53D57A16AE69B70D7DF6BE815BCB57DC7395AB991 | |
E77DCCCB70AD61D50AC7E8C5DA1F79D5BC22B1F42A6651252EB449241BD6068B | |
C7840150DC084B1E0F6961EC61C39793BBED40FE17A7E24124DFE07F2C1A7B40 | |
F4542569E3F54CBC93AB835567507242DDDCAE2A84743DA103332EEFF3501ABD | |
851CC3973B096C8DA88E1EDB568C17750D019CA7F2528B3DA933D33D7F306A46 | |
C0C3A9CBDC769F3B86EAB40A9032769FE61E5E9B93CE7A93A0CC02EF43D4B9B5 | |
256F7CC33E3E359427702FF79E59C5EEA73164CC74D96B6F24E6BE19B62500E7 | |
445E6D6EBA924CC86005C107F329B248997AAC4149FBBD540A656FBA50A68C19 | |
D321AF1AF7D8B0A19B87897938B23ADB57C9089B73F2C15E0E2747B0071D1715 | |
822F2266CA284C5318E75C1286F7B4ED746E9289323B57462E227ED8D4D1AC8F | |
399B6B1AED4B62C165FE074DD9A43DEC0F0E1D5A50C89BFCA4A902CBFDBC17D5 | |
6BCDC49281217C3D8A82ED29A6BC89154885B08954AC3F78FA11BB09BF34A109 | |
1DF27F8D8B8572CB76D7275D7FE686C88F4297DA39095C1399B1E55459DFFDF6 | |
49BF5F9D59C27291FCB0D9F0C593DCB00CA9705E5D294E9C55353BDEFBC37273 | |
A155AB7DB6D22A44487D909BB040F5300B6E24283CDB7D7D902E7CE5CDD533BB | |
FD210DFB8C2F3B33FEEE191608EF58DD2816F08E9850DB734143115BA199690E | |
5F53A249455BB903C2C57A5CE23BFA6D069966034F74947A70037DEB1459DC88 | |
AD3BE25985B1DFA0A72C7CE59365F2AE7142FB4B2A78B7905D10AEB13998DDD4 | |
9783473EFECA3003D6A1B8DB8FE0E1A8AA291F170110D974C058806A25B4C419 | |
B1043F48E99EF5B98F4987E1FFD3200CD6A32B3427BA2762310FDEA58934D95C | |
3E99AA348FAFFDF2D73867C47067EA17A96CA36E5329E30C3A37F45B4274D165 | |
0ABBD4F17EC6DEDEFA188E39501B923286C56627ACB87FEC73271E459A383D0D |

Filename | SHA256  
---|---  
Order001.ppam |
DCA3AC723A130E56FB158C34C68E1C4B7D8577D0DBE9D8B859BFFF7ADA34D02E  
Loader | 4C0E2CB721585C480169B3804E17E2761BC5FE76584CF1375FCCDB33CA64D5A5  
  
## Network IOCs:

| 192[.]154[.]226[.]47 | |
--------------------------------------------------------- | |
hxxps://www[.]mediafire[.]com/file/s2w0i5rhl9e4wje/1.dll | |
hxxps://www[.]mediafire[.]com/file/u8t0g2vyrvoyldp/10.dll | |
hxxps://www[.]mediafire[.]com/file/hheln09oi15b266/11.dll | |
hxxps://www[.]mediafire[.]com/file/mra2u90srnmymxl/12.dll | |
hxxps://www[.]mediafire[.]com/file/e7fmuc053m1vdz5/13.dll | |
hxxps://www[.]mediafire[.]com/file/l3xh5g98wf5l4gv/14.dll | |
hxxps://www[.]mediafire[.]com/file/5d7sd1qat59dtpy/15.dll | |
hxxps://www[.]mediafire[.]com/file/2tpkh278oypz794/16.dll | |
hxxps://www[.]mediafire[.]com/file/hjjo0rc7izwy4is/17.dll | |
hxxps://www[.]mediafire[.]com/file/wy0e3mn2xyaqdhd/18.dll | |
hxxps://www[.]mediafire[.]com/file/otza6n31talvvle/19.dll | |
hxxps://www[.]mediafire[.]com/file/dsgxrjtpbyyzm7u/2.dll | |
hxxps://www[.]mediafire[.]com/file/mf3pufkmdshddyq/20.dll | |
hxxps://www[.]mediafire[.]com/file/ijdnf0wqv4e5frr/21.dll | |
hxxps://www[.]mediafire[.]com/file/c9gt9xi3l9srlhi/22.dll | |
hxxps://www[.]mediafire[.]com/file/pqk7p5p1vvcv5s1/23.dll | |
hxxps://www[.]mediafire[.]com/file/mqbl43fcem1fndd/24.dll | |
hxxps://www[.]mediafire[.]com/file/xz0guzs3g004f0i/25.dll | |
hxxps://www[.]mediafire[.]com/file/qe4ece114vu4n0o/3.dll | |
hxxps://www[.]mediafire[.]com/file/wbh1kq3u82mcso6/4.dll | |
hxxps://www[.]mediafire[.]com/file/x0o4nlef7snbixu/5.dll | |
hxxps://www[.]mediafire[.]com/file/xrnlyn4pjcmcfyf/6.dll | |
hxxps://www[.]mediafire[.]com/file/qbzdrs7ulvvzfay/7.dll | |
hxxps://www[.]mediafire[.]com/file/9q41qxg988c3opx/8.dll | |
hxxps://www[.]mediafire[.]com/file/xxbskabqkber6oq/9.dll |

## Mitre TTPs

Resource Development |  
---|---  
Stage Capabilities: Upload Malware | T1608.001  
Initial Access |  
Phishing: Spearphishing Attachment | T1566.001  
Execution |  
Command and Scripting Interpreter: PowerShell | T1059.001  
User Execution: Malicious File | T1204.002  
Persistence |  
Boot or Logon Autostart Execution: Registry Run Keys / Startup Folder |
T1547.001  
Defense Evasion |  
Process Injection: Portable Executable Injection | T1055.002  
Reflective Code Loading | T1620  
Credentials Access |  
Credentials from Password Stores: Credentials from Web Browsers | T1555.003  
Input Capture: Keylogging | T1056.001  
Discovery |  
Account Discovery | T1087  
Command and Control |  
Application Layer Protocol: Web Protocols | T1071.001  
  
* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1841/>

