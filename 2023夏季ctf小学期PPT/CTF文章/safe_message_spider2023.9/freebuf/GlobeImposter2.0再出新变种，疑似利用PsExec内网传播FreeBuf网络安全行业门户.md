**近日，深信服安全团队发现了GlobeImposter2.0勒索病毒新变种，该变种疑似利用微软官网工具PsExec进行内网传播并使用了新的勒索界面。截止目前，国内已在政府单位、建筑地产等行业发现多个感染案例。**

此外，我们观察到，国外用户也同时受到该变种侵害，Twitter安全研究账号GrujaRS同步发现该变种有活跃现象。

![](https://image.3001.net/images/20190920/1568944044_5d842fac55bc8.png!small)

本次发现的勒索病毒正是GlobeImposter2.0家族的新变种。勒索界面如下：

![](https://image.3001.net/images/20190920/1568944054_5d842fb6a52b7.png!small)

该 **变种** **文件加密** **后缀** 一共有21个：

>
> .Erenahen,.bobelectron，.ciphered，.tabufa，.saveyoudata，.saveyourdata,.hotprice8,.666decrypt666,.1ibertoned,.unlockassistant,.shelbyboom,AsabHadare,.helpinc,.Coockish,.rescuerr,.supporthelpgood,.decrypt019,.Saveyourdata,.decrypt2019,.helprobot,.telcomsupp2351,.Gamgamga

该变种使用的黑客邮箱有：

> bobelectron@cock.li
>
> bobelectron@tutanota.com
>
> Erenahen@cock.li
>
> Kishemez@tutano.com

##  **GlobeImposter家族简介**

GlobeImposter是近期非常活跃的勒索家族，首次出现在2017年5月份，此后，不断出现新的版本和变种；今年七月，更有“十二主神”系列爆发，国内医疗行业深受威胁。深信服安全团队一直持续关注并跟踪此勒索病毒家族，下图是深信服跟踪GlobeImposter勒索病毒演进的时间轴：

![](https://image.3001.net/images/20190920/1568944087_5d842fd7d2da4.png!small)

##  **GlobeImposter2.0最新变种详细分析**

在被勒索的主机中，发现勒索时间点生成了PsExec服务以及3个脚本文件：

![](https://image.3001.net/images/20190920/1568944103_5d842fe72adda.png!small)

PsExec是微软发布的一个轻量级telnet替代工具，使用者无需手动安装客户端软件即可执行其他系统上的进程，并且可以获得与控制台应用程序相当的完全交互性。微软官方介绍了该工具的安装和使用方法，并且提醒用户该工具会被恶意软件利用。

![](https://image.3001.net/images/20190920/1568944109_5d842fed471ed.png!small)

脚本文件内容如下，其功能为结束mssqlserver以及反病毒软件：

![](https://image.3001.net/images/20190920/1568944113_5d842ff1725e2.png!small)

##  **样本分析**

解密出内置rsa公钥信息，计算内置rsa公钥的sha256哈希，使用内置rsa公钥的sha256哈希作为aes密钥解密出加密文件后缀以及信息提示文件名称：

![](https://image.3001.net/images/20190920/1568944119_5d842ff744c83.png!small)

解密出文件夹白名单，后缀名白名单。详细文件夹名称如下：

> Windows, Microsoft, Microsoft Help, Windows App Certification Kit, windows
> Defender, ESET, COMODO, Windows NT, Windows Kits, Windows Mail, Windows
> Media Player, Windows Multimedia Platform, Nindows Phone Kits, Windows Phone
> Silverlight Kits, Windows Photo Viewer, Windows Portable Devices, windows
> Sidebar, WindowsPowerShel1, VIDIA Corporation, Microsoft. NET, Internet
> Explorer, Kaspersky Lab, McAfee, Avira, spytech software, sysconfig, Avast,
> Dr. Web, Symantec, Symantec_Client_Security, system volume information, **G,
> Microsoft Shared, Common Files, Outlook Express, Movie Maker, Chrome,
> Mozilla Firefox, Opera, YandexBrowser, ntldr, Wsus, ProgramData

获取%localappdata%者%appdata%目录，将自身拷贝过去。添加到Software\\\Microsoft\\\Windows\\\CurrentVersion\\\RunOnce下的BrowserUpdateCheck作为启动项，其会进行检测是否已被感染：

![](https://image.3001.net/images/20190920/1568944129_5d84300115f3b.png!small)

![](https://image.3001.net/images/20190920/1568944132_5d843004b6e61.png!small)

然后其会在用户的%pulbic%或者%ALLUSERPROFILE%下创建内置rsa公钥的sha256哈希为名称的文件，其中保存着用户ID信息以及生成的rsa公钥等信息：

![](https://image.3001.net/images/20190920/1568944146_5d8430128bb6e.png!small)

再对用户磁盘进行遍历，包括移动磁盘，固定磁盘以及网络磁盘(基本上是共享或者映射)然后对文件进行加密。

加密完之后会在用户temp目录下生成tmp.bat用来删除用户磁盘卷影，远程桌面连接信息，删除日志信息等：

![](https://image.3001.net/images/20190920/1568944153_5d84301949eb0.png!small)![](https://image.3001.net/images/20190920/1568944160_5d843020354a2.png!small)

然后创建一个cmd进程将自身删除：

![](https://image.3001.net/images/20190920/1568944164_5d843024afa0f.png!small)

##  **解决方案：**

针对已经出现勒索现象的用户，由于暂时没有解密工具，建议尽快对感染主机进行断网隔离。深信服提醒广大用户尽快做好病毒检测与防御措施，防范该病毒家族的勒索攻击。

##  **病毒检测查杀**

1、深信服为广大用户免费提供查杀工具，可下载如下工具，进行检测查杀。

64位系统下载链接：

> <http://edr.sangfor.com.cn/tool/SfabAntiBot_X64.7z>

32位系统下载链接：

> <http://edr.sangfor.com.cn/tool/SfabAntiBot_X86.7z>

2、深信服EDR产品、下一代防火墙及安全感知平台等安全产品均具备病毒检测能力，部署相关产品用户可进行病毒检测，如图所示：

![](https://image.3001.net/images/20190920/1568944171_5d84302b80495.png!small)

##  **病毒防御**

深信服安全团队再次提醒广大用户，勒索病毒以防为主，目前大部分勒索病毒加密后的文件都无法解密，注意日常防范措施：

> 1、及时给电脑打补丁，修复漏洞。
>
> 2、对重要的数据文件定期进行非本地备份。
>
> 3、不要点击来源不明的邮件附件，不从不明网站下载软件。
>
> 4、尽量关闭不必要的文件共享权限。
>
> 5、更改账户密码，设置强密码，避免使用统一的密码，因为统一的密码会导致一台被攻破，多台遭殃。
>
>
> 6、如果业务上无需使用RDP的，建议关闭RDP。当出现此类事件时，推荐使用深信服防火墙，或者终端检测响应平台（EDR）的微隔离功能对3389等端口进行封堵，防止扩散！
>
>
> 7、深信服防火墙、终端检测响应平台（EDR）均有防爆破功能，防火墙开启此功能并启用11080051、11080027、11080016规则，EDR开启防爆破功能可进行防御。
>
> 8、深信服防火墙客户，建议升级到AF805版本，并开启人工智能引擎Save，以达到最好的防御效果。
>
> 9、使用深信服安全产品，接入安全云脑，使用云查服务可以即时检测防御新威胁。
>
>
> 10、深信服推出安全运营服务，通过以“人机共智”的服务模式帮助用户快速扩展安全能力，针对此类威胁安全运营服务提供设备安全设备策略检查、安全威胁检查、相关漏洞检查等服务，确保第一时间检测风险以及更新策略，防范此类威胁。

最后，建议企业对全网进行一次安全检查和杀毒扫描，加强防护工作。推荐使用深信服安全感知+防火墙+EDR，对内网进行感知、查杀和防护。

 ***本文作者： 深信服千里目安全实验室，转载请注明来自FreeBuf.COM**  

