# Osiris 银行木马的下载程序使用了 doppelgänging 技术

阅读量 **224812**

|评论 **3**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-09-04 11:30:27

 **x**

##### 译文声明

本文是翻译文章，文章来源：blog.malwarebytes.com/

原文地址：<https://blog.malwarebytes.com/threat-analysis/2018/08/process-doppelganging-meets-process-hollowing_osiris/>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t01438186e69a0263b7.jpg)

对于恶意软件制作者来说，Holly
Grails框架可以很好的将恶意软件伪装成合法进程，以方便他们逃过杀软的检测来进行攻击。对于研究人员和逆向工程师来说，这种攻击方法也备受关注，因为它同时展示了Windows
API的创新用法。

Process
Doppelgänging技术是在2017年的BlackHat上发布的一项新技术，用于代码注入，据说这种利用方式支持所有Windows系统，能够绕过绝大多数安全产品的检测。
一段时间后，一个名为SynAck的勒索软件就将该技术应用到了恶意行为上，链接地址为：[https://securelist.com/synack-targeted-ransomware-uses-the-doppelganging-technique/85431/。](https://securelist.com/synack-targeted-ransomware-uses-the-doppelganging-technique/85431/%E3%80%82)  
虽然ProcessDoppelgänging的应用在野外仍然很少见，但在最近的Osiris银行特洛伊木马（Kronos的新版本）样本中，我们发现了它的一些攻击特征。
经过仔细检查后可以发现在原技术的基础上，此次的攻击方法有了一定的改进。

译者注：Doppelgänging是Process Hollowing
(RunPE)的一种取代方法。ProcessDoppelgänging和Process
Hollowing都可以在合法的可执行文件的掩护下运行恶意文件。这两者在实现方面有所不同，且使用了不同的API函数。对于Process
Doppelgänging的理解可以参照：<https://hshrzd.wordpress.com/2017/12/18/process-doppelganging-a-new-way-to-impersonate-a-process/>  
在这次的攻击中，攻击者将ProcessDoppelgänging和Process
Hollowing中各自最优秀的的部分进行了合并，创造了一个更加强大恶意软件。 在这篇文章主要叙述了如何在受害机器上用一个有趣的加载器部署Osiris。

## 概述

Osiris分三个步骤进行加载：

  1. 使用ProcessDoppelgänging技术的改进方法所制作的软件进行第一步装载
  2. 使用自我注入方式进行第二步装载
  3. Osiris核心代码执行所有的恶意活动

## 加载其他NTDLL

运行时，初始dropper会创建一个新的挂起进程：wermgr.exe。查看注入进程所加载的模块，我们可以发现多出的NTDLL：  
  
当我们仔细研究这些多出的NTDLL会调用哪些函数时，我们会发现更多有趣的细节：它调用了几个与NTFS事务相关的API。于是很容易猜到，这里采用了ProcessDoppelgänging技术。这是一种众所周知的技术，一些恶意软件的作者会使用这种技术来逃避杀软并且同时隐藏他们所调用的API。  
NTDLL.dll是一个特殊的低级DLL，基本上它只是系统调用的一个包装器，与系统中的其他DLL没有任何依赖关系。由于这个原因，它无需填充其导入表就可以进行加载，而其他系统DLL（如Kernel32.dll）在很大程度上依赖于从NTDLL导出的函数。这就是许多本地监视器可以发现和拦截NTDLL导出的函数的原因：查看正在调用的函数，并检查进程是否进行了可疑活动。  
当然，恶意软件作者也深知这一点，所以为了逃避这种检查机制，他们会从磁盘中加载他们自创的未使用过的NTDLL副本。下面就来介绍一下Osiris银行木马所使用的具体方法：  
在查看内存映射时，我们可以发现附加的NTDLL就像其他普通的DLL一样，会被作为映像加载。这种类型的映射是LoadLibrary函数加载的DLL的典型映射，或者也可能是来自NTDLL的低级版本LdrLoadDll。NTDLL会被默认加载到每个可执行文件中，而且官方的API无法重复加载相同的DLL。通常，恶意软件作者会手动映射第二个副本，但这会提供不同的映射类型，这与正常加载出来的DLL是完全不同的。
在这里，恶意软件的作者使用了以下函数将文件作为一个section加载：

ntdll.NtCreateFile – 打开ntdll.dll文件  
ntdll.NtCreateSection –从该文件中创建一个section  
ntdll.ZwMapViewOfSection –将此section映射到进程地址空间  
  
这个方法很巧妙，因为DLL被映射成了一个映像，所以它看起来像是以正常的方式进行了加载。此DLL会进一步秘密地加载恶意载荷。

## Process Doppelgänging与Process Hollowing的对比

此病毒将载荷注入新进程的方式与Dopplegänging有明显的相似之处。但是，如果经过仔细分析，我们也可以看到这种方法与去年Black
Hat会议中提出的经典实现方法有着不同之处。而这种方法其实更接近于Hollowing技术。  
Process Doppelgänging与Process Hollowing技术类似，不同之处在于前者通过攻击Windows NTFS
运作机制和一个来自Windows进程载入器中的过时的应用。  
经典的Process
Doppelgänging实现方式为（同时利用两种不同的关键功能，以此掩盖已修改可执行文件的加载进程，NTFS事务修改实际上不会写入到磁盘的可执行文件中，而之后使用未公开的进程加载机制实现详情来加载已修改的可执行文件，但不会在回滚已修改可执行文件前执行该操作，其结果是从已修改的可执行文件创建进程，而杀毒软件的安全机制检测不到）：  
  
Process Hollowing实现方式（Process Hollowing是现代恶意软件常用的一种进程创建技术。一般来说，使用Process
Hollowing技术所创建出来的进程在使用任务管理器之类的工具进行查看时，它们看起来是正常的，但是这种进程中包含的所码实际上就是恶意代码）：  
  
此Osiris病毒加载方式：  

## 创建一个新进程

Osiris加载器先会创建它将进行注入的进程。该过程由Kernel32：CreateProcessInternalW中的函数创建。  
  
新进程（wermgr.exe）是在原始文件挂起的状态下创建的，这种行为与Hollowing的行为类似。  
在ProcessDopplegänging算法中，创建新流程会晚很多，并会使用新的API：NtCreateProcessEx：  
  
这种差异很重要，因为在ProcessDoppelgänging中，新进程不是从原始文件创建的，而是从特殊缓冲区（section）创建的。这个section在早期被创建的，并且是使用“不可见”文件在NTFS事务中进行创建的。在Osiris加载器中，这个section也会出现，但顺序是颠倒的，将这两者称为不同的算法也未尝不可。  
创建进程后，相同的映像（wermgr.exe）将映射到加载器的上下文中，就像之前使用NTDLL一样。  
  
后来证明，加载器将修补远程进程。wermgr.exe的本地副本将用于收集有关应用的补丁的位置信息。

## NTFS事务的使用

NTFS事务通常在数据库上运行时会使用到，也以类似的方式存在于NTFS文件系统中。 NTFS事务将一系列操作封装到一个单元中。
在事务内部创建文件时，直到提交事务之前它将不接受任何外部访问。 ProcessDoppelgänging使用它们来创建投放载荷的不可见文件。  
通过分析案例可以发现，他们使用NTFS事务的方法是完全相同的，只有所用的API有着细微的差别。加载程序会创建一个新事务，在该事务中创建一个新文件。最初的实现使用了来自Kernel32的CreateTransaction和CreateFileTransacted。而在这里，他们被低级别的其他方法取代了。  
  
首先，调用来自NTDLL的函数ZwCreateTransaction。然后，作者通过RtlSetCurrentTransaction和ZwCreateFile打开事务处理文件（创建的文件是％TEMP％
Liebert.bmp）。接着dropper将缓冲区写入文件，这里使用了具有ZwWriteFile的RtlSetCurrentTransaction。  
  
可以看到正在写入的缓冲区包含了第二阶段新的PE载荷。对于此技术，文件通常只在事务中可见，不能由其他进程（如AV扫描程序）打开。  
  
此事务文件会创建一个section。而要执行功能的话，只能通过低级API：ZwCreateSection / NtCreateSection来实现。  
  
创建该section后，即不再需要该文件。事务通过ZwRollbackTransaction被回滚，刚刚对文件的更改不会保存在磁盘上。  
因此，上述部分与ProcessDoppelgänging的对应部分是相同的。dropper的作者通过使用从 NTDLL的自定义副本调用的
低级函数的方式使其更加隐秘。  
此时，Osiris dropper创建了两个完全不相关的元素：  
一个进程（此时包含映射的、合法的可执行文件wermgr.exe）  
一个section（从事务处理文件创建并包含恶意载荷）  
如果这是典型的ProcessDoppelgänging则将不会产生上述情况，而是会根据带有映射载荷的部分直接创建进程。  
在恶意作者的两种方法结合点处，如果跟踪执行就可以看到在回滚事务之后，调用了以下函数（格式：RVA;函数）：  
4b1e6;ntdll_1.ZwQuerySection  
4b22b;ntdll.NtClose  
4b239;ntdll.NtClose  
4aab8;ntdll_1.ZwMapViewOfSection  
4af27;ntdll_1.ZwProtectVirtualMemory  
4af5b;ntdll_1.ZwWriteVirtualMemory  
4af8a;ntdll_1.ZwProtectVirtualMemory  
4b01c;ntdll_1.ZwWriteVirtualMemory  
4b03a;ntdll_1.ZwResumeThread  
因此，新创建的部分看起来只是作为附加模块映射到了新进程中。将载荷写入内存并设置为必要的补丁（例如入口点重定向）后，将恢复该过程：  
  
重定向执行的方式类似于Process
Hollowing的变体。远程进程的PEB已打补丁，新模块库也已经被设置为需添加的部分。（由于这个原因，当进程恢复时，导入将自动加载。）  
  
但是，入口点重定向仅由原始模块的入口点地址处的补丁完成。单个跳转重定向到注入模块的入口点：  
  
如果修补入口点失败，则加载程序包含的第二个入口点重定向变体，方法是在线程的上下文中设置新地址（ZwGetThreadContext – >
ZwSetThreadContext），这是Process Hollowing中使用的经典技术：  

## 两全其美的办法（两种技术的结合）

Process Hollowing的薄弱点是关于注入载荷的内存空间上设置的保护权限。Process
Hollowing通过VirtualAllocEx在远程进程中分配内存页，然后在那里写入载荷。它会产生一种不良影响：访问权限（MEM_PRIVATE）与正常加载的可执行文件（MEM_IMAGE）不同。将有效负载加载为映像的主要障碍是需要将其加载在磁盘上，但是一旦这么做就很容易被杀毒软件发现。  
Doppelgänging提供了一种解决方案：不可见的事务处理文件，可以安全地放入载荷而不会被发现。此技术假定事务处理文件将用于创建section（MEM_IMAGE），然后此section将成为新进程的基础（使用NtCreateProcessEx）。  
此解决方案运行良好，但要求所有流程参数必须手动加载：首先通过RtlCreateProcessParametersEx创建它们，然后将它们设置为远程PEB。这使得在64位系统上运行32位进程就变得很困难起来，因为在WoW64进程的情况下，有2个PEB需要填充。  
如果我们像Process
Hollowing那样创建流程，那么ProcessDoppelgänging的那些问题就可以轻松解决。作者使用来自Kernel32的文档化API，从合法文件中创建了一个进程。载有载荷的部分由于加载了适当的访问权限（MEM_IMAGE），可以在后续中被添加，且执行时重定向到它。

## 第二阶段装载

这里的Kernel32的DLL文件(8d58c731f61afe74e9f450cc1c7987be)并非核心部分，仅是加载器的下一个阶段。它唯一的作用是加载最终的有效载荷。步骤是将Osiris核心逐块解压缩，并将其依赖项手动加载到加载器进程中新分配的内存区域。在这次自注入之后，加载器跳转到有效负载的入口点：  
  
有趣的是，应用程序的入口点与标头中保存的入口点不同。因此，如果转储载荷并相互依赖地运行它，则无法执行相同的代码。  
标题中设置的入口点是RVA 0x26840：  
  
该调用会使应用程序进入无限的休眠之中：  
  
而执行恶意软件的真正入口点是0x25386，此入口点仅加载器知晓。  
  
原始的Kronos（2a550956263a22991c34f076f3160b49）也使用了隐藏入口点这种技巧，Kronos最终的载荷被注入进了svchost。通过修补svchost的入口点将执行重定向到核心部分：  
  
在这种情况下，载荷的入口点为RVA
0x13B90，而载荷头中保存的入口点（d8425578fc2d84513f1f22d3d518e3c3）为0x15002。  
  
真正的Kronos入口点的代码与Osiris有相似之处，但是并不完全相同：  

## IOC信息

第1阶段（原始样本）  
e7d3181ef643d77bb33fe328d1ea58f512b4f27c8e6ed71935a2e7548f2facc0  
第2阶段（第二阶段装载机）  
40288538ec1b749734cb58f95649bd37509281270225a87597925f606c013f3a  
Osiris（核心病毒）  
d98a9c5b4b655c6d888ab4cf82db276d9132b09934a58491c642edf1662e831e

本文翻译自blog.malwarebytes.com/ [原文链接](https://blog.malwarebytes.com/threat-analysis/2018/08/process-doppelganging-meets-process-hollowing_osiris/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **呐，你的花花** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/158740](/post/id/158740)

安全客 - 有思想的安全新媒体

本文转载自: [blog.malwarebytes.com/](https://blog.malwarebytes.com/threat-analysis/2018/08/process-doppelganging-meets-process-hollowing_osiris/)

如若转载,请注明出处： <https://blog.malwarebytes.com/threat-analysis/2018/08/process-doppelganging-meets-process-hollowing_osiris/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [恶意软件](/tag/恶意软件)
  * [银行木马](/tag/银行木马)
  * [doppelgänging](/tag/doppelgänging)
  * [Osiris](/tag/Osiris)

 **+1** __3赞

 __收藏

![](https://p0.ssl.qhimg.com/t01605c9b2ce4b35048.png) 呐，你的花花

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

