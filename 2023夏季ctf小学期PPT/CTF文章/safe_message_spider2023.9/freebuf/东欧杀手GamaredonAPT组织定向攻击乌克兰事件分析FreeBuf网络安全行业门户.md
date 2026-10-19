##  概述

**GamaredonAPT组织是疑似具有东欧背景的APT团伙，该组织攻击活动最早可追溯到2013年，其主要针对乌克兰政府机构官员，反对党成员和新闻工作者，以窃取情报为目的。**

根据奇安信红雨滴团队观测从2019年末至今，Gamaredon组织保持高强度的活跃状态，且每次活动都与乌克兰地区的政治以及安全动态有关。2020年1月25日乌克兰安全局宣布在2019年共阻止了482次针对关键基础设施的网络攻击。

在五一假期前后，奇安信红雨滴团队发现Gamaredon组织开始了新活动，在此次活动中，该组织依然使用模板注入的方式从远程服务器下载payload，与以往不同的是本次活动下载的payload为带有cve-2017-11882漏洞的rtf文档，而非以往的带有恶意的宏文档来执行后续代码，由于模板注入免杀效果较好，VT上仅有为数不多的杀软报毒。

![](https://image.3001.net/images/20200509/1588994239_5eb620bff2918.png!small)

##  样本分析

执行流程如下：

![](https://image.3001.net/images/20200509/1588994251_5eb620cb6a445.png!small)

###  诱饵文档

此次捕获的样本，相关信息如下：

**文件名** |  **MD5** |  **模板注入地址** |  **修改时间**  
---|---|---|---  
**Условия создание фрагмента.docx** |  89d6bbbaa54253f56af8769ed6c1e9ec  |
<http://logins.kl.com.ua/sectigoprotect.cer> |  2020-05-01 22:32:14  
**Условия.docx** |  e6183f5be1d907fb9a53e08b5c28a9ae  |
<http://logins.kl.com.ua/digital.cer> |  2020-04-28 21:25:24  
  
样本均采用模板注入技术执行后续payload，此方式能起到极好的免杀效果，通过奇安信新一代反病毒引擎可精确检测除模板注入地址：

![](https://image.3001.net/images/20200509/1588994262_5eb620d64281f.png!small)

打开文档后，word会向远程服务器下载恶意的RTF文档并运行：

![](https://image.3001.net/images/20200509/1588994270_5eb620dec6b14.png!small)

文档内容如下：

![](https://image.3001.net/images/20200509/1588994277_5eb620e587ab2.png!small)![](https://image.3001.net/images/20200509/1588994281_5eb620e9bc5ff.png!small)

###  RTF文档信息

**文件名** |  **MD5**  
---|---  
**Digital.cer** |  63f4f59656bba5cb700f7f252028be7f  
**SectigoProtect.cer** |  fd1077af257671250e666d07e99565a1  
  
![](https://image.3001.net/images/20200509/1588994288_5eb620f086699.png!small)

使用11882漏洞，调用CMD向远程服务器发起请求，下载并执行2.msi程序：

![](https://image.3001.net/images/20200509/1588994297_5eb620f99ec4c.png!small)

###  恶意Msi

**文件名** |  **MD5**  
---|---  
**2.msi** |  0fe3f5fbf08c53ee45d8094632dbdb59  
  
Msi的主要功能为Droper释放各个模块：

![](https://image.3001.net/images/20200509/1588994313_5eb62109d432e.png!small)

其中的二进制文件为SFX自解压文件：

![](https://image.3001.net/images/20200509/1588994319_5eb6210f97412.png!small)

在C盘dllbroker目录下释放如下文件：

![](https://image.3001.net/images/20200509/1588994324_5eb62114a083a.png!small)

会先调用WScript.exe执行System.vbe：

**文件名** |  **MD5**  
---|---  
**System.vbe** |  787ebad76b4f40b4fb19451d17a941cd  
  
内容如下：

![](https://image.3001.net/images/20200509/1588994335_5eb6211f50c97.png!small)

在dllbroker目录下生成System.lnk快捷方式指向自身，调用CMD执行Zjv0obArqjtjrdV0Haf0JAmZCyY2Sl.bat

**文件名** |  **MD5**  
---|---  
**Zjv0obArqjtjrdV0Haf0JAmZCyY2Sl.bat** |  0d3b300ab76a2b9fe092b8e670158216  
  
Bat脚本内容如下：

![](https://image.3001.net/images/20200509/1588994342_5eb62126e2e9c.png!small)

将本目录下的System.lnk拷贝到启动目录下实现持久化，并运行brokernet.exe程序。

**文件名** |  **MD5**  
---|---  
**brokernet.exe** |  7df85f5215c5a11c4e2ad007bd5b1571  
  
.net程序加了.NETReactor的壳：

![](https://image.3001.net/images/20200509/1588994351_5eb6212f9f4ce.png!small)

主要功能为后门程序：

![](https://image.3001.net/images/20200509/1588994356_5eb62134a7031.png!small)

读取同目录下的vmcheck32.dll文件，解密C2，并发起请求，vmcheck32.dll内容如下：

![](https://image.3001.net/images/20200509/1588994363_5eb6213b10837.png!small)

Base64解密后如下：

![](https://image.3001.net/images/20200509/1588994367_5eb6213fd7c95.png!small)

连接远程服务器：

![](https://image.3001.net/images/20200509/1588994372_5eb62144c98f8.png!small)

收集本机相关信息如IP地址、硬件信息等：

![](https://image.3001.net/images/20200509/1588994378_5eb6214a92ec8.png!small)

从远程服务器如下文件：

![](https://image.3001.net/images/20200509/1588994383_5eb6214fd8a70.png!small)

调用CSC.exe在固定目录下生成可执行文件。

meqbjtdp.cmdline内容如下：

![](https://image.3001.net/images/20200509/1588994392_5eb62158d7d29.png!small)

**文件名** |  **MD5**  
---|---  
**dwm.exe** |  fe4e7581f9e3093a5ef528f75e05e1b5  
**msdtc.exe** |  37192f9f3d4c05ab38a0eafb297d6e35  
**svchost.exe** |  ad918fdcece862134a84a21d8abcc63f  
  
可能生成的目录如下：

**目录名**  
---  
**C:\Program Files (x86)\Windows Media Player\Skins\**  
**C:\System Volume Information\**  
**C:\Documents and Settings\**  
**C:\Boot\zh-CN\**  
**C:\ProgramData\Favorites\**  
**C:\Windows\tracing\**  
**C:\PerfLogs\Admin\**  
  
生成的可执行文件主要功能为启动器，用于启动brokernet.exe。

![](https://image.3001.net/images/20200509/1588994403_5eb6216381d08.png!small)

由于在分析过程中网络连接不稳定导致后续的行为丢失，不管怎么样，这是一个成熟度非常很高的后门，我们将其命名为“BrokerGama”。

##  关联分析

通过奇安信ALPHA威胁分析平台等内部数据和公开威胁情报信息,我们发现在[logins.kl.com.ua](https://www.virustotal.com/gui/url/23b7796b9d800e4567929ad2d9f6be77251452cb0a81c03c4edd8edb277afad4)域名上还有一个名为4.msi的可执行文件。

![](https://image.3001.net/images/20200509/1588994409_5eb621698187c.png!small)

**文件名** |  **MD5**  
---|---  
**4.msi** |  b5622716e68468ff38d32ef5f4795a87  
  
里面同样是SFX自解压文件，但是释放的payload却大不相同，在%appdata%目录下释放service文件：

![](https://image.3001.net/images/20200509/1588994416_5eb62170ccc3e.png!small)

**文件名** |  **MD5**  
---|---  
**service.exe** |  3973d7da737d0cc7b6b8536f36f0c98a  
  
有趣的是，该Spy类的软件由VC编写。主要功能为窃取相关信息。

截屏保存为screen.jpeg：

![](https://image.3001.net/images/20200509/1588994423_5eb6217730bad.png!small)

遍历Discord\\\Local Storage和Authy Desktop\\\Local Storage目录下的文件：

![](https://image.3001.net/images/20200509/1588994429_5eb6217dc2032.png!small)

判断Telegram是否安装，拷贝tdata目录下的数据：

![](https://image.3001.net/images/20200509/1588994436_5eb62184cf4a2.png!small)

收集FileZilla相关信息：

![](https://image.3001.net/images/20200509/1588994441_5eb62189decbb.png!small)

寻找Total Commander 文件管理器配置文件：

![](https://image.3001.net/images/20200509/1588994447_5eb6218f724fa.png!small)

收集pidgin即时通讯软件相关配置文件：

![](https://image.3001.net/images/20200509/1588994452_5eb62194aaf0d.png!small)

收集虚拟货币钱包：

![](https://image.3001.net/images/20200509/1588994457_5eb6219979adb.png!small)

**相关路径**  
---  
**Ethereum\\\keystore**  
**Electrum\\\wallets**  
**Electrum-NMC\\\wallets**  
**com.liberty.jaxx\\\indexedDB**  
**Exodus\\\exodus.wallet**  
**Fetch\\\Local Storage**  
**Eidoo\\\Electron storage**  
**MyCrypto\\\Local Storage**  
**Bitcoin\\\wallets**  
**Coinomi\\\wallet**  
**Guarda\\\Local Storage**  
**Peercoin\\\wallets**  
**Monero\\\wallets**  
**.bitpay\\\app\\\Local Storage**  
  
收集steam相关文件：

![](https://image.3001.net/images/20200509/1588994464_5eb621a0ec6fd.png!small)![](https://image.3001.net/images/20200509/1588994479_5eb621af3587b.png!small)

获取本机相关信息：

![](https://image.3001.net/images/20200509/1588994484_5eb621b440120.png!small)

获取NordVPN.exe和ProtonVPN.exe相关文件，以及获取浏览器存储的账号密码：

![](https://image.3001.net/images/20200509/1588994491_5eb621bb1110d.png!small)

获取浏览器的相关记录：

![](https://image.3001.net/images/20200509/1588994496_5eb621c0005b8.png!small)

之后将上述数据打包成zip文件发送给远程服务器：

![](https://image.3001.net/images/20200509/1588994502_5eb621c62a282.png!small)

IP地址：193.109.84.21，

打包后的内容如下：

![](https://image.3001.net/images/20200509/1588994508_5eb621ccc2f25.png!small)

基于样本中出现的字符串，我们将此类样本命名为“grbrSpy”。

通过对Gamaredon APT组织最近两个月的样本进行归类，我们猜测该行动应该是在二月份谋划，三月份实施攻击一直持续到现在。

**文件名** |  **MD5**  
---|---  
**BILATERAL COOPERATION PLAN.DOCX** |  b8bee6cba4ec62b05bacbd5b6e79cf94  
**BILATERAL COOPERATION PLAN.DOCX** |  b99dceea34d883db0ba4db7d626b11c2  
**OSCE.docx** |  7ef3d61b6e56de27c689c668b4688414  
**2ce959b961c81e34f4d4ccb4a23fab5b.zip** |  2ce959b961c81e34f4d4ccb4a23fab5b  
**OSCE.docx** |  6928b6c0da32bfd34a837dafd42b3abe  
**OSCE.docx** |  4da1af09833868e013e02add23e59957  
**Project TIKA in Ukraine.docx** |  7cdf57c02f50e6477452678d3023cdb8  
**Запит на iнформацiю.docx** |  2147f94942593ef3473ea00c83c2267d  
**OSCE.docx** |  b54ad8e721a2c8175daa357dc9252103  
**Р’iС‚Р°Р** **Ѕ** **Р** **Ѕ** **С** **Џ** **РЎР‘Р** **Ј.docx** |
c047dd99d3658e5df1d0f14f0beb7917  
**Вiтання СБУ.docx** |  b6e30ea779ab250032fb7f3c2c493778  
**Р’iС‚Р°Р** **Ѕ** **Р** **Ѕ** **С** **Џ** **РЎР‘Р** **Ј.docx** |
971c53db7f875a1008995b0397cba489  
**21-540-0215.docx** |  7ed9035341a1906ff731236633b8d911  
**Запит на iнформацiю.docx** |  8aeba52be05a59306e54ef9baa917658  
**Contacts of the embassy.docx** |  7219192d3fce7a1b2a0b6320da6cc4a3  
**Embassy of Ukraine in Hungary.docx** |  6885d6b44be537824377b74b63534d82  
**21-540-0215.docx** |  9786a23382b5d7ed1f1f8d640cfc82b5  
**Посольство Укра** **ї** **ни** **в** **Угорщин** **і.docx** |
ffa2fc9b24b87b6eead448641eb1eee8  
**Посольство Укра** **ї** **ни** **в** **Угорщин** **і.docx** |
3352636bdec80c3a6876d09cb043aa9d  
**PROJECT.DOCX** |  3140e5c776400c841efbc79b85bf245a  
**PROJECT.DOCX** |  d10c70f8eef196e148fea275230de1d9  
**PROJECT.DOCX** |  9afe18faeb125c1bd70d3***6d1397aa  
**contact.docx** |  27a70ddc4e1626792b71e12b54af9666  
**email.docx** |  521bf37724aa2bef9ffd4ceb910c8a2a  
**20200420_TATB.docx** |  67735f22639a5a8bc13d811eba88fbe3  
**Условия.docx** |  e6183f5be1d907fb9a53e08b5c28a9ae  
**Условия рекламной интеграции.docx** |  d8d285b34e588a12d946828c5c097ec3  
**Conditions.docx** |  5616b794188223d5cd567fdd91ce676b  
**Условия создание фрагмента.docx** |  89d6bbbaa54253f56af8769ed6c1e9ec  
  
部分诱饵截图如下：

![](https://image.3001.net/images/20200509/1588994521_5eb621d99e4ef.png!small)![](https://image.3001.net/images/20200509/1588994526_5eb621de6b2c6.png!small)

上述所有样本创建时间均为2020-02-25 05:41:00，且文档的元数据有相似之处：

![](https://image.3001.net/images/20200509/1588994533_5eb621e5f048d.png!small)

Creator均为“DESKTOP-”开头，我们推测这些模板注入的样本为该团伙的ToolKit生成，在该团伙早期的样本中同样存在该现象：

![](https://image.3001.net/images/20200509/1588994541_5eb621ed11a53.png!small)

同时当我们对上述brokernet.exe，也就是“brokerGama”家族的样本进行关联时发现了大量的相似样本，集中出现在4月份初，伪装成各式各样的软件。

![](https://image.3001.net/images/20200509/1588994547_5eb621f322166.png!small)

通过VT_RedDrip的沙箱可以看到这类样本的行为和上述分析一致：

![](https://image.3001.net/images/20200509/1588994553_5eb621f957295.png!small)

有些样本在dclib目录下带有反虚拟机模块：

![](https://image.3001.net/images/20200509/1588994560_5eb62200078db.png!small)

##  总结

2020年以来，疫情肆虐全球，同时网络空间的攻击活动也越发频繁，近期，东欧形势备受关注，而具有该国背景的APT组织近期也活动频繁。

奇安信红雨滴团队提醒广大用户，切勿打开社交媒体分享的来历不明的链接，不点击执行未知来源的邮件附件，不运行夸张的标题的未知文件，不安装非正规途径来源的APP。做到及时备份重要文件，更新安装补丁。

若需运行，安装来历不明的应用，可先通过奇安信威胁情报文件深度分析平台（<https://sandbox.ti.qianxin.com/sandbox/page>）进行简单判别。目前已支持包括Windows、安卓平台在内的多种格式文件深度分析。

![](https://image.3001.net/images/20200509/1588994579_5eb62213d19db.png!small)

##  IOC

**MD5**

> 89d6bbbaa54253f56af8769ed6c1e9ec
>
> e6183f5be1d907fb9a53e08b5c28a9ae
>
> 0fe3f5fbf08c53ee45d8094632dbdb59
>
> 787ebad76b4f40b4fb19451d17a941cd
>
> 0d3b300ab76a2b9fe092b8e670158216
>
> 7df85f5215c5a11c4e2ad007bd5b1571
>
> fe4e7581f9e3093a5ef528f75e05e1b5
>
> 37192f9f3d4c05ab38a0eafb297d6e35
>
> ad918fdcece862134a84a21d8abcc63f
>
> b5622716e68468ff38d32ef5f4795a87
>
> 3973d7da737d0cc7b6b8536f36f0c98a

**C2**

> logins.kl.com.ua
>
> netskacm.mcdir.ru
>
> 193.109.84.21：80

 ***本文作者：奇安信威胁情报中心，转载请注明来自FreeBuf.COM**

