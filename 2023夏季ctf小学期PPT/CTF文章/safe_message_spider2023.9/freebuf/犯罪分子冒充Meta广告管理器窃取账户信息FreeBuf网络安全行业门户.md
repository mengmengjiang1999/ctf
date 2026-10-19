与所有的社交媒体一样，Facebook 也需要应对虚假账户、诈骗与恶意软件的威胁。过去的几周，研究人员发现冒充 Meta 与 Facebook的
广告管理器再次浮现。骗子承诺通过优化提供更好的广告推广效果，在使用骗子提供的恶意软件时可以提高性能。Meta 官方跟踪了例如 DuckTail
等多个攻击团伙，这些攻击团伙已经在 Facebook 平台活跃了多年。

研究人员发现了一种新的攻击方式，攻击者利用恶意 Chrome 扩展来窃取 Facebook
账户凭据，攻击者与过去常见的攻击团伙无关。在跟踪分析攻击时，研究人员发现攻击者将其中一个恶意软件文件与窃取的数据打包时存在失误。

## 虚假广告管理器

Ads Manager 是一款帮助用户在 Facebook、Instagram 与 Meta 等平台上投放在线广告的产品。5 月份，TechCrunch
披露了诈骗者如何通过验证后的账户从 Meta 购买广告。他们试图吸引潜在的受害者下载该软件，诱骗受害者可以通过“更专业、更安全的工具”来管理广告。

六月初，研究人员就发现了使用类似诱饵、相同方式的欺诈账户。值得注意的是，这些欺诈账户通常拥有数以万计的关注者，其消息可以迅速传播。

