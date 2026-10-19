# Windows内核对象管理全景解析完结

阅读量 **352240**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-10-23 14:30:28

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t01a07625d9571da527.jpg)

## 0、引言

在前一篇《
Windows内核对象管理全景解析前奏》中，详细讲解了Windows中内核对象管理的“基础”知识，但光有这些基础知识还很难形成知识网，对于内核对象管理的把握可能还不是很到位，这一篇文章就是承接前一篇，为读者构建出Windows内核中对象管理的“宏图伟业”，从一个比较高的层次来把握其本质。

涉及到的知识：  
1、Windows内核对象；  
2、Windows内核对象管理；  
3、Windbg内核调试；  
4、Windbg的常规使用；

## 1、借助工具来宏观的看一下内核对象

有没有什么现成的工具以供浏览当前系统中存在的内核对象呢？最好像Explorer浏览硬盘上的文件夹那样带有目录层次结构的。有，当然有，而且还是微软官方出品的，而且还不止一个。先看看傻瓜式的GUI工具——WinObj.exe。运行效果如下，注意，这个要以管理员权限运行。简单的介绍些该软件所呈现出来的内容。

![](https://p4.ssl.qhimg.com/t0186bf390f04d1be7a.png)

最上边的那个”\”表示的是根对象，Windows内核中的所有其他内核对象都隶属于该对象下。这个有点类似于Linux中的根目录一样。【微软也真是奇怪，又爱又恨吗？】”\”下的层次结构显示出来的便是其他属于同等层次的内核对象，然后依次往复下去，至少你需要明白一点，这些对象的类型都是一样的，尽管你现在还不知道他们到底是哪一种类型。右边显示出来的便是隶属于该目录下的具体的其他对象，对，你没有看错，就是“目录”对象下的其他对象，内核中有一个对象——目录对象，用来管理其他对象，这个就是我前一篇说的，Windows内核中仿照着文件系统实现了一个小型的文件系统来管理内核对象。那么问题来了，这个软件是怎么获取到这些内核对象的呢？换一个问题就是，WinObj.exe调用了哪些API来获取到的呢？再更深层次的挖一下就是，调用的这些API是通过查询什么结构来找到这些数据的呢？ok，这些问题先放一边，我们再来看另一个工具——Windbg。看看他是怎么给我们呢展示出这些信息的，如下：

![](https://p2.ssl.qhimg.com/t017f34aa3044287216.png)

![](https://p5.ssl.qhimg.com/t01082b27cb24366ad3.png)

嗯，虽然给的数据不太好看，但更讲求的是本质。下边我们就要脱离所有的工具，自己手动遍历出所有的内核对象，这样才理解的深刻。

## 2、内核对象管理的基础构建

我们先来再看一下内核对象类型对象数组，找一个比较有意思的类型对象。

![](https://p1.ssl.qhimg.com/t01b86f253267e1e5a7.png)

名字叫“Directory”，其目的昭然若揭，就是用来管理的嘛，管理啥呢？当然是管理其他的“Directory”对象或者其他诸如“Process”、“Thread”等的类型对象。OK了，虚拟文件系统中的第一环已经有了，我们来具体的分析下这个类型对象。

    
    
    0: kd> dt nt!_OBJECT_DIRECTORY
       +0x000 HashBuckets      : [37] Ptr32 _OBJECT_DIRECTORY_ENTRY
       +0x094 Lock             : _EX_PUSH_LOCK
       +0x098 DeviceMap        : Ptr32 _DEVICE_MAP
       +0x09c SessionId        : Uint4B
       +0x0a0 NamespaceEntry   : Ptr32 Void
       +0x0a4 Flags            : Uint4B
    

其中最重要的便是_OBJECT_DIRECTORY_ENTRY了，大家可能第一眼看到是37个的数组，可能心里会犯嘀咕，怎么才37个呢，超过这个数就不能管理了吗？其实不是这样的，来看下这个结构体的具体实现：

    
    
    0: kd> dt nt!_OBJECT_DIRECTORY_ENTRY
       +0x000 ChainLink        : Ptr32 _OBJECT_DIRECTORY_ENTRY
       +0x004 Object           : Ptr32 Void
       +0x008 HashValue        : Uint4B
    

三个字段，

ChainLink：第一个字段是连接着下一个_OBJECT_DIRECTORY_ENTRY，是个单向链表；  
Object：指向该Entry所管理的那个对象，比如EPROCESS，ETHREAD等等；  
HashValue：该Entry的Hash值；

这里需要解释下，这个Hash的具体含义，其实很简单，就是根据某个算法计算出待插入的对象的一个Hash值，这个值完全是为了加快后边根据名字遍历指定对象时，加快查询速度。但请注意，这个Hasn值不能作为核对的唯一标准，因为系统计算这个Hash值的算法并没有保证该Hash的唯一性，所以在校验是否为指定对象时，Hash值的查询知识第一步，后边还会根据待查询的对象名来精确比较。

ObReferenceObjectByName()这个API大家可以自己去逆向分析下。

现在简单叙述下Windows创建一个内核对象的简单过程，看看系统是如何创建内核对象并且是如何和这个nt!_OBJECT_DIRECTORY发生关系的。以创建线程对象为例进行讲解说明。

![](https://p1.ssl.qhimg.com/t01bae9acdb79593e78.png)

![](https://p2.ssl.qhimg.com/t01802534534d0087e9.png)

PspAllocateThread()内部调用了一个非常重要的函数——ObCreateObject()，如下：

![](https://p2.ssl.qhimg.com/t0175101863948c0c61.png)

这里简单解释下PsThreadType这个全局变量，这个其实就是线程类型对象对象，其值与nt!ObpObjectTypes[6]是一样的，如下：

    
    
    0: kd> dd nt!ObpObjectTypes
    83f81aa0  a19378e0 a1937818 a1937750 a1937508
    83f81ab0  a19c2040 a19c2f78 a19c2eb0 a19c2de8
    83f81ac0  a19c2d20 a19c2668 a19e2330 a19ea418
    83f81ad0  a19ea350 a19e9418 a19e9350 a19e89b8
    83f81ae0  a19e88f0 a19e8828 a19e8760 a19e8698
    83f81af0  a19e85d0 a19e8508 a19e8440 a19e8378
    83f81b00  a19e7040 a19e7f78 a19e7eb0 a19e7160
    83f81b10  a19f3f78 a19f3eb0 a19f3de8 a19f3930
    0: kd> dd nt!PsThreadType l1
    83fa8028  a19c2eb0
    

Windows内核搞出这么一个全局变量，完全是为了方便，而不用每次都去遍历数据，有人可能会问，没有遍历数组啊，直接取Index为6的不就完事了吗？其实，OS内核没有保证nt!ObpObjectTypes[6]就一定是线程对象。OK，下边就主要分析ObCreateObject()内部的具体实现就行了。

![](https://p1.ssl.qhimg.com/t01d1a3f131863d3a3a.png)

![](https://p5.ssl.qhimg.com/t01d277984f966fdf09.png)

绕了这么一大圈，就为了看他一眼，好了回归正题，那又是在哪里插入进去的呢？NtCreateThread中还有一个关键的函数调用，即PspInsertThread()，该函数内部调用了另一个关键的API即ObInsertObjectEx(),如下所示：

![](https://p1.ssl.qhimg.com/t016e55d5aff98ce2ad.png)

其内部调用ObpCreateHandle()，该函数是为此对象创建出一个句柄，并插入到句柄表中，此外还有个副作用，我们需要分析的就是分析这个副作用。即插入到全局的Directory中。

![](https://p1.ssl.qhimg.com/t01bb23b8cceadb0029.png)

ObpCreateHandle()中调用ObpInsertOrLocateNamedObject()进行对象的插入或者名字的定位，这个函数非常关键，其内部有算法，跟进去。

![](https://p4.ssl.qhimg.com/t011693a4ab4ea94310.png)

ObpInsertOrLocateNamedObject()中调用ObpLookupObjectName()进一步处理。

![](https://p1.ssl.qhimg.com/t01536d9a770cd74365.png)

该函数体内出现了两个非常重要的东西，第一个是全局变量ObpRootDirectoryObject，第二个便是ObpLookupDirectoryEntry();分别如下图所示：

![](https://p5.ssl.qhimg.com/t01351bf4db15beb6e4.png)

![](https://p3.ssl.qhimg.com/t018f0c4af5d0adf209.png)

ObpLookupDirectoryEntry的完整C伪代码如下：

![](https://p5.ssl.qhimg.com/t01483f10603edd4273.png)

显然这个函数的作用已经不用过多的解释了，怎么遍历查找该全局“Directory”的也不用解释了。简单分析下便可知道具体的算法。

## 3、内核对象管理大管家——ObpRootDirectoryObject

在上一小节中，我们从源码中碰到了一个全局变量ObpRootDirectoryObject，这个全局对象可谓能够呼风唤雨，先来看下该对象对指向的具体的信息：

    
    
    0: kd> dd ObpRootDirectoryObject l1
    83f81a88  a8605ed0
    
    0: kd> dt nt!_OBJECT_HEADER a8605ed0-18
       +0x000 PointerCount     : 0n44
       +0x004 HandleCount      : 0n0
       +0x004 NextToFree       : (null)
       +0x008 Lock             : _EX_PUSH_LOCK
       +0x00c TypeIndex        : 0x3 ''            //注意这个
       +0x00d TraceFlags       : 0 ''
       +0x00e InfoMask         : 0x2 ''            //注意这个
       +0x00f Flags            : 0x12 ''
       +0x010 ObjectCreateInfo : 0x00000001 _OBJECT_CREATE_INFORMATION
       +0x010 QuotaBlockCharged : 0x00000001 Void
       +0x014 SecurityDescriptor : 0xa860501d Void
       +0x018 Body             : _QUAD
    
    0: kd> dt nt!_OBJECT_HEADER_NAME_INFO a8605ed0-18-10
       +0x000 Directory        : (null)
       +0x004 Name             : _UNICODE_STRING "\"
       +0x00c ReferenceCount   : 0n0
    

由nt!_OBJECT_HEADER.TypeIndex为3可知，这是个根，回忆一下之前讲的数组的0号索引。由nt!_OBJECT_HEADER.InfoMask可知，其存在nt!_OBJECT_HEADER_NAME_INFO可变头信息，打出来看到其名字确实为”\”。那么这个对象的Body是什么呢？当然是nt!_OBJECT_DIRECTORY；为什么呢？其实由其名字就可以知道了。看看其Body的信息如下：

    
    
    0: kd> dt nt!_OBJECT_DIRECTORY a8605ed0 -r2
       +0x000 HashBuckets      : [37] 0xa8608c98 _OBJECT_DIRECTORY_ENTRY
          +0x000 ChainLink        : 0xa8715fd8 _OBJECT_DIRECTORY_ENTRY
             +0x000 ChainLink        : (null)
             +0x004 Object           : 0xa278b358 Void
             +0x008 HashValue        : 0x125b
          +0x004 Object           : 0xa8610b60 Void
          +0x008 HashValue        : 0x2b26d
       +0x094 Lock             : _EX_PUSH_LOCK
          +0x000 Locked           : 0y0
          +0x000 Waiting          : 0y0
          +0x000 Waking           : 0y0
          +0x000 MultipleShared   : 0y0
          +0x000 Shared           : 0y0000000000000000000000000000 (0)
          +0x000 Value            : 0
          +0x000 Ptr              : (null)
       +0x098 DeviceMap        : (null)
       +0x09c SessionId        : 0xffffffff
       +0x0a0 NamespaceEntry   : (null)
       +0x0a4 Flags            : 0
    

我们就沿着展开第一个HashBuckets吧，看看里边的数据都是些什么。-r2是告诉Windbg递归展开内部2层。注意第二层的ChainLink为null，说明这条链已经到头了。我们来具体分析下HashBuckets[0]号链上的这两个元素都是啥对象。

先看第一个对象，如下；正好是root对象；

    
    
    0: kd> dt nt!_OBJECT_HEADER 0xa8610b60-18
       +0x000 PointerCount     : 0n6
       +0x004 HandleCount      : 0n0
       +0x004 NextToFree       : (null)
       +0x008 Lock             : _EX_PUSH_LOCK
       +0x00c TypeIndex        : 0x3 ''
       +0x00d TraceFlags       : 0 ''
       +0x00e InfoMask         : 0x2 ''
       +0x00f Flags            : 0x12 ''
       +0x010 ObjectCreateInfo : 0x00000001 _OBJECT_CREATE_INFORMATION
       +0x010 QuotaBlockCharged : 0x00000001 Void
       +0x014 SecurityDescriptor : 0xa860501c Void
       +0x018 Body             : _QUAD
    

第二个对象信息如下：

    
    
    0: kd> dt nt!_OBJECT_HEADER 0xa278b358-18
       +0x000 PointerCount     : 0n2
       +0x004 HandleCount      : 0n0
       +0x004 NextToFree       : (null)
       +0x008 Lock             : _EX_PUSH_LOCK
       +0x00c TypeIndex        : 0x19 ''
       +0x00d TraceFlags       : 0 ''
       +0x00e InfoMask         : 0x2 ''
       +0x00f Flags            : 0x12 ''
       +0x010 ObjectCreateInfo : 0x00000001 _OBJECT_CREATE_INFORMATION
       +0x010 QuotaBlockCharged : 0x00000001 Void
       +0x014 SecurityDescriptor : (null)
       +0x018 Body             : _QUAD
    
    0: kd> dt nt!_OBJECT_HEADER_NAME_INFO 0xa278b358-18-10
       +0x000 Directory        : 0xa8605ed0 _OBJECT_DIRECTORY
       +0x004 Name             : _UNICODE_STRING "Ntfs"
       +0x00c ReferenceCount   : 0n0
    
    0: kd> dt nt!_DEVICE_OBJECT 0xa278b358
       +0x000 Type             : 0n3
       +0x002 Size             : 0xb8
       +0x004 ReferenceCount   : 0n1
       +0x008 DriverObject     : 0xa2407660 _DRIVER_OBJECT
       +0x00c NextDevice       : (null)
       +0x010 AttachedDevice   : 0xa24648a8 _DEVICE_OBJECT
       +0x014 CurrentIrp       : (null)
       +0x018 Timer            : (null)
       +0x01c Flags            : 0x40
       +0x020 Characteristics  : 0
       +0x024 Vpb              : (null)
       +0x028 DeviceExtension  : (null)
       +0x02c DeviceType       : 8
       +0x030 StackSize        : 9 ''
       +0x034 Queue            : <unnamed-tag>
       +0x05c AlignmentRequirement : 0
       +0x060 DeviceQueue      : _KDEVICE_QUEUE
       +0x074 Dpc              : _KDPC
       +0x094 ActiveThreadCount : 0
       +0x098 SecurityDescriptor : 0xa87be310 Void
       +0x09c DeviceLock       : _KEVENT
       +0x0ac SectorSize       : 0x200
       +0x0ae Spare1           : 1
       +0x0b0 DeviceObjectExtension : 0xa278b410 _DEVOBJ_EXTENSION
       +0x0b4 Reserved         : (null)
    
    0: kd> dt 0xa2407660 _DRIVER_OBJECT
    ntdll!_DRIVER_OBJECT
       +0x000 Type             : 0n4
       +0x002 Size             : 0n168
       +0x004 DeviceObject     : 0xa2ee4020 _DEVICE_OBJECT
       +0x008 Flags            : 0x92
       +0x00c DriverStart      : 0xa782f000 Void
       +0x010 DriverSize       : 0x12f000
       +0x014 DriverSection    : 0xa192f368 Void
       +0x018 DriverExtension  : 0xa2407708 _DRIVER_EXTENSION
       +0x01c DriverName       : _UNICODE_STRING "\FileSystem\Ntfs"
       +0x024 HardwareDatabase : 0x841aa250 _UNICODE_STRING "\REGISTRY\MACHINE\HARDWARE\DESCRIPTION\SYSTEM"
       +0x028 FastIoDispatch   : 0xa786e900 _FAST_IO_DISPATCH
       +0x02c DriverInit       : 0xa79329fa     long  Ntfs!GsDriverEntry+0
       +0x030 DriverStartIo    : (null)
       +0x034 DriverUnload     : (null)
       +0x038 MajorFunction    : [28] 0xa78c7bc8     long  Ntfs!NtfsFsdCreate+0
    

都出来了，原来是文件系统下的一个文件设备驱动对象。ok，分析完上边两个Directory中的对象后，再回到之前说的Windbg的自动化命令的输出，我们来对比下：

![](https://p5.ssl.qhimg.com/t019574f6c9217be9d3.png)

是不是一模一样，现在你是否可以彻底搞明白Windbg的自动化命令是如何工作了的呢？不，我应该问，你是否彻底搞明白Windows的内核对象管理是如何实现了的呢？

## 4、附赠两张Windows内核对象全景图

下边这张图是我之前，很久以前学XP的时候自己总结的，而文章中讲解的是Win7的，所有有所区别，但原理是一样的，看这个图，有一种俯视的感觉：

![](https://p2.ssl.qhimg.com/t01e41a42885398027d.png)

## 5、作业

仿照着我给的上边这个图，把Win7下的内核对象管理也弄一张类似的图出来。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **void *** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/220061](/post/id/220061)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Windows](/tag/Windows)
  * [逆向工程](/tag/逆向工程)
  * [内核对象](/tag/内核对象)

 **+1** __4赞

 __收藏

![](https://p5.ssl.qhimg.com/t013c5d4d3bc7c086d8.jpg) void *

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

