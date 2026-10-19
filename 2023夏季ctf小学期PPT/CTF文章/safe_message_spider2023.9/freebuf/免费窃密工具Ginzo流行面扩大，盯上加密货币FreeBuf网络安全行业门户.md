2022 年 3 月 24 日，研究人员发现了新出现的免费窃密工具 Ginzo Stealer。3 月 4 日，攻击者在 Youtube 上上传了演示视频。

视频下方的描述中指出，窃密工具是免费提供的，这可能是吸引网络犯罪者的营销技巧。

![image.png-64.6kB](https://image.3001.net/images/20220427/1651049671_626904c72ccbcf00f23dc.png!small)视频描述

根据统计跟踪，在 3 月 20 日到 30 日期间，就在 VirusTotal 上发现了 400 多个 Ginzo 样本文件。

![image.png-132kB](https://image.3001.net/images/20220427/1651049671_626904c7957c592f071ad.png!small)出售广告

根据 Ginzo 的 Telegram 频道最新消息，该窃密工具现在正在对外出售。

## 混淆

Ginzo Stealer 使用 ConfuserEx 进行混淆，这会导致在反编译代码时遇到错误。因为类型初始化时
`.cctor`会动态解密代码，还会初始化字符串解密所需的数据。

使用 `de4dot`这样的自动反混淆工具已经不够用了，研究人员需要进行调试、静态分析和手动去混淆。

![image.png-853.7kB](https://image.3001.net/images/20220427/1651049672_626904c833f8bf1b3d91d.png!small)解密代码

## 典型行为

Ginzo Stealer 首先从 C&C 服务器下载以下附加模块：

> Newtonsoft.Json.dll
>
> BouncyCastle.Crypto.dll
>
> SQLite.Interop.dll
>
> System.Data.SQLite.dll
>
> DotNetZip.dll

由于异常处理不当，如果无法下载这些模块，窃取样本会在一段时间后崩溃。

Ginzo Stealer 从 C&C 服务器请求 `ginzolist.txt`。此文本文件中包含可执行文件的其他下载地址。在测试时，该文件包含两个下载
`antiwm.exe`和 `generation.exe`的地址。文件 `antivm.exe`是一个挖矿程序，`generation.exe`是一个基于
.NET 的窃密程序，专门用于 Discord Token。另外，这两个文件都是加壳的。

Ginzo Stealer 在 `%LOCALAPPDATA%`中创建一个名为
`GinzoFolder`的文件夹。它将所有提取的系统信息都存储在该处，例如屏幕截图、个人凭据、Cookie、Telegram 数据和加密货币钱包信息。

![image.png-100.6kB](https://image.3001.net/images/20220427/1651049675_626904cb2c717eea07b65.png!small)文件夹内容

Ginzo Stealer 创建一个名为 `System.txt`的文件来存储通用系统信息，其中包括 IP
地址、操作系统、用户名、计算机名称、屏幕分辨率、显卡型号、处理器型号、内存信息、启动时间和 Ginzo Stealer 的 Telegram
频道信息。Ginzo Stealer 还会在 `ChromeUploadTime.txt`中存储一个日期时间，以确保被窃取的数据不会过于频繁地发送给攻击者。

![image.png-66.8kB](https://image.3001.net/images/20220427/1651049675_626904cb891b060d82aea.png!small)文件内容

Ginzo Stealer 会从系统中获取以下数据：

> Telegram 信息
>
> Opera、Chrome、Opera GX、Firefox 的 Cookie 和密码
>
> 所有桌面文件
>
> Discord 的 Token
>
> 加密货币钱包
>
> 系统信息

然后向 C&C 服务器上报窃取的数据，URL 为
`hxxps://nominally.ru/g1nzo.php?data=1148674342&countc=<cookie_count>&countp=<password_count>&country=<country>&ip=<ip_address>&countw=<cryptowallet_count>`。

![image.png-241.7kB](https://image.3001.net/images/20220427/1651049676_626904cc083a7f1772786.png!small)部分代码

`data`参数为 Ginzo Stealer 硬编码的 ID，Ginzo 会将 GinzoFolder 中的文件压缩到
`ginzoarchive.zip`中发送到 C&C 服务器。

![image.png-221.4kB](https://image.3001.net/images/20220427/1651049676_626904cca5e19005cd670.png!small)部分代码

## 结论

Ginzo Stealer 已经是一个成熟的窃密工具了，在很短的时间内被广泛利用，值得对其加以关注。

犯罪分子不会做慈善，免费提供工具往往是吸引未来的买家群体。并且，由于所有窃密数据都会回传到运营商的手中，这是一件稳赚不赔的买卖。

## IOC

> 3fd0837381babda7ef617b810457f0db32bd7c1f7e345480e6c525050ca818fa  
> ee1524e4980cac431ae0f92888ee0cc8a1fa9e7981df0be6abd7efa98adf9a45  
> a9a42ca72be1083b57ee9542925cda5211606b5d07b7b0be21516762e1680124  
> hxxps://nominally.ru/cis.txt  
> hxxps://nominally.ru/ginzolist.txt  
> hxxps://nominally.ru/library/System.Data.SQLite.dll  
> hxxps://nominally.ru/library/Newtonsoft.Json.dll  
> hxxps://nominally.ru/library/BouncyCastle.Crypto.dll  
> hxxps://nominally.ru/library/x86/SQLite.Interop.dll  
> hxxps://nominally.ru/library/x64/SQLite.Interop.dll  
> hxxps://nominally.ru/library/antiwm.exe  
> hxxps://nominally.ru/library/generation.exe

## 参考来源

> [GData](https://www.gdatasoftware.com/blog/2022/03/ginzo-free-malware)

