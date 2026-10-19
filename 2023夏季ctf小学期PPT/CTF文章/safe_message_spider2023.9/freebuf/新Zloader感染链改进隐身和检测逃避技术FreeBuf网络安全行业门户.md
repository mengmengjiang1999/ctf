## ZLoader——Zeus 银行木马的积极变种

ZLoader（又称 Terdot）于 2016 年被首次发现，是臭名昭著的 Zeus 银行木马的一个变种。目前，该恶意软件仍然在积极开发中，平均每周发布
1 到 2 个新版本。

ZLoader 是一种典型的银行木马，通过窃取
Cookie、密码和任何敏感信息来获利。它攻击世界各地金融机构的用户，还为勒索软件和其他恶意软件提供入口。其较新的版本实现了一个 VNC
模块，支持通过隐蔽信道远程访问失陷主机。ZLoader 主要依靠 DDE 和宏代码混淆技术来通过精心设计的文档投递最终 Payload。

最近发现感染链演化包括动态创建代理、从远程服务器下载的 Payload 等。与此同时，感染链通过禁用 Windows Defender 并依靠 LOLBAS
技术来逃避检测，从而实现更高级别的隐蔽性。![](https://image.3001.net/images/20210920/1632150894_6148a56e55d7aaefa338e.jpg!small)

## 技术分析

恶意软件通过 Google Adwords 发布的 Google 广告下载的。

> 用户首先在 Goolge 检索中发现下载软件的网站，例如`team viewer download`
>
> 点击广告后会被重定向到攻击者控制下的虚假 TeamViewer 网站。
>
> 用户被诱骗下载带有数字签名的 MSI 格式的虚假恶意软件

用户点击广告会通过 aclk 页面重定向，攻击者使用 Google Adwords 获取流量：

    
    
    hxxps://www.google.com/aclk?sa=L&ai=DChcSEwiMusngi8_yAhVbbm8EHYpXDh0YABABGgJqZg&ae=2&sig=AOD64_05er1E772xSHdHTQn_3lAIdsmPxA&q&adurl&ved=2ahUKEwjV8cHgi8_yAhXPaM0KHTCBDeAQ0Qx6BAgCEAE&dct=1

在重定向后，用户会通过 `hxxps://team-viewer.site/download/Team-Viewer.msi`下载恶意文件 `Team-Viewer.msi`。

伪造的 TeamViewer 安装程序，签名时间是 2021-08-23 10:07:00，网络犯罪分子设法获取了加拿大一家软件公司
Flyintellect 的有效证书。当然，公司在 2021 年 6 月 29 日注册，攻击者也可能是为了获取证书而注册的公司。

通过证书可以发现使用相同证书的其他样本，攻击者不仅针对 TeamViewer 也针对其他发起攻击，例如 `JavaPlug-in.mis`、`Zoom.mis`和 `discord.msi`。

撰写本文时，并不能在 VirusTotal 中发现这几个样本。

## 绕过防御

`.msi`是第一阶段的 Dropper，在目录中创建随机合法文件 `C:\Program Files (x86)\Sun Technology
Network\Oracle Java SE`。创建文件夹后，通过 `cmd.exe /c setup.bat`执行。

启动感染链的第二阶段，`updatescript.bat`将通过 Invoke-WebRequest 从
`hxxps://websekir.com/g00glbat/index/processingSetRequestBat/?servername=msi`下载后续恶意软件，接着执行第三阶段
`cmd /c updatescript.bat`。

第三阶段中，通过 Set-MpPreference 禁用所有 Windows Defender 模块，然后利用 `Add-MpPreference`对
Windows Defender 隐藏恶意软件的所有组件。

而第四阶段的 Dropper 通过 `hxxps://pornofilmspremium.com/tim.EXE`保存为 `tim.exe`。执行是通过
`explorer.exe tim.exe`实现的，这一般会触发 EDR
对父子进程关系的检测。![](https://image.3001.net/images/20210920/1632151024_6148a5f04701b9e9244d7.jpg!small)

`tim.exe`是 Windows 程序 `wextract.exe`植入后门的版本，嵌入了多个额外的资源，如
`RUNPROGRAM`、`REBOOT`和
`POSTRUNPROGRAM`。![](https://image.3001.net/images/20210920/1632151087_6148a62fa9ed006066419.jpg!small)

后门会创建新的恶意批处理文件 `tim.bat`，通过 `hxxps://pornofilmspremium.com/tim.dll`下载最终的
ZLoader DLL 文件并利用 `nsudo.bat`异步执行。

## 提权

`nsudo.bat`通过验证对 SYSTEM 配置单元的访问权限来检查当前的执行上下文是否具有权限。

负责提权的脚本片段如下所示：

    
    
    :UACPromptecho Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"set params = %*:"="echo UAC.ShellExecute "cmd.exe", "/c %~s0 %params%", "", "runas", 1 >> "%temp%\getadmin.vbs""%temp%\getadmin.vbs"del "%temp%\getadmin.vbs"exit /B

权限提升后，脚本执行禁用 Windows Defender 的步骤。将名为 NSudo 的程序重命名为 `javase.exe`，通过
`hxxps://pornofilmspremium.com/javase.exe`下载而来。攻击者利用此程序来生成具有
`TrustedInstaller`权限的进程。

该脚本 `autorun100.bat`下载文件并放置在启动文件夹
`%USERPROFILE%\AppData\Roaming\Microsoft\Windows\Start
Menu\Programs\Startup`，该脚本确保 WinDefend 服务在下次启动时被删除。

`nsudo.bat`脚本通过注册表
`HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System\EnableLUA`禁用
UAC。

## ZLoader

`tim.dll`通过 `regsvr-32.exe`执行，创建注册表
`HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run\Iwalcacvalue:
regsvr-32.exe /s C:\Users\[REDACTED]\AppData\Roaming\Kyubt\otcyovw.dll`。

利用线程劫持的进程注入技术脱壳：

    
    
    VirtualAllocEx() -> WriteProcessMemory() -> GetThreadContext() -> SetThreadContext() -> ResumeThread()

解密 DLL
并跳转入口点：![](https://image.3001.net/images/20210920/1632151091_6148a633d17281b19efe2.jpg!small)

一旦内存被写入远程进程，从进程内存中可以提取脱壳后的 DLL。将 DLL 文件与 ZLoader 的 Payload 比较，相似度为
92.62%。![](https://image.3001.net/images/20210920/1632151099_6148a63b0d9e19e2b7676.jpg!small)

## 基础设施

分析的样本属于 `Tim`僵尸网络。从失陷主机中发现的一个 C&C 域名 `mjwougyhwlgewbajxbnn.com`直到 2021 年 8 月
25 日一直解析到 `194.58.108.89`，在 8 月 26 日切换到 `195.24.66.70`。

`194.58.108.89`属于 ASN 48287 – RU-CENTER，部署了 350 个域名，形成了 ZLoader 的基础设施架构。

域名中发现了 `gate.php`，这是 ZLoader 僵尸网络的指纹，所有域名都是在 2021 年 4 月至 8 月期间注册的，并且在 8 月 26
日切换到 `195.24.66.70`上。

## 针对金融机构

新出现的 ZLoader 的攻击行动是有针对性的，Payload 中被嵌入 AU 与 DE 的域名列表，并包含一些通配符字符串，拦截对特定金融机构的 Web
请求。

    
    
    @https://*commerzbank.de*@https://*.de/*/entry*@https://*.de/banking-*/portal?*@https://*.de/banking-*/portal;*@https://*.de/portal/portal*@https://*.de/privatkunden/*@https://*.de*abmelden*@https://*.de/de/home*@https://*.de/en/home*@https://*.de/fi/home*@https://*banking.sparda.de*@https://*banking.sparda-*@https://*banking.sparda.de/wps/loggedout.jsp@https://*meine.deutsche-bank.de/trxm/db*@https://*banking.berliner-bank.de/trxm*@https://*meine.norisbank.de/trxm/noris*@https://*targobank.de*@https://banking4.anz.com/IBAU/BANKAWAY*@https://banking.westpac.com.au/*@https://www1.my.commbank.com.au/netbank/Portfolio/Home/*@https://ibanking.stgeorge.com.au/ibank/*@https://ibanking.banksa.com.au/ibank/*@https://ibanking.bankofmelbourne.com.au/ibank/*@https://online.macquarie.com.au/*@https://ob.cua.com.au/ib/*@https://banking.bendigobank.com.au/banking*@https://internetbanking.suncorpbank.com.au/*@https://www.ing.com.au/securebanking/*@https://ib.nab.com.au/*@https://online.beyondbank.com.au/*@https://ib.greater.com.au*@www.independentreserve.com*@www.coinspot.com.au*@https://auth.btcmarkets.net/*

通过对 `mjwougyhwlgewbajxbn.com`通信模式的分析，可以发现大部分映射流量。

## 结论

ZLoader 构建的攻击链使攻击推向更高的复杂度，也具备更高的隐蔽水平。目前尚且没有证据表明该攻击链是由特定合作伙伴实施的，后续还将进一步跟踪攻击活动。

## 参考来源

> [PDF](https://assets.sentinelone.com/sentinellabs/SentinelLabs-Zloader)
>
> [Sentinelone](https://www.sentinelone.com/labs/hide-and-seek-new-zloader-> infection-chain-comes-with-improved-stealth-and-evasion-mechanisms/)

