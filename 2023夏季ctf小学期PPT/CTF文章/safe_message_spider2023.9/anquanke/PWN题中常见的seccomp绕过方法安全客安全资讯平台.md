# PWN题中常见的seccomp绕过方法

阅读量 **359147**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-10-27 16:30:33

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t0186dda3f9f7aa7f42.png)

工欲善其事，必先利其器

先了解些前置知识

## 前置知识

在wiki上面 seccomp的说明如下，简而言之就是一个保护系统安全的一种机制，可以通过控制syscall，禁止掉一些危险的syscall

    
    
    seccomp (short for secure computing mode) is a computer security facility in the Linux kernel. seccomp allows a process to make a one-way transition into a "secure" state where it cannot make any system calls except exit(), sigreturn(), read() and write() to already-open file descriptors. Should it attempt any other system calls, the kernel will terminate the process with SIGKILL or SIGSYS.[1][2] In this sense, it does not virtualize the system's resources but isolates the process from them entirely.
    

一般使用seccomp有两种方法，一种是用prctl，另一种是用seccomp

先说下第一种,他可以通过第一个参数控制一个进程去做什么，他可以做很多东西，其中一个就是 PR_SET_SECCOMP，这个就是控制程序去开启 seccomp
mode，还有一个就是PR_SET_NO_NEW_PRIVS，这个可以让程序无法获得特权

    
    
    prctl - operations on a process
    prctl() is called with a first argument describing what to do (with values defined in <linux/prctl.h>), and further arguments with a significance depending on the first one
    

关于 PR_SET_NO_NEW_PRIVS 可以这样用,第二个参数为1就可

    
    
    prctl(PR_SET_NO_NEW_PRIVS,1,0,0,0);
    

PR_SET_SECCOMP 可以这样

先定义好BPF 比如下面这样定义

    
    
        struct sock_filter st[]=
    {
        {0x20 ,0x00, 0x00, 0x00000004},
        {0x15 ,0x00, 0x04, 0xc000003e},
        {0x20 ,0x00, 0x00, 0x00000000},
        {0x35 ,0x02, 0x00, 0x40000000},
        {0x15 ,0x01, 0x00, 0x0000003b},
        {0x06 ,0x00, 0x00, 0x7fff0000},
        {0x06 ,0x00, 0x00, 0x00000000}
    };
    

然后通过再给sock_fprog结构体，然后传给 prctl做参数

    
    
    struct sock_fprog sfg ={7,st};
    prctl(PR_SET_SECCOMP,SECCOMP_MODE_FILTER,&sfg);
    

上面这个 sock_filter 结构体可以通过[seccomp-tools](https://github.com/david942j/seccomp-tools) dump出来，或者 seccomp_export_bpf导出

然后再说说 通过seccomp的函数来 开启 seccomp,先给出一个例子

    
    
    {    scmp_filter_ctx ctx;
        ctx = seccomp_init(SCMP_ACT_ALLOW);
        seccomp_rule_add(ctx, SCMP_ACT_KILL, SCMP_SYS(execve), 0);
        seccomp_load(ctx);    
    }
    seccomp_init \\
    scmp_filter_ctx seccomp_init(uint32_t def_action);
    initialize the internal seccomp filter state, prepares it for use, and sets the default action based on the def_action parameter
    

可以看道 seccomp_init 返回的是一个 scmp_filter_ctx 的结构体

而有效的 def_action 有下面几种

    
    
    SCMP_ACT_KILL
    SCMP_ACT_KILL_PROCESS
    SCMP_ACT_TRAP
    SCMP_ACT_ERRNO
    SCMP_ACT_TRACE
    SCMP_ACT_LOG
    SCMP_ACT_ALLOW
    

我们关注的应该是 SCMP_ACT_KILL 和 SCMP_ACT_ALLOW，一个是白名单，一个是黑名单

seccomp_rule_add 可以添加规则

    
    
    int seccomp_rule_add(scmp_filter_ctx ctx, uint32_t action,
                                int syscall, unsigned int arg_cnt, ...);
    

arg_cnt 这个指令是指后面参数的个数，比如

    
    
    rc = seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(read), 3,
                          SCMP_A0(SCMP_CMP_EQ, fd),
                          SCMP_A1(SCMP_CMP_EQ, (scmp_datum_t)buf),
                          SCMP_A2(SCMP_CMP_LE, BUF_SIZE));
    rc = seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(write), 1,
                          SCMP_CMP(0, SCMP_CMP_EQ, fd));
    rc = seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(exit_group), 0);
    

