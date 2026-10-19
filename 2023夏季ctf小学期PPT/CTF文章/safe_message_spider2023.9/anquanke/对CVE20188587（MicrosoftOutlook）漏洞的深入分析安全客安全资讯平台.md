# 对CVE-2018-8587（Microsoft Outlook）漏洞的深入分析

阅读量 **291222**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-12-20 10:59:54

 **x**

##### 译文声明

本文是翻译文章，文章原作者 fortinet，文章来源：fortinet.com

原文地址：<https://www.fortinet.com/blog/threat-research/a-deep-analysis-of-the-microsoft-outlook-vulnerability-.html>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/dm/1024_538_/t0155b7faa48a18e713.png)

## 事件经过

前一段时间，Fortinet的FortiGuard实验室研究员Yonghui Han按照FortiGuard
Labs的漏洞披露规则，向微软报告了Office
Outlook中存在的一个堆溢出漏洞。12月11日微软宣布该漏洞已被修补，并发布了漏洞通告，该漏洞的CVE编号为CVE-2018-8587

Microsoft Outlook是Microsoft
Office套件的组件之一，广泛用于发送和接收电子邮件，管理联系人，记录和跟踪日程安排以及执行其他任务。Yonghui
Han在Windows上运行的多个版本的Outlook中发现了堆溢出漏洞，该漏洞涵盖从Outlook 2010到最新的Outlook
2019以及Office 365
ProPlus的所有32/64位版本的软件。该漏洞通过构造格式错误的RWZ文件（邮件分类规则文件）触发，当Outlook接受到不正确的RWZ文件时，它分配的堆空间过少而且缺少合适的边界检查，导致堆溢出漏洞产生。

## 漏洞复现

复现流程：运行Microsoft
Outlook，然后单击“规则=>管理规则和警报=>选项=>导入规则”，然后选择导致Outlook崩溃的PoC文件，接着进行漏洞的分析。

