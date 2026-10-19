最近，在地下论坛中出现了许多 macOS 的信息窃密程序，例如 Pureland、MacStealer和Amos Atomic
Stealer。其中，Atomic Stealer 提供了迄今为止最完整的功能，例如窃取账户密码、浏览器数据、会话 Cookie 与加密货币钱包信息。在
Telegram 的宣传中，攻击者可以以每月 1000 美元的价格租用 Web 控制面板来管理攻击活动。

不过攻击者不止步于此，也一直在寻找各种方法通过不同版本的 Atomic Stealer 来攻击 macOS 用户。近日，研究人员就发现了全新的 Atomic
Stealer 变种。

## Atomic Stealer 分发

目前，攻击者通过特定的 Telegram 频道来分发 Amos Atomic MacOS Stealer。4 月 9 日开通的频道中，开发者以每月 1000
美元的价格提供控制面板租用服务，并且提供最新基于磁盘镜像的安装程序。

![image.png-992.5kB](https://image.3001.net/images/20230507/1683389047_64567a7716d8cfa53801c.png!small)通过
Telegram 宣传

Payload 的分配与租用的攻击者有关，因此其实现方式各不相同。目前为止，在野观察到的情况有伪装成 Tor
浏览器等合法应用程序的安装程序，也有伪装成常见软件（Photoshop CC、Notion 、Microsoft Office 等）的破解版本。

![image.png-412.6kB](https://image.3001.net/images/20230507/1683389048_64567a781c25fbee029aa.png!small)伪装成合法应用程序

通过 Google Ads 投放的恶意广告也是分发的途径之一：

![image.png-576kB](https://image.3001.net/images/20230507/1683389048_64567a78bf921236e1349.png!small)部分分发
URL

Atomic Stealer 频道目前拥有超过 300 名订阅者，有部分订阅者表示十分满意该恶意软件。

![image.png-80.9kB](https://image.3001.net/images/20230507/1683389050_64567a7a38027eb48e9d5.png!small)表达支持的消息

## Atomic Stealer 变种 A

虚假应用程序是使用 Appify 的一个分支开发的，该脚本主要用于帮助制作 macOS 应用程序。所有的 Atomic Stealer
目前都包含相同的、Go 开发的可执行文件，大约为 51.5MB。

![image.png-1820.1kB](https://image.3001.net/images/20230507/1683389050_64567a7ac6e13ca54b12d.png!small)二进制文件分析

除了 Appify README 之外，Bundle 仅包含 Go 程序文件、图标文件与 Info.plist。

![image.png-226.7kB](https://image.3001.net/images/20230507/1683389051_64567a7bebb624fd2bfb2.png!small)应用程序结构

当前分发的应用程序包都是使用默认的 Appify 包标识符构建的，这可能是攻击者为了逃避检测故意的。

### 变种 A 的行为

Atomic Stealer 并没有进行持久化，这也是业界的一种趋势。因为从 macOS Ventura
开始，苹果增加了登录项通知，攻击者也开始转向一次性窃密。尽管 Atomic Stealer 通过 AppleScript
欺骗获取用户登录密码的方式十分粗糙，但仍然十分有效。

![image.png-166.5kB](https://image.3001.net/images/20230507/1683389052_64567a7cd1d34d19b5da8.png!small)窃取用户登录密码

攻击者使用 osascript 创建对话框，并将 hidden answer 参数传递给 display dialog
命令。这样将创建一个类似身份验证的对话框，但用户输入的密码明文会被攻击者获取，而且系统日志中也会进行记录。

    
    
    display dialog "MacOS wants to access System PreferencesYou entered invalid password.Please enter your password." with title "System Preferences" with icon file "System:Library:CoreServices:CoreTypes.bundle:Contents:Resources:ToolbarAdvanced.icns" default answer "" giving up after 30 with hidden answer ¬

对话框弹出的消息中包含语法与句法错误，这表明开发者的母语可能不是英语。如果点击取消只会不断循环弹出对话框，点击确定后会通过 /usr/bin/dscl
-authonly 来校验是否输入了有效密码。通过 osascript 反复调用对话框，很容易进行检测。

![image.png-215.5kB](https://image.3001.net/images/20230507/1683389053_64567a7d927a782219a91.png!small)密码校验

窃取完各种用户凭据后，Atomic Stealer 会向用户弹出错误信息。但从单词拼写错误以及错误消息不应该包含取消按钮来看，攻击者对英语与
AppleScript 都并不熟悉。

![image.png-188.4kB](https://image.3001.net/images/20230507/1683389054_64567a7e69397e414d4e7.png!small)成功窃取用户数据后抛出错误信息

攻击者主要是以经济获利为动机而进行的网络犯罪。

![image.png-669kB](https://image.3001.net/images/20230507/1683389055_64567a7f016ad7669b5ac.png!small)信息窃取函数

该恶意软件包含窃取用户钥匙串与加密钱包密钥的功能，例如 Atomic、Binance、Electrum 和 Exodus 等。Atomic Stealer
在内存中生成一个名为 unix1 的进程来获取钥匙串，并且针对 Chrome 和 Firefox 浏览器的扩展进行窃密。

![image.png-496.9kB](https://image.3001.net/images/20230507/1683389055_64567a7fd798b775ce02d.png!small)Atomic
Stealer 执行链

## Atomic Stealer 变种 B

根据某些样本文件发现的 37.220.87.16，可以关联到其他变种。该变种文件在 VirusTotal 上的检出率仍然为零，且伪装成游戏安装程序。

![image.png-274.8kB](https://image.3001.net/images/20230507/1683389056_64567a80adfcf6c2f3104.png!small)新变种

该变种不再依赖应用程序包进行分发，而是通过原始 Go 二进制文件直接进行分发。以 Game Installer 为文件名的文件，在 4 月 13 日被上传到
VirusTotal。DMG 文件的图标中，显示了文本 Start Game。

![image.png-89.8kB](https://image.3001.net/images/20230507/1683389057_64567a81571a23108ee80.png!small)程序图标

由于二进制文件并未携带签名，必须用户介入才能执行。

变种 B 的功能相比变种 A 更多，主要集中在 Firefox 和 Chromium 浏览器上。变种 B 还新增了针对 Coinomi 钱包的窃密。

![image.png-485.1kB](https://image.3001.net/images/20230507/1683389058_64567a821885e51b7e855.png!small)变种
B 的主要函数

变体 A 和 B 都使用 /usr/bin/security 来查找 Chrome 密码。

    
    
    security 2>&1 > /dev/null find-generic-password -ga 'Chrome' | awk '{print $2}

![image.png-813.9kB](https://image.3001.net/images/20230507/1683389059_64567a833c158bb8860e1.png!small)查找
Chrome 密码

根据变种 B 来看，开发机的用户名为 administrator。这与变种 A 不同，变种 A 开发机的用户名为 iluhaboltov。变种 B
中，还发现了字符串 ATOMIC STEALER COOCKIE。

![image.png-497.8kB](https://image.3001.net/images/20230507/1683389060_64567a84063fb86d43906.png!small)硬编码字符串

与 Telegram 频道中提供的软件包不同，此版本的 Atomic Stealer 在窃取信息方面更具选择性，似乎专门针对游戏与加密货币用户。

用户 @Crypto-ALMV 于 4 月 29 日创建了一个相关的 Youtube
频道，来宣传针对加密货币钱包的产品功能。但频道、用户与视频都处于早期阶段，可能尚未正式启用。

![image.png-340.5kB](https://image.3001.net/images/20230507/1683389060_64567a84cbfe2ac547918.png!small)Youtube
频道信息

## 结论

随着普及度越来越高，针对 macOS 用户的攻击越来越多。很多 macOS 的设备都缺乏良好的保护，犯罪分子有很多机会可以进行攻击。而且 Atomic
Stealer 售卖犯罪工具也是很赚钱的，许多犯罪分子都急于窃取用户数据。

## IOC

> amos-malware[.]ru/sendlogillegal  
> 37[.]220.87[.]16:5000/sendlog  
> 0a87b12b2d12526c8ba287f0fb0b2f7b7e23ab4a  
> 24c9f5c90ad325dae02aa52e2b1bac2857ae2faf  
> 36997111b5e7aa81b430a72df9f54bac2a9695ba  
> 7534b4ef7727d14b4fdd32d18651d32572c7747b  
> 0db22608be1172844c0ebf08d573ea4e7ef37308  
> 2681a24f0ec0b1c153cc12d5d861c0c19c8383ea  
> 385b9cc7d3147f049e7b42e97f242c5060fc9e97  
> 46426409b9e65043b15ce2fcddd61213ff4e5156  
> 48a0a7d4f0ae4b79b4f762857af3bbb02e8ab584  
> 4f25d1a1aa18c8d85d555cd7a8f1cf2cf202af8c  
> 58a3bddbc7c45193ecbefa22ad0496b60a29dff2  
> 5d2e995fa5dce271ac5e364d7198842391402728  
> 79007aabf9970e0aff7df52fd1c658b69f950c6f  
> 793195d48cce96bb9b4fc1ee5bac03b371db75f7  
> 82f4647e6783b012fc9a1f86108c644fcf491cf6  
> 849cde22d1d188cc290bb527bbd7252ad07099af  
> 9058ab6e05cb1f9ce77e4f8c18324a6827fb270d  
> 97b19a82a32890d5ddaecac5a294cc3384309ea9  
> 98f98a737a26c9dd1b27c474715976356ea4e18b  
> aab3a2897950e85a2b957f77d2f100e61e29061c  
> b42243d72765f142953bb26794b148858bff10a8  
> ca05f80fe44174d1089077f4b2303c436653226f  
> d5db5a11b9605d54cf66a153b0112b91c950d88f  
> d9d46ecfc1100d2b671ad97dc870e879d2634473  
> de465aad6cde9f0ce30fce0157bc18abf5a60d40  
> e114f643805394caece2326fb53e5d3a604a1aa9  
> f28025717f9db8a651f40c8326f477bf9d51a10f  
> 1f29b00c18bc0b7e1dfee5e79f8111da09f8fab8  
> a02730f734032ed0f3b3705926b657aa4b88d720  
> c70fdf4362eb56032793ab08e6aeb892f1bd4a9b  
> e951b889aabca7ee5b0ff9d06a057884ed788b70

## 参考来源

> [SentinelOne](https://www.sentinelone.com/blog/atomic-stealer-threat-actor-> spawns-second-variant-of-macos-malware-sold-on-telegram/)

