研究人员近日发现 IceXLoader 的最新 3.0 版本是使用 Nim 语言开发的，这种语言在过去两年中被攻击者尝试应用在攻击中，最著名的是
TrickBot 开发的 NimzaLoader 恶意软件。

## ICE_X

研究人员发现了一个带有字符串 `ICE_X`和 `v3.0`的恶意软件，并且由 Nim
语言开发。发现的样本并未完全实现所有功能，例如互斥锁目前只有虚拟代码，可能是正在开发的新版本。

研究人员在地下论坛进行了深入分析，发现该恶意软件在论坛中以 `ICE X`的名义进行售卖，终身许可 118 美元。

![image.png-482.4kB](https://image.3001.net/images/20220620/1655717479_62b03e6792571d54e6896.png!small)论坛广告

攻击者对外销售多种恶意软件，并且提供各种攻击相关的服务。开发者声称他们的四人团队已经拥有十四年的相关服务经验，稳定客户超过两百个。

![image.png-213.5kB](https://image.3001.net/images/20220620/1655717481_62b03e6954d79c9ff7d0c.png!small)开发网站

研究人员将该恶意软件家族命名为 `IceXLoader`，避免与原有的 IceX 木马产生混淆。

## 新版本

开发者提供了配置恶意软件的演示视频，可以看到经典模型的 C&C URL：`icex/Script.php`。

![image.png-202kB](https://image.3001.net/images/20220620/1655717482_62b03e6a027eee72ecc6e.png!small)配置恶意软件

视频里演示了使用 IceXLoader 的 1.0 版本连接 C&C 服务器：

![image.png-117kB](https://image.3001.net/images/20220620/1655717482_62b03e6a93bcf0cb9d1d2.png!small)C&C
面板

根据 URL 特征，可以找到使用 AutoIT 语言开发的 1.0 版本恶意软件。两个版本的功能几乎相同，3.0 版本的 IceXLoader 主要是
Nim 实现的升级版。

![image.png-400.7kB](https://image.3001.net/images/20220620/1655717483_62b03e6b0cf94e9ddb6fa.png!small)版本比较

开发人员声称其恶意软件为 FUD（完全不能检测），这表明其可以绕过安全检测。开发者还表明，恶意软件也会随着安全产品不断更新对抗检测。

这可能也是攻击者利用 Nim 开发恶意软件的原因，攻击者利用安全产品在这一语言领域尚且没有检测优势。

## 技术细节

### 持久化

IceXLoader 使用可配置的文件名将自身复制到 `%AppData%\Microsoft\Windows\Start
Menu\Programs\Startup\`，以实现重启后的持久化存在。

与此同时，IceXLoader 在
`Software\Microsoft\Windows\CurrentVersion\Run`中添加了一个注册表项，其值为在 %AppData%
中留存的第二个副本。

由于 3.0 版本的恶意软件尚未完整实现互斥锁，Windows 重启启动后会运行多个 IceXLoader 实例。

### 检测逃避

IceXLoader 对 AMSI.DLL 中的 `AmsiScanBuffer`进行内存修补，以此绕过 Windows 反恶意软件扫描接口的检测。

将一些禁用 Windows Defender 实时扫描的 PowerShell 命令写入 %TEMP%\file.bat 并执行，还阻止 Windows
Defender 扫描 IceXLoader 所在的目录。

![image.png-98.5kB](https://image.3001.net/images/20220620/1655717484_62b03e6ca7d5c8047ae73.png!small)检测逃避

### C&C

IceXLoader 通过 HTTP/HTTPS POST 请求与硬编码的 C&C 服务器进行通信。User-Agent 会被配置为失陷主机的
GUID，并且 C&C 通信是明文的，没有经过编码或者加密。

![image.png-70.4kB](https://image.3001.net/images/20220620/1655717485_62b03e6d3758117e438fa.png!small)C&C
通信

IceXLoader 通过发送 `SetOn=On`的初始 POST 请求开始通信，C&C 服务器通常会响应 `info`命令进行登记注册。通过
`Done=info<|>`确认命令后，执行命令。

IceXLoader 会收集以下信息：

> 硬编码昵称，默认为 ICE X
>
> 用户名、机器名称以及是否有管理员权限
>
> Windows 版本
>
> 安装的安全产品
>
> .NET 框架版本
>
> Loader 版本
>
> 内存总量
>
> 处理器名称
>
> 显卡名称

收集的信息如下所示：

![image.png-153.3kB](https://image.3001.net/images/20220620/1655717485_62b03e6d9185da03c2774.png!small)示例请求

## 命令

IceXLoader 支持的命令如下所示：

> close：停止执行
>
> info：收集系统信息并回传
>
> msg：显示指定消息的对话框
>
> restart：重启恶意软件
>
> runFile：下载到本地、下载到内存执行文件
>
> Sleep：设定睡眠间隔时间
>
> Update：更新恶意软件
>
> uninstall：清除恶意软件

## 感染链

IceXLoader 旧版本分发 DcRat，而新版本进行门罗币挖矿。

![image.png-43.2kB](https://image.3001.net/images/20220620/1655717486_62b03e6e0eec160e4b785.png!small)旧感染链

![image.png-40kB](https://image.3001.net/images/20220620/1655717486_62b03e6e56992d798fbe4.png!small)新感染链

## 结论

攻击者正在将代码移植到不常见的语言中，逃避安全产品的检测。随着安全研究的深入，攻击者也在不断进行技术更新。

## IOC

> 6d98c8bdb20a85ef44677f3e7eed32c9fee0c18354e3365c28e11cb6130a8794  
> 4eaed1357af8b4f757c16d90afb339161ac73fa4b8d867a416664b89a1d0a809  
> 3a838c22312f4279f400b7eee63918d9232907a1aa483c824cb8a815150f06e8  
> 4c26dbee513067e6d327e4b336b29992fd5270a0a8ecd1e9571378a3fb0bdc60  
> 4fe56d88c1170a3d0e025b9d8f7939139a7618b3868eb993037c6e3b52d9d501  
> fecfca77593850e4f6deb8090fc35b14366ab27ef0ada833f940b2d4cb381509  
> 619356420efd4dc53704fb5eb5c93f1f5d4a0123ed1fdd5ce276a832381de51d  
> 915f0d1e9bd1b681d9935af168cb9f1823c738b869fb2c3646f81098a0fe5d95  
> hxxp[:]//kulcha.didns.ru:8080/Script.php  
> hxxp[:]//golden-cheats.com/icex/Script.php  
> hxxps[:]//r4yza92.com/Script.php  
> hxxp[:]//62.197.136.240/script.php  
> hxxp[:]//funmustsolutions.site/wp-includes/icex/Script.php  
> hxxps[:]//north.ac/pxnel.php  
> hxxp[:]//hhj.jbk0871.fun/study/Script.php  
> hxxp[:]//funmustsolutions.site/wp-includes/icex/Files/Client.exe  
> hxxp[:]//funmustsolutions.site/wp-includes/icex/Files/Loader.exe  
> hxxp[:]//golden-cheats.com/icex/Files/BadforICE.exeBadforICE.exe  
> hxxp[:]//golden-cheats.com/remote-config.json  
> hxxp[:]//golden-cheats.com/loader/uploads/InstallerLoader_Wjyhorou.bmp

## 参考来源

> [Fortinet](https://www.fortinet.com/blog/threat-research/new-> icexloader-3-0-developers-warm-up-to-nim)

