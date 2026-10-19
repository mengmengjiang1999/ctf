一、背景介绍  

VLC
是一款自由、开源的跨平台多媒体播放器及框架。它支持众多音频与视频解码器及文件格式和各类流式协议，也能作为流式服务器在IPv4或IPv6的高速网络连接下使用。

本文主要分析VLC Media Player 2.2.8版本的MKV格式视音频分离器(demuxer)中存在的一个UAF漏洞，实验环境为最新版本的Win10
64位,主要从漏洞细节和漏洞的利用两大部分对漏洞进行分析。

在漏洞细节部分，主要分为以下三个方面：

1.如何找到漏洞触发点？

2.如何确定UAF对象？

3.分析漏洞成因。

在漏洞利用部分，下面这些问题都将得到说明：

1.如何通过精确的Heap Spary布置shellcode？

2.如何重新利用UAF对象？

3.如何bypass DEP&ASLR？

**MKV**

MKV格式属于Matroska开源多媒体容器标准中的一种。它是建立在EBML语言的基础上，这是一种类似于XML格式的可扩展二进制元语言，使用可变长度的整数存储，以节省空间。EBML元素都有自己的级别，每一个高一级的元素由若干次一级的元素组成。整个MKV文件
从整体看可分为2大部分：EBMLHeader和Segment。前者包含了文件的版本、文档类型等相关信息；后者则保存了媒体文件的视频和音频的实际数据，又可以再分为SeekHead、Chapters、Attachments、Cluster等若干子元素。

## 1.1漏洞描述

该漏洞主要是源于VLC播放器用于处理MKV格式的视音频分离器模块——libmkv_plugin.dll中,该模块的一个matroska_segment_c对象在释放后被重引用。可以通过构造大量和该对象大小相同的数据块，最终使这块内存重新被分配，后面再引用该对象时，便可控制程序指针，最后通过精确的Heap
Spray布置shellcode、ROP绕过DEP，造成任意代码执行。

## 1.2受影响的系统版本

VLC media player <= 2.2.8

## 1.3漏洞编号

CVE-2018-11529

# 二、漏洞细节

由于VLC Media
Player的release版本没有调试信息，所以我们可以在官网下载源码自行编译带有调试信息的程序。另外要注意的的一点是，官方推荐使用MinGW在Linux环境下交叉编译VLCMedia
Player。而MinGW使用的是DWARF格式调试信息而非PDB格式，所以在Windbg中调试时，依然无法看到符号信息，但这依然方便了我们使用IDA静态分析。

## 2.1漏洞触发点

首先我们需要找到漏洞触发的位置，使用Windbg自带工具gflag开启页堆：

