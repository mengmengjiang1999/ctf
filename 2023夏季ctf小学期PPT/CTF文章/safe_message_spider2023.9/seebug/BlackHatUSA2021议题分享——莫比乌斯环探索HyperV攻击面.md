**作者：洪祯皓@蚂蚁安全实验室  
原文链接：<https://mp.weixin.qq.com/s/TMe_Qxh4CZB3L0GiA1hbqA>**

近日，蚂蚁安全光年实验室洪祯皓的议题《Mobius Band Explore Hyper-V Attack Interface through
Vulnerabilities Internals》入选全球最顶级的极客大会Black Hat USA
2021，该议题重点分享了微软Azure云的虚拟化解决方案Hyper-V的新型攻击面。

虚拟化软件作为业务和硬件的连接桥梁，一旦被发现漏洞，很可能横向影响多台虚拟机，纵向影响业务软件及物理机安全。Hyper-V作为微软虚拟化解决方案的代表，微软对其安全漏洞的奖金高达25万美金，可见微软对其安全性的重视与信心，业内相关的研究资料也是凤毛麟角。

本篇议题首先介绍了Hyper-V的基本架构，以及Guest中的数据是如何传输到Host中的Hyper-V组件并加以解析的。然后通过和Windows平台上EOP漏洞利用的比较，总结出Hyper-V在安全研究中存在的难点。议题中还公开了三个已经修复的Hyper-V RCE漏洞，这三个漏洞都可以在Guest中触发，并可导致Hyper-V
Host执行任意代码。通过探究这些漏洞的成因和触发方式，读者将了解到Hyper-V的多个攻击面。

## 01 Hyper-V架构介绍

Hyper-V总体架构如下：

