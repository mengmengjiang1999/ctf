2月25日，ASEC 分析小组发布一篇报告，披露了新型的信息窃取程序 ColdStealer 的细节信息。

## ColdStealer简述

该恶意软件通常会将自己伪装成破解软件，通过一个 dropper
恶意软件进行分发，具体过程如下图所示。![1645772095_62187d3fde970af75dc07.png!small?1645772096599](https://image.3001.net/images/20220225/1645772095_62187d3fde970af75dc07.png!small?1645772096599)

图 1. ColdStealer 的感染过程

ColdStealer 具有多层结构，使用 .NET 混淆打包的方法，旨在收集各种用户信息并将其发送到 C2。它是在 .NET
中配置的，由于功能简单，大小只有 80KB。因其样本的命名空间是“ColdStealer”，便以此得名。

![1645772147_62187d736b8bbb4cf031f.png!small?1645772148018](https://image.3001.net/images/20220225/1645772147_62187d736b8bbb4cf031f.png!small?1645772148018)

图 2. ColdStealer

该恶意软件会将收集到的信息以 ZIP 形式保存，然后将内存流发送到
C2。这样做没有文件和执行的痕迹，以此可以绕过安全检测。![1645772201_62187da9bb04a6cf84613.png!small?1645772202367](https://image.3001.net/images/20220225/1645772201_62187da9bb04a6cf84613.png!small?1645772202367)

图 3. 收集信息时使用 ZIP

## ColdStealer的六大功能

该恶意软件有六个主要功能： **窃取浏览器信息、窃取加密货币钱包信息、窃取文件、窃取FTP服务器信息、窃取系统信息和发送异常（错误）信息。**

###  **窃取浏览器信息**

其目标是多个基于 Chromium 的浏览器、Opera 和 FireFox。其中基于 Chromium 的浏览器包括：

> Battle.net、Chromium、Google Chrome 、Google Chrome (x86),、MapleStudio
> ChromePlus、 Iridium,、7Star,、CentBrowser,、Chedot,、Vivaldi、Kometa,、Elements、
> Epic、uCozMedia Uran、 Sleipnir5、Citrio、Coowon、Liebao、QIP Surf、Orbitum、Comodo
> Dragon、Amigo、Torch、Yandex
> Browser、Comodo、360Browser、Maxthon3、K-Melon、Sputnik、Nichrome、CocCoc、Uran、Chromodo、Atom、BraveSoftware、
> Microsoft Edge、Nvidia、Steam、CryptoTab

![1645772254_62187dde910822c1cd6b0.png!small?1645772255265](https://image.3001.net/images/20220225/1645772254_62187dde910822c1cd6b0.png!small?1645772255265)

图 4. Chromium 浏览器信息收集代码

该代码可支持浏览器的最新版本，收集保存在浏览器中的 ID、密码、cookie 和 Web
数据文件。并且，扩展程序也会被查询，下面列出的程序也是恶意软件的目标，其中包括与加密货币钱包或用户验证相关的程序。

>
> Metamask、YoroiWallet、Tronlink、NiftyWallet、MathWallet、Coinbase、BinanceChain，BraveWallet、GuardaWallet、EqualWallet、JaxxLiberty、BitAppWallet、iWallet、Wombat、AtomicWallet、MewCx、GuildWallet、SaturnWallet、RoninWallet、PhantomWallet、Arweave、Auro、Celo、Clover、Coin98、Crypto.com、Cyano、Cyano
> PRO、Dune、Fractal、Gero、Harmony、Hiro、Iconex、Kardia
> Chain、Keplr、KHC、Lamden、Liquality、Maiar、Mew
> CEX、Mobox、NeoLine、Nami、Oasis、Polymesh、Rabby、Solflare、Sollet、Solong、Temple、Terra
> Station、TezBox、Theta、XDeFi、ZebeDee、Authenticator CC

此外，ColdStealer并不是窃取整个文件，而是在内部解析文件，然后只发送必要的信息。然而，由于它没有考虑Unicode编码，因此在解析以韩语为系统语言的浏览器(SQLite格式)的文件时，会发生错误。

![1645772289_62187e01938c8def8d3a6.png!small?1645772290237](https://image.3001.net/images/20220225/1645772289_62187e01938c8def8d3a6.png!small?1645772290237)

图 5. SQLite 解析错误

解析成功后，浏览器访问记录保存在“Domain.text”中，帐号和密码保存在“Passwords.text”中。

![1645772306_62187e12b9b3d92e81342.png!small?1645772307428](https://image.3001.net/images/20220225/1645772306_62187e12b9b3d92e81342.png!small?1645772307428)

图 6. 收集的浏览器密码

###  **窃取文件**

目标是桌面中的文件和用户帐户的子目录。它会收集所有带有“wallet”字符串或扩展名的.txt 和 .dat文件。

![1645772333_62187e2de0e84064e983a.png!small?1645772334585](https://image.3001.net/images/20220225/1645772333_62187e2de0e84064e983a.png!small?1645772334585)

图 7. 窃取文件的代码

###  **窃取FTP服务器信息**

收集保存在最常见的 FTP 程序 FileZilla 中的服务器列表和密码。

![1645772350_62187e3e0c33159945832.png!small?1645772350930](https://image.3001.net/images/20220225/1645772350_62187e3e0c33159945832.png!small?1645772350930)

图 8. 窃取 FTP 服务器信息的代码

###  **窃取系统信息**

收集各种系统信息，包括 Windows 版本、语言、CPU 类型、剪贴板数据、执行权限等。

![1645772373_62187e559b2b5fa0ce8c4.png!small?1645772374331](https://image.3001.net/images/20220225/1645772373_62187e559b2b5fa0ce8c4.png!small?1645772374331)

图 9. 窃取系统信息的代码

###  **窃取加密货币钱包信息**

收集保存在漫游目录、本地目录、注册表等中的钱包程序信息。

>
> Zcash、Armory、Bytecoin、JaxxClassic、JaxxLiberty、Exodus、Ethereum、Electrum、Electrum-> LTC、Electrum-> BCH、Atomic、Guarda、Wasabi、Daedalus、Coinomi、Litecoin、Dash、Bitcoin、monero-> core、Binance。

###  **收集和发送错误信息**

记录并发送程序运行时发生的每个错误（异常）。

![1645772400_62187e70d722e4dae7c14.png!small?1645772401538](https://image.3001.net/images/20220225/1645772400_62187e70d722e4dae7c14.png!small?1645772401538)

图 10. 收集错误的代码

信息在完成收集后会被发送到C2。该恶意软件使用 HTTP POST 方法，而C2 URL已被硬编码在特定位置。

![1645772411_62187e7b4de0688aeeb17.png!small?1645772411951](https://image.3001.net/images/20220225/1645772411_62187e7b4de0688aeeb17.png!small?1645772411951)

图 11. C2 URL

##  **[IOC Info]**

###  **Downloader**

1578ad8f244ae82c36e3feadeb7d66e3  
8f021266830397dac3e34f1b3bdde60c  
05c97434f3c6970103a3ceda97572481  
529951790a4a6da8743af98a24c4088e  
a141acc27f79584575a7d2af634be917  
8550ebb8f4f5b377df3a3492dbc08f63  
511b48b4471e8ab08a4ec6495157f62a  
0b3b4b02ed9d4844ec53a3f2a7064432  
8e0486fb2291090d4411f58aa030dd23  
90f31a31dee14f1efc80e7f121a44763  
e23b0bab2ebcff10bc39f95cb92e6d9f  
28f7a338c703cf695e776108a7dc3f00  
5ccb4a79accca8b6fdc364042705b1a9  
7789b3c473654e3251b102083d49128a  
50920220980a2c188fb88ba770a72ded  
452aeffb5c3c564988b0b7686a1433e9  
2ef96ecfe9a2d05bfc24a936a97e66f1  
fb0dcc61efe76eccef9b7fa20514a1b9  
ac34f72d560a282b919da74e2f5ef8e1  
3144517e723720c79c5f975a629cd2d7  
f1006f3968f9edf76090e34702e647e6  
03c3f6369b934cf86576c394e9172359

###  **ColdStealer**

758f815f3775e1b063eba3ab33479a9f  
0d34d8571c6998796a2edb212a8037f5  
6953629af9858647b65c47ae738334db  
f94e8d62921d078c58860ffc2374a357  
50f2b28aba4d4cb47544bcc98980a63e  
9ec150a4c04da6a1087a3cd36086fde3  
79a9f2ae5af2b370eea6c7fc6681e3ef  
3b94bf347edcc8f137741989de3eb882  
485edc4695212c4e97cf2e841661151c  
a48f8e50e74b3792eeaffc6d25ca0080  
dc2cbd65ca5411b8a9326338c74c7758  
940d63f67b70b37e7ee662b851ae389b  
05748b4e8730bb2a705fe1e2e00c5d77  
8f0f4e736d83e296b55802c2337f341b  
01144efd1dc06a0b9d3ea8a1e632dc26  
cd9ba1e78dab227e2fda2cf952adcab4

###  **C2**

hxxp://jordanserver232[.]com  
hxxp://realacademicmediausa[.]com  
hxxp://topexpertshop[.]com  
hxxp://realmoneycreate[.]xyz  
hxxp://thehomenow[.]xyz  
hxxp://real -enter-solutions[.]xyz  
hxxp://enter-me[.]xyz

## 参考来源：

https://asec.ahnlab.com/en/32090/

