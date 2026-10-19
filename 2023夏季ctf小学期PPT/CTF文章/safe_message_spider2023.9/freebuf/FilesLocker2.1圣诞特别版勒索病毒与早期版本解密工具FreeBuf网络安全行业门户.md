## 前言

**近日，深信服EDR安全团队跟踪到多个客户感染了FilesLocker勒索病毒，其中最新版本的已更新到了FilesLocker2.1，这是一个专门为了庆祝圣诞节而设计命名的版本，中招客户除了系统被加密破坏之外，还有来自勒索作者的节日问候。**

FilesLocker是一款代理型勒索软件，勒索病毒制造者只负责制作勒索病毒本身，传播方式通过招中间代理的方式来实现，故传播方式多种多样。其中，最新版本的FilesLocker2.1版本最后会在桌面生成中英文的勒索信息提示文件，并弹出勒索窗口。并且还会从<https://i.loli.net/2018/12/31/5c29eac523516.bmp>
下载一张图片设置为桌面壁纸，画面颇为欢乐喜庆。

![](https://image.3001.net/images/20190103/1546513949_5c2dee1de4f3b.png!small)

FilesLocker2.1版本的勒索界面（圣诞版）

根据可靠消息，该加密作者释放的RSA私钥在加密完之后会在浏览器弹出（适用于FilesLocker1.0和FilesLocker2.0中招客户，FilesLocker2.1圣诞特别版暂时没有释放密钥，也就是说圣诞版暂时无法解密，提醒广大用户小心）。

![](https://image.3001.net/images/20190103/1546513960_5c2dee285bc63.png!small)

该工具已将该RSA私钥集成进入工具，然后用该私钥将用户被加密的AES密钥解密出来。

![](https://image.3001.net/images/20190103/1546513968_5c2dee308f36d.png!small)

![](https://image.3001.net/images/20190103/1546513968_5c2dee309ce1c.png!small)

解密文件：

![](https://image.3001.net/images/20190103/1546513975_5c2dee377746a.png!small)

该工具提供的所有函数：

![](https://image.3001.net/images/20190103/1546513983_5c2dee3f5150a.png!small)

## 一、背景介绍

2018年10月，有人在暗网发布FilesLocker勒索病毒合作计划。事后有国内多家安全厂商跟进报道，随即此贴访问量暴涨十倍，并且作者之后在帖子上更新了报道链接。

![](https://image.3001.net/images/20190103/1546513991_5c2dee4798759.png!small)

2018年底最后一天，作者放出了1.0和2.0版本的私钥，目前国外也有安全人员根据私钥开发出了解密工具。但这并不是作者偃旗息鼓了，最新的2.1版本已经到来，且更换了新的RSA秘钥对。

## 二、样本分析

### 2.1 版本

由于作者已经将之前的私钥放出，在2.1版本中，便更新了公钥，如图所示。

![](https://image.3001.net/images/20190103/1546514003_5c2dee531e6c1.png!small)

随机生成加密文件的AES密钥，使用RSA加密，最后再把密文用base64编码：

![](https://image.3001.net/images/20190103/1546514011_5c2dee5b62991.png!small)

加密AES秘钥，并用base64编码密文

样本只加密系统盘中指定文件夹和非系统盘中指定文件名后缀名的文件。

![](https://image.3001.net/images/20190103/1546514028_5c2dee6c0aead.png!small)

系统盘指定文件夹

![](https://image.3001.net/images/20190103/1546514041_5c2dee795b28c.png!small)

加密除了系统盘之外的其他磁盘

![](https://image.3001.net/images/20190103/1546514051_5c2dee83b790c.png!small)

指定加密的文件后缀名，共367种

加密文件使用了AES算法，ECB模式：

![](https://image.3001.net/images/20190103/1546514062_5c2dee8e03084.png!small)

加密文件代码

加密完成后会在文件名后面添加后缀.[fileslocker@pm.me]。

![](https://image.3001.net/images/20190103/1546514072_5c2dee983cde1.png!small)

添加文件名后缀

整个加密阶段完成以后，会调用vssadmin.exe删除掉系统卷影副本

![](https://image.3001.net/images/20190103/1546514086_5c2deea6c21bc.png!small)

删除卷影副本

### 2.0 版本

2018年11月底，FilesLocker升级到了2.0版本，主体功能没有变化。加密的文件后缀比1.0版本增加了10个。加密以后会从指定链接下载图片并设置为桌面壁纸。

![](https://image.3001.net/images/20190103/1546514332_5c2def9c9675d.png!small)

并对勒索弹窗也做了些改变。

![](https://image.3001.net/images/20190103/1546514344_5c2defa870b5d.png!small)

### 1.0 版本

2018年10月，作者在暗网发布了合作计划，样本开始出现。1.0版本病毒名字伪装成Windows Update，用以迷惑用户。

![](https://image.3001.net/images/20190103/1546514355_5c2defb395f59.png!small)

原始文件名字

1.0版本加密的文件后缀有357种：

![](https://image.3001.net/images/20190103/1546514375_5c2defc70ccef.png!small)

指定加密的文件后缀名，共357种

1.0会在桌面生成中英文的勒索信息提示文件，并弹出勒索窗口。

![](https://image.3001.net/images/20190103/1546514386_5c2defd2d52e9.png!small)

1.0版本的勒索界面

## 三、解决方案

针对FilesLocker1.0和2.0的勒索解密工具（FilesLocker2.1圣诞特别版暂时没有解密工具）：[http://edr.sangfor.com.cn/tool/FilesLockerDecrypter.zip](http://edr.sangfor.com.cn/FilesLockerDecrypter.zip)

### (1) 选择被加密的文件夹

![](https://image.3001.net/images/20190103/1546514397_5c2defdd67075.png!small)

### (2) 选择自己的ID文件（桌面上生成的加密信，中英文的都可以）

![](https://image.3001.net/images/20190103/1546514406_5c2defe67386a.png!small)

### (3) 点击Decrypt开始解密

![](https://image.3001.net/images/20190103/1546514415_5c2defef9079f.png!small)

病毒检测查杀：

1\.
深信服为广大用户免费提供查杀工具，可下载如下工具，进行检测查杀。<http://edr.sangfor.com.cn/tool/SfabAntiBot.zip>

 ***本文作者：千里目安全实验室，转载请注明来自FreeBuf.COM**

