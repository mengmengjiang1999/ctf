McAfee 最近发现了一种新的 Android 恶意软件 Elibomi
针对印度纳税人展开攻击。该恶意软件伪装成报税应用程序，通过网络钓鱼窃取敏感的财务和个人信息。

2020 年 11 月发现的第一个攻击活动伪装成虚假的 IT 证书申请，而第二个攻击活动于 2021 年 5 月首次出现，伪装成虚假的报税程序。

最新的攻击行动中，恶意软件使用短信伪装成印度税务部门进行投递。攻击者发送目标用户的姓名使钓鱼更加可信，欺骗用户相信是合法的报税应用程序。

Elibomi 窃取的数据被暴露在互联网上，包括电子邮件地址、电话号码、短信/彩信以及财务和个人信息。

## 报税程序

Elibomi 使用税务部门的徽标诱使用户安装该应用程序，这些应用程序的包名称由一个随机词+另一个随机字符串+imobile（如
`direct.uujgiq.imobile`与
`olayan.aznohomqlq.imobile`）组成。![](https://image.3001.net/images/20210911/1631374229_613ccb95f399c93d441fd.png!small)

得到权限后，Elibomi
会尝试收集存储在受感染设备中的个人信息，例如电子邮件地址、电话号码和短信和彩信：![](https://image.3001.net/images/20210911/1631374235_613ccb9b49fe6e12707f5.png!small)

## 数据暴露

攻击者的其中一台 C&C
服务器暴露在互联网上，通过研究发现了攻击行动的主要投递方式。攻击者发送的短信督促用户检查所得税申报表的紧急更新，引诱用户点击恶意链接。![](https://image.3001.net/images/20210911/1631374242_613ccba2bf3fb92a1b417.png!small)

Elibomi
不仅将发送的短信暴露出来，窃取用户的账号列表也被暴露出来。![](https://image.3001.net/images/20210911/1631374252_613ccbacb3266ab941047.png!small)

用户点击恶意链接就会跳转到伪装成印度税务部门的钓鱼网站，该页面通过用户的真实姓名来进行描述，提高可信度。![](https://image.3001.net/images/20210911/1631374260_613ccbb4d64e887beb5c0.png!small)

针对每个用户分发不同的恶意软件。![](https://image.3001.net/images/20210911/1631374267_613ccbbb2e1f46db9637a.png!small)

分析发现，iMobile 虚假报税应用程序存在多种 Elibomi 变种。例如，一些 iMobile
应用程序只有登录页面，而在其他应用程序中，可以选择“注册”并申请虚假退税。![](https://image.3001.net/images/20210911/1631374290_613ccbd2e1453dab2e6ba.png!small)

受害者的敏感财务信息也暴露在互联网上：

![](https://image.3001.net/images/20210911/1631374313_613ccbe9553f68025e022.png!small)

## 虚假 IT 证书申请

发现在去年 11 月的攻击行动伪装成 IT 证书的申请。两次攻击行动的代码相似之处如下所示：

![](https://image.3001.net/images/20210911/1631374322_613ccbf2547ce56e95ce0.png!small)

恶意应用程序仿冒 IT 证书管理功能，假装验证设备。不仅请求短信权限，也会请求管理员权限，这让清除起来更加困难。

该恶意软件假装进行“安全扫描”，实际上在后台做的是窃取个人信息，如电子邮件、电话号码和短信彩信。![](https://image.3001.net/images/20210911/1631374330_613ccbfa819824053418d.png!small)

这次攻击行动的 C&C
服务器也对外暴露了数据：![](https://image.3001.net/images/20210911/1631374344_613ccc080a4b53cb70c3a.png!small)

## 字符串混淆

攻击者设计了字符串混淆技术，所有字符串都通过调用不同的类进行解码。![](https://image.3001.net/images/20210911/1631374353_613ccc114a9f4b9fc9256.png!small)

算法是简单的替换密码，例如将 35 替换为 `h`、将 80 替换为
`t`混淆字符串。![](https://image.3001.net/images/20210911/1631374358_613ccc16143c7334e67e6.png!small)

## IOC

> 1e8fba3c530c3cd7d72e208e25fbf704ad7699c0a6728ab1b290c645995ddd56  
> 7f7b0555563e08e0763fe52f1790c86033dab8004aa540903782957d0116b87f  
> 120a51611a02d1d8bd404bb426e07959ef79e808f1a55ce5bff33f04de1784ac  
> ecbd905c44b1519590df5465ea8acee9d3c155334b497fd86f6599b1c16345ef  
> da900a00150fcd608a09dab8a8ccdcf33e9efc089269f9e0e6b3daadb9126231  
> 795425dfc701463f1b55da0fa4e7c9bb714f99fecf7b7cdb6f91303e50d1efc0  
> b41c9f27c49386e61d87e7fc429b930f5e01038d17ff3840d7a3598292c935d7  
> 8de8c8c95fecd0b1d7b1f352cbaf839cba1c3b847997c804dfa2d5e3c0c87dfe  
> ecbd905c44b1519590df5465ea8acee9d3c155334b497fd86f6599b1c16345ef  
> 326d81ba7a715a57ba7aa2398824b420fff84cda85c0dd143462300af4e0a37a  
> 154cfd0dbb7eb2a4f4e5193849d314fa70dcc3caebfb9ab11b4ee26e98cb08f7  
> c59ecd344729dac99d9402609e248c80e10d39c4d4d712edef0df9ee460fbd7b  
> 16284cad1b5a36e2d2ea9f67f5c772af01b64d785f181fd31d2e2bec2d98ce98  
> 98fc0d5f914ae47b61bc7b54986295d86b-502a9264d7f74739ca452fac65a179  
> 32724a3d2a3543cc982c7632f40f9e831b16d3f88025348d9eda0d2dfbb75dfe

## 参考来源

> [Mcafee﻿](https://www.mcafee.com/blogs/other-blogs/mcafee-labs/phishing-> android-malware-targets-taxpayers-in-india/)

