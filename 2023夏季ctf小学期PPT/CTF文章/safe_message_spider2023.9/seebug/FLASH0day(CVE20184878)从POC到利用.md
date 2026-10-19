作者：ze0r@360 A-TEAM  
来源：<https://mp.weixin.qq.com/s/F2N04exaW8QO1IeHRZgmfg>

本篇文章，360 A-TEAM 将为大家介绍FLASH 0day(CVE-2018-4878)如何从POC到利用。

声明：本文由ze0r@360 A-Team原创，仅用于技术研究，不恰当使用会造成危害，严禁违法使用，否则后果自负。

#### 0×00 前言

这篇文章没有前言，简单粗暴，干货满满~下面我们就开始吧~

#### 0×01 在野EXP

一开始我们下载到了当时在野的EXP，用FFDEC查看AS脚本，关键触发点如下：

![](https://images.seebug.org/content/images/2018/03/8c1c6b9c-ab02-4d74-9fab-b57fb7fd24f3.jpg-w331s)

![](https://images.seebug.org/content/images/2018/03/18b8521f-d0c7-4b26-a8ce-1e14487c1b0a.jpg-w331s)

从反编译的脚本中，可发现除了布局内存外就是这两个方法，主要就是以一个§\x05§为参数初始化了一个drmManager对象，之后就将§\x05§赋值为NULL，而§\x05§为：

![](https://images.seebug.org/content/images/2018/03/b001b099-234f-458f-bc53-867428f73736.jpg-w331s)

之后在github上发现已经有人发布了POC，而代码完全一致，只不过把乱变量名变得有意义了，而且也可以直接编译生成。故分析依照此POC进行。

前面已经说过，除了布局内存的代码外，就是初始化并赋值后建立了一个监听器。在POC中exploit方法中只留下这段代码，编译运行：

![](https://images.seebug.org/content/images/2018/03/9bb1028d-239b-49d1-a5c3-7a9d69c4e3af.jpg-w331s)
![](https://images.seebug.org/content/images/2018/03/65b3d105-2806-4081-84df-6de90dc55e48.jpg-w331s)

打开稍等片刻就会崩溃到调试器，查看：

![](https://images.seebug.org/content/images/2018/03/dae08db7-710a-45ef-8fb8-7947a5eb9264.jpg-w331s)

可见直接使用ecx传递了一个对象，在IDA中也确认这是一次虚函数调用。

![](https://images.seebug.org/content/images/2018/03/bc35b085-2098-49c4-8449-690eb022aa6e.jpg-w331s)

根据汇编代码可断定，ECX偏移0x0c处为某对象指针，而此对象已经全是0，造成了悬挂指针。再看AS3脚本中，把一个MyListener（实现了DRMOperationCompleteListener接口）类型对象赋值null。所以可猜测ecx->0x0c为MyListener对象。下断此时ecx这个对象的构造过程：

![](https://images.seebug.org/content/images/2018/03/e0edfee0-503c-4fee-a272-46a0358beecd.jpg-w331s)

![](https://images.seebug.org/content/images/2018/03/e81e5a4c-2e95-46ad-b968-45f15f2e8b8d.jpg-w331s)

大致可判断此对象共5个方法，triggerVul即面触发崩溃的方法。查看引用共有2处：

![](https://images.seebug.org/content/images/2018/03/08bb3c2b-31a1-4eb1-9e71-eaecf12e8b31.jpg-w331s)

反汇编确认赋值方法为1037a150：

![](https://images.seebug.org/content/images/2018/03/170f46d3-dd8a-44b7-9b7f-6a980c8b35bd.jpg-w331s)
![](https://images.seebug.org/content/images/2018/03/f0539a20-8871-4e0a-9534-df98be6bfbb9.jpg-w331s)

windbg中下断，单步几次后查看对象内存：

![](https://images.seebug.org/content/images/2018/03/f14f73ec-16f2-47e3-ac32-aff90adf8873.jpg-w331s)

确认此对象0x0c处为DRMOperationCompleteListener实例指针，即DRMOperationCompleteListener实例在被置null之后被垃圾回收，而在对象中还留存着实例指针造成悬挂指针问题。

#### 0×02 POC利用

而在POC的利用中，则是利用双重释放内存来利用此漏洞。如下：

![](https://images.seebug.org/content/images/2018/03/74d3b57d-b157-4e00-a337-28cca701297a.jpg-w331s)
![](https://images.seebug.org/content/images/2018/03/4b31d63b-8641-491f-a5d5-c08a5ae32af8.jpg-w331s)

由于在代码中，在出现异常后又new了一个新的MyListener对象，由于同是Mylistener对象大小相同，所以内存管理器会仍然分配这块原来MyListener对象所在内存给新对象（只要没被占用）。而之后代码drmManager从未被使用，所以垃圾回收会释放drmManager对象，同样，也会把drmManager对象成员释放（减少引用计数），于是0x068c0100会再次被清除回收：

![](https://images.seebug.org/content/images/2018/03/ce2ec0ae-ee0d-4fc7-a68f-1d0456dce81f.jpg-w331s)

在清除完成后，AS3中的danglingpointer变量仍然指向这块区域，所以在POC中，也是定时查看danglingpointer的成员变量是否被改变来判断是否已经完成内存释放。而之后大量申请内存以再次被内存管理器分配此内存完成占用。在偏移0x70处下写入断点（因为重启了调试器，故下面截图中地址并不完全相同）：

![](https://images.seebug.org/content/images/2018/03/ed7ccd01-9b44-4e35-94b3-08acac3c1eb7.jpg-w331s)

可以看到Mem_Arr已经成功占位，正在写入变量默认值。完成后可得内存布局：

![](https://images.seebug.org/content/images/2018/03/b9654b1e-1c17-4281-94d1-ef6cd15904bf.jpg-w331s)

可见Mem_arr的数据区域为0x054a815c-0x054a819c(position=0x31)。其中0x38383838为改写的Modify对象标记，即：

![](https://images.seebug.org/content/images/2018/03/e3fc492f-dc1b-45ea-ad7c-e531583416c5.jpg-w331s)

AS3代码中，PwnBuffer主要设置成员o1的成员变量值，下写入断点得到布局：

![](https://images.seebug.org/content/images/2018/03/95b8b3cf-a18d-47e6-ae16-cc38b950f40b.jpg-w331s)

从POC注释中我们知道danglingpointer.a14为m_buffer地址，而a31为o1对象，而查看上面的布局，发现有明显的故意错误（0x54a818c已经被错误的改写为0xfffffff0），修正后：“this.danglingpointer.a30
=this.danglingpointer.a14 - 0x10;”。修正后布局：

![](https://images.seebug.org/content/images/2018/03/2f94a66c-1529-43e7-af4c-9e4fd313560e.jpg-w331s)

正确改写o1指针后，调用 PwnBuffer则更改了arr[0]属性，之后可成功读取内存：

![](https://images.seebug.org/content/images/2018/03/1db03012-fe2a-4724-a2a4-0c9dd68dbdd9.jpg-w331s)

此时由于arr[0]长度已经被设置成0xffffffff，故可读写进程任意地址内存：

![](https://images.seebug.org/content/images/2018/03/82d0e7d8-9ea0-49e3-b528-0c16dd5ec175.jpg-w331s)

![](https://images.seebug.org/content/images/2018/03/020edac6-11c4-49fe-8451-41f6e6add8fe.jpg-w331s)

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/536/>

