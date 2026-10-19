## 背景

继七月份监测到某犯罪团伙利用混淆AutoIt脚本加载Globeimposter勒索病毒之后([Globeimposter勒索病毒新变种分析](https://www.freebuf.com/articles/network/280195.html))。阿里云安全近期又监测到两个攻击手法类似，但攻击载荷不同的恶意样本，样本A的攻击载荷为Remcos远控木马，
样本B的攻击载荷疑似CryptoBot窃密木马。初步判定属于同一犯罪团伙， 判定依据主要来源以下三个方面：

  * 所规避的用户名相同。 当计算机的用户名为DESKTOP-QO5QU33、NfZtFbPfH、tz和ELICZ时， 脚本会自动退出。
  * ![](https://image.3001.net/images/20210903/1630654765_6131d12d64806023d6f4f.png!small)AutoIt脚本所使用的混淆方法相同。

攻击者都对样本的编译时间进行了修改来对抗分析。![](https://image.3001.net/images/20210903/1630654907_6131d1bb6fb2888c6bccf.png!small)

## 远控载荷的样本

该样本是一个7z sfx压缩文件， 运行过程中释放四个文件， 包括: Gia.xla、Qui.xla、Sconvolge.xla 和
Bellissima.xla。

· Gia.xla 是一个修改之后的带签名的AutoIt程序  
· Qui.xla 是混淆之后的AutoIt脚本， 用于解密攻击载荷并将其注入到AutoIt.exe进程中。  
· Sconvolge.xla 是一个Bat脚本， 用于生成Auto.exe程序， 并执行AutoIt脚本。  
· Bellissima.xla是加密之后的远控木马Remcos。

对上述四个文件进行分析，
判定该样本的攻击流程与[Globeimposter勒索病毒新变种分析](https://www.freebuf.com/articles/network/280195.html)一文相同。但部分细节略有不同，
如下：

· 解密密钥。 样本A在对载荷解密时所使用的密钥为1233。  
· 傀儡进程。 本次注入的进程对象是AutoIt.exe。  
· 攻击载荷。 样本A使用的载荷为Remcos 3.13 Pro远控木马。 Remcos木马于2016年开始在黑客论坛· ·
公开售卖，至今已经经历81个版本的改进， 最新版本为3.2.0。

## 窃密载荷的样本

同远控载荷样本的执行流程相同， 释放的四个文件分别为:Accendeva.pub、Dianzi.pub、Inebriato.pub和Osi.pub。

· Dianzi.pub功能同上Gia.xla  
· Osi.pub功能同上Qui.xla， 但注入手法略有不同。  
· Accendeva.pub功能同上Sconvolge.xla。  
· Inebriato.pub为加密之后的窃密木马CryptBot。

## Osi.pub文件分析

对该文件去混淆之后， 发现使用的解密密钥为458348364， 且注入手法与之前略有不同。 本次使用注入手法如下：

· 解密CryptBot攻击载荷。  
· 调用LoadLibraryExA函数加载Explore。exe文件， 随后调用NtUnmapViewOfSection解除相关内存映射。  
· 为了规避相关检测， 将解密之后的载荷映射到Explorer。exe在进程中地址。  
· 执行CryptBot窃密木马。

流程图:

![](https://image.3001.net/images/20210903/1630655722_6131d4ea9f5e3513b65f4.png!small)

![](https://image.3001.net/images/20210903/1630656050_6131d632739c45fd0bc41.png!small)

![](https://image.3001.net/images/20210903/1630656064_6131d6402599fd7343497.png!small)

![](https://image.3001.net/images/20210903/1630656257_6131d701a25cb725a415d.png!small)

## 窃密木马CryptBot分析

本次捕获的CryptBot木马主要窃取以下四类信息:

· 浏览器存储的用户名和密码、Cookie和信用卡凭证。  
· 数字货币钱包的应用程序信息。  
· 截图。  
· 用户计算机的信息。

将以上四类信息分门别类放入特定的文件夹中，打包成ZIP文件发送至远端。

### 1\. 检测相关杀软

检测AVAST和AVG杀毒软件是否存在，若存在则sleep随机时间进行对抗。

![](https://image.3001.net/images/20210903/1630656447_6131d7bfedf26d089d9fa.png!small)

### 2\. 创建文件夹

在%tmp%创建如下文件夹结构， 其中files和Files搜集的信息是相同的。

    
    
    GKg147x             // 随机字符串
    │──files_           // 存储cookie
    │  ├─cookies        // 各个浏览器的Cookie
    │  ├─cryptocurrency // 各中加密货币的私钥
    │  └─files // 空
    └─_Files
        ├─_Cookies
        ├─_Files
        └─_Wallet

### 3\. 窃取浏览器信息

主要收集的浏览器包括: Chrome浏览器、Brave浏览器、Opera浏览器和Firefox浏览器， 下面以Chrome浏览器为例进行讲解。
拷贝Chrome浏览器下存储用户信息的文件Login Data、Cookie和WebData至GKg147x下， 并以随机字符串重命名。

 **窃取密码**

创建文件\files_AllPasswords_list.txt和_Files\passwords.txt用于存放收集所有浏览器账号和密码，并创建\files_AllForms_list.txt和_Files\forms.txt存放所有浏览器自动填充字段。

![](https://image.3001.net/images/20210903/1630656602_6131d85a45af4f6e76240.png!small)

 **窃取Cookie**

创建文件\files__AllCookies_list.txt和_Files\cookies.txt用于存放收集所有浏览器Cookie。

![](https://image.3001.net/images/20210903/1630656883_6131d9730230b35bbb0df.png!small)

 **窃取信用卡凭证**

创建文件\files__All_CC_list.txt和_Files\cc.txt用于存放搜集的所有信用卡凭证。

![](https://image.3001.net/images/20210903/1630656926_6131d99ecca1c418ff8ca.png!small)

### 4.窃取加密货币

窃取数字货币钱包的应用程序信息， 如下图所示:

![](https://image.3001.net/images/20210903/1630656993_6131d9e159dde4a4d6c61.png!small)

### 5.窃取屏幕截屏

截取当前屏幕内容保存至\files__Screen_Desktop。jpeg

![](https://image.3001.net/images/20210903/1630657039_6131da0f0e9edb6b54ab5.png!small)

### 6.窃取用户计算机信息

将收集计算机信息保存至\files__Information。txt， 包括: 操作系统版本、用户名、CPU信息和已安装的软件等。

![](https://image.3001.net/images/20210903/1630657075_6131da3330935b12baab2.png!small)

### 7.上传文件

压缩_Files和\files_文件夹为ZIP文件， 通过http协议向URL1和URL2以POST方式上传两文件。

    
    
    URL 1:  http://www.ewaisb31.top/index.php
    URL 2:  http://www.morxeg03.top/index.php

## Iocs

### 文件MD5

    
    
    远控样本:a85dcd5e018b1a955980886fc9d4aed3
    Gia.xla:9a6f19828f9cbff4df6018fb8d8d7f04
    Qui.xla:c1370e348301340498d0a4f60a91db38
    Sconvolge.xla:8246de2fdf44e4df5b902b1a8f94e9e0
    Bellissima.xla:b27a96ab2d0cd9702328aa217e0eaa1b
    Remcos:7edb66afc8f728cc76593e16a353ad9b
    
    窃密样本:c2bc3bef415ae0ed2e89cb864fff2bfc
    Dianzi.pub:2eba0ba5ce4e6a1853ce1c304da98aee
    Accendeva.pub:1317cba2fd4a74ae8d694e0bca385e9b
    Inebriato.pub:60aa93132ca559097cbd55d0450e7239
    Osi.pub:86e4615ed5d78184c933adcc9c5024d4
    CryptBot:8f9228d278741de4346220ca3cba18e2

### IP和域名

    
    
    // Remcos控制端
    176.111.174.14:12441
        
    // 窃密相关URL
    http://ewaisb31.top --> 接收文件
    http://morxeg03.top --> 接收文件
    http://winxob04.top/download.php?file=lv.exe

## 专家建议

阿里云安全中心建议云上客户做好以下三点，进一步降低被恶意攻击的机会：

> 定期修复系统漏洞，避免被黑客利用。
>
> 不使用弱密码，对重要的系统开启双因子认证。
>
> 使用安全组，限制IP段访问，避免不必要的网络端口暴露在互联网，减小攻击面。
>
> 关闭或者修改一些常用端口：445、135、139等等。对内网的安全域进行合理的划分，域之间做好各种ACL的限制。

开启 **阿里云安全中心** -> **恶意行为防御**
功能。![](https://image.3001.net/images/20210903/1630657409_6131db81a47d9d1885b3d.png!small)

  