![](https://p4.ssl.qhimg.com/t014b611e1ee29782be.png)

以下是发生崩溃时的调用堆栈：

![](https://p5.ssl.qhimg.com/t012143ed9380bc2550.png)

可以看到，崩溃发生在堆块被释放时。由于我们现在无法确认被释放的堆块有什么问题，所以我们通过启用Full Page Heap机制来跟踪有问题的堆块。命令如下：

    
    
    YOUR_WINDBG_INSATALL_LOCATIONgflags.exe /p /enable outlook.exe /full
    

下面的返回结果，表明命令成功执行。

![](https://p2.ssl.qhimg.com/t0137b4fd6a32cbad2d.png)

然后我们再次复现来监视新堆栈

![](https://p5.ssl.qhimg.com/t018c0e371de9277fd4.png)

现在我们可以看到ECX指向的非零内存地址是不可读的，并且在将数据写入该内存地址时会发生异常。判断出程序很有可能尝试将数据写入未分配（或未释放）的内存地址。我们可以通过检查内存页面分配情况进行判断。内存页面分配情况显示这里依然存在保留的内存空间。如下图所示：

![](https://p0.ssl.qhimg.com/t019ed2005f5c4c8653.png)

我们现在需要弄清楚程序为什么要将数据写入未使用的内存页面。通过静态分析，我们可以看到ECX的值来自EDI，并且在调用MAPIAllocateBuffer之后程序似乎正在修改EDI，如下图所示：

![](https://p3.ssl.qhimg.com/t01dc80cd2b293abf4c.png)

通过静态分析，我们了解到函数MAPIAllocateBuffer是RtlAllocateHeap的包装函数，它用于确保请求的堆大小参数不大于0x7FFFFFF7。这意味着它不是一个负值。但是，在这种情况下，它不会检查0是否可以作为参数。并且因为实际分配的堆大小比请求的堆大小多8个字节，所以这8个字节用0x0000000001000010填充。此后，MAPIAllocateBuffer在这8个字节后返回堆地址。因此，调用MAPIAllocateBuffer后的EDI值为8
加上 从RtlAllocateHeap接收的分配的堆地址。如下图所示：

![](https://p1.ssl.qhimg.com/t01643eb6c61fa9579e.png)

![](https://p2.ssl.qhimg.com/t01de800eb7bb1a70fd.png)

从上面的静态分析中，我们可以基本判断出向保留的内存空间中写入数据的原因极有可能是由整数溢出引起的。结合调试，我们发现调用MAPIAllocateBuffer的堆大小值确实为0。但是，由于MAPIAllocateBuffer请求分配大小为0
+ 8 =
8的堆，因此RtlAllocateHeap不会返回错误而是会返回正确的堆地址。但是，MAPIAllocateBuffer会向这8个字节写入0x0000000001000010，然后向用户返回无效的heap-tail地址。如下图所示：

![](https://p5.ssl.qhimg.com/t0115d10749a357a64f.png)

接下来，我们需要弄清楚为什么请求的堆大小的值变为0。结合调试和静态分析，我们发现0来自当前函数的参数：arg_4（eax = arg_4 * 4 + 4）
。但是，在调用当前函数时，arg_4的值不并是传入参数的值，说明此函数会修改arg_4。通过调试我们可以看到修改的功能是在子函数sub_65F7DA中完成的。如下图所示：

![](https://p0.ssl.qhimg.com/t01ae85443fab698ee9.png)

通过对子函数sub_65F7DA的分析，我们发现它是另一个包装函数。经过一系列调试后，我们终于发现函数ReadFile，也就是arg_4的值，实际上来自PoC文件。如下图所示：

![](https://p1.ssl.qhimg.com/t0150c22da8a51371e9.png)

![](https://p4.ssl.qhimg.com/t012aeff6e9b9c70481.png)

调试显示arg_4读取的文件中的内容为0xFFFFFFFF，通过整数溢出，使得传递的堆的分配大小为0xFFFFFFFF * 4 + 4 =
0。但是，程序没有检查这一点，导致在下一个堆中出现Out-of-Bounds问题。如下图所示：

![](https://p2.ssl.qhimg.com/t014a2567dac04f3af2.png)

检查PoC文件，我们可以看到0xFFFFFFFF值确实存在。

![](https://p5.ssl.qhimg.com/t0109ea0a66ec1f2e5c.png)

将其修改为0xAABBCCDD，我们再次执行调试并设置相同的断点来验证溢出是由这4个字节引起的。

![](https://p0.ssl.qhimg.com/t01729eeac24a4f568b.png)

![](https://p2.ssl.qhimg.com/t011f076995ec5325cd.png)

到这里我们成功分析出漏洞产生的原因！

接下来，通过在Patch发布之后比较程序的汇编代码，我们可以看到现在程序已经添加了对所请求的分配堆大小的验证。如下图所示：

![](https://p4.ssl.qhimg.com/t0115598813d731108b.png)

## 解决方法

更新即可

本文翻译自fortinet.com [原文链接](https://www.fortinet.com/blog/threat-research/a-deep-analysis-of-the-microsoft-outlook-vulnerability-.html)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **ppz** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/168205](/post/id/168205)

安全客 - 有思想的安全新媒体

本文转载自: [fortinet.com](https://www.fortinet.com/blog/threat-research/a-deep-analysis-of-the-microsoft-outlook-vulnerability-.html)

如若转载,请注明出处： <https://www.fortinet.com/blog/threat-research/a-deep-analysis-of-the-microsoft-outlook-vulnerability-.html>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Office](/tag/Office)
  * [OUTLOOK](/tag/OUTLOOK)
  * [系统安全](/tag/系统安全)
  * [CVE-2018-8587](/tag/CVE-2018-8587)

 **+1** __0赞

 __收藏

![](https://p5.ssl.qhimg.com/t015a71f9dca2ee0439.jpg) ppz

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

