**卡巴斯基持续关注分析Roaming
Mantis相关网络活动。该组织的攻击方法有所改进，不断在新的攻击目标上窃取资金。攻击者利用白名单和运行环境检测等技术避免被分析溯源。此外还检测到新的恶意软件家族：Fakecop和Wroba.j。**

##  传播方式

2018年该组织在原有域名劫持方法的基础上，增加了一种Wroba.g的传播方法SMiShing，使用的是一家物流公司的虚假交货通知。2019年确认了另一种新方法，利用恶意APK冒充快递公司，例如日本的Sagawa
Express、台湾的Yamato Transport和FedEx、韩国的CJ Logistics和俄罗斯的Econ Express。

![](https://image.3001.net/images/20200301/1583035243_5e5b336b40214.png!small)2020年2月，攻击者利用“为日方冠状病毒问题提供免费口罩”的短信进行攻击。再次说明犯罪分子在活动中总是利用热点话题。

##  白名单功能

Roaming Mantis在Wroba.g登陆页面（目前仅在朝鲜语页面）中采用了白名单功能，可逃避安全研究人员。
用户访问登录页面时，必须输入电话号码进行确认。 如果电话号码在白名单上，则登录页面会分发恶意app.apk：

##
![](https://image.3001.net/images/20200301/1583035570_5e5b34b2650fb.png!small)混淆技术

Wroba.g加载模块中利用了Multidex混淆技术，Multidex配置允许应用构建和读取多个索引文件。2019年，APK文件中使用Multidex隐藏恶意加载模块，分析表明它正在被一点一点地修改：

![](https://image.3001.net/images/20200301/1583035888_5e5b35f091471.png!small)用红色正方形标记的类${num}.dex是恶意加载程序模块，所有其他的DEX文件都是垃圾代码。Wroba.g的加密有效负载仍然在assets目录下，可以通过python脚本来解密。

##  目标分析

Wroba.g的目标是日本的运营商和在线银行，攻击者将受害者重定向到钓鱼网站，以窃取凭据：

![](https://image.3001.net/images/20200301/1583036932_5e5b3a04cd902.png!small)当恶意软件在受感染设备上检测到日本在线银行或特定移动运营商时，它会在后台连接到pinterest.com的恶意帐户获取钓鱼网站。向受害者推送消息，声称已阻止来自第三方的未经授权的访问，并要求用户单击按钮以确认是否要继续。如果用户单击此按钮，将重定向到假冒网站：

![](https://image.3001.net/images/20200301/1583037033_5e5b3a69ad24b.png!small)针对在线银行和移动运营商的软件包和其对应的帐户：

![](https://image.3001.net/images/20200301/1583037131_5e5b3acb410c8.png!small)从上表可以看出，截至2019年12月，所有账户都有相应的钓鱼网站。攻击者会不断更改这些URL。

##  最新发现

Roaming
Mantis一直使用Wroba.g和Wroba.f作为其主要的安卓恶意软件。2019年4月又发现其他两个恶意软件家族，Wroba.j和Fakecop。这两个恶意软件家族在基础设施、传播方式等方面与其他家族有一些相似之处。在‘[Roaming
Mantis: A melting pot of Android bots in
Botconf2019](https://www.botconf.eu/wp-content/uploads/2019/12/B2019-Ishimaru-Niseki-Ogawa-Mantis.pdf)’中展示了时间表、假冒品牌、恶意软件功能和洗钱方法。

根据检测数据，发现Wroba.j中垃圾短信功能：

![](https://image.3001.net/images/20200301/1583037613_5e5b3cadf0ee7.png!small)恶意软件从短信反馈结果自动创建电话号码列表，该恶意软件还可以检查国际移动用户识别码（IMSI），以识别移动运营商，并将电话号码添加到相关列表中。

![](https://image.3001.net/images/20200301/1583037725_5e5b3d1d7f185.png!small)根据下面显示的硬编码IMSIs和字符串，攻击者的目标是Docomo和软银移动运营商。

##
![](https://image.3001.net/images/20200301/1583037796_5e5b3d646cf2c.png!small)总结

Roaming
Mantis以经济利益为目标，并且极力避免被安全人员追踪。它现在正在采用白名单功能来实现这一目标，这个新方法目前只适用于韩语页面，但在其他语言中实现只是时间问题。

该组织非常积极地在Android恶意软件中使用SMiShing，这意味着所有受感染的移动设备可能形成一个僵尸网络，用于恶意软件的传送、用户信息窃取等。

##  APK MD5

> e6ae4277418323810505c28d2b6b3647 Wroba.g
>
> 939770e5a14129740dc57c440afbf558 Wroba.f
>
> 521312a8b5a76519f9237ec500afd534 Wroba.j
>
> 6d29caaa8b30cc8b454e74a75d33c902 Fakecop

***参考来源：[securelist](https://securelist.com/roaming-mantis-part-v/96250/)，由Kriston编译，转载请注明来自FreeBuf.COM**

  

