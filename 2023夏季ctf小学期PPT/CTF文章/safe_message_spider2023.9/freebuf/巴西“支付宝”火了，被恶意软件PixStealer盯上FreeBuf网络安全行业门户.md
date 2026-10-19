9月末， **研究人员在谷歌应用商店发现了一系列针对Pix支付系统和巴西银行的恶意软件**
，其中一个版本可以直接窃取目标钱包，研究人员将其命名为PixStealer。

新冠加速了银行业数字化进程，在此期间最成功的例子之一是Pix，一项巴西中央银行创建的即时支付解决方案。

Pix于2020年11月发布，现在每天的交易量已达到4000万笔，每周交易总额达到了47亿美元，但同时，黑客也盯上了Pix支付。

## PixStealer技术分析

PixStealer恶意软件的内部名称是Pag Cashback 1.4。该软件在谷歌应用商店上伪装成PagBank
Cashback进行传播。包名为com.pagcashback.beta，表示应用程序可能仍处于测试阶段。

PixStealer非常小，只具有最低权限，没有与C&C连接，它只有一个功能：将受害者的所有资金转移到攻击者控制的帐户。因此，恶意软件无法通过C&C更新，也无法窃取和上传受害者信息，但却可以保持不被发现。

![1635473932_617b5a0caa74c1d00e24d.png!small?1635473931916](https://image.3001.net/images/20211029/1635473932_617b5a0caa74c1d00e24d.png!small?1635473931916)

PixStealer同样适用安卓的可访问性服务。AAS的主要目的是帮助残疾用户更方便地适用安卓设备和应用。当恶意软件诱使目标启用该服务时，应用程序能够读取用户的任何可读取内容，并执行用户可执行的任何操作。

恶意软件会向受害者发送消息，要求激活可访问性服务，获取所谓的“现金返还”功能，该服务名为com.gservice.autobot.Acessibilidade，如下图：

![1635473950_617b5a1e81dc5c684e0a6.png!small?1635473949776](https://image.3001.net/images/20211029/1635473950_617b5a1e81dc5c684e0a6.png!small?1635473949776)

授权可访问性服务后，恶意软件显示信息的同时调用并打开PagBank进行同步。受害者打开银行帐户并输入凭据后，恶意软件会通过访问权限单击“显示”（下图眼睛图标）按钮来查询受害者的当前余额。

![1635473981_617b5a3db705dbc35c928.png!small?1635473980991](https://image.3001.net/images/20211029/1635473981_617b5a3db705dbc35c928.png!small?1635473980991)

查询结果保存在valor中：

![1635474003_617b5a536ef57f1855f35.png!small?1635474003372](https://image.3001.net/images/20211029/1635474003_617b5a536ef57f1855f35.png!small?1635474003372)

随后恶意软件会显示假的覆盖图，要求用户等待同步完成：

![1635474009_617b5a5914cc6be3bb5ca.png!small?1635474008359](https://image.3001.net/images/20211029/1635474009_617b5a5914cc6be3bb5ca.png!small?1635474008359)

覆盖屏幕起着非常重要的作用：在此期间恶意软件在后台将所有资金转移到黑客控制的帐户。  
PagBank需要在用户执行Pix支付前进行身份验证，确保该设备属于银行账户的所有者，并要求用户执行以下验证：

> 双因素身份验证（凭据和SMS）  
> 上传身份确认文件  
> 使用摄像头拍摄用户。  
> 但PixStealer是在通过身份验证阶段才开始运行，绕过了所有检查。

## 同家族恶意软件MalRhino

不与C&C通信的独立恶意软件是很难被检测到，在研究过程中发现一个与PixStealer具有高度同源性的恶意软件：MalRhino，与前者具有相似的mainfest、日志信息、服务和方法名。

![1635474035_617b5a73260341223d531.png!small?1635474034571](https://image.3001.net/images/20211029/1635474035_617b5a73260341223d531.png!small?1635474034571)

PixStealer中的日志信息

![1635474050_617b5a8299bb83086df15.png!small?1635474049895](https://image.3001.net/images/20211029/1635474050_617b5a8299bb83086df15.png!small?1635474049895)

MalRhino 中的日志信息

该恶意软件假冒巴西国际银行，使用Rhino框架，软件包名为com.gnservice.beta，也通过谷歌应用商店传播，运行前同样需要用户授予权限。

![1635474076_617b5a9c95ba9f29c7f39.png!small?1635474075856](https://image.3001.net/images/20211029/1635474076_617b5a9c95ba9f29c7f39.png!small?1635474075856)

## IOCs

PixStealer：  
28e8170485bbee78e1a54aae6a955e64fe299978cbb908da60e8663c794fd195
com.pagcashback.beta  
c0585b792c0a9b8ef99b2b31edb28c5dac23f0c9eb47a0b800de848a9ab4b06c
com.pagback.beta  
8b4f064895f8fac9a5f25a900ff964828e481d5df2a2c2e08e17231138e3e902
com.gnservice.beta

MalRhino：  
2990f396c120b33c492d02e771c9f1968239147acec13afc9f500acae271aa11
com.gnservice.beta

## 原文链接

[checkpoint﻿](https://research.checkpoint.com/2021/pixstealer-a-new-wave-of-android-banking-trojans-abusing-accessibility-services/)

