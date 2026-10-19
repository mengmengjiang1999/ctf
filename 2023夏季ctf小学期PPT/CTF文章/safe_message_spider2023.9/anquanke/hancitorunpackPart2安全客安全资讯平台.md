# hancitor unpack Part2

阅读量 **165359**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-12-06 16:30:27

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t011fdd55fb0f70eda4.jpg)

## intro

这是hancitor装载器的第二部分内容，对于恶意代码装载器来说，总是有着千变万化的方法去实现恶意代码，我仅学习这些代码并期望能在之后为此做出贡献 ！

MD5 (Hancitor – Packed): 7e9ba57db08f53b56715b0a8121bd839  
MD5 (Hancitor – Unpacked): a68de37bf71d2e5f5c9ab6c84f2fd695

###  样本分析

首先是导出函数，该样本除DllEntryPoint有8个导出函数，都是常见的单词，一般用于减慢分析样本的速度。

![](https://p1.ssl.qhimg.com/t01601a538a666c7efe.png)

对于分析这种样本的脱壳和有趣的部分，我们的分析流程如下：

首先f9 运行到entry point

![](https://p2.ssl.qhimg.com/t016430737ee581c3ec.png)

然后来到kernel32.dll的VirtualAlloc函数打下断点，虽然提示地址无法执行，我们仍需要设下断点

![](https://p3.ssl.qhimg.com/t01e36bb7e896d318da.png)

等待一会儿后就会命中断点了，此时我们根据msdn观察栈数据

    
    
    LPVOID VirtualAlloc(
      [in, optional] LPVOID lpAddress,
      [in]           SIZE_T dwSize,
      [in]           DWORD  flAllocationType,
      [in]           DWORD  flProtect
    );
    

![](https://p2.ssl.qhimg.com/t018f0e58c954d86e8e.png)

然后我们直接执行到retn。

![](https://p2.ssl.qhimg.com/t01f8073695b4a30f28.png)

第一，我们需要在VirtualAlloc函数入口打下断点，运行并hit到断点后，Return 返回到我们的代码段。直到我们看到如下几个特殊点：

  1. call to ebx + 2113E4 ，是用于动态调用 _VirtualAlloc**函数的，_
  2. rep movsb -用于把shellcode写入到刚刚申请的空间
  3. jmp eax – 跳转并执行shellcode

![](https://p5.ssl.qhimg.com/t01bdf4acdaaa7ec9a2.png)

因为shellcode存储在eax寄存器中，我们使用follow in dump即可找到对应的shellcode，是一个以字节组E8 00 00 00
起始的经典trick。

同时，根据习惯，我们可以猜想完整的unpack应该在shellcode的附近。我们运行两次直到我们第三次命中断点，此次生成了一大段的空白段供shellcode编写

![](https://p1.ssl.qhimg.com/t01eaf771f1205a7820.png)

我们在此处第一个字节打下硬件断点并运行

第一次运行只生成了首字节，第二次如下

![](https://p2.ssl.qhimg.com/t0189fa813ef0e42ab0.png)

第三次如下

![](https://p3.ssl.qhimg.com/t017bbe042d8269f5c8.png)

而实际上操作该地址的是以下几个汇编指令

![](https://p2.ssl.qhimg.com/t015700574b079dccba.png)

通过x32 dbg的图像功能显示如下，我们在一个小循环中找到一个带有一些经典的操作码，例如旋转右侧和排除或（ROR和XOR OPCODE）。

![](https://p3.ssl.qhimg.com/t014c9f1cd3aa4bcb03.png)

在这个特殊的循环中，加密主体在过去两年的恶意样本中同样类似出现过，例如：Hancitor，Zloader，SquirrelWaffle，Ursnif

![](https://p2.ssl.qhimg.com/t018097b5f6545c4222.png)

通过在leave opcode上设置断点，我们可以使循环结束，而一旦循环结束，我们就可以看到ASCII字符M8Z表明这是一个APLIB压缩后的代码。

![](https://p4.ssl.qhimg.com/t0143a6dbc27716dca4.png)

那么既然我们直到了这是一个APLIB实现的压缩，我们现在就是要寻找一个解压缩的代码。

  1. 首先删除硬件断点
  2. 在APLIB 压缩的headers区域设置硬件访问断点
  3. 运行

实际上是把ESI的数据解密后移动到了EDI地址处（这里的地址发生变化是因为中间发生失误运行了程序导致我重新跑了一次，地址变化了（0x110001—》
0x190000））

![](https://p5.ssl.qhimg.com/t0188f13aedf92f048a.png)

我们在retn处打下断点并运行后访问0x000117041地址处即可找到unack后的文件。此时我们使用processHacker进行提取

![](https://p3.ssl.qhimg.com/t01a6ae0907b0efa23d.png)

首先dump出0x110000处的数据

![](https://p3.ssl.qhimg.com/t0195d8417319d31ed5.png)

然后提取处0x7041物理地址处的数据即可。

![](https://p5.ssl.qhimg.com/t019ab2387feb48da3f.png)

然后这个文件是一个完整的文件，我们可以直接看到导入函数表和代码数据了。

![](https://p4.ssl.qhimg.com/t01b3132e3c5f000e6a.png)

## 收尾

这也是一个比较好玩的样本，本篇文章的分析仅通过以下文章学习分析和自己总结得出，不得不感叹技术的力量，感谢观看！  
<https://elis531989.medium.com/the-squirrel-strikes-back-analysis-of-the-newly-emerged-cobalt-strike-loader-squirrelwaffle-937b73dbd9f9>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Scr1pt** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/260705](/post/id/260705)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Malware](/tag/Malware)
  * [Hancitor](/tag/Hancitor)
  * [unpack](/tag/unpack)

 **+1** __0赞

 __收藏

![](https://thirdqq.qlogo.cn/g?b=oidb&k=vjicoX0azzqIIhmSdjJo9hQ&s=40&t=1606815583)
Scr1pt

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

