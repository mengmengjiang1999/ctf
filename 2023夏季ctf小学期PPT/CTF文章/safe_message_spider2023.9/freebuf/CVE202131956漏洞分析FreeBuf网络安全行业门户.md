## 一、概述

CVE-2021-31956是微软2021年6月份披露的一个内核堆溢出漏洞，攻击者可以利用此漏洞实现本地权限提升，nccgroup的博客已经进行了详细的利用分析，不过并没有贴出exploit的源代码。

本篇文章记录京东信息安全实验室技术人员学习windows exploit的过程，使用的利用技巧和nccgroup提到的大同小异，仅供学习参考。

## 二、漏洞定位

漏洞定位在windows的NTFS文件系统驱动上(C:\Windows\System32\drivers\ntfs.sys)，NTFS文件系统允许为每一个文件额外存储若干个键值对属性，称之为EA(Extend
Attribution) 。从微软的开发文档上可以查出，有一些系统调用是用来处理键值对的读写操作。

![1640339773_61c5993de19022ab9b067.png!small](https://image.3001.net/images/20211224/1640339773_61c5993de19022ab9b067.png!small)

如下是查询EA的系统调用实现，查询时接收一个用户传入的字典的key集合eaList，将查询到的键值对写入到output_buffer。每次写完一个键值对，需要四字节对齐，函数内部维护了一个变量padding_length用来指示每次向output_buffer写入时需要额外填充的数据长度，同时维护了一个变量为output_buffer_length用来记录output_buffer剩余的可用空间。但是在【A】处写入键值对时并没有检查output_buffer_length是否大于padding_length，两个uint32相减以后发生整数溢出绕过检查，在后面memmove的时候实现任意长度，任意内容越界写。![1640339845_61c599854abac32e4d9bc.png!small](https://image.3001.net/images/20211224/1640339845_61c599854abac32e4d9bc.png!small)

![1640339914_61c599ca32b04a11385b1.png!small](https://image.3001.net/images/20211224/1640339914_61c599ca32b04a11385b1.png!small)

![1640339974_61c59a067112089948b9c.png!small](https://image.3001.net/images/20211224/1640339974_61c59a067112089948b9c.png!small)

## 三、漏洞分析

在具体介绍利用之前，需要先简单了解一下windows的堆分配算法。Windows10引入了新的方式进行堆块管理，称为Segment
Heap，这里有篇文章对此进行了详细的描述

> <https://www.sstic.org/media/SSTIC2020/SSTIC-> actes/pool_overflow_exploitation_since_windows_10_19h1/SSTIC2020-Article-> pool_overflow_exploitation_since_windows_10_19h1-bayet_fariello.pdf>

每个堆块有个堆头用来记录元信息，占据了16个字节，结构如下：

![1640340026_61c59a3ab1efc83661664.png!small](https://image.3001.net/images/20211224/1640340026_61c59a3ab1efc83661664.png!small)

这个漏洞里，越界对象output_buffer是系统临时申请的堆块，系统调用结束以后会被立即释放，不能持久化保存，这导致SegmentHeap
Aligned Chunk Confusion的方法在这里并不适用。
通过实验发现windows在free时的检查并不严格，通过合理控制越界内容，破坏掉下一个堆块的PoolHeader以后，并不会触发异常，这允许我们直接覆盖下一个堆块的数据，接下来的目标就是挑选合适的被攻击堆块对象。

通过查阅资料，我找到了一个用户可以自定义大小的结构体_WNF_STATE_DATA。关于WNF的实际用法，微软并没有提供官方的说明文档，这里不展开介绍，只用把它理解成一个内核实现的数据存储器即可。通过NtCreateWnfStateName创建一个WNF对象实例，实例的数据结构为_WNF_NAME_INSTANCE；通过NtUpdateWnfStateData可以往对象里写入数据，使用_WNF_STATE_DATA数据结构存储写入的内容；通过NtQueryWnfStateData可以读取之前写入的数据，通过NtDeleteWnfStateData可以释放掉这个对象。![1640340063_61c59a5f2a8e6c2bad2c6.png!small](https://image.3001.net/images/20211224/1640340063_61c59a5f2a8e6c2bad2c6.png!small)

举例说明，WNF数据在内核里的保存方式如下所示：

![1640340089_61c59a792b1f2ecf12bfb.png!small](https://image.3001.net/images/20211224/1640340089_61c59a792b1f2ecf12bfb.png!small)

通过喷堆，控制堆布局如下，NtFE是可以越界写的
chunk，后面紧挨着的是_WNF_STATE_DATA数据结构。越界修改结构体里的DataSize对象，接下来调用NtQueryWnfStateData实现相对偏移地址读写。

![1640340136_61c59aa86714c58e1e878.png!small](https://image.3001.net/images/20211224/1640340136_61c59aa86714c58e1e878.png!small)

被篡改过后的_WNF_STATE_DATA 数据结构：

![1640340162_61c59ac22e72374ba1090.png!small](https://image.3001.net/images/20211224/1640340162_61c59ac22e72374ba1090.png!small)

接下来讲述如何将相对偏移读写转换为任意地址读写。

## 四、任意地址读

我们需要使用到另外一个数据结构PipeAttribution，和WNF类似，这个对象可以自定义大小。这里两个指针AttributeName、AttributeValue
正常情况下是指向PipeAttribute.data[]后面的，如果通过堆布局，将AttributeValue的指针该为任意地址，就可以实现任意地址读。遗憾的是，windows并没有提供直接更新该数据结构的功能，不能通过该方法进行任意地址写。

![1640340211_61c59af36d3d9c148ce07.png!small](https://image.3001.net/images/20211224/1640340211_61c59af36d3d9c148ce07.png!small)

理想情况下的堆布局如下所示，ffffdd841d4b6850是之前被覆盖的_WNF_STATE_DATA对象，其余的chunk被释放，然后使用PipeAttribution对象堆喷重新占回。![1640340251_61c59b1bdc79b6dbd5c99.png!small](https://image.3001.net/images/20211224/1640340251_61c59b1bdc79b6dbd5c99.png!small)

根据上面讲述的方法实现任意地址读函数：

![1640340302_61c59b4e5b93b2680b8ba.png!small](https://image.3001.net/images/20211224/1640340302_61c59b4e5b93b2680b8ba.png!small)

##  **五、任意地址写**

我通过修改_WNF_NAME_INSTANCE结构体内的指针_WNF_STATE_DATA实现任意地址写。具体操作是再次释放掉原来的PipeAttribution，使用_WNF_NAME_INSTANCE重新进行堆喷，布局好的堆如下所示

![1640340339_61c59b733125fc142c23b.png!small](https://image.3001.net/images/20211224/1640340339_61c59b733125fc142c23b.png!small)

通过局部地址读写，覆盖掉下一个Wnf结构体（ffffdd841d4b69d0
）里的_WNF_STATE_DATA，使用对应的结构体进行NtUpdateWnfStateData操作，即可实现任意地址写。

##  **六、Windows权限提升**

windows权限提升的方法一般都是遍历进程链表，找到高权限进程的token（8字节），替换当前进程的token。

![1640340391_61c59ba786c27a373d901.png!small](https://image.3001.net/images/20211224/1640340391_61c59ba786c27a373d901.png!small)

最后执行cmd。

![](https://image.3001.net/images/20211224/1640339456_61c598005dfddbf269df4.png!small)

## 七、总结

该漏洞的触发条件并不复杂，利用过程也比较简单，虽然windows的堆分配已经有了很大的随机化，但是大力出奇迹，很容易能够得到理想的堆布局，本地实验过程中的exp基本很少将系统打崩溃。写exp的主要时间是在学习windows系统调用如何传参，查阅了很多文档才搞清楚WNF的用法。总体来说难度不大，非常适合初学者入门。