![image.png-745.6kB](https://image.3001.net/images/20230715/1689432020_64b2afd418c5533cf1823.png!small)欺诈账户

诈骗者主要针对在该平台上想要投放广告的人。为了入侵这些账户，攻击者将受害者重定向到外部网站。这些网站使用官方的图标构建，引诱受害者通过链接下载
Facebook 广告管理器。各大云服务提供商都被攻击者用于托管加密压缩包，如 Google、Trello 等。

![image.png-470.4kB](https://image.3001.net/images/20230715/1689432021_64b2afd5b7f41fc6b5202.png!small)钓鱼网站

## 恶意 Chrome 扩展

压缩文件解压后，为一个 MSI 安装程序。该程序会在 C:\Program Files (x86)\Ads Manager\Ads Manager
下安装多个组件，包括批处理脚本与两个文件夹。其中有一个自定义的 Chrome 扩展，而 System 文件夹中包含单独的 WebDriver 文件。

![image.png-493.3kB](https://image.3001.net/images/20230715/1689432022_64b2afd6b1b2c0d00d6fe.png!small)文件组件

批处理脚本在 MSI 安装程序完成后启动，生成一个新的浏览器窗口。浏览器加载自定义扩展，将受害者引导至 Facebook 登录页面。

    
    
    taskkill /F /IM chrome.exetaskkill /F /IM chromedriver.exetimeout /t 1 >nulstart chrome.exe --load-extension="%~dp0/nmmhkkegccagdldgiimedpiccmgmiedagg4" "https://www.facebook.com/business/tools/ads-manager"

![image.png-169.8kB](https://image.3001.net/images/20230715/1689432024_64b2afd84e54716cf864c.png!small)虚假登录页面

自定义扩展程序伪装成 Google Translate，但根据源码查看其进行了十六进制混淆，试图隐藏真实意图。

![image.png-1642.7kB](https://image.3001.net/images/20230715/1689432025_64b2afd90369fe3d83e9d.png!small)恶意扩展

对扩展程序进行逆向分析后，可以知道其与谷歌翻译无关，旨在获取 Facebook 的账户凭据与 Cookie。攻击者除了使用 cookies.getAll
外，还使用 Google Analytics 窃取数据。

![image.png-446.8kB](https://image.3001.net/images/20230715/1689432026_64b2afdabbd8056199763.png!small)数据泄露

## 意外泄露

研究人员总共发现了二十余个不同的恶意 Facebook 广告管理器的安装包，尽管使用的样本存在差异，但主要还是为了窃取 Facebook 账户凭据。

![image.png-404.7kB](https://image.3001.net/images/20230715/1689432028_64b2afdc89d0e67583f06.png!small)各种安装包

在分析各种钓鱼网站时，研究人员发现了一个与其他完全不同的压缩文件。讽刺的是，攻击者没有将恶意软件放入其中，而是把窃取的数据上传上来。

![image.png-1233.5kB](https://image.3001.net/images/20230715/1689432030_64b2afde7d887478dd091.png!small)错误文件

压缩文件中包含几个最后修改时间为 6 月 15 日的几个文件文件：

![image.png-253.5kB](https://image.3001.net/images/20230715/1689432031_64b2afdff21cda848b732.png!small)泄露的文件

看文件名就知道内容，文件中包含有关身份验证的各种信息（Cookie、Token 等）。

![image.png-143.4kB](https://image.3001.net/images/20230715/1689432033_64b2afe1eaec6b9fca7b9.png!small)文件详细信息

名为 List_ADS_Tach.txt 的文件的第一行包含一些越南语的列名称，攻击者可能是越南籍。数据总共 828 行，也就是被泄露的 Facebook
账户的数量。

![image.png-523.1kB](https://image.3001.net/images/20230715/1689432034_64b2afe2f40f7a23146f5.png!small)窃取账户的信息

攻击者对受害者的广告账户特别感兴趣，获取了与其广告预算有关的各项数据。

![image.png-804.1kB](https://image.3001.net/images/20230715/1689432036_64b2afe4c34386e850876.png!small)广告信息

广告账户里有大量余额的都会被攻击者盯上，来获取经济利益。

![image.png-140kB](https://image.3001.net/images/20230715/1689432038_64b2afe65322f04811550.png!small)账户余额

将这些数据在地图上进行标记，可以发现受害者遍布世界各地。

![image.png-282.6kB](https://image.3001.net/images/20230715/1689432039_64b2afe71ec18c6a67ac2.png!small)受害者分布

几天后，攻击者发现了这个错误，从 Google Drive 中删除了文件。也更新了钓鱼网站对应的链接，使用 MediaFire 托管了新文件。

![image.png-701.1kB](https://image.3001.net/images/20230715/1689432043_64b2afeb4da9ce2f51635.png!small)更新钓鱼网站

## 低成本的威胁

企业可能会想要下载那些声称可以增加收入的程序来优化 Facebook
上的广告活动。但请记住，天下没有灵丹妙药，任何听起来好的令人难以置信的事情通常都是骗局。

欺诈者花费了大量时间，研究与了解如何滥用社交媒体。社交媒体平台上，需要持续与欺诈者进行对抗。

## IOC

> fd637520a9ca34f7b4b21164581a4ec498bf106ba168b5cb9fcd54b5c2caafd0  
> e73f53ea5dca6d45362fef233c65b99e5b394e97f4f2fe39b374e49c6a273e60  
> 2082e4a8cd0495aabb0f72a41224f134214d0959e208facbfe960c8c74166cda  
> 3638702c83364fc625c0f91388e9b06d94c3486ac0357038f66667d05f9c52e6  
> 547955e97c945ad7283e1637ec0f5e2dbf13c7fb4885a854fb0744542579c6ff  
> 587698e967d05a649428d3a4e45fd64fcea18affd5b021f15d01b8a39a244f8a  
> 6719e6ba89b0a59d325f4531432195afe65154c1d63b9c3bab8ad8925f2f911d  
> 72ba4254e94b7308de92652d1aaf29084fae55d01e0643df1050a638a3bd9dc8  
> 76731d0ed28a552c6f673b6c3e1b08c0499d4b44050df6838439055e01990406  
> 81d9bc3eabe578d606787ab191dd0ff7e8f58a06e35813591e17855daef8505b  
> 8564962190135783b2f21c64cc05fdb226a89a7cbd309ca353fcc31a2a669f0e  
> 8a6a2d439e537b5985b7492f0dded6ae3e1e80133c073d09849712c08927ca55  
> 99057370f8c0312bb5b4a7ed0bd3753b60488e71576af210edd7f813514acb55  
> a29131934b589eb325a76c7d638ac3a0a55c5f185189c71cdf79d8d662129fb7  
> b146d19f7ea988f36449463931758935a54b58e1052dd3a5d20060b2e991b1da  
> c3704b2250e0e8663c86ad5a63e1051004d6967827ef90aab553ddfce682ca5a  
> c9f0da6aa38d4c3d38dc734d7937cdac47c272cca3e2df030242854a9661d314  
> d43d288368bad68e600dae08db5e4846adcaeb4a7d1902ab76417fca3f4c0cf7  
> e94b66b1a3f27dc282a451d3820b3d3d8380be9b9ebab04eedcf4bb0020908e8  
> f128cbfddf3d5c2f5742d3d5d5dae1a041023eba543ee2ddf4d8afdbd42f29b3  
> f1b14728d9f42def90e6eec8c32b2ef5eef43e73383eefa70bf70d8be953c3e5  
> f9ccac29307547adbf779338d6f22bde128feea847012f6392d7ef69cab30878  
> fbadmanage.info

## 参考来源

> [Malwarebytes](https://www.malwarebytes.com/blog/threat-> intelligence/2023/07/criminals-target-businesses-with-malicious-extension-> for-metas-ads-manager-and-accidentally-leak-stolen-accounts)

