# heap segment与arena的关系

再来回顾一下heap header和arena header的数据结构

    
    
    typedef struct _heap_info
    {
      mstate ar_ptr; /* 堆对应的 arena 的地址 */
      struct _heap_info *prev; /* 由于一个线程申请一个堆之后，可能会使用完，之后就必须得再次申请。因此，一个可能会有多个堆。prev即记录了上一个 heap_info 的地址。这里可以看到每个堆的 heap_info 是通过单向链表进行链接的。 */
      size_t size;   /*size 表示当前堆的大小 */
      size_t mprotect_size; /* 最后一部分确保对齐  */
      /* Make sure the following data is properly aligned, particularly
         that sizeof (heap_info) + 2 * SIZE_SZ is a multiple of
         MALLOC_ALIGNMENT. */
      char pad[-6 * SIZE_SZ & MALLOC_ALIGN_MASK];
    } heap_info;
    
    
    
    struct malloc_state
    {
      /* 该变量用于控制程序串行访问同一个分配区，当一个线程获取了分配区之后，其它线程要想访问该分配区，就必须等待该线程分配完成候才能够使用。(意思就是当线程数多余arena数时，想要复用arena必须等待arena空闲)  */
      mutex_t mutex;
      /*flags记录了分配区的一些标志，比如 bit0 记录了分配区是否有 fast bin chunk ，bit1 标识分配区是否能返回连续的虚拟地址空间(具体可以自己查)  */
      int flags;
      /* 存放每个 fast chunk 链表头部的指针 */
      mfastbinptr fastbinsY[NFASTBINS];
      /* 指向分配区的 top chunk */
      mchunkptr top;
      /* 最新的 chunk 分割之后剩下的那部分 */
      mchunkptr last_remainder;
      /* 用于存储 unstored bin，small bins 和 large bins 的 chunk 链表。 */
      mchunkptr bins[NBINS * 2 - 2];
      /* ptmalloc 用一个 bit 来标识某一个 bin 中是否包含空闲 chunk */
      unsigned int binmap[BINMAPSIZE];
      /* Linked list */
      struct malloc_state *next;
      /* 空闲状态下的arena的链表  */
      struct malloc_state *next_free;
      /* 在这个arena中从系统分配的内存。  */
      INTERNAL_SIZE_T system_mem;
      INTERNAL_SIZE_T max_system_mem;
    };
    

上面有一些数据结构可能比较陌生，我们再补充一些有关chunk的其他知识

## Top chunk

程序第一次进行 malloc 的时候，heap 会被分为两块，一块给用户，剩下的那块就是 top
chunk。当一个chunk处于一个arena的最顶部(最高内存地址)的时候，就被称为top
chunk。该chunk不属于任何bin(chunk被释放以后就被放在bin内，后面会细讲)，而是在系统当前的所有freechunk都无法满足用户请求的内存大小的时候，该chunk会被分配给用户使用(后备隐藏能源)。  
然后问题又来了，top chunk和用户请求的大小也不一定一样啊，于是heap会这样分配：

> 当用户申请的chunk小于top chunk的时候，top
> chunk将会把自己分成两份，用户请求的那一份chunk和剩余的chunk。用户可以使用请求的chunk，剩余的chunk会作为新的top
> chunk存在
>
> 如果用户请求的内存大于top
> chunk，那么就只能扩展heap或者分配新的heap。之前已经说过，主线程只有一个heap，通过调用brk升高堆顶来扩展heap，而其他线程则会使用mmap分配新的heap

## 一个主线程一个其他线程(其他线程只有一个heap)

接下来我们就可以处理一下heap和arena之间的联系。直接大佬的图![image.png](https://image.3001.net/images/20210910/1631276695_613b4e97a8898045a7c0b.png!small)解读一下这个图，首先看只有主线程的arena，malloc_state的top(前面说了，top字段是指向top
chunk的)字段，而为什么会把主线程的arena头给取出来呢？前面也讲到过，主线程的arena并不在heap segment中，而是在data
segment中，所以要取出来表示。那为什么图中的top指向的是malloc_chunk呢？我们来看看top的原英文注释

    
    
    /* Base of the topmost chunk -- not otherwise kept in a bin */
    

我们来看一下这句话，它的意思是top会指向top
chunk的底部(base有基础的意思，在这里翻译为底部，后面也写了，不以任何方式存储在bin中)，所以在途中显示是指向malloc
chunk(因为传统表示指针就是指向顶部，top chunk的底部也就是malloc chunk的顶部)  
  
然后看Thread Arena，在heap_info中，ar_ptr字段指向对应的arena地址，然后malloc_state中的top字段指向top
chunk的底部。

## 当其他线程有多个heap的情况

一般情况下，当一个线程请求多个heap，这些heap是不连续的。所以有了下面的大佬图![image.png](https://image.3001.net/images/20210910/1631278101_613b54155493654e277a7.png!small)这里的关系感觉有点混乱。所以要好好的捋一捋
。首先ar_ptr字段指向了malloc_state，然后malloc_state中的top字段指向的新的top chunk底部，注意原来的top
chunk被free了，进入了bin，然后heap info中的prev字段指向了原先的heap
info的起始位置。这样就构成了一个链表的结构，可以方便管理。

 **这样，三个比较重要的数据结构(malloc_state、heap_info、malloc_chunk)也就产生了联系**

 **本文参考自[ctfwiki](https://ctf-wiki.org/pwn/linux/user-mode/heap/ptmalloc2/heap-structure/#_5)、[知乎阿里聚安全](https://zhuanlan.zhihu.com/p/24753861)，感谢大佬和freebuf**

