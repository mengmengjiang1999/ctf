2021 年 11 月以来，研究人员发现针对中国澳门豪华酒店（包括 Grand Coloane Resort-澳门鹭环海天度假酒店、Wynn Palace-澳门永利皇宮酒店）的攻击行动。攻击始于一封针对酒店管理人员的鱼叉邮件，攻击目标包括人力资源副总裁、经理助理和前台经理，攻击者想通过这些攻击目标获取酒店的对应权限，例如预定系统。

鱼叉邮件带有恶意 Excel 文档，文档引诱受害者启用宏代码。攻击的基本流程如下所示：

![image.png-40.9kB](https://image.3001.net/images/20220329/1648546980_6242d4a4debb08e6c5a9c.png!small)攻击流程

Zscaler 的研究人员在 2021 年 12 月下旬披露了一个 DarkHotel 的攻击行动。本文分析到的 C&C IP 地址
`23.111.184.119`也与之相关，该 IP 地址被攻击者持续使用。

## DarkHotel

DarkHotel 是一个疑似为韩国背景的 APT
攻击组织，过往针对法律、医药和汽车行业发起攻击。该组织经常通过携带恶意文档的鱼叉邮件攻击酒店与酒店访客，从而在入住豪华酒店的高管处窃取敏感信息。

## 钓鱼邮件

2021 年 12 月 7 日，攻击者以澳门旅游局的名义向澳门 17 家酒店发送了一封电子邮件，邮件携带名为 `信息.xls`的附件。

![image.png-56.7kB](https://image.3001.net/images/20220329/1648546981_6242d4a5464e82b8ce0ed.png!small)邮件元数据

同属于同一攻击行动的另一封电子邮件中，攻击者要求酒店员工填写 Excel 确认是否存在该人员入住酒店：

![image.png-31.4kB](https://image.3001.net/images/20220329/1648546981_6242d4a5a9e2ce37a0a46.png!small)邮件正文

## 技术分析

攻击者通过 Excel 2013 983040 的程序来生成恶意 Excel 文档。

![image.png-49.8kB](https://image.3001.net/images/20220329/1648546982_6242d4a6249550c8348ac.png!small)恶意文档元数据

在 `DocumentSummaryInformation`或 `Summaryinformation`流中查找四字节的属性
`PropertySetSystemIdentifier`可以确定创建 Excel 的操作系统：

![image.png-89.3kB](https://image.3001.net/images/20220329/1648546982_6242d4a678ea27a74524f.png!small)十六进制数据

由此可知，攻击者通过 Windows 8 操作系统来创建该文件。

Excel 通过默认密码 `VelvetSweatshop`进行加密，打开后会显示诱饵信息引诱受害者。

![image.png-124.8kB](https://image.3001.net/images/20220329/1648546982_6242d4a6db5e3e7a1a12a.png!small)Excel
文件

打开文件时会触发嵌入的宏代码：

![image.png-206.1kB](https://image.3001.net/images/20220329/1648546983_6242d4a75cae3478eaac6.png!small)文件解析

恶意宏代码被存储在 `Module1.bas`中：

![image.png-167.2kB](https://image.3001.net/images/20220329/1648546983_6242d4a7d7425be5e1563.png!small)宏代码

宏代码经过高度混淆，创建了大量的循环来解码字符串与命令。

![image.png-252.4kB](https://image.3001.net/images/20220329/1648546984_6242d4a88311a0f324940.png!small)混淆代码

以其中一个为例，函数中创建 COM 对象并通过 `Schedule.Service`对任务进行调度。

![image.png-158.4kB](https://image.3001.net/images/20220329/1648546985_6242d4a97b8b350d104ec.png!small)对象创建

这样，攻击者就不必使用 `schtasks.exe`来设置定时任务。

不同的计划任务设置如下所示：

> Connect
>
> GetFolder
>
> NewTask
>
> Settings
>
> StartWhenAvailable
>
> RunOnlyIfNetworkAvailable
>
> StopIfGoingOnBatteries
>
> DisallowStartIfOnBatteries

首先在 `C:\\Users\USER\AppData\\Roaming\\Microsoft\\Windows\\`中释放名为
`prcjobs.vbs`的脚本，接着使用 `wscript.exe`执行 `wscript.exe /b /nologo
"C:\Users\USER\AppData\Roaming\Microsoft\Windows\prcjobs.vbs" "powershell -c`。

![image.png-137.1kB](https://image.3001.net/images/20220329/1648546986_6242d4aa42c32791f4abd.png!small)PowerShell
脚本

该组织使用的另一个 Excel 样本文件中包含更多的 PowerShell 代码，攻击者也在不断改进攻击。

这个新文件会在 `\System32`下寻找 `SyncappvpublishingServer.vbs`，由于执行的是微软签名的 wscript.exe
是会被信任执行的。

![image.png-149.4kB](https://image.3001.net/images/20220329/1648546986_6242d4aac7eb123d99d2e.png!small)检索文件

执行过程和代码与之前的样本是非常相似的：

![image.png-156.6kB](https://image.3001.net/images/20220329/1648546987_6242d4ab708fc8914c763.png!small)部分代码

硬编码的 C&C 服务器 `https://fsm-gov.com`冒充密克罗尼西亚联邦的政府网站，真正的网站域名为 `fsmgov.org`。

![image.png-183.4kB](https://image.3001.net/images/20220329/1648546988_6242d4ac11f2454c2113e.png!small)真正网站

![image.png-15.9kB](https://image.3001.net/images/20220329/1648546988_6242d4acac32b47803ee7.png!small)假冒网站

服务器提供商为 Hivelocity，但该厂商并不愿意与研究人员合作。

攻击者通过 `Mailman`来发送电子邮件：

![image.png-47.4kB](https://image.3001.net/images/20220329/1648546989_6242d4ad0b17e228ae37b.png!small)网页信息

## 攻击目标

DarkHotel
攻击的其中一家酒店正要举办国际环境论坛和国际贸易与投资博览会，这都是攻击者非常感兴趣的。但不巧的是，澳门的疫情形势变得严峻后这些活动基本都被推迟或者取消。所以，攻击者在
1 月 18 日之后也停止了攻击。

## 通报

澳门保安局在 2021 年 12 月披露了该攻击行动：

![image.png-128.3kB](https://image.3001.net/images/20220329/1648546989_6242d4ad661b1ce0f507f.png!small)政府公告

## 其他攻击行动

该 IP 地址也参与了其他攻击行动，其中一个是针对 MetaMask 用户的 Collab.Land 钓鱼页面。

![image.png-42.9kB](https://image.3001.net/images/20220329/1648546989_6242d4adc746928f719b4.png!small)钓鱼页面

MetaMask 用户被提示输入凭据，回传到 Discord 服务器收集信息。

![image.png-101.8kB](https://image.3001.net/images/20220329/1648546990_6242d4ae343283e9751de.png!small)网页源码

攻击的 TTP 存在较大差异，可以认为该攻击与 DarkHotel 无关。而且这种无关的攻击会增大该 IP 地址暴露的机会，限制感染目标的能力。

## 结论

不论是不是 DarkHotel，针对酒店行业的攻击也持续都存在。入住豪华酒店的高管应该提高警惕，使用酒店提供的 WiFi 时更要谨慎。

## IOC

> fsm-gov.com  
> 163c386598e1826b0d81a93d2ca0dc615265473b66d4521c359991828b725c14  
> a251ac8cec78ac4f39fc5536996bed66c3436f8c16d377922187ea61722c71f8

## 参考来源

> [Trellix](https://www.trellix.com/en-us/about/newsroom/stories/threat-> labs/suspected-darkhotel-apt-activity-update.html)

