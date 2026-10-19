**作者：bwner@浙银网络安全创新实验室**  
**本文为作者投稿，Seebug Paper 期待你的分享，凡经采用即有礼品相送！ 投稿邮箱：paper@seebug.org**

### 前言

最近在学习 IoT 相关漏洞利用，打算先学习一下 Qiling 框架，为后续的漏洞利用文章做铺垫。 Qiling 框架是基于 unicorn
的多架构平台模拟执行框架，提供的仿真环境很全面，能够在模拟执行的基础上提供统一的分析 API，这个A PI
包括插桩分析、快照、系统调用和API劫持等操作。在2021年JOANSIVION提供了两个QilingLab能够针对Qiling框架各种操作进行学习的程序，并提供了相应的writeup。他提供的
writeup 是 arm 架构的，因此本文以 x86_64 架构为基础，在他的文章上进行相应补充。程序下载地址放在了文末参考链接中。

时隔两年，Qiling 框架进行了很多更新与改动，我在完成 QilingLab 的过程中发现高版本的 Qiling
存在问题，因此从代码审计的角度入手，分析并提出解决方案，如果曾经分析过 QilingLab 的朋友可以直接跳到 Challenge 10
部分。本文将以最为基础的视角来陪着大家从 0 到 1 学习 Qiling 框架，希望大家看完能有所收获。

首先下载Qiling:

    
    
    git clone --recurse-submodules https://github.com/qilingframework/qiling.git # 使用 --recurse-submodules 递归下载模块，rootfs是单独更新的项目

使用版本为最新版：

    
    
    > pip show qiling
    Name: qiling
    Version: 1.4.5
    Summary: Qiling is an advanced binary emulation framework that cross-platform-architecture

可以看到 QilingLab 提供的11个挑战如下：

    
    
    Welcome to QilingLab.
    Here is the list of challenges:
    Challenge 1: Store 1337 at pointer 0x1337.
    Challenge 2: Make the 'uname' syscall return the correct values.
    Challenge 3: Make '/dev/urandom' and 'getrandom' "collide".
    Challenge 4: Enter inside the "forbidden" loop.
    Challenge 5: Guess every call to rand().
    Challenge 6: Avoid the infinite loop.
    Challenge 7: Don't waste time waiting for 'sleep'.
    Challenge 8: Unpack the struct and write at the target address.
    Challenge 9: Fix some string operation to make the iMpOsSiBlE come true.
    Challenge 10: Fake the 'cmdline' line file to return the right content.
    Challenge 11: Bypass CPUID/MIDR_EL1 checks.

### 整体分析

运行一下程序，可以看到输出了挑战的所有题目：

    
    
    > ./qilinglab-x86_64 
    Welcome to QilingLab.
    Here is the list of challenges:
    Challenge 1: Store 1337 at pointer 0x1337.
    Challenge 2: Make the 'uname' syscall return the correct values.
    Challenge 3: Make '/dev/urandom' and 'getrandom' "collide".
    Challenge 4: Enter inside the "forbidden" loop.
    Challenge 5: Guess every call to rand().
    Challenge 6: Avoid the infinite loop.
    Challenge 7: Don't waste time waiting for 'sleep'.
    Challenge 8: Unpack the struct and write at the target address.
    Challenge 9: Fix some string operation to make the iMpOsSiBlE come true.
    Challenge 10: Fake the 'cmdline' line file to return the right content.
    Challenge 11: Bypass CPUID/MIDR_EL1 checks.
    
    Checking which challenge are solved...
    Note: Some challenges will results in segfaults and infinite loops if they aren't solved.
    [1]    8036 segmentation fault (core dumped)  ./qilinglab-x86_64

先调用Qiling仿真环境运行一下：

    
    
    from qiling import *
    
    if __name__ == '__main__':
        path = ["qilinglab-x86_64"]
        rootfs = "rootfs/x8664_linux"
        ql = Qiling(path, rootfs)
        ql.run()

发现报错：

    
    
    unicorn.unicorn.UcError: Invalid memory read (UC_ERR_READ_UNMAPPED)

接下来进行分析无法运行的原因，按照出题人所说需要解决第一个挑战才能正常进入。首先查看一下文件信息，可以看到程序使用小端顺序，符号表未裁剪：

    
    
    > readelf -h qilinglab-x86_64
    ELF Header:
      Magic:   7f 45 4c 46 02 01 01 00 00 00 00 00 00 00 00 00 
      Class:                             ELF64
      Data:                              2's complement, little endian
      Version:                           1 (current)
      OS/ABI:                            UNIX - System V
      ABI Version:                       0
      Type:                              DYN (Shared object file)
      Machine:                           Advanced Micro Devices X86-64
      Version:                           0x1
      Entry point address:               0xa80
      Start of program headers:          64 (bytes into file)
      Start of section headers:          15840 (bytes into file)
      Flags:                             0x0
      Size of this header:               64 (bytes)
      Size of program headers:           56 (bytes)
      Number of program headers:         9
      Size of section headers:           64 (bytes)
      Number of section headers:         29
      Section header string table index: 28
    
    
    > file -L qilinglab-x86_64
    qilinglab-x86_64: ELF 64-bit LSB shared object, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, for GNU/Linux 3.2.0, BuildID[sha1]=76164e6b494c1af9d9f746e2dc7d3663cc23525c, not stripped

拖到IDA里看一下函数流程，main函数：

    
    
    ; Attributes: bp-based frame
    
    ; int __cdecl main(int argc, const char **argv, const char **envp)
    public main
    main proc near
    
    var_10= qword ptr -10h
    var_4= dword ptr -4
    
    ; __unwind {
    push    rbp
    mov     rbp, rsp
    sub     rsp, 10h
    mov     [rbp+var_4], edi
    mov     [rbp+var_10], rsi
    mov     eax, 0
    call    start
    mov     eax, 0
    leave
    retn
    ; } // starts at 15CA
    main endp

可以看到跳转到start，查看一下start伪代码：

    
    
    unsigned __int64 start()
    {
      int v0; // eax
      int i; // [rsp+0h] [rbp-20h]
      int v3; // [rsp+4h] [rbp-1Ch]
      int v4; // [rsp+4h] [rbp-1Ch]
      int v5; // [rsp+4h] [rbp-1Ch]
      int v6; // [rsp+4h] [rbp-1Ch]
      int v7; // [rsp+4h] [rbp-1Ch]
      int v8; // [rsp+4h] [rbp-1Ch]
      int v9; // [rsp+4h] [rbp-1Ch]
      int v10; // [rsp+4h] [rbp-1Ch]
      int v11; // [rsp+4h] [rbp-1Ch]
      int v12; // [rsp+4h] [rbp-1Ch]
      char v13[11]; // [rsp+Dh] [rbp-13h] BYREF
      char v14[11]; // [rsp+Eh] [rbp-12h] BYREF
      char v15[11]; // [rsp+10h] [rbp-10h] BYREF
      unsigned __int64 v16; // [rsp+18h] [rbp-8h]
    
      v16 = __readfsqword(0x28u);  // __readfsqword指令的参数是一个偏移量，0x28u是一个无符号整数常量，值为0x28，即40，表示从FS寄存器中的偏移量为40的地址开始读取64位数据。
      for ( i = 0; i < 11; ++i )
        v13[i] = 0;
      printf("Welcome to QilingLab.\nHere is the list of challenges:");
      printf("\nChallenge 1: Store 1337 at pointer 0x1337.");
      printf("\nChallenge 2: Make the 'uname' syscall return the correct values.");
      printf("\nChallenge 3: Make '/dev/urandom' and 'getrandom' \"collide\".");
      printf("\nChallenge 4: Enter inside the \"forbidden\" loop.");
      printf("\nChallenge 5: Guess every call to rand().");
      printf("\nChallenge 6: Avoid the infinite loop.");
      printf("\nChallenge 7: Don't waste time waiting for 'sleep'.");
      printf("\nChallenge 8: Unpack the struct and write at the target address.");
      printf("\nChallenge 9: Fix some string operation to make the iMpOsSiBlE come true.");
      printf("\nChallenge 10: Fake the 'cmdline' line file to return the right content.");
      printf("\nChallenge 11: Bypass CPUID/MIDR_EL1 checks.");
      puts(
        "\n"
        "\n"
        "Checking which challenge are solved...\n"
        "Note: Some challenges will results in segfaults and infinite loops if they aren't solved.");
      challenge1(v13);
      v3 = checker(v13, 0LL);
      challenge2(v14);
      v4 = checker(v13, 1LL) + v3;
      challenge3(&v14[1]);
      v5 = checker(v13, 2LL) + v4;
      challenge4(v15);
      v6 = checker(v13, 3LL) + v5;
      challenge5(&v15[1]);
      v7 = checker(v13, 4LL) + v6;
      challenge6(&v15[2]);
      v8 = checker(v13, 5LL) + v7;
      challenge7(&v15[3]);
      v9 = checker(v13, 6LL) + v8;
      challenge8(&v15[4]);
      v10 = checker(v13, 7LL) + v9;
      challenge9(&v15[5]);
      v11 = checker(v13, 8LL) + v10;
      challenge10(&v15[6]);
      v12 = checker(v13, 9LL) + v11;
      challenge11(&v15[7]);
      v0 = checker(v13, 10LL);
      printf("\nYou solved %d/%d of the challenges\n", (unsigned int)(v0 + v12), 11LL);
      return __readfsqword(0x28u) ^ v16;
    }

查看调用的checker函数伪代码，可以知道当检查到问题已解决时返回1：

    
    
    __int64 __fastcall checker(__int64 a1, int a2)
    {
      __int64 result; // rax
    
      if ( *(_BYTE *)(a2 + a1) ) ; 检查数组a1中下标为a2的元素是否为0，非0返回1
      {
        printf("\nChallenge %d: SOLVED", (unsigned int)(a2 + 1));
        result = 1LL;
      }
      else
      {
        printf("\nChallenge %d: NOT SOLVED", (unsigned int)(a2 + 1));
        result = 0LL;
      }
      return result;
    }

我们梳理一下函数逻辑：循环初始化数组v13所有元素为0，如果完成对应挑战就会改变v13对应数组的值，再用checker进行一次检查v13数组元素是否为0.再将checker返回值传递给变量，再加到下一次的检查结果上。这个过程不断重复，最后将累加起来的值输出到`"\nYou
solved %d/%d of the challenges\n"`。

### Challenge 1: 内存数据修改

拖到IDA里看一下 challenge 1 汇编代码：

    
    
    .text:0000000000000B8A                 public challenge1
    .text:0000000000000B8A challenge1      proc near               ; CODE XREF: start+123↓p
    .text:0000000000000B8A
    .text:0000000000000B8A var_18          = qword ptr -18h        ; 分配quadword类型的局部变量var_18位于[rbp-18h]的位置
    .text:0000000000000B8A var_C           = dword ptr -0Ch        ; qword 8字节，dword 4字节
    .text:0000000000000B8A var_8           = qword ptr -8
    .text:0000000000000B8A
    .text:0000000000000B8A ; __unwind {
    .text:0000000000000B8A                 push    rbp
    .text:0000000000000B8B                 mov     rbp, rsp
    .text:0000000000000B8E                 mov     [rbp+var_18], rdi  ; [rbp-18h], rdi 此处rdi值为指向v13的指针
    .text:0000000000000B92                 mov     [rbp+var_8], 1337h
    .text:0000000000000B9A                 mov     rax, [rbp+var_8]
    .text:0000000000000B9E                 mov     eax, [rax]         ; 将内存地址1337h的值传递给eax
    .text:0000000000000BA0                 mov     [rbp+var_C], eax
    .text:0000000000000BA3                 cmp     [rbp+var_C], 539h  ; cmp jnz: 不相等就跳转loc_BB3进行retn (539h = 1337)
    .text:0000000000000BAA                 jnz     short loc_BB3
    .text:0000000000000BAC                 mov     rax, [rbp+var_18]
    .text:0000000000000BB0                 mov     byte ptr [rax], 1  ; 将值为1的字节写入存储在rax所指向的内存地址中
    .text:0000000000000BB3
    .text:0000000000000BB3 loc_BB3:                                ; CODE XREF: challenge1+20↑j
    .text:0000000000000BB3                 nop
    .text:0000000000000BB4                 pop     rbp
    .text:0000000000000BB5                 retn
    .text:0000000000000BB5 ; } // starts at B8A

可以看出我们需要让内存地址1337h处的值为1337才能让cmp判断相等，rdi传入的是数组地址对应数组首个元素地址，相等后调整rdi地址处的值为1，这也符合后续被checker函数检查数组后进行的一系列操作。

    
    
    .text:0000000000000B8E                 mov     [rbp+var_18], rdi
    
    ...
    
    .text:0000000000000BAC                 mov     rax, [rbp+var_18]
    .text:0000000000000BB0                 mov     byte ptr [rax], 1

challenge 1 对应的伪代码如下：

    
    
    _BYTE *__fastcall challenge1(_BYTE *a1)
    {
      _BYTE *result; // rax
    
      result = (_BYTE *)*(unsigned int *)((char *)&loc_1335 + 2); // 标识符loc_xxxx通常用于表示一个内存地址或常量值
      if ( *(_DWORD *)((char *)&loc_1335 + 2) == 1337 )
      {
        result = a1;
        *a1 = 1;
      }
      return result;
    }

在Qiling中编写字节序列常用有以下方式，我选用的是pack16。

    
    
     ql.mem.write(0x1000, b'\x41\x42\x43') # 手动输入
    
     ql.pack(">I", 0x12345678) # 函数调用将返回一个4字节的大端序字节序列，其中包含整数值 0x12345678 的二进制表示。
                               # ">I"参数指定了这个字节序列的格式，其中">"表示大端序，"<"表示小端序，"I"表示一个32位无符号整数。
    
     ql.pack16(0x1234)         # 这个函数专门用于16位整数

