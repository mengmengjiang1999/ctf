**在glibc2.26版本以后，出现了一个新的bin被称为TcacheBin，本文将详细的讲解一下TcacheBin的相关知识以及漏洞利用**

# TcacheBin相关代码

## 相关的宏

    
    
    #if USE_TCACHE
    /* We want 64 entries.  This is an arbitrary limit, which tunables can reduce.  */
    # define TCACHE_MAX_BINS        64
    # define MAX_TCACHE_SIZE    tidx2usize (TCACHE_MAX_BINS-1)
    
    /* Only used to pre-fill the tunables.  */
    # define tidx2usize(idx)    (((size_t) idx) * MALLOC_ALIGNMENT + MINSIZE - SIZE_SZ)
    
    /* When "x" is from chunksize().  */
    # define csize2tidx(x) (((x) - MINSIZE + MALLOC_ALIGNMENT - 1) / MALLOC_ALIGNMENT)
    /* When "x" is a user-provided size.  */
    # define usize2tidx(x) csize2tidx (request2size (x))
    
    /* With rounding and alignment, the bins are...
       idx 0   bytes 0..24 (64-bit) or 0..12 (32-bit)
       idx 1   bytes 25..40 or 13..20
       idx 2   bytes 41..56 or 21..28
       etc.  */
    
    /* This is another arbitrary limit, which tunables can change.  Each
       tcache bin will hold at most this number of chunks.  */
    # define TCACHE_FILL_COUNT 7
    #endif
    

宏比较多，可以直接从glibc中进行查看。简单来说就是glibc为每个线程都分配了一个TcacheBin，并且bin数组为64个，每个bin最多可以存放7个chunk。在32位系统中，bin会存放12-512字节的chunk，在64位系统中bin会存放24-1032字节的chunk。也就是说符合这些大小的chunk被释放后不会先加入fastbin，而是会先放入TcacheBin中。

## 声明的结构体

    
    
    /* We overlay this structure on the user-data portion of a chunk when
       the chunk is stored in the per-thread cache.  */
    typedef struct tcache_entry
    {
      struct tcache_entry *next;
    } tcache_entry;
    
    /* There is one of these for each thread, which contains the
       per-thread cache (hence "tcache_perthread_struct").  Keeping
       overall size low is mildly important.  Note that COUNTS and ENTRIES
       are redundant (we could have just counted the linked list each
       time), this is for performance reasons.  */
    typedef struct tcache_perthread_struct
    {
      char counts[TCACHE_MAX_BINS];
      tcache_entry *entries[TCACHE_MAX_BINS];
    } tcache_perthread_struct;
    
    static __thread tcache_perthread_struct *tcache = NULL;
    

