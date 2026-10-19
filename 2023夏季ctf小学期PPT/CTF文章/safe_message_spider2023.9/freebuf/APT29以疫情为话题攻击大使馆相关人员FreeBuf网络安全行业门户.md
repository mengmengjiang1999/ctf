Nobelium 也称为 APT29 和 Cozy Bear，是一个疑似俄罗斯支持的高级网络犯罪团伙。两年前，他们发起的 SolarWinds
攻击使得无数防御团队夜以继日的工作。最近，APT29 又转换了攻击目标，将视线转移到了大使馆。

研究人员发现，APT29 正在冒充与土耳其大使馆有关的人员进行钓鱼邮件攻击。钓鱼邮件以 Omicron/Covid-19
疫情为诱饵，督促与大使馆有关的人应该格外注意。

![image.png-275.9kB](https://image.3001.net/images/20220303/1646274090_6220262a39e6aa970fb30.png!small)钓鱼邮件

电子邮件源地址是一个专注于社会事务的政府部门泄露的电子邮件账户。邮件从非洲一个法语国家发出，伪装成土耳其大使馆的邮件发送到讲葡萄牙语的国家，邮件本身是用英文写的。

邮件带有 .html 的附件，样本文件会创建恶意 JavaScript 文件。

![image.png-172.4kB](https://image.3001.net/images/20220303/1646274091_6220262b7138b438a2743.png!small)恶意
JavaScript 对比

最初，APT29 发起的 HTML Smuggling 攻击使用 EnvyScout 将文本转换为 .iso 文件。EnvyScout
是该组织的工具之一，都是 `x-cd-image`应用程序类型的文件。如下所示，创建 .iso 文件的函数已经被简化了。

![image.png-127.5kB](https://image.3001.net/images/20220303/1646274092_6220262c6992e89ed5ede.png!small)创建
ISO

创建的 .ISO 文件被用户打开后，Windows 将文件挂在到可用驱动器号上。

![image.png-324.6kB](https://image.3001.net/images/20220303/1646274093_6220262d0df6976c35855.png!small)挂载
ISO 文件

APT29 此前使用的恶意文件和最新的而已文件都包含指向 DLL 文件的快捷方式。bin 文件夹中的 DLL 文件名为
`DeleteDateConnectionPosition.dll`。

后续的载荷为 Cobalt Strike，快捷方式使用名为 `DeleteDateConnectionPosition`的导出函数启动 DLL。

![image.png-308.8kB](https://image.3001.net/images/20220303/1646274094_6220262e0aa051baa9200.png!small)DLL
导出函数

DLL 文件的许多函数中都包含垃圾代码，其中包含 C&C 服务器。

![image.png-260.2kB](https://image.3001.net/images/20220303/1646274094_6220262e7aa73ee3b8a12.png!small)C&C
服务器

## JARM 指纹

C&C 服务器 `sinitude.com`的 JARM 指纹在很多服务器上被发现，其中许多服务器也仍然是 Cobalt Strike 服务器。

在恶意软件家族 BazarLoader 有关的 C&C 服务器上也发现了相同的 JARM 指纹，该恶意软件家族不会在俄文计算机上运行。

查看遥测数据，有几个 IP 地址连接到 C&C 服务器。但分析后发现，其实只有一个 IP 地址创建了完整链接，该地址位于乌克兰第二大城市哈尔科夫，且是
Tor 网络中的一部分。

## 结论

APT29 使用的技术与过去类似，钓鱼邮件仍然是有效的攻击方式。

## IOC

> A896C2D16CCADCDEDD10390C3AF3399361914DB57BDE1673E46180244E806A1D0  
> 3CB0D2CFF9DB85C8E816515DDC380EA73850846317B0BB73EA6145C026276948  
> 6EE1E629494D7B5138386D98BD718B010EE774FE4A4C9D0E069525408BB7B1F7  
> sinitude.com

## 参考来源

> [Fortinet](https://www.fortinet.com/blog/threat-research/nobelium-returns-> to-the-political-world-stage)

