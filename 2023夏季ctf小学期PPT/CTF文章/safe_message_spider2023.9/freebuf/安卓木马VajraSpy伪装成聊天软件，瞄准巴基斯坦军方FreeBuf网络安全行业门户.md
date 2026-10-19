VajraSpy 是一个安卓远控木马，使用指定的谷歌云存储服务来存储窃取的数据。研究人员发现，APT-Q-43 组织使用 VajraSpy 木马伪装成名为
`Crazy Talk`的聊天应用程序，攻击巴基斯坦军方人员。

解压缩 `CrazyTalk.apk`样本可以发现多个 `classes.dex`，多个 `classes.dex`文件使用 Multidex 进行加载。

![image.png-61.3kB](https://image.3001.net/images/20220427/1651049398_626903b6d86e288816796.png!small)文件内容

该木马使用 Firebase 云存储服务来存储从失陷设备上收集的数据。

应用的入口点为 classes2.dex 的 MainActivity，其中的 `onCreate()`函数确认应用程序拥有“Notification
Access”和“Accessibility Service”的权限，并收集 Firebase Cloud Messaging（FCM）的 Token。

![image.png-201.2kB](https://image.3001.net/images/20220427/1651049399_626903b7728d4735cfec2.png!small)部分代码

恶意软件模拟一个聊天应用程序要请求的权限：

![image.png-214.4kB](https://image.3001.net/images/20220427/1651049400_626903b81c62bc12d1924.png!small)权限列表

恶意软件初始化 Firebase 存储服务：

![image.png-53.1kB](https://image.3001.net/images/20220427/1651049400_626903b8acb9edd195244.png!small)部分代码

在 FirebaseStorage 初始化后，应用程序通过启动 StorageReference 来收集受害者的个人信息：

![image.png-153.2kB](https://image.3001.net/images/20220427/1651049401_626903b957833b2c6d087.png!small)部分代码

如上所示，`putBytes()`函数通过 `StorageReference`对象将数据上传到 Firebase 存储服务。

除了上传的 contacts.json 文件，恶意软件还会收集其他用户数据，如短信、通话记录、WhatsApp（包括企业帐户）消息、 Signal
应用程序消息、设备详细信息、受害者设备的应用程序列表等。

![image.png-220.6kB](https://image.3001.net/images/20220427/1651049402_626903ba14109c578cc6c.png!small)部分代码

WhatsApp、WhatsAppBusiness 或 Signal 的消息会暂时存储在 SQLite DB 的指定数据表中，然后将其上传到指定的
Firebase 云存储服务。

![image.png-265.8kB](https://image.3001.net/images/20220427/1651049402_626903bad96b37ae52b6a.png!small)WhatsApp
数据收集

![image.png-144.1kB](https://image.3001.net/images/20220427/1651049403_626903bbafa9bd3a381f9.png!small)写入数据表

![image.png-280.1kB](https://image.3001.net/images/20220427/1651049404_626903bc5f717d77178b5.png!small)通过表中数据创建数组

## 总结

最近，安卓恶意软件势头正盛，各种不同的恶意软件都在快速攀升。攻击者也在积极利用各种能够利用的手段（如云存储服务等），将攻击过程隐蔽化、合法化。

## IOC

> 0C980F475766F3A57F35D19F44B07666

## 参考来源

> [K7 Lab](https://labs.k7computing.com/index.php/vajraspy-an-android-rat/)