![image.png](https://image.3001.net/images/20180801/1533115492_5b617c6401015.png!small)

将vlc.exe附加到Windbg上，打开poc.mkv，在此处触发了异常，可以确定漏洞存在于libmkv_plugin.dll模块，再结合IDA和源码分析，得知具体位置是在函数int
Control(demux_t_0 *p_demux, int i_query, va_list args)中

![image.png](https://image.3001.net/images/20180801/1533115499_5b617c6b2f5f7.png!small)

现在关闭页堆，重新打开vlc.exe，并在刚才异常的位置下断点，再次打开poc.mkv，可以看到[ebp+28h]处的值为0x22000020，

![image.png](https://image.3001.net/images/20180801/1533115506_5b617c721fd76.png!small)  

查看ebp处的内容，发现正是PoC中构造的UAF_object的内容，因此可以基本确定，ebp中保存的是指向UAF对象指针。

![image.png](https://image.3001.net/images/20180801/1533115529_5b617c89b4e30.png!small)

当然这里并不是漏洞的触发点，UAF漏洞的触发一般都是要再次引用该对象的某个方法。所以我们可以在[ebp+28h]处设置一个内存访问断点（也就是上图中0x22000020的位置）：
_ba r4 0f4069e8_

继续运行程序，断在了函数matroska_segment_c::UnSelect()中：

![image.png](https://image.3001.net/images/20180801/1533115554_5b617ca2a4f4b.png!small)

继续往后执行几步便会触发漏洞，弹出计算器。

![image.png](https://image.3001.net/images/20180801/1533115566_5b617cae7ee36.png!small)

![image.png](https://image.3001.net/images/20180801/1533115582_5b617cbea8366.png!small)

这里的call指令调用了一个位于vlc.exe模块中的地址，结合PoC来看也是ROP链第一个gadget的地址。

![image.png](https://image.3001.net/images/20180801/1533115601_5b617cd10833e.png!small)

到这里已经可以初步推测漏洞成因，在对象matroska_segment_c被释放后，接着申请与其大小相同内存去“占坑”，待后面重引用该对象中某个函数或成员时，就可以控制程序执行流程。

## 2.2释放重引用的位置

接下来的问题是——matroska_segment_c对象是在哪里被释放，又是在哪里被重新分配呢？尝试使用!heap -p
-a查看分配此内存时的栈回溯信息，发现无法却显示。

  
![image.png](https://image.3001.net/images/20180801/1533115616_5b617ce0235c8.png!small)  

这是因为这里编译器采用了一种称为FPO（Frame Pointer
Omission）的优化方式，它压缩或者省略了在栈上为函数创建栈帧指针的过程。这样可以加速函数调用，但是在这种情况下，调试器可能不能基于EBP展开栈帧（除非它有启用了FPO模块相匹配的符号文件，而前面提到过，我们没有办法生成用于Windbg调试的PDB文件）。

**在哪里分配？**

又因为程序每次加载时堆的地址都是不固定的，也无法靠下断点来进行分析，那么我们只能结合IDA和源码来分析了。通过交叉引用找到调用matroska_segment_c::UnSelect()的Close()函数，观察matroska_segment_c
*是从哪取出的，过程整理如下：

① 将p_this强制转换为demux_t*型并赋值给p_demux

② 从p_demux偏移0x48处取出demux_sys_t*型的结构赋值给p_sys

③ 再从p_sys偏移0x6C处取出virtual_segment_c *型结构赋值给p_vsegment

④ 调用virtual_segment_c的CurrentSegment()方法得到一个matroska_segment_c *型指针

⑤ 最后调用matroska_segment_c的Unselect()方法触发漏洞

  
![image.png](https://image.3001.net/images/20180801/1533115640_5b617cf88c14b.png!small)  

![image.png](https://image.3001.net/images/20180801/1533115654_5b617d0666804.png!small)  

再来看看定义该函数的vlc/modules/demux/mkv/mkv.cpp文件

![image.png](https://image.3001.net/images/20180801/1533115666_5b617d12c24d5.png!small)  

文件中定义了Open()、Close()和Control()等函数，通过函数名和注释可以推测，程序在处理mkv文件时，首先执行Open()函数。而Open()和Close()都有相同的参数——p_this，在上面的分析中，UAF对象的指针正是从该结构体中取出的。刚进入Open()函数时，对象的初始化应该都没有完成，我们只需监视p_demux结构在上述内存偏移中的变化，就能找到分配UAF对象的地方。

在IDA找到Open()函数起始地址，在Windbg中下断点，然后找到该函数参数p_this这个结构的位置，在其相应偏移处设置内存访问断点，观察这些位置内存的变化。

  
![image.png](https://image.3001.net/images/20180801/1533115675_5b617d1b4d6d8.png!small)  

中断到这里时，UAF对象处于已经被创建了。

  
![image.png](https://image.3001.net/images/20180801/1533115688_5b617d282dfe8.png!small)

在IDA中查看该地址，定位在demux_sys_t::PreloadLinked(demux_sys_t*const
this)函数中，而这个函数又只在函数Open(vlc_object_t *)中被引用，最后很快就能在源码中找到分配该内存的位置：

  
![image.png](https://image.3001.net/images/20180801/1533115708_5b617d3ca82b8.png!small)  

  
![image.png](https://image.3001.net/images/20180801/1533115717_5b617d4509f9c.png!small)  

 **在哪里释放？**

描述一个堆块的数据结构是HEAP_ENTRY，它位于一个堆块起始处前8字节，而一个堆块的状态由占用状态变为空闲状态时，对于已释放的堆块，堆管理器定义了HEAP_FREE_ENTRY结构来描述，相比HEAP_ENTRY，它多了8个字节的LIST_ENTRY结构用于存放空闲链表（Free
List）的节点。

那么要定位到该堆块释放的位置就是十分容易了，我们只需要在HEAP_ENTRY处设置内存访问断点，当堆块释放时HEAP_ENTRY中某些标志位发生改变就能立刻断下。

  
![image.png](https://image.3001.net/images/20180801/1533115740_5b617d5c7b930.png!small)  

按F5继续运行，不出所料的断在了ntdll!RtFreeHeap中，只需要Step
Out几次，就能来到libmkv_plugin.dll模块中释放这块内存地方了。

此时，堆块状态已经由busy变为了free：

![image.png](https://image.3001.net/images/20180801/1533115758_5b617d6e5f276.png!small)

同样的，结合IDA在源码中找到释放堆块的位置。

![image.png](https://image.3001.net/images/20180801/1533115765_5b617d7522a55.png!small)

 **在哪里重用？**

继续追踪堆块的变化，和上面的方法类似，就不再赘述了。

![image.png](https://image.3001.net/images/20180801/1533115786_5b617d8ae5bdb.png!small)![image.png](https://image.3001.net/images/20180801/1533115793_5b617d9124407.png!small)

![image.png](https://image.3001.net/images/20180801/1533115801_5b617d99bf1b1.png!small)

## 2.3漏洞成因

在libmkv_plugin.dll模块的static intOpen(vlc_object_t *
p_this)函数中，通过调用ProloadLinked()函数预加载所有链接段，并创建了一个virtual_segment_c对象实例，在该对象的构造函数中，matroska_segment_c对象被初始化。

但后面的FreeUnused()函数中却又释放掉了matroska_segment_c*指向的内存。

![image.png](https://image.3001.net/images/20180801/1533115811_5b617da33eb18.png!small)

而在static void Close(vlc_object_t
*p_this)函数中，p_vsegment调用CurrentSegment()方法返回了一个指向matroska_segment_c的指针赋值给p_segment，但该指针指向的对象matroska_segment_c已经被释放,p_segment
早已是一个悬空指针。

![image.png](https://image.3001.net/images/20180801/1533115822_5b617dae95f6d.png!small)

# 三、漏洞利用

## 3.1 Heap Spray部署shellcode

一个MKV文件所有的音视频帧数据都存放在Cluster这个结构中。每个Cluster内可能有很多个BlockGroup组成，BlockGroup内又由若干个Block组成。这些Block内就是音视频的帧数据。在PoC就是构造了数十个大小为0xfff000的Cluster，并将喷射数据放入每个Block中。

![image.png](https://image.3001.net/images/20180801/1533115878_5b617de62da0d.png!small)

![image.png](https://image.3001.net/images/20180801/1533115893_5b617df58ba21.png!small)

当堆块进行大量分配的时候，堆地址的低位不会发生变化，仅有几个高字节是改变的，查看堆喷的内存块，可以看到每次打开PoC堆喷的地址总是以“018”结尾的，变化的总是前面的高位地址，所以我们只需以将每个Block的大小控制为0x1000，就能够准确得到喷射的位置。以下图为例，0x22000020所在堆块的UserPtr是0x211e5020。(0x22000020
- 0x211e5020) / 0x1000 =
0xE1B(3611)刚好能被整除，也就是0x22000020的内容能被我们精确控制，因为它永远是一个Block的起始地址。

![image.png](https://image.3001.net/images/20180801/1533115906_5b617e0220648.png!small)

## 3.2构造UAF对象

MKV的Attachment部分主要是用于支持在文件中附加任何类型的文件，包括图片、网页、程序等。通过构造500个大小与之前被释放的matroska_segment_c大小相同的attachments，使释放掉的内存被重新分配。

结合源码可以看到，最后触发漏洞的函数并不是UAF对象的方法，而是从UAF对象中又取出的其他，所以在上面堆喷的数据中不仅布置了shellcode，还有demux_sys_t、demux_t和es_out_t这些结构。最终触发漏洞的es_out_Del函数的指针就定义在es_out_t这个结构中，回过头看看堆喷数据中，该指针已被布置为了ROP
chains的起始地址。

![image.png](https://image.3001.net/images/20180801/1533115914_5b617e0ab1d57.png!small)  

## 3.3 bypass DEP&ASLR

使用Immunity
debugger的插件mona，我们可以查看程序所有运行的模块。这里可以看到主程序vlc.exe的Rebase是False,即使有ASLR，程序每次打开其加载地址仍然和以前一样的不会改变，所以我们可以在vlc.exe模块中寻找可用的gadget，构造ROP
chains。

![image.png](https://image.3001.net/images/20180801/1533115927_5b617e1748a6a.png!small)

完整的ROP链如下：

不同于普通的栈溢出，此时我们能控制的只有几个寄存器的值，而当前程序的栈空间是不可控的，所以在ROP链的开始利用Stack Pivot,
将栈指针esp指向堆喷的内存中，相当于将堆作为栈来使用。

![image.png](https://image.3001.net/images/20180801/1533115968_5b617e40dd5d8.png!small)

![image.png](https://image.3001.net/images/20180801/1533115959_5b617e37076d5.png!small)

将edi的值放入edx,剩下的三条指令没有实际作用，在栈上填充无用的数据来补偿被三个pop指令弹出的值。

剩下的几条gadget在为后面布置栈的内容做准备。

![image.png](https://image.3001.net/images/20180801/1533116033_5b617e8181c5d.png!small)

![image.png](https://image.3001.net/images/20180801/1533116048_5b617e90dfa13.png!small)

![image.png](https://image.3001.net/images/20180801/1533116068_5b617ea426b2d.png!small)

![image.png](https://image.3001.net/images/20180801/1533116080_5b617eb0632c5.png!small)![image.png](https://image.3001.net/images/20180801/1533116088_5b617eb8b893c.png!small)![image.png](https://image.3001.net/images/20180801/1533116095_5b617ebf79fb7.png!small)  

将上面寄存器中的值压入栈中。

![image.png](https://image.3001.net/images/20180801/1533116112_5b617ed05ec5e.png!small)![image.png](https://image.3001.net/images/20180801/1533116118_5b617ed6a65fc.png!small)

设置VirtualProtectStub的参数。

![image.png](https://image.3001.net/images/20180801/1533116139_5b617eebe0d23.png!small)

转跳到VirtualProtectStub函数中，修改喷射内存的的执行权限。

![image.png](https://image.3001.net/images/20180801/1533116159_5b617eff2db01.png!small)

完成后转跳到shellcode继续执行。

![image.png](https://image.3001.net/images/20180801/1533116170_5b617f0af2824.png!small)![image.png](https://image.3001.net/images/20180801/1533116177_5b617f1152a3a.png!small)

要实现漏洞的利用，只需简单的修改PoC中的shellcode部分就行，下面是经过修改的用于MSF的漏洞利用模块。

![image.png](https://image.3001.net/images/20180801/1533116197_5b617f250e569.png!small)![image.png](https://image.3001.net/images/20180801/1533116201_5b617f29d358f.png!small)

# 四、修复建议

目前官方已修复该漏洞，可从官网下载最新版本。

