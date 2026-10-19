思科此前揭露了 Arid Viper APT 组织的攻击活动，该组织自从 2017 年来经常使用 Delphi 恶意样本。Arid Viper APT
组织被认为与加沙地区存在利益关联，该组织在 2021 年 10 月的攻击行动中使用 Micropsia 恶意软件。

攻击者基于 Delphi 开发了 Micropsia 恶意软件针对巴勒斯坦发起攻击，涉及到的样本多为政治内容相关。最近，Arid Viper
组织利用最初发布在土耳其国营通讯社 Anadolu 和巴勒斯坦 MAAN 发展中心的内容为诱饵，针对巴勒斯坦的机构发起攻击。

## Arid Viper

Arid Viper 也被称为双尾蝎或 APT-C-23，于 2015
年被首次曝光。该组织主要目的是进行间谍活动和信息窃密，其攻击目标主要是巴勒斯坦的组织及个人。Arid Viper
在技术迭代上并不频繁，主要针对移动平台和桌面平台发起攻击，攻击工具也主要围绕着 Delphi 开发的 Micropsia 恶意软件进行更新升级，后续也移植了
Python 版本和 Android 版本的恶意软件。

## 攻击行动

思科研究人员发现了针对巴勒斯坦发起的新一轮攻击行动，所使用的技术手段与该组织 2017 年的攻击行动基本一致。

2019 年使用的诱饵文档声称是 2018 年的年度报告，但实际内容是 2014 年和 2015 年的。

