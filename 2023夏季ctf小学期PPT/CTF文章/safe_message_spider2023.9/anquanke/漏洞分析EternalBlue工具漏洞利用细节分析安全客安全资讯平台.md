# 【漏洞分析】EternalBlue工具漏洞利用细节分析

阅读量 **157812**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2017-11-06 17:18:36

 **x**

##### 译文声明

本文是翻译文章，文章来源：安全客

译文仅供参考，具体内容表达以及含义原文为准。

**前言**

****

EternalBlue（永恒之蓝）据称是方程式组织在其漏洞利用框架中一个针对SMB服务进行攻击的模块，由于其涉及漏洞的影响广泛性及利用稳定性，在被公开以后为破坏性巨大的勒索蠕虫WannaCry所用而名噪一时。360威胁情报中心对于WannaCry的活动持续地进行着监控，我们看到的趋势是
**WannaCry的感染量还在增加，说明作为蠕虫主要传播手段的EternalBlue相应的漏洞还大量存在着。** 但是，对于
**EternalBlue这个攻击利器本身的技术分析在公开渠道上看到的讨论其实并不充分**
，本文尝试通过一个较完全的分析梳理相关的细节，揭示其成因和相应的利用技巧。

  

**测试环境**

****

对于EternalBlue的分析是在一个相对简单的环境中进行的，执行攻击的系统为一个Win7机器，目标机器也是Win7
32位系统，没有安装EternalBlue相关的补丁，srv.sys文件的版本为 **6.1.7601.17514** ，srvnet.sys的版本为
**6.1.7601.17514** 。本文中所有的调试器中代码截图都对应上述的版本，不同版本的文件在代码本身或偏移可能不同，但整体的执行逻辑应该差不多。

**漏洞**

****

根据我们的分析，EternalBlue达到其攻击目的事实上利用了3个独立的漏洞：第一个也就是 **CVE-2017-0144**
被用于引发越界内存写；第二个漏洞则用于绕过内存写的长度限制；第三个漏洞被用于攻击数据的内存布局。下面重点介绍一下前两个漏洞，第三个漏洞会在内存布局的过程中提到。

**漏洞1**

首先是EternalBlue工具中使用到的主体漏洞，该漏洞也是Eternalblue的核心部分，编号为CVE-2017-0144。漏洞通过SMB协议的SMB_COM_TRANSACTION2命令触发，该命令说明如下所示：

当该数据包中包含对应的FEA LIST时，SMB服务中会将FEA LIST转换为对应的NTFEA
LIST，其对应的数据结构并不公开，如下所示为趋势团队分析出的对应的FEALIST结构。

入口处理函数为SrvSmbOpen2，其中漏洞出现在函数SrvOs2FeaListToNt中：

如下所示为对应的漏洞函数SrvOs2FeaListToNt，用于实现FEA LIST转换为对应的NTFEA
LIST，函数调用SrvOs2FeaListSizeToNt计算FEALIST的长度，但是该函数存在漏洞导致在特定的情况下，攻击者可以伪造超长的size，从而导致在之后的SrvOs2FeaToNt转换中导致pool溢出。

进入导致漏洞的SrvOs2FeaListSizeToNt函数，该函数会计算对应的FEA
LIST的长度并随后对长度进行更新，该长度一开始为DWORD类型的，之后的长度更新代码中计算出的size拷贝回去的时候是按WORD进行的拷贝，此时只要原变量a中的初始值大于FFFF，即为10000+，该函数的计算结果就会增大。

该赋值中如下所示esi变成了si，此时如果eax高位中的数据不为零，则将返回的超长的size。

如下图所示为对应发送的该数据包，可以看到该请求数据包的长度为103d0，其中对应的FEALIST的长度为10000。

如下图所示，eax为链表的开头，其指向了FEA LIST的总长度，即10000，esi为遍历之后的链表尾部，eax-esi=ff5d，为实际对应的长度，但是更新长度的mov指令中esi变成了si，由于eax中的值为10000，原本应该被赋值为ff5d的eax，变成了1ff5d。

