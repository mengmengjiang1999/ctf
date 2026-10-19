## **概要**

在研究 win32k 模块的 uaf 漏洞时，最重要的一点就是，了解目标对象整个生命周期的状态转换过程，尤其是哪些行为会触发 ref 的增加，哪些行为会导致
ref 的减少，甚至部分场景会使得内核不考虑 ref 值直接 free 目标对象。本文旨在探讨这样一种场景导致的 uaf 漏洞：内核没有正确处理 gdi
对象的所有权问题，使得 gdi 对象在被引用的状态下仍然被 free，从而导致 uaf（本文分析调试的目标系统为 win7x86）。

##  **相关知识**

Win32k 中 gdi 对象通常有如下几种所属关系：

#define OBJECT_OWNER_ERROR ( 0x80000022)

#define OBJECT_OWNER_PUBLIC ( 0x00000000)

#define OBJECT_OWNER_CURRENT ( 0x80000002)

#define OBJECT_OWNER_NONE ( 0x80000012)

  

其中最值得关注的是 OBJECT_OWNER_CURRENT 和 OBJECT_OWNER_PUBLIC，OBJECT_OWNER_PUBLIC 代表的该
gdi 对象并不从属于某个进程，而 OBJECT_OWNER_CURRENT 则代表该 gdi 对象属于当前进程（在 setowner 时
OBJECT_OWNER_CURRENT 会转换为当前进程 id），当 win32 进程结束退出时会调用
NtGdiCloseProcess，该函数主要作用便是清理各类属于本进程的 gdi 对象，释放它们所占据的系统资源：

  
![](https://image.3001.net/images/20210104/1609728430_5ff281ae41ab98800f6bf.png!small)  

上图中 v2 代表的是触发资源清理操作的原因，1-进程结束；2-会话结束，我们可以看到当进程退出时，会先调用
ultiUserGreCleanupHmgOwnRemoveAllLocks 函数清理相应类型对象的锁，然后调用 vCleanup* 清理相应的 gdi
对象，MultiUserGreCleanupHmgOwnRemoveAllLocks 函数的参数则代表相应的 gdi 对象类型，如 5 对应于 bitmap
对象，4 对应于 regions 对象，我们进一步看看 MultiUserGreCleanupHmgOwnRemoveAllLocks 函数做了什么：

![](https://image.3001.net/images/20210104/1609728449_5ff281c1a2aecbe890444.png!small)  

可以看到系统在遍历 gdi 对象的句柄表，对于属于当前进程的 gdi 对象，主动清零它们的引用计数和锁计数，那么我们可以抽象出这样一种漏洞模型，存在 gdi
对象 A，先通过某些操作使得系统中的其他对象保持着对 gdi 对象 A 的引用，接着关键点在于设法使得对象 A 的所有者属性变为
OBJECT_OWNER_CURRENT 从属于进程 P1（并且引用对象 A 的对象在对象 A 释放前不受进程 P1 退出的影响），那么当 P1
进程退出时，便会释放对象 A，而内核中依旧保存着对象 A 的引用，这样便构造了一个典型的 uaf
场景，CVE-2015-1722、CVE-2015-1724 CVE-2015-6173、CVE-2016-0094、CVE-2019-0803
等漏洞基本都是这个抽象场景的实例化体现，后文中我们将以 CVE-2015-1722 为示例对这种场景进行分析。

  

##  **CVE-2015-1722 分析**

如下是 CVE-2015-1722 的 POC：

![](https://image.3001.net/images/20210104/1609728476_5ff281dc3eae56fd99097.png!small)  

POC 中 hbmp1 则是前面漏洞模型中的关键的 gdi 对象 A，此时它的 owner 是 POC 进程，“先通过某些操作使得系统中的其他对象保持着对
gdi 对象的引用”，这一步是通过 NtGdiSelectBitmap 来实现的，使得 hdc2 代表的 dc 对象维持了对 hbmp1 代表的
bitmap 对象的引用，“接着关键点在于设法使得对象 A 的所有者属性变为 OBJECT_OWNER_CURRENT 从属于进程 P1”，这一步是先通过
InsertMenu 将 bitmap 和对应的 item 关联，接着通过 SetClipboardData 将 bitmap 的 owner 变为
public 即(0)，最后 postmessage 将 notepad 关闭触发 FreeItemBitmap 操作，在 FreeItemBitmap 中
bitmap的owner 变为 notepad 进程，那么 notepad 在执行完 FreeItemBitmap 便会将 hbmp1 对应的 bitmap
对象释放掉。但是，此时 hdc2 对应的 dc 对象仍然维持了对 hbmp1 的引用，这便是一个典型的 uaf 场景。

仔细思考一下我们最初提炼的漏洞模型，最关键的因素有两点：(1) 系统在修改 gdi 对象的 owner
时并没有考虑该对象是否存在被其他代码引用的情况；(2) win32 进程退出时调用 NtGdiCloseProcess 清理 gdi
对象时太过粗暴，没有考虑到由于 (1) 导致的 uaf 的问题，在 CVE-2019-0803 漏洞之前，微软对于这个模式的漏洞的 patch
都是处于头痛医头，脚痛医脚的状态，简单的删除/修改了会调用 setowner 相关的函数，那么攻击者找到新的 setowner 方法后，patch
便无效了，直到 CVE-2019-0803 的 path 出现，对于 bitmap 对象的该漏洞模型场景进行了完整的校验，整个 patch
分为两部分，setowner 部分增加了对引用计数的校验：

  

![](https://image.3001.net/images/20210104/1609728519_5ff2820726ed299b71671.png!small)  
在引用计数不为 0 时，增加了一个特殊的标志位 0x4000，另一部分是在 NtGdiCloseProcess 处：  
![](https://image.3001.net/images/20210104/1609728530_5ff282122c0f4fb9df57d.png!small)  
对于存在 0x4000 标志位的对象，做了特殊的处理。

  

##  **思考**

随着攻防对抗的不断深入，浅层次的漏洞资源已经是消耗殆尽，在这种情况下更需要从开发者和一个更宏观的角度思考问题：为什么开发者这么设计这个机制？这个机制的利弊是什么？安全边界是什么？什么场景容易出问题？在我们对目标的运行机制有了深入的研究，能够回答上面的问题后，是不是能提炼出一个适应于目标的漏洞场景模型，然后依照这个模型去进行漏洞挖掘，这样是否效率能更高一些呢？就像是早年的
usercallback 和 2019/2020 年大火的服务类提权漏洞。希望本文能给读者带来一些这方面的启发和帮助，也欢迎各位看官拍砖吐槽交流。

