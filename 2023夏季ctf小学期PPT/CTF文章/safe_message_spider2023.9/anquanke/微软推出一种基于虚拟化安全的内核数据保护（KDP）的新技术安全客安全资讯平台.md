# 微软推出一种基于虚拟化安全的内核数据保护（KDP）的新技术

阅读量 **254931**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-07-13 14:45:34

 **x**

##### 译文声明

本文是翻译文章，文章原作者 Base Kernel Team，文章来源：microsoft.com

原文地址：<https://www.microsoft.com/security/blog/2020/07/08/introducing-kernel-data-protection-a-new-platform-security-technology-for-preventing-data-corruption/>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t01286a5a29933386fc.png)

攻击者面对代码完整性(Code Integrity, CI)和控制流保护(Control Flow Guard,
CFG)等防止内存损坏的安全技术时，通常会将他们的重心转向数据损坏。攻击者使用数据破坏技术来攻击系统安全策略、升级特权、篡改安全认证、修改
“initialize once” 数据结构等等。

内核数据保护（KDP）是一种新的技术，它通过[虚拟化安全](https://docs.microsoft.com/en-us/windows-hardware/design/device-experiences/oem-vbs)的技术保护Windows内核和驱动程序的一部分来防止数据损坏攻击。KDP提供了一组API可将一些内核内存标记为只读，从而防止攻击者修改受保护的内存。例如，我们已经看到攻击者使用经过签名但易受攻击的驱动程序来攻击策略数据结构并安装未经签名的恶意驱动程序。KDP通过确保策略数据结构不会被篡改来减轻此类攻击。

将内核内存保护为只读的概念在Windows内核、收件箱组件、安全产品甚至第三方驱动程序（如反作弊和数字版权管理（DRM）软件）等方面具有重要的应用价值。

KDP除了可以增加应用程序的安全性保护程序不被篡改外，还包含了以下的好处：

    
    
    1. 性能改进——KDP减轻了认证组件的负担，不再需要定期验证已写保护的数据变量
    2. 可靠性改进——KDP使诊断内存损坏错误变得更容易，而这些错误不一定代表安全漏洞
    3. 为驱动程序开发人员和供应商提供激励，以提高与基于虚拟的安全性的兼容性，改善生态系统中这些技术的采用
    

KDP使用在[ Secured-core PCs](https://www.microsoft.com/en-us/windowsforbusiness/windows10-secured-core-computers?SilentAuth=1)上默认支持的技术，
Secured-core
PCs实现了一组特定的设备需求，这些需求将隔离和最小信任的安全最佳实践应用到支撑Windows操作系统的技术上。KDP通过为敏感的系统配置数据增加另一层保护，增强了由组成
Secured-core PCs的特性所提供的安全性。

在这个博客中，我们将分享关于内核数据保护如何工作以及如何在Windows10上实现的技术细节，目的是激励和授权驱动程序开发人员和供应商充分利用这项旨在应对数据损坏攻击的技术。

## 内核数据保护：概述

在VBS环境中，正常的NT内核在名为VTL0的虚拟化环境中运行，而安全内核在名为VTL1的更安全、更隔离的环境中运行。有关VBS和安全内核的更多详细信息可以在[这里](https://channel9.msdn.com/Blogs/Seth-Juarez/Isolated-User-Mode-in-Windows-10-with-Dave-Probert)和[这里](https://channel9.msdn.com/Blogs/Seth-Juarez/Windows-10-Virtual-Secure-Mode-with-David-Hepkin)找到。KDP旨在保护Windows内核中运行的驱动程序和软件（即OS代码本身）免受[数据驱动](https://channel9.msdn.com/Blogs/Seth-Juarez/Windows-10-Virtual-Secure-Mode-with-David-Hepkin)的攻击。它分为两个部分实现：

    
    
    1. 静态KDP使在内核模式下运行的软件能够静态地保护它自己映像的一部分不被VTL0中的任何其他实体篡改。
    2. 动态KDP帮助内核模式软件从“安全池”分配和释放只读内存。从池返回的内存只能初始化一次。
    

由KDP管理的内存总是由安全内核(VTL1)进行验证，并由hypervisor使用第二级地址转换(SLAT)表进行保护。因此，在NT内核(VTL0)中运行的任何软件都不能修改受保护内存的内容。

最新的Windows 10 Insider
Build中已经提供了动态KDP和静态KDP，除了可执行页面之外，可以使用任何类型的内存。可执行页面的保护已经由hypervisor-protected
code integrity
(HVCI)提供，它阻止任何非签名内存成为可执行内存，并授予W^X(可写或可执行的页面，但不能同时授予二者)条件。本文未介绍HVCI和W ^
X条件（有关更多详细信息，请参阅即将出版的新的Windows Internals书籍）。

## 静态KDP

如果驱动程序希望通过静态KDP保护其映像的一部分，则应调用MmProtectDriverSection API，该API原型如下：

    
    
    NTSTATUS MmProtectDriverSection (PVOID AddressWithinSection, SIZE_T Size, ULONG Flags)
    

驱动程序指定位于数据段内的地址，还可以指定受保护区域的大小和某些标志。在撰写本文时，“size”参数被保留以备将来使用：地址所在的整个数据段将始终受到API的保护。

如果函数成功执行，则支持静态部分的内存对于VTL0变为只读，并通过SLAT进行保护。

并且不允许卸载具有受保护部分的驱动程序，否则将导致蓝屏错误。然而，我们也考虑到了有时驱动应该能够卸载。因此，我们引入了MM_PROTECT_DRIVER_SECTION_ALLOW_UNLOAD标志位，如果调用者指定了它，系统将能够卸载目标驱动程序，这意味着在本例中，受保护的部分将首先不受保护，然后由NtUnloadDriver释放。

## 动态KDP

动态KDP允许驱动程序使用安全池提供的服务分配和初始化只读内存，安全池由安全内核管理。使用者首先创建与标记关联的安全池上下文。使用者未来的所有内存分配都将与创建的安全池上下文相关联。在创建了上下文之后，可以通过对ExAllocatePool3
API的一个新的扩展参数执行只读分配:

    
    
    PVOID ExAllocatePool3 (POOL_FLAGS Flags, SIZE_T NumberOfBytes, ULONG Tag, PCPOOL_EXTENDED_PARAMETER ExtendedParameters, ULONG Count);
    

然后，调用者可以指定分配的大小和初始缓冲区，以便在POOL_EXTENDED_PARAMS_SECURE_POOL数据结构中复制内存。在VTL0中运行的任何实体都不能修改返回的内存区域。此外，在分配时，调用者提供一个标记和一个cookie值，它们被编码并嵌入到分配的内存中。使用着可以在任何时候验证地址是否在为动态KDP分配保留的内存范围内，以及预期的cookie和标记是否已经编码到给定的内存中。

这允许调用者检查其指向安全池分配的指针没有被不同的分配切换。

与静态KDP类似，动态KDP默认情况下不能释放或修改内存区域。但调用者可以在分配时使用SECURE_POOL_FLAGS_FREEABLE(1)和SECURE_POOL_FLAG_MODIFIABLE(2)标志来指定分配的内存是否是可释放和可修改的。

使用这些标志会降低分配的安全性，但允许在泄漏所有分配都不可行的情况下使用动态KDP内存，例如在计算机上为每个进程进行的分配。

## windows10 上的KDP如何实现

如前所述，静态KDP和动态KDP都依赖于hypervisor中SLAT保护的物理内存。当处理器支持SLAT时，它使用[另一层进行内存地址转换](https://en.wikipedia.org/wiki/Second_Level_Address_Translation)。

###  二级地址转换（SLAT）

当hypervisor启用SLAT支持，并且VM在VMX非root模式下执行时，处理器将一个名为Guest virtual
address（GVA，或ARM64中的stage 1 virtual address）的初始虚拟地址转换为名为Guest physical
address（GPA或ARM64中的IPA）的中间物理地址。这种转换仍然由页表管理，有Guest操作系统管理的CR3控制寄存器寻址。转换的最终结果返回给处理器一个GPA，并在Guest页表中指定访问保护。请注意，只有在内核模式下运行的软件才能与页表交互。rootkit通常在内核模式下运行，并且确实可以修改中间物理页的保护。

hypervisor使用扩展(或嵌套)页表帮助处理器转换GPA。在非slat系统上，当TLB中没有虚拟地址时，处理器需要查阅层次结构中的所有页表，以重建最终的物理地址。如下图所示，虚拟地址被分成四个部分(在LA48系统上)。每个部分表示层次结构页表中的索引。初始PML4表的物理地址由CR3寄存器指定。这解释了为什么处理器总是能够转换地址并获得层次结构中下一个表的下一个物理地址。需要注意的是，在层次结构的每个页表条目中，NT内核通过一组属性指定了一个页保护。只有在每个页表条目中指定的保护的总和允许的情况下，才可以访问最终的物理地址。

![](https://www.microsoft.com/security/blog/wp-content/uploads/2020/07/kernel-data-protection-kdp-fig1-X64-Stage-1-address-translation-Virtual-address-to-guest-physical-address.png)

当SLAT打开时，需要将Guest的CR3寄存器中指定的中间物理地址转换为真实的系统物理地址(SPA)。机制类似:hypervisor将表示当前执行VM的活动虚拟机控制块(VMCB)的nCR3字段配置为嵌套(或扩展)页表的物理地址(注意，该字段在Intel体系结构中称为“EPT
pointer”)。嵌套页表是以类似于标准页表的方式构建的，因此处理器需要扫描整个层次结构以找到正确的物理地址，如图2所示。在图中，“n”表示层次结构中嵌套的页表，由hypervisor管理，而“g”表示Guest页表，由NT内核管理。

![](https://www.microsoft.com/security/blog/wp-content/uploads/2020/07/kernel-data-protection-kdp-fig-2-X64-Stage-2-physical-address-translation-GPA-to-SPA.png)

如图所示，Guest虚拟地址到系统物理地址的最终转换需要两种转换类型：GVA到GPA（由Guest
VM的内核配置）和GPA到SPA（由hypervisor配置）。请注意，在最坏的情况下，转换涉及所有四个页面层次结构级别，这将导致20个表查找。该机制可能会很慢，并通过处理器对增强TLB的支持来缓解。在TLB条目中，还包含了另一个标识当前正在执行的VM的ID（在Intel系统中称为虚拟处理器标识符或VPID，在AMD系统中称为地址空间ID或ASID），因此处理器可以缓存属于两个不同VM的虚拟地址的转换结果，而不会发生任何冲突。

![](https://www.microsoft.com/security/blog/wp-content/uploads/2020/07/kernel-data-protection-kdp-fig3-Nested-entry-of-an-NPT-page-table-in-the-hierarchy.png)

如上图所示，一个NPT条目指定了多个访问保护属性。这允许hypervisor进一步保护系统物理地址（除了hypervisor本身之外，任何其他实体都不能访问NPT）。当处理器试图读、写或运行NPT不允许访问的地址时，会引发NPT冲突（Intel体系结构中的EPT冲突），并生成VM出口。NTP违反生成的VM退出并不经常发生。通常，它是在嵌套配置中产生的，或者在HVCI中使用MBEC软件时产生的。如果由于其他原因而发生不扩散冲突，Microsoft
Hypervisor将向当前虚拟处理器(VP)注入访问冲突异常，该虚拟处理器由Guest操作系统以不同的方式管理，但如果没有异常处理程序选择处理该异常，则通常通过错误检查进行管理。

###  静态KDP实现

SLAT保护是允许KDP存在的主要原理。在Windows中，动态和静态KDP实现是相似的，它们都由安全内核管理。安全内核是唯一能够向hypervisor发出ModifyVtlProtectionMask
hypercall的实体，其目标是修改映射在较低VTL0中的物理页面的SLAT访问保护。

对于静态KDP，NT内核验证驱动程序不是会话驱动程序或映射了大页面。如果存在这些条件之一，或者该节是可丢弃的节，则不能应用静态KDP。  
如果调用MmProtectDriverSection
API的实体没有请求目标映像不可加载，则NT内核将执行对安全内核的第一次调用，该内核将锁定与驱动程序关联的正常地址范围（NAR）。

“pinning”操作防止驱动程序的地址空间被重用，使驱动程序不可卸载。然后，NT内核将属于该部分的所有页面放入内存，并使它们私有化（即原型pte没有寻址）。

然后，在叶PTE结构中，页面被标记为只读（在图2中突出显示为“gPTE”）。在这个阶段，NT内核最终可以通过SLAT调用安全内核来保护底层物理页面。安全内核分两个阶段应用保护：

    
    
    1. 通过在数据库中添加适当的NTEs(普通表地址)并更新属于VTL1的底层安全pfn，注册属于该节的所有物理页并将它们标记为“属于VTL0”。这允许安全内核跟踪物理页面，这些页面仍然属于NT内核。
    2. 对VTL0 SLAT table应用只读保护。hypervisor为每个VTL使用一个SLAT表和VMCB。
    

目标Image的部分现在受到保护。VTL0中的任何实体都不能写入属于该节的任何页。如前所述，这个场景中的安全内核保护了一些最初由VTL0中的NT内核分配的内存页。

## 动态KDP实现

动态KDP使用新段堆提供的服务从安全池中分配内存，该池几乎完全由安全内核管理。

在引导过程的早期阶段，NT内存管理器计算安全池使用的512GB区域的随机虚拟基址，该区域恰好跨越256个内核PML4条目中的一个。在第1阶段的后期，NT内存管理器会发出一个安全调用，其内部名为INITIALIZE_SECURE_POOL，其中包括计算过的内存区域，并允许安全内核初始化安全池。

安全内核创建一个NAR，表示属于不安全NT内核的整个512GB虚拟区域，并初始化属于NAR的所有相对NTEs。安全内核中的安全池虚拟地址空间是256GB，这意味着它的PML4映射与一些其他内容共享，并且与NT相比不在相同的基址上。因此，在初始化安全池描述符时，安全内核还会计算一个增量值，即安全内核中的安全池基址与NT内核中保留的基址之间的差值（如下图所示）。这很重要，因为它允许安全内核向NT内核指定映射属于安全池的物理页面的位置。

![](https://www.microsoft.com/security/blog/wp-content/uploads/2020/07/kernel-data-protection-kdp-fig4-The-Secure-Pool-VTL1-to-VTL0-DELTA-value.png)

当运行在VTL0内核中的软件请求从安全池分配一些内存时，对安全内核进行安全调用，该安全调用调用内部的RtlpHpAllocateHeap函数，该函数在两个VTLs中都公开。如果段堆计算出安全池中已经没有空闲内存段了，它就调用SkmmAllocatePoolMemory例程，该例程为池分配新的内存页。如果不需要，堆总是试图避免提交新的内存页。

与NT内核公开的NtAllocateVirtualMemory API一样，SkmmAllocatePoolMemory
API支持两种操作:保留和提交。保留操作允许安全内核的内存管理器保留池分配所需的一些pte。提交操作实际上分配空闲的物理页。

物理页面是从属于安全内核(其安全pfn处于安全状态)的一组空闲页面中分配的，并映射到VTL 1的页表中，这意味着分配了所有VTL
1分页表层次结构。与静态KDP一样，安全内核向hypervisor发送“ModifyVtlProtectionMask”的调用。其目标是将VTL0
SLAT表中的物理页映射为只读。VTL0可以访问这些页面之后，安全内核将复制调用者指定的数据并回调NT。

NT内核使用内存管理器提供的服务来映射VTL0中的客户物理页面。请记住，VTL0和VTL1的整个root分区物理地址空间都映射为标识映射，这意味着在VTL0中有效的客户物理页码在VTL1中也有效。安全内核要求NT内存管理器通过准确地知道应该将页面映射到哪个虚拟地址来映射属于安全池的页面。这要感谢之前在阶段1中计算的增量值(图4)。

分配返回给VTL0中的调用者。与静态KDP一样，底层页面不再可以从VTL0中的任何实体写入。

精明的读者会注意到，上面对KDP的描述只涉及为支持给定受保护内存区域的Guest物理地址建立SLAT保护。KDP不强制保护区域的虚拟地址范围映射是如何转换的。今天，安全内核只定期验证受保护内存区域是否转换为适当的、受SLAT保护的GPA。KDP的设计允许将来扩展对受保护内存区域的地址转换层次结构进行更直接的控制。

## KDP在inbox组件中的应用

为了演示KDP如何为两个inbox组件提供价值，我们将着重介绍在CI.dll和[Windows Defender System
Guard](https://www.microsoft.com/security/blog/2018/04/19/introducing-windows-defender-system-guard-runtime-attestation/) 的具体实现

首先,CI.dll使用KDP的目的是在初始化（即从注册表读取或在启动时生成）后保护内部策略状态。这些数据结构对于保护至关重要，就好像它们被篡改了一样——一个经过适当签名但易受攻击的驱动程序可能会攻击策略数据结构，然后在系统上安装一个未签名的驱动程序。使用KDP可以确保策略数据结构不会被篡改，从而减轻这种攻击。

其次，Windows Defender System
Guard为了提供运行时证明，认证代理只允许连接到证明驱动程序一次。这是因为状态存储在VTL1存储器中。驱动程序将连接状态存储在其内存中，需要对其进行保护，以防止攻击尝试使用可能被篡改的代理重置连接。KDP可以锁定这些变量，并确保只能在代理和驱动程序之间建立一个连接。

代码完整性和Windows Defender System Guard是 Secured-core
PCs机的两个关键特征。KDP增强了对这些重要安全系统的保护，使得攻击者的攻击变得更困难。

这些只是几个示例，说明将内核和驱动程序内存保护为只读对于系统的安全性和完整性是多么有用。随着KDP被更广泛地采用，我们希望能够扩大保护的范围，因为我们希望更广泛地保护数据破坏攻击。

## KDP入门

除了运行基于虚拟化的安全性所需的需求外，动态和静态KDP都没有任何进一步的要求。在理想情况下，VBS可以在任何支持以下操作的计算机上启动：

    
    
    1. 英特尔、AMD或ARM虚拟化扩展
    2. 二级地址转换:AMD的NPT, Intel的EPT, ARM的第二阶段地址转换
    3. 可选的硬件MBEC，它降低了与HVCI相关的性能成本
    

更多关于VBS要求的信息可以在[这里](https://docs.microsoft.com/en-us/windows-hardware/design/device-experiences/oem-vbs)找到。在[ Secured-core
PCs](https://www.microsoft.com/en-us/windowsforbusiness/windows10-secured-core-computers?SilentAuth=1)上，支持基于虚拟化的安全性，默认情况下启用硬件支持的安全功能。客户可以从各种合作伙伴供应商处找到安全的核心PC，这些产品具有全面的安全功能，这些功能现在由KDP增强。

本文翻译自microsoft.com
[原文链接](https://www.microsoft.com/security/blog/2020/07/08/introducing-kernel-data-protection-a-new-platform-security-technology-for-preventing-data-corruption/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **jux1a** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/210206](/post/id/210206)

安全客 - 有思想的安全新媒体

本文转载自:
[microsoft.com](https://www.microsoft.com/security/blog/2020/07/08/introducing-kernel-data-protection-a-new-platform-security-technology-for-preventing-data-corruption/)

如若转载,请注明出处： <https://www.microsoft.com/security/blog/2020/07/08/introducing-kernel-data-protection-a-new-platform-security-technology-for-preventing-data-corruption/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [操作系统](/tag/操作系统)

 **+1** __2赞

 __收藏

![](https://p1.ssl.qhimg.com/t01c900f6a705a10464.png) jux1a

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

