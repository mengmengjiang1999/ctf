![](https://image.3001.net/images/20201022/1603367048_5f9170887e90b063998e8.png!small)

## 漏洞概述

Windows内核在处理内存中对象的时候，存在一个提权漏洞。攻击者将能够利用该漏洞实现提权，并在目标设备上实现代码执行。为了利用该漏洞，经过了身份认证的本地攻击者可以在目标主机上运行一个专门设计的应用程序。在这篇文章中，我们将对这个漏洞CVE-2020-1034进行深入分析。

## 补丁对比

受影响的模块为ntoskrnl.exe，我下载了该模块的已修复版本和未修复版本，并在Windows 10 1903 x64系统上对其进行了分析比对。

下面给出的是版本18362.1049和18362.1082之间的源码对比结果：

![](https://image.3001.net/images/20201022/1603367063_5f917097b3634722e4725.png!small)

很明显，EtwpNotifyGuid发生了变化，因此我对该函数源码进行了简单分析，并发现了一个重大改变：

![](https://image.3001.net/images/20201022/1603367070_5f91709e03a5dd5793779.png!small)

因此，我决定对其进行深入分析。

## 漏洞分析

首先，我研究了一下EtwpNotifyGuid的网关，也就是[
_NtTraceControl_](http://www.geoffchappell.com/studies/windows/km/ntoskrnl/api/etw/traceapi/control/index.htm)。

![](https://image.3001.net/images/20201022/1603367081_5f9170a9ec8a6bda23401.png!small)

调用EtwpNotifyGuid的FunctionCode为0x11，而且在调用之前还需要进行一些条件检测，具体如下图所示：

![](https://image.3001.net/images/20201022/1603367088_5f9170b0eb804dc6e7dc8.png!small)

在对EtwpNotifyGuid的分析过程中，我们还发现了下面这些有意思的修复点：

![](https://image.3001.net/images/20201022/1603367095_5f9170b7aeb0431b4facf.png!small)

rdi寄存器包含收入缓冲区的地址，图表中的数据表明地址rdi+0Ch的字节数据决定了是否去创建一个UmReplyObject对象。

接下来，我们看看r12b寄存器的值是从哪里来的：

![](https://image.3001.net/images/20201022/1603367103_5f9170bfd77097a2a000a.png!small)

r12b的初始值为4，但是这里被设置成了1。因此，当byte ptr
[rdi+0Ch]的值为1时，rdi+18h的qword会被设置为新创建的UmReplyObject的地址。否则，qword将保持原样。这将引起非常严重的后果，因为输入数据永远不可信。

我将rdi+18h的qword设置为了一个任意值，正如我们所料，设备蓝屏了：

![](https://image.3001.net/images/20201022/1603367109_5f9170c5e323485808763.png!small)

这就非常棒了，我们继续。

这里的输入缓冲区被传递给了EtwpSendDataBlock和EtwpQueueNotification：

![](https://image.3001.net/images/20201022/1603367123_5f9170d3078d86d931c74.png!small)

查看EtwpQueueNotification，我发现了引用UmReplyObject的地方：

![](https://image.3001.net/images/20201022/1603367130_5f9170da853b9b7729e0e.png!small)

这里的bl值为0，如果rbp+0Ch的字节值不为0，那么rbp+18h的qword会被读取为一个指向对象的指针，然后对象的引用将会增加。

![](https://image.3001.net/images/20201022/1603367136_5f9170e0ca761aef5df49.png!small)

我们知道了漏洞的根源，罪魁祸首就是代码对rbp+0C字节数据的不一致对比。对比操作是在EtwpNotifyGuid中进行的，代码会比较值是否为1来判断是否需要创建一个新的UmReplyObject对象。但在最后一次比较中，将该值与零进行了比较。

第一次比较在C代码中的形式如下：

    
    
    if（*（bool*）（rdi+0x0C）==  true）

第二次比较的代码形式如下：

    
    
    if (*(bool*)(rbp+0x0C))

如果值不是1或者0的话，任何输入的值都将被视作对象地址。接下来，ObfReferenceObject将会调用该地址，这也就意味着qword ptr
[[InputBuffer + 0x18] - 0x30] ++运算将会被执行，这样将导致任意地址增加。

## 漏洞利用代码

![](https://image.3001.net/images/20201022/1603367144_5f9170e82a9f545db4201.png!small)

## 漏洞演示视频