之后在紧接着的函数SrvOsFeaToNt中，由于使用了错误的长度进行memmove从而导致溢出。

下图为其中的复制导致越界写，长度为a8，可以看到正常请求应该是在86535000这个srv.sys对象SMB
buffer中，由于长度过长导致对srvnet.sys分配的buffer越界写。

Enternalblue中通过内存布局，将srvnet对象buffer稳定的分配到srv拷贝对象buffer之后，如下图所示为越界写时的内存情况。

Srvnet 对象buffer中包含两个重要的域：

1.一个指向指定结构（srvnet_recv）的指针（即上图中的8834e4c0，被ffdff020覆盖），该指针将会在smb(srnet)连接结束或断开时被用于寻址函数地址。

2.一个用于接收缓冲区的MDL（即上图中的86546160，被ffdfef80覆盖）

因此覆盖并控制MDL将导致之后的tcp
栈实现任意写入伪造对象的操作，覆盖并控制该指针可用于将其指向一个攻击者控制的伪造对象，此时断开smb(srvnet)连接即可导致代码执行。

如下图所示，MDL复写为ffdfef80后，紧接着Eternalblue发送的shellcode就会被写入到ffdfef80+0x80的位置，即ffdff000。

可以看到此时的调用栈：

写入的地址ffdff000是系统预留的用于保存系统信息的地址，并且可执行。

被写入到ffdff000地址的是一个srvnet_recv的结构（该结构不公开）和紧随其后的shellcode，该结构用于smb(srnet)结束或断开连接的时候通过SrvNetWskReceiveComplete调用SrvNetCommonReceiveHandler
。SrvNetCommonReceiveHandler
根据srv_recv中的指针此处为下图中的poi（ffdff190（ffdff020（被覆盖的对应指针）+0x16c）+4）获取到对应的函数并调用，地址即我们伪造的shellcode的地址（ffdff1f1）。

**漏洞2**

如上述漏洞所示可以导致一次越界写，但其前提是FEA LIST的长度必须大于10000，通过分析可以发现FEA
LIST只存在于SMB_COM_TRANSACTION2命令的子命令中，而该命令的数据结构如下：

TotalDataCount（数据包总长度）是USHOER类型的，即最大值只能为FFFF，那在这个地方EternalBlue是如何发送的长度大于FFFF的SMB_COM_TRANSACTION2子命令请求的呢？

通过抓包可以发现此处发送的并不是SMB_COM_TRANSACTION2子命令的请求包，而是SMB_COM_NT_TRANSACT子命令的请求包：

如下图所示SMB_COM_NT_TRANSACT子命令中TotalDataCount的类型为ULONG，支持发送大于FFFF长度的数据包。

但是SMB_COM_NT_TRANSACT本身是不支持FEA LIST的，这里就涉及到EternalBlue中使用到的第二个漏洞。

SMB的子命令中存在一个名为TRANSACTION系列的命令：

SMB_COM_TRANSACTION: 用于和邮槽、命名管道进行通信

SMB_COM_TRANSACTION2: 用于打开或创建一个共享文件或文件夹，设置它们的扩展属性

SMB_COM_NT_TRANSACT: 用于打开或创建一个文件或文件夹，并应用扩展属性EA或安全描述符SD

其中产生漏洞的即为对应的SMB_COM_TRANSACTION2命令。

对于TRANSACTION系列的命令如果发送的长度过大，SMB会将该请求包拆分成**Second的形式进行发送，如下所示为其相应的**Second系列的命令：

SMB_COM_TRANSACTION

SMB_COM_TRANSACTION_SECONDARY

SMB_COM_TRANSACTION2

SMB_COM_TRANSACTION2_SECONDARY

SMB_COM_NT_TRANSACT

SMB_COM_NT_TRANSACT_SECONDARY

服务端根据SMB请求头部的TIP，PID，UID，MID确定哪一个**Second属于对应的transtion，而服务端根据最后一个**Second确定对应的transtion类型，即如果最后一个**Second为SMB_COM_TRANSACTION2_SECONDARY，就按SMB_COM_TRANSACTION2来处理。

