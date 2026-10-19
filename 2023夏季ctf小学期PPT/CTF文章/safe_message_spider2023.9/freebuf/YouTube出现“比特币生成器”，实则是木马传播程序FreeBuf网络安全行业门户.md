**近日油管上出现大量关于“比特币生成器”的广告宣传视频，号称该工具可为用户免费生成比特币，实际上却是一个散布Qulab信息窃取和剪贴板劫持木马的恶意行为。**

 **![youtube-rectangle_headpic.jpg](https://image.3001.net/images/20190531/15592744313075.jpg!small)**

该活动由安全研究员Frost发现，他表示已对此木马行为追踪了15天左右，每次发现类似视频并上报的时候，YouTube都会很快将视频删除并封禁相应用户，但治标不治本，很快又会有新的账户出现上传类似视频。

![videos.jpg](https://image.3001.net/images/20190531/15592744092841.jpg!small)

视频上传者

视频的内容是介绍一个号称可以免费生成比特币的工具，并附带下载链接，该工具实际上是一个木马程序，以及一个<https://freebitco.in>网站的链接。如图：

![youtube-videos.jpg](https://image.3001.net/images/20190531/15592744571593.jpg!small)木马宣传视频

当用户点击视频中的下载链接时，会跳转到一个Setup.exe文件的下载页面。如果用户下载并运行该文件，则计算机内将会被植入Qulab木马。

![setup-download.jpg](https://image.3001.net/images/20190531/15592744797688.jpg!small)

程序下载页面

## Qulab木马

这个YouTube骗局中推送的恶意程序是Qulab信息窃取和剪贴板劫持木马。程序执行后，木马会将自身复制到%AppData%\amd64_microsoft-windows-netio-infrastructure\msaudite.module.exe这个位置并启动。

根据Fulaik0关于Qulab上的文章可以了解到，Qulab木马会窃取用户浏览器历史记录、保存浏览器凭据、cookie，以及FileZilla、Discord和Steam中保存到凭据。该木马还会从计算机中窃取.txt、.maFile和.wallet文件。

除此之外，QUlab还会成为剪贴板劫持程序或限幅器，也就是说它可以监控Windows剪贴板中出现的数据，并且在检测到数据时，还能将其与攻击者想要的不同数据做出交换。在当前的攻击场景中，Qulab会寻找已经复制到剪贴板中的加密货币地址，并将其交换出来。

由于加密货币的地址是长字符串并且难以口头记忆，所以很多用户都不会发觉他们所记录的地址已经被悄悄的换成了别的内容，攻击者可以通过这种方式大肆窃取加密货币。

Fumik0_的分析表明Qulab支持以下Clipper组件的加密货币地址：

![image.png](https://image.3001.net/images/20190531/15592745176828.png!small)

在编译被盗数据时，木马程序会通过Telegram将其发送给攻击者，如下所示：

![network-traffic-r.jpg](https://image.3001.net/images/20190531/1559274557591.jpg!small)

如果不幸感染了该木马，请立即更改常用账户以及网站的密码。再次建议，请尝试使用密码管理器为每个账户创建唯一且强大的密码。

***参考来源：[bleepingcomputer](https://www.bleepingcomputer.com/news/security/youtube-cryptocurrency-videos-pushing-info-stealing-trojan/)，Karunesh91编译，转载请注明来自FreeBuf.COM**

