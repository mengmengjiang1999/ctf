# 新型勒索软件利用开源的GnuPG加密数据

阅读量 **145070**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-03-25 15:27:52

 **x**

##### 译文声明

本文是翻译文章，文章来源：securingtomorrow.mcafee.com

原文地址：<https://securingtomorrow.mcafee.com/mcafee-labs/ransomware-takes-open-source-path-encrypts-gnu-privacy-guard/>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t01cc1c263c5dfcb840.png)

## 一、前言

McAfee实验室最近发现了一种新型的勒索软件，其使用开源的GNU Privacy Guard (GnuPG)来加密数据。
GnuPG是一个混合加密软件程序，使用常规的对称加密来提高加密速度以及公钥加密来进行安全的密钥交换。尽管使用GnuPG加密文件的勒索软件不是第一次出现，但这种方式并不常见。  
我们这次分析的样本—GPGQwerty具有以下SHA-256散列值:

>   * 2762a7eadb782d8a404ad033144954384be3ed11e9714c468c99f0d3df644ef5
>   * 39c510bc504a647ef8fa1da8ad3a34755a762f1be48e200b9ae558a41841e502
>   * f5cd435ea9a1c9b7ec374ccbd08cc6c4ea866bcdc438ea8f1523251966c6e88b
>

我们发现这些样本的运行需要许多其他文件支持。这三个文件本身不会加密任何内容。GPGQwerty由一系列文件组成，这些文件共同运行来加密受害者的计算机。这一系列文件如下所示:

  
这个勒索软件在3月初首次出现。通常，这类恶意软件会通过垃圾邮件，恶意附件，漏洞利用或是伪造成合法下载应用等方式进行传播。二进制文件39c510bc504a647ef8fa1da8ad3a34755a762f1be48e200b9ae558a41841e502是在hxxp://62.152.47.251:8000/w/find.exe中被发现的;它可能是路过式下载（Drive-by download）策略的一部分，或是用于将来托管在合法网站上进行恶意传播。  
Key.bat，run.js，和find.exe是在加密过程中起至关重要作用的三个文件。感染过程如图所示：

![](https://p0.ssl.qhimg.com/t0160ab4b2f4f76b326.png)

## 二、技术细节分析

二进制文件find.exe有8个节区，其.bss节区的Raw Size为0。

  
它还有一个特殊的TimeDateStamp（文件创建时的时间戳）:

  
该样本利用恶意线程本地存储（TLS）回调技术来防止其他人对其分析。通常，此技术允许可执行文件包含恶意TLS回调函数，以便在可执行头中的AddressOfEntryPoint字段（二进制文件的正常执行点）之前运行。

  
该操作从批处理文件key.bat的执行开始。它通过执行JavaScript脚本
run.js来导入密钥并在受害者机器上启动find.exe。批处理和JavaScript文件的内容如下所示:

  
  
接下来，该勒索软件利用命令行工具taskkill杀死了一些选定的正在运行的任务。该命令具有通过指定进程ID或图像文件名来杀死任务或进程的功能。在下面的代码片段中，我们看到它通过指定图像名强制终止一些进程。

  
勒索软件试图通过GnuPG（gpg.exe）加密数据。恶意软件还会将扩展名.qwerty附加到加密文件后缀处:

  
恶意软件使用shred.exe覆盖原始文件。

  
在加密完成之后，勒索软件会分配一个唯一的ID来标识每个受害者。它还会创建一个.txt文件，指出计算机上的所有文件都已被锁定，受害者必须付费才能解密这些文件。

  
GPGQwerty使用Windows下的del删除回收站：

  
勒索软件利用“vssadmin.exe Delete Shadows /All /Quiet”这条命令来删除目标系统中的volume shadow
copies服务（用于管理及执行用于备份和其他目的的磁碟区卷影）(vssadmin.exe,
wmic.exe)。从而防止受害者恢复加密文件。它还会删除备份目录（wbadmin.exe）并在启动时禁用自动修复（bcdedit.exe）:

  
最后，它会在每个包含加密文件的文件夹中创建赎金备注readme_decrypt.txt。赎金备注中提供了在72小时内与指定电子邮件地址进行沟通的说明，以安排后续付款。

![](https://p2.ssl.qhimg.com/t01740f182e0441c5d5.png)

## 三、检测规则

下面给出了McAfee检测此勒索软件的规则框架:

    
    
    rule crime_ransomware_windows_GPGQwerty: crime_ransomware_windows_GPGQwerty
    
    {
    
    meta:
    
    author = “McAfee Labs”
    
    description = “Detect GPGQwerty ransomware”
    
    strings:
    
    $a = “gpg.exe –recipient qwerty -o”
    
    $b = “%s%s.%d.qwerty”
    
    $c = “del /Q /F /S %s$recycle.bin”
    
    $d = “cryz1@protonmail.com”
    
    condition:
    
    all of them 
    
    }

本文翻译自securingtomorrow.mcafee.com
[原文链接](https://securingtomorrow.mcafee.com/mcafee-labs/ransomware-takes-open-source-path-encrypts-gnu-privacy-guard/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **CuteWeier** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/101723](/post/id/101723)

安全客 - 有思想的安全新媒体

本文转载自:
[securingtomorrow.mcafee.com](https://securingtomorrow.mcafee.com/mcafee-labs/ransomware-takes-open-source-path-encrypts-gnu-privacy-guard/)

如若转载,请注明出处： <https://securingtomorrow.mcafee.com/mcafee-labs/ransomware-takes-open-source-path-encrypts-gnu-privacy-guard/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [恶意软件](/tag/恶意软件)
  * [勒索软件](/tag/勒索软件)
  * [样本分析](/tag/样本分析)

 **+1** __3赞

 __收藏

![](https://p0.ssl.qhmsg.com/dm/200_200_100/t015f786102d9185a33.jpg) CuteWeier

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

