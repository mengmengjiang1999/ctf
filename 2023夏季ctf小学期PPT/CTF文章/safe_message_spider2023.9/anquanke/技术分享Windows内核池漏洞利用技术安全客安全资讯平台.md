# 【技术分享】Windows内核池漏洞利用技术

阅读量 **164680**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2017-07-05 14:54:10

 **x**

##### 译文声明

本文是翻译文章，文章来源：samdb.xyz

原文地址：<https://samdb.xyz/windows-kernel-exploitation-part-4/>

译文仅供参考，具体内容表达以及含义原文为准。

译者：[华为未然实验室](http://bobao.360.cn/member/contribute?uid=2794169747)

预估稿费：300RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

本文将介绍如何利用[HackSys Team Extremely Vulnerable
Driver](https://github.com/hacksysteam/HackSysExtremeVulnerableDriver)中的释放后重用和池溢出问题。为此我们需要对Windows内核内存管理有所了解。因此，本文将涵盖以下内容：

1\. Windows内核内存分配概述

2\. Windows内核池风水演练

3\. 利用HackSys Team Extremely Vulnerable Driver的释放后重用

4\. 通过两种不同的方法利用HackSys Team Extremely Vulnerable Driver的池溢出

本文专注于windows 7 sp1（32位）。

  

**Windows内核池**

了解内存管理的基础知识有所帮助，如果你不曾了解虚拟内存和分页，那么有必要快速阅读以下内容：

1\. [内存程序剖析](http://duartes.org/gustavo/blog/post/anatomy-of-a-program-in-memory/)

2\. [内核如何管理你的内存](http://duartes.org/gustavo/blog/post/how-the-kernel-manages-your-memory/)

Windows内核使用两种动态大小的“池”来分配系统内存，这些内核等同于用户模式下的堆。我只介绍理解利用方法原理所需的详情，更多信息请查看：

1. [Windows 7 内核池利用](https://media.blackhat.com/bh-dc-11/Mandt/BlackHat_DC_2011_Mandt_kernelpool-wp.pdf)，作者：Tarjei Mandt

2\. 《Windows Internals》第7版第1部分第5章或《Windows Internals》第6版第2部分第10章——内存管理

3\.  [Windows驱动程序的内存管理](https://msdn.microsoft.com/en-us/library/windows/hardware/ff554389\(v=vs.85\).aspx)

Windows中有两种关键类型的池——非分页池和分页池。还有特殊池（我将在介绍释放后重用利用方法时介绍）和win32k使用的会话池（本文不作介绍）。

  

**分页池对比非分页池**

非分页池由保证总是存储在物理内存中的内存组成，而分页池中分配的内存可以被分页。这是必需的，因为某些内核结构需要在高于可满足缺页中断的[IRQL](https://blogs.technet.microsoft.com/askperf/2008/01/22/what-is-irql-and-why-is-it-important/)可访问。有关IRQL的更多详细信息以及各级别支持的操作，请参阅“[管理硬件优先级](https://msdn.microsoft.com/en-us/library/windows/hardware/ff554368\(v=vs.85\).aspx)”。

这意味着非分页池用于存储进程、线程、信号量等关键控制结构。而分页池用于存储文件映射、对象句柄等。分页池实际上由几个单独的池组成，而在Windows
7中，只有一个非分页池。

为了分配池内存，驱动程序和内核通常使用ExAllocatePoolWithTag函数，其定义如下：

PoolType参数包含一个POOL_TYPE枚举中的值。这定义了正在请求什么类型的池内存，我们将主要看到其用0调用，这对应于非分页池。

第二个参数是所需的池内存的字节数，最后的PoolTag参数是一个32位值，其被完全视为用于标记内存用途的4个字符，这在调试时非常方便，并且也被大量内核内存instrumentation使用——跟踪使用某个标签进行了多少分配，当内存分配到某个标签时中断，等等。

为了释放分配的池内存，通常使用[ExFreePoolWithTag](https://msdn.microsoft.com/en-us/library/windows/hardware/ff544593\(v=vs.85\).aspx)函数。

这只需要一个指向有效池分配的指针，池元数据将给予所有其他所需的东西，在标准条件下，提供的池标签将不会被验证。但是，启用正确的调试设置后，标签将被验证，如果其不匹配，则会触发一个BSOD。现在我们来看看这些函数的工作原理。

  

**分配内存**

反编译器 ExAllocatePoolWithTag 乍看之下很吓人。

还好，Tarjei Mandt已经在其[论文](https://media.blackhat.com/bh-dc-11/Mandt/BlackHat_DC_2011_Mandt_kernelpool-wp.pdf)中将函数转化为伪代码，这可以作为一个很好的指导。我将使用他的伪代码和IDA中的一些检查等，并通过windbg来解释函数的工作原理。他的解释可能更好、更准确，本节中的所有代码片段都来自其论文。

首先，函数检查请求的字节数是否超过4080字节，如果是，则调用Big Pool 分配器。

此处，esi包含请求的字节数，如果高于0xff0，则转到nt!ExpAllocateBigPool。否则采取true分支，处理继续。

在这一点上，[esp+48h+var_20]持有末尾为1的PoolType。所以如果该值等于0，则其是一个非分页池，跳过上面的if语句并转到随即显示的else，同时，如果类型是用于分页池内存，则采取true分支。

在true分支上，其检查池类型是否用于会话池。

其随后立即检查请求的字节数是否高于32。

同时，在false分支上，其还检查分配是否高于32字节。

如果任一检查通过，逻辑会有点麻烦，更多详情可见[Tarjei的论文](https://media.blackhat.com/bh-dc-11/Mandt/BlackHat_DC_2011_Mandt_kernelpool-wp.pdf)。该函数将尝试通过在相关池的Lookaside列表中找到一个条目来分配请求的块。Lookaside列表是每个池的每处理器结构，对它的引用存储在[内核处理器控制块](http://www.codemachine.com/article_kernelstruct.html#KPCR)中。Lookaside列表由通常请求的内存大小的单链表组成，对于一般池内存，这是频繁进行的小分配。使用Lookaside列表可以使这些频繁的分配更快地进行。对于非常频繁进行的固定大小的分配，存在其他更具体的lookaside列表。

如果两个大小检查均未通过，或者从lookaside列表分配内存失败，则分页池描述符被锁定，这与用于非分页池的结构相同，并且以相同的方式使用，所以我稍后将对此进行描述。

现在我们有了请求的分配是非分页池类型时运行的代码，此处我们在上面的loc_518175处采取了false分支。

接下来，代码将检查请求的块大小是小于还是等于32字节，如下所示。如上所述，如果分配足够小，其将尝试使用lookaside列表，如果成功则返回true。

如果lookaside列表不能使用或请求的块大小大于32字节，则非分页池描述符将被锁定。首先将获取非分页池描述符的指针，如果有超过1个的非分页池，将进行查找。

首先，将根据可用的非分页池数量和“本地节点”（论文解释了这一点，但出于性能原因，多核系统中的每个处理器都可以有首选本地内存）来计算ExpNonPagedPoolDescriptor表中的索引：

此处eax最终持有所选索引。然后从表中读取引用：

这与分页池的逻辑相同，计算索引然后获得引用：

此时，分页和非分页分配的代码路径已达到同一点。分配器将检查页面描述符是否被锁定，如果没有锁定则获取锁定。

现在描述符结构实际上包含什么？还好，其包含在Windows 7的公共符号中。

我们刚刚看到，(Non)PagedLock字段在函数明确获取描述符锁定之前被检查。PoolType是自解释的，PoolIndex字段指示可以在内核导出的ExpPagedPoolDescriptor或ExpNonPagedPoolDescriptors表中找到哪些条目。我们真正关心的其他字段是PendingFrees
和PendingFreeDepth（在下一节中解释），以及我们需要现在看一看的ListHeads。

ListHeads是8个字节倍数到大分配的空闲内存块列表。每个条目包括一个LIST_ENTRY结构，其是相同大小的块的链表的一部分。列表由请求的块大小+
8（以给POOL_HEADER留出空间，稍后描述）索引，除以8以获得字节数。分配器将从所需的确切大小的条目开始通览列表，查找要使用的有效块，如果不能精确匹配，则其查找更大的条目并将其拆分。伪代码如下：

因篇幅限制，此处我们有所删减，不过我们可以更详细地介绍函数实际上成功找到正确大小的内存块时会发生什么。分配器进行的分配是请求的数量+8字节，以给之前提到的POOL_HEADER留出空间。该结构包含在Windows
7的公共符号中，如下所示：

PreviousSize字段是内存中先前分配的大小，这是在释放分配以检查损坏时使用的。如前所述，PoolIndex字段可用于查找分配的POOL_DESCRIPTOR。BlockSize是包括header在内的分配的总大小，最后，PoolType是来自分配的POOL_TYPE枚举的值，如果块不空闲，则为2。PoolTag是自解释的。

最后，如果函数在已分配的内存页中找不到分配空间，则其将调用MiAllocatePoolPages，以创建更多，并返回新内存中的地址。

如下所示：

**  
**

**释放内存**

这一次我只提供了一些关于[Tarjei Mandt](https://media.blackhat.com/bh-dc-11/Mandt/BlackHat_DC_2011_Mandt_kernelpool-wp.pdf)的反转代码的评论，我不知道程序集片段有多大用处，希望我的补充有作用。这只包括与漏洞利用有关的组件，所有代码和细节请参阅原论文。

块大小应等于下一个池对象头中的上一个大小字段，如果不是，则内存已损坏，BugCheck被触发。当覆盖这个结构时，我们需要确保用正确的值覆盖块大小，否则会蓝屏。

然后检查分页池类型，我跳过了会话部分。

如果启用了延迟释放，则查看等待列表是否有>= 32个条目，如果有，则全部释放，并将当前条目添加到列表中。

我们只查看允许DefferedFree的系统，所以我将跳过旧的合并逻辑。ExDeferredFreePool中的逻辑相当直观，函数定义如下。

其接收一个指向POOL_DESCRIPTOR的指针，该指针先前被ExFreePoolWithTag锁定。然后其循环通过PendingFrees，并释放每个条目。如果上一个或下一个条目被释放，则其将与当前被释放的块合并。

  

**Windows内核池风水**

为了执行内核池风水，我们需要在正确类型的池中分配对象，及哪些是对我们有用的大小。我们知道，关键的内核数据结构（如信号量）存储在非分页池（也因所有基于池的挑战而被HackSys驱动程序使用）中。要开始，我们需要找出一些在非分页池中分配的内核结构及其大小。实现此目标的简单方法是分配一些控件对象，然后使用内核调试器来查看相应的池分配。我使用以下代码来做到这一点。

编译并运行此代码得到如下输出，然后敲击回车键后，我们附带的内核调试器应该中断。

使用调试器，我们可以找到每个结构驻留在内存中的位置以及为其分配了多少内存。在windbg中，可以输入!handle命令来获取对象的详细信息。此处我正在检索Reserve对象的详细信息。

一旦我们知道对象地址，我们就可以使用!pool命令查找其池详细信息。作为其第二个参数解析2意味着其只显示我们感兴趣的确切分配，删除2将显示内存页内的周围分配。

这里我们可以看到，Reserve对象被分配了一个'IoCo'标签，占用了60个字节。为其他对象重复此过程得到以下结果。

知道对象大小将在稍后我们需要确保确定大小的目标对象被可靠地分配内存空间中时有用。现在我们尝试使用Event对象进行池修饰，这些对象为我们提供了一个空闲和分配的0x40字节池块的模式。

因为分配器开始在空闲页上分配内存之前通过查找空闲块为对象分配内存，因此我们需要先填充现有的0x40字节空闲块。

比如下面的代码将分配五个事件对象。

现在，如果我们构建这个代码并使用附带的内核调试器来运行它，我们可以看到五个事件对象的句柄。

检查windbg中的最后两个句柄发现，其没有被分配到彼此接近之处。

进一步查看分配了倒数第二个Event对象的页面的池信息后发现，其刚好被放置在两个随机对象之间的第一个可用间隙中。

但是，如果我们将DEFRAG_EVENT_COUNT增加到更大的数，结果大不相同。

再次运行它并查看最后的五个句柄。

检查windbg中的句柄可以看到，其被连续分配在内存中。

检查分配有两个Event对象的页面的池布局可以发现，一长串Event对象被连续分配。内存分配器的确定性表明，如果我们分配足够的Event对象，这最终总会发生。

现在我们要在受控大小的地址空间中创建“孔”。此时我们知道，分配的任何更多事件对象将大部分被连续分配，所以，通过分配大量对象，然后间隔释放，我们应该得到一个空闲和分配对象的模式。

我将以下代码添加到了上面的示例（循环打印最后五个句柄的位置）中。

运行后，我们得到一个示例句柄，该句柄从一个模糊随机索引打印到其余句柄中。

检查windbg中的句柄后可以找到其在内存中的地址。

知道分配地址后，我们可以再次查看其分配的页的池布局。此处我们可以看到，我们已经成功地创建了一个空闲和分配的事件对象的模式。

对于我们无法找到相同大小的相应内核对象的对象/分配，我们可以使用分割大小的对象的多个副本，或尝试更精细的东西。

HackSysTeam极其脆弱的驱动程序释放后重用利用

内存在释放后被使用时存在释放后重用(UAF)漏洞。通过查找代码执行此操作的地方，可能可以用其他内容替换释放的内存。那么当引用内存并且代码认为一个结构/对象在那里时，另一个是。通过在可用内存中放置正确的新数据，可以获得代码执行。

  

**漏洞**

正如我刚才所解释的，为了利用UAF，我们需要以下几点：

1\. 一种创建对象的方式

2\. 一种释放对象的方式

3\. 一种替换其的方法

4\. 一种导致替换对象作为原始对象被引用的方式

和以前一样，简要看一下IDA中的驱动程序表明了我们的所有需求，我将从第1、2及4点开始，因为这些让我们开发了一个崩溃PoC。首先，我们需要一种使用驱动程序在内核内存中创建一个对象的方法，查看IOCTL分派函数给我们呈现了一个通过记录以下字符串进行的函数调用：******
HACKSYS_EVD_IOCTL_CREATE_UAF_OBJECT ******。这看似正是我们所寻找的。

查看函数本身后可以看到在非分页池上分配了0x58字节的内存。

如果此分配成功，则其继续将值加载到内存中，并在全局变量中保存对其的引用。

在1处，函数将所有分配的内存设置为用“0x41”字节填充。然后将0字节加载到内存的最后一个字节。在3处加载到对象的前四个字节的函数指针是一个记录其被调用的简单函数。

最后在4处，驱动程序在名为P的全局变量中保存指向内存的指针。

现在我们可以创建对象，我们需要一种方法来释放它。记录****** HACKSYS_EVD_IOCTL_FREE_UAF_OBJECT
******之后的IOCTL分派函数中的函数调用可能是一个很好的调用。

查看函数本身可以看到，其不需要任何输入，而是在我们查看的最后一个函数存储的引用之上操作。

一旦被调用，函数在1处检查在create函数中引用的全局指针“P”是否为空，然后在2处继续在其上调用ExFreePoolWithTag。

到我们的第三个需求——一种使驱动程序以某种方式引用释放的对象的方法，****** HACKSYS_EVD_IOCTL_USE_UAF_OBJECT
******似乎可以做到这一点。

查看函数后可知，其尝试通过create函数调用加载到UAF对象的前四个字节的函数指针。

在1处，其确保P包含指向对象的指针，且不是空指针。然后其将前四个字节的内存加载到eax中，并在2处确保其不是空字节。如果这两个检查都成功，则在3处进行回调。

敲定所需的IOCTL代码为我们提供了我们需要的三种IOCTL代码。

**  
**

**编写崩溃PoC**

为了可靠地检测是否已发生UAF，我使用了一些Windows内核池调试功能。在这种情况下，使用以下命令启用HackSysExtremeVulnerableDriver的[专用池](https://docs.microsoft.com/en-us/windows-hardware/drivers/devtest/special-pool)。

如果这成功运行，我们应会看到以下输出。

当启用了特殊池的二进制程序调用ExAllocatePoolWithTag函数时，其将使用ExAllocatePoolWithTagSpecialPool函数来分配内存，而不是遵循其标准逻辑。如下所示。

ExFreePoolWithTag函数具有匹配的逻辑。特殊池作为由单独的内存页支持的文字分离内存池工作。特殊池有一些不同的选项。默认情况下，其处于验证结束模式，简言之，这意味着由驱动程序所作的所有分配被放置在尽可能靠近内存页末尾处，后续和之前页面被标记为不可访问。这意味着，如果驱动程序尝试在分配结束后访问内存，将会触发错误。此外，页面上未使用的内存用特殊模式标记，因此如果这些内存损坏，则该内存释放后可检测到错误。

此外，特殊池将标记其释放的内存，并尽可能长时间地避免重新分配该内存。如果释放的内存被引用，其将触发错误。这会对驱动程序产生巨大的性能影响，因此其只在调试内存问题时启用。

在特殊池为启用状态下，我们可以为此漏洞创建一个简单的崩溃概念证明。下面的代码将创建UAF对象、释放该对象，然后导致其被引用。如果驱动程序引用释放的内存，这应该因特殊池调试功能而触发蓝屏。

现在编译并运行，然后…

使用附带的内核调试器重新启动系统，重新启用特殊池并重新运行PoC，这样我们可以确认崩溃是否由被引用的释放的内存引起。

!analyze
-v输出立即告诉我们，崩溃可能是由被引用的释放的内存引起的，进一步查看分析输出可知，崩溃指令是之前在调用UAF对象回调函数的IOCTL中看到的push
[eax]指令。

检查驱动程序尝试再次访问的内存地址的池详细信息后确认，内存可能之前已被释放。

**  
**

**将其转化为利用方法**

有了崩溃后，我们需要用可让我们在引用时实现代码执行的东西代替对象使用的内存。通常，我们必须寻找一个适当的对象，并可能使用一个基本的原语来让我们获得一个我们可以用于提升我们的权限的更有用的原语。不过幸运的是，HackSys驱动程序有一个让这更容易的函数。日志消息******
HACKSYS_EVD_IOCTL_CREATE_FAKE_OBJECT ******之后暴露的函数可以实现我们需要的功能。

查看函数实现后可知，其分配0x58字节的数据，然后检查分配是否成功。

一旦其分配了所需的内存，其便将数据从IOCTL输入缓冲区复制到其中。

在1处，指向分配的内存的指针为ebx，在2处，其验证从输入缓冲区读取数据是否是安全的，然后在3处，其在返回之前将0x16,
4字节块从输入缓冲区复制到新分配的内存中。

伪分配的对象与我们可以释放并导致被引用的对象大小相同，这一事实是理想的场景。通过使用先前描述的内核池按摩技术，我们可以导致伪对象分配到UAF对象的地址。通过加载一个指向伪对象开头的某些令牌窃取shellcode的指针，我们可以触发使用UAF对象IOCTL代码处理程序，从而使驱动程序执行我们的payload。

与我在池风水示例中使用的Event对象不同，UAF对象不是0x40字节，所以我们将使用Reserve对象，因为我们早先发现，当包括8字节POOL_HEADER时，这些是匹配0x58字节的UAF对象的内存中的0x60字节。首先，我们需要添加以下header。

接下来，我们添加以下代码来执行实际的池风水，这将填充任何现有的空闲0x60字节区域，然后创建一个分配和空闲的0x60字节块的模式。

现在我们可以强制我们的伪对象分配到我们需要制作伪对象的UAF对象之前所在的位置。我们首先将本系列前面部分中使用的令牌窃取器添加到我们的用户空间代码中。

接下来我们来创建我们的伪对象，我们知道其需要是0x58字节，前四个包含一个函数指针，其余的字节我们不关心。将函数指针设置为我们的令牌窃取shellcode的地址后，其将在驱动程序引用我们的伪对象并触发其所认为的原始对象回调时执行。这紧随用于释放UAF对象的DeviceIOControl调用。

我创建了0x250的伪对象，用于填充我们之前创建的所有间隙。另外，我们需要在我们文件的顶部定义HACKSYS_EVD_IOCTL_ALLOCATE_FAKE_OBJECT。

最后一些清理代码和调用系统启动calc.exe适合代码的末尾。

构建然后运行代码（特殊池为禁用状态）给我们提供了一个作为SYSTEM运行的良好计算器。

漏洞利用的最终/完整代码见[Github](https://github.com/sam-b/HackSysDriverExploits/blob/master/HackSysUseAfterFree/HackSysUseAfterFree/HackSysUseAfterFree.cpp)。

  

**HackSysTeam极其脆弱的驱动程序池溢出**

触发驱动程序池溢出漏洞的IOCTL代码很容易找到，****** HACKSYS_EVD_IOCTL_POOL_OVERFLOW
******记录后随即进行的函数调用是明显的目标。

查看处理程序函数后可知，其在非分页池上进行大小为0x1F8字节的池分配（edi 在函数的开始与自身xor）。

如果分配成功，则处理程序将数据从用户提供的缓冲区复制到池中。然而，复制的数据量由IOCTL中提供的大小控制。

这意味着，如果一个调用者提供的长度大于0x1F8个字节，就会发生越界写入，这也可称为池溢出。我们将再次启用特殊池，从而使触发漏洞更容易。

以下代码将提供一个IOCTL请求，其将在池分配结束后写入4个字节，这应该导致其访问标记为不可访问的页面，并导致系统蓝屏。

编译然后运行，我们得到了我们想要的。

调试崩溃后可以看到，和预期的一样，驱动程序尝试在分配结束后写入。

查看崩溃详情后可知，其是在我们之前在HACKSYS_EVD_IOCTL_POOL_OVERFLOW处理程序中看到的rep movs指令处崩溃。

检查损坏的内存地址后可以看到，和预期一样，一连串0x41字节后是无法访问的内存。

**  
**

**池溢出池风水**

与UAF利用一样，我们需要能确保我们的内存在分配时位置正确。在这种情况下，我们要确保另一个对象在内存中紧随其后。这一次，我们分配的内存大小为0x200字节（0x1F8
+
8字节header），Reserve对象分配总大小为60个字节，这太小，并清楚地分开了我们想使其不切实际的数量，但是，我们之前看过的Event对象是0x40字节的分配。这一清楚的划分分配到8是理想的。

为了修整堆，这次我们再次使用Event对象对其进行碎片整理，然后我们将分配大量连续的Event对象，并以8个块的形式释放它们。这应该使我们获得分配200字节的模式，然后分配非分页池内存。下面的代码在触发调试器中断之前执行池修饰，这样我们可以检查它是否有效。

这个运行后我们便可看到打印的指针值，然后按下Enter键触发断点。

在内核调试器中，我转储了句柄信息以获取对象的详细信息。

查看对象分配周围的池内存，可以看到一个很好的重复模式——8个分配的事件对象，随后是8个空闲的事件对象，与计划的完全一致。

现在我们可以触发我们的溢出，40字节的Event对象肯定将跟随我们控制的内存，所以我们可以开始整合利用方法。

  

**池溢出利用第一回合**

现在我们可以可靠地覆盖一个Event对象的header，我们需要实际覆盖一些东西。我将使用两种不同的方法，一种是最初在“[Windows 7
内核池利用](https://media.blackhat.com/bh-dc-11/Mandt/BlackHat_DC_2011_Mandt_kernelpool-wp.pdf)”中讨论的，另一种是在“[纯数据Pwning微软Windows内核：微软Windows
8.1内核池溢出利用](https://www.blackhat.com/docs/us-14/materials/us-14-Tarakanov-Data-Only-Pwning-Microsoft-Windows-Kernel-Exploitation-Of-Kernel-Pool-Overflows-On-Microsoft-Windows-8.1.pdf)”中讨论的。首先，我将使用Object Type索引覆盖技术。  

如[Code
Machine博文](http://codemachine.com/article_objectheader.html)中所述，Windows内核内存中的每个对象都由几个结构以及对象结构本身组成。第一个是我们之前讨论的POOL_HEADER结构。以下是一个Event对象的例子，这次我们不会破坏该结构，所以当我们在内存中进一步重写另一个结构时，我们将重用我们的利用方法中的值，以使其保持原样。

接下来有一个或多个可选结构，存在哪些可选结构可通过查看出现在实际对象OBJECT_HEADER之前的最后一个结构找到。来自Event对象的示例OBJECT_HEADER布局如下所示：

InfoMask字段只有0x8位设置，这意味着，如Code
Machine文章中所述，池header和对象header之间的唯一可选结构是OBJECT_HEADER_QUOTA_INFO。该文章还告诉我们，其大小为0x10字节，所以我们可以通过回看0x10字节在内存中查看它。

OBJECT_HEADER结构是我们将破坏的结构，所以当我们覆盖这个结构时，我们将使用其默认值使其保持原样。

OBJECT_HEADER结构包含用于管理对象的对象元数据，用于指示可选header、存储调试信息等。如Nikita的幻灯片中所述，该header包含“TypeIndex”字段，这用作ObTypeIndexTable（用于存储指向OBJECT_TYPE结构的指针，这些结构提供有关每个内核对象的重要细节）的索引。查看Windbg中的ObTypeIndexTable，我们可以看到条目。

将条目0xc视作OBJECT_TYPE结构使我们获得以下内容：

所以我们肯定有正确的对象类型，但没有什么可以明显让我们实现代码执行。进一步查看结构后我们看到TypeInfo字段，在windbg中更仔细检查该字段后发现了一系列很好的函数指针。

这意味着正根据结构跳转到函数。如果我们可以控制其中的一个，我们应该能够让内核在我们选择的地址处执行shellcode。通过回看可以看到，
ObTypeIndexTable的第一个条目是一个NULL指针，所以我们用0覆盖OBJECT_HEADER中的TypeIndex字段，然后，当内核尝试执行时，内核应该尝试从NULL页面读取函数指针。因为我们是在Windows
7 32位上执行此操作，所以我们可以分配NULL页，从而可以控制内核执行跳转到的位置，这样我们便可使用与我之前所用相同的shellcode来提升我们的权限。

现在我们要覆盖TypeIndex字段，保持缓冲区末尾和和Event对象之间的所有其他字段不变。我们从增加我们之前使用的InBuffer的大小开始。额外的0x28字节将覆盖POOL_HEADER（0x8字节）、OBJECT_HEADER_QUOTA_INFO（0x10字节）及OBJECT_HEADER，直到并包括TypeIndex（0x10字节）。

首先，我们使用之前看到的默认值覆盖POOL_HEADER和OBJECT_HEADER_QUOTA_INFO结构。

最后，我们覆盖了OBJECT_HEADER结构，主要使用其默认值，但TypeIndex值设置为0。

现在让我们运行代码（确保特殊池已禁用），我们应该会得到因内核尝试在地址0x0处访问OBJECT_TYPE结构而导致的崩溃。我立即在我附带的调试器中获得了一个BugCheck，在发生异常的时候查看指令和寄存器，我们看到的正是我们所希望的。

一个名为ObpCloseHandleTableEntry的函数在尝试从ebx+0x74读取内存时出错（ebx为0）。这应对应于OBJECT_TYPE结构中的DeleteProcedure条目（如果其按照计划从NULL页读取）。现在我们只需要使用与本系列中之前使用的相同的方法分配NULL页，并设置一个函数指针偏移量，以指向我们的令牌窃取shellcode。

在main的开始添加了以下代码，以分配NULL页。

成功分配NULL页后，我们只需要放置一个指向我们的shellcode的指针，以代替其中一个函数指针。我尝试在每个函数的偏移量处放置一个shellcode指针，发现Delete、OkayToClose及Close程序会导致shellcode以一种直接的方式被执行。我决定覆盖Delete程序，因为b33f使用了[OkayToClose](http://www.fuzzysecurity.com/tutorials/expDev/20.html)，Ashfaq使用了[Close](https://github.com/hacksysteam/HackSysExtremeVulnerableDriver/blob/master/Exploit/PoolOverflow.c)。

最后，我们需要稍微修改shellcode，因为Delete程序预期4字节的参数需要从栈中删除，以避免事情变得不稳定。将ret
4;添加到shellcode的末尾即可搞定。最后，在我们开始整理内存前，添加一个不错的system("calc.exe");。现在我们再次运行代码，应该会得到一个作为SYSTEM运行的计算器，如下所示。

漏洞利用的最终/完整代码见[Github](https://github.com/sam-b/HackSysDriverExploits/blob/master/HackSysPoolOverflowObjectTypeOverwrite/HackSysPoolOverflowObjectTypeOverwrite/HackSysPoolOverflowObjectTypeOverwrite.cpp)。

  

**池溢出利用第二回合**

我将使用的利用该漏洞的第二种技术是PoolIndex覆盖技术——作为例子在“[Windows 7
内核池利用](https://media.blackhat.com/bh-dc-11/Mandt/BlackHat_DC_2011_Mandt_kernelpool-wp.pdf)”中使用，并在“[First Dip Into
the Kernel Pool : MS10-058](http://doar-e.github.io/blog/2014/03/11/first-dip-into-the-kernel-pool-ms10-058/)”中通过示例代码使用。  

这次我们只覆盖相邻Event对象的POOL_HEADER结构，所以我们的缓冲区可以小一些。

我们将要覆盖的字段是PoolIndex字段。默认情况下，Windows
7主机将只有一个非分页池，这意味着该字段将不会被实际使用。所以首先我们将覆盖PoolType字段，使块看起来是分页池的一部分。如前所述，该字段中需要的值可以在POOL_TYPE枚举中找到，最终为3。

PoolIndex字段用于索引 nt!ExpPagedPoolDescriptor
数组，以便在对象被释放时为其找到正确的PoolDescriptor。查看windbg中的数组可以看到：

你会注意到，仅前五个条目是有效的指针，其余的是NULL，这意味着，如果我们用大于或等于5的值覆盖POOL_HEADER的PoolIndex字段，当对象被释放时，内核将尝试从NULL页开始引用
一个POOL_DESCRIPTOR。像以前一样，我们可以从用户空间分配NULL页，并以可以实现代码执行的方式设置结构值。首先，我们来覆盖PoolIndex字段，并确保内核按预期崩溃。

现在编译并运行二进制文件，我们得到了崩溃。

内核成功崩溃，尝试在释放池分配时访问0x0 + 0x80地址的内存。现在我们如何从控制池描述符转到代码执行？

如前所述，池描述符包括一个PendingFrees列表，如果其包含32个或更多条目，其将被释放。通过伪造一个Pool
Descriptor对象，我们可以使PendingFrees列表指向我们控制的伪池分配，如果我们将PendingFreesDepth设置为32或更多，则内核将尝试释放它们。释放的对象地址将被添加到ListHeads列表中，通过在该列表中创建指向要覆盖的目标地址的伪条目，刚刚被释放的伪对象的地址将被写到ListHeads列表中第一个条目的Blink地址。

这使我们可将受控用户模式地址写入内存中的任何地址。现在，我们让内核将伪对象地址写到0x41414141。

希望一些代码会使这个更清楚。所有这些代码都放在池喷射代码之前。

首先我们像之前一样分配NULL页。

现在我们需要从0x0开始创建伪POOL_DESCRIPTOR结构。我基本上是通过逆向[Jeremy的解决方案](http://doar-e.github.io/blog/2014/03/11/first-dip-into-the-kernel-pool-ms10-058/)来说明如何做到这一点，所以我使用了他的值。

最后我们在0x1208创建伪块，相应的POOL_HEADER需要为0x1200。

0x1208处的内存是一个NULL指针，这一事实意味着DeferedFree将释放它然后停止，因为没有后续条目。

我们还需要在对象释放后立即创建另一个伪POOL_HEADER，因为当内存管理器释放前一个块时，其将验证其大小是否等于下一个块前一个大小字段。

现在构建和运行代码，我们得到了预期的错误。

这里我们可以看到，0x1208由ExDeferredFreePool写入[esi+4]，等于0x41414141。现在我们需要覆盖内存中的一些内容，这让我们可实现代码执行。为此，我选择覆盖HalDispatchTable中的一个条目，和我利用[任意覆盖漏洞](https://samdb.xyz/windows-kernel-exploitation-part-6-arbitary-overwrite-null-pointer-type-confusion-and-integer-overflow-examples/)时一样。

一旦条目被覆盖，触发正确的函数将导致使用分派表条目和内核代码执行被重定向到伪池分配之前的位置(0x1208)。

首先，我们需要找到HalDispatch表地址和我们要覆盖的目标条目，在这种情况下是ntdll中的NtQueryIntervalProfile函数被调用时使用的第二个条目。

接下来我们更新伪ListHeads条目，以指向 where。

最后，我们在0x1208处放置一个0xcc字节（int
3操作码）来触发断点，并增加一个对NtQueryIntervalProfile的调用，以便在我们清理所有东西后调用该函数。放置0xCC字节的原因是，如果不这样做，0x1208处的字节是clc（0xf8）的操作码，后跟ret（0xc3），这意味着什么都不会发生，操作系统保持正常。

我们还没有设置我们的shellcode，但现在我们应该可在0x1208处实现代码执行。再次运行代码，我们得到了这一结果。

最后一步是设置shellcode。执行将从0x1208开始，所以我们不能只是在此处放置一个指针，相反，我们在调用NtQueryIntervalProfile之前设置了以下数据。

现在重新编译并运行代码，我们得到如下结果：

该漏洞利用的最终/完整代码见[Github](https://github.com/sam-b/HackSysDriverExploits/blob/master/HackSysPoolOverflowTypeIndexOverwrite/HackSysPoolOverflowTypeIndexOverwrite/HackSysPoolOverflowTypeIndexOverwrite.cpp)。

本文翻译自samdb.xyz [原文链接](https://samdb.xyz/windows-kernel-exploitation-part-4/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **小黑** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/86380](/post/id/86380)

安全客 - 有思想的安全新媒体

本文转载自: [samdb.xyz](https://samdb.xyz/windows-kernel-exploitation-part-4/)

如若转载,请注明出处： <https://samdb.xyz/windows-kernel-exploitation-part-4/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p2.ssl.qhmsg.com/dm/200_200_100/t00df551a583a87f4e9.jpg) 小黑

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