TcacheBin新定义了两个结构体，第一个结构体里面存入一个指针，该指针指向下一个chunk。重点在第二个结构体，第二个结构体中有两个数组，其中第一个数组存放的是每一个bin链表有多少chunk，第二个则是每个bin数组中的内容存放fd指针，指向下一个chunk，并且TcacheBin以单链表构成，每个chunk的fd指针指向下一个chunk的fd字段。![AIO\)\)L\]MK_\)G@DH45ZZ~6%R.png](https://image.3001.net/images/20211014/1634191983_6167ca6f9e8697636b538.png!small)

# 什么时候会用到TcacheBin

**free：**在释放chunk的时候，如果chunk符合Tcachebin的大小，并且该bin还没有被装满(没有七个)，则会优先放入TcacheBin中

 **malloc：**

  1. 当我们使用malloc的时候，返回一个chunk，并且该chunk是从fastbin中返回的，那么该chunk所对应下标的所有chunk都会被放入TcacheBin(当然，前提是Tcachebin没有被装满)，而且由于fastbin和Tcachebin都是先进后出，所以就会导致chunk在移动完以后chunk的顺序和fastbin中的顺序相反。

  2. smallbin中的也一样，返回的一个chunk属于smallbin，那么smallbin中对应的chunk就会全部放入Tcachebin(前提是没有装满)

  3. 当出现堆块的合并等其它情况的时候，每一个符合条件的chunk都会优先放入TcacheBin中，而不是直接返回(除非Tcache已满)。寻找结束后Tcache会返回其中一个

**比较重要的一点，当我们调用malloc的时候，其实是先调用libc_malloc然后调用int_malloc，但是如果我们请求的大小在Tcachebin中有符合的chunk那么就会在libc_malloc中返回该chunk，而不会调用int_malloc**

 **我们在处理chunk的过程中，如果在Tcache中的chunk已满，那么会直接返回最后一个chunk；binning code
结束后，如果没有直接返回（如上），那么如果有至少一个符合要求的 chunk 被找到，则返回最后一个。**

 **tcache 中的 chunk 不会被合并，无论是相邻 chunk，还是 chunk 和 top chunk。因为这些 chunk 会被标记为
inuse。**

# TcacheBin的检查机制

    
    
    /* Caller must ensure that we know tc_idx is valid and there's room
       for more chunks.  */
    static __always_inline void
    tcache_put (mchunkptr chunk, size_t tc_idx)
    {
      tcache_entry *e = (tcache_entry *) chunk2mem (chunk);
      assert (tc_idx < TCACHE_MAX_BINS);
      e->next = tcache->entries[tc_idx];
      tcache->entries[tc_idx] = e;
      ++(tcache->counts[tc_idx]);
    }
    
    /* Caller must ensure that we know tc_idx is valid and there's
       available chunks to remove.  */
    static __always_inline void *
    tcache_get (size_t tc_idx)
    {
      tcache_entry *e = tcache->entries[tc_idx];
      assert (tc_idx < TCACHE_MAX_BINS);
      assert (tcache->entries[tc_idx] > 0);
      tcache->entries[tc_idx] = e->next;
      --(tcache->counts[tc_idx]);
      return (void *) e;
    }
    

这两个函数是TcacheBin取出和放入chunk，这两个函数基本决定了Tcachebin的检查机制非常简陋，甚至比fastbin还要简陋，所以很多漏洞我们都可以使用。我们可以看到glibc只对tc_idx做了一些检查，于是我们可以利用很多漏洞

# Double Free

我们知道fastbin中为了防止double free，glibc只在其头部进行了检查，而在tcachebin中连检查都没有。我们可以直接连续两次释放。

    
    
    #include <stdlib.h>
    #include <stdio.h>
    
    int main() {
        void *p1 = malloc(0x10);
        fprintf(stderr, "1st malloc(0x10): %p\n", p1);
        fprintf(stderr, "Freeing the first one\n");
        free(p1);
        fprintf(stderr, "Freeing the first one again\n");
        free(p1);
        fprintf(stderr, "2nd malloc(0x10): %p\n", malloc(0x10));
        fprintf(stderr, "3rd malloc(0x10): %p\n", malloc(0x10));
    }
    

然后我们看一下输出结果![image.png](https://image.3001.net/images/20211014/1634202566_6167f3c681d4496cdf227.png!small)其原理和fastbin一样，也是形成环然后可以无限申请  
![image.png](https://image.3001.net/images/20211014/1634206540_6168034c35937ba03137a.png!small)

# 绕过Tcache

如果程序在编写的时候对Tcache进行了一些保护，需要我们绕过Tcache，那么此时我们应该怎么做呢？

此时有两种思路，首先是填满Tcache，填满以后再次进行malloc释放以后就会进入fastbin

    
    
    #include <stdio.h>
    #include <stdlib.h>
    int main(){
    	int *p[7];
    	for(int i = 0;i<=7;i++){
    			p[i] = malloc(0x20);
    
    
    	}
    	for(int i = 0;i<=7;i++)
    			free(p[i]);
    
    	int *a = malloc(0x20);
    	free(a);
    	return 0;
    
    }
    

程序运行后将会填满Tcache，然后再次释放就会释放到fastbin中。释放到smallbin中同理。

第二种思路就是尝试找到结构体，直接更改结构体内的chunk数。当我们遇到限制创建chunk时，例如用户只能创建5个chunk，大小都为fastbin的大小，此时我们想要绕过就只能通过更改结构体了。当我们开辟堆空间的时候，Tcache结构体的空间也将会被开辟在堆![image.png](https://image.3001.net/images/20211014/1634213419_61681e2bf0b765149957d.png!small)我们完全可以进行篡改，例如我们可以把记录chunk个数的地方改为-1，由于定义的时候是无符号整数，所以如果被改为-1其结果就是变得非常大。然后我们就可以成功绕过Tcache。

**其实TcacheBin还有好多漏洞都可以进行利用，可以在smallbin和fastbin进行利用的方式基本都可以在Tcachebin中使用。在glibc2.29版本中，给Tcache新增了一些检查，这个大家可以自行了解一下**

 **本文参考自[glibc tcache 机制](https://firmianay.gitbooks.io/ctf-all-in-one/content/doc/4.14_glibc_tcache.html)、[Tcache attack](https://ctf-wiki.org/pwn/linux/user-mode/heap/ptmalloc2/tcache-attack/)、[Tcache
Attack学习记录](https://www.cnblogs.com/Theffth-blog/p/12790720.html)**

