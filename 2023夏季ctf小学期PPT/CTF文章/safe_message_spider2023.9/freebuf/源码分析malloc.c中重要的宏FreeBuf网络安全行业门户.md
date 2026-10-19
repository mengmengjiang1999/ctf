**我们之前讲了不少的漏洞，但是这只是原理上的，我们想要更好的利用，少不了分析一些源码。我们首先来分析一下malloc.c中比较重要的宏**

# request2size

    
    
    #define request2size(req)                                         \
      (((req) + SIZE_SZ + MALLOC_ALIGN_MASK < MINSIZE)  ?             \
       MINSIZE :                                                      \
       ((req) + SIZE_SZ + MALLOC_ALIGN_MASK) & ~MALLOC_ALIGN_MASK)
    
    #define MALLOC_ALIGN_MASK      (MALLOC_ALIGNMENT - 1)
    
    #define MALLOC_ALIGNMENT       (2 * SIZE_SZ)
    
    #define MINSIZE  \
      (unsigned long)(((MIN_CHUNK_SIZE+MALLOC_ALIGN_MASK) & ~MALLOC_ALIGN_MASK))
    
    #define MIN_CHUNK_SIZE        (sizeof(struct malloc_chunk))
    
    struct malloc_chunk {
    
      INTERNAL_SIZE_T      prev_size;  /* Size of previous chunk (if free).  */
      INTERNAL_SIZE_T      size;       /* Size in bytes, including overhead. */
    
      struct malloc_chunk* fd;         /* double links -- used only if free. */
      struct malloc_chunk* bk;
    };
    

首先是request2size宏，我在glibc中找到了所有和它相关的宏定义。这个request2size宏定义是为了实现用户请求的内存块和malloc实际分配的内存块做一个转换。req就是我们要请求的内存块。

首先请求的时候首先进行比较，req+8+15<32，也就是说当我们申请分配0~8个字节的时候，实际上都会给我们分配32字节的内存，也就是0x20。

当我们申请的字节数大于8的时候，实际会分配给我们（req+0x8+0xf）&（~0xf）个字节。举例来说例如我们申请0x12字节的内存，实际分配也就是0x20字节。

大家计算以后会发现，这样请求可以利用到下一个chunk的prevsize，并且可以使内存对齐

# chunk2mem和mem2chunk

    
    
    #define chunk2mem(p)   ((Void_t*)((char*)(p) + 2*SIZE_SZ))
    #define mem2chunk(mem) ((mchunkptr)((char*)(mem) - 2*SIZE_SZ))
    

这个比较简单，我们之前已经提到过，我们实际申请的内存的指针其实是chunk的size字段尾部，于是我们可以让指针进行转化，chunk2mem就是chunk指针转化为user指针，mem2chunk就是user指针转化为chunk指针

# chunk的状态

    
    
    #define PREV_INUSE 0x1
    #define IS_MMAPPED 0x2
    #define NON_MAIN_ARENA 0x4
    

这三个我们之前也解释过，分别处于chunk的size字段的最后一位，倒数第二位，倒数第三位。prev_inuse位表示了前一个chunk是否处于使用状态，is_mmapped表示chunk是否由mmap映射得到，non_main_arena表示chunk是否不是主线程的chunk

# 对某chunkP的标志位进行提取和修改

    
    
    #define SIZE_BITS (PREV_INUSE|IS_MMAPPED|NON_MAIN_ARENA)
    
    #define prev_inuse(p)       ((p)->size & PREV_INUSE)
    
    #define chunk_is_mmapped(p) ((p)->size & IS_MMAPPED)
    
    #define chunk_non_main_arena(p) ((p)->size & NON_MAIN_ARENA)
    
    #define inuse(p)\
    ((((mchunkptr)(((char*)(p))+((p)->size & ~SIZE_BITS)))->size) & PREV_INUSE)
    
    #define set_inuse(p)\
    ((mchunkptr)(((char*)(p)) + ((p)->size & ~SIZE_BITS)))->size |= PREV_INUSE
    
    #define clear_inuse(p)\
    ((mchunkptr)(((char*)(p)) + ((p)->size & ~SIZE_BITS)))->size &= ~(PREV_INUSE)
    

首先我们定义了SIZE_BITS，类似于掩码的作用。第二三四个宏都是提取相应位置的状态位。

本堆块的下一个堆块的prev_inuse位表示了本chunk的使用情况，第五个宏定义就是提取本chunk的下一个chunk的prev_inuse位

第六个表示将chunkp的下一个chunk的prev_inuse位设置为1

最后一个宏表示将chunkp的下一个chunk的prev_inuse位设置为0

# 对当前chunk的inuse位进行修改

    
    
    #define inuse_bit_at_offset(p, s)\
     (((mchunkptr)(((char*)(p)) + (s)))->size & PREV_INUSE)
     
     #define set_inuse_bit_at_offset(p, s)\
     (((mchunkptr)(((char*)(p)) + (s)))->size |= PREV_INUSE)
     
    #define clear_inuse_bit_at_offset(p, s)\
     (((mchunkptr)(((char*)(p)) + (s)))->size &= ~(PREV_INUSE))
    

第一个宏表示了当前chunk的inuse位  
第二个宏表示修改当前的chunk的inuse位为1  
第三个宏表示修改当前chunk的inuse位为0  
其中p和s分别表示当前chunk的指针和当前chunk到下一个chunk的偏移

# 设置当前chunk的size位

    
    
    #define set_head_size(p, s)  ((p)->size = (((p)->size & SIZE_BITS) | (s)))
    
    #define set_head(p, s)       ((p)->size = (s))
    
    #define set_foot(p, s)       (((mchunkptr)((char*)(p) + (s)))->prev_size = (s))
    
    #define chunksize(p)         ((p)->size & ~(SIZE_BITS))
    

第一个宏表示设置p的size位，并且不修改size位的低三位  
第二个宏表示设置p的size位，但是会可以修改低三位  
第三个宏表示设置chunkP的下一个chunk的prev_size位，至于为什么叫做set_foot则与chunk结构的前世今生有关，以后有时间讲一下  
第四个宏表示提取p的size位但是不包括低三位

# 寻找与当前chunk物理相邻的chunk

    
    
    #define next_chunk(p) ((mchunkptr)( ((char*)(p)) + ((p)->size & ~SIZE_BITS) ))
    
    #define prev_chunk(p) ((mchunkptr)( ((char*)(p)) - ((p)->prev_size) ))
    
    #define chunk_at_offset(p, s)  ((mchunkptr)(((char*)(p)) + (s)))
    

第一个宏表示寻找当前chunk物理相邻的高地址chunk  
第二个宏表示寻找当前chunk物理相邻的低地址chunk  
第三个宏表示当前chunk加上某偏移后的地址，也就是说当前chunk加上某个偏移之后的地址，将会被视为一个chunk的头指针

 **这些就是总结的一些比较重要的指针，到后面不管是malloc底层代码还是chunk合并代码，包括unlink，都会用到这些宏**

 **本文参考自glibc源码及其注释**

