***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 **Trickbot曾经是一个简单的银行木马，已经走过了漫长的道路。随着时间的推移，我们已经看到网络犯罪分子如何继续为此恶意软件添加更多功能。**  

去年三月，Trickbot增加了一个新模块，增加了检测规避和屏幕锁定功能。本月，我们看到Trickbot（被趋势科技检测为
[TSPY_TRICKBOT.THOIBEAI](https://www.trendmicro.com/vinfo/us/threat-encyclopedia/malware/TSPY_TRICKBOT.THOIBEAI)）现在拥有一个密码管理器模块（pwgrab32），可以窃取多个应用程序和浏览器的访问权限，例如Microsoft
Outlook，Filezilla，WinSCP，Google Chrome，Mozilla Firefox， Internet
Explorer和Microsoft Edge。根据我们的遥测技术，我们发现这个Trickbot变种主要影响了美国，加拿大和菲律宾的用户。  

## **分析Trickbot的模块**

恶意软件作者继续使用Trickbot的模块化结构 -它能够通过从C＆C服务器下载新模块来不断更新自身，并更改其配置，以便更新成熟的恶意软件。为了更好地了解这种威胁，我们分析了Trickbot的不同模块，从我们本月看到的新的pwgrab32模块开始。

###  _pwgrab32模块_

Trickbot的新模块，名为pwgrab32或PasswordGrabber，窃取来自Filezilla，Microsoft
Outlook和WinSCP等应用程序的凭据。

![Clipboard
Image.png](https://image.3001.net/images/20181102/1541128640_5bdbc1c00b57d.png!small)

图1.受影响系统中Trickbot新模块pwgrab32的屏幕截图

![Clipboard
Image.png](https://image.3001.net/images/20181102/1541128655_5bdbc1cf84fdc.png!small)

图2.从FileZilla窃取FTP密码的新模块代码的截屏

![Clipboard
Image.png](https://image.3001.net/images/20181102/1541128666_5bdbc1da02d73.png!small)

图3.窃取Microsoft Outlook凭据的新模块代码的屏幕截图

![Clipboard
Image.png](https://image.3001.net/images/20181102/1541128676_5bdbc1e44123b.png!small)

图4.从开源FTP WinSCP获取Trickbot密码的屏幕截图

除了从应用程序窃取凭据外，它还从几个流行的Web浏览器窃取以下信息，例如Google Chrome，Mozilla Firefox，Internet
Explorer和Microsoft Edge：

> 用户名和密码
>
> 互联网饼干
>
> 浏览记录
>
> 自动填充
>
> HTTP帖子

![Clipboard
Image.png](https://image.3001.net/images/20181102/1541128689_5bdbc1f1c7262.png!small)

图5. Trickbot代码的屏幕截图，其结构是从流行的Web浏览器窃取密码

应该注意的是，这个Trickbot变种不能从第三方密码管理器应用程序中窃取密码。我们正在进一步研究这个恶意软件，看看它是否能够从具有浏览器插件的密码管理器中窃取密码。

###  _shareDll32模块_

 **** Trickbot使用shareDll32模块帮助在整个网络中传播自己。它连接到C＆C服务器http：// 185.251.9.251 /
radiance.png以下载自身的副本并将其另存为setuplog.tmp。

![Clipboard
Image.png](https://image.3001.net/images/20181102/1541128705_5bdbc20173d4a.png!small)

图6. Trickbot的shareDll32模块允许它连接到C＆C服务器以下载自身的副本

![Clipboard
Image.png](https://image.3001.net/images/20181102/1541128719_5bdbc20f79fb3.png!small)

图7.下载的文件保存为setuplog.tmp

然后，shareDll32模块使用WNetEnumResource和GetComputerNameW枚举和标识在同一域上连接的系统。

![Clipboard
Image.png](https://image.3001.net/images/20181102/1541128731_5bdbc21b20e20.png!small)

图8.使用WNetEnumResourceW和GetComputerNameW枚举和标识已连接系统的代码的屏幕截图

然后将文件setuplog.tmp复制到已发现的计算机或系统的管理共享中。

![Clipboard
Image.png](https://image.3001.net/images/20181102/1541128743_5bdbc227b5c49.png!small)

图9.在管理共享中复制的setuplog.tmp的屏幕截图

为了使恶意软件更具持久性，它具有自动启动服务，允许Trickbot在机器启动时运行。此服务可以具有以下显示名称：

> 服务技术
>
> Service_Techno2
>
> 工艺，服务2
>
> Technoservices
>
> 高级 - 消息技术服务
>
> ServiceTechno5

###  _wormDll模块_

wormDll32模块尝试使用NetServerEnum和LDAP查询识别网络中的服务器和域控制器。2017年，Flashpoint的安全研究人员首次[观察到](https://www.flashpoint-intel.com/blog/new-version-trickbot-adds-worm-propagation-module/)
Trickbot的蠕虫传播能力。

![Clipboard
Image.png](https://image.3001.net/images/20181102/1541128754_5bdbc232dbf7e.png!small)

图10.使用NetServerEnum标识域中工作站和服务器的代码的屏幕截图

![Clipboard
Image.png](https://image.3001.net/images/20181102/1541128764_5bdbc23c637e2.png!small)

图11.使用LDAP查询标识网络中域控制器的代码的屏幕截图

![Clipboard
Image.png](https://image.3001.net/images/20181102/1541128776_5bdbc2482ca6f.png!small)

图12.使用LDAP查询标识网络中不是域控制器的计算机的代码的屏幕截图

我们还发现，有使用“pysmb，”利用NT LM
0.12查询旧版Windows操作系统和IPC股可能SMB协议的实现。应该注意的是，这个功能似乎仍处于开发阶段。

![Clipboard
Image.png](https://image.3001.net/images/20181102/1541128790_5bdbc2567b958.png!small)

图13.显示可能的SMB通信的代码的屏幕截图

###  _networkDll32_

Trickbot使用此加密模块扫描网络并窃取相关网络信息。它执行以下命令以收集有关受感染系统的信息：

![Clipboard
Image.png](https://image.3001.net/images/20181102/1541128836_5bdbc284e7b47.png!small)

图14. networkDll32模块执行的用于收集网络信息的命令的屏幕截图

###  _Wormdll32模块_

Wormdll32是Trickbot用于通过SMB和LDAP查询传播自身的加密模块。它与模块“wormDll”一起用于在网络上传播。

###  _importDll32模块_

该模块负责窃取浏览器数据，例如浏览历史记录，Cookie和插件等。

###  _systeminfo32模块_

 **** 一旦成功安装在系统中，Trickbot将收集系统信息，如操作系统，CPU和内存信息，用户帐户，已安装程序和服务的列表。

###  _mailsearcher32模块_

此模块搜索受感染系统的文件以收集电子邮件地址以进行信息窃取。

收集垃圾邮件活动相关需求的电子邮件地址通常是恶意软件行为，但是，Kryptos Research最近报告说，Emotet银行木马不只是窃取电子邮件地址;
它还可以收集受Emotet感染的设备上通过Microsoft Outlook发送和接收的电子邮件。根据Brad
Duncan[之前的研究](https://isc.sans.edu/diary/One+Emotet+infection+leads+to+three+follow-up+malware+infections/24140)，Emotet
还负责向用户提供这款吸引密码的Trickbot变体以及[Azorult](https://www.trendmicro.com/vinfo/us/threat-encyclopedia/spam/3661/spam-campaign-leads-to-azorult-trojan-spyware)。

###  _injectDll32模块_

此加密模块监视银行应用程序可能使用的网站。它还用于使用[反射DLL注入](https://github.com/stephenfewer/ReflectiveDLLInjection)技术将代码注入其目标进程。

injectDll32监控银行相关网站的两种不同的凭证窃取方法：

首先，当用户登录其名单上的任何受监控银行网站时，如大通银行，花旗银行，美国银行，斯巴达银行，桑坦德银行，汇丰银行，加拿大帝国商业银行（CIBC）和Metrobank，Trickbot将会向C＆C服务器发送POST响应以提取用户的登录凭据。

其次，Trickbot监控用户是否访问其列表中的某些银行相关网站，例如C.
Hoare＆Co银行，圣詹姆斯广场银行和苏格兰皇家银行，并将用户重定向到假冒网络钓鱼网站。

银行URL Trickbot监控包括来自美国，加拿大，英国，德国，澳大利亚，奥地利，爱尔兰，伦敦，瑞士和苏格兰的网站。

##  **Trickbot的其他值得注意的技巧**

Trickbot通常通过[恶意垃圾邮件活动](https://blog.trendmicro.com/trendlabs-security-intelligence/look-locky-ransomwares-recent-spam-activities/?_ga=2.67425105.153681460.1540774662-609786015.1505725418)发送。该恶意软件通过执行某些命令和修改注册表项来禁用Microsoft的内置防病毒Windows
Defender。

此外，它还会终止与Windows
Defender相关的进程，如MSASCuil.exe，MSASCui.exe和反间谍软件实用程序Msmpeng.exe。它还有一个自动启动机制（Msntcs），它在系统启动时触发，并在首次执行后每十分钟触发一次。

它禁用以下反恶意软件服务：

> MBamService（Malwarebytes相关流程）
>
> SAVService（Sophos AV相关流程）

它的反分析功能可以检查系统并在找到某些模块时自行终止，例如pstorec.dll，vmcheck.dll，wpespy.dll和dbghelp.dll。

##  **捍卫Trickbot的技巧：趋势科技解决方案**

恶意软件作者继续使用新模块更新Trickbot和Emotet等银行木马，使其更难以检测和打击。用户和企业可以受益于使用多层方法来降低银行特洛伊木马等威胁带来的风险的保护。

趋势科技 _[XGen™安全性](https://www.trendmicro.com/en_us/business/products/all-solutions.html)_
提供跨代混合威胁防御技术，以保护系统免受各种类型的威胁，包括银行木马，勒索软件和加密货币挖掘恶意软件。它在[网关](http://www.trendmicro.com/us/business/complete-user-protection/index.html)和[端点](http://www.trendmicro.com/us/enterprise/product-security/vulnerability-protection/)上具有高保真的[机器学习](https://www.trendmicro.com/vinfo/us/security/definition/machine-learning)功能 ，可以保护物理，虚拟和云工作负载。借助Web /
URL过滤，行为分析和自定义沙盒等功能，XGen安全可以抵御当今绕过传统控制的威胁; 利用已知，未知或未公开的漏洞; 窃取或加密个人身份数据;
或进行恶意加密货币挖掘。智能，优化和连接，XGen安全性为趋势科技的套件提供支持。
[](http://www.trendmicro.com/us/business/complete-user-protection/index.html)
[](http://www.trendmicro.com/us/enterprise/product-security/vulnerability-protection/)

## **妥协的指标**

### ip

103.10.145.197:449

103.110.91.118:449

103.111.53.126:449

107.173.102.231:443

107.175.127.147:443

115.78.3.170:443

116.212.152.12:449

121.58.242.206:449

128.201.92.41:449

167.114.13.91:443

170.81.32.66:449

173.239.128.74:443

178.116.83.49:443

181.113.17.230:449

182.253.20.66:449

182.50.64.148:449

185.66.227.183:443

187.190.249.230:443

190.145.74.84:449

192.252.209.44:443

197.232.50.85:443

198.100.157.163:443

212.23.70.149:443

23.226.138.169:443

23.92.93.229:443

23.94.233.142:443

23.94.41.215:443

42.115.91.177:443

46.149.182.112:449

47.49.168.50:443

62.141.94.107:443

68.109.83.22:443

70.48.101.54:443

71.13.140.89:443

75.103.4.186:443

81.17.86.112:443

82.222.40.119:449

94.181.47.198:449

### SHA256

TSPY_TRICKBOT.THOIBEAI：  
806bc3a91b86dbc5c367ecc259136f77482266d9fedca009e4e78f7465058d16

 ***本文作者：bingbingxiaohu，转载请注明来自FreeBuf.COM**