分别是 3 ，1，0 个。然后后面的参数就是 comparison op,主要有下面几种

    
    
    SCMP_CMP_NE
    Matches when the argument value is not equal to the datum value, example:
    
    SCMP_CMP( arg , SCMP_CMP_NE , datum )
    
    SCMP_CMP_LT
    Matches when the argument value is less than the datum value, example:
    
    SCMP_CMP( arg , SCMP_CMP_LT , datum )
    
    SCMP_CMP_LE
    Matches when the argument value is less than or equal to the datum value, example:
    
    SCMP_CMP( arg , SCMP_CMP_LE , datum )
    
    SCMP_CMP_EQ
    Matches when the argument value is equal to the datum value, example:
    
    SCMP_CMP( arg , SCMP_CMP_EQ , datum )
    
    SCMP_CMP_GE
    Matches when the argument value is greater than or equal to the datum value, example:
    
    SCMP_CMP( arg , SCMP_CMP_GE , datum )
    
    SCMP_CMP_GT
    Matches when the argument value is greater than the datum value, example:
    
    SCMP_CMP( arg , SCMP_CMP_GT , datum )
    
    SCMP_CMP_MASKED_EQ
    Matches when the masked argument value is equal to the masked datum value, example:
    
    SCMP_CMP( arg , SCMP_CMP_MASKED_EQ , mask , datum )
    

seccomp_load 其实就是应用 filter

下面是安装指令

    
    
    sudo apt install libseccomp-dev libseccomp2 seccomp
    

## CTF中常见的seccomp

第一种，也是最常见的,禁用了execve或者system

    
    
     0000: 0x20 0x00 0x00 0x00000004  A = arch
     0001: 0x15 0x00 0x04 0xc000003e  if (A != ARCH_X86_64) goto 0006
     0002: 0x20 0x00 0x00 0x00000000  A = sys_number
     0003: 0x35 0x02 0x00 0x40000000  if (A >= 0x40000000) goto 0006
     0004: 0x15 0x01 0x00 0x0000003b  if (A == execve) goto 0006
     0005: 0x06 0x00 0x00 0x7fff0000  return ALLOW
     0006: 0x06 0x00 0x00 0x00000000  return KILL
    

这种可以通过 open read write 来读取flag

可以看 高校战役的 lgd

第二种是禁用了 open，write，read

    
    
     0000: 0x20 0x00 0x00 0x00000004  A = arch
     0001: 0x15 0x00 0x09 0xc000003e  if (A != ARCH_X86_64) goto 0011
     0002: 0x20 0x00 0x00 0x00000000  A = sys_number
     0003: 0x35 0x00 0x01 0x40000000  if (A < 0x40000000) goto 0005
     0004: 0x15 0x00 0x06 0xffffffff  if (A != 0xffffffff) goto 0011
     0005: 0x15 0x05 0x00 0x00000000  if (A == read) goto 0011
     0006: 0x15 0x04 0x00 0x00000001  if (A == write) goto 0011
     0007: 0x15 0x03 0x00 0x00000002  if (A == open) goto 0011
     0008: 0x15 0x02 0x00 0x00000003  if (A == close) goto 0011
     0009: 0x15 0x01 0x00 0x0000003b  if (A == execve) goto 0011
     0010: 0x06 0x00 0x00 0x7fff0000  return ALLOW
     0011: 0x06 0x00 0x00 0x00000000  return KILL
    

open系统调用实际上是调用了openat，所以直接 调用openat，然后除了 read，write，其实还有两个

readv，和writev，这些就能绕过限制读取flag,有些连openat都禁用的可以 ptrace 修改syscall

这个能看 `zer0pts CTF2020的sycall kit`

第三种是 控制了 open，write，read的参数

比如最近的天翼杯里面的一道题

    
    
     0000: 0x20 0x00 0x00 0x00000004  A = arch
     0001: 0x15 0x00 0x0b 0xc000003e  if (A != ARCH_X86_64) goto 0013
     0002: 0x20 0x00 0x00 0x00000000  A = sys_number
     0003: 0x35 0x00 0x01 0x40000000  if (A < 0x40000000) goto 0005
     0004: 0x15 0x00 0x08 0xffffffff  if (A != 0xffffffff) goto 0013
     0005: 0x15 0x06 0x00 0x00000002  if (A == open) goto 0012
     0006: 0x15 0x00 0x06 0x00000000  if (A != read) goto 0013
     0007: 0x20 0x00 0x00 0x00000014  A = fd >> 32 # read(fd, buf, count)
     0008: 0x25 0x03 0x00 0x00000000  if (A > 0x0) goto 0012
     0009: 0x15 0x00 0x03 0x00000000  if (A != 0x0) goto 0013
     0010: 0x20 0x00 0x00 0x00000010  A = fd # read(fd, buf, count)
     0011: 0x35 0x00 0x01 0x00000004  if (A < 0x4) goto 0013
     0012: 0x06 0x00 0x00 0x7fff0000  return ALLOW
     0013: 0x06 0x00 0x00 0x00000000  return KILL
    

