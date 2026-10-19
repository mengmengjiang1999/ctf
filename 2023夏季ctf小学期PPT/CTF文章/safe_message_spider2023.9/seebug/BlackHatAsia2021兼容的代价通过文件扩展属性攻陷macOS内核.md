**作者：库特@蚂蚁安全实验室  
原文链接：<https://mp.weixin.qq.com/s/bfdwAhRRso34OOZrG2r65Q> **

文件系统是操作系统的基础设施之一，其中存在的任何缺陷都会导致严重后果。在研究苹果macOS文件系统的具体实现时，我们在xattr特性中发现了一系列严重漏洞。

文章将以CVE-2020-27904和CVE-2019-8852（由天穹实验室的库特同学独立发现并报告）为例，剖析漏洞成因，展示漏洞利用过程用到的独特技术，对此类漏洞的危害进行了演示，我们应当重视文件系统漏洞带来的潜在风险。

### 01 关于xattr

xattr是extended file
attributes的缩写，即文件扩展属性，是文件元数据的一种。xattr独立于文件内容存储，由文件系统分配专用的存储空间，可以使用xattr为文件添加额外的属性，实现各种各样的功能。例如Finder中的颜色标签，就是xattr的一种应用场景。

![
](https://images.seebug.org/content/images/2021/05/f9ada4a0-ee0a-4dca-9a0f-6e31d012d75d.png-w331s)

可以通过命令xattr、mdls等查看和操作文件xattr。在代码层面，我们可以通过getxattr、setxattr等系统调用读取和修改xattr。

### 02 在FAT文件系统中兼容xattr

macOS支持很多种文件系统格式，HFS+和APFS是苹果的私有文件系统，
它们支持xattr，这毫无疑问。此外macOS也支持FAT，这是一种比较“古老”的文件系统，仅仅提供相对简单的文件管理功能。但是经过我的测试，FAT文件系统中，竟然也可以正常使用xattr特性，是一件很神奇的事情。

macOS内核代码是开源的，我们可以尝试从代码层面分析，FAT文件系统是如何支持xattr特性的。答案在以下源文件中bsd/vfs/vfs_xattr.c，当我们调用setxattr系统调用时，FAT文件系统的相关回调函数会返回ENOTSUP，说明FAT并没有xattr特性的原生支持。但是接下来会执行以下函数default_setxattr，这个函数为FAT等文件系统提供了xattr的一整套兼容方案。

![
](https://images.seebug.org/content/images/2021/05/838ecded-69c9-4d38-9544-10ebfc455f36.png-w331s)

通过阅读代码，我们发现，在类似于FAT这种没有原生支持xattr的文件系统中，苹果引入了Apple
Double文件，来模拟xattr。在setxattr之后，在相同目录下，会多出一个前缀为"._"的隐藏文件，这就是FAT中存储xattr的位置了。但这同时也意味着，macOS需要在内核中对xattr文件进行解析，这是一个很危险的操作，如果解析不当很容易导致问题发生。

### 03 xattr漏洞之一（CVE-2020-27904）

首先简单介绍一下FAT中存储xattr的apple double文件结构，其实就是几种类型的数据依次排序。文件头部是apple double file
header和ext attr header两个数据结构，之后是attr entry，存储xattr名字和属性值在文件中的偏移，然后是xattr data。

漏洞代码位于bsd/vfs/vfs_xattr.c这个文件中。当进行代码审计时，注意到这个函数check_and_swap_attrhdr，它的作用是，对读入内存的apple
double文件进行校验，确认文件结构是否合法。图示的for循环，用来检查存储的xattr键值对是否位于有效的数据区。

![
](https://images.seebug.org/content/images/2021/05/85767944-bfa5-4a89-8ec3-ec757ae445f3.png-w331s)

但是让我们看一下红色标记的这一行代码，做了两件事情，offset和length相加，检查是否存在整数溢出，还检查了attr
data的结尾，是否超出header指定的数据区结尾。

但是，这里存在一个问题，这段代码没有对offset本身做检查，或者说没有对data的起始地址做检查，当offset < data_start时，attr
data将会跟之前的数据结构重合，例如attr entry，ext attr header，file
header！当调用setxattr设置xattr时，相当于一个写操作，是可以更改所有这些可以重叠的数据结构的。

#### 3.1 漏洞利用

我们必须利用setxattr覆写file
header的能力，做一些有用的事情，比如实现任意地址读写。让我们查看所有涉及到这两个header的代码，寻找有一些有用的副作用。

首先，找到了以下一段代码，当setxattr完成后，会通过write_xattrinfo把更改保存到文件。在写回文件之前，会通过data_start +
data_length重新计算文件大小。然而，这两个字段，都在非法offset的覆盖范围之内，我们可以更改其中的任何一个，来增大文件的大小，比如增加到64mb。这样，write_xattrinfo会遵照我们的指示，把同样多的内存写入到文件之中，但是apple
double文件一般只会分配64kb大小的内存，如果我们要求保存64mb内存，保存的长度大于实际内存大小，就发生了越界读操作。越界读取的内存会保存到apple
double文件之中，我们可以在用户态读取这个文件的内容，来探测内核的内存信息。

![
](https://images.seebug.org/content/images/2021/05/07411c43-976e-4e55-8cdb-f5ceb116c57b.png-w331s)

具体参考这张图，这是我通过以下的代码，实际dump到apple
double文件的内容，使用十六进制显示。绿色标记(offset+0x78)的是我伪造的一个非法offset，指向data_start字段，这可以通过篡改用户空间的"._"
apple double文件实现。文件偏移64kb开始处开始，就是我们越界读取到的内核内存。

![
](https://images.seebug.org/content/images/2021/05/18ddc741-72d9-444c-a77b-b3e3f778d302.png-w331s)

那么，有什么用处呢？大家都知道，现代内核中，都开启了ASLR保护，内核信息泄漏，最直观的用处就是可以用来探测内核内存布局。我在这个内存位置，提前布局了一个ipc_kmsg，参考kmsg的定义，当只有一个kmsg时，prev和next均指向自身，也就是这个kmsg的首地址，通过这一点，我们可以计算出自己在内存中的位置。所以，现在ASLR就不是一个问题了。

现在，我们有了一个oob-read，但是对于拿到内核权限来说，这还不够，通常我们需要通过一个内核任意地址写，来实现这个目标，这是这个漏洞最有挑战性的一个点了。

已知现在可以控制两个header中的数据，我们继续查看代码，观察还有哪些有用的副作用。来到以下代码，在VNOP_WRITE写文件的前后，分别有一个swap_adhdr操作。这个函数做的事情比较简单，就是把header中的整数，做了一次swap操作，也就是大小端序转换。

![
](https://images.seebug.org/content/images/2021/05/a258d862-099d-4de5-836b-0478f685b89a.png-w331s)

这里为什么要做一个swap操作呢？apple double文件是大端序存储的，内存中的数据与文件中的字节顺序是不一致的，需要做一次端序转换才能写入文件。

这段代码中有一个for循环，循环的次数来自于文件header，而我们可以任意的修改header中的数据，因此for循环的次数，我们是可以控制的！我们可以把循环次数变成一个很大的数，比如一百万，for循环会一直持续下去，这样我们就得到了一个越界。但是，这并不是一个oob-write，仅仅是一个oob-swap。

#### 3.2 从oob-swap到uaf

那么，oob-swap可以做一些什么呢？

具体来看，swap操作会改变一个数字的端序，如果转换之后依然使用小端序来解释，那么数字的值会发生变化。你可以让一个整数变大，也可以让一个整数变小，这就足够了。

这里依然要用到ipc_kmsg，首先我们把一个特定的kmsg放置在apple double内存之后，这个kmsg就是我们oob-swap的目标。

然后，我们再看一下kmsg结构，oob-swap可以改变一些什么。kmsg头部的字段是ikm_size，是一个uint32，因为kmsg是变长的，需要使用这个字段记录kmsg的长度，释放时，根据这个字段的值释放当初分配的内存。如果我们利用oob-swap，让这个字段变大，比如0x1234 ->
0x4321，那如果我们释放这个kmsg，实际上会多释放一部分内存，跟随在这个kmsg之后的其它内核对象，就被一同释放掉了，但这个对象的引用还在，我们依然可以使用这个已被释放掉的对象，也就是说，我们得到了一个UaF。于是，我们可以把oob-swap漏洞，转化成一种非常有用的漏洞类型了！

![ ](https://images.seebug.org/content/images/2021/05/77ece881-cbf8-4e1d-bbbe-cd1da718ffe5.png-w331s)

但是，oob-swap操作，一次连续翻转12个字节，并且起始位置不是4字节对齐的，因此，我们无法做到只翻转ikm_size这个字段。实际上，我们得到的是一个10个字节的越界翻转（绿色标记）。这意味着，我们得到了比我当初设想中更多的副作用，并且这些副作用对我们的漏洞利用是有害的。具体来讲，共有ikm_size、ikm_flags、ikm_next三个字段遭到破坏。

当然，我们还是可以控制ikm_size的大小，可以顺利触发overfree的操作。但是，ikm_next是一个很重要的指针，它的损坏，会导致后续内核panic。

根据panic信息，我们找到了以下的代码，内核在释放kmg之前，会做一些检查，我们必须保证，oob-swap之后ikm_next是有效的。

![
](https://images.seebug.org/content/images/2021/05/5f5afebd-d14c-4541-a4ba-08430859a454.png-w331s)

我们再次观察一下，oob-swap的结果，ikm_flags的高16位，覆盖了ikm_next指针的低16位，而大部分情况下，ikm_flags的高位是0，所以可以近似的认为，ikm_next低16位被清零了。那么我们如何避免panic呢？

考虑这么一种情况，如果kmsg分配在64kb对齐的地址处，比如0xAABB0000，由于ikm_next指向kmsg本身，也就是ikm_next指针低16位等于0。此时，即使oob-swap把它的低位清零，ikm_next依然是一个有效的指针，因为它的低位原本就是0。这样做就可以避免后续的panic，得到一个完美的UaF。

为了实现把ipc_kmsg分配到64kb对齐的地址处（0x10000），需要对内核堆进行精确布局。我连续分配了18个大小为0x11000的kmsg，这样做的好处是，它们的地址会依次递增，当然了我们只关心低16位的变化，他们的地址分别为xxx1000
xxx2000 ... xxxf000 xxx0000。其中必然包含一个64kb对齐的kmsg！利用我们已经获得的oob-read能力，可以清楚的知道是哪一个kmsg是我们需要的，如下图所示。

![
](https://images.seebug.org/content/images/2021/05/0c335876-222a-427b-af67-56df49c03ef8.png-w331s)

接下来需要在64kb地址边界处，精确地对kmsg进行分割，我们把连续的3个kmsg释放掉，重新分配3段新的内存，包含一个16 page内存页和两个8
page内存页。其中的16 page内存页预留给xattrinfo使用，它会对齐到64kb，下一个8
page内存页同样也会对齐到64kb，这个位置用来放置目标kmsg，是oob-swap破坏的对象，我们将会利用oob-swap把它伪造成为一个16
page大小的kmsg。下一个8 page内存页，是ool ports page，是我们overfree的对象。经过这一系列操作，然后把oob-swap破坏掉的kmsg释放，紧随其后得ool ports page会一并被释放掉，我们就得到一个完美的UaF。

![
](https://images.seebug.org/content/images/2021/05/8242554c-ac9b-4675-9bc7-9d33fb8f0577.png-w331s)

后面的事情就比较简单了，可以通过一些通用的漏洞利用技术创建tfp0，获取到内核任意地址读写能力，完成漏洞利用。

1、通过共享内存，在内核中伪造一个fake task，和一个fake port。

2、可以通过OSData对释放掉的ool ports page重新占位，控制ool port的值，指向fake port。

3、receive ports，得到task port。

4、利用pft trick(pid for task)，实现任意地址读，确定kernel task和kernel map的值。

5、更新fake task，得到tfp0。

### 04 xattr漏洞之二（CVE-2019-8852）

这个漏洞在2019年的10.15.2版本中修复，已经有一点老了。

还是参考default_setxattr函数，有这样一段代码。xattr文件中存在一个特殊的属性，com.apple.FinderInfo。当设置这个属性时，会跳转到以下代码，用户可以为这个属性设置32字节的数据。

![
](https://images.seebug.org/content/images/2021/05/c1904cb0-25ea-4319-969e-6a37277bf91d.png-w331s)

问题是，finderinfo的偏移地址，也是来自于文件，并且没有对这个值的有效范围进行检查，当这个值大于64kb时，就会发生越界，越界写的数据完全受我们控制。

这个漏洞提供了32字节的任意地址读写能力，唯一的限制是，读写的地址只能位于xattrinfo页面之后。这是一个比较完美的漏洞，关于漏洞利用的过程，这里就不做过多介绍了。

### 05 结语

文件系统是内核的一个有效的攻击面，历史上这种类型的漏洞并不鲜见。文章展示的漏洞再次证明，通过文件系统漏洞对内核发起攻击，是一种非常有效的方法，有很大的危害。因此，设计和实现一个文件系统时，需要非常的小心谨慎，对来自用户空间的任何数据都要进行严格校验。

CVE-2020-27904是一个非常有意思的漏洞，老实说它的漏洞品相并不好，但是通过我们独特的漏洞利用技术，我们实际上可以做到漏洞的稳定利用，把它转变成一个完美的漏洞。希望其中用到的一些思路和技术，可以给相关领域的研究者带来启发。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1585/>

