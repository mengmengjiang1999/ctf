# 在WIN10上不使用Mimikatz绕过LSA保护（PPL）

阅读量 **214791**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-03-02 10:00:32

 **x**

##### 译文声明

本文是翻译文章，文章原作者 redcursor，文章来源：redcursor.com.au

原文地址：<https://www.redcursor.com.au/blog/bypassing-lsa-protection-aka-protected-process-light-without-mimikatz-on-windows-10﻿>

译文仅供参考，具体内容表达以及含义原文为准。

从Windows 8.1（和Server 2012
R2）开始，Microsoft引入了一项称为LSA保护的功能。此功能基于PPL技术，它是一种纵深防御的安全功能，旨在“防止非管理员非PPL进程通过打开进程之类的函数串改PPL进程的代码和数据”。

我发现许多人都对这个技术存在误解，认为LSA
Protection是阻止利用SeDebug或管理员权限从内存中提取凭证的攻击,例如使用Mimikatz来提取凭证。实际上LSA保护不能抵御这些攻击，它只会让你在执行这些攻击前，需要做一些额外的操作，让攻击变得更加困难一些。

要绕过LSA保护，您有几种选择：

    
    
    1.删除RunAsPPL注册表项并重新启动（这可能是最糟糕的方法，因为您将丢失内存中的所有凭据）
    2.通过修改EPROCESS内核结构，在LSASS进程上禁用PPL标志
    3.直接读取LSASS过程存储器的内容，而不使用打开的过程函数
    

后两种方法需要具有读取和写入内核内存的能力。实现此目的最简单的方法是通过加载驱动程序，尽管您可以创建自己的驱动程序，但我决定利用产品MSI
Afterburner的RTCore64.sys驱动程序。我选择该驱动程序是因为它已签名，并允许读写任意内存，感谢MSI。

我决定实施第二种方法，因为删除PPL标志允许使用现成的工具（如Mimikatz）从LSASS转储凭证。为此，我们需要找到LSASS
EPROCESS结构的地址，并将5个值（SignatureLevel，SectionSignatureLevel，Type，Audit和Signer）修改为零。

EnumDeviceDrivers函数可用于泄漏内核基地址。这可以用来定位PsInitialSystemProcess，它指向系统进程的EPROCESS结构。由于内核将进程存储在链接列表中，因此EPROCESS结构的ActiveProcessLinks成员可用于迭代链接列表并查找LSASS。

![](https://p0.ssl.qhimg.com/t01cfb6095f4a076d77.png)

如果我们看一下EPROCESS结构（请参见下面的图2），我们可以看到我们需要修改的5个字段通常都按连续4个字节对齐。
这使我们可以在单个4字节写入中修改EPROCESS结构，如下所示：  
“WriteMemoryPrimitive（设备，4，CurrentProcessAddress + SignatureLevelOffset，0x00）;

![](https://p5.ssl.qhimg.com/t01f907f604db1ecae8.png)

现在已经删除了PPL，所有转储LSASS的传统方法都可以使用，例如MimiKatz，MiniDumpWriteDump API调用等。

可以在[GitHub](https://github.com/RedCursorSecurityConsulting/PPLKiller
"GitHub")上找到用C / C ++编写的用于执行此攻击的工具。 我仅在Windows
1903、1909和2004上进行过测试。它应该在所有版本的Windows上都可以运行。

本文翻译自redcursor.com.au [原文链接](https://www.redcursor.com.au/blog/bypassing-lsa-protection-aka-protected-process-light-without-mimikatz-on-windows-10﻿)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **HelloWorld** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/232080](/post/id/232080)

安全客 - 有思想的安全新媒体

本文转载自: [redcursor.com.au](https://www.redcursor.com.au/blog/bypassing-lsa-protection-aka-protected-process-light-without-mimikatz-on-windows-10﻿)

如若转载,请注明出处： <https://www.redcursor.com.au/blog/bypassing-lsa-protection-aka-protected-process-light-without-mimikatz-on-windows-10﻿>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [渗透测试](/tag/渗透测试)
  * [系统安全](/tag/系统安全)

 **+1** __0赞

 __收藏

![](https://thirdwx.qlogo.cn/mmopen/vi_32/MRL7MicQcb9FMwAfl4PuXOClsqXRFX1XsRsTIYBF1sEoVqbPRAsXMU5PtWb3WibIJibI8oPXUwXgPemeMw0CaAuibw/132)
HelloWorld

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

