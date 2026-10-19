上一篇我们介绍了[三种chunk的申请](https://www.freebuf.com/articles/system/290660.html%20)，里面穿插了malloc_consolidate函数，这个函数主要负责管理fastbin中空闲的chunk并且还可以初始化堆。

# 源代码

    
    
    static void malloc_consolidate(av) mstate av;
    #endif
    {
      mfastbinptr*    fb;                 /* current fastbin being consolidated */
      mfastbinptr*    maxfb;              /* last fastbin (for loop control) */
      mchunkptr       p;                  /* current chunk being consolidated */
      mchunkptr       nextp;              /* next chunk to consolidate */
      mchunkptr       unsorted_bin;       /* bin header */
      mchunkptr       first_unsorted;     /* chunk to link to */
    
      /* These have same use as in free() */
      mchunkptr       nextchunk;
      INTERNAL_SIZE_T size;
      INTERNAL_SIZE_T nextsize;
      INTERNAL_SIZE_T prevsize;
      int             nextinuse;
      mchunkptr       bck;
      mchunkptr       fwd;
    
      /*
        If max_fast is 0, we know that av hasn't
        yet been initialized, in which case do so below
      */
    
      if (av->max_fast != 0) {
        clear_fastchunks(av);
    
        unsorted_bin = unsorted_chunks(av);
    
        /*
          Remove each chunk from fast bin and consolidate it, placing it
          then in unsorted bin. Among other reasons for doing this,
          placing in unsorted bin avoids needing to calculate actual bins
          until malloc is sure that chunks aren't immediately going to be
          reused anyway.
        */
    
        maxfb = &(av->fastbins[fastbin_index(av->max_fast)]);
        fb = &(av->fastbins[0]);
        do {
          if ( (p = *fb) != 0) {
            *fb = 0;
    
            do {
              check_inuse_chunk(av, p);
              nextp = p->fd;
    
              /* Slightly streamlined version of consolidation code in free() */
              size = p->size & ~(PREV_INUSE|NON_MAIN_ARENA);
              nextchunk = chunk_at_offset(p, size);
              nextsize = chunksize(nextchunk);
    
              if (!prev_inuse(p)) {
                prevsize = p->prev_size;
                size += prevsize;
                p = chunk_at_offset(p, -((long) prevsize));
                unlink(p, bck, fwd);
              }
    
              if (nextchunk != av->top) {
                nextinuse = inuse_bit_at_offset(nextchunk, nextsize);
    
                if (!nextinuse) {
                  size += nextsize;
                  unlink(nextchunk, bck, fwd);
                } else
    	      clear_inuse_bit_at_offset(nextchunk, 0);
    
                first_unsorted = unsorted_bin->fd;
                unsorted_bin->fd = p;
                first_unsorted->bk = p;
    
                set_head(p, size | PREV_INUSE);
                p->bk = unsorted_bin;
                p->fd = first_unsorted;
                set_foot(p, size);
              }
    
              else {
                size += nextsize;
                set_head(p, size | PREV_INUSE);
                av->top = p;
              }
    
            } while ( (p = nextp) != 0);
    
          }
        } while (fb++ != maxfb);
      }
      else {
        malloc_init_state(av);
        check_malloc_state(av);
      }
    }
    

# arena未被初始化

其实代码中有些注释比较有用，比如

    
    
    /*
        If max_fast is 0, we know that av hasn't
        yet been initialized, in which case do so below
      */
    

我们注意到最开始就有一个if语句，也就是说max_fast等于0的时候，表示av指针指向的arena还没有被初始化。代码的最后有一个else语句，也就是说没有初始化的arena会执行这条语句

    
    
    else {
        malloc_init_state(av);
        check_malloc_state(av);
      }
    

这条语句就是执行两个函数，首先是arena的初始化函数，还有一个是检查malloc_state，其中初始化函数我们后面会讲到，这里可以理解为没有被初始化的arena首先会执行一个初始化函数，然后会检查arena。同时我们也得到了一个信息，max_fast字段可以直接体现一个arena是否被初始化。arena已初始化。

## fastbin的清空

首先我们要知道，max_fast定义在malloc_state结构体中，并且还有一段注释

    
    
    low 2 bits used as flags 
    The maximum chunk size to be eligible for fastbin
    

第一条是低两位作为标志位，第二条意思是符合fastbin的最大分块的大小。然后if语句里面第一条代码就是`clear_fastchunks(av)`，见名知意就是要清空fastbin里面的chunk。我们看一下具体的实现

    
    
    #define clear_fastchunks(M)    ((M)->max_fast |=  FASTCHUNKS_BIT)
    

这是一个宏定义，同时我们也了解到`#define FASTCHUNKS_BIT (1U)`、`#define NONCONTIGUOUS_BIT
(2U)`这两个定义正是max_fast的两个标志位，并且这两个标志位各有一段注释，但是我们只说一下第一个

    
    
    /*
      FASTCHUNKS_BIT held in max_fast indicates that there are probably
      some fastbin chunks. It is set true on entering a chunk into any
      fastbin, and cleared only in malloc_consolidate.
    
      The truth value is inverted so that have_fastchunks will be true
      upon startup (since statics are zero-filled), simplifying
      initialization checks.
    */
    

第一个注释表示有任何一个堆块进入fastbin该位都会被设置为真，只有在malloc_consolidate函数中可以被清空。并且该位的真值被颠倒，也就是说1表示假，0表示真，所以清空它使用的是`|=`。

## 寻找指针

下面有一个unsorted_bin变量，作用是用来寻找unsorted_bin的地址。这里涉及到了几个宏

    
    
    #define unsorted_chunks(M)          (bin_at(M, 1))
    
    #define bin_at(m, i) ((mbinptr)((char*)&((m)->bins[(i)<<1]) - (SIZE_SZ<<1)))
    

就是用unsorted_bins的地址减去两个标准字长。i的值是1，左移一位相当于乘2，然后减去两个标准字长(但是我不知道为什么要这么麻烦)。这个就是bins数组的头指针

然后maxfb指针存放了fastbin的尾地址，fb存放了fastbin的头地址

    
    
    maxfb = &(av->fastbins[fastbin_index(av->max_fast)]);
    fb = &(av->fastbins[0]);
    

## 第一层循环

第一层循环代码是这样

    
    
    do {
          if ( (p = *fb) != 0) {
            *fb = 0;
    
            ......
        } while (fb++ != maxfb);
    

这就是在遍历fastbin数组，并且判断其是否为空，不为空的话进行清空操作。并且将p赋值，就是链表尾部，只不过现在的链表已经脱离的fastbin

## 第二层循环：后向合并

    
    
    do {
              check_inuse_chunk(av, p);
              nextp = p->fd;
    
              /* Slightly streamlined version of consolidation code in free() */
              size = p->size & ~(PREV_INUSE|NON_MAIN_ARENA);
              nextchunk = chunk_at_offset(p, size);
              nextsize = chunksize(nextchunk);
    
              if (!prev_inuse(p)) {
                prevsize = p->prev_size;
                size += prevsize;
                p = chunk_at_offset(p, -((long) prevsize));
                unlink(p, bck, fwd);
              }
    
              if (nextchunk != av->top) {
                nextinuse = inuse_bit_at_offset(nextchunk, nextsize);
    
                if (!nextinuse) {
                  size += nextsize;
                  unlink(nextchunk, bck, fwd);
                } else
    	      clear_inuse_bit_at_offset(nextchunk, 0);
    
                first_unsorted = unsorted_bin->fd;
                unsorted_bin->fd = p;
                first_unsorted->bk = p;
    
                set_head(p, size | PREV_INUSE);
                p->bk = unsorted_bin;
                p->fd = first_unsorted;
                set_foot(p, size);
              }
    
              else {
                size += nextsize;
                set_head(p, size | PREV_INUSE);
                av->top = p;
              }
    
            } while ( (p = nextp) != 0);
    

这是第二层的循环，代码量比较大，我们慢慢来。  
最开始首先初始化变量，将一些变量进行赋值。

然后检查p的previnuse位是否为0，如果不为0则将p进行脱链，并且进行后向合并

    
    
    if (!prev_inuse(p)) {
                prevsize = p->prev_size;
                size += prevsize;
                p = chunk_at_offset(p, -((long) prevsize));
                unlink(p, bck, fwd);
              }
    

这个比较重要，所以我们来看一下具体发生了什么。首先给prevsize变量赋值，更改size变量。然后将物理相邻的低地址chunk作为p指针，然后将p进行脱链。这样就完成了堆的后向合并![image.png](https://image.3001.net/images/20211002/1633171832_61583978119a1558e207c.png!small)  
大概是这个样子的，这个就是chunk的后向合并

## 第二层循环：前向合并

    
    
    if (nextchunk != av->top) {
                nextinuse = inuse_bit_at_offset(nextchunk, nextsize);
    
                if (!nextinuse) {
                  size += nextsize;
                  unlink(nextchunk, bck, fwd);
                } else
    	            clear_inuse_bit_at_offset(nextchunk, 0);
    
                first_unsorted = unsorted_bin->fd;
                unsorted_bin->fd = p;
                first_unsorted->bk = p;
    
                set_head(p, size | PREV_INUSE);
                p->bk = unsorted_bin;
                p->fd = first_unsorted;
                set_foot(p, size);
              }
    
    else {
                size += nextsize;
                set_head(p, size | PREV_INUSE);
                av->top = p;
              }
    

这就是前向合并的代码。最开始的时候先看下一个chunk是不是topchunk，如果是topchunk的话，则直接执行下面的else语句。我们先来看下面的else语句。size字段直接加上topchunk的size，并且设置p的size位，然后将top指针指向p，这样就完成了topchunk的融合。

如果下一个chunk不是topchunk，首先判断下下个chunk的inuse位。如果为0则说明nextchunk处于空闲，则将其脱链。如果没有处于空闲状态，则更改nextchunk的inuse位

后面就是对unsortedbin的处理。首先将unsortedbin的链表尾chunk赋值给first_unsorted，并且将p加入unsortedbin的链表中  
![image.png](https://image.3001.net/images/20211002/1633174758_615844e6d8ce2916d6bb1.png!small)  
最后的情况就是这样的，我的p专门拿出来了，但是其实就是将p放入链表尾部，操作十分简单

# 总结

对于审计来说代码量还可以，难度的话也还好。但是总结起来很简单：判断arena初始化，清空fastbin标志，清空fastbin中chunk，合并chunk。其实一共就做了这么几个工作

 **我们已经处理完了malloc_consolidate函数，但是这个函数中有一个初始化函数也比较重要，我们后面会进行讲解**

 **本文参考自[Glibc：浅谈 malloc_consolidate()
函数具体实现](https://blog.csdn.net/Plus_RE/article/details/79265805)、[glibc2.23源码](https://ftp.gnu.org/gnu/glibc/)**

