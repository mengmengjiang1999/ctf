RedLine 是一种窃密恶意软件，以恶意软件即服务（MaaS）的商业模式获利。RedLine 主要针对 Windows 用户发起攻击，收集 Web
浏览器和 FTP 应用程序的登陆凭据、加密钱包信息、信用卡信息、Discord 等即时通讯服务的登录信息等。

2020 年年初，RedLine 在各种犯罪论坛中频繁出现。订阅制每个月需要 150 美元，终身买断制需要 800 美元。RedLine 的
Telegram 频道也可以购买比特币支付购买费用，还会赠送给付费用户一个免费的加壳程序，用户可以自行加壳对抗检测。

![image.png-230kB](https://image.3001.net/images/20211210/1639122827_61b3078b0331c19f49c0a.png!small)

兜售广告

在 RedLine 的 Telegram 频道中，可以看到版本更新通知。例如攻击者在 2021 年 11 月的第一周发布了版本号为 22.3
的新版本，这也说明 RedLine 的开发者致力于不断改进功能保持活跃。

![image.png-129.6kB](https://image.3001.net/images/20211210/1639122848_61b307a054b8673bd9044.png!small)

版本更新信息

近期，RedLine 的破解版在几个犯罪论坛上被披露。我们可以从一个攻击者的角度来查看 RedLine 的功能和易用性，攻击者还附带了安装说明的文档。

![image.png-189.4kB](https://image.3001.net/images/20211210/1639122863_61b307af68ad7f8d7d56b.png!small)

泄露信息

RedLine 的 C&C 面板如下所示，登录的用户名和密码在订阅时一起发送给用户，RedLine 的 C&C 面板不是传统上的 Web 面板。

![image.png-49.3kB](https://image.3001.net/images/20211210/1639122883_61b307c385acd67d7b01c.png!small)

C&C 面板

登录可以在界面上看见以下功能：

> 失陷主机的日志
>
> 排序和搜索日志
>
> 将特定国家/地区/IP 列入黑名单
>
> 在失陷主机上加载任务
>
> 选择要窃取的数据

![image.png-63.8kB](https://image.3001.net/images/20211210/1639122902_61b307d67497edaf19115.png!small)

RedLine 控制界面

如下所示，凭据校验是通过 SOAP over HTTP POST
请求确认的。请求中包含编码后的登录信息和订阅信息，由恶意软件开发者的身份验证服务器进行确认。

![image.png-937.4kB](https://image.3001.net/images/20211210/1639122918_61b307e64e937d618f7d2.png!small)

登录请求

C&C 面板读取某些文本文件作为配置文件，并将其转发到 RedLine 的客户端。`chromeBrowsers.txt`和
`geckoBrowsers.txt`中包含目标浏览器列表。

![image.png-654.6kB](https://image.3001.net/images/20211210/1639122937_61b307f9c02abfe6b465d.png!small)

配置文件

`Panel.exe.config`中包含配置信息，如会话劫持的目标域名、目标文件路径的正则表达式。

![image.png-165.7kB](https://image.3001.net/images/20211210/1639122957_61b3080d8c05c9ddea6c5.png!small)

配置文件

使用 `serviceSettings.json`来存储用于 C&C
通信的端口号，`telegramChatsSettings.json`存储有关发送新失陷主机详细信息的 Telegram 机器人。

RedLine 带有硬编码的 C&C 服务器 IP 地址和端口，以及唯一的 BuildID。

![image.png-83.6kB](https://image.3001.net/images/20211210/1639122975_61b3081f0fa43eb1becc4.png!small)

硬编码 C&C 地址

名为 `IRemoteEndpoint`的接口负责维护 RedLine 的 C&C 通信。

![image.png-356.8kB](https://image.3001.net/images/20211210/1639122991_61b3082f2ecdb94c393d3.png!small)

接口代码

RedLine 在执行后会立刻使用 `RequestConnection()`和 `TryGetConnection()`连接 C&C 服务器，前者会建立与
C&C 服务器的信道，后者会通过 HTTP POST 发送一个 SOAP 请求。

![image.png-356.8kB](https://image.3001.net/images/20211210/1639123009_61b30841182cfb7780a50.png!small)

请求代码

![image.png-331.4kB](https://image.3001.net/images/20211210/1639123025_61b3085145c0616eeb60b.png!small)

请求信息

RedLine 从 C&C 服务器获取指令时，会调用 `TryGetArgs()`通过 HTTP POST 向服务器发送 SOAP 请求。

![image.png-131.4kB](https://image.3001.net/images/20211210/1639123043_61b30863d861c53a7b891.png!small)

部分代码

C&C 服务器使用 `chromeBrowser.txt`、`geckBrowser.txt`等文件的内容作为响应返回。

![image.png-462.1kB](https://image.3001.net/images/20211210/1639123061_61b3087502bc36b49fc20.png!small)

响应信息

RedLine 再通过另一个 HTTP POST 请求回传从失陷主机收集的数据。

![image.png-1095.1kB](https://image.3001.net/images/20211210/1639123077_61b30885493e0689ad0a6.png!small)

窃取数据的网络流量

进一步，RedLine 也可以再执行 C&C 服务器下发的其他指令。

RedLine 基于正则表达式定制窃密目标。与所有典型的窃密恶意软件一样，它会收集失陷主机的相关信息，如 IP 地址、运行进程、处理器信息等。

`GeoHelper`类通过 `ip-api.com`获取失陷主机 IP 的详细信息。

![image.png-413.6kB](https://image.3001.net/images/20211210/1639123099_61b3089b9d049610f1348.png!small)

网络信息相关代码

相似的，`SystemInfoHelper`类获取失陷主机的详细信息，如处理器类型、显卡类型、防火墙和进程信息。

![image.png-552.6kB](https://image.3001.net/images/20211210/1639123117_61b308ad801434373df0b.png!small)

系统信息相关代码

RedLine 还会检测实现主机上是否存在任何加密货币钱包，在文件系统上检索以 `wallet`为结尾的文件。

![image.png-383.5kB](https://image.3001.net/images/20211210/1639123135_61b308bf0e8a13bb40f24.png!small)

加密货币信息相关代码

针对 Metamask、Armory、Coinomi、Guarda 和 Exodus 的加密货币钱包有一些特殊的操作。

RedLine 还会收集场景 V-P-N 客户端（如 NordV-P-N、OpenV-P-N 和 ProtonV-P-N）的相关信息。

![image.png-583.8kB](https://image.3001.net/images/20211210/1639123154_61b308d2a489180c13439.png!small)

V-P-N 信息相关代码

如前所述，RedLine 还能够提取浏览器的用户名和密码。包括 Cookie、信用卡信息和自动填充数据。相关实现在 `ScannedBrowser`类中：

![image.png-388.2kB](https://image.3001.net/images/20211210/1639123174_61b308e63118c812381b5.png!small)

浏览器信息相关代码

在 `C_h_r_o_m_e`类中，通过 `FileCopier`类中的方法来填充
`ScannedBrowser`类中的数据。`C_h_r_o_m_e`类用于扫描密码并解密 base64 编码的密码。

![image.png-582.2kB](https://image.3001.net/images/20211210/1639123194_61b308fa31144e5686ceb.png!small)

窃取浏览器信息

RedLine 针对 FTP 客户端也要窃密，由 `FileZilla`类实现，该类会扫描 FileZilla 文件夹下的文件，并调用
`ScanCredentials`函数提取登录信息。

![image.png-595.4kB](https://image.3001.net/images/20211210/1639123216_61b30910c6bc8927c6cd3.png!small)

窃取 FTP 信息

RedLine 还会窃取即时通讯服务（如 Discord）和游戏服务（如
Steam）的凭据。`GameLauncherRule`类通过注册表检查失陷主机是否安装了 Steam 再获取包含用户数据的 SSFN 文件。

![image.png-608.6kB](https://image.3001.net/images/20211210/1639123235_61b309231d801dd8b1aea.png!small)

检查环境信息

RedLine 作为恶意软件即服务（MaaS）的提供商，将网络犯罪带给了更多普通水平的攻击者。随着破解版的披露，RedLine 也将会越来越受欢迎。

## IOC

> b160ce13f27f1e016b7bfc7a015f686b  
> a2f6561c95f5fff9775ed41fdb105b03  
> FC39A6ED-50506F88EAF39130CE4DEB7C

## 参考来源

> [K7Computing](https://labs.k7computing.com/index.php/redline-stealer-the-> maas-info-stealer/)