#### writeup 1

根据前面的分析可以得到 challenge 1 writeup:

    
    
    from qiling import *
    
    def challenge1(ql):
        ql.mem.map(0x1000, 0x1000, info='[challenge1]')
        # 为地址范围?[0x1000, 0x2000) 映射了一块内存，第一个参数0x1000是映射的起始地址，第二个参数0x1000是映射的大小，映射的大小必须是页大小的倍数，这里的页大小是 Qiling模拟器的默认页大小，4096字节。info是对这部分内存做的一个标记，后续Qiling如果想接着使用的话就可以用这个标记来定位。
        ql.mem.write(0x1337, ql.pack16(1337))
        # 将整数值 1337 转换为一个16位字节序列写入内存地址 0x1337 所指定的内存位置，小端输入
    
    if __name__ == '__main__':
        path = ["qilinglab-x86_64"]
        rootfs = "rootfs/x8664_linux"
        ql = Qiling(path, rootfs)
        challenge1(ql)
        ql.run()

运行上面的脚本，可以看到 challenge 1 已经解决：

    
    
    Challenge 11: Bypass CPUID/MIDR_EL1 checks.
    
    Checking which challenge are solved...
    [=]     write(fd = 0x1, buf = 0x55555575a260, count = 0x54) = 0x54
    Note: Some challenges will results in segfaults and infinite loops if they aren't solved.
    [=]     write(fd = 0x1, buf = 0x55555575a260, count = 0x5a) = 0x5a
    
    [=]     write(fd = 0x1, buf = 0x55555575a260, count = 0x1) = 0x1
    [=]     uname(buf = 0x80000000db70) = 0x0
    Challenge 1: SOLVED
    [=]     write(fd = 0x1, buf = 0x55555575a260, count = 0x14) = 0x14
    [=]     openat(fd = 0xffffff9c, path = 0x555555555698, flags = 0x0, mode = 0x0) = -0x2 (ENOENT)
    [=]     read(fd = 0xffffffff, buf = 0x80000000dce0, length = 0x20) = -0x9 (EBADF)
    [=]     read(fd = 0xffffffff, buf = 0x80000000dcdf, length = 0x1) = -0x9 (EBADF)
    [=]     close(fd = 0xffffffff) = -0x1 (EPERM)
    [=]     getrandom(buf = 0x80000000dd00, buflen = 0x20, flags = 0x1) = 0x20
    Challenge 2: NOT SOLVED
    [=]     write(fd = 0x1, buf = 0x55555575a260, count = 0x18) = 0x18
    Challenge 3: NOT SOLVED
    [=]     write(fd = 0x1, buf = 0x55555575a260, count = 0x18) = 0x18
    [=]     time() = 0x64704df9
    Challenge 4: NOT SOLVED
    [=]     write(fd = 0x1, buf = 0x55555575a260, count = 0x18) = 0x18

**如果我们想使用Qiling进行远程调试的话，应该怎么做？**

我们在使用qemu配合IDA进行远程调试时，需要使用下面的qemu-arm-static：

    
    
    sudo chroot ./ ./qemu-arm-static -g 12345 ./bin/httpd

查了一下qiling文档，调试qiling的仿真程序需要在脚本中添加下面的代码：

    
    
    ql.debugger = 'gdb:0.0.0.0:12345'

接着设置一下IDA的gdb debugger，断点在入口函数处，

