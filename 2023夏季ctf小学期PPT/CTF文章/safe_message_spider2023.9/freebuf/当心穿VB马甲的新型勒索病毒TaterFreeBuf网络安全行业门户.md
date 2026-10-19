## **一、** **行为概述**  

**近日，深信服安全团队收到客户反馈，其服务器遭到勒索病毒攻击，所有文件数据被加密，加密后缀名为“.tater”。**

**此次攻击的为一种新型的勒索病毒，除了豁免少数几个系统文件夹以外，其会对其他目录的所有后缀的文件进行无差别加密，同时该病毒还加了一层VB程序外壳进行伪装。由于加密算法采用了RSA+AES的方式，暂时无法解密。**

勒索信息：

![01.jpg](https://image.3001.net/images/20190401/1554102707_5ca1b9b36dfec.jpg!small)

加密后文件：

![02.jpg](https://image.3001.net/images/20190401/1554102714_5ca1b9baabbf4.jpg!small)

##  **二、** **入侵分析**

文件加密时间为2019/3/26 6:43左右：

![03.jpg](https://image.3001.net/images/20190401/1554102717_5ca1b9bda9394.jpg!small)

排查日志发现，服务器在2019/3/26 6:39:21被远程登录过，登录IP为一个内网IP地址：

![04.jpg](https://image.3001.net/images/20190401/1554102727_5ca1b9c713a7c.jpg!small)

黑客登陆后放入进程管理工具Process Hacker用来结束系统中的安全软件，然后放入病毒到tater@mail2tor.com文件夹进行勒索：

![05.jpg](https://image.3001.net/images/20190401/1554102730_5ca1b9ca3dab0.jpg!small)

##  **三、** **详细分析**

主程序代码结构，如下所示：

![06.png](https://image.3001.net/images/20190401/1554102733_5ca1b9cd59967.png!small)

查询程序自身资源数据，如下所示：

![07.png](https://image.3001.net/images/20190401/1554102738_5ca1b9d229e20.png!small)

在内存中解密出相应的数据，如下所示：

![08.png](https://image.3001.net/images/20190401/1554102742_5ca1b9d63e448.png!small)

创建子进程，调用程序，如下所示：

![09.png](https://image.3001.net/images/20190401/1554102745_5ca1b9d9167d1.png!small)

创建的子进程，如下图所示：

![10.png](https://image.3001.net/images/20190401/1554102768_5ca1b9f0674c8.png!small)

勒索的核心代码被加载到内存中执行，从内存中DUMP出勒索加密的Payload，如下所示：

![11.png](https://image.3001.net/images/20190401/1554102771_5ca1b9f396551.png!small)

通过判断操作系统语言，对指定区域进行豁免，包括：俄罗斯、哈萨克、白俄罗斯、乌克兰、鞑靼：

![12.jpg](https://image.3001.net/images/20190401/1554102775_5ca1b9f7ab596.jpg!small)

删除磁盘卷影：

![13.jpg](https://image.3001.net/images/20190401/1554102779_5ca1b9fbf2589.jpg!small)

结束指定进程：

![14.jpg](https://image.3001.net/images/20190401/1554102791_5ca1ba0798e4e.jpg!small)

进程列表如下：

    
    
    sqlwriter.exe、sqlbrowser.exe、sqlservr.exe、TNSLSNR.EXE、mysqld.exe、MsDtsSrvr.exe、sqlceip.exe、msmdsrv.exe、mpdwsvc.exe、fdlauncher.exe、Launchpad.exe、chrome.exe、oracle.exe、devenv.exe、PerfWatson2.exe、ServiceHubHost Node x86.exe、Node.exe、Microsoft VisualStudio    Web Host.exe、Lightshot.exe、netbeans64.exe、spnsrvnt.exe、sntlsrtsrvr.exe、w3wp.exe、TeamViewer_Service.exe、TeamViewer.exe、SecomSDK.exe、schedul2.exe\schedhlp.exe、adm_tray.exe、EXCEL.EXE、MSACCESS.EXE、OUTLOOK.EXE、POWERPNT.EXE、AnyDesk.exe、MicrosoftSqlServer IntegrationServices MasterServiceHost.exe、MicrosoftSqlServer IntegrationServices WorkerAgentServiceHost.exe

从程序中解密出RSA公钥1：

![15.png](https://image.3001.net/images/20190401/1554102803_5ca1ba1301cb1.png!small)

生成一对新的RSA公钥2和私钥2：

![16.png](https://image.3001.net/images/20190401/1554102807_5ca1ba17e846b.png!small)

使用公钥1加密私钥2，并base64编码：

![17.png](https://image.3001.net/images/20190401/1554102811_5ca1ba1bd90dc.png!small)

将公钥2与编码后的私钥2写入文件%appdata%\\_uninstalling_.png，如下：

![18.jpg](https://image.3001.net/images/20190401/1554102815_5ca1ba1f3e44a.jpg!small)

加密共享文件：

![19.jpg](https://image.3001.net/images/20190401/1554102818_5ca1ba22e61ac.jpg!small)

加密磁盘文件：

![20.jpg](https://image.3001.net/images/20190401/1554102822_5ca1ba26c675b.jpg!small)

将勒索信息写入文件“#HOW TODECRYPT#.txt”：

![21.jpg](https://image.3001.net/images/20190401/1554102833_5ca1ba3124e79.jpg!small)

豁免以下目录：Windows、$Recycle.bin、SystemVolume Information。

![22.jpg](https://image.3001.net/images/20190401/1554102836_5ca1ba34b370e.jpg!small)

生成AES密钥并用公钥2加密：

![23.jpg](https://image.3001.net/images/20190401/1554102840_5ca1ba387f6e4.jpg!small)

用AES加密文件，然后将加密后的AES密钥写入到加密后的文件中：

![24.jpg](https://image.3001.net/images/20190401/1554102844_5ca1ba3c5f426.jpg!small)

加密后的文件加上后缀“.tater”。

![25.jpg](https://image.3001.net/images/20190401/1554102849_5ca1ba418a6c8.jpg!small)

##  **四、解决方案**

针对已经出现勒索现象的用户，由于暂时没有解密工具，建议尽快对感染主机进行断网隔离。深信服提醒广大用户尽快做好病毒检测与防御措施，防范该病毒家族的勒索攻击。

###  **病毒检测查杀**

1.深信服为广大用户免费提供查杀工具，可下载如下工具，进行检测查杀。

64位系统下载链接：

<http://edr.sangfor.com.cn/tool/SfabAntiBot_X64.7z>

32位系统下载链接：

<http://edr.sangfor.com.cn/tool/SfabAntiBot_X86.7z>

2.深信服EDR产品、下一代防火墙及安全感知平台等安全产品均具备病毒检测能力，部署相关产品用户可进行病毒检测，如图所示：

![26.png](https://image.3001.net/images/20190401/1554102860_5ca1ba4c3b182.png!small)

###  **病毒防御**

深信服安全团队再次提醒广大用户，勒索病毒以防为主，目前大部分勒索病毒加密后的文件都无法解密，注意日常防范措施：

1.及时给电脑打补丁，修复漏洞。

2.对重要的数据文件定期进行非本地备份。

3.不要点击来源不明的邮件附件，不从不明网站下载软件。

4.尽量关闭不必要的文件共享权限。

5.更改账户密码，设置强密码，避免使用统一的密码，因为统一的密码会导致一台被攻破，多台遭殃。

6.如果业务上无需使用RDP的，建议关闭RDP。当出现此类事件时，推荐使用深信服防火墙，或者终端检测响应平台（EDR）的微隔离功能对3389等端口进行封堵，防止扩散！

7.深信服防火墙、终端检测响应平台（EDR）均有防爆破功能，防火墙开启此功能并启用11080051、11080027、11080016规则，EDR开启防爆破功能可进行防御。

8.深信服防火墙客户，建议升级到AF805版本，并开启人工智能引擎Save，以达到最好的防御效果。

9.使用深信服安全产品，接入安全云脑，使用云查服务可以即时检测防御新威胁。

最后，建议企业对全网进行一次安全检查和杀毒扫描，加强防护工作。推荐使用深信服安全感知+防火墙+EDR，对内网进行感知、查杀和防护。

 ***本文作者：深信服千里目安全实验室，转载请注明来自FreeBuf.COM**

