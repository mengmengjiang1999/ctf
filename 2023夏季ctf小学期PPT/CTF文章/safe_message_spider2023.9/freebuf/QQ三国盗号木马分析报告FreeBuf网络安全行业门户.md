*****本文原创作者：RNGorgeous，本文属FreeBuf原创奖励计划，未经许可禁止转载**  
**

##  **一.背景介绍**  

**近年来网络游戏越来越火，人们充值大量金钱玩一个心爱的游戏已成常态，所以有些游戏账号非常值钱，特别是QQ三国这种每次更新都要氪金的游戏，虽然只剩下部分老玩家在玩，但他们中的大部分账号都有许多值钱的装备和物资。使得某些不法分子将目光放在了这些游戏账号上面，他们编写盗号木马，通过各种手段让玩家运行，窃取到账号后会盗取装备和物资，以换取金钱。**

##  **二.概述**

该木马运行后会在QQSG.exe所在目录释放Tsg1.dll(盗号模块)，并修改三个dll的入口地址，使得QQSG.exe运行时加载这三个dll的其中一个后也会加载Tsg1.dll。该盗号模块加载时会创建一个线程，负责将本地的网卡、系统版本等信息提交到编写者的服务器。然后修改QQSG.exe的关键地址，以截取账号密码等信息，发送到编写者的服务器。

![1.jpg](https://image.3001.net/images/20180729/1532835075_5b5d35038eee4.jpg!small)

图-盗号流程

##  **三.详细分析**

### 1.母体木马qqsg501.exe

MD5:10BFAF8079777878CFB155B87651DE5A

 **1.1 进程提权**

![2.png](https://image.3001.net/images/20180729/1532835106_5b5d35227c150.png!small)

图-进程提权

 **1.2 寻找QQSG.exe**

创建进程快照，寻找QQSG.exe，找不到则查询注册表项，还找不到就遍历硬盘寻找。

![3.png](https://image.3001.net/images/20180729/1532835118_5b5d352e5b05f.png!small)

图-在进程和注册表中寻找QQSG.exe

![4.png](https://image.3001.net/images/20180729/1532835146_5b5d354a0f2c6.png!small)

图-遍历硬盘寻找QQSG.exe

 **1.3 关闭QQSG.exe**

关闭后，玩家只能重新登录，然后被后面注入的模块盗取账号。

![5.png](https://image.3001.net/images/20180729/1532835210_5b5d358aa291e.png!small)

图-关闭QQSG.exe

 **1.4 释放盗号模块Tsg1.dll**

![6.png](https://image.3001.net/images/20180729/1532835227_5b5d359b83420.png!small)

图-释放Tsg1.dll

 **1.5 修改三个dll**

修改三个dll（dsound.dll、Zlib1.dll、DisplayD3D8_Dll.dll）的DLLMain入口地址，使其被加载时顺便加载盗号模块Tsg1.dll，加载完会自我修复。

![7.png](https://image.3001.net/images/20180729/1532835240_5b5d35a8db6f1.png!small)

图-修改dll

**1.6 自我删除**

做完dll注入的工作后，会自我删除。

![8.png](https://image.3001.net/images/20180729/1532835328_5b5d3600e40cd.png!small)

图-自我删除

### 2.盗号模块Tsg1.dll

MD5:065AB6C5416DC2168B83FD178A68895

 **2.1 检测加载该dll的进程**

![9.png](https://image.3001.net/images/20180729/1532835349_5b5d3615a8431.png!small)

图-检测进程

 **2.2 发送本机信息**

创建一个线程获取本机的网卡、系统等信息，然后发送到[HTtp://cda3.dnsdate.com:6299](http://cda3.dnsdate.com:6299/)，并会请求文件，写入临时文件夹，因为域名已无法访问，该行为无法明确。

![10.png](https://image.3001.net/images/20180729/1532835375_5b5d362f054ad.png!small)

图-发送请求

![11.png](https://image.3001.net/images/20180729/1532835440_5b5d367074a83.png!small)

图-发送内容

 **2.3 HOOK QQSG.exe关键指令**

从QQSG.exe代码起始地址开始寻找匹配、修改某些位置的代码，因为QQSG.exe加了PELock壳保护，只能结合其余5个未被该dll调用却会发送数据或截屏给编写者服务器的函数（sub_10004C04、sub_10004C97、sub_10004C48、sub_10004D44、sub_10004D70），猜测这段代码是HOOK了5个关键位置代码，分别跳转到这5个函数，并向编写者服务器发送各种账号信息。

![12.png](https://image.3001.net/images/20180729/1532835473_5b5d369190ca9.png!small)

![13.png](https://image.3001.net/images/20180729/1532835491_5b5d36a3a736e.png!small)

图-修改代码

 **2.4 发送账号信息**

sub_10004C04会检查通过HOOK传递过来的参数是何种账号信息，并决定将其发送到编写者服务器的哪个地址，地址由函数sub_100043DB解密得到。

有三个接收地址：

<http://222.186.55.213:8107/gk/lin.asp>

<http://222.186.55.213:8107/gk/mb.asp>

<http://222.186.55.213:8107/gk/pic.asp>

![14.png](https://image.3001.net/images/20180729/1532835522_5b5d36c213022.png!small)

图-检查传递过来的参数

![15.png](https://image.3001.net/images/20180729/1532835548_5b5d36dc83269.png!small)

图-发送账号信息

 **2.5 发送截图**

sub_10004D70通过HOOK得到执行机会后会创建线程，进行截屏并且发送图片到编写者的服务器，可能是想得到密保卡。

![16.png](https://image.3001.net/images/20180729/1532835587_5b5d3703bf1b7.png!small)

图-截屏

![17.png](https://image.3001.net/images/20180729/1532835606_5b5d37169d328.png!small)

图-发送图片

##  **四．总结**

该木马运用了在资源表隐藏文件、DLL入口劫持和优先加载当前目录下dll方式实现DLL注入、HOOK游戏关键指令获取账号密码、截屏、发送请求等技术来实现盗号的功能，全程十分隐蔽。

 ***本文原创作者：RNGorgeous，本文属FreeBuf原创奖励计划，未经许可禁止转载**