如下图为处理对应**Second的逻辑，对于一个transaction，如果没有发送完，后续会跟上对应的**Second数据包，服务端不会检查对应的**Second类型，只要保证其TIP，PID，UID，MID匹配，服务端就会将这些数据重新组装还原成一个transaction，而类型由最后一个**Second决定。

因此，为了发送一个长度为0x10000的SMB_COM_TRANSACTION2，首先发送一个长度为103d0（FEA
LIST：1000）SMB_COM_NT_TRANSACT，之后发送一系列SMB_COM_TRANSACTION2_SECONDARY数据包，只要保证TIP，PID，UID，MID一致，服务端最后就会将其当做一个SMB_COM_TRANSACTION2来处理，而此时其长度103d0。

由于SMB会等待最后一个**SECOND数据包到来才生成最后的transaction，因此EternalBlue可以在此期间发包对目标设备的内存进行部署，之后再发送最后一个数据包从而触发漏洞越界写。

  

**内存布局的构建**

****

如上述分析，利用漏洞会触发溢出导致越界写，而EternalBlue中对于该漏洞的利用思路和大多数的pool越界写是一致的：

1.在内存中spray一系列srvnet的对象buffer

2.释放掉其中的空间，以便于srv的对象buffer进行占位

3.srv对象buffer占位

4.发包越界写srvnet的对象buffer

5.触发代码执行

**srvnet对象spray**

但是这里和一般的内核漏洞的利用存在一个很大的区别，就是我们的环境是远程的。通常的本地内核漏洞利用的时候我们可以从容地选择进行spray的内核对象，但是对于远程的环境而言，内核对象的选择及对应的控制就要小很多。

EternalBlue中用于被覆盖的对象为srvnet buffer，其中的对象包含两个重要的结构：

1.一个指向指定结构的指针，通过覆盖它可以将其指向一个伪造的结构，从而实现后续的代码执行。

2.一个接受MDL的缓冲区，通过覆盖它可以保证将后续发送的伪造结构及shellcode写到指定的区域。

微软提供了SMB 2直接支持TCP的通信方式，可以通过该方式来创建srvnet缓冲区。

如下图所示srvnet对象的spray过程，生成的大小依赖于前四字节。

**srv对象spray**

srv对象是通过释放后重申请的方式获取的地址空间，但是SMB中如何通过远程方式稳定的申请并释放一段pool内存了?这就涉及到EternalBlue中使用的第3个漏洞。

该漏洞出现在SMB_COM_SESSION_SETUP_ANDX命令中：

该命令的请求依赖于WordCount的值来确定具体的请求格式，当为12时格式如下图所示，当为13时红框中的变量会有所区别。

直接借用网上逆向简化后的一段代码，如下所示：如果发送的代码中WordConut为12，包含CAP_EXTENDED_SECURITY字段，但却没有FLAGS2_EXTENDED_SECURITY字段，将会导致服务器将以处理13类型请求的方式去处理类型12的请求包，从而进入错误的函数
**GetNtSecurityParameters** 流程中。

**GetNtSecurityParameters**
会检查对应的请求中的参数，函数参数中的v70为通过wordcount和Bytecount计算出来的一个size。

**GetNtSecurityParameters** 函数中的计算如下所示：

该参数返回后作为 **SrvAllocateNonPagedPool** 的参数分配一段pool。

因此利用该漏洞将12类型的请求包通过13类型进行处理，由于两种类型的请求包格式不一致，通过控制请求包指定偏移的数据，即可以控制SrvAllocateNonPagedPool创建的pool的大小，可以使用以下的断点监控该过程：

    
    
    bp GetNtSecurityParameters+0x1AC ".printf"GetNtSecurityParameters1\n";r;.echo;?cx-si+bx+1d;g;"
    bp SrvAllocateNonPagedPool+0x10 ".printf"SrvAllocateNonPagedPool NonPageSize:%p\n",ecx;g;"
    bp SrvAllocateNonPagedPool+0x15C ".printf"SrvAllocateNonPagedPool alloc Nopage:%p\n",eax;g;"
    bp BlockingSessionSetupAndX+0x7C0 ".printf"BlockingSessionSetupAndX double\n";g;"

