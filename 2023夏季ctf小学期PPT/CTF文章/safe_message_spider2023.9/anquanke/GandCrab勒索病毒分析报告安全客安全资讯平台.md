# GandCrab勒索病毒分析报告

阅读量 **339969**

|评论 **4**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-09-17 16:30:02

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t0162f3dab3f4a75c9d.jpg)

## 前言

呼，历时4天半，终于完成了对GandCrab病毒的分析，这个病毒是在52破解ScareCrowL前辈的帖子上参考借鉴而来，漫漫病毒分析之路，任重且道远，还好，我们拥有巨人的肩膀，让我们看的更远更多。

首先讲一下，为什么分析这个病毒，在四叶草公司实习，几天下来，有点厌倦分析病毒这件事了，哇，想到以后还要干好多年，心态炸了。公司峰哥给我了两个样本，说现在流行勒索和挖矿病毒，客户也中过，叫我去试试分析。然后就有了这篇病毒分析报告。顿时，分析出来有不一样的收获，这是传统病毒不一样的。

一月份，GandCrab勒索软件首次亮相，这是一种着名的恶意软件，分布在黑暗网络上，可能源于俄罗斯，主要针对斯堪的纳维亚和英语国家。……（码字太麻烦了，这里有一份关于GandCrab简介，了解一下：[http://baijiahao.baidu.com/s?id=1599794170709869995&wfr=spider&for=pc](http://baijiahao.baidu.com/s?id=1599794170709869995&wfr=spider&for=pc)）

## 二：样本信息

  * 样本名称：hmieuy.exe
  * 样本md5：f42774332fb637650ff0e524ce1b1685
  * 是否加壳：无壳
  * 编译语言：Microsoft Visual C++ v.10 – 2010 ( E8 )
  * 样本来源：[https://www.52pojie.cn/forum.php?mod=viewthread&tid=712552&extra=page%3D1%26filter%3Dtypeid%26typeid%3D62](https://www.52pojie.cn/forum.php?mod=viewthread&tid=712552&extra=page%3D1%26filter%3Dtypeid%26typeid%3D62)

## 三：行为分析

这个样本的主要作用就是从资源段中检索数据，然后把其加载到内存，经过解密，然后调用解密好的shellcode。

shellcode主要是调用LoadLibrary和GetProcAddress。获取所需要函数的地址，以便后期的生成新的病毒文件

重新开辟内存空间，解密新的PE文件，并把它映射入内存，复制文件头和各个区表。

修复IAT，这样就形成了新的病毒文件，命名为PE1.exe

PE1.exe采用dll反射注入技术，利用ReflectiveLoader要完成的任务是对自身的装载(这一切都是在内存中发生)

调用dll文件的入口点

核心程序的行为

  1. 获取系统的DNS网域，本地用户名，键盘区域，CPU架构，CPU信息，磁盘驱动器
  2. 连接病毒服务器
  3. 判断病毒进程在系统中是否互斥，如果存在多个相同病毒进程，终止进程。
  4. 检查杀毒软件驱动，如果没有，则复制自身，修改注册表自启动
  5. 寻找并终止指定的进程，因为这些进程可能会影响到对文件的加密
  6. 利用机器数据生成加密赎金ID
  7. 启用微软加密服务
  8. 对磁盘文件除了必要文件必要路径下进行加密
  9. 检查进程安全令牌
  10. 删除卷影副本，避免管理员利用副本进行恢复。
  11. 执行指定的shell操作。

![](https://i.imgur.com/eC9uxdq.png)

## 四：样本分析

###  原始样本(hmieuy.exe)

通读代码，发现EnumResourceNamesA
API函数，函数目的是枚举指定的二进制资源，我们可以猜测程序功能是，枚举资源文件，然后映射如内存，经过解密，形成shellcode，然后执行shellcode。

![](https://i.imgur.com/PvZwDtY.png)

![](https://i.imgur.com/vezYlfn.png)

修改内存保护设置，映射文件到内存，然后解密shellcode并且执行shellcode。

![](https://i.imgur.com/VA8bmL2.png)

这是第一层保护

###  shellcode(内存中dump而来)

利用PEB，获取Kernel32.dll的基地址。

![](https://i.imgur.com/nbKHSec.png)

获取LoadLibrary和GetProcAddress的地址，以便在函数中调用其他函数。这个是使用shellcode最先做的两件事情。

再次申请空间，加载解密后续的病毒代码，首先加载文件头，然后遍历节区，

![](https://i.imgur.com/l3j6zFP.png)

修改IAT

![](https://i.imgur.com/yfKHcwj.png)

###  PE1.exe（内存中dump而来）

观察tmain函数，发现函数流程就是经过三个验证，最后执行sub_11A8.而这个函数是反射式dll注入的主要的函数。

![](https://i.imgur.com/n7OGNno.png)

调用了函数sub_获取的机器信息和dll导出函数ReflectiveLoader

![](https://i.imgur.com/Ou7Qzm6.png)

修改内存保护设置

![](https://i.imgur.com/KGj9daA.png)

调用函数ReflectiveLoader，反射式dll注入自身[这是病毒保护自我的重点，了解反射式dll注入的流程]

![](https://i.imgur.com/GI8yT8C.png)

1.需要获取被加载到内存dll的基地址，连自己在内存的哪里都不知道，还玩的屁啊

![](https://i.imgur.com/f2qlQfB.png)

2.利用模块和函数的Hash来获取主要函数的地址。

![](https://i.imgur.com/wPYdpd4.png)

3.分配内存区域，存放dll代码(之前应该已经注入好了)

![](https://i.imgur.com/qxZnVxF.png)

4.修复，获取IAT

![](https://i.imgur.com/mtQK1oz.png)

![](https://i.imgur.com/yMfYKjW.png)

5.修复重定位表

![](https://i.imgur.com/BvmmJBq.png)

6.得到OEP，跳转到dll文件的OEP地址。

###  PE2.dll (内存中dump而来)

####  整体分析

病毒发作的前期：

![](https://i.imgur.com/OOQMD70.png)

病毒发作的中期：

病毒发作的晚期：

####  模块1：收集机器信息，链接url读取文件，生成互斥体

调用GetInforAndOpenUrl(10007580)获取系统信息，检测进程中是否存在指定给的杀毒软件，然后连接指定的url读取文件

  * 系统的DNS网域，
  * 本地用户名，
  * 键盘区域，但是病毒并不感染俄罗斯用户

![](https://i.imgur.com/kdfqpjg.png)

  * CPU架构，
  * CPU信息，
  * 磁盘驱动器

![](https://i.imgur.com/68pEhmT.png)

![](https://i.imgur.com/kAADsGT.png)

  * 检测进程中是否存在指定给的杀毒软件

![](https://i.imgur.com/Zk6b7Gd.png)

  * 连接到指定的URL，并且读取文件

  * 打开Http请求，读取网络文件至缓冲区

![](https://i.imgur.com/ehPElVU.png)

  * 以自身的硬件信息，生成ranson-id，并由此创建互斥体。

![](https://i.imgur.com/qZcvZsM.png)

####  模块2：检测杀软驱动

检查是否有卡巴斯基和诺顿等杀软的驱动，先检查是否存在卡巴斯基的驱动，如果存在，XXX，如果不存在，在检查其他杀软的驱动，如果都不存在，那就将自身复制，同时写入注册表自启动项。

![](https://i.imgur.com/zxUWYA9.png)

将病毒释放到系统目录下。

![](https://i.imgur.com/GEft18W.png)

![](https://i.imgur.com/0jkOjsc.png)

将释放的文件写入注册表Runonce中，以实现病毒的自启。

![](https://i.imgur.com/d2J5sx1.png)

![](https://i.imgur.com/RrkcJrA.png)

####  模块3：关闭相关进程

由于在进程文件加密的时候，不允许进程占用，所以需要终止某些特定的进程。

![](https://i.imgur.com/e2s1k5a.png)

![](https://i.imgur.com/FIvNDBH.png)

####  模块4：利用机器数据生成RansomID

产生了支付赎金的赎金ID，这个是由的pc_group和机器识别码生成的，

![](https://i.imgur.com/Z6mfW5R.png)

![](https://i.imgur.com/KBg0LHc.png)

同时为了受害者方便交付赎金，提供了安装洋葱浏览器的教程，卧槽真的贴心。

![](https://i.imgur.com/5XAHwt6.png)

####  模块5：启用微软的CSP加密服务

利用CryptAcquireContextW创建CSP密码容器句柄

利用 CryptGenKey产生随机秘钥

生成密钥有两种方式，CryptGenKey（生成随机密钥）和CryptImportKey（导入密钥），病毒使用了CryptGenKey方式。另：Microsoft
Base Cryptographic Provider v1.0：密钥长度为512位。Microsoft Enhanced Cryptographic
Provider v1.0：密钥长度为1024位

加密

销毁容器

![](https://i.imgur.com/DsGbt7D.png)

####  模块6：发送Base加密后的公秘钥

产生特征的编码字符

![](https://i.imgur.com/dHAI6aq.png)

![](https://i.imgur.com/wBqkB1a.png)

将RSA生成的秘钥和公钥利用CryptBinaryToStringA函数Base64加密，以便后期网路传输。

![](https://i.imgur.com/r3cUppG.png)

![](https://i.imgur.com/EnkzDN8.png)

检索系统信息，然后再进行Base64编码。

![](https://i.imgur.com/QQH8O1N.png)

将获取的机器信息的Base64编码连接到秘钥的后面

![](https://i.imgur.com/QkwfWEK.png)

读取之前释放到Hacky目录下的病毒，可以是利用后续的函数进行父子进程共享该段数据。

![](https://i.imgur.com/yVfAJo8.png)

建立管道通信，解析域名，判断网络连接是否正常

![](https://i.imgur.com/RqupYhR.png)

####  模块7：建立管道通信

首先将三个域名传入。

  * malwarehunterteam.bit
  * politiaromana.bit
  * gdcb.bit

![](https://i.imgur.com/ItxAF0B.png)

创建管道连接，管道的作用是实现进程之间的消息交互

![](https://i.imgur.com/RtZbJku.png)

利用管道的通信机制，创建一个子进程，命令行参数是nslookup %s
ns1.virmach.ru,目的是解析之前穿入的三个域名。读取文件，判断是否联网，如果没有联网，readfile的buf存在error信息，程序进程死循环

![](https://i.imgur.com/J9VA1ME.png)

![](https://i.imgur.com/L5Iyfk2.png)

![](https://i.imgur.com/0fVO0Ez.png)

管道输入的一般新步骤：

![](https://i.imgur.com/WULxnv0.png)

修补可执行文件，我们将一些关键A24FF4等跳转jmp或者nop掉即可实现。

####  模块8：文件加密部分

病毒首先需要获取机器的磁盘驱动器。除了CD-ROM其他的驱动器都被感染，对于搜索到的每个驱动器，释放一个线程，进行加密。加快加密的速度。

![](https://i.imgur.com/wb6XSnA.png)

病毒不会感染特殊目录和特殊格式的文件

![](https://i.imgur.com/FIIqbOy.png)

![](https://i.imgur.com/nZOfPMo.png)

然后在驱动器中遍历，如果是文档则递归调用原函数，负责调用加密函数。

![](https://i.imgur.com/cjUyEjo.png)

![](https://i.imgur.com/6AUZn7Q.png)

管道通信

####  模块9：安全令牌检测

检测进程的安全令牌

![](https://i.imgur.com/t070Q5s.png)

####  模块10：删除卷影副本

利用shellExecute函数执行cmd，参数是/c vssadmin delete shadows /all
/quiet，删除卷影副本，目的是不让管理员恢复数据。

![](https://i.imgur.com/ZJpP1Fo.png)

![](https://i.imgur.com/BT6ynew.png)

## 五：技术总结

GandCrab病毒主要采用到的技术有，shellcode藏匿，利用shellcode的短小的特点，触发shellcode到内存，减少了被杀毒软件查杀的风险。经过第一层加密后，病毒释放了一个恶意代码文件(PE1.exe)，该文件采用的是反射式dll注入技术，该技术不想传统的dll注入需要在文件系统中产生文件，所要执行的dll全在内存中，这是第二层保护手段。经过两次dump后，可以得到本次病毒的主体文件，建立了管道，实现子进程和父进程之间的通信。

###  shellcode

需要细细的看，参考自：<https://zhuanlan.zhihu.com/p/28788521>

###  反射式dll注入

传统的dll注入，是在文件系统中存放一个dll模块，然后进程利用LoadLibrary和CreateRemoteThread这两个API函数装载模块到内存空间，实现注入。而杀软在布置Hook的时候，重点钩取的就是这两种API函数。

反射式dll注入不需要dll文件落地，减少被查杀的风险。首先将需要注入的dll写入进程内存，然后为该dll添加一个导出函数，利用这个导出函数让其自动的装载dll。

主要有两个方向的问题：第一个如何将dll写入内存(注射器的实现),第二个如果调用自身(ReflectiveLoader的实现)

参考自：<http://www.freebuf.com/articles/system/151161.html>

####  注射器的实现

  * 1.将待注入DLL读入自身内存(利用解密磁盘上加密的文件、网络传输等方式避免文件落地)
  * 2.利用VirtualAlloc和WriteProcessMemory在目标进程中写入待注入的DLL文件
  * 3.利用CreateRemoteThread等函数启动位于目标进程中的ReflectiveLoader

####  ReflectiveLoader的实现

  * 1.定位DLL文件在内存中的基址
  * 2.获取所需的系统API
  * 3.分配一片用来装载DLL的空间
  * 4.复制PE文件头和各个节
  * 5.处理DLL的引入表,修复重定位表
  * 6.调用DLL入口点

###  管道通信

管道是一种用于在进程间共享数据的机制，其实质是一段共享内存，病毒利用了管道进行父子进程的通信，这样子进程就可以直接影响父进程内存。为实现父子进程间通信，需要对子进程的管道进行重定向：创建子进程函数
CreateProcess中有一个参数STARUIINFO，默认情况下子进程的输入输出管道是标准输入输出流，可以通过下面的方法实现管道重定向：

    
    
    STARTUPINFO si;
    si.hStdInput   = hPipeInputRead;   //输入由标准输入 -> 从管道中读取
    si.hStdOutput  = hPipeOutputWrite; //输出由标准输出 -> 输出到管道
    

摘录自[https://www.52pojie.cn/forum.php?mod=viewthread&tid=712552&extra=page%3D1%26filter%3Dtypeid%26typeid%3D62](https://www.52pojie.cn/forum.php?mod=viewthread&tid=712552&extra=page%3D1%26filter%3Dtypeid%26typeid%3D62)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **HaCky** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/159912](/post/id/159912)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [恶意软件](/tag/恶意软件)
  * [勒索软件](/tag/勒索软件)
  * [GandCrab](/tag/GandCrab)

 **+1** __15赞

 __收藏

![](https://p1.ssl.qhimg.com/t01487b5bd2c28db179.jpg) HaCky

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

