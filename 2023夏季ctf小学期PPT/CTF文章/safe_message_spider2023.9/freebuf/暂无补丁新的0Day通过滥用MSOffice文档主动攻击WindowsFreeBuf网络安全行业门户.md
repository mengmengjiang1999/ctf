微软周二警告称，一个影响Internet Explorer的0
day漏洞被积极利用，该漏洞正被用来通过利用武器化的Office文档来劫持易受攻击的Windows系统。

该漏洞在针对 Windows 10上的Office 365和Office 2019的针对性攻击中被利用。

跟踪为CVE-2021-40444(CVSS 分数：8.8)，远程代码执行缺陷源于MSHTML(又名 Trident)，这是现已停产的Internet
Explorer的专有浏览器引擎，在Office中用于在其中呈现Web内容Word、Excel和PowerPoint文档。

## 针对 Office 365 的持续攻击

该安全问题被标识为CVE-2021-40444，影响Windows Server2008 到2019和 Windows
8.1到10，其严重性级别为8.8(最高 10 级)。

该公司在一份公告中表示，微软意识到有针对性的攻击，这些攻击试图通过向潜在受害者发送特制的Microsoft Office文档来利用该安全漏洞。

![](https://image.3001.net/images/20210909/1631156279_61397837460a4def0a717.png!small)  

但如果Microsoft Office以默认配置运行，即在受保护的视图模式或Office 365的应用程序防护中打开来自Web的文档，则攻击会被阻止。

Protected View是一种只读模式，禁用了大部分编辑功能，而Application
Guard隔离不受信任的文档，拒绝他们访问公司资源、Intranet或系统上的其他文件。

具有活动的Microsoft Defender Antivirus和Defender for Endpoint(内部版本 1.349.22.0
及更高版本)的系统受益于防止尝试利用CVE-2021-40444的保护。

Microsoft的企业安全平台会将有关此攻击的警报显示为“可疑Cpl文件执行”。

来自多家网络安全公司的研究人员发现并报告了该漏洞。在一条推文中，EXPMON(漏洞利用监视器)表示，他们在检测到针对Microsoft
Office用户的“高度复杂的0 day攻击”后发现了该漏洞。

![](https://image.3001.net/images/20210909/1631156264_613978283f66910487346.png!small)  

EXPMON研究人员在Windows 10 上重现了对最新 Office 2019 / Office 365 的攻击。

EXPMON研究人员表示，袭击者使用的.docx文件，打开该文档后，该文档会加载 Internet Explorer引擎以呈现来自威胁参与者的远程网页。

然后使用网页中的特定ActiveX控件下载恶意软件。执行威胁是使用“一种称为‘Cpl文件执行’的技巧”完成的。

研究人员告诉BleepingComputer， **攻击方法是100%可靠的，这使得它非常危险。**

## 0-day攻击的解决方法

微软预计将发布安全更新作为其周二补丁月度发布周期的一部分，或者“根据客户需求”发布带外补丁。在此期间，Windows制造商敦促用户和企业禁用Internet
Explorer中的所有ActiveX控件，以减轻任何潜在的攻击。

Windows 注册表更新可确保所有站点的ActiveX都处于非活动状态，而已经可用的 ActiveX控件将继续运行。

用户应使用 .REG 扩展名保存下面的文件并执行它以将其应用于策略配置单元。系统重新启动后，应应用新配置。

由于CVE-2021-40444的更新尚不可用，因此他们发布了以下解决方法，以防止ActiveX 控件在Internet
Explorer和嵌入浏览器的应用程序中运行。

要禁用 ActiveX 控件，请按照以下步骤操作：

打开记事本并将以下文本粘贴到文本文件中。然后将文件另存为disable-activex.reg。确保您已启用文件扩展名的显示以正确创建注册表文件。

或者，您可以从此处下载注册表文件。

> Windows Registry Editor Version 5.00
>
>
> [HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows\CurrentVersion\Internet
> Settings\Zones\0]
>
> "1001"=dword:00000003
>
> "1004"=dword:00000003
>
>
> [HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows\CurrentVersion\Internet
> Settings\Zones\1]
>
> "1001"=dword:00000003
>
> "1004"=dword:00000003
>
>
> [HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows\CurrentVersion\Internet
> Settings\Zones\2]
>
> "1001"=dword:00000003
>
> "1004"=dword:00000003
>
>
> [HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows\CurrentVersion\Internet
> Settings\Zones\3]
>
> "1001"=dword:00000003
>
> "1004"=dword:00000003
>
>
> [HKEY_LOCAL_MACHINE\SOFTWARE\Policies\WOW6432Node\Microsoft\Windows\CurrentVersion\Internet
> Settings\Zones\0]
>
> "1001"=dword:00000003
>
> "1004"=dword:00000003
>
>
> [HKEY_LOCAL_MACHINE\SOFTWARE\Policies\WOW6432Node\Microsoft\Windows\CurrentVersion\Internet
> Settings\Zones\1]
>
> "1001"=dword:00000003
>
> "1004"=dword:00000003
>
>
> [HKEY_LOCAL_MACHINE\SOFTWARE\Policies\WOW6432Node\Microsoft\Windows\CurrentVersion\Internet
> Settings\Zones\2]
>
> "1001"=dword:00000003
>
> "1004"=dword:00000003
>
>
> [HKEY_LOCAL_MACHINE\SOFTWARE\Policies\WOW6432Node\Microsoft\Windows\CurrentVersion\Internet
> Settings\Zones\3]
>
> "1001"=dword:00000003
>
> "1004"=dword:00000003

找到新创建的 disable-activex.reg并双击它。当显示 UAC 提示时，单击“ 是” 按钮以导入注册表项。

重新启动计算机以应用新配置。

重新启动计算机后，Internet Explorer 中的 ActiveX 控件将被禁用。

当 Microsoft 针对此漏洞提供官方安全更新时，您可以通过手动删除创建的注册表项来删除此临时注册表修复程序。

或者可以利用此reg文件自动删除条目。

微软不断披露的安全漏洞说明，软件中的安全漏洞为企业遭到网络攻击提供了巨大的潜在风险。作为网络系统中最基础的部分，软件安全在网络安全中起到重要的作用。尤其网络犯罪团伙不断扫描网络系统中的安全漏洞加以利用，提升软件安全成为现有网络防护手段的重要补充。建议企业在软件开发过程中及时通过[源代码安全检测](https://www.woocoom.com/b031.html)查找代码缺陷及运行时的安全漏洞，在编码阶段将可见的安全漏洞扼杀在摇篮，不给犯罪分子留下可乘之机，同时也能将企业修复漏洞成本降至较低水平。

  

> 参读链接：
>
> https://www.woocoom.com/b021.html?id=5155e22b040f47faa05867c408c7735a
>
> https://www.bleepingcomputer.com/news/security/microsoft-shares-temp-fix-> for-ongoing-office-365-zero-day-attacks/