如下图所示即为通过断点监控到的非法size生成的过程，通过构造畸形数据包，包含数据87f8，漏洞触发后识别出该错误的偏移，计算最后会分配一段大小为10fec大小的pool。

通过断开对应的该命令请求，可以导致之前分配的10fec大小的pool被释放，从而在地址空间中生成一个hole，该hole之后会被srv对象buffer来填充。

现在知道了如何在内存中稳定的spray一段连续的srvnet的对象buffer，以及如何开辟并释放一段指定大小的空间，内存布局的基本条件已经具备，可以看到具体的布局流程到最后的触发执行过程如下：

1.通过SMB_COM_NT_TRANSACT发送一段FEA LIST长度满足0x10000的数据包

2.发送后续的SMB_COM_TRANSACTION2_SECONDARY，这将导致smb服务将SMB_COM_NT_TRANSACT当做SMB_COM_TRANSACTION2处理，但是最后一个SMB_COM_TRANSACTION2_SECONDARY留置最后。

3.通过smb 2协议进行srvnet对象的spray

4.通过SMB_COM_SESSION_SETUP_ANDX漏洞在srvnet对象之后分配一段大小和srv对象大小几乎一致的pool内存

5.通过smb 2协议继续进行srvnet对象的spray，以确保srvnet位于srv对象之后

6.断开连接导致第4步开辟的pool内存释放，生成一个hole

7.发送最后一个SMB_COM_TRANSACTION2_SECONDARY，由于大小一致，该数据包会填补生成的hole，并触发漏洞导致之后的srvnet对象buffer中的MDL和指针被修改，此时后续发送的数据将拷贝到ffdff000的位置。

8.断开所有连接，触发srvnet_recv指向的shellcode执行

可以通过以下断点监控利用时内存的释放和分配（主要是srv，srvnet对象）：

    
    
    bp SrvAllocateNonPagedPool+0x10 ".printf"SrvAllocateNonPagedPool NonPageSize:%p\n",ecx;g;"
    bp SrvAllocateNonPagedPool+0x15C ".printf"SrvAllocateNonPagedPool alloc Nopage:%p\n",eax;g;"
    bp SrvFreeNonPagedPool+0x3 ".printf"SrvFreeNonPagedPool free Nopage:%p\n",eax;g;"
    bp BlockingSessionSetupAndX ".printf"BlockingSessionSetupAndX\n";g;"
    bp SrvNetAllocateNonPagedBufferInternal ".printf"AllocateNonPaged NonPagedBufferSize:%p\n",poi(esp+8);g;"
    bp SrvNetAllocateNonPagedBufferInternal+0x179 ".printf"AllocateNonPaged NonPagedBufferAddress:%p\n",eax;g;"
    bp SrvNetFreeNonPagedBufferInternal ".printf"SrvNetFreeNonPagedBufferInternal free NonPageBufferAddress:%p\n",poi(esp+4);g;"
    ba e1 srvnet!SrvNetWskReceiveComplete+0x13 ".if(poi(esi+0x24) == ffdff020) {} .else {gc}"

如下图所示即为整体监控到的数据包于内存中的布局情况，其中867bb000处为对应的srv buffer对象，之后867cc000上的srvnet
buffer对象将会被覆盖如下所示：

以上为EternalBlue利用过程中内存布局及对应发送数据包的一个概述，但是其内部其实还有一些细节可供深入挖掘。由于作者水平有限，有什么错误欢迎大家指正。

  

**参考资料**

****

<http://bobao.360.cn/learning/detail/3738.html>

<https://github.com/worawit/MS17-010>

<http://blog.trendmicro.com/trendlabs-security-intelligence/ms17-010-eternalblue/>

本文翻译自安全客 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **奇安信威胁情报中心** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/87168](/post/id/87168)

安全客 - 有思想的安全新媒体

本文转载自: [安全客]()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p3.ssl.qhimg.com/t01dce0f9e833e11f13.png) 奇安信威胁情报中心

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