![图片](https://images.seebug.org/content/images/2021/09/10/1631262996000-1urbzb.png-w331s)

Hyper-V的Hypervisor架构如下：

![图片](https://images.seebug.org/content/images/2021/09/10/1631262996000-2jrhqb.png-w331s)

Hyper-V的VMBUS架构如下：

![图片](https://images.seebug.org/content/images/2021/09/10/1631262997000-3ovqyf.png-w331s)

Hyper-V中的Host Driver架构如下:

![图片](https://images.seebug.org/content/images/2021/09/10/1631262997000-4diurc.png-w331s)

Hyper-V的Ring3架构如下：

![图片](https://images.seebug.org/content/images/2021/09/10/1631262997000-5qirtb.png-w331s)

## 02 Hyper-V Guest和Host之间如何通信

Hyper-V Guest和Host之间的通信依靠VMBUS组件。在Guest中，vmbus_open函数用来初始化Guest中的VMBUS
Channel。vmbus_open函数的流程如下：

![图片](https://images.seebug.org/content/images/2021/09/10/1631262997000-6ogqpm.png-w331s)

vmbus_sendpacket函数被Guest用来向Host发送数据，vmbus_on_event函数被Guest用来接收Host发来的数据。

下面介绍在Host中的VMBUS，这里有两个重要的函数：vmbkmclr!KmclpVmbusManualIsr和vmbkmclr!KmclpVmbusIsr。

vmbkmclr!KmclpVmbusManualIsr用来分发Guest数据到Host驱动，vmbkmclr!KmclpVmbusIsr用来分发数据到Host用户态组件。

下面是Guest数据到Host驱动的路径，这里拿storvsp驱动为例。

![图片](https://images.seebug.org/content/images/2021/09/10/1631262998000-7rqzhp.png-w331s)

下面是Guest数据到Host用户态组件的路径，这里拿vmiccore组件为例。

![图片](https://images.seebug.org/content/images/2021/09/10/1631262998000-8caqlg.png-w331s)

## 03 Hyper-V安全研究的难点

这里我们用Win32k!EngRealizeBrush整数溢出漏洞（MS17-017）比较Hyper-V在安全研究中的难点。

在攻击面层面上，传统的EoP漏洞可以使用的系统API很多，并且Ring0中的驱动可以直接从用户态地址读取数据。而Hyper-V中，没有可以使用的系统API，所有的数据都通过VMBUS传输，Ring0中的驱动无法直接从Guest地址中读取数据。

在内核对象的分配和释放层面上，传统的EoP漏洞有很多内核对象可以利用、很容易控制内核对象的分配和释放、通过利用内核对象构造读写原语也相对容易。在Hyper-V中，目前还在寻找适合用作漏洞利用的内核对象、对内核对象的释放与分配无法做到直接的控制，也无法做到直接控制分配与释放的时机、某些内核对象中只有很少的内容可以从Guest中控制。

在TOCTTOU类型的漏洞层面上，传统的EoP需要满足两个基本点，第一是内核模块取到一个用户态的指针，第二是从这个用户态指针中获取数据超过两次。但在Hyper-V中，所有的数据都通过VMBUS机制传输，Ring0组件无法直接通过Guest中的地址读取到数据。

## 04 漏洞细节

这个漏洞编号为CVE-2019-0620，下面是触发这个漏洞的栈回溯。

![图片](https://images.seebug.org/content/images/2021/09/10/1631262998000-9zmlzq.png-w331s)

发生这个漏洞的根源在调用vmbkmclr!VmbChannelPacketComplete函数时，两次调用中使用了相同的第一参数。

![图片](https://images.seebug.org/content/images/2021/09/10/1631262999000-10aismb.png-w331s)

我们在WinDbg中下断点，并且进行调试。

断点内容为：bp storvsp!VstorCompleteScsiRequest+0x2d7 "r @rcx;k;r @$thread;!pool
@rcx;.echo ; g"。

![图片](https://images.seebug.org/content/images/2021/09/10/1631263000000-11uoemn.png-w331s)

![图片](https://images.seebug.org/content/images/2021/09/10/1631263000000-12tybwy.png-w331s)

下面的栈回溯在正常流程中被触发：

![图片](https://images.seebug.org/content/images/2021/09/10/1631263000000-13nscll.png-w331s)

下面的栈回溯只有在vhdmp!VhdmpiPerformExtraScsiActions函数的第二参数偏移0x08处的内存不为NULL时被触发。

使用vhdmp!VhdmpiScsiCommandWriteUsingToken和vhdmp!
VhdmpiScsiCommandCopyOperationAbort函数可以间接的将vhdmp!VhdmpiPerformExtraScsiActions函数的第二参数偏移0x08处的内存写入一个指针，并触发如下栈回溯。

![图片](https://images.seebug.org/content/images/2021/09/10/1631263000000-14qrdcg.png-w331s)

vhdmp!VhdmpiScsiCommandWriteUsingToken和vhdmp!
VhdmpiScsiCommandCopyOperationAbort函数的上层调用是vhdmp!VhdmpiScsiCommandCopyOperations。

![图片](https://images.seebug.org/content/images/2021/09/10/1631263001000-15mtids.png-w331s)

如图所示，v5可以通过Guest控制。

![图片](https://images.seebug.org/content/images/2021/09/10/1631263001000-16tiayp.png-w331s)

POC代码节选如下：

![图片](https://images.seebug.org/content/images/2021/09/10/1631263001000-17xiysh.png-w331s)

下个漏洞的编号为CVE-2019-0720。下面是崩溃时的现场。

![图片](https://images.seebug.org/content/images/2021/09/10/1631263001000-18rscrf.png-w331s)

RtlDeleteElementGenericTableAvl函数的第二参数是RtlLookupElementGenericTableAvl函数的返回值。

![图片](https://images.seebug.org/content/images/2021/09/10/1631263002000-19kvrnx.png-w331s)

![图片](https://images.seebug.org/content/images/2021/09/10/1631263002000-20vsidx.png-w331s)

RtlDeleteElementGenericTableAvl函数从generic
table中删除一个特定的元素并且随后释放掉这个特定元素。vmbusr!ChUnmapGpadlView函数的第二参数是gpadl_handle，gpadl_handle可以被Guest控制。

vmbusr!ChUnmapGpadlView函数运行在多线程的环境中，也就是多CPU环境中。vmbusr!ChUnmapGpadlView函数的第二参数也就是gpadl_handle可以被Guest控制，并且该函数第一参数可以被我们使用的channel控制。

假设有如下的情况：

1、有两个线程ThreadA和ThreadB，运行在不同的CPU上。

2、ThreadA和ThreadB同时运行到vmbusr!ChUnmapGpadlView函数。

3、这两个线程调用vmbusr!ChUnmapGpadlView函数使用同样的参数。

4、ThreadA比ThreadB要快一点点。

我们把vmbusr!ChUnmapGpadlView函数分为三个状态。如下图：

![图片](https://images.seebug.org/content/images/2021/09/10/1631263002000-21nfcem.png-w331s)

第一步，ThreadA首先会获取到自旋锁，ThreadA处于状态1并持有锁。同时，ThreadB也会试图获取并等待锁。

第二步，ThreadA调用函数RtlLookupElementGenericTableAvl并返回指针A，然后ThreadA释放掉自旋锁。

第三步，ThreadB会获取到相同的锁，ThreadA现在在试图获取并等待锁。这个时候，ThreadA在状态2，ThreadB在状态1并且持有锁。

第四步，ThreadB调用RtlLookupElementGenericTableAvl函数并且返回指针B，然后ThreadB释放掉自旋锁。因为两个线程调用vmbusr!ChUnmapGpadlView函数使用了相同的参数，所以指针A和指针B是相同的。

第五步，ThreadA会获取到第二个自旋锁，然后调用vmbusr!ChDeleteGpadlViewIfUnreferenced函数并且释放掉指针A指向的内存，并且将指针A从generic
table中删除。最后，ThreadA会释放掉自旋锁。现在，ThreadB在状态2，ThreadA在状态3。

第六步，ThreadB获取到第二个自旋锁，然后调用函数vmbusr!ChDeleteGpadlViewIfUnreferenced释放到指针B指向的内存，并且将指针B从generic
table中删除。

因为指针A和指针B相等，所以vmbusr!ChDeleteGpadlViewIfUnreferenced函数使用了一个已经释放掉的内存作为第二参数，然后，发生UAF。

所以，如果我们想触发这个问题，必须要有两个必要条件：1、有两个互不干扰的线程运行到vmbusr!ChUnmapGpadlView函数。2、两个线程调用vmbusr!ChUnmapGpadlView函数拥有相同的参数，即gpadl_handle相同。

幸运的是，我找到了两个不同的线程调用vmbusr!ChUnmapGpadlView函数，并且可以控制它们变成两个互不干扰的线程。下图是这两个线程的栈回溯。

![图片](https://images.seebug.org/content/images/2021/09/10/1631263002000-22uzwkz.png-w331s)

![图片](https://images.seebug.org/content/images/2021/09/10/1631263003000-23sqbjy.png-w331s)

Thread1可以通过向宿主机发送NVSP_MSG1_TYPE_REVOKE_RECV_BUF消息和CHANNELMSG_GPADL_TEARDOWN消息触发。代码节选如下：

![图片](https://images.seebug.org/content/images/2021/09/10/1631263003000-24akbcf.png-w331s)

Thread2可以通过模拟按下虚拟机的reset键触发。代码节选如下：

![图片](https://images.seebug.org/content/images/2021/09/10/1631263004000-25kbxfa.png-w331s)

并且，efi.rest_system会触发一个重要的线程去控制Thread1和Thread2变成两个互不干扰的线程。下面是这个重要线程的栈回溯：

![图片](https://images.seebug.org/content/images/2021/09/10/1631263004000-26bmdcf.png-w331s)

这个重要的线程需要在Thread1和Thread2前运行，所以我们需要使用下面的代码来设置vmswitch!VmsVmNicPvtRevokeRecieveBufferWorkItem函数进入睡眠状态。

![图片](https://images.seebug.org/content/images/2021/09/10/1631263004000-27rgplb.png-w331s)

POC代码的原理是设置vmswitch!VmsVmNicPvtRevokeRecieveBufferWorkItem函数的第二参数偏移0xe0处的内存设置成非0，并且vmswitch!VmsVmNicPvtRevokeRecieveBufferWorkItem函数会进入睡眠状态直到第二参数偏移0xe0处的内存设置成0。幸运的是，我们也可以调用efi.rest_system把第二参数偏移0xe0处的内存设置成0。

![图片](https://images.seebug.org/content/images/2021/09/10/1631263004000-28curzu.png-w331s)

现在，我们可以创建两个互不相干的调用vmbusr!ChUnmapGpadlView函数的线程了。

下面是这个漏洞的触发和调试过程。

![图片](https://images.seebug.org/content/images/2021/09/10/1631263004000-29dddjz.png-w331s)

![图片](https://images.seebug.org/content/images/2021/09/10/1631263005000-30bbtpy.png-w331s)

![](https://images.seebug.org/content/images/2021/09/50765922-d462-4001-a0ab-a95706deebae.jpg-w331s)

![图片](https://images.seebug.org/content/images/2021/09/10/1631263005000-32msjeh.png-w331s)

![图片](https://images.seebug.org/content/images/2021/09/10/1631263005000-33uaxlv.png-w331s)

![图片](https://images.seebug.org/content/images/2021/09/10/1631263005000-34mafad.png-w331s)

最后一个漏洞是CVE-2020-16891，下面是这个漏洞崩溃时的现场。

![图片](https://images.seebug.org/content/images/2021/09/10/1631263006000-35glvwl.png-w331s)

![图片](https://images.seebug.org/content/images/2021/09/10/1631263006000-36zehdg.png-w331s)

这个漏洞触发需要使用windows server系列的操作系统，而且需要如下设置。在网卡的选择上，我使用了Intel(R) Ethernet 10G 4P
X540/I350 rNDC #2网卡。

![图片](https://images.seebug.org/content/images/2021/09/10/1631263006000-37imijg.png-w331s)

这个问题发生在vmwp!EmulatorVp::FlushGvaTranslationCache函数中，这个函数如下图所示。

![图片](https://images.seebug.org/content/images/2021/09/10/1631263006000-38erbwl.png-w331s)

![图片](https://images.seebug.org/content/images/2021/09/10/1631263006000-39skuoq.png-w331s)

在偏移0x9E处，vmwp!EmulatorVp::FlushGvaTranslationCache函数会调用vmwp!
VND_HANDLER_CONTEXT::RemoveReference函数。在vmwp!
VND_HANDLER_CONTEXT::RemoveReference函数中会调用vmwp!Vml::VmSharableObject::DecrementUserCount函数，如果函数vmwp!VND_HANDLER_CONTEXT::RemoveReference第一个参数偏移-0x50处的值为1的话，vmwp!Vml::VmSharableObject::DecrementUserCount将会释放掉一个VmbComMmioHandlerAdapter对象，这个对象的大小为0xb0。

函数vmwp!VND_HANDLER_CONTEXT::RemoveReference第一个参数偏移-0x50处的值为一个引用计数器的地址，如果这个引用计数器的值为1，一个VmbComMmioHandlerAdapter对象就会被释放。在下面的文章中，我将这个引用计数器称为
**KEY_REF_COUNTER** 。

我们发现，调用vmwp!VndCompletionHandler::HandleVndCallback函数也可以减少上文中提到的
**KEY_REF_COUNTER**
。在vmwp!VndCompletionHandler::HandleVndCallback函数偏移0xAAE位置处，调用了Vml::VmSharableObject::DecrementUserCount函数。如图。

![图片](https://images.seebug.org/content/images/2021/09/10/1631263007000-40znoik.png-w331s)

我们可以通过构造下面的POC代码，控制vmwp.exe进程运行到vmwp!VndCompletionHandler::HandleVndCallback函数偏移0xAAE位置处。

![图片](https://images.seebug.org/content/images/2021/09/10/1631263007000-41mdgbk.png-w331s)

![图片](https://images.seebug.org/content/images/2021/09/10/1631263007000-42fqffi.png-w331s)

下面的POC代码用来控制vmwp.exe进程运行到vmwp!EmulatorVp::FlushGvaTranslationCache+0x9e位置处。

![图片](https://images.seebug.org/content/images/2021/09/10/1631263007000-43hzbwx.png-w331s)

但是，这个virt_addr+0x1004地址代表着什么呢？经过查阅Linux
Kernel代码，我发现这个地址可能代表着PCI_COMMAND的地址，向其中写入2和0分别代表着开启和关闭内存空间响应这个功能。

下面我们触发并且调试这个漏洞。下面是断点信息。

![图片](https://images.seebug.org/content/images/2021/09/10/1631263007000-44amirm.png-w331s)

我们直接来到漏洞发生位置，在vmwp!VndCompletionHandler::HandleVndCallback函数偏移0xAAE位置处，
**KEY_REF_COUNTER** 被减1，随后在
vmwp!EmulatorVp::ActuallyAttemptEmulation偏移0x2b3处断下，通过调试器可以看到，这时的
**KEY_REF_COUNTER** 的值为1。如下图所示。

![图片](https://images.seebug.org/content/images/2021/09/10/1631263008000-45ayhoc.png-w331s)

通过查看VmbComMmioHandlerAdapter对象的地址，发现此时的对象还没有被释放，如下图。

![图片](https://images.seebug.org/content/images/2021/09/10/1631263008000-46tulpz.png-w331s)

继续跟踪，发现VmbComMmioHandlerAdapter对象随后被释放掉了。

![图片](https://images.seebug.org/content/images/2021/09/10/1631263008000-47qlhqy.png-w331s)

继续调试，进程在vmwp!EmulatorVp::ActuallyAttemptEmulation偏移0x290处断下。此时的rcx寄存器中存放的正是刚刚被释放的VmbComMmioHandlerAdapter对象的地址，用WinDbg查看这个地址的状态，如下图。

![图片](https://images.seebug.org/content/images/2021/09/10/1631263009000-48eyebm.png-w331s)

## 05 攻击面

vmcall调用、虚拟化MSR读写、APIC虚拟化、嵌套虚拟化等是Hypervisor组件攻击面。

![图片](https://images.seebug.org/content/images/2021/09/10/1631263009000-49dlisu.png-w331s)

Guest可以通过发送CHANNELMSG_OPENCHANNEL等消息到达VMBUS组件的攻击面。

![图片](https://images.seebug.org/content/images/2021/09/10/1631263009000-50blhhi.png-w331s)

虚拟设备如vmswitch、storvsp、动态内存等，在Guest中可以通过调用vmbus_sendpacket发送特定的虚拟设备数据到达对应的驱动文件或者dll文件中。如下两图。

![图片](https://images.seebug.org/content/images/2021/09/10/1631263009000-51hiajf.png-w331s)

![图片](https://images.seebug.org/content/images/2021/09/10/1631263010000-52kycwr.png-w331s)

## 06 潜在攻击面

Hyper-V的潜在攻击面有vmswitch中的Packet Direct功能、Network Direct功能、PCI-E
PassThrough、虚拟机层嵌套虚拟化等等。这些组件不是虚拟机默认配置，但是可以通过特定配置打开。换句话说，这些组件功能并不常用，可能是一些比较好的研究方向。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1705/>

