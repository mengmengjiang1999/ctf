**之前讲解了malloc_consolidate函数，我们知道了函数大概运行了一些什么。在该函数中有一个很重要的函数——malloc_init_state，负责了bins的初始化**

    
    
    {
      int     i;
      mbinptr bin;
    
      /* Establish circular links for normal bins */
      for (i = 1; i < NBINS; ++i) {
        bin = bin_at(av,i);
        bin->fd = bin->bk = bin;
      }
    
    #if MORECORE_CONTIGUOUS
      if (av != &main_arena)
    #endif
        set_noncontiguous(av);
    
      set_max_fast(av, DEFAULT_MXFAST);
    
      av->top            = initial_top(av);
    }
    
    #define bin_at(m,i) ((mbinptr)((char*)&((m)->bins[(i)<<1]) - (SIZE_SZ<<1)))
    
    
    

代码挺短的，但是知识点比较多

# bins的初始化

首先看源码的开头

    
    
    for (i = 1; i < NBINS; ++i) {
        bin = bin_at(av,i);
        bin->fd = bin->bk = bin;
      }
    

最开始很明显就是清空所有的bins，使用for循环进行遍历，然后将bin的fd和bk指针全部指向自己

# 设置参数

    
    
    #if MORECORE_CONTIGUOUS
      if (av != &main_arena)
    #endif
        set_noncontiguous(av);
    
      set_max_fast(av, DEFAULT_MXFAST);
    
      av->top            = initial_top(av);
    }
    

首先先判断该arena是否为main_arena,并且设置max_fast参数的倒数第二个比特，并且设置max_fast和top字段，我们具体看一下做了什么

    
    
    #define set_noncontiguous(M)   ((M)->max_fast |=  NONCONTIGUOUS_BIT)
    
    #define set_max_fast(M, s) \
      (M)->max_fast = (((s) == 0)? SMALLBIN_WIDTH: request2size(s)) | \
      FASTCHUNKS_BIT | \
      ((M)->max_fast &  NONCONTIGUOUS_BIT)
      
    #define initial_top(M) (unsorted_chunks(M))
    
    #define unsorted_chunks(M) (bin_at(M, 1))
    
    #define DEFAULT_MXFAST 64
    

我们一个一个来看。

## MORECORE

首先来了解一下NONCONTIGUOUS_BIT。这个是max_fast字段的倒数第二个比特位，之前已经了解过max_fast字段的低两位是标志位。倒数第二个比特位就是NONCONTIGUOUS_BIT。该比特位表示MORECORE没有返回连续的空间。

我们先来了解一下MORECORE。`#define MORECORE
sbrk`。我们首先要肯定这样的一个前提：主分配区扩展堆空间使用的是sbrk()；非主分配区使用mmap()先进行匿名映射，然后再根据申请的堆块大小进行切分，mmap映射区是不保证虚拟内存地址连续的。于是我们就有了这样的一个想法：主分配区默认返回连续的地址空间，非主分配区默认分配不连续的地址空间(有可能碰巧连续，但是我们不考虑这种情况)。也就是说我们的MORECORE宏是可以人为进行定义的，可以用sbrk也可以使用mmap。于是我们也就知道了，主分配区该位一般为0，非主分配区一般为1.

而`set_noncontiguous(av);`就是设置NONCONTIGUOUS_BIT。

## set_max_fast

上面的宏定义已经有了。我们直接来进行计算就行

    
    
    #define set_max_fast(M, s) \
      (M)->max_fast = (((s) == 0)? SMALLBIN_WIDTH: request2size(s)) | \
      FASTCHUNKS_BIT | \
      ((M)->max_fast &  NONCONTIGUOUS_BIT)
    

我们直接带入就可以了。

## 设置top字段

我们也已经知道了宏，`((((mbinptr)((char*)&((av)->bins[(1)<<1]) -((sizeof(size_t))<<1)))))`这个就是我们真正的公式。也就是把top字段指向bins头。

**这就是malloc_init_state，至此我们才算真正知道了malloc_consolidate到底干了什么。首先是对fastbin进行清空并且合并，然后才对bins进行清空，并且设置一些参数，我们可以继续回到int_malloc函数中去了**

**本文参考自[https://www.cxyzjd.com/article/luozhaotian/80267712](ptmalloc%E5%A0%86%E6%95%B0%E6%8D%AE%E7%BB%93%E6%9E%84)**

