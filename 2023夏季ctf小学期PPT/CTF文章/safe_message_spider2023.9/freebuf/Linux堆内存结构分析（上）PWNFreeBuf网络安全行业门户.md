# 堆分配函数与内存结构

`malloc`通过`brk()`或`mmap()`系统调用来获取内存，其区别点在于申请的内存是否大于`128KB.`

拿来一张超经典的图来说事

![1671120461_639b464d0a1747d1516b9.jpg!small?1671120442535](https://image.3001.net/images/20221216/1671120461_639b464d0a1747d1516b9.jpg!small?1671120442535)

### `brk()`

`brk()`通过（发生中断）上移程序的`brk`指针来向内核申请获取内存。

最初`start_brk`和`brk`指向相同的位置

其中关于`Random brk offset`：

  *  **关闭`ASLR`**：`start_brk`和`brk`初始指向数据段（`.data`）/`.bss`段的结尾`end_data`
  *  **开启`ASLR`**：`start_brk`和`brk`初始指向数据段（`.data`）/`.bss`段的结尾`end_data + Random brk offset`

### `mmap()`

`malloc`使用`mmap`创建 私有匿名映射段。

私有匿名映射的主要目的是分配新内存（用`0`填充），并且这个新内存将由调用进程独占使用。

位于图中的`Memory Mapping Segment`段。

# 各个阶段堆内存分布

    
    
    #include <stdio.h>
    #include <stdlib.h>
    #include <pthread.h>
    #include <unistd.h>
    #include <sys/types.h>
    void* threadFunc(void* arg) 
    {
    				// int locate = 1;
            printf("Before malloc in thread 1\\n");
            getchar();
            char* addr = (char*) malloc(1000);
            printf("After malloc and before free in thread 1\\n");
            getchar();
            free(addr);
            printf("After free in thread 1\\n");
            getchar();
    }
    int main() 
    {
            pthread_t t1;
            void* s;
            int ret;
            char* addr;
            // printf("Welcome to per thread arena example::%d\\n",getpid());
            // printf("Before malloc in main thread\\n");
            // getchar();
            addr = (char*) malloc(1000);
            printf("After malloc and before free in main thread\\n");
            getchar();
            free(addr);
            printf("After free in main thread\\n");
            getchar();
            ret = pthread_create(&t1, NULL, threadFunc, NULL);
            if(ret)
            {
                    printf("Thread creation error\\n");
                    return -1;
            }
            ret = pthread_join(t1, &s);
            if(ret)
            {
                    printf("Thread join error\\n");
                    return -1;
            }
            return 0;
    }
    

### 主线程调用`malloc`之前 __`in main thread`

此时由于没有调用`malloc`所以内存中并不会存在`heap`段，并且在线程创建前也是没有线程堆栈的。

 **但注意，此处会有一个小的 “意外”：**

> 注意关注`main`函数注释掉的三行，将他们注释掉的原因在于方便我们更清晰的关注`malloc`的分配策略：

首先说明，`printf`的实现中，会调用 **`__vfprintf_internal`**
这个内部函数：该函数主要用于将可变参数列表格式化为字符串并将其写入指定流。

 **在下列情况中它可能会申请堆空间来存储这些字符串** ：

  * 可变参数列表中包含的参数数量较多，导致格式化后的字符串需要较多的内存来存储。
  * 可变参数列表中包含的参数类型不确定，因此无法预先确定格式化后的字符串长度。

在这些情况下， **`__vfprintf_internal`** 函数可能会动态申请堆空间来存储格式化后的字符串，以确保有足够的内存来容纳这些字符串。

于是就会出现这样的情况

![1671120477_639b465d1bccc618aac38.png!small?1671120458596](https://image.3001.net/images/20221216/1671120477_639b465d1bccc618aac38.png!small?1671120458596)

  

为了探明到底是谁调用了`malloc`于是在跟着往里走走，便发现：

![1671120493_639b466d0f30f7a499059.png!small?1671120474592](https://image.3001.net/images/20221216/1671120493_639b466d0f30f7a499059.png!small?1671120474592)

果然在 **`__vfprintf_internal`中发生了`malloc`的调用（可真靠里啊….）**

 **所以先将前面的`printf`注释掉：**

![1671120505_639b46792ddd31ddd4fcd.png!small?1671120486634](https://image.3001.net/images/20221216/1671120505_639b46792ddd31ddd4fcd.png!small?1671120486634)

此时没有调用`malloc`前，并没有产生`heap`段。

### 主线程调用`malloc`__`in main thread`

之后主线程通过`malloc`申请了`1000`字节的空间，这明显是小于`128KB`这个界限值的，所以此时会通过系统调用`brk()`上移堆区指针分配空间，一共分配了：

![1671120510_639b467ec35668e39edc6.png!small?1671120492205](https://image.3001.net/images/20221216/1671120510_639b467ec35668e39edc6.png!small?1671120492205)

`0x59000 - 0x7a000 = 0x21000`字节的空间，也就是`135148 / 1024 = 132
KB`的空间，远远大于我们需要的`1000`字节的空间。

这`132 KB`的空间的 “名号” 为：`arena.`

又因为他是在主线程中分配的，所以又被称为`main arena.`

每个`arena`中又有多个以链表组织的`chunk`，刚刚`malloc`分配的`1000`字节空间就属于`main
arena`下的一个`chunk`块。

![1671120556_639b46ac314a846bb3f93.png!small?1671120537501](https://image.3001.net/images/20221216/1671120556_639b46ac314a846bb3f93.png!small?1671120537501)

看其中的`Uable size`表示的就是可用大小，也就是刚刚申请的`1000`字节，至于为啥块的总大小为`1008`字节会在后续说明。

 **为什么分配远大于申请的空间？**

由于若每次分配都要进行系统调用切换状态是非常低效的，所以会维持一个类似内存池的结构，比方说上述例子，第一次在主线程中申请后堆空间后，若后续再继续申请堆空间，则会先从这分配的`132
KB`中剩余的部分申请。

直到不够的时候才会通过增加`brk()`（视申请的空间大小而定）上移堆指针（增加`program break
location`）的方式（申请过大则使用`mmap`内存映射）来增加`main arena`的大小。

同理，当`main arena`中有过多空闲内存的时候，也会通过减小`program break location`的方式来缩小`main
arena`的大小。

### 主线程调用`free`__`in main thread`

![1671120565_639b46b5a59fe63ad6402.png!small?1671120547064](https://image.3001.net/images/20221216/1671120565_639b46b5a59fe63ad6402.png!small?1671120547064)

可以看到，在主线程中`free`掉刚刚申请的空间后，`heap`段并没有被释放，有前面的描述这里很好理解，因为后续还有可能要申请堆空间所以堆空间不会直接还给系统，交给内存分配器`ptmalloc`来管理。

释放掉返还的空间并不会直接加入`main arena`中的链表中，而是被加入到`main arena bin`中，这是一种专门用于存储同类型`free
chunk`的双链表。

【但注意，该双向链表并不是一个全新的结构，而是依次指向了原`main arena`中被释放的`chunk`块】

这类用于记录释放后的空闲空间的双向链表称为`bins.`

只要有空间被`free`后，加入了`bins`，那么之后再通过`malloc`申请空间时，就会先从`bins`双链表中寻找符合要求的`chunk.`

### `thread 1`调用`malloc`__`in (thread 1) thread`

> 为了通过`gdb`观察`thread 1`，直接在`threadFunc`打断点运行即可

由于`Linux`中子线程是通过`mmap`映射内存空间，所以其堆是通过`mmap`映射而来，且栈也位于内存映射区

详情见：

[Where are the stacks for the other threads located in a process virtual
address space?](https://stackoverflow.com/questions/44858528/where-are-the-stacks-for-the-other-threads-located-in-a-process-virtual-address)

此处若要向确认其栈空间确实位于`mmap`的内存映射区可以用一个最简单的方案，在线程函数中创建一个变量，观察其地址`int locate =
1;`（原代码中已注释掉）

![1671120618_639b46ea3465659204e5c.png!small?1671120600327](https://image.3001.net/images/20221216/1671120618_639b46ea3465659204e5c.png!small?1671120600327)

而由于该区域是紧邻`libc.so.6`这个位于映射区的动态库的，所以可以确认子线程的栈空间确实位于内存映射区中。

根据刚刚的内存分布图，内存中 **栈区 内存映射去 堆区 的虚拟内存地址是依次递减的。**

![1671120649_639b4709a204888a6a42b.png!small?1671120631583](https://image.3001.net/images/20221216/1671120649_639b4709a204888a6a42b.png!small?1671120631583)

所以为该进程分配的堆区也确实位于刚刚栈区的上方（低地址），其大小于主线程中通过`brk()`分配的大小相同，也是`0x21000`也就是`132
KB`即`thread1`的`arena.`

### `thread 1`调用`free`__`in (thread 1) thread`

流程同主线程

## 关于 Arena

结合前面的介绍，可知`arena`是一种 **用于组织堆分配块的数据结构。**

该单词`"arena"`的原意是一个大型的比赛场馆或活动场所，比如一个体育馆或剧院。在这种情况下，`arena`可能是因为它用来组织和管理大量的内存块，类似于一个体育馆用来组织和管理大量的比赛或活动

下述参考来源于网络，并没有进行验证：

* * *

虽然看似上述程序中每个进程申请堆空间时都会有一个独立的`arena`，但`arena`的数量并不是可以随着现成的增加随意增加的，是有着最大值限制的。

systems| number of arena  
---|---  
32bits| 2 x number of cpu cores + 1  
64bits| 8 x number of cpu cores + 1  
  
若核心数对应的最大`arena`数不足以支撑新产生的线程，则`ptmalloc`则会遍历所有可用的`arena`，并尝试加锁，若加锁成功则将该`arena`返回给申请的线程，此`arena`会被当前子线程和原来使用的线程共享使用，若找不到（当前所有的`arena`都在使用中）则当前子线程的`malloc`被阻塞等待。

* * *

# 堆内存管理

在`ptmalloc`中对于堆的管理，主要涉及到`3`种数据结构，但若是直接列出每种数据结构的结构体，未免过于枯燥且难以理解，所以我们还是从刚刚的程序分析，分析结构体中的每一个字段在内存中的位置。

首先出场的是`_heap_info`这个结构体

## _heap_info

> 注意：该结构体`main arena`中并不存在，子线程`thread
> arena`中是存在的，而且每当剩余空间不足重新申请一块`heap`的时候就会产生一个该结构体。

其作用一种用于在程序中存储堆信息的数据结构，具体存储了什么信息先来看他的结构体。

    
    
    typedef struct _heap_info
    {
      mstate ar_ptr;                /* arena for this heap. */
      struct _heap_info *prev;      /* Previous heap. */
      size_t size;                  /* Current size in bytes. */
      size_t mprotect_size;         /* Size in bytes that has been mprotected
                                       PROT_READ|PROT_WRITE.  */
       /* Make sure the following data is properly aligned, particularly
          that sizeof (heap_info) + 2 * SIZE_SZ is a multiple of
          MALLOC_ALIGNMENT. */
      char pad[-6 * SIZE_SZ & MALLOC_ALIGN_MASK];
    } heap_info;
    

// **`pad`** 字段用来确保该结构在内存中是正确对齐的，无需特别关注其计算含义。

###  **单 heap segment 情况**

> 单`heap`段时只有一个`_heap_info`结构，位于堆区的最开始。

拿出一张很经典的图

![1671120668_639b471c4c62da67270c6.png!small?1671120649756](https://image.3001.net/images/20221216/1671120668_639b471c4c62da67270c6.png!small?1671120649756)

    
    
    不过目前来说它过于复杂，所以先画一个简化版，再慢慢丰富它。
    

![1671120675_639b4723e19fdf534c1df.png!small?1671120657812](https://image.3001.net/images/20221216/1671120675_639b4723e19fdf534c1df.png!small?1671120657812)

    
    
    嗯~这样就简单多啦！
    

此处就以刚刚程序中，线程里通过内存映射创建的一块堆区为示例：

【 注意：此处堆区指的是通过`brk`上移获取的堆空间与通过`mmap`映射的内存空间】

线程`thread 1`中的堆区范围：

![1671120701_639b473d02ec795a2c588.png!small?1671120682160](https://image.3001.net/images/20221216/1671120701_639b473d02ec795a2c588.png!small?1671120682160)

我们来看看这段堆区中`_heap_info`结构体中的数值是什么（由于从第`4 * 8 = 32`字节开始都为填充部分，所以只看前`32`字节的数据）。

![1671120709_639b474507864966f818c.png!small?1671120690426](https://image.3001.net/images/20221216/1671120709_639b474507864966f818c.png!small?1671120690426)

依次对应下来：

  * `ar_ptr`：`0x00007ffff0000030`指向`malloc_state`结构体的指针

接下来会详细来讲

  * `prev`：`0x0000000000000000`指向上一个堆的指针

由于就一块所以为`NULL`

  * `size`：`0x0000000000021000`当前堆的字节大小

和刚才算出的一样`132 KB`

  * `mprotect_size`：`0x0000000000021000`当前已被标记为可读写的堆的字节大小

和刚才算出的一样`132 KB`从刚刚的截图也可看出这段空间都是可读可写的

###  **多 heap segment 情况**

这很好理解，启用刚刚为`NULL`的`prev`指针就可以啦！

但注意，上面说了，`prev`是指向上一个堆的指针，所以是将第二个`heap_info`结构体的`prev`成员指向了第一个`heap_info`结构体的起始位置（`ar_ptr`），这样就构成了一个单链表，方便后续管理。

【先提前说一下：`malloc_state`这个结构体只存在于第一块`heap`中，后续映射来的 heap 中是不存在该结构体的】

所以简化后的示意图为：

![1671120719_639b474f3a7270003a2a4.png!small?1671120700638](https://image.3001.net/images/20221216/1671120719_639b474f3a7270003a2a4.png!small?1671120700638)

## malloc_chunk

由于`malloc_state`涉及到了整个`arena`的管理，所以先介绍`chunk`块的结构与其他的机制，最后再回归到`malloc_state`中将会更好理解。

前面说过，为了便于管理和更加高效的利用内存，第一次申请堆空间时，实际上是申请了一大块远大于所申请空间的`arena`，而真正返回给用户实际申请大小的是
`arena`中的一个 `chunk`，但刚刚也同样观测到，最终返回的大小比用户实际申请的空间还要大`8`字节，其中每个 `chunk`都由一个结构体
`malloc_chunk`表示，也称为 `chunk header.`

任何的堆管理器都是以`chunk`为单位进行堆内存管理的，所以对于每一个 chunk 块中肯定要存在着控制信息，用于指示当前`chunk`的基本信息。

    
    
    struct malloc_chunk 
    {
      /* #define INTERNAL_SIZE_T size_t */
      INTERNAL_SIZE_T      prev_size;  /* Size of previous chunk (if free).  */
      INTERNAL_SIZE_T      size;       /* Size in bytes, including overhead. */
      struct malloc_chunk* fd;         /* double links -- used only if free. 这两个指针只在free chunk中存在*/
      struct malloc_chunk* bk;
    
      /* Only used for large blocks: pointer to next larger size.  */
      struct malloc_chunk* fd_nextsize; /* double links -- used only if free. */
      struct malloc_chunk* bk_nextsize;
    };
    

堆内存管理器要求每个`chunk`块的大小必须为`8`的整数倍，而通过上述结构体的`size`字段正是用于描述当前`chunk`块大小的，既然必须是`8`的整数倍，那么对于`size`这个数二进制下，低`3`位就无效了。（简单来说：一旦这三位有哪些位被置`1`了，都会导致最终的数一定不是`8`的倍数）

所以这空出来的`3`位，就被当作了当前`chunk`的标志位，每一位都表示这当前`chunk`块一个状态信息，具体的含义会在接下来说明。

### chunk 块的分类

`chunk`总共分为`4`类：

  * `allocated chunk`已被分配使用的 chunk 块
  * `free chunk`未被分配未使用的 chunk 块
  * `top chunk`
  * `last remainder chunk`

### chunk 的组织结构

> 先简单介绍一下 chunk 块的组织结构，详细的介绍，将在会后面说明。

 **chunk 在堆内存中是连续的，并不是直接由指针构成的链表，而是通过 prev_size 和 size 构成的隐式链表。**

这样做的好处在于：在进行分配操作的时候，堆内存管理器可以通过遍历整个堆内存的 chunk，分析每个 chunk 的 size 字段，进而找到合适的
chunk，而且在合并不同 chunk 时，可以减少内存碎片。

若不这么做，chunk 的合并只能向下合并，必须从头遍历整个堆，然后加以合并，意味着每次进行 chunk 释放操作消耗的时间与堆的大小成线性关系。

### allocated chunk

> 已被分配使用的`chunk`块

![1671120739_639b476353288ec3459a7.png!small?1671120720657](https://image.3001.net/images/20221216/1671120739_639b476353288ec3459a7.png!small?1671120720657)

图 1-1

下图可能与上图存在差异，这并不是错误，后面会进行介绍：

![1671120742_639b4766d19516909e749.png!small?1671120724244](https://image.3001.net/images/20221216/1671120742_639b4766d19516909e749.png!small?1671120724244)

图 1-2

相关参数含义：

  * prev_size ：该参数为 malloc_chunk 中第一个字段，也就是上图中自上而下第一个的大方框中，根据当前 chunk 前一个 chunk 类型的不同，此处有两种含义：

    * 若前一个 chunk 为 free chunk 则 prev_size 表示前一个 free chunk 的大小
    * 若前一个 chunk 为 allocated chunk 则 prev_size 没有特殊含义，此处保存的是上一个 allocated chunk 块剩余的用户数据（主要是为了复用该控件）
  * size ：该参数为 malloc_chunk 中第二个字段，也就是上图中自上而下第二个大方框中，该字段共由 4 部分组成：

    * 前 **三位**
      * N PREV_INUSE 前一个 chunk 是否为 allocated chunk
      * M IS_MAPPED 当前 chunk 是否是通过 mmap 系统调用产生的
      * P NON_MAIN_ARENA 当前 chunk 是否属于 main arena (也就是主线程的 arena)

拿来之前的一张图来，当前可以看 flags ：

    * PREV_INUSE 置位，说明前一个 chunk 为已分配 chunk 这么解释对于除第一个被分配的内存块的 size 字段以外内存块的 P 位是正确的，但由于该图中的分配是主线程中的第一次分配，对于堆中第一个被分配的内存块的 size 字段的 P 位都会被置为 1

【目的在于：防止非法访问前面的内存】

    * IS_MMAPPED 没置位，说明当前堆是通过 brk() 上移分配的

    * NON_MAIN_ARENA 没置位，说明当前为主线程 arena

![1671120751_639b476f51e90c414f02f.png!small?1671120732584](https://image.3001.net/images/20221216/1671120751_639b476f51e90c414f02f.png!small?1671120732584)

    *  **其余位** ：当前 chunk 大小

大小必须是 SIZE_SZ 的整数倍，如果申请的大小不是其整数倍，会被填充。

      * 32位系统 SIZE_SZ = 4
      * 64位系统 SIZE_SZ = 8

上图中我们用 malloc 申请了 1000 字节的空间最终分配了 1008 字节的原因在于，由于该 chunk 的前一块不是 free chunk
所以并不存在第一个 prev_size 或者说 prev_size 的位置保存的是前一块中的数据，那么其实附加信息只有 size ，由于 64 位系统/程序
所以附加了 8 字节的空间，又因为 1008 是 2 * SIZE_SZ 的倍数，所以无需填充。

  * 用户数据 for user_data

用户数据区域会被置 0 ，准备存入用户的数据

### free chunk

![1671120757_639b477553b2db83088c1.png!small?1671120738603](https://image.3001.net/images/20221216/1671120757_639b477553b2db83088c1.png!small?1671120738603)

图 1-3

有了前面的图，此处就直接看原图了。

  * prev_size ：为了防止碎片化，堆中不存在两个相邻的 free chunk （如果存在，则会被堆管理器合并为一个），因此对于 free chunk ，其 prev_size 区域中一定包含的是上一个 chunk 中一部分的有效数据或者为了地址对齐所做的填充对齐 padding

  * size ：与 allocated chunk 一致，表示当前 chunk 的大小，其标志位 N M P 也同上述含义相同

  * fd ：前向指针

指向当前 free chunk 在同一个 bin（一种用于加快内存分配和释放效率的显示链表）的下一个 free chunk

  * bk ：后向指针

指向当前 free chunk 在同一个 bin 的上一个 free chunk

###  **top chunk**

该 chunk 位于一个 arena 的最顶部（即最高内存地址处），不属于任何 bin.

在当前的 heap 所有的 free chunk（无论哪种 bin 中）都无法满足用户请求的内存大小的时候，将会将该 chunk 的空间 ，分配给用户使用。

如果 top chunk 的大小比用户请求的大小要大的话，就将该 top chunk 分作两部分：用户请求的 chunk 和 剩余的部分。（成为新的 top
chunk）

否则，就需要扩展 heap 或分配新的 heap 了，在 main arena 中通过 sbrk 扩展 heap，而在 thread arena 中通过
mmap 分配新的 heap.

###  **Last Remainder Chunk**

该 chunk 涉及到另一个非常重要的显示链表 bin ，在介绍完 bin 后再回来说他。

### 隐式链表

若不对 chunk 块进行分类，则默认所有的 chunk 块都是长成这个样子的：

![1671120762_639b477a2527bf120b4f6.png!small?1671120743821](https://image.3001.net/images/20221216/1671120762_639b477a2527bf120b4f6.png!small?1671120743821)

假设当前有三个 chunk 块，分别将其命名为：

  * FREE_A
  * ALLOCATE_B
  * FREE_C

通过其名字就可以知道当前三个 chunk 块的结构关系为： **一个已经分配的块在两个未使用的块之间**

那么就有了这样的问题，若要释放当前的 ALLOCATE_B 块，该如何将 FREE_A ALLOCATE_B FREE_C 合成一个 free chunk
(之前说过是不存在相邻 free chunk 的)？

这里主要的问题在于如何合并 FREE_A 与 ALLOCATE_B FREE_C，因为 ALLOCATE_B 和 FREE_C
是很好合并的，ALLOCATE_B 只要向下获取到 FREE_C 的 chunk size 参数，也就知道了 FREE_C 的大小，直接合并即可。

但 ALLOCATE_B 块 和 FREE_A 之间该如何合并呢？

这就提出了带边界的标记的合并技术，而且要对 chunk 块进行分类，因为 allocated chunk 是不需要合并的，自然也就不存在这个问题。

所谓的带边界标记中的边界标记，也就是在原默认 chunk 块的边界处附加一个相邻 chunk 块的信息，于是自然而然， **当前 chunk 块为 free
chunk 时，就会为当前 free chunk 块 附加一个尾部，该尾部与其头部 size 字段一致。**

【allocated chunk 是不会附加该尾部的】

![1671120765_639b477df21dbae4d5bb8.png!small?1671120747412](https://image.3001.net/images/20221216/1671120765_639b477df21dbae4d5bb8.png!small?1671120747412)

但此时还是拥有优化空间的，当前 free chunk 没有必要完全复制一份其首部 chunk size到尾部，因为若该尾部交给 free chunk
来添加，那无论该 free chunk 所处什么位置，都需要添加一个尾部，所以完全可以将这个任务交给 allocated chunk 来完成，只有当
allocated chunk 前为 free chunk 时，在 allocated chunk 的 chunk size 前记录前一个 free
chunk 的大小 size 即可，于是我们最常见的一种格式（图 1-2）便出现了：

![1671120769_639b47810aa98e7956f6b.png!small?1671120751256](https://image.3001.net/images/20221216/1671120769_639b47810aa98e7956f6b.png!small?1671120751256)

若前面不是 free chunk 则 prev_size 用于保存前一个 chunk 块的剩余数据或 padding 填充即可

有了这样的结构，FREE_A 与 ALLOCATE_B 的合并就变得简单了。

##  **malloc_state**

malloc_state 用于表示 arena 的信息，因此也被称为 arena header ，每个线程只含有个 arena header.

    
    
    struct malloc_state
    {
      /* Serialize access.  */
      mutex_t mutex;
      
      /* Flags (formerly in max_fast).  */
      int flags;
    
      /* Fastbins */
      mfastbinptr fastbinsY[NFASTBINS];
    
      /* Base of the topmost chunk -- not otherwise kept in a bin */
      mchunkptr top;
    
      /* The remainder from the most recent split of a small request */
      mchunkptr last_remainder;
    
      /* Normal bins packed as described above */
      mchunkptr bins[NBINS * 2 - 2];
    
      /* Bitmap of bins */
      unsigned int binmap[BINMAPSIZE];
    
      /* Linked list */
      struct malloc_state *next;
    
      /* Linked list for free arenas.  */
      struct malloc_state *next_free;
    
      /* Memory allocated from the system in this arena.  */
      INTERNAL_SIZE_T system_mem;
      INTERNAL_SIZE_T max_system_mem;
    };
    

该结构的介绍同样需要先说 bin ，所以也在后续说明。

# 参考文章/深入学习

[Syscalls used by
malloc.](https://sploitfun.wordpress.com/2015/02/11/syscalls-used-by-malloc/)

[linux进程的内存布局](https://lishiwen4.github.io/linux/linux-process-memory-location)

[Heap--初探--chunk的获取与释放 |
Squarer](https://squarepants0.github.io/2020/09/07/heap-chu-tan-chunk-de-huo-qu-yu-shi-fang/#toc-heading-1)

[Linux 堆内存管理深入分析](https://murphypei.github.io/blog/2019/01/linux-heap)

[Linux堆内存管理深入分析上](https://introspelliam.github.io/2017/09/10/pwn/Linux%E5%A0%86%E5%86%85%E5%AD%98%E7%AE%A1%E7%90%86%E6%B7%B1%E5%85%A5%E5%88%86%E6%9E%90%E4%B8%8A/)

[Understanding glibc
malloc](https://sploitfun.wordpress.com/2015/02/10/understanding-glibc-malloc/comment-page-1/)