![image.png-184.9kB](https://image.3001.net/images/20220211/1644557898_6205f64a74f3ee3f6ed7b.png!small)诱饵文档

该组织使用的一系列恶意文件如下所示：

![image.png-317kB](https://image.3001.net/images/20220211/1644557908_6205f6547a6e9fda468ba.png!small)诱饵文档列表

政治类主题的文件在 2018 年到 2019 年有所减少，但在 2020 年和 2021 年又显著增多。

## 新的诱饵文件

新发现的诱饵文件中有与政治有关的内容，并且使用了阿-拉-伯-语，这都表明攻击目标主要针对巴勒斯坦的组织。

2021 年 9 月发现的诱饵文件包含关于巴勒斯坦统一的内容，来自 2021 年 9 月 3 日 Anadolu 发布的文章。

![image.png-149.5kB](https://image.3001.net/images/20220211/1644557910_6205f6561a486b2680b3a.png!small)诱饵文档

同一时期发现的另一个诱饵文件，取材自 MAAN 发展中心（旨在促进巴勒斯坦发展的机构）撰写的关于巴勒斯坦社会和经济可持续发展的文章。

![image.png-195.7kB](https://image.3001.net/images/20220211/1644557911_6205f6571df2c28d99034.png!small)诱饵文档

在 2021 年 7 月捕获的一个诱饵文件中则包含巴勒斯坦卫生部的声明文件。同年 3
月，诱饵文件中包含巴勒斯坦政治活动家对更早时发布的总统令提出的一系列问题，总统令中要求在立法选举前要尊重言论自由。

![image.png-122.4kB](https://image.3001.net/images/20220211/1644557911_6205f657c5cb11874a314.png!small)诱饵文档

## 投递

在调查分析中，没有发现任何有关的电子邮件或者社交媒体内容。只发现了恶意样本和包含恶意样本的压缩文件，这与在 2017
年发现该组织的攻击行动是一致的，研究人员猜测攻击者仍然是通过电子邮件来进行样本投递。

## 样本分析

样本仍然是基于 Delphi 开发的 Micropsia，界面的 Delphi 表单中有四个计时器按钮，用于执行不同的恶意行为。

![image.png-33.9kB](https://image.3001.net/images/20220211/1644557912_6205f658578e872f8a722.png!small)Delphi
表单

![image.png-211.4kB](https://image.3001.net/images/20220211/1644557912_6205f658b67d7005ebd89.png!small)表单内容

### 部署诱饵

一个计时器负责提取诱饵文档并将其保存到 `%TEMP%`文件夹，再通过 `ShellExecute`打开显示。

![image.png-276.3kB](https://image.3001.net/images/20220211/1644557913_6205f659410703f306512.png!small)提取并显示诱饵文档

如果使用 `-start`启动样本，将会跳过提取并显示诱饵文档的部分直接跳转到 RAT 远控木马。

### 持久化

一个计时器负责维持持久化。在 `%TEMP%`文件夹下为自己创建一个快捷方式，再将快捷方式移动到当前用户的启动文件夹，以此完成持久化。

### 信息收集

一个定时器用于收集失陷主机的信息，如下所示：

> 为失陷主机生成一个 ID 并保存到文件中，如 `%APPDATA%\dsfjj45k.tmp```读取计算机名和用户名，将二者与 ID 连接起来
> `<COMPNAME>_<username>_<pcid>```使用`SELECT * FROM AntiVirusProduct`通过
> `winmgmts:\\localhost\root\SecurityCenter2`收集安装的杀软信息  
> 获取操作系统信息，如安装软件名称

收集到的信息要进行 base64 编码：

    
    
    vcqmxylcv= base64 encoded <COMPNAME>_<username>_<pcid>vcnwaapcv= base64 encoded AV Name list.vcllgracv= base64 encoded OS version string.vcwjlxycv= base64 encoded implant command line.vccodwfcv= base64 encoded hardcoded flag.

通过 HTTP POST 请求将数据发送到 C&C 服务器。

### 远控

发送了相关信息后，样本等待 C&C 服务器的执行命令。

命令执行的结果会通过以下变量回传 C&C 服务器：

    
    
    vcgqjdlrcv = hardcoded value 0.mugnaq = base64 encoded screenshot or command output.

C&C 服务器下发的命令以 `;<cmd_code>;<base64_encoded_supporting_data>;`为格式，常用命令如下所示：

![image.png-37.8kB](https://image.3001.net/images/20220211/1644557913_6205f659b067a269354cc.png!small)命令下发

样本与 C&C 服务器通信使用两个不同的 URL，一个用于回传远控命令、一个用于回传屏幕截图。

    
    
    hxxps://deangelomcnay.news/qWIlIdKf2buIH0k/GbrHoIfRqtE69hH/ZCgbo9EVhYMA8PXhxxps://deangelomcnay.news/qWIlIdKf2buIH0k/GbrHoIfRqtE69hH/bu5EmpJE7DUfzZD

## 结论

从 2017 年到 2021 年，Arid Viper 持续发动进攻性网络攻击。在公开披露后，攻击者通常会拆除攻击基础设施并且修改恶意样本。但 Arid
Viper 并未因攻击行动被披露而受到震慑，照常使用相同的 TTP 进行攻击。

Arid Viper 的技术并不十分先进，但是随着时间的不断推移，攻击者也在不断测试新的攻击技术。如 Micropsia 具备 Delphi、Python
和 Android 不同版本。

## IOC

> d4e56e3a9dec89cc32df78aa4ba8b079aa5e697ed99a1e21e9bd31e85d5d1370  
> 1d4e54529feef53850f97f39029a906d53f3d4b2aea8373e27c413324a55681c  
> bc03948ce4d88f32017d4a1725a05341d3ff72a616645d9893b8f5d11068217f  
> 8a730266c62fa79435497b1d7db38011e63b6c53b48593d65c24c36044d92dba  
> f2f36a72cfb25cef74ff0ea8e3ad1c49c6dc3e128fd60a2717f4c5a225e20df2  
> 895adb54a13d9ebf3f7215f1bad77c0c548e7dd4c58c3a338d440520efcb8fc9  
> 27eaeb7f0195230e22d5beacc05b7d944aaec4894fbc02824f59b172e360713f  
> 7b9087d91a31d03dd2c235d8debf8ed10f4b82c430a236d159e06e7fb47464a9  
> aa507bbe5d2a32f6e1e3f311c1baf93fd4707def8596083f26683e85972f5ac0  
> c9d7b5d06cd8ab1a01bf0c5bf41ef2a388e41b4c66b1728494f86ed255a95d48  
> 0a55551ade55705d4be6e946ab-58a26d7cf8087558894af8799931b09d38f3bc  
> c7e74330440fcf8f6b112f5493769de6cdbdea5944ab78697ab115c927cbd0a1  
> 2d03ff4e5d4d72afffd9bde9225fe03d6dc941982d6f3a0bbd14076a6c890247  
> e288d7e42c8cdbf0156f008ff7d663f8c8e68faa2e902d51f3287f1bceae79b2  
> 5463b3573451d23f09cb3f6f3c210de182ed0dd8a89459381a7f69aa7f8ac9b4  
> deangelomcnay.news  
> juliansturgill.info  
> earlahenry.com  
> nicholasuhl.website  
> cooperron.me  
> dorothymambrose.live  
> ruthgreenrtg.live  
> hxxp://deangelomcnay.news/qWIlIdKf2buIH0k/GbrHoIfRqtE69hH/ZCgbo9EVhYMA8PX  
> hxxp://deangelomcnay.news/qWIlIdKf2buIH0k/GbrHoIfRqtE69hH/bu5EmpJE7DUfzZD  
> hxxps://cooperron.me/qWIlIdKf2buIH0k/GbrHoIfRqtE69hH/  
> hxxps://cooperron.me/qWIlIdKf2buIH0k/GbrHoIfRqtE69hH/  
> hxxps://dorothymambrose.live/hx3FByTR5o3zNZYD/sYkaiHz0Mse13C79dy1I/  
> hxxp://dorothymambrose.live/hx3FByTR5o3zNZYD/sYkaiHz0Mse13C79dy1I/  
> hxxps://nicholasuhl.website/X2EYSWlzSZgSUME210Zv/YPPV6kFl2PwwF0TEVHMy/  
> hxxp://nicholasuhl.website/X2EYSWlzSZgSUME210Zv/YPPV6kFl2PwwF0TEVHMy/  
> hxxps://earlahenry.com/Ct2azbEP57LtWgmK/lWaPwemAJ3LPFmDH/  
> hxxp://earlahenry.com/Ct2azbEP57LtWgmK/lWaPwemAJ3LPFmDH/  
> hxxp://juliansturgill.info/um2NxySaF4L5mSYE/KY1hNeVvrE1XCrKP/

## 参考来源

> [Talos](https://blog.talosintelligence.com/2022/02/arid-viper-targets-> palestine.html)

