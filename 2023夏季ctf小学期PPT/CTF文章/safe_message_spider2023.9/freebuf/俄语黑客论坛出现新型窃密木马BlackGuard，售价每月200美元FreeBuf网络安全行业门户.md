近年来，恶意软件即服务的出现大幅度降低了犯罪分子发动攻击的技术门槛，极大地促进了勒索软件和网络钓鱼攻击（以及其他类型的攻击）的增长。

最近，研究人员发现了 BlackGuard 在黑客论坛提供恶意软件即服务。其每月售价为 200 美元，终身服务价格为 700 美元。

![image.png-64.9kB](https://image.3001.net/images/20220406/1649225168_624d2dd071630180e5bcf.png!small)宣传页面

BlackGuard 能够窃取与加密钱包、VPN、Messenger、FTP 凭据、浏览器凭据和电子邮件等相关信息。

## 技术分析

BlackGuard 是一个 .NET 开发的窃密木马，攻击者也在积极开发新功能。

### 反检测

BlackGuard 在执行后就会检查并终止杀软与沙盒的相关进程：

![image.png-121.1kB](https://image.3001.net/images/20220406/1649225168_624d2dd0da8830d8f3fca.png!small)反检测

### 混淆

BlackGuard 包含一个硬编码的字节数组，在运行时会被解码为字符串再进行 base64 解码，通过这种方式规避安全检测：

![image.png-148.5kB](https://image.3001.net/images/20220406/1649225169_624d2dd17d587d8b2f7f0.png!small)混淆

### 位置检查

BlackGuard 向 `http://ipwhois.app/xml/`发送请求检查失陷主机所在国家/地区，如果设备位于独联体国家内，就自动退出。

![image.png-89.7kB](https://image.3001.net/images/20220406/1649225170_624d2dd21592c8a857a0f.png!small)位置检查

### 反调试

BlackGuard 使用 `user-32!BlockInput()`拦截鼠标和键盘事件中断调试。

![image.png-45.6kB](https://image.3001.net/images/20220406/1649225170_624d2dd27a3e18ab52c53.png!small)反调试

### 窃密

完成所有检查后，将会进行窃密，从各种浏览器、软件、硬编码目录中收集信息。

![image.png-346.1kB](https://image.3001.net/images/20220406/1649225171_624d2dd327c61133489c1.png!small)窃密代码

![image.png-274.7kB](https://image.3001.net/images/20220406/1649225172_624d2dd4352891fc2756e.png!small)功能介绍

### 浏览器窃密

BlackGuard 通过固定路径从基于 Chrome 和 Gecko 的浏览器中窃取历史记录、密码、自动填充、下载文件等信息。

![image.png-340.6kB](https://image.3001.net/images/20220406/1649225173_624d2dd51ac763ba07149.png!small)浏览器窃密

### 加密货币钱包

BlackGuard 还支持窃取与加密钱包应用程序相关的敏感信息，包括地址、私钥与其他敏感数据（如 `wallet.dat`），检查 AppData
中的默认钱包文件位置并将其复制走。

![image.png-163kB](https://image.3001.net/images/20220406/1649225174_624d2dd6066ce130fe75e.png!small)加密货币钱包窃密

### 加密钱包扩展

针对安装在 Chrome 和 Edge 中的具有硬编码扩展 ID 的加密钱包扩展，BlackGuard 也会进行窃密。

![image.png-273.4kB](https://image.3001.net/images/20220406/1649225174_624d2dd68faead48cb320.png!small)加密钱包扩展

### C&C

BlackGuard 会在收集信息后创建一个包含所有文件的 .zip 文件，并通过 POST 请求将硬件 ID 与其他受害者相关信息一起发送到 C&C
服务器。

![image.png-299.7kB](https://image.3001.net/images/20220406/1649225175_624d2dd7475fcf29eb0f4.png!small)C&C
部分代码

![image.png-126.6kB](https://image.3001.net/images/20220406/1649225176_624d2dd8643cf1717f216.png!small)C&C
流量

![image.png-258.6kB](https://image.3001.net/images/20220406/1649225176_624d2dd8f3720f7f0a117.png!small)控制面板

## 目标应用程序

### 浏览器

Chrome, Opera, Firefox, MapleStudio, Iridium, 7Star, CentBrowser, Chedot,
Vivaldi, Kometa, Elements Browser, Epic Privacy Browser, uCozMedia, Coowon,
liebao, QIP Surf, Orbitum, Comodo, Amigo, Torch, Comodo, 360Browser, Maxthon3,
K-Melon, Sputnik, Nichrome, CocCoc, Uran, Chromodo, Edge, BraveSoftware

### 加密钱包

AtomicWallet, BitcoinCore, DashCore, Electrum, Ethereum, Exodus, LitecoinCore,
Monero, Jaxx, Zcash, Solar, Zap, AtomicDEX, Binance, Frame, TokenPocket,
Wassabi

### 加密钱包扩展

Binance, coin98, Phantom, Mobox, XinPay, Math10, Metamask, BitApp,
Guildwallet, iconx, Sollet, Slope Wallet, Starcoin, Swash, Finnie, KEPLR,
Crocobit, OXYGEN, Nifty, Liquality, Auvitas wallet, Math wallet, MTV wallet,
Rabet wallet, Ronin wallet, Yoroi wallet, ZilPay wallet, Exodus, Terra
Station, Jaxx

### 电子邮件客户端

Outlook

### 其他应用程序

NordVPN, Open-VPN, ProtonVpn, Totalcomander, Filezilla, WinSCP, Steam

### 通讯软件

Telegram, Signal, Tox, Element, Pidgin, Discord

## 结论

尽管 BlackGuard 的应用并不十分广，但是它仍然是快速增长中的威胁。BlackGuard 也在不断进行改进，并且在黑客社区中建立了较为良好的信誉。

## IOC

> 4d66b5a09f4e500e7df0794552829c925a5728ad0acd9e68ec020e138abe80ac  
> c98e24c174130bba4836e08d24170866aa7128d62d3e2b25f3bc8562fdc74a66  
> 7f2542ed2768a8bd5f6054eaf3c5f75cb4f77c0c8e887e58b613cb43d9dd9c13  
> f2d25cb96d3411e4696f8f5401cb8f1af0d83bf3c6b69f511f1a694b1a86b74d  
> bbc8ac47d3051fbab328d4a8a4c1c8819707ac045ab6ac94b1997dac59be2ece  
> f47db48129530cf19f3c42f0c9f38ce1915f403469483661999dc2b19e12650b  
> ead17dee70549740a4e649a647516c140d303f507e0c42ac4b6856e6a4ff9e14  
> 1ee88a8f680ffd175943e465bf85e003e1ae7d90a0b677b785c7be8ded481392  
> 71edf6e4460d3eaf5f385610004cfd68d1a08b753d3991c6a64ca61beb4c673a  
> e08d69b8256bcea27032d1faf574f47d5412b6da6565dbe52c968ccecea1cd5d  
> win.mirtonewbacker.com  
> umpulumpu.ru  
> greenblguard.shop  
> onetwostep.at

## 参考来源

> [Zscaler](https://www.zscaler.com/blogs/security-research/analysis-> blackguard-new-info-stealer-malware-being-sold-russian-hacking)