还有 HACK 2020里面的一道

    
    
    line  CODE  JT   JF      K
    =================================
     0000: 0x20 0x00 0x00 0x00000004  A = arch
     0001: 0x15 0x00 0x12 0xc000003e  if (A != ARCH_X86_64) goto 0020
     0002: 0x20 0x00 0x00 0x00000000  A = sys_number
     0003: 0x35 0x00 0x01 0x40000000  if (A < 0x40000000) goto 0005
     0004: 0x15 0x00 0x0f 0xffffffff  if (A != 0xffffffff) goto 0020
     0005: 0x15 0x0d 0x00 0x00000002  if (A == open) goto 0019
     0006: 0x15 0x0c 0x00 0x00000003  if (A == close) goto 0019
     0007: 0x15 0x0b 0x00 0x0000000a  if (A == mprotect) goto 0019
     0008: 0x15 0x0a 0x00 0x000000e7  if (A == exit_group) goto 0019
     0009: 0x15 0x00 0x04 0x00000000  if (A != read) goto 0014
     0010: 0x20 0x00 0x00 0x00000014  A = fd >> 32 # read(fd, buf, count)
     0011: 0x15 0x00 0x08 0x00000000  if (A != 0x0) goto 0020
     0012: 0x20 0x00 0x00 0x00000010  A = fd # read(fd, buf, count)
     0013: 0x15 0x05 0x06 0x00000000  if (A == 0x0) goto 0019 else goto 0020
     0014: 0x15 0x00 0x05 0x00000001  if (A != write) goto 0020
     0015: 0x20 0x00 0x00 0x00000014  A = fd >> 32 # write(fd, buf, count)
     0016: 0x15 0x00 0x03 0x00000000  if (A != 0x0) goto 0020
     0017: 0x20 0x00 0x00 0x00000010  A = fd # write(fd, buf, count)
     0018: 0x15 0x00 0x01 0x00000001  if (A != 0x1) goto 0020
     0019: 0x06 0x00 0x00 0x7fff0000  return ALLOW
     0020: 0x06 0x00 0x00 0x00000000  return KILL
    

这种限制 参数的 可以冲参数上有什么问题，去考虑，比如第二道

限制只能冲 0 读，那可以把 0 close 再open 就可以

然后第一道，也是fd 限制为0，但是

    
    
     0007: 0x20 0x00 0x00 0x00000014  A = fd >> 32 # read(fd, buf, count)
     0008: 0x25 0x03 0x00 0x00000000  if (A > 0x0) goto 0012
    

fd为4个字节就能绕过

第四种是限制了sys_number,看起来完全无法利用一样，但是可以用32位的绕过或者用0x400000+sys_number，这样好像是调用了32位的ABI

    
    
     0000: 0x20 0x00 0x00 0x00000004  A = arch
     0001: 0x15 0x00 0x07 0xc000003e  if (A != ARCH_X86_64) goto 0009
     0002: 0x20 0x00 0x00 0x00000000  A = sys_number
     0003: 0x15 0x05 0x00 0x00000002  if (A == open) goto 0009
     0004: 0x15 0x04 0x00 0x00000009  if (A == mmap) goto 0009
     0005: 0x15 0x03 0x00 0x00000065  if (A == ptrace) goto 0009
     0006: 0x15 0x02 0x00 0x00000101  if (A == openat) goto 0009
     0007: 0x15 0x01 0x00 0x00000130  if (A == open_by_handle_at) goto 0009
     0008: 0x06 0x00 0x00 0x7fff0000  return ALLOW
     0009: 0x06 0x00 0x00 0x00000000  return KILL
    

这种就是 没判断

    
    
    if (A < 0x40000000)
    

导致了可以 0x40000000+sys_number绕过，sys_number |= 0x40000000

    
    
     0000: 0x20 0x00 0x00 0x00000000  A = sys_number
     0001: 0x15 0x04 0x00 0x00000001  if (A == write) goto 0006
     0002: 0x15 0x03 0x00 0x00000000  if (A == read) goto 0006
     0003: 0x15 0x02 0x00 0x00000009  if (A == mmap) goto 0006
     0004: 0x15 0x01 0x00 0x00000005  if (A == fstat) goto 0006
     0005: 0x06 0x00 0x00 0x00050005  return ERRNO(5)
     0006: 0x06 0x00 0x00 0x7fff0000  return ALLOW
     0007: 0x06 0x00 0x00 0x00000000  return KILL
    

如果没有 if (A != ARCH_X86_64) 这个可以同32位的shellcode绕过过，具体的可以参考下
SCTF2020里面的`CoolCode` ,利用 `retfq` 切换到32模式，来执行指令

可以 看 [1](http://p4nda.top/2018/07/27/CISCN-Final/)

参考链接

[一道 CTF 题目学习 prctl 函数的沙箱过滤规则](https://www.anquanke.com/post/id/186447#h2-7)

[seccomp学习笔记](//veritas501.space/2018/05/05/seccomp%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0/))

[seccomp_sys](https://docs.rs/seccomp-sys/0.1.0/seccomp_sys/fn.seccomp_rule_add.html)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **s0xzordIn** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/219077](/post/id/219077)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Pwn](/tag/Pwn)
  * [CTF](/tag/CTF)

 **+1** __6赞

 __收藏

![](https://p2.ssl.qhimg.com/t01a2756d72879362ad.png) s0xzordIn

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

