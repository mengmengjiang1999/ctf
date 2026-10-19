社会工程学策略始终都是攻击者青睐的手段，趋势科技的研究人员最新发现了两类新兴恶意软件，都在一定程度上使用了社会工程学策略来引诱受害者。Redline
Stealer 利用近期大火的生成式人工智能投放恶意广告进行传播，而 CopperStealth 和 CopperPhish
则是通过软件下载站与钓鱼网页进行传播。

## 以生成式 AI 为诱饵广告

攻击者在 Google 等搜索引擎中投放了恶意广告，例如在搜索 midjourney 时：

![image.png-299.1kB](https://image.3001.net/images/20230518/1684386701_6465b38d09171c9b89461.png!small)恶意广告

### 技术分析

用户点击这些广告时，用户的 IP 地址会发送到后端服务器并且提供恶意网页：

![image.png-415.4kB](https://image.3001.net/images/20230518/1684386702_6465b38e2a6f5ddb4d020.png!small)跳转恶意网站

部分恶意广告还能过滤机器人的访问，最大限度避免暴露。当发现是机器人或者手动输入 URL 访问的情况，服务器将返回一个非恶意的版本。

![image.png-245.7kB](https://image.3001.net/images/20230518/1684386703_6465b38fb7066bd3d5bb4.png!small)非恶意网站

通过 Telegram 与 C&C 服务器进行通信，以避免网络检测。

![image.png-243.1kB](https://image.3001.net/images/20230518/1684386704_6465b3907d4e573609287.png!small)C&C
通信

执行安装程序（Midjourney-x64.msix）后，将显示一个虚假的安装窗口，后台执行恶意 PowerShell 代码。

![image.png-89.8kB](https://image.3001.net/images/20230518/1684386705_6465b391f220dc63aba5f.png!small)虚假窗口

最终会给失陷主机安装 Redline 窃密软件，MSIX 文件会执行名为 frank_obfus.ps1 的混淆 PowerShell 脚本。该脚本会从
openaijobs[.]ru 下载并执行 Redline 窃密软件。

![image.png-326.6kB](https://image.3001.net/images/20230518/1684386706_6465b392bab603b04acbb.png!small)去混淆代码

Redline 将会窃取敏感信息，例如浏览器 Cookie、密码、加密货币钱包与文件信息等。

![image.png-1511.2kB](https://image.3001.net/images/20230518/1684386708_6465b394151b12a35ccec.png!small)敏感信息窃取

![image.png-220kB](https://image.3001.net/images/20230518/1684386708_6465b394f3ac180d7aeaa.png!small)恶意广告

![image.png-180.8kB](https://image.3001.net/images/20230518/1684386710_6465b396179f30db6a104.png!small)恶意广告

## Water Orthrus 使用新攻击武器

自从 2021 年开始，趋势科技的研究人员一直在跟踪 Water Orthrus 的攻击行动，该攻击者总是通过 PPI（按安装付费）网络来分发
CopperStealer 窃密木马。研究人员认为，Water Orthrus 与 2019 年被披露的 Scranos 有关。

![image.png-116.5kB](https://image.3001.net/images/20230518/1684386710_6465b396ec06a25a96776.png!small)CopperStealth
感染链

2023 年 3 月，研究人员发现两个传播新型恶意软件（CopperStealth 和 CopperPhish）的攻击行动。这两个恶意软件都与
CopperStealer 高度相似，很可能是由同一开发者开发的，研究人员认为这些攻击都是 Water Orthrus 的攻击行动。

![image.png-89.9kB](https://image.3001.net/images/20230518/1684386711_6465b3978c1ec148df6dc.png!small)CopperPhish
感染链

### CopperStealth

最早在 2023 年 3 月 8 日就发现 CopperStealth
通过中国常见的软件共享网站进行传播，恶意软件伪装成免费软件针对中国用户进行攻击。CopperStealth 执行后还会释放并加载
Rootkit，Rootkit 会阻止列入黑名单的注册表项，阻止某些可执行文件和驱动程序的执行。

恶意软件通过流行的中文软件下载网站分发，此前有研究称其提供恶意安装程序感染恶意软件。安装程序中包含多个编码的 URL，程序运行后解码 URL
并下载执行，其中就包括 CopperStealth。

![image.png-97kB](https://image.3001.net/images/20230518/1684386712_6465b3982a1046bf6a507.png!small)选择驱动代码

CopperStealth 包含一个名为 HelloWorld 的导出函数，该函数在早期版本的 CopperStealer 中就已经存在。Dropper
检查系统架构是 32 位或者 64 位，并对应从资源中读取相应的驱动程序。

![image.png-24kB](https://image.3001.net/images/20230518/1684386712_6465b398e1cdf275df718.png!small)资源中的两个驱动程序

创建并启动一个新的驱动程序服务，该服务在系统启动时启动：

![image.png-64.6kB](https://image.3001.net/images/20230518/1684386713_6465b39956eaeef7aefd0.png!small)创建新驱动服务

Rootkit 被注册为文件系统过滤驱动程序。在 DriverEntry 函数中，驱动程序具有 IRP_MJ_CREATE、IRP_MJ_READ 与
IRP_MJ_SHUTDOWN 的特定处理程序。Rootkit 会更改 HKLM\SYSTEM\CurrentControlSet\Services
注册表中的驱动程序名称并在 HKLM\SYSTEM\CurrentControlSet\Control\SessionManager 中插入
PendingFileRenameOperations 注册表值以在重新启动时自动移动文件。

IRP_MJ_READ 会监控文件系统上任何读取文件的尝试，如果检测到列入黑名单的进程（\360saf\、\kingsoft
antivirus\、\360SD\、\Windows Defender\）试图读取 \windows\temp 文件夹中的 Rootkit
文件，驱动程序会产生 STATUS_ACCESS_DENIED 消息来阻止访问文件。然后，Rookit
会注册一个注册表回调程序，每次线程在注册表中执行操作时都会调用该程序。程序监控访问
HKLM\SYSTEM\CurrentControlSet\Services\ 中 Rootkit 注册表路径的尝试，同样会阻止对文件的访问。

列入黑名单的进程（360safe.exe、360sd.exe、QQPCTray.exe 与 kxetray.exe）查询注册表，也会产生
STATUS_ACCESS_DENIED 消息。

![image.png-91.6kB](https://image.3001.net/images/20230518/1684386713_6465b399cec946d40075f.png!small)阻止注册表访问代码

Rootkit 还设置了镜像加载通知程序，每当新镜像加载到内存中时就会调用该程序。如果镜像名称与硬编码文件名相对应，就会映射一个 DLL
文件并在新创建的进程中运行。64 位版本的 Rootkit 中包含 32 位与 64 位版本的 DLL 文件。

![image.png-80.1kB](https://image.3001.net/images/20230518/1684386714_6465b39a6a0914796b71e.png!small)通过注入的
DLL 文件终止进程

注入的 DLL 文件在附加到新创建的进程后，就会调用 ExitProcess 来终止该进程。

![image.png-57kB](https://image.3001.net/images/20230518/1684386715_6465b39b18ddf70f54db5.png!small)DLL
终止进程

如果新加载的进程是驱动程序，Rootkit 会检索黑名单中的字节序列。如果找到，驱动程序的入口点将被篡改以返回 STATUS_ACCESS_DENIED
消息。驱动程序黑名单针对火绒、金山、360 等安全软件。

![image.png-50.2kB](https://image.3001.net/images/20230518/1684386715_6465b39b9b86b73ae2c27.png!small)Rootkit
篡改驱动程序入口点

最后，Rootkit 会将 Payload 注入其他线程。线程枚举所有正在运行的进程并查找 explorer.exe
与另一个具有分配令牌权限、增加配额权限的西城进程。此外还会增加 HKLM\SOFTWARE\Microsoft\recount
注册表值，其中包含自失陷后机器重启的次数。如果重启次数大于三，Rookit 解密并解压 DLL 模块中的统计信息。在二进制文件中修复统计信息 URL
地址（以 cnzz_url 为占位符），最后将模块注入 explorer.exe。

![image.png-86.8kB](https://image.3001.net/images/20230518/1684386716_6465b39c1e5cfba09e6d1.png!small)统计模块的占位符

成功注入 explorer.exe 后，就会请求任务。一旦驱动程序获取了任务，就会将响应（以 searching_magic_url
为占位符）插入任务模块中。与统计模块类似，任务模块也嵌入在 Rootkit 中。

![image.png-269.7kB](https://image.3001.net/images/20230518/1684386716_6465b39c994b2042a0030.png!small)任务模块的占位符

样本通过访问 hxxp://www.msftconnecttest.com/connecttest.txt 测试网络连接，成功连接后将失陷主机的机器 ID
回传 hxxp://cnzz_url&m=。解密后的任务为 JSON 格式，如下所示：

  * name：TEMP 目录中创建的文件名
  * onlyone：只运行一次
  * exclude360：排除运行 360 的机器
  * reboot_count：在第 N 次重启时启动
  * url：下载并执行的 URL

### CopperPhish

2023 年 4 月，研究人员发现了另一个传播 CopperPhish 的攻击活动。该攻击并没有地理围栏，而是通过免费匿名文件共享网站背后的 PPI
网络进行传播。受害者在点击伪装成下载链接的广告后，就会被重定向到 PPI 网络下载页面。下载的文件是
PrivateLoader，后续会下载许多不同的恶意软件。

![image.png-172.6kB](https://image.3001.net/images/20230518/1684386717_6465b39dca2a89601562b.png!small)重定向的下载页面

CopperPhish 也使用与 CopperStealer 相同的加密方式进行混淆，随后将一些文件（图标 PNG 文件、二维码 PNG 文件与钓鱼
HTML 文件）放入 %APPDATA%\Roaming\Microsoft 文件夹下。

![image.png-21.8kB](https://image.3001.net/images/20230518/1684386718_6465b39e84b59f7e2e4f7.png!small)释放的文件

这些文件存储在文件的资源中，HTML 页面已经翻译成了五十种语言。每种语言都有对应的 HTML 文件，但 PNG 图片是共用的。

![image.png-78.1kB](https://image.3001.net/images/20230518/1684386718_6465b39ee08d0e696835e.png!small)钓鱼页面

恶意软件启动两个线程，一个线程启动 rundll32 进程并注入带有浏览器窗口的程序。

![image.png-69.7kB](https://image.3001.net/images/20230518/1684386719_6465b39f710a3a993215d.png!small)启动进程的线程

另一个线程连接到命名管道并等待接收消息。如果收到消息，则主程序会自行卸载并退出。这表明受害者输入的确认码是正确的，钓鱼成功即可自行卸载。

![image.png-50.9kB](https://image.3001.net/images/20230518/1684386719_6465b39fe3d5026e0ec59.png!small)打开管道等待消息

![image.png-35.7kB](https://image.3001.net/images/20230518/1684386720_6465b3a0668fb561da6fc.png!small)卸载代码

通过 Web 浏览器控件类（SHDocVwCtl）来控制 Web 浏览器对象的行为，读取受害者在 checkcode 字段输入的值。

![image.png-20kB](https://image.3001.net/images/20230518/1684386720_6465b3a0cce9c76b10044.png!small)通过管道发送消息

窗口不提供最小化或者关闭的按钮，受害者如果通过任务管理器关闭，另一个线程也会再将其拉起来。受害者也只能继续，在确认代码后才能消除窗口。

![image.png-218.1kB](https://image.3001.net/images/20230518/1684386721_6465b3a13c7a932e6cd6c.png!small)钓鱼网页

扫描并打开钓鱼 URL 后，受害者可以看到一个要求确认身份的网页：

![image.png-57.4kB](https://image.3001.net/images/20230518/1684386722_6465b3a22bd406fe97c23.png!small)钓鱼网页

后续的页面要求受害者提供各种敏感信息，例如信用卡号等：

![image.png-127.3kB](https://image.3001.net/images/20230518/1684386722_6465b3a2a4806a9e6b6ea.png!small)其他敏感信息

输入敏感信息并通过检查后，钓鱼工具包关闭浏览器并且自动卸载钓鱼工具包。

![image.png-65.9kB](https://image.3001.net/images/20230518/1684386723_6465b3a38659b5251ca52.png!small)成功后页面

![image.png-99.4kB](https://image.3001.net/images/20230518/1684386724_6465b3a424727a32eeecb.png!small)校验代码

### 归因

这两个攻击活动都与之前提到的攻击活动有关，具体来说：

  * Dropper 使用相同的加密方式
  * DES 加密的密钥与初始化向量相同
  * DLL 文件的导出函数相同
  * 互斥量命名相似

## 参考来源

> [TrendMicro1](https://www.trendmicro.com/en_us/research/23/e/malicious-ai-> tool-ads-used-to-deliver-redline-stealer.html)  
> [TrendMicro2](https://www.trendmicro.com/en_us/research/23/e/water-orthrus-> new-campaigns-deliver-rootkit-and-phishing-modules.html)

