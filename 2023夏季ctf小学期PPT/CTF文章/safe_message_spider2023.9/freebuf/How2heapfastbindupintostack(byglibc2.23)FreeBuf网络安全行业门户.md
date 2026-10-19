## how2heap 的 fastbin_dup_into_stack.c 源码

![](https://image.3001.net/images/20210530/1622390233_60b3b5d99eb9b8911cd7b.png!small)

## pwndbg 调试观察

先malloc了3块内存

![](https://image.3001.net/images/20210530/1622390239_60b3b5df32e51406f57f4.png!small)

堆块结构：

![](https://image.3001.net/images/20210530/1622390242_60b3b5e24809a382d9c9f.png!small)

这里堆信息显示的堆块地址都比栈上存储的堆块地址小0x10，这是因为heap显示的地址是堆块的真正的头部地址，指向的是堆块的第一个数据prev_size，而栈上存储的地址是返回给用户使用的指针fd的位置，pre_size和size字段在64位操作系统上都是8字节大小，所以前面占了0x10，导致看到的两个地址相差0x10大小，至于申请的堆块大小为0x20，实际size位显示的却比申请大小大1字节，这是因为size字段低三比特位为特殊的flag值，分别为：

1.NON_MAIN_ARENA， 记录当前堆是否不属于主线程，1表示不属于，0表示属于；

2\. IS_MAPPED， 记录当前堆是否是由mmap分配的；

3.PREV_INUSE， 记录前一个堆块是否被分配(即是否是使用状态)。

但是fastbin为了快速分配使用，在fast
chunk被free掉的时候并不会将后一个chunk的PREV_INUSE位置零，fd、bk指针在堆块处于分配状态的时候，堆结构体偏移fd的位置就用来存储数据，当堆块处于空闲状态的时候，fd、bk指针就分别记录“物理”相邻的前()一空闲堆块、后()一空闲堆块的地址，用于对应空闲链表的管理。

此处演示的是fastbin范围的堆块，如果是largebin范围的堆块，再往下还有两个指针 fd_nextsize、bk_nextsize。

![](https://image.3001.net/images/20210530/1622390242_60b3b5e2d6c299d1fabd1.png!small)

fd_nextsize、bk_nextsize指针在large
chunk处于空闲状态的时候使用，分别用于记录前()一个与当前chunk大小不同的第一个空闲chunk和后()一个与当前chunk大小不同的第一个chunk。

### 然后free掉a

free前，如图所示

![](https://image.3001.net/images/20210530/1622390244_60b3b5e47ebb831ee06ac.png!small)

free后，如图所示

![](https://image.3001.net/images/20210530/1622390249_60b3b5e929632b8b5509b.png!small)

这时候如果我们再次free(a)，程序就会crash，因为这时候a对应的堆地址被存放到fastbin的链表头部，又因为堆块a的大小在fastbin的范围内，free的时候会检测当前free的对象是否处于fastbins的头部，如果是，则执行Malloc_printerr(报错)并退出程序。

![](https://image.3001.net/images/20210530/1622390252_60b3b5ec33e9497bf3b91.png!small)

那么绕过该机制的方法就是free掉一个相同大小的chunk，这样fastbin空闲链表里的情况如图所示。

![](https://image.3001.net/images/20210530/1622390254_60b3b5ee0b78d7faab6f9.png!small)

![](https://image.3001.net/images/20210530/1622390257_60b3b5f1a0e1649e8b6d0.png!small)

现在我们就可以再次 free(a)，

free(a)的时候ptmalloc内存管理器会检测到fastbin空闲链表头部是b，所以允许free(a)，这样a的chunk头地址就会再次被放到fastbin空闲链表头部，且指向“前一个”空闲堆块b，这样就产生了
a -> b -> a -> b -> a ... 的循环链表的情况，这样我们就能重复malloc到一个chunk。

![](https://image.3001.net/images/20210530/1622390259_60b3b5f38db2960809759.png!small)

接下来做了一次malloc，返回的chunk a的地址存到了指针d中，

![](https://image.3001.net/images/20210530/1622390261_60b3b5f53dd36c03fc876.png!small)

可以看到在堆信息中并没有看到新的chunk产生，因为malloc的大小为8，64位系统的MIN_CHUNK_SIZE为32bit，即至少包含PREV_SIZE,
SIZE, *FD, *BK四个字段，所以分配的最小chunk大小为0x20，内存中size字段为0x21，而fastbin的内存分配策略是exact
fit，即只释放跟申请内存大小恰好相等的堆块，而且是FIFO(First In First
Out)机制，所以这里申请了8字节大小的chunk，分配到的就是之前释放的，在fastbin头部位置的chunk a。

![](https://image.3001.net/images/20210530/1622390263_60b3b5f7072c6127f886d.png!small)

可以看到在fastbin空闲链表中，chunk b 移动到了链表的头部，而刚刚被malloc的，本应移出空闲链表的 chunk a
则移动到了链表尾部，fastbin空闲链表代表0x20大小的数组指向的仍然是一个循环链表。再一次malloc，将chunk a 移到链表头，如图所示。

![](https://image.3001.net/images/20210530/1622390265_60b3b5f941b0fa9141ce3.png!small)

这时候我们就可以通过修改chunk
a的fd指针域，指向栈上一个地址，如果这个地址的后(高地址)8个字节存储的值正好是0x20，ptmalloc就会判断这是一个合法的堆块，该地址就会加入到空闲链表中，因为这个地址是写在chunk
a的fd指针域，是chunk a指向的前面一"空闲堆块"。

![](https://image.3001.net/images/20210530/1622390268_60b3b5fc69d9e6fe5432f.png!small)

那么我们下一次malloc就会分配到chunk a，再次malloc就会分配到栈空间了，

malloc 8字节，如图所示

![](https://image.3001.net/images/20210530/1622390271_60b3b5ffb7cfde9a18d3f.png!small)

此时的fastbin

![](https://image.3001.net/images/20210530/1622390274_60b3b60211114fe0ac401.png!small)

之前栈空间上伪造的chunk已经移动到链表头了，

再次malloc就能拿到栈空间，如图所示

![](https://image.3001.net/images/20210530/1622390275_60b3b60383e4d0136b151.png!small)

这就是free完没有将指针置NULL产生的 "dangling pointer" 产生的 "Double Free" 漏洞产生的 "Use After
Free" 攻击的完整分析过程。

## 安全建议

malloc出来的指针free之后要置NULL。

