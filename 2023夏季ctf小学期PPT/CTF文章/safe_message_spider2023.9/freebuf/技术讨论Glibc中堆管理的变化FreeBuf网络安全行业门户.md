##  前言

**在学pwn的道路上，我们大多从linux入手，从栈到堆，各种漏洞利用，都和Glibc或多或少打过交道。我的堆入门应该和很多人一样是从libc2.23开始的，之后又经历了各种libc版本的变化，随着现在的pwn题越来越与时俱进，我们会逐渐接触更新的libc版本，因此，我们必须知道，Glibc中堆管理变化了什么，从安全角度，我们的得失又是什么呢？从libc2.27开始，我们聊一聊Glibc中堆管理的漏洞利用的得失。**

关键字： CTF pwn 新版本libc libc 2.27 libc 2.29 libc 2.30 堆溢出

##  GLibc2.27

Glibc2.23我就不想多说了，感兴趣的朋友可以学一学pwn相关的堆漏洞利用知识，网上现在总结的也算是比较多。我就不赘述了。从Glibc2.27开始，发生了很多有趣的地方，我们一起聊一聊。

###  Tcache

Tcache可是说是Glibc2.27中一个大的改变，其实Tcache的引入是从Glibc2.26开始的。但是（以下个人见解）Linux中比较受欢迎的发行版，ubuntu
18.04中的libc版本是2.27，再加上很多发行版都是2.27版本，所以，我们常见的pwn题也就在这种环境下编译开发了，因此，我们直接说说2.27版本，跳过2.26版本。

我认为Tcache使得漏洞利用变简单了，其得失我总结了一下：

> 漏洞利用最后一哆嗦，特别简单暴力  
>
>
> Tcache的管理结构在堆上，比main_arena好搞一点，毕竟Libc地址一般比堆地址难搞到
>
> Tcache有时候使得泄露Libc地址变得困难

这里我说下Tcache的机制，tcache就是一个为了内存分配速度而存在的机制，当size不大（这个程度后面讲）堆块free后，不会直接进入各种bin，而是进入tcache，如果下次需要该大小内存，直接讲tcache分配出去，是不是感觉和fastbin蛮像的，但是其size的范围比fastbin大多了，他有64个bin链数组，也就是(64+1)*size_sz*2，在64位系统中就是0x410大小，有图有真相：

