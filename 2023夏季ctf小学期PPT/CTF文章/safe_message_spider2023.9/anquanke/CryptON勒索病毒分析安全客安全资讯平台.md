# CryptON勒索病毒分析

阅读量 **171064**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-08-17 10:30:39

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t012a955129b114c670.png)

## 0x00 前言

前些天刚刚学完常见对称加密算法原理，故找来一勒索病毒练手。其中如有不当之处，望读者指正，笔者感激不尽。

## 0x01 样本分析

病毒使用到所有函数名称均加密存储，用以抵抗静态分析，其加密方式使用的是替换式密码，具体替换规则如下图所示：

![](https://s1.ax1x.com/2020/07/16/Ur1Y1f.png)

知道替换规则之后，通过一脚本将病毒使用到的函数名称解密如下：

![](https://s1.ax1x.com/2020/07/16/Ur18ht.png)

![](https://s1.ax1x.com/2020/07/16/Ur1tc8.png)

![](https://s1.ax1x.com/2020/07/16/Ur1J9P.png)

![](https://s1.ax1x.com/2020/07/16/Ur13tI.png)

![](https://s1.ax1x.com/2020/07/16/Ur1ang.png)

![](https://s1.ax1x.com/2020/07/16/Ur1BAs.png)

![](https://s1.ax1x.com/2020/07/16/Ur1w7j.png)

![](https://s1.ax1x.com/2020/07/16/Ur1NjS.png)

![](https://s1.ax1x.com/2020/07/16/Ur1dBQ.png)

![](https://s1.ax1x.com/2020/07/16/Ur1DNn.png)

若某一函数地址获取失败，则直接调用`ExitProcess`退出当前进程：

![](https://s1.ax1x.com/2020/07/16/Ur1rhq.png)

* * *

判断Country Code是否为以下四个国家：

![](https://s1.ax1x.com/2020/07/16/Ur163V.png)

具体对应如下：

![](https://s1.ax1x.com/2020/07/16/Ur1y90.png)

如果是这四个国家之一，同样是直接调用`ExitProcess`退出当前进程。

* * *

接下来将内存区域中如下字符串以`0x00`分割，并逐一复制到分配的堆块中：

![](https://s1.ax1x.com/2020/07/16/Ur1ccT.png)

其流程如下所示(部分函数没有截图)：

![](https://s1.ax1x.com/2020/07/16/Ur1fHJ.png)

* * *

判断主机是否接入互联网：

![](https://s1.ax1x.com/2020/07/16/Ur1gjU.png)

检查当前用户是否是管理员组的成员：

![](https://s1.ax1x.com/2020/07/16/Ur1RuF.png)

通过`vssadmin`删除卷影副本：

![](https://s1.ax1x.com/2020/07/16/Ur1WB4.png)

在调用`ShellExecuteEx()`之前由下列函数为其设置`SHELLEXECUTEINFO`结构中字段的值：

![](https://s1.ax1x.com/2020/07/16/Ur14E9.png)

之后通过`bcdedit`禁用自动修复：

![](https://s1.ax1x.com/2020/07/16/Ur15NR.png)

![](https://s1.ax1x.com/2020/07/16/Ur1I41.png)

* * *

将之前复制的字符串(如下所示)以`;`分割：

![](https://s1.ax1x.com/2020/07/16/Ur1T9x.png)

![](https://s1.ax1x.com/2020/07/16/Ur1736.png)

创建名为`LozhYNgbDQij5tYp`的互斥对象：

![](https://s1.ax1x.com/2020/07/16/Ur1HgK.png)

创建0x32个线程(加密线程，此处先不作展开，详见下文)：

![](https://s1.ax1x.com/2020/07/16/Ur1bjO.png)

之后创建加密准备线程：

![](https://s1.ax1x.com/2020/07/16/Ur1LuD.png)

首先获取主机名、用户名及临时目录路径：

![](https://s1.ax1x.com/2020/07/16/Ur1ODe.png)

获取卷信息：

![](https://s1.ax1x.com/2020/07/16/Ur1vEd.png)

将0xD6FDFBEF转换为十进制(3,606,969,327)，用于后续生成用户标识：

![](https://s1.ax1x.com/2020/07/16/Ur1XHH.png)

通过CRC32算法计算出用户标识：

![](https://s1.ax1x.com/2020/07/16/UrcdzT.png)

其后开始生成密钥：

![](https://s1.ax1x.com/2020/07/16/UrsxOJ.png)

共生成4组密钥，其大小如下所示：

![](https://s1.ax1x.com/2020/07/16/Ursvy4.png)

于临时目录下创建一名为用户标识的文件：

![](https://s1.ax1x.com/2020/07/16/UryU7n.png)

根据用户标识生成加密文件扩展名：

![](https://s1.ax1x.com/2020/07/16/UrcaWV.png)

获取操作系统位数、版本：

![](https://s1.ax1x.com/2020/07/16/Ury9T1.png)

将如下内容拼接在一起，其形式是”report||用户标识||用户标识十六进制表示_密钥1_密钥2_密钥3_密钥4||ComputerName||版本||位数||语言”：

![](https://s1.ax1x.com/2020/07/16/UryPFx.png)

于勒索病毒目录下创建一名为`temp000000.txt`的文本文档，并将上述拼接内容写入文件：

![](https://s1.ax1x.com/2020/07/16/Urywt0.png)

![](https://s1.ax1x.com/2020/07/16/UryiY6.png)

接下来创建勒索文本并写入内容如下：

![](https://s1.ax1x.com/2020/07/16/UryElD.png)

遍历网络资源：

![](https://s1.ax1x.com/2020/07/16/UryuTI.png)

将遍历到的文件夹与下列字符串逐一比较，避免加密重要文件夹：

![](https://s1.ax1x.com/2020/07/16/Urydkq.png)

![](https://s1.ax1x.com/2020/07/16/UrygB9.png)

遍历网络资源中的目录：

![](https://s1.ax1x.com/2020/07/16/Ury0hV.png)

将勒索文本复制到每一文件目录下：

![](https://s1.ax1x.com/2020/07/16/Ur6pjg.png)

加密线程使用的加密算法首先是AES加密，其算法原理不再赘述(可参阅[密码学基础：AES加密算法](https://bbs.pediy.com/thread-253884.htm))：

![](https://s1.ax1x.com/2020/07/16/Uryr1U.png)

根据其密钥扩展算法亦可识别：

![](https://s1.ax1x.com/2020/07/16/UryyX4.png)

接下来将密文再次通过RC4算法进行加密：

![](https://s1.ax1x.com/2020/07/16/UrycnJ.png)

## 0x02 参考链接

  * [样本分析中解决 ollydbg 多线程调试](https://bbs.pediy.com/thread-254194.htm)
  * [再探勒索病毒之删除卷影副本的方法](https://cloud.tencent.com/developer/article/1655857)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **ERFZE** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/213890](/post/id/213890)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [恶意软件](/tag/恶意软件)
  * [勒索软件](/tag/勒索软件)

 **+1** __0赞

 __收藏

![](https://p4.ssl.qhimg.com/t01a9ce08613e49eaf2.png) ERFZE

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

