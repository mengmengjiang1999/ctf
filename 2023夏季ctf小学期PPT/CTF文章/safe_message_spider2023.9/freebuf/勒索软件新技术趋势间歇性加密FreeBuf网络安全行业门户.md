攻击者正在大量应用间歇性加密来快速加密受害者的文件，这也是一个重大的卖点。

从两方面来看，间歇性加密对勒索软件运营者来说是非常重要的：

  *  **速度** ：完全加密是非常耗时的，而时间对攻击者来说是非常重要的，加密速度越快就越能防止被检测与拦截
  *  **逃避** ：防御者可以使用统计分析来检测勒索软件的加密操作，通过评估文件 IO 操作强度或文件修改的相似性可以进行检测。与完全加密相比，间歇加密可以有效规避此类分析

2021 年夏天，LockFile 勒索软件是首批引入间歇性加密技术的勒索软件家族之一。后来，越来越多的勒索软件都应用了这一技术。

## Qyick 勒索软件

2022 年 8 月末，研究人员发现一个名为 lucrostm 的用户在地下犯罪论坛上宣传一种名为 Qyick 的新型勒索软件。

Qyick 勒索软件是一次性买断制，而非更常见的订阅制。根据购买的级别，价格从 0.2 比特币到 1.5
比特币不等。卖家可以得到保证，如果勒索软件在购买六个月内被安全软件检测到，攻击者将会以六折到八折的价格提供一个新的样本。

![image.png-400.7kB](https://image.3001.net/images/20221001/1664631583_6338431f5b3cbe8d5fa6e.png!small)Qyick
勒索软件广告

Qyick 勒索软件是用 Go 编写的，并且具备间歇性加密功能。lucrostm 声称 Qyick 勒索软件具备如此快的加密能力，就是通过间歇性加密实现的。

当前版本的 Qyick 并不具备数据泄露功能，但 lucrostm 表示未来将会新增执行任意可执行代码的功能，主要用于数据泄露。

## Agenda 勒索软件

Agenda 勒索软件在 2022 年 8
月首次被发现，主要针对非洲和亚洲的医疗保健和教育组织进行攻击。该勒索软件有一些自定义选项，包括更改加密文件的文件扩展名以及要终止的进程和服务列表。

Agenda 勒索软件支持多种加密模式（`skip-step`、`percent`和 `fast`），如下所示：

![image.png-367.4kB](https://image.3001.net/images/20221001/1664631584_633843203f45c4bda3069.png!small)帮助信息

每种模式如下所示：

加密方式| 描述  
---|---  
skip-step| 每 Y MB 加密文件、跳过 N MB  
fast| 加密文件的前 N MB  
percent| 每 N MB 加密文件、跳过 P MB（P 为总大小的百分比）  
  
## BlackCat 勒索软件

BlackCat 勒索软件在 2021 年底开始频繁攻击，也是第一个已知的使用 Rust 编写的勒索软件。BlackCat 背后的开发者于 2021 年
12 月初首次被发现在俄罗斯地下犯罪论坛上进行宣传。

![image.png-320.4kB](https://image.3001.net/images/20221001/1664631585_6338432124508de94a695.png!small)论坛信息

BlackCat 勒索软件运行着勒索软件即服务（RaaS），使用防弹主机来部署网站，并且使用比特币混合服务来进行匿名交易。

![image.png-52.6kB](https://image.3001.net/images/20221001/1664631586_63384322cdfb99cfb009f.png!small)ALPHV
Collections 一个可搜索泄露受害者数据的数据库

BlackCat 勒索软件攻击全球各种组织与企业，2022 年 9 月，BlackCat 勒索软件针对意大利的国有能源服务公司 GSE 发起攻击。

SentinelLabs 研究员 Aleksandar Milenkoski 对 BlackCat 勒索软件样本进行了逆向分析，加密模式如下所示：

![image.png-94.4kB](https://image.3001.net/images/20221001/1664631587_63384323aa842ed2002f9.png!small)加密模式信息

与完全加密相比，使用 Auto 模式的 BlackCat 勒索软件可以显著减少加密时间。

## P=LAY 勒索软件

该勒索软件是勒索软件领域的新玩家，于 2022 年 6 月下旬首次被发现。最近，该勒索软件攻击了多个知名目标，如 2022 年 8
月攻击了阿根廷科尔多瓦法院。

![image.png-15.1kB](https://image.3001.net/images/20221001/1664631588_6338432452c2d3b265956.png!small)勒索软件勒索信息

与 Agenda 和 BlackCat 相比，该勒索软件不可配置。其加密模式是固定的：

> 如果文件大小小于或等于 0x3fffffff 字节，加密 2 个块
>
> 如果文件大小小于或等于 0x27fffffff 字节，加密 3 个块
>
> 如果文件大小大于 0x280000000 字节，加密 5 个块

分析时观察到一个样本每隔一个 0x100000 字节块进行加密，该文件包含空字符串，可以有效区分加密块与未加密块。

![image.png-802.8kB](https://image.3001.net/images/20221001/1664631588_63384324d9134b4710ce6.png!small)加密文件的部分内容

## Black Basta 勒索软件

Black Basta 是一个 RaaS 程序，于 2022 年 4 月出现。Black Basta 勒索软件接棒 Conti 勒索软件出现，该勒索软件采用
C++ 语言编写。

Black Basta 在勒索软件领域迅速占据了一席之地，两周内公布了二十多个受害者，主要集中在公用事业、技术、金融和制造业。

![image.png-206.6kB](https://image.3001.net/images/20221001/1664631589_63384325e008a221b9422.png!small)Black
Basta 网站

与 P=LAY 勒索软件一样，Black Basta 不具备可配置加密模式。其加密模式为：

> 如果文件大小小于 704 字节，完全加密
>
> 如果文件大小小于 4 KB，则从文件开头开始跳过 192 字节并每 64 字节进行加密
>
> 如果文件大小大于 4 KB，则从文件开头开始跳过 128 字节并每 64 字节进行加密

与 P=LAY 勒索软件类似，由于包含空字符，使加密块和未加密块在视觉上更容易区分。

![image.png-636.3kB](https://image.3001.net/images/20221001/1664631590_63384326bbdf372210ac3.png!small)Black
Basta 加密内容

## 结论

间歇性加密对于攻击者来说是非常有用的，这种方法有助于规避勒索软件检测机制，更快地加密文件。研究人员预计，间歇性加密将会被更多勒索软件家族所采用。

## IOC

> 5f99214d68883e91f586e85d8db96deda5ca54af  
> 8917af3878fa49fe4ec930230b881ff0ae8d19c9  
> 14177730443c70aefeeda3162b324fdedf9cf9e0  
> a996ccd0d58125bf299e89f4c03ff37afdab33fc

## 参考来源

> [SentinelOne](https://www.sentinelone.com/labs/crimeware-trends-ransomware-> developers-turn-to-intermittent-encryption-to-evade-detection/)