![](https://image.3001.net/images/20200417/1587120092_5e9987dc956da.png!small)

![](https://image.3001.net/images/20200417/1587120099_5e9987e3dfbfb.png!small)

也就是说，在64位情况下，tcache可以接受0x20~0x410大小的堆块。

###  Tcache poisoning

那么Tcache对漏洞利用来说，不像fastbin attack一样，需要寻找合适的size了， **在2.27的环境下是可以直接做到任意地址写的**
，这一点非常nice, 这种利用方法，在也被叫做 **tcache poisoning** 。同时，在double
free领域，Tcache可以直接double free，而不需要像fastbin那样，需要和链上上一个堆块不一样,也就是下面这个样子。

    
    
     /*
     heap0 ----> heap1 ----> heap0 (fastbin YES)
     heap0 ----> heap0 (fastbin NO)
     heap0 ----> heap0 (Tcahce YES)
     */

还有一点不同，就是在Tcache中， **fd指向的并不是堆头，而是堆内容** ，这一点也是需要我们注意的。

![](https://image.3001.net/images/20200417/1587120119_5e9987f7a0e1a.png!small)

**leak libc地址**

单纯在堆中leak
libc地址，一般是使用size大于fastbin范围的堆块，而在有tcache的情况下，这个变得相较之前困难，我将我目前用的比较多的方法总结如下：

1、申请8个大堆块，释放8个，这里堆块大小，大于fastbin范围，就是填满tcache。

![](https://image.3001.net/images/20200417/1587120123_5e9987fbad0f0.png!small)

2、有double free的情况下，连续free 8次同一个堆块，这里堆块大小，大于fastbin范围。

![](https://image.3001.net/images/20200417/1587120132_5e9988047dd50.png!small)

3、申请大堆块，大于0x410。

![](https://image.3001.net/images/20200417/1587120145_5e998811bd223.png!small)

4、修改堆上的Tcache管理结构

![](https://image.3001.net/images/20200417/1587120160_5e998820136bc.png!small)

大致就是以上几种方法，如果还有其他的想法，欢迎交流。

###  Tcache Stashing Unlink Attack

网上有很多人在分析这一漏洞的时候，都是基于libc2.29分析的，其实在libc2.27中，这一漏洞就已经存在了。

这里简单讲下，这是small bin 中的检查，即：__glibc_unlikely(bck->fd != victim)

    
    
        // 获取 small bin 中倒数第二个 chunk 。
                     bck = victim->bk;
                     // 检查 bck->fd 是不是 victim，防止伪造
                     if (__glibc_unlikely(bck->fd != victim)) {
                         errstr = "malloc(): smallbin double linked list corrupted";
                         goto errout;
                     }
                     // 设置 victim 对应的 inuse 位
                     set_inuse_bit_at_offset(victim, nb);
                     // 修改 small bin 链表，将 small bin 的最后一个 chunk 取出来
                     bin->bk = bck;
                     bck->fd = bin;

我们来看看Tcache中的情况：

    
    
     #if USE_TCACHE
       /* While we're here, if we see other chunks of the same size,
          stash them in the tcache.  */
       size_t tc_idx = csize2tidx (nb);
       if (tcache && tc_idx < mp_.tcache_bins)
         {
           mchunkptr tc_victim;
            /* While bin not empty and tcache not full, copy chunks over.  */
           while (tcache->counts[tc_idx] < mp_.tcache_count
          && (tc_victim = last (bin)) != bin)
     {
       if (tc_victim != 0)
         {
           bck = tc_victim->bk;
           set_inuse_bit_at_offset (tc_victim, nb);
           if (av != &main_arena)
     set_non_main_arena (tc_victim);
           bin->bk = bck;
           bck->fd = bin;//0
            tcache_put (tc_victim, tc_idx);//1
                 }
     }
        }
     #endif

那么，我们需要注意2个地方，就是我在源码中标注的0和1。那么这两个地方由于没有任何检查，导致了两个问题，1、任意地址写libc地址，2、将任意地址放入tcache。

那么这段的逻辑是什么呢，简单来说，当我们从smallbin中申请了一个chunk后，会将此大小的tcache用smallbin里的堆块填满。

我们来看看什么时候，终止填入呢，两个条件：tcache->counts[tc_idx] >= mp_.tcache_count || (tc_victim
= last (bin)) ==
bin就是上述while循环中的相反的条件。也就是说，如果smallbin里没heap了或者tcache填满了，就不需要继续填充了，但是由于我们期望漏洞利用，所以需要改掉bck，这就导致(tc_victim
= last (bin)) ==
bin这个条件是很难达到的。所以，我们需要控制tcache中的数量，但是，这里又出现了一个矛盾，那就是如果Tcache不为空，就不会从smallbin中取出堆块。

所以，综上所述，只有绕过tcache的calloc能够符合这样的要求，那么，如果，我们想要任意地址写libc，就在tcache中留一个空间，如果期望任意地址放入tcache，就在tcache中留两个空间，同时，我们需要清楚，动手脚的small
bin 应该是倒数第二个smallbin。

画个图示意一下：

![](https://image.3001.net/images/20200417/1587120182_5e9988362eb2b.png!small)

将Chunk1的bk指向目标地址，再calloc一个0xa0大小的chunk，参照上述的目的，确定自己需要在Tcache中留几个heap。

###  Tcache结构破坏

这个其实没什么好说的，只是一个tips吧，tcache的管理结构在堆上，再加上tcache宽松的检查条件，其实有时候搞一搞这里还是蛮有意思的。

libc2.27中的东西基本就讲这些了，接下来就是libc2.29了

##  Glibc2.29

在2.27的基础上，我们看看2.29做了哪些改变：

###  Tcache的double free防护

首先是一个对漏洞利用者较为遗憾的改动，就是在tcache的结构体上，加了一个key。

![](https://image.3001.net/images/20200417/1587120194_5e998842eb954.png!small)

![](https://image.3001.net/images/20200417/1587120202_5e99884a87841.png!small)

在官方注释上，这一增加是为了检测tcache的double
free，在2.27的libc中，tcache为了速度，几乎没有什么安全保护，这一机制会缓解部分漏洞利用。那么，这一增加如何作用呢，我们可以看到，在tcache_put中，对这一结构体进行了赋值，赋值的内容就是定义的tcache_perthread_struct结构体tcache的地址，tcache就是通过这一函数来判断当前的heap是否在tcache中，当然，在tcache_get中，也会将其清理。同时在free中加了这么一段。

    
    
     if (__glibc_unlikely (e->key == tcache))
       {
         tcache_entry *tmp;
         LIBC_PROBE (memory_tcache_double_free, 2, e, tc_idx);
         for (tmp = tcache->entries[tc_idx];
      tmp;
      tmp = tmp->next)
           if (tmp == e)
     malloc_printerr ("free(): double free detected in tcache 2");
         /* If we get here, it was a coincidence.  We've wasted a
            few cycles, but don't abort.  */
       }

也就是说在free时，如果当前的chunk的bk位置是tcache这一地址，那么就会循环检测当前大小的tcache的链表，查看链表中是否存在当前的chunk。所以，想要double
free前，记得先改一下bk。

###  unlink前操作

在free的时候，unlink前新加了一个检查，这个不太致命，注意绕过即可。

    
    
     /* consolidate backward */
         if (!prev_inuse(p)) {
           prevsize = prev_size (p);
           size += prevsize;
           p = chunk_at_offset(p, -((long) prevsize));
           if (__glibc_unlikely (chunksize(p) != prevsize))//add
             malloc_printerr ("corrupted size vs. prev_size while consolidating");//add
           unlink_chunk (av, p);
         }

###  unsortbin保护

不说了，unsortbin attack我先不用了，总可以了吧（含泪）。

    
    
       if (__glibc_unlikely (size <= 2 * SIZE_SZ)
                   || __glibc_unlikely (size > av->system_mem))
                 malloc_printerr ("malloc(): invalid size (unsorted)");
               if (__glibc_unlikely (chunksize_nomask (next) < 2 * SIZE_SZ)
                   || __glibc_unlikely (chunksize_nomask (next) > av->system_mem))
                 malloc_printerr ("malloc(): invalid next size (unsorted)");
               if (__glibc_unlikely ((prev_size (next) & ~(SIZE_BITS)) != size))
                 malloc_printerr ("malloc(): mismatching next->prev_size (unsorted)");
               if (__glibc_unlikely (bck->fd != victim)
                   || __glibc_unlikely (victim->fd != unsorted_chunks (av)))
                 malloc_printerr ("malloc(): unsorted double linked list corrupted");
               if (__glibc_unlikely (prev_inuse (next)))
                 malloc_printerr ("malloc(): invalid next->prev_inuse (unsorted)");
     ...... ......
         /* remove from unsorted list */
               if (__glibc_unlikely (bck->fd != victim))
                 malloc_printerr ("malloc(): corrupted unsorted chunks 3");
               unsorted_chunks (av)->bk = bck;
               bck->fd = unsorted_chunks (av);

##  libc 2.30

那么到了libc2.30其实增加的东西也是不多了。

###  largebin attack

在largebin 中，加了这个，刚好对largbin的bk和bk_nextsize做出了限制。

![](https://image.3001.net/images/20200417/1587120211_5e998853d3a62.png!small)

那么在插入large bin时，就不能使用large bin Attack了（关于Largebin Attack的方法，可参照我之前文章）

##  写在最后

如有错误欢迎指正：[sofr@foxmail.com](mailto:sofr@foxmail.com)

 ***本文作者： 白里个白sofr，转载请注明来自FreeBuf.COM**  
  

