**近期发现四个新兴勒索软件组织：AvosLocker、Hive、HelloKitty、LockBit 2.0。** 它们活动频繁，未来可能造成更大的影响。

 **AvosLocker** 于6月底开始活动，其标志性图标为蓝色甲虫；

 **Hive** 是一种双重勒索勒索软件，于6月份开始活动，目前已经影响了28家组织；

 **HelloKitty**
最早可追溯到2020年，主要针对Windows系统，在今年7月份，HelloKitty的Linux变体开始针对VMware的ESXi hypervisor；

 **LockBit 2.0** 与一些引人注目的攻击事件有关，影响了多个行业，目前已有52名受害者，接下来本文将会对这些勒索软件进行详细分析。

## AvosLocker

AvosLocker是一种全新的勒索软件，于 **2021年7月4日首次被发现**
，其遵循RaaS模型，同名勒索软件运营商avos在暗网发布了广告，内容包括勒索软件功能等信息。

![1630894875_61357b1beadc882109060.png!small?1630894874289](https://image.3001.net/images/20210906/1630894875_61357b1beadc882109060.png!small?1630894874289)

AvosLocker在执行时首先打开一个Windows
shell，显示加密过程的进度。加密完成后会将.avos扩展名附加到加密文件中，并在每个加密目录中放置赎金便笺GET_YOUR_files_BACK.TXT。

![1630897714_613586325d87090dcf7c4.png!small?1630897712459](https://image.3001.net/images/20210906/1630897714_613586325d87090dcf7c4.png!small?1630897712459)

加密后文件：

![1630897744_61358650aae4d548f2b7d.png!small?1630897742823](https://image.3001.net/images/20210906/1630897744_61358650aae4d548f2b7d.png!small?1630897742823)

AvosLocker TOR网站：

![1630897770_6135866a311c234ed3914.png!small?1630897768575](https://image.3001.net/images/20210906/1630897770_6135866a311c234ed3914.png!small?1630897768575)

提交ID后，受害者将被索取赎金，赎金最低50000美元，最高75000美元。与其他勒索软件组一样，如果受害者没有在指定时间内支付，AvosLocker会提高勒索价格。

![1630898089_613587a9471497be2b809.png!small?1630898087900](https://image.3001.net/images/20210906/1630898089_613587a9471497be2b809.png!small?1630898087900)

目前他已经影响了七个组织：两个律师事务所，一个在英国，一个在美国；西班牙的一家物流公司；比利时的一家房地产公司；土耳其的一家公司；叙利亚交通组织和一个美国城市。

![1630898191_6135880fd312cbf6380d9.png!small?1630898190092](https://image.3001.net/images/20210906/1630898191_6135880fd312cbf6380d9.png!small?1630898190092)

## Hive

Hive勒索软件于 **2021年6月开始运营** ， **攻击的组织包括医疗服务提供商和一些中型组织，这些组织缺乏抵御勒索软件攻击的能力。**
Hive网站上公布了28名受害者，其中包括一家欧洲航空公司和三家美国机构，硬件零售、制造和法律部门。

![1630898353_613588b158b0123c2063d.png!small?1630898351540](https://image.3001.net/images/20210906/1630898353_613588b158b0123c2063d.png!small?1630898351540)

勒索软件执行时，它会下载两个批处理脚本，hive.bat尝试删除自身，第二个脚本shadow.bat负责删除系统的卷副本。Hive
ransomware将[Randomic characters].Hive扩展添加到加密文件中，并留下名为HOW_to_DECRYPT.txt的勒索说明。

![1630918200_6135d6381fa577c9dea50.png!small?1630918198341](https://image.3001.net/images/20210906/1630918200_6135d6381fa577c9dea50.png!small?1630918198341)

赎金通知中提供的登录凭据是针对特定受害者的。登录后，受害者可与Hive组织交谈并获取解密程序。

![1630918280_6135d688a6ab1830991c2.png!small?1630918278717](https://image.3001.net/images/20210906/1630918280_6135d688a6ab1830991c2.png!small?1630918278717)

## HelloKitty

HelloKitty于 **2020年底首次出现** ， **主要针对Windows系统。**
2021年7月，发现了一个名为fully_Linux.ELF的Linux（ELF）示例，可追溯到2020年10月，从今年3月开始，样本开始瞄准ESXi。

六家受Hello
Kitty影响的机构，包括意大利和荷兰制药机构、一家德国制造商、一家澳大利亚工业自动化解决方案机构、一家美国医疗机构和一家股票经纪人。赎金争论高达1000万美金，最低95万美金，同时支持BTC支付。

![1630918561_6135d7a1d5954d0fa8942.png!small?1630918559911](https://image.3001.net/images/20210906/1630918561_6135d7a1d5954d0fa8942.png!small?1630918559911)

Linux HelloKitty勒索软件参数：

![1630918607_6135d7cf8037cedacd12f.png!small?1630918605586](https://image.3001.net/images/20210906/1630918607_6135d7cf8037cedacd12f.png!small?1630918605586)

## LockBit 2.0

LockBit遵循RaaS模型，自 **2019年9月开始活跃** ，最近升级到了LockBit
2.0。自2021年6月以来，他们在阿根廷、澳大利亚、奥地利、比利时、巴西、德国、意大利、马来西亚、墨西哥、罗马尼亚、瑞士、英国和美国进行勒索活动。官网会有受害者文件解密发布倒计时，从而给所有受害者施压。

![1630918795_6135d88b0f63c92a201f2.png!small?1630918793162](https://image.3001.net/images/20210906/1630918795_6135d88b0f63c92a201f2.png!small?1630918793162)

攻击者声称他们的软件是就目前运行最快的加密软件。

![1630918851_6135d8c3522efaad5c404.png!small?1630918851739](https://image.3001.net/images/20210906/1630918851_6135d8c3522efaad5c404.png!small?1630918851739)

执行LockBit时，它开始加密文件并附加.LockBit扩展名，将加密文件的图标更改为LockBit 2.0徽标，加密完成后留下名为Restore-My-Files.txt的赎金说明。

![1630919135_6135d9df84e1b57a9d2d1.png!small?1630919133879](https://image.3001.net/images/20210906/1630919135_6135d9df84e1b57a9d2d1.png!small?1630919133879)![1630919139_6135d9e3bebfee7c71f34.png!small?1630919137794](https://image.3001.net/images/20210906/1630919139_6135d9e3bebfee7c71f34.png!small?1630919137794)

如果加密成功，LockBit 2.0勒索软件会修改受害者的桌面壁纸：

![1630919172_6135da04de51394574301.png!small?1630919171543](https://image.3001.net/images/20210906/1630919172_6135da04de51394574301.png!small?1630919171543)

官网受害者登录界面：

![1630919222_6135da3640624b4b751ed.png!small?1630919220256](https://image.3001.net/images/20210906/1630919222_6135da3640624b4b751ed.png!small?1630919220256)

## IOC

### AvosLocker

43b7a60c0ef8b4af001f45a0c57410b7374b1d75a6811e0dfc86e4d60f503856

fb544e1f74ce02937c3a3657be8d125d5953996115f65697b7d39e237020706f

3984968230c96d52d78af1905ea1b224e7de36776a6af398a0462321f3c22020

01792043e07a0db52664c5878b253531b293754dc6fd6a8426899c1a66ddd61f

### Hive Ransomware

A0b4e3d7e4cd20d25ad2f92be954b95eea44f8f1944118a3194295c5677db749

1e21c8e27a97de1796ca47a9613477cf7aec335a783469c5ca3a09d4f07db0ff

Fdbc66ebe7af710e15946e1541e2e81ddfd62aa3b35339288a9a244fb56a74cf

88f7544a29a2ceb175a135d9fa221cbfd3e8c71f32dd6b09399717f85ea9afd1

### Hello Kitty (Linux)

16a0054a277d8c26beb97850ac3e86dd0736ae6661db912b8782b4eb08cfd36e

556e5cb5e4e77678110961c8d9260a726a363e00bf8d278e5302cb4bfccc3eed

9f82f22c137688d0b3e7912d415605d2bbc56478311fd0b3dc265f8d0006aa8c

8f3db63f70fad912a3d5994e80ad9a6d1db6c38d119b38bc04890dfba4c4a2b2

bedf30bbcefc54bc48432674255856f47c0ba2ec46e913d078a53e66ac9dcff8

Ca607e431062ee49a21d69d722750e5edbd8ffabcb54fa92b231814101756041

b4f90cff1e3900a3906c3b74f307498760462d719c31d008fc01937f5400fb85

### Lockbit 2.0

F32e9fb8b1ea73f0a71f3edaebb7f2b242e72d2a4826d6b2744ad3d830671202

4de287e0b05e138ab942d71d1d4d2ad5fb7d46a336a446f619091bdace4f2d0a

F3e891a2a39dd948cd85e1c8335a83e640d0987dbd48c16001a02f6b7c1733ae

Ea028ec3efaab9a3ce49379fef714bef0b120661dcbb55fcfab5c4f720598477

Bcdb59232137e570d4afb3c635f8df19ceb03e3f57fe558f4fc69a0be778c6ab

## 原文链接

[unit42](https://unit42.paloaltonetworks.com/emerging-ransomware-groups/)

