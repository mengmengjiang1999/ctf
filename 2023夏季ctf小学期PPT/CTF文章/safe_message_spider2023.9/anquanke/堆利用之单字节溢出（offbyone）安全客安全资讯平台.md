# 堆利用之单字节溢出（off-by-one）

阅读量 **302581**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2017-12-05 12:19:34

 **x**

##### 译文声明

本文是翻译文章，文章原作者 _py，文章来源：0x00sec.org

原文地址：<https://0x00sec.org/t/null-byte-poisoning-the-magic-byte/3874>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t01899db408f7764530.jpg)

## 前言

大家好，今天的话题是迄今为止我最喜欢的堆利用开发技术（就Linux而言）——单字节溢出（off-by-one），该技术非常棒，尽管多年来malloc已经被强化了多次，但是它还是成功的绕过了所有的缓解措施。

为了向你们演示这个技术，我专门写了一个pwnable，环境是Ubuntu 16.04。

## 二进制浏览

在介绍攻击的理论之前，我们先快速浏览一下这个程序的汇编。

1.我们可以新建块对象，块对象的结构如下：

![](https://p2.ssl.qhimg.com/t0144c3d3716c326373.png)

————————————————————————————————

声明：为了便于区分，后文统一将strunck chunk结构所在的块成为属性块，而char* data指向的块称为数据块，属性块加上数据块称为块对象。

————————————————————————————————

2.我们可以转储块对象的内容。

3.我们可以释放块对象，这里并不存在bug。

![](https://p2.ssl.qhimg.com/t0107ed09aa07c7778e.png)

4.我们还可以编辑块对象的内容，有趣的事就在这里。

![](https://p1.ssl.qhimg.com/t01efe13d2023dbbfbc.png)

可以看到，上面的片段最后调用了一个函数，经验丰富的”老鸟”应该一眼就能看出这里有一个很严重的BUG。考虑一下下面的情况：

![](https://p0.ssl.qhimg.com/t015b8479d54f2e3f88.png)

![](https://p4.ssl.qhimg.com/t01d989f518e1b0c170.png)

如果我们对块对象0调用edit()函数，那么它就会根据块对象0的数据块指针找到对应的数据块，然后在数据块的结尾处添加一个NULL字节。

![](https://p2.ssl.qhimg.com/t01ddd14184a8b68a1e.png)

![](https://p4.ssl.qhimg.com/t011ba40ff2704c9a42.png)

![](https://p4.ssl.qhimg.com/t0130433db3b9f3022a.png)

通过简单的计算，我们会发现0x603030+0x88已经跑到块对象1的范围中了，而且恰好是块对象1属性块的size域，所以添加的NULL字节会覆盖size域的最低字节，导致块对象1的大小从0x21变成0x00。这就是传说中的单字节溢出（off-by-one），那如何利用这个BUG呢，别急，听我细细道来。

## libc泄漏

再利用之前我们需要先做一些准备，比如泄露libc。

此时释放块对象0有以下的效果：

![](https://p1.ssl.qhimg.com/t0174210837e6b58930.png)

![](https://p2.ssl.qhimg.com/t0184eb11c5a46a700c.png)

块对象0的数据块大小是0x90，按理说应该放到small bin中去，但堆管理器为了提高效率，会先将其放到unsorted
bin中，让它有第二次机会，源码如下：

![](https://p1.ssl.qhimg.com/t0179a8968c39b104ea.png)

释放后可以看到块对象0数据块中的前向指针和后向指针都指向了libc中的main
arena。他们的值相同是因为此时此刻，该块是该双向链表中的唯一一个空闲块。Main arena的情况如下：

![](https://p0.ssl.qhimg.com/t01e41a42e3e50e4429.png)

从上图可以看到，块对象0释放后，属性块和数据块分别放到了fastbin和unsorted
bin中，根据malloc的源码，如果此时新建一个块对象，那么fastbin中的块会作为新块对象的属性快返回给我们，而如果我们的数据长度不超过0x90，比如0x08，那么unsorted
bin中的那个空闲块就会成为新块对象的数据块。同时malloc为了节省内存，会将unsorted bin中的那个块进行切割，返回一个大小对齐后的块，如下:

![](https://p0.ssl.qhimg.com/t010f1d237b78bcc5a8.png)

![](https://p4.ssl.qhimg.com/t0163cc396e7bdce4a1.png)

要想泄漏libc指针，我们只需请求合适的大小（比如0x08）使其刚好能够包含libc指针就可以了。你可能注意到了后向指针的值变成了0x00007ffff7dd3838，至于为什么会这样，就由你自己研究了。

现在我们只要转储这个新块的值，我们就可以获得libc的地址，最后计算得到libc基址（最后获取函数地址会用到）。

## The whys & hows

我们的总体思路是分配一个新块对象A，然后利用A的数据块去覆盖一个正在使用的块对象B的属性块，然后我们通过编辑A的数据块，将B中的数据块指针换成我们指定的地址（比如GOT表项的地址就是一个不错的选择），再然后，我们就可以通过编辑B的“数据块”从而获得任意地址写的能力。

在此之前我们需要先分配几个块。

![](https://p3.ssl.qhimg.com/t01e268cae68ef60ba3.png)

我们先忽略参数的具体意义，后面我会详细解释。现在main arena的情况是：

![](https://p0.ssl.qhimg.com/t01d45dc8ff7cf3d428.png)

reminder块的大小是0x70，这对我们的分配有什么意义呢？就像前面解释的，每新建一个块对象，我们都需要先用0x20个字节来存放属性（也就是属性块），而0x20很明显比0x70小，所以reminder块又会被分割，最后，reminder块的大小会变成0x50。

![](https://p3.ssl.qhimg.com/t016fe88ad12b46a0ae.png)

而对于我们的数据，由于已经没有空闲块可以承载我们的数据了，所以malloc

只能指望top chunk了，源码如下：

![](https://p4.ssl.qhimg.com/t0103a60f5f159268d8.png)

现在来看一下我们的分配操作造成的影响。

![](https://p0.ssl.qhimg.com/t018d788aec135df894.png)

可以看到，unsorted bin中的块已经被放到了small
bin相应的链表中，而reminder块的地址移到了更远的地方，同时大小变成了0x50，而top
chunk为了满足请求，移动了0x210个字节。下面是gdb中的视图：

![](https://p3.ssl.qhimg.com/t0102d6feab250ca731.png)

我们接着再建两个块对象。

![](https://p3.ssl.qhimg.com/t0121890788e2ab2ad6.png)

![](https://p5.ssl.qhimg.com/t0126a9755237ea403b.png)

准备工作全部完成，注意，块X就是我们前面用“D”填充的那个块，而块Y是用“E”填充的那个，而用“F”填充的那个是用来隔离的。还有一点是，上图的chunk
x和chunk y都指的是数据块，他们的属性块是通过刚刚small bin中的那个块分割得到的，所以没有在这里。

## Previous size 域

当一个块A被释放后，如果它的大小不在fastbin的范畴，邻接块A的块B就需要更新关于A的信息，操作很简单，就是将块B上的IN_USE位设置为0，然后将块B上的Previous
size域设置为块A的大小，表示块A已经被释放了。我们结合实际情况来看一下：

![](https://p3.ssl.qhimg.com/t01d2403c0dba5b07c9.png)

![](https://p4.ssl.qhimg.com/t016bee62c5e0ced970.png)

可以看到，块X的释放后，块Y的size域的值从0x111变成了0x110。而块Y的Previous
size域也从0x00变成了0x210。注意，Previous
size只有当前一个块被释放了才会被使用，其他时候都是用来存放前一个块的数据。你可以简单的算一算，0x6033f0（块Y的地址）减去0x210就等于0x6031e0。

为了让你们有更好的直观感受，接下来的操作过程我会进行两次，不同之处在与，第一次的操作不会用NULL覆盖块X的size域，而第二次操作会用NULL覆盖块X的size域，这样通过对比，可以获得更直观的印象。

首先，利用块X释放后留下的空间新建一个块对象（比X小）。

![](https://p4.ssl.qhimg.com/t0111688a3cc1d7a6b6.png)

Malloc会执行一下操作：

![](https://p1.ssl.qhimg.com/t012396f426109eda88.png)

具体过程总结如下：

  * 用空闲块X的当前大小减去我们请求的大小（0x210-0x110）得到reminder块的大小。
  * 计算reminder块的地址（0x6031e0 + 0x110 ）。
  * 将释放后的块X从unsorted bin链表中摘除，准备分割。
  * 将它声明为reminder块（av->last_remainder = remainder）。
  * 用set_head宏更新reminder块的size域。
  *   * 更新块Y的Previous size域。
  *   * 将切割好的块返回给用户。

新的内存视图如下：

![](https://p4.ssl.qhimg.com/t01a0f234a5f114dc0f.png)

我们计算一下各值。

![](https://p1.ssl.qhimg.com/t019b3a2894874e0d39.png)

看样子，上面的操作没有错。

我们现在来看一下另一种情况——在建新块对象之前用NULL覆盖块X的size域。

## Null Byte Poisoning

我们将利用前面发现的一个结论：edit（）函数会将传入的字符串的末尾加上一个NULL。

![](https://p1.ssl.qhimg.com/t0106a5ee9c0505300a.png)

![](https://p1.ssl.qhimg.com/t01ebe209bc5000d57e.png)

（块1紧邻块X）

我们在这里先解释一下前面新建块对象X时的参数：

![](https://p0.ssl.qhimg.com/t014b266c9ee78b0f69.png)

malloc在从链表中摘除空闲块的时候进行一些检查，我们需要绕过他们：

![](https://p5.ssl.qhimg.com/t01ee3897c18ddfca21.png)

实际上，我们只需要绕过第一个检查就行了，第二个检查我们符合条件。第一个检查如下：

![](https://p3.ssl.qhimg.com/t0137ea93dd9a7b5c16.png)

其实就是检查后一个块的Previous size 域的值是否等于前一个块的大小。由于我们会将块X的大小改为0x200，而地址0x6031e0 +
0x200=0x6033e0还处于块X中，为了绕过检查，我们需要对0x6033e0的值做一定的手脚。

也就是说，我们需要将0x6033e0处的值修改为0x200，否则上面的检查就会检测到内存损坏，然后终止该程序的运行。

接下来进行分配操作。

![](https://p1.ssl.qhimg.com/t0181a5e1b388ecdcae.png)

![](https://p0.ssl.qhimg.com/t019eb9360066141320.png)

注意到了吗？块Y的Previous
size域并没有被更新为reminder块的大小，而且reminder块的大小比第一种情况少了0x10，通过对比我们可以看到，reminder块的大小实际被写到了0x6033e0，也就是在块Y的Previous
size域的基础上往上偏移了0x10的地方，这绝不是偶然，我们计算一下：

![](https://p2.ssl.qhimg.com/t016999fac8cbc8697e.png)

可以看到，因为我们前面通过NULL覆盖修改了块X的大小，经过一系列连锁反应，导致了set_foot宏实际更新的地址变成0x6033e0（因为0x6032f0
+ 0xf0 =
0x6033e0）。这是一个对我们很有利的条件，因为现在块Y还以为前一个空闲块在它前面0x210处，而不知道，实际上那里已经发生了翻天覆地的变化。

那我们怎么利用这个有利条件呢？我们的主要目标是要想办法覆盖数据块指针。让我们继续探索并见证奇迹的发生。

![](https://p4.ssl.qhimg.com/t0147c4a56b8eb8c6c0.png)

![](https://p3.ssl.qhimg.com/t01e90fed5a767e620e.png)

我们在分配了新块对象W之后，块Y假的Previous size域已被更新为0x40（0xf0 – (0x90 + 0x20)) ==
0x40）。我们成功的在块Z和块Y之间放置了一个数据块指针（如果你明白我意思的话），接下来的操作你估计也想到了，我们先释放块Z。

![](https://p0.ssl.qhimg.com/t01f7a83214365f5fd5.png)

如果现在释放块Y，会发生什么？

![](https://p5.ssl.qhimg.com/t015e9ee2f0200eb697.png)

从源码可以看到，块Y释放后，malloc会检查它前面是否有空闲块，以便进行合并操作，注意，前面说过，块Y还以为它的前一个块大小为0x210，也就是起始地址在往前偏移0x210的地方，而现在0x210处是什么？是我们刚刚释放的块Z，这样一来，事情就变得很有趣了。

![](https://p4.ssl.qhimg.com/t0158aa6cc8ac9730ff.png)

![](https://p5.ssl.qhimg.com/t0139906d1af6cf6335.png)

可以看到，先后释放块Z和块Y之后，malloc进行了合并操作，从块Z开始，到块Y结束的整片空间被合并成了一个空闲块。其原因是为块Y检查它前面是否有空闲块时，发现空闲的块Z，但是由于我们的“恶意操作”，导致块Y的Previous
size域没有被更新（值一直是0x210），而malloc又没有检查块Z的大小，所以malloc认为块Z的到大小就是0x210，然后整片空间就变成了一个空闲块。但是不要忘了在这个空闲块的空间中，还有一个没有被释放的块W，这就为我们交叠块W创造了条件。

现在来看一下main arena的情况：

![](https://p3.ssl.qhimg.com/t017aa52f516dfb6483.png)

如果此时我们再分配一个大小为0x140的块会怎样？我们猜一下：

  * 根据fastbin的后进先出原则，块0x603060应该会被返回给我们作为属性块。
  * 而我们数据的长度是0x140，为了存放我们的数据，块0x6031e0应该会被返回给我们。

![](https://p5.ssl.qhimg.com/t014cb1639180c0c913.png)

![](https://p5.ssl.qhimg.com/t01516c82b20f2f7f63.png)

可以看到我们已经成功的用atoi（）对应的GOT表项的地址覆盖了块对象W的数据块指针，剩下的就是对块对象W调用edit（）函数，然后用将atoi（）的地址换成其他地址，比如system（）。

本文翻译自0x00sec.org [原文链接](https://0x00sec.org/t/null-byte-poisoning-the-magic-byte/3874)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **牧野之鹰** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/88961](/post/id/88961)

安全客 - 有思想的安全新媒体

本文转载自: [0x00sec.org](https://0x00sec.org/t/null-byte-poisoning-the-magic-byte/3874)

如若转载,请注明出处： <https://0x00sec.org/t/null-byte-poisoning-the-magic-byte/3874>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [堆溢出](/tag/堆溢出)

 **+1** __0赞

 __收藏

![](https://p3.ssl.qhmsg.com/dm/200_200_100/t013494c7eecab51c55.jpg) 牧野之鹰

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