![
](https://images.seebug.org/content/images/2023/05/9754f94f-9525-4092-8ea7-0bbe0c930a0d.png-w331s)

![
](https://images.seebug.org/content/images/2023/05/c11e9701-1b93-4337-ae59-9ecf86f0c4a7.png-w331s)

运行添加dbg后的脚本：

![
](https://images.seebug.org/content/images/2023/05/eb59d00b-8bf3-4e1b-bcd9-7b1fe7f66698.png-w331s)

运行后报错：

    
    
    ValueError: '/home/ubuntu/Desktop/qilinglab/qilinglab-x86_64' does not start with '/home/ubuntu/Desktop/qilinglab/rootfs/x8664_linux'

Qiling对于报错的提示都挺好的，这里需要将qilinglab-x86_64放置到指定的rootfs目录（我这里是使用的rootfs/x8664_linux作为rootfs目录）下运行，复制后更改一下程序运行的路径，更改后的代码如下：

    
    
    from qiling import *
    
    def challenge1(ql):
        ql.mem.map(0x1000, 0x1000, info='[challenge1]')
        ql.mem.write(0x1337, ql.pack16(1337))
    
    if __name__ == '__main__':
        path = ["rootfs/x8664_linux/qilinglab-x86_64"]
        rootfs = "rootfs/x8664_linux"
        ql = Qiling(path, rootfs)
        challenge1(ql)
        ql.debugger = 'gdb:0.0.0.0:12345'
        ql.run()

可以看到程序已经可以远程调试了：

![
](https://images.seebug.org/content/images/2023/05/b5fee10a-3ff6-4b02-9029-f0b78e15cf82.png-w331s)

### Challenge 2: hook系统调用

> Challenge 2: Make the 'uname' syscall return the correct values.

查看challenges 2 汇编代码：

    
    
    .text:0000555555554BB6                 public challenge2
    .text:0000555555554BB6 challenge2      proc near               ; CODE XREF: start+147↓p
    .text:0000555555554BB6
    .text:0000555555554BB6 var_1D8         = qword ptr -1D8h
    .text:0000555555554BB6 var_1D0         = dword ptr -1D0h
    .text:0000555555554BB6 var_1CC         = dword ptr -1CCh
    .text:0000555555554BB6 var_1C8         = dword ptr -1C8h
    .text:0000555555554BB6 var_1C4         = dword ptr -1C4h
    .text:0000555555554BB6 name            = utsname ptr -1C0h
    .text:0000555555554BB6 s               = byte ptr -3Ah
    .text:0000555555554BB6 var_32          = word ptr -32h
    .text:0000555555554BB6 var_30          = byte ptr -30h
    .text:0000555555554BB6 var_18          = qword ptr -18h
    .text:0000555555554BB6
    .text:0000555555554BB6                 push    rbp
    .text:0000555555554BB7                 mov     rbp, rsp
    .text:0000555555554BBA                 push    rbx
    .text:0000555555554BBB                 sub     rsp, 1D8h
    .text:0000555555554BC2                 mov     [rbp+var_1D8], rdi
    .text:0000555555554BC9                 mov     rax, fs:28h     ; 从Segment fs(用于TLS)对应的内存段,偏移量40h处取一个值，把这个值加载到rax寄存器
    .text:0000555555554BD2                 mov     [rbp+var_18], rax
    .text:0000555555554BD6                 xor     eax, eax        ; 清零eax寄存器，更新零标志位ZF = 1(表示eax为0)
    .text:0000555555554BD8                 lea     rax, [rbp+name] ; 将[rbp+name]的地址传给rax
    .text:0000555555554BDF                 mov     rdi, rax        ; name
    .text:0000555555554BE2                 call    _uname
    .text:0000555555554BE7                 test    eax, eax        ; 不修改eax的内容,只更新标志位
    .text:0000555555554BE9                 jz      short loc_555555554BFC ; ZF=1，则转移到目的地址
    .text:0000555555554BEB                 lea     rdi, s          ; "uname"
    .text:0000555555554BF2                 call    _perror         ; _perror() 用于打印错误信息
    .text:0000555555554BF7                 jmp     loc_555555554D13
    .text:0000555555554BFC ; ---------------------------------------------------------------------------    .text:0000555555554BFC
    .text:0000555555554BFC loc_555555554BFC:                       ; CODE XREF: challenge2+33↑j
    .text:0000555555554BFC                 mov     rax, cs:qword_55555555567E
    .text:0000555555554C03                 mov     qword ptr [rbp+s], rax
    .text:0000555555554C07                 movzx   eax, cs:word_555555555686
    .text:0000555555554C0E                 mov     [rbp+var_32], ax
    .text:0000555555554C12                 mov     rax, cs:qword_555555555688
    .text:0000555555554C19                 mov     rdx, cs:qword_555555555690
    .text:0000555555554C20                 mov     qword ptr [rbp+var_30], rax
    .text:0000555555554C24                 mov     qword ptr [rbp+var_30+8], rdx
    .text:0000555555554C28                 mov     [rbp+var_1D0], 0
    .text:0000555555554C32                 mov     [rbp+var_1CC], 0
    .text:0000555555554C3C                 jmp     short loc_555555554C6D
    .text:0000555555554C3E ; ---------------------------------------------------------------------------    .text:0000555555554C3E
    .text:0000555555554C3E loc_555555554C3E:                       ; CODE XREF: challenge2+CF↓j
    .text:0000555555554C3E                 mov     eax, [rbp+var_1C8]
    .text:0000555555554C44                 cdqe
    .text:0000555555554C46                 movzx   edx, [rbp+rax+name.sysname]
    .text:0000555555554C4E                 mov     eax, [rbp+var_1C8]
    .text:0000555555554C54                 cdqe
    .text:0000555555554C56                 movzx   eax, [rbp+rax+s]
    .text:0000555555554C5B                 cmp     dl, al
    .text:0000555555554C5D                 jnz     short loc_555555554C66
    .text:0000555555554C5F                 add     [rbp+var_1D0], 1
    .text:0000555555554C66
    .text:0000555555554C66 loc_555555554C66:                       ; CODE XREF: challenge2+A7↑j
    .text:0000555555554C66                 add     [rbp+var_1C8], 1
    .text:0000555555554C6D
    .text:0000555555554C6D loc_555555554C6D:                       ; CODE XREF: challenge2+86↑j
    .text:0000555555554C6D                 mov     eax, [rbp+var_1C8]
    .text:0000555555554C73                 movsxd  rbx, eax
    .text:0000555555554C76                 lea     rax, [rbp+s]
    .text:0000555555554C7A                 mov     rdi, rax        ; s
    .text:0000555555554C7D                 call    _strlen
    .text:0000555555554C82                 cmp     rbx, rax        ; 相等，则ZF=1, CF=0, OF=0
                                                                   ; 小于，则ZF=0, CF=1, OF=0
                                                                   ; 大于，则ZF=0, CF=0, OF=0
    .text:0000555555554C85                 jb      short loc_555555554C3E ; 前一条指令执行的结果为小于则跳转
    .text:0000555555554C87                 jmp     short loc_555555554CB8 ; 此处跳出循环
    .text:0000555555554C89 ; ---------------------------------------------------------------------------    .text:0000555555554C89
    .text:0000555555554C89 loc_555555554C89:                       ; CODE XREF: challenge2+11A↓j
    .text:0000555555554C89                 mov     eax, [rbp+var_1C4]
    .text:0000555555554C8F                 cdqe
    .text:0000555555554C91                 movzx   edx, [rbp+rax+name.version]
    .text:0000555555554C99                 mov     eax, [rbp+var_1C4]
    .text:0000555555554C9F                 cdqe
    .text:0000555555554CA1                 movzx   eax, [rbp+rax+var_30]
    .text:0000555555554CA6                 cmp     dl, al
    .text:0000555555554CA8                 jnz     short loc_555555554CB1
    .text:0000555555554CAA                 add     [rbp+var_1CC], 1
    .text:0000555555554CB1
    .text:0000555555554CB1 loc_555555554CB1:                       ; CODE XREF: challenge2+F2↑j
    .text:0000555555554CB1                 add     [rbp+var_1C4], 1
    .text:0000555555554CB8
    .text:0000555555554CB8 loc_555555554CB8:                       ; CODE XREF: challenge2+D1↑j
    .text:0000555555554CB8                 mov     eax, [rbp+var_1C4]
    .text:0000555555554CBE                 movsxd  rbx, eax        ; 将eax寄存器中的32位符号扩展为64位，并将结果存储到rbx寄存器中
    .text:0000555555554CC1                 lea     rax, [rbp+var_30]
    .text:0000555555554CC5                 mov     rdi, rax        ; s
    .text:0000555555554CC8                 call    _strlen
    .text:0000555555554CCD                 cmp     rbx, rax
    .text:0000555555554CD0                 jb      short loc_555555554C89
    .text:0000555555554CD2                 mov     ebx, [rbp+var_1D0]
    .text:0000555555554CD8                 lea     rax, [rbp+s]
    .text:0000555555554CDC                 mov     rdi, rax        ; s
    .text:0000555555554CDF                 call    _strlen
    .text:0000555555554CE4                 cmp     rbx, rax
    .text:0000555555554CE7                 jnz     short loc_555555554D13
    .text:0000555555554CE9                 mov     ebx, [rbp+var_1CC]
    .text:0000555555554CEF                 lea     rax, [rbp+var_30]
    .text:0000555555554CF3                 mov     rdi, rax        ; s
    .text:0000555555554CF6                 call    _strlen
    .text:0000555555554CFB                 cmp     rbx, rax
    .text:0000555555554CFE                 jnz     short loc_555555554D13
    .text:0000555555554D00                 cmp     [rbp+var_1D0], 5
    .text:0000555555554D07                 jbe     short loc_555555554D13
    .text:0000555555554D09                 mov     rax, [rbp+var_1D8]
    .text:0000555555554D10                 mov     byte ptr [rax], 1
    .text:0000555555554D13
    .text:0000555555554D13 loc_555555554D13:                       ; CODE XREF: challenge2+41↑j
    .text:0000555555554D13                                         ; challenge2+131↑j ...
    .text:0000555555554D13                 mov     rax, [rbp+var_18]
    .text:0000555555554D17                 xor     rax, fs:28h
    .text:0000555555554D20                 jz      short loc_555555554D27
    .text:0000555555554D22                 call    ___stack_chk_fail
    .text:0000555555554D27 ; ---------------------------------------------------------------------------    .text:0000555555554D27
    .text:0000555555554D27 loc_555555554D27:                       ; CODE XREF: challenge2+16A↑j
    .text:0000555555554D27                 add     rsp, 1D8h
    .text:0000555555554D2E                 pop     rbx
    .text:0000555555554D2F                 pop     rbp
    .text:0000555555554D30                 retn
    .text:0000555555554D30 challenge2      endp

正确的运行逻辑： challenge2 -> loc_555555554BFC -> loc_555555554C6D ->
loc_555555554CB8 -> loc_555555554D13 -> loc_555555554D27

对应伪代码：

    
    
    unsigned __int64 __fastcall challenge2(_BYTE *a1)
    {
      unsigned int v2; // [rsp+10h] [rbp-1D0h]
      int v3; // [rsp+14h] [rbp-1CCh]
      int v4; // [rsp+18h] [rbp-1C8h]
      int v5; // [rsp+1Ch] [rbp-1C4h]
      struct utsname name; // [rsp+20h] [rbp-1C0h] BYREF
      char s[10]; // [rsp+1A6h] [rbp-3Ah] BYREF
      char v8[24]; // [rsp+1B0h] [rbp-30h] BYREF
      unsigned __int64 v9; // [rsp+1C8h] [rbp-18h]
    
      v9 = __readfsqword(0x28u);
      if ( uname(&name) )
      {
        perror("uname");
      }
      else
      {
        strcpy(s, "QilingOS");
        strcpy(v8, "ChallengeStart");
        v2 = 0;
        v3 = 0;
        while ( v4 < strlen(s) )
        {
          if ( name.sysname[v4] == s[v4] )
            ++v2;
          ++v4;
        }
        while ( v5 < strlen(v8) )
        {
          if ( name.version[v5] == v8[v5] )
            ++v3;
          ++v5;
        }
        if ( v2 == strlen(s) && v3 == strlen(v8) && v2 > 5 )
          *a1 = 1;
      }
      return __readfsqword(0x28u) ^ v9;
    }

第一个if判断：

    
    
      if ( uname(&name) )
      {
        perror("uname");
      }

`uname(&name)` 是一个系统调用函数，它的作用是获取当前系统的名称和版本信息，并将这些信息存储到?`struct
utsname`?类型的结构体变量?`name`?中，`name` 使用`struct utsname name;`声明
，如果成功获取的话函数返回值为0，就可以进入else了。else中我们最后需要执行`*a1 =
1`，这里面有两个循环进行字符串逐个判断，如果相同就能在最后的if判断中让`*a1 = 1`。此处我们需要了解uname的结构体，uname的结构为：

    
    
    struct utsname {
        char sysname[65];
        char nodename[65];
        char release[65];   
        char version[65];
        char machine[65];
        char domainname[65];
    };

我们需要让name.sysname等于"QilingOS"，name.version等于"ChallengeStart"。

出题人提供了源码，可以看到源码的逻辑跟分析的一致：

    
    
    void  challenge2(char *check) {
        unsigned int i, j, k, l;
        struct utsname name; 
        char qiling_OS[10]; 
        char chall_start[24];
    
        if ( uname(&name) ) {
            perror("uname");
        }
        else {
            strcpy(qiling_OS, "QilingOS");
            strcpy(chall_start, "ChallengeStart");
            i = 0;
            j = 0;
            while ( k < strlen(qiling_OS) ) {
                if ( name.sysname[k] == qiling_OS[k] )
                    ++i;
                ++k;
            }
            while ( l < strlen(chall_start) ) {
                if ( name.version[l] == chall_start[l] )
                    ++j;
                ++l;
            }
            if ( i == strlen(qiling_OS) && j == strlen(chall_start) && i > 5 )
                *check = 1;
        }
    }

根据上述分析，我们需要hook系统调用uname。在Qiling中有四种hook方式，这四个方式都是常量：

  1. QL_INTERCEPT.EXIT：在系统调用执行完成之后立即执行hook函数
  2. QL_INTERCEPT.ENTER：在系统调用执行之前执行hook函数
  3. QL_INTERCEPT.EXIT_TREE：在系统调用执行完成并返回后，执行完其他所有系统调用的hook函数之后再执行当前系统调用的hook函数
  4. QL_INTERCEPT.EXIT_ALL：在系统调用执行完成并返回后，执行所有系统调用的hook函数

为了使用上面的hook方式，需要使用 `from qiling.const import *` 导入Qiling模拟器中的常量。

系统调用返回结构体型数据时,会将结构体的地址存放在寄存器rdi中，因此我们需要使用 `ql.arch.regs.rdi`得到rdi中存储的uname地址。

#### writeup 2

writeup:

    
    
    from qiling import *
    from qiling.const import * #?导入Qiling模拟器中的常量
    
    def my_uname_on_exit_hook(ql, *args):
        rdi = ql.arch.regs.rdi
        print(f"utsname address: {hex(rdi)}") # utsname address: 0x80000000db50
        ql.mem.write(rdi, b'QilingOS\x00')
        ql.mem.write(rdi + 65 * 3, b'ChallengeStart\x00') # 000080000000DC13
    
    def challenge2(ql):
        # 使用QL_INTERCEPT.EXIT在系统调用执行完成之后立即执行hook函数，ql.os.set_syscall 使用方法在官方文档 Hijack 部分
        ql.os.set_syscall("uname", my_uname_on_exit_hook, QL_INTERCEPT.EXIT)
    
    if __name__ == '__main__':
        path = ["rootfs/x8664_linux/qilinglab-x86_64"]
        rootfs = "rootfs/x8664_linux"
        ql = Qiling(path, rootfs)
        # 记得加上challenge1
        challenge2(ql)
        ql.run()

用IDA看一下运行脚本后rdi指向的sysname和version，可以看到已经按照我们的脚本进行了修改：

![
](https://images.seebug.org/content/images/2023/05/55307a3b-bd79-4f3e-802b-7d6bc61fb55c.png-w331s)

![ ](https://images.seebug.org/content/images/2023/05/3419294a-996c-456b-bdcb-fd46b11b61a1.png-w331s)

![
](https://images.seebug.org/content/images/2023/05/4004674a-9bdb-4b75-b3c5-d72e2dcc1fde.png-w331s)

运行脚本，challenge2已解决：

    
    
    Checking which challenge are solved...
    [=]     write(fd = 0x1, buf = 0x55555575a260, count = 0x54) = 0x54
    Note: Some challenges will results in segfaults and infinite loops if they aren't solved.
    [=]     write(fd = 0x1, buf = 0x55555575a260, count = 0x5a) = 0x5a
    
    [=]     write(fd = 0x1, buf = 0x55555575a260, count = 0x1) = 0x1
    [=]     uname(buf = 0x80000000db50) = 0x0
    Challenge 1: SOLVED
    [=]     write(fd = 0x1, buf = 0x55555575a260, count = 0x14) = 0x14
    [=]     openat(fd = 0xffffff9c, path = 0x555555555698, flags = 0x0, mode = 0x0) = -0x2 (ENOENT)
    [=]     read(fd = 0xffffffff, buf = 0x80000000dcc0, length = 0x20) = -0x9 (EBADF)
    [=]     read(fd = 0xffffffff, buf = 0x80000000dcbf, length = 0x1) = -0x9 (EBADF)
    [=]     close(fd = 0xffffffff) = -0x1 (EPERM)
    [=]     getrandom(buf = 0x80000000dce0, buflen = 0x20, flags = 0x1) = 0x20
    Challenge 2: SOLVED
    [=]     write(fd = 0x1, buf = 0x55555575a260, count = 0x14) = 0x14
    Challenge 3: NOT SOLVED
    [=]     write(fd = 0x1, buf = 0x55555575a260, count = 0x18) = 0x18
    [=]     time() = 0x6471f7b0
    Challenge 4: NOT SOLVED
    [=]     write(fd = 0x1, buf = 0x55555575a260, count = 0x18) = 0x18

### Challenge 3: 自定义文件对象

> Challenge 3: Make '/dev/urandom' and 'getrandom' "collide".

IDA 看一下 Challenge 3：

    
    
    .text:0000555555554D31                 public challenge3
    .text:0000555555554D31 challenge3      proc near               ; CODE XREF: start+16B↓p
    .text:0000555555554D31
    .text:0000555555554D31 var_68          = qword ptr -68h
    .text:0000555555554D31 var_60          = dword ptr -60h
    .text:0000555555554D31 var_5C          = dword ptr -5Ch
    .text:0000555555554D31 fd              = dword ptr -58h
    .text:0000555555554D31 var_51          = byte ptr -51h
    .text:0000555555554D31 buf             = byte ptr -50h
    .text:0000555555554D31 var_30          = byte ptr -30h
    .text:0000555555554D31 var_8           = qword ptr -8
    .text:0000555555554D31
    .text:0000555555554D31                 push    rbp
    .text:0000555555554D32                 mov     rbp, rsp
    .text:0000555555554D35                 sub     rsp, 70h
    .text:0000555555554D39                 mov     [rbp+var_68], rdi
    .text:0000555555554D3D                 mov     rax, fs:28h
    .text:0000555555554D46                 mov     [rbp+var_8], rax
    .text:0000555555554D4A                 xor     eax, eax
    .text:0000555555554D4C                 mov     esi, 0          ; oflag
    .text:0000555555554D51                 lea     rdi, file       ; "/dev/urandom"
    .text:0000555555554D58                 mov     eax, 0
    .text:0000555555554D5D                 call    _open
    .text:0000555555554D62                 mov     [rbp+fd], eax
    .text:0000555555554D65                 lea     rcx, [rbp+buf]
    .text:0000555555554D69                 mov     eax, [rbp+fd]
    .text:0000555555554D6C                 mov     edx, 20h ; ' '  ; nbytes
    .text:0000555555554D71                 mov     rsi, rcx        ; buf
    .text:0000555555554D74                 mov     edi, eax        ; fd
    .text:0000555555554D76                 call    _read
    .text:0000555555554D7B                 lea     rcx, [rbp+var_51]
    .text:0000555555554D7F                 mov     eax, [rbp+fd]
    .text:0000555555554D82                 mov     edx, 1          ; nbytes
    .text:0000555555554D87                 mov     rsi, rcx        ; buf
    .text:0000555555554D8A                 mov     edi, eax        ; fd
    .text:0000555555554D8C                 call    _read
    .text:0000555555554D91                 mov     eax, [rbp+fd]
    .text:0000555555554D94                 mov     edi, eax        ; fd
    .text:0000555555554D96                 call    _close
    .text:0000555555554D9B                 lea     rax, [rbp+var_30]
    .text:0000555555554D9F                 mov     edx, 1
    .text:0000555555554DA4                 mov     esi, 20h ;
    .text:0000555555554DA9                 mov     rdi, rax
    .text:0000555555554DAC                 call    _getrandom
    .text:0000555555554DB1                 mov     [rbp+var_60], 0
    .text:0000555555554DB8                 mov     [rbp+var_5C], 0
    .text:0000555555554DBF                 jmp     short loc_555555554DF3
    .text:0000555555554DC1 ; ---------------------------------------------------------------------------    .text:0000555555554DC1
    .text:0000555555554DC1 loc_555555554DC1:                       ; CODE XREF: challenge3+C6↓j
    .text:0000555555554DC1                 mov     eax, [rbp+var_5C]
    .text:0000555555554DC4                 cdqe
    .text:0000555555554DC6                 movzx   edx, [rbp+rax+buf] ; edx清零，读取 rbp+rax+buf 地址处的一个字节,并将其扩充到64位移入edx寄存器低8位
    .text:0000555555554DCB                 mov     eax, [rbp+var_5C]
    .text:0000555555554DCE                 cdqe                       ; 将32位eax值扩展为64位rax值
    .text:0000555555554DD0                 movzx   eax, [rbp+rax+var_30]
    .text:0000555555554DD5                 cmp     dl, al
    .text:0000555555554DD7                 jnz     short loc_555555554DEF
    .text:0000555555554DD9                 mov     eax, [rbp+var_5C]
    .text:0000555555554DDC                 cdqe
    .text:0000555555554DDE                 movzx   edx, [rbp+rax+buf]
    .text:0000555555554DE3                 movzx   eax, [rbp+var_51]
    .text:0000555555554DE7                 cmp     dl, al             ; di：edx低8位，al：eax低8位
    .text:0000555555554DE9                 jz      short loc_555555554DEF
    .text:0000555555554DEB                 add     [rbp+var_60], 1
    .text:0000555555554DEF
    .text:0000555555554DEF loc_555555554DEF:                       ; CODE XREF: challenge3+A6↑j
    .text:0000555555554DEF                                         ; challenge3+B8↑j
    .text:0000555555554DEF                 add     [rbp+var_5C], 1
    .text:0000555555554DF3
    .text:0000555555554DF3 loc_555555554DF3:                       ; CODE XREF: challenge3+8E↑j
    .text:0000555555554DF3                 cmp     [rbp+var_5C], 1Fh
    .text:0000555555554DF7                 jle     short loc_555555554DC1 ; 小于或等于则跳转
    .text:0000555555554DF9                 cmp     [rbp+var_60], 20h ;
    .text:0000555555554DFD                 jnz     short loc_555555554E06
    .text:0000555555554DFF                 mov     rax, [rbp+var_68]
    .text:0000555555554E03                 mov     byte ptr [rax], 1 ; byte ptr是指定操作数的大小，这里是一个byte
                                                                     ; 将字节值1存储在rax寄存器指向的内存地址中
    .text:0000555555554E06
    .text:0000555555554E06 loc_555555554E06:                       ; CODE XREF: challenge3+CC↑j
    .text:0000555555554E06                 nop
    .text:0000555555554E07                 mov     rax, [rbp+var_8]
    .text:0000555555554E0B                 xor     rax, fs:28h
    .text:0000555555554E14                 jz      short locret_555555554E1B
    .text:0000555555554E16                 call    ___stack_chk_fail
    .text:0000555555554E1B ; ---------------------------------------------------------------------------    .text:0000555555554E1B
    .text:0000555555554E1B locret_555555554E1B:                    ; CODE XREF: challenge3+E3↑j
    .text:0000555555554E1B                 leave
    .text:0000555555554E1C                 retn
    .text:0000555555554E1C challenge3      endp

Challenge 3 伪代码：

    
    
    unsigned __int64 __fastcall challenge3(_BYTE *a1)
    {
      int v2; // [rsp+10h] [rbp-60h]
      int i; // [rsp+14h] [rbp-5Ch]
      int fd; // [rsp+18h] [rbp-58h]
      char v5; // [rsp+1Fh] [rbp-51h] BYREF
      char buf[32]; // [rsp+20h] [rbp-50h] BYREF
      char v7[40]; // [rsp+40h] [rbp-30h] BYREF
      unsigned __int64 v8; // [rsp+68h] [rbp-8h]
    
      v8 = __readfsqword(0x28u); // 从fs段读取地址0x28处的8个字节,并将其存储在v8变量中。地址0x28处的数据通常被用来存储函数的返回地址
      fd = open("/dev/urandom", 0);
      read(fd, buf, 0x20uLL);
      read(fd, &v5, 1uLL);
      close(fd);
      getrandom(v7, 32LL, 1LL);
      v2 = 0;
      for ( i = 0; i <= 31; ++i )
      {
        if ( buf[i] == v7[i] && buf[i] != v5 )
          ++v2;
      }
      if ( v2 == 32 )
        *a1 = 1; // 修改指针所指向的内存中的值
      return __readfsqword(0x28u) ^ v8;
    }

分析程序逻辑，主要关注点在buf，v5与v7三者之间的关系：

    
    
      read(fd, buf, 0x20uLL);
      read(fd, &v5, 1uLL);
    ···
      getrandom(v7, 32LL, 1LL);

`read(fd, buf, 0x20uLL)`：从文件描述符fd读取32(0x20)字节的数据，并将其存储在字符数组buf中。原函数：`ssize_t
read(int fd, void *buf, size_t count);`

`read(fd, &v5, 1uLL)`：从文件描述符fd读取1字节的数据，并将其存储在字符变量v5中。

`getrandom(v7, 32LL,
1LL)`：系统调用，从系统提供的随机数源获取随机数据。代码含义是从系统熵池中获取32字节的随机数据，并将其存储在字符数组v7中。

我们需要在i循环中让`buf[i]`与`v7[i]`相等，且`buf[i]`不等于`v5`。getrandom是利用系统调用获取随机数，urandom是利用文件读写操作获取随机数，要解决这道题需要让两者一样。关于
`/dev/urandom` 与 `getrandom` 的相关知识：

`/dev/urandom` 是一个 Unix/Linux 系统中的特殊文件，它是一个伪随机数发生器设备文件，用于生成随机数。

在Qiling中使用 `ql.add_fs_mapper("/dev/urandom", "/dev/urandom")` 将宿主机中的
`/dev/urandom (后面的)` 设备文件映射到 Qiling 虚拟机中的 `/dev/urandom （前面的）`
文件上，以便为虚拟机中的程序提供随机数服务。

getrandom使用方法：

    
    
    getrandom(ql, buf, buflen, flags)
    
    buf：指向缓冲区的指针，用于存储读取到的随机数据。
    buflen：要从系统熵池读取的字节数。
    flags：指定 getrandom 函数的行为。常见的 flags 值包括：
        0：如果系统熵池中没有足够的熵，getrandom 会阻塞直到有足够的熵可用。
        GRND_NONBLOCK（通常为 1）：getrandom 在系统熵池中没有足够的熵时，会立即返回错误而不是阻塞。
        GRND_RANDOM（通常为 2）：尝试从 /dev/random 获取随机数据，而不是从 /dev/urandom 获取。这个选项会导致 getrandom 的行为更加谨慎，可能会在熵不足时阻塞。
    
    返回值：
    如果成功获取随机数据，getrandom 返回实际读取的字节数。
    如果出错，返回 -1 并设置 errno。常见的错误包括 EAGAIN（系统熵池中没有足够的熵，且 flags 设置为非阻塞模式）和 EFAULT（buf 指针无效或指向不可访问的内存区域）。

我们可以使用[QlFsMappedObject](https://docs.qiling.io/en/latest/hijack/#hijacking-vfs-objects)自定义文件对象，实现"/dev/urandom"：

    
    
    from qiling import Qiling
    from qiling.os.mapper import QlFsMappedObject
    
    class FakeUrandom(QlFsMappedObject):
    
        def read(self, size: int) -> bytes:
            if size == 1: 
             return b"\x42" # v5的长度为1
            # return a constant value upon reading
            else:
             return b"\x41"
    
        def fstat(self) -> int: # fstat() 是Linux/Unix系统调用之一，用来获取文件的状态信息
            # return -1 to let syscall fstat ignore it
            return -1
    
        def close(self) -> int:
            return 0
    
    if __name__ == "__main__":
        ql = Qiling([r'rootfs/x86_linux/bin/x86_fetch_urandom'], r'rootfs/x86_linux')
    
        ql.add_fs_mapper(r'/dev/urandom', FakeUrandom())
        ql.run()

我们可以通过hook系统调用自定义一个"getrandom"，例如：

    
    
    def hook_getrandom(ql, buf, buflen, flags):
        # 自定义 getrandom 函数实现
        if buflen == 32:
            data = b'\x41' * buflen  # b'\x41' = A
            ql.mem.write(buf, data)
            ql.os.set_syscall_return(buflen)
        else:
            ql.os.set_syscall_return(-1)
    
    ···
    # 调用自定义系统调用
    ql.os.set_syscall("getrandom", hook_getrandom)

#### writeup 3

    
    
    from qiling import *
    from qiling.const import * #?导入Qiling模拟器中的常量
    from qiling.os.mapper import QlFsMappedObject
    
    class FakeUrandom(QlFsMappedObject):  
    
        def read(self, size: int) -> bytes:  
            if size == 1:
                return b"\x42" 
            else:
                return b"\x41" * size
    
        def close(self) -> int:
            return 0
    
    def hook_getrandom(ql, buf, buflen, flags):
        # 自定义 getrandom 函数实现
        if buflen == 32:
            data = b'\x41' * buflen  # b'\x41' = A
            ql.mem.write(buf, data)
            ql.os.set_syscall_return(buflen)
        else:
            ql.os.set_syscall_return(-1)
    
    def challenge3(ql):
        ql.add_fs_mapper(r'/dev/urandom', FakeUrandom())
        ql.os.set_syscall("getrandom", hook_getrandom)
    
    if __name__ == '__main__':
        path = ["rootfs/x8664_linux/qilinglab-x86_64"]
        rootfs = "rootfs/x8664_linux"
        ql = Qiling(path, rootfs)
        # 记得加上challenge1
        challenge2(ql)
        ql.run()

运行后，可以看到challenge 3已解决：

    
    
    Checking which challenge are solved...
    [=]     write(fd = 0x1, buf = 0x55555575a260, count = 0x54) = 0x54
    Note: Some challenges will results in segfaults and infinite loops if they aren't solved.
    [=]     write(fd = 0x1, buf = 0x55555575a260, count = 0x5a) = 0x5a
    
    [=]     write(fd = 0x1, buf = 0x55555575a260, count = 0x1) = 0x1
    utsname address: 0x80000000db50
    [=]     uname(buf = 0x80000000db50) = 0x0
    Challenge 1: SOLVED
    [=]     write(fd = 0x1, buf = 0x55555575a260, count = 0x14) = 0x14
    [=]     openat(fd = 0xffffff9c, path = 0x555555555698, flags = 0x0, mode = 0x0) = 0x3
    [=]     read(fd = 0x3, buf = 0x80000000dcc0, length = 0x20) = 0x20
    [=]     read(fd = 0x3, buf = 0x80000000dcbf, length = 0x1) = 0x1
    [=]     close(fd = 0x3) = 0x0
    [=]     getrandom(buf = 0x80000000dce0, buflen = 0x20, flags = 0x1) = ?
    Challenge 2: SOLVED
    [=]     write(fd = 0x1, buf = 0x55555575a260, count = 0x14) = 0x14
    Challenge 3: SOLVED
    [=]     write(fd = 0x1, buf = 0x55555575a260, count = 0x14) = 0x14
    [=]     time() = 0x6472521d
    Challenge 4: NOT SOLVED
    [=]     write(fd = 0x1, buf = 0x55555575a260, count = 0x18) = 0x18

### Challenge 4：hook特定地址

> Challenge 4: Enter inside the "forbidden" loop.
    
    
    .text:0000555555554E1D                 public challenge4
    .text:0000555555554E1D challenge4      proc near               ; CODE XREF: start+18F↓p
    .text:0000555555554E1D
    .text:0000555555554E1D var_18          = qword ptr -18h
    .text:0000555555554E1D var_8           = dword ptr -8
    .text:0000555555554E1D var_4           = dword ptr -4
    .text:0000555555554E1D
    .text:0000555555554E1D                 push    rbp
    .text:0000555555554E1E                 mov     rbp, rsp
    .text:0000555555554E21                 mov     [rbp+var_18], rdi
    .text:0000555555554E25                 mov     [rbp+var_8], 0
    .text:0000555555554E2C                 mov     [rbp+var_4], 0
    .text:0000555555554E33                 jmp     short loc_555555554E40
    .text:0000555555554E35 ; ---------------------------------------------------------------------------    .text:0000555555554E35
    .text:0000555555554E35 loc_555555554E35:                       ; CODE XREF: challenge4+29↓j
    .text:0000555555554E35                 mov     rax, [rbp+var_18]
    .text:0000555555554E39                 mov     byte ptr [rax], 1
    .text:0000555555554E3C                 add     [rbp+var_4], 1
    .text:0000555555554E40
    .text:0000555555554E40 loc_555555554E40:                       ; CODE XREF: challenge4+16↑j
    .text:0000555555554E40                 mov     eax, [rbp+var_8]
    .text:0000555555554E43                 cmp     [rbp+var_4], eax
    .text:0000555555554E46                 jl      short loc_555555554E35 ; 小于则跳转
    .text:0000555555554E48                 nop
    .text:0000555555554E49                 pop     rbp
    .text:0000555555554E4A                 retn
    .text:0000555555554E4A challenge4      endp

IDA 查看伪代码发现什么都看不到：

    
    
    __int64 challenge4()
    {
      return 0LL;
    }

根据汇编逻辑，我们最终需要实现 `mov byte ptr [rax], 1` ，但是在 loc_555555554E40 中 ：

    
    
    mov     [rbp+var_8], 0
    mov     [rbp+var_4], 0
    
    ···
    
    mov     eax, [rbp+var_8]
    cmp     [rbp+var_4], eax
    add     [rbp+var_4], 1

实际上就是
0比0，我们需要让`[rbp+var_4]`小于`[rbp+var_8]`，jl指令才会跳转到loc_555555554E35函数中，执行`*a=1`，然后再通过
`add [rbp+var_4], 1` 跳出循环。

![
](https://images.seebug.org/content/images/2023/05/dd764a9a-c627-4695-8793-0a82609bd40d.png-w331s)

我们根据逻辑patch汇编使得 `[rbp+var_8], 1` ，就可以得到正确的伪代码：

![
](https://images.seebug.org/content/images/2023/05/2ea919a6-398b-41f1-9d8b-6a8d2f8d3c24.png-w331s)

    
    
    __int64 __fastcall challenge4(_BYTE *a1)
    {
      __int64 result; // rax
      int i; // [rsp+14h] [rbp-4h]
    
      for ( i = 0; ; ++i ) // for 循环运行一次后让*a1 = 1，接着break。
      {
        result = 1LL;
        if ( i >= 1 )
          break;
        *a1 = 1;
      }
      return result;
    }

可以看到我们的分析是正确的，接着就来编写 Qiling challenge 4 writeup：

#### writeup 4

    
    
    def enter_forbidden_loop_hook(ql):
        ql.arch.regs.eax = 1
    ?
    def challenge4(ql):
        """
        .text:0000555555554E40                 mov     eax, [rbp+var_8]
        .text:0000555555554E43                 cmp     [rbp+var_4], eax <-- 在运行此命令前hook eax，使得eax = 1
        .text:0000555555554E46                 jl      short loc_555555554E35
        """
        base = ql.mem.get_lib_base(os.path.split(ql.path)[-1])  # 根据文件路径查找已经加载的文件，获取对应文件的基地址
        # os.path.split(ql.path)：os.path.split 函数将 ql.path 分成两部分：目录名和基本文件名。这个函数返回一个包含这两部分的元组。
        # os.path.split(ql.path)[-1]：这将返回元组中的最后一个元素，即基本文件名。在 Python 中，-1 索引表示列表或元组的最后一个元素。
        # base = ql.mem.get_lib_base(os.path.split(ql.path)[-1])：ql.mem.get_lib_base 函数使用提取的文件名作为参数，以获取已加载库的基地址。将返回的基地址赋值给变量 base
        hook_addr = base + 0xE43
        ql.hook_address(enter_forbidden_loop_hook, hook_addr) # 当执行流程到达hook_addr时，该函数将被调用。此时hook_addr处的代码还未被执行。

运行后，可以看到 challenge 4 已经被解决：

    
    
    Challenge 1: SOLVED
    [=]     write(fd = 0x1, buf = 0x55555575a260, count = 0x14) = 0x14
    [=]     openat(fd = 0xffffff9c, path = 0x555555555698, flags = 0x0, mode = 0x0) = 0x3
    [=]     read(fd = 0x3, buf = 0x80000000dcc0, length = 0x20) = 0x20
    [=]     read(fd = 0x3, buf = 0x80000000dcbf, length = 0x1) = 0x1
    [=]     close(fd = 0x3) = 0x0
    [=]     getrandom(buf = 0x80000000dce0, buflen = 0x20, flags = 0x1) = ?
    Challenge 2: SOLVED
    [=]     write(fd = 0x1, buf = 0x55555575a260, count = 0x14) = 0x14
    Challenge 3: SOLVED
    [=]     write(fd = 0x1, buf = 0x55555575a260, count = 0x14) = 0x14
    [=]     time() = 0x64730987
    Challenge 4: SOLVED
    [=]     write(fd = 0x1, buf = 0x55555575a260, count = 0x14) = 0x14

### Challenge 5：hook函数调用

> Challenge 5: Guess every call to rand().
    
    
    .text:0000555555554E4B                 public challenge5
    .text:0000555555554E4B challenge5      proc near               ; CODE XREF: start+1B3↓p
    .text:0000555555554E4B
    .text:0000555555554E4B var_58          = qword ptr -58h
    .text:0000555555554E4B var_48          = dword ptr -48h
    .text:0000555555554E4B var_44          = dword ptr -44h
    .text:0000555555554E4B var_40          = dword ptr -40h
    .text:0000555555554E4B var_20          = dword ptr -20h
    .text:0000555555554E4B var_8           = qword ptr -8
    .text:0000555555554E4B
    .text:0000555555554E4B                 push    rbp
    .text:0000555555554E4C                 mov     rbp, rsp
    .text:0000555555554E4F                 sub     rsp, 60h
    .text:0000555555554E53                 mov     [rbp+var_58], rdi
    .text:0000555555554E57                 mov     rax, fs:28h
    .text:0000555555554E60                 mov     [rbp+var_8], rax
    .text:0000555555554E64                 xor     eax, eax
    .text:0000555555554E66                 mov     edi, 0          ; timer
    .text:0000555555554E6B                 call    _time
    .text:0000555555554E70                 mov     edi, eax        ; seed
    .text:0000555555554E72                 call    _srand
    .text:0000555555554E77                 mov     [rbp+var_48], 0
    .text:0000555555554E7E                 jmp     short loc_555555554EA1
    .text:0000555555554E80 ; ---------------------------------------------------------------------------    .text:0000555555554E80
    .text:0000555555554E80 loc_555555554E80:                       ; CODE XREF: challenge5+5A↓j
    .text:0000555555554E80                 mov     eax, [rbp+var_48]
    .text:0000555555554E83                 cdqe
    .text:0000555555554E85                 mov     [rbp+rax*4+var_40], 0
    .text:0000555555554E8D                 call    _rand
    .text:0000555555554E92                 mov     edx, eax
    .text:0000555555554E94                 mov     eax, [rbp+var_48]
    .text:0000555555554E97                 cdqe
    .text:0000555555554E99                 mov     [rbp+rax*4+var_20], edx
    .text:0000555555554E9D                 add     [rbp+var_48], 1
    .text:0000555555554EA1
    .text:0000555555554EA1 loc_555555554EA1:                       ; CODE XREF: challenge5+33↑j
    .text:0000555555554EA1                 cmp     [rbp+var_48], 4
    .text:0000555555554EA5                 jle     short loc_555555554E80
    .text:0000555555554EA7                 mov     [rbp+var_44], 0
    .text:0000555555554EAE                 jmp     short loc_555555554ED3
    .text:0000555555554EB0 ; ---------------------------------------------------------------------------    .text:0000555555554EB0
    .text:0000555555554EB0 loc_555555554EB0:                       ; CODE XREF: challenge5+8C↓j
    .text:0000555555554EB0                 mov     eax, [rbp+var_44]
    .text:0000555555554EB3                 cdqe
    .text:0000555555554EB5                 mov     edx, [rbp+rax*4+var_40]
    .text:0000555555554EB9                 mov     eax, [rbp+var_44]
    .text:0000555555554EBC                 cdqe
    .text:0000555555554EBE                 mov     eax, [rbp+rax*4+var_20]
    .text:0000555555554EC2                 cmp     edx, eax
    .text:0000555555554EC4                 jz      short loc_555555554ECF
    .text:0000555555554EC6                 mov     rax, [rbp+var_58]
    .text:0000555555554ECA                 mov     byte ptr [rax], 0
    .text:0000555555554ECD                 jmp     short loc_555555554EE0
    .text:0000555555554ECF ; ---------------------------------------------------------------------------    .text:0000555555554ECF
    .text:0000555555554ECF loc_555555554ECF:                       ; CODE XREF: challenge5+79↑j
    .text:0000555555554ECF                 add     [rbp+var_44], 1
    .text:0000555555554ED3
    .text:0000555555554ED3 loc_555555554ED3:                       ; CODE XREF: challenge5+63↑j
    .text:0000555555554ED3                 cmp     [rbp+var_44], 4
    .text:0000555555554ED7                 jle     short loc_555555554EB0
    .text:0000555555554ED9                 mov     rax, [rbp+var_58]
    .text:0000555555554EDD                 mov     byte ptr [rax], 1
    .text:0000555555554EE0
    .text:0000555555554EE0 loc_555555554EE0:                       ; CODE XREF: challenge5+82↑j
    .text:0000555555554EE0                 mov     rax, [rbp+var_8]
    .text:0000555555554EE4                 xor     rax, fs:28h
    .text:0000555555554EED                 jz      short locret_555555554EF4
    .text:0000555555554EEF                 call    ___stack_chk_fail
    .text:0000555555554EF4 ; ---------------------------------------------------------------------------    .text:0000555555554EF4
    .text:0000555555554EF4 locret_555555554EF4:                    ; CODE XREF: challenge5+A2↑j
    .text:0000555555554EF4                 leave
    .text:0000555555554EF5                 retn
    .text:0000555555554EF5 challenge5      endp

challenge 5 伪代码如下：

    
    
    unsigned __int64 __fastcall challenge5(_BYTE *a1)
    {
      unsigned int v1; // eax
      int i; // [rsp+18h] [rbp-48h]
      int j; // [rsp+1Ch] [rbp-44h]
      int v5[14]; // [rsp+20h] [rbp-40h]
      unsigned __int64 v6; // [rsp+58h] [rbp-8h]
    
      v6 = __readfsqword(0x28u);
      v1 = time(0LL);
      srand(v1); // srand 使用时间作为种子，生成真正的随机数
      for ( i = 0; i <= 4; ++i )
      {
        v5[i] = 0;          // 0,1,2,3,4
        v5[i + 8] = rand(); // 8,9,19,11,12
      }
      for ( j = 0; j <= 4; ++j ) // 我们需要绕过此循环
      {
        if ( v5[j] != v5[j + 8] )
        {
          *a1 = 0;
          return __readfsqword(0x28u) ^ v6;
        }
      }
      *a1 = 1;
      return __readfsqword(0x28u) ^ v6;
    }

分析代码逻辑，我们想要最后得到`*a1 = 1`的话，需要绕过第二个for循环。让rand()得到的值都为0就可以了。hook方法在官方手册
[Hijacking OS API (POSIX)](https://docs.qiling.io/en/latest/hijack/) 。

#### writeup 5

    
    
    def hook_rand(ql):
        ql.arch.regs.rax = 0 # 在x86-64架构中，函数的返回值通常保存在RAX寄存器中。rand函数的返回值会存储在rax寄存器
    
    def challenge5(ql):
        ql.os.set_api('rand', hook_rand)

运行后没有显示第五个挑战是否被解决，因为被第六题的死循环卡住了。

### Challenge 6：修改寄存器值

> Challenge 6: Avoid the infinite loop.
    
    
    .text:0000555555554EF6                 public challenge6
    .text:0000555555554EF6 challenge6      proc near               ; CODE XREF: start+1D7↓p
    .text:0000555555554EF6
    .text:0000555555554EF6 var_18          = qword ptr -18h
    .text:0000555555554EF6 var_5           = byte ptr -5
    .text:0000555555554EF6 var_4           = dword ptr -4
    .text:0000555555554EF6
    .text:0000555555554EF6                 push    rbp
    .text:0000555555554EF7                 mov     rbp, rsp
    .text:0000555555554EFA                 mov     [rbp+var_18], rdi
    .text:0000555555554EFE                 mov     [rbp+var_4], 0
    .text:0000555555554F05                 mov     [rbp+var_5], 1
    .text:0000555555554F09                 jmp     short loc_555555554F12
    .text:0000555555554F0B ; ---------------------------------------------------------------------------    .text:0000555555554F0B
    .text:0000555555554F0B loc_555555554F0B:                       ; CODE XREF: challenge6+22↓j
    .text:0000555555554F0B                 mov     [rbp+var_4], 1
    .text:0000555555554F12
    .text:0000555555554F12 loc_555555554F12:                       ; CODE XREF: challenge6+13↑j
    .text:0000555555554F12                 movzx   eax, [rbp+var_5]
    .text:0000555555554F16                 test    al, al          ; 不修改al的内容,只更新标志位
    .text:0000555555554F18                 jnz     short loc_555555554F0B ; ZF=0 则跳转loc_555555554F0B函数
    .text:0000555555554F1A                 mov     rax, [rbp+var_18]
    .text:0000555555554F1E                 mov     byte ptr [rax], 1
    .text:0000555555554F21                 nop
    .text:0000555555554F22                 pop     rbp
    .text:0000555555554F23                 retn
    .text:0000555555554F23 challenge6      endp

查看伪代码，可以看到跟第四题一样：

    
    
    void challenge6()
    {
      while ( 1 )
        ;
    }

![
](https://images.seebug.org/content/images/2023/05/37a8738b-67cd-4874-a32f-f91f7199add0.png-w331s)

我们需要执行loc_555555554F0B函数，然后再退出循环。我们需要让ZF=0，jnz才能跳转loc_555555554F0B函数。

主要关注点在`test al, al`上，这条指令的含义是将EAX的低8位(al)与自身与运算，主要是用于修改ZF标志位。

    
    
    test al, al = al & al
    由于操作数 al 相同,所以运算结果必然是 al 本身的值。
    根据运算结果值是否为 0,ZF 标志位会被设置为:
    结果为 0:ZF=1
    结果不为 0:ZF=0

因此我们需要将eax设置为0，对`mov [rbp+var_5], 1` 进行patch，改为 `mov [rbp+var_5],
0`，就可以正确生成伪代码了，得到的和我们预期的一致。

    
    
    void __fastcall challenge6(_BYTE *a1)
    {
      *a1 = 1;
    }

#### writeup 6

    
    
    def hook_rax(ql):
        ql.arch.regs.rax = 0
    def challenge6(ql):
        base = ql.mem.get_lib_base(os.path.split(ql.path)[-1])
        hook_addr = base + 0xF16
        ql.hook_address(hook_rax, hook_addr)

运行后可以看到第五个挑战已经解决，但是第六个还没显示，应该是需要解出第七题：

    
    
    Challenge 1: SOLVED
    [=]     write(fd = 0x1, buf = 0x55555575a260, count = 0x14) = 0x14
    [=]     openat(fd = 0xffffff9c, path = 0x555555555698, flags = 0x0, mode = 0x0) = 0x3
    [=]     read(fd = 0x3, buf = 0x80000000dcc0, length = 0x20) = 0x20
    [=]     read(fd = 0x3, buf = 0x80000000dcbf, length = 0x1) = 0x1
    [=]     close(fd = 0x3) = 0x0
    [=]     getrandom(buf = 0x80000000dce0, buflen = 0x20, flags = 0x1) = ?
    Challenge 2: SOLVED
    [=]     write(fd = 0x1, buf = 0x55555575a260, count = 0x14) = 0x14
    Challenge 3: SOLVED
    [=]     write(fd = 0x1, buf = 0x55555575a260, count = 0x14) = 0x14
    [=]     time() = 0x64732fa5
    Challenge 4: SOLVED
    [=]     write(fd = 0x1, buf = 0x55555575a260, count = 0x14) = 0x14
    Challenge 5: SOLVED
    [=]     write(fd = 0x1, buf = 0x55555575a260, count = 0x14) = 0x14

### Challenge 7：hook函数调用

> Challenge 7: Don't waste time waiting for 'sleep'.
    
    
    .text:0000555555554F24                 public challenge7
    .text:0000555555554F24 challenge7      proc near               ; CODE XREF: start+1FB↓p
    .text:0000555555554F24
    .text:0000555555554F24 var_8           = qword ptr -8
    .text:0000555555554F24
    .text:0000555555554F24                 push    rbp
    .text:0000555555554F25                 mov     rbp, rsp
    .text:0000555555554F28                 sub     rsp, 10h
    .text:0000555555554F2C                 mov     [rbp+var_8], rdi
    .text:0000555555554F30                 mov     rax, [rbp+var_8]
    .text:0000555555554F34                 mov     byte ptr [rax], 1
    .text:0000555555554F37                 mov     edi, 0FFFFFFFFh ; seconds
    .text:0000555555554F3C                 call    _sleep          ; <------- hook
    .text:0000555555554F41                 nop
    .text:0000555555554F42                 leave
    .text:0000555555554F43                 retn
    .text:0000555555554F43 challenge7      endp

伪代码如下：

    
    
    unsigned int __fastcall challenge7(_BYTE *a1)
    {
      *a1 = 1;
      return sleep(0xFFFFFFFF);
    }

我们可以利用之前学的方法hook sleep函数，还是比较简单的。

#### writeup 7

    
    
    def hook_sleep(ql):
        return 0
    def challenge7(ql):
        ql.os.set_api('sleep', hook_sleep)

运行后，可以看到1-7题已解决：

    
    
    [=]     write(fd = 0x1, buf = 0x55555575a260, count = 0x19) = 0x19
    You solved 7/11 of the challenges
    [=]     write(fd = 0x1, buf = 0x55555575a260, count = 0x22) = 0x22
    [=]     exit_group(code = 0x0) = ?

### Challenge 8：修改结构体的值

> Challenge 8: Unpack the struct and write at the target address.
    
    
    .text:0000555555554F44                 public challenge8
    .text:0000555555554F44 challenge8      proc near               ; CODE XREF: start+21F↓p
    .text:0000555555554F44
    .text:0000555555554F44 var_18          = qword ptr -18h
    .text:0000555555554F44 var_8           = qword ptr -8
    .text:0000555555554F44
    .text:0000555555554F44                 push    rbp
    .text:0000555555554F45                 mov     rbp, rsp
    .text:0000555555554F48                 sub     rsp, 20h
    .text:0000555555554F4C                 mov     [rbp+var_18], rdi
    .text:0000555555554F50                 mov     edi, 18h        ; size
    .text:0000555555554F55                 call    _malloc
    .text:0000555555554F5A                 mov     [rbp+var_8], rax
    .text:0000555555554F5E                 mov     edi, 1Eh        ; size
    .text:0000555555554F63                 call    _malloc
    .text:0000555555554F68                 mov     rdx, rax
    .text:0000555555554F6B                 mov     rax, [rbp+var_8]
    .text:0000555555554F6F                 mov     [rax], rdx
    .text:0000555555554F72                 mov     rax, [rbp+var_8]
    .text:0000555555554F76                 mov     dword ptr [rax+8], 539h
    .text:0000555555554F7D                 mov     rax, [rbp+var_8]
    .text:0000555555554F81                 movss   xmm0, cs:dword_555555555A98
    .text:0000555555554F89                 movss   dword ptr [rax+0Ch], xmm0
    .text:0000555555554F8E                 mov     rax, [rbp+var_8]
    .text:0000555555554F92                 mov     rax, [rax]
    .text:0000555555554F95                 mov     rcx, 64206D6F646E6152h
    .text:0000555555554F9F                 mov     [rax], rcx
    .text:0000555555554FA2                 mov     dword ptr [rax+8], 617461h
    .text:0000555555554FA9                 mov     rax, [rbp+var_8]
    .text:0000555555554FAD                 mov     rdx, [rbp+var_18]
    .text:0000555555554FB1                 mov     [rax+10h], rdx
    .text:0000555555554FB5                 nop
    .text:0000555555554FB6                 leave
    .text:0000555555554FB7                 retn
    .text:0000555555554FB7 challenge8      endp

伪代码如下：

    
    
    _DWORD *__fastcall challenge8(__int64 a1)
    {
      _DWORD *result; // rax
      _DWORD *v2; // [rsp+18h] [rbp-8h]
    
      v2 = malloc(0x18uLL);             // 调用malloc函数，请求分配0x18字节（24字节）的内存。分配成功后，指向分配内存的指针被赋值给变量v2
      *(_QWORD *)v2 = malloc(0x1EuLL);  // 调用malloc函数，请求分配0x1E字节（30字节）的内存。
                                        // 将返回的指针（指向分配的30字节内存块）存储在v2所指向的内存中的前8个字节（64位系统一个指针大小为8字节，即一个_QWORD）
      v2[2] = 1337;
      v2[3] = 1039980266;
      strcpy(*(char **)v2, "Random data");
      result = v2;
      *((_QWORD *)v2 + 2) = a1;
      return result;
    }

v2是一个指针，指向malloc分配的内存块，相当于结构体的头指针，结构体整理后的内容如下：

![
](https://images.seebug.org/content/images/2023/05/309ee7cc-9505-429d-9b38-0ca6e03b100e.png-w331s)

    
    
    typedef struct {
        char *string_ptr; // 8 字节的指针，指向字符串 "Random data" 所在的内存
        uint32_t value1;  // 4 字节的整数，值为 1337
        uint32_t value2;  // 4 字节的整数，值为 1039980266
        int64_t a1;       // 8 字节的整数，值为传入的参数 a1
    } CustomStruct;

我们需要修改`*a1`为1，我使用的是以下方法对程序运行时存在的魔数进行搜索来判断结构体头指针位置，进而根据对应地址进行修改：

#### writeup 8

    
    
    import struct
    
    def challenge8_hook(ql):
    
        # 在内存中寻找魔数
        MAGIC = 0x3DFCD6EA00000539
    '''
        魔数由结构体中 value1 与 value2 构成。
        1. 将 value1 转换为 16 进制表示：1337 的 16 进制表示为 0x539。
        2. 将 value2 转换为 16 进制表示：1039980266 的 16 进制表示为 0x3DFCD6EA。
        3. 将 value2 字段左移 32 位，这相当于将其乘以 2^32：0x3DFCD6EA * 2^32 = 0x3DFCD6EA00000000。
        4. 将 value2 与 alue1 的值相加：0x3DFCD6EA00000000 + 0x539 = 0x3DFCD6EA00000539。
        所以，将 value1 和 value2 字段组合得到的魔数是 0x3DFCD6EA00000539。
    '''
    
        magic_addrs = ql.mem.search(ql.pack64(MAGIC)) # 转换魔数成为字节序列
    
        for magic_addr in magic_addrs: # 为了避免重复，循环检测
    
            # Dump and unpack the candidate structure
            candidate_heap_struct_addr = magic_addr - 8 # 魔数距离堆头指针距离为 8 bytes
            candidate_heap_struct = ql.mem.read(candidate_heap_struct_addr, 24) # 获取结构体地址结构
    
            string_addr, _ , check_addr = struct.unpack('QQQ', candidate_heap_struct) 
            # struct.unpack() 是一个 Python 函数，用于将字节序列解包为多个值，解包 candidate_heap_struct 地址结构。
            # 'QQQ' 是一个格式字符串，表示要解包的数据结构包含3个64位（8 字节）无符号整数。
            # string_addr, _ , check_addr：只关注 string_addr 与 check_addr，最后得到相应地址
    
            if ql.mem.string(string_addr) == "Random data":
                # 修改*a1为1
                ql.mem.write(check_addr, b"\x01")
                break
    
    def challenge8(ql):
        base_addr = ql.mem.get_lib_base(os.path.split(ql.path)[-1])
        end_of_challenge8 = base_addr + 0xFB5     # 程序运行结束时的地址
    
        ql.hook_address(challenge8_hook, end_of_challenge8)

运行后可以看到第八题已解出：

    
    
    You solved 8/11 of the challenges
    [=]     write(fd = 0x1, buf = 0x55555575a260, count = 0x22) = 0x22
    [=]     exit_group(code = 0x0) = ?

### Challenge 9： hook函数调用

> Challenge 9: Fix some string operation to make the iMpOsSiBlE come true.
    
    
    .text:0000555555554FB8                 public challenge9
    .text:0000555555554FB8 challenge9      proc near               ; CODE XREF: start+243↓p
    .text:0000555555554FB8
    .text:0000555555554FB8 var_68          = qword ptr -68h
    .text:0000555555554FB8 var_58          = qword ptr -58h
    .text:0000555555554FB8 dest            = byte ptr -50h
    .text:0000555555554FB8 src             = byte ptr -30h
    .text:0000555555554FB8 var_28          = qword ptr -28h
    .text:0000555555554FB8 var_20          = qword ptr -20h
    .text:0000555555554FB8 var_18          = dword ptr -18h
    .text:0000555555554FB8 var_8           = qword ptr -8
    .text:0000555555554FB8
    .text:0000555555554FB8                 push    rbp
    .text:0000555555554FB9                 mov     rbp, rsp
    .text:0000555555554FBC                 sub     rsp, 70h
    .text:0000555555554FC0                 mov     [rbp+var_68], rdi
    .text:0000555555554FC4                 mov     rax, fs:28h
    .text:0000555555554FCD                 mov     [rbp+var_8], rax
    .text:0000555555554FD1                 xor     eax, eax
    .text:0000555555554FD3                 mov     rax, cs:qword_5555555556A5
    .text:0000555555554FDA                 mov     rdx, cs:qword_5555555556AD
    .text:0000555555554FE1                 mov     qword ptr [rbp+src], rax
    .text:0000555555554FE5                 mov     [rbp+var_28], rdx
    .text:0000555555554FE9                 mov     rax, cs:qword_5555555556B5
    .text:0000555555554FF0                 mov     [rbp+var_20], rax
    .text:0000555555554FF4                 mov     eax, cs:dword_5555555556BD
    .text:0000555555554FFA                 mov     [rbp+var_18], eax
    .text:0000555555554FFD                 lea     rdx, [rbp+src]
    .text:0000555555555001                 lea     rax, [rbp+dest]
    .text:0000555555555005                 mov     rsi, rdx        ; src
    .text:0000555555555008                 mov     rdi, rax        ; dest
    .text:000055555555500B                 call    _strcpy
    .text:0000555555555010                 lea     rax, [rbp+dest]
    .text:0000555555555014                 mov     [rbp+var_58], rax
    .text:0000555555555018                 jmp     short loc_555555555038
    .text:000055555555501A ; ---------------------------------------------------------------------------    .text:000055555555501A
    .text:000055555555501A loc_55555555501A:                       ; CODE XREF: challenge9+89↓j
    .text:000055555555501A                 mov     rax, [rbp+var_58]
    .text:000055555555501E                 movzx   eax, byte ptr [rax]
    .text:0000555555555021                 movsx   eax, al
    .text:0000555555555024                 mov     edi, eax        ; c
    .text:0000555555555026                 call    _tolower
    .text:000055555555502B                 mov     edx, eax
    .text:000055555555502D                 mov     rax, [rbp+var_58]
    .text:0000555555555031                 mov     [rax], dl
    .text:0000555555555033                 add     [rbp+var_58], 1
    .text:0000555555555038
    .text:0000555555555038 loc_555555555038:                       ; CODE XREF: challenge9+60↑j
    .text:0000555555555038                 mov     rax, [rbp+var_58]
    .text:000055555555503C                 movzx   eax, byte ptr [rax]
    .text:000055555555503F                 test    al, al
    .text:0000555555555041                 jnz     short loc_55555555501A
    .text:0000555555555043                 lea     rdx, [rbp+dest]
    .text:0000555555555047                 lea     rax, [rbp+src]
    .text:000055555555504B                 mov     rsi, rdx        ; s2
    .text:000055555555504E                 mov     rdi, rax        ; s1
    .text:0000555555555051                 call    _strcmp
    .text:0000555555555056                 test    eax, eax
    .text:0000555555555058                 setz    dl
    .text:000055555555505B                 mov     rax, [rbp+var_68]
    .text:000055555555505F                 mov     [rax], dl
    .text:0000555555555061                 nop
    .text:0000555555555062                 mov     rax, [rbp+var_8]
    .text:0000555555555066                 xor     rax, fs:28h
    .text:000055555555506F                 jz      short locret_555555555076
    .text:0000555555555071                 call    ___stack_chk_fail
    .text:0000555555555076 ; ---------------------------------------------------------------------------    .text:0000555555555076
    .text:0000555555555076 locret_555555555076:                    ; CODE XREF: challenge9+B7↑j
    .text:0000555555555076                 leave
    .text:0000555555555077                 retn
    .text:0000555555555077 challenge9      endp

伪代码为：

    
    
    unsigned __int64 __fastcall challenge9(bool *a1)
    {
      char *i; // [rsp+18h] [rbp-58h]
      char dest[32]; // [rsp+20h] [rbp-50h] BYREF
      char src[40]; // [rsp+40h] [rbp-30h] BYREF
      unsigned __int64 v5; // [rsp+68h] [rbp-8h]
    
      v5 = __readfsqword(0x28u);
      strcpy(src, "aBcdeFghiJKlMnopqRstuVWxYz");
      strcpy(dest, src);
      for ( i = dest; *i; ++i )
        *i = tolower(*i);
      *a1 = strcmp(src, dest) == 0;
      return __readfsqword(0x28u) ^ v5;
    }

根据代码，我们需要让 `strcmp(src, dest) == 0` ，strcmp(str1,str2) 如果`str1 == str2`,则返回 0。
tolower函数是将给定的字符转换为小写形式。我们可以通过hook tolower让tolower失效，strcmp自然能够顺利对比一致。

#### writeup 9

    
    
    def hook_tolower(ql):
        return 0
    def challenge9(ql):
        ql.os.set_api('tolower', hook_tolower)

运行后顺利通过：

    
    
    You solved 9/11 of the challenges
    [=]     write(fd = 0x1, buf = 0x55555575a260, count = 0x22) = 0x22
    [=]     exit_group(code = 0x0) = ?

### Challenge 10：自定义文件对象

> Challenge 10: Fake the 'cmdline' line file to return the right content.
    
    
    .text:0000555555555078                 public challenge10
    .text:0000555555555078 challenge10     proc near               ; CODE XREF: start+267↓p
    .text:0000555555555078
    .text:0000555555555078 var_68          = qword ptr -68h
    .text:0000555555555078 var_60          = dword ptr -60h
    .text:0000555555555078 fd              = dword ptr -5Ch
    .text:0000555555555078 var_58          = qword ptr -58h
    .text:0000555555555078 buf             = byte ptr -50h
    .text:0000555555555078 var_8           = qword ptr -8
    .text:0000555555555078
    .text:0000555555555078                 push    rbp
    .text:0000555555555079                 mov     rbp, rsp
    .text:000055555555507C                 sub     rsp, 70h
    .text:0000555555555080                 mov     [rbp+var_68], rdi
    .text:0000555555555084                 mov     rax, fs:28h
    .text:000055555555508D                 mov     [rbp+var_8], rax
    .text:0000555555555091                 xor     eax, eax
    .text:0000555555555093                 mov     esi, 0          ; oflag
    .text:0000555555555098                 lea     rdi, aProcSelfCmdlin ; "/proc/self/cmdline"
    .text:000055555555509F                 mov     eax, 0
    .text:00005555555550A4                 call    _open
    .text:00005555555550A9                 mov     [rbp+fd], eax
    .text:00005555555550AC                 cmp     [rbp+fd], 0FFFFFFFFh
    .text:00005555555550B0                 jz      loc_55555555513F
    .text:00005555555550B6                 lea     rcx, [rbp+buf]
    .text:00005555555550BA                 mov     eax, [rbp+fd]
    .text:00005555555550BD                 mov     edx, 3Fh ; '?'  ; nbytes
    .text:00005555555550C2                 mov     rsi, rcx        ; buf
    .text:00005555555550C5                 mov     edi, eax        ; fd
    .text:00005555555550C7                 call    _read
    .text:00005555555550CC                 mov     [rbp+var_58], rax
    .text:00005555555550D0                 cmp     [rbp+var_58], 0
    .text:00005555555550D5                 jle     short loc_555555555142
    .text:00005555555550D7                 mov     eax, [rbp+fd]
    .text:00005555555550DA                 mov     edi, eax        ; fd
    .text:00005555555550DC                 call    _close
    .text:00005555555550E1                 mov     [rbp+var_60], 0
    .text:00005555555550E8                 jmp     short loc_555555555106
    .text:00005555555550EA ; ---------------------------------------------------------------------------    .text:00005555555550EA
    .text:00005555555550EA loc_5555555550EA:                       ; CODE XREF: challenge10+97↓j
    .text:00005555555550EA                 mov     eax, [rbp+var_60]
    .text:00005555555550ED                 cdqe
    .text:00005555555550EF                 movzx   eax, [rbp+rax+buf]
    .text:00005555555550F4                 test    al, al
    .text:00005555555550F6                 jnz     short loc_555555555102
    .text:00005555555550F8                 mov     eax, [rbp+var_60]
    .text:00005555555550FB                 cdqe
    .text:00005555555550FD                 mov     [rbp+rax+buf], 20h ; ' '
    .text:0000555555555102
    .text:0000555555555102 loc_555555555102:                       ; CODE XREF: challenge10+7E↑j
    .text:0000555555555102                 add     [rbp+var_60], 1
    .text:0000555555555106
    .text:0000555555555106 loc_555555555106:                       ; CODE XREF: challenge10+70↑j
    .text:0000555555555106                 mov     eax, [rbp+var_60]
    .text:0000555555555109                 cdqe
    .text:000055555555510B                 cmp     [rbp+var_58], rax
    .text:000055555555510F                 jg      short loc_5555555550EA ; 大于则跳转
    .text:0000555555555111                 lea     rdx, [rbp+buf]
    .text:0000555555555115                 mov     rax, [rbp+var_58]
    .text:0000555555555119                 add     rax, rdx
    .text:000055555555511C                 mov     byte ptr [rax], 0
    .text:000055555555511F                 lea     rax, [rbp+buf]
    .text:0000555555555123                 lea     rsi, s2         ; "qilinglab"
    .text:000055555555512A                 mov     rdi, rax        ; s1
    .text:000055555555512D                 call    _strcmp
    .text:0000555555555132                 test    eax, eax
    .text:0000555555555134                 jnz     short loc_555555555143
    .text:0000555555555136                 mov     rax, [rbp+var_68]
    .text:000055555555513A                 mov     byte ptr [rax], 1
    .text:000055555555513D                 jmp     short loc_555555555143
    .text:000055555555513F ; ---------------------------------------------------------------------------    .text:000055555555513F
    .text:000055555555513F loc_55555555513F:                       ; CODE XREF: challenge10+38↑j
    .text:000055555555513F                 nop
    .text:0000555555555140                 jmp     short loc_555555555143
    .text:0000555555555142 ; ---------------------------------------------------------------------------    .text:0000555555555142
    .text:0000555555555142 loc_555555555142:                       ; CODE XREF: challenge10+5D↑j
    .text:0000555555555142                 nop
    .text:0000555555555143
    .text:0000555555555143 loc_555555555143:                       ; CODE XREF: challenge10+BC↑j
    .text:0000555555555143                                         ; challenge10+C5↑j ...
    .text:0000555555555143                 mov     rax, [rbp+var_8]
    .text:0000555555555147                 xor     rax, fs:28h
    .text:0000555555555150                 jz      short locret_555555555157
    .text:0000555555555152                 call    ___stack_chk_fail
    .text:0000555555555157 ; ---------------------------------------------------------------------------    .text:0000555555555157
    .text:0000555555555157 locret_555555555157:                    ; CODE XREF: challenge10+D8↑j
    .text:0000555555555157                 leave
    .text:0000555555555158                 retn
    .text:0000555555555158 challenge10     endp

对应伪代码为：

    
    
    unsigned __int64 __fastcall challenge10(_BYTE *a1)
    {
      int i; // [rsp+10h] [rbp-60h]
      int fd; // [rsp+14h] [rbp-5Ch]
      ssize_t v4; // [rsp+18h] [rbp-58h]
      char buf[72]; // [rsp+20h] [rbp-50h] BYREF
      unsigned __int64 v6; // [rsp+68h] [rbp-8h]
    
      v6 = __readfsqword(0x28u);
      fd = open("/proc/self/cmdline", 0);
      if ( fd != -1 )
      {
        v4 = read(fd, buf, 0x3FuLL);
        if ( v4 > 0 )
        {
          close(fd);
          for ( i = 0; v4 > i; ++i )
          {
            if ( !buf[i] )
              buf[i] = 32;
          }
          buf[v4] = 0;
          if ( !strcmp(buf, "qilinglab") )
            *a1 = 1;
        }
      }
      return __readfsqword(0x28u) ^ v6;
    }

根据代码，我们需要让 buf 等于 "qilinglab"。 fd：open失败为-1，open成功为0。
/proc/self/cmdline是一个在Linux系统中的特殊文件，它提供了当前进程（即访问/proc/self/cmdline的进程）的命令行参数信息。

假如我们使用命令`./my_program arg1 arg2 arg3`启动一个程序时，读取/proc/self/cmdline的过程在
`./my_program` 中，/proc/self/cmdline文件的内容将是：

    
    
    ./my_program\0arg1\0arg2\0arg3\0

按照第三个挑战的方法，我们可以使用自定义文件对象来更改读取文件时的返回值：

#### writeup 10

    
    
    class Fake_cmdline(QlFsMappedObject):
        def read(self, expected_len):
            return b'qilinglab' 
    
        def close(self):
            return 0
    
    def challenge10(ql):
        ql.add_fs_mapper('/proc/self/cmdline', Fake_cmdline())

在运行后并没有解题成功，好像是在hook `/proc/self/cmdline` 这里存在问题，我写了个脚本单独调试以下cmdline读取程序：

c 程序：用来读取cmdline，文件名：test_cmdline

    
    
    #include <stdio.h>
    #include <stdlib.h>
    
    int main() {
        FILE *file;
        char ch;
    
        // 打开/proc/self/cmdline文件
        file = fopen("/proc/self/cmdline", "r");
        if (file == NULL) {
            printf("无法打开/proc/self/cmdline文件。\n");
            exit(EXIT_FAILURE);
        }
        printf("读取/proc/self/cmdline：\n");
        // 逐个字符读取文件内容并输出到终端
        while ((ch = fgetc(file)) != EOF) {
            // 将空字符替换为换行符以提高可读性
            if (ch == '\0') {
                putchar('\n');
            } else {
                putchar(ch);
            }
        }
    
        // 关闭文件
        fclose(file);
    
        return 0;
    }

python程序：用来hook test_cmdline 中的文件操作

    
    
    from qiling import *  
    from qiling.const import *   
    from qiling.os.mapper import QlFsMappedObject
    from qiling.const import QL_INTERCEPT
    from qiling.os.const import STRING
    
    import struct
    import os
    
    class Fake_cmdline(QlFsMappedObject):
        def read(self, expected_len):
            return b'qilinglab'
    
        def close(self):
            return 0
    
    def challenge10(ql):
        ql.add_fs_mapper('/proc/self/cmdline', Fake_cmdline())
    
    if __name__ == '__main__':
         path = ["test_cmdline"]
         rootfs = "rootfs/x8664_linux"
         ql = Qiling(path, rootfs)
         challenge10(ql)
         ql.run()

运行结果如下，可以看到确实在读取操作的过程中存在问题。

    
    
    读取/proc/self/cmdline：
    [=]     write(fd = 0x1, buf = 0x55555555b490, count = 0x1c) = 0x1c
    [=]     fstat(fd = 0x3, buf_ptr = 0x80000000dc50) = -0x1 (EPERM)
    [=]     read(fd = 0x3, buf = 0x55555555b8a0, length = 0x2000) = 0xd
    test_cmdline
    [=]     write(fd = 0x1, buf = 0x55555555b490, count = 0xd) = 0xd
    [=]     read(fd = 0x3, buf = 0x55555555b8a0, length = 0x2000) = 0x0
    [=]     close(fd = 0x3) = 0x0

切换到
Qilinglab当时使用的版本看一下是否存在这个问题，Qilinglab的文章是7月21发的，对应Qiling版本应该是1.2.4，使用pip指定版本安装方法：

    
    
    pip install Qiling==1.2.4

运行后存在版本不兼容问题，因此我将从这个版本开始直到最新版的每个版本都进行了测试。结果如下：

1.4.3 可以正确进行文件映射：

    
    
    Challenge 10: SOLVED
    [=]     write(fd = 0x1, buf = 0x55555575a260, count = 0x15) = 0x15

1.4.4 无法正确进行文件映射：

    
    
    Challenge 10: NOT SOLVED
    [=]     write(fd = 0x1, buf = 0x55555575a260, count = 0x19) = 0x19

我们使用的最新版是 1.4.5，也就是说在1.4.3到1.4.4这个版本更新中可能存在问题，因此接下来进行代码审计。文件映射在源码对应的
`qiling/os/mapper.py` 中，我们对比一下文件改动：

![
](https://images.seebug.org/content/images/2023/05/688e7d01-74c7-4b2b-8b73-8aeacbaac4a4.png-w331s)

改动如下：

  1. 新增 QlFsMappedCallable
  2. 由 inspect.isclass(real_dest) 扩展到 callable(real_dest)
  3. 由 real_path 更改为 host_path
  4. 新增 ql.fs_mapper.add_fs_mapping() 方法，使用 ql.add_fs_mapper() （QlFsMapper 的实例）进行调用，能够卸载映射的文件

第1点：

在之前,Qiling只支持字符串和对象做为文件系统映射。而QlFsMappedCallable允许用户传入一个类对象real_dest,然后在调用时实例化这个类对象。

用于 `add_fs_mapping(self, ql_path: Union[os.PathLike, str], real_dest:
Union[str, QlFsMappedObject, QlFsMappedCallable])` 。

第2点：

  * isclass 只检查类
  * callable 可以检查函数和类

第3点：

  * Guest 程序指的是在 Qiling 框架下被模拟执行的程序
  * real_path 是 Guest 程序运行时所使用的路径
  * host_path 是可以被 Guest 程序打开的 Host 系统中的一个路径

第4点：

  * 属于新增能够卸载映射的文件的功能

我们替换1.4.4的mapper.py为1.4.3版本，

    
    
    vim /home/ubuntu/anaconda3/envs/ql1-4-4/lib/python3.9/site-packages/qiling/os/mapper.py

更改后依然没变化，报错。接着分析是否是针对 `/proc/self/cmdline` 有新的处理方式，加载1.4.4的源码到vscode中，发现在
`linux.py` 文件中新增以下代码：

![
](https://images.seebug.org/content/images/2023/05/3f9f80a6-1e31-43c2-b652-4e0d6f2a1aa3.png-w331s)

看一下更新对比：

![
](https://images.seebug.org/content/images/2023/05/b8998de1-6343-4957-a987-249581bc071e.png-w331s)

1.4.4版本的linux.py文件与1.4.3版本的linux.py文件相比,有以下主要改动:

  1. 添加了setup_procfs()方法,用于设置/proc伪文件系统。这使得Qiling可以模拟/proc目录和相关文件,提供更真实的linux环境。
  2. /proc/self目录下的几个文件(auxv、cmdline、environ、exe、maps)被映射到QlProcFS类的静态方法上,这使得Qiling可以模拟读取这几个文件。
  3. run()方法中,除非是处理驱动程序或shellcode,否则都会调用setup_procfs()设置/proc文件系统。这确保除特殊情况外,Qiling都会模拟/proc文件系统。
  4. 添加了fs_mapper属性,用于管理文件系统映射。setup_procfs()就是通过fs_mapper添加/proc文件系统映射的。

之前在1.4.3版本中模拟/proc目录的方式有两个:

  1. 直接读取/proc文件内容
  2. 通过QlFsMappedCallable映射/proc文件,返回自定义内容

这两种方式存在一定缺点:

  1. 无法方便地重用/proc内容,需要多次读取
  2. 映射时需要定义QlFsMappedCallable类,很麻烦，处理方式不统一

所以总的来说1.4.4版本对/proc处理做了封装，使得它更模块化、易用。但是在新增的几个模块中对 '/proc/self/auxv'
等文件做出了额外的限制，我们在映射这几个文件时可能存在问题。因此我怀疑 cmdline 的问题就是在这个地方。

接着看run(self)函数：

    
    
        def run(self):
            # do not set-up procfs for drivers and shellcode
            if not self.ql.code and not self.ql.loader.is_driver:
                self.setup_procfs()

这段代码的含义是:

只有在加载ELF文件或可执行程序的时候,才设置/proc文件系统。

  1. 对于直接加载Shellcode(`self.ql.code`)的情况,不设置/proc文件系统
  2. 对于加载驱动程序 (`self.ql.loader.is_driver`) 的情况,也不设置/proc文件系统

    
    
    vim /home/ubuntu/anaconda3/envs/ql1-4-4/lib/python3.9/site-packages/qiling/os/linux/linux.py

因此将此处判断代码注释后，就应该可以成功运行了。注释后运行：

    
    
    Challenge 8: SOLVED
    [=]     write(fd = 0x1, buf = 0x55555575a260, count = 0x14) = 0x14
    [=]     openat(fd = 0xffffff9c, path = 0x5555555556c1, flags = 0x0, mode = 0x0) = 0x3
    [=]     read(fd = 0x3, buf = 0x80000000dcc0, length = 0x3f) = 0x9
    [=]     close(fd = 0x3) = 0x0
    Challenge 9: SOLVED
    [=]     write(fd = 0x1, buf = 0x55555575a260, count = 0x14) = 0x14
    Challenge 10: SOLVED
    [=]     write(fd = 0x1, buf = 0x55555575a260, count = 0x15) = 0x15

运行成功！

这个问题应该在1.4.4和1.4.5中都存在，我们可以通过新增一个选项 `ql = Qiling(path, rootfs,
enable_procfs=False)` 来控制是否设置/proc文件系统，当`enable_procfs=False`
时关闭，默认值为True。我们需要修改 `core.py` 文件：

    
    
    vim /home/ubuntu/anaconda3/envs/ql1-4-4/lib/python3.9/site-packages/qiling/core.py
    
    
    def __init__(
        self,
        argv: Sequence[str] = None,
        rootfs: str = r'.',
        env: MutableMapping[AnyStr, AnyStr] = {},
        code: bytes = None,
        ostype: Union[str, QL_OS] = None,
        archtype: Union[str, QL_ARCH] = None,
        verbose: QL_VERBOSE = QL_VERBOSE.DEFAULT,
        profile: str = None,
        console: bool = True,
        log_file=None,
        log_override=None,
        log_plain: bool = False,
        multithread: bool = False,
        filter=None,
        stop: QL_STOP = QL_STOP.NONE,
        *,
        endian: Optional[QL_ENDIAN] = None,
        thumb: bool = False,
        libcache: bool = False,
        enable_procfs: bool = True         # <---------------------------- 新添加的参数，默认值为True
    ):
        self.enable_procfs = enable_procfs # <---------------------------- 设置 enable_procfs 属性
    ······

修改 `linux.py` 中的代码新增对参数enable_procfs的判断：

    
    
        def run(self):
            # if not self.ql.code and not self.ql.loader.is_driver:   # 原来的代码
            if self.ql.enable_procfs and not self.ql.code and not self.ql.loader.is_driver:
                self.setup_procfs()

这样我们只需要将ql改成下面的代码即可：

    
    
    ql = Qiling(path, rootfs, enable_procfs=False)

然后修改我们的challenge10测试一下，运行成功！

    
    
    Challenge 8: SOLVED
    [=]     write(fd = 0x1, buf = 0x55555575a260, count = 0x14) = 0x14
    [=]     openat(fd = 0xffffff9c, path = 0x5555555556c1, flags = 0x0, mode = 0x0) = 0x3
    [=]     read(fd = 0x3, buf = 0x80000000dcc0, length = 0x3f) = 0x9
    [=]     close(fd = 0x3) = 0x0
    Challenge 9: SOLVED
    [=]     write(fd = 0x1, buf = 0x55555575a260, count = 0x14) = 0x14
    Challenge 10: SOLVED
    [=]     write(fd = 0x1, buf = 0x55555575a260, count = 0x15) = 0x15

### Challenge 11：绕过CPUID校验

> Challenge 11: Bypass CPUID/MIDR_EL1 checks.

伪代码如下：

    
    
    unsigned __int64 __fastcall challenge11(_BYTE *a1)
    {
      int v7; // [rsp+1Ch] [rbp-34h]
      int v8; // [rsp+24h] [rbp-2Ch]
      char s[4]; // [rsp+2Bh] [rbp-25h] BYREF
      char v10[4]; // [rsp+2Fh] [rbp-21h] BYREF
      char v11[4]; // [rsp+33h] [rbp-1Dh] BYREF
      unsigned __int64 v12; // [rsp+38h] [rbp-18h]
    
      v12 = __readfsqword(0x28u);
      _RAX = 0x40000000LL;
      __asm { cpuid }
      v7 = _RCX;
      v8 = _RDX;
      if ( __PAIR64__(_RBX, _RCX) == 0x696C6951614C676ELL && (_DWORD)_RDX == 538976354 )
        *a1 = 1;
      sprintf(
        s,
        "%c%c%c%c",
        (unsigned int)_RBX,
        (unsigned int)((int)_RBX >> 8),
        (unsigned int)((int)_RBX >> 16),
        (unsigned int)((int)_RBX >> 24));
      sprintf(
        v10,
        "%c%c%c%c",
        (unsigned int)v7,
        (unsigned int)(v7 >> 8),
        (unsigned int)(v7 >> 16),
        (unsigned int)(v7 >> 24));
      sprintf(
        v11,
        "%c%c%c%c",
        (unsigned int)v8,
        (unsigned int)(v8 >> 8),
        (unsigned int)(v8 >> 16),
        (unsigned int)(v8 >> 24));
      return __readfsqword(0x28u) ^ v12;
    }

关键部分汇编代码如下：

    
    
    .text:000055555555518F                 cpuid
    .text:0000555555555191                 mov     eax, edx
    .text:0000555555555193                 mov     esi, ebx
    .text:0000555555555195                 mov     [rbp+var_30], esi
    .text:0000555555555198                 mov     [rbp+var_34], ecx
    .text:000055555555519B                 mov     [rbp+var_2C], eax
    .text:000055555555519E                 cmp     [rbp+var_30], 696C6951h
    .text:00005555555551A5                 jnz     short loc_5555555551C0
    .text:00005555555551A7                 cmp     [rbp+var_34], 614C676Eh
    .text:00005555555551AE                 jnz     short loc_5555555551C0
    .text:00005555555551B0                 cmp     [rbp+var_2C], 20202062h
    .text:00005555555551B7                 jnz     short loc_5555555551C0
    .text:00005555555551B9                 mov     rax, [rbp+var_48]
    .text:00005555555551BD                 mov     byte ptr [rax], 1

我们需要让`*a=1`，就要让if的判断顺利通过，`if ( __PAIR64__(_RBX, _RCX) == 0x696C6951614C676ELL
&& (_DWORD)_RDX == 538976354 )` 的含义为：

  1. rbx和rcx两个32位寄存器组成的64位值等于0x696C6951614C676ELL
  2. RDX寄存器的低32位等于538976354

因此我们跳过cpuid指令修改寄存器即可。

#### writeup 11

    
    
    def hook_cpuid(ql, address, size):
    
        if ql.mem.read(address, size) == b'\x0F\xA2': # CPUID指令的机器码是 0F A2
            regs = ql.arch.regs
            regs.ebx = 0x696C6951
            regs.ecx = 0x614C676E
            regs.edx = 0x20202062
            regs.rip += 2 # 跳过cpuid指令防止被cpuid篡改 000055555555518F -> 0000555555555191
    
    def challenge11(ql):
        begin, end = 0, 0
        for info in ql.mem.map_info:
            print(info)
            if info[2] == 5 and 'qilinglab-x86_64' in info[3]:
                begin, end = info[:2]
                print(f"{begin} -> {end}")
    
        ql.hook_code(hook_cpuid, begin=begin, end=end)

最后可以看到全部题目均已解决：

    
    
    You solved 11/11 of the challenges
    [=]     write(fd = 0x1, buf = 0x55555575a260, count = 0x23) = 0x23
    [=]     exit_group(code = 0x0) = ?

最后完整代码为：

    
    
    from qiling import *  
    from qiling.const import *   
    from qiling.os.mapper import QlFsMappedObject
    from qiling.const import QL_INTERCEPT
    from qiling.os.const import STRING
    from qiling.os.mapper import QlFsMappedCallable
    
    import struct
    import os
    
    def challenge1(ql):
         ql.mem.map(0x1000, 0x1000, info='[challenge1]')  
         ql.mem.write(0x1337, ql.pack16(1337))   
    
    def my_uname_on_exit_hook(ql, *args):
         rdi = ql.arch.regs.rdi  
         print(f"utsname address: {hex(rdi)}")
         ql.mem.write(rdi, b'QilingOS\x00')  
         ql.mem.write(rdi + 65 * 3, b'ChallengeStart\x00')
    
    def challenge2(ql):  
         ql.os.set_syscall("uname", my_uname_on_exit_hook, QL_INTERCEPT.EXIT)
    
    class FakeUrandom(QlFsMappedObject):
    
        def read(self, size: int) -> bytes:  
            if size == 1:
                print("*************3**************")
                return b"\x42" 
            else:
                return b"\x41" * size
    
        def close(self) -> int:
            return 0
    
    def hook_getrandom(ql, buf, buflen, flags):
        # 自定义 getrandom 函数实现
        if buflen == 32:
            data = b'\x41' * buflen  # b'\x41' = A
            ql.mem.write(buf, data)
            ql.os.set_syscall_return(buflen)
        else:
            ql.os.set_syscall_return(-1)
    
    def challenge3(ql):
         ql.add_fs_mapper(r'/dev/urandom', FakeUrandom())  
         ql.os.set_syscall("getrandom", hook_getrandom)
    
    def enter_forbidden_loop_hook(ql):
         ql.arch.regs.eax = 1
    
    def challenge4(ql):
        """
        .text:0000555555554E40                 mov     eax, [rbp+var_8]
        .text:0000555555554E43                 cmp     [rbp+var_4], eax <-- 在运行此命令前hook eax，使得eax = 1
        .text:0000555555554E46                 jl      short loc_555555554E35
        """
        base = ql.mem.get_lib_base(os.path.split(ql.path)[-1])  # 根据文件路径查找已经加载的文件，获取对应文件的基地址
        hook_addr = base + 0xE43
        ql.hook_address(enter_forbidden_loop_hook, hook_addr) # 当执行流程到达hook_addr时，该函数将被调用。此时hook_addr处的代码还未被执行。
    
    def hook_rand(ql):
        ql.arch.regs.rax = 0
    
    def challenge5(ql):
        ql.os.set_api('rand', hook_rand)
    
    def hook_rax(ql):
        ql.arch.regs.rax = 0
    def challenge6(ql):
        base = ql.mem.get_lib_base(os.path.split(ql.path)[-1])
        hook_addr = base + 0xF16
        ql.hook_address(hook_rax, hook_addr)
    
    def hook_sleep(ql):
        return 0
    def challenge7(ql):
        ql.os.set_api('sleep', hook_sleep)
    
    def challenge8_hook(ql):
    
        # Find all occurrences of the magic in memory
        MAGIC = 0x3DFCD6EA00000539
        magic_addrs = ql.mem.search(ql.pack64(MAGIC)) 
    
        for magic_addr in magic_addrs:
    
            # Dump and unpack the candidate structure
            candidate_heap_struct_addr = magic_addr - 8
            candidate_heap_struct = ql.mem.read(candidate_heap_struct_addr, 24)
    
            string_addr, _ , check_addr = struct.unpack('QQQ', candidate_heap_struct) 
            # struct.unpack() 是一个 Python 函数，用于将字节序列解包为多个值，解包 candidate_heap_struct 变量中的数据。
            # 'QQQ' 是一个格式字符串，表示要解包的数据结构包含3个64位（8 字节）无符号整数。
            # string_addr, _ , check_addr：只关注 string_addr 与 check_addr
    
            if ql.mem.string(string_addr) == "Random data":
                # 修改*a1为1
                ql.mem.write(check_addr, b"\x01")
                break
    
    def challenge8(ql):
        base_addr = ql.mem.get_lib_base(os.path.split(ql.path)[-1])
        end_of_challenge8 = base_addr + 0xFB5     # 程序运行结束时的地址
    
        ql.hook_address(challenge8_hook, end_of_challenge8)
    
    def hook_tolower(ql):
        return 0
    
    def challenge9(ql):
        ql.os.set_api('tolower', hook_tolower)
    
    class Fake_cmdline(QlFsMappedObject):
        def read(self, expected_len):
            return b'qilinglab'
    
        def close(self):
            return 0
    
    def challenge10(ql):
        # ql.add_fs_mapper('/proc/self/cmdline', Fake_cmdline())
        ql.add_fs_mapper('/proc/self/cmdline', QlFsMappedCallable(Fake_cmdline))
    
    def hook_cpuid(ql, address, size):
        if ql.mem.read(address, size) == b'\x0F\xA2':
            regs = ql.arch.regs
            regs.ebx = 0x696C6951
            regs.ecx = 0x614C676E
            regs.edx = 0x20202062
            regs.rip += 2
    
    def challenge11(ql):
        begin, end = 0, 0
        for info in ql.mem.map_info:
            print(info)
            if info[2] == 5 and 'qilinglab-x86_64' in info[3]:
                begin, end = info[:2]
                print(f"{begin} -> {end}")
    
        ql.hook_code(hook_cpuid, begin=begin, end=end)
    
    if __name__ == '__main__':  
         path = ["rootfs/x8664_linux/qilinglab-x86_64"]  
         rootfs = "rootfs/x8664_linux"  
         ql = Qiling(path, rootfs, enable_procfs=False)
         challenge1(ql)  
         challenge2(ql) 
         challenge3(ql)
         challenge4(ql)
         challenge5(ql)
         challenge6(ql)
         challenge7(ql)
         challenge8(ql)
         challenge9(ql)
         challenge10(ql)
         challenge11(ql)
         ql.run()

### 总结

跟着上面的文章思路走一遍，我相信大家已经了解了 Qiling 框架的使用方法。通过分析 Qiling 的源码，也加强了我对 Qiling框架的理解。

如果在本文中发现问题，欢迎大家在下面留言。

### 参考文章

[Qiling 官方文档](https://docs.qiling.io/en/latest/)  
[Qiling lab](https://joansivion.github.io/qilinglabs/#setup)  
[Qiling
Framework入门，11个挑战快速上手@PJXRocks](https://zhuanlan.zhihu.com/p/405559684)  
[浅尝qiling框架-qilinglab
writeup@badmonkey](https://badmonkey.site/archives/qilinglab-writeup)  
[11个小挑战，Qiling Framework
入门上手跟练@Cr0ssx2](https://bbs.kanxue.com/thread-268989-1.htm)

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/2073/>

