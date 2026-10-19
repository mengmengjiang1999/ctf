***严正声明：本文仅限于技术讨论与分享，严禁用于非法途径**

 **Google
play和ios应用商店对试图诱骗用户下载广告或恶意软件的应用有很严密的检测。最近，我们还发现了隐藏在应用商店合法产品中的恶意应用程序。这些应用诱骗不知情的用户下载赌博应用。**

我们在ios应用商店和google
play上发现了数百个虚假应用，它们的描述与其内容不一致。虽然这些应用的描述各不相同，但它们有着相同的行为：会转化为赌博应用，这些应用可能因违反当地政府法规和应用商店政策而被禁止。一些应用程序排名前100被多次下载，有些甚至被评为超过10万次。

![1569741211_5d90599b3d96d.png!small](https://image.3001.net/images/20190929/1569741211_5d90599b3d96d.png!small)

## 应用传播方式

这些应用程序可以通过赌博网站或应用程序商店下载。例如，访问网站时，将显示以下页面。

![1569741541_5d905ae5d8a89.png!small](https://image.3001.net/images/20190929/1569741541_5d905ae5d8a89.png!small)

网站上的下载按钮会将用户重定向到应用商店，说明了这些赌博应用通过了iOS应用商店的审查。一些应用程序会弹出一个网页，诱使用户安装一个不受应用程序商店监管的应用程序。

![1569741951_5d905c7f6dfee.png!small](https://image.3001.net/images/20190929/1569741951_5d905c7f6dfee.png!small)

对于android用户，下载按钮会将他们重定向到一个页面，该页面可下载android应用程序包（apk）文件，这个apk与通过webview加载的赌博应用程序具有相同的用户界面。

![1569742036_5d905cd4e10a6.png!small](https://image.3001.net/images/20190929/1569742036_5d905cd4e10a6.png!small)

![1569742054_5d905ce64ed6b.png!small](https://image.3001.net/images/20190929/1569742054_5d905ce64ed6b.png!small)

如上图所示，app
store上的应用程序描述为葡萄酒。但在打开应用程序时发现了一个不同的内容，与之前提到的网页相似。下载的应用程序与其在应用商店上的描述完全不同。

![1570344240_5d998d300a93e.png!small](https://image.3001.net/images/20191006/1570344822508.png!small)

这些应用程序在google play上的部署方式类似。图6显示了google play列表的屏幕截图，以及用户启动应用程序时的实际界面。

## 如何绕过应用商店的审查

在app store和google play上不禁止赌博或金钱游戏应用程序，但它们受到严格限制。此外，google
play只允许在某些国家使用赌博应用程序，只要这些应用程序满足其要求。

这些虚假应用程序以一个普通的应用程序伪装自己，具有不同的特性和功能（例如，用于天气或娱乐功能），但这些假应用程序可以被控制。面的流程图中描述了整个过程。

![1569743793_5d9063b168d29.png!small](https://image.3001.net/images/20190929/1569743793_5d9063b168d29.png!small)

首先，应用程序有一个“切换”功能，攻击者可以将应用程序设置为显示或隐藏实际的应用程序内容。在这种情况下，api在应用程序的审查过程中被关闭。

![1570344197_5d998d050a4e2.png!small](https://image.3001.net/images/20191006/1570344197_5d998d050a4e2.png!small)

请注意，在下图中，kaiguan这个词在中文中的意思是打开/关闭，而1700对于这些应用程序来说似乎是一个不寻常的数字。

![1570344009_5d998c49499bc.png!small](https://image.3001.net/images/20191006/1570344009_5d998c49499bc.png!small)

应用程序将使用其应用程序ID查询指定的地址。相应的响应将以Base64编码。如果应用程序ID无效，则响应将返回为空。

![1570344054_5d998c767035c.png!small](https://image.3001.net/images/20191006/1570344054_5d998c767035c.png!small)

如果数据不为空并且可以成功解码，则将使用url在webview中加载。

![1570344142_5d998cce48275.png!small](https://image.3001.net/images/20191006/1570344142_5d998cce48275.png!small)

在ios上，如果响应为空，webview将被隐藏，以便“正常”应用程序可以继续。

![1569744319_5d9065bf59a4c.png!small](https://image.3001.net/images/20191006/15703447991114.png!small)

在android系统上，如果为空，它只会跳转到本地，应用程序将继续其“正常”（商店批准）的应用程序功能。

因此，在审查应用程序之前，开发人员只需按下“关闭”开关，就可以启动一个外观正常的应用程序。该应用可能会通过应用商店的审查，因为赌博功能已经被隐藏。应用程序通过审查后，可以从应用程序商店公开下载它们。然后，攻击者将其“打开”以允许查看应用程序的实际内容。

![1569744627_5d9066f3ce558.png!small](https://image.3001.net/images/20190929/1569744627_5d9066f3ce558.png!small)

## 应用排名

在进行研究时，应用程序只使用webview加载赌博网站，而没有在设备上做任何恶意操作。尽管这些应用程序可能是假的，但它们的排名仍然高于它们所模拟的应用程序。

根据google play的数据，应用程序只在2019年8月发布，这也解释了它们的下载量低的原因。iOS应用商店并非如此，在app
store上进行的关键字搜索显示，有两个应用属于相同app，假冒应用程序的排名高于其类似的应用程序。

![1569744766_5d90677e505f7.png!small](https://image.3001.net/images/20190929/1569744766_5d90677e505f7.png!small)

合法的应用程序已经更新了两年，而假冒的应用程序在过去六个月里只有两次小的更新，弹出式webview是在第二次更新中植入的。

在中国的iOS应用商店中，似乎有许多假冒的应用已经出现，并跻身前100名。这些应用程序下载量较高，其中一个甚至获得44万的下载量。

![1569744887_5d9067f760775.png!small](https://image.3001.net/images/20190929/1569744887_5d9067f760775.png!small)

搜索了可能与ios应用程序商店上的应用程序相关的典型关键字，发现了以下匹配结果（在某些区域内受到限制）。

Keyword| CN Market| JP Market| US Market  
---|---|---|---  
重庆时时彩 (Chongqing Lottery Every Hour)| 214| 40| 61  
分分彩 (Lottery Every Minute)| 55| 26| 52  
北京赛车 (Beijing Racing)| 314| 9| 104  
  
  
![fig-16-gambling-apps-japan-google-search.png](https://image.3001.net/images/20191006/15703420902969.png!small)

## 虚假应用程序的命令和控制（C&C）通信

C&C服务器app[.]kaiguan1700[.]com，用于控制上述三个应用程序（需要注意的是，其IP地址仅承载此URL）。在我们尝试访问它之后，服务器已关闭。与此同时，这些应用程序表现得和正常的应用程序相同，因为我们意外地“关闭”了“开关”，这表明这些应用共享同一个C&C服务器。

![1569745143_5d9068f716ba2.jpg!small](https://image.3001.net/images/20190929/1569745143_5d9068f716ba2.jpg!small)

由于成百上千的假应用被上传到应用商店，并且他们使用不同的开发人员帐户，所以他们的类别各不相同。利用C&C服务器聚类是一个很好的区分方法，可将应用程序聚类在一起，防止它们被用户下载。

## IOCs

App Name/Label| Bundle Name| Version  
---|---|---  
グロ一バルホリデ一情報— 28元の登録| com.luther.worldholiday| 1.6  
グロ一バルホリデ一情報— 28元の登録| com.gavinjeremy.publicholidays| 1.1  
微醺| KK.WeiXun| 1.0.1  
semsiye| com.semsiye.semsiye| 1.2  
HappyEnglishTOKorean| com.HappyEnglishTOKorean| 1.2  
No Hit| com.NoHit.cw| 1.0.2  
TeaAssistant| com.wuzhongxin.teaassistant| 1.1  
SkyMadness| sky.madness.com| 1.0.1  
Simon Color Match| com.jda.Color-Match| 1.3  
Classic Poems| com.abcd.Poems| 1.2  
Employee attendance tracker| com.emp.att| 1.1  
Package Name| SHA-256| Version  
---|---|---  
com.hh.ii.d587|
B8409F8D625AACEF0DA1C50075443833781FD935DEF608FE396B11D4EEC619AE| 1.0  
com.hh.ii.p557|
AD791FBAD2C3F06FE7C8CA9820D7D6F62C5C0BAAA835023472ADA1276C80CF7E| 1.0  
com.hh.ii.c603|
4D7F591760EF07A2F240A6EF0AF4F9544437833A83C68B03E8E04F0E662B38F4| 1.0  
com.liuhe.fenxi.ruanjian|
98F4C2CAB302C1B5954D8EC3B0658D83958D522DE6157B14171AAA6BB45F5798| 1.0  
com.jz.shequ.jiaoliu|
8DB2AD04FD93704954CEE498F2431E98CAAD9D1E9BB836DEBD5BBF982A2FD246| 1.0  
com.tain.jing.ssc|
B7DCF23836919E**CF5E71D313E4866CDAD0C8D514BFF0DE8C3147E65D3EEA93| 1.0  
com.jiu.ou.id2957|
6C368EF20A419C3E792435C9DAF3CE9CD239611BDD6D40840CA70E56669B5A24| 1.0  
com.jiu.ou.id2969|
1338C22DE793CF4C6F523A6C1A42C9EEFE5886F3C345ADF2D469C90323CC0691| 1.0  
com.jiu.ou.id2968|
35B16C8A575B586BA10D0CEF9DB0356E7EBEDF93F887F3A5E90BD971557204D2| 1.0  
com.jiu.ou.id3001|
DAF9E73A4B256D15D9A231B12A0DCDBD4BB152F6557BFF76D184A9286A2DB456| 1.0  
com.jiu.ou.id3006|
C8355E6A056884CD781A36302CC8CE66CE1A912100AE37B28DBE44D3FDD2D702| 1.0  
com.jiu.ou.id3007|
375EB929AF991AFA92769DE5D285BC7E4085150BD585335D4BD**60101849970| 1.0  
com.jiu.ou.id3000|
6ADCD1D37D0024EA9E3**43BE029A774D845E2A9EFF48DD43988B05161454077| 1.0  
com.jiu.ou.id3002|
42F90F0B9B635057170933AA8E73E869728B797010C6CA4891FA59E4D63F377C| 1.0  
com.jiu.ou.id3010|
4DD441A5559E9F17B3A275AFDD73E18FEB27BFB37E9F9C027CEE8D62A268E846| 1.0  
  
 ***参考来源：[trendmicro](https://blog.trendmicro.com/trendlabs-security-intelligence/gambling-apps-sneak-top-100-hundreds-fake-apps-spread-app-store-google-play/)，由Kriston编译，转载请注明来自FreeBuf.COM**

