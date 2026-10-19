CryptBot 最早在 2019 年被发现，近期再次爆发。最新版本的 CryptBot 已经显著简化，只包含信息窃取的功能，样本大小相比以前小得多。

CryptBot 针对敏感的用户数据，例如浏览器登录信息、加密货币钱包、存储的信用卡信息、密码等信息。收集到的信息会被发送回 C&C
服务器，出售获取经济利益。

## 破解软件网站

CryptBot
最近通过破解软件网站进行分发，这些网站提供的是常见游戏和其他软件的破解版。攻击者通过这种方式捆绑传播恶意软件，让受害者不知不觉中下载并执行恶意样本。

## 技术分析

CryptBot 的攻击链条起始于受害者访问失陷的页面下载 SFX 文件，如伪装成最新版本的 Adobe Photoshop。

![image.png-303.8kB](https://image.3001.net/images/20220315/1647354374_6230a206d7f43752da819.png!small)网页示例

随后，将名为 `7ZSfxMod_x86.exe`的 SFX 文件下载到机器上。

![image.png-185.4kB](https://image.3001.net/images/20220315/1647354376_6230a20830ddfe2e75da9.png!small)恶意文件

解压后，名为 `7ZipSfx.000`的文件夹在 `%Temp%`目录中创建。其中，数字会随着文件数量与解压次数变化。例如，第二次解压将会创建名为
`7ZipSfx.001`的文件夹。

![image.png-149.1kB](https://image.3001.net/images/20220315/1647354376_6230a208dabc7f72dae7c.png!small)文件夹

文件夹中包含四个文件，用于下一阶段的攻击：

> aeFdOLFszTz.dll，ntdll.dll 的副本文件
>
> Avevano.gif，BAT 脚本
>
> Carne.gif，混淆的 AutoIT 脚本
>
> Raccontero.exe，AutoIT v3 可执行解释器

如上所示，两个伪装成 GIF 图片的文件都是恶意脚本。不同版本的 CryptBot 还会使用 .MP3 与 .WMV 作为扩展名。

BAT 恶意脚本如下所示。脚本对安全产品（BullGuardCore 和 Panda Cloud
Antivirus）进行扫描，如果存在将会延迟执行以逃避检测。

![image.png-207.4kB](https://image.3001.net/images/20220315/1647354377_6230a20967259f7fafd26.png!small)恶意脚本

如下所示，BAT 恶意脚本解密高度混淆的 AutoIT 脚本 `Carne.gif`，BAT 还会将 AutoIT 脚本复制到虚拟内存区域运行。

![image.png-432.3kB](https://image.3001.net/images/20220315/1647354377_6230a209f366519d79dca.png!small)混淆脚本

使用 AutoIT 可执行解释器 `Raccontero.exe`运行 `Carne.gif`，脚本的文件名作为参数提供。

![image.png-63.1kB](https://image.3001.net/images/20220315/1647354379_6230a20b556d82bf85714.png!small)进程启动

AutoIT 进程 `Raccontero.exe.pif`会将恶意 CryptBot 加载至内存中。

## 功能

CryptBot 首先在机器中检索用户与系统信息，收集的数据会存储在用户的 `%Temp%`目录下。发送给 C&C 服务器后，该文件即被删除。

检索的数据包括：

> 加密货币钱包
>
> 登录信息
>
> 表单数据
>
> Cookie
>
> 浏览器历史记录
>
> 信用卡信息
>
> 敏感数据文件
>
> 操作系统和硬件信息
>
> 已安装程序列表

![image.png-454.9kB](https://image.3001.net/images/20220315/1647354379_6230a20bd37406ee99a10.png!small)扫描加密货币钱包

受害者的数据存储在压缩的 TXT 文件中，随后会被发送给 `rygvpi61.top/index.php`。

CryptBot 也包含备用的 C&C 服务器，可以下载其他恶意软件。

![image.png-294.7kB](https://image.3001.net/images/20220315/1647354380_6230a20cc4beecbd0ab1b.png!small)恶意样本

## 最新变种

最新版本的 CryptBot 于 2022 年初在野被发现，攻击者只保留了数据泄露相关的核心功能，如反沙盒等功能都删除了。

最新版本的 CryptBot 不会窃取受害者的屏幕截图，也不会自行清除恶意文件。

新版本使用的混淆方法也与 CryptBot 旧版本不同，现在的恶意 BAT 脚本使用了更复杂的混淆来阻止研究人员分析。

新版本也更新了对最新版本 Chrome v96 的窃密，覆盖 Chrome 的全部版本。

## 结论

目前为止，只发现 CryptBot 针对 Windows 设备发起攻击。可能是与投递方式与破解软件有关，这在 MacOS 与 Linux 上并不常见。

攻击者将恶意样本缩小了一半，这样可以简化攻击进行更频繁、更快速的感染。

## Yara

    
    
    import "pe"rule CryptBot {meta:description = "Detects 2022 CryptBot Through Imphash"author = "BlackBerry Threat Research Team"date = "2022-02-26"license = "This Yara rule is provided under the Apache License 2.0 (https://www.apache.org/licenses/LICENSE-2.0) and open to any user or organization, as long as you use it under this license and ensure originator credit in any derivative to The BlackBerry Research & Intelligence Team"strings:$s1 = "7z SFX"condition:(//PE Fileuint16(0) == 0x5a4d and//Imphashpe.imphash() == "e55dbecdaf2c7cc43f3d577e70c6c583" orpe.imphash() == "27fc501de77f5768cac058a2a9512c3a" orpe.imphash() == "fda990324138bdc940f9020ce3e8d5fc" orpe.imphash() == "997edafa1e226ba6317ec804803f9a57" orpe.imphash() == "4b3cfc81e94566bb0e35b6156e51fbd5" and//All Stringsall of ($s*) )}

## IOC

    
    
    53d8d466679a01953aab35947655a8c1a2ff3c19ac188e9f40e3135553cf7556rygvpi61.top/index.phpgewuib08.top/download.php?file=scrods.exe﻿

## 参考来源

> [BlackBerry](https://blogs.blackberry.com/en/2022/03/threat-thursday-> cryptbot-infostealer)

