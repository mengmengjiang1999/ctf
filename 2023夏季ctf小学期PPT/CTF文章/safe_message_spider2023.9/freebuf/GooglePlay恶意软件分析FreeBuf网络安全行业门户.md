**最近在Google Play上发现了多个恶意应用程序（由Trend
Micro检测为AndroidOS_BadBooster.HRX），它们能够访问远程恶意广告配置服务器、进行广告欺诈并下载多达3000多个恶意软件变体或恶意负载。这些恶意应用程序通过清理、组织和删除文件来提高设备性能，已被下载超过47万次。该攻击活动自2017年以来一直很活跃，Google
Play已经从商店中删除了恶意应用程序。**

根据分析，3000个恶意软件变体或恶意有效负载会下载到设备上，伪装成设备启动程序或程序列表上不显示图标的系统程序。攻击者可以使用受影响的设备发表有利于恶意应用的虚假评论，并通过点击弹出的广告来进行广告欺诈。  

![1.PNG](https://image.3001.net/images/20200209/1581259416_5e401a98ba569.png!small)![1.PNG](https://image.3001.net/images/20200209/1581259450_5e401abad6347.png!small)

## 技术分析

攻击活动中名为Speed Clean的程序具有提升移动设备性能的功能。使用时应用程序会弹出广告，看上去对于移动应用程序是无害的行为。  

![2.PNG](https://image.3001.net/images/20200209/1581259703_5e401bb726510.png!small)Speed
Clean还能够启动透明的活动背景来隐藏恶意内容。  

![1.PNG](https://image.3001.net/images/20200209/1581259801_5e401c1983484.png!small)

这之后，Java包“com.adsmoving”下名为“com.adsmoving.MainService”的恶意服务将建立与远程广告配置服务器的连接，注册新的恶意安装用户。注册完成后Speed
Clean将开始向用户推送恶意广告，恶意广告内容和木马程序将显示在应用程序的“推荐页面”下。

![1.PNG](https://image.3001.net/images/20200209/1581260047_5e401d0f3c26d.png!small)![2.PNG](https://image.3001.net/images/20200209/1581260105_5e401d49608bd.png!small)![1.PNG](https://image.3001.net/images/20200209/1581260125_5e401d5d58f59.png!small)图6为恶意软件流量。

在安装了“alps-14065.apk”之后，启动程序或设备的程序列表上也不会显示任何应用程序图标。它会添加了一个名为“com.phone.sharedstorage”的应用程序，可以在“下载的应用程序”找到。  

![1.PNG](https://image.3001.net/images/20200209/1581260245_5e401dd58f445.png!small)

与2017年检测到的安卓恶意软件家族之一ANDROIDS TOASTAMIGO相同，Speed
Clean应用程序可以下载恶意软件变体或有效载荷，从而执行不同的广告欺诈。本次攻击活动中使用的一些典型恶意广告欺诈行为如下：

1、模拟用户点击广告。恶意应用集成在合法的移动广告平台中，如谷歌AdMob和Facebook等。  
![1.PNG](https://image.3001.net/images/20200210/1581312496_5e40e9f0b3245.png!small)2、将来自移动广告平台的应用程序安装到虚拟环境中，以防止被用户发现。

![1.PNG](https://image.3001.net/images/20200210/1581312617_5e40ea695ca59.png!small)3、诱使用户启用访问权限，停用Google
Play Protect的安全保护功能。确保恶意负载可以下载并安装更多的恶意应用程序，不会被用户发现。

![1.PNG](https://image.3001.net/images/20200210/1581312724_5e40ead48a932.png!small)4、使用受影响设备发布虚假评论。

![1.PNG](https://image.3001.net/images/20200210/1581312796_5e40eb1cf4155.png!small)5、使用accessibility功能利用Google和Facebook帐户登陆恶意软件。

![1.PNG](https://image.3001.net/images/20200210/1581312980_5e40ebd41c974.png!small)从恶意软件变体以及与此攻击活动相关的恶意有效载荷中获取信息如下：  

![1.PNG](https://image.3001.net/images/20200210/1581313131_5e40ec6bc7fbe.png!small)还注意到受感染最严重的国家或地区是日本、台湾、美国、印度和泰国。  

![1.PNG](https://image.3001.net/images/20200210/1581313207_5e40ecb7801c8.png!small)可以将国家/地区代码的地理参数值修改为任何国家/地区代码，甚至是随机的不存在的国家/地区代码，远程广告配置服务器始终返回恶意内容，但是该活动排除了中国用户。  

![1.PNG](https://image.3001.net/images/20200210/1581313544_5e40ee086dddb.png!small)

## 总结

攻击者试图通过更为真实的恶意应用来欺骗用户，因此用户应在下载任何应用之前应进行仔细的辨别。可以通过在商店用户评论来验证应用的合法性。但是，恶意应用程序能够下载有效载荷并发布虚假评论。尽管有很多正面评价，但会出现许多不同的用户留下了内容相同正面评价。

 ***参考来源：[trendmicro](https://blog.trendmicro.com/trendlabs-security-intelligence/malicious-apps-on-google-play-communicate-with-trojans-install-malware-perform-mobile-ad-fraud/https://blog.trendmicro.com/trendlabs-security-intelligence/malicious-apps-on-google-play-communicate-with-trojans-install-malware-perform-mobile-ad-fraud/)，由Kriston编译，转载请注明来自FreeBuf.COM**  

