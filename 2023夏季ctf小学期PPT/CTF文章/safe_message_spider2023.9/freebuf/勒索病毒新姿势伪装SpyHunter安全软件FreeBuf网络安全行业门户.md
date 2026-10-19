**近日，国外安全研究人员曝光了一款伪装成安全软件SpyHunter的勒索病毒，其开发人员使用了SpyHunter的标识作为勒索软件的图标，同时将文件命名为“SpyHunters.exe”，通过钓鱼邮件附件进行传播，并在勒索文本中写道“Our
company SpyHunter is guaranteed to decrypt your files.Creating and removing
viruses is our vocation”。（我们公司 Spy Hunter 保证解密您的文件，创建和删除病毒是我们的职业）**  

事实上，该勒索病毒是GarrantyDecrypt家族的一个新变种。GarrantyDecrypt于2018年10月首次在Twiter被提出，每隔几个月便发布一次新版本。在该家族的其中一个变种中，攻击者还假装是Proton的安全团队，要求受害者支付780美元的Proton服务费用。在本次发现的变种中，攻击者故技重施，伪装成SpyHunter
来诋毁EnigmaSoft。

## 勒索特征

![](https://image.3001.net/images/20190803/1564795472_5d44e2509008e.png!small)

1.勒索信息：

![](https://image.3001.net/images/20190803/1564799927_5d44f3b7713f5.png!small)

2.加密后文件后缀为：

![](https://image.3001.net/images/20190803/1564799936_5d44f3c06de2c.png!small)

## 详细分析

1.程序由VB语言做了一层封装，首先查找自身资源”MERIDINAN”：

![](https://image.3001.net/images/20190803/1564799950_5d44f3ced69b1.png!small)

2.解密payload，图中是解密前后的数据对比（左为加密前，右为加密后）：

![](https://image.3001.net/images/20190803/1564799957_5d44f3d5b0556.png!small)

3.创建同名进程挂起，写入释放在内存中的PE文件，并修改进程context后运行：

![](https://image.3001.net/images/20190803/1564799968_5d44f3e0f2f54.png!small)

修改后的context如下图所示：

![](https://image.3001.net/images/20190803/1564799981_5d44f3ed1d79e.png!small)

4.解密出RSA公钥：

![](https://image.3001.net/images/20190803/1564800426_5d44f5aae5daa.png!small)

5.判断操作系统语言，排除地区的主机：

![](https://image.3001.net/images/20190803/1564799999_5d44f3ff1b856.png!small)

6.解密出删除磁盘卷影的命令并通过vssadmin.exe：、

![](https://image.3001.net/images/20190803/1564800012_5d44f40cd686b.png!small)

7.解密出进程列表，查找并终止列表中的进程：

![](https://image.3001.net/images/20190803/1564800019_5d44f41350279.png!small)

相关进程列表如下：

sqlwriter.exe、sqlbrowser.exe、sqlservr.exe、TNSLSNR.EXE、mysqld.exe、MsDtsSrvr.exe、sqlceip.exe、msmdsrv.exe、mpdwsvc.exe、fdlauncher.exe、Launchpad.exe、chrome.exe、oracle.exe、devenv.exe、PerfWatson2.exe、ServiceHub.Host.Node.x86.exe、Node.exe、Microsoft.VisualStudio.Web.Host.exe、Lightshot.exe、netbeans64.exe、spnsrvnt.exe、sntlsrtsrvr.exe、w3wp.exe、TeamViewer_Service.exe、TeamViewer.exe、SecomSDK.exe、schedul2.exe、schedhlp.exe、adm_tray.exe、EXCEL.EXE、MSACCESS.EXE、OUTLOOK.EXE、POWERPNT.EXE、AnyDesk.exe、Microsoft.SqlServer.IntegrationServices.MasterServiceHost.exe、Microsoft.SqlServer.IntegrationServices.WorkerAgentServiceHost.exe

8.生成AES密钥，并使用RSA算法加密后存放在”C:\Documents and Settings\Administrator\Application
Data\\_uninstalling_.png”目录下：

![](https://image.3001.net/images/20190803/1564800067_5d44f443c5676.png!small)

9.遍历共享目录进行加密：

![](https://image.3001.net/images/20190803/1564800048_5d44f430774b2.png!small)

10.遍历逻辑驱动，并在每一个根目录释放勒索信息TXT文件” $HOWDECRYPT$.txt”：

![](https://image.3001.net/images/20190803/1564800078_5d44f44e7cb2b.png!small)

11.使用AES算法对文件进行加密：

![](https://image.3001.net/images/20190803/1564800084_5d44f454a36a7.png!small)

## 解决方案

针对已经出现勒索现象的用户，由于暂时没有解密工具，建议尽快对感染主机进行断网隔离。深信服提醒广大用户尽快做好病毒检测与防御措施，防范该病毒家族的勒索攻击。

## 病毒检测查杀

1、深信服EDR产品、下一代防火墙及安全感知平台等安全产品均具备病毒检测能力，部署相关产品用户可进行病毒检测，如图所示：

![](https://image.3001.net/images/20190803/1564800093_5d44f45d768a3.png!small)

2、深信服为广大用户免费提供查杀工具，可下载如下工具，进行检测查杀。

64位系统下载链接：

<http://edr.sangfor.com.cn/tool/SfabAntiBot_X64.7z>

32位系统下载链接：

<http://edr.sangfor.com.cn/tool/SfabAntiBot_X86.7z>

3、深信服EDR官网提供勒索病毒搜索功能，支持勒索病毒家族名或加密后缀查询，快速找到相关信息。

搜索链接：[https://edr.sangfor.com.cn](https://edr.sangfor.com.cn/)

## 病毒防御

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

 ***本文作者：深信服千里目安全实验室，转载请注明来自FreeBuf.COM**

